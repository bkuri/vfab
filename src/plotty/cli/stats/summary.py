"""
Statistics summary commands for ploTTY.

This module provides commands for viewing overall statistics summaries
including job counts, completion rates, and system metrics.
"""

from __future__ import annotations

from ...stats import StatisticsService
from ...utils import error_handler
from ..status.output import get_output_manager


def show_stats_summary(
    json_output: bool = False,
    csv_output: bool = False,
):
    """Show overall statistics summary."""
    try:
        output = get_output_manager()
        stats_service = StatisticsService()
        summary = stats_service.get_job_summary_stats()

        # Prepare data for different formats
        json_data = summary

        # Build CSV data
        csv_data = [["ploTTY Statistics Summary"], [], ["Metric", "Value"]]

        for key, value in summary.items():
            if isinstance(value, dict):
                csv_data.append([key, ""])
                for sub_key, sub_value in value.items():
                    csv_data.append([f"  {sub_key}", str(sub_value)])
            else:
                csv_data.append([key, str(value)])

        # Build markdown content
        sections = []

        for key, value in summary.items():
            if isinstance(value, dict):
                rows = [
                    f"| {sub_key} | {sub_value} |"
                    for sub_key, sub_value in value.items()
                ]
                sections.append(
                    f"""## {key.title()}
| Metric | Value |
|--------|-------|
{chr(10).join(rows)}"""
                )
            else:
                sections.append(
                    f"""## {key.title()}
{value}"""
                )

        markdown_content = f"""# ploTTY Statistics Summary

{chr(10).join(sections)}"""

        # Output using the manager
        output.print_markdown(
            content=markdown_content,
            json_data=json_data,
            csv_data=csv_data,
            json_output=json_output,
            csv_output=csv_output,
        )

    except Exception as e:
        error_handler.handle(e)
