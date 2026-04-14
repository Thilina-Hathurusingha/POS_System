"""
Logging Configuration Module
Provides centralized logging setup with three levels: ERROR, WARNING, DEBUG
Supports colored output for better readability
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

# ========== Log Level Constants ==========
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_DEBUG = "DEBUG"

# ========== Color Codes for Terminal Output ==========
class ColorCodes:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'           # Error
    YELLOW = '\033[93m'        # Warning
    CYAN = '\033[96m'          # Debug
    GREEN = '\033[92m'         # Info
    GRAY = '\033[90m'          # Timestamp


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for different log levels"""
    
    COLORS = {
        'DEBUG': ColorCodes.CYAN,
        'INFO': ColorCodes.GREEN,
        'WARNING': ColorCodes.YELLOW,
        'ERROR': ColorCodes.RED,
        'CRITICAL': ColorCodes.RED + ColorCodes.BOLD,
    }
    
    def format(self, record):
        """Format log record with colors"""
        # Get the color for this log level
        levelname = record.levelname
        if levelname in self.COLORS:
            # Add color to level name
            record.levelname = f"{self.COLORS[levelname]}{levelname}{ColorCodes.RESET}"
        
        # Format the message
        formatted = super().format(record)
        return formatted


class AppLogger:
    """
    Centralized Logger class for the POS application
    Manages logging configuration and provides easy access to logger instances
    """
    
    _loggers = {}  # Cache for logger instances
    _log_level = LOG_LEVEL_ERROR  # Default log level
    _console_handler = None
    _file_handler = None
    _initialized = False
    
    @classmethod
    def setup(cls, log_level=LOG_LEVEL_ERROR, log_file=None):
        """
        Setup logging configuration for the application
        
        Args:
            log_level: One of 'ERROR', 'WARNING', 'DEBUG' (default: 'ERROR')
            log_file: Optional file path to save logs (default: None - console only)
        """
        # ========== Validate and Set Log Level ==========
        if log_level not in [LOG_LEVEL_ERROR, LOG_LEVEL_WARNING, LOG_LEVEL_DEBUG]:
            raise ValueError(f"Invalid log level: {log_level}. Must be ERROR, WARNING, or DEBUG")
        
        cls._log_level = log_level
        
        # Convert string level to logging module level
        level_map = {
            LOG_LEVEL_ERROR: logging.ERROR,
            LOG_LEVEL_WARNING: logging.WARNING,
            LOG_LEVEL_DEBUG: logging.DEBUG,
        }
        numeric_level = level_map[log_level]
        
        # ========== Create Root Logger ==========
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # ========== Remove Existing Handlers ==========
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # ========== Console Handler (Stdout) ==========
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        
        # Use colored formatter for console output
        console_formatter = ColoredFormatter(
            fmt=f'{ColorCodes.GRAY}[%(asctime)s]{ColorCodes.RESET} [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        cls._console_handler = console_handler
        
        # ========== File Handler (Optional) ==========
        if log_file:
            try:
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=5*1024*1024,  # 5 MB max file size
                    backupCount=5  # Keep 5 backup files
                )
                file_handler.setLevel(numeric_level)
                
                # Use plain formatter for file output (no colors)
                file_formatter = logging.Formatter(
                    fmt='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                root_logger.addHandler(file_handler)
                
                cls._file_handler = file_handler
            except Exception as e:
                console_handler.handle(logging.LogRecord(
                    'AppLogger', logging.ERROR, '', 0,
                    f'Failed to setup file logging: {e}', (), None
                ))
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name):
        """
        Get or create a logger instance
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        # ========== Initialize if Not Already Done ==========
        if not cls._initialized:
            cls.setup(log_file='log/app.log')  # Use current log level for setup
        
        # ========== Check Cache ==========
        if name not in cls._loggers:
            # Create and cache new logger
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def set_level(cls, log_level):
        """
        Change log level at runtime
        
        Args:
            log_level: One of 'ERROR', 'WARNING', 'DEBUG'
        """
        if log_level not in [LOG_LEVEL_ERROR, LOG_LEVEL_WARNING, LOG_LEVEL_DEBUG]:
            raise ValueError(f"Invalid log level: {log_level}")
        
        level_map = {
            LOG_LEVEL_ERROR: logging.ERROR,
            LOG_LEVEL_WARNING: logging.WARNING,
            LOG_LEVEL_DEBUG: logging.DEBUG,
        }
        numeric_level = level_map[log_level]
        
        # Update root logger and all handlers
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        for handler in root_logger.handlers:
            handler.setLevel(numeric_level)
        
        cls._log_level = log_level


# ========== Convenience Function for Module Usage ==========
def get_logger(name):
    """Convenience function to get logger instances"""
    return AppLogger.get_logger(name)
