"""Test utility functions and error handling."""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
from typer import BadParameter

from plotty.utils import (
    PlottyError,
    JobError,
    DeviceError,
    ConfigError,
    ValidationError,
    ErrorHandler,
    create_error,
    create_job_error,
    create_device_error,
    create_config_error,
    create_validation_error,
    validate_file_exists,
    validate_directory,
)


class TestPlottyError:
    """Test custom PlottyError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = PlottyError("Test message")
        assert str(error) == "[red]Error:[/red] Test message"
        assert error.message == "Test message"
        assert error.suggestion is None
        assert error.technical is None
        assert error.category == "general"

    def test_error_with_suggestion(self):
        """Test error with suggestion."""
        error = PlottyError(
            "Test message", suggestion="Try again", technical="Details", category="test"
        )
        assert "Test message" in str(error)
        assert "Try again" in str(error)
        assert "Details" in str(error)
        assert error.category == "test"

    def test_job_error(self):
        """Test job-specific error."""
        error = JobError("Job failed", job_id="123")
        assert error.job_id == "123"
        assert error.category == "job"

    def test_device_error(self):
        """Test device-specific error."""
        error = DeviceError("Device not found", device_type="AxiDraw")
        assert error.device_type == "AxiDraw"
        assert error.category == "device"

    def test_config_error(self):
        """Test config-specific error."""
        error = ConfigError("Config invalid", config_file="/path/to/config")
        assert error.config_file == "/path/to/config"
        assert error.category == "config"

    def test_validation_error(self):
        """Test validation-specific error."""
        error = ValidationError("Invalid format", expected_format="YYYY-MM-DD")
        assert error.expected_format == "YYYY-MM-DD"
        assert error.category == "validation"


class TestErrorHandler:
    """Test centralized error handling."""

    @pytest.fixture
    def mock_console(self):
        """Mock console for testing."""
        return Mock()

    @pytest.fixture
    def error_handler(self, mock_console):
        """Create error handler with mock console."""
        return ErrorHandler(console=mock_console)

    def test_handle_plotty_error(self, error_handler, mock_console):
        """Test handling PlottyError."""
        error = PlottyError("Test error", suggestion="Fix it")
        error_handler.handle(error, exit_on_error=False)

        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "Test error" in call_args
        assert "Fix it" in call_args

    def test_handle_bad_parameter(self, error_handler, mock_console):
        """Test handling BadParameter."""
        error = BadParameter("Invalid job ID")
        error_handler.handle(error, exit_on_error=False)

        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "Invalid parameter" in call_args

    def test_handle_file_not_found(self, error_handler, mock_console):
        """Test handling FileNotFoundError."""
        error = FileNotFoundError("No such file", "/path/to/file")
        error_handler.handle(error, exit_on_error=False)

        mock_console.print.assert_called_once()

    def test_handle_permission_error(self, error_handler, mock_console):
        """Test handling PermissionError."""
        error = PermissionError("Permission denied")
        error_handler.handle(error, exit_on_error=False)

        mock_console.print.assert_called_once()

    def test_handle_connection_error(self, error_handler, mock_console):
        """Test handling ConnectionError."""
        error = ConnectionError("Connection failed")
        error_handler.handle(error, exit_on_error=False)

        mock_console.print.assert_called_once()

    def test_handle_import_error(self, error_handler, mock_console):
        """Test handling ImportError."""
        error = ImportError("Module not found")
        error_handler.handle(error, exit_on_error=False)

        mock_console.print.assert_called_once()

    def test_handle_json_error(self, error_handler, mock_console):
        """Test handling JSONDecodeError."""
        error = json.JSONDecodeError("Invalid JSON", "test", 0)
        error_handler.handle(error, exit_on_error=False)

        mock_console.print.assert_called_once()

    def test_handle_value_error(self, error_handler, mock_console):
        """Test handling ValueError."""
        error = ValueError("Invalid value")
        error_handler.handle(error, exit_on_error=False)

        mock_console.print.assert_called_once()

    def test_handle_generic_error(self, error_handler, mock_console):
        """Test handling generic Exception."""
        error = Exception("Generic error")
        error_handler.handle(error, exit_on_error=False)

        mock_console.print.assert_called_once()

    def test_exit_on_error(self, error_handler):
        """Test exit_on_error behavior."""
        error = PlottyError("Test error")

        with patch("sys.exit") as mock_exit:
            error_handler.handle(error, exit_on_error=True)
            mock_exit.assert_called_once_with(1)


class TestErrorFactoryFunctions:
    """Test error factory functions."""

    def test_create_error(self):
        """Test create_error function."""
        error = create_error("Test message", suggestion="Fix it")
        assert isinstance(error, PlottyError)
        assert error.message == "Test message"
        assert error.suggestion == "Fix it"

    def test_create_job_error(self):
        """Test create_job_error function."""
        error = create_job_error("Job failed", job_id="123")
        assert isinstance(error, JobError)
        assert error.job_id == "123"

    def test_create_device_error(self):
        """Test create_device_error function."""
        error = create_device_error("Device offline", device_type="AxiDraw")
        assert isinstance(error, DeviceError)
        assert error.device_type == "AxiDraw"

    def test_create_config_error(self):
        """Test create_config_error function."""
        error = create_config_error("Config missing", config_file="/path/to/config")
        assert isinstance(error, ConfigError)
        assert error.config_file == "/path/to/config"

    def test_create_validation_error(self):
        """Test create_validation_error function."""
        error = create_validation_error("Invalid date", expected_format="YYYY-MM-DD")
        assert isinstance(error, ValidationError)
        assert error.expected_format == "YYYY-MM-DD"


class TestValidationFunctions:
    """Test file and directory validation functions."""

    def test_validate_file_exists_success(self, tmp_path):
        """Test successful file validation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = validate_file_exists(test_file)
        assert result == test_file

    def test_validate_file_not_found(self):
        """Test file not found validation."""
        non_existent = Path("/non/existent/file.txt")

        with pytest.raises(PlottyError) as exc_info:
            validate_file_exists(non_existent)

        assert "not found" in str(exc_info.value).lower()
        assert exc_info.value.category == "file"

    def test_validate_directory_exists(self, tmp_path):
        """Test successful directory validation."""
        result = validate_directory(tmp_path)
        assert result == tmp_path

    def test_validate_directory_not_found(self):
        """Test directory not found validation."""
        non_existent = Path("/non/existent/directory")

        with pytest.raises(PlottyError) as exc_info:
            validate_directory(non_existent)

        assert "not found" in str(exc_info.value).lower()
        assert exc_info.value.category == "file"

    def test_validate_file_is_directory(self, tmp_path):
        """Test validation when file path is actually a directory."""
        # The function only checks existence, not if it's a file
        # So this should actually pass
        result = validate_file_exists(tmp_path)
        assert result == tmp_path

    def test_validate_directory_is_file(self, tmp_path):
        """Test validation when directory path is actually a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(PlottyError) as exc_info:
            validate_directory(test_file)

        assert "is not a directory" in str(exc_info.value).lower()

    def test_custom_description_in_validation(self, tmp_path):
        """Test custom description in validation errors."""
        non_existent = Path("/non/existent")

        with pytest.raises(PlottyError) as exc_info:
            validate_file_exists(non_existent, description="Configuration file")

        error_str = str(exc_info.value)
        assert "Configuration file" in error_str


class TestErrorHandlingIntegration:
    """Test error handling integration scenarios."""

    def test_error_handler_with_real_console(self):
        """Test error handler with real console (no mocking)."""
        handler = ErrorHandler()

        # Should not raise exception
        handler.handle(PlottyError("Test"), exit_on_error=False)

    def test_error_suggestions_for_different_parameters(self):
        """Test that different parameter types get appropriate suggestions."""
        handler = ErrorHandler()

        # Test job-related error
        job_error = BadParameter("Invalid job ID")
        with patch.object(handler.console, "print") as mock_print:
            handler.handle(job_error, exit_on_error=False)
            call_args = str(mock_print.call_args[0][0])
            assert "job" in call_args.lower()

        # Test paper-related error
        paper_error = BadParameter("Invalid paper size")
        with patch.object(handler.console, "print") as mock_print:
            handler.handle(paper_error, exit_on_error=False)
            call_args = str(mock_print.call_args[0][0])
            assert "paper" in call_args.lower()

        # Test pen-related error
        pen_error = BadParameter("Invalid pen type")
        with patch.object(handler.console, "print") as mock_print:
            handler.handle(pen_error, exit_on_error=False)
            call_args = str(mock_print.call_args[0][0])
            assert "pen" in call_args.lower()

    def test_error_categories(self):
        """Test that different error types have correct categories."""
        assert PlottyError("test").category == "general"
        assert JobError("test").category == "job"
        assert DeviceError("test").category == "device"
        assert ConfigError("test").category == "config"
        assert ValidationError("test").category == "validation"
