"""
Batch operations commands for ploTTY CLI.
"""

from __future__ import annotations

import typer

from .planning import plan_all
from .plotting import plot_all
from .queue import clear_queue

# Create batch command group
batch_app = typer.Typer(help="Batch operations commands")

# Register commands
batch_app.command()(plan_all)
batch_app.command()(plot_all)
batch_app.command()(clear_queue)
