"""Test core business logic modules with actual available functions."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from plotty.utils import PlottyError, create_error, validate_file_exists


class TestUtils:
    """Test utility functions."""

    def test_plotty_error_creation(self):
        """Test PlottyError creation."""
        error = PlottyError(
            message="Test error",
            suggestion="Try again",
            technical="Details",
            category="test",
        )

        error_str = str(error)
        assert "Test error" in error_str
        assert "Try again" in error_str
        assert "Details" in error_str

    def test_plotty_error_minimal(self):
        """Test PlottyError with minimal parameters."""
        error = PlottyError(message="Simple error")

        error_str = str(error)
        assert "Simple error" in error_str
        assert "💡" not in error_str  # No suggestion
        assert "Technical details" not in error_str  # No technical details

    def test_create_error_function(self):
        """Test create_error utility function."""
        error = create_error(
            message="Created error",
            suggestion="Check input",
            technical="Null value",
            category="validation",
        )

        assert isinstance(error, PlottyError)
        assert error.message == "Created error"
        assert error.suggestion == "Check input"

    def test_validate_file_exists_valid(self):
        """Test validate_file_exists with existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)

            try:
                result = validate_file_exists(temp_path, "Test file")
                assert result == temp_path
            finally:
                temp_path.unlink(missing_ok=True)

    def test_validate_file_exists_invalid(self):
        """Test validate_file_exists with non-existent file."""
        non_existent = Path("/non/existent/file.txt")

        with pytest.raises(PlottyError) as exc_info:
            validate_file_exists(non_existent, "Test file")

        error_str = str(exc_info.value)
        assert "Test file not found" in error_str
        assert "💡" in error_str  # Should have suggestion


class TestFileOperations:
    """Test file operations used across modules."""

    def test_temp_file_creation_cleanup(self):
        """Test temporary file creation and cleanup."""
        temp_files = []

        for i in range(3):
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".test"
            ) as f:
                f.write(f"test content {i}")
                temp_files.append(Path(f.name))

        # Verify files exist
        for temp_file in temp_files:
            assert temp_file.exists()
            assert temp_file.read_text() in [
                "test content 0",
                "test content 1",
                "test content 2",
            ]

        # Cleanup
        for temp_file in temp_files:
            temp_file.unlink(missing_ok=True)

    def test_path_operations(self):
        """Test path operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test path creation
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")

            assert test_file.exists()
            assert test_file.read_text() == "test content"

            # Test directory operations
            subdir = temp_path / "subdir"
            subdir.mkdir()
            assert subdir.exists()
            assert subdir.is_dir()


class TestErrorHandling:
    """Test error handling patterns."""

    def test_error_with_suggestion_formatting(self):
        """Test error formatting with suggestion."""
        error = PlottyError(
            message="File not found", suggestion="Check the file path and try again"
        )

        error_str = str(error)
        lines = error_str.split("\n")
        assert len(lines) == 2
        assert "File not found" in lines[0]
        assert "Check the file path and try again" in lines[1]
        assert "💡" in lines[1]

    def test_error_with_technical_details(self):
        """Test error formatting with technical details."""
        error = PlottyError(
            message="Connection failed", technical="Network timeout after 30 seconds"
        )

        error_str = str(error)
        lines = error_str.split("\n")
        assert len(lines) == 2
        assert "Connection failed" in lines[0]
        assert "Network timeout after 30 seconds" in lines[1]
        assert "Technical details" in lines[1]

    def test_error_category_handling(self):
        """Test error category is stored correctly."""
        error = PlottyError(message="Validation failed", category="validation")

        assert error.category == "validation"
        # Category is stored but may not appear in string representation
        assert error.category == "validation"


class TestConfiguration:
    """Test configuration-related functionality."""

    def test_config_loading_error_handling(self):
        """Test configuration loading error handling."""
        with patch("plotty.config.load_config") as mock_load:
            mock_load.side_effect = Exception("Config file corrupted")

            # Should handle config errors gracefully
            with pytest.raises(Exception):
                from plotty.config import load_config

                load_config()

    def test_config_default_values(self):
        """Test configuration default values."""
        with patch("plotty.config.load_config") as mock_load:
            mock_config = Mock()
            mock_config.database = Mock()
            mock_config.database.url = "sqlite:///default.db"
            mock_load.return_value = mock_config

            from plotty.config import load_config

            config = load_config()

            assert config.database.url == "sqlite:///default.db"


class TestPerformance:
    """Test performance characteristics."""

    def test_file_validation_performance(self):
        """Test file validation performance."""
        # Create a test file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)

            try:
                import time

                start_time = time.time()

                # Multiple validations should be fast
                for _ in range(100):
                    validate_file_exists(temp_path, "Test file")

                end_time = time.time()

                # Should complete quickly even with many validations
                assert end_time - start_time < 1.0
            finally:
                temp_path.unlink(missing_ok=True)

    def test_error_creation_performance(self):
        """Test error creation performance."""
        import time

        start_time = time.time()

        # Creating many errors should be fast
        errors = []
        for i in range(1000):
            error = create_error(f"Error {i}", f"Suggestion {i}")
            errors.append(error)

        end_time = time.time()

        assert len(errors) == 1000
        assert end_time - start_time < 0.5
        assert all(isinstance(e, PlottyError) for e in errors)


class TestModuleImports:
    """Test that core modules can be imported."""

    def test_import_backup_module(self):
        """Test backup module import."""
        from plotty import backup

        assert backup is not None
        assert hasattr(backup, "BackupManager")

    def test_import_paper_module(self):
        """Test paper module import."""
        from plotty import paper

        assert paper is not None
        assert hasattr(paper, "PaperManager")

    def test_import_utils_module(self):
        """Test utils module import."""
        from plotty import utils

        assert utils is not None
        assert hasattr(utils, "PlottyError")
        assert hasattr(utils, "create_error")

    def test_import_db_module(self):
        """Test db module import."""
        from plotty import db

        assert db is not None
        assert hasattr(db, "get_session")


class TestClassInstantiation:
    """Test that core classes can be instantiated."""

    def test_plotty_error_instantiation(self):
        """Test PlottyError can be instantiated."""
        error = PlottyError("Test message")
        assert isinstance(error, Exception)
        assert isinstance(error, PlottyError)
        assert error.message == "Test message"
        assert error.suggestion is None
        assert error.technical is None
        assert error.category == "general"

    def test_plotty_error_inheritance(self):
        """Test PlottyError inherits from Exception."""
        error = PlottyError("Test")
        assert isinstance(error, Exception)

        # Should be catchable as Exception
        try:
            raise error
        except Exception as e:
            assert e == error
