"""
Guard validate command for ploTTY.
"""

from __future__ import annotations

from pathlib import Path

import typer

from ...utils import error_handler
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


def validate_transition(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to validate"
    ),
    target_state: str = typer.Option(
        "ARMED", "--state", "-s", help="Target state to validate transition to"
    ),
):
    """Validate if job can transition to target state."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        guard_system = create_guard_system(cfg, workspace)

        can_transition, guard_checks = guard_system.can_transition(job_id, target_state)

        if console:
            console.print("🔍 State Transition Validation", style="bold blue")
            console.print(f"Job ID: {job_id}")
            console.print(f"Target State: {target_state}")
            console.print("=" * 50)

            result_style = "green" if can_transition else "red"
            console.print(
                f"Can Transition: [{result_style}]{'YES' if can_transition else 'NO'}[/{result_style}]"
            )

            if guard_checks:
                console.print("\nGuard Results:")
                table = Table()
                table.add_column("Guard", style="cyan")
                table.add_column("Result", style="white")
                table.add_column("Message", style="white")

                for check in guard_checks:
                    check_style = (
                        "green"
                        if check.result.value == "pass"
                        else "red" if check.result.value == "fail" else "yellow"
                    )
                    table.add_row(
                        check.name,
                        f"[{check_style}]{check.result.value.upper()}[/{check_style}]",
                        check.message,
                    )

                console.print(table)
        else:
            print("State Transition Validation")
            print(f"Job ID: {job_id}")
            print(f"Target State: {target_state}")
            print("=" * 50)
            print(f"Can Transition: {'YES' if can_transition else 'NO'}")

            if guard_checks:
                print("\nGuard Results:")
                print(f"{'Guard':<25} {'Result':<12} {'Message'}")
                print("-" * 50)

                for check in guard_checks:
                    print(
                        f"{check.name:<25} {check.result.value.upper():<12} {check.message}"
                    )

        # Exit with appropriate code
        if can_transition:
            raise typer.Exit(ExitCode.SUCCESS)
        else:
            raise typer.Exit(ExitCode.ERROR)

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
