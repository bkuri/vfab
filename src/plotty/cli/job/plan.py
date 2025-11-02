"""
Plan job command for ploTTY CLI.
"""

from __future__ import annotations

from pathlib import Path
import typer
import json
from datetime import datetime

from ...config import load_config
from ...utils import error_handler
from ..core import get_available_job_ids

try:
    from rich.console import Console

    console = Console()
except ImportError:
    console = None

plan_app = typer.Typer(help="Plan jobs for plotting")


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


@plan_app.command()
def job(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to plan"
    ),
    pen: str = "0.3mm black",
    interactive: bool = False,
):
    """Plan a job for plotting."""
    try:
        config = load_config(None)
        job_dir = Path(config.workspace) / "jobs" / job_id

        if not job_dir.exists():
            raise typer.BadParameter(f"Job {job_id} not found")

        # Load job data
        job_file = job_dir / "job.json"
        if not job_file.exists():
            raise typer.BadParameter(f"Job metadata not found for {job_id}")

        job_data = json.loads(job_file.read_text())
        src_svg = job_dir / "src.svg"

        if not src_svg.exists():
            raise typer.BadParameter(f"Source SVG not found for job {job_id}")

        # Get available pens from database
        from ...db import get_session
        from ...models import Pen

        with get_session() as session:
            pens = session.query(Pen).all()
            available_pens = [
                {
                    "id": p.id,
                    "name": p.name,
                    "width_mm": p.width_mm,
                    "speed_cap": p.speed_cap,
                    "pressure": p.pressure,
                    "passes": p.passes,
                }
                for p in pens
            ]

        # Create pen mapping from specified pen
        pen_map = None
        if pen:
            # Detect layers to create mapping
            from ...multipen import detect_svg_layers

            layers = detect_svg_layers(src_svg)
            pen_map = {layer.name: pen for layer in layers}

        # Plan the job
        from ...planner import plan_layers

        plan_result = plan_layers(
            src_svg=src_svg,
            preset="fast",  # Use fast preset for planning
            presets_file=config.vpype.presets_file,
            pen_map=pen_map,
            out_dir=job_dir,
            available_pens=available_pens,
            interactive=interactive,
            paper_size=job_data.get("paper", "A4"),
        )

        # Save planning results
        plan_file = job_dir / "plan.json"
        plan_file.write_text(json.dumps(plan_result, indent=2, default=str))

        # Update job state to OPTIMIZED
        job_data["state"] = "OPTIMIZED"
        job_data["planned_at"] = datetime.now().isoformat()
        job_file.write_text(json.dumps(job_data, indent=2))

        # Update job state to OPTIMIZED in JSON file
        job_data["state"] = "OPTIMIZED"
        job_data["planned_at"] = datetime.now().isoformat()
        job_data["plan_result"] = plan_result
        job_file.write_text(json.dumps(job_data, indent=2))

        # Display results
        if console:
            console.print(f"✅ Job {job_id} planned successfully")
            console.print(f"   Layers: {plan_result['layer_count']}")
            console.print(
                f"   Time estimate: {plan_result['estimates']['post_s']:.1f}s"
            )
            if plan_result["estimates"]["time_saved_percent"] > 0:
                console.print(
                    f"   Time saved: {plan_result['estimates']['time_saved_percent']:.1f}%"
                )
        else:
            print(f"Job {job_id} planned successfully")
            print(f"Layers: {plan_result['layer_count']}")
            print(f"Time estimate: {plan_result['estimates']['post_s']:.1f}s")

    except Exception as e:
        error_handler.handle(e)
