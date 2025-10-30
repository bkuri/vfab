import typer, uuid, json
from pathlib import Path
from .config import load_config
from .planner import plan_layers
from .capture import start_ip, stop
from .axidraw_integration import create_manager
from .checklist import create_checklist
from .fsm import create_fsm

app = typer.Typer(no_args_is_help=True)

@app.command()
def add(src: str, name: str = "", paper: str = "A3"):
cfg = load_config(None)
job_id = uuid.uuid4().hex[:12]
jdir = Path(cfg.workspace) / "jobs" / job_id
jdir.mkdir(parents=True, exist_ok=True)
(jdir / "src.svg").write_bytes(Path(src).read_bytes())
(jdir / "job.json").write_text(json.dumps({"id": job_id, "name": name or Path(src).stem, "paper": paper, "state": "QUEUED"}))
print(job_id)

@app.command()
def plan(job_id: str, pen: str = "0.3mm black"):
cfg = load_config(None)
jdir = Path(cfg.workspace) / "jobs" / job_id
res = plan_layers(jdir / "src.svg", cfg.vpype.preset, cfg.vpype.presets_file, {"Layer 1": pen}, jdir)
(jdir / "plan.json").write_text(json.dumps(res, indent=2))
print(res["estimates"])

@app.command()
def record_test(job_id: str, seconds: int = 5):
cfg = load_config(None)
jdir = Path(cfg.workspace) / "jobs" / job_id
out = jdir / "sample.mp4"
if cfg.camera.mode != "ip":
raise SystemExit("v1: camera.mode must be 'ip' for record_test")
procs = start_ip(cfg.camera.url, str(out))
try:
    import time; time.sleep(seconds)
finally:
    stop(procs)
    print(out)

@app.command()
def plot(job_id: str, port: str = None, model: int = 1, preview: bool = False):
    """Plot a job using AxiDraw."""
    cfg = load_config(None)
    jdir = Path(cfg.workspace) / "jobs" / job_id
    svg_file = jdir / "src.svg"
    
    if not svg_file.exists():
        raise typer.BadParameter(f"Job {job_id} not found")
    
    manager = create_manager(port=port, model=model)
    result = manager.plot_file(svg_file, preview_only=preview)
    
    if result["success"]:
        print(f"✓ Plot completed successfully")
        print(f"  Time: {result['time_elapsed']:.2f}s")
        print(f"  Distance: {result['distance_pendown']:.2f}mm pen-down")
        if preview:
            print(f"  Preview mode - no physical plotting performed")
    else:
        print(f"✗ Plot failed: {result['error']}")
        raise typer.Exit(1)


@app.command()
def interactive(port: str = None, model: int = 1, units: str = "inches"):
    """Enter interactive AxiDraw control mode."""
    manager = create_manager(port=port, model=model)
    
    if not manager.connect():
        print(f"✗ Failed to connect to AxiDraw")
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
def status(port: str = None, model: int = 1):
    """Check AxiDraw status and system information."""
    manager = create_manager(port=port, model=model)
    
    # Try to get system info
    sysinfo = manager.get_sysinfo()
    if sysinfo["success"]:
        print(f"✓ AxiDraw System Information")
        print(f"  Firmware: {sysinfo['fw_version']}")
        print(f"  Software: {sysinfo['version']}")
    else:
        print(f"✗ Could not read system info: {sysinfo['error']}")
    
    # Try to list devices
    devices = manager.list_devices()
    if devices["success"]:
        print(f"✓ Found {len(devices['devices'])} device(s)")
        for i, device in enumerate(devices['devices'], 1):
                print(f"  {i}. {device}")
    else:
        print(f"✗ Could not list devices: {devices['error']}")


@app.command()
def checklist_show(job_id: str):
    """Show checklist status for a job."""
    cfg = load_config(None)
    jdir = Path(cfg.workspace) / "jobs" / job_id
    
    if not jdir.exists():
        raise typer.BadParameter(f"Job {job_id} not found")
    
    checklist = create_checklist(job_id, jdir)
    progress = checklist.get_progress()
    
    print(f"Checklist for Job {job_id}")
    print(f"Progress: {progress['required_completed']}/{progress['required_total']} required items ({progress['progress_percent']:.1f}%)")
    print(f"Status: {'✓ Complete' if progress['is_complete'] else '✗ Incomplete'}")
    print()
    
    for item in checklist.get_all_items():
        status = "✓" if item.completed else "✗"
        required = "(required)" if item.required else "(optional)"
        print(f"  {status} {item.name} {required}")
        print(f"    {item.description}")
        if item.completed and item.notes:
            print(f"    Notes: {item.notes}")
        print()


@app.command()
def checklist_complete(job_id: str, item: str, notes: str = ""):
    """Complete a checklist item."""
    cfg = load_config(None)
    jdir = Path(cfg.workspace) / "jobs" / job_id
    
    if not jdir.exists():
        raise typer.BadParameter(f"Job {job_id} not found")
    
    checklist = create_checklist(job_id, jdir)
    
    if checklist.complete_item(item, notes):
        print(f"✓ Completed checklist item: {item}")
        progress = checklist.get_progress()
        print(f"Progress: {progress['required_completed']}/{progress['required_total']} required items")
    else:
        print(f"✗ Checklist item not found: {item}")


@app.command()
def checklist_reset(job_id: str, item: str):
    """Reset a checklist item to incomplete."""
    cfg = load_config(None)
    jdir = Path(cfg.workspace) / "jobs" / job_id
    
    if not jdir.exists():
        raise typer.BadParameter(f"Job {job_id} not found")
    
    checklist = create_checklist(job_id, jdir)
    
    if checklist.uncomplete_item(item):
        print(f"✓ Reset checklist item: {item}")
    else:
        print(f"✗ Checklist item not found: {item}")


@app.command()
def guards_check(job_id: str):
    """Check guards for a job."""
    cfg = load_config(None)
    jdir = Path(cfg.workspace) / "jobs" / job_id
    
    if not jdir.exists():
        raise typer.BadParameter(f"Job {job_id} not found")
    
    from .guards import create_guard_system
    guard_system = create_guard_system(cfg, Path(cfg.workspace))
    
    # Check guards for ARMED state (most restrictive)
    can_transition, guard_checks = guard_system.can_transition(job_id, "ARMED")
    
    print(f"Guard check for Job {job_id} (targeting ARMED state)")
    print(f"Overall result: {'✓ PASS' if can_transition else '✗ FAIL'}")
    print()
    
    for check in guard_checks:
        status_icon = {
            "pass": "✓",
            "fail": "✗", 
            "soft_fail": "⚠"
        }.get(check.result.value, "?")
        
        print(f"{status_icon} {check.name}: {check.message}")
        if check.details:
            for key, value in check.details.items():
                print(f"    {key}: {value}")
        print()


@app.command()
def pen_test(port: str = None, model: int = 1, cycles: int = 3):
    """Test pen up/down movement."""
    manager = create_manager(port=port, model=model)
    
    print(f"Testing pen movement ({cycles} cycles)...")
    
    for i in range(cycles):
        print(f"  Cycle {i+1}/{cycles}")
        
        # Pen up
        result = manager.pen_up()
        if result["success"]:
                print("    ✓ Pen raised")
        else:
                print(f"    ✗ Failed to raise pen: {result['error']}")
        
        time.sleep(1)
        
        # Pen down
        result = manager.pen_down()
        if result["success"]:
                print("    ✓ Pen lowered")
        else:
                print(f"    ✗ Failed to lower pen: {result['error']}")
        
        time.sleep(1)
    
    print("✓ Pen test completed")


if __name__ == "__main__":
    app()
