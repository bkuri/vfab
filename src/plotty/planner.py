from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
from .vpype import run_vpype, load_preset
from .estimation import features, estimate_seconds
from .progress import layer_progress

try:
    from .drivers import create_manager
except ImportError:
    create_manager = None

from .multipen import (
    detect_svg_layers,
    extract_layers_to_files,
    create_pen_mapping_prompt,
    save_pen_mapping,
    create_multipen_svg,
)


def plan_layers(
    src_svg: Path,
    preset: str,
    presets_file: str,
    pen_map: Optional[dict[str, str]],
    out_dir: Path,
    available_pens: Optional[List[Dict]] = None,
    interactive: bool = False,
    paper_size: str = "A4",
):
    """Plan layers for multi-pen plotting.

    Args:
        src_svg: Source SVG file
        preset: vpype preset name
        presets_file: Path to vpype presets
        pen_map: Layer to pen mapping (optional, will prompt if None)
        out_dir: Output directory
        available_pens: List of available pens from database
        interactive: Whether to prompt for pen mapping

    Returns:
        Dictionary with planning results
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # Detect layers in SVG
    layers = detect_svg_layers(src_svg)

    # Handle pen mapping
    if not pen_map and interactive and available_pens:
        pen_map = create_pen_mapping_prompt(layers, available_pens)
    elif not pen_map:
        # Default to first pen for all layers
        pen_map = {layer.name: "0.3mm black" for layer in layers}

    # Save pen mapping
    save_pen_mapping(out_dir, pen_map)

    # Extract layers to separate files
    layer_files = extract_layers_to_files(src_svg, out_dir / "layers")

    # Process each layer
    processed_layers = []
    total_pre_time = 0
    total_post_time = 0

    with layer_progress.process_layers(len(layer_files), "Processing") as update_layer:
        for i, layer in enumerate(layer_files):
            update_layer(i, f"Starting {layer.name}")

            layer_svg = out_dir / "layers" / f"layer_{i:02d}.svg"
            if not layer_svg.exists():
                update_layer(i, f"Skipping {layer.name} (file not found)")
                continue

            # Get features and estimates for this layer
            update_layer(i, f"Analyzing {layer.name}")
            preF = features(layer_svg)
            pre_est = estimate_seconds(preF, {})
            total_pre_time += pre_est

            # Apply vpype optimization to layer
            optimized_layer = out_dir / "layers" / f"layer_{i:02d}_optimized.svg"

            # Get paper dimensions for vpype
            from .paper import PaperSize

            width_mm, height_mm = PaperSize.get_dimensions(paper_size) or (
                210.0,
                297.0,
            )  # Default to A4

            update_layer(i, f"Optimizing {layer.name}")
            pipe = load_preset(preset, presets_file).format(
                src=str(layer_svg),
                dst=str(optimized_layer),
                pagesize=paper_size.lower(),
                width_mm=width_mm,
                height_mm=height_mm,
            )
            run_vpype(pipe, layer_svg, optimized_layer)

            update_layer(i, f"Finalizing {layer.name}")
            postF = features(optimized_layer)
            post_est = estimate_seconds(postF, {})
            total_post_time += post_est

            # Get pen info for this layer
            pen_name = pen_map.get(
                layer.name, list(pen_map.values())[0] if pen_map else "0.3mm black"
            )
            pen_info = next(
                (p for p in (available_pens or []) if p["name"] == pen_name), {}
            )

            processed_layers.append(
                {
                    "name": layer.name,
                    "pen": pen_name,
                    "pen_info": pen_info,
                    "svg": str(optimized_layer),
                    "original_svg": str(layer_svg),
                    "order_index": layer.order_index,
                    "element_count": len(layer.elements),
                    "estimates": {
                        "pre_s": round(pre_est, 1),
                        "post_s": round(post_est, 1),
                    },
                    "features": {"pre": preF.__dict__, "post": postF.__dict__},
                }
            )

    # Create combined multi-pen SVG with AxiDraw layer control
    multipen_svg = out_dir / "multipen.svg"
    create_multipen_svg(
        src_svg, layer_files, pen_map, multipen_svg, available_pens or []
    )

    return {
        "layers": processed_layers,
        "layer_count": len(processed_layers),
        "pen_map": pen_map,
        "estimates": {
            "pre_s": round(total_pre_time, 1),
            "post_s": round(total_post_time, 1),
            "time_saved_percent": round(
                (
                    ((total_pre_time - total_post_time) / total_pre_time * 100)
                    if total_pre_time > 0
                    else 0
                ),
                1,
            ),
        },
        "multipen_svg": str(multipen_svg),
        "layer_files": [
            str(out_dir / "layers" / f"layer_{i:02d}.svg")
            for i in range(len(layer_files))
        ],
    }


def plan_axidraw_layers(
    src_svg: Path,
    preset: str,
    presets_file: str,
    pen_map: dict[str, str],
    out_dir: Path,
    port: str | None = None,
    model: int = 1,
    available_pens: Optional[List[Dict]] = None,
    interactive: bool = False,
    **axidraw_options,
) -> dict:
    """Plan layers specifically for AxiDraw plotting with multi-pen support.

    Args:
        src_svg: Source SVG file
        preset: vpype preset name
        presets_file: Path to vpype presets
        pen_map: Layer to pen mapping
        out_dir: Output directory
        port: AxiDraw port (auto-detect if None)
        model: AxiDraw model number
        available_pens: List of available pens from database
        interactive: Whether to prompt for pen mapping
        **axidraw_options: Additional AxiDraw options

    Returns:
        Dictionary with AxiDraw-specific planning results
    """
    if create_manager is None:
        raise ImportError(
            "AxiDraw support not available. Install with: uv pip install -e '.[axidraw]'"
        )

    out_dir.mkdir(parents=True, exist_ok=True)

    # Use the enhanced multi-pen planning
    plan_result = plan_layers(
        src_svg, preset, presets_file, pen_map, out_dir, available_pens, interactive
    )

    # Create AxiDraw manager for time estimation
    manager = create_manager(port=port, model=model)

    # Get AxiDraw estimates for each layer
    total_axidraw_est = 0
    total_distance = 0

    for layer in plan_result["layers"]:
        layer_svg = layer["svg"]
        result = manager.plot_file(layer_svg, preview_only=True, **axidraw_options)

        if result["success"]:
            layer["axidraw_est"] = round(result["time_estimate"], 1)
            layer["distance_mm"] = result["distance_pendown"]
            total_axidraw_est += result["time_estimate"]
            total_distance += result["distance_pendown"]
        else:
            layer["axidraw_est"] = layer["estimates"]["post_s"]  # Fallback
            layer["distance_mm"] = 0

    return {
        **plan_result,
        "estimates": {
            **plan_result["estimates"],
            "axidraw_s": round(total_axidraw_est, 1),
        },
        "axidraw": {
            "total_distance_mm": total_distance,
            "port": port,
            "model": model,
            "options": axidraw_options,
        },
    }
