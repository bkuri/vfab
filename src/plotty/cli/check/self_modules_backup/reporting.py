"""
Test reporting utilities for self-tests.

This module provides utilities for generating test reports in various formats.
"""

from __future__ import annotations

import sys
import json
import csv
import io
from pathlib import Path
from typing import List, Dict, Any


def generate_report(
    results: List[Dict[str, Any]],
    test_env: Path,
    duration: float,
    json_output: bool = False,
    csv_output: bool = False,
) -> None:
    """Generate test report in markdown format."""
    total_tests = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = total_tests - passed

    # Handle JSON output
    if json_output:
        json_data = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "duration": duration,
                "environment": str(test_env),
            },
            "results": results,
        }
        print(json.dumps(json_data, indent=2))
        return

    # Handle CSV output
    if csv_output:
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Category", "Command", "Status", "Message", "Duration"])

        # Write results
        for result in results:
            writer.writerow(
                [
                    result["category"],
                    result["command"],
                    result["status"],
                    result["message"],
                    result.get("details", {}).get("duration", 0),
                ]
            )

        print(output.getvalue().strip())
        return

    # Check if output is redirected
    is_redirected = not sys.stdout.isatty()

    if is_redirected:
        _generate_markdown_report(
            results, test_env, duration, total_tests, passed, failed
        )
    else:
        _generate_rich_report(results, test_env, duration, total_tests, passed, failed)


def _generate_markdown_report(
    results: List[Dict[str, Any]],
    test_env: Path,
    duration: float,
    total_tests: int,
    passed: int,
    failed: int,
) -> None:
    """Generate markdown report for redirected output."""
    print("# ploTTY Self-Test Results")
    print()
    print("## Summary")
    print()
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| Total Tests | {total_tests} |")
    print(f"| ✅ Passed | {passed} |")
    print(f"| ❌ Failed | {failed} |")
    print(f"| Duration | {duration:.1f}s |")
    print(f"| Environment | {test_env} |")
    print()

    # Categories
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "failed": 0}
        if result["status"] == "PASS":
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1

    print("## Test Categories")
    print()
    print("| Category | Passed | Failed | Total | Success Rate |")
    print("|----------|--------|--------|-------|-------------|")
    for cat, stats in categories.items():
        total = stats["passed"] + stats["failed"]
        success_rate = (stats["passed"] / total * 100) if total > 0 else 0
        print(
            f"| {cat} | {stats['passed']} | {stats['failed']} | {total} | {success_rate:.1f}% |"
        )
    print()

    # Detailed results
    print("## Detailed Results")
    print()
    print("| Category | Command | Status | Message |")
    print("|----------|---------|--------|---------|")
    for result in results:
        status_emoji = "✅" if result["status"] == "PASS" else "❌"
        message = (
            result["message"][:80] + "..."
            if len(result["message"]) > 80
            else result["message"]
        )
        print(
            f"| {result['category']} | {result['command']} | {status_emoji} {result['status']} | {message} |"
        )


def _generate_rich_report(
    results: List[Dict[str, Any]],
    test_env: Path,
    duration: float,
    total_tests: int,
    passed: int,
    failed: int,
) -> None:
    """Generate rich report for interactive output."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        # Summary panel
        summary_text = f"""
Total Tests: {total_tests}
✅ Passed: {passed}
❌ Failed: {failed}
Duration: {duration:.1f}s
Environment: {test_env}
        """.strip()

        console.print(
            Panel(summary_text, title="🧪 ploTTY Self-Test Results", expand=False)
        )

        # Results table
        table = Table(title="Test Results")
        table.add_column("Category", style="cyan")
        table.add_column("Command", style="white")
        table.add_column("Status", style="green")
        table.add_column("Message", style="yellow")

        for result in results:
            status = "✅ PASS" if result["status"] == "PASS" else "❌ FAIL"
            message = (
                result["message"][:60] + "..."
                if len(result["message"]) > 60
                else result["message"]
            )
            table.add_row(result["category"], result["command"], status, message)

        console.print(table)

    except ImportError:
        # Fallback to plain text
        print("\n🧪 ploTTY Self-Test Results")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Duration: {duration:.1f}s")
        print(f"Environment: {test_env}")
        print()
        for result in results:
            status = "✅ PASS" if result["status"] == "PASS" else "❌ FAIL"
            print(f"{result['category']}: {result['command']} - {status}")
