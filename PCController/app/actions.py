import ctypes
import os
import shutil
import subprocess
import time
import webbrowser
import winsound
from typing import Any, Dict, List
from ctypes import wintypes
import psutil
import pyperclip
from app.logger import logger

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Win32 Process Creation structures for launching strictly on the user's interactive desktop
class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.c_void_p),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]

CREATE_NEW_CONSOLE = 0x00000010
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

def launch_on_default_desktop(command_line: str) -> bool:
    """Launches any command or application directly on the user's visible physical monitor (WinSta0\\Default).
    
    Breaks out of background/sandboxed jobs so the window is 100% visible and interactive.
    """
    ensure_desktop_attached()
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(STARTUPINFOW)
    si.lpDesktop = r"WinSta0\Default"
    si.dwFlags = 0x00000001  # STARTF_USESHOWWINDOW
    si.wShowWindow = 5  # SW_SHOW
    pi = PROCESS_INFORMATION()

    flags = CREATE_NEW_CONSOLE | CREATE_BREAKAWAY_FROM_JOB
    ok = kernel32.CreateProcessW(
        None, command_line, None, None, False, flags, None, None,
        ctypes.byref(si), ctypes.byref(pi)
    )
    if not ok:
        # Fallback without breakaway flag
        ok = kernel32.CreateProcessW(
            None, command_line, None, None, False, CREATE_NEW_CONSOLE, None, None,
            ctypes.byref(si), ctypes.byref(pi)
        )
    if ok:
        kernel32.CloseHandle(pi.hProcess)
        kernel32.CloseHandle(pi.hThread)
        return True
    return False

# Detect Chrome and Edge paths
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_PATH):
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

# Screen dimension bounds
SCREEN_W = user32.GetSystemMetrics(0) or 1366
SCREEN_H = user32.GetSystemMetrics(1) or 768

# Win32 Virtual Key Constants
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_PRIOR = 0x21  # PageUp
VK_NEXT = 0x22   # PageDown
VK_F5 = 0x74
VK_LWIN = 0x5B
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_F11 = 0x7A

KEYEVENTF_KEYUP = 0x0002
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def ensure_desktop_attached():
    """Attaches the current execution thread to the interactive Windows input desktop."""
    try:
        desk = user32.OpenInputDesktop(0, False, 0x01FF)
        if desk:
            user32.SetThreadDesktop(desk)
            user32.CloseDesktop(desk)
            return True
    except Exception:
        pass
    return False


def play_feedback_sound():
    """Subtle Windows audio chime so user knows PC received command."""
    try:
        winsound.MessageBeep(winsound.MB_OK)
    except Exception:
        pass


def volume_up(steps: int = 5) -> str:
    ensure_desktop_attached()
    for _ in range(steps):
        user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
        user32.keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, 0)
    play_feedback_sound()
    return f"Volume Increased (+{steps * 2}%)"


def volume_down(steps: int = 5) -> str:
    ensure_desktop_attached()
    for _ in range(steps):
        user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
        user32.keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, 0)
    play_feedback_sound()
    return f"Volume Decreased (-{steps * 2}%)"


def volume_mute() -> str:
    ensure_desktop_attached()
    user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
    user32.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, 0)
    play_feedback_sound()
    return "Volume Mute Toggled"


def media_play_pause() -> str:
    ensure_desktop_attached()
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_KEYUP, 0)
    play_feedback_sound()
    return "Media Play / Pause Toggled"


def play_youtube_video() -> str:
    """
    Plays the current video on YouTube, or clicks and starts the first video on a search page.
    """
    ensure_desktop_attached()
    desk = user32.OpenInputDesktop(0, False, 0x01FF)
    if desk:
        user32.SetThreadDesktop(desk)

    # 1. Bring Chrome window to foreground
    target_hwnd = None
    def enum_cb(hwnd, _):
        nonlocal target_hwnd
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                t = buff.value.lower()
                if "youtube" in t or "chrome" in t:
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

    time.sleep(0.3)

    # 2. Click on the first video on the search page (approx x=480, y=260)
    user32.SetCursorPos(480, 260)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.2)

    # 3. Also press 'k' (YouTube play/pause key)
    user32.keybd_event(0x4B, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x4B, 0, KEYEVENTF_KEYUP, 0)

    play_feedback_sound()
    logger.info("Triggered YouTube play on first video / active player")
    return "YouTube video play kar di gayi hai! 🎵"


def media_next() -> str:
    ensure_desktop_attached()
    user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 0, 0)
    user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, KEYEVENTF_KEYUP, 0)
    play_feedback_sound()
    return "Skipped to Next Track"


def media_prev() -> str:
    ensure_desktop_attached()
    user32.keybd_event(VK_MEDIA_PREV_TRACK, 0, 0, 0)
    user32.keybd_event(VK_MEDIA_PREV_TRACK, 0, KEYEVENTF_KEYUP, 0)
    play_feedback_sound()
    return "Returned to Previous Track"


def media_seek(direction: str = "forward") -> str:
    """Seeks 10s forward or backward in active YouTube / Netflix / video player."""
    ensure_desktop_attached()
    if direction.lower() in ("forward", "fwd", "right", "next"):
        user32.keybd_event(0x4C, 0, 0, 0)  # L key (YouTube +10s)
        user32.keybd_event(0x4C, 0, KEYEVENTF_KEYUP, 0)
        return "Seek Forward (+10s)"
    else:
        user32.keybd_event(0x4A, 0, 0, 0)  # J key (YouTube -10s)
        user32.keybd_event(0x4A, 0, KEYEVENTF_KEYUP, 0)
        return "Seek Backward (-10s)"


def media_toggle_subtitles() -> str:
    ensure_desktop_attached()
    user32.keybd_event(0x43, 0, 0, 0)  # C key
    user32.keybd_event(0x43, 0, KEYEVENTF_KEYUP, 0)
    return "Toggled Subtitles (C)"


def media_speed(mode: str = "up") -> str:
    ensure_desktop_attached()
    vk_target = 0xBE if mode == "up" else 0xBC  # Shift + > or <
    user32.keybd_event(VK_SHIFT, 0, 0, 0)
    user32.keybd_event(vk_target, 0, 0, 0)
    user32.keybd_event(vk_target, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
    return f"Playback Speed {'Increased' if mode == 'up' else 'Decreased'}"


def media_toggle_fullscreen() -> str:
    ensure_desktop_attached()
    user32.keybd_event(0x46, 0, 0, 0)  # F key
    user32.keybd_event(0x46, 0, KEYEVENTF_KEYUP, 0)
    return "Toggled Fullscreen (F)"


def presentation_action(cmd: str) -> str:
    """Controls PowerPoint, Google Slides, PDF presentations."""
    ensure_desktop_attached()
    c = cmd.lower().strip()
    if c in ("next", "forward", "slide_next"):
        user32.keybd_event(VK_NEXT, 0, 0, 0)  # PageDown
        user32.keybd_event(VK_NEXT, 0, KEYEVENTF_KEYUP, 0)
        return "Next Slide"
    elif c in ("prev", "previous", "slide_prev", "back"):
        user32.keybd_event(VK_PRIOR, 0, 0, 0)  # PageUp
        user32.keybd_event(VK_PRIOR, 0, KEYEVENTF_KEYUP, 0)
        return "Previous Slide"
    elif c in ("start", "f5", "begin"):
        user32.keybd_event(VK_F5, 0, 0, 0)
        user32.keybd_event(VK_F5, 0, KEYEVENTF_KEYUP, 0)
        return "Presentation Started (F5)"
    elif c in ("exit", "escape", "stop"):
        user32.keybd_event(VK_ESCAPE, 0, 0, 0)
        user32.keybd_event(VK_ESCAPE, 0, KEYEVENTF_KEYUP, 0)
        return "Exited Presentation (Esc)"
    elif c in ("black", "b"):
        user32.keybd_event(0x42, 0, 0, 0)  # B
        user32.keybd_event(0x42, 0, KEYEVENTF_KEYUP, 0)
        return "Toggled Black Screen"
    return f"Slide action: {cmd}"


def run_macro_workflow(macro_name: str) -> str:
    """Executes predefined 1-tap workflows."""
    ensure_desktop_attached()
    m = macro_name.lower().strip()
    if m == "work_mode":
        launch_on_default_desktop("chrome.exe")
        time.sleep(0.3)
        launch_on_default_desktop("code")
        time.sleep(0.3)
        launch_on_default_desktop("notepad.exe")
        return "💼 Work Mode: Chrome, VS Code & Notepad Launched!"
    elif m == "chill_mode":
        launch_app("youtube")
        time.sleep(0.5)
        launch_app("spotify")
        return "☕ Chill Mode: YouTube & Spotify Ready!"
    elif m == "gaming_mode":
        for p in ("chrome.exe", "msedge.exe", "notepad.exe", "code.exe"):
            try:
                subprocess.run(["taskkill", "/F", "/IM", p], capture_output=True)
            except Exception:
                pass
        return "🎮 Gaming Mode: Background Apps Cleared!"
    elif m == "study_mode":
        webbrowser.open("https://docs.google.com")
        time.sleep(0.3)
        webbrowser.open("https://chatgpt.com")
        return "📚 Study Mode: Google Docs & ChatGPT Opened!"
    return f"Macro '{macro_name}' executed"


# Native cursor movement with physical boundary checks
def mouse_move(dx: int, dy: int) -> str:
    ensure_desktop_attached()
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    new_x = max(0, min(pt.x + dx, SCREEN_W - 1))
    new_y = max(0, min(pt.y + dy, SCREEN_H - 1))
    user32.SetCursorPos(new_x, new_y)
    return f"Mouse moved to ({new_x}, {new_y})"


def mouse_click(button: str = "left") -> str:
    ensure_desktop_attached()
    btn = button.lower().strip()
    if btn == "left":
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        return "Left Click"
    elif btn == "right":
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        return "Right Click"
    return "Click"


def mouse_double_click() -> str:
    ensure_desktop_attached()
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    return "Double Click"


def mouse_scroll(amount: int) -> str:
    ensure_desktop_attached()
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, amount, 0)
    return f"Scrolled {'Up' if amount > 0 else 'Down'}"


def type_text(text: str, press_enter: bool = False) -> str:
    """Pastes text directly into the active window (supports Urdu, emojis, etc.)."""
    if not text:
        return "Empty text"
    ensure_desktop_attached()
    pyperclip.copy(text)

    # Press Ctrl+V via keybd_event
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(0x56, 0, 0, 0)  # V
    user32.keybd_event(0x56, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

    if press_enter:
        time.sleep(0.15)
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)

    play_feedback_sound()
    return f"Typed & Sent: '{text[:25]}...'" if press_enter else (f"Typed: '{text[:25]}...'" if len(text) > 25 else f"Typed: '{text}'")


def type_live(text: str) -> str:
    """Live real-time typing: native key injection for ASCII, clipboard fallback for Unicode."""
    if not text:
        return ""
    ensure_desktop_attached()
    for ch in text:
        if ch in ("\n", "\r"):
            user32.keybd_event(VK_RETURN, 0, 0, 0)
            user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
        elif ch == "\b":
            user32.keybd_event(VK_BACK, 0, 0, 0)
            user32.keybd_event(VK_BACK, 0, KEYEVENTF_KEYUP, 0)
        elif ch == "\t":
            user32.keybd_event(VK_TAB, 0, 0, 0)
            user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
        else:
            vk = user32.VkKeyScanA(ord(ch)) if ord(ch) < 256 else -1
            if vk != -1:
                vkey = vk & 0xFF
                shift = (vk >> 8) & 0xFF
                if shift & 1:
                    user32.keybd_event(VK_SHIFT, 0, 0, 0)
                user32.keybd_event(vkey, 0, 0, 0)
                user32.keybd_event(vkey, 0, KEYEVENTF_KEYUP, 0)
                if shift & 1:
                    user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
            else:
                pyperclip.copy(ch)
                user32.keybd_event(VK_CONTROL, 0, 0, 0)
                user32.keybd_event(0x56, 0, 0, 0)
                user32.keybd_event(0x56, 0, KEYEVENTF_KEYUP, 0)
                user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    return text


def type_in_notepad(text: str) -> str:
    """Opens Notepad directly on the user's visible physical monitor and types text into it."""
    if not text:
        return "Empty text"
    ensure_desktop_attached()
    try:
        launch_on_default_desktop("notepad.exe")
        time.sleep(1.0)
        type_text(text)
        # Send Enter
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
        return f"Notepad opened and typed: '{text}'"
    except Exception as e:
        return f"Error: {e}"


def press_special_key(key: str) -> str:
    ensure_desktop_attached()
    key_codes = {
        "enter": VK_RETURN,
        "backspace": VK_BACK,
        "escape": VK_ESCAPE,
        "space": VK_SPACE,
        "tab": VK_TAB,
        "up": VK_UP,
        "down": VK_DOWN,
        "left": VK_LEFT,
        "right": VK_RIGHT,
    }
    vk = key_codes.get(key.lower())
    if vk:
        user32.keybd_event(vk, 0, 0, 0)
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        play_feedback_sound()
        return f"Pressed {key.upper()}"
    return f"Unknown key {key}"


def trigger_hotkey(hotkey_name: str) -> str:
    ensure_desktop_attached()
    hk = hotkey_name.lower().strip()

    if hk == "close_window":
        return safe_close_window()
    elif hk == "show_desktop":
        user32.keybd_event(VK_LWIN, 0, 0, 0)
        user32.keybd_event(0x44, 0, 0, 0)  # D
        user32.keybd_event(0x44, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
        play_feedback_sound()
        return "Toggled Desktop"
    elif hk == "alt_tab":
        user32.keybd_event(VK_MENU, 0, 0, 0)  # Alt
        user32.keybd_event(VK_TAB, 0, 0, 0)
        user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
        play_feedback_sound()
        return "Triggered Alt+Tab"
    elif hk == "copy":
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(0x43, 0, 0, 0)  # C
        user32.keybd_event(0x43, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        return "Copied"
    elif hk == "paste":
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(0x56, 0, 0, 0)  # V
        user32.keybd_event(0x56, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        return "Pasted"
    elif hk == "select_all":
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(0x41, 0, 0, 0)  # A
        user32.keybd_event(0x41, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        return "Selected All"
    elif hk == "undo":
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(0x5A, 0, 0, 0)  # Z
        user32.keybd_event(0x5A, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        return "Undo"
    elif hk == "fullscreen":
        user32.keybd_event(VK_F11, 0, 0, 0)
        user32.keybd_event(VK_F11, 0, KEYEVENTF_KEYUP, 0)
        return "Fullscreen Toggled"
    return f"Unknown hotkey {hotkey_name}"


def safe_close_window() -> str:
    """Closes the current active application safely without risking Explorer or Desktop crashes."""
    try:
        ensure_desktop_attached()
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return "No active window found"

        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value.strip()
        low_title = title.lower()

        # Strictly protect system-critical shells and developer IDE
        protected = [
            "program manager",
            "",
            "taskbar",
            "antigravity",
            "windows shell experience host",
            "start",
            "search",
        ]
        if any(p == low_title or (p and p in low_title) for p in protected) or not title:
            return "Desktop & system processes protected"

        # Post WM_CLOSE (0x0010) cleanly to active application
        user32.PostMessageW(hwnd, 0x0010, 0, 0)
        play_feedback_sound()
        return f"Closed window: {title[:25]}"
    except Exception as e:
        return f"Could not close window: {e}"


def lock_screen() -> str:
    user32.LockWorkStation()
    return "PC Locked (Unlock monitor to continue)"


def _launch_via_run_dialog(command: str) -> None:
    """Launches any command/URL on the USER's visible Default desktop using Win+R.
    
    This works even when the server runs inside a sandboxed desktop (like Antigravity IDE)
    because keybd_event sends hardware-level input to the active input desktop.
    """
    ensure_desktop_attached()
    import pyperclip
    
    # 1. Press Win+R to open Run dialog on the user's visible desktop
    user32.keybd_event(VK_LWIN, 0, 0, 0)
    user32.keybd_event(0x52, 0, 0, 0)  # R key
    user32.keybd_event(0x52, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.6)
    
    # 2. Clear any existing text with Ctrl+A then paste command
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(0x41, 0, 0, 0)  # A key (Select All)
    user32.keybd_event(0x41, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.05)
    
    # 3. Copy command to clipboard and paste
    pyperclip.copy(command)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(0x56, 0, 0, 0)  # V key
    user32.keybd_event(0x56, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.15)
    
    # 4. Press Enter to execute
    user32.keybd_event(VK_RETURN, 0, 0, 0)
    user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)


def focus_chrome_window() -> bool:
    """Finds Chrome and brings it to the foreground."""
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
                if "chrome" in title or "google" in title:
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
        return True
    return False


def open_url(url: str) -> str:
    """Opens any website or URL directly on the user's visible physical monitor in Chrome or Edge."""
    if not url:
        return "Empty URL"
    clean_url = url.strip()
    if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
        clean_url = "https://" + clean_url

    ensure_desktop_attached()
    try:
        if os.path.exists(CHROME_PATH):
            cmd = f'"{CHROME_PATH}" "{clean_url}"'
            ok = launch_on_default_desktop(cmd)
            time.sleep(0.3)
            focus_chrome_window()
        elif os.path.exists(EDGE_PATH):
            cmd = f'"{EDGE_PATH}" "{clean_url}"'
            ok = launch_on_default_desktop(cmd)
        else:
            ok = launch_on_default_desktop(f'cmd.exe /c start "" "{clean_url}"')

        play_feedback_sound()
        return f"Opened website: {clean_url}"
    except Exception as e:
        logger.error(f"Error opening URL {clean_url}: {e}")
        return f"Could not open {clean_url}: {e}"


def launch_app(app_name: str) -> str:
    """Universal application and website launcher - displays immediately on user's physical monitor."""
    app = app_name.lower().strip()
    ensure_desktop_attached()
    try:
        # Web destinations
        if app in ["browser", "chrome", "google", "chrom", "gogle"]:
            return open_url("https://www.google.com")
        elif app in ["youtube", "yt", "youtub"]:
            return open_url("https://www.youtube.com")
        elif app in ["whatsapp", "wa", "whatsap"]:
            return open_url("https://web.whatsapp.com")
        elif app in ["chatgpt", "gpt", "ai", "chat gpt"]:
            return open_url("https://chatgpt.com")
        elif app in ["gmail", "email", "mail"]:
            return open_url("https://mail.google.com")
        elif app in ["github"]:
            return open_url("https://github.com")
        elif app in ["facebook", "fb"]:
            return open_url("https://www.facebook.com")
        elif app in ["instagram", "insta"]:
            return open_url("https://www.instagram.com")
        elif app in ["twitter", "x"]:
            return open_url("https://x.com")
        elif app in ["netflix"]:
            return open_url("https://www.netflix.com")
        elif app in ["spotify"]:
            return open_url("https://open.spotify.com")
        elif app in ["reddit"]:
            return open_url("https://www.reddit.com")

        # Windows Applications directly on physical desktop
        elif app in ["notepad", "note"]:
            launch_on_default_desktop("notepad.exe")
            play_feedback_sound()
            return "Notepad Opened"
        elif app in ["calc", "calculator"]:
            launch_on_default_desktop("calc.exe")
            play_feedback_sound()
            return "Calculator Opened"
        elif app in ["explorer", "files", "my_computer", "pc"]:
            launch_on_default_desktop("explorer.exe")
            play_feedback_sound()
            return "File Explorer Opened"
        elif app in ["downloads"]:
            launch_on_default_desktop(f'explorer.exe "{os.path.expanduser("~/Downloads")}"')
            play_feedback_sound()
            return "Downloads Folder Opened"
        elif app in ["documents"]:
            launch_on_default_desktop(f'explorer.exe "{os.path.expanduser("~/Documents")}"')
            play_feedback_sound()
            return "Documents Folder Opened"
        elif app in ["taskmgr", "task_manager"]:
            launch_on_default_desktop("taskmgr.exe")
            play_feedback_sound()
            return "Task Manager Opened"
        elif app in ["paint", "mspaint"]:
            launch_on_default_desktop("mspaint.exe")
            play_feedback_sound()
            return "Paint Opened"
        elif app in ["control", "control_panel"]:
            launch_on_default_desktop("control.exe")
            play_feedback_sound()
            return "Control Panel Opened"
        elif app in ["device_manager"]:
            launch_on_default_desktop("mmc.exe devmgmt.msc")
            play_feedback_sound()
            return "Device Manager Opened"
        elif app in ["settings"]:
            launch_on_default_desktop("cmd.exe /c start ms-settings:")
            play_feedback_sound()
            return "Windows Settings Opened"
        elif app in ["terminal", "cmd"]:
            launch_on_default_desktop("cmd.exe")
            play_feedback_sound()
            return "Command Prompt Opened"
        elif app in ["powershell"]:
            launch_on_default_desktop("powershell.exe")
            play_feedback_sound()
            return "PowerShell Opened"
        elif "." in app and not app.endswith((".exe", ".bat", ".cmd", ".msc", ".py", ".ps1")):
            return open_url(app)
        else:
            if shutil.which(app) or (os.path.exists(app) and app.endswith((".exe", ".bat", ".cmd", ".lnk"))):
                return run_custom_program(app_name)
            else:
                return f"Application or command '{app_name}' not found."
    except Exception as e:
        logger.error(f"Error launching {app_name}: {e}")
        return f"Could not launch {app_name}: {e}"


def run_custom_program(cmd: str) -> str:
    """Launches any executable, URL, or command on the user's visible physical desktop."""
    if not cmd:
        return "Empty command"
    clean_cmd = cmd.strip()

    if ("." in clean_cmd and not clean_cmd.endswith((".exe", ".bat", ".cmd", ".msc", ".py", ".ps1"))
            and "/" not in clean_cmd and "\\" not in clean_cmd and " " not in clean_cmd):
        return open_url(clean_cmd)

    try:
        ok = launch_on_default_desktop(clean_cmd)
        if not ok:
            launch_on_default_desktop(f"cmd.exe /c start {clean_cmd}")
        play_feedback_sound()
        return f"Launched program: {clean_cmd}"
    except Exception as err:
        return f"Could not run '{clean_cmd}': {err}"


def close_app_by_name(target_name: str) -> str:
    """Closes any running application by its process name safely."""
    target = target_name.lower().strip()
    if not target:
        return "Empty app name"

    # Strictly protect operating system critical components, Antigravity IDE, and server processes
    protected = [
        "explorer", "antigravity", "system", "csrss", "lsass",
        "services", "svchost", "wininit", "winlogon", "smss", "fontdrvhost",
        "powershell", "python", "agy", "code"
    ]
    if any(p in target for p in protected):
        return f"Process '{target_name}' is protected to keep system & server running!"

    closed_count = 0
    my_pid = os.getpid()
    parent_pid = psutil.Process(my_pid).ppid() if psutil.pid_exists(my_pid) else None

    for p in psutil.process_iter(["name", "pid"]):
        try:
            if p.info["pid"] in [my_pid, parent_pid]:
                continue
            name = (p.info["name"] or "").lower()
            if target in name:
                p.terminate()
                closed_count += 1
        except Exception:
            pass

    if closed_count > 0:
        play_feedback_sound()
        return f"Closed {closed_count} instance(s) of '{target_name}'"
    return f"No running app found matching '{target_name}'"


def get_running_user_apps() -> List[Dict[str, Any]]:
    """Returns a list of common active user applications for the dashboard."""
    common_apps = {
        "chrome.exe": ("Google Chrome", "🌐"),
        "msedge.exe": ("Microsoft Edge", "🌐"),
        "notepad.exe": ("Notepad", "📝"),
        "calc.exe": ("Calculator", "🧮"),
        "calculatorapp.exe": ("Calculator", "🧮"),
        "vlc.exe": ("VLC Media Player", "🎬"),
        "spotify.exe": ("Spotify", "🎵"),
        "mspaint.exe": ("Paint", "🎨"),
    }
    apps = []
    seen = set()
    for p in psutil.process_iter(["pid", "name"]):
        try:
            name = (p.info["name"] or "").lower()
            if name in common_apps and name not in seen:
                seen.add(name)
                display_name, icon = common_apps[name]
                apps.append({
                    "pid": p.info["pid"],
                    "process_name": p.info["name"],
                    "display_name": display_name,
                    "icon": icon,
                    "short_id": name.replace(".exe", "")
                })
        except Exception:
            pass
    return apps


def system_sleep() -> str:
    try:
        subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "PC entering Sleep mode..."
    except Exception as e:
        return f"Sleep error: {e}"


def system_restart() -> str:
    try:
        subprocess.Popen('shutdown /r /t 10 /c "Restart initiated by Remote Mobile Controller"', shell=True)
        return "PC Restarting in 10 seconds! (To cancel: tap Cancel Shutdown)"
    except Exception as e:
        return f"Restart error: {e}"


def system_shutdown() -> str:
    try:
        subprocess.Popen('shutdown /s /t 15 /c "Shutdown initiated by Remote Mobile Controller"', shell=True)
        return "PC Shutting down in 15 seconds! (To cancel: tap Cancel Shutdown)"
    except Exception as e:
        return f"Shutdown error: {e}"


def system_cancel_shutdown() -> str:
    try:
        subprocess.Popen("shutdown /a", shell=True)
        return "Pending Restart/Shutdown Cancelled!"
    except Exception as e:
        return f"Cancel error: {e}"


# Universal Action Dispatcher
def execute_universal_action(action_type: str, payload: dict[str, Any] = None) -> dict[str, Any]:
    payload = payload or {}
    act = action_type.lower().strip()

    try:
        # Audio & Feedback
        if act in ["beep", "test_ping", "ping"]:
            play_feedback_sound()
            msg = "PC Online & Audio Working! 🔔"
        elif act == "volume_up":
            msg = volume_up()
        elif act == "volume_down":
            msg = volume_down()
        elif act == "volume_mute":
            msg = volume_mute()

        # Media Controls
        elif act == "media_play_pause":
            msg = media_play_pause()
        elif act in ["youtube_play", "play_youtube", "play_video"]:
            msg = play_youtube_video()
        elif act == "media_next":
            msg = media_next()
        elif act == "media_prev":
            msg = media_prev()
        elif act in ["media_seek_forward", "media_seek_fwd", "media_forward"]:
            msg = media_seek("forward")
        elif act in ["media_seek_backward", "media_seek_back", "media_rewind"]:
            msg = media_seek("backward")
        elif act == "media_subtitles":
            msg = media_toggle_subtitles()
        elif act == "media_speed_up":
            msg = media_speed("up")
        elif act == "media_speed_down":
            msg = media_speed("down")
        elif act == "media_fullscreen":
            msg = media_toggle_fullscreen()

        # Presentation Slide Controls
        elif act in ["presentation", "slide_action"]:
            cmd = payload.get("command", "") or payload.get("cmd", "") or payload.get("action", "")
            msg = presentation_action(cmd)
        elif act.startswith("presentation_"):
            cmd = act.replace("presentation_", "")
            msg = presentation_action(cmd)

        # Macro Workflows
        elif act in ["macro", "run_macro"]:
            m_name = payload.get("name", "") or payload.get("macro", "")
            msg = run_macro_workflow(m_name)
        elif act.startswith("macro_"):
            m_name = act.replace("macro_", "")
            msg = run_macro_workflow(m_name)

        # Clipboard Sync
        elif act in ["sync_clipboard", "set_clipboard"]:
            txt = payload.get("text", "")
            pyperclip.copy(txt)
            msg = f"PC Clipboard updated ({len(txt)} chars)"

        # WhatsApp Messaging & Contacts
        elif act in ["whatsapp_send", "send_whatsapp"]:
            recipient = payload.get("recipient", "") or payload.get("phone", "") or payload.get("to", "")
            message_text = payload.get("message", "") or payload.get("text", "")
            from app.whatsapp_sender import send_whatsapp_message
            return send_whatsapp_message(recipient, message_text)
        elif act in ["whatsapp_open_chat", "open_chat"]:
            recipient = payload.get("recipient", "") or payload.get("phone", "") or payload.get("to", "")
            from app.whatsapp_sender import open_whatsapp_chat
            return open_whatsapp_chat(recipient)
        elif act in ["whatsapp_type_message", "type_message"]:
            text = payload.get("text", "") or payload.get("message", "")
            from app.whatsapp_sender import type_whatsapp_message
            return type_whatsapp_message(text)
        elif act in ["whatsapp_send_active", "send_it"]:
            from app.whatsapp_sender import send_active_message
            return send_active_message()
        elif act in ["save_contact", "set_contact"]:
            c_name = payload.get("name", "")
            c_phone = payload.get("phone", "")
            from app.contacts_manager import set_contact
            set_contact(c_name, c_phone)
            msg = f"Contact '{c_name}' saved with number {c_phone}"
            return {"success": True, "message": msg, "action": "save_contact"}
        elif act in ["delete_contact", "remove_contact"]:
            c_name = payload.get("name", "")
            from app.contacts_manager import delete_contact
            delete_contact(c_name)
            return {"success": True, "message": f"Deleted contact '{c_name}'", "action": "delete_contact"}

        # Mouse Controls (Silent stream)
        elif act == "mouse_move":
            dx = int(payload.get("dx", 0))
            dy = int(payload.get("dy", 0))
            msg = mouse_move(dx, dy)
            return {"success": True, "message": msg, "action": act, "silent": True}
        elif act == "mouse_click":
            btn = payload.get("button", "left")
            msg = mouse_click(btn)
        elif act == "mouse_double_click":
            msg = mouse_double_click()
        elif act == "mouse_scroll":
            amt = int(payload.get("amount", 0))
            msg = mouse_scroll(amt)

        # Keyboard & Typing
        elif act in ["type_live", "live_type"]:
            txt = payload.get("text", "")
            msg = type_live(txt)
            return {"success": True, "message": msg, "action": act, "silent": True}
        elif act in ["type_text", "dictate_send"]:
            txt = payload.get("text", "")
            press_enter = bool(payload.get("press_enter", False) or payload.get("auto_send", False) or act == "dictate_send")
            msg = type_text(txt, press_enter=press_enter)
        elif act == "type_in_notepad":
            txt = payload.get("text", "")
            msg = type_in_notepad(txt)
        elif act == "press_key":
            k = payload.get("key", "")
            msg = press_special_key(k)
        elif act == "hotkey":
            hk = payload.get("hotkey", "")
            msg = trigger_hotkey(hk)

        # Open Any URL / Website
        elif act == "open_url":
            target_url = payload.get("url", "")
            msg = open_url(target_url)

        # Run Any Program / Command
        elif act == "run_program":
            prog = payload.get("program", "")
            msg = run_custom_program(prog)

        # Close Specific App By Name
        elif act in ["close_app", "close_process"]:
            pname = payload.get("name", "")
            msg = close_app_by_name(pname)

        # Predefined App Launchers
        elif act.startswith("open_"):
            app_id = act.replace("open_", "")
            msg = launch_app(app_id)

        # Window Controls
        elif act == "close_window":
            msg = safe_close_window()
        elif act == "show_desktop":
            msg = trigger_hotkey("show_desktop")
        elif act == "alt_tab":
            msg = trigger_hotkey("alt_tab")

        # System Session & Power
        elif act == "lock_screen":
            msg = lock_screen()
        elif act == "system_sleep":
            msg = system_sleep()
        elif act == "system_restart":
            msg = system_restart()
        elif act == "system_shutdown":
            msg = system_shutdown()
        elif act == "cancel_shutdown":
            msg = system_cancel_shutdown()

        else:
            msg = f"Unknown action: '{action_type}'"
            logger.warning(msg)
            return {"success": False, "message": msg}

        speak_map = {
            "volume_up": "Volume barha diya gaya hai",
            "volume_down": "Volume kam kar diya gaya hai",
            "volume_mute": "Volume mute ho gaya",
            "media_play_pause": "Media toggle ho gaya",
            "media_next": "Agla track chala diya",
            "media_prev": "Peechla track chala diya",
            "lock_screen": "Computer lock ho chuka hai",
            "show_desktop": "Desktop screen open ho chuki hai",
            "close_window": "Window band kar di gayi hai",
            "open_youtube": "YouTube open ho chuka hai",
            "open_chrome": "Google Chrome open ho chuka hai",
            "open_chatgpt": "ChatGPT open ho chuka hai",
            "open_whatsapp": "WhatsApp open ho chuka hai",
        }
        speak = speak_map.get(act, msg)
        logger.info(f"Action Executed: {act} -> {msg}")
        return {"success": True, "message": msg, "speak": speak, "action": act}

    except Exception as err:
        logger.error(f"Error executing action {act}: {err}")
        return {"success": False, "message": f"Execution error: {str(err)}"}
