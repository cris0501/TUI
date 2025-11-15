from core.store import PromptStore
from core.redraw import RedrawManager
from utils import Logger

class PromptVM:
    def __init__(self, store: PromptStore, redraw: RedrawManager):
        self.cursor_idx = 0
        self._redraw = redraw
        self.logger = Logger()
        self.store = store
        self.text = store.text
        store.subscribe(self._on_event)

    def _on_event(self, evt: dict):
        if evt.get("type") == "textChanged":
            self.text = self.store.text
            self._redraw.invalidate("promp")

    def submit(self):
        self.logger.info(f"Submit event {self.text}")
        self.store.set_text("")
        self.cursor_idx = 0
        self._redraw.invalidate("prompt")

    def move_to_start(self):
        self.cursor_idx = 0

    def move_to_end(self):
        self.cursor_idx = len(self.text)

    def insert_char(self, char):
        # left + char + right
        lhs = self.text[:self.cursor_idx]
        rhs = self.text[self.cursor_idx:]
        self.store.set_text(lhs + char + rhs)
        self.cursor_idx += 1
        self._redraw.invalidate("prompt")

    def move_cursor_left(self):
        if self.cursor_idx > 0:
            self.cursor_idx -= 1

    def move_cursor_right(self):
        if self.cursor_idx < len(self.text):
            self.cursor_idx += 1

    def backspace(self):
        """
        ----------- [] cursor ------
        left - 1  / [] / right
        """
        if self.cursor_idx > 0:
            lhs = self.text[:self.cursor_idx - 1]
            rhs = self.text[self.cursor_idx:]
            self.store.set_text(lhs + rhs)
            self.cursor_idx -= 1
            self._redraw.invalidate("prompt")

    def delete_under_cursor(self):
        """
        ------- [cursor] ------
        left / [] / 1 + right
        """
        if self.cursor_idx < len(self.text):
            lhs = self.text[:self.cursor_idx]
            rhs = self.text[self.cursor_idx + 1:]
            self.store.set_text(lhs + rhs)
            self._redraw.invalidate("prompt")