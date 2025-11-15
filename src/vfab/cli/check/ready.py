"""
Ready check command for vfab CLI.
"""

from __future__ import annotations

import typer


def check_ready(
    component: str = typer.Argument(
        "all", help="Component to check (plotter/camera/all)"
    ),
) -> None:
    """Check overall system readiness."""
    try:
        from ...detection import DeviceDetector
        from ...utils import error_handler
        from ...progress import show_status

        show_status("Checking system readiness...", "info")

        detector = DeviceDetector()

        if component in ["all", "plotter"]:
            show_status("Checking plotter readiness...", "info")
            axidraw_result = detector.detect_axidraw_devices()
            if axidraw_result["count"] > 0:
                show_status(
                    f"✅ Plotter ready ({axidraw_result['count']} device(s))", "success"
                )
            else:
                show_status("❌ Plotter not ready", "error")

        if component in ["all", "camera"]:
            show_status("Checking camera readiness...", "info")
            camera_result = detector.detect_camera_devices()
            if camera_result["count"] > 0:
                show_status(
                    f"✅ Camera ready ({camera_result['count']} device(s))", "success"
                )
            else:
                show_status("❌ Camera not ready", "error")

        show_status("✅ System readiness check completed", "success")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


__all__ = ["check_ready"]
