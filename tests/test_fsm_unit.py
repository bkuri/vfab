"""Test basic FSM functionality without complex dependencies."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime, timezone

from vfab.fsm import JobState, StateTransition


class TestJobState:
    """Test JobState enumeration."""

    def test_job_state_values(self):
        """Test that all expected job states exist."""
        expected_states = {
            "NEW",
            "QUEUED",
            "ANALYZED",
            "OPTIMIZED",
            "READY",
            "ARMED",
            "PLOTTING",
            "PAUSED",
            "COMPLETED",
            "ABORTED",
            "FAILED",
        }
        actual_states = {state.name for state in JobState}
        assert actual_states == expected_states

    def test_job_state_string_values(self):
        """Test that job states have expected string values."""
        assert JobState.NEW.value == "NEW"
        assert JobState.QUEUED.value == "QUEUED"
        assert JobState.ANALYZED.value == "ANALYZED"
        assert JobState.COMPLETED.value == "COMPLETED"
        assert JobState.FAILED.value == "FAILED"


class TestStateTransition:
    """Test StateTransition dataclass."""

    def test_state_transition_creation(self):
        """Test creating a state transition."""
        timestamp = datetime.now(timezone.utc)
        metadata = {"user": "test"}
        transition = StateTransition(
            from_state=JobState.NEW,
            to_state=JobState.QUEUED,
            timestamp=timestamp,
            reason="Job queued",
            metadata=metadata,
        )

        assert transition.from_state == JobState.NEW
        assert transition.to_state == JobState.QUEUED
        assert transition.timestamp == timestamp
        assert transition.reason == "Job queued"
        assert transition.metadata == metadata


class TestBasicFSM:
    """Test basic FSM functionality with minimal mocking."""

    @pytest.fixture
    def mock_workspace(self):
        """Mock workspace path."""
        return Path("/tmp/test_workspace")

    @pytest.fixture
    def fsm(self, mock_workspace):
        """Create minimal FSM instance."""
        # Clean up any existing journal file from previous tests
        job_dir = mock_workspace / "jobs" / "test_job"
        journal_file = job_dir / "journal.jsonl"
        if journal_file.exists():
            journal_file.unlink()

        # Mock all optional dependencies
        mock_guard_system = Mock()
        mock_guard_system.can_transition.return_value = (True, [])

        with (
            patch("vfab.fsm.create_hook_executor", return_value=Mock()),
            patch("vfab.fsm.create_guard_system", return_value=mock_guard_system),
            patch("vfab.fsm.get_crash_recovery", return_value=Mock()),
            patch("vfab.fsm.create_checklist", return_value=Mock()),
            patch("vfab.fsm.get_statistics_service", return_value=Mock()),
            patch("vfab.fsm.load_config", return_value={}),
        ):

            from vfab.fsm import JobFSM

            return JobFSM("test_job", mock_workspace)

    def test_fsm_initialization(self, fsm):
        """Test FSM initialization."""
        assert fsm.job_id == "test_job"
        assert fsm.current_state == JobState.NEW
        assert len(fsm.transitions) == 0

    def test_can_transition_to(self, fsm):
        """Test checking if transition is allowed."""
        # Test valid transition
        assert fsm.can_transition_to(JobState.ANALYZED) is True
        assert fsm.can_transition_to(JobState.READY) is True

        # Test invalid transition (can't jump directly to completed)
        assert fsm.can_transition_to(JobState.COMPLETED) is False

    def test_successful_transition_to(self, fsm):
        """Test successful state transition."""
        result = fsm.transition_to(
            target_state=JobState.ANALYZED, reason="Job analyzed"
        )

        assert result is True
        assert fsm.current_state == JobState.ANALYZED
        assert len(fsm.transitions) == 1

        transition = fsm.transitions[0]
        assert transition.from_state == JobState.NEW
        assert transition.to_state == JobState.ANALYZED
        assert transition.reason == "Job analyzed"

    def test_invalid_transition_to(self, fsm):
        """Test invalid state transition."""
        result = fsm.transition_to(
            target_state=JobState.COMPLETED, reason="Invalid jump"
        )

        assert result is False
        assert fsm.current_state == JobState.NEW
        assert len(fsm.transitions) == 0

    def test_transition_to_with_metadata(self, fsm):
        """Test transition with metadata."""
        metadata = {"user": "test_user", "priority": "high"}
        result = fsm.transition_to(
            target_state=JobState.ANALYZED,
            reason="High priority job",
            metadata=metadata,
        )

        assert result is True
        transition = fsm.transitions[0]
        assert transition.metadata == metadata

    def test_get_state_history(self, fsm):
        """Test getting state history."""
        # Add some transitions
        fsm.transition_to(target_state=JobState.ANALYZED, reason="Analyzed")
        fsm.transition_to(target_state=JobState.OPTIMIZED, reason="Optimized")

        history = fsm.get_state_history()
        assert len(history) == 2  # Should have 2 state entries

    def test_workflow_progression(self, fsm):
        """Test a simple workflow progression."""
        # Progress through a few states
        assert (
            fsm.transition_to(
                target_state=JobState.ANALYZED, reason="Analysis complete"
            )
            is True
        )
        assert fsm.current_state == JobState.ANALYZED

        assert (
            fsm.transition_to(
                target_state=JobState.OPTIMIZED, reason="Optimization complete"
            )
            is True
        )
        assert fsm.current_state == JobState.OPTIMIZED

        assert (
            fsm.transition_to(target_state=JobState.READY, reason="Ready to plot")
            is True
        )
        assert fsm.current_state == JobState.READY

        # Should have 3 transitions
        assert len(fsm.transitions) == 3
