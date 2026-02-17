import curses

from utils import Logger
from tui.ui.layout import Layout
from tui.ui.widgets.base import Widget
from tui.state.app_state import AppState
from tui.state.render_queue import RenderQueue

logger = Logger()


class Renderer:
    def __init__(self, layout: Layout, render_queue: RenderQueue):
        self._layout = layout
        self._render_queue = render_queue
        self._widgets: dict[str, Widget] = {}
        self._windows: dict[str, curses.window] = {}

    def register_widget(self, widget: Widget):
        self._widgets[widget.widget_id] = widget

    def create_windows(self, stdscr: curses.window):
        self._windows.clear()
        for wid in self._widgets:
            rect = self._layout.get_rect(wid)
            try:
                win = stdscr.subwin(rect.h, rect.w, rect.y, rect.x)
                self._windows[wid] = win
            except curses.error:
                logger.error(f"Cannot create subwin for {wid}: {rect}")

    def flush(self, state: AppState):
        dirty = self._render_queue.drain()
        if not dirty:
            return
        for wid in dirty:
            widget = self._widgets.get(wid)
            win = self._windows.get(wid)
            if widget and win:
                rect = self._layout.get_rect(wid)
                try:
                    win.resize(rect.h, rect.w)
                    win.mvwin(rect.y, rect.x)
                except curses.error:
                    pass
                widget.draw(win, rect, state)
        curses.doupdate()

    def on_resize(self, stdscr: curses.window, H: int, W: int, state: AppState):
        curses.resizeterm(H, W)
        stdscr.clear()
        stdscr.noutrefresh()
        self._layout.recalculate(H, W)
        self.create_windows(stdscr)
        self._render_queue.invalidate_all(self._widgets.keys())
        self.flush(state)

    def position_cursor(self, stdscr: curses.window, state: AppState):
        prompt_rect = self._layout.get_rect("prompt")
        cursor_y = prompt_rect.y + 1
        cursor_x = prompt_rect.x + 4 + state.cursor_idx
        try:
            stdscr.move(cursor_y, cursor_x)
        except curses.error:
            pass
