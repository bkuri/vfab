"""
Session management commands.
"""

from __future__ import annotations

import typer

try:
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Confirm = None


def session_reset() -> None:
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

        # Confirm reset
        if console and Confirm:
            if not Confirm.ask("⚠️  This will reset all jobs and layers. Continue?"):
                from ...progress import show_status

                show_status("Operation cancelled", "info")
                return
        else:
            response = (
                input("⚠️  This will reset all jobs and layers. Continue? [y/N]: ")
                .strip()
                .lower()
            )
            if response not in ["y", "yes"]:
                print("Operation cancelled")
                return

        with get_session() as session:
            # Count current jobs and layers
            job_count = session.query(Job).count()
            layer_count = session.query(Layer).count()

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
