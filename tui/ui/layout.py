from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any

@dataclass
class Dimensions:
    """Dimensiones de un área o widget."""
    width: int
    height: int
    x: int = 0
    y: int = 0
    
    def contains_point(self, x: int, y: int) -> bool:
        """Verifica si un punto está dentro del área."""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Obtiene (x1, y1, x2, y2)."""
        return (self.x, self.y, self.x + self.width - 1, self.y + self.height - 1)

@dataclass
class LayoutConfig:
    """Configuración global del layout."""
    title_height: int = 1
    footer_height: int = 1
    prompt_height: int = 2
    min_width: int = 20
    min_height: int = 10

class LayoutService:
    """
    Servicio de layout que gestiona las dimensiones y posiciones
    de los widgets en la terminal.
    """
    
    def __init__(self, config: Optional[LayoutConfig] = None):
        self._config = config or LayoutConfig()
        self._terminal_width = 80
        self._terminal_height = 24
        self._widget_areas: Dict[str, Dimensions] = {}
        self._needs_recalculate = True
    
    def update_terminal_size(self, width: int, height: int) -> None:
        """
        Actualiza el tamaño de la terminal y marca para recálculo.
        
        Args:
            width: Ancho de la terminal
            height: Alto de la terminal
        """
        if width != self._terminal_width or height != self._terminal_height:
            self._terminal_width = max(width, self._config.min_width)
            self._terminal_height = max(height, self._config.min_height)
            self._needs_recalculate = True
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """
        Obtiene el tamaño actual de la terminal.
        
        Returns:
            Tuple (width, height)
        """
        return (self._terminal_width, self._terminal_height)
    
    def get_widget_area(self, widget_id: str) -> Optional[Dimensions]:
        """
        Obtiene el área asignada a un widget.
        
        Args:
            widget_id: ID del widget
            
        Returns:
            Dimensions del widget o None si no existe
        """
        if self._needs_recalculate:
            self._recalculate_layout()
        
        return self._widget_areas.get(widget_id)
    
    def get_all_widget_areas(self) -> Dict[str, Dimensions]:
        """
        Obtiene todas las áreas de widgets.
        
        Returns:
            Diccionario de widget_id -> Dimensions
        """
        if self._needs_recalculate:
            self._recalculate_layout()
        
        return self._widget_areas.copy()
    
    def _recalculate_layout(self) -> None:
        """Recalcula el layout de widgets basado en el tamaño actual."""
        self._widget_areas.clear()
        
        w, h = self._terminal_width, self._terminal_height
        
        # Title (línea superior)
        self._widget_areas['title'] = Dimensions(
            width=w,
            height=self._config.title_height,
            x=0,
            y=0
        )
        
        # Footer (línea inferior)
        self._widget_areas['footer'] = Dimensions(
            width=w,
            height=self._config.footer_height,
            x=0,
            y=max(0, h - self._config.footer_height)
        )
        
        # Prompt (arriba del footer)
        self._widget_areas['prompt'] = Dimensions(
            width=w,
            height=self._config.prompt_height,
            x=0,
            y=max(0, h - self._config.footer_height - self._config.prompt_height)
        )
        
        # Logs (área central)
        logs_y = self._config.title_height
        logs_height = max(1, h - self._config.title_height - 
                         self._config.prompt_height - self._config.footer_height)
        
        self._widget_areas['logs'] = Dimensions(
            width=w,
            height=logs_height,
            x=0,
            y=logs_y
        )
        
        self._needs_recalculate = False
    
    def is_valid_layout(self) -> bool:
        """
        Verifica si el layout actual es válido.
        
        Returns:
            True si todas las áreas son válidas
        """
        if self._needs_recalculate:
            self._recalculate_layout()
        
        # Verificar que todas las áreas estén dentro de la terminal
        for widget_id, area in self._widget_areas.items():
            if (area.width <= 0 or area.height <= 0 or
                area.x < 0 or area.y < 0 or
                area.x + area.width > self._terminal_width or
                area.y + area.height > self._terminal_height):
                return False
        
        return True
    
    def force_recalculate(self) -> None:
        """Fuerza el recálculo del layout en el próximo acceso."""
        self._needs_recalculate = True
    
    def get_config(self) -> LayoutConfig:
        """
        Obtiene la configuración actual del layout.
        
        Returns:
            LayoutConfig actual
        """
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """
        Actualiza parámetros de configuración.
        
        Args:
            **kwargs: Parámetros a actualizar
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self._needs_recalculate = True