"""
Backup info command for ploTTY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from ...backup import BackupConfig, BackupManager

console = Console()

info_app = typer.Typer(
    name="info", help="Show backup information", no_args_is_help=True
)


@info_app.command()
def backup(
    backup_file: str = typer.Argument(..., help="Backup file to inspect"),
    backup_dir: Optional[str] = typer.Option(
        None, "--backup-dir", "-b", help="Backup directory path"
    ),
) -> None:
    """Show detailed information about a backup."""
    try:
        backup_path = Path(backup_file)

        # If not absolute path, look in backup directory
        if not backup_path.is_absolute():
            backup_dir_path = Path(backup_dir) if backup_dir else Path("backups")
            backup_path = backup_dir_path / backup_file

        if not backup_path.exists():
            console.print(f"[red]Backup file not found: {backup_path}[/red]")
            raise typer.Exit(1)

        # Create backup manager and get info
        backup_config = BackupConfig(
            backup_directory=Path(backup_dir) if backup_dir else Path("backups")
        )
        manager = BackupManager(backup_config)

        backups = manager.list_backups()
        backup_info = None
        for backup in backups:
            if Path(backup["path"]) == backup_path.resolve():
                backup_info = backup
                break

        if not backup_info:
            console.print("[red]Could not read backup information[/red]")
            raise typer.Exit(1)

        # Display information
        console.print(
            Panel(
                f"[bold]Backup Information[/bold]\n\n"
                f"[cyan]File:[/cyan] {backup_info['file']}\n"
                f"[cyan]Type:[/cyan] {backup_info['type']}\n"
                f"[cyan]Created:[/cyan] {backup_info['created_at']}\n"
                f"[cyan]Size:[/cyan] {backup_info['size'] / (1024 * 1024):.1f}MB\n"
                f"[cyan]Compression:[/cyan] {backup_info['compression']}\n"
                f"[cyan]Files:[/cyan] {backup_info['total_files']}\n"
                f"[cyan]Uncompressed Size:[/cyan] {backup_info['total_size'] / (1024 * 1024):.1f}MB",
                title="📦 Backup Details",
                border_style="blue",
            )
        )

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
