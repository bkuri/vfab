# ploTTY API Documentation

Welcome to the comprehensive API documentation for ploTTY, a powerful plotter management system. This documentation covers all aspects of the ploTTY API including CLI commands, database models, configuration, and programmatic interfaces.

## Table of Contents

- [Overview](#overview)
- [CLI API Reference](#cli-api-reference)
- [Database Models](#database-models)
- [Configuration Schema](#configuration-schema)
- [Core Classes and Methods](#core-classes-and-methods)
- [Job Lifecycle and States](#job-lifecycle-and-states)
- [Examples and Integration](#examples-and-integration)

## Overview

ploTTY is a Python-based plotter management system that provides:

- **Command Line Interface**: Complete CLI for job management, device control, and system administration
- **Database Backend**: SQLAlchemy-based models for pens, papers, jobs, and statistics
- **Finite State Machine**: Robust job lifecycle management with state transitions
- **Multi-pen Support**: Advanced pen management and plotting capabilities
- **Configuration System**: YAML-based configuration with Pydantic validation
- **Extensible Architecture**: Plugin system for guards, hooks, and custom functionality

The system is designed around a clear separation of concerns with well-defined APIs for each component.

## Quick Start

```bash
# Install ploTTY
uv pip install -e ".[dev,vpype]"

# Add a new job
plotty add job my_design design.svg --preset hq --apply

# List jobs
plotty list jobs

# Start plotting
plotty plot my_design --preset safe --apply

# Check system status
plotty info system
```

## Architecture

ploTTY follows a modular architecture:

```
ploTTY/
├── CLI Layer          # Typer-based command interface
├── Core Logic         # FSM, planning, estimation
├── Database Layer     # SQLAlchemy models and migrations
├── Device Drivers     # AxiDraw and plotter integration
├── Configuration      # Pydantic-based settings management
└── Extensions         # Guards, hooks, statistics
```

Each layer exposes well-defined APIs that can be used independently or together.