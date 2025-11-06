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

    # Test list jobs --failed flag (recovery integration)
    result = run_command("list jobs --failed", test_env)
    test_result = create_test_result(
        "System Validation",
        "list jobs --failed",
        "Test failed and resumable jobs listing",
        result,
        "default",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"list jobs --failed... {status}")

    # Test list jobs --resumable flag
    result = run_command("list jobs --resumable", test_env)
    test_result = create_test_result(
        "System Validation",
        "list jobs --resumable",
        "Test resumable jobs listing",
        result,
        "default",
    )
    results.append(test_result)
    status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
    print(f"list jobs --resumable... {status}")

    # Test check job with recovery info integration
    # First create a test job to check
    result = run_command("add job RecoveryTestJob", test_env)
    if result["success"]:
        # Now check the job - should show recovery info if applicable
        result = run_command("check job RecoveryTestJob", test_env)
        test_result = create_test_result(
            "System Validation",
            "check job RecoveryTestJob",
            "Test job checking with recovery info integration",
            result,
            "default",
        )
        results.append(test_result)
        status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
        print(f"check job recovery integration... {status}")

        # Clean up test job
        run_command("remove job RecoveryTestJob", test_env)
    else:
        # If job creation failed, still record the test
        test_result = create_test_result(
            "System Validation",
            "check job RecoveryTestJob",
            "Test job checking with recovery info integration (job creation failed)",
            result,
            "default",
        )
        results.append(test_result)
        status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
        print(f"check job recovery integration... {status}")

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
