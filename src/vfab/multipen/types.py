"""
Core types for multi-pen functionality.
"""

from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, NamedTuple


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

    def __init__(
        self,
        name: str,
        elements: List[ET.Element],
        order_index: int,
        visible: bool = True,
        color: Optional[str] = None,
    ):
        self.name = name
        self.elements = elements
        self.order_index = order_index
        self.visible = visible  # Layer visibility (Inkscape hidden layers)
        self.color = color  # Layer color for visualization
        self.pen_id: Optional[int] = None
        self.stats: Dict = {}

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "order_index": self.order_index,
            "visible": self.visible,
            "color": self.color,
            "pen_id": self.pen_id,
            "element_count": len(self.elements),
            "stats": self.stats,
        }
