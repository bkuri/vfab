"""
Timing test command for ploTTY CLI.
"""

from __future__ import annotations
import signal
import time


def timeout_handler(signum, frame):
    """Handle timeout for timing operations."""
    raise TimeoutError("Timing operation timed out - no device responding")


def timing_test() -> None:
    """Test device timing and synchronization."""
    try:
        from ...drivers.axidraw import create_manager, is_axidraw_available
        from ...utils import error_handler
        from ...progress import show_status
        from ...config import get_config

        show_status("Testing device timing...", "info")

        if not is_axidraw_available():
            show_status("❌ AxiDraw support not available", "error")
            show_status("💡 Install with: uv pip install -e '.[axidraw]'", "info")
            return

        # Get configuration for penlift setting
        config = get_config()
        penlift_setting = config.device.penlift

        # Set a timeout for hardware operations
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)  # 15 second timeout for timing test

        try:
            manager = create_manager()
            show_status(
                f"Connecting to AxiDraw with penlift={penlift_setting}...", "info"
            )

            # Connect in interactive mode for movement testing
            if not manager.connect():
                raise Exception("Failed to connect to AxiDraw")

            show_status("✓ Connected to AxiDraw", "success")

            # Test movement timing
            show_status("Testing movement timing...", "info")
            start_time = time.time()

            # Test basic movements
            manager.move_to(0, 0)
            manager.move_to(1, 1)  # Move 1 inch in both X and Y
            manager.move_to(0, 0)

            end_time = time.time()
            duration = end_time - start_time

            manager.disconnect()
            signal.alarm(0)  # Cancel timeout

            show_status(
                f"✓ Movement test completed in {duration:.2f} seconds", "success"
            )
            show_status("✅ Timing test completed successfully", "success")

        except TimeoutError:
            signal.alarm(0)  # Cancel timeout
            show_status(
                "⚠️  Timing test timed out - no AxiDraw device responding", "warning"
            )
            show_status("💡 Connect an AxiDraw device to test timing", "info")

    except Exception as e:
        from ...utils import error_handler

        signal.alarm(0)  # Ensure timeout is cancelled
        error_handler.handle(e)
