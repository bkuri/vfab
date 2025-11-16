"""
Show driver status and information command.
"""

from __future__ import annotations

import typer


def info_command(
    driver: str = typer.Argument(..., help="Driver name"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information"
    ),
) -> None:
    """Show detailed status and information for a specific driver.

    Examples:
        vfab driver info axidraw
        vfab driver info mydriver --verbose
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

        # Get driver info
        driver_info = registry.get_driver_info(driver.lower())
        driver_class = registry.get_driver_class(driver.lower())
        driver_source = registry.get_driver_source(driver.lower())

        if not driver_info or not driver_class:
            available_drivers = ", ".join(registry.get_driver_names())
            raise typer.BadParameter(
                f"Unknown driver: {driver}. Available: {available_drivers}"
            )

        show_status(f"Getting {driver_info.display_name} driver information...", "info")

        # Display information
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table

            console = Console()

            # Check status
            try:
                is_available = driver_class.is_available()
                install_status = driver_class.get_installation_status()
                status_text = install_status.value.replace("_", " ").title()
            except Exception:
                is_available = False
                status_text = "Unknown"

            # Summary panel
            status_icon = "✅" if is_available else "❌"
            summary = f"""
Status: {status_icon} {status_text}
Type: {driver_info.driver_type.value}
Version: {driver_info.version}
Author: {driver_info.author}
            """.strip()

            border_style = "green" if is_available else "red"
            console.print(
                Panel(
                    summary,
                    title=f"🔧 {driver_info.display_name} Driver Status",
                    border_style=border_style,
                )
            )

            if verbose:
                # Detailed information
                console.print()
                console.print("📋 Detailed Information:", style="bold")

                details_table = Table()
                details_table.add_column("Property", style="cyan")
                details_table.add_column("Value", style="white")

                details_table.add_row("Name", driver_info.name)
                details_table.add_row("Display Name", driver_info.display_name)
                details_table.add_row("Version", driver_info.version)
                details_table.add_row("Type", driver_info.driver_type.value)
                details_table.add_row("Author", driver_info.author)
                details_table.add_row(
                    "Source", driver_source.value if driver_source else "unknown"
                )

                if driver_info.website:
                    details_table.add_row("Website", driver_info.website)

                details_table.add_row("Description", driver_info.description)

                console.print(details_table)

                # Capabilities
                if driver_info.capabilities:
                    console.print()
                    console.print("🔧 Capabilities:", style="bold")
                    for cap in driver_info.capabilities:
                        req_marker = " (required)" if cap.required else ""
                        console.print(f"  • {cap.name}{req_marker}", style="cyan")
                        console.print(f"    {cap.description}", style="dim")

                # Dependencies
                if driver_info.dependencies:
                    console.print()
                    console.print("📦 Dependencies:", style="bold")
                    for dep in driver_info.dependencies:
                        console.print(f"  • {dep}", style="cyan")

                # Test driver if available
                if is_available:
                    console.print()
                    console.print("🧪 Testing driver...", style="bold")
                    try:
                        driver_instance = driver_class()
                        test_result = driver_instance.test()
                        if test_result.success:
                            console.print("✅ Driver test passed", style="green")
                            if test_result.message:
                                console.print(f"  {test_result.message}", style="dim")
                        else:
                            console.print("❌ Driver test failed", style="red")
                            if test_result.message:
                                console.print(f"  {test_result.message}", style="red")
                    except Exception as e:
                        console.print(f"❌ Driver test failed: {e}", style="red")

        except ImportError:
            # Fallback to plain text
            print(f"{driver_info.display_name} Driver Status")
            print("=" * 30)
            print(f"Name: {driver_info.name}")
            print(f"Version: {driver_info.version}")
            print(f"Type: {driver_info.driver_type.value}")
            print(f"Author: {driver_info.author}")
            print(f"Description: {driver_info.description}")

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
