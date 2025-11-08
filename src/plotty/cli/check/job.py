"""
Job checking command for ploTTY CLI.
"""

from __future__ import annotations

import typer
from pathlib import Path

from ...config import load_config
from ...guards import create_guard_system
from ...codes import ExitCode
from ...recovery import get_crash_recovery
from ..core import get_available_job_ids

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Table = None


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


def check_job(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to check"
    ),
    guard_name: str = typer.Option(
        None, "--guard", "-g", help="Specific guard to check (default: all)"
    ),
) -> None:
    """Check guards for a job."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        guard_system = create_guard_system(cfg, workspace)

        if guard_name:
            # Check specific guard
            result = guard_system.check_guard(guard_name, job_id)
            if result.result.value == "pass":
                if console:
                    console.print(
                        f"✅ Guard '{guard_name}' passed for job {job_id}",
                        style="green",
                    )
                else:
                    print(f"✅ Guard '{guard_name}' passed for job {job_id}")
            elif result.result.value == "skipped":
                if console:
                    console.print(
                        f"  Guard '{guard_name}' skipped for job {job_id}: {result.message}",
                        style="cyan",
                    )
                else:
                    print(
                        f"  Guard '{guard_name}' skipped for job {job_id}: {result.message}"
                    )
            else:
                if console:
                    console.print(
                        f"❌ Guard '{guard_name}' failed for job {job_id}: {result.message}",
                        style="red",
                    )
                else:
                    print(
                        f"❌ Guard '{guard_name}' failed for job {job_id}: {result.message}"
                    )
        else:
            # Check all guards
            results = guard_system.check_all(job_id)

            if console and Table:
                table = Table()
                table.add_column("Guard", style="cyan")
                table.add_column("Status", style="white")
                table.add_column("Message", style="white")

                for result in results:
                    if result.result.value == "pass":
                        status = "✅ PASS"
                        status_style = "green"
                    elif result.result.value == "skipped":
                        status = "  SKIP"
                        status_style = "cyan"
                    else:
                        status = "❌ FAIL"
                        status_style = "red"
                    table.add_row(
                        result.name,
                        f"[{status_style}]{status}[/{status_style}]",
                        result.message,
                    )

                console.print(f"\n📋 Guard Check Results for Job {job_id}")
                console.print(table)
            else:
                print(f"\nGuard Check Results for Job {job_id}")
                print("=" * 50)
                for result in results:
                    if result.result.value == "pass":
                        status = "PASS"
                    elif result.result.value == "skipped":
                        status = "SKIP"
                    else:
                        status = "FAIL"
                    print(f"{result.name}: {status} - {result.message}")

        # After guard checks, show recovery info if available
        try:
            workspace = Path(cfg.workspace)
            recovery = get_crash_recovery(workspace)

            status_info = recovery.get_job_status(job_id)
            if "error" not in status_info and status_info.get("resumable", False):
                if console:
                    console.print("\n🔄 Recovery Information", style="bold blue")
                    console.print(
                        f"Current State: {status_info.get('current_state', 'Unknown')}"
                    )
                    console.print(
                        f"Emergency Shutdown: {'Yes' if status_info.get('emergency_shutdown') else 'No'}"
                    )
                    console.print(f"Use 'plotty resume {job_id}' to recover this job")
                else:
                    print("\nRecovery Information:")
                    print(
                        f"Current State: {status_info.get('current_state', 'Unknown')}"
                    )
                    print(
                        f"Emergency Shutdown: {'Yes' if status_info.get('emergency_shutdown') else 'No'}"
                    )
                    print(f"Use 'plotty resume {job_id}' to recover this job")
        except Exception:
            # Recovery info not available, silently skip
            pass

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
