import logging
import traceback

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        self._logger = logging.getLogger("Debug_Logger")
        self._logger.setLevel(logging.DEBUG)

        if not self._logger.handlers:
            file_handler = logging.FileHandler('debug.log')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)

            self._logger.addHandler(file_handler)

    def info(self, message):
        self._logger.info(message)

    def warning(self, message):
        self._logger.warning(message)

    def error(self, message, exc_info=False):
        if exc_info:
            self._logger.error(message, exc_info=True)
        else:
            self._logger.error(message)
