import typer, uuid, json
from pathlib import Path
from .config import load_config
from .planner import plan_layers
from .capture import start_ip, stop

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

if **name** == "**main**":
app()
