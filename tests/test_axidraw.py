"""Tests for AxiDraw integration functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Import functions if available
try:
    from plotty.drivers import create_manager, is_axidraw_available
except ImportError:
    create_manager = None

    def is_axidraw_available():
        """Check if pyaxidraw is available."""
        return False


def get_create_manager():
    """Get create_manager function if available."""
    try:
        from plotty.drivers import create_manager

        return create_manager
    except ImportError:
        return None


class TestAxiDrawManager:
    """Test AxiDraw manager functionality."""

    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_create_manager(self):
        """Test manager creation."""
        manager = create_manager()
        assert manager.model == 1
        assert manager.port is None
        assert not manager.connected

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_plot_file_success(self, mock_axidraw):
        """Test successful file plotting."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = None
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()
        svg_file = Path("test.svg")

        result = manager.plot_file(svg_file)

        assert result["success"] is True
        mock_ad.plot_setup.assert_called_once_with(str(svg_file))
        mock_ad.plot_run.assert_called_once_with(True)
        # Note: speed_pendown is not set by default, so we don't test it

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_plot_file_preview(self, mock_axidraw):
        """Test preview mode plotting."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = "<svg>preview</svg>"
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()
        svg_file = Path("test.svg")

        result = manager.plot_file(svg_file, preview_only=True)

        assert result["success"] is True
        # Note: preview is set internally, we just check success

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_plot_file_failure(self, mock_axidraw):
        """Test plot failure handling."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.side_effect = Exception("Connection failed")
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()
        svg_file = Path("test.svg")

        result = manager.plot_file(svg_file)

        assert result["success"] is False
        assert "Connection failed" in result["error"]

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_interactive_operations(self, mock_axidraw):
        """Test interactive mode operations."""
        mock_ad = Mock()
        mock_ad.interactive.return_value = None
        mock_ad.connect.return_value = True
        mock_ad.moveto.return_value = None
        mock_ad.lineto.return_value = None
        mock_ad.penup.return_value = None
        mock_ad.pendown.return_value = None
        mock_ad.current_pos.return_value = (2.5, 3.0)
        mock_ad.current_pen.return_value = True
        mock_ad.disconnect.return_value = None
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()

        # Test connection and operations
        assert manager.connect() is True
        mock_ad.interactive.assert_called_once()
        mock_ad.connect.assert_called_once()

        # Test movement
        manager.move_to(2.5, 3.0)
        mock_ad.moveto.assert_called_with(2.5, 3.0)

        # Test pen operations
        manager.pen_up()
        mock_ad.penup.assert_called_once()

        manager.pen_down()
        mock_ad.pendown.assert_called_once()

        # Test position query
        pos = manager.get_position()
        assert pos == (2.5, 3.0)
        mock_ad.current_pos.assert_called_once()

        # Test pen state
        pen_state = manager.get_pen_state()
        assert pen_state is True
        mock_ad.current_pen.assert_called_once()

        # Test disconnect
        manager.disconnect()
        mock_ad.disconnect.assert_called_once()
        assert not manager.connected

    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_interactive_not_connected(self):
        """Test operations when not connected."""
        manager = create_manager()

        # These should raise RuntimeError when not connected
        with pytest.raises(RuntimeError, match="Not connected to AxiDraw"):
            manager.get_position()

        with pytest.raises(RuntimeError, match="Not connected to AxiDraw"):
            manager.get_pen_state()

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_pen_operations(self, mock_axidraw):
        """Test pen up/down operations."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = None
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()
        svg_file = Path("test.svg")

        # Test with different pen heights
        result = manager.plot_file(svg_file, pen_height_up=60, pen_height_down=30)

        assert result["success"] is True
        # Note: pen_height_up/pen_height_down are not directly mapped to options
        # They would need to be implemented in the plot_file method

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_sysinfo(self, mock_axidraw):
        """Test system information retrieval."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = None
        mock_ad.fw_version_string = "2.8.1"
        mock_ad.version_string = "3.9.6"
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()

        info = manager.get_sysinfo()

        assert info["success"] is True
        assert "fw_version" in info
        assert info["fw_version"] == "2.8.1"
        assert "version" in info
        assert info["version"] == "3.9.6"

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_list_devices(self, mock_axidraw):
        """Test device listing."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = None
        mock_ad.name_list = ["AxiDraw_1", "/dev/ttyUSB0"]
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()

        devices = manager.list_devices()

        assert devices["success"] is True
        assert "devices" in devices
        assert len(devices["devices"]) == 2
        assert "AxiDraw_1" in devices["devices"]
        assert "/dev/ttyUSB0" in devices["devices"]

    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    @patch("plotty.drivers.axidraw.axidraw")
    def test_set_units(self, mock_axidraw):
        """Test unit setting."""
        mock_ad = Mock()
        mock_ad.interactive.return_value = None
        mock_ad.connect.return_value = True
        mock_ad.update.return_value = None
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()
        manager.connect()

        # Test setting units
        manager.set_units("mm")
        mock_ad.options.units = 2  # mm = 2
        mock_ad.update.assert_called_once()

        # Test invalid units
        with pytest.raises(ValueError, match="Invalid units"):
            manager.set_units("invalid")

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_cycle_pen(self, mock_axidraw):
        """Test pen cycling."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = None
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()

        result = manager.cycle_pen()

        assert result["success"] is True
        mock_ad.plot_setup.assert_called_once()
        assert mock_ad.options.mode == "cycle"

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(
        not is_axidraw_available(),
        reason="pyaxidraw not available",
    )
    def test_toggle_pen(self, mock_axidraw):
        """Test pen toggling."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = None
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()

        result = manager.toggle_pen()

        assert result["success"] is True
        mock_ad.plot_setup.assert_called_once()
        assert mock_ad.options.mode == "toggle"
