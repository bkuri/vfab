"""
Intermediate tests for self-test.

This module contains tests for job lifecycle and job management
commands that form the core workflow.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .core import run_command, create_test_svg
from .basic import create_test_result


def run_job_lifecycle_tests(test_env: Path) -> Tuple[List[dict], Path]:
    """Run job lifecycle tests."""
    results = []

    print("\nJob Lifecycle Tests:")

    # Add test pen
    result = run_command("add pen TestPen 0.5 25 50 1", test_env)
    test_result = create_test_result(
        "Job Lifecycle",
        "add pen TestPen 0.5 25 50 1",
        "Add test pen configuration",
        result,
        "duplicate_detection",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"add pen TestPen... {status}")

    # Add test paper
    result = run_command("add paper TestPaper 210 297", test_env)
    test_result = create_test_result(
        "Job Lifecycle",
        "add paper TestPaper 210 297",
        "Add test paper configuration",
        result,
        "duplicate_detection",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"add paper TestPaper... {status}")

    # Create test SVG and add job
    test_svg = create_test_svg(test_env)
    result = run_command(f"add job TestJob {test_svg}", test_env)
    test_result = create_test_result(
        "Job Lifecycle",
        f"add job TestJob {test_svg.name}",
        "Add test job",
        result,
        "default",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"add job TestJob... {status}")

    # List jobs
    result = run_command("list jobs", test_env)
    test_result = create_test_result(
        "Job Lifecycle", "list jobs", "List all jobs", result, "default"
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"list jobs... {status}")

    return results, test_svg


def run_job_management_tests(test_env: Path, test_svg: Path) -> List[dict]:
    """Run job management workflow tests."""
    results = []

    print("\nJob Management Workflow Tests:")

    # Test optimize command
    result = run_command(f"optimize {test_svg.name}", test_env)
    test_result = create_test_result(
        "Job Management",
        f"optimize {test_svg.name}",
        "Test job optimization preview",
        result,
        "default",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"optimize job... {status}")

    # Test queue command
    result = run_command("queue TestJob", test_env)
    test_result = create_test_result(
        "Job Management",
        "queue TestJob",
        "Test manual job queuing",
        result,
        "state_validation",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"queue job... {status}")

    # Test restart command
    result = run_command("restart TestJob", test_env)
    test_result = create_test_result(
        "Job Management",
        "restart TestJob",
        "Test job restart functionality",
        result,
        "default",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"restart job... {status}")

    # Test resume command
    result = run_command("resume TestJob", test_env)
    test_result = create_test_result(
        "Job Management",
        "resume TestJob",
        "Test job resume functionality",
        result,
        "default",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"resume job... {status}")

    return results
