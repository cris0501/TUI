class AppState:
    def __init__(self):
        self.app_name: str = "TUI"
        self.status: str = "IDLE"
        self.prompt_text: str = ""
        self.cursor_idx: int = 0
        self.log_lines: list[str] = []
        self.max_log_lines: int = 500
        self.actions: dict[str, str] = {
            "F1": "Update",
            "F2": "Add",
            "F3": "Test",
        }
        self.running: bool = True
        self.tick: int = 0

    def append_log(self, line: str):
        self.log_lines.append(line)
        if len(self.log_lines) > self.max_log_lines:
            self.log_lines = self.log_lines[-self.max_log_lines:]
