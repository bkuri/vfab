# ploTTY User Guide

**Purpose:** Comprehensive guide for users wanting to master ploTTY for pen plotting productivity.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Your First Plot](#2-your-first-plot)
3. [Working with Multi-Pen Designs](#3-working-with-multi-pen-designs)
4. [Creative Tool Integration](#4-creative-tool-integration)
5. [Batch Production Workflow](#5-batch-production-workflow)
6. [Advanced Optimization](#6-advanced-optimization)
7. [Studio Management](#7-studio-management)
8. [Real-World Examples](#8-real-world-examples)
9. [Tips and Best Practices](#9-tips-and-best-practices)

---

## 1. Getting Started

### 1.1 What is ploTTY?

ploTTY is a headless-first pen plotter manager that helps you:
- **Queue and optimize** SVG files for plotting
- **Manage multiple pens** automatically
- **Track plotting time** accurately
- **Record sessions** for documentation
- **Recover from crashes** gracefully

### 1.2 System Requirements

**Minimum:**
- Python 3.11+
- 2GB RAM
- 100MB disk space
- USB port (for AxiDraw)

**Recommended:**
- 4GB RAM
- 1GB disk space
- IP camera for recording
- Multiple pens for complex designs

### 1.3 Installation

```bash
# Install uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone ploTTY
git clone https://github.com/your-org/plotty.git
cd plotty

# Install (without hardware support)
uv pip install -e ".[dev,vpype]"

# Install with AxiDraw support
uv pip install -e ".[dev,vpype,axidraw]"

# Initialize database
uv run alembic upgrade head
```

### 1.4 First-Time Setup

```bash
# Run interactive setup wizard
uv run plotty setup
```

**Setup prompts:**
```
🔧 ploTTY Setup Wizard
======================

Device Configuration:
  AxiDraw port [/dev/ttyUSB0]: 
  Device model [1]: 
  Pen up position [60]: 
  Pen down position [40]: 

Paper Settings:
  Default paper size [A4]: 
  Default margin [10mm]: 
  Default orientation [portrait]: 

Camera Setup (optional):
  Camera URL [http://localhost:8881/stream.mjpeg]: 
  Enable recording [y]: 

✅ Configuration saved to config/config.yaml
```

---

## 2. Your First Plot

### 2.1 Preparing Your Design

**SVG Requirements:**
- Vector paths only (no bitmaps)
- Reasonable complexity (<10,000 points)
- Layers named meaningfully (optional)

**Example SVG structure:**
```xml
<svg>
  <!-- Single layer design -->
  <path d="M10,10 L100,100" stroke="black" stroke-width="0.5"/>
  
  <!-- Multi-layer design -->
  <g inkscape:label="outline">
    <path d="M10,10 L100,100" stroke="black" stroke-width="0.5"/>
  </g>
  <g inkscape:label="fill">
    <path d="M20,20 L90,90" stroke="red" stroke-width="0.3"/>
  </g>
</svg>
```

### 2.2 Adding Your First Job

```bash
# Add a simple design
uv run plotty add my_first_drawing.svg --paper a4

# Add with custom name
uv run plotty add complex_art.svg --name "Client Logo" --paper a3
```

**Output:**
```
✅ Added job: my_first_drawing
📊 Analysis results:
  - Dimensions: 150mm × 100mm
  - Points: 1,247
  - Estimated time: 8 minutes
  - Layers detected: 1
```

### 2.3 Planning the Job

```bash
# Interactive planning (recommended for first time)
uv run plotty plan my_first_drawing --interactive

# Quick planning with defaults
uv run plotty plan my_first_drawing
```

**Interactive planning shows:**
```
🎨 Layer Analysis
==================
Detected 1 layer:
  🔵 Layer 1: "default" (1,247 points) - BLACK

📝 Optimization Options
========================
1. Fast (default) - Quick optimization
2. High Quality - Better path optimization
3. Custom - Enter your vpype pipeline

Choose optimization [1]: 1

⏱️ Time Estimation
==================
Pre-optimization: 8.2 minutes
Post-optimization: 6.1 minutes (25% faster)

✅ Job planned successfully
```

### 2.4 Plotting

```bash
# Start plotting
uv run plotty plot my_first_drawing
```

**Real-time progress:**
```
🖊️ Plotting: my_first_drawing
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

### 2.5 Viewing Results

```bash
# Job information
uv run plotty info job my_first_drawing

# View generated report
# Open: workspace/jobs/my_first_drawing/report.html
```

---

## 3. Working with Multi-Pen Designs

### 3.1 Understanding Multi-Pen Detection

ploTTY automatically detects multi-pen requirements from:
- **SVG layers** (Inkscape, Illustrator)
- **AxiDraw layer control syntax** (`%layer_name` comments)

**Example multi-layer SVG:**
```xml
<svg>
  <g inkscape:label="outline">
    <path d="..." stroke="black" stroke-width="0.5"/>
  </g>
  <g inkscape:label="shading">
    <path d="..." stroke="gray" stroke-width="0.3"/>
  </g>
  <g inkscape:label="highlights">
    <path d="..." stroke="white" stroke-width="0.2"/>
  </g>
</svg>
```

### 3.2 Setting Up Multiple Pens

```bash
# View current pens
uv run plotty list pens

# Add pens interactively
uv run plotty setup pen

# Add specific pen
uv run plotty add pen \
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
uv run plotty add colorful_design.svg --paper a4

# Plan with interactive pen mapping
uv run plotty plan colorful_design --interactive
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
uv run plotty plot colorful_design
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

---

## 4. Creative Tool Integration

### 4.1 vsketch Integration with vpype-plotty

**Installation:**
```bash
# Install vpype-plotty for vsketch integration
pipx inject vsketch vpype-plotty
```

**Basic vsketch workflow:**
```python
import vsketch

class MyDesign(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")
        
        # Your creative code here
        for i in range(10):
            vsk.circle(i * 2, i * 2, radius=1)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        # Standard optimization
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Add to ploTTY queue
        vsk.vpype("plotty-add --name my_design --preset hq --queue")

if __name__ == "__main__":
    MyDesign().display()
```

**Advanced vsketch integration:**
```python
class AdvancedDesign(vsketch.SketchClass):
    # Interactive parameters
    complexity = vsketch.Param(50)
    density = vsketch.Param(10)
    
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4")
        vsk.scale("cm")
        
        for i in range(self.complexity):
            with vsk.pushMatrix():
                vsk.rotate(i * 0.1)
                vsk.translate(
                    vsk.randomGaussian() * self.density * 0.1,
                    vsk.randomGaussian() * self.density * 0.1
                )
                vsk.circle(0, 0, radius=0.5)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Dynamic job naming based on parameters
        job_name = f"design_c{self.complexity}_d{self.density}"
        vsk.vpype(f"plotty-add --name '{job_name}' --preset hq --queue")
```

### 4.2 Direct vpype Integration

**For non-vsketch workflows:**
```bash
# Add existing SVG to ploTTY
vpype read design.svg plotty-add --name existing_art --preset fast

# Create generative art and queue
vpype rand --seed 123 plotty-add --name random_art --paper A3 --queue

# Batch processing
for seed in {1..10}; do
    vpype rand --seed $seed plotty-add --name "batch_$seed" --queue
done
```

### 4.3 Multi-Pen Design Integration

**vsketch multi-pen example:**
```python
class MultiPenArt(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4")
        vsk.scale("cm")
        
        # Layer 1: Black outlines
        vsk.stroke(1)
        vsk.penWidth("0.3mm", 1)
        for i in range(5):
            vsk.rect(i * 3, i * 2, 2, 2)
        
        # Layer 2: Red details
        vsk.stroke(2)
        vsk.penWidth("0.2mm", 2)
        for i in range(5):
            vsk.circle(i * 3 + 1, i * 2 + 1, radius=0.5)
        
        # Layer 3: Blue accents
        vsk.stroke(3)
        vsk.penWidth("0.5mm", 3)
        for i in range(5):
            vsk.line(i * 3, i * 2, i * 3 + 2, i * 2 + 2)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")
        vsk.vpype("plotty-add --name multipen_art --preset hq --queue")
```

### 4.4 Batch Processing with vpype-plotty

**Generate multiple variants:**
```python
# batch_generator.py
import subprocess
import json

def generate_batch(base_name, seed_range):
    """Generate multiple designs and queue them."""
    job_ids = []
    
    for seed in seed_range:
        print(f"Generating design with seed {seed}...")
        
        # Generate using vsketch
        cmd = [
            "vsk", "run", "generative_design.py",
            "--set", f"seed={seed}",
            "--save-only"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Queue with ploTTY
            job_name = f"{base_name}_seed_{seed}"
            cmd = [
                "vpype", "read", f"output/{base_name}_{seed}.svg",
                "plotty-add", "--name", job_name, "--preset", "fast", "--queue"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                job_id = result.stdout.strip()
                job_ids.append(job_id)
                print(f"✅ Queued job {job_id}")
    
    # Save job list
    with open(f"{base_name}_jobs.json", "w") as f:
        json.dump(job_ids, f, indent=2)
    
    return job_ids

# Usage
jobs = generate_batch("experiment", range(1, 21))
print(f"Generated {len(jobs)} jobs")
```

### 4.5 Integration with Other Creative Tools

**Inkscape workflow:**
```bash
# Design in Inkscape, export to SVG
inkscape --export-type=svg design.svg

# Add to ploTTY queue
vpype read design.svg plotty-add --name inkscape_art --preset hq
```

**Illustrator workflow:**
```bash
# Export from Illustrator as SVG
# File > Export > Export As... > SVG

# Process with vpype and queue
vpype read illustrator_art.svg plotty-add --name vector_design --queue
```

**Processing/p5.js workflow:**
```javascript
// Processing sketch that exports SVG
void setup() {
  size(400, 400);
}

void draw() {
  background(255);
  // Your creative code
  circle(mouseX, mouseY, 50);
  
  // Export SVG on keypress
  if (keyPressed) {
    save("processing_art.svg");
  }
}
```

```bash
# Convert and queue
vpype read processing_art.svg plotty-add --name processing_sketch --preset default
```

### 4.6 Best Practices for Creative Integration

**File Organization:**
```bash
# Recommended project structure
my_project/
├── sketches/           # vsketch .py files
├── output/            # Generated SVGs
├── ploppy_jobs/       # ploTTY workspace
└── batch_scripts/      # Automation scripts
```

**Parameter Management:**
```python
# Use meaningful parameter names
class ProfessionalDesign(vsketch.SketchClass):
    client_name = vsketch.Param("Acme Corp")
    project_type = vsketch.Param("logo")
    quality_level = vsketch.Param("hq")
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Professional job naming
        job_name = f"{self.client_name}_{self.project_type}_{self.quality_level}"
        vsk.vpype(f"plotty-add --name '{job_name}' --preset {self.quality_level} --queue")
```

**Quality Control:**
```python
# Add quality checks before queuing
def finalize(self, vsk: vsketch.Vsketch) -> None:
    vsk.vpype("linemerge linesimplify reloop linesort")
    
    # Check complexity before queuing
    if vsk.document.get_total_length() > 50000:  # mm
        print("⚠️  Warning: Very long plot time expected")
        print("Consider reducing complexity or using hq preset")
    
    # Queue with appropriate preset based on complexity
    if vsk.document.get_total_length() > 20000:
        preset = "hq"
    elif vsk.document.get_total_length() > 10000:
        preset = "default"
    else:
        preset = "fast"
    
    vsk.vpype(f"plotty-add --name complex_design --preset {preset} --queue")
```

### 4.7 ⚠️ Optimization Control

**Critical**: Understanding optimization handling prevents double-processing and ensures optimal performance.

#### **Optimization Workflow**

**vsketch → vpype-plotty → ploTTY (Recommended):**
```python
def finalize(self, vsk: vsketch.Vsketch) -> None:
    # Step 1: vsketch optimizes
    vsk.vpype("linemerge linesimplify reloop linesort")
    
    # Step 2: Skip ploTTY optimization (already done)
    vsk.vpype("plotty-add --name my_design --preset none --queue")
```

**Raw SVG → vpype → ploTTY:**
```bash
# Option 1: vpype optimizes, ploTTY skips
vpype read design.svg linemerge linesimplify \
    plotty-add --name optimized --preset none

# Option 2: ploTTY optimizes
vpype read design.svg plotty-add --name raw --preset hq
```

#### **Optimization Control Matrix**

| Source | vpype Command | ploTTY Preset | Result |
|---------|---------------|----------------|---------|
| vsketch optimized | `--preset none` | Skip | No double optimization |
| Raw SVG | vpype optimizes | `--preset none` | Single optimization |
| Raw SVG | none | `--preset hq/fast/default` | ploTTY optimization |
| Pre-optimized SVG | none | `--preset none` | No optimization |

#### **Best Practice Guidelines**

**1. Use `--preset none` when:**
- vsketch already optimized the design
- vpype already processed the file
- File is pre-optimized by other tools

**2. Use ploTTY presets when:**
- Working with raw SVG files
- Want consistent production quality
- Prefer ploTTY's optimization pipeline

**3. Match optimization levels:**
```python
# Consistent optimization across tools
def get_optimization_level(complexity):
    if complexity > 20000:  # mm of lines
        return "hq"
    elif complexity > 10000:
        return "default"
    else:
        return "fast"

# Use same logic in both vsketch and vpype workflows
```

---

## 5. Batch Production Workflow

### 4.1 Organizing Batch Jobs

```bash
# Create project directory
mkdir client_project
cd client_project

# Add all designs
uv run plotty add logo.svg --paper a4
uv run plotty add business_card.svg --paper a4
uv run plotty add letterhead.svg --paper a4
```

### 4.2 Batch Planning

```bash
# Plan all jobs with fast optimization
uv run plotty plan-all --preset fast

# Plan with pen optimization
uv run plotty plan-all --optimize-pens

# Plan specific jobs
uv run plotty plan logo business_card --preset hq
```

### 4.3 Batch Plotting

```bash
# Plot all planned jobs
uv run plotty plot-all

# Plot with safety preset (slower but more reliable)
uv run plotty plot-all --preset safe

# Monitor progress
uv run plotty list queue --watch
```

### 4.4 Queue Management

```bash
# View current queue
uv run plotty list queue

# Remove completed jobs
uv run plotty queue cleanup --state completed

# Remove old jobs (older than 7 days)
uv run plotty queue cleanup --older-than 7d

# Export queue status
uv run plotty list queue --json > queue_status.json
```

---

## 5. Advanced Optimization

### 5.1 Understanding vpype Presets

ploTTY includes optimization presets:

```yaml
# Fast preset (default)
fast: "read {src} pagesize {pagesize} crop 0 0 {width_mm}mm {height_mm}mm linemerge linesort write {dst}"

# High quality preset  
hq: "read {src} pagesize {pagesize} crop 0 0 {width_mm}mm {height_mm}mm linemerge linesort linesimplify write {dst}"
```

### 5.2 Custom Optimization

```bash
# Use custom vpype pipeline
uv run plotty plan job --custom "read {src} linemerge linesort write {dst}"

# Compare presets
uv run plotty plan job --preset fast --dry-run
uv run plotty plan job --preset hq --dry-run
```

### 5.3 Time Estimation

```bash
# Detailed time breakdown
uv run plotty estimate job --detailed

# Compare pre/post optimization
uv run plotty estimate job --stage pre
uv run plotty estimate job --stage post
```

**Estimation output:**
```
⏱️ Time Estimation: job
=======================
Pre-optimization:
  - Drawing time: 8.2 minutes
  - Pen changes: 0
  - Total: 8.2 minutes

Post-optimization:
  - Drawing time: 6.1 minutes  
  - Pen changes: 0
  - Total: 6.1 minutes

Improvement: 25% faster (2.1 minutes saved)
```

---

## 6. Studio Management

### 6.1 Device Management

```bash
# Check device status
uv run plotty check ready

# Test device movement
uv run plotty check device --test-move

# Update device configuration
uv run plotty config device --port /dev/ttyUSB1
```

### 6.2 Pen and Paper Inventory

```bash
# List all resources
uv run plotty list pens
uv run plotty list paper

# Add new paper size
uv run plotty add paper \
  --name "Custom Large" \
  --width 300 \
  --height 200 \
  --margin 15

# Update pen information
uv run plotty update pen 1 \
  --speed-cap 60 \
  --pressure "light"
```

### 6.3 Performance Monitoring

```bash
# Quick statistics overview
uv run plotty stats summary

# Detailed job analytics
uv run plotty stats jobs --last 30

# Performance metrics
uv run plotty stats performance --pen-usage
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

## 7. Real-World Examples

### 7.1 Graphic Design Studio

**Scenario:** Studio producing client logos and business cards

```bash
# Morning setup
uv run plotty check ready
uv run plotty status

# Process client batch
for file in client_*.svg; do
    uv run plotty add "$file" --paper a4 --name "Client $(basename "$file" .svg)"
done

# Optimize for production
uv run plotty plan-all --preset hq --optimize-pens

# Production run
uv run plotty plot-all --preset safe

# End of day report
uv run plotty stats summary --export > daily_report.json
```

### 7.2 Artist Workflow

**Scenario:** Artist creating multi-color art prints

```bash
# Add new artwork
uv run plotty add artwork_v2.svg --paper a3 --name "Abstract Series v2"

# Careful planning with custom pen mapping
uv run plotty plan artwork_v2 --interactive

# Test plot (small section)
uv run plotty record-test artwork_v2 --seconds 30

# Review test results
uv run plotty compare-test artwork_v2

# Full production plot
uv run plotty plot artwork_v2 --preset hq

# Document session
uv run plotty info job artwork_v2 --show-media
```

### 7.3 Educational Workshop

**Scenario:** Workshop with multiple participants

```bash
# Setup demo files
for participant in alice bob charlie; do
    uv run plotty add "${participant}_design.svg" --paper a4
done

# Quick batch planning
uv run plotty plan-all --preset fast

# Demonstrate plotting
uv run plotty plot alice_design --preview

# Let participants plot their work
uv run plotty plot bob_design
uv run plotty plot charlie_design

# Workshop summary
uv run plotty stats jobs --workshop
```

---

## 8. Tips and Best Practices

### 8.1 File Organization

```
projects/
├── active/
│   ├── client_a/
│   │   ├── logo.svg
│   │   └── business_card.svg
│   └── personal/
│       └── artwork.svg
├── archive/
│   ├── 2025-10/
│   └── 2025-11/
└── templates/
    ├── test_pattern.svg
    └── calibration.svg
```

### 8.2 Naming Conventions

**Good practices:**
```bash
# Descriptive names
uv run plotty add "client_logo_final_v2.svg" --name "Client Logo v2"
uv run plotty add "test_pattern_2025-11-07.svg" --name "Daily Test"

# Consistent dating
uv run plotty add "workshop_alice_20251107.svg" --name "Workshop: Alice"
```

### 8.3 Quality Assurance

```bash
# Always test new designs
uv run plotty record-test new_design --seconds 60

# Verify optimization results
uv run plotty estimate new_design --stage pre
uv run plotty estimate new_design --stage post

# Check pen mapping
uv run plotty info job new_design --show-layers

# Test plot settings
uv run plotty plot new_design --preview --dry-run
```

### 8.4 Maintenance

```bash
# Daily checks
uv run plotty check ready
uv run plotty status

# Weekly cleanup
uv run plotty queue cleanup --state completed
uv run plotty queue cleanup --older-than 7d

# Monthly review
uv run plotty stats summary --last 30
uv run plotty list pens --check-usage
uv run plotty list paper --check-usage
```

### 8.5 Troubleshooting Quick Tips

| Issue | Check | Solution |
|-------|-------|----------|
| Device not found | `plotty check device` | Check USB connection |
| Poor line quality | `plotty check servo` | Adjust pen heights |
| Slow plotting | `plotty stats performance` | Use fast preset |
| Camera not working | `plotty check camera` | Verify IP feed URL |
| Job stuck | `plotty recovery list` | Resume or abort |

---

## Getting Help

- **Command help**: `plotty --help` or `plotty <command> --help`
- **API documentation**: See `docs/api/` directory
- **Community**: GitHub Discussions
- **Issues**: GitHub Issues (include `plotty info system` output)

---

**This guide covers the essential ploTTY workflows for users at all levels. Start with the basics and gradually explore advanced features as you become comfortable with the system.**