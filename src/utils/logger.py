import logging
import sys
from rich.logging import RichHandler
from rich.console import Console

def setup_logger(name: str = "multimodal_researcher", level: str = "INFO") -> logging.Logger:
    """Setup a beautiful logger with Rich formatting"""
    
    # Create console for Rich
    console = Console()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create Rich handler
    handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_path=False,
        show_time=True
    )
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(message)s",
        datefmt="[%X]"
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger