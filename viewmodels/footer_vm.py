
from core.store import FooterStore
from core.redraw import RedrawManager

class FooterVM:
    def __init__(self, store: FooterStore, redraw: RedrawManager):
        self._store = store
        self._redraw = redraw
        self._text = store.text
        store.subscribe(self._on_event)

    def _on_event(self, evt: dict):
        if evt.get("type") == "textChanged":
            self._text = self._store.text
            self._redraw.invalidate("footer")  # solo footer

    def text(self) -> str:
        return self._text
