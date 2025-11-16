"""
Dynamic configuration schema generation for vfab drivers.

This module provides utilities for generating configuration schemas
based on available drivers and their capabilities.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

try:
    from .base import BaseDriver, DriverType
    from .registry import DriverRegistry, get_registry, initialize_registry
except ImportError:
    # Fallback for when running as a script
    from vfab.drivers.base import BaseDriver, DriverType
    from vfab.drivers.registry import DriverRegistry, get_registry, initialize_registry

logger = logging.getLogger(__name__)


class DynamicConfigSchema:
    """Generates and manages dynamic configuration schemas for drivers."""

    def __init__(self, registry: Optional[DriverRegistry] = None) -> None:
        """Initialize the dynamic config schema generator.

        Args:
            registry: Driver registry to use, creates global one if None
        """
        self.registry = registry or get_registry()
        self._schema_cache: Optional[Dict[str, Any]] = None

    def generate_schema(self, include_deprecated: bool = False) -> Dict[str, Any]:
        """Generate a complete configuration schema for all available drivers.

        Args:
            include_deprecated: Whether to include deprecated configuration options

        Returns:
            Complete JSON schema for configuration
        """
        if self._schema_cache and not include_deprecated:
            return self._schema_cache

        # Initialize registry if needed
        if not self.registry.is_initialized():
            initialize_registry()

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "vfab Configuration Schema",
            "description": "Dynamic configuration schema generated from available drivers",
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        }

        # Add base vfab configuration
        schema["properties"].update(self._get_base_schema())

        # Add driver-specific configuration
        driver_configs = self._generate_driver_configs(include_deprecated)
        schema["properties"]["drivers"] = {
            "type": "object",
            "description": "Driver-specific configuration",
            "properties": driver_configs,
            "additionalProperties": False,
        }

        # Cache the schema if not including deprecated
        if not include_deprecated:
            self._schema_cache = schema

        return schema

    def _get_base_schema(self) -> Dict[str, Any]:
        """Get the base vfab configuration schema.

        Returns:
            Base configuration schema
        """
        return {
            "version": {
                "type": "string",
                "description": "Configuration file version",
                "default": "1.0",
            },
            "logging": {
                "type": "object",
                "description": "Logging configuration",
                "properties": {
                    "level": {
                        "type": "string",
                        "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        "default": "INFO",
                        "description": "Logging level",
                    },
                    "file": {
                        "type": "string",
                        "description": "Log file path (optional)",
                    },
                },
                "additionalProperties": False,
            },
            "database": {
                "type": "object",
                "description": "Database configuration",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Database connection URL",
                        "default": "sqlite:///vfab.db",
                    },
                    "pool_size": {
                        "type": "integer",
                        "minimum": 1,
                        "default": 5,
                        "description": "Database connection pool size",
                    },
                },
                "additionalProperties": False,
            },
        }

    def _generate_driver_configs(self, include_deprecated: bool) -> Dict[str, Any]:
        """Generate configuration schemas for all drivers.

        Args:
            include_deprecated: Whether to include deprecated options

        Returns:
            Driver configuration schemas
        """
        driver_configs = {}

        # Group drivers by type
        for driver_type in DriverType:
            type_drivers = self.registry.get_drivers_by_type(driver_type)
            if not type_drivers:
                continue

            # Create type-specific configuration
            type_config = {
                "type": "object",
                "description": f"{driver_type.value.title()} driver configuration",
                "properties": {},
                "additionalProperties": False,
            }

            # Add configuration for each driver of this type
            for driver_name in type_drivers:
                driver_info = self.registry.get_driver_info(driver_name)
                if not driver_info:
                    continue

                driver_config = self._generate_single_driver_config(
                    driver_name, driver_info, include_deprecated
                )
                if driver_config:
                    type_config["properties"][driver_name] = driver_config

            if type_config["properties"]:
                driver_configs[driver_type.value] = type_config

        return driver_configs

    def _generate_single_driver_config(
        self, driver_name: str, driver_info: Any, include_deprecated: bool
    ) -> Optional[Dict[str, Any]]:
        """Generate configuration schema for a single driver.

        Args:
            driver_name: Name of the driver
            driver_info: Driver information object
            include_deprecated: Whether to include deprecated options

        Returns:
            Driver configuration schema or None
        """
        try:
            # Get driver class to access its configuration schema
            driver_class = self.registry.get_driver_class(driver_name)
            if not driver_class:
                return None

            # Create base driver configuration
            config = {
                "type": "object",
                "description": f"{driver_info.display_name} configuration",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "default": True,
                        "description": f"Enable {driver_info.display_name} driver",
                    }
                },
                "additionalProperties": False,
            }

            # Add driver-specific configuration from schema
            if hasattr(driver_class, "get_config_schema"):
                driver_schema = driver_class.get_config_schema()
                if driver_schema:
                    # Merge driver schema with base configuration
                    if "properties" in driver_schema:
                        config["properties"].update(driver_schema["properties"])
                    if "required" in driver_schema:
                        config["required"] = driver_schema["required"]

            # Add capability-specific configuration
            if driver_info.capabilities:
                for capability in driver_info.capabilities:
                    if capability.config_schema:
                        cap_config = {
                            "type": "object",
                            "description": f"{capability.name} configuration",
                            "properties": capability.config_schema.get(
                                "properties", {}
                            ),
                            "additionalProperties": False,
                        }
                        config["properties"][f"cap_{capability.name}"] = cap_config

            return config

        except Exception as e:
            logger.warning(f"Failed to generate config for driver {driver_name}: {e}")
            return None

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate a configuration dictionary against the generated schema.

        Args:
            config: Configuration to validate

        Returns:
            List of validation errors (empty if valid)
        """
        try:
            import jsonschema

            schema = self.generate_schema()
            validator = jsonschema.Draft7Validator(schema)

            errors = []
            for error in validator.iter_errors(config):
                error_path = " -> ".join(str(p) for p in error.absolute_path)
                errors.append(f"{error_path}: {error.message}")

            return errors

        except ImportError:
            logger.warning("jsonschema not available, skipping validation")
            return []
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return [f"Validation error: {e}"]

    def get_default_config(self) -> Dict[str, Any]:
        """Generate a default configuration based on available drivers.

        Returns:
            Default configuration dictionary
        """
        schema = self.generate_schema()
        default_config = {}

        def extract_defaults(schema_obj: Dict[str, Any], path: List[str] = []) -> None:
            """Extract default values from schema."""
            if "default" in schema_obj:
                # Set the default value at the current path
                current = default_config
                for key in path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[path[-1]] = schema_obj["default"]

            if "properties" in schema_obj:
                for prop_name, prop_schema in schema_obj["properties"].items():
                    extract_defaults(prop_schema, path + [prop_name])

        # Extract defaults from the main schema
        extract_defaults(schema)

        # Add basic driver defaults
        driver_names = self.registry.get_driver_names()
        if driver_names:
            default_config["drivers"] = {}
            for driver_name in driver_names:
                driver_info = self.registry.get_driver_info(driver_name)
                if driver_info:
                    driver_type = driver_info.driver_type.value
                    if driver_type not in default_config["drivers"]:
                        default_config["drivers"][driver_type] = {}
                    default_config["drivers"][driver_type][driver_name] = {
                        "enabled": True
                    }

        return default_config

    def save_schema(
        self, output_path: Union[str, Path], include_deprecated: bool = False
    ) -> None:
        """Save the generated schema to a file.

        Args:
            output_path: Path where to save the schema
            include_deprecated: Whether to include deprecated options
        """
        schema = self.generate_schema(include_deprecated)
        output_path = Path(output_path)

        with open(output_path, "w") as f:
            json.dump(schema, f, indent=2)

        logger.info(f"Configuration schema saved to {output_path}")

    def save_default_config(self, output_path: Union[str, Path]) -> None:
        """Save a default configuration file.

        Args:
            output_path: Path where to save the configuration
        """
        config = self.get_default_config()
        output_path = Path(output_path)

        with open(output_path, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Default configuration saved to {output_path}")


def generate_config_schema(include_deprecated: bool = False) -> Dict[str, Any]:
    """Generate a configuration schema for all available drivers.

    Args:
        include_deprecated: Whether to include deprecated options

    Returns:
        Configuration schema
    """
    generator = DynamicConfigSchema()
    return generator.generate_schema(include_deprecated)


def validate_configuration(config: Dict[str, Any]) -> List[str]:
    """Validate a configuration dictionary.

    Args:
        config: Configuration to validate

    Returns:
        List of validation errors
    """
    generator = DynamicConfigSchema()
    return generator.validate_config(config)


def get_default_configuration() -> Dict[str, Any]:
    """Get a default configuration for available drivers.

    Returns:
        Default configuration dictionary
    """
    generator = DynamicConfigSchema()
    return generator.get_default_config()
