"""
Logging module for gerbyx with performance optimization.

Uses lazy evaluation to avoid string formatting overhead when debug is disabled.
"""
import logging
import functools
from typing import Any, Callable

# Configure logger
logger = logging.getLogger('gerbyx')
logger.setLevel(logging.INFO)

# Create console handler with formatter
_handler = logging.StreamHandler()
_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
_handler.setFormatter(_formatter)
logger.addHandler(_handler)


def set_level(level: str):
    """Set logging level: 'DEBUG', 'INFO', 'WARNING', 'ERROR'"""
    logger.setLevel(getattr(logging, level.upper()))


def is_debug_enabled() -> bool:
    """Check if debug logging is enabled (for performance optimization)"""
    return logger.isEnabledFor(logging.DEBUG)


# Lazy logging decorators for performance
def debug(msg_func: Callable[[], str]):
    """
    Lazy debug logging - only evaluates message if debug is enabled.
    
    Usage:
        debug(lambda: f"Processing {len(items)} items")
    """
    if is_debug_enabled():
        logger.debug(msg_func())


def info(msg: str):
    """Info level logging"""
    logger.info(msg)


def warning(msg: str):
    """Warning level logging"""
    logger.warning(msg)


def error(msg: str):
    """Error level logging"""
    logger.error(msg)


# Performance-optimized logging context
class LogContext:
    """Context manager for scoped logging with timing"""
    def __init__(self, operation: str, level: str = 'DEBUG'):
        self.operation = operation
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        if self.level == 'DEBUG' and not is_debug_enabled():
            return self
        
        import time
        self.start_time = time.perf_counter()
        
        if self.level == 'DEBUG':
            logger.debug(f"Starting: {self.operation}")
        else:
            logger.info(f"Starting: {self.operation}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is None:
            return
        
        import time
        elapsed = (time.perf_counter() - self.start_time) * 1000
        
        if exc_type:
            logger.error(f"Failed: {self.operation} ({elapsed:.2f}ms) - {exc_val}")
        elif self.level == 'DEBUG':
            logger.debug(f"Completed: {self.operation} ({elapsed:.2f}ms)")
        else:
            logger.info(f"Completed: {self.operation} ({elapsed:.2f}ms)")


def log_performance(func):
    """
    Decorator to log function performance (DEBUG level only).
    Zero overhead when debug is disabled.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not is_debug_enabled():
            return func(*args, **kwargs)
        
        import time
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        
        logger.debug(f"{func.__name__}() took {elapsed:.2f}ms")
        return result
    
    return wrapper
