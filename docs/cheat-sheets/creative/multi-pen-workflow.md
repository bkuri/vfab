# Multi-Pen Workflow Cheat Sheet

**Colorful designs made easy** - Master multi-pen plotting for stunning artwork.

---

## 🧭 Quick Navigation
- **New to vfab?** [First Plot Checklist](../beginner/first-plot-checklist.md)
- **Want to generate designs?** [vsketch Integration](vsketch-integration.md)
- **Need to optimize for multi-pen?** [Design Optimization](design-optimization.md)
- **Making many copies?** [Batch Production](../power-user/batch-production.md)

---

## 🎨 Understanding Multi-Pen Detection

vfab automatically detects multi-pen needs from:

### SVG Layers (Recommended)
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

### AxiDraw Layer Comments
```xml
<!-- %layer: outline -->
<path d="..." stroke="black" stroke-width="0.5"/>

<!-- %layer: shading -->
<path d="..." stroke="gray" stroke-width="0.3"/>
```

---

## 🖊️ Pen Setup & Management

### Quick Pen Setup
```bash
# List current pens
vfab list pens

# Add essential pens
vfab add pen --name "Fine Black" --width 0.3 --color "#000000"
vfab add pen --name "Medium Black" --width 0.7 --color "#000000"
vfab add pen --name "Fine Red" --width 0.3 --color "#FF0000"
vfab add pen --name "Medium Blue" --width 0.5 --color "#0000FF"
```

### Professional Pen Collection
```bash
# Fine detail pens
vfab add pen --name "Ultra Fine Black" --width 0.2 --color "#000000" --speed-cap 40
vfab add pen --name "Fine Black" --width 0.3 --color "#000000" --speed-cap 50
vfab add pen --name "Fine Red" --width 0.3 --color "#FF0000" --speed-cap 50

# Medium workhorse pens
vfab add pen --name "Medium Black" --width 0.7 --color "#000000" --speed-cap 80
vfab add pen --name "Medium Blue" --width 0.5 --color "#0000FF" --speed-cap 70

# Specialty pens
vfab add pen --name "Gold" --width 0.5 --color "#FFD700" --speed-cap 60
vfab add pen --name "Silver" --width 0.5 --color "#C0C0C0" --speed-cap 60
```

### View Pen Usage
```bash
# See all pens with usage stats
vfab list pens --show-usage

# Check pen performance
vfab stats pens --last 30
```

---

## 🎯 Multi-Pen Job Workflow

### Step 1: Add Multi-Pen Design
```bash
# Add with automatic detection
vfab add colorful_design.svg --name "Rainbow Art" --paper a4

# Add with custom name
vfab add multi_layer_art.svg --name "Client Logo - Multi-Color"
```

### Step 2: Interactive Pen Mapping
```bash
# Plan with interactive pen mapping
vfab plan colorful_art --interactive
```

**Interactive mapping example:**
```
🎨 Multi-Pen Layer Detection
============================
Detected 3 layers:
  🔵 Layer 1: "outline" (523 points) - BLACK
  🟢 Layer 2: "fill" (1,247 points) - GRAY
  🟡 Layer 3: "highlights" (89 points) - WHITE

Available pens:
  [1] Ultra Fine Black 0.2mm
  [2] Fine Black 0.3mm
  [3] Medium Black 0.7mm
  [4] Fine Red 0.3mm
  [5] Medium Blue 0.5mm

Map layers to pens (e.g. "1,2,3"): 3,2,4

🔄 Pen Change Optimization
=========================
Original pen changes: 6
Optimized pen changes: 2 (67% reduction)
Time saved: ~4 minutes

✅ Pen mapping saved
```

### Step 3: Plot with Pen Changes
```bash
# Start multi-pen plotting
vfab plot colorful_art
```

**During plotting:**
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

---

## ⚡ Advanced Multi-Pen Techniques

### Optimize Pen Changes
```bash
# Global pen optimization across all jobs
vfab plan-all --optimize-pens --global-pen-order

# Custom pen change priority
vfab plan colorful_art --pen-order 3,2,4,1

# Minimize pen changes
vfab plan colorful_art --minimize-pen-changes
```

### Smart Pen Mapping Strategies
```bash
# Strategy 1: Group by color darkness
vfab plan artwork --group-by-darkness

# Strategy 2: Minimize pen change time
vfab plan artwork --optimize-pen-time

# Strategy 3: Balance pen wear
vfab plan artwork --balance-pen-wear
```

### Batch Multi-Pen Processing
```bash
# Add multiple multi-pen designs
for file in multi_pen_*.svg; do
    vfab add "$file" --name "Multi: $(basename "$file" .svg)"
done

# Optimize all for minimal pen changes
vfab plan-all --optimize-pens --global-optimization

# Plot all with pen change prompts
vfab plot-all --auto-pen-change
```

---

## 🎨 Design Tips for Multi-Pen

### Layer Organization Best Practices

**Good layer structure:**
```xml
<svg>
  <!-- Dark colors first (less visible pen changes) -->
  <g inkscape:label="dark_elements">
    <path stroke="black" .../>
    <path stroke="darkgray" .../>
    <path stroke="darkblue" .../>
  </g>
  
  <!-- Medium colors -->
  <g inkscape:label="medium_elements">
    <path stroke="red" .../>
    <path stroke="blue" .../>
    <path stroke="green" .../>
  </g>
  
  <!-- Light colors last (more visible pen changes) -->
  <g inkscape:label="light_elements">
    <path stroke="white" .../>
    <path stroke="lightgray" .../>
    <path stroke="yellow" .../>
  </g>
</svg>
```

### Color Grouping Strategies
```xml
<!-- Strategy 1: Group by pen type -->
<g inkscape:label="fine_lines">
  <path stroke-width="0.2" .../>
  <path stroke-width="0.3" .../>
</g>
<g inkscape:label="medium_lines">
  <path stroke-width="0.5" .../>
  <path stroke-width="0.7" .../>
</g>

<!-- Strategy 2: Group by color family -->
<g inkscape:label="warm_colors">
  <path stroke="red" .../>
  <path stroke="orange" .../>
  <path stroke="yellow" .../>
</g>
<g inkscape:label="cool_colors">
  <path stroke="blue" .../>
  <path stroke="green" .../>
  <path stroke="purple" .../>
</g>
```

### Pen Change Minimization
```xml
<!-- Bad: Frequent pen changes -->
<g inkscape:label="black"><path stroke="black"/></g>
<g inkscape:label="red"><path stroke="red"/></g>
<g inkscape:label="black"><path stroke="black"/></g>
<g inkscape:label="red"><path stroke="red"/></g>

<!-- Good: Grouped by pen -->
<g inkscape:label="black_elements">
  <path stroke="black"/>
  <path stroke="black"/>
</g>
<g inkscape:label="red_elements">
  <path stroke="red"/>
  <path stroke="red"/>
</g>
```

---

## 🔧 Multi-Pen Troubleshooting

### Common Issues

**Pen change prompts not appearing:**
```bash
# Check if multi-pen was detected
vfab info job my_job --show-layers

# Force multi-pen mode
vfab plan my_job --force-multi-pen
```

**Wrong pen mapping:**
```bash
# Re-plan with different mapping
vfab plan my_job --interactive --remap-pens

# Check current pen mapping
vfab info job my_job --show-pen-mapping
```

**Too many pen changes:**
```bash
# Optimize pen changes
vfab plan my_job --optimize-pens --aggressive

# Check pen change optimization
vfab estimate my_job --show-pen-changes
```

### Pen Quality Issues

**Inconsistent line quality between pens:**
```bash
# Check pen-specific settings
vfab list pens --show-settings

# Adjust pen speed caps
vfab update pen 1 --speed-cap 40  # Slower for fine pens
vfab update pen 3 --speed-cap 80  # Faster for medium pens
```

**Pen-specific optimization:**
```bash
# Plan with pen-specific settings
vfab plan my_job --pen-specific-optimization

# Test pen performance
vfab test pen --pen-id 1 --pattern detailed
vfab test pen --pen-id 3 --pattern fast
```

---

## 📊 Multi-Pen Analytics

### Track Multi-Pen Performance
```bash
# Pen usage statistics
vfab stats pens --last 30 --by-job-type

# Multi-pen job analysis
vfab stats jobs --multi-pen-only --last 30

# Pen change efficiency
vfab stats performance --pen-change-analysis
```

### Sample Analytics Output
```
📊 Multi-Pen Statistics (Last 30 Days)
======================================
Multi-pen jobs: 24 (48% of total)
Average pen changes per job: 2.3
Pen change time saved: 45 minutes total

🖊️ Pen Usage Breakdown
========================
Fine Black: 18 jobs (75% of multi-pen jobs)
Medium Black: 12 jobs (50%)
Fine Red: 8 jobs (33%)
Medium Blue: 6 jobs (25%)

⚡ Pen Change Optimization
========================
Original pen changes: 156
Optimized pen changes: 89 (43% reduction)
Time saved: 1h 23m
```

---

## 🎯 Professional Multi-Pen Workflows

### Limited Edition Multi-Pen Prints
```bash
# Create edition with consistent pen mapping
edition_size=10
artwork="Rainbow Geometry"

for i in $(seq 1 $edition_size); do
    # Generate with consistent seed for reproducibility
    vfab add "${artwork}_edition${i}.svg" \
        --name "${artwork} - Edition ${i}/${edition_size}" \
        --paper a3
    
    # Use same pen mapping for all editions
    vfab plan "${artwork}_edition${i}" \
        --pen-mapping "3,2,4,1" \
        --save-mapping
done

# Plot all editions with consistent pen changes
vfab plot-all --preserve-pen-order
```

### Client Multi-Pen Projects
```bash
# Professional client workflow
client_name="Acme Corp"
project_name="Brand Colors"

# Add client designs with color standards
vfab add logo.svg --name "${client_name} - Logo" --paper a4
vfab add business_card.svg --name "${client_name} - Business Card" --paper a4

# Use client-specific pen mapping
vfab plan-all --pen-mapping "2,4,3" --client-standards

# Plot with quality documentation
vfab plot-all --document-pen-changes --quality-check
```

---

## 💡 Multi-Pen Pro Tips

### Efficiency Tips
- 🎨 **Group similar colors** in the same layers
- 🖊️ **Use consistent pen mapping** across editions
- ⚡ **Optimize pen changes** before plotting
- 📊 **Track pen usage** to balance wear

### Quality Tips
- 🖊️ **Test pen combinations** on scrap paper
- 🎯 **Use appropriate pen widths** for detail levels
- ⏱️ **Adjust speed per pen** for consistent quality
- 📹 **Document pen changes** for client work

### Creative Tips
- 🌈 **Plan color hierarchy** - dark to light colors
- 🎨 **Consider pen contrast** - visible vs subtle changes
- 📐 **Group by visual weight** - fine details together
- 🔄 **Create pen change patterns** - artistic effect

---

## 📚 Quick Reference

### Pen Mapping Shortcuts
```bash
# Quick pen mapping for common setups
vfab plan job --preset "dark_to_light"    # Black → Gray → White
vfab plan job --preset "warm_to_cool"     # Red → Blue → Green
vfab plan job --preset "fine_to_medium"    # 0.3mm → 0.7mm
```

### Emergency Multi-Pen Commands
```bash
# Skip pen change for problematic layer
vfab plot job --skip-pen-change

# Force single-pen mode
vfab plan job --force-single-pen --pen-id 2

# Reset pen mapping
vfab plan job --reset-pen-mapping
```

---

**🎯 Goal:** Create stunning multi-color artwork with minimal pen changes and maximum quality.

**📚 Next:** [vsketch Integration](vsketch-integration.md) for creative coding workflows.