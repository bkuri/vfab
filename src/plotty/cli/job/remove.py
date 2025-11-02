"""
Remove job command for ploTTY CLI.
"""

from __future__ import annotations

from pathlib import Path
import typer
import json
import shutil

from ...config import load_config
from ...utils import error_handler, create_job_error
from ...progress import show_status
from ..core import get_available_job_ids

try:
    from rich.prompt import Confirm
except ImportError:
    Confirm = None

remove_app = typer.Typer(help="Remove jobs")


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


@remove_app.command()
def job(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to remove"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Remove a job from workspace."""
    try:
        cfg = load_config(None)
        jdir = Path(cfg.workspace) / "jobs" / job_id

        if not jdir.exists():
            raise create_job_error(f"Job {job_id} not found", job_id=job_id)

        # Get job name for confirmation
        job_file = jdir / "job.json"
        job_name = job_id
        if job_file.exists():
            try:
                job_data = json.loads(job_file.read_text())
                job_name = job_data.get("name", job_id)
            except Exception:
                pass

        # Confirmation prompt
        if not force:
            if Confirm:
                if not Confirm.ask(f"Remove job '{job_name}' ({job_id})?"):
                    show_status("Job removal cancelled", "info")
                    return
            else:
                response = input(f"Remove job '{job_name}' ({job_id})? [y/N]: ")
                if response.lower() not in ["y", "yes"]:
                    show_status("Job removal cancelled", "info")
                    return

        # Remove job directory
        shutil.rmtree(jdir)

        show_status(f"✓ Removed job {job_id}: {job_name}", "success")

    except Exception as e:
        error_handler.handle(e)
