from typing import Dict, Any
from .base import Widget, RenderData

class FooterWidget(Widget):
    """Widget para mostrar el footer con opciones."""
    
    def __init__(self):
        super().__init__("footer")
    
    def get_render_data(self, app_state: Dict[str, Any]) -> RenderData:
        """
        Obtiene los datos para renderizar el footer.
        
        Args:
            app_state: Estado global de la aplicación
            
        Returns:
            RenderData con el contenido del footer
        """
        footer_state = app_state.get('footer', {})
        options = footer_state.get('options', {})
        current_action = footer_state.get('current_action', '')
        ui_state = app_state.get('ui', {})
        width = ui_state.get('width', 80)
        
        # Construir string de opciones
        option_parts = []
        for key, label in options.items():
            option_parts.append(f"{key}:{label}")
        
        options_text = " | ".join(option_parts)
        
        # Truncar si es muy largo
        if len(options_text) > width:
            options_text = options_text[:width-3] + "..."
        
        return RenderData(
            content=options_text,
            attributes={
                'options': options,
                'current_action': current_action
            }
        )
    
    def validate_state(self, app_state: Dict[str, Any]) -> bool:
        """Valida que el estado sea compatible con este widget."""
        return ('footer' in app_state and 
                'ui' in app_state and
                isinstance(app_state.get('footer', {}).get('options'), dict))