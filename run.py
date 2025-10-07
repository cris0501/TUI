import curses
import time
from core.layout import LayoutService
from core.redraw import RedrawManager
from core.store import FooterStore, LogsStore, PromptStore
from views.title import TitleView
from views.logs import LogsView
from views.prompt import PromptView
from views.footer import FooterView
from viewmodels.title_vm import TitleVM
from viewmodels.logs_vm import LogsVM
from viewmodels.prompt_vm import PromptVM
from viewmodels.footer_vm import FooterVM

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    # Servicios
    layout = LayoutService()
    redraw = RedrawManager()
    redraw.set_layout(layout)

    # Stores
    footer_store = FooterStore()
    logs_store = LogsStore()
    prompt_store = PromptStore()

    # VMs
    title_vm = TitleVM(app_name="TUI")
    logs_vm = LogsVM(logs_store, redraw)
    prompt_vm = PromptVM(prompt_store, redraw)
    footer_vm = FooterVM(footer_store, redraw)

    # Vistas y ventanas
    H, W = stdscr.getmaxyx()
    layout.on_resize(H, W)

    # subwin( nlines, ncols, y, x )
    title_win = stdscr.subwin(1, W, 0, 0)
    logs_win  = stdscr.subwin(max(1, H-3), W, 1, 0)
    prompt_win= stdscr.subwin(1, W, max(0, H-3), 0)
    footer_win= stdscr.subwin(1, W, max(0, H-2), 0)

    title_view = TitleView()
    logs_view = LogsView()
    prompt_view = PromptView()
    footer_view = FooterView()

    redraw.bind("title", title_win, title_view, title_vm)
    redraw.bind("logs", logs_win, logs_view, logs_vm)
    redraw.bind("prompt", prompt_win, prompt_view, prompt_vm)
    redraw.bind("footer", footer_win, footer_view, footer_vm)

    redraw.invalidate_all()
    redraw.flush()

    running = True
    tick = 0
    while running:
        try:
            key = stdscr.get_wch()
        except curses.error:
            key = None

        if isinstance(key, str):
            prompt_vm.add_text(key)
        elif isinstance(key, int):
            if key == curses.KEY_BACKSPACE:
                prompt_vm.add_text(key)
            elif key == curses.KEY_RESIZE:
                H, W = stdscr.getmaxyx()
                curses.resizeterm(H, W)
                layout.on_resize(H, W)
                redraw.invalidate_all()

        # Flush si hay algo sucio
        redraw.flush()

        time.sleep(0.01)

if __name__ == "__main__":
    curses.wrapper(main)
