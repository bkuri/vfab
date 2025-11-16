# vfab Core Workflows

**Purpose:** Step-by-step guides for the essential vfab operations that users perform daily.

---

## 1. Basic Plotting Workflow

### 1.1 Quick Start (First Plot)

```bash
# 1. Initial setup (one-time)
vfab setup

# 2. Add your first job
vfab add my_drawing.svg --paper a4

# 3. Plan the job (optimization + pen mapping)
vfab plan my_drawing --interactive

# 4. Plot the job
vfab plot my_drawing
```

**What happens:**
- `setup`: Creates configuration, prompts for device settings
- `add`: Analyzes SVG, detects layers, creates job in database
- `plan`: Optimizes paths, estimates time, maps layers to pens
- `plot`: Executes plotting with real-time progress

### 1.2 Daily Workflow

```bash
# Check current status
vfab status

# Add new jobs
vfab add batch1.svg --paper a3
vfab add batch2.svg --paper a4

# Plan all jobs
vfab plan-all --preset fast

# Plot sequentially
vfab plot batch1
vfab plot batch2
```

---

## 2. Multi-Pen Workflow

### 2.1 Automatic Multi-Pen Detection

vfab automatically detects multi-pen requirements:

```bash
# Add a multi-layer SVG
vfab add complex_art.svg --paper a4

# Plan with interactive pen mapping
vfab plan complex_art --interactive
```

**Interactive pen mapping prompt:**
```
🎨 Detected 4 layers:
  🔵 Layer 1: "outline" (234 elements) - BLUE
  🟢 Layer 2: "fill" (156 elements) - GREEN  
  🟡 Layer 3: "highlights" (89 elements) - YELLOW
  🔴 Layer 4: "details" (45 elements) - RED

Available pens:
  [1] 0.3mm Black (fine)
  [2] 0.7mm Black (medium)
  [3] 0.3mm Red (fine)
  [4] 0.5mm Blue (medium)

Map layers to pens (comma-separated, e.g. "1,2,3,4"):
```

### 2.2 Pen Optimization

```bash
# Plan with pen optimization (reduces pen swaps)
vfab plan complex_art --optimize-pens

# View optimization results
vfab info job complex_art
```

**Optimization report:**
```
📊 Pen Optimization Results:
  Original pen swaps: 12
  Optimized pen swaps: 4 (67% reduction)
  Time saved: ~8 minutes
```

---

## 3. Batch Operations Workflow

### 3.1 Batch Planning

```bash
# Plan all queued jobs with fast preset
vfab plan-all --preset fast

# Plan with custom optimization
vfab plan-all --preset hq --optimize-pens

# Plan specific jobs
vfab plan job1 job2 job3 --interactive
```

### 3.2 Batch Plotting

```bash
# Plot all planned jobs
vfab plot-all

# Plot with preset (overrides job-specific settings)
vfab plot-all --preset safe

# Plot specific jobs
vfab plot job1 job2 job3
```

### 3.3 Queue Management

```bash
# View queue
vfab list queue

# Remove completed jobs
vfab queue cleanup --state completed

# Remove old jobs (older than 7 days)
vfab queue cleanup --older-than 7d

# Remove specific jobs
vfab remove job1 job2
```

---

## 4. Recovery and Error Handling

### 4.1 Crash Recovery

```bash
# Check for interrupted jobs
vfab recovery list

# Resume interrupted job
vfab resume interrupted_job

# Safe abort (pen up, park)
vfab abort interrupted_job --safe
```

### 4.2 Error Scenarios

**Device disconnected:**
```bash
# Check device status
vfab check ready

# Reconnect device
vfab driver test axidraw
```

**Pen out of ink:**
```bash
# Test pen operation
vfab driver test axidraw

# Replace pen and update database
vfab setup pen --replace
```

**Camera issues:**
```bash
# Check camera status
vfab check camera

# Continue without camera
vfab plot job_name --no-camera
```

---

## 5. Advanced Workflows

### 5.1 Custom Optimization

```bash
# Use custom vpype pipeline
vfab plan job --custom "read {src} linemerge linesort write {dst}"

# Compare optimization presets
vfab plan job --preset fast --dry-run
vfab plan job --preset hq --dry-run
vfab compare job fast hq
```

### 5.2 Time Estimation

```bash
# Get detailed time estimate
vfab estimate job --detailed

# Compare pre/post optimization
vfab estimate job --stage pre
vfab estimate job --stage post
```

### 5.3 Test Recording

```bash
# Record test plot (5 seconds)
vfab record-test job --seconds 5

# Compare with actual plot
vfab compare-test job
```

---

## 6. Monitoring and Statistics

### 6.1 Real-time Monitoring

```bash
# Watch job progress
vfab watch job

# System status overview
vfab status --detailed

# Queue status
vfab list queue --watch
```

### 6.2 Performance Analytics

```bash
# Quick overview
vfab stats summary

# Detailed job analytics
vfab stats jobs --last 30

# Performance metrics
vfab stats performance --pen-usage
```

---

## 7. Configuration Management

### 7.1 Device Configuration

```bash
# View current config
vfab info system

# Update device settings
vfab config device --port /dev/ttyUSB0 --model 1

# Test device
vfab driver test axidraw
```

### 7.2 Pen and Paper Management

```bash
# List available pens
vfab list pens

# Add new pen
vfab add pen --name "Fine Black" --width 0.3 --color "#000000"

# Add paper size
vfab add paper --name "Custom" --width 200 --height 150 --margin 10
```

---

## 8. Workflow Examples

### 8.1 Studio Production Workflow

```bash
# Morning setup
vfab check ready
vfab status

# Process daily batch
for svg in *.svg; do
    vfab add "$svg" --paper a4
done
vfab plan-all --preset hq --optimize-pens
vfab plot-all

# End of day cleanup
vfab queue cleanup --state completed
vfab stats summary
```

### 8.2 Development Workflow

```bash
# Test new design
vfab add prototype.svg --paper a4
vfab plan prototype --interactive
vfab record-test prototype --seconds 10

# Review and iterate
vfab info job prototype
vfab compare-test prototype

# Production run
vfab plot prototype --preset safe
```

### 8.3 Multi-Device Workflow (Future v2)

```bash
# Check all devices
vfab list devices

# Distribute jobs across devices
vfab plan-all --distribute
vfab plot-all --concurrent
```

---

## 9. Best Practices

### 9.1 File Organization

```
projects/
├── active/
│   ├── design1.svg
│   ├── design2.svg
└── archive/
    ├── completed/
    └── tests/
```

### 9.2 Naming Conventions

```bash
# Good naming
vfab add "client_logotype_v2.svg" --paper a4
vfab add "test_pattern_2025-11-07.svg" --paper a4

# Avoid
vfab add "drawing.svg" --paper a4
vfab add "final_final.svg" --paper a4
```

### 9.3 Quality Assurance

```bash
# Always test new designs
vfab record-test new_design --seconds 30

# Verify optimization
vfab estimate new_design --stage pre
vfab estimate new_design --stage post

# Check pen mapping
vfab info job new_design --show-layers
```

---

## 10. Troubleshooting Quick Reference

| Problem | Command | Solution |
|---------|---------|----------|
| Device not found | `vfab driver test axidraw` | Check USB connection |
| Pen not moving | `vfab driver test axidraw` | Test servo operation |
| Poor optimization | `vfab plan job --preset hq` | Use high-quality preset |
| Camera not working | `vfab check camera` | Check IP feed URL |
| Job stuck | `vfab recovery list` | Resume or safe abort |
| Slow plotting | `vfab stats performance` | Check speed settings |

---

**These workflows cover the essential vfab operations. For specific command details, use `vfab --help` or `vfab <command> --help`.**