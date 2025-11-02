"""
Guard check command for ploTTY.
"""

from __future__ import annotations

from pathlib import Path

import typer

from ...utils import error_handler
from ...config import load_config
from ...guards import create_guard_system
from ...exit_codes import ExitCode
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


def check_guards(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to check"
    ),
    guard_name: str = typer.Option(
        None, "--guard", "-g", help="Specific guard to check (default: all)"
    ),
):
    """Check guards for a job."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        guard_system = create_guard_system(cfg, workspace)

        if guard_name:
            # Check specific guard
            result = guard_system.check_guard(guard_name, job_id)

            if console:
                console.print(f"🛡️  Guard Check: {guard_name}", style="bold blue")
                console.print("=" * 50)

                console.print(
                    f"Result: [{result.result.value}]{result.result.value.upper()}[/{result.result.value}]"
                )
                console.print(f"Message: {result.message}")

                if result.details:
                    console.print("Details:")
                    for key, value in result.details.items():
                        console.print(f"  {key}: {value}")
            else:
                print(f"Guard Check: {guard_name}")
                print("=" * 50)
                print(f"Result: {result.result.value.upper()}")
                print(f"Message: {result.message}")

                if result.details:
                    print("Details:")
                    for key, value in result.details.items():
                        print(f"  {key}: {value}")
        else:
            # Check all guards
            results = guard_system.check_all(job_id)

            if console:
                console.print(
                    f"🛡️  All Guards Check for Job '{job_id}'", style="bold blue"
                )
                console.print("=" * 50)

                table = Table()
                table.add_column("Guard", style="cyan")
                table.add_column("Result", style="white")
                table.add_column("Message", style="white")

                for result in results:
                    result_style = (
                        "green"
                        if result.result.value == "pass"
                        else "red"
                        if result.result.value == "fail"
                        else "yellow"
                    )
                    table.add_row(
                        result.name,
                        f"[{result_style}]{result.result.value.upper()}[/{result_style}]",
                        result.message,
                    )

                console.print(table)

                # Summary
                passed = sum(1 for r in results if r.result.value == "pass")
                failed = sum(1 for r in results if r.result.value == "fail")
                soft_failed = sum(1 for r in results if r.result.value == "soft_fail")

                console.print(
                    f"\nSummary: {passed} passed, {failed} failed, {soft_failed} soft-failed"
                )
            else:
                print(f"All Guards Check for Job '{job_id}'")
                print("=" * 50)
                print(f"{'Guard':<25} {'Result':<12} {'Message'}")
                print("-" * 50)

                for result in results:
                    print(
                        f"{result.name:<25} {result.result.value.upper():<12} {result.message}"
                    )

                # Summary
                passed = sum(1 for r in results if r.result.value == "pass")
                failed = sum(1 for r in results if r.result.value == "fail")
                soft_failed = sum(1 for r in results if r.result.value == "soft_fail")

                print(
                    f"\nSummary: {passed} passed, {failed} failed, {soft_failed} soft-failed"
                )

    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
