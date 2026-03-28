"""
Cobo Gaming Mode Toggle - System Tray Application
Toggles between WORK MODE and GAMING MODE via system tray icon.
Writes state to C:\behique\mode.json for BIOS coordination.

Requirements: pip install pystray Pillow
Fallback: Uses tkinter if pystray is not available.
"""

import json
import os
import sys
import threading
from pathlib import Path

# --- Configuration ---
MODE_FILE = Path(r"C:\behique\mode.json")
MODE_NORMAL = "normal"
MODE_GAMING = "gaming"

# --- Mode persistence ---

def ensure_mode_dir():
    """Create the behique directory if it doesn't exist."""
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)

def read_mode():
    """Read current mode from mode.json. Returns 'normal' if file missing/corrupt."""
    try:
        with open(MODE_FILE, "r") as f:
            data = json.load(f)
            return data.get("mode", MODE_NORMAL)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return MODE_NORMAL

def write_mode(mode):
    """Write mode to mode.json."""
    ensure_mode_dir()
    with open(MODE_FILE, "w") as f:
        json.dump({"mode": mode}, f, indent=2)

# --- Toast notifications ---

def show_notification(title, message):
    """Show a Windows toast notification. Falls back to print if unavailable."""
    try:
        # Try win10toast first
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=3, threaded=True)
        return
    except ImportError:
        pass

    try:
        # Try plyer as fallback
        from plyer import notification
        notification.notify(title=title, message=message, timeout=3)
        return
    except ImportError:
        pass

    try:
        # Try Windows-native PowerShell toast
        import subprocess
        ps_script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = @"
        <toast>
            <visual>
                <binding template="ToastGeneric">
                    <text>{title}</text>
                    <text>{message}</text>
                </binding>
            </visual>
        </toast>
"@
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Cobo BIOS").Show($toast)
        """
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return
    except Exception:
        pass

    # Last resort: just print
    print(f"[{title}] {message}")


# --- Icon generation ---

def create_icon_image(color):
    """Create a simple colored circle icon using Pillow."""
    from PIL import Image, ImageDraw
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw filled circle
    margin = 4
    draw.ellipse([margin, margin, size - margin, size - margin], fill=color)
    # Draw a small "G" or "W" in the center
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 28)
    except (OSError, IOError):
        font = ImageFont.load_default()

    letter = "W" if color == "green" else "G"
    text_color = "white"
    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 2), letter, fill=text_color, font=font)
    return img


# ============================================================
# Try pystray-based system tray (preferred)
# ============================================================

def run_pystray():
    """Run the system tray app using pystray."""
    import pystray
    from pystray import MenuItem as item

    current_mode = read_mode()

    def get_icon_image():
        color = "green" if current_mode == MODE_NORMAL else "red"
        return create_icon_image(color)

    def get_title():
        if current_mode == MODE_NORMAL:
            return "Cobo - WORK MODE"
        return "Cobo - GAMING MODE"

    def toggle(icon, _=None):
        nonlocal current_mode
        if current_mode == MODE_NORMAL:
            current_mode = MODE_GAMING
            write_mode(MODE_GAMING)
            show_notification("Gaming Mode ON", "BIOS tasks paused")
        else:
            current_mode = MODE_NORMAL
            write_mode(MODE_NORMAL)
            show_notification("Work Mode ON", "BIOS tasks active")
        icon.icon = get_icon_image()
        icon.title = get_title()
        icon.update_menu()

    def set_work(icon, _):
        nonlocal current_mode
        if current_mode != MODE_NORMAL:
            current_mode = MODE_NORMAL
            write_mode(MODE_NORMAL)
            show_notification("Work Mode ON", "BIOS tasks active")
            icon.icon = get_icon_image()
            icon.title = get_title()
            icon.update_menu()

    def set_gaming(icon, _):
        nonlocal current_mode
        if current_mode != MODE_GAMING:
            current_mode = MODE_GAMING
            write_mode(MODE_GAMING)
            show_notification("Gaming Mode ON", "BIOS tasks paused")
            icon.icon = get_icon_image()
            icon.title = get_title()
            icon.update_menu()

    def show_status(icon, _):
        mode_label = "WORK MODE" if current_mode == MODE_NORMAL else "GAMING MODE"
        show_notification("Cobo Status", f"Current mode: {mode_label}")

    def on_quit(icon, _):
        icon.stop()

    def is_work_mode(_):
        return current_mode == MODE_NORMAL

    def is_gaming_mode(_):
        return current_mode == MODE_GAMING

    menu = pystray.Menu(
        item("Work Mode", set_work, checked=is_work_mode),
        item("Gaming Mode", set_gaming, checked=is_gaming_mode),
        pystray.Menu.SEPARATOR,
        item("Status", show_status),
        item("Exit", on_quit),
    )

    icon = pystray.Icon(
        "cobo_gaming_toggle",
        get_icon_image(),
        get_title(),
        menu,
    )

    # Left-click toggles mode
    icon.on_activate = toggle

    icon.run()


# ============================================================
# Tkinter fallback (if pystray not available)
# ============================================================

def run_tkinter_fallback():
    """Fallback GUI using tkinter (no system tray, just a small window)."""
    import tkinter as tk
    from tkinter import messagebox

    current_mode = read_mode()

    root = tk.Tk()
    root.title("Cobo Gaming Toggle")
    root.geometry("300x200")
    root.resizable(False, False)

    # Try to keep window on top
    root.attributes("-topmost", True)

    mode_var = tk.StringVar(value=current_mode)

    def update_ui():
        if mode_var.get() == MODE_NORMAL:
            status_label.config(text="WORK MODE", fg="green", bg="#1a1a2e")
            toggle_btn.config(text="Switch to Gaming Mode", bg="#cc3333", fg="white")
            root.configure(bg="#1a1a2e")
        else:
            status_label.config(text="GAMING MODE", fg="red", bg="#1a1a2e")
            toggle_btn.config(text="Switch to Work Mode", bg="#33cc33", fg="white")
            root.configure(bg="#1a1a2e")

    def toggle():
        if mode_var.get() == MODE_NORMAL:
            mode_var.set(MODE_GAMING)
            write_mode(MODE_GAMING)
            show_notification("Gaming Mode ON", "BIOS tasks paused")
        else:
            mode_var.set(MODE_NORMAL)
            write_mode(MODE_NORMAL)
            show_notification("Work Mode ON", "BIOS tasks active")
        update_ui()

    def show_status():
        mode_label = "WORK MODE" if mode_var.get() == MODE_NORMAL else "GAMING MODE"
        messagebox.showinfo("Cobo Status", f"Current mode: {mode_label}")

    # Dark theme
    root.configure(bg="#1a1a2e")

    title_label = tk.Label(
        root, text="COBO", font=("Consolas", 20, "bold"),
        fg="#00ffcc", bg="#1a1a2e"
    )
    title_label.pack(pady=(15, 5))

    status_label = tk.Label(
        root, text="", font=("Consolas", 16, "bold"),
        bg="#1a1a2e"
    )
    status_label.pack(pady=5)

    toggle_btn = tk.Button(
        root, text="", font=("Consolas", 11, "bold"),
        command=toggle, relief="flat", padx=15, pady=8, cursor="hand2"
    )
    toggle_btn.pack(pady=10)

    status_btn = tk.Button(
        root, text="Status", font=("Consolas", 9),
        command=show_status, bg="#333355", fg="#aaaacc",
        relief="flat", padx=10, pady=3, cursor="hand2"
    )
    status_btn.pack()

    update_ui()

    # Minimize to taskbar behavior
    def on_close():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    try:
        import pystray
        from PIL import Image
        run_pystray()
    except ImportError:
        print("pystray/Pillow not found, using tkinter fallback...")
        run_tkinter_fallback()
