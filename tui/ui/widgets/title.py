import curses

from tui.ui.widgets.base import Widget
from tui.ui.layout import Rect
from tui.state.app_state import AppState


class TitleWidget(Widget):
    @property
    def widget_id(self) -> str:
        return "title"

    def draw(self, win: curses.window, rect: Rect, state: AppState) -> None:
        win.erase()
        title = state.app_name
        status = state.status
        section = rect.w // 2
        try:
            win.addnstr(0, 1, title, max(0, section - 1), curses.A_BOLD)
            col = max(section, rect.w - len(status) - 1)
            win.addnstr(0, col, status, max(0, section - 2), curses.A_BOLD)
            win.hline(1, 0, curses.ACS_HLINE, rect.w)
        except curses.error:
            pass
        win.noutrefresh()
