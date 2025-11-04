"""
System logs management commands for ploTTY CLI.

This module provides commands for viewing and managing log files.
"""

from __future__ import annotations

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Create console for output
console = Console()


def list_logs() -> None:
    """List available log files."""
    try:
        # Look for logs in common locations
        log_locations = [
            Path("logs"),
            Path.home() / ".local" / "share" / "plotty" / "logs",
            Path("/var/log/plotty"),
        ]

        log_files = []
        for log_dir in log_locations:
            if log_dir.exists():
                log_files.extend(list(log_dir.glob("*.log*")))

        if not log_files:
            console.print("[yellow]No log files found[/yellow]")
            return

        # Create table for log files
        table = Table(title="Log Files")
        table.add_column("File", style="cyan")
        table.add_column("Size", style="magenta")
        table.add_column("Modified", style="green")

        for log_file in sorted(
            log_files, key=lambda x: x.stat().st_mtime, reverse=True
        ):
            if log_file.exists():
                stat = log_file.stat()
                size_str = f"{stat.st_size:,} bytes"
                from datetime import datetime

                modified_str = datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                table.add_row(log_file.name, size_str, modified_str)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing log files: {e}[/red]")
        raise typer.Exit(1)


def show_logs(
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
) -> None:
    """Show recent log entries."""
    try:
        # Look for main log file in common locations
        log_locations = [
            Path("logs/plotty.log"),
            Path.home() / ".local" / "share" / "plotty" / "logs" / "plotty.log",
            Path("/var/log/plotty/plotty.log"),
        ]

        main_log = None
        for log_path in log_locations:
            if log_path.exists():
                main_log = log_path
                break

        if not main_log:
            console.print("[yellow]Main log file not found[/yellow]")
            console.print("[dim]Checked locations:[/dim]")
            for log_path in log_locations:
                console.print(f"  • {log_path}")
            return

        if follow:
            console.print(f"[dim]Following {main_log}... (Ctrl+C to stop)[/dim]")
            try:
                with open(main_log, "r") as f:
                    # Go to end of file
                    f.seek(0, 2)
                    while True:
                        line = f.readline()
                        if line:
                            console.print(line.rstrip())
                        else:
                            import time

                            time.sleep(0.1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped following logs[/yellow]")
        else:
            # Show last N lines
            with open(main_log, "r") as f:
                all_lines = f.readlines()
                recent_lines = (
                    all_lines[-lines:] if len(all_lines) > lines else all_lines
                )

                for line in recent_lines:
                    console.print(line.rstrip())

    except Exception as e:
        console.print(f"[red]Error reading log file: {e}[/red]")
        raise typer.Exit(1)


def cleanup_logs(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to keep logs"),
) -> None:
    """Clean up old log files."""
    try:
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        # Look for logs in common locations
        log_locations = [
            Path("logs"),
            Path.home() / ".local" / "share" / "plotty" / "logs",
            Path("/var/log/plotty"),
        ]

        cleaned_count = 0
        for log_dir in log_locations:
            if log_dir.exists():
                for log_file in log_dir.glob("*.log*"):
                    try:
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            log_file.unlink()
                            cleaned_count += 1
                            console.print(
                                f"[dim]Removed old log: {log_file.name}[/dim]"
                            )
                    except OSError as e:
                        console.print(f"[red]Failed to remove {log_file}: {e}[/red]")

        if cleaned_count > 0:
            console.print(f"[green]✓[/green] Cleaned up {cleaned_count} old log files")
        else:
            console.print("[yellow]No old log files to clean up[/yellow]")

    except Exception as e:
        console.print(f"[red]Error during log cleanup: {e}[/red]")
        raise typer.Exit(1)


# Create logs command group
logs_app = typer.Typer(no_args_is_help=True, help="Logging system management")

# Add commands
logs_app.command("list", help="List available log files")(list_logs)
logs_app.command("cleanup", help="Clean up old log files")(cleanup_logs)
logs_app.command("show", help="Show recent log entries")(show_logs)

__all__ = ["logs_app"]
