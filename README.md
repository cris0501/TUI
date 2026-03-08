# TUI

Terminal user interface application built with [Textual](https://github.com/Textualize/textual).

## Requirements

- Python 3.11+
- `textual`

```bash
pip install textual
```

## Running

```bash
python -m tui.app
```

## Layout

```
┌─────────────────────────────────┐
│ TUI                        IDLE │  ← TitleBar (app name + status)
│─────────────────────────────────│
│                                 │
│  > log line 1                   │  ← MainPanel (scrollable log)
│  > log line 2                   │
│  ...                            │
│─────────────────────────────────│
│ >> _                            │  ← PromptBar (separator + text input)
│ F1: Update | F2: Add  F9: Exit  │  ← FooterBar (keybinding hints)
└─────────────────────────────────┘
```

## Key Bindings

| Key | Action |
|-----|--------|
| `Enter` | Submit input |
| `F1`–`F5` | Dynamic actions (configurable via socket) |
| `F8` | Disconnect socket server |
| `F9` | Exit |

## Socket Server

The app can act as a TCP server that receives JSON payloads to update its actions.

Start the server from the prompt by typing `server`, then providing the IP and port when prompted.

### Payload format example

```json
{
  "payload": "Body response",
  "_actions": [
    {"kind":"notify","type":"information","body":"Test notify"},
    {"kind":"notify","type":"error","body":"Test error", "title":"Fatal error"}
  ],
  "_links": [
    "F1:Load file",
    "F2:Return home",
    "F3: Cancel action"
  ]
}
```

### Example using netcat

```bash
echo '{"_actions": [{"kind":"notify","type":"information","body":"Test notify"},{"kind":"notify","type":"error","body":"Test notify", "title":"Chale"}], "_links": ["F1:Load file", "F2:Return home", "F3: Cancel action"], "payload": "None"}' | nc localhost 5000
```

Disconnect by typing `disconnect` or pressing `F8`.

## Architecture

```
tui/
├── app.py              # TUIApp — entry point, message handlers, event wiring
├── core/
│   └── events.py       # Textual Message subclasses (domain events)
├── state/
│   └── app_state.py    # AppState — plain data class, no framework coupling
├── ui/
│   └── widgets/
│       ├── title.py       # TitleBar — app name + status (render via Rich Text)
│       ├── main_panel.py  # MainPanel — scrollable log (RichLog subclass)
│       ├── prompt.py      # PromptBar — separator rule + text Input
│       └── footer.py      # FooterBar — keybinding hints (render via Rich Text)
├── handlers/
│   └── status_handlers.py  # Submit logic per PromptMode (normal / ip / port)
└── services/
    └── socket.py       # SocketService — TCP server (Textual thread worker)
utils/
└── logger.py           # Singleton logger, writes to mi_debug.log
```

## Event flow

```
User presses Enter
  │
  ▼
Input.Submitted (Textual built-in)
  │ → TUIApp.on_input_submitted
  ▼
status_handlers.handle_*_mode(app, text)
  │ → posts domain Messages (LogAppendEvent, UpdateStatus, StartSocketEvent, …)
  ▼
TUIApp.on_<message> handlers
  │ → update AppState
  │ → query_one(Widget).refresh() or .write()
  ▼
Textual redraws the affected widget
```

## Who owns what

| What | Where |
|---|---|
| **App state** | `AppState` — plain mutable object, no framework dependency |
| **Domain events** | `tui/core/events.py` — `Message` subclasses |
| **Input handling** | Textual `Input` widget (built-in) + `TUIApp.on_key` for F-keys |
| **Submit logic** | `status_handlers.py` — one function per `PromptMode` |
| **Widget rendering** | Each widget's `render()` (Rich Text) or `compose()` (sub-widgets) |
| **Background I/O** | `SocketService.run()` via `app.run_worker(..., thread=True)` |

## Common changes

**Add a new keybinding:**
Edit `TUIApp.on_key` in `app.py` — map the Textual key name to an `ActionEvent`.

**React to a new event:**
1. Define the `Message` subclass in `core/events.py`
2. Add the handler `on_<snake_case_name>` to `TUIApp` in `app.py`

**Change widget appearance:**
Edit the widget's `render()` method (returns a Rich `Text`) or its `compose()` layout.

**Add a new widget:**
1. Create it in `ui/widgets/`
2. Yield it in `TUIApp.compose()`
3. Add a CSS size rule in `TUIApp.CSS`

