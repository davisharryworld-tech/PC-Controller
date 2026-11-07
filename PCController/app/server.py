import io
import json
import os
import platform
import shutil
import socket
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse
import pyautogui
import pyperclip
import psutil

from app.actions import execute_universal_action
from app.ai_parser import interpret_and_execute_nl
from app.config import settings
from app.dashboard import get_dashboard_html, get_device_locked_html
from app.logger import logger
from app.schemas import HealthStatus, SystemInfoResponse, WSMessageIn, WSMessageOut
from app.ws_manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Local LAN/Wi-Fi IP Address: {settings.LOCAL_IP}")
    ts_ip = settings.TAILSCALE_IP
    if ts_ip:
        logger.info(f"Tailscale Remote IP:        {ts_ip}")
    else:
        logger.info("Tailscale Remote IP:        Not active (run 'tailscale login' to connect)")
    logger.info(f"Listening on:               http://{settings.HOST}:{settings.PORT}")
    logger.info(f"Local Dashboard:            http://{settings.LOCAL_IP}:{settings.PORT}/")
    if ts_ip:
        logger.info(f"Remote Tailscale Dashboard: http://{ts_ip}:{settings.PORT}/")
    logger.info(f"Health check endpoint:      http://{settings.LOCAL_IP}:{settings.PORT}/health")
    logger.info(f"WebSocket endpoint:         ws://{settings.LOCAL_IP}:{settings.PORT}/ws/controller")
    logger.info("=" * 60)

    # Send mobile push notification on PC boot/startup
    def send_boot_notification():
        import urllib.request
        import time
        time.sleep(2.0)
        endpoint = "https://notify.run/Xr8sUVetppo2cKoSrqTN"
        ts_part = f"Tailscale: http://{ts_ip}:8000/" if ts_ip else ""
        msg = f"🎮 PC Controller Online! Aapka server connect ho gaya hai.\nWi-Fi: http://{settings.LOCAL_IP}:8000/\n{ts_part}"
        try:
            req = urllib.request.Request(
                endpoint,
                data=msg.encode("utf-8"),
                headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"}
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                if r.status == 200:
                    logger.info("Startup push notification sent to mobile via notify.run! 🔔")
        except Exception as e:
            logger.warning(f"Could not send startup push notification: {e}")

    import threading
    threading.Thread(target=send_boot_notification, daemon=True).start()

    yield
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Local Wi-Fi & Tailscale Remote PC Agent for Android-to-PC controller.",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def device_access_guard(request: Request, call_next):
    client_ip = request.client.host if request.client else ""

    # 1. Local PC access is always allowed
    if client_ip in ("127.0.0.1", "::1", "localhost"):
        return await call_next(request)

    # 2. Hardware Tailscale IP: ONLY user's Honor X6c is allowed
    if client_ip.startswith("100."):
        if client_ip in settings.AUTHORIZED_TAILSCALE_IPS:
            return await call_next(request)
        else:
            logger.warning(f"⛔ Blocked unauthorized Tailscale device: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "detail": "Access Denied: Tailscale device is not authorized."}
            )

    # 3. Wi-Fi / LAN Access: Check Device Key in headers, query param, or cookies
    token = (
        request.headers.get("X-Device-Token")
        or request.query_params.get("token")
        or request.cookies.get("device_token")
    )
    if token == settings.AUTHORIZED_DEVICE_TOKEN:
        return await call_next(request)

    # If opening root URL in browser without token, show Device Lock screen
    if request.url.path == "/" and request.method == "GET":
        logger.info(f"Serving device lock pairing screen to unrecognized client: {client_ip}")
        return HTMLResponse(
            status_code=403,
            content=get_device_locked_html(client_ip)
        )

    logger.warning(f"⛔ Blocked unauthorized device on Wi-Fi: {client_ip} trying to access {request.url.path}")
    return JSONResponse(
        status_code=403,
        content={"error": "Forbidden", "detail": "Access Denied: Only authorized Honor X6c device is allowed."}
    )


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """
    Serves the interactive mobile & desktop web remote control dashboard.
    """
    return HTMLResponse(
        content=get_dashboard_html(
            local_ip=settings.LOCAL_IP,
            tailscale_ip=settings.TAILSCALE_IP,
            port=settings.PORT,
            project_name=settings.PROJECT_NAME,
            authorized_token=settings.AUTHORIZED_DEVICE_TOKEN,
        )
    )


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """
    Health check endpoint returning JSON status of the server.
    """
    return HealthStatus(
        status="online",
        server_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        local_ip=settings.LOCAL_IP,
        tailscale_ip=settings.TAILSCALE_IP,
        port=settings.PORT,
        connected_clients=ws_manager.connection_count,
    )


@app.get("/api/system", response_model=SystemInfoResponse)
async def system_info():
    """
    Returns non-sensitive PC system status and network info for local clients.
    """
    return SystemInfoResponse(
        os=f"{platform.system()} {platform.release()}",
        cpu_model=platform.processor() or "Detected x86_64",
        total_ram_gb=8.0,
        local_ip=settings.LOCAL_IP,
        tailscale_ip=settings.TAILSCALE_IP,
        port=settings.PORT,
        ollama_available=True,
        status="ready",
    )


@app.get("/api/running_apps")
async def running_apps():
    """
    Returns active user applications currently running on the PC.
    """
    from app.actions import get_running_user_apps
    return {"apps": get_running_user_apps()}


@app.get("/api/contacts")
async def get_contacts():
    """
    Returns saved WhatsApp contacts mapping names to phone numbers.
    """
    from app.contacts_manager import load_contacts
    return {"contacts": load_contacts()}


@app.post("/api/contacts")
async def add_or_update_contact(data: dict):
    """
    Saves or updates a WhatsApp contact.
    """
    from app.contacts_manager import set_contact
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    if not name or not phone:
        return {"success": False, "message": "Name and phone are required."}
    set_contact(name, phone)
    return {"success": True, "message": f"Saved {name} -> {phone}"}


@app.delete("/api/contacts/{name}")
async def remove_contact(name: str):
    """
    Deletes a contact from the address book.
    """
    from app.contacts_manager import delete_contact
    delete_contact(name)
    return {"success": True, "message": f"Deleted contact {name}"}


RECEIVED_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "PC_Controller_Received")
os.makedirs(RECEIVED_DIR, exist_ok=True)


def capture_pc_frame(scale: float = 0.55, quality: int = 65, show_cursor: bool = True) -> bytes:
    """Fast screen capture using ImageGrab with attached desktop and visible mouse cursor."""
    from PIL import ImageGrab, ImageDraw
    from app.actions import ensure_desktop_attached
    ensure_desktop_attached()
    img = ImageGrab.grab()
    w, h = img.size
    target_w, target_h = int(w * scale), int(h * scale)
    img_small = img.resize((target_w, target_h))
    if show_cursor:
        try:
            mx, my = pyautogui.position()
            cx, cy = int(mx * scale), int(my * scale)
            draw = ImageDraw.Draw(img_small)
            # Draw highly visible cursor dot
            draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill="#ef4444", outline="#ffffff", width=2)
        except Exception:
            pass
    buf = io.BytesIO()
    img_small.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


@app.get("/api/screen/screenshot")
async def get_screenshot(raw: bool = False):
    """Captures and returns the current PC screen as an optimized JPEG image."""
    try:
        scale = 1.0 if raw else 0.65
        quality = 85 if raw else 65
        frame = capture_pc_frame(scale=scale, quality=quality, show_cursor=True)
        return StreamingResponse(io.BytesIO(frame), media_type="image/jpeg")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/screen/stream")
async def get_screen_stream():
    """Streams live PC screen as a smooth MJPEG video stream with visible mouse cursor."""
    import asyncio

    async def frame_generator():
        while True:
            try:
                frame = capture_pc_frame(scale=0.55, quality=55, show_cursor=True)
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
                await asyncio.sleep(0.09)  # ~11 FPS
            except Exception:
                await asyncio.sleep(0.2)

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.post("/api/files/upload")
async def upload_file_from_mobile(file: UploadFile = File(...)):
    """Receives a file uploaded from mobile and saves it to PC Downloads."""
    try:
        file_path = os.path.join(RECEIVED_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Received file from mobile: {file.filename} -> {file_path}")
        return {
            "success": True,
            "message": f"File '{file.filename}' received and saved to PC Downloads!",
            "path": file_path,
            "size": os.path.getsize(file_path),
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@app.get("/api/files/list")
async def list_received_files():
    """Lists files in the PC_Controller_Received folder."""
    files = []
    if os.path.exists(RECEIVED_DIR):
        for f in os.listdir(RECEIVED_DIR):
            fp = os.path.join(RECEIVED_DIR, f)
            if os.path.isfile(fp):
                files.append({
                    "name": f,
                    "size_mb": round(os.path.getsize(fp) / (1024 * 1024), 2),
                    "modified": os.path.getmtime(fp),
                })
    return {"files": sorted(files, key=lambda x: x["modified"], reverse=True)}


@app.get("/api/files/download/{filename}")
async def download_file_to_mobile(filename: str):
    """Sends a file from PC Downloads folder to mobile."""
    fp = os.path.join(RECEIVED_DIR, filename)
    if os.path.exists(fp) and os.path.isfile(fp):
        return FileResponse(fp, filename=filename)
    return JSONResponse(status_code=404, content={"error": "File not found"})


@app.get("/api/clipboard")
async def get_pc_clipboard():
    """Returns the current text in the PC clipboard."""
    try:
        txt = pyperclip.paste() or ""
        return {"clipboard": txt}
    except Exception as e:
        return {"clipboard": "", "error": str(e)}


@app.post("/api/clipboard")
async def set_pc_clipboard(data: dict):
    """Sets the PC clipboard text from mobile."""
    try:
        txt = data.get("text", "")
        pyperclip.copy(txt)
        return {"success": True, "message": f"PC Clipboard updated ({len(txt)} chars)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/system/wol-info")
async def get_wol_info():
    """Returns PC network interface MAC addresses for mobile Wake-on-LAN."""
    mac_addrs = []
    try:
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK and addr.address:
                    mac_addrs.append({"interface": iface, "mac": addr.address})
    except Exception:
        pass
    return {
        "host": socket.gethostname(),
        "local_ip": settings.LOCAL_IP,
        "mac_addresses": mac_addrs,
    }


@app.post("/api/whatsapp/send")
async def http_whatsapp_send(data: dict):
    """
    Dispatches a WhatsApp message to a phone number or contact name.
    """
    from app.whatsapp_sender import send_whatsapp_message
    recipient = data.get("recipient", "").strip()
    message = data.get("message", "").strip()
    if not recipient or not message:
        return {"success": False, "message": "Recipient and message cannot be empty."}
    return send_whatsapp_message(recipient, message)


@app.post("/api/whatsapp/open_chat")
async def http_whatsapp_open_chat(data: dict):
    """
    Opens a specific WhatsApp chat without typing a message.
    """
    from app.whatsapp_sender import open_whatsapp_chat
    recipient = data.get("recipient", "").strip()
    if not recipient:
        return {"success": False, "message": "Recipient cannot be empty."}
    return open_whatsapp_chat(recipient)


@app.websocket("/ws")
@app.websocket("/ws/controller")
async def websocket_controller_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time bidirectional communication with mobile clients.
    Handles connection handshake, keep-alive ping/pong, and safe PC actions.
    """
    client_host = websocket.client.host if websocket.client else "unknown"
    token = websocket.query_params.get("token")

    # Hardware & Token verification (Locks to User's Honor X6c)
    is_authorized = False
    if client_host in ("127.0.0.1", "::1", "localhost"):
        is_authorized = True
    elif client_host.startswith("100.") and client_host in settings.AUTHORIZED_TAILSCALE_IPS:
        is_authorized = True
    elif token == settings.AUTHORIZED_DEVICE_TOKEN:
        is_authorized = True

    if not is_authorized:
        # Check initial handshake message with device_token or reject immediately
        await websocket.accept()
        try:
            import asyncio
            raw_text = await asyncio.wait_for(websocket.receive_text(), timeout=4.0)
            data = json.loads(raw_text)
            if data.get("type") == "handshake":
                dev_token = data.get("payload", {}).get("device_token")
                if dev_token == settings.AUTHORIZED_DEVICE_TOKEN:
                    is_authorized = True
        except Exception:
            pass

        if not is_authorized:
            logger.warning(f"⛔ Rejecting unauthorized WebSocket connection from: {client_host}")
            try:
                await websocket.send_text(json.dumps({
                    "type": "auth_error",
                    "status": "forbidden",
                    "payload": {"message": "Access Denied: Only authorized Honor X6c device is allowed."}
                }))
                await websocket.close(code=4003)
            except Exception:
                pass
            return

    await ws_manager.connect(websocket)
    client_host = websocket.client.host if websocket.client else "unknown"

    # Send initial welcome / handshake confirmation
    welcome = WSMessageOut(
        type="welcome",
        status="connected",
        payload={
            "server": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "server_ip": settings.LOCAL_IP,
            "message": "Connected to PC Agent. Ready for safe local controller communication.",
        },
    )
    await ws_manager.send_message(websocket, welcome)

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                data = json.loads(raw_text)
                msg_in = WSMessageIn(**data)
            except Exception as parse_err:
                logger.warning(f"Invalid message format received from {client_host}: {raw_text[:100]} | Error: {parse_err}")
                await ws_manager.send_message(
                    websocket,
                    WSMessageOut(
                        type="error",
                        status="invalid_format",
                        payload={"error": "Message must be valid JSON with a 'type' field."},
                    ),
                )
                continue

            # Handle safe message types
            if msg_in.type == "ping":
                await ws_manager.send_message(
                    websocket,
                    WSMessageOut(
                        type="pong",
                        status="ok",
                        payload={"received_at": msg_in.timestamp},
                    ),
                )

            elif msg_in.type == "handshake":
                device_info = msg_in.payload.get("device_name", "Device") if msg_in.payload else "Unknown Device"
                logger.info(f"Handshake received from {device_info} ({client_host})")
                await ws_manager.send_message(
                    websocket,
                    WSMessageOut(
                        type="handshake_ack",
                        status="accepted",
                        payload={
                            "server": settings.PROJECT_NAME,
                            "server_ip": settings.LOCAL_IP,
                            "client_ip": client_host,
                            "session": "active",
                        },
                    ),
                )

            elif msg_in.type == "action":
                # Predefined and dynamic PC actions (volume, mouse, keyboard, apps, system)
                action_name = msg_in.payload.get("action", "") if msg_in.payload else ""
                res = execute_universal_action(action_name, msg_in.payload)
                if not res.get("silent"):
                    await ws_manager.send_message(
                        websocket,
                        WSMessageOut(
                            type="action_result",
                            status="ok" if res["success"] else "error",
                            payload=res,
                        ),
                    )

            elif msg_in.type == "command":
                # Natural language voice and text command interpreter
                query = (msg_in.payload.get("query", "") if msg_in.payload else "").strip()
                logger.info(f"Natural language command received: '{query}' from {client_host}")
                
                # Execute via intelligent AI intent parser
                res = interpret_and_execute_nl(query)
                await ws_manager.send_message(
                    websocket,
                    WSMessageOut(
                        type="action_result",
                        status="ok" if res.get("success", True) else "error",
                        payload={"message": f"'{query}' -> {res.get('message', 'Done')}"},
                    ),
                )

            elif msg_in.type == "status":
                await ws_manager.send_message(
                    websocket,
                    WSMessageOut(
                        type="status",
                        status="ok",
                        payload={
                            "server": settings.PROJECT_NAME,
                            "local_ip": settings.LOCAL_IP,
                            "connected_clients": ws_manager.connection_count,
                        },
                    ),
                )

            else:
                logger.warning(f"Unsupported message type '{msg_in.type}' received from {client_host}")
                await ws_manager.send_message(
                    websocket,
                    WSMessageOut(
                        type="rejected",
                        status="unsupported",
                        payload={"message": f"Action type '{msg_in.type}' is restricted or not implemented."},
                    ),
                )

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info(f"Client disconnected gracefully: {client_host}")
    except Exception as e:
        ws_manager.disconnect(websocket)
        logger.error(f"Unexpected error in WebSocket session for {client_host}: {e}")

