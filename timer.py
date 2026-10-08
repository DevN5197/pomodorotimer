
# timer.py

from settings import SESSIONS_BEFORE_LONG_BREAK


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
        on_tick,
        on_session_complete
    ):
        self.root = root

        # Timer durations
        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes

        # Functions called when something happens
        self.on_tick = on_tick
        self.on_session_complete = on_session_complete

        # Current session
        self.current_session = self.WORK

        # Number of completed work sessions
        self.completed_sessions = 0

        # Remaining time in seconds
        self.remaining_seconds = 0

        # Timer state
        self.running = False
        self.paused = False

        # ID returned by Tkinter's after()
        self.after_id = None

        # Start with a fresh work session
        self.reset()

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):
        """Reset the entire Pomodoro cycle."""

        # Cancel an existing countdown
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

        self.remaining_seconds = self.work_minutes * 60

        # Tell the GUI to update
        self.on_tick(
            self.remaining_seconds,
            self.current_session,
            self.completed_sessions
        )

    # =========================================================
    # START
    # =========================================================

    def start(self):
        """Start or resume the timer."""

        # Don't create multiple countdown loops
        if self.running:
            return

        self.running = True
        self.paused = False

        # Schedule the next tick after 1 second
        self.after_id = self.root.after(
            1000,
            self._countdown
        )

    # =========================================================
    # PAUSE
    # =========================================================

    def pause(self):
        """Pause the timer."""

        if not self.running:
            return

        self.running = False
        self.paused = True

        # Cancel the scheduled callback
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except Exception:
                pass

            self.after_id = None

    # =========================================================
    # PAUSE / RESUME
    # =========================================================

    def toggle_pause(self):
        """Toggle between pause and resume."""

        if self.running:
            self.pause()
        else:
            self.start()

    # =========================================================
    # COUNTDOWN
    # =========================================================

    def _countdown(self):
        """
        Run the countdown.

        Tkinter's after() is used instead of time.sleep()
        so that the GUI never freezes.
        """

        # Timer was paused/stopped
        if not self.running:
            return

        # There is still time remaining
        if self.remaining_seconds > 0:

            self.remaining_seconds -= 1

            # Update GUI
            self.on_tick(
                self.remaining_seconds,
                self.current_session,
                self.completed_sessions
            )

            # Call this function again after 1 second
            self.after_id = self.root.after(
                1000,
                self._countdown
            )

        else:

            # Timer reached zero
            self._session_finished()

    # =========================================================
    # SESSION FINISHED
    # =========================================================

    def _session_finished(self):
        """Handle completion of the current session."""

        self.running = False
        self.paused = False
        self.after_id = None

        # -----------------------------------------------------
        # WORK SESSION
        # -----------------------------------------------------

        if self.current_session == self.WORK:

            # Count completed work session
            self.completed_sessions += 1

            # Notify GUI
            self.on_session_complete(
                self.WORK,
                self.completed_sessions
            )

            # Every 4th work session → long break
            if (
                self.completed_sessions
                % SESSIONS_BEFORE_LONG_BREAK
                == 0
            ):

                self.current_session = self.LONG_BREAK

                self.remaining_seconds = (
                    self.long_break_minutes * 60
                )

            # Otherwise → short break
            else:

                self.current_session = self.SHORT_BREAK

                self.remaining_seconds = (
                    self.short_break_minutes * 60
                )

        # -----------------------------------------------------
        # SHORT BREAK
        # -----------------------------------------------------

        elif self.current_session == self.SHORT_BREAK:

            self.on_session_complete(
                self.SHORT_BREAK,
                self.completed_sessions
            )

            # Next → work
            self.current_session = self.WORK

            self.remaining_seconds = (
                self.work_minutes * 60
            )

        # -----------------------------------------------------
        # LONG BREAK
        # -----------------------------------------------------

        elif self.current_session == self.LONG_BREAK:

            self.on_session_complete(
                self.LONG_BREAK,
                self.completed_sessions
            )

            # Next → work
            self.current_session = self.WORK

            self.remaining_seconds = (
                self.work_minutes * 60
            )

        # Update GUI with the new session
        self.on_tick(
            self.remaining_seconds,
            self.current_session,
            self.completed_sessions
        )

    # =========================================================
    # SETTINGS
    # =========================================================

    def update_settings(
        self,
        work_minutes,
        short_break_minutes,
        long_break_minutes
    ):
        """Update durations and reset the timer."""

        self.work_minutes = work_minutes
        self.short_break_minutes = short_break_minutes
        self.long_break_minutes = long_break_minutes

        self.reset()

    # =========================================================
    # SESSION NAME
    # =========================================================

    def get_session_name(self):
        """Return a readable name for the current session."""

        names = {
            self.WORK: "WORK SESSION",
            self.SHORT_BREAK: "SHORT BREAK",
            self.LONG_BREAK: "LONG BREAK"
        }

        return names[self.current_session]

