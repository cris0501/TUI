
from datetime import datetime

class TitleVM:
    def __init__(self, app_name: str):
        self._app_name = app_name

    def title_text(self) -> str:
        # Derivación mínima; podrías inyectar un ThemeStore si quieres
        return f"{self._app_name} (MVVM demo)"
