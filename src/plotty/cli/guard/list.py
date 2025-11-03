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


def list_guards(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
) -> None:
    """List available guards."""
    try:
        # Prepare data
        headers = ["Guard Name", "Description", "Type"]
        guards_info = [
            ("device_idle", "Ensures plotter device is idle", "System"),
            ("camera_health", "Checks camera system health", "System"),
            ("checklist_complete", "Validates job checklist completion", "Job"),
            ("paper_session_valid", "Ensures one paper per session", "Job"),
            ("pen_layer_compatible", "Validates pen-layer compatibility", "Job"),
        ]
        rows = [[name, desc, guard_type] for name, desc, guard_type in guards_info]

        # Output in requested format
        if json_output:
            import json

            guards_data = [
                {"name": name, "description": desc, "type": guard_type}
                for name, desc, guard_type in guards_info
            ]
            typer.echo(json.dumps(guards_data, indent=2))
        elif csv_output:
            import csv
            import sys

            writer = csv.writer(sys.stdout)
            writer.writerow(headers)
            writer.writerows(rows)
        else:
            # Markdown output (default)
            typer.echo("# 🛡️ Available System Guards")
            typer.echo()
            typer.echo("| " + " | ".join(headers) + " |")
            typer.echo("| " + " | ".join(["---"] * len(headers)) + " |")

            for row in rows:
                typer.echo("| " + " | ".join(row) + " |")

    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
