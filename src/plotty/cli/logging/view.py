"""
Log viewing command for ploTTY.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ...config import load_config
from ...logging import (
    LogLevel,
    LogFormat,
    get_logger,
)

console = Console()


def view_logs(
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    level: Optional[LogLevel] = typer.Option(
        None, "--level", "-l", help="Filter by log level"
    ),
    job_id: Optional[str] = typer.Option(None, "--job", "-j", help="Filter by job ID"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
) -> None:
    """View log file contents with optional filtering."""
    try:
        config = load_config(config_path)
        logger = get_logger("cli")

        if not config.logging.enabled:
            console.print("[red]Logging is disabled in configuration[/red]")
            raise typer.Exit(1)

        log_file = Path(config.logging.log_file)
        if not log_file.exists():
            console.print(f"[red]Log file not found: {log_file}[/red]")
            console.print("[yellow]Try running some ploTTY commands first[/yellow]")
            raise typer.Exit(1)

        if follow:
            console.print(f"[green]Following log file: {log_file}[/green]")
            console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")

            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    # Go to end of file
                    f.seek(0, 2)

                    while True:
                        line = f.readline()
                        if line:
                            if _should_show_line(
                                line, level, job_id, config.logging.format
                            ):
                                console.print(line.rstrip())
                        else:
                            import time

                            time.sleep(0.1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped following logs[/yellow]")
        else:
            # Show last N lines
            with open(log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()

                # Filter lines
                filtered_lines = [
                    line
                    for line in all_lines
                    if _should_show_line(line, level, job_id, config.logging.format)
                ]

                # Show last N lines
                show_lines = (
                    filtered_lines[-lines:]
                    if len(filtered_lines) > lines
                    else filtered_lines
                )

                if show_lines:
                    console.print(
                        f"[green]Showing {len(show_lines)} lines from {log_file}[/green]\n"
                    )
                    for line in show_lines:
                        console.print(line.rstrip())
                else:
                    console.print("[yellow]No matching log entries found[/yellow]")

    except Exception as e:
        from ...utils import error_handler

        # Try to log if logger is available, but don't let logging errors cause issues
        try:
            logger = get_logger("cli")
            logger.error(f"Failed to view logs: {e}")
        except Exception:
            pass
        error_handler.handle(e)


def _should_show_line(
    line: str,
    level_filter: Optional[LogLevel],
    job_filter: Optional[str],
    log_format: LogFormat,
) -> bool:
    """Check if a log line should be shown based on filters."""
    if not level_filter and not job_filter:
        return True

    # Parse based on format
    if log_format == LogFormat.JSON:
        try:
            log_data = json.loads(line)

            # Level filter
            if level_filter:
                log_level = log_data.get("level", "INFO")
                level_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                if level_order.index(log_level) < level_order.index(level_filter.value):
                    return False

            # Job filter
            if job_filter:
                if "extra" in log_data and "job_id" in log_data["extra"]:
                    if log_data["extra"]["job_id"] != job_filter:
                        return False
                elif "job_id" in log_data:
                    if log_data["job_id"] != job_filter:
                        return False
                else:
                    return False

            return True

        except (json.JSONDecodeError, KeyError):
            # If we can't parse, show it
            return True
    else:
        # Text format parsing
        line_lower = line.lower()

        # Level filter
        if level_filter:
            if level_filter.value.lower() not in line_lower:
                # Check if it's a higher level
                level_order = ["debug", "info", "warning", "error", "critical"]
                current_level_index = 0
                for i, level_name in enumerate(level_order):
                    if level_name in line_lower:
                        current_level_index = i
                        break

                filter_index = level_order.index(level_filter.value.lower())
                if current_level_index < filter_index:
                    return False

        # Job filter
        if job_filter and job_filter.lower() not in line_lower:
            return False

        return True
