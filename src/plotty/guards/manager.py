"""
Guard system manager for coordinating multiple guards.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import logging

from .base import GuardCheck, GuardResult
from .system_guards import DeviceGuard, CameraGuard
from .job_guards import ChecklistGuard, PaperSessionGuard, PenLayerGuard

logger = logging.getLogger(__name__)


class GuardSystem:
    """Manages and coordinates multiple guards."""

    def __init__(self, config, workspace: Path):
        self.config = config
        self.workspace = workspace
        self.device_guard = DeviceGuard(config)
        self.camera_guard = CameraGuard(config)
        self.checklist_guard = ChecklistGuard(config)
        self.paper_session_guard = PaperSessionGuard(config)
        self.pen_layer_guard = PenLayerGuard(config)

        self.guards = {
            "device_idle": self.device_guard,
            "camera_health": self.camera_guard,
            "checklist_complete": self.checklist_guard,
            "paper_session_valid": self.paper_session_guard,
            "pen_layer_compatible": self.pen_layer_guard,
        }

    def check_all(self, job_id: str) -> List[GuardCheck]:
        """Run all guards and return results."""
        results = []

        for guard_name, guard in self.guards.items():
            try:
                if guard_name == "checklist_complete":
                    result = guard.check(job_id, self.workspace)
                else:
                    result = guard.check(job_id)
                results.append(result)

                # Log guard results
                if result.result == GuardResult.FAIL:
                    logger.error(f"Guard {guard_name} failed: {result.message}")
                elif result.result == GuardResult.SOFT_FAIL:
                    logger.warning(f"Guard {guard_name} soft-failed: {result.message}")
                else:
                    logger.info(f"Guard {guard_name} passed: {result.message}")

            except Exception as e:
                logger.error(f"Guard {guard_name} threw exception: {e}")
                results.append(
                    GuardCheck(
                        guard_name,
                        GuardResult.FAIL,
                        f"Guard execution failed: {str(e)}",
                        {"error": str(e)},
                    )
                )

        return results

    def check_guard(self, guard_name: str, job_id: str) -> GuardCheck:
        """Check a specific guard."""
        if guard_name not in self.guards:
            return GuardCheck(
                guard_name,
                GuardResult.FAIL,
                f"Unknown guard: {guard_name}",
                {"error": "unknown_guard"},
            )

        guard = self.guards[guard_name]
        try:
            if guard_name == "checklist_complete":
                return guard.check(job_id, self.workspace)
            else:
                return guard.check(job_id)
        except Exception as e:
            return GuardCheck(
                guard_name,
                GuardResult.FAIL,
                f"Guard execution failed: {str(e)}",
                {"error": str(e)},
            )

    def evaluate_guards(
        self, job_id: str, target_state: str, current_state: str = None
    ) -> List[GuardCheck]:
        """Evaluate guards for a state transition."""
        guards = []

        # Determine which guards to check based on target state
        if target_state in ["ARMED", "PLOTTING"]:
            # Device must be idle for armed/plotting states
            guards.append(self.device_guard.check(job_id))

            # Checklist must be complete for armed state
            if target_state == "ARMED":
                guards.append(self.checklist_guard.check(job_id, self.workspace))

                # Paper session guard - one paper per session
                if (
                    hasattr(self.config, "paper")
                    and hasattr(self.config.paper, "require_one_per_session")
                    and self.config.paper.require_one_per_session
                ):
                    guards.append(self.paper_session_guard.check(job_id))

                # Pen layer guard - one pen per layer
                guards.append(self.pen_layer_guard.check(job_id))

        # Camera health check (soft-fail allowed) for plotting states
        if target_state == "PLOTTING":
            guards.append(self.camera_guard.check(job_id))

        return guards

    def can_transition(
        self, job_id: str, target_state: str, current_state: str = None
    ) -> tuple[bool, List[GuardCheck]]:
        """Check if transition is allowed by guards."""
        guard_checks = self.evaluate_guards(job_id, target_state, current_state)

        # Check for any hard failures
        hard_failures = [g for g in guard_checks if g.result == GuardResult.FAIL]

        can_transition = len(hard_failures) == 0

        return can_transition, guard_checks


def create_guard_system(config, workspace: Path):
    """Factory function to create guard system."""
    return GuardSystem(config, workspace)
