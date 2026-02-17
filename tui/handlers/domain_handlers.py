from tui.core.context import Context
from tui.state.app_state import PromptMode
from tui.core.events import (
    ActionEvent,
    BackspaceEvent,
    CursorMoveEvent,
    DeleteEvent,
    InsertCharEvent,
    LogAppendEvent,
    QuitEvent,
    SubmitEvent,
    UpdateStatus,
    StartSocketEvent,
)
from tui.services.socket import SocketService


def register(ctx: Context):
    ctx.bus.subscribe(InsertCharEvent, lambda ev: _insert_char(ctx, ev))
    ctx.bus.subscribe(BackspaceEvent, lambda ev: _backspace(ctx, ev))
    ctx.bus.subscribe(DeleteEvent, lambda ev: _delete(ctx, ev))
    ctx.bus.subscribe(CursorMoveEvent, lambda ev: _cursor_move(ctx, ev))
    ctx.bus.subscribe(SubmitEvent, lambda ev: _submit(ctx, ev))
    ctx.bus.subscribe(ActionEvent, lambda ev: _action(ctx, ev))
    ctx.bus.subscribe(QuitEvent, lambda ev: _quit(ctx, ev))
    ctx.bus.subscribe(LogAppendEvent, lambda ev: _log_append(ctx, ev))
    ctx.bus.subscribe(UpdateStatus, lambda ev: _update_status(ctx, ev))
    ctx.bus.subscribe(StartSocketEvent, lambda ev: _start_socket(ctx))


def _insert_char(ctx: Context, event: InsertCharEvent):
    state = ctx.state
    lhs = state.prompt_text[:state.cursor_idx]
    rhs = state.prompt_text[state.cursor_idx:]
    state.prompt_text = lhs + event.char + rhs
    state.cursor_idx += 1
    ctx.render_queue.invalidate("prompt")


def _backspace(ctx: Context, event: BackspaceEvent):
    state = ctx.state
    if state.cursor_idx > 0:
        lhs = state.prompt_text[:state.cursor_idx - 1]
        rhs = state.prompt_text[state.cursor_idx:]
        state.prompt_text = lhs + rhs
        state.cursor_idx -= 1
        ctx.render_queue.invalidate("prompt")


def _delete(ctx: Context, event: DeleteEvent):
    state = ctx.state
    if state.cursor_idx < len(state.prompt_text):
        lhs = state.prompt_text[:state.cursor_idx]
        rhs = state.prompt_text[state.cursor_idx + 1:]
        state.prompt_text = lhs + rhs
        ctx.render_queue.invalidate("prompt")


def _cursor_move(ctx: Context, event: CursorMoveEvent):
    state = ctx.state
    if event.direction == "left" and state.cursor_idx > 0:
        state.cursor_idx -= 1
    elif event.direction == "right" and state.cursor_idx < len(state.prompt_text):
        state.cursor_idx += 1
    elif event.direction == "home":
        state.cursor_idx = 0
    elif event.direction == "end":
        state.cursor_idx = len(state.prompt_text)


def _update_status(ctx: Context, event: UpdateStatus):
    ctx.state.status = event.status
    ctx.render_queue.invalidate("title")


def _submit(ctx: Context, event: SubmitEvent):
    state = ctx.state
    input_text = event.text.strip()

    if state.prompt_mode == PromptMode.NORMAL:
        if input_text == "disconect_server" and ctx.socket:
            ctx.socket.stop()
            ctx.socket = None
            ctx.post(UpdateStatus(status="IDLE"))
            ctx.post(LogAppendEvent(line="> Socket cerrado"))
        elif input_text == "server" and not ctx.socket:
            ctx.post(LogAppendEvent(line="Configurando Socket Service..."))
            state.prompt_mode = PromptMode.AWAITING_IP
            ctx.post(UpdateStatus(status="Server..."))
        else:
            # Comportamiento normal para otros comandos
            ctx.post(LogAppendEvent(line=f"> {input_text}"))

    elif state.prompt_mode == PromptMode.AWAITING_IP and not ctx.socket:
        # Guardamos la IP (podrías validar con regex aquí)
        state.temp_ip = input_text if input_text else "127.0.0.1"
        state.prompt_mode = PromptMode.AWAITING_PORT
        ctx.post(LogAppendEvent(line=f"IP fijada: {state.temp_ip}"))

    elif state.prompt_mode == PromptMode.AWAITING_PORT and not ctx.socket:
        try:
            state.temp_port = int(input_text) if input_text else 5000
            ctx.post(LogAppendEvent(line=f"Iniciando server en {state.temp_ip}:{state.temp_port}..."))
            ctx.post(StartSocketEvent(host=state.temp_ip, port=state.temp_port))
            state.prompt_mode = PromptMode.NORMAL
        except ValueError:
            ctx.post(LogAppendEvent(line="[!] Puerto inválido. Intenta de nuevo."))
            state.prompt_mode = PromptMode.NORMAL
            ctx.post(UpdateStatus(status="IDLE"))


    # Limpieza común
    state.prompt_text = ""
    state.cursor_idx = 0
    ctx.render_queue.invalidate("prompt")


def _action(ctx: Context, event: ActionEvent):
    state = ctx.state
    action_name = state.actions.get(event.key, event.key)
    ctx.post(LogAppendEvent(line=f"[{event.key}] {action_name}"))


def _quit(ctx: Context, event: QuitEvent):
    ctx.state.running = False


def _log_append(ctx: Context, event: LogAppendEvent):
    ctx.state.append_log(event.line)
    ctx.render_queue.invalidate("main_panel")


def _start_socket(ctx: Context):
    ctx.socket = SocketService(ctx)
    ctx.socket.start()
    ctx.post(UpdateStatus(status="IDLE"))
