"""
Test driver functionality command.
"""

from __future__ import annotations

import signal
import time
from typing import Optional
import typer


def timeout_handler(signum, frame):
    """Handle timeout for driver operations."""
    raise TimeoutError("Driver operation timed out - no device responding")


def test_command(
    driver: str = typer.Argument(..., help="Driver name"),
    device_id: str = typer.Option(
        None, "--device", "-d", help="Specific device ID to test"
    ),
) -> None:
    """Test driver functionality and hardware connectivity.

    Examples:
        vfab driver test axidraw
        vfab driver test mydriver --device device1
    """
    try:
        from ...utils import error_handler
        from ...progress import show_status

        try:
            from ...drivers.registry import get_registry, initialize_registry
        except ImportError:
            from vfab.drivers.registry import get_registry, initialize_registry

        # Initialize registry to discover drivers
        initialize_registry()
        registry = get_registry()

        # Get driver class
        driver_class = registry.get_driver_class(driver.lower())
        driver_info = registry.get_driver_info(driver.lower())

        if not driver_class or not driver_info:
            available_drivers = ", ".join(registry.get_driver_names())
            raise typer.BadParameter(
                f"Unknown driver: {driver}. Available: {available_drivers}"
            )

        # Check if driver is available
        if not driver_class.is_available():
            show_status(f"❌ {driver_info.display_name} support not available", "error")
            show_status(f"💡 Install with: vfab driver install {driver}", "info")
            raise typer.Exit(1)

        show_status(f"Testing {driver_info.display_name} driver...", "info")

        # Create driver instance
        try:
            driver_instance = driver_class()
        except Exception as e:
            show_status(f"❌ Failed to create driver instance: {e}", "error")
            raise typer.Exit(1)

        # List devices
        try:
            devices = driver_instance.list_devices()
            if not devices:
                show_status("❌ No devices found", "error")
                show_status("💡 Check connections and permissions", "info")
                raise typer.Exit(1)

            show_status(f"✅ Found {len(devices)} device(s)", "success")
            for device in devices:
                device_name = device.get("name", "Unknown")
                device_id_str = device.get("id", "Unknown")
                show_status(f"  • {device_name} ({device_id_str})", "info")

        except Exception as e:
            show_status(f"⚠️  Could not list devices: {e}", "warning")

        # Test driver functionality
        show_status("Running driver tests...", "info")
        try:
            test_result = driver_instance.test()

            if test_result.success:
                show_status("✅ Driver test passed", "success")
                if test_result.message:
                    show_status(f"  {test_result.message}", "info")

                if test_result.details:
                    show_status("Test details:", "info")
                    for key, value in test_result.details.items():
                        show_status(f"  {key}: {value}", "info")
            else:
                show_status("❌ Driver test failed", "error")
                if test_result.message:
                    show_status(f"  {test_result.message}", "error")
                raise typer.Exit(1)

        except Exception as e:
            show_status(f"❌ Driver test failed: {e}", "error")
            raise typer.Exit(1)

        show_status("", "info")
        show_status("🎉 All tests completed successfully!", "success")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
