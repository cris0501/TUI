from abc import ABC, abstractmethod

class Window(ABC):
  def __init__(self, height = None, width = None, y_pos = None, stdsrc = None):
    self.width = width
    self.height = height
    self.y_pos = y_pos
    self.data = None
    self.stdsrc = stdsrc

  def set_metadata (self, data):
    self.width = data['width']
    self.height = data['height']
    self.y_pos = data['y_pos']
    self.stdsrc = data['stdsrc']