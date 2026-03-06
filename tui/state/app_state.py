from enum import Enum, auto


class PromptMode(Enum):
    NORMAL = auto()
    AWAITING_IP = auto()
    AWAITING_PORT = auto()


class AppState:
    def __init__(self):
        self.app_name: str = "TUI"
        self.status: str = "IDLE"
        self.log_lines: list[str] = []
        self.max_log_lines: int = 500
        self.actions: dict[str, str] = {
            "F1": "Update",
            "F2": "Add",
            "F3": "Test",
        }
        self.system_actions: dict[str, str] = {}
        self.prompt_mode = PromptMode.NORMAL
        self.temp_ip = "127.0.0.1"
        self.temp_port = 5000

    def append_log(self, line: str):
        self.log_lines.append(line)
        if len(self.log_lines) > self.max_log_lines:
            self.log_lines = self.log_lines[-self.max_log_lines:]
