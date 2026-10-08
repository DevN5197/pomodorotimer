# app.py

import tkinter as tk
from tkinter import messagebox

from settings import (
    DEFAULT_WORK_MINUTES,
    DEFAULT_SHORT_BREAK_MINUTES,
    DEFAULT_LONG_BREAK_MINUTES,
    SESSIONS_BEFORE_LONG_BREAK
)

from timer import PomodoroTimer
from notifications import show_notification


class PomodoroApp:
    """Main Pomodoro desktop application."""

    BG = "#121212"
    CARD = "#1E1E1E"
    TEXT = "#FFFFFF"
    SECONDARY_TEXT = "#AAAAAA"
    ACCENT = "#E63946"
    BUTTON = "#2A2A2A"

    def __init__(self, root):

        self.root = root

        self.root.title("Pomodoro Timer")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        # Prevent multiple settings windows
        self.settings_window = None

        # IMPORTANT:
        # Create the GUI BEFORE creating the timer.
        # The timer immediately calls update_display(),
        # so time_label and other widgets must already exist.
        self.create_ui()

        # Create timer AFTER GUI exists
        self.timer = PomodoroTimer(
            root=self.root,
            work_minutes=DEFAULT_WORK_MINUTES,
            short_break_minutes=DEFAULT_SHORT_BREAK_MINUTES,
            long_break_minutes=DEFAULT_LONG_BREAK_MINUTES,
            on_tick=self.update_display,
            on_session_complete=self.session_complete
        )

        # Show initial state
        self.update_display(
            self.timer.remaining_seconds,
            self.timer.current_session,
            self.timer.completed_sessions
        )

    # =========================================================
    # GUI
    # =========================================================

    def create_ui(self):
        """Create all GUI components."""

        # -------------------------
        # Title
        # -------------------------

        title = tk.Label(
            self.root,
            text="🍅  POMODORO",
            font=("Segoe UI", 24, "bold"),
            bg=self.BG,
            fg=self.TEXT
        )

        title.pack(pady=(30, 5))

        subtitle = tk.Label(
            self.root,
            text="Focus. Work. Rest. Repeat.",
            font=("Segoe UI", 10),
            bg=self.BG,
            fg=self.SECONDARY_TEXT
        )

        subtitle.pack()

        # -------------------------
        # Main card
        # -------------------------

        self.card = tk.Frame(
            self.root,
            bg=self.CARD,
            width=420,
            height=390
        )

        self.card.pack(
            padx=40,
            pady=25,
            fill="both",
            expand=False
        )

        self.card.pack_propagate(False)

        # -------------------------
        # Session label
        # -------------------------

        self.session_label = tk.Label(
            self.card,
            text="WORK SESSION",
            font=("Segoe UI", 13, "bold"),
            bg=self.CARD,
            fg=self.ACCENT
        )

        self.session_label.pack(pady=(35, 10))

        # -------------------------
        # Timer display
        # -------------------------

        self.time_label = tk.Label(
            self.card,
            text="25:00",
            font=("Segoe UI", 65, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        )

        self.time_label.pack(pady=10)

        # -------------------------
        # Session counter
        # -------------------------

        self.session_counter = tk.Label(
            self.card,
            text="Session 1 / 4",
            font=("Segoe UI", 11),
            bg=self.CARD,
            fg=self.SECONDARY_TEXT
        )

        self.session_counter.pack(pady=10)

        # -------------------------
        # Progress dots
        # -------------------------

        self.progress_frame = tk.Frame(
            self.card,
            bg=self.CARD
        )

        self.progress_frame.pack(pady=5)

        self.progress_dots = []

        for _ in range(SESSIONS_BEFORE_LONG_BREAK):

            dot = tk.Label(
                self.progress_frame,
                text="●",
                font=("Segoe UI", 14),
                bg=self.CARD,
                fg="#444444"
            )

            dot.pack(
                side="left",
                padx=5
            )

            self.progress_dots.append(dot)

        # -------------------------
        # Buttons
        # -------------------------

        button_frame = tk.Frame(
            self.card,
            bg=self.CARD
        )

        button_frame.pack(pady=25)

        self.start_button = tk.Button(
            button_frame,
            text="▶  START",
            command=self.start_pause,
            font=("Segoe UI", 11, "bold"),
            bg=self.ACCENT,
            fg="white",
            activebackground=self.ACCENT,
            activeforeground="white",
            relief="flat",
            bd=0,
            width=12,
            height=2,
            cursor="hand2"
        )

        self.start_button.pack(
            side="left",
            padx=8
        )

        reset_button = tk.Button(
            button_frame,
            text="↻  RESET",
            command=self.reset_timer,
            font=("Segoe UI", 11, "bold"),
            bg=self.BUTTON,
            fg=self.TEXT,
            activebackground="#333333",
            activeforeground=self.TEXT,
            relief="flat",
            bd=0,
            width=12,
            height=2,
            cursor="hand2"
        )

        reset_button.pack(
            side="left",
            padx=8
        )

        # -------------------------
        # Settings
        # -------------------------

        settings_button = tk.Button(
            self.root,
            text="⚙  Settings",
            command=self.open_settings,
            font=("Segoe UI", 10),
            bg=self.BG,
            fg=self.SECONDARY_TEXT,
            activebackground=self.BG,
            activeforeground=self.TEXT,
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        settings_button.pack(pady=5)

        # -------------------------
        # Footer
        # -------------------------

        self.status_label = tk.Label(
            self.root,
            text="Ready to focus.",
            font=("Segoe UI", 9),
            bg=self.BG,
            fg=self.SECONDARY_TEXT
        )

        self.status_label.pack(
            side="bottom",
            pady=15
        )

    # =========================================================
    # TIMER CONTROLS
    # =========================================================

    def start_pause(self):
        """Start or pause the timer."""

        if self.timer.running:

            self.timer.pause()

            self.start_button.config(
                text="▶  RESUME"
            )

            self.status_label.config(
                text="Timer paused."
            )

        else:

            self.timer.start()

            self.start_button.config(
                text="⏸  PAUSE"
            )

            self.status_label.config(
                text="Focus mode active."
            )

    def reset_timer(self):
        """Reset the Pomodoro cycle."""

        self.timer.reset()

        self.start_button.config(
            text="▶  START"
        )

        self.status_label.config(
            text="Ready to focus."
        )

    # =========================================================
    # DISPLAY
    # =========================================================

    def update_display(
        self,
        remaining_seconds,
        session_type,
        completed_sessions
    ):
        """Update the GUI based on timer state."""

        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60

        self.time_label.config(
            text=f"{minutes:02d}:{seconds:02d}"
        )

        names = {
            PomodoroTimer.WORK: "WORK SESSION",
            PomodoroTimer.SHORT_BREAK: "SHORT BREAK",
            PomodoroTimer.LONG_BREAK: "LONG BREAK"
        }

        self.session_label.config(
            text=names[session_type]
        )

        # Work = red
        if session_type == PomodoroTimer.WORK:

            self.session_label.config(
                fg=self.ACCENT
            )

        # Break = green
        else:

            self.session_label.config(
                fg="#4CAF50"
            )

        # Calculate completed sessions in current cycle
        if session_type == PomodoroTimer.LONG_BREAK:

            completed_in_cycle = SESSIONS_BEFORE_LONG_BREAK

        else:

            completed_in_cycle = (
                completed_sessions
                % SESSIONS_BEFORE_LONG_BREAK
            )

        # Session counter
        if session_type == PomodoroTimer.WORK:

            session_num = completed_in_cycle + 1

            self.session_counter.config(
                text=f"Session {session_num} / "
                     f"{SESSIONS_BEFORE_LONG_BREAK}"
            )

        elif session_type == PomodoroTimer.SHORT_BREAK:

            self.session_counter.config(
                text=f"Short Break "
                     f"({completed_in_cycle} / "
                     f"{SESSIONS_BEFORE_LONG_BREAK} complete)"
            )

        else:

            self.session_counter.config(
                text=f"Long Break "
                     f"({SESSIONS_BEFORE_LONG_BREAK} / "
                     f"{SESSIONS_BEFORE_LONG_BREAK} complete)"
            )

        # Progress dots
        for i, dot in enumerate(self.progress_dots):

            if i < completed_in_cycle:

                dot.config(
                    fg=self.ACCENT
                )

            else:

                dot.config(
                    fg="#444444"
                )

    # =========================================================
    # SESSION COMPLETE
    # =========================================================

    def session_complete(
        self,
        session_type,
        completed_sessions
    ):
        """Called when a timer reaches zero."""

        if session_type == PomodoroTimer.WORK:

            if (
                completed_sessions
                % SESSIONS_BEFORE_LONG_BREAK
                == 0
            ):

                show_notification(
                    self.root,
                    f"🎉 {SESSIONS_BEFORE_LONG_BREAK} "
                    f"Sessions Complete!",
                    "Excellent work! Time for your long break."
                )

            else:

                show_notification(
                    self.root,
                    "🍅 Work Session Complete!",
                    "Great work! Time for a short break."
                )

        elif session_type == PomodoroTimer.SHORT_BREAK:

            show_notification(
                self.root,
                "☕ Break Complete!",
                "Time to get back to work."
            )

        elif session_type == PomodoroTimer.LONG_BREAK:

            show_notification(
                self.root,
                "🌴 Long Break Complete!",
                "Ready for another Pomodoro cycle?"
            )

        self.start_button.config(
            text="▶  START"
        )

        self.status_label.config(
            text="Session complete!"
        )

    # =========================================================
    # SETTINGS
    # =========================================================

    def open_settings(self):
        """Open the settings window."""

        if (
            self.settings_window is not None
            and self.settings_window.winfo_exists()
        ):
            self.settings_window.focus()
            return

        self.settings_window = tk.Toplevel(
            self.root
        )

        self.settings_window.title(
            "Pomodoro Settings"
        )

        self.settings_window.geometry(
            "350x400"
        )

        self.settings_window.resizable(
            False,
            False
        )

        self.settings_window.configure(
            bg=self.CARD
        )

        tk.Label(
            self.settings_window,
            text="⚙  Settings",
            font=("Segoe UI", 20, "bold"),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(pady=25)

        # Variables
        work_var = tk.StringVar(
            value=str(self.timer.work_minutes)
        )

        short_var = tk.StringVar(
            value=str(self.timer.short_break_minutes)
        )

        long_var = tk.StringVar(
            value=str(self.timer.long_break_minutes)
        )

        self.create_setting_field(
            self.settings_window,
            "Work duration",
            work_var
        )

        self.create_setting_field(
            self.settings_window,
            "Short break",
            short_var
        )

        self.create_setting_field(
            self.settings_window,
            "Long break",
            long_var
        )

        save_button = tk.Button(
            self.settings_window,
            text="SAVE SETTINGS",
            command=lambda: self.save_settings(
                work_var,
                short_var,
                long_var
            ),
            font=("Segoe UI", 10, "bold"),
            bg=self.ACCENT,
            fg="white",
            activebackground=self.ACCENT,
            relief="flat",
            width=20,
            height=2,
            cursor="hand2"
        )

        save_button.pack(pady=25)

    def create_setting_field(
        self,
        parent,
        label,
        variable
    ):
        """Create one settings input field."""

        frame = tk.Frame(
            parent,
            bg=self.CARD
        )

        frame.pack(
            fill="x",
            padx=40,
            pady=8
        )

        tk.Label(
            frame,
            text=label,
            font=("Segoe UI", 10),
            bg=self.CARD,
            fg=self.TEXT
        ).pack(side="left")

        entry = tk.Entry(
            frame,
            textvariable=variable,
            font=("Segoe UI", 10),
            width=8,
            justify="center"
        )

        entry.pack(side="right")

    def save_settings(
        self,
        work_var,
        short_var,
        long_var
    ):
        """Validate and save new timer settings."""

        try:

            work = int(work_var.get())
            short_break = int(short_var.get())
            long_break = int(long_var.get())

            if (
                work <= 0
                or short_break <= 0
                or long_break <= 0
            ):
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Settings",
                "Please enter positive whole numbers."
            )

            return

        self.timer.update_settings(
            work,
            short_break,
            long_break
        )

        self.start_button.config(
            text="▶  START"
        )

        self.status_label.config(
            text="Settings updated."
        )

        self.settings_window.destroy()

    # =========================================================
    # CLOSE
    # =========================================================

    def on_close(self):
        """Clean up timer and close application."""

        if (
            hasattr(self, "timer")
            and self.timer
            and self.timer.after_id
        ):

            try:
                self.root.after_cancel(
                    self.timer.after_id
                )
            except Exception:
                pass

        self.root.destroy()


if __name__ == "__main__":

    root = tk.Tk()

    app = PomodoroApp(root)

    root.mainloop()