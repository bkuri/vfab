"""
Plotting commands for ploTTY CLI.
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
    port: Optional[str] = typer.Option(None, "--port", help="Device port"),
    model: int = typer.Option(1, "--model", help="Device model"),
):
    """Plot a job."""
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
                f"Plotting job {job_id} with preset '{preset}': {preset_obj.description}",
                "info",
            )
        else:
            show_status(f"Plotting job {job_id} with default settings", "info")

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
                f"Job {job_id} must be planned first. Run: plotty job plan {job_id}",
                "warning",
            )
            return

        # Find the optimized SVG file
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
                f"Job {job_id} must be planned first. Run: plotty job plan {job_id}",
                "warning",
            )
            return

        # Find the optimized SVG file
        optimized_svg = job_dir / "multipen.svg"
        if not optimized_svg.exists():
            optimized_svg = job_dir / "src.svg"

        if not optimized_svg.exists():
            raise typer.BadParameter(f"No SVG file found for job {job_id}")

        # Use the MultiPenPlotter for actual plotting
        from ..plotting import MultiPenPlotter

        # Create plotter
        plotter = MultiPenPlotter(port=port, model=model)

        # Apply preset settings to the device manager if preset provided
        if preset_obj:
            preset_settings = preset_obj.to_vpype_args()
            # Convert preset settings to device manager parameters
            device_config = {
                "speed_pendown": int(preset_settings.get("speed", 25)),
                "speed_penup": int(preset_settings.get("speed", 75)),
                "pen_pos_up": int(preset_settings.get("pen_height", 60)),
                "pen_pos_down": int(preset_settings.get("pen_height", 40)),
            }
            # Apply settings to the manager
            for key, value in device_config.items():
                if hasattr(plotter.manager, key):
                    setattr(plotter.manager, key, value)

        # Execute plotting using the AxiDraw layer control method
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


@plot_app.command()
def interactive(port: Optional[str] = None, model: int = 1, units: str = "inches"):
    """Start interactive plotting session."""
    try:
        from ..plotting import MultiPenPlotter
        from ..config import load_config
        from .core import get_available_job_ids

        # Initialize plotter
        plotter = MultiPenPlotter(port=port, model=model, interactive=True)

        if console:
            console.print("🎯 ploTTY Interactive Plotting Session")
            console.print("=" * 50)
            console.print(f"📡 Device: {'auto' if port is None else port}")
            console.print(f"🖊️  Model: {model}")
            console.print(f"📏 Units: {units}")
            console.print("")

        # Main interactive loop
        while True:
            if console:
                console.print("📋 Available Commands:")
                console.print("  • list-jobs     - List available jobs")
                console.print("  • plot <job>   - Plot a specific job")
                console.print("  • plot-ready   - Plot all READY jobs")
                console.print("  • presets      - Show available presets")
                console.print("  • status       - Show device status")
                console.print("  • quit/exit    - Exit interactive mode")
                console.print("")

            try:
                command = input("ploTTY> ").strip().lower()

                if command in ["quit", "exit", "q"]:
                    if console:
                        console.print("👋 Goodbye!")
                    break

                elif command == "list-jobs" or command == "ls":
                    jobs = get_available_job_ids()
                    if console and Table:
                        table = Table(title="Available Jobs")
                        table.add_column("Job ID", style="cyan")
                        table.add_column("State", style="white")

                        for job_id in jobs:
                            # Get job state
                            cfg = load_config(None)
                            job_file = (
                                Path(cfg.workspace) / "jobs" / job_id / "job.json"
                            )
                            if job_file.exists():
                                job_data = json.loads(job_file.read_text())
                                state = job_data.get("state", "UNKNOWN")
                            else:
                                state = "NO_FILE"

                            table.add_row(job_id, state)

                        console.print(table)
                    else:
                        jobs = get_available_job_ids()
                        print("Available Jobs:")
                        for job_id in jobs:
                            print(f"  {job_id}")

                elif command.startswith("plot "):
                    job_id = command[5:].strip()
                    if not job_id:
                        if console:
                            console.print("❌ Please specify a job ID", style="red")
                        continue

                    # Plot specific job
                    cfg = load_config(None)
                    job_dir = Path(cfg.workspace) / "jobs" / job_id

                    if not job_dir.exists():
                        if console:
                            console.print(f"❌ Job {job_id} not found", style="red")
                        continue

                    # Check if job is ready
                    job_file = job_dir / "job.json"
                    if job_file.exists():
                        job_data = json.loads(job_file.read_text())
                        if job_data.get("state") not in ["OPTIMIZED", "READY"]:
                            if console:
                                console.print(
                                    f"⚠️  Job {job_id} must be planned first",
                                    style="yellow",
                                )
                            continue

                    # Find SVG file
                    svg_file = job_dir / "multipen.svg"
                    if not svg_file.exists():
                        svg_file = job_dir / "src.svg"

                    if not svg_file.exists():
                        if console:
                            console.print(
                                f"❌ No SVG file found for job {job_id}", style="red"
                            )
                        continue

                    # Plot the job
                    if console:
                        console.print(f"🖊️  Plotting job {job_id}...")

                    result = plotter.plot_with_axidraw_layers(svg_file)

                    if result["success"]:
                        if console:
                            console.print(
                                f"✅ Job {job_id} plotted successfully!", style="green"
                            )
                            console.print(f"   Time: {result['time_elapsed']:.1f}s")
                            console.print(
                                f"   Distance: {result['distance_pendown']:.1f}mm"
                            )
                    else:
                        if console:
                            console.print(
                                f"❌ Plotting failed: {result.get('error', 'Unknown error')}",
                                style="red",
                            )

                elif command == "plot-ready":
                    # Plot all ready jobs
                    cfg = load_config(None)
                    jobs_dir = Path(cfg.workspace) / "jobs"
                    ready_jobs = []

                    for job_dir in jobs_dir.iterdir():
                        if not job_dir.is_dir():
                            continue

                        job_file = job_dir / "job.json"
                        if job_file.exists():
                            job_data = json.loads(job_file.read_text())
                            if job_data.get("state") == "READY":
                                ready_jobs.append(job_dir.name)

                    if not ready_jobs:
                        if console:
                            console.print("📋 No READY jobs found", style="yellow")
                        continue

                    if console:
                        console.print(f"📋 Found {len(ready_jobs)} READY jobs")

                    for job_id in ready_jobs:
                        job_dir = jobs_dir / job_id
                        svg_file = job_dir / "multipen.svg"
                        if not svg_file.exists():
                            svg_file = job_dir / "src.svg"

                        if svg_file.exists():
                            if console:
                                console.print(f"🖊️  Plotting {job_id}...")

                            result = plotter.plot_with_axidraw_layers(svg_file)

                            if result["success"]:
                                if console:
                                    console.print(
                                        f"✅ {job_id} completed", style="green"
                                    )
                            else:
                                if console:
                                    console.print(
                                        f"❌ {job_id} failed: {result.get('error')}",
                                        style="red",
                                    )

                elif command == "presets":
                    # Show presets
                    import sys
                    import os

                    sys.path.insert(
                        0, os.path.join(os.path.dirname(__file__), "..", "..")
                    )
                    from plotty.presets import list_presets

                    all_presets = list_presets()

                    if console and Table:
                        table = Table(title="Available Presets")
                        table.add_column("Name", style="cyan")
                        table.add_column("Description", style="white")
                        table.add_column("Speed", style="white", justify="right")

                        for preset in all_presets.values():
                            table.add_row(
                                preset.name, preset.description, f"{preset.speed:.0f}%"
                            )
                        console.print(table)
                    else:
                        print("Available Presets:")
                        for preset in all_presets.values():
                            print(f"  {preset.name}: {preset.description}")

                elif command == "status":
                    # Show device status
                    if console:
                        console.print("📡 Device Status:")
                        console.print(f"   Port: {'auto' if port is None else port}")
                        console.print(f"   Model: {model}")
                        console.print("   Interactive: ✅")

                        # Test device connection
                        try:
                            # Try to get device info
                            if hasattr(plotter.manager, "connected"):
                                status = (
                                    "Connected"
                                    if plotter.manager.connected
                                    else "Disconnected"
                                )
                                console.print(f"   Connection: {status}")
                            else:
                                console.print("   Connection: Unknown")
                        except Exception:
                            console.print("   Connection: Check failed")

                elif command == "help" or command == "?":
                    if console:
                        console.print("📋 ploTTY Interactive Commands:")
                        console.print("  list-jobs     - List available jobs")
                        console.print("  plot <job>   - Plot a specific job")
                        console.print("  plot-ready   - Plot all READY jobs")
                        console.print("  presets      - Show available presets")
                        console.print("  status       - Show device status")
                        console.print("  help/?       - Show this help")
                        console.print("  quit/exit    - Exit interactive mode")

                else:
                    if command:
                        if console:
                            console.print(f"❌ Unknown command: {command}", style="red")
                        else:
                            print(f"Unknown command: {command}")

            except KeyboardInterrupt:
                if console:
                    console.print("\n👋 Goodbye!")
                break
            except EOFError:
                if console:
                    console.print("\n👋 Goodbye!")
                break
            except Exception as cmd_error:
                if console:
                    console.print(f"❌ Error: {cmd_error}", style="red")
                else:
                    print(f"Error: {cmd_error}")

    except Exception as e:
        error_handler.handle(e)


@plot_app.command()
def presets():
    """List available plot presets."""
    try:
        import sys
        import os

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
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


@plot_app.command()
def pen_test(port: Optional[str] = None, model: int = 1, cycles: int = 3):
    """Test pen operation."""
    try:
        from ..plotting import MultiPenPlotter

        # Initialize plotter
        plotter = MultiPenPlotter(port=port, model=model, interactive=False)

        if console:
            console.print("🖊️  Pen Test")
            console.print("=" * 30)
            console.print(f"📡 Device: {'auto' if port is None else port}")
            console.print(f"🔄 Cycles: {cycles}")
            console.print("")

        # Test basic pen movements
        test_results = {
            "success": True,
            "cycles_completed": 0,
            "errors": [],
            "total_time": 0,
        }

        import time

        start_time = time.time()

        for cycle in range(cycles):
            try:
                if console:
                    console.print(f"🔄 Cycle {cycle + 1}/{cycles}")

                # Test pen up/down
                if console:
                    console.print("  📐 Testing pen up/down movement...")

                # Use the device manager to test pen movements
                if hasattr(plotter.manager, "pen_up"):
                    plotter.manager.pen_up()
                    time.sleep(0.5)

                if hasattr(plotter.manager, "pen_down"):
                    plotter.manager.pen_down()
                    time.sleep(0.5)

                # Test small movement pattern
                if console:
                    console.print("  📏 Testing movement pattern...")

                # Create a simple test pattern
                test_moves = [
                    (0, 0),  # Start position
                    (100, 0),  # Move right
                    (100, 100),  # Move up
                    (0, 100),  # Move left
                    (0, 0),  # Return to start
                ]

                for i, (x, y) in enumerate(test_moves):
                    if hasattr(plotter.manager, "move_to"):
                        plotter.manager.move_to(x, y)
                        time.sleep(0.2)

                    if console and i > 0:  # Skip first position
                        console.print(f"    📍 Move to ({x}, {y})")

                test_results["cycles_completed"] += 1

                if console:
                    console.print(f"  ✅ Cycle {cycle + 1} completed", style="green")

                # Small delay between cycles
                if cycle < cycles - 1:
                    time.sleep(1)

            except Exception as cycle_error:
                error_msg = f"Cycle {cycle + 1} failed: {str(cycle_error)}"
                test_results["errors"].append(error_msg)
                test_results["success"] = False

                if console:
                    console.print(f"  ❌ {error_msg}", style="red")

        test_results["total_time"] = time.time() - start_time

        # Print summary
        if console:
            console.print("")
            console.print("📊 Test Results:")
            console.print(
                f"   Cycles completed: {test_results['cycles_completed']}/{cycles}"
            )
            console.print(f"   Total time: {test_results['total_time']:.1f}s")

            if test_results["errors"]:
                console.print(f"   Errors: {len(test_results['errors'])}")
                for error in test_results["errors"]:
                    console.print(f"     - {error}", style="red")

            if test_results["success"]:
                console.print("   Overall result: ✅ PASS", style="green")
            else:
                console.print("   Overall result: ❌ FAIL", style="red")
        else:
            print("Pen Test Results:")
            print(f"  Cycles: {test_results['cycles_completed']}/{cycles}")
            print(f"  Time: {test_results['total_time']:.1f}s")
            print(f"  Result: {'PASS' if test_results['success'] else 'FAIL'}")

            if test_results["errors"]:
                print("  Errors:")
                for error in test_results["errors"]:
                    print(f"    - {error}")

    except Exception as e:
        error_handler.handle(e)
