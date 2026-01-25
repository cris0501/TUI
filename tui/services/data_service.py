from typing import Dict, Any, Optional, List
import json
import os

class DataService:
    """
    Servicio para operaciones de datos externas.
    
    Maneja persistencia, carga de configuración,
    y operaciones con archivos o APIs externas.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self._config_file = config_file or "tui_config.json"
        self._data: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carga configuración desde archivo.
        
        Returns:
            Diccionario con configuración cargada
        """
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    self._config = json.load(f)
            else:
                self._config = self._get_default_config()
                self.save_config()
        except Exception as e:
            self._config = self._get_default_config()
        
        return self._config.copy()
    
    def save_config(self) -> bool:
        """
        Guarda configuración actual a archivo.
        
        Returns:
            True si se guardó exitosamente, False si no
        """
        try:
            with open(self._config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception:
            return False
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración.
        
        Args:
            key: Clave de configuración
            default: Valor por defecto
            
        Returns:
            Valor de configuración o default
        """
        return self._config.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> None:
        """
        Establece un valor de configuración.
        
        Args:
            key: Clave de configuración
            value: Valor a establecer
        """
        self._config[key] = value
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Obtiene toda la configuración.
        
        Returns:
            Diccionario completo de configuración
        """
        return self._config.copy()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración por defecto.
        
        Returns:
            Diccionario con configuración por defecto
        """
        return {
            "tick_interval": 0.01,
            "max_log_lines": 500,
            "prompt_max_length": 256,
            "title_height": 1,
            "footer_height": 1,
            "prompt_height": 2,
            "min_width": 20,
            "min_height": 10,
            "add_timestamps": False,
            "auto_save_config": True,
            "debug_mode": False,
            "theme": "default"
        }
    
    def save_logs_to_file(self, lines: List[str], filename: Optional[str] = None) -> bool:
        """
        Guarda líneas de logs a archivo.
        
        Args:
            lines: Líneas a guardar
            filename: Nombre de archivo (opcional)
            
        Returns:
            True si se guardó exitosamente, False si no
        """
        if filename is None:
            timestamp = self._get_timestamp()
            filename = f"tui_logs_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for line in lines:
                    f.write(line + '\n')
            return True
        except Exception:
            return False
    
    def load_logs_from_file(self, filename: str) -> List[str]:
        """
        Carga líneas de logs desde archivo.
        
        Args:
            filename: Nombre de archivo
            
        Returns:
            Lista de líneas cargadas
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return [line.rstrip('\n') for line in f.readlines()]
        except Exception:
            return []
    
    def save_app_state(self, state_data: Dict[str, Any], filename: Optional[str] = None) -> bool:
        """
        Guarda estado de la aplicación a archivo.
        
        Args:
            state_data: Datos del estado a guardar
            filename: Nombre de archivo (opcional)
            
        Returns:
            True si se guardó exitosamente, False si no
        """
        if filename is None:
            timestamp = self._get_timestamp()
            filename = f"tui_state_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            return True
        except Exception:
            return False
    
    def load_app_state(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Carga estado de la aplicación desde archivo.
        
        Args:
            filename: Nombre de archivo
            
        Returns:
            Diccionario con estado cargado o None si falla
        """
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_data_directory(self) -> str:
        """
        Obtiene el directorio de datos de la aplicación.
        
        Returns:
            Ruta al directorio de datos
        """
        return os.path.dirname(os.path.abspath(self._config_file))
    
    def list_saved_states(self) -> List[str]:
        """
        Lista todos los archivos de estado guardados.
        
        Returns:
            Lista de nombres de archivo
        """
        try:
            directory = self.get_data_directory()
            files = []
            for file in os.listdir(directory):
                if file.startswith('tui_state_') and file.endswith('.json'):
                    files.append(file)
            return sorted(files)
        except Exception:
            return []
    
    def list_saved_logs(self) -> List[str]:
        """
        Lista todos los archivos de logs guardados.
        
        Returns:
            Lista de nombres de archivo
        """
        try:
            directory = self.get_data_directory()
            files = []
            for file in os.listdir(directory):
                if file.startswith('tui_logs_') and file.endswith('.txt'):
                    files.append(file)
            return sorted(files)
        except Exception:
            return []
    
    def _get_timestamp(self) -> str:
        """
        Obtiene timestamp formateado para nombres de archivo.
        
        Returns:
            String con timestamp
        """
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def cleanup_old_files(self, max_files: int = 10) -> None:
        """
        Limpia archivos antiguos manteniendo solo los más recientes.
        
        Args:
            max_files: Número máximo de archivos a mantener
        """
        try:
            # Limpiar estados antiguos
            states = self.list_saved_states()
            if len(states) > max_files:
                for old_file in states[:-max_files]:
                    os.remove(os.path.join(self.get_data_directory(), old_file))
            
            # Limpiar logs antiguos
            logs = self.list_saved_logs()
            if len(logs) > max_files:
                for old_file in logs[:-max_files]:
                    os.remove(os.path.join(self.get_data_directory(), old_file))
                    
        except Exception:
            pass