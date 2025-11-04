"""
Timing test command for ploTTY CLI.
"""

from __future__ import annotations


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
