import curses
from window import Window

class Title (Window):
  def __init__(self, stdscr = None):
    super().__init__(stdscr)
  
  def set_project (self, name):
    self.project = name
  
  def set_status (self, status):
    self.status = status

  def _draw_(self):
    self.stdscr.move(0, 0)
    self.stdscr.clrtoeol()
    left = f"{self.project}"
    right = f"{self.status}"
    self.stdscr.addnstr(0, 0, left, max(0, self.width - 1), curses.A_BOLD)
    self.stdscr.addnstr(0, max(0, self.width - len(right) - 1), right, len(right), curses.A_DIM)