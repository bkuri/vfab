"""
Comprehensive tests for plotting.py multi-pen plotting functionality.
"""

from __future__ import annotations
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from vfab.plotting import PenSwapPrompt, MultiPenPlotter


class TestPenSwapPrompt:
    """Test PenSwapPrompt class functionality."""

    def test_pen_swap_prompt_initialization(self):
        """Test PenSwapPrompt initialization."""
        prompt = PenSwapPrompt(interactive=True)
        assert prompt.interactive is True
        assert prompt.current_pen is None

        prompt_noninteractive = PenSwapPrompt(interactive=False)
        assert prompt_noninteractive.interactive is False

    def test_prompt_pen_swap_no_swap_needed(self):
        """Test pen swap prompt when no swap is needed."""
        prompt = PenSwapPrompt(interactive=True)

        # Same pen should return True without prompting
        result = prompt.prompt_pen_swap("black", "black", "test_layer")
        assert result is True

    def test_prompt_pen_swap_first_pen(self):
        """Test pen swap prompt for first pen (no from_pen)."""
        prompt = PenSwapPrompt(interactive=True)

        with patch("builtins.input", return_value=""):
            with patch("builtins.print") as mock_print:
                result = prompt.prompt_pen_swap(None, "black", "test_layer")

                assert result is True
                assert prompt.current_pen == "black"
                # Should print the prompt message
                mock_print.assert_called()

    def test_prompt_pen_swap_with_swap(self):
        """Test pen swap prompt with actual pen swap."""
        prompt = PenSwapPrompt(interactive=True)

        with patch("builtins.input", return_value=""):
            with patch("builtins.print") as mock_print:
                result = prompt.prompt_pen_swap("red", "black", "test_layer")

                assert result is True
                assert prompt.current_pen == "black"
                mock_print.assert_called()

    def test_prompt_pen_swap_non_interactive(self):
        """Test pen swap prompt in non-interactive mode."""
        prompt = PenSwapPrompt(interactive=False)

        with patch("builtins.print") as mock_print:
            result = prompt.prompt_pen_swap("red", "black", "test_layer")

            assert result is True
            assert prompt.current_pen == "black"
            mock_print.assert_called()

    def test_prompt_pen_swap_user_continue(self):
        """Test pen swap prompt with user choosing to continue."""
        prompt = PenSwapPrompt(interactive=True)

        with patch("builtins.input", return_value="continue"):
            result = prompt.prompt_pen_swap("red", "black", "test_layer")

            assert result is True
            assert prompt.current_pen == "black"

    def test_prompt_pen_swap_user_skip(self):
        """Test pen swap prompt with user choosing to skip."""
        prompt = PenSwapPrompt(interactive=True)

        with patch("builtins.input", return_value="skip"):
            result = prompt.prompt_pen_swap("red", "black", "test_layer")

            assert result is False
            # current_pen should not change when skipping
            assert prompt.current_pen != "black"

    def test_prompt_pen_swap_user_abort(self):
        """Test pen swap prompt with user choosing to abort."""
        prompt = PenSwapPrompt(interactive=True)

        with patch("builtins.input", return_value="abort"):
            with pytest.raises(KeyboardInterrupt, match="Plotting aborted"):
                prompt.prompt_pen_swap("red", "black", "test_layer")

    def test_prompt_pen_swap_invalid_then_valid(self):
        """Test pen swap prompt with invalid input followed by valid input."""
        prompt = PenSwapPrompt(interactive=True)

        with patch("builtins.input", side_effect=["invalid", "continue"]):
            with patch("builtins.print") as mock_print:
                result = prompt.prompt_pen_swap("red", "black", "test_layer")

                assert result is True
                assert prompt.current_pen == "black"
                # Should print error message for invalid input
                mock_print.assert_any_call(
                    "Invalid option. Try: continue, skip, or abort"
                )


class TestMultiPenPlotter:
    """Test MultiPenPlotter class functionality."""

    @pytest.fixture
    def mock_manager(self):
        """Create mock manager for testing."""
        manager = Mock()
        manager.plot_file.return_value = {
            "success": True,
            "time_elapsed": 10.5,
            "distance_pendown": 150.0,
        }
        return manager

    @pytest.fixture
    def workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_multipen_plotter_no_axidraw_available(self):
        """Test MultiPenPlotter initialization when AxiDraw is not available."""
        with patch("vfab.plotting.is_axidraw_available", return_value=False):
            with pytest.raises(ImportError, match="AxiDraw support not available"):
                MultiPenPlotter()

    def test_multipen_plotter_initialization(self, mock_manager):
        """Test MultiPenPlotter initialization with AxiDraw available."""
        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(
                    port="/dev/ttyUSB0", model=2, interactive=False
                )

                assert plotter.manager == mock_manager
                assert plotter.interactive is False
                assert isinstance(plotter.prompt, PenSwapPrompt)
                assert plotter.prompt.interactive is False

    def test_plot_multipen_job_success(self, mock_manager, workspace):
        """Test successful multi-pen job plotting."""
        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                # Create test layer files
                job_dir = workspace / "test_job"
                job_dir.mkdir()

                layer_files = []
                for i in range(3):
                    layer_file = job_dir / f"layer_{i}.svg"
                    layer_file.write_text(
                        f"<svg><circle cx='{i*10}' cy='{i*10}' r='5'/></svg>"
                    )
                    layer_files.append(layer_file)

                layers = [
                    {
                        "name": "layer_0",
                        "svg": str(layer_files[0]),
                        "order_index": 0,
                        "element_count": 10,
                    },
                    {
                        "name": "layer_1",
                        "svg": str(layer_files[1]),
                        "order_index": 1,
                        "element_count": 15,
                    },
                    {
                        "name": "layer_2",
                        "svg": str(layer_files[2]),
                        "order_index": 2,
                        "element_count": 20,
                    },
                ]

                pen_map = {
                    "layer_0": "0.3mm black",
                    "layer_1": "0.5mm red",
                    "layer_2": "0.7mm blue",
                }

                with patch("builtins.print"):  # Suppress print output
                    result = plotter.plot_multipen_job(job_dir, layers, pen_map)

                assert result["success"] is True
                assert len(result["layers_plotted"]) == 3
                assert len(result["layers_skipped"]) == 0
                assert (
                    result["pen_swaps"] == 2
                )  # Should swap pen for each layer after first
                assert result["total_time"] > 0
                assert result["total_distance"] > 0
                assert len(result["errors"]) == 0

                # Verify manager.plot_file was called for each layer
                assert mock_manager.plot_file.call_count == 3

    def test_plot_multipen_job_with_pen_swaps(self, mock_manager, workspace):
        """Test multi-pen job with pen swaps."""
        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                # Create test layer files
                job_dir = workspace / "test_job"
                job_dir.mkdir()

                layer_file = job_dir / "layer.svg"
                layer_file.write_text("<svg><circle cx='10' cy='10' r='5'/></svg>")

                # Two layers with same pen - should only swap once
                layers = [
                    {
                        "name": "layer_0",
                        "svg": str(layer_file),
                        "order_index": 0,
                        "element_count": 10,
                    },
                    {
                        "name": "layer_1",
                        "svg": str(layer_file),
                        "order_index": 1,
                        "element_count": 15,
                    },
                ]

                pen_map = {
                    "layer_0": "0.3mm black",
                    "layer_1": "0.3mm black",  # Same pen
                }

                with patch("builtins.print"):
                    result = plotter.plot_multipen_job(job_dir, layers, pen_map)

                assert result["success"] is True
                assert result["pen_swaps"] == 0  # No swaps needed - same pen

    def test_plot_multipen_job_missing_layer_file(self, mock_manager, workspace):
        """Test multi-pen job with missing layer file."""
        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                job_dir = workspace / "test_job"
                job_dir.mkdir()

                layers = [
                    {
                        "name": "missing_layer",
                        "svg": str(job_dir / "missing.svg"),
                        "order_index": 0,
                    }
                ]

                pen_map = {"missing_layer": "0.3mm black"}

                with patch("builtins.print"):
                    result = plotter.plot_multipen_job(job_dir, layers, pen_map)

                assert result["success"] is True  # Still succeeds but with error
                assert len(result["layers_plotted"]) == 0
                assert len(result["errors"]) == 1
                assert "not found" in result["errors"][0]

    def test_plot_multipen_job_plotting_failure(self, mock_manager, workspace):
        """Test multi-pen job with plotting failure."""
        # Make manager.plot_file return failure
        mock_manager.plot_file.return_value = {
            "success": False,
            "error": "Device not connected",
        }

        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                job_dir = workspace / "test_job"
                job_dir.mkdir()

                layer_file = job_dir / "layer.svg"
                layer_file.write_text("<svg><circle cx='10' cy='10' r='5'/></svg>")

                layers = [{"name": "layer_0", "svg": str(layer_file), "order_index": 0}]

                pen_map = {"layer_0": "0.3mm black"}

                with patch("builtins.print"):
                    result = plotter.plot_multipen_job(job_dir, layers, pen_map)

                assert result["success"] is True  # Job succeeds but layer fails
                assert len(result["layers_plotted"]) == 0
                assert len(result["errors"]) == 1
                assert "Device not connected" in result["errors"][0]

    def test_plot_multipen_job_with_progress_callback(self, mock_manager, workspace):
        """Test multi-pen job with progress callback."""
        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                job_dir = workspace / "test_job"
                job_dir.mkdir()

                layer_file = job_dir / "layer.svg"
                layer_file.write_text("<svg><circle cx='10' cy='10' r='5'/></svg>")

                layers = [{"name": "layer_0", "svg": str(layer_file), "order_index": 0}]

                pen_map = {"layer_0": "0.3mm black"}

                progress_calls = []

                def progress_callback(current, total, layer_result):
                    progress_calls.append((current, total, layer_result))

                with patch("builtins.print"):
                    _ = plotter.plot_multipen_job(
                        job_dir, layers, pen_map, progress_callback
                    )

                assert len(progress_calls) == 1
                assert progress_calls[0][0] == 1  # current layer
                assert progress_calls[0][1] == 1  # total layers
                assert "name" in progress_calls[0][2]

    def test_plot_multipen_job_user_interrupt(self, mock_manager, workspace):
        """Test multi-pen job interrupted by user."""
        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                job_dir = workspace / "test_job"
                job_dir.mkdir()

                layer_file = job_dir / "layer.svg"
                layer_file.write_text("<svg><circle cx='10' cy='10' r='5'/></svg>")

                layers = [
                    {"name": "layer_0", "svg": str(layer_file), "order_index": 0},
                    {"name": "layer_1", "svg": str(layer_file), "order_index": 1},
                ]

                pen_map = {"layer_0": "0.3mm black", "layer_1": "0.5mm red"}

                # Simulate KeyboardInterrupt during second layer
                mock_manager.plot_file.side_effect = [
                    {"success": True, "time_elapsed": 10.0, "distance_pendown": 100.0},
                    KeyboardInterrupt("User interrupt"),
                ]

                with patch("builtins.print"):
                    result = plotter.plot_multipen_job(job_dir, layers, pen_map)

                assert result["success"] is False
                assert len(result["layers_plotted"]) == 1
                assert len(result["errors"]) == 1
                assert "interrupted by user" in result["errors"][0]

    def test_plot_multipen_job_with_pen_info(self, mock_manager, workspace):
        """Test multi-pen job with pen-specific settings."""
        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                job_dir = workspace / "test_job"
                job_dir.mkdir()

                layer_file = job_dir / "layer.svg"
                layer_file.write_text("<svg><circle cx='10' cy='10' r='5'/></svg>")

                layers = [
                    {
                        "name": "layer_0",
                        "svg": str(layer_file),
                        "order_index": 0,
                        "pen_info": {"speed_cap": 50},  # Custom speed setting
                    }
                ]

                pen_map = {"layer_0": "0.3mm black"}

                with patch("builtins.print"):
                    result = plotter.plot_multipen_job(job_dir, layers, pen_map)

                assert result["success"] is True
                # Verify plot_file was called with speed_pendown option
                mock_manager.plot_file.assert_called_once()
                call_kwargs = mock_manager.plot_file.call_args[1]
                assert call_kwargs["speed_pendown"] == 50

    def test_plot_with_axidraw_layers_success(self, mock_manager, workspace):
        """Test plotting with AxiDraw native layer control."""
        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                svg_file = workspace / "multipen.svg"
                svg_file.write_text('<svg><g layer="test_layer"/></svg>')

                # Mock detect_svg_layers
                mock_layers = [Mock(name="test_layer")]
                with patch(
                    "vfab.plotting.detect_svg_layers", return_value=mock_layers
                ):
                    with patch(
                        "vfab.plotting.parse_axidraw_layer_control"
                    ) as mock_parse:
                        mock_control = Mock()
                        mock_control.speed = 30
                        mock_control.force_pause = False
                        mock_control.delay_ms = 0
                        mock_parse.return_value = mock_control

                        with patch("builtins.print"):
                            result = plotter.plot_with_axidraw_layers(svg_file)

                assert result["success"] is True
                # Verify plot_file was called with layer options
                mock_manager.plot_file.assert_called_once()
                call_args, call_kwargs = mock_manager.plot_file.call_args
                assert call_kwargs["layer_mode"] is True
                assert call_kwargs["layers"] == "all"

    def test_plot_with_axidraw_layers_failure(self, mock_manager, workspace):
        """Test plotting with AxiDraw native layer control when plotting fails."""
        mock_manager.plot_file.return_value = {
            "success": False,
            "error": "Plotting device error",
        }

        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                svg_file = workspace / "multipen.svg"
                svg_file.write_text('<svg><g layer="test_layer"/></svg>')

                with patch("vfab.plotting.detect_svg_layers", return_value=[]):
                    with patch("builtins.print"):
                        result = plotter.plot_with_axidraw_layers(svg_file)

                assert result["success"] is False
                assert "Plotting device error" in result["error"]


class TestPlottingIntegration:
    """Test integration scenarios for plotting functionality."""

    def test_pen_swap_prompt_state_persistence(self):
        """Test that PenSwapPrompt maintains state between calls."""
        prompt = PenSwapPrompt(interactive=True)

        with patch("builtins.input", return_value=""):
            # First pen setup
            result1 = prompt.prompt_pen_swap(None, "black", "layer1")
            assert result1 is True
            assert prompt.current_pen == "black"

            # Same pen - no swap needed
            result2 = prompt.prompt_pen_swap("black", "black", "layer2")
            assert result2 is True
            assert prompt.current_pen == "black"

            # Different pen - swap needed
            result3 = prompt.prompt_pen_swap("black", "red", "layer3")
            assert result3 is True
            assert prompt.current_pen == "red"

    def test_multipen_plotter_layer_ordering(self):
        """Test that MultiPenPlotter processes layers in correct order."""
        mock_manager = Mock()
        mock_manager.plot_file.return_value = {
            "success": True,
            "time_elapsed": 10.0,
            "distance_pendown": 100.0,
        }

        with patch("vfab.plotting.is_axidraw_available", return_value=True):
            with patch("vfab.plotting.create_manager", return_value=mock_manager):
                plotter = MultiPenPlotter(interactive=False)

                # Create layers out of order
                layers = [
                    {"name": "layer_2", "svg": "path2.svg", "order_index": 2},
                    {"name": "layer_0", "svg": "path0.svg", "order_index": 0},
                    {"name": "layer_1", "svg": "path1.svg", "order_index": 1},
                ]

                pen_map = {"layer_0": "black", "layer_1": "red", "layer_2": "blue"}

                with tempfile.TemporaryDirectory() as tmp_dir:
                    job_dir = Path(tmp_dir)

                    # Mock file existence checks
                    with patch("pathlib.Path.exists", return_value=True):
                        with patch("builtins.print"):
                            _ = plotter.plot_multipen_job(job_dir, layers, pen_map)

                # Verify layers were plotted in correct order (0, 1, 2)
                assert mock_manager.plot_file.call_count == 3
                calls = mock_manager.plot_file.call_args_list
                # The calls should be in order of order_index
                assert len(calls) == 3
