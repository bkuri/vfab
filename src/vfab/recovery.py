"""
Crash recovery system for vfab FSM.

This module provides crash-safe resume capabilities using journal persistence
as specified in the PRD for reliable operation.
"""

from __future__ import annotations
import json
import signal
import atexit
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timezone
import logging

from .fsm import JobFSM, JobState, StateTransition

logger = logging.getLogger(__name__)


class CrashRecovery:
    """Manages crash recovery for FSM operations."""

    def __init__(self, workspace: Path):
        """Initialize crash recovery system.

        Args:
            workspace: Path to workspace directory
        """
        self.workspace = workspace
        self.active_fsms: Dict[str, JobFSM] = {}
        self.cleanup_handlers_registered = False

        # Register signal handlers for graceful shutdown
        self._register_signal_handlers()

        # Register atexit handler for cleanup
        atexit.register(self._cleanup_all_fsms)

    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        if self.cleanup_handlers_registered:
            return

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self._cleanup_all_fsms()
            exit(0)

        # Register common termination signals
        for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]:
            signal.signal(sig, signal_handler)

        self.cleanup_handlers_registered = True

    def _cleanup_all_fsms(self) -> None:
        """Clean up all active FSMs."""
        for job_id, fsm in self.active_fsms.items():
            try:
                self._safe_shutdown_fsm(fsm)
            except Exception as e:
                logger.error(f"Error shutting down FSM {job_id}: {e}")

        self.active_fsms.clear()

    def _safe_shutdown_fsm(self, fsm: JobFSM) -> None:
        """Safely shutdown an FSM.

        Args:
            fsm: FSM to shutdown
        """
        # If FSM is in PLOTTING state, try to pause/abort
        if fsm.current_state in [JobState.PLOTTING, JobState.ARMED]:
            logger.warning(
                f"Emergency shutdown for job {fsm.job_id} in state {fsm.current_state.value}"
            )

            # Write emergency shutdown to journal
            fsm._write_journal(
                {
                    "type": "emergency_shutdown",
                    "state": fsm.current_state.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "reason": "signal_received",
                }
            )

            # Try to abort the job
            fsm.abort_job("Emergency shutdown")

    def register_fsm(self, fsm: JobFSM) -> None:
        """Register an FSM for crash recovery.

        Args:
            fsm: FSM to register
        """
        self.active_fsms[fsm.job_id] = fsm
        logger.info(f"Registered FSM for crash recovery: {fsm.job_id}")

    def unregister_fsm(self, fsm: JobFSM) -> None:
        """Unregister an FSM from crash recovery.

        Args:
            fsm: FSM to unregister
        """
        if fsm.job_id in self.active_fsms:
            del self.active_fsms[fsm.job_id]
            logger.info(f"Unregistered FSM from crash recovery: {fsm.job_id}")

    def recover_job(self, job_id: str) -> Optional[JobFSM]:
        """Recover a job from journal after crash.

        Args:
            job_id: Job identifier to recover

        Returns:
            Recovered FSM or None if not recoverable
        """
        job_dir = self.workspace / "jobs" / job_id
        journal_file = job_dir / "journal.jsonl"

        if not journal_file.exists():
            logger.warning(f"No journal found for job {job_id}")
            return None

        try:
            # Read journal to determine last state
            last_state = None
            emergency_shutdown = False

            with open(journal_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line.strip())

                        # Check for emergency shutdown
                        if entry.get("type") == "emergency_shutdown":
                            emergency_shutdown = True
                            last_state = JobState[entry["state"]]

                        # Track state changes
                        elif entry.get("type") == "state_change":
                            last_state = JobState[entry["to_state"]]

                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Invalid journal entry: {e}")
                        continue

            if not last_state:
                logger.warning(f"No valid state found in journal for job {job_id}")
                return None

            # Create FSM in recovered state
            fsm = JobFSM(job_id, self.workspace)
            fsm.current_state = last_state

            # Load transition history from journal
            with open(journal_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line.strip())
                        if entry.get("type") == "state_change":
                            transition = StateTransition(
                                from_state=JobState[entry["from_state"]],
                                to_state=JobState[entry["to_state"]],
                                timestamp=datetime.fromisoformat(entry["timestamp"]),
                                reason=entry.get("reason", ""),
                                metadata=entry.get("metadata", {}),
                            )
                            fsm.transitions.append(transition)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

            # Add recovery transition to history
            if emergency_shutdown:
                recovery_transition = StateTransition(
                    from_state=last_state,
                    to_state=last_state,
                    timestamp=datetime.now(timezone.utc),
                    reason="Crash recovery",
                    metadata={"emergency_shutdown": True},
                )
                fsm.transitions.append(recovery_transition)

                # Write recovery to journal
                fsm._write_journal(
                    {
                        "type": "recovery",
                        "from_state": last_state.value,
                        "to_state": last_state.value,
                        "reason": "Crash recovery after emergency shutdown",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

            logger.info(f"Recovered job {job_id} in state {last_state.value}")
            return fsm

        except Exception as e:
            logger.error(f"Failed to recover job {job_id}: {e}")
            return None

    def get_resumable_jobs(self) -> List[str]:
        """Get list of jobs that can be resumed.

        Returns:
            List of resumable job IDs
        """
        jobs_dir = self.workspace / "jobs"
        if not jobs_dir.exists():
            return []

        resumable = []

        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue

            job_id = job_dir.name
            journal_file = job_dir / "journal.jsonl"

            if not journal_file.exists():
                continue

            try:
                # Check if job is in a non-terminal state
                with open(journal_file, "r") as f:
                    last_state_change = None
                    for line in reversed(list(f)):  # Read from end
                        if not line.strip():
                            continue

                        try:
                            entry = json.loads(line.strip())
                            if entry.get("type") == "state_change":
                                last_state_change = entry
                                break  # Found the last state change
                        except (json.JSONDecodeError, KeyError):
                            continue

                    # If we found a state change, check if it's resumable
                    if last_state_change:
                        state = JobState[last_state_change["to_state"]]
                        # Job is resumable if not in terminal state
                        if state not in [
                            JobState.COMPLETED,
                            JobState.ABORTED,
                        ]:
                            resumable.append(job_id)

            except Exception as e:
                logger.warning(f"Error checking resumability of {job_id}: {e}")
                continue

        return resumable

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get detailed status of a job from journal.

        Args:
            job_id: Job identifier

        Returns:
            Status dictionary
        """
        job_dir = self.workspace / "jobs" / job_id
        journal_file = job_dir / "journal.jsonl"

        if not journal_file.exists():
            return {"error": "Job not found"}

        try:
            entries = []
            current_state = None
            last_transition = None
            emergency_shutdown = False

            with open(journal_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line.strip())
                        entries.append(entry)

                        if entry.get("type") == "emergency_shutdown":
                            emergency_shutdown = True
                            current_state = JobState[entry["state"]]
                        elif entry.get("type") == "state_change":
                            current_state = JobState[entry["to_state"]]
                            last_transition = entry

                    except (json.JSONDecodeError, KeyError):
                        continue

            # Get job file info
            job_file = job_dir / "job.json"
            job_info = {}
            if job_file.exists():
                with open(job_file, "r") as f:
                    job_info = json.load(f)

            return {
                "job_id": job_id,
                "current_state": current_state.value if current_state else None,
                "emergency_shutdown": emergency_shutdown,
                "last_transition": last_transition,
                "job_info": job_info,
                "journal_entries": len(entries),
                "resumable": (
                    current_state not in [JobState.COMPLETED, JobState.ABORTED]
                    if current_state
                    else False
                ),
            }

        except Exception as e:
            return {"error": str(e)}

    def cleanup_journal(self, job_id: str, keep_entries: int = 100) -> bool:
        """Clean up old journal entries to prevent growth.

        Args:
            job_id: Job identifier
            keep_entries: Number of recent entries to keep

        Returns:
            True if cleanup successful
        """
        job_dir = self.workspace / "jobs" / job_id
        journal_file = job_dir / "journal.jsonl"

        if not journal_file.exists():
            return False

        try:
            # Read all entries
            entries = []
            with open(journal_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            entries.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue

            # Keep only recent entries
            if len(entries) <= keep_entries:
                return True  # No cleanup needed

            recent_entries = entries[-keep_entries:]

            # Write back recent entries
            with open(journal_file, "w") as f:
                for entry in recent_entries:
                    f.write(json.dumps(entry) + "\n")

            logger.info(
                f"Cleaned journal for {job_id}: {len(entries) - keep_entries} old entries removed"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to cleanup journal for {job_id}: {e}")
            return False


# Global crash recovery instance
_crash_recovery_instance: Optional[CrashRecovery] = None


def get_crash_recovery(workspace: Path) -> CrashRecovery:
    """Get or create global crash recovery instance.

    Args:
        workspace: Path to workspace directory

    Returns:
        CrashRecovery instance
    """
    global _crash_recovery_instance

    if _crash_recovery_instance is None:
        _crash_recovery_instance = CrashRecovery(workspace)

    return _crash_recovery_instance


def requeue_job_to_front(job_id: str, workspace: Path) -> bool:
    """Move job to front of queue by updating timestamp and priority.

    Args:
        job_id: Job identifier to requeue
        workspace: Path to workspace directory

    Returns:
        True if successful, False otherwise
    """
    try:
        job_file = workspace / "jobs" / job_id / "job.json"
        if not job_file.exists():
            logger.warning(f"Job file not found for requeue: {job_id}")
            return False

        job_data = json.loads(job_file.read_text())

        # Set to far future timestamp to ensure front position
        # and add high priority flag
        job_data["updated_at"] = datetime(2100, 1, 1, tzinfo=timezone.utc).isoformat()
        job_data["queue_priority"] = 1  # High priority flag

        job_file.write_text(json.dumps(job_data, indent=2))
        logger.info(f"Requeued job {job_id} to front of queue")
        return True

    except Exception as e:
        logger.error(f"Failed to requeue job {job_id} to front: {e}")
        return False


def requeue_job_to_end(job_id: str, workspace: Path) -> bool:
    """Move job to end of queue with current timestamp.

    Args:
        job_id: Job identifier to requeue
        workspace: Path to workspace directory

    Returns:
        True if successful, False otherwise
    """
    try:
        job_file = workspace / "jobs" / job_id / "job.json"
        if not job_file.exists():
            logger.warning(f"Job file not found for requeue: {job_id}")
            return False

        job_data = json.loads(job_file.read_text())

        # Set to current time for end position
        # and normal priority
        job_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        job_data["queue_priority"] = 0  # Normal priority

        job_file.write_text(json.dumps(job_data, indent=2))
        logger.info(f"Requeued job {job_id} to end of queue")
        return True

    except Exception as e:
        logger.error(f"Failed to requeue job {job_id} to end: {e}")
        return False


def detect_interrupted_jobs(
    workspace: Path, grace_minutes: int = 5
) -> List[Dict[str, Any]]:
    """Detect jobs that should have finished but are still PLOTTING.

    Args:
        workspace: Path to workspace directory
        grace_minutes: Grace period beyond estimated end time

    Returns:
        List of interrupted job information
    """
    from datetime import datetime, timedelta

    current_time = datetime.now(timezone.utc)
    interrupted = []

    jobs_dir = workspace / "jobs"
    if not jobs_dir.exists():
        return interrupted

    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue

        job_file = job_dir / "job.json"
        if not job_file.exists():
            continue

        try:
            job_data = json.loads(job_file.read_text())
            if job_data.get("state") != "PLOTTING":
                continue

            # Check if we have timing data
            est_end_time_str = job_data.get("estimated_end_time")
            if not est_end_time_str:
                continue

            est_end_time = datetime.fromisoformat(
                est_end_time_str.replace("Z", "+00:00")
            )
            grace_period = timedelta(minutes=grace_minutes)

            if current_time > est_end_time + grace_period:
                overdue_minutes = (current_time - est_end_time).total_seconds() / 60
                interrupted.append(
                    {
                        "job_id": job_dir.name,
                        "job_data": job_data,
                        "overdue_minutes": overdue_minutes,
                        "estimated_end_time": est_end_time_str,
                        "plotting_started_at": job_data.get("plotting_started_at"),
                    }
                )
        except Exception as e:
            logger.warning(f"Error checking job {job_dir.name} for interrupts: {e}")
            continue

    return interrupted


def prompt_interrupted_resume(interrupted_jobs: List[Dict[str, Any]]) -> bool:
    """Prompt user to resume interrupted jobs.

    Args:
        interrupted_jobs: List of interrupted job information

    Returns:
        True if user chose to resume, False otherwise
    """
    if not interrupted_jobs:
        return False

    try:
        from rich.console import Console
        from rich.prompt import Confirm

        console = Console()
    except ImportError:
        console = None
        Confirm = None

    # Show interrupted jobs
    if console:
        console.print("⚠️  Interrupted plot(s) detected:", style="yellow")
        for job in interrupted_jobs:
            job_id = job["job_id"]
            overdue = job["overdue_minutes"]
            end_time = job["estimated_end_time"]
            console.print(
                f"  • {job_id} - {overdue:.1f}min overdue (was due at {end_time})"
            )
    else:
        print("Interrupted plot(s) detected:")
        for job in interrupted_jobs:
            job_id = job["job_id"]
            overdue = job["overdue_minutes"]
            print(f"  • {job_id} - {overdue:.1f}min overdue")

    # Ask if user wants to resume
    if len(interrupted_jobs) == 1:
        prompt_text = f"Resume interrupted job {interrupted_jobs[0]['job_id']}?"
    else:
        prompt_text = f"Resume {len(interrupted_jobs)} interrupted jobs?"

    if console and Confirm:
        return Confirm.ask(prompt_text, default=True)
    else:
        response = input(f"{prompt_text} [Y/n]: ").strip().lower()
        return response in ["y", "yes", ""]


def resume_all_jobs(workspace: Path) -> List[JobFSM]:
    """Resume all resumable jobs.

    Args:
        workspace: Path to workspace directory

    Returns:
        List of resumed FSMs
    """
    recovery = get_crash_recovery(workspace)
    resumable_jobs = recovery.get_resumable_jobs()

    resumed = []
    for job_id in resumable_jobs:
        fsm = recovery.recover_job(job_id)
        if fsm:
            resumed.append(fsm)
            recovery.register_fsm(fsm)

    logger.info(f"Resumed {len(resumed)} jobs: {[fsm.job_id for fsm in resumed]}")
    return resumed
