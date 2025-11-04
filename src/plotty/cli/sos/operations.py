"""
Recovery operations commands.
"""

from __future__ import annotations

import typer
from pathlib import Path

from ...config import load_config
from ...recovery import get_crash_recovery, recover_all_jobs
from ...progress import show_status
from ...codes import ExitCode
from ...utils import error_handler

try:
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Confirm = None


def recover_job(job_id: str) -> None:
    """Recover a specific job."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        recovery = get_crash_recovery(workspace)

        # Check if job is recoverable
        status = recovery.get_job_status(job_id)
        if "error" in status:
            if console:
                console.print(f"❌ Error: {status['error']}", style="red")
            else:
                print(f"Error: {status['error']}")
            raise typer.Exit(ExitCode.NOT_FOUND)

        if not status.get("recoverable"):
            if console:
                console.print(
                    f"❌ Job '{job_id}' is not recoverable (state: {status.get('current_state')})",
                    style="red",
                )
            else:
                print(
                    f"Job '{job_id}' is not recoverable (state: {status.get('current_state')})"
                )
            raise typer.Exit(ExitCode.INVALID_INPUT)

        # Confirm recovery
        if console and Confirm:
            if not Confirm.ask(
                f"Recover job '{job_id}' from state '{status.get('current_state')}'?"
            ):
                show_status("Recovery cancelled", "info")
                return
        else:
            response = (
                input(
                    f"Recover job '{job_id}' from state '{status.get('current_state')}'? [y/N]: "
                )
                .strip()
                .lower()
            )
            if response not in ["y", "yes"]:
                print("Recovery cancelled")
                return

        # Perform recovery
        show_status(f"Recovering job '{job_id}'...", "info")
        fsm = recovery.recover_job(job_id)

        if fsm:
            recovery.register_fsm(fsm)
            if console:
                console.print(
                    f"✅ Successfully recovered job '{job_id}'", style="green"
                )
                console.print(f"Current state: {fsm.current_state.value}")
            else:
                print(f"Successfully recovered job '{job_id}'")
                print(f"Current state: {fsm.current_state.value}")
        else:
            if console:
                console.print(f"❌ Failed to recover job '{job_id}'", style="red")
            else:
                print(f"Failed to recover job '{job_id}'")
            raise typer.Exit(ExitCode.ERROR)

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def recover_all_jobs_cmd() -> None:
    """Recover all recoverable jobs."""
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

        # Confirm recovery
        if console and Confirm:
            if not Confirm.ask(
                f"Recover all {len(recoverable_jobs)} recoverable jobs?"
            ):
                show_status("Recovery cancelled", "info")
                return
        else:
            response = (
                input(f"Recover all {len(recoverable_jobs)} recoverable jobs? [y/N]: ")
                .strip()
                .lower()
            )
            if response not in ["y", "yes"]:
                print("Recovery cancelled")
                return

        # Perform recovery
        show_status(f"Recovering {len(recoverable_jobs)} jobs...", "info")
        recovered_fsms = recover_all_jobs(workspace)

        if console:
            console.print(
                f"✅ Successfully recovered {len(recovered_fsms)} jobs", style="green"
            )
            if recovered_fsms:
                console.print("Recovered jobs:")
                for fsm in recovered_fsms:
                    console.print(
                        f"  • {fsm.job_id} (state: {fsm.current_state.value})"
                    )
        else:
            print(f"Successfully recovered {len(recovered_fsms)} jobs")
            if recovered_fsms:
                print("Recovered jobs:")
                for fsm in recovered_fsms:
                    print(f"  • {fsm.job_id} (state: {fsm.current_state.value})")

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def cleanup_journal(job_id: str, keep_entries: int = 100) -> None:
    """Clean up old recovery entries."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        recovery = get_crash_recovery(workspace)

        # Check if job exists
        status_info = recovery.get_job_status(job_id)
        if "error" in status_info:
            if console:
                console.print(f"❌ Error: {status_info['error']}", style="red")
            else:
                print(f"Error: {status_info['error']}")
            raise typer.Exit(ExitCode.NOT_FOUND)

        # Confirm cleanup
        if console and Confirm:
            if not Confirm.ask(
                f"Clean up journal for job '{job_id}', keeping {keep_entries} most recent entries?"
            ):
                show_status("Cleanup cancelled", "info")
                return
        else:
            response = (
                input(
                    f"Clean up journal for job '{job_id}', keeping {keep_entries} most recent entries? [y/N]: "
                )
                .strip()
                .lower()
            )
            if response not in ["y", "yes"]:
                print("Cleanup cancelled")
                return

        # Perform cleanup
        show_status(f"Cleaning up journal for job '{job_id}'...", "info")
        success = recovery.cleanup_journal(job_id, keep_entries)

        if success:
            if console:
                console.print(
                    f"✅ Successfully cleaned up journal for job '{job_id}'",
                    style="green",
                )
            else:
                print(f"Successfully cleaned up journal for job '{job_id}'")
        else:
            if console:
                console.print(
                    f"❌ Failed to clean up journal for job '{job_id}'", style="red"
                )
            else:
                print(f"Failed to clean up journal for job '{job_id}'")
            raise typer.Exit(ExitCode.ERROR)

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
