"""
Job management commands for ploTTY CLI.
"""

from __future__ import annotations

from pathlib import Path
import typer
import uuid
import json

from ..config import load_config
from ..utils import error_handler, validate_file_exists, create_job_error
from ..progress import show_status
from .core import get_available_job_ids

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Table = None
    Confirm = None

# Create job command group
job_app = typer.Typer(help="Job management commands")


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


@job_app.command()
def add(src: str, name: str = "", paper: str = "A3"):
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


@job_app.command()
def plan(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to plan"
    ),
    pen: str = "0.3mm black",
    interactive: bool = False,
):
    """Plan a job for plotting."""
    try:
        # TODO: Implement job planning logic
        print(f"Planning job {job_id} with pen {pen}, interactive={interactive}")
    except Exception as e:
        error_handler.handle(e)


@job_app.command()
def record_test(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to record"
    ),
    seconds: int = 5,
):
    """Record a test plot for timing."""
    try:
        # TODO: Implement test recording logic
        print(f"Recording test for job {job_id} for {seconds} seconds")
    except Exception as e:
        error_handler.handle(e)


@job_app.command("list")
def list_jobs():
    """List all jobs in workspace."""
    try:
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        if not jobs_dir.exists():
            show_status("No jobs directory found", "warning")
            return

        jobs = []
        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue

            job_file = job_dir / "job.json"
            if not job_file.exists():
                continue

            try:
                job_data = json.loads(job_file.read_text())

                # Get plan info for time estimates
                plan_file = job_dir / "plan.json"
                time_estimate = None
                layer_count = None
                if plan_file.exists():
                    plan_data = json.loads(plan_file.read_text())
                    time_estimate = plan_data.get("estimates", {}).get("post_s")
                    layer_count = len(plan_data.get("layers", []))

                jobs.append(
                    {
                        "id": job_data.get("id", job_dir.name),
                        "name": job_data.get("name", "Unknown"),
                        "state": job_data.get("state", "UNKNOWN"),
                        "paper": job_data.get("paper", "Unknown"),
                        "time_estimate": time_estimate,
                        "layer_count": layer_count,
                    }
                )
            except Exception:
                continue

        if not jobs:
            show_status("No jobs found", "info")
            return

        # Sort by state priority
        state_priority = {
            "PLOTTING": 0,
            "ARMED": 1,
            "READY": 2,
            "OPTIMIZED": 3,
            "ANALYZED": 4,
            "QUEUED": 5,
            "NEW": 6,
            "PAUSED": 7,
            "COMPLETED": 8,
            "ABORTED": 9,
            "FAILED": 10,
        }
        jobs.sort(key=lambda j: state_priority.get(j["state"], 99))

        if console and Table:
            # Rich table output
            table = Table(title=f"Jobs ({len(jobs)} total)")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("State", style="white")
            table.add_column("Paper", style="white")
            table.add_column("Layers", style="white", justify="right")
            table.add_column("Est. Time", style="white", justify="right")

            for job in jobs:
                time_str = "Unknown"
                if job["time_estimate"]:
                    if job["time_estimate"] < 60:
                        time_str = f"{job['time_estimate']:.1f}s"
                    else:
                        time_str = f"{job['time_estimate'] / 60:.1f}m"

                table.add_row(
                    job["id"],
                    job["name"][:20],
                    job["state"],
                    job["paper"],
                    str(job["layer_count"]) if job["layer_count"] else "Unknown",
                    time_str,
                )

            console.print(table)
        else:
            # Fallback plain text output
            print(f"Jobs ({len(jobs)} total):")
            for job in jobs:
                time_str = (
                    f" {job['time_estimate']:.1f}s" if job["time_estimate"] else ""
                )
                print(f"  {job['id']}: {job['name']} ({job['state']}){time_str}")

    except Exception as e:
        error_handler.handle(e)


@job_app.command()
def remove(
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
        import shutil

        shutil.rmtree(jdir)

        show_status(f"✓ Removed job {job_id}: {job_name}", "success")

    except Exception as e:
        error_handler.handle(e)
