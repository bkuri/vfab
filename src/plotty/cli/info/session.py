"""
Session management commands for ploTTY.
"""

from __future__ import annotations

import typer
from ..common import confirm_destructive_operation, create_apply_option

try:
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Confirm = None


def session_reset(
    apply: bool = create_apply_option("Apply session reset (dry-run by default)"),
) -> None:
    """Reset the current session."""
    try:
        from ...db import get_session
        from ...models import Job, Layer
        from ...progress import show_boxed_progress
        from ...codes import ExitCode
        from sqlalchemy import text

        if console:
            console.print("🔄 Session Reset", style="bold blue")
        else:
            print("🔄 Session Reset")
            print("=" * 20)

        # Get current session info for preview
        with get_session() as session:
            job_count = session.query(Job).count()
            layer_count = session.query(Layer).count()

        # Confirm using common library
        if not confirm_destructive_operation(
            operation_name="reset",
            item_description=f"session ({job_count} jobs, {layer_count} layers)",
            apply_flag=apply,
            console_instance=console,
        ):
            from ...progress import show_status

            show_status("Operation cancelled", "info")
            return

        with get_session() as session:
            if console:
                console.print(f"Found {job_count} jobs and {layer_count} layers")
            else:
                print(f"Found {job_count} jobs and {layer_count} layers")

            if job_count == 0 and layer_count == 0:
                if console:
                    console.print("✅ Session is already clean", style="green")
                else:
                    print("Session is already clean")
                return

            # Delete all layers first (foreign key constraint)
            show_boxed_progress("Resetting session", 1, 2)
            session.query(Layer).delete()
            session.commit()

            # Delete all jobs
            show_boxed_progress("Resetting session", 2, 2)
            session.query(Job).delete()
            session.commit()

            # Reset database sequences if using PostgreSQL
            try:
                session.execute(text("ALTER SEQUENCE jobs_id_seq RESTART WITH 1"))
                session.execute(text("ALTER SEQUENCE layers_id_seq RESTART WITH 1"))
                session.commit()
            except Exception:
                # Ignore sequence reset errors (might be SQLite)
                pass

            if console:
                console.print("✅ Session reset successfully", style="green")
            else:
                print("Session reset successfully")

    except typer.Exit:
        raise
    except Exception as e:
        from ...utils import error_handler
        from ...codes import ExitCode

        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


def session_info() -> None:
    """Show current session information."""
    try:
        from ...db import get_session
        from ...models import Job, Layer

        if console:
            console.print("📊 Session Information", style="bold blue")
        else:
            print("📊 Session Information")
            print("=" * 25)

        with get_session() as session:
            # Count jobs and layers
            job_count = session.query(Job).count()
            layer_count = session.query(Layer).count()

            # Count jobs by state
            pending_jobs = session.query(Job).filter(Job.state == "pending").count()
            running_jobs = session.query(Job).filter(Job.state == "running").count()
            completed_jobs = session.query(Job).filter(Job.state == "completed").count()
            failed_jobs = session.query(Job).filter(Job.state == "failed").count()

            if console:
                console.print(f"Total Jobs: {job_count}")
                console.print(f"Total Layers: {layer_count}")
                console.print("")
                console.print("Jobs by State:")
                console.print(f"  Pending: {pending_jobs}")
                console.print(f"  Running: {running_jobs}")
                console.print(f"  Completed: {completed_jobs}")
                console.print(f"  Failed: {failed_jobs}")
            else:
                print(f"Total Jobs: {job_count}")
                print(f"Total Layers: {layer_count}")
                print("")
                print("Jobs by State:")
                print(f"  Pending: {pending_jobs}")
                print(f"  Running: {running_jobs}")
                print(f"  Completed: {completed_jobs}")
                print(f"  Failed: {failed_jobs}")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


__all__ = ["session_reset", "session_info"]
