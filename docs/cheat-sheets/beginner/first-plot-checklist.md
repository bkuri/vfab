# First Plot Checklist

**Never miss a step** - Follow this checklist for perfect first plots every time.

---

## 🧭 Quick Navigation
- **Daily routine?** [Daily Quick Start](daily-quickstart.md)
- **Need command help?** [Common Commands](common-commands.md)
- **Having issues?** [Troubleshooting Basics](troubleshooting-basics.md)
- **Ready for color?** [Multi-Pen Workflow](../creative/multi-pen-workflow.md)

---

## 📋 Pre-Plot Checklist (5 minutes)

### 🔌 Hardware Setup
- [ ] **AxiDraw connected** to USB port
- [ ] **Power adapter** plugged in and solid green light
- [ ] **USB cable** securely connected (try different port if issues)
- [ ] **Plotter on** flat, stable surface

### 📄 Paper & Pen Setup  
- [ ] **Paper loaded** correctly in plotter
- [ ] **Paper guides** snug against paper edges
- [ ] **Pen in holder** with cap removed
- [ ] **Pen tip** extends ~2mm below holder
- [ ] **Pen works** (test on scrap paper first)

### 💻 Software Check
- [ ] **ploTTY running** (`plotty --version` works)
- [ ] **Device detected** (`plotty check device`)
- [ ] **Database ready** (`plotty check database`)

---

## 🎯 Design Preparation (2 minutes)

### ✅ SVG File Check
- [ ] **File exists** and is accessible
- [ ] **SVG is valid** (opens in browser/Inkscape)
- [ ] **Size appropriate** for paper (not larger than paper)
- [ ] **Vector paths only** (no bitmap images)

### 📏 Size Verification
```bash
# Quick check your design
plotty add your_design.svg --dry-run
```

**Look for:**
- ✅ Dimensions fit your paper
- ✅ Reasonable point count (<10,000 for first plot)
- ✅ No error messages

---

## 🚀 Plotting Process (5-10 minutes)

### 1️⃣ Add Your Design
```bash
# Add with descriptive name
plotty add your_design.svg --name "My First Plot"
```

**Expected output:**
```
✅ Added job: my_first_plot
📊 Analysis results:
  - Dimensions: 150mm × 100mm  
  - Points: 1,247
  - Estimated time: 8 minutes
  - Layers detected: 1
```

### 2️⃣ Plan the Job
```bash
# Interactive planning (recommended for beginners)
plotty plan my_first_plot --interactive
```

**Interactive prompts:**
```
Choose optimization [1]: 1  # Press Enter for Fast
```

### 3️⃣ Final Check Before Plotting
- [ ] **Pen cap removed**
- [ ] **Paper flat** and secured
- [ ] **Area clear** around plotter
- [ ] **Time available** for full plot
- [ ] **Phone ready** to record (optional)

### 4️⃣ Start Plotting
```bash
# Begin plotting
plotty plot my_first_plot
```

**During plotting:**
- 🖊️ Watch first few minutes closely
- ⏸️ Press Space to pause if needed
- 📱 Take photo/video if desired
- ⏱️ Note actual time vs estimate

---

## ✅ Post-Plot Checklist (2 minutes)

### 🖊️ Quality Check
- [ ] **Lines complete** (no missing sections)
- [ ] **Line quality good** (consistent darkness)
- [ ] **No pen skips** or jagged lines
- [ ] **Design within bounds** (didn't run off paper)

### 📊 Results Review
```bash
# Check job details
plotty info job my_first_plot

# View detailed report
# Open: workspace/jobs/my_first_plot/report.html
```

### 🧹 Cleanup
- [ ] **Replace pen cap** if not plotting more
- [ ] **Remove paper** carefully
- [ ] **Clear workspace** for next plot
- [ ] **Note any issues** for next time

---

## 🚨 Troubleshooting Guide

| Issue | Immediate Action | Follow-up |
|-------|------------------|-----------|
| **Device not found** | Check USB connection, try different port | `plotty check device` |
| **Pen not drawing** | Check pen tip, try new pen | `plotty check servo` |
| **Lines too light** | Lower pen position slightly | `plotty config device --pen-down 35` |
| **Plot runs off paper** | Check design size, paper position | `plotty add design.svg --dry-run` |
| **Job stuck** | Press Space to pause, then A to abort | `plotty recovery list` |

---

## 💡 Pro Tips for First Plots

**Before you start:**
- 🎯 **Use simple designs** first (basic shapes, text)
- 📏 **Test with cheap paper** before using expensive materials
- 🖊️ **Have spare pens** ready

**During plotting:**
- 👀 **Stay nearby** for first few minutes
- 📱 **Record video** to review pen movement
- ⏸️ **Don't hesitate to pause** if something looks wrong

**After plotting:**
- 📊 **Compare actual vs estimated time**
- 📝 **Take notes** on what worked well
- 🎯 **Try one improvement** next time

---

## 📞 Quick Help Commands

```bash
# If anything goes wrong
plotty check ready          # Full system check
plotty status               # Current status
plotty info system          # System info for support
plotty recovery list        # Recovery options
```

---

## ✨ Success Criteria

**Your first plot is successful when:**
- ✅ Design completes without errors
- ✅ Lines are visible and complete
- ✅ Plot stays within paper boundaries
- ✅ Actual time is reasonable (within 50% of estimate)
- ✅ You feel confident to try another

---

**🎯 Goal:** Complete this checklist without thinking. Once it becomes automatic, you're ready for [Common Commands](common-commands.md)!

**📚 Next Steps:** 
- Try 3 more simple designs using this checklist
- Move to [Common Commands](common-commands.md) to learn more options
- Explore [Multi-Pen Workflow](../creative/multi-pen-workflow.md) when ready for colors