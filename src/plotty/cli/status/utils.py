"""
Shared utilities for status commands.

This module contains common functions used across status subcommands
for formatting, job loading, and data processing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from rich.console import Console

from ...config import load_config

logger = logging.getLogger(__name__)

# Create console for rich output
console = Console()


def get_available_job_ids() -> List[str]:
    """Get list of available job IDs for autocomplete."""
    try:
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"
        job_ids = []

        if jobs_dir.exists():
            for job_dir in jobs_dir.iterdir():
                if job_dir.is_dir():
                    job_file = job_dir / "job.json"
                    if job_file.exists():
                        job_ids.append(job_dir.name)

        return sorted(job_ids, reverse=True)  # Most recent first
    except Exception:
        return []


def complete_job_id(ctx, args: List[str], incomplete: str) -> List[str]:
    """Autocomplete function for job IDs."""
    available_ids = get_available_job_ids()
    return [job_id for job_id in available_ids if job_id.startswith(incomplete)]


def load_job_data(job_dir: Path) -> Optional[Dict[str, Any]]:
    """Load job data from job.json file.

    Args:
        job_dir: Path to job directory

    Returns:
        Job data dictionary or None if failed
    """
    try:
        job_file = job_dir / "job.json"
        if not job_file.exists():
            return None
        return json.loads(job_file.read_text())
    except Exception:
        return None


def load_plan_data(job_dir: Path) -> Optional[Dict[str, Any]]:
    """Load plan data from plan.json file.

    Args:
        job_dir: Path to job directory

    Returns:
        Plan data dictionary or None if failed
    """
    try:
        plan_file = job_dir / "plan.json"
        if not plan_file.exists():
            return None
        return json.loads(plan_file.read_text())
    except Exception:
        return None


def collect_jobs(
    jobs_dir: Path, state_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Collect job data from jobs directory.

    Args:
        jobs_dir: Path to jobs directory
        state_filter: Optional state to filter by

    Returns:
        List of job dictionaries
    """
    jobs = []

    if not jobs_dir.exists():
        return jobs

    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue

        job_data = load_job_data(job_dir)
        if not job_data:
            continue

        # Filter by state if specified
        if state_filter and job_data.get("state") != state_filter:
            continue

        # Get plan info if available
        plan_data = load_plan_data(job_dir)
        time_estimate = None
        layer_count = None

        if plan_data:
            time_estimate = plan_data.get("estimates", {}).get("post_s")
            layer_count = len(plan_data.get("layers", []))

        jobs.append(
            {
                "id": job_data.get("id", job_dir.name),
                "name": job_data.get("name", "Unknown"),
                "state": job_data.get("state", "UNKNOWN"),
                "config_status": job_data.get("config_status", "DEFAULTS"),
                "paper": job_data.get("paper", "Unknown"),
                "time_estimate": time_estimate,
                "layer_count": layer_count,
                "created_at": job_data.get("created_at"),
                "updated_at": job_data.get("updated_at"),
                "error": job_data.get("error"),
            }
        )

    return jobs


def sort_jobs_by_state(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort jobs by state priority.

    Args:
        jobs: List of job dictionaries

    Returns:
        Sorted list of jobs
    """
    state_priority = {
        "PLOTTING": 0,
        "ARMED": 1,
        "READY": 2,
        "OPTIMIZED": 3,
        "ANALYZED": 4,
        "QUEUED": 5,
        "NEW": 6,
        "PAUSED": 7,
        "COMPLETED": 8,
        "ABORTED": 9,
        "FAILED": 10,
    }

    return sorted(jobs, key=lambda j: state_priority.get(j["state"], 99))


def format_time(seconds: Optional[float]) -> str:
    """Format time in seconds to human readable format."""
    if seconds is None:
        return "Unknown"

    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_state(state: str) -> str:
    """Format job state with color."""
    state_colors = {
        "NEW": "blue",
        "QUEUED": "yellow",
        "ANALYZED": "cyan",
        "OPTIMIZED": "green",
        "READY": "bright_green",
        "ARMED": "magenta",
        "PLOTTING": "red",
        "PAUSED": "yellow",
        "COMPLETED": "green",
        "ABORTED": "red",
        "FAILED": "bright_red",
    }

    color = state_colors.get(state, "white")
    return f"[{color}]{state}[/{color}]"


def get_axidraw_status() -> str:
    """Check AxiDraw availability."""
    try:
        import importlib.util

        spec = importlib.util.find_spec("plotty.drivers.axidraw")
        return "✅ Available" if spec else "❌ Not installed"
    except Exception:
        return "❌ Error checking"


def get_camera_status(cfg) -> str:
    """Get camera status string."""
    return "✅ Enabled" if cfg.camera.mode != "disabled" else "❌ Disabled"


def count_jobs_by_state(jobs: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count jobs by state.

    Args:
        jobs: List of job dictionaries

    Returns:
        Dictionary mapping states to counts
    """
    state_counts = {}
    for job in jobs:
        state = job.get("state", "UNKNOWN")
        state_counts[state] = state_counts.get(state, 0) + 1
    return state_counts


def get_queue_summary(jobs: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get queue summary statistics.

    Args:
        jobs: List of job dictionaries

    Returns:
        Dictionary with queue statistics
    """
    queue_count = len(jobs)
    ready_count = sum(1 for job in jobs if job.get("state") == "READY")
    completed_count = sum(1 for job in jobs if job.get("state") == "COMPLETED")
    failed_count = sum(1 for job in jobs if job.get("state") == "FAILED")

    return {
        "total": queue_count,
        "ready": ready_count,
        "completed": completed_count,
        "failed": failed_count,
    }
