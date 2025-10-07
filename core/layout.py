from typing import Callable, Dict, Tuple, List, NamedTuple

class Rect(NamedTuple):
    y: int
    x: int
    h: int
    w: int

class LayoutService:
    def __init__(self):
        self._rects: Dict[str, Rect] = {}
        self._subs: List[Callable[[Dict[str, Rect]], None]] = [] # [ fn(dicc) -> none, fn(...) ]

    def get_rect(self, view_id: str) -> Rect:
        return self._rects[view_id]

    def subscribe(self, cb: Callable[[Dict[str, Rect]], None]): # fn(dicc) -> none
        self._subs.append(cb)
        if self._rects:
            cb(dict(self._rects))

    def _notify(self):
        snap = dict(self._rects)
        for cb in list(self._subs):
            cb(snap)

    def on_resize(self, H: int, W: int):
        # Layout vertical simple:
        # ┌ title (1) ┐
        # ├ logs (H-4)┤
        # ├ prompt (1)┤
        # ├-----------┤
        # └ footer (2)┘
        title_h = 1
        prompt_h = 1
        footer_h = 2
        logs_h = max(1, H - (title_h + prompt_h + footer_h))
        self._rects = {
            "title": Rect(0, 0, title_h, W),
            "logs": Rect(1, 0, logs_h-1 if logs_h>1 else 1, W),
            "prompt": Rect(H - (prompt_h + footer_h), 0, prompt_h, W),
            "footer": Rect(H - footer_h, 0, footer_h, W),
        }
        self._notify()
