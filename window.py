from abc import ABC, abstractmethod

class Window(ABC):
  def __init__(self, stdscr = None):
    self.stdscr = stdscr

  def set_metadata (self, data):
    self.width = data['width']
    self.height = data['height']
    self.y_pos = data['y_pos']