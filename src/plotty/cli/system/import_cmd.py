"""
System import command for ploTTY CLI.

Provides simplified import functionality for restoring backups.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from rich.prompt import Confirm

from plotty.backup import BackupManager

# Create console for output
console = Console()


def import_command(
    backup_file: Path = typer.Argument(
        ...,
        help="Path to backup file to import from",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompts"
    ),
) -> None:
    """Import system data from a backup file.

    This command restores ploTTY system data from a previously created backup.
    The operation will replace existing data with the contents of the backup.

    Examples:
        plotty system import backup_20231201_120000.tar.gz
        plotty system import /tmp/backup/plotty_backup.tar.gz --force
    """
    try:
        # Validate backup file
        if not backup_file.exists():
            console.print(f"[red]✗[/red] Backup file not found: {backup_file}")
            raise typer.Exit(1)

        if backup_file.suffix not in [".tar.gz", ".tgz"]:
            console.print(f"[red]✗[/red] Invalid backup file format: {backup_file}")
            console.print("[dim]Expected .tar.gz or .tgz file[/dim]")
            raise typer.Exit(1)

        # Show what will be imported
        console.print(f"[bold blue]Import:[/bold blue] {backup_file}")
        console.print(f"[bold]Size:[/bold] {backup_file.stat().st_size:,} bytes")

        # Confirm unless forced
        if not force:
            console.print(
                "[yellow]⚠[/yellow] This will replace existing data with backup contents"
            )
            if not Confirm.ask("Continue with import?"):
                console.print("[yellow]Import cancelled.[/yellow]")
                raise typer.Exit(0)

        # Restore the backup using BackupManager
        console.print("[dim]Restoring from backup...[/dim]")
        backup_manager = BackupManager()
        backup_manager.restore_backup(backup_file)

        console.print("[green]✓[/green] Import completed successfully")
        console.print(
            "[dim]You may need to restart ploTTY for changes to take effect[/dim]"
        )

    except Exception as e:
        console.print(f"[red]✗[/red] Import failed: {e}")
        raise typer.Exit(1)
