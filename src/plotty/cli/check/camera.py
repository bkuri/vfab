"""
Camera test command for ploTTY CLI.
"""

from __future__ import annotations



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
