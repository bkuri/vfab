"""
Modular self-test package for ploTTY CLI.

This package provides comprehensive self-testing capabilities with isolated
environments and detailed reporting, organized by test complexity levels.
"""

from .core import create_test_environment, run_command, create_test_svg
from .basic import run_basic_command_tests
from .intermediate import run_job_lifecycle_tests, run_job_management_tests
from .advanced import run_system_validation_tests, run_resource_management_tests
from .integration import run_system_integration_tests
from .reporting import generate_report

__all__ = [
    "create_test_environment",
    "run_command",
    "create_test_svg",
    "run_basic_command_tests",
    "run_job_lifecycle_tests",
    "run_job_management_tests",
    "run_system_validation_tests",
    "run_resource_management_tests",
    "run_system_integration_tests",
    "generate_report",
]
