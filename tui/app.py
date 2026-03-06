from __future__ import annotations

from textual.app import App, ComposeResult
from textual import events
from textual.widgets import Input

from tui.state.app_state import AppState, PromptMode
from tui.core.events import (
    ActionEvent,
    LogAppendEvent,
    UpdateActionsEvent,
    UpdateSystemActionsEvent,
    UpdateStatus,
    StartSocketEvent,
)
from tui.ui.widgets.title import TitleBar
from tui.ui.widgets.main_panel import MainPanel
from tui.ui.widgets.prompt import PromptBar
from tui.ui.widgets.footer import FooterBar
from tui.services.socket import SocketService
from tui.handlers.status_handlers import (
    handle_normal_mode,
    handle_ip_mode,
    handle_port_mode,
)

_STATE_HANDLERS = {
    PromptMode.NORMAL: handle_normal_mode,
    PromptMode.AWAITING_IP: handle_ip_mode,
    PromptMode.AWAITING_PORT: handle_port_mode,
}

_FKEY_MAP = {
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f8": "F8",
}


class TUIApp(App):
    CSS = """
    Screen   { layout: vertical; }
    TitleBar { height: 2; }
    MainPanel { height: 1fr; }
    PromptBar { height: 2; }
    FooterBar { height: 1; }

    PromptBar Rule { margin: 0; }
    PromptBar Horizontal { height: 1; background: $surface; }
    PromptBar Label { height: 1; width: auto; padding: 0 0 0 1; color: $text; }
    PromptBar Input { border: none; height: 1; width: 1fr; padding: 0; }
    """

    def __init__(self) -> None:
        super().__init__()
        self.state = AppState()
        self.socket_service: SocketService | None = None

    def compose(self) -> ComposeResult:
        yield TitleBar()
        yield MainPanel(id="main_panel")
        yield PromptBar()
        yield FooterBar()

    def on_mount(self) -> None:
        panel = self.query_one(MainPanel)
        panel.write("Welcome to TUI / For C. Ramirez")
        panel.write("Type text and press Enter to add log entries")
        self.query_one(PromptBar).focus_input()

    def action_quit(self) -> None:
        if self.socket_service:
            self.socket_service.stop()
        self.exit()

    def on_key(self, event: events.Key) -> None:
        if event.key == "f9":
            self.action_quit()
        elif event.key in _FKEY_MAP:
            self._handle_action(_FKEY_MAP[event.key])

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        handler = _STATE_HANDLERS.get(self.state.prompt_mode)
        if handler:
            handler(self, text)
        event.input.clear()
        self._refresh_prompt_prefix()

    # --- Message handlers ---

    def on_log_append_event(self, event: LogAppendEvent) -> None:
        self.state.append_log(event.line)
        self.query_one(MainPanel).write(event.line)

    def on_update_status(self, event: UpdateStatus) -> None:
        self.state.status = event.status
        self.query_one(TitleBar).refresh()

    def on_action_event(self, event: ActionEvent) -> None:
        self._handle_action(event.key)

    def on_update_actions_event(self, event: UpdateActionsEvent) -> None:
        self.state.actions = event.actions
        self.post_message(LogAppendEvent(line=f"Current actions: {self.state.actions}"))
        self.query_one(FooterBar).refresh()

    def on_update_system_actions_event(self, event: UpdateSystemActionsEvent) -> None:
        self.state.system_actions = event.system_actions
        self.query_one(FooterBar).refresh()

    def on_start_socket_event(self, event: StartSocketEvent) -> None:
        self.socket_service = SocketService(self, event.host, event.port)
        self.run_worker(self.socket_service.run, thread=True)

    # --- Helpers ---

    def _handle_action(self, key: str) -> None:
        state = self.state
        if key == "F8" and self.socket_service:
            self.socket_service.stop()
            self.socket_service = None
            self.post_message(UpdateStatus(status="IDLE"))
            self.post_message(LogAppendEvent(line="> Socket cerrado"))
            self.post_message(UpdateSystemActionsEvent(system_actions={}))
            return
        action_name = state.actions.get(key, state.system_actions.get(key, key))
        self.post_message(LogAppendEvent(line=f"[{key}] {action_name}"))

    def _refresh_prompt_prefix(self) -> None:
        state = self.state
        prefixes = {
            PromptMode.NORMAL: ">> ",
            PromptMode.AWAITING_IP: f"[ip:{state.temp_ip}] > ",
            PromptMode.AWAITING_PORT: f"[port:{state.temp_port}] > ",
        }
        self.query_one(PromptBar).set_prefix(prefixes[state.prompt_mode])


if __name__ == "__main__":
    TUIApp().run()
