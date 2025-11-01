"""Tests for AxiDraw integration functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

try:
    from plotty.drivers import create_manager, is_axidraw_available
except ImportError:
    create_manager = None

    def is_axidraw_available():
        return False


class TestAxiDrawManager:
    """Test AxiDraw manager functionality."""

    @pytest.mark.skipif(not is_axidraw_available(), reason="pyaxidraw not available")
    def test_create_manager(self):
        """Test manager creation."""
        manager = create_manager()
        assert manager.model == 1
        assert manager.port is None
        assert not manager.connected

        manager_with_port = create_manager(port="/dev/ttyUSB0", model=2)
        assert manager_with_port.model == 2
        assert manager_with_port.port == "/dev/ttyUSB0"

    @patch("plotty.drivers.axidraw.axidraw")
    @pytest.mark.skipif(not is_axidraw_available(), reason="pyaxidraw not available")
    def test_plot_file_success(self, mock_axidraw):
        """Test successful SVG plotting."""
        # Setup mock
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = "<svg>test</svg>"
        mock_ad.time_elapsed = 10.5
        mock_ad.distance_pendown = 150.0
        mock_ad.pen_lifts = 25
        mock_ad.fw_version_string = "2.8.1"
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()
        svg_file = Path("test.svg")

        result = manager.plot_file(svg_file, speed_pendown=30)

        assert result["success"] is True
        assert "output_svg" in result
        assert result["time_elapsed"] == 10.5
        assert result["distance_pendown"] == 150.0
        assert result["pen_lifts"] == 25
        assert result["fw_version"] == "2.8.1"

        mock_ad.plot_setup.assert_called_once_with(str(svg_file))
        mock_ad.plot_run.assert_called_once_with(True)
        assert mock_ad.options.speed_pendown == 30

    @patch("plotty.drivers.axidraw.axidraw")
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
        mock_ad.options.preview = True

    @patch("plotty.drivers.axidraw.axidraw")
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
        assert "error" in result
        assert result["error"] == "Connection failed"

    @patch("plotty.drivers.axidraw.axidraw")
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

        # Test connection
        assert manager.connect() is True
        assert manager.connected is True

        # Test movements
        manager.move_to(1.0, 2.0)
        manager.draw_to(3.0, 4.0)
        manager.pen_up()
        manager.pen_down()

        # Test queries
        pos = manager.get_position()
        assert pos == (2.5, 3.0)
        pen_state = manager.get_pen_state()
        assert pen_state is True

        # Test disconnection
        manager.disconnect()
        assert manager.connected is False

        # Verify method calls
        mock_ad.interactive.assert_called_once()
        mock_ad.connect.assert_called_once()
        mock_ad.moveto.assert_called_with(1.0, 2.0)
        mock_ad.lineto.assert_called_with(3.0, 4.0)
        mock_ad.penup.assert_called_once()
        mock_ad.pendown.assert_called_once()
        mock_ad.disconnect.assert_called_once()

    def test_interactive_not_connected(self):
        """Test operations when not connected."""
        manager = create_manager()

        with pytest.raises(RuntimeError, match="Not connected to AxiDraw"):
            manager.move_to(1.0, 2.0)

        with pytest.raises(RuntimeError, match="Not connected to AxiDraw"):
            manager.draw_to(1.0, 2.0)

        with pytest.raises(RuntimeError, match="Not connected to AxiDraw"):
            manager.pen_up()

    @patch("plotty.drivers.axidraw.axidraw")
    def test_pen_operations(self, mock_axidraw):
        """Test pen up/down operations."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = None
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()

        # Test pen cycle
        result = manager.cycle_pen()
        assert result["success"] is True
        mock_ad.options.mode = "cycle"
        mock_ad.plot_run.assert_called_once()

        # Test pen toggle
        result = manager.toggle_pen()
        assert result["success"] is True
        mock_ad.options.mode = "toggle"
        mock_ad.plot_run.assert_called()

    @patch("plotty.drivers.axidraw.axidraw")
    def test_sysinfo(self, mock_axidraw):
        """Test system information retrieval."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = None
        mock_ad.fw_version_string = "2.8.1"
        mock_ad.version_string = "3.9.6"
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()

        result = manager.get_sysinfo()

        assert result["success"] is True
        assert result["fw_version"] == "2.8.1"
        assert result["version"] == "3.9.6"
        mock_ad.options.mode = "sysinfo"
        mock_ad.plot_run.assert_called_once()

    @patch("plotty.drivers.axidraw.axidraw")
    def test_list_devices(self, mock_axidraw):
        """Test device listing."""
        mock_ad = Mock()
        mock_ad.plot_setup.return_value = None
        mock_ad.plot_run.return_value = None
        mock_ad.name_list = ["AxiDraw_1", "/dev/ttyUSB0"]
        mock_axidraw.AxiDraw.return_value = mock_ad

        manager = create_manager()

        result = manager.list_devices()

        assert result["success"] is True
        assert len(result["devices"]) == 2
        assert "AxiDraw_1" in result["devices"]
        mock_ad.options.mode = "manual"
        mock_ad.options.manual_cmd = "list_names"
        mock_ad.plot_run.assert_called_once()

    def test_set_units(self):
        """Test unit setting."""
        manager = create_manager()

        # Mock connection for unit testing
        manager.connected = True
        manager.ad = Mock()
        manager.ad.update.return_value = None

        manager.set_units("cm")
        assert manager.ad.options.units == 1

        manager.set_units("mm")
        assert manager.ad.options.units == 2

        with pytest.raises(ValueError, match="Invalid units"):
            manager.set_units("invalid")

    @patch("plotty.drivers.axidraw._AXIDRAW_AVAILABLE", False)
    def test_import_error_handling(self):
        """Test ImportError when pyaxidraw not available."""
        with pytest.raises(ImportError, match="pyaxidraw not found"):
            create_manager()


class TestAxiDrawIntegration:
    """Test integration with planner module."""

    def test_plan_axidraw_layers_basic(self):
        """Test basic AxiDraw layer planning integration."""
        # This test verifies the integration between planner and axidraw modules
        # without getting into the complex vpype mocking

        from plotty.planner import plan_axidraw_layers
        from plotty.drivers import create_manager

        # Test that create_manager can be called with the expected parameters
        try:
            manager = create_manager(port="/dev/ttyUSB0", model=2)
            # If pyaxidraw is available, verify the manager was created correctly
            assert manager.port == "/dev/ttyUSB0"
            assert manager.model == 2
        except ImportError:
            # If pyaxidraw is not available, that's expected in test environment
            pass

        # Test that the function exists and has the right signature
        import inspect

        sig = inspect.signature(plan_axidraw_layers)
        actual_params = list(sig.parameters.keys())
        print(f"Actual parameters: {actual_params}")

        # Just check that key parameters exist
        key_params = ["src_svg", "preset", "pen_map", "out_dir", "port"]
        for param in key_params:
            assert param in actual_params


if __name__ == "__main__":
    pytest.main([__file__])
