"""
List plot presets command for ploTTY CLI.
"""

from __future__ import annotations

import typer
from ...utils import error_handler
from ..status.output import get_output_manager

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Table = None


def list_plot_presets(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
) -> None:
    """List available plot presets."""
    try:
        import sys
        import os

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        from plotty.presets import list_presets

        all_presets = list_presets()

        # Prepare data
        headers = ["Name", "Description", "Speed", "Pressure", "Passes"]
        rows = []

        for preset in all_presets.values():
            rows.append(
                [
                    preset.name,
                    preset.description,
                    f"{preset.speed:.0f}%",
                    str(preset.pen_pressure),
                    str(preset.passes),
                ]
            )

        # Prepare JSON data
        presets_data = []
        for preset in all_presets.values():
            presets_data.append(
                {
                    "name": preset.name,
                    "description": preset.description,
                    "speed": preset.speed,
                    "pen_pressure": preset.pen_pressure,
                    "passes": preset.passes,
                }
            )

        # Output in requested format
        if json_output:
            import json

            typer.echo(json.dumps(presets_data, indent=2))
        elif csv_output:
            import csv
            import sys

            writer = csv.writer(sys.stdout)
            writer.writerow(headers)
            writer.writerows(rows)
        else:
            # Rich table output (default)
            output = get_output_manager()

            # Build markdown content
            markdown_content = output.print_table_markdown(
                title="Available Plot Presets", headers=headers, rows=rows
            )

            # Output using the manager
            output.print_markdown(
                content=markdown_content,
                json_data={"presets": presets_data},
                json_output=json_output,
                csv_output=csv_output,
            )

    except Exception as e:
        error_handler.handle(e)
