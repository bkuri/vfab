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
        from ..db import get_session

        try:
            with get_session() as session:
                # Import models here to avoid circular imports
                from ..models import Job, Paper

                # Get the current job
                job = session.query(Job).filter(Job.id == job_id).first()
                if not job:
                    return GuardCheck(
                        "paper_session_valid",
                        GuardResult.FAIL,
                        f"Job {job_id} not found",
                        {"error": "job_not_found"},
                    )

                # Check if job has paper assigned
                if job.paper_id is None:
                    return GuardCheck(
                        "paper_session_valid",
                        GuardResult.FAIL,
                        "Job has no paper assigned",
                        {"job_id": job_id, "paper_id": None},
                    )

                # Check if there are other active jobs with the same paper
                # Active jobs are those in states that would conflict with paper usage
                active_states = ["QUEUED", "ARMED", "PLOTTING", "PAUSED"]
                conflicting_jobs = (
                    session.query(Job)
                    .filter(
                        Job.paper_id == job.paper_id,
                        Job.id != job_id,
                        Job.state.in_(active_states),
                    )
                    .all()
                )

                if conflicting_jobs:
                    job_ids = [str(j.id) for j in conflicting_jobs]
                    return GuardCheck(
                        "paper_session_valid",
                        GuardResult.FAIL,
                        f"Paper already in use by jobs: {', '.join(job_ids)}",
                        {
                            "job_id": job_id,
                            "paper_id": job.paper_id,
                            "conflicting_jobs": job_ids,
                        },
                    )

                # Get paper details for context
                paper = session.query(Paper).filter(Paper.id == job.paper_id).first()
                paper_name = paper.name if paper else f"ID:{job.paper_id}"

                return GuardCheck(
                    "paper_session_valid",
                    GuardResult.PASS,
                    f"Paper '{paper_name}' is available for job {job_id}",
                    {
                        "job_id": job_id,
                        "paper_id": job.paper_id,
                        "paper_name": paper_name,
                    },
                )

        except Exception as e:
            return GuardCheck(
                "paper_session_valid",
                GuardResult.FAIL,
                f"Failed to validate paper session: {str(e)}",
                {"error": str(e), "job_id": job_id},
            )


class PenLayerGuard(Guard):
    """Guard for checking pen-layer compatibility."""

    def check(self, job_id: str) -> GuardCheck:
        """Check if pen configuration is compatible with layers."""
        from ..db import get_session

        try:
            with get_session() as session:
                # Import models here to avoid circular imports
                from ..models import Job, Layer, Pen

                # Get the current job with layers
                job = session.query(Job).filter(Job.id == job_id).first()
                if not job:
                    return GuardCheck(
                        "pen_layer_compatible",
                        GuardResult.FAIL,
                        f"Job {job_id} not found",
                        {"error": "job_not_found"},
                    )

                # Get all layers for this job, ordered by index
                layers = (
                    session.query(Layer)
                    .filter(Layer.job_id == job_id)
                    .order_by(Layer.order_index)
                    .all()
                )

                if not layers:
                    return GuardCheck(
                        "pen_layer_compatible",
                        GuardResult.SOFT_FAIL,
                        f"Job {job_id} has no layers defined",
                        {"job_id": job_id, "layer_count": 0},
                    )

                # Check each layer for pen compatibility
                issues = []
                compatible_layers = 0
                layer_details = []

                for layer in layers:
                    layer_info = {
                        "layer_name": layer.layer_name,
                        "order_index": layer.order_index,
                        "pen_id": layer.pen_id,
                    }

                    if layer.pen_id is None:
                        issues.append(f"Layer '{layer.layer_name}' has no pen assigned")
                        layer_info["status"] = "no_pen"
                    else:
                        # Check if pen exists
                        pen = session.query(Pen).filter(Pen.id == layer.pen_id).first()
                        if not pen:
                            issues.append(
                                f"Layer '{layer.layer_name}' references non-existent pen ID {layer.pen_id}"
                            )
                            layer_info["status"] = "pen_not_found"
                        else:
                            layer_info["pen_name"] = pen.name
                            layer_info["status"] = "compatible"
                            compatible_layers += 1

                    layer_details.append(layer_info)

                # Determine overall result
                total_layers = len(layers)
                if len(issues) == 0:
                    return GuardCheck(
                        "pen_layer_compatible",
                        GuardResult.PASS,
                        f"All {total_layers} layers have compatible pen assignments",
                        {
                            "job_id": job_id,
                            "total_layers": total_layers,
                            "compatible_layers": compatible_layers,
                            "layers": layer_details,
                        },
                    )
                else:
                    # If some layers are compatible but others have issues, it's a soft fail
                    # If no layers are compatible, it's a hard fail
                    result = (
                        GuardResult.SOFT_FAIL
                        if compatible_layers > 0
                        else GuardResult.FAIL
                    )

                    return GuardCheck(
                        "pen_layer_compatible",
                        result,
                        f"Pen-layer compatibility issues found: {'; '.join(issues)}",
                        {
                            "job_id": job_id,
                            "total_layers": total_layers,
                            "compatible_layers": compatible_layers,
                            "issues": issues,
                            "layers": layer_details,
                        },
                    )

        except Exception as e:
            return GuardCheck(
                "pen_layer_compatible",
                GuardResult.FAIL,
                f"Failed to validate pen-layer compatibility: {str(e)}",
                {"error": str(e), "job_id": job_id},
            )
