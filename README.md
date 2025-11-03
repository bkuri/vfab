# ploTTY

Headless-first FSM plotter manager with vpype optimization, smart multi-pen detection,
and per-session recording (IP feed v1; native v4l2 later).

## Quick Start

### Prerequisites
```bash
# install uv (Arch)
pacman -Qi uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh

# ensure Python 3.11+ available (uv can manage it too)
uv python install 3.12
```

### Installation

**For Planning & Simulation (no AxiDraw hardware):**
```bash
# create venv + install project in editable mode
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,vpype]"

# DB migrate + smoke test
uv run alembic upgrade head
uv run pytest -q

# try CLI
uv run plotty --help
```

**For AxiDraw Hardware Support:**
```bash
# install with AxiDraw integration
uv pip install -e ".[dev,vpype,axidraw]"

# DB migrate + smoke test  
uv run alembic upgrade head
uv run pytest -q

# try CLI
uv run plotty --help
```

> **Note**: ploTTY works perfectly without AxiDraw hardware for planning, optimization, and simulation. Install axidraw extra only if you have physical hardware.

## AxiDraw Integration

ploTTY provides **smart AxiDraw integration** with automatic multipen detection and graceful degradation.

### Installation

```bash
# Install with AxiDraw support
uv pip install -e ".[dev,vpype,axidraw]"
```

> **Important**: ploTTY works without AxiDraw hardware for planning and simulation. The axidraw extra is only needed for physical plotting.

### AxiDraw CLI Commands

```bash
# Plan a job with smart multipen detection
uv run plotty plan <job_id> --interactive

# Plot a job with AxiDraw (supports multipen)
uv run plotty plot <job_id>

# Preview plot without moving pen
uv run plotty plot <job_id> --preview

# Interactive XY control
uv run plotty interactive

# Test pen up/down movement
uv run plotty pen-test

# List available pens from database
uv run plotty pen-list

# Add new pen to database
uv run plotty pen-add
```

### Smart Multipen Detection

ploTTY automatically detects layers in your SVG files and provides:

- **🎨 Color-coded layer overview** with element counts
- **🚫 Hidden layer filtering** (skips Inkscape hidden layers and `%` documentation layers)  
- **🖊️ Interactive pen mapping** for multi-layer designs
- **⚡ Automatic mode selection** (single-pen vs multi-pen)

### vpype Optimization Presets

ploTTY includes vpype presets for different optimization levels with **dynamic paper sizing**:

```yaml
# config/vpype-presets.yaml
presets:
  fast:
    pipe: "read {src} pagesize {pagesize} crop 0 0 {width_mm:g}mm {height_mm:g}mm linemerge linesort write {dst}"
  
  hq:
    pipe: "read {src} pagesize {pagesize} crop 0 0 {width_mm:g}mm {height_mm:g}mm linemerge linesort linesimplify write {dst}"
```

**Available presets:**
- **`fast`**: Quick optimization (linemerge + linesort) - default
- **`hq`**: High quality (adds linesimplify for segment reduction)

**Dynamic paper sizing**: Presets automatically use the paper size from your config:
```yaml
# config/config.yaml
vpype:
  preset: fast                    # or hq
  presets_file: "config/vpype-presets.yaml"

paper:
  default_size: A4               # A3, A4, Letter, etc.
  default_margin_mm: 10.0
  default_orientation: portrait
```

The `{pagesize}`, `{width_mm}`, and `{height_mm}` placeholders are automatically replaced with your configured paper size, so you don't need separate presets for different paper sizes!

### AxiDraw Configuration

Add AxiDraw device configuration to your config:

```yaml
devices:
  axidraw:
    port: /dev/ttyUSB0          # or COM3 on Windows, auto-detect if None
    model: 1                   # 1=V2/V3/SE/A4, 2=V3/A3/SE/A3, etc.
    pen_up_position: 50          # 0-100, higher = more up
    pen_down_position: 30        # 0-100, lower = more down
    pen_speed: 50                # 1-100, percentage of max speed
    pen_lift_speed: 75           # 1-100, percentage of max speed
    units: mm                   # mm, cm, or inches
```

### Error Handling

If AxiDraw support is not installed, ploTTY provides clear guidance:

```
❌ AxiDraw support not available. Install with: uv pip install -e '.[axidraw]'
```

All non-AxiDraw features (planning, optimization, simulation) work without the axidraw extra.

### AxiDraw CLI Commands

```bash
# Check AxiDraw status and list connected devices
uv run plotty axidraw status

# Plot a job with AxiDraw (with time estimation)
uv run plotty axidraw plot <job_id>

# Preview plot without moving the pen
uv run plotty axidraw plot <job_id> --preview

# Interactive XY control
uv run plotty axidraw interactive

# Test pen up/down movement
uv run plotty axidraw pen-test
```

### AxiDraw Configuration

Add AxiDraw device configuration to your config:

```yaml
devices:
  axidraw:
    port: /dev/ttyUSB0          # or COM3 on Windows
    model: AxiDraw V3/A3        # AxiDraw V3/A3, AxiDraw V3/A2, etc.
    pen_up_position: 50          # 0-100, higher = more up
    pen_down_position: 30        # 0-100, lower = more down
    pen_speed: 50                # 1-100, percentage of max speed
    pen_lift_speed: 75           # 1-100, percentage of max speed
    units: mm                   # mm, cm, or inches
```

## Common Development Tasks

```bash
# lint / format
uvx ruff check .
uvx black .

# pre-commit (once)
uvx pre-commit install
uvx pre-commit run -a

# run tools without activating venv
uv run plotty add --src demo.svg --paper A3 | tee /tmp/J
uv run plotty plan "$(cat /tmp/J)" --interactive
uv run plotty record_test "$(cat /tmp/J)" --seconds 5

# test AxiDraw integration (if hardware available)
uv run plotty pen-test --cycles 1
uv run plotty interactive --help
```

## Feature Highlights

- **🧠 Smart Multipen Detection**: Automatically detects SVG layers and suggests pen mapping
- **🎨 Color-Coded Overview**: Visual layer display with element counts and colors
- **🚫 Hidden Layer Filtering**: Skips Inkscape hidden layers per AxiDraw standards
- **⚡ Graceful Degradation**: Works perfectly without AxiDraw hardware
- **📊 Time Estimation**: Accurate plotting time estimates with vpype optimization
- **🎥 Session Recording**: IP camera integration for plot documentation
- **🖊️ Pen Database**: Manage multiple pens with width and speed settings
# CI/CD Debug
