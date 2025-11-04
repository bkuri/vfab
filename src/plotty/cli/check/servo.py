"""
Servo test command for ploTTY CLI.
"""

from __future__ import annotations



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
