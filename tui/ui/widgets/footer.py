import curses

from tui.ui.widgets.base import Widget
from tui.ui.layout import Rect
from tui.state.app_state import AppState


class FooterWidget(Widget):
    @property
    def widget_id(self) -> str:
        return "footer"

    def draw(self, win: curses.window, rect: Rect, state: AppState) -> None:
        win.erase()
        opts = " | ".join(f"{k}: {v}" for k, v in state.actions.items())
        exit_label = "F9: Exit"
        section = rect.w - (len(exit_label) + 2)
        try:
            win.addnstr(0, 1, opts, max(0, section), curses.A_DIM)
            win.addnstr(0, max(1, section + 1), exit_label, len(exit_label), curses.A_BOLD)
        except curses.error:
            pass
        win.noutrefresh()
