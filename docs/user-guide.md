# ploTTY User Guide

**Purpose:** Master pen plotting productivity with ploTTY - from your first plot to professional studio management.

---

## Table of Contents

🚀 [Quick Start](#quick-start) - 5-minute setup for beginners

**🌱 Beginner Path** (Learn the basics)
1. [Getting Started](#1-getting-started) - Installation & first setup
2. [Your First Plot](#2-your-first-plot) - Complete walkthrough
3. [Common Tasks](#3-common-tasks) - Everyday plotting needs

**🎨 Creative Path** (Express yourself)
4. [Multi-Pen Artwork](#4-multi-pen-artwork) - Colorful designs
5. [Creative Tool Integration](#5-creative-tool-integration) - vsketch, vpype, and more
6. [Artistic Workflows](#6-artistic-workflows) - From sketch to final piece

**⚡ Power User Path** (Professional productivity)
7. [Batch Production](#7-batch-production) - Efficient workflows
8. [Advanced Optimization](#8-advanced-optimization) - Fine-tune performance
9. [Studio Management](#9-studio-management) - Professional operations

**📚 Reference**
10. [Real-Time Monitoring](#10-real-time-monitoring) - WebSocket dashboard & alerts
11. [Real-World Examples](#11-real-world-examples) - Industry workflows
12. [Troubleshooting](#12-troubleshooting) - Quick fixes
13. [Best Practices](#13-best-practices) - Pro tips

---

## 🚀 Quick Start

**New to ploTTY? Get plotting in 5 minutes!**

```bash
# 1. Install ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty
uv pip install -e ".[dev,vpype,axidraw]"
uv run alembic upgrade head

# 2. Quick setup
plotty setup  # Accept defaults for now

# 3. Add your first design
plotty add your_design.svg --paper a4

# 4. Plot it!
plotty plot your_design
```

That's it! 🎉 You're plotting. For detailed setup, see [Getting Started](#1-getting-started).

---

# 🌱 Beginner Path

## 1. Getting Started

### 1.1 What is ploTTY?

ploTTY is your **pen plotting productivity assistant** that helps you:
- 📋 **Queue jobs** - Line up multiple designs
- ⚡ **Optimize automatically** - Faster plotting, better results  
- 🖊️ **Manage pens** - Switch between colors/sizes seamlessly
- ⏱️ **Track time** - Know exactly how long each job takes
- 📹 **Record sessions** - Document your creative process
- 🔄 **Recover gracefully** - Pick up where you left off after crashes

### 1.2 System Requirements

**Minimum Setup:**
- Python 3.11+
- 2GB RAM
- 100MB disk space
- USB port (for AxiDraw)

**Recommended Setup:**
- 4GB RAM
- 1GB disk space
- IP camera for recording
- Multiple pens for complex designs

### 1.3 Installation

```bash
# Step 1: Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Step 2: Clone ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty

# Step 3: Install with hardware support
uv pip install -e ".[dev,vpype,axidraw]"

# Step 4: Initialize database
uv run alembic upgrade head
```

> **💡 Tip:** Run `plotty --version` to verify installation.

### 1.4 First-Time Setup

```bash
# Run the interactive setup wizard
plotty setup
```

**Setup walkthrough:**
```
🔧 ploTTY Setup Wizard
======================

Device Configuration:
  AxiDraw port [/dev/ttyUSB0]: [Press Enter for default]
  Device model [1]: [Press Enter for AxiDraw v3]
  Pen up position [60]: [Press Enter]
  Pen down position [40]: [Press Enter]

Paper Settings:
  Default paper size [A4]: [Press Enter]
  Default margin [10mm]: [Press Enter]
  Default orientation [portrait]: [Press Enter]

Camera Setup (optional):
  Camera URL [http://localhost:8881/stream.mjpeg]: [Press Enter to skip]
  Enable recording [y]: n [Press Enter to skip for now]

✅ Configuration saved to config/config.yaml
🎉 Ready to plot!
```

> **🎯 Goal:** Accept all defaults for your first setup. You can customize later.

## 2. Your First Plot

Let's walk through your complete first plotting experience.

### 2.1 Prepare Your Design

**Your SVG should be:**
- ✅ Vector paths only (no images/bitmaps)
- ✅ Reasonable complexity (<10,000 points for starters)
- ✅ Properly sized for your paper

**Quick test SVG** (save as `test.svg`):
```xml
<svg width="200mm" height="150mm" viewBox="0 0 200 150">
  <!-- Simple test pattern -->
  <rect x="10" y="10" width="180" height="130" 
        fill="none" stroke="black" stroke-width="0.5"/>
  <circle cx="100" cy="75" r="30" 
          fill="none" stroke="black" stroke-width="0.5"/>
  <text x="100" y="75" text-anchor="middle" 
        font-family="Arial" font-size="12" fill="black">
    My First Plot!
  </text>
</svg>
```

### 2.2 Add Your First Job

```bash
# Add the test design
plotty add test.svg --paper a4

# Add with a friendly name
plotty add test.svg --name "My First Plot" --paper a4
```

**What you'll see:**
```
✅ Added job: test
📊 Analysis results:
  - Dimensions: 200mm × 150mm
  - Points: 47
  - Estimated time: 2 minutes
  - Layers detected: 1
```

> **💡 Success Tip:** If you get an error, check that your SVG file exists and is valid.

### 2.3 Plan the Job

Planning optimizes your design for faster plotting.

```bash
# Interactive planning (perfect for beginners)
plotty plan test --interactive
```

**Interactive walkthrough:**
```
🎨 Layer Analysis
==================
Detected 1 layer:
  🔵 Layer 1: "default" (47 points) - BLACK

📝 Optimization Options
========================
1. Fast (default) - Quick optimization, great for simple designs
2. High Quality - Better path optimization, takes longer
3. Custom - Enter your own vpype commands

Choose optimization [1]: [Press Enter for Fast]

⏱️ Time Estimation
==================
Pre-optimization: 2.1 minutes
Post-optimization: 1.8 minutes (14% faster)

✅ Job planned successfully
```

### 2.4 Plot It!

Make sure your AxiDraw is connected and has paper loaded, then:

```bash
# Start plotting
plotty plot test
```

**Real-time progress display:**
```
🖊️ Plotting: test
==================
Progress: ████████████████████ 67%
Time remaining: 0m 45s
Current layer: default (1/1)
Pen: Black 0.5mm
Speed: 25% (medium)

Controls:
  [Space] Pause/Resume
  [A] Abort  
  [S] Skip to next layer
```

> **🎯 First Plot Success!** Press Space to pause if needed, or just let it finish.

### 2.5 Check Your Results

```bash
# See job details
plotty info job test

# View the generated report
# Open: workspace/jobs/test/report.html in your browser
```

**Report includes:**
- 📊 Plot time statistics
- 🖼️ Camera recording (if enabled)
- 📈 Performance metrics
- ✅ Success confirmation

---

## 3. Common Tasks

Master the everyday operations you'll use frequently.

### 3.1 Job Management

**View what's queued:**
```bash
# List all jobs
plotty list jobs

# See current queue
plotty list queue

# Check job status
plotty info job test
```

**Remove jobs:**
```bash
# Remove specific job
plotty remove job test

# Clear completed jobs
plotty queue cleanup --state completed
```

### 3.2 Quick Plotting Workflow

**Your daily plotting routine:**
```bash
# 1. Add new design
plotty add new_design.svg --name "Today's Art" --paper a4

# 2. Plan it (interactive is best)
plotty plan new_design --interactive

# 3. Plot it
plotty plot new_design

# 4. Check results
plotty info job new_design
```

### 3.3 Paper and Pen Basics

**Check available paper:**
```bash
plotty list paper
```

**Add custom paper size:**
```bash
plotty add paper \
  --name "Square" \
  --width 150 \
  --height 150 \
  --margin 10
```

**Basic pen management:**
```bash
# List pens
plotty list pens

# Add a new pen
plotty add pen \
  --name "Fine Black" \
  --width 0.3 \
  --color "#000000"
```

### 3.4 Status and Health Checks

**Quick system check:**
```bash
# Is everything ready?
plotty check ready

# Detailed status
plotty status

# Test device movement
plotty check device --test-move
```

**Common status outputs:**
```
✅ Device: Connected (/dev/ttyUSB0)
✅ Database: Healthy
✅ Queue: 2 jobs pending
⚠️  Camera: Not configured (optional)
```

### 3.5 Time Estimation

**Know how long jobs will take:**
```bash
# Quick estimate
plotty estimate job_name

# Detailed breakdown
plotty estimate job_name --detailed

# Compare before/after optimization
plotty estimate job_name --stage pre
plotty estimate job_name --stage post
```

**Sample output:**
```
⏱️ Time Estimation: complex_design
==================================
Pre-optimization: 12.4 minutes
Post-optimization: 8.7 minutes (30% faster)

Time saved: 3.7 minutes - worth the wait!
```

> **🎯 Beginner Goal:** Get comfortable with this workflow. Once it feels natural, you're ready for the [Creative Path](#-creative-path).

---

# 🎨 Creative Path

## 4. Multi-Pen Artwork

Create colorful, multi-layered designs with automatic pen management.

### 4.1 Understanding Multi-Pen Detection

ploTTY automatically detects when your design needs multiple pens from:

**SVG Layers** (Inkscape, Illustrator, etc.):
```xml
<svg>
  <g inkscape:label="outline">
    <path d="M10,10 L100,100" stroke="black" stroke-width="0.5"/>
  </g>
  <g inkscape:label="shading">
    <path d="M20,20 L90,90" stroke="gray" stroke-width="0.3"/>
  </g>
  <g inkscape:label="highlights">
    <path d="M30,30 L80,80" stroke="white" stroke-width="0.2"/>
  </g>
</svg>
```

**AxiDraw Layer Comments**:
```svg
<!-- %layer: outline -->
<path d="M10,10 L100,100" stroke="black" stroke-width="0.5"/>

<!-- %layer: shading -->
<path d="M20,20 L90,90" stroke="gray" stroke-width="0.3"/>
```

### 4.2 Setting Up Your Pen Collection

**View current pens:**
```bash
plotty list pens
```

**Add pens interactively:**
```bash
plotty setup pen
```

**Add specific pens:**
```bash
# Fine detail pen
plotty add pen \
  --name "Fine Black" \
  --width 0.3 \
  --color "#000000" \
  --speed-cap 50

# Medium workhorse pen
plotty add pen \
  --name "Medium Black" \
  --width 0.7 \
  --color "#000000" \
  --speed-cap 80

# Color pens
plotty add pen \
  --name "Fine Red" \
  --width 0.3 \
  --color "#FF0000" \
  --speed-cap 50

plotty add pen \
  --name "Medium Blue" \
  --width 0.5 \
  --color "#0000FF" \
  --speed-cap 70
```

**Your pen database:**
```
📊 Available Pens
================
1. Fine Black (0.3mm) - #000000
2. Medium Black (0.7mm) - #000000  
3. Fine Red (0.3mm) - #FF0000
4. Medium Blue (0.5mm) - #0000FF
```

### 4.3 Planning Multi-Pen Artwork

**Add your colorful design:**
```bash
plotty add colorful_art.svg --paper a4 --name "Rainbow Design"
```

**Interactive pen mapping:**
```bash
plotty plan colorful_art --interactive
```

**Pen mapping walkthrough:**
```
🎨 Multi-Pen Layer Detection
============================
Detected 3 layers:
  🔵 Layer 1: "outline" (523 points) - BLACK
  🟢 Layer 2: "fill" (1,247 points) - GRAY  
  🟡 Layer 3: "highlights" (89 points) - WHITE

Available pens:
  [1] Fine Black 0.3mm
  [2] Medium Black 0.7mm
  [3] Fine Red 0.3mm
  [4] Medium Blue 0.5mm

Map layers to pens (e.g. "1,2,3"): 2,1,3

🔄 Pen Change Optimization
=========================
Original pen changes: 6
Optimized pen changes: 2 (67% reduction)
Time saved: ~4 minutes

✅ Pen mapping saved
```

> **💡 Pro Tip:** Map similar colors together (e.g., all dark colors with the same pen) to minimize pen changes.

### 4.4 Plotting Multi-Pen Artwork

**Start your colorful plot:**
```bash
plotty plot colorful_art
```

**During plotting - pen change prompts:**
```
🖊️ Plotting: colorful_art
==============================
Layer 1/3: outline (Pen: Medium Black)
██████████████████████████████ 100%

🔄 Pen Change Required
======================
Next layer: "fill" (requires Fine Red pen)
Please change pen now...

[Enter] Continue | [S] Skip layer | [A] Abort
```

**Pen change tips:**
- 🖊️ **Gentle swaps** - Don't force pens into the holder
- 📏 **Check alignment** - Make sure the new pen is centered
- ⏱️ **Quick changes** - Practice makes this faster
- 📝 **Take notes** - Remember which pen numbers are which colors

### 4.5 Multi-Pen Best Practices

**Design for efficient pen changes:**
```xml
<!-- Good: Group similar colors together -->
<g inkscape:label="dark_elements">
  <path stroke="black" .../>
  <path stroke="darkgray" .../>
</g>
<g inkscape:label="light_elements">
  <path stroke="white" .../>
  <path stroke="lightgray" .../>
</g>
```

**Pen optimization strategies:**
- **Color grouping** - Plot all dark colors, then all light colors
- **Pen priority** - Use your most reliable pen for the largest areas
- **Test first** - Do a quick test plot with just the outlines

**Advanced pen mapping:**
```bash
# Plan with custom pen order
plotty plan artwork --pen-order 2,1,4,3

# Optimize for minimum pen changes
plotty plan artwork --optimize-pens

# Preview pen changes without plotting
plotty plan artwork --dry-run --show-pen-changes
```

### 3.2 Setting Up Multiple Pens

```bash
# View current pens
plotty list pens

# Add pens interactively
plotty setup pen

# Add specific pen
plotty add pen \
  --name "Fine Black" \
  --width 0.3 \
  --color "#000000" \
  --speed-cap 50
```

**Pen database example:**
```
📊 Available Pens
=================
1. Fine Black (0.3mm) - #000000
2. Medium Black (0.7mm) - #000000  
3. Fine Red (0.3mm) - #FF0000
4. Medium Blue (0.5mm) - #0000FF
```

### 3.3 Planning Multi-Pen Jobs

```bash
# Add multi-pen design
plotty add colorful_design.svg --paper a4

# Plan with interactive pen mapping
plotty plan colorful_design --interactive
```

**Interactive pen mapping:**
```
🎨 Multi-Pen Layer Detection
=============================
Detected 3 layers:
  🔵 Layer 1: "outline" (523 points) - BLUE
  🟢 Layer 2: "fill" (1,247 points) - GREEN
  🟡 Layer 3: "highlights" (89 points) - YELLOW

Available pens:
  [1] Fine Black 0.3mm
  [2] Medium Black 0.7mm
  [3] Fine Red 0.3mm
  [4] Medium Blue 0.5mm

Map layers to pens (e.g. "1,2,3"): 4,1,3

🔄 Pen Optimization
==================
Original pen changes: 6
Optimized pen changes: 2 (67% reduction)
Time saved: ~4 minutes

✅ Pen mapping saved
```

### 3.4 Plotting Multi-Pen Jobs

```bash
# Plot with pen change prompts
plotty plot colorful_design
```

**During plotting:**
```
🖊️ Plotting: colorful_design
===============================
Layer 1/3: outline (Pen: Medium Blue)
███████████████████████████████ 100%

🔄 Pen Change Required
======================
Next layer: "fill" (requires Fine Red pen)
Please change pen now...

[Enter] Continue | [S] Skip layer | [A] Abort
```

## 5. Creative Tool Integration

Connect ploTTY with your favorite creative tools for seamless workflows.

### 5.1 vsketch + vpype-plotty (Recommended)

**Setup vsketch integration:**
```bash
# Install vpype-plotty plugin for vsketch
pipx inject vsketch vpype-plotty
```

**Basic vsketch workflow:**
```python
import vsketch

class MyDesign(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")
        
        # Your creative code
        for i in range(10):
            vsk.circle(i * 2, i * 2, radius=1)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        # Optimize in vsketch
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Send to ploTTY queue
        vsk.vpype("plotty-add --name my_design --preset hq --queue")

if __name__ == "__main__":
    MyDesign().display()
```

**Advanced vsketch with parameters:**
```python
class GenerativeArt(vsketch.SketchClass):
    # Interactive parameters
    complexity = vsketch.Param(50, min=10, max=200, step=10)
    density = vsketch.Param(10, min=1, max=50)
    style = vsketch.Param("geometric", choices=["geometric", "organic", "mixed"])
    
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4")
        vsk.scale("cm")
        
        # Generate based on parameters
        for i in range(self.complexity):
            with vsk.pushMatrix():
                vsk.rotate(i * 0.1)
                vsk.translate(
                    vsk.randomGaussian() * self.density * 0.1,
                    vsk.randomGaussian() * self.density * 0.1
                )
                
                if self.style == "geometric":
                    vsk.rect(0, 0, 0.5, 0.5)
                elif self.style == "organic":
                    vsk.circle(0, 0, radius=0.3)
                else:
                    vsk.polygon([(0, 0), (0.5, 0.2), (0.3, 0.5)])
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Dynamic naming based on parameters
        job_name = f"{self.style}_c{self.complexity}_d{self.density}"
        vsk.vpype(f"plotty-add --name '{job_name}' --preset hq --queue")

if __name__ == "__main__":
    GenerativeArt().display()
```

### 5.2 Direct vpype Integration

**For existing SVG files:**
```bash
# Add existing design to ploTTY
vpype read my_art.svg plotty-add --name "My Art" --preset fast

# Create generative art and queue directly
vpype rand --seed 123 plotty-add --name "Random Art 123" --paper A3 --queue

# Process and optimize in one step
vpype read design.svg linemerge linesimplify \
    plotty-add --name "Optimized Design" --preset none
```

**Batch generation with vpype:**
```bash
# Create a series of variations
for seed in {1..10}; do
    vpype rand --seed $seed \
        plotty-add --name "Variation $seed" --preset fast --queue
done

# Geometric patterns
for i in {1..5}; do
    vpype rect --grid 4x$i --spacing 20mm \
        plotty-add --name "Grid $i" --queue
done
```

### 5.3 Multi-Pen vsketch Integration

**Create multi-layer designs programmatically:**
```python
class MultiLayerArt(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4")
        vsk.scale("cm")
        
        # Layer 1: Black outlines (stroke 1)
        vsk.stroke(1)
        vsk.penWidth("0.3mm", 1)
        for i in range(5):
            vsk.rect(i * 3, i * 2, 2, 2)
        
        # Layer 2: Red details (stroke 2)
        vsk.stroke(2)
        vsk.penWidth("0.2mm", 2)
        for i in range(5):
            vsk.circle(i * 3 + 1, i * 2 + 1, radius=0.5)
        
        # Layer 3: Blue accents (stroke 3)
        vsk.stroke(3)
        vsk.penWidth("0.5mm", 3)
        for i in range(5):
            vsk.line(i * 3, i * 2, i * 3 + 2, i * 2 + 2)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")
        vsk.vpype("plotty-add --name multi_pen_art --preset hq --queue")
```

### 5.4 Integration with Design Software

**Inkscape workflow:**
```bash
# Design in Inkscape, then export
# 1. Create your design in Inkscape
# 2. File > Save As... > SVG
# 3. Use meaningful layer names

# Add to ploTTY queue
vpype read inkscape_design.svg plotty-add --name "Inkscape Art" --preset hq
```

**Adobe Illustrator workflow:**
```bash
# Export from Illustrator
# 1. File > Export > Export As...
# 2. Choose SVG format
# 3. Use "Save Artboards" if you have multiple designs

# Process with ploTTY
vpype read illustrator_art.svg plotty-add --name "Illustrator Design" --queue
```

**Processing/p5.js workflow:**
```javascript
// Processing sketch that exports SVG
void setup() {
  size(400, 400, SVG, "processing_art.svg");  // Direct SVG output
  background(255);
  
  // Your creative code
  for (int i = 0; i < 10; i++) {
    circle(random(width), random(height), random(10, 50));
  }
  
  exit();  // Saves the file and exits
}

// Or interactive export
void draw() {
  if (keyPressed && key == 's') {
    save("processing_sketch.svg");
  }
}
```

```bash
# Queue Processing art
vpype read processing_art.svg plotty-add --name "Processing Sketch" --preset default
```

### 5.5 Creative Project Organization

**Recommended project structure:**
```bash
my_creative_project/
├── sketches/              # vsketch .py files
│   ├── generative_art.py
│   └── multi_pen_design.py
├── output/               # Generated SVGs
│   ├── art_001.svg
│   └── art_002.svg
├── ploppy_workspace/     # ploTTY job data
├── scripts/             # Automation scripts
│   └── batch_generate.py
└── assets/              # Reference materials
    └── inspiration.jpg
```

**Professional naming conventions:**
```python
class ClientProject(vsketch.SketchClass):
    client_name = vsketch.Param("Acme Corp")
    project_type = vsketch.Param("logo", choices=["logo", "pattern", "illustration"])
    version = vsketch.Param("v1")
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Professional job naming
        job_name = f"{self.client_name}_{self.project_type}_{self.version}"
        vsk.vpype(f"plotty-add --name '{job_name}' --preset hq --queue")
```

### 5.6 ⚠️ Critical: Optimization Control

**Understanding optimization prevents double-processing and ensures best results.**

#### **The Optimization Rule**
- **vsketch optimizes** → ploTTY should skip (`--preset none`)
- **ploTTY optimizes** → vsketch should skip optimization
- **Never both** → Avoids double-processing and quality loss

#### **Correct Workflows**

**Workflow 1: vsketch optimizes (Recommended)**
```python
def finalize(self, vsk: vsketch.Vsketch) -> None:
    # vsketch does the optimization
    vsk.vpype("linemerge linesimplify reloop linesort")
    
    # ploTTY skips optimization (already done)
    vsk.vpype("plotty-add --name my_design --preset none --queue")
```

**Workflow 2: ploTTY optimizes**
```python
def finalize(self, vsk: vsketch.Vsketch) -> None:
    # vsketch skips optimization
    # vsk.vpype("linemerge linesimplify reloop linesort")  # Commented out
    
    # ploTTY handles optimization
    vsk.vpype("plotty-add --name my_design --preset hq --queue")
```

**Workflow 3: vpype optimizes, ploTTY skips**
```bash
# vpype optimizes, ploTTY skips
vpype read design.svg linemerge linesimplify \
    plotty-add --name optimized --preset none
```

#### **Quick Reference**

| Tool Doing Optimization | ploTTY Command | When to Use |
|------------------------|----------------|-------------|
| vsketch | `--preset none` | Most vsketch workflows |
| vpype | `--preset none` | When vpype processes first |
| ploTTY | `--preset hq/fast/default` | Raw SVG files |
| None | `--preset none` | Pre-optimized files |

> **🚨 Golden Rule:** Only one tool should optimize. Choose your favorite and stick with it consistently.

---

## 6. Artistic Workflows

Professional workflows from concept to final piece.

### 6.1 Concept Development Workflow

**Step 1: Sketch and test**
```python
# quick_sketch.py - Fast iteration
import vsketch

class QuickSketch(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a5")  # Smaller for quick tests
        vsk.scale("cm")
        
        # Rapid prototyping code
        for i in range(20):
            vsk.circle(
                vsk.random(0, 10), 
                vsk.random(0, 15), 
                radius=vsk.random(0.1, 1.0)
            )
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        # Quick optimization for testing
        vsk.vpype("linemerge linesort")
        vsk.vpype("plotty-add --name 'quick_test' --preset fast --queue")
```

**Step 2: Refine and scale**
```python
# refined_art.py - Production ready
class RefinedArt(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a3")  # Final size
        vsk.scale("cm")
        
        # Polished, intentional design
        for i in range(50):
            with vsk.pushMatrix():
                angle = (i / 50) * 2 * 3.14159
                radius = 5 + i * 0.1
                vsk.translate(
                    10 + radius * math.cos(angle),
                    10 + radius * math.sin(angle)
                )
                vsk.circle(0, 0, radius=0.2)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        # Production optimization
        vsk.vpype("linemerge linesimplify reloop linesort")
        vsk.vpype("plotty-add --name 'refined_piece' --preset hq --queue")
```

### 6.2 Multi-Revision Workflow

**Version control your art:**
```bash
# Create version series
for version in {1..5}; do
    vsk run my_art.py --set complexity=$version \
        --save-only --output "art_v${version}.svg"
    
    vpype read "art_v${version}.svg" \
        plotty-add --name "Art Series v${version}" --queue
done

# Plot all versions
plotty plot-all
```

**Compare versions:**
```bash
# Estimate time for each version
for job in art_series_*; do
    echo "=== $job ==="
    plotty estimate "$job" --detailed
done
```

### 6.3 Client Presentation Workflow

**Professional client deliverables:**
```python
class ClientPresentation(vsketch.SketchClass):
    client_name = vsketch.Param("Acme Corp")
    project_code = vsketch.Param("LOGO-2025")
    
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4")
        vsk.scale("cm")
        
        # Professional logo design
        self.draw_logo(vsk)
        self.add_text_info(vsk)
    
    def draw_logo(self, vsk: vsketch.Vsketch) -> None:
        # Your logo design code
        pass
    
    def add_text_info(self, vsk: vsketch.Vsketch) -> None:
        # Add project metadata as text
        vsk.text(f"{self.client_name} - {self.project_code}", 
                1, 1, size=0.3)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Professional naming
        job_name = f"{self.client_name}_{self.project_code}_final"
        vsk.vpype(f"plotty-add --name '{job_name}' --preset hq --queue")
```

### 6.4 Limited Edition Workflow

**Numbered editions with documentation:**
```bash
# Create limited edition series
edition_size=10
artwork_name="Geometric Harmony"

for edition in $(seq 1 $edition_size); do
    # Generate with unique seed for each edition
    vsk run limited_edition.py --set seed=$((edition * 123)) \
        --set edition_number=$edition \
        --save-only
    
    # Queue with edition naming
    job_name="${artwork_name} - Edition ${edition}/${edition_size}"
    vpype read output.svg \
        plotty-add --name "$job_name" --preset hq --queue
done

# Plot with documentation
plotty plot-all --document-each
```

### 6.5 Exhibition Preparation Workflow

**Gallery-ready artwork:**
```bash
# Prepare multiple pieces for exhibition
exhibition_pieces=("piece1" "piece2" "piece3" "piece4")

for piece in "${exhibition_pieces[@]}"; do
    # Generate at exhibition size
    vsk run "${piece}.py" --set size=a2 --save-only
    
    # Add to queue with exhibition naming
    vpype read "${piece}.svg" \
        plotty-add --name "Exhibition: ${piece}" \
                   --paper a2 --preset hq --queue
    
    # Create test print first
    vpype read "${piece}.svg" \
        plotty-add --name "Test: ${piece}" \
                   --paper a4 --preset fast --queue
done

# Plot test versions first
plotty plot "Test:*"

# After approval, plot full size
plotty plot "Exhibition:*"
```

> **🎯 Creative Goal:** Develop workflows that match your artistic process. Use these as templates and adapt them to your unique style.

---

# ⚡ Power User Path

## 7. Batch Production

Professional workflows for high-volume plotting operations.

### 7.1 Project Organization

**Create structured project directories:**
```bash
# Professional project setup
mkdir -p client_acme/{designs,output,documentation}
cd client_acme

# Add all client designs
plotty add designs/logo.svg --name "Acme Logo" --paper a4
plotty add designs/business_card.svg --name "Acme Business Card" --paper a4
plotty add designs/letterhead.svg --name "Acme Letterhead" --paper a4
```

**Batch import from directory:**
```bash
# Import all SVGs from a directory
for file in designs/*.svg; do
    basename=$(basename "$file" .svg)
    plotty add "$file" --name "Acme: $basename" --paper a4
done
```

### 7.2 Intelligent Batch Planning

**Plan all jobs with optimization:**
```bash
# Fast batch planning (good for simple designs)
plotty plan-all --preset fast

# High-quality batch planning (complex designs)
plotty plan-all --preset hq

# Smart pen optimization across all jobs
plotty plan-all --optimize-pens --global-pen-order
```

**Selective batch planning:**
```bash
# Plan specific jobs with custom settings
plotty plan "Acme Logo" "Acme Business Card" --preset hq

# Plan by pattern matching
plotty plan "Acme:*" --preset fast

# Plan jobs added today
plotty plan --added-today --preset default
```

**Advanced batch planning options:**
```bash
# Plan with time constraints
plotty plan-all --max-time-per-job 30m --preset fast

# Plan with pen change minimization
plotty plan-all --minimize-pen-changes --pen-priority 2,1,3

# Dry run to see planning results
plotty plan-all --dry-run --show-estimates
```

### 7.3 Automated Batch Plotting

**Standard batch execution:**
```bash
# Plot all planned jobs
plotty plot-all

# Plot with safety preset (slower but more reliable)
plotty plot-all --preset safe

# Plot with automatic camera recording
plotty plot-all --record-all
```

**Advanced batch plotting:**
```bash
# Plot with time limits
plotty plot-all --max-total-time 4h

# Plot with automatic pen change prompts
plotty plot-all --auto-pen-change

# Plot with progress monitoring
plotty plot-all --monitor --notify-on-complete
```

**Conditional batch plotting:**
```bash
# Only plot jobs under 15 minutes
plotty plot-all --max-job-time 15m

# Plot high-priority jobs first
plotty plot-all --priority-order

# Plot with automatic retry on failure
plotty plot-all --retry-failed --max-retries 2
```

### 7.4 Queue Management and Monitoring

**Real-time queue monitoring:**
```bash
# Watch queue progress
plotty list queue --watch

# Detailed queue status
plotty list queue --detailed --show-estimates

# Export queue status for reporting
plotty list queue --json > queue_status_$(date +%Y%m%d).json
```

**Automated queue cleanup:**
```bash
# Remove completed jobs
plotty queue cleanup --state completed

# Remove old jobs (older than 7 days)
plotty queue cleanup --older-than 7d

# Remove failed jobs
plotty queue cleanup --state failed

# Comprehensive cleanup
plotty queue cleanup --completed --failed --older-than 3d
```

**Queue organization:**
```bash
# Group jobs by project
plotty queue group --by-project "Acme"

# Reorder queue by priority
plotty queue reorder --by-time-estimate

# Pause specific jobs
plotty queue pause "Acme:*"

# Resume paused jobs
plotty queue resume "Acme:*"
```

### 7.5 Production Reporting

**Generate production reports:**
```bash
# Daily production summary
plotty stats production --date today --export > daily_report.json

# Client-specific reports
plotty stats jobs --client "Acme" --last 30 --export > acme_report.json

# Performance analytics
plotty stats performance --pen-usage --time-analysis --export > performance.json
```

**Automated reporting script:**
```bash
#!/bin/bash
# production_report.sh - Daily production reporting

DATE=$(date +%Y-%m-%d)
REPORT_DIR="reports/$DATE"
mkdir -p "$REPORT_DIR"

# Generate comprehensive report
{
    echo "# Production Report - $DATE"
    echo ""
    echo "## Queue Status"
    plotty list queue --detailed
    echo ""
    echo "## Today's Performance"
    plotty stats summary --today
    echo ""
    echo "## Pen Usage"
    plotty stats pens --last 7
    echo ""
    echo "## Failed Jobs"
    plotty list jobs --state failed --today
} > "$REPORT_DIR/production_report.md"

# Export machine-readable data
plotty stats production --date today --json > "$REPORT_DIR/production_data.json"

echo "Report generated: $REPORT_DIR/production_report.md"
```

### 7.6 Advanced Batch Automation

**Intelligent batch processing:**
```python
# smart_batch.py - Intelligent batch processing
import subprocess
import json
import time

def smart_batch_process(project_name, max_total_time_hours=4):
    """Process batch with intelligent optimization."""
    
    # Add all project files
    subprocess.run([
        "uv", "run", "plotty", "add", f"{project_name}/*.svg",
        "--name", f"{project_name}_batch", "--paper", "a4"
    ])
    
    # Plan with time constraints
    result = subprocess.run([
        "uv", "run", "plotty", "plan-all", 
        "--preset", "fast",
        "--max-time-per-job", "30m"
    ], capture_output=True, text=True)
    
    # Check total estimated time
    if "Total estimated time" in result.stdout:
        # Parse total time and adjust if needed
        total_time = parse_time_from_output(result.stdout)
        if total_time > max_total_time_hours * 3600:
            print("⚠️ Batch too long, splitting into smaller groups")
            split_batch_processing(project_name)
        else:
            # Start batch plotting
            subprocess.run([
                "uv", "run", "plotty", "plot-all",
                "--monitor", "--notify-on-complete"
            ])

def split_batch_processing(project_name):
    """Split large batch into manageable chunks."""
    # Implementation for splitting large batches
    pass

if __name__ == "__main__":
    smart_batch_process("client_acme")
```

> **🎯 Power User Goal:** Build automated workflows that minimize manual intervention while maximizing quality and efficiency.

## 8. Advanced Optimization

Fine-tune every aspect of plotting performance and quality.

### 8.1 Understanding Optimization Presets

ploTTY includes three optimization levels:

**Fast Preset** (Quick processing):
```yaml
fast: "read {src} pagesize {pagesize} crop 0 0 {width_mm}mm {height_mm}mm linemerge linesort write {dst}"
```
- ✅ Quick processing
- ✅ Good for simple designs
- ⚠️ Less path optimization

**Default Preset** (Balanced):
```yaml
default: "read {src} pagesize {pagesize} crop 0 0 {width_mm}mm {height_mm}mm linemerge linesort linesimplify write {dst}"
```
- ✅ Balanced speed/quality
- ✅ Good for most designs
- ✅ Reasonable optimization

**High Quality Preset** (Maximum optimization):
```yaml
hq: "read {src} pagesize {pagesize} crop 0 0 {width_mm}mm {height_mm}mm linemerge linesort linesimplify reloop write {dst}"
```
- ✅ Best path optimization
- ✅ Minimal pen lifts
- ⏰ Longer processing time

### 8.2 Custom Optimization Pipelines

**Create your own optimization:**
```bash
# Custom pipeline for specific needs
plotty plan job --custom "read {src} linemerge linesort write {dst}"

# Advanced custom pipeline
plotty plan job --custom "read {src} linemerge linesimplify reloop linesort write {dst}"

# Minimal optimization (for already optimized files)
plotty plan job --custom "read {src} write {dst}"
```

**Custom optimization examples:**
```bash
# For geometric designs (focus on line merging)
plotty plan geometric_design \
  --custom "read {src} linemerge --tolerance 0.1mm linesort write {dst}"

# For organic designs (focus on line simplification)
plotty plan organic_art \
  --custom "read {src} linesimplify --tolerance 0.05mm linesort write {dst}"

# For text-heavy designs (preserve detail)
plotty plan typography \
  --custom "read {src} linemerge --tolerance 0.01mm linesort write {dst}"
```

### 8.3 Optimization Comparison and Testing

**Compare different presets:**
```bash
# Test all presets on the same job
plotty plan test_job --preset fast --dry-run --save-as fast_test
plotty plan test_job --preset default --dry-run --save-as default_test
plotty plan test_job --preset hq --dry-run --save-as hq_test

# Compare results
plotty compare fast_test default_test hq_test --show-time-estimates
```

**Detailed time analysis:**
```bash
# Comprehensive time breakdown
plotty estimate job --detailed --show-optimization-steps

# Compare pre/post optimization
plotty estimate job --stage pre --save pre_estimate
plotty estimate job --stage post --save post_estimate
plotty compare pre_estimate post_estimate --show-improvement
```

**Sample detailed output:**
```
⏱️ Detailed Time Estimation: complex_art
=========================================
Pre-optimization Analysis:
  - Total path length: 15,234mm
  - Pen lifts: 47
  - Direction changes: 234
  - Estimated drawing time: 12.4 minutes
  - Pen change time: 0 minutes
  - Total time: 12.4 minutes

Post-optimization Analysis:
  - Total path length: 12,891mm (15% reduction)
  - Pen lifts: 23 (51% reduction)
  - Direction changes: 156 (33% reduction)
  - Estimated drawing time: 8.7 minutes
  - Pen change time: 0 minutes
  - Total time: 8.7 minutes

Optimization Summary:
  - Time saved: 3.7 minutes (30% faster)
  - Path efficiency: 15% improvement
  - Pen lift reduction: 51% fewer lifts
  - Processing time: 45 seconds
```

### 8.4 Advanced Pen Optimization

**Global pen optimization across jobs:**
```bash
# Optimize pen changes across entire queue
plotty optimize-pens --global --queue-wide

# Custom pen change priority
plotty optimize-pens --pen-order 2,1,3,4 --minimize-distance

# Pen optimization with time constraints
plotty optimize-pens --max-pen-change-time 30s --prefer-fewer-changes
```

**Pen optimization strategies:**
```bash
# Strategy 1: Minimize total pen changes
plotty plan-all --optimize-pens --strategy min-changes

# Strategy 2: Minimize pen change time
plotty plan-all --optimize-pens --strategy min-time

# Strategy 3: Optimize for pen wear
plotty plan-all --optimize-pens --strategy balance-wear

# Strategy 4: Prioritize speed over pen changes
plotty plan-all --optimize-pens --strategy speed-first
```

### 8.5 Performance Tuning

**Device-specific optimization:**
```bash
# AxiDraw v3 optimization
plotty config device --model v3 --optimize-for v3

# Custom speed profiles
plotty add speed-profile \
  --name "precision" \
  --speed 15 \
  --acceleration 50 \
  --pen-up-delay 50

# Use custom speed profile
plotty plan job --speed-profile precision
```

**Paper-specific optimization:**
```bash
# Optimization for different paper types
plotty add paper-profile \
  --name "watercolor_paper" \
  --type "rough" \
  --pen-pressure "light" \
  --speed-reduction 20

plotty plan job --paper-profile watercolor_paper
```

**Environmental optimization:**
```bash
# Humidity-aware optimization
plotty plan job --humidity high --adjust-speed

# Temperature compensation
plotty plan job --temperature cold --compensate
```

### 8.6 Quality vs Speed Trade-offs

**Automated quality selection:**
```bash
# Let ploTTY choose optimal preset
plotty plan job --auto-preset --target-time 10m

# Quality-based selection
plotty plan job --quality-threshold 95 --auto-preset

# Speed-based selection
plotty plan job --speed-priority --max-time 5m
```

**Manual quality tuning:**
```bash
# Custom quality settings
plotty plan job \
  --line-merge-tolerance 0.05mm \
  --line-simplify-tolerance 0.02mm \
  --min-path-length 1mm

# Progressive refinement
plotty plan job --progressive-refinement --iterations 3
```

### 8.7 Optimization Profiling

**Profile optimization performance:**
```bash
# Profile optimization process
plotty profile job --show-steps --timing

# Compare optimization algorithms
plotty profile job --compare-algorithms fast,hq,custom

# Optimization bottleneck analysis
plotty profile job --find-bottlenecks
```

**Sample profiling output:**
```
🔍 Optimization Profile: detailed_art
=====================================
Step 1: File loading - 0.2s
Step 2: Path parsing - 0.8s
Step 3: Line merging - 2.1s (bottleneck)
Step 4: Line simplification - 1.5s
Step 5: Path sorting - 0.9s
Step 6: Relooping - 1.2s
Step 7: File writing - 0.3s

Total optimization time: 7.0s
Recommendation: Use larger merge tolerance for faster processing
```

### 8.8 Optimization Automation

**Smart optimization selection:**
```python
# auto_optimizer.py - Intelligent optimization selection
import subprocess
import json

def auto_optimize(job_name, target_time=None, quality_priority=False):
    """Automatically select best optimization based on job characteristics."""
    
    # Get job analysis
    result = subprocess.run([
        "uv", "run", "plotty", "info", "job", job_name, "--json"
    ], capture_output=True, text=True)
    
    job_data = json.loads(result.stdout)
    
    # Analyze job characteristics
    complexity = job_data.get('complexity_score', 0)
    path_length = job_data.get('total_path_length', 0)
    layer_count = job_data.get('layer_count', 1)
    
    # Select optimization strategy
    if quality_priority:
        preset = "hq"
    elif target_time:
        preset = select_preset_for_target_time(complexity, target_time)
    elif complexity > 1000:
        preset = "hq"
    elif complexity > 100:
        preset = "default"
    else:
        preset = "fast"
    
    # Apply optimization
    subprocess.run([
        "uv", "run", "plotty", "plan", job_name, "--preset", preset
    ])
    
    return preset

def select_preset_for_target_time(complexity, target_time_minutes):
    """Select preset to meet target time."""
    if target_time_minutes < 5:
        return "fast"
    elif target_time_minutes < 15:
        return "default"
    else:
        return "hq"

if __name__ == "__main__":
    preset = auto_optimize("my_job", target_time=10)
    print(f"Selected preset: {preset}")
```

> **🎯 Optimization Goal:** Find the perfect balance between processing time, plotting time, and output quality for your specific workflow.

## 9. Studio Management

Professional studio operations and resource management.

### 9.1 Device Management

**Device health monitoring:**
```bash
# Comprehensive device check
plotty check ready --detailed

# Test device movement patterns
plotty check device --test-move --pattern full-range

# Device calibration
plotty calibrate device --auto-calibrate

# Device performance test
plotty benchmark device --duration 5m
```

**Multi-device management:**
```bash
# List all connected devices
plotty list devices

# Switch between devices
plotty config device --active axidraw_v3_1

# Device-specific settings
plotty config device --name axidraw_v3_1 \
  --speed-profile precision \
  --pen-up-delay 60 \
  --pen-down-delay 40
```

**Device maintenance tracking:**
```bash
# Log maintenance
plotty maintenance log --type cleaning --device axidraw_v3_1

# Schedule maintenance reminders
plotty maintenance schedule --interval 100h --type cleaning

# View maintenance history
plotty maintenance history --device axidraw_v3_1 --last 90d
```

### 9.2 Pen and Paper Inventory

**Comprehensive pen management:**
```bash
# List all pens with detailed info
plotty list pens --detailed --show-usage

# Add new pen with full specifications
plotty add pen \
  --name "Ultra Fine Black" \
  --width 0.2 \
  --color "#000000" \
  --type "technical" \
  --brand "Sakura" \
  --model "Pigma Micron 003" \
  --speed-cap 40 \
  --pressure "light" \
  --cost 3.50

# Update pen usage tracking
plotty update pen 1 --log-usage --hours-used 2.5

# Pen inventory management
plotty inventory pens --check-stock --reorder-threshold 3
```

**Advanced paper management:**
```bash
# List paper with inventory tracking
plotty list paper --show-stock --show-cost

# Add custom paper with full details
plotty add paper \
  --name "Arches Watercolor" \
  --width 210 \
  --height 297 \
  --margin 15 \
  --type "watercolor" \
  --weight 300 \
  --texture "rough" \
  --cost-per-sheet 5.25 \
  --stock-count 25

# Paper usage tracking
plotty update paper "Arches Watercolor" --consume 1

# Cost analysis by paper type
plotty analyze paper --cost-per-job --last 30
```

**Resource optimization:**
```bash
# Optimize pen usage across jobs
plotty optimize pens --minimize-wear --balance-usage

# Suggest paper sizes for jobs
plotty suggest paper --job complex_art --optimize-waste

# Resource cost analysis
plotty analyze costs --by-project --include-materials
```

### 9.3 Performance Monitoring and Analytics

**Real-time performance monitoring:**
```bash
# Live performance dashboard
plotty monitor --live --refresh 5s

# Performance alerts setup
plotty alerts set --metric success-rate --threshold 95 --below

# Automated performance reports
plotty report performance --daily --email studio@example.com
```

**Comprehensive analytics:**
```bash
# Studio-wide statistics
plotty stats summary --last 30 --detailed

# Job performance analytics
plotty stats jobs --by-complexity --by-paper-type --by-pen

# Device performance tracking
plotty stats device --uptime --error-rate --maintenance-schedule

# Resource utilization analysis
plotty stats resources --pen-usage --paper-consumption --cost-analysis
```

**Sample comprehensive analytics output:**
```
📊 Studio Performance Dashboard (Last 30 Days)
=============================================
Overall Performance:
  - Jobs completed: 127 (98.4% success rate)
  - Total plotting time: 45h 23m
  - Average job time: 21.4 minutes
  - Device uptime: 99.2%

Resource Utilization:
  - Most used pen: Fine Black (42% of jobs)
  - Most popular paper: A4 (68% of jobs)
  - Material cost per job: $2.34
  - Pen change frequency: 1.8 per job

Quality Metrics:
  - Average optimization improvement: 28%
  - Customer satisfaction: 4.7/5.0
  - Replot rate: 1.6%
  - Error rate: 1.6%

Financial Summary:
  - Revenue: $3,847.50
  - Material costs: $297.18
  - Device depreciation: $156.00
  - Net profit: $3,394.32
```

### 9.4 Workflow Automation

**Automated studio workflows:**
```bash
# Morning startup routine
plotty workflow morning-startup \
  --device-check \
  --inventory-check \
  --queue-review \
  --schedule-optimization

# End-of-day shutdown
plotty workflow end-of-day \
  --backup-data \
  --generate-reports \
  --schedule-maintenance \
  --cleanup-temp

# Weekly maintenance
plotty workflow weekly-maintenance \
  --device-calibration \
  --inventory-audit \
  --performance-review \
  --backup-verification
```

**Intelligent automation:**
```python
# studio_automation.py - Smart studio management
import subprocess
import json
from datetime import datetime, timedelta

class StudioManager:
    def __init__(self):
        self.load_configuration()
    
    def morning_routine(self):
        """Automated morning startup sequence."""
        print("🌅 Starting morning studio routine...")
        
        # Check device health
        device_status = self.check_device_health()
        if not device_status['ready']:
            self.handle_device_issues(device_status)
        
        # Check inventory levels
        inventory_status = self.check_inventory()
        if inventory_status['needs_reorder']:
            self.generate_reorder_list(inventory_status)
        
        # Review and optimize today's queue
        self.optimize_todays_queue()
        
        # Generate morning report
        self.generate_morning_report()
    
    def check_device_health(self):
        """Comprehensive device health check."""
        result = subprocess.run([
            "uv", "run", "plotty", "check", "ready", "--json"
        ], capture_output=True, text=True)
        
        return json.loads(result.stdout)
    
    def optimize_todays_queue(self):
        """Optimize queue for today's production."""
        # Get today's jobs
        result = subprocess.run([
            "uv", "run", "plotty", "list", "queue", "--today", "--json"
        ], capture_output=True, text=True)
        
        jobs = json.loads(result.stdout)
        
        # Optimize for minimal pen changes and time
        subprocess.run([
            "uv", "run", "plotty", "optimize-pens", 
            "--global", "--strategy", "min-time"
        ])
        
        print(f"✅ Optimized {len(jobs)} jobs for today")
    
    def generate_morning_report(self):
        """Generate comprehensive morning report."""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'device_status': self.check_device_health(),
            'inventory_status': self.check_inventory(),
            'queue_status': self.get_queue_status(),
            'yesterday_performance': self.get_yesterday_stats()
        }
        
        # Save report
        filename = f"reports/morning_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📊 Morning report saved: {filename}")

if __name__ == "__main__":
    studio = StudioManager()
    studio.morning_routine()
```

### 9.5 Quality Assurance

**Automated quality checks:**
```bash
# Pre-plot quality validation
plotty validate job --check-paths --check-complexity --check-time

# Post-plot quality assessment
plotty assess job --compare-with-expected --quality-score

# Batch quality validation
plotty validate-all --strict-mode --fail-on-warnings
```

**Quality tracking:**
```bash
# Quality metrics over time
plotty quality trends --last 90 --by-complexity

# Quality by pen/paper combinations
plotty quality matrix --pens-vs-paper

# Customer quality feedback tracking
plotty quality feedback --by-client --by-project
```

> **🎯 Studio Management Goal:** Create a self-monitoring, self-optimizing studio that requires minimal manual intervention while maintaining maximum quality and efficiency.

### 6.2 Pen and Paper Inventory

```bash
# List all resources
plotty list pens
plotty list paper

# Add new paper size
plotty add paper \
  --name "Custom Large" \
  --width 300 \
  --height 200 \
  --margin 15

# Update pen information
plotty update pen 1 \
  --speed-cap 60 \
  --pressure "light"
```

### 6.3 Performance Monitoring

```bash
# Quick statistics overview
plotty stats summary

# Detailed job analytics
plotty stats jobs --last 30

# Performance metrics
plotty stats performance --pen-usage
```

**Statistics output:**
```
📊 Studio Statistics (Last 30 Days)
===================================
Jobs completed: 47
Total plotting time: 12h 34m
Average job time: 16 minutes
Most used pen: Fine Black (67%)
Success rate: 98%

🖊️ Pen Usage
=============
Fine Black: 31 jobs (66%)
Medium Black: 9 jobs (19%)
Fine Red: 4 jobs (9%)
Medium Blue: 3 jobs (6%)
```

---

## 10. Real-Time Monitoring

Monitor your ploTTY studio in real-time with WebSocket connections for live dashboards, alerts, and automation.

### 10.1 WebSocket Monitoring Basics

ploTTY includes a built-in WebSocket server that provides real-time updates about jobs, system status, and device activity.

**Start the monitoring daemon:**
```bash
# Start in background
plotty daemon --start

# Start with custom settings
plotty daemon --start --port 8765 --host 0.0.0.0

# Check daemon status
plotty daemon --status
```

**Basic monitoring with CLI:**
```bash
# Simple terminal monitoring
plotty monitor

# Monitor specific channels
plotty monitor --channels jobs,system

# Monitor with filtering
plotty monitor --filter "job.status:plotting"
```

### 10.2 Web Dashboard Setup

Create a real-time web dashboard for visual monitoring.

**HTML dashboard example:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>ploTTY Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { padding: 10px; margin: 5px 0; border-radius: 5px; }
        .plotting { background: #e3f2fd; }
        .completed { background: #e8f5e8; }
        .error { background: #ffebee; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
    </style>
</head>
<body>
    <h1>🖊️ ploTTY Studio Monitor</h1>
    <div id="status">Connecting...</div>
    <div id="jobs"></div>
    <div id="metrics" class="metrics"></div>

    <script>
        const ws = new WebSocket('ws://localhost:8765');
        
        ws.onopen = () => {
            document.getElementById('status').innerHTML = '🟢 Connected to ploTTY';
        };
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            updateDisplay(data);
        };
        
        function updateDisplay(data) {
            if (data.type === 'job_update') {
                updateJobDisplay(data.payload);
            } else if (data.type === 'system_status') {
                updateSystemDisplay(data.payload);
            }
        }
        
        function updateJobDisplay(job) {
            const jobsDiv = document.getElementById('jobs');
            const jobDiv = document.createElement('div');
            jobDiv.className = `status ${job.status}`;
            jobDiv.innerHTML = `
                <strong>${job.name}</strong> - ${job.status}
                <br>Progress: ${job.progress || 0}%
                ${job.estimated_time_remaining ? `<br>ETA: ${job.estimated_time_remaining}` : ''}
            `;
            jobsDiv.appendChild(jobDiv);
        }
    </script>
</body>
</html>
```

### 10.3 Python Monitoring Client

Create custom Python monitoring scripts for automation and alerts.

**Basic Python client:**
```python
# monitor.py - Python WebSocket client
import asyncio
import websockets
import json
from datetime import datetime

class PlottyMonitor:
    def __init__(self, uri="ws://localhost:8765"):
        self.uri = uri
        self.callbacks = {
            'job_update': self.on_job_update,
            'system_status': self.on_system_status,
            'device_status': self.on_device_status
        }
    
    async def connect(self):
        """Connect to ploTTY WebSocket server."""
        self.websocket = await websockets.connect(self.uri)
        print(f"🔗 Connected to ploTTY at {self.uri}")
        
        # Start listening
        await self.listen()
    
    async def listen(self):
        """Listen for WebSocket messages."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("❌ Connection to ploTTY lost")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def handle_message(self, data):
        """Handle incoming WebSocket messages."""
        message_type = data.get('type')
        payload = data.get('payload')
        timestamp = data.get('timestamp')
        
        if message_type in self.callbacks:
            await self.callbacks[message_type](payload, timestamp)
        else:
            print(f"📨 Unknown message type: {message_type}")
    
    async def on_job_update(self, job, timestamp):
        """Handle job status updates."""
        status_emoji = {
            'pending': '⏳',
            'planning': '📋',
            'planned': '✅',
            'plotting': '🖊️',
            'completed': '🎉',
            'failed': '❌'
        }
        
        emoji = status_emoji.get(job.get('status'), '❓')
        print(f"{emoji} Job {job.get('name')}: {job.get('status')}")
        
        if job.get('status') == 'plotting':
            progress = job.get('progress', 0)
            eta = job.get('estimated_time_remaining', 'Unknown')
            print(f"   Progress: {progress}% | ETA: {eta}")
        
        # Custom alerts
        if job.get('status') == 'failed':
            await self.send_alert(f"Job {job.get('name')} failed!")
        elif job.get('status') == 'completed':
            await self.send_alert(f"Job {job.get('name')} completed successfully!")
    
    async def on_system_status(self, status, timestamp):
        """Handle system status updates."""
        print(f"🖥️ System: Device {status.get('device_status')}, Queue: {status.get('queue_size')} jobs")
    
    async def on_device_status(self, device, timestamp):
        """Handle device status updates."""
        print(f"🔌 Device: {device.get('name')} - {device.get('status')}")
    
    async def send_alert(self, message):
        """Send alert (customize for your needs)."""
        print(f"🚨 ALERT: {message}")
        # Add email, Slack, or other notification methods here

async def main():
    monitor = PlottyMonitor()
    await monitor.connect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 10.4 Alert System Integration

Set up automated alerts for important events.

**Email alerts example:**
```python
# alerts.py - Alert system integration
import smtplib
import asyncio
from email.mime.text import MIMEText
from monitor import PlottyMonitor

class AlertSystem(PlottyMonitor):
    def __init__(self, email_config=None):
        super().__init__()
        self.email_config = email_config or {}
        self.alert_rules = {
            'job_failed': self.alert_job_failed,
            'job_completed': self.alert_job_completed,
            'device_disconnected': self.alert_device_disconnected,
            'queue_full': self.alert_queue_full
        }
    
    async def alert_job_failed(self, job, timestamp):
        """Send alert when job fails."""
        message = f"""
        ploTTY Job Failed Alert
        
        Job: {job.get('name')}
        Status: {job.get('status')}
        Error: {job.get('error_message', 'Unknown error')}
        Time: {timestamp}
        
        Check ploTTY for details.
        """
        await self.send_email("ploTTY Job Failed", message)
    
    async def alert_job_completed(self, job, timestamp):
        """Send notification when job completes."""
        if job.get('estimated_time') and job.get('actual_time'):
            time_diff = job['actual_time'] - job['estimated_time']
            if abs(time_diff) > 300:  # 5 minute difference
                message = f"""
                ploTTY Job Time Anomaly
                
                Job: {job.get('name')}
                Estimated: {job.get('estimated_time')}s
                Actual: {job.get('actual_time')}s
                Difference: {time_diff}s
                
                Review optimization settings.
                """
                await self.send_email("ploTTY Time Anomaly", message)
    
    async def send_email(self, subject, message):
        """Send email alert."""
        if not self.email_config:
            print(f"📧 Email alert: {subject}")
            return
        
        try:
            msg = MIMEText(message)
            msg['Subject'] = f"[ploTTY] {subject}"
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)
            
            print(f"📧 Email sent: {subject}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

# Usage example
async def main():
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your-email@gmail.com',
        'password': 'your-app-password',
        'from': 'your-email@gmail.com',
        'to': 'alerts@your-studio.com'
    }
    
    alert_system = AlertSystem(email_config)
    await alert_system.connect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 10.5 Production Monitoring Patterns

Professional monitoring setups for studio environments.

**Multi-client monitoring:**
```python
# production_monitor.py - Production monitoring setup
import asyncio
import json
import logging
from datetime import datetime, timedelta
from monitor import PlottyMonitor

class ProductionMonitor(PlottyMonitor):
    def __init__(self):
        super().__init__()
        self.metrics = {
            'jobs_completed': 0,
            'jobs_failed': 0,
            'total_plotting_time': 0,
            'shift_start': datetime.now()
        }
        self.performance_log = []
    
    async def on_job_update(self, job, timestamp):
        """Track job performance metrics."""
        await super().on_job_update(job, timestamp)
        
        if job.get('status') == 'completed':
            self.metrics['jobs_completed'] += 1
            if job.get('actual_time'):
                self.metrics['total_plotting_time'] += job['actual_time']
            
            # Log performance data
            self.performance_log.append({
                'job_name': job.get('name'),
                'completion_time': timestamp,
                'actual_time': job.get('actual_time'),
                'estimated_time': job.get('estimated_time'),
                'accuracy': job.get('actual_time') / job.get('estimated_time') if job.get('estimated_time') else None
            })
            
            # Check for performance issues
            await self.check_performance_issues(job)
        
        elif job.get('status') == 'failed':
            self.metrics['jobs_failed'] += 1
            await self.log_failure(job)
    
    async def check_performance_issues(self, job):
        """Check for performance anomalies."""
        if not job.get('estimated_time') or not job.get('actual_time'):
            return
        
        accuracy = job['actual_time'] / job['estimated_time']
        
        # Job took significantly longer than estimated
        if accuracy > 1.5:  # 50% longer than estimated
            await self.send_alert(f"Job {job.get('name')} took {accuracy:.1f}x longer than estimated")
        
        # Job was much faster than estimated (might indicate quality issues)
        elif accuracy < 0.5:  # 50% faster than estimated
            await self.send_alert(f"Job {job.get('name')} was unusually fast - check quality")
    
    async def generate_shift_report(self):
        """Generate end-of-shift performance report."""
        shift_duration = datetime.now() - self.metrics['shift_start']
        avg_job_time = self.metrics['total_plotting_time'] / max(self.metrics['jobs_completed'], 1)
        
        report = f"""
        ploTTY Shift Report
        ===================
        Shift Duration: {shift_duration}
        Jobs Completed: {self.metrics['jobs_completed']}
        Jobs Failed: {self.metrics['jobs_failed']}
        Success Rate: {self.metrics['jobs_completed'] / (self.metrics['jobs_completed'] + self.metrics['jobs_failed']) * 100:.1f}%
        Average Job Time: {avg_job_time:.1f}s
        Total Plotting Time: {self.metrics['total_plotting_time']}s
        
        Performance Summary:
        """
        
        # Add performance analysis
        if self.performance_log:
            accuracies = [p['accuracy'] for p in self.performance_log if p['accuracy']]
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                report += f"\nAverage Estimation Accuracy: {avg_accuracy:.2f}"
        
        print(report)
        await self.send_email("ploTTY Shift Report", report)

# Schedule monitoring
async def run_production_monitoring():
    """Run production monitoring with scheduled reports."""
    monitor = ProductionMonitor()
    
    # Start monitoring in background
    monitoring_task = asyncio.create_task(monitor.connect())
    
    # Schedule shift reports (every 8 hours)
    while True:
        await asyncio.sleep(8 * 3600)  # 8 hours
        await monitor.generate_shift_report()

if __name__ == "__main__":
    asyncio.run(run_production_monitoring())
```

### 10.6 Integration with External Systems

Connect ploTTY monitoring to your existing infrastructure.

**Slack integration:**
```python
# slack_monitor.py - Slack integration
import asyncio
import json
import requests
from monitor import PlottyMonitor

class SlackMonitor(PlottyMonitor):
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url
    
    async def send_slack_message(self, message, color="good"):
        """Send message to Slack channel."""
        payload = {
            "attachments": [{
                "color": color,
                "text": message,
                "ts": datetime.now().timestamp()
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to send Slack message: {e}")
    
    async def on_job_update(self, job, timestamp):
        """Send job updates to Slack."""
        await super().on_job_update(job, timestamp)
        
        status_colors = {
            'completed': 'good',
            'failed': 'danger',
            'plotting': 'warning'
        }
        
        if job.get('status') in status_colors:
            emoji = {"completed": "✅", "failed": "❌", "plotting": "🖊️"}.get(job.get('status'), "📋")
            message = f"{emoji} ploTTY Job `{job.get('name')}`: {job.get('status')}"
            
            if job.get('status') == 'plotting' and job.get('progress'):
                message += f" ({job.get('progress')}% complete)"
            
            await self.send_slack_message(message, status_colors[job.get('status')])

# Usage
async def main():
    webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    monitor = SlackMonitor(webhook_url)
    await monitor.connect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 10.7 Monitoring Best Practices

**Production monitoring guidelines:**

1. **Reliable Connections**
   ```python
   # Implement reconnection logic
   async def connect_with_retry(self, max_retries=5):
       for attempt in range(max_retries):
           try:
               await self.connect()
               break
           except Exception as e:
               if attempt == max_retries - 1:
                   raise
               await asyncio.sleep(2 ** attempt)  # Exponential backoff
   ```

2. **Message Filtering**
   ```python
   # Filter messages to reduce noise
   def should_process_message(self, data):
       # Only process job updates for specific jobs
       if data.get('type') == 'job_update':
           job_name = data.get('payload', {}).get('name', '')
           return job_name.startswith('production_')
       return True
   ```

3. **Rate Limiting**
   ```python
   # Prevent alert fatigue
   class RateLimiter:
       def __init__(self, max_alerts_per_hour=10):
           self.max_alerts = max_alerts_per_hour
           self.alerts_sent = []
       
       async def can_send_alert(self):
           now = datetime.now()
           hour_ago = now - timedelta(hours=1)
           recent_alerts = [a for a in self.alerts_sent if a > hour_ago]
           return len(recent_alerts) < self.max_alerts
   ```

4. **Data Persistence**
   ```python
   # Save monitoring data for analysis
   async def save_metrics(self, data):
       filename = f"metrics/metrics_{datetime.now().strftime('%Y%m%d')}.json"
       with open(filename, 'a') as f:
           json.dump(data, f)
           f.write('\n')
   ```

> **🎯 Monitoring Goal:** Create a comprehensive monitoring system that keeps you informed without overwhelming you with alerts. Focus on actionable insights and proactive problem detection.

---

# 📚 Reference

## 11. Real-World Examples

Learn from professionals using ploTTY in production environments.

### 10.1 Graphic Design Studio Workflow

**Scenario:** Commercial studio handling client logos and business cards

```bash
#!/bin/bash
# studio_workflow.sh - Daily studio routine

# Morning setup
echo "🌅 Morning studio setup..."
plotty check ready --detailed
plotty status
plotty inventory check --alert-low

# Process today's client batch
echo "📋 Processing client designs..."
for file in client_*.svg; do
    client_name=$(basename "$file" .svg | sed 's/client_//')
    plotty add "$file" \
        --name "Client: $client_name" \
        --paper a4 \
        --priority normal
done

# Optimize for production efficiency
echo "⚡ Optimizing production queue..."
plotty plan-all --preset hq --optimize-pens --global-pen-order

# Production run with quality monitoring
echo "🖊️ Starting production run..."
plotty plot-all --preset safe --record-all --monitor

# End of day reporting
echo "📊 Generating daily report..."
plotty stats summary --today --export > "reports/daily_$(date +%Y%m%d).json"
plotty inventory usage --log-consumption

echo "✅ Studio workflow complete!"
```

**Client delivery automation:**
```bash
# Prepare client delivery package
plotty package client_acme \
  --include-reports \
  --include-photos \
  --generate-invoice \
  --email-client
```

### 10.2 Artist Studio Workflow

**Scenario:** Professional artist creating limited edition prints

```bash
#!/bin/bash
# artist_workflow.sh - Art production workflow

artwork_name="Geometric Harmony v3"
edition_size=10

echo "🎨 Creating limited edition: $artwork_name"

# Step 1: Generate master design
echo "✏️ Generating master design..."
vsk run "$artwork_name.py" --set edition=master --save-only

# Step 2: Create test print
echo "🖨️ Creating test print..."
plotty add "${artwork_name}_master.svg" \
    --name "Test: $artwork_name" \
    --paper a4 --preset fast

plotty plot "Test:*" --preview --record

# Step 3: Review and approve test
echo "📋 Review test print before continuing..."
read -p "Press Enter to continue with full edition, Ctrl+C to cancel..."

# Step 4: Generate edition series
echo "📚 Generating edition series ($edition_size prints)..."
for edition in $(seq 1 $edition_size); do
    # Generate unique variant
    vsk run "$artwork_name.py" \
        --set edition=$edition \
        --set seed=$((edition * 42)) \
        --save-only
    
    # Queue with edition naming
    job_name="${artwork_name} - Edition ${edition}/${edition_size}"
    plotty add "${artwork_name}_edition${edition}.svg" \
        --name "$job_name" \
        --paper a3 --preset hq \
        --priority high
done

# Step 5: Plot edition with documentation
echo "🖊️ Plotting limited edition..."
plotty plot-all --record-all --document-each --numbered

# Step 6: Generate certificate of authenticity
echo "📜 Generating certificates..."
plotty generate certificates \
  --artwork "$artwork_name" \
  --edition-size $edition_size \
  --artist "Your Name" \
  --date "$(date +%Y-%m-%d)"

echo "✅ Limited edition complete!"
```

### 10.3 Educational Workshop Workflow

**Scenario:** University workshop with 20 participants

```bash
#!/bin/bash
# workshop_workflow.sh - Educational workshop management

workshop_name="Generative Art 101"
participants=("alice" "bob" "charlie" "diana" "eve")

echo "🎓 Setting up $workshop_name workshop..."

# Step 1: Setup demo files
echo "📋 Preparing demo files..."
plotty add demo_pattern.svg --name "Demo: Basic Pattern" --paper a4
plotty add demo_complex.svg --name "Demo: Advanced Technique" --paper a4

# Step 2: Add participant designs
echo "👥 Adding participant designs..."
for participant in "${participants[@]}"; do
    if [[ -f "${participant}_design.svg" ]]; then
        plotty add "${participant}_design.svg" \
            --name "Workshop: $participant" \
            --paper a4 --priority normal
    fi
done

# Step 3: Quick batch planning for demo
echo "⚡ Planning demo files..."
plotty plan "Demo:*" --preset fast

# Step 4: Demonstrate plotting
echo "🖊️ Live demonstration..."
echo "Plotting basic pattern..."
plotty plot "Demo: Basic Pattern" --preview --explain-steps

echo "Plotting advanced technique..."
plotty plot "Demo: Advanced Technique" --preview --explain-steps

# Step 5: Participant plotting session
echo "👥 Participant plotting session..."
for participant in "${participants[@]}"; do
    echo "Plotting $participant's design..."
    plotty plot "Workshop: $participant" --record
done

# Step 6: Generate workshop report
echo "📊 Generating workshop report..."
plotty report workshop \
  --name "$workshop_name" \
  --participants "${#participants[@]}" \
  --include-photos \
  --include-statistics \
  --export "workshop_report_$(date +%Y%m%d).pdf"

echo "✅ Workshop complete!"
```

### 10.4 Production Facility Workflow

**Scenario:** High-volume production facility with multiple devices

```python
# production_facility.py - Industrial-scale production
import subprocess
import json
import time
from datetime import datetime

class ProductionFacility:
    def __init__(self):
        self.devices = self.load_devices()
        self.queue = self.load_queue()
    
    def shift_start(self):
        """Automated shift start routine."""
        print("🏭 Starting production shift...")
        
        # Check all devices
        for device in self.devices:
            status = self.check_device(device['id'])
            if not status['ready']:
                self.handle_device_issue(device, status)
        
        # Load today's production schedule
        self.load_production_schedule()
        
        # Optimize across all devices
        self.optimize_global_queue()
        
        # Start production on all devices
        self.start_parallel_production()
    
    def optimize_global_queue(self):
        """Optimize queue across multiple devices."""
        print("⚡ Optimizing global production queue...")
        
        # Get all pending jobs
        jobs = self.get_all_pending_jobs()
        
        # Sort by priority and device compatibility
        optimized_jobs = self.sort_jobs_by_efficiency(jobs)
        
        # Distribute across devices
        for i, job in enumerate(optimized_jobs):
            device = self.devices[i % len(self.devices)]
            self.assign_job_to_device(job, device)
    
    def monitor_production(self):
        """Real-time production monitoring."""
        while True:
            # Check all devices
            for device in self.devices:
                status = self.get_device_status(device['id'])
                
                if status['idle'] and self.has_pending_jobs():
                    self.assign_next_job(device)
                
                if status['error']:
                    self.handle_production_error(device, status)
            
            # Generate status report every 10 minutes
            if time.time() % 600 < 60:
                self.generate_status_report()
            
            time.sleep(30)  # Check every 30 seconds
    
    def generate_status_report(self):
        """Generate comprehensive production report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'devices': [self.get_device_status(d['id']) for d in self.devices],
            'queue': self.get_queue_status(),
            'production_today': self.get_today_production_stats(),
            'efficiency_metrics': self.calculate_efficiency_metrics()
        }
        
        # Save and optionally send report
        filename = f"production_status_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

if __name__ == "__main__":
    facility = ProductionFacility()
    facility.shift_start()
    facility.monitor_production()
```

## 12. Troubleshooting

### 12.1 Device Issues
### 12.2 Quality Issues
### 12.3 Performance Issues
### 12.4 Software Issues

## 13. Best Practices

### 13.1 File Organization
### 13.2 Naming Conventions
### 13.3 Quality Assurance
### 13.4 Maintenance Schedule
### 13.5 Professional Workflow Tips

**Efficiency tips:**
- 🎯 **Batch similar jobs** - Group by paper size, pen requirements, or complexity
- ⚡ **Use presets consistently** - Develop standard presets for different job types
- 📊 **Monitor performance metrics** - Track trends to optimize over time
- 🔄 **Automate repetitive tasks** - Create scripts for common workflows

**Quality tips:**
- ✅ **Always test new designs** - Use small test plots before full production
- 📏 **Calibrate regularly** - Keep devices in optimal condition
- 🖊️ **Track pen performance** - Replace pens before quality degrades
- 📹 **Document important jobs** - Use camera recording for client work

**Business tips:**
- 💰 **Track material costs** - Use ploTTY's cost tracking features
- ⏱️ **Monitor time efficiency** - Use stats to improve pricing estimates
- 📋 **Maintain client records** - Use consistent naming and documentation
- 📊 **Generate regular reports** - Use analytics for business insights

---

## Getting Help

**Quick help:**
- **Command help**: `plotty --help` or `plotty <command> --help`
- **System info**: `plotty info system` (include with bug reports)
- **Version check**: `plotty --version`

**Documentation:**
- **API documentation**: `docs/api/` directory
- **Installation guide**: `docs/installation.md`
- **Troubleshooting**: `docs/troubleshooting/`

**Community:**
- **GitHub Discussions**: Community questions and discussions
- **GitHub Issues**: Bug reports and feature requests
- **Discord/Slack**: Real-time community chat (if available)

**Professional support:**
- **Enterprise support**: Contact for studio licensing and support
- **Consulting**: Custom workflow optimization and training
- **Development**: Custom feature development and integration

---

**🎯 Your ploTTY Journey:** Start with the [Beginner Path](#-beginner-path) to master the basics, progress through the [Creative Path](#-creative-path) to develop your artistic style, and advance to the [Power User Path](#-power-user-path) for professional studio management. Each path builds on the previous one, creating a complete mastery of pen plotting productivity.