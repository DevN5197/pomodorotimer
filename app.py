# app.py  ──  Neon-Dark Premium Edition

import math
import tkinter as tk
from tkinter import messagebox

from settings import load_settings, save_settings
from timer import PomodoroTimer
from notifications import show_notification


# ══════════════════════════════════════════════════════════════
# Colour helpers
# ══════════════════════════════════════════════════════════════

def _hex_rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def _rgb_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def _lerp(c1, c2, t):
    r1, g1, b1 = _hex_rgb(c1)
    r2, g2, b2 = _hex_rgb(c2)
    return _rgb_hex(
        r1 + (r2 - r1) * t,
        g1 + (g2 - g1) * t,
        b1 + (b2 - b1) * t,
    )


# ══════════════════════════════════════════════════════════════
# Canvas drawing helpers
# ══════════════════════════════════════════════════════════════

def _round_rect(canvas, x1, y1, x2, y2, r, **kw):
    """Draw a smooth rounded rectangle on a canvas."""
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
# Custom rounded canvas button
# ══════════════════════════════════════════════════════════════

class _RoundBtn(tk.Canvas):
    """Neon rounded button drawn on a Canvas."""

    def __init__(
        self, parent, text, command,
        w=130, h=46, r=13,
        fill="#FF2D55", fill_h=None,
        fg="#FFFFFF", bg="#0A0A14",
        font_spec=("Segoe UI", 10, "bold"),
        **kw,
    ):
        super().__init__(
            parent, width=w, height=h,
            bg=bg, highlightthickness=0, bd=0, **kw,
        )
        self._cmd     = command
        self._text    = text
        self._fill    = fill
        self._fill_h  = fill_h or _lerp(fill, "#FFFFFF", 0.18)
        self._fg      = fg
        self._font    = font_spec
        self._bw, self._bh, self._br = w, h, r   # btn dims (avoid _w/_h clash w/ Tkinter)
        self._hover   = False

        self._draw()
        self.bind("<Button-1>", lambda e: self._cmd())
        self.bind("<Enter>",    lambda e: self._set_hover(True))
        self.bind("<Leave>",    lambda e: self._set_hover(False))

    def _draw(self):
        self.delete("all")
        color = self._fill_h if self._hover else self._fill
        _round_rect(self, 2, 2, self._bw - 2, self._bh - 2, self._br,
                    fill=color, outline="")
        self.create_text(
            self._bw // 2, self._bh // 2,
            text=self._text, font=self._font, fill=self._fg,
        )

    def _set_hover(self, v):
        self._hover = v
        self._draw()

    def config(self, **kw):
        """Support .config(text=...) like tk.Button."""
        if "text" in kw:
            self._text = kw["text"]
        self._draw()


# ══════════════════════════════════════════════════════════════
# Main Application
# ══════════════════════════════════════════════════════════════

class PomodoroApp:
    """Neon-Dark Premium Pomodoro Application."""

    # ── Colour palette ─────────────────────────────────────────
    BG           = "#0A0A14"   # deep dark navy
    CARD         = "#11111C"   # card background
    CARD_BORDER  = "#1E1E32"   # card border / separator
    CARD2        = "#0E0E1A"   # alternate card shade

    TEXT         = "#E8E8FF"   # warm white
    TEXT_DIM     = "#3A3A5A"   # very dim secondary
    TEXT_MID     = "#7A7A9A"   # medium secondary

    ACCENT_WORK  = "#FF2D55"   # neon red  (work)
    ACCENT_BREAK = "#00D4AA"   # neon teal (short break)
    ACCENT_LONG  = "#BF5FFF"   # neon violet (long break)

    BTN_DIM      = "#18182A"   # secondary button fill
    BTN_DIM_H    = "#22223A"   # secondary button hover

    RING_TRACK   = "#141428"   # arc track
    RING_SIZE    = 238
    RING_PAD     = 16

    # Glow layers: outer → core  (width, lerp-ratio-toward-accent)
    _GLOW_W = [32, 20, 10, 4]
    _GLOW_R = [0.14, 0.38, 0.68, 1.00]

    # ── Init ───────────────────────────────────────────────────

    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("480x750")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.settings_window   = None
        self.daily_sessions    = 0
        self.daily_focus_seconds = 0

        self._accent_cur    = self.ACCENT_WORK
        self._breath_t      = 0.0
        self._breath_after  = None

        self._cfg = load_settings()

        # Build GUI before creating timer (timer callbacks reference widgets)
        self.create_ui()

        self.timer = PomodoroTimer(
            root=self.root,
            work_minutes=self._cfg["work_minutes"],
            short_break_minutes=self._cfg["short_break_minutes"],
            long_break_minutes=self._cfg["long_break_minutes"],
            sessions_before_long_break=self._cfg["sessions_before_long_break"],
            auto_start=self._cfg["auto_start"],
            on_tick=self.update_display,
            on_session_complete=self.session_complete,
        )

        # Keyboard shortcuts
        self.root.bind("<space>", lambda e: self.start_pause())
        self.root.bind("<r>",     lambda e: self.reset_timer())
        self.root.bind("<R>",     lambda e: self.reset_timer())
        self.root.bind("<s>",     lambda e: self.skip_session())
        self.root.bind("<S>",     lambda e: self.skip_session())

        # Initial render
        self.update_display(
            self.timer.remaining_seconds,
            self.timer.total_seconds,
            self.timer.current_session,
            self.timer.completed_sessions,
        )

    # ══════════════════════════════════════════════════════════
    # UI construction
    # ══════════════════════════════════════════════════════════

    def create_ui(self):
        self._build_accent_strip()
        self._build_header()
        self._build_task_entry()
        self._build_timer_card()
        self._build_action_buttons()
        self._build_settings_link()
        self._build_stats_bar()
        self._build_footer()

    # ── Top accent strip ───────────────────────────────────────

    def _build_accent_strip(self):
        self._accent_strip = tk.Frame(self.root, bg=self.ACCENT_WORK, height=3)
        self._accent_strip.pack(fill="x")

    # ── Header ─────────────────────────────────────────────────

    def _build_header(self):
        frm = tk.Frame(self.root, bg=self.BG)
        frm.pack(fill="x", padx=30, pady=(22, 0))

        tk.Label(
            frm, text="🍅  POMODORO",
            font=("Segoe UI", 22, "bold"),
            bg=self.BG, fg=self.TEXT,
        ).pack(side="left")

        self._header_dot = tk.Label(
            frm, text="",
            font=("Segoe UI", 14),
            bg=self.BG, fg=self.ACCENT_WORK,
        )
        self._header_dot.pack(side="right", padx=2, pady=(8, 0))

        tk.Label(
            self.root,
            text="Focus  ·  Work  ·  Rest  ·  Repeat",
            font=("Segoe UI", 9),
            bg=self.BG, fg=self.TEXT_DIM,
        ).pack(pady=(4, 0))

    # ── Task label entry ───────────────────────────────────────

    def _build_task_entry(self):
        outer = tk.Frame(self.root, bg=self.CARD_BORDER)
        outer.pack(fill="x", padx=30, pady=(16, 0), ipady=1)

        inner = tk.Frame(outer, bg=self.CARD)
        inner.pack(fill="x", pady=1)

        self._task_icon = tk.Label(
            inner, text="▸",
            font=("Segoe UI", 11, "bold"),
            bg=self.CARD, fg=self.ACCENT_WORK,
        )
        self._task_icon.pack(side="left", padx=(12, 4), pady=8)

        tk.Label(
            inner, text="Working on:",
            font=("Segoe UI", 9),
            bg=self.CARD, fg=self.TEXT_MID,
        ).pack(side="left", pady=8)

        self.task_var = tk.StringVar()
        self.task_entry = tk.Entry(
            inner,
            textvariable=self.task_var,
            font=("Segoe UI", 10),
            bg=self.CARD, fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat", bd=0,
        )
        self.task_entry.pack(
            side="left", fill="x", expand=True,
            padx=(8, 12), pady=8,
        )

    # ── Timer card ─────────────────────────────────────────────

    def _build_timer_card(self):
        # Border frame (1 px neon border via bg colour)
        self._card_border = tk.Frame(self.root, bg=self.CARD_BORDER)
        self._card_border.pack(padx=30, pady=(18, 0))

        self.card = tk.Frame(self._card_border, bg=self.CARD, width=418, height=408)
        self.card.pack(padx=1, pady=1)
        self.card.pack_propagate(False)

        # ── Session badge ──────────────────────────────────────
        badge_frm = tk.Frame(self.card, bg=self.CARD)
        badge_frm.pack(pady=(22, 0))

        self._badge_cv = tk.Canvas(
            badge_frm, width=190, height=30,
            bg=self.CARD, highlightthickness=0,
        )
        self._badge_cv.pack()

        self._badge_rect = _round_rect(
            self._badge_cv, 0, 0, 190, 30, 10,
            fill=self.ACCENT_WORK, outline="",
        )
        self._badge_text = self._badge_cv.create_text(
            95, 15, text="  WORK SESSION  ",
            font=("Segoe UI", 9, "bold"), fill=self.BG,
        )

        # Invisible compat label (existing code calls .config on it)
        self.session_label = tk.Label(
            self.card, text="", font=("Segoe UI", 1),
            bg=self.CARD, fg=self.CARD,
        )

        # ── Ring ───────────────────────────────────────────────
        rs = self.RING_SIZE
        self.ring_canvas = tk.Canvas(
            self.card, width=rs, height=rs,
            bg=self.CARD, highlightthickness=0,
        )
        self.ring_canvas.pack(pady=(10, 0))

        cx = cy = rs // 2
        pad = self.RING_PAD

        # Track arc (full circle, dim)
        self.ring_canvas.create_arc(
            pad, pad, rs - pad, rs - pad,
            start=90, extent=-359.9,
            style="arc", outline=self.RING_TRACK, width=3,
            tags="track",
        )

        # Glow + core arcs (later = drawn on top)
        self._glow_ids = []
        for tag in ["glow1", "glow2", "glow3", "core"]:
            aid = self.ring_canvas.create_arc(
                pad, pad, rs - pad, rs - pad,
                start=90, extent=0,
                style="arc", outline=self.BG, width=1,
                tags=tag,
            )
            self._glow_ids.append(aid)

        # Initialise widths once
        self._set_ring_widths()

        # Time text
        self._ring_time_id = self.ring_canvas.create_text(
            cx, cy - 14,
            text="25:00",
            font=("Segoe UI", 46, "bold"),
            fill=self.TEXT,
        )

        # Session sub-label inside ring
        self._ring_sub_id = self.ring_canvas.create_text(
            cx, cy + 30,
            text="WORK",
            font=("Segoe UI", 9, "bold"),
            fill=self.ACCENT_WORK,
        )

        # ── Session counter + dot indicators ──────────────────
        info_frm = tk.Frame(self.card, bg=self.CARD)
        info_frm.pack(pady=(6, 0))

        self.session_counter = tk.Label(
            info_frm, text="Session 1 / 4",
            font=("Segoe UI", 10),
            bg=self.CARD, fg=self.TEXT_MID,
        )
        self.session_counter.pack()

        n = self._cfg["sessions_before_long_break"]
        self._dots_w = n * 22 + 10
        self.dots_canvas = tk.Canvas(
            info_frm, width=self._dots_w, height=20,
            bg=self.CARD, highlightthickness=0,
        )
        self.dots_canvas.pack(pady=(6, 0))

        self._dot_ids     = []
        self.progress_dots = []   # compat shim
        self._build_dots(n)

    # ── Action buttons ─────────────────────────────────────────

    def _build_action_buttons(self):
        frm = tk.Frame(self.root, bg=self.BG)
        frm.pack(pady=(18, 0))

        self.start_button = _RoundBtn(
            frm, "▶  START", self.start_pause,
            w=144, h=48, r=14,
            fill=self.ACCENT_WORK, fg="#FFFFFF", bg=self.BG,
        )
        self.start_button.pack(side="left", padx=6)

        _RoundBtn(
            frm, "↻  RESET", self.reset_timer,
            w=120, h=48, r=14,
            fill=self.BTN_DIM, fill_h=self.BTN_DIM_H,
            fg=self.TEXT, bg=self.BG,
        ).pack(side="left", padx=6)

        self.skip_button = _RoundBtn(
            frm, "⏭  SKIP", self.skip_session,
            w=110, h=48, r=14,
            fill=self.BTN_DIM, fill_h=self.BTN_DIM_H,
            fg=self.TEXT_MID, bg=self.BG,
        )
        self.skip_button.pack(side="left", padx=6)

    # ── Settings link ──────────────────────────────────────────

    def _build_settings_link(self):
        tk.Button(
            self.root, text="⚙  Settings",
            command=self.open_settings,
            font=("Segoe UI", 9),
            bg=self.BG, fg=self.TEXT_DIM,
            activebackground=self.BG, activeforeground=self.TEXT,
            relief="flat", bd=0, cursor="hand2",
        ).pack(pady=(10, 0))

    # ── Daily stats bar ────────────────────────────────────────

    def _build_stats_bar(self):
        outer = tk.Frame(self.root, bg=self.CARD_BORDER)
        outer.pack(fill="x", padx=30, pady=(10, 0), ipady=1)

        bar = tk.Frame(outer, bg=self.CARD)
        bar.pack(fill="x", pady=1)

        tk.Label(
            bar, text="TODAY",
            font=("Segoe UI", 7, "bold"),
            bg=self.CARD, fg=self.TEXT_DIM,
        ).pack(side="left", padx=(16, 0), pady=10)

        tk.Frame(bar, bg=self.CARD_BORDER, width=1, height=18).pack(
            side="left", padx=14, pady=7,
        )

        self.stats_sessions_label = tk.Label(
            bar, text="🍅  0 sessions",
            font=("Segoe UI", 9),
            bg=self.CARD, fg=self.TEXT,
        )
        self.stats_sessions_label.pack(side="left", pady=10)

        tk.Frame(bar, bg=self.CARD_BORDER, width=1, height=18).pack(
            side="left", padx=14, pady=7,
        )

        self.stats_focus_label = tk.Label(
            bar, text="⏱  0 min focused",
            font=("Segoe UI", 9),
            bg=self.CARD, fg=self.TEXT,
        )
        self.stats_focus_label.pack(side="left", pady=10)

    # ── Footer ─────────────────────────────────────────────────

    def _build_footer(self):
        tk.Label(
            self.root,
            text="Space · start/pause    R · reset    S · skip",
            font=("Segoe UI", 8),
            bg=self.BG, fg=self.TEXT_DIM,
        ).pack(pady=(10, 0))

        self.status_label = tk.Label(
            self.root, text="Ready to focus.",
            font=("Segoe UI", 9),
            bg=self.BG, fg=self.TEXT_MID,
        )
        self.status_label.pack(side="bottom", pady=10)

    # ══════════════════════════════════════════════════════════
    # Dot helpers
    # ══════════════════════════════════════════════════════════

    def _build_dots(self, n):
        """(Re)build the canvas dot indicators."""
        self.dots_canvas.delete("all")
        self._dot_ids      = []
        self.progress_dots = []      # compat

        dot_w = n * 22 + 10
        self.dots_canvas.config(width=dot_w)

        for i in range(n):
            cx = 11 + i * 22
            cy = 10
            oid = self.dots_canvas.create_oval(
                cx - 6, cy - 6, cx + 6, cy + 6,
                fill=self.TEXT_DIM, outline="",
            )
            self._dot_ids.append(oid)
            self.progress_dots.append(oid)

    def _update_dots(self, completed_in_cycle, accent):
        for i, oid in enumerate(self._dot_ids):
            self.dots_canvas.itemconfig(
                oid,
                fill=accent if i < completed_in_cycle else self.TEXT_DIM,
            )

    # ══════════════════════════════════════════════════════════
    # Ring drawing
    # ══════════════════════════════════════════════════════════

    def _set_ring_widths(self):
        """Apply static widths to all glow arcs."""
        for aid, w in zip(self._glow_ids, self._GLOW_W):
            self.ring_canvas.itemconfig(aid, width=w)

    def _draw_ring(self, remaining, total, session_type):
        """Update ring arc extents and glow colours."""
        fraction = (remaining / total) if total else 1.0
        extent   = -360.0 * fraction
        accent   = self._accent_for(session_type)

        glow_colors = [_lerp(self.CARD, accent, r) for r in self._GLOW_R]

        for aid, color in zip(self._glow_ids, glow_colors):
            self.ring_canvas.itemconfig(aid, extent=extent, outline=color)

    def _accent_for(self, session_type):
        return {
            PomodoroTimer.WORK:        self.ACCENT_WORK,
            PomodoroTimer.SHORT_BREAK: self.ACCENT_BREAK,
            PomodoroTimer.LONG_BREAK:  self.ACCENT_LONG,
        }.get(session_type, self.ACCENT_WORK)

    # ── Breathing animation (pulses while running) ─────────────

    def _start_breathing(self):
        self._breath_t = 0.0
        self._breathe()

    def _stop_breathing(self):
        if self._breath_after is not None:
            try:
                self.root.after_cancel(self._breath_after)
            except Exception:
                pass
            self._breath_after = None
        # Reset to static widths
        self._set_ring_widths()
        self._header_dot.config(text="")

    def _breathe(self):
        if not (hasattr(self, "timer") and self.timer.running):
            return
        self._breath_t += 0.07
        t = math.sin(self._breath_t) * 0.5 + 0.5       # 0 → 1 sine
        # Pulse outer glow width
        base_w = self._GLOW_W[0]
        self.ring_canvas.itemconfig(self._glow_ids[0], width=int(base_w + t * 14))
        # Blink header dot
        self._header_dot.config(
            text="●" if int(self._breath_t * 3) % 2 == 0 else "◌",
            fg=self._accent_cur,
        )
        self._breath_after = self.root.after(50, self._breathe)

    # ── Badge + strip update ───────────────────────────────────

    def _update_badge(self, session_type):
        names = {
            PomodoroTimer.WORK:        "  WORK SESSION  ",
            PomodoroTimer.SHORT_BREAK: "  SHORT BREAK   ",
            PomodoroTimer.LONG_BREAK:  "  LONG BREAK    ",
        }
        sub = {
            PomodoroTimer.WORK:        "WORK",
            PomodoroTimer.SHORT_BREAK: "BREAK",
            PomodoroTimer.LONG_BREAK:  "LONG BREAK",
        }
        accent = self._accent_for(session_type)

        self._badge_cv.itemconfig(self._badge_rect, fill=accent)
        self._badge_cv.itemconfig(self._badge_text, text=names[session_type])
        self.ring_canvas.itemconfig(self._ring_sub_id,
                                    text=sub[session_type], fill=accent)
        self._accent_strip.config(bg=accent)
        self._task_icon.config(fg=accent)
        # Keep compat label invisible
        self.session_label.config(text="", fg=self.CARD)

    # ══════════════════════════════════════════════════════════
    # Timer controls
    # ══════════════════════════════════════════════════════════

    def start_pause(self):
        if self.timer.running:
            self.timer.pause()
            self.start_button.config(text="▶  RESUME")
            self.status_label.config(text="Timer paused.")
            self._stop_breathing()
        else:
            self.timer.start()
            self.start_button.config(text="⏸  PAUSE")
            self.status_label.config(text="Focus mode active.")
            self._start_breathing()

    def reset_timer(self):
        self._stop_breathing()
        self.timer.reset()
        self.start_button.config(text="▶  START")
        self.status_label.config(text="Ready to focus.")
        self.root.title("Pomodoro Timer")

    def skip_session(self):
        self._stop_breathing()
        self.timer.skip()
        self.start_button.config(text="▶  START")
        self.status_label.config(text="Session skipped.")

    # ══════════════════════════════════════════════════════════
    # Display update  (called every second by the timer)
    # ══════════════════════════════════════════════════════════

    def update_display(
        self,
        remaining_seconds,
        total_seconds,
        session_type,
        completed_sessions,
    ):
        minutes  = remaining_seconds // 60
        seconds  = remaining_seconds % 60
        time_str = f"{minutes:02d}:{seconds:02d}"

        # Time text on ring
        self.ring_canvas.itemconfig(self._ring_time_id, text=time_str)

        # Window title bar shows live countdown
        title_names = {
            PomodoroTimer.WORK:        "Work",
            PomodoroTimer.SHORT_BREAK: "Short Break",
            PomodoroTimer.LONG_BREAK:  "Long Break",
        }
        self.root.title(f"{time_str}  ·  {title_names[session_type]}")

        # Accent + badge + strip
        accent = self._accent_for(session_type)
        self._accent_cur = accent
        self._update_badge(session_type)

        # Ring
        self._draw_ring(remaining_seconds, total_seconds, session_type)

        # Cycle maths
        s_cycle = self.timer.sessions_before_long_break
        if session_type == PomodoroTimer.LONG_BREAK:
            completed_in_cycle = s_cycle
        else:
            completed_in_cycle = completed_sessions % s_cycle

        # Session counter text
        if session_type == PomodoroTimer.WORK:
            self.session_counter.config(
                text=f"Session {completed_in_cycle + 1} / {s_cycle}"
            )
        elif session_type == PomodoroTimer.SHORT_BREAK:
            self.session_counter.config(
                text=f"Short Break  ·  {completed_in_cycle} / {s_cycle} done"
            )
        else:
            self.session_counter.config(
                text=f"Long Break  ·  all {s_cycle} sessions done"
            )

        # Dot indicators
        self._update_dots(completed_in_cycle, accent)

    # ══════════════════════════════════════════════════════════
    # Session complete callback
    # ══════════════════════════════════════════════════════════

    def session_complete(self, session_type, completed_sessions):
        self._stop_breathing()

        if session_type == PomodoroTimer.WORK:
            self.daily_sessions     += 1
            self.daily_focus_seconds += self.timer.work_minutes * 60
            self._update_stats_bar()

        if session_type == PomodoroTimer.WORK:
            if completed_sessions % self.timer.sessions_before_long_break == 0:
                show_notification(
                    self.root,
                    f"🎉 {self.timer.sessions_before_long_break} Sessions Complete!",
                    "Excellent work! Time for your long break.",
                )
            else:
                show_notification(
                    self.root,
                    "🍅 Work Session Complete!",
                    "Great work! Time for a short break.",
                )
        elif session_type == PomodoroTimer.SHORT_BREAK:
            show_notification(
                self.root, "☕ Break Complete!", "Time to get back to work."
            )
        elif session_type == PomodoroTimer.LONG_BREAK:
            show_notification(
                self.root, "🌴 Long Break Complete!", "Ready for another cycle?"
            )

        self.start_button.config(text="▶  START")
        self.status_label.config(text="Session complete!")

        if self.timer.auto_start:
            self._start_breathing()

    def _update_stats_bar(self):
        mins = self.daily_focus_seconds // 60
        s    = "s" if self.daily_sessions != 1 else ""
        self.stats_sessions_label.config(
            text=f"🍅  {self.daily_sessions} session{s}"
        )
        self.stats_focus_label.config(text=f"⏱  {mins} min focused")

    # ══════════════════════════════════════════════════════════
    # Settings window
    # ══════════════════════════════════════════════════════════

    def open_settings(self):
        if (
            self.settings_window is not None
            and self.settings_window.winfo_exists()
        ):
            self.settings_window.focus()
            return

        win = tk.Toplevel(self.root)
        self.settings_window = win
        win.title("Settings")
        win.geometry("390x500")
        win.resizable(False, False)
        win.configure(bg=self.BG)
        win.transient(self.root)
        win.grab_set()

        # Top accent strip on settings window
        tk.Frame(win, bg=self.ACCENT_WORK, height=3).pack(fill="x")

        tk.Label(
            win, text="⚙  Settings",
            font=("Segoe UI", 18, "bold"),
            bg=self.BG, fg=self.TEXT,
        ).pack(pady=(24, 4))

        tk.Label(
            win,
            text="Changes reset the current timer.",
            font=("Segoe UI", 8),
            bg=self.BG, fg=self.TEXT_DIM,
        ).pack()

        # Fields card
        fields_border = tk.Frame(win, bg=self.CARD_BORDER)
        fields_border.pack(fill="x", padx=30, pady=(22, 0), ipady=1)

        fields = tk.Frame(fields_border, bg=self.CARD)
        fields.pack(fill="x", padx=1, pady=1)

        work_var  = tk.StringVar(value=str(self.timer.work_minutes))
        short_var = tk.StringVar(value=str(self.timer.short_break_minutes))
        long_var  = tk.StringVar(value=str(self.timer.long_break_minutes))
        cycle_var = tk.StringVar(value=str(self.timer.sessions_before_long_break))

        first = True
        for lbl, var in [
            ("Work duration (min)",  work_var),
            ("Short break (min)",    short_var),
            ("Long break (min)",     long_var),
            ("Sessions per cycle",   cycle_var),
        ]:
            if not first:
                tk.Frame(fields, bg=self.CARD_BORDER, height=1).pack(fill="x")
            self._create_setting_field(fields, lbl, var)
            first = False

        # Auto-start toggle
        auto_border = tk.Frame(win, bg=self.CARD_BORDER)
        auto_border.pack(fill="x", padx=30, pady=(10, 0), ipady=1)

        auto_row = tk.Frame(auto_border, bg=self.CARD)
        auto_row.pack(fill="x", padx=1, pady=1)

        auto_var = tk.BooleanVar(value=self.timer.auto_start)

        tk.Label(
            auto_row, text="Auto-start next session",
            font=("Segoe UI", 10),
            bg=self.CARD, fg=self.TEXT,
        ).pack(side="left", padx=16, pady=12)

        tk.Checkbutton(
            auto_row, variable=auto_var,
            bg=self.CARD, activebackground=self.CARD,
            selectcolor=self.BTN_DIM, cursor="hand2",
        ).pack(side="right", padx=16)

        # Save button
        _RoundBtn(
            win, "SAVE SETTINGS",
            lambda: self._save_settings(
                work_var, short_var, long_var, cycle_var, auto_var
            ),
            w=210, h=46, r=13,
            fill=self.ACCENT_WORK, fg="#FFFFFF", bg=self.BG,
        ).pack(pady=28)

    def _create_setting_field(self, parent, label, variable):
        row = tk.Frame(parent, bg=self.CARD)
        row.pack(fill="x")

        tk.Label(
            row, text=label,
            font=("Segoe UI", 10),
            bg=self.CARD, fg=self.TEXT,
        ).pack(side="left", padx=16, pady=13)

        tk.Entry(
            row, textvariable=variable,
            font=("Segoe UI", 10), width=6,
            justify="center",
            bg=self.BTN_DIM, fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
        ).pack(side="right", padx=16, ipady=5)

    def _save_settings(self, work_var, short_var, long_var, cycle_var, auto_var):
        try:
            work  = int(work_var.get())
            short = int(short_var.get())
            long_ = int(long_var.get())
            cycle = int(cycle_var.get())
            if work <= 0 or short <= 0 or long_ <= 0 or cycle <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Settings",
                "Please enter positive whole numbers.",
                parent=self.settings_window,
            )
            return

        auto = auto_var.get()
        cfg  = {
            "work_minutes":               work,
            "short_break_minutes":        short,
            "long_break_minutes":         long_,
            "sessions_before_long_break": cycle,
            "auto_start":                 auto,
        }
        save_settings(cfg)
        self._cfg = cfg

        if cycle != len(self._dot_ids):
            self._build_dots(cycle)

        self._stop_breathing()
        self.timer.update_settings(work, short, long_, cycle, auto)
        self.start_button.config(text="▶  START")
        self.status_label.config(text="Settings updated.")
        self.settings_window.destroy()

    # ══════════════════════════════════════════════════════════
    # Close
    # ══════════════════════════════════════════════════════════

    def on_close(self):
        self._stop_breathing()
        if hasattr(self, "timer") and self.timer and self.timer.after_id:
            try:
                self.root.after_cancel(self.timer.after_id)
            except Exception:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app  = PomodoroApp(root)
    root.mainloop()
