"""
Logging status command for ploTTY.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import typer
from rich.console import Console

from ...config import load_config
from ...logging import (
    LogOutput,
    get_logger,
    logging_manager,
    config_from_settings,
)

console = Console()


def logging_status(
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
) -> None:
    """Show current logging configuration and status."""
    try:
        config = load_config(config_path)
        logging_config = config_from_settings(config)
        logger = get_logger("cli")

        # Prepare configuration data
        config_data = {
            "enabled": logging_config.enabled,
            "level": logging_config.level.value,
            "format": logging_config.format.value,
            "output": logging_config.output.value,
        }

        if logging_config.output in [LogOutput.FILE, LogOutput.BOTH]:
            config_data.update(
                {
                    "log_file": logging_config.log_file,
                    "max_file_size_mb": logging_config.max_file_size // (1024 * 1024),
                    "backup_count": logging_config.backup_count,
                }
            )

        # Show log files
        log_files = logging_manager.list_log_files()
        log_files_data = []

        for log_file in sorted(log_files):
            try:
                stat = log_file.stat()
                size = stat.st_size
                size_str = (
                    f"{size / 1024:.1f}KB"
                    if size < 1024 * 1024
                    else f"{size / (1024 * 1024):.1f}MB"
                )
                modified = datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                log_files_data.append(
                    {
                        "file": log_file.name,
                        "size": size_str,
                        "modified": modified,
                    }
                )
            except Exception:
                log_files_data.append(
                    {
                        "file": log_file.name,
                        "size": "Unknown",
                        "modified": "Unknown",
                    }
                )

        # Output in requested format
        if json_output:
            import json

            output_data = {
                "configuration": config_data,
                "log_files": log_files_data,
            }
            typer.echo(json.dumps(output_data, indent=2, default=str))
        elif csv_output:
            import csv
            import sys

            writer = csv.writer(sys.stdout)

            # Configuration section
            writer.writerow(["Configuration"])
            writer.writerow(["Setting", "Value"])
            for key, value in config_data.items():
                writer.writerow([key, value])
            writer.writerow([])

            # Log files section
            writer.writerow(["Log Files"])
            writer.writerow(["File", "Size", "Modified"])
            for log_file in log_files_data:
                writer.writerow(
                    [log_file["file"], log_file["size"], log_file["modified"]]
                )
        else:
            # Markdown output (default)
            typer.echo("# Logging System Status")
            typer.echo()
            typer.echo("## Configuration")
            typer.echo("| Setting | Value |")
            typer.echo("|---------|-------|")

            enabled_status = "✅ Enabled" if logging_config.enabled else "❌ Disabled"
            typer.echo(f"| Enabled | {enabled_status} |")
            typer.echo(f"| Level | {logging_config.level.value} |")
            typer.echo(f"| Format | {logging_config.format.value} |")
            typer.echo(f"| Output | {logging_config.output.value} |")

            if logging_config.output in [LogOutput.FILE, LogOutput.BOTH]:
                typer.echo(f"| Log File | {logging_config.log_file} |")
                typer.echo(
                    f"| Max Size | {logging_config.max_file_size // (1024 * 1024)}MB |"
                )
                typer.echo(f"| Backup Count | {logging_config.backup_count} |")

            typer.echo()

            if log_files_data:
                typer.echo("## Log Files")
                typer.echo("| File | Size | Modified |")
                typer.echo("|------|------|----------|")

                for log_file in log_files_data:
                    typer.echo(
                        f"| {log_file['file']} | {log_file['size']} | {log_file['modified']} |"
                    )

    except Exception as e:
        from ...utils import error_handler

        # Try to log if logger is available, but don't let logging errors cause issues
        try:
            logger = get_logger("cli")
            logger.error(f"Failed to show logging status: {e}")
        except Exception:
            pass
        error_handler.handle(e)
