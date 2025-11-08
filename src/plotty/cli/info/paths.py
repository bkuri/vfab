"""
Show ploTTY file paths and configuration locations.
"""

from __future__ import annotations

from pathlib import Path

from ...config import (
    get_config,
    get_workspace_path,
    get_database_url,
    get_vpype_presets_path,
    get_log_file_path,
)


def get_default_config_path() -> Path:
    """Get the default config file path."""
    import platformdirs

    return Path(platformdirs.user_config_dir("plotty")) / "config.yaml"


def paths_command() -> None:
    """Show actual file locations used by ploTTY."""
    use_rich = False
    console = None

    try:
        from rich.console import Console

        console = Console()
        use_rich = True
    except ImportError:
        use_rich = False

    config = get_config()

    # Get actual paths
    config_file = get_default_config_path()
    workspace_path = get_workspace_path(config)
    database_url = get_database_url(config)
    vpype_presets = get_vpype_presets_path(config)
    log_file = get_log_file_path(config)

    if use_rich and console:
        console.print("📁 ploTTY File Locations", style="bold blue")
        console.print()
        console.print("🔧 Configuration:", style="bold")
        console.print(f"  Config file: {config_file}")
        console.print(f"  VPype presets: {vpype_presets}")
        console.print()
        console.print("💾 Data Storage:", style="bold")
        console.print(f"  Workspace: {workspace_path}")
        console.print(f"  Database: {database_url}")
        console.print(f"  Log file: {log_file}")
        console.print()
        console.print("📂 Workspace Subdirectories:", style="bold")
        console.print(f"  Jobs: {workspace_path / 'jobs'}")
        console.print(f"  Output: {workspace_path / 'output'}")
        console.print(f"  Logs: {workspace_path / 'logs'}")
        console.print()
        console.print("💡 Tips:", style="bold cyan")
        console.print(
            "  • Set PLOTTY_CONFIG environment variable to use custom config file"
        )
        console.print(
            "  • Set workspace in config.yaml to use custom workspace location"
        )
        console.print("  • Set database.url in config.yaml to use custom database")
    else:
        print("📁 ploTTY File Locations")
        print()
        print("🔧 Configuration:")
        print(f"  Config file: {config_file}")
        print(f"  VPype presets: {vpype_presets}")
        print()
        print("💾 Data Storage:")
        print(f"  Workspace: {workspace_path}")
        print(f"  Database: {database_url}")
        print(f"  Log file: {log_file}")
        print()
        print("📂 Workspace Subdirectories:")
        print(f"  Jobs: {workspace_path / 'jobs'}")
        print(f"  Output: {workspace_path / 'output'}")
        print(f"  Logs: {workspace_path / 'logs'}")
        print()
        print("💡 Tips:")
        print("  • Set PLOTTY_CONFIG environment variable to use custom config file")
        print("  • Set workspace in config.yaml to use custom workspace location")
        print("  • Set database.url in config.yaml to use custom database")
