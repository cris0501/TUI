from __future__ import annotations

from typing import Dict

from textual.message import Message


class LogAppendEvent(Message):
    def __init__(self, line: str) -> None:
        super().__init__()
        self.line = line


class UpdateStatus(Message):
    def __init__(self, status: str) -> None:
        super().__init__()
        self.status = status


class ActionEvent(Message):
    def __init__(self, key: str) -> None:
        super().__init__()
        self.key = key


class UpdateLinksEvent(Message):
    def __init__(self, links: Dict[str, str]) -> None:
        super().__init__()
        self.links = links

class ExecAction(Message):
    def __init__(self, action: Dict[str, str]) -> None:
        super().__init__()
        self.kind = action.get("kind", "")
        self.type = action.get("type", "information")
        self.title = action.get("title", "")
        self.body = action.get("body", "")

class UpdateSystemActionsEvent(Message):
    def __init__(self, system_actions: Dict[str, str]) -> None:
        super().__init__()
        self.system_actions = system_actions


class StartSocketEvent(Message):
    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.host = host
        self.port = port

class StopSocketEvent(Message):
    def __init__(self) -> None:
        super().__init__()
        pass


class TickEvent(Message):
    def __init__(self, tick: int) -> None:
        super().__init__()
        self.tick = tick

