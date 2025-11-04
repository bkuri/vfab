"""
List jobs command for ploTTY CLI.
"""

from __future__ import annotations

from pathlib import Path
import typer
import json

from ...config import load_config
from ...utils import error_handler
from ...progress import show_status
from ..status.output import get_output_manager

list_app = typer.Typer(help="List jobs")


@list_app.command("jobs")
def jobs(
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

        # Sort by state priority
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
        jobs.sort(key=lambda j: state_priority.get(j["state"], 99))

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

        # Build markdown content
        markdown_content = output.print_table_markdown(
            title=f"Jobs ({len(jobs)} total)", headers=headers, rows=formatted_rows
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
