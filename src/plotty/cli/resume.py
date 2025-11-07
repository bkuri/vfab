"""
Resume command for ploTTY CLI.

Provides functionality to resume interrupted plotting jobs from their last state.
"""

from __future__ import annotations

import typer
from pathlib import Path

from ..config import load_config
from ..recovery import get_crash_recovery, requeue_job_to_front
from ..progress import show_status
from ..codes import ExitCode
from ..utils import error_handler

try:
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Confirm = None


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        recovery = get_crash_recovery(workspace)
        resumable_jobs = recovery.get_resumable_jobs()
        return [job_id for job_id in resumable_jobs if job_id.startswith(incomplete)]
    except Exception:
        return []


def resume_command(
    job_id: str = typer.Argument(
        None,
        help="Job ID to resume (omit for all jobs)",
        autocompletion=complete_job_id,
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Apply resume changes (dry-run by default)"
    ),
    now: bool = typer.Option(
        False, "--now", help="Prioritize resumed job to front of queue"
    ),
) -> None:
    """Resume interrupted plotting jobs."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        recovery = get_crash_recovery(workspace)

        if job_id:
            # Resume specific job
            status = recovery.get_job_status(job_id)
            if "error" in status:
                if console:
                    console.print(f"❌ Error: {status['error']}", style="red")
                else:
                    print(f"Error: {status['error']}")
                raise typer.Exit(ExitCode.NOT_FOUND)

            if not status.get("resumable"):
                if console:
                    console.print(
                        f"❌ Job '{job_id}' is not resumable (state: {status.get('current_state')})",
                        style="red",
                    )
                else:
                    print(
                        f"Job '{job_id}' is not resumable (state: {status.get('current_state')})"
                    )
                raise typer.Exit(ExitCode.INVALID_INPUT)

            # Show what will be done
            if console:
                console.print(
                    f"🔄 Will resume job '{job_id}' from state '{status.get('current_state')}'"
                )
            else:
                print(
                    f"Will resume job '{job_id}' from state '{status.get('current_state')}'"
                )

            if not apply:
                if console:
                    console.print(
                        "💡 Use --apply to actually resume job", style="yellow"
                    )
                else:
                    print("Use --apply to actually resume job")
                return

            # Confirm and perform resume
            if console and Confirm:
                if not Confirm.ask(f"Resume job '{job_id}'?"):
                    show_status("Resume cancelled", "info")
                    return
            else:
                response = input(f"Resume job '{job_id}'? [y/N]: ").strip().lower()
                if response not in ["y", "yes"]:
                    print("Resume cancelled")
                    return

            show_status(f"Resuming job '{job_id}'...", "info")
            fsm = recovery.recover_job(job_id)

            if fsm:
                recovery.register_fsm(fsm)

                # Handle queue positioning if requested
                if now:
                    try:
                        requeue_job_to_front(job_id, workspace)
                        if console:
                            console.print(
                                f"🚀 Job '{job_id}' moved to front of queue",
                                style="blue",
                            )
                        else:
                            print(f"Job '{job_id}' moved to front of queue")
                    except Exception as e:
                        if console:
                            console.print(
                                f"⚠️  Failed to move job to front of queue: {e}",
                                style="yellow",
                            )
                        else:
                            print(f"Warning: Failed to move job to front of queue: {e}")

                if console:
                    console.print(
                        f"✅ Successfully resumed job '{job_id}'", style="green"
                    )
                    console.print(f"Current state: {fsm.current_state.value}")
                else:
                    print(f"Successfully resumed job '{job_id}'")
                    print(f"Current state: {fsm.current_state.value}")
            else:
                if console:
                    console.print(f"❌ Failed to resume job '{job_id}'", style="red")
                else:
                    print(f"Failed to resume job '{job_id}'")
                raise typer.Exit(ExitCode.ERROR)

        else:
            # Resume all resumable jobs
            resumable_jobs = recovery.get_resumable_jobs()

            if not resumable_jobs:
                if console:
                    console.print("✅ No jobs need resuming", style="green")
                else:
                    print("No jobs need resuming")
                return

            # Show what will be done
            if console:
                console.print(f"🔄 Will resume {len(resumable_jobs)} jobs:")
                for job_id in resumable_jobs:
                    console.print(f"  • {job_id}")
            else:
                print(f"Will resume {len(resumable_jobs)} jobs:")
                for job_id in resumable_jobs:
                    print(f"  • {job_id}")

            if not apply:
                if console:
                    console.print(
                        "💡 Use --apply to actually resume jobs", style="yellow"
                    )
                else:
                    print("Use --apply to actually resume jobs")
                return

            # Confirm and perform resume
            if console and Confirm:
                if not Confirm.ask(f"Resume all {len(resumable_jobs)} jobs?"):
                    show_status("Resume cancelled", "info")
                    return
            else:
                response = (
                    input(f"Resume all {len(resumable_jobs)} jobs? [y/N]: ")
                    .strip()
                    .lower()
                )
                if response not in ["y", "yes"]:
                    print("Resume cancelled")
                    return

            show_status(f"Resuming {len(resumable_jobs)} jobs...", "info")
            resumed_fsms = []

            for job_id in resumable_jobs:
                fsm = recovery.recover_job(job_id)
                if fsm:
                    recovery.register_fsm(fsm)
                    resumed_fsms.append(fsm)

            if console:
                console.print(
                    f"✅ Successfully resumed {len(resumed_fsms)} jobs", style="green"
                )
                if resumed_fsms:
                    console.print("Resumed jobs:")
                    for fsm in resumed_fsms:
                        console.print(
                            f"  • {fsm.job_id} (state: {fsm.current_state.value})"
                        )
            else:
                print(f"Successfully resumed {len(resumed_fsms)} jobs")
                if resumed_fsms:
                    print("Resumed jobs:")
                    for fsm in resumed_fsms:
                        print(f"  • {fsm.job_id} (state: {fsm.current_state.value})")

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
