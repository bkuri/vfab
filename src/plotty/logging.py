"""
Comprehensive logging configuration for ploTTY.

This module provides structured logging with configurable levels, output destinations,
log rotation, and integration with the ploTTY error handling system.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import platformdirs
from pydantic import BaseModel, Field
from rich.console import Console
from rich.logging import RichHandler


class LogLevel(str, Enum):
    """Log levels with string values for configuration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Available log formats."""

    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    RICH = "rich"


class LogOutput(str, Enum):
    """Available log output destinations."""

    CONSOLE = "console"
    FILE = "file"
    BOTH = "both"


class LoggingConfig(BaseModel):
    """Configuration for the logging system."""

    # Basic settings
    enabled: bool = True
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.RICH

    # Output settings
    output: LogOutput = LogOutput.BOTH
    log_file: Path = Field(
        default=Path(platformdirs.user_data_dir("plotty")) / "logs" / "plotty.log"
    )
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    backup_count: int = Field(default=5)

    # Console settings
    console_show_timestamp: bool = False
    console_show_level: bool = True
    console_rich_tracebacks: bool = True

    # Structured logging
    include_job_id: bool = True
    include_device_info: bool = True
    include_session_id: bool = True

    # Performance settings
    buffer_size: int = 1024
    flush_interval: int = 5


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add thread and process info for debugging
        if record.thread:
            log_data["thread_id"] = record.thread
            log_data["thread_name"] = record.threadName

        if record.process:
            log_data["process_id"] = record.process

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if enabled
        if self.include_extra and hasattr(record, "__dict__"):
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                }:
                    extra_fields[key] = value

            if extra_fields:
                log_data["extra"] = extra_fields

        return json.dumps(log_data, default=str)


class SimpleFormatter(logging.Formatter):
    """Simple formatter for clean console output."""

    def __init__(self, show_timestamp: bool = False, show_level: bool = True):
        self.show_timestamp = show_timestamp
        self.show_level = show_level

        if show_timestamp and show_level:
            format_str = "%(asctime)s - %(levelname)s - %(message)s"
        elif show_level:
            format_str = "%(levelname)s: %(message)s"
        else:
            format_str = "%(message)s"

        super().__init__(format_str, datefmt="%H:%M:%S")


class DetailedFormatter(logging.Formatter):
    """Detailed formatter with full context information."""

    def __init__(self):
        format_str = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(module)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        super().__init__(format_str, datefmt="%Y-%m-%d %H:%M:%S")


class PlottyLogger:
    """
    Enhanced logger with ploTTY-specific features.

    Provides structured logging with job context, device information,
    and session tracking for comprehensive monitoring and debugging.
    """

    def __init__(
        self,
        name: str,
        config: Optional[LoggingConfig] = None,
        console: Optional[Console] = None,
    ) -> None:
        self.name = name
        self.config = config or LoggingConfig()
        self.console = console or Console()

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, self.config.level.value))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Setup handlers if enabled
        if self.config.enabled:
            self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup console and file handlers based on configuration."""
        handlers = []

        # Console handler
        if self.config.output in [LogOutput.CONSOLE, LogOutput.BOTH]:
            console_handler = self._create_console_handler()
            handlers.append(console_handler)

        # File handler
        if self.config.output in [LogOutput.FILE, LogOutput.BOTH]:
            file_handler = self._create_file_handler()
            handlers.append(file_handler)

        # Add handlers to logger
        for handler in handlers:
            self.logger.addHandler(handler)

    def _create_console_handler(self) -> logging.Handler:
        """Create appropriate console handler based on format."""
        if self.config.format == LogFormat.RICH:
            handler = RichHandler(
                console=self.console,
                show_time=self.config.console_show_timestamp,
                show_level=self.config.console_show_level,
                rich_tracebacks=self.config.console_rich_tracebacks,
                markup=True,
            )
        else:
            handler = logging.StreamHandler(sys.stdout)

            if self.config.format == LogFormat.SIMPLE:
                formatter = SimpleFormatter(
                    show_timestamp=self.config.console_show_timestamp,
                    show_level=self.config.console_show_level,
                )
            elif self.config.format == LogFormat.DETAILED:
                formatter = DetailedFormatter()
            elif self.config.format == LogFormat.JSON:
                formatter = StructuredFormatter()
            else:
                formatter = SimpleFormatter()

            handler.setFormatter(formatter)

        handler.setLevel(getattr(logging, self.config.level.value))
        return handler

    def _create_file_handler(self) -> logging.Handler:
        """Create rotating file handler."""
        # Ensure log directory exists
        self.config.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler
        handler = logging.handlers.RotatingFileHandler(
            filename=self.config.log_file,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
            encoding="utf-8",
        )

        # Set formatter
        if self.config.format == LogFormat.JSON:
            formatter = StructuredFormatter()
        elif self.config.format == LogFormat.DETAILED:
            formatter = DetailedFormatter()
        else:
            formatter = SimpleFormatter(show_timestamp=True, show_level=True)

        handler.setFormatter(formatter)
        handler.setLevel(getattr(logging, self.config.level.value))
        return handler

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional extra context."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message with optional extra context."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with optional extra context."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with optional extra context."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with optional extra context."""
        self._log(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        kwargs["exc_info"] = True
        self._log(logging.ERROR, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal logging method with extra context."""
        extra = {}

        # Add job context if enabled
        if self.config.include_job_id and "job_id" in kwargs:
            extra["job_id"] = kwargs.pop("job_id")

        # Add device info if enabled
        if self.config.include_device_info and "device_info" in kwargs:
            extra["device_info"] = kwargs.pop("device_info")

        # Add session ID if enabled
        if self.config.include_session_id and "session_id" in kwargs:
            extra["session_id"] = kwargs.pop("session_id")

        # Add any remaining kwargs as extra
        extra.update(kwargs)

        # Log the message
        self.logger.log(level, message, extra=extra)

    def job_start(self, job_id: str, job_type: str = "plot", **context) -> None:
        """Log job start event."""
        self.info(
            f"Job started: {job_type} ({job_id})",
            job_id=job_id,
            event="job_start",
            job_type=job_type,
            **context,
        )

    def job_complete(
        self, job_id: str, duration: Optional[float] = None, **context
    ) -> None:
        """Log job completion event."""
        message = f"Job completed: {job_id}"
        if duration:
            message += f" (duration: {duration:.2f}s)"

        self.info(
            message, job_id=job_id, event="job_complete", duration=duration, **context
        )

    def job_error(self, job_id: str, error: Exception, **context) -> None:
        """Log job error event."""
        self.error(
            f"Job failed: {job_id} - {error}",
            job_id=job_id,
            event="job_error",
            error_type=type(error).__name__,
            error_message=str(error),
            **context,
        )

    def device_connect(self, device_type: str, device_id: str, **context) -> None:
        """Log device connection event."""
        self.info(
            f"Device connected: {device_type} ({device_id})",
            event="device_connect",
            device_type=device_type,
            device_id=device_id,
            **context,
        )

    def device_disconnect(self, device_type: str, device_id: str, **context) -> None:
        """Log device disconnection event."""
        self.info(
            f"Device disconnected: {device_type} ({device_id})",
            event="device_disconnect",
            device_type=device_type,
            device_id=device_id,
            **context,
        )

    def device_error(
        self, device_type: str, device_id: str, error: Exception, **context
    ) -> None:
        """Log device error event."""
        self.error(
            f"Device error: {device_type} ({device_id}) - {error}",
            event="device_error",
            device_type=device_type,
            device_id=device_id,
            error_type=type(error).__name__,
            error_message=str(error),
            **context,
        )


class LoggingManager:
    """
    Centralized logging management for ploTTY.

    Manages logger instances, configuration updates, and provides
    convenience methods for application-wide logging.
    """

    _instance: Optional[LoggingManager] = None
    _loggers: Dict[str, PlottyLogger] = {}

    def __new__(cls) -> LoggingManager:
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._config = LoggingConfig()
            self._console = Console()
            self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._initialized = True

    def get_logger(self, name: str) -> PlottyLogger:
        """Get or create a logger instance."""
        if name not in self._loggers:
            self._loggers[name] = PlottyLogger(name, self._config, self._console)
        return self._loggers[name]

    def update_config(self, config: LoggingConfig) -> None:
        """Update logging configuration for all loggers."""
        self._config = config

        # Recreate all loggers with new config
        for name in list(self._loggers.keys()):
            del self._loggers[name]

    def set_level(self, level: LogLevel) -> None:
        """Set log level for all loggers."""
        self._config.level = level
        for logger in self._loggers.values():
            logger.logger.setLevel(getattr(logging, level.value))

    def get_session_id(self) -> str:
        """Get the current session ID."""
        return self._session_id

    def list_log_files(self) -> list[Path]:
        """List all log files in the log directory."""
        log_dir = self._config.log_file.parent
        if not log_dir.exists():
            return []

        return list(log_dir.glob("*.log*"))

    def cleanup_old_logs(self, keep_days: int = 30) -> None:
        """Clean up old log files."""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=keep_days)

        for log_file in self.list_log_files():
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    self.get_logger("logging").info(
                        f"Cleaned up old log file: {log_file}"
                    )
            except OSError as e:
                self.get_logger("logging").error(
                    f"Failed to clean up log file {log_file}: {e}"
                )


# Global logging manager instance
logging_manager = LoggingManager()


def get_logger(name: str) -> PlottyLogger:
    """Get a logger instance from the global logging manager."""
    return logging_manager.get_logger(name)


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """Setup logging with optional custom configuration."""
    if config:
        logging_manager.update_config(config)


def config_from_settings(settings) -> LoggingConfig:
    """Convert Settings to LoggingConfig."""
    return LoggingConfig(
        enabled=settings.logging.enabled,
        level=LogLevel(settings.logging.level.upper()),
        format=LogFormat(settings.logging.format.lower()),
        output=LogOutput(settings.logging.output.lower()),
        log_file=Path(settings.logging.log_file),
        max_file_size=settings.logging.max_file_size,
        backup_count=settings.logging.backup_count,
        console_show_timestamp=settings.logging.console_show_timestamp,
        console_show_level=settings.logging.console_show_level,
        console_rich_tracebacks=settings.logging.console_rich_tracebacks,
        include_job_id=settings.logging.include_job_id,
        include_device_info=settings.logging.include_device_info,
        include_session_id=settings.logging.include_session_id,
        buffer_size=settings.logging.buffer_size,
        flush_interval=settings.logging.flush_interval,
    )
