# Free Local Wi-Fi AI PC Controller - PC Agent Foundation

A lightweight, secure, and completely local PC agent server built with FastAPI and WebSockets. It enables local Wi-Fi communication between an Android mobile phone and your Windows 11 PC without internet dependencies, cloud subscriptions, or port forwarding.

---

## Architecture Overview

```
PCController/
├── .venv/                 # Python 3.11 isolated virtual environment
├── app/
│   ├── __init__.py        # Package metadata (v0.1.0)
│   ├── config.py          # Auto-detection of local Wi-Fi IP and server settings
│   ├── logger.py          # Dual console & file logger (logs/pc_agent.log)
│   ├── schemas.py         # Pydantic schemas for health & WebSocket messaging
│   ├── server.py          # FastAPI application, REST endpoints, and WebSocket handler
│   └── ws_manager.py      # Connection manager for active mobile/client sessions
├── logs/                  # Server operation logs
├── main.py                # Server entry point with startup network banner
├── test_client.py         # Automated test suite (Health check & WebSocket verification)
├── requirements.txt       # Minimal, lightweight dependencies
└── README.md              # Documentation
```

---

## Requirements

* Windows 11
* Python 3.11 (installed in `.venv`)
* Both the Windows PC and Android phone must be connected to the **same local Wi-Fi network**.

---

## How to Start the PC Agent

### Using PowerShell:
1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd "e:\personal AI\PCController"
   ```

2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Start the PC agent:
   ```powershell
   python main.py
   ```

Upon starting, the server will detect your local network IP and display:
```
======================================================================
         FREE LOCAL WI-FI AI PC CONTROLLER - PC AGENT
======================================================================
  * PC Local IP (Wi-Fi/LAN): 10.69.9.202
  * Binding Host:            0.0.0.0
  * Binding Port:            8000
----------------------------------------------------------------------
  * Health / Status Check:   http://10.69.9.202:8000/health
  * System Info:             http://10.69.9.202:8000/api/system
  * WebSocket Endpoint:      ws://10.69.9.202:8000/ws/controller
======================================================================
```

---

## How to Stop the PC Agent

To gracefully stop the server at any time:
* Press **`Ctrl + C`** in the terminal window where the server is running.
* The server will disconnect active clients, flush logs, and exit cleanly.

---

## Verification & Testing

With the server running, open a second terminal window to run the automated verification suite:

```powershell
cd "e:\personal AI\PCController"
.\.venv\Scripts\python.exe test_client.py
```

This will automatically test:
1. `GET /health` - Verifies server status, name, version, and local IP.
2. `GET /api/system` - Verifies system hardware and OS reporting.
3. `WebSocket ws://127.0.0.1:8000/ws/controller` - Verifies handshake, ping/pong keepalive, and status queries.

---

## Security & Safety Guardrails

* **Local Network Only:** Binds strictly for local LAN/Wi-Fi communication. No port forwarding, no UPnP, and no cloud exposure.
* **No Arbitrary Commands:** The server does not execute shell commands or arbitrary code received over the network.
* **No Elevated Privileges:** Runs with standard user privileges without requesting administrator elevation.
* **No Credential Storage:** No passwords, keys, or sensitive personal data are collected or persisted.
* **Lightweight:** Minimal memory footprint designed specifically for 8GB RAM PCs.

