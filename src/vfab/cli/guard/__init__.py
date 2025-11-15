"""
Guard commands for vfab CLI.
"""

from __future__ import annotations

import typer

from .list import list_guards
from .check import check_guards
from .validate import validate_transition

# Create guard command group
guard_app = typer.Typer(no_args_is_help=True, help="System guard commands")

# Register commands
guard_app.command("list")(list_guards)
guard_app.command("check")(check_guards)
guard_app.command("validate")(validate_transition)

__all__ = ["guard_app"]
