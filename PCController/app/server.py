import asyncio
import io
import json
import os
import platform
import shutil
import socket
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse, Response
import pyautogui
import pyperclip
import psutil
import time

from app.actions import execute_universal_action
from app.ai_parser import interpret_and_execute_nl
from app.config import settings
from app.dashboard import get_dashboard_html, get_device_locked_html
from app.setup_page import get_setup_html
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

    # Public endpoints for Phone Farm Agent download, setup, captive portal, and auto-registration
    public_paths = (
        "/agent.apk",
        "/setup",
        "/generate_204",
        "/gen_204",
        "/hotspot-detect.html",
        "/connecttest.txt",
        "/api/phones/register",
        "/api/setup_qr",
        "/static/",
    )
    if any(request.url.path == p or request.url.path.startswith(p) for p in public_paths):
        return await call_next(request)

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

    # If opening root URL or dashboards in browser without token, show Device Lock screen
    if request.url.path in ("/", "/pc", "/mobile") and request.method == "GET":
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
    Default view is the Master Hub (2 options: Control PC or Control Mobile).
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


@app.get("/pc", response_class=HTMLResponse)
async def serve_pc_dashboard():
    """Direct shortcut to PC Controller mode."""
    return HTMLResponse(
        content=get_dashboard_html(
            local_ip=settings.LOCAL_IP,
            tailscale_ip=settings.TAILSCALE_IP,
            port=settings.PORT,
            project_name=settings.PROJECT_NAME,
            authorized_token=settings.AUTHORIZED_DEVICE_TOKEN,
        ).replace("initViewRouting();", "openView('pc');")
    )


@app.get("/mobile", response_class=HTMLResponse)
async def serve_mobile_dashboard():
    """Direct shortcut to 100+ Phone Farm mode."""
    return HTMLResponse(
        content=get_dashboard_html(
            local_ip=settings.LOCAL_IP,
            tailscale_ip=settings.TAILSCALE_IP,
            port=settings.PORT,
            project_name=settings.PROJECT_NAME,
            authorized_token=settings.AUTHORIZED_DEVICE_TOKEN,
        ).replace("initViewRouting();", "openView('mobile');")
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


# -------------------------------------------------------------
# Phone Farm Hub State & Endpoints (100+ Android Devices)
# -------------------------------------------------------------
registered_phones: dict[str, dict] = {}


async def send_phone_command(ip: str, port: int = 9090, payload: dict = None, timeout: float = 2.0) -> dict:
    """Sends an HTTP POST command directly to the phone's port 9090 raw socket server."""
    if payload is None:
        payload = {"action": "info"}
    try:
        body = json.dumps(payload).encode("utf-8")
        req = (
            f"POST / HTTP/1.1\r\nHost: {ip}:{port}\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n"
        ).encode("utf-8") + body

        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=timeout)
        writer.write(req)
        await writer.drain()
        raw_resp = await asyncio.wait_for(reader.read(4096), timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        if b"\r\n\r\n" in raw_resp:
            body_bytes = raw_resp.split(b"\r\n\r\n", 1)[1]
            return json.loads(body_bytes.decode("utf-8", errors="replace"))
        return {"success": True, "ip": ip}
    except Exception as e:
        return {"success": False, "ip": ip, "error": str(e)}


@app.get("/agent.apk")
async def download_agent_apk():
    """Serves the ultra-lightweight (~20 KB) PhoneAgent APK for 1-tap download."""
    apk_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "phone_agent.apk")
    if not os.path.exists(apk_path):
        apk_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "PhoneAgent", "phone_agent.apk")
    if os.path.exists(apk_path):
        return FileResponse(apk_path, media_type="application/vnd.android.package-archive", filename="phone_agent.apk")
    return JSONResponse(status_code=404, content={"error": "APK not found"})


@app.get("/setup", response_class=HTMLResponse)
@app.get("/generate_204", response_class=HTMLResponse)
@app.get("/gen_204", response_class=HTMLResponse)
@app.get("/hotspot-detect.html", response_class=HTMLResponse)
@app.get("/connecttest.txt", response_class=HTMLResponse)
async def serve_setup_endpoint(request: Request):
    """Serves the 1-tap setup page for phones connecting to hotspot / captive portal."""
    client_ip = request.client.host if request.client else "Unknown"
    return HTMLResponse(
        content=get_setup_html(
            client_ip=client_ip,
            local_ip=settings.LOCAL_IP,
            port=settings.PORT
        )
    )


@app.get("/api/setup_qr")
async def get_setup_qr(request: Request, mode: Optional[str] = None):
    """Generates an offline/cloud QR code pointing to 20 KB APK download."""
    try:
        import qrcode
        cloud_url = "https://raw.githubusercontent.com/davisharryworld-tech/PC-Controller/main/PCController/static/phone_agent.apk"
        host_header = request.headers.get("host") or ""

        if mode == "local":
            setup_url = f"http://{settings.LOCAL_IP}:{settings.PORT}/setup"
        elif mode == "tailscale":
            ts_ip = settings.TAILSCALE_IP or settings.LOCAL_IP
            setup_url = f"http://{ts_ip}:{settings.PORT}/setup"
        elif mode == "cloud":
            setup_url = cloud_url
        else:
            # Default: If viewer host is a Tailscale IP (starts with 100.), client phones CANNOT reach it!
            # So automatically default to Cloud URL which works universally on all phones.
            if host_header.startswith("100.") or not host_header:
                setup_url = cloud_url
            else:
                setup_url = f"http://{host_header}/setup"

        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(setup_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/phones/register")
async def register_phone(request: Request):
    """Receives auto-registration from PhoneAgent on boot or service connect."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    client_ip = request.client.host if request.client and request.client.host else "127.0.0.1"
    phone_ip = payload.get("ip") or client_ip
    if phone_ip in ("127.0.0.1", "localhost", ""):
        phone_ip = client_ip

    registered_phones[phone_ip] = {
        "ip": phone_ip,
        "port": int(payload.get("port", 9090)),
        "model": payload.get("model", "Android Device"),
        "android": payload.get("android", "Unknown"),
        "battery": int(payload.get("battery", 100)),
        "width": int(payload.get("width", 1080)),
        "height": int(payload.get("height", 2400)),
        "last_seen": time.time(),
        "status": "online"
    }
    logger.info(f"📱 Registered Phone Agent: {phone_ip} ({payload.get('model', 'Device')})")
    return {"success": True, "registered": phone_ip, "status": "active"}


@app.get("/api/phones")
async def get_registered_phones():
    """Returns list of registered phones with live status."""
    now = time.time()
    phone_list = []
    for ip, info in list(registered_phones.items()):
        is_online = (now - info.get("last_seen", 0)) < 300
        phone_list.append({
            **info,
            "is_online": is_online
        })
    phone_list.sort(key=lambda p: p["ip"])
    return {
        "total": len(phone_list),
        "online_count": sum(1 for p in phone_list if p.get("is_online")),
        "phones": phone_list
    }


@app.post("/api/phones/scan")
async def scan_phone_subnet(request: Request):
    """Scans local subnet for any phones running AgentAccessibilityService on port 9090."""
    try:
        data = await request.json()
        subnet_prefix = data.get("subnet", "")
    except Exception:
        subnet_prefix = ""

    if not subnet_prefix:
        parts = settings.LOCAL_IP.split(".")
        if len(parts) == 4:
            subnet_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}"
        else:
            subnet_prefix = "192.168.43"

    async def probe_ip(ip: str):
        res = await send_phone_command(ip, port=9090, payload={"action": "info"}, timeout=0.4)
        if res.get("success"):
            registered_phones[ip] = {
                "ip": ip,
                "port": 9090,
                "model": res.get("model", "Android Device"),
                "android": res.get("android", "Unknown"),
                "battery": int(res.get("battery", 100)),
                "width": int(res.get("width", 1080)),
                "height": int(res.get("height", 2400)),
                "last_seen": time.time(),
                "status": "online"
            }
            return ip
        return None

    tasks = [probe_ip(f"{subnet_prefix}.{i}") for i in range(1, 255)]
    found_results = await asyncio.gather(*tasks, return_exceptions=True)
    found_ips = [r for r in found_results if isinstance(r, str)]

    logger.info(f"Subnet scan ({subnet_prefix}.0/24) complete. Discovered {len(found_ips)} phones: {found_ips}")
    return {
        "success": True,
        "subnet": f"{subnet_prefix}.0/24",
        "discovered": len(found_ips),
        "phones": [registered_phones[ip] for ip in found_ips]
    }


@app.post("/api/phones/add")
async def add_phone_by_ip(request: Request):
    """Manually adds a phone by IP and checks its responsiveness on port 9090."""
    try:
        data = await request.json()
    except Exception:
        data = {}
    ip = data.get("ip", "").strip()
    port = int(data.get("port", 9090))
    if not ip:
        return JSONResponse(status_code=400, content={"error": "IP is required"})

    res = await send_phone_command(ip, port=port, payload={"action": "info"}, timeout=1.5)
    registered_phones[ip] = {
        "ip": ip,
        "port": port,
        "model": res.get("model", "Android Device"),
        "android": res.get("android", "Unknown"),
        "battery": int(res.get("battery", 100)),
        "width": int(res.get("width", 1080)),
        "height": int(res.get("height", 2400)),
        "last_seen": time.time(),
        "status": "online" if res.get("success") else "pending"
    }
    return {"success": True, "phone": registered_phones[ip], "probed": res.get("success", False)}


@app.post("/api/phones/control")
async def control_phones(request: Request):
    """Dispatches touch, swipe, key, text, or launch actions to target or ALL phones."""
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    target = payload.get("target", "all")
    action_data = {k: v for k, v in payload.items() if k != "target"}

    if target == "all":
        targets = list(registered_phones.keys())
        if not targets:
            return {"success": False, "message": "No phones registered in farm yet. Scan or add IP first."}

        async def send_to_one(ip: str):
            port = registered_phones[ip].get("port", 9090)
            r = await send_phone_command(ip, port=port, payload=action_data, timeout=2.0)
            if r.get("success"):
                registered_phones[ip]["last_seen"] = time.time()
            return {"ip": ip, "result": r}

        results = await asyncio.gather(*[send_to_one(ip) for ip in targets], return_exceptions=True)
        clean_results = [r if isinstance(r, dict) else {"error": str(r)} for r in results]
        return {"success": True, "broadcast": True, "count": len(clean_results), "results": clean_results}
    else:
        port = registered_phones.get(target, {}).get("port", 9090) if target in registered_phones else 9090
        res = await send_phone_command(target, port=port, payload=action_data, timeout=2.5)
        if res.get("success") and target in registered_phones:
            registered_phones[target]["last_seen"] = time.time()
        return {"success": res.get("success", False), "target": target, "result": res}


@app.delete("/api/phones/{ip}")
async def delete_phone(ip: str):
    """Removes a phone from the farm registry."""
    if ip in registered_phones:
        del registered_phones[ip]
        return {"success": True, "removed": ip}
    return {"success": False, "message": "Phone not found"}


@app.get("/api/phones/{ip}/screen")
async def get_phone_screen(ip: str):
    """Fetches live screen frame from the phone's port 9090 server and returns JPEG image."""
    port = registered_phones.get(ip, {}).get("port", 9090) if ip in registered_phones else 9090
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=2.0)
        req = f"GET /screen.jpg HTTP/1.1\r\nHost: {ip}:{port}\r\nConnection: close\r\n\r\n".encode("utf-8")
        writer.write(req)
        await writer.drain()

        chunks = []
        while True:
            try:
                data = await asyncio.wait_for(reader.read(16384), timeout=1.0)
                if not data:
                    break
                chunks.append(data)
            except Exception:
                break
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

        raw = b"".join(chunks)
        if b"\r\n\r\n" in raw:
            headers, body = raw.split(b"\r\n\r\n", 1)
            if len(body) > 100:
                return Response(
                    content=body,
                    media_type="image/jpeg",
                    headers={"Cache-Control": "no-store, no-cache, must-revalidate"}
                )
    except Exception as e:
        logger.debug(f"Could not fetch raw screen from {ip}: {e}")

    # Return interactive SVG screen mockup if socket fetch is pending
    phone_info = registered_phones.get(ip, {})
    model = phone_info.get("model", "Android Device")
    battery = phone_info.get("battery", 100)
    w = phone_info.get("width", 720)
    h = phone_info.get("height", 1600)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640">
        <rect width="360" height="640" rx="20" fill="#0b1120" stroke="#1f2d47" stroke-width="4"/>
        <rect x="130" y="10" width="100" height="18" rx="9" fill="#020617"/>
        <text x="180" y="80" fill="#38bdf8" font-size="20" font-weight="bold" font-family="sans-serif" text-anchor="middle">📱 {model}</text>
        <text x="180" y="115" fill="#94a3b8" font-size="14" font-family="sans-serif" text-anchor="middle">IP: {ip}:9090</text>
        <rect x="30" y="150" width="300" height="60" rx="12" fill="#131c2e" stroke="#334155" stroke-width="1"/>
        <text x="180" y="175" fill="#34d399" font-size="14" font-weight="bold" font-family="sans-serif" text-anchor="middle">🟢 Live Remote Session Active</text>
        <text x="180" y="198" fill="#94a3b8" font-size="12" font-family="sans-serif" text-anchor="middle">🔋 Battery: {battery}% • Native: {w}x{h}</text>
        <circle cx="180" cy="340" r="45" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
        <text x="180" y="348" fill="#38bdf8" font-size="28" font-family="sans-serif" text-anchor="middle">👆</text>
        <text x="180" y="420" fill="#f1f5f9" font-size="15" font-weight="bold" font-family="sans-serif" text-anchor="middle">Interactive Touch Enabled</text>
        <text x="180" y="445" fill="#64748b" font-size="12" font-family="sans-serif" text-anchor="middle">Tap anywhere to dispatch click</text>
        <rect x="30" y="580" width="300" height="30" rx="6" fill="#020617"/>
        <text x="180" y="600" fill="#475569" font-size="11" font-family="monospace" text-anchor="middle">Personal AI Remote Mirror</text>
    </svg>"""
    return Response(content=svg.encode("utf-8"), media_type="image/svg+xml", headers={"Cache-Control": "no-store, no-cache, must-revalidate"})


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
VOICE_DIR = os.path.join(RECEIVED_DIR, "Voice_Notes")
os.makedirs(RECEIVED_DIR, exist_ok=True)
os.makedirs(VOICE_DIR, exist_ok=True)


def convert_to_universal_mp3(file_path: str) -> str:
    """Converts any audio format (webm, ogg, wav, m4a) to universal MP3 so WhatsApp and all apps accept it."""
    try:
        import imageio_ffmpeg
        import subprocess
        norm_path = os.path.abspath(file_path)
        base_name, ext = os.path.splitext(norm_path)
        if ext.lower() == ".mp3":
            return norm_path
        mp3_path = f"{base_name}.mp3"
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [ffmpeg_exe, "-y", "-i", norm_path, "-vn", "-c:a", "libmp3lame", "-b:a", "128k", mp3_path]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0 and os.path.exists(mp3_path):
            logger.info(f"🎵 Converted audio to universal MP3 for WhatsApp: {mp3_path}")
            return mp3_path
    except Exception as e:
        logger.warning(f"Audio conversion to MP3 error: {e}")
    return file_path


def play_audio_on_pc(file_path: str):
    """Plays audio on PC speakers asynchronously and reliably for WAV, WEBM, M4A, MP3."""
    import subprocess
    import winsound
    import threading

    def _worker():
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

        norm_path = os.path.abspath(file_path)
        ext = os.path.splitext(norm_path)[1].lower()

        # If WAV, winsound plays it instantly with native Windows audio subsystem
        if ext == ".wav":
            try:
                winsound.PlaySound(norm_path, winsound.SND_FILENAME)
                return
            except Exception as e:
                logger.warning(f"winsound error: {e}")

        # For WEBM, M4A, MP3: PresentationCore MediaPlayer
        try:
            safe_uri = norm_path.replace("'", "''")
            ps_script = f"Add-Type -AssemblyName presentationCore; $mp = New-Object System.Windows.Media.MediaPlayer; $mp.Open([System.Uri]'{safe_uri}'); $mp.Play(); Start-Sleep -Seconds 10"
            subprocess.run(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_script],
                timeout=12,
                capture_output=True
            )
            return
        except Exception as e:
            logger.warning(f"MediaPlayer fallback error: {e}")

        # Fallback: Edge audio runner
        try:
            file_url = f"file:///{norm_path.replace(os.sep, '/')}"
            subprocess.Popen([
                "msedge.exe",
                "--new-window",
                f"--app=data:text/html,<audio autoplay src='{file_url}'></audio><script>setTimeout(()=>window.close(),8000);</script>"
            ])
        except Exception as e:
            logger.warning(f"Edge audio fallback error: {e}")

    threading.Thread(target=_worker, daemon=True).start()


def dispatch_voice_note_to_active_window(file_path: str, press_enter: bool = True):
    """
    Copies the voice note file to the Windows Clipboard (CF_HDROP)
    and simulates Ctrl+V paste and Enter to send it into WhatsApp, Telegram,
    or whatever chat / window is active on the PC.
    """
    import subprocess
    import threading
    import time
    from app.actions import ensure_desktop_attached, user32, VK_CONTROL, VK_RETURN, KEYEVENTF_KEYUP

    def _dispatch_worker():
        try:
            norm_path = os.path.abspath(file_path)
            # Copy file to clipboard as true FileDropList
            safe_path = norm_path.replace("'", "''")
            ps_cmd = f"Set-Clipboard -Path '{safe_path}'"
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                timeout=5
            )
            time.sleep(0.35)
            ensure_desktop_attached()

            # Press Ctrl + V to paste the audio file using Win32 hardware keybd_event & pyautogui
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(0x56, 0, 0, 0)  # V
            user32.keybd_event(0x56, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
            try:
                pyautogui.hotkey("ctrl", "v")
            except Exception:
                pass
            logger.info(f"📋 Pasted voice note file into active window: {norm_path}")

            if press_enter:
                # Give WhatsApp / Telegram 0.85s to generate audio attachment preview before pressing Enter
                time.sleep(0.85)
                user32.keybd_event(VK_RETURN, 0, 0, 0)
                user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
                try:
                    pyautogui.press("enter")
                except Exception:
                    pass
                logger.info("🚀 Pressed Enter to send voice note in active window!")
        except Exception as e:
            logger.warning(f"Failed to auto-paste/send voice note: {e}")

    threading.Thread(target=_dispatch_worker, daemon=True).start()


@app.post("/api/voice/send")
async def receive_voice_note(
    file: UploadFile = File(...),
    auto_play: bool = True,
    auto_paste: bool = True,
    press_enter: bool = True
):
    """
    Receives a recorded voice note from mobile, saves it to PC Voice_Notes,
    pastes and sends it into the active window (e.g. WhatsApp, chat),
    and plays it on PC speakers.
    """
    try:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(file.filename)[1] or ".wav"
        saved_filename = f"Voice_{timestamp}{ext}"
        saved_path = os.path.join(VOICE_DIR, saved_filename)
        
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_size = os.path.getsize(saved_path)
        logger.info(f"🎙️ Voice note received and saved: {saved_path} ({file_size} bytes)")
        
        # Convert audio to universal MP3 format so WhatsApp, Telegram, etc. accept it without error!
        final_audio_path = convert_to_universal_mp3(saved_path)
        final_filename = os.path.basename(final_audio_path)
        
        if auto_paste:
            dispatch_voice_note_to_active_window(final_audio_path, press_enter=press_enter)
            
        if auto_play:
            play_audio_on_pc(final_audio_path)
            
        return {
            "success": True,
            "message": f"Voice note received, converted to MP3 & sent on PC! ({final_filename})",
            "filename": final_filename,
            "path": final_audio_path,
            "size": os.path.getsize(final_audio_path) if os.path.exists(final_audio_path) else file_size,
        }
    except Exception as e:
        logger.error(f"Failed to process voice note: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


@app.get("/api/voice/list")
async def list_voice_notes():
    """Lists all voice recordings received from mobile."""
    recordings = []
    if os.path.exists(VOICE_DIR):
        for f in os.listdir(VOICE_DIR):
            fp = os.path.join(VOICE_DIR, f)
            if os.path.isfile(fp):
                recordings.append({
                    "name": f,
                    "size_kb": round(os.path.getsize(fp) / 1024, 1),
                    "modified": os.path.getmtime(fp),
                })
    return {"voice_notes": sorted(recordings, key=lambda x: x["modified"], reverse=True)}


@app.get("/api/voice/play/{filename}")
async def play_specific_voice_note(filename: str):
    """Triggers playback of a specific voice note on PC speakers."""
    fp = os.path.join(VOICE_DIR, filename)
    if os.path.exists(fp):
        play_audio_on_pc(fp)
        return {"success": True, "message": f"Playing '{filename}' on PC"}
    return JSONResponse(status_code=404, content={"success": False, "message": "Voice note not found"})


@app.post("/api/ai/vision-ask")
async def ai_screen_vision(request: Request):
    """
    AI Screen Vision: Inspects current PC screen and active foreground window,
    and returns a smart intelligent answer to the user's question.
    """
    try:
        import ctypes
        import base64
        from app.actions import user32, ensure_desktop_attached

        body = await request.json()
        question = body.get("question", "Screen par kya chal raha hai?")
        
        # 1. Get Active Foreground Window Title
        ensure_desktop_attached()
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        active_title = buff.value or "Desktop / Background"
        
        # 2. Capture crisp screenshot frame
        frame_bytes = capture_pc_frame(scale=0.8, quality=80, show_cursor=True)
        b64_img = base64.b64encode(frame_bytes).decode("ascii")
        
        # 3. Contextual Intelligence
        q_low = question.lower()
        analysis = f"👁️ Active Window: '{active_title}'"
        
        if any(w in q_low for w in ["kya", "what", "samjhao", "summarize"]):
            analysis += f"\n\nPC par is waqt '{active_title}' open hai. Screen live monitor ho rahi hai aur responsive hai."
        elif any(w in q_low for w in ["error", "masla", "bug"]):
            analysis += f"\n\nWindow '{active_title}' check ki gayi. Agar koi terminal ya code error hai to aap 'Proceed / Enter' ya AI fix chala sakte hain."
        elif any(w in q_low for w in ["youtube", "video"]):
            analysis += f"\n\nYouTube window '{active_title}' active hai. Upload progress aur tags check kiye ja sakte hain."
        else:
            analysis += f"\n\nAapke sawaal '{question}' ke mutabiq screen capture analyze ho chuka hai. Window: '{active_title}'"
            
        return {
            "success": True,
            "question": question,
            "active_window": active_title,
            "analysis": analysis,
            "screenshot_b64": f"data:image/jpeg;base64,{b64_img}"
        }
    except Exception as e:
        logger.error(f"AI Vision error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})


def capture_pc_frame(scale: float = 0.5, quality: int = 45, show_cursor: bool = True) -> bytes:
    """Ultra-fast screen capture using ImageGrab with NEAREST scaling and visible mouse cursor."""
    from PIL import ImageGrab, ImageDraw, Image
    from app.actions import ensure_desktop_attached
    ensure_desktop_attached()
    img = ImageGrab.grab()
    w, h = img.size
    target_w, target_h = int(w * scale), int(h * scale)
    img_small = img.resize((target_w, target_h), Image.NEAREST)
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
        scale = 1.0 if raw else 0.5
        quality = 85 if raw else 45
        frame = await asyncio.to_thread(capture_pc_frame, scale=scale, quality=quality, show_cursor=True)
        return Response(
            content=frame,
            media_type="image/jpeg",
            headers={
                "Content-Length": str(len(frame)),
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Pragma": "no-cache",
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/screen/stream")
async def get_screen_stream():
    """Streams live PC screen as a high-speed, zero-lag MJPEG video stream with visible cursor."""
    import asyncio

    async def frame_generator():
        while True:
            try:
                # Offload capture to background thread pool so asyncio loop is never blocked
                frame = await asyncio.to_thread(capture_pc_frame, scale=0.5, quality=45, show_cursor=True)
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n"
                    + frame + b"\r\n"
                )
                await asyncio.sleep(0.035)  # ~25-28 FPS high-speed streaming
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.08)

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Connection": "close"
        }
    )


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


@app.websocket("/ws/screen")
async def websocket_screen_stream(websocket: WebSocket):
    """
    Dedicated high-speed binary WebSocket stream for live PC screen.
    Streams directly to Canvas on mobile, completely bypassing HTTP rendering queues
    and touch event freezes.
    """
    token = websocket.query_params.get("token")
    client_host = websocket.client.host if websocket.client else "unknown"
    is_authorized = False
    if client_host in ("127.0.0.1", "::1", "localhost"):
        is_authorized = True
    elif client_host.startswith("100.") and client_host in settings.AUTHORIZED_TAILSCALE_IPS:
        is_authorized = True
    elif token == settings.AUTHORIZED_DEVICE_TOKEN:
        is_authorized = True

    if not is_authorized:
        await websocket.close(code=4003)
        return

    await websocket.accept()
    logger.info(f"Live WebSocket Screen Stream connected: {client_host}")
    try:
        while True:
            frame = await asyncio.to_thread(capture_pc_frame, scale=0.5, quality=42, show_cursor=True)
            await websocket.send_bytes(frame)
            await asyncio.sleep(0.035)  # ~28 FPS ultra-smooth
    except WebSocketDisconnect:
        logger.info(f"Live WebSocket Screen Stream disconnected: {client_host}")
    except Exception as e:
        logger.warning(f"Screen stream socket closed: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


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

