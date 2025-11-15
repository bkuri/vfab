# Core Classes and Methods

vfab provides a rich set of core classes for managing plotting operations, job lifecycle, and device interactions. This section documents the main public APIs.

## Finite State Machine (FSM)

### JobFSM

The core class managing job lifecycle and state transitions.

```python
from vfab.fsm import JobFSM, JobState, create_fsm

# Create FSM for a job
fsm = create_fsm(job_id="abc123", workspace=Path("/workspace"))

# Get current state
current_state = fsm.current_state

# Transition to new state
success = fsm.transition_to(JobState.ANALYZED, reason="Starting analysis")

# Apply optimizations
success = fsm.apply_optimizations(preset="hq", digest=2)

# Queue job for plotting
success = fsm.queue_ready_job()
```

**Key Methods:**

#### `create_fsm(job_id: str, workspace: Path) -> JobFSM`
Factory function to create FSM instance.

#### `transition_to(state: JobState, reason: str) -> bool`
Transition job to new state with validation.

#### `apply_optimizations(preset: str, digest: int) -> bool`
Apply optimization settings to job.

#### `queue_ready_job() -> bool`
Queue a ready job for plotting.

#### `arm_job() -> bool`
Perform pre-flight checks and arm job for plotting.

#### `get_job_data() -> dict`
Get current job metadata.

#### `update_job_data(data: dict) -> None`
Update job metadata.

### JobState Enum

Defines all possible job states:

```python
class JobState(Enum):
    NEW = "NEW"
    QUEUED = "QUEUED"
    ANALYZED = "ANALYZED"
    OPTIMIZED = "OPTIMIZED"
    READY = "READY"
    ARMED = "ARMED"
    PLOTTING = "PLOTTING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"
```

## Plotting Classes

### MultiPenPlotter

Handles multi-pen plotting with pen swap management.

```python
from vfab.plotting import MultiPenPlotter

# Create plotter instance
plotter = MultiPenPlotter(
    port="/dev/ttyUSB0",
    model=2,
    interactive=True
)

# Plot with pen management
result = plotter.plot_with_axidraw_layers(svg_path)

# Plot job directory
result = plotter.plot_multipen_job(
    job_dir=Path("/workspace/jobs/abc123"),
    layers=layer_list,
    pen_map=pen_mapping
)
```

**Key Methods:**

#### `__init__(port: Optional[str], model: int, interactive: bool)`
Initialize plotter with device settings.

#### `plot_with_axidraw_layers(svg_path: Path) -> dict`
Plot SVG file with AxiDraw layer control.

#### `plot_multipen_job(job_dir: Path, layers: List[dict], pen_map: dict) -> dict`
Plot multi-pen job with pen swap prompts.

### PenSwapPrompt

Handles user interaction for pen changes.

```python
from vfab.plotting import PenSwapPrompt

prompt = PenSwapPrompt(interactive=True)

# Prompt for pen change
should_continue = prompt.prompt_pen_swap(
    from_pen="0.3mm black",
    to_pen="0.5mm red", 
    layer_name="outline"
)
```

## Planning and Estimation

### plan_layers()

Plan job layers and create plotting strategy.

```python
from vfab.planner import plan_layers

result = plan_layers(
    src_svg=Path("design.svg"),
    preset="default",
    presets_file="config/vpype-presets.yaml",
    pen_map={"layer1": "0.3mm black"},
    out_dir=Path("output"),
    interactive=True,
    paper_size="A4"
)

# Result contains:
# - layer_count: int
# - pen_map: dict
# - estimates: dict
# - layers: list
```

### estimate_seconds()

Estimate plotting time for features.

```python
from vfab.estimation import estimate_seconds, features

# Get feature analysis
feature_data = features(svg_path)

# Estimate time
time_seconds = estimate_seconds(feature_data, speed_factor=1.0)
```

## Database Operations

### get_session()

Get database session for operations.

```python
from vfab.db import get_session
from vfab.models import Job, Pen, Paper

with get_session() as session:
    # Query jobs
    jobs = session.query(Job).filter(Job.state == "QUEUED").all()
    
    # Create new pen
    new_pen = Pen(name="0.7mm blue", width_mm=0.7, color_hex="#0000FF")
    session.add(new_pen)
    session.commit()
    
    # Get job with relationships
    job = session.query(Job).options(
        joinedload(Job.layers).joinedload(Layer.pen)
    ).filter(Job.id == "abc123").first()
```

### Database Models

All models provide standard SQLAlchemy ORM methods:

```python
# Create
pen = Pen(name="0.3mm black", width_mm=0.3, color_hex="#000000")
session.add(pen)
session.commit()

# Read
pens = session.query(Pen).all()
pen = session.query(Pen).filter(Pen.name == "0.3mm black").first()

# Update
pen.width_mm = 0.35
session.commit()

# Delete
session.delete(pen)
session.commit()
```

## Configuration Management

### load_config() / get_config()

Load and access configuration.

```python
from vfab.config import load_config, get_config, save_config

# Load configuration
config = load_config("/path/to/config.yaml")

# Get current configuration
config = get_config()

# Access configuration sections
device_port = config.device.port
workspace_path = config.workspace
log_level = config.logging.level

# Modify and save
config.device.speed_pendown = 30
save_config(config)
```

### load_vpype_presets()

Load VPype presets from file.

```python
from vfab.config import load_vpype_presets

presets = load_vpype_presets("config/vpype-presets.yaml")

# Access preset
fast_preset = presets.get("fast", {})
```

## Device Management

### create_manager()

Create device manager for plotting hardware.

```python
from vfab.drivers import create_manager, is_axidraw_available

if is_axidraw_available():
    manager = create_manager(port="/dev/ttyUSB0", model=2)
    
    # Plot file
    result = manager.plot_file("design.svg")
    
    # Preview only
    result = manager.plot_file("design.svg", preview_only=True)
```

### is_axidraw_available()

Check if AxiDraw support is available.

```python
from vfab.drivers import is_axidraw_available

if is_axidraw_available():
    print("AxiDraw support available")
else:
    print("AxiDraw support not available - install with: uv pip install -e '.[axidraw]'")
```

## Multi-pen System

### detect_svg_layers()

Detect layers in SVG file.

```python
from vfab.multipen import detect_svg_layers

layers = detect_svg_layers(Path("design.svg"))

# Returns list of layer information
for layer in layers:
    print(f"Layer: {layer['name']}, Paths: {layer['path_count']}")
```

### parse_axidraw_layer_control()

Parse AxiDraw layer control comments.

```python
from vfab.multipen import parse_axidraw_layer_control

layer_info = parse_axidraw_layer_control(svg_content)

# Returns layer control data
pen_assignments = layer_info.get("pen_assignments", {})
```

## Progress and Status

### show_status()

Display status messages with consistent formatting.

```python
from vfab.progress import show_status, progress_task

# Simple status
show_status("Job completed successfully", "success")
show_status("Warning: Low ink", "warning")
show_status("Error: Device not found", "error")

# Progress tracking
with progress_task("Processing files", 100) as update:
    for i in range(100):
        # Process item
        update(1)
```

### progress_task()

Context manager for progress tracking.

```python
from vfab.progress import progress_task

with progress_task("Optimizing jobs", job_count) as update:
    for job in jobs:
        # Optimize job
        optimize_job(job)
        update(1)
```

## Error Handling

### error_handler

Global error handler for consistent error reporting.

```python
from vfab.utils import error_handler

try:
    # Operation that might fail
    result = risky_operation()
except Exception as e:
    error_handler.handle(e)
    # Error is logged and reported consistently
```

## Utility Functions

### Common utilities

```python
from vfab.utils import (
    get_available_job_ids,
    format_duration,
    format_distance,
    validate_job_id,
    sanitize_filename
)

# Get available job IDs
job_ids = get_available_job_ids()

# Format values
duration_str = format_duration(1800)  # "30m 0s"
distance_str = format_distance(15000)  # "15.0m"

# Validation
is_valid = validate_job_id("abc123")
clean_name = sanitize_filename("my design/2024")
```

## Hooks System

### create_hook_executor()

Create hook executor for custom automation.

```python
from vfab.hooks import create_hook_executor

executor = create_hook_executor(job_id="abc123", workspace=Path("/workspace"))

# Execute hooks for event
executor.execute_hooks("COMPLETED", {
    "job_id": "abc123",
    "duration": 1800,
    "success": True
})
```

## Guards System

### create_guard_system()

Create guard system for validation.

```python
from vfab.guards import create_guard_system

guards = create_guard_system(config, workspace=Path("/workspace"))

# Run guards
result = guards.run_guards("pre_plot", {
    "job_id": "abc123",
    "device_ready": True
})

if not result.passed:
    print(f"Guards failed: {result.failures}")
```

## Recovery System

### get_crash_recovery()

Get crash recovery system.

```python
from vfab.recovery import get_crash_recovery, detect_interrupted_jobs

recovery = get_crash_recovery(workspace=Path("/workspace"))

# Detect interrupted jobs
interrupted = detect_interrupted_jobs(workspace, grace_minutes=5)

# Recover job
fsm = recovery.recover_job("abc123")
if fsm:
    recovery.register_fsm(fsm)
```

## Statistics Service

### get_statistics_service()

Get statistics service for analytics.

```python
from vfab.stats import get_statistics_service

stats = get_statistics_service()

# Record job event
stats.record_job_event(
    job_id="abc123",
    event_type="completed",
    duration_seconds=1800,
    distance_plotted_mm=15000
)

# Get system statistics
summary = stats.get_system_summary()
```

## Integration Examples

### Complete Job Processing

```python
from pathlib import Path
from vfab.fsm import create_fsm, JobState
from vfab.plotting import MultiPenPlotter
from vfab.config import get_config

def process_and_plot_job(job_id: str, svg_path: Path):
    """Complete job processing and plotting workflow."""
    
    # Create FSM
    config = get_config()
    fsm = create_fsm(job_id, Path(config.workspace))
    
    # Analyze job
    if not fsm.transition_to(JobState.ANALYZED, "Starting analysis"):
        return False
    
    # Optimize job
    if not fsm.apply_optimizations(preset="hq", digest=2):
        return False
    
    # Make ready
    if not fsm.transition_to(JobState.READY, "Optimization complete"):
        return False
    
    # Queue job
    if not fsm.queue_ready_job():
        return False
    
    # Arm job
    if not fsm.arm_job():
        return False
    
    # Start plotting
    if not fsm.transition_to(JobState.PLOTTING, "Starting plot"):
        return False
    
    # Plot with MultiPenPlotter
    plotter = MultiPenPlotter(interactive=False)
    result = plotter.plot_with_axidraw_layers(svg_path)
    
    if result["success"]:
        fsm.transition_to(JobState.COMPLETED, "Plotting complete")
        return True
    else:
        fsm.transition_to(JobState.FAILED, f"Plotting failed: {result['error']}")
        return False
```

### Custom Hook Implementation

```python
from vfab.hooks import HookExecutor

class CustomHookExecutor(HookExecutor):
    def execute_custom_notification(self, event_type: str, data: dict):
        """Send custom notification for job events."""
        
        if event_type == "COMPLETED":
            message = f"Job {data['job_id']} completed in {data['duration']}s"
            # Send to custom notification system
            self.send_notification(message)
        
        elif event_type == "FAILED":
            message = f"Job {data['job_id']} failed: {data['error']}"
            # Send alert
            self.send_alert(message)
```

### Custom Guard Implementation

```python
from vfab.guards import GuardSystem, GuardResult

class CustomGuardSystem(GuardSystem):
    def check_device_temperature(self, context: dict) -> GuardResult:
        """Check if device temperature is within safe range."""
        
        temp = self.get_device_temperature()
        
        if temp > 50:  # Too hot
            return GuardResult(
                passed=False,
                message=f"Device temperature too high: {temp}°C",
                suggestion="Let device cool down before plotting"
            )
        
        return GuardResult(passed=True)
```

## Testing Support

### Test Environment

```python
from vfab.testing import TestEnvironment, create_test_job

# Create test environment
env = TestEnvironment()

# Create test job
job_id = create_test_job(
    env.workspace,
    svg_content="<svg>...</svg>",
    name="test_job"
)

# Use in tests
fsm = create_fsm(job_id, env.workspace)
assert fsm.current_state == JobState.NEW
```

These core classes provide the foundation for building custom vfab integrations, extensions, and automated workflows.