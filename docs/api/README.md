# vfab API Documentation

Welcome to the comprehensive API documentation for vfab, a powerful plotter management system. This documentation covers all aspects of the vfab API including CLI commands, database models, configuration, and programmatic interfaces.

## Table of Contents

- [Overview](#overview)
- [CLI API Reference](#cli-api-reference)
- [Driver Development](#driver-development)
- [Database Models](#database-models)
- [Configuration Schema](#configuration-schema)
- [Core Classes and Methods](#core-classes-and-methods)
- [Job Lifecycle and States](#job-lifecycle-and-states)
- [Examples and Integration](#examples-and-integration)

## Overview

vfab is a Python-based plotter management system that provides:

- **Command Line Interface**: Complete CLI for job management, device control, and system administration
- **Database Backend**: SQLAlchemy-based models for pens, papers, jobs, and statistics
- **Finite State Machine**: Robust job lifecycle management with state transitions
- **Multi-pen Support**: Advanced pen management and plotting capabilities
- **Configuration System**: YAML-based configuration with Pydantic validation
- **Extensible Architecture**: Plugin system for guards, hooks, and custom functionality

The system is designed around a clear separation of concerns with well-defined APIs for each component.

## Driver Development

For developers looking to add new hardware drivers to vfab, see:

- **[Driver Development Guide](../driver/development.md)** - Step-by-step instructions for adding new drivers
- **[Driver Architecture](../driver/architecture.md)** - System architecture and design patterns
- **[Driver Requirements](../requirements/drivers.md)** - Strategic roadmap and implementation milestones

### Quick Driver Examples

```bash
# List available drivers
vfab driver list

# Install AxiDraw support
vfab driver install axidraw

# Check driver status
vfab driver info axidraw --verbose

# Test driver functionality
vfab driver test axidraw --cycles 3
```

## Quick Start

```bash
# Install vfab
uv pip install -e ".[dev,vpype]"

# Add a new job
vfab add job my_design design.svg --preset hq --apply

# List jobs
vfab list jobs

# Start plotting
vfab plot my_design --preset safe --apply

# Check system status
vfab info system
```

## Architecture

vfab follows a modular architecture:

```
vfab/
├── CLI Layer          # Typer-based command interface
├── Core Logic         # FSM, planning, estimation
├── Database Layer     # SQLAlchemy models and migrations
├── Device Drivers     # AxiDraw and plotter integration
├── Configuration      # Pydantic-based settings management
└── Extensions         # Guards, hooks, statistics
```

Each layer exposes well-defined APIs that can be used independently or together.