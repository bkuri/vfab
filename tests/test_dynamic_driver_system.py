"""
Tests for the dynamic driver system.

This module tests the driver registry, plugin loading, and dynamic
configuration generation functionality.
"""

from __future__ import annotations

import pytest
import tempfile
from pathlib import Path
from typing import Any, Dict


# Test the base driver interface
def test_base_driver_interface():
    """Test the BaseDriver abstract interface."""
    from vfab.drivers.base import BaseDriver, DriverInfo, DriverType, DriverStatus

    # Create a concrete test driver
    class TestDriver(BaseDriver):
        DRIVER_INFO = DriverInfo(
            name="test",
            display_name="Test Driver",
            version="1.0.0",
            description="A test driver for unit testing",
            driver_type=DriverType.OTHER,
        )

        @classmethod
        def is_available(cls) -> bool:
            return True

        @classmethod
        def get_installation_status(cls) -> DriverStatus:
            return DriverStatus.AVAILABLE

        @classmethod
        def install(cls, force: bool = False) -> bool:
            return True

        def test(self) -> Any:
            from vfab.drivers.base import DriverTestResult

            return DriverTestResult(success=True, message="Test passed")

        def list_devices(self) -> list:
            return [{"id": "test", "name": "Test Device"}]

    # Test instantiation
    driver = TestDriver()
    assert driver.name == "test"
    assert driver.driver_type == DriverType.OTHER

    # Test methods
    assert driver.is_available()
    assert driver.get_installation_status() == DriverStatus.AVAILABLE
    assert driver.install()

    test_result = driver.test()
    assert test_result.success

    devices = driver.list_devices()
    assert len(devices) == 1
    assert devices[0]["id"] == "test"


def test_driver_registry():
    """Test the DriverRegistry functionality."""
    from vfab.drivers.registry import DriverRegistry, DriverSource
    from vfab.drivers.base import BaseDriver, DriverInfo, DriverType

    # Create a test registry
    registry = DriverRegistry()

    # Create a test driver
    class TestDriver(BaseDriver):
        DRIVER_INFO = DriverInfo(
            name="registry_test",
            display_name="Registry Test Driver",
            version="1.0.0",
            description="Test driver for registry testing",
            driver_type=DriverType.OTHER,
        )

        @classmethod
        def is_available(cls) -> bool:
            return True

        @classmethod
        def get_installation_status(cls) -> Any:
            from vfab.drivers.base import DriverStatus

            return DriverStatus.AVAILABLE

        @classmethod
        def install(cls, force: bool = False) -> bool:
            return True

        def test(self) -> Any:
            from vfab.drivers.base import DriverTestResult

            return DriverTestResult(success=True, message="Test passed")

        def list_devices(self) -> list:
            return []

    # Register the driver
    success = registry.register_driver(TestDriver, DriverSource.BUILTIN)
    assert success

    # Test retrieval
    driver_class = registry.get_driver_class("registry_test")
    assert driver_class == TestDriver

    driver_info = registry.get_driver_info("registry_test")
    assert driver_info.name == "registry_test"

    # Test listing
    driver_names = registry.get_driver_names()
    assert "registry_test" in driver_names

    available_drivers = registry.get_available_drivers()
    assert "registry_test" in available_drivers

    # Test driver creation
    driver_instance = registry.create_driver("registry_test")
    assert isinstance(driver_instance, TestDriver)

    # Test unregistration
    unregistered = registry.unregister_driver("registry_test")
    assert unregistered

    driver_names = registry.get_driver_names()
    assert "registry_test" not in driver_names


def test_plugin_loader():
    """Test the PluginLoader functionality."""
    from vfab.drivers.plugin_loader import PluginLoader
    from vfab.drivers.registry import DriverRegistry

    # Create a temporary plugin directory
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin_dir = Path(temp_dir)

        # Create a test plugin file
        plugin_file = plugin_dir / "test_driver.py"
        plugin_content = """
from vfab.drivers.base import BaseDriver, DriverInfo, DriverType, DriverStatus, DriverTestResult

class TestPluginDriver(BaseDriver):
    DRIVER_INFO = DriverInfo(
        name="plugin_test",
        display_name="Plugin Test Driver",
        version="1.0.0",
        description="Test driver loaded from plugin",
        driver_type=DriverType.OTHER
    )
    
    @classmethod
    def is_available(cls) -> bool:
        return True
        
    @classmethod
    def get_installation_status(cls) -> DriverStatus:
        return DriverStatus.AVAILABLE
        
    @classmethod
    def install(cls, force: bool = False) -> bool:
        return True
        
    def test(self) -> DriverTestResult:
        return DriverTestResult(success=True, message="Plugin test passed")
        
    def list_devices(self) -> list:
        return [{"id": "plugin", "name": "Plugin Device"}]
"""
        plugin_file.write_text(plugin_content)

        # Test plugin loading
        registry = DriverRegistry()
        loader = PluginLoader(registry)

        loaded_count = loader.load_from_directory(plugin_dir)
        assert loaded_count >= 1

        # Check if driver was registered
        driver_names = registry.get_driver_names()
        assert "plugin_test" in driver_names


def test_config_schema_generation():
    """Test dynamic configuration schema generation."""
    from vfab.drivers.config_schema import DynamicConfigSchema
    from vfab.drivers.registry import DriverRegistry

    # Create a test registry with a mock driver
    registry = DriverRegistry()

    # Create schema generator
    generator = DynamicConfigSchema(registry)

    # Generate schema
    schema = generator.generate_schema()

    # Check schema structure
    assert "$schema" in schema
    assert "type" in schema
    assert schema["type"] == "object"
    assert "properties" in schema

    # Check base properties
    properties = schema["properties"]
    assert "version" in properties
    assert "logging" in properties
    assert "database" in properties
    assert "drivers" in properties

    # Test default config generation
    default_config = generator.get_default_config()
    assert isinstance(default_config, dict)
    assert "version" in default_config


def test_driver_capabilities():
    """Test driver capability system."""
    from vfab.drivers.base import (
        BaseDriver,
        DriverInfo,
        DriverType,
        DriverCapability,
        DriverStatus,
        DriverTestResult,
    )

    class CapableDriver(BaseDriver):
        DRIVER_INFO = DriverInfo(
            name="capable_test",
            display_name="Capable Test Driver",
            version="1.0.0",
            description="Test driver with capabilities",
            driver_type=DriverType.OTHER,
            capabilities=[
                DriverCapability(
                    name="test_capability",
                    description="A test capability",
                    required=True,
                ),
                DriverCapability(
                    name="optional_capability",
                    description="An optional capability",
                    required=False,
                ),
            ],
        )

        @classmethod
        def is_available(cls) -> bool:
            return True

        @classmethod
        def get_installation_status(cls) -> DriverStatus:
            return DriverStatus.AVAILABLE

        @classmethod
        def install(cls, force: bool = False) -> bool:
            return True

        def test(self) -> DriverTestResult:
            return DriverTestResult(success=True, message="Capability test passed")

        def list_devices(self) -> list:
            return []

    driver = CapableDriver()

    # Test capability methods
    capabilities = driver.get_capabilities()
    assert len(capabilities) == 2

    assert driver.has_capability("test_capability")
    assert driver.has_capability("optional_capability")
    assert not driver.has_capability("nonexistent_capability")


def test_driver_type_enums():
    """Test driver type and status enums."""
    from vfab.drivers.base import DriverType, DriverStatus

    # Test DriverType enum
    assert DriverType.PLOTTER == "plotter"
    assert DriverType.CAMERA == "camera"
    assert DriverType.DATABASE == "database"
    assert DriverType.NETWORK == "network"
    assert DriverType.STORAGE == "storage"
    assert DriverType.OTHER == "other"

    # Test DriverStatus enum
    assert DriverStatus.NOT_INSTALLED == "not_installed"
    assert DriverStatus.INSTALLED == "installed"
    assert DriverStatus.AVAILABLE == "available"
    assert DriverStatus.ERROR == "error"
    assert DriverStatus.UNKNOWN == "unknown"


def test_global_registry_functions():
    """Test global registry convenience functions."""
    from vfab.drivers.registry import (
        get_registry,
        initialize_registry,
        get_driver_names,
    )

    # Initialize global registry
    initialize_registry()

    # Get global registry
    registry = get_registry()
    assert registry is not None

    # Test convenience functions
    driver_names = get_driver_names()
    assert isinstance(driver_names, list)


if __name__ == "__main__":
    # Run basic tests
    test_base_driver_interface()
    test_driver_registry()
    test_driver_capabilities()
    test_driver_type_enums()
    test_global_registry_functions()

    print("All basic driver system tests passed!")
