from **future** import annotations
from pydantic import BaseModel, Field
from pathlib import Path
import os, yaml

class CameraCfg(BaseModel):
mode: str = "ip"
url: str | None = "[http://127.0.0.1:8881/stream.mjpeg](http://127.0.0.1:8881/stream.mjpeg)"
device: str | None = None
enabled: bool = True
timelapse_fps: int = 1

class DatabaseCfg(BaseModel):
url: str = "sqlite:///./plotty.db"
echo: bool = False

class DeviceCfg(BaseModel):
preferred: str = "axidraw:auto"
pause_ink_swatch: bool = True

class VpypeCfg(BaseModel):
preset: str = "multipen-fast"
presets_file: str = str(Path("config/vpype-presets.yaml"))

class Settings(BaseModel):
workspace: str = str(Path("./workspace").absolute())
camera: CameraCfg = Field(default_factory=CameraCfg)
database: DatabaseCfg = Field(default_factory=DatabaseCfg)
device: DeviceCfg = Field(default_factory=DeviceCfg)
vpype: VpypeCfg = Field(default_factory=VpypeCfg)

def load_config(path: str | None = None) -> Settings:
p = Path(path or os.environ.get("PLOTTY_CONFIG", "config/config.yaml"))
data = yaml.safe_load(p.read_text()) if p.exists() else {}
return Settings(**(data or {}))
