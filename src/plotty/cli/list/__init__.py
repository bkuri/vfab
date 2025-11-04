"""
Configuration management commands for ploTTY CLI.
"""

from __future__ import annotations

import typer

from .pen_management import pen_list
from .paper_management import paper_list
from .session_management import session_reset
from .presets import list_plot_presets
from ..guard.list import list_guards

# Create list command group
list_app = typer.Typer(no_args_is_help=True, help="List and manage resources")

# Register pen management commands
list_app.command("pens")(pen_list)

# Register paper management commands
list_app.command("papers")(paper_list)

# Register presets command
list_app.command("presets")(list_plot_presets)

# Register session management commands
list_app.command("session")(session_reset)

# Register guard listing
list_app.command("guards")(list_guards)

__all__ = ["list_app"]
