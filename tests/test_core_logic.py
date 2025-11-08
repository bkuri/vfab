"""Test core business logic modules."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

from plotty.backup import BackupManager, BackupType
from plotty.plotting import MultiPenPlotter, PenSwapPrompt
from plotty.paper import PaperSize, PaperConfig


class TestBackupManager:
    """Test backup functionality."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.db')
        conn = sqlite3.connect(path)
        conn.close()
        yield Path(path)
        Path(path).unlink(missing_ok=True)
    
    @pytest.fixture
    def backup_manager(self, temp_db):
        """Create backup manager with temporary database."""
        with patch('plotty.backup.get_db_path', return_value=temp_db):
            return BackupManager()
    
    def test_backup_creation(self, backup_manager):
        """Test basic backup creation."""
        # Test full backup - returns Path to backup file
        with patch.object(backup_manager, '_create_backup_file') as mock_create:
            mock_create.return_value = Path("/tmp/test_backup.tar.gz")
            result = backup_manager.create_backup(backup_type=BackupType.FULL)
            assert isinstance(result, Path)
    
    def test_backup_manifest_creation(self, backup_manager):
        """Test backup manifest creation."""
        manifest = backup_manager._create_manifest(BackupType.FULL)
        assert manifest.version == "1.0"
        assert manifest.created_by == "ploTTY"
        assert manifest.backup_type == BackupType.FULL


class TestPenSwapPrompt:
    """Test pen swap prompt functionality."""
    
    def test_prompt_creation(self):
        """Test pen swap prompt creation."""
        prompt = PenSwapPrompt(interactive=False)
        assert prompt.interactive is False
        assert prompt.current_pen is None
    
    def test_no_swap_needed(self):
        """Test that no swap is needed when pens are the same."""
        prompt = PenSwapPrompt(interactive=False)
        result = prompt.prompt_pen_swap("black", "black", "test_layer")
        assert result is True
    
    def test_first_pen_no_swap(self):
        """Test first pen setup (no previous pen)."""
        prompt = PenSwapPrompt(interactive=False)
        result = prompt.prompt_pen_swap(None, "black", "test_layer")
        assert result is True
    
    def test_pen_swap_required(self):
        """Test pen swap scenario."""
        prompt = PenSwapPrompt(interactive=False)
        result = prompt.prompt_pen_swap("black", "red", "test_layer")
        assert result is True


class TestPaperSize:
    """Test paper size enumeration and utilities."""
    
    def test_get_all_sizes(self):
        """Test getting all available paper sizes."""
        sizes = PaperSize.get_all_sizes()
        assert "A4" in sizes
        assert "Letter" in sizes
        assert len(sizes) > 0
    
    def test_get_dimensions(self):
        """Test getting paper dimensions."""
        a4_dims = PaperSize.get_dimensions("A4")
        assert a4_dims is not None
        assert a4_dims[0] == 210.0  # width
        assert a4_dims[1] == 297.0  # height
        
        invalid_dims = PaperSize.get_dimensions("InvalidSize")
        assert invalid_dims is None
    
    def test_is_valid_size(self):
        """Test paper size validation."""
        assert PaperSize.is_valid_size("A4") is True
        assert PaperSize.is_valid_size("Letter") is True
        assert PaperSize.is_valid_size("InvalidSize") is False
    
    def test_paper_config_creation(self):
        """Test paper configuration creation."""
        config = PaperConfig(
            name="A4",
            width_mm=210.0,
            height_mm=297.0,
            orientation="portrait"
        )
        assert config.name == "A4"
        assert config.width_mm == 210.0
        assert config.height_mm == 297.0
        assert config.orientation == "portrait"


class TestMultiPenPlotter:
    """Test multi-pen plotter functionality."""
    
    def test_plotter_creation(self):
        """Test plotter creation."""
        # Mock the driver manager to avoid hardware dependencies
        with patch('plotty.plotting.create_manager') as mock_manager:
            mock_manager.return_value = Mock()
            plotter = MultiPenPlotter()
            assert plotter is not None
    
    def test_layer_detection(self):
        """Test SVG layer detection."""
        from plotty.multipen import detect_svg_layers
        
        # Test with temporary SVG file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write('''<svg xmlns="http://www.w3.org/2000/svg">
                <g id="layer1">
                    <rect x="0" y="0" width="100" height="100" />
                </g>
                <g id="layer2">
                    <circle cx="50" cy="50" r="25" />
                </g>
            </svg>''')
            svg_path = Path(f.name)
        
        try:
            layers = detect_svg_layers(svg_path)
            assert isinstance(layers, list)
        finally:
            svg_path.unlink(missing_ok=True)


class TestErrorHandling:
    """Test error handling in core modules."""
    
    def test_backup_manager_error_handling(self):
        """Test backup manager error handling."""
        with patch('plotty.backup.get_db_path', return_value=Path("/nonexistent/path")):
            backup_manager = BackupManager()
            
            # Should handle missing database gracefully
            with patch.object(backup_manager, '_create_backup_file') as mock_create:
                mock_create.side_effect = Exception("Database not found")
                
                with pytest.raises(Exception):
                    backup_manager.create_backup(backup_type=BackupType.FULL)
    
    def test_paper_size_error_handling(self):
        """Test paper size error handling."""
        # Test with invalid dimensions
        result = PaperSize.get_dimensions("")
        assert result is None
        
        result = PaperSize.is_valid_size("")
        assert result is False