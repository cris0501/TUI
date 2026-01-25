from typing import Any, Dict, Optional
from .event_bus import EventBus
from .message_loop import MessageLoop
from ..state.app_state import AppState
from ..state.render_queue import RenderQueue
from ..ui.layout import LayoutService
from ..ui.renderer import Renderer

class Context:
    """
    Contenedor de dependencias compartidas para toda la aplicación.
    
    Provee acceso controlado a los componentes principales para handlers
    y otros servicios que necesiten interactuar con el sistema.
    """
    
    def __init__(self):
        self._event_bus: Optional[EventBus] = None
        self._message_loop: Optional[MessageLoop] = None
        self._app_state: Optional[AppState] = None
        self._render_queue: Optional[RenderQueue] = None
        self._layout: Optional[LayoutService] = None
        self._renderer: Optional[Renderer] = None
        self._services: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
    
    # Core components
    def set_event_bus(self, event_bus: EventBus) -> None:
        """Registra el EventBus global."""
        self._event_bus = event_bus
    
    def get_event_bus(self) -> EventBus:
        """Obtiene el EventBus global."""
        if self._event_bus is None:
            raise RuntimeError("EventBus not initialized")
        return self._event_bus
    
    def set_message_loop(self, message_loop: MessageLoop) -> None:
        """Registra el MessageLoop global."""
        self._message_loop = message_loop
    
    def get_message_loop(self) -> MessageLoop:
        """Obtiene el MessageLoop global."""
        if self._message_loop is None:
            raise RuntimeError("MessageLoop not initialized")
        return self._message_loop
    
    def set_app_state(self, app_state: AppState) -> None:
        """Registra el AppState global."""
        self._app_state = app_state
    
    def get_app_state(self) -> AppState:
        """Obtiene el AppState global."""
        if self._app_state is None:
            raise RuntimeError("AppState not initialized")
        return self._app_state
    
    def set_render_queue(self, render_queue: RenderQueue) -> None:
        """Registra la RenderQueue global."""
        self._render_queue = render_queue
    
    def get_render_queue(self) -> RenderQueue:
        """Obtiene la RenderQueue global."""
        if self._render_queue is None:
            raise RuntimeError("RenderQueue not initialized")
        return self._render_queue
    
    # UI components
    def set_layout(self, layout: LayoutService) -> None:
        """Registra el LayoutService."""
        self._layout = layout
    
    def get_layout(self) -> LayoutService:
        """Obtiene el LayoutService."""
        if self._layout is None:
            raise RuntimeError("LayoutService not initialized")
        return self._layout
    
    def set_renderer(self, renderer: Renderer) -> None:
        """Registra el Renderer."""
        self._renderer = renderer
    
    def get_renderer(self) -> Renderer:
        """Obtiene el Renderer."""
        if self._renderer is None:
            raise RuntimeError("Renderer not initialized")
        return self._renderer
    
    # Services
    def register_service(self, name: str, service: Any) -> None:
        """
        Registra un servicio con un nombre específico.
        
        Args:
            name: Nombre del servicio
            service: Instancia del servicio
        """
        self._services[name] = service
    
    def get_service(self, name: str) -> Any:
        """
        Obtiene un servicio por nombre.
        
        Args:
            name: Nombre del servicio
            
        Returns:
            Instancia del servicio
            
        Raises:
            RuntimeError: Si el servicio no está registrado
        """
        if name not in self._services:
            raise RuntimeError(f"Service '{name}' not registered")
        return self._services[name]
    
    def has_service(self, name: str) -> bool:
        """
        Verifica si un servicio está registrado.
        
        Args:
            name: Nombre del servicio
            
        Returns:
            True si está registrado, False si no
        """
        return name in self._services
    
    # Configuration
    def set_config(self, key: str, value: Any) -> None:
        """
        Establece un valor de configuración.
        
        Args:
            key: Clave de configuración
            value: Valor
        """
        self._config[key] = value
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración.
        
        Args:
            key: Clave de configuración
            default: Valor por defecto si no existe
            
        Returns:
            Valor de configuración o default
        """
        return self._config.get(key, default)
    
    # Convenience methods
    def emit_event(self, event) -> None:
        """
        Emite un evento al MessageLoop (conveniencia).
        
        Args:
            event: Evento a emitir
        """
        self.get_message_loop().put_event(event)
    
    def schedule_render(self, widget_id: str) -> None:
        """
        Encola un render request (conveniencia).
        
        Args:
            widget_id: ID del widget a renderizar
        """
        from ..state.render_queue import RenderRequest
        self.get_render_queue().schedule_render(RenderRequest(widget_id))
    
    def is_initialized(self) -> bool:
        """
        Verifica si todos los componentes core están inicializados.
        
        Returns:
            True si está completamente inicializado
        """
        required_components = [
            self._event_bus,
            self._message_loop,
            self._app_state,
            self._render_queue,
            self._layout,
            self._renderer
        ]
        return all(comp is not comp for comp in required_components)

# Global context instance
_global_context: Optional[Context] = None

def get_global_context() -> Context:
    """
    Obtiene el contexto global de la aplicación.
    
    Returns:
        Instancia global de Context
    """
    global _global_context
    if _global_context is None:
        _global_context = Context()
    return _global_context

def set_global_context(context: Context) -> None:
    """
    Establece el contexto global (principalmente para pruebas).
    
    Args:
        context: Nueva instancia de Context
    """
    global _global_context
    _global_context = context