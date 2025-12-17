# SYMBO_AGENTIC_REASONERS System - Action Items (Third Opinion)

**Date:** 2025-12-06  
**Priority System:** P0 (Critical/Blocking) → P1 (High) → P2 (Medium) → P3 (Low)  
**Status Tracking:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

---

## P0 - CRITICAL BLOCKERS (Must Fix Before ANY Deployment)

### P0-1: Add Missing Core Dependencies 🔴

**Issue:** scipy and mpmath are used in production but not listed in requirements  
**Impact:** Phase 2 completely non-functional, system crashes at runtime  
**Files Affected:** 7 files use scipy, 1 file uses mpmath

**Action Items:**
- [ ] Update `pyproject.toml` dependencies section:
  ```toml
  dependencies = [
      "sympy>=1.12,<2.0",
      "numpy>=1.24.0,<2.0",
      "scipy>=1.10.0",      # ADD
      "mpmath>=1.3.0",      # ADD
  ]
  ```
- [ ] Update `requirements.txt`:
  ```
  sympy>=1.12,<2.0
  numpy>=1.24.0,<2.0
  scipy>=1.10.0
  mpmath>=1.3.0
  ```
- [ ] Update `requirements-full.txt` with same additions
- [ ] Test installation: `pip install -e .`
- [ ] Verify Phase 2 health check passes
- [ ] Run integration tests with real scipy

**Estimated Effort:** 2 hours  
**Owner:** DevOps/Build Engineer  
**Verification:** Phase 2 system starts and executes matrix operations successfully

---

### P0-2: Eliminate Mock Data in Production Paths 🔴

**Issue:** 6 mock/simulation components return fake results with SUCCESS status  
**Impact:** Users receive false results, data integrity violation, potential fraud

**Decision Required:** Choose remediation strategy:
- **Option A:** Fail fast (recommended)
- **Option B:** Explicit mock mode with warnings
- **Option C:** Remove mock code entirely

#### P0-2a: VectorDatabase Mock Mode

**File:** `symbo_agentic_reasoners_phase0/memory/vector_database.py`  
**Lines:** 140, 349-366

**Action Items:**
- [ ] **Option A (Recommended):** Add fail-fast check:
  ```python
  def __init__(self, persist_directory: str = "./symbo_agentic_reasoners_vector_store"):
      try:
          import chromadb
          from chromadb.config import Settings
      except ImportError:
          raise RuntimeError(
              "ChromaDB is required for production use.\n"
              "Install with: pip install chromadb sentence-transformers\n"
              "Or use --mock flag for testing only."
          )
  ```
- [ ] Remove `_mock_storage` dictionary
- [ ] Remove `_mock_retrieve()` method
- [ ] Remove `_generate_mock_embedding()` method
- [ ] Update tests to use explicit mock fixtures

**Estimated Effort:** 4 hours  
**Owner:** Phase 0 Team

#### P0-2b: MockSupervisor in Orchestrator

**File:** `symbo_agentic_reasoners_phase3/orchestrator/phase3_orchestrator.py`  
**Lines:** 520-536

**Action Items:**
- [ ] Remove `MockSupervisor` class entirely
- [ ] Update `_discover_supervisor()` to return None if not found
- [ ] Update `process()` to return explicit ERROR:
  ```python
  if not supervisor:
      return {
          'status': 'ERROR',
          'code': 'NO_SUPERVISOR',
          'message': f'No supervisor available for domain: {domain_tag}',
          'conversation_id': conversation_id
      }
  ```
- [ ] Move MockSupervisor to `tests/mocks/mock_supervisor.py`
- [ ] Update tests to import from test fixtures

**Estimated Effort:** 3 hours  
**Owner:** Phase 3 Team

#### P0-2c: Simulated Student Responses

**File:** `symbo_agentic_reasoners_phase5/phase5_system.py`  
**Lines:** 623-634

**Action Items:**
- [ ] Remove `_simulate_student_response()` method
- [ ] Update routing logic to fail if Symbo not available:
  ```python
  if not self.symbo_available:
      return {
          'status': 'ERROR',
          'message': 'Symbo student model not available',
          'suggestion': 'Install torch and train student model'
      }
  ```
- [ ] Add startup check for Symbo availability
- [ ] Document Symbo as required for Phase 5

**Estimated Effort:** 2 hours  
**Owner:** Phase 5 Team

#### P0-2d: MockProver in Deep Search

**File:** `symbo_agentic_reasoners_phase6/deep_search/prover_engine.py`  
**Lines:** 50-111

**Action Items:**
- [ ] Remove `MockProver` class
- [ ] Update `ProverEngine.__init__()` to require real prover:
  ```python
  def __init__(self, prover_backend: str = "lean"):
      if prover_backend == "mock":
          raise ValueError(
              "Mock prover not allowed in production. "
              "Use 'lean', 'coq', or 'isabelle'."
          )
  ```
- [ ] Move MockProver to `tests/mocks/mock_prover.py`
- [ ] Update all tests to use explicit mock fixtures

**Estimated Effort:** 3 hours  
**Owner:** Phase 6 Team

#### P0-2e: Mock Embeddings

**Files:** 
- `symbo_agentic_reasoners_phase0/memory/vector_database.py:349`
- `symbo_agentic_reasoners_phase6/formal_knowledge_integration/vector_database_updater.py:275`

**Action Items:**
- [ ] Remove `_generate_mock_embedding()` methods
- [ ] Require sentence-transformers for embeddings:
  ```python
  try:
      from sentence_transformers import SentenceTransformer
      self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
  except ImportError:
      raise RuntimeError(
          "sentence-transformers required for embeddings.\n"
          "Install with: pip install sentence-transformers"
      )
  ```
- [ ] Update tests to use real embeddings or explicit mocks

**Estimated Effort:** 4 hours  
**Owner:** Phase 0 & Phase 6 Teams

**Total P0-2 Effort:** 16 hours  
**Verification:** No mock/simulated results returned with SUCCESS status

---

### P0-3: Fix All Bare Except Clauses 🔴

**Issue:** 25+ bare `except:` clauses catch SystemExit, KeyboardInterrupt, hide bugs  
**Impact:** System cannot be stopped, errors hidden, debugging impossible

**Action Items:**

#### P0-3a: Phase 1 Files (2 instances)

**Files:**
- `symbo_agentic_reasoners_phase1/solvers/pilot_solver.py:266`
- `symbo_agentic_reasoners_phase1/phase1_system.py:262`

**Action:**
```python
# BEFORE:
try:
    result = compute()
except:
    return None

# AFTER:
try:
    result = compute()
except (ValueError, TypeError, sp.SympifyError) as e:
    logger.error(f"Computation failed: {e}", exc_info=True)
    return None
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise
```

- [ ] Fix `pilot_solver.py:266`
- [ ] Fix `phase1_system.py:262`
- [ ] Add logging statements
- [ ] Test error propagation

**Estimated Effort:** 2 hours  
**Owner:** Phase 1 Team

#### P0-3b: Phase 2 Files (5 instances)

**Files:**
- `symbo_agentic_reasoners_phase2/agents/algebra/polynomial_specialist.py:278`
- `symbo_agentic_reasoners_phase2/agents/algebra/arithmetic_specialist.py:245`
- `symbo_agentic_reasoners_phase2/agents/algebra/number_theory_specialist.py:311`
- `symbo_agentic_reasoners_phase2/agents/calculus/integration_specialist.py:285, 297`

**Action:**
- [ ] Replace bare excepts with specific exception types
- [ ] Add proper logging with traceback
- [ ] Re-raise unexpected exceptions
- [ ] Test each specialist agent

**Estimated Effort:** 4 hours  
**Owner:** Phase 2 Team

#### P0-3c: Phase 5 Files (6 instances)

**Files:**
- `symbo_agentic_reasoners_phase5/symbo/nano_tensor.py:231, 275, 294, 313, 332` (5 instances)
- `symbo_agentic_reasoners_phase5/symbo/symbo_llm_core.py:317`

**Action:**
- [ ] Fix all 6 bare except clauses
- [ ] Add specific exception types for tensor operations
- [ ] Add logging for neural network errors
- [ ] Test with real PyTorch operations

**Estimated Effort:** 4 hours  
**Owner:** Phase 5 Team

#### P0-3d: Test Files (2 instances)

**Files:**
- `tests/test_phase4.py:386`
- `audit/phase1/tests/edge_tests.py:58`

**Action:**
- [ ] Fix test exception handling
- [ ] Ensure tests can fail properly
- [ ] Add assertion messages

**Estimated Effort:** 1 hour  
**Owner:** QA Team

**Total P0-3 Effort:** 11 hours  
**Verification:** No bare `except:` in production code, all exceptions logged

---

## P0 Summary

**Total Critical Items:** 3 major issues (with 9 sub-items)  
**Total Estimated Effort:** 29 hours (~4 days)  
**Blocking:** ALL deployment activities  
**Success Criteria:**
- [ ] All dependencies installable via `pip install -e .`
- [ ] No mock data returned with SUCCESS status
- [ ] No bare except clauses in production code
- [ ] Phase 2 health check passes
- [ ] Integration tests pass

---

## P1 - HIGH PRIORITY (Fix Before Production)

### P1-1: Update ChromaDB to Modern API 🔴

**Issue:** Using deprecated `chroma_db_impl` parameter  
**Impact:** Fails with ChromaDB 0.4.0+, system claims compatibility but doesn't work

**File:** `symbo_agentic_reasoners_phase0/memory/vector_database.py:126-129`

**Action Items:**
- [ ] Replace deprecated API:
  ```python
  # OLD:
  self.client = chromadb.Client(Settings(
      chroma_db_impl="duckdb+parquet",
      persist_directory=persist_directory
  ))
  
  # NEW:
  self.client = chromadb.PersistentClient(path=persist_directory)
  ```
- [ ] Update imports: `from chromadb import PersistentClient`
- [ ] Test with ChromaDB 0.4.0+
- [ ] Update requirements to specify `chromadb>=0.4.0`
- [ ] Update documentation

**Estimated Effort:** 2 hours  
**Owner:** Phase 0 Team  
**Verification:** System works with ChromaDB 0.4.22 (latest)

---

### P1-2: Add Integration Tests with Real Dependencies 🔴

**Issue:** Tests use mocks exclusively, real implementations untested  
**Impact:** Interface mismatches undetected, production failures

**Action Items:**
- [ ] Create `tests/integration/` directory structure:
  ```
  tests/integration/
  ├── __init__.py
  ├── conftest.py          # Shared fixtures
  ├── test_phase0_real.py  # Real ChromaDB, real vector ops
  ├── test_phase1_real.py  # Real orchestration
  ├── test_phase2_real.py  # Real scipy operations
  └── test_end_to_end.py   # Full pipeline
  ```
- [ ] Add pytest markers:
  ```python
  @pytest.mark.integration
  @pytest.mark.requires_chromadb
  def test_vector_database_real():
      # Test with actual ChromaDB
  ```
- [ ] Create Docker Compose for test dependencies:
  ```yaml
  version: '3.8'
  services:
    chromadb:
      image: chromadb/chroma:latest
      ports:
        - "8000:8000"
  ```
- [ ] Add CI/CD pipeline configuration
- [ ] Document integration test requirements

**Estimated Effort:** 16 hours (2 days)  
**Owner:** QA Team  
**Verification:** Integration tests pass with real dependencies

---

### P1-3: Standardize Error Handling Across Codebase 🔴

**Issue:** Inconsistent error handling patterns (silent, logged, re-raised)  
**Impact:** Unpredictable behavior, difficult debugging

**Action Items:**
- [ ] Create `docs/ERROR_HANDLING_POLICY.md`:
  ```markdown
  # Error Handling Policy
  
  ## Categories
  1. Expected Errors (ValueError, TypeError, KeyError)
     - Log at WARNING level
     - Return error status
     - Do NOT crash
  
  2. System Errors (RuntimeError, IOError, ImportError)
     - Log at ERROR level with traceback
     - Attempt graceful degradation
     - May crash if critical
  
  3. Unexpected Errors (Exception)
     - Log at CRITICAL level
     - Re-raise immediately
     - System should crash
  ```
- [ ] Create error handling templates:
  ```python
  # Template for expected errors
  try:
      result = operation()
  except (ValueError, TypeError, KeyError) as e:
      logger.warning(f"Operation failed: {e}")
      return {'status': 'ERROR', 'message': str(e)}
  
  # Template for system errors
  try:
      result = system_operation()
  except (RuntimeError, IOError, ImportError) as e:
      logger.error(f"System error: {e}", exc_info=True)
      return {'status': 'SYSTEM_ERROR', 'message': str(e)}
  
  # Template for unexpected errors
  try:
      result = critical_operation()
  except Exception as e:
      logger.critical(f"Unexpected error: {e}", exc_info=True)
      raise
  ```
- [ ] Audit all exception handlers (100+ locations)
- [ ] Refactor to match policy
- [ ] Add error handling tests

**Estimated Effort:** 24 hours (3 days)  
**Owner:** Architecture Team  
**Verification:** All error handlers follow documented policy

---

### P1-4: Add matplotlib and plotly to Dependencies 🔴

**Issue:** Phase 5 uses visualization libraries not in requirements  
**Impact:** Visualization features fail at runtime

**Action Items:**
- [ ] Add to `pyproject.toml`:
  ```toml
  [project.optional-dependencies]
  visualization = [
      "matplotlib>=3.7.0",
      "plotly>=5.14.0",
  ]
  full = [
      # ... existing ...
      "matplotlib>=3.7.0",
      "plotly>=5.14.0",
  ]
  ```
- [ ] Update documentation for visualization features
- [ ] Add graceful degradation if not installed
- [ ] Test visualization outputs

**Estimated Effort:** 2 hours  
**Owner:** Phase 5 Team  
**Verification:** Visualization features work or fail gracefully

---

## P1 Summary

**Total High Priority Items:** 4 items  
**Total Estimated Effort:** 44 hours (~5.5 days)  
**Blocking:** Production deployment  
**Success Criteria:**
- [ ] ChromaDB 0.4.0+ works correctly
- [ ] Integration tests pass
- [ ] Error handling policy documented and followed
- [ ] All dependencies properly declared

---

## P2 - MEDIUM PRIORITY (Production Hardening)

### P2-1: Implement Sandbox Timeout Enforcement 🔴

**Issue:** Code execution sandbox has timeout parameter but doesn't enforce it  
**Impact:** Malicious/buggy code can run indefinitely

**File:** `symbo_agentic_reasoners_phase6/algorithm_discovery/sandbox_evaluator.py:380`

**Action Items:**
- [ ] Implement signal-based timeout (Unix):
  ```python
  import signal
  
  def timeout_handler(signum, frame):
      raise TimeoutError("Code execution exceeded timeout")
  
  def evaluate_code(self, code: str, timeout: float = 5.0):
      signal.signal(signal.SIGALRM, timeout_handler)
      signal.alarm(int(timeout))
      try:
          exec(code, restricted_globals, namespace)
      finally:
          signal.alarm(0)
  ```
- [ ] Add resource limits:
  ```python
  import resource
  resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
  resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))
  ```
- [ ] Consider multiprocessing for true isolation
- [ ] Add timeout tests
- [ ] Document sandbox limitations

**Estimated Effort:** 8 hours  
**Owner:** Phase 6 Team  
**Verification:** Long-running code terminates after timeout

---

### P2-2: Remove sys.path Manipulation 🔴

**Issue:** Runtime sys.path modification in 6+ files  
**Impact:** Import confusion, security risk, breaks tooling

**Files:**
- All phase system files (`phase1_system.py` through `phase6_system.py`)

**Action Items:**
- [ ] Remove all `sys.path.insert()` calls
- [ ] Ensure proper package installation: `pip install -e .`
- [ ] Update all imports to use absolute paths:
  ```python
  # BEFORE:
  sys.path.insert(0, os.path.dirname(__file__))
  from agents.problem_analysis import ProblemAnalysisTeam
  
  # AFTER:
  from symbo_agentic_reasoners_phase1.agents.problem_analysis import ProblemAnalysisTeam
  ```
- [ ] Test in clean virtual environment
- [ ] Update documentation
- [ ] Update IDE configurations

**Estimated Effort:** 6 hours  
**Owner:** Build Team  
**Verification:** System works without sys.path manipulation

---

### P2-3: Add Comprehensive Test Coverage 🔴

**Issue:** Test coverage incomplete, no concurrency tests  
**Impact:** Bugs in untested code paths

**Action Items:**
- [ ] Measure current coverage: `pytest --cov=symbo_agentic_reasoners_phase0 --cov=symbo_agentic_reasoners_phase1 ...`
- [ ] Target: 70% coverage minimum
- [ ] Add unit tests for:
  - [ ] All BDI agent methods
  - [ ] All orchestrator decision paths
  - [ ] All specialist agent operations
  - [ ] All error handling paths
- [ ] Add concurrency tests:
  - [ ] Blackboard thread safety
  - [ ] ComplexityGatekeeper under load
  - [ ] Multiple agents accessing DF simultaneously
- [ ] Add performance benchmarks:
  - [ ] Query routing latency
  - [ ] Vector database retrieval speed
  - [ ] End-to-end problem solving time
- [ ] Set up coverage reporting in CI/CD

**Estimated Effort:** 40 hours (1 week)  
**Owner:** QA Team  
**Verification:** Coverage >70%, all critical paths tested

---

### P2-4: Add Monitoring and Alerting 🔴

**Issue:** No operational monitoring, can't detect issues in production  
**Impact:** Silent failures, no visibility into system health

**Action Items:**
- [ ] Add metrics collection:
  ```python
  from prometheus_client import Counter, Histogram, Gauge
  
  query_counter = Counter('symbo_agentic_reasoners_queries_total', 'Total queries')
  query_duration = Histogram('symbo_agentic_reasoners_query_duration_seconds', 'Query duration')
  active_agents = Gauge('symbo_agentic_reasoners_active_agents', 'Number of active agents')
  ```
- [ ] Add health check endpoints:
  ```python
  @app.route('/health')
  def health():
      return {
          'status': 'healthy',
          'phase0': phase0.health_check(),
          'phase1': phase1.health_check(),
          # ...
      }
  ```
- [ ] Add structured logging for key events:
  - Query received
  - Validation failed
  - Supervisor delegated
  - Result returned
  - Error occurred
- [ ] Set up alerting rules:
  - Error rate > 5%
  - Query latency > 10s
  - Agent crashes
  - Memory usage > 80%
- [ ] Create monitoring dashboard

**Estimated Effort:** 16 hours (2 days)  
**Owner:** DevOps Team  
**Verification:** Metrics visible in monitoring system

---

### P2-5: Security Audit and Hardening 🔴

**Issue:** Code execution, external API calls, potential vulnerabilities  
**Impact:** Security breaches, data leaks

**Action Items:**
- [ ] Conduct security audit:
  - [ ] Review all `exec()` usage
  - [ ] Review all external API calls
  - [ ] Review all file system access
  - [ ] Review all network operations
- [ ] Implement security controls:
  - [ ] Input validation for all user inputs
  - [ ] Rate limiting for API endpoints
  - [ ] Authentication/authorization if needed
  - [ ] Audit logging for sensitive operations
- [ ] Add security tests:
  - [ ] Test sandbox escape attempts
  - [ ] Test injection attacks
  - [ ] Test resource exhaustion
- [ ] Document security model
- [ ] Create incident response plan

**Estimated Effort:** 24 hours (3 days)  
**Owner:** Security Team  
**Verification:** Security audit passed, controls implemented

---

## P2 Summary

**Total Medium Priority Items:** 5 items  
**Total Estimated Effort:** 94 hours (~12 days)  
**Blocking:** Production deployment at scale  
**Success Criteria:**
- [ ] Sandbox enforces timeouts and resource limits
- [ ] No sys.path manipulation
- [ ] Test coverage >70%
- [ ] Monitoring and alerting operational
- [ ] Security audit passed

---

## P3 - LOW PRIORITY (Future Improvements)

### P3-1: Performance Optimization 🔴

**Action Items:**
- [ ] Profile critical paths
- [ ] Optimize vector database queries
- [ ] Cache frequently accessed data
- [ ] Parallelize independent operations
- [ ] Add query result caching

**Estimated Effort:** 40 hours  
**Owner:** Performance Team

---

### P3-2: Enhanced Documentation 🔴

**Action Items:**
- [ ] Add API documentation (Sphinx)
- [ ] Create architecture diagrams
- [ ] Add troubleshooting guide
- [ ] Create deployment guide
- [ ] Add video tutorials

**Estimated Effort:** 40 hours  
**Owner:** Documentation Team

---

### P3-3: Developer Experience Improvements 🔴

**Action Items:**
- [ ] Add pre-commit hooks
- [ ] Set up automatic code formatting
- [ ] Add type checking in CI/CD
- [ ] Create development container
- [ ] Add debugging tools

**Estimated Effort:** 16 hours  
**Owner:** DevOps Team

---

## Summary Dashboard

### By Priority

| Priority | Items | Estimated Effort | Status |
|----------|-------|------------------|--------|
| P0 (Critical) | 3 major (9 sub) | 29 hours (~4 days) | 🔴 Not Started |
| P1 (High) | 4 items | 44 hours (~5.5 days) | 🔴 Not Started |
| P2 (Medium) | 5 items | 94 hours (~12 days) | 🔴 Not Started |
| P3 (Low) | 3 items | 96 hours (~12 days) | 🔴 Not Started |
| **TOTAL** | **15 items** | **263 hours (~33 days)** | **0% Complete** |

### Critical Path to Production

**Minimum Viable Production (MVP):**
- Complete all P0 items (4 days)
- Complete all P1 items (5.5 days)
- Complete P2-1, P2-4, P2-5 (6 days)
- **Total: ~15.5 days (3 weeks)**

**Full Production Ready:**
- Complete all P0, P1, P2 items
- **Total: ~21.5 days (4.5 weeks)**

### Resource Requirements

**Immediate (P0):**
- 1 DevOps Engineer (dependencies)
- 2 Backend Engineers (mock removal, exception handling)
- 1 QA Engineer (verification)

**Short-term (P1):**
- 1 Backend Engineer (ChromaDB update)
- 2 QA Engineers (integration tests)
- 1 Architect (error handling policy)

**Medium-term (P2):**
- 1 Security Engineer (audit)
- 1 DevOps Engineer (monitoring)
- 2 QA Engineers (test coverage)
- 1 Backend Engineer (sandbox, sys.path)

---

## Tracking and Reporting

### Daily Standup Questions
1. What P0 items were completed yesterday?
2. What P0 items will be completed today?
3. What blockers exist?

### Weekly Status Report
- P0 items: X/9 complete (Y%)
- P1 items: X/4 complete (Y%)
- Blockers and risks
- Estimated completion date

### Definition of Done
- [ ] Code changes committed and reviewed
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Verified in staging environment
- [ ] Approved by tech lead

---

## Contact and Escalation

**For P0 Issues:**
- Escalate immediately to: Tech Lead
- Expected response time: 1 hour
- Daily status updates required

**For P1 Issues:**
- Report to: Project Manager
- Expected response time: 4 hours
- Weekly status updates required

**For P2/P3 Issues:**
- Track in: Project management tool
- Review in: Weekly planning meeting

---

**End of Action Items**

*Last Updated: 2025-12-06*  
*Next Review: After P0 completion*
