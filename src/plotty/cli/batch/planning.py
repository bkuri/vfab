"""
Batch planning commands.
"""

from __future__ import annotations

import json
from datetime import datetime

import typer

from ...config import load_config
from ...utils import error_handler
from ...progress import show_status
from ...planner import plan_layers
from ...db import get_session
from ...models import Pen
from ...multipen import detect_svg_layers
from ..status.output import get_output_manager
from .utils import get_jobs_by_state, group_layers_by_pen, calculate_pen_optimization

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Confirm

    console = Console()
except ImportError:
    console = None
    Table = None
    Confirm = None


def plan_all(
    by_pen: bool = typer.Option(
        False,
        "--by-pen",
        help="Group optimization by pen to minimize pen changes during plotting",
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Apply planning changes (default: preview mode only)"
    ),
    state: str = typer.Option(
        "QUEUED", "--state", help="Filter by job state (QUEUED, OPTIMIZED, READY, etc.)"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output in JSON format (useful for scripting/automation)"
    ),
    csv_output: bool = typer.Option(False, "--csv", help="Output in CSV format"),
    quiet: bool = typer.Option(
        False, "--quiet", help="Minimal output (show only essential information)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Detailed output (show processing details and job paths)",
    ),
    confirm: bool = typer.Option(
        None,
        "--confirm/--no-confirm",
        help="Ask for confirmation before applying changes (default: ask)",
    ),
):
    """Plan multiple jobs with pen optimization.

    Examples:
        plotty batch plan-all --by-pen --apply
        plotty batch plan-all --state OPTIMIZED --json
        plotty batch plan-all --by-pen --verbose --apply

    Without --apply, shows preview of optimization benefits only.
    Pen optimization can reduce pen changes by 50-90% for multi-layer plots.
    """
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
                                "layer_elements": (
                                    len(item["layer"].elements)
                                    if hasattr(item["layer"], "elements")
                                    else 0
                                ),
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
            elif csv_output:
                # CSV output for planning data
                output = get_output_manager()

                # Build hierarchical CSV data for optimization summary
                hierarchical_csv_data = [
                    {
                        "section": "Optimization",
                        "category": "Traditional Swaps",
                        "item": "",
                        "value": str(optimization["traditional_swaps"]),
                    },
                    {
                        "section": "Optimization",
                        "category": "Optimized Swaps",
                        "item": "",
                        "value": str(optimization["optimized_swaps"]),
                    },
                    {
                        "section": "Optimization",
                        "category": "Reduction",
                        "item": "",
                        "value": f"{optimization['reduction_percentage']:.0f}%",
                    },
                    {
                        "section": "Summary",
                        "category": "Total Jobs",
                        "item": "",
                        "value": str(len(jobs)),
                    },
                    {
                        "section": "Summary",
                        "category": "Pen Groups",
                        "item": "",
                        "value": str(len(pen_groups)),
                    },
                ]

                # Build tabular CSV data for pen groups
                tabular_csv_data = {
                    "headers": ["Pen", "Jobs", "Layers", "Est. Time"],
                    "rows": [
                        {
                            "Pen": pen_name,
                            "Jobs": str(len(set(item["job"]["id"] for item in layers))),
                            "Layers": str(len(layers)),
                            "Est. Time": "Unknown",  # TODO: Calculate time estimates
                        }
                        for pen_name, layers in pen_groups.items()
                    ],
                }

                output.print_hierarchical_csv(data=hierarchical_csv_data)
                output.print_tabular_csv(
                    data=tabular_csv_data["rows"], headers=tabular_csv_data["headers"]
                )
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

                # Process each pen group
                successful_plans = []
                failed_plans = []
                pen_groups = group_layers_by_pen(jobs)

                for pen_name, layers in pen_groups.items():
                    try:
                        if not quiet:
                            show_status(
                                f"Planning pen group: {pen_name} ({len(layers)} layers)",
                                "info",
                            )

                        # Plan each layer individually for now (simplified approach)
                        for item in layers:
                            job = item["job"]
                            layer = item["layer"]
                            job_id = job["id"]
                            job_dir = job["path"]

                            # Create pen mapping for this layer
                            pen_map = {layer.name: pen_name}

                            # Plan the layer
                            layer_svg = job_dir / "layers" / f"{layer.name}.svg"
                            if layer_svg.exists():
                                plan_result = plan_layers(
                                    src_svg=layer_svg,
                                    preset="fast",
                                    presets_file=cfg.vpype.presets_file,
                                    pen_map=pen_map,
                                    out_dir=job_dir,
                                    available_pens=available_pens,
                                    interactive=False,
                                    paper_size=job["data"].get("paper", "A3"),
                                )

                                # Save planning results
                                plan_file = job_dir / "plan.json"
                                plan_file.write_text(
                                    json.dumps(plan_result, indent=2, default=str)
                                )

                                # Update job state
                                job_data = job["data"]
                                job_data["state"] = "OPTIMIZED"
                                job_data["planned_at"] = datetime.now().isoformat()
                                job_data["pen_group"] = pen_name
                                job_data["plan_result"] = plan_result

                                job_file = job_dir / "job.json"
                                job_file.write_text(json.dumps(job_data, indent=2))

                        successful_plans.append(pen_name)

                    except Exception as pen_error:
                        failed_plans.append(
                            {
                                "pen": pen_name,
                                "error": f"Failed to plan pen group: {str(pen_error)}",
                            }
                        )

                # Report results
                if not quiet:
                    if successful_plans:
                        show_status(
                            f"Successfully planned {len(successful_plans)} pen groups",
                            "success",
                        )
                        if verbose:
                            for pen_name in successful_plans:
                                print(f"  ✓ {pen_name}")

                    if failed_plans:
                        show_status(
                            f"Failed to plan {len(failed_plans)} pen groups", "error"
                        )
                        if verbose:
                            for failure in failed_plans:
                                print(f"  ✗ {failure['pen']}: {failure['error']}")

                    # Show optimization summary
                    optimization = calculate_pen_optimization(pen_groups)
                    if console:
                        console.print("\n📊 Optimization Summary:")
                        console.print(
                            f"   Traditional pen swaps: {optimization['traditional_swaps']}"
                        )
                        console.print(
                            f"   Optimized pen swaps: {optimization['optimized_swaps']}"
                        )
                        console.print(
                            f"   Reduction: {optimization['reduction_percentage']:.0f}%"
                        )

                if json_output:
                    result_data = {
                        "mode": "pen_optimized",
                        "results": {
                            "successful": successful_plans,
                            "failed": failed_plans,
                            "total_pen_groups": len(successful_plans)
                            + len(failed_plans),
                            "optimization": calculate_pen_optimization(pen_groups),
                        },
                    }
                    print(json.dumps(result_data, indent=2, default=str))

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
            elif csv_output:
                # CSV output for traditional planning
                output = get_output_manager()

                # Build hierarchical CSV data for summary
                hierarchical_csv_data = [
                    {
                        "section": "Planning",
                        "category": "Mode",
                        "item": "",
                        "value": "Traditional",
                    },
                    {
                        "section": "Planning",
                        "category": "Total Jobs",
                        "item": "",
                        "value": str(len(jobs)),
                    },
                    {
                        "section": "Planning",
                        "category": "Dry Run",
                        "item": "",
                        "value": str(not apply),
                    },
                ]

                # Build tabular CSV data for jobs
                tabular_csv_data = {
                    "headers": ["ID", "Name", "State"],
                    "rows": [
                        {
                            "ID": job["id"],
                            "Name": job["name"],
                            "State": job["data"]["state"],
                        }
                        for job in jobs
                    ],
                }

                output.print_hierarchical_csv(data=hierarchical_csv_data)
                output.print_tabular_csv(
                    data=tabular_csv_data["rows"], headers=tabular_csv_data["headers"]
                )
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
