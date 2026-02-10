from tui.core.context import Context
from tui.core.events import (
    ActionEvent,
    BackspaceEvent,
    CursorMoveEvent,
    DeleteEvent,
    InsertCharEvent,
    LogAppendEvent,
    QuitEvent,
    SubmitEvent,
    TickEvent,
)


def register(ctx: Context):
    ctx.bus.subscribe(InsertCharEvent, lambda ev: _insert_char(ctx, ev))
    ctx.bus.subscribe(BackspaceEvent, lambda ev: _backspace(ctx, ev))
    ctx.bus.subscribe(DeleteEvent, lambda ev: _delete(ctx, ev))
    ctx.bus.subscribe(CursorMoveEvent, lambda ev: _cursor_move(ctx, ev))
    ctx.bus.subscribe(SubmitEvent, lambda ev: _submit(ctx, ev))
    ctx.bus.subscribe(ActionEvent, lambda ev: _action(ctx, ev))
    ctx.bus.subscribe(QuitEvent, lambda ev: _quit(ctx, ev))
    ctx.bus.subscribe(LogAppendEvent, lambda ev: _log_append(ctx, ev))
    ctx.bus.subscribe(TickEvent, lambda ev: _tick(ctx, ev))


def _insert_char(ctx: Context, event: InsertCharEvent):
    state = ctx.state
    lhs = state.prompt_text[:state.cursor_idx]
    rhs = state.prompt_text[state.cursor_idx:]
    state.prompt_text = lhs + event.char + rhs
    state.cursor_idx += 1
    ctx.render_queue.invalidate("prompt")


def _backspace(ctx: Context, event: BackspaceEvent):
    state = ctx.state
    if state.cursor_idx > 0:
        lhs = state.prompt_text[:state.cursor_idx - 1]
        rhs = state.prompt_text[state.cursor_idx:]
        state.prompt_text = lhs + rhs
        state.cursor_idx -= 1
        ctx.render_queue.invalidate("prompt")


def _delete(ctx: Context, event: DeleteEvent):
    state = ctx.state
    if state.cursor_idx < len(state.prompt_text):
        lhs = state.prompt_text[:state.cursor_idx]
        rhs = state.prompt_text[state.cursor_idx + 1:]
        state.prompt_text = lhs + rhs
        ctx.render_queue.invalidate("prompt")


def _cursor_move(ctx: Context, event: CursorMoveEvent):
    state = ctx.state
    if event.direction == "left" and state.cursor_idx > 0:
        state.cursor_idx -= 1
    elif event.direction == "right" and state.cursor_idx < len(state.prompt_text):
        state.cursor_idx += 1
    elif event.direction == "home":
        state.cursor_idx = 0
    elif event.direction == "end":
        state.cursor_idx = len(state.prompt_text)


def _submit(ctx: Context, event: SubmitEvent):
    state = ctx.state
    if event.text:
        ctx.post(LogAppendEvent(line=f"> {event.text}"))
    state.prompt_text = ""
    state.cursor_idx = 0
    ctx.render_queue.invalidate("prompt")


def _action(ctx: Context, event: ActionEvent):
    state = ctx.state
    action_name = state.actions.get(event.key, event.key)
    ctx.post(LogAppendEvent(line=f"[{event.key}] {action_name}"))


def _quit(ctx: Context, event: QuitEvent):
    ctx.state.running = False


def _log_append(ctx: Context, event: LogAppendEvent):
    ctx.state.append_log(event.line)
    ctx.render_queue.invalidate("main_panel")


def _tick(ctx: Context, event: TickEvent):
    ctx.state.tick = event.tick
