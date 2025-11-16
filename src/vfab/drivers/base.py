"""
Base driver interface for vfab driver system.

This module defines the abstract interface that all drivers must implement,
providing a consistent API for driver management, testing, and configuration.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, Type, Union
from pathlib import Path

from pydantic import BaseModel, Field


class DriverType(str, Enum):
    """Types of drivers supported by vfab."""

    PLOTTER = "plotter"
    CAMERA = "camera"
    DATABASE = "database"
    NETWORK = "network"
    STORAGE = "storage"
    OTHER = "other"


class DriverStatus(str, Enum):
    """Driver installation and availability status."""

    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    AVAILABLE = "available"
    ERROR = "error"
    UNKNOWN = "unknown"


class DriverCapability(BaseModel):
    """Represents a specific capability of a driver."""

    name: str = Field(description="Name of the capability")
    description: str = Field(description="Human-readable description")
    required: bool = Field(
        default=False, description="Whether this capability is required"
    )
    config_schema: Optional[Dict[str, Any]] = Field(
        default=None, description="Configuration schema for this capability"
    )


class DriverInfo(BaseModel):
    """Information about a driver."""

    name: str = Field(description="Driver name")
    display_name: str = Field(description="Human-readable display name")
    version: str = Field(description="Driver version")
    description: str = Field(description="Driver description")
    author: str = Field(default="vfab", description="Driver author")
    driver_type: DriverType = Field(description="Type of driver")
    capabilities: List[DriverCapability] = Field(
        default_factory=list, description="Driver capabilities"
    )
    dependencies: List[str] = Field(
        default_factory=list, description="Required dependencies"
    )
    config_schema: Optional[Dict[str, Any]] = Field(
        default=None, description="Configuration schema"
    )
    website: Optional[str] = Field(
        default=None, description="Driver website/documentation"
    )


class DriverTestResult(BaseModel):
    """Result of driver functionality test."""

    success: bool = Field(description="Whether the test passed")
    message: str = Field(description="Test result message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional test details"
    )
    duration_ms: Optional[float] = Field(
        default=None, description="Test duration in milliseconds"
    )


class BaseDriver(ABC):
    """Abstract base class for all vfab drivers.

    All drivers must inherit from this class and implement the required methods
    to provide consistent functionality across different hardware and software
    components.
    """

    # Class-level driver information
    DRIVER_INFO: ClassVar[DriverInfo]

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the driver with optional configuration.

        Args:
            config: Driver-specific configuration dictionary
        """
        self.config = config or {}
        self._status: Optional[DriverStatus] = None

    @property
    def info(self) -> DriverInfo:
        """Get driver information."""
        return self.DRIVER_INFO

    @property
    def name(self) -> str:
        """Get driver name."""
        return self.DRIVER_INFO.name

    @property
    def driver_type(self) -> DriverType:
        """Get driver type."""
        return self.DRIVER_INFO.driver_type

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if the driver is available and functional.

        Returns:
            True if driver dependencies are satisfied and driver can be used
        """
        pass

    @classmethod
    @abstractmethod
    def get_installation_status(cls) -> DriverStatus:
        """Get the current installation status of the driver.

        Returns:
            Current installation status
        """
        pass

    @classmethod
    @abstractmethod
    def install(cls, force: bool = False) -> bool:
        """Install the driver and its dependencies.

        Args:
            force: Whether to force reinstall even if already installed

        Returns:
            True if installation was successful
        """
        pass

    @abstractmethod
    def test(self) -> DriverTestResult:
        """Test driver functionality.

        Returns:
            Test result with success status and details
        """
        pass

    @abstractmethod
    def list_devices(self) -> List[Dict[str, Any]]:
        """List available devices for this driver.

        Returns:
            List of device information dictionaries
        """
        pass

    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific device.

        Args:
            device_id: Identifier for the device

        Returns:
            Device information dictionary or None if not found
        """
        devices = self.list_devices()
        for device in devices:
            if device.get("id") == device_id or device.get("name") == device_id:
                return device
        return None

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate driver configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid
        """
        # Default implementation - subclasses should override
        return True

    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """Get the configuration schema for this driver.

        Returns:
            JSON schema for configuration validation
        """
        return self.DRIVER_INFO.config_schema

    def get_capabilities(self) -> List[DriverCapability]:
        """Get driver capabilities.

        Returns:
            List of driver capabilities
        """
        return self.DRIVER_INFO.capabilities

    def has_capability(self, capability_name: str) -> bool:
        """Check if driver has a specific capability.

        Args:
            capability_name: Name of the capability to check

        Returns:
            True if driver has the capability
        """
        return any(cap.name == capability_name for cap in self.get_capabilities())

    def __repr__(self) -> str:
        """String representation of the driver."""
        return (
            f"{self.__class__.__name__}(name='{self.name}', type='{self.driver_type}')"
        )


class PlotterDriver(BaseDriver):
    """Base class for plotter drivers."""

    @property
    def driver_type(self) -> DriverType:
        """Get driver type."""
        return DriverType.PLOTTER

    @abstractmethod
    def connect(self, device_id: Optional[str] = None) -> bool:
        """Connect to a plotter device.

        Args:
            device_id: Optional device identifier, uses first available if None

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the plotter.

        Returns:
            True if disconnection successful
        """
        pass

    @abstractmethod
    def get_position(self) -> Dict[str, float]:
        """Get current pen position.

        Returns:
            Dictionary with x, y coordinates and pen state
        """
        pass

    @abstractmethod
    def move_to(self, x: float, y: float, pen_down: bool = False) -> bool:
        """Move pen to specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            pen_down: Whether pen should be down during movement

        Returns:
            True if movement successful
        """
        pass


class CameraDriver(BaseDriver):
    """Base class for camera drivers."""

    @property
    def driver_type(self) -> DriverType:
        """Get driver type."""
        return DriverType.CAMERA

    @abstractmethod
    def capture_image(self, save_path: Optional[Path] = None) -> Optional[bytes]:
        """Capture an image from the camera.

        Args:
            save_path: Optional path to save the image

        Returns:
            Image data as bytes or None if capture failed
        """
        pass

    @abstractmethod
    def get_camera_info(self) -> Dict[str, Any]:
        """Get camera information and capabilities.

        Returns:
            Dictionary with camera information
        """
        pass


class DatabaseDriver(BaseDriver):
    """Base class for database drivers."""

    @property
    def driver_type(self) -> DriverType:
        """Get driver type."""
        return DriverType.DATABASE

    @abstractmethod
    def connect(self, connection_string: str) -> bool:
        """Connect to the database.

        Args:
            connection_string: Database connection string

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    def execute_query(
        self, query: str, params: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a database query.

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            Query results as list of dictionaries
        """
        pass


# Driver registry for type hints
DriverClass = Type[BaseDriver]
DriverInstance = BaseDriver
