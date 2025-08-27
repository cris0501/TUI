import curses
from window import Window

class Footer (Window):
  def __init__(self, stdscr = None):
    super().__init__(stdscr)

  def set_content (self, data):
    self.data = data
  
  def _draw_(self):
    # 2 líneas de footer con menú (F1..F9); separador arriba
    self.stdscr.hline(self.y_pos, 0, curses.ACS_HLINE, self.width)
    labels = [f"[F{i+1}] {item.get('title','')}" for i, item in enumerate(self.data[:9])]
    # Particiona labels en dos líneas respetando ancho
    line1, line2 = "", ""
    for lab in labels:
        if not line1 or len(line1) + len(lab) + 2 <= self.width - 2: # Empty label or len string
            line1 = (lab if not line1 else line1 + "  " + lab)
        elif not line2 or len(line2) + len(lab) + 2 <= self.width - 2:
            line2 = (lab if not line2 else line2 + "  " + lab)
        else:
            # Si tampoco cabe en line2, recorta y añade "…"
            if len(line2) < self.width - 3:
                line2 = line2[:max(0, self.width - 5)] + "…"
            break
    self.stdscr.addnstr(self.y_pos + 1, 1, line1, self.width - 2, curses.A_BOLD)
    self.stdscr.addnstr(self.y_pos + 2, 1, line2, self.width - 2, curses.A_BOLD)