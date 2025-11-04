"""
SOS (Save Our System) recovery commands for ploTTY CLI.

This module provides the main entry point for recovery commands,
delegating to specialized modules for different aspects of recovery.
"""

from __future__ import annotations

import typer

# Import specialized modules
from .listing import list_recoverable, job_status
from .operations import recover_job, recover_all_jobs_cmd, cleanup_journal
from ..core import get_available_job_ids

# Create sos command group
sos_app = typer.Typer(no_args_is_help=True, help="Recovery and rescue commands")


def complete_job_id(incomplete: str):
    """Autocomplete for job IDs."""
    return [
        job_id for job_id in get_available_job_ids() if job_id.startswith(incomplete)
    ]


# Listing commands
sos_app.command("list")(list_recoverable)
sos_app.command("status")(job_status)

# Operations commands
sos_app.command()(recover_job)
sos_app.command("recover-all")(recover_all_jobs_cmd)
sos_app.command("cleanup")(cleanup_journal)

__all__ = ["sos_app"]
