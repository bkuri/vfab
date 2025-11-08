"""
Restart command for ploTTY CLI.

Provides functionality to restart jobs from beginning by removing progress data.
"""

from __future__ import annotations

import typer
from pathlib import Path
import shutil

from ..config import load_config
from ..progress import show_status
from ..codes import ExitCode
from ..utils import error_handler
from ..recovery import requeue_job_to_front

try:
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Confirm = None


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        jobs_dir = workspace / "jobs"

        if not jobs_dir.exists():
            return []

        job_ids = []
        for job_dir in jobs_dir.iterdir():
            if job_dir.is_dir():
                job_id = job_dir.name
                if job_id.startswith(incomplete):
                    job_ids.append(job_id)
        return job_ids
    except Exception:
        return []


def restart_command(
    job_id: str = typer.Argument(
        ..., help="Job ID to restart", autocompletion=complete_job_id
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Apply restart changes (dry-run by default)"
    ),
    now: bool = typer.Option(
        False, "--now", help="Move job to front of queue after restart"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
) -> None:
    """Restart job from beginning."""
    try:
        cfg = load_config(None)
        workspace = Path(cfg.workspace)
        job_dir = workspace / "jobs" / job_id

        if not job_dir.exists():
            if console:
                console.print(f"❌ Job '{job_id}' not found", style="red")
            else:
                print(f"Job '{job_id}' not found")
            raise typer.Exit(ExitCode.NOT_FOUND)

        # Identify what will be removed
        files_to_remove = []
        dirs_to_remove = []

        # Journal file
        journal_file = job_dir / "journal.jsonl"
        if journal_file.exists():
            files_to_remove.append(journal_file)

        # Progress files
        for pattern in ["*.progress", "*.tmp", "*.partial"]:
            for file_path in job_dir.glob(pattern):
                files_to_remove.append(file_path)

        # Output files (partial)
        output_dir = job_dir / "output"
        if output_dir.exists():
            dirs_to_remove.append(output_dir)

        if not files_to_remove and not dirs_to_remove:
            if console:
                console.print(
                    f"ℹ️  Job '{job_id}' has no progress data to remove", style="blue"
                )
            else:
                print(f"Job '{job_id}' has no progress data to remove")
            return

        # Show what will be removed
        if console:
            console.print(f"🔄 Will restart job '{job_id}' by removing:")
            for file_path in files_to_remove:
                console.print(f"  📄 {file_path.name}")
            for dir_path in dirs_to_remove:
                console.print(f"  📁 {dir_path.name}/")
        else:
            print(f"Will restart job '{job_id}' by removing:")
            for file_path in files_to_remove:
                print(f"  {file_path.name}")
            for dir_path in dirs_to_remove:
                print(f"  {dir_path.name}/")

        if not apply:
            if console:
                console.print("💡 Use --apply to actually restart job", style="yellow")
            else:
                print("Use --apply to actually restart job")
            return

        # Confirm restart
        if console and Confirm:
            if not Confirm.ask(
                f"Restart job '{job_id}'? This will remove all progress data."
            ):
                show_status("Restart cancelled", "info")
                return
        else:
            response = (
                input(
                    f"Restart job '{job_id}'? This will remove all progress data. [y/N]: "
                )
                .strip()
                .lower()
            )
            if response not in ["y", "yes"]:
                print("Restart cancelled")
                return

        # Perform restart with progress tracking
        from ..progress import progress_task
        
        total_operations = len(files_to_remove) + len(dirs_to_remove)
        
        with progress_task(f"Restarting job '{job_id}'", total_operations) as update:
            # Remove files
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    if console:
                        console.print(f"  ✓ Removed {file_path.name}", style="green")
                    else:
                        print(f"  Removed {file_path.name}")
                except Exception as e:
                    if console:
                        console.print(
                            f"  ❌ Failed to remove {file_path.name}: {e}", style="red"
                        )
                    else:
                        print(f"  Failed to remove {file_path.name}: {e}")
                finally:
                    update(1)

            # Remove directories
            for dir_path in dirs_to_remove:
                try:
                    shutil.rmtree(dir_path)
                    if console:
                        console.print(f"  ✓ Removed {dir_path.name}/", style="green")
                    else:
                        print(f"  Removed {dir_path.name}/")
                except Exception as e:
                    if console:
                        console.print(
                            f"  ❌ Failed to remove {dir_path.name}/: {e}", style="red"
                        )
                    else:
                        print(f"  Failed to remove {dir_path.name}/: {e}")
                finally:
                    update(1)

        # Handle queue positioning if requested
        if now:
            try:
                requeue_job_to_front(job_id, workspace)
                if console:
                    console.print(
                        f"🚀 Job '{job_id}' moved to front of queue", style="blue"
                    )
                else:
                    print(f"Job '{job_id}' moved to front of queue")
            except Exception as e:
                if console:
                    console.print(
                        f"⚠️  Failed to move job to front of queue: {e}", style="yellow"
                    )
                else:
                    print(f"Warning: Failed to move job to front of queue: {e}")

        if console:
            console.print(f"✅ Successfully restarted job '{job_id}'", style="green")
            console.print("Job is ready to begin from the start")
        else:
            print(f"Successfully restarted job '{job_id}'")
            print("Job is ready to begin from the start")

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)
