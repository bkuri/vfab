"""
Backup creation command for ploTTY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ...backup import BackupConfig, BackupManager, BackupType, CompressionType

console = Console()

create_app = typer.Typer(
    name="create", help="Create a backup of ploTTY data", no_args_is_help=True
)


@create_app.command()
def backup(
    backup_type: BackupType = typer.Option(
        BackupType.FULL, "--type", "-t", help="Type of backup to create"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Custom name for backup"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", "-d", help="Description for backup"
    ),
    compression: CompressionType = typer.Option(
        CompressionType.GZIP, "--compression", "-c", help="Compression type"
    ),
    backup_dir: Optional[str] = typer.Option(
        None, "--backup-dir", "-b", help="Backup directory path"
    ),
    include_workspace: bool = typer.Option(
        True, "--workspace/--no-workspace", help="Include workspace files"
    ),
    include_database: bool = typer.Option(
        True, "--database/--no-database", help="Include database"
    ),
    include_config: bool = typer.Option(
        True, "--config/--no-config", help="Include configuration"
    ),
    include_jobs: bool = typer.Option(
        True, "--jobs/--no-jobs", help="Include job files"
    ),
) -> None:
    """Create a backup of ploTTY data."""
    try:
        # Create backup configuration
        backup_config = BackupConfig(
            backup_directory=Path(backup_dir) if backup_dir else Path("backups"),
            compression=compression,
            include_workspace=include_workspace,
            include_database=include_database,
            include_config=include_config,
            include_jobs=include_jobs,
        )

        # Create backup manager
        manager = BackupManager(backup_config)

        console.print(f"[green]Creating {backup_type.value} backup...[/green]")

        # Create backup with progress tracking
        from ...progress import spinner_task

        with spinner_task(f"Creating {backup_type.value} backup"):
            backup_path = manager.create_backup(
                backup_type=backup_type, name=name, description=description
            )

        console.print("[green]✓ Backup created successfully![/green]")
        console.print(f"[blue]Location: {backup_path}[/blue]")

        # Show backup info
        stat = backup_path.stat()
        size_mb = stat.st_size / (1024 * 1024)
        console.print(f"[cyan]Size: {size_mb:.2f} MB[/cyan]")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
