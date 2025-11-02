"""
Recovery listing and status commands.
"""

from __future__ import annotations

import typer
from pathlib import Path

from ...config import load_config
from ...crash_recovery import get_crash_recovery
from ...exit_codes import ExitCode
from ...utils import error_handler

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Table = None


def list_recoverable() -> None:
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

        if console:
            console.print("🔄 Recoverable Jobs", style="bold blue")
            console.print("=" * 40)

            table = Table()
            table.add_column("Job ID", style="cyan")
            table.add_column("Current State", style="white")
            table.add_column("Emergency Shutdown", style="yellow")
            table.add_column("Recoverable", style="green")

            for job_id in recoverable_jobs:
                status = recovery.get_job_status(job_id)
                if "error" not in status:
                    table.add_row(
                        job_id,
                        status.get("current_state", "Unknown"),
                        "Yes" if status.get("emergency_shutdown") else "No",
                        "Yes" if status.get("recoverable") else "No",
                    )

            console.print(table)
        else:
            print("Recoverable Jobs:")
            print("=" * 40)
            print(f"{'Job ID':<20} {'State':<15} {'Emergency':<10} {'Recoverable':<12}")
            print("-" * 40)

            for job_id in recoverable_jobs:
                status = recovery.get_job_status(job_id)
                if "error" not in status:
                    print(
                        f"{job_id:<20} {status.get('current_state', 'Unknown'):<15} {'Yes' if status.get('emergency_shutdown') else 'No':<10} {'Yes' if status.get('recoverable') else 'No':<12}"
                    )

        if console:
            console.print(f"\nFound {len(recoverable_jobs)} recoverable job(s)")
        else:
            print(f"\nFound {len(recoverable_jobs)} recoverable job(s)")

    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def job_status(job_id: str) -> None:
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

        if console:
            console.print(f"📊 Recovery Status for Job '{job_id}'", style="bold blue")
            console.print("=" * 50)

            console.print(
                f"Current State: {status_info.get('current_state', 'Unknown')}"
            )
            console.print(
                f"Emergency Shutdown: {'Yes' if status_info.get('emergency_shutdown') else 'No'}"
            )
            console.print(
                f"Recoverable: {'Yes' if status_info.get('recoverable') else 'No'}"
            )
            console.print(f"Journal Entries: {status_info.get('journal_entries', 0)}")

            if status_info.get("last_transition"):
                transition = status_info["last_transition"]
                console.print("\nLast Transition:")
                console.print(f"  From: {transition.get('from_state', 'Unknown')}")
                console.print(f"  To: {transition.get('to_state', 'Unknown')}")
                console.print(f"  Reason: {transition.get('reason', 'Unknown')}")
                console.print(f"  Time: {transition.get('timestamp', 'Unknown')}")
        else:
            print(f"Recovery Status for Job '{job_id}'")
            print("=" * 50)
            print(f"Current State: {status_info.get('current_state', 'Unknown')}")
            print(
                f"Emergency Shutdown: {'Yes' if status_info.get('emergency_shutdown') else 'No'}"
            )
            print(f"Recoverable: {'Yes' if status_info.get('recoverable') else 'No'}")
            print(f"Journal Entries: {status_info.get('journal_entries', 0)}")

            if status_info.get("last_transition"):
                transition = status_info["last_transition"]
                print("\nLast Transition:")
                print(f"  From: {transition.get('from_state', 'Unknown')}")
                print(f"  To: {transition.get('to_state', 'Unknown')}")
                print(f"  Reason: {transition.get('reason', 'Unknown')}")
                print(f"  Time: {transition.get('timestamp', 'Unknown')}")

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
