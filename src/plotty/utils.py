"""
Utility functions for ploTTY including error handling and common operations.

This module provides centralized error handling, user-friendly error messages,
and utility functions used across the ploTTY application.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console


class PlottyError(Exception):
    """
    Custom exception class for ploTTY with user-friendly error messages and suggestions.

    This exception provides structured error information including:
    - User-friendly error message
    - Technical details (optional)
    - Suggestions for resolution
    - Error category for proper handling
    """

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        technical: Optional[str] = None,
        category: str = "general",
    ) -> None:
        self.message = message
        self.suggestion = suggestion
        self.technical = technical
        self.category = category
        super().__init__(self.message)

    def __str__(self) -> str:
        result = f"[red]Error:[/red] {self.message}"
        if self.suggestion:
            result += f"\n[yellow]💡 Suggestion:[/yellow] {self.suggestion}"
        if self.technical:
            result += f"\n[dim]Technical details:[/dim] {self.technical}"
        return result


class JobError(PlottyError):
    """Job-related errors with specific suggestions."""

    def __init__(self, message: str, job_id: Optional[str] = None, **kwargs):
        self.job_id = job_id
        super().__init__(message, category="job", **kwargs)


class DeviceError(PlottyError):
    """Device/plotter-related errors with hardware-specific suggestions."""

    def __init__(self, message: str, device_type: str = "AxiDraw", **kwargs):
        self.device_type = device_type
        super().__init__(message, category="device", **kwargs)


class ConfigError(PlottyError):
    """Configuration-related errors with setup suggestions."""

    def __init__(self, message: str, config_file: Optional[str] = None, **kwargs):
        self.config_file = config_file
        super().__init__(message, category="config", **kwargs)


class ValidationError(PlottyError):
    """Input validation errors with format suggestions."""

    def __init__(self, message: str, expected_format: Optional[str] = None, **kwargs):
        self.expected_format = expected_format
        super().__init__(message, category="validation", **kwargs)


class ErrorHandler:
    """
    Centralized error handling for ploTTY commands.

    Provides consistent error formatting, logging, and user guidance
    across all CLI commands and operations.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        self.console = console or Console()

    def handle(self, error: Exception, exit_on_error: bool = True) -> None:
        """
        Handle an exception with user-friendly formatting.

        Args:
            error: The exception to handle
            exit_on_error: Whether to exit the program after handling
        """
        if isinstance(error, PlottyError):
            self.console.print(str(error))
        elif isinstance(error, typer.BadParameter):
            self._handle_bad_parameter(error)
        elif isinstance(error, FileNotFoundError):
            self._handle_file_not_found(error)
        elif isinstance(error, PermissionError):
            self._handle_permission_error(error)
        elif isinstance(error, (ConnectionError, OSError)):
            self._handle_connection_error(error)
        elif isinstance(error, ImportError):
            self._handle_import_error(error)
        elif isinstance(error, json.JSONDecodeError):
            self._handle_json_error(error)
        elif isinstance(error, ValueError):
            self._handle_value_error(error)
        else:
            self._handle_generic_error(error)

        if exit_on_error:
            sys.exit(1)

    def _handle_bad_parameter(self, error: typer.BadParameter) -> None:
        """Handle invalid CLI parameters with helpful suggestions."""
        message = f"Invalid parameter: {error}"

        # Common parameter suggestions
        if "job" in str(error).lower():
            suggestion = "Use 'plotty status queue' to see available job IDs"
        elif "paper" in str(error).lower():
            suggestion = "Use 'plotty paper-list' to see available paper sizes"
        elif "pen" in str(error).lower():
            suggestion = "Use 'plotty pen-list' to see available pens"
        else:
            suggestion = "Check the command help with '--help' for valid options"

        plotty_error = PlottyError(
            message=message,
            suggestion=suggestion,
            technical=str(error),
            category="parameter",
        )
        self.console.print(str(plotty_error))

    def _handle_file_not_found(self, error: FileNotFoundError) -> None:
        """Handle file not found errors with helpful suggestions."""
        file_path = Path(str(error.filename)) if error.filename else Path("unknown")

        message = f"File not found: {file_path}"
        suggestion = self._get_file_suggestion(file_path)

        plotty_error = PlottyError(
            message=message,
            suggestion=suggestion,
            technical=str(error),
            category="file",
        )
        self.console.print(str(plotty_error))

    def _handle_permission_error(self, error: PermissionError) -> None:
        """Handle permission errors with helpful suggestions."""
        message = "Permission denied"
        suggestion = "Check file permissions and ensure you have access to the required resources"

        plotty_error = PlottyError(
            message=message,
            suggestion=suggestion,
            technical=str(error),
            category="permission",
        )
        self.console.print(str(plotty_error))

    def _handle_connection_error(self, error: Exception) -> None:
        """Handle connection/device errors with helpful suggestions."""
        message = "Connection or device error"
        suggestion = (
            "Check device connections and ensure the plotter is properly configured"
        )

        plotty_error = PlottyError(
            message=message,
            suggestion=suggestion,
            technical=str(error),
            category="connection",
        )
        self.console.print(str(plotty_error))

    def _handle_import_error(self, error: ImportError) -> None:
        """Handle import errors with installation suggestions."""
        module_name = (
            str(error).split("'")[1] if "'" in str(error) else "unknown module"
        )

        if "axidraw" in module_name.lower():
            message = "AxiDraw support not available"
            suggestion = "Install with: uv pip install -e '.[axidraw]'"
        elif "vpype" in module_name.lower():
            message = "vpype not available"
            suggestion = "Install with: uv pip install -e '.[vpype]'"
        else:
            message = f"Missing dependency: {module_name}"
            suggestion = "Install with: uv pip install -e '.[dev,vpype,axidraw]'"

        plotty_error = PlottyError(
            message=message,
            suggestion=suggestion,
            technical=str(error),
            category="dependency",
        )
        self.console.print(str(plotty_error))

    def _handle_json_error(self, error: json.JSONDecodeError) -> None:
        """Handle JSON parsing errors with file-specific suggestions."""
        message = "Invalid JSON format in file"
        suggestion = "Check file syntax and ensure valid JSON structure"

        if hasattr(error, "doc") and error.doc:
            # Try to extract filename from the document
            first_line = error.doc.split("\n")[0] if error.doc else ""
            if "config" in first_line.lower():
                suggestion = (
                    "Validate your configuration file with 'plotty config-check'"
                )

        plotty_error = PlottyError(
            message=message,
            suggestion=suggestion,
            technical=f"Line {error.lineno}, Column {error.colno}: {error.msg}",
            category="format",
        )
        self.console.print(str(plotty_error))

    def _handle_value_error(self, error: ValueError) -> None:
        """Handle value errors with format suggestions."""
        message = f"Invalid value: {str(error)}"

        # Common value error suggestions
        error_str = str(error).lower()
        if "paper" in error_str:
            suggestion = "Use 'plotty paper-list' to see available paper sizes"
        elif "pen" in error_str:
            suggestion = "Use 'plotty pen-list' to see available pens"
        elif "orientation" in error_str:
            suggestion = "Valid orientations: 'portrait' or 'landscape'"
        elif "positive" in error_str:
            suggestion = "Values must be positive numbers"
        else:
            suggestion = "Check the input format and try again"

        plotty_error = PlottyError(
            message=message,
            suggestion=suggestion,
            technical=str(error),
            category="validation",
        )
        self.console.print(str(plotty_error))

    def _handle_generic_error(self, error: Exception) -> None:
        """Handle generic errors with debugging information."""
        message = f"Unexpected error: {type(error).__name__}"
        suggestion = "Run with --debug flag for more information or check the logs"

        plotty_error = PlottyError(
            message=message,
            suggestion=suggestion,
            technical=str(error),
            category="general",
        )
        self.console.print(str(plotty_error))

    def _get_file_suggestion(self, file_path: Path) -> str:
        """Get helpful suggestions based on file type and path."""
        if file_path.suffix.lower() in [".svg", ".png", ".jpg", ".jpeg"]:
            return f"Check if the file exists and is accessible: {file_path}"
        elif file_path.suffix.lower() == ".yaml":
            return "Check your configuration file path and YAML syntax"
        elif "config" in str(file_path).lower():
            return "Run 'plotty setup' to create a valid configuration"
        else:
            return f"Verify the file path exists: {file_path}"


def create_error(
    message: str,
    suggestion: Optional[str] = None,
    technical: Optional[str] = None,
    category: str = "general",
) -> PlottyError:
    """
    Create a PlottyError with given parameters.

    This is a convenience function for creating consistent error messages
    across the application.

    Args:
        message: User-friendly error message
        suggestion: Optional suggestion for resolution
        technical: Optional technical details
        category: Error category for grouping

    Returns:
        PlottyError instance
    """
    return PlottyError(
        message=message, suggestion=suggestion, technical=technical, category=category
    )


def create_job_error(
    message: str, job_id: Optional[str] = None, suggestion: Optional[str] = None
) -> JobError:
    """Create a JobError with job-specific context."""
    if not suggestion:
        if job_id:
            suggestion = f"Use 'plotty status job {job_id}' to check job status"
        else:
            suggestion = "Use 'plotty status queue' to see available jobs"

    return JobError(message=message, job_id=job_id, suggestion=suggestion)


def create_device_error(
    message: str, device_type: str = "AxiDraw", suggestion: Optional[str] = None
) -> DeviceError:
    """Create a DeviceError with hardware-specific context."""
    if not suggestion:
        if device_type == "AxiDraw":
            suggestion = "Check AxiDraw connection and install with: uv pip install -e '.[axidraw]'"
        else:
            suggestion = "Check device connections and configuration"

    return DeviceError(message=message, device_type=device_type, suggestion=suggestion)


def create_config_error(
    message: str, config_file: Optional[str] = None, suggestion: Optional[str] = None
) -> ConfigError:
    """Create a ConfigError with configuration-specific context."""
    if not suggestion:
        suggestion = "Run 'plotty setup' to create a valid configuration"

    return ConfigError(message=message, config_file=config_file, suggestion=suggestion)


def create_validation_error(
    message: str,
    expected_format: Optional[str] = None,
    suggestion: Optional[str] = None,
) -> ValidationError:
    """Create a ValidationError with format-specific context."""
    if not suggestion:
        if expected_format:
            suggestion = f"Expected format: {expected_format}"
        else:
            suggestion = "Check the input format and try again"

    return ValidationError(
        message=message, expected_format=expected_format, suggestion=suggestion
    )


def validate_file_exists(file_path: Path, description: str = "File") -> Path:
    """
    Validate that a file exists and return the path if valid.

    Args:
        file_path: Path to validate
        description: Description of the file for error messages

    Returns:
        The validated path

    Raises:
        PlottyError: If the file doesn't exist
    """
    if not file_path.exists():
        raise create_error(
            message=f"{description} not found: {file_path}",
            suggestion=f"Check the file path and ensure the {description.lower()} exists",
            category="file",
        )
    return file_path


def validate_directory(dir_path: Path, description: str = "Directory") -> Path:
    """
    Validate that a directory exists and is writable.

    Args:
        dir_path: Directory path to validate
        description: Description of the directory for error messages

    Returns:
        The validated path

    Raises:
        PlottyError: If the directory doesn't exist or isn't writable
    """
    if not dir_path.exists():
        raise create_error(
            message=f"{description} not found: {dir_path}",
            suggestion=f"Create the {description.lower()} or check the path",
            category="file",
        )

    if not dir_path.is_dir():
        raise create_error(
            message=f"Path is not a directory: {dir_path}",
            suggestion="Provide a valid directory path",
            category="file",
        )

    return dir_path


# Global error handler instance
error_handler = ErrorHandler()
