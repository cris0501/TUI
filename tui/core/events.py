from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class Event:
    pass


# --- Raw input events ---

@dataclass(frozen=True)
class KeyEvent(Event):
    key: str | int


@dataclass(frozen=True)
class ResizeEvent(Event):
    height: int
    width: int


@dataclass(frozen=True)
class TickEvent(Event):
    tick: int


@dataclass(frozen=True)
class UpdateActionsEvent(Event):
    actions: Dict[str, str]


@dataclass(frozen=True)
class UpdateStatus(Event):
    status: str


@dataclass(frozen=True)
class StartSocketEvent(Event):
    host: str
    port: int

# --- Semantic events (translated by input_handlers) ---

@dataclass(frozen=True)
class InsertCharEvent(Event):
    char: str


@dataclass(frozen=True)
class BackspaceEvent(Event):
    pass


@dataclass(frozen=True)
class DeleteEvent(Event):
    pass


@dataclass(frozen=True)
class CursorMoveEvent(Event):
    direction: str  # "left" | "right" | "home" | "end"


@dataclass(frozen=True)
class SubmitEvent(Event):
    text: str


@dataclass(frozen=True)
class ActionEvent(Event):
    key: str  # "F1" | "F2" | ...


@dataclass(frozen=True)
class QuitEvent(Event):
    pass


@dataclass(frozen=True)
class LogAppendEvent(Event):
    line: str
