"""Test core business logic modules with actual functions."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from plotty.backup import BackupManager, BackupType
from plotty.paper import PaperManager
from plotty.utils import PlottyError, create_error, validate_file_exists


class TestBackupManager:
    """Test backup functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Initialize with basic structure
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, name TEXT)"
        )
        conn.execute("INSERT INTO jobs (id, name) VALUES (1, 'test_job')")
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    def test_backup_manager_init(self, temp_db):
        """Test BackupManager initialization."""
        with patch(
            "plotty.backup.get_database_url", return_value=f"sqlite:///{temp_db}"
        ):
            manager = BackupManager()
            assert manager is not None

    def test_create_backup_full(self, temp_db):
        """Test creating a full backup."""
        with patch(
            "plotty.backup.get_database_url", return_value=f"sqlite:///{temp_db}"
        ):
            manager = BackupManager()

            with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as f:
                backup_path = Path(f.name)

            result_path = None
            try:
                result_path = manager.create_backup(BackupType.FULL)
                assert result_path.exists()
            finally:
                if result_path:
                    result_path.unlink(missing_ok=True)

    def test_create_backup_config(self, temp_db):
        """Test creating a config backup."""
        with patch(
            "plotty.backup.get_database_url", return_value=f"sqlite:///{temp_db}"
        ):
            manager = BackupManager()

            result_path = None
            try:
                result_path = manager.create_backup(BackupType.CONFIG)
                assert result_path.exists()
            finally:
                if result_path:
                    result_path.unlink(missing_ok=True)

    def test_restore_backup(self, temp_db):
        """Test restoring a backup."""
        with patch(
            "plotty.backup.get_database_url", return_value=f"sqlite:///{temp_db}"
        ):
            manager = BackupManager()

            result_path = None
            try:
                # Create a backup
                result_path = manager.create_backup(BackupType.FULL)
                assert result_path.exists()

                # Test that restore can be called (even if no data to restore)
                success = manager.restore_backup(result_path)
                assert success
            finally:
                if result_path:
                    result_path.unlink(missing_ok=True)


class TestPaperManager:
    """Test paper management functionality."""

    def test_paper_manager_init(self):
        """Test PaperManager initialization."""
        with patch("plotty.paper.get_session") as mock_session:
            mock_session.return_value.__enter__.return_value = Mock()

            manager = PaperManager(session_factory=Mock())
            assert manager is not None

    def test_list_papers(self):
        """Test listing paper configurations."""
        # Test with no session (should return standard papers)
        manager = PaperManager(session_factory=Mock())
        papers = manager.list_papers()
        assert len(papers) == 13  # Standard papers count


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

        assert "Test error" in str(error)
        assert "Try again" in str(error)
        assert "Details" in str(error)

    def test_plotty_error_minimal(self):
        """Test PlottyError with minimal parameters."""
        error = PlottyError(message="Simple error")

        assert "Simple error" in str(error)
        assert "💡" not in str(error)  # No suggestion
        assert "Technical details" not in str(error)  # No technical details

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

        assert "Test file not found" in str(exc_info.value)
        assert "💡" in str(exc_info.value)  # Should have suggestion


class TestErrorHandling:
    """Test error handling in core modules."""

    def test_backup_manager_nonexistent_db(self):
        """Test backup manager with nonexistent database."""
        with patch(
            "plotty.backup.get_database_url", return_value="sqlite:///nonexistent.db"
        ):
            manager = BackupManager()

            result_path = None
            try:
                result_path = manager.create_backup(BackupType.FULL)
                assert result_path.exists()
            finally:
                if result_path:
                    result_path.unlink(missing_ok=True)

    def test_paper_manager_session_error(self):
        """Test paper manager database error handling."""
        manager = PaperManager(session_factory=Mock())
        
        # Mock session factory to raise exception
        manager.session_factory = Mock()
        manager.session_factory.side_effect = Exception("Database connection failed")
        
        # This should handle the exception gracefully
        paper = manager.get_paper_by_name("NonExistent")
        assert paper is None


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


class TestDateTimeOperations:
    """Test date/time operations in backup module."""

    def test_backup_timestamp_format(self):
        """Test backup timestamp formatting."""
        with patch("plotty.backup.get_database_url", return_value="sqlite:///test.db"):
            manager = BackupManager()

            # Test timestamp generation
            timestamp = manager._generate_timestamp()
            assert isinstance(timestamp, str)
            assert len(timestamp) > 0

            # Should be parseable
            try:
                datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                assert True
            except ValueError:
                assert False, "Timestamp should be in correct format"


class TestConfigurationIntegration:
    """Test configuration integration with core modules."""

    def test_backup_config_integration(self):
        """Test backup manager configuration integration."""
        from plotty.backup import BackupConfig
        
        config = BackupConfig(
            backup_directory=Path("/tmp/backup"),
            retention_days=7
        )

        with patch(
            "plotty.backup.get_database_url", return_value="sqlite:///test.db"
        ):
            manager = BackupManager(config=config)
            assert manager.config.backup_directory == Path("/tmp/backup")
            assert manager.config.retention_days == 7


class TestPerformance:
    """Test performance characteristics."""

    def test_backup_performance_small_db(self):
        """Test backup performance with small database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Create small test database
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER, data TEXT)")
        for i in range(100):
            conn.execute("INSERT INTO test VALUES (?, ?)", (i, f"data_{i}"))
        conn.commit()
        conn.close()

        try:
            with patch(
                "plotty.backup.get_database_url", return_value=f"sqlite:///{db_path}"
            ):
                manager = BackupManager()

                with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as f:
                    backup_path = Path(f.name)

                result_path = None
                try:
                    import time

                    start_time = time.time()
                    result_path = manager.create_backup(BackupType.FULL)
                    end_time = time.time()

                    assert result_path.exists()
                    assert end_time - start_time < 5.0  # Should complete quickly
                finally:
                    if result_path:
                        result_path.unlink(missing_ok=True)
        finally:
            Path(db_path).unlink(missing_ok=True)
