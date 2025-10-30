from __future__ import annotations
from pydantic import BaseModel, Field
from pathlib import Path
import os, yaml


class CameraCfg(BaseModel):
    mode: str = "ip"
    url: str | None = "http://127.0.0.1:8881/stream.mjpeg"
    device: str | None = None
    enabled: bool = True
    timelapse_fps: int = 1


class DatabaseCfg(BaseModel):
    url: str = "sqlite:///./plotty.db"
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


class VpypeCfg(BaseModel):
    preset: str = "multipen-fast"
    presets_file: str = str(Path("config/vpype-presets.yaml"))


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


class Settings(BaseModel):
    workspace: str = str(Path("./workspace").absolute())
    camera: CameraCfg = Field(default_factory=CameraCfg)
    database: DatabaseCfg = Field(default_factory=DatabaseCfg)
    device: DeviceCfg = Field(default_factory=DeviceCfg)
    vpype: VpypeCfg = Field(default_factory=VpypeCfg)
    hooks: HooksCfg = Field(default_factory=HooksCfg)


def load_config(path: str | None = None) -> Settings:
    p = Path(path or os.environ.get("PLOTTY_CONFIG", "config/config.yaml"))
    data = yaml.safe_load(p.read_text()) if p.exists() else {}
    return Settings(**(data or {}))
