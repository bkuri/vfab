from __future__ import annotations
from dataclasses import dataclass
from .vpype_runner import stats_json


@dataclass
class Features:
    l_down: float
    l_travel: float
    n_lifts: int
    n_corners: int


def features(svg_path) -> Features:
    s = stats_json(svg_path)
    layer = next(iter(s.get("layers", {}).values()), {})
    return Features(
        l_down=layer.get("length_total_mm", 0.0),
        l_travel=layer.get("length_travel_mm", 0.0),
        n_lifts=layer.get("pen_lifts", 0),
        n_corners=layer.get("corners", 0),
    )


def estimate_seconds(f: Features, coeffs: dict[str, float]) -> float:
    a = coeffs.get("a", 0.04)
    b = coeffs.get("b", 0.06)
    c = coeffs.get("c", 0.35)
    d = coeffs.get("d", 0.002)
    return a * f.l_down + b * f.l_travel + c * f.n_lifts + d * f.n_corners
