"""
Logging configuration
"""

import logging
from loguru import logger as loguru_logger
import sys


def setup_logging():
    """Setup logging configuration"""
    
    # Remove default handler
    logging.getLogger().handlers = []
    
    # Configure loguru
    loguru_logger.remove()
    loguru_logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Add file logging
    loguru_logger.add(
        "logs/weather_api.log",
        format="{time} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="500 MB"
    )
    
    # Return standard logger
    return logging.getLogger(__name__)
