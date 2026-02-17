# TUI

Terminal UI framework in Python/curses. Architecture: **Message Loop + Event Bus**.

```
python -m tui.app
```

Requires Python 3.10+, a real TTY (no notebooks), and the standard `curses` module.

## Structure

```
tui/
├── app.py                  # Bootstrap: wires all parts and starts the loop
├── core/
│   ├── events.py           # All event dataclasses (KeyEvent, InsertCharEvent, etc.)
│   ├── event_bus.py        # Passive handler lookup table
│   ├── context.py          # Dependency container + post() delegate
│   └── message_loop.py     # Main loop + InputThread (daemon)
├── state/
│   ├── app_state.py        # Mutable app state (prompt_text, log_lines, cursor, etc.)
│   └── render_queue.py     # Dirty set: tracks which widgets need redraw
├── ui/
│   ├── layout.py           # Rect namedtuple + Layout (computes widget positions)
│   ├── renderer.py         # Owns curses subwindows, calls widget.draw(), doupdate()
│   └── widgets/
│       ├── base.py         # Abstract Widget: widget_id + draw(win, rect, state)
│       ├── title.py        # App name + status
│       ├── main_panel.py   # Log viewer
│       ├── prompt.py       # Text input line
│       └── footer.py       # Action keys (F1-F5, F9)
├── handlers/
│   ├── input_handlers.py   # KeyEvent -> semantic events (InsertCharEvent, etc.)
│   ├── domain_handlers.py  # Semantic events -> state mutations + invalidate()
│   └── ui_handlers.py      # UI-specific handlers (resize placeholder)
└── services/
    ├── clock.py            # Daemon thread, posts TickEvent each second
    └── data_service.py     # Placeholder for IO
utils/
└── logger.py               # Singleton, writes to mi_debug.log
```

## Startup sequence

`app.py` runs inside `curses.wrapper()`:

1. Creates `AppState`, `RenderQueue`, `Layout`, `EventBus`, wraps them in `Context`
2. Calls `layout.recalculate(H, W)` with the terminal size
3. Creates the 4 widgets and registers them in `Renderer`
4. `Renderer.create_windows(stdscr)` creates one curses **subwindow** per widget
5. Creates `MessageLoop` — this wires `ctx.post()` to the loop's internal deque
6. Registers handlers (input, domain, ui) in the `EventBus`
7. Starts the `Clock` daemon thread
8. Invalidates all widgets and enters `ml.run()` (blocks until exit)

## Main loop cycle

```
┌─────────────────────────────────────────────────────────────┐
│  InputThread (daemon)           Clock (daemon)              │
│  ┌─────────────────────┐       ┌──────────────────┐        │
│  │ stdscr.get_wch()    │       │ sleep(1)          │        │
│  │ blocks until keypress│       │ post(TickEvent)   │        │
│  │ post(KeyEvent)      │       └──────────────────┘        │
│  │ post(ResizeEvent)   │                                    │
│  └─────────────────────┘                                    │
│           │                              │                  │
│           └──────────┐  ┌────────────────┘                  │
│                      ▼  ▼                                   │
│               ┌──────────────┐                              │
│               │  deque (GIL) │  thread-safe event queue     │
│               └──────┬───────┘                              │
│                      │                                      │
│  ════════════════════╪══════════════════════════════════     │
│  Main Thread         ▼                                      │
│  ┌───────────────────────────────────────────────────┐      │
│  │ while state.running:              (≈60 FPS)       │      │
│  │                                                   │      │
│  │   1. drain_queue (up to 100 events)               │      │
│  │      ├─ ResizeEvent? → renderer.on_resize() first │      │
│  │      └─ dispatch to bus handlers                  │      │
│  │                                                   │      │
│  │   2. renderer.flush(state)                        │      │
│  │      └─ redraw dirty widgets only                 │      │
│  │                                                   │      │
│  │   3. renderer.position_cursor()                   │      │
│  │                                                   │      │
│  │   4. sleep(0.016)                                 │      │
│  └───────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Event flow (key press to screen update)

```
User presses 'a'
  │
  ▼
InputThread: get_wch() returns 'a'
  │ post(KeyEvent(key='a'))
  ▼
Main thread drain_queue picks it up
  │ dispatch to input_handlers
  ▼
input_handlers: KeyEvent('a') → post(InsertCharEvent('a'))
  │ (re-enters queue, dispatched on next drain iteration)
  ▼
domain_handlers: InsertCharEvent('a')
  │ state.prompt_text = "...a..."
  │ state.cursor_idx += 1
  │ render_queue.invalidate("prompt")
  ▼
renderer.flush():
  │ drain dirty → {"prompt"}
  │ prompt_widget.draw(win, rect, state)
  │ curses.doupdate()
  ▼
renderer.position_cursor():
  │ stdscr.move(cursor_y, cursor_x)
  ▼
Terminal shows the updated prompt with 'a' and the blinking cursor
```

## Who owns what

This is the key thing to understand when making changes:

| What | Who owns it | Where |
|---|---|---|
| **curses subwindows** | `Renderer` | Creates them, resizes them, passes them to widgets |
| **drawing on screen** | `Widget.draw()` | Receives `(win, rect, state)` from Renderer. Paints on `win` |
| **layout positions** | `Layout` | Computes Rect(y, x, h, w) for each widget_id |
| **what to redraw** | `RenderQueue` | Handlers call `invalidate(widget_id)` after state changes |
| **when to redraw** | `MessageLoop` | Calls `renderer.flush()` once per tick after draining events |
| **app state** | `AppState` | Single mutable object. Handlers modify it, widgets read it |
| **key translation** | `input_handlers` | Raw KeyEvent -> semantic event (InsertCharEvent, etc.) |
| **state mutations** | `domain_handlers` | Semantic event -> modify state + invalidate widgets |

**Widgets don't know about curses subwindows.** The Renderer creates and owns the `win` objects.
The widget just receives `win` as an argument and draws on it. This means:

- To **change what a widget looks like**: edit its `draw()` method in `widgets/`
- To **change where a widget is placed**: edit `Layout.recalculate()` in `layout.py`
- To **add a new widget**: create a Widget subclass, register it in `Renderer` (app.py), add its rect calculation in `Layout`
- To **invalidate a widget**: call `render_queue.invalidate("widget_id")` from any handler

## How curses detects input

Curses input is **blocking** — `stdscr.get_wch()` halts the calling thread until the
user presses a key (or the terminal sends a resize signal). That's why input runs on a
separate daemon thread: the main thread must keep running its drain/render cycle.

After `renderer.flush()` calls `curses.doupdate()`, the terminal has the latest frame.
The cursor is then placed by `stdscr.move()`. At this point `get_wch()` on the input
thread is already blocking, waiting for the next key. Drawing and input don't interfere
because they run on different threads and curses in Python has the GIL serializing access.

## Common changes

**Add a new keybinding:**
`input_handlers.py` — add a case in the KeyEvent handler that posts a new semantic event.

**React to a new event:**
1. Define the event in `events.py`
2. Add a handler in `domain_handlers.py` that mutates state and invalidates the right widget(s)
3. Register the handler in `domain_handlers.register()`

**Change widget appearance:**
Edit the widget's `draw(win, rect, state)` method. The `win` is already sized and positioned
by the Renderer — just use `win.addstr()`, `win.hline()`, etc.

**Add a new widget:**
1. Create a class extending `Widget` in `widgets/`
2. Add its rect calculation in `Layout.recalculate()`
3. Instantiate and register in `app.py`

**Force a widget to redraw:**
Call `ctx.render_queue.invalidate("widget_id")` from any handler after changing state that
the widget reads.
