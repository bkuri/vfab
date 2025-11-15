"""
System export command for vfab CLI.

Provides simplified export functionality with --only flag for specific data types.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from rich.console import Console

from vfab.backup import BackupManager, BackupType


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
    apply: bool = typer.Option(
        False, "--apply", help="Actually perform the export (default is dry-run)"
    ),
) -> None:
    """Export system data and configurations.

    This command creates backups of vfab system data. Use --only to specify
    what to export, or omit to export everything.

    Examples:
        vfab system export --only=config              # Dry run export config
        vfab system export --only=database --apply    # Actually export database
        vfab system export --apply                    # Export everything
    """
    try:
        # Show what will be exported
        console.print(f"[bold blue]Export:[/bold blue] {only}")
        console.print(f"[bold]Output directory:[/bold] {output_dir}")

        # Confirm unless apply is used
        if not apply:
            console.print("[dim]Dry run mode - use --apply to actually export[/dim]")
            console.print(f"[yellow]Would export {only} to {output_dir}[/yellow]")
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

    except typer.Exit:
        # Re-raise typer.Exit exceptions (used for controlled exit)
        raise
    except Exception as e:
        console.print(f"[red]✗[/red] Export failed: {e}")
        raise typer.Exit(1)
