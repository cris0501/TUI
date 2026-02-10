import curses

from tui.ui.widgets.base import Widget
from tui.ui.layout import Rect
from tui.state.app_state import AppState


class MainPanelWidget(Widget):
    @property
    def widget_id(self) -> str:
        return "main_panel"

    def draw(self, win: curses.window, rect: Rect, state: AppState) -> None:
        win.erase()
        visible = state.log_lines[-rect.h:]
        for y, line in enumerate(visible):
            try:
                win.addnstr(y, 1, line, max(0, rect.w - 2))
            except curses.error:
                pass
        win.noutrefresh()
