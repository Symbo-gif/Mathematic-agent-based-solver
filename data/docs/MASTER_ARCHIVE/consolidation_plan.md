# Solver, Engine, and Agent Consolidation Plan

## Executive Summary

Analysis of the codebase identified **84 total components** across solvers, engines, and agents with moderate technical debt. Key issues include naming inconsistencies, duplicate functionality, and architectural misalignment.

## Current Component Inventory

| Component Type | Count | Location | Status |
|---|---|---|---|
| Top-level Solvers | 3 | core/ + solvers/ | 2 active, 1 deprecated |
| Domain Engines | 6 | core/ + discovery/ | Healthy |
| Specialists | 53 | agents/specialists/ | Minor naming issues |
| Supervisors | 11 | agents/supervisors/ | Healthy |
| Synthesis | 4 | agents/synthesis/ | Healthy |
| Provers | 2 | agents/provers/ | Partial |
| System Agents | 5 | system_agents/ | Healthy |

## Critical Issues Identified

### 1. Solver Redundancy
Three parallel solving pathways exist:
- **SolverEngine** (core/solver_engine.py) - Direct, streamlined, native computation
- **MathSolver** (core/math_solver.py) - Full BDI pipeline with verification
- **PilotSolverAgent** (solvers/pilot_solver.py) - SymPy wrapper (DEPRECATED)

**Resolution**:
- MathSolver = Primary user API
- SolverEngine = Internal fallback/native path
- PilotSolverAgent = Remove in next cleanup

### 2. Naming Inconsistencies
Files named "_agent" that should be "_specialist":
- `frequentist_agent.py`
- `combinatorics_agent.py`
- `graph_theory_agent.py`
- `bayesian_engine.py` (should be bayesian_specialist.py)

### 3. Exploration Engine Duplication
CuriosityEngine and ImaginationEngine overlap in functionality:
- Both generate novel problems
- Both track exploration results
- ImaginationEngine extends CuriosityEngine

**Resolution**: Document that ImaginationEngine is the extended version with background scheduling.

### 4. Internal Engine Extraction
DifferentiationEngine, IntegrationEngine, LimitEngine are implementation details buried in native_calculus.py. Consider extracting for testability.

## Naming Convention (Established)

| Suffix | Meaning | Example |
|---|---|---|
| Engine | Low-level computational abstraction | DifferentiationEngine |
| Specialist | Domain expert BDI agent | PolynomialSpecialist |
| Supervisor | Routing/coordination agent | CalculusSupervisor |
| Agent | Generic autonomous BDI agent | BDIAgent |

## Recommended Solver Selection

| Use Case | Recommended Solver |
|---|---|
| User-facing API | MathSolver |
| Performance-critical native computation | SolverEngine |
| Testing/development | SolverEngine (faster) |
| Full verification required | MathSolver |
| Batch processing | SolverEngine with BatchProcessor |

## Consolidation Roadmap

### Phase 1: Critical Cleanup (Immediate)
- [x] Document solver selection guidelines
- [ ] Mark PilotSolverAgent as deprecated in docstring
- [ ] Add deprecation warnings to PilotSolverAgent

### Phase 2: Naming Standardization (Next Sprint)
- [ ] Rename frequentist_agent.py -> frequentist_specialist.py
- [ ] Rename combinatorics_agent.py -> combinatorics_specialist.py
- [ ] Rename graph_theory_agent.py -> graph_theory_specialist.py
- [ ] Rename bayesian_engine.py -> bayesian_specialist.py

### Phase 3: Architecture Alignment (Future)
- [ ] Refactor Discovery engines to use Blackboard + BDI patterns
- [ ] Register Discovery engines in Directory Facilitator
- [ ] Add Lean4 ProverEngine backend
- [ ] Extract internal engines from native_calculus.py

## Component Dependency Map

```
User Request
     │
     ▼
┌─────────────┐
│ MathSolver  │◄──── Primary API (full pipeline)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Orchestrator│
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│ Supervisors │────►│ SolverEngine │◄── Fallback (native computation)
└──────┬──────┘     └──────────────┘
       │
       ▼
┌─────────────┐
│ Specialists │
└─────────────┘
```

## Files Requiring Attention

### Deprecated (Remove)
- `src/symbo_agentic_reasoners/solvers/pilot_solver.py`

### Rename
- `src/symbo_agentic_reasoners/agents/specialists/discrete_math/frequentist_agent.py`
- `src/symbo_agentic_reasoners/agents/specialists/discrete_math/combinatorics_agent.py`
- `src/symbo_agentic_reasoners/agents/specialists/discrete_math/graph_theory_agent.py`
- `src/symbo_agentic_reasoners/agents/specialists/statistics/bayesian_engine.py`

### Document
- `src/symbo_agentic_reasoners/discovery/curiosity_engine.py`
- `src/symbo_agentic_reasoners/discovery/imagination_engine.py`

---
Generated: 2025-12-14
Status: In Progress
