import curses
from window import Window

class Logs (Window):
  def __init__(self, stdscr = None):
    super().__init__(stdscr)

  def _draw_(self, lines, scroll):
    viewport = max(0, self.height - 1)
    start = max(0, len(lines) - viewport - scroll) # line to begin enumerate
    end   = len(lines) - scroll if scroll == 0 else len(lines) - scroll
    view  = lines[start:end]
    y = self.y_pos # position of cursor
    for line in view:
        # Cortar por ancho
        for chunk_start in range(0, len(line), self.width):
            if y >= self.y_pos + viewport: break # Cursor exed limit of viewport
            chunk = line[chunk_start:chunk_start + self.width] # cut text overview
            self.stdscr.move(y, 0); self.stdscr.clrtoeol()
            self.stdscr.addnstr(y, 0, chunk, self.width)
            y += 1
        if y >= self.y_pos + viewport: break