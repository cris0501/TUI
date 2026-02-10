from typing import Iterable


class RenderQueue:
    def __init__(self):
        self._dirty: set[str] = set()

    def invalidate(self, widget_id: str):
        self._dirty.add(widget_id)

    def invalidate_all(self, ids: Iterable[str]):
        self._dirty.update(ids)

    def drain(self) -> set[str]:
        snapshot = set(self._dirty)
        self._dirty.clear()
        return snapshot
