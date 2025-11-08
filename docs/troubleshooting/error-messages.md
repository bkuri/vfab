# Error Message Reference

This document provides a comprehensive reference for error messages encountered in ploTTY, their causes, and specific solutions.

## Quick Error Lookup

### A
- **AxiDraw support not available** - [Device Integration Issues](../README.md#device-integration-issues)
- **AttributeError: module does not have attribute** - [Common Test Failures](../README.md#common-test-failures-and-root-causes)

### C
- **Config invalid** - [Database and Configuration Problems](../README.md#database-and-configuration-problems)
- **Connection refused** - [Database Connection Issues](../README.md#1-database-connection-issues)
- **Camera not accessible** - [Camera Integration Issues](../README.md#2-camera-integration-issues)

### D
- **Database locked** - [Concurrent Access Issues](../README.md#2-concurrent-access-issues)
- **Device not connected** - [AxiDraw Connection Problems](../README.md#1-axidraw-connection-problems)

### F
- **File not found** - [File/Path Errors](../README.md#2-filepath-errors)
- **Permission denied** - [Permission Errors](../README.md#3-permission-errors)

### I
- **ImportError** - [Module Import Issues](../README.md#1-module-import-and-mocking-issues)
- **Invalid state transition** - [State Machine Corruption](../README.md#3-state-machine-corruption)

### J
- **Job stuck in PLOTTING** - [Job Recovery After Crash](../README.md#1-job-recovery-after-crash)

### N
- **No jobs directory found** - [Workspace and Directory Issues](../README.md#3-workspace-and-directory-issues)

### V
- **Validation failed** - [Configuration File Issues](../README.md#2-configuration-file-issues)

## Detailed Error Analysis

### Configuration Errors

#### `ConfigError: Config invalid`
```bash
# Example error:
[red]Error:[/red] Config invalid
[yellow]💡 Suggestion:[/yellow] Run 'plotty setup' to create a valid configuration
[dim]Technical details:[/dim] YAML parsing error: line 5, column 3: mapping values are not allowed here

# Common causes:
- Invalid YAML syntax
- Missing required fields
- Incorrect data types

# Solutions:
1. Validate YAML syntax:
   python -c "import yaml; yaml.safe_load(open('~/.config/plotty/config.yaml'))"

2. Recreate configuration:
   plotty setup

3. Check configuration schema:
   plotty info system
```

#### `ValidationError: Invalid value`
```bash
# Example error:
[red]Error:[/red] Invalid value: "A5" is not a valid paper size
[yellow]💡 Suggestion:[/yellow] Use 'plotty list paper' to see available paper sizes

# Common validation errors:
- Invalid paper sizes
- Invalid pen types
- Invalid orientations

# Solutions:
1. Check available options:
   plotty list paper
   plotty list pens

2. Use correct values:
   plotty add job test file.svg --paper A4
```

### Device Errors

#### `DeviceError: Device not connected`
```bash
# Example error:
[red]Error:[/red] Device not connected
[yellow]💡 Suggestion:[/yellow] Check AxiDraw connection and install with: uv pip install -e '.[axidraw]'

# Diagnostic steps:
1. Check physical connection:
   lsusb | grep -i axidraw

2. Check device permissions:
   ls -la /dev/ttyUSB* /dev/ttyACM*

3. Test device detection:
   plotty check servo

# Solutions:
1. Install AxiDraw support:
   uv pip install -e ".[axidraw]"

2. Fix permissions:
   sudo usermod -a -G dialout $USER
   # Logout and login again

3. Specify device explicitly:
   plotty add job test file.svg --device /dev/ttyUSB0
```

### Job Management Errors

#### `JobError: Job stuck in PLOTTING state`
```bash
# Example error:
[red]Error:[/red] Job job_123 is stuck in PLOTTING state
[yellow]💡 Suggestion:[/yellow] Use 'plotty restart job_123' to check job status

# Recovery procedures:
1. Check job status:
   plotty info job job_123

2. Resume interrupted jobs:
   plotty resume

3. Force restart:
   plotty restart job_123

4. Check for crashes:
   cat ~/.local/share/plotty/workspace/jobs/job_123/journal.jsonl | grep emergency_shutdown
```

### File System Errors

#### `FileNotFoundError: File not found`
```bash
# Example error:
[red]Error:[/red] File not found: /path/to/file.svg
[yellow]💡 Suggestion:[/yellow] Check if file exists and is accessible: /path/to/file.svg

# Common causes:
- Incorrect file path
- File permissions
- File actually doesn't exist

# Solutions:
1. Verify file exists:
   ls -la /path/to/file.svg

2. Check file type:
   file /path/to/file.svg

3. Use absolute paths:
   plotty add job test /full/path/to/file.svg
```

#### `PermissionError: Permission denied`
```bash
# Example error:
[red]Error:[/red] Permission denied
[yellow]💡 Suggestion:[/yellow] Check file permissions and ensure you have access to required resources

# Solutions:
1. Check permissions:
   ls -la ~/.local/share/plotty/

2. Fix permissions:
   chmod -R u+rw ~/.local/share/plotty/

3. Check ownership:
   chown -R $USER:$USER ~/.local/share/plotty/
```

### Database Errors

#### `ConnectionError: Database locked`
```bash
# Example error:
[red]Error:[/red] Connection or device error
[yellow]💡 Suggestion:[/yellow] Check device connections and ensure plotter is properly configured

# For database locks:
1. Check for running processes:
   ps aux | grep plotty

2. Wait for completion:
   plotty info queue

3. Force unlock (last resort):
   rm ~/.local/share/plotty/plotty.db-journal

4. Reinitialize database:
   rm ~/.local/share/plotty/plotty.db
   plotty setup
```

### State Machine Errors

#### `Invalid state transition`
```bash
# Example error:
[red]Error:[/red] Cannot transition from COMPLETED to PLOTTING
[yellow]💡 Suggestion:[/yellow] Use 'plotty status queue' to see available job IDs

# Valid state transitions:
NEW → ANALYZED → OPTIMIZED → READY → QUEUED → ARMED → PLOTTING → (PAUSED) → COMPLETED | ABORTED | FAILED

# Solutions:
1. Check current state:
   plotty info job <job_id>

2. Use valid transitions:
   plotty restart <job_id>  # Reset to NEW
   plotty resume <job_id>   # Resume from PAUSED
```

## Error Categories and Handling

### 1. User Input Errors
- **Symptoms**: Invalid parameters, malformed commands
- **Category**: `validation` or `parameter`
- **Handling**: Use `--help` flag, check available options

### 2. System Configuration Errors  
- **Symptoms**: Config file issues, missing dependencies
- **Category**: `config` or `dependency`
- **Handling**: Run `plotty setup`, install missing packages

### 3. Hardware/Device Errors
- **Symptoms**: Device not found, connection failures
- **Category**: `device` or `connection`
- **Handling**: Check physical connections, install drivers

### 4. File System Errors
- **Symptoms**: File not found, permission denied
- **Category**: `file` or `permission`
- **Handling**: Verify paths, check permissions

### 5. Runtime Errors
- **Symptoms**: Crashes, unexpected behavior
- **Category**: `general` or `job`
- **Handling**: Check logs, use recovery commands

## Debug Mode Usage

For detailed error information, use debug mode:

```bash
# Enable debug logging
plotty --debug <command>

# Example with debug:
plotty --debug add job test file.svg

# Check debug logs
tail -f ~/.local/share/plotty/logs/plotty.log | grep DEBUG
```

## Getting Help

When encountering errors not covered here:

1. **Check the logs**:
   ```bash
   tail -50 ~/.local/share/plotty/logs/plotty.log
   ```

2. **Run system check**:
   ```bash
   plotty check self --verbose
   ```

3. **Get system information**:
   ```bash
   plotty info system --json
   ```

4. **Report issues**:
   - Include error message
   - Include debug logs
   - Include system information
   - Include steps to reproduce