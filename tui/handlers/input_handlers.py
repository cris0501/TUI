import curses

from tui.utils import Logger
from tui.core.context import Context
from tui.core.events import (
    ActionEvent,
    BackspaceEvent,
    CursorMoveEvent,
    DeleteEvent,
    InsertCharEvent,
    KeyEvent,
    QuitEvent,
    SubmitEvent,
    UpdateActionsEvent,
    UpdateSystemActionsEvent,
    LogAppendEvent
)


def register(ctx: Context):
    ctx.bus.subscribe(KeyEvent, lambda ev: _handle_key(ctx, ev))
    ctx.bus.subscribe(UpdateActionsEvent, lambda ev: _handle_actions(ctx, ev))
    ctx.bus.subscribe(UpdateSystemActionsEvent, lambda ev: _handle_system_actions(ctx, ev))


def _handle_key(ctx: Context, event: KeyEvent):
    key = event.key

    if isinstance(key, str):
        if key in ("\b", "\x7f"):
            ctx.post(BackspaceEvent())
        elif key in ("\n", "\r"):
            ctx.post(SubmitEvent(text=ctx.state.prompt_text))
        elif key == "\x03":  # Ctrl+C
            ctx.post(QuitEvent())
        else:
            ctx.post(InsertCharEvent(char=key))

    elif isinstance(key, int):
        if key == curses.KEY_BACKSPACE or key == 127:
            ctx.post(BackspaceEvent())
        elif key == curses.KEY_DC:
            ctx.post(DeleteEvent())
        elif key == curses.KEY_LEFT:
            ctx.post(CursorMoveEvent(direction="left"))
        elif key == curses.KEY_RIGHT:
            ctx.post(CursorMoveEvent(direction="right"))
        elif key == curses.KEY_HOME:
            ctx.post(CursorMoveEvent(direction="home"))
        elif key == curses.KEY_END:
            ctx.post(CursorMoveEvent(direction="end"))
        elif key == curses.KEY_F1:
            ctx.post(ActionEvent(key="F1"))
        elif key == curses.KEY_F2:
            ctx.post(ActionEvent(key="F2"))
        elif key == curses.KEY_F3:
            ctx.post(ActionEvent(key="F3"))
        elif key == curses.KEY_F4:
            ctx.post(ActionEvent(key="F4"))
        elif key == curses.KEY_F5:
            ctx.post(ActionEvent(key="F5"))
        elif key == curses.KEY_F8:
            ctx.post(ActionEvent(key="F8"))
        elif key == curses.KEY_F9:
            ctx.post(QuitEvent())

def _handle_actions(ctx: Context, event: UpdateActionsEvent):
    ctx.state.actions = event.actions
    ctx.post(LogAppendEvent(line=f"Current actions: {ctx.state.actions}"))
    ctx.render_queue.invalidate("footer")

def _handle_system_actions(ctx: Context, event: UpdateSystemActionsEvent):
    ctx.state.system_actions = event.system_actions
    ctx.render_queue.invalidate("footer")