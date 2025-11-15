"""
List jobs command for vfab CLI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import typer
import json

from ...config import load_config
from ...utils import error_handler
from ...progress import show_status
from ..info.output import get_output_manager
from ...recovery import get_crash_recovery


def jobs(
    state: Optional[str] = typer.Option(
        None,
        "--state",
        "-s",
        help="Filter by job state (NEW, QUEUED, OPTIMIZED, READY, PLOTTING, COMPLETED, FAILED, etc.)",
    ),
    failed: bool = typer.Option(
        False, "--failed", help="Show failed and resumable (interrupted) jobs"
    ),
    resumed: bool = typer.Option(False, "--resumed", help="Show only resumed jobs"),
    finished: bool = typer.Option(False, "--finished", help="Show only finished jobs"),
    resumable: bool = typer.Option(
        False, "--resumable", help="Show only resumable (interrupted) jobs"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
):
    """List all jobs in workspace."""
    try:
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        if not jobs_dir.exists():
            show_status("No jobs directory found", "warning")
            return

        jobs = []
        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue

            job_file = job_dir / "job.json"
            if not job_file.exists():
                continue

            try:
                job_data = json.loads(job_file.read_text())

                # Get plan info for time estimates
                plan_file = job_dir / "plan.json"
                time_estimate = None
                layer_count = None
                if plan_file.exists():
                    plan_data = json.loads(plan_file.read_text())
                    time_estimate = plan_data.get("estimates", {}).get("post_s")
                    layer_count = len(plan_data.get("layers", []))

                jobs.append(
                    {
                        "id": job_data.get("id", job_dir.name),
                        "name": job_data.get("name", "Unknown"),
                        "state": job_data.get("state", "UNKNOWN"),
                        "paper": job_data.get("paper", "Unknown"),
                        "time_estimate": time_estimate,
                        "layer_count": layer_count,
                        "created_at": job_data.get("created_at"),
                        "modified_at": job_data.get("modified_at"),
                        "dir_mtime": job_dir.stat().st_mtime,  # Directory modification time as fallback
                    }
                )
            except Exception:
                continue

        if not jobs:
            if json_output:
                print("[]")
            else:
                show_status("No jobs found", "info")
            return

        # Apply filters
        if state:
            # Filter by specific state
            state_upper = state.upper()
            jobs = [j for j in jobs if j["state"] == state_upper]
        elif failed:
            # Show failed jobs AND resumable jobs
            try:
                workspace = Path(cfg.workspace)
                recovery = get_crash_recovery(workspace)
                resumable_jobs = set(recovery.get_resumable_jobs())
                jobs = [
                    j
                    for j in jobs
                    if j["state"] == "FAILED" or j["id"] in resumable_jobs
                ]
            except Exception:
                # Fallback: show failed jobs plus potentially resumable states
                jobs = [
                    j
                    for j in jobs
                    if j["state"] in ["FAILED", "PLOTTING", "ARMED", "QUEUED"]
                ]
        elif resumed:
            jobs = [
                j for j in jobs if j["state"] in ["PLOTTING", "ARMED", "READY"]
            ]  # Jobs that were resumed
        elif finished:
            jobs = [j for j in jobs if j["state"] in ["COMPLETED", "ABORTED"]]
        elif resumable:
            # Show only resumable jobs
            try:
                workspace = Path(cfg.workspace)
                recovery = get_crash_recovery(workspace)
                resumable_jobs = set(recovery.get_resumable_jobs())
                jobs = [j for j in jobs if j["id"] in resumable_jobs]
            except Exception:
                # Fallback: show potentially resumable states
                jobs = [
                    j
                    for j in jobs
                    if j["state"] in ["PLOTTING", "ARMED", "QUEUED", "FAILED"]
                ]

        # Sort by state priority first, then by reverse chronological order
        state_priority = {
            "PLOTTING": 0,
            "ARMED": 1,
            "READY": 2,
            "OPTIMIZED": 3,
            "ANALYZED": 4,
            "QUEUED": 5,
            "NEW": 6,
            "PAUSED": 7,
            "COMPLETED": 8,
            "ABORTED": 9,
            "FAILED": 10,
        }

        def sort_key(job):
            # Primary sort: state priority
            priority = state_priority.get(job["state"], 99)

            # Secondary sort: reverse chronological (newest first)
            # Try multiple timestamp sources in order of preference
            timestamp = None
            if job.get("modified_at"):
                timestamp = job["modified_at"]
                # Convert string timestamps to float if needed
                if isinstance(timestamp, str):
                    try:
                        # Try ISO format first
                        from datetime import datetime

                        timestamp = datetime.fromisoformat(
                            timestamp.replace("Z", "+00:00")
                        ).timestamp()
                    except (ValueError, AttributeError):
                        try:
                            timestamp = float(timestamp)
                        except ValueError:
                            timestamp = 0
            elif job.get("created_at"):
                timestamp = job["created_at"]
                # Convert string timestamps to float if needed
                if isinstance(timestamp, str):
                    try:
                        # Try ISO format first
                        from datetime import datetime

                        timestamp = datetime.fromisoformat(
                            timestamp.replace("Z", "+00:00")
                        ).timestamp()
                    except (ValueError, AttributeError):
                        try:
                            timestamp = float(timestamp)
                        except ValueError:
                            timestamp = 0
            else:
                timestamp = job["dir_mtime"]

            # For reverse chronological, we negate the timestamp
            # (newer timestamps should come first)
            return (priority, -timestamp if timestamp else 0)

        jobs.sort(key=sort_key)

        if json_output:
            # JSON output for LLM parsing
            print(json.dumps(jobs, indent=2, default=str))
            return

        # Rich table output (default)
        output = get_output_manager()

        # Prepare rows with formatted time
        formatted_rows = []
        for job in jobs:
            time_str = "Unknown"
            if job["time_estimate"]:
                if job["time_estimate"] < 60:
                    time_str = f"{job['time_estimate']:.1f}s"
                else:
                    time_str = f"{job['time_estimate'] / 60:.1f}m"

            formatted_rows.append(
                [
                    job["id"],
                    job["name"][:20],
                    job["state"],
                    job["paper"],
                    str(job["layer_count"]) if job["layer_count"] else "Unknown",
                    time_str,
                ]
            )

        headers = ["ID", "Name", "State", "Paper", "Layers", "Est. Time"]

        # Build title based on filters
        title_parts = []
        if state:
            title_parts.append(f"{state.upper()} Jobs")
        elif failed:
            title_parts.append("Failed & Resumable")
        elif resumed:
            title_parts.append("Resumed")
        elif finished:
            title_parts.append("Finished")
        elif resumable:
            title_parts.append("Resumable")
        else:
            title_parts.append("All")

        if state:
            title = f"{state.upper()} Jobs ({len(jobs)} total)"
        else:
            title = f"{title_parts[0]} Jobs ({len(jobs)} total)"

        # Build markdown content
        markdown_content = output.print_table_markdown(
            title=title, headers=headers, rows=formatted_rows
        )

        # Output using the manager
        output.print_markdown(
            content=markdown_content,
            json_data={"jobs": jobs},
            json_output=json_output,
            csv_output=csv_output,
        )

    except Exception as e:
        error_handler.handle(e)


__all__ = ["jobs"]
