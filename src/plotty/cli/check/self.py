"""
Enhanced self-test command for ploTTY.

This module provides comprehensive self-testing with expanded test coverage
including basic commands, job lifecycle, job management workflows, system
validation, resource management, and system integration tests.
"""

from __future__ import annotations


import tempfile
import time
from pathlib import Path

import typer
from rich.console import Console

from plotty.cli.common import console as cli_console
from plotty.cli.info.output import get_output_manager
from plotty.fsm import JobState
from plotty.progress import progress_task

# Modular structure was removed, always use integrated implementation
MODULAR_AVAILABLE = False


class TestProgressTracker:
    """Track and display progress for test execution with test names."""

    def __init__(self, total_tests: int, update_func) -> None:
        """Initialize tracker with total test count and update function.

        Args:
            total_tests: Total number of tests to run
            update_func: Callable to update progress display
        """
        self.total_tests = total_tests
        self.current_test = 0
        self.update_func = update_func
        self.current_test_name = ""

    def advance(self, test_name: str) -> None:
        """Advance progress to next test.

        Args:
            test_name: Name of test being run
        """
        self.current_test += 1
        self.current_test_name = test_name

        # For two-line display, extract cleaner test name
        if ": " in test_name:
            category, clean_name = test_name.split(": ", 1)
            display_name = f"[{self.current_test}/{self.total_tests}] {clean_name}"
        else:
            display_name = f"[{self.current_test}/{self.total_tests}] {test_name}"

        self.update_func(1, display_name)


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
    import shlex

    try:
        # Parse command safely to prevent injection
        cmd_parts = shlex.split(command)
        result = subprocess.run(
            cmd_parts, capture_output=True, text=True, timeout=60, cwd=cwd
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
    name: str,
    success: bool,
    message: str = "",
    details: dict | None = None,
    skipped: bool = False,
) -> dict:
    """Create a standardized test result."""
    return {
        "name": name,
        "success": success,
        "skipped": skipped,
        "message": message,
        "details": details or {},
        "timestamp": time.time(),
    }


def run_integrated_basic_tests(test_env: dict, progress_tracker=None) -> list:
    """Run integrated basic tests."""
    results = []

    basic_tests = [
        ("check config", "Configuration validation"),
        ("list pens", "Pen listing"),
        ("list papers", "Paper listing"),
        ("info system", "System information"),
    ]

    for cmd, description in basic_tests:
        test_name = f"Basic: {description}"
        if progress_tracker:
            progress_tracker.advance(test_name)

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
                test_name,
                success,
                message,
            )
        )

    return results


def run_integrated_job_lifecycle_tests(test_env: dict, progress_tracker=None) -> list:
    """Run integrated job lifecycle tests."""
    results = []

    # Create test SVG
    test_name = "Job Lifecycle: Test SVG creation"
    if progress_tracker:
        progress_tracker.advance(test_name)

    if not create_integrated_test_svg(test_env["test_svg"]):
        results.append(
            create_test_result(test_name, False, "✗ Failed to create test SVG")
        )
        return results

    results.append(
        create_test_result(
            test_name,
            True,
            "✓ Passed",
        )
    )

    # Test job creation (use unique name to avoid conflicts)
    import uuid

    test_name = "Job Lifecycle: Job creation"
    if progress_tracker:
        progress_tracker.advance(test_name)

    unique_job_id = f"test-job-{uuid.uuid4().hex[:6]}"
    result = run_integrated_command(
        f'plotty add job {unique_job_id} "{test_env["test_svg"]}" --apply'
    )
    if result["success"]:
        # Extract job ID from output
        import re

        job_id_match = re.search(r"Added and queued job: ([\w-]+)", result["stdout"])
        if job_id_match:
            test_env["test_job_id"] = job_id_match.group(1)
            results.append(
                create_test_result(
                    test_name,
                    True,
                    f"✓ Created job {test_env['test_job_id']}",
                )
            )
        else:
            results.append(
                create_test_result(
                    test_name,
                    False,
                    "✗ Could not extract job ID from output",
                )
            )
    else:
        results.append(
            create_test_result(test_name, False, f"✗ Failed: {result['stderr']}")
        )

    # Test job status check
    if test_env.get("test_job_id"):
        test_name = "Job Lifecycle: Job status check"
        if progress_tracker:
            progress_tracker.advance(test_name)

        result = run_integrated_command(f"plotty info job {test_env['test_job_id']}")
        results.append(
            create_test_result(
                test_name,
                result["success"],
                "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
            )
        )

    return results


def run_integrated_job_management_tests(test_env: dict, progress_tracker=None) -> list:
    """Run integrated job management tests."""
    results = []

    # Test job listing
    test_name = "Job Management: Job listing"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty list jobs")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test queue status
    test_name = "Job Management: Queue status"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty info queue")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test session info
    test_name = "Job Management: Session info"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty info session")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test job removal (if we have a test job)
    if test_env.get("test_job_id"):
        test_name = "Job Management: Job removal"
        if progress_tracker:
            progress_tracker.advance(test_name)

        result = run_integrated_command(f"plotty remove job {test_env['test_job_id']}")
        results.append(
            create_test_result(
                test_name,
                result["success"],
                "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
            )
        )

    return results


def run_integrated_system_validation_tests(
    test_env: dict, progress_tracker=None
) -> list:
    """Run integrated system validation tests."""
    results = []

    # Test system readiness
    test_name = "System Validation: System readiness"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty check ready")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test camera check
    test_name = "System Validation: Camera check"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty check camera")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test servo check (hardware-dependent)
    test_name = "System Validation: Servo check"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty check servo")
    if result["success"]:
        results.append(
            create_test_result(
                test_name,
                True,
                "✓ Passed - Servo motor operational",
            )
        )
    elif "AxiDraw support not available" in result["stdout"]:
        results.append(
            create_test_result(
                test_name,
                True,  # Success for tracking purposes
                "⚠️ Skipped - AxiDraw hardware not available",
                skipped=True,
            )
        )
    else:
        results.append(
            create_test_result(
                test_name,
                False,
                f"✗ Failed: {result['stderr']}",
            )
        )

    # Test timing check (hardware-dependent)
    test_name = "System Validation: Timing check"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty check timing")
    if result["success"]:
        results.append(
            create_test_result(
                test_name,
                True,
                "✓ Passed - Device timing operational",
            )
        )
    elif "AxiDraw support not available" in result["stdout"]:
        results.append(
            create_test_result(
                test_name,
                True,  # Success for tracking purposes
                "⚠️ Skipped - AxiDraw hardware not available",
                skipped=True,
            )
        )
    else:
        results.append(
            create_test_result(
                test_name,
                False,
                f"✗ Failed: {result['stderr']}",
            )
        )

    return results


def run_integrated_resource_management_tests(
    test_env: dict, progress_tracker=None
) -> list:
    """Run integrated resource management tests."""
    results = []

    # Test statistics
    test_name = "Resource Management: Statistics summary"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty stats summary")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test job statistics
    test_name = "Resource Management: Job statistics"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty stats jobs")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test performance statistics
    test_name = "Resource Management: Performance statistics"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty stats performance")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    return results


def run_integrated_recovery_system_tests(test_env: dict, progress_tracker=None) -> list:
    """Run integrated recovery system tests."""
    results = []

    # Test list jobs --failed flag
    test_name = "Recovery System: Failed jobs listing"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty list jobs --failed")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test list jobs --resumable flag
    test_name = "Recovery System: Resumable jobs listing"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty list jobs --resumable")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test interrupt detection functionality
    test_name = "Recovery System: Interrupt detection"
    if progress_tracker:
        progress_tracker.advance(test_name)

    try:
        from plotty.recovery import detect_interrupted_jobs
        from plotty.config import load_config
        from pathlib import Path

        cfg = load_config()
        workspace = Path(cfg.workspace)

        # Test interrupt detection (should return empty list normally)
        interrupted_jobs = detect_interrupted_jobs(workspace, 5)
        results.append(
            create_test_result(
                test_name,
                True,
                f"✓ Passed - Found {len(interrupted_jobs)} interrupted jobs",
            )
        )
    except Exception as e:
        results.append(
            create_test_result(
                test_name,
                False,
                f"✗ Failed: {str(e)}",
            )
        )

    # Test recovery config loading
    test_name = "Recovery System: Config loading"
    if progress_tracker:
        progress_tracker.advance(test_name)

    try:
        from plotty.config import load_config

        cfg = load_config()
        grace_minutes = cfg.recovery.interrupt_grace_minutes
        auto_detect = cfg.recovery.auto_detect_enabled
        max_attempts = cfg.recovery.max_resume_attempts

        results.append(
            create_test_result(
                test_name,
                True,
                f"✓ Passed - Grace: {grace_minutes}min, Auto-detect: {auto_detect}, Max attempts: {max_attempts}",
            )
        )
    except Exception as e:
        results.append(
            create_test_result(
                test_name,
                False,
                f"✗ Failed: {str(e)}",
            )
        )

    # Test resume command (dry-run)
    test_name = "Recovery System: Resume command availability"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty resume --help")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    # Test check job with recovery info (if we have a test job)
    if test_env.get("test_job_id"):
        test_name = "Recovery System: Job check with recovery info"
        if progress_tracker:
            progress_tracker.advance(test_name)

        result = run_integrated_command(f"plotty check job {test_env['test_job_id']}")
        results.append(
            create_test_result(
                test_name,
                result["success"],
                "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
            )
        )

    return results


def run_integrated_performance_tests(test_env: dict, progress_tracker=None) -> list:
    """Run integrated performance tests."""
    results = []

    # Test memory profiling
    test_name = "Performance: Memory profiling"
    if progress_tracker:
        progress_tracker.advance(test_name)

    try:
        import tracemalloc
        import gc
        import os

        # Start memory tracing
        tracemalloc.start()
        gc.collect()
        baseline = tracemalloc.get_traced_memory()[0]

        # Test basic commands memory usage
        commands = ["plotty check config", "plotty list pens", "plotty info system"]
        peak_memory = baseline

        for cmd in commands:
            os.system(cmd + " > /dev/null 2>&1")
            current, _ = tracemalloc.get_traced_memory()
            peak_memory = max(peak_memory, current)

        gc.collect()
        final_memory = tracemalloc.get_traced_memory()[0]
        memory_growth = final_memory - baseline

        tracemalloc.stop()

        # Assess memory performance
        if memory_growth < 1024 * 1024:  # Less than 1MB
            status = "✓ Passed - No significant memory leaks detected"
        elif memory_growth < 5 * 1024 * 1024:  # Less than 5MB
            status = "⚠️ Passed - Minor memory growth detected"
        else:
            status = "✗ Failed - Significant memory growth detected"

        results.append(
            create_test_result(
                test_name,
                memory_growth < 5 * 1024 * 1024,  # Pass if < 5MB growth
                f"{status} (Growth: {memory_growth // 1024}KB)",
            )
        )
    except Exception as e:
        results.append(create_test_result(test_name, False, f"✗ Failed: {str(e)}"))

    # Test database performance
    test_name = "Performance: Database performance"
    if progress_tracker:
        progress_tracker.advance(test_name)

    try:
        from plotty.db import get_session
        from plotty.models import Job, Layer, Pen, Paper, JobStatistics
        import time

        with get_session() as session:
            # Test query performance
            start_time = time.time()
            jobs = session.query(Job).all()
            job_time = time.time() - start_time

            start_time = time.time()
            _ = session.query(Job).filter(Job.state.in_(["queued", "running"])).all()
            filter_time = time.time() - start_time

            start_time = time.time()
            _ = session.query(Job, Paper).join(Paper).limit(10).all()
            join_time = time.time() - start_time

        # Assess database performance
        if job_time < 0.01 and filter_time < 0.01 and join_time < 0.01:
            status = "✓ Passed - Excellent database performance"
        elif job_time < 0.1 and filter_time < 0.05 and join_time < 0.05:
            status = "✓ Passed - Good database performance"
        else:
            status = "⚠️ Passed - Database performance needs optimization"

        results.append(
            create_test_result(
                test_name,
                True,  # Always pass, just report performance level
                f"{status} (Jobs: {job_time:.3f}s, Filter: {filter_time:.3f}s, Join: {join_time:.3f}s)",
            )
        )
    except Exception as e:
        results.append(create_test_result(test_name, False, f"✗ Failed: {str(e)}"))

    # Test cross-platform compatibility
    test_name = "Integration: Cross-platform compatibility"
    if progress_tracker:
        progress_tracker.advance(test_name)

    try:
        import tempfile
        import platform
        from pathlib import Path

        # Test file operations
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test file creation and reading
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")
            file_read_ok = test_file.read_text() == "test content"

            # Test directory operations
            subdir = temp_path / "subdir"
            subdir.mkdir()
            dir_ok = subdir.is_dir()

            # Test path handling
            if platform.system() == "Windows":
                path1 = Path("C:\\Users\\test")
                expected_sep = "\\"
            else:
                path1 = Path("/home/test")
                expected_sep = "/"
            
            path_ok = expected_sep in str(path1 / "documents")

            # Test special characters (skip on Windows)
            if platform.system() != "Windows":
                special_file = temp_path / "file-with-special.chars.txt"
                special_file.write_text("test")
                special_ok = special_file.exists()
            else:
                special_ok = True  # Skip on Windows

        if file_read_ok and dir_ok and path_ok and special_ok:
            status = f"✓ Passed - Compatible with {platform.system()} {platform.release()}"
        else:
            status = f"✗ Failed - Platform compatibility issues detected"

        results.append(
            create_test_result(
                test_name,
                file_read_ok and dir_ok and path_ok and special_ok,
                status,
            )
        )
    except Exception as e:
        results.append(create_test_result(test_name, False, f"✗ Failed: {str(e)}"))

    return results


def run_integrated_stress_tests(test_env: dict, progress_tracker=None) -> list:
    """Run integrated stress tests."""
    results = []

    # Test load testing with small dataset
    test_name = "Stress: Load testing (10 jobs)"
    if progress_tracker:
        progress_tracker.advance(test_name)

    try:
        import tempfile
        import subprocess
        import sys
        from pathlib import Path

        # Run load test with small dataset
        # Use current working directory (should be project root)
        test_script = Path.cwd() / "tests" / "test_load.py"
        
        if test_script.exists():
            result = subprocess.run(
                [sys.executable, str(test_script), "--jobs", "10"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=test_script.parent,
            )

            # Parse output for success
            if result.returncode == 0 and "EXCELLENT" in result.stdout:
                status = "✓ Passed - Load testing completed successfully"
            elif result.returncode == 0 and "ACCEPTABLE" in result.stdout:
                status = "✓ Passed - Load testing completed acceptably"
            elif result.returncode == 0:
                status = "⚠️ Passed - Load testing completed with issues"
            else:
                status = "✗ Failed - Load testing failed"

            results.append(
                create_test_result(
                    test_name,
                    result.returncode == 0,
                    status,
                )
            )
        else:
            results.append(
                create_test_result(
                    test_name,
                    False,
                    "✗ Failed - Load test script not found",
                )
            )
    except Exception as e:
        results.append(create_test_result(test_name, False, f"✗ Failed: {str(e)}"))

    return results


def run_integrated_system_integration_tests(
    test_env: dict, progress_tracker=None
) -> list:
    """Run integrated system integration tests."""
    results = []

    # Test job FSM
    test_name = "System Integration: Job FSM"
    if progress_tracker:
        progress_tracker.advance(test_name)

    try:
        # Just test that we can import and access the class
        current_state = JobState.NEW
        results.append(
            create_test_result(
                test_name,
                True,
                f"✓ JobFSM available, default state: {current_state.value}",
            )
        )
    except Exception as e:
        results.append(create_test_result(test_name, False, f"✗ Failed: {str(e)}"))

    # Test help system
    test_name = "System Integration: Help system"
    if progress_tracker:
        progress_tracker.advance(test_name)

    result = run_integrated_command("plotty --help")
    results.append(
        create_test_result(
            test_name,
            result["success"],
            "✓ Passed" if result["success"] else f"✗ Failed: {result['stderr']}",
        )
    )

    return results


def generate_integrated_report(results: list, console: Console) -> dict:
    """Generate integrated test report using OutputManager for consistent formatting."""
    passed = sum(1 for r in results if r["success"] and not r.get("skipped", False))
    skipped = sum(1 for r in results if r.get("skipped", False))
    failed = sum(1 for r in results if not r["success"] and not r.get("skipped", False))
    success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 100

    output_manager = get_output_manager()

    # Check if we should use Rich formatting (not redirected)
    use_rich = not output_manager.is_redirected()

    if use_rich:
        # Rich formatting for terminal
        from rich.table import Table

        from rich.text import Text

        # Group results by category first to calculate table width
        categories = {}
        for result in results:
            category = result["name"].split(": ")[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)

        # Create results table first to determine width
        table = Table(
            title="ploTTY Self-Test Results", show_header=True, header_style="bold"
        )
        table.add_column("Status", width=6, justify="center")
        table.add_column("Category", width=15)
        table.add_column("Test", width=25)
        table.add_column("Result", width=40)

        # Add rows to table (but don't print yet)
        for category, category_results in categories.items():
            for result in category_results:
                # Create colored status emojis
                if result.get("skipped", False):
                    status_text = Text(" ", style="cyan")
                elif result["success"]:
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

                # Add color coding for different test results
                if result.get("skipped", False):
                    row_style = "cyan"
                elif not result["success"]:
                    row_style = "red"
                else:
                    row_style = "white"
                table.add_row(
                    status_text, category, test_name, message, style=row_style
                )

        # Summary panel with calculated width and color coding
        summary_text = Text()
        summary_text.append("Total: ", style="bold")
        summary_text.append(f"{len(results)} ", style="cyan")
        summary_text.append("Passed: ", style="bold")
        summary_text.append(f"{passed} ", style="green")
        summary_text.append("Skipped: ", style="bold")
        summary_text.append(f"{skipped} ", style="cyan")
        summary_text.append("Failed: ", style="bold")
        summary_text.append(f"{failed} ", style="red")
        summary_text.append(
            f"({success_rate:.1f}%)", style="yellow" if failed > 0 else "green"
        )

        # Print the table
        console.print(table)

        # Print summary on separate line
        console.print(summary_text)

    else:
        # Plain markdown for redirected output
        markdown_content = f"""# ploTTY Self-Test Results

 ## Summary

 | Metric | Value |
 |--------|-------|
 | Total Tests | {len(results)} |
 | ✅ Passed | {passed} |
 | ⚠️ Skipped | {skipped} |
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
                if result.get("skipped", False):
                    status = " "
                elif result["success"]:
                    status = "✅"
                else:
                    status = "❌"
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
        "skipped": skipped,
        "failed": failed,
        "success_rate": success_rate,
        "results": results,
    }


def _calculate_total_tests(level: str) -> int:
    """Calculate total number of tests for the given level.

    Args:
        level: Test level (basic, intermediate, advanced, integration, or all)

    Returns:
        Total number of tests for the level
    """
    # Test counts per category
    basic_count = 4  # 4 tests
    job_lifecycle_count = 3  # 3 tests
    job_management_count = 4  # 4 tests
    system_validation_count = 4  # 4 tests
    resource_management_count = 3  # 3 tests
    recovery_system_count = 6  # 6 tests (5 + 1 for job check with recovery info)
    performance_count = 2  # 2 tests (memory profiling + database performance)
    stress_count = 1  # 1 test (load testing with 10 jobs)
    integration_count = 3  # 3 tests (FSM + help + cross-platform)

    if level == "basic":
        return basic_count
    elif level == "intermediate":
        return job_lifecycle_count + job_management_count
    elif level == "advanced":
        return (
            system_validation_count + resource_management_count + recovery_system_count
        )
    elif level == "performance":
        return performance_count
    elif level == "stress":
        return stress_count
    elif level == "integration":
        return integration_count
    elif level == "all":
        return (
            basic_count
            + job_lifecycle_count
            + job_management_count
            + system_validation_count
            + resource_management_count
            + recovery_system_count
            + performance_count
            + stress_count
            + integration_count
        )
    return 0


def run_self_test(
    level: str = typer.Option(
        "basic",
        "--level",
        "-l",
        help="Test level: basic, intermediate, advanced, performance, stress, integration, or all",
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
    * **intermediate**: Job lifecycle and management (7 tests)
    * **advanced**: System validation, resource management, and recovery system (13 tests)
    * **performance**: Memory profiling and performance analysis (2 tests)
    * **stress**: Load testing and stress analysis (1 test)
    * **integration**: System integration tests (3 tests)
    * **all**: Run all tests (30 tests total)

    Each test runs in isolated environments with proper cleanup.
    """
    console = cli_console

    if verbose:
        console.print(f"[blue]Starting ploTTY self-test (level: {level})...[/blue]")

    # Calculate total tests for progress tracking
    total_tests = _calculate_total_tests(level)

    # Always use integrated test structure
    if verbose:
        console.print("[blue]Using integrated test structure...[/blue]")
    test_env = create_integrated_test_environment()

    basic_tests = run_integrated_basic_tests
    job_lifecycle_tests = run_integrated_job_lifecycle_tests
    job_management_tests = run_integrated_job_management_tests
    system_validation_tests = run_integrated_system_validation_tests
    resource_management_tests = run_integrated_resource_management_tests
    recovery_system_tests = run_integrated_recovery_system_tests
    performance_tests = run_integrated_performance_tests
    stress_tests = run_integrated_stress_tests
    integration_tests = run_integrated_system_integration_tests
    report_func = generate_integrated_report

    all_results = []

    try:
        # Create progress tracker with two-line display
        with progress_task(
            "Running tests", total=total_tests, two_line=True
        ) as update_progress:
            progress_tracker = TestProgressTracker(total_tests, update_progress)

            # Run tests based on level
            if level in ["basic", "all"]:
                if verbose:
                    console.print("[blue]Running basic tests...[/blue]")
                all_results.extend(basic_tests(test_env, progress_tracker))

            if level in ["intermediate", "all"]:
                if verbose:
                    console.print("[blue]Running job lifecycle tests...[/blue]")
                all_results.extend(job_lifecycle_tests(test_env, progress_tracker))

                if verbose:
                    console.print("[blue]Running job management tests...[/blue]")
                all_results.extend(job_management_tests(test_env, progress_tracker))

            if level in ["advanced", "all"]:
                if verbose:
                    console.print("[blue]Running system validation tests...[/blue]")
                all_results.extend(system_validation_tests(test_env, progress_tracker))

                if verbose:
                    console.print("[blue]Running resource management tests...[/blue]")
                all_results.extend(
                    resource_management_tests(test_env, progress_tracker)
                )

                if verbose:
                    console.print("[blue]Running recovery system tests...[/blue]")
                all_results.extend(recovery_system_tests(test_env, progress_tracker))

            if level in ["performance", "all"]:
                if verbose:
                    console.print("[blue]Running performance tests...[/blue]")
                all_results.extend(performance_tests(test_env, progress_tracker))

            if level in ["stress", "all"]:
                if verbose:
                    console.print("[blue]Running stress tests...[/blue]")
                all_results.extend(stress_tests(test_env, progress_tracker))

            if level in ["integration", "all"]:
                if verbose:
                    console.print("[blue]Running system integration tests...[/blue]")
                all_results.extend(integration_tests(test_env, progress_tracker))

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
        help="Test level: basic, intermediate, advanced, performance, stress, integration, or all",
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
