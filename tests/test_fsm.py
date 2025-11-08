#!/usr/bin/env python3
"""Test script for FSM implementation."""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plotty.fsm import JobState, create_fsm


def test_fsm_basic():
    """Test basic FSM functionality."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        workspace = Path(tmp_dir)
        fsm = create_fsm("test123", workspace)

        # Test initial state
        assert fsm.current_state == JobState.NEW
        print("✓ Initial state correct")

        # Test valid transitions
        assert fsm.can_transition_to(JobState.ANALYZED)
        assert fsm.can_transition_to(JobState.QUEUED)  # Can go directly to QUEUED
        assert not fsm.can_transition_to(JobState.PLOTTING)
        print("✓ Transition validation works")

        # Test state transition
        result = fsm.transition_to(JobState.ANALYZED, "File analyzed", {})
        assert result
        assert fsm.current_state == JobState.ANALYZED
        print("✓ State transition works")

        # Test history
        history = fsm.get_state_history()
        assert len(history) == 1
        assert history[0]["from_state"] == JobState.NEW.value
        assert history[0]["to_state"] == JobState.ANALYZED.value
        print("✓ State history works")

        print("All FSM tests passed!")


if __name__ == "__main__":
    test_fsm_basic()
