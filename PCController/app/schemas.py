from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    status: str = "online"
    server_name: str
    version: str
    local_ip: str
    tailscale_ip: Optional[str] = None
    port: int
    connected_clients: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SystemInfoResponse(BaseModel):
    os: str
    cpu_model: str
    total_ram_gb: float
    local_ip: str
    tailscale_ip: Optional[str] = None
    port: int
    ollama_available: bool
    status: str = "ready"


class WSMessageIn(BaseModel):
    type: str  # e.g., 'ping', 'handshake', 'action', 'command', 'status'
    payload: Optional[dict[str, Any]] = None
    device_id: Optional[str] = None
    auth_token: Optional[str] = None
    timestamp: Optional[Any] = None


class WSMessageOut(BaseModel):
    type: str  # e.g., 'pong', 'handshake_ack', 'action_result', 'status', 'error'
    status: str = "ok"
    payload: Optional[dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
