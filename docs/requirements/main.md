# ploTTY — Product Requirements Document (PRD)

**One-liner:** Headless-first, checklist-driven, FSM-based pen-plotter manager that queues, optimizes (vpype), and plots SVGs (AxiDraw first), with per-session recording and multi-pen (per-layer) support.

**Targets**
- **Users:** artists/makers/studios with one or more plotters (multi-device support planned for v2)
- **OS:** Linux (Arch first-class), macOS OK, Windows best-effort
- **Interfaces:** CLI + TUI + optional local JSON-RPC (no GUI deps)
- **Container:** Podman Quadlet (systemd-managed)
- **DB:** SQLite by default; pluggable via SQLAlchemy for Postgres/MySQL later

---

## 1) Goals (v1) / Non-Goals

**Goals**
- Deterministic **FSM** for job lifecycle with crash-safe resume.
- Queue → Analyze → Optimize(vpype) → Checklist → Arm → Plot → Report.
- **Pre & post** optimization time estimates (geom model + optional `pyaxidraw.report_time`).
- **Multi-pen**: smart SVG layer detection with color-coded overview, hidden layer filtering, and one pen per layer with gated swaps and per-layer metrics.
- **AxiDraw** driver (pyaxidraw) with graceful degradation, clear error messages, dry-run, pause/resume/abort, safe park.
- **Recording:** v1 consumes **IP video** (`http/rtsp`, e.g. `localhost:8881`); later native **USB/v4l2** with custom ffmpeg filters.
- **Headless** over SSH; systemd units + JSONL journal.
- **Reports:** self-contained HTML per job (metrics, thumbnails, links to MP4).

**Non-Goals (v1)**
- Cloud accounts/sync, multi-node orchestration, GUI, non-pen CNC/G-code.

---

## 2) User stories (acceptance, abbreviated)

1. **Queue SVG** → auto-detect dims; choose paper; **smart layer detection with color-coded overview**; map layers→pens → state `QUEUED`.
2. **Optimize** via vpype preset or custom pipe → see before/after stroke & length deltas.
3. **Checklist gates** (paper taped, origin set, pen test, webcam OK) block Start until all green.
4. **Plot** shows live ETA, current layer/pen; pause/resume/abort; prompt at layer boundaries.
5. **Record** starts on `PLOTTING`, stops on terminal; saves MP4 (+ optional timelapse).
6. **Recover** after crash/SSH drop: resume or safe abort with consistent journal.
7. **Report** shows pre/post estimates vs actual, per-layer metrics, diffs.

---

## 3) Architecture

CLI/TUI ──> Orchestrator (FSM) ──> Device Driver (v1: single device, v2: multi-device)
│
├─> vpype Runner (subprocess)
├─> Estimator (geom + pyaxidraw)
├─> Capture (ffmpeg: IP v1; v4l2 later)
└─> Persistence (SQLite + workspace FS + JSONL journal)

**FSM states:** `NEW → QUEUED → ANALYZED → OPTIMIZED → READY → ARMED → PLOTTING → (PAUSED) → COMPLETED | ABORTED | FAILED`  
**Guards:** device idle; checklist complete; camera health (soft-fail allowed).
**Hooks:** Per-state configurable actions (commands, scripts, webhooks) with variable substitution.

---

## 4) Data model (SQLite, via SQLAlchemy)
- `devices(id, kind, name, port, firmware, defaults_json, created_at, updated_at)`
- `pens(id, name, width_mm, speed_cap, pressure, passes, color_hex)`
- `papers(id, name, width_mm, height_mm, margin_mm, orientation)`
- `jobs(id, name, src_path, opt_path, paper_id, state, timings_json, metrics_json, media_json, created_at, updated_at)`
- `layers(id, job_id, layer_name, order_index, pen_id, stats_json, planned bool)`

Job folder:

```
workspace/jobs/<id>/
src.svg
layers/<n>.svg
optimized.svg
journal.jsonl
recording.mp4
timelapse.mp4 (opt)
report.html
logs/{fsm.log,device.log}
```

---

## 5) Estimation (pre/post)

**Features:** `L_down`, `L_travel`, `N_lifts`, `N_corners`  
**Model:** `T ≈ a*L_down + b*L_travel + c*N_lifts + d*N_corners` (coeffs per device+pen; auto-calibrated after each job).  
**Pre-opt:** approximate travel via nearest-neighbor; **Post-opt:** exact from optimized paths.  
Optional **`pyaxidraw.report_time`** (post-opt); store method + error band.
Persist `pre`, `post`, and `actual` in `jobs.metrics_json` and per-layer `layers.stats_json`.

---

## 6) vpype integration

- **Preset registry** (YAML) with placeholders `{src}`, `{dst}`, `{paper_w}`, `{paper_h}`, `{margin}`.
- Per-layer processing for multi-pen (or one combined run retaining layers).
- Diff metrics: segments, total lengths, lifts, estimated time saved (%).

---

## 7) Device layer

- **AxiDraw (v1):** pyaxidraw wrapper; mm/s, accel, pen up/down heights; dry-run renderer.
- **Controls:** home, pen up/down, safe park, plot SVG, pause/resume/abort.
- **Future:** HPGL serial, custom HID/USB, REST.

---

## 8) Webcam & recording

- **v1:** **IP feed** (`http(s)`/`rtsp`, e.g. `http://127.0.0.1:8881/stream.mjpeg`) → ffmpeg `recording.mp4`; optional timelapse (`fps=1`).
- **v1.1:** native **v4l2 (USB)** with custom ffmpeg chain: perspective/color/hqdn3d; device health checks at `ARMED`.
- Start/stop bound to FSM; on errors continue plotting, flag `camera_unavailable`.
- **Hooks execution** on state transitions with variable substitution (`{job_id}`, `{job_path}`, `{state}`, `{error}`).

**Config**
```yaml
camera:
  mode: ip            # 'ip' (v1) or 'v4l2' (v1.1)
  url: "http://127.0.0.1:8881/stream.mjpeg"
  device: "/dev/video0"
  enabled: true
  timelapse_fps: 1
  ffmpeg_filters: ""  # used in v4l2 mode

hooks:
  NEW:
    - command: "notify-send 'Job queued: {job_id}'"
  QUEUED:
    - script: "/usr/local/bin/pre-process.sh {job_path}"
  ANALYZED:
    - command: "python analyze_layers.py {job_id}"
  OPTIMIZED:
    - webhook: "http://monitoring.local/optimized"
  READY:
    - script: "checklist_reminder.sh {job_id}"
  ARMED:
    - command: "ffmpeg-start-recording {job_id}"
  PLOTTING:
    - command: "update-status-led plotting"
  PAUSED:
    - command: "notify-send 'Plot paused - {job_id}'"
  COMPLETED:
    - command: "generate-report.sh {job_id}"
    - webhook: "http://archive.local/completed"
  ABORTED:
    - command: "cleanup-failed.sh {job_id}"
  FAILED:
    - command: "alert-admin.sh {job_id} {error}"
```

---

## 9) Headless runtime & ops

- CLI (plotty) + daemon (plottyd) with local JSON-RPC; logs to stdout + JSONL.
- Systemd services (user/system) and Podman Quadlet container.
- Permissions (Arch): service user in uucp (USB) and video (v4l2).
- Safety: SIGINT/SIGTERM → pen up, park, stop recording, mark ABORTED.

Quadlet (v1, IP camera):

```ini
[Container]
Image=ghcr.io/yourorg/plotty:latest
Network=host
Volume=%h/plotty/workspace:/var/lib/plotty:Z
Volume=%h/.config/plotty:/etc/plotty:Z
Environment=PLOTTY_CONFIG=/etc/plotty/config.yaml
Exec=plottyd --workspace /var/lib/plotty --rpc :8765
# For native USB/v4l later:
# Device=/dev/ttyUSB0
# Device=/dev/video0
```

---

## 10) Multi-pen (per-layer)

- Parse SVG layer names/order; auto-detect multi-pen requirements from SVG structure and AxiDraw layer control syntax.
- At layer boundary: lift, park, prompt to swap pen (CLI + ntfy/MQTT; TUI v1.1), optional ink swatch.
- Store per-layer metrics & estimates; show per-layer ETAs during run.

```sh
plotty job layers <job>
plotty job map-pen <job> --layer "Hatch" --pen "0.4mm red"
plotty job plan <job> --json
```

## 10.1) Smart Multipen Detection (v1)

- **Automatic Detection:** Parse SVG for multiple layers OR AxiDraw layer control syntax (`+S`, `+H`, `+D`, `!`, `%`)
- **Hidden Layer Filtering:** Skip layers marked with `%` (documentation-only) in AxiDraw layer control syntax
- **Fallback Logic:** Single-layer SVGs use single-pen mode; multi-layer or control-syntax SVGs use multipen mode
- **No Manual Flags:** Remove requirement for explicit `--multipen` flag; auto-detect from job content
- **Layer Control Support:** Full support for [AxiDraw Layer Control](https://wiki.evilmadscientist.com/AxiDraw_Layer_Control) syntax including:
  - `+S<1-100>`: Set pen speed percentage
  - `+H<0-100>`: Set pen height (up/down) percentage  
  - `+D<1+>`: Set delay in milliseconds after layer
  - `!`: Force pause after layer (pen swap)
  - `%`: Documentation layer (skip plotting)

---

## 11) Checklists (gates)

Default required (toggleable): paper size/orientation; paper taped & square; pen loaded + ink test; origin set; surface clearance; webcam OK (soft-fail).

---

## 12) API surface (JSON-RPC/HTTP)

- `POST /jobs (src, paper, pen map) → job id`
- `POST /jobs/{id}/optimize (preset|pipe)`
- `POST /jobs/{id}/estimate?stage=pre|post`
- `POST /jobs/{id}/checklist (item=true)`
- `POST /jobs/{id}/start|pause|resume|abort`
- `GET /jobs/{id} (state, metrics, layers, media)`
- `POST /calibrate (device, pen, features, actual_s)`
- `GET /hooks` (list configured hooks)
- `POST /hooks/test` (test hook execution)

---

## 13) Non-functional

Reliability (idempotent resume, fsync journal), latency (pause/abort <500 ms), throughput (10+ queued), observability (structured logs), security (local-only by default).

---

## 14) Packaging & deps

- Runtime: Python 3.10+; pyaxidraw, vpype, sqlalchemy, alembic, pydantic, typer, jinja2, ffmpeg.
- DB drivers: SQLite baked-in; extras later (psycopg, mysqlclient).
- Container: slim + ffmpeg; optional USB/v4l devices via Quadlet.

Quick add:

---

## 8) Implementation Status

### ✅ Completed (v1)

**Core FSM & Job Management**
- [x] FSM-based job lifecycle with crash-safe resume
- [x] Queue → Analyze → Optimize → Checklist → Plot → Report flow
- [x] SQLite persistence with JSONL journal
- [x] Workspace management with job directories

**Smart Multipen Detection** 
- [x] SVG layer detection with Inkscape compatibility
- [x] Color-coded layer overview with element counts
- [x] Hidden layer filtering (display:none, groupmode="hidden", % documentation)
- [x] Interactive pen mapping with database integration
- [x] Automatic single-pen vs multi-pen mode selection

**AxiDraw Integration**
- [x] Robust pyaxidraw import handling with graceful degradation
- [x] Clear error messages and installation instructions
- [x] Optional dependency management (axicli package metadata fix)
- [x] Dry-run, pause/resume/abort, safe park functionality
- [x] Time estimation with vpype optimization

**CLI & Planning**
- [x] Complete CLI interface with all required commands
- [x] vpype integration for path optimization
- [x] Pre/post optimization time estimates
- [x] Paper and pen database management
- [x] Checklist-driven safety gates

**Recording & Reporting**
- [x] IP camera integration (v1)
- [x] Per-session MP4 recording with ffmpeg
- [x] Self-contained HTML job reports
- [x] Metrics, thumbnails, and video links

### 🚧 In Progress

**TUI (Terminal User Interface)**
- [ ] Textual-based interactive interface
- [ ] Real-time plotting progress visualization
- [ ] Device health monitoring
- [ ] Job queue management
- [ ] Session management with FSM state display

### 🚧 In Progress (v1 UX Enhancement)

**Tier 1 Features (Week 1)**
- [ ] Quick status commands (status, queue, job info)
- [ ] Enhanced error messages with suggestions
- [ ] Progress indicators for long operations

**Tier 2 Features (Week 2)**
- [ ] Job management shortcuts (cancel, retry, duplicate)
- [ ] One-command setup wizard
- [ ] Configuration validation and auto-fix

**Tier 3 Features (Week 3-4)**
- [ ] Quick plot presets (fast, safe, preview)
- [ ] Usage statistics and analytics
- [ ] Batch operations (plan-all, plot-all)
- [ ] Enhanced help system with examples

### 📋 Deferred (v2)

**Multi-Device Support**
- [ ] Multiple plotter management
- [ ] Device pooling and load balancing
- [ ] Cross-device job orchestration

**Native Camera Support**
- [ ] USB/v4l2 camera integration
- [ ] Custom ffmpeg filters
- [ ] Hardware-accelerated encoding

---

## 15) v1 UX Enhancement Strategy

### **15.1) Easy Wins for v1**

Based on current codebase analysis (146K lines, 80% core functionality complete), the following high-impact, low-effort features are identified for v1:

#### **Tier 1 (Must Have - Week 1)**
1. **Quick Status Commands** - `plotty status`, `plotty queue`, `plotty job <id>`
   - **Impact**: 10x UX improvement - no need to launch dashboard for quick checks
   - **Effort**: 1-2 hours (reuse existing dashboard functions)

2. **Better Error Messages** - User-friendly error handling with suggestions
   - **Impact**: Dramatically better user experience, reduced support burden
   - **Effort**: 2-3 hours (centralized error system)

3. **Progress Indicators** - Progress bars for long operations (planning, optimization)
   - **Impact**: User feedback during operations, perceived performance improvement
   - **Effort**: 2-3 hours (tqdm integration)

#### **Tier 2 (Should Have - Week 2)**
4. **Job Management Shortcuts** - `plotty cancel <id>`, `plotty retry <id>`, `plotty duplicate <id>`
   - **Impact**: Common workflow operations currently missing
   - **Effort**: 2-3 hours (FSM state management)

5. **One-Command Setup** - `plotty setup` interactive first-time configuration
   - **Impact**: Removes friction for new users, improves onboarding
   - **Effort**: 1-2 hours (wizard implementation)

6. **Config Validation** - `plotty config-check`, `plotty config-fix`
   - **Impact**: Prevents runtime errors from bad configuration
   - **Effort**: 1-2 hours (validation rules)

#### **Tier 3 (Nice to Have - Week 3-4)**
7. **Quick Plot Presets** - `--fast`, `--safe`, `--preview` options
   - **Impact**: Power user features for different scenarios
   - **Effort**: 1 hour (preset configurations)

8. **Quick Stats** - `plotty stats` usage analytics
   - **Impact**: Helps users understand their usage patterns
   - **Effort**: 1 hour (database queries)

9. **Batch Operations** - `plotty plan-all`, `plotty plot-all`, `plotty clear-queue`
   - **Impact**: Power user workflow automation
   - **Effort**: 2-3 hours (loop operations)

10. **Better Help System** - `plotty help <command>`, `plotty examples`
   - **Impact**: Better feature discoverability
   - **Effort**: 1 hour (help organization)

### **15.2) Implementation Strategy**

#### **Phase 1: Foundation (Week 1)**
- **CLI Infrastructure**: Extend `src/plotty/cli.py` with new command groups
- **Error Enhancement**: Create `src/plotty/utils.py` with centralized error handling
- **Progress System**: Add `src/plotty/progress.py` for progress indicators
- **Status Commands**: Reuse existing `dashboard.py` functions for CLI exposure

#### **Phase 2: Core Features (Week 2)**
- **Job Management**: Extend FSM with job manipulation commands
- **Setup Wizard**: Interactive configuration with device detection
- **Config Validation**: Add validation rules to `src/plotty/config.py`

#### **Phase 3: Power Features (Week 3-4)**
- **Plot Presets**: Add preset options to existing plot command
- **Batch Operations**: Loop-based job processing
- **Stats & Help**: Database analytics and help system improvements

#### **New Files Structure**:
```
src/plotty/
├── utils.py              # Error handling, progress bars
├── cli_status.py        # Status/queue commands  
├── cli_jobs.py          # Job management commands
├── cli_setup.py        # Setup wizard
└── progress.py          # Progress indicator utilities
```

### **15.3) Success Metrics**

#### **User Experience Goals**
- **Time to first plot**: < 5 minutes (including setup)
- **Common operations**: < 10 seconds (status, queue, job info)
- **Error recovery**: Clear guidance for 90% of errors

#### **Technical Goals**
- **Test coverage**: > 80% for new features
- **CLI response time**: < 2 seconds for all commands
- **Backward compatibility**: 100% (no breaking changes)

#### **Feature Completeness**
- **Tier 1 features**: 100% complete
- **Tier 2 features**: 80% complete  
- **Tier 3 features**: 50% complete

### **15.4) Go/No-Go Criteria**

#### **Go Conditions for v1 Release**
- All Tier 1 features working and tested
- Core tests passing (>80% coverage)
- No breaking changes to existing workflows
- Documentation updated with new commands
- Performance regression < 20%

#### **No-Go Conditions**
- Breaking changes to existing workflows
- Critical bugs in core functionality
- Performance regression > 20%
- Incomplete error handling for new features

---

## 9) Development Workflow

```bash
mkdir -p docs
$EDITOR docs/PRD.md
git add docs/PRD.md && git commit -m "docs: add PRD for ploTTY v1" && git push
```
