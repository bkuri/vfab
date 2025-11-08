# CLI API Reference

The ploTTY CLI provides a comprehensive command-line interface built with Typer. The CLI is organized into logical command groups for different operations.

## Main CLI Structure

```bash
plotty [GLOBAL_OPTIONS] COMMAND [SUBCOMMAND] [OPTIONS] [ARGUMENTS]
```

### Global Options

- `--version`: Show version and exit
- `--help`: Show help message

## Command Groups

### 1. Add Commands (`plotty add`)

Add new resources to the system.

#### `plotty add job`
Add a single job from an SVG or PLOB file.

```bash
plotty add job JOB_NAME FILE_PATH [OPTIONS]
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
plotty add job my_design design.svg --apply

# Add job with high-quality optimization
plotty add job my_design design.svg --preset hq --digest 2 --apply

# Preview job addition
plotty add job my_design design.svg --dry-run
```

#### `plotty add jobs`
Add multiple jobs using a file pattern.

```bash
plotty add jobs PATTERN [OPTIONS]
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
plotty add jobs "*.svg" --apply

# Add PLOB files in pristine mode
plotty add jobs "designs/*.plob" --pristine --apply
```

#### `plotty add pen`
Add a new pen configuration.

```bash
plotty add pen NAME WIDTH_MM SPEED_CAP PRESSURE PASSES [OPTIONS]
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
plotty add pen "0.3mm black" 0.3 25.0 80 1 --color "#000000"
```

#### `plotty add paper`
Add a new paper configuration.

```bash
plotty add paper NAME WIDTH_MM HEIGHT_MM [OPTIONS]
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
plotty add paper "A4" 210.0 297.0 --margin 15 --orientation portrait
```

### 2. List Commands (`plotty list`)

List and manage resources.

#### `plotty list jobs`
List all jobs with their status.

```bash
plotty list jobs [OPTIONS]
```

**Options:**
- `--state, -s`: Filter by job state
- `--format, -f`: Output format (table, json, csv)

#### `plotty list pens`
List all pen configurations.

```bash
plotty list pens [OPTIONS]
```

#### `plotty list papers`
List all paper configurations.

```bash
plotty list papers [OPTIONS]
```

#### `plotty list presets`
List available plotting presets.

```bash
plotty list presets [OPTIONS]
```

#### `plotty list guards`
List configured guards.

```bash
plotty list guards [OPTIONS]
```

### 3. Info Commands (`plotty info`)

Status and monitoring commands.

#### `plotty info` (default)
Show complete status overview.

```bash
plotty info [OPTIONS]
```

**Options:**
- `--json`: Export status as JSON
- `--csv`: Export status as CSV

#### `plotty info system`
Show overall system status.

```bash
plotty info system [OPTIONS]
```

#### `plotty info tldr`
Show quick overview (too long; didn't read).

```bash
plotty info tldr [OPTIONS]
```

#### `plotty info job`
Show detailed information about a specific job.

```bash
plotty info job JOB_ID [OPTIONS]
```

**Arguments:**
- `JOB_ID`: Job ID to show details for

**Options:**
- `--json`: Export status as JSON
- `--csv`: Export status as CSV

#### `plotty info queue`
Show job queue status.

```bash
plotty info queue [OPTIONS]
```

**Options:**
- `--limit, -l`: Limit number of jobs shown (default: 10)
- `--state, -s`: Filter by job state
- `--json`: Export as JSON
- `--csv`: Export as CSV

#### `plotty info session`
Show current session information.

```bash
plotty info session
```

#### `plotty info reset`
Reset the current session.

```bash
plotty info reset [OPTIONS]
```

**Options:**
- `--apply`: Apply session reset (dry-run by default)

### 4. Core Job Commands

#### `plotty plot` / `plotty start`
Start plotting a job.

```bash
plotty plot JOB_ID [OPTIONS]
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
plotty plot my_design --dry-run

# Plot with safe preset
plotty plot my_design --preset safe --apply

# Plot with specific device
plotty plot my_design --port /dev/ttyUSB0 --model 2 --apply
```

#### `plotty plan`
Plan a job for plotting with layer analysis.

```bash
plotty plan JOB_ID [OPTIONS]
```

**Arguments:**
- `JOB_ID`: Job ID to plan

**Options:**
- `--pen, -p`: Default pen specification (default: "0.3mm black")
- `--interactive, -i`: Interactive layer planning

#### `plotty optimize`
Optimize jobs with preview by default.

```bash
plotty optimize [JOB_IDS] [OPTIONS]
```

**Arguments:**
- `JOB_IDS`: Comma-separated job IDs (optional, defaults to all optimizable jobs)

**Options:**
- `--preset, -p`: Optimization preset (fast, default, hq)
- `--digest, -d`: Digest level for AxiDraw acceleration (0-2)
- `--apply`: Actually perform optimization (preview by default)

#### `plotty queue`
Manually queue a job for plotting.

```bash
plotty queue JOB_ID
```

**Arguments:**
- `JOB_ID`: Job ID to queue

### 5. Recovery Commands

#### `plotty resume`
Resume interrupted plotting jobs.

```bash
plotty resume [JOB_ID] [OPTIONS]
```

**Arguments:**
- `JOB_ID`: Job ID to resume (optional, will detect interrupted jobs)

**Options:**
- `--force`: Force resume without confirmation
- `--from-layer`: Resume from specific layer

#### `plotty restart`
Restart job from beginning.

```bash
plotty restart JOB_ID [OPTIONS]
```

**Arguments:**
- `JOB_ID`: Job ID to restart

**Options:**
- `--force`: Force restart without confirmation

### 6. Check Commands (`plotty check`)

System and device checking.

#### `plotty check self`
Check ploTTY installation and dependencies.

```bash
plotty check self
```

#### `plotty check camera`
Check camera configuration and access.

```bash
plotty check camera [OPTIONS]
```

#### `plotty check servo`
Check servo/pen lift system.

```bash
plotty check servo [OPTIONS]
```

#### `plotty check timing`
Check timing and synchronization.

```bash
plotty check timing [OPTIONS]
```

#### `plotty check ready`
Check if system is ready for plotting.

```bash
plotty check ready [OPTIONS]
```

#### `plotty check job`
Check job configuration and files.

```bash
plotty check job JOB_ID [OPTIONS]
```

### 7. Stats Commands (`plotty stats`)

Statistics and analytics.

#### `plotty stats summary`
Show system statistics summary.

```bash
plotty stats summary [OPTIONS]
```

#### `plotty stats jobs`
Show job statistics.

```bash
plotty stats jobs [OPTIONS]
```

#### `plotty stats performance`
Show performance metrics.

```bash
plotty stats performance [OPTIONS]
```

### 8. System Commands (`plotty system`)

System management commands.

#### `plotty system export`
Export system configuration and data.

```bash
plotty system export [OPTIONS]
```

#### `plotty system import`
Import system configuration and data.

```bash
plotty system import FILE_PATH [OPTIONS]
```

### 9. Remove Commands (`plotty remove`)

Remove resources from the system.

#### `plotty remove job`
Remove a job.

```bash
plotty remove job JOB_ID [OPTIONS]
```

#### `plotty remove pen`
Remove a pen configuration.

```bash
plotty remove pen PEN_NAME [OPTIONS]
```

#### `plotty remove paper`
Remove a paper configuration.

```bash
plotty remove paper PAPER_NAME [OPTIONS]
```

### 10. Interactive Commands

#### `plotty interactive`
Start an interactive plotting session.

```bash
plotty interactive [OPTIONS]
```

#### `plotty setup`
Run setup wizard.

```bash
plotty setup
```

## Common Options Pattern

Many ploTTY commands follow these patterns:

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

ploTTY uses standard exit codes:
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
    plotty add job "$job_name" "$file" --preset hq --apply
    plotty plot "$job_name" --preset safe --apply
done
```

### Python Integration
```python
import subprocess
import json

# Get job queue status
result = subprocess.run(
    ["plotty", "info", "queue", "--json"],
    capture_output=True,
    text=True
)
queue_data = json.loads(result.stdout)
print(f"Jobs in queue: {len(queue_data['jobs'])}")
```