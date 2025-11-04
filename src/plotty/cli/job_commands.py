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
from ..planner import plan_layers
from .core import get_available_job_ids
from .common import create_apply_option

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
        from ..config import load_config
        from pathlib import Path
        import json

        cfg = load_config(None)
        job_dir = Path(cfg.workspace) / "jobs" / job_id

        if not job_dir.exists():
            raise typer.BadParameter(f"Job {job_id} not found")

        # Find source SVG file
        src_svg = job_dir / "src.svg"
        if not src_svg.exists():
            raise typer.BadParameter(f"Source SVG not found for job {job_id}")

        # Plan the job using plan_layers function
        result = plan_layers(
            src_svg=src_svg,
            preset=cfg.vpype.preset,
            presets_file=cfg.vpype.presets_file,
            pen_map=None,  # Will use default pen mapping
            out_dir=job_dir,
            interactive=interactive,
            paper_size="A4",
        )

        # Update job metadata
        job_file = job_dir / "job.json"
        if job_file.exists():
            job_data = json.loads(job_file.read_text())
            job_data["state"] = "OPTIMIZED"
            job_data["planning"] = {
                "layer_count": result["layer_count"],
                "pen_map": result["pen_map"],
                "estimates": result["estimates"],
                "planned_at": str(Path.cwd()),
            }
            job_file.write_text(json.dumps(job_data, indent=2))

        show_status(f"Job {job_id} planned successfully", "success")

    except Exception as e:
        error_handler.handle(e)


def optimize_command(
    job_ids: Optional[str] = typer.Argument(
        None, help="Comma-separated job IDs to optimize"
    ),
    apply: bool = create_apply_option(
        "Actually perform optimization (preview by default)"
    ),
) -> None:
    """Optimize jobs with preview by default."""
    try:
        from ..config import load_config
        from ..utils import error_handler
        from ..progress import show_status
        from ..planner import plan_layers
        from pathlib import Path
        import json

        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        # Get target jobs
        if job_ids:
            target_ids = [job_id.strip() for job_id in job_ids.split(",")]
        else:
            # Get all pristine jobs
            target_ids = []
            if jobs_dir.exists():
                for job_dir in jobs_dir.iterdir():
                    if job_dir.is_dir():
                        job_file = job_dir / "job.json"
                        if job_file.exists():
                            try:
                                job_data = json.loads(job_file.read_text())
                                if (
                                    job_data.get("optimization", {}).get("level")
                                    == "none"
                                ):
                                    target_ids.append(job_dir.name)
                            except Exception:
                                continue

        if not target_ids:
            show_status("No jobs found to optimize", "info")
            return

        # Show preview table
        jobs_data = []
        for job_id in target_ids:
            job_dir = jobs_dir / job_id
            job_file = job_dir / "job.json"
            if job_file.exists():
                try:
                    job_data = json.loads(job_file.read_text())
                    src_file = job_dir / "src.svg"
                    current_size = src_file.stat().st_size if src_file.exists() else 0

                    jobs_data.append(
                        {
                            "id": job_id,
                            "name": job_data.get("name", "Unknown"),
                            "current_size": current_size,
                            "status": job_data.get("optimization", {}).get(
                                "level", "none"
                            ),
                        }
                    )
                except Exception:
                    jobs_data.append(
                        {
                            "id": job_id,
                            "name": "Unknown",
                            "current_size": 0,
                            "status": "error",
                        }
                    )

        # Display preview table
        if console:
            console.print("🔧 Job Optimization Summary")
            console.print()

            from rich.table import Table

            table = Table()
            table.add_column("Job ID", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Current Size", style="yellow")
            table.add_column("Status", style="green")

            for job in jobs_data:
                size_str = (
                    f"{job['current_size'] / 1024:.1f}KB"
                    if job["current_size"] > 0
                    else "Unknown"
                )
                status_style = "red" if job["status"] == "none" else "green"
                status_text = "Pristine" if job["status"] == "none" else "Optimized"

                table.add_row(
                    job["id"],
                    job["name"],
                    size_str,
                    f"[{status_style}]{status_text}[/{status_style}]",
                )

            console.print(table)
            console.print()
            console.print(
                f"💡 Use --apply to optimize {len(jobs_data)} jobs", style="yellow"
            )
        else:
            print("Job Optimization Summary")
            print("=" * 25)
            for job in jobs_data:
                size_str = (
                    f"{job['current_size'] / 1024:.1f}KB"
                    if job["current_size"] > 0
                    else "Unknown"
                )
                status_text = "Pristine" if job["status"] == "none" else "Optimized"
                print(f"{job['id']}: {job['name']} ({size_str}) - {status_text}")
            print(f"\nUse --apply to optimize {len(jobs_data)} jobs")

        if not apply:
            return

        # Perform optimization
        show_status(f"Optimizing {len(jobs_data)} jobs...", "info")
        optimized_count = 0
        failed_count = 0

        for job_id in target_ids:
            try:
                # Find source SVG file
                src_svg = jobs_dir / job_id / "src.svg"
                if not src_svg.exists():
                    raise FileNotFoundError(f"Source SVG not found for job {job_id}")

                # Plan the job using plan_layers function
                plan_layers(
                    src_svg=src_svg,
                    preset=cfg.vpype.preset,
                    presets_file=cfg.vpype.presets_file,
                    pen_map=None,  # Will use default pen mapping
                    out_dir=jobs_dir / job_id,
                    interactive=False,
                    paper_size="A4",
                )

                # Update optimization metadata
                job_file = jobs_dir / job_id / "job.json"
                if job_file.exists():
                    job_data = json.loads(job_file.read_text())
                    job_data["optimization"] = {
                        "level": "full",
                        "applied_at": str(Path.cwd()),
                        "version": "1.0",
                    }
                    job_file.write_text(json.dumps(job_data, indent=2))

                optimized_count += 1
                if console:
                    console.print(f"  ✓ Optimized {job_id}", style="green")
                else:
                    print(f"  Optimized {job_id}")

            except Exception as e:
                failed_count += 1
                if console:
                    console.print(f"  ❌ Failed to optimize {job_id}: {e}", style="red")
                else:
                    print(f"  Failed to optimize {job_id}: {e}")

        show_status(
            f"Optimized {optimized_count} jobs, {failed_count} failed",
            "success" if failed_count == 0 else "warning",
        )

    except Exception as e:
        error_handler.handle(e)


__all__ = ["start_command", "plan_command", "optimize_command"]
