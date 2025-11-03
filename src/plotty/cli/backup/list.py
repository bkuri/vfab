"""
Backup listing command for ploTTY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from ...backup import BackupConfig, BackupManager
from ..status.output import get_output_manager

list_app = typer.Typer(name="list", help="List available backups", no_args_is_help=True)


@list_app.command()
def backups(
    backup_dir: Optional[str] = typer.Option(
        None, "--backup-dir", "-b", help="Backup directory path"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
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
            if json_output:
                typer.echo("[]")
            else:
                typer.echo("# Backup Listing")
                typer.echo()
                typer.echo("No backups found")
            return

        # Prepare data
        headers = ["Name", "Type", "Created", "Size", "Compression", "Files"]
        rows = []

        for backup in backups:
            created_str = backup["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            size_str = f"{backup['size'] / (1024 * 1024):.1f}MB"

            rows.append(
                [
                    backup["file"],
                    backup["type"],
                    created_str,
                    size_str,
                    backup["compression"],
                    str(backup["total_files"]),
                ]
            )

        # Output in requested format
        if json_output:
            import json

            typer.echo(json.dumps(backups, indent=2, default=str))
        elif csv_output:
            import csv
            import sys

            writer = csv.writer(sys.stdout)
            writer.writerow(headers)
            writer.writerows(rows)
        else:
            # Rich table output (default)
            output = get_output_manager()

            # Build markdown content
            markdown_content = output.print_table_markdown(
                title=f"Backup Listing ({len(backups)} backups)",
                headers=headers,
                rows=rows,
            )

            # Output using the manager
            output.print_markdown(
                content=markdown_content,
                json_data={"backups": backups},
                json_output=json_output,
                csv_output=csv_output,
            )

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
