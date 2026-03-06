# Changelog

## [Unreleased] — curses → Textual migration

### Removed

| File | Reason |
|---|---|
| `tui/core/message_loop.py` | Replaced by Textual's asyncio event loop (`App.run()`) |
| `tui/core/event_bus.py` | Replaced by Textual's built-in message dispatch (`on_*` methods) |
| `tui/core/context.py` | Dependency container made obsolete — `TUIApp` is now the context |
| `tui/state/render_queue.py` | Dirty-tracking replaced by `widget.refresh()` and `RichLog.write()` |
| `tui/ui/layout.py` | `Rect` + `Layout` class replaced by Textual CSS (`height`, `1fr`) |
| `tui/ui/renderer.py` | Replaced by Textual's rendering pipeline; no manual `doupdate()` |
| `tui/ui/colors.py` | `curses.init_color` / `init_pair` replaced by CSS color names and Rich styles |
| `tui/ui/widgets/base.py` | Abstract `Widget(draw(win, rect, state))` replaced by `textual.widget.Widget` |
| `tui/handlers/input_handlers.py` | Raw key translation (`KeyEvent` → `InsertCharEvent`, etc.) made obsolete by Textual's `Input` widget and `on_key` |
| `tui/handlers/domain_handlers.py` | Logic merged into `TUIApp` message handlers (`on_log_append_event`, etc.) |
| `tui/handlers/ui_handlers.py` | Resize handling removed — Textual manages terminal resize automatically |
| `tui/services/clock.py` | `threading.Thread` clock replaced by `App.set_interval()` (available if needed) |

### Changed

#### `tui/core/events.py`
- All event classes were `@dataclass(frozen=True)` subclassing a custom `Event` base.
- Now each is a `textual.message.Message` subclass with an `__init__` calling `super().__init__()`.
- Removed events that Textual handles natively: `KeyEvent`, `ResizeEvent`, `InsertCharEvent`, `BackspaceEvent`, `DeleteEvent`, `CursorMoveEvent`, `SubmitEvent`, `QuitEvent`.
- Kept: `LogAppendEvent`, `UpdateStatus`, `ActionEvent`, `UpdateActionsEvent`, `UpdateSystemActionsEvent`, `StartSocketEvent`, `TickEvent`.

#### `tui/state/app_state.py`
- Removed the `running: bool` field — the event loop lifetime is now managed by Textual, not a boolean flag.
- All other fields (`app_name`, `status`, `log_lines`, `actions`, `system_actions`, `prompt_mode`, `temp_ip`, `temp_port`) are unchanged.

#### `tui/ui/widgets/title.py` — `TitleWidget` → `TitleBar`
- Before: `draw(win: curses.window, rect: Rect, state: AppState)` — painted directly onto a curses subwindow.
- After: `render() -> rich.text.Text` — returns a two-line Rich `Text` (title + status on line 1, `─` rule on line 2). Textual calls this automatically.
- Color: `curses.color_pair(PAIR_TITLE/PAIR_STATUS)` → Rich styles `"bold cyan"` / `"bold green"`.

#### `tui/ui/widgets/main_panel.py` — `MainPanelWidget` → `MainPanel`
- Before: custom `draw()` that iterated `state.log_lines` and called `win.addnstr()` per line.
- After: subclass of `textual.widgets.RichLog`. Log lines are appended with `panel.write(line)`. Scrolling is handled by Textual automatically.

#### `tui/ui/widgets/prompt.py` — `PromptWidget` → `PromptBar`
- Before: `draw()` painted a horizontal line and the full prompt string (prefix + text) using curses; cursor position was managed manually in `Renderer.position_cursor()`.
- After: `compose()` yields a `Rule` (separator) and a `Horizontal` container with a `Label` (prefix) + `Input` (text). All editing (backspace, delete, arrows, home, end) is handled by Textual's `Input` widget. Cursor is managed automatically.
- Prefix label is updated via `set_prefix(text)` when `PromptMode` changes.

#### `tui/ui/widgets/footer.py` — `FooterWidget` → `FooterBar`
- Before: `draw()` painted two strings (left actions, right system actions) with manual `sys_x` column calculation.
- After: `render() -> rich.text.Text` — same layout logic, returned as a Rich `Text.assemble()`. Colors: `"dim"` for actions, `"bold magenta"` for system actions.

#### `tui/handlers/status_handlers.py`
- Before: functions took `ctx: Context` as first argument; posted events via `ctx.post(...)`.
- After: functions take `app: TUIApp` as first argument; post events via `app.post_message(...)`.
- Renamed from private `_handle_*_mode` to public `handle_*_mode` since they are imported directly by `app.py`.

#### `tui/services/socket.py` — `SocketService`
- Before: managed its own `threading.Thread`; called `self._ctx.post(...)` to send events.
- After: no longer owns a thread. `run()` is a plain blocking method called via `app.run_worker(service.run, thread=True)`. Sends events via `self._app.post_message(...)`.
- Constructor changed from `SocketService(ctx)` to `SocketService(app, host, port)` — host and port are passed directly instead of read from `ctx.state`.

#### `tui/app.py`
- Before: `main(stdscr)` function run inside `curses.wrapper()`. Manually wired `AppState`, `RenderQueue`, `Layout`, `EventBus`, `Context`, `Renderer`, `MessageLoop`, and all handler registrations.
- After: `TUIApp(App)` class. `compose()` declares widgets, `on_mount()` seeds initial logs and focuses the input. Message handlers (`on_log_append_event`, `on_update_status`, etc.) replace the `EventBus` subscription pattern. Entry point: `TUIApp().run()`.

### Architecture summary

| Concept | Before (curses) | After (Textual) |
|---|---|---|
| Event loop | Manual `while state.running` + `time.sleep(0.016)` | `App.run()` (asyncio) |
| Event dispatch | `EventBus` — dict of `type → [handler]`, drained in ML | Textual `on_*` method dispatch |
| Input reading | Daemon thread calling `stdscr.get_wch()` | Built-in — Textual handles all keys |
| Resize | `SIGWINCH` → `ResizeEvent` → `renderer.on_resize()` | Automatic — Textual handles resize |
| Drawing | `widget.draw(win, rect, state)` → `curses.doupdate()` | `widget.render()` / `compose()` + `refresh()` |
| Layout | `Layout.recalculate(H, W)` → `Rect(y, x, h, w)` per widget | CSS (`height: 2`, `height: 1fr`, etc.) |
| Dirty tracking | `RenderQueue` — set of widget IDs | `widget.refresh()` on state change |
| Background threads | Manual `threading.Thread` with `daemon=True` | `app.run_worker(fn, thread=True)` |
| Colors | `curses.init_color` + `init_pair` | CSS color names + Rich styles |
