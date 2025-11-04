"""
Remove commands for ploTTY CLI.

This module provides commands for removing resources like pens, paper, and jobs.
"""

from __future__ import annotations

import typer
from pathlib import Path

# Create remove command group
remove_app = typer.Typer(no_args_is_help=True, help="Remove resources")


def remove_pen(name: str) -> None:
    """Remove a pen configuration."""
    try:
        from ...db import get_session
        from ...models import Pen
        from ...codes import ExitCode
        from ...progress import show_status

        with get_session() as session:
            # Find the pen
            pen = session.query(Pen).filter(Pen.name == name).first()
            if not pen:
                typer.echo(f"Error: Pen '{name}' not found", err=True)
                raise typer.Exit(ExitCode.NOT_FOUND)

            # Check if pen is in use
            from ...models import Layer

            layers_using_pen = (
                session.query(Layer).filter(Layer.pen_id == pen.id).count()
            )
            if layers_using_pen > 0:
                typer.echo(
                    f"Error: Cannot remove pen '{name}': it is used by {layers_using_pen} layer(s)",
                    err=True,
                )
                raise typer.Exit(ExitCode.BUSY)

            # Confirm removal
            response = input(f"Remove pen '{name}'? [y/N]: ").strip().lower()
            if response not in ["y", "yes"]:
                show_status("Operation cancelled", "info")
                return

            # Remove the pen
            session.delete(pen)
            session.commit()

            typer.echo(f"✅ Removed pen '{name}' successfully")

    except typer.Exit:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def remove_paper(name: str) -> None:
    """Remove a paper configuration."""
    try:
        from ...db import get_session
        from ...models import Paper
        from ...codes import ExitCode
        from ...progress import show_status

        with get_session() as session:
            # Find the paper
            paper = session.query(Paper).filter(Paper.name == name).first()
            if not paper:
                typer.echo(f"Error: Paper '{name}' not found", err=True)
                raise typer.Exit(ExitCode.NOT_FOUND)

            # Check if paper is in use
            from ...models import Job

            jobs_using_paper = (
                session.query(Job).filter(Job.paper_id == paper.id).count()
            )
            if jobs_using_paper > 0:
                typer.echo(
                    f"Error: Cannot remove paper '{name}': it is used by {jobs_using_paper} job(s)",
                    err=True,
                )
                raise typer.Exit(ExitCode.BUSY)

            # Confirm removal
            response = input(f"Remove paper '{name}'? [y/N]: ").strip().lower()
            if response not in ["y", "yes"]:
                show_status("Operation cancelled", "info")
                return

            # Remove the paper
            session.delete(paper)
            session.commit()

            typer.echo(f"✅ Removed paper '{name}' successfully")

    except typer.Exit:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def remove_job(
    job_id: str,
    apply: bool = typer.Option(
        False, "--apply", help="Apply removal (dry-run by default)"
    ),
) -> None:
    """Remove a job from workspace."""
    try:
        from ...config import load_config
        from ...utils import error_handler
        from ...progress import show_status
        from ...codes import ExitCode

        cfg = load_config(None)
        job_dir = Path(cfg.workspace) / "jobs" / job_id

        # Validate job exists
        if not job_dir.exists():
            typer.echo(f"Error: Job '{job_id}' not found", err=True)
            raise typer.Exit(ExitCode.NOT_FOUND)

        # Show what will be done
        typer.echo(f"Will remove job '{job_id}' and all its data")

        if not apply:
            typer.echo("💡 Use --apply to actually remove job")
            return

        # Confirm removal
        response = input(f"Remove job '{job_id}'? [y/N]: ").strip().lower()
        if response not in ["y", "yes"]:
            show_status("Operation cancelled", "info")
            return

        # Remove job directory
        import shutil

        shutil.rmtree(job_dir)

        show_status(f"✓ Removed job {job_id}", "success")

    except typer.Exit:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def remove_jobs(
    only: str = typer.Option(
        None, "--only", help="Comma-separated list of job IDs to remove"
    ),
    failed: bool = typer.Option(False, "--failed", help="Remove only failed jobs"),
    resumed: bool = typer.Option(False, "--resumed", help="Remove only resumed jobs"),
    finished: bool = typer.Option(
        False, "--finished", help="Remove only finished jobs"
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Apply removal (dry-run by default)"
    ),
) -> None:
    """Remove multiple jobs with filtering options."""
    try:
        from ...config import load_config
        from ...utils import error_handler
        from ...progress import show_status
        from ...codes import ExitCode
        import json

        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        if not jobs_dir.exists():
            show_status("No jobs directory found", "warning")
            return

        # Get all jobs
        all_jobs = []
        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue

            job_file = job_dir / "job.json"
            if not job_file.exists():
                continue

            try:
                job_data = json.loads(job_file.read_text())
                all_jobs.append(
                    {
                        "id": job_data.get("id", job_dir.name),
                        "state": job_data.get("state", "UNKNOWN"),
                        "path": job_dir,
                    }
                )
            except Exception:
                continue

        if not all_jobs:
            show_status("No jobs found", "info")
            return

        # Apply filters
        jobs_to_remove = all_jobs

        if only:
            only_ids = [job_id.strip() for job_id in only.split(",")]
            jobs_to_remove = [j for j in jobs_to_remove if j["id"] in only_ids]

        if failed:
            jobs_to_remove = [j for j in jobs_to_remove if j["state"] == "FAILED"]
        elif resumed:
            jobs_to_remove = [
                j
                for j in jobs_to_remove
                if j["state"] in ["PLOTTING", "ARMED", "READY"]
            ]
        elif finished:
            jobs_to_remove = [
                j for j in jobs_to_remove if j["state"] in ["COMPLETED", "ABORTED"]
            ]

        if not jobs_to_remove:
            show_status("No jobs match the specified criteria", "info")
            return

        # Show what will be removed
        typer.echo(f"Will remove {len(jobs_to_remove)} jobs:")
        for job in jobs_to_remove:
            typer.echo(f"  • {job['id']} (state: {job['state']})")

        if not apply:
            typer.echo("💡 Use --apply to actually remove jobs")
            return

        # Confirm removal
        response = input(f"Remove {len(jobs_to_remove)} jobs? [y/N]: ").strip().lower()
        if response not in ["y", "yes"]:
            show_status("Operation cancelled", "info")
            return

        # Remove jobs
        import shutil

        removed_count = 0
        failed_count = 0

        for job in jobs_to_remove:
            try:
                shutil.rmtree(job["path"])
                typer.echo(f"  ✓ Removed {job['id']}")
                removed_count += 1
            except Exception as e:
                typer.echo(f"  ❌ Failed to remove {job['id']}: {e}", err=True)
                failed_count += 1

        show_status(
            f"Removed {removed_count} jobs, {failed_count} failed",
            "success" if failed_count == 0 else "warning",
        )

    except typer.Exit:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


# Register commands
remove_app.command("pen", help="Remove a pen configuration")(remove_pen)
remove_app.command("paper", help="Remove a paper configuration")(remove_paper)
remove_app.command("job", help="Remove a job")(remove_job)
remove_app.command("jobs", help="Remove multiple jobs with filtering")(remove_jobs)

__all__ = ["remove_app"]
