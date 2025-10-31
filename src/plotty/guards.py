"""
FSM Guards implementation for ploTTY.

This module provides guard functions that validate state transitions
according to PRD requirements: device idle, checklist complete, camera health.
"""

from __future__ import annotations
import requests
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from enum import Enum


try:
    from .axidraw_integration import create_manager
except ImportError:
    create_manager = None

try:
    from .checklist import create_checklist
except ImportError:
    create_checklist = None

logger = logging.getLogger(__name__)


class GuardResult(Enum):
    """Result of guard evaluation."""

    PASS = "pass"
    FAIL = "fail"
    SOFT_FAIL = "soft_fail"  # Allow transition but warn


class GuardCheck:
    """Result of a single guard check."""

    def __init__(
        self,
        name: str,
        result: GuardResult,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.result = result
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "name": self.name,
            "result": self.result.value,
            "message": self.message,
            "details": self.details,
        }


class DeviceGuard:
    """Guard for checking device idle status."""

    def __init__(self, config):
        self.config = config

    def check(self, job_id: str) -> GuardCheck:
        """Check if device is idle and available.

        Args:
            job_id: Job identifier for logging

        Returns:
            GuardCheck with result
        """
        if create_manager is None:
            return GuardCheck(
                "device_idle",
                GuardResult.SOFT_FAIL,
                "AxiDraw integration not available - device check skipped",
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
            # In a real implementation, we'd check for active plotting
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


class CameraGuard:
    """Guard for checking camera health."""

    def __init__(self, config):
        self.config = config

    def check(self, job_id: str) -> GuardCheck:
        """Check if camera is healthy (soft-fail allowed).

        Args:
            job_id: Job identifier for logging

        Returns:
            GuardCheck with result
        """
        if not self.config.camera.enabled:
            return GuardCheck(
                "camera_health",
                GuardResult.PASS,
                "Camera disabled in configuration",
                {"enabled": False},
            )

        try:
            if self.config.camera.mode == "ip":
                return self._check_ip_camera()
            elif self.config.camera.mode == "v4l2":
                return self._check_v4l2_camera()
            else:
                return GuardCheck(
                    "camera_health",
                    GuardResult.SOFT_FAIL,
                    f"Unknown camera mode: {self.config.camera.mode}",
                    {"mode": self.config.camera.mode},
                )

        except Exception as e:
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                f"Camera check failed: {str(e)}",
                {"error": str(e)},
            )

    def _check_ip_camera(self) -> GuardCheck:
        """Check IP camera health."""
        url = self.config.camera.url
        if not url:
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                "IP camera URL not configured",
                {"mode": "ip", "url": None},
            )

        try:
            # Try to access camera stream with timeout
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                return GuardCheck(
                    "camera_health",
                    GuardResult.PASS,
                    "IP camera accessible",
                    {
                        "mode": "ip",
                        "url": url,
                        "status_code": response.status_code,
                        "content_type": response.headers.get("content-type", "unknown"),
                    },
                )
            else:
                return GuardCheck(
                    "camera_health",
                    GuardResult.SOFT_FAIL,
                    f"IP camera returned status {response.status_code}",
                    {"mode": "ip", "url": url, "status_code": response.status_code},
                )

        except requests.exceptions.Timeout:
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                "IP camera timeout",
                {"mode": "ip", "url": url, "error": "timeout"},
            )
        except Exception as e:
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                f"IP camera check failed: {str(e)}",
                {"mode": "ip", "url": url, "error": str(e)},
            )

    def _check_v4l2_camera(self) -> GuardCheck:
        """Check V4L2 camera health."""
        device = self.config.camera.device
        if not device:
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                "V4L2 camera device not configured",
                {"mode": "v4l2", "device": None},
            )

        try:
            # Try to get camera info using v4l2-ctl or ffmpeg
            result = subprocess.run(
                ["ffmpeg", "-f", "v4l2", "-i", device, "-t", "1", "-f", "null", "-"],
                capture_output=True,
                timeout=5,
            )

            if result.returncode == 0:
                return GuardCheck(
                    "camera_health",
                    GuardResult.PASS,
                    "V4L2 camera accessible",
                    {"mode": "v4l2", "device": device},
                )
            else:
                return GuardCheck(
                    "camera_health",
                    GuardResult.SOFT_FAIL,
                    f"V4L2 camera not accessible: {result.stderr.decode().strip()}",
                    {
                        "mode": "v4l2",
                        "device": device,
                        "returncode": result.returncode,
                        "stderr": result.stderr.decode().strip(),
                    },
                )

        except subprocess.TimeoutExpired:
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                "V4L2 camera timeout",
                {"mode": "v4l2", "device": device, "error": "timeout"},
            )
        except FileNotFoundError:
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                "ffmpeg not found for V4L2 camera check",
                {"mode": "v4l2", "device": device, "error": "ffmpeg_not_found"},
            )
        except Exception as e:
            return GuardCheck(
                "camera_health",
                GuardResult.SOFT_FAIL,
                f"V4L2 camera check failed: {str(e)}",
                {"mode": "v4l2", "device": device, "error": str(e)},
            )


class ChecklistGuard:
    """Guard for checking checklist completion."""

    def __init__(self, config):
        self.config = config

    def check(self, job_id: str, workspace: Path) -> GuardCheck:
        """Check if checklist is complete for a job.

        Args:
            job_id: Job identifier
            workspace: Path to workspace

        Returns:
            GuardCheck with result
        """
        if create_checklist is None:
            return GuardCheck(
                "checklist_complete",
                GuardResult.SOFT_FAIL,
                "Checklist system not available - check skipped",
                {"warning": "checklist_not_available"},
            )

        try:
            job_dir = workspace / "jobs" / job_id
            checklist = create_checklist(job_id, job_dir)

            if not checklist.is_complete():
                incomplete_items = checklist.get_incomplete_items()
                completed_items = checklist.get_completed_items()
                progress = checklist.get_progress()

                return GuardCheck(
                    "checklist_complete",
                    GuardResult.FAIL,
                    f"Checklist incomplete: {len(incomplete_items)} items remaining",
                    {
                        "job_id": job_id,
                        "progress": progress,
                        "incomplete_items": [item.name for item in incomplete_items],
                        "completed_items": [item.name for item in completed_items],
                    },
                )

            progress = checklist.get_progress()
            return GuardCheck(
                "checklist_complete",
                GuardResult.PASS,
                f"Checklist complete ({progress['required_completed']}/{progress['required_total']} items)",
                {"job_id": job_id, "progress": progress},
            )

        except Exception as e:
            return GuardCheck(
                "checklist_complete",
                GuardResult.FAIL,
                f"Checklist check failed: {str(e)}",
                {"job_id": job_id, "error": str(e)},
            )


class GuardSystem:
    """System for evaluating FSM guards."""

    def __init__(self, config, workspace: Path):
        """Initialize guard system.

        Args:
            config: Application configuration
            workspace: Path to workspace directory
        """
        self.config = config
        self.workspace = workspace
        self.device_guard = DeviceGuard(config)
        self.camera_guard = CameraGuard(config)
        self.checklist_guard = ChecklistGuard(config)
        self.paper_session_guard = PaperSessionGuard(workspace)
        self.pen_layer_guard = PenLayerGuard(workspace)

    def evaluate_guards(
        self, job_id: str, target_state: str, current_state: Optional[str] = None
    ) -> List[GuardCheck]:
        """Evaluate guards for a state transition.

        Args:
            job_id: Job identifier
            target_state: Target FSM state
            current_state: Current FSM state (optional)

        Returns:
            List of guard check results
        """
        guards = []

        # Determine which guards to check based on target state
        if target_state in ["ARMED", "PLOTTING"]:
            # Device must be idle for armed/plotting states
            guards.append(self.device_guard.check(job_id))

            # Checklist must be complete for armed state
            if target_state == "ARMED":
                guards.append(self.checklist_guard.check(job_id, self.workspace))

                # Paper session guard - one paper per session
                if self.config.paper.require_one_per_session:
                    guards.append(self.paper_session_guard.check(job_id))

                # Pen layer guard - one pen per layer
                guards.append(self.pen_layer_guard.check(job_id))

        # Camera health check (soft-fail allowed) for plotting states
        if target_state in ["ARMED", "PLOTTING"]:
            guards.append(self.camera_guard.check(job_id))

        return guards

    def can_transition(
        self, job_id: str, target_state: str, current_state: Optional[str] = None
    ) -> tuple[bool, List[GuardCheck]]:
        """Check if transition is allowed by guards.

        Args:
            job_id: Job identifier
            target_state: Target FSM state
            current_state: Current FSM state (optional)

        Returns:
            Tuple of (can_transition, guard_checks)
        """
        guard_checks = self.evaluate_guards(job_id, target_state, current_state)

        # Check for any hard failures
        hard_failures = [g for g in guard_checks if g.result == GuardResult.FAIL]

        can_transition = len(hard_failures) == 0

        return can_transition, guard_checks


class PaperSessionGuard:
    """Guard to enforce one paper per session rule."""

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def check(self, job_id: str) -> GuardCheck:
        """Check if this is the first job in the session."""
        try:
            # Check for session marker file
            session_file = self.workspace / ".paper_session"

            if not session_file.exists():
                # First job in session - create marker
                session_file.write_text(job_id)
                return GuardCheck(
                    "paper_one_per_session",
                    GuardResult.PASS,
                    "First job in session - paper OK",
                    {"session_job": job_id},
                )
            else:
                # Check if this is the same job as session start
                session_job = session_file.read_text().strip()
                if session_job == job_id:
                    return GuardCheck(
                        "paper_one_per_session",
                        GuardResult.PASS,
                        "Same job as session start",
                        {"session_job": job_id},
                    )
                else:
                    return GuardCheck(
                        "paper_one_per_session",
                        GuardResult.FAIL,
                        f"Paper already used for job {session_job}. Start new session or use fresh paper.",
                        {"session_job": session_job, "current_job": job_id},
                    )
        except Exception as e:
            return GuardCheck(
                "paper_one_per_session",
                GuardResult.FAIL,
                f"Paper session check error: {str(e)}",
                {"job_id": job_id, "error": str(e)},
            )

    def reset_session(self) -> bool:
        """Reset the paper session marker."""
        try:
            session_file = self.workspace / ".paper_session"
            if session_file.exists():
                session_file.unlink()
            return True
        except Exception:
            return False


class PenLayerGuard:
    """Guard to enforce one pen per layer rule."""

    def __init__(self, workspace: Path):
        self.workspace = workspace

    def check(self, job_id: str) -> GuardCheck:
        """Check if pen mapping follows one-pen-per-layer rule."""
        try:
            job_dir = self.workspace / "jobs" / job_id
            plan_file = job_dir / "plan.json"

            if not plan_file.exists():
                return GuardCheck(
                    "pen_one_per_layer",
                    GuardResult.FAIL,
                    "No plan file found - cannot validate pen mapping",
                    {"job_id": job_id},
                )

            import json

            plan_data = json.loads(plan_file.read_text())
            pen_map = plan_data.get("pen_map", {})
            layers = plan_data.get("layers", [])

            # Validate each layer has exactly one pen assigned
            violations = []
            for layer in layers:
                layer_name = layer.get("name", "")
                assigned_pen = pen_map.get(layer_name)

                if not assigned_pen:
                    violations.append(f"Layer '{layer_name}' has no pen assigned")
                elif isinstance(assigned_pen, list) and len(assigned_pen) > 1:
                    violations.append(
                        f"Layer '{layer_name}' has multiple pens assigned: {assigned_pen}"
                    )

            if violations:
                return GuardCheck(
                    "pen_one_per_layer",
                    GuardResult.FAIL,
                    f"Pen mapping violations: {'; '.join(violations)}",
                    {"violations": violations, "pen_map": pen_map, "job_id": job_id},
                )
            else:
                return GuardCheck(
                    "pen_one_per_layer",
                    GuardResult.PASS,
                    f"Pen mapping valid: {len(pen_map)} layers with unique pens",
                    {"pen_map": pen_map, "layer_count": len(layers), "job_id": job_id},
                )
        except Exception as e:
            return GuardCheck(
                "pen_one_per_layer",
                GuardResult.FAIL,
                f"Pen layer check error: {str(e)}",
                {"job_id": job_id, "error": str(e)},
            )


def create_guard_system(config, workspace: Path) -> GuardSystem:
    """Factory function to create guard system.

    Args:
        config: Application configuration
        workspace: Path to workspace directory

    Returns:
        GuardSystem instance
    """
    return GuardSystem(config, workspace)
