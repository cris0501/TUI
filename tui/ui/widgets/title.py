from typing import Dict, Any
from .base import Widget, RenderData

class TitleWidget(Widget):
    """Widget para mostrar el título de la aplicación."""
    
    def __init__(self):
        super().__init__("title")
    
    def get_render_data(self, app_state: Dict[str, Any]) -> RenderData:
        """
        Obtiene los datos para renderizar el título.
        
        Args:
            app_state: Estado global de la aplicación
            
        Returns:
            RenderData con el contenido del título
        """
        title_state = app_state.get('title', {})
        app_name = title_state.get('app_name', 'TUI')
        version = title_state.get('version', '1.0.0')
        ui_state = app_state.get('ui', {})
        width = ui_state.get('width', 80)
        
        # Crear título centrado
        title_text = f"{app_name} v{version}"
        
        # Centrar el título en la línea
        if len(title_text) < width:
            padding = (width - len(title_text)) // 2
            title_text = ' ' * padding + title_text
        
        return RenderData(
            content=title_text,
            attributes={'centered': True}
        )
    
    def validate_state(self, app_state: Dict[str, Any]) -> bool:
        """Valida que el estado sea compatible con este widget."""
        return ('title' in app_state and 
                'ui' in app_state and
                isinstance(app_state.get('ui', {}).get('width'), int))