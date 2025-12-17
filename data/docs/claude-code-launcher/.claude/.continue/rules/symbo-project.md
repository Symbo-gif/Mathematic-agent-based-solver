# SYMBO_AGENTIC_REASONERS Project Rules

## System Description
Multi-agent mathematical discovery engine (v0.6.0) with:
- BDI (Belief-Desire-Intention) cognitive architecture
- FIPA-ACL compliant agent communication
- Blackboard-based collaborative problem solving
- OMDoc mathematical expression encoding
- 6-phase hierarchical agent system

## Directory Structure

### Source Code Location
ALL source code: `src/symbo_agentic_reasoners/`

Subfolders:
- `core/` - OMDoc, BDI, Blackboard, Orchestrator
- `agents/` - Agent hierarchy (supervisors/, specialists/)
- `protocols/` - FIPA-ACL communication
- `infrastructure/` - AMS, ACC, Directory Facilitator
- `verification/` - Formal verification
- `middleware/` - Meta-cognitive (Phases 3-4)
- `solvers/` - SymPy wrappers
- `discovery/` - Discovery engine (Phase 6)
- `optimization/` - Production optimization (Phase 5)

### Other Locations
- Tests: `tests/{unit,integration,fixtures}/`
- Audit reports: `audit/reports/`
- Current assessments: `docs/assessments/critical/`
- Archived assessments: `docs/assessments/archive/`
- Traces: `data/traces/{thought,audit,test}/`
- Scripts: `scripts/`
- Legacy reference (READ-ONLY): `docs/MASTER_ARCHIVE/`

## MANDATORY: Archiving Protocol

When archiving ANY assessment, audit, or versioned document:

1. **COPY** to appropriate archive with naming: `{NAME}_v{VERSION}_{YYYY-MM-DD}.md`
2. **DELETE** original file after confirming archive exists
3. **NEVER** leave duplicates in both locations

Example:
```
Original: docs/assessments/critical/SYSTEM_ASSESSMENT.md
Archive:  docs/assessments/archive/SYSTEM_ASSESSMENT_v2.1_2025-12-07.md
Action:   Delete original after archiving
```

## Import Conventions
```python
from symbo_agentic_reasoners.core import OMObject, BDIAgent, Blackboard
from symbo_agentic_reasoners.protocols import FIPAMessage
from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
```

## Agent Tiers
- Tier 1: Main Orchestrator (coordinator)
- Tier 2: Domain Supervisors (Algebra, Calculus, LinAlg, Stats)
- Tier 3: Task Specialists (domain-specific operations)

## Phases
0: Infrastructure | 1: Cognitive Chassis | 2: Math Workforce
3: Meta-Cognitive | 4: Governance | 5: Optimization | 6: Discovery

## Testing
```bash
python -m pytest tests/
python scripts/quick_test.py
python scripts/run_all_audits.py
```

## Prohibitions
- NO code in legacy `symbo_agentic_reasoners_phase*` folders
- NO duplicate files after archiving
- NO traces in project root (use `data/traces/`)
- NO relative imports across packages
