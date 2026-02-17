from tui.core.context import Context
from tui.core.events import ResizeEvent, LogAppendEvent


def register(ctx: Context):
    ctx.bus.subscribe(ResizeEvent, lambda ev: _handle_resize(ctx, ev))


def _handle_resize(ctx: Context, event: ResizeEvent):
    ctx.post(LogAppendEvent(line=f"Resized to {event.width}x{event.height}"))
    ctx.render_queue.invalidate_all(ctx.layout.widget_ids())
