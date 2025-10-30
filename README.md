# ploTTY

Headless-first FSM plotter manager with vpype optimization, multi-pen planning (per layer),
and per-session recording (IP feed v1; native v4l2 later).

## Quickstart (Arch/Linux)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,vpype]"      # add ",axidraw" if you have hardware
alembic upgrade head
plotty add --src demo.svg --paper A3 | tee /tmp/J
plotty plan $(cat /tmp/J)
plotty record_test $(cat /tmp/J) --seconds 5
````

