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


def remove_job(job_id: str) -> None:
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


# Register commands
remove_app.command("pen", help="Remove a pen configuration")(remove_pen)
remove_app.command("paper", help="Remove a paper configuration")(remove_paper)
remove_app.command("job", help="Remove a job")(remove_job)

__all__ = ["remove_app"]
