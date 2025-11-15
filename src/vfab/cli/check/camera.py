"""
Camera test command for vfab CLI.
"""

from __future__ import annotations


def camera_test() -> None:
    """Test camera connectivity and capture."""
    try:
        from ...detection import DeviceDetector
        from ...utils import error_handler
        from ...progress import show_status
        from ...config import load_config

        # Check if camera is enabled in configuration
        try:
            cfg = load_config(None)
            if not cfg.camera.enabled:
                show_status(
                    "  Camera test skipped - Camera disabled in configuration",
                    "warning",  # Using warning for appropriate visibility
                )
                return
        except Exception:
            # If config can't be loaded, proceed with hardware check
            pass

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
