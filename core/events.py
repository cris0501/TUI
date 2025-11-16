from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class StoreEvent:
    source: str
    type: str
    payload: dict

ResizeEvent = StoreEvent  # alias semántico
