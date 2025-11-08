"""Test Finite State Machine for job lifecycle."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime, timezone

from plotty.fsm import JobState, StateTransition, JobFSM, create_fsm


class TestJobState:
    """Test JobState enumeration."""
    
    def test_job_state_values(self):
        """Test that all expected job states exist."""
        expected_states = {
            'NEW', 'QUEUED', 'ANALYZED', 'OPTIMIZED', 
            'READY', 'ARMED', 'PLOTTING', 'PAUSED', 
            'COMPLETED', 'ABORTED', 'FAILED'
        }
        actual_states = {state.name for state in JobState}
        assert actual_states == expected_states
    
    def test_job_state_values_exist(self):
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
        transition = StateTransition(
            from_state=JobState.NEW,
            to_state=JobState.QUEUED,
            timestamp=timestamp,
            reason="Job queued",
            metadata={"user": "test"}
        )
        
        assert transition.from_state == JobState.NEW
        assert transition.to_state == JobState.QUEUED
        assert transition.timestamp == timestamp
        assert transition.reason == "Job queued"
        assert transition.metadata == {"user": "test"}
    
    def test_state_transition_attributes(self):
        """Test state transition attributes."""
        timestamp = datetime.now(timezone.utc)
        metadata = {"test": "data"}
        transition = StateTransition(
            from_state=JobState.NEW,
            to_state=JobState.QUEUED,
            timestamp=timestamp,
            reason="Test",
            metadata=metadata
        )
        
        assert transition.from_state == JobState.NEW
        assert transition.to_state == JobState.QUEUED
        assert transition.timestamp == timestamp
        assert transition.reason == "Test"
        assert transition.metadata == metadata


class TestJobFSM:
    """Test JobFSM core functionality."""
    
    @pytest.fixture
    def mock_workspace(self):
        """Mock workspace path."""
        return Path("/tmp/test_workspace")
    
    @pytest.fixture
    def job_fsm(self, mock_workspace):
        """Create JobFSM instance with mocked dependencies."""
        with patch('plotty.fsm.create_hook_executor') as mock_hooks, \
             patch('plotty.fsm.create_guard_system') as mock_guards, \
             patch('plotty.fsm.get_crash_recovery') as mock_recovery, \
             patch('plotty.fsm.create_checklist') as mock_checklist, \
             patch('plotty.fsm.get_statistics_service') as mock_stats:
            
            # Setup mocks
            mock_hooks.return_value = Mock()
            mock_guards.return_value = Mock()
            mock_recovery.return_value = Mock()
            mock_checklist.return_value = Mock()
            mock_stats.return_value = Mock()
            
            fsm = JobFSM(
                job_id="test_job_123",
                workspace=mock_workspace
            )
            
            return fsm
    
    def test_fsm_initialization(self, job_fsm):
        """Test FSM initialization."""
        assert job_fsm.job_id == "test_job_123"
        assert job_fsm.current_state == JobState.NEW
        assert len(job_fsm.transitions) == 0
        assert job_fsm.created_at is not None
    
    def test_get_state(self, job_fsm):
        """Test getting current state."""
        assert job_fsm.get_state() == JobState.NEW
    
    def test_get_valid_transitions(self, job_fsm):
        """Test getting valid transitions from current state."""
        transitions = job_fsm.get_valid_transitions()
        assert JobState.QUEUED in transitions
        assert JobState.FAILED in transitions
        assert JobState.ABORTED in transitions
        assert JobState.COMPLETED not in transitions  # Can't jump to completed
    
    def test_can_transition(self, job_fsm):
        """Test checking if transition is allowed."""
        assert job_fsm.can_transition(JobState.QUEUED) is True
        assert job_fsm.can_transition(JobState.FAILED) is True
        assert job_fsm.can_transition(JobState.COMPLETED) is False
    
    def test_successful_transition(self, job_fsm):
        """Test successful state transition."""
        result = job_fsm.transition(
            to_state=JobState.QUEUED,
            reason="Job queued by user"
        )
        
        assert result is True
        assert job_fsm.current_state == JobState.QUEUED
        assert len(job_fsm.transitions) == 1
        
        transition = job_fsm.transitions[0]
        assert transition.from_state == JobState.NEW
        assert transition.to_state == JobState.QUEUED
        assert transition.reason == "Job queued by user"
    
    def test_invalid_transition(self, job_fsm):
        """Test invalid state transition."""
        result = job_fsm.transition(
            to_state=JobState.COMPLETED,
            reason="Invalid jump"
        )
        
        assert result is False
        assert job_fsm.current_state == JobState.NEW
        assert len(job_fsm.transitions) == 0
    
    def test_transition_with_metadata(self, job_fsm):
        """Test transition with metadata."""
        metadata = {"user": "test_user", "priority": "high"}
        result = job_fsm.transition(
            to_state=JobState.QUEUED,
            reason="High priority job",
            metadata=metadata
        )
        
        assert result is True
        transition = job_fsm.transitions[0]
        assert transition.metadata == metadata
    
    def test_get_transition_history(self, job_fsm):
        """Test getting transition history."""
        # Add some transitions
        job_fsm.transition(JobState.QUEUED, "Queued")
        job_fsm.transition(JobState.ANALYZED, "Analyzed")
        
        history = job_fsm.get_transition_history()
        assert len(history) == 2
        assert history[0].from_state == JobState.NEW
        assert history[0].to_state == JobState.QUEUED
        assert history[1].from_state == JobState.QUEUED
        assert history[1].to_state == JobState.ANALYZED
    
    def test_is_terminal_state(self, job_fsm):
        """Test checking if state is terminal."""
        assert job_fsm.is_terminal_state(JobState.COMPLETED) is True
        assert job_fsm.is_terminal_state(JobState.ABORTED) is True
        assert job_fsm.is_terminal_state(JobState.FAILED) is True
        assert job_fsm.is_terminal_state(JobState.NEW) is False
        assert job_fsm.is_terminal_state(JobState.PLOTTING) is False
    
    def test_can_pause(self, job_fsm):
        """Test pause capability."""
        # Can't pause when not plotting
        assert job_fsm.can_pause() is False
        
        # Move to plotting state
        job_fsm.transition(JobState.QUEUED)
        job_fsm.transition(JobState.ANALYZED)
        job_fsm.transition(JobState.OPTIMIZED)
        job_fsm.transition(JobState.READY)
        job_fsm.transition(JobState.ARMED)
        job_fsm.transition(JobState.PLOTTING)
        
        assert job_fsm.can_pause() is True
    
    def test_can_resume(self, job_fsm):
        """Test resume capability."""
        # Can't resume when not paused
        assert job_fsm.can_resume() is False
        
        # Move to paused state
        job_fsm.transition(JobState.QUEUED)
        job_fsm.transition(JobState.ANALYZED)
        job_fsm.transition(JobState.OPTIMIZED)
        job_fsm.transition(JobState.READY)
        job_fsm.transition(JobState.ARMED)
        job_fsm.transition(JobState.PLOTTING)
        job_fsm.transition(JobState.PAUSED)
        
        assert job_fsm.can_resume() is True
    
    def test_get_status_info(self, job_fsm):
        """Test getting status information."""
        job_fsm.transition(JobState.QUEUED, "Test transition")
        
        status = job_fsm.get_status_info()
        
        assert status['job_id'] == "test_job_123"
        assert status['current_state'] == "QUEUED"
        assert status['can_pause'] is False
        assert status['can_resume'] is False
        assert status['is_terminal'] is False
        assert 'transitions_count' in status
        assert 'last_transition' in status
    
    def test_to_dict_serialization(self, job_fsm):
        """Test FSM serialization to dictionary."""
        job_fsm.transition(JobState.QUEUED, "Test")
        
        result = job_fsm.to_dict()
        
        expected_keys = {
            'job_id', 'current_state', 'created_at', 'updated_at',
            'transitions', 'metadata'
        }
        assert set(result.keys()) == expected_keys
        assert result['job_id'] == "test_job_123"
        assert result['current_state'] == "QUEUED"
        assert len(result['transitions']) == 1


class TestFSMFactory:
    """Test FSM factory function."""
    
    def test_create_fsm(self):
        """Test creating FSM through factory."""
        with patch('plotty.fsm.create_hook_executor') as mock_hooks, \
             patch('plotty.fsm.create_guard_system') as mock_guards, \
             patch('plotty.fsm.get_crash_recovery') as mock_recovery, \
             patch('plotty.fsm.create_checklist') as mock_checklist, \
             patch('plotty.fsm.get_statistics_service') as mock_stats:
            
            # Setup mocks
            mock_hooks.return_value = Mock()
            mock_guards.return_value = Mock()
            mock_recovery.return_value = Mock()
            mock_checklist.return_value = Mock()
            mock_stats.return_value = Mock()
            
            workspace = Path("/tmp/test")
            fsm = create_fsm("test_job", workspace)
            
            assert isinstance(fsm, JobFSM)
            assert fsm.job_id == "test_job"
            assert fsm.workspace == workspace


class TestFSMIntegration:
    """Test FSM integration scenarios."""
    
    @pytest.fixture
    def fsm(self):
        """Create FSM for integration tests."""
        with patch('plotty.fsm.create_hook_executor'), \
             patch('plotty.fsm.create_guard_system'), \
             patch('plotty.fsm.get_crash_recovery'), \
             patch('plotty.fsm.create_checklist'), \
             patch('plotty.fsm.get_statistics_service'):
            
            return JobFSM("integration_test", Path("/tmp"))
    
    def test_complete_successful_workflow(self, fsm):
        """Test complete successful job workflow."""
        # Normal progression
        workflow = [
            (JobState.QUEUED, "Job queued"),
            (JobState.ANALYZED, "Analysis complete"),
            (JobState.OPTIMIZED, "Optimization complete"),
            (JobState.READY, "Ready to plot"),
            (JobState.ARMED, "Plotter armed"),
            (JobState.PLOTTING, "Started plotting"),
            (JobState.COMPLETED, "Plotting complete")
        ]
        
        for state, reason in workflow:
            result = fsm.transition(state, reason)
            assert result is True
            assert fsm.current_state == state
        
        assert fsm.is_terminal_state(fsm.current_state) is True
        assert len(fsm.transitions) == len(workflow)
    
    def test_pause_resume_workflow(self, fsm):
        """Test pause and resume workflow."""
        # Progress to plotting
        for state in [JobState.QUEUED, JobState.ANALYZED, JobState.OPTIMIZED, 
                     JobState.READY, JobState.ARMED, JobState.PLOTTING]:
            fsm.transition(state)
        
        # Pause
        assert fsm.can_pause() is True
        fsm.transition(JobState.PAUSED, "User requested pause")
        assert fsm.current_state == JobState.PAUSED
        
        # Resume
        assert fsm.can_resume() is True
        fsm.transition(JobState.PLOTTING, "Resumed plotting")
        assert fsm.current_state == JobState.PLOTTING
        
        # Complete
        fsm.transition(JobState.COMPLETED, "Finished")
        assert fsm.current_state == JobState.COMPLETED
    
    def test_failure_workflow(self, fsm):
        """Test failure workflow."""
        # Progress partway then fail
        fsm.transition(JobState.QUEUED)
        fsm.transition(JobState.ANALYZED)
        
        # Fail
        fsm.transition(JobState.FAILED, "Plotter hardware error")
        assert fsm.current_state == JobState.FAILED
        assert fsm.is_terminal_state(fsm.current_state) is True
        
        # Can't continue after failure
        assert fsm.can_transition(JobState.OPTIMIZED) is False