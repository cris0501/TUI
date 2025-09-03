
import curses
from views.base import BaseView
from core.layout import LayoutService

class PromptView(BaseView):
    view_id = "prompt"

    def draw(self, win: curses.window, layout: LayoutService, vm):
        rect = layout.get_rect(self.view_id)
        self._apply_rect(win, rect)
        text = vm.text()
        label = ">> " + text
        try:
            win.addnstr(0, 1, label, max(0, rect.w - 2), curses.A_REVERSE)
        except curses.error:
            pass
        win.noutrefresh()
