
from typing import List
from core.store import LogsStore
from core.redraw import RedrawManager

class LogsVM:
    def __init__(self, store: LogsStore, redraw: RedrawManager):
        self._store = store
        self._redraw = redraw
        self._lines_cache: List[str] = store.lines
        store.subscribe(self._on_event)

    def _on_event(self, evt: dict):
        if evt.get("type") == "appended":
            self._lines_cache = self._store.lines
            self._redraw.invalidate("logs")  # Solo invalidamos logs

    def visible_lines(self, h: int) -> List[str]:
        # Aquí podrías aplicar filtros, formateo, etc.
        return self._lines_cache
