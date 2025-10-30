from **future** import annotations
from pathlib import Path
import subprocess, json, shlex, yaml

def run_vpype(pipe: str, src: Path, dst: Path) -> None:
cmd = pipe.replace("{src}", shlex.quote(str(src))).replace("{dst}", shlex.quote(str(dst)))
subprocess.run(f'vpype -v {cmd}', shell=True, check=True)

def stats_json(svg: Path) -> dict:
p = subprocess.run(["vpype", "read", str(svg), "stats", "-o", "json"],
check=True, capture_output=True, text=True)
return json.loads(p.stdout)

def load_preset(name: str, presets_file: str) -> str:
presets = yaml.safe_load(Path(presets_file).read_text()) or {}
rec = presets.get("presets", {}).get(name)
if not rec: raise KeyError(f"vpype preset not found: {name}")
return rec["pipe"]
