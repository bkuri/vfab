"""
Backup cleanup command for ploTTY.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ...backup import BackupConfig, BackupManager

console = Console()

cleanup_app = typer.Typer(
    name="cleanup", help="Clean up old backups", no_args_is_help=True
)


@cleanup_app.command()
def backups(
    days: int = typer.Option(
        30, "--days", "-d", help="Delete backups older than N days"
    ),
    keep: int = typer.Option(
        10, "--keep", "-k", help="Keep only the N most recent backups"
    ),
    backup_dir: Optional[str] = typer.Option(
        None, "--backup-dir", "-b", help="Backup directory path"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be deleted without deleting"
    ),
) -> None:
    """Clean up old backups."""
    try:
        # Create backup manager
        backup_config = BackupConfig(
            backup_directory=Path(backup_dir) if backup_dir else Path("backups"),
            retention_days=days,
            max_backups=keep,
        )
        manager = BackupManager(backup_config)

        # Get current backups
        backups = manager.list_backups()

        if not backups:
            console.print("[yellow]No backups found[/yellow]")
            return

        # Find backups to delete
        cutoff_date = datetime.now() - timedelta(days=days)
        to_delete = []

        for i, backup in enumerate(backups):
            should_delete = False
            reason = ""

            if backup["created_at"] < cutoff_date:
                should_delete = True
                reason = f"Older than {days} days"
            elif i >= keep:
                should_delete = True
                reason = f"Exceeds keep limit of {keep}"

            if should_delete:
                to_delete.append((backup, reason))

        if not to_delete:
            console.print(
                f"[green]No backups need cleanup (keeping {len(backups)})[/green]"
            )
            return

        # Show what will be deleted
        console.print(f"[yellow]Found {len(to_delete)} backups to delete:[/yellow]\n")

        table = Table()
        table.add_column("Backup", style="cyan")
        table.add_column("Created", style="yellow")
        table.add_column("Size", style="blue")
        table.add_column("Reason", style="red")

        total_size = 0
        for backup, reason in to_delete:
            created_str = backup["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            size_str = f"{backup['size'] / (1024 * 1024):.1f}MB"
            total_size += backup["size"]

            table.add_row(backup["file"], created_str, size_str, reason)

        console.print(table)

        total_size_mb = total_size / (1024 * 1024)
        console.print(
            f"\n[bold red]Total space to be freed: {total_size_mb:.1f}MB[/bold red]"
        )

        if dry_run:
            console.print("\n[yellow]Dry run mode - no files were deleted[/yellow]")
            console.print("Run without --dry-run to actually delete these files")
            return

        # Confirmation
        if not typer.confirm(f"\n[yellow]Delete {len(to_delete)} backups?[/yellow]"):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

        # Delete backups
        deleted_count = 0
        for backup, _ in to_delete:
            try:
                manager.delete_backup(Path(backup["path"]))
                deleted_count += 1
            except Exception as e:
                console.print(f"[red]Failed to delete {backup['file']}: {e}[/red]")

        console.print(
            f"[green]✓ Deleted {deleted_count} backups, freed {total_size_mb:.1f}MB[/green]"
        )

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
