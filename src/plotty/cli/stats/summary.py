"""
Statistics summary commands for ploTTY.

This module provides commands for viewing overall statistics summaries
including job counts, completion rates, and system metrics.
"""

from __future__ import annotations

from ...stats import StatisticsService
from ...utils import error_handler
from ..info.output import get_output_manager


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

        # Build hierarchical CSV data
        hierarchical_csv_data = []

        for key, value in summary.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    hierarchical_csv_data.append(
                        {
                            "section": key.title(),
                            "category": sub_key,
                            "item": "",
                            "value": str(sub_value),
                        }
                    )
            else:
                hierarchical_csv_data.append(
                    {
                        "section": key.title(),
                        "category": "",
                        "item": "",
                        "value": str(value),
                    }
                )

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
            hierarchical_csv_data=hierarchical_csv_data,
            json_output=json_output,
            csv_output=csv_output,
        )

    except Exception as e:
        error_handler.handle(e)
