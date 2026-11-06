import ctypes
from ctypes import wintypes
import os
import re
import threading
import time
import urllib.parse
from app.actions import (
    open_url, press_special_key, type_text, ensure_desktop_attached,
    play_feedback_sound, user32, kernel32, VK_CONTROL, VK_MENU, VK_RETURN,
    KEYEVENTF_KEYUP
)
from app.contacts_manager import get_phone_for_contact, set_contact, load_contacts
from app.logger import logger


def find_whatsapp_hwnd():
    """Finds the HWND of the WhatsApp window if currently running and visible."""
    ensure_desktop_attached()
    desk = user32.OpenInputDesktop(0, False, 0x01FF)
    if desk:
        user32.SetThreadDesktop(desk)

    target_hwnd = None

    def enum_cb(hwnd, _):
        nonlocal target_hwnd
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.lower()
                if "whatsapp" in title:
                    target_hwnd = hwnd
                    return False
        return True

    cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(enum_cb)
    user32.EnumDesktopWindows(desk, cb, 0)
    return target_hwnd


def is_whatsapp_open() -> bool:
    """Returns True if WhatsApp is currently running on the desktop."""
    return find_whatsapp_hwnd() is not None


def focus_whatsapp_window() -> bool:
    """Finds the WhatsApp or Chrome window and forces it to the foreground with keyboard input focus."""
    ensure_desktop_attached()
    desk = user32.OpenInputDesktop(0, False, 0x01FF)
    if desk:
        user32.SetThreadDesktop(desk)

    target_hwnd = find_whatsapp_hwnd()
    if not target_hwnd:
        # Fallback to Chrome if WhatsApp title not yet updated
        def enum_cb(hwnd, _):
            nonlocal target_hwnd
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.lower()
                    if "chrome" in title:
                        target_hwnd = hwnd
                        return False
            return True
        cb = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(enum_cb)
        user32.EnumDesktopWindows(desk, cb, 0)

    if target_hwnd:
        fg_hwnd = user32.GetForegroundWindow()
        fg_thread = user32.GetWindowThreadProcessId(fg_hwnd, None)
        cur_thread = kernel32.GetCurrentThreadId()

        if fg_thread != cur_thread:
            user32.AttachThreadInput(fg_thread, cur_thread, True)

        user32.ShowWindow(target_hwnd, 9)  # SW_RESTORE
        user32.SetForegroundWindow(target_hwnd)
        user32.BringWindowToTop(target_hwnd)

        if fg_thread != cur_thread:
            user32.AttachThreadInput(fg_thread, cur_thread, False)

        logger.info(f"Focused WhatsApp / Chrome window (HWND: {target_hwnd})")
        return True
    return False


def clean_phone_number(phone_raw: str) -> str:
    """Standardizes phone numbers into international format (e.g., 923001234567)."""
    digits = re.sub(r"\D", "", phone_raw)
    if digits.startswith("03") and len(digits) == 11:
        # Pakistani 03001234567 -> 923001234567
        digits = "92" + digits[1:]
    elif digits.startswith("3") and len(digits) == 10:
        # 3001234567 -> 923001234567
        digits = "92" + digits
    elif digits.startswith("00"):
        digits = digits[2:]
    return digits


def open_whatsapp_chat(recipient: str) -> dict:
    """
    Opens a specific WhatsApp chat in-place inside the existing WhatsApp window.
    Does NOT open a new browser, new window, or reload the page.
    Directly searches and opens the chat just like clicking with a mouse.
    """
    clean_rec = recipient.strip().lower()
    clean_rec = re.sub(r"^(?:with|of|for|ki|is bande|is number)\s+", "", clean_rec).strip()
    logger.info(f"WhatsApp Open Chat request for: '{clean_rec}'")

    # Determine query to search
    search_query = clean_rec
    if clean_rec in ["my number", "apna number", "mera number", "me", "myself", "self"]:
        phone = (get_phone_for_contact("my number") or
                 get_phone_for_contact("me") or
                 get_phone_for_contact("apna number"))
        if phone:
            search_query = phone
        else:
            search_query = "You"
    else:
        # Check if recipient has a saved phone or is a name
        saved_phone = get_phone_for_contact(clean_rec)
        if saved_phone:
            search_query = clean_rec

    # 1. If WhatsApp is ALREADY OPEN: Open chat in-place without opening any new tab or browser!
    if is_whatsapp_open():
        focus_whatsapp_window()
        time.sleep(0.3)

        # Press Escape to clear any current search/modal
        user32.keybd_event(0x1B, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x1B, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.15)

        # Shortcut: Ctrl + Alt + / (0xBF) to focus search in WhatsApp Web
        VK_OEM_2 = 0xBF
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_MENU, 0, 0, 0)
        user32.keybd_event(VK_OEM_2, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(VK_OEM_2, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.2)

        # Clear search box with Ctrl+A, Backspace
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(0x41, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x41, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        user32.keybd_event(0x08, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(0x08, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)

        # Type search query
        type_text(search_query)
        time.sleep(1.0)

        # Press Enter to select the chat
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
        play_feedback_sound()

        return {
            "success": True,
            "message": f"'{clean_rec}' ki chat WhatsApp me open ho gayi hai! Ab bolen: 'send message <text>' ya 'likho <text>'.",
            "speak": f"{clean_rec} ki chat open ho chuki hai",
            "recipient": clean_rec
        }

    # 2. If WhatsApp is NOT open: Open WhatsApp in the existing Chrome window (as a tab)
    open_url("https://web.whatsapp.com")

    def search_and_open_after_load():
        time.sleep(6.5)
        focus_whatsapp_window()
        time.sleep(0.5)
        type_text(search_query)
        time.sleep(1.5)
        press_special_key("enter")
        play_feedback_sound()

    threading.Thread(target=search_and_open_after_load, daemon=True).start()
    return {
        "success": True,
        "message": f"WhatsApp open karke '{clean_rec}' ki chat kholi ja rahi hai.",
        "speak": f"{clean_rec} ki chat open ho rahi hai",
        "recipient": clean_rec
    }


def type_whatsapp_message(text: str) -> dict:
    """
    Types text into the currently active WhatsApp chat compose box WITHOUT sending it.
    The user can review it on screen and then say 'send it' to dispatch.
    """
    clean_text = text.strip()
    # Strip prefixes like "message", "msg", "that"
    clean_text = re.sub(r"^(?:message|msg|that)\s+", "", clean_text, flags=re.IGNORECASE).strip()
    if not clean_text:
        return {"success": False, "message": "Message text cannot be empty.", "speak": "Message khali hai"}

    focus_whatsapp_window()
    time.sleep(0.3)
    type_text(clean_text)
    play_feedback_sound()
    return {
        "success": True,
        "message": f"Message type ho gaya: '{clean_text}'. Bhejne k liye kahein: 'send it' ya 'send'!",
        "speak": "Message type ho chuka hai. Send karne ke liye 'send it' bolein",
        "typed": clean_text
    }


def send_active_message() -> dict:
    """
    Dispatches the currently typed message in the active chat by pressing Enter.
    """
    focus_whatsapp_window()
    time.sleep(0.2)
    press_special_key("enter")
    play_feedback_sound()
    logger.info("Dispatched active chat message via Enter")
    return {
        "success": True,
        "message": "Message send ho gaya! 🚀",
        "speak": "Message send ho gaya hai"
    }


def send_whatsapp_message(recipient: str, message: str) -> dict:
    """
    Direct single-command WhatsApp sending: opens chat, types message, and automatically sends.
    If WhatsApp is open, does in-place chat search, types message, and dispatches.
    """
    clean_rec = recipient.strip().lower()
    msg_clean = message.strip()

    if not clean_rec or not msg_clean:
        return {"success": False, "message": "Recipient or message empty"}

    logger.info(f"WhatsApp sending request: To '{clean_rec}', Message: '{msg_clean}'")

    # If WhatsApp is already open, use seamless in-place flow
    if is_whatsapp_open():
        open_whatsapp_chat(clean_rec)
        time.sleep(1.2)
        type_whatsapp_message(msg_clean)
        time.sleep(0.5)
        return send_active_message()

    # Otherwise open direct chat URL
    phone = clean_phone_number(clean_rec)
    if not (phone and len(phone) >= 10):
        phone = get_phone_for_contact(clean_rec)

    if phone and len(phone) >= 10:
        encoded_msg = urllib.parse.quote(msg_clean)
        wa_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
        open_url(wa_url)

        def auto_send_via_url():
            ensure_desktop_attached()
            time.sleep(7.5)
            focus_whatsapp_window()
            time.sleep(0.5)
            press_special_key("enter")
            time.sleep(2.0)
            focus_whatsapp_window()
            press_special_key("enter")
            play_feedback_sound()
            logger.info(f"WhatsApp message dispatched to {phone}")

        t = threading.Thread(target=auto_send_via_url, daemon=True)
        t.start()

        return {
            "success": True,
            "message": f"WhatsApp opened for '{clean_rec}': message typed & sending automatically!",
            "speak": f"{clean_rec} ko message send ho raha hai",
            "phone": phone,
            "text": msg_clean
        }

    return send_whatsapp_by_search(clean_rec, msg_clean)


def send_whatsapp_by_search(contact_name: str, message: str) -> dict:
    """
    Searches contact, focuses chat, types message, and sends.
    """
    open_url("https://web.whatsapp.com")

    def auto_search_and_send():
        ensure_desktop_attached()
        time.sleep(6.5)
        focus_whatsapp_window()
        time.sleep(0.5)
        type_text(contact_name)
        time.sleep(1.8)
        press_special_key("enter")
        time.sleep(1.5)
        type_text(message)
        time.sleep(0.8)
        press_special_key("enter")
        play_feedback_sound()
        logger.info(f"WhatsApp search & send completed for '{contact_name}'")

    t = threading.Thread(target=auto_search_and_send, daemon=True)
    t.start()

    return {
        "success": True,
        "message": f"WhatsApp: Searching '{contact_name}', typing message & sending!",
        "speak": f"{contact_name} ko message send ho raha hai",
        "recipient": contact_name,
        "text": message
    }
