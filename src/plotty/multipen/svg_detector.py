"""
SVG layer detection and extraction functionality.
"""

from __future__ import annotations
from defusedxml import ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree
from pathlib import Path
from typing import List
import re

from .types import LayerInfo


def detect_svg_layers(svg_path: Path) -> List[LayerInfo]:
    """Detect layers in an SVG file.

    Args:
        svg_path: Path to SVG file

    Returns:
        List of LayerInfo objects representing detected layers
    """
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG file not found: {svg_path}")

    # Parse SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()

    if root is None:
        raise ValueError(f"Could not parse SVG file: {svg_path}")

    # Handle XML namespaces
    namespaces = {
        "svg": "http://www.w3.org/2000/svg",
        "inkscape": "http://www.inkscape.org/namespaces/inkscape",
        "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",
    }

    layers = []

    # Method 1: Look for Inkscape layers (groups with inkscape:label)
    layer_groups = root.findall(".//svg:g[@inkscape:label]", namespaces)
    if layer_groups:
        for i, group in enumerate(layer_groups):
            layer_name = group.get(
                f"{{{namespaces['inkscape']}}}label", f"Layer {i + 1}"
            )

            # Check Inkscape visibility
            style = group.get("style", "")
            visible = True
            if "display:none" in style.replace(" ", ""):
                visible = False

            # Check Inkscape group style attribute for visibility
            inkscape_visibility = group.get(
                f"{{{namespaces['inkscape']}}}groupmode", "layer"
            )
            if inkscape_visibility == "hidden":
                visible = False

            # Extract layer color for visualization
            color = None
            # Try to get color from group style
            if "stroke:" in style:
                stroke_match = re.search(r"stroke:([^;]+)", style)
                if stroke_match:
                    color = stroke_match.group(1).strip()

            # Try to get color from inkscape:label color if available
            label_color = group.get(f"{{{namespaces['inkscape']}}}label-color")
            if label_color:
                color = label_color

            elements = list(
                group.findall(".//svg:path", namespaces)
                + group.findall(".//svg:line", namespaces)
                + group.findall(".//svg:rect", namespaces)
                + group.findall(".//svg:circle", namespaces)
                + group.findall(".//svg:ellipse", namespaces)
                + group.findall(".//svg:polygon", namespaces)
                + group.findall(".//svg:polyline", namespaces)
            )
            layers.append(LayerInfo(layer_name, elements, i, visible, color))

    # Method 2: Look for groups with id attributes
    else:
        groups = root.findall(".//svg:g[@id]", namespaces)
        if groups:
            for i, group in enumerate(groups):
                layer_name = group.get("id", f"Layer {i + 1}")

                # Check visibility for generic groups
                style = group.get("style", "")
                visible = True
                if "display:none" in style.replace(" ", ""):
                    visible = False

                # Extract color for visualization
                color = None
                if "stroke:" in style:
                    stroke_match = re.search(r"stroke:([^;]+)", style)
                    if stroke_match:
                        color = stroke_match.group(1).strip()

                elements = list(group)
                layers.append(LayerInfo(layer_name, elements, i, visible, color))

        # Method 3: No groups found, treat all elements as one layer
        else:
            all_elements = (
                root.findall(".//svg:path", namespaces)
                + root.findall(".//svg:line", namespaces)
                + root.findall(".//svg:rect", namespaces)
                + root.findall(".//svg:circle", namespaces)
                + root.findall(".//svg:ellipse", namespaces)
                + root.findall(".//svg:polygon", namespaces)
                + root.findall(".//svg:polyline", namespaces)
            )

            if all_elements:
                layers.append(LayerInfo("Layer 1", all_elements, 0, True, None))

    return layers


def extract_layers_to_files(svg_path: Path, output_dir: Path) -> List[LayerInfo]:
    """Extract layers to separate SVG files.

    Args:
        svg_path: Source SVG file
        output_dir: Directory to save layer files

    Returns:
        List of LayerInfo objects with file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse original SVG
    tree = ET.parse(svg_path)
    root = tree.getroot()

    if root is None:
        raise ValueError(f"Could not parse SVG file: {svg_path}")

    # Get dimensions and viewBox from original
    width = root.get("width", "100mm")
    height = root.get("height", "100mm")
    viewbox = root.get("viewBox")

    # Detect layers
    layers = detect_svg_layers(svg_path)

    for layer in layers:
        # Create new SVG for this layer
        layer_root = Element(
            "svg",
            {
                "width": width,
                "height": height,
                "viewBox": viewbox if viewbox else f"0 0 {width} {height}",
                "xmlns": "http://www.w3.org/2000/svg",
            },
        )

        # Add layer elements
        for element in layer.elements:
            layer_root.append(element)

        # Save layer file
        layer_file = output_dir / f"layer_{layer.order_index:02d}.svg"
        layer_tree = ElementTree(layer_root)
        layer_tree.write(layer_file, encoding="unicode", xml_declaration=True)

        # Store file path in layer info
        layer.stats["svg_file"] = str(layer_file)

    return layers


def display_layer_overview(layers: List[LayerInfo]) -> None:
    """Display a color-coded overview of detected layers.

    Args:
        layers: List of LayerInfo objects
    """
    print("\n" + "=" * 60)
    print("🎨 LAYER OVERVIEW")
    print("=" * 60)

    visible_layers = [layer for layer in layers if layer.visible]
    hidden_layers = [layer for layer in layers if not layer.visible]

    if visible_layers:
        print(f"\n📐 Visible layers ({len(visible_layers)}):")
        print("-" * 40)
        for i, layer in enumerate(visible_layers):
            color_indicator = ""
            if layer.color:
                # Simple color indicator using terminal colors
                color_map = {
                    "red": "🔴",
                    "blue": "🔵",
                    "green": "🟢",
                    "yellow": "🟡",
                    "black": "⚫",
                    "white": "⚪",
                    "purple": "🟣",
                    "orange": "🟠",
                    "cyan": "🔷",
                }
                color_lower = (
                    layer.color.lower()
                    .replace("#", "")
                    .replace("rgb", "")
                    .replace(" ", "")
                )
                color_indicator = color_map.get(color_lower, "🎨")

            print(f"  {i + 1:2d}. {color_indicator} {layer.name}")
            print(f"      Elements: {len(layer.elements)}")
            if layer.color:
                print(f"      Color: {layer.color}")

    if hidden_layers:
        print(f"\n🚫 Hidden layers ({len(hidden_layers)}) - will be skipped:")
        print("-" * 40)
        for i, layer in enumerate(hidden_layers):
            print(f"  {i + 1:2d}. 🚫 {layer.name}")
            print(f"      Elements: {len(layer.elements)}")

    print("\n" + "=" * 60)
