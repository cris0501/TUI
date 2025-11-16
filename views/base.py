import curses
from core.layout import LayoutService, Rect

class BaseView:
    view_id = "base"

    def draw(self, win: curses.window, layout: LayoutService, vm):
        raise NotImplementedError

    def _apply_rect(self, win: curses.window, rect: Rect):
        # Ajusta posición y tamaño, limpia ventana
        try:
            win.mvwin(rect.y, rect.x)
            win.resize(rect.h, rect.w)
        except curses.error:
            pass
        win.erase()
