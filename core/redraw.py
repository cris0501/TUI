import curses
from typing import Dict, Set

class RedrawManager:
    def __init__(self):
        self._dirty: Set[str] = set()
        self._views: Dict[str, object] = {} # Controller
        self._wins: Dict[str, object] = {} # Space in term
        self._layout = None
        self._vms: Dict[str, object] = {}

    def bind(self, view_id: str, win, view, vm):
        self._views[view_id] = view
        self._wins[view_id] = win
        self._vms[view_id] = vm
        self.invalidate(view_id)

    def set_layout(self, layout):
        self._layout = layout

    def invalidate(self, view_id: str):
        self._dirty.add(view_id)

    def invalidate_all(self):
        self._dirty.update(self._views.keys())

    def flush(self):
        if not self._dirty:
            return
        for vid in list(self._dirty):
            view = self._views.get(vid)
            win = self._wins.get(vid)
            vm = self._vms.get(vid)
            if view and win and vm:
                try:
                    view.draw(win, self._layout, vm)
                except Exception as e:
                    print(f"Error redraw ${view}")
                    pass
        self._dirty.clear()
        curses.doupdate()
