"""
Add job command for ploTTY CLI.
"""

from __future__ import annotations

from pathlib import Path
import typer
import uuid
import json

from ...config import load_config
from ...utils import error_handler, validate_file_exists
from ...progress import show_status

add_app = typer.Typer(help="Add new jobs")


@add_app.command()
def job(src: str, name: str = "", paper: str = "A3"):
    """Add a new job to workspace."""
    try:
        cfg = load_config(None)

        # Validate source file exists
        src_path = Path(src)
        validate_file_exists(src_path, "Source SVG file")

        # Generate 6-character job ID for better usability
        job_id = uuid.uuid4().hex[:6]
        jdir = Path(cfg.workspace) / "jobs" / job_id

        # Create job directory
        jdir.mkdir(parents=True, exist_ok=True)

        # Copy source file
        (jdir / "src.svg").write_bytes(src_path.read_bytes())

        # Create job metadata
        job_data = {
            "id": job_id,
            "name": name or src_path.stem,
            "paper": paper,
            "state": "QUEUED",
            "config_status": "DEFAULTS",
            "created_at": str(Path.cwd()),
        }

        (jdir / "job.json").write_text(json.dumps(job_data, indent=2))

        show_status(f"✓ Added job {job_id}: {job_data['name']}", "success")
        print(job_id)

    except Exception as e:
        error_handler.handle(e)
