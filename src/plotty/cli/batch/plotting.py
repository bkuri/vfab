"""
Batch plotting commands.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer

from ...utils import error_handler
from ...progress import show_status
from ...plotting import MultiPenPlotter
from .utils import get_jobs_by_state, group_layers_by_pen

try:
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Confirm = None


def plot_all(
    by_pen: bool = typer.Option(
        False,
        "--by-pen",
        help="Group plotting by pen to minimize pen changes (recommended for multi-pen plots)",
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Execute plotting (default: preview mode only)"
    ),
    preset: str = typer.Option(
        None,
        "--preset",
        help="Plot preset for all jobs (fast, safe, preview, detail, draft)",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", help="Minimal output (show only errors and final results)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", help="Detailed output (show individual layer/job progress)"
    ),
    confirm: bool = typer.Option(
        None,
        "--confirm/--no-confirm",
        help="Ask for confirmation before plotting (default: ask)",
    ),
):
    """Plot multiple jobs with pen optimization.

    Examples:
        plotty batch plot-all --by-pen --apply
        plotty batch plot-all --preset fast --apply
        plotty batch plot-all --by-pen --preset safe --verbose --apply

    Without --apply, shows preview and time estimation only.
    """
    try:
        jobs = get_jobs_by_state("READY")  # Only plot ready jobs

        if not jobs:
            if not quiet:
                show_status("No READY jobs found for plotting", "warning")
            return

        if by_pen:
            pen_groups = group_layers_by_pen(jobs)

            if not quiet:
                if console:
                    console.print("📋 Plotting Guide Preview")
                    console.print("=" * 50)

                    step_num = 1
                    for pen_name, layers in pen_groups.items():
                        console.print(f"\n🖊️  Step {step_num}: Load {pen_name} pen")
                        console.print("   Ready to plot:")

                        for item in layers:
                            job = item["job"]
                            layer = item["layer"]
                            if verbose:
                                console.print(
                                    f"   • {job['name']} - {layer.name} ({len(layer.elements)} elements)"
                                )
                            else:
                                console.print(f"   • {job['name']} - {layer.name}")

                        step_num += 1

                    console.print("\n🎯 To execute guided plotting:")
                    console.print("    plotty batch plot-all --by-pen --apply")
                else:
                    print("📋 Plotting Guide Preview")
                    print("=" * 50)
                    step_num = 1
                    for pen_name, layers in pen_groups.items():
                        print(f"\nStep {step_num}: Load {pen_name} pen")
                        print("   Ready to plot:")
                        for item in layers:
                            job = item["job"]
                            layer = item["layer"]
                            if verbose:
                                print(
                                    f"   • {job['name']} - {layer.name} ({len(layer.elements)} elements)"
                                )
                            else:
                                print(f"   • {job['name']} - {layer.name}")
                        step_num += 1
                    print("\nTo execute: plotty batch plot-all --by-pen --apply")

        # Execute batch plotting setup
        from ...config import load_config
        import sys
        import os

        # Import presets locally to avoid import issues
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        try:
            from plotty.presets import get_preset
        except ImportError:
            get_preset = None

        # Get preset if specified
        preset_obj = None
        if preset:
            if not get_preset:
                raise typer.BadParameter(
                    f"Preset system unavailable. Cannot use preset '{preset}'."
                )

            preset_obj = get_preset(preset)
            if not preset_obj:
                # Try to get available preset names for better error message
                try:
                    from plotty.presets import preset_names

                    available = ", ".join(preset_names())
                except Exception:
                    available = "preset system unavailable"
                raise typer.BadParameter(
                    f"Unknown preset '{preset}'. Available: {available}"
                )

        # Show time estimation preview before asking for confirmation
        if not quiet and (apply or not console):
            show_status("Calculating time estimation...", "info")

            # Create preview plotter for time estimation
            preview_plotter = MultiPenPlotter(port=None, model=1, interactive=False)

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

            total_est_time = 0
            total_est_distance = 0

            if by_pen:
                # Calculate time for pen-optimized plotting
                pen_groups = group_layers_by_pen(jobs)

                for pen_name, layers in pen_groups.items():
                    pen_time = 0
                    pen_distance = 0

                    for item in layers:
                        job = item["job"]
                        layer = item["layer"]
                        job_dir = job["path"]

                        # Find layer SVG file
                        layer_svg = job_dir / "layers" / f"{layer.name}.svg"
                        if not layer_svg.exists():
                            layer_svg = job_dir / "multipen.svg"
                        if not layer_svg.exists():
                            layer_svg = job_dir / "src.svg"

                        if layer_svg.exists():
                            try:
                                preview_result = preview_plotter.manager.plot_file(
                                    layer_svg, preview_only=True
                                )
                                if preview_result.get("success"):
                                    pen_time += preview_result.get("time_estimate", 0)
                                    pen_distance += preview_result.get(
                                        "distance_pendown", 0
                                    )
                            except Exception:
                                pass  # Skip if preview fails

                    if console:
                        console.print(
                            f"🖊️  {pen_name}: {pen_time / 60:.1f} min, {pen_distance:.0f}mm"
                        )
                    else:
                        print(
                            f"{pen_name}: {pen_time / 60:.1f} min, {pen_distance:.0f}mm"
                        )

                    total_est_time += pen_time
                    total_est_distance += pen_distance
            else:
                # Calculate time for traditional batch plotting
                for job in jobs:
                    job_dir = job["path"]

                    # Find optimized SVG file
                    optimized_svg = job_dir / "multipen.svg"
                    if not optimized_svg.exists():
                        optimized_svg = job_dir / "src.svg"

                    if optimized_svg.exists():
                        try:
                            preview_result = preview_plotter.manager.plot_file(
                                optimized_svg, preview_only=True
                            )
                            if preview_result.get("success"):
                                total_est_time += preview_result.get("time_estimate", 0)
                                total_est_distance += preview_result.get(
                                    "distance_pendown", 0
                                )
                        except Exception:
                            pass  # Skip if preview fails

            # Show total estimation
            if console:
                console.print(
                    f"\n⏱️  Total estimated time: {total_est_time / 60:.1f} minutes"
                )
                console.print(
                    f"📏 Total estimated distance: {total_est_distance:.0f}mm"
                )
                if preset_obj:
                    speed_factor = preset_obj.speed / 100.0
                    console.print(f"⚡ Speed factor: {speed_factor:.1f}x")
                console.print("")
            else:
                print(f"\nTotal estimated time: {total_est_time / 60:.1f} minutes")
                print(f"Total estimated distance: {total_est_distance:.0f}mm")
                if preset_obj:
                    speed_factor = preset_obj.speed / 100.0
                    print(f"Speed factor: {speed_factor:.1f}x")
                print("")

        # Show time estimation preview before asking for confirmation
        if not quiet and (apply or not console):
            show_status("Calculating time estimation...", "info")

            # Create preview plotter for time estimation
            preview_plotter = MultiPenPlotter(port=None, model=1, interactive=False)

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

            total_est_time = 0
            total_est_distance = 0

            if by_pen:
                # Calculate time for pen-optimized plotting
                pen_groups = group_layers_by_pen(jobs)

                for pen_name, layers in pen_groups.items():
                    pen_time = 0
                    pen_distance = 0

                    for item in layers:
                        job = item["job"]
                        layer = item["layer"]
                        job_dir = job["path"]

                        # Find layer SVG file
                        layer_svg = job_dir / "layers" / f"{layer.name}.svg"
                        if not layer_svg.exists():
                            layer_svg = job_dir / "multipen.svg"
                        if not layer_svg.exists():
                            layer_svg = job_dir / "src.svg"

                        if layer_svg.exists():
                            try:
                                preview_result = preview_plotter.manager.plot_file(
                                    layer_svg, preview_only=True
                                )
                                if preview_result.get("success"):
                                    pen_time += preview_result.get("time_estimate", 0)
                                    pen_distance += preview_result.get(
                                        "distance_pendown", 0
                                    )
                            except Exception:
                                pass  # Skip if preview fails

                    if console:
                        console.print(
                            f"🖊️  {pen_name}: {pen_time / 60:.1f} min, {pen_distance:.0f}mm"
                        )
                    else:
                        print(
                            f"{pen_name}: {pen_time / 60:.1f} min, {pen_distance:.0f}mm"
                        )

                    total_est_time += pen_time
                    total_est_distance += pen_distance
            else:
                # Calculate time for traditional batch plotting
                for job in jobs:
                    job_dir = job["path"]

                    # Find optimized SVG file
                    optimized_svg = job_dir / "multipen.svg"
                    if not optimized_svg.exists():
                        optimized_svg = job_dir / "src.svg"

                    if optimized_svg.exists():
                        try:
                            preview_result = preview_plotter.manager.plot_file(
                                optimized_svg, preview_only=True
                            )
                            if preview_result.get("success"):
                                total_est_time += preview_result.get("time_estimate", 0)
                                total_est_distance += preview_result.get(
                                    "distance_pendown", 0
                                )
                        except Exception:
                            pass  # Skip if preview fails

            # Show total estimation
            if console:
                console.print(
                    f"\n⏱️  Total estimated time: {total_est_time / 60:.1f} minutes"
                )
                console.print(
                    f"📏 Total estimated distance: {total_est_distance:.0f}mm"
                )
                if preset_obj:
                    speed_factor = preset_obj.speed / 100.0
                    console.print(f"⚡ Speed factor: {speed_factor:.1f}x")
                console.print("")
            else:
                print(f"\nTotal estimated time: {total_est_time / 60:.1f} minutes")
                print(f"Total estimated distance: {total_est_distance:.0f}mm")
                if preset_obj:
                    speed_factor = preset_obj.speed / 100.0
                    print(f"Speed factor: {speed_factor:.1f}x")
                print("")

        if apply:
            # Ask for confirmation unless --no-confirm is specified
            if confirm is not False and console and Confirm:
                action = "pen-optimized plotting" if by_pen else "batch plotting"
                if not Confirm.ask(f"\nExecute {action} for {len(jobs)} jobs?"):
                    if not quiet:
                        show_status("Plotting cancelled by user", "info")
                    return

            # Create actual plotter
            plotter = MultiPenPlotter(port=None, model=1)  # Use default port/model

            # Apply preset settings if provided
            if preset_obj:
                preset_settings = preset_obj.to_vpype_args()
                device_config = {
                    "speed_pendown": int(preset_settings.get("speed", 25)),
                    "speed_penup": int(preset_settings.get("speed", 75)),
                    "pen_pos_up": int(preset_settings.get("pen_height", 60)),
                    "pen_pos_down": int(preset_settings.get("pen_height", 40)),
                }
                for key, value in device_config.items():
                    if hasattr(plotter.manager, key):
                        setattr(plotter.manager, key, value)

            successful_plots = []
            failed_plots = []
            total_time = 0
            total_distance = 0

            if by_pen:
                # Pen-optimized plotting - group by pen and plot sequentially
                pen_groups = group_layers_by_pen(jobs)

                if not quiet:
                    if console:
                        console.print(
                            f"\n🖊️  Starting pen-optimized plotting ({len(pen_groups)} pen groups)"
                        )
                    else:
                        print(
                            f"\nStarting pen-optimized plotting ({len(pen_groups)} pen groups)"
                        )

                step_num = 1
                for pen_name, layers in pen_groups.items():
                    if not quiet:
                        if console:
                            console.print(
                                f"\n📝 Step {step_num}: Loading {pen_name} pen"
                            )
                            console.print(f"   Plotting {len(layers)} layers...")
                        else:
                            print(f"\nStep {step_num}: Loading {pen_name} pen")
                            print(f"   Plotting {len(layers)} layers...")

                    # Plot all layers for this pen
                    for item in layers:
                        job = item["job"]
                        layer = item["layer"]
                        job_id = job["id"]
                        job_dir = job["path"]

                        try:
                            # Find the layer SVG file
                            layer_svg = job_dir / "layers" / f"{layer.name}.svg"
                            if not layer_svg.exists():
                                # Fallback to main optimized SVG
                                layer_svg = job_dir / "multipen.svg"
                            if not layer_svg.exists():
                                layer_svg = job_dir / "src.svg"

                            if not layer_svg.exists():
                                failed_plots.append(
                                    {
                                        "job_id": job_id,
                                        "layer": layer.name,
                                        "error": f"No SVG file found for layer '{layer.name}' (tried: layers/{layer.name}.svg, multipen.svg, src.svg)",
                                    }
                                )
                                continue

                            if not quiet:
                                if verbose:
                                    show_status(
                                        f"  Plotting {job_id} - {layer.name}", "info"
                                    )
                                elif console:
                                    console.print(f"    • {job_id} - {layer.name}")

                            # Plot the layer
                            result = plotter.plot_with_axidraw_layers(layer_svg)

                            if result["success"]:
                                successful_plots.append(
                                    {
                                        "job_id": job_id,
                                        "layer": layer.name,
                                        "time": result.get("time_elapsed", 0),
                                        "distance": result.get("distance_pendown", 0),
                                    }
                                )
                                total_time += result.get("time_elapsed", 0)
                                total_distance += result.get("distance_pendown", 0)

                                if verbose:
                                    show_status(
                                        f"    ✓ {job_id} - {layer.name} ({result.get('time_elapsed', 0):.1f}s)",
                                        "success",
                                    )
                            else:
                                failed_plots.append(
                                    {
                                        "job_id": job_id,
                                        "layer": layer.name,
                                        "error": result.get("error", "Unknown error"),
                                    }
                                )
                                if verbose:
                                    show_status(
                                        f"    ✗ {job_id} - {layer.name}: {result.get('error', 'Unknown error')}",
                                        "error",
                                    )

                        except Exception as layer_error:
                            failed_plots.append(
                                {
                                    "job_id": job_id,
                                    "layer": layer.name,
                                    "error": str(layer_error),
                                }
                            )
                            if verbose:
                                show_status(
                                    f"    ✗ {job_id} - {layer.name}: {layer_error}",
                                    "error",
                                )

                    step_num += 1

            else:
                # Traditional batch plotting - plot each job individually
                if not quiet:
                    if console:
                        console.print(
                            f"\n📋 Starting traditional batch plotting ({len(jobs)} jobs)"
                        )
                    else:
                        print(
                            f"\nStarting traditional batch plotting ({len(jobs)} jobs)"
                        )

                for job in jobs:
                    job_id = job["id"]
                    job_dir = job["path"]

                    try:
                        # Find optimized SVG file
                        optimized_svg = job_dir / "multipen.svg"
                        if not optimized_svg.exists():
                            optimized_svg = job_dir / "src.svg"

                        if not optimized_svg.exists():
                            failed_plots.append(
                                {
                                    "job_id": job_id,
                                    "error": f"No SVG file found for job '{job_id}' (tried: multipen.svg, src.svg)",
                                }
                            )
                            continue

                        if not quiet:
                            if verbose:
                                show_status(f"Plotting {job_id}", "info")
                            elif console:
                                console.print(f"  • {job_id}")

                        # Plot the job
                        result = plotter.plot_with_axidraw_layers(optimized_svg)

                        if result["success"]:
                            successful_plots.append(
                                {
                                    "job_id": job_id,
                                    "time": result.get("time_elapsed", 0),
                                    "distance": result.get("distance_pendown", 0),
                                }
                            )
                            total_time += result.get("time_elapsed", 0)
                            total_distance += result.get("distance_pendown", 0)

                            if verbose:
                                show_status(
                                    f"  ✓ {job_id} ({result.get('time_elapsed', 0):.1f}s)",
                                    "success",
                                )
                        else:
                            failed_plots.append(
                                {
                                    "job_id": job_id,
                                    "error": result.get("error", "Unknown error"),
                                }
                            )
                            if verbose:
                                show_status(
                                    f"  ✗ {job_id}: {result.get('error', 'Unknown error')}",
                                    "error",
                                )

                    except Exception as job_error:
                        failed_plots.append({"job_id": job_id, "error": str(job_error)})
                        if verbose:
                            show_status(f"  ✗ {job_id}: {job_error}", "error")

            # Report results
            if not quiet:
                if console:
                    console.print("\n📊 Batch Plotting Results:")
                    console.print(f"   ✅ Successful: {len(successful_plots)}")
                    console.print(f"   ❌ Failed: {len(failed_plots)}")
                    console.print(
                        f"   ⏱️  Total time: {total_time:.1f}s ({total_time / 60:.1f} minutes)"
                    )
                    console.print(f"   📏 Total distance: {total_distance:.1f}mm")

                    if preset_obj:
                        console.print(
                            f"   ⚡ Preset: {preset} ({preset_obj.description})"
                        )
                else:
                    print("\nBatch Plotting Results:")
                    print(f"   Successful: {len(successful_plots)}")
                    print(f"   Failed: {len(failed_plots)}")
                    print(
                        f"   Total time: {total_time:.1f}s ({total_time / 60:.1f} minutes)"
                    )
                    print(f"   Total distance: {total_distance:.1f}mm")
                    if preset_obj:
                        print(f"   Preset: {preset} ({preset_obj.description})")

                if failed_plots and verbose:
                    print("\nFailed plots:")
                    for failure in failed_plots:
                        if "layer" in failure:
                            print(
                                f"  ✗ {failure['job_id']} - {failure['layer']}: {failure['error']}"
                            )
                        else:
                            print(f"  ✗ {failure['job_id']}: {failure['error']}")

            # Update job states to COMPLETED for successful plots
            cfg = load_config(None)
            for success in successful_plots:
                try:
                    job_id = success["job_id"]
                    job_dir = Path(cfg.workspace) / "jobs" / job_id
                    job_file = job_dir / "job.json"

                    if job_file.exists():
                        job_data = json.loads(job_file.read_text())
                        job_data["state"] = "COMPLETED"
                        job_data["completed_at"] = datetime.now().isoformat()
                        job_data["plotting_time"] = success.get("time", 0)
                        job_data["plotting_distance"] = success.get("distance", 0)

                        job_file.write_text(json.dumps(job_data, indent=2))
                except Exception:
                    pass  # Don't fail the whole operation if state update fails

    except Exception as e:
        error_handler.handle(e)
