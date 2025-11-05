"""
Test environment utilities for ploTTY self-testing.

This module provides isolated test environment creation with temporary workspaces,
databases, and configurations to ensure safe testing without affecting production data.
"""

from __future__ import annotations

import os
import tempfile
import shutil
import yaml
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

from ..config import load_config


@dataclass
class TestEnvironment:
    """Isolated test environment for ploTTY testing."""

    temp_dir: Path
    test_workspace: Path
    test_config: Path
    test_database: Path
    cleanup_on_exit: bool

    def __post_init__(self):
        """Create directory structure after initialization."""
        self.test_workspace.mkdir(parents=True, exist_ok=True)
        (self.test_workspace / "jobs").mkdir(exist_ok=True)
        (self.test_workspace / "output").mkdir(exist_ok=True)
        self.test_config.parent.mkdir(parents=True, exist_ok=True)

    def setup(self) -> Path:
        """Create test configuration and return config path."""
        # Load base configuration
        base_config = load_config(None)

        # Create test-specific configuration
        test_config_data = {
            "workspace": str(self.test_workspace),
            "database": {"url": f"sqlite:///{self.test_database}", "echo": False},
            "device": {
                "preferred": "mock:device",
                "port": "MOCK_PORT",
                "model": 1,
                "pen_pos_up": 60,
                "pen_pos_down": 40,
                "speed_pendown": 25,
                "speed_penup": 75,
                "units": "inches",
                "pause_ink_swatch": True,
                "detection_timeout": 5,
            },
            "camera": {"enabled": False, "mode": "disabled", "test_access": False},
            "vpype": {
                "preset": base_config.vpype.preset,
                "presets_file": base_config.vpype.presets_file,
            },
            "paper": {
                "default_size": "A4",
                "default_margin_mm": 10.0,
                "default_orientation": "portrait",
                "require_one_per_session": False,  # Disable for testing
                "track_usage": False,  # Disable for testing
            },
            "logging": {
                "enabled": True,
                "level": "WARNING",  # Reduce noise during tests
                "format": "plain",
                "output": "file",
                "log_file": str(self.test_workspace / "test.log"),
                "console_show_timestamp": False,
                "console_show_level": False,
            },
        }

        # Write test configuration
        self.test_config.write_text(
            yaml.dump(test_config_data, default_flow_style=False)
        )

        return self.test_config

    def cleanup(self) -> None:
        """Clean up temporary test environment."""
        if self.cleanup_on_exit and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_svg(self, name: str, content: Optional[str] = None) -> Path:
        """Create a test SVG file in the test environment."""
        svg_dir = self.temp_dir / "test_svgs"
        svg_dir.mkdir(exist_ok=True)

        svg_path = svg_dir / f"{name}.svg"

        if content is None:
            # Default simple test SVG
            content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100mm" height="100mm" viewBox="0 0 100 100"
     xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="30" stroke="black" fill="none" stroke-width="0.5"/>
  <rect x="20" y="20" width="60" height="60" stroke="black" fill="none" stroke-width="0.5"/>
</svg>"""

        svg_path.write_text(content)
        return svg_path


def create_test_environment(cleanup: bool = True) -> TestEnvironment:
    """Create a new isolated test environment.

    Args:
        cleanup: Whether to clean up temporary files on exit

    Returns:
        TestEnvironment instance
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="plotty_test_"))

    test_env = TestEnvironment(
        temp_dir=temp_dir,
        test_workspace=temp_dir / "workspace",
        test_config=temp_dir / "config" / "test_config.yaml",
        test_database=temp_dir / "workspace" / "test_plotty.db",
        cleanup_on_exit=cleanup,
    )

    return test_env


@contextmanager
def test_environment_context(cleanup: bool = True):
    """Context manager for isolated test environment.

    Args:
        cleanup: Whether to clean up temporary files on exit

    Yields:
        TestEnvironment instance
    """
    test_env = create_test_environment(cleanup)
    config_path = test_env.setup()

    # Store original config environment variable
    original_config = os.environ.get("PLOTTY_CONFIG")

    try:
        # Set test configuration
        os.environ["PLOTTY_CONFIG"] = str(config_path)

        # Initialize test database
        from ..db import init_database

        test_db_url = f"sqlite:///{test_env.test_database}"
        init_database(test_db_url, echo=False)

        yield test_env

    finally:
        # Restore original configuration
        if original_config:
            os.environ["PLOTTY_CONFIG"] = original_config
        elif "PLOTTY_CONFIG" in os.environ:
            del os.environ["PLOTTY_CONFIG"]

        # Clean up
        test_env.cleanup()


def get_test_svgs() -> Dict[str, str]:
    """Get predefined test SVG templates.

    Returns:
        Dictionary mapping SVG names to content
    """
    return {
        "simple": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100mm" height="100mm" viewBox="0 0 100 100"
     xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="30" stroke="black" fill="none" stroke-width="0.5"/>
</svg>""",
        "complex": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100mm" height="100mm" viewBox="0 0 100 100"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style type="text/css">
      .layer1 { stroke: red; fill: none; }
      .layer2 { stroke: blue; fill: none; }
      .layer3 { stroke: green; fill: none; }
    </style>
  </defs>
  <g class="layer1">
    <circle cx="50" cy="50" r="30"/>
    <rect x="20" y="20" width="60" height="60"/>
  </g>
  <g class="layer2">
    <line x1="50" y1="20" x2="50" y2="80"/>
    <line x1="20" y1="50" x2="80" y2="50"/>
  </g>
  <g class="layer3">
    <polygon points="50,20 80,80 20,80"/>
  </g>
</svg>""",
        "invalid": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100mm" height="100mm" viewBox="0 0 100 100"
     xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="30" stroke="black" fill="none"/>
  <!-- Missing closing tag for invalid SVG -->
  <rect x="20" y="20" width="60" height="60" stroke="black" fill="none"
</svg>""",
    }


__all__ = [
    "TestEnvironment",
    "create_test_environment",
    "test_environment_context",
    "get_test_svgs",
]
