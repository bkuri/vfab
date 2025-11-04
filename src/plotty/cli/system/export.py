"""
System export command for ploTTY CLI.

Provides simplified export functionality with --only flag for specific data types.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from rich.console import Console
from rich.prompt import Confirm

from plotty.backup import BackupManager, BackupType


# Create console for output
console = Console()

# Valid export targets
ExportTargets = Literal[
    "config", "database", "logs", "output", "presets", "statistics", "all"
]


def export_command(
    only: ExportTargets = typer.Argument(
        "all",
        help="What to export: config, database, logs, output, presets, statistics, or all",
    ),
    output_dir: Path = typer.Option(
        Path("./backup"),
        "--output-dir",
        "-o",
        help="Directory to save export to (default: ./backup)",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompts"
    ),
) -> None:
    """Export system data and configurations.

    This command creates backups of ploTTY system data. Use --only to specify
    what to export, or omit to export everything.

    Examples:
        plotty system export --only=config
        plotty system export --only=database --output-dir /tmp/backup
        plotty system export --force
    """
    try:
        # Show what will be exported
        console.print(f"[bold blue]Export:[/bold blue] {only}")
        console.print(f"[bold]Output directory:[/bold] {output_dir}")

        # Confirm unless forced
        if not force:
            if not Confirm.ask(f"Export {only}?"):
                console.print("[yellow]Export cancelled.[/yellow]")
                raise typer.Exit(0)

        # Create the backup using BackupManager
        console.print("[dim]Creating export...[/dim]")
        backup_manager = BackupManager()

        # Map export targets to backup types
        type_mapping = {
            "config": BackupType.CONFIG,
            "database": BackupType.DATABASE,
            "logs": BackupType.WORKSPACE,  # Logs are part of workspace backup
            "output": BackupType.WORKSPACE,  # Output is part of workspace backup
            "presets": BackupType.CONFIG,  # Presets are part of config backup
            "statistics": BackupType.DATABASE,  # Statistics are in database
            "all": BackupType.FULL,
        }

        backup_type = type_mapping[only]
        backup_path = backup_manager.create_backup(
            backup_type=backup_type, name=f"export_{only}"
        )

        console.print(f"[green]✓[/green] Export completed: {backup_path}")

    except Exception as e:
        console.print(f"[red]✗[/red] Export failed: {e}")
        raise typer.Exit(1)
