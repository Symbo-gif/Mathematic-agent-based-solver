# SYMBO_AGENTIC_REASONERS Project Structure - AFTER Reorganization
## Completed: 2025-12-06

This document captures the project structure after the src-layout reorganization.

## New Directory Structure

```
Mathematic-agent-based-solver/
├── src/                            # SOURCE CODE (src-layout)
│   └── symbo_agentic_reasoners/                       # Main package
│       ├── __init__.py             # Package init (v0.6.0)
│       │
│       ├── core/                   # Core components
│       │   ├── __init__.py
│       │   ├── omdoc_schema.py     # OMDoc/OpenMath encoding
│       │   ├── bdi_agent.py        # BDI cognitive framework
│       │   ├── blackboard.py       # Shared memory workspace
│       │   ├── vector_database.py  # Long-term RAG memory
│       │   ├── orchestrator.py     # Main Orchestrator (Tier 1)
│       │   └── system.py           # System integration
│       │
│       ├── protocols/              # Communication protocols
│       │   ├── __init__.py
│       │   └── fipa_acl.py         # FIPA-ACL messaging
│       │
│       ├── infrastructure/         # Agent infrastructure
│       │   ├── __init__.py
│       │   ├── ams.py              # Agent Management System
│       │   ├── acc.py              # Agent Communication Channel
│       │   └── directory_facilitator.py
│       │
│       ├── agents/                 # Agent hierarchy
│       │   ├── __init__.py
│       │   ├── base/               # Base agent classes
│       │   │   ├── __init__.py
│       │   │   └── problem_analysis.py
│       │   ├── supervisors/        # Tier 2 Domain Supervisors
│       │   │   ├── __init__.py
│       │   │   ├── algebra_supervisor.py
│       │   │   ├── calculus_supervisor.py
│       │   │   ├── linalg_supervisor.py
│       │   │   └── stats_supervisor.py
│       │   └── specialists/        # Tier 3 Task Specialists
│       │       ├── algebra/
│       │       │   ├── arithmetic_specialist.py
│       │       │   ├── polynomial_specialist.py
│       │       │   └── number_theory_specialist.py
│       │       ├── calculus/
│       │       │   ├── differentiation_specialist.py
│       │       │   ├── integration_specialist.py
│       │       │   ├── ode_solver.py
│       │       │   └── series_specialist.py
│       │       ├── linear_algebra/
│       │       ├── discrete_math/
│       │       ├── statistics/
│       │       └── numerical/
│       │
│       ├── verification/           # Verification components
│       │   ├── __init__.py
│       │   └── verification_core.py
│       │
│       ├── middleware/             # Meta-cognitive middleware
│       │   ├── __init__.py
│       │   ├── hypothesis_generation.py
│       │   ├── knowledge_management.py
│       │   ├── precondition_validation.py
│       │   ├── conflict_resolution.py
│       │   ├── failure_analysis.py
│       │   └── meta_learning.py
│       │
│       ├── solvers/                # Mathematical solvers
│       │   ├── __init__.py
│       │   └── pilot_solver.py     # SymPy wrapper
│       │
│       ├── discovery/              # Discovery engine (Phase 6)
│       │   ├── __init__.py
│       │   ├── algorithm/          # Algorithm discovery
│       │   ├── conjecture/         # Conjecture generation
│       │   ├── deep_search/        # Deep search
│       │   └── formal/             # Formal knowledge
│       │
│       ├── optimization/           # Production optimization (Phase 5)
│       │   ├── __init__.py
│       │   ├── distillation/       # Thought trace distillation
│       │   ├── symbo/              # SymboLLM
│       │   └── evolutionary_flywheel.py
│       │
│       └── utils/                  # Utilities
│           ├── __init__.py         # Path constants
│           └── logging.py
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   ├── fixtures/                   # Test fixtures
│   └── mocks/                      # Mock objects
│
├── docs/                           # Documentation
│   ├── architecture/               # Architecture docs
│   ├── api/                        # API documentation
│   ├── assessments/                # Assessments
│   │   ├── archive/                # Archived assessments
│   │   └── critical/               # Current critical assessments
│   ├── BEFORE_STRUCTURE.md         # Pre-reorganization structure
│   ├── AFTER_STRUCTURE.md          # This file
│   └── DEVELOPER_GUIDE.md          # Developer guide
│
├── data/                           # Runtime data
│   ├── traces/                     # Agent traces
│   │   ├── thought/                # Thought traces
│   │   ├── audit/                  # Audit traces
│   │   └── test/                   # Test traces
│   └── output/                     # Runtime output
│
├── scripts/                        # Utility scripts
│   ├── quick_test.py
│   ├── run_all_audits.py
│   └── verify_installation.py
│
├── audit/                          # Audit infrastructure
│   └── [per-phase audit tools]
│
├── Reference Documents/            # Phase reference docs
│
├── pyproject.toml                  # Package configuration
├── requirements.txt                # Dependencies
└── .gitignore
```

## Key Changes from Original Structure

### 1. Src-Layout Pattern
- All source code now in `src/symbo_agentic_reasoners/` following PyPA recommendations
- Package discovery via `[tool.setuptools.packages.find] where = ["src"]`

### 2. Consolidated Phase Folders
- 7 `symbo_agentic_reasoners_phaseN/` folders merged into logical package structure
- Phase functionality now organized by concern, not development phase

### 3. Standardized Trace Locations
- `thought_traces/` → `data/traces/thought/`
- `audit_thought_traces/` → `data/traces/audit/`
- `test_thought_traces/` → `data/traces/test/`

### 4. Assessment Migration
- `Archive assessments/` → `docs/assessments/archive/`
- `critical assessments/` → `docs/assessments/critical/`

### 5. Clean Import Structure
```python
# New import pattern
from symbo_agentic_reasoners.core import OMObject, BDIAgent, Blackboard
from symbo_agentic_reasoners.protocols import FIPAMessage, create_request
from symbo_agentic_reasoners.infrastructure import DirectoryFacilitator
from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
```

## Package Configuration

```toml
[project]
name = "symbo_agentic_reasoners"
version = "0.6.0"

[tool.setuptools.packages.find]
where = ["src"]
include = ["symbo_agentic_reasoners*"]
```

## Backward Compatibility

The old `symbo_agentic_reasoners_phase*` modules remain in the repository for reference but are no longer part of the installed package. Tests and scripts should be updated to use the new import paths.
