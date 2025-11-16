import curses
from views.base import BaseView
from core.layout import LayoutService

class LogsView(BaseView):
    view_id = "logs"

    def draw(self, win: curses.window, layout: LayoutService, vm):
        rect = layout.get_rect(self.view_id)
        self._apply_rect(win, rect)
        lines = vm.visible_lines(rect.h)
        y = 0
        for line in lines[-rect.h:]:
            try:
                win.addnstr(y, 1, line, max(0, rect.w - 2))
            except e:
                print(f"Error redraw ${e}")
            y += 1
            if y >= rect.h:
                break
        #win.border()
        win.noutrefresh()
