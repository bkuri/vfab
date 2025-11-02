"""
Multi-pen plotting support for ploTTY.

This package provides functionality for detecting SVG layers, mapping them to pens,
and generating multi-pen AxiDraw-compatible SVG files.
"""

from .types import LayerControl, LayerInfo
from .svg_detector import (
    detect_svg_layers,
    extract_layers_to_files,
    display_layer_overview,
)
from .pen_mapping import (
    create_pen_mapping_prompt,
    save_pen_mapping,
    load_pen_mapping,
    validate_pen_compatibility,
)
from .axidraw_integration import (
    parse_axidraw_layer_control,
    generate_layer_name,
    create_multipen_svg,
)

__all__ = [
    "LayerControl",
    "LayerInfo",
    "detect_svg_layers",
    "extract_layers_to_files",
    "display_layer_overview",
    "create_pen_mapping_prompt",
    "save_pen_mapping",
    "load_pen_mapping",
    "validate_pen_compatibility",
    "parse_axidraw_layer_control",
    "generate_layer_name",
    "create_multipen_svg",
]
