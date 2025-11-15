"""
Initialization utilities for vfab configuration and workspace setup.

This module handles first-time setup, config file installation, and
XDG-compliant directory creation.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
import platformdirs


def get_xdg_config_dir() -> Path:
    """Get XDG config directory for vfab."""
    return Path(platformdirs.user_config_dir("vfab"))


def get_xdg_data_dir() -> Path:
    """Get XDG data directory for vfab."""
    return Path(platformdirs.user_data_dir("vfab"))


def install_default_config(force: bool = False) -> bool:
    """
    Install default configuration files to XDG config directory.

    Args:
        force: Whether to overwrite existing config files

    Returns:
        True if installation was successful, False otherwise
    """
    try:
        config_dir = get_xdg_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)

        # Try multiple source locations for config files
        source_locations = []

        # 1. Package-relative path (for installed package)
        try:
            import importlib

            vfab_module = importlib.import_module("vfab")

            if vfab_module.__file__:
                package_dir = Path(vfab_module.__file__).parent
                source_locations.append(package_dir / "config")
        except (ImportError, AttributeError):
            pass

        # 2. Local development path
        source_locations.append(Path("src/vfab/config"))
        source_locations.append(Path("config"))

        # Find valid source directory
        config_source_dir = None
        for location in source_locations:
            if location.exists() and (location / "config.yaml").exists():
                config_source_dir = location
                break

        if not config_source_dir:
            return False

        # Install main config file
        config_target = config_dir / "config.yaml"
        if not config_target.exists() or force:
            config_source = config_source_dir / "config.yaml"
            shutil.copy2(config_source, config_target)

        # Install vpype presets file
        vpype_target = config_dir / "vpype-presets.yaml"
        if not vpype_target.exists() or force:
            vpype_source = config_source_dir / "vpype-presets.yaml"
            if vpype_source.exists():
                shutil.copy2(vpype_source, vpype_target)

        return True

    except Exception:
        return False


def ensure_workspace_structure() -> bool:
    """
    Ensure workspace directory structure exists.

    Returns:
        True if workspace structure was created/verified, False otherwise
    """
    try:
        from .config import load_config

        cfg = load_config()
        workspace = Path(cfg.workspace)

        # Create workspace and subdirectories
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "jobs").mkdir(exist_ok=True)
        (workspace / "output").mkdir(exist_ok=True)
        (workspace / "logs").mkdir(exist_ok=True)

        return True

    except Exception:
        return False


def is_first_run() -> bool:
    """
    Check if this is the first time vfab is run.

    Returns:
        True if this appears to be first run, False otherwise
    """
    config_dir = get_xdg_config_dir()
    config_file = config_dir / "config.yaml"

    return not config_file.exists()


def initialize_vfab(force_config: bool = False) -> bool:
    """
    Initialize vfab configuration and workspace.

    Args:
        force_config: Whether to overwrite existing config files

    Returns:
        True if initialization was successful, False otherwise
    """
    success = True

    # Install default configuration
    if not install_default_config(force=force_config):
        success = False

    # Ensure workspace structure
    if not ensure_workspace_structure():
        success = False

    return success


def get_default_config_path() -> Path:
    """Get the default config file path in XDG config directory."""
    return get_xdg_config_dir() / "config.yaml"


def get_user_config_path() -> Path:
    """Get the user config file path, respecting VFAB_CONFIG env var."""
    if "VFAB_CONFIG" in os.environ:
        return Path(os.environ["VFAB_CONFIG"])
    return get_default_config_path()
