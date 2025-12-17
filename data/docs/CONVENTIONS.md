# SYMBO_AGENTIC_REASONERS - AI Assistant Conventions

> This file provides context for AI assistants (Blackbox, Copilot, Codeium, etc.)

## System Overview

**SYMBO_AGENTIC_REASONERS** (v0.6.0) is a multi-agent mathematical discovery engine featuring:
- BDI (Belief-Desire-Intention) cognitive architecture
- FIPA-ACL compliant agent communication
- Blackboard-based collaborative workspace
- OMDoc mathematical expression encoding
- Symbolic computation via SymPy
- Neural-symbolic reasoning (SymboLLM)

**License:** Apache 2.0 | **Authors:** Damien Davison & Michael Maillet

---

## Directory Structure

```
src/symbo_agentic_reasoners/    # ALL SOURCE CODE HERE
    core/                       # OMDoc, BDI, Blackboard, Orchestrator
    agents/                     # Agent hierarchy
        supervisors/            # Tier 2 domain coordinators
        specialists/            # Tier 3 task experts
    protocols/                  # FIPA-ACL messaging
    infrastructure/             # AMS, ACC, Directory Facilitator
    verification/               # Formal verification
    middleware/                 # Meta-cognitive (Phases 3-4)
    solvers/                    # SymPy wrappers
    discovery/                  # Discovery engine (Phase 6)
    optimization/               # Production optimization (Phase 5)
    utils/                      # Utilities and path constants

tests/                          # Test suite
    unit/                       # Unit tests
    integration/                # Integration tests
    fixtures/                   # Test fixtures

audit/                          # Audit infrastructure
    reports/                    # Generated audit reports
    phase1-6/                   # Per-phase audit modules

docs/                           # Documentation
    assessments/
        critical/               # Current assessments
        archive/                # Archived assessments
    architecture/               # Architecture docs
    api/                        # API docs
    MASTER_ARCHIVE/             # Legacy reference (READ-ONLY)

data/                           # Runtime data
    traces/
        thought/                # LLM reasoning traces
        audit/                  # Audit execution records
        test/                   # Test run logs
    output/                     # Temporary runtime output

scripts/                        # Utility scripts
```

---

## MANDATORY: File Archiving Protocol

When archiving assessments, audits, or versioned documents:

### Step 1: Copy to Archive
```
{ARCHIVE_DIR}/{FILENAME}_v{VERSION}_{YYYY-MM-DD}.md
```

Examples:
- `docs/assessments/archive/SYSTEM_ASSESSMENT_v2.1_2025-12-07.md`
- `audit/reports/archive/PHASE3_AUDIT_v1.0_2025-12-07.md`

### Step 2: DELETE Original
After confirming archive exists, delete the original file.

### Step 3: Verify
Ensure no duplicates remain.

### Archive Locations

| Content Type | Archive Location |
|--------------|------------------|
| Assessments | `docs/assessments/archive/` |
| Audit reports | `audit/reports/archive/` |
| Legacy code | `docs/MASTER_ARCHIVE/` (read-only reference) |

---

## Import Conventions

```python
# Core components
from symbo_agentic_reasoners.core import (
    OMObject, OMDocStatement, BDIAgent, Belief, Desire, Intention,
    Blackboard, BlackboardEntry
)

# Protocols
from symbo_agentic_reasoners.protocols import FIPAMessage, FIPAProtocol

# Infrastructure
from symbo_agentic_reasoners.infrastructure import (
    AgentManagementSystem, DirectoryFacilitator
)

# Agents (use full paths)
from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist
```

---

## Agent Hierarchy

```
Tier 1: Main Orchestrator
    |
    +-- Tier 2: Domain Supervisors
    |       |-- Algebra Supervisor
    |       |-- Calculus Supervisor
    |       |-- Linear Algebra Supervisor
    |       +-- Statistics Supervisor
    |
    +-- Tier 3: Task Specialists
            |-- Polynomial, Arithmetic, Number Theory (Algebra)
            |-- Differentiation, Integration, ODE, Series (Calculus)
            |-- Matrix Ops, Decomposition, Vector Space (LinAlg)
            +-- Bayesian, Distribution, Frequentist (Stats)
```

---

## Phase Architecture

| Phase | Name | Purpose |
|-------|------|---------|
| 0 | Infrastructure | OMDoc, BDI, FIPA-ACL, AMS, Blackboard |
| 1 | Cognitive Chassis | Orchestrator, Parser, Pilot Solver |
| 2 | Mathematical Workforce | Domain Supervisors + Specialists |
| 3 | Meta-Cognitive | Validation, Knowledge Mgmt, Hypothesis |
| 4 | Governance | Conflict Resolution, Failure Analysis |
| 5 | Optimization | Distillation, SymboLLM, Hybrid Deploy |
| 6 | Discovery | Conjecture, Deep Search, Formalization |

---

## Development Commands

```bash
# Run tests
python -m pytest tests/

# Quick verification
python scripts/quick_test.py

# Full audit
python scripts/run_all_audits.py

# Verify installation
python scripts/verify_installation.py
```

---

## Prohibited Actions

1. **NEVER** create code in legacy `symbo_agentic_reasoners_phase*` folders
2. **NEVER** leave duplicate files after archiving
3. **NEVER** put trace files in project root (use `data/traces/`)
4. **NEVER** use relative imports across packages
5. **NEVER** modify files in `docs/MASTER_ARCHIVE/` (read-only reference)

---

## Key Files

- Package init: `src/symbo_agentic_reasoners/__init__.py`
- Path constants: `src/symbo_agentic_reasoners/utils/__init__.py`
- Main orchestrator: `src/symbo_agentic_reasoners/core/orchestrator.py`
- Config: `pyproject.toml`
