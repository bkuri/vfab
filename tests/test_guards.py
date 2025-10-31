#!/usr/bin/env python3
"""Test script for guards implementation."""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plotty.guards import create_guard_system
from plotty.config import load_config
from plotty.checklist import create_checklist


def test_guards_integration():
    """Test guards integration."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        workspace = Path(tmp_dir)

        # Create test config
        config_file = workspace / "config.yaml"
        config_file.write_text("""
workspace: ./workspace
database: { url: "sqlite:///./plotty.db", echo: false }
camera: { mode: ip, url: "http://127.0.0.1:8881/stream.mjpeg", enabled: true, timelapse_fps: 1 }
device: { preferred: "axidraw:auto", pause_ink_swatch: true }
vpype: { preset: fast, presets_file: "config/vpype-presets.yaml" }
hooks: {}
""")

        # Set config env var
        import os

        os.environ["PLOTTY_CONFIG"] = str(config_file)

        config = load_config()
        guard_system = create_guard_system(config, workspace)

        print("Testing guards system...")

        # Test device guard (will likely soft-fail without actual device)
        print("\n1. Testing device guard:")
        device_check = guard_system.device_guard.check("test123")
        print(f"   Result: {device_check.result.value}")
        print(f"   Message: {device_check.message}")

        # Test camera guard (will likely soft-fail without actual camera)
        print("\n2. Testing camera guard:")
        camera_check = guard_system.camera_guard.check("test123")
        print(f"   Result: {camera_check.result.value}")
        print(f"   Message: {camera_check.message}")

        # Test checklist guard
        print("\n3. Testing checklist guard:")
        job_dir = workspace / "jobs" / "test123"
        checklist = create_checklist("test123", job_dir)

        # Initially incomplete
        checklist_check = guard_system.checklist_guard.check("test123", workspace)
        print(f"   Initial result: {checklist_check.result.value}")
        print(f"   Message: {checklist_check.message}")

        # Complete required items
        checklist.complete_item("paper_size_set", "A3 selected")
        checklist.complete_item("paper_taped", "Paper taped securely")
        checklist.complete_item("origin_set", "Origin at (0,0)")
        checklist.complete_item("pen_loaded", "0.3mm black pen loaded")
        checklist.complete_item("surface_clear", "Clear area verified")

        # Now should pass
        checklist_check = guard_system.checklist_guard.check("test123", workspace)
        print(f"   After completion result: {checklist_check.result.value}")
        print(f"   Message: {checklist_check.message}")

        # Test full guard evaluation
        print("\n4. Testing full guard evaluation:")
        can_transition, guard_checks = guard_system.can_transition("test123", "ARMED")
        print(f"   Can transition to ARMED: {can_transition}")
        print(f"   Number of guard checks: {len(guard_checks)}")

        for check in guard_checks:
            print(f"   - {check.name}: {check.result.value} - {check.message}")

        print("\nAll guards tests completed!")


if __name__ == "__main__":
    test_guards_integration()
