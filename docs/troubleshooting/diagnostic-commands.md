# Diagnostic Commands Guide

This guide provides comprehensive diagnostic commands for troubleshooting ploTTY issues, organized by system component and problem type.

## System Health Diagnostics

### Basic System Check
```bash
# Comprehensive health check
plotty check self

# Component-specific checks
plotty check camera
plotty check servo
plotty check timing
plotty check ready

# Verbose health check with details
plotty check self --verbose
```

### System Information
```bash
# Basic system information
plotty info system

# JSON output for scripting
plotty info system --json

# CSV output for spreadsheets
plotty info system --csv

# Detailed system status
plotty info system --verbose
```

## Job Management Diagnostics

### Queue Status
```bash
# Check all jobs in queue
plotty info queue

# Filter by state
plotty info queue --state plotting
plotty info queue --state failed
plotty info queue --state completed

# Show recent jobs
plotty info queue --recent 10

# Queue with timestamps
plotty info queue --timestamps
```

### Job Details
```bash
# Basic job information
plotty info job <job_id>

# Detailed job information
plotty info job <job_id> --verbose

# Show job history
plotty info job <job_id> --history

# Show job layers
plotty info job <job_id> --layers

# Show job metadata
plotty info job <job_id> --metadata
```

### Job State Analysis
```bash
# List all jobs with states
plotty list jobs --with-states

# Filter by specific state
plotty list jobs --state plotting
plotty list jobs --state failed
plotty list jobs --state completed

# Show job transitions
plotty info job <job_id> --transitions

# Show job journal
cat ~/.local/share/plotty/workspace/jobs/<job_id>/journal.jsonl
```

## Device Diagnostics

### AxiDraw/Plotter Diagnostics
```bash
# Test plotter connection
plotty check servo

# Test plotter movement
plotty check servo --test-movement

# Check device detection
plotty check servo --detect-devices

# Test with specific device
plotty check servo --device /dev/ttyUSB0

# Show device information
plotty info system | grep -A 10 device
```

### Camera Diagnostics
```bash
# Test camera connection
plotty check camera

# Test camera stream
plotty check camera --test-stream

# Check camera service
plotty check camera --service-status

# Test camera URL
curl -I http://127.0.0.1:8881/stream.mjpeg

# Show camera configuration
plotty info system | grep -A 10 camera
```

### Multi-pen System Diagnostics
```bash
# List available pens
plotty list pens

# Check pen mapping
plotty info job <job_id> --pen-mapping

# Test pen swap system
plotty check ready --pen-test

# Validate pen configuration
plotty list pens --validate
```

## Database Diagnostics

### Database Connection
```bash
# Test database connection
sqlite3 ~/.local/share/plotty/plotty.db ".tables"

# Check database integrity
sqlite3 ~/.local/share/plotty/plotty.db "PRAGMA integrity_check;"

# Check database size
ls -lh ~/.local/share/plotty/plotty.db

# Check database locks
lsof ~/.local/share/plotty/plotty.db
```

### Database Content
```bash
# Count jobs in database
sqlite3 ~/.local/share/plotty/plotty.db "SELECT COUNT(*) FROM jobs;"

# Show recent jobs
sqlite3 ~/.local/share/plotty/plotty.db "SELECT id, state, created_at FROM jobs ORDER BY created_at DESC LIMIT 10;"

# Check failed jobs
sqlite3 ~/.local/share/plotty/plotty.db "SELECT id, error_message FROM jobs WHERE state = 'FAILED';"

# Database schema
sqlite3 ~/.local/share/plotty/plotty.db ".schema"
```

## Configuration Diagnostics

### Configuration Validation
```bash
# Check configuration syntax
python -c "import yaml; yaml.safe_load(open('~/.config/plotty/config.yaml'))"

# Validate configuration schema
plotty info system --validate-config

# Show configuration
plotty info system --show-config

# Check specific configuration sections
plotty info system | grep -A 5 workspace
plotty info system | grep -A 5 database
plotty info system | grep -A 5 device
```

### Configuration Paths
```bash
# Show configuration file location
echo $PLOTTY_CONFIG
# Or default location:
ls -la ~/.config/plotty/config.yaml

# Check workspace path
plotty info system | grep workspace

# Verify workspace structure
tree ~/.local/share/plotty/workspace/

# Check workspace permissions
ls -la ~/.local/share/plotty/workspace/
```

## Performance Diagnostics

### Resource Usage
```bash
# Monitor ploTTY processes
ps aux | grep plotty

# Monitor memory usage
watch -n 1 'ps aux | grep plotty | grep -v grep'

# Check disk usage
du -sh ~/.local/share/plotty/

# Monitor disk space
df -h ~/.local/share/plotty/

# Check I/O usage
iotop -p $(pgrep -f plotty)
```

### Performance Metrics
```bash
# Check plotting performance
plotty stats performance

# Job completion times
plotty stats jobs --timing

# System performance summary
plotty stats summary

# Performance by job type
plotty stats jobs --by-type
```

## Log Analysis

### Real-time Log Monitoring
```bash
# Follow main log file
tail -f ~/.local/share/plotty/logs/plotty.log

# Follow error logs
tail -f ~/.local/share/plotty/logs/plotty.log | grep ERROR

# Follow warning logs
tail -f ~/.local/share/plotty/logs/plotty.log | grep WARNING

# Multi-level monitoring
tail -f ~/.local/share/plotty/logs/plotty.log | grep -E "(ERROR|WARNING|CRITICAL)"
```

### Historical Log Analysis
```bash
# Recent errors
tail -100 ~/.local/share/plotty/logs/plotty.log | grep ERROR

# Error count by type
grep ERROR ~/.local/share/plotty/logs/plotty.log | cut -d' ' -f4- | sort | uniq -c

# Warnings in last hour
find ~/.local/share/plotty/logs/ -name "*.log" -mmin -60 -exec grep WARNING {} \;

# Log file rotation status
ls -la ~/.local/share/plotty/logs/

# Compressed old logs
find ~/.local/share/plotty/logs/ -name "*.log.*" -exec gzip {} \;
```

### Job Journal Analysis
```bash
# List all job journals
find ~/.local/share/plotty/workspace/jobs -name "journal.jsonl"

# Analyze specific job journal
cat ~/.local/share/plotty/workspace/jobs/<job_id>/journal.jsonl | jq .

# Find interrupted jobs
grep -l "emergency_shutdown" ~/.local/share/plotty/workspace/jobs/*/journal.jsonl

# Job transition history
cat ~/.local/share/plotty/workspace/jobs/<job_id>/journal.jsonl | grep "state_change"

# Hook execution results
cat ~/.local/share/plotty/workspace/jobs/<job_id>/journal.jsonl | grep "hooks_executed"
```

## Network and Service Diagnostics

### Network Connectivity
```bash
# Test camera stream connectivity
curl -v http://127.0.0.1:8881/stream.mjpeg

# Check network latency
ping -c 3 127.0.0.1

# Test port availability
netstat -tlnp | grep :8881

# Check service status
systemctl status motion
systemctl status network
```

### Service Dependencies
```bash
# Check required services
systemctl status motion
systemctl status avahi-daemon

# Check USB devices
lsusb
dmesg | grep -i usb

# Check serial devices
ls -la /dev/ttyUSB* /dev/ttyACM*
dmesg | grep -i tty
```

## Recovery Diagnostics

### Crash Recovery
```bash
# Check for interrupted jobs
plotty info queue --interrupted

# Show resumable jobs
plotty info queue --resumable

# Check crash recovery status
find ~/.local/share/plotty/workspace/jobs -name "journal.jsonl" -exec grep -l "emergency_shutdown" {} \;

# Analyze crash patterns
grep "emergency_shutdown" ~/.local/share/plotty/workspace/jobs/*/journal.jsonl | cut -d'"' -f8 | sort | uniq -c
```

### Data Integrity
```bash
# Check workspace integrity
find ~/.local/share/plotty/workspace/jobs -name "job.json" -exec python -c "import json; json.load(open('{}'))" \;

# Validate job files
for job in ~/.local/share/plotty/workspace/jobs/*/; do
    if [ -f "$job/job.json" ]; then
        echo "Validating $(basename $job)"
        python -c "import json; json.load(open('$job/job.json'))" && echo "OK" || echo "INVALID"
    fi
done

# Check for corrupted journals
find ~/.local/share/plotty/workspace/jobs -name "journal.jsonl" -exec python -c "
import json
import sys
try:
    with open('{}') as f:
        for line in f:
            if line.strip():
                json.loads(line)
    print('{}: OK'.format('{}'))
except:
    print('{}: CORRUPTED'.format('{}'))
" \;
```

## Advanced Diagnostics

### Debug Mode Operations
```bash
# Run commands with debug output
plotty --debug check self
plotty --debug info system
plotty --debug list jobs

# Enable debug logging
export PLOTTY_LOG_LEVEL=DEBUG
plotty check self

# Debug specific components
plotty --debug --component fsm check self
plotty --debug --component device check servo
```

### System Integration Tests
```bash
# Test complete workflow
plotty --debug add job test_diagnostics /path/to/test.svg
plotty info job test_diagnostics
plotty restart test_diagnostics

# Test all components
for component in camera servo timing ready; do
    echo "Testing $component..."
    plotty check $component
done

# Stress test
for i in {1..10}; do
    plotty add job stress_test_$i /path/to/test.svg &
done
wait
plotty info queue
```

## Automation Scripts

### Health Check Script
```bash
#!/bin/bash
# ploddy_health_check.sh

echo "=== ploTTY Health Check ==="
echo "Timestamp: $(date)"
echo

# System check
echo "1. System Health:"
plotty check self
echo

# Queue status
echo "2. Queue Status:"
plotty info queue --recent 5
echo

# Device status
echo "3. Device Status:"
plotty check servo
plotty check camera
echo

# Disk space
echo "4. Disk Usage:"
df -h ~/.local/share/plotty/
echo

# Recent errors
echo "5. Recent Errors:"
tail -10 ~/.local/share/plotty/logs/plotty.log | grep ERROR || echo "No recent errors"
echo

echo "=== Health Check Complete ==="
```

### Diagnostic Report Script
```bash
#!/bin/bash
# ploddy_diagnostics.sh

REPORT_FILE="/tmp/plotty_diagnostics_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "ploTTY Diagnostic Report"
    echo "Generated: $(date)"
    echo "========================="
    echo

    echo "SYSTEM INFORMATION:"
    echo "------------------"
    plotty info system --json
    echo

    echo "QUEUE STATUS:"
    echo "-------------"
    plotty info queue
    echo

    echo "DEVICE STATUS:"
    echo "-------------"
    plotty check servo
    plotty check camera
    echo

    echo "RECENT ERRORS:"
    echo "--------------"
    tail -20 ~/.local/share/plotty/logs/plotty.log | grep ERROR || echo "No recent errors"
    echo

    echo "DISK USAGE:"
    echo "-----------"
    du -sh ~/.local/share/plotty/
    df -h ~/.local/share/plotty/
    echo

    echo "CONFIGURATION:"
    echo "-------------"
    cat ~/.config/plotty/config.yaml
} > "$REPORT_FILE"

echo "Diagnostic report saved to: $REPORT_FILE"
```

## Quick Reference Commands

```bash
# Essential diagnostic commands
plotty check self              # Full system health check
plotty info system             # System information
plotty info queue              # Queue status
plotty info job <id>           # Job details

# Device checks
plotty check servo             # Test plotter
plotty check camera            # Test camera

# Log analysis
tail -f ~/.local/share/plotty/logs/plotty.log    # Follow logs
grep ERROR ~/.local/share/plotty/logs/plotty.log  # Find errors

# Database checks
sqlite3 ~/.local/share/plotty/plotty.db ".tables"  # Database structure
sqlite3 ~/.local/share/plotty/plotty.db "SELECT COUNT(*) FROM jobs;"  # Job count

# Performance
ps aux | grep plotty          # Running processes
du -sh ~/.local/share/plotty/  # Disk usage
```

This diagnostic guide provides comprehensive tools for identifying, analyzing, and resolving ploTTY issues across all system components.