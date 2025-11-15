from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

from .vpype import stats_json
from .presets import get_preset


@dataclass
class Features:
    l_down: float
    l_travel: float
    n_lifts: int
    n_corners: int


@dataclass
class EstimationResult:
    """Time estimation result with detailed breakdown."""

    total_seconds: float
    total_minutes: float
    pen_down_time: float
    travel_time: float
    lift_time: float
    corner_time: float
    preset_multiplier: float
    features: Features


def features(svg_path: Path) -> Features:
    """Extract features from SVG file for time estimation."""
    s = stats_json(svg_path)
    layer = next(iter(s.get("layers", {}).values()), {})
    return Features(
        l_down=layer.get("length_total_mm", 0.0),
        l_travel=layer.get("length_travel_mm", 0.0),
        n_lifts=layer.get("pen_lifts", 0),
        n_corners=layer.get("corners", 0),
    )


def estimate_seconds(f: Features, coeffs: Dict[str, float]) -> float:
    """Estimate plotting time in seconds using linear coefficients."""
    a = coeffs.get("a", 0.04)  # Pen down time coefficient
    b = coeffs.get("b", 0.06)  # Travel time coefficient
    c = coeffs.get("c", 0.35)  # Lift time coefficient
    d = coeffs.get("d", 0.002)  # Corner time coefficient
    return a * f.l_down + b * f.l_travel + c * f.n_lifts + d * f.n_corners


def estimate_with_preset(
    svg_path: Path, preset_name: Optional[str] = None
) -> EstimationResult:
    """Estimate plotting time with preset-specific adjustments."""

    # Base coefficients for default plotting
    base_coeffs = {
        "a": 0.04,  # 40ms per mm pen down
        "b": 0.06,  # 60ms per mm travel
        "c": 0.35,  # 350ms per lift
        "d": 0.002,  # 2ms per corner
    }

    # Get preset-specific multiplier
    preset_multiplier = 1.0
    if preset_name:
        preset = get_preset(preset_name)
        if preset:
            # Speed affects overall time (inverse relationship)
            preset_multiplier = 100.0 / preset.speed

            # Adjust coefficients based on preset characteristics
            base_coeffs["c"] *= (
                1.0 + (100 - preset.pen_pressure) / 200.0
            )  # Pressure affects lift time
            base_coeffs["d"] *= (
                1.0 + (100 - preset.acceleration) / 100.0
            )  # Acceleration affects corner time

    # Extract features
    f = features(svg_path)

    # Calculate time components
    pen_down_time = base_coeffs["a"] * f.l_down
    travel_time = base_coeffs["b"] * f.l_travel
    lift_time = base_coeffs["c"] * f.n_lifts
    corner_time = base_coeffs["d"] * f.n_corners

    # Apply preset multiplier
    total_seconds = (
        pen_down_time + travel_time + lift_time + corner_time
    ) * preset_multiplier

    return EstimationResult(
        total_seconds=total_seconds,
        total_minutes=total_seconds / 60.0,
        pen_down_time=pen_down_time * preset_multiplier,
        travel_time=travel_time * preset_multiplier,
        lift_time=lift_time * preset_multiplier,
        corner_time=corner_time * preset_multiplier,
        preset_multiplier=preset_multiplier,
        features=f,
    )


def estimate_batch(
    svg_files: List[Path], preset_name: Optional[str] = None
) -> Dict[str, EstimationResult]:
    """Estimate time for multiple SVG files (batch operation)."""
    results = {}
    total_time = 0.0

    for svg_file in svg_files:
        try:
            result = estimate_with_preset(svg_file, preset_name)
            results[str(svg_file)] = result
            total_time += result.total_seconds
        except Exception:
            # Create error result
            results[str(svg_file)] = EstimationResult(
                total_seconds=0.0,
                total_minutes=0.0,
                pen_down_time=0.0,
                travel_time=0.0,
                lift_time=0.0,
                corner_time=0.0,
                preset_multiplier=1.0,
                features=Features(0.0, 0.0, 0, 0),
            )

    return results


def estimate_job(job_dir: Path, preset_name: Optional[str] = None) -> EstimationResult:
    """Estimate time for a complete job (all layers)."""

    # Look for optimized SVG first, then source SVG
    multipen_svg = job_dir / "multipen.svg"
    src_svg = job_dir / "src.svg"

    svg_file = None
    if multipen_svg.exists():
        svg_file = multipen_svg
    elif src_svg.exists():
        svg_file = src_svg

    if not svg_file:
        raise ValueError(f"No SVG file found in {job_dir}")

    return estimate_with_preset(svg_file, preset_name)


def estimate_pen_groups(
    pen_groups: Dict[str, List], preset_name: Optional[str] = None
) -> Dict[str, Dict]:
    """Estimate time for pen-optimized groups."""
    results = {}

    for pen_name, layers in pen_groups.items():
        pen_results = {}
        total_time = 0.0

        for item in layers:
            job = item["job"]
            layer = item["layer"]

            # Estimate layer time
            layer_svg = job["path"] / "layers" / f"{layer.name}.svg"
            if layer_svg.exists():
                try:
                    result = estimate_with_preset(layer_svg, preset_name)
                    pen_results[f"{job['id']}_{layer.name}"] = result
                    total_time += result.total_seconds
                except Exception:
                    # Skip problematic layers
                    continue

        results[pen_name] = {
            "layers": pen_results,
            "total_seconds": total_time,
            "total_minutes": total_time / 60.0,
            "layer_count": len(pen_results),
        }

    return results


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        return f"{hours:.0f}h {minutes:.0f}m"


def get_estimation_summary(result: EstimationResult) -> Dict[str, float]:
    """Get summary statistics for estimation result."""
    return {
        "total_seconds": result.total_seconds,
        "total_minutes": result.total_minutes,
        "pen_down_mm": result.features.l_down,
        "travel_mm": result.features.l_travel,
        "lifts": result.features.n_lifts,
        "corners": result.features.n_corners,
        "preset_multiplier": result.preset_multiplier,
    }
