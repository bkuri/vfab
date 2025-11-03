"""
Queue status commands for ploTTY.

This module provides commands for viewing and managing the job queue,
including filtering, sorting, and queue statistics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ...config import load_config
from ...utils import error_handler
from .utils import (
    collect_jobs,
    sort_jobs_by_state,
    format_time,
)
from .output import get_output_manager


def show_job_queue(
    limit: int = 10,
    state: Optional[str] = None,
    json_output: bool = False,
    csv_output: bool = False,
):
    """Show jobs in queue."""
    try:
        output = get_output_manager()
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        if not jobs_dir.exists():
            markdown_content = "# ploTTY Job Queue\n\nNo jobs directory found"
            output.print_markdown(content=markdown_content)
            return

        # Collect jobs
        jobs = collect_jobs(jobs_dir, state_filter=state)

        if not jobs:
            markdown_content = "# ploTTY Job Queue\n\nNo jobs found"
            output.print_markdown(content=markdown_content)
            return

        # Sort by state (prioritize active jobs)
        jobs = sort_jobs_by_state(jobs)

        # Limit results
        jobs = jobs[:limit]

        # Prepare data for different formats
        json_data = {
            "queue": {
                "limit": limit,
                "state_filter": state,
                "total_found": len(jobs),
                "jobs": jobs,
            }
        }

        # Build tabular CSV data
        headers = ["ID", "Name", "State", "Config", "Paper", "Layers", "Est. Time"]
        rows = []

        for job in jobs:
            rows.append(
                {
                    "ID": job["id"],
                    "Name": job["name"][:30],
                    "State": job["state"],
                    "Config": job["config_status"],
                    "Paper": job["paper"],
                    "Layers": (
                        str(job["layer_count"]) if job["layer_count"] else "Unknown"
                    ),
                    "Est. Time": format_time(job["time_estimate"]),
                }
            )

        tabular_csv_data = {
            "headers": headers,
            "rows": rows,
        }

        # Build markdown content
        state_filter = ""
        if state:
            state_filter = f"\nShowing jobs with state: **{state}**"

        # Build job rows
        job_rows = []
        for job in jobs:
            job_rows.append(
                f"| {job['id']} | {job['name'][:30]} | {job['state']} | "
                f"{job['config_status']} | {job['paper']} | "
                f"{str(job['layer_count']) if job['layer_count'] else 'Unknown'} | "
                f"{format_time(job['time_estimate'])} |"
            )

        job_table = "\n".join(job_rows)

        markdown_content = f"""# ploTTY Job Queue{state_filter}

Showing **{len(jobs)}** jobs (limited to {limit})

| ID | Name | State | Config | Paper | Layers | Est. Time |
|----|------|-------|--------|-------|--------|-----------|
{job_table}"""

        # Output using the manager
        output.print_markdown(
            content=markdown_content,
            json_data=json_data,
            tabular_csv_data=tabular_csv_data,
            json_output=json_output,
            csv_output=csv_output,
        )

    except Exception as e:
        error_handler.handle(e)
