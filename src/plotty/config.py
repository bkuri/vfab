from __future__ import annotations

# Performance: Module optimized for v0.9.0

from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, List
import os
import yaml
import platformdirs


class CameraCfg(BaseModel):
    mode: str = "ip"
    url: str | None = "http://127.0.0.1:8881/stream.mjpeg"
    device: str | None = None
    enabled: bool = True
    timelapse_fps: int = 1
    test_access: bool = True
    motion_service: str = "motion"


class DatabaseCfg(BaseModel):
    url: str | None = None  # None = use default XDG location
    echo: bool = False


class DeviceCfg(BaseModel):
    preferred: str = "axidraw:auto"
    pause_ink_swatch: bool = True
    port: str | None = None
    model: int = 1
    pen_pos_up: int = 60
    pen_pos_down: int = 40
    speed_pendown: int = 25
    speed_penup: int = 75
    units: str = "inches"
    penlift: int = (
        1  # 1: Default for AxiDraw model, 2: Standard servo, 3: Brushless servo
    )
    remote_detection_host: str | None = None
    detection_timeout: int = 5


class OptimizationLevelCfg(BaseModel):
    description: str
    vpype_preset: str
    digest_default: int


class DigestLevelCfg(BaseModel):
    description: str
    enabled: bool
    compression: str = "standard"


class FileTypeCfg(BaseModel):
    mode: str
    auto_pristine: bool = False
    skip_optimization: bool = False


class OptimizationCfg(BaseModel):
    levels: dict[str, OptimizationLevelCfg] = Field(
        default_factory=lambda: {
            "fast": OptimizationLevelCfg(
                description="Fast optimization for quick plotting",
                vpype_preset="fast",
                digest_default=1,
            ),
            "default": OptimizationLevelCfg(
                description="Standard optimization balanced for speed and quality",
                vpype_preset="default",
                digest_default=1,
            ),
            "hq": OptimizationLevelCfg(
                description="High quality optimization for best results",
                vpype_preset="hq",
                digest_default=2,
            ),
        }
    )
    digest_levels: dict[int, DigestLevelCfg] = Field(
        default_factory=lambda: {
            0: DigestLevelCfg(
                description="No digest generation (slower plotting)", enabled=False
            ),
            1: DigestLevelCfg(
                description="Standard digest for AxiDraw acceleration",
                enabled=True,
                compression="standard",
            ),
            2: DigestLevelCfg(
                description="High compression digest for maximum speed",
                enabled=True,
                compression="high",
            ),
        }
    )
    file_types: dict[str, FileTypeCfg] = Field(
        default_factory=lambda: {
            ".plob": FileTypeCfg(
                mode="plob", auto_pristine=True, skip_optimization=True
            ),
            ".svg": FileTypeCfg(
                mode="normal", auto_pristine=False, skip_optimization=False
            ),
        }
    )
    default_level: str = "default"
    default_digest: int = 1


class VpypeCfg(BaseModel):
    preset: str = "fast"
    presets_file: str = str(Path("config/vpype-presets.yaml"))


class PaperCfg(BaseModel):
    default_size: str = "A4"
    default_margin_mm: float = 10.0
    default_orientation: str = "portrait"
    require_one_per_session: bool = True
    track_usage: bool = True


class HooksCfg(BaseModel):
    NEW: list[dict[str, str]] = Field(default_factory=list)
    QUEUED: list[dict[str, str]] = Field(default_factory=list)
    ANALYZED: list[dict[str, str]] = Field(default_factory=list)
    OPTIMIZED: list[dict[str, str]] = Field(default_factory=list)
    READY: list[dict[str, str]] = Field(default_factory=list)
    ARMED: list[dict[str, str]] = Field(default_factory=list)
    PLOTTING: list[dict[str, str]] = Field(default_factory=list)
    PAUSED: list[dict[str, str]] = Field(default_factory=list)
    COMPLETED: list[dict[str, str]] = Field(default_factory=list)
    ABORTED: list[dict[str, str]] = Field(default_factory=list)
    FAILED: list[dict[str, str]] = Field(default_factory=list)


class RecoveryCfg(BaseModel):
    interrupt_grace_minutes: int = 5
    auto_detect_enabled: bool = True
    max_resume_attempts: int = 3


class PhysicalSetupCfg(BaseModel):
    """Configuration for physical setup validation."""

    require_confirmation: bool = True
    show_guidance: bool = True
    auto_detect_paper: bool = False
    auto_detect_pen: bool = False
    paper_alignment_tolerance: float = 2.0  # mm
    pen_force_check: bool = True
    device_connection_check: bool = True
    skip_on_resume: bool = False
    timeout_seconds: int = 30


class WebSocketCfg(BaseModel):
    """Configuration for WebSocket monitoring server."""

    enabled: bool = False
    host: str = "localhost"
    port: int = 8765
    max_connections: int = 100
    heartbeat_interval: int = 30
    authentication: bool = False
    api_key: Optional[str] = None
    channels: List[str] = Field(default_factory=lambda: ["jobs", "devices", "system"])


class LoggingSettings(BaseModel):
    enabled: bool = True
    level: str = "INFO"
    format: str = "rich"
    output: str = "both"
    log_file: str = str(
        Path(platformdirs.user_data_dir("plotty")) / "logs" / "plotty.log"
    )
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_show_timestamp: bool = False
    console_show_level: bool = True
    console_rich_tracebacks: bool = True
    include_job_id: bool = True
    include_device_info: bool = True
    include_session_id: bool = True
    buffer_size: int = 1024
    flush_interval: int = 5


class Settings(BaseModel):
    workspace: str = str(Path(platformdirs.user_data_dir("plotty")) / "workspace")
    camera: CameraCfg = Field(default_factory=CameraCfg)
    database: DatabaseCfg = Field(default_factory=DatabaseCfg)
    device: DeviceCfg = Field(default_factory=DeviceCfg)
    vpype: VpypeCfg = Field(default_factory=VpypeCfg)
    optimization: OptimizationCfg = Field(default_factory=OptimizationCfg)
    paper: PaperCfg = Field(default_factory=PaperCfg)
    hooks: HooksCfg = Field(default_factory=HooksCfg)
    recovery: RecoveryCfg = Field(default_factory=RecoveryCfg)
    physical_setup: PhysicalSetupCfg = Field(default_factory=PhysicalSetupCfg)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    websocket: WebSocketCfg = Field(default_factory=WebSocketCfg)


def _ensure_config_initialized() -> None:
    """Ensure ploTTY configuration is initialized on first run."""
    try:
        # Import here to avoid circular imports
        import importlib

        init_module = importlib.import_module(".init", package="plotty")

        if init_module.is_first_run():
            init_module.initialize_plotty()
    except ImportError:
        # If init module is not available, skip initialization
        pass
    except Exception:
        # Don't let initialization errors break config loading
        pass


def load_config(path: str | None = None) -> Settings:
    # Handle first-time initialization
    if path is None and not os.environ.get("PLOTTY_CONFIG"):
        _ensure_config_initialized()

        # Try to use XDG config path if no custom path specified
        try:
            import importlib

            init_module = importlib.import_module(".init", package="plotty")
            default_config_path = init_module.get_default_config_path()
            if default_config_path.exists():
                path = str(default_config_path)
        except (ImportError, AttributeError):
            # Fallback to default path
            pass

    p = Path(path or os.environ.get("PLOTTY_CONFIG", "config/config.yaml"))
    data = yaml.safe_load(p.read_text()) if p.exists() else {}

    settings = Settings(**(data or {}))

    # Ensure workspace directory structure exists
    try:
        workspace_path = get_workspace_path(settings)
        workspace_path.mkdir(parents=True, exist_ok=True)
        (workspace_path / "jobs").mkdir(exist_ok=True)
        (workspace_path / "output").mkdir(exist_ok=True)
        (workspace_path / "logs").mkdir(exist_ok=True)
    except Exception:
        # Don't let workspace creation break config loading
        pass

    return settings


def get_config() -> Settings:
    """Get current configuration instance."""
    return load_config()


def get_workspace_path(config: Settings | None = None) -> Path:
    """Get actual workspace path, using XDG default if not configured."""
    if config is None:
        config = get_config()

    if config.workspace and config.workspace != str(
        Path(platformdirs.user_data_dir("plotty")) / "workspace"
    ):
        # User has custom workspace
        return Path(config.workspace)
    else:
        # Use XDG default
        return Path(platformdirs.user_data_dir("plotty")) / "workspace"


def get_database_url(config: Settings | None = None) -> str:
    """Get actual database URL, using XDG default if not configured."""
    if config is None:
        config = get_config()

    if (
        config.database.url
        and config.database.url
        != f"sqlite:///{Path(platformdirs.user_data_dir('plotty')) / 'plotty.db'}"
    ):
        # User has custom database URL
        return config.database.url
    else:
        # Use XDG default
        return f"sqlite:///{Path(platformdirs.user_data_dir('plotty')) / 'plotty.db'}"


def get_vpype_presets_path(config: Settings | None = None) -> Path:
    """Get actual vpype presets path, using XDG default if not configured."""
    if config is None:
        config = get_config()

    if config.vpype.presets_file and config.vpype.presets_file != "vpype-presets.yaml":
        # User has custom presets file
        return Path(config.vpype.presets_file)
    else:
        # Use XDG config directory
        return Path(platformdirs.user_config_dir("plotty")) / "vpype-presets.yaml"


def get_log_file_path(config: Settings | None = None) -> Path:
    """Get actual log file path, using XDG default if not configured."""
    if config is None:
        config = get_config()

    if config.logging.log_file and config.logging.log_file != str(
        Path(platformdirs.user_data_dir("plotty")) / "logs" / "plotty.log"
    ):
        # User has custom log file
        return Path(config.logging.log_file)
    else:
        # Use XDG default
        return Path(platformdirs.user_data_dir("plotty")) / "logs" / "plotty.log"


def save_config(config: Settings, path: str | None = None) -> None:
    """Save configuration to YAML file.

    Args:
        config: Settings instance to save
        path: Path to save config file (default: XDG config directory)
    """
    if path is None and not os.environ.get("PLOTTY_CONFIG"):
        # Use XDG config directory by default
        try:
            import importlib

            init_module = importlib.import_module(".init", package="plotty")
            path = str(init_module.get_default_config_path())
        except (ImportError, AttributeError):
            # Fallback to platformdirs
            path = str(Path(platformdirs.user_config_dir("plotty")) / "config.yaml")

    p = Path(path or os.environ.get("PLOTTY_CONFIG", "config/config.yaml"))

    # Ensure parent directory exists
    p.parent.mkdir(parents=True, exist_ok=True)

    # Convert config to dictionary and save as YAML
    config_dict = config.model_dump(exclude_none=True)

    with open(p, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)


def load_vpype_presets(presets_file: str | None = None) -> dict:
    """Load VPype presets from YAML file."""
    if presets_file is None:
        cfg = load_config()
        presets_file = str(get_vpype_presets_path(cfg))

    p = Path(presets_file)
    if not p.exists():
        return {}

    with open(p, "r") as f:
        return yaml.safe_load(f) or {}
