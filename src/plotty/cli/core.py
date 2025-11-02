"""
Core utilities and shared functionality for CLI commands.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from ..config import load_config


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

        return sorted(job_ids)
    except Exception:
        return []
