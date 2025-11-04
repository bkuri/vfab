"""
Main level job commands for ploTTY CLI.
"""

from __future__ import annotations

from typing import Optional
import json
from pathlib import Path
import typer

from ..utils import error_handler
from ..progress import show_status
from ..config import load_config
from .core import get_available_job_ids

try:
    from rich.console import Console

    console = Console()
except ImportError:
    console = None


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


def start_command(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to start"
    ),
    preset: str = typer.Option(
        None, "--preset", "-p", help="Plot preset (fast, safe, preview, detail, draft)"
    ),
    port: Optional[str] = typer.Option(None, "--port", help="Device port"),
    model: int = typer.Option(1, "--model", help="Device model"),
):
    """Start plotting a job."""
    try:
        # Import presets locally to avoid import issues
        import sys
        import os

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from plotty.presets import get_preset, preset_names

        # Validate preset if provided
        if preset and not get_preset(preset):
            available = ", ".join(preset_names())
            raise typer.BadParameter(
                f"Unknown preset '{preset}'. Available: {available}"
            )

        # Get preset details if provided
        preset_obj = None
        if preset:
            preset_obj = get_preset(preset)
            if not preset_obj:
                available = ", ".join(preset_names())
                raise typer.BadParameter(
                    f"Unknown preset '{preset}'. Available: {available}"
                )

            show_status(
                f"Starting job {job_id} with preset '{preset}': {preset_obj.description}",
                "info",
            )
        else:
            show_status(f"Starting job {job_id} with default settings", "info")

        # Load job and validate
        cfg = load_config(None)
        job_dir = Path(cfg.workspace) / "jobs" / job_id

        if not job_dir.exists():
            raise typer.BadParameter(f"Job {job_id} not found")

        job_file = job_dir / "job.json"
        if not job_file.exists():
            raise typer.BadParameter(f"Job metadata not found for {job_id}")

        job_data = json.loads(job_file.read_text())

        # Check if job is planned
        if job_data.get("state") not in ["OPTIMIZED", "READY"]:
            show_status(
                f"Job {job_id} must be planned first. Run: plotty plan {job_id}",
                "warning",
            )
            return

        # Find optimized SVG file
        optimized_svg = job_dir / "multipen.svg"
        if not optimized_svg.exists():
            optimized_svg = job_dir / "src.svg"

        if not optimized_svg.exists():
            raise typer.BadParameter(f"No SVG file found for job {job_id}")

        # Show time estimation before plotting
        if console:
            show_status("Calculating time estimation...", "info")

            # Use AxiDraw preview mode for accurate time estimation
            from ..plotting import MultiPenPlotter

            preview_plotter = MultiPenPlotter(port=port, model=model, interactive=False)

            # Apply preset settings to preview if provided
            if preset_obj:
                preset_settings = preset_obj.to_vpype_args()
                device_config = {
                    "speed_pendown": int(preset_settings.get("speed", 25)),
                    "speed_penup": int(preset_settings.get("speed", 75)),
                    "pen_pos_up": int(preset_settings.get("pen_height", 60)),
                    "pen_pos_down": int(preset_settings.get("pen_height", 40)),
                }
                for key, value in device_config.items():
                    if hasattr(preview_plotter.manager, key):
                        setattr(preview_plotter.manager, key, value)

            # Run preview to get time estimate
            preview_result = preview_plotter.manager.plot_file(
                optimized_svg, preview_only=True
            )

            if preview_result.get("success"):
                est_time = preview_result.get("time_estimate", 0)
                est_distance = preview_result.get("distance_pendown", 0)

                console.print(f"\n⏱️  Estimated time: {est_time / 60:.1f} minutes")
                console.print(f"📏 Estimated distance: {est_distance:.1f}mm")

                if preset_obj:
                    speed_factor = preset_obj.speed / 100.0
                    console.print(f"⚡ Speed factor: {speed_factor:.1f}x")
            else:
                console.print("⚠️  Could not estimate time", style="yellow")

        # Use MultiPenPlotter for actual plotting
        from ..plotting import MultiPenPlotter

        # Create plotter
        plotter = MultiPenPlotter(port=port, model=model)

        # Apply preset settings to device manager if preset provided
        if preset_obj:
            preset_settings = preset_obj.to_vpype_args()
            # Convert preset settings to device manager parameters
            device_config = {
                "speed_pendown": int(preset_settings.get("speed", 25)),
                "speed_penup": int(preset_settings.get("speed", 75)),
                "pen_pos_up": int(preset_settings.get("pen_height", 60)),
                "pen_pos_down": int(preset_settings.get("pen_height", 40)),
            }
            # Apply settings to manager
            for key, value in device_config.items():
                if hasattr(plotter.manager, key):
                    setattr(plotter.manager, key, value)

        # Execute plotting using AxiDraw layer control method
        result = plotter.plot_with_axidraw_layers(optimized_svg)

        if result["success"]:
            show_status(f"Job {job_id} plotted successfully", "success")
            if console:
                console.print(f"   Time: {result['time_elapsed']:.1f}s")
                console.print(f"   Distance: {result['distance_pendown']:.1f}mm")
        else:
            show_status(
                f"Plotting failed: {result.get('error', 'Unknown error')}", "error"
            )
    except Exception as e:
        error_handler.handle(e)


def plan_command(
    job_id: str,
    pen: str = "0.3mm black",
    interactive: bool = False,
):
    """Plan a job for plotting."""
    try:
        from ..planner import JobPlanner
        from ..config import load_config
        from pathlib import Path

        cfg = load_config(None)
        job_dir = Path(cfg.workspace) / "jobs" / job_id

        if not job_dir.exists():
            raise typer.BadParameter(f"Job {job_id} not found")

        planner = JobPlanner(cfg)
        planner.plan_job(job_id, pen, interactive)

        show_status(f"Job {job_id} planned successfully", "success")

    except Exception as e:
        error_handler.handle(e)


__all__ = ["start_command", "plan_command"]
