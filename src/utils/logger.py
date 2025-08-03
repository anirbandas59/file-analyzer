#!/usr/bin/env python3
# File: src/utils/logger.py

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class FileAnalyzerLogger:
    """
    Comprehensive logging system for the File Analyzer application.

    Features:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File rotation to prevent large log files
    - Console and file output
    - Performance tracking
    - Error tracking with context
    """

    _instance: Optional['FileAnalyzerLogger'] = None
    _logger: logging.Logger | None = None

    def __new__(cls) -> 'FileAnalyzerLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is not None:
            return  # Already initialized

        # Create logs directory
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Setup logger
        self._setup_logger()

        # Log startup
        self.info("FileAnalyzer logging system initialized")
        self.info(f"Log directory: {self.log_dir.absolute()}")

    def _setup_logger(self):
        """Setup the logger with file and console handlers."""
        self._logger = logging.getLogger("FileAnalyzer")
        self._logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self._logger.handlers:
            return

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s() | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # File handler with rotation (10MB max, keep 5 files)
        log_file = self.log_dir / f"fileanalyzer_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        # Console handler (only INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)

        # Error file handler for errors and critical issues
        error_log_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)

        # Add handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        self._logger.addHandler(error_handler)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, exception: Exception | None = None, **kwargs):
        """Log error message with optional exception."""
        if exception:
            self._logger.error(f"{message} | Exception: {exception}", exc_info=True, **kwargs)
        else:
            self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, exception: Exception | None = None, **kwargs):
        """Log critical message with optional exception."""
        if exception:
            self._logger.critical(f"{message} | Exception: {exception}", exc_info=True, **kwargs)
        else:
            self._log(logging.CRITICAL, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method."""
        if self._logger:
            self._logger.log(level, message, **kwargs)

    def log_performance(self, operation: str, duration: float, details: dict | None = None):
        """Log performance metrics."""
        msg = f"PERFORMANCE | {operation} | Duration: {duration:.3f}s"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            msg += f" | {detail_str}"
        self.info(msg)

    def log_file_operation(self, operation: str, path: str, success: bool = True,
                          details: dict | None = None):
        """Log file operations."""
        status = "SUCCESS" if success else "FAILED"
        msg = f"FILE_OP | {operation} | {status} | Path: {path}"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            msg += f" | {detail_str}"

        if success:
            self.info(msg)
        else:
            self.error(msg)

    def log_ui_action(self, action: str, component: str, details: dict | None = None):
        """Log UI interactions."""
        msg = f"UI_ACTION | {component} | {action}"
        if details:
            detail_str = " | ".join([f"{k}: {v}" for k, v in details.items()])
            msg += f" | {detail_str}"
        self.debug(msg)

    def log_memory_usage(self, component: str, memory_mb: float):
        """Log memory usage."""
        self.debug(f"MEMORY | {component} | {memory_mb:.2f} MB")

    def log_scan_results(self, path: str, file_count: int, total_size: int,
                        duration: float):
        """Log directory scan results."""
        from ..utils.file_utils import format_size
        self.info(
            f"SCAN_COMPLETE | Path: {path} | Files: {file_count} | "
            f"Size: {format_size(total_size)} | Duration: {duration:.3f}s"
        )

    def log_startup(self, version: str = "1.0.0"):
        """Log application startup."""
        self.info("=" * 80)
        self.info(f"File Analyzer v{version} - Application Starting")
        self.info(f"Python version: {sys.version}")
        self.info(f"Platform: {sys.platform}")
        self.info(f"Working directory: {os.getcwd()}")
        self.info("=" * 80)

    def log_shutdown(self):
        """Log application shutdown."""
        self.info("=" * 80)
        self.info("File Analyzer - Application Shutting Down")
        self.info("=" * 80)

    def get_log_files(self) -> list:
        """Get list of all log files."""
        if not self.log_dir.exists():
            return []
        return [f for f in self.log_dir.glob("*.log")]

    def cleanup_old_logs(self, days: int = 30):
        """Remove log files older than specified days."""
        if not self.log_dir.exists():
            return

        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        removed_count = 0

        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    removed_count += 1
                except Exception as e:
                    self.error(f"Failed to remove old log file {log_file}", e)

        if removed_count > 0:
            self.info(f"Cleaned up {removed_count} old log files")


# Global logger instance
logger = FileAnalyzerLogger()


# Convenience functions for easy access
def debug(message: str, **kwargs):
    """Log debug message."""
    logger.debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log info message."""
    logger.info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message."""
    logger.warning(message, **kwargs)


def error(message: str, exception: Exception | None = None, **kwargs):
    """Log error message."""
    logger.error(message, exception, **kwargs)


def critical(message: str, exception: Exception | None = None, **kwargs):
    """Log critical message."""
    logger.critical(message, exception, **kwargs)


def log_performance(operation: str, duration: float, details: dict | None = None):
    """Log performance metrics."""
    logger.log_performance(operation, duration, details)


def log_file_operation(operation: str, path: str, success: bool = True,
                      details: dict | None = None):
    """Log file operations."""
    logger.log_file_operation(operation, path, success, details)


def log_ui_action(action: str, component: str, details: dict | None = None):
    """Log UI interactions."""
    logger.log_ui_action(action, component, details)
