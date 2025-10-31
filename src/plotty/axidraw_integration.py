"""
AxiDraw integration module for plotty.

This module provides both Plot and Interactive context support for AxiDraw plotters,
following the official pyaxidraw API documentation.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

try:
    from pyaxidraw import axidraw
except ImportError as e:
    raise ImportError(
        "pyaxidraw not found. Install with: "
        "python -m pip install https://cdn.evilmadscientist.com/dl/ad/public/AxiDraw_API.zip"
    ) from e


class AxiDrawManager:
    """Manages AxiDraw plotter operations in both Plot and Interactive contexts."""

    def __init__(self, port: Optional[str] = None, model: int = 1):
        """Initialize AxiDraw manager.

        Args:
            port: USB port or nickname for AxiDraw (auto-detect if None)
            model: AxiDraw model number (1=V2/V3/SE/A4, 2=V3/A3/SE/A3, etc.)
        """
        self.ad = axidraw.AxiDraw()
        self.port = port
        self.model = model
        self.connected = False

    def setup_plot_context(self, svg_file: Path, **options) -> None:
        """Setup Plot context for SVG file.

        Args:
            svg_file: Path to SVG file to plot
            **options: Additional AxiDraw options (speed, pen height, etc.)
        """
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
        self.ad.options.report_time = True

        try:
            output_svg = self.ad.plot_run(True)
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

    def cycle_pen(self) -> Dict[str, Any]:
        """Cycle pen down then up for setup.

        Returns:
            Dictionary with operation result
        """
        self.ad.plot_setup()
        self.ad.options.mode = "cycle"
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


def create_manager(port: Optional[str] = None, model: int = 1) -> AxiDrawManager:
    """Factory function to create AxiDraw manager.

    Args:
        port: USB port or nickname for AxiDraw
        model: AxiDraw model number

    Returns:
        AxiDrawManager instance
    """
    return AxiDrawManager(port=port, model=model)
