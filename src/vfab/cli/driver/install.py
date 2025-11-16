"""
Install driver support command.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import typer


def install_command(
    driver: str = typer.Argument(..., help="Driver name"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force reinstall even if already available"
    ),
) -> None:
    """Install driver support for hardware devices.

    Examples:
        vfab driver install axidraw
        vfab driver install mydriver --force
    """
    try:
        from ...utils import error_handler
        from ...progress import show_status

        try:
            from ...drivers.registry import get_registry, initialize_registry
        except ImportError:
            from vfab.drivers.registry import get_registry, initialize_registry

        # Initialize registry to discover available drivers
        initialize_registry()
        registry = get_registry()

        # Validate driver name
        driver_class = registry.get_driver_class(driver.lower())
        if not driver_class:
            available_drivers = ", ".join(registry.get_driver_names())
            raise typer.BadParameter(
                f"Unknown driver: {driver}. Available: {available_drivers}"
            )

        # Check if already available
        if driver_class.is_available() and not force:
            show_status(f"✓ {driver} support is already installed", "success")
            show_status("💡 Use --force to reinstall", "info")
            return

        # Check if we're in a vfab project
        if not Path("pyproject.toml").exists():
            raise typer.BadParameter(
                "Not in a vfab project directory. Run from project root."
            )

        show_status(f"Installing {driver} support...", "info")

        # Install using driver's install method
        try:
            success = driver_class.install(force=force)
            if success:
                show_status(f"✓ {driver} support installed successfully", "success")

                # Test the installation
                if driver_class.is_available():
                    show_status(
                        "✓ Installation verified - driver is available", "success"
                    )
                else:
                    show_status(
                        "⚠ Installation completed but driver not available", "warning"
                    )
                    show_status(
                        "💡 You may need to restart your shell or check your PATH",
                        "info",
                    )
            else:
                show_status(f"❌ Failed to install {driver} support", "error")
                raise typer.Exit(1)

        except Exception as e:
            show_status(f"❌ Failed to install {driver} support", "error")
            show_status(f"Error: {str(e)}", "error")
            raise typer.Exit(1)

    except Exception as e:
        from ...utils import error_handler

        error_handler.handle(e)
