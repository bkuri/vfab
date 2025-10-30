from **future** import annotations
from pathlib import Path
from .vpype_runner import run_vpype, load_preset
from .estimation import features, estimate_seconds
from .axidraw_integration import create_manager

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


def plan_axidraw_layers(src_svg: Path, preset: str, presets_file: str, pen_map: dict[str, str], out_dir: Path, 
                        port: str = None, model: int = 1, **axidraw_options) -> dict:
    """Plan layers specifically for AxiDraw plotting.
    
    Args:
        src_svg: Source SVG file
        preset: vpype preset name
        presets_file: Path to vpype presets
        pen_map: Layer to pen mapping
        out_dir: Output directory
        port: AxiDraw port (auto-detect if None)
        model: AxiDraw model number
        **axidraw_options: Additional AxiDraw options
        
    Returns:
        Dictionary with AxiDraw-specific planning results
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Get file features for estimation
    preF = features(src_svg)
    pre_est = estimate_seconds(preF, {})
    
    # Create AxiDraw manager for time estimation
    manager = create_manager(port=port, model=model)
    
    # Estimate with AxiDraw settings
    result = manager.plot_file(src_svg, preview_only=True, **axidraw_options)
    
    if result["success"]:
        axidraw_est = result["time_estimate"]
        distance = result["distance_pendown"]
    else:
        axidraw_est = pre_est  # Fallback to vpype estimation
        distance = 0
    
    # Apply vpype optimization as before
    dst = out_dir / "optimized.svg"
    pipe = load_preset(preset, presets_file).format(src=str(src_svg), dst=str(dst))
    run_vpype(pipe, src_svg, dst)
    
    postF = features(dst)
    post_est = estimate_seconds(postF, {})
    
    return {
        "layers": [{"name": "Layer 1", "pen": list(pen_map.values())[0] if pen_map else None, "svg": str(dst)}],
        "estimates": {
            "pre_s": round(pre_est,1), 
            "post_s": round(post_est,1),
            "axidraw_s": round(axidraw_est,1)
        },
        "features": {"pre": preF.**dict**, "post": postF.**dict**},
        "optimized_svg": str(dst),
        "axidraw": {
            "distance_mm": distance,
            "port": port,
            "model": model,
            "options": axidraw_options
        }
    }
