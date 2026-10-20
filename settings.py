# settings.py

import json
import os

# Default Pomodoro durations in minutes
DEFAULT_WORK_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15

# Number of work sessions before a long break
SESSIONS_BEFORE_LONG_BREAK = 4

# Auto-start next session
DEFAULT_AUTO_START = False

# Settings file path (same directory as this file)
SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "user_settings.json"
)


def load_settings():
    """Load settings from JSON file, falling back to defaults."""
    defaults = {
        "work_minutes": DEFAULT_WORK_MINUTES,
        "short_break_minutes": DEFAULT_SHORT_BREAK_MINUTES,
        "long_break_minutes": DEFAULT_LONG_BREAK_MINUTES,
        "sessions_before_long_break": SESSIONS_BEFORE_LONG_BREAK,
        "auto_start": DEFAULT_AUTO_START,
    }

    if not os.path.exists(SETTINGS_FILE):
        return defaults

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        # Merge saved over defaults so new keys always exist
        defaults.update(saved)
    except Exception:
        pass

    return defaults


def save_settings(settings: dict):
    """Persist settings dict to JSON file."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass
