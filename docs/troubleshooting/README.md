# ploTTY Troubleshooting Guide

This guide extracts common issues, error patterns, and troubleshooting scenarios from the ploTTY test suite and codebase analysis. It provides practical solutions for diagnosing and resolving problems users may encounter.

## Table of Contents

1. [Common Test Failures and Root Causes](#common-test-failures-and-root-causes)
2. [Error Handling Patterns](#error-handling-patterns)
3. [Device Integration Issues](#device-integration-issues)
4. [Database and Configuration Problems](#database-and-configuration-problems)
5. [Recovery and Crash Scenarios](#recovery-and-crash-scenarios)
6. [Edge Cases and Boundary Conditions](#edge-cases-and-boundary-conditions)
7. [Diagnostic Commands](#diagnostic-commands)
8. [Preventive Measures](#preventive-measures)

---

## Common Test Failures and Root Causes

### 1. Module Import and Mocking Issues

**Symptoms:**
- `AttributeError: module 'plotty.cli.add' does not have the attribute 'load_config'`
- Test failures related to missing module attributes
- Mock patching failures

**Root Causes:**
- Tests expecting functions that have been moved or refactored
- Incorrect import paths in test mocking
- Module structure changes not reflected in tests

**Solutions:**
```bash
# Check actual module structure
find src/plotty -name "*.py" | xargs grep -l "load_config"

# Update test imports to match current structure
# Use proper import paths like:
from plotty.config import load_config
```

### 2. CLI Command Structure Issues

**Symptoms:**
- `List subcommand 'paper' should exist` errors
- Missing subcommands in help output
- Exit code 2 for valid commands

**Root Causes:**
- Incomplete CLI command implementation
- Missing subcommand registration
- Typer configuration issues

**Solutions:**
```bash
# Check available commands
plotty --help
plotty list --help

# Verify subcommand implementation exists
ls -la src/plotty/cli/list/
```

### 3. Workspace and Directory Issues

**Symptoms:**
- `No jobs directory found` errors
- File not found errors in tests
- Path resolution failures

**Root Causes:**
- Missing workspace initialization
- Incorrect workspace configuration
- Permission issues

**Solutions:**
```bash
# Initialize workspace
plotty setup

# Check workspace configuration
plotty info system

# Verify directory structure
ls -la ~/.local/share/plotty/workspace/jobs/
```

---

## Error Handling Patterns

### 1. Custom Error Hierarchy

ploTTY uses a structured error system with specific error types:

```python
# Base error with user-friendly messages
PlottyError(message, suggestion=None, technical=None, category="general")

# Specialized error types
JobError(message, job_id=None)           # Job-related issues
DeviceError(message, device_type="AxiDraw") # Hardware issues  
ConfigError(message, config_file=None)     # Configuration problems
ValidationError(message, expected_format=None) # Input validation
```

### 2. Common Error Categories and Solutions

#### File/Path Errors
```bash
# Error: File not found
plotty add job test /nonexistent/file.svg

# Solution: Check file exists and is readable
ls -la /path/to/file.svg
file /path/to/file.svg
```

#### Permission Errors
```bash
# Error: Permission denied
# Solution: Check permissions and ownership
ls -la ~/.local/share/plotty/
chmod -R u+rw ~/.local/share/plotty/
```

#### Configuration Errors
```bash
# Error: Config invalid
# Solution: Validate and recreate config
plotty check self
plotty setup
```

#### Device Connection Errors
```bash
# Error: Device not connected
# Solution: Check AxiDraw connection
plotty check servo
plotty check camera
ls -la /dev/ttyUSB* /dev/ttyACM*
```

---

## Device Integration Issues

### 1. AxiDraw Connection Problems

**Symptoms:**
- `ImportError: AxiDraw support not available`
- `Device not connected` errors
- Plotting failures

**Diagnostic Steps:**
```bash
# Check AxiDraw installation
python -c "import axidraw; print('AxiDraw available')"

# Check device detection
lsusb | grep -i axidraw
dmesg | grep -i tty

# Test device connection
plotty check servo
```

**Solutions:**
```bash
# Install AxiDraw support
uv pip install -e ".[axidraw]"

# Check device permissions
sudo usermod -a -G dialout $USER
# Logout and login again

# Test with specific device
plotty add job test file.svg --device /dev/ttyUSB0
```

### 2. Camera Integration Issues

**Symptoms:**
- Camera connection failures
- Motion detection not working
- Timelapse failures

**Diagnostic Steps:**
```bash
# Check camera configuration
plotty check camera

# Test camera URL
curl -I http://127.0.0.1:8881/stream.mjpeg

# Check motion service
systemctl status motion
```

**Solutions:**
```bash
# Update camera configuration
plotty setup
# Or edit config.yaml:
camera:
  enabled: true
  url: "http://127.0.0.1:8881/stream.mjpeg"
  mode: "ip"
```

### 3. Multi-pen System Issues

**Symptoms:**
- Pen swap failures
- Incorrect pen mapping
- Layer detection problems

**Diagnostic Steps:**
```bash
# Check pen configuration
plotty list pens

# Validate pen mapping
plotty info job <job_id>

# Test pen swap system
plotty check ready
```

**Solutions:**
```bash
# Configure pen mapping
plotty add pen "0.3mm black" --width 0.3 --color "#000000"

# Validate SVG layers
plotty info job <job_id> --show-layers
```

---

## Database and Configuration Problems

### 1. Database Connection Issues

**Symptoms:**
- Database lock errors
- Connection refused
- Migration failures

**Diagnostic Steps:**
```bash
# Check database location
plotty info system | grep database

# Test database access
sqlite3 ~/.local/share/plotty/plotty.db ".tables"

# Check database permissions
ls -la ~/.local/share/plotty/plotty.db
```

**Solutions:**
```bash
# Reinitialize database
rm ~/.local/share/plotty/plotty.db
plotty setup

# Run migrations
uv run alembic upgrade head

# Check database configuration
cat ~/.config/plotty/config.yaml | grep database
```

### 2. Configuration File Issues

**Symptoms:**
- YAML parsing errors
- Invalid configuration values
- Missing configuration sections

**Diagnostic Steps:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('~/.config/plotty/config.yaml'))"

# Check configuration schema
plotty info system

# Test configuration loading
python -c "from plotty.config import load_config; print(load_config())"
```

**Solutions:**
```bash
# Recreate configuration
plotty setup

# Backup and reset config
mv ~/.config/plotty/config.yaml ~/.config/plotty/config.yaml.backup
plotty setup

# Manual configuration check
cat ~/.config/plotty/config.yaml
```

### 3. Workspace Issues

**Symptoms:**
- Job creation failures
- File permission errors
- Missing directories

**Diagnostic Steps:**
```bash
# Check workspace structure
tree ~/.local/share/plotty/workspace/

# Verify permissions
ls -la ~/.local/share/plotty/workspace/

# Check disk space
df -h ~/.local/share/plotty/
```

**Solutions:**
```bash
# Reinitialize workspace
rm -rf ~/.local/share/plotty/workspace/
plotty setup

# Fix permissions
chmod -R u+rw ~/.local/share/plotty/workspace/

# Create missing directories
mkdir -p ~/.local/share/plotty/workspace/jobs
```

---

## Recovery and Crash Scenarios

### 1. Job Recovery After Crash

**Symptoms:**
- Jobs stuck in PLOTTING state
- Interrupted plots
- Journal corruption

**Diagnostic Steps:**
```bash
# Check for interrupted jobs
plotty info queue

# Check job status
plotty info job <job_id>

# Examine journal files
cat ~/.local/share/plotty/workspace/jobs/<job_id>/journal.jsonl
```

**Recovery Commands:**
```bash
# Resume interrupted jobs
plotty resume

# Check resumable jobs
plotty list jobs --state interrupted

# Force job state change
plotty restart <job_id>
```

### 2. Emergency Shutdown Recovery

**Symptoms:**
- Jobs with emergency_shutdown in journal
- Incomplete state transitions
- Guard system failures

**Recovery Process:**
```bash
# Identify crashed jobs
find ~/.local/share/plotty/workspace/jobs -name "journal.jsonl" -exec grep -l "emergency_shutdown" {} \;

# Manual recovery
plotty recovery <job_id>

# Clean up corrupted journals
plotty cleanup --job <job_id>
```

### 3. State Machine Corruption

**Symptoms:**
- Invalid state transitions
- Jobs stuck in non-terminal states
- FSM initialization failures

**Solutions:**
```bash
# Reset job state
plotty remove job <job_id> --force
plotty add job <job_id> <file.svg>

# Validate state transitions
plotty check job <job_id>

# Reset entire system (last resort)
rm -rf ~/.local/share/plotty/workspace/
plotty setup
```

---

## Edge Cases and Boundary Conditions

### 1. Large File Handling

**Issues:**
- Memory exhaustion with large SVG files
- Timeout during optimization
- Disk space issues

**Solutions:**
```bash
# Check file size before processing
ls -lh large_file.svg

# Use appropriate optimization level
plotty add job large_job large_file.svg --optimization fast

# Monitor disk space
df -h ~/.local/share/plotty/workspace/

# Split large jobs if needed
# Use external tools to split SVG into smaller files
```

### 2. Concurrent Access Issues

**Issues:**
- Database locking
- Job queue conflicts
- Resource contention

**Solutions:**
```bash
# Check for active processes
ps aux | grep plotty

# Wait for completion
plotty info queue

# Use job priorities
plotty add job urgent_job urgent.svg --priority high
```

### 3. Network and Service Dependencies

**Issues:**
- Camera service unavailable
- Remote device connection failures
- Service timeouts

**Solutions:**
```bash
# Check service status
systemctl status motion
systemctl status network

# Test network connectivity
ping -c 3 127.0.0.1
curl -I http://127.0.0.1:8881/stream.mjpeg

# Configure timeouts
plotty setup
# Edit config.yaml:
device:
  detection_timeout: 10
camera:
  test_access: true
```

---

## Diagnostic Commands

### System Health Check
```bash
# Comprehensive system check
plotty check self

# Component-specific checks
plotty check camera
plotty check servo  
plotty check timing
plotty check ready
```

### Information Gathering
```bash
# System information
plotty info system --json

# Queue status
plotty info queue --csv

# Job details
plotty info job <job_id> --verbose

# Available resources
plotty list pens
plotty list paper
plotty list presets
```

### Log Analysis
```bash
# Check application logs
tail -f ~/.local/share/plotty/logs/plotty.log

# Filter by error level
grep "ERROR" ~/.local/share/plotty/logs/plotty.log

# Analyze job journals
find ~/.local/share/plotty/workspace/jobs -name "journal.jsonl" -exec cat {} \;
```

### Performance Monitoring
```bash
# Monitor resource usage
watch -n 1 'ps aux | grep plotty'

# Check disk usage
du -sh ~/.local/share/plotty/

# Database performance
sqlite3 ~/.local/share/plotty/plotty.db ".schema"
sqlite3 ~/.local/share/plotty/plotty.db "SELECT COUNT(*) FROM jobs;"
```

---

## Preventive Measures

### 1. Regular Maintenance

**Weekly Tasks:**
```bash
# Clean up old journals
find ~/.local/share/plotty/workspace/jobs -name "journal.jsonl" -mtime +7 -delete

# Compact database
sqlite3 ~/.local/share/plotty/plotty.db "VACUUM;"

# Check disk space
df -h ~/.local/share/plotty/

# Backup configuration
cp ~/.config/plotty/config.yaml ~/.config/plotty/config.yaml.backup.$(date +%Y%m%d)
```

**Monthly Tasks:**
```bash
# Full system backup
plotty system export --output backup_$(date +%Y%m%d).tar.gz

# Clean up completed jobs
plotty remove job --state completed --older-than 30d

# Update dependencies
uv pip install -e ".[dev,vpype,axidraw]"
```

### 2. Configuration Best Practices

**File Organization:**
```yaml
# Use absolute paths in configuration
workspace: "/home/user/.local/share/plotty/workspace"
database:
  url: "sqlite:///home/user/.local/share/plotty/plotty.db"

# Set appropriate timeouts
device:
  detection_timeout: 10
camera:
  test_access: true
```

**Resource Management:**
```yaml
# Configure reasonable limits
optimization:
  default_level: "default"
  default_digest: 1

logging:
  max_file_size: 10485760  # 10MB
  backup_count: 5
```

### 3. Monitoring Setup

**Log Monitoring:**
```bash
# Set up log rotation
sudo nano /etc/logrotate.d/plotty
# Content:
~/.local/share/plotty/logs/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
```

**Health Checks:**
```bash
# Create a health check script
cat > ~/plotty_health.sh << 'EOF'
#!/bin/bash
echo "=== ploTTY Health Check ==="
plotty check self
echo "=== Disk Usage ==="
df -h ~/.local/share/plotty/
echo "=== Recent Errors ==="
tail -10 ~/.local/share/plotty/logs/plotty.log | grep ERROR
EOF

chmod +x ~/plotty_health.sh
```

### 4. Backup Strategy

**Automated Backups:**
```bash
# Create backup script
cat > ~/backup_plotty.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/plotty"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration
cp ~/.config/plotty/config.yaml $BACKUP_DIR/config_$DATE.yaml

# Backup database
cp ~/.local/share/plotty/plotty.db $BACKUP_DIR/plotty_$DATE.db

# Backup workspace (compressed)
tar -czf $BACKUP_DIR/workspace_$DATE.tar.gz ~/.local/share/plotty/workspace/

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.yaml" -mtime +7 -delete
find $BACKUP_DIR -name "*.db" -mtime +7 -delete  
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x ~/backup_plotty.sh

# Add to crontab for daily execution
crontab -e
# Add: 0 2 * * * /home/user/backup_plotty.sh
```

---

## Quick Reference

### Common Error Messages and Solutions

| Error Message | Cause | Solution |
|---|---|---|
| `File not found` | Incorrect file path | Verify file exists with `ls -la` |
| `Permission denied` | File/directory permissions | Use `chmod` or check ownership |
| `Device not connected` | AxiDraw not detected | Check USB connection and permissions |
| `Config invalid` | YAML syntax error | Validate with `python -c "import yaml; yaml.safe_load(...)"` |
| `Database locked` | Concurrent access | Wait for other processes to complete |
| `Job stuck in PLOTTING` | Crash/interrupt | Use `plotty resume` or `plotty restart` |
| `Camera not accessible` | Network/service issue | Check URL and service status |
| `Invalid state transition` | FSM state error | Check current state with `plotty info job` |

### Essential Commands

```bash
# System setup
plotty setup                    # Initialize configuration
plotty check self               # System health check

# Job management  
plotty add job <name> <file>    # Add new job
plotty list jobs                 # List all jobs
plotty info job <id>            # Job details
plotty restart <id>             # Restart job

# Device checks
plotty check servo              # Test AxiDraw
plotty check camera             # Test camera
plotty check ready              # Check all systems

# Recovery
plotty resume                   # Resume interrupted jobs
plotty info queue              # Check queue status
```

### File Locations

```
Configuration: ~/.config/plotty/config.yaml
Database:     ~/.local/share/plotty/plotty.db  
Workspace:    ~/.local/share/plotty/workspace/
Logs:         ~/.local/share/plotty/logs/plotty.log
```

This troubleshooting guide is based on comprehensive analysis of the ploTTY test suite, covering real-world scenarios and solutions extracted from test failures, error handling patterns, and recovery mechanisms.