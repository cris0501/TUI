import curses
from window import Window

class Promp (Window):
  def __init__(self, stdscr = None):
    super().__init__(stdscr)

  def _draw_(self, data):
    # Línea de prompt (una línea), resaltada
    self.stdscr.move(self.y_pos, 0)
    self.stdscr.clrtoeol()
    prompt = f"> {data}"
    self.stdscr.addnstr(self.y_pos, 0, prompt[-(self.width-1):], self.width, curses.A_REVERSE)