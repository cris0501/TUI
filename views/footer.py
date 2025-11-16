import curses
from views.base import BaseView
from core.layout import LayoutService
from utils import Logger

class FooterView(BaseView):
    view_id = "footer"

    def __init__(self):
        self.logger = Logger()

    def draw(self, win: curses.window, layout: LayoutService, vm):
        rect = layout.get_rect(self.view_id)
        self._apply_rect(win, rect)
        opts = vm.options()
        _exit = 'F9: Exit'
        section = rect.w - (len(_exit) + 2)
        try:
            #win.hline(0, 0, curses.ACS_HLINE, rect.w)
            win.addnstr(0, 1, opts, max(0, section), curses.A_DIM)
            win.addnstr(0, section+1, _exit, max(0, len(_exit)), curses.A_BOLD)
        except Exception as e:
            self.logger.error(f"Error footer_view: {e}")
        win.noutrefresh()
