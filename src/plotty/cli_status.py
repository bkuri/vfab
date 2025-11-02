"""
CLI status commands for ploTTY.

Provides quick status commands for checking system status,
job queue, and individual job information without needing
to launch the full dashboard.
"""

from __future__ import annotations

import logging
import json
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table

from .config import load_config
from .utils import error_handler

logger = logging.getLogger(__name__)

# Create console for rich output
console = Console()

# Create status command group
status_app = typer.Typer(
    help="Status and monitoring commands", invoke_without_command=True
)


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


def complete_job_id(ctx: typer.Context, args: List[str], incomplete: str) -> List[str]:
    """Autocomplete function for job IDs."""
    available_ids = get_available_job_ids()
    return [job_id for job_id in available_ids if job_id.startswith(incomplete)]


@status_app.callback()
def show_status_overview(
    ctx: typer.Context,
    markdown: bool = typer.Option(
        False, "--markdown", "-m", help="Export status as markdown"
    ),
    json_output: bool = typer.Option(False, "--json", help="Export status as JSON"),
):
    """Show complete status overview or run subcommands."""
    if ctx.invoked_subcommand is None:
        # Show complete status overview when no subcommand is provided
        try:
            # Load configuration
            cfg = load_config(None)

            if json_output:
                # JSON output for LLM parsing
                status_data = {
                    "system": {
                        "axidraw_available": axidraw_status == "✅ Available",
                        "camera_enabled": cfg.camera.mode != "disabled",
                        "workspace": cfg.workspace,
                    },
                    "queue": {
                        "total_jobs": queue_count,
                        "ready_jobs": ready_count,
                    },
                    "jobs": jobs,  # Will be populated below
                }
                print(json.dumps(status_data, indent=2, default=str))
                return

            if markdown:
                # Markdown output for piping to files
                print("# ploTTY Status Report")
                print()

                # System status
                print("## System Status")
                print("| Component | Status |")
                print("|-----------|--------|")

                # Check AxiDraw availability
                try:
                    import importlib.util

                    spec = importlib.util.find_spec("plotty.drivers.axidraw")
                    axidraw_status = "✅ Available" if spec else "❌ Not installed"
                except Exception:
                    axidraw_status = "❌ Error checking"
                print(f"| AxiDraw | {axidraw_status} |")

                # Camera status
                camera_status = (
                    "✅ Enabled" if cfg.camera.mode != "disabled" else "❌ Disabled"
                )
                print(f"| Camera | {camera_status} |")
                print(f"| Workspace | {cfg.workspace} |")

                # Count jobs
                jobs_dir = Path(cfg.workspace) / "jobs"
                queue_count = 0
                ready_count = 0
                state_counts = {}

                if jobs_dir.exists():
                    for job_dir in jobs_dir.iterdir():
                        if job_dir.is_dir():
                            job_file = job_dir / "job.json"
                            if job_file.exists():
                                try:
                                    job_data = json.loads(job_file.read_text())
                                    queue_count += 1
                                    state = job_data.get("state", "UNKNOWN")
                                    state_counts[state] = state_counts.get(state, 0) + 1
                                    if (
                                        state == "QUEUED"
                                        and job_data.get("config_status")
                                        == "CONFIGURED"
                                    ):
                                        ready_count += 1
                                except Exception as e:
                                    logger.debug(
                                        f"Failed to read job file {job_file}: {e}"
                                    )

                print(f"| Queue | {queue_count} jobs ({ready_count} ready) |")
                print()

                # Job queue
                print("## Job Queue")
                print("| ID | Name | State | Config | Paper | Layers | Est. Time |")
                print("|----|------|-------|--------|-------|--------|-----------|")

                # Collect and sort jobs
                jobs = []
                for job_dir in jobs_dir.iterdir():
                    if not job_dir.is_dir():
                        continue
                    job_file = job_dir / "job.json"
                    if not job_file.exists():
                        continue
                    try:
                        job_data = json.loads(job_file.read_text())

                        # Get plan info
                        plan_file = job_dir / "plan.json"
                        time_estimate = None
                        layer_count = None
                        if plan_file.exists():
                            plan_data = json.loads(plan_file.read_text())
                            time_estimate = plan_data.get("estimates", {}).get("post_s")
                            layer_count = len(plan_data.get("layers", []))

                        jobs.append(
                            {
                                "id": job_data.get("id", job_dir.name),
                                "name": job_data.get("name", "Unknown"),
                                "state": job_data.get("state", "UNKNOWN"),
                                "config_status": job_data.get(
                                    "config_status", "DEFAULTS"
                                ),
                                "paper": job_data.get("paper", "Unknown"),
                                "time_estimate": time_estimate,
                                "layer_count": layer_count,
                            }
                        )
                    except Exception as e:
                        logger.debug(f"Failed to load job {job_dir.name}: {e}")
                        continue

                # Sort by state priority
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
                jobs.sort(key=lambda j: state_priority.get(j["state"], 99))

                # Print jobs
                for job in jobs[:20]:  # Limit to 20 for markdown
                    time_str = (
                        f"{job['time_estimate']:.1f}s"
                        if job["time_estimate"]
                        else "Unknown"
                    )
                    if job["time_estimate"] and job["time_estimate"] > 60:
                        time_str = f"{job['time_estimate'] / 60:.1f}m"

                    print(
                        f"| {job['id']} | {job['name'][:20]} | {job['state']} | {job['config_status']} | {job['paper']} | {job['layer_count'] or 'Unknown'} | {time_str} |"
                    )

                if len(jobs) > 20:
                    print("| ... | ... | ... | ... | ... | ... | ... |")
                    print(f"| | | | | | **{len(jobs) - 20} more jobs** | |")

                print()

                # State summary
                if state_counts:
                    print("## Jobs by State")
                    for state, count in sorted(state_counts.items()):
                        print(f"- {state}: {count}")

            else:
                # Rich console output
                # System status table
                system_table = Table(title="🎨 ploTTY System Status", show_header=False)
                system_table.add_column("Component", style="cyan")
                system_table.add_column("Status", style="white")

                # Check AxiDraw availability
                try:
                    import importlib.util

                    spec = importlib.util.find_spec("plotty.drivers.axidraw")
                    axidraw_status = "✅ Available" if spec else "❌ Not installed"
                except Exception:
                    axidraw_status = "❌ Error checking"

                system_table.add_row("AxiDraw", axidraw_status)

                # Camera status
                camera_status = (
                    "✅ Enabled" if cfg.camera.mode != "disabled" else "❌ Disabled"
                )
                system_table.add_row("Camera", camera_status)

                # Workspace
                system_table.add_row("Workspace", str(cfg.workspace))

                # Count jobs
                jobs_dir = Path(cfg.workspace) / "jobs"
                queue_count = 0
                ready_count = 0

                if jobs_dir.exists():
                    for job_dir in jobs_dir.iterdir():
                        if job_dir.is_dir():
                            job_file = job_dir / "job.json"
                            if job_file.exists():
                                try:
                                    job_data = json.loads(job_file.read_text())
                                    queue_count += 1
                                    if job_data.get("state") == "QUEUED":
                                        if (
                                            job_data.get("config_status")
                                            == "CONFIGURED"
                                        ):
                                            ready_count += 1
                                except Exception:
                                    pass

                system_table.add_row(
                    "Queue", f"{queue_count} jobs ({ready_count} ready)"
                )

                console.print(system_table)

                # Job queue table
                jobs = []
                if jobs_dir.exists():
                    for job_dir in jobs_dir.iterdir():
                        if not job_dir.is_dir():
                            continue
                        job_file = job_dir / "job.json"
                        if not job_file.exists():
                            continue
                        try:
                            job_data = json.loads(job_file.read_text())

                            # Get plan info
                            plan_file = job_dir / "plan.json"
                            time_estimate = None
                            layer_count = None
                            if plan_file.exists():
                                plan_data = json.loads(plan_file.read_text())
                                time_estimate = plan_data.get("estimates", {}).get(
                                    "post_s"
                                )
                                layer_count = len(plan_data.get("layers", []))

                            jobs.append(
                                {
                                    "id": job_data.get("id", job_dir.name),
                                    "name": job_data.get("name", "Unknown"),
                                    "state": job_data.get("state", "UNKNOWN"),
                                    "config_status": job_data.get(
                                        "config_status", "DEFAULTS"
                                    ),
                                    "paper": job_data.get("paper", "Unknown"),
                                    "time_estimate": time_estimate,
                                    "layer_count": layer_count,
                                }
                            )
                        except Exception:
                            continue

                if jobs:
                    # Sort by state priority
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
                    jobs.sort(key=lambda j: state_priority.get(j["state"], 99))

                    queue_table = Table(title=f"Job Queue ({len(jobs)} jobs)")
                    queue_table.add_column("ID", style="cyan")
                    queue_table.add_column("Name", style="white")
                    queue_table.add_column("State", style="white")
                    queue_table.add_column("Config", style="white")
                    queue_table.add_column("Paper", style="white")
                    queue_table.add_column("Layers", style="white", justify="right")
                    queue_table.add_column("Est. Time", style="white", justify="right")

                    for job in jobs[:15]:  # Show first 15 jobs
                        time_str = "Unknown"
                        if job["time_estimate"]:
                            if job["time_estimate"] < 60:
                                time_str = f"{job['time_estimate']:.1f}s"
                            else:
                                time_str = f"{job['time_estimate'] / 60:.1f}m"

                        queue_table.add_row(
                            job["id"],
                            job["name"][:20],
                            job["state"],
                            job["config_status"],
                            job["paper"],
                            str(job["layer_count"])
                            if job["layer_count"]
                            else "Unknown",
                            time_str,
                        )

                    console.print(queue_table)

                    if len(jobs) > 15:
                        console.print(f"... and {len(jobs) - 15} more jobs")

        except Exception as e:
            error_handler.handle(e)


@status_app.command("system")
def show_system_status():
    """Show overall system status."""
    try:
        # Load configuration
        cfg = load_config(None)

        # Create status table
        table = Table(title="🎨 ploTTY System Status", show_header=False)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="white")

        # Check AxiDraw availability
        try:
            import importlib.util

            spec = importlib.util.find_spec("plotty.drivers.axidraw")
            axidraw_status = "✅ Available" if spec else "❌ Not installed"
        except Exception:
            axidraw_status = "❌ Error checking"

        table.add_row("AxiDraw", axidraw_status)

        # Camera status
        camera_status = "✅ Enabled" if cfg.camera.mode != "disabled" else "❌ Disabled"
        table.add_row("Camera", camera_status)

        # Workspace
        table.add_row("Workspace", str(cfg.workspace))

        # Count jobs
        jobs_dir = Path(cfg.workspace) / "jobs"
        queue_count = 0
        ready_count = 0

        if jobs_dir.exists():
            for job_dir in jobs_dir.iterdir():
                if job_dir.is_dir():
                    job_file = job_dir / "job.json"
                    if job_file.exists():
                        try:
                            job_data = json.loads(job_file.read_text())
                            queue_count += 1
                            if job_data.get("state") == "QUEUED":
                                if job_data.get("config_status") == "CONFIGURED":
                                    ready_count += 1
                        except Exception:
                            pass

        table.add_row("Queue", f"{queue_count} jobs ({ready_count} ready)")

        console.print(table)

    except Exception as e:
        error_handler.handle(e)


@status_app.command("tldr")
def show_quick_status():
    """Show quick overview of system and queue (too long; didn't read)."""
    try:
        # Load configuration
        cfg = load_config(None)

        # Quick status line
        console.print("🎨 ploTTY Quick Status")
        console.print("=" * 30)

        # System indicators
        try:
            import importlib.util

            spec = importlib.util.find_spec("plotty.drivers.axidraw")
            axi_status = "✅" if spec else "❌"
        except Exception:
            axi_status = "❌"

        cam_status = "✅" if cfg.camera.mode != "disabled" else "❌"
        console.print(f"AxiDraw: {axi_status}  Camera: {cam_status}")

        # Queue summary
        jobs_dir = Path(cfg.workspace) / "jobs"
        queue_count = 0
        ready_count = 0

        if jobs_dir.exists():
            for job_dir in jobs_dir.iterdir():
                if job_dir.is_dir():
                    job_file = job_dir / "job.json"
                    if job_file.exists():
                        try:
                            job_data = json.loads(job_file.read_text())
                            queue_count += 1
                            if job_data.get("state") == "QUEUED":
                                if job_data.get("config_status") == "CONFIGURED":
                                    ready_count += 1
                        except Exception:
                            pass

        if queue_count > 0:
            console.print(f"Queue: {queue_count} jobs ({ready_count} ready)")
        else:
            console.print("Queue: Empty")

        # Workspace
        workspace_short = Path(cfg.workspace).name
        console.print(f"Workspace: {workspace_short}")

    except Exception as e:
        error_handler.handle(e)


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


@status_app.command("queue")
def show_job_queue(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum number of jobs to show"
    ),
    state: Optional[str] = typer.Option(
        None, "--state", "-s", help="Filter by job state"
    ),
):
    """Show jobs in the queue."""
    try:
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        if not jobs_dir.exists():
            console.print("[yellow]No jobs directory found[/yellow]")
            return

        # Collect jobs
        jobs = []

        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue

            job_file = job_dir / "job.json"
            if not job_file.exists():
                continue

            try:
                job_data = json.loads(job_file.read_text())

                # Filter by state if specified
                if state and job_data.get("state") != state:
                    continue

                # Get plan info if available
                plan_file = job_dir / "plan.json"
                time_estimate = None
                layer_count = None

                if plan_file.exists():
                    plan_data = json.loads(plan_file.read_text())
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
                    }
                )

            except Exception:
                continue

        if not jobs:
            console.print("[yellow]No jobs found[/yellow]")
            return

        # Sort by state (prioritize active jobs)
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

        jobs.sort(key=lambda j: state_priority.get(j["state"], 99))

        # Limit results
        jobs = jobs[:limit]

        # Create table
        table = Table(title=f"Job Queue (showing {len(jobs)})")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("State", style="white")
        table.add_column("Config", style="white")
        table.add_column("Paper", style="white")
        table.add_column("Layers", style="white", justify="right")
        table.add_column("Est. Time", style="white", justify="right")

        for job in jobs:
            table.add_row(
                job["id"],
                job["name"][:30],  # Truncate long names
                format_state(job["state"]),
                job["config_status"],
                job["paper"],
                str(job["layer_count"]) if job["layer_count"] else "Unknown",
                format_time(job["time_estimate"]),
            )

        console.print(table)

    except Exception as e:
        error_handler.handle(e)


@status_app.command("job")
def show_job_details(
    job_id: str = typer.Argument(
        ..., autocompletion=complete_job_id, help="Job ID to show details for"
    ),
):
    """Show detailed information about a specific job."""
    try:
        cfg = load_config(None)
        job_dir = Path(cfg.workspace) / "jobs" / job_id

        if not job_dir.exists():
            console.print(f"[red]Job {job_id} not found[/red]")
            return

        # Load job data
        job_file = job_dir / "job.json"
        if not job_file.exists():
            console.print(f"[red]Job data not found for {job_id}[/red]")
            return

        job_data = json.loads(job_file.read_text())

        # Create job details table
        table = Table(title=f"Job Details: {job_data.get('name', 'Unknown')}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("ID", job_data.get("id", "Unknown"))
        table.add_row("Name", job_data.get("name", "Unknown"))
        table.add_row("State", format_state(job_data.get("state", "UNKNOWN")))
        table.add_row("Config Status", job_data.get("config_status", "DEFAULTS"))
        table.add_row("Paper", job_data.get("paper", "Unknown"))

        # Add timestamps if available
        if "created_at" in job_data:
            table.add_row("Created", job_data["created_at"])
        if "updated_at" in job_data:
            table.add_row("Updated", job_data["updated_at"])

        console.print(table)

        # Show plan details if available
        plan_file = job_dir / "plan.json"
        if plan_file.exists():
            plan_data = json.loads(plan_file.read_text())

            console.print("\n[bold]Plan Information[/bold]")

            plan_table = Table()
            plan_table.add_column("Metric", style="cyan")
            plan_table.add_column("Value", style="white")

            # Layer information
            layers = plan_data.get("layers", [])
            plan_table.add_row("Layers", str(len(layers)))

            # Time estimates
            estimates = plan_data.get("estimates", {})
            if estimates:
                plan_table.add_row(
                    "Pre-optimization time", format_time(estimates.get("pre_s"))
                )
                plan_table.add_row(
                    "Post-optimization time", format_time(estimates.get("post_s"))
                )

                if "pre_s" in estimates and "post_s" in estimates:
                    improvement = (
                        (estimates["pre_s"] - estimates["post_s"]) / estimates["pre_s"]
                    ) * 100
                    plan_table.add_row("Time improvement", f"{improvement:.1f}%")

            # Segment information
            total_segments = sum(layer.get("segments", 0) for layer in layers)
            plan_table.add_row("Total segments", f"{total_segments:,}")

            console.print(plan_table)

            # Show layer details
            if layers:
                console.print("\n[bold]Layer Details[/bold]")

                layer_table = Table()
                layer_table.add_column("Layer", style="cyan", justify="right")
                layer_table.add_column("Color", style="white")
                layer_table.add_column("Segments", style="white", justify="right")
                layer_table.add_column("Time", style="white", justify="right")

                for i, layer in enumerate(layers, 1):
                    layer_table.add_row(
                        str(i),
                        layer.get("color", "Unknown"),
                        f"{layer.get('segments', 0):,}",
                        format_time(layer.get("time_s")),
                    )

                console.print(layer_table)

        # Show error information if failed
        if job_data.get("state") == "FAILED" and "error" in job_data:
            console.print("\n[bold red]Error Information[/bold red]")
            console.print(f"[red]{job_data['error']}[/red]")

    except Exception as e:
        error_handler.handle(e)
