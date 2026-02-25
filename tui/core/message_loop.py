import curses
import os
import signal
import threading
import time
from collections import deque

from tui.utils import Logger
from tui.core.context import Context
from tui.core.events import Event, KeyEvent, ResizeEvent
from tui.ui.renderer import Renderer

logger = Logger()


class _InputThread:
    def __init__(self, stdscr: curses.window, post):
        self._stdscr = stdscr
        self._post = post
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
            try:
                key = self._stdscr.get_wch()
            except curses.error:
                continue

            if isinstance(key, int) and key == curses.KEY_RESIZE:
                continue
            self._post(KeyEvent(key=key))


class MessageLoop:
    def __init__(self, stdscr: curses.window, ctx: Context, renderer: Renderer):
        self._stdscr = stdscr
        self._ctx = ctx
        self._renderer = renderer
        self._queue: deque[Event] = deque()
        self._input_thread = _InputThread(stdscr, self.post)

        ctx.set_post(self.post)

    def post(self, event: Event):
        self._queue.append(event)

    def _on_sigwinch(self, signum, frame):
        size = os.get_terminal_size()
        self.post(ResizeEvent(height=size.lines, width=size.columns))

    def run(self):
        signal.signal(signal.SIGWINCH, self._on_sigwinch)
        self._stdscr.nodelay(False)
        self._input_thread.start()

        state = self._ctx.state
        self._renderer.flush(state)
        self._renderer.position_cursor(self._stdscr, state)

        try:
            while state.running:
                self._drain_queue()
                self._renderer.flush(state)
                self._renderer.position_cursor(self._stdscr, state)
                time.sleep(0.016)
        except KeyboardInterrupt:
            state.running = False
        finally:
            self._input_thread.stop()

    def _drain_queue(self):
        bus = self._ctx.bus
        for _ in range(100):
            try:
                event = self._queue.popleft()
            except IndexError:
                break

            if isinstance(event, ResizeEvent):
                self._renderer.on_resize(
                    self._stdscr, event.height, event.width, self._ctx.state
                )

            handlers = bus.get_handlers(type(event))
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Handler error for {type(event).__name__}: {e}", exc_info=True)
