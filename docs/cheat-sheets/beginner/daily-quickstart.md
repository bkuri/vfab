# Daily Quick Start Cheat Sheet

**5 commands you'll use every day** - Print this and keep it by your plotter!

---

## 🧭 Quick Navigation
- **New to vfab?** Start with [First Plot Checklist](first-plot-checklist.md)
- **Need more commands?** [Common Commands Reference](common-commands.md)
- **Something wrong?** [Troubleshooting Basics](troubleshooting-basics.md)
- **Ready for more?** [Multi-Pen Workflow](../creative/multi-pen-workflow.md)

---

## 🌅 Morning Setup (2 minutes)

```bash
# 1. Check everything is ready
vfab check ready

# 2. See today's queue
vfab list queue

# 3. Quick status overview
vfab status
```

**Expected output:** ✅ Device ready, ✅ Database healthy, X jobs pending

---

## 📋 Add New Design (30 seconds)

```bash
# Quick add with defaults
vfab add my_design.svg

# Add with custom name
vfab add my_design.svg --name "My Art"

# Add with paper size
vfab add my_design.svg --paper a4 --name "Today's Art"
```

**Expected output:** ✅ Added job: my_design (47 points, ~2 minutes)

---

## ⚡ Plan & Plot (1 minute)

```bash
# Plan with defaults (fast optimization)
vfab plan my_design

# Interactive planning (better for new designs)
vfab plan my_design --interactive

# Start plotting
vfab plot my_design
```

**Interactive planning tips:**
- Choose **1 (Fast)** for simple designs
- Choose **2 (High Quality)** for complex art
- Press Enter to accept defaults

---

## 📊 Check Results (30 seconds)

```bash
# Job information
vfab info job my_design

# View report (opens in browser)
# Open: workspace/jobs/my_design/report.html
```

**Key info to look for:**
- ✅ Success status
- ⏱️ Actual vs estimated time
- 📊 Optimization improvement

---

## 🧹 End of Day (1 minute)

```bash
# Clean up completed jobs
vfab queue cleanup --state completed

# Quick daily stats
vfab stats summary --today

# Check device for tomorrow
vfab check ready
```

---

## 🚨 Quick Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| Device not found | Check USB cable, try different port |
| Poor line quality | `vfab check servo` |
| Job stuck | `vfab recovery list` |
| Camera not working | Skip camera for now (optional) |

---

## 💡 Pro Tips

**Save time with these shortcuts:**

```bash
# Add and plan in one step
vfab add design.svg --name "Art" && vfab plan Art

# Plan all pending jobs
vfab plan-all --preset fast

# Plot all planned jobs
vfab plot-all
```

**Daily routine checklist:**
- [ ] Device connected and powered
- [ ] Paper loaded correctly
- [ ] Pen in good condition
- [ ] Camera working (if using)
- [ ] Workspace clear

---

## 📞 Need Help?

```bash
# Quick help for any command
vfab --help
vfab add --help
vfab plot --help

# System info for support
vfab info system
```

---

**🎯 Goal:** Make this 5-minute routine automatic. Once it becomes muscle memory, you're ready for advanced features!

**📚 Next:** [First Plot Checklist](first-plot-checklist.md) for detailed step-by-step guidance.