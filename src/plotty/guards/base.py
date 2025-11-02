"""
Base classes and enums for the guards system.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GuardResult(Enum):
    """Result of guard evaluation."""

    PASS = "pass"
    FAIL = "fail"
    SOFT_FAIL = "soft_fail"  # Allow transition but warn


class GuardCheck:
    """Result of a single guard check."""

    def __init__(
        self,
        name: str,
        result: GuardResult,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.result = result
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "name": self.name,
            "result": self.result.value,
            "message": self.message,
            "details": self.details,
        }


class Guard:
    """Base class for all guards."""

    def __init__(self, config):
        self.config = config

    def check(self, *args, **kwargs) -> GuardCheck:
        """Check the guard condition.

        Returns:
            GuardCheck with result
        """
        raise NotImplementedError("Subclasses must implement check method")
