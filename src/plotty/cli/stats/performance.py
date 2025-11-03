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

        # Build hierarchical CSV data for performance metrics
        hierarchical_csv_data = []

        # Add main performance metrics
        hierarchical_csv_data.extend(
            [
                {
                    "section": "Performance",
                    "category": "Time",
                    "item": "Total Plotting Time",
                    "value": f"{performance_stats.get('total_plotting_time', 0.0):.1f}s",
                },
                {
                    "section": "Performance",
                    "category": "Time",
                    "item": "Average Job Time",
                    "value": f"{performance_stats.get('average_job_time', 0.0):.1f}s",
                },
                {
                    "section": "Performance",
                    "category": "Jobs",
                    "item": "Completed Jobs",
                    "value": str(performance_stats.get("completed_jobs", 0)),
                },
            ]
        )

        # Add job age information if available
        if performance_stats.get("oldest_job"):
            hierarchical_csv_data.append(
                {
                    "section": "Performance",
                    "category": "Age",
                    "item": "Oldest Job",
                    "value": performance_stats["oldest_job"].strftime("%Y-%m-%d %H:%M"),
                }
            )

        if performance_stats.get("newest_job"):
            hierarchical_csv_data.append(
                {
                    "section": "Performance",
                    "category": "Age",
                    "item": "Newest Job",
                    "value": performance_stats["newest_job"].strftime("%Y-%m-%d %H:%M"),
                }
            )

        # Build tabular CSV data for recent metrics
        tabular_csv_data = None

        if (
            "recent_metrics" in performance_stats
            and performance_stats["recent_metrics"]
        ):
            headers = ["Type", "Value", "Unit", "Timestamp"]
            rows = []

            for metric in performance_stats["recent_metrics"]:
                rows.append(
                    {
                        "Type": metric.get("type", ""),
                        "Value": str(metric.get("value", "")),
                        "Unit": metric.get("unit", ""),
                        "Timestamp": (
                            metric.get("timestamp", "").strftime("%Y-%m-%d %H:%M:%S")
                            if metric.get("timestamp")
                            else ""
                        ),
                    }
                )

            tabular_csv_data = {
                "headers": headers,
                "rows": rows,
            }

        # Build markdown content
        sections = []

        # Performance summary section
        perf_rows = [
            f"| Total Plotting Time | {performance_stats.get('total_plotting_time', 0.0):.1f}s |",
            f"| Average Job Time | {performance_stats.get('average_job_time', 0.0):.1f}s |",
            f"| Completed Jobs | {performance_stats.get('completed_jobs', 0)} |",
        ]

        if performance_stats.get("oldest_job"):
            perf_rows.append(
                f"| Oldest Job | {performance_stats['oldest_job'].strftime('%Y-%m-%d %H:%M')} |"
            )

        if performance_stats.get("newest_job"):
            perf_rows.append(
                f"| Newest Job | {performance_stats['newest_job'].strftime('%Y-%m-%d %H:%M')} |"
            )

        sections.append(
            f"""## Performance Summary
| Metric | Value |
|--------|-------|
{chr(10).join(perf_rows)}"""
        )

        # Recent metrics section
        if (
            "recent_metrics" in performance_stats
            and performance_stats["recent_metrics"]
        ):
            metric_rows = []
            for metric in performance_stats["recent_metrics"]:
                timestamp = (
                    metric.get("timestamp", "").strftime("%Y-%m-%d %H:%M:%S")
                    if metric.get("timestamp")
                    else ""
                )
                metric_rows.append(
                    f"| {metric.get('type', '')} | {metric.get('value', '')} | "
                    f"{metric.get('unit', '')} | {timestamp} |"
                )
            sections.append(
                f"""## Recent Metrics
| Type | Value | Unit | Timestamp |
|------|-------|------|-----------|
{chr(10).join(metric_rows)}"""
            )

        markdown_content = f"""# ploTTY Performance Metrics ({days} days)

{chr(10).join(sections)}"""

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
