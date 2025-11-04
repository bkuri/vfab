"""
Device management commands for ploTTY CLI.

This module provides commands for device testing and interactive plotting sessions.
"""

from __future__ import annotations

import typer

# Create device command group
device_app = typer.Typer(no_args_is_help=True, help="Device management commands")


def check(
    component: str = typer.Argument(
        "all", help="Component to check (plotter/camera/all)"
    ),
) -> None:
    """Check device readiness."""
    try:
        from ...detection import DeviceDetector
        from ...utils import error_handler
        from ...progress import show_status

        show_status("Checking device readiness...", "info")

        detector = DeviceDetector()

        if component in ["all", "plotter"]:
            axidraw_result = detector.detect_axidraw_devices()
            if axidraw_result["count"] > 0:
                show_status(
                    f"✅ Plotter ready ({axidraw_result['count']} device(s))", "success"
                )
            else:
                show_status("❌ Plotter not ready", "error")

        if component in ["all", "camera"]:
            camera_result = detector.detect_camera_devices()
            if camera_result["count"] > 0:
                show_status(
                    f"✅ Camera ready ({camera_result['count']} device(s))", "success"
                )
            else:
                show_status("❌ Camera not ready", "error")

        show_status("✅ Device readiness check completed", "success")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


# Register check command
device_app.command("check", help="Check device readiness")(check)

__all__ = ["device_app"]
