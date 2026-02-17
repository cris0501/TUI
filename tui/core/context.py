from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from tui.core.event_bus import EventBus
    from tui.core.events import Event
    from tui.state.app_state import AppState
    from tui.state.render_queue import RenderQueue
    from tui.ui.layout import Layout


class Context:
    def __init__(
        self,
        state: AppState,
        render_queue: RenderQueue,
        layout: Layout,
        bus: EventBus,
    ):
        self.state = state
        self.render_queue = render_queue
        self.layout = layout
        self.bus = bus
        self._post: Callable[[Event], None] | None = None
        self.socket = None

    def set_post(self, fn: Callable[[Event], None]):
        self._post = fn

    def post(self, event: Event):
        if self._post is None:
            raise RuntimeError("post() called before MessageLoop wired set_post()")
        self._post(event)
