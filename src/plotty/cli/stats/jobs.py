"""
Job statistics commands for ploTTY.

This module provides commands for viewing job-related statistics
including completion rates, time estimates, and job history.
"""

from __future__ import annotations

from ...stats import StatisticsService
from ...utils import error_handler
from ..status.output import get_output_manager


def show_job_stats(
    limit: int = 10,
    json_output: bool = False,
    csv_output: bool = False,
):
    """Show job-related statistics."""
    try:
        output = get_output_manager()
        stats_service = StatisticsService()
        job_stats = stats_service.get_job_summary_stats()

        # Add limit handling for recent jobs if needed
        if "by_state" in job_stats:
            # Convert to a format suitable for display
            job_stats_display = {
                "summary": {
                    "total_jobs": job_stats.get("total_jobs", 0),
                    "completed_jobs": job_stats.get("completed_jobs", 0),
                    "failed_jobs": job_stats.get("failed_jobs", 0),
                    "success_rate": f"{job_stats.get('success_rate', 0):.1f}%",
                    "avg_time": f"{job_stats.get('avg_time', 0):.1f}s",
                    "total_time": f"{job_stats.get('total_time', 0):.1f}s",
                },
                "by_state": job_stats.get("by_state", {}),
                "by_paper": job_stats.get("by_paper", {}),
            }
        else:
            job_stats_display = job_stats

        # Prepare data for different formats
        json_data = job_stats

        # Build hierarchical CSV data
        hierarchical_csv_data = []

        if "summary" in job_stats_display:
            for key, value in job_stats_display["summary"].items():
                hierarchical_csv_data.append(
                    {
                        "section": "Summary",
                        "category": key,
                        "item": "",
                        "value": str(value),
                    }
                )

        if "by_state" in job_stats_display:
            for state, count in job_stats_display["by_state"].items():
                hierarchical_csv_data.append(
                    {
                        "section": "Jobs by State",
                        "category": state,
                        "item": "",
                        "value": str(count),
                    }
                )

        if "by_paper" in job_stats_display:
            for paper, count in job_stats_display["by_paper"].items():
                hierarchical_csv_data.append(
                    {
                        "section": "Jobs by Paper",
                        "category": paper,
                        "item": "",
                        "value": str(count),
                    }
                )

        # Build markdown content
        sections = []

        if "summary" in job_stats_display:
            rows = [
                f"| {key} | {value} |"
                for key, value in job_stats_display["summary"].items()
            ]
            sections.append(
                f"""## Summary
| Metric | Value |
|--------|-------|
{chr(10).join(rows)}"""
            )

        if "by_state" in job_stats_display:
            rows = [
                f"| {state} | {count} |"
                for state, count in job_stats_display["by_state"].items()
            ]
            sections.append(
                f"""## Jobs by State
| State | Count |
|-------|-------|
{chr(10).join(rows)}"""
            )

        if "by_paper" in job_stats_display:
            rows = [
                f"| {paper} | {count} |"
                for paper, count in job_stats_display["by_paper"].items()
            ]
            sections.append(
                f"""## Jobs by Paper
| Paper | Count |
|-------|-------|
{chr(10).join(rows)}"""
            )

        markdown_content = f"""# ploTTY Job Statistics

{chr(10).join(sections)}"""

        # Output using the manager
        output.print_markdown(
            content=markdown_content,
            json_data=json_data,
            hierarchical_csv_data=hierarchical_csv_data,
            json_output=json_output,
            csv_output=csv_output,
        )

    except Exception as e:
        error_handler.handle(e)
