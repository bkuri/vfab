# vpype-vfab Integration Guide

## Overview

**vpype-vfab** is a vpype plugin that seamlessly bridges creative tools (vsketch, vpype) with vfab's production plotter management system. It enables a complete workflow from generative art creation to professional plotter job management.

## Installation

### For vsketch Users

```bash
# Install plugin into vsketch environment
pipx inject vsketch vpype-vfab

# Verify installation
vsk --help | grep vfab
```

### For vpype Users

```bash
# Install plugin into vpype environment  
pipx inject vpype vpype-vfab

# Verify installation
vpype --help | grep vfab
```

### Development Installation

```bash
# Clone repository
git clone https://github.com/your-org/vpype-vfab.git
cd vpype-vfab

# Install in development mode
pip install -e ".[dev]"

# Install into local vpype for testing
pipx inject vpype -e .
```

## Quick Start

### vsketch Integration

The most common use case is integrating vpype-vfab directly into your vsketch workflow:

```python
import vsketch

class MySketch(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")
        
        # Your generative art code here
        for i in range(22):
            with vsk.pushMatrix():
                for j in range(12):
                    with vsk.pushMatrix():
                        vsk.rotate(0.03 * vsk.random(-i, i))
                        vsk.translate(
                            0.01 * vsk.randomGaussian() * i,
                            0.01 * vsk.randomGaussian() * i,
                        )
                        vsk.rect(0, 0, 1, 1)
                    vsk.translate(1, 0)
            vsk.translate(0, 1)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        # Standard vpype optimization
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Add to vfab with high-quality preset and auto-queue
        vsk.vpype("vfab-add --name schotter --preset hq --queue")

if __name__ == "__main__":
    MySketch().display()
```

### Standalone vpype Usage

You can also use vpype-vfab directly with vpype commands:

```bash
# Create generative art and add to vfab
vpype rand --seed 123 vfab-add --name random_art --preset fast

# Add existing SVG to vfab
vpype read input.svg vfab-add --name existing_design --paper A3

# Queue existing job
vpype vfab-queue --name my_design --priority 2

# Check job status
vpype vfab-status --name my_design

# List all queued jobs
vpype vfab-list --state queued --format table
```

## Command Reference

### `vfab-add`

Add current vpype document to vfab job queue.

```bash
vpype vfab-add [OPTIONS]
```

**Options:**
- `--name, -n`: Job name (defaults to auto-generated timestamp)
- `--preset, -p`: Optimization preset (`fast`, `default`, `hq`) [default: `fast`]
- `--paper`: Paper size [default: `A4`]
- `--queue/--no-queue`: Automatically queue job after adding [default: `no-queue`]
- `--workspace`: vfab workspace path (auto-detected if omitted)

**Examples:**
```bash
# Basic usage
vpype vfab-add --name my_design

# High-quality optimization with auto-queue
vpype vfab-add --name detailed_art --preset hq --queue

# Custom paper size
vpype vfab-add --name poster --paper A3 --preset default
```

### `vfab-queue`

Queue existing vfab job for plotting.

```bash
vpype vfab-queue [OPTIONS]
```

**Options:**
- `--name, -n`: Job name to queue [required]
- `--priority`: Job priority (higher numbers = higher priority) [default: `1`]
- `--interactive/--no-interactive`: Interactive pen mapping for multi-pen designs [default: `interactive`]

**Examples:**
```bash
# Queue job with default settings
vpype vfab-queue --name my_design

# High priority job with interactive pen mapping
vpype vfab-queue --name urgent_job --priority 5 --interactive

# Non-interactive queue (use existing pen mapping)
vpype vfab-queue --name batch_job --no-interactive
```

### `vfab-status`

Check vfab job status.

```bash
vpype vfab-status [OPTIONS]
```

**Options:**
- `--name, -n`: Specific job name (shows all if omitted)
- `--format`: Output format (`table`, `json`, `simple`) [default: `table`]

**Examples:**
```bash
# Show status for specific job
vpype vfab-status --name my_design

# Show all jobs in JSON format
vpype vfab-status --format json

# Simple text output
vpype vfab-status --format simple
```

### `vfab-list`

List vfab jobs with filtering options.

```bash
vpype vfab-list [OPTIONS]
```

**Options:**
- `--state`: Filter by job state (`queued`, `ready`, `plotting`, `completed`, `failed`)
- `--format`: Output format (`table`, `json`, `csv`) [default: `table`]
- `--limit`: Limit number of jobs shown

**Examples:**
```bash
# List all queued jobs
vpype vfab-list --state queued

# Export completed jobs to CSV
vpype vfab-list --state completed --format csv

# Show first 5 jobs in JSON format
vpype vfab-list --limit 5 --format json
```

## Workflow Examples

### Creative to Production Pipeline

This complete example shows how to go from creative exploration to production plotting:

```python
# sketch_my_design.py
import vsketch

class GenerativeDesign(vsketch.SketchClass):
    # Parameters for interactive exploration
    complexity = vsketch.Param(50)
    density = vsketch.Param(10)
    variation = vsketch.Param(1.0)
    
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")
        
        # Generative pattern based on parameters
        for i in range(self.complexity):
            angle = i * 0.1 * self.variation
            radius = 0.5 + 0.5 * vsk.random(-1, 1)
            
            with vsk.pushMatrix():
                vsk.rotate(angle)
                vsk.translate(
                    vsk.randomGaussian() * self.density * 0.1,
                    vsk.randomGaussian() * self.density * 0.1
                )
                vsk.circle(0, 0, radius=radius)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        # Optimize for plotting
        vsk.vpype("linemerge linesimplify reloop linesort")
        
        # Add to vfab with parameter-based naming
        job_name = f"gen_design_c{self.complexity}_d{self.density}_v{self.variation:.1f}"
        vsk.vpype(f"vfab-add --name '{job_name}' --preset hq --queue")

if __name__ == "__main__":
    GenerativeDesign().display()
```

```bash
# Run interactively to explore parameters
vsk run sketch_my_design

# Once satisfied, generate multiple variants
for complexity in 30 50 70; do
    for density in 5 10 15; do
        for variation in 0.5 1.0 1.5; do
            vsk run sketch_my_design --set complexity=$complexity density=$density variation=$variation --save-only
            vsk run sketch_my_design --set complexity=$complexity density=$density variation=$variation
        done
    done
done

# Check queue status
vpype vfab-list --state queued

# Monitor first job
vpype vfab-status --name gen_design_c50_d10_v1.0
```

### Batch Processing Workflow

For generating large numbers of designs:

```python
# batch_generator.py
import subprocess
import json
from pathlib import Path

def generate_batch(base_name, seed_range, preset="fast"):
    """Generate multiple designs and queue them."""
    job_ids = []
    
    for seed in seed_range:
        print(f"Generating design with seed {seed}...")
        
        # Generate design using vsketch
        cmd = [
            "vsk", "run", "batch_design.py",
            "--set", f"seed={seed}",
            "--save-only"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to generate seed {seed}: {result.stderr}")
            continue
        
        # Find the generated SVG
        output_dir = Path("output")
        svg_files = list(output_dir.glob(f"batch_design_*_{seed}.svg"))
        
        if not svg_files:
            print(f"❌ No SVG found for seed {seed}")
            continue
            
        svg_file = svg_files[0]
        job_name = f"{base_name}_seed_{seed}"
        
        # Add to vfab
        cmd = [
            "vpype", "read", str(svg_file),
            "vfab-add", 
            "--name", job_name,
            "--preset", preset,
            "--queue"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            job_id = result.stdout.strip()
            job_ids.append(job_id)
            print(f"✅ Queued job {job_id} for seed {seed}")
        else:
            print(f"❌ Failed to queue seed {seed}: {result.stderr}")
    
    # Save job list for reference
    with open(f"{base_name}_jobs.json", "w") as f:
        json.dump(job_ids, f, indent=2)
    
    return job_ids

if __name__ == "__main__":
    # Generate 50 designs with seeds 100-149
    jobs = generate_batch("batch_experiment", range(100, 150))
    print(f"Successfully queued {len(jobs)} jobs")
```

### Multi-Pen Design Workflow

For designs that use multiple pens/colors:

```python
# multipen_design.py
import vsketch

class MultiPenDesign(vsketch.SketchClass):
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=False)
        vsk.scale("cm")
        
        # Layer 1: Black pen - outlines
        vsk.stroke(1)
        vsk.penWidth("0.3mm", 1)
        for i in range(5):
            vsk.circle(i * 3, i * 2, radius=1)
        
        # Layer 2: Red pen - details
        vsk.stroke(2)
        vsk.penWidth("0.2mm", 2)
        for i in range(5):
            with vsk.pushMatrix():
                vsk.translate(i * 3, i * 2)
                for j in range(8):
                    angle = j * 45
                    vsk.line(0, 0, 
                             0.5 * vsk.cos(angle), 
                             0.5 * vsk.sin(angle))
        
        # Layer 3: Blue pen - accents
        vsk.stroke(3)
        vsk.penWidth("0.5mm", 3)
        for i in range(5):
            vsk.circle(i * 3 + 1.5, i * 2 + 1, radius=0.2)
    
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")
        vsk.vpype("vfab-add --name multipen_art --preset hq --queue")

if __name__ == "__main__":
    MultiPenDesign().display()
```

```bash
# This will trigger interactive pen mapping
vsk run multipen_design.py

# Or queue non-interactively with predefined pen mapping
vpype vfab-queue --name multipen_art --no-interactive
```

## Configuration

### vfab Workspace Detection

vpype-vfab automatically detects vfab workspace using this priority order:

1. **Explicit workspace path** (`--workspace` option)
2. **Current directory**: `./vfab-workspace/`
3. **Home directory**: `~/vfab-workspace/`
4. **XDG data directory**: `~/.local/share/vfab/`
5. **Create default**: `~/vfab-workspace/` (if none found)

### vfab Configuration

The plugin reads vfab configuration from:
- `{workspace}/config.yaml`
- `{workspace}/vpype-presets.yaml`

If vfab is not installed, vpype-vfab uses sensible defaults:
```yaml
vpype:
  preset: fast
  presets_file: vpype-presets.yaml
paper:
  default_size: A4
  default_margin_mm: 10.0
```

### Optimization Presets

Available presets match vfab's optimization levels:

| Preset | Description | Use Case |
|---------|-------------|----------|
| `fast` | Quick optimization (linemerge + linesort) | Drafts, quick tests |
| `default` | Balanced optimization | General use |
| `hq` | High quality (adds linesimplify) | Final production |

### ⚠️ Optimization Handling

**Important**: vpype-vfab provides flexible control over optimization to prevent double-processing:

#### **Optimization Scenarios**

**1. vsketch Integration (Recommended)**
```python
def finalize(self, vsk: vsketch.Vsketch) -> None:
    # vsketch handles optimization
    vsk.vpype("linemerge linesimplify reloop linesort")
    
    # Skip vfab optimization (already optimized)
    vsk.vpype("vfab-add --name my_design --preset none --queue")
```

**2. Raw SVG Processing**
```bash
# Let vpype optimize, vfab skips
vpype read raw.svg linemerge linesimplify vfab-add --name optimized --preset none

# Let vfab optimize
vpype read raw.svg vfab-add --name raw --preset hq
```

**3. Pre-optimized Files**
```bash
# Already optimized SVG - skip all optimization
vpype read optimized.svg vfab-add --name production --preset none
```

#### **Optimization Control Options**

| Command | Optimization Applied | Use Case |
|---------|-------------------|------------|
| `--preset none` | Skip vfab optimization | Already optimized by vsketch/vpype |
| `--preset fast` | Use vfab fast preset | Quick vfab optimization |
| `--preset hq` | Use vfab high-quality preset | Production quality |
| `--preset default` | Use vfab balanced preset | General use |

#### **How vfab Detects Optimization**

vpype-vfab communicates optimization state to vfab through metadata:

```python
# vpype-vfab adds optimization metadata
job_metadata = {
    'name': job_name,
    'preset': preset,
    'optimized_by_vpype': True,  # Tells vfab to skip optimization
    'vpype_commands': ['linemerge', 'linesimplify', 'reloop', 'linesort']
}
```

**Result**: vfab sees `optimized_by_vpype: True` and skips its optimization step, preventing double-processing.

#### **Best Practices**

**For vsketch users:**
- Use `--preset none` to leverage vsketch's optimization
- vsketch provides creative control, vfab handles production

**For vpype users:**
- Optimize in vpype, use `--preset none` in vfab
- Or use vfab presets for consistent production quality

**For mixed workflows:**
- Match optimization levels: vpype `fast` → vfab `fast`
- Use `--preset hq` for final production regardless of source

## Troubleshooting

### Common Issues

**vfab workspace not found**
```bash
# Check if vfab is installed
vfab --version

# Create workspace manually
mkdir -p ~/vfab-workspace
vfab init ~/vfab-workspace

# Or specify workspace explicitly
vpype vfab-add --workspace /path/to/workspace --name my_design
```

**Plugin not found in vpype/vsketch**
```bash
# Verify installation
pipx list | grep vpype-vfab

# Reinstall if needed
pipx inject vpype vpype-vfab --force

# Check vpype plugin registration
vpype --help | grep vfab
```

**Job creation fails**
```bash
# Enable verbose output
vpype -v vfab-add --name test_design

# Check vfab configuration
cat ~/vfab-workspace/config.yaml

# Test vfab directly
vfab add job test_design --src test.svg --apply
```

**Pen mapping issues**
```bash
# Check vfab pen database
vfab list pens

# Use interactive mode for first setup
vpype vfab-queue --name my_design --interactive

# Or configure pens first
vfab setup
```

### Getting Help

```bash
# vpype-vfab specific help
vpype vfab-add --help
vpype vfab-queue --help
vpype vfab-status --help
vpype vfab-list --help

# General vpype help
vpype --help

# vfab help (if installed)
vfab --help
```

## Advanced Usage

### Custom Job Templates

Create reusable job templates for consistent settings:

```python
# job_template.py
import subprocess
import json
from pathlib import Path

def create_job_from_template(svg_path, template_name, **kwargs):
    """Create job using predefined template."""
    
    templates = {
        "production": {
            "preset": "hq",
            "paper": "A4",
            "queue": True
        },
        "draft": {
            "preset": "fast", 
            "paper": "A4",
            "queue": False
        },
        "poster": {
            "preset": "hq",
            "paper": "A3",
            "queue": True
        }
    }
    
    if template_name not in templates:
        raise ValueError(f"Unknown template: {template_name}")
    
    template = templates[template_name]
    template.update(kwargs)
    
    # Build command
    cmd = [
        "vpype", "read", svg_path,
        "vfab-add",
        "--name", kwargs.get("name", f"template_{template_name}"),
        "--preset", template["preset"],
        "--paper", template["paper"]
    ]
    
    if template["queue"]:
        cmd.append("--queue")
    
    # Execute
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Created job: {result.stdout.strip()}")
    else:
        print(f"❌ Failed: {result.stderr}")
    
    return result.returncode == 0

# Usage examples
create_job_from_template("design.svg", "production", name="final_art")
create_job_from_template("sketch.svg", "draft", name="test_print")
create_job_from_template("poster.svg", "poster", name="large_print")
```

### Integration with Other Tools

vpype-vfab works with any tool that outputs SVG:

```bash
# From Inkscape
inkscape --export-type=svg design.svg
vpype read design.svg vfab-add --name inkscape_design

# From other generative tools
my_generative_tool --output design.svg
vpype read design.svg vfab-add --name generated_art

# From vector editing software
illustrator --export design.svg
vpype read design.svg vfab-add --name illustrator_art
```
