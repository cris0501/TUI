import curses
from views.base import BaseView
from core.layout import LayoutService
from utils import Logger

class TitleView(BaseView):
    view_id = "title"
    
    def __init__(self):
        self.logger = Logger()

    def draw(self, win: curses.window, layout: LayoutService, vm):
        rect = layout.get_rect(self.view_id)
        self._apply_rect(win, rect)
        title = vm.title()
        status = vm.status()
        section = int(rect.w / 2)
        try:
            win.addnstr(0, 1, title, max(len(title), section-1), curses.A_BOLD)
            win.addnstr(0, max(section, rect.w-len(status)-1), status, max(0, section-2), curses.A_BOLD)
            #win.hline(1, 0, curses.ACS_HLINE, rect.w)
        except Exception as e:
            self.logger.error(f"Error redraw {e}")
        win.noutrefresh()
