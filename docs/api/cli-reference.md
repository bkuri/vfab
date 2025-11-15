# CLI API Reference

The vfab CLI provides a comprehensive command-line interface built with Typer. The CLI is organized into logical command groups for different operations.

## Main CLI Structure

```bash
vfab [GLOBAL_OPTIONS] COMMAND [SUBCOMMAND] [OPTIONS] [ARGUMENTS]
```

### Global Options

- `--version`: Show version and exit
- `--help`: Show help message

## Command Groups

### 1. Add Commands (`vfab add`)

Add new resources to the system.

#### `vfab add job`
Add a single job from an SVG or PLOB file.

```bash
vfab add job JOB_NAME FILE_PATH [OPTIONS]
```

**Arguments:**
- `JOB_NAME`: Name for the new job
- `FILE_PATH`: Path to SVG or PLOB file

**Options:**
- `--preset, -p`: Optimization preset (fast, default, hq)
- `--digest, -d`: Digest level for AxiDraw acceleration (0-2)
- `--force, -f`: Override existing job with same name
- `--apply`: Actually add job (dry-run by default)
- `--dry-run`: Preview job addition without creating files

**Examples:**
```bash
# Add job with default settings
vfab add job my_design design.svg --apply

# Add job with high-quality optimization
vfab add job my_design design.svg --preset hq --digest 2 --apply

# Preview job addition
vfab add job my_design design.svg --dry-run
```

#### `vfab add jobs`
Add multiple jobs using a file pattern.

```bash
vfab add jobs PATTERN [OPTIONS]
```

**Arguments:**
- `PATTERN`: File pattern (e.g., '*.svg', 'designs/*.plob')

**Options:**
- `--pristine`: Skip optimization (add in pristine state)
- `--apply`: Actually add jobs (dry-run by default)
- `--dry-run`: Preview job addition without creating files

**Examples:**
```bash
# Add all SVG files
vfab add jobs "*.svg" --apply

# Add PLOB files in pristine mode
vfab add jobs "designs/*.plob" --pristine --apply
```

#### `vfab add pen`
Add a new pen configuration.

```bash
vfab add pen NAME WIDTH_MM SPEED_CAP PRESSURE PASSES [OPTIONS]
```

**Arguments:**
- `NAME`: Pen name (unique)
- `WIDTH_MM`: Pen width in millimeters
- `SPEED_CAP`: Maximum speed
- `PRESSURE`: Pressure setting (0-100)
- `PASSES`: Number of passes (≥1)

**Options:**
- `--color, -c`: Pen color in hex format (default: #000000)

**Example:**
```bash
vfab add pen "0.3mm black" 0.3 25.0 80 1 --color "#000000"
```

#### `vfab add paper`
Add a new paper configuration.

```bash
vfab add paper NAME WIDTH_MM HEIGHT_MM [OPTIONS]
```

**Arguments:**
- `NAME`: Paper name (unique)
- `WIDTH_MM`: Paper width in millimeters
- `HEIGHT_MM`: Paper height in millimeters

**Options:**
- `--margin, -m`: Margin in millimeters (default: 10)
- `--orientation, -o`: Paper orientation (portrait/landscape, default: portrait)

**Example:**
```bash
vfab add paper "A4" 210.0 297.0 --margin 15 --orientation portrait
```

### 2. List Commands (`vfab list`)

List and manage resources.

#### `vfab list jobs`
List all jobs with their status.

```bash
vfab list jobs [OPTIONS]
```

**Options:**
- `--state, -s`: Filter by job state
- `--format, -f`: Output format (table, json, csv)

#### `vfab list pens`
List all pen configurations.

```bash
vfab list pens [OPTIONS]
```

#### `vfab list papers`
List all paper configurations.

```bash
vfab list papers [OPTIONS]
```

#### `vfab list presets`
List available plotting presets.

```bash
vfab list presets [OPTIONS]
```

#### `vfab list guards`
List configured guards.

```bash
vfab list guards [OPTIONS]
```

### 3. Info Commands (`vfab info`)

Status and monitoring commands.

#### `vfab info` (default)
Show complete status overview.

```bash
vfab info [OPTIONS]
```

**Options:**
- `--json`: Export status as JSON
- `--csv`: Export status as CSV

#### `vfab info system`
Show overall system status.

```bash
vfab info system [OPTIONS]
```

#### `vfab info tldr`
Show quick overview (too long; didn't read).

```bash
vfab info tldr [OPTIONS]
```

#### `vfab info job`
Show detailed information about a specific job.

```bash
vfab info job JOB_ID [OPTIONS]
```

**Arguments:**
- `JOB_ID`: Job ID to show details for

**Options:**
- `--json`: Export status as JSON
- `--csv`: Export status as CSV

#### `vfab info queue`
Show job queue status.

```bash
vfab info queue [OPTIONS]
```

**Options:**
- `--limit, -l`: Limit number of jobs shown (default: 10)
- `--state, -s`: Filter by job state
- `--json`: Export as JSON
- `--csv`: Export as CSV

#### `vfab info session`
Show current session information.

```bash
vfab info session
```

#### `vfab info reset`
Reset the current session.

```bash
vfab info reset [OPTIONS]
```

**Options:**
- `--apply`: Apply session reset (dry-run by default)

### 4. Core Job Commands

#### `vfab plot` / `vfab start`
Start plotting a job.

```bash
vfab plot JOB_ID [OPTIONS]
```

**Arguments:**
- `JOB_ID`: Job ID to start

**Options:**
- `--preset, -p`: Plot preset (fast, safe, preview, detail, draft)
- `--port`: Device port
- `--model`: Device model (default: 1)
- `--apply`: Actually start plotting (dry-run by default)
- `--dry-run`: Preview plotting without moving pen

**Available Presets:**
- `fast`: Maximum speed for quick drafts
- `safe`: Conservative settings for reliability
- `preview`: Quick preview without pen down
- `detail`: High precision for detailed artwork
- `draft`: Quick draft with moderate quality

**Examples:**
```bash
# Preview plotting
vfab plot my_design --dry-run

# Plot with safe preset
vfab plot my_design --preset safe --apply

# Plot with specific device
vfab plot my_design --port /dev/ttyUSB0 --model 2 --apply
```

#### `vfab plan`
Plan a job for plotting with layer analysis.

```bash
vfab plan JOB_ID [OPTIONS]
```

**Arguments:**
- `JOB_ID`: Job ID to plan

**Options:**
- `--pen, -p`: Default pen specification (default: "0.3mm black")
- `--interactive, -i`: Interactive layer planning

#### `vfab optimize`
Optimize jobs with preview by default.

```bash
vfab optimize [JOB_IDS] [OPTIONS]
```

**Arguments:**
- `JOB_IDS`: Comma-separated job IDs (optional, defaults to all optimizable jobs)

**Options:**
- `--preset, -p`: Optimization preset (fast, default, hq)
- `--digest, -d`: Digest level for AxiDraw acceleration (0-2)
- `--apply`: Actually perform optimization (preview by default)

#### `vfab queue`
Manually queue a job for plotting.

```bash
vfab queue JOB_ID
```

**Arguments:**
- `JOB_ID`: Job ID to queue

### 5. Recovery Commands

#### `vfab resume`
Resume interrupted plotting jobs.

```bash
vfab resume [JOB_ID] [OPTIONS]
```

**Arguments:**
- `JOB_ID`: Job ID to resume (optional, will detect interrupted jobs)

**Options:**
- `--force`: Force resume without confirmation
- `--from-layer`: Resume from specific layer

#### `vfab restart`
Restart job from beginning.

```bash
vfab restart JOB_ID [OPTIONS]
```

**Arguments:**
- `JOB_ID`: Job ID to restart

**Options:**
- `--force`: Force restart without confirmation

### 6. Check Commands (`vfab check`)

System and device checking.

#### `vfab check self`
Check vfab installation and dependencies.

```bash
vfab check self
```

#### `vfab check camera`
Check camera configuration and access.

```bash
vfab check camera [OPTIONS]
```

#### `vfab check servo`
Check servo/pen lift system.

```bash
vfab check servo [OPTIONS]
```

#### `vfab check timing`
Check timing and synchronization.

```bash
vfab check timing [OPTIONS]
```

#### `vfab check ready`
Check if system is ready for plotting.

```bash
vfab check ready [OPTIONS]
```

#### `vfab check job`
Check job configuration and files.

```bash
vfab check job JOB_ID [OPTIONS]
```

### 7. Stats Commands (`vfab stats`)

Statistics and analytics.

#### `vfab stats summary`
Show system statistics summary.

```bash
vfab stats summary [OPTIONS]
```

#### `vfab stats jobs`
Show job statistics.

```bash
vfab stats jobs [OPTIONS]
```

#### `vfab stats performance`
Show performance metrics.

```bash
vfab stats performance [OPTIONS]
```

### 8. System Commands (`vfab system`)

System management commands.

#### `vfab system export`
Export system configuration and data.

```bash
vfab system export [OPTIONS]
```

#### `vfab system import`
Import system configuration and data.

```bash
vfab system import FILE_PATH [OPTIONS]
```

### 9. Remove Commands (`vfab remove`)

Remove resources from the system.

#### `vfab remove job`
Remove a job.

```bash
vfab remove job JOB_ID [OPTIONS]
```

#### `vfab remove pen`
Remove a pen configuration.

```bash
vfab remove pen PEN_NAME [OPTIONS]
```

#### `vfab remove paper`
Remove a paper configuration.

```bash
vfab remove paper PAPER_NAME [OPTIONS]
```

### 10. Interactive Commands

#### `vfab interactive`
Start an interactive plotting session.

```bash
vfab interactive [OPTIONS]
```

#### `vfab setup`
Run setup wizard.

```bash
vfab setup
```

### 11. Monitoring Commands (`vfab daemon`, `vfab monitor`)

Real-time monitoring and daemon management commands.

#### `vfab daemon`
Start the vfab daemon process with WebSocket server.

```bash
vfab daemon [OPTIONS]
```

**Options:**
- `--host, -h`: WebSocket server bind address (default: localhost)
- `--port, -p`: WebSocket server port (default: 8766)
- `--workspace, -w`: Working directory for jobs and data
- `--log-level, -l`: Logging verbosity (debug, info, warning, error)
- `--config, -c`: Path to configuration file
- `--daemonize, -d`: Run as background daemon process
- `--pid-file`: Path to PID file for process management
- `--user, -u`: Run as specified user (requires root)
- `--group, -g`: Run as specified group (requires root)

**Examples:**
```bash
# Development daemon
vfab daemon --log-level debug

# Production daemon
sudo vfab daemon --host 0.0.0.0 --port 8766 --daemonize --user vfab

# Custom workspace
vfab daemon --workspace /mnt/storage/vfab-workspace
```

#### `vfab monitor`
Connect to WebSocket server for real-time monitoring.

```bash
vfab monitor [OPTIONS]
```

**Options:**
- `--host, -h`: WebSocket server host (default: localhost)
- `--port, -p`: WebSocket server port (default: 8766)
- `--channels, -c`: Channels to subscribe to (jobs, system, device)
- `--job-id`: Filter messages for specific job ID
- `--level, -l`: Message level filter (debug, info, warning, error)
- `--format, -f`: Output format (json, pretty)
- `--follow, -F`: Continuous monitoring (don't exit)
- `--api-key`: API key for authentication
- `--timeout`: Connection timeout in seconds (default: 30)

**Examples:**
```bash
# Monitor all channels
vfab monitor --follow

# Monitor specific job
vfab monitor --job-id my_design_001 --follow

# Monitor with JSON output
vfab monitor --format json --channels jobs,system --follow

# Production monitoring with authentication
vfab monitor --api-key your-secret-key --host monitor.example.com --follow
```

**Channel Subscription:**
- `jobs`: Job state changes and progress updates
- `system`: System status and alerts
- `device`: Device status and hardware events

**Output Formats:**
- `pretty`: Human-readable formatted output (default)
- `json`: Raw JSON messages for programmatic use

## Common Options Pattern

Many vfab commands follow these patterns:

### Dry-run / Apply Pattern
Most modification commands use dry-run by default:
- `--dry-run`: Preview changes without executing
- `--apply`: Actually execute the changes

### Output Format Options
Status and listing commands support multiple output formats:
- `--json`: Export as JSON
- `--csv`: Export as CSV
- Default: Human-readable table format

### Autocompletion
The CLI supports autocompletion for job IDs and other parameters where applicable.

## Exit Codes

vfab uses standard exit codes:
- `0`: Success
- `1`: General error
- `2`: Invalid usage
- `3`: Resource not found
- `4`: Resource already exists

## Configuration

The CLI can be configured via:
- Environment variables (`PLOTTY_CONFIG`)
- Configuration file (`config/config.yaml`)
- Command-line options (highest priority)

## Integration Examples

### Bash Scripting
```bash
#!/bin/bash
# Add and plot multiple designs
for file in designs/*.svg; do
    job_name=$(basename "$file" .svg)
    vfab add job "$job_name" "$file" --preset hq --apply
    vfab plot "$job_name" --preset safe --apply
done
```

### Python Integration
```python
import subprocess
import json

# Get job queue status
result = subprocess.run(
    ["vfab", "info", "queue", "--json"],
    capture_output=True,
    text=True
)
queue_data = json.loads(result.stdout)
print(f"Jobs in queue: {len(queue_data['jobs'])}")
```