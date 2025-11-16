# Diagnostic Commands Guide

This guide provides comprehensive diagnostic commands for troubleshooting vfab issues, organized by system component and problem type.

## System Health Diagnostics

### Basic System Check
```bash
# Comprehensive health check
vfab check self

# Component-specific checks
vfab check camera
vfab driver test axidraw
vfab check ready

# Verbose health check with details
vfab check self --verbose
```

### System Information
```bash
# Basic system information
vfab info system

# JSON output for scripting
vfab info system --json

# CSV output for spreadsheets
vfab info system --csv

# Detailed system status
vfab info system --verbose
```

## Job Management Diagnostics

### Queue Status
```bash
# Check all jobs in queue
vfab info queue

# Filter by state
vfab info queue --state plotting
vfab info queue --state failed
vfab info queue --state completed

# Show recent jobs
vfab info queue --recent 10

# Queue with timestamps
vfab info queue --timestamps
```

### Job Details
```bash
# Basic job information
vfab info job <job_id>

# Detailed job information
vfab info job <job_id> --verbose

# Show job history
vfab info job <job_id> --history

# Show job layers
vfab info job <job_id> --layers

# Show job metadata
vfab info job <job_id> --metadata
```

### Job State Analysis
```bash
# List all jobs with states
vfab list jobs --with-states

# Filter by specific state
vfab list jobs --state plotting
vfab list jobs --state failed
vfab list jobs --state completed

# Show job transitions
vfab info job <job_id> --transitions

# Show job journal
cat ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl
```

## Device Diagnostics

### AxiDraw/Plotter Diagnostics
```bash
# Test plotter connection
vfab driver test axidraw

# Test plotter movement
vfab driver test axidraw

# Check device detection
vfab driver test axidraw

# Test with specific device
vfab driver test axidraw

# Show device information
vfab info system | grep -A 10 device
```

### Camera Diagnostics
```bash
# Test camera connection
vfab check camera

# Test camera stream
vfab check camera --test-stream

# Check camera service
vfab check camera --service-status

# Test camera URL
curl -I http://127.0.0.1:8881/stream.mjpeg

# Show camera configuration
vfab info system | grep -A 10 camera
```

### Multi-pen System Diagnostics
```bash
# List available pens
vfab list pens

# Check pen mapping
vfab info job <job_id> --pen-mapping

# Test pen swap system
vfab check ready --pen-test

# Validate pen configuration
vfab list pens --validate
```

## Database Diagnostics

### Database Connection
```bash
# Test database connection
sqlite3 ~/.local/share/vfab/vfab.db ".tables"

# Check database integrity
sqlite3 ~/.local/share/vfab/vfab.db "PRAGMA integrity_check;"

# Check database size
ls -lh ~/.local/share/vfab/vfab.db

# Check database locks
lsof ~/.local/share/vfab/vfab.db
```

### Database Content
```bash
# Count jobs in database
sqlite3 ~/.local/share/vfab/vfab.db "SELECT COUNT(*) FROM jobs;"

# Show recent jobs
sqlite3 ~/.local/share/vfab/vfab.db "SELECT id, state, created_at FROM jobs ORDER BY created_at DESC LIMIT 10;"

# Check failed jobs
sqlite3 ~/.local/share/vfab/vfab.db "SELECT id, error_message FROM jobs WHERE state = 'FAILED';"

# Database schema
sqlite3 ~/.local/share/vfab/vfab.db ".schema"
```

## Configuration Diagnostics

### Configuration Validation
```bash
# Check configuration syntax
python -c "import yaml; yaml.safe_load(open('~/.config/vfab/config.yaml'))"

# Validate configuration schema
vfab info system --validate-config

# Show configuration
vfab info system --show-config

# Check specific configuration sections
vfab info system | grep -A 5 workspace
vfab info system | grep -A 5 database
vfab info system | grep -A 5 device
```

### Configuration Paths
```bash
# Show configuration file location
echo $PLOTTY_CONFIG
# Or default location:
ls -la ~/.config/vfab/config.yaml

# Check workspace path
vfab info system | grep workspace

# Verify workspace structure
tree ~/.local/share/vfab/workspace/

# Check workspace permissions
ls -la ~/.local/share/vfab/workspace/
```

## Performance Diagnostics

### Resource Usage
```bash
# Monitor vfab processes
ps aux | grep vfab

# Monitor memory usage
watch -n 1 'ps aux | grep vfab | grep -v grep'

# Check disk usage
du -sh ~/.local/share/vfab/

# Monitor disk space
df -h ~/.local/share/vfab/

# Check I/O usage
iotop -p $(pgrep -f vfab)
```

### Performance Metrics
```bash
# Check plotting performance
vfab stats performance

# Job completion times
vfab stats jobs --timing

# System performance summary
vfab stats summary

# Performance by job type
vfab stats jobs --by-type
```

## Log Analysis

### Real-time Log Monitoring
```bash
# Follow main log file
tail -f ~/.local/share/vfab/logs/vfab.log

# Follow error logs
tail -f ~/.local/share/vfab/logs/vfab.log | grep ERROR

# Follow warning logs
tail -f ~/.local/share/vfab/logs/vfab.log | grep WARNING

# Multi-level monitoring
tail -f ~/.local/share/vfab/logs/vfab.log | grep -E "(ERROR|WARNING|CRITICAL)"
```

### Historical Log Analysis
```bash
# Recent errors
tail -100 ~/.local/share/vfab/logs/vfab.log | grep ERROR

# Error count by type
grep ERROR ~/.local/share/vfab/logs/vfab.log | cut -d' ' -f4- | sort | uniq -c

# Warnings in last hour
find ~/.local/share/vfab/logs/ -name "*.log" -mmin -60 -exec grep WARNING {} \;

# Log file rotation status
ls -la ~/.local/share/vfab/logs/

# Compressed old logs
find ~/.local/share/vfab/logs/ -name "*.log.*" -exec gzip {} \;
```

### Job Journal Analysis
```bash
# List all job journals
find ~/.local/share/vfab/workspace/jobs -name "journal.jsonl"

# Analyze specific job journal
cat ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl | jq .

# Find interrupted jobs
grep -l "emergency_shutdown" ~/.local/share/vfab/workspace/jobs/*/journal.jsonl

# Job transition history
cat ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl | grep "state_change"

# Hook execution results
cat ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl | grep "hooks_executed"
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
vfab info queue --interrupted

# Show resumable jobs
vfab info queue --resumable

# Check crash recovery status
find ~/.local/share/vfab/workspace/jobs -name "journal.jsonl" -exec grep -l "emergency_shutdown" {} \;

# Analyze crash patterns
grep "emergency_shutdown" ~/.local/share/vfab/workspace/jobs/*/journal.jsonl | cut -d'"' -f8 | sort | uniq -c
```

### Data Integrity
```bash
# Check workspace integrity
find ~/.local/share/vfab/workspace/jobs -name "job.json" -exec python -c "import json; json.load(open('{}'))" \;

# Validate job files
for job in ~/.local/share/vfab/workspace/jobs/*/; do
    if [ -f "$job/job.json" ]; then
        echo "Validating $(basename $job)"
        python -c "import json; json.load(open('$job/job.json'))" && echo "OK" || echo "INVALID"
    fi
done

# Check for corrupted journals
find ~/.local/share/vfab/workspace/jobs -name "journal.jsonl" -exec python -c "
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
vfab --debug check self
vfab --debug info system
vfab --debug list jobs

# Enable debug logging
export PLOTTY_LOG_LEVEL=DEBUG
vfab check self

# Debug specific components
vfab --debug --component fsm check self
vfab --debug --component device check servo
```

### System Integration Tests
```bash
# Test complete workflow
vfab --debug add job test_diagnostics /path/to/test.svg
vfab info job test_diagnostics
vfab restart test_diagnostics

# Test all components
for component in camera servo timing ready; do
    echo "Testing $component..."
    vfab check $component
done

# Stress test
for i in {1..10}; do
    vfab add job stress_test_$i /path/to/test.svg &
done
wait
vfab info queue
```

## Automation Scripts

### Health Check Script
```bash
#!/bin/bash
# ploddy_health_check.sh

echo "=== vfab Health Check ==="
echo "Timestamp: $(date)"
echo

# System check
echo "1. System Health:"
vfab check self
echo

# Queue status
echo "2. Queue Status:"
vfab info queue --recent 5
echo

# Device status
echo "3. Device Status:"
vfab driver test axidraw
vfab check camera
echo

# Disk space
echo "4. Disk Usage:"
df -h ~/.local/share/vfab/
echo

# Recent errors
echo "5. Recent Errors:"
tail -10 ~/.local/share/vfab/logs/vfab.log | grep ERROR || echo "No recent errors"
echo

echo "=== Health Check Complete ==="
```

### Diagnostic Report Script
```bash
#!/bin/bash
# ploddy_diagnostics.sh

REPORT_FILE="/tmp/vfab_diagnostics_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "vfab Diagnostic Report"
    echo "Generated: $(date)"
    echo "========================="
    echo

    echo "SYSTEM INFORMATION:"
    echo "------------------"
    vfab info system --json
    echo

    echo "QUEUE STATUS:"
    echo "-------------"
    vfab info queue
    echo

    echo "DEVICE STATUS:"
    echo "-------------"
    vfab check servo
    vfab check camera
    echo

    echo "RECENT ERRORS:"
    echo "--------------"
    tail -20 ~/.local/share/vfab/logs/vfab.log | grep ERROR || echo "No recent errors"
    echo

    echo "DISK USAGE:"
    echo "-----------"
    du -sh ~/.local/share/vfab/
    df -h ~/.local/share/vfab/
    echo

    echo "CONFIGURATION:"
    echo "-------------"
    cat ~/.config/vfab/config.yaml
} > "$REPORT_FILE"

echo "Diagnostic report saved to: $REPORT_FILE"
```

## Quick Reference Commands

```bash
# Essential diagnostic commands
vfab check self              # Full system health check
vfab info system             # System information
vfab info queue              # Queue status
vfab info job <id>           # Job details

# Device checks
vfab driver test axidraw     # Test plotter
vfab check camera            # Test camera

# Log analysis
tail -f ~/.local/share/vfab/logs/vfab.log    # Follow logs
grep ERROR ~/.local/share/vfab/logs/vfab.log  # Find errors

# Database checks
sqlite3 ~/.local/share/vfab/vfab.db ".tables"  # Database structure
sqlite3 ~/.local/share/vfab/vfab.db "SELECT COUNT(*) FROM jobs;"  # Job count

# Performance
ps aux | grep vfab          # Running processes
du -sh ~/.local/share/vfab/  # Disk usage
```

This diagnostic guide provides comprehensive tools for identifying, analyzing, and resolving vfab issues across all system components.