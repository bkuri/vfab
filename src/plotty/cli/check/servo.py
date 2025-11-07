"""
Servo test command for ploTTY CLI.
"""

from __future__ import annotations
import signal
import typer


def timeout_handler(signum, frame):
    """Handle timeout for servo operations."""
    raise TimeoutError("Servo operation timed out - no device responding")


def servo_test(
    penlift: int = typer.Option(
        None,
        "--penlift",
        "-p",
        help="Pen lift servo configuration (1=Default, 2=Standard, 3=Brushless). Overrides config setting.",
    )
) -> None:
    """Test servo motor operation."""
    try:
        from ...drivers.axidraw import create_manager, is_axidraw_available
        from ...utils import error_handler
        from ...progress import show_status
        from ...config import get_config

        show_status("Testing servo motor...", "info")

        if not is_axidraw_available():
            show_status("❌ AxiDraw support not available", "error")
            show_status("💡 Install with: uv pip install -e '.[axidraw]'", "info")
            return

        # Get configuration for penlift setting
        config = get_config()

        # Use command-line option if provided, otherwise use config
        if penlift is not None:
            penlift_setting = penlift
            source = "command line"
        else:
            penlift_setting = config.device.penlift
            source = "config"

        penlift_descriptions = {
            1: "Default for AxiDraw model",
            2: "Standard servo (lowest connector position)",
            3: "Brushless servo (3rd position up)",
        }
        penlift_desc = penlift_descriptions.get(
            penlift_setting, f"Custom ({penlift_setting})"
        )

        # Set a timeout for hardware operations
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout

        try:
            manager = create_manager()
            show_status(
                f"Attempting to connect to AxiDraw with penlift={penlift_setting} ({penlift_desc}) [{source}]...",
                "info",
            )

            # Connect in interactive mode for servo testing
            if not manager.connect():
                raise Exception("Failed to connect to AxiDraw")

            show_status("✓ Connected to AxiDraw", "success")

            # Set penlift option after connecting
            manager.ad.options.penlift = penlift_setting
            manager.ad.update()

            # Test servo up/down using interactive mode
            show_status("Testing servo up/down cycle...", "info")
            manager.pen_up()
            manager.pen_down()

            manager.disconnect()
            signal.alarm(0)  # Cancel timeout

            show_status(
                f"✓ Servo cycle completed with penlift={penlift_setting}", "success"
            )
            show_status("✅ Servo test completed successfully", "success")

        except TimeoutError:
            signal.alarm(0)  # Cancel timeout
            show_status(
                "⚠️  Servo test timed out - no AxiDraw device responding", "warning"
            )
            show_status("💡 Connect an AxiDraw device to test servo operation", "info")

    except Exception as e:
        from ...utils import error_handler

        signal.alarm(0)  # Ensure timeout is cancelled
        error_handler.handle(e)
