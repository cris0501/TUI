from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tui.app import TUIApp

from tui.core.events import (
    LogAppendEvent,
    UpdateStatus,
    StartSocketEvent,
    UpdateSystemActionsEvent,
)
from tui.state.app_state import PromptMode


def handle_normal_mode(app: "TUIApp", input_text: str) -> None:
    state = app.state

    if input_text == "server" and not app.socket_service:
        app.post_message(LogAppendEvent(line="Configurando Socket Service..."))
        state.prompt_mode = PromptMode.AWAITING_IP
        app.post_message(UpdateStatus(status="Server..."))

    elif input_text == "disconnect" and app.socket_service:
        app.socket_service.stop()
        app.socket_service = None
        app.post_message(UpdateStatus(status="IDLE"))
        app.post_message(LogAppendEvent(line="> Socket cerrado"))
        app.post_message(UpdateSystemActionsEvent(system_actions={}))

    else:
        app.post_message(LogAppendEvent(line=f"> {input_text}"))


def handle_ip_mode(app: "TUIApp", input_text: str) -> None:
    state = app.state
    state.temp_ip = input_text if input_text else "127.0.0.1"
    state.prompt_mode = PromptMode.AWAITING_PORT
    app.post_message(LogAppendEvent(line=f"IP fijada: {state.temp_ip}"))


def handle_port_mode(app: "TUIApp", input_text: str) -> None:
    state = app.state
    try:
        state.temp_port = int(input_text) if input_text else 5000
        app.post_message(
            LogAppendEvent(line=f"Iniciando server en {state.temp_ip}:{state.temp_port}...")
        )
        app.post_message(StartSocketEvent(host=state.temp_ip, port=state.temp_port))
        app.post_message(UpdateSystemActionsEvent(system_actions={"F8": "Disconnect"}))
    except ValueError:
        app.post_message(LogAppendEvent(line="[!] Puerto inválido. Cancelando..."))
        app.post_message(UpdateStatus(status="IDLE"))

    state.prompt_mode = PromptMode.NORMAL

