# ploTTY

Headless-first FSM plotter manager with vpype optimization, multi-pen planning (per layer),
and per-session recording (IP feed v1; native v4l2 later).

# install uv (Arch)
pacman -Qi uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh

# ensure Python 3.11+ available (uv can manage it too)
uv python install 3.12

# create venv + install project in editable mode with dev extras
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,vpype]"   # add ",axidraw" if you have the hardware

# DB migrate + smoke
uv run alembic upgrade head
uv run pytest -q

# try CLI
uv run plotty --help

## AxiDraw Integration

If you have an AxiDraw plotter, install with the axidraw extra:

```bash
uv pip install -e ".[dev,vpype,axidraw]"
```

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

## Common dev tasks

```bash
# lint / format
uvx ruff check .
uvx black .

# pre-commit (once)
uvx pre-commit install
uvx pre-commit run -a

# run tools without activating venv
uv run plotty add --src demo.svg --paper A3 | tee /tmp/J
uv run plotty plan "$(cat /tmp/J)"
uv run plotty record_test "$(cat /tmp/J)" --seconds 5
```
