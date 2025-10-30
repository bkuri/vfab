# ploTTY — Product Requirements Document (PRD)

**One-liner:** Headless-first, checklist-driven, FSM-based pen-plotter manager that queues, optimizes (vpype), and plots SVGs (AxiDraw first), with per-session recording and multi-pen (per-layer) support.

**Targets**
- **Users:** artists/makers/studios with one or more plotters
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
- **Multi-pen**: one pen per SVG layer with gated swaps and per-layer metrics.
- **AxiDraw** driver (pyaxidraw) with dry-run, pause/resume/abort, safe park.
- **Recording:** v1 consumes **IP video** (`http/rtsp`, e.g. `localhost:8881`); later native **USB/v4l2** with custom ffmpeg filters.
- **Headless** over SSH; systemd units + JSONL journal.
- **Reports:** self-contained HTML per job (metrics, thumbnails, links to MP4).

**Non-Goals (v1)**
- Cloud accounts/sync, multi-node orchestration, GUI, non-pen CNC/G-code.

---

## 2) User stories (acceptance, abbreviated)

1. **Queue SVG** → auto-detect dims; choose paper; map layers→pens → state `QUEUED`.
2. **Optimize** via vpype preset or custom pipe → see before/after stroke & length deltas.
3. **Checklist gates** (paper taped, origin set, pen test, webcam OK) block Start until all green.
4. **Plot** shows live ETA, current layer/pen; pause/resume/abort; prompt at layer boundaries.
5. **Record** starts on `PLOTTING`, stops on terminal; saves MP4 (+ optional timelapse).
6. **Recover** after crash/SSH drop: resume or safe abort with consistent journal.
7. **Report** shows pre/post estimates vs actual, per-layer metrics, diffs.

---

## 3) Architecture

CLI/TUI ──> Orchestrator (FSM) ──> Device Driver(s)
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

- Parse SVG layer names/order; require 1:1 mapping layer→pen before start.
- At layer boundary: lift, park, prompt to swap pen (TUI/CLI + ntfy/MQTT), optional ink swatch.
- Store per-layer metrics & estimates; show per-layer ETAs during run.

```sh
plotty job layers <job>
plotty job map-pen <job> --layer "Hatch" --pen "0.4mm red"
plotty job plan <job> --json
```

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

```bash
mkdir -p docs
$EDITOR docs/PRD.md
git add docs/PRD.md && git commit -m "docs: add PRD for ploTTY v1" && git push
```
