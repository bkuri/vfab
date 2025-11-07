"""
Job-level guards for checklist, paper session, and pen validation.
"""

from __future__ import annotations

from pathlib import Path
from .base import Guard, GuardCheck, GuardResult

# Import optional modules
try:
    from ..checklist import create_checklist
except ImportError:
    create_checklist = None


class ChecklistGuard(Guard):
    """Guard for checking checklist completion."""

    def check(self, job_id: str, workspace: Path) -> GuardCheck:
        """Check if checklist is complete for a job."""
        if create_checklist is None:
            return GuardCheck(
                "checklist_complete",
                GuardResult.SKIPPED,
                "Checklist system not available",
                {"warning": "checklist_not_available"},
            )

        try:
            checklist = create_checklist(job_id, workspace / "jobs" / job_id)
            if checklist is None:
                return GuardCheck(
                    "checklist_complete",
                    GuardResult.SOFT_FAIL,
                    "Could not load checklist",
                    {"error": "checklist_load_failed"},
                )

            progress = checklist.get_progress()
            if progress["required_completed"] < progress["required_total"]:
                missing = progress["required_total"] - progress["required_completed"]
                return GuardCheck(
                    "checklist_complete",
                    GuardResult.FAIL,
                    f"{missing} required checklist items incomplete",
                    {
                        "required_completed": progress["required_completed"],
                        "required_total": progress["required_total"],
                        "missing": missing,
                    },
                )

            return GuardCheck(
                "checklist_complete",
                GuardResult.PASS,
                "All required checklist items complete",
                progress,
            )

        except Exception as e:
            return GuardCheck(
                "checklist_complete",
                GuardResult.SOFT_FAIL,
                f"Checklist check failed: {str(e)}",
                {"error": str(e)},
            )


class PaperSessionGuard(Guard):
    """Guard for checking paper session validity."""

    def check(self, job_id: str) -> GuardCheck:
        """Check if paper session is valid."""
        # TODO: Implement paper session validation
        return GuardCheck(
            "paper_session_valid",
            GuardResult.SKIPPED,
            "Paper session validation not implemented",
            {"warning": "not_implemented"},
        )


class PenLayerGuard(Guard):
    """Guard for checking pen-layer compatibility."""

    def check(self, job_id: str) -> GuardCheck:
        """Check if pen configuration is compatible with layers."""
        # TODO: Implement pen-layer compatibility validation
        return GuardCheck(
            "pen_layer_compatible",
            GuardResult.SKIPPED,
            "Pen-layer compatibility check not implemented",
            {"warning": "not_implemented"},
        )
