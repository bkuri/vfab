"""
Add commands for ploTTY CLI.

This module provides commands for adding new resources like pens, paper, jobs, and tests.
"""

from __future__ import annotations

import typer
from pathlib import Path

# Create add command group
add_app = typer.Typer(no_args_is_help=True, help="Add new resources")


def add_single_job(
    src: str,
    name: str = typer.Option("", "--name", "-n", help="Job name"),
    paper: str = typer.Option("A4", "--paper", "-p", help="Paper size"),
    pristine: bool = typer.Option(
        False, "--pristine", help="Skip optimization (add in pristine state)"
    ),
) -> None:
    """Add a single job to workspace."""
    try:
        from ...config import load_config
        from ...fsm import create_fsm, JobState
        from ...utils import error_handler, validate_file_exists
        from ...progress import show_status
        import uuid
        import json
        from datetime import datetime, timezone

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

        # Create initial job metadata with NEW state
        job_data = {
            "id": job_id,
            "name": name or src_path.stem,
            "paper": paper,
            "state": JobState.NEW.value,
            "config_status": "DEFAULTS",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "optimization": {
                "level": "none" if pristine else "pending",
                "applied_at": None,
                "version": "1.0",
            },
        }

        (jdir / "job.json").write_text(json.dumps(job_data, indent=2))

        # Create FSM and handle transitions
        fsm = create_fsm(job_id, Path(cfg.workspace))

        if pristine:
            # NEW -> QUEUED (skip optimization, ready to plot)
            success = fsm.transition_to(
                JobState.QUEUED, reason="Job added in pristine mode - ready to plot"
            )
        else:
            # NEW -> QUEUED -> ANALYZED -> OPTIMIZED -> READY
            # First queue the job
            success = fsm.transition_to(
                JobState.QUEUED, reason="Job queued for processing"
            )

            if success:
                # Analyze phase
                success = fsm.transition_to(
                    JobState.ANALYZED, reason="Starting job analysis"
                )

                if success:
                    # Optimization phase (using FSM's built-in optimization)
                    success = fsm.optimize_job(interactive=False)

                    if success:
                        # Ready phase (job is ready after optimization)
                        success = fsm.transition_to(
                            JobState.READY,
                            reason="Job optimization completed, ready for plotting",
                        )

        if success:
            show_status(f"✓ Added job {job_id}: {job_data['name']}", "success")
            print(job_id)
        else:
            # Handle failure - FSM should have transitioned to FAILED state
            show_status(f"✗ Failed to add job {job_id}", "error")
            raise typer.Exit(1)

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


def add_pen(
    name: str,
    width_mm: float,
    speed_cap: float,
    pressure: int,
    passes: int,
    color_hex: str = typer.Option(
        "#000000", "--color", "-c", help="Pen color in hex format"
    ),
) -> None:
    """Add a new pen configuration."""
    try:
        from ...db import get_session
        from ...models import Pen
        from ...codes import ExitCode

        # Validate color hex format
        if not color_hex.startswith("#"):
            color_hex = f"#{color_hex}"

        # Validate ranges
        if width_mm <= 0:
            raise typer.BadParameter("Width must be positive")
        if speed_cap <= 0:
            raise typer.BadParameter("Speed must be positive")
        if not (0 <= pressure <= 100):
            raise typer.BadParameter("Pressure must be between 0 and 100")
        if passes < 1:
            raise typer.BadParameter("Passes must be at least 1")

        with get_session() as session:
            # Check if pen already exists
            existing_pen = session.query(Pen).filter(Pen.name == name).first()
            if existing_pen:
                typer.echo(f"Error: Pen '{name}' already exists", err=True)
                raise typer.Exit(ExitCode.ALREADY_EXISTS)

            # Create new pen
            new_pen = Pen(
                name=name,
                width_mm=width_mm,
                speed_cap=speed_cap,
                pressure=pressure,
                passes=passes,
                color_hex=color_hex,
            )

            session.add(new_pen)
            session.commit()

            typer.echo(f"✅ Added pen '{name}' successfully")

    except typer.BadParameter:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def add_paper(
    name: str,
    width_mm: float,
    height_mm: float,
    margin_mm: float = typer.Option(10, "--margin", "-m", help="Margin in mm"),
    orientation: str = typer.Option(
        "portrait", "--orientation", "-o", help="Paper orientation"
    ),
) -> None:
    """Add a new paper configuration."""
    try:
        from ...db import get_session
        from ...models import Paper
        from ...codes import ExitCode

        # Validate inputs
        if width_mm <= 0:
            raise typer.BadParameter("Width must be positive")
        if height_mm <= 0:
            raise typer.BadParameter("Height must be positive")
        if margin_mm < 0:
            raise typer.BadParameter("Margin cannot be negative")
        if orientation not in ["portrait", "landscape"]:
            raise typer.BadParameter("Orientation must be 'portrait' or 'landscape'")

        with get_session() as session:
            # Check if paper already exists
            existing_paper = session.query(Paper).filter(Paper.name == name).first()
            if existing_paper:
                typer.echo(f"Error: Paper '{name}' already exists", err=True)
                raise typer.Exit(ExitCode.ALREADY_EXISTS)

            # Create new paper
            new_paper = Paper(
                name=name,
                width_mm=width_mm,
                height_mm=height_mm,
                margin_mm=margin_mm,
                orientation=orientation,
            )

            session.add(new_paper)
            session.commit()

            typer.echo(f"✅ Added paper '{name}' successfully")

    except typer.BadParameter:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def add_jobs(
    pattern: str = typer.Argument(
        ..., help="File pattern for multiple jobs (e.g., *.svg)"
    ),
    pristine: bool = typer.Option(
        False, "--pristine", help="Skip optimization (add in pristine state)"
    ),
) -> None:
    """Add multiple jobs using file pattern."""
    try:
        from ...config import load_config
        from ...fsm import create_fsm, JobState
        from ...utils import error_handler
        from ...progress import show_status
        from pathlib import Path
        import glob
        import uuid
        import json
        from datetime import datetime, timezone

        cfg = load_config(None)

        # Find files matching pattern
        files = glob.glob(pattern)

        if not files:
            show_status(f"No files found matching pattern: {pattern}", "warning")
            return

        show_status(f"Found {len(files)} files matching pattern", "info")

        # Process each file using FSM-based flow
        added_jobs = []
        failed_jobs = []

        for file_path in files:
            try:
                src_path = Path(file_path)

                # Generate 6-character job ID
                job_id = uuid.uuid4().hex[:6]
                jdir = Path(cfg.workspace) / "jobs" / job_id

                # Create job directory
                jdir.mkdir(parents=True, exist_ok=True)

                # Copy source file
                (jdir / "src.svg").write_bytes(src_path.read_bytes())

                # Create initial job metadata with NEW state
                job_data = {
                    "id": job_id,
                    "name": src_path.stem,
                    "paper": "A4",  # Default paper
                    "state": JobState.NEW.value,
                    "config_status": "DEFAULTS",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "optimization": {
                        "level": "none" if pristine else "pending",
                        "applied_at": None,
                        "version": "1.0",
                    },
                }

                (jdir / "job.json").write_text(json.dumps(job_data, indent=2))

                # Create FSM and handle transitions
                fsm = create_fsm(job_id, Path(cfg.workspace))

                if pristine:
                    # NEW -> READY (skip optimization, ready to plot)
                    success = fsm.transition_to(
                        JobState.READY,
                        reason="Job added in pristine mode - ready to plot",
                    )
                else:
                    # NEW -> QUEUED -> ANALYZED -> OPTIMIZED -> READY
                    # First queue the job
                    success = fsm.transition_to(
                        JobState.QUEUED, reason="Job queued for processing"
                    )

                    if success:
                        # Analyze phase
                        success = fsm.transition_to(
                            JobState.ANALYZED, reason="Starting job analysis"
                        )

                        if success:
                            # Optimization phase (using FSM's built-in optimization)
                            success = fsm.optimize_job(interactive=False)

                            if success:
                                # Ready phase (job is ready after optimization)
                                success = fsm.transition_to(
                                    JobState.READY,
                                    reason="Job optimization completed, ready for plotting",
                                )

                if success:
                    added_jobs.append(job_id)
                    show_status(f"✓ Added job {job_id}: {src_path.name}", "success")
                else:
                    failed_jobs.append((file_path, "FSM transition failed"))
                    show_status(
                        f"✗ Failed to add {src_path.name}: FSM transition failed",
                        "error",
                    )

            except Exception as e:
                failed_jobs.append((file_path, str(e)))
                show_status(f"Failed to add {file_path}: {e}", "error")

        # Summary
        show_status(f"Successfully added {len(added_jobs)} jobs", "success")
        if added_jobs:
            print("Added job IDs:", ", ".join(added_jobs))

        if failed_jobs:
            show_status(f"Failed to add {len(failed_jobs)} jobs:", "error")
            for file_path, error in failed_jobs:
                print(f"  {file_path}: {error}")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


# Register commands
add_app.command("job", help="Add a new job")(add_single_job)
add_app.command("jobs", help="Add multiple jobs using pattern")(add_jobs)
add_app.command("pen", help="Add a new pen configuration")(add_pen)
add_app.command("paper", help="Add a new paper configuration")(add_paper)


__all__ = ["add_app"]
