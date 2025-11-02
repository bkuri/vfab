"""
Logging configuration command for ploTTY.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ...config import load_config
from ...logging import (
    LogLevel,
    LogFormat,
    LogOutput,
    get_logger,
    logging_manager,
)

console = Console()


def configure_logging(
    level: Optional[LogLevel] = typer.Option(
        None, "--level", "-l", help="Set log level"
    ),
    format: Optional[LogFormat] = typer.Option(
        None, "--format", "-f", help="Set log format"
    ),
    output: Optional[LogOutput] = typer.Option(
        None, "--output", "-o", help="Set output destination"
    ),
    enabled: Optional[bool] = typer.Option(
        None, "--enabled/--disabled", help="Enable/disable logging"
    ),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
) -> None:
    """Configure logging settings."""
    try:
        config = load_config(config_path)
        logger = get_logger("cli")

        # Update configuration
        changes = []

        if level is not None:
            config.logging.level = level
            changes.append(f"Level: {level.value}")

        if format is not None:
            config.logging.format = format
            changes.append(f"Format: {format.value}")

        if output is not None:
            config.logging.output = output
            changes.append(f"Output: {output.value}")

        if enabled is not None:
            config.logging.enabled = enabled
            changes.append(f"Enabled: {enabled}")

        if not changes:
            console.print("[yellow]No changes specified[/yellow]")
            console.print("Use --help to see available options")
            raise typer.Exit(0)

        # Save configuration
        config_file = Path(config_path or "config/config.yaml")
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict and save
        config_dict = config.model_dump()

        import yaml

        with open(config_file, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)

        # Update logging manager
        logging_manager.update_config(config.logging)

        console.print("[green]Updated logging configuration:[/green]")
        for change in changes:
            console.print(f"  • {change}")

        console.print(f"[blue]Configuration saved to: {config_file}[/blue]")

    except Exception as e:
        from ...utils import error_handler

        # Try to log if logger is available, but don't let logging errors cause issues
        try:
            logger = get_logger("cli")
            logger.error(f"Failed to configure logging: {e}")
        except Exception:
            pass
        error_handler.handle(e)
