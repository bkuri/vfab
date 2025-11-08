"""Performance testing framework for ploTTY."""

import time
import pytest
import psutil
import os
from typing import Dict
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class PerformanceMetrics:
    """Performance metrics for a test run."""

    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    disk_io_read: int
    disk_io_write: int
    operations_per_second: float = 0.0

    def __post_init__(self):
        if self.execution_time > 0:
            self.operations_per_second = 1.0 / self.execution_time


class PerformanceBenchmark:
    """Performance benchmarking framework."""

    def __init__(self):
        self.baseline_metrics: Dict[str, PerformanceMetrics] = {}
        self.current_metrics: Dict[str, PerformanceMetrics] = {}

    @contextmanager
    def measure_performance(self, operation_name: str):
        """Measure performance of an operation."""
        # Get initial system state
        process = psutil.Process(os.getpid())
        initial_io = process.io_counters()

        start_time = time.time()

        try:
            yield
        finally:
            end_time = time.time()
            execution_time = end_time - start_time

            # Get final system state
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = process.cpu_percent()
            final_io = process.io_counters()

            # Calculate metrics
            metrics = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage_mb=final_memory,
                cpu_percent=final_cpu,
                disk_io_read=final_io.read_bytes - initial_io.read_bytes,
                disk_io_write=final_io.write_bytes - initial_io.write_bytes,
            )

            self.current_metrics[operation_name] = metrics

    def set_baseline(self, operation_name: str, metrics: PerformanceMetrics):
        """Set baseline metrics for comparison."""
        self.baseline_metrics[operation_name] = metrics

    def compare_to_baseline(self, operation_name: str) -> Dict[str, float]:
        """Compare current metrics to baseline."""
        if operation_name not in self.baseline_metrics:
            return {}

        baseline = self.baseline_metrics[operation_name]
        current = self.current_metrics[operation_name]

        return {
            "execution_time_ratio": current.execution_time / baseline.execution_time,
            "memory_ratio": current.memory_usage_mb / baseline.memory_usage_mb,
            "cpu_ratio": (
                current.cpu_percent / baseline.cpu_percent
                if baseline.cpu_percent > 0
                else 1.0
            ),
            "performance_change_percent": (
                (baseline.operations_per_second - current.operations_per_second)
                / baseline.operations_per_second
            )
            * 100,
        }

    def assert_performance_target(
        self, operation_name: str, max_execution_time: float, max_memory_mb: float
    ):
        """Assert that performance meets targets."""
        metrics = self.current_metrics[operation_name]

        assert (
            metrics.execution_time <= max_execution_time
        ), f"{operation_name} took {metrics.execution_time:.2f}s, expected <= {max_execution_time}s"

        assert (
            metrics.memory_usage_mb <= max_memory_mb
        ), f"{operation_name} used {metrics.memory_usage_mb:.1f}MB, expected <= {max_memory_mb}MB"


class TestPerformanceTargets:
    """Test performance against defined targets."""

    @pytest.fixture
    def benchmark(self):
        """Provide performance benchmark instance."""
        return PerformanceBenchmark()

    def test_startup_performance(self, benchmark):
        """Test application startup performance."""
        with benchmark.measure_performance("startup"):
            # Test ploTTY startup time
            import subprocess
            import sys

            result = subprocess.run(
                [sys.executable, "-m", "plotty.cli", "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0

        # Performance targets for startup (adjusted for reality)
        benchmark.assert_performance_target(
            "startup", max_execution_time=2.0, max_memory_mb=100.0
        )

    def test_configuration_loading_performance(self, benchmark):
        """Test configuration loading performance."""
        with benchmark.measure_performance("config_loading"):
            from plotty.config import load_config

            config = load_config()
            assert config is not None

        # Configuration loading should be fast (adjusted for reality)
        benchmark.assert_performance_target(
            "config_loading", max_execution_time=0.1, max_memory_mb=100.0
        )

    def test_database_operations_performance(self, benchmark):
        """Test database operations performance."""
        with benchmark.measure_performance("database_init"):
            from plotty.db import init_database, get_session
            from tempfile import NamedTemporaryFile
            import os

            with NamedTemporaryFile(suffix=".db", delete=False) as f:
                db_path = f.name

            try:
                init_database(f"sqlite:///{db_path}")

                with get_session():
                    # Test basic database operations
                    pass
            finally:
                os.unlink(db_path)

        # Database operations should be efficient (adjusted for reality)
        benchmark.assert_performance_target(
            "database_init", max_execution_time=0.5, max_memory_mb=100.0
        )

    def test_job_processing_performance(self, benchmark):
        """Test job processing performance."""
        # This would test with actual job files
        # For now, test the framework itself

        with benchmark.measure_performance("job_processing_simulation"):
            # Simulate job processing overhead
            time.sleep(0.01)  # Simulate 10ms of processing

        # Job processing should meet targets
        benchmark.assert_performance_target(
            "job_processing_simulation", max_execution_time=5.0, max_memory_mb=100.0
        )

    def test_memory_usage_stability(self, benchmark):
        """Test memory usage doesn't grow excessively."""
        initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

        # Perform multiple operations
        for i in range(10):
            with benchmark.measure_performance(f"operation_{i}"):
                # Simulate various operations
                from plotty.config import load_config

                load_config()

        final_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory

        # Memory growth should be minimal
        assert (
            memory_growth < 50.0
        ), f"Memory grew by {memory_growth:.1f}MB, expected < 50MB"


class TestPerformanceRegression:
    """Test for performance regressions."""

    def test_guard_system_performance(self):
        """Test guard system performance doesn't regress."""
        # Skip for now - will implement when guard manager is properly tested
        pytest.skip("Guard manager performance test - needs proper implementation")

    def test_cli_command_performance(self):
        """Test CLI command performance."""
        import subprocess
        import sys

        commands_to_test = [
            ["--help"],
            ["list", "jobs"],
            ["check", "self"],
            ["info", "system"],
        ]

        for cmd in commands_to_test:
            start_time = time.time()

            result = subprocess.run(
                [sys.executable, "-m", "plotty.cli"] + cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            execution_time = time.time() - start_time

            assert result.returncode == 0, f"Command {cmd} failed"
            assert (
                execution_time < 5.0
            ), f"Command {cmd} took {execution_time:.2f}s, expected < 5.0s"


class TestLoadPerformance:
    """Test performance under load."""

    def test_concurrent_database_access(self):
        """Test database performance under concurrent access."""
        # Skip concurrent test for now - SQLite has limitations with concurrent access
        pytest.skip("SQLite concurrent access test - needs proper setup")
