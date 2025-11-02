"""
Batch operations commands for ploTTY CLI.
"""

from __future__ import annotations

from pathlib import Path
import json
import typer
from typing import List, Dict, Any

from ..config import load_config
from ..utils import error_handler
from ..progress import show_status
from ..multipen import detect_svg_layers

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Table = None
    Confirm = None


# Create batch command group
batch_app = typer.Typer(help="Batch operations commands")


def get_jobs_by_state(state_filter: str = "QUEUED") -> List[Dict[str, Any]]:
    """Get jobs filtered by state."""
    try:
        cfg = load_config(None)
        jobs_dir = Path(cfg.workspace) / "jobs"

        jobs = []
        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue

            job_file = job_dir / "job.json"
            if not job_file.exists():
                continue

            try:
                job_data = json.loads(job_file.read_text())
                if job_data.get("state") == state_filter:
                    jobs.append(
                        {
                            "id": job_data.get("id", job_dir.name),
                            "name": job_data.get("name", "Unknown"),
                            "path": job_dir,
                            "data": job_data,
                        }
                    )
            except Exception:
                continue

        return jobs
    except Exception as e:
        error_handler.handle(e)
        return []


def group_layers_by_pen(jobs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group all layers across jobs by pen type."""
    pen_groups = {}

    for job in jobs:
        svg_path = job["path"] / "src.svg"
        if not svg_path.exists():
            continue

        try:
            layers = detect_svg_layers(svg_path)
            for layer in layers:
                if not layer.visible:
                    continue

                pen_name = (
                    f"pen_{layer.pen_id}" if layer.pen_id is not None else "default"
                )
                if pen_name not in pen_groups:
                    pen_groups[pen_name] = []

                pen_groups[pen_name].append(
                    {
                        "job": job,
                        "layer": layer,
                    }
                )
        except Exception:
            continue

    return pen_groups


def calculate_pen_optimization(
    pen_groups: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Calculate optimization benefits of pen-based planning."""
    total_layers = sum(len(layers) for layers in pen_groups.values())
    traditional_swaps = len(pen_groups) * len(
        pen_groups.get("default", [])
    )  # Rough estimate
    optimized_swaps = len(pen_groups)

    return {
        "total_layers": total_layers,
        "traditional_swaps": traditional_swaps,
        "optimized_swaps": optimized_swaps,
        "swap_reduction": traditional_swaps - optimized_swaps,
        "reduction_percentage": (
            (traditional_swaps - optimized_swaps) / traditional_swaps * 100
        )
        if traditional_swaps > 0
        else 0,
    }


@batch_app.command()
def plan_all(
    by_pen: bool = typer.Option(False, "--by-pen", help="Group optimization by pen"),
    apply: bool = typer.Option(False, "--apply", help="Apply planning changes"),
    state: str = typer.Option("QUEUED", "--state", help="Filter by job state"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output"),
    verbose: bool = typer.Option(False, "--verbose", help="Detailed output"),
    confirm: bool = typer.Option(
        None,
        "--confirm/--no-confirm",
        help="Ask for confirmation before applying changes",
    ),
):
    """Plan multiple jobs with pen optimization (implicit dry-run without --apply)."""
    try:
        cfg = load_config(None)
        jobs = get_jobs_by_state(state)

        if not jobs:
            if not quiet:
                show_status(f"No jobs found with state '{state}'", "warning")
            return

        # Always show preview unless --apply is used
        if by_pen:
            # Group layers by pen across all jobs
            pen_groups = group_layers_by_pen(jobs)
            optimization = calculate_pen_optimization(pen_groups)

            if json_output:
                # JSON output for LLM parsing
                plan_data = {
                    "mode": "pen_optimized",
                    "optimization": optimization,
                    "pen_groups": {
                        pen_name: [
                            {
                                "job_id": item["job"]["id"],
                                "job_name": item["job"]["name"],
                                "layer_name": item["layer"].name,
                                "layer_elements": len(item["layer"].elements)
                                if hasattr(item["layer"], "elements")
                                else 0,
                            }
                            for item in layers
                        ]
                        for pen_name, layers in pen_groups.items()
                    },
                    "total_jobs": len(jobs),
                    "dry_run": not apply,
                    "apply_command": "plotty batch plan-all --by-pen --apply",
                }
                if verbose:
                    plan_data["verbose_info"] = {
                        "processing_time": "unknown",
                        "job_details": [
                            {
                                "id": job["id"],
                                "name": job["name"],
                                "path": str(job["path"]),
                            }
                            for job in jobs
                        ],
                    }
                print(json.dumps(plan_data, indent=2, default=str))
            elif not quiet:
                # Display optimization preview
                if console:
                    console.print("🖊️  Pen-Optimized Planning Preview")
                    console.print("=" * 50)

                    # Optimization summary
                    console.print(
                        f"💡 Optimization: {optimization['traditional_swaps']} pen swaps → {optimization['optimized_swaps']} pen swaps ({optimization['reduction_percentage']:.0f}% reduction)"
                    )

                    # Pen groups table
                    if Table is not None:
                        table = Table(title="Pen Grouping")
                        table.add_column("Pen", style="cyan")
                        table.add_column("Jobs", style="white", justify="right")
                        table.add_column("Layers", style="white", justify="right")
                        table.add_column("Est. Time", style="white", justify="right")

                        for pen_name, layers in pen_groups.items():
                            job_count = len(set(item["job"]["id"] for item in layers))
                            layer_count = len(layers)

                            table.add_row(
                                pen_name,
                                str(job_count),
                                str(layer_count),
                                "Unknown",  # TODO: Calculate time estimates
                            )

                        console.print(table)

                    # Call to action
                    if apply:
                        console.print("\n✅ Applying pen-optimized planning...")
                    else:
                        console.print(
                            "\n📋 Preview mode - to apply these optimizations:"
                        )
                        console.print("    plotty batch plan-all --by-pen --apply")
                else:
                    print("🖊️  Pen-Optimized Planning Preview")
                    print("=" * 50)
                    print(
                        f"💡 Optimization: {optimization['traditional_swaps']} pen swaps → {optimization['optimized_swaps']} pen swaps ({optimization['reduction_percentage']:.0f}% reduction)"
                    )
                    print("\nPen Groups:")
                    for pen_name, layers in pen_groups.items():
                        job_count = len(set(item["job"]["id"] for item in layers))
                        print(f"  {pen_name}: {job_count} jobs, {len(layers)} layers")

                    if apply:
                        print("\n✅ Applying pen-optimized planning...")
                    else:
                        print(
                            "\nPreview mode - to apply: plotty batch plan-all --by-pen --apply"
                        )

            if apply:
                # Ask for confirmation unless --no-confirm is specified
                if confirm is not False and console and Confirm:
                    if not Confirm.ask(
                        f"\nApply pen-optimized planning to {len(jobs)} jobs?"
                    ):
                        if not quiet:
                            show_status("Planning cancelled by user", "info")
                        return

                # TODO: Implement actual pen-optimized planning
                if not quiet:
                    show_status("Pen-optimized planning not yet implemented", "warning")
                return

        else:
            # Traditional planning (all jobs individually)
            if json_output:
                plan_data = {
                    "mode": "traditional",
                    "jobs": [
                        {
                            "id": job["id"],
                            "name": job["name"],
                            "state": job["data"]["state"],
                        }
                        for job in jobs
                    ],
                    "total_jobs": len(jobs),
                    "dry_run": not apply,
                    "apply_command": "plotty batch plan-all --apply",
                }
                if verbose:
                    plan_data["verbose_info"] = {
                        "job_paths": [str(job["path"]) for job in jobs],
                        "processing_details": "traditional mode processes jobs individually",
                    }
                print(json.dumps(plan_data, indent=2, default=str))
            elif not quiet:
                if console:
                    console.print(f"📋 Traditional Planning Preview ({len(jobs)} jobs)")
                    console.print("=" * 50)

                    if Table is not None:
                        table = Table(title="Jobs to Plan")
                        table.add_column("ID", style="cyan")
                        table.add_column("Name", style="white")
                        table.add_column("State", style="white")

                        for job in jobs:
                            table.add_row(
                                job["id"],
                                job["name"][:30],
                                job["data"]["state"],
                            )

                        console.print(table)

                    if apply:
                        console.print("\n✅ Applying traditional planning...")
                    else:
                        console.print("\n📋 Preview mode - to apply planning:")
                        console.print("    plotty batch plan-all --apply")
                else:
                    print(f"📋 Traditional Planning Preview ({len(jobs)} jobs)")
                    print("=" * 50)
                    for job in jobs:
                        print(f"  {job['id']}: {job['name']} ({job['data']['state']})")

                    if apply:
                        print("\n✅ Applying traditional planning...")
                    else:
                        print(
                            "\nPreview mode - to apply: plotty batch plan-all --apply"
                        )

        if apply and not by_pen:
            # Ask for confirmation unless --no-confirm is specified
            if confirm is not False and console and Confirm:
                if not Confirm.ask(
                    f"\nApply traditional planning to {len(jobs)} jobs?"
                ):
                    if not quiet:
                        show_status("Planning cancelled by user", "info")
                    return

            # Implement traditional batch planning
            from ..planner import plan_layers
            from ..db import get_session
            from ..models import Pen
            from datetime import datetime

            # Get available pens from database
            with get_session() as session:
                pens = session.query(Pen).all()
                available_pens = [
                    {
                        "id": p.id,
                        "name": p.name,
                        "width_mm": p.width_mm,
                        "speed_cap": p.speed_cap,
                        "pressure": p.pressure,
                        "passes": p.passes,
                    }
                    for p in pens
                ]

            # Plan each job individually
            successful_plans = []
            failed_plans = []

            for job in jobs:
                job_id = job["id"]
                try:
                    job_dir = job["path"]
                    src_svg = job_dir / "src.svg"

                    if not src_svg.exists():
                        failed_plans.append(
                            {"id": job_id, "error": "Source SVG not found"}
                        )
                        continue

                    # Create default pen mapping (all layers use default pen)
                    from ..multipen import detect_svg_layers

                    layers = detect_svg_layers(src_svg)
                    pen_map = {layer.name: "0.3mm black" for layer in layers}

                    # Plan the job
                    plan_result = plan_layers(
                        src_svg=src_svg,
                        preset="fast",  # Use fast preset for planning
                        presets_file=cfg.vpype.presets_file,
                        pen_map=pen_map,
                        out_dir=job_dir,
                        available_pens=available_pens,
                        interactive=False,
                        paper_size=job["data"].get("paper", "A4"),
                    )

                    # Save planning results
                    plan_file = job_dir / "plan.json"
                    plan_file.write_text(json.dumps(plan_result, indent=2, default=str))

                    # Update job state to OPTIMIZED
                    job_data = job["data"]
                    job_data["state"] = "OPTIMIZED"
                    job_data["planned_at"] = datetime.now().isoformat()
                    job_data["plan_result"] = plan_result

                    job_file = job_dir / "job.json"
                    job_file.write_text(json.dumps(job_data, indent=2))

                    successful_plans.append(job_id)

                except Exception as e:
                    failed_plans.append({"id": job_id, "error": str(e)})

            # Report results
            if not quiet:
                if successful_plans:
                    show_status(
                        f"Successfully planned {len(successful_plans)} jobs", "success"
                    )
                    if verbose:
                        for job_id in successful_plans:
                            print(f"  ✓ {job_id}")

                if failed_plans:
                    show_status(f"Failed to plan {len(failed_plans)} jobs", "error")
                    if verbose:
                        for failure in failed_plans:
                            print(f"  ✗ {failure['id']}: {failure['error']}")

            if json_output:
                result_data = {
                    "mode": "traditional",
                    "results": {
                        "successful": successful_plans,
                        "failed": failed_plans,
                        "total_processed": len(successful_plans) + len(failed_plans),
                    },
                }
                print(json.dumps(result_data, indent=2, default=str))

    except Exception as e:
        error_handler.handle(e)


@batch_app.command()
def plot_all(
    by_pen: bool = typer.Option(False, "--by-pen", help="Group plotting by pen"),
    apply: bool = typer.Option(False, "--apply", help="Execute plotting"),
    preset: str = typer.Option(None, "--preset", help="Plot preset for all jobs"),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output"),
    verbose: bool = typer.Option(False, "--verbose", help="Detailed output"),
    confirm: bool = typer.Option(
        None, "--confirm/--no-confirm", help="Ask for confirmation before plotting"
    ),
):
    """Plot multiple jobs with pen optimization."""
    try:
        jobs = get_jobs_by_state("READY")  # Only plot ready jobs

        if not jobs:
            if not quiet:
                show_status("No READY jobs found for plotting", "warning")
            return

        if by_pen:
            pen_groups = group_layers_by_pen(jobs)

            if not quiet:
                if console:
                    console.print("📋 Plotting Guide Preview")
                    console.print("=" * 50)

                    step_num = 1
                    for pen_name, layers in pen_groups.items():
                        console.print(f"\n🖊️  Step {step_num}: Load {pen_name} pen")
                        console.print("   Ready to plot:")

                        for item in layers:
                            job = item["job"]
                            layer = item["layer"]
                            if verbose:
                                console.print(
                                    f"   • {job['name']} - {layer.name} ({len(layer.elements)} elements)"
                                )
                            else:
                                console.print(f"   • {job['name']} - {layer.name}")

                        step_num += 1

                    console.print("\n🎯 To execute guided plotting:")
                    console.print("    plotty batch plot-all --by-pen --apply")
                else:
                    print("📋 Plotting Guide Preview")
                    print("=" * 50)
                    step_num = 1
                    for pen_name, layers in pen_groups.items():
                        print(f"\nStep {step_num}: Load {pen_name} pen")
                        print("   Ready to plot:")
                        for item in layers:
                            job = item["job"]
                            layer = item["layer"]
                            if verbose:
                                print(
                                    f"   • {job['name']} - {layer.name} ({len(layer.elements)} elements)"
                                )
                            else:
                                print(f"   • {job['name']} - {layer.name}")
                        step_num += 1
                    print("\nTo execute: plotty batch plot-all --by-pen --apply")

        if apply:
            # Ask for confirmation unless --no-confirm is specified
            if confirm is not False and console and Confirm:
                action = "pen-optimized plotting" if by_pen else "batch plotting"
                if not Confirm.ask(f"\nExecute {action} for {len(jobs)} jobs?"):
                    if not quiet:
                        show_status("Plotting cancelled by user", "info")
                    return

            # TODO: Implement actual plotting execution
            if not quiet:
                show_status("Batch plotting execution not yet implemented", "warning")

    except Exception as e:
        error_handler.handle(e)


@batch_app.command()
def clear_queue(
    state: str = typer.Option(None, "--state", help="Filter by job state"),
    older_than: str = typer.Option(
        None, "--older-than", help="Clear jobs older than duration (e.g., 7d, 24h)"
    ),
    apply: bool = typer.Option(False, "--apply", help="Apply changes"),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output"),
    verbose: bool = typer.Option(False, "--verbose", help="Detailed output"),
    confirm: bool = typer.Option(
        None, "--confirm/--no-confirm", help="Ask for confirmation before clearing"
    ),
):
    """Clear jobs from queue with filtering options."""
    try:
        # Get jobs for verbose output and confirmation
        jobs = get_jobs_by_state(state or "QUEUED")

        # TODO: Implement queue clearing logic
        if not quiet:
            if state:
                show_status(f"Would clear jobs with state '{state}'", "info")
            if older_than:
                show_status(f"Would clear jobs older than '{older_than}'", "info")

            if apply:
                # Ask for confirmation unless --no-confirm is specified
                if confirm is not False and console and Confirm:
                    if not Confirm.ask(f"\nClear {len(jobs)} jobs from queue?"):
                        show_status("Queue clearing cancelled by user", "info")
                        return

                show_status("Queue clearing not yet implemented", "warning")
            else:
                show_status("Preview mode - use --apply to execute", "info")

        if verbose:
            # Additional verbose information
            print(f"Found {len(jobs)} jobs matching criteria")
            for job in jobs[:5]:  # Show first 5 jobs
                print(f"  - {job['id']}: {job['name']}")
            if len(jobs) > 5:
                print(f"  ... and {len(jobs) - 5} more jobs")

    except Exception as e:
        error_handler.handle(e)
