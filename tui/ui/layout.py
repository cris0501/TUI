from typing import NamedTuple


class Rect(NamedTuple):
    y: int
    x: int
    h: int
    w: int


class Layout:
    def __init__(self):
        self._rects: dict[str, Rect] = {}

    def recalculate(self, H: int, W: int):
        title_h = 2
        prompt_h = 2
        footer_h = 1
        logs_h = max(1, H - (title_h + prompt_h + footer_h))

        self._rects = {
            "title": Rect(0, 0, title_h, W),
            "main_panel": Rect(title_h, 0, logs_h, W),
            "prompt": Rect(H - (prompt_h + footer_h), 0, prompt_h, W),
            "footer": Rect(H - footer_h, 0, footer_h, W),
        }

    def get_rect(self, widget_id: str) -> Rect:
        return self._rects[widget_id]

    def widget_ids(self) -> list[str]:
        return list(self._rects.keys())
