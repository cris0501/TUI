from typing import Dict, Any

from ..core.events import Event, EventType
from ..core.context import get_global_context

class DomainHandlers:
    """
    Handlers para lógica de negocio y cambios de estado complejos.
    
    Maneja la lógica de negocio que no es puramente UI,
    como persistencia, validación, y operaciones complejas.
    """
    
    def __init__(self):
        self._context = get_global_context()
    
    def handle_prompt_submit_domain(self, event: Event) -> None:
        """
        Maneja la lógica de dominio para submit de prompt.
        
        Args:
            event: Evento de submit
        """
        app_state = self._context.get_app_state()
        text = app_state.prompt.text
        
        if not text.strip():
            return
        
        # Procesar comando si es especial
        if text.startswith('/'):
            self._process_command(text[1:].strip())
        else:
            # Procesar como comando normal
            self._process_normal_command(text)
    
    def handle_footer_action_domain(self, event: Event) -> None:
        """
        Maneja la lógica de dominio para acciones de footer.
        
        Args:
            event: Evento de acción de footer
        """
        action = event.payload.get('action', '')
        
        # Manejar acciones específicas
        if action == 'F1':
            self._handle_update_action()
        elif action == 'F2':
            self._handle_add_action()
        elif action == 'F3':
            self._handle_test_action()
        elif action == 'F4':
            self._handle_config_action()
        elif action == 'F5':
            self._handle_help_action()
    
    def handle_logs_append_domain(self, event: Event) -> None:
        """
        Maneja la lógica de dominio para append de logs.
        
        Args:
            event: Evento de append de logs
        """
        # Aquí se podrían agregar:
        # - Filtrado de logs
        # - Persistencia a archivo
        # - Formateo especial
        # - Integración con sistemas externos
        
        line = event.payload.get('line', '')
        
        # Agregar timestamp si está habilitado
        if self._context.get_config('add_timestamps', False) and line:
            import datetime
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            line = f"[{timestamp}] {line}"
            
            # Actualizar el payload con la línea con timestamp
            # y emitir de nuevo para que se muestre
            from ..core.events import LogsAppendEvent
            updated_event = LogsAppendEvent(
                event_type=EventType.LOGS_APPEND,
                source="domain_handler",
                payload={"line": line},
                line=line
            )
            self._context.emit_event(updated_event)
    
    def _process_command(self, command: str) -> None:
        """
        Procesa comandos especiales que empiezan con '/'.
        
        Args:
            command: Comando sin el '/'
        """
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Comandos disponibles
        if cmd == 'clear':
            self._clear_logs()
        elif cmd == 'debug':
            self._toggle_debug()
        elif cmd == 'help':
            self._show_help()
        elif cmd == 'exit' or cmd == 'quit':
            self._exit_app()
        elif cmd == 'config':
            self._handle_config_command(args)
        else:
            self._unknown_command(command)
    
    def _process_normal_command(self, text: str) -> None:
        """
        Procesa comandos normales (no empiezan con '/').
        
        Args:
            text: Texto del comando
        """
        # Aquí se podría integrar con:
        # - Sistema de plugins
        # - Base de datos
        # - API externas
        # - Procesamiento de datos
        
        # Por ahora, solo loguear que se procesó
        from ..core.events import LogsAppendEvent
        log_event = LogsAppendEvent(
            event_type=EventType.LOGS_APPEND,
            source="domain_handler",
            payload={"line": f"Processed: {text}"},
            line=f"Processed: {text}"
        )
        self._context.emit_event(log_event)
    
    def _clear_logs(self) -> None:
        """Limpia los logs."""
        from ..core.events import LogsAppendEvent
        # Enviar evento especial para limpiar logs
        clear_event = LogsAppendEvent(
            event_type=EventType.LOGS_APPEND,
            source="domain_handler",
            payload={"line": "", "clear": True},
            line=""
        )
        self._context.emit_event(clear_event)
    
    def _toggle_debug(self) -> None:
        """Activa/desactiva modo debug."""
        app_state = self._context.get_app_state()
        app_state.toggle_debug()
        
        status = "enabled" if app_state.debug_mode else "disabled"
        from ..core.events import LogsAppendEvent
        log_event = LogsAppendEvent(
            event_type=EventType.LOGS_APPEND,
            source="domain_handler",
            payload={"line": f"Debug mode {status}"},
            line=f"Debug mode {status}"
        )
        self._context.emit_event(log_event)
    
    def _show_help(self) -> None:
        """Muestra ayuda."""
        help_text = [
            "Available commands:",
            "  /clear      - Clear logs",
            "  /debug      - Toggle debug mode", 
            "  /help       - Show this help",
            "  /exit       - Exit application",
            "  /config     - Configuration commands",
            "",
            "Function keys:",
            "  F1 - Update  F2 - Add",
            "  F3 - Test    F4 - Config",
            "  F5 - Help    F9 - Exit"
        ]
        
        for line in help_text:
            from ..core.events import LogsAppendEvent
            log_event = LogsAppendEvent(
                event_type=EventType.LOGS_APPEND,
                source="domain_handler",
                payload={"line": line},
                line=line
            )
            self._context.emit_event(log_event)
    
    def _exit_app(self) -> None:
        """Sale de la aplicación."""
        from ..core.events import ShutdownEvent
        event = ShutdownEvent(
            event_type=EventType.SHUTDOWN,
            source="domain_handler",
            payload={"reason": "command_exit"}
        )
        self._context.emit_event(event)
    
    def _handle_config_command(self, args: list) -> None:
        """
        Maneja comandos de configuración.
        
        Args:
            args: Argumentos del comando config
        """
        if not args:
            self._show_config()
        elif len(args) == 2:
            key, value = args
            self._set_config(key, value)
        else:
            from ..core.events import LogsAppendEvent
            log_event = LogsAppendEvent(
                event_type=EventType.LOGS_APPEND,
                source="domain_handler",
                payload={"line": "Usage: /config [key value]"},
                line="Usage: /config [key value]"
            )
            self._context.emit_event(log_event)
    
    def _show_config(self) -> None:
        """Muestra configuración actual."""
        app_state = self._context.get_app_state()
        from ..core.events import LogsAppendEvent
        
        log_event = LogsAppendEvent(
            event_type=EventType.LOGS_APPEND,
            source="domain_handler",
            payload={"line": "Current configuration:"},
            line="Current configuration:"
        )
        self._context.emit_event(log_event)
        
        for key, value in app_state.config.items():
            log_event = LogsAppendEvent(
                event_type=EventType.LOGS_APPEND,
                source="domain_handler",
                payload={"line": f"  {key}: {value}"},
                line=f"  {key}: {value}"
            )
            self._context.emit_event(log_event)
    
    def _set_config(self, key: str, value: str) -> None:
        """
        Establece un valor de configuración.
        
        Args:
            key: Clave de configuración
            value: Valor a establecer
        """
        app_state = self._context.get_app_state()
        converted_value = value
        
        # Intentar convertir a tipo apropiado
        if value.lower() in ('true', 'false'):
            converted_value = value.lower() == 'true'
        elif value.isdigit():
            converted_value = int(value)
        elif '.' in value and value.replace('.', '').isdigit():
            converted_value = float(value)
        
        app_state.config[key] = converted_value
        
        from ..core.events import LogsAppendEvent
        log_event = LogsAppendEvent(
            event_type=EventType.LOGS_APPEND,
            source="domain_handler",
            payload={"line": f"Set {key} = {converted_value}"},
            line=f"Set {key} = {converted_value}"
        )
        self._context.emit_event(log_event)
    
    def _unknown_command(self, command: str) -> None:
        """
        Maneja comandos desconocidos.
        
        Args:
            command: Comando desconocido
        """
        from ..core.events import LogsAppendEvent
        log_event = LogsAppendEvent(
            event_type=EventType.LOGS_APPEND,
            source="domain_handler",
            payload={"line": f"Unknown command: /{command}"},
            line=f"Unknown command: /{command}"
        )
        self._context.emit_event(log_event)
    
    def _handle_update_action(self) -> None:
        """Maneja acción de update (F1)."""
        from ..core.events import LogsAppendEvent
        log_event = LogsAppendEvent(
            event_type=EventType.LOGS_APPEND,
            source="domain_handler",
            payload={"line": "Update triggered"},
            line="Update triggered"
        )
        self._context.emit_event(log_event)
    
    def _handle_add_action(self) -> None:
        """Maneja acción de add (F2)."""
        from ..core.events import LogsAppendEvent
        log_event = LogsAppendEvent(
            event_type=EventType.LOGS_APPEND,
            source="domain_handler",
            payload={"line": "Add action triggered"},
            line="Add action triggered"
        )
        self._context.emit_event(log_event)
    
    def _handle_test_action(self) -> None:
        """Maneja acción de test (F3)."""
        from ..core.events import LogsAppendEvent
        log_event = LogsAppendEvent(
            event_type=EventType.LOGS_APPEND,
            source="domain_handler",
            payload={"line": "Test action triggered"},
            line="Test action triggered"
        )
        self._context.emit_event(log_event)
    
    def _handle_config_action(self) -> None:
        """Maneja acción de config (F4)."""
        self._show_config()
    
    def _handle_help_action(self) -> None:
        """Maneja acción de help (F5)."""
        self._show_help()

def register_domain_handlers(event_bus) -> None:
    """
    Registra todos los domain handlers en el Event Bus.
    
    Args:
        event_bus: EventBus donde registrar los handlers
    """
    handlers = DomainHandlers()
    
    # Registrar handlers para eventos de dominio
    event_bus.register(EventType.FOOTER_ACTION, handlers.handle_footer_action_domain)
    event_bus.register(EventType.LOGS_APPEND, handlers.handle_logs_append_domain)