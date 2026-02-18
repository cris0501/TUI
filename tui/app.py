import curses

from tui.core.event_bus import EventBus
from tui.core.context import Context
from tui.core.message_loop import MessageLoop
from tui.state.app_state import AppState
from tui.state.render_queue import RenderQueue
from tui.ui.layout import Layout
from tui.ui.renderer import Renderer
from tui.ui.widgets.title import TitleWidget
from tui.ui.widgets.main_panel import MainPanelWidget
from tui.ui.widgets.prompt import PromptWidget
from tui.ui.widgets.footer import FooterWidget
from tui.handlers import input_handlers, domain_handlers, ui_handlers
from tui.ui.colors import init_colors

def main(stdscr: curses.window):
    curses.curs_set(1)
    init_colors()
    stdscr.keypad(True)
    stdscr.clear()
    stdscr.noutrefresh()

    # Core dependencies
    state = AppState()
    render_queue = RenderQueue()
    layout = Layout()
    bus = EventBus()
    ctx = Context(state, render_queue, layout, bus)

    # Layout
    H, W = stdscr.getmaxyx()
    layout.recalculate(H, W)

    # Widgets
    widgets = [TitleWidget(), MainPanelWidget(), PromptWidget(), FooterWidget()]

    # Renderer
    renderer = Renderer(layout, render_queue)
    for w in widgets:
        renderer.register_widget(w)
    renderer.create_windows(stdscr)

    # Message loop (wires ctx.post)
    ml = MessageLoop(stdscr, ctx, renderer)

    # Register handlers
    input_handlers.register(ctx)
    domain_handlers.register(ctx)
    ui_handlers.register(ctx)

    # Seed welcome logs
    state.append_log("Welcome to TUI / For C. Ramirez")
    state.append_log("Type text and press Enter to add log entries")

    # Initial full draw
    render_queue.invalidate_all(layout.widget_ids())

    try:
        ml.run()
    finally:
        # clock.stop()
        if ctx.socket:
            ctx.socket.stop()
        pass


if __name__ == "__main__":
    curses.wrapper(main)
