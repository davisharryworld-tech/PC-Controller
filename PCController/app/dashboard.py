def get_device_locked_html(client_ip: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>⛔ Access Denied - Device Locked</title>
  <style>
    body {{
      background: #090d16;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      padding: 16px;
      box-sizing: border-box;
    }}
    .card {{
      background: #131c2e;
      border: 1px solid #ef4444;
      border-radius: 16px;
      max-width: 440px;
      width: 100%;
      padding: 28px 24px;
      text-align: center;
      box-shadow: 0 8px 32px rgba(239, 68, 68, 0.2);
    }}
    .icon {{
      font-size: 3.5rem;
      margin-bottom: 12px;
    }}
    h1 {{
      font-size: 1.35rem;
      color: #ef4444;
      margin-bottom: 8px;
    }}
    p {{
      font-size: 0.88rem;
      color: #94a3b8;
      line-height: 1.5;
      margin-bottom: 20px;
    }}
    .badge {{
      background: rgba(239, 68, 68, 0.15);
      color: #fca5a5;
      border: 1px solid rgba(239, 68, 68, 0.3);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 0.8rem;
      display: inline-block;
      margin-bottom: 20px;
    }}
    .input-box {{
      width: 100%;
      padding: 12px;
      background: #0b1120;
      border: 1px solid #334155;
      border-radius: 8px;
      color: #fff;
      font-size: 0.9rem;
      margin-bottom: 12px;
      box-sizing: border-box;
      text-align: center;
    }}
    .btn {{
      width: 100%;
      padding: 12px;
      background: #4f46e5;
      border: none;
      border-radius: 8px;
      color: #fff;
      font-weight: 700;
      cursor: pointer;
      font-size: 0.9rem;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">⛔</div>
    <h1>Access Denied: Device Locked</h1>
    <div class="badge">Unrecognized Client IP: {client_ip}</div>
    <p>
      Ye PC Controller sirf aur sirf <b>Honor X6c</b> mobile ke liye exclusive lock hai. Kisi aur device ko access ki ijazat nahi hai.
    </p>
    <div style="text-align:left; font-size:0.75rem; color:#64748b; margin-bottom:6px;">
      Device Pairing Key (Sirf Owner k liye):
    </div>
    <input type="password" id="devKey" class="input-box" placeholder="Enter Secret Device Key..." />
    <button class="btn" onclick="unlockDevice()">Authorize Device</button>
  </div>
  <script>
    function unlockDevice() {{
      const key = document.getElementById("devKey").value.trim();
      if (!key) return alert("Secret Key enter karein!");
      localStorage.setItem("device_token", key);
      document.cookie = "device_token=" + key + "; path=/; max-age=31536000";
      location.href = "/?token=" + encodeURIComponent(key);
    }}
    const saved = localStorage.getItem("device_token");
    if (saved && !location.search.includes("token=")) {{
      location.href = "/?token=" + encodeURIComponent(saved);
    }}
  </script>
</body>
</html>"""


def get_dashboard_html(local_ip: str, port: int, project_name: str, tailscale_ip: str = None, authorized_token: str = "") -> str:
    ts_info = f'<div style="font-size:0.75rem; color:#818cf8; margin-top:2px;">🔒 Tailscale Remote: {tailscale_ip}</div>' if tailscale_ip else '<div style="font-size:0.72rem; color:#64748b; margin-top:2px;">Tailscale: not active</div>'
    server_http_origin = f"http://{tailscale_ip or local_ip}:{port}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{project_name} - Master PC Controller</title>
  <style>
    :root {{
      --bg: #090d16;
      --card: #131c2e;
      --card-border: #1e293b;
      --accent: #6366f1;
      --accent-hover: #4f46e5;
      --accent-light: rgba(99, 102, 241, 0.15);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --success: #10b981;
      --danger: #ef4444;
      --warning: #f59e0b;
      --radius: 14px;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      -webkit-tap-highlight-color: transparent;
    }}
    body {{
      background: var(--bg);
      color: var(--text);
      display: flex;
      justify-content: center;
      min-height: 100vh;
      padding: 12px;
      overflow-x: hidden;
    }}
    .container {{
      width: 100%;
      max-width: 520px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 4px 2px;
    }}
    .logo-box h1 {{
      font-size: 1.25rem;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #fff;
    }}
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(16, 185, 129, 0.15);
      color: var(--success);
      padding: 5px 12px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 700;
      border: 1px solid rgba(16, 185, 129, 0.3);
      cursor: pointer;
      transition: all 0.3s;
    }}
    .status-badge.disconnected {{
      background: rgba(239, 68, 68, 0.15);
      color: var(--danger);
      border-color: rgba(239, 68, 68, 0.3);
    }}
    .dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: currentColor;
      box-shadow: 0 0 6px currentColor;
    }}
    .toast {{
      position: fixed;
      top: 14px;
      left: 50%;
      transform: translateX(-50%) translateY(-90px);
      background: #1e293b;
      color: #fff;
      padding: 10px 22px;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 700;
      border: 1.5px solid var(--accent);
      box-shadow: 0 8px 24px rgba(0,0,0,0.7);
      pointer-events: none;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 9999;
      opacity: 0;
      text-align: center;
      max-width: 90%;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .toast.show {{
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }}
    .tabs {{
      display: flex;
      background: var(--card);
      padding: 4px;
      border-radius: 12px;
      border: 1px solid var(--card-border);
      gap: 3px;
      overflow-x: auto;
    }}
    .tab-btn {{
      flex: 1;
      padding: 9px 4px;
      border-radius: 8px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      text-align: center;
      white-space: nowrap;
      transition: all 0.2s;
    }}
    .tab-btn.active {{
      background: var(--accent);
      color: #fff;
      box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
    }}
    .tab-content {{
      display: none;
      flex-direction: column;
      gap: 12px;
    }}
    .tab-content.active {{
      display: flex;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 14px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }}
    .card-title {{
      font-size: 0.75rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }}
    .grid-4 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }}
    button.btn {{
      background: #1b273d;
      border: 1px solid #283955;
      color: var(--text);
      padding: 13px 8px;
      border-radius: 10px;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 4px;
      transition: transform 0.1s, background 0.15s;
      user-select: none;
    }}
    button.btn:active {{
      transform: scale(0.93);
      background: var(--accent);
      border-color: var(--accent);
    }}
    .btn span.icon {{
      font-size: 1.3rem;
    }}
    .btn-danger {{
      background: rgba(239, 68, 68, 0.15);
      border-color: rgba(239, 68, 68, 0.3);
      color: #fca5a5;
    }}
    .btn-danger:active {{
      background: var(--danger);
      color: #fff;
    }}
    .btn-warning {{
      background: rgba(245, 158, 11, 0.15);
      border-color: rgba(245, 158, 11, 0.3);
      color: #fde68a;
    }}
    .btn-warning:active {{
      background: var(--warning);
      color: #000;
    }}
    .touchpad {{
      height: 200px;
      background: #0d1524;
      border: 2px dashed #24344d;
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      color: #475569;
      font-size: 0.9rem;
      font-weight: 600;
      touch-action: none;
      position: relative;
      cursor: crosshair;
      user-select: none;
    }}
    .touchpad.active {{
      border-color: var(--accent);
      background: #0f192c;
    }}
    .touchpad-buttons {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
      margin-top: 8px;
    }}
    .touchpad-btn {{
      height: 50px;
      font-size: 0.9rem;
      font-weight: 700;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 10px;
      color: #fff;
      cursor: pointer;
      user-select: none;
    }}
    .touchpad-btn:active {{
      transform: scale(0.95);
      background: var(--accent);
    }}
    .speech-box {{
      display: flex;
      gap: 6px;
    }}
    .input-bar {{
      flex: 1;
      background: #0b1120;
      border: 1px solid var(--card-border);
      color: #fff;
      padding: 11px 13px;
      border-radius: 10px;
      font-size: 0.88rem;
      outline: none;
    }}
    .input-bar:focus {{
      border-color: var(--accent);
    }}
    .mic-btn {{
      background: #1e293b;
      border: 1px solid #334155;
      color: #fff;
      padding: 0 14px;
      border-radius: 10px;
      font-size: 1.2rem;
      cursor: pointer;
    }}
    .mic-btn.listening {{
      background: var(--danger);
      animation: pulse 1s infinite;
    }}
    @keyframes pulse {{
      0% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }}
      70% {{ box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
    }}
    .chips-bar {{
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-top: 8px;
      padding-bottom: 2px;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
    }}
    .chips-bar::-webkit-scrollbar {{
      display: none;
    }}
    .chip {{
      background: #192338;
      border: 1px solid #283a59;
      color: #94a3b8;
      padding: 6px 11px;
      border-radius: 18px;
      font-size: 0.76rem;
      font-weight: 600;
      white-space: nowrap;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      user-select: none;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
    }}
    .chip:active {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }}
    .log-box {{
      background: #070b14;
      border: 1px solid #162032;
      border-radius: 10px;
      padding: 8px 10px;
      font-family: monospace;
      font-size: 0.75rem;
      color: #38bdf8;
      max-height: 85px;
      overflow-y: auto;
    }}
    .log-entry {{
      margin-bottom: 2px;
    }}
    .app-pill {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #0d1524;
      border: 1px solid #1f2d47;
      padding: 9px 12px;
      border-radius: 8px;
      font-size: 0.85rem;
    }}
    .app-pill-kill {{
      background: #ef4444;
      color: #fff;
      border: none;
      border-radius: 6px;
      padding: 4px 10px;
      font-size: 0.75rem;
      font-weight: 700;
      cursor: pointer;
    }}
    .wa-btn {{
      background: linear-gradient(135deg, #25d366 0%, #128c7e 100%);
      color: #ffffff;
      font-weight: 800;
      border: 1px solid #25d366;
      border-radius: 10px;
      padding: 12px 16px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 4px 14px rgba(37, 211, 102, 0.35);
      transition: all 0.2s;
    }}
    .wa-btn:active {{
      transform: scale(0.98);
      filter: brightness(0.9);
    }}
    .contact-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #0b1120;
      border: 1px solid #1e293b;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 0.82rem;
    }}
  </style>
</head>
<body>

<div id="toast" class="toast">Action Executed</div>

<div class="container">
  <header>
    <div class="logo-box">
      <h1>🎮 Master PC Controller</h1>
      {ts_info}
    </div>
    <div id="statusBadge" class="status-badge disconnected" onclick="reconnectNow()" title="Tap to reconnect">
      <span class="dot"></span>
      <span id="statusText">Connecting...</span>
    </div>
  </header>

  <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid #10b981; border-radius: 8px; padding: 7px 10px; font-size: 0.76rem; display: flex; align-items: center; justify-content: space-between;">
    <span>🔔 <b>Auto-Alert:</b> PC on hote hi phone par notification paane k liye:</span>
    <a href="https://notify.run/c/Xr8sUVetppo2cKoSrqTN" target="_blank" class="btn" style="background:#10b981; border:none; padding:4px 10px; font-size:0.75rem; text-decoration:none; color:#fff; font-weight:700;">Subscribe</a>
  </div>

  <!-- AI Voice & Command Bar -->
  <div class="card" style="padding: 10px;">
    <div id="httpsBanner" style="display:none; background: rgba(99, 102, 241, 0.15); border: 1px solid #4f46e5; border-radius: 8px; padding: 8px 10px; margin-bottom: 8px; font-size: 0.78rem; align-items: center; justify-content: space-between;">
      <span>🔒 Mic chalane k liye HTTPS par switch karein:</span>
      <button class="btn" style="background:#4f46e5; border-color:#6366f1; padding:4px 10px; font-size:0.75rem;" onclick="switchToHttps()">Switch to HTTPS</button>
    </div>
    <div class="speech-box">
      <input type="text" id="cmdInput" class="input-bar" placeholder="Bolye ya likhein: 'open chat gpt' ya 'ali ki chat kholo'...">
      <button id="langToggleBtn" class="btn" style="padding:0 8px; font-size:0.75rem; background:#1e293b; border-color:#334155; font-weight:800; color:#4ade80;" onclick="toggleVoiceLang()" title="Toggle Urdu / English Mic">🌐 UR</button>
      <button id="micBtn" class="mic-btn" onclick="toggleVoiceRecognition()" title="Voice Command">🎤</button>
      <button class="btn" style="background:#7c3aed; border-color:#8b5cf6; padding:0 10px; font-weight:700; white-space:nowrap; font-size:0.76rem;" onclick="startWebVoiceRecord()" title="Record real voice note and send to PC">🎙️ Voice Note</button>
      <button class="btn" style="background: var(--accent); border-color: var(--accent); padding: 0 14px;" onclick="sendTextCommand()">Send</button>
    </div>
    <div class="chips-bar">
      <button class="chip" style="border-color:#a855f7; color:#c084fc; font-weight:700;" onclick="startWebVoiceRecord()">🎙️ Record Voice Note</button>
      <button class="chip" style="border-color:#10b981; color:#34d399;" onclick="quickVoice('open chat gpt')">🤖 ChatGPT</button>
      <button class="chip" onclick="quickVoice('open youtube')">▶️ YouTube</button>
      <button class="chip" onclick="quickVoice('open my number chat')">💬 My Chat</button>
      <button class="chip" onclick="quickVoice('open youtube and play songs')">🎵 Play Songs</button>
      <button class="chip" style="border-color:#25d366; color:#4ade80;" onclick="switchTab('whatsapp')">💬 WhatsApp Hub</button>
      <button class="chip" onclick="quickVoice('volume up')">🔊 Vol +</button>
      <button class="chip" onclick="quickVoice('volume down')">🔉 Vol -</button>
      <button class="chip" onclick="quickVoice('volume mute')">🔇 Mute</button>
      <button class="chip" onclick="quickVoice('open chrome')">🌐 Chrome</button>
      <button class="chip" onclick="quickVoice('close')">❌ Close App</button>
    </div>
  </div>

  <!-- Mic Permission Helper Modal for Android Chrome HTTP -->
  <div id="micHelpModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:99999; align-items:center; justify-content:center; padding:16px; box-sizing:border-box;">
    <div style="background:#131c2e; border:1px solid #3b82f6; border-radius:14px; max-width:440px; width:100%; padding:18px; color:#f8fafc; font-size:0.86rem; box-shadow:0 8px 32px rgba(0,0,0,0.6);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <h3 style="margin:0; font-size:1.05rem; color:#60a5fa; display:flex; align-items:center; gap:8px;">
          <span>🎙️</span> Android Mic Enable (1-Time Setup)
        </h3>
        <button onclick="closeMicHelp()" style="background:none; border:none; color:#94a3b8; font-size:1.4rem; cursor:pointer;">&times;</button>
      </div>
      <p style="margin:0 0 10px 0; line-height:1.4; color:#cbd5e1; font-size:0.82rem;">
        Android Chrome policy ke tehat HTTP connections par microphone by-default block hota hai. Isko 10 seconds me allow karein:
      </p>
      <div style="background:#0b1120; border-radius:8px; padding:10px; margin-bottom:10px; font-size:0.8rem; line-height:1.5;">
        <b>1.</b> Naya Chrome Tab kholein aur ye paste karein:<br>
        <code style="color:#38bdf8; word-break:break-all;">chrome://flags/#unsafely-treat-insecure-origin-as-secure</code>
        <div style="margin-top:6px;">
          <button class="btn" style="padding:5px 12px; font-size:0.75rem; background:#1e293b;" onclick="copyText('chrome://flags/#unsafely-treat-insecure-origin-as-secure', 'Flag URL Copied!')">📋 Copy Flag URL</button>
        </div>
      </div>
      <div style="background:#0b1120; border-radius:8px; padding:10px; margin-bottom:10px; font-size:0.8rem; line-height:1.5;">
        <b>2.</b> Is box me ye address paste karein aur <b>Enabled</b> select karein:<br>
        <code style="color:#4ade80; word-break:break-all;">{server_http_origin}</code>
        <div style="margin-top:6px;">
          <button class="btn" style="padding:5px 12px; font-size:0.75rem; background:#1e293b;" onclick="copyText('{server_http_origin}', 'Server URL Copied!')">📋 Copy Server Address</button>
        </div>
      </div>
      <p style="margin:0 0 14px 0; font-size:0.75rem; color:#94a3b8;">
        <b>3.</b> Neeche <b>Relaunch</b> button dabayein. Mic aur Voice control permanently chal jayega!
      </p>
      <div style="display:flex; gap:8px;">
        <button class="btn" style="flex:1; background:#1e293b; border-color:#334155; padding:9px;" onclick="closeMicHelp()">Band Karein</button>
        <button class="btn" style="flex:1; background:var(--accent); border-color:var(--accent); padding:9px; font-weight:700;" onclick="closeMicHelp()">Theek Hai (Got it)</button>
      </div>
    </div>
  </div>

  <!-- Navigation Tabs -->
  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('quick', this)">⚡ Quick</button>
    <button class="tab-btn" onclick="switchTab('screen', this)">📺 Screen</button>
    <button class="tab-btn" onclick="switchTab('media', this)">🎬 Media</button>
    <button class="tab-btn" onclick="switchTab('presentation', this)">📊 Slides</button>
    <button class="tab-btn" onclick="switchTab('files', this)">📁 Files</button>
    <button class="tab-btn" style="border-color: rgba(37, 211, 102, 0.4); color: #4ade80;" onclick="switchTab('whatsapp', this)">💬 WhatsApp</button>
    <button class="tab-btn" onclick="switchTab('apps', this)">🚀 Apps & Web</button>
    <button class="tab-btn" onclick="switchTab('running', this)">❌ Close Apps</button>
    <button class="tab-btn" onclick="switchTab('keyboard', this)">⌨️ Typing</button>
    <button class="tab-btn" onclick="switchTab('mouse', this)">🖱️ Mouse</button>
  </div>

  <!-- TAB WA: WHATSAPP DIRECT CHAT & SENDER -->
  <div id="tab-whatsapp" class="tab-content">
    <!-- Send Message Card -->
    <div class="card" style="border-color: rgba(37, 211, 102, 0.35);">
      <div class="card-title" style="color: #4ade80;">
        <span>💬 Direct WhatsApp Message Sender</span>
      </div>
      <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 10px; line-height: 1.4;">
        Number ya saved contact name likhein aur message type karein. PC par WhatsApp chat khud khulegi aur message dispatch hoga!
      </div>
      
      <div style="margin-bottom: 8px;">
        <label style="font-size:0.75rem; color:#94a3b8; display:block; margin-bottom:3px;">Recipient (Phone number ya Saved Name):</label>
        <div style="display:flex; gap:6px;">
          <input type="text" id="waRecipient" class="input-bar" placeholder="e.g. 03001234567 ya ali, abu, my number...">
          <button class="btn" style="background:#1e293b; border-color:#334155; padding:0 12px; font-size:0.78rem; white-space:nowrap;" onclick="openWhatsAppChatDirect()">📂 Open Chat</button>
        </div>
      </div>
      
      <div style="margin-bottom: 10px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
          <label style="font-size:0.75rem; color:#94a3b8;">Message to send:</label>
          <button class="btn" id="waDictateBtn" style="padding:2px 8px; font-size:0.72rem; background:#1e293b; border-color:#25d366; color:#4ade80;" onclick="dictateWhatsAppMessage()">🎤 Bol Kar Likhein</button>
        </div>
        <textarea id="waMessage" class="input-bar" style="height: 68px; resize: vertical;" placeholder="Apna exact message yahan type karein ya mic se bolein..."></textarea>
      </div>

      <div class="chips-bar" style="padding-top:0; margin-bottom:10px;">
        <button class="chip" onclick="fillWaQuickMsg('Assalam o Alaikum! Kese hain?')">👋 Assalam o Alaikum</button>
        <button class="chip" onclick="fillWaQuickMsg('Main raste me hun, thori dair me pohonch raha hun.')">🚗 Raste me hun</button>
        <button class="chip" onclick="fillWaQuickMsg('Urgently call me please!')">📞 Call me</button>
        <button class="chip" onclick="fillWaQuickMsg('Kaam ho gaya hai, verify karlein.')">✅ Kaam done</button>
      </div>

      <button class="wa-btn" style="width: 100%;" onclick="sendWhatsAppDirect()">
        <span>🚀 Send via WhatsApp (Auto Types & Dispatches)</span>
      </button>
    </div>

    <!-- Saved Contacts Address Book Card -->
    <div class="card">
      <div class="card-title">
        <span>📇 Saved Contacts Phonebook</span>
        <button style="background: transparent; border: 1px solid #25d366; color: #4ade80; border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; cursor: pointer;" onclick="loadContacts()">🔄 Refresh</button>
      </div>
      <div style="display:flex; gap:6px; margin-bottom:8px;">
        <button class="chip" style="border-color:#38bdf8; color:#38bdf8;" onclick="setupMyNumberUI()">📱 Set 'My Number'</button>
      </div>
      <div style="display: flex; gap: 6px; margin-bottom: 10px;">
        <input type="text" id="saveContactName" class="input-bar" style="flex:1;" placeholder="Name (e.g. ali)">
        <input type="text" id="saveContactPhone" class="input-bar" style="flex:1.4;" placeholder="Phone (03001234567)">
        <button class="btn" style="background:#059669; border-color:#10b981; padding:0 12px; font-weight:700;" onclick="saveContactUI()">Save</button>
      </div>
      <div id="contactsList" style="display: flex; flex-direction: column; gap: 6px;">
        <div style="color: #64748b; font-size: 0.8rem; text-align: center; padding: 10px;">Loading contacts...</div>
      </div>
    </div>
  </div>

  <!-- TAB 1: QUICK CONTROLS -->
  <div id="tab-quick" class="tab-content active">
    <!-- Quick Ping / Connection Test -->
    <div class="card" style="padding: 12px; display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg, #1e1b4b 0%, #1e293b 100%); border-color: #4338ca;">
      <div>
        <div style="font-size: 0.9rem; font-weight: 800; color: #c7d2fe;">🔔 Test PC Connection</div>
        <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">Tap to ring chime on PC & verify response</div>
      </div>
      <button class="btn" style="background: #4f46e5; border-color: #6366f1; padding: 10px 18px; flex-direction: row; gap: 6px; box-shadow: 0 4px 12px rgba(99,102,241,0.4);" onclick="sendAction('beep')">
        <span class="icon" style="font-size: 1.2rem;">🔔</span>
        <span style="font-weight: 700;">Ping PC</span>
      </button>
    </div>

    <!-- Volume Controls -->
    <div class="card">
      <div class="card-title"><span>🔊 Master Hardware Volume</span></div>
      <div class="grid-3">
        <button class="btn" onclick="sendAction('volume_down')">
          <span class="icon">🔉</span>
          <span>Vol -10%</span>
        </button>
        <button class="btn" onclick="sendAction('volume_mute')">
          <span class="icon">🔇</span>
          <span>Mute</span>
        </button>
        <button class="btn" onclick="sendAction('volume_up')">
          <span class="icon">🔊</span>
          <span>Vol +10%</span>
        </button>
      </div>
    </div>

    <!-- Media Controls -->
    <div class="card">
      <div class="card-title"><span>🎵 Media Controls</span></div>
      <div class="grid-3">
        <button class="btn" onclick="sendAction('media_prev')">
          <span class="icon">⏮️</span>
          <span>Previous</span>
        </button>
        <button class="btn" onclick="sendAction('media_play_pause')">
          <span class="icon">⏯️</span>
          <span>Play / Pause</span>
        </button>
        <button class="btn" onclick="sendAction('media_next')">
          <span class="icon">⏭️</span>
          <span>Next</span>
        </button>
      </div>
    </div>

    <!-- Windows Navigation Controls -->
    <div class="card">
      <div class="card-title"><span>⚙️ Windows Shortcuts</span></div>
      <div class="grid-4">
        <button class="btn" onclick="sendAction('show_desktop')">
          <span class="icon">🖥️</span>
          <span>Desktop</span>
        </button>
        <button class="btn" onclick="sendAction('alt_tab')">
          <span class="icon">🔄</span>
          <span>Alt+Tab</span>
        </button>
        <button class="btn" onclick="sendAction('hotkey', {{ hotkey: 'fullscreen' }})">
          <span class="icon">⛶</span>
          <span>Fullscreen</span>
        </button>
        <button class="btn btn-danger" onclick="sendAction('close_window')">
          <span class="icon">❌</span>
          <span>Close App</span>
        </button>
      </div>
    </div>

    <!-- 1-Tap Quick Macros -->
    <div class="card">
      <div class="card-title"><span>⚡ 1-Tap Quick Workflows</span></div>
      <div class="grid-2">
        <button class="btn" style="border-color:#38bdf8;" onclick="sendAction('run_macro', {{ macro: 'work' }})">
          <span class="icon">💼</span>
          <span style="font-weight:700;">Work Mode</span>
          <span style="font-size:0.68rem; color:#94a3b8;">VS Code + Chrome</span>
        </button>
        <button class="btn" style="border-color:#f59e0b;" onclick="sendAction('run_macro', {{ macro: 'gaming' }})">
          <span class="icon">🎮</span>
          <span style="font-weight:700;">Gaming Mode</span>
          <span style="font-size:0.68rem; color:#94a3b8;">Boost Vol + YouTube</span>
        </button>
        <button class="btn" style="border-color:#10b981;" onclick="sendAction('run_macro', {{ macro: 'study' }})">
          <span class="icon">📚</span>
          <span style="font-weight:700;">Study Mode</span>
          <span style="font-size:0.68rem; color:#94a3b8;">ChatGPT + Docs</span>
        </button>
        <button class="btn" style="border-color:#a855f7;" onclick="sendAction('run_macro', {{ macro: 'chill' }})">
          <span class="icon">🛋️</span>
          <span style="font-weight:700;">Chill Mode</span>
          <span style="font-size:0.68rem; color:#94a3b8;">Netflix + Fullscreen</span>
        </button>
      </div>
    </div>

    <!-- Wake-on-LAN Info Card -->
    <div class="card" style="border-color: rgba(99, 102, 241, 0.4);">
      <div class="card-title"><span>🔌 Wake-on-LAN Remote Power-ON</span></div>
      <div style="font-size:0.75rem; color:#94a3b8; line-height:1.4; margin-bottom:8px;">
        PC shutdown hone par magic packet bhej kar on karne k liye MAC Address:
      </div>
      <div id="wolInfoBox" style="background:#0b1120; border:1px solid #1e293b; border-radius:8px; padding:8px 10px; font-family:monospace; font-size:0.75rem; color:#818cf8; margin-bottom:8px;">
        Loading MAC...
      </div>
      <button class="btn" style="width:100%; background:#1e293b; border-color:#4f46e5; color:#c7d2fe; padding:8px;" onclick="loadWolInfoWeb()">
        🔄 Refresh Network MAC Addresses
      </button>
    </div>
  </div>

  <!-- TAB: SCREEN MIRROR & SCREENSHOT -->
  <div id="tab-screen" class="tab-content">
    <div class="card">
      <div class="card-title">
        <span>📺 Live PC Screen Stream</span>
        <button id="streamToggleBtn" class="btn" style="padding:4px 10px; font-size:0.75rem; background:#4f46e5; border-color:#6366f1;" onclick="toggleScreenStreamWeb()">▶️ Start Stream</button>
      </div>
      <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:10px;">
        Low-latency live video stream of your Windows desktop directly in your phone browser.
      </div>
      <div id="screenStreamContainer" style="width:100%; min-height:180px; background:#0b1120; border:1px solid #1e293b; border-radius:10px; display:flex; align-items:center; justify-content:center; overflow:hidden;">
        <span id="screenPlaceholder" style="color:#64748b; font-size:0.8rem;">Tap 'Start Stream' to mirror PC screen</span>
        <img id="screenStreamImg" style="width:100%; display:none; border-radius:10px;" alt="Live PC Screen" />
      </div>
    </div>

    <div class="card">
      <div class="card-title">
        <span>📸 Instant PC Screenshot</span>
      </div>
      <div style="display:flex; gap:8px; margin-bottom:10px;">
        <button class="btn" style="flex:1; background:var(--accent); border-color:var(--accent); padding:10px;" onclick="takeScreenshotWeb()">
          📸 Capture Screenshot Now
        </button>
        <a id="downloadScreenshotBtn" class="btn" style="display:none; padding:10px; text-decoration:none; background:#059669; border-color:#10b981;" download="pc_screenshot.jpg">
          💾 Download
        </a>
      </div>
      <div id="screenshotPreviewContainer" style="width:100%; min-height:140px; background:#0b1120; border:1px solid #1e293b; border-radius:10px; display:flex; align-items:center; justify-content:center; overflow:hidden;">
        <span id="screenshotPlaceholder" style="color:#64748b; font-size:0.8rem;">No screenshot captured yet</span>
        <img id="screenshotImg" style="width:100%; display:none; border-radius:10px;" alt="PC Screenshot" />
      </div>
    </div>
  </div>

  <!-- TAB: YOUTUBE & NETFLIX MEDIA REMOTE -->
  <div id="tab-media" class="tab-content">
    <div class="card" style="border-color: rgba(239, 68, 68, 0.4);">
      <div class="card-title" style="color:#f87171;">
        <span>🎬 Smart YouTube & Netflix Remote</span>
      </div>
      <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:12px;">
        10s Seek, Subtitles, Playback speed & Fullscreen shortcuts tailored for browser media.
      </div>
      
      <!-- Big Play / Pause -->
      <button class="btn" style="width:100%; padding:20px; font-size:1.1rem; font-weight:800; background:linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); border-color:#6366f1; margin-bottom:10px;" onclick="sendAction('media_play_pause')">
        <span class="icon" style="font-size:1.8rem;">⏯️</span>
        <span>Play / Pause</span>
      </button>

      <!-- 10s Seek Controls -->
      <div class="grid-2" style="margin-bottom:10px;">
        <button class="btn" style="padding:16px; background:#1e293b; border-color:#334155;" onclick="sendAction('media_seek', {{ direction: 'backward', seconds: 10 }})">
          <span class="icon" style="font-size:1.5rem;">⏪</span>
          <span style="font-weight:700;">10s Peeche (J)</span>
        </button>
        <button class="btn" style="padding:16px; background:#1e293b; border-color:#334155;" onclick="sendAction('media_seek', {{ direction: 'forward', seconds: 10 }})">
          <span class="icon" style="font-size:1.5rem;">⏩</span>
          <span style="font-weight:700;">10s Aage (L)</span>
        </button>
      </div>

      <!-- Video Enhancements Grid -->
      <div class="grid-4" style="margin-bottom:10px;">
        <button class="btn" onclick="sendAction('media_fullscreen')">
          <span class="icon">⛶</span>
          <span>Fullscreen (F)</span>
        </button>
        <button class="btn" onclick="sendAction('media_subtitles')">
          <span class="icon">💬</span>
          <span>Subtitles (C)</span>
        </button>
        <button class="btn" onclick="sendAction('media_speed', {{ direction: 'decrease' }})">
          <span class="icon">🐢</span>
          <span>Speed &lt;</span>
        </button>
        <button class="btn" onclick="sendAction('media_speed', {{ direction: 'increase' }})">
          <span class="icon">⚡</span>
          <span>Speed &gt;</span>
        </button>
      </div>

      <!-- Tracks & Volume -->
      <div class="grid-3">
        <button class="btn" onclick="sendAction('media_prev')">
          <span class="icon">⏮️</span>
          <span>Prev Track</span>
        </button>
        <button class="btn" onclick="sendAction('volume_mute')">
          <span class="icon">🔇</span>
          <span>Mute</span>
        </button>
        <button class="btn" onclick="sendAction('media_next')">
          <span class="icon">⏭️</span>
          <span>Next Track</span>
        </button>
      </div>
    </div>
  </div>

  <!-- TAB: PRESENTATION SLIDE CLICKER -->
  <div id="tab-presentation" class="tab-content">
    <div class="card" style="border-color: rgba(245, 158, 11, 0.4);">
      <div class="card-title" style="color:#fbbf24;">
        <span>📊 PowerPoint & PDF Slide Clicker</span>
      </div>
      <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:14px;">
        PowerPoint, Google Slides ya PDF presentations k liye dedicated remote clicker.
      </div>

      <!-- Huge Prev / Next Buttons -->
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:14px;">
        <button class="btn" style="padding:32px 12px; background:#1e293b; border:2px solid #334155; font-size:1rem; font-weight:800;" onclick="sendAction('presentation_prev')">
          <span class="icon" style="font-size:2.2rem; margin-bottom:6px;">⏮️</span>
          <span>PREVIOUS</span>
          <span style="font-size:0.7rem; color:#94a3b8;">Page Up</span>
        </button>
        <button class="btn" style="padding:32px 12px; background:linear-gradient(135deg, #d97706 0%, #b45309 100%); border:2px solid #f59e0b; font-size:1rem; font-weight:800; color:#fff;" onclick="sendAction('presentation_next')">
          <span class="icon" style="font-size:2.2rem; margin-bottom:6px;">⏭️</span>
          <span>NEXT</span>
          <span style="font-size:0.7rem; color:#fef3c7;">Page Down</span>
        </button>
      </div>

      <!-- Slide Show Controls -->
      <div class="grid-3">
        <button class="btn" style="background:#065f46; border-color:#059669; color:#a7f3d0;" onclick="sendAction('presentation_start')">
          <span class="icon">▶️</span>
          <span style="font-weight:700;">Start (F5)</span>
        </button>
        <button class="btn" style="background:#1e1b4b; border-color:#4338ca; color:#c7d2fe;" onclick="sendAction('presentation_black')">
          <span class="icon">⬛</span>
          <span style="font-weight:700;">Black (B)</span>
        </button>
        <button class="btn btn-danger" onclick="sendAction('presentation_exit')">
          <span class="icon">⏹️</span>
          <span style="font-weight:700;">Exit (Esc)</span>
        </button>
      </div>
    </div>
  </div>

  <!-- TAB: FILES & UNIVERSAL CLIPBOARD -->
  <div id="tab-files" class="tab-content">
    <!-- Voice Note Recorder Card -->
    <div class="card" style="border-color: rgba(168, 85, 247, 0.4); background: linear-gradient(135deg, #1e1b4b 0%, #131c2e 100%);">
      <div class="card-title" style="color: #c084fc;">
        <span>🎙️ Live Voice Note Sender</span>
      </div>
      <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:12px;">
        Mobile mic se bolein. Stop dabate hi PC par voice note receive hoga aur PC speakers par foran play ho jayega.
      </div>
      <div id="voiceRecordControls" style="display:flex; flex-direction:column; gap:8px;">
        <button id="startVoiceRecBtn" class="btn" style="background:#7c3aed; border-color:#8b5cf6; padding:14px; font-weight:700;" onclick="startWebVoiceRecord()">
          🎤 Tap to Record Voice Note
        </button>
        <div id="recordingActiveBox" style="display:none; background:rgba(239, 68, 68, 0.2); border:1.5px solid #ef4444; border-radius:10px; padding:12px; align-items:center; justify-content:space-between;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#ef4444; box-shadow:0 0 8px #ef4444;"></span>
            <span id="recTimerText" style="font-weight:800; color:#fca5a5; font-size:0.9rem;">RECORDING: 00:00</span>
          </div>
          <button class="btn" style="background:#10b981; border:none; padding:8px 14px; font-weight:700;" onclick="stopAndSendWebVoice()">
            Stop & Send 🚀
          </button>
        </div>
      </div>
    </div>

    <!-- File Drop to PC -->
    <div class="card" style="border-color: rgba(59, 130, 246, 0.4);">
      <div class="card-title" style="color:#60a5fa;">
        <span>📁 Wireless Phone-to-PC File Drop</span>
      </div>
      <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:10px;">
        Phone se koi bhi file choose karein, PC k <code>Downloads/PC_Controller_Received/</code> folder me receive hogi.
      </div>
      <div style="display:flex; flex-direction:column; gap:8px;">
        <input type="file" id="webFileInput" class="input-bar" style="padding:8px;" />
        <button class="btn" style="background:#2563eb; border-color:#3b82f6; font-weight:700; padding:12px;" onclick="uploadFileWeb()">
          📤 Upload Selected File to PC
        </button>
      </div>
    </div>

    <!-- Received Files on PC -->
    <div class="card">
      <div class="card-title">
        <span>📥 Files on PC (Received Folder)</span>
        <button style="background:transparent; border:1px solid #3b82f6; color:#60a5fa; border-radius:6px; padding:2px 8px; font-size:0.72rem; cursor:pointer;" onclick="loadPCFilesWeb()">🔄 Refresh</button>
      </div>
      <div id="pcFilesList" style="display:flex; flex-direction:column; gap:6px;">
        <div style="color:#64748b; font-size:0.8rem; text-align:center; padding:10px;">Tap Refresh to view received files</div>
      </div>
    </div>

    <!-- Universal Shared Clipboard -->
    <div class="card" style="border-color: rgba(168, 85, 247, 0.4);">
      <div class="card-title" style="color:#c084fc;">
        <span>📋 Universal Phone ⇄ PC Clipboard</span>
      </div>
      <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:8px;">
        Phone se text PC ke clipboard me bhejein ya PC ka copied text yahan mangwayen:
      </div>
      <textarea id="webClipboardText" class="input-bar" style="height:76px; resize:vertical; margin-bottom:8px;" placeholder="PC clipboard text yahan aayega ya type karke Send dabayein..."></textarea>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
        <button class="btn" style="background:#1e293b; border-color:#64748b; font-weight:700;" onclick="fetchClipboardWeb()">
          📥 Fetch PC Clipboard
        </button>
        <button class="btn" style="background:#7c3aed; border-color:#8b5cf6; font-weight:700;" onclick="sendClipboardWeb()">
          📤 Send to PC Clipboard
        </button>
      </div>
    </div>
  </div>

  <!-- TAB 2: APPS & WEB LAUNCHER HUB -->
  <div id="tab-apps" class="tab-content">
    <!-- Open ANY Website URL -->
    <div class="card">
      <div class="card-title"><span>🌐 Open Any Website</span></div>
      <div style="display: flex; gap: 6px;">
        <input type="text" id="urlInput" class="input-bar" placeholder="e.g. youtube.com, chatgpt.com, github.com">
        <button class="btn" style="background: var(--accent); padding: 0 16px;" onclick="openCustomUrl()">Open</button>
      </div>
      <div class="grid-4" style="margin-top: 10px;">
        <button class="btn" onclick="sendAction('open_youtube')"><span class="icon">▶️</span><span>YouTube</span></button>
        <button class="btn" onclick="sendAction('open_browser')"><span class="icon">🌐</span><span>Google</span></button>
        <button class="btn" onclick="sendAction('open_whatsapp')"><span class="icon">💬</span><span>WhatsApp</span></button>
        <button class="btn" onclick="sendAction('open_chatgpt')"><span class="icon">🤖</span><span>ChatGPT</span></button>
      </div>
    </div>

    <!-- Open ANY Windows Program -->
    <div class="card">
      <div class="card-title"><span>🚀 Launch Windows Programs</span></div>
      <div style="display: flex; gap: 6px; margin-bottom: 10px;">
        <input type="text" id="progInput" class="input-bar" placeholder="e.g. vlc, winword, excel, mspaint, cmd">
        <button class="btn" style="background: var(--accent); padding: 0 16px;" onclick="runCustomProgram()">Run</button>
      </div>
      <div class="grid-3">
        <button class="btn" onclick="sendAction('open_notepad')"><span class="icon">📝</span><span>Notepad</span></button>
        <button class="btn" onclick="sendAction('open_calc')"><span class="icon">🧮</span><span>Calculator</span></button>
        <button class="btn" onclick="sendAction('open_explorer')"><span class="icon">📁</span><span>Explorer</span></button>
        <button class="btn" onclick="sendAction('open_terminal')"><span class="icon">💻</span><span>CMD</span></button>
        <button class="btn" onclick="sendAction('open_powershell')"><span class="icon">⚡</span><span>PowerShell</span></button>
        <button class="btn" onclick="sendAction('open_taskmgr')"><span class="icon">📊</span><span>Task Mgr</span></button>
        <button class="btn" onclick="sendAction('open_paint')"><span class="icon">🎨</span><span>Paint</span></button>
        <button class="btn" onclick="sendAction('open_settings')"><span class="icon">⚙️</span><span>Settings</span></button>
        <button class="btn" onclick="sendAction('open_control')"><span class="icon">🎛️</span><span>Control Pnl</span></button>
        <button class="btn" onclick="sendAction('open_downloads')"><span class="icon">📥</span><span>Downloads</span></button>
        <button class="btn" onclick="sendAction('open_documents')"><span class="icon">📄</span><span>Documents</span></button>
        <button class="btn" onclick="sendAction('open_gmail')"><span class="icon">📧</span><span>Gmail</span></button>
      </div>
    </div>
  </div>

  <!-- TAB 3: APP MANAGER & PROCESS KILLER -->
  <div id="tab-running" class="tab-content">
    <div class="card">
      <div class="card-title"><span>❌ Close Any App by Name</span></div>
      <div style="display: flex; gap: 6px;">
        <input type="text" id="killAppInput" class="input-bar" placeholder="e.g. chrome, notepad, vlc, calc">
        <button class="btn btn-danger" style="padding: 0 16px;" onclick="closeCustomApp()">Close</button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">
        <span>Active User Applications</span>
        <button style="background: transparent; border: 1px solid var(--accent); color: var(--accent); border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; cursor: pointer;" onclick="loadRunningApps()">🔄 Refresh</button>
      </div>
      <div id="runningAppsList" style="display: flex; flex-direction: column; gap: 6px;">
        <div style="color: #64748b; font-size: 0.8rem; text-align: center; padding: 10px;">Loading running apps...</div>
      </div>
    </div>
  </div>

  <!-- TAB 4: REMOTE KEYBOARD & TYPING -->
  <div id="tab-keyboard" class="tab-content">
    <div class="card">
      <div class="card-title">
        <span>⚡ Real-Time Live Typing</span>
        <span style="color: #10b981; font-size: 0.72rem; font-weight: bold;">● Live Active</span>
      </div>
      <div style="display: flex; gap: 6px; margin-bottom: 8px;">
        <input type="text" id="typeInput" class="input-bar" placeholder="Yahan live type karein (Direct PC par show hoga)...">
        <button class="btn" style="background: #334155; padding: 0 12px;" onclick="clearLiveTypeInput()">Clear</button>
        <button class="btn" style="background: #059669; border-color: #10b981; padding: 0 12px;" onclick="sendTypeInNotepad()">In Notepad</button>
      </div>
      <div style="font-size: 0.74rem; color: #94a3b8; margin-bottom: 12px; line-height: 1.5;">
        🟢 <b>Live Keystrokes:</b> Mobile par jo bhi character ya word type karenge ya delete karenge, wo foran PC active window par live type hoga.
      </div>

      <div class="card-title"><span>Special Keys</span></div>
      <div class="grid-4">
        <button class="btn" onclick="sendKey('enter')">Enter ⏎</button>
        <button class="btn" onclick="sendKey('backspace')">⌫ Back</button>
        <button class="btn" onclick="sendKey('space')">Space</button>
        <button class="btn" onclick="sendKey('escape')">Esc</button>
      </div>
      <div class="grid-4" style="margin-top: 8px;">
        <button class="btn" onclick="sendKey('tab')">Tab</button>
        <button class="btn" onclick="sendKey('up')">⬆️ Up</button>
        <button class="btn" onclick="sendKey('down')">⬇️ Down</button>
        <button class="btn" onclick="sendKey('right')">➡️ Right</button>
      </div>

      <div class="card-title" style="margin-top: 14px;"><span>Edit Hotkeys</span></div>
      <div class="grid-4">
        <button class="btn" onclick="sendHotkey('copy')">Copy</button>
        <button class="btn" onclick="sendHotkey('paste')">Paste</button>
        <button class="btn" onclick="sendHotkey('select_all')">Select All</button>
        <button class="btn" onclick="sendHotkey('undo')">Undo</button>
      </div>
    </div>
  </div>

  <!-- TAB 5: VIRTUAL MOUSE & SYSTEM POWER -->
  <div id="tab-mouse" class="tab-content">
    <div class="card">
      <div class="card-title">
        <span>🖱️ Virtual Touchpad</span>
        <span style="font-size: 0.7rem; color: #64748b;">Finger drag to move mouse</span>
      </div>
      <div id="touchpad" class="touchpad">
        <span>🖱️ Touch & Drag to Move Mouse</span>
        <span style="font-size: 0.72rem; color: #64748b; margin-top: 4px;">Tap: Left Click &bull; Double Tap: Right Click</span>
      </div>
      <div class="touchpad-buttons">
        <button class="touchpad-btn" onclick="sendMouseClick('left')">Left Click</button>
      </div>
      <div class="grid-2" style="margin-top: 8px;">
        <button class="btn" onclick="sendMouseScroll(150)"><span class="icon">⬆️</span><span>Scroll Up</span></button>
        <button class="btn" onclick="sendMouseScroll(-150)"><span class="icon">⬇️</span><span>Scroll Down</span></button>
      </div>
    </div>

    <!-- Power & Session Controls -->
    <div class="card">
      <div class="card-title"><span>🔒 Session & Power Controls</span></div>
      <div class="grid-2">
        <button class="btn btn-warning" onclick="if(confirm('Lock PC screen?')) sendAction('lock_screen')">
          <span class="icon">🔒</span>
          <span>Lock PC</span>
        </button>
        <button class="btn btn-warning" onclick="if(confirm('Put PC to Sleep?')) sendAction('system_sleep')">
          <span class="icon">💤</span>
          <span>Sleep PC</span>
        </button>
      </div>
      <div class="grid-2" style="margin-top: 8px;">
        <button class="btn btn-danger" onclick="if(confirm('Restart PC in 10s?')) sendAction('system_restart')">
          <span class="icon">🔄</span>
          <span>Restart PC</span>
        </button>
        <button class="btn btn-danger" onclick="if(confirm('Shutdown PC in 15s?')) sendAction('system_shutdown')">
          <span class="icon">⏹️</span>
          <span>Shutdown PC</span>
        </button>
      </div>
      <button class="btn" style="margin-top: 8px; width: 100%; border-color: #3b82f6; color: #93c5fd;" onclick="sendAction('cancel_shutdown')">
        🛑 Cancel Pending Restart / Shutdown
      </button>
    </div>
  </div>

  <!-- Live Activity Log -->
  <div class="card" style="padding: 10px;">
    <div class="card-title" style="margin-bottom: 6px;"><span>⚡ Live Feedback</span></div>
    <div id="logBox" class="log-box">
      <div class="log-entry">Connected to PC: {local_ip}:{port}</div>
    </div>
  </div>
</div>

<script>
  let ws = null;
  const statusBadge = document.getElementById("statusBadge");
  const statusText = document.getElementById("statusText");
  const logBox = document.getElementById("logBox");
  const cmdInput = document.getElementById("cmdInput");
  const urlInput = document.getElementById("urlInput");
  const progInput = document.getElementById("progInput");
  const killAppInput = document.getElementById("killAppInput");
  const typeInput = document.getElementById("typeInput");
  const micBtn = document.getElementById("micBtn");
  const touchpad = document.getElementById("touchpad");
  const toast = document.getElementById("toast");

  function showToast(msg, isError = false) {{
    toast.textContent = msg;
    toast.style.borderColor = isError ? "var(--danger)" : "var(--success)";
    toast.classList.add("show");
    if (navigator.vibrate) navigator.vibrate(30);
    setTimeout(() => toast.classList.remove("show"), 2200);
  }}

  function log(msg) {{
    const entry = document.createElement("div");
    entry.className = "log-entry";
    const time = new Date().toLocaleTimeString();
    entry.textContent = `[${{time}}] ${{msg}}`;
    logBox.prepend(entry);
  }}

  function switchTab(tabId, el) {{
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    if (el) {{
      el.classList.add("active");
    }} else {{
      const b = document.querySelector(`[onclick*="'${{tabId}}'"]`);
      if (b) b.classList.add("active");
    }}
    const target = document.getElementById("tab-" + tabId);
    if (target) target.classList.add("active");
    if (navigator.vibrate) navigator.vibrate(15);
    if (tabId === "running") loadRunningApps();
    if (tabId === "whatsapp") loadContacts();
    if (tabId === "files") loadPCFilesWeb();
    if (tabId === "quick") loadWolInfoWeb();
    if (tabId !== "screen" && screenStreaming) toggleScreenStreamWeb();
  }}

  const urlParams = new URLSearchParams(window.location.search);
  const qToken = urlParams.get("token");
  if (qToken) {{
    localStorage.setItem("device_token", qToken);
    document.cookie = "device_token=" + qToken + "; path=/; max-age=31536000";
  }}
  const currentDeviceToken = localStorage.getItem("device_token") || "{authorized_token}";

  function authFetch(url, options = {{}}) {{
    options.headers = options.headers || {{}};
    if (currentDeviceToken) {{
      options.headers["X-Device-Token"] = currentDeviceToken;
    }}
    return fetch(url, options);
  }}

  // Screen Stream & Screenshot
  let screenStreaming = false;
  function toggleScreenStreamWeb() {{
    const img = document.getElementById("screenStreamImg");
    const placeholder = document.getElementById("screenPlaceholder");
    const btn = document.getElementById("streamToggleBtn");
    screenStreaming = !screenStreaming;
    if (screenStreaming) {{
      img.src = "/api/screen/stream?token=" + encodeURIComponent(currentDeviceToken) + "&t=" + Date.now();
      img.style.display = "block";
      if (placeholder) placeholder.style.display = "none";
      btn.textContent = "⏹️ Stop Stream";
      btn.style.background = "#dc2626";
      showToast("📺 Live Screen Stream Active");
    }} else {{
      img.src = "";
      img.style.display = "none";
      if (placeholder) placeholder.style.display = "block";
      btn.textContent = "▶️ Start Stream";
      btn.style.background = "#4f46e5";
      showToast("📺 Screen Stream Stopped");
    }}
  }}

  function takeScreenshotWeb() {{
    const img = document.getElementById("screenshotImg");
    const placeholder = document.getElementById("screenshotPlaceholder");
    const dlBtn = document.getElementById("downloadScreenshotBtn");
    showToast("📸 Capturing PC Screenshot...");
    const url = "/api/screen/screenshot?token=" + encodeURIComponent(currentDeviceToken) + "&t=" + Date.now();
    img.onload = () => {{
      img.style.display = "block";
      if (placeholder) placeholder.style.display = "none";
      if (dlBtn) {{
        dlBtn.href = url;
        dlBtn.style.display = "inline-flex";
      }}
      showToast("✅ Screenshot Captured!");
    }};
    img.src = url;
  }}

  // File Upload & List
  async function uploadFileWeb() {{
    const fileInput = document.getElementById("webFileInput");
    if (!fileInput.files || fileInput.files.length === 0) {{
      showToast("⚠️ Koi file choose karein pehle", true);
      return;
    }}
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);
    showToast("📤 Uploading: " + file.name + "...");
    try {{
      const res = await authFetch("/api/files/upload", {{
        method: "POST",
        body: formData
      }});
      const data = await res.json();
      if (data.status === "ok") {{
        showToast("✅ File saved to PC Downloads!");
        fileInput.value = "";
        loadPCFilesWeb();
      }} else {{
        showToast("❌ Upload error: " + (data.message || "Failed"), true);
      }}
    }} catch(e) {{
      showToast("❌ Network error while uploading", true);
    }}
  }}

  async function loadPCFilesWeb() {{
    const list = document.getElementById("pcFilesList");
    if (!list) return;
    list.innerHTML = '<div style="color:#64748b; font-size:0.8rem; text-align:center; padding:6px;">Loading files...</div>';
    try {{
      const res = await authFetch("/api/files/list");
      const data = await res.json();
      const files = data.files || [];
      if (files.length === 0) {{
        list.innerHTML = '<div style="color:#64748b; font-size:0.8rem; text-align:center; padding:10px;">Koi file nahi mili PC_Controller_Received folder me</div>';
        return;
      }}
      list.innerHTML = "";
      files.forEach(f => {{
        const item = document.createElement("div");
        item.style.cssText = "display:flex; justify-content:space-between; align-items:center; background:#0b1120; border:1px solid #1e293b; padding:8px 12px; border-radius:8px; font-size:0.8rem;";
        const kb = (f.size / 1024).toFixed(1);
        item.innerHTML = `<div><div style="font-weight:700; color:#f8fafc;">${{f.name}}</div><div style="font-size:0.7rem; color:#94a3b8;">${{kb}} KB</div></div><a href="/api/files/download/${{encodeURIComponent(f.name)}}?token=${{encodeURIComponent(currentDeviceToken)}}" target="_blank" style="color:#38bdf8; text-decoration:none; font-weight:700; font-size:0.75rem;">⬇️ Download</a>`;
        list.appendChild(item);
      }});
    }} catch(e) {{
      list.innerHTML = '<div style="color:#ef4444; font-size:0.8rem; text-align:center;">Failed to load files</div>';
    }}
  }}

  // Clipboard Sync
  async function fetchClipboardWeb() {{
    showToast("📥 Fetching PC Clipboard...");
    try {{
      const res = await authFetch("/api/clipboard");
      const data = await res.json();
      const text = data.text || "";
      document.getElementById("webClipboardText").value = text;
      showToast("✅ PC Clipboard Fetched!");
    }} catch(e) {{
      showToast("❌ Failed to fetch clipboard", true);
    }}
  }}

  async function sendClipboardWeb() {{
    const text = document.getElementById("webClipboardText").value;
    if (!text) {{
      showToast("⚠️ Textbox me text likhein pehle", true);
      return;
    }}
    try {{
      const res = await authFetch("/api/clipboard", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ text: text }})
      }});
      if (res.ok) {{
        showToast("✅ Sent to PC Clipboard!");
      }} else {{
        showToast("❌ Could not update PC clipboard", true);
      }}
    }} catch(e) {{
      showToast("❌ Network error", true);
    }}
  }}

  // Wake-on-LAN Info
  async function loadWolInfoWeb() {{
    const box = document.getElementById("wolInfoBox");
    if (!box) return;
    try {{
      const res = await authFetch("/api/system/wol-info");
      const data = await res.json();
      let macs = (data.mac_addresses || []).map(m => `${{m.interface}}: ${{m.mac}}`).join("<br>");
      box.innerHTML = `<b>Host:</b> ${{data.host}}<br><b>Local IP:</b> ${{data.local_ip}}<br><b>MAC:</b><br>${{macs || "None found"}}`;
    }} catch(e) {{
      box.textContent = "Error fetching MAC";
    }}
  }}

  // Web Voice Recording via MediaRecorder
  let webMediaRecorder = null;
  let voiceAudioChunks = [];
  let voiceRecTimer = null;
  let voiceSecCount = 0;

  async function startWebVoiceRecord() {{
    switchTab('files');
    try {{
      const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
      voiceAudioChunks = [];
      webMediaRecorder = new MediaRecorder(stream);
      webMediaRecorder.ondataavailable = (e) => {{
        if (e.data.size > 0) voiceAudioChunks.push(e.data);
      }};
      webMediaRecorder.start();

      document.getElementById("startVoiceRecBtn").style.display = "none";
      const activeBox = document.getElementById("recordingActiveBox");
      if (activeBox) activeBox.style.display = "flex";

      voiceSecCount = 0;
      updateRecTimer();
      voiceRecTimer = setInterval(() => {{
        voiceSecCount++;
        updateRecTimer();
      }}, 1000);
      showToast("🎙️ Recording Voice... Bolye!");
    }} catch(e) {{
      showToast("⚠️ Mic access error: " + e.message, true);
    }}
  }}

  function updateRecTimer() {{
    const m = String(Math.floor(voiceSecCount / 60)).padStart(2, '0');
    const s = String(voiceSecCount % 60).padStart(2, '0');
    const el = document.getElementById("recTimerText");
    if (el) el.textContent = `RECORDING: ${{m}}:${{s}}`;
  }}

  async function stopAndSendWebVoice() {{
    if (!webMediaRecorder) return;
    clearInterval(voiceRecTimer);
    showToast("📤 Sending Voice Note to PC...");

    webMediaRecorder.onstop = async () => {{
      const audioBlob = new Blob(voiceAudioChunks, {{ type: "audio/webm" }});
      const formData = new FormData();
      formData.append("file", audioBlob, `Voice_${{Date.now()}}.webm`);

      try {{
        const res = await authFetch("/api/voice/send?auto_play=true", {{
          method: "POST",
          body: formData
        }});
        const data = await res.json();
        if (data.success) {{
          showToast("🎙️ Voice note PC par send aur play ho gaya!");
          loadPCFilesWeb();
        }} else {{
          showToast("❌ Failed to send voice note", true);
        }}
      }} catch(err) {{
        showToast("❌ Upload error", true);
      }}

      // Reset UI
      document.getElementById("startVoiceRecBtn").style.display = "flex";
      const activeBox = document.getElementById("recordingActiveBox");
      if (activeBox) activeBox.style.display = "none";
    }};

    webMediaRecorder.stop();
  }}

  function connectWebSocket() {{
    const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${{wsProto}}//${{location.host}}/ws/controller?token=${{encodeURIComponent(currentDeviceToken)}}`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {{
      statusBadge.className = "status-badge";
      statusText.textContent = "PC Connected";
      log("🟢 Live Wi-Fi & Tailscale Connection Established!");
      showToast("🟢 Connected to Windows PC!");

      if (window.Notification && Notification.permission === "granted") {{
        try {{
          new Notification("🎮 PC Controller Online", {{
            body: "Aapka server connect ho gaya hai! 🟢"
          }});
        }} catch(e) {{}}
      }}
      if (navigator.vibrate) navigator.vibrate([150, 80, 150]);

      ws.send(JSON.stringify({{
        type: "handshake",
        device_id: "mobile_web_controller",
        payload: {{
          device_name: "Honor X6c",
          device_token: currentDeviceToken
        }}
      }}));
    }};

    ws.onmessage = (event) => {{
      try {{
        const data = JSON.parse(event.data);
        if (data.type === "action_result") {{
          const msg = data.payload?.message || "Action executed";
          log(`✅ ${{msg}}`);
          showToast(msg);
        }} else if (data.type === "welcome") {{
          log(`👋 ${{data.payload?.message || "Connected"}}`);
        }}
      }} catch (err) {{
        console.error(err);
      }}
    }};

    ws.onerror = () => {{
      statusBadge.className = "status-badge disconnected";
      statusText.textContent = "Error";
    }};

    ws.onclose = () => {{
      statusBadge.className = "status-badge disconnected";
      statusText.textContent = "Disconnected (Tap)";
      log("🔴 Connection lost. Reconnecting in 3s...");
      setTimeout(connectWebSocket, 3000);
    }};
  }}

  function reconnectNow() {{
    showToast("🔄 Reconnecting to PC...");
    if (ws) {{
      try {{ ws.close(); }} catch(e) {{}}
    }}
    // Request Notification permission
  if ("Notification" in window && Notification.permission === "default") {{
    try {{ Notification.requestPermission(); }} catch(e) {{}}
  }}

  connectWebSocket();
  }}

  function sendAction(actionName, payload = {{}}) {{
    if (!ws || ws.readyState !== WebSocket.OPEN) {{
      log("⚠️ PC is not connected!");
      showToast("⚠️ Not Connected to PC!", true);
      return;
    }}
    payload.action = actionName;
    ws.send(JSON.stringify({{
      type: "action",
      payload: payload
    }}));
    if (navigator.vibrate) navigator.vibrate(25);
  }}

  function openCustomUrl() {{
    const url = urlInput.value.trim();
    if (!url) return;
    sendAction("open_url", {{ url: url }});
    urlInput.value = "";
  }}

  urlInput.addEventListener("keydown", (e) => {{
    if (e.key === "Enter") openCustomUrl();
  }});

  function runCustomProgram() {{
    const prog = progInput.value.trim();
    if (!prog) return;
    sendAction("run_program", {{ program: prog }});
    progInput.value = "";
  }}

  progInput.addEventListener("keydown", (e) => {{
    if (e.key === "Enter") runCustomProgram();
  }});

  function closeCustomApp() {{
    const app = killAppInput.value.trim();
    if (!app) return;
    sendAction("close_app", {{ name: app }});
    killAppInput.value = "";
    setTimeout(loadRunningApps, 800);
  }}

  killAppInput.addEventListener("keydown", (e) => {{
    if (e.key === "Enter") closeCustomApp();
  }});

  // WhatsApp Chat & Sender Functions
  function fillWaQuickMsg(msg) {{
    const box = document.getElementById("waMessage");
    if (box) box.value = msg;
  }}

  function fillWaRecipient(rec) {{
    const box = document.getElementById("waRecipient");
    if (box) {{
      box.value = rec;
      box.focus();
    }}
  }}

  function sendWhatsAppDirect() {{
    const rec = document.getElementById("waRecipient").value.trim();
    const msg = document.getElementById("waMessage").value.trim();
    if (!rec) {{
      showToast("⚠️ Recipient number ya contact name likhein", true);
      return;
    }}
    if (!msg) {{
      showToast("⚠️ Message text type karein", true);
      return;
    }}
    log(`💬 WhatsApp to ${{rec}}: "${{msg}}"`);
    sendAction("whatsapp_send", {{ recipient: rec, message: msg }});
    showToast(`💬 WhatsApp message sent to ${{rec}}!`);
  }}

  function openWhatsAppChatDirect() {{
    const rec = document.getElementById("waRecipient").value.trim();
    if (!rec) {{
      showToast("⚠️ Recipient number ya contact name likhein", true);
      return;
    }}
    log(`💬 Opening WhatsApp chat with ${{rec}}...`);
    sendAction("whatsapp_open_chat", {{ recipient: rec }});
    showToast(`📂 Opening chat for ${{rec}}...`);
  }}

  function setupMyNumberUI() {{
    document.getElementById("saveContactName").value = "my number";
    document.getElementById("saveContactPhone").focus();
    showToast("📱 Apna number likhein aur Save dabayein!");
  }}

  let waDictationRec = null;
  function dictateWhatsAppMessage() {{
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {{
      showToast("⚠️ Mic browser me supported nahi hai", true);
      showMicHelp();
      return;
    }}
    const dictateBtn = document.getElementById("waDictateBtn");
    const waBox = document.getElementById("waMessage");
    
    if (!waDictationRec) {{
      waDictationRec = new SpeechRecognition();
      waDictationRec.continuous = false;
      waDictationRec.interimResults = false;

      waDictationRec.onstart = () => {{
        dictateBtn.textContent = "🔴 Sun raha hun...";
        showToast("🎙️ Apna message bolein... (Bol kar chup hon)");
      }};
      waDictationRec.onresult = (e) => {{
        dictateBtn.textContent = "🎤 Bol Kar Likhein";
        if (e.results && e.results[0] && e.results[0][0]) {{
          const spoken = e.results[0][0].transcript;
          waBox.value = (waBox.value ? waBox.value + " " : "") + spoken;
          showToast("✅ Message type ho gaya!");
        }}
      }};
      waDictationRec.onerror = (e) => {{
        dictateBtn.textContent = "🎤 Bol Kar Likhein";
        showToast(`⚠️ Mic: ${{e.error}}`, true);
      }};
      waDictationRec.onend = () => {{
        dictateBtn.textContent = "🎤 Bol Kar Likhein";
      }};
    }}
    waDictationRec.lang = currentVoiceLang;
    try {{
      waDictationRec.start();
    }} catch(err) {{
      try {{ waDictationRec.stop(); }} catch(e) {{}}
    }}
  }}

  function loadContacts() {{
    fetch("/api/contacts")
      .then(r => r.json())
      .then(data => {{
        const box = document.getElementById("contactsList");
        box.innerHTML = "";
        const contacts = data.contacts || {{}};
        const names = Object.keys(contacts);
        if (names.length === 0) {{
          box.innerHTML = '<div style="color:#64748b; font-size:0.8rem; text-align:center; padding:10px;">Koi contact saved nahi hai.</div>';
          return;
        }}
        names.forEach(name => {{
          const phone = contacts[name];
          const div = document.createElement("div");
          div.className = "contact-item";
          div.innerHTML = `
            <div style="cursor:pointer;" onclick="fillWaRecipient('${{name}}')">
              <span style="font-weight:700; color:#38bdf8;">👤 ${{name.toUpperCase()}}</span>
              <span style="color:#94a3b8; font-size:0.75rem; margin-left:6px;">${{phone || 'No number'}}</span>
            </div>
            <div style="display:flex; gap:6px;">
              <button class="btn" style="background:#1e293b; border-color:#334155; padding:3px 8px; font-size:0.72rem;" onclick="fillWaRecipient('${{name}}')">Select</button>
              <button class="btn btn-danger" style="padding:3px 8px; font-size:0.72rem;" onclick="deleteContactUI('${{name}}')">&times;</button>
            </div>
          `;
          box.appendChild(div);
        }});
      }})
      .catch(err => console.error(err));
  }}

  function saveContactUI() {{
    const name = document.getElementById("saveContactName").value.trim();
    const phone = document.getElementById("saveContactPhone").value.trim();
    if (!name || !phone) {{
      showToast("⚠️ Name aur phone dono required hain", true);
      return;
    }}
    fetch("/api/contacts", {{
      method: "POST",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{ name: name, phone: phone }})
    }})
    .then(r => r.json())
    .then(data => {{
      showToast(`✅ Contact '${{name}}' saved!`);
      document.getElementById("saveContactName").value = "";
      document.getElementById("saveContactPhone").value = "";
      loadContacts();
    }})
    .catch(err => {{
      showToast("❌ Error saving contact", true);
    }});
  }}

  function deleteContactUI(name) {{
    if (!confirm(`Delete contact '${{name}}'?`)) return;
    fetch(`/api/contacts/${{name}}`, {{ method: "DELETE" }})
      .then(r => r.json())
      .then(data => {{
        showToast(`🗑️ Contact '${{name}}' deleted`);
        loadContacts();
      }})
      .catch(err => console.error(err));
  }}

  function loadRunningApps() {{
    fetch("/api/running_apps")
      .then(r => r.json())
      .then(data => {{
        const box = document.getElementById("runningAppsList");
        box.innerHTML = "";
        if (!data.apps || data.apps.length === 0) {{
          box.innerHTML = '<div style="color:#64748b; font-size:0.8rem; text-align:center; padding:10px;">No user applications currently detected.</div>';
          return;
        }}
        data.apps.forEach(app => {{
          const div = document.createElement("div");
          div.className = "app-pill";
          div.innerHTML = `<span>${{app.icon}} ${{app.display_name}}</span>`;
          const btn = document.createElement("button");
          btn.className = "app-pill-kill";
          btn.textContent = "Close";
          btn.onclick = () => {{
            sendAction("close_app", {{ name: app.short_id }});
            setTimeout(loadRunningApps, 800);
          }};
          div.appendChild(btn);
          box.appendChild(div);
        }});
      }})
      .catch(err => console.error(err));
  }}

  function sendMouseClick(btn) {{
    sendAction("mouse_click", {{ button: btn }});
  }}

  function sendMouseScroll(amt) {{
    sendAction("mouse_scroll", {{ amount: amt }});
  }}

  function sendKey(keyName) {{
    sendAction("press_key", {{ key: keyName }});
  }}

  function sendHotkey(hk) {{
    sendAction("hotkey", {{ hotkey: hk }});
  }}

  let prevLiveTypeVal = "";
  function clearLiveTypeInput() {{
    prevLiveTypeVal = "";
    typeInput.value = "";
  }}

  typeInput.addEventListener("input", () => {{
    const curVal = typeInput.value;
    if (curVal.length > prevLiveTypeVal.length) {{
      const added = curVal.substring(prevLiveTypeVal.length);
      sendAction("type_live", {{ text: added }});
    }} else if (curVal.length < prevLiveTypeVal.length) {{
      const diff = prevLiveTypeVal.length - curVal.length;
      for (let i = 0; i < diff; i++) {{
        sendKey("backspace");
      }}
    }}
    prevLiveTypeVal = curVal;
  }});

  function sendTypeInNotepad() {{
    const text = typeInput.value;
    if (!text) return;
    sendAction("type_in_notepad", {{ text: text }});
    clearLiveTypeInput();
  }}

  // Zero-lag C-kernel touch tracking with accumulator
  // Zero-lag C-kernel touch tracking with accumulator & tap/double-tap gestures
  let lastX = 0;
  let lastY = 0;
  let accumX = 0;
  let accumY = 0;
  let isMoving = false;
  let moveThrottle = 0;

  let touchStartX = 0;
  let touchStartY = 0;
  let touchStartTime = 0;
  let hasMoved = false;
  let lastTapTime = 0;
  let tapTimer = null;

  touchpad.addEventListener("touchstart", (e) => {{
    const touch = e.touches[0];
    lastX = touch.clientX;
    lastY = touch.clientY;
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
    touchStartTime = Date.now();
    hasMoved = false;
    accumX = 0;
    accumY = 0;
    isMoving = true;
    touchpad.classList.add("active");
  }});

  touchpad.addEventListener("touchmove", (e) => {{
    if (!isMoving) return;
    const touch = e.touches[0];
    const dist = Math.hypot(touch.clientX - touchStartX, touch.clientY - touchStartY);
    if (dist > 8) {{
      hasMoved = true;
      if (tapTimer) {{
        // If single tap timer was waiting and user drags, fire the pending left click
        clearTimeout(tapTimer);
        tapTimer = null;
      }}
    }}

    accumX += (touch.clientX - lastX);
    accumY += (touch.clientY - lastY);
    lastX = touch.clientX;
    lastY = touch.clientY;

    const now = Date.now();
    if (now - moveThrottle > 35) {{
      moveThrottle = now;
      const sendDx = Math.round(accumX * 2.2);
      const sendDy = Math.round(accumY * 2.2);
      accumX = 0;
      accumY = 0;
      if (ws && ws.readyState === WebSocket.OPEN && (sendDx !== 0 || sendDy !== 0)) {{
        ws.send(JSON.stringify({{
          type: "action",
          payload: {{ action: "mouse_move", dx: sendDx, dy: sendDy }}
        }}));
      }}
    }}
  }});

  touchpad.addEventListener("touchend", () => {{
    isMoving = false;
    touchpad.classList.remove("active");

    const touchDuration = Date.now() - touchStartTime;
    // Tap detection: finger didn't drag and released quickly (< 280ms)
    if (!hasMoved && touchDuration < 280) {{
      const now = Date.now();
      if (now - lastTapTime < 320) {{
        // DOUBLE TAP -> RIGHT CLICK
        if (tapTimer) {{
          clearTimeout(tapTimer);
          tapTimer = null;
        }}
        lastTapTime = 0;
        sendMouseClick("right");
      }} else {{
        // SINGLE TAP -> LEFT CLICK
        lastTapTime = now;
        tapTimer = setTimeout(() => {{
          sendMouseClick("left");
          tapTimer = null;
        }}, 250);
      }}
    }}
  }});

  // Voice & Text Commands
  function sendTextCommand() {{
    const text = cmdInput.value.trim().toLowerCase();
    if (!text) return;
    cmdInput.value = "";
    log(`🗣️ Command: "${{text}}"`);

    if (ws && ws.readyState === WebSocket.OPEN) {{
      ws.send(JSON.stringify({{
        type: "command",
        payload: {{ query: text }}
      }}));
    }}
  }}

  function quickVoice(cmd) {{
    cmdInput.value = cmd;
    sendTextCommand();
  }}

  cmdInput.addEventListener("keydown", (e) => {{
    if (e.key === "Enter") sendTextCommand();
  }});

  let currentVoiceLang = "ur-PK";
  function toggleVoiceLang() {{
    const btn = document.getElementById("langToggleBtn");
    if (currentVoiceLang === "ur-PK") {{
      currentVoiceLang = "en-US";
      btn.textContent = "🌐 EN";
      btn.style.color = "#38bdf8";
      showToast("🌐 Voice: English / Roman Urdu Mode");
    }} else {{
      currentVoiceLang = "ur-PK";
      btn.textContent = "🌐 UR";
      btn.style.color = "#4ade80";
      showToast("🌐 Voice: Urdu (اردو) Mode");
    }}
  }}

  // Voice Recognition
  let recognition = null;
  function toggleVoiceRecognition() {{
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {{
      showToast("⚠️ Speech recognition browser me available nahi hai", true);
      showMicHelp();
      return;
    }}
    if (!recognition) {{
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {{
        micBtn.classList.add("listening");
        showToast(currentVoiceLang === "ur-PK" ? "🎙️ اردو میں بولیں..." : "🎙️ Bolye (English/Roman Urdu)...", false);
        log("🎙️ Sun raha hun... Bolye!");
      }};

      recognition.onresult = (event) => {{
        micBtn.classList.remove("listening");
        if (event.results && event.results[0] && event.results[0][0]) {{
          const text = event.results[0][0].transcript;
          cmdInput.value = text;
          log(`🗣️ Voice: "${{text}}"`);
          sendTextCommand();
        }}
      }};

      recognition.onerror = (e) => {{
        micBtn.classList.remove("listening");
        log(`⚠️ Mic Error: ${{e.error}}`);
        if (e.error === "not-allowed" || e.error === "service-not-allowed") {{
          showToast("🔒 Android Chrome ne HTTP mic block kiya", true);
          showMicHelp();
        }} else if (e.error === "no-speech") {{
          showToast("⚠️ Kuch suna nahi gaya, dubara bolen", true);
        }} else {{
          showToast(`⚠️ Mic error: ${{e.error}}`, true);
        }}
      }};

      recognition.onend = () => micBtn.classList.remove("listening");
    }}
    recognition.lang = currentVoiceLang;
    try {{
      recognition.start();
    }} catch(e) {{
      try {{ recognition.stop(); }} catch(err) {{}}
      showMicHelp();
    }}
  }}

  function showMicHelp() {{
    const modal = document.getElementById("micHelpModal");
    if (modal) modal.style.display = "flex";
  }}

  function closeMicHelp() {{
    const modal = document.getElementById("micHelpModal");
    if (modal) modal.style.display = "none";
  }}

  function copyText(str, msg) {{
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(str).then(() => showToast(msg || "Copied!")).catch(() => prompt("Copy this:", str));
    }} else {{
      prompt("Copy this:", str);
    }}
  }}

  function switchToHttps() {{
    const host = location.hostname;
    location.href = `https://${{host}}:8443/`;
  }}

  // Show HTTPS banner if on HTTP
  if (location.protocol === "http:") {{
    const b = document.getElementById("httpsBanner");
    if (b) b.style.display = "flex";
  }}

  // Request Notification permission
  if ("Notification" in window && Notification.permission === "default") {{
    try {{ Notification.requestPermission(); }} catch(e) {{}}
  }}

  connectWebSocket();
</script>

</body>
</html>
"""
