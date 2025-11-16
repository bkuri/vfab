"""
Driver management commands for vfab CLI.

This package provides hardware driver management functionality including:
- Installation of driver support
- Driver status and information
- Hardware testing and validation
- Device detection and listing
"""

from __future__ import annotations

import typer

try:
    from .install import install_command
    from .list import list_command
    from .info import info_command
    from .test import test_command
except ImportError:
    # Handle import errors gracefully
    install_command = None
    list_command = None
    info_command = None
    test_command = None

# Create driver app
driver_app = typer.Typer(
    name="driver",
    help="Hardware driver management and installation",
    no_args_is_help=True,
)

# Add subcommands if available
if install_command:
    driver_app.command("install", help="Install driver support")(install_command)
if list_command:
    driver_app.command("list", help="List available and installed drivers")(
        list_command
    )
if info_command:
    driver_app.command("info", help="Show driver status and information")(info_command)
if test_command:
    driver_app.command("test", help="Test driver functionality")(test_command)


# Add dynamic driver commands
def add_dynamic_driver_commands() -> None:
    """Add driver-specific commands dynamically based on available drivers."""
    try:
        try:
            from ..drivers.registry import get_registry, initialize_registry
        except ImportError:
            from vfab.drivers.registry import get_registry, initialize_registry

        # Initialize registry to discover drivers
        initialize_registry()
        registry = get_registry()

        # Get available drivers
        available_drivers = registry.get_available_drivers()

        # Add driver-specific commands for each available driver
        for driver_name in available_drivers:
            driver_info = registry.get_driver_info(driver_name)
            if not driver_info:
                continue

            # Create a driver-specific sub-app
            driver_specific_app = typer.Typer(
                name=driver_name,
                help=f"{driver_info.display_name} specific commands",
                no_args_is_help=True,
            )

            # Add common driver commands with driver pre-filled
            if info_command:

                @driver_specific_app.command(
                    "info", help=f"Show {driver_info.display_name} information"
                )
                def driver_info_command(
                    verbose: bool = typer.Option(
                        False, "--verbose", "-v", help="Show detailed information"
                    ),
                ) -> None:
                    """Show driver-specific information."""
                    # Call the info command directly with pre-filled driver
                    from .info import info_command

                    info_command(driver_name, verbose)

            if test_command:

                @driver_specific_app.command(
                    "test", help=f"Test {driver_info.display_name} functionality"
                )
                def driver_test_command(
                    device_id: str = typer.Option(
                        None, "--device", "-d", help="Specific device ID to test"
                    ),
                ) -> None:
                    """Test driver-specific functionality."""
                    # Call the test command directly with pre-filled driver
                    from .test import test_command

                    test_command(driver_name, device_id)

            # Add the driver-specific app as a subcommand
            driver_app.add_typer(driver_specific_app, name=driver_name)

    except Exception as e:
        # If dynamic command creation fails, continue without them
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to create dynamic driver commands: {e}")


# Try to add dynamic commands
try:
    add_dynamic_driver_commands()
except Exception:
    # Silently continue if dynamic commands fail
    pass

__all__ = ["driver_app"]
