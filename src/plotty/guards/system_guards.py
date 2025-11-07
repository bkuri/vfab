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

        # Implement actual camera health checks
        try:
            import requests
            from urllib.parse import urlparse
            
            camera_url = self.config.camera.url
            if not camera_url:
                return GuardCheck(
                    "camera_health",
                    GuardResult.SOFT_FAIL,
                    "Camera enabled but no URL configured",
                    {"enabled": True, "url": None},
                )
            
            # Parse URL to determine camera type
            parsed_url = urlparse(camera_url)
            
            if self.config.camera.mode == "ip" and parsed_url.scheme in ["http", "https"]:
                # Test IP camera connectivity
                try:
                    # Set a reasonable timeout for camera check
                    response = requests.get(camera_url, timeout=5)
                    
                    if response.status_code == 200:
                        # Check if we're getting actual image data
                        content_type = response.headers.get('content-type', '').lower()
                        if any(img_type in content_type for img_type in ['image', 'video', 'multipart']):
                            return GuardCheck(
                                "camera_health",
                                GuardResult.PASS,
                                f"Camera accessible at {camera_url}",
                                {
                                    "enabled": True,
                                    "url": camera_url,
                                    "status_code": response.status_code,
                                    "content_type": content_type,
                                },
                            )
                        else:
                            return GuardCheck(
                                "camera_health",
                                GuardResult.SOFT_FAIL,
                                f"Camera responded but with unexpected content type: {content_type}",
                                {
                                    "enabled": True,
                                    "url": camera_url,
                                    "status_code": response.status_code,
                                    "content_type": content_type,
                                },
                            )
                    else:
                        return GuardCheck(
                            "camera_health",
                            GuardResult.SOFT_FAIL,
                            f"Camera returned HTTP {response.status_code}",
                            {
                                "enabled": True,
                                "url": camera_url,
                                "status_code": response.status_code,
                            },
                        )
                        
                except requests.exceptions.Timeout:
                    return GuardCheck(
                        "camera_health",
                        GuardResult.SOFT_FAIL,
                        f"Camera timeout after 5 seconds",
                        {"enabled": True, "url": camera_url, "error": "timeout"},
                    )
                except requests.exceptions.ConnectionError:
                    return GuardCheck(
                        "camera_health",
                        GuardResult.SOFT_FAIL,
                        f"Cannot connect to camera at {camera_url}",
                        {"enabled": True, "url": camera_url, "error": "connection_error"},
                    )
                except Exception as e:
                    return GuardCheck(
                        "camera_health",
                        GuardResult.SOFT_FAIL,
                        f"Camera check failed: {str(e)}",
                        {"enabled": True, "url": camera_url, "error": str(e)},
                    )
            
            elif self.config.camera.mode == "device" and self.config.camera.device:
                # Test device camera (e.g., /dev/video0)
                try:
                    import os
                    device_path = self.config.camera.device
                    
                    if os.path.exists(device_path):
                        # Check if device is accessible
                        if os.access(device_path, os.R_OK):
                            return GuardCheck(
                                "camera_health",
                                GuardResult.PASS,
                                f"Camera device {device_path} is accessible",
                                {
                                    "enabled": True,
                                    "mode": "device",
                                    "device": device_path,
                                },
                            )
                        else:
                            return GuardCheck(
                                "camera_health",
                                GuardResult.SOFT_FAIL,
                                f"Camera device {device_path} is not accessible",
                                {
                                    "enabled": True,
                                    "mode": "device", 
                                    "device": device_path,
                                    "error": "permission_denied",
                                },
                            )
                    else:
                        return GuardCheck(
                            "camera_health",
                            GuardResult.SOFT_FAIL,
                            f"Camera device {device_path} does not exist",
                            {
                                "enabled": True,
                                "mode": "device",
                                "device": device_path,
                                "error": "device_not_found",
                            },
                        )
                        
                except Exception as e:
                    return GuardCheck(
                        "camera_health",
                        GuardResult.SOFT_FAIL,
                        f"Device camera check failed: {str(e)}",
                        {"enabled": True, "mode": "device", "error": str(e)},
                    )
            
            else:
                return GuardCheck(
                    "camera_health",
                    GuardResult.SOFT_FAIL,
                    f"Unsupported camera mode: {self.config.camera.mode}",
                    {
                        "enabled": True,
                        "mode": self.config.camera.mode,
                        "url": camera_url,
                    },
                )
                
        except ImportError:
            # requests module not available - this is a soft dependency
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                "Camera health check requires 'requests' module",
                {"enabled": True, "error": "missing_dependency", "dependency": "requests"},
            )
        except Exception as e:
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                f"Camera health check failed: {str(e)}",
                {"enabled": True, "error": str(e)},
            )
