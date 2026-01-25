import time

class ClockService:
    """
    Servicio de clock para generar eventos temporales.
    
    Provee una fuente de ticks para el Message Loop
    y operaciones relacionadas con el tiempo.
    """
    
    def __init__(self, tick_interval: float = 0.01):
        self._tick_interval = tick_interval
        self._last_tick = 0
        self._start_time = time.time()
    
    def get_current_time(self) -> float:
        """
        Obtiene el tiempo actual.
        
        Returns:
            Timestamp actual
        """
        return time.time()
    
    def get_elapsed_time(self) -> float:
        """
        Obtiene el tiempo transcurrido desde el inicio.
        
        Returns:
            Tiempo transcurrido en segundos
        """
        return time.time() - self._start_time
    
    def should_tick(self) -> bool:
        """
        Verifica si es tiempo de generar un tick.
        
        Returns:
            True si es tiempo de tick
        """
        current_time = self.get_current_time()
        if current_time - self._last_tick >= self._tick_interval:
            self._last_tick = current_time
            return True
        return False
    
    def set_tick_interval(self, interval: float) -> None:
        """
        Establece el intervalo de ticks.
        
        Args:
            interval: Intervalo en segundos
        """
        self._tick_interval = max(0.001, interval)
    
    def reset_timer(self) -> None:
        """Resetea el timer de tiempo transcurrido."""
        self._start_time = time.time()
    
    def format_elapsed_time(self) -> str:
        """
        Formatea el tiempo transcurrido como string.
        
        Returns:
            String con formato MM:SS
        """
        elapsed = int(self.get_elapsed_time())
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_uptime_string(self) -> str:
        """
        Obtiene un string descriptivo del uptime.
        
        Returns:
            String con uptime formateado
        """
        elapsed = self.get_elapsed_time()
        
        if elapsed < 60:
            return f"{elapsed:.1f}s"
        elif elapsed < 3600:
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            return f"{hours}h {minutes}m"