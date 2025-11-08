# Job Lifecycle and States

ploTTY uses a sophisticated Finite State Machine (FSM) to manage the complete lifecycle of plotting jobs. Understanding the job states and transitions is crucial for integrating with ploTTY and building custom workflows.

## Job States

The job lifecycle is defined by the `JobState` enum with the following states:

### Primary States

| State | Description | Typical Duration |
|-------|-------------|------------------|
| `NEW` | Job created, not yet processed | Seconds |
| `QUEUED` | Job added to processing queue | Seconds to minutes |
| `ANALYZED` | Job analysis completed | Seconds |
| `OPTIMIZED` | Job optimization completed | Seconds to minutes |
| `READY` | Job ready for plotting | Variable |
| `ARMED` | Pre-flight checks completed | Seconds |
| `PLOTTING` | Currently being plotted | Minutes to hours |
| `COMPLETED` | Plotting finished successfully | Final state |

### Terminal States

| State | Description | Cause |
|-------|-------------|-------|
| `PAUSED` | Plotting paused by user | User action |
| `ABORTED` | Plotting aborted by user | User action |
| `FAILED` | Plotting failed due to error | System error |

## State Transition Diagram

```
    NEW
     │
     ├─→ ANALYZED ─→ OPTIMIZED ─→ READY ─→ ARMED ─→ PLOTTING ─→ COMPLETED
     │                                              │
     │                                              ├─→ PAUSED ─→ PLOTTING
     │                                              │
     │                                              ├─→ ABORTED
     │                                              │
     │                                              └─→ FAILED
     │
     └─→ READY (pristine mode) ─→ ARMED ─→ PLOTTING ─→ COMPLETED
```

## Valid Transitions

The FSM enforces strict state transitions to ensure job integrity:

### From NEW
- `NEW → ANALYZED`: Start job analysis
- `NEW → READY`: Skip analysis (pristine mode)

### From QUEUED
- `QUEUED → ANALYZED`: Start analysis
- `QUEUED → READY`: Skip analysis (pristine mode)

### From ANALYZED
- `ANALYZED → OPTIMIZED`: Apply optimizations
- `ANALYZED → FAILED`: Analysis failed

### From OPTIMIZED
- `OPTIMIZED → READY`: Optimization complete
- `OPTIMIZED → FAILED`: Optimization failed

### From READY
- `READY → QUEUED`: Queue for plotting
- `READY → ARMED`: Pre-flight checks

### From ARMED
- `ARMED → PLOTTING`: Start plotting
- `ARMED → FAILED`: Pre-flight checks failed

### From PLOTTING
- `PLOTTING → COMPLETED`: Plotting finished successfully
- `PLOTTING → PAUSED`: User paused plotting
- `PLOTTING → ABORTED`: User aborted plotting
- `PLOTTING → FAILED`: Plotting error

### From PAUSED
- `PAUSED → PLOTTING`: Resume plotting
- `PAUSED → ABORTED`: Abort paused job

## FSM Implementation

### Creating and Managing FSM

```python
from plotty.fsm import create_fsm, JobState
from pathlib import Path

# Create FSM for job
fsm = create_fsm(job_id="abc123", workspace=Path("/workspace"))

# Get current state
current_state = fsm.current_state
print(f"Current state: {current_state}")

# Check if transition is valid
if fsm.can_transition_to(JobState.ANALYZED):
    print("Can transition to ANALYZED")
```

### State Transitions

```python
# Simple transition
success = fsm.transition_to(JobState.ANALYZED, reason="Starting analysis")

# Transition with metadata
success = fsm.transition_to(
    JobState.OPTIMIZED, 
    reason="Optimization complete",
    metadata={
        "preset": "hq",
        "digest": 2,
        "optimization_time": 45.2
    }
)

# Check transition result
if success:
    print("Transition successful")
else:
    print("Transition failed")
```

### High-Level Operations

```python
# Apply optimizations (ANALYZED → OPTIMIZED → READY)
success = fsm.apply_optimizations(preset="hq", digest=2)

# Queue ready job (READY → QUEUED)
success = fsm.queue_ready_job()

# Arm job for plotting (READY → ARMED)
success = fsm.arm_job()

# Start plotting (ARMED → PLOTTING)
success = fsm.transition_to(JobState.PLOTTING, "Starting plot")
```

## State Metadata

Each state transition can include metadata that's stored with the job:

```python
# Transition with rich metadata
fsm.transition_to(
    JobState.COMPLETED,
    reason="Plotting completed successfully",
    metadata={
        "plotting_time": 1800.5,
        "distance_plotted": 15000.0,
        "pen_changes": 3,
        "layers_completed": 5,
        "device_used": "axidraw:v2",
        "preset": "safe"
    }
)
```

## Job Data Structure

Jobs store their state and history in JSON format:

```json
{
    "id": "abc123",
    "name": "my_design",
    "state": "COMPLETED",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z",
    "state_history": [
        {
            "state": "NEW",
            "timestamp": "2024-01-15T10:30:00Z",
            "reason": "Job created"
        },
        {
            "state": "ANALYZED",
            "timestamp": "2024-01-15T10:30:15Z",
            "reason": "Analysis complete",
            "metadata": {
                "layer_count": 5,
                "path_count": 127
            }
        },
        {
            "state": "OPTIMIZED",
            "timestamp": "2024-01-15T10:31:00Z",
            "reason": "Optimization complete",
            "metadata": {
                "preset": "hq",
                "digest": 2,
                "optimization_time": 45.2
            }
        },
        {
            "state": "READY",
            "timestamp": "2024-01-15T10:31:05Z",
            "reason": "Ready to plot"
        },
        {
            "state": "ARMED",
            "timestamp": "2024-01-15T10:45:00Z",
            "reason": "Pre-flight checks passed"
        },
        {
            "state": "PLOTTING",
            "timestamp": "2024-01-15T10:45:30Z",
            "reason": "Started plotting"
        },
        {
            "state": "COMPLETED",
            "timestamp": "2024-01-15T11:00:30Z",
            "reason": "Plotting completed successfully",
            "metadata": {
                "plotting_time": 1800.5,
                "distance_plotted": 15000.0,
                "pen_changes": 3,
                "layers_completed": 5
            }
        }
    ],
    "config_status": "OPTIMIZED",
    "paper": "A4",
    "metadata": {
        "file_type": "svg",
        "mode": "normal",
        "preset": "hq",
        "digest": 2
    }
}
```

## State-Specific Operations

### NEW State Operations

```python
if fsm.current_state == JobState.NEW:
    # Job is newly created
    # Can start analysis or go directly to ready (pristine)
    
    # Start analysis
    fsm.transition_to(JobState.ANALYZED, "Starting analysis")
    
    # Or skip to ready (pristine mode)
    fsm.transition_to(JobState.READY, "Pristine mode - ready to queue")
```

### ANALYZED State Operations

```python
if fsm.current_state == JobState.ANALYZED:
    # Job analysis is complete
    # Can apply optimizations
    
    success = fsm.apply_optimizations(
        preset="hq",
        digest=2
    )
```

### READY State Operations

```python
if fsm.current_state == JobState.READY:
    # Job is ready for plotting
    # Can queue or arm for plotting
    
    # Queue for later plotting
    fsm.queue_ready_job()
    
    # Or arm for immediate plotting
    fsm.arm_job()
```

### ARMED State Operations

```python
if fsm.current_state == JobState.ARMED:
    # Pre-flight checks complete
    # Ready to start plotting
    
    fsm.transition_to(JobState.PLOTTING, "Starting plot")
```

### PLOTTING State Operations

```python
if fsm.current_state == JobState.PLOTTING:
    # Currently plotting
    # Can pause, abort, or complete
    
    # Pause plotting
    fsm.transition_to(JobState.PAUSED, "User paused")
    
    # Abort plotting
    fsm.transition_to(JobState.ABORTED, "User aborted")
    
    # Complete successfully
    fsm.transition_to(JobState.COMPLETED, "Plotting complete")
```

## Error Handling and Recovery

### Transition Failures

```python
success = fsm.transition_to(JobState.ANALYZED, "Starting analysis")

if not success:
    # Get failure reason
    error = fsm.get_last_error()
    print(f"Transition failed: {error}")
    
    # Check current state
    print(f"Current state: {fsm.current_state}")
```

### Recovery from Failed States

```python
if fsm.current_state == JobState.FAILED:
    # Get failure information
    job_data = fsm.get_job_data()
    failure_reason = job_data.get("failure_reason", "Unknown")
    
    # Can retry from appropriate state
    if "analysis" in failure_reason.lower():
        # Retry analysis
        fsm.transition_to(JobState.ANALYZED, "Retrying analysis")
    elif "optimization" in failure_reason.lower():
        # Retry optimization
        fsm.apply_optimizations(preset="default")
    elif "plotting" in failure_reason.lower():
        # Retry plotting
        fsm.arm_job()  # Re-arm and try again
```

## Hooks Integration

State transitions trigger hooks for automation:

```python
# Hook configuration in config.yaml
hooks:
  ANALYZED:
    - command: "notify-send 'Job {job_name} analyzed'"
      type: "system"
  OPTIMIZED:
    - command: "python scripts/validate_optimization.py {job_id}"
      type: "script"
  COMPLETED:
    - command: "curl -X POST https://api.example.com/complete -d '{job_data}'"
      type: "webhook"
  FAILED:
    - command: "python scripts/alert_failure.py {job_id} {error}"
      type: "script"
```

## Guards Integration

Guards validate state transitions:

```python
# Guard system checks before critical transitions
guards = create_guard_system(config, workspace)

# Before plotting
if fsm.current_state == JobState.ARMED:
    guard_result = guards.run_guards("pre_plot", {
        "job_id": fsm.job_id,
        "device_ready": True
    })
    
    if guard_result.passed:
        fsm.transition_to(JobState.PLOTTING, "Starting plot")
    else:
        fsm.transition_to(JobState.FAILED, f"Guards failed: {guard_result.failures}")
```

## Statistics Integration

State transitions are recorded for analytics:

```python
# Statistics service automatically records state changes
stats = get_statistics_service()

# Manual recording (usually done automatically)
stats.record_job_event(
    job_id=fsm.job_id,
    event_type="state_change",
    from_state=previous_state.value,
    to_state=new_state.value,
    metadata={"reason": reason}
)
```

## Best Practices

### 1. Always Check Transition Results

```python
# Good
success = fsm.transition_to(JobState.ANALYZED, "Starting analysis")
if not success:
    handle_failure(fsm.get_last_error())

# Bad - ignores failure
fsm.transition_to(JobState.ANALYZED, "Starting analysis")
```

### 2. Use High-Level Operations When Available

```python
# Good - uses built-in logic
success = fsm.apply_optimizations(preset="hq", digest=2)

# Bad - manual transitions
fsm.transition_to(JobState.OPTIMIZED, "Applying optimizations")
# ... missing validation and error handling
```

### 3. Include Rich Metadata

```python
# Good - informative metadata
fsm.transition_to(
    JobState.COMPLETED,
    "Plotting completed successfully",
    metadata={
        "plotting_time": 1800.5,
        "distance_plotted": 15000.0,
        "pen_changes": 3,
        "device_used": "axidraw:v2"
    }
)

# Bad - minimal information
fsm.transition_to(JobState.COMPLETED, "Done")
```

### 4. Handle State-Specific Logic

```python
# Good - state-specific handling
if fsm.current_state == JobState.PLOTTING:
    # Handle plotting-specific logic
    pass
elif fsm.current_state == JobState.PAUSED:
    # Handle pause-specific logic
    pass

# Bad - assumes state
# This might fail if job is not in PLOTTING state
fsm.transition_to(JobState.COMPLETED, "Complete")
```

## Integration Examples

### Custom Workflow Automation

```python
def automated_plotting_workflow(job_id: str, svg_path: Path):
    """Complete automated plotting workflow."""
    
    fsm = create_fsm(job_id, svg_path.parent)
    
    try:
        # Analyze
        if not fsm.transition_to(JobState.ANALYZED, "Auto-analysis"):
            return False
        
        # Optimize with best settings
        if not fsm.apply_optimizations(preset="hq", digest=2):
            return False
        
        # Queue and arm
        if not fsm.queue_ready_job():
            return False
        
        if not fsm.arm_job():
            return False
        
        # Start plotting
        if not fsm.transition_to(JobState.PLOTTING, "Auto-plot"):
            return False
        
        # Plot with MultiPenPlotter
        plotter = MultiPenPlotter(interactive=False)
        result = plotter.plot_with_axidraw_layers(svg_path)
        
        if result["success"]:
            fsm.transition_to(
                JobState.COMPLETED,
                "Auto-plot complete",
                metadata=result
            )
            return True
        else:
            fsm.transition_to(
                JobState.FAILED,
                f"Auto-plot failed: {result['error']}"
            )
            return False
            
    except Exception as e:
        fsm.transition_to(JobState.FAILED, f"Workflow error: {e}")
        return False
```

### State Monitoring

```python
def monitor_job_state(job_id: str, workspace: Path):
    """Monitor job state changes."""
    
    fsm = create_fsm(job_id, workspace)
    last_state = None
    
    while True:
        current_state = fsm.current_state
        
        if current_state != last_state:
            print(f"Job {job_id} state changed: {last_state} → {current_state}")
            
            # Handle state-specific actions
            if current_state == JobState.COMPLETED:
                print(f"Job {job_id} completed successfully!")
                break
            elif current_state == JobState.FAILED:
                print(f"Job {job_id} failed!")
                break
            elif current_state == JobState.PLOTTING:
                print(f"Job {job_id} is plotting...")
            
            last_state = current_state
        
        time.sleep(1)  # Check every second
```

Understanding the job lifecycle and FSM is essential for building robust ploTTY integrations and custom workflows. The state system ensures job integrity, enables error recovery, and provides hooks for automation.