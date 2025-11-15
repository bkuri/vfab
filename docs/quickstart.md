# vfab Quickstart Guide

**Get your first plot running in 5 minutes!**

---

## 🚀 1. Install vfab (30 seconds)

### Option A: Quick Install (Recommended)
```bash
# Install uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install vfab
git clone https://github.com/your-org/vfab.git
cd vfab
uv pip install -e ".[vpype]"

# Initialize database
uv run alembic upgrade head
```

### Option B: System Package Manager
```bash
# Arch Linux
sudo pacman -S vfab

# pip (if you must)
pip install vfab[vpype]
```

**Verify Installation:**
```bash
vfab --version
# Should show: vfab 1.0.1
```

---

## 📊 2. Add Your First Design (1 minute)

### Option A: Use Example Design
```bash
# Create test design
vfab add demo --src https://example.com/simple-design.svg --name my_first_plot
```

### Option B: Use Your Own SVG
```bash
# Add your design
vfab add my_design.svg --name my_first_plot --paper a4
```

**Expected Output:**
```
✅ Added job: my_first_plot
📊 Analysis results:
  - Dimensions: 150mm × 100mm  
  - Points: 1,247
  - Estimated time: 8 minutes
  - Layers detected: 1
```

---

## ⚡ 3. Plot It! (2 minutes)

### Start Plotting
```bash
# Start the plot
vfab plot my_first_plot
```

**Real-time Progress:**
```
🖊️ Plotting: my_first_plot
===============================
Progress: ████████████████████ 67%
Time remaining: 2m 15s
Current layer: default (1/1)
Pen: Black 0.5mm
Speed: 25% (medium)

Controls:
  [Space] Pause/Resume
  [A] Abort  
  [S] Skip to next layer
```

### What's Happening?
1. **vfab analyzes** your SVG for optimal plotting path
2. **AxiDraw moves** the pen following optimized routes
3. **Progress tracking** shows real-time completion
4. **Automatic recording** captures the process (if camera enabled)

---

## 🎉 4. Success! (30 seconds)

### View Results
```bash
# Job information
vfab info job my_first_plot

# View generated report
# Open: workspace/jobs/my_first_plot/report.html
```

**Expected Report:**
- Total plot time: 7m 42s
- Pen changes: 0
- Total distance: 2.3m
- Quality score: 98.5%

---

## 📡 Real-Time Monitoring (Optional, 2 minutes)

### Start WebSocket Monitoring
```bash
# Terminal 1: Start daemon with WebSocket server
vfab daemon --log-level info

# Terminal 2: Monitor real-time activity  
vfab monitor --follow
```

### What You'll See
```bash
🔌 Connected to vfab WebSocket
============================================================
[19:30:15] 📋 Job my_first_plot: QUEUED → RUNNING
[19:30:22] 📊 Job my_first_plot: 25.0% complete
[19:30:45] 📊 Job my_first_plot: 67.0% complete  
[19:31:08] 📋 Job my_first_plot: RUNNING → COMPLETED
```

### Web Dashboard (Optional)
```bash
# Open HTML dashboard in browser
open docs/examples/web-dashboard.html
# Or create your own using WebSocket API
```

---

## 🔄 What's Next? (1.5 minutes)

### Immediate Next Steps
```bash
# Try multi-pen design
vfab add colorful_design.svg --name rainbow_test

# Plan multiple jobs
vfab add "*.svg" --name batch_test

# Explore all commands
vfab --help
```

### Learning Paths

**🎨 Creative Integration (5 minutes)**
- Want to create generative art? → [vsketch Integration Guide](vpype-vfab.md)
- Use Processing/p5.js? → [Creative Tool Integration](user-guide.md#4-creative-tool-integration)

**⚙️ Advanced Features (10 minutes)**
- Multi-pen workflows → [Multi-Pen Guide](user-guide.md#3-working-with-multi-pen-designs)
- Batch production → [Batch Workflow](user-guide.md#5-batch-production-workflow)

**🔧 Power User (15 minutes)**
- Custom optimization → [Optimization Guide](user-guide.md#6-advanced-optimization)
- Studio management → [Studio Guide](user-guide.md#7-studio-management)

---

## 🆘 Need Help?

### Quick Fixes
```bash
# Check system readiness
vfab check ready

# Test AxiDraw connection
vfab check servo

# View all jobs
vfab list jobs
```

### Common Issues
| Problem | Quick Solution |
|---------|----------------|
| "Device not found" | `vfab check ready` |
| "Permission denied" | `sudo usermod -a -G dialout $USER` |
| "SVG too complex" | Use `--preset hq` for better optimization |

### Get More Help
- **📚 Full Documentation**: [User Guide](user-guide.md)
- **🎨 Creative Integration**: [vpype-vfab Guide](vpype-vfab.md)
- **🐛 Troubleshooting**: [Troubleshooting Guide](troubleshooting/)
- **💬 Community**: [GitHub Discussions](https://github.com/your-org/vfab/discussions)

---

## 🎯 You Did It!

**In 5 minutes you:**
✅ Installed vfab  
✅ Added your first design  
✅ Started your first plot  
✅ Learned the basics

**Ready for more?**
- 🎨 [Creative workflows](vpype-vfab.md) - vsketch, vpype integration
- 📊 [Production features](user-guide.md) - Batch jobs, multi-pen
- ⚙️ [Advanced configuration](api/configuration-schema.md) - Custom optimization

**Happy plotting! 🎉**

---

*This quickstart covers the essential vfab workflow. For comprehensive features, advanced workflows, and detailed configuration, see the full [User Guide](user-guide.md).*