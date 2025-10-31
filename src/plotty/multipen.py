from __future__ import annotations
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional, NamedTuple
import json
import re


class LayerControl(NamedTuple):
    """AxiDraw layer control parameters parsed from layer name."""

    layer_number: Optional[int]
    speed: Optional[int]  # +S parameter (1-100)
    height: Optional[int]  # +H parameter (0-100)
    delay_ms: Optional[int]  # +D parameter (>=1)
    force_pause: bool  # ! parameter
    documentation_only: bool  # % parameter
    original_name: str


class LayerInfo:
    """Represents a single layer in an SVG file."""

    def __init__(self, name: str, elements: List[ET.Element], order_index: int):
        self.name = name
        self.elements = elements
        self.order_index = order_index
        self.pen_id: Optional[int] = None
        self.stats: Dict = {}

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "order_index": self.order_index,
            "pen_id": self.pen_id,
            "element_count": len(self.elements),
            "stats": self.stats,
        }


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
            elements = list(
                group.findall(".//svg:path", namespaces)
                + group.findall(".//svg:line", namespaces)
                + group.findall(".//svg:rect", namespaces)
                + group.findall(".//svg:circle", namespaces)
                + group.findall(".//svg:ellipse", namespaces)
                + group.findall(".//svg:polygon", namespaces)
                + group.findall(".//svg:polyline", namespaces)
            )
            layers.append(LayerInfo(layer_name, elements, i))

    # Method 2: Look for groups with id attributes
    else:
        groups = root.findall(".//svg:g[@id]", namespaces)
        if groups:
            for i, group in enumerate(groups):
                layer_name = group.get("id", f"Layer {i + 1}")
                elements = list(group)
                layers.append(LayerInfo(layer_name, elements, i))

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
                layers.append(LayerInfo("Layer 1", all_elements, 0))

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

    # Get dimensions and viewBox from original
    width = root.get("width", "100mm")
    height = root.get("height", "100mm")
    viewbox = root.get("viewBox")

    # Detect layers
    layers = detect_svg_layers(svg_path)

    for layer in layers:
        # Create new SVG for this layer
        layer_root = ET.Element(
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
        layer_tree = ET.ElementTree(layer_root)
        layer_tree.write(layer_file, encoding="unicode", xml_declaration=True)

        # Store file path in layer info
        layer.stats["svg_file"] = str(layer_file)

    return layers


def create_pen_mapping_prompt(
    layers: List[LayerInfo], available_pens: List[Dict]
) -> Dict[str, str]:
    """Create interactive prompt for pen mapping.

    Args:
        layers: List of detected layers
        available_pens: List of available pens from database

    Returns:
        Dictionary mapping layer names to pen names
    """
    print("\n=== Multi-Pen Layer Mapping ===")
    print(f"Detected {len(layers)} layer(s):")

    for i, layer in enumerate(layers):
        print(f"  {i + 1}. {layer.name} ({len(layer.elements)} elements)")

    print("\nAvailable pens:")
    for i, pen in enumerate(available_pens):
        print(f"  {i + 1}. {pen['name']} ({pen.get('width_mm', 'unknown')}mm)")

    pen_map = {}

    for layer in layers:
        print(f"\nLayer: {layer.name}")
        print("Select pen (enter number or pen name):")

        while True:
            choice = input("> ").strip()

            # Try to parse as number
            try:
                pen_index = int(choice) - 1
                if 0 <= pen_index < len(available_pens):
                    selected_pen = available_pens[pen_index]
                    pen_map[layer.name] = selected_pen["name"]
                    print(f"  ✓ Mapped {layer.name} → {selected_pen['name']}")
                    break
                else:
                    print("  Invalid selection, try again")
                    continue
            except ValueError:
                # Try to match by name
                matching_pens = [
                    p for p in available_pens if p["name"].lower() == choice.lower()
                ]
                if matching_pens:
                    pen_map[layer.name] = matching_pens[0]["name"]
                    print(f"  ✓ Mapped {layer.name} → {matching_pens[0]['name']}")
                    break
                else:
                    print("  Pen not found, try again")
                    continue

    return pen_map


def save_pen_mapping(job_dir: Path, pen_map: Dict[str, str]) -> None:
    """Save pen mapping to job directory.

    Args:
        job_dir: Job directory path
        pen_map: Layer to pen mapping
    """
    mapping_file = job_dir / "pen_mapping.json"
    with open(mapping_file, "w") as f:
        json.dump(pen_map, f, indent=2)


def load_pen_mapping(job_dir: Path) -> Optional[Dict[str, str]]:
    """Load pen mapping from job directory.

    Args:
        job_dir: Job directory path

    Returns:
        Pen mapping dictionary or None if not found
    """
    mapping_file = job_dir / "pen_mapping.json"
    if mapping_file.exists():
        with open(mapping_file, "r") as f:
            return json.load(f)
    return None


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


def validate_pen_compatibility(layer: LayerInfo, pen: Dict) -> bool:
    """Validate if a pen is suitable for a layer.

    Args:
        layer: Layer information
        pen: Pen information

    Returns:
        True if pen is compatible, False otherwise
    """
    # Basic validation - can be extended with more sophisticated rules
    element_count = len(layer.elements)

    # Check if pen has speed limits that might be problematic
    speed_cap = pen.get("speed_cap", None)
    if speed_cap and speed_cap < 10 and element_count > 1000:
        print(
            f"  ⚠ Warning: {pen['name']} has low speed cap but layer has many elements"
        )
        return False

    return True
