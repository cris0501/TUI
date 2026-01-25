from typing import Dict, List, Callable, Any
from .events import EventType, Event

EventHandler = Callable[[Event], None]

class EventBus:
    """
    Event Bus pasivo que solo registra handlers.
    No ejecuta lógica ni tiene estado de runtime.
    Solo mantiene un registro de qué handler corresponde a cada tipo de evento.
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
    
    def register(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Registra un handler para un tipo de evento específico.
        
        Args:
            event_type: Tipo de evento a manejar
            handler: Función que procesará el evento
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unregister(self, event_type: EventType, handler: EventHandler) -> bool:
        """
        Remueve un handler del registro.
        
        Args:
            event_type: Tipo de evento
            handler: Handler a remover
            
        Returns:
            True si se removió exitosamente, False si no se encontró
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass
        return False
    
    def get_handlers(self, event_type: EventType) -> List[EventHandler]:
        """
        Obtiene todos los handlers registrados para un tipo de evento.
        
        Args:
            event_type: Tipo de evento
            
        Returns:
            Lista de handlers registrados (puede estar vacía)
        """
        return self._handlers.get(event_type, []).copy()
    
    def get_all_registered_events(self) -> List[EventType]:
        """
        Obtiene todos los tipos de eventos que tienen handlers registrados.
        
        Returns:
            Lista de EventType con handlers registrados
        """
        return list(self._handlers.keys())
    
    def clear_all(self) -> None:
        """
        Limpia todos los handlers registrados.
        Útil para pruebas o reinicialización.
        """
        self._handlers.clear()
    
    def get_handler_count(self, event_type: EventType) -> int:
        """
        Obtiene el número de handlers registrados para un tipo de evento.
        
        Args:
            event_type: Tipo de evento
            
        Returns:
            Número de handlers registrados
        """
        return len(self._handlers.get(event_type, []))