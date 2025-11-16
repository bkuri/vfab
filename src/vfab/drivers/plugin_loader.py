"""
Plugin loading system for vfab drivers.

This module provides utilities for loading and managing driver plugins
from various sources including entry points, configuration files, and
dynamic discovery.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

try:
    from .base import BaseDriver, DriverInfo
    from .registry import DriverRegistry, DriverSource
except ImportError:
    # Fallback for when running as a script
    from vfab.drivers.base import BaseDriver, DriverInfo
    from vfab.drivers.registry import DriverRegistry, DriverSource

logger = logging.getLogger(__name__)


class PluginLoader:
    """Handles loading of driver plugins from various sources."""

    def __init__(self, registry: DriverRegistry) -> None:
        """Initialize the plugin loader.

        Args:
            registry: Driver registry to register loaded plugins with
        """
        self.registry = registry
        self._loaded_plugins: Dict[str, Any] = {}

    def load_from_config(self, config_path: Union[str, Path]) -> int:
        """Load plugins from a configuration file.

        Args:
            config_path: Path to plugin configuration file

        Returns:
            Number of plugins loaded
        """
        config_path = Path(config_path)
        if not config_path.exists():
            logger.warning(f"Plugin config file not found: {config_path}")
            return 0

        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            plugins = config.get("plugins", [])
            loaded_count = 0

            for plugin_config in plugins:
                if self._load_plugin_from_config(plugin_config):
                    loaded_count += 1

            logger.info(f"Loaded {loaded_count} plugins from {config_path}")
            return loaded_count

        except Exception as e:
            logger.error(f"Failed to load plugins from {config_path}: {e}")
            return 0

    def _load_plugin_from_config(self, plugin_config: Dict[str, Any]) -> bool:
        """Load a single plugin from configuration.

        Args:
            plugin_config: Plugin configuration dictionary

        Returns:
            True if plugin loaded successfully
        """
        plugin_type = plugin_config.get("type")
        if plugin_type == "module":
            return self._load_module_plugin(plugin_config)
        elif plugin_type == "class":
            return self._load_class_plugin(plugin_config)
        elif plugin_type == "entry_point":
            return self._load_entry_point_plugin(plugin_config)
        else:
            logger.warning(f"Unknown plugin type: {plugin_type}")
            return False

    def _load_module_plugin(self, config: Dict[str, Any]) -> bool:
        """Load a plugin from a Python module.

        Args:
            config: Plugin configuration

        Returns:
            True if loaded successfully
        """
        module_name = config.get("module")
        if not module_name:
            logger.error("Module plugin missing 'module' field")
            return False

        try:
            import importlib

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
                    self.registry.register_driver(attr, DriverSource.USER)
                    logger.debug(f"Loaded module plugin driver: {attr_name}")
                    return True

            logger.warning(f"No driver classes found in module: {module_name}")
            return False

        except ImportError as e:
            logger.error(f"Failed to import module {module_name}: {e}")
            return False

    def _load_class_plugin(self, config: Dict[str, Any]) -> bool:
        """Load a plugin from a specific class.

        Args:
            config: Plugin configuration

        Returns:
            True if loaded successfully
        """
        module_name = config.get("module")
        class_name = config.get("class")

        if not module_name or not class_name:
            logger.error("Class plugin missing 'module' or 'class' field")
            return False

        try:
            import importlib

            module = importlib.import_module(module_name)
            driver_class = getattr(module, class_name)

            if (
                isinstance(driver_class, type)
                and issubclass(driver_class, BaseDriver)
                and driver_class != BaseDriver
                and hasattr(driver_class, "DRIVER_INFO")
            ):
                self.registry.register_driver(driver_class, DriverSource.USER)
                logger.debug(f"Loaded class plugin driver: {class_name}")
                return True
            else:
                logger.error(f"Class {class_name} is not a valid driver")
                return False

        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load class {module_name}.{class_name}: {e}")
            return False

    def _load_entry_point_plugin(self, config: Dict[str, Any]) -> bool:
        """Load a plugin from an entry point.

        Args:
            config: Plugin configuration

        Returns:
            True if loaded successfully
        """
        entry_point_name = config.get("entry_point")
        if not entry_point_name:
            logger.error("Entry point plugin missing 'entry_point' field")
            return False

        try:
            # Try importlib.metadata first
            try:
                from importlib.metadata import entry_points

                eps = entry_points()
                if hasattr(eps, "select"):
                    plugin_eps = eps.select(group="vfab_driver", name=entry_point_name)
                else:
                    # Old API not supported, skip
                    plugin_eps = []
            except ImportError:
                logger.debug("Entry points not available")
                return False

            for ep in plugin_eps:
                try:
                    driver_class = ep.load()
                    self.registry.register_driver(driver_class, DriverSource.PLUGIN)
                    logger.debug(f"Loaded entry point plugin: {entry_point_name}")
                    return True
                except Exception as e:
                    logger.warning(
                        f"Failed to load entry point {entry_point_name}: {e}"
                    )

            logger.warning(f"Entry point not found: {entry_point_name}")
            return False

        except Exception as e:
            logger.error(f"Failed to load entry point plugin {entry_point_name}: {e}")
            return False

    def load_from_directory(self, directory: Union[str, Path]) -> int:
        """Load all plugins from a directory.

        Args:
            directory: Directory containing plugin files

        Returns:
            Number of plugins loaded
        """
        directory = Path(directory)
        if not directory.exists() or not directory.is_dir():
            logger.warning(f"Plugin directory not found: {directory}")
            return 0

        loaded_count = 0

        # Load Python files
        for py_file in directory.glob("*.py"):
            if self._load_plugin_file(py_file):
                loaded_count += 1

        # Load plugin config files
        for config_file in directory.glob("*.json"):
            loaded_count += self.load_from_config(config_file)

        logger.info(f"Loaded {loaded_count} plugins from directory {directory}")
        return loaded_count

    def _load_plugin_file(self, plugin_file: Path) -> bool:
        """Load a plugin from a Python file.

        Args:
            plugin_file: Python file containing plugin

        Returns:
            True if plugin loaded successfully
        """
        if plugin_file.name.startswith("_"):
            return False

        try:
            import importlib.util

            module_name = plugin_file.stem
            spec = importlib.util.spec_from_file_location(module_name, str(plugin_file))

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Look for driver classes
                loaded_any = False
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseDriver)
                        and attr != BaseDriver
                        and hasattr(attr, "DRIVER_INFO")
                    ):
                        self.registry.register_driver(attr, DriverSource.USER)
                        logger.debug(f"Loaded file plugin driver: {attr_name}")
                        loaded_any = True

                return loaded_any

        except Exception as e:
            logger.warning(f"Failed to load plugin file {plugin_file}: {e}")

        return False

    def create_plugin_config_template(self, output_path: Union[str, Path]) -> None:
        """Create a template plugin configuration file.

        Args:
            output_path: Path where to create the template
        """
        template = {
            "plugins": [
                {
                    "type": "module",
                    "module": "my_driver_module",
                    "description": "Load all driver classes from a module",
                },
                {
                    "type": "class",
                    "module": "my_driver_module",
                    "class": "MyDriverClass",
                    "description": "Load a specific driver class",
                },
                {
                    "type": "entry_point",
                    "entry_point": "my_driver",
                    "description": "Load from an entry point",
                },
            ]
        }

        output_path = Path(output_path)
        with open(output_path, "w") as f:
            json.dump(template, f, indent=2)

        logger.info(f"Created plugin config template: {output_path}")


def load_plugins_from_standard_locations(registry: DriverRegistry) -> None:
    """Load plugins from standard vfab locations.

    Args:
        registry: Driver registry to load plugins into
    """
    loader = PluginLoader(registry)

    # Standard plugin locations
    plugin_paths = [
        Path.home() / ".vfab" / "plugins",
        Path("/etc/vfab/plugins"),
        Path.cwd() / "plugins",
        Path.cwd() / ".vfab" / "plugins",
    ]

    total_loaded = 0
    for plugin_path in plugin_paths:
        if plugin_path.exists():
            total_loaded += loader.load_from_directory(plugin_path)

    # Also check for plugin config files
    config_paths = [
        Path.home() / ".vfab" / "plugins.json",
        Path("/etc/vfab/plugins.json"),
        Path.cwd() / "plugins.json",
        Path.cwd() / ".vfab" / "plugins.json",
    ]

    for config_path in config_paths:
        if config_path.exists():
            total_loaded += loader.load_from_config(config_path)

    if total_loaded > 0:
        logger.info(f"Loaded {total_loaded} plugins from standard locations")


def setup_plugin_directories() -> None:
    """Create standard plugin directories if they don't exist."""
    directories = [
        Path.home() / ".vfab" / "plugins",
        Path.home() / ".vfab" / "drivers",
    ]

    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured plugin directory exists: {directory}")
        except Exception as e:
            logger.warning(f"Failed to create plugin directory {directory}: {e}")
