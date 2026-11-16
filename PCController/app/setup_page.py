def get_setup_html(client_ip: str, local_ip: str, port: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>📱 Personal AI - Phone Farm Agent Setup</title>
  <style>
    :root {{
      --bg: #090d16;
      --card: #131c2e;
      --border: #1f2d47;
      --accent: #10b981;
      --accent-hover: #059669;
      --text: #f8fafc;
      --muted: #94a3b8;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    body {{
      background: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 16px;
    }}
    .container {{
      max-width: 460px;
      width: 100%;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 26px 20px;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
      text-align: center;
    }}
    .icon-badge {{
      width: 64px;
      height: 64px;
      background: rgba(16, 185, 129, 0.15);
      border: 1.5px solid var(--accent);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2rem;
      margin: 0 auto 16px;
      box-shadow: 0 0 20px rgba(16, 185, 129, 0.25);
    }}
    h1 {{
      font-size: 1.35rem;
      font-weight: 800;
      margin-bottom: 6px;
      color: #fff;
    }}
    p.subtitle {{
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 18px;
    }}
    .info-bar {{
      display: flex;
      justify-content: space-between;
      background: #0b1120;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 9px 14px;
      margin-bottom: 20px;
      font-size: 0.78rem;
    }}
    .info-bar span {{
      color: var(--muted);
    }}
    .info-bar strong {{
      color: #38bdf8;
    }}
    .download-btn {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 100%;
      padding: 15px;
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: #fff;
      font-size: 1rem;
      font-weight: 800;
      text-decoration: none;
      border-radius: 12px;
      border: none;
      cursor: pointer;
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
      margin-bottom: 22px;
      transition: transform 0.1s, box-shadow 0.1s;
    }}
    .download-btn:active {{
      transform: scale(0.98);
      box-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
    }}
    .size-tag {{
      background: rgba(255, 255, 255, 0.2);
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
    }}
    .steps {{
      text-align: left;
      background: #0b1120;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 20px;
    }}
    .step-item {{
      display: flex;
      gap: 12px;
      margin-bottom: 14px;
    }}
    .step-item:last-child {{
      margin-bottom: 0;
    }}
    .step-num {{
      width: 26px;
      height: 26px;
      border-radius: 50%;
      background: #1f2d47;
      color: #38bdf8;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 0.8rem;
      flex-shrink: 0;
    }}
    .step-text strong {{
      display: block;
      color: #f1f5f9;
      font-size: 0.85rem;
      margin-bottom: 2px;
    }}
    .step-text p {{
      color: var(--muted);
      font-size: 0.78rem;
      line-height: 1.35;
    }}
    .features {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 18px;
    }}
    .feat {{
      background: #0d1526;
      border: 1px solid #1a273f;
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 0.72rem;
      color: #a7f3d0;
      text-align: center;
    }}
    .footer-note {{
      font-size: 0.72rem;
      color: #64748b;
      line-height: 1.4;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="icon-badge">📱</div>
    <h1>Personal AI Phone Farm</h1>
    <p class="subtitle">Ultra-Lightweight Background Agent</p>

    <div class="info-bar">
      <span>Your IP: <strong>{client_ip}</strong></span>
      <span>Master: <strong>{local_ip}:{port}</strong></span>
    </div>

    <a href="/agent.apk" class="download-btn">
      <span>📥 Download Agent APK</span>
      <span class="size-tag">~20 KB</span>
    </a>

    <div class="features">
      <div class="feat">⚡ 20 KB Ultra Tiny</div>
      <div class="feat">🔄 Auto Boot Survive</div>
      <div class="feat">🔋 0% Battery Drain</div>
      <div class="feat">🌐 Stateless Port 9090</div>
    </div>

    <!-- Offline QR Code for direct camera scan -->
    <div style="background:#0b1120; border:1px solid var(--border); border-radius:12px; padding:12px; margin-bottom:18px;">
      <div style="font-size:0.75rem; color:var(--muted); margin-bottom:8px;">Kisi aur phone k Camera se scan karke download karein:</div>
      <img src="/api/setup_qr" style="width:130px; height:130px; border-radius:8px; background:#fff; padding:6px; display:block; margin:0 auto;" alt="Setup QR">
    </div>

    <div class="steps">
      <div class="step-item">
        <div class="step-num">1</div>
        <div class="step-text">
          <strong>Download & Install (1 Sec)</strong>
          <p>Upar diye button se 20 KB ki APK download karke open karein aur Install karein.</p>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">2</div>
        <div class="step-text">
          <strong>Enable Remote Service</strong>
          <p>App khol kar 'Enable Remote Service' tap karein -> Accessibility me 'PersonalAI Remote Agent' ko ON kar dein.</p>
        </div>
      </div>
      <div class="step-item">
        <div class="step-num">3</div>
        <div class="step-text">
          <strong>Sab Set Hai! (24/7 Active)</strong>
          <p>Mobile shutdown ya reboot hone par bhi service khud restart hogi aur control active rahega.</p>
        </div>
      </div>
    </div>

    <div class="footer-note">
      Connected via Hotspot / Local Network • Personal AI Hub v2.1
    </div>
  </div>
</body>
</html>
"""
