from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class RenderData:
    """Datos que un widget provee para ser renderizado."""
    content: str = ""
    cursor_x: Optional[int] = None
    cursor_y: Optional[int] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

class Widget(ABC):
    """
    Contrato base para todos los widgets del sistema.
    
    Los widgets:
    - No gestionan flujo global
    - No acceden a curses directamente  
    - Proporcionan datos de renderizado
    - Pueden manejar eventos locales
    """
    
    def __init__(self, widget_id: str):
        self.widget_id = widget_id
        self._visible = True
        self._focused = False
    
    @abstractmethod
    def get_render_data(self, app_state: Dict[str, Any]) -> RenderData:
        """
        Obtiene los datos necesarios para renderizar el widget.
        
        Args:
            app_state: Estado global de la aplicación
            
        Returns:
            RenderData con información para el renderer
        """
        pass
    
    def handle_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Maneja un evento local del widget.
        
        Args:
            event_data: Datos del evento
            
        Returns:
            True si el evento fue manejado, False si no
        """
        # Implementación por defecto: no maneja eventos
        return False
    
    @property
    def visible(self) -> bool:
        """Verifica si el widget es visible."""
        return self._visible
    
    @visible.setter
    def visible(self, value: bool) -> None:
        """Establece la visibilidad del widget."""
        self._visible = value
    
    @property
    def focused(self) -> bool:
        """Verifica si el widget tiene el foco."""
        return self._focused
    
    @focused.setter
    def focused(self, value: bool) -> None:
        """Establece el foco del widget."""
        self._focused = value
    
    def can_focus(self) -> bool:
        """
        Determina si el widget puede recibir foco.
        
        Returns:
            True si puede recibir foco, False si no
        """
        return False
    
    def get_min_dimensions(self) -> tuple[int, int]:
        """
        Obtiene las dimensiones mínimas requeridas.
        
        Returns:
            Tuple (min_width, min_height)
        """
        return (1, 1)
    
    def validate_state(self, app_state: Dict[str, Any]) -> bool:
        """
        Valida que el estado sea compatible con este widget.
        
        Args:
            app_state: Estado global de la aplicación
            
        Returns:
            True si es válido, False si no
        """
        return True