# Quick Reference: Second Opinion

## Critical "Gotchas" for Developers

### 1. The "Mock Mode" Trap
- **Issue:** If you don't have `chromadb` installed, the system runs in "Mock Mode".
- **Symptom:** Vector search returns random/hash-based results that have **zero semantic meaning**.
- **Fix:** Install `chromadb` or explicitly check for `mock` status in your agent logic.

### 2. Missing Dependencies
- The system **will crash** if you try to use Phase 2 (Calculus/Algebra) without `scipy` installed.
- **Fix:** `pip install scipy mpmath` (until `requirements.txt` is updated).

### 3. The "Black Hole" Exception Handler
- **Issue:** Several key files use bare `except:` clauses.
- **Symptom:** The system hangs or behaves erratically, and **Ctrl+C does not work** because `KeyboardInterrupt` is caught.
- **Fix:** If the system hangs, you may need to kill the process from Task Manager/Activity Monitor.

## Key Locations to Watch

| Component | File | Issue |
| :--- | :--- | :--- |
| **Vector DB** | `symbo_agentic_reasoners_phase0/memory/vector_database.py` | Silent mock fallback |
| **Discovery** | `symbo_agentic_reasoners_phase6/phase6_discovery_engine.py` | Bare `except:` clauses |
| **Symbo** | `symbo_agentic_reasoners_phase5/symbo/symbo_llm_core.py` | Bare `except:` clauses |
| **Orchestrator** | `symbo_agentic_reasoners_phase3/orchestrator/phase3_orchestrator.py` | Uses `MockSupervisor` |

## Command Quick List

- **Run Tests (Fast):** `pytest tests/smoke_tests.py`
- **Run Full Audit:** `python scripts/run_all_audits.py`
- **Check Logs:** Logs are typically written to `logs/` (check `symbo_agentic_reasoners_logging.py` for config).
