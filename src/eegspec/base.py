from dataclasses import dataclass, field
from .vendor.dualhandler import DualHandler
import logging

@dataclass
class BaseApp:
    """Base app wrapper installing DualHandler for consistent logging."""
    log_level: str = "INFO"
    log_dir: str = None
    log_prefix: str = ""
    log_suffix: str = ""
    log_percentage: float = None
    logger: logging.Logger = field(init=False)

    def __post_init__(self):
        self._dh = DualHandler(log_dir=self.log_dir, prefix=self.log_prefix, suffix=self.log_suffix, percentage=self.log_percentage)
        self.logger = self._dh.logger
        self.logger.setLevel(getattr(logging, self.log_level.upper(), logging.INFO))
        self.logger.debug("Logger initialized")
