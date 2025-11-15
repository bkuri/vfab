"""
vfab testing framework.

This package provides comprehensive self-testing capabilities with isolated
environments, result reporting, and test utilities.
"""

from .test_environment import (
    TestEnvironment,
    create_test_environment,
    test_environment_context,
    get_test_svgs,
)

from .models import (
    TestStatus,
    TestCategory,
    TestResult,
    CategoryStats,
    TestSummary,
    TestSuite,
    TestTimer,
)

from .reporter import TestReporter

__all__ = [
    # Test environment
    "TestEnvironment",
    "create_test_environment",
    "test_environment_context",
    "get_test_svgs",
    # Data models
    "TestStatus",
    "TestCategory",
    "TestResult",
    "CategoryStats",
    "TestSummary",
    "TestSuite",
    "TestTimer",
    # Reporting
    "TestReporter",
]
