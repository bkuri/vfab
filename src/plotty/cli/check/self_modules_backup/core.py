"""
Core utilities for self-testing.

This module provides shared functionality for test environment setup,
command execution, and basic test utilities.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any


def create_test_environment() -> Path:
    """Create isolated test environment."""
    temp_dir = Path(tempfile.mkdtemp(prefix="plotty_test_"))

    # Create workspace
    workspace = temp_dir / "workspace"
    workspace.mkdir(parents=True)
    (workspace / "jobs").mkdir()
    (workspace / "output").mkdir()

    # Create test config
    config_dir = temp_dir / "config"
    config_dir.mkdir()

    test_config = {
        "workspace": str(workspace),
        "database": {"url": f"sqlite:///{workspace / 'test_plotty.db'}", "echo": False},
        "device": {"preferred": "mock:device", "port": "MOCK_PORT"},
        "camera": {"enabled": False},
        "logging": {"enabled": False},
    }

    config_file = config_dir / "test_config.yaml"
    config_file.write_text(yaml.dump(test_config))

    return temp_dir


def run_command(command: str, test_env: Path, timeout: int = 30) -> Dict[str, Any]:
    """Run a ploTTY command in test environment."""
    try:
        # Set environment for test
        env = os.environ.copy()
        env["PLOTTY_CONFIG"] = str(test_env / "config" / "test_config.yaml")

        # Execute command
        result = subprocess.run(
            f"uv run python -m plotty.cli {command}".split(),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd="/home/bk/source/plotty",  # Run from project root
        )

        # For check config, treat WARNING (exit code 2) as success since warnings are expected
        success_threshold = 0 if "check config" not in command else 2
        success = result.returncode in [0, success_threshold]

        return {
            "success": success,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timeout": False,
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Command timed out",
            "timeout": True,
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "timeout": False,
        }


def create_test_svg(test_env: Path) -> Path:
    """Create a test SVG file."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100mm" height="100mm" viewBox="0 0 100 100"
     xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="30" stroke="black" fill="none" stroke-width="0.5"/>
  <rect x="20" y="20" width="60" height="60" stroke="black" fill="none" stroke-width="0.5"/>
</svg>"""

    svg_file = test_env / "test.svg"
    svg_file.write_text(svg_content)
    return svg_file


def cleanup_test_environment(test_env: Path) -> None:
    """Clean up test environment."""
    shutil.rmtree(test_env, ignore_errors=True)
