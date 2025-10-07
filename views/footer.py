
import curses
from views.base import BaseView
from core.layout import LayoutService

class FooterView(BaseView):
    view_id = "footer"

    def draw(self, win: curses.window, layout: LayoutService, vm):
        rect = layout.get_rect(self.view_id)
        self._apply_rect(win, rect)
        msg = vm.text()
        try:
            win.hline(0, 0, curses.ACS_HLINE, rect.w)
            win.addnstr(1, 1, msg, max(0, rect.w - 2), curses.A_DIM)
        except curses.error:
            pass
        win.noutrefresh()
