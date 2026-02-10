from tui.core.context import Context
from tui.core.events import ResizeEvent


def register(ctx: Context):
    ctx.bus.subscribe(ResizeEvent, lambda ev: _handle_resize(ctx, ev))


def _handle_resize(ctx: Context, event: ResizeEvent):
    pass
