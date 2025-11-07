"""
Servo test command for ploTTY CLI.
"""

from __future__ import annotations
import signal
import sys
import typer


def timeout_handler(signum, frame):
    """Handle timeout for servo operations."""
    raise TimeoutError("Servo operation timed out - no device responding")


def servo_test(
    penlift: int = typer.Option(
        None,
        "--penlift",
        "-p",
        help="Pen lift servo configuration (1=Default, 2=Standard, 3=Brushless). Overrides config setting."
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
            3: "Brushless servo (3rd position up)"
        }
        penlift_desc = penlift_descriptions.get(penlift_setting, f"Custom ({penlift_setting})")

        # Set a timeout for hardware operations
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout

        try:
            manager = create_manager()
            show_status(f"Attempting to connect to AxiDraw with penlift={penlift_setting} ({penlift_desc}) [{source}]...", "info")
            
            # Test servo up/down using cycle mode with configured penlift setting
            result = manager.cycle_pen(penlift=penlift_setting)
            signal.alarm(0)  # Cancel timeout
            
            if result["success"]:
                show_status(f"✓ Servo cycle completed with penlift={penlift_setting}", "success")
            else:
                error_msg = result.get('error', 'Unknown error')
                show_status(f"Error details: {error_msg}", "error")
                if "no AxiDraw found" in error_msg.lower() or "device" in error_msg.lower():
                    show_status("⚠️  No AxiDraw device found - servo test requires hardware", "warning")
                else:
                    raise Exception(f"Servo cycle failed: {error_msg}")
            
            show_status("✅ Servo test completed successfully", "success")
            
        except TimeoutError:
            signal.alarm(0)  # Cancel timeout
            show_status("⚠️  Servo test timed out - no AxiDraw device responding", "warning")
            show_status("💡 Connect an AxiDraw device to test servo operation", "info")

    except Exception as e:
        from ...utils import error_handler
        signal.alarm(0)  # Ensure timeout is cancelled
        error_handler.handle(e)
