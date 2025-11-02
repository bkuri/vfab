"""
Plot presets for ploTTY - predefined configurations for different scenarios.

This module provides preset configurations that can be used with the --preset flag
to quickly apply common plotting settings.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


@dataclass
class PlotPreset:
    """Plot preset configuration."""

    name: str
    description: str
    speed: float  # Speed percentage (0-100)
    pen_height: float  # Pen height percentage (0-100)
    pen_pressure: int  # Pen pressure (0-100)
    passes: int  # Number of passes
    acceleration: float  # Acceleration factor
    cornering: float  # Cornering factor

    def to_vpype_args(self) -> Dict[str, Any]:
        """Convert preset to vpype arguments."""
        return {
            "speed": self.speed,
            "pen_height": self.pen_height,
            "pen_pressure": self.pen_pressure,
            "passes": self.passes,
            "acceleration": self.acceleration,
            "cornering": self.cornering,
        }


# Preset definitions
PRESETS: Dict[str, PlotPreset] = {
    "fast": PlotPreset(
        name="fast",
        description="Maximum speed for quick drafts and tests",
        speed=100.0,
        pen_height=50.0,
        pen_pressure=60,
        passes=1,
        acceleration=1.5,
        cornering=1.2,
    ),
    "safe": PlotPreset(
        name="safe",
        description="Conservative settings for reliable plotting",
        speed=60.0,
        pen_height=40.0,
        pen_pressure=80,
        passes=1,
        acceleration=0.8,
        cornering=0.9,
    ),
    "preview": PlotPreset(
        name="preview",
        description="Quick preview without pen down (dry run)",
        speed=120.0,
        pen_height=100.0,  # Pen up
        pen_pressure=0,
        passes=1,
        acceleration=2.0,
        cornering=1.5,
    ),
    "detail": PlotPreset(
        name="detail",
        description="High precision for detailed artwork",
        speed=40.0,
        pen_height=30.0,
        pen_pressure=90,
        passes=2,
        acceleration=0.6,
        cornering=0.7,
    ),
    "draft": PlotPreset(
        name="draft",
        description="Quick draft with moderate quality",
        speed=80.0,
        pen_height=45.0,
        pen_pressure=70,
        passes=1,
        acceleration=1.2,
        cornering=1.0,
    ),
}


def get_preset(name: str) -> Optional[PlotPreset]:
    """Get a preset by name."""
    return PRESETS.get(name.lower())


def list_presets() -> Dict[str, PlotPreset]:
    """Get all available presets."""
    return PRESETS.copy()


def preset_names() -> list[str]:
    """Get list of preset names."""
    return list(PRESETS.keys())


def validate_preset(name: str) -> bool:
    """Check if a preset exists."""
    return name.lower() in PRESETS


def apply_preset_to_config(
    preset: PlotPreset, config: Dict[str, Any]
) -> Dict[str, Any]:
    """Apply preset settings to a configuration dictionary."""
    updated_config = config.copy()

    # Apply preset values
    updated_config.update(preset.to_vpype_args())

    # Add preset metadata
    updated_config["preset"] = preset.name
    updated_config["preset_description"] = preset.description

    return updated_config


def preset_to_json(preset: PlotPreset) -> str:
    """Convert preset to JSON string."""
    return json.dumps(
        {
            "name": preset.name,
            "description": preset.description,
            "settings": preset.to_vpype_args(),
        },
        indent=2,
    )
