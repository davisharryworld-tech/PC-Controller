import json
import re
import threading
import time
import urllib.parse
import urllib.request
from typing import Optional, List, Dict, Any

from app.actions import (
    open_url, launch_app, close_app_by_name, safe_close_window,
    volume_up, volume_down, volume_mute, media_play_pause,
    media_next, media_prev, trigger_hotkey, lock_screen,
    type_text, type_in_notepad, play_youtube_video,
    minimize_window, maximize_window, antigravity_proceed,
    system_sleep, system_restart, system_shutdown
)
from app.contacts_manager import set_contact, load_contacts
from app.logger import logger
from app.whatsapp_sender import (
    send_whatsapp_message, open_whatsapp_chat,
    type_whatsapp_message, send_active_message
)


def split_compound_instruction(raw: str) -> List[str]:
    """
    Intelligently splits complex compound instructions in Roman Urdu, Urdu, and English
    into ordered individual execution steps.
    e.g. 'antigravity ko minimize karke youtube kholo aur us me search karo koi song'
    -> ['antigravity ko minimize', 'youtube kholo', 'us me search karo koi song']
    """
    text = raw.strip()
    if not text:
        return []

    # 1. Sequential conjunctions: 'kar ke', 'karke', 'krke', 'kar k', 'kr k'
    p_karke = re.compile(r'\b(?:kar\s*ke|karke|kar\s*k|krke|kr\s*k)\b', re.IGNORECASE)
    text = p_karke.sub(' __THEN__ ', text)

    # 2. Temporal sequencers: 'aur phir', 'phir', 'aur fir', 'fir', 'then', 'uske baad', 'iske baad', 'ke baad', 'baad me'
    p_then = re.compile(r'\b(?:aur\s+phir|phir|aur\s+fir|fir|then|aur\s+then|uske\s+baad|iske\s+baad|ke\s+baad|baad\s+me)\b', re.IGNORECASE)
    text = p_then.sub(' __THEN__ ', text)

    # 3. Action words that mark the end of a command preceding 'aur' / 'and':
    # e.g., '...kholo aur...', '...karo aur...', '...badhao aur...', '...barhao aur...', '...band karo aur...'
    text = re.sub(
        r'\b(kholo|open|karo|kar\s*do|karna|badhao|barhao|kam\s*karo|band\s*karo|close|likho|type|chalao|play|dabao|proceed|minimize|maximize)\s+(?:aur|and)\s+',
        r'\1 __THEN__ ',
        text,
        flags=re.IGNORECASE
    )

    # 4. Contextual pronouns following 'aur' or standalone: 'aur us me', 'aur isme', 'aur wahan', 'us me likho'
    text = re.sub(r'\b(?:aur|and)?\s*(?=(?:us\s*me|usme|isme|is\s*me|wahan)\s+(?:search|likho|type|chalao|play|dhoondo))\b', ' __THEN__ ', text, flags=re.IGNORECASE)

    # 5. Punctuation delimiters
    text = re.sub(r'[,;]+', ' __THEN__ ', text)

    parts = [p.strip() for p in text.split('__THEN__') if p.strip()]
    return parts if parts else [raw.strip()]


def query_ollama_llm(user_prompt: str) -> Optional[List[Dict[str, Any]]]:
    """
    Calls local Ollama LLM on port 11434 to parse complex, conversational Roman Urdu commands
    into a structured JSON action plan. Returns None if Ollama is unavailable or times out.
    """
    try:
        system_prompt = (
            "You are a Windows PC Controller AI Assistant. The user gives commands in Roman Urdu, Urdu, or English.\n"
            "Convert the user's instructions into a JSON array of actions.\n"
            "Supported actions:\n"
            "- {\"action\": \"minimize_window\", \"target\": \"antigravity\"}\n"
            "- {\"action\": \"maximize_window\", \"target\": \"chrome\"}\n"
            "- {\"action\": \"close_window\", \"target\": \"app_name\"}\n"
            "- {\"action\": \"play_youtube\", \"query\": \"song or video name\"}\n"
            "- {\"action\": \"open_url\", \"url\": \"https://...\"}\n"
            "- {\"action\": \"open_app\", \"app\": \"notepad\"}\n"
            "- {\"action\": \"type_in_notepad\", \"text\": \"some text\"}\n"
            "- {\"action\": \"volume_up\"}\n"
            "- {\"action\": \"volume_down\"}\n"
            "- {\"action\": \"volume_mute\"}\n"
            "- {\"action\": \"lock_screen\"}\n"
            "- {\"action\": \"antigravity_proceed\"}\n"
            "Output ONLY the raw JSON array. No explanations, no markdown blocks."
        )

        payload = json.dumps({
            "model": "chrisakakmaenn/wormgpt:latest",
            "prompt": f"{system_prompt}\nUser Command: {user_prompt}\nJSON:",
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 120}
        }).encode("utf-8")

        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_out = data.get("response", "").strip()
            match = re.search(r'\[.*\]', raw_out, re.DOTALL)
            if match:
                actions = json.loads(match.group(0))
                if isinstance(actions, list) and len(actions) > 0:
                    return actions
    except Exception as e:
        logger.debug(f"Ollama local LLM query skipped/error: {e}")
    return None


def execute_action_dict(act: Dict[str, Any]) -> Dict[str, Any]:
    """Executes a single structured action dictionary."""
    name = act.get("action", "")

    if name in ["minimize_window", "minimize"]:
        target = act.get("target") or act.get("app")
        msg = minimize_window(target)
        return {"success": True, "message": msg, "action": "minimize_window"}

    elif name in ["maximize_window", "maximize"]:
        target = act.get("target") or act.get("app")
        msg = maximize_window(target)
        return {"success": True, "message": msg, "action": "maximize_window"}

    elif name in ["close_window", "close_app", "close"]:
        target = act.get("target") or act.get("app")
        if target:
            msg = close_app_by_name(target)
        else:
            msg = safe_close_window()
        return {"success": True, "message": msg, "action": "close_window"}

    elif name in ["play_youtube", "youtube_play", "search_youtube"]:
        query = act.get("query") or act.get("song") or "popular songs"
        msg = play_youtube_video(query)
        return {"success": True, "message": msg, "action": "youtube_play"}

    elif name in ["open_url"]:
        url = act.get("url", "https://google.com")
        msg = open_url(url)
        return {"success": True, "message": msg, "action": "open_url"}

    elif name in ["open_app", "launch_app"]:
        app_name = act.get("app") or act.get("target") or ""
        msg = launch_app(app_name)
        return {"success": True, "message": msg, "action": f"open_{app_name}"}

    elif name in ["type_in_notepad"]:
        txt = act.get("text", "")
        msg = type_in_notepad(txt)
        return {"success": True, "message": msg, "action": "type_in_notepad"}

    elif name in ["type_text"]:
        txt = act.get("text", "")
        msg = type_text(txt, press_enter=bool(act.get("press_enter", True)))
        return {"success": True, "message": msg, "action": "type_text"}

    elif name in ["antigravity_proceed", "proceed"]:
        msg = antigravity_proceed()
        return {"success": True, "message": msg, "action": "antigravity_proceed"}

    elif name in ["volume_up"]:
        msg = volume_up()
        return {"success": True, "message": msg, "action": "volume_up"}

    elif name in ["volume_down"]:
        msg = volume_down()
        return {"success": True, "message": msg, "action": "volume_down"}

    elif name in ["volume_mute", "mute"]:
        msg = volume_mute()
        return {"success": True, "message": msg, "action": "volume_mute"}

    elif name in ["lock_screen"]:
        msg = lock_screen()
        return {"success": True, "message": msg, "action": "lock_screen"}

    elif name in ["system_sleep"]:
        msg = system_sleep()
        return {"success": True, "message": msg, "action": "system_sleep"}

    return {"success": False, "message": f"Unknown action '{name}'", "action": name}


def execute_single_step(step_str: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses and executes an individual sub-step instruction in Roman Urdu / Urdu / English.
    Maintains and updates context (e.g. active app, last subject).
    """
    raw = step_str.strip()
    low = raw.lower()

    # 1. Antigravity Proceed / Submit / Enter (Auto-coder bot)
    if any(w in low for w in ["proceed", "submit", "enter dabao", "antigravity proceed", "continue", "aage badhao"]):
        msg = antigravity_proceed()
        return {"success": True, "message": msg, "speak": "Antigravity proceed kar diya", "action": "antigravity_proceed"}

    # 2. Window Minimize (e.g. "antigravity ko minimize", "minimize chrome", "hata do")
    if any(w in low for w in ["minimize", "chhota karo", "chota karo", "hata do", "hide"]):
        target = re.sub(r"\b(?:ko|kar\s*do|karo|karna|kar|please|isay|isko)\b", "", low)
        target = re.sub(r"\b(?:minimize|chhota karo|chota karo|hata do|hide)\b", "", target).strip()
        if not target or target in ["window", "screen", "current", "active"]:
            target = None
        msg = minimize_window(target)
        return {"success": True, "message": msg, "speak": f"{target or 'Window'} minimize ho gayi", "action": "minimize_window"}

    # 3. Window Maximize / Fullscreen
    if any(w in low for w in ["maximize", "bada karo", "fullscreen", "full screen"]):
        target = re.sub(r"\b(?:ko|kar\s*do|karo|karna|kar|please|isay|isko)\b", "", low)
        target = re.sub(r"\b(?:maximize|bada karo|fullscreen|full screen)\b", "", target).strip()
        msg = maximize_window(target or None)
        return {"success": True, "message": msg, "speak": f"{target or 'Window'} maximize ho gayi", "action": "maximize_window"}

    # 4. Close Window or Application
    if any(low.startswith(p) for p in ["close ", "band karo ", "exit ", "kill ", "quit ", "band "]) or any(w in low for w in ["band kar do", "band karo", "band"]):
        target = re.sub(r"\b(?:close|band\s*karo|band\s*kar\s*do|exit|kill|quit|band|ko)\b", "", low).strip()
        if not target or target in ["window", "isay", "isko", "current", "app"]:
            msg = safe_close_window()
            return {"success": True, "message": msg, "speak": "Window band kar di gayi hai", "action": "close_window"}
        else:
            msg = close_app_by_name(target)
            return {"success": True, "message": msg, "speak": f"{target} band kar diya gaya hai", "action": "close_app"}

    # -------------------------------------------------------------
    # 5. WhatsApp Conversational Actions
    # -------------------------------------------------------------
    send_it_match = re.search(r"^(?:send\s+it(?:\s+now)?|send(?:\s+this)?|send\s+kar\s*do|send\s+karo|bhejo|bhej\s*do|سینڈ\s*کرو|بھیجو|بھیج\s*دو)$", low)
    if send_it_match:
        return send_active_message()

    save_contact_match = re.search(r"(?:save|add)\s+contact\s+(.+?)\s+([0-9\+]+)$", low)
    if save_contact_match:
        c_name = save_contact_match.group(1).strip()
        c_phone = save_contact_match.group(2).strip()
        set_contact(c_name, c_phone)
        return {"success": True, "message": f"Contact '{c_name}' saved with number {c_phone}", "speak": f"Contact {c_name} save ho chuka hai", "action": "save_contact"}

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

    chat_open_patterns = [
        r"^(?:is\s+(?:bande|number)\s+)?(.+?)\s+(?:ki\s+)?chat\s+(?:open|kholo|start)(?:\s+karo|\s+kar\s*do)?$",
        r"^(?:open|kholo)\s+(?:chat\s+(?:with|of|for)\s+)?(.+?)\s+chat$",
        r"^chat\s+(?:open|kholo|start)(?:\s+karo)?(?:\s+(?:with|of|for|ki))?\s+(.+)$",
        r"^open\s+chat(?:\s+(?:with|of|for))?\s+(.+)$",
    ]
    for p in chat_open_patterns:
        m = re.search(p, raw, re.IGNORECASE)
        if m:
            rec = m.group(1).strip()
            rec = re.sub(r"^(?:with|of|for|ki|is bande|is number)\s+", "", rec, flags=re.IGNORECASE).strip()
            if rec.lower() not in ["gpt", "chatgpt", "youtube", "yt", "chrome", "google", "browser", "notepad", "whatsapp"]:
                if rec:
                    return open_whatsapp_chat(rec)

    # -------------------------------------------------------------
    # 6. YouTube Search & Play (Context-aware: 'search karo koi song', 'us me search karo X', 'aatif aslam ka gana chalao')
    # -------------------------------------------------------------
    is_yt_context = context.get("last_app") == "youtube" or any(w in low for w in ["youtube", "yt"])

    yt_search_match = re.search(r"(?:us\s*me|usme|isme|is\s*me|wahan|youtube|yt)?\s*(?:search|dhoondo|play|chalao|lagao|suno)(?:\s+(?:karo|kar\s*do))?\s+(.+)", low)
    if yt_search_match and (is_yt_context or any(w in low for w in ["song", "gana", "video", "music", "track", "youtube", "yt"])):
        song = yt_search_match.group(1).strip()
        song_clean = re.sub(r"\b(?:on|in|pe|par|me|ko|karo|kar\s*do|youtube|yt)\b", "", song).strip()
        if not song_clean or song_clean in ["koi", "kuch", "some", "koi sa", "koisa"]:
            song_clean = "popular songs 2026"
        msg = play_youtube_video(song_clean)
        context["last_app"] = "youtube"
        return {"success": True, "message": msg, "speak": f"YouTube par {song_clean} play ho raha hai", "action": "youtube_play"}

    direct_song = re.search(r"^(.+?)\s*(?:ka\s+gana|gana|song|video)?\s*(?:chalao|play|lagao|suno)(?:\s+(?:karo|kar\s*do))?$", low)
    if direct_song and any(w in low for w in ["gana", "song", "chalao", "play", "music"]):
        song = direct_song.group(1).strip()
        song_clean = re.sub(r"\b(?:gana|song|video|chalao|play|lagao|suno|ka)\b", "", song).strip()
        msg = play_youtube_video(song_clean)
        context["last_app"] = "youtube"
        return {"success": True, "message": msg, "speak": f"YouTube par {song_clean} play ho raha hai", "action": "youtube_play"}

    # 7. Standalone YouTube Open
    if any(w in low for w in ["open youtube", "open yt", "youtube kholo", "youtube open karo", "youtube open"]):
        open_url("https://www.youtube.com")
        context["last_app"] = "youtube"
        return {"success": True, "message": "YouTube open ho chuka hai! ▶️", "speak": "YouTube open ho chuka hai", "action": "open_youtube"}

    # 8. Notepad & Typing Combos
    if "notepad" in low and any(w in low for w in ["likho", "type", "write"]):
        txt = re.sub(r".*?(?:likho|type|write)\s+", "", raw, flags=re.IGNORECASE).strip()
        msg = type_in_notepad(txt)
        context["last_app"] = "notepad"
        return {"success": True, "message": msg, "speak": "Notepad me text likh diya gaya hai", "action": "type_in_notepad"}

    if (context.get("last_app") == "notepad" or any(w in low for w in ["usme", "us me", "isme"])) and any(w in low for w in ["likho", "type", "write"]):
        txt = re.sub(r".*?(?:likho|type|write)\s+", "", raw, flags=re.IGNORECASE).strip()
        msg = type_in_notepad(txt)
        context["last_app"] = "notepad"
        return {"success": True, "message": msg, "speak": "Notepad me text likh diya gaya hai", "action": "type_in_notepad"}

    # 9. Standalone Notepad Open
    if any(w in low for w in ["open notepad", "notepad kholo", "notepad open karo"]):
        launch_app("notepad")
        context["last_app"] = "notepad"
        return {"success": True, "message": "Notepad open ho gaya hai! 📝", "speak": "Notepad open ho chuka hai", "action": "open_notepad"}

    # 10. Standalone Apps (ChatGPT, Chrome, WhatsApp)
    if any(w in low for w in ["chatgpt", "chat gpt", "open chat gpt", "chatgpt kholo", "open chatgpt"]):
        open_url("https://chatgpt.com")
        context["last_app"] = "chatgpt"
        return {"success": True, "message": "ChatGPT open ho chuka hai! 🤖", "speak": "ChatGPT open ho chuka hai", "action": "open_chatgpt"}

    if any(w in low for w in ["open chrome", "chrome kholo", "browser kholo", "open browser"]):
        open_url("https://www.google.com")
        context["last_app"] = "chrome"
        return {"success": True, "message": "Google Chrome open ho chuka hai! 🌐", "speak": "Google Chrome open ho chuka hai", "action": "open_browser"}

    if any(w in low for w in ["open whatsapp", "whatsapp kholo"]):
        open_url("https://web.whatsapp.com")
        context["last_app"] = "whatsapp"
        return {"success": True, "message": "WhatsApp open ho chuka hai! 💬", "speak": "WhatsApp open ho chuka hai", "action": "open_whatsapp"}

    # 11. Volume Controls
    if any(w in low for w in ["volume up", "awaaz badhao", "awaz barhao", "sound up", "vol up", "badhao", "barhao"]):
        msg = volume_up()
        return {"success": True, "message": msg, "speak": "Volume barha diya gaya hai", "action": "volume_up"}
    if any(w in low for w in ["volume down", "awaaz kam", "awaz kam", "sound down", "vol down", "kam karo"]):
        msg = volume_down()
        return {"success": True, "message": msg, "speak": "Volume kam kar diya gaya hai", "action": "volume_down"}
    if any(w in low for w in ["mute", "silent", "sound off", "aawaz band", "awaz band"]):
        msg = volume_mute()
        return {"success": True, "message": msg, "speak": "Volume mute ho gaya hai", "action": "volume_mute"}

    # 12. Media Playback Controls
    if any(w in low for w in ["pause", "resume", "media play", "media pause", "gana roko"]):
        msg = media_play_pause()
        return {"success": True, "message": msg, "speak": "Media toggle ho gaya", "action": "media_play_pause"}
    if any(w in low for w in ["next track", "next song", "agla gana"]):
        msg = media_next()
        return {"success": True, "message": msg, "speak": "Agla gana", "action": "media_next"}
    if any(w in low for w in ["previous track", "peechla gana"]):
        msg = media_prev()
        return {"success": True, "message": msg, "speak": "Peechla gana", "action": "media_prev"}

    # 13. General Google Search
    search_match = re.search(r"(?:search|dhoondo|find)\s+(.+?)(?:\s+(?:on|in|pe|par)\s+(?:google|internet|web))?$", low)
    if search_match and not any(w in low for w in ["youtube", "yt"]):
        query_text = search_match.group(1).strip()
        encoded = urllib.parse.quote_plus(query_text)
        open_url(f"https://www.google.com/search?q={encoded}")
        return {"success": True, "message": f"Google Search: '{query_text}'", "speak": f"Google par {query_text} search ho gaya", "action": "google_search"}

    # 14. System Lock / Sleep / Navigation
    if any(w in low for w in ["desktop", "minimize all", "home"]):
        msg = trigger_hotkey("show_desktop")
        return {"success": True, "message": msg, "speak": "Desktop open ho gaya hai", "action": "show_desktop"}
    if any(w in low for w in ["lock pc", "lock computer", "computer lock", "screen lock"]):
        msg = lock_screen()
        return {"success": True, "message": msg, "speak": "Computer lock ho chuka hai", "action": "lock_screen"}

    # 15. Fallback: Type text onto active screen and press Enter
    msg = type_text(raw, press_enter=True)
    return {"success": True, "message": f"Typed on PC: '{raw}'", "speak": "PC par type kar diya gaya hai", "action": "type_text"}


def interpret_and_execute_nl(query: str) -> Dict[str, Any]:
    """
    Intelligently parses and executes natural language instructions supporting
    Roman Urdu, Urdu script, and English.
    Handles compound multi-step workflows sequentially with context passing,
    and uses local Ollama AI as an intelligent agentic fallback.
    """
    raw = query.strip()
    if not raw:
        return {"success": False, "message": "Khali command receive hui hai.", "speak": "Kuch bolein ya likhein", "action": "empty"}

    logger.info(f"AI Assistant Intent Parsing: '{raw}'")

    # -------------------------------------------------------------
    # Step A: Split compound multi-step commands
    # e.g. "antigravity ko minimize karke youtube kholo aur us me search karo koi song"
    # -> Step 1: "antigravity ko minimize"
    # -> Step 2: "youtube kholo"
    # -> Step 3: "us me search karo koi song"
    # -------------------------------------------------------------
    steps = split_compound_instruction(raw)

    # -------------------------------------------------------------
    # Step B: Multi-step sequential execution
    # -------------------------------------------------------------
    if len(steps) > 1:
        logger.info(f"Detected {len(steps)} sequential steps in compound command: {steps}")
        results = []
        context: Dict[str, Any] = {}

        # Lookahead optimization: If Step N is "open youtube" and Step N+1 is "search <song>",
        # skip opening plain youtube since play_youtube directly handles search and autoplay!
        skip_indices = set()
        for idx in range(len(steps) - 1):
            s_curr = steps[idx].lower()
            s_next = steps[idx + 1].lower()
            if any(w in s_curr for w in ["youtube kholo", "open youtube", "open yt"]) and any(w in s_next for w in ["search", "play", "chalao", "suno", "gana", "song"]):
                skip_indices.add(idx)

        for i, step in enumerate(steps):
            if i in skip_indices:
                context["last_app"] = "youtube"
                continue

            time.sleep(0.3)
            res = execute_single_step(step, context)
            results.append(res.get("message", step))

        combined_msg = " ➔ ".join(results)
        return {
            "success": True,
            "message": f"✅ Multi-Step Completed: {combined_msg}",
            "speak": "Aapki saari instructions execute ho chuki hain",
            "action": "compound_multi_step"
        }

    # -------------------------------------------------------------
    # Step C: Single-step execution with local Ollama LLM fallback
    # -------------------------------------------------------------
    context: Dict[str, Any] = {}
    res = execute_single_step(raw, context)

    # If simple pattern fell back to typing, check if local Ollama AI can parse it better
    if res.get("action") == "type_text" and len(raw.split()) > 2:
        ollama_plan = query_ollama_llm(raw)
        if ollama_plan:
            logger.info(f"Ollama AI Plan Generated: {ollama_plan}")
            msgs = []
            for act in ollama_plan:
                r = execute_action_dict(act)
                msgs.append(r.get("message", ""))
                time.sleep(0.3)
            return {
                "success": True,
                "message": f"🤖 AI Executed: {' | '.join(msgs)}",
                "speak": "AI ne aapka kaam mukammal kar diya hai",
                "action": "ollama_ai_plan"
            }

    return res
