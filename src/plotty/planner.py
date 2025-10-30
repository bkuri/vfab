from **future** import annotations
from pathlib import Path
from .vpype_runner import run_vpype, load_preset
from .estimation import features, estimate_seconds

def plan_layers(src_svg: Path, preset: str, presets_file: str, pen_map: dict[str, str], out_dir: Path):
out_dir.mkdir(parents=True, exist_ok=True)
preF = features(src_svg)
pre_est = estimate_seconds(preF, {})
dst = out_dir / "optimized.svg"
pipe = load_preset(preset, presets_file).format(src=str(src_svg), dst=str(dst))
run_vpype(pipe, src_svg, dst)
postF = features(dst)
post_est = estimate_seconds(postF, {})
return {
"layers": [{"name": "Layer 1", "pen": list(pen_map.values())[0] if pen_map else None, "svg": str(dst)}],
"estimates": {"pre_s": round(pre_est,1), "post_s": round(post_est,1)},
"features": {"pre": preF.**dict**, "post": postF.**dict**},
"optimized_svg": str(dst)
}
