import threading
import time

from tui.core.context import Context
from tui.core.events import TickEvent


class Clock:
    def __init__(self, ctx: Context, interval: float = 1.0):
        self._ctx = ctx
        self._interval = interval
        self._tick = 0
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        while self._running:
            time.sleep(self._interval)
            if self._running:
                self._tick += 1
                self._ctx.post(TickEvent(tick=self._tick))
