# Action Items: Second Opinion

## Priority 0 (Critical - Immediate Action Required)

- [ ] **Fix Missing Dependencies**
    - Add `scipy>=1.10.0` to `requirements.txt` and `pyproject.toml`.
    - Add `mpmath>=1.3.0` to `requirements.txt` and `pyproject.toml`.
    - **Rationale:** System crashes immediately in Phase 2 without these.

- [ ] **Eliminate Bare `except:` Clauses**
    - **Target Files:**
        - `symbo_agentic_reasoners_phase6/phase6_discovery_engine.py`
        - `symbo_agentic_reasoners_phase5/symbo/symbo_llm_core.py`
        - `symbo_agentic_reasoners_phase2/agents/algebra/polynomial_specialist.py`
        - `symbo_agentic_reasoners_phase1/solvers/pilot_solver.py`
    - **Action:** Replace `except:` with `except Exception as e:` and add `logging.exception("...")`.

- [ ] **Disable Silent Mock Fallbacks**
    - **Target:** `symbo_agentic_reasoners_phase0/memory/vector_database.py`
    - **Action:** Change default behavior to raise `ImportError` or `RuntimeError` if ChromaDB is missing, UNLESS a specific `--mock-mode` flag is passed.
    - **Rationale:** Prevent users from getting garbage results without knowing why.

## Priority 1 (High - Address Before Next Release)

- [ ] **Audit `except Exception` Blocks**
    - **Action:** Review all `except Exception` blocks (approx 50+) to ensuring they are not swallowing critical errors. Ensure they log tracebacks.

- [ ] **Segregate Mock Classes**
    - **Target:** `MockSupervisor`, `MockProver`, `MockVectorDB`
    - **Action:** Move these classes out of production files (`*_system.py`, `*_orchestrator.py`) and into a `tests/mocks` or `symbo_agentic_reasoners_phase0/mocks` module.
    - **Rationale:** Cleans up production code and prevents accidental usage.

- [ ] **Add Missing Visualization Dependencies**
    - Add `matplotlib` and `plotly` to `requirements.txt` (or optional group).

## Priority 2 (Medium - Technical Debt)

- [ ] **Standardize Logging**
    - Ensure all modules use the central `symbo_agentic_reasoners_logging` configuration rather than `print` statements or ad-hoc logging setup.

- [ ] **Type Hint Refinement**
    - Run `mypy` on the codebase and address top-level type errors, especially in Phase 0 and Phase 1.
