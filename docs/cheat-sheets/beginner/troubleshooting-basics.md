# Troubleshooting Basics Cheat Sheet

**Fix common issues fast** - Don't panic, try these solutions first.

---

## 🚨 Emergency Stop

**If plotter is going crazy:**
```bash
# IMMEDIATELY STOP
plotty abort

# Or press Ctrl+C twice
# Then physically unplug USB if needed
```

**Once stopped:**
```bash
# Check what happened
plotty status
plotty recovery list
```

---

## 🔌 Device Connection Issues

### "Device not found" or "No device detected"

**Quick fixes (try in order):**
1. **Check USB cable** - Unplug and reconnect firmly
2. **Try different USB port** - Use port directly on computer (not hub)
3. **Check power** - Green light solid on AxiDraw?
4. **Restart ploTTY** - `plotty restart`

**Diagnostic commands:**
```bash
# Check device detection
plotty check device

# List available ports
plotty list ports

# Test specific port
plotty check device --port /dev/ttyUSB1
```

**If still not found:**
```bash
# Try auto-detection
plotty config device --auto-detect

# Manual port specification
plotty config device --port /dev/ttyUSB0  # Linux
plotty config device --port COM3          # Windows
plotty config device --port /dev/cu.usbmodem1411  # Mac
```

---

## 🖊️ Pen & Drawing Issues

### Lines too light or not drawing

**Quick fixes:**
1. **Check pen** - Test on scrap paper first
2. **Remove pen cap** - Easy to forget!
3. **Lower pen position** - Move pen closer to paper

**Pen position adjustment:**
```bash
# Lower pen by 5 units (try more if still light)
plotty config device --pen-down 35

# Test pen movement
plotty check servo

# Test with simple pattern
plotty test pattern --basic
```

**Pen position guide:**
- **Pen up:** 60-70 (pen lifts off paper)
- **Pen down:** 30-45 (pen touches paper)
- **Start with:** up=60, down=40
- **Adjust by:** 2-3 units at a time

### Lines too dark/bleeding

**Quick fixes:**
1. **Raise pen position** - Less pressure on paper
2. **Use lighter pen** - Finer tip or different ink
3. **Faster speed** - Less ink deposition

```bash
# Raise pen by 5 units
plotty config device --pen-down 45

# Increase plotting speed
plotty config device --speed 30
```

### Pen skipping or jagged lines

**Quick fixes:**
1. **Clean pen tip** - Wipe with damp cloth
2. **Test pen** - Draw lines by hand
3. **Check paper** - Smooth, flat surface?
4. **Slower speed** - More controlled movement

```bash
# Reduce speed for better control
plotty config device --speed 15

# Test with slower speed
plotty test pattern --slow
```

---

## 📄 Paper & Position Issues

### Plot runs off paper

**Quick fixes:**
1. **Check design size** - Is it larger than paper?
2. **Verify paper position** - Aligned with plotter origin?
3. **Check paper size settings** - Correct in ploTTY?

**Diagnostic commands:**
```bash
# Check design vs paper size
plotty add design.svg --dry-run

# Verify paper configuration
plotty list paper

# Test plot boundaries
plotty test pattern --boundary
```

**Paper size verification:**
```bash
# Add correct paper size
plotty add paper --name "A4" --width 210 --height 297

# Use specific paper for job
plotty add design.svg --paper a4
```

### Paper moves during plotting

**Quick fixes:**
1. **Secure paper better** - Tape edges, use heavier paper
2. **Reduce speed** - Less vibration
3. **Check plotter stability** - On solid surface

```bash
# Reduce speed for less vibration
plotty config device --speed 20

# Test with reduced speed
plotty test pattern --slow
```

---

## ⚡ Software & Performance Issues

### Commands running very slow

**Quick fixes:**
1. **Check system resources** - Close other applications
2. **Simplify design** - Too many points?
3. **Use faster preset** - `--preset fast`

**Diagnostic commands:**
```bash
# Check system resources
plotty check system

# Profile job performance
plotty profile job

# Check design complexity
plotty info job my_job --show-complexity
```

**Performance optimization:**
```bash
# Use fast optimization
plotty plan job --preset fast

# Simplify design
plotty plan job --simplify --tolerance 0.1

# Check what's taking time
plotty profile job --show-steps
```

### Database errors or locked

**Quick fixes:**
1. **Restart ploTTY** - Often clears locks
2. **Check disk space** - Full disk causes issues
3. **Verify permissions** - Can write to workspace?

```bash
# Check database status
plotty check database

# Restart ploTTY service
plotty restart

# Check disk space
plotty check system --disk-space
```

### Memory errors

**Quick fixes:**
1. **Close other programs** - Free up RAM
2. **Simplify design** - Reduce complexity
3. **Process in parts** - Split large designs

```bash
# Check memory usage
plotty check system --memory

# Simplify complex design
plotty plan job --reduce-complexity

# Process in sections
plotty split job --parts 4
```

---

## 📹 Camera & Recording Issues

### Camera not working

**Quick fixes:**
1. **Check URL** - Correct camera URL?
2. **Test camera** - Opens in browser?
3. **Check network** - Same network as ploTTY?

```bash
# Test camera connection
plotty check camera

# Test specific URL
plotty check camera --url http://192.168.1.100:8881/stream.mjpeg

# Update camera URL
plotty config camera --url http://your-camera-url/stream.mjpeg
```

### Recording not saving

**Quick fixes:**
1. **Check disk space** - Full disk can't save
2. **Verify permissions** - Can write to output directory?
3. **Test recording** - Try manual recording

```bash
# Test recording manually
plotty record test --seconds 10

# Check output directory
plotty check workspace --write-permissions

# Clean up old recordings
plotty cleanup recordings --older-than 7d
```

---

## 🔄 Job & Queue Issues

### Job stuck in queue

**Quick fixes:**
1. **Check job status** - What state is it in?
2. **Resume if paused** - May just be paused
3. **Restart if stuck** - Sometimes needed

```bash
# Check job status
plotty info job stuck_job

# Resume if paused
plotty resume stuck_job

# Restart if needed
plotty restart stuck_job

# Last resort: remove and re-add
plotty remove job stuck_job
plotty add design.svg --name "restart_job"
```

### Queue not updating

**Quick fixes:**
1. **Check ploTTY status** - Is it running?
2. **Restart queue** - Clear queue state
3. **Verify database** - Not corrupted?

```bash
# Check ploTTY status
plotty status

# Restart queue system
plotty restart queue

# Check database integrity
plotty check database --verify
```

---

## 🆘 Getting Help

### When to ask for help

**Contact support if:**
- Device never detected after trying all USB ports
- Same error persists after multiple restarts
- Database corruption suspected
- Hardware damage suspected

**Before asking for help:**
```bash
# Gather system information
plotty info system > system_info.txt

# Get recent logs
plotty logs --tail 100 > recent_logs.txt

# Note what you were doing
# Note exact error messages
# Note what you've tried
```

**What to include in support request:**
1. **System info** - `plotty info system`
2. **Exact error** - Copy full error message
3. **What you tried** - List troubleshooting steps
4. **When it happens** - Every time or intermittent?

---

## 📋 Quick Troubleshooting Flowchart

```
Problem?
├─ Device not found → Check USB → Try different port → Check power
├─ No drawing → Check pen → Lower pen position → Test pen
├─ Lines light → Lower pen → Test pen → Check paper
├─ Runs off paper → Check design size → Verify paper position
├─ Very slow → Check system resources → Simplify design
├─ Job stuck → Check status → Resume → Restart
└─ Other error → Check logs → Restart ploTTY → Get help
```

---

## 💡 Prevention Tips

**Avoid common problems:**
- 🔌 **Use quality USB cables** - Cheap cables cause issues
- 🖊️ **Test pens first** - Don't use dried out pens
- 📄 **Use good paper** - Smooth, flat, right weight
- 💾 **Keep disk space free** - At least 1GB available
- 🔄 **Restart regularly** - Prevents memory leaks

**Daily maintenance:**
```bash
# Quick health check
plotty check ready

# Clean up old jobs
plotty queue cleanup --completed

# Check system resources
plotty check system
```

---

**🎯 Goal:** Solve 80% of problems with these basics. Know when to ask for help vs. when to keep troubleshooting.

**📚 Next:** [Multi-Pen Workflow](../creative/multi-pen-workflow.md) when ready for colorful designs!