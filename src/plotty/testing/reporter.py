"""
Test result reporter for ploTTY self-testing.

This module provides comprehensive test result reporting using existing
OutputManager system for consistent formatting across all output formats.
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from .models import TestResult, TestSummary, TestSuite, TestStatus
except ImportError:
    # Fallback definitions for testing
    from enum import Enum
    from dataclasses import dataclass
    from typing import Dict, List, Any, Optional

    class TestStatus(Enum):
        PASS = "PASS"
        FAIL = "FAIL"
        SKIP = "SKIP"

    @dataclass
    class TestResult:
        category: str
        command: str
        status: TestStatus
        duration: float
        message: str
        details: Optional[Dict[str, Any]] = None
        error: Optional[str] = None

    @dataclass
    class TestSummary:
        total_tests: int
        passed: int
        failed: int
        skipped: int
        duration: float
        environment: str
        categories: Dict[str, Any]

    @dataclass
    class TestSuite:
        name: str
        version: str
        environment: str
        summary: TestSummary


# Import OutputManager lazily to avoid circular imports
OutputManager = None
get_output_manager = None


def _get_output_manager():
    """Lazy import of OutputManager."""
    global OutputManager, get_output_manager
    if OutputManager is None:
        try:
            from ..cli.info.output import OutputManager as OM, get_output_manager as gom

            OutputManager = OM
            get_output_manager = gom
        except ImportError:
            # Fallback for testing
            OutputManager = None

            def get_output_manager():
                return None

    return get_output_manager()


class TestReporter:
    """Reporter for test results using OutputManager."""

    def __init__(self, output_manager: Optional[OutputManager] = None):
        """Initialize reporter with output manager."""
        self.output = output_manager or get_output_manager()
        self.results: List[TestResult] = []

    def add_result(self, result: TestResult) -> None:
        """Add a test result."""
        self.results.append(result)

    def generate_report(
        self, test_suite: TestSuite, json_output: bool = False, csv_output: bool = False
    ) -> None:
        """Generate comprehensive test report.

        Args:
            test_suite: Complete test suite with results
            json_output: Whether to output JSON format
            csv_output: Whether to output CSV format
        """
        # Build markdown content
        markdown_content = self._build_markdown_report(test_suite)

        # Build structured data for JSON/CSV
        json_data = test_suite.to_dict() if json_output else None
        csv_data = self._build_csv_data(test_suite) if csv_output else None

        # Use OutputManager for proper format handling
        self.output.print_markdown(
            content=markdown_content,
            json_data=json_data,
            tabular_csv_data=csv_data,
            json_output=json_output,
            csv_output=csv_output,
        )

    def _build_markdown_report(self, test_suite: TestSuite) -> str:
        """Build comprehensive markdown report."""
        summary = test_suite.summary

        # Build sections
        sections = {}

        # Summary section
        sections["Summary"] = self._build_summary_table(summary)

        # Test categories section
        sections["Test Categories"] = self._build_categories_table(summary.categories)

        # Detailed results section
        sections["Detailed Results"] = self._build_detailed_results_table()

        # Failed tests section (if any)
        failed_results = [r for r in self.results if r.status == TestStatus.FAIL]
        if failed_results:
            sections["Failed Tests"] = self._build_failed_tests_table(failed_results)

        # Environment info section
        sections["Environment"] = self._build_environment_info(test_suite)

        # Combine all sections
        return self.output.print_sectioned_markdown(
            title=f"ploTTY System Test Results - {test_suite.name}", sections=sections
        )

    def _build_summary_table(self, summary: TestSummary) -> str:
        """Build summary table."""
        rows = [
            ["Total Tests", str(summary.total_tests)],
            ["✅ Passed", str(summary.passed)],
            ["❌ Failed", str(summary.failed)],
            ["⏭️ Skipped", str(summary.skipped)],
            ["Success Rate", f"{summary.success_rate:.1f}%"],
            ["Duration", f"{summary.duration:.1f}s"],
            ["Environment", summary.environment],
        ]

        return self.output.print_table_markdown(
            title="Test Summary", headers=["Metric", "Value"], rows=rows
        )

    def _build_categories_table(self, categories: Dict[str, Any]) -> str:
        """Build test categories table."""
        rows = []
        for category_name, stats in categories.items():
            category_display = category_name.replace("_", " ").title()
            success_rate = stats.get("success_rate", 0)
            rows.append(
                [
                    category_display,
                    str(stats.get("passed", 0)),
                    str(stats.get("failed", 0)),
                    str(stats.get("skipped", 0)),
                    str(stats.get("total", 0)),
                    f"{success_rate:.1f}%",
                ]
            )

        return self.output.print_table_markdown(
            title="Test Categories",
            headers=[
                "Category",
                "Passed",
                "Failed",
                "Skipped",
                "Total",
                "Success Rate",
            ],
            rows=rows,
        )

    def _build_detailed_results_table(self) -> str:
        """Build detailed results table."""
        rows = []
        for result in self.results:
            status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}.get(
                result.status.value, "❓"
            )

            category_display = result.category.value.replace("_", " ").title()
            rows.append(
                [
                    category_display,
                    result.command,
                    f"{status_emoji} {result.status.value}",
                    f"{result.duration:.2f}s",
                    result.message,
                ]
            )

        return self.output.print_table_markdown(
            title="Detailed Results",
            headers=["Category", "Command", "Status", "Duration", "Message"],
            rows=rows,
        )

    def _build_failed_tests_table(self, failed_results: List[TestResult]) -> str:
        """Build failed tests details table."""
        rows = []
        for result in failed_results:
            category_display = result.category.value.replace("_", " ").title()
            error_msg = result.error or "No error details available"
            rows.append(
                [
                    category_display,
                    result.command,
                    result.message,
                    error_msg[:100] + "..." if len(error_msg) > 100 else error_msg,
                ]
            )

        return self.output.print_table_markdown(
            title="Failed Tests Details",
            headers=["Category", "Command", "Message", "Error"],
            rows=rows,
        )

    def _build_environment_info(self, test_suite: TestSuite) -> str:
        """Build environment information section."""
        env_path = Path(test_suite.environment)

        info_lines = [
            f"**Test Directory:** `{test_suite.environment}`",
            f"**Workspace:** `{env_path / 'workspace'}`",
            f"**Database:** `{env_path / 'workspace' / 'test_plotty.db'}`",
            f"**Configuration:** `{env_path / 'config' / 'test_config.yaml'}`",
            f"**Test Suite:** {test_suite.name} v{test_suite.version}",
            f"**Start Time:** {test_suite.start_time:.2f}",
        ]

        if test_suite.end_time:
            info_lines.append(f"**End Time:** {test_suite.end_time:.2f}")

        return "\n".join(info_lines)

    def _build_csv_data(self, test_suite: TestSuite) -> Dict[str, Any]:
        """Build CSV data for tabular output."""
        # Summary CSV data
        summary_rows = [
            ["Section", "Category", "Item", "Value"],
            ["Summary", "Tests", "Total", str(test_suite.summary.total_tests)],
            ["Summary", "Tests", "Passed", str(test_suite.summary.passed)],
            ["Summary", "Tests", "Failed", str(test_suite.summary.failed)],
            ["Summary", "Tests", "Skipped", str(test_suite.summary.skipped)],
            [
                "Summary",
                "Tests",
                "Success Rate",
                f"{test_suite.summary.success_rate:.1f}%",
            ],
            ["Summary", "Tests", "Duration", f"{test_suite.summary.duration:.1f}s"],
            ["Summary", "Environment", "Path", test_suite.environment],
        ]

        # Categories CSV data
        for category_name, stats in test_suite.summary.categories.items():
            category_display = category_name.replace("_", " ").title()
            summary_rows.extend(
                [
                    [
                        "Categories",
                        category_display,
                        "Passed",
                        str(stats.get("passed", 0)),
                    ],
                    [
                        "Categories",
                        category_display,
                        "Failed",
                        str(stats.get("failed", 0)),
                    ],
                    [
                        "Categories",
                        category_display,
                        "Skipped",
                        str(stats.get("skipped", 0)),
                    ],
                    [
                        "Categories",
                        category_display,
                        "Total",
                        str(stats.get("total", 0)),
                    ],
                    [
                        "Categories",
                        category_display,
                        "Success Rate",
                        f"{stats.get('success_rate', 0):.1f}%",
                    ],
                ]
            )

        # Detailed results CSV data
        for result in self.results:
            category_display = result.category.value.replace("_", " ").title()
            summary_rows.append(
                [
                    "Results",
                    category_display,
                    result.command,
                    f"{result.status.value}:{result.duration:.2f}s:{result.message}",
                ]
            )

        return {
            "headers": ["Section", "Category", "Item", "Value"],
            "rows": summary_rows[1:],  # Skip header row
        }

    def print_progress(self, current: int, total: int, message: str = "") -> None:
        """Print progress update (only for interactive output)."""
        if not self.output.is_redirected():
            progress = f"[{current}/{total}] {message}"
            # Simple progress output - could be enhanced with rich progress bar
            print(f"\r{progress}", end="", flush=True)

            if current == total:
                print()  # New line when complete


__all__ = ["TestReporter"]
