"""
Device test subcommands for ploTTY CLI.

This module provides specific test commands for different device components.
"""

from __future__ import annotations

import typer

# Create test subcommand group
test_app = typer.Typer(no_args_is_help=True, help="Device testing commands")


def servo_test() -> None:
    """Test servo motor operation."""
    try:
        from ...drivers.axidraw import AxiDrawDriver
        from ...utils import error_handler
        from ...progress import show_status

        show_status("Testing servo motor...", "info")

        driver = AxiDrawDriver()
        # Test servo up/down
        driver.pen_up()
        show_status("✓ Servo up position", "success")

        driver.pen_down()
        show_status("✓ Servo down position", "success")

        driver.pen_up()
        show_status("✅ Servo test completed successfully", "success")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


def camera_test() -> None:
    """Test camera connectivity and capture."""
    try:
        from ...detection import DeviceDetector
        from ...utils import error_handler
        from ...progress import show_status

        show_status("Testing camera...", "info")

        detector = DeviceDetector()
        result = detector.detect_camera_devices()

        if result["count"] > 0:
            show_status(
                f"✅ Camera test passed - {result['count']} camera(s) found", "success"
            )
        else:
            show_status("❌ Camera test failed - no cameras found", "error")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


def timing_test() -> None:
    """Test device timing and synchronization."""
    try:
        from ...drivers.axidraw import AxiDrawDriver
        from ...utils import error_handler
        from ...progress import show_status
        import time

        show_status("Testing device timing...", "info")

        driver = AxiDrawDriver()

        # Test movement timing
        start_time = time.time()
        driver.move(0, 0)
        driver.move(100, 100)
        driver.move(0, 0)
        end_time = time.time()

        duration = end_time - start_time
        show_status(f"✓ Movement test completed in {duration:.2f} seconds", "success")

        show_status("✅ Timing test completed successfully", "success")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)


# Register test subcommands
test_app.command("servo", help="Test servo motor operation")(servo_test)
test_app.command("camera", help="Test camera connectivity")(camera_test)
test_app.command("timing", help="Test device timing")(timing_test)

__all__ = ["test_app"]
