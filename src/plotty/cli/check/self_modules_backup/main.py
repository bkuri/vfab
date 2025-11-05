"""
Self-test command for ploTTY CLI.

This module provides comprehensive self-testing capabilities with isolated
environments and detailed reporting, organized by test complexity levels.
"""

from __future__ import annotations

import time
import sys
from pathlib import Path
from typing import List, Dict, Any

import typer
from importlib import metadata

from ...codes import ExitCode
from ...utils import error_handler

# Import modular test components
from .core import create_test_environment, cleanup_test_environment
from .basic import run_basic_command_tests
from .intermediate import run_job_lifecycle_tests, run_job_management_tests
from .advanced import run_system_validation_tests, run_resource_management_tests
from .integration import run_system_integration_tests
from .reporting import generate_report


def run_tests(test_env: Path) -> List[Dict[str, Any]]:
    """Run all test categories."""
    results = []

    # Basic command tests
    results.extend(run_basic_command_tests(test_env))

    # Job lifecycle tests
    lifecycle_results, test_svg = run_job_lifecycle_tests(test_env)
    results.extend(lifecycle_results)

    # Job management workflow tests
    results.extend(run_job_management_tests(test_env, test_svg))

    # Enhanced system validation tests
    results.extend(run_system_validation_tests(test_env))

    # Resource management tests
    results.extend(run_resource_management_tests(test_env))

    # System integration tests
    results.extend(run_system_integration_tests(test_env))

    return results


def check_self(
    keep_files: bool = typer.Option(
        False, "--keep-files", help="Keep test artifacts for debugging"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output results in JSON format"
    ),
    csv_output: bool = typer.Option(
        False, "--csv", help="Output results in CSV format"
    ),
) -> None:
    """Run comprehensive ploTTY self-tests in isolated environment.

    This command creates a temporary workspace and database to test all
    ploTTY functionality without affecting your production data.

    Examples:
        plotty check self                    # Basic dry-run tests
        plotty check self --keep-files        # Keep test artifacts
        plotty check self --json              # JSON output
    """
    try:
        # Get version
        try:
            version = metadata.version("plotty")
        except metadata.PackageNotFoundError:
            version = "unknown"

        # Create test environment
        test_env = create_test_environment()

        try:
            if not sys.stdout.isatty():
                print(f"# Running ploTTY v{version} self-tests")
                print(f"# Test environment: {test_env}")
            else:
                print(f"🧪 Running ploTTY v{version} self-tests...")
                print(f"📁 Test environment: {test_env}")
            print()

            # Run tests
            start_time = time.time()
            results = run_tests(test_env)
            duration = time.time() - start_time

            # Generate report
            generate_report(results, test_env, duration, json_output, csv_output)

            # Exit with appropriate code
            failed = sum(1 for r in results if r["status"] == "FAIL")
            if failed > 0:
                print(f"\n❌ {failed} test(s) failed")
                raise typer.Exit(ExitCode.ERROR)
            else:
                print(f"\n✅ All {len(results)} tests passed!")
                raise typer.Exit(ExitCode.SUCCESS)

        finally:
            # Cleanup
            if not keep_files:
                cleanup_test_environment(test_env)
                print(f"🧹 Cleaned up test environment: {test_env}")
            else:
                print(f"📁 Test environment preserved: {test_env}")

    except typer.Exit:
        raise
    except Exception as e:
        error_handler.handle(e)
        raise typer.Exit(ExitCode.ERROR)


__all__ = ["check_self"]
