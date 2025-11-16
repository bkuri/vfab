"""
AxiDraw integration module for vfab.

This module provides both Plot and Interactive context support for AxiDraw plotters,
following the official pyaxidraw API documentation.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
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
    )
except ImportError:
    from vfab.drivers.base import (
        PlotterDriver,
        DriverInfo,
        DriverStatus,
        DriverTestResult,
        DriverCapability,
    )


class AxiDrawDriver(PlotterDriver):
    """AxiDraw driver implementation using the BaseDriver interface."""

    DRIVER_INFO = DriverInfo(
        name="axidraw",
        display_name="AxiDraw Plotter",
        version="1.0.0",
        description="AxiDraw USB pen plotter driver supporting all AxiDraw models",
        author="vfab",
        driver_type="plotter",
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
            DriverCapability(
                name="svg_plotting",
                description="Direct SVG file plotting capability",
                required=False,
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
        """Initialize the AxiDraw driver.

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
    def install(cls, force: bool = False) -> bool:
        """Install AxiDraw support."""
        if cls.is_available() and not force:
            return True

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
                self.ad.move(x, y)
            return True
        except Exception:
            return False

            if device_id and device_id != "auto":
                self.ad.options.port = device_id

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
        """Move pen to specified coordinates."""
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
        """Lift the pen."""
        try:
            if self.ad:
                self.ad.disconnect()
            self.connected = False
            return True
        except Exception:
            return False

    def pen_down(self) -> bool:
        """Lower the pen."""
        try:
            if self.ad:
                self.ad.pendown()
            return True
        except Exception:
            return False

    def disconnect(self) -> bool:
        """Disconnect from AxiDraw."""
        try:
            if self._connected:
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
        """Move pen to specified coordinates."""
        try:
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
        """Lift the pen."""
        try:
            if self.ad:
                self.ad.moveto(x, y)
            return True
        except Exception:
            return False

    def pen_down(self) -> bool:
        """Lower the pen."""
        try:
            if self.ad:
                self.ad.lineto(x, y)
            return True
        except Exception:
            return False


class AxiDrawManager:
    """Manages AxiDraw plotter operations in both Plot and Interactive contexts."""

    def __init__(self, port: Optional[str] = None, model: int = 1, penlift: int = 1):
        """Initialize AxiDraw manager.

        Args:
            port: USB port or nickname for AxiDraw (auto-detect if None)
            model: AxiDraw model number (1=V2/V3/SE/A4, 2=V3/A3/SE/A3, etc.)
            penlift: Pen lift servo configuration
        """
        if not _AXIDRAW_AVAILABLE:
            raise ImportError(_IMPORT_ERROR)

        self.ad = axidraw.AxiDraw() if axidraw else None
        self.port = port
        self.model = model
        self.penlift = penlift
        self.connected = False
        self.default_penlift = penlift  # Default penlift setting

    def setup_plot_context(self, svg_file: Path, **options) -> None:
        """Setup Plot context for SVG file.

        Args:
            svg_file: Path to SVG file to plot
            **options: Additional AxiDraw options (speed, pen height, etc.)
        """
        if self.ad:
            self.ad.plot_setup(str(svg_file))

        # Apply model setting
        self.ad.options.model = self.model

        # Apply port if specified
        if self.port:
            self.ad.options.port = self.port

        # Apply additional options
        for key, value in options.items():
            if hasattr(self.ad.options, key):
                setattr(self.ad.options, key, value)

    def plot_file(
        self, svg_file: Path, preview_only: bool = False, **options
    ) -> Dict[str, Any]:
        """Plot an SVG file using AxiDraw.

        Args:
            svg_file: Path to SVG file to plot
            preview_only: If True, simulate plot without moving
            **options: Additional AxiDraw options

        Returns:
            Dictionary with plot results and metadata
        """
        self.setup_plot_context(svg_file, **options)

        if preview_only:
            self.ad.options.preview = True

        # Enable time reporting for estimates
        if self.ad:
            self.ad.options.report_time = True

        try:
            output_svg = self.ad.plot_run(True) if self.ad else None
            return {
                "success": True,
                "output_svg": output_svg,
                "time_elapsed": getattr(self.ad, "time_elapsed", 0),
                "time_estimate": getattr(self.ad, "time_estimate", 0),
                "distance_pendown": getattr(self.ad, "distance_pendown", 0),
                "distance_total": getattr(self.ad, "distance_total", 0),
                "pen_lifts": getattr(self.ad, "pen_lifts", 0),
                "fw_version": getattr(self.ad, "fw_version_string", "Unknown"),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(self.ad, "errors", {}).get("code", 0),
            }

    def setup_interactive_context(self, **options) -> None:
        """Setup Interactive context for direct XY control.

        Args:
            **options: Additional AxiDraw options
        """
        if self.ad:
            self.ad.interactive()

            # Apply model setting
            self.ad.options.model = self.model

            # Apply port if specified
            if self.port:
                self.ad.options.port = self.port

            # Apply additional options
            for key, value in options.items():
                if hasattr(self.ad.options, key):
                    setattr(self.ad.options, key, value)

    def connect(self) -> bool:
        """Connect to AxiDraw in Interactive context.

        Returns:
            True if connection successful, False otherwise
        """
        self.setup_interactive_context()
        self.connected = self.ad.connect()
        return self.connected

    def disconnect(self) -> None:
        """Disconnect from AxiDraw."""
        if self.connected:
            self.ad.disconnect()
            self.connected = False

    def move_to(self, x: float, y: float) -> None:
        """Move pen-up to absolute position.

        Args:
            x: X coordinate (inches by default)
            y: Y coordinate (inches by default)
        """
        if not self.connected:
            raise RuntimeError("Not connected to AxiDraw. Call connect() first.")
        self.ad.moveto(x, y)

    def draw_to(self, x: float, y: float) -> None:
        """Draw line to absolute position.

        Args:
            x: X coordinate (inches by default)
            y: Y coordinate (inches by default)
        """
        if not self.connected:
            raise RuntimeError("Not connected to AxiDraw. Call connect() first.")
        self.ad.lineto(x, y)

    def move_relative(self, dx: float, dy: float) -> None:
        """Move pen-up by relative amount.

        Args:
            dx: X movement (inches by default)
            dy: Y movement (inches by default)
        """
        if not self.connected:
            raise RuntimeError("Not connected to AxiDraw. Call connect() first.")
        self.ad.move(dx, dy)

    def draw_relative(self, dx: float, dy: float) -> None:
        """Draw line by relative amount.

        Args:
            dx: X movement (inches by default)
            dy: Y movement (inches by default)
        """
        if not self.connected:
            raise RuntimeError("Not connected to AxiDraw. Call connect() first.")
        self.ad.line(dx, dy)

    def pen_up(self) -> None:
        """Raise the pen."""
        if not self.connected:
            raise RuntimeError("Not connected to AxiDraw. Call connect() first.")
        self.ad.penup()

    def pen_down(self) -> None:
        """Lower the pen."""
        if not self.connected:
            raise RuntimeError("Not connected to AxiDraw. Call connect() first.")
        self.ad.pendown()

    def get_position(self) -> Tuple[float, float]:
        """Get current position.

        Returns:
            Tuple of (x, y) coordinates
        """
        if not self.connected:
            raise RuntimeError("Not connected to AxiDraw. Call connect() first.")
        return self.ad.current_pos()

    def get_pen_state(self) -> bool:
        """Get current pen state.

        Returns:
            True if pen is up, False if pen is down
        """
        if not self.connected:
            raise RuntimeError("Not connected to AxiDraw. Call connect() first.")
        return self.ad.current_pen()

    def set_units(self, units: str) -> None:
        """Set coordinate units.

        Args:
            units: 'inches', 'cm', or 'mm'
        """
        if not self.connected:
            raise RuntimeError("Not connected to AxiDraw. Call connect() first.")

        unit_map = {"inches": 0, "cm": 1, "mm": 2}
        if units not in unit_map:
            raise ValueError(f"Invalid units: {units}. Use 'inches', 'cm', or 'mm'.")

        self.ad.options.units = unit_map[units]
        self.ad.update()

    def cycle_pen(self, penlift: Optional[int] = None) -> Dict[str, Any]:
        """Cycle pen down then up for setup.

        Args:
            penlift: Pen lift servo configuration (1-3). 1: Default for AxiDraw model.
                    2: Standard servo (lowest connector position).
                    3: Narrow-band brushless servo (3rd position up).
                    If None, uses the manager's default_penlift setting.

        Returns:
            Dictionary with operation result
        """
        self.ad.plot_setup()
        self.ad.options.mode = "cycle"

        # Apply penlift setting - use provided value, otherwise use default
        effective_penlift = (
            penlift if penlift is not None else getattr(self, "default_penlift", 1)
        )
        self.ad.options.penlift = effective_penlift

        try:
            self.ad.plot_run()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_pen(self) -> Dict[str, Any]:
        """Toggle pen between up and down.

        Returns:
            Dictionary with operation result
        """
        self.ad.plot_setup()
        self.ad.options.mode = "toggle"
        try:
            self.ad.plot_run()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_sysinfo(self) -> Dict[str, Any]:
        """Get system information.

        Returns:
            Dictionary with system information
        """
        self.ad.plot_setup()
        self.ad.options.mode = "sysinfo"
        try:
            self.ad.plot_run()
            return {
                "success": True,
                "fw_version": getattr(self.ad, "fw_version_string", "Unknown"),
                "version": getattr(self.ad, "version_string", "Unknown"),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_devices(self) -> Dict[str, Any]:
        """List connected AxiDraw devices.

        Returns:
            Dictionary with device list
        """
        self.ad.plot_setup()
        self.ad.options.mode = "manual"
        self.ad.options.manual_cmd = "list_names"
        try:
            self.ad.plot_run()
            return {"success": True, "devices": getattr(self.ad, "name_list", [])}
        except Exception as e:
            return {"success": False, "error": str(e)}


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
) -> AxiDrawManager:
    """Factory function to create AxiDraw manager.

    Args:
        port: USB port or nickname for AxiDraw
        model: AxiDraw model number
        penlift: Pen lift servo configuration (1-3). If None, uses config default.

    Returns:
        AxiDrawManager instance

    Raises:
        ImportError: If pyaxidraw is not available
    """
    manager = AxiDrawManager(port=port, model=model)

    # Set penlift if provided, otherwise use config
    if penlift is None:
        try:
            from ..config import get_config

            config = get_config()
            manager.default_penlift = config.device.penlift
        except Exception:
            # Fallback to default if config unavailable
            manager.default_penlift = 1
    else:
        manager.default_penlift = penlift

    return manager
