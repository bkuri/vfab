"""
System-level guards for device and camera validation.
"""

from __future__ import annotations

from .base import Guard, GuardCheck, GuardResult

# Import optional modules
try:
    from ..drivers import create_manager
except ImportError:
    create_manager = None


class DeviceGuard(Guard):
    """Guard for checking device idle status."""

    def check(self, job_id: str) -> GuardCheck:
        """Check if device is idle and available."""
        if create_manager is None:
            return GuardCheck(
                "device_idle",
                GuardResult.SKIPPED,
                "AxiDraw integration not available",
                {"warning": "axidraw_not_available"},
            )

        try:
            # Create device manager
            manager = create_manager(
                port=self.config.device.port, model=self.config.device.model
            )

            # Try to get device status
            sysinfo = manager.get_sysinfo()
            if not sysinfo["success"]:
                return GuardCheck(
                    "device_idle",
                    GuardResult.FAIL,
                    f"Device not accessible: {sysinfo.get('error', 'Unknown error')}",
                    {"error": sysinfo.get("error")},
                )

            # Check if device is busy (simplified check)
            devices = manager.list_devices()
            if not devices["success"]:
                return GuardCheck(
                    "device_idle",
                    GuardResult.SOFT_FAIL,
                    f"Could not verify device status: {devices.get('error', 'Unknown error')}",
                    {"error": devices.get("error")},
                )

            device_list = devices.get("devices", [])
            device_count = len(device_list) if device_list else 0
            if device_count == 0:
                return GuardCheck(
                    "device_idle",
                    GuardResult.FAIL,
                    "No AxiDraw devices found",
                    {"device_count": 0},
                )

            return GuardCheck(
                "device_idle",
                GuardResult.PASS,
                f"Device ready ({device_count} device(s) found)",
                {
                    "device_count": device_count,
                    "devices": device_list,
                    "firmware": sysinfo.get("fw_version", "Unknown"),
                },
            )

        except Exception as e:
            return GuardCheck(
                "device_idle",
                GuardResult.SOFT_FAIL,
                f"Device check failed: {str(e)}",
                {"error": str(e)},
            )


class CameraGuard(Guard):
    """Guard for checking camera health."""

    def check(self, job_id: str) -> GuardCheck:
        """Check if camera is healthy (soft-fail allowed)."""
        if not self.config.camera.enabled:
            return GuardCheck(
                "camera_health",
                GuardResult.PASS,
                "Camera disabled in configuration",
                {"enabled": False},
            )

        # TODO: Implement actual camera health checks
        return GuardCheck(
            "camera_health",
            GuardResult.SKIPPED,
            "Camera health check not implemented",
            {"warning": "not_implemented"},
        )
