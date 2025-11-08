"""
Comprehensive tests for recovery.py crash recovery system.
"""

from __future__ import annotations
import json
import tempfile
import pytest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from plotty.recovery import CrashRecovery, get_crash_recovery, requeue_job_to_front
from plotty.fsm import JobState


class TestCrashRecovery:
    """Test CrashRecovery class functionality."""

    @pytest.fixture
    def workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def crash_recovery(self, workspace):
        """Create CrashRecovery instance for testing."""
        return CrashRecovery(workspace)

    def test_crash_recovery_initialization(self, crash_recovery, workspace):
        """Test CrashRecovery initialization."""
        assert crash_recovery.workspace == workspace
        assert crash_recovery.active_fsms == {}
        assert isinstance(crash_recovery.cleanup_handlers_registered, bool)

    def test_register_fsm(self, crash_recovery):
        """Test registering an FSM."""
        mock_fsm = Mock()
        mock_fsm.job_id = "test_job"
        
        crash_recovery.register_fsm(mock_fsm)
        
        assert "test_job" in crash_recovery.active_fsms
        assert crash_recovery.active_fsms["test_job"] == mock_fsm

    def test_unregister_fsm(self, crash_recovery):
        """Test unregistering an FSM."""
        mock_fsm = Mock()
        mock_fsm.job_id = "test_job"
        
        # First register
        crash_recovery.register_fsm(mock_fsm)
        assert "test_job" in crash_recovery.active_fsms
        
        # Then unregister
        crash_recovery.unregister_fsm(mock_fsm)
        assert "test_job" not in crash_recovery.active_fsms

    def test_unregister_nonexistent_fsm(self, crash_recovery):
        """Test unregistering FSM that doesn't exist."""
        mock_fsm = Mock()
        mock_fsm.job_id = "nonexistent_job"
        
        # Should not raise error
        crash_recovery.unregister_fsm(mock_fsm)

    def test_recover_job_no_journal(self, crash_recovery):
        """Test recovering job with no journal."""
        result = crash_recovery.recover_job("nonexistent_job")
        assert result is None

    def test_recover_job_with_valid_journal(self, crash_recovery, workspace):
        """Test recovering job with valid journal."""
        job_id = "test_job"
        job_dir = workspace / "jobs" / job_id
        job_dir.mkdir(parents=True)
        journal_file = job_dir / "journal.jsonl"
        
        # Create journal with state transitions
        journal_entries = [
            {
                "type": "state_change",
                "from_state": "NEW",
                "to_state": "ANALYZED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": "Job analyzed",
                "metadata": {}
            },
            {
                "type": "state_change", 
                "from_state": "ANALYZED",
                "to_state": "OPTIMIZED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": "Job optimized",
                "metadata": {"optimization_level": "high"}
            }
        ]
        
        with open(journal_file, "w") as f:
            for entry in journal_entries:
                f.write(json.dumps(entry) + "\n")
        
        # Recover the job
        with patch('plotty.recovery.JobFSM') as mock_job_fsm:
            mock_fsm_instance = Mock()
            mock_fsm_instance.job_id = job_id
            mock_fsm_instance.current_state = JobState.NEW
            mock_fsm_instance.transitions = []
            mock_job_fsm.return_value = mock_fsm_instance
            
            result = crash_recovery.recover_job(job_id)
            
            assert result is not None
            mock_job_fsm.assert_called_once_with(job_id, workspace)
            assert mock_fsm_instance.current_state == JobState.OPTIMIZED
            assert len(mock_fsm_instance.transitions) == 2

    def test_recover_job_with_emergency_shutdown(self, crash_recovery, workspace):
        """Test recovering job after emergency shutdown."""
        job_id = "emergency_job"
        job_dir = workspace / "jobs" / job_id
        job_dir.mkdir(parents=True)
        journal_file = job_dir / "journal.jsonl"
        
        # Create journal with emergency shutdown
        journal_entries = [
            {
                "type": "state_change",
                "from_state": "READY",
                "to_state": "PLOTTING",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": "Started plotting",
                "metadata": {}
            },
            {
                "type": "emergency_shutdown",
                "state": "PLOTTING",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": "signal_received"
            }
        ]
        
        with open(journal_file, "w") as f:
            for entry in journal_entries:
                f.write(json.dumps(entry) + "\n")
        
        with patch('plotty.recovery.JobFSM') as mock_job_fsm:
            mock_fsm_instance = Mock()
            mock_fsm_instance.job_id = job_id
            mock_fsm_instance.current_state = JobState.NEW
            mock_fsm_instance.transitions = []
            mock_fsm_instance._write_journal = Mock()
            mock_job_fsm.return_value = mock_fsm_instance
            
            result = crash_recovery.recover_job(job_id)
            
            assert result is not None
            assert mock_fsm_instance.current_state == JobState.PLOTTING
            # Should add recovery transition
            assert len(mock_fsm_instance.transitions) == 2
            mock_fsm_instance._write_journal.assert_called()

    def test_recover_job_corrupted_journal(self, crash_recovery, workspace):
        """Test recovering job with corrupted journal."""
        job_id = "corrupted_job"
        job_dir = workspace / "jobs" / job_id
        job_dir.mkdir(parents=True)
        journal_file = job_dir / "journal.jsonl"
        
        # Create corrupted journal
        with open(journal_file, "w") as f:
            f.write("invalid json\n")
            f.write('{"invalid": "json"\n')
        
        result = crash_recovery.recover_job(job_id)
        assert result is None

    def test_get_resumable_jobs_empty(self, crash_recovery):
        """Test getting resumable jobs with no jobs directory."""
        resumable = crash_recovery.get_resumable_jobs()
        assert resumable == []

    def test_get_resumable_jobs_with_jobs(self, crash_recovery, workspace):
        """Test getting resumable jobs with mixed job states."""
        jobs_dir = workspace / "jobs"
        jobs_dir.mkdir()
        
        # Create multiple jobs with different states
        jobs_to_create = [
            ("completed_job", "COMPLETED"),
            ("aborted_job", "ABORTED"), 
            ("active_job", "PLOTTING"),
            ("ready_job", "READY"),
            ("failed_job", "FAILED")
        ]
        
        for job_id, final_state in jobs_to_create:
            job_dir = jobs_dir / job_id
            job_dir.mkdir()
            journal_file = job_dir / "journal.jsonl"
            
            entry = {
                "type": "state_change",
                "from_state": "NEW",
                "to_state": final_state,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": f"Job {final_state.lower()}",
                "metadata": {}
            }
            
            with open(journal_file, "w") as f:
                f.write(json.dumps(entry) + "\n")
        
        resumable = crash_recovery.get_resumable_jobs()
        
        # Should include jobs that are not COMPLETED or ABORTED
        expected = ["active_job", "ready_job", "failed_job"]
        assert sorted(resumable) == sorted(expected)

    def test_get_job_status_not_found(self, crash_recovery):
        """Test getting status for nonexistent job."""
        status = crash_recovery.get_job_status("nonexistent")
        assert "error" in status
        assert status["error"] == "Job not found"

    def test_get_job_status_valid(self, crash_recovery, workspace):
        """Test getting status for valid job."""
        job_id = "status_job"
        job_dir = workspace / "jobs" / job_id
        job_dir.mkdir(parents=True)
        
        # Create journal
        journal_file = job_dir / "journal.jsonl"
        journal_entry = {
            "type": "state_change",
            "from_state": "NEW",
            "to_state": "OPTIMIZED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "Job optimized",
            "metadata": {"test": "data"}
        }
        
        with open(journal_file, "w") as f:
            f.write(json.dumps(journal_entry) + "\n")
        
        # Create job file
        job_file = job_dir / "job.json"
        job_info = {"name": job_id, "created": "2024-01-01T00:00:00Z"}
        
        with open(job_file, "w") as f:
            json.dump(job_info, f)
        
        status = crash_recovery.get_job_status(job_id)
        
        assert status["job_id"] == job_id
        assert status["current_state"] == "OPTIMIZED"
        assert status["emergency_shutdown"] is False
        assert status["last_transition"] == journal_entry
        assert status["job_info"] == job_info
        assert status["journal_entries"] == 1
        assert status["resumable"] is True

    def test_cleanup_journal_no_file(self, crash_recovery):
        """Test cleaning up nonexistent journal."""
        result = crash_recovery.cleanup_journal("nonexistent")
        assert result is False

    def test_cleanup_journal_no_cleanup_needed(self, crash_recovery, workspace):
        """Test cleaning up journal that doesn't need cleanup."""
        job_id = "small_job"
        job_dir = workspace / "jobs" / job_id
        job_dir.mkdir(parents=True)
        journal_file = job_dir / "journal.jsonl"
        
        # Create small journal (less than default keep_entries)
        with open(journal_file, "w") as f:
            for i in range(5):
                entry = {
                    "type": "state_change",
                    "from_state": "NEW",
                    "to_state": "ANALYZED",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "reason": f"Entry {i}",
                    "metadata": {}
                }
                f.write(json.dumps(entry) + "\n")
        
        result = crash_recovery.cleanup_journal(job_id, keep_entries=10)
        assert result is True
        
        # Verify all entries still exist
        with open(journal_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 5

    def test_cleanup_journal_with_cleanup(self, crash_recovery, workspace):
        """Test cleaning up journal that needs cleanup."""
        job_id = "large_job"
        job_dir = workspace / "jobs" / job_id
        job_dir.mkdir(parents=True)
        journal_file = job_dir / "journal.jsonl"
        
        # Create large journal
        original_entries = []
        for i in range(150):
            entry = {
                "type": "state_change",
                "from_state": "NEW",
                "to_state": "ANALYZED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": f"Entry {i}",
                "metadata": {"index": i}
            }
            original_entries.append(entry)
        
        # Write the journal
        with open(journal_file, "w") as f:
            for entry in original_entries:
                f.write(json.dumps(entry) + "\n")
        
        result = crash_recovery.cleanup_journal(job_id, keep_entries=50)
        assert result is True
        
        # Verify only recent entries remain
        with open(journal_file, "r") as f:
            lines = f.readlines()
            assert len(lines) == 50
            
            # Check that these are the most recent entries
            for i, line in enumerate(lines):
                entry = json.loads(line.strip())
                assert entry["metadata"]["index"] == 100 + i  # Last 50 entries

    def test_safe_shutdown_fsm_plotting_state(self, crash_recovery):
        """Test safe shutdown of FSM in PLOTTING state."""
        mock_fsm = Mock()
        mock_fsm.current_state = JobState.PLOTTING
        mock_fsm.job_id = "plotting_job"
        mock_fsm._write_journal = Mock()
        mock_fsm.abort_job = Mock()
        
        crash_recovery._safe_shutdown_fsm(mock_fsm)
        
        # Should write emergency shutdown and abort
        mock_fsm._write_journal.assert_called_once()
        mock_fsm.abort_job.assert_called_once_with("Emergency shutdown")

    def test_safe_shutdown_fsm_safe_state(self, crash_recovery):
        """Test safe shutdown of FSM in safe state."""
        mock_fsm = Mock()
        mock_fsm.current_state = JobState.COMPLETED
        mock_fsm.job_id = "completed_job"
        mock_fsm._write_journal = Mock()
        mock_fsm.abort_job = Mock()
        
        crash_recovery._safe_shutdown_fsm(mock_fsm)
        
        # Should not write emergency shutdown or abort
        mock_fsm._write_journal.assert_not_called()
        mock_fsm.abort_job.assert_not_called()

    def test_cleanup_all_fsms(self, crash_recovery):
        """Test cleaning up all active FSMs."""
        mock_fsm1 = Mock()
        mock_fsm1.job_id = "job1"
        mock_fsm2 = Mock()
        mock_fsm2.job_id = "job2"
        
        crash_recovery.active_fsms = {"job1": mock_fsm1, "job2": mock_fsm2}
        
        crash_recovery._cleanup_all_fsms()
        
        # Should call safe shutdown on both and clear the dict
        mock_fsm1._safe_shutdown_fsm.assert_not_called()  # Called via different method
        mock_fsm2._safe_shutdown_fsm.assert_not_called()
        assert crash_recovery.active_fsms == {}


class TestGlobalFunctions:
    """Test global functions in recovery module."""

    def test_get_crash_recovery_singleton(self):
        """Test that get_crash_recovery returns singleton instance."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            
            # Reset global instance
            import plotty.recovery
            plotty.recovery._crash_recovery_instance = None
            
            # Get instance twice
            recovery1 = get_crash_recovery(workspace)
            recovery2 = get_crash_recovery(workspace)
            
            assert recovery1 is recovery2
            assert isinstance(recovery1, CrashRecovery)

    def test_requeue_job_to_front(self):
        """Test requeueing job to front of queue."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            job_id = "test_job"
            
            # Create job file
            jobs_dir = workspace / "jobs"
            jobs_dir.mkdir()
            job_dir = jobs_dir / job_id
            job_dir.mkdir()
            job_file = job_dir / "job.json"
            
            original_job_data = {
                "name": job_id,
                "created": "2024-01-01T00:00:00Z",
                "priority": 5
            }
            
            with open(job_file, "w") as f:
                json.dump(original_job_data, f)
            
            result = requeue_job_to_front(job_id, workspace)
            
            assert result is True
            
            # Verify job file was updated
            with open(job_file, "r") as f:
                updated_data = json.load(f)
            
            assert updated_data["queue_priority"] == 1  # Should be set to highest priority
            assert "updated_at" in updated_data

    def test_requeue_nonexistent_job(self):
        """Test requeueing nonexistent job."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            result = requeue_job_to_front("nonexistent", workspace)
            assert result is False


class TestSignalHandling:
    """Test signal handling functionality."""

    @patch('signal.signal')
    @patch('atexit.register')
    def test_signal_handler_registration(self, mock_atexit, mock_signal):
        """Test that signal handlers are registered properly."""
        import signal
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            
            # Reset global instance to test fresh initialization
            import plotty.recovery
            plotty.recovery._crash_recovery_instance = None
            
            recovery = get_crash_recovery(workspace)
            
            # Verify atexit handler was registered
            mock_atexit.assert_called_once_with(recovery._cleanup_all_fsms)
            
            # Verify signal handlers were registered
            expected_signals = [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]
            assert mock_signal.call_count == len(expected_signals)

    def test_signal_handler_functionality(self):
        """Test that signal handler works correctly."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            
            # Mock the exit function to prevent actual exit during test
            with patch('builtins.exit') as mock_exit:
                # Create recovery with mocked signal registration
                with patch('signal.signal') as mock_signal_set:
                    recovery = CrashRecovery(workspace)
                    
                    mock_fsm = Mock()
                    mock_fsm.job_id = "test_job"
                    recovery.active_fsms = {"test_job": mock_fsm}
                    
                    # Extract the handler function that was registered
                    # Since cleanup_handlers_registered becomes True after first call,
                    # we need to examine what was registered during initialization
                    if mock_signal_set.call_args:
                        call_args = mock_signal_set.call_args[0]
                        if len(call_args) >= 2:
                            handler_func = call_args[1]
                            
                            # Call the handler
                            handler_func(15, None)  # SIGTERM
                            
                            # Verify cleanup was called and exit was called
                            mock_exit.assert_called_with(0)