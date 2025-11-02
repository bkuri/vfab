# ploTTY Implementation Roadmap

**Purpose:** This document outlines the remaining implementation tasks for ploTTY v1, organized by priority and complexity. It serves as a living roadmap for completing core functionality and nice-to-have management features.

---

## 1. Critical Path (Core Functionality)

### 1.1 Plotting Execution (`src/plotty/cli/batch/`)

**Priority: HIGH | Complexity: MEDIUM**

- [ ] **Pen-optimized planning execution** (Line 257)
  - Implement actual pen-optimized planning logic
  - Apply pen grouping to job planning
  - Update job states and metadata

- [ ] **Time estimation calculations** (Line 216)
  - Calculate estimated plotting time per pen group
  - Factor in pen swap overhead
  - Provide accurate ETA for batch operations

- [ ] **Traditional batch planning** (Line 333)
  - Implement individual job planning loop
  - Maintain existing job planning behavior
  - Support batch planning without pen optimization

- [ ] **Plotting execution with presets** (Line 416)
  - Connect batch plotting to actual plotter execution
  - Apply plot presets consistently across jobs
  - Handle pen swap prompts and automation

- [ ] **Queue clearing logic** (Line 442)
  - Implement job filtering by state and age
  - Safe job removal with cleanup
  - Support for dry-run preview mode

### 1.2 Job Management (`src/plotty/cli/job/`)

**Priority: HIGH | Complexity: LOW**

- [ ] **Job planning implementation** (Line 88)
  - Connect job planning to vpype optimization
  - Store planning results in job metadata
  - Update job state to PLANNED/READY

- [ ] **Test recording system** (Line 103)
  - Implement test plot recording functionality
  - Store test results and metrics
  - Support test result comparison

### 1.3 Plot Commands (`src/plotty/cli/plot/`)

**Priority: HIGH | Complexity: LOW**

- [ ] **Preset application logic** (Line 74)
  - Apply plot presets to plotting parameters
  - Integrate with existing plotting system
  - Validate preset compatibility

- [ ] **Interactive plotting** (Line 83)
  - Implement interactive plotting prompts
  - Support step-by-step plotting execution
  - Handle user input during plotting

- [ ] **Pen testing functionality** (Line 131)
  - Implement pen test plotting
  - Validate pen functionality before jobs
  - Store pen test results

---

## 2. Management Features (Nice-to-have)

### 2.1 Configuration Management (`src/plotty/cli/config/`)

**Priority: MEDIUM | Complexity: MEDIUM**

- [ ] **Pen listing/addition/removal** (Lines 35, 52, 64)
  - Implement pen database CRUD operations
  - Support pen specification validation
  - Update pen mapping configurations

- [ ] **Paper listing/addition/removal** (Lines 74, 90, 102)
  - Implement paper database CRUD operations
  - Support custom paper sizes and margins
  - Validate paper specifications

- [ ] **Configuration persistence** (Lines 202, 218)
  - Save configuration changes to YAML
  - Validate configuration before saving
  - Support configuration rollback

- [ ] **Session reset logic** (Line 340)
  - Implement configuration reset to defaults
  - Preserve critical settings during reset
  - Support selective reset options

### 2.2 Recovery System (`src/plotty/cli/recovery/`)

**Priority: LOW | Complexity: HIGH**

- [ ] **Recovery listing/execution** (Lines 27, 41, 51)
  - Implement crash recovery detection
  - List recoverable jobs and sessions
  - Execute recovery procedures safely

- [ ] **Job recovery logic** (Line 41)
  - Implement job state restoration
  - Validate job integrity before recovery
  - Handle partial recovery scenarios

- [ ] **Recovery status/cleanup** (Lines 65, 80)
  - Track recovery progress and status
  - Clean up failed recovery attempts
  - Maintain recovery logs and metrics

### 2.3 Guard System (`src/plotty/guards/`)

**Priority: LOW | Complexity: LOW**

- [ ] **Paper session validation** (`job_guards.py:75`)
  - Implement paper setup validation
  - Check paper alignment and dimensions
  - Validate paper session state

- [ ] **Pen-layer compatibility** (`job_guards.py:89`)
  - Validate pen assignments to layers
  - Check pen compatibility with layer requirements
  - Prevent incompatible pen-layer combinations

- [ ] **Camera health checks** (`system_guards.py:98`)
  - Implement camera connectivity testing
  - Validate camera feed quality
  - Handle camera unavailability gracefully

---

## 3. Implementation Priority Matrix

| Feature | Complexity | Impact | Priority | Estimated Effort |
|---------|------------|--------|----------|------------------|
| Pen-optimized planning execution | Medium | High | 1 | 2-3 days |
| Job planning implementation | Low | High | 2 | 1 day |
| Preset application logic | Low | Medium | 3 | 0.5 day |
| Time estimation calculations | Medium | Medium | 4 | 1-2 days |
| Traditional batch planning | Low | Medium | 5 | 0.5 day |
| Configuration management | Medium | Medium | 6 | 2-3 days |
| Plotting execution with presets | Medium | Medium | 7 | 1-2 days |
| Queue clearing logic | Low | Low | 8 | 0.5 day |
| Interactive plotting | Low | Low | 9 | 0.5 day |
| Pen testing functionality | Low | Low | 10 | 0.5 day |
| Recovery system | High | Low | 11 | 3-4 days |
| Guard validation | Low | Low | 12 | 1-2 days |

---

## 4. Development Phases

### Phase 1: Core Plotting (Week 1)
**Goal:** Complete essential plotting functionality

**Tasks:**
- [ ] Job planning implementation
- [ ] Preset application logic  
- [ ] Traditional batch planning
- [ ] Interactive plotting
- [ ] Pen testing functionality

**Deliverables:**
- Fully functional job planning
- Working plot preset system
- Basic batch operations

### Phase 2: Advanced Plotting (Week 2)
**Goal:** Complete pen optimization and batch features

**Tasks:**
- [ ] Pen-optimized planning execution
- [ ] Time estimation calculations
- [ ] Plotting execution with presets
- [ ] Queue clearing logic

**Deliverables:**
- Complete pen optimization system
- Accurate time estimation
- Full batch operation capabilities

### Phase 3: Management Features (Week 3-4)
**Goal:** Complete configuration and management systems

**Tasks:**
- [ ] Configuration management
- [ ] Recovery system (optional)
- [ ] Guard validation

**Deliverables:**
- Complete configuration system
- Robust recovery capabilities
- Comprehensive guard system

---

## 5. Integration Points

### 5.1 Existing Systems Integration

**FSM Integration:**
- All plotting features must integrate with `src/plotty/fsm.py`
- Maintain state consistency across operations
- Support crash recovery and state restoration

**Database Integration:**
- Use existing models in `src/plotty/models.py`
- Follow database patterns in `src/plotty/db.py`
- Maintain data integrity and consistency

**Configuration Integration:**
- Use configuration system in `src/plotty/config.py`
- Support YAML-based configuration
- Validate configuration changes

### 5.2 Testing Strategy

**Unit Tests:**
- Test each implementation task individually
- Mock external dependencies (AxiDraw, camera)
- Validate error handling and edge cases

**Integration Tests:**
- Test end-to-end workflows
- Validate FSM state transitions
- Test database operations and consistency

**Smoke Tests:**
- Verify basic functionality after each phase
- Test CLI commands and options
- Validate configuration loading and saving

---

## 6. Success Criteria

### 6.1 Functional Requirements

**Phase 1 Completion:**
- [ ] All jobs can be planned successfully
- [ ] Plot presets work with all plot commands
- [ ] Basic batch operations function correctly
- [ ] Interactive plotting provides user feedback

**Phase 2 Completion:**
- [ ] Pen optimization reduces pen swaps by >50%
- [ ] Time estimates are accurate within ±20%
- [ ] Batch plotting executes without manual intervention
- [ ] Queue management operations work reliably

**Phase 3 Completion:**
- [ ] Configuration can be fully managed via CLI
- [ ] Recovery system handles crash scenarios
- [ ] Guard system prevents unsafe operations

### 6.2 Quality Requirements

**Code Quality:**
- [ ] All new code passes linting (`uvx ruff check`)
- [ ] All new code is formatted (`uvx black`)
- [ ] Test coverage >80% for new features
- [ ] Documentation updated for all new commands

**Performance:**
- [ ] CLI commands respond within 2 seconds
- [ ] Batch operations scale to 50+ jobs
- [ ] Memory usage remains stable during long operations
- [ ] No memory leaks in plotting operations

---

## 7. Risk Mitigation

### 7.1 Technical Risks

**AxiDraw Integration:**
- **Risk:** Hardware dependency issues
- **Mitigation:** Graceful degradation, comprehensive mocking in tests

**Database Consistency:**
- **Risk:** Data corruption during concurrent operations
- **Mitigation:** Atomic operations, proper transaction handling

**Performance Scaling:**
- **Risk:** Batch operations become slow with many jobs
- **Mitigation:** Efficient algorithms, progress indicators, pagination

### 7.2 Schedule Risks

**Complexity Underestimation:**
- **Risk:** Tasks take longer than estimated
- **Mitigation:** Buffer time in schedule, regular progress reviews

**Dependency Delays:**
- **Risk:** External dependencies cause delays
- **Mitigation:** Early dependency validation, fallback options

**Quality Issues:**
- **Risk:** Rushed implementation introduces bugs
- **Mitigation:** Code reviews, automated testing, phased approach

---

## 8. Next Steps

1. **Create GitHub Issues** for each task group
2. **Set up Milestones** for each development phase
3. **Assign tasks** to team members based on expertise
4. **Set up CI/CD** for automated testing and validation
5. **Establish code review process** for all changes
6. **Monitor progress** against timeline and adjust as needed

---

## 9. Tracking

**GitHub Milestones:**
- `v1-phase1-core-plotting` - Week 1 deliverables
- `v1-phase2-advanced-plotting` - Week 2 deliverables  
- `v1-phase3-management-features` - Week 3-4 deliverables

**Key Metrics:**
- Tasks completed per phase
- Test coverage percentage
- Code quality metrics
- Performance benchmarks

**Review Schedule:**
- Daily standups for progress tracking
- Weekly reviews for milestone assessment
- Phase completion reviews before proceeding

---

*This document is a living roadmap and will be updated as implementation progresses. Last updated: $(date)*