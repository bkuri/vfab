# Recovery and Crash Scenarios

This guide covers recovery procedures, crash analysis, and preventive measures for handling system failures and interruptions in vfab.

## Table of Contents

1. [Types of Crashes and Interruptions](#types-of-crashes-and-interruptions)
2. [Immediate Recovery Procedures](#immediate-recovery-procedures)
3. [Journal Analysis and Recovery](#journal-analysis-and-recovery)
4. [State Machine Recovery](#state-machine-recovery)
5. [Data Recovery Procedures](#data-recovery-procedures)
6. [Crash Pattern Analysis](#crash-pattern-analysis)
7. [Preventive Measures](#preventive-measures)

---

## Types of Crashes and Interruptions

### 1. Signal-Based Interruptions

**Causes:**
- User pressing Ctrl+C
- System shutdown/restart
- Process termination
- Power failure

**Symptoms:**
- Jobs stuck in PLOTTING state
- `emergency_shutdown` entries in journals
- Incomplete state transitions

**Detection:**
```bash
# Find interrupted jobs
grep -l "emergency_shutdown" ~/.local/share/vfab/workspace/jobs/*/journal.jsonl

# Check signal handlers
vfab info system | grep -i signal

# Monitor for interrupted jobs
vfab info queue --interrupted
```

### 2. Hardware Failures

**Causes:**
- AxiDraw disconnection
- Camera service failure
- USB port issues
- Power loss to devices

**Symptoms:**
- Device connection errors
- Plotting stops mid-job
- Camera feed interruption

**Detection:**
```bash
# Check device status
vfab check servo
vfab check camera

# Check hardware logs
dmesg | grep -i usb
dmesg | grep -i tty

# Monitor device connections
watch -n 1 'lsusb | grep -i axidraw'
```

### 3. Software Crashes

**Causes:**
- Memory exhaustion
- Unhandled exceptions
- Database corruption
- Resource conflicts

**Symptoms:**
- Process termination
- Core dumps
- Database lock errors

**Detection:**
```bash
# Check for crashes
grep -i "crash\|error\|exception" ~/.local/share/vfab/logs/vfab.log

# Check system logs
journalctl -u vfab --since "1 hour ago"

# Monitor process health
ps aux | grep vfab
```

### 4. Resource Exhaustion

**Causes:**
- Disk space full
- Memory exhaustion
- Too many concurrent jobs
- Large file processing

**Symptoms:**
- "No space left on device" errors
- Out of memory errors
- Performance degradation

**Detection:**
```bash
# Check disk space
df -h ~/.local/share/vfab/

# Check memory usage
free -h
ps aux | grep vfab | awk '{sum+=$6} END {print sum/1024 "MB"}'

# Check file sizes
find ~/.local/share/vfab/workspace -name "*.svg" -exec ls -lh {} \; | sort -k5 -hr
```

---

## Immediate Recovery Procedures

### 1. Emergency Shutdown Recovery

**Step 1: Assess the Situation**
```bash
# Check for active jobs
vfab info queue

# Identify interrupted jobs
vfab info queue --interrupted

# Check system status
vfab check self
```

**Step 2: Secure Active Jobs**
```bash
# Pause all plotting jobs
for job in $(vfab info queue --state plotting | awk '{print $1}'); do
    vfab pause $job
done

# Save current state
vfab system export --output emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz
```

**Step 3: Resume or Restart**
```bash
# Attempt automatic recovery
vfab resume

# Manual recovery for specific jobs
vfab restart <job_id>

# Check recovery results
vfab info queue
```

### 2. Device Recovery

**AxiDraw Recovery:**
```bash
# Reset device connection
sudo usbreset /dev/bus/usb/XXX/YYY  # Replace with actual bus/device

# Check device permissions
sudo chmod 666 /dev/ttyUSB0

# Test device
vfab check servo --force-detect

# Restart device services
sudo systemctl restart udev
```

**Camera Recovery:**
```bash
# Restart camera service
sudo systemctl restart motion

# Test camera stream
curl -I http://127.0.0.1:8881/stream.mjpeg

# Reconfigure camera
vfab setup --camera-only
```

### 3. Database Recovery

**Database Lock Recovery:**
```bash
# Check for database locks
lsof ~/.local/share/vfab/vfab.db

# Force unlock (last resort)
rm ~/.local/share/vfab/vfab.db-journal

# Check database integrity
sqlite3 ~/.local/share/vfab/vfab.db "PRAGMA integrity_check;"

# Repair if needed
sqlite3 ~/.local/share/vfab/vfab.db ".recover" | sqlite3 recovered.db
mv recovered.db ~/.local/share/vfab/vfab.db
```

**Database Corruption Recovery:**
```bash
# Backup corrupted database
cp ~/.local/share/vfab/vfab.db ~/.local/share/vfab/vfab.db.corrupted

# Reinitialize from backup
vfab system import --backup latest_backup.tar.gz

# Or recreate database
rm ~/.local/share/vfab/vfab.db
vfab setup
```

---

## Journal Analysis and Recovery

### 1. Journal Structure

Each job maintains a journal (`journal.jsonl`) with entries:
```json
{"type": "state_change", "from_state": "READY", "to_state": "PLOTTING", "timestamp": "...", "reason": "...", "metadata": {...}}
{"type": "emergency_shutdown", "state": "PLOTTING", "timestamp": "...", "reason": "signal_received"}
{"type": "recovery", "from_state": "PLOTTING", "to_state": "PLOTTING", "timestamp": "...", "reason": "Crash recovery"}
```

### 2. Analyzing Journals

**Find Interrupted Jobs:**
```bash
# List all interrupted jobs
for journal in ~/.local/share/vfab/workspace/jobs/*/journal.jsonl; do
    if grep -q "emergency_shutdown" "$journal"; then
        job_id=$(echo "$journal" | cut -d'/' -f7)
        echo "Interrupted job: $job_id"
    fi
done
```

**Analyze Crash Patterns:**
```bash
# Extract crash reasons
grep "emergency_shutdown" ~/.local/share/vfab/workspace/jobs/*/journal.jsonl | \
    jq -r '.reason' | sort | uniq -c

# Timeline of crashes
grep "emergency_shutdown" ~/.local/share/vfab/workspace/jobs/*/journal.jsonl | \
    jq -r '.timestamp' | sort
```

**Validate Journal Integrity:**
```bash
#!/bin/bash
# validate_journals.sh

for journal in ~/.local/share/vfab/workspace/jobs/*/journal.jsonl; do
    echo "Validating $(basename $(dirname $journal))..."
    
    line_num=0
    while IFS= read -r line; do
        ((line_num++))
        
        # Skip empty lines
        [ -z "$line" ] && continue
        
        # Validate JSON
        if ! echo "$line" | python -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
            echo "  Invalid JSON at line $line_num: $line"
        fi
    done < "$journal"
    
    echo "  Validation complete"
done
```

### 3. Manual Journal Recovery

**Recover from Corrupted Journal:**
```bash
# Backup corrupted journal
cp ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl \
   ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl.backup

# Extract valid entries
grep -v "invalid_json" ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl.backup > \
   ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl

# Verify recovery
vfab info job <job_id>
```

**Reconstruct Missing Journal:**
```bash
# Create minimal journal for job without one
mkdir -p ~/.local/share/vfab/workspace/jobs/<job_id>
cat > ~/.local/share/vfab/workspace/jobs/<job_id>/journal.jsonl << EOF
{"type": "state_change", "from_state": "NEW", "to_state": "NEW", "timestamp": "$(date -Iseconds)", "reason": "Journal reconstruction", "metadata": {}}
EOF

# Reset job to known state
vfab restart <job_id>
```

---

## State Machine Recovery

### 1. Understanding State Transitions

Valid transitions in vfab FSM:
```
NEW → ANALYZED → OPTIMIZED → READY → QUEUED → ARMED → PLOTTING → (PAUSED) → COMPLETED | ABORTED | FAILED
```

### 2. State Recovery Procedures

**Recover from Invalid States:**
```bash
# Check current state
vfab info job <job_id> --state-only

# Reset to NEW if in invalid state
vfab remove job <job_id> --force
vfab add job <job_id> <original_file.svg>

# Or use restart command
vfab restart <job_id>
```

**Recover Stuck Transitions:**
```bash
# Identify stuck jobs
vfab info queue --stuck

# Force state transition (advanced)
sqlite3 ~/.local/share/vfab/vfab.db "UPDATE jobs SET state = 'READY' WHERE id = '<job_id>'"

# Verify recovery
vfab info job <job_id>
```

### 3. Bulk Recovery Operations

**Recover All Interrupted Jobs:**
```bash
#!/bin/bash
# recover_all_interrupted.sh

echo "Finding interrupted jobs..."
interrupted_jobs=$(vfab info queue --interrupted | awk '{print $1}')

if [ -z "$interrupted_jobs" ]; then
    echo "No interrupted jobs found."
    exit 0
fi

echo "Found interrupted jobs: $interrupted_jobs"
echo "Starting recovery..."

for job_id in $interrupted_jobs; do
    echo "Recovering job: $job_id"
    
    # Check job state
    current_state=$(vfab info job $job_id --state-only)
    echo "  Current state: $current_state"
    
    # Attempt recovery based on state
    case $current_state in
        "PLOTTING")
            vfab restart $job_id
            ;;
        "PAUSED")
            vfab resume $job_id
            ;;
        "ARMED")
            vfab restart $job_id
            ;;
        *)
            echo "  Unknown state, forcing restart"
            vfab restart $job_id
            ;;
    esac
    
    # Verify recovery
    new_state=$(vfab info job $job_id --state-only)
    echo "  New state: $new_state"
    echo
done

echo "Recovery complete."
```

---

## Data Recovery Procedures

### 1. Backup and Restore

**Create Emergency Backup:**
```bash
# Full system backup
vfab system export --output emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz

# Configuration-only backup
cp ~/.config/vfab/config.yaml ~/config_backup_$(date +%Y%m%d_%H%M%S).yaml

# Database backup
cp ~/.local/share/vfab/vfab.db ~/database_backup_$(date +%Y%m%d_%H%M%S).db
```

**Restore from Backup:**
```bash
# Restore full system
vfab system import --backup emergency_backup_YYYYMMDD_HHMMSS.tar.gz

# Restore configuration
cp ~/config_backup_YYYYMMDD_HHMMSS.yaml ~/.config/vfab/config.yaml

# Restore database
cp ~/database_backup_YYYYMMDD_HHMMSS.db ~/.local/share/vfab/vfab.db
```

### 2. Partial Data Recovery

**Recover Job Data:**
```bash
# Extract job from backup
tar -xzf emergency_backup.tar.gz "workspace/jobs/<job_id>/" --strip-components=1

# Move to current workspace
mv jobs/<job_id> ~/.local/share/vfab/workspace/jobs/

# Update database
sqlite3 ~/.local/share/vfab/vfab.db "INSERT OR REPLACE INTO jobs VALUES ('<job_id>', 'RECOVERED', datetime('now'), datetime('now'));"
```

**Recover Configuration:**
```bash
# Extract specific config sections
tar -xzf emergency_backup.tar.gz "config/config.yaml" --strip-components=1

# Merge with current config
python -c "
import yaml
with open('config.yaml') as f:
    backup = yaml.safe_load(f)
with open('~/.config/vfab/config.yaml') as f:
    current = yaml.safe_load(f)

# Merge backup into current (backup takes precedence)
current.update(backup)

with open('~/.config/vfab/config.yaml', 'w') as f:
    yaml.dump(current, f)
"
```

---

## Crash Pattern Analysis

### 1. Common Crash Patterns

**Pattern 1: Memory Exhaustion**
```bash
# Symptoms
grep "out of memory\|MemoryError" ~/.local/share/vfab/logs/vfab.log

# Analysis
free -h
ps aux | grep vfab | sort -k4 -nr

# Solution
# Reduce job complexity or increase system memory
vfab add job large_job file.svg --optimization fast
```

**Pattern 2: Device Disconnection**
```bash
# Symptoms
grep "device.*disconnect\|connection.*lost" ~/.local/share/vfab/logs/vfab.log

# Analysis
dmesg | grep -i usb | tail -20

# Solution
# Improve USB connection or use powered hub
vfab check servo --reconnect
```

**Pattern 3: Database Locks**
```bash
# Symptoms
grep "database.*lock\|locked" ~/.local/share/vfab/logs/vfab.log

# Analysis
lsof ~/.local/share/vfab/vfab.db

# Solution
# Kill conflicting processes or force unlock
pkill -f vfab
rm ~/.local/share/vfab/vfab.db-journal
```

### 2. Crash Frequency Analysis

**Track Crash Frequency:**
```bash
#!/bin/bash
# crash_analysis.sh

echo "Crash Analysis Report"
echo "====================="
echo "Generated: $(date)"
echo

# Count crashes by type
echo "Crashes by Type:"
grep -E "(emergency_shutdown|ERROR|CRITICAL)" ~/.local/share/vfab/logs/vfab.log | \
    cut -d' ' -f4- | sort | uniq -c | sort -nr

echo
echo "Crashes by Hour:"
grep -E "(emergency_shutdown|ERROR|CRITICAL)" ~/.local/share/vfab/logs/vfab.log | \
    cut -d' ' -f1-2 | sort | uniq -c

echo
echo "Most Affected Jobs:"
grep -E "(emergency_shutdown|ERROR)" ~/.local/share/vfab/logs/vfab.log | \
    grep -o "job_[a-zA-Z0-9]*" | sort | uniq -c | sort -nr | head -5
```

### 3. Performance-Related Crashes

**Identify Performance Issues:**
```bash
# Monitor resource usage during crashes
while true; do
    echo "$(date): $(ps aux | grep vfab | grep -v grep | awk '{sum+=$3} END {print sum}')% CPU, $(ps aux | grep vfab | grep -v grep | awk '{sum+=$6} END {print sum/1024}')MB RAM"
    sleep 5
done &

# Run job and monitor
vfab restart <problematic_job>
```

---

## Preventive Measures

### 1. System Monitoring

**Automated Health Checks:**
```bash
#!/bin/bash
# monitor_vfab.sh

LOG_FILE="/var/log/vfab_monitor.log"

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check for stuck jobs
    stuck_jobs=$(vfab info queue --stuck | wc -l)
    if [ $stuck_jobs -gt 0 ]; then
        echo "[$timestamp] WARNING: $stuck_jobs stuck jobs detected" >> $LOG_FILE
    fi
    
    # Check disk space
    disk_usage=$(df ~/.local/share/vfab/ | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $disk_usage -gt 90 ]; then
        echo "[$timestamp] CRITICAL: Disk usage ${disk_usage}%" >> $LOG_FILE
    fi
    
    # Check for errors
    error_count=$(grep -c "ERROR" ~/.local/share/vfab/logs/vfab.log)
    if [ $error_count -gt 0 ]; then
        echo "[$timestamp] WARNING: $error_count errors in log file" >> $LOG_FILE
    fi
    
    sleep 300  # Check every 5 minutes
done
```

### 2. Automatic Recovery

**Cron-based Recovery:**
```bash
# Add to crontab for automatic recovery
# */15 * * * * /home/user/scripts/auto_recovery.sh

#!/bin/bash
# auto_recovery.sh

# Check for interrupted jobs
interrupted=$(vfab info queue --interrupted | awk '{print $1}')

if [ ! -z "$interrupted" ]; then
    echo "$(date): Auto-recovering interrupted jobs: $interrupted"
    vfab resume
    
    # Log recovery attempt
    echo "$(date): Auto-recovery completed" >> /var/log/vfab_auto_recovery.log
fi
```

### 3. Backup Automation

**Regular Backups:**
```bash
#!/bin/bash
# backup_vfab.sh

BACKUP_DIR="/backup/vfab"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# System backup
vfab system export --output $BACKUP_DIR/system_$DATE.tar.gz

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: system_$DATE.tar.gz"
```

### 4. Resource Management

**Disk Space Management:**
```bash
#!/bin/bash
# cleanup_vfab.sh

# Clean old logs
find ~/.local/share/vfab/logs -name "*.log.*" -mtime +7 -delete

# Clean old journals
find ~/.local/share/vfab/workspace/jobs -name "journal.jsonl" -mtime +30 -exec sh -c '
    file="$1"
    backup="${file}.backup"
    # Keep last 50 lines
    tail -50 "$file" > "$backup"
    mv "$backup" "$file"
' _ {} \;

# Clean completed jobs older than 30 days
find ~/.local/share/vfab/workspace/jobs -name "job.json" -mtime +30 -exec dirname {} \; | \
    xargs -I {} rm -rf {}

echo "Cleanup completed"
```

### 5. Configuration Validation

**Pre-start Validation:**
```bash
#!/bin/bash
# validate_before_start.sh

# Validate configuration
if ! python -c "import yaml; yaml.safe_load(open('~/.config/vfab/config.yaml'))" 2>/dev/null; then
    echo "ERROR: Invalid configuration file"
    exit 1
fi

# Check workspace
if [ ! -d ~/.local/share/vfab/workspace ]; then
    echo "ERROR: Workspace directory not found"
    exit 1
fi

# Check database
if [ ! -f ~/.local/share/vfab/vfab.db ]; then
    echo "ERROR: Database file not found"
    exit 1
fi

# Check device access
if ! vfab check servo >/dev/null 2>&1; then
    echo "WARNING: Device check failed"
fi

echo "Validation passed"
```

---

## Quick Recovery Reference

### Emergency Commands
```bash
# Immediate recovery
vfab resume                           # Resume all interrupted jobs
vfab restart <job_id>                 # Restart specific job
vfab check self                       # System health check

# Data recovery
vfab system export --output backup.tar.gz
vfab system import --backup backup.tar.gz

# Cleanup
vfab cleanup --jobs --older-than 30d
vfab cleanup --logs --older-than 7d
```

### Critical File Locations
```
Configuration:    ~/.config/vfab/config.yaml
Database:         ~/.local/share/vfab/vfab.db
Workspace:        ~/.local/share/vfab/workspace/
Logs:            ~/.local/share/vfab/logs/vfab.log
Job Journals:    ~/.local/share/vfab/workspace/jobs/*/journal.jsonl
```

### Recovery Checklist
- [ ] Check for interrupted jobs
- [ ] Verify device connections
- [ ] Validate configuration
- [ ] Check disk space
- [ ] Review recent logs
- [ ] Create backup before recovery
- [ ] Test recovery with non-critical jobs
- [ ] Monitor system after recovery

This comprehensive recovery guide ensures that vfab users can handle any crash scenario effectively and minimize downtime.