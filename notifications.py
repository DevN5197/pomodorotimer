
# notifications.py

import sys
import tkinter as tk


def play_notification(root):
    """Play a system notification sound."""
    try:
        if sys.platform == "win32":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            root.bell()
    except Exception:
        try:
            root.bell()
        except Exception:
            pass


def show_notification(root, title, message):
    """Show a styled popup notification when a Pomodoro session finishes."""

    popup = tk.Toplevel(root)

    popup.title(title)
    popup.geometry("360x200")
    popup.resizable(False, False)
    popup.configure(bg="#1E1E1E")

    # Keep popup above the main window and bring to front
    popup.transient(root)
    popup.attributes("-topmost", True)
    popup.lift()
    popup.focus_force()

    # Title
    tk.Label(
        popup,
        text=title,
        font=("Segoe UI", 14, "bold"),
        bg="#1E1E1E",
        fg="#FFFFFF"
    ).pack(pady=(20, 8))

    # Message
    tk.Label(
        popup,
        text=message,
        font=("Segoe UI", 10),
        bg="#1E1E1E",
        fg="#AAAAAA",
        wraplength=310,
        justify="center"
    ).pack(pady=5)

    # OK button
    tk.Button(
        popup,
        text="OK",
        font=("Segoe UI", 10, "bold"),
        bg="#E63946",
        fg="white",
        activebackground="#D62828",
        activeforeground="white",
        relief="flat",
        bd=0,
        width=12,
        height=1,
        cursor="hand2",
        command=popup.destroy
    ).pack(pady=18)

    # Play sound
    play_notification(root)

