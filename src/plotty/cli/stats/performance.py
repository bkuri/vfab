"""
Performance statistics commands for ploTTY.

This module provides commands for viewing performance metrics
including plotting speed, efficiency trends, and system utilization.
"""

from __future__ import annotations

from ...stats import StatisticsService
from ...utils import error_handler
from ..status.output import get_output_manager


def show_performance_stats(
    days: int = 7,
    json_output: bool = False,
    csv_output: bool = False,
):
    """Show performance metrics and trends."""
    try:
        output = get_output_manager()
        stats_service = StatisticsService()
        performance_stats = stats_service.get_performance_stats()

        # Prepare data for different formats
        json_data = performance_stats

        # Build CSV data
        csv_data = [[f"ploTTY Performance Metrics ({days} days)"], []]

        if "summary" in performance_stats:
            csv_data.extend(
                [
                    ["Summary"],
                    ["Metric", "Value"],
                ]
            )
            for key, value in performance_stats["summary"].items():
                csv_data.append([key, str(value)])
            csv_data.append([])

        if "daily_metrics" in performance_stats:
            csv_data.extend(
                [
                    ["Daily Metrics"],
                    ["Date", "Jobs", "Avg Time", "Total Time"],
                ]
            )
            for metric in performance_stats["daily_metrics"]:
                csv_data.append(
                    [
                        metric.get("date", ""),
                        str(metric.get("job_count", "")),
                        str(metric.get("avg_time_seconds", "")),
                        str(metric.get("total_time_seconds", "")),
                    ]
                )

        # Build markdown content
        sections = []

        if "summary" in performance_stats:
            rows = [
                f"| {key} | {value} |"
                for key, value in performance_stats["summary"].items()
            ]
            sections.append(
                f"""## Summary
| Metric | Value |
|--------|-------|
{chr(10).join(rows)}"""
            )

        if "daily_metrics" in performance_stats:
            rows = []
            for metric in performance_stats["daily_metrics"]:
                rows.append(
                    f"| {metric.get('date', '')} | {metric.get('job_count', '')} | "
                    f"{metric.get('avg_time_seconds', '')} | "
                    f"{metric.get('total_time_seconds', '')} |"
                )
            sections.append(
                f"""## Daily Metrics
| Date | Jobs | Avg Time | Total Time |
|------|------|----------|------------|
{chr(10).join(rows)}"""
            )

        markdown_content = f"""# ploTTY Performance Metrics ({days} days)

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
