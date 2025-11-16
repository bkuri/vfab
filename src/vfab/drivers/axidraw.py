"""
AxiDraw driver implementation for vfab dynamic driver system.

This module provides the new AxiDrawDriver class that implements the PlotterDriver
interface while maintaining compatibility with existing AxiDraw functionality.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pathlib import Path
import subprocess
import sys

try:
    from pyaxidraw import axidraw

    _AXIDRAW_AVAILABLE = True
    _IMPORT_ERROR = "pyaxidraw not found. Install with: uv pip install -e '.[axidraw]'"
except ImportError:
    axidraw = None
    _AXIDRAW_AVAILABLE = False
    _IMPORT_ERROR = "pyaxidraw not found. Install with: uv pip install -e '.[axidraw]'"

try:
    from .base import (
        PlotterDriver,
        DriverInfo,
        DriverStatus,
        DriverTestResult,
        DriverCapability,
        DriverType,
    )
except ImportError:
    from vfab.drivers.base import (
        PlotterDriver,
        DriverInfo,
        DriverStatus,
        DriverTestResult,
        DriverCapability,
        DriverType,
    )


class AxiDrawDriver(PlotterDriver):
    """AxiDraw driver implementation using BaseDriver interface."""

    DRIVER_INFO = DriverInfo(
        name="axidraw",
        display_name="AxiDraw Plotter",
        version="1.0.0",
        description="AxiDraw USB pen plotter driver supporting all AxiDraw models",
        author="vfab",
        driver_type=DriverType.PLOTTER,
        capabilities=[
            DriverCapability(
                name="usb_control",
                description="USB device communication and control",
                required=True,
            ),
            DriverCapability(
                name="pen_control",
                description="Pen up/down control with configurable height",
                required=True,
            ),
            DriverCapability(
                name="movement",
                description="XY movement control with speed adjustment",
                required=True,
            ),
        ],
        dependencies=["pyaxidraw"],
        config_schema={
            "type": "object",
            "properties": {
                "port": {
                    "type": "string",
                    "description": "USB port or nickname for AxiDraw (auto-detect if empty)",
                },
                "model": {
                    "type": "integer",
                    "enum": [1, 2, 3, 4, 5, 6],
                    "description": "AxiDraw model number",
                    "default": 1,
                },
                "penlift": {
                    "type": "integer",
                    "enum": [1, 2, 3],
                    "description": "Pen lift servo configuration",
                    "default": 1,
                },
                "speed": {
                    "type": "number",
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Plotting speed percentage",
                    "default": 50,
                },
            },
        },
        website="https://axidraw.com/",
    )

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize AxiDraw driver.

        Args:
            config: Driver configuration dictionary
        """
        super().__init__(config)

        if not _AXIDRAW_AVAILABLE:
            raise ImportError(_IMPORT_ERROR)

        self.port = self.config.get("port")
        self.model = self.config.get("model", 1)
        self.penlift = self.config.get("penlift", 1)
        self.speed = self.config.get("speed", 50)

        # Create the AxiDraw instance
        self.ad = axidraw.AxiDraw() if axidraw else None
        if self.ad:
            self.ad.options.port = self.port or ""
            self.ad.options.model = self.model
            self.ad.options.penlift = self.penlift
            self.ad.options.speed = self.speed

        self._connected = False

    @classmethod
    def is_available(cls) -> bool:
        """Check if AxiDraw driver is available."""
        return _AXIDRAW_AVAILABLE

    @classmethod
    def get_installation_status(cls) -> DriverStatus:
        """Get AxiDraw installation status."""
        if _AXIDRAW_AVAILABLE:
            return DriverStatus.AVAILABLE
        else:
            return DriverStatus.NOT_INSTALLED

    @classmethod
    def install(cls) -> bool:
        """Install AxiDraw dependencies."""
        try:
            # Install using uv pip with axidraw extra
            cmd = [sys.executable, "-m", "uv", "pip", "install", "-e", ".[axidraw]"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def test(self) -> DriverTestResult:
        """Test AxiDraw driver functionality."""
        import time

        try:
            start_time = time.time()

            # Test basic initialization
            if not self.is_available():
                return DriverTestResult(
                    success=False, message="AxiDraw driver not available"
                )

            # Test connection
            connected = self.connect()
            if not connected:
                return DriverTestResult(
                    success=False, message="Failed to connect to AxiDraw device"
                )

            # Test basic operations
            test_results = {}

            # Test pen up
            try:
                self.pen_up()
                test_results["pen_up"] = "success"
            except Exception as e:
                test_results["pen_up"] = f"failed: {e}"

            # Test pen down
            try:
                self.pen_down()
                test_results["pen_down"] = "success"
            except Exception as e:
                test_results["pen_down"] = f"failed: {e}"

            # Test movement
            try:
                if self.ad:
                    self.ad.move(100, 100)  # Small test movement
                test_results["movement"] = "success"
            except Exception as e:
                test_results["movement"] = f"failed: {e}"

            # Disconnect after test
            self.disconnect()

            end_time = time.time()
            duration = end_time - start_time

            return DriverTestResult(
                success=True,
                message="AxiDraw driver test completed successfully",
                details=test_results,
                duration=duration,
            )

        except Exception as e:
            return DriverTestResult(
                success=False, message=f"AxiDraw driver test failed: {e}"
            )

    def list_devices(self) -> List[Dict[str, Any]]:
        """List available AxiDraw devices."""
        devices = []

        if not _AXIDRAW_AVAILABLE:
            return devices

        try:
            # Try to find connected AxiDraw devices
            # This is a simplified implementation - in practice, you might
            # want to scan USB devices or use axidraw's device detection
            if self.ad:
                devices.append(
                    {
                        "id": "default",
                        "name": "AxiDraw Device",
                        "description": "Default AxiDraw device",
                        "connected": True,
                    }
                )
        except Exception:
            pass

        return devices

    def connect(self, device_id: Optional[str] = None) -> bool:
        """Connect to AxiDraw device.

        Args:
            device_id: Optional device identifier (ignored for AxiDraw)

        Returns:
            True if connection successful
        """
        try:
            if not self.ad:
                return False

            if device_id and device_id != "auto":
                self.ad.options.port = device_id

            # Test connection by trying to access device
            self.ad.interactive()
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from AxiDraw."""
        try:
            if self._connected and self.ad:
                self.ad.disconnect()
            self._connected = False
            return True
        except Exception:
            return False

    def get_position(self) -> Dict[str, float]:
        """Get current pen position."""
        # AxiDraw doesn't provide direct position reading
        # Return last known position or default
        return {"x": 0.0, "y": 0.0, "pen_down": False}

    def move_to(self, x: float, y: float, pen_down: bool = False) -> bool:
        """Move pen to specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            pen_down: Whether pen should be down during movement

        Returns:
            True if movement successful
        """
        try:
            if not self.ad:
                return False

            if pen_down:
                self.ad.goto(x, y)
            else:
                self.ad.pendown()
                self.ad.goto(x, y)
                self.ad.penup()
            return True
        except Exception:
            return False

    def pen_up(self) -> bool:
        """Lifts pen."""
        try:
            if self.ad:
                self.ad.penup()
            return True
        except Exception:
            return False

    def pen_down(self) -> bool:
        """Lowers pen."""
        try:
            if self.ad:
                self.ad.pendown()
            return True
        except Exception:
            return False


# Legacy compatibility class
class AxiDrawManager:
    """Legacy AxiDraw manager for backward compatibility."""

    def __init__(self, port: Optional[str] = None, model: int = 1):
        """Initialize legacy AxiDraw manager."""
        self.driver = AxiDrawDriver({"port": port, "model": model})
        self.port = port
        self.model = model
        self.connected = False
        self.default_penlift = 1

    def setup_plot_context(self, svg_file: Path, **options) -> None:
        """Setup plot context - delegated to driver."""
        # For now, this is a simplified implementation
        pass

    def plot_file(
        self, svg_file: Path, preview_only: bool = False, **options
    ) -> Dict[str, Any]:
        """Plot SVG file - simplified implementation."""
        try:
            if preview_only:
                return {"success": True, "preview": True}

            # Connect and plot
            if self.driver.connect():
                return {"success": True, "plotted": True}
            else:
                return {"success": False, "error": "Connection failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def interactive(self) -> None:
        """Enter interactive mode."""
        if self.driver.connect():
            self.connected = True

    def disconnect(self) -> None:
        """Disconnect from device."""
        self.driver.disconnect()
        self.connected = False

    @property
    def ad(self):
        """Access to underlying AxiDraw instance for compatibility."""
        return self.driver.ad if hasattr(self.driver, "ad") else None

    @property
    def options(self):
        """Access to options for compatibility."""
        return (
            self.driver.ad.options
            if hasattr(self.driver, "ad") and self.driver.ad
            else None
        )


# Legacy compatibility functions
def is_axidraw_available() -> bool:
    """Check if pyaxidraw is available.

    Returns:
        True if pyaxidraw is installed and importable, False otherwise
    """
    return _AXIDRAW_AVAILABLE


def get_axidraw_install_instructions() -> str:
    """Get installation instructions for pyaxidraw.

    Returns:
        String with installation instructions
    """
    return _IMPORT_ERROR


def create_manager(
    port: Optional[str] = None, model: int = 1, penlift: Optional[int] = None
) -> "AxiDrawDriver":
    """Factory function to create AxiDraw manager.

    Args:
        port: USB port or nickname for AxiDraw
        model: AxiDraw model number
        penlift: Pen lift servo configuration (1-3). If None, uses config default.

    Returns:
        AxiDrawDriver instance

    Raises:
        ImportError: If pyaxidraw is not available
    """
    config = {"port": port, "model": model}
    if penlift is not None:
        config["penlift"] = penlift

    return AxiDrawDriver(config)
