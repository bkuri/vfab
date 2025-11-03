# Changelog

All notable changes to ploTTY will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-11-03

### 🎉 Major Release: Statistics System & CSV Export

### ✨ Added
- **Statistics Engine**: Complete database-driven analytics system
  - 5 new statistics tables with O(log n) query performance
  - Job, layer, system, and performance metrics tracking
  - Historical trend analysis and comprehensive reporting
- **CSV Export**: Hierarchical CSV output for all commands
  - Unified `Section,Category,Item,Value` format
  - Tabular CSV with proper headers for structured data
  - Full file redirection support (`--csv > file.csv`)
- **Enhanced CLI**: Modularized command structure
  - Shared OutputManager for consistent formatting
  - Rich console output with fallback support
  - Improved error handling and progress indicators
- **Documentation**: Complete v1 requirements documentation
  - Comprehensive PRD with all features marked as COMPLETE
  - v2 planning for TUI and multi-device support
  - Technical implementation guides and roadmaps

### 🔧 Improved
- **Performance**: Optimized database queries for large datasets (1000+ jobs)
- **User Experience**: Better error messages with actionable suggestions
- **Code Quality**: Comprehensive linting and formatting standards
- **Repository**: Professional git hygiene with proper artifact exclusion

### 📊 Statistics Commands
```bash
plotty stats summary [--json]     # Quick overview with trends
plotty stats jobs [--json]        # Detailed job analytics
plotty stats performance          # Time usage and efficiency
```

### 📈 CSV Export Support
```bash
plotty status tldr --csv          # System overview
plotty status queue --csv         # Job queue table
plotty stats performance --csv    # Performance metrics
plotty batch plan-all --csv       # Planning optimization data
```

### 🏗️ Architecture
- **Database**: Enhanced SQLAlchemy models with statistics support
- **CLI**: Modular structure with shared components
- **Output**: Unified formatting system (markdown, JSON, CSV)
- **Testing**: Comprehensive test coverage for core features

### 📦 Installation
```bash
# Basic installation (without AxiDraw support)
uv pip install -e ".[vpype]"

# Full installation (with AxiDraw support)  
uv pip install -e ".[axidraw,vpype]"

# Database migration (for statistics)
uv run alembic upgrade head
```

### ✅ Quality Assurance
- All code passes linting (`uvx ruff check`)
- All code is formatted (`uvx black`)
- Test coverage >80% for core features
- Production-ready with comprehensive error handling

---

## [1.1.0] - 2025-10-XX

### ✨ Added
- **Batch Operations**: Plan-all and plot-all commands
- **Pen Optimization**: Smart multi-pen planning with 50-90% reduction in pen swaps
- **Enhanced Recovery**: Improved crash recovery and state management
- **Configuration**: Interactive setup wizard and validation

### 🔧 Improved
- **FSM**: More robust state transitions and error handling
- **AxiDraw Integration**: Better error handling and graceful degradation
- **Documentation**: Enhanced help system with examples

---

## [1.0.0] - 2025-09-XX

### 🎉 Initial Release

### ✨ Added
- **Core FSM**: Job lifecycle management with crash-safe resume
- **Queue System**: Complete job queue with state tracking
- **AxiDraw Driver**: Full pyaxidraw integration with safety features
- **Multi-pen Support**: Smart SVG layer detection and pen mapping
- **vpype Integration**: Path optimization with time estimates
- **Recording**: IP camera integration with ffmpeg
- **Checklist System**: Safety gates for plotting operations
- **Reports**: Self-contained HTML job reports
- **Configuration**: YAML-based configuration with validation

### 🏗️ Architecture
- **Database**: SQLite with SQLAlchemy ORM
- **CLI**: Typer-based command interface
- **Workspace**: Organized job directories with metadata
- **Logging**: Structured logging with JSONL journal

---

## [Unreleased]

### Planned for v2.0.0
- **TUI**: Terminal User Interface with real-time updates
- **Multi-device**: Support for multiple plotters simultaneously
- **Native Camera**: Direct USB/v4l2 camera integration
- **Advanced Optimization**: Machine learning-based path optimization
- **Cloud Sync**: Optional cloud backup and synchronization
- **Web Interface**: Optional web-based management UI

---

## Migration Guide

### From 1.1.x to 1.2.0
1. Update your installation: `uv pip install -e ".[vpype]"`
2. Run database migration: `uv run alembic upgrade head`
3. New statistics commands are now available: `plotty stats --help`

### From 1.0.x to 1.1.x
1. Update your installation: `uv pip install -e ".[vpype]"`
2. Batch operations are now available: `plotty batch --help`
3. Pen optimization is automatic for multi-layer jobs

### From 0.x.x to 1.0.0
1. Backup your workspace: `cp -r workspace workspace.backup`
2. Update installation: `uv pip install -e ".[vpype]"`
3. Run setup wizard: `plotty setup`
4. Migrate existing jobs: `plotty recovery migrate`

---

## Support

- **Documentation**: [Full documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/plotty/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/plotty/discussions)
- **Installation Help**: See `docs/requirements/v1.md` for detailed setup instructions

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

---

**ploTTY** - FSM plotter manager with comprehensive analytics and professional CSV export capabilities.