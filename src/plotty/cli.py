import typer
import uuid
import json
import time
from pathlib import Path
from typing import Optional, List
from .config import load_config
from .planner import plan_layers
from .capture import start_ip, stop

# Import status commands
from .cli_status import status_app

try:
    from .drivers import create_manager, is_axidraw_available
except ImportError:
    create_manager = None

    def is_axidraw_available():
        return False


try:
    from .crash_recovery import get_crash_recovery, recover_all_jobs
except ImportError:
    get_crash_recovery = None
    recover_all_jobs = None

app = typer.Typer(no_args_is_help=False, invoke_without_command=True)

# Add status commands as a sub-group
app.add_typer(status_app, name="status", help="Status and monitoring commands")


def get_available_job_ids() -> List[str]:
    """Get list of available job IDs for autocomplete."""
    try:
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"
        job_ids = []

        if jobs_dir.exists():
            for job_dir in jobs_dir.iterdir():
                if job_dir.is_dir():
                    job_file = job_dir / "job.json"
                    if job_file.exists():
                        job_ids.append(job_dir.name)

        return sorted(job_ids, reverse=True)  # Most recent first
    except Exception:
        return []


def complete_job_id(ctx: typer.Context, args: List[str], incomplete: str) -> List[str]:
    """Autocomplete function for job IDs."""
    available_ids = get_available_job_ids()
    return [job_id for job_id in available_ids if job_id.startswith(incomplete)]


@app.callback()
def main(ctx: typer.Context):
    """ploTTY - FSM plotter manager with smart multipen detection."""
    if ctx.invoked_subcommand is None:
        # Show interactive dashboard
        from .dashboard import show_dashboard

        show_dashboard()


@app.command()
def add(src: str, name: str = "", paper: str = "A3"):
    cfg = load_config(None)
    # Generate shorter 6-character job ID for better usability
    job_id = uuid.uuid4().hex[:6]
    jdir = Path(cfg.workspace) / "jobs" / job_id
    jdir.mkdir(parents=True, exist_ok=True)
    (jdir / "src.svg").write_bytes(Path(src).read_bytes())
    (jdir / "job.json").write_text(
        json.dumps(
            {
                "id": job_id,
                "name": name or Path(src).stem,
                "paper": paper,
                "state": "QUEUED",
            }
        )
    )
    print(job_id)


@app.command()
def plan(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to plan"
    ),
    pen: str = "0.3mm black",
    interactive: bool = False,
):
    """Plan a job with smart multi-pen detection."""
    cfg = load_config(None)
    jdir = Path(cfg.workspace) / "jobs" / job_id

    # Load available pens from database
    available_pens = []
    try:
        from .db import get_session
        from .models import Pen

        with get_session() as session:
            pens = session.query(Pen).all()
            available_pens = [
                {
                    "id": pen.id,
                    "name": pen.name,
                    "width_mm": pen.width_mm,
                    "speed_cap": pen.speed_cap,
                    "pressure": pen.pressure,
                    "passes": pen.passes,
                    "color_hex": pen.color_hex,
                }
                for pen in pens
            ]
    except Exception:
        pass

    # Import multipen functions for layer detection
    from .multipen import detect_svg_layers, display_layer_overview

    # Detect layers and show overview
    svg_path = jdir / "src.svg"
    layers = detect_svg_layers(svg_path)

    # Show layer overview
    display_layer_overview(layers)

    # Filter out hidden layers for processing
    visible_layers = [layer for layer in layers if layer.visible]
    hidden_count = len(layers) - len(visible_layers)

    if hidden_count > 0:
        print(
            f"\n🚫 Skipping {hidden_count} hidden layer(s) as per AxiDraw layer control"
        )

    # Smart pen mapping: use multipen if multiple visible layers and pens available
    if len(visible_layers) > 1 and available_pens and interactive:
        # Use multipen workflow
        res = plan_layers(
            svg_path,
            cfg.vpype.preset,
            cfg.vpype.presets_file,
            None,  # Will prompt for pen mapping
            jdir,
            available_pens,
            interactive,
            cfg.paper.default_size,
        )
    else:
        # Use single pen workflow
        pen_map = {"Layer 1": pen}  # Default fallback
        if len(visible_layers) == 1:
            pen_map = {visible_layers[0].name: pen}
        res = plan_layers(
            svg_path,
            cfg.vpype.preset,
            cfg.vpype.presets_file,
            pen_map,
            jdir,
            available_pens,
            interactive,
            cfg.paper.default_size,
        )
    (jdir / "plan.json").write_text(json.dumps(res, indent=2))

    print(f"📊 Planning completed for {res['layer_count']} layers")
    print(
        f"⏱️  Time estimates: {res['estimates']['pre_s']}s → "
        f"{res['estimates']['post_s']}s"
    )
    if res["estimates"]["time_saved_percent"] > 0:
        print(f"💾 Time saved: {res['estimates']['time_saved_percent']}%")
    print(f"🖊️  Pen mapping: {res['pen_map']}")
    print(f"📁 Multi-pen SVG: {res['multipen_svg']}")


@app.command()
def record_test(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to record"
    ),
    seconds: int = 5,
):
    cfg = load_config(None)
    jdir = Path(cfg.workspace) / "jobs" / job_id
    out = jdir / "sample.mp4"
    if cfg.camera.mode != "ip":
        raise SystemExit("v1: camera.mode must be 'ip' for record_test")
    procs = start_ip(cfg.camera.url, str(out))
    try:
        time.sleep(seconds)
    finally:
        stop(procs)
        print(out)


@app.command()
def plot(
    job_id: str,
    port: Optional[str] = None,
    model: int = 1,
    preview: bool = False,
    multipen: bool = True,
    interactive: bool = True,
):
    """Plot a job using AxiDraw."""
    if not is_axidraw_available():
        raise typer.BadParameter(
            "AxiDraw support not available. Install with: "
            "uv pip install -e '.[axidraw]'"
        )
    """Plot a job using AxiDraw with multi-pen support."""
    cfg = load_config(None)
    jdir = Path(cfg.workspace) / "jobs" / job_id

    # Check for plan file
    plan_file = jdir / "plan.json"
    if not plan_file.exists():
        raise typer.BadParameter(f"Job {job_id} not planned. Run 'plan' command first.")

    plan_data = json.loads(plan_file.read_text())

    if multipen and plan_data.get("layer_count", 0) > 1:
        # Multi-pen plotting
        from .plotting import MultiPenPlotter

        plotter = MultiPenPlotter(port=port, model=model, interactive=interactive)

        if plan_data.get("multipen_svg") and Path(plan_data["multipen_svg"]).exists():
            # Use AxiDraw native layer control
            result = plotter.plot_with_axidraw_layers(Path(plan_data["multipen_svg"]))
        else:
            # Use manual multi-pen plotting
            result = plotter.plot_multipen_job(
                jdir, plan_data["layers"], plan_data["pen_map"]
            )
    else:
        # Single-pen plotting (original behavior)
        svg_file = jdir / "src.svg"
        if not svg_file.exists():
            raise typer.BadParameter(f"Job {job_id} not found")

        manager = create_manager(port=port, model=model)
        result = manager.plot_file(svg_file, preview_only=preview)

    if result["success"]:
        print("✓ Plot completed successfully")
        print(f"  Time: {result['time_elapsed']:.2f}s")
        print(f"  Distance: {result['distance_pendown']:.2f}mm pen-down")
        if preview:
            print("  Preview mode - no physical plotting performed")
    else:
        print(f"✗ Plot failed: {result['error']}")
        raise typer.Exit(1)


@app.command()
def interactive(port: Optional[str] = None, model: int = 1, units: str = "inches"):
    """Enter interactive AxiDraw control mode."""
    if not is_axidraw_available():
        raise typer.BadParameter(
            "AxiDraw support not available. Install with: "
            "uv pip install -e '.[axidraw]'"
        )
    manager = create_manager(port=port, model=model)

    if not manager.connect():
        print("✗ Failed to connect to AxiDraw")
        raise typer.Exit(1)

    try:
        manager.set_units(units)
        print(f"✓ Connected to AxiDraw in {units} units")
        print(f"  Current position: {manager.get_position()}")
        print(f"  Pen is {'up' if manager.get_pen_state() else 'down'}")
        print("  Commands: move, draw, pen-up, pen-down, pos, quit")

        while True:
            try:
                cmd = input("axidraw> ").strip().lower()
                if not cmd:
                    continue
                elif cmd == "quit" or cmd == "q":
                    break
                elif cmd == "pen-up" or cmd == "u":
                    manager.pen_up()
                    print("  Pen raised")
                elif cmd == "pen-down" or cmd == "d":
                    manager.pen_down()
                    print("  Pen lowered")
                elif cmd == "pos" or cmd == "p":
                    pos = manager.get_position()
                    pen_state = "up" if manager.get_pen_state() else "down"
                    print(f"  Position: {pos}, Pen: {pen_state}")
                elif cmd.startswith("move "):
                    try:
                        _, coords = cmd.split(" ", 1)
                        x, y = map(float, coords.split(","))
                        manager.move_to(x, y)
                        print(f"  Moved to ({x}, {y})")
                    except ValueError:
                        print("  Invalid coordinates. Use: move x,y")
                elif cmd.startswith("draw "):
                    try:
                        _, coords = cmd.split(" ", 1)
                        x, y = map(float, coords.split(","))
                        manager.draw_to(x, y)
                        print(f"  Drew to ({x}, {y})")
                    except ValueError:
                        print("  Invalid coordinates. Use: draw x,y")
                else:
                    print("  Available commands:")
                    print("    move x,y     - Move pen-up to position")
                    print("    draw x,y     - Draw line to position")
                    print("    pen-up/u      - Raise pen")
                    print("    pen-down/d    - Lower pen")
                    print("    pos/p         - Show position")
                    print("    quit/q        - Exit")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"  Error: {e}")

    finally:
        manager.disconnect()
        print("✓ Disconnected from AxiDraw")


@app.command()
def pen_test(port: Optional[str] = None, model: int = 1, cycles: int = 3):
    """Test pen up/down movement."""
    if not is_axidraw_available():
        raise typer.BadParameter(
            "AxiDraw support not available. Install with: "
            "uv pip install -e '.[axidraw]'"
        )
    manager = create_manager(port=port, model=model)
    print(f"Testing pen movement ({cycles} cycles)...")

    for i in range(cycles):
        print(f"  Cycle {i + 1}/{cycles}")
        result = manager.pen_up()
        if result["success"]:
            print("    ✓ Pen up")
        else:
            print(f"    ✗ Failed to raise pen: {result['error']}")

        result = manager.pen_down()
        if result["success"]:
            print("    ✓ Pen down")
        else:
            print(f"    ✗ Failed to lower pen: {result['error']}")


@app.command()
def pen_list():
    """List available pens from database."""
    try:
        from .db import get_session
        from .models import Pen
        from rich.console import Console

        console = Console()
        default_pen = "0.3mm black"

        with get_session() as session:
            pens = session.query(Pen).all()

            if not pens:
                print("No pens found in database.")
                print("Add pens with: pen-add <name> [options]")
                return

            print("🖊️  Available pens:")
            for pen in pens:
                # Highlight default pen in green
                if pen.name == default_pen:
                    console.print(f"  {pen.id}: [green]{pen.name}[/green] (default)")
                else:
                    console.print(f"  {pen.id}: {pen.name}")

                if pen.width_mm:
                    print(f"    Width: {pen.width_mm}mm")
                if pen.speed_cap:
                    print(f"    Speed cap: {pen.speed_cap}")
                if pen.pressure:
                    print(f"    Pressure: {pen.pressure}")
                if pen.color_hex:
                    print(f"    Color: #{pen.color_hex}")

    except Exception as e:
        print(f"✗ Failed to load pens: {e}")


@app.command()
def pen_add(
    name: str,
    width_mm: Optional[float] = None,
    speed_cap: Optional[int] = None,
    pressure: Optional[int] = None,
    passes: int = 1,
    color_hex: Optional[str] = None,
):
    """Add a new pen to the database."""
    try:
        from .db import get_session
        from .models import Pen

        with get_session() as session:
            # Check if pen already exists
            existing = session.query(Pen).filter(Pen.name == name).first()
            if existing:
                print(f"✗ Pen '{name}' already exists (ID: {existing.id})")
                raise typer.Exit(1)

            # Create new pen
            pen = Pen(
                name=name,
                width_mm=width_mm,
                speed_cap=speed_cap,
                pressure=pressure,
                passes=passes,
                color_hex=color_hex,
            )
            session.add(pen)
            session.commit()

            # Get the ID before session closes
            pen_id = pen.id

        print(f"✓ Added pen '{name}' (ID: {pen_id})")

    except Exception as e:
        print(f"✗ Failed to add pen: {e}")
        raise typer.Exit(1)


@app.command()
def pen_remove(name: str):
    """Remove a pen from database."""
    try:
        from .db import get_session
        from .models import Pen

        with get_session() as session:
            pen = session.query(Pen).filter(Pen.name == name).first()
            if not pen:
                print(f"✗ Pen '{name}' not found")
                raise typer.Exit(1)

            session.delete(pen)
            session.commit()

        print(f"✓ Removed pen '{name}'")

    except Exception as e:
        print(f"✗ Failed to remove pen: {e}")
        raise typer.Exit(1)


@app.command()
def report(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to generate report for"
    ),
    open_browser: bool = False,
):
    """Generate and view job report."""
    cfg = load_config(None)
    jdir = Path(cfg.workspace) / "jobs" / job_id

    if not jdir.exists():
        raise typer.BadParameter(f"Job {job_id} not found")

    try:
        from .reporting import JobReporter

        reporter = JobReporter(jdir)
        report_path = reporter.generate_report()

        print(f"✓ Report generated: {report_path}")

        # Show summary
        summary = reporter.get_metrics_summary()
        print("\n📊 Job Summary:")
        print(f"   Layers: {summary.get('layer_count', 0)}")
        print(f"   Elements: {summary.get('total_elements', 0):,}")

        if summary.get("has_results"):
            print(f"   Plotted: {summary.get('layers_plotted', 0)} layers")
            print(f"   Time: {summary.get('total_time', 0):.1f}s")
            print(f"   Distance: {summary.get('total_distance', 0):.1f}mm")
            print(f"   Pen swaps: {summary.get('pen_swaps', 0)}")

        if open_browser:
            import webbrowser

            webbrowser.open(f"file://{report_path}")
            print("🌐 Opened report in browser")

    except Exception as e:
        print(f"✗ Failed to generate report: {e}")
        raise typer.Exit(1)


@app.command()
def paper_list():
    """List available paper sizes."""
    try:
        from .paper import PaperSize
        from .db import get_session
        from .config import load_config
        from rich.console import Console

        console = Console()
        cfg = load_config(None)
        default_paper = cfg.paper.default_size

        print("📄 Available Paper Sizes:")
        print("\nStandard Sizes:")
        for size in PaperSize:
            name, width_mm, height_mm = size.value
            # Highlight default paper in green
            if name == default_paper:
                console.print(
                    f"  {name:12} {width_mm:6.1f} × {height_mm:6.1f}mm "
                    "[green](default)[/green]"
                )
            else:
                print(f"  {name:12} {width_mm:6.1f} × {height_mm:6.1f}mm")

        # Show custom papers from database
        try:
            with get_session() as session:
                from .models import Paper

                custom_papers = session.query(Paper).all()
                if custom_papers:
                    print("\nCustom Papers:")
                    for paper in custom_papers:
                        # Highlight default paper in green
                        if paper.name == default_paper:
                            console.print(
                                f"  {paper.name:12} {paper.width_mm:6.1f} × "
                                f"{paper.height_mm:6.1f}mm "
                                f"(margin: {paper.margin_mm}mm, {paper.orientation}) "
                                "[green](default)[/green]"
                            )
                        else:
                            print(
                                f"  {paper.name:12} {paper.width_mm:6.1f} × "
                                f"{paper.height_mm:6.1f}mm "
                                f"(margin: {paper.margin_mm}mm, {paper.orientation})"
                            )
        except Exception:
            pass

    except Exception as e:
        print(f"✗ Failed to list papers: {e}")


@app.command()
def paper_add(
    name: str,
    width_mm: float,
    height_mm: float,
    margin_mm: float = 10.0,
    orientation: str = "portrait",
):
    """Add a custom paper size to database."""
    try:
        from .db import get_session
        from .models import Paper

        if orientation not in ["portrait", "landscape"]:
            raise typer.BadParameter("Orientation must be 'portrait' or 'landscape'")

        with get_session() as session:
            # Check if paper already exists
            existing = session.query(Paper).filter(Paper.name == name).first()
            if existing:
                print(f"✗ Paper '{name}' already exists")
                raise typer.Exit(1)

            # Add new paper
            db_paper = Paper(
                name=name,
                width_mm=width_mm,
                height_mm=height_mm,
                margin_mm=margin_mm,
                orientation=orientation,
            )
            session.add(db_paper)
            session.commit()

        print(f"✓ Added custom paper '{name}' ({width_mm}×{height_mm}mm)")

    except Exception as e:
        print(f"✗ Failed to add paper: {e}")
        raise typer.Exit(1)


@app.command()
def paper_remove(name: str):
    """Remove a custom paper from database."""
    try:
        from .db import get_session
        from .models import Paper

        with get_session() as session:
            paper = session.query(Paper).filter(Paper.name == name).first()
            if not paper:
                print(f"✗ Paper '{name}' not found")
                raise typer.Exit(1)

            session.delete(paper)
            session.commit()

        print(f"✓ Removed paper '{name}'")

    except Exception as e:
        print(f"✗ Failed to remove paper: {e}")
        raise typer.Exit(1)


@app.command()
def session_reset():
    """Reset paper session marker (start new session)."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)

        session_file = workspace / ".paper_session"
        if session_file.exists():
            session_file.unlink()
            print("✓ Paper session reset - you can now use fresh paper")
        else:
            print("ℹ️  No active paper session found")

    except Exception as e:
        print(f"✗ Failed to reset session: {e}")
        raise typer.Exit(1)


@app.command()
def recovery_list():
    """List jobs that can be recovered after a crash."""
    if get_crash_recovery is None:
        print("✗ Crash recovery system not available")
        raise typer.Exit(1)

    cfg = load_config(None)
    workspace = Path(cfg.workspace)
    recovery = get_crash_recovery(workspace)

    recoverable = recovery.get_recoverable_jobs()

    if not recoverable:
        print("No recoverable jobs found")
        return

    print(f"Found {len(recoverable)} recoverable job(s):")
    print()

    for job_id in recoverable:
        status = recovery.get_job_status(job_id)
        print(f"  {job_id}: {status['current_state']}")
        if status.get("emergency_shutdown"):
            print("    ⚠ Emergency shutdown detected")
        print(f"    Journal entries: {status['journal_entries']}")
        print()


@app.command()
def recovery_recover(job_id: str):
    """Recover a specific job after a crash."""
    if get_crash_recovery is None:
        print("✗ Crash recovery system not available")
        raise typer.Exit(1)

    cfg = load_config(None)
    workspace = Path(cfg.workspace)
    recovery = get_crash_recovery(workspace)

    fsm = recovery.recover_job(job_id)

    if fsm is None:
        print(f"✗ Could not recover job {job_id}")
        raise typer.Exit(1)

    print(f"✓ Recovered job {job_id}")
    print(f"  Current state: {fsm.current_state.value}")
    print(f"  Transitions: {len(fsm.transitions)}")

    # Register with crash recovery system
    recovery.register_fsm(fsm)


@app.command()
def recovery_recover_all():
    """Recover all recoverable jobs after a crash."""
    if recover_all_jobs is None:
        print("✗ Crash recovery system not available")
        raise typer.Exit(1)

    cfg = load_config(None)
    workspace = Path(cfg.workspace)

    recovered = recover_all_jobs(workspace)

    if not recovered:
        print("No jobs to recover")
        return

    print(f"✓ Recovered {len(recovered)} job(s):")
    for fsm in recovered:
        print(f"  {fsm.job_id}: {fsm.current_state.value}")


@app.command()
def recovery_status(job_id: str):
    """Show detailed recovery status for a job."""
    if get_crash_recovery is None:
        print("✗ Crash recovery system not available")
        raise typer.Exit(1)

    cfg = load_config(None)
    workspace = Path(cfg.workspace)
    recovery = get_crash_recovery(workspace)

    status = recovery.get_job_status(job_id)

    if "error" in status:
        print(f"✗ {status['error']}")
        raise typer.Exit(1)

    print(f"Recovery Status for Job {job_id}")
    print(f"Current state: {status['current_state']}")
    print(f"Recoverable: {'Yes' if status['recoverable'] else 'No'}")
    print(f"Emergency shutdown: {'Yes' if status['emergency_shutdown'] else 'No'}")
    print(f"Journal entries: {status['journal_entries']}")

    if status["last_transition"]:
        trans = status["last_transition"]
        print(f"Last transition: {trans['from_state']} → {trans['to_state']}")
        print(f"  Reason: {trans['reason']}")
        print(f"  Time: {trans['timestamp']}")


@app.command()
def recovery_cleanup(job_id: str, keep_entries: int = 100):
    """Clean up old journal entries for a job."""
    if get_crash_recovery is None:
        print("✗ Crash recovery system not available")
        raise typer.Exit(1)

    cfg = load_config(None)
    workspace = Path(cfg.workspace)
    recovery = get_crash_recovery(workspace)

    success = recovery.cleanup_journal(job_id, keep_entries)

    if success:
        print(
            f"✓ Cleaned journal for job {job_id} (keeping last {keep_entries} entries)"
        )
    else:
        print(f"✗ Failed to clean journal for job {job_id}")


if __name__ == "__main__":
    app()
