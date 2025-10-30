# ploTTY Agent Guidelines

## Build/Test Commands
- **Install**: `uv pip install -e ".[dev,vpype]"` (add `,axidraw` for hardware)
- **Lint**: `uvx ruff check .`
- **Format**: `uvx black .`
- **Test single**: `uv run pytest tests/test_<module>.py -q`
- **Test all**: `uv run pytest -q`
- **DB migrate**: `uv run alembic upgrade head`
- **Pre-commit**: `uvx pre-commit install && uvx pre-commit run -a`

## Code Style
- **Python**: 3.11+, use `from __future__ import annotations`
- **Imports**: Group stdlib, third-party, local imports; use `typer`, `pydantic`, `pathlib`
- **Formatting**: Black with default settings
- **Types**: Use Pydantic models for config, type hints everywhere
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error handling**: Use `typer.BadParameter` for CLI validation, `SystemExit` for fatal errors
- **CLI**: Use Typer for commands, `no_args_is_help=True`
- **Config**: YAML-based with Pydantic validation in `config.py`
- **Tests**: pytest with descriptive docstrings, Mock for external deps