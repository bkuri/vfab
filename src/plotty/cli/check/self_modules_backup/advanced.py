"""
Advanced tests for self-test.

This module contains tests for system validation and resource management
commands that require more complex validation logic.
"""

from __future__ import annotations

from .core import run_command
from .basic import create_test_result


def run_system_validation_tests(test_env) -> list:
    """Run enhanced system validation tests."""
    results = []

    print("\nEnhanced System Validation Tests:")

    # Test check job command
    result = run_command("check job TestJob", test_env)
    test_result = create_test_result(
        "System Validation",
        "check job TestJob",
        "Test job status checking",
        result,
        "known_issue",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"check job... {status}")

    # Test info job command
    result = run_command("info job TestJob", test_env)
    test_result = create_test_result(
        "System Validation",
        "info job TestJob",
        "Test job information display",
        result,
        "default",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"info job... {status}")

    # Test info tldr command
    result = run_command("info tldr", test_env)
    test_result = create_test_result(
        "System Validation",
        "info tldr",
        "Test quick status overview",
        result,
        "default",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"info tldr... {status}")

    # Test list presets command
    result = run_command("list presets", test_env)
    test_result = create_test_result(
        "System Validation", "list presets", "Test preset listing", result, "default"
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"list presets... {status}")

    return results


def run_resource_management_tests(test_env) -> list:
    """Run resource management tests."""
    results = []

    print("\nResource Management Tests:")

    # Test remove job command
    result = run_command("remove job TestJob", test_env)
    test_result = create_test_result(
        "Resource Management",
        "remove job TestJob",
        "Test job removal with cleanup",
        result,
        "default",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"remove job... {status}")

    # Test remove pen command
    result = run_command("remove pen TestPen", test_env)
    test_result = create_test_result(
        "Resource Management",
        "remove pen TestPen",
        "Test pen removal with cleanup",
        result,
        "dependency_validation",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"remove pen... {status}")

    # Test remove paper command
    result = run_command("remove paper TestPaper", test_env)
    test_result = create_test_result(
        "Resource Management",
        "remove paper TestPaper",
        "Test paper removal with cleanup",
        result,
        "dependency_validation",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"remove paper... {status}")

    return results
