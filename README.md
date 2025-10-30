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
