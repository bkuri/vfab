"""
Device checking commands for ploTTY CLI.
"""

from __future__ import annotations

import typer

# Create device check subcommand group
device_check_app = typer.Typer(no_args_is_help=True, help="Device checking commands")


def check_plotter() -> None:
    """Check plotter readiness."""
    try:
        from ...detection import DeviceDetector
        from ...utils import error_handler
        from ...progress import show_status

        show_status("Checking plotter readiness...", "info")

        detector = DeviceDetector()
        axidraw_result = detector.detect_axidraw_devices()

        if axidraw_result["count"] > 0:
            show_status(
                f"✅ Plotter ready ({axidraw_result['count']} device(s))", "success"
            )
        else:
            show_status("❌ Plotter not ready", "error")

        show_status("✅ Plotter check completed", "success")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


def check_camera() -> None:
    """Check camera readiness."""
    try:
        from ...detection import DeviceDetector
        from ...utils import error_handler
        from ...progress import show_status

        show_status("Checking camera readiness...", "info")

        detector = DeviceDetector()
        camera_result = detector.detect_camera_devices()

        if camera_result["count"] > 0:
            show_status(
                f"✅ Camera ready ({camera_result['count']} device(s))", "success"
            )
        else:
            show_status("❌ Camera not ready", "error")

        show_status("✅ Camera check completed", "success")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


# Register device check commands
device_check_app.command("plotter", help="Check plotter readiness")(check_plotter)
device_check_app.command("camera", help="Check camera readiness")(check_camera)

__all__ = ["device_check_app"]
