# SYMBO_AGENTIC_REASONERS - Project Instructions for Claude

## What This System Is

**SYMBO_AGENTIC_REASONERS (Symbo)** is a multi-agent mathematical discovery engine using BDI (Belief-Desire-Intention) cognitive architecture. It autonomously solves mathematical problems through:
- Hierarchical agent collaboration (Tier 1-3)
- FIPA-ACL compliant messaging
- Blackboard-based shared workspace
- OMDoc mathematical expression encoding
- **NATIVE mathematical reasoning (NO SYMPY FALLBACKS)**

**Version:** 0.6.0 | **License:** Apache 2.0

---

## CRITICAL: NO SYMPY PHILOSOPHY

**This project is building a MATHEMATICAL REASONING ENTITY, not a SymPy wrapper.**

### Core Principles:
1. **NEVER add SymPy fallbacks** - if native engine can't solve it, extend the native engine
2. **Native calculus first** - differentiation, integration, limits via pattern recognition and mathematical rules
3. **Taylor series expansion** - fundamental technique for 0/0 indeterminate forms
4. **Pattern-based limit evaluation** - recognize mathematical forms, don't delegate to SymPy

### Native Calculus Engine (`core/native_calculus.py`):
- Pure Python symbolic calculus WITHOUT SymPy dependency
- Internal AST representation using dataclasses
- Pattern matching for rule application
- Handles: derivatives, integrals, limits, series

### When Something Fails:
1. **DO NOT** add `sp.limit()`, `sp.solve()`, or other SymPy fallbacks
2. **DO** identify the mathematical pattern that's missing
3. **DO** extend `native_calculus.py` with new pattern recognition
4. **DO** implement the mathematical reasoning natively

### Example - Correct Approach:
```python
# WRONG - SymPy fallback
if not native_success:
    return sp.limit(expr, var, point)  # NO!

# RIGHT - Extend native patterns
# Add to _try_taylor_expansion_limit():
# Pattern: (log(1+x) - log(1))/x → 1
match = re.match(rf'^\(\s*log\(1\+{var}\)\s*-\s*log\(1\)\s*\)/{var}$', expr)
if match:
    return '1'  # Native reasoning via Taylor: log(1+x) = x - x²/2 + ...
```

---

## File Organization Rules

### Source Code
- **Location:** `src/symbo_agentic_reasoners/`
- **Pattern:** src-layout (PyPA recommended)
- **DO NOT** put code in root or legacy phase folders

### Where File Types Go

| File Type | Location | Notes |
|-----------|----------|-------|
| Source code (.py) | `src/symbo_agentic_reasoners/` | Use existing subfolders: `core/`, `agents/`, `protocols/`, etc. |
| Tests | `tests/` | Mirror src structure: `unit/`, `integration/`, `fixtures/` |
| Audit reports | `audit/reports/` | Markdown format, timestamp naming |
| Audit code | `audit/phase{N}/` | Per-phase audit modules |
| Current assessments | `docs/assessments/critical/` | Use `first opinion/`, `second_opinion/`, `Third opinion/` |
| Architecture docs | `docs/architecture/` | System design documentation |
| API docs | `docs/api/` | API reference documentation |
| Thought traces | `data/traces/thought/` | LLM reasoning traces (JSON) |
| Audit traces | `data/traces/audit/` | Audit execution records |
| Test traces | `data/traces/test/` | Test run logs |
| Runtime output | `data/output/` | Temporary runtime data |
| Utility scripts | `scripts/` | Helper tools, not core logic |

---

## CRITICAL: Archiving Protocol

### When Archiving Assessments or Audits:

1. **Copy** to archive with version + timestamp:
   ```
   docs/assessments/archive/ASSESSMENT_v{VERSION}_{YYYY-MM-DD}.md
   ```

2. **DELETE the original file** after successful archive copy

3. **Naming convention:**
   - `SYSTEM_ASSESSMENT_v2.1_2025-12-06.md`
   - `CRITICAL_AUDIT_v1.0_2025-12-07.md`
   - `PHASE3_REVIEW_v1.2_2025-12-07.md`

### Archive Locations:

| Content Type | Archive Location |
|--------------|------------------|
| Assessments | `docs/assessments/archive/` |
| Audit reports | `audit/reports/archive/` (create if needed) |
| Legacy phase code | `docs/MASTER_ARCHIVE/symbo_agentic_reasoners_phase{N}/` (read-only reference) |
| Historical traces | `docs/MASTER_ARCHIVE/test_thought_traces/` |

### DO:
- Always archive before deleting
- Include version number in archive filename
- Include date stamp in archive filename
- Verify archive exists before deleting original

### DON'T:
- Leave duplicate files in both locations
- Archive without version/timestamp
- Delete without archiving first

---

## Import Conventions

```python
# Core components
from symbo_agentic_reasoners.core import (
    OMObject, BDIAgent, Blackboard, BlackboardEntry
)

# Protocols
from symbo_agentic_reasoners.protocols import FIPAMessage, FIPAProtocol

# Infrastructure
from symbo_agentic_reasoners.infrastructure import AgentManagementSystem

# Agents - use full paths
from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist
```

---

## Agent Hierarchy

```
Tier 1: Main Orchestrator (central coordinator)
    |
Tier 2: Domain Supervisors
    |-- Algebra Supervisor
    |-- Calculus Supervisor
    |-- Linear Algebra Supervisor
    |-- Statistics Supervisor
    |
Tier 3: Task Specialists
    |-- Polynomial, Differentiation, Matrix Ops, Bayesian, etc.
```

---

## Phase Structure (Reference)

| Phase | Purpose | Key Components |
|-------|---------|----------------|
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

## Key Files Reference

- **Entry point:** `src/symbo_agentic_reasoners/__init__.py`
- **Path constants:** `src/symbo_agentic_reasoners/utils/__init__.py`
- **Main orchestrator:** `src/symbo_agentic_reasoners/core/orchestrator.py`
- **Blackboard:** `src/symbo_agentic_reasoners/core/blackboard.py`
- **Config:** `pyproject.toml` (package metadata, deps, tools)

### Native Mathematical Reasoning (CRITICAL):
- **Native calculus:** `src/symbo_agentic_reasoners/core/native_calculus.py` - derivatives, integrals, limits, series
- **Solver engine:** `src/symbo_agentic_reasoners/core/solver_engine.py` - routes problems to specialists
- **Input normalizer:** `src/symbo_agentic_reasoners/core/input_normalizer.py` - parses mathematical notation
- **Number theory native:** `src/symbo_agentic_reasoners/core/number_theory_native.py` - primes, totient, Mobius

---

## Notes for AI Assistants

1. **NEVER ADD SYMPY FALLBACKS** - This is a mathematical reasoning entity, not a SymPy wrapper
2. **Extend native_calculus.py** when patterns are missing - use Taylor series, L'Hôpital's rule, pattern recognition
3. **Never create files in legacy phase folders** - they are read-only reference
4. **Always use full import paths** from `symbo_agentic_reasoners.*`
5. **Test changes** with `python -m pytest tests/` before committing
6. **Document significant changes** in appropriate docs folder
7. **Trace outputs** go to `data/traces/`, not project root

### Current Test Status:
- **3607 tests passing** (as of 2025-12-13)
- All limits computed natively via pattern recognition
- All derivatives/integrals via native calculus engine
