"""
List plot presets command for ploTTY CLI.
"""

from __future__ import annotations

from ...utils import error_handler

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Table = None


def list_plot_presets():
    """List available plot presets."""
    try:
        import sys
        import os

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        from plotty.presets import list_presets

        all_presets = list_presets()

        if console and Table:
            table = Table(title="Available Plot Presets")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Speed", style="white", justify="right")
            table.add_column("Pressure", style="white", justify="right")
            table.add_column("Passes", style="white", justify="right")

            for preset in all_presets.values():
                table.add_row(
                    preset.name,
                    preset.description,
                    f"{preset.speed:.0f}%",
                    f"{preset.pen_pressure}",
                    f"{preset.passes}",
                )

            console.print(table)
        else:
            print("Available Plot Presets:")
            for preset in all_presets.values():
                print(f"  {preset.name}: {preset.description}")
                print(
                    f"    Speed: {preset.speed:.0f}%, Pressure: {preset.pen_pressure}, Passes: {preset.passes}"
                )

    except Exception as e:
        error_handler.handle(e)
