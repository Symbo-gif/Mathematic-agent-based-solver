# SYMBO_AGENTIC_REASONERS System - Quick Reference Guide (Third Opinion)

**Date:** 2025-12-06  
**Purpose:** Fast lookup for critical issues, fixes, and verification steps  
**Audience:** Developers, DevOps, QA Engineers

---

## 🚨 CRITICAL ISSUES AT A GLANCE

### The Big Three (P0 - BLOCKING)

| # | Issue | Impact | Quick Fix | Time |
|---|-------|--------|-----------|------|
| 1 | **Missing scipy/mpmath** | Phase 2 crashes | Add to requirements | 2h |
| 2 | **Mock data as real results** | False results returned | Remove mocks or fail fast | 16h |
| 3 | **Bare except clauses (25+)** | Errors hidden, can't debug | Replace with specific types | 11h |

**Total P0 Effort:** ~29 hours (4 days)  
**Blocking:** ALL deployment

---

## 📋 Quick Checklist

### Before ANY Deployment
```bash
# 1. Check dependencies
pip install -e .
python -c "import scipy, mpmath; print('OK')"

# 2. Verify no mock mode
grep -r "MockSupervisor\|_mock_storage\|_simulate_student" symbo_agentic_reasoners_phase*/

# 3. Check for bare excepts
grep -r "except:" symbo_agentic_reasoners_phase*/ | grep -v "except Exception"

# 4. Run health checks
python -c "from symbo_agentic_reasoners_phase2.phase2_system import Phase2System; s=Phase2System(); print(s.health_check())"
```

**If ANY check fails → DO NOT DEPLOY**

---

## 🔧 Quick Fixes

### Fix #1: Add Missing Dependencies (2 hours)

**File:** `pyproject.toml`

```toml
# ADD THESE LINES:
dependencies = [
    "sympy>=1.12,<2.0",
    "numpy>=1.24.0,<2.0",
    "scipy>=1.10.0",      # ← ADD
    "mpmath>=1.3.0",      # ← ADD
]
```

**File:** `requirements.txt`

```txt
sympy>=1.12,<2.0
numpy>=1.24.0,<2.0
scipy>=1.10.0          # ← ADD
mpmath>=1.3.0          # ← ADD
```

**Verify:**
```bash
pip install -e .
python -c "import scipy; import mpmath; print('Dependencies OK')"
```

---

### Fix #2: Remove Mock Data (16 hours)

#### 2a. VectorDatabase (4h)

**File:** `symbo_agentic_reasoners_phase0/memory/vector_database.py`

```python
# REMOVE THESE:
# Line 140: self._mock_storage: Dict[str, VectorEntry] = {}
# Line 349-366: def _generate_mock_embedding(...)

# ADD THIS at line 120:
def __init__(self, persist_directory: str = "./symbo_agentic_reasoners_vector_store"):
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise RuntimeError(
            "ChromaDB and sentence-transformers required.\n"
            "Install: pip install chromadb sentence-transformers"
        )
    # ... rest of init
```

#### 2b. MockSupervisor (3h)

**File:** `symbo_agentic_reasoners_phase3/orchestrator/phase3_orchestrator.py`

```python
# DELETE LINES 520-536 (entire MockSupervisor class)

# UPDATE _discover_supervisor() at line 510:
def _discover_supervisor(self, domain_tag: str):
    service_type = f"math.{domain_tag.lower()}"
    if self.df:
        results = self.df.search(service_type=service_type)
        if results:
            return results[0]
    return None  # ← Return None, not MockSupervisor

# UPDATE process() to handle None:
supervisor = self._discover_supervisor(domain_tag)
if not supervisor:
    return {
        'status': 'ERROR',
        'code': 'NO_SUPERVISOR',
        'message': f'No supervisor for domain: {domain_tag}'
    }
```

#### 2c. Simulated Student (2h)

**File:** `symbo_agentic_reasoners_phase5/phase5_system.py`

```python
# DELETE LINES 623-634 (_simulate_student_response method)

# UPDATE route_query() around line 580:
if not self.symbo_available:
    return {
        'status': 'ERROR',
        'message': 'Symbo student model not available',
        'suggestion': 'Install torch and train model'
    }
```

#### 2d. MockProver (3h)

**File:** `symbo_agentic_reasoners_phase6/deep_search/prover_engine.py`

```python
# DELETE LINES 50-111 (entire MockProver class)

# UPDATE ProverEngine.__init__():
def __init__(self, prover_backend: str = "lean"):
    if prover_backend == "mock":
        raise ValueError("Mock prover not allowed in production")
    # ... rest of init
```

---

### Fix #3: Replace Bare Excepts (11 hours)

**Pattern to find:**
```bash
grep -n "except:" symbo_agentic_reasoners_phase*/*.py | grep -v "except Exception"
```

**Replace with:**

```python
# BEFORE (WRONG):
try:
    result = operation()
except:
    return None

# AFTER (CORRECT):
try:
    result = operation()
except (ValueError, TypeError, KeyError) as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    return None
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise
```

**Files to fix (25+ instances):**
- `symbo_agentic_reasoners_phase1/solvers/pilot_solver.py:266`
- `symbo_agentic_reasoners_phase1/phase1_system.py:262`
- `symbo_agentic_reasoners_phase2/agents/algebra/polynomial_specialist.py:278`
- `symbo_agentic_reasoners_phase2/agents/calculus/integration_specialist.py:285, 297`
- `symbo_agentic_reasoners_phase5/symbo/nano_tensor.py:231, 275, 294, 313, 332`
- `symbo_agentic_reasoners_phase5/symbo/symbo_llm_core.py:317`

---

## 🧪 Quick Tests

### Test #1: Dependencies Installed
```bash
python -c "
import sympy
import numpy
import scipy
import mpmath
print('✓ All core dependencies installed')
"
```

### Test #2: No Mock Mode Active
```bash
python -c "
from symbo_agentic_reasoners_phase0.memory.vector_database import VectorDatabase
try:
    vdb = VectorDatabase()
    if hasattr(vdb, '_mock_storage'):
        print('✗ FAIL: Mock mode still active')
        exit(1)
    print('✓ No mock mode')
except RuntimeError as e:
    if 'ChromaDB' in str(e):
        print('✓ Fails fast without ChromaDB (correct)')
    else:
        raise
"
```

### Test #3: Phase 2 Health Check
```bash
python -c "
from symbo_agentic_reasoners_phase2.phase2_system import Phase2System
system = Phase2System()
system.start()
health = system.health_check()
if health['overall']:
    print('✓ Phase 2 healthy')
else:
    print('✗ FAIL: Phase 2 unhealthy')
    print(health)
    exit(1)
system.shutdown()
"
```

### Test #4: Exception Handling
```bash
# Should NOT find any bare excepts in production code
if grep -r "except:" symbo_agentic_reasoners_phase*/ | grep -v "except Exception" | grep -v "test_" | grep -v ".pyc"; then
    echo "✗ FAIL: Bare except clauses found"
    exit 1
else
    echo "✓ No bare except clauses"
fi
```

---

## 📊 System Status Dashboard

### Quick Status Check
```bash
#!/bin/bash
echo "=== SYMBO_AGENTIC_REASONERS System Status ==="
echo ""

# Dependencies
echo "1. Dependencies:"
python -c "import scipy, mpmath" 2>/dev/null && echo "  ✓ scipy, mpmath" || echo "  ✗ MISSING scipy/mpmath"

# Mock mode
echo "2. Mock Mode:"
grep -q "_mock_storage\|MockSupervisor\|_simulate_student" symbo_agentic_reasoners_phase*/*.py && echo "  ✗ Mock code present" || echo "  ✓ No mock code"

# Bare excepts
echo "3. Exception Handling:"
BARE_EXCEPTS=$(grep -r "except:" symbo_agentic_reasoners_phase*/ 2>/dev/null | grep -v "except Exception" | grep -v "test_" | wc -l)
if [ $BARE_EXCEPTS -eq 0 ]; then
    echo "  ✓ No bare excepts"
else
    echo "  ✗ $BARE_EXCEPTS bare except clauses"
fi

# Health check
echo "4. System Health:"
python -c "from symbo_agentic_reasoners_phase1.phase1_system import Phase1System; s=Phase1System(); h=s.health_check(); print('  ✓ Healthy' if h['overall'] else '  ✗ Unhealthy'); s.shutdown()" 2>/dev/null || echo "  ✗ Cannot start"

echo ""
echo "=== End Status ==="
```

---

## 🎯 Priority Matrix

### What to Fix First

```
┌─────────────────────────────────────────────────────────┐
│ CRITICAL (Fix Today)                                    │
├─────────────────────────────────────────────────────────┤
│ 1. Add scipy/mpmath to requirements         [2 hours]  │
│ 2. Remove MockSupervisor                    [3 hours]  │
│ 3. Fix bare excepts in Phase 1              [2 hours]  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ HIGH (Fix This Week)                                    │
├─────────────────────────────────────────────────────────┤
│ 4. Remove VectorDatabase mock mode          [4 hours]  │
│ 5. Remove simulated student                 [2 hours]  │
│ 6. Fix bare excepts in Phase 2              [4 hours]  │
│ 7. Update ChromaDB API                      [2 hours]  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ MEDIUM (Fix This Month)                                 │
├─────────────────────────────────────────────────────────┤
│ 8. Add integration tests                   [16 hours]  │
│ 9. Standardize error handling              [24 hours]  │
│ 10. Implement sandbox timeout               [8 hours]  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Quick Diagnostics

### Problem: "ImportError: No module named scipy"
**Cause:** Missing dependency  
**Fix:** Add scipy to requirements (Fix #1)  
**Time:** 2 hours

### Problem: "SUCCESS" but no actual result
**Cause:** Mock mode active  
**Fix:** Remove mock components (Fix #2)  
**Time:** 16 hours

### Problem: System hangs, can't Ctrl+C
**Cause:** Bare except catching KeyboardInterrupt  
**Fix:** Replace bare excepts (Fix #3)  
**Time:** 11 hours

### Problem: "chroma_db_impl is deprecated"
**Cause:** Old ChromaDB API  
**Fix:** Update to PersistentClient  
**Time:** 2 hours

### Problem: Tests pass but production fails
**Cause:** Tests use mocks, not real components  
**Fix:** Add integration tests  
**Time:** 16 hours

---

## 📞 Emergency Contacts

### Critical Issues (P0)
- **Escalate to:** Tech Lead
- **Response time:** 1 hour
- **Contact:** [Add contact info]

### High Priority (P1)
- **Escalate to:** Project Manager
- **Response time:** 4 hours
- **Contact:** [Add contact info]

---

## 🔗 Related Documents

- **Full Assessment:** `system_Assessment.md`
- **Detailed Action Items:** `action_item.md`
- **First Opinion:** `../first opinion/SYSTEM_ASSESSMENT.md`
- **Second Opinion:** `../second_opinion/system_Assessment.md`
- **Archive:** `../../Archive assessments/CRITICAL_ASSESSMENT_v2.1_2025-12-06.md`

---

## 📝 Quick Commands Reference

### Installation
```bash
# Clean install
pip uninstall -y symbo_agentic_reasoners
pip install -e .

# With all dependencies
pip install -e ".[full]"

# Development mode
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific phase
pytest tests/test_phase2.py

# Run with coverage
pytest --cov=symbo_agentic_reasoners_phase0 --cov=symbo_agentic_reasoners_phase1 tests/

# Run integration tests (when added)
pytest -m integration tests/integration/
```

### Health Checks
```bash
# Phase 0
python -c "from symbo_agentic_reasoners_phase0.phase0_system import Phase0System; s=Phase0System(); s.start(); print(s.health_check()); s.shutdown()"

# Phase 1
python -c "from symbo_agentic_reasoners_phase1.phase1_system import Phase1System; s=Phase1System(); s.start(); print(s.health_check()); s.shutdown()"

# Phase 2
python -c "from symbo_agentic_reasoners_phase2.phase2_system import Phase2System; s=Phase2System(); s.start(); print(s.health_check()); s.shutdown()"
```

### Code Quality
```bash
# Format code
black symbo_agentic_reasoners_phase*/

# Lint code
ruff check symbo_agentic_reasoners_phase*/

# Type check
mypy symbo_agentic_reasoners_phase*/

# Find bare excepts
grep -r "except:" symbo_agentic_reasoners_phase*/ | grep -v "except Exception" | grep -v ".pyc"

# Find mock code
grep -r "Mock\|mock\|simulate" symbo_agentic_reasoners_phase*/ | grep -v ".pyc" | grep -v "test_"
```

---

## ⚡ One-Liner Fixes

### Add scipy/mpmath
```bash
echo -e "scipy>=1.10.0\nmpmath>=1.3.0" >> requirements.txt && pip install scipy mpmath
```

### Check for mocks
```bash
grep -r "MockSupervisor\|_mock_storage\|_simulate_student\|MockProver" symbo_agentic_reasoners_phase*/*.py
```

### Count bare excepts
```bash
grep -r "except:" symbo_agentic_reasoners_phase*/ | grep -v "except Exception" | grep -v "test_" | wc -l
```

### Verify installation
```bash
python -c "import sympy, numpy, scipy, mpmath; print('All dependencies OK')"
```

---

## 🎓 Learning Resources

### Understanding the Issues

**Mock Data Problem:**
- Mock components return fake results with SUCCESS status
- Users can't distinguish real from fake results
- Can lead to false mathematical conclusions

**Bare Except Problem:**
```python
try:
    compute()
except:  # ← Catches EVERYTHING including Ctrl+C
    pass
```
This catches SystemExit, KeyboardInterrupt, and hides all bugs.

**Missing Dependencies:**
- Code imports scipy but requirements.txt doesn't list it
- System appears to work until runtime crash
- Phase 2 completely non-functional without scipy

---

## 📈 Progress Tracking

### Daily Checklist
```
Day 1:
[ ] Add scipy/mpmath to requirements
[ ] Test Phase 2 with real scipy
[ ] Remove MockSupervisor
[ ] Fix 5 bare except clauses

Day 2:
[ ] Remove VectorDatabase mock mode
[ ] Remove simulated student
[ ] Fix 10 more bare except clauses
[ ] Update ChromaDB API

Day 3:
[ ] Remove MockProver
[ ] Fix remaining bare excepts
[ ] Add integration test structure
[ ] Run full test suite

Day 4:
[ ] Complete integration tests
[ ] Verify all fixes
[ ] Update documentation
[ ] Deploy to staging
```

---

**End of Quick Reference**

*Keep this document handy for fast issue resolution*  
*Last Updated: 2025-12-06*
