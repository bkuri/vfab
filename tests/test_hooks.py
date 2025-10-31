#!/usr/bin/env python3
"""Test script for hooks implementation."""

import sys
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plotty.fsm import JobState, create_fsm


def test_hooks_integration():
    """Test hooks integration with FSM."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        workspace = Path(tmp_dir)

        # Create test config with hooks
        config_file = workspace / "config.yaml"
        config_file.write_text("""
workspace: ./workspace
database: { url: "sqlite:///./plotty.db", echo: false }
camera: { mode: ip, url: "http://127.0.0.1:8881/stream.mjpeg", enabled: true, timelapse_fps: 1 }
device: { preferred: "axidraw:auto", pause_ink_swatch: true }
vpype: { preset: fast, presets_file: "config/vpype-presets.yaml" }

hooks:
  NEW:
    - command: "echo 'Job {job_id} created'"
  QUEUED:
    - command: "echo 'Job {job_id} queued'"
  COMPLETED:
    - command: "echo 'Job {job_id} completed'"
""")

        # Set config env var
        import os

        os.environ["PLOTTY_CONFIG"] = str(config_file)

        fsm = create_fsm("test_hooks", workspace)

        # Test state transitions with hooks
        print("Testing hooks integration...")

        # Transition to QUEUED (should execute NEW and QUEUED hooks)
        result = fsm.transition_to(JobState.QUEUED, "Test queue", {})
        assert result
        print("✓ QUEUED transition with hooks executed")

        # Check journal for hook execution
        journal_file = fsm.job_dir / "journal.jsonl"
        assert journal_file.exists()

        with open(journal_file, "r") as f:
            journal_entries = [json.loads(line) for line in f if line.strip()]

        # Should have state change and hooks executed entries
        hook_entries = [e for e in journal_entries if e.get("type") == "hooks_executed"]
        assert len(hook_entries) >= 1
        print("✓ Hook execution recorded in journal")

        print("All hooks tests passed!")


if __name__ == "__main__":
    import json

    test_hooks_integration()
