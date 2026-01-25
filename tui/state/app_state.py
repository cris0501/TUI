from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class PromptState:
    """Estado del componente prompt."""
    text: str = ""
    cursor_position: int = 0
    max_length: int = 256

@dataclass
class LogsState:
    """Estado del componente logs."""
    lines: List[str] = field(default_factory=list)
    max_lines: int = 500
    
    def append_line(self, line: str) -> None:
        """Añade una línea manteniendo el límite máximo."""
        self.lines.append(line)
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]

@dataclass
class FooterState:
    """Estado del componente footer."""
    options: Dict[str, str] = field(default_factory=dict)
    current_action: str = ""
    
    def __post_init__(self):
        if not self.options:
            self.options = {
                'F1': 'Update',
                'F2': 'Add', 
                'F3': 'Test',
                'F4': 'Config',
                'F5': 'Help',
                'F9': 'Exit'
            }

@dataclass
class TitleState:
    """Estado del componente title."""
    app_name: str = "TUI"
    version: str = "1.0.0"

@dataclass
class UIState:
    """Estado relacionado con la UI."""
    width: int = 80
    height: int = 24
    needs_resize: bool = False
    
    def update_dimensions(self, width: int, height: int) -> None:
        """Actualiza las dimensiones y marca resize."""
        if self.width != width or self.height != height:
            self.width = width
            self.height = height
            self.needs_resize = True
    
    def clear_resize_flag(self) -> None:
        """Limpia la bandera de resize."""
        self.needs_resize = False

@dataclass
class AppState:
    """
    Estado global mínimo y explícito de la aplicación.
    
    No hay reactividad automática. Las mutaciones ocurren
    explícitamente a través de eventos y handlers.
    """
    prompt: PromptState = field(default_factory=PromptState)
    logs: LogsState = field(default_factory=LogsState)
    footer: FooterState = field(default_factory=FooterState)
    title: TitleState = field(default_factory=TitleState)
    ui: UIState = field(default_factory=UIState)
    
    # Estado de la aplicación
    running: bool = True
    debug_mode: bool = False
    
    # Configuración
    config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicialización después de la creación."""
        if not self.config:
            self.config = {
                'tick_interval': 0.01,
                'max_log_lines': 500,
                'prompt_max_length': 256
            }
    
    # Métodos de conveniencia para mutación explícita
    def shutdown(self) -> None:
        """Marca la aplicación para terminar."""
        self.running = False
    
    def toggle_debug(self) -> None:
        """Activa/desactiva modo debug."""
        self.debug_mode = not self.debug_mode
    
    # Métodos de estado específicos
    def get_active_widget_count(self) -> int:
        """Obtiene el número de widgets activos."""
        return 4  # title, logs, prompt, footer
    
    def is_healthy(self) -> bool:
        """Verifica si el estado es consistente."""
        return (
            self.prompt.cursor_position >= 0 and
            self.prompt.cursor_position <= len(self.prompt.text) and
            len(self.prompt.text) <= self.prompt.max_length and
            len(self.logs.lines) <= self.logs.max_lines and
            self.ui.width > 0 and
            self.ui.height > 0
        )