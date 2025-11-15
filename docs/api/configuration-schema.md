# Configuration Schema

vfab uses a comprehensive configuration system built with Pydantic for validation and YAML for human-readable configuration files. The configuration is defined in `src/vfab/config.py`.

## Configuration Structure

The main configuration is represented by the `Settings` class, which contains all configuration sections:

```python
class Settings(BaseModel):
    workspace: str = str(Path(platformdirs.user_data_dir("vfab")) / "workspace")
    camera: CameraCfg = Field(default_factory=CameraCfg)
    database: DatabaseCfg = Field(default_factory=DatabaseCfg)
    device: DeviceCfg = Field(default_factory=DeviceCfg)
    vpype: VpypeCfg = Field(default_factory=VpypeCfg)
    optimization: OptimizationCfg = Field(default_factory=OptimizationCfg)
    paper: PaperCfg = Field(default_factory=PaperCfg)
    hooks: HooksCfg = Field(default_factory=HooksCfg)
    recovery: RecoveryCfg = Field(default_factory=RecoveryCfg)
    physical_setup: PhysicalSetupCfg = Field(default_factory=PhysicalSetupCfg)
    websocket: WebSocketCfg = Field(default_factory=WebSocketCfg)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
```

## Configuration Sections

### 1. Camera Configuration (`CameraCfg`)

Camera settings for monitoring and timelapse functionality.

```python
class CameraCfg(BaseModel):
    mode: str = "ip"                              # Camera mode: "ip" or "device"
    url: str | None = "http://127.0.0.1:8881/stream.mjpeg"  # IP camera URL
    device: str | None = None                     # Device camera path
    enabled: bool = True                           # Enable camera
    timelapse_fps: int = 1                         # Timelapse frames per second
    test_access: bool = True                       # Test camera access on startup
    motion_service: str = "motion"                 # Motion service name
```

**YAML Example:**
```yaml
camera:
  mode: "ip"
  url: "http://192.168.1.100:8080/stream.mjpeg"
  enabled: true
  timelapse_fps: 2
  test_access: true
```

### 2. Database Configuration (`DatabaseCfg`)

Database connection settings.

```python
class DatabaseCfg(BaseModel):
    url: str = f"sqlite:///{Path(platformdirs.user_data_dir('vfab')) / 'vfab.db'}"
    echo: bool = False
```

**YAML Examples:**

SQLite (default):
```yaml
database:
  url: "sqlite:///path/to/vfab.db"
  echo: false
```

PostgreSQL:
```yaml
database:
  url: "postgresql://user:password@localhost/vfab"
  echo: false
```

### 3. Device Configuration (`DeviceCfg`)

Plotter device settings.

```python
class DeviceCfg(BaseModel):
    preferred: str = "axidraw:auto"               # Preferred device type
    pause_ink_swatch: bool = True                  # Pause for ink swatch
    port: str | None = None                        # Device port
    model: int = 1                                 # Device model number
    pen_pos_up: int = 60                           # Pen up position
    pen_pos_down: int = 40                         # Pen down position
    speed_pendown: int = 25                        # Pen down speed
    speed_penup: int = 75                          # Pen up speed
    units: str = "inches"                          # Units: "inches" or "mm"
    penlift: int = 1                               # Pen lift type (1-3)
    remote_detection_host: str | None = None        # Remote detection host
    detection_timeout: int = 5                     # Device detection timeout
```

**YAML Example:**
```yaml
device:
  preferred: "axidraw:auto"
  port: "/dev/ttyUSB0"
  model: 2
  pen_pos_up: 65
  pen_pos_down: 35
  speed_pendown: 30
  speed_penup: 80
  units: "mm"
  penlift: 2
  detection_timeout: 10
```

### 4. VPype Configuration (`VpypeCfg`)

VPype plotting engine settings.

```python
class VpypeCfg(BaseModel):
    preset: str = "fast"                           # Default VPype preset
    presets_file: str = str(Path("config/vpype-presets.yaml"))  # Presets file path
```

**YAML Example:**
```yaml
vpype:
  preset: "default"
  presets_file: "config/custom-vpype-presets.yaml"
```

### 5. Optimization Configuration (`OptimizationCfg`)

File optimization settings and presets.

```python
class OptimizationLevelCfg(BaseModel):
    description: str                               # Level description
    vpype_preset: str                              # VPype preset to use
    digest_default: int                            # Default digest level

class DigestLevelCfg(BaseModel):
    description: str                               # Digest level description
    enabled: bool                                  # Whether digest is enabled
    compression: str = "standard"                  # Compression type

class FileTypeCfg(BaseModel):
    mode: str                                      # File processing mode
    auto_pristine: bool = False                    # Auto-pristine mode
    skip_optimization: bool = False                # Skip optimization

class OptimizationCfg(BaseModel):
    levels: dict[str, OptimizationLevelCfg]         # Optimization levels
    digest_levels: dict[int, DigestLevelCfg]       # Digest levels
    file_types: dict[str, FileTypeCfg]             # File type configurations
    default_level: str = "default"                  # Default optimization level
    default_digest: int = 1                        # Default digest level
```

**Default Optimization Levels:**
- `fast`: Fast optimization for quick plotting
- `default`: Standard optimization balanced for speed and quality
- `hq`: High quality optimization for best results

**Default Digest Levels:**
- `0`: No digest generation (slower plotting)
- `1`: Standard digest for AxiDraw acceleration
- `2`: High compression digest for maximum speed

**YAML Example:**
```yaml
optimization:
  default_level: "hq"
  default_digest: 2
  levels:
    ultra_fast:
      description: "Ultra-fast optimization for testing"
      vpype_preset: "ultra_fast"
      digest_default: 2
  file_types:
    ".svg":
      mode: "normal"
      auto_pristine: false
      skip_optimization: false
    ".plob":
      mode: "plob"
      auto_pristine: true
      skip_optimization: true
```

### 6. Paper Configuration (`PaperCfg`)

Paper handling settings.

```python
class PaperCfg(BaseModel):
    default_size: str = "A4"                       # Default paper size
    default_margin_mm: float = 10.0               # Default margin in mm
    default_orientation: str = "portrait"           # Default orientation
    require_one_per_session: bool = True           # Require paper selection per session
    track_usage: bool = True                       # Track paper usage statistics
```

**YAML Example:**
```yaml
paper:
  default_size: "A3"
  default_margin_mm: 15.0
  default_orientation: "landscape"
  require_one_per_session: false
  track_usage: true
```

### 7. Hooks Configuration (`HooksCfg`)

Event hook configuration for custom automation.

```python
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
```

**YAML Example:**
```yaml
hooks:
  NEW:
    - command: "notify-send 'New job added: {job_name}'"
      type: "system"
  COMPLETED:
    - command: "python scripts/post_process.py {job_id}"
      type: "script"
    - command: "curl -X POST https://api.example.com/webhook -d '{job_data}'"
      type: "webhook"
```

### 8. Recovery Configuration (`RecoveryCfg`)

Job recovery and interruption handling settings.

```python
class RecoveryCfg(BaseModel):
    interrupt_grace_minutes: int = 5               # Grace period for interrupted jobs
    auto_detect_enabled: bool = True              # Auto-detect interrupted jobs
    max_resume_attempts: int = 3                   # Maximum resume attempts
```

**YAML Example:**
```yaml
recovery:
  interrupt_grace_minutes: 10
  auto_detect_enabled: true
  max_resume_attempts: 5
```

### 9. Physical Setup Configuration (`PhysicalSetupCfg`)

Physical setup validation and guidance settings.

```python
class PhysicalSetupCfg(BaseModel):
    require_confirmation: bool = True              # Require confirmation before plotting
    show_guidance: bool = True                     # Show setup guidance
    auto_detect_paper: bool = False                 # Auto-detect paper size
    auto_detect_pen: bool = False                  # Auto-detect pen configuration
    paper_alignment_tolerance: float = 2.0         # Paper alignment tolerance in mm
    pen_force_check: bool = True                   # Check pen force
    device_connection_check: bool = True           # Check device connection
    skip_on_resume: bool = False                    # Skip checks on resume
    timeout_seconds: int = 30                      # Setup timeout in seconds
```

**YAML Example:**
```yaml
physical_setup:
  require_confirmation: false
  show_guidance: true
  auto_detect_paper: true
  paper_alignment_tolerance: 1.5
  timeout_seconds: 60
```

### 10. WebSocket Configuration (`WebSocketCfg`)

Real-time monitoring and WebSocket server settings.

```python
class WebSocketCfg(BaseModel):
    enabled: bool = True                           # Enable WebSocket server
    host: str = "localhost"                        # Server bind address
    port: int = 8766                               # Server port
    authenticate: bool = False                        # Require API key authentication
    api_key: str | None = None                       # API key for authentication
    max_connections: int = 100                       # Maximum concurrent connections
    heartbeat_interval: int = 30                      # Heartbeat interval (seconds)
    channels: List[str] = ["jobs", "system", "device"]  # Available channels
    allowed_origins: List[str] = ["*"]              # CORS allowed origins
    message_rate_limit: int = 100                     # Messages per minute per client
    connection_timeout: int = 300                      # Connection timeout (seconds)
    compression: bool = True                           # Enable message compression
```

**YAML Example:**
```yaml
websocket:
  enabled: true
  host: "localhost"
  port: 8766
  authenticate: false
  api_key: null
  max_connections: 100
  heartbeat_interval: 30
  channels:
    - "jobs"
    - "system"
    - "device"
  allowed_origins:
    - "*"
  message_rate_limit: 100
  connection_timeout: 300
  compression: true
```

**Production Configuration:**
```yaml
websocket:
  enabled: true
  host: "0.0.0.0"
  port: 8766
  authenticate: true
  api_key: "your-secret-api-key-here"
  max_connections: 50
  heartbeat_interval: 60
  channels:
    - "jobs"
    - "system"
    - "device"
  allowed_origins:
    - "https://your-domain.com"
    - "https://monitor.your-domain.com"
  message_rate_limit: 60
  connection_timeout: 600
  compression: true
```

### 11. Logging Configuration (`LoggingSettings`)

Comprehensive logging settings.

```python
class LoggingSettings(BaseModel):
    enabled: bool = True                            # Enable logging
    level: str = "INFO"                            # Log level
    format: str = "rich"                           # Log format
    output: str = "both"                           # Output destination
    log_file: str = str(Path(platformdirs.user_data_dir("vfab")) / "logs" / "vfab.log")
    max_file_size: int = 10485760                  # Max file size (10MB)
    backup_count: int = 5                          # Number of backup files
    console_show_timestamp: bool = False           # Show timestamp in console
    console_show_level: bool = True                 # Show log level in console
    console_rich_tracebacks: bool = True            # Use rich tracebacks
    include_job_id: bool = True                    # Include job ID in logs
    include_device_info: bool = True               # Include device info in logs
    include_session_id: bool = True                # Include session ID in logs
    buffer_size: int = 1024                        # Log buffer size
    flush_interval: int = 5                        # Flush interval in seconds
```

**YAML Example:**
```yaml
logging:
  enabled: true
  level: "DEBUG"
  format: "rich"
  output: "both"
  log_file: "/var/log/vfab/vfab.log"
  max_file_size: 20971520  # 20MB
  backup_count: 10
  console_show_timestamp: true
  include_job_id: true
  include_device_info: true
  include_session_id: true
```

## Configuration Management

### Loading Configuration

```python
from vfab.config import load_config, get_config

# Load from default location
config = load_config()

# Load from specific file
config = load_config("/path/to/config.yaml")

# Get current configuration instance
config = get_config()
```

### Saving Configuration

```python
from vfab.config import load_config, save_config

# Load, modify, and save
config = load_config()
config.device.speed_pendown = 30
save_config(config, "/path/to/new_config.yaml")
```

### Environment Variables

- `PLOTTY_CONFIG`: Path to configuration file (overrides default)

### Configuration Precedence

1. Command-line options (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

## Complete Configuration Example

```yaml
# config/config.yaml
workspace: "/home/user/vfab-workspace"

camera:
  mode: "ip"
  url: "http://192.168.1.100:8080/stream.mjpeg"
  enabled: true
  timelapse_fps: 2
  test_access: true

database:
  url: "postgresql://vfab:password@localhost/vfab"
  echo: false

device:
  preferred: "axidraw:auto"
  port: "/dev/ttyUSB0"
  model: 2
  pen_pos_up: 65
  pen_pos_down: 35
  speed_pendown: 30
  speed_penup: 80
  units: "mm"
  penlift: 2
  detection_timeout: 10

vpype:
  preset: "default"
  presets_file: "config/vpype-presets.yaml"

optimization:
  default_level: "hq"
  default_digest: 2
  levels:
    ultra_fast:
      description: "Ultra-fast optimization for testing"
      vpype_preset: "ultra_fast"
      digest_default: 2

paper:
  default_size: "A3"
  default_margin_mm: 15.0
  default_orientation: "landscape"
  require_one_per_session: false
  track_usage: true

hooks:
  NEW:
    - command: "notify-send 'New job added: {job_name}'"
      type: "system"
  COMPLETED:
    - command: "python scripts/post_process.py {job_id}"
      type: "script"

recovery:
  interrupt_grace_minutes: 10
  auto_detect_enabled: true
  max_resume_attempts: 5

physical_setup:
  require_confirmation: false
  show_guidance: true
  auto_detect_paper: true
  paper_alignment_tolerance: 1.5
  timeout_seconds: 60

logging:
  enabled: true
  level: "DEBUG"
  format: "rich"
  output: "both"
  log_file: "/var/log/vfab/vfab.log"
  max_file_size: 20971520
  backup_count: 10
  console_show_timestamp: true
  include_job_id: true
  include_device_info: true
  include_session_id: true
```

## Configuration Validation

The configuration system uses Pydantic for automatic validation:

```python
from vfab.config import Settings
from pydantic import ValidationError

try:
    config = Settings(**config_dict)
except ValidationError as e:
    print(f"Configuration error: {e}")
```

Common validation errors:
- Invalid log levels
- Out-of-range numeric values
- Invalid file paths
- Missing required fields

## Dynamic Configuration Updates

Some configuration sections support runtime updates:

```python
from vfab.config import get_config

config = get_config()

# Update device settings (may require device reconnection)
config.device.speed_pendown = 25

# Update logging settings (takes effect immediately)
config.logging.level = "DEBUG"
```

## Configuration Templates

vfab provides configuration templates for different use cases:

### Development Template
```yaml
# config/development.yaml
database:
  echo: true
logging:
  level: "DEBUG"
  console_show_timestamp: true
```

### Production Template
```yaml
# config/production.yaml
database:
  url: "postgresql://vfab:password@db.example.com/vfab"
logging:
  level: "INFO"
  output: "file"
  log_file: "/var/log/vfab/vfab.log"
```

### Testing Template
```yaml
# config/testing.yaml
workspace: "/tmp/vfab-test"
database:
  url: "sqlite:///test.db"
logging:
  level: "WARNING"
  enabled: false
```