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
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
      width: 100%;
      margin: 0;
      padding: 10px 8px;
      overflow-x: hidden;
      box-sizing: border-box;
    }}
    .container {{
      width: 100%;
      max-width: 520px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-sizing: border-box;
      overflow-x: hidden;
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
    /* Master Selection Hub (PC vs Mobile) */
    .hub-container {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 92vh;
      padding: 18px 14px;
      box-sizing: border-box;
      max-width: 480px;
      margin: 0 auto;
    }}
    .hub-header {{
      text-align: center;
      margin-bottom: 22px;
      width: 100%;
    }}
    .hub-icon-badge {{
      width: 58px;
      height: 58px;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(79, 70, 229, 0.25), rgba(16, 185, 129, 0.25));
      border: 1.5px solid #6366f1;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.8rem;
      margin: 0 auto 10px;
      box-shadow: 0 0 20px rgba(99, 102, 241, 0.35);
    }}
    .hub-title {{
      font-size: 1.35rem;
      font-weight: 800;
      color: #fff;
      margin-bottom: 4px;
    }}
    .hub-subtitle {{
      font-size: 0.82rem;
      color: #94a3b8;
    }}
    .hub-card {{
      width: 100%;
      border-radius: 16px;
      padding: 18px 16px;
      margin-bottom: 14px;
      box-sizing: border-box;
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
      position: relative;
    }}
    .hub-card:active {{
      transform: scale(0.98);
    }}
    .hub-card-pc {{
      border: 1.5px solid #4f46e5;
      background: linear-gradient(145deg, #131b2e 0%, #0d1322 100%);
      box-shadow: 0 8px 24px rgba(79, 70, 229, 0.2);
    }}
    .hub-card-mobile {{
      border: 1.5px solid #059669;
      background: linear-gradient(145deg, #0e1e24 0%, #091519 100%);
      box-shadow: 0 8px 24px rgba(16, 185, 129, 0.2);
    }}
    .hub-card-top {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
    }}
    .hub-card-icon {{
      font-size: 2rem;
      width: 44px;
      height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.05);
    }}
    .hub-card-title {{
      font-size: 1.15rem;
      font-weight: 800;
      color: #fff;
    }}
    .hub-card-desc {{
      font-size: 0.78rem;
      color: #94a3b8;
      margin-bottom: 10px;
      line-height: 1.4;
    }}
    .hub-card-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-bottom: 12px;
    }}
    .hub-card-btn {{
      width: 100%;
      padding: 12px;
      border-radius: 10px;
      border: none;
      font-weight: 800;
      font-size: 0.88rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      color: #fff;
    }}
    .hub-card-btn-pc {{
      background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
      box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4);
    }}
    .hub-card-btn-mobile {{
      background: linear-gradient(135deg, #059669 0%, #10b981 100%);
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
    }}
    .top-nav-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 12px;
      padding: 8px 10px;
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 12px;
    }}
    .nav-back-btn {{
      background: #1e293b;
      border: 1px solid #334155;
      color: #cbd5e1;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 0.76rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .nav-back-btn:active {{
      background: #334155;
      color: #fff;
    }}
    .nav-switch-btn {{
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid #10b981;
      color: #34d399;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 0.76rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .nav-switch-btn:active {{
      filter: brightness(1.2);
    }}
    .nav-switch-btn-pc {{
      background: rgba(99, 102, 241, 0.15);
      border: 1px solid #6366f1;
      color: #a5b4fc;
    }}
  </style>
</head>
<body>

<div id="toast" class="toast">Action Executed</div>

<!-- ======================================================== -->
<!-- VIEW 1: MASTER SELECTION HUB (Control PC vs Mobile)      -->
<!-- ======================================================== -->
<div id="view-hub" class="hub-container">
  <div class="hub-header">
    <div class="hub-icon-badge">⚡</div>
    <div class="hub-title">Personal AI Command Center</div>
    <div class="hub-subtitle">Kisko control karna chahte hain? Option select karein:</div>
    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">
      🌐 Master Hub Server: <strong style="color:#38bdf8;">{local_ip}:{port}</strong>
    </div>
  </div>

  <!-- Card 1: Control PC -->
  <div class="hub-card hub-card-pc" onclick="openView('pc')">
    <div class="hub-card-top">
      <div class="hub-card-icon" style="color:#818cf8;">🖥️</div>
      <div>
        <div class="hub-card-title">Control PC</div>
        <div style="font-size:0.75rem; color:#a5b4fc;">Master Computer Remote Control</div>
      </div>
    </div>
    <div class="hub-card-desc">
      Apne Windows PC ko mobile se mukammal control karein. Voice control, ultra-fast screen streaming, typing, files aur YouTube studio chalayein.
    </div>
    <div class="hub-card-tags">
      <span class="chip" style="background:#1e1b4b; border-color:#3730a3; color:#c7d2fe;">⚡ Quick Power & Sleep</span>
      <span class="chip" style="background:#1e1b4b; border-color:#3730a3; color:#c7d2fe;">🎙️ AI Voice Command</span>
      <span class="chip" style="background:#1e1b4b; border-color:#3730a3; color:#c7d2fe;">📺 Live Screen</span>
      <span class="chip" style="background:#1e1b4b; border-color:#3730a3; color:#c7d2fe;">🤖 Antigravity Bot</span>
      <span class="chip" style="background:#1e1b4b; border-color:#3730a3; color:#c7d2fe;">💬 WhatsApp</span>
    </div>
    <button class="hub-card-btn hub-card-btn-pc" onclick="openView('pc'); event.stopPropagation();">
      <span>🖥️ Open PC Controller</span>
      <span>➔</span>
    </button>
  </div>

  <!-- Card 2: Control Mobile -->
  <div class="hub-card hub-card-mobile" onclick="openView('mobile')">
    <div class="hub-card-top">
      <div class="hub-card-icon" style="color:#34d399;">📱</div>
      <div>
        <div class="hub-card-title">Control Mobile (Phone Farm)</div>
        <div style="font-size:0.75rem; color:#6ee7b7;">100+ Physical Android Devices Hub</div>
      </div>
    </div>
    <div class="hub-card-desc">
      Hotspot se connect hone wale 100+ physical mobiles ko aik sath control karein. 20 KB agent, universal broadcast gestures, subnet scanner aur sync actions.
    </div>
    <div class="hub-card-tags">
      <span class="chip" style="background:#064e3b; border-color:#047857; color:#a7f3d0;">🔀 Broadcast to All Phones</span>
      <span class="chip" style="background:#064e3b; border-color:#047857; color:#a7f3d0;">🎮 Touch, Swipe, Home, Back</span>
      <span class="chip" style="background:#064e3b; border-color:#047857; color:#a7f3d0;">🔍 0.5s Auto-Scan Subnet</span>
      <span class="chip" style="background:#064e3b; border-color:#047857; color:#a7f3d0;">⚡ 20 KB Ultra Tiny Agent</span>
      <span class="chip" style="background:#064e3b; border-color:#047857; color:#a7f3d0;">🔋 Live Battery & Monitor</span>
    </div>
    <button class="hub-card-btn hub-card-btn-mobile" onclick="openView('mobile'); event.stopPropagation();">
      <span>📱 Open Mobile Farm Controller</span>
      <span>➔</span>
    </button>
  </div>
</div>

<!-- ======================================================== -->
<!-- VIEW 2: PC CONTROLLER DASHBOARD                         -->
<!-- ======================================================== -->
<div id="view-pc" class="container" style="display:none;">
  <!-- Top Switch Bar -->
  <div class="top-nav-bar">
    <button class="nav-back-btn" onclick="openView('hub')">🏠 Back to Hub</button>
    <div style="font-size:0.8rem; font-weight:700; color:#818cf8;">🖥️ PC Controller Mode</div>
    <button class="nav-switch-btn" onclick="openView('mobile')">📱 Switch to Mobile Farm ➔</button>
  </div>
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
    <!-- Active Recording Banner (Directly inside top card when recording) -->
    <div id="topVoiceRecBanner" style="display:none; background:rgba(239, 68, 68, 0.2); border:1.5px solid #ef4444; border-radius:10px; padding:10px 12px; margin-bottom:8px; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap:8px;">
        <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#ef4444; box-shadow:0 0 10px #ef4444; animation:pulse 1s infinite;"></span>
        <div>
          <span id="topRecTimer" style="font-weight:800; color:#fca5a5; font-size:0.92rem;">🔴 RECORDING: 00:00</span>
          <div style="font-size:0.7rem; color:#cbd5e1;">Stop dabate hi PC par Send ho jayega!</div>
        </div>
      </div>
      <div style="display:flex; gap:6px;">
        <button class="btn" style="background:#10b981; border:none; padding:8px 14px; font-weight:800; font-size:0.82rem;" onclick="stopAndSendWebVoice()">Stop & Send 🚀</button>
        <button class="btn" style="background:#334155; border:none; padding:8px 10px;" onclick="cancelWebVoice()">❌</button>
      </div>
    </div>

    <!-- Tier 1: Input Bar & Send -->
    <div style="display:flex; gap:6px; margin-bottom:8px;">
      <input type="text" id="cmdInput" class="input-bar" placeholder="Bolye ya likhein: 'open chat gpt', 'ali ki chat'...">
      <button id="langToggleBtn" class="btn" style="padding:0 10px; font-size:0.75rem; background:#1e293b; border-color:#334155; font-weight:800; color:#4ade80;" onclick="toggleVoiceLang()" title="Toggle Urdu / English Mic">🌐 UR</button>
      <button class="btn" style="background: var(--accent); border-color: var(--accent); padding: 0 16px; font-weight:700;" onclick="sendTextCommand()">Send</button>
    </div>

    <!-- Tier 2: Two Big Mobile Buttons (100% visible, never off-screen) -->
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
      <button id="mainVoiceNoteBtn" class="btn" style="background: linear-gradient(135deg, #7c3aed, #4f46e5); border:1px solid #a855f7; padding:12px 8px; font-weight:800; font-size:0.84rem; color:#fff; box-shadow:0 2px 10px rgba(124, 58, 237, 0.35);" onclick="toggleVoiceNoteRecord()" title="Mobile se Voice Note record karke PC par direct send karein">
        <span style="font-size:1.15rem;">🎙️</span> Voice Note Bhejein
      </button>

      <button id="micBtn" class="btn" style="background:#1e293b; border:1px solid #334155; padding:12px 8px; font-weight:700; font-size:0.84rem; color:#fff;" onclick="toggleVoiceRecognition()" title="Bol kar text type karein">
        <span style="font-size:1.15rem;">🎤</span> Bol Kar Likhna
      </button>
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
    <button class="tab-btn active" onclick="switchTab('quick', this)">⚡ Quick & Power</button>
    <button class="tab-btn" style="border-color:#10b981; color:#34d399; font-weight:700;" onclick="switchTab('phonefarm', this)">📱 Phone Farm (100x)</button>
    <button class="tab-btn" style="border-color:#a855f7; color:#c084fc; font-weight:700;" onclick="switchTab('antigravity', this)">🤖 Antigravity Bot</button>
    <button class="tab-btn" style="border-color:#ef4444; color:#f87171; font-weight:700;" onclick="switchTab('youtube', this)">🎬 YouTube Studio</button>
    <button class="tab-btn" style="border-color:#38bdf8; color:#38bdf8; font-weight:700;" onclick="switchTab('vision', this)">👁️ AI Vision</button>
    <button class="tab-btn" onclick="switchTab('screen', this)">📺 Screen</button>
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
      <div class="grid-3">
        <button class="btn" onclick="sendAction('show_desktop')">
          <span class="icon">🖥️</span>
          <span>Desktop</span>
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

    <!-- 1-Tap Remote Power Cockpit -->
    <div class="card" style="border-color: rgba(239, 68, 68, 0.4); background: linear-gradient(135deg, #1e1b4b 0%, #18181b 100%);">
      <div class="card-title" style="color: #f87171;">
        <span>⚡ Remote Power Cockpit</span>
      </div>
      <div style="font-size:0.75rem; color:#cbd5e1; margin-bottom:10px;">
        Ghar k kisi bhi hisse se PC ko 1 tap me band ya sleep karein:
      </div>
      <div class="grid-2" style="margin-bottom:8px;">
        <button class="btn btn-danger" style="padding:14px; font-weight:800;" onclick="confirmAction('PC Shut down karein? (15s timer chalega)', () => sendAction('system_shutdown'))">
          <span class="icon" style="font-size:1.4rem;">🔴</span>
          <span>Shutdown PC</span>
          <span style="font-size:0.68rem; color:#fca5a5;">(15s Timer)</span>
        </button>
        <button class="btn" style="padding:14px; background:#1e293b; border-color:#eab308; font-weight:700;" onclick="sendAction('system_sleep')">
          <span class="icon" style="font-size:1.4rem;">🟡</span>
          <span>Sleep PC</span>
          <span style="font-size:0.68rem; color:#fde047;">(Standby)</span>
        </button>
      </div>
      <div class="grid-2">
        <button class="btn" style="padding:12px; background:#1e293b; border-color:#38bdf8;" onclick="confirmAction('PC Restart karein?', () => sendAction('system_restart'))">
          <span class="icon">🔄</span>
          <span>Restart PC</span>
        </button>
        <button class="btn" style="padding:12px; background:#065f46; border-color:#10b981; color:#a7f3d0; font-weight:700;" onclick="sendAction('cancel_shutdown')">
          <span class="icon">🟢</span>
          <span>Cancel Shutdown</span>
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

  <!-- TAB: ANTIGRAVITY & AI AUTOMATION BOT -->
  <div id="tab-antigravity" class="tab-content">
    <!-- Auto-Submitter Card -->
    <div class="card" style="border-color: rgba(168, 85, 247, 0.4); background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);">
      <div class="card-title" style="color: #c084fc;">
        <span>🤖 Antigravity Auto-Submitter & Proceed Bot</span>
      </div>
      <div style="font-size: 0.78rem; color: #cbd5e1; margin-bottom: 12px; line-height: 1.5;">
        Jab aap coding session chala rahe hon, baar baar PC par "Submit" ya "Proceed" dabane ki zaroorat nahi:
      </div>
      
      <!-- Big 1-Tap Proceed Button -->
      <button class="btn" style="width:100%; padding:20px; font-size:1.15rem; font-weight:800; background:linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%); border:2px solid #a855f7; margin-bottom:12px; box-shadow:0 4px 20px rgba(124, 58, 237, 0.4);" onclick="sendAction('antigravity_proceed')">
        <span class="icon" style="font-size:2rem;">⚡</span>
        <span>PROCEED / SUBMIT NOW</span>
        <span style="font-size:0.75rem; color:#e0e7ff; margin-top:2px;">Dispatches Enter to active Antigravity/Terminal session</span>
      </button>

      <!-- Continuous Auto-Proceed Loop Toggle -->
      <div style="background:#090d16; border:1px solid #1e293b; border-radius:10px; padding:12px; display:flex; align-items:center; justify-content:space-between;">
        <div>
          <div style="font-weight:700; color:#f8fafc; font-size:0.86rem;">Continuous Auto-Proceed Mode</div>
          <div style="font-size:0.72rem; color:#94a3b8;">Har 8s baad khud Enter press karega taake long runs na rukein</div>
        </div>
        <button id="autoProceedToggleBtn" class="btn" style="background:#1e293b; border-color:#334155; padding:8px 14px; font-weight:800;" onclick="toggleAutoProceedUI()">
          OFF ⏸️
        </button>
      </div>
    </div>

    <!-- Emergency Rescue Card -->
    <div class="card" style="border-color: rgba(56, 189, 248, 0.4);">
      <div class="card-title" style="color:#38bdf8;">
        <span>🧊 Emergency PC Freeze Rescue</span>
      </div>
      <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:10px;">
        Agar kisi heavy compile ya video render ki wajah se PC hang/freeze ho jaye, to memory free karke PC ko responsive banayein:
      </div>
      <button class="btn" style="width:100%; padding:14px; background:#0e7490; border-color:#06b6d4; font-weight:800; color:#fff;" onclick="sendAction('rescue_pc')">
        <span class="icon">🧊</span>
        <span>Rescue PC (Flush RAM & Unfreeze)</span>
      </button>
    </div>
  </div>

  <!-- TAB: YOUTUBE CREATOR STUDIO & AI SEO -->
  <div id="tab-youtube" class="tab-content">
    <!-- Direct Studio Uploader -->
    <div class="card" style="border-color: rgba(239, 68, 68, 0.4); background: linear-gradient(135deg, #2e1010 0%, #131c2e 100%);">
      <div class="card-title" style="color: #f87171;">
        <span>🎬 YouTube Creator Studio</span>
      </div>
      <div style="font-size: 0.76rem; color: #cbd5e1; margin-bottom: 10px;">
        1-Tap me YouTube Studio ka direct video upload page open karein:
      </div>
      <button class="btn" style="width:100%; padding:14px; background:#dc2626; border-color:#ef4444; font-weight:800; color:#fff; box-shadow:0 4px 16px rgba(239,68,68,0.4);" onclick="sendAction('open_youtube_studio')">
        <span class="icon" style="font-size:1.4rem;">📤</span>
        <span>Open YouTube Studio Upload Page</span>
      </button>
    </div>

    <!-- AI Viral YouTube SEO & Tag Generator -->
    <div class="card" style="border-color: rgba(245, 158, 11, 0.4);">
      <div class="card-title" style="color: #fbbf24;">
        <span>🏷️ AI Viral YouTube SEO & Tag Generator</span>
      </div>
      <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 8px;">
        Apni video ka topic likhein ya bolein. AI viral Titles, Tags aur Description generate karke direct PC clipboard me paste kar dega:
      </div>
      <div style="display:flex; gap:6px; margin-bottom:10px;">
        <input type="text" id="ytSeoTopicInput" class="input-bar" placeholder="e.g. AI Coding Assistant Tutorial 2026...">
        <button class="btn" style="background:#d97706; border-color:#f59e0b; padding:0 14px; font-weight:700; white-space:nowrap;" onclick="generateYtSeoWeb()">Generate 🚀</button>
      </div>
      <div id="ytSeoResultsBox" style="display:none; background:#0b1120; border:1px solid #1e293b; border-radius:10px; padding:12px; font-size:0.78rem;">
        <div style="color:#4ade80; font-weight:800; margin-bottom:6px;">✅ Copied to PC Clipboard!</div>
        <div id="ytSeoContent" style="white-space:pre-wrap; color:#cbd5e1; font-family:monospace; max-height:160px; overflow-y:auto;"></div>
      </div>
    </div>

    <!-- Upload / Render Timer Alert -->
    <div class="card">
      <div class="card-title"><span>⏱️ Video Upload & Render Completion Alert</span></div>
      <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:10px;">
        Estimated upload/render minutes set karein. Complete hote hi phone aur PC par alarm bajega:
      </div>
      <div style="display:flex; gap:6px;">
        <input type="number" id="renderTimerMinutes" class="input-bar" placeholder="Minutes (e.g. 10)" style="max-width:140px;">
        <button class="btn" style="flex:1; background:#1e293b; border-color:#38bdf8; font-weight:700;" onclick="setRenderTimerWeb()">⏱️ Set Alert Timer</button>
      </div>
    </div>
  </div>

  <!-- TAB: AI SCREEN VISION -->
  <div id="tab-vision" class="tab-content">
    <div class="card" style="border-color: rgba(56, 189, 248, 0.4); background: linear-gradient(135deg, #082f49 0%, #0f172a 100%);">
      <div class="card-title" style="color: #38bdf8;">
        <span>👁️ AI Screen Vision & Assistant</span>
      </div>
      <div style="font-size: 0.76rem; color: #cbd5e1; margin-bottom: 12px; line-height: 1.4;">
        PC par is waqt jo bhi khula hai, uske mutabiq sawaal poochein ya analysis maangein:
      </div>
      <div style="display:flex; gap:6px; margin-bottom:10px;">
        <input type="text" id="visionQuestionInput" class="input-bar" placeholder="e.g. 'Screen par kya chal raha hai?', 'Error explain karo'...">
        <button class="btn" style="background:#0284c7; border-color:#38bdf8; padding:0 14px; font-weight:700;" onclick="askAiVisionWeb()">Analyze 👁️</button>
      </div>
      <div id="visionResultCard" style="display:none; background:#090d16; border:1px solid #1e293b; border-radius:10px; padding:12px;">
        <div id="visionActiveWindowBadge" style="font-size:0.75rem; font-weight:800; color:#38bdf8; margin-bottom:6px;"></div>
        <div id="visionAnalysisText" style="font-size:0.82rem; color:#f1f5f9; line-height:1.5; white-space:pre-wrap; margin-bottom:10px;"></div>
        <img id="visionImgPreview" style="width:100%; border-radius:8px; border:1px solid #334155;" alt="Screen analysis frame">
      </div>
    </div>
  </div>

  <!-- TAB: SCREEN MIRROR & MOUSE -->
  <div id="tab-screen" class="tab-content">
    <div class="card" style="border-color: rgba(99, 102, 241, 0.4); padding: 12px;">
      
      <!-- 1. LIVE PC SCREEN STREAM -->
      <div class="card-title" style="margin-bottom:8px;">
        <span>📺 Live PC Screen</span>
        <button id="streamToggleBtn" class="btn" style="padding:4px 10px; font-size:0.75rem; background:#4f46e5; border-color:#6366f1;" onclick="toggleScreenStreamWeb()">▶️ Start Stream</button>
      </div>
      <div id="screenStreamContainer" style="position:relative; width:100%; aspect-ratio:16/9; background:#000; border:2px solid #1e293b; border-radius:10px; display:flex; align-items:center; justify-content:center; overflow:hidden; touch-action:none; user-select:none; cursor:crosshair;">
        <span id="screenPlaceholder" style="color:#64748b; font-size:0.8rem;">Tap 'Start Stream' to mirror PC screen</span>
        <canvas id="screenCanvas" style="width:100%; height:100%; object-fit:contain; display:none; border-radius:8px; pointer-events:none;"></canvas>
        <img id="screenStreamImg" style="width:100%; height:100%; object-fit:contain; display:none; border-radius:8px; pointer-events:none;" alt="Live PC Screen" />
        <div id="screenTouchHint" style="display:none; position:absolute; top:8px; right:8px; background:rgba(15,23,42,0.88); border:1px solid #6366f1; border-radius:20px; padding:3px 10px; font-size:0.68rem; color:#a5b4fc; pointer-events:none; z-index:5;">
          ⚡ Live Socket Stream Active
        </div>
      </div>

      <!-- 2. HIGH-SPEED MOUSE CONTROLLER BOX -->
      <div style="margin-top:10px; background:#070d19; border:1px solid #1e293b; border-radius:12px; padding:10px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <span style="font-size:0.82rem; font-weight:800; color:#c7d2fe; display:flex; align-items:center; gap:5px;">
            🖱️ Mouse Box
          </span>
          <button id="mouseSpeedPill" class="chip" style="padding:2px 8px; font-size:0.68rem; border-color:#38bdf8; color:#38bdf8;" onclick="cycleMouseSpeed()">⚡ Speed: Fast (3.5x)</button>
        </div>

        <!-- Precision Gliding Touchpad Surface -->
        <div id="screenTouchpad" class="touchpad" style="height:130px; background:#0b1222; border:1.5px dashed #4f46e5; border-radius:10px;">
          <span style="font-size:0.86rem; color:#a5b4fc; font-weight:700;">👆 Fast Touchpad: Drag to Move PC Mouse</span>
          <span style="font-size:0.7rem; color:#64748b; margin-top:3px;">1-Tap: Left Click &bull; 2-Tap: Right Click</span>
        </div>
      </div>

      <!-- 3. PC LIVE TYPING BOX -->
      <div style="margin-top:10px; background:#070d19; border:1px solid #1e293b; border-radius:12px; padding:10px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <span style="font-size:0.82rem; font-weight:800; color:#c7d2fe; display:flex; align-items:center; gap:5px;">
            ⌨️ Live Typing Box
          </span>
          <span style="font-size:0.68rem; color:#64748b;">Direct PC Cursor Typing</span>
        </div>
        <div style="display:flex; gap:6px;">
          <input type="text" id="screenLiveTypeInput" class="input-bar" placeholder="Yahan type karein aur Type dabayein..." onkeydown="if(event.key==='Enter') sendScreenLiveType()" />
          <button class="btn" style="background:linear-gradient(135deg, #4f46e5, #6366f1); border-color:#6366f1; padding:0 14px; font-weight:800; white-space:nowrap;" onclick="sendScreenLiveType()">
            Type 🚀
          </button>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:6px; margin-top:8px;">
          <button class="btn" style="padding:8px 4px; font-size:0.75rem; background:#1e293b; border-color:#334155;" onclick="sendKeyStroke('enter')">⏎ Enter</button>
          <button class="btn" style="padding:8px 4px; font-size:0.75rem; background:#1e293b; border-color:#334155;" onclick="sendKeyStroke('backspace')">⌫ Backspace</button>
          <button class="btn" style="padding:8px 4px; font-size:0.75rem; background:#1e293b; border-color:#334155;" onclick="sendKeyStroke('space')">␣ Space</button>
        </div>
      </div>

      <!-- 4. COMPACT 1-TAP SCREENSHOT & DIRECT DOWNLOAD BUTTON -->
      <div style="margin-top:10px;">
        <button id="quickScreenDlBtn" class="btn" style="width:100%; padding:11px; font-size:0.82rem; font-weight:700; background:#0f172a; border-color:#334155; color:#94a3b8; display:flex; align-items:center; justify-content:center; gap:6px;" onclick="quickCaptureAndDownloadWeb()">
          <span>📸</span>
          <span>Capture Screen & Direct Download</span>
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
        <button class="btn" onclick="sendAction('open_explorer')"><span class="icon">📁</span><span>Explorer</span></button>
        <button class="btn" onclick="sendAction('open_settings')"><span class="icon">⚙️</span><span>Settings</span></button>
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
</div><!-- END VIEW-PC -->

<!-- ======================================================== -->
<!-- VIEW 3: MOBILE FARM CONTROLLER DASHBOARD                -->
<!-- ======================================================== -->
<div id="view-mobile" class="container" style="display:none;">
  <!-- Top Switch Bar -->
  <div class="top-nav-bar">
    <button class="nav-back-btn" onclick="openView('hub')">🏠 Back to Hub</button>
    <div style="font-size:0.8rem; font-weight:700; color:#34d399;">📱 Mobile Farm Mode</div>
    <button class="nav-switch-btn nav-switch-btn-pc" onclick="openView('pc')">🖥️ Switch to PC ➔</button>
  </div>

  <header>
    <div class="logo-box">
      <h1>📱 Mobile Farm Controller</h1>
      <span style="font-size:0.75rem; color:#94a3b8;">100+ Android Devices Hub • Port 9090</span>
    </div>
    <div class="status-badge" style="background:rgba(16,185,129,0.15); border-color:#10b981; color:#34d399; cursor:pointer;" onclick="loadPhoneFarmDevices()" title="Refresh farm devices">
      <span class="dot"></span>
      <span>Farm Active</span>
    </div>
  </header>

  <!-- Hub Overview & Setup Banner -->
    <div class="card" style="border-color: rgba(16, 185, 129, 0.4);">
      <div class="card-title" style="color: #34d399;">
        <span>📱 100+ Phone Farm Hub & Multi-Device Control</span>
        <button class="chip" style="background:#064e3b; border-color:#059669; color:#a7f3d0;" onclick="loadPhoneFarmDevices()">🔄 Refresh</button>
      </div>
      <div style="font-size: 0.76rem; color: #94a3b8; margin-bottom: 12px; line-height: 1.4;">
        Master Hotspot se connect hone wale tamam mobiles yahan auto-register hote hain. Har mobile me 20 KB ka agent background me 24/7 chalta hai aur port 9090 se direct control hota hai.
      </div>

      <!-- Quick Stats Badges -->
      <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom: 12px;">
        <div class="chip" style="background:#0b1324; border-color:#1e293b; color:#34d399;">
          🟢 Active: <strong id="pfOnlineCount" style="margin-left:4px;">0</strong> / <span id="pfTotalCount">0</span> Devices
        </div>
        <div class="chip" style="background:#0b1324; border-color:#1e293b; color:#38bdf8;">
          🌐 Master Hub: <strong>{local_ip}:{port}</strong>
        </div>
        <div class="chip" style="background:#0b1324; border-color:#10b981; color:#a7f3d0; cursor:pointer;" onclick="copyText('http://{local_ip}:{port}/setup', 'Setup link copied!')">
          📋 Copy Setup Link (for phones)
        </div>
        <div class="chip" style="background:#0b1324; border-color:#38bdf8; color:#38bdf8; cursor:pointer;" onclick="toggleQrModal()">
          📷 Show QR Code to Scan
        </div>
      </div>

      <!-- QR Code Modal Popup -->
      <div id="pfQrModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:99999; align-items:center; justify-content:center; padding:16px; box-sizing:border-box;">
        <div style="background:#131c2e; border:1.5px solid #10b981; border-radius:16px; max-width:360px; width:100%; padding:20px; text-align:center; color:#fff; box-shadow:0 8px 32px rgba(16,185,129,0.3);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <strong style="font-size:1rem; color:#34d399;">📷 Scan to Install Agent (20 KB)</strong>
            <button onclick="toggleQrModal()" style="background:none; border:none; color:#94a3b8; font-size:1.4rem; cursor:pointer;">&times;</button>
          </div>
          <p style="font-size:0.78rem; color:#94a3b8; margin-bottom:14px; line-height:1.4;">
            Kisi bhi phone ka normal <b>Camera</b> khol kar is QR code par point karein -> Screen par link tap karein aur install karein!
          </p>
          <div style="background:#fff; padding:10px; border-radius:12px; display:inline-block; margin-bottom:12px;">
            <img src="/api/setup_qr" style="width:180px; height:180px; display:block;" alt="Setup QR Code">
          </div>
          <div style="font-size:0.75rem; color:#38bdf8; font-family:monospace; margin-bottom:14px;">
            http://{local_ip}:{port}/setup
          </div>
          <button class="btn" style="background:#1e293b; border-color:#334155; width:100%; padding:10px;" onclick="toggleQrModal()">Close</button>
        </div>
      </div>

      <!-- Auto Scan & Manual Add Toolbar -->
      <div style="display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
        <input type="text" id="pfManualIp" class="input-bar" style="flex:1; min-width:140px;" placeholder="Add IP (e.g. 192.168.43.45)...">
        <button class="btn" style="background:#1e293b; border-color:#334155; padding:8px 12px; font-size:0.78rem;" onclick="addPhoneFarmManualIp()">➕ Add IP</button>
        <button class="btn" id="pfScanBtn" style="background:#065f46; border-color:#059669; color:#fff; padding:8px 12px; font-size:0.78rem; font-weight:700;" onclick="scanPhoneFarmSubnet()">🔍 Auto-Scan Subnet</button>
      </div>
    </div>

    <!-- Master Remote Control Panel -->
    <div class="card" style="border-color: rgba(56, 189, 248, 0.35);">
      <div class="card-title" style="color: #38bdf8;">
        <span>🎮 Universal Remote Controller</span>
      </div>

      <!-- Target Selection Dropdown -->
      <div style="margin-bottom: 12px;">
        <label style="font-size:0.75rem; color:#94a3b8; display:block; margin-bottom:4px;">Target Device(s):</label>
        <select id="pfTargetSelect" class="input-bar" style="width:100%; font-weight:700; color:#34d399; background:#0b1120;">
          <option value="all">⚡ ALL PHONES (Broadcast to 100+ Devices Simultaneously)</option>
        </select>
      </div>

      <!-- Navigation Global Keys -->
      <div style="font-size:0.72rem; color:#94a3b8; margin-bottom:4px; font-weight:600;">System Navigation Keys:</div>
      <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap:6px; margin-bottom:12px;">
        <button class="btn" style="background:#0d1526; border-color:#1e293b; padding:9px 4px; font-size:0.78rem;" onclick="sendPhoneFarmAction('key', {{ key: 'back' }})">◀ Back</button>
        <button class="btn" style="background:#0d1526; border-color:#1e293b; padding:9px 4px; font-size:0.78rem;" onclick="sendPhoneFarmAction('key', {{ key: 'home' }})">🏠 Home</button>
        <button class="btn" style="background:#0d1526; border-color:#1e293b; padding:9px 4px; font-size:0.78rem;" onclick="sendPhoneFarmAction('key', {{ key: 'recents' }})">🔲 Apps</button>
        <button class="btn" style="background:#0d1526; border-color:#1e293b; padding:9px 4px; font-size:0.78rem;" onclick="sendPhoneFarmAction('key', {{ key: 'notifications' }})">🔔 Notif</button>
        <button class="btn" style="background:#0d1526; border-color:#1e293b; padding:9px 4px; font-size:0.78rem;" onclick="sendPhoneFarmAction('key', {{ key: 'lock' }})">🔒 Lock</button>
      </div>

      <!-- Directional Swipes / Scroll -->
      <div style="font-size:0.72rem; color:#94a3b8; margin-bottom:4px; font-weight:600;">Directional Gestures & Swipes:</div>
      <div style="display:grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap:6px; margin-bottom:12px;">
        <button class="btn" style="background:#131d33; border-color:#223252; padding:10px 4px; font-size:0.78rem;" onclick="sendPhoneFarmAction('swipe', {{ x1: 500, y1: 1400, x2: 500, y2: 400, duration: 250 }})">⬆️ Swipe Up</button>
        <button class="btn" style="background:#131d33; border-color:#223252; padding:10px 4px; font-size:0.78rem;" onclick="sendPhoneFarmAction('swipe', {{ x1: 500, y1: 400, x2: 500, y2: 1400, duration: 250 }})">⬇️ Swipe Down</button>
        <button class="btn" style="background:#131d33; border-color:#223252; padding:10px 4px; font-size:0.78rem;" onclick="sendPhoneFarmAction('swipe', {{ x1: 800, y1: 800, x2: 200, y2: 800, duration: 250 }})">⬅️ Swipe Left</button>
        <button class="btn" style="background:#131d33; border-color:#223252; padding:10px 4px; font-size:0.78rem;" onclick="sendPhoneFarmAction('swipe', {{ x1: 200, y1: 800, x2: 800, y2: 800, duration: 250 }})">➡️ Swipe Right</button>
      </div>

      <!-- Text Typing Input -->
      <div style="font-size:0.72rem; color:#94a3b8; margin-bottom:4px; font-weight:600;">Broadcast Text Typing:</div>
      <div style="display:flex; gap:6px; margin-bottom:12px;">
        <input type="text" id="pfTextInput" class="input-bar" placeholder="Type text to type into active inputs...">
        <button class="btn" style="background:#4f46e5; border-color:#4338ca; padding:0 14px; font-size:0.8rem; font-weight:700; white-space:nowrap;" onclick="sendPhoneFarmType()">⌨️ Send Text</button>
      </div>

      <!-- App Launcher -->
      <div style="font-size:0.72rem; color:#94a3b8; margin-bottom:4px; font-weight:600;">Launch App on Devices:</div>
      <div style="display:flex; gap:6px; margin-bottom:6px;">
        <input type="text" id="pfAppPackage" class="input-bar" placeholder="Package name (e.g. com.android.chrome)...">
        <button class="btn" style="background:#0891b2; border-color:#0e7490; padding:0 14px; font-size:0.8rem; font-weight:700; white-space:nowrap;" onclick="sendPhoneFarmLaunchApp()">🚀 Launch App</button>
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:12px;">
        <span class="chip" onclick="document.getElementById('pfAppPackage').value='com.android.chrome'; sendPhoneFarmLaunchApp();">🌐 Chrome</span>
        <span class="chip" onclick="document.getElementById('pfAppPackage').value='com.google.android.youtube'; sendPhoneFarmLaunchApp();">🎬 YouTube</span>
        <span class="chip" onclick="document.getElementById('pfAppPackage').value='com.whatsapp'; sendPhoneFarmLaunchApp();">💬 WhatsApp</span>
        <span class="chip" onclick="document.getElementById('pfAppPackage').value='com.android.settings'; sendPhoneFarmLaunchApp();">⚙️ Settings</span>
      </div>

      <!-- Custom Precision Tap -->
      <div style="font-size:0.72rem; color:#94a3b8; margin-bottom:4px; font-weight:600;">Precision Coordinate Tap (X, Y):</div>
      <div style="display:flex; gap:6px;">
        <input type="number" id="pfTapX" class="input-bar" style="width:80px;" placeholder="X (500)" value="500">
        <input type="number" id="pfTapY" class="input-bar" style="width:80px;" placeholder="Y (1000)" value="1000">
        <button class="btn" style="flex:1; background:#059669; border-color:#047857; font-size:0.8rem; font-weight:700;" onclick="sendPhoneFarmTap()">👆 Perform Tap</button>
      </div>
    </div>

    <!-- Connected Devices Farm Grid -->
    <div class="card">
      <div class="card-title">
        <span>📋 Connected Devices Farm (<span id="pfCardCount">0</span>)</span>
      </div>
      <div id="pfDevicesList" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap:10px; margin-top:8px;">
        <div style="color:#64748b; font-size:0.82rem; grid-column: 1/-1; text-align:center; padding:20px;">
          Koi device connect nahi hai. Hotspot connect karke <strong>/setup</strong> se 20 KB APK install karein ya <strong>Auto-Scan Subnet</strong> dabayein.
        </div>
      </div>
    </div>

    <!-- Live Farm Command Log -->
    <div class="card">
      <div class="card-title">
        <span>📜 Farm Command Activity Log</span>
        <button class="chip" onclick="document.getElementById('pfActivityLog').innerHTML=''">Clear</button>
      </div>
      <div id="pfActivityLog" class="log-box" style="max-height:110px;">
        <div class="log-entry">[Ready] Phone Farm Controller initialized on port 9090.</div>
      </div>
    </div>
  </div><!-- END VIEW-MOBILE -->

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
    const el = document.getElementById("logBox");
    if (!el) return;
    const entry = document.createElement("div");
    entry.className = "log-entry";
    const time = new Date().toLocaleTimeString();
    entry.textContent = `[${{time}}] ${{msg}}`;
    el.prepend(entry);
  }}

  // -------------------------------------------------------------
  // Master View Switcher (Landing Hub vs PC Controller vs Mobile)
  // -------------------------------------------------------------
  function openView(mode) {{
    const hub = document.getElementById("view-hub");
    const pc = document.getElementById("view-pc");
    const mob = document.getElementById("view-mobile");

    if (mode === "pc") {{
      if (hub) hub.style.display = "none";
      if (mob) mob.style.display = "none";
      if (pc) pc.style.display = "block";
      try {{ history.replaceState(null, "", "#pc"); }} catch(e) {{}}
    }} else if (mode === "mobile") {{
      if (hub) hub.style.display = "none";
      if (pc) pc.style.display = "none";
      if (mob) mob.style.display = "block";
      try {{ history.replaceState(null, "", "#mobile"); }} catch(e) {{}}
      loadPhoneFarmDevices();
    }} else {{
      // default: hub
      if (pc) pc.style.display = "none";
      if (mob) mob.style.display = "none";
      if (hub) hub.style.display = "flex";
      try {{ history.replaceState(null, "", "#hub"); }} catch(e) {{}}
    }}
    window.scrollTo(0, 0);
  }}

  function initViewRouting() {{
    const hash = (location.hash || "").replace("#", "").toLowerCase();
    const urlParams = new URLSearchParams(window.location.search);
    const qMode = (urlParams.get("mode") || "").toLowerCase();

    if (qMode === "pc" || hash === "pc") {{
      openView("pc");
    }} else if (qMode === "mobile" || hash === "mobile") {{
      openView("mobile");
    }} else {{
      openView("hub");
    }}
  }}

  window.addEventListener("hashchange", () => {{
    const hash = (location.hash || "").replace("#", "").toLowerCase();
    if (hash === "pc") openView("pc");
    else if (hash === "mobile") openView("mobile");
    else openView("hub");
  }});

  function switchTab(tabId, el) {{
    if (tabId === "phonefarm") {{
      openView("mobile");
      return;
    }}
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

  // Live WebSocket Screen Streamer (Zero-Latency Canvas Engine)
  let screenStreaming = false;
  let screenWs = null;

  function startScreenWebSocket() {{
    if (screenWs) {{
      try {{ screenWs.close(); }} catch(e) {{}}
      screenWs = null;
    }}
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${{protocol}}//${{location.host}}/ws/screen?token=${{encodeURIComponent(currentDeviceToken)}}`;

    screenWs = new WebSocket(wsUrl);
    screenWs.binaryType = "blob";

    const canvas = document.getElementById("screenCanvas");
    const ctx = canvas ? canvas.getContext("2d") : null;
    const placeholder = document.getElementById("screenPlaceholder");

    screenWs.onopen = () => {{
      showToast("⚡ Live Socket Screen Connected!");
    }};

    screenWs.onmessage = async (event) => {{
      if (!screenStreaming) return;
      if (event.data instanceof Blob) {{
        try {{
          const bitmap = await createImageBitmap(event.data);
          if (canvas && ctx) {{
            if (canvas.width !== bitmap.width || canvas.height !== bitmap.height) {{
              canvas.width = bitmap.width;
              canvas.height = bitmap.height;
            }}
            ctx.drawImage(bitmap, 0, 0);
            bitmap.close();
            if (placeholder && placeholder.style.display !== "none") {{
              placeholder.style.display = "none";
            }}
          }}
        }} catch(err) {{
          const url = URL.createObjectURL(event.data);
          const img = document.getElementById("screenStreamImg");
          if (img) {{
            img.onload = () => URL.revokeObjectURL(url);
            img.src = url;
            img.style.display = "block";
          }}
        }}
      }}
    }};

    screenWs.onerror = () => {{
      if (screenStreaming) {{
        setTimeout(startScreenWebSocket, 1500);
      }}
    }};

    screenWs.onclose = () => {{
      if (screenStreaming) {{
        setTimeout(startScreenWebSocket, 1000);
      }}
    }};
  }}

  function toggleScreenStreamWeb() {{
    const canvas = document.getElementById("screenCanvas");
    const img = document.getElementById("screenStreamImg");
    const placeholder = document.getElementById("screenPlaceholder");
    const btn = document.getElementById("streamToggleBtn");
    const hint = document.getElementById("screenTouchHint");
    screenStreaming = !screenStreaming;

    if (screenStreaming) {{
      if (canvas) canvas.style.display = "block";
      if (placeholder) placeholder.style.display = "none";
      if (hint) hint.style.display = "block";
      btn.textContent = "⏹️ Stop Stream";
      btn.style.background = "#dc2626";
      showToast("⚡ Live Socket Stream Shuru!");

      startScreenWebSocket();
    }} else {{
      if (screenWs) {{
        try {{ screenWs.close(); }} catch(e) {{}}
        screenWs = null;
      }}
      if (canvas) canvas.style.display = "none";
      if (img) img.style.display = "none";
      if (placeholder) placeholder.style.display = "block";
      if (hint) hint.style.display = "none";
      btn.textContent = "▶️ Start Stream";
      btn.style.background = "#4f46e5";
      showToast("📺 Screen Stream Stopped");
    }}
  }}

  // Live PC Typing Functions
  function sendScreenLiveType() {{
    const input = document.getElementById("screenLiveTypeInput");
    if (!input) return;
    const txt = input.value;
    if (!txt) return;
    sendAction("type_text", {{ text: txt }});
    input.value = "";
    showToast("⌨️ Typed on PC: " + txt);
  }}

  function sendKeyStroke(k) {{
    sendAction("press_key", {{ key: k }});
    showToast("⌨️ Key: " + k.toUpperCase());
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

  function toggleVoiceNoteRecord() {{
    if (webMediaRecorder && webMediaRecorder.state === "recording") {{
      stopAndSendWebVoice();
    }} else {{
      startWebVoiceRecord();
    }}
  }}

  function cancelWebVoice() {{
    if (webMediaRecorder && webMediaRecorder.state === "recording") {{
      clearInterval(voiceRecTimer);
      webMediaRecorder.onstop = null;
      webMediaRecorder.stop();
      resetVoiceUI();
      showToast("❌ Recording cancel kar di gayi");
    }}
  }}

  function resetVoiceUI() {{
    const topBanner = document.getElementById("topVoiceRecBanner");
    if (topBanner) topBanner.style.display = "none";
    const mainBtn = document.getElementById("mainVoiceNoteBtn");
    if (mainBtn) {{
      mainBtn.innerHTML = '<span style="font-size:1.15rem;">🎙️</span> Voice Note Bhejein';
      mainBtn.style.background = "linear-gradient(135deg, #7c3aed, #4f46e5)";
    }}
    const startBtn = document.getElementById("startVoiceRecBtn");
    if (startBtn) startBtn.style.display = "flex";
    const activeBox = document.getElementById("recordingActiveBox");
    if (activeBox) activeBox.style.display = "none";
  }}

  async function startWebVoiceRecord() {{
    try {{
      const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
      voiceAudioChunks = [];
      webMediaRecorder = new MediaRecorder(stream);
      webMediaRecorder.ondataavailable = (e) => {{
        if (e.data.size > 0) voiceAudioChunks.push(e.data);
      }};
      webMediaRecorder.start();

      // Update both top card banner and button
      const topBanner = document.getElementById("topVoiceRecBanner");
      if (topBanner) topBanner.style.display = "flex";
      const mainBtn = document.getElementById("mainVoiceNoteBtn");
      if (mainBtn) {{
        mainBtn.innerHTML = '<span style="font-size:1.15rem;">⏹️</span> Tap to Send 🚀';
        mainBtn.style.background = "#dc2626";
      }}
      const startBtn = document.getElementById("startVoiceRecBtn");
      if (startBtn) startBtn.style.display = "none";
      const activeBox = document.getElementById("recordingActiveBox");
      if (activeBox) activeBox.style.display = "flex";

      voiceSecCount = 0;
      updateRecTimer();
      voiceRecTimer = setInterval(() => {{
        voiceSecCount++;
        updateRecTimer();
      }}, 1000);
      showToast("🎙️ Voice Note Recording shuru... Bolye!");
    }} catch(e) {{
      showToast("⚠️ Mic access error: " + e.message, true);
      showMicHelp();
    }}
  }}

  function updateRecTimer() {{
    const m = String(Math.floor(voiceSecCount / 60)).padStart(2, '0');
    const s = String(voiceSecCount % 60).padStart(2, '0');
    const timerStr = `🔴 RECORDING: ${{m}}:${{s}}`;
    const el1 = document.getElementById("recTimerText");
    if (el1) el1.textContent = timerStr;
    const el2 = document.getElementById("topRecTimer");
    if (el2) el2.textContent = timerStr;
  }}

  async function stopAndSendWebVoice() {{
    if (!webMediaRecorder || webMediaRecorder.state !== "recording") return;
    clearInterval(voiceRecTimer);
    showToast("📤 PC par Voice Note bheja ja raha hai...");

    webMediaRecorder.onstop = async () => {{
      const audioBlob = new Blob(voiceAudioChunks, {{ type: "audio/webm" }});
      const formData = new FormData();
      formData.append("file", audioBlob, `Voice_${{Date.now()}}.webm`);

      try {{
        const res = await authFetch("/api/voice/send?auto_play=true&auto_paste=true&press_enter=true", {{
          method: "POST",
          body: formData
        }});
        const data = await res.json();
        if (data.success) {{
          showToast("🚀 Voice Note PC par Paste & Send ho gaya!");
          loadPCFilesWeb();
        }} else {{
          showToast("❌ Failed: " + (data.message || ""), true);
        }}
      }} catch(err) {{
        showToast("❌ Upload error: " + err.message, true);
      }}

      resetVoiceUI();
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
          if (data.payload?.data?.titles) {{
            const rBox = document.getElementById("ytSeoResultsBox");
            const cBox = document.getElementById("ytSeoContent");
            if (rBox && cBox) {{
              rBox.style.display = "block";
              const d = data.payload.data;
              const nl = String.fromCharCode(10);
              const titlesStr = d.titles ? d.titles.map(t => "- " + t).join(nl) : "";
              const tagsStr = d.tags ? d.tags.join(", ") : "";
              cBox.textContent = "TITLES:" + nl + titlesStr + nl + nl + "TAGS:" + nl + tagsStr + nl + nl + "DESCRIPTION:" + nl + (d.description || "");
            }}
          }}
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

  function confirmAction(promptMsg, callback) {{
    if (confirm(promptMsg)) {{
      callback();
    }}
  }}

  let autoProceedState = false;
  function toggleAutoProceedUI() {{
    autoProceedState = !autoProceedState;
    sendAction("toggle_auto_proceed", {{ enabled: autoProceedState }});
    const btn = document.getElementById("autoProceedToggleBtn");
    if (btn) {{
      if (autoProceedState) {{
        btn.textContent = "ON 🟢";
        btn.style.background = "#15803d";
        btn.style.borderColor = "#22c55e";
        showToast("🤖 Auto-Proceed Loop ACTIVE! Submitting every 8s...");
      }} else {{
        btn.textContent = "OFF ⏸️";
        btn.style.background = "#1e293b";
        btn.style.borderColor = "#334155";
        showToast("⏸️ Auto-Proceed Loop PAUSED");
      }}
    }}
  }}

  function generateYtSeoWeb() {{
    const input = document.getElementById("ytSeoTopicInput");
    const topic = input ? input.value.trim() : "";
    if (!topic) {{
      showToast("Video topic likhein ya bolein", true);
      return;
    }}
    showToast("Generating Viral YouTube SEO package...");
    sendAction("generate_youtube_seo", {{ topic: topic }});
  }}

  let renderTimer = null;
  function setRenderTimerWeb() {{
    const minInput = document.getElementById("renderTimerMinutes");
    const mins = parseFloat(minInput ? minInput.value : 0);
    if (!mins || mins <= 0) {{
      showToast("Valid minutes darj karein", true);
      return;
    }}
    if (renderTimer) clearTimeout(renderTimer);
    const ms = mins * 60 * 1000;
    showToast(`⏱️ Alert Timer set for ${{mins}} minute(s)!`);
    renderTimer = setTimeout(() => {{
      sendAction("beep");
      showToast("🎉 Upload / Render Complete Alarm! 🔔", false);
      if (window.Notification && Notification.permission === "granted") {{
        new Notification("PC Controller: Task Complete! 🎉", {{
          body: `Aapka ${{mins}} minute ka upload/render complete ho chuka hai!`,
          icon: "/icon.png"
        }});
      }}
    }}, ms);
  }}

  async function askAiVisionWeb() {{
    const qInput = document.getElementById("visionQuestionInput");
    const q = qInput ? qInput.value.trim() : "Screen par kya chal raha hai?";
    showToast("👁️ Analyzing PC Screen with AI...");
    try {{
      const res = await authFetch("/api/ai/vision-ask", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ question: q }})
      }});
      const data = await res.json();
      if (data.success) {{
        const card = document.getElementById("visionResultCard");
        const b = document.getElementById("visionActiveWindowBadge");
        const a = document.getElementById("visionAnalysisText");
        const img = document.getElementById("visionImgPreview");
        if (card) card.style.display = "block";
        if (b) b.textContent = `WINDOW: ${{data.active_window}}`;
        if (a) a.textContent = data.analysis;
        if (img) img.src = data.screenshot_b64;
        showToast("✅ Screen Analyzed!");
      }} else {{
        showToast("Vision error: " + data.message, true);
      }}
    }} catch(err) {{
      showToast("Network error analyzing screen", true);
    }}
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

  // Mouse Speed & Sensitivity Controller
  let mouseSpeedMultiplier = parseFloat(localStorage.getItem("mouse_speed_mult") || "3.5");

  function cycleMouseSpeed() {{
    if (mouseSpeedMultiplier <= 2.2) {{
      mouseSpeedMultiplier = 3.5;
    }} else if (mouseSpeedMultiplier <= 3.5) {{
      mouseSpeedMultiplier = 5.0;
    }} else {{
      mouseSpeedMultiplier = 2.2;
    }}
    localStorage.setItem("mouse_speed_mult", mouseSpeedMultiplier);
    updateMouseSpeedPill();
    showToast("⚡ Mouse Speed: " + mouseSpeedMultiplier + "x");
  }}

  function updateMouseSpeedPill() {{
    const pill = document.getElementById("mouseSpeedPill");
    if (!pill) return;
    const label = mouseSpeedMultiplier >= 5.0 ? "⚡ Ultra (5x)" : (mouseSpeedMultiplier >= 3.5 ? "⚡ Fast (3.5x)" : "🎯 Normal (2.2x)");
    pill.textContent = "Speed: " + label;
  }}
  updateMouseSpeedPill();


  // 1-Tap Direct Screenshot Capture & Download
  async function quickCaptureAndDownloadWeb() {{
    const btn = document.getElementById("quickScreenDlBtn");
    if (btn) btn.innerHTML = "<span>⏳</span> <span>Capturing Screenshot...</span>";
    showToast("📸 Capturing & Downloading Screenshot...");
    try {{
      const url = "/api/screen/screenshot?token=" + encodeURIComponent(currentDeviceToken) + "&t=" + Date.now();
      const res = await fetch(url);
      if (!res.ok) throw new Error("Capture failed");
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = blobUrl;
      a.download = "pc_screen_" + Date.now() + ".jpg";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 10000);
      showToast("✅ Screenshot Downloaded to Phone!");
    }} catch(e) {{
      showToast("❌ Screenshot download error", true);
    }} finally {{
      if (btn) btn.innerHTML = "<span>📸</span> <span>Capture Screen & Direct Download</span>";
    }}
  }}

  // Ultra-Responsive 70 FPS Touchpad with Hardware Delta Injection & Dynamic Acceleration
  function bindTouchpad(el) {{
    if (!el) return;
    let tLastX = 0, tLastY = 0, tAccumX = 0, tAccumY = 0;
    let tIsMoving = false, tMoveThrottle = 0;
    let tStartX = 0, tStartY = 0, tStartTime = 0;
    let tHasMoved = false, tLastTapTime = 0, tTapTimer = null;

    el.addEventListener("touchstart", (e) => {{
      const touch = e.touches[0];
      tLastX = touch.clientX;
      tLastY = touch.clientY;
      tStartX = touch.clientX;
      tStartY = touch.clientY;
      tStartTime = Date.now();
      tHasMoved = false;
      tAccumX = 0;
      tAccumY = 0;
      tIsMoving = true;
      el.classList.add("active");
    }}, {{ passive: false }});

    el.addEventListener("touchmove", (e) => {{
      if (!tIsMoving) return;
      e.preventDefault();
      const touch = e.touches[0];
      const dist = Math.hypot(touch.clientX - tStartX, touch.clientY - tStartY);
      if (dist > 6) {{
        tHasMoved = true;
        if (tTapTimer) {{
          clearTimeout(tTapTimer);
          tTapTimer = null;
        }}
      }}

      const deltaX = (touch.clientX - tLastX);
      const deltaY = (touch.clientY - tLastY);
      tAccumX += deltaX;
      tAccumY += deltaY;
      tLastX = touch.clientX;
      tLastY = touch.clientY;

      const now = Date.now();
      if (now - tMoveThrottle > 14) {{
        tMoveThrottle = now;
        const stepDist = Math.hypot(deltaX, deltaY);
        // Dynamic acceleration boost for quick flicks vs slow precision
        const accel = stepDist > 6 ? 1.45 : 1.0;
        const sendDx = Math.round(tAccumX * mouseSpeedMultiplier * accel);
        const sendDy = Math.round(tAccumY * mouseSpeedMultiplier * accel);
        tAccumX = 0;
        tAccumY = 0;
        if (ws && ws.readyState === WebSocket.OPEN && (sendDx !== 0 || sendDy !== 0)) {{
          ws.send(JSON.stringify({{
            type: "action",
            payload: {{ action: "mouse_move", dx: sendDx, dy: sendDy }}
          }}));
        }}
      }}
    }}, {{ passive: false }});

    el.addEventListener("touchend", () => {{
      tIsMoving = false;
      el.classList.remove("active");

      const touchDuration = Date.now() - tStartTime;
      if (!tHasMoved && touchDuration < 280) {{
        const now = Date.now();
        if (now - tLastTapTime < 320) {{
          if (tTapTimer) {{
            clearTimeout(tTapTimer);
            tTapTimer = null;
          }}
          tLastTapTime = 0;
          sendMouseClick("right");
        }} else {{
          tLastTapTime = now;
          tTapTimer = setTimeout(() => {{
            sendMouseClick("left");
            tTapTimer = null;
          }}, 240);
        }}
      }}
    }});
  }}

  // Initialize both touchpads
  bindTouchpad(document.getElementById("touchpad"));
  bindTouchpad(document.getElementById("screenTouchpad"));

  // Interactive Live Screen direct touch & drag controller
  function initScreenDirectTouch() {{
    const container = document.getElementById("screenStreamContainer");
    const img = document.getElementById("screenStreamImg");
    const badge = document.getElementById("screenCoordBadge");
    if (!container || !img) return;

    let sLastX = 0, sLastY = 0, sAccumX = 0, sAccumY = 0;
    let sIsMoving = false, sMoveThrottle = 0;
    let sStartX = 0, sStartY = 0, sStartTime = 0;
    let sHasMoved = false, sLastTapTime = 0, sTapTimer = null;

    container.addEventListener("touchstart", (e) => {{
      if (!screenStreaming) return;
      const touch = e.touches[0];
      sLastX = touch.clientX;
      sLastY = touch.clientY;
      sStartX = touch.clientX;
      sStartY = touch.clientY;
      sStartTime = Date.now();
      sHasMoved = false;
      sAccumX = 0;
      sAccumY = 0;
      sIsMoving = true;
      container.style.borderColor = "var(--accent)";
    }}, {{ passive: false }});

    container.addEventListener("touchmove", (e) => {{
      if (!sIsMoving || !screenStreaming) return;
      e.preventDefault();
      const touch = e.touches[0];
      const dist = Math.hypot(touch.clientX - sStartX, touch.clientY - sStartY);
      if (dist > 6) {{
        sHasMoved = true;
        if (sTapTimer) {{
          clearTimeout(sTapTimer);
          sTapTimer = null;
        }}
      }}

      const deltaX = (touch.clientX - sLastX);
      const deltaY = (touch.clientY - sLastY);
      sAccumX += deltaX;
      sAccumY += deltaY;
      sLastX = touch.clientX;
      sLastY = touch.clientY;

      const now = Date.now();
      if (now - sMoveThrottle > 14) {{
        sMoveThrottle = now;
        const stepDist = Math.hypot(deltaX, deltaY);
        const accel = stepDist > 6 ? 1.45 : 1.0;
        const sendDx = Math.round(sAccumX * mouseSpeedMultiplier * accel);
        const sendDy = Math.round(sAccumY * mouseSpeedMultiplier * accel);
        sAccumX = 0;
        sAccumY = 0;
        if (ws && ws.readyState === WebSocket.OPEN && (sendDx !== 0 || sendDy !== 0)) {{
          ws.send(JSON.stringify({{
            type: "action",
            payload: {{ action: "mouse_move", dx: sendDx, dy: sendDy }}
          }}));
        }}
      }}
    }}, {{ passive: false }});

    container.addEventListener("touchend", () => {{
      if (!sIsMoving) return;
      sIsMoving = false;
      container.style.borderColor = "#1e293b";

      const touchDuration = Date.now() - sStartTime;
      // Direct Tap on Screen: tap coordinate maps to PC screen coordinate
      if (!sHasMoved && touchDuration < 300) {{
        const rect = img.getBoundingClientRect();
        const normX = Math.max(0, Math.min(1, (sStartX - rect.left) / (rect.width || 1)));
        const normY = Math.max(0, Math.min(1, (sStartY - rect.top) / (rect.height || 1)));

        const now = Date.now();
        if (now - sLastTapTime < 320) {{
          if (sTapTimer) {{
            clearTimeout(sTapTimer);
            sTapTimer = null;
          }}
          sLastTapTime = 0;
          if (ws && ws.readyState === WebSocket.OPEN) {{
            ws.send(JSON.stringify({{
              type: "action",
              payload: {{ action: "mouse_click_at", x: normX, y: normY, button: "right" }}
            }}));
            if (badge) badge.textContent = `Right Click @ ${{Math.round(normX*100)}}%,${{Math.round(normY*100)}}%`;
            if (navigator.vibrate) navigator.vibrate(25);
          }}
        }} else {{
          sLastTapTime = now;
          sTapTimer = setTimeout(() => {{
            if (ws && ws.readyState === WebSocket.OPEN) {{
              ws.send(JSON.stringify({{
                type: "action",
                payload: {{ action: "mouse_click_at", x: normX, y: normY, button: "left" }}
              }}));
              if (badge) badge.textContent = `Click @ ${{Math.round(normX*100)}}%,${{Math.round(normY*100)}}%`;
              if (navigator.vibrate) navigator.vibrate(25);
            }}
            sTapTimer = null;
          }}, 240);
        }}
      }}
    }});
  }}
  initScreenDirectTouch();

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

  // -------------------------------------------------------------
  // Phone Farm (100+ Devices) Management & Remote Control
  // -------------------------------------------------------------
  let pfPhones = [];

  async function loadPhoneFarmDevices() {{
    try {{
      const res = await authFetch("/api/phones");
      const data = await res.json();
      pfPhones = data.phones || [];

      const totalEl = document.getElementById("pfTotalCount");
      const onlineEl = document.getElementById("pfOnlineCount");
      const cardEl = document.getElementById("pfCardCount");
      if (totalEl) totalEl.textContent = data.total || 0;
      if (onlineEl) onlineEl.textContent = data.online_count || 0;
      if (cardEl) cardEl.textContent = data.total || 0;

      // Update target selector
      const sel = document.getElementById("pfTargetSelect");
      if (sel) {{
        const curVal = sel.value;
        sel.innerHTML = '<option value="all">⚡ ALL PHONES (Broadcast to 100+ Devices Simultaneously)</option>';
        pfPhones.forEach(p => {{
          const opt = document.createElement("option");
          opt.value = p.ip;
          opt.textContent = `📱 ${{p.model}} (${{p.ip}}) - Bat: ${{p.battery}}%`;
          sel.appendChild(opt);
        }});
        if (curVal) sel.value = curVal;
      }}

      // Render device cards
      renderPhoneFarmCards();
    }} catch(e) {{
      console.error("Failed to load phone farm devices:", e);
    }}
  }}

  function renderPhoneFarmCards() {{
    const container = document.getElementById("pfDevicesList");
    if (!container) return;
    if (pfPhones.length === 0) {{
      container.innerHTML = `
        <div style="color:#64748b; font-size:0.82rem; grid-column: 1/-1; text-align:center; padding:20px;">
          Koi device connect nahi hai. Hotspot connect karke <strong>/setup</strong> se 20 KB APK install karein ya <strong>Auto-Scan Subnet</strong> dabayein.
        </div>`;
      return;
    }}

    container.innerHTML = pfPhones.map(p => {{
      const isOnline = p.is_online;
      const statusBadge = isOnline ? 
        '<span style="background:rgba(16,185,129,0.2); color:#34d399; padding:2px 8px; border-radius:10px; font-size:0.7rem; font-weight:700;">🟢 ONLINE</span>' :
        '<span style="background:rgba(239,68,68,0.2); color:#f87171; padding:2px 8px; border-radius:10px; font-size:0.7rem; font-weight:700;">⏸️ IDLE</span>';

      return `
        <div style="background:#0b1120; border:1px solid ${{isOnline ? '#1f2d47' : '#334155'}}; border-radius:12px; padding:12px; display:flex; flex-direction:column; gap:8px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="color:#f1f5f9; font-size:0.86rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">📱 ${{p.model || 'Android Phone'}}</strong>
            ${{statusBadge}}
          </div>
          <div style="display:flex; justify-content:space-between; font-size:0.74rem; color:#94a3b8;">
            <span>IP: <strong style="color:#38bdf8;">${{p.ip}}</strong>:9090</span>
            <span>🔋 ${{p.battery}}% | 📐 ${{p.width}}x${{p.height}}</span>
          </div>
          <div style="display:grid; grid-template-columns: repeat(6, 1fr) auto; gap:4px; margin-top:4px;">
            <button class="btn" style="background:#0c4a6e; border-color:#0284c7; color:#38bdf8; padding:6px 2px; font-size:0.72rem; font-weight:700;" title="Toggle Live Screen View" onclick="togglePhoneScreenBox('${{p.ip}}')">📺 Screen</button>
            <button class="btn" style="background:#131c2e; border-color:#1e293b; padding:6px 2px; font-size:0.72rem;" title="Home" onclick="sendIndividualPhoneAction('${{p.ip}}', 'key', {{ key: 'home' }})">🏠</button>
            <button class="btn" style="background:#131c2e; border-color:#1e293b; padding:6px 2px; font-size:0.72rem;" title="Back" onclick="sendIndividualPhoneAction('${{p.ip}}', 'key', {{ key: 'back' }})">◀</button>
            <button class="btn" style="background:#131c2e; border-color:#1e293b; padding:6px 2px; font-size:0.72rem;" title="Swipe Up" onclick="sendIndividualPhoneAction('${{p.ip}}', 'swipe', {{ x1: 500, y1: 1400, x2: 500, y2: 400, duration: 250 }})">⬆️</button>
            <button class="btn" style="background:#131c2e; border-color:#1e293b; padding:6px 2px; font-size:0.72rem;" title="Swipe Down" onclick="sendIndividualPhoneAction('${{p.ip}}', 'swipe', {{ x1: 500, y1: 400, x2: 500, y2: 1400, duration: 250 }})">⬇️</button>
            <button class="btn" style="background:#131c2e; border-color:#1e293b; padding:6px 2px; font-size:0.72rem;" title="Tap Center" onclick="sendIndividualPhoneAction('${{p.ip}}', 'tap', {{ x: 500, y: 1000 }})">👆</button>
            <button class="btn" style="background:#450a0a; border-color:#7f1d1d; color:#fca5a5; padding:6px 6px; font-size:0.72rem;" title="Remove" onclick="deletePhoneFarmDevice('${{p.ip}}')">🗑️</button>
          </div>

          <!-- Live Screen Preview Box -->
          <div id="pfScreenBox-${{p.ip}}" style="display:none; margin-top:8px; background:#020617; border:1px solid #1e293b; border-radius:12px; padding:10px; text-align:center;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              <span style="font-size:0.75rem; color:#38bdf8; font-weight:700;">📺 Live Screen (${{p.ip}})</span>
              <div style="display:flex; gap:4px;">
                <button class="chip" style="padding:2px 8px; font-size:0.7rem;" onclick="refreshPhoneScreen('${{p.ip}}')">🔄 Refresh</button>
                <button id="pfAutoBtn-${{p.ip}}" class="chip" style="padding:2px 8px; font-size:0.7rem; color:#34d399;" onclick="toggleAutoPhoneScreen('${{p.ip}}')">⚡ Stream: OFF</button>
              </div>
            </div>
            <div style="position:relative; display:inline-block; max-width:240px; width:100%;">
              <img id="pfScreenImg-${{p.ip}}" src="/api/phones/${{p.ip}}/screen" style="width:100%; height:auto; border-radius:10px; border:1.5px solid #38bdf8; cursor:crosshair; display:block; box-shadow:0 6px 20px rgba(0,0,0,0.7);" onclick="onPhoneScreenTap(event, '${{p.ip}}', ${{p.width || 720}}, ${{p.height || 1600}})" alt="Live Screen">
            </div>
            <div style="font-size:0.68rem; color:#64748b; margin-top:5px;">
              👆 Screen par jahan tap karenge, mobile me wahan click hoga!
            </div>
          </div>
        </div>
      `;
    }}).join("");
  }}

  function logPhoneFarm(msg) {{
    const el = document.getElementById("pfActivityLog");
    if (!el) return;
    const time = new Date().toLocaleTimeString();
    const entry = document.createElement("div");
    entry.className = "log-entry";
    entry.textContent = `[${{time}}] ${{msg}}`;
    el.prepend(entry);
  }}

  async function scanPhoneFarmSubnet() {{
    const btn = document.getElementById("pfScanBtn");
    if (btn) {{
      btn.disabled = true;
      btn.textContent = "⏳ Scanning...";
    }}
    showToast("🔍 Subnet scan shuru ho gaya hai (port 9090)...");
    logPhoneFarm("Starting subnet scan on port 9090 across 254 IPs...");

    try {{
      const res = await authFetch("/api/phones/scan", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{}})
      }});
      const data = await res.json();
      logPhoneFarm(`Scan finished! Found ${{data.discovered}} phone(s) on subnet ${{data.subnet}}.`);
      showToast(`✅ Scan Complete! ${{data.discovered}} phone(s) mile.`);
      await loadPhoneFarmDevices();
    }} catch(e) {{
      logPhoneFarm(`Scan failed: ${{e.message}}`);
      showToast("⚠️ Subnet scan me masla aaya", true);
    }} finally {{
      if (btn) {{
        btn.disabled = false;
        btn.textContent = "🔍 Auto-Scan Subnet";
      }}
    }}
  }}

  async function addPhoneFarmManualIp() {{
    const ipInput = document.getElementById("pfManualIp");
    const ip = ipInput.value.trim();
    if (!ip) return showToast("⚠️ IP address likhein", true);

    logPhoneFarm(`Adding IP: ${{ip}}...`);
    try {{
      const res = await authFetch("/api/phones/add", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ ip: ip, port: 9090 }})
      }});
      const data = await res.json();
      if (data.success) {{
        showToast(`📱 Phone ${{ip}} add hogaya!`);
        logPhoneFarm(`Device ${{ip}} (${{data.phone.model}}) registered successfully.`);
        ipInput.value = "";
        await loadPhoneFarmDevices();
      }} else {{
        showToast("⚠️ Device connect nahi hui", true);
      }}
    }} catch(e) {{
      showToast(`⚠️ Error: ${{e.message}}`, true);
    }}
  }}

  async function deletePhoneFarmDevice(ip) {{
    if (!confirm(`Phone ${{ip}} ko farm list se hatana chahte hain?`)) return;
    try {{
      await authFetch(`/api/phones/${{ip}}`, {{ method: "DELETE" }});
      showToast(`Device ${{ip}} removed.`);
      logPhoneFarm(`Removed ${{ip}} from farm.`);
      await loadPhoneFarmDevices();
    }} catch(e) {{
      showToast(`Error removing: ${{e.message}}`, true);
    }}
  }}

  async function sendPhoneFarmAction(action, extraParams = {{}}) {{
    const target = document.getElementById("pfTargetSelect").value || "all";
    const payload = {{ target: target, action: action, ...extraParams }};

    const targetDesc = target === "all" ? "ALL 100+ PHONES" : target;
    logPhoneFarm(`Dispatching [${{action.toUpperCase()}}] to ${{targetDesc}}...`);

    try {{
      const res = await authFetch("/api/phones/control", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(payload)
      }});
      const data = await res.json();
      if (data.success) {{
        if (data.broadcast) {{
          logPhoneFarm(`✅ Broadcast [${{action}}] sent to ${{data.count}} devices!`);
          showToast(`⚡ Action '${{action}}' sent to ${{data.count}} phones!`);
        }} else {{
          logPhoneFarm(`✅ Action [${{action}}] executed on ${{target}}!`);
          showToast(`📱 Action '${{action}}' executed on ${{target}}!`);
        }}
      }} else {{
        logPhoneFarm(`⚠️ Failed: ${{data.message || 'Error'}}`);
        showToast(`⚠️ ${{data.message || 'Command failed'}}`, true);
      }}
    }} catch(e) {{
      logPhoneFarm(`Error sending command: ${{e.message}}`);
      showToast(`⚠️ Command error: ${{e.message}}`, true);
    }}
  }}

  async function sendIndividualPhoneAction(ip, action, extraParams = {{}}) {{
    const payload = {{ target: ip, action: action, ...extraParams }};
    logPhoneFarm(`Dispatching [${{action.toUpperCase()}}] to ${{ip}}...`);
    try {{
      const res = await authFetch("/api/phones/control", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(payload)
      }});
      const data = await res.json();
      if (data.success) {{
        logPhoneFarm(`✅ [${{action}}] on ${{ip}} OK`);
        showToast(`📱 ${{ip}}: ${{action}} OK`);
      }} else {{
        showToast(`⚠️ ${{ip}} error`, true);
      }}
    }} catch(e) {{
      showToast(`⚠️ ${{e.message}}`, true);
    }}
  }}

  function sendPhoneFarmType() {{
    const input = document.getElementById("pfTextInput");
    const text = input.value;
    if (!text) return showToast("⚠️ Pehle text likhein", true);
    sendPhoneFarmAction("type", {{ text: text }});
    input.value = "";
  }}

  function sendPhoneFarmLaunchApp() {{
    const input = document.getElementById("pfAppPackage");
    const pkg = input.value.trim();
    if (!pkg) return showToast("⚠️ Package name likhein", true);
    sendPhoneFarmAction("open_app", {{ package: pkg }});
  }}

  function sendPhoneFarmTap() {{
    const x = parseInt(document.getElementById("pfTapX").value || "500", 10);
    const y = parseInt(document.getElementById("pfTapY").value || "1000", 10);
    sendPhoneFarmAction("tap", {{ x: x, y: y }});
  }}

  function toggleQrModal() {{
    const m = document.getElementById("pfQrModal");
    if (!m) return;
    m.style.display = m.style.display === "flex" ? "none" : "flex";
  }}

  // -------------------------------------------------------------
  // Interactive Phone Screen Mirroring & Tap Stream Engine
  // -------------------------------------------------------------
  const pfScreenIntervals = {{}};

  function togglePhoneScreenBox(ip) {{
    const box = document.getElementById("pfScreenBox-" + ip);
    if (!box) return;
    const isHidden = box.style.display === "none";
    box.style.display = isHidden ? "block" : "none";
    if (isHidden) {{
      refreshPhoneScreen(ip);
    }} else {{
      stopAutoPhoneScreen(ip);
    }}
  }}

  function refreshPhoneScreen(ip) {{
    const img = document.getElementById("pfScreenImg-" + ip);
    if (img) {{
      img.src = `/api/phones/${{ip}}/screen?t=` + Date.now();
    }}
  }}

  function toggleAutoPhoneScreen(ip) {{
    const btn = document.getElementById("pfAutoBtn-" + ip);
    if (pfScreenIntervals[ip]) {{
      stopAutoPhoneScreen(ip);
      if (btn) {{
        btn.textContent = "⚡ Stream: OFF";
        btn.style.color = "#94a3b8";
      }}
      showToast(`Stream paused for ${{ip}}`);
    }} else {{
      pfScreenIntervals[ip] = setInterval(() => refreshPhoneScreen(ip), 1200);
      if (btn) {{
        btn.textContent = "⚡ Stream: ON 🟢";
        btn.style.color = "#34d399";
      }}
      showToast(`⚡ Live Stream started for ${{ip}}`);
      refreshPhoneScreen(ip);
    }}
  }}

  function stopAutoPhoneScreen(ip) {{
    if (pfScreenIntervals[ip]) {{
      clearInterval(pfScreenIntervals[ip]);
      delete pfScreenIntervals[ip];
    }}
  }}

  function onPhoneScreenTap(evt, ip, nativeW, nativeH) {{
    const rect = evt.target.getBoundingClientRect();
    const clickX = evt.clientX - rect.left;
    const clickY = evt.clientY - rect.top;

    const pctX = clickX / rect.width;
    const pctY = clickY / rect.height;

    const targetX = Math.round(pctX * (nativeW || 720));
    const targetY = Math.round(pctY * (nativeH || 1600));

    logPhoneFarm(`👆 Interactive Screen Tap on ${{ip}} at (${{targetX}}, ${{targetY}})`);
    showToast(`👆 Tap (${{targetX}}, ${{targetY}}) on ${{ip}}`);
    sendIndividualPhoneAction(ip, "tap", {{ x: targetX, y: targetY }});

    setTimeout(() => refreshPhoneScreen(ip), 450);
  }}

  connectWebSocket();
  initViewRouting();
</script>

</body>
</html>
"""
