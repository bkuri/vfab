"""
Backup listing command for ploTTY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ...backup import BackupConfig, BackupManager

console = Console()

list_app = typer.Typer(name="list", help="List available backups", no_args_is_help=True)


@list_app.command()
def backups(
    backup_dir: Optional[str] = typer.Option(
        None, "--backup-dir", "-b", help="Backup directory path"
    ),
) -> None:
    """List all available backups."""
    try:
        # Create backup manager
        backup_config = BackupConfig(
            backup_directory=Path(backup_dir) if backup_dir else Path("backups")
        )
        manager = BackupManager(backup_config)

        # Get backups
        backups = manager.list_backups()

        if not backups:
            console.print("[yellow]No backups found[/yellow]")
            return

        console.print(f"[green]Found {len(backups)} backups:[/green]\n")

        # Create table
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Created", style="yellow")
        table.add_column("Size", style="blue")
        table.add_column("Compression", style="magenta")
        table.add_column("Files", style="white")

        for backup in backups:
            created_str = backup["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            size_str = f"{backup['size'] / (1024 * 1024):.1f}MB"

            table.add_row(
                backup["file"],
                backup["type"],
                created_str,
                size_str,
                backup["compression"],
                str(backup["total_files"]),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing backups: {e}[/red]")
        raise typer.Exit(1)
