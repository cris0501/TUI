from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Set, List
from queue import Queue, Empty
import time

@dataclass
class RenderRequest:
    """Solicitud de renderizado para un widget específico."""
    widget_id: str
    priority: int = 0  # Mayor número = mayor prioridad
    timestamp: float = field(default_factory=time.time)
    
    def __lt__(self, other):
        """Para ordenamiento por prioridad y tiempo."""
        if self.priority != other.priority:
            return self.priority > other.priority  # Mayor prioridad primero
        return self.timestamp < other.timestamp  # Más antiguo primero

class RenderQueue:
    """
    Cola de solicitudes de redraw para desacoplar renderizado.
    
    Los widgets no se redibujan directamente, sino que encolan
    solicitudes que son procesadas por el Renderer central.
    """
    
    def __init__(self):
        self._queue: Queue[RenderRequest] = Queue()
        self._pending_widgets: Set[str] = set()
        self._last_render_times: Dict[str, float] = {}
    
    def schedule_render(self, request: RenderRequest) -> None:
        """
        Encola una solicitud de renderizado.
        
        Args:
            request: Solicitud de renderizado
        """
        # Evitar duplicados del mismo widget
        if request.widget_id not in self._pending_widgets:
            self._pending_widgets.add(request.widget_id)
            self._queue.put(request)
    
    def schedule_widget_render(self, widget_id: str, priority: int = 0) -> None:
        """
        Método de conveniencia para encolar renderizado de un widget.
        
        Args:
            widget_id: ID del widget a renderizar
            priority: Prioridad de renderizado
        """
        request = RenderRequest(widget_id=widget_id, priority=priority)
        self.schedule_render(request)
    
    def get_next_request(self, timeout: Optional[float] = None) -> Optional[RenderRequest]:
        """
        Obtiene la siguiente solicitud de renderizado.
        
        Args:
            timeout: Tiempo de espera máximo
            
        Returns:
            Solicitud de renderizado o None si no hay
        """
        try:
            request = self._queue.get(timeout=timeout)
            self._pending_widgets.discard(request.widget_id)
            return request
        except Empty:
            return None
    
    def get_all_pending_requests(self) -> List[RenderRequest]:
        """
        Obtiene todas las solicitudes pendientes.
        
        Returns:
            Lista de todas las solicitudes pendientes
        """
        requests = []
        while not self._queue.empty():
            try:
                request = self._queue.get_nowait()
                self._pending_widgets.discard(request.widget_id)
                requests.append(request)
            except Empty:
                break
        return requests
    
    def has_pending_renders(self) -> bool:
        """
        Verifica si hay renders pendientes.
        
        Returns:
            True si hay solicitudes pendientes
        """
        return not self._queue.empty()
    
    def get_pending_count(self) -> int:
        """
        Obtiene el número de solicitudes pendientes.
        
        Returns:
            Número de solicitudes en cola
        """
        return self._queue.qsize()
    
    def get_pending_widgets(self) -> Set[str]:
        """
        Obtiene los IDs de widgets con renders pendientes.
        
        Returns:
            Set de widget IDs pendientes
        """
        return self._pending_widgets.copy()
    
    def clear_pending_for_widget(self, widget_id: str) -> bool:
        """
        Limpia solicitudes pendientes para un widget específico.
        
        Args:
            widget_id: ID del widget
            
        Returns:
            True si había solicitudes pendientes, False si no
        """
        if widget_id in self._pending_widgets:
            # Reconstruir cola sin las solicitudes del widget
            temp_requests = []
            while not self._queue.empty():
                try:
                    request = self._queue.get_nowait()
                    if request.widget_id != widget_id:
                        temp_requests.append(request)
                except Empty:
                    break
            
            # Reencolar solicitudes válidas
            for request in temp_requests:
                self._queue.put(request)
            
            self._pending_widgets.discard(widget_id)
            return True
        return False
    
    def clear_all(self) -> None:
        """
        Limpia todas las solicitudes pendientes.
        """
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except Empty:
                break
        self._pending_widgets.clear()
    
    def record_render_time(self, widget_id: str, render_time: float) -> None:
        """
        Registra el tiempo de renderizado para métricas.
        
        Args:
            widget_id: ID del widget renderizado
            render_time: Tiempo en segundos
        """
        self._last_render_times[widget_id] = render_time
    
    def get_last_render_time(self, widget_id: str) -> Optional[float]:
        """
        Obtiene el último tiempo de renderizado de un widget.
        
        Args:
            widget_id: ID del widget
            
        Returns:
            Tiempo de renderizado o None si no existe
        """
        return self._last_render_times.get(widget_id)