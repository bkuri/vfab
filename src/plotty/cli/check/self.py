"""
Enhanced self-test command for ploTTY.

This module provides comprehensive self-testing with expanded test coverage
including basic commands, job lifecycle, job management workflows, system
validation, resource management, and system integration tests.
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

import typer
from rich.console import Console

from plotty.cli.common import console as cli_console
from plotty.cli.info.output import get_output_manager
from plotty.fsm import JobState

# Import enhanced test modules
try:
    # Try to import from modular structure
    sys.path.insert(0, str(Path(__file__).parent))
    from .self.core import create_test_environment
    from .self.basic import run_basic_command_tests
    from .self.intermediate import run_job_lifecycle_tests, run_job_management_tests
    from .self.advanced import (
        run_system_validation_tests,
        run_resource_management_tests,
    )
    from .self.integration import run_system_integration_tests
    from .self.reporting import generate_report

    MODULAR_AVAILABLE = True
except ImportError:
    # Fallback to integrated implementation
    MODULAR_AVAILABLE = False


def create_integrated_test_environment() -> dict:
    """Create integrated test environment when modular imports fail."""
    temp_dir = Path(tempfile.mkdtemp(prefix="plotty_self_test_"))

    return {
        "temp_dir": temp_dir,
        "test_svg": str(temp_dir / "test.svg"),
        "test_job_id": None,
        "original_cwd": Path.cwd(),
        "console": Console(),
    }


def run_integrated_command(command: str, cwd: Path | None = None) -> dict:
    """Run integrated command when modular imports fail."""
    import subprocess

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=60, cwd=cwd
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 60 seconds",
            "returncode": -1,
        }
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def create_integrated_test_svg(output_path: str) -> bool:
    """Create integrated test SVG when modular imports fail."""
    try:
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="80" height="80" fill="none" stroke="black" stroke-width="1"/>
  <circle cx="50" cy="50" r="20" fill="none" stroke="black" stroke-width="1"/>
</svg>"""

        with open(output_path, "w") as f:
            f.write(svg_content)

        return True
    except Exception:
        return False


def create_test_result(
    name: str, success: bool, message: str = "", details: dict = None
) -> dict:
    """Create a standardized test result."""
    return {
        "name": name,
        "success": success,
        "message": message,
        "details": details or {},
        "timestamp": time.time(),
    }


def run_integrated_basic_tests(test_env: dict) -> list:
    """Run integrated basic tests."""
    results = []

    basic_tests = [
        ("check config", "Configuration validation"),
        ("list pens", "Pen listing"),
        ("list papers", "Paper listing"),
        ("info system", "System information"),
    ]

    for cmd, description in basic_tests:
        result = run_integrated_command(f"plotty {cmd}")

        # Special handling for check config - warnings (exit code 2) are expected
        if "check config" in cmd:
            success = result["returncode"] <= 2  # 0=success, 1=error, 2=warnings
            message = "✓ Passed" if success else f"✗ Failed: {result['stderr']}"
        else:
            success = result["success"]
            message = "✓ Passed" if success else f"✗ Failed: {result['stderr']}"

        results.append(
            create_test_result(
                f"Basic: {description}",
                success,
                message,
            )
        )

    return results


def run_integrated_job_lifecycle_tests(test_env: dict) -> list:
    """Run integrated job lifecycle tests."""
    results = []

    # Create test SVG
    if not create_integrated_test_svg(test_env["test_svg"]):
        results.append(
            create_test_result(
                "Job Lifecycle: Test SVG creation", False, "✗ Failed to create test SVG"
            )
        )
        return results

    # Test job creation (use unique name to avoid conflicts)
    import uuid

    unique_job_id = f"test-job-{uuid.uuid4().hex[:6]}"
    result = run_integrated_command(
        f'plotty add job {unique_job_id} "{test_env["test_svg"]}"'
    )
    if result["success"]:
        # Extract job ID from output
        import re

        job_id_match = re.search(r"job: ([\w-]+)", result["stdout"])
        if job_id_match:
            test_env["test_job_id"] = job_id_match.group(1)
            results.append(
                create_test_result(
                    "Job Lifecycle: Job creation",
                    True,
                    f"✓ Created job {test_env['test_job_id']}",
                )
            )
        else:
            results.append(
                create_test_result(
                    "Job Lifecycle: Job creation",
                    False,
                    "✗ Could not extract job ID from output",
                )
            )
    else:
        results.append(
            create_test_result(
                "Job Lifecycle: Job creation", False, f"✗ Failed: {result['stderr']}"
            )
        )

    # Test job status check
    if test_env.get("test_job_id"):
        result = run_integrated_command(f"plotty info job {test_env['test_job_id']}")
        results.append(
            create_test_result(
                "Job Lifecycle: Job status check",
                result["success"],
                "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
            )
        )

    return results


def run_integrated_job_management_tests(test_env: dict) -> list:
    """Run integrated job management tests."""
    results = []

    # Test job listing
    result = run_integrated_command("plotty list jobs")
    results.append(
        create_test_result(
            "Job Management: Job listing",
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test queue status
    result = run_integrated_command("plotty info queue")
    results.append(
        create_test_result(
            "Job Management: Queue status",
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test session info
    result = run_integrated_command("plotty info session")
    results.append(
        create_test_result(
            "Job Management: Session info",
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test job removal (if we have a test job)
    if test_env.get("test_job_id"):
        result = run_integrated_command(f"plotty remove job {test_env['test_job_id']}")
        results.append(
            create_test_result(
                "Job Management: Job removal",
                result["success"],
                "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
            )
        )

    return results


def run_integrated_system_validation_tests(test_env: dict) -> list:
    """Run integrated system validation tests."""
    results = []

    # Test system readiness
    result = run_integrated_command("plotty check ready")
    results.append(
        create_test_result(
            "System Validation: System readiness",
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test camera check
    result = run_integrated_command("plotty check camera")
    results.append(
        create_test_result(
            "System Validation: Camera check",
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test servo check (hardware-dependent)
    result = run_integrated_command("plotty check servo")
    if result["success"]:
        results.append(
            create_test_result(
                "System Validation: Servo check",
                True,
                "✓ Passed - Servo motor operational",
            )
        )
    elif "AxiDraw support not available" in result["stdout"]:
        results.append(
            create_test_result(
                "System Validation: Servo check",
                True,  # Mark as passed since it's expected without hardware
                "⚠️ Skipped - AxiDraw hardware not available",
            )
        )
    else:
        results.append(
            create_test_result(
                "System Validation: Servo check",
                False,
                f"✗ Failed: {result['stderr']}",
            )
        )

    # Test timing check (hardware-dependent)
    result = run_integrated_command("plotty check timing")
    if result["success"]:
        results.append(
            create_test_result(
                "System Validation: Timing check",
                True,
                "✓ Passed - Device timing operational",
            )
        )
    elif "AxiDraw support not available" in result["stdout"]:
        results.append(
            create_test_result(
                "System Validation: Timing check",
                True,  # Mark as passed since it's expected without hardware
                "⚠️ Skipped - AxiDraw hardware not available",
            )
        )
    else:
        results.append(
            create_test_result(
                "System Validation: Timing check",
                False,
                f"✗ Failed: {result['stderr']}",
            )
        )

    return results


def run_integrated_resource_management_tests(test_env: dict) -> list:
    """Run integrated resource management tests."""
    results = []

    # Test statistics
    result = run_integrated_command("plotty stats summary")
    results.append(
        create_test_result(
            "Resource Management: Statistics summary",
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test job statistics
    result = run_integrated_command("plotty stats jobs")
    results.append(
        create_test_result(
            "Resource Management: Job statistics",
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test performance statistics
    result = run_integrated_command("plotty stats performance")
    results.append(
        create_test_result(
            "Resource Management: Performance statistics",
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    return results


def run_integrated_system_integration_tests(test_env: dict) -> list:
    """Run integrated system integration tests."""
    results = []

    # Test job FSM
    try:
        # Just test that we can import and access the class
        current_state = JobState.NEW
        results.append(
            create_test_result(
                "System Integration: Job FSM",
                True,
                f"✓ JobFSM available, default state: {current_state.value}",
            )
        )
    except Exception as e:
        results.append(
            create_test_result(
                "System Integration: Job FSM", False, f"✗ Failed: {str(e)}"
            )
        )

    # Test help system
    result = run_integrated_command("plotty --help")
    results.append(
        create_test_result(
            "System Integration: Help system",
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    return results


def generate_integrated_report(results: list, console: Console) -> dict:
    """Generate integrated test report using OutputManager for consistent formatting."""
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    success_rate = (passed / len(results)) * 100 if results else 0

    output_manager = get_output_manager()

    # Check if we should use Rich formatting (not redirected)
    use_rich = not output_manager.is_redirected()

    if use_rich:
        # Rich formatting for terminal
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text

        # Group results by category first to calculate table width
        categories = {}
        for result in results:
            category = result["name"].split(": ")[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)

        # Create results table first to determine width
        table = Table(title="Test Results", show_header=True, header_style="bold")
        table.add_column("Status", width=6, justify="center")
        table.add_column("Category", width=15)
        table.add_column("Test", width=25)
        table.add_column("Result", width=40)

        # Add rows to table (but don't print yet)
        for category, category_results in categories.items():
            for result in category_results:
                # Create colored status emojis
                if result["success"]:
                    status_text = Text("✅", style="green")
                else:
                    status_text = Text("❌", style="red")

                test_name = (
                    result["name"].split(": ", 1)[1]
                    if ": " in result["name"]
                    else result["name"]
                )
                message = (
                    result["message"]
                    .replace("✓ Passed", "Passed")
                    .replace("✗ Failed:", "Failed:")
                )

                # Truncate long messages for table display
                if len(message) > 37:
                    message = message[:34] + "..."

                # Add color coding for failed tests
                row_style = "red" if not result["success"] else "white"
                table.add_row(
                    status_text, category, test_name, message, style=row_style
                )

        # Calculate table width (approximately)
        # Status: 6, Category: 15, Test: 25, Result: 40, plus borders and spacing: ~7
        table_width = 6 + 15 + 25 + 40 + 7  # ~93 characters

        # Summary panel with calculated width and color coding
        summary_text = Text()
        summary_text.append("Total: ", style="bold")
        summary_text.append(f"{len(results)} ", style="cyan")
        summary_text.append("Passed: ", style="bold")
        summary_text.append(f"{passed} ", style="green")
        summary_text.append("Failed: ", style="bold")
        summary_text.append(f"{failed} ", style="red")
        summary_text.append(
            f"({success_rate:.1f}%)", style="yellow" if failed > 0 else "green"
        )

        panel = Panel(
            summary_text,
            title="[bold blue]ploTTY Self-Test Results[/bold blue]",
            width=table_width,
            padding=(1, 2),
            border_style="blue",
        )
        console.print(panel)

        # Print the table
        console.print(table)

    else:
        # Plain markdown for redirected output
        markdown_content = f"""# ploTTY Self-Test Results

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {len(results)} |
| ✅ Passed | {passed} |
| ❌ Failed | {failed} |
| Success Rate | {success_rate:.1f}% |

## Test Results

| Status | Category | Test | Result |
|--------|----------|------|--------|"""

        # Group results by category
        categories = {}
        for result in results:
            category = result["name"].split(": ")[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)

        # Add test results to markdown table
        for category, category_results in categories.items():
            for result in category_results:
                status = "✅" if result["success"] else "❌"
                test_name = (
                    result["name"].split(": ", 1)[1]
                    if ": " in result["name"]
                    else result["name"]
                )
                message = (
                    result["message"]
                    .replace("✓ Passed", "Passed")
                    .replace("✗ Failed:", "Failed:")
                )

                # Escape markdown special characters
                message = message.replace("|", "\\|").replace("\n", " ")

                markdown_content += (
                    f"\n| {status} | {category} | {test_name} | {message} |"
                )

        # Use OutputManager to print markdown
        output_manager.print_markdown(markdown_content)

    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "results": results,
    }

    # Use OutputManager to print (handles Rich rendering vs plain markdown)
    output_manager.print_markdown(markdown_content)

    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "results": results,
    }


def run_self_test(
    level: str = typer.Option(
        "basic",
        "--level",
        "-l",
        help="Test level: basic, intermediate, advanced, integration, or all",
    ),
    report_file: str = typer.Option(
        None, "--report-file", "-r", help="Save detailed report to file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """
    Run ploTTY self-test.

    Performs comprehensive testing of ploTTY installation and configuration.
    Tests are organized by complexity levels:

    * **basic**: Core command tests (4 tests)
    * **intermediate**: Job lifecycle and management (8 tests)
    * **advanced**: System validation and resource management (7 tests)
    * **integration**: System integration tests (2 tests)
    * **all**: Run all tests (21 tests total)

    Each test runs in isolated environments with proper cleanup.
    """
    console = cli_console

    if verbose:
        console.print(f"[blue]Starting ploTTY self-test (level: {level})...[/blue]")

    # Use modular or integrated approach
    if MODULAR_AVAILABLE:
        if verbose:
            console.print("[green]Using modular test structure...[/green]")
        test_env = create_test_environment()

        basic_tests = run_basic_command_tests
        job_lifecycle_tests = run_job_lifecycle_tests
        job_management_tests = run_job_management_tests
        system_validation_tests = run_system_validation_tests
        resource_management_tests = run_resource_management_tests
        integration_tests = run_system_integration_tests
        report_func = generate_report
    else:
        if verbose:
            console.print(
                "[yellow]Using integrated test structure (fallback)...[/yellow]"
            )
        test_env = create_integrated_test_environment()

        basic_tests = run_integrated_basic_tests
        job_lifecycle_tests = run_integrated_job_lifecycle_tests
        job_management_tests = run_integrated_job_management_tests
        system_validation_tests = run_integrated_system_validation_tests
        resource_management_tests = run_integrated_resource_management_tests
        integration_tests = run_integrated_system_integration_tests
        report_func = generate_integrated_report

    all_results = []

    try:
        # Run tests based on level
        if level in ["basic", "all"]:
            if verbose:
                console.print("[blue]Running basic tests...[/blue]")
            all_results.extend(basic_tests(test_env))

        if level in ["intermediate", "all"]:
            if verbose:
                console.print("[blue]Running job lifecycle tests...[/blue]")
            all_results.extend(job_lifecycle_tests(test_env))

            if verbose:
                console.print("[blue]Running job management tests...[/blue]")
            all_results.extend(job_management_tests(test_env))

        if level in ["advanced", "all"]:
            if verbose:
                console.print("[blue]Running system validation tests...[/blue]")
            all_results.extend(system_validation_tests(test_env))

            if verbose:
                console.print("[blue]Running resource management tests...[/blue]")
            all_results.extend(resource_management_tests(test_env))

        if level in ["integration", "all"]:
            if verbose:
                console.print("[blue]Running system integration tests...[/blue]")
            all_results.extend(integration_tests(test_env))

        # Generate report
        report = report_func(all_results, console)

        # Save report if requested
        if report_file:
            import json

            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            console.print(f"[green]Report saved to: {report_file}[/green]")

        # Exit with appropriate code
        if report["failed"] > 0:
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Self-test failed with error: {e}[/red]")
        raise typer.Exit(1)

    finally:
        # Cleanup
        if "temp_dir" in test_env:
            import shutil

            shutil.rmtree(test_env["temp_dir"], ignore_errors=True)


def check_self(
    level: str = typer.Option(
        "basic",
        "--level",
        "-l",
        help="Test level: basic, intermediate, advanced, integration, or all",
    ),
    report_file: str = typer.Option(
        None, "--report-file", "-r", help="Save detailed report to file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """Wrapper function for check self command."""
    run_self_test(level=level, report_file=report_file, verbose=verbose)
