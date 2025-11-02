"""
Finite State Machine implementation for ploTTY job lifecycle.

This module implements the core FSM that manages job states according to the PRD:
NEW → QUEUED → ANALYZED → OPTIMIZED → READY → ARMED → PLOTTING → (PAUSED) → COMPLETED | ABORTED | FAILED
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json
import logging
from pathlib import Path

from .config import load_config
from .planner import plan_layers
from .estimation import features, estimate_seconds

logger = logging.getLogger(__name__)

# Import optional modules
try:
    from .hooks import create_hook_executor
except ImportError:

    def create_hook_executor(job_id, workspace):
        return None


try:
    from .guards import create_guard_system
except ImportError:

    def create_guard_system(config, workspace):
        return None


try:
    from .crash_recovery import get_crash_recovery
except ImportError:

    def get_crash_recovery(workspace):
        return None


try:
    from .checklist import create_checklist
except ImportError:

    def create_checklist(job_id, job_dir):
        return None


class JobState(Enum):
    """Job states as defined in the PRD."""

    NEW = "NEW"
    QUEUED = "QUEUED"
    ANALYZED = "ANALYZED"
    OPTIMIZED = "OPTIMIZED"
    READY = "READY"
    ARMED = "ARMED"
    PLOTTING = "PLOTTING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"


@dataclass
class StateTransition:
    """Represents a state transition with metadata."""

    from_state: JobState
    to_state: JobState
    timestamp: datetime
    reason: str
    metadata: Dict[str, Any]


class JobFSM:
    """Finite State Machine for managing job lifecycle."""

    # Valid state transitions as per PRD
    VALID_TRANSITIONS = {
        JobState.NEW: [JobState.QUEUED],
        JobState.QUEUED: [JobState.ANALYZED, JobState.ABORTED],
        JobState.ANALYZED: [JobState.OPTIMIZED, JobState.FAILED],
        JobState.OPTIMIZED: [JobState.READY, JobState.FAILED],
        JobState.READY: [JobState.ARMED, JobState.ABORTED],
        JobState.ARMED: [JobState.PLOTTING, JobState.ABORTED],
        JobState.PLOTTING: [
            JobState.PAUSED,
            JobState.COMPLETED,
            JobState.ABORTED,
            JobState.FAILED,
        ],
        JobState.PAUSED: [JobState.PLOTTING, JobState.ABORTED],
        JobState.COMPLETED: [],  # Terminal state
        JobState.ABORTED: [],  # Terminal state
        JobState.FAILED: [],  # Terminal state
    }

    def __init__(self, job_id: str, workspace: Path):
        """Initialize FSM for a job.

        Args:
            job_id: Unique job identifier
            workspace: Path to workspace directory
        """
        self.job_id = job_id
        self.workspace = workspace
        self.job_dir = workspace / "jobs" / job_id
        self.current_state = JobState.NEW
        self.transitions: List[StateTransition] = []
        self.config = load_config()
        self.hook_executor = create_hook_executor(job_id, workspace)
        self.guard_system = create_guard_system(self.config, workspace)
        self._last_guard_checks: List[Any] = []

        # Initialize journal file for crash recovery
        self.journal_file = self.job_dir / "journal.jsonl"
        self._load_journal()

        # Register with crash recovery system
        try:
            crash_recovery = get_crash_recovery(workspace)
            if crash_recovery is not None:
                crash_recovery.register_fsm(self)
        except Exception:
            # Crash recovery not available, continue without it
            pass

    def _load_journal(self) -> None:
        """Load existing journal for crash recovery."""
        if self.journal_file.exists():
            try:
                with open(self.journal_file, "r") as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        if entry.get("type") == "state_change":
                            self.current_state = JobState(entry["to_state"])
            except Exception:
                # If journal is corrupted, start fresh
                self.current_state = JobState.NEW

    def _write_journal(self, entry: Dict[str, Any]) -> None:
        """Write entry to journal file."""
        self.job_dir.mkdir(parents=True, exist_ok=True)
        with open(self.journal_file, "a") as f:
            f.write(
                json.dumps(
                    {
                        **entry,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "job_id": self.job_id,
                    }
                )
                + "\n"
            )
            f.flush()

    def can_transition_to(self, target_state: JobState) -> bool:
        """Check if transition to target state is valid."""
        # First check FSM state rules
        if target_state not in self.VALID_TRANSITIONS.get(self.current_state, []):
            return False

        # Then check guards for target state
        if self.guard_system is not None:
            can_transition, guard_checks = self.guard_system.can_transition(
                self.job_id, target_state.value, self.current_state.value
            )
        else:
            # No guard system available - allow transition
            can_transition, guard_checks = True, []

        # Store guard results for logging
        self._last_guard_checks = guard_checks

        return can_transition

    def transition_to(
        self,
        target_state: JobState,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Transition to target state if valid.

        Args:
            target_state: Target state to transition to
            reason: Reason for transition
            metadata: Additional metadata about transition

        Returns:
            True if transition succeeded, False otherwise
        """
        if not self.can_transition_to(target_state):
            return False

        transition = StateTransition(
            from_state=self.current_state,
            to_state=target_state,
            timestamp=datetime.now(timezone.utc),
            reason=reason,
            metadata=metadata or {},
        )

        self.transitions.append(transition)
        self.current_state = target_state

        # Write to journal for crash recovery
        self._write_journal(
            {
                "type": "state_change",
                "from_state": transition.from_state.value,
                "to_state": transition.to_state.value,
                "reason": reason,
                "metadata": metadata or {},
            }
        )

        # Update job file
        self._update_job_file()

        # Execute hooks for the new state
        self._execute_hooks(target_state, reason, metadata or {})

        return True

    def _update_job_file(self) -> None:
        """Update job.json file with current state."""
        job_file = self.job_dir / "job.json"
        if job_file.exists():
            with open(job_file, "r") as f:
                job_data = json.load(f)
            job_data["state"] = self.current_state.value
            job_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(job_file, "w") as f:
                json.dump(job_data, f, indent=2)

    def get_state_history(self) -> List[Dict[str, Any]]:
        """Get history of state transitions."""
        return [
            {
                "from_state": t.from_state.value,
                "to_state": t.to_state.value,
                "timestamp": t.timestamp.isoformat(),
                "reason": t.reason,
                "metadata": t.metadata,
            }
            for t in self.transitions
        ]

    # State-specific methods implementing PRD user stories

    def queue_job(self, src_path: str, name: str = "", paper: str = "A3") -> bool:
        """Queue a new job (User Story 1)."""
        if self.current_state != JobState.NEW:
            return False

        # Copy source file and create job metadata

        src_file = Path(src_path)
        (self.job_dir / "src.svg").write_bytes(src_file.read_bytes())

        job_data = {
            "id": self.job_id,
            "name": name or src_file.stem,
            "paper": paper,
            "state": JobState.QUEUED.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(self.job_dir / "job.json", "w") as f:
            json.dump(job_data, f, indent=2)

        return self.transition_to(JobState.QUEUED, f"Job queued: {name}", {})

    def analyze_job(self) -> bool:
        """Analyze job geometry and features."""
        if self.current_state != JobState.QUEUED:
            return False

        try:
            src_svg = self.job_dir / "src.svg"
            job_features = features(src_svg)

            # Store analysis results
            analysis = {
                "features": job_features.__dict__,
                "estimated_time": estimate_seconds(job_features, {}),
            }

            with open(self.job_dir / "analysis.json", "w") as f:
                json.dump(analysis, f, indent=2)

            return self.transition_to(JobState.ANALYZED, "Analysis completed", analysis)
        except Exception as e:
            return self.transition_to(
                JobState.FAILED, f"Analysis failed: {str(e)}", {"error": str(e)}
            )

    def optimize_job(
        self, pen_map: Optional[Dict[str, str]] = None, interactive: bool = False
    ) -> bool:
        """Optimize job via vpype with multi-pen support (User Story 2)."""
        if self.current_state != JobState.ANALYZED:
            return False

        try:
            # Load available pens from database if available
            available_pens = []
            try:
                from .db import get_session
                from .models import Pen

                with get_session() as session:
                    pens = session.query(Pen).all()
                    available_pens = [
                        {
                            "id": pen.id,
                            "name": pen.name,
                            "width_mm": pen.width_mm,
                            "speed_cap": pen.speed_cap,
                            "pressure": pen.pressure,
                            "passes": pen.passes,
                            "color_hex": pen.color_hex,
                        }
                        for pen in pens
                    ]
            except Exception:
                # Database not available, continue without pen info
                pass

            # Use enhanced multi-pen planning
            result = plan_layers(
                self.job_dir / "src.svg",
                self.config.vpype.preset,
                self.config.vpype.presets_file,
                pen_map or {},
                self.job_dir,
                available_pens,
                interactive,
            )

            with open(self.job_dir / "plan.json", "w") as f:
                json.dump(result, f, indent=2)

            # Store layer information for plotting
            self.layers = result["layers"]
            self.pen_map = result["pen_map"]

            return self.transition_to(
                JobState.OPTIMIZED,
                f"Multi-pen optimization completed: {result['layer_count']} layers",
                result,
            )
        except Exception as e:
            return self.transition_to(
                JobState.FAILED, f"Optimization failed: {str(e)}", {"error": str(e)}
            )

    def ready_job(self) -> bool:
        """Mark job as ready after optimization."""
        if self.current_state != JobState.OPTIMIZED:
            return False

        return self.transition_to(JobState.READY, "Job ready for plotting", {})

    def arm_job(self) -> bool:
        """Arm job for plotting (pre-flight checks)."""
        if self.current_state != JobState.READY:
            return False

        # Validate checklist before arming
        if create_checklist is not None:
            try:
                checklist = create_checklist(self.job_id, self.job_dir)
                if checklist is not None:
                    progress = checklist.get_progress()

                    # Check if all required items are completed
                    if progress["required_completed"] < progress["required_total"]:
                        missing = (
                            progress["required_total"] - progress["required_completed"]
                        )
                        return self.transition_to(
                            JobState.READY,
                            f"Cannot arm job: {missing} required checklist items incomplete",
                            {},
                        )

                    logger.info(
                        f"Checklist validation passed: {progress['required_completed']}/{progress['required_total']} required items complete"
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to validate checklist for job {self.job_id}: {e}"
                )
                # Continue with arming but log the issue

        return self.transition_to(JobState.ARMED, "Job armed for plotting", {})

    def start_plotting(self) -> bool:
        """Start plotting job."""
        if self.current_state != JobState.ARMED:
            return False

        return self.transition_to(JobState.PLOTTING, "Plotting started", {})

    def pause_plotting(self) -> bool:
        """Pause plotting."""
        if self.current_state != JobState.PLOTTING:
            return False

        return self.transition_to(JobState.PAUSED, "Plotting paused", {})

    def resume_plotting(self) -> bool:
        """Resume plotting."""
        if self.current_state != JobState.PAUSED:
            return False

        return self.transition_to(JobState.PLOTTING, "Plotting resumed", {})

    def complete_job(self, metrics: Optional[Dict[str, Any]] = None) -> bool:
        """Complete job successfully."""
        if self.current_state not in [JobState.PLOTTING, JobState.PAUSED]:
            return False

        return self.transition_to(JobState.COMPLETED, "Job completed", metrics or {})

    def abort_job(self, reason: str = "") -> bool:
        """Abort job."""
        if self.current_state in [
            JobState.COMPLETED,
            JobState.ABORTED,
            JobState.FAILED,
        ]:
            return False

        return self.transition_to(JobState.ABORTED, f"Job aborted: {reason}", {})

    def fail_job(self, error: str) -> bool:
        """Mark job as failed."""
        if self.current_state in [
            JobState.COMPLETED,
            JobState.ABORTED,
            JobState.FAILED,
        ]:
            return False

        return self.transition_to(
            JobState.FAILED, f"Job failed: {error}", {"error": error}
        )

    def _execute_hooks(
        self, state: JobState, reason: str, metadata: Dict[str, Any]
    ) -> None:
        """Execute hooks for a state transition.

        Args:
            state: Target state
            reason: Transition reason
            metadata: Transition metadata
        """
        try:
            # Get hooks for this state from config
            state_hooks = getattr(self.config.hooks, state.value, [])

            if not state_hooks:
                return

            # Get context for variable substitution
            if self.hook_executor is not None:
                context = self.hook_executor.get_context(state.value, metadata)
                context["reason"] = reason

                # Execute hooks
                results = self.hook_executor.execute_hooks(state_hooks, context)
            else:
                results = []  # No hook executor available

            # Write hook results to journal
            self._write_journal(
                {
                    "type": "hooks_executed",
                    "state": state.value,
                    "reason": reason,
                    "results": results,
                }
            )

            # Write guard results to journal if available
            if hasattr(self, "_last_guard_checks"):
                self._write_journal(
                    {
                        "type": "guards_evaluated",
                        "state": state.value,
                        "checks": [
                            check.to_dict() for check in self._last_guard_checks
                        ],
                    }
                )

        except Exception as e:
            # Log hook execution errors but don't fail the transition
            self._write_journal(
                {"type": "hooks_error", "state": state.value, "error": str(e)}
            )

    def get_last_guard_results(self) -> List[Dict[str, Any]]:
        """Get results from last guard evaluation.

        Returns:
            List of guard check results
        """
        if hasattr(self, "_last_guard_checks"):
            return [check.to_dict() for check in self._last_guard_checks]
        return []


def create_fsm(job_id: str, workspace: Path) -> JobFSM:
    """Factory function to create FSM for a job."""
    return JobFSM(job_id, workspace)
