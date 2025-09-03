
from typing import Callable, List, Dict, Any

class Store:
    """Store base con suscripción por callbacks."""
    def __init__(self, name: str):
        self._name = name
        self._subs: List[Callable[[dict], None]] = []

    @property
    def name(self) -> str:
        return self._name

    def subscribe(self, cb: Callable[[dict], None]) -> Callable[[], None]:
        self._subs.append(cb)
        def unsubscribe():
            try:
                self._subs.remove(cb)
            except ValueError:
                pass
        return unsubscribe

    def _emit(self, type_: str, payload: Dict[str, Any]):
        evt = {"source": self._name, "type": type_, "payload": payload}
        # Copia defensiva ante modificaciones en el callback
        for cb in list(self._subs):
            cb(evt)


class FooterStore(Store):
    def __init__(self):
        super().__init__("footer")
        self._text = "Listo."

    @property
    def text(self) -> str:
        return self._text

    def set_text(self, text: str):
        self._text = text
        self._emit("textChanged", {"text": text})


class LogsStore(Store):
    def __init__(self, max_lines: int = 500):
        super().__init__("logs")
        self._lines: List[str] = []
        self._max = max_lines

    @property
    def lines(self) -> List[str]:
        return list(self._lines)

    def append(self, line: str):
        self._lines.append(line)
        if len(self._lines) > self._max:
            self._lines = self._lines[-self._max:]
        self._emit("appended", {"line": line, "count": len(self._lines)})


class PromptStore(Store):
    def __init__(self):
        super().__init__("prompt")
        self._text = ""

    @property
    def text(self) -> str:
        return self._text

    def set_text(self, text: str):
        self._text = text
        self._emit("textChanged", {"text": text})
