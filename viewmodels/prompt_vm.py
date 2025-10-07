
from core.store import PromptStore
from core.redraw import RedrawManager

class PromptVM:
    def __init__(self, store: PromptStore, redraw: RedrawManager):
        self._store = store
        self._redraw = redraw
        self._text = store.text
        store.subscribe(self._on_event)

    def _on_event(self, evt: dict):
        if evt.get("type") == "textChanged":
            self._text = self._store.text
            self._redraw.invalidate("prompt")  # invalidamos prompt

    def text(self) -> str:
        return self._text
  
    def add_text(self, msg: str):
      self._text += msg
      self._store.set_text(self._text)
