# GitHub Copilot Instructions for SYMBO_AGENTIC_REASONERS

## Project Context
Multi-agent mathematical discovery engine (v0.6.0) with BDI cognitive architecture, FIPA-ACL messaging, and symbolic computation via SymPy.

## Code Location
ALL source code goes in `src/symbo_agentic_reasoners/`

Submodules:
- `core/` - OMDoc, BDI, Blackboard, Orchestrator
- `agents/supervisors/` - Tier 2 domain coordinators
- `agents/specialists/` - Tier 3 task experts
- `protocols/` - FIPA-ACL messaging
- `infrastructure/` - AMS, ACC, DF
- `verification/` - Formal verification
- `middleware/` - Meta-cognitive layers
- `solvers/` - SymPy wrappers
- `discovery/` - Discovery engine
- `optimization/` - Production optimization

## Import Pattern
```python
from symbo_agentic_reasoners.core import OMObject, BDI Agent, Blackboard
from symbo_agentic_reasoners.protocols import FIPAMessage
from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
```

## File Destinations
- Source: `src/symbo_agentic_reasoners/`
- Tests: `tests/`
- Audits: `audit/reports/`
- Assessments: `docs/assessments/critical/` or `archive/`
- Traces: `data/traces/{thought,audit,test}/`
- Legacy (DO NOT MODIFY): `docs/MASTER_ARCHIVE/`

## Archiving Rule
When archiving any document:
1. Copy to archive: `{NAME}_v{VERSION}_{YYYY-MM-DD}.md`
2. Delete original after archive confirmed
3. Never leave duplicates

## Agent Hierarchy
Tier 1: Main Orchestrator
Tier 2: Domain Supervisors (Algebra, Calculus, LinAlg, Stats)
Tier 3: Task Specialists

## Testing
```bash
python -m pytest tests/
python scripts/quick_test.py
```
