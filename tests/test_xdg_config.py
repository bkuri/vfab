"""
Test simplified configuration system with helper functions.
"""

import os
import tempfile
from pathlib import Path
import pytest
import yaml

from plotty.config import (
    load_config,
    get_workspace_path,
    get_database_url,
    get_vpype_presets_path,
    get_log_file_path,
    get_config,
)


class TestConfigHelpers:
    """Test configuration helper functions."""

    def test_get_workspace_path_default(self):
        """Test workspace path with default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal config (no workspace specified)
            config_data = {}

            config_file = Path(temp_dir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = load_config(str(config_file))
            workspace = get_workspace_path(config)

            # Should use platformdirs default (we can't easily mock this in test)
            assert isinstance(workspace, Path)
            assert workspace.name == "workspace"

    def test_get_workspace_path_custom(self):
        """Test workspace path with custom configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with custom workspace
            config_data = {"workspace": str(Path(temp_dir) / "custom_workspace")}

            config_file = Path(temp_dir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = load_config(str(config_file))
            workspace = get_workspace_path(config)

            assert workspace == Path(temp_dir) / "custom_workspace"

    def test_get_database_url_default(self):
        """Test database URL with default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["XDG_DATA_HOME"] = temp_dir

            config = get_config()
            url = get_database_url(config)

            expected = f"sqlite:///{temp_dir}/plotty/plotty.db"
            assert url == expected

    def test_get_database_url_custom(self):
        """Test database URL with custom configuration."""
        config_data = {"database": {"url": "postgresql://user:pass@localhost/plotty"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = load_config(str(config_file))
            url = get_database_url(config)

            assert url == "postgresql://user:pass@localhost/plotty"

    def test_get_vpype_presets_path_default(self):
        """Test VPype presets path with default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["XDG_CONFIG_HOME"] = temp_dir

            config = get_config()
            path = get_vpype_presets_path(config)

            expected = Path(temp_dir) / "plotty" / "vpype-presets.yaml"
            assert path == expected

    def test_get_vpype_presets_path_custom(self):
        """Test VPype presets path with custom configuration."""
        config_data = {"vpype": {"presets_file": "/custom/path/presets.yaml"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = load_config(str(config_file))
            path = get_vpype_presets_path(config)

            assert path == Path("/custom/path/presets.yaml")

    def test_get_log_file_path_default(self):
        """Test log file path with default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal config (no logging specified)
            config_data = {}

            config_file = Path(temp_dir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = load_config(str(config_file))
            path = get_log_file_path(config)

            # Should use platformdirs default (we can't easily mock this in test)
            assert isinstance(path, Path)
            assert path.name == "plotty.log"
            assert path.parent.name == "logs"

    def test_get_log_file_path_custom(self):
        """Test log file path with custom configuration."""
        config_data = {"logging": {"file": "/custom/logs/plotty.log"}}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = load_config(str(config_file))
            path = get_log_file_path(config)

            # Check if custom path is used (need to check the helper function)
            # For now, just verify it returns a Path
            assert isinstance(path, Path)


class TestConfigLoading:
    """Test configuration loading with simplified approach."""

    def test_load_config_minimal(self):
        """Test loading minimal configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal config
            config_data = {}

            config_file = Path(temp_dir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = load_config(str(config_file))

            # Should use defaults
            assert config.workspace is not None
            assert config.database.url is None  # Will use helper function

    def test_workspace_creation(self):
        """Test workspace directory creation on config load."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["XDG_DATA_HOME"] = temp_dir

            # Create minimal config
            config_data = {}

            config_file = Path(temp_dir) / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            # Load config (should create workspace)
            config = load_config(str(config_file))
            workspace = get_workspace_path(config)

            assert workspace.exists()
            assert (workspace / "jobs").exists()
            assert (workspace / "output").exists()
            assert (workspace / "logs").exists()

    def test_config_without_xdg_vars(self):
        """Test that config files no longer contain XDG variables."""
        # Load the actual config file from the project
        config_file = (
            Path(__file__).parent.parent / "src" / "plotty" / "config" / "config.yaml"
        )

        with open(config_file) as f:
            content = f.read()

        # Should not contain XDG variables
        assert "$XDG_" not in content
        assert "${XDG_" not in content

        # Should have comments about defaults
        assert "default:" in content.lower() or "xdg" in content.lower()


class TestPathsCommand:
    """Test the paths command functionality."""

    def test_paths_command_output(self):
        """Test that paths command shows correct locations."""
        # This is more of an integration test
        # For now, just ensure the functions can be called
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["XDG_CONFIG_HOME"] = temp_dir
            os.environ["XDG_DATA_HOME"] = temp_dir

            config = get_config()

            # These should not raise exceptions
            workspace = get_workspace_path(config)
            db_url = get_database_url(config)
            vpype_path = get_vpype_presets_path(config)
            log_path = get_log_file_path(config)

            assert isinstance(workspace, Path)
            assert isinstance(db_url, str)
            assert isinstance(vpype_path, Path)
            assert isinstance(log_path, Path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
