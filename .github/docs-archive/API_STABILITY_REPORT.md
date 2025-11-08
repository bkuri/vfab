# ploTTY v0.9.0 API Stability Report

## Executive Summary

This report analyzes the current ploTTY API structure to identify stable public APIs
that should be maintained for v1.0.0 compatibility.

## Core Module APIs

### config.py

**Public Classes:**
- `CameraCfg`
- `DatabaseCfg`
- `DeviceCfg`
- `OptimizationLevelCfg`
- `DigestLevelCfg`
- `FileTypeCfg`
- `OptimizationCfg`
- `VpypeCfg`
- `PaperCfg`
- `HooksCfg`
- `RecoveryCfg`
- `PhysicalSetupCfg`
- `LoggingSettings`
- `Settings`

**Public Functions:**
- `load_config()`
- `get_config()`
- `save_config()`
- `load_vpype_presets()`

### models.py

**Public Classes:**
- `Device`
- `Pen`
- `Paper`
- `Job`
- `Layer`
- `StatisticsConfig`
- `JobStatistics`
- `LayerStatistics`
- `SystemStatistics`
- `PerformanceMetrics`

### fsm.py

**Public Classes:**
- `JobState`
- `StateTransition`
- `JobFSM`

**Public Functions:**
- `create_fsm()`
- `from_job()`
- `can_transition_to()`
- `transition_to()`
- `get_state_history()`
- `queue_job()`
- `analyze_job()`
- `optimize_job()`
- `ready_job()`
- `queue_ready_job()`
- `validate_file()`
- `apply_optimizations()`
- `arm_job()`
- `start_plotting()`
- `pause_plotting()`
- `resume_plotting()`
- `complete_job()`
- `abort_job()`
- `fail_job()`
- `get_last_guard_results()`
- `create_hook_executor()`
- `create_guard_system()`
- `get_crash_recovery()`
- `create_checklist()`
- `get_statistics_service()`

**Public Constants:**
- `NEW`
- `QUEUED`
- `ANALYZED`
- `OPTIMIZED`
- `READY`
- `ARMED`
- `PLOTTING`
- `PAUSED`
- `COMPLETED`
- `ABORTED`
- `FAILED`

### db.py

**Public Classes:**
- `SessionContext`

**Public Functions:**
- `init_database()`
- `get_session()`
- `get_database_path()`
- `get_database_info()`
- `make_engine()`
- `is_valid_database_url()`
- `get_default_database_url()`

### utils.py

**Public Classes:**
- `PlottyError`
- `JobError`
- `DeviceError`
- `ConfigError`
- `ValidationError`
- `ErrorHandler`

**Public Functions:**
- `create_error()`
- `create_job_error()`
- `create_device_error()`
- `create_config_error()`
- `create_validation_error()`
- `validate_file_exists()`
- `validate_directory()`
- `handle()`

**Public Constants:**
- `message`
- `suggestion`
- `message`
- `suggestion`
- `message`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `message`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `message`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`
- `suggestion`

### stats.py

**Public Classes:**
- `StatisticsService`

**Public Functions:**
- `get_statistics_service()`
- `record_job_event()`
- `record_layer_stats()`
- `record_performance_metric()`
- `get_job_summary_stats()`
- `get_performance_stats()`
- `get_pen_usage_stats()`
- `configure_statistics()`
- `cleanup_old_statistics()`

**Public Constants:**
- `deleted_count`

### recovery.py

**Public Classes:**
- `CrashRecovery`

**Public Functions:**
- `get_crash_recovery()`
- `requeue_job_to_front()`
- `requeue_job_to_end()`
- `detect_interrupted_jobs()`
- `prompt_interrupted_resume()`
- `resume_all_jobs()`
- `register_fsm()`
- `unregister_fsm()`
- `recover_job()`
- `get_resumable_jobs()`
- `get_job_status()`
- `cleanup_journal()`
- `signal_handler()`

**Public Constants:**
- `last_state`
- `emergency_shutdown`
- `current_state`
- `last_transition`
- `emergency_shutdown`
- `console`
- `Confirm`
- `last_state_change`
- `emergency_shutdown`
- `emergency_shutdown`

### hooks.py

**Public Classes:**
- `HookExecutionError`
- `HookExecutor`

**Public Functions:**
- `create_hook_executor()`
- `execute_hooks()`
- `get_context()`

**Public Constants:**
- `substituted_cmd`
- `substituted_path`
- `substituted_url`
- `hook_type`
- `hook_target`
- `hook_type`
- `hook_type`
- `hook_type`

## CLI API

### Main Commands

- `plotty add`
- `plotty stats`
- `plotty guard`
- `plotty remove`
- `plotty system`
- `plotty list`
- `plotty check`
- `plotty info`

### Command Subcommands

- `stats.jobs`
- `stats.summary`
- `stats.performance`
- `guard.validate`
- `guard.list`
- `guard.check`
- `system.export`
- `system.import_cmd`
- `list.presets`
- `list.paper_management`
- `list.jobs`
- `list.pen_management`
- `list.setup_wizard`
- `check.self`
- `check.ready`
- `check.timing`
- `check.camera`
- `check.servo`
- `check.job`
- `info.output`
- `info.session`
- `info.utils`
- `info.queue`
- `info.job`
- `info.system`

## Configuration API

**Configuration Classes:**
- `CameraCfg`
- `DatabaseCfg`
- `DeviceCfg`
- `OptimizationLevelCfg`
- `DigestLevelCfg`
- `FileTypeCfg`
- `OptimizationCfg`
- `VpypeCfg`
- `PaperCfg`
- `HooksCfg`
- `RecoveryCfg`
- `PhysicalSetupCfg`


## API Stability Recommendations

### 🟢 STABLE APIs (Safe for v1.0.0)

**CLI Commands:**
- All top-level `plotty` commands and their basic options
- Core workflow commands: `add`, `list`, `info`, `check`, `remove`, `stats`

**Configuration:**
- All `*Cfg` classes in `config.py`
- YAML-based configuration structure
- Environment variable overrides

**Core Models:**
- Database models in `models.py` (Job, Layer, Pen, Paper, etc.)
- FSM states and transitions

### 🟡 STABILIZING APIs (Review needed)

**Internal Modules:**
- `utils.py` functions (review for utility vs internal use)
- `stats.py` service classes
- `recovery.py` system classes

**Advanced Features:**
- Hook system APIs
- Plugin system interfaces
- Advanced configuration options

### 🔴 INTERNAL APIs (Not for public use)

**Implementation Details:**
- Database session management
- Internal FSM implementation
- CLI argument parsing internals
- Logging system internals

## v1.0.0 API Stability Requirements

### Must Be Stable
1. **CLI Command Structure** - All current commands must remain compatible
2. **Configuration Format** - YAML structure must remain backward compatible
3. **Database Models** - Core models must maintain compatibility
4. **Basic Workflows** - Core job lifecycle operations

### Should Be Stable
1. **Utility Functions** - Common utilities in `utils.py`
2. **Statistics API** - Performance and job statistics
3. **Recovery System** - Job recovery and resumption

### Can Change
1. **Internal Implementation** - FSM internals, database sessions
2. **CLI Argument Parsing** - Internal argument handling
3. **Logging System** - Internal logging structure

## Recommendations for v0.9.0

1. **Document Public APIs** - Add proper docstrings to all public elements
2. **Version the APIs** - Consider API versioning for future changes
3. **Create API Tests** - Add compatibility tests for public APIs
4. **Deprecation Policy** - Establish clear deprecation policy for v1.0.0

## Next Steps

1. Review and approve this API stability analysis
2. Update documentation to reflect stable vs internal APIs
3. Add API compatibility tests to test suite
4. Prepare v1.0.0 API stability guarantee
