import logging
import os

class DualHandler(logging.Handler):
    """Custom logging handler that outputs to both the console and optionally the log file with color in console output."""

    def __init__(self, log_dir=None, prefix='', suffix='', percentage=None):
        super().__init__()

        # Set up the logging attribute
        self.logger = logging.getLogger(__name__)

        # Optional file handler (only if log_dir is provided)
        self.file_handler = None
        if log_dir:
            if prefix == suffix == '':
                prefix = 'log'
            if percentage:
                suffix += f'{percentage * 100:.0f}'
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'{prefix}{suffix}.log')
            self.file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')

        # Console handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.stream = open(self.console_handler.stream.fileno(), mode='w', encoding='utf-8', buffering=1)

        # Set logging level and format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        if self.file_handler:
            self.file_handler.setFormatter(formatter)
        self.console_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.handlers = []
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self)

    def emit(self, record):
        """Emit log records to console, and to file if file logging is enabled."""
        # Emit to file handler (if enabled)
        if self.file_handler:
            self.file_handler.emit(record)
        # Emit to console handler
        self.console_handler.emit(record)

    def log_info(self, msg):
        self.logger.info(msg)

    def log_warning(self, msg):
        self.logger.warning(msg)

    def log_error(self, msg):
        self.logger.error(msg)

    def log_debug(self, msg):
        self.logger.debug(msg)
