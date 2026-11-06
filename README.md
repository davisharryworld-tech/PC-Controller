# 🎮 Master PC Controller

A powerful, low-latency Windows PC Controller featuring an Android Mobile App (Flutter) and Web Dashboard with live screen mirroring, touch mouse, real-time typing, YouTube/Netflix media remote, PowerPoint slide clicker, wireless file drop, universal clipboard sync, WhatsApp automation, and Wake-on-LAN.

---

## 🌟 Key Features

1. **📺 Live Screen Mirroring & Instant Screenshots**:
   - Real-time low-latency MJPEG video stream of your Windows desktop directly to mobile.
   - 1-tap instant screenshot capture with direct download to mobile storage.

2. **🖱️ Virtual Touchpad & System Controls**:
   - Fixed touchpad surface (drag-lock enabled to prevent screen scrolling).
   - Single tap = Left Click.
   - Double tap = Right Click.
   - Dedicated Left & Right Click buttons.

3. **⌨️ Real-Time Live Typing & Voice Commands**:
   - Live character-by-character keyboard input into any active Windows field.
   - Bilingual voice recognition in Urdu (اردو) and English / Roman Urdu.

4. **🎬 Smart YouTube & Netflix Media Remote**:
   - 10-second fast seek backward (`J`) and forward (`L`).
   - Big Play / Pause.
   - Subtitles toggle (`C`), Playback speed control (`<` and `>`), and Fullscreen (`F`).

5. **📊 PowerPoint & PDF Presentation Clicker**:
   - Huge PREVIOUS (`Page Up`) and NEXT (`Page Down`) buttons for live presentations.
   - Start Slideshow (`F5`), Black Screen (`B`), and Exit (`Esc`).

6. **📁 Wireless File Drop & Universal Clipboard**:
   - Wireless mobile-to-PC file upload saved directly to `Downloads/PC_Controller_Received/`.
   - Bidirectional shared clipboard sync (Phone ⇄ PC).

7. **💬 WhatsApp Automation Hub**:
   - Direct phone number or saved contact opener.
   - Auto-types and dispatches messages with 1 tap.
   - Saved contacts phonebook.

8. **⚡ 1-Tap Quick Workflows / Macros**:
   - Work Mode (VS Code + Chrome).
   - Gaming Mode (Volume boost + YouTube).
   - Study Mode (ChatGPT + Google Docs).
   - Chill Mode (Netflix / YouTube + Fullscreen).

9. **🔌 Wake-on-LAN**:
   - Magic packet sender to turn on shutdown/sleeping PCs over the local network.

---

## 📁 Repository Structure

```
├── PCController/           # Python FastAPI + WebSocket Backend Agent
│   ├── app/
│   │   ├── actions.py      # Win32 & PyAutoGUI action handlers
│   │   ├── dashboard.py    # Responsive HTML5 Mobile & Web Dashboard
│   │   ├── server.py       # FastAPI REST endpoints & WebSocket hub
│   │   ├── config.py       # Configuration & Tailscale detector
│   │   └── schemas.py      # Pydantic data models
│   ├── main.py             # Dual HTTP (8000) & HTTPS (8443) entrypoint
│   └── requirements.txt    # Python dependencies
│
├── pc_controller_app/      # Cross-Platform Flutter Mobile Application
│   ├── lib/
│   │   ├── screens/        # 10 categorized tabs & dashboard
│   │   ├── services/       # WebSocket & HTTP PC Service
│   │   └── main.dart       # App entrypoint
│   └── pubspec.yaml        # Flutter dependencies
│
├── PC_Controller.apk       # Pre-compiled Release Android APK
└── README.md
```

---

## 🚀 Getting Started

### 1. Windows PC Backend Setup
```bash
cd PCController
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 2. Android App
- Transfer and install `PC_Controller.apk` onto your Android phone.
- Ensure both Phone and PC are on the same Wi-Fi network or connected via Tailscale VPN.
- Open the app, and it will automatically connect to your PC controller daemon.
