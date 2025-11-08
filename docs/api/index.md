# ploTTY API Documentation Index

Welcome to the comprehensive ploTTY API documentation. This documentation provides complete coverage of ploTTY's APIs for developers, users, and system integrators.

## 📚 Documentation Sections

### [📖 Overview](README.md)
- Introduction to ploTTY architecture
- Quick start guide
- Key concepts and terminology
- System architecture overview

### [🖥️ CLI API Reference](cli-reference.md)
- Complete command-line interface documentation
- All commands, options, and arguments
- Usage examples and best practices
- Exit codes and error handling

### [🗄️ Database Models](database-models.md)
- SQLAlchemy model definitions
- Database schema and relationships
- Query examples and patterns
- Migration information

### [⚙️ Configuration Schema](configuration-schema.md)
- Complete configuration reference
- All configuration options and defaults
- YAML configuration examples
- Environment variable support

### [🏗️ Core Classes and Methods](core-classes.md)
- Public API documentation
- Key classes and their methods
- Integration patterns
- Code examples

### [🔄 Job Lifecycle and States](job-lifecycle.md)
- Finite State Machine (FSM) documentation
- State transitions and validation
- Job metadata and history
- Error handling and recovery

### [🔧 Examples and Integration](examples-integration.md)
- Practical integration examples
- Web API implementations
- Automation workflows
- Testing patterns

## 🚀 Quick Start

### For Users

```bash
# Install ploTTY
uv pip install -e ".[dev,vpype]"

# Add and plot a job
plotty add job my_design design.svg --preset hq --apply
plotty plot my_design --preset safe --apply

# Check status
plotty info system
```

### For Developers

```python
from plotty.fsm import create_fsm, JobState
from plotty.plotting import MultiPenPlotter
from plotty.config import get_config

# Create and manage jobs
config = get_config()
fsm = create_fsm("job_id", Path(config.workspace))

# Process job
if fsm.apply_optimizations(preset="hq", digest=1):
    if fsm.queue_ready_job():
        print("Job ready for plotting")
```

## 🏗️ Architecture Overview

ploTTY follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Core Logic     │    │ Database Layer  │
│                 │    │                 │    │                 │
│ • Typer CLI     │◄──►│ • FSM           │◄──►│ • SQLAlchemy    │
│ • Commands      │    │ • Planning      │    │ • Models        │
│ • Options       │    │ • Estimation    │    │ • Migrations    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Device Drivers  │    │ Configuration   │    │ Extensions      │
│                 │    │                 │    │                 │
│ • AxiDraw       │    │ • Pydantic      │    │ • Hooks         │
│ • Plotter Mgmt  │    │ • YAML Config   │    │ • Guards        │
│ • Multi-pen     │    │ • Validation    │    │ • Statistics    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 Job Lifecycle

All jobs progress through a well-defined state machine:

```
NEW → QUEUED → ANALYZED → OPTIMIZED → READY → ARMED → PLOTTING → COMPLETED
                     │                                       │
                     └─────────────────────→ FAILED ←────────┘
```

## 📊 Key Features

- **Finite State Machine**: Robust job lifecycle management
- **Multi-pen Support**: Advanced pen management and plotting
- **Configuration System**: Flexible YAML-based configuration
- **Database Backend**: SQLAlchemy models for persistence
- **CLI Interface**: Comprehensive command-line tools
- **Extensible Architecture**: Hooks, guards, and plugins
- **Statistics**: Comprehensive analytics and reporting
- **Recovery**: Automatic crash recovery and resume

## 🛠️ Integration Patterns

### Command Line Integration
```bash
# Direct CLI usage
plotty add job my_design design.svg --apply
plotty plot my_design --preset safe --apply
```

### Python Module Integration
```python
# Import ploTTY as a module
from plotty.fsm import create_fsm
from plotty.plotting import MultiPenPlotter

# Use ploTTY APIs
fsm = create_fsm("job_id", workspace)
plotter = MultiPenPlotter()
```

### Web API Integration
```python
# Build web services on top of ploTTY
from flask import Flask
from plotty.fsm import create_fsm

app = Flask(__name__)
@app.route('/api/jobs/<job_id>/plot')
def plot_job(job_id):
    fsm = create_fsm(job_id, workspace)
    # ... plotting logic
```

## 📋 Common Workflows

### 1. Basic Job Processing
```python
# Create job → Optimize → Queue → Plot
fsm = create_fsm(job_id, workspace)
fsm.apply_optimizations(preset="default", digest=1)
fsm.queue_ready_job()
# ... plotting logic
```

### 2. Batch Processing
```python
# Process multiple files
for svg_file in glob.glob("*.svg"):
    job_id = Path(svg_file).stem
    fsm = create_fsm(job_id, workspace)
    fsm.apply_optimizations(preset="fast", digest=1)
    fsm.queue_ready_job()
```

### 3. Custom Automation
```python
# File watcher integration
class PlotHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.svg'):
            process_svg_file(event.src_path)
```

## 🔍 Finding Information

### For CLI Users
- Start with [CLI API Reference](cli-reference.md)
- Check [Configuration Schema](configuration-schema.md) for setup options
- Review [Examples](examples-integration.md) for common workflows

### For Developers
- Begin with [Core Classes and Methods](core-classes.md)
- Understand [Job Lifecycle](job-lifecycle.md) for state management
- Review [Database Models](database-models.md) for data persistence
- Check [Integration Examples](examples-integration.md) for patterns

### For System Integrators
- Focus on [Configuration Schema](configuration-schema.md) for deployment
- Review [Database Models](database-models.md) for data integration
- Check [Examples and Integration](examples-integration.md) for web APIs

## 🧪 Testing and Development

### Running Tests
```bash
# Run all tests
uv run pytest -q

# Run specific test module
uv run pytest tests/test_fsm_unit.py -q

# Run with coverage
uv run pytest --cov=plotty tests/
```

### Development Setup
```bash
# Install development dependencies
uv pip install -e ".[dev,vpype,axidraw]"

# Set up pre-commit hooks
uvx pre-commit install && uvx pre-commit run -a

# Run linting and formatting
uvx ruff check .
uvx black .
```

## 📞 Getting Help

### Documentation
- This API documentation provides comprehensive coverage
- Check the [Examples and Integration](examples-integration.md) section for practical guidance
- Review the [Configuration Schema](configuration-schema.md) for setup options

### Community
- Check the ploTTY repository for issues and discussions
- Review test files for additional usage examples
- Examine the source code for detailed implementation information

### Troubleshooting
- Use `plotty check self` to verify installation
- Check `plotty info system` for system status
- Review logs in the configured log directory
- Use `--dry-run` options to preview operations

## 📈 Version Information

This documentation covers ploTTY version 1.2.0 and later. API compatibility is maintained within major versions, but always check the specific version documentation for any changes.

## 🔄 Continuous Updates

The ploTTY API is continuously evolving. This documentation is updated with each release to reflect:
- New commands and options
- Additional configuration settings
- Enhanced integration patterns
- Improved error handling and recovery

For the latest information, always refer to the version-specific documentation included with your ploTTY installation.

---

**Happy plotting with ploTTY!** 🎨✨