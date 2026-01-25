#!/usr/bin/env python3
"""
Entry point principal de la aplicación TUI.

Implementa la arquitectura message-driven con:
- Message Loop como orquestador central
- Event Bus como registro pasivo
- Render Queue desacoplada
- Estado explícito no reactivo
"""

import curses
import sys
from typing import Optional

from core.events import EventType
from core.event_bus import EventBus
from core.message_loop import MessageLoop
from core.context import get_global_context, set_global_context, Context
from state.app_state import AppState
from state.render_queue import RenderQueue
from ui.layout import LayoutService
from ui.renderer import Renderer
from ui.widgets.title import TitleWidget
from ui.widgets.logs import LogsWidget
from ui.widgets.prompt import PromptWidget
from ui.widgets.footer import FooterWidget
from handlers.input_handlers import InputHandlers
from handlers.ui_handlers import register_ui_handlers
from handlers.domain_handlers import register_domain_handlers
from services.clock import ClockService
from services.data_service import DataService


class TUIApp:
    """
    Aplicación TUI principal.
    
    Orquesta todos los componentes según la arquitectura requerida.
    """
    
    def __init__(self):
        self._stdscr: Optional[Any] = None
        self._context: Optional[Context] = None
        self._input_handlers: Optional[InputHandlers] = None
    
    def initialize(self, stdscr) -> None:
        """
        Inicializa todos los componentes de la aplicación.
        
        Args:
            stdscr: Ventana principal de curses
        """
        self._stdscr = stdscr
        
        # Crear contexto global
        self._context = Context()
        set_global_context(self._context)
        
        # Inicializar componentes core
        self._initialize_core_components()
        
        # Inicializar servicios
        self._initialize_services()
        
        # Inicializar UI
        self._initialize_ui()
        
        # Inicializar widgets
        self._initialize_widgets()
        
        # Registrar handlers
        self._register_handlers()
        
        # Configurar estado inicial
        self._setup_initial_state()
    
    def _initialize_core_components(self) -> None:
        """Inicializa componentes core del sistema."""
        # Event Bus - registro pasivo de handlers
        event_bus = EventBus()
        self._context.set_event_bus(event_bus)
        
        # App State - estado global mínimo
        app_state = AppState()
        self._context.set_app_state(app_state)
        
        # Render Queue - cola de redraws desacoplada
        render_queue = RenderQueue()
        self._context.set_render_queue(render_queue)
        
        # Message Loop - orquestador central
        message_loop = MessageLoop(event_bus, render_queue)
        self._context.set_message_loop(message_loop)
    
    def _initialize_services(self) -> None:
        """Inicializa servicios de la aplicación."""
        # Clock service para ticks
        clock = ClockService()
        self._context.register_service('clock', clock)
        
        # Data service para persistencia
        data_service = DataService()
        self._context.register_service('data', data_service)
        
        # Cargar configuración
        config = data_service.load_config()
        app_state = self._context.get_app_state()
        app_state.config.update(config)
    
    def _initialize_ui(self) -> None:
        """Inicializa componentes UI."""
        # Layout service para gestión de ventanas
        config = self._context.get_app_state().config
        layout_config = {
            'title_height': config.get('title_height', 1),
            'footer_height': config.get('footer_height', 1),
            'prompt_height': config.get('prompt_height', 2),
            'min_width': config.get('min_width', 20),
            'min_height': config.get('min_height', 10)
        }
        layout = LayoutService(**layout_config)
        self._context.set_layout(layout)
        
        # Renderer - único acceso a curses
        renderer = Renderer(self._stdscr, layout)
        self._context.set_renderer(renderer)
        
        # Configurar render queue en renderer
        render_queue = self._context.get_render_queue()
        renderer.set_render_queue(render_queue)
        
        # Inicializar renderer
        renderer.initialize()
    
    def _initialize_widgets(self) -> None:
        """Inicializa y registra widgets."""
        renderer = self._context.get_renderer()
        
        # Crear widgets
        widgets = [
            TitleWidget(),
            LogsWidget(),
            PromptWidget(),
            FooterWidget()
        ]
        
        # Registrar widgets en renderer
        for widget in widgets:
            renderer.register_widget(widget)
    
    def _register_handlers(self) -> None:
        """Registra todos los handlers en el Event Bus."""
        event_bus = self._context.get_event_bus()
        
        # Registrar UI handlers
        register_ui_handlers(event_bus)
        
        # Registrar domain handlers
        register_domain_handlers(event_bus)
        
        # Inicializar input handlers
        self._input_handlers = InputHandlers()
    
    def _setup_initial_state(self) -> None:
        """Configura el estado inicial de la aplicación."""
        app_state = self._context.get_app_state()
        
        # Actualizar dimensiones iniciales
        height, width = self._stdscr.getmaxyx()
        app_state.ui.update_dimensions(width, height)
        
        # Actualizar layout
        layout = self._context.get_layout()
        layout.update_terminal_size(width, height)
        
        # Agregar mensaje de bienvenida
        welcome_lines = [
            "╔════════════════════════════════════════╗",
            "║     TUI Application Started             ║",
            "║     Type /help for available commands  ║",
            "╚════════════════════════════════════════╝"
        ]
        
        for line in welcome_lines:
            app_state.logs.append_line(line)
        
        # Programar renderizado inicial de todos los widgets
        render_queue = self._context.get_render_queue()
        for widget_id in ['title', 'logs', 'prompt', 'footer']:
            render_queue.schedule_widget_render(widget_id)
    
    def run(self) -> None:
        """
        Ejecuta el bucle principal de la aplicación.
        """
        if not self._context:
            raise RuntimeError("App not initialized")
        
        message_loop = self._context.get_message_loop()
        
        try:
            # Bucle principal
            while self._context.get_app_state().running:
                # Procesar input
                self._process_input()
                
                # Ejecutar un tick del message loop
                message_loop.tick()
                
                # Procesar renders pendientes
                renderer = self._context.get_renderer()
                renderer.render_pending_requests()
                
                # Pequeña pausa para no consumir CPU
                curses.napms(10)
                
        except KeyboardInterrupt:
            # Manejar Ctrl+C gracefulmente
            from core.events import ShutdownEvent
            shutdown_event = ShutdownEvent(
                event_type=EventType.SHUTDOWN,
                source="app",
                payload={"reason": "interrupt"}
            )
            self._context.emit_event(shutdown_event)
        
        finally:
            self._cleanup()
    
    def _process_input(self) -> None:
        """
        Procesa input del usuario y emite eventos.
        """
        try:
            key = self._stdscr.get_wch()
            if key is not None:
                # Delegar procesamiento a input handlers
                self._input_handlers.handle_key_input(key)
        except curses.error:
            # No hay input disponible
            pass
    
    def _cleanup(self) -> None:
        """
        Limpia recursos al salir.
        """
        try:
            # Guardar configuración
            if self._context and self._context.has_service('data'):
                data_service = self._context.get_service('data')
                app_state = self._context.get_app_state()
                data_service.set_config_value('debug_mode', app_state.debug_mode)
                data_service.save_config()
            
            # Limpiar renderer
            if self._context:
                renderer = self._context.get_renderer()
                renderer.cleanup()
            
            # Restaurar pantalla de curses
            curses.endwin()
            
        except Exception:
            # Ignorar errores en cleanup
            pass


def main(stdscr) -> None:
    """
    Función main para curses.wrapper.
    
    Args:
        stdscr: Ventana principal de curses
    """
    try:
        # Crear y ejecutar aplicación
        app = TUIApp()
        app.initialize(stdscr)
        app.run()
        
    except Exception as e:
        # Manejar errores críticos
        curses.endwin()
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Ejecutar con curses.wrapper para manejo seguro de terminal
    curses.wrapper(main)