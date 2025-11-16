"""
List available and installed drivers command.
"""

from __future__ import annotations


def list_command() -> None:
    """List available and installed hardware drivers.

    Examples:
        vfab driver list
    """
    try:
        from ...utils import error_handler
        from ...progress import show_status

        try:
            from ...drivers.registry import get_registry, initialize_registry
            from ...drivers.base import DriverType
        except ImportError:
            from vfab.drivers.registry import get_registry, initialize_registry
            from vfab.drivers.base import DriverType

        # Initialize registry to discover drivers
        initialize_registry()
        registry = get_registry()

        show_status("Scanning for drivers...", "info")

        # Get all drivers
        all_drivers = registry.get_driver_names()
        available_drivers = registry.get_available_drivers()
        installed_drivers = registry.get_installed_drivers()

        if not all_drivers:
            show_status("No drivers found", "warning")
            return

        # Display results
        try:
            from rich.console import Console
            from rich.table import Table

            console = Console()
            console.print("🔧 Hardware Drivers Status")
            console.print()

            table = Table()
            table.add_column("Driver", style="cyan")
            table.add_column("Type", style="white")
            table.add_column("Status", style="yellow")
            table.add_column("Install Command", style="green")

            # Add rows for each driver
            for driver_name in sorted(all_drivers):
                driver_info = registry.get_driver_info(driver_name)
                display_name = driver_info.display_name if driver_info else driver_name
                driver_type = (
                    driver_info.driver_type.value if driver_info else "unknown"
                )

                if driver_name in available_drivers:
                    status = "✅ Available"
                    install_cmd = "Already installed"
                elif driver_name in installed_drivers:
                    status = "⚠️ Installed but not available"
                    install_cmd = f"vfab driver install {driver_name} --force"
                else:
                    status = "❌ Not installed"
                    install_cmd = f"vfab driver install {driver_name}"

                table.add_row(display_name, driver_type, status, install_cmd)

            console.print(table)

        except ImportError:
            # Fallback to plain text
            print("Hardware Drivers Status")
            print("=" * 25)
            for driver_name in sorted(all_drivers):
                driver_info = registry.get_driver_info(driver_name)
                display_name = driver_info.display_name if driver_info else driver_name
                driver_type = (
                    driver_info.driver_type.value if driver_info else "unknown"
                )

                if driver_name in available_drivers:
                    status = "Available"
                elif driver_name in installed_drivers:
                    status = "Installed but not available"
                else:
                    status = "Not installed"

                print(f"{display_name} ({driver_type}): {status}")

        show_status(
            "💡 Use 'vfab driver info <driver>' for detailed information", "info"
        )

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
