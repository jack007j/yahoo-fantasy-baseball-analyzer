"""
Logging configuration for the Yahoo Fantasy Baseball application.
"""

import logging
import logging.handlers
import sys
from typing import Optional
from pathlib import Path

from .config import get_config
from .constants import LOG_FORMAT, LOG_DATE_FORMAT


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level override
        log_file: Optional log file path
        enable_console: Whether to enable console logging
    """
    try:
        # Get configuration
        config = get_config()
        logging_config = config.logging_config
        
        # Use provided level or config level
        level = log_level or logging_config.level
        log_format = logging_config.format
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            fmt=log_format,
            datefmt=LOG_DATE_FORMAT
        )
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper()))
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            try:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5
                )
                file_handler.setLevel(getattr(logging, level.upper()))
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
                
            except Exception as e:
                print(f"Warning: Could not set up file logging: {e}")
        
        # Configure third-party loggers
        _configure_third_party_loggers()
        
        # Log configuration success
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured: level={level}, console={enable_console}, file={log_file}")
        
    except Exception as e:
        # Fallback to basic configuration
        logging.basicConfig(
            level=logging.INFO,
            format=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT
        )
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to configure logging: {e}")


def _configure_third_party_loggers() -> None:
    """Configure logging levels for third-party libraries."""
    # Reduce noise from third-party libraries
    third_party_loggers = {
        'requests': logging.WARNING,
        'urllib3': logging.WARNING,
        'streamlit': logging.WARNING,
        'yahoo_oauth': logging.WARNING,
        'yahoo_fantasy_api': logging.INFO,
        'matplotlib': logging.WARNING,
        'PIL': logging.WARNING
    }
    
    for logger_name, level in third_party_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None) -> None:
    """
    Log function call with parameters.
    
    Args:
        func_name: Function name
        args: Function arguments
        kwargs: Function keyword arguments
    """
    logger = logging.getLogger('function_calls')
    
    if logger.isEnabledFor(logging.DEBUG):
        args_str = ', '.join(str(arg) for arg in args) if args else ''
        kwargs_str = ', '.join(f'{k}={v}' for k, v in (kwargs or {}).items())
        
        params = ', '.join(filter(None, [args_str, kwargs_str]))
        logger.debug(f"Calling {func_name}({params})")


def log_api_request(method: str, url: str, status_code: int, duration: float) -> None:
    """
    Log API request details.
    
    Args:
        method: HTTP method
        url: Request URL
        status_code: Response status code
        duration: Request duration in seconds
    """
    logger = logging.getLogger('api_requests')
    
    level = logging.INFO
    if status_code >= 400:
        level = logging.WARNING
    if status_code >= 500:
        level = logging.ERROR
    
    logger.log(
        level,
        f"{method} {url} -> {status_code} ({duration:.2f}s)"
    )


def log_cache_operation(operation: str, key: str, hit: bool = None) -> None:
    """
    Log cache operation.
    
    Args:
        operation: Cache operation (get, set, delete, clear)
        key: Cache key
        hit: Whether cache hit occurred (for get operations)
    """
    logger = logging.getLogger('cache_operations')
    
    if operation == 'get' and hit is not None:
        result = 'HIT' if hit else 'MISS'
        logger.debug(f"Cache {operation}: {key} -> {result}")
    else:
        logger.debug(f"Cache {operation}: {key}")


def log_analysis_step(step: str, details: str = None) -> None:
    """
    Log analysis step.
    
    Args:
        step: Analysis step name
        details: Optional step details
    """
    logger = logging.getLogger('analysis')
    
    message = f"Analysis step: {step}"
    if details:
        message += f" - {details}"
    
    logger.info(message)


def log_error_with_context(error: Exception, context: dict = None) -> None:
    """
    Log error with additional context.
    
    Args:
        error: Exception that occurred
        context: Additional context information
    """
    logger = logging.getLogger('errors')
    
    error_msg = f"Error: {type(error).__name__}: {str(error)}"
    
    if context:
        context_str = ', '.join(f'{k}={v}' for k, v in context.items())
        error_msg += f" | Context: {context_str}"
    
    logger.error(error_msg, exc_info=True)


class StructuredLogger:
    """
    Structured logger for consistent logging across the application.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with structured data."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with structured data."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with structured data."""
        self._log(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with structured data."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal logging method with structured data."""
        if kwargs:
            structured_data = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
            full_message = f"{message} | {structured_data}"
        else:
            full_message = message
        
        self.logger.log(level, full_message)


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


# Performance logging decorator
def log_performance(func):
    """
    Decorator to log function performance.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('performance')
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    return wrapper