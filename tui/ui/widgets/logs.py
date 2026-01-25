from typing import Dict, Any
from .base import Widget, RenderData

class LogsWidget(Widget):
    """Widget para mostrar logs de la aplicación."""
    
    def __init__(self):
        super().__init__("logs")
    
    def get_render_data(self, app_state: Dict[str, Any]) -> RenderData:
        """
        Obtiene los datos para renderizar los logs.
        
        Args:
            app_state: Estado global de la aplicación
            
        Returns:
            RenderData con el contenido de los logs
        """
        logs_state = app_state.get('logs', {})
        lines = logs_state.get('lines', [])
        ui_state = app_state.get('ui', {})
        height = ui_state.get('height', 24)
        title_height = app_state.get('ui', {}).get('title_height', 1)
        prompt_height = app_state.get('ui', {}).get('prompt_height', 2)
        footer_height = app_state.get('ui', {}).get('footer_height', 1)
        
        # Calcular altura disponible para logs
        available_height = height - title_height - prompt_height - footer_height
        
        # Obtener las últimas líneas que caben
        if len(lines) > available_height:
            display_lines = lines[-available_height:]
        else:
            display_lines = lines
        
        # Unir todas las líneas
        content = '\n'.join(display_lines) if display_lines else ""
        
        return RenderData(
            content=content,
            attributes={
                'scrollable': True,
                'line_count': len(display_lines),
                'total_lines': len(lines)
            }
        )
    
    def validate_state(self, app_state: Dict[str, Any]) -> bool:
        """Valida que el estado sea compatible con este widget."""
        return ('logs' in app_state and 
                'ui' in app_state and
                isinstance(app_state.get('logs', {}).get('lines'), list))