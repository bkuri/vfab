"""
Configuration management commands for ploTTY CLI.
"""

from __future__ import annotations

import typer

from .pen_management import pen_list, pen_add, pen_remove
from .paper_management import paper_list, paper_add, paper_remove
from .session_management import session_reset
from .setup_wizard import setup, check_config
from .presets import list_plot_presets

# Create config command group
config_app = typer.Typer(no_args_is_help=True, help="Configuration commands")

# Register pen management commands
config_app.command("pens")(pen_list)
config_app.command("pen-add")(pen_add)
config_app.command("pen-remove")(pen_remove)

# Register paper management commands
config_app.command("paper-list")(paper_list)
config_app.command("paper-add")(paper_add)
config_app.command("paper-remove")(paper_remove)

# Register session management commands
config_app.command("session-reset")(session_reset)

# Register setup wizard commands
config_app.command("setup")(setup)
config_app.command("check")(check_config)

# Register presets command
config_app.command("presets")(list_plot_presets)

__all__ = ["config_app"]
