"""
Utility functions for ploTTY including error handling and common operations.

This module provides centralized error handling, user-friendly error messages,
and utility functions used across the ploTTY application.
"""

from __future__ import annotations

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
            result += f"\n[yellow]Suggestion:[/yellow] {self.suggestion}"
        if self.technical:
            result += f"\n[dim]Technical details:[/dim] {self.technical}"
        return result


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
            self.console.print(f"[red]Invalid parameter:[/red] {error}")
        elif isinstance(error, FileNotFoundError):
            self._handle_file_not_found(error)
        elif isinstance(error, PermissionError):
            self._handle_permission_error(error)
        elif isinstance(error, (ConnectionError, OSError)):
            self._handle_connection_error(error)
        else:
            self._handle_generic_error(error)

        if exit_on_error:
            sys.exit(1)

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
    Create a PlottyError with the given parameters.

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
