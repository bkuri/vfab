# ploTTY Core Workflows

**Purpose:** Step-by-step guides for the essential ploTTY operations that users perform daily.

---

## 1. Basic Plotting Workflow

### 1.1 Quick Start (First Plot)

```bash
# 1. Initial setup (one-time)
plotty setup

# 2. Add your first job
plotty add my_drawing.svg --paper a4

# 3. Plan the job (optimization + pen mapping)
plotty plan my_drawing --interactive

# 4. Plot the job
plotty plot my_drawing
```

**What happens:**
- `setup`: Creates configuration, prompts for device settings
- `add`: Analyzes SVG, detects layers, creates job in database
- `plan`: Optimizes paths, estimates time, maps layers to pens
- `plot`: Executes plotting with real-time progress

### 1.2 Daily Workflow

```bash
# Check current status
plotty status

# Add new jobs
plotty add batch1.svg --paper a3
plotty add batch2.svg --paper a4

# Plan all jobs
plotty plan-all --preset fast

# Plot sequentially
plotty plot batch1
plotty plot batch2
```

---

## 2. Multi-Pen Workflow

### 2.1 Automatic Multi-Pen Detection

ploTTY automatically detects multi-pen requirements:

```bash
# Add a multi-layer SVG
plotty add complex_art.svg --paper a4

# Plan with interactive pen mapping
plotty plan complex_art --interactive
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
plotty plan complex_art --optimize-pens

# View optimization results
plotty info job complex_art
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
plotty plan-all --preset fast

# Plan with custom optimization
plotty plan-all --preset hq --optimize-pens

# Plan specific jobs
plotty plan job1 job2 job3 --interactive
```

### 3.2 Batch Plotting

```bash
# Plot all planned jobs
plotty plot-all

# Plot with preset (overrides job-specific settings)
plotty plot-all --preset safe

# Plot specific jobs
plotty plot job1 job2 job3
```

### 3.3 Queue Management

```bash
# View queue
plotty list queue

# Remove completed jobs
plotty queue cleanup --state completed

# Remove old jobs (older than 7 days)
plotty queue cleanup --older-than 7d

# Remove specific jobs
plotty remove job1 job2
```

---

## 4. Recovery and Error Handling

### 4.1 Crash Recovery

```bash
# Check for interrupted jobs
plotty recovery list

# Resume interrupted job
plotty resume interrupted_job

# Safe abort (pen up, park)
plotty abort interrupted_job --safe
```

### 4.2 Error Scenarios

**Device disconnected:**
```bash
# Check device status
plotty check ready

# Reconnect device
plotty check device --reconnect
```

**Pen out of ink:**
```bash
# Test pen operation
plotty check servo

# Replace pen and update database
plotty setup pen --replace
```

**Camera issues:**
```bash
# Check camera status
plotty check camera

# Continue without camera
plotty plot job_name --no-camera
```

---

## 5. Advanced Workflows

### 5.1 Custom Optimization

```bash
# Use custom vpype pipeline
plotty plan job --custom "read {src} linemerge linesort write {dst}"

# Compare optimization presets
plotty plan job --preset fast --dry-run
plotty plan job --preset hq --dry-run
plotty compare job fast hq
```

### 5.2 Time Estimation

```bash
# Get detailed time estimate
plotty estimate job --detailed

# Compare pre/post optimization
plotty estimate job --stage pre
plotty estimate job --stage post
```

### 5.3 Test Recording

```bash
# Record test plot (5 seconds)
plotty record-test job --seconds 5

# Compare with actual plot
plotty compare-test job
```

---

## 6. Monitoring and Statistics

### 6.1 Real-time Monitoring

```bash
# Watch job progress
plotty watch job

# System status overview
plotty status --detailed

# Queue status
plotty list queue --watch
```

### 6.2 Performance Analytics

```bash
# Quick overview
plotty stats summary

# Detailed job analytics
plotty stats jobs --last 30

# Performance metrics
plotty stats performance --pen-usage
```

---

## 7. Configuration Management

### 7.1 Device Configuration

```bash
# View current config
plotty info system

# Update device settings
plotty config device --port /dev/ttyUSB0 --model 1

# Test device
plotty check device --test-move
```

### 7.2 Pen and Paper Management

```bash
# List available pens
plotty list pens

# Add new pen
plotty add pen --name "Fine Black" --width 0.3 --color "#000000"

# Add paper size
plotty add paper --name "Custom" --width 200 --height 150 --margin 10
```

---

## 8. Workflow Examples

### 8.1 Studio Production Workflow

```bash
# Morning setup
plotty check ready
plotty status

# Process daily batch
for svg in *.svg; do
    plotty add "$svg" --paper a4
done
plotty plan-all --preset hq --optimize-pens
plotty plot-all

# End of day cleanup
plotty queue cleanup --state completed
plotty stats summary
```

### 8.2 Development Workflow

```bash
# Test new design
plotty add prototype.svg --paper a4
plotty plan prototype --interactive
plotty record-test prototype --seconds 10

# Review and iterate
plotty info job prototype
plotty compare-test prototype

# Production run
plotty plot prototype --preset safe
```

### 8.3 Multi-Device Workflow (Future v2)

```bash
# Check all devices
plotty list devices

# Distribute jobs across devices
plotty plan-all --distribute
plotty plot-all --concurrent
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
plotty add "client_logotype_v2.svg" --paper a4
plotty add "test_pattern_2025-11-07.svg" --paper a4

# Avoid
plotty add "drawing.svg" --paper a4
plotty add "final_final.svg" --paper a4
```

### 9.3 Quality Assurance

```bash
# Always test new designs
plotty record-test new_design --seconds 30

# Verify optimization
plotty estimate new_design --stage pre
plotty estimate new_design --stage post

# Check pen mapping
plotty info job new_design --show-layers
```

---

## 10. Troubleshooting Quick Reference

| Problem | Command | Solution |
|---------|---------|----------|
| Device not found | `plotty check device` | Check USB connection |
| Pen not moving | `plotty check servo` | Test servo operation |
| Poor optimization | `plotty plan job --preset hq` | Use high-quality preset |
| Camera not working | `plotty check camera` | Check IP feed URL |
| Job stuck | `plotty recovery list` | Resume or safe abort |
| Slow plotting | `plotty stats performance` | Check speed settings |

---

**These workflows cover the essential ploTTY operations. For specific command details, use `plotty --help` or `plotty <command> --help`.**