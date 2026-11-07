import os
import socket
import subprocess
from typing import Optional


def detect_local_ip() -> str:
    """
    Detect the local IPv4 address used on the active LAN/Wi-Fi network.
    Uses UDP socket connect (does not send data) to query OS routing table.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 8.8.8.8:80 is used solely to determine which local network interface routes outbound traffic
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass

    # Fallback method: hostname resolution
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and not ip.startswith("169.254."):
                return ip
    except Exception:
        pass

    return "127.0.0.1"


def detect_tailscale_ip() -> Optional[str]:
    """
    Detect the private Tailscale IPv4 address (100.x.y.z) if Tailscale is active.
    """
    tailscale_cli = r"C:\Program Files\Tailscale\tailscale.exe"
    if os.path.exists(tailscale_cli):
        try:
            res = subprocess.run([tailscale_cli, "ip", "-4"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                ip = res.stdout.strip()
                if ip.startswith("100."):
                    return ip
        except Exception:
            pass

    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip.startswith("100."):
                return ip
    except Exception:
        pass

    return None


class Settings:
    PROJECT_NAME: str = "Local AI PC Controller"
    VERSION: str = "0.2.0"
    HOST: str = os.getenv("PC_AGENT_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PC_AGENT_PORT", "8000"))
    HTTPS_PORT: int = int(os.getenv("PC_AGENT_HTTPS_PORT", "8443"))
    LOCAL_IP: str = detect_local_ip()

    @property
    def SSL_CERT_PATH(self) -> str:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "certs", "cert.pem")

    @property
    def SSL_KEY_PATH(self) -> str:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "certs", "key.pem")

    @property
    def TAILSCALE_IP(self) -> Optional[str]:
        return detect_tailscale_ip()

    # Allowed origins for CORS (LAN, Tailscale mesh, and localhost)
    CORS_ORIGINS: list[str] = [
        "*",
    ]

    # Exclusive Device Whitelisting (Locks access exclusively to User's Honor X6c)
    AUTHORIZED_TAILSCALE_IPS: list[str] = ["100.81.196.79"]
    AUTHORIZED_DEVICE_NAME: str = "honor-x6c"
    AUTHORIZED_DEVICE_TOKEN: str = os.getenv("PC_AUTHORIZED_DEVICE_TOKEN", "HX6C-982341-EXCLUSIVE-HONOR-TOKEN")


settings = Settings()
