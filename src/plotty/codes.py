"""
Standardized exit codes for ploTTY CLI.

This module defines consistent exit codes for different scenarios,
making the system more predictable for automation and LLM integration.
"""

from __future__ import annotations
import sys
import typer
from typing import Optional


class ExitCode:
    """Standard exit codes for ploTTY."""

    SUCCESS = 0  # Operation completed successfully
    ERROR = 1  # General error occurred
    WARNING = 2  # Operation completed with warnings
    INVALID_INPUT = 3  # Invalid user input
    FILE_NOT_FOUND = 4  # File or resource not found
    PERMISSION_DENIED = 5  # Permission denied
    DEVICE_ERROR = 6  # Device-related error
    NETWORK_ERROR = 7  # Network-related error
    CONFIG_ERROR = 8  # Configuration error
    VALIDATION_ERROR = 9  # Validation failed
    TIMEOUT = 10  # Operation timed out
    CANCELLED = 11  # Operation cancelled by user
    NOT_FOUND = 12  # Resource not found
    ALREADY_EXISTS = 13  # Resource already exists
    BUSY = 14  # Resource is busy
    NOT_IMPLEMENTED = 15  # Feature not implemented
    INTERNAL_ERROR = 16  # Internal application error
    TESTS_FAILED = 17  # One or more tests failed


def exit_with_code(code: int, message: Optional[str] = None) -> None:
    """Exit with a specific exit code and optional message."""
    if message:
        print(message, file=sys.stderr)
    sys.exit(code)


def exit_success(message: Optional[str] = None) -> None:
    """Exit with success code."""
    exit_with_code(ExitCode.SUCCESS, message)


def exit_error(message: str) -> None:
    """Exit with error code."""
    exit_with_code(ExitCode.ERROR, message)


def exit_warning(message: str) -> None:
    """Exit with warning code."""
    exit_with_code(ExitCode.WARNING, message)


def exit_validation_error(message: str) -> None:
    """Exit with validation error code."""
    exit_with_code(ExitCode.VALIDATION_ERROR, message)


def exit_file_not_found(message: str) -> None:
    """Exit with file not found code."""
    exit_with_code(ExitCode.FILE_NOT_FOUND, message)


def exit_device_error(message: str) -> None:
    """Exit with device error code."""
    exit_with_code(ExitCode.DEVICE_ERROR, message)


def exit_config_error(message: str) -> None:
    """Exit with configuration error code."""
    exit_with_code(ExitCode.CONFIG_ERROR, message)


def exit_cancelled(message: Optional[str] = None) -> None:
    """Exit with cancelled code."""
    exit_with_code(ExitCode.CANCELLED, message or "Operation cancelled")


def handle_typer_exit(e: typer.Exit) -> None:
    """Handle Typer exit with proper exit code."""
    if e.exit_code == 0:
        exit_success()
    else:
        exit_with_code(e.exit_code)


def get_exit_code_name(code: int) -> str:
    """Get human-readable name for exit code."""
    code_names = {
        0: "SUCCESS",
        1: "ERROR",
        2: "WARNING",
        3: "INVALID_INPUT",
        4: "FILE_NOT_FOUND",
        5: "PERMISSION_DENIED",
        6: "DEVICE_ERROR",
        7: "NETWORK_ERROR",
        8: "CONFIG_ERROR",
        9: "VALIDATION_ERROR",
        10: "TIMEOUT",
        11: "CANCELLED",
        12: "NOT_FOUND",
        13: "ALREADY_EXISTS",
        14: "BUSY",
        15: "NOT_IMPLEMENTED",
        16: "INTERNAL_ERROR",
    }
    return code_names.get(code, f"UNKNOWN({code})")


# Context manager for exit code handling
class ExitCodeManager:
    """Context manager for consistent exit code handling."""

    def __init__(
        self, success_code: int = ExitCode.SUCCESS, error_code: int = ExitCode.ERROR
    ):
        self.success_code = success_code
        self.error_code = error_code
        self.exception_occurred = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.exception_occurred = True
            if isinstance(exc_val, typer.Exit):
                handle_typer_exit(exc_val)
            else:
                exit_with_code(self.error_code, str(exc_val))
        return True  # Suppress exception since we've handled it
