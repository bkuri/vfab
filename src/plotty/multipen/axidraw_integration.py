"""
AxiDraw-specific functionality for multi-pen plotting.
"""

from __future__ import annotations
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict
import re

from .types import LayerControl, LayerInfo


def parse_axidraw_layer_control(layer_name: str) -> LayerControl:
    """Parse AxiDraw layer control syntax from layer name.

    Args:
        layer_name: Raw layer name from SVG

    Returns:
        LayerControl object with parsed parameters
    """
    # Remove leading whitespace
    name = layer_name.lstrip()

    # Check for documentation layer (%)
    documentation_only = name.startswith("%")
    if documentation_only:
        name = name[1:].lstrip()

    # Check for force pause (!)
    force_pause = name.startswith("!")
    if force_pause:
        name = name[1:].lstrip()

    # Initialize parameters
    layer_number = None
    speed = None
    height = None
    delay_ms = None

    # Parse layer number (optional)
    number_match = re.match(r"^(\d+)", name)
    if number_match:
        layer_number = int(number_match.group(1))
        name = name[number_match.end() :].lstrip()

    # Parse control codes (+S, +H, +D)
    # These can appear in any order but only the last valid one of each type takes effect
    speed_matches = re.findall(r"\+S(\d+)", name, re.IGNORECASE)
    if speed_matches:
        speed_val = int(speed_matches[-1])
        speed = speed_val if 1 <= speed_val <= 100 else None

    height_matches = re.findall(r"\+H(\d+)", name, re.IGNORECASE)
    if height_matches:
        height_val = int(height_matches[-1])
        height = height_val if 0 <= height_val <= 100 else None

    delay_matches = re.findall(r"\+D(\d+)", name, re.IGNORECASE)
    if delay_matches:
        delay_val = int(delay_matches[-1])
        delay_ms = delay_val if delay_val >= 1 else None

    return LayerControl(
        layer_number=layer_number,
        speed=speed,
        height=height,
        delay_ms=delay_ms,
        force_pause=force_pause,
        documentation_only=documentation_only,
        original_name=layer_name,
    )


def generate_layer_name(control: LayerControl, display_name: str) -> str:
    """Generate layer name with AxiDraw control syntax.

    Args:
        control: Layer control parameters
        display_name: Human-readable layer name

    Returns:
        Layer name string with control codes
    """
    parts = []

    # Add documentation marker if needed
    if control.documentation_only:
        parts.append("%")

    # Add pause marker if needed
    if control.force_pause:
        parts.append("!")

    # Add layer number if specified
    if control.layer_number is not None:
        parts.append(str(control.layer_number))

    # Add control codes
    if control.speed is not None:
        parts.append(f"+S{control.speed}")

    if control.height is not None:
        parts.append(f"+H{control.height}")

    if control.delay_ms is not None:
        parts.append(f"+D{control.delay_ms}")

    # Add display name
    if display_name:
        parts.append(display_name)

    return " ".join(parts)


def create_multipen_svg(
    original_svg_path: Path,
    layers: List[LayerInfo],
    pen_map: Dict[str, str],
    output_path: Path,
    available_pens: List[Dict],
) -> None:
    """Create a multi-pen SVG with AxiDraw layer control syntax.

    Args:
        original_svg_path: Path to original SVG file
        layers: List of layer information
        pen_map: Layer name to pen name mapping
        output_path: Output SVG file path
        available_pens: List of available pens with their properties
    """
    # Parse original SVG to get structure
    tree = ET.parse(original_svg_path)
    root = tree.getroot()

    # Create pen lookup
    pen_by_name = {pen["name"]: pen for pen in available_pens}

    # Copy SVG attributes
    new_root = ET.Element(
        "svg",
        {
            "width": root.get("width", "100mm"),
            "height": root.get("height", "100mm"),
            "viewBox": root.get("viewBox", "0 0 100 100"),
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:inkscape": "http://www.inkscape.org/namespaces/inkscape",
        },
    )

    # Sort layers by order_index
    sorted_layers = sorted(layers, key=lambda layer: layer.order_index)

    for i, layer in enumerate(sorted_layers):
        if not layer.elements:
            continue

        # Get pen for this layer
        pen_name = pen_map.get(
            layer.name, list(pen_map.values())[0] if pen_map else "0.3mm black"
        )
        pen = pen_by_name.get(pen_name, {})

        # Create layer control
        control = LayerControl(
            layer_number=i + 1,  # AxiDraw layers 1-1000
            speed=pen.get("speed_cap"),
            height=None,  # Could be derived from pen pressure
            delay_ms=None,
            force_pause=True,  # Always pause for pen swap
            documentation_only=False,
            original_name=layer.name,
        )

        # Generate layer name with control syntax
        layer_name = generate_layer_name(control, f"{layer.name} ({pen_name})")

        # Create layer group
        layer_group = ET.SubElement(
            new_root,
            "g",
            {
                "inkscape:groupmode": "layer",
                "inkscape:label": layer_name,
                "id": f"layer_{i:02d}",
            },
        )

        # Add layer elements
        for element in layer.elements:
            layer_group.append(element)

    # Save the multi-pen SVG
    tree = ET.ElementTree(new_root)
    tree.write(output_path, encoding="unicode", xml_declaration=True)
