import logging
from .clients.sync_client import Chapa
from .clients.async_client import AsyncChapa


def enable_logging(level: str = "INFO") -> None:
    """
    Enable logging for the pychapa library.
    
    Args:
        level (str): The logging level. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


__all__ = ["Chapa", "AsyncChapa", "enable_logging"]
