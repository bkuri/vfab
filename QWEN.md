# ploTTY - Comprehensive Project Context

## Project Overview

ploTTY is a headless-first FSM (Finite State Machine) plotter manager that provides intelligent vector graphics optimization for plotting devices, particularly AxiDraw plotters. The project combines vpype optimization with smart multi-pen detection and per-session recording capabilities.

**Key Features:**
- **Finite State Machine Architecture**: Job lifecycle management following NEW → QUEUED → ANALYZED → OPTIMIZED → READY → ARMED → PLOTTING → COMPLETED/ABORTED/FAILED
- **Smart Multi-pen Detection**: Automatically detects SVG layers and provides interactive pen mapping
- **vpype Integration**: High-quality vector optimization with configurable presets
- **AxiDraw Hardware Support**: Direct integration with AxiDraw plotters (optional extra)
- **Session Recording**: IP camera integration for plot documentation
- **Database Management**: SQLAlchemy-based pen, paper, and job management
- **Crash Recovery**: Journal-based recovery system for interrupted operations

## Architecture & Components

### Core Modules
- `fsm.py`: Finite State Machine managing job lifecycle
- `models.py`: SQLAlchemy database models for jobs, pens, papers, and layers
- `cli/`: Typer-based command line interface
- `vpype.py`: Integration with vpype for vector optimization
- `planner.py`: Multi-pen layer planning and optimization
- `config.py`: Pydantic-based configuration system
- `db.py`: Database session management
- `plotting.py`: Plotting operations and device control
- `drivers/`: Hardware driver implementations
- `multipen/`: Multi-pen detection and mapping logic
- `hooks.py`: Event-based hook system
- `guards.py`: Pre-transition validation checks
- `recovery.py`: Crash recovery mechanisms
- `stats.py`: Statistics and metrics collection

### State Machine Design
The FSM implements these user stories:
- User Story 1: Queue new jobs with source file and paper selection
- User Story 2: Multi-pen optimization with vpype integration
- User Story 3: Pre-flight checks and job arming
- User Story 4: Plotting with pause/resume capabilities

### Database Models
- `Job`: Main job entity tracking state and metadata
- `Layer`: Individual SVG layers mapped to specific pens
- `Pen`: Pen definitions with width, speed, and pressure settings
- `Paper`: Paper size definitions with margins
- `Device`: Plotter device configurations
- `Statistics`: Comprehensive job, layer, and system metrics

## Building and Running

### Prerequisites
```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.12
```

### Installation
For planning and simulation (no hardware):
```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,vpype]"

# Initialize database
uv run alembic upgrade head
uv run pytest -q
uv run plotty --help
```

For AxiDraw hardware support:
```bash
uv pip install -e ".[dev,vpype,axidraw]"
uv run alembic upgrade head
uv run pytest -q
uv run plotty --help
```

### Key Commands
```bash
# Job management
uv run plotty job add --src path/to/file.svg --paper A3
uv run plotty job list
uv run plotty job plan <job_id> --interactive

# Plotting
uv run plotty plot <job_id>
uv run plotty plot <job_id> --preview  # Preview without actual plotting

# Configuration
uv run plotty config show
uv run plotty config edit

# Hardware control
uv run plotty plot pen-test
uv run plotty plot interactive  # Manual control

# Status and monitoring
uv run plotty status
uv run plotty stats summary
```

## Development Conventions

### Code Style
- Follows PEP 8 standards
- Uses Ruff for linting and Black for formatting
- Type hints required for all public functions
- Pydantic for configuration models
- SQLAlchemy for database models

### Testing
- Uses pytest for unit and integration testing
- Pre-commit hooks for code quality checks
- Database migration testing with Alembic

### Configuration
- Centralized configuration via Pydantic models
- YAML-based presets for vpype optimization
- Environment variable overrides supported
- Platform-specific data directories using platformdirs

### Error Handling
- Comprehensive exception handling in FSM transitions
- Journal-based crash recovery system
- Graceful degradation when optional components unavailable
- Detailed logging with rich formatting

## Project Structure
```
plotty/
├── src/plotty/           # Main source code
│   ├── cli/             # Command line interface
│   ├── drivers/         # Hardware drivers
│   ├── guards/          # FSM guards
│   ├── multipen/        # Multi-pen logic
│   ├── __init__.py      # Version and package init
│   ├── fsm.py           # Finite state machine
│   ├── models.py        # Database models
│   ├── config.py        # Configuration system
│   ├── vpype.py         # vpype integration
│   └── ...              # Other modules
├── config/              # Configuration files
├── alembic/             # Database migrations
├── pyproject.toml       # Project dependencies and metadata
└── README.md            # User documentation
```

## Core Concepts

### Multi-pen Workflow
1. **Detection**: Automatically identify SVG layers in input files
2. **Mapping**: Interactive assignment of layers to physical pens
3. **Optimization**: Sequential plotting with pen changes
4. **Validation**: Pre-flight checks before plotting

### vpype Optimization
- Configurable presets (fast vs high-quality)
- Dynamic paper sizing with automatic dimension substitution
- Line merging, sorting, and simplification
- Support for custom vpype command pipelines

### Job Lifecycle
- NEW → QUEUED → ANALYZED → OPTIMIZED → READY → ARMED → PLOTTING → (PAUSED) → COMPLETED/ABORTED/FAILED
- Each transition has validation guards and event hooks
- Journal-based recovery from crashes
- Comprehensive statistics collection

This project is designed for users who need reliable, optimized plotting with sophisticated multi-pen handling and crash recovery capabilities.