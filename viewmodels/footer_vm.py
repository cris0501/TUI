from core.store import FooterStore
from core.redraw import RedrawManager
from services.log_service import LogService
from utils import Logger

class FooterVM:
    def __init__(self, store: FooterStore, redraw: RedrawManager):
        self.logger = Logger()
        self._store = store
        self._redraw = redraw
        self._options = store.options
        self._service = LogService()
        store.subscribe(self._on_event)

    def _on_event(self, evt: dict):
        if evt.get("type") == "optionsChanged":
            self._options = self._store.options
            self._redraw.invalidate("footer")  # solo footer

    def action(self, key):
        if key == 'F9':
            self._service.register_event(f"Send {key} action, Exit TUI")
            exit(0)
        elif key in self._options:
            self._service.register_event(f"Send {key} action")
        else:
            self._service.register_event(f"Not {key} action")

    def options(self) -> str:
        temp = " | ".join(f"{k}: {self._options[k]}" for k in self._options)
        self.logger.info(f"Options: {temp}")
        return temp
