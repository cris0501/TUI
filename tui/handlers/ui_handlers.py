from typing import Dict, Any

from ..core.events import Event, EventType
from ..core.context import get_global_context

class UIHandlers:
    """
    Handlers para reacciones visuales a eventos de estado.
    
    Se encarga de encolar redraws en RenderQueue cuando
    cambia el estado que requiere actualización visual.
    """
    
    def __init__(self):
        self._context = get_global_context()
    
    def handle_prompt_text_changed(self, event: Event) -> None:
        """
        Maneja cambios en el texto del prompt.
        
        Args:
            event: Evento de cambio de texto
        """
        # Actualizar estado del prompt
        app_state = self._context.get_app_state()
        app_state.prompt.text = event.payload.get('text', '')
        if 'cursor_position' in event.payload:
            app_state.prompt.cursor_position = event.payload['cursor_position']
        
        # Encolar renderizado del prompt
        self._context.schedule_render('prompt')
    
    def handle_logs_append(self, event: Event) -> None:
        """
        Maneja adición de líneas a los logs.
        
        Args:
            event: Evento de append de logs
        """
        # Actualizar estado de logs
        app_state = self._context.get_app_state()
        line = event.payload.get('line', '')
        if line:  # Solo añadir si no es vacío (para clear)
            if event.payload.get('clear', False):
                app_state.logs.lines.clear()
            else:
                app_state.logs.append_line(line)
        
        # Encolar renderizado de logs
        self._context.schedule_render('logs')
    
    def handle_footer_action(self, event: Event) -> None:
        """
        Maneja acciones del footer.
        
        Args:
            event: Evento de acción de footer
        """
        # Actualizar estado del footer
        app_state = self._context.get_app_state()
        action = event.payload.get('action', '')
        app_state.footer.current_action = action
        
        # Encolar renderizado del footer
        self._context.schedule_render('footer')
        
        # Manejar acciones específicas
        if action == 'F9':
            # Salir de la aplicación
            from ..core.events import ShutdownEvent
            shutdown_event = ShutdownEvent(
                event_type=EventType.SHUTDOWN,
                source="ui_handler",
                payload={"reason": "footer_exit"}
            )
            self._context.emit_event(shutdown_event)
    
    def handle_resize(self, event: Event) -> None:
        """
        Maneja eventos de resize de terminal.
        
        Args:
            event: Evento de resize
        """
        # Actualizar estado de UI
        app_state = self._context.get_app_state()
        width = event.payload.get('width', 80)
        height = event.payload.get('height', 24)
        app_state.ui.update_dimensions(width, height)
        
        # Forzar recálculo de layout
        self._context.get_layout().update_terminal_size(width, height)
        
        # Encolar renderizado de todos los widgets
        self._context.schedule_render('title')
        self._context.schedule_render('logs')
        self._context.schedule_render('prompt')
        self._context.schedule_render('footer')
    
    def handle_render_request(self, event: Event) -> None:
        """
        Maneja solicitudes explícitas de renderizado.
        
        Args:
            event: Evento de solicitud de render
        """
        # Encolar renderizado del widget solicitado
        widget_id = event.payload.get('widget_id', '')
        if widget_id:
            self._context.schedule_render(widget_id)
    
    def handle_tick(self, event: Event) -> None:
        """
        Maneja eventos de tick del sistema.
        
        Args:
            event: Evento de tick
        """
        # Verificar si hay cambios pendientes que requieren renderizado
        app_state = self._context.get_app_state()
        
        # Si hay resize pendiente, procesarlo
        if app_state.ui.needs_resize:
            self.handle_resize(event)
            app_state.ui.clear_resize_flag()
    
    def handle_shutdown(self, event: Event) -> None:
        """
        Maneja eventos de shutdown.
        
        Args:
            event: Evento de shutdown
        """
        # Marcar aplicación como no corriendo
        app_state = self._context.get_app_state()
        app_state.running = False
        
        # Detener message loop
        try:
            self._context.get_message_loop().stop()
        except:
            pass

def register_ui_handlers(event_bus) -> None:
    """
    Registra todos los UI handlers en el Event Bus.
    
    Args:
        event_bus: EventBus donde registrar los handlers
    """
    handlers = UIHandlers()
    
    # Registrar handlers para cada tipo de evento
    event_bus.register(EventType.PROMPT_TEXT_CHANGED, handlers.handle_prompt_text_changed)
    event_bus.register(EventType.LOGS_APPEND, handlers.handle_logs_append)
    event_bus.register(EventType.FOOTER_ACTION, handlers.handle_footer_action)
    event_bus.register(EventType.RESIZE, handlers.handle_resize)
    event_bus.register(EventType.RENDER_REQUEST, handlers.handle_render_request)
    event_bus.register(EventType.TICK, handlers.handle_tick)
    event_bus.register(EventType.SHUTDOWN, handlers.handle_shutdown)