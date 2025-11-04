"""
Job checking command for ploTTY CLI.
"""

from __future__ import annotations

import typer
from pathlib import Path

from ...config import load_config
from ...guards import create_guard_system
from ...codes import ExitCode
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
            if result.passed:
                if console:
                    console.print(
                        f"✅ Guard '{guard_name}' passed for job {job_id}",
                        style="green",
                    )
                else:
                    print(f"✅ Guard '{guard_name}' passed for job {job_id}")
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
            results = guard_system.check_all_guards(job_id)

            if console and Table:
                table = Table()
                table.add_column("Guard", style="cyan")
                table.add_column("Status", style="white")
                table.add_column("Message", style="white")

                for guard_name, result in results.items():
                    status = "✅ PASS" if result.passed else "❌ FAIL"
                    status_style = "green" if result.passed else "red"
                    table.add_row(
                        guard_name,
                        f"[{status_style}]{status}[/{status_style}]",
                        result.message,
                    )

                console.print(f"\n📋 Guard Check Results for Job {job_id}")
                console.print(table)
            else:
                print(f"\nGuard Check Results for Job {job_id}")
                print("=" * 50)
                for guard_name, result in results.items():
                    status = "PASS" if result.passed else "FAIL"
                    print(f"{guard_name}: {status} - {result.message}")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
