"""
Enhanced check commands for ploTTY CLI.

This module provides comprehensive checking and testing commands for
system health, device validation, and job verification.
"""

from __future__ import annotations

import typer
from pathlib import Path

# Import check functions
from .servo import servo_test
from .camera import camera_test
from .timing import timing_test
from .device import device_check_app
from .job import check_job

# Create check command group
check_app = typer.Typer(no_args_is_help=True, help="System and device checking")

# Add device subcommand group
check_app.add_typer(device_check_app, name="plotter", help="Plotter checking commands")

# Register test commands
check_app.command("servo", help="Test servo motor operation")(servo_test)
check_app.command("camera", help="Test camera connectivity")(camera_test)
check_app.command("timing", help="Test device timing")(timing_test)

# Register job checking
check_app.command("job", help="Check job status and guards")(check_job)


def run_general_check() -> None:
    """Run general system health check."""
    try:
        from ...detection import DeviceDetector
        from ...config import load_config
        from ...utils import error_handler
        from ...progress import show_status

        show_status("Running general system check...", "info")

        # Check configuration
        try:
            cfg = load_config(None)
            show_status("✓ Configuration loaded successfully", "success")
        except Exception as e:
            show_status(f"✗ Configuration error: {e}", "error")

        # Check workspace
        try:
            workspace = Path(cfg.workspace)
            if workspace.exists():
                show_status(f"✓ Workspace accessible: {workspace}", "success")
            else:
                show_status(f"✗ Workspace not found: {workspace}", "error")
        except Exception as e:
            show_status(f"✗ Workspace check failed: {e}", "error")

        # Check devices
        try:
            detector = DeviceDetector()

            # Check plotter
            axidraw_result = detector.detect_axidraw_devices()
            if axidraw_result["count"] > 0:
                show_status(
                    f"✓ Plotter ready ({axidraw_result['count']} device(s))", "success"
                )
            else:
                show_status("✗ Plotter not ready", "warning")

            # Check camera
            camera_result = detector.detect_camera_devices()
            if camera_result["count"] > 0:
                show_status(
                    f"✓ Camera ready ({camera_result['count']} device(s))", "success"
                )
            else:
                show_status("✗ Camera not ready", "warning")

        except Exception as e:
            show_status(f"✗ Device check failed: {e}", "error")

        show_status("✅ General system check completed", "success")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


@check_app.callback()
def check_callback(ctx: typer.Context):
    """System health and device checking."""
    if ctx.invoked_subcommand is None:
        run_general_check()


__all__ = ["check_app"]
