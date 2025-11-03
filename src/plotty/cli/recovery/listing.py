"""
Recovery listing and status commands.
"""

from __future__ import annotations

import typer
from pathlib import Path

from ...config import load_config
from ...recovery import get_crash_recovery
from ...codes import ExitCode
from ...utils import error_handler

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Table = None


def list_recoverable(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
) -> None:
    """List available recovery entries."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        recovery = get_crash_recovery(workspace)

        recoverable_jobs = recovery.get_recoverable_jobs()

        if not recoverable_jobs:
            if console:
                console.print("✅ No jobs need recovery", style="green")
            else:
                print("No jobs need recovery")
            return

        # Prepare data
        headers = ["Job ID", "Current State", "Emergency Shutdown", "Recoverable"]
        rows = []

        for job_id in recoverable_jobs:
            status = recovery.get_job_status(job_id)
            if "error" not in status:
                rows.append(
                    [
                        job_id,
                        status.get("current_state", "Unknown"),
                        "Yes" if status.get("emergency_shutdown") else "No",
                        "Yes" if status.get("recoverable") else "No",
                    ]
                )

        # Output in requested format
        if json_output:
            import json

            jobs_data = []
            for job_id in recoverable_jobs:
                status = recovery.get_job_status(job_id)
                if "error" not in status:
                    jobs_data.append(
                        {
                            "job_id": job_id,
                            "current_state": status.get("current_state", "Unknown"),
                            "emergency_shutdown": status.get(
                                "emergency_shutdown", False
                            ),
                            "recoverable": status.get("recoverable", False),
                        }
                    )
            output_data = {
                "recoverable_jobs": jobs_data,
                "total_count": len(recoverable_jobs),
            }
            typer.echo(json.dumps(output_data, indent=2, default=str))
        elif csv_output:
            import csv
            import sys

            writer = csv.writer(sys.stdout)
            writer.writerow(headers)
            writer.writerows(rows)
            writer.writerow([])
            writer.writerow(["Total", str(len(recoverable_jobs))])
        else:
            # Markdown output (default)
            typer.echo("# 🔄 Recoverable Jobs")
            typer.echo()
            typer.echo("| " + " | ".join(headers) + " |")
            typer.echo("| " + " | ".join(["---"] * len(headers)) + " |")

            for row in rows:
                typer.echo("| " + " | ".join(row) + " |")

            typer.echo()
            typer.echo(f"Found {len(recoverable_jobs)} recoverable job(s)")

    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def job_status(
    job_id: str,
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
) -> None:
    """Check recovery status for a job."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        recovery = get_crash_recovery(workspace)

        status_info = recovery.get_job_status(job_id)

        if "error" in status_info:
            if console:
                console.print(f"❌ Error: {status_info['error']}", style="red")
            else:
                print(f"Error: {status_info['error']}")
            raise typer.Exit(ExitCode.NOT_FOUND)

        # Output in requested format
        if json_output:
            import json

            typer.echo(json.dumps(status_info, indent=2, default=str))
        elif csv_output:
            import csv
            import sys

            writer = csv.writer(sys.stdout)

            # Status information
            writer.writerow(["Status Information"])
            writer.writerow(["Property", "Value"])
            writer.writerow(
                ["Current State", status_info.get("current_state", "Unknown")]
            )
            writer.writerow(
                [
                    "Emergency Shutdown",
                    "Yes" if status_info.get("emergency_shutdown") else "No",
                ]
            )
            writer.writerow(
                ["Recoverable", "Yes" if status_info.get("recoverable") else "No"]
            )
            writer.writerow(
                ["Journal Entries", str(status_info.get("journal_entries", 0))]
            )
            writer.writerow([])

            # Last transition
            if status_info.get("last_transition"):
                writer.writerow(["Last Transition"])
                writer.writerow(["Property", "Value"])
                transition = status_info["last_transition"]
                writer.writerow(["From", transition.get("from_state", "Unknown")])
                writer.writerow(["To", transition.get("to_state", "Unknown")])
                writer.writerow(["Time", transition.get("timestamp", "Unknown")])
        else:
            # Markdown output (default)
            typer.echo(f"# 📊 Recovery Status for Job '{job_id}'")
            typer.echo()
            typer.echo("## Status Information")
            typer.echo("| Property | Value |")
            typer.echo("|----------|-------|")
            typer.echo(
                f"| Current State | {status_info.get('current_state', 'Unknown')} |"
            )
            typer.echo(
                f"| Emergency Shutdown | {'Yes' if status_info.get('emergency_shutdown') else 'No'} |"
            )
            typer.echo(
                f"| Recoverable | {'Yes' if status_info.get('recoverable') else 'No'} |"
            )
            typer.echo(f"| Journal Entries | {status_info.get('journal_entries', 0)} |")

            if status_info.get("last_transition"):
                transition = status_info["last_transition"]
                typer.echo()
                typer.echo("## Last Transition")
                typer.echo("| Property | Value |")
                typer.echo("|----------|-------|")
                typer.echo(f"| From | {transition.get('from_state', 'Unknown')} |")
                typer.echo(f"| To | {transition.get('to_state', 'Unknown')} |")
                typer.echo(f"| Time | {transition.get('timestamp', 'Unknown')} |")

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
