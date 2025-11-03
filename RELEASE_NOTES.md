# ploTTY v1.0.0 Release Notes

## 🎉 Initial Release: FSM Plotter Manager

**Release Date:** November 3, 2025  
**Version:** 1.0.0  
**Status:** Production Ready 🚀

---

## 📋 Overview

ploTTY is a headless-first finite state machine (FSM) plotter manager designed for professional plotting workflows. It provides comprehensive job management, device control, and analytics for AxiDraw and compatible plotters.

---

## ✨ Key Features

### 🏗️ Core Architecture
- **FSM Engine**: Complete finite state machine for reliable plotter job management
- **Cross-Platform**: XDG-compliant user data directories with platformdirs
- **System Installation**: Proper system-wide installation support

### 🎯 Device Support  
- **AxiDraw Integration**: Full support for v3, v4, SE/A3 models
- **Multipen System**: Automatic pen detection and switching
- **Simulation Mode**: Software-only plotting for testing

### 📊 Analytics & Statistics
- **Statistics Engine**: Database-driven analytics with O(log n) performance
- **CSV Export**: Hierarchical data export for all commands
- **Historical Tracking**: Job performance, success rates, and trends

### 🛠️ Job Management
- **Complete CLI**: Add, plan, list, remove, and monitor jobs
- **Batch Processing**: Queue and plot multiple jobs sequentially  
- **Interactive Control**: Real-time plotter control and pen testing
- **Guard System**: Pre-flight checks and validation

### 💾 Data Management
- **Backup System**: Complete backup and restore functionality
- **Recovery System**: Crash recovery and job state restoration
- **Hook System**: Configurable commands for state transitions

---

## 🚀 Installation

### From PyPI (when published)
```bash
pip install plotty
```

### From Source
```bash
git clone https://github.com/bkuri/plotty
cd plotty
uv pip install -e ".[dev,vpype]"
```

### AxiDraw Support
```bash
pip install pyaxidraw
```

---

## ⚡ Quick Start

```bash
# Run setup wizard
plotty setup

# Add a drawing
plotty job add drawing.svg

# Plan the job
plotty job plan drawing

# Plot the job  
plotty plot drawing

# View statistics
plotty stats summary
```

---

## 📁 User Data Structure

```
~/.local/share/plotty/
├── workspace/         # Jobs and plots
├── logs/             # Application logs
├── backups/          # User backups
└── plotty.db         # Database

~/.config/plotty/
└── config.yaml       # Configuration
```

---

## 🖥️ System Integration

### Arch Linux
```bash
# Build and install
makepkg -si
```

### Systemd Service
```bash
# Enable user service
systemctl --user enable --now plottyd
```

### Shell Completions
- **bash**: `/usr/share/bash-completion/completions/plotty`
- **zsh**: `/usr/share/zsh/site-functions/_plotty`  
- **fish**: `/usr/share/fish/vendor_completions.d/plotty.fish`

---

## 🧪 Testing

```bash
# Run test suite
uv run pytest

# Run with coverage
uv run pytest --cov=plotty
```

---

## 📚 Documentation

- **README.md**: Comprehensive usage guide
- **CHANGELOG.md**: Detailed version history  
- **docs/**: Implementation details and requirements
- **--help**: Built-in CLI help

---

## 🙏 Acknowledgments

- **AxiDraw**: Evil Mad Scientist Laboratories
- **VPype**: Antoine Beyeler  
- **Typer**: Sebastián Ramírez
- **Rich**: Will McGugan
- **SQLAlchemy**: Mike Bayer

---

## 🔮 Future Plans

- **TUI Interface**: Terminal user interface
- **Multi-Device**: Support for multiple plotters
- **Web Interface**: Browser-based management
- **Plugin System**: Extensible architecture
- **Cloud Sync**: Remote workspace synchronization

---

## 📋 Requirements

- **Python**: 3.11+
- **Dependencies**: See pyproject.toml
- **Optional**: pyaxidraw (AxiDraw), vpype (SVG processing)

---

**ploTTY v1.0.0** - Production-ready FSM plotter management 🎯