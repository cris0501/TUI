from collections import defaultdict
from typing import Callable

from tui.core.events import Event


class EventBus:
    def __init__(self):
        self._handlers: dict[type[Event], list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: type[Event], handler: Callable):
        self._handlers[event_type].append(handler)

    def get_handlers(self, event_type: type[Event]) -> list[Callable]:
        return self._handlers.get(event_type, [])
