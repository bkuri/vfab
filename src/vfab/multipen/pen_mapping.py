"""
Interactive pen mapping and persistence functionality.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Optional
import json

from .types import LayerInfo


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

    # Count visible layers
    visible_layers = [layer for layer in layers if layer.visible]
    hidden_layers = [layer for layer in layers if not layer.visible]

    if visible_layers:
        print(f"\n📐 Visible layers ({len(visible_layers)}):")
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

            visibility_icon = "👁️" if layer.visible else "🚫"
            print(
                f"  {i + 1:2d}. {visibility_icon} {color_indicator} {layer.name} ({len(layer.elements)} elements)"
            )

    if hidden_layers:
        print(f"\n🚫 Hidden layers ({len(hidden_layers)}) - will be skipped:")
        for i, layer in enumerate(hidden_layers):
            print(f"  {i + 1:2d}. 🚫 {layer.name} ({len(layer.elements)} elements)")

    print("\nAvailable pens:")
    for i, pen in enumerate(available_pens):
        print(f"  {i + 1}. {pen['name']} ({pen.get('width_mm', 'unknown')}mm)")

    pen_map = {}

    # Only map visible layers
    for layer in visible_layers:
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
