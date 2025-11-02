"""Simple terminal dashboard for ploTTY.

Provides interactive menu system for common ploTTY operations.
"""

from __future__ import annotations

import logging
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from .config import load_config

logger = logging.getLogger(__name__)


def clear_screen():
    """Clear terminal screen."""
    os.system("clear" if os.name == "posix" else "cls")


def print_header():
    """Print ploTTY dashboard header."""
    print("🎨 ploTTY Dashboard - v0.0.1")
    print("=" * 50)
    print()


def get_system_status() -> Dict:
    """Get current system status."""
    status = {
        "axidraw": {"available": False, "connected": False, "port": None},
        "camera": {"enabled": False, "url": None},
        "workspace": None,
        "queue_count": 0,
        "ready_jobs": 0,
        "default_jobs": 0,
    }

    # Check AxiDraw availability
    try:
        import importlib.util

        spec = importlib.util.find_spec("plotty.drivers.axidraw")
        status["axidraw"]["available"] = spec is not None
    except Exception as e:
        logger.debug(f"Failed to check AxiDraw availability: {e}")

    # Load config for workspace and camera
    try:
        cfg = load_config(None)
        status["workspace"] = cfg.workspace
        status["camera"]["enabled"] = cfg.camera.mode != "disabled"
        status["camera"]["url"] = getattr(cfg.camera, "url", None)
    except Exception as e:
        logger.debug(f"Failed to load config: {e}")

    # Count jobs in queue
    try:
        workspace = Path(status["workspace"]) if status["workspace"] else Path.cwd()
        jobs_dir = workspace / "jobs"
        if jobs_dir.exists():
            for job_dir in jobs_dir.iterdir():
                if job_dir.is_dir():
                    job_file = job_dir / "job.json"
                    if job_file.exists():
                        try:
                            job_data = json.loads(job_file.read_text())
                            status["queue_count"] += 1

                            # Check job configuration status
                            if job_data.get("state") == "QUEUED":
                                if job_data.get("config_status") == "CONFIGURED":
                                    status["ready_jobs"] += 1
                                else:
                                    status["default_jobs"] += 1
                        except Exception as e:
                            logger.debug(f"Failed to process job {job_dir.name}: {e}")
    except Exception as e:
        logger.debug(f"Failed to count jobs in workspace: {e}")

    return status


def print_system_status(status: Dict):
    """Print system status section."""
    print("📊 System Status")
    print("├─ AxiDraw:", end=" ")
    if status["axidraw"]["available"]:
        print("✅ Available")
    else:
        print("❌ Not installed")

    print("├─ Camera:", end=" ")
    if status["camera"]["enabled"]:
        print("✅ Enabled")
    else:
        print("❌ Disabled")

    print("├─ Queue:", end=" ")
    print(f"{status['queue_count']} jobs", end="")
    if status["ready_jobs"] > 0 or status["default_jobs"] > 0:
        print(f" ({status['ready_jobs']} ready, {status['default_jobs']} defaults)")
    else:
        print()

    print("└─ Workspace:", status["workspace"] or "Unknown")
    print()


def get_job_queue() -> List[Dict]:
    """Get list of jobs in queue."""
    jobs = []

    try:
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        if not jobs_dir.exists():
            return jobs

        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue

            job_file = job_dir / "job.json"
            if not job_file.exists():
                continue

            try:
                job_data = json.loads(job_file.read_text())

                # Get plan info if available
                plan_file = job_dir / "plan.json"
                time_estimate = None
                if plan_file.exists():
                    plan_data = json.loads(plan_file.read_text())
                    time_estimate = plan_data.get("estimates", {}).get("post_s")

                jobs.append(
                    {
                        "id": job_data.get("id", job_dir.name),
                        "name": job_data.get("name", "Unknown"),
                        "state": job_data.get("state", "UNKNOWN"),
                        "config_status": job_data.get("config_status", "DEFAULTS"),
                        "paper": job_data.get("paper", "Unknown"),
                        "time_estimate": time_estimate,
                    }
                )
            except Exception as e:
                logger.debug(f"Failed to load job {job_dir.name}: {e}")
                continue

    except Exception as e:
        logger.debug(f"Failed to load jobs list: {e}")

    # Sort by creation time (simple ID sort for now)
    jobs.sort(key=lambda x: x["id"])
    return jobs


def format_time_estimate(seconds: Optional[float]) -> str:
    """Format time estimate for display."""
    if seconds is None:
        return "--"

    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.0f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_status_indicator(job: Dict) -> str:
    """Get status indicator for job."""
    if job["state"] != "QUEUED":
        return "⚪"  # Not queued

    if job["config_status"] == "CONFIGURED":
        return "🟢"  # Ready
    else:
        return "🟡"  # Defaults


def print_job_queue(jobs: List[Dict]):
    """Print job queue table."""
    if not jobs:
        print("📋 Job Queue: Empty")
        print()
        return

    print("📋 Job Queue")
    print("┌─────────────┬──────────────┬─────────┬─────────────┬─────────┐")
    print("│ Job ID      │ Name         │ Status  │ Paper       │ Time    │")
    print("├─────────────┼──────────────┼─────────┼─────────────┼─────────┤")

    for job in jobs:
        status_indicator = get_status_indicator(job)
        status_text = job["config_status"].lower()
        time_str = format_time_estimate(job["time_estimate"])

        # Truncate long names
        name = job["name"][:12] + "…" if len(job["name"]) > 12 else job["name"]

        print(
            f"│ {job['id'][:11]:11s} │ {name:12s} │ {status_indicator} {status_text:7s} │ {job['paper'][:11]:11s} │ {time_str:7s} │"
        )

    print("└─────────────┴──────────────┴─────────┴─────────────┴─────────┘")
    print()


def print_menu_options():
    """Print menu options."""
    print("📋 Quick Actions")
    print("[1] 📁 Add SVG to queue")
    print("[2] 📋 Review queued jobs")
    print("[3] 🎯 Plot next job")
    print("[4] 🖊️  Manage pens")
    print("[5] 📐 Manage papers")
    print("[6] 📊 System status")
    print("[7] 🎥 Camera setup")
    print("[8] ⚙️  Settings")
    print("[q] 👋 Quit")
    print()


def handle_choice(choice: str, jobs: List[Dict]) -> bool:
    """Handle user menu choice.

    Args:
        choice: User input
        jobs: Current job list

    Returns:
        True to continue, False to quit
    """
    choice = choice.strip().lower()

    if choice == "q":
        print("👋 Goodbye!")
        return False
    elif choice == "1":
        return handle_add_job()
    elif choice == "2":
        return handle_review_jobs(jobs)
    elif choice == "3":
        return handle_plot_next(jobs)
    elif choice == "4":
        return handle_manage_pens()
    elif choice == "5":
        return handle_manage_papers()
    elif choice == "6":
        return handle_system_status()
    elif choice == "7":
        return handle_camera_setup()
    elif choice == "8":
        return handle_settings()
    else:
        # Check if user entered a job ID
        for job in jobs:
            if job["id"].startswith(choice):
                return handle_review_job(job["id"])

        print(f"❌ Unknown option: {choice}")
        print("Try a number [1-8], job ID, or 'q' to quit")
        input("Press Enter to continue...")
        return True


def run_plotty_command(args: List[str]) -> bool:
    """Run ploTTY command and return to dashboard.

    Args:
        args: Command arguments

    Returns:
        True to continue dashboard
    """
    try:
        cmd = ["uv", "run", "python", "-m", "plotty"] + args
        subprocess.run(cmd, cwd=Path.cwd())
        input("Press Enter to continue...")
        return True
    except KeyboardInterrupt:
        print("\n❌ Command cancelled")
        input("Press Enter to continue...")
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        input("Press Enter to continue...")
        return True


def handle_add_job() -> bool:
    """Handle add job menu option."""
    print("📁 Add SVG to queue")
    print("Enter path to SVG file (or 'back' to return):")

    svg_path = input("> ").strip()
    if svg_path.lower() in ("back", "b", ""):
        return True

    if not Path(svg_path).exists():
        print("❌ File not found")
        input("Press Enter to continue...")
        return True

    print("Enter job name (optional):")
    name = input("> ").strip()

    print("Enter paper size (default: A3):")
    paper = input("> ").strip() or "A3"

    return run_plotty_command(["add", svg_path, "--name", name, "--paper", paper])


def handle_review_jobs(jobs: List[Dict]) -> bool:
    """Handle review jobs menu option."""
    if not jobs:
        print("📋 No jobs in queue")
        input("Press Enter to continue...")
        return True

    print("📋 Review Jobs")
    for i, job in enumerate(jobs, 1):
        status_indicator = get_status_indicator(job)
        print(f"[{i}] {status_indicator} {job['id'][:8]} - {job['name']}")

    print("Select job number to review (or 'back' to return):")
    choice = input("> ").strip().lower()

    if choice.lower() in ("back", "b", ""):
        return True

    try:
        job_idx = int(choice) - 1
        if 0 <= job_idx < len(jobs):
            return handle_review_job(jobs[job_idx]["id"])
        else:
            print("❌ Invalid job number")
    except ValueError:
        print("❌ Please enter a number")

    input("Press Enter to continue...")
    return True


def handle_review_job(job_id: str) -> bool:
    """Handle reviewing a specific job."""
    print(f"📋 Review Job: {job_id}")
    print("⚠️  Job review not implemented yet")
    print("This will allow editing pen mapping, paper, camera, etc.")
    input("Press Enter to continue...")
    return True


def handle_plot_next(jobs: List[Dict]) -> bool:
    """Handle plot next job menu option."""
    queued_jobs = [j for j in jobs if j["state"] == "QUEUED"]

    if not queued_jobs:
        print("🎯 No queued jobs to plot")
        input("Press Enter to continue...")
        return True

    next_job = queued_jobs[0]
    print(f"🎯 Plot next job: {next_job['name']} ({next_job['id'][:8]})")
    print("Proceed with plotting? (y/N):")

    choice = input("> ").strip().lower()
    if choice in ("y", "yes"):
        return run_plotty_command(["plot", next_job["id"]])
    else:
        print("Plotting cancelled")
        input("Press Enter to continue...")
        return True


def handle_manage_pens() -> bool:
    """Handle manage pens menu option."""
    return run_plotty_command(["pen-list"])


def handle_manage_papers() -> bool:
    """Handle manage papers menu option."""
    return run_plotty_command(["paper-list"])


def handle_system_status() -> bool:
    """Handle system status menu option."""
    print("📊 Detailed System Status")
    print("⚠️  Detailed status not implemented yet")
    print("This will show AxiDraw connection, camera status, etc.")
    input("Press Enter to continue...")
    return True


def handle_camera_setup() -> bool:
    """Handle camera setup menu option."""
    print("🎥 Camera Setup")
    print("⚠️  Camera setup not implemented yet")
    print("This will configure IP camera, recording settings, etc.")
    input("Press Enter to continue...")
    return True


def handle_settings() -> bool:
    """Handle settings menu option."""
    print("⚙️  Settings")
    print("⚠️  Settings not implemented yet")
    print("This will show/edit ploTTY configuration.")
    input("Press Enter to continue...")
    return True


def show_dashboard():
    """Show interactive ploTTY dashboard."""
    while True:
        clear_screen()
        print_header()

        # Get and display system status
        status = get_system_status()
        print_system_status(status)

        # Get and display job queue
        jobs = get_job_queue()
        print_job_queue(jobs)

        # Show menu options
        print_menu_options()

        # Get user input
        choice = input("Select action [1-8], job ID, or 'q' to quit: ").strip()

        # Handle choice
        if not handle_choice(choice, jobs):
            break  # User chose to quit


if __name__ == "__main__":
    show_dashboard()
