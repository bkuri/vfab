"""
Device detection utilities for ploTTY.

This module provides hardware detection for AxiDraw plotters and cameras,
with support for both local and remote detection via SSH.
"""

from __future__ import annotations

import subprocess
from typing import Dict, Any, Optional, List


class DeviceDetector:
    """Detects actual hardware devices locally or remotely."""

    def __init__(self, remote_host: Optional[str] = None, timeout: int = 5):
        """Initialize device detector.

        Args:
            remote_host: SSH host for remote detection (None for local)
            timeout: Timeout for remote commands in seconds
        """
        self.remote_host = remote_host
        self.timeout = timeout

    def detect_axidraw_devices(self) -> Dict[str, Any]:
        """Detect AxiDraw hardware devices.

        Returns:
            Dictionary with device detection results:
            - count: Number of devices found
            - installed: Whether pyaxidraw is installed
            - device_id: USB device ID
            - device_name: Human readable device name
            - accessible: Whether devices are accessible
        """
        result = {
            "count": 0,
            "installed": self._check_pyaxidraw_installed(),
            "device_id": "04d8:xxxx",
            "device_name": "Microchip/AxiDraw compatible device",
            "accessible": False,
        }

        # Check USB devices for AxiDraw
        usb_count = self._detect_axidraw_usb()
        result["count"] = usb_count

        # Get detailed device information if devices found
        if usb_count > 0:
            device_details = self._get_device_details()
            result["devices"] = device_details
            result["accessible"] = self._test_axidraw_access()
        else:
            result["devices"] = []

        return result

    def detect_camera_devices(self) -> Dict[str, Any]:
        """Detect camera hardware devices.

        Returns:
            Dictionary with camera detection results:
            - count: Number of camera devices found
            - devices: List of device paths
            - accessible: Whether cameras are accessible
            - motion_running: Whether motion service is blocking cameras
        """
        result = {
            "count": 0,
            "devices": [],
            "accessible": False,
            "motion_running": False,
        }

        # Find video devices
        video_devices = self._find_video_devices()
        result["count"] = len(video_devices)
        result["devices"] = video_devices

        # Check if motion is running
        result["motion_running"] = self._check_motion_running()

        # Test camera accessibility
        if video_devices:
            result["accessible"] = self._test_camera_access(video_devices[0])

        return result

    def _run_command(self, cmd: str) -> str:
        """Run command locally or remotely."""
        if self.remote_host:
            try:
                result = subprocess.run(
                    ["ssh", self.remote_host, cmd],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                return result.stdout.strip()
            except subprocess.TimeoutExpired:
                return ""
            except Exception:
                return ""
        else:
            try:
                # Use shlex for safe command parsing when shell features are needed
                import shlex
                cmd_parts = shlex.split(cmd)
                result = subprocess.run(
                    cmd_parts,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                return result.stdout.strip()
            except subprocess.TimeoutExpired:
                return ""
            except Exception:
                return ""

    def _check_pyaxidraw_installed(self) -> bool:
        """Check if pyaxidraw module is available."""
        try:
            import importlib.util
            spec = importlib.util.find_spec("pyaxidraw")
            return spec is not None
        except ImportError:
            return False

    def _detect_axidraw_usb(self) -> int:
        """Detect AxiDraw devices via USB."""
        try:
            result = subprocess.run(
                ["lsusb"], capture_output=True, text=True, timeout=self.timeout
            )
            if result.returncode == 0:
                # Count lines containing Microchip vendor ID 04d8
                return sum(1 for line in result.stdout.split('\n') if '04d8:' in line)
            return 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return 0

    def _get_device_details(self) -> List[Dict[str, str]]:
        """Get detailed information about detected Microchip devices."""
        try:
            result = subprocess.run(
                ["lsusb"], capture_output=True, text=True, timeout=self.timeout
            )
            if result.returncode != 0:
                return []
                
            devices = []
            for line in result.stdout.split("\n"):
                if line.strip() and '04d8:' in line:
                    # Parse lsusb output format: Bus XXX Device XXX: ID XXXX:XXXX Description
                    parts = line.split("ID ")
                    if len(parts) >= 2:
                        device_id = parts[1].split(" ")[0]
                        description = " ".join(parts[1].split(" ")[1:])
                        devices.append({"id": device_id, "description": description})

            return devices
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return []

    def _test_axidraw_access(self) -> bool:
        """Test if AxiDraw devices are accessible."""
        try:
            from pyaxidraw import axidraw
            ad = axidraw.AxiDraw()
            ad.interactive()
            return True
        except Exception:
            return False

    def _find_video_devices(self) -> List[str]:
        """Find video device paths."""
        import glob
        try:
            devices = glob.glob('/dev/video*')
            return sorted(devices)
        except Exception:
            return []

    def _check_motion_running(self) -> bool:
        """Check if motion service is running."""
        try:
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, timeout=self.timeout
            )
            if result.returncode == 0:
                # Look for motion process, excluding the grep process itself
                return any('motion' in line and '[m]otion' not in line 
                          for line in result.stdout.split('\n'))
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False

    def _test_camera_access(self, device_path: str) -> bool:
        """Test if camera device is accessible."""
        try:
            result = subprocess.run(
                ["v4l2-ctl", "--device={device_path}".format(device_path=device_path), "--list-formats"],
                capture_output=True, text=True, timeout=self.timeout
            )
            # Check if we got a valid response (not an error about device busy)
            return (
                result.returncode == 0 and 
                result.stdout != "" and 
                "ioctl" not in result.stderr and 
                "No such file" not in result.stderr
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False
