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
            "device_id": "04d8:fd92",
            "device_name": "Microchip EiBotBoard (AxiDraw)",
            "accessible": False,
        }

        # Check USB devices for AxiDraw
        usb_count = self._detect_axidraw_usb()
        result["count"] = usb_count

        # Test accessibility if devices found
        if usb_count > 0:
            result["accessible"] = self._test_axidraw_access()

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
                result = subprocess.run(
                    cmd,
                    shell=True,
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
        cmd = "python3 -c 'import pyaxidraw; print(\"OK\")' 2>/dev/null"
        return self._run_command(cmd) == "OK"

    def _detect_axidraw_usb(self) -> int:
        """Detect AxiDraw devices via USB."""
        cmd = "lsusb | grep '04d8:fd92' | wc -l"
        try:
            count = int(self._run_command(cmd))
            return count
        except ValueError:
            return 0

    def _test_axidraw_access(self) -> bool:
        """Test if AxiDraw devices are accessible."""
        # Try to import and initialize pyaxidraw with simpler command for SSH compatibility
        cmd = "python3 -c 'from pyaxidraw import axidraw; ad = axidraw.AxiDraw(); ad.interactive(); print(\"OK\")' 2>/dev/null"
        result = self._run_command(cmd)
        return result == "OK"

    def _find_video_devices(self) -> List[str]:
        """Find video device paths."""
        cmd = "ls /dev/video* 2>/dev/null || true"
        result = self._run_command(cmd)
        if not result:
            return []

        devices = [dev.strip() for dev in result.split("\n") if dev.strip()]
        return sorted(devices)

    def _check_motion_running(self) -> bool:
        """Check if motion service is running."""
        cmd = "ps aux | grep '[m]otion' | wc -l"
        try:
            count = int(self._run_command(cmd))
            return count > 0
        except ValueError:
            return False

    def _test_camera_access(self, device_path: str) -> bool:
        """Test if camera device is accessible."""
        cmd = f"v4l2-ctl --device={device_path} --list-formats 2>/dev/null | head -1"
        try:
            result = self._run_command(cmd)
            # Check if we got a valid response (not an error about device busy)
            return (
                result != "" and "ioctl" not in result and "No such file" not in result
            )
        except Exception:
            return False
