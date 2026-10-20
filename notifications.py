
# notifications.py  ──  Neon-Dark Premium Edition

import sys
import tkinter as tk


# ══════════════════════════════════════════════════════════════
# Colour helpers (duplicated here to keep module self-contained)
# ══════════════════════════════════════════════════════════════

def _round_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [
        x1 + r, y1,    x2 - r, y1,
        x2,     y1,    x2,     y1 + r,
        x2,     y2 - r, x2,    y2,
        x2 - r, y2,    x1 + r, y2,
        x1,     y2,    x1,     y2 - r,
        x1,     y1 + r, x1,    y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


# ══════════════════════════════════════════════════════════════
# Sound
# ══════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════
# Popup
# ══════════════════════════════════════════════════════════════

BG          = "#0A0A14"
CARD        = "#13131E"
CARD_BORDER = "#252538"
TEXT        = "#E8E8FF"
TEXT_MID    = "#7A7A9A"
ACCENT      = "#FF2D55"


def show_notification(root, title, message, auto_close_ms=10_000):
    """
    Neon-styled popup notification.
    Auto-closes after `auto_close_ms` milliseconds.
    """
    popup = tk.Toplevel(root)
    popup.title("")
    popup.geometry("380x230")
    popup.resizable(False, False)
    popup.configure(bg=BG)
    popup.transient(root)
    popup.attributes("-topmost", True)
    popup.lift()
    popup.focus_force()

    # Remove default window decorations slightly (Windows only via overrideredirect)
    # We keep title bar for accessibility but style the content area

    # ── Top accent strip ──────────────────────────────────────
    tk.Frame(popup, bg=ACCENT, height=3).pack(fill="x")

    # ── Content card ─────────────────────────────────────────
    outer = tk.Frame(popup, bg=CARD_BORDER)
    outer.pack(fill="both", expand=True, padx=20, pady=16, ipady=1)

    card = tk.Frame(outer, bg=CARD)
    card.pack(fill="both", expand=True, padx=1, pady=1)

    # Title
    tk.Label(
        card, text=title,
        font=("Segoe UI", 13, "bold"),
        bg=CARD, fg=TEXT,
        wraplength=320, justify="center",
    ).pack(pady=(18, 6))

    # Message
    tk.Label(
        card, text=message,
        font=("Segoe UI", 10),
        bg=CARD, fg=TEXT_MID,
        wraplength=320, justify="center",
    ).pack(pady=(0, 8))

    # Countdown
    countdown_label = tk.Label(
        card,
        text=f"Closing in {auto_close_ms // 1000}s",
        font=("Segoe UI", 8),
        bg=CARD, fg="#2A2A42",
    )
    countdown_label.pack()

    # ── OK button (canvas-based round) ───────────────────────
    btn_cv = tk.Canvas(card, width=120, height=36,
                       bg=CARD, highlightthickness=0)
    btn_cv.pack(pady=(10, 16))

    def _draw_btn(hover=False):
        btn_cv.delete("all")
        color = "#FF4D6E" if hover else ACCENT
        _round_rect(btn_cv, 2, 2, 118, 34, 10, fill=color, outline="")
        btn_cv.create_text(60, 18, text="OK",
                           font=("Segoe UI", 10, "bold"), fill="#FFFFFF")

    _draw_btn()
    btn_cv.bind("<Button-1>", lambda e: popup.destroy())
    btn_cv.bind("<Enter>",    lambda e: _draw_btn(hover=True))
    btn_cv.bind("<Leave>",    lambda e: _draw_btn(hover=False))

    # ── Auto-close countdown ──────────────────────────────────
    play_notification(root)

    remaining = [auto_close_ms // 1000]

    def _tick():
        if not popup.winfo_exists():
            return
        remaining[0] -= 1
        if remaining[0] <= 0:
            popup.destroy()
            return
        countdown_label.config(text=f"Closing in {remaining[0]}s")
        popup.after(1000, _tick)

    popup.after(1000, _tick)
