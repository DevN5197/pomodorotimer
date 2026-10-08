# 🍅 Pomodoro Timer
This is a fun project I made to brush up my skills in python and to learn the tkinter library as well as be proud of a project that aims to help me solve my real world problem of focusing when doing intensive tasks like studying, coding etc. using pomodoro timers that are explained below 

A simple, lightweight **Pomodoro Timer desktop application** built with Python and Tkinter.

Designed for focused study and work sessions without the distractions of a browser-based timer.

## ✨ Features

* ⏱️ **Pomodoro timer**

  * 25-minute work sessions by default
  * 5-minute short breaks
  * 15-minute long breaks
* 🔄 **Automatic session cycles**

  * 4 work sessions → long break
  * Work → Short Break → Work → ... → Long Break
* ▶️ **Start / Pause / Resume**
* ↻ **Reset timer**
* ⚙️ **Custom timer settings**

  * Change work duration
  * Change short break duration
  * Change long break duration
* 📊 **Session progress tracking**
* 🔴 **Visual progress indicators**
* 🔔 **Desktop notifications**
* 🖥️ **Native desktop GUI**
* 🌙 **Dark-themed interface**
* 🪶 Lightweight with no external UI framework

## 🖥️ Preview

The application uses a simple dark interface with:

* Current session indicator
* Large countdown timer
* Session counter
* Progress dots
* Start/Pause and Reset controls
* Settings window

## 🛠️ Built With

* **Python 3**
* **Tkinter** — Desktop GUI
* **Windows `winsound`** — Notification sounds
* Python standard library

No external Python packages are required.

## 📁 Project Structure

```text
pomodorotimer/
│
├── app.py             # Main GUI and application logic
├── main.py            # Application entry point
├── timer.py           # Pomodoro timer logic
├── settings.py        # Default timer configuration
├── notifications.py   # Desktop notification functionality
├── README.md
└── .gitignore
```

### Architecture

The application separates the GUI from the timer logic:

```text
main.py
   │
   ▼
app.py
   │
   ├── timer.py
   │      └── Timer state & session transitions
   │
   ├── settings.py
   │      └── Default durations
   │
   └── notifications.py
          └── Desktop notifications
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/DevN5197/pomodorotimer.git
```

### 2. Enter the project directory

```bash
cd pomodorotimer
```

### 3. Run the application

```bash
python main.py
```

The Pomodoro Timer window should open immediately.

## ⚙️ Default Settings

| Setting                    |    Default |
| -------------------------- | ---------: |
| Work Session               | 25 minutes |
| Short Break                |  5 minutes |
| Long Break                 | 15 minutes |
| Sessions Before Long Break |          4 |

These defaults are defined in `settings.py`.

## 🔁 How the Timer Works

The application follows the standard Pomodoro cycle:

```text
┌──────────────┐
│ Work Session │
│   25 min     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Short Break  │
│    5 min     │
└──────┬───────┘
       │
       ▼
   Next Work
       │
       ▼
   ... repeat ...
       │
       ▼
After 4 Work Sessions
       │
       ▼
┌──────────────┐
│  Long Break  │
│   15 min     │
└──────┬───────┘
       │
       ▼
   New Cycle
```

## ⚙️ Customizing Durations

You can change the timer durations directly from the application's **Settings** menu.

Alternatively, the default values can be changed in `settings.py`:

```python
DEFAULT_WORK_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15

SESSIONS_BEFORE_LONG_BREAK = 4
```

All values must be positive whole numbers.

## 🧠 Implementation

The timer uses Tkinter's `after()` mechanism rather than `time.sleep()`.

This allows the countdown to run without freezing the graphical interface.

The core timer logic is contained in `timer.py`, while `app.py` handles the user interface and user interactions.

## 🔔 Notifications

When a session finishes, the application displays a notification indicating what comes next.

Examples:

* 🍅 Work session completed → Short break
* 🎉 Four work sessions completed → Long break
* ☕ Break completed → Back to work
* 🌴 Long break completed → Start another cycle

On Windows, the application also uses the system notification sound through `winsound`.

## 💻 Requirements

* Windows
* Python **3.x**
* Tkinter

Tkinter is included with most standard Python installations on Windows.

Check your Python installation:

```bash
python --version
```

## 📦 Building an Executable

If you want to use the timer without opening Python, you can package it as a Windows `.exe` using PyInstaller.

Install PyInstaller:

```bash
pip install pyinstaller
```

Then build the application:

```bash
pyinstaller --onefile --windowed --name PomodoroTimer main.py
```

The executable will be created inside:

```text
dist/
└── PomodoroTimer.exe
```

You can then run the `.exe` directly on your Windows PC.

## 🎯 Why I Built This

I wanted a **simple desktop Pomodoro timer for personal use** without having to keep a browser tab open.

The goal was to keep the application:

* Simple
* Lightweight
* Distraction-free
* Easy to customize
* Easy to run locally

## 🔮 Possible Future Improvements

Some features that could be added in the future:

* [ ] Custom notification sounds
* [ ] System tray support
* [ ] Keyboard shortcuts
* [ ] Auto-start next session
* [ ] Session history
* [ ] Daily productivity statistics
* [ ] Task names
* [ ] Dark/light themes
* [ ] Minimize-to-tray
* [ ] Customizable number of sessions per cycle
* [ ] Windows installer

## 📄 License

This project is intended primarily for personal use.

If you want to use, modify, or distribute the project, feel free to do so according to the terms you choose to add to this repository.
