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
from .common import create_apply_option, create_dry_run_option

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
    apply: bool = create_apply_option("Start plotting (dry-run by default)"),
    dry_run: bool = create_dry_run_option("Preview plotting without moving pen"),
):
    """Start plotting a job with physical setup validation.

    Examples:
        plotty plot my_design
        plotty plot my_design --preset safe --apply
        plotty plot my_design --dry-run --preview

    This command validates physical setup (paper alignment, pen configuration) and
    starts plotting. Use --apply to actually plot, otherwise runs in preview mode.
    
    Available presets:
        fast    - Maximum speed for quick drafts
        safe    - Conservative settings for reliability  
        preview - Quick preview without pen down
        detail  - High precision for detailed artwork
        draft   - Quick draft with moderate quality
    """
    try:
        # Check for dry-run/preview mode
        if dry_run or not apply:
            if console:
                console.print("🔄 Plot Preview Mode:")
                console.print(f"  Job ID: {job_id}")
                if preset:
                    console.print(f"  Preset: {preset}")
                console.print("💡 Use --apply to start actual plotting", style="yellow")
            else:
                print(f"Plot Preview for job {job_id}")
                if preset:
                    print(f"  Preset: {preset}")
                print("Use --apply to start actual plotting")
            return
        # Import presets locally to avoid import issues
        import sys
        import os

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from plotty.presets import get_preset, preset_names

        # Validate preset if provided
        if preset and not get_preset(preset):
            available = ", ".join(preset_names())
            raise typer.BadParameter(
                f"❌ Unknown preset '{preset}'\n"
                f"💡 Available presets: {available}\n"
                f"   • List presets: plotty list presets\n"
                f"   • Use default preset: omit --preset flag"
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

        # Check if job is queued for plotting
        if job_data.get("state") not in ["QUEUED"]:
            show_status(
                f"Job {job_id} must be added first. Run: plotty add job {job_id}",
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

        # Create FSM for proper state management
        from ..fsm import create_fsm, JobState

        fsm = create_fsm(job_id, Path(cfg.workspace))

        # Transition: QUEUED -> ARMED (pre-flight checks)
        if not fsm.arm_job():
            show_status(f"Failed to arm job {job_id} for plotting", "error")
            return

        # Transition: ARMED -> PLOTTING
        if not fsm.transition_to(JobState.PLOTTING, "Starting plotting process"):
            show_status(f"Failed to start plotting for job {job_id}", "error")
            return

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
            # Transition: PLOTTING -> COMPLETED
            fsm.transition_to(JobState.COMPLETED, "Plotting completed successfully")
            show_status(f"Job {job_id} plotted successfully", "success")
            if console:
                console.print(f"   Time: {result['time_elapsed']:.1f}s")
                console.print(f"   Distance: {result['distance_pendown']:.1f}mm")
        else:
            # Transition: PLOTTING -> FAILED
            fsm.transition_to(
                JobState.FAILED,
                f"Plotting failed: {result.get('error', 'Unknown error')}",
            )
            show_status(
                f"Plotting failed: {result.get('error', 'Unknown error')}", "error"
            )
    except Exception as e:
        error_handler.handle(e)


def plan_command(
    job_id: str = typer.Argument(..., autocompletion=complete_job_id, help="Job ID to plan"),
    pen: str = typer.Option("0.3mm black", "--pen", "-p", help="Default pen specification"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive layer planning"),
):
    """Plan a job for plotting with layer analysis.

    Examples:
        plotty plan my_design
        plotty plan my_design --pen "0.5mm red" --interactive
        plotty plan my_design --pen "0.3mm black"

    This command analyzes job layers, estimates plotting time, and creates a plan.
    Interactive mode allows you to assign pens to layers and modify plotting order.
    """
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
    preset: Optional[str] = typer.Option(
        None, "--preset", "-p", help="Optimization preset (fast, default, hq)"
    ),
    digest: Optional[int] = typer.Option(
        None, "--digest", "-d", help="Digest level for AxiDraw acceleration (0-2)"
    ),
    apply: bool = create_apply_option(
        "Actually perform optimization (preview by default)"
    ),
) -> None:
    """Optimize jobs with preview by default."""
    try:
        from ..config import load_config, get_config
        from ..fsm import create_fsm

        cfg = load_config(None)
        config = get_config()
        jobs_dir = Path(cfg.workspace) / "jobs"

        # Validate preset if provided
        if preset and preset not in config.optimization.levels:
            available = ", ".join(config.optimization.levels.keys())
            raise typer.BadParameter(
                f"Unknown preset '{preset}'. Available: {available}"
            )

        # Validate digest if provided
        if digest is not None and digest not in config.optimization.digest_levels:
            available = ", ".join(map(str, config.optimization.digest_levels.keys()))
            raise typer.BadParameter(
                f"Invalid digest level '{digest}'. Available: {available}"
            )

        # Get target jobs
        if job_ids:
            target_ids = [job_id.strip() for job_id in job_ids.split(",")]
        else:
            # Get all jobs that can be optimized (READY or ANALYZED)
            target_ids = []
            if jobs_dir.exists():
                for job_dir in jobs_dir.iterdir():
                    if job_dir.is_dir():
                        job_file = job_dir / "job.json"
                        if job_file.exists():
                            try:
                                job_data = json.loads(job_file.read_text())
                                state = job_data.get("state")
                                # Can optimize jobs in READY or ANALYZED state
                                if state in ["READY", "ANALYZED"]:
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
                    current_state = job_data.get("state", "unknown")
                    current_preset = job_data.get("metadata", {}).get("preset", "none")
                    current_digest = job_data.get("metadata", {}).get("digest", "none")

                    jobs_data.append(
                        {
                            "id": job_id,
                            "name": job_data.get("name", "Unknown"),
                            "current_size": current_size,
                            "state": current_state,
                            "preset": current_preset,
                            "digest": current_digest,
                        }
                    )
                except Exception:
                    jobs_data.append(
                        {
                            "id": job_id,
                            "name": "Unknown",
                            "current_size": 0,
                            "state": "error",
                            "preset": "error",
                            "digest": "error",
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
            table.add_column("State", style="yellow")
            table.add_column("Current Preset", style="blue")
            table.add_column("Current Digest", style="magenta")

            for job in jobs_data:
                size_str = (
                    f"{job['current_size'] / 1024:.1f}KB"
                    if job["current_size"] > 0
                    else "Unknown"
                )

                table.add_row(
                    job["id"],
                    job["name"],
                    job["state"],
                    str(job["preset"]),
                    str(job["digest"]),
                )

            console.print(table)

            # Show optimization settings
            console.print()
            console.print("🎯 Optimization Settings:", style="bold")
            if preset:
                console.print(f"  Preset: {preset}", style="green")
            else:
                console.print(
                    f"  Preset: {config.optimization.default_level} (default)",
                    style="yellow",
                )

            if digest is not None:
                console.print(f"  Digest: {digest}", style="green")
            else:
                console.print(
                    f"  Digest: {config.optimization.default_digest} (default)",
                    style="yellow",
                )

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
                print(f"{job['id']}: {job['name']} ({size_str}) - {job['state']}")
            print("\nOptimization settings:")
            print(f"  Preset: {preset or config.optimization.default_level}")
            print(f"  Digest: {digest or config.optimization.default_digest}")
            print(f"\nUse --apply to optimize {len(jobs_data)} jobs")

        if not apply:
            return

        # Perform optimization using FSM with progress tracking
        from ..progress import progress_task
        
        optimized_count = 0
        failed_count = 0

        with progress_task(f"Optimizing {len(jobs_data)} jobs", len(target_ids)) as update:
            for i, job_id in enumerate(target_ids):
                try:
                    # Create FSM for the job
                    fsm = create_fsm(job_id, Path(cfg.workspace))

                    # Apply optimizations with specified or default settings
                    effective_preset = preset or config.optimization.default_level
                    effective_digest = (
                        digest if digest is not None else config.optimization.default_digest
                    )

                    if fsm.apply_optimizations(
                        preset=effective_preset, digest=effective_digest
                    ):
                        optimized_count += 1
                        if console:
                            console.print(
                                f"  ✓ Optimized {job_id} (preset: {effective_preset}, digest: {effective_digest})",
                                style="green",
                            )
                        else:
                            print(f"  Optimized {job_id}")
                    else:
                        failed_count += 1
                        if console:
                            console.print(f"  ❌ Failed to optimize {job_id}", style="red")
                        else:
                            print(f"  Failed to optimize {job_id}")

                    # Update progress
                    update(1)

                except Exception as e:
                    failed_count += 1
                    if console:
                        console.print(f"  ❌ Failed to optimize {job_id}: {e}", style="red")
                    else:
                        print(f"  Failed to optimize {job_id}: {e}")
                    
                    # Still update progress even on failure
                    update(1)

        show_status(
            f"Optimized {optimized_count} jobs, {failed_count} failed",
            "success" if failed_count == 0 else "warning",
        )

    except Exception as e:
        error_handler.handle(e)


def queue_command(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to queue for plotting"
    ),
):
    """Manually queue a job for plotting (READY → QUEUED).

    Note: 'plotty add job' automatically queues jobs. Use this command for manual control
    or when you need to queue jobs that were added with --no-queue flag (future feature).
    """
    try:
        from ..config import load_config
        from ..fsm import create_fsm
        from pathlib import Path
        import json

        cfg = load_config(None)
        job_dir = Path(cfg.workspace) / "jobs" / job_id

        if not job_dir.exists():
            raise typer.BadParameter(f"Job {job_id} not found")

        # Load job metadata
        job_file = job_dir / "job.json"
        if not job_file.exists():
            raise typer.BadParameter(f"Job metadata not found for {job_id}")

        job_data = json.loads(job_file.read_text())
        current_state = job_data.get("state")

        # Check if job is in READY state
        if current_state != "READY":
            raise typer.BadParameter(
                f"Job {job_id} is in '{current_state}' state, must be in 'READY' state to queue"
            )

        # Create FSM and transition to QUEUED using proper method
        fsm = create_fsm(job_id, Path(cfg.workspace))

        if fsm.queue_ready_job():
            show_status(f"✓ Job {job_id} manually queued for plotting", "success")
        else:
            show_status(f"✗ Failed to queue job {job_id}", "error")
            raise typer.Exit(1)

    except Exception as e:
        error_handler.handle(e)


__all__ = ["start_command", "plan_command", "optimize_command", "queue_command"]
