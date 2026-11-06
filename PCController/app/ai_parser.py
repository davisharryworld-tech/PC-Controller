import re
import threading
import time
import urllib.parse
from app.actions import (
    open_url, launch_app, close_app_by_name, safe_close_window,
    volume_up, volume_down, volume_mute, media_play_pause,
    media_next, media_prev, trigger_hotkey, lock_screen,
    type_text, type_in_notepad, play_youtube_video
)
from app.contacts_manager import set_contact, load_contacts
from app.logger import logger
from app.whatsapp_sender import (
    send_whatsapp_message, open_whatsapp_chat,
    type_whatsapp_message, send_active_message
)

def interpret_and_execute_nl(query: str) -> dict:
    """
    Intelligently parses and executes human natural language instructions
    supporting English, Urdu, and Roman Urdu.
    Returns dictionary with: success, message, speak, and action.
    """
    raw = query.strip()
    low = raw.lower()

    logger.info(f"Natural Language Intent Parsing: '{raw}'")

    # -------------------------------------------------------------
    # 0. App & Web Priority Shortcuts (Prevent collisions with WhatsApp)
    # e.g., "open chat gpt" or "open chatgpt" while in WhatsApp must open ChatGPT in Chrome!
    # -------------------------------------------------------------
    # 0A. ChatGPT / AI priority (supports English, Roman Urdu, Urdu script, and speech mishearings)
    chatgpt_terms = [
        "chatgpt", "chat gpt", "charge gpt", "chart gpt", "chad gpt", "chat gbt", "church wiki",
        "چیٹ جی پی ٹی", "جیٹ جی پی ٹی", "جی پی ٹی", "اوپن چیٹ جی پی ٹی", "اوپن جیٹ جی پی ٹی",
        "open ai", "openai"
    ]
    if any(term in low for term in chatgpt_terms):
        msg = open_url("https://chatgpt.com")
        return {
            "success": True,
            "message": "ChatGPT open ho chuka hai! 🤖",
            "action": "open_chatgpt"
        }

    # 0B. YouTube standalone open (if not a song/search query)
    yt_open_terms = [
        "open youtube", "open yt", "youtube kholo", "youtube open karo", "youtube open",
        "یوٹیوب کھولو", "اوپن یوٹیوب", "یوٹیوب اوپن کرو"
    ]
    if any(term in low for term in yt_open_terms) or (low in ["youtube", "yt", "یوٹیوب"] and not any(w in low for w in ["play", "chalao", "suno", "gana", "song"])):
        msg = open_url("https://www.youtube.com")
        return {
            "success": True,
            "message": "YouTube open ho chuka hai! ▶️",
            "action": "open_youtube"
        }

    # 0C. Chrome / Browser standalone open
    chrome_open_terms = [
        "open chrome", "open browser", "open google", "chrome kholo", "browser kholo", "google kholo",
        "اوپن کروم", "کروم کھولو", "اوپن گوگل", "گوگل کھولو"
    ]
    if any(term in low for term in chrome_open_terms) or low in ["chrome", "google", "browser", "کروم", "گوگل"]:
        msg = open_url("https://www.google.com")
        return {
            "success": True,
            "message": "Google Chrome open ho chuka hai! 🌐",
            "action": "open_browser"
        }

    # 0D. WhatsApp standalone open
    wa_open_terms = [
        "open whatsapp", "whatsapp kholo", "open wa", "wa kholo", "whatsapp open karo",
        "اوپن واٹس ایپ", "واٹس ایپ کھولو", "واٹس ایپ اوپن کرو"
    ]
    if any(term in low for term in wa_open_terms) or low in ["whatsapp", "wa", "واٹس ایپ"]:
        msg = open_url("https://web.whatsapp.com")
        return {
            "success": True,
            "message": "WhatsApp open ho chuka hai! 💬",
            "action": "open_whatsapp"
        }

    # -------------------------------------------------------------
    # 1. WhatsApp Conversational Workflow:
    #   Step A: Open chat: "ali ki chat open karo" / "open my number chat"
    #   Step B: Type message: "send message hi" / "message hello" / "likho salam"
    #   Step C: Send it: "send it" / "send" / "bhejo"
    # -------------------------------------------------------------
    # 1A. Dispatch currently typed message ("send it", "bhejo", "send karo")
    send_it_match = re.search(r"^(?:send\s+it(?:\s+now)?|send(?:\s+this)?|send\s+kar\s*do|send\s+karo|bhejo|bhej\s*do|سینڈ\s*کرو|بھیجو|بھیج\s*دو)$", low)
    if send_it_match:
        return send_active_message()

    # 1B. Check save contact command (supports multi-word names like "my number")
    save_contact_match = re.search(r"(?:save|add)\s+contact\s+(.+?)\s+([0-9\+]+)$", low)
    if save_contact_match:
        c_name = save_contact_match.group(1).strip()
        c_phone = save_contact_match.group(2).strip()
        set_contact(c_name, c_phone)
        return {
            "success": True,
            "message": f"Contact '{c_name}' saved with number {c_phone}",
            "speak": f"Contact {c_name} save ho chuka hai",
            "action": "save_contact"
        }

    # 1C. "type <msg> and send it to <recipient>" (e.g. "type how are you and send it to ali")
    m_type_and_send_to = re.search(r"^(?:type|write|likho)\s+(.+?)\s+(?:and\s+send\s+(?:it\s+)?to|aur\s+(?:send\s+karo|bhejo)\s+)\s*(.+?)(?:\s+ko)?$", raw, re.IGNORECASE)
    if m_type_and_send_to:
        msg_text = m_type_and_send_to.group(1).strip()
        rec = m_type_and_send_to.group(2).strip()
        rec = re.sub(r"\s+ko$", "", rec, flags=re.IGNORECASE).strip()
        if rec and msg_text:
            open_whatsapp_chat(rec)
            time.sleep(1.0)
            type_whatsapp_message(msg_text)
            time.sleep(0.4)
            res = send_active_message()
            res["speak"] = f"{rec} ko message send ho gaya hai"
            return res

    # 1D. "type <msg> and send it" / "type <msg> and send" (into active chat)
    m_type_and_send_active = re.search(r"^(?:type|write|likho)\s+(.+?)\s+(?:and\s+send\s+it|and\s+send|aur\s+bhejo|aur\s+send\s+karo)$", raw, re.IGNORECASE)
    if m_type_and_send_active:
        msg_text = m_type_and_send_active.group(1).strip()
        if msg_text:
            type_whatsapp_message(msg_text)
            time.sleep(0.3)
            return send_active_message()

    # 1E. "send a message to <recipient> <msg>" or "send message to <recipient> that <msg>"
    m_send_msg_to = re.search(r"^(?:send\s+(?:a\s+)?message|send\s+msg)\s+(?:to\s+)([0-9\+\-\s]{10,15}|[a-zA-Z]+)(?:\s+that|\s+saying|\s*:\s*|\s+)(.+)$", raw, re.IGNORECASE)
    if m_send_msg_to:
        rec = m_send_msg_to.group(1).strip()
        msg_text = m_send_msg_to.group(2).strip()
        msg_text = re.sub(r"^(?:that|saying|message|msg)\s+", "", msg_text, flags=re.IGNORECASE).strip()
        if rec and msg_text:
            open_whatsapp_chat(rec)
            time.sleep(1.0)
            type_whatsapp_message(msg_text)
            time.sleep(0.4)
            res = send_active_message()
            res["speak"] = f"{rec} ko message send ho gaya hai"
            return res

    # 1F. "<recipient> ko message/bolo/bhejo <msg>"
    m_rec_ko_msg = re.search(r"^(?:is\s+(?:bande|number)\s+)?([0-9\+\-\s]{10,15}|[a-zA-Z]+)\s+ko\s+(?:message|msg|bolo|likho|bhejo)(?:\s+(?:karo|bhejo|likho|k|ke))?\s+(.+)$", raw, re.IGNORECASE)
    if m_rec_ko_msg:
        rec = m_rec_ko_msg.group(1).strip()
        msg_text = m_rec_ko_msg.group(2).strip()
        msg_text = re.sub(r"^(?:k|ke|message|msg)\s+", "", msg_text, flags=re.IGNORECASE).strip()
        if rec and msg_text:
            open_whatsapp_chat(rec)
            time.sleep(1.0)
            type_whatsapp_message(msg_text)
            time.sleep(0.4)
            res = send_active_message()
            res["speak"] = f"{rec} ko message send ho gaya hai"
            return res

    # 1G. Open specific chat in-place (without typing message)
    chat_open_patterns = [
        # "is bande/number <recipient> ki chat open karo"
        r"^(?:is\s+(?:bande|number)\s+)?(.+?)\s+(?:ki\s+)?chat\s+(?:open|kholo|start)(?:\s+karo|\s+kar\s*do)?$",
        # "open <recipient> chat" or "open chat of/with <recipient>"
        r"^(?:open|kholo)\s+(?:chat\s+(?:with|of|for)\s+)?(.+?)\s+chat$",
        # "chat open/kholo <recipient>" or "chat open karo <recipient>"
        r"^chat\s+(?:open|kholo|start)(?:\s+karo)?(?:\s+(?:with|of|for|ki))?\s+(.+)$",
        # "open chat with/for <recipient>"
        r"^open\s+chat(?:\s+(?:with|of|for))?\s+(.+)$",
        # Urdu script: "چیٹ کھولو" / "کی چیٹ کھولو"
        r"^(.+?)\s+کی\s+چیٹ\s+(?:کھولو|اوپن\s*کرو)$",
        r"^چیٹ\s+کھولو\s+(.+)$",
    ]

    for p in chat_open_patterns:
        m = re.search(p, raw, re.IGNORECASE)
        if m:
            rec = m.group(1).strip()
            rec = re.sub(r"^(?:with|of|for|ki|is bande|is number)\s+", "", rec, flags=re.IGNORECASE).strip()
            # Explicitly guard against app names being captured as WhatsApp recipients
            if rec.lower() in [
                "gpt", "chatgpt", "chat gpt", "ai", "youtube", "yt", "chrome",
                "google", "browser", "notepad", "calc", "calculator", "whatsapp"
            ]:
                continue
            if rec:
                return open_whatsapp_chat(rec)

    # 1H. Type message into active chat ("send message <text>", "type message <text>", "message <text>", "likho <text>")
    type_msg_match = re.search(r"^(?:send\s+message|type\s+message|likho\s+message|message|type|likho|write)\s+(.+)$", raw, re.IGNORECASE)
    if type_msg_match and not any(w in low for w in [" ko message", " par message", " pe message", " ko whatsapp", "to 0", "to +"]):
        msg_text = type_msg_match.group(1).strip()
        msg_text = re.sub(r"^(?:that|:)\s+", "", msg_text).strip()
        if msg_text:
            return type_whatsapp_message(msg_text)

    # 1I. Direct single-command fallback patterns (e.g. "whatsapp 0300... <msg>")
    wa_patterns = [
        # 1. '<recipient> ko whatsapp karo <msg>'
        r"^([0-9\+\-\s]{10,15}|[a-zA-Z\s]+?)\s+(?:ko|pe|par)\s+whatsapp(?:\s+pe|\s+par)?\s+(?:karo|bhejo|likho)?\s*(.+)$",
        # 2. 'whatsapp par/pe <recipient> ko message karo <msg>' or 'whatsapp <recipient> <msg>'
        r"^(?:send\s+)?whatsapp(?:\s+pe|\s+par)?\s+(?:to\s+)?([0-9\+\-\s]{10,15}|[a-zA-Z\s]+?)(?:\s+(?:ko|pe|par))?\s+(?:message|msg|text|likho|send)?(?:\s+karo)?(?:\s*:\s*|\s+that\s+|\s+message\s+|\s+)?(.+)$",
        # 3. 'message <recipient> on whatsapp <msg>'
        r"^(?:message|msg|send)\s+([0-9\+\-\s]{10,15}|[a-zA-Z\s]+?)\s+(?:on|in|via)\s+whatsapp\s*(?:that\s+|message\s+|\s+)?(.+)$",
        # 4. Urdu script: "<recipient> کو میسج کرو <msg>"
        r"^(.+?)\s+کو\s+(?:واٹس\s*ایپ\s+)?(?:میسج|پیغام)\s*(?:کرو|بھیجو|لکھو)?\s*(.+)$",
        r"^(?:واٹس\s*ایپ\s+کرو\s+)(.+?)\s+(?:کو)?\s*(.+)$"
    ]

    for pattern in wa_patterns:
        m = re.search(pattern, raw, re.IGNORECASE)
        if m:
            recipient = m.group(1).strip()
            message_body = m.group(2).strip()
            # Clean message_body from prefix like "message", "msg", "karo", "bhejo", "likho", "that"
            message_body = re.sub(r"^(?:message|msg|karo|bhejo|likho|that)\s+", "", message_body, flags=re.IGNORECASE).strip()
            if recipient and message_body:
                res = send_whatsapp_message(recipient, message_body)
                return res

    # -------------------------------------------------------------
    # 2. YouTube Specific Song / Video Playing & Playback Controls
    # -------------------------------------------------------------
    # Check explicit "play karo is song ko" / "is song ko play karo" / "play karo" / "play it" / "chalao isko"
    play_curr_match = re.search(r"^(?:(?:play|chalao)(?:\s+(?:karo|kar\s*do))?(?:\s+(?:is\s+song\s+ko|is\s+video\s+ko|is\s+ko|isko|this\s+video|this\s+song|this|it|song|video))?|(?:is\s+)?(?:song|video|gana)\s*(?:ko\s+)?(?:play|chalao)(?:\s+(?:karo|kar\s*do|it|this|isko))?)$", low)
    if play_curr_match:
        msg = play_youtube_video()
        return {
            "success": True,
            "message": msg,
            "speak": "YouTube video play ho chuki hai",
            "action": "youtube_play"
        }

    yt_patterns = [
        r"(?:open\s+)?(?:youtube|yt)\s+(?:and\s+)?(?:play|search|chalao|lagao|suno)\s+(.+)",
        r"(?:play|chalao|lagao|suno|search)\s+(.+?)\s+(?:on|in|pe|par)\s+(?:youtube|yt)",
        r"(?:youtube|yt)\s+(?:pe|par|me|in)?\s*(.+?)\s*(?:chalao|lagao|play|suno)",
        r"(?:یوٹیوب|یوٹیوب\s*پر)\s*(.+?)\s*(?:چلاؤ|سنو|کھولو)",
        r"(?:چلاؤ|لگاؤ|سنو)\s+(.+?)(?:\s+(?:یوٹیوب|یوٹیوب\s*پر))?",
    ]

    target_song = None
    for pattern in yt_patterns:
        m = re.search(pattern, low)
        if m:
            target_song = m.group(1).strip()
            break

    # Also detect direct "play <something>" if it refers to songs/music
    if not target_song:
        direct_play = re.search(r"^(?:play|chalao|lagao)\s+(.+)", low)
        if direct_play and not any(w in low for w in ["game", "video game", "pause", "media"]):
            target_song = direct_play.group(1).strip()

    if target_song:
        # Clean extra filler words like "song", "gana", "video", "songs"
        cleaned_song = re.sub(r"\b(?:songs?|gane|gana|music|videos?|audio|track)\b", "", target_song).strip()
        if not cleaned_song:
            cleaned_song = "popular songs"

        # Open YouTube search in a new tab of current Chrome
        encoded = urllib.parse.quote_plus(cleaned_song)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        open_url(url)

        # Background thread: auto-click and start the first search result after 3.5s
        def auto_start_youtube():
            time.sleep(3.5)
            play_youtube_video()
        threading.Thread(target=auto_start_youtube, daemon=True).start()

        return {
            "success": True,
            "message": f"YouTube par '{cleaned_song}' play ho raha hai! 🎵",
            "speak": f"YouTube par {cleaned_song} play ho raha hai",
            "action": "youtube_play"
        }

    # -------------------------------------------------------------
    # 3. General Google Search
    # e.g. "search python tutorials on google", "google par search karo weather"
    # -------------------------------------------------------------
    search_match = re.search(r"(?:search|dhoondo|find)\s+(.+?)(?:\s+(?:on|in|pe|par)\s+(?:google|internet|web))?$", low)
    if search_match and not any(w in low for w in ["youtube", "yt"]):
        query_text = search_match.group(1).strip()
        encoded = urllib.parse.quote_plus(query_text)
        url = f"https://www.google.com/search?q={encoded}"
        open_url(url)
        return {
            "success": True,
            "message": f"Google par search kar diya gaya hai: '{query_text}'",
            "speak": f"Google par {query_text} search ho chuka hai",
            "action": "google_search"
        }

    # -------------------------------------------------------------
    # 4. Notepad and Type Combo
    # e.g. "open notepad and write hello world", "notepad me likho kal meeting hai"
    # -------------------------------------------------------------
    np_match = re.search(r"notepad.*?(?:write|type|likho)\s+(.+)", low)
    if np_match:
        text_to_type = np_match.group(1).strip()
        msg = type_in_notepad(text_to_type)
        return {
            "success": True,
            "message": msg,
            "speak": "Notepad me text likh diya gaya hai",
            "action": "type_in_notepad"
        }

    # -------------------------------------------------------------
    # 5. Direct Typing Commands
    # e.g. "type hello brother", "likho good morning"
    # -------------------------------------------------------------
    if low.startswith("type ") or low.startswith("likho ") or low.startswith("write "):
        text_to_type = raw.split(" ", 1)[1]
        msg = type_text(text_to_type)
        return {
            "success": True,
            "message": msg,
            "speak": "PC par type kar diya gaya hai",
            "action": "type_text"
        }

    # -------------------------------------------------------------
    # 6. Close / Exit Applications
    # e.g. "close chrome", "band karo notepad", "close window"
    # -------------------------------------------------------------
    if any(low.startswith(p) for p in ["close ", "band karo ", "exit ", "kill ", "quit "]):
        target = re.sub(r"^(?:close|band karo|exit|kill|quit)\s+", "", low).strip()
        if target in ["app", "window", "isay", "isko", "this", "current"]:
            msg = safe_close_window()
            return {"success": True, "message": msg, "speak": "Window band kar di gayi hai", "action": "close_window"}
        else:
            msg = close_app_by_name(target)
            return {"success": True, "message": msg, "speak": f"{target} band kar diya gaya hai", "action": "close_app"}

    # -------------------------------------------------------------
    # 7. Open specific Apps or Websites
    # e.g. "open chrome", "kholo calc", "open whatsapp"
    # -------------------------------------------------------------
    if low.startswith("open ") or low.startswith("kholo ") or low.startswith("launch ") or low.startswith("start "):
        target = re.sub(r"^(?:open|kholo|launch|start)\s+", "", low).strip()
        if "." in target and " " not in target:
            msg = open_url(target)
            return {"success": True, "message": msg, "speak": f"{target} open ho chuka hai", "action": "open_url"}
        msg = launch_app(target)
        return {"success": True, "message": msg, "speak": f"{target} open ho chuka hai", "action": f"open_{target}"}

    # -------------------------------------------------------------
    # 8. Common Website / App Keyword Detection
    # -------------------------------------------------------------
    if any(w in low for w in ["youtube", "yt", "youtub"]):
        msg = open_url("https://www.youtube.com")
        return {"success": True, "message": "YouTube open ho chuka hai! ▶️", "speak": "YouTube open ho chuka hai", "action": "open_youtube"}
    if any(w in low for w in ["whatsapp", "wa", "whatsap"]):
        msg = open_url("https://web.whatsapp.com")
        return {"success": True, "message": "WhatsApp open ho chuka hai! 💬", "speak": "WhatsApp open ho chuka hai", "action": "open_whatsapp"}
    if any(w in low for w in ["chatgpt", "gpt", "ai", "chat gpt"]):
        msg = open_url("https://chatgpt.com")
        return {"success": True, "message": "ChatGPT open ho chuka hai! 🤖", "speak": "ChatGPT open ho chuka hai", "action": "open_chatgpt"}
    if any(w in low for w in ["gmail", "email", "mail"]):
        msg = open_url("https://mail.google.com")
        return {"success": True, "message": "Gmail open ho chuka hai! ✉️", "speak": "Gmail open ho chuka hai", "action": "open_gmail"}
    if any(w in low for w in ["chrome", "browser", "google"]):
        msg = open_url("https://www.google.com")
        return {"success": True, "message": "Google Chrome open ho chuka hai! 🌐", "speak": "Google Chrome open ho chuka hai", "action": "open_browser"}

    # -------------------------------------------------------------
    # 9. Volume Controls (English + Roman Urdu + Urdu script)
    # e.g. "awaaz badhao", "sound down", "mute"
    # -------------------------------------------------------------
    if any(w in low for w in ["volume up", "awaaz badhao", "awaz barhao", "sound up", "vol up", "badhao", "barhao", "آواز بڑھاؤ", "آواز تیز"]):
        msg = volume_up()
        return {"success": True, "message": msg, "speak": "Volume barha diya gaya hai", "action": "volume_up"}
    if any(w in low for w in ["volume down", "awaaz kam", "awaz kam", "sound down", "vol down", "kam karo", "آواز کم"]):
        msg = volume_down()
        return {"success": True, "message": msg, "speak": "Volume kam kar diya gaya hai", "action": "volume_down"}
    if any(w in low for w in ["mute", "silent", "sound off", "aawaz band", "awaz band", "chup", "میوٹ", "آواز بند"]):
        msg = volume_mute()
        return {"success": True, "message": msg, "speak": "Volume mute ho gaya hai", "action": "volume_mute"}

    # -------------------------------------------------------------
    # 10. Media Playback Controls
    # -------------------------------------------------------------
    if any(w in low for w in ["pause", "resume", "media play", "media pause", "gana roko", "chalao"]):
        msg = media_play_pause()
        return {"success": True, "message": msg, "speak": "Media toggle ho gaya", "action": "media_play_pause"}
    if any(w in low for w in ["next track", "next song", "agla gana", "agla"]):
        msg = media_next()
        return {"success": True, "message": msg, "speak": "Agla gana chala diya hai", "action": "media_next"}
    if any(w in low for w in ["previous track", "prev song", "peechla gana", "peechla"]):
        msg = media_prev()
        return {"success": True, "message": msg, "speak": "Peechla gana chala diya hai", "action": "media_prev"}

    # -------------------------------------------------------------
    # 11. System Navigation
    # -------------------------------------------------------------
    if any(w in low for w in ["desktop", "minimize all", "home"]):
        msg = trigger_hotkey("show_desktop")
        return {"success": True, "message": msg, "speak": "Desktop open ho gaya hai", "action": "show_desktop"}
    if any(w in low for w in ["lock pc", "lock computer", "computer lock", "screen lock"]):
        msg = lock_screen()
        return {"success": True, "message": msg, "speak": "Computer lock ho chuka hai", "action": "lock_screen"}

    # -------------------------------------------------------------
    # 12. Fallback: Type text onto active screen
    # -------------------------------------------------------------
    msg = type_text(raw)
    return {
        "success": True,
        "message": f"Typed on PC: '{raw}'",
        "speak": "PC par type kar diya gaya hai",
        "action": "type_text"
    }
