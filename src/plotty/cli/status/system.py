"""
System status commands for ploTTY.

This module provides commands for checking overall system status,
hardware availability, and configuration.
"""

from __future__ import annotations

from pathlib import Path

from ...config import load_config
from ...utils import error_handler
from .utils import (
    get_axidraw_status,
    get_camera_status,
    collect_jobs,
    get_queue_summary,
    format_time,
    sort_jobs_by_state,
)
from .output import get_output_manager


def show_system_status(
    json_output: bool = False,
    csv_output: bool = False,
):
    """Show overall system status."""
    try:
        output = get_output_manager()

        # Load configuration
        cfg = load_config(None)

        # Check AxiDraw availability
        axidraw_status = get_axidraw_status()
        camera_status = get_camera_status(cfg)

        # Count jobs
        jobs_dir = Path(cfg.workspace) / "jobs"
        jobs = collect_jobs(jobs_dir)
        queue_summary = get_queue_summary(jobs)

        # Prepare data for different formats
        json_data = {
            "system": {
                "axidraw_status": axidraw_status,
                "camera_status": camera_status,
                "workspace": cfg.workspace,
                "queue_summary": queue_summary,
            }
        }

        # Build hierarchical CSV data
        hierarchical_csv_data = [
            {
                "section": "System Status",
                "category": "AxiDraw",
                "item": "",
                "value": axidraw_status,
            },
            {
                "section": "System Status",
                "category": "Camera",
                "item": "",
                "value": camera_status,
            },
            {
                "section": "System Status",
                "category": "Workspace",
                "item": "",
                "value": cfg.workspace,
            },
            {
                "section": "System Status",
                "category": "Queue",
                "item": "",
                "value": f"{queue_summary['total']} jobs ({queue_summary['ready']} ready)",
            },
        ]

        markdown_content = """## System Components
| Component | Status |
|-----------|--------|
| AxiDraw | {axidraw_status} |
| Camera | {camera_status} |
| Workspace | {workspace} |
| Queue | {queue_total} jobs ({queue_ready} ready) |
""".format(
            axidraw_status=axidraw_status,
            camera_status=camera_status,
            workspace=cfg.workspace,
            queue_total=queue_summary["total"],
            queue_ready=queue_summary["ready"],
        )

        # Output using the manager
        output.print_markdown(
            content=markdown_content,
            json_data=json_data,
            hierarchical_csv_data=hierarchical_csv_data,
            json_output=json_output,
            csv_output=csv_output,
        )

    except Exception as e:
        error_handler.handle(e)


def show_quick_status(
    json_output: bool = False,
    csv_output: bool = False,
):
    """Show quick overview of system and queue (too long; didn't read)."""
    try:
        output = get_output_manager()

        # Load configuration
        cfg = load_config(None)

        # Check AxiDraw availability
        axidraw_status = get_axidraw_status()
        axi_available = "Available" in axidraw_status
        cam_enabled = cfg.camera.mode != "disabled"

        # Queue summary
        jobs_dir = Path(cfg.workspace) / "jobs"
        jobs = collect_jobs(jobs_dir)
        queue_summary = get_queue_summary(jobs)

        # Get next ready job info
        next_job_info = None
        if queue_summary["ready"] > 0:
            ready_jobs = [j for j in jobs if j.get("state") == "READY"]
            if ready_jobs:
                next_job = ready_jobs[0]
                next_job_info = {
                    "name": next_job.get("name", "Unknown"),
                    "id": next_job.get("id", "Unknown")[:8],
                    "time_estimate": next_job.get("time_estimate", 0),
                }

        # Prepare data for different formats
        json_data = {
            "system": {
                "axidraw_available": axi_available,
                "camera_enabled": cam_enabled,
                "workspace": cfg.workspace,
            },
            "queue": queue_summary,
            "next_job": next_job_info,
        }

        # Build hierarchical CSV data
        hierarchical_csv_data = [
            {
                "section": "System",
                "category": "AxiDraw",
                "item": "",
                "value": "✅" if axi_available else "❌",
            },
            {
                "section": "System",
                "category": "Camera",
                "item": "",
                "value": "✅" if cam_enabled else "❌",
            },
            {
                "section": "System",
                "category": "Workspace",
                "item": "",
                "value": Path(cfg.workspace).name,
            },
            {
                "section": "Queue",
                "category": "Total",
                "item": "",
                "value": str(queue_summary["total"]),
            },
            {
                "section": "Queue",
                "category": "Ready",
                "item": "",
                "value": str(queue_summary["ready"]),
            },
            {
                "section": "Queue",
                "category": "Completed",
                "item": "",
                "value": str(queue_summary["completed"]),
            },
            {
                "section": "Queue",
                "category": "Failed",
                "item": "",
                "value": str(queue_summary["failed"]),
            },
        ]

        if next_job_info:
            hierarchical_csv_data.extend(
                [
                    {
                        "section": "Next Job",
                        "category": "Name",
                        "item": "",
                        "value": next_job_info["name"],
                    },
                    {
                        "section": "Next Job",
                        "category": "ID",
                        "item": "",
                        "value": next_job_info["id"],
                    },
                    {
                        "section": "Next Job",
                        "category": "Est. Time",
                        "item": "",
                        "value": format_time(next_job_info["time_estimate"]),
                    },
                ]
            )

        # No tabular data for tldr command
        tabular_csv_data = None

        # Build markdown content
        next_job_section = ""
        if next_job_info:
            next_job_section = f"""

## Next Job
- Name: {next_job_info["name"]}
- ID: {next_job_info["id"]}
- Est. Time: {format_time(next_job_info["time_estimate"])}"""

        markdown_content = f"""## System
- AxiDraw: {"✅" if axi_available else "❌"}
- Camera: {"✅" if cam_enabled else "❌"}
- Workspace: {Path(cfg.workspace).name}

## Queue
- Total: {queue_summary["total"]} jobs
- Ready: {queue_summary["ready"]} jobs
- Completed: {queue_summary["completed"]} jobs
- Failed: {queue_summary["failed"]} jobs{next_job_section}"""

        # Output using the manager
        output.print_markdown(
            content=markdown_content,
            json_data=json_data,
            hierarchical_csv_data=hierarchical_csv_data,
            tabular_csv_data=tabular_csv_data,
            json_output=json_output,
            csv_output=csv_output,
        )

    except Exception as e:
        error_handler.handle(e)


def show_status_overview(
    json_output: bool = False,
    csv_output: bool = False,
):
    """Show complete status overview or run subcommands."""
    try:
        output = get_output_manager()

        # Load configuration
        cfg = load_config(None)

        # Check AxiDraw availability first (needed for both JSON and markdown)
        axidraw_status = get_axidraw_status()
        camera_status = get_camera_status(cfg)

        # Count jobs (needed for both JSON and markdown)
        jobs_dir = Path(cfg.workspace) / "jobs"
        jobs = collect_jobs(jobs_dir)
        queue_summary = get_queue_summary(jobs)

        # Sort and show jobs
        sorted_jobs = sort_jobs_by_state(jobs)

        # Prepare data for different formats
        json_data = {
            "system": {
                "axidraw_available": "Available" in axidraw_status,
                "camera_enabled": cfg.camera.mode != "disabled",
                "workspace": cfg.workspace,
            },
            "queue": {
                "total_jobs": queue_summary["total"],
                "ready_jobs": queue_summary["ready"],
                "completed_jobs": queue_summary["completed"],
                "failed_jobs": queue_summary["failed"],
            },
            "jobs": jobs,
        }

        # Build hierarchical CSV data for system status
        hierarchical_csv_data = [
            {
                "section": "System Status",
                "category": "AxiDraw",
                "item": "",
                "value": axidraw_status,
            },
            {
                "section": "System Status",
                "category": "Camera",
                "item": "",
                "value": camera_status,
            },
            {
                "section": "System Status",
                "category": "Workspace",
                "item": "",
                "value": cfg.workspace,
            },
            {
                "section": "System Status",
                "category": "Queue",
                "item": "",
                "value": f"{queue_summary['total']} jobs ({queue_summary['ready']} ready)",
            },
        ]

        # Build tabular CSV data for job queue
        job_queue_headers = [
            "ID",
            "Name",
            "State",
            "Config",
            "Paper",
            "Layers",
            "Est. Time",
        ]
        job_queue_rows = []

        for job in sorted_jobs[:20]:  # Limit to 20 for CSV
            time_str = (
                f"{job['time_estimate']:.1f}s" if job["time_estimate"] else "Unknown"
            )
            if job["time_estimate"] and job["time_estimate"] > 60:
                time_str = f"{job['time_estimate'] / 60:.1f}m"

            job_queue_rows.append(
                {
                    "ID": job["id"],
                    "Name": job["name"][:20],
                    "State": job["state"],
                    "Config": job["config_status"],
                    "Paper": job["paper"],
                    "Layers": job["layer_count"] or "Unknown",
                    "Est. Time": time_str,
                }
            )

        tabular_csv_data = {
            "headers": job_queue_headers,
            "rows": job_queue_rows,
        }

        # Build job queue table for markdown
        job_rows = []
        for job in sorted_jobs[:20]:  # Limit to 20 for markdown
            time_str = (
                f"{job['time_estimate']:.1f}s" if job["time_estimate"] else "Unknown"
            )
            if job["time_estimate"] and job["time_estimate"] > 60:
                time_str = f"{job['time_estimate'] / 60:.1f}m"

            job_rows.append(
                f"| {job['id']} | {job['name'][:20]} | {job['state']} | {job['config_status']} | {job['paper']} | {job['layer_count'] or 'Unknown'} | {time_str} |"
            )

        if len(sorted_jobs) > 20:
            job_rows.append("| ... | ... | ... | ... | ... | ... | ... |")
            job_rows.append(f"| | | | | | **{len(sorted_jobs) - 20} more jobs** | |")

        job_table = "\n".join(job_rows)

        # State summary
        from .utils import count_jobs_by_state

        state_counts = count_jobs_by_state(jobs)
        state_summary = ""
        if state_counts:
            state_lines = [
                f"- {state}: {count}" for state, count in sorted(state_counts.items())
            ]
            state_summary = "\n## Jobs by State\n" + "\n".join(state_lines)

        markdown_content = f"""# ploTTY Status Report

## System Status
| Component | Status |
|-----------|--------|
| AxiDraw | {axidraw_status} |
| Camera | {camera_status} |
| Workspace | {cfg.workspace} |
| Queue | {queue_summary["total"]} jobs ({queue_summary["ready"]} ready) |

## Job Queue
| ID | Name | State | Config | Paper | Layers | Est. Time |
|----|------|-------|--------|-------|--------|-----------|
{job_table}{state_summary}"""

        # Output using the manager
        output.print_markdown(
            content=markdown_content,
            json_data=json_data,
            hierarchical_csv_data=hierarchical_csv_data,
            tabular_csv_data=tabular_csv_data,
            json_output=json_output,
            csv_output=csv_output,
        )

    except Exception as e:
        error_handler.handle(e)
