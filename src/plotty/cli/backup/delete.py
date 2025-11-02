"""
Backup delete command for ploTTY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ...backup import BackupConfig, BackupManager

console = Console()

delete_app = typer.Typer(name="delete", help="Delete a backup", no_args_is_help=True)


@delete_app.command()
def backup(
    backup_file: str = typer.Argument(..., help="Backup file to delete"),
    backup_dir: Optional[str] = typer.Option(
        None, "--backup-dir", "-b", help="Backup directory path"
    ),
    confirm: bool = typer.Option(
        False, "--confirm", "-y", help="Skip confirmation prompt"
    ),
) -> None:
    """Delete a backup file."""
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
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        console.print(f"[blue]Backup file: {backup_path}[/blue]")
        console.print(f"[cyan]Size: {size_mb:.1f}MB[/cyan]")

        # Confirmation
        if not confirm:
            if not typer.confirm("\n[yellow]Delete this backup?[/yellow]"):
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        # Delete backup
        backup_config = BackupConfig(
            backup_directory=Path(backup_dir) if backup_dir else Path("backups")
        )
        manager = BackupManager(backup_config)

        manager.delete_backup(backup_path)

        console.print("[green]✓ Backup deleted successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error deleting backup: {e}[/red]")
        raise typer.Exit(1)
