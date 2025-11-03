# Changelog

All notable changes to ploTTY will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-03

### 🎉 Initial Release: FSM Plotter Manager

### ✨ Core Features
- **FSM Architecture**: Complete finite state machine for plotter job management
- **Job Management**: Add, plan, list, remove, and monitor plotting jobs
- **Device Support**: AxiDraw integration with multipen detection and switching
- **Batch Processing**: Queue and plot multiple jobs sequentially
- **Interactive Control**: Real-time plotter control and pen testing
- **Statistics Engine**: Comprehensive analytics with database-driven metrics
- **CSV Export**: Hierarchical data export for all commands
- **Backup System**: Complete backup and restore functionality
- **Guard System**: Pre-flight checks and validation
- **Hook System**: Configurable commands for state transitions
- **Recovery System**: Crash recovery and job state restoration

### 🏠 Architecture
- **User Data Structure**: XDG-compliant directory layout
  - Workspace: `~/.local/share/plotty/workspace/`
  - Database: `~/.local/share/plotty/plotty.db`
  - Logs: `~/.local/share/plotty/logs/`
  - Backups: `~/.local/share/plotty/backups/`
- **Cross-Platform**: platformdirs integration for Windows/macOS/Linux
- **System Installation**: Proper system-wide installation support

### 🛠️ Development
- **CLI Framework**: Typer-based command-line interface
- **Database**: SQLAlchemy with Alembic migrations
- **Configuration**: YAML-based with Pydantic validation
- **Logging**: Rich-formatted logging with multiple levels
- **Testing**: Comprehensive pytest test suite
- **CI/CD**: GitHub Actions with multi-Python testing

### 📦 Packaging
- **Arch Linux**: PKGBUILD with proper dependencies
- **Systemd**: User service for daemon operation
- **Quadlet**: Container definition for podman
- **Shell Completions**: bash, zsh, and fish support

### 🎯 Supported Devices
- **AxiDraw**: v3, v4, SE/A3 with multipen support
- **Simulation**: Software-only plotting mode
- **Extensible**: Driver system for new plotter types

### 📊 Statistics & Analytics
- **Job Metrics**: Duration, success rate, error tracking
- **Layer Analysis**: Per-layer plotting statistics
- **Performance**: System resource monitoring
- **Historical**: Trend analysis and reporting
- **Export**: CSV format for external analysis

### 🔧 Configuration
- **Paper Management**: Size, margin, orientation settings
- **Device Settings**: Speed, pen positions, calibration
- **Camera Integration**: IP camera with timelapse support
- **Hook Configuration**: Custom commands for events
- **VPype Integration**: SVG optimization and processing

### 🚀 Installation
```bash
# From PyPI (when published)
pip install plotty

# From source
uv pip install -e ".[dev,vpype]"

# AxiDraw support
pip install pyaxidraw
```

### 📖 Quick Start
```bash
plotty setup                    # Run setup wizard
plotty job add drawing.svg      # Add a job
plotty job plan drawing        # Plan the job
plotty plot drawing            # Plot the job
plotty stats summary           # View statistics
```

### 🙏 Acknowledgments
- **AxiDraw**: Evil Mad Scientist Laboratories
- **VPype**: Antoine Beyeler
- **Typer**: Sebastián Ramírez
- **Rich**: Will McGugan
- **SQLAlchemy**: Mike Bayer

---

## [Unreleased]

### Future Plans
- **TUI Interface**: Terminal user interface for job management
- **Multi-Device**: Support for multiple plotters simultaneously
- **Web Interface**: Browser-based management dashboard
- **Plugin System**: Extensible architecture for custom features
- **Cloud Sync**: Remote workspace synchronization
- **Mobile App**: Job monitoring and control from mobile devices