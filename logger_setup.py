"""
Logging configuration.
Creates both file and console logging.
Every action is recorded with timestamp.
"""

import logging
from config import LOG_FILE


def setup_logger():
    """
    Set up logger that writes to both file and console.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger("MarketingCampaign")
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger
    
    # Format: timestamp - level - message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler — saves all logs to file
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler — shows logs in terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
