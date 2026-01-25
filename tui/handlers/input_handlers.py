import curses
from typing import Dict, Any

from ..core.events import Event, EventType
from ..core.context import get_global_context

class InputHandlers:
    """
    Handlers para procesamiento de input de teclado y mouse.
    
    Convierte input crudo en eventos estandarizados para el sistema.
    """
    
    def __init__(self):
        self._context = get_global_context()
    
    def handle_key_input(self, key) -> None:
        """
        Procesa input de teclado y emite eventos apropiados.
        
        Args:
            key: Input de curses (str o int)
        """
        if isinstance(key, str):
            # Caracteres imprimibles y especiales
            self._handle_character_key(key)
        elif isinstance(key, int):
            # Códigos de teclas especiales
            self._handle_special_key(key)
    
    def _handle_character_key(self, char: str) -> None:
        """
        Maneja caracteres individuales.
        
        Args:
            char: Carácter ingresado
        """
        # Caracteres de control
        if char in ('\b', '\x7f'):
            self._emit_prompt_backspace()
        elif char in ('\n', '\r'):
            self._emit_prompt_submit()
        elif char == '\t':
            # Tab - podría usarse para autocompletar
            pass
        else:
            # Caracter normal
            self._emit_prompt_insert(char)
    
    def _handle_special_key(self, key_code: int) -> None:
        """
        Maneja códigos de teclas especiales.
        
        Args:
            key_code: Código de tecla de curses
        """
        # Teclas de edición
        if key_code == curses.KEY_BACKSPACE or key_code == 127:
            self._emit_prompt_backspace()
        elif key_code == curses.KEY_DC:
            self._emit_prompt_delete()
        elif key_code == curses.KEY_LEFT:
            self._emit_cursor_move_left()
        elif key_code == curses.KEY_RIGHT:
            self._emit_cursor_move_right()
        elif key_code == curses.KEY_HOME:
            self._emit_cursor_home()
        elif key_code == curses.KEY_END:
            self._emit_cursor_end()
        elif key_code == curses.KEY_UP:
            self._emit_cursor_up()
        elif key_code == curses.KEY_DOWN:
            self._emit_cursor_down()
        
        # Teclas de función
        elif key_code == curses.KEY_F1:
            self._emit_footer_action('F1')
        elif key_code == curses.KEY_F2:
            self._emit_footer_action('F2')
        elif key_code == curses.KEY_F3:
            self._emit_footer_action('F3')
        elif key_code == curses.KEY_F4:
            self._emit_footer_action('F4')
        elif key_code == curses.KEY_F5:
            self._emit_footer_action('F5')
        elif key_code == curses.KEY_F9:
            self._emit_footer_action('F9')
        
        # Resize
        elif key_code == curses.KEY_RESIZE:
            self._emit_resize()
        
        # Salir
        elif key_code in (curses.KEY_EXIT, 27):  # 27 = ESC
            self._emit_shutdown()
    
    def handle_mouse_input(self, mouse_data: Dict[str, Any]) -> None:
        """
        Procesa input de mouse y emite eventos apropiados.
        
        Args:
            mouse_data: Datos del evento de mouse
        """
        # Implementación futura para soporte de mouse
        pass
    
    # Métodos de emisión de eventos
    def _emit_prompt_insert(self, char: str) -> None:
        """Emite evento para insertar carácter en prompt."""
        from ..core.events import PromptTextChangedEvent
        app_state = self._context.get_app_state()
        current_text = app_state.prompt.text
        cursor_pos = app_state.prompt.cursor_position
        
        new_text = current_text[:cursor_pos] + char + current_text[cursor_pos:]
        
        event = PromptTextChangedEvent(
            event_type=EventType.PROMPT_TEXT_CHANGED,
            source="input_handler",
            payload={"text": new_text, "cursor_position": cursor_pos + 1},
            text=new_text
        )
        self._context.emit_event(event)
    
    def _emit_prompt_backspace(self) -> None:
        """Emite evento para backspace en prompt."""
        from ..core.events import PromptTextChangedEvent
        app_state = self._context.get_app_state()
        current_text = app_state.prompt.text
        cursor_pos = app_state.prompt.cursor_position
        
        if cursor_pos > 0:
            new_text = current_text[:cursor_pos-1] + current_text[cursor_pos:]
            
            event = PromptTextChangedEvent(
                event_type=EventType.PROMPT_TEXT_CHANGED,
                source="input_handler",
                payload={"text": new_text, "cursor_position": cursor_pos - 1},
                text=new_text
            )
            self._context.emit_event(event)
    
    def _emit_prompt_delete(self) -> None:
        """Emite evento para delete en prompt."""
        from ..core.events import PromptTextChangedEvent
        app_state = self._context.get_app_state()
        current_text = app_state.prompt.text
        cursor_pos = app_state.prompt.cursor_position
        
        if cursor_pos < len(current_text):
            new_text = current_text[:cursor_pos] + current_text[cursor_pos+1:]
            
            event = PromptTextChangedEvent(
                event_type=EventType.PROMPT_TEXT_CHANGED,
                source="input_handler",
                payload={"text": new_text, "cursor_position": cursor_pos},
                text=new_text
            )
            self._context.emit_event(event)
    
    def _emit_prompt_submit(self) -> None:
        """Emite evento para submit del prompt."""
        app_state = self._context.get_app_state()
        text = app_state.prompt.text
        
        if text.strip():
            # Añadir a logs
            from ..core.events import LogsAppendEvent
            log_event = LogsAppendEvent(
                event_type=EventType.LOGS_APPEND,
                source="prompt_submit",
                payload={"line": f"> {text}"},
                line=f"> {text}"
            )
            self._context.emit_event(log_event)
            
            # Limpiar prompt
            from ..core.events import PromptTextChangedEvent
            clear_event = PromptTextChangedEvent(
                event_type=EventType.PROMPT_TEXT_CHANGED,
                source="prompt_submit",
                payload={"text": "", "cursor_position": 0},
                text=""
            )
            self._context.emit_event(clear_event)
    
    def _emit_cursor_move_left(self) -> None:
        """Emite evento para mover cursor izquierda."""
        app_state = self._context.get_app_state()
        new_pos = max(0, app_state.prompt.cursor_position - 1)
        
        from ..core.events import PromptTextChangedEvent
        event = PromptTextChangedEvent(
            event_type=EventType.PROMPT_TEXT_CHANGED,
            source="input_handler",
            payload={"text": app_state.prompt.text, "cursor_position": new_pos},
            text=app_state.prompt.text
        )
        self._context.emit_event(event)
    
    def _emit_cursor_move_right(self) -> None:
        """Emite evento para mover cursor derecha."""
        app_state = self._context.get_app_state()
        new_pos = min(len(app_state.prompt.text), app_state.prompt.cursor_position + 1)
        
        from ..core.events import PromptTextChangedEvent
        event = PromptTextChangedEvent(
            event_type=EventType.PROMPT_TEXT_CHANGED,
            source="input_handler",
            payload={"text": app_state.prompt.text, "cursor_position": new_pos},
            text=app_state.prompt.text
        )
        self._context.emit_event(event)
    
    def _emit_cursor_home(self) -> None:
        """Emite evento para mover cursor al inicio."""
        from ..core.events import PromptTextChangedEvent
        event = PromptTextChangedEvent(
            event_type=EventType.PROMPT_TEXT_CHANGED,
            source="input_handler",
            payload={"text": self._context.get_app_state().prompt.text, "cursor_position": 0},
            text=self._context.get_app_state().prompt.text
        )
        self._context.emit_event(event)
    
    def _emit_cursor_end(self) -> None:
        """Emite evento para mover cursor al final."""
        app_state = self._context.get_app_state()
        from ..core.events import PromptTextChangedEvent
        event = PromptTextChangedEvent(
            event_type=EventType.PROMPT_TEXT_CHANGED,
            source="input_handler",
            payload={"text": app_state.prompt.text, "cursor_position": len(app_state.prompt.text)},
            text=app_state.prompt.text
        )
        self._context.emit_event(event)
    
    def _emit_cursor_up(self) -> None:
        """Emite evento para mover cursor arriba (historial)."""
        # Implementación futura para historial de comandos
        pass
    
    def _emit_cursor_down(self) -> None:
        """Emite evento para mover cursor abajo (historial)."""
        # Implementación futura para historial de comandos
        pass
    
    def _emit_footer_action(self, action: str) -> None:
        """Emite evento de acción de footer."""
        from ..core.events import FooterActionEvent
        event = FooterActionEvent(
            event_type=EventType.FOOTER_ACTION,
            source="input_handler",
            payload={"action": action},
            action=action
        )
        self._context.emit_event(event)
    
    def _emit_resize(self) -> None:
        """Emite evento de resize."""
        # Obtener nuevas dimensiones
        import curses
        height, width = curses.LINES, curses.COLS
        
        # Actualizar layout
        self._context.get_layout().update_terminal_size(width, height)
        
        # Emitir evento
        from ..core.events import ResizeEvent
        event = ResizeEvent(
            event_type=EventType.RESIZE,
            source="input_handler",
            payload={"width": width, "height": height},
            width=width,
            height=height
        )
        self._context.emit_event(event)
    
    def _emit_shutdown(self) -> None:
        """Emite evento de shutdown."""
        from ..core.events import ShutdownEvent
        event = ShutdownEvent(
            event_type=EventType.SHUTDOWN,
            source="input_handler",
            payload={"reason": "user_exit"}
        )
        self._context.emit_event(event)