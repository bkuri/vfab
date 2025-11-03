"""
Plotting commands for ploTTY CLI.

This module provides commands for plotting jobs, interactive sessions,
presets management, and device testing.
"""

from __future__ import annotations

import typer

from .plot import plot_job
from .interactive import interactive_session
from .presets import list_plot_presets
from .pen_test import test_pen_operation

# Create plot command group
plot_app = typer.Typer(no_args_is_help=True, help="Plotting commands")

# Register commands
plot_app.command("plot")(plot_job)
plot_app.command("interactive")(interactive_session)
plot_app.command("presets")(list_plot_presets)
plot_app.command("pen-test")(test_pen_operation)

__all__ = ["plot_app"]
