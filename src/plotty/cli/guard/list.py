"""
Guard list command for ploTTY.
"""

from __future__ import annotations


import typer

from ...utils import error_handler
from ...codes import ExitCode

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Table = None


def list_guards():
    """List available guards."""
    try:
        if console:
            console.print("🛡️  Available System Guards", style="bold blue")
            console.print("=" * 40)

            table = Table()
            table.add_column("Guard Name", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Type", style="yellow")

            guards_info = [
                ("device_idle", "Ensures plotter device is idle", "System"),
                ("camera_health", "Checks camera system health", "System"),
                ("checklist_complete", "Validates job checklist completion", "Job"),
                ("paper_session_valid", "Ensures one paper per session", "Job"),
                ("pen_layer_compatible", "Validates pen-layer compatibility", "Job"),
            ]

            for name, desc, guard_type in guards_info:
                table.add_row(name, desc, guard_type)

            console.print(table)
        else:
            print("Available System Guards:")
            print("=" * 40)
            print(f"{'Guard Name':<25} {'Description':<35} {'Type':<8}")
            print("-" * 40)

            guards_info = [
                ("device_idle", "Ensures plotter device is idle", "System"),
                ("camera_health", "Checks camera system health", "System"),
                ("checklist_complete", "Validates job checklist completion", "Job"),
                ("paper_session_valid", "Ensures one paper per session", "Job"),
                ("pen_layer_compatible", "Validates pen-layer compatibility", "Job"),
            ]

            for name, desc, guard_type in guards_info:
                print(f"{name:<25} {desc:<35} {guard_type:<8}")

    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
