import curses
from views.base import BaseView
from core.layout import LayoutService
from utils import Logger

class PromptView(BaseView):
    view_id = "prompt"

    def __init__(self):
        self.logger = Logger()

    def draw(self, win: curses.window, layout: LayoutService, vm):
        rect = layout.get_rect(self.view_id)
        self._apply_rect(win, rect)
        text = ">> " + vm.text()
        try:
            win.hline(0, 0, curses.ACS_HLINE, rect.w)
            win.addnstr(1, 1, text, max(0, rect.w - 2), curses.A_BOLD)
        except curses.error as e:
            self.logger.error(f"Promp view: {e}")
        #win.border()
        win.noutrefresh()

    def set_cursor(self, stdscr, layout: LayoutService, vm):
        offset_x = 4
        rect = layout.get_rect(self.view_id)
        stdscr.move(rect.y+1, rect.x + offset_x + vm.cursor_idx)