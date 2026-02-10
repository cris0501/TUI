import curses
from abc import ABC, abstractmethod

from tui.ui.layout import Rect
from tui.state.app_state import AppState


class Widget(ABC):
    @property
    @abstractmethod
    def widget_id(self) -> str: ...

    @abstractmethod
    def draw(self, win: curses.window, rect: Rect, state: AppState) -> None: ...
