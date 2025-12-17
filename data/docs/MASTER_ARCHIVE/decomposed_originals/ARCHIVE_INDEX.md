# Decomposed Originals Archive

**Created**: 2025-12-14
**Purpose**: Archive of monolithic scripts that have been decomposed into supervisor-specialist architectures.

---

## Decomposition Status

### 1. native_calculus.py (13,330 lines)
- **Status**: PARTIALLY DECOMPOSED - Original remains as fallback
- **Location**: `src/symbo_agentic_reasoners/core/native_calculus.py`
- **Decomposed To**: `src/symbo_agentic_reasoners/core/calculus/`
- **Architecture**: Supervisor-Specialist pattern
- **Modules Extracted**:
  - `calculus_supervisor.py` - Main coordinator
  - `ast_types.py` - Internal AST representation (Num, Sym, Add, Mul, Pow, Func)
  - `expression_parser.py` - String to AST parser
  - `validation.py` - Safety checks (depth & length limits)
  - `differentiation_specialist.py` - Derivatives engine (EXTRACTING)
  - `integration_specialist.py` - Antiderivatives engine (EXTRACTING)
  - `limit_specialist.py` - Limit evaluation (EXTRACTING)
- **Keep Original**: YES - serves as fallback during migration
- **Archive Original**: NO - still actively used for fallback imports

### 2. solver_engine.py (1,699 lines)
- **Status**: ANALYSIS COMPLETE - RECOMMENDED FOR DECOMPOSITION
- **Location**: `src/symbo_agentic_reasoners/core/solver_engine.py`
- **Recommended Structure**:
  ```
  solver_engine/
  ├── __init__.py
  ├── supervisor.py (SolverSupervisor)
  ├── schemas.py (SolveStatus, SolveResult)
  ├── specialists/
  │   ├── validation_specialist.py
  │   ├── classification_specialist.py
  │   ├── routing_specialist.py
  │   ├── native_fallback_specialist.py
  │   └── specialized_solvers/
  │       ├── diophantine_specialist.py
  │       ├── determinant_specialist.py
  │       ├── limit_native_specialist.py
  │       └── number_theory_series_specialist.py
  └── utils/
      ├── environment_manager.py
      └── statistics_tracker.py
  ```
- **Benefits**: Testability, maintainability, extensibility
- **Migration Steps**: See decomposition analysis report

### 3. orchestrator.py (1,261 lines)
- **Status**: ANALYSIS COMPLETE - DO NOT DECOMPOSE
- **Location**: `src/symbo_agentic_reasoners/core/orchestrator.py`
- **Reasoning**: Already appropriately designed as top-level coordinator
- **Architecture**: Supervisor pattern (delegates to domain supervisors)
- **Recommendation**: Keep as-is; it IS the top-level supervisor
- **Minor Refactoring Suggested**:
  - Extract configuration (domain mappings) to config files
  - Make SymPy fallback policy pluggable
  - Create specialist factory pattern

---

## Archival Guidelines

1. **Do NOT delete** working monolithic files until decomposition is complete
2. **Maintain backward compatibility** during migration
3. **Archive snapshots** only after full migration is verified
4. **Keep fallback imports** working during transition

---

## Related Documentation

- `src/symbo_agentic_reasoners/core/calculus/__init__.py` - Calculus package documentation
- `sonar files/calculus_decomposition_plan.md` - Detailed decomposition plan (if exists)
- Commit `f79796a` - NO SYMPY philosophy update

---

*Archive maintained by Claude Code automated agents*
