import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime

# Create logs directory if it doesn't exist
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
LOG_FILE = LOGS_DIR / "app.log"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"

def setup_logging():
    """Configure logging for the application - Laravel style"""
    
    # Create formatters - Laravel-like format
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs (INFO and above) - like Laravel's app.log
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (ERROR and above only) - like Laravel's error log
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)  # Reduce uvicorn noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Reduce access log noise
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # Reduce SQL log noise
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)  # Reduce SQL pool noise
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)
