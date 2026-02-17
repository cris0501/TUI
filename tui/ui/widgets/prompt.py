import curses

from tui.ui.widgets.base import Widget
from tui.ui.layout import Rect
from tui.state.app_state import (AppState, PromptMode)


class PromptWidget(Widget):
    @property
    def widget_id(self) -> str:
        return "prompt"

    def draw(self, win: curses.window, rect: Rect, state: AppState) -> None:
        win.erase()
        prefixes = {
            PromptMode.NORMAL: ">> ",
            PromptMode.AWAITING_IP: f"[ip:{state.temp_ip}] > ",
            PromptMode.AWAITING_PORT: f"[port:{state.temp_port}] > "
        }
        prefix = prefixes.get(state.prompt_mode, ">> ")

        text = prefix + state.prompt_text
        try:
            win.hline(0, 0, curses.ACS_HLINE, rect.w)
            win.attrset(0)
            win.addnstr(1, 1, text, max(0, rect.w - 2), curses.A_BOLD)
        except curses.error:
            pass
        win.noutrefresh()
