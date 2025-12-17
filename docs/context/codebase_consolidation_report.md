# Codebase Consolidation Report: Solvers, Engines, and Agents
## SYMBO_AGENTIC_REASONERS Mathematical Problem Solver

**Date Generated:** 2025-12-14
**Project:** Mathematic Agent Based Solver
**Status:** Analysis Complete - Consolidation Plan Ready

---

## Executive Summary

The SYMBO_AGENTIC_REASONERS codebase has solver, engine, and agent files scattered across multiple locations:

- **Root-level `core/` directory:** Contains `reasoning_engine.py` (orphaned, uses SymPy)
- **`src/symbo_agentic_reasoners/core/`:** Contains `math_solver.py` and `solver_engine.py` (core solvers)
- **`src/symbo_agentic_reasoners/solvers/`:** Contains `pilot_solver.py` (legacy agent-based solver)
- **`src/symbo_agentic_reasoners/agents/specialists/`:** Contains domain-specific solvers mixed with specialist agents
- **`src/symbo_agentic_reasoners/discovery/`:** Contains `curiosity_engine.py`, `imagination_engine.py`, and discovery engines
- **`src/system_agents/`:** Contains 10 system-level agents for maintenance/operations
- **`scripts/`:** Contains `math_solver.py` and `math_solver_ui.py` (entry points, not core logic)
- **`tests/`:** Contains `crackfinder_agent.py` (implementation, not a test)

This fragmentation makes it difficult to:
- Find related components
- Understand the solving pipeline
- Maintain consistent dependencies
- Extend the solver architecture

---

## Detailed File Inventory

### SOLVERS (Files with "solver" in name)

| File Path | Type | Purpose | Status |
|-----------|------|---------|--------|
| `core/reasoning_engine.py` | Orphaned Engine | Formal proof system (uses SymPy - against NO SYMPY philosophy) | NEEDS CONSOLIDATION |
| `src/symbo_agentic_reasoners/core/math_solver.py` | Solver API | User-facing problem solver using full agent pipeline | CORE - STAYS |
| `src/symbo_agentic_reasoners/core/solver_engine.py` | Solver Engine | Direct problem solving (bypasses orchestrator, native modules) | CORE - STAYS |
| `src/symbo_agentic_reasoners/solvers/pilot_solver.py` | Legacy Agent | Original tracer bullet solver (Phase 1) | LEGACY - REVIEW |
| `src/symbo_agentic_reasoners/agents/specialists/algebra/equation_system_solver.py` | Specialist | Solves equation systems | STAYS (Specialist) |
| `src/symbo_agentic_reasoners/agents/specialists/calculus/ode_solver.py` | Specialist | Solves ODEs | STAYS (Specialist) |
| `scripts/math_solver.py` | CLI Entry Point | Command-line interface to solvers | CORRECT LOCATION |
| `scripts/math_solver_ui.py` | GUI Entry Point | Graphical interface to solvers | CORRECT LOCATION |

**Key Finding:** Most solvers are already in appropriate locations. Main issue: Root-level `core/reasoning_engine.py` is orphaned and violates the NO SYMPY philosophy.

---

### ENGINES (Files with "engine" in name)

| File Path | Type | Purpose | Status |
|-----------|------|---------|--------|
| `core/reasoning_engine.py` | Formal Proof Engine | Implements formal verification using Peano axioms (SymPy-based) | **ORPHANED** |
| `src/symbo_agentic_reasoners/core/solver_engine.py` | Problem Solver | Streamlined direct solving pipeline | CORE - CORRECT |
| `src/symbo_agentic_reasoners/discovery/curiosity_engine.py` | Autonomous Explorer | Generates and solves novel problems during idle time | DISCOVERY - CORRECT |
| `src/symbo_agentic_reasoners/discovery/imagination_engine.py` | Background Explorer | Autonomous mathematical exploration with knowledge integration | DISCOVERY - CORRECT |
| `src/symbo_agentic_reasoners/discovery/deep_search/prover_engine.py` | Theorem Prover | Abstraction for switching between proof backends | DISCOVERY - CORRECT |
| `src/symbo_agentic_reasoners/agents/specialists/statistics/bayesian_engine.py` | Probabilistic Engine | Implements Bayesian inference | SPECIALIST - CORRECT |

**Key Finding:** Most engines are properly organized. The only problematic engine is `core/reasoning_engine.py` at the project root level.

---

### AGENTS (Files with "agent" in name)

#### Core Agent Infrastructure
| File Path | Type | Purpose | Status |
|-----------|------|---------|--------|
| `src/symbo_agentic_reasoners/core/bdi_agent.py` | Framework | BDI (Belief-Desire-Intention) agent base class | CORE - CORRECT |
| `src/symbo_agentic_reasoners/core/agent_communication.py` | Framework | Agent message passing and communication | CORE - CORRECT |
| `src/symbo_agentic_reasoners/infrastructure/agent_factory.py` | Factory | Creates agent instances dynamically | INFRASTRUCTURE - CORRECT |
| `src/symbo_agentic_reasoners/infrastructure/agent_pool.py` | Pool | Manages agent lifecycle and pooling | INFRASTRUCTURE - CORRECT |
| `src/symbo_agentic_reasoners/infrastructure/agent_registry.py` | Registry | Tracks available agents and their capabilities | INFRASTRUCTURE - CORRECT |
| `src/symbo_agentic_reasoners/monitoring/agent_monitor.py` | Monitor | Tracks agent health and performance | MONITORING - CORRECT |

#### Specialist Agents (Domain-Specific)
| Directory | Count | Status | Purpose |
|-----------|-------|--------|---------|
| `agents/specialists/algebra/` | 5 agents | CORRECT | Algebra specialists |
| `agents/specialists/calculus/` | 4 agents | CORRECT | Calculus specialists |
| `agents/specialists/discrete_math/` | 2 agents | CORRECT | Discrete math agents |
| `agents/specialists/geometry/` | 3 agents | CORRECT | Geometry specialists |
| `agents/specialists/linear_algebra/` | 4 agents | CORRECT | Linear algebra specialists |
| `agents/specialists/logic/` | 3 agents | CORRECT | Logic specialists |
| `agents/specialists/numerical/` | 1 agent | CORRECT | Numerical computation |
| `agents/specialists/physics/` | 9 agents | CORRECT | Physics specialists |
| `agents/specialists/statistics/` | 3 agents | CORRECT | Statistics agents |

#### Supervisor Agents
| File Path | Count | Status | Purpose |
|-----------|-------|--------|---------|
| `src/symbo_agentic_reasoners/agents/supervisors/` | 10 supervisors | CORRECT | Domain supervisors coordinating specialists |

#### Synthesis Agents
| File Path | Count | Status | Purpose |
|-----------|-------|--------|---------|
| `src/symbo_agentic_reasoners/agents/synthesis/` | 4 agents | CORRECT | Proof and conjecture synthesis |

#### Verification Agents
| File Path | Count | Status | Purpose |
|-----------|-------|--------|---------|
| `src/symbo_agentic_reasoners/agents/provers/` | 2 agents | CORRECT | Logic verification |

#### System Agents
| File Path | Type | Purpose | Status |
|-----------|------|---------|--------|
| `src/system_agents/audit_agent.py` | System | Audits system health and performance | CORRECT |
| `src/system_agents/cleanup_agent.py` | System | Manages cleanup operations | CORRECT |
| `src/system_agents/code_chunking_agent.py` | System | Decomposes code for analysis | CORRECT |
| `src/system_agents/code_chunking_agent - 2.py` | System | **DUPLICATE** - marked with " - 2" | NEEDS CLEANUP |
| `src/system_agents/crackfinder_agent.py` | System | Testing framework (comprehensive crack-finding) | CORRECT |
| `src/system_agents/documentation_agent.py` | System | Generates documentation | CORRECT |
| `src/system_agents/mathematical_cracker.py` | System | Tests mathematical correctness | CORRECT |
| `src/system_agents/script_decomposer.py` | System | Decomposes scripts into components | CORRECT |
| `src/system_agents/security_stress_tester.py` | System | Tests security under stress | CORRECT |
| `src/system_agents/structure_cataloger.py` | System | Catalogs codebase structure | CORRECT |

#### Misplaced Implementation
| File Path | Type | Purpose | Status |
|-----------|------|---------|--------|
| `tests/crackfinder_agent.py` | Test/Implementation | Testing framework implementation | **MISPLACED** - Move to `src/system_agents/` |

**Key Finding:** Agent organization is excellent. All specialist, supervisor, and synthesis agents are properly organized. Main issues: One system agent is in `tests/` when it should be in `src/system_agents/`, and there's a duplicate `code_chunking_agent - 2.py`.

---

## Issues Identified

### CRITICAL ISSUES

1. **Orphaned Root-Level Engine**
   - File: `core/reasoning_engine.py`
   - Problem: At project root, violates NO SYMPY philosophy (uses `sympy as sp`)
   - Impact: Creates confusion about solver architecture
   - Recommendation: Move to `src/symbo_agentic_reasoners/core/` or archive

2. **SymPy-Using Engine in NO SYMPY Project**
   - File: `core/reasoning_engine.py`
   - Problem: Implements formal proof system using SymPy
   - Project Philosophy: "NO SYMPY - Use native symbolic module"
   - Recommendation: Convert to native modules or move to archive

### MODERATE ISSUES

3. **Misplaced Test Implementation**
   - File: `tests/crackfinder_agent.py`
   - Problem: Full testing framework (not a test file)
   - Current Location: `tests/` (test directory)
   - Correct Location: `src/system_agents/`
   - Impact: Unclear what goes in tests vs. system agents

4. **Duplicate System Agent**
   - File: `src/system_agents/code_chunking_agent - 2.py`
   - Problem: Duplicate with unusual naming convention
   - Recommendation: Verify which is current, delete other, document intent

### MINOR ISSUES

5. **Legacy Pilot Solver**
   - File: `src/symbo_agentic_reasoners/solvers/pilot_solver.py`
   - Status: Phase 1 "tracer bullet" solver
   - Impact: Historical artifact, may be redundant with `solver_engine.py`
   - Recommendation: Document purpose or mark as deprecated

6. **Multiple Phases in Data/Archive**
   - Issue: Phase documentation scattered in `data/docs/MASTER_ARCHIVE/`
   - Impact: Not part of active codebase but referenced in analysis
   - Recommendation: Keep for historical reference, exclude from active code

---

## Current Organization Assessment

### WELL-ORGANIZED AREAS (No Action Needed)

#### ✓ Core System Files
- `src/symbo_agentic_reasoners/core/` properly contains:
  - `solver_engine.py` - Direct solving pipeline
  - `math_solver.py` - User-facing API
  - `bdi_agent.py` - Agent framework
  - `orchestrator.py` - Task orchestration
  - Native modules (`native_symbolic.py`, `native_calculus.py`)
  - Supporting infrastructure

#### ✓ Specialist Agents
- `src/symbo_agentic_reasoners/agents/specialists/` contains:
  - Domain-organized subdirectories (algebra/, calculus/, physics/, etc.)
  - Specialist and engine implementations properly grouped
  - Supervisor agents in `supervisors/` subdirectory
  - Clear responsibility boundaries

#### ✓ Discovery System
- `src/symbo_agentic_reasoners/discovery/` contains:
  - `curiosity_engine.py` - Idle-time exploration
  - `imagination_engine.py` - Background learning
  - `deep_search/` - Advanced proof search
  - Conjecture and formalization modules

#### ✓ System Agents
- `src/system_agents/` contains:
  - Operational agents (audit, cleanup, monitoring)
  - Analysis agents (code chunking, structure cataloging)
  - Testing agents (crackfinder, stress tester)

#### ✓ Entry Points
- `scripts/` correctly contains:
  - `math_solver.py` - CLI interface
  - `math_solver_ui.py` - GUI interface
  - Test runners and utilities

#### ✓ Infrastructure
- `src/symbo_agentic_reasoners/infrastructure/` properly organized
- `src/symbo_agentic_reasoners/monitoring/` properly organized
- `src/symbo_agentic_reasoners/optimization/` properly organized

### PROBLEM AREAS (Action Needed)

#### ✗ Orphaned Root-Level Core
- **Location:** `core/` at project root
- **Files:** `reasoning_engine.py` only
- **Issue:** Isolated from main source tree
- **Action:** Consolidate into `src/symbo_agentic_reasoners/core/`

#### ✗ Misplaced Implementation in Tests
- **Location:** `tests/crackfinder_agent.py`
- **Issue:** Full testing framework, not a test
- **Action:** Move to `src/system_agents/`

#### ✗ Duplicate Files
- **Location:** `src/system_agents/code_chunking_agent - 2.py`
- **Issue:** Duplicate with non-standard naming
- **Action:** Verify and remove duplicate

---

## Proposed Consolidation Actions

### ACTION 1: Consolidate Root-Level Core Directory
**Priority:** HIGH
**Complexity:** Medium
**Risk:** Low

**Current State:**
```
c:\dev\Mathematic agent based solver\
├── core\
│   └── reasoning_engine.py  (orphaned, SymPy-based)
├── src\
│   └── symbo_agentic_reasoners\
│       └── core\
│           ├── math_solver.py
│           ├── solver_engine.py
│           └── ... (other core modules)
```

**Proposed State:**
```
c:\dev\Mathematic agent based solver\
├── src\
│   └── symbo_agentic_reasoners\
│       └── core\
│           ├── reasoning_engine.py  (MOVED HERE)
│           ├── math_solver.py
│           ├── solver_engine.py
│           └── ... (other core modules)
```

**Steps:**
1. Move `core/reasoning_engine.py` to `src/symbo_agentic_reasoners/core/`
2. Update imports in any files referencing the old location
3. Remove empty `core/` root directory
4. Run tests to verify no import breakage

**Note on SymPy Issue:** The `reasoning_engine.py` file uses SymPy despite project philosophy. Consider:
- Converting to native modules, OR
- Creating an `archive/` subdirectory for legacy implementations, OR
- Deprecating it in favor of `solver_engine.py`

### ACTION 2: Move Misplaced System Agent
**Priority:** MEDIUM
**Complexity:** Low
**Risk:** Low

**Current State:**
```
tests\
├── crackfinder_agent.py  (implementation, not test)
src\
└── system_agents\
    └── (10 other agents)
```

**Proposed State:**
```
src\
└── system_agents\
    ├── crackfinder_agent.py  (MOVED HERE)
    └── (10 other agents)
tests\
└── (only actual test files remain)
```

**Steps:**
1. Move `tests/crackfinder_agent.py` to `src/system_agents/`
2. Update any imports from `tests.crackfinder_agent` to `symbo_agentic_reasoners.system_agents.crackfinder_agent`
3. Search for references in test files and update them
4. Run tests to verify no import breakage

### ACTION 3: Handle Duplicate System Agent
**Priority:** LOW
**Complexity:** Low
**Risk:** Very Low

**Current State:**
```
src\
└── system_agents\
    ├── code_chunking_agent.py
    ├── code_chunking_agent - 2.py  (DUPLICATE)
```

**Proposed State:**
```
src\
└── system_agents\
    └── code_chunking_agent.py  (single version)
```

**Steps:**
1. Compare `code_chunking_agent.py` and `code_chunking_agent - 2.py`
2. Identify which is the current version
3. Delete the old version
4. If there's a reason for the separation (e.g., different implementations), document it and rename appropriately
5. Run tests to ensure no breakage

### ACTION 4: Document Pilot Solver Status
**Priority:** LOW
**Complexity:** Low
**Risk:** Very Low

**Current State:**
```
src\symbo_agentic_reasoners\solvers\
└── pilot_solver.py  (Phase 1 "tracer bullet")
```

**Options:**
1. **Keep as-is** if it's used for backwards compatibility or testing
2. **Move to archive** if it's purely historical
3. **Deprecate** with a comment explaining the Phase 1 context
4. **Document** its relationship to `solver_engine.py` and `math_solver.py`

**Recommendation:** Add documentation clarifying:
- Purpose: Phase 1 verification of data pipeline
- Relationship to `solver_engine.py` (newer, direct solving)
- Relationship to `math_solver.py` (user-facing API with orchestration)

---

## Consolidation Summary Table

### Files to Move

| Current Location | New Location | Action | Priority | Risk |
|------------------|--------------|--------|----------|------|
| `core/reasoning_engine.py` | `src/symbo_agentic_reasoners/core/reasoning_engine.py` | MOVE | HIGH | LOW |
| `tests/crackfinder_agent.py` | `src/system_agents/crackfinder_agent.py` | MOVE | MEDIUM | LOW |
| `src/system_agents/code_chunking_agent - 2.py` | DELETE (or rename if intentional) | DELETE | LOW | VERY LOW |

### Files to Document

| File Path | Action | Priority |
|-----------|--------|----------|
| `src/symbo_agentic_reasoners/solvers/pilot_solver.py` | Document phase and purpose | LOW |
| `src/symbo_agentic_reasoners/core/math_solver.py` | Document vs solver_engine.py | LOW |
| `src/symbo_agentic_reasoners/core/solver_engine.py` | Document direct solving pipeline | LOW |

### New Directory Structure (After Consolidation)

```
c:\dev\Mathematic agent based solver\
├── scripts\                           (Entry points - CLI/GUI)
│   ├── math_solver.py                (CLI)
│   └── math_solver_ui.py             (GUI)
│
├── src\
│   ├── symbo_agentic_reasoners\
│   │   ├── core\                     (Framework & core solvers)
│   │   │   ├── bdi_agent.py          (Agent framework)
│   │   │   ├── math_solver.py        (User-facing API)
│   │   │   ├── solver_engine.py      (Direct solving)
│   │   │   ├── reasoning_engine.py   (Formal proofs - MOVED)
│   │   │   ├── orchestrator.py       (Task orchestration)
│   │   │   ├── native_symbolic.py    (NO SYMPY symbolic)
│   │   │   ├── native_calculus.py    (NO SYMPY calculus)
│   │   │   └── ... (other core modules)
│   │   │
│   │   ├── agents\                   (Agent implementations)
│   │   │   ├── specialists\          (Domain specialists)
│   │   │   │   ├── algebra\
│   │   │   │   ├── calculus\
│   │   │   │   ├── geometry\
│   │   │   │   ├── physics\
│   │   │   │   ├── statistics\
│   │   │   │   └── ... (other domains)
│   │   │   ├── supervisors\          (Supervisor agents)
│   │   │   ├── synthesis\            (Proof synthesis)
│   │   │   ├── provers\              (Logic provers)
│   │   │   └── base\                 (Base agent classes)
│   │   │
│   │   ├── solvers\                  (Solver implementations)
│   │   │   └── pilot_solver.py       (Legacy Phase 1)
│   │   │
│   │   ├── discovery\                (Autonomous exploration)
│   │   │   ├── curiosity_engine.py   (Idle exploration)
│   │   │   ├── imagination_engine.py (Background learning)
│   │   │   └── deep_search\          (Advanced proof search)
│   │   │
│   │   ├── infrastructure\           (Factory, registry, pooling)
│   │   ├── monitoring\               (Health & performance)
│   │   ├── optimization\             (Performance tuning)
│   │   ├── verification\             (Proof verification)
│   │   └── ... (other subsystems)
│   │
│   └── system_agents\                (System-level operations)
│       ├── crackfinder_agent.py      (Testing - MOVED)
│       ├── audit_agent.py            (Health audit)
│       ├── cleanup_agent.py          (Cleanup)
│       ├── code_chunking_agent.py    (Code analysis)
│       ├── documentation_agent.py    (Documentation)
│       ├── mathematical_cracker.py   (Math verification)
│       ├── script_decomposer.py      (Script analysis)
│       ├── security_stress_tester.py (Security testing)
│       └── structure_cataloger.py    (Structure analysis)
│
└── tests\                             (Test suite only)
    ├── test_*.py                     (Unit tests)
    ├── integration\                  (Integration tests)
    └── fixtures\                     (Test data)
```

---

## Import Path Updates Required

When consolidating, the following import paths will need to be updated:

### If Moving `reasoning_engine.py`:

**Old imports to find and update:**
```python
from core.reasoning_engine import ...
from core import reasoning_engine
import core.reasoning_engine as ...
```

**New import path:**
```python
from symbo_agentic_reasoners.core.reasoning_engine import ...
from symbo_agentic_reasoners.core import reasoning_engine
import symbo_agentic_reasoners.core.reasoning_engine as ...
```

**Files to check:**
- All files in `src/` that reference `core.reasoning_engine`
- Configuration files that might reference the module

### If Moving `crackfinder_agent.py`:

**Old imports to find and update:**
```python
from tests.crackfinder_agent import ...
from tests import crackfinder_agent
import tests.crackfinder_agent as ...
```

**New import path:**
```python
from symbo_agentic_reasoners.system_agents.crackfinder_agent import ...
from symbo_agentic_reasoners.system_agents import crackfinder_agent
import symbo_agentic_reasoners.system_agents.crackfinder_agent as ...
```

**Files to check:**
- Test files in `tests/`
- Any scripts that import `crackfinder_agent`
- Documentation that references the import path

---

## Consolidation Checklist

### Pre-Consolidation
- [ ] Backup complete `core/` directory
- [ ] Document current imports of `core/reasoning_engine.py`
- [ ] Document current imports of `tests/crackfinder_agent.py`
- [ ] Run full test suite to establish baseline
- [ ] Review `code_chunking_agent.py` vs `code_chunking_agent - 2.py`

### Execution Phase 1: Move reasoning_engine.py
- [ ] Copy `core/reasoning_engine.py` to `src/symbo_agentic_reasoners/core/`
- [ ] Search codebase for imports of old location
- [ ] Update imports to new location
- [ ] Delete original at `core/reasoning_engine.py`
- [ ] Run tests to verify no breakage

### Execution Phase 2: Move crackfinder_agent.py
- [ ] Copy `tests/crackfinder_agent.py` to `src/system_agents/`
- [ ] Search codebase for imports from old location
- [ ] Update imports in test files
- [ ] Delete original at `tests/crackfinder_agent.py`
- [ ] Run tests to verify no breakage

### Execution Phase 3: Handle Duplicate
- [ ] Compare `code_chunking_agent.py` and `code_chunking_agent - 2.py`
- [ ] Determine which is current
- [ ] Delete old version
- [ ] Document if intentional separation exists
- [ ] Run tests to verify

### Post-Consolidation
- [ ] Run complete test suite
- [ ] Verify all imports resolve correctly
- [ ] Check documentation for path references
- [ ] Document the consolidation
- [ ] Remove empty directories
- [ ] Update architecture documentation

---

## Risk Assessment

### Low-Risk Actions
- **Moving `reasoning_engine.py`**: Low risk if imports are properly updated
  - Contained module with limited external dependencies
  - Moving within same project maintains relative structure
  - Can be executed safely with comprehensive search/replace

- **Removing duplicate `code_chunking_agent - 2.py`**: Very low risk
  - Clear duplicate with unusual naming
  - Should verify but likely safe to delete

### Medium-Risk Actions
- **Moving `crackfinder_agent.py`**: Medium risk due to test dependencies
  - Must carefully update imports in test files
  - May have indirect references through test infrastructure
  - Requires verification that testing framework still works

### Mitigation Strategies
1. **Version Control**: Use git to track changes and enable easy rollback
2. **Testing**: Run full test suite before and after each change
3. **Documentation**: Document all changes for future reference
4. **Incremental**: Perform one action at a time, verify, then move to next

---

## Benefits of Consolidation

### Improved Organization
- **Single canonical location** for each type of component
- **Clearer mental model** of system architecture
- **Easier navigation** for new developers

### Reduced Confusion
- No more wondering "where do solvers go?"
- Clear distinction between test code and implementation
- Obvious location for new components

### Better Maintainability
- Centralized solving pipeline in `src/symbo_agentic_reasoners/core/`
- Specialist agents clearly organized by domain
- System agents grouped separately from domain logic

### Facilitated Development
- Faster to find related components
- Easier to understand dependencies
- Cleaner import paths

---

## Recommendations

### Immediate Actions (HIGH PRIORITY)
1. **Move `core/reasoning_engine.py` to core** - Eliminates orphaned directory
2. **Move `tests/crackfinder_agent.py` to system_agents** - Clarifies test vs. implementation boundary

### Short-term Actions (MEDIUM PRIORITY)
3. **Remove duplicate `code_chunking_agent - 2.py`** - Cleaner filesystem
4. **Document pilot_solver.py purpose** - Clarify Phase 1 vs. current system

### Documentation (LOW PRIORITY)
5. **Create architecture guide** explaining:
   - Solver pipeline: `math_solver.py` vs `solver_engine.py`
   - Agent hierarchy: specialists → supervisors → orchestrator
   - Discovery system: curiosity and imagination engines
   - System agents: maintenance and testing operations

---

## Appendix: Complete File Manifest

### Solver Files
- `src/symbo_agentic_reasoners/core/math_solver.py` - User-facing API
- `src/symbo_agentic_reasoners/core/solver_engine.py` - Direct solving pipeline
- `src/symbo_agentic_reasoners/solvers/pilot_solver.py` - Legacy Phase 1
- `src/symbo_agentic_reasoners/agents/specialists/algebra/equation_system_solver.py` - Specialist
- `src/symbo_agentic_reasoners/agents/specialists/calculus/ode_solver.py` - Specialist
- `core/reasoning_engine.py` - **ORPHANED, needs consolidation**
- `scripts/math_solver.py` - CLI entry point (correct location)
- `scripts/math_solver_ui.py` - GUI entry point (correct location)

### Engine Files
- `src/symbo_agentic_reasoners/core/solver_engine.py` - Problem solving
- `src/symbo_agentic_reasoners/discovery/curiosity_engine.py` - Idle exploration
- `src/symbo_agentic_reasoners/discovery/imagination_engine.py` - Background learning
- `src/symbo_agentic_reasoners/discovery/deep_search/prover_engine.py` - Proof search
- `src/symbo_agentic_reasoners/agents/specialists/statistics/bayesian_engine.py` - Probabilistic
- `core/reasoning_engine.py` - **ORPHANED**

### Agent Files (37 implemented agents)
- **Core Framework (6)**: BDI agent, communication, factory, pool, registry, monitor
- **Specialist Agents (37)**: Organized by domain in `agents/specialists/`
- **Supervisor Agents (10)**: Domain supervisors in `agents/supervisors/`
- **Synthesis Agents (4)**: In `agents/synthesis/`
- **Verification Agents (2)**: In `agents/provers/`
- **System Agents (10)**: In `src/system_agents/`
- **Misplaced (1)**: `tests/crackfinder_agent.py` should be in `system_agents/`

---

## Conclusion

The SYMBO_AGENTIC_REASONERS codebase is generally well-organized. The main consolidation requirements are:

1. **Eliminating orphaned root-level `core/` directory** containing `reasoning_engine.py`
2. **Moving misplaced implementation** (`crackfinder_agent.py`) from tests to system_agents
3. **Removing duplicate** system agent file with non-standard naming
4. **Documenting relationships** between solver entry points and engines

These changes will create a cleaner, more navigable codebase that accelerates development and reduces cognitive load for developers understanding the solver architecture.

**Estimated Effort:** 2-4 hours with testing
**Risk Level:** Low to Medium (primarily import path updates)
**Benefits:** High (improved clarity and maintainability)

---

*Report Generated by Codebase Architecture Analysis*
*For: Mathematic Agent Based Solver Project*
*Date: 2025-12-14*
