# ploTTY Quickstart Guide

**Get your first plot running in 5 minutes!**

---

## 🚀 1. Install ploTTY (30 seconds)

### Option A: Quick Install (Recommended)
```bash
# Install uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty
uv pip install -e ".[vpype]"

# Initialize database
uv run alembic upgrade head
```

### Option B: System Package Manager
```bash
# Arch Linux
sudo pacman -S plotty

# pip (if you must)
pip install plotty[vpype]
```

**Verify Installation:**
```bash
uv run plotty --version
# Should show: ploTTY 1.0.1
```

---

## 📊 2. Add Your First Design (1 minute)

### Option A: Use Example Design
```bash
# Create test design
uv run plotty add demo --src https://example.com/simple-design.svg --name my_first_plot
```

### Option B: Use Your Own SVG
```bash
# Add your design
uv run plotty add my_design.svg --name my_first_plot --paper a4
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
uv run plotty plot my_first_plot
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
1. **ploTTY analyzes** your SVG for optimal plotting path
2. **AxiDraw moves** the pen following optimized routes
3. **Progress tracking** shows real-time completion
4. **Automatic recording** captures the process (if camera enabled)

---

## 🎉 4. Success! (30 seconds)

### View Results
```bash
# Job information
uv run plotty info job my_first_plot

# View generated report
# Open: workspace/jobs/my_first_plot/report.html
```

**Expected Report:**
- Total plot time: 7m 42s
- Pen changes: 0
- Total distance: 2.3m
- Quality score: 98.5%

---

## 🔄 What's Next? (1.5 minutes)

### Immediate Next Steps
```bash
# Try multi-pen design
uv run plotty add colorful_design.svg --name rainbow_test

# Plan multiple jobs
uv run plotty add "*.svg" --name batch_test

# Explore all commands
uv run plotty --help
```

### Learning Paths

**🎨 Creative Integration (5 minutes)**
- Want to create generative art? → [vsketch Integration Guide](vpype-plotty.md)
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
uv run plotty check ready

# Test AxiDraw connection
uv run plotty check servo

# View all jobs
uv run plotty list jobs
```

### Common Issues
| Problem | Quick Solution |
|---------|----------------|
| "Device not found" | `uv run plotty check ready` |
| "Permission denied" | `sudo usermod -a -G dialout $USER` |
| "SVG too complex" | Use `--preset hq` for better optimization |

### Get More Help
- **📚 Full Documentation**: [User Guide](user-guide.md)
- **🎨 Creative Integration**: [vpype-plotty Guide](vpype-plotty.md)
- **🐛 Troubleshooting**: [Troubleshooting Guide](troubleshooting/)
- **💬 Community**: [GitHub Discussions](https://github.com/your-org/plotty/discussions)

---

## 🎯 You Did It!

**In 5 minutes you:**
✅ Installed ploTTY  
✅ Added your first design  
✅ Started your first plot  
✅ Learned the basics

**Ready for more?**
- 🎨 [Creative workflows](vpype-plotty.md) - vsketch, vpype integration
- 📊 [Production features](user-guide.md) - Batch jobs, multi-pen
- ⚙️ [Advanced configuration](api/configuration-schema.md) - Custom optimization

**Happy plotting! 🎉**

---

*This quickstart covers the essential ploTTY workflow. For comprehensive features, advanced workflows, and detailed configuration, see the full [User Guide](user-guide.md).*