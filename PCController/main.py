import os
import sys
import threading
import uvicorn
from app.config import settings
from app.logger import logger
from generate_cert import generate_self_signed_cert


def print_banner():
    ts_ip = settings.TAILSCALE_IP
    ts_section = f"""  * Tailscale Remote HTTP:   http://{ts_ip}:{settings.PORT}/
  * Tailscale Remote HTTPS:  https://{ts_ip}:{settings.HTTPS_PORT}/ (MIC UNLOCKED!)
  * Remote WebSocket:        ws://{ts_ip}:{settings.PORT}/ws/controller""" if ts_ip else """  * Tailscale Remote IP:     Not connected"""

    banner = f"""
======================================================================
     LOCAL & REMOTE WI-FI AI PC CONTROLLER - PC AGENT v{settings.VERSION}
======================================================================
[LOCAL WI-FI NETWORK]
  * PC Local IP (Wi-Fi/LAN): {settings.LOCAL_IP}
  * HTTP Dashboard:          http://{settings.LOCAL_IP}:{settings.PORT}/
  * HTTPS Dashboard:         https://{settings.LOCAL_IP}:{settings.HTTPS_PORT}/ (MIC ACTIVE)
----------------------------------------------------------------------
[TAILSCALE PRIVATE REMOTE NETWORK]
{ts_section}
----------------------------------------------------------------------
  * HTTP Port:               {settings.PORT}
  * HTTPS Port (Secure Mic): {settings.HTTPS_PORT}
======================================================================
"""
    print(banner)


def run_http_server():
    """Runs HTTP server on port 8000 (accessible normally)."""
    try:
        uvicorn.run(
            "app.server:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=False,
            log_level="warning",
        )
    except Exception as e:
        logger.error(f"HTTP server error: {e}")


def run_https_server():
    """Runs HTTPS server on port 8443 (unlocks Microphone on Android Chrome)."""
    cert_dir = os.path.join(os.path.dirname(__file__), "certs")
    cert_path, key_path = generate_self_signed_cert(cert_dir)
    try:
        uvicorn.run(
            "app.server:app",
            host=settings.HOST,
            port=settings.HTTPS_PORT,
            ssl_keyfile=key_path,
            ssl_certfile=cert_path,
            reload=False,
            log_level="info",
        )
    except Exception as e:
        logger.error(f"HTTPS server error: {e}")


def free_ports(ports):
    """Terminates any stale/orphaned processes holding controller ports before binding."""
    try:
        import psutil
        current_pid = os.getpid()
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port in ports and conn.status == psutil.CONN_LISTEN:
                if conn.pid and conn.pid != current_pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        logger.info(f"Auto-clearing old process {proc.name()} (PID: {conn.pid}) on port {conn.laddr.port}")
                        proc.kill()
                        proc.wait(timeout=2)
                    except Exception as e:
                        logger.warning(f"Could not kill process {conn.pid}: {e}")
    except Exception as e:
        logger.warning(f"Could not scan network ports: {e}")


def main():
    free_ports([settings.PORT, settings.HTTPS_PORT])
    print_banner()
    logger.info("Initializing Dual HTTP (8000) & HTTPS (8443) PC Controller...")
    
    # Run HTTP server in background thread so both HTTP & HTTPS work simultaneously
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Run HTTPS server on main thread
    try:
        run_https_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"Server encountered fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
