from utils import Logger

class LogService ():
    def __init__(self):
        self.logger = Logger()

    def register_event (self, msg):
        self.logger.info(f"{msg}")