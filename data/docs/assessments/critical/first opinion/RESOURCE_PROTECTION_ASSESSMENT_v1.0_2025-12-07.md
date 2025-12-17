# RESOURCE PROTECTION & EMERGENCY SHUTDOWN ASSESSMENT

**Version:** 1.1
**Date:** 2025-12-07
**Assessment Type:** Critical Infrastructure Gap Analysis
**Status:** IMPLEMENTED - All P0/P1 items complete

---

## EXECUTIVE SUMMARY

The system has **partial resource protection** but lacks a comprehensive, unified resource governance layer with proper emergency shutdown capabilities. The existing components are well-designed but operate in isolation without integration.

### Overall Rating: **MODERATE RISK**

| Category | Status | Risk Level |
|----------|--------|------------|
| VRAM Monitoring | Implemented | LOW |
| GPU Memory Management | Implemented | LOW |
| CPU Monitoring | NOT IMPLEMENTED | HIGH |
| RAM Monitoring | PARTIAL (estimation only) | MEDIUM |
| Disk I/O Monitoring | NOT IMPLEMENTED | MEDIUM |
| Throttling | PARTIAL (queue-based) | MEDIUM |
| Emergency Shutdown | NOT IMPLEMENTED | **CRITICAL** |
| Error Reporting | PARTIAL (console only) | HIGH |
| Component Integration | NOT IMPLEMENTED | HIGH |

---

## DETAILED FINDINGS

### 1. WHAT EXISTS (Positive)

#### 1.1 Agent Management System (AMS)
**Location:** `src/symbo_agentic_reasoners/infrastructure/ams.py`

**Implemented:**
- VRAM monitoring via `nvidia-smi` queries (lines 206-231)
- "One-Model-At-A-Time" enforcement for cognitive agents
- Agent lifecycle management (create, activate, deactivate, kill, suspend)
- Background monitoring thread (`_monitor_loop`) checking every 5 seconds
- Queue-based VRAM slot allocation
- Thread-safe operations with `threading.RLock()`

**Hardware Constants:**
```python
MAX_VRAM_GB = 8.0                  # RTX 4060 VRAM limit
MAX_RAM_GB = 32.0                  # System RAM limit
VRAM_THRESHOLD = 0.90              # 90% usage triggers rejection
LLM_VRAM_REQUIREMENT = 5.5         # 7B model at 4-bit quantization
INFRASTRUCTURAL_VRAM = 0.5         # Reserved for OS/infrastructure
```

**Critical Gap:** At line 524, the monitor detects >95% VRAM but only prints a warning:
```python
if vram_utilization > 0.95:
    print(f"AMS CRITICAL: VRAM usage {vram_utilization:.1%} exceeds critical threshold!")
    # In production, would take corrective action  <-- NOT IMPLEMENTED
```

#### 1.2 GPU Scheduler
**Location:** `src/symbo_agentic_reasoners/optimization/deployment/gpu_scheduler.py`

**Implemented:**
- GPU availability detection via PyTorch/CUDA
- GPU memory tracking (total, used, free)
- Priority-based task queuing (`PriorityQueue`)
- Memory-aware task execution
- Automatic CPU fallback when GPU unavailable
- Task statistics tracking

**Limitation:** Not integrated with AMS or main orchestrator.

#### 1.3 Failure Analysis Team
**Location:** `src/symbo_agentic_reasoners/middleware/failure_analysis.py`

**Implemented:**
- Error classification (COMPUTATIONAL, LOGICAL, DOMAIN)
- Pattern matching for resource-related failures (timeout, overflow, memory, OOM)
- Root cause analysis
- Alternative path generation ("Plan B" engine)
- Remedy actions: `REQUEST_RESOURCES`, `TRIGGER_REFINEMENT`, `TRIGGER_ALTERNATIVE`

**Limitation:** Classifies and routes errors but does not prevent them or throttle compute.

#### 1.4 Resilience Tester
**Location:** `src/symbo_agentic_reasoners/optimization/hardening/resilience_tester.py`

**Implemented:**
- Chaos engineering fault scenarios
- Emergency abort function (`abort_all_injections()`)
- Recovery time measurement
- Safe mode for simulation-only testing

**Limitation:** Testing-only tool, not operational protection.

---

### 2. CRITICAL GAPS

#### 2.1 NO CPU MONITORING (HIGH RISK)
- `get_ram_usage()` exists but only estimates based on registered agents
- No `psutil.cpu_percent()` tracking
- No per-agent CPU throttling
- No CPU spike detection

**Impact:** Runaway computations can freeze the system without warning.

#### 2.2 NO ACTUAL RAM MONITORING (MEDIUM RISK)
- AMS has `MAX_RAM_GB = 32.0` but `get_ram_usage()` just sums agent requirements
- No real-time system memory checking via `psutil`
- No memory pressure response

**Impact:** System can run out of memory without detection.

#### 2.3 NO DISK I/O MONITORING (MEDIUM RISK)
- Vector database operations not tracked
- No disk space constraints checked
- No I/O throttling

**Impact:** Disk full conditions can cause silent failures.

#### 2.4 NO EMERGENCY SHUTDOWN SYSTEM (CRITICAL)
- AMS prints warning at 95% VRAM but takes NO action
- No global kill switch
- No graceful degradation path
- No process termination cascade
- No state preservation before shutdown

**Impact:** Catastrophic failure with no recovery path.

#### 2.5 NO TIMEOUT/WATCHDOG MECHANISMS (HIGH RISK)
- No global execution timeouts
- No deadlines on operations
- No watchdog timers for hung processes
- Operations can block indefinitely

**Impact:** Hung agents can starve the system.

#### 2.6 NO CENTRALIZED RESOURCE GOVERNOR (HIGH RISK)
- GPU Scheduler, Compute Optimizer, Security Monitor exist in isolation
- No unified API for resource queries
- No coordinated throttling decisions
- Components don't communicate

**Impact:** Resource contention without arbitration.

#### 2.7 NO PERSISTENT ERROR LOGGING (HIGH RISK)
- Errors print to console and disappear
- No log files
- No alerting system
- No error persistence for post-mortem analysis

**Impact:** Cannot diagnose failures after the fact.

---

### 3. CURRENT PROTECTION FLOW

```
[Problem Input]
     |
     v
[AMS] ---> Check VRAM availability
     |        |
     |        +---> If >90%: REJECT agent activation
     |        +---> If >95%: PRINT WARNING (no action)
     |
     v
[GPU Scheduler] ---> Check GPU memory
     |        |
     |        +---> If insufficient: FALLBACK to CPU
     |
     v
[Task Execution]
     |
     v
[Failure Analysis] ---> IF error detected:
     |        |
     |        +---> Classify error type
     |        +---> Generate "Plan B"
     |        +---> Route to alternative method
     |
     v
[Result or Failure]  <-- No emergency shutdown path exists
```

---

### 4. RECOMMENDED ARCHITECTURE

```
                    +-------------------------+
                    |   RESOURCE GOVERNOR     |
                    |   (New Central Module)  |
                    +-------------------------+
                              |
        +---------------------+---------------------+
        |                     |                     |
   +----v----+          +-----v-----+         +----v----+
   |   AMS   |          |    GPU    |         | Memory  |
   | (VRAM)  |          | Scheduler |         | Monitor |
   +---------+          +-----------+         +---------+
        |                     |                     |
        +---------------------+---------------------+
                              |
                    +--------------------+
                    | THROTTLE DECISION  |
                    +--------------------+
                              |
        +---------------------+---------------------+
        |                     |                     |
   PROCEED              THROTTLE            EMERGENCY
   (< 80%)              (80-95%)             SHUTDOWN
                              |                (>95%)
                    +--------------------+
                    | - Pause queue      | +-------------------+
                    | - Extend timeouts  | | - Save state      |
                    | - Reduce priority  | | - Kill agents     |
                    +--------------------+ | - Log error       |
                                           | - Alert user      |
                                           +-------------------+
```

---

### 5. SPECIFIC FIXES NEEDED

#### 5.1 Immediate (Critical)

1. **Add Emergency Shutdown to AMS** (`ams.py:511-530`)
   - When >95% VRAM: Force-deactivate cognitive agents
   - When >98% VRAM: System-wide shutdown
   - Save current state before shutdown

2. **Implement CPU/RAM Monitoring**
   - Use `psutil.cpu_percent()` and `psutil.virtual_memory()`
   - Add to AMS monitoring loop
   - Define thresholds (e.g., 90% CPU, 85% RAM)

3. **Create Error Persistence**
   - Log errors to `data/traces/error/`
   - Include timestamp, agent, stack trace
   - Rotate logs to prevent disk fill

#### 5.2 Short-term (High Priority)

4. **Create ResourceGovernor Module**
   - Central resource tracking
   - Unified throttle decisions
   - Integration point for all monitors

5. **Add Watchdog Timers**
   - Default 60-second timeout on operations
   - Configurable per-operation
   - Automatic termination on timeout

6. **Implement Graceful Degradation**
   - Reduce agent concurrency when stressed
   - Extend timeouts instead of failing
   - Pause non-essential operations

#### 5.3 Medium-term (Improvement)

7. **Add Alerting System**
   - Console alerts for warnings
   - File logging for all events
   - Optional webhook/email for critical

8. **Integrate Existing Components**
   - Wire GPU Scheduler to orchestrator
   - Connect Failure Analysis to ResourceGovernor
   - Enable Resilience Tester for continuous monitoring

---

### 6. IMPLEMENTATION PRIORITY

| Priority | Component | Effort | Risk Mitigated |
|----------|-----------|--------|----------------|
| P0 | Emergency shutdown in AMS | 2 hours | CRITICAL |
| P0 | CPU/RAM monitoring | 3 hours | HIGH |
| P1 | Error persistence logging | 2 hours | HIGH |
| P1 | Watchdog timers | 4 hours | HIGH |
| P2 | ResourceGovernor module | 8 hours | MEDIUM |
| P2 | Component integration | 6 hours | MEDIUM |
| P3 | Alerting system | 4 hours | LOW |
| P3 | Graceful degradation | 6 hours | LOW |

---

### 7. CONCLUSION

The system has strong foundations for resource protection (AMS is well-designed), but the critical emergency response path is incomplete. The primary risk is that **resource exhaustion detection exists but response does not**.

**Recommendation:** Implement P0 items immediately to prevent catastrophic failure. The existing infrastructure provides good hooks for integration - the main work is connecting them and adding the missing shutdown logic.

---

## APPENDIX A: Key File Locations

| Component | Path |
|-----------|------|
| AMS | `src/symbo_agentic_reasoners/infrastructure/ams.py` |
| GPU Scheduler | `src/symbo_agentic_reasoners/optimization/deployment/gpu_scheduler.py` |
| Compute Optimizer | `src/symbo_agentic_reasoners/optimization/deployment/compute_optimizer.py` |
| Security Monitor | `src/symbo_agentic_reasoners/optimization/hardening/security_monitor.py` |
| Resilience Tester | `src/symbo_agentic_reasoners/optimization/hardening/resilience_tester.py` |
| Failure Analysis | `src/symbo_agentic_reasoners/middleware/failure_analysis.py` |
| Phase0 System | `src/symbo_agentic_reasoners/core/system.py` |

## APPENDIX B: Current Hardware Constraints

```
CPU:        AMD Ryzen 7 8700F (8-Core)
System RAM: 32 GB DDR5
GPU:        NVIDIA GeForce RTX 4060
VRAM:       8 GB GDDR6 (CRITICAL BOTTLENECK)
```

---

---

## IMPLEMENTATION SUMMARY (Added 2025-12-07)

### Completed Implementations

| Item | Status | Location |
|------|--------|----------|
| Emergency shutdown in AMS | DONE | `infrastructure/ams.py:759-823` |
| CPU monitoring with psutil | DONE | `infrastructure/ams.py:346-366` |
| RAM monitoring with psutil | DONE | `infrastructure/ams.py:308-344` |
| Error persistence logging | DONE | `infrastructure/ams.py:834-862` |
| Watchdog timeout system | DONE | `infrastructure/watchdog.py` (new) |
| ResourceGovernor integration | DONE | `infrastructure/resource_governor.py` (new) |

### New Files Created

1. **watchdog.py** - Operation timeout enforcement
   - Task registration with configurable timeouts
   - Background monitoring thread
   - Heartbeat mechanism for long tasks
   - Decorator and context manager support

2. **resource_governor.py** - Central resource coordination
   - Integrates AMS, Watchdog, GPU Scheduler
   - Unified throttle level calculation
   - Operation approval/rejection logic
   - Emergency callback system

### AMS Enhancements

- Added `EmergencyLevel` enum (NORMAL, WARNING, CRITICAL, EMERGENCY, SHUTDOWN)
- Added real CPU/RAM monitoring via psutil
- Added sustained high resource counters (avoids single-spike reactions)
- Added `_execute_emergency_shutdown()` - actual termination of agents
- Added error logging to `data/traces/error/`
- Added emergency callback registration
- Added resource history for trend detection

### Test Script

Run verification with:
```bash
python scripts/test_resource_protection.py
```

### Thresholds Configured

| Resource | Warning | Critical | Emergency |
|----------|---------|----------|-----------|
| VRAM | 85% | 95% | 98% |
| RAM | 85% | 92% | 95% |
| CPU | 90% | 95% | - |

---

*Assessment prepared by Claude Code analysis of symbo_agentic_reasoners codebase*
