# ploTTY Troubleshooting Guide

**Purpose:** Comprehensive guide to diagnosing and resolving common ploTTY issues based on real-world testing and error patterns.

---

## Table of Contents

1. [Quick Diagnostics](#1-quick-diagnostics)
2. [Installation Issues](#2-installation-issues)
3. [Device Problems](#3-device-problems)
4. [Configuration Errors](#4-configuration-errors)
5. [Job and Planning Issues](#5-job-and-planning-issues)
6. [Plotting Problems](#6-plotting-problems)
7. [Database Issues](#7-database-issues)
8. [Performance Issues](#8-performance-issues)
9. [Recovery and Crashes](#9-recovery-and-crashes)
10. [Preventive Maintenance](#10-preventive-maintenance)

---

## 1. Quick Diagnostics

### 1.1 System Health Check

```bash
# Comprehensive system check
plotty check ready

# Individual component checks
plotty check device
plotty check camera
plotty check servo
plotty check timing

# System information
plotty info system
```

### 1.2 Common Error Patterns

Based on test analysis, these are the most frequent issues:

| Error Type | Frequency | Common Cause |
|------------|-----------|--------------|
| Import errors | High | Missing dependencies |
| Device not found | High | USB/connection issues |
| Configuration invalid | Medium | YAML syntax errors |
| Database locked | Medium | Concurrent access |
| Permission denied | Low | File system permissions |

---

## 2. Installation Issues

### 2.1 Dependency Problems

**Symptoms:**
```
ModuleNotFoundError: No module named 'axidraw'
ImportError: cannot import name 'pyaxidraw'
```

**Solutions:**
```bash
# Check installation
uv pip list | grep -E "(axidraw|vpype|plotty)"

# Reinstall with correct extras
uv pip install -e ".[dev,vpype,axidraw]"

# Verify core dependencies
python -c "import vpype; print('vpype OK')"
python -c "import pyaxidraw; print('axidraw OK')"  # May fail without hardware
```

### 2.2 Python Version Issues

**Symptoms:**
```
SyntaxError: invalid syntax
TypeError: 'type' object is not subscriptable
```

**Solutions:**
```bash
# Check Python version
python --version  # Should be 3.11+

# Install correct Python version
uv python install 3.12

# Recreate virtual environment
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,vpype,axidraw]"
```

### 2.3 Path and Import Issues

**Symptoms:**
```
ModuleNotFoundError: No module named 'plotty'
ImportError: attempted relative import beyond top-level package
```

**Solutions:**
```bash
# Install in editable mode
uv pip install -e .

# Check PYTHONPATH
echo $PYTHONPATH

# Run from project root
cd /path/to/plotty
uv run plotty --help
```

---

## 3. Device Problems

### 3.1 AxiDraw Not Found

**Symptoms:**
```
❌ AxiDraw device not found
❌ No USB devices detected
```

**Diagnosis:**
```bash
# Check USB connection
lsusb | grep -i axidraw
dmesg | grep -i tty

# Check device permissions
ls -la /dev/ttyUSB*
groups $USER | grep -o uucp

# Test device detection
plotty check device --verbose
```

**Solutions:**
```bash
# Add user to uucp group (Linux)
sudo usermod -a -G uucp $USER
# Log out and log back in

# Try different port
plotty config device --port /dev/ttyUSB1

# Test with specific model
plotty config device --model 2  # A3/SE/A3
```

### 3.2 Pen Servo Issues

**Symptoms:**
```
❌ Pen not moving
❌ Servo calibration failed
```

**Diagnosis:**
```bash
# Test servo operation
plotty check servo --cycles 3

# Check pen heights
plotty info system | grep -A5 "pen_pos"
```

**Solutions:**
```bash
# Adjust pen heights
plotty config device --pen-pos-up 70
plotty config device --pen-pos-down 30

# Test different values
plotty check servo --test-heights

# Reset to defaults
plotty config device --reset-pen-heights
```

### 3.3 Device Timing Issues

**Symptoms:**
```
⚠️ Device timing inconsistent
⚠️ Plot speed too fast/slow
```

**Diagnosis:**
```bash
# Check device timing
plotty check timing --verbose

# Test different speeds
plotty check timing --speed-test
```

**Solutions:**
```bash
# Adjust speeds
plotty config device --speed-pendown 20
plotty config device --speed-penup 60

# Use conservative settings
plotty config device --speed-pendown 15 --speed-penup 50
```

---

## 4. Configuration Errors

### 4.1 YAML Syntax Errors

**Symptoms:**
```
yaml.scanner.ScannerError
Invalid configuration file
```

**Diagnosis:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Check configuration
plotty check config
```

**Common YAML Issues:**
```yaml
# ❌ Wrong indentation
device:
port: /dev/ttyUSB0  # Should be indented

# ✅ Correct indentation
device:
  port: /dev/ttyUSB0

# ❌ Missing quotes
paper: A4  # Should be quoted if it's a string

# ✅ Correct
paper: "A4"
```

### 4.2 Invalid Configuration Values

**Symptoms:**
```
ValidationError: value is not a valid integer
Configuration validation failed
```

**Diagnosis:**
```bash
# Check configuration values
plotty info system --validate

# Show current config
plotty info system --show-config
```

**Common Value Issues:**
```yaml
# ❌ Invalid pen heights (must be 0-100)
device:
  pen_pos_up: 150    # Too high
  pen_pos_down: -10  # Too low

# ✅ Valid values
device:
  pen_pos_up: 60
  pen_pos_down: 40

# ❌ Invalid paper size
paper:
  default_size: "A5"  # Not supported

# ✅ Valid sizes
paper:
  default_size: "A4"  # A3, A4, Letter
```

### 4.3 Missing Configuration Sections

**Symptoms:**
```
KeyError: 'device'
Missing required configuration section
```

**Solutions:**
```bash
# Reset configuration
plotty setup --reset

# Add missing sections manually
plotty config device --interactive
plotty config paper --interactive
```

---

## 5. Job and Planning Issues

### 5.1 SVG Parsing Problems

**Symptoms:**
```
❌ Invalid SVG file
❌ No vector paths found
```

**Diagnosis:**
```bash
# Validate SVG file
plotty check svg your_file.svg

# Show SVG analysis
plotty add your_file.svg --dry-run --verbose
```

**Common SVG Issues:**
- **Bitmap images**: SVG contains raster images
- **No paths**: SVG has only text or shapes without paths
- **Corrupted file**: Invalid XML structure

**Solutions:**
```bash
# Convert to paths (Inkscape)
inkscape your_file.svg --export-plain-svg=your_file_paths.svg

# Optimize SVG
svgo your_file.svg

# Check with vpype directly
vpype read your_file.svg show --debug
```

### 5.2 Layer Detection Issues

**Symptoms:**
```
⚠️ No layers detected
⚠️ Unexpected layer count
```

**Diagnosis:**
```bash
# Analyze layers
plotty add your_file.svg --analyze-layers

# Show layer details
plotty plan your_job --show-layers
```

**Solutions:**
```bash
# Force single-pen mode
plotty plan your_job --single-pen

# Manual layer mapping
plotty plan your_job --interactive --manual-mapping

# Check for hidden layers
plotty check svg your_file.svg --show-hidden
```

### 5.3 Optimization Failures

**Symptoms:**
```
❌ vpype optimization failed
❌ Pipeline execution error
```

**Diagnosis:**
```bash
# Test vpype directly
vpype read your_file.svg linemerge linesort write output.svg

# Check optimization preset
plotty info presets
```

**Solutions:**
```bash
# Use different preset
plotty plan your_job --preset fast

# Use custom pipeline
plotty plan your_job --custom "read {src} write {dst}"

# Skip optimization
plotty plan your_job --no-optimize
```

---

## 6. Plotting Problems

### 6.1 Plotting Stuck or Frozen

**Symptoms:**
```
⏸️ Plotting paused unexpectedly
🔄 Plotting not progressing
```

**Diagnosis:**
```bash
# Check job status
plotty info job your_job

# Check device status
plotty check device

# View active processes
ps aux | grep plotty
```

**Solutions:**
```bash
# Pause/resume
plotty pause your_job
plotty resume your_job

# Safe abort
plotty abort your_job --safe

# Force recovery
plotty recovery list
plotty resume your_job --force
```

### 6.2 Poor Plot Quality

**Symptoms:**
```
⚠️ Lines not connecting
⚠️ Inconsistent line width
```

**Diagnosis:**
```bash
# Check pen settings
plotty list pens

# Test pen operation
plotty check servo --test-plot

# Review optimization
plotty info job your_job --show-optimization
```

**Solutions:**
```bash
# Adjust pen heights
plotty config device --pen-pos-up 65 --pen-pos-down 35

# Use high-quality preset
plotty plan your_job --preset hq

# Reduce speed
plotty config device --speed-pendown 20

# Test different pen
plotty update pen 1 --width 0.7  # Use wider pen
```

### 6.3 Time Estimation Inaccurate

**Symptoms:**
```
⚠️ Time estimate way off
⚠️ Plot taking much longer
```

**Diagnosis:**
```bash
# Compare estimates
plotty estimate your_job --stage pre
plotty estimate your_job --stage post

# Check actual vs estimated
plotty info job your_job --show-timing
```

**Solutions:**
```bash
# Calibrate device
plotty calibrate device --test-job your_job

# Use conservative estimates
plotty config estimation --conservative

# Track performance
plotty stats performance --accuracy
```

---

## 7. Database Issues

### 7.1 Database Locked

**Symptoms:**
```
❌ Database is locked
❌ Concurrent access denied
```

**Diagnosis:**
```bash
# Check database status
plotty check database

# Look for locked processes
lsof workspace/plotty.db
```

**Solutions:**
```bash
# Wait and retry (temporary locks)
sleep 5
plotty add your_file.svg

# Force unlock (use carefully)
plotty database unlock --force

# Restart database service
plotty database restart
```

### 7.2 Database Corruption

**Symptoms:**
```
❌ Database corrupted
❌ No such table
```

**Diagnosis:**
```bash
# Check database integrity
plotty check database --integrity

# Test database access
sqlite3 workspace/plotty.db ".tables"
```

**Solutions:**
```bash
# Backup and recreate
plotty database backup
plotty database reset

# Run migrations
uv run alembic upgrade head

# Restore from backup (if available)
plotty database restore backup_file.db
```

### 7.3 Migration Issues

**Symptoms:**
```
❌ Migration failed
❌ Schema mismatch
```

**Solutions:**
```bash
# Check migration status
uv run alembic current

# Run migrations manually
uv run alembic upgrade head

# Reset migrations (last resort)
uv run alembic downgrade base
uv run alembic upgrade head
```

---

## 8. Performance Issues

### 8.1 Slow Operations

**Symptoms:**
```
⏳ Commands taking too long
⏳ Large files processing slowly
```

**Diagnosis:**
```bash
# Check system resources
plotty check system --resources

# Profile operation
plotty add large_file.svg --profile

# Check database performance
plotty stats performance --queries
```

**Solutions:**
```bash
# Use fast preset
plotty plan-all --preset fast

# Optimize database
plotty database optimize

# Increase memory limits
plotty config system --max-memory 4GB
```

### 8.2 Memory Issues

**Symptoms:**
```
⚠️ Out of memory
⚠️ System becoming unresponsive
```

**Diagnosis:**
```bash
# Check memory usage
plotty check system --memory

# Monitor during operation
plotty monitor --memory
```

**Solutions:**
```bash
# Reduce batch size
plotty plan-all --batch-size 5

# Use streaming mode
plotty add large_file.svg --streaming

# Clear cache
plotty cache clear
```

---

## 9. Recovery and Crashes

### 9.1 Crash Recovery

**Symptoms:**
```
💥 ploTTY crashed
💥 Job interrupted
```

**Diagnosis:**
```bash
# Check for interrupted jobs
plotty recovery list

# Check crash logs
plotty logs --crash

# Check system status
plotty check ready
```

**Solutions:**
```bash
# Resume interrupted job
plotty resume interrupted_job

# Safe abort if needed
plotty abort interrupted_job --safe

# Full system recovery
plotty recovery full --safe
```

### 9.2 Power Loss Recovery

**Symptoms:**
```
⚡ Power outage during plotting
⚡ System reboot required
```

**Solutions:**
```bash
# Check system after reboot
plotty check ready

# Find interrupted jobs
plotty recovery list --power-loss

# Safe recovery procedure
plotty recovery power-loss --safe
```

### 9.3 Data Recovery

**Symptoms:**
```
📁 Lost job files
📁 Corrupted workspace
```

**Solutions:**
```bash
# Check workspace integrity
plotty check workspace --integrity

# Repair workspace
plotty workspace repair

# Restore from backup
plotty backup restore --latest
```

---

## 10. Preventive Maintenance

### 10.1 Daily Checks

```bash
# Morning system check
plotty check ready
plotty status

# Quick performance check
plotty stats summary --today
```

### 10.2 Weekly Maintenance

```bash
# Clean up completed jobs
plotty queue cleanup --state completed --older-than 7d

# Database optimization
plotty database optimize

# Backup configuration
plotty backup config
```

### 10.3 Monthly Maintenance

```bash
# Full system check
plotty check system --full

# Performance analysis
plotty stats performance --last 30

# Archive old jobs
plotty archive --older-than 30d
```

### 10.4 Best Practices

1. **Regular Backups**: Back up configuration and important jobs
2. **System Monitoring**: Use `plotty check ready` before important jobs
3. **Test Plots**: Use `plotty record-test` for new designs
4. **Update Regularly**: Keep ploTTY and dependencies updated
5. **Document Issues**: Keep a log of recurring problems

---

## Emergency Procedures

### Complete System Reset

```bash
# Emergency reset (last resort)
plotty emergency-reset --confirm

# This will:
# - Reset configuration to defaults
# - Clear all jobs from queue
# - Restart database
# - Archive current workspace
```

### Contact Support

When reporting issues, include:

```bash
# Generate system report
plotty info system --full > system_report.txt

# Include error logs
plotty logs --errors > error_logs.txt

# Show recent jobs
plotty list jobs --recent > recent_jobs.txt
```

---

**This troubleshooting guide is based on comprehensive testing of ploTTY's error handling and recovery systems. Most issues can be resolved using the diagnostic commands and solutions provided.**