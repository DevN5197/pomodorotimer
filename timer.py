# timer.py


class PomodoroTimer:
    """
    Handles all Pomodoro timer logic.

    The GUI itself is in app.py.
    This class only manages the timer state.
    """

    # Session types
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"

    def __init__(
        self,
        root,
        work_minutes,
        short_break_minutes,
        long_break_minutes,
        sessions_before_long_break,
        on_tick,
        on_session_complete,
        auto_start=False,
    ):
        self.root = root

        # Timer durations
        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.sessions_before_long_break = sessions_before_long_break
        self.auto_start = auto_start

        # Callbacks
        self.on_tick = on_tick
        self.on_session_complete = on_session_complete

        # State
        self.current_session = self.WORK
        self.completed_sessions = 0
        self.remaining_seconds = 0
        self.total_seconds = 0          # duration of current session (for progress ring)
        self.running = False
        self.paused = False
        self.after_id = None

        # Start with a fresh work session (skip callback – app calls it after init)
        self.reset(notify=False)

    # =========================================================
    # RESET
    # =========================================================

    def reset(self, notify=True):
        """Reset the entire Pomodoro cycle."""

        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass

        self.after_id = None
        self.current_session = self.WORK
        self.completed_sessions = 0
        self.running = False
        self.paused = False

        self.total_seconds = self.work_minutes * 60
        self.remaining_seconds = self.total_seconds

        if notify:
            self.on_tick(
                self.remaining_seconds,
                self.total_seconds,
                self.current_session,
                self.completed_sessions,
            )

    # =========================================================
    # START / PAUSE
    # =========================================================

    def start(self):
        """Start or resume the timer."""
        if self.running:
            return

        self.running = True
        self.paused = False

        self.after_id = self.root.after(1000, self._countdown)

    def pause(self):
        """Pause the timer."""
        if not self.running:
            return

        self.running = False
        self.paused = True

        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def toggle_pause(self):
        """Toggle between pause and resume."""
        if self.running:
            self.pause()
        else:
            self.start()

    # =========================================================
    # SKIP
    # =========================================================

    def skip(self):
        """Skip the current session immediately."""
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

        self.running = False
        self.remaining_seconds = 0
        self._session_finished()

    # =========================================================
    # COUNTDOWN
    # =========================================================

    def _countdown(self):
        """
        Run the countdown.

        Tkinter's after() is used instead of time.sleep()
        so that the GUI never freezes.
        """
        if not self.running:
            return

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1

            self.on_tick(
                self.remaining_seconds,
                self.total_seconds,
                self.current_session,
                self.completed_sessions,
            )

            self.after_id = self.root.after(1000, self._countdown)

        else:
            self._session_finished()

    # =========================================================
    # SESSION FINISHED
    # =========================================================

    def _session_finished(self):
        """Handle completion of the current session."""

        self.running = False
        self.paused = False
        self.after_id = None

        # --------------------------------------------------
        # WORK SESSION
        # --------------------------------------------------

        if self.current_session == self.WORK:

            self.completed_sessions += 1

            self.on_session_complete(self.WORK, self.completed_sessions)

            if (
                self.completed_sessions
                % self.sessions_before_long_break
                == 0
            ):
                self.current_session = self.LONG_BREAK
                self.total_seconds = self.long_break_minutes * 60
            else:
                self.current_session = self.SHORT_BREAK
                self.total_seconds = self.short_break_minutes * 60

        # --------------------------------------------------
        # SHORT BREAK
        # --------------------------------------------------

        elif self.current_session == self.SHORT_BREAK:

            self.on_session_complete(self.SHORT_BREAK, self.completed_sessions)

            self.current_session = self.WORK
            self.total_seconds = self.work_minutes * 60

        # --------------------------------------------------
        # LONG BREAK
        # --------------------------------------------------

        elif self.current_session == self.LONG_BREAK:

            self.on_session_complete(self.LONG_BREAK, self.completed_sessions)

            self.current_session = self.WORK
            self.total_seconds = self.work_minutes * 60

        self.remaining_seconds = self.total_seconds

        self.on_tick(
            self.remaining_seconds,
            self.total_seconds,
            self.current_session,
            self.completed_sessions,
        )

        # Auto-start next session if enabled
        if self.auto_start:
            self.start()

    # =========================================================
    # SETTINGS
    # =========================================================

    def update_settings(
        self,
        work_minutes,
        short_break_minutes,
        long_break_minutes,
        sessions_before_long_break,
        auto_start,
    ):
        """Update durations and reset the timer."""
        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes
        self.sessions_before_long_break = sessions_before_long_break
        self.auto_start = auto_start

        self.reset()

    # =========================================================
    # HELPERS
    # =========================================================

    def get_session_name(self):
        """Return a readable name for the current session."""
        names = {
            self.WORK: "WORK SESSION",
            self.SHORT_BREAK: "SHORT BREAK",
            self.LONG_BREAK: "LONG BREAK",
        }
        return names[self.current_session]
