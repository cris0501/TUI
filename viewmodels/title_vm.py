from datetime import datetime

class TitleVM:
    def __init__(self, app_name: str):
        self._app_name = app_name
        self._status = "IDLE"

    def title(self) -> str:
        return f"{self._app_name} (MVVM demo)"
    
    def status(self) -> str:
        return self._status
