import time
from typing import List, Optional
from queue import Queue, Empty
from .event_bus import EventBus
from .events import Event, EventType
from ..state.render_queue import RenderQueue

class MessageLoop:
    """
    Message Loop central que orquesta el ciclo de ejecución.
    
    Es el único componente que:
    - Orquesta el ciclo de ejecución (tick)
    - Decide cuándo se procesan eventos
    - Invoca handlers
    
    NO contiene lógica de negocio.
    """
    
    def __init__(self, event_bus: EventBus, render_queue: RenderQueue):
        self._event_bus = event_bus
        self._render_queue = render_queue
        self._message_queue: Queue[Event] = Queue()
        self._running = False
        self._tick_interval = 0.01  # 10ms default
        self._last_tick = 0
    
    def put_event(self, event: Event) -> None:
        """
        Encola un evento para ser procesado en el próximo tick.
        
        Args:
            event: Evento a procesar
        """
        self._message_queue.put(event)
    
    def start(self) -> None:
        """
        Inicia el message loop.
        Este método bloquea hasta que se llame a stop().
        """
        self._running = True
        self._last_tick = time.time()
        
        while self._running:
            self.tick()
    
    def stop(self) -> None:
        """
        Detiene el message loop de forma segura.
        """
        self._running = False
    
    def tick(self) -> None:
        """
        Ejecuta un ciclo completo del message loop:
        1. Obtiene eventos pendientes
        2. Consulta al EventBus qué handlers corresponden
        3. Ejecuta los handlers
        4. Decide si hay redraw
        """
        current_time = time.time()
        
        # Generar evento de tick si es necesario
        if current_time - self._last_tick >= self._tick_interval:
            from .events import TickEvent
            self.put_event(TickEvent(
                event_type=EventType.TICK,
                source="message_loop",
                payload={"timestamp": current_time},
                timestamp=current_time
            ))
            self._last_tick = current_time
        
        # Procesar todos los eventos pendientes
        events_processed = 0
        while events_processed < 100:  # Limitar para evitar bloqueos
            try:
                event = self._message_queue.get_nowait()
                self._process_event(event)
                events_processed += 1
            except Empty:
                break
        
        # Decidir si hay redraw
        if self._render_queue.has_pending_renders():
            self._trigger_render()
    
    def _process_event(self, event: Event) -> None:
        """
        Procesa un evento específico:
        - Busca handlers en el EventBus
        - Ejecuta todos los handlers correspondientes
        - Maneja errores de handlers individualmente
        """
        try:
            handlers = self._event_bus.get_handlers(event.event_type)
            
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    # Log error but continue processing other handlers
                    print(f"Error in handler for {event.event_type}: {e}")
                    
        except Exception as e:
            print(f"Error processing event {event.event_type}: {e}")
    
    def _trigger_render(self) -> None:
        """
        Dispara el renderizado de widgets pendientes.
        Este método separa el procesamiento de eventos del renderizado.
        """
        # El renderizador consumirá la RenderQueue
        # Esta implementación puede extenderse para scheduling más sofisticado
        pass
    
    def set_tick_interval(self, interval: float) -> None:
        """
        Configura el intervalo entre ticks.
        
        Args:
            interval: Intervalo en segundos (default: 0.01)
        """
        self._tick_interval = max(0.001, interval)  # Mínimo 1ms
    
    def get_queue_size(self) -> int:
        """
        Obtiene el número de eventos pendientes en la cola.
        
        Returns:
            Número de eventos en cola
        """
        return self._message_queue.qsize()
    
    def is_running(self) -> bool:
        """
        Verifica si el message loop está activo.
        
        Returns:
            True si está corriendo, False si está detenido
        """
        return self._running