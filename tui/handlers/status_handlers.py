from tui.core.events import (
        LogAppendEvent,
        UpdateStatus,
        StartSocketEvent,
        UpdateSystemActionsEvent)
from tui.core.context import Context
from tui.state.app_state import PromptMode

def _handle_normal_mode(ctx: Context, input_text: str):
    state = ctx.state
    
    if input_text == "server" and not ctx.socket:
        ctx.post(LogAppendEvent(line="Configurando Socket Service..."))
        state.prompt_mode = PromptMode.AWAITING_IP
        ctx.post(UpdateStatus(status="Server..."))
        
    elif input_text in ("disconnect", "disconnect_server") and ctx.socket:
        ctx.socket.stop()
        ctx.socket = None
        ctx.post(UpdateStatus(status="IDLE"))
        ctx.post(LogAppendEvent(line="> Socket cerrado"))
        ctx.post(UpdateSystemActionsEvent(system_actions={}))

    else:
        ctx.post(LogAppendEvent(line=f"> {input_text}"))

def _handle_ip_mode(ctx: Context, input_text: str):
    state = ctx.state
    state.temp_ip = input_text if input_text else "127.0.0.1"
    state.prompt_mode = PromptMode.AWAITING_PORT
    ctx.post(LogAppendEvent(line=f"IP fijada: {state.temp_ip}"))

def _handle_port_mode(ctx: Context, input_text: str):
    state = ctx.state
    try:
        state.temp_port = int(input_text) if input_text else 5000
        ctx.post(LogAppendEvent(line=f"Iniciando server en {state.temp_ip}:{state.temp_port}..."))
        ctx.post(StartSocketEvent(host=state.temp_ip, port=state.temp_port))
        ctx.post(UpdateSystemActionsEvent(system_actions={"F8": "Disconnect"}))
    except ValueError:
        ctx.post(LogAppendEvent(line="[!] Puerto inválido. Cancelando..."))
        ctx.post(UpdateStatus(status="IDLE"))
    
    # Siempre volvemos a normal al terminar este flujo
    state.prompt_mode = PromptMode.NORMAL

