"""
Job details status commands for vfab.

This module provides commands for viewing detailed information
about specific jobs, including plans, layers, and error information.
"""

from __future__ import annotations

from pathlib import Path

from ...config import load_config
from ...utils import error_handler, create_job_error
from .utils import (
    load_job_data,
    load_plan_data,
    format_time,
)
from .output import get_output_manager


def show_job_details(
    job_id: str,
    json_output: bool = False,
    csv_output: bool = False,
):
    """Show detailed information about a specific job."""
    try:
        output = get_output_manager()
        cfg = load_config(None)
        job_dir = Path(cfg.workspace) / "jobs" / job_id

        if not job_dir.exists():
            raise create_job_error(f"Job {job_id} not found", job_id=job_id)

        # Load job data
        job_data = load_job_data(job_dir)
        if not job_data:
            raise create_job_error(
                f"Job metadata not found for {job_id}", job_id=job_id
            )

        # Load plan data if available
        plan_data = load_plan_data(job_dir)
        layers = plan_data.get("layers", []) if plan_data else []
        estimates = plan_data.get("estimates", {}) if plan_data else {}

        # Prepare data for different formats
        json_data = {
            "job": job_data,
            "plan": plan_data,
            "layers": layers,
            "estimates": estimates,
        }

        # Build hierarchical CSV data for job info
        hierarchical_csv_data = [
            {
                "section": "Job Details",
                "category": "ID",
                "item": "",
                "value": job_data.get("id", "Unknown"),
            },
            {
                "section": "Job Details",
                "category": "Name",
                "item": "",
                "value": job_data.get("name", "Unknown"),
            },
            {
                "section": "Job Details",
                "category": "State",
                "item": "",
                "value": job_data.get("state", "UNKNOWN"),
            },
            {
                "section": "Job Details",
                "category": "Config Status",
                "item": "",
                "value": job_data.get("config_status", "DEFAULTS"),
            },
            {
                "section": "Job Details",
                "category": "Paper",
                "item": "",
                "value": job_data.get("paper", "Unknown"),
            },
        ]

        if "created_at" in job_data:
            hierarchical_csv_data.append(
                {
                    "section": "Job Details",
                    "category": "Created",
                    "item": "",
                    "value": job_data["created_at"],
                }
            )
        if "updated_at" in job_data:
            hierarchical_csv_data.append(
                {
                    "section": "Job Details",
                    "category": "Updated",
                    "item": "",
                    "value": job_data["updated_at"],
                }
            )

        # Build tabular CSV data for layers
        tabular_csv_data = None

        if plan_data:
            hierarchical_csv_data.extend(
                [
                    {
                        "section": "Plan Information",
                        "category": "Layers",
                        "item": "",
                        "value": str(len(layers)),
                    },
                ]
            )

            if estimates:
                hierarchical_csv_data.extend(
                    [
                        {
                            "section": "Plan Information",
                            "category": "Pre-optimization time",
                            "item": "",
                            "value": format_time(estimates.get("pre_s")),
                        },
                        {
                            "section": "Plan Information",
                            "category": "Post-optimization time",
                            "item": "",
                            "value": format_time(estimates.get("post_s")),
                        },
                    ]
                )

                if "pre_s" in estimates and "post_s" in estimates:
                    improvement = (
                        (estimates["pre_s"] - estimates["post_s"]) / estimates["pre_s"]
                    ) * 100
                    hierarchical_csv_data.append(
                        {
                            "section": "Plan Information",
                            "category": "Time improvement",
                            "item": "",
                            "value": f"{improvement:.1f}%",
                        }
                    )

            total_segments = sum(layer.get("segments", 0) for layer in layers)
            hierarchical_csv_data.append(
                {
                    "section": "Plan Information",
                    "category": "Total segments",
                    "item": "",
                    "value": f"{total_segments:,}",
                }
            )

            if layers:
                layer_headers = ["Layer", "Color", "Segments", "Time"]
                layer_rows = []

                for i, layer in enumerate(layers, 1):
                    layer_rows.append(
                        {
                            "Layer": str(i),
                            "Color": layer.get("color", "Unknown"),
                            "Segments": str(layer.get("segments", 0)),
                            "Time": format_time(layer.get("time_s")),
                        }
                    )

                tabular_csv_data = {
                    "headers": layer_headers,
                    "rows": layer_rows,
                }

        if job_data.get("state") == "FAILED" and "error" in job_data:
            hierarchical_csv_data.extend(
                [
                    {
                        "section": "Error Information",
                        "category": "Error",
                        "item": "",
                        "value": job_data["error"],
                    },
                ]
            )

            # All CSV data is now built in hierarchical_csv_data and tabular_csv_data above

        # Build markdown content
        job_info_rows = [
            f"| ID | {job_data.get('id', 'Unknown')} |",
            f"| Name | {job_data.get('name', 'Unknown')} |",
            f"| State | {job_data.get('state', 'UNKNOWN')} |",
            f"| Config Status | {job_data.get('config_status', 'DEFAULTS')} |",
            f"| Paper | {job_data.get('paper', 'Unknown')} |",
        ]

        if "created_at" in job_data:
            job_info_rows.append(f"| Created | {job_data['created_at']} |")
        if "updated_at" in job_data:
            job_info_rows.append(f"| Updated | {job_data['updated_at']} |")

        job_info_table = "\n".join(job_info_rows)

        # Build plan information
        plan_section = ""
        if plan_data:
            plan_info_rows = [f"| Layers | {len(layers)} |"]

            if estimates:
                plan_info_rows.extend(
                    [
                        f"| Pre-optimization time | {format_time(estimates.get('pre_s'))} |",
                        f"| Post-optimization time | {format_time(estimates.get('post_s'))} |",
                    ]
                )

                if "pre_s" in estimates and "post_s" in estimates:
                    improvement = (
                        (estimates["pre_s"] - estimates["post_s"]) / estimates["pre_s"]
                    ) * 100
                    plan_info_rows.append(f"| Time improvement | {improvement:.1f}% |")

            total_segments = sum(layer.get("segments", 0) for layer in layers)
            plan_info_rows.append(f"| Total segments | {total_segments:,} |")

            plan_info_table = "\n".join(plan_info_rows)

            # Build layer details
            layer_section = ""
            if layers:
                layer_rows = []
                for i, layer in enumerate(layers, 1):
                    layer_rows.append(
                        f"| {i} | {layer.get('color', 'Unknown')} | "
                        f"{layer.get('segments', 0):,} | "
                        f"{format_time(layer.get('time_s'))} |"
                    )
                layer_table = "\n".join(layer_rows)
                layer_section = f"""

### Layer Details
| Layer | Color | Segments | Time |
|-------|-------|----------|------|
{layer_table}"""

            plan_section = f"""

## Plan Information
| Metric | Value |
|--------|-------|
{plan_info_table}{layer_section}"""

        # Build error section
        error_section = ""
        if job_data.get("state") == "FAILED" and "error" in job_data:
            error_section = f"""

## Error Information
```
{job_data["error"]}
```"""

        markdown_content = f"""# Job Details: {job_data.get("name", "Unknown")}

## Job Information
| Property | Value |
|----------|-------|
{job_info_table}{plan_section}{error_section}"""

        # Output using the manager
        output.print_markdown(
            content=markdown_content,
            json_data=json_data,
            hierarchical_csv_data=hierarchical_csv_data,
            tabular_csv_data=tabular_csv_data,
            json_output=json_output,
            csv_output=csv_output,
        )

    except Exception as e:
        error_handler.handle(e)
