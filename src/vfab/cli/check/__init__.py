"""
Enhanced check commands for vfab CLI.

This module provides comprehensive checking and testing commands for
system health, device validation, and job verification.
"""

from __future__ import annotations

import typer

# Import check functions
from .servo import servo_test
from .camera import camera_test
from .timing import timing_test
from .job import check_job
from .ready import check_ready
from ..list.setup_wizard import check_config
from .self import check_self

# Create check command group
check_app = typer.Typer(no_args_is_help=True, help="System and device checking")

# Register check commands
check_app.command("camera", help="Test camera connectivity")(camera_test)
check_app.command("config", help="Check configuration")(check_config)
check_app.command("job", help="Check job status and guards")(check_job)
check_app.command("ready", help="Check overall system readiness")(check_ready)
check_app.command("self", help="Run comprehensive self-tests")(check_self)
check_app.command("servo", help="Test servo motor operation")(servo_test)
check_app.command("timing", help="Test device timing")(timing_test)


__all__ = ["check_app"]
