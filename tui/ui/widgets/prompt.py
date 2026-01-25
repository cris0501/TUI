from typing import Dict, Any
from .base import Widget, RenderData

class PromptWidget(Widget):
    """Widget para el prompt de entrada de texto."""
    
    def __init__(self):
        super().__init__("prompt")
        self._focused = True
        self._visible = True
    
    def get_render_data(self, app_state: Dict[str, Any]) -> RenderData:
        """
        Obtiene los datos para renderizar el prompt.
        
        Args:
            app_state: Estado global de la aplicación
            
        Returns:
            RenderData con el contenido del prompt
        """
        prompt_state = app_state.get('prompt', {})
        text = prompt_state.get('text', '')
        cursor_pos = prompt_state.get('cursor_position', 0)
        ui_state = app_state.get('ui', {})
        width = ui_state.get('width', 80)
        
        # Preparar el texto del prompt
        prompt_line = f"> {text}"
        
        # Truncar si es muy largo
        if len(prompt_line) > width:
            # Mantener el cursor visible
            if cursor_pos + 2 > width:
                # Mostrar el final del texto
                start_idx = len(prompt_line) - width
                prompt_line = prompt_line[start_idx:]
                cursor_pos = width - 2
            else:
                prompt_line = prompt_line[:width]
        
        # Calcular posición del cursor en la línea visible
        cursor_x = cursor_pos + 2  # +2 por "> "
        
        return RenderData(
            content=prompt_line,
            cursor_x=cursor_x,
            cursor_y=0,
            attributes={
                'editable': True,
                'focused': self._focused
            }
        )
    
    def can_focus(self) -> bool:
        """El prompt puede recibir foco."""
        return True
    
    def validate_state(self, app_state: Dict[str, Any]) -> bool:
        """Valida que el estado sea compatible con este widget."""
        return ('prompt' in app_state and 
                'ui' in app_state and
                isinstance(app_state.get('prompt', {}).get('text'), str) and
                isinstance(app_state.get('prompt', {}).get('cursor_position'), int))