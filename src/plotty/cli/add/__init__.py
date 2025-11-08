"""
Add commands for ploTTY CLI.

This module provides commands for adding new resources like pens, paper, jobs, and tests.
"""

from __future__ import annotations

from typing import Optional
import typer
from pathlib import Path

from ..common import create_apply_option, create_dry_run_option, DryRunContext

# Create add command group
add_app = typer.Typer(no_args_is_help=True, help="Add new resources")


def add_single_job(
    job_name: str = typer.Argument(..., help="Name for the new job"),
    file_path: Path = typer.Argument(..., help="Path to SVG or PLOB file to add"),
    preset: Optional[str] = typer.Option(
        None, "--preset", "-p", help="Optimization preset (fast, default, hq)"
    ),
    digest: Optional[int] = typer.Option(
        None, "--digest", "-d", help="Digest level for AxiDraw acceleration (0-2)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Override existing job with same name"
    ),
    apply: bool = create_apply_option("Add job (dry-run by default)"),
    dry_run: bool = create_dry_run_option(
        "Preview job addition without creating files"
    ),
) -> None:
    """Add a new job from an SVG or PLOB file.

    Examples:
        plotty add job my_design drawing.svg
        plotty add job my_design drawing.svg --preset hq --digest 2
        plotty add job my_design drawing.svg --force --apply

    This command analyzes the file, detects layers, and prepares it for plotting.
    Use --apply to actually create the job, otherwise runs in preview mode.
    """
    from plotty.fsm import create_fsm, JobState
    from plotty.config import get_config, load_config
    from plotty.utils import error_handler
    from plotty.progress import show_status
    from pathlib import Path
    import json
    from datetime import datetime, timezone

    # Validate file exists
    if not file_path.exists():
        typer.echo(f"❌ Error: File '{file_path}' not found")
        typer.echo("💡 Suggestions:")
        typer.echo(f"   • Check if the file path is correct: {file_path}")
        typer.echo("   • Use absolute path if the file is in a different directory")
        typer.echo("   • List available files with: ls *.svg *.plob")
        raise typer.Exit(1)

    # Detect file type and determine mode
    file_ext = file_path.suffix.lower()
    is_plob_file = file_ext == ".plob"

    # Get config for optimization settings
    config = get_config()

    # Determine preset and digest based on file type and overrides
    if is_plob_file:
        # Plob files always use pristine mode (no optimization)
        effective_preset = None
        effective_digest = None
        mode = "plob"
    elif preset:
        # User-specified preset
        effective_preset = preset
        effective_digest = (
            digest if digest is not None else config.optimization.default_digest
        )
        mode = "normal"
    else:
        # Use default optimization
        effective_preset = config.optimization.default_level
        effective_digest = (
            digest if digest is not None else config.optimization.default_digest
        )
        mode = "normal"

    # Create job directory and files (following add_jobs pattern)
    cfg = load_config(None)
    job_id = job_name
    jdir = Path(cfg.workspace) / "jobs" / job_id

    # Check if job already exists
    if not force and jdir.exists():
        typer.echo(f"❌ Error: Job '{job_name}' already exists")
        typer.echo("💡 Suggestions:")
        typer.echo(
            f"   • Use --force to override existing job: plotty add job {job_name} {file_path} --force"
        )
        typer.echo(
            f"   • Choose a different job name: plotty add job {job_name}_v2 {file_path}"
        )
        typer.echo("   • List existing jobs: plotty list jobs")
        raise typer.Exit(1)

    # Dry-run/preview mode
    if dry_run or not apply:
        items_to_add = [
            f"job '{job_name}' from '{file_path}'",
            f"target directory: {jdir}",
            f"preset: {preset or 'default'}",
            f"digest: {digest or 'default'}",
        ]

        ctx = DryRunContext(
            operation_name="add job",
            apply_flag=apply,
            items=items_to_add,
            item_type="job",
            operation_type="file_op",
        )

        if not ctx.should_execute():
            return

    # Create job directory
    jdir.mkdir(parents=True, exist_ok=True)

    # Copy source file to appropriate location
    if is_plob_file:
        # Plob files go to multipen.plob
        (jdir / "multipen.plob").write_bytes(file_path.read_bytes())
    else:
        # SVG files go to src.svg
        (jdir / "src.svg").write_bytes(file_path.read_bytes())

    # Create initial job metadata with NEW state
    job_data = {
        "id": job_id,
        "name": job_name,
        "paper": "A4",  # Default paper
        "state": JobState.NEW.value,
        "config_status": "DEFAULTS",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "mode": mode,
            "file_type": file_ext,
            "preset": effective_preset,
            "digest": effective_digest,
        },
    }

    (jdir / "job.json").write_text(json.dumps(job_data, indent=2))

    # Create FSM and handle transitions
    fsm = create_fsm(job_id, Path(cfg.workspace))

    try:
        if mode == "plob":
            # Plob files: NEW -> READY -> QUEUED (skip analysis and optimization)
            success = fsm.transition_to(
                JobState.READY,
                reason="Plob file - ready to queue",
            )
            if success:
                success = fsm.queue_ready_job()
        else:
            # Normal files: NEW -> ANALYZED -> OPTIMIZED -> READY -> QUEUED
            success = fsm.transition_to(
                JobState.ANALYZED, reason="Starting job analysis"
            )

            if success:
                success = fsm.apply_optimizations(
                    preset=effective_preset, digest=effective_digest
                )

                if success:
                    success = fsm.transition_to(
                        JobState.READY, reason="Job ready to queue"
                    )
                    if success:
                        success = fsm.queue_ready_job()

        if success:
            # Show final status
            mode_desc = (
                "Plob file" if mode == "plob" else f"Optimized ({effective_preset})"
            )
            show_status(f"✓ Added and queued job: {job_name}", "success")
            typer.echo(f"  File: {file_path}")
            typer.echo(f"  Mode: {mode_desc}")
            if effective_preset:
                typer.echo(f"  Preset: {effective_preset}")
            if effective_digest is not None:
                typer.echo(f"  Digest: {effective_digest}")
        else:
            show_status(f"✗ Failed to add job {job_name}", "error")
            raise typer.Exit(1)

    except Exception as e:
        # Cleanup on failure
        import shutil

        if jdir.exists():
            shutil.rmtree(jdir)
        error_handler.handle(e)
        raise typer.Exit(1)


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
        ..., help="File pattern for multiple jobs (e.g., '*.svg', 'designs/*.plob')"
    ),
    pristine: bool = typer.Option(
        False,
        "--pristine",
        help="Skip optimization (add in pristine state for manual control)",
    ),
    apply: bool = create_apply_option("Add jobs (dry-run by default)"),
    dry_run: bool = create_dry_run_option(
        "Preview job addition without creating files"
    ),
) -> None:
    """Add multiple jobs using a file pattern.

    Examples:
        plotty add jobs "*.svg"
        plotty add jobs "designs/*.svg" --apply
        plotty add jobs "*.plob" --pristine --apply

    This command processes all files matching the pattern and creates jobs for each one.
    Use --apply to actually create the jobs, otherwise runs in preview mode.
    The --pristine flag skips optimization for manual control over the plotting process.
    """
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

        # Dry-run/preview mode
        if dry_run or not apply:
            items_to_add = [
                f"{len(files)} jobs from pattern '{pattern}'",
                f"mode: {'pristine' if pristine else 'optimized'}",
            ]

            ctx = DryRunContext(
                operation_name="add multiple jobs",
                apply_flag=apply,
                items=items_to_add,
                item_type="job batch",
                operation_type="file_op",
            )

            if not ctx.should_execute():
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
                    # NEW -> READY -> QUEUED (skip optimization, auto-queue)
                    success = fsm.transition_to(
                        JobState.READY,
                        reason="Job added in pristine mode - ready to queue",
                    )
                    if success:
                        # Automatic transition to QUEUED
                        success = fsm.queue_ready_job()
                else:
                    # NEW -> ANALYZED -> OPTIMIZED -> READY -> QUEUED
                    # Analyze phase
                    success = fsm.transition_to(
                        JobState.ANALYZED, reason="Starting job analysis"
                    )

                    if success:
                        # Optimization phase (using FSM's built-in optimization)
                        success = fsm.optimize_job(interactive=False)

                        if success:
                            # Ready phase (job is ready to be queued)
                            success = fsm.transition_to(
                                JobState.READY,
                                reason="Job optimization completed, ready to queue",
                            )
                            if success:
                                # Automatic transition to QUEUED
                                success = fsm.queue_ready_job()

                if success:
                    added_jobs.append(job_id)
                    show_status(
                        f"✓ Added and queued job {job_id}: {src_path.name}", "success"
                    )
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
