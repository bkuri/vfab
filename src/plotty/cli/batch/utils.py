"""
Batch operations utility functions.
"""

from __future__ import annotations

from pathlib import Path
import json
from typing import List, Dict, Any

from ...config import load_config
from ...utils import error_handler
from ...multipen import detect_svg_layers


def get_jobs_by_state(state_filter: str = "QUEUED") -> List[Dict[str, Any]]:
    """Get jobs filtered by state."""
    try:
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        jobs = []
        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue

            job_file = job_dir / "job.json"
            if not job_file.exists():
                continue

            try:
                job_data = json.loads(job_file.read_text())
                if job_data.get("state") == state_filter:
                    jobs.append(
                        {
                            "id": job_data.get("id", job_dir.name),
                            "name": job_data.get("name", "Unknown"),
                            "path": job_dir,
                            "data": job_data,
                        }
                    )
            except Exception:
                continue

        return jobs
    except Exception as e:
        error_handler.handle(e)
        return []


def group_layers_by_pen(jobs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group all layers across jobs by pen type."""
    pen_groups = {}

    for job in jobs:
        svg_path = job["path"] / "src.svg"
        if not svg_path.exists():
            continue

        try:
            layers = detect_svg_layers(svg_path)
            for layer in layers:
                if not layer.visible:
                    continue

                pen_name = (
                    f"pen_{layer.pen_id}" if layer.pen_id is not None else "default"
                )
                if pen_name not in pen_groups:
                    pen_groups[pen_name] = []

                pen_groups[pen_name].append(
                    {
                        "job": job,
                        "layer": layer,
                    }
                )
        except Exception:
            continue

    return pen_groups


def calculate_pen_optimization(
    pen_groups: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Calculate optimization benefits of pen-based planning."""
    total_layers = sum(len(layers) for layers in pen_groups.values())
    traditional_swaps = len(pen_groups) * len(
        pen_groups.get("default", [])
    )  # Rough estimate
    optimized_swaps = len(pen_groups)

    return {
        "total_layers": total_layers,
        "traditional_swaps": traditional_swaps,
        "optimized_swaps": optimized_swaps,
        "swap_reduction": traditional_swaps - optimized_swaps,
        "reduction_percentage": (
            ((traditional_swaps - optimized_swaps) / traditional_swaps * 100)
            if traditional_swaps > 0
            else 0
        ),
    }
