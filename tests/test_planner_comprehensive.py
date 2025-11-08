"""
Comprehensive tests for planner.py layer planning functionality.
"""

from __future__ import annotations
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from plotty.planner import plan_layers, plan_axidraw_layers


class TestPlanLayers:
    """Test plan_layers function functionality."""

    @pytest.fixture
    def workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def sample_svg(self, workspace):
        """Create a sample SVG file for testing."""
        svg_file = workspace / "test.svg"
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <g layer="layer1">
        <circle cx="50" cy="50" r="10" fill="none" stroke="black"/>
    </g>
    <g layer="layer2">
        <rect x="10" y="10" width="30" height="30" fill="none" stroke="red"/>
    </g>
</svg>'''
        svg_file.write_text(svg_content)
        return svg_file

    def test_plan_layers_basic_functionality(self, workspace, sample_svg):
        """Test basic layer planning functionality with minimal mocking."""
        # Create mock layers
        mock_layer1 = Mock()
        mock_layer1.name = "layer1"
        mock_layer1.order_index = 0
        mock_layer1.elements = [Mock(), Mock()]
        
        mock_layer2 = Mock()
        mock_layer2.name = "layer2"
        mock_layer2.order_index = 1
        mock_layer2.elements = [Mock()]
        
        mock_layers = [mock_layer1, mock_layer2]
        
        with patch('plotty.planner.detect_svg_layers', return_value=mock_layers):
            with patch('plotty.planner.extract_layers_to_files', return_value=mock_layers):
                with patch('plotty.planner.load_preset') as mock_load_preset:
                    with patch('plotty.planner.features') as mock_features:
                        with patch('plotty.planner.estimate_seconds', return_value=10.0):
                            with patch('plotty.planner.run_vpype'):
                                with patch('plotty.planner.create_multipen_svg'):
                                    with patch('plotty.planner.save_pen_mapping'):
                                        # Mock preset
                                        mock_preset = Mock()
                                        mock_preset.format.return_value = "vpype_command"
                                        mock_load_preset.return_value = mock_preset
                                        
                                        # Create a simple mock for features
                                        mock_feature = Mock()
                                        mock_feature.path_count = 1
                                        mock_feature.point_count = 100
                                        mock_features.return_value = mock_feature
                                        
                                        out_dir = workspace / "output"
                                        layers_dir = out_dir / "layers"
                                        layers_dir.mkdir(parents=True)
                                        
                                        # Create fake layer files to exist
                                        for i in range(2):
                                            layer_file = layers_dir / f"layer_{i:02d}.svg"
                                            layer_file.write_text(f"<svg><circle cx='{i*10}' cy='{i*10}' r='5'/></svg>")
                                            optimized_file = layers_dir / f"layer_{i:02d}_optimized.svg"
                                            optimized_file.write_text(f"<svg><rect x='{i*10}' y='{i*10}' width='10' height='10'/></svg>")
                                        
                                        result = plan_layers(
                                            src_svg=sample_svg,
                                            preset="test_preset",
                                            presets_file="test_presets.yaml",
                                            pen_map=None,
                                            out_dir=out_dir,
                                            interactive=False
                                        )
                                        
                                        assert result["layer_count"] == 2
                                        assert len(result["layers"]) == 2
                                        assert "pen_map" in result
                                        assert "estimates" in result
                                        assert "multipen_svg" in result
                                        assert "layer_files" in result

    def test_plan_layers_with_custom_pen_map(self, workspace, sample_svg):
        """Test layer planning with custom pen mapping."""
        mock_layer = Mock()
        mock_layer.name = "test_layer"
        mock_layer.order_index = 0
        mock_layer.elements = [Mock()]
        
        with patch('plotty.planner.detect_svg_layers', return_value=[mock_layer]):
            with patch('plotty.planner.extract_layers_to_files', return_value=[mock_layer]):
                with patch('plotty.planner.load_preset') as mock_load_preset:
                    with patch('plotty.planner.features') as mock_features:
                        with patch('plotty.planner.estimate_seconds', return_value=5.0):
                            with patch('plotty.planner.run_vpype'):
                                with patch('plotty.planner.create_multipen_svg'):
                                    with patch('plotty.planner.save_pen_mapping'):
                                        # Mock preset
                                        mock_preset = Mock()
                                        mock_preset.format.return_value = "vpype_command"
                                        mock_load_preset.return_value = mock_preset
                                        
                                        mock_feature = Mock()
                                        mock_feature.path_count = 1
                                        mock_feature.point_count = 50
                                        mock_features.return_value = mock_feature
                                        
                                        pen_map = {"test_layer": "0.5mm red"}
                                        out_dir = workspace / "output"
                                        layers_dir = out_dir / "layers"
                                        layers_dir.mkdir(parents=True)
                                        
                                        # Create fake layer files
                                        layer_file = layers_dir / "layer_00.svg"
                                        layer_file.write_text("<svg><circle cx='10' cy='10' r='5'/></svg>")
                                        optimized_file = layers_dir / "layer_00_optimized.svg"
                                        optimized_file.write_text("<svg><rect x='10' y='10' width='10' height='10'/></svg>")
                                        
                                        result = plan_layers(
                                            src_svg=sample_svg,
                                            preset="test_preset",
                                            presets_file="test_presets.yaml",
                                            pen_map=pen_map,
                                            out_dir=out_dir,
                                            interactive=False
                                        )
                                        
                                        assert result["pen_map"] == pen_map
                                        assert result["layers"][0]["pen"] == "0.5mm red"

    def test_plan_layers_interactive_mode(self, workspace, sample_svg):
        """Test layer planning in interactive mode."""
        mock_layer = Mock()
        mock_layer.name = "interactive_layer"
        mock_layer.order_index = 0
        mock_layer.elements = [Mock()]
        
        with patch('plotty.planner.detect_svg_layers', return_value=[mock_layer]):
            with patch('plotty.planner.extract_layers_to_files', return_value=[mock_layer]):
                with patch('plotty.planner.load_preset') as mock_load_preset:
                    with patch('plotty.planner.features') as mock_features:
                        with patch('plotty.planner.estimate_seconds', return_value=8.0):
                            with patch('plotty.planner.run_vpype'):
                                with patch('plotty.planner.create_multipen_svg'):
                                    with patch('plotty.planner.create_pen_mapping_prompt') as mock_prompt:
                                        with patch('plotty.planner.save_pen_mapping'):
                                            # Mock preset
                                            mock_preset = Mock()
                                            mock_preset.format.return_value = "vpype_command"
                                            mock_load_preset.return_value = mock_preset
                                            
                                            mock_feature = Mock()
                                            mock_feature.path_count = 1
                                            mock_feature.point_count = 75
                                            mock_features.return_value = mock_feature
                                            
                                            interactive_pen_map = {"interactive_layer": "0.3mm black"}
                                            mock_prompt.return_value = interactive_pen_map
                                            
                                            available_pens = [{"name": "0.3mm black", "type": "fineliner"}]
                                            
                                            out_dir = workspace / "output"
                                            result = plan_layers(
                                                src_svg=sample_svg,
                                                preset="test_preset",
                                                presets_file="test_presets.yaml",
                                                pen_map=None,
                                                out_dir=out_dir,
                                                available_pens=available_pens,
                                                interactive=True
                                            )
                                            
                                            mock_prompt.assert_called_once_with([mock_layer], available_pens)
                                            assert result["pen_map"] == interactive_pen_map

    def test_plan_layers_with_available_pens(self, workspace, sample_svg):
        """Test layer planning with available pens information."""
        mock_layer = Mock()
        mock_layer.name = "pen_info_layer"
        mock_layer.order_index = 0
        mock_layer.elements = [Mock()]
        
        with patch('plotty.planner.detect_svg_layers', return_value=[mock_layer]):
            with patch('plotty.planner.extract_layers_to_files', return_value=[mock_layer]):
                with patch('plotty.planner.load_preset') as mock_load_preset:
                    with patch('plotty.planner.features') as mock_features:
                        with patch('plotty.planner.estimate_seconds', return_value=12.0):
                            with patch('plotty.planner.run_vpype'):
                                with patch('plotty.planner.create_multipen_svg'):
                                    with patch('plotty.planner.save_pen_mapping'):
                                        # Mock preset
                                        mock_preset = Mock()
                                        mock_preset.format.return_value = "vpype_command"
                                        mock_load_preset.return_value = mock_preset
                                        
                                        mock_feature = Mock()
                                        mock_feature.path_count = 1
                                        mock_feature.point_count = 100
                                        mock_features.return_value = mock_feature
                                        
                                        pen_map = {"pen_info_layer": "0.5mm red"}
                                        available_pens = [
                                            {"name": "0.5mm red", "type": "fineliner", "speed_cap": 40}
                                        ]
                                        
                                        out_dir = workspace / "output"
                                        layers_dir = out_dir / "layers"
                                        layers_dir.mkdir(parents=True)
                                        
                                        # Create fake layer files
                                        layer_file = layers_dir / "layer_00.svg"
                                        layer_file.write_text("<svg><circle cx='10' cy='10' r='5'/></svg>")
                                        optimized_file = layers_dir / "layer_00_optimized.svg"
                                        optimized_file.write_text("<svg><rect x='10' y='10' width='10' height='10'/></svg>")
                                        
                                        result = plan_layers(
                                            src_svg=sample_svg,
                                            preset="test_preset",
                                            presets_file="test_presets.yaml",
                                            pen_map=pen_map,
                                            out_dir=out_dir,
                                            available_pens=available_pens,
                                            interactive=False
                                        )
                                        
                                        layer_pen_info = result["layers"][0]["pen_info"]
                                        assert layer_pen_info["name"] == "0.5mm red"
                                        assert layer_pen_info["speed_cap"] == 40

    def test_plan_layers_missing_files(self, workspace, sample_svg):
        """Test layer planning when layer files are missing."""
        mock_layer = Mock()
        mock_layer.name = "missing_layer"
        mock_layer.order_index = 0
        mock_layer.elements = [Mock()]
        
        with patch('plotty.planner.detect_svg_layers', return_value=[mock_layer]):
            with patch('plotty.planner.extract_layers_to_files', return_value=[mock_layer]):
                with patch('plotty.planner.load_preset') as mock_load_preset:
                    with patch('plotty.planner.run_vpype'):
                        with patch('plotty.planner.create_multipen_svg'):
                            with patch('plotty.planner.save_pen_mapping'):
                                # Mock preset
                                mock_preset = Mock()
                                mock_preset.format.return_value = "vpype_command"
                                mock_load_preset.return_value = mock_preset
                                
                                out_dir = workspace / "output"
                                result = plan_layers(
                                    src_svg=sample_svg,
                                    preset="test_preset",
                                    presets_file="test_presets.yaml",
                                    pen_map=None,
                                    out_dir=out_dir,
                                    interactive=False
                                )
                                
                                # Should have no processed layers since files don't exist
                                assert result["layer_count"] == 0
                                assert len(result["layers"]) == 0

    def test_plan_layers_time_estimates(self, workspace, sample_svg):
        """Test layer planning time estimation calculations."""
        mock_layer1 = Mock()
        mock_layer1.name = "layer1"
        mock_layer1.order_index = 0
        mock_layer1.elements = [Mock()]
        
        mock_layer2 = Mock()
        mock_layer2.name = "layer2"
        mock_layer2.order_index = 1
        mock_layer2.elements = [Mock()]
        
        with patch('plotty.planner.detect_svg_layers', return_value=[mock_layer1, mock_layer2]):
            with patch('plotty.planner.extract_layers_to_files', return_value=[mock_layer1, mock_layer2]):
                with patch('plotty.planner.load_preset') as mock_load_preset:
                    with patch('plotty.planner.features') as mock_features:
                        with patch('plotty.planner.estimate_seconds') as mock_estimate:
                            with patch('plotty.planner.run_vpype'):
                                with patch('plotty.planner.create_multipen_svg'):
                                    with patch('plotty.planner.save_pen_mapping'):
                                        # Mock preset
                                        mock_preset = Mock()
                                        mock_preset.format.return_value = "vpype_command"
                                        mock_load_preset.return_value = mock_preset
                                        
                                        mock_feature = Mock()
                                        mock_feature.path_count = 1
                                        mock_feature.point_count = 100
                                        mock_features.return_value = mock_feature
                                        
                                        # Different pre/post estimates for each layer
                                        mock_estimate.side_effect = [20.0, 15.0, 25.0, 18.0]
                                        
                                        out_dir = workspace / "output"
                                        layers_dir = out_dir / "layers"
                                        layers_dir.mkdir(parents=True)
                                        
                                        # Create fake layer files
                                        for i in range(2):
                                            layer_file = layers_dir / f"layer_{i:02d}.svg"
                                            layer_file.write_text(f"<svg><circle cx='{i*10}' cy='{i*10}' r='5'/></svg>")
                                            optimized_file = layers_dir / f"layer_{i:02d}_optimized.svg"
                                            optimized_file.write_text(f"<svg><rect x='{i*10}' y='{i*10}' width='10' height='10'/></svg>")
                                        
                                        result = plan_layers(
                                            src_svg=sample_svg,
                                            preset="test_preset",
                                            presets_file="test_presets.yaml",
                                            pen_map=None,
                                            out_dir=out_dir,
                                            interactive=False
                                        )
                                        
                                        estimates = result["estimates"]
                                        assert estimates["pre_s"] == 45.0  # 20.0 + 25.0
                                        assert estimates["post_s"] == 33.0  # 15.0 + 18.0
                                        
                                        # Check time saved calculation
                                        expected_time_saved = ((45.0 - 33.0) / 45.0) * 100
                                        assert estimates["time_saved_percent"] == round(expected_time_saved, 1)

    def test_plan_layers_output_directory_creation(self, workspace, sample_svg):
        """Test that output directory is created properly."""
        mock_layer = Mock()
        mock_layer.name = "dir_test_layer"
        mock_layer.order_index = 0
        mock_layer.elements = [Mock()]
        
        with patch('plotty.planner.detect_svg_layers', return_value=[mock_layer]):
            with patch('plotty.planner.extract_layers_to_files', return_value=[mock_layer]):
                with patch('plotty.planner.load_preset') as mock_load_preset:
                    with patch('plotty.planner.features') as mock_features:
                        with patch('plotty.planner.estimate_seconds', return_value=10.0):
                            with patch('plotty.planner.run_vpype'):
                                with patch('plotty.planner.create_multipen_svg'):
                                    with patch('plotty.planner.save_pen_mapping'):
                                        # Mock preset
                                        mock_preset = Mock()
                                        mock_preset.format.return_value = "vpype_command"
                                        mock_load_preset.return_value = mock_preset
                                        
                                        mock_feature = Mock()
                                        mock_feature.path_count = 1
                                        mock_feature.point_count = 100
                                        mock_features.return_value = mock_feature
                                        
                                        # Use nested directory that doesn't exist
                                        out_dir = workspace / "nested" / "output" / "dir"
                                        
                                        result = plan_layers(
                                            src_svg=sample_svg,
                                            preset="test_preset",
                                            presets_file="test_presets.yaml",
                                            pen_map=None,
                                            out_dir=out_dir,
                                            interactive=False
                                        )
                                        
                                        # Directory should be created
                                        assert out_dir.exists()
                                        assert "layer_count" in result


class TestPlanAxiDrawLayers:
    """Test plan_axidraw_layers function functionality."""

    @pytest.fixture
    def workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def sample_svg(self, workspace):
        """Create a sample SVG file for testing."""
        svg_file = workspace / "test.svg"
        svg_file.write_text('<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="10"/></svg>')
        return svg_file

    def test_plan_axidraw_layers_no_axidraw_available(self, workspace, sample_svg):
        """Test AxiDraw layer planning when AxiDraw is not available."""
        with patch('plotty.planner.create_manager', None):
            with pytest.raises(ImportError, match="AxiDraw support not available"):
                plan_axidraw_layers(
                    src_svg=sample_svg,
                    preset="test_preset",
                    presets_file="test_presets.yaml",
                    pen_map={"layer1": "0.3mm black"},
                    out_dir=workspace / "output"
                )

    def test_plan_axidraw_layers_success(self, workspace, sample_svg):
        """Test successful AxiDraw layer planning."""
        mock_manager = Mock()
        mock_manager.plot_file.return_value = {
            "success": True,
            "time_estimate": 30.0,
            "distance_pendown": 500.0
        }
        
        with patch('plotty.planner.create_manager', return_value=mock_manager):
            with patch('plotty.planner.plan_layers') as mock_plan_layers:
                plan_result = {
                    "layers": [
                        {"name": "layer1", "svg": "layer1.svg", "estimates": {"post_s": 25.0}},
                        {"name": "layer2", "svg": "layer2.svg", "estimates": {"post_s": 20.0}}
                    ],
                    "pen_map": {"layer1": "0.3mm black", "layer2": "0.5mm red"},
                    "estimates": {"pre_s": 50.0, "post_s": 45.0, "time_saved_percent": 10.0},
                    "layer_count": 2,
                    "multipen_svg": "multipen.svg",
                    "layer_files": ["layer1.svg", "layer2.svg"]
                }
                mock_plan_layers.return_value = plan_result
                
                out_dir = workspace / "output"
                result = plan_axidraw_layers(
                    src_svg=sample_svg,
                    preset="test_preset",
                    presets_file="test_presets.yaml",
                    pen_map={"layer1": "0.3mm black", "layer2": "0.5mm red"},
                    out_dir=out_dir,
                    port="/dev/ttyUSB0",
                    model=2
                )
                
                # Check that plan_layers was called
                mock_plan_layers.assert_called_once()
                
                # Check AxiDraw-specific additions
                assert "axidraw" in result
                assert result["axidraw"]["port"] == "/dev/ttyUSB0"
                assert result["axidraw"]["model"] == 2
                
                # Check enhanced estimates
                assert result["estimates"]["axidraw_s"] == 60.0  # 30.0 + 30.0
                assert result["axidraw"]["total_distance_mm"] == 1000.0  # 500.0 + 500.0
                
                # Check layer-specific AxiDraw estimates
                assert result["layers"][0]["axidraw_est"] == 30.0
                assert result["layers"][0]["distance_mm"] == 500.0
                assert result["layers"][1]["axidraw_est"] == 30.0
                assert result["layers"][1]["distance_mm"] == 500.0

    def test_plan_axidraw_layers_plot_failure(self, workspace, sample_svg):
        """Test AxiDraw layer planning when plot_file fails."""
        mock_manager = Mock()
        mock_manager.plot_file.return_value = {
            "success": False,
            "error": "Device not connected"
        }
        
        with patch('plotty.planner.create_manager', return_value=mock_manager):
            with patch('plotty.planner.plan_layers') as mock_plan_layers:
                plan_result = {
                    "layers": [
                        {"name": "layer1", "svg": "layer1.svg", "estimates": {"post_s": 25.0}}
                    ],
                    "pen_map": {"layer1": "0.3mm black"},
                    "estimates": {"pre_s": 30.0, "post_s": 25.0, "time_saved_percent": 16.7},
                    "layer_count": 1,
                    "multipen_svg": "multipen.svg",
                    "layer_files": ["layer1.svg"]
                }
                mock_plan_layers.return_value = plan_result
                
                out_dir = workspace / "output"
                result = plan_axidraw_layers(
                    src_svg=sample_svg,
                    preset="test_preset",
                    presets_file="test_presets.yaml",
                    pen_map={"layer1": "0.3mm black"},
                    out_dir=out_dir
                )
                
                # Should fallback to post_s estimates when plot_file fails
                assert result["layers"][0]["axidraw_est"] == 25.0  # Fallback to post_s
                assert result["layers"][0]["distance_mm"] == 0

    def test_plan_axidraw_layers_with_options(self, workspace, sample_svg):
        """Test AxiDraw layer planning with additional options."""
        mock_manager = Mock()
        mock_manager.plot_file.return_value = {
            "success": True,
            "time_estimate": 15.0,
            "distance_pendown": 250.0
        }
        
        with patch('plotty.planner.create_manager', return_value=mock_manager):
            with patch('plotty.planner.plan_layers') as mock_plan_layers:
                plan_result = {
                    "layers": [
                        {"name": "layer1", "svg": "layer1.svg", "estimates": {"post_s": 20.0}}
                    ],
                    "pen_map": {"layer1": "0.3mm black"},
                    "estimates": {"pre_s": 25.0, "post_s": 20.0, "time_saved_percent": 20.0},
                    "layer_count": 1,
                    "multipen_svg": "multipen.svg",
                    "layer_files": ["layer1.svg"]
                }
                mock_plan_layers.return_value = plan_result
                
                out_dir = workspace / "output"
                result = plan_axidraw_layers(
                    src_svg=sample_svg,
                    preset="test_preset",
                    presets_file="test_presets.yaml",
                    pen_map={"layer1": "0.3mm black"},
                    out_dir=out_dir,
                    speed_pendown=50,
                    speed_penup=75,
                    custom_option="test_value"
                )
                
                # Check that options were passed to plot_file
                mock_manager.plot_file.assert_called_with(
                    "layer1.svg",
                    preview_only=True,
                    speed_pendown=50,
                    speed_penup=75,
                    custom_option="test_value"
                )
                
                # Check options are stored in result
                assert result["axidraw"]["options"]["speed_pendown"] == 50
                assert result["axidraw"]["options"]["speed_penup"] == 75
                assert result["axidraw"]["options"]["custom_option"] == "test_value"

    def test_plan_axidraw_layers_preserves_all_data(self, workspace, sample_svg):
        """Test that AxiDraw planning preserves all plan_layers data."""
        mock_manager = Mock()
        mock_manager.plot_file.return_value = {
            "success": True,
            "time_estimate": 20.0,
            "distance_pendown": 300.0
        }
        
        with patch('plotty.planner.create_manager', return_value=mock_manager):
            with patch('plotty.planner.plan_layers') as mock_plan_layers:
                plan_result = {
                    "layers": [
                        {
                            "name": "layer1",
                            "svg": "layer1.svg",
                            "pen": "0.3mm black",
                            "pen_info": {"type": "fineliner"},
                            "order_index": 0,
                            "element_count": 5,
                            "estimates": {"pre_s": 25.0, "post_s": 20.0},
                            "features": {"pre": {"path_count": 1}, "post": {"path_count": 1}}
                        }
                    ],
                    "layer_count": 1,
                    "pen_map": {"layer1": "0.3mm black"},
                    "estimates": {"pre_s": 25.0, "post_s": 20.0, "time_saved_percent": 20.0},
                    "multipen_svg": "multipen.svg",
                    "layer_files": ["layer_00.svg"]
                }
                mock_plan_layers.return_value = plan_result
                
                out_dir = workspace / "output"
                result = plan_axidraw_layers(
                    src_svg=sample_svg,
                    preset="test_preset",
                    presets_file="test_presets.yaml",
                    pen_map={"layer1": "0.3mm black"},
                    out_dir=out_dir
                )
                
                # Check that all original data is preserved
                assert result["layer_count"] == 1
                assert result["pen_map"] == {"layer1": "0.3mm black"}
                assert result["multipen_svg"] == "multipen.svg"
                assert result["layer_files"] == ["layer_00.svg"]
                
                # Check layer data preservation
                layer = result["layers"][0]
                assert layer["name"] == "layer1"
                assert layer["pen"] == "0.3mm black"
                assert layer["pen_info"]["type"] == "fineliner"
                assert layer["order_index"] == 0
                assert layer["element_count"] == 5
                assert layer["estimates"]["pre_s"] == 25.0
                assert layer["estimates"]["post_s"] == 20.0
                assert layer["features"]["pre"]["path_count"] == 1
                
                # Check AxiDraw additions
                assert layer["axidraw_est"] == 20.0
                assert layer["distance_mm"] == 300.0