"""
Driver registry for dynamic driver discovery and management.

This module provides the core registry system for discovering, loading,
and managing vfab drivers from multiple sources.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

try:
    from .base import (
        BaseDriver,
        DriverClass,
        DriverInfo,
        DriverStatus,
        DriverType,
    )
except ImportError:
    # Fallback for when running as a script
    from vfab.drivers.base import (
        BaseDriver,
        DriverClass,
        DriverInfo,
        DriverStatus,
        DriverType,
    )

logger = logging.getLogger(__name__)


class DriverSource(str, Enum):
    """Sources where drivers can be found."""

    BUILTIN = "builtin"  # Built-in drivers with vfab
    PLUGIN = "plugin"  # External plugin packages
    USER = "user"  # User-defined drivers
    SYSTEM = "system"  # System-wide drivers


class DriverRegistry:
    """Registry for discovering and managing vfab drivers.

    The registry maintains a collection of available drivers from various
    sources and provides methods for discovery, loading, and instantiation.
    """

    def __init__(self) -> None:
        """Initialize the driver registry."""
        self._drivers: Dict[str, DriverClass] = {}
        self._driver_sources: Dict[str, DriverSource] = {}
        self._driver_info: Dict[str, DriverInfo] = {}
        self._search_paths: List[Path] = []
        self._initialized: bool = False

    def add_search_path(self, path: Union[str, Path]) -> None:
        """Add a path to search for drivers.

        Args:
            path: Directory path to search for drivers
        """
        path_obj = Path(path)
        if path_obj.exists() and path_obj.is_dir():
            self._search_paths.append(path_obj.resolve())
            logger.debug(f"Added driver search path: {path_obj}")
        else:
            logger.warning(f"Driver search path does not exist: {path}")

    def register_driver(
        self, driver_class: DriverClass, source: DriverSource = DriverSource.BUILTIN
    ) -> bool:
        """Register a driver class with the registry.

        Args:
            driver_class: Driver class to register
            source: Source of the driver

        Returns:
            True if registration successful
        """
        try:
            # Get driver info from class
            if not hasattr(driver_class, "DRIVER_INFO"):
                logger.error(
                    f"Driver class {driver_class.__name__} missing DRIVER_INFO"
                )
                return False

            driver_info = driver_class.DRIVER_INFO
            driver_name = driver_info.name

            # Check for conflicts
            if driver_name in self._drivers:
                existing_source = self._driver_sources[driver_name]
                if (
                    source == DriverSource.BUILTIN
                    and existing_source != DriverSource.BUILTIN
                ):
                    # Builtin drivers take precedence
                    logger.debug(
                        f"Overriding non-builtin driver {driver_name} with builtin"
                    )
                elif (
                    existing_source == DriverSource.BUILTIN
                    and source != DriverSource.BUILTIN
                ):
                    logger.debug(
                        f"Skipping non-builtin driver {driver_name}, builtin exists"
                    )
                    return False
                else:
                    logger.warning(
                        f"Driver name conflict: {driver_name} from {source} vs {existing_source}"
                    )

            # Register the driver
            self._drivers[driver_name] = driver_class
            self._driver_sources[driver_name] = source
            self._driver_info[driver_name] = driver_info

            logger.debug(f"Registered driver {driver_name} from {source}")
            return True

        except Exception as e:
            logger.error(f"Failed to register driver {driver_class.__name__}: {e}")
            return False

    def unregister_driver(self, driver_name: str) -> bool:
        """Unregister a driver from the registry.

        Args:
            driver_name: Name of driver to unregister

        Returns:
            True if unregistration successful
        """
        if driver_name in self._drivers:
            del self._drivers[driver_name]
            del self._driver_sources[driver_name]
            del self._driver_info[driver_name]
            logger.debug(f"Unregistered driver {driver_name}")
            return True
        return False

    def _discover_plugin_drivers(self) -> None:
        """Discover drivers from installed plugin packages."""
        # Look for packages with vfab_driver entry point
        try:
            # Try importlib.metadata first (Python 3.8+)
            try:
                from importlib.metadata import entry_points

                vfab_entry_points = entry_points()
                if hasattr(vfab_entry_points, "select"):
                    # New API (Python 3.10+)
                    plugin_eps = vfab_entry_points.select(group="vfab_driver")
                else:
                    # Old API - skip if not available
                    plugin_eps = []
            except ImportError:
                # Skip plugin discovery if metadata not available
                logger.debug(
                    "importlib.metadata not available, skipping plugin discovery"
                )
                return

            for entry_point in plugin_eps:
                try:
                    driver_class = entry_point.load()
                    self.register_driver(driver_class, DriverSource.PLUGIN)
                    logger.debug(f"Loaded plugin driver: {entry_point.name}")
                except Exception as e:
                    logger.warning(
                        f"Failed to load plugin driver {entry_point.name}: {e}"
                    )

        except Exception as e:
            logger.debug(f"Plugin discovery failed: {e}")

    def _discover_user_drivers(self, search_path: Path) -> None:
        """Discover user drivers from a search path.

        Args:
            search_path: Directory path to search for drivers
        """
        for driver_file in search_path.glob("**/*_driver.py"):
            try:
                module_name = driver_file.stem
                spec = importlib.util.spec_from_file_location(
                    module_name, str(driver_file)
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    # Look for driver classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BaseDriver)
                            and attr != BaseDriver
                        ):
                            self.register_driver(attr, DriverSource.USER)

            except Exception as e:
                logger.warning(f"Failed to load user driver {driver_file}: {e}")

    def discover_drivers(self) -> None:
        """Discover drivers from all configured sources."""
        logger.info("Discovering drivers...")

        # Discover built-in drivers
        self._discover_builtin_drivers()

        # Discover plugin drivers
        self._discover_plugin_drivers()

        # Discover user drivers from search paths
        for search_path in self._search_paths:
            self._discover_user_drivers(search_path)

        self._initialized = True
        logger.info(f"Driver discovery complete. Found {len(self._drivers)} drivers.")

    def _discover_builtin_drivers(self) -> None:
        """Discover built-in drivers from the vfab.drivers package."""
        try:
            # Import the drivers package
            drivers_package = importlib.import_module("vfab.drivers")
            drivers_path = (
                Path(drivers_package.__file__).parent
                if drivers_package.__file__
                else Path.cwd()
            )

            # Look for driver modules
            for module_file in drivers_path.glob("*.py"):
                if module_file.name.startswith("_") or module_file.name == "base.py":
                    continue

                module_name = module_file.stem
                spec = importlib.util.spec_from_file_location(
                    module_name, str(module_file)
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)

                    # Look for driver classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BaseDriver)
                            and attr != BaseDriver
                        ):
                            self.register_driver(attr, DriverSource.USER)

        except Exception as e:
            logger.warning(f"Failed to discover builtin drivers: {e}")

    def _load_driver_module(self, module_name: str, source: DriverSource) -> None:
        """Load a driver module and register any driver classes.

        Args:
            module_name: Name of the module to load
            source: Source of the module
        """
        try:
            module = importlib.import_module(module_name)

            # Look for driver classes in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseDriver)
                    and attr != BaseDriver
                    and hasattr(attr, "DRIVER_INFO")
                ):
                    self.register_driver(attr, source)

        except ImportError as e:
            logger.debug(f"Failed to import driver module {module_name}: {e}")

    def get_driver_names(self) -> List[str]:
        """Get list of all registered driver names.

        Returns:
            List of driver names
        """
        return list(self._drivers.keys())

    def get_driver_class(self, driver_name: str) -> Optional[DriverClass]:
        """Get a driver class by name.

        Args:
            driver_name: Name of the driver

        Returns:
            Driver class or None if not found
        """
        return self._drivers.get(driver_name)

    def get_driver_info(self, driver_name: str) -> Optional[DriverInfo]:
        """Get driver information by name.

        Returns:
            DriverInfo object or None if not found
        """
        return self._driver_info.get(driver_name)

    def get_driver_source(self, driver_name: str) -> Optional[DriverSource]:
        """Get the source of a driver.

        Args:
            driver_name: Name of the driver

        Returns:
            DriverSource or None if not found
        """
        return self._driver_sources.get(driver_name)

    def get_drivers_by_type(self, driver_type: DriverType) -> List[str]:
        """Get list of drivers of a specific type.

        Args:
            driver_type: Type of drivers to get

        Returns:
            List of driver names
        """
        return [
            name
            for name, info in self._driver_info.items()
            if info.driver_type == driver_type
        ]

    def get_available_drivers(self) -> List[str]:
        """Get list of drivers that are available and functional.

        Returns:
            List of available driver names
        """
        available = []
        for name, driver_class in self._drivers.items():
            try:
                if driver_class.is_available():
                    available.append(name)
            except Exception as e:
                logger.warning(f"Error checking availability of driver {name}: {e}")
        return available

    def get_installed_drivers(self) -> List[str]:
        """Get list of drivers that are installed.

        Returns:
            List of installed driver names
        """
        installed = []
        for name, driver_class in self._drivers.items():
            try:
                status = driver_class.get_installation_status()
                if status in [DriverStatus.INSTALLED, DriverStatus.AVAILABLE]:
                    installed.append(name)
            except Exception as e:
                logger.warning(
                    f"Error checking installation status of driver {name}: {e}"
                )
        return installed

    def create_driver(
        self, driver_name: str, config: Optional[Dict[str, Any]] = None
    ) -> Optional[BaseDriver]:
        """Create an instance of a driver.

        Args:
            driver_name: Name of the driver to create
            config: Optional driver configuration

        Returns:
            Driver instance or None if creation failed
        """
        driver_class = self.get_driver_class(driver_name)
        if not driver_class:
            logger.error(f"Driver not found: {driver_name}")
            return None

        try:
            return driver_class(config)
        except Exception as e:
            logger.error(f"Failed to create driver instance {driver_name}: {e}")
            return None

    def is_initialized(self) -> bool:
        """Check if the registry has been initialized.

        Returns:
            True if initialized
        """
        return self._initialized

    def get_registry_info(self) -> Dict[str, Any]:
        """Get information about the registry state.

        Returns:
            Dictionary with registry information
        """
        return {
            "initialized": self._initialized,
            "total_drivers": len(self._drivers),
            "available_drivers": len(self.get_available_drivers()),
            "installed_drivers": len(self.get_installed_drivers()),
            "search_paths": [str(p) for p in self._search_paths],
            "drivers_by_type": {
                driver_type.value: self.get_drivers_by_type(driver_type)
                for driver_type in DriverType
            },
            "drivers_by_source": {
                source.value: [
                    name for name, src in self._driver_sources.items() if src == source
                ]
                for source in DriverSource
            },
        }


# Global registry instance
_global_registry: Optional[DriverRegistry] = None


def get_registry() -> DriverRegistry:
    """Get the global driver registry instance.

    Returns:
        Global DriverRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = DriverRegistry()
        # Add default search paths
        _global_registry.add_search_path(Path.home() / ".vfab" / "drivers")
        _global_registry.add_search_path(Path("/etc/vfab/drivers"))
        _global_registry.add_search_path(Path.cwd() / "drivers")
    return _global_registry


def initialize_registry() -> None:
    """Initialize the global registry by discovering drivers."""
    registry = get_registry()
    if not registry.is_initialized():
        registry.discover_drivers()


def get_driver_names() -> List[str]:
    """Get list of all registered driver names.

    Returns:
        List of driver names
    """
    return get_registry().get_driver_names()


def get_available_drivers() -> List[str]:
    """Get list of available drivers.

    Returns:
        List of available driver names
    """
    return get_registry().get_available_drivers()


def create_driver(
    driver_name: str, config: Optional[Dict[str, Any]] = None
) -> Optional[BaseDriver]:
    """Create a driver instance.

    Args:
        driver_name: Name of the driver
        config: Optional configuration

    Returns:
        Driver instance or None
    """
    return get_registry().create_driver(driver_name, config)
