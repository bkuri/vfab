"""
Batch queue management commands.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta
import re

import typer

from ...utils import error_handler
from ...progress import show_status
from .utils import get_jobs_by_state

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Table = None
    Confirm = None


def clear_queue(
    state: str = typer.Option(
        None, "--state", help="Filter by job state (QUEUED, OPTIMIZED, READY, etc.)"
    ),
    older_than: str = typer.Option(
        None,
        "--older-than",
        help="Clear jobs older than duration (e.g., 7d, 24h, 30m, 1h)",
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Apply changes (default: preview mode only)"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", help="Minimal output (show only essential information)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Detailed output (show individual job details)"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output in JSON format (useful for scripting/automation)"
    ),
    confirm: bool = typer.Option(
        None,
        "--confirm/--no-confirm",
        help="Ask for confirmation before clearing (default: ask)",
    ),
):
    """Clear jobs from queue with filtering options.

    Examples:
        plotty batch clear-queue --state QUEUED --apply
        plotty batch clear-queue --older-than 7d --apply
        plotty batch clear-queue --state FAILED --older-than 24h --json

    Duration formats: 7d (7 days), 24h (24 hours), 30m (30 minutes)
    Without --apply, shows preview of jobs that would be cleared.
    """
    try:
        # Get jobs for verbose output and confirmation
        jobs = get_jobs_by_state(state or "QUEUED")

        # Parse older_than duration
        cutoff_time = None
        if older_than:
            # Parse duration like "7d", "24h", "30m"
            pattern = r"(\d+)([dhm])"  # digits + unit
            match = re.fullmatch(pattern, older_than.lower())
            if match:
                amount = int(match.group(1))
                unit = match.group(2)

                # Validate amount is reasonable
                if amount <= 0:
                    raise typer.BadParameter(
                        f"Duration must be positive: {amount}{unit}"
                    )
                if unit == "d" and amount > 365:
                    raise typer.BadParameter(
                        f"Duration too large: {amount} days (max: 365)"
                    )
                if unit == "h" and amount > 8760:  # 365 days
                    raise typer.BadParameter(
                        f"Duration too large: {amount} hours (max: 8760)"
                    )
                if unit == "m" and amount > 525600:  # 365 days
                    raise typer.BadParameter(
                        f"Duration too large: {amount} minutes (max: 525600)"
                    )

                if unit == "d":
                    cutoff_time = datetime.now() - timedelta(days=amount)
                elif unit == "h":
                    cutoff_time = datetime.now() - timedelta(hours=amount)
                elif unit == "m":
                    cutoff_time = datetime.now() - timedelta(minutes=amount)
                else:
                    raise typer.BadParameter(
                        f"Invalid duration unit: {unit} (use: d, h, m)"
                    )
            else:
                raise typer.BadParameter(
                    f"Invalid duration format: '{older_than}'. Use format like '7d', '24h', '30m'"
                )

        # Filter jobs based on criteria
        jobs_to_clear = []

        for job_info in jobs:
            should_clear = False
            reason = ""
            job_data = job_info["data"]
            job_path = job_info["path"]

            # Check state filter
            if state:
                if job_data.get("state") == state:
                    should_clear = True
                    reason = f"state='{state}'"

            # Check age filter
            if cutoff_time:
                created_at = job_data.get("created_at")
                if created_at:
                    try:
                        # Parse ISO datetime
                        job_time = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )
                        if job_time < cutoff_time:
                            if should_clear:
                                reason += f" and age>'{older_than}'"
                            else:
                                should_clear = True
                                reason = f"age>'{older_than}'"
                    except ValueError:
                        pass  # Skip if date parsing fails

            if should_clear:
                jobs_to_clear.append(
                    {"id": job_info["id"], "reason": reason, "path": job_path}
                )

        if not jobs_to_clear:
            if not quiet:
                show_status("No jobs match clearing criteria", "info")
            return

        # Show preview or apply clearing
        if not quiet:
            if console and Table:
                table = Table(title=f"Jobs to Clear ({len(jobs_to_clear)} total)")
                table.add_column("Job ID", style="cyan")
                table.add_column("Name", style="white")
                table.add_column("State", style="white")
                table.add_column("Reason", style="yellow")

                for job_info in jobs_to_clear:
                    job_path = job_info["path"]
                    job_file = job_path / "job.json"

                    if job_file.exists():
                        job_data = json.loads(job_file.read_text())
                        table.add_row(
                            job_info["id"],
                            job_data.get("name", "Unknown"),
                            job_data.get("state", "UNKNOWN"),
                            job_info["reason"],
                        )
                    else:
                        table.add_row(
                            job_info["id"], "Unknown", "NO_FILE", job_info["reason"]
                        )

                console.print(table)
            else:
                print(f"Jobs to Clear ({len(jobs_to_clear)} total):")
                for job_info in jobs_to_clear:
                    print(f"  {job_info['id']}: {job_info['reason']}")

        if apply:
            # Ask for confirmation unless --no-confirm is specified
            if confirm is not False and console and Confirm:
                if not Confirm.ask(f"\nClear {len(jobs_to_clear)} jobs from queue?"):
                    show_status("Queue clearing cancelled by user", "info")
                    return

            # Execute clearing
            cleared_jobs = []
            failed_jobs = []

            for job_info in jobs_to_clear:
                try:
                    job_path = job_info["path"]

                    # Remove job directory and all contents
                    shutil.rmtree(job_path)

                    cleared_jobs.append(job_info["id"])

                    if verbose:
                        show_status(f"Cleared job {job_info['id']}", "success")

                except Exception as clear_error:
                    failed_jobs.append(
                        {"id": job_info["id"], "error": str(clear_error)}
                    )

                    if verbose:
                        show_status(
                            f"Failed to clear {job_info['id']}: {clear_error}", "error"
                        )

            # Report results
            if not quiet:
                if cleared_jobs:
                    show_status(
                        f"Successfully cleared {len(cleared_jobs)} jobs", "success"
                    )

                if failed_jobs:
                    show_status(f"Failed to clear {len(failed_jobs)} jobs", "error")
                    if verbose:
                        for failure in failed_jobs:
                            print(f"  ✗ {failure['id']}: {failure['error']}")

            if json_output:
                result_data = {
                    "cleared": cleared_jobs,
                    "failed": failed_jobs,
                    "total_processed": len(cleared_jobs) + len(failed_jobs),
                    "criteria": {
                        "state": state,
                        "older_than": older_than,
                        "cutoff_time": cutoff_time.isoformat() if cutoff_time else None,
                    },
                }
                print(json.dumps(result_data, indent=2, default=str))
        else:
            show_status("Preview mode - use --apply to execute", "info")

        if verbose:
            # Additional verbose information
            print(f"Found {len(jobs)} jobs matching criteria")
            for job_info in jobs[:5]:  # Show first 5 jobs
                print(f"  - {job_info['id']}: {job_info['name']}")
            if len(jobs) > 5:
                print(f"  ... and {len(jobs) - 5} more jobs")

    except Exception as e:
        error_handler.handle(e)
