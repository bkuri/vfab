"""
Test result data models for ploTTY self-testing.

This module provides data classes for test results, summaries, and reporting
with proper type hints and serialization support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import time


class TestStatus(Enum):
    """Test result status."""

    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"


class TestCategory(Enum):
    """Test categories for organization."""

    BASIC_COMMANDS = "basic_commands"
    JOB_LIFECYCLE = "job_lifecycle"
    SYSTEM_INTEGRATION = "system_integration"
    DEVICE_OPERATIONS = "device_operations"
    ERROR_HANDLING = "error_handling"


@dataclass
class TestResult:
    """Individual test result."""

    category: TestCategory
    command: str
    status: TestStatus
    duration: float
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "category": self.category.value,
            "command": self.command,
            "status": self.status.value,
            "duration": self.duration,
            "message": self.message,
            "details": self.details,
            "error": self.error,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TestResult:
        """Create from dictionary."""
        return cls(
            category=TestCategory(data["category"]),
            command=data["command"],
            status=TestStatus(data["status"]),
            duration=data["duration"],
            message=data["message"],
            details=data.get("details"),
            error=data.get("error"),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class CategoryStats:
    """Statistics for a test category."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100

    def add_result(self, result: TestResult) -> None:
        """Add a test result to stats."""
        self.total += 1
        if result.status == TestStatus.PASS:
            self.passed += 1
        elif result.status == TestStatus.FAIL:
            self.failed += 1
        elif result.status == TestStatus.SKIP:
            self.skipped += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "success_rate": self.success_rate,
        }


@dataclass
class TestSummary:
    """Summary of all test results."""

    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    environment: str
    categories: Dict[str, CategoryStats] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    @property
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "duration": self.duration,
            "success_rate": self.success_rate,
            "environment": self.environment,
            "categories": {k: v.to_dict() for k, v in self.categories.items()},
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_results(
        cls, results: List[TestResult], environment: str, duration: float
    ) -> TestSummary:
        """Create summary from list of results."""
        # Calculate overall stats
        total_tests = len(results)
        passed = sum(1 for r in results if r.status == TestStatus.PASS)
        failed = sum(1 for r in results if r.status == TestStatus.FAIL)
        skipped = sum(1 for r in results if r.status == TestStatus.SKIP)

        # Calculate category stats
        categories: Dict[str, CategoryStats] = {}
        for result in results:
            category_key = result.category.value
            if category_key not in categories:
                categories[category_key] = CategoryStats()
            categories[category_key].add_result(result)

        return cls(
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration=duration,
            environment=environment,
            categories=categories,
        )


@dataclass
class TestSuite:
    """Complete test suite with results and metadata."""

    name: str
    version: str
    environment: str
    results: List[TestResult] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    @property
    def duration(self) -> float:
        """Get test suite duration."""
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def summary(self) -> TestSummary:
        """Get test summary."""
        return TestSummary.from_results(self.results, self.environment, self.duration)

    def add_result(self, result: TestResult) -> None:
        """Add a test result."""
        self.results.append(result)

    def finish(self) -> None:
        """Mark test suite as finished."""
        self.end_time = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "environment": self.environment,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "summary": self.summary.to_dict(),
            "results": [r.to_dict() for r in self.results],
        }


class TestTimer:
    """Context manager for timing test execution."""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None

    def __enter__(self) -> TestTimer:
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing."""
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time

    def get_duration(self) -> float:
        """Get duration in seconds."""
        return self.duration or 0.0


__all__ = [
    "TestStatus",
    "TestCategory",
    "TestResult",
    "CategoryStats",
    "TestSummary",
    "TestSuite",
    "TestTimer",
]
