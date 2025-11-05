"""
Integration tests for self-test.

This module contains tests for system integration commands
that validate overall system functionality.
"""

from __future__ import annotations

from .core import run_command
from .basic import create_test_result


def run_system_integration_tests(test_env) -> list:
    """Run system integration tests."""
    results = []

    print("\nSystem Integration Tests:")
    system_tests = [
        ("system export", "System export functionality"),
        ("check ready", "System readiness check"),
    ]

    for cmd, desc in system_tests:
        result = run_command(cmd, test_env)
        test_result = create_test_result(
            "System Integration", cmd, desc, result, "default"
        )
        results.append(test_result)
        status = "✅ PASS" if test_result["status"] == "PASS" else "❌ FAIL"
        print(f"Testing: {cmd}...", end=" ")
        print(status)

    return results
