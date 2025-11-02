"""
Log cleanup command for ploTTY.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ...logging import get_logger, logging_manager

console = Console()


def cleanup_logs(
    days: int = typer.Option(30, "--days", "-d", help="Keep logs newer than N days"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be deleted without deleting"
    ),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
) -> None:
    """Clean up old log files."""
    try:
        logger = get_logger("cli")

        log_files = logging_manager.list_log_files()
        if not log_files:
            console.print("[yellow]No log files found[/yellow]")
            return

        cutoff_date = datetime.now() - timedelta(days=days)
        files_to_delete = []

        for log_file in log_files:
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    files_to_delete.append((log_file, file_time))
            except OSError:
                continue

        if not files_to_delete:
            console.print(f"[green]No log files older than {days} days found[/green]")
            return

        # Show files to be deleted
        console.print(
            f"[yellow]Found {len(files_to_delete)} log files older than {days} days:[/yellow]\n"
        )

        table = Table()
        table.add_column("File", style="cyan")
        table.add_column("Modified", style="red")
        table.add_column("Size", style="yellow")

        total_size = 0
        for log_file, file_time in files_to_delete:
            try:
                stat = log_file.stat()
                size = stat.st_size
                total_size += size
                size_str = (
                    f"{size / 1024:.1f}KB"
                    if size < 1024 * 1024
                    else f"{size / (1024 * 1024):.1f}MB"
                )
                modified = file_time.strftime("%Y-%m-%d %H:%M:%S")

                table.add_row(str(log_file), modified, size_str)
            except OSError:
                table.add_row(str(log_file), "Unknown", "Unknown")

        console.print(table)

        total_size_str = (
            f"{total_size / 1024:.1f}KB"
            if total_size < 1024 * 1024
            else f"{total_size / (1024 * 1024):.1f}MB"
        )
        console.print(f"\n[bold]Total space to be freed: {total_size_str}[/bold]")

        if dry_run:
            console.print("\n[yellow]Dry run mode - no files were deleted[/yellow]")
            console.print("Run without --dry-run to actually delete these files")
            return

        # Confirm deletion
        if not typer.confirm(f"\nDelete {len(files_to_delete)} log files?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

        # Delete files
        deleted_count = 0
        for log_file, _ in files_to_delete:
            try:
                log_file.unlink()
                deleted_count += 1
                logger.info(f"Deleted old log file: {log_file}")
            except OSError as e:
                console.print(f"[red]Failed to delete {log_file}: {e}[/red]")

        console.print(f"[green]✓ Deleted {deleted_count} log files[/green]")

    except Exception as e:
        from ...utils import error_handler

        # Try to log if logger is available, but don't let logging errors cause issues
        try:
            logger = get_logger("cli")
            logger.error(f"Failed to cleanup logs: {e}")
        except Exception:
            pass
        error_handler.handle(e)
