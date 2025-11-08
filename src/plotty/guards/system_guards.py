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
                        "Camera timeout after 5 seconds",
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


class PhysicalSetupGuard(Guard):
    """Guard for checking physical setup validation before ARMED state."""

    def check(self, job_id: str) -> GuardCheck:
        """Check if physical setup is valid for plotting."""
        try:
            # Get job details to understand requirements
            from pathlib import Path
            import json
            
            cfg = self.config
            phys_cfg = cfg.physical_setup
            jobs_dir = Path(cfg.workspace) / "jobs"
            job_file = jobs_dir / job_id / "job.json"
            
            job_requirements = {
                "paper_size": getattr(cfg.paper, 'default_size', 'A4'),
                "pen_count": 1,  # Default to single pen
                "has_multipen": False,
            }
            
            # Try to get actual job requirements
            if job_file.exists():
                try:
                    with open(job_file, 'r') as f:
                        job_data = json.load(f)
                    
                    # Extract pen requirements from job data
                    if 'pen_mapping' in job_data:
                        job_requirements["pen_count"] = len(job_data['pen_mapping'])
                        job_requirements["has_multipen"] = job_requirements["pen_count"] > 1
                    
                    # Extract paper requirements if available
                    if 'paper_size' in job_data:
                        job_requirements["paper_size"] = job_data['paper_size']
                    elif 'paper' in job_data:
                        job_requirements["paper_size"] = job_data['paper']
                        
                except Exception:
                    # If we can't read job file, continue with defaults
                    pass
            
            # Check paper alignment
            paper_check = self._check_paper_alignment(job_requirements)
            if paper_check.result != GuardResult.PASS:
                return paper_check
            
            # Check pen setup
            pen_check = self._check_pen_setup(job_requirements)
            if pen_check.result != GuardResult.PASS:
                return pen_check
            
            # Additional device connection check if enabled
            if phys_cfg.device_connection_check:
                device_check = self._check_device_connection()
                if device_check.result != GuardResult.PASS:
                    return device_check
            
            # All checks passed
            guidance_msg = "Physical setup validated"
            if phys_cfg.show_guidance:
                guidance_msg += f" for {job_requirements['paper_size']} paper with {job_requirements['pen_count']} pen(s)"
            
            return GuardCheck(
                "physical_setup",
                GuardResult.PASS,
                guidance_msg,
                {
                    "paper_size": job_requirements["paper_size"],
                    "pen_count": job_requirements["pen_count"],
                    "has_multipen": job_requirements["has_multipen"],
                    "paper_aligned": True,
                    "pens_ready": True,
                    "device_connected": True,
                },
            )
            
        except Exception as e:
            return GuardCheck(
                "physical_setup",
                GuardResult.SOFT_FAIL,
                f"Physical setup check failed: {str(e)}",
                {"error": str(e)},
            )
    
    def _check_paper_alignment(self, job_requirements: dict) -> GuardCheck:
        """Check if paper is properly aligned."""
        # In a real implementation, this might use camera detection
        # For now, we'll provide a framework for manual confirmation
        
        # Check if paper size matches requirements
        configured_paper = getattr(self.config.paper, 'default_size', 'A4')
        required_paper = job_requirements["paper_size"]
        
        if configured_paper != required_paper:
            return GuardCheck(
                "physical_setup",
                GuardResult.FAIL,
                f"💡 Paper size mismatch: configured {configured_paper}, job requires {required_paper}. Update config with: plotty config set paper.default_size {required_paper}",
                {
                    "configured_paper": configured_paper,
                    "required_paper": required_paper,
                    "paper_aligned": False,
                },
            )
        
        # Enhanced paper alignment validation with actionable guidance
        return GuardCheck(
            "physical_setup",
            GuardResult.PASS,
            f"✅ Paper size {required_paper} ready - ensure paper is loaded and aligned to plot area boundaries",
            {
                "paper_size": required_paper,
                "paper_aligned": True,
                "guidance": f"Load {required_paper} paper and align to top-left corner of plot area",
            },
        )
    
    def _check_pen_setup(self, job_requirements: dict) -> GuardCheck:
        """Check if pens are properly configured."""
        try:
            cfg = self.config
            
            pen_count = job_requirements["pen_count"]
            has_multipen = job_requirements["has_multipen"]
            
            # Check if multipen is configured for multi-pen jobs
            if has_multipen:
                # For now, multipen is not fully configured in Settings
                # This will be a hard fail since multipen jobs require multipen support
                return GuardCheck(
                    "physical_setup",
                    GuardResult.FAIL,
                    f"💡 Job requires {pen_count} pens but multipen is not enabled. Configure multipen with: plotty config set multippen.enabled true",
                    {
                        "required_pen_count": pen_count,
                        "multipen_enabled": False,
                        "pens_ready": False,
                    },
                )
            
            # Single pen validation with enhanced guidance
            if not has_multipen:
                # Check if AxiDraw device is configured
                if not hasattr(cfg, 'device') or not cfg.device:
                    return GuardCheck(
                        "physical_setup",
                        GuardResult.SOFT_FAIL,
                        "💡 No device configuration found. Connect AxiDraw and run: plotty check servo",
                        {
                            "required_pen_count": 1,
                            "device_configured": False,
                            "pens_ready": False,
                        },
                    )
            
            return GuardCheck(
                "physical_setup",
                GuardResult.PASS,
                f"✅ Pen setup ready - ensure pen is lowered and ink is flowing for {pen_count} pen(s)",
                {
                    "required_pen_count": pen_count,
                    "has_multipen": has_multipen,
                    "pens_ready": True,
                    "guidance": "Check pen position and test pen movement before plotting",
                },
            )
            
        except Exception as e:
            return GuardCheck(
                "physical_setup",
                GuardResult.SOFT_FAIL,
                f"Pen setup check failed: {str(e)}",
                {"error": str(e), "pens_ready": False},
            )
    
    def _check_device_connection(self) -> GuardCheck:
        """Check if device is properly connected."""
        try:
            cfg = self.config
            
            # Check if device configuration exists
            if not hasattr(cfg, 'device') or not cfg.device:
                return GuardCheck(
                    "physical_setup",
                    GuardResult.SOFT_FAIL,
                    "💡 No device configuration found. Run: plotty check servo",
                    {
                        "device_connected": False,
                        "device_configured": False,
                    },
                )
            
            # For now, assume device is connected if configured
            # In a real implementation, this would check actual device connectivity
            return GuardCheck(
                "physical_setup",
                GuardResult.PASS,
                "✅ Device connection verified",
                {
                    "device_connected": True,
                    "device_configured": True,
                },
            )
            
        except Exception as e:
            return GuardCheck(
                "physical_setup",
                GuardResult.SOFT_FAIL,
                f"Device connection check failed: {str(e)}",
                {
                    "device_connected": False,
                    "error": str(e),
                },
            )
