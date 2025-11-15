
import curses
from views.base import BaseView
from core.layout import LayoutService

class PromptView(BaseView):
    view_id = "prompt"

    def draw(self, win: curses.window, layout: LayoutService, vm):
        rect = layout.get_rect(self.view_id)
        self._apply_rect(win, rect)
        text = vm.text
        label = ">> " + text
        try:
            win.hline(0, 0, curses.ACS_HLINE, rect.w)
            win.addnstr(1, 1, label, max(0, rect.w - 2), curses.A_BOLD)
        except curses.error:
            pass
        #win.border()
        win.noutrefresh()

    def set_cursor(self, stdscr, layout: LayoutService, vm):
        rect = layout.get_rect(self.view_id)
        stdscr.move(rect.y+1, vm.cursor_idx+4)