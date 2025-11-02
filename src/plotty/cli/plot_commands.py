"""
Plotting commands for ploTTY CLI.
"""

from __future__ import annotations

from typing import Optional
import typer

from ..utils import error_handler
from ..progress import show_status
from ..presets import get_preset, list_presets, preset_names
from .core import get_available_job_ids

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Table = None

# Create plot command group
plot_app = typer.Typer(help="Plotting commands")


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


@plot_app.command()
def plot(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to plot"
    ),
    preset: str = typer.Option(
        None, "--preset", "-p", help="Plot preset (fast, safe, preview, detail, draft)"
    ),
):
    """Plot a job."""
    try:
        # Validate preset if provided
        if preset and not get_preset(preset):
            available = ", ".join(preset_names())
            raise typer.BadParameter(
                f"Unknown preset '{preset}'. Available: {available}"
            )

        # Get preset details
        preset_obj = None
        preset_info = None
        if preset:
            preset_obj = get_preset(preset)
            preset_info = {
                "name": preset_obj.name,
                "description": preset_obj.description,
                "settings": preset_obj.to_vpype_args(),
            }

        # This will be implemented with actual plotting logic
        if preset:
            show_status(
                f"Plotting job {job_id} with preset '{preset}': {preset_obj.description}",
                "info",
            )
            print(f"Preset settings: {preset_info['settings']}")
        else:
            show_status(f"Plotting job: {job_id}", "info")

        # TODO: Implement actual plotting functionality with preset application
    except Exception as e:
        error_handler.handle(e)


@plot_app.command()
def interactive(port: Optional[str] = None, model: int = 1, units: str = "inches"):
    """Start interactive plotting session."""
    try:
        # TODO: Implement interactive plotting
        print(
            f"Starting interactive session on port {port}, model {model}, units {units}"
        )
    except Exception as e:
        error_handler.handle(e)


@plot_app.command()
def presets():
    """List available plot presets."""
    try:
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


@plot_app.command()
def pen_test(port: Optional[str] = None, model: int = 1, cycles: int = 3):
    """Test pen operation."""
    try:
        # TODO: Implement pen test
        print(f"Running pen test: {cycles} cycles on port {port}, model {model}")
    except Exception as e:
        error_handler.handle(e)
