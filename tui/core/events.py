from dataclasses import dataclass
from typing import Optional, Dict, Any, Union
from enum import Enum

class EventType(Enum):
    # Input events
    KEY_PRESS = "key_press"
    MOUSE_CLICK = "mouse_click"
    
    # State mutation events
    PROMPT_TEXT_CHANGED = "prompt_text_changed"
    LOGS_APPEND = "logs_append"
    FOOTER_ACTION = "footer_action"
    
    # UI events
    RESIZE = "resize"
    RENDER_REQUEST = "render_request"
    
    # System events
    TICK = "tick"
    SHUTDOWN = "shutdown"

@dataclass(frozen=True)
class BaseEvent:
    event_type: EventType
    source: str
    payload: Dict[str, Any]

@dataclass(frozen=True)
class KeyPressEvent(BaseEvent):
    key: Union[str, int]  # char or curses key code
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.KEY_PRESS)

@dataclass(frozen=True)
class MouseClickEvent(BaseEvent):
    x: int
    y: int
    button: int
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.MOUSE_CLICK)

@dataclass(frozen=True)
class PromptTextChangedEvent(BaseEvent):
    text: str
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.PROMPT_TEXT_CHANGED)

@dataclass(frozen=True)
class LogsAppendEvent(BaseEvent):
    line: str
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.LOGS_APPEND)

@dataclass(frozen=True)
class FooterActionEvent(BaseEvent):
    action: str
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.FOOTER_ACTION)

@dataclass(frozen=True)
class ResizeEvent(BaseEvent):
    height: int
    width: int
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.RESIZE)

@dataclass(frozen=True)
class RenderRequestEvent(BaseEvent):
    widget_id: str
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.RENDER_REQUEST)

@dataclass(frozen=True)
class TickEvent(BaseEvent):
    timestamp: float
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.TICK)

@dataclass(frozen=True)
class ShutdownEvent(BaseEvent):
    reason: Optional[str] = None
    
    def __post_init__(self):
        object.__setattr__(self, 'event_type', EventType.SHUTDOWN)

# Type aliases for easier usage
Event = Union[
    KeyPressEvent,
    MouseClickEvent,
    PromptTextChangedEvent,
    LogsAppendEvent,
    FooterActionEvent,
    ResizeEvent,
    RenderRequestEvent,
    TickEvent,
    ShutdownEvent
]