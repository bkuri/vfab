# vfab Troubleshooting Guide

This guide extracts common issues, error patterns, and troubleshooting scenarios from the vfab test suite and codebase analysis. It provides practical solutions for diagnosing and resolving problems users may encounter.

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
- `AttributeError: module 'vfab.cli.add' does not have the attribute 'load_config'`
- Test failures related to missing module attributes
- Mock patching failures

**Root Causes:**
- Tests expecting functions that have been moved or refactored
- Incorrect import paths in test mocking
- Module structure changes not reflected in tests

**Solutions:**
```bash
# Check actual module structure
find src/vfab -name "*.py" | xargs grep -l "load_config"

# Update test imports to match current structure
# Use proper import paths like:
from vfab.config import load_config
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
vfab --help
vfab list --help

# Verify subcommand implementation exists
ls -la src/vfab/cli/list/
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
vfab setup

# Check workspace configuration
vfab info system

# Verify directory structure
ls -la ~/.local/share/vfab/workspace/jobs/
```

---

## Error Handling Patterns

### 1. Custom Error Hierarchy

vfab uses a structured error system with specific error types:

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
vfab add job test /nonexistent/file.svg

# Solution: Check file exists and is readable
ls -la /path/to/file.svg
file /path/to/file.svg
```

#### Permission Errors
```bash
# Error: Permission denied
# Solution: Check permissions and ownership
ls -la ~/.local/share/vfab/
chmod -R u+rw ~/.local/share/vfab/
```

#### Configuration Errors
```bash
# Error: Config invalid
# Solution: Validate and recreate config
vfab check self
vfab setup
```

#### Device Connection Errors
```bash
# Error: Device not connected
# Solution: Check AxiDraw connection
vfab driver test axidraw
vfab check camera
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
vfab driver test axidraw
```

**Solutions:**
```bash
# Install AxiDraw support
uv pip install -e ".[axidraw]"

# Check device permissions
sudo usermod -a -G dialout $USER
# Logout and login again

# Test with specific device
vfab add job test file.svg --device /dev/ttyUSB0
```

### 2. Camera Integration Issues

**Symptoms:**
- Camera connection failures
- Motion detection not working
- Timelapse failures

**Diagnostic Steps:**
```bash
# Check camera configuration
vfab check camera

# Test camera URL
curl -I http://127.0.0.1:8881/stream.mjpeg

# Check motion service
systemctl status motion
```

**Solutions:**
```bash
# Update camera configuration
vfab setup
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
vfab list pens

# Validate pen mapping
vfab info job <job_id>

# Test pen swap system
vfab check ready
```

**Solutions:**
```bash
# Configure pen mapping
vfab add pen "0.3mm black" --width 0.3 --color "#000000"

# Validate SVG layers
vfab info job <job_id> --show-layers
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
vfab info system | grep database

# Test database access
sqlite3 ~/.local/share/vfab/vfab.db ".tables"

# Check database permissions
ls -la ~/.local/share/vfab/vfab.db
```

**Solutions:**
```bash
# Reinitialize database
rm ~/.local/share/vfab/vfab.db
vfab setup

# Run migrations
uv run alembic upgrade head

# Check database configuration
cat ~/.config/vfab/config.yaml | grep database
```

### 2. Configuration File Issues

**Symptoms:**
- YAML parsing errors
- Invalid configuration values
- Missing configuration sections

**Diagnostic Steps:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('~/.config/vfab/config.yaml'))"

# Check configuration schema
vfab info system

# Test configuration loading
python -c "from vfab.config import load_config; print(load_config())"
```

**Solutions:**
```bash
# Recreate configuration
vfab setup

# Backup and reset config
mv ~/.config/vfab/config.yaml ~/.config/vfab/config.yaml.backup
vfab setup

# Manual configuration check
cat ~/.config/vfab/config.yaml
```

### 3. Workspace Issues

**Symptoms:**
- Job creation failures
- File permission errors
- Missing directories

**Diagnostic Steps:**
```bash
# Check workspace structure
tree ~/.local/share/vfab/workspace/

# Verify permissions
ls -la ~/.local/share/vfab/workspace/

# Check disk space
df -h ~/.local/share/vfab/
```

**Solutions:**
```bash
# Reinitialize workspace
rm -rf ~/.local/share/vfab/workspace/
vfab setup

# Fix permissions
chmod -R u+rw ~/.local/share/vfab/workspace/

# Create missing directories
mkdir -p ~/.local/share/vfab/workspace/jobs
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
vfab info queue

# Check job status
vfab info job <job_id>

# Examine journal files
cat ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl
```

**Recovery Commands:**
```bash
# Resume interrupted jobs
vfab resume

# Check resumable jobs
vfab list jobs --state interrupted

# Force job state change
vfab restart <job_id>
```

### 2. Emergency Shutdown Recovery

**Symptoms:**
- Jobs with emergency_shutdown in journal
- Incomplete state transitions
- Guard system failures

**Recovery Process:**
```bash
# Identify crashed jobs
find ~/.local/share/vfab/workspace/jobs -name "journal.jsonl" -exec grep -l "emergency_shutdown" {} \;

# Manual recovery
vfab recovery <job_id>

# Clean up corrupted journals
vfab cleanup --job <job_id>
```

### 3. State Machine Corruption

**Symptoms:**
- Invalid state transitions
- Jobs stuck in non-terminal states
- FSM initialization failures

**Solutions:**
```bash
# Reset job state
vfab remove job <job_id> --force
vfab add job <job_id> <file.svg>

# Validate state transitions
vfab check job <job_id>

# Reset entire system (last resort)
rm -rf ~/.local/share/vfab/workspace/
vfab setup
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
vfab add job large_job large_file.svg --optimization fast

# Monitor disk space
df -h ~/.local/share/vfab/workspace/

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
ps aux | grep vfab

# Wait for completion
vfab info queue

# Use job priorities
vfab add job urgent_job urgent.svg --priority high
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
vfab setup
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
vfab check self

# Component-specific checks
vfab check camera
vfab driver test axidraw
vfab check ready
```

### Information Gathering
```bash
# System information
vfab info system --json

# Queue status
vfab info queue --csv

# Job details
vfab info job <job_id> --verbose

# Available resources
vfab list pens
vfab list paper
vfab list presets
```

### Log Analysis
```bash
# Check application logs
tail -f ~/.local/share/vfab/logs/vfab.log

# Filter by error level
grep "ERROR" ~/.local/share/vfab/logs/vfab.log

# Analyze job journals
find ~/.local/share/vfab/workspace/jobs -name "journal.jsonl" -exec cat {} \;
```

### Performance Monitoring
```bash
# Monitor resource usage
watch -n 1 'ps aux | grep vfab'

# Check disk usage
du -sh ~/.local/share/vfab/

# Database performance
sqlite3 ~/.local/share/vfab/vfab.db ".schema"
sqlite3 ~/.local/share/vfab/vfab.db "SELECT COUNT(*) FROM jobs;"
```

---

## Preventive Measures

### 1. Regular Maintenance

**Weekly Tasks:**
```bash
# Clean up old journals
find ~/.local/share/vfab/workspace/jobs -name "journal.jsonl" -mtime +7 -delete

# Compact database
sqlite3 ~/.local/share/vfab/vfab.db "VACUUM;"

# Check disk space
df -h ~/.local/share/vfab/

# Backup configuration
cp ~/.config/vfab/config.yaml ~/.config/vfab/config.yaml.backup.$(date +%Y%m%d)
```

**Monthly Tasks:**
```bash
# Full system backup
vfab system export --output backup_$(date +%Y%m%d).tar.gz

# Clean up completed jobs
vfab remove job --state completed --older-than 30d

# Update dependencies
uv pip install -e ".[dev,vpype,axidraw]"
```

### 2. Configuration Best Practices

**File Organization:**
```yaml
# Use absolute paths in configuration
workspace: "/home/user/.local/share/vfab/workspace"
database:
  url: "sqlite:///home/user/.local/share/vfab/vfab.db"

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
sudo nano /etc/logrotate.d/vfab
# Content:
~/.local/share/vfab/logs/*.log {
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
cat > ~/vfab_health.sh << 'EOF'
#!/bin/bash
echo "=== vfab Health Check ==="
vfab check self
echo "=== Disk Usage ==="
df -h ~/.local/share/vfab/
echo "=== Recent Errors ==="
tail -10 ~/.local/share/vfab/logs/vfab.log | grep ERROR
EOF

chmod +x ~/vfab_health.sh
```

### 4. Backup Strategy

**Automated Backups:**
```bash
# Create backup script
cat > ~/backup_vfab.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/vfab"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration
cp ~/.config/vfab/config.yaml $BACKUP_DIR/config_$DATE.yaml

# Backup database
cp ~/.local/share/vfab/vfab.db $BACKUP_DIR/vfab_$DATE.db

# Backup workspace (compressed)
tar -czf $BACKUP_DIR/workspace_$DATE.tar.gz ~/.local/share/vfab/workspace/

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.yaml" -mtime +7 -delete
find $BACKUP_DIR -name "*.db" -mtime +7 -delete  
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x ~/backup_vfab.sh

# Add to crontab for daily execution
crontab -e
# Add: 0 2 * * * /home/user/backup_vfab.sh
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
| `Job stuck in PLOTTING` | Crash/interrupt | Use `vfab resume` or `vfab restart` |
| `Camera not accessible` | Network/service issue | Check URL and service status |
| `Invalid state transition` | FSM state error | Check current state with `vfab info job` |

### Essential Commands

```bash
# System setup
vfab setup                    # Initialize configuration
vfab check self               # System health check

# Job management  
vfab add job <name> <file>    # Add new job
vfab list jobs                 # List all jobs
vfab info job <id>            # Job details
vfab restart <id>             # Restart job

# Device checks
vfab driver test axidraw      # Test AxiDraw
vfab check camera             # Test camera
vfab check ready              # Check all systems

# Recovery
vfab resume                   # Resume interrupted jobs
vfab info queue              # Check queue status
```

### File Locations

```
Configuration: ~/.config/vfab/config.yaml
Database:     ~/.local/share/vfab/vfab.db  
Workspace:    ~/.local/share/vfab/workspace/
Logs:         ~/.local/share/vfab/logs/vfab.log
```

This troubleshooting guide is based on comprehensive analysis of the vfab test suite, covering real-world scenarios and solutions extracted from test failures, error handling patterns, and recovery mechanisms.