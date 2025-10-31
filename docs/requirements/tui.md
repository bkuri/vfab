# ploTTY TUI (Terminal User Interface) Requirements

**One-liner:** Interactive terminal interface for ploTTY that provides real-time session management, device monitoring, and job control while preserving CLI-first architecture.

**Targets**
- **Users:** ploTTY users who prefer interactive terminal interfaces over pure CLI
- **OS:** Linux (primary), macOS, Windows where Textual is supported
- **Interface:** Textual-based TUI as optional layer over existing CLI
- **Integration:** Connects to existing ploTTY backend systems (plotting, paper, guards, FSM)

---

## 1) Goals / Non-Goals

**Goals**
- Provide interactive terminal interface for ploTTY operations
- Real-time visualization of plotting progress with layer-by-layer feedback and color-coded layer display
- Device health monitoring and status display
- Job queue management with visual feedback
- Session management with FSM state visualization
- Integration with existing ploTTY backend systems
- Preserve all existing CLI functionality

**Non-Goals**
- Replace existing CLI interface
- GUI or web interface
- Remote access (beyond existing SSH/JSON-RPC)
- Multi-node orchestration
- Multi-device support (deferred to v2)

---

## 2) User Stories

1. **Launch TUI** → User runs `plotty --tui` to enter interactive mode
2. **View Devices** → See connected plotter status and health metrics (v1: single device)
3. **Manage Jobs** → Browse, queue, and control plotting jobs interactively
4. **Monitor Progress** → Real-time layer-by-layer progress visualization with ETA and color-coded layer indicators
5. **Control Sessions** → Start, pause, resume, abort plotting sessions
6. **View Guards** → See paper session and pen layer guard status
7. **Device Health** → Monitor plotter health metrics (v1: single device)
8. **Job Selection** → Interactive job browsing and selection for plotting

---

## 3) Integration Architecture

```
CLI (plotty) ──> TUI (Textual App) ──> Existing Backend Systems
                    │
                    ├─> plotting.py (MultiPenPlotter, timing)
                    ├─> paper.py (PaperManager, PaperSessionGuard)
                    ├─> guards.py (PenLayerGuard)
                    ├─> fsm.py (PlotterFSM)
                    ├─> config.py (load_config)
                    ├─> db.py (job/device/pen/paper data)
                    └─> cli.py (existing commands)
```

**Key Integration Points:**
- **Timer Integration:** Connect TUI session display to existing `plotting.py` timing
- **Job Management:** Use existing workspace job system and database
- **Device Control:** Integrate with existing AxiDraw manager (v1: single device)
- **State Management:** Connect to existing FSM states and transitions
- **Guard System:** Display paper session and pen layer guard status

---

## 4) TUI Components

### 4.1 Main Application
```python
class PlottyTUI(App):
    """ploTTY Terminal User Interface"""
    
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("p", "plot_job", "Plot Job"), 
        ("s", "stop_plot", "Stop Plot"),
        ("r", "reset_session", "Reset Session"),
        ("c", "check_guards", "Check Guards"),
        ("j", "select_job", "Select Job"),
        ("a", "add_job", "Add Job"),
        ("f5", "refresh", "Refresh")
    ]
```

### 4.2 Core Widgets
- **SessionWidget:** Enhanced stopwatch with plot-specific metrics
- **JobQueue:** DataTable for job management and selection
- **DeviceStatus:** Single device status and health metrics
- **LayerProgressBar:** Visual layer-by-layer progress
- **DeviceHealthWidget:** Health monitoring with gauges
- **GuardStatusWidget:** Paper and pen guard status display

### 4.3 Layout Structure
```
Header (ploTTY TUI)
├─ Main Container (Horizontal)
│  ├─ Sessions Panel (2fr)
│  │  ├─ Active Sessions Header
│  │  └─ Sessions Scroll (SessionWidgets)
│  └─ Info Panel (1fr)
│     ├─ Job Queue Widget
│     ├─ Device Status Widget
│     └─ System Health Widget
└─ Footer (keyboard shortcuts)
```

---

## 5) Backend Integration Requirements

### 5.1 Timer Integration
- Connect TUI `SessionDisplay` to existing `plotting.py` timing functionality
- Preserve existing timing data and metrics
- Provide real-time updates during plotting

### 5.2 Job Management
- Use existing workspace job system (`workspace/jobs/`)
- Connect to database job records
- Support job selection and queuing
- Display job metadata and planning results

### 5.3 Device Integration
- Connect to existing `axidraw_integration.py` with graceful degradation
- Use existing device manager and connection handling
- Display real device status and health (with availability indicators)
- Support device control through TUI (clear error messages when unavailable)
- Integrate with smart multipen detection system

### 5.4 Guard System Integration
- Display `PaperSessionGuard` status and session tracking
- Show `PenLayerGuard` status and pen swap requirements
- Visual guard status indicators
- Support guard override options (display-only initially)

### 5.5 FSM Integration
- Display current FSM states for all active sessions
- Show state transitions in real-time
- Support state-based button visibility and actions
- Connect to existing crash recovery system

---

## 6) Implementation Phases

### Phase 1: Foundation (High Priority)
1. **Add Textual dependency** to `pyproject.toml`
2. **Create integrated TUI module** at `src/plotty/tui.py`
3. **Add TUI CLI command** with `--tui` flag launch
4. **Basic backend connections** to config and job systems

### Phase 2: Core Integration (Medium Priority)
5. **Timer integration** with existing `plotting.py` timing
6. **Job management** connection to workspace and database
7. **Device control** integration with axidraw manager
8. **FSM state** display and management

### Phase 3: Enhancement (Low Priority)
9. **Guard system** display and integration
10. **Device health** monitoring and real-time updates
11. **Advanced features** (layer progress, pen swap visualization)
12. **Testing** and validation of integrated systems

---

## 7) Technical Specifications

### 7.1 Dependencies
```toml
[project.optional-dependencies]
tui = ["textual>=0.44.0"]
```

### 7.2 CLI Integration
```python
@app.command()
def tui():
    """Launch ploTTY Terminal User Interface."""
    from .tui import PlottyTUI
    app = PlottyTUI()
    app.run()
```

### 7.3 Key Integration Points
```python
# Backend connections in src/plotty/tui.py
from .plotting import MultiPenPlotter
from .paper import PaperManager, PaperSessionGuard  
from .guards import PenLayerGuard
from .fsm import PlotterFSM
from .config import load_config
from .db import get_session
```

---

## 8) Design Decisions

### 8.1 TUI Mode Approach
**Decision:** CLI-first with optional `--tui` flag
- Preserves existing CLI functionality
- TUI as supplemental interface layer
- Maintains headless operation capability

### 8.2 Timer Integration
**Decision:** Supplemental to existing timing
- TUI timer displays existing timing data
- Preserves current timing architecture
- Adds visualization without replacement

### 8.3 Job Management
**Decision:** TUI selection with CLI backend
- TUI provides interactive job browsing
- Uses existing job system and workspace
- Supports both TUI and CLI job arguments

### 8.4 Guard Interaction
**Decision:** Display-only initially
- Shows guard status and requirements
- No override capabilities in v1
- Preserves guard system integrity

---

## 5) Multipen Detection Integration

### 5.1 Smart Detection Logic
- **Layer Analysis:** Parse SVG for Inkscape layers, groups, or AxiDraw layer control syntax
- **Hidden Layer Filtering:** Automatically skip layers marked with `%` (documentation-only) prefix
- **Automatic Mode Selection:** Single-pen for simple SVGs, multipen for complex/labeled SVGs
- **Control Syntax Support:** Full parsing of `+S` (speed), `+H` (height), `+D` (delay), `!` (pause), `%` (documentation) markers

### 5.2 Integration Points
- **CLI Integration:** Remove `--multipen` flag requirement; auto-detect in `plot` command
- **TUI Integration:** Display detected pen requirements and layer mappings
- **Backend Integration:** Connect to existing `multipen.py` detection logic
- **Layer Filtering:** Respect AxiDraw layer control syntax for skipping documentation layers

### 5.3 Detection Algorithm
```python
def should_use_multipen(job_dir: Path, plan_data: Dict) -> bool:
    """Auto-detect if multipen plotting should be used."""
    
    # Check 1: Multiple layers detected
    if plan_data.get("layer_count", 0) > 1:
        return True
    
    # Check 2: AxiDraw layer control syntax in SVG
    src_svg = job_dir / "src.svg"
    if src_svg.exists():
        layers = detect_svg_layers(src_svg)
        plotable_layers = []
        
        for layer in layers:
            control = parse_axidraw_layer_control(layer.name)
            # Skip documentation layers
            if not control.documentation_only:
                plotable_layers.append(layer)
                
        # Use multipen if multiple plotable layers or layer control syntax found
        if len(plotable_layers) > 1 or any(
            parse_axidraw_layer_control(l.name).layer_number is not None 
            for l in plotable_layers
        ):
            return True
    
    return False
```

---

## 9) Success Criteria

### 9.1 Functional Requirements
- [ ] TUI launches with `plotty --tui`
- [ ] Displays connected device status (v1: single device)
- [ ] Shows job queue and allows selection
- [ ] Provides real-time plotting progress
- [ ] Integrates with existing timing system
- [ ] Displays FSM states and transitions
- [ ] Shows guard system status
- [ ] Auto-detects multipen requirements from SVG content
- [ ] Filters hidden/documentation layers according to AxiDraw layer control syntax

### 9.2 Integration Requirements
- [ ] Connects to existing backend systems
- [ ] Preserves all CLI functionality
- [ ] Uses existing job and device management (v1: single device)
- [ ] Integrates with paper and guard systems
- [ ] Maintains database consistency
- [ ] Implements smart multipen detection without manual flags
- [ ] Respects AxiDraw layer control syntax for hidden layers

### 9.3 User Experience
- [ ] Responsive keyboard controls
- [ ] Clear visual feedback
- [ ] Intuitive navigation
- [ ] Real-time updates
- [ ] Error handling and recovery

---

## 10) Existing Assets

### 10.1 TUI Prototypes (Already Built)
- `src/textual/plotty_tui_demo.py` (641 lines) - Complete demonstration
- `src/textual/plotty_tui_standalone.py` - Simplified version
- `src/textual/plotty_tui_integrated.py` - Backend integration example

### 10.2 Backend Systems (Ready for Integration)
- `src/plotty/plotting.py` - Multi-pen plotting and timing
- `src/plotty/paper.py` - Paper management and guards
- `src/plotty/guards.py` - Pen layer guards
- `src/plotty/fsm.py` - Plotter FSM
- `src/plotty/cli.py` - Existing CLI commands
- `src/plotty/db.py` - Database models

### 10.3 What's Ready
- Complete TUI interface with CSS styling
- Session management and progress tracking
- Device health monitoring widgets
- Job queue management
- Keyboard bindings and navigation
- Real-time simulation capabilities

---

## 10) Implementation Phases

### Phase 1: Foundation (High Priority)
1. **Add Textual dependency** to `pyproject.toml`
2. **Create integrated TUI module** at `src/plotty/tui.py`
3. **Add TUI CLI command** with `--tui` flag launch
4. **Basic backend connections** to config and job systems

### Phase 2: Core Integration (Medium Priority)
5. **Smart multipen detection** - Remove `--multipen` flag requirement
6. **Timer integration** with existing `plotting.py` timing
7. **Job management** connection to workspace and database
8. **FSM state** display and management

### Phase 3: Enhancement (Low Priority)
9. **Guard system** display and integration
10. **Device health** monitoring and real-time updates
11. **Advanced features** (layer progress, pen swap visualization)
12. **Testing** and validation of integrated systems

### Deferred to v2: Multi-Device Support
- Device discovery and management
- Concurrent plotting on multiple devices
- Device assignment and load balancing
- Multi-device health monitoring

---

## 11) Existing Assets

### 11.1 TUI Prototypes (Already Built)
- `src/textual/plotty_tui_demo.py` (641 lines) - Complete demonstration
- `src/textual/plotty_tui_standalone.py` - Simplified version
- `src/textual/plotty_tui_integrated.py` - Backend integration example

### 11.2 Backend Systems (Ready for Integration)
- `src/plotty/plotting.py` - Multi-pen plotting and timing
- `src/plotty/paper.py` - Paper management and guards
- `src/plotty/guards.py` - Pen layer guards
- `src/plotty/fsm.py` - Plotter FSM
- `src/plotty/cli.py` - Existing CLI commands
- `src/plotty/db.py` - Database models

### 11.3 What's Ready
- Complete TUI interface with CSS styling
- Session management and progress tracking
- Device health monitoring widgets
- Job queue management
- Keyboard bindings and navigation
- Real-time simulation capabilities

---

## 12) Next Steps

1. **Foundation:** Add Textual dependency and create TUI module
2. **Integration:** Connect to existing backend systems
3. **Smart Detection:** Implement automatic multipen detection with hidden layer filtering
4. **Testing:** Validate integration with existing CLI commands
5. **Enhancement:** Add advanced features and optimizations
6. **Documentation:** Update user guides and examples

---

## 7) Implementation Status

### ✅ Backend Foundation (COMPLETED)

**Smart Multipen Detection System**
- [x] SVG layer detection with Inkscape compatibility
- [x] Color-coded layer overview with element counts  
- [x] Hidden layer filtering (display:none, groupmode="hidden", % documentation)
- [x] Interactive pen mapping with database integration
- [x] Automatic single-pen vs multi-pen mode selection

**AxiDraw Integration**
- [x] Robust pyaxidraw import handling with graceful degradation
- [x] Clear error messages and installation instructions  
- [x] Optional dependency management (axicli package metadata fix)
- [x] Time estimation with vpype optimization

**CLI & Planning Systems**
- [x] Complete CLI interface with all required commands
- [x] vpype integration for path optimization
- [x] Paper and pen database management
- [x] Checklist-driven safety gates

### 🚧 TUI Implementation (IN PROGRESS)

**Core TUI Framework**
- [x] Textual dependency management
- [x] Basic TUI application structure
- [x] Layout system (header, main, footer)
- [x] Widget foundation classes

**Backend Integration Needed**
- [ ] Connect TUI to existing plotting systems
- [ ] Real-time progress visualization
- [ ] Device status monitoring
- [ ] Job queue management interface
- [ ] Session control integration

### 📋 Implementation Notes

The extensive TUI prototyping work means most interface components are already designed. The smart multipen detection system is **fully implemented** in the backend, so TUI integration primarily involves:

1. **Connecting existing widgets** to live backend data
2. **Implementing real-time updates** for plotting progress
3. **Adding device monitoring** with availability indicators
4. **Integrating session management** with FSM state display

The heavy lifting (layer detection, pen mapping, AxiDraw integration) is complete - TUI work is primarily about visualization and control interfaces to the existing systems.