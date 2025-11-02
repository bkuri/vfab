"""
Statistics commands for ploTTY CLI.
"""

from __future__ import annotations

from pathlib import Path
import json
import typer
from datetime import datetime

from ..config import load_config
from ..utils import error_handler

try:
    from rich.console import Console

    console = Console()
except ImportError:
    console = None


# Create stats command group
stats_app = typer.Typer(help="Statistics and analytics commands")


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


def format_time(seconds):
    """Format seconds into human readable time."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"


@stats_app.command()
def tldr(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Quick stats overview (too long; didn't read)."""
    try:
        stats = get_job_stats()

        if json_output:
            # JSON output for LLM parsing
            json_stats = {
                "total_jobs": stats.get("total_jobs", 0),
                "completed_jobs": stats.get("completed_jobs", 0),
                "queued_jobs": stats.get("by_state", {}).get("QUEUED", 0),
                "failed_jobs": stats.get("failed_jobs", 0),
                "success_rate": stats.get("success_rate", 0),
                "avg_time_seconds": stats.get("avg_time", 0),
                "estimated_queue_time_seconds": stats.get("by_state", {}).get(
                    "QUEUED", 0
                )
                * stats.get("avg_time", 0),
                "device_available": True,  # Simplified check
            }
            print(json.dumps(json_stats, indent=2))
            return

        if console:
            console.print("📊 ploTTY Quick Stats")
            console.print("=" * 30)
        else:
            print("📊 ploTTY Quick Stats")
            print("=" * 30)

        # Job counts
        total = stats.get("total_jobs", 0)
        completed = stats.get("completed_jobs", 0)
        queued = stats.get("by_state", {}).get("QUEUED", 0)
        failed = stats.get("failed_jobs", 0)

        if console:
            console.print(
                f"Jobs: {total} total | {completed} completed | {queued} queued | {failed} failed"
            )
        else:
            print(
                f"Jobs: {total} total | {completed} completed | {queued} queued | {failed} failed"
            )

        # Success rate and timing
        success_rate = stats.get("success_rate", 0)
        avg_time = stats.get("avg_time", 0)

        if console:
            console.print(
                f"Success: {success_rate:.0f}% | Avg time: {format_time(avg_time)}"
            )
        else:
            print(f"Success: {success_rate:.0f}% | Avg time: {format_time(avg_time)}")

        # Queue estimate
        if queued > 0 and avg_time > 0:
            queue_time = queued * avg_time
            if console:
                console.print(f"Est. queue: {format_time(queue_time)}")
            else:
                print(f"Est. queue: {format_time(queue_time)}")

        # Device status (simplified)
        try:
            import importlib.util

            spec = importlib.util.find_spec("plotty.drivers.axidraw")
            device_status = "✅ Ready" if spec else "❌ Not available"

            if console:
                console.print(f"Device: {device_status}")
            else:
                print(f"Device: {device_status}")
        except Exception:
            if console:
                console.print("Device: ❓ Unknown")
            else:
                print("Device: ❓ Unknown")

    except Exception as e:
        error_handler.handle(e)


@stats_app.command()
def jobs(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Detailed job statistics."""
    try:
        stats = get_job_stats()

        if json_output:
            # JSON output for LLM parsing
            print(json.dumps(stats, indent=2, default=str))
            return

        if console:
            console.print("📈 Job Statistics")
            console.print("=" * 30)

            # Job states
            console.print("\nJobs by State:")
            for state, count in stats.get("by_state", {}).items():
                console.print(f"  {state}: {count}")

            # Paper types
            console.print("\nJobs by Paper:")
            for paper, count in stats.get("by_paper", {}).items():
                console.print(f"  {paper}: {count}")

            # Timing stats
            console.print("\nTiming Statistics:")
            console.print(f"  Total jobs: {stats.get('total_jobs', 0)}")
            console.print(f"  Completed: {stats.get('completed_jobs', 0)}")
            console.print(f"  Failed: {stats.get('failed_jobs', 0)}")
            console.print(f"  Success rate: {stats.get('success_rate', 0):.1f}%")
            console.print(f"  Average time: {format_time(stats.get('avg_time', 0))}")
            console.print(f"  Total time: {format_time(stats.get('total_time', 0))}")

        else:
            print("📈 Job Statistics")
            print("=" * 30)

            for key, value in stats.items():
                if key not in ["by_state", "by_paper"]:
                    print(f"  {key}: {value}")

    except Exception as e:
        error_handler.handle(e)


@stats_app.command()
def time():
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
