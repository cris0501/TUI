import curses
from typing import Dict, Any, Optional
from ..state.render_queue import RenderRequest, RenderQueue
from ..ui.layout import LayoutService, Dimensions
from ..ui.widgets.base import Widget, RenderData

class Renderer:
    """
    Único componente con acceso directo a curses.
    
    Consume la RenderQueue y redibuja todo en un solo paso.
    Ningún otro componente puede llamar directamente a curses.
    """
    
    def __init__(self, stdscr, layout: LayoutService):
        self._stdscr = stdscr
        self._layout = layout
        self._widgets: Dict[str, Widget] = {}
        self._subwindows: Dict[str, Any] = {}  # curses subwindows
        self._render_queue: Optional[RenderQueue] = None
        self._initialized = False
    
    def set_render_queue(self, render_queue: RenderQueue) -> None:
        """
        Establece la cola de renderizado.
        
        Args:
            render_queue: Cola de solicitudes de renderizado
        """
        self._render_queue = render_queue
    
    def register_widget(self, widget: Widget) -> None:
        """
        Registra un widget para renderizado.
        
        Args:
            widget: Widget a registrar
        """
        self._widgets[widget.widget_id] = widget
        self._create_subwindow(widget.widget_id)
    
    def unregister_widget(self, widget_id: str) -> None:
        """
        Remueve un widget del registro.
        
        Args:
            widget_id: ID del widget a remover
        """
        if widget_id in self._widgets:
            del self._widgets[widget_id]
        
        if widget_id in self._subwindows:
            try:
                self._subwindows[widget_id].clear()
                self._subwindows[widget_id].refresh()
            except:
                pass
            del self._subwindows[widget_id]
    
    def initialize(self) -> None:
        """
        Inicializa el renderer y configura curses.
        """
        if self._initialized:
            return
        
        # Configuración inicial de curses
        curses.curs_set(1)
        self._stdscr.nodelay(True)
        self._stdscr.keypad(True)
        
        # Crear subwindows para todos los widgets registrados
        for widget_id in self._widgets:
            self._create_subwindow(widget_id)
        
        self._initialized = True
    
    def _create_subwindow(self, widget_id: str) -> None:
        """
        Crea o actualiza la subwindow para un widget.
        
        Args:
            widget_id: ID del widget
        """
        area = self._layout.get_widget_area(widget_id)
        if area is None:
            return
        
        # Remover subwindow existente si hay
        if widget_id in self._subwindows:
            try:
                self._subwindows[widget_id].clear()
            except:
                pass
        
        # Crear nueva subwindow
        try:
            subwin = self._stdscr.subwin(
                area.height,
                area.width,
                area.y,
                area.x
            )
            self._subwindows[widget_id] = subwin
        except curses.error:
            # Si falla la creación, puede ser por tamaño inválido
            pass
    
    def render_pending_requests(self) -> None:
        """
        Procesa todas las solicitudes de renderizado pendientes.
        """
        if not self._render_queue or not self._initialized:
            return
        
        # Obtener todas las solicitudes pendientes
        requests = self._render_queue.get_all_pending_requests()
        
        if not requests:
            return
        
        # Agrupar por widget para evitar renderizados duplicados
        widgets_to_render = set(req.widget_id for req in requests)
        
        # Renderizar cada widget una vez
        for widget_id in widgets_to_render:
            self._render_widget(widget_id)
        
        # Actualizar la pantalla una sola vez
        self._update_screen()
    
    def _render_widget(self, widget_id: str) -> None:
        """
        Renderiza un widget específico.
        
        Args:
            widget_id: ID del widget a renderizar
        """
        widget = self._widgets.get(widget_id)
        subwin = self._subwindows.get(widget_id)
        
        if not widget or not subwin:
            return
        
        if not widget.visible:
            # Limpiar la subwindow si no está visible
            subwin.clear()
            return
        
        # Verificar que el área sea válida
        area = self._layout.get_widget_area(widget_id)
        if not area or area.width <= 0 or area.height <= 0:
            return
        
        try:
            # Obtener datos del widget
            app_state = self._get_app_state()  # Esto se implementará
            render_data = widget.get_render_data(app_state)
            
            # Limpiar y dibujar
            subwin.clear()
            self._draw_content(subwin, render_data, area)
            
            # Configurar cursor si aplica
            if (widget.focused and 
                render_data.cursor_x is not None and 
                render_data.cursor_y is not None):
                try:
                    subwin.move(render_data.cursor_y, render_data.cursor_x)
                except curses.error:
                    pass
                    
        except Exception as e:
            # En caso de error, limpiar la subwindow
            try:
                subwin.clear()
            except:
                pass
    
    def _draw_content(self, subwin, render_data: RenderData, area: Dimensions) -> None:
        """
        Dibuja el contenido en la subwindow.
        
        Args:
            subwin: Subwindow de curses
            render_data: Datos a renderizar
            area: Área disponible
        """
        if not render_data.content:
            return
        
        lines = render_data.content.split('\n')
        
        for i, line in enumerate(lines):
            if i >= area.height:
                break
            
            # Truncar línea si es necesario
            if len(line) > area.width:
                line = line[:area.width]
            
            try:
                subwin.addstr(i, 0, line)
            except curses.error:
                # Ignorar errores de dibujado fuera de límites
                pass
    
    def _update_screen(self) -> None:
        """
        Actualiza la pantalla física.
        """
        try:
            # Refrescar todas las subwindows
            for subwin in self._subwindows.values():
                subwin.noutrefresh()
            
            # Actualizar pantalla principal
            curses.doupdate()
        except curses.error:
            pass
    
    def _get_app_state(self) -> Dict[str, Any]:
        """
        Obtiene el estado global de la aplicación.
        
        Returns:
            Diccionario con estado de la aplicación
        """
        try:
            from ..core.context import get_global_context
            context = get_global_context()
            app_state = context.get_app_state()
            
            # Convertir dataclasses a diccionarios para compatibilidad con widgets
            return {
                'title': {
                    'app_name': app_state.title.app_name,
                    'version': app_state.title.version
                },
                'logs': {
                    'lines': list(app_state.logs.lines),
                    'max_lines': app_state.logs.max_lines
                },
                'prompt': {
                    'text': app_state.prompt.text,
                    'cursor_position': app_state.prompt.cursor_position,
                    'max_length': app_state.prompt.max_length
                },
                'footer': {
                    'options': dict(app_state.footer.options),
                    'current_action': app_state.footer.current_action
                },
                'ui': {
                    'width': app_state.ui.width,
                    'height': app_state.ui.height,
                    'needs_resize': app_state.ui.needs_resize,
                    'title_height': 1,
                    'prompt_height': 2,
                    'footer_height': 1
                }
            }
        except Exception:
            # Fallback en caso de error
            return {
                'title': {'app_name': 'TUI', 'version': '1.0.0'},
                'logs': {'lines': [], 'max_lines': 500},
                'prompt': {'text': '', 'cursor_position': 0, 'max_length': 256},
                'footer': {'options': {}, 'current_action': ''},
                'ui': {'width': 80, 'height': 24, 'needs_resize': False,
                       'title_height': 1, 'prompt_height': 2, 'footer_height': 1}
            }
    
    def handle_resize(self) -> None:
        """
        Maneja un evento de resize de terminal.
        """
        # Recrear todas las subwindows
        for widget_id in self._widgets:
            self._create_subwindow(widget_id)
        
        # Forzar renderizado completo
        if self._render_queue:
            for widget_id in self._widgets:
                self._render_queue.schedule_widget_render(widget_id)
    
    def cleanup(self) -> None:
        """
        Limpia recursos del renderer.
        """
        # Limpiar todas las subwindows
        for subwin in self._subwindows.values():
            try:
                subwin.clear()
                subwin.refresh()
            except:
                pass
        
        self._subwindows.clear()
        self._initialized = False