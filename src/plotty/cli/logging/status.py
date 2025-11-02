"""
Logging status command for ploTTY.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

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
) -> None:
    """Show current logging configuration and status."""
    try:
        config = load_config(config_path)
        logging_config = config_from_settings(config)
        logger = get_logger("cli")

        # Create status panel
        status_text = Text()
        status_text.append("Logging System Status\n", style="bold blue")
        status_text.append(
            f"Enabled: {logging_config.enabled}\n",
            style="green" if logging_config.enabled else "red",
        )
        status_text.append(f"Level: {logging_config.level.value}\n", style="yellow")
        status_text.append(f"Format: {logging_config.format.value}\n", style="cyan")
        status_text.append(f"Output: {logging_config.output.value}\n", style="cyan")

        if logging_config.output in [LogOutput.FILE, LogOutput.BOTH]:
            status_text.append(f"Log File: {logging_config.log_file}\n", style="blue")
            status_text.append(
                f"Max Size: {logging_config.max_file_size // (1024 * 1024)}MB\n",
                style="blue",
            )
            status_text.append(
                f"Backup Count: {logging_config.backup_count}\n", style="blue"
            )

        console.print(
            Panel(status_text, title="📊 Logging Status", border_style="blue")
        )

        # Show log files
        log_files = logging_manager.list_log_files()
        if log_files:
            console.print("\n[bold]Log Files:[/bold]")

            table = Table()
            table.add_column("File", style="cyan")
            table.add_column("Size", style="green")
            table.add_column("Modified", style="yellow")

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

                    table.add_row(str(log_file), size_str, modified)
                except OSError:
                    table.add_row(str(log_file), "Unknown", "Unknown")

            console.print(table)
        else:
            console.print("[yellow]No log files found[/yellow]")

    except Exception as e:
        from ...utils import error_handler

        # Try to log if logger is available, but don't let logging errors cause issues
        try:
            logger = get_logger("cli")
            logger.error(f"Failed to show logging status: {e}")
        except Exception:
            pass
        error_handler.handle(e)
