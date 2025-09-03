
import curses
from views.base import BaseView
from core.layout import LayoutService

class TitleView(BaseView):
    view_id = "title"

    def draw(self, win: curses.window, layout: LayoutService, vm):
        rect = layout.get_rect(self.view_id)
        self._apply_rect(win, rect)
        title = vm.title_text()
        try:
            win.addnstr(0, 1, title, max(0, rect.w - 2), curses.A_BOLD)
        except curses.error:
            pass
        win.noutrefresh()
