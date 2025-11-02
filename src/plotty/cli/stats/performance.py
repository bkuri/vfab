"""
Performance statistics for ploTTY CLI.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from ...config import load_config
from ...utils import error_handler

try:
    from rich.console import Console

    console = Console()
except ImportError:
    console = None


def format_time(seconds):
    """Format seconds into human readable time."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"


def get_job_stats():
    """Get comprehensive job statistics."""
    try:
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        stats = {
            "total_jobs": 0,
            "by_state": {},
            "by_paper": {},
            "completed_jobs": 0,
            "failed_jobs": 0,
            "total_time": 0,
            "avg_time": 0,
            "oldest_job": None,
            "newest_job": None,
        }

        if not jobs_dir.exists():
            return stats

        job_times = []

        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue

            job_file = job_dir / "job.json"
            if not job_file.exists():
                continue

            try:
                job_data = json.loads(job_file.read_text())
                stats["total_jobs"] += 1

                # Count by state
                state = job_data.get("state", "UNKNOWN")
                stats["by_state"][state] = stats["by_state"].get(state, 0) + 1

                # Count by paper
                paper = job_data.get("paper", "Unknown")
                stats["by_paper"][paper] = stats["by_paper"].get(paper, 0) + 1

                # Track completed/failed
                if state == "COMPLETED":
                    stats["completed_jobs"] += 1
                elif state == "FAILED":
                    stats["failed_jobs"] += 1

                # Get time estimates
                plan_file = job_dir / "plan.json"
                if plan_file.exists():
                    plan_data = json.loads(plan_file.read_text())
                    time_est = plan_data.get("estimates", {}).get("post_s")
                    if time_est:
                        job_times.append(time_est)
                        stats["total_time"] += time_est

                # Track job ages
                created_at = job_data.get("created_at")
                if created_at:
                    try:
                        # Handle different timestamp formats
                        if isinstance(created_at, str):
                            job_time = datetime.fromisoformat(
                                created_at.replace("Z", "+00:00")
                            )
                        else:
                            job_time = created_at

                        if not stats["oldest_job"] or job_time < stats["oldest_job"]:
                            stats["oldest_job"] = job_time
                        if not stats["newest_job"] or job_time > stats["newest_job"]:
                            stats["newest_job"] = job_time
                    except Exception:
                        pass

            except Exception:
                continue

        # Calculate averages
        if job_times:
            stats["avg_time"] = sum(job_times) / len(job_times)

        # Calculate success rate
        if stats["total_jobs"] > 0:
            stats["success_rate"] = (
                stats["completed_jobs"] / stats["total_jobs"]
            ) * 100
        else:
            stats["success_rate"] = 0

        return stats

    except Exception as e:
        error_handler.handle(e)
        return {}


def show_performance():
    """Time usage analytics."""
    try:
        stats = get_job_stats()

        if console:
            console.print("⏱️  Time Analytics")
            console.print("=" * 30)

            total_time = stats.get("total_time", 0)
            avg_time = stats.get("avg_time", 0)
            completed = stats.get("completed_jobs", 0)

            console.print(f"Total plotting time: {format_time(total_time)}")
            console.print(f"Average job time: {format_time(avg_time)}")
            console.print(f"Completed jobs: {completed}")

            if completed > 0:
                console.print(
                    f"Time per completed job: {format_time(total_time / completed)}"
                )

            # Job age analysis
            oldest = stats.get("oldest_job")
            newest = stats.get("newest_job")

            if oldest and newest:
                age_span = newest - oldest
                console.print(f"Job age span: {age_span.days} days")

        else:
            print("⏱️  Time Analytics")
            print("=" * 30)
            print(f"Total time: {format_time(stats.get('total_time', 0))}")
            print(f"Average time: {format_time(stats.get('avg_time', 0))}")

    except Exception as e:
        error_handler.handle(e)
