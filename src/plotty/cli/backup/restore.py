"""
Backup restore command for ploTTY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ...backup import BackupConfig, BackupManager

console = Console()

restore_app = typer.Typer(
    name="restore", help="Restore from backup", no_args_is_help=True
)


@restore_app.command()
def backup(
    backup_file: str = typer.Argument(..., help="Backup file to restore"),
    restore_config: bool = typer.Option(
        True, "--config/--no-config", help="Restore configuration"
    ),
    restore_database: bool = typer.Option(
        True, "--database/--no-database", help="Restore database"
    ),
    restore_jobs: bool = typer.Option(
        True, "--jobs/--no-jobs", help="Restore job files"
    ),
    restore_workspace: bool = typer.Option(
        True, "--workspace/--no-workspace", help="Restore workspace files"
    ),
    target_directory: Optional[str] = typer.Option(
        None, "--target", "-t", help="Target directory for workspace restore"
    ),
    backup_dir: Optional[str] = typer.Option(
        None, "--backup-dir", "-b", help="Backup directory path"
    ),
    confirm: bool = typer.Option(
        False, "--confirm", "-y", help="Skip confirmation prompt"
    ),
) -> None:
    """Restore from a backup file."""
    try:
        backup_path = Path(backup_file)

        # If not absolute path, look in backup directory
        if not backup_path.is_absolute():
            backup_dir_path = Path(backup_dir) if backup_dir else Path("backups")
            backup_path = backup_dir_path / backup_file

        if not backup_path.exists():
            console.print(f"[red]Backup file not found: {backup_path}[/red]")
            raise typer.Exit(1)

        # Show backup info
        console.print(f"[blue]Backup file: {backup_path}[/blue]")

        # Create backup manager
        backup_config = BackupConfig(
            backup_directory=Path(backup_dir) if backup_dir else Path("backups")
        )
        manager = BackupManager(backup_config)

        # Show what will be restored
        restore_items = []
        if restore_config:
            restore_items.append("Configuration")
        if restore_database:
            restore_items.append("Database")
        if restore_jobs:
            restore_items.append("Jobs")
        if restore_workspace:
            restore_items.append("Workspace")

        console.print(f"\n[green]Will restore: {', '.join(restore_items)}[/green]")

        # Confirmation
        if not confirm:
            if not typer.confirm(
                "\n[yellow]This will overwrite existing data. Continue?[/yellow]"
            ):
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        # Perform restore
        console.print("[green]Restoring backup...[/green]")

        target_path = Path(target_directory) if target_directory else None

        manager.restore_backup(
            backup_path=backup_path,
            restore_config=restore_config,
            restore_database=restore_database,
            restore_jobs=restore_jobs,
            restore_workspace=restore_workspace,
            target_directory=target_path,
        )

        console.print("[green]✓ Backup restored successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error restoring backup: {e}[/red]")
        raise typer.Exit(1)
