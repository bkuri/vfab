# vfab v0.9.0 Complete API Documentation

## Overview

This is the comprehensive API documentation for vfab v0.9.0, covering all stable public APIs for v1.0.0 compatibility.

## Table of Contents

- [Configuration API](#configuration-api-reference)
- [Database Models](#database-models-api-reference)
- [Finite State Machine](#finite-state-machine-api-reference)
- [Utility Functions](#utility-functions-api-reference)
- [Integration Examples](#integration-examples)

---

# Configuration API Reference

## Overview

vfab uses a hierarchical configuration system based on Pydantic models. All configuration is stored in YAML format and validated at runtime.

## Configuration Classes

### CameraCfg

Configuration class for camera settings.

```python
from vfab.config import CameraCfg

# Access configuration
config = get_config()
setting = config.cameracfg
```

### DatabaseCfg

Configuration class for database settings.

```python
from vfab.config import DatabaseCfg

# Access configuration
config = get_config()
setting = config.databasecfg
```

### DeviceCfg

Configuration class for device settings.

```python
from vfab.config import DeviceCfg

# Access configuration
config = get_config()
setting = config.devicecfg
```

### OptimizationLevelCfg

Configuration class for optimizationlevel settings.

```python
from vfab.config import OptimizationLevelCfg

# Access configuration
config = get_config()
setting = config.optimizationlevelcfg
```

### DigestLevelCfg

Configuration class for digestlevel settings.

```python
from vfab.config import DigestLevelCfg

# Access configuration
config = get_config()
setting = config.digestlevelcfg
```

### FileTypeCfg

Configuration class for filetype settings.

```python
from vfab.config import FileTypeCfg

# Access configuration
config = get_config()
setting = config.filetypecfg
```

### OptimizationCfg

Configuration class for optimization settings.

```python
from vfab.config import OptimizationCfg

# Access configuration
config = get_config()
setting = config.optimizationcfg
```

### VpypeCfg

Configuration class for vpype settings.

```python
from vfab.config import VpypeCfg

# Access configuration
config = get_config()
setting = config.vpypecfg
```

### PaperCfg

Configuration class for paper settings.

```python
from vfab.config import PaperCfg

# Access configuration
config = get_config()
setting = config.papercfg
```

### HooksCfg

Configuration class for hooks settings.

```python
from vfab.config import HooksCfg

# Access configuration
config = get_config()
setting = config.hookscfg
```

### RecoveryCfg

Configuration class for recovery settings.

```python
from vfab.config import RecoveryCfg

# Access configuration
config = get_config()
setting = config.recoverycfg
```

### PhysicalSetupCfg

Configuration class for physicalsetup settings.

```python
from vfab.config import PhysicalSetupCfg

# Access configuration
config = get_config()
setting = config.physicalsetupcfg
```

### LoggingSettings

Configuration class for loggingsettings settings.

```python
from vfab.config import LoggingSettings

# Access configuration
config = get_config()
setting = config.loggingsettings
```

### Settings

Configuration class for settings settings.

```python
from vfab.config import Settings

# Access configuration
config = get_config()
setting = config.settings
```


---

# Database Models API Reference

## Overview

vfab uses SQLAlchemy models for database persistence. All models are defined in `vfab.models` and support full SQLAlchemy operations.

## Model Classes

### Device

Plotter device configuration and status.

```python
from vfab.models import Device

# Query model
with get_session() as session:
    items = session.query(Device).all()
```

### Pen

Pen tool configuration and settings.

```python
from vfab.models import Pen

# Query model
with get_session() as session:
    items = session.query(Pen).all()
```

### Paper

Paper size and margin definitions.

```python
from vfab.models import Paper

# Query model
with get_session() as session:
    items = session.query(Paper).all()
```

### Job

Plotting job metadata and state.

```python
from vfab.models import Job

# Query model
with get_session() as session:
    items = session.query(Job).all()
```

### Layer

Multi-pen layer configuration.

```python
from vfab.models import Layer

# Query model
with get_session() as session:
    items = session.query(Layer).all()
```

### StatisticsConfig

Statistics collection settings.

```python
from vfab.models import StatisticsConfig

# Query model
with get_session() as session:
    items = session.query(StatisticsConfig).all()
```

### JobStatistics

Job execution statistics.

```python
from vfab.models import JobStatistics

# Query model
with get_session() as session:
    items = session.query(JobStatistics).all()
```

### LayerStatistics

Layer-specific statistics.

```python
from vfab.models import LayerStatistics

# Query model
with get_session() as session:
    items = session.query(LayerStatistics).all()
```

### SystemStatistics

System-wide statistics.

```python
from vfab.models import SystemStatistics

# Query model
with get_session() as session:
    items = session.query(SystemStatistics).all()
```

### PerformanceMetrics

Performance measurement data.

```python
from vfab.models import PerformanceMetrics

# Query model
with get_session() as session:
    items = session.query(PerformanceMetrics).all()
```


---

# Finite State Machine API Reference

## Overview

The vfab FSM (Finite State Machine) manages job lifecycle with well-defined states and transitions. All FSM operations are validated and logged.

## Job States

### NEW

Job created but not yet processed.

### ANALYZED

Job analyzed and validated.

### OPTIMIZED

Job optimized for plotting.

### READY

Job ready for plotting.

### ARMED

Job armed and pre-flight checks passed.

### RUNNING

Job currently plotting.

### COMPLETED

Job successfully completed.

### FAILED

Job failed during execution.

### CANCELLED

Job cancelled by user.

### PAUSED

Job paused during execution.

## FSM Operations

```python
from vfab.fsm import JobFSM, JobState, create_fsm

# Create FSM instance
fsm = create_fsm(job_id="example", workspace=Path("/workspace"))

# Check current state
current = fsm.current_state

# Transition to new state
success = fsm.transition_to(JobState.ANALYZED, reason="Analysis complete")

# Apply optimizations
success = fsm.apply_optimizations(preset="hq", digest=2)

# Queue for plotting
success = fsm.queue_ready_job()

# Arm for execution
success = fsm.arm_job()
```

## Key Methods

- `create_fsm(job_id: str, workspace: Path) -> JobFSM`: Create FSM instance
- `transition_to(state: JobState, reason: str) -> bool`: Transition to new state
- `apply_optimizations(preset: str, digest: int) -> bool`: Apply optimizations
- `queue_ready_job() -> bool`: Queue job for plotting
- `arm_job() -> bool`: Arm job for execution
- `get_job_data() -> dict`: Get job metadata
- `update_job_data(data: dict) -> None`: Update job metadata


---

# Utility Functions API Reference

## Overview

vfab provides various utility functions for common operations, file handling, and system interactions.

## Core Utilities

```python
from vfab.utils import (
    format_duration,
    format_bytes,
    safe_filename,
    create_backup,
    validate_svg_file,
    get_system_info
)

# Format duration in human readable format
duration_str = format_duration(3600)  # "1h 0m"

# Format bytes in human readable format
size_str = format_bytes(1024)  # "1.0 KB"

# Create safe filename
safe = safe_filename("My Design/File")  # "My_Design_File"

# Validate SVG file
is_valid = validate_svg_file("design.svg")

# Get system information
info = get_system_info()
```

## File Operations

- `safe_filename(name: str) -> str`: Create safe filename
- `validate_svg_file(path: Path) -> bool`: Validate SVG file
- `create_backup(path: Path, backup_type: str) -> Path`: Create backup

## Formatting Utilities

- `format_duration(seconds: float) -> str`: Format duration
- `format_bytes(bytes: int) -> str`: Format bytes
- `format_percentage(value: float) -> str`: Format percentage

## System Utilities

- `get_system_info() -> dict`: Get system information
- `check_disk_space(path: Path) -> bool`: Check disk space
- `get_available_memory() -> int`: Get available memory


---

# Integration Examples

## Overview

This section provides practical examples for integrating vfab into various workflows and applications.

## Basic Job Management

```python
from vfab.fsm import create_fsm
from vfab.config import get_config
from pathlib import Path

# Initialize vfab
config = get_config()
workspace = Path(config.workspace)

# Create and manage a job
fsm = create_fsm("my_job", workspace)

# Add SVG file
fsm.update_job_data({
    "src_path": "design.svg",
    "name": "My Design"
})

# Process job
if fsm.transition_to("ANALYZED", "Starting analysis"):
    if fsm.apply_optimizations("hq", 2):
        if fsm.queue_ready_job():
            print("Job ready for plotting")
```

## Custom Guard Implementation

```python
from vfab.guards.base import BaseGuard
from vfab.guards.manager import GuardSystem

class CustomSetupGuard(BaseGuard):
    def check(self, context: dict) -> Tuple[bool, str]:
        if context.get("special_mode"):
            return True, "Special mode OK"
        return False, "Special mode required"
    
    def fix(self, context: dict) -> Tuple[bool, str]:
        context["special_mode"] = True
        return True, "Enabled special mode"

# Register custom guard
guards = GuardSystem(config, workspace)
guards.register_guard("custom_setup", CustomSetupGuard())
```

## Statistics Collection

```python
from vfab.stats import StatisticsService
from vfab.models import JobStatistics

# Create statistics service
stats = StatisticsService()

# Record job event
stats.record_job_event(
    job_id="my_job",
    event_type="started",
    duration_seconds=0.0,
    metadata={"preset": "hq"}
)

# Get job statistics
job_stats = stats.get_job_statistics("my_job")

# Get system statistics
system_stats = stats.get_system_statistics()
```

## Configuration Management

```python
from vfab.config import load_config, save_config, Settings

# Load configuration
config = load_config()

# Modify settings
config.settings.logging_level = "DEBUG"
config.device.speed_pendown = 30

# Save configuration
save_config(config)

# Create custom configuration
custom_settings = Settings(
    logging_level="INFO",
    workspace="/custom/workspace",
    database_url="sqlite:///custom.db"
)
```

## Database Operations

```python
from vfab.db import get_session
from vfab.models import Job, Pen, Paper

# Query jobs
with get_session() as session:
    jobs = session.query(Job).filter(Job.state == "COMPLETED").all()
    
    for job in jobs:
        print(f"Job {job.id}: {job.name}")

# Create new pen
with get_session() as session:
    new_pen = Pen(
        name="Fine Liner",
        width_mm=0.3,
        color_hex="#000000"
    )
    session.add(new_pen)
    session.commit()

# Update paper settings
with get_session() as session:
    paper = session.query(Paper).filter(Paper.name == "A4").first()
    if paper:
        paper.margin_mm = 15
        session.commit()
```

## Error Handling and Recovery

```python
from vfab.recovery import detect_interrupted_jobs, CrashRecovery
from vfab.fsm import JobState

# Detect interrupted jobs
workspace = Path("/workspace")
interrupted = detect_interrupted_jobs(workspace, grace_minutes=5)

# Recover interrupted jobs
recovery = CrashRecovery(workspace)
for job_id in interrupted:
    if recovery.can_resume(job_id):
        success = recovery.resume_job(job_id)
        print(f"Resumed job {job_id}: {success}")

# Handle job failures
try:
    fsm.transition_to(JobState.RUNNING, "Starting plot")
except Exception as e:
    print(f"Job transition failed: {e}")
```



## API Stability Guarantee

For vfab v1.0.0, the following APIs are guaranteed to remain stable:

### ✅ Guaranteed Stable
- All configuration classes and their public attributes
- All database models and their relationships
- FSM states and transition methods
- Core utility functions
- CLI command structure and options

### 🔄 May Evolve
- Internal implementation details
- Advanced configuration options
- Experimental features
- Hook system internals

### ❌ Internal APIs
- Database session management
- Internal FSM implementation
- CLI argument parsing internals
- Logging system internals

## Versioning Policy

vfab follows Semantic Versioning (SemVer):
- **Major (X.0.0)**: Breaking changes to stable APIs
- **Minor (X.Y.0)**: New features, backward compatible
- **Patch (X.Y.Z)**: Bug fixes, backward compatible

## Support

For API questions and support:
- 📖 [Documentation](https://vfab.ai/docs)
- 🐛 [Issue Tracker](https://github.com/your-repo/vfab/issues)
- 💬 [Discussions](https://github.com/your-repo/vfab/discussions)

