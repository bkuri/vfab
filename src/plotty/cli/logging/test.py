"""
Logging test command for ploTTY.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from ...config import load_config
from ...logging_config import (
    LogLevel,
    LogOutput,
    get_logger,
)

console = Console()


def test_logging(
    level: LogLevel = typer.Option(
        LogLevel.INFO, "--level", "-l", help="Log level to test"
    ),
    count: int = typer.Option(5, "--count", "-n", help="Number of test messages"),
    config_path: Optional[str] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
) -> None:
    """Send test log messages to verify logging configuration."""
    try:
        config = load_config(config_path)
        logger = get_logger("test")

        console.print(
            f"[green]Testing logging with {count} messages at {level.value} level[/green]\n"
        )

        test_messages = [
            ("System startup completed", {"component": "system", "version": "1.0"}),
            (
                "Device connected successfully",
                {"device_type": "AxiDraw", "device_id": "test-001"},
            ),
            ("Job processing started", {"job_id": "test-job-001", "job_type": "plot"}),
            ("Performance metrics", {"duration": 1.23, "lines_plotted": 1000}),
            ("User action completed", {"action": "test", "user": "test-user"}),
        ]

        for i in range(count):
            message, context = test_messages[i % len(test_messages)]

            if level == LogLevel.DEBUG:
                logger.debug(f"Test {i + 1}: {message}", **context)
            elif level == LogLevel.INFO:
                logger.info(f"Test {i + 1}: {message}", **context)
            elif level == LogLevel.WARNING:
                logger.warning(f"Test {i + 1}: {message}", **context)
            elif level == LogLevel.ERROR:
                logger.error(f"Test {i + 1}: {message}", **context)
            elif level == LogLevel.CRITICAL:
                logger.critical(f"Test {i + 1}: {message}", **context)

        console.print(f"[green]✓ Sent {count} test log messages[/green]")

        if config.logging.output in [LogOutput.FILE, LogOutput.BOTH]:
            console.print(f"[blue]Check log file: {config.logging.log_file}[/blue]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
