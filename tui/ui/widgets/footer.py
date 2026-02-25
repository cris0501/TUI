import curses

from tui.ui.widgets.base import Widget
from tui.ui.layout import Rect
from tui.state.app_state import AppState
from tui.ui import colors


class FooterWidget(Widget):
    @property
    def widget_id(self) -> str:
        return "footer"

    def draw(self, win: curses.window, rect: Rect, state: AppState) -> None:
        win.erase()

        # Right side: system actions + F9, anchored to the end
        sys_parts = [f"{k}: {v}" for k, v in state.system_actions.items()]
        sys_parts.append("F9: Exit")
        sys_str = " | ".join(sys_parts)
        sys_x = max(0, rect.w - len(sys_str) - 1)
        try:
            win.addnstr(0, sys_x, sys_str, len(sys_str),
                        curses.color_pair(colors.PAIR_ACCENT) | curses.A_BOLD)
        except curses.error:
            pass

        # Left side: dynamic actions, limited to not overlap the right side
        opts = " | ".join(f"{k}: {v}" for k, v in state.actions.items())
        try:
            win.addnstr(0, 1, opts, max(0, sys_x - 2),
                        curses.color_pair(colors.PAIR_FOOTER))
        except curses.error:
            pass

        win.noutrefresh()
