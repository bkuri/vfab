from __future__ import annotations
from pathlib import Path
import subprocess

import shlex
import yaml


def run_vpype(pipe: str, src: Path, dst: Path) -> None:
    cmd = pipe.replace("{src}", shlex.quote(str(src))).replace(
        "{dst}", shlex.quote(str(dst))
    )
    subprocess.run(f"vpype -v {cmd}", shell=True, check=True)


def stats_json(svg: Path) -> dict:
    """Parse vpype stat output into a dictionary."""
    p = subprocess.run(
        ["vpype", "read", str(svg), "stat"],
        check=True,
        capture_output=True,
        text=True,
    )

    # Parse the text output into a structured format
    output = p.stdout
    result = {"layers": {}, "page_size": None, "totals": {}}

    lines = output.split("\n")
    current_layer = None

    for line in lines:
        line = line.strip()

        # Parse page size
        if line.startswith("Current page size:"):
            size_str = line.split(":", 1)[1].strip()
            # Parse (width, height) format
            if size_str.startswith("(") and size_str.endswith(")"):
                size_str = size_str[1:-1]  # Remove parentheses
                parts = size_str.split(",")
                if len(parts) == 2:
                    result["page_size"] = {
                        "width": float(parts[0].strip()),
                        "height": float(parts[1].strip()),
                    }

        # Parse layer info
        elif line.startswith("Layer "):
            layer_num = line.split()[1]
            current_layer = layer_num
            result["layers"][layer_num] = {
                "length_total_mm": 0.0,
                "path_count": 0,
                "segment_count": 0,
            }

        # Parse layer properties
        elif current_layer is not None and ":" in line:
            if line.startswith("Length:"):
                length = float(line.split(":", 1)[1].strip())
                result["layers"][current_layer]["length_total_mm"] = length
            elif line.startswith("Path count:"):
                count = int(line.split(":", 1)[1].strip())
                result["layers"][current_layer]["path_count"] = count
            elif line.startswith("Segment count:"):
                count = int(line.split(":", 1)[1].strip())
                result["layers"][current_layer]["segment_count"] = count

        # Parse totals
        elif line.startswith("Totals"):
            continue
        elif line.startswith("Length:") and current_layer is None:
            # This is total length after "Totals" section
            total_length = float(line.split(":", 1)[1].strip())
            result["totals"]["length_total_mm"] = total_length
        elif line.startswith("Layer count:") and current_layer is None:
            count = int(line.split(":", 1)[1].strip())
            result["totals"]["layer_count"] = count
        elif line.startswith("Path count:") and current_layer is None:
            count = int(line.split(":", 1)[1].strip())
            result["totals"]["path_count"] = count
        elif line.startswith("Segment count:") and current_layer is None:
            count = int(line.split(":", 1)[1].strip())
            result["totals"]["segment_count"] = count

    return result


def load_preset(name: str, presets_file: str) -> str:
    presets = yaml.safe_load(Path(presets_file).read_text()) or {}
    rec = presets.get("presets", {}).get(name)
    if not rec:
        raise KeyError(f"vpype preset not found: {name}")
    return rec["pipe"]
