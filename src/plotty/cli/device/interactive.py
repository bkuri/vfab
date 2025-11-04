"""
Interactive plotting session command for ploTTY CLI.
"""

from __future__ import annotations

from typing import Optional
import json
from pathlib import Path
import typer

from ...utils import error_handler
from ...config import load_config
from ..core import get_available_job_ids

try:
    from rich.console import Console
    from rich.table import Table

    console = Console()
except ImportError:
    console = None
    Table = None


def interactive_session(
    port: Optional[str] = typer.Option(None, "--port", help="Device port"),
    model: int = typer.Option(1, "--model", help="Device model"),
    units: str = typer.Option("inches", "--units", help="Coordinate units"),
):
    """Start interactive plotting session."""
    try:
        from ...plotting import MultiPenPlotter

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

                    # Plot job
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
                        0, os.path.join(os.path.dirname(__file__), "..", "..", "..")
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
