# Implementation Plan: Phases 4-8
**Codebase Quality Improvement Continuation**

**Date**: December 17, 2025
**Status**: Phases 1-3 COMPLETE, Phases 4-8 PLANNED
**Previous Work**: See commits 588aa1a, 60727fe, 3045a25

---

## Completed Work (Phases 1-3) ✅

### Phase 1: Archived Code Deletion ✅
- **Removed**: 16,687 LOC dead code (6.4% reduction)
- **Files**: _archived_originals/ directory → moved to MASTER_ARCHIVE
- **Tests**: 4,947 passing, no regressions
- **Commit**: 588aa1a

### Phase 2: SymPy Removal ✅
- **Removed**: SymPy from pyproject.toml, requirements.txt, requirements-full.txt
- **Replaced**: reasoning_engine.py now uses 100% native implementations
- **Added**: Implies class to sympy_compatibility.py
- **Achievement**: 100% native mathematical reasoning (0 SymPy core dependencies)
- **Tests**: 4,947 passing
- **Commit**: 60727fe

### Phase 3: Critical Security Fixes ✅
- **Fixed**: ReDoS bypass (100-byte literal pattern limit)
- **Fixed**: Path traversal (_canonicalize_resource_path function)
- **Fixed**: Arithmetic DoS (pre-execution complexity analysis)
- **Added**: 21 comprehensive security tests (100% passing)
- **Tests**: 4,968 passing (gained 21)
- **Commit**: 3045a25

---

## Remaining Work (Phases 4-8)

### Current Codebase Status
- **Total LOC**: ~244,000 (down from ~261,000)
- **Test-to-Code Ratio**: 0.53 (target: 0.7)
- **Documentation Coverage**: ~65% (target: 80%)
- **Large Files**: 3 files >900 LOC remaining (orchestrator.py: 1,503)
- **Security Issues**: 9 remaining (4 HIGH, 2 MEDIUM, 3 LOW)

---

## PHASE 4: Decompose orchestrator.py (5-7 Days)

### Current Status
- ✅ Package created: `src/symbo_agentic_reasoners/core/orchestration/`
- ✅ Module created: `data_structures.py` (90 LOC)
- ✅ Module created: `decomposition.py` (160 LOC)
- ⏳ **Remaining**: 4 modules to extract from orchestrator.py

### File Structure to Create

```
src/symbo_agentic_reasoners/core/orchestration/
├── __init__.py                  # Backward-compatible exports
├── data_structures.py          # ✅ DONE - Task, NoAgentAvailableError, mappings
├── decomposition.py            # ✅ DONE - HTN decomposition, agent lifecycle
├── agent_invocation.py         # TODO - Direct invocation, specialist calling
├── native_fallback.py          # TODO - Native computation fallbacks
├── blackboard_integration.py   # TODO - Blackboard posting/awaiting
└── learning_memory.py          # TODO - Look-before-leap, solution recording
```

### Module 3: agent_invocation.py (~250 LOC)

**Extract from orchestrator.py lines 409-1138:**

**Functions to move:**
- `_direct_invoke(structured, supervisor_instance)` - Direct agent invocation
- `_invoke_specialist_directly(specialist, problem_text)` - Specialist direct call
- `_get_service_type(operation)` - Map operation to service type
- `_find_capable_agents(service_type, properties)` - Query DF for agents
- `_map_operation_to_service(operation)` - Service type mapping
- `_create_specialist_for_operation(operation, domain)` - Specialist factory
- `_call_specialist(specialist_class, problem)` - Generic specialist invocation

**Implementation:**
```python
# agent_invocation.py template

import logging
from typing import Any, Optional, Dict, List
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator

logger = logging.getLogger('symbo_agentic_reasoners.orchestration.agent_invocation')


class AgentInvoker:
    """Handles direct agent invocation and specialist calling."""

    def __init__(self, df: Optional[DirectoryFacilitator] = None):
        self.df = df
        self.invocations = 0

    def direct_invoke(self, structured: StructuredProblem, supervisor_instance: Any) -> Optional[Any]:
        """
        Direct invocation path - calls supervisor/specialist directly.

        (Copy implementation from orchestrator.py:409-527)
        """
        pass  # TODO: Extract code

    def invoke_specialist_directly(self, specialist: Any, problem_text: str) -> Optional[Any]:
        """
        Invoke specialist agent directly for synchronous execution.

        (Copy implementation from orchestrator.py)
        """
        pass  # TODO: Extract code

    def get_service_type(self, operation: str) -> str:
        """Map operation to service type."""
        pass  # TODO: Extract code

    def find_capable_agents(self, service_type: str, properties: Dict = None) -> List:
        """Query Directory Facilitator for capable agents."""
        if not self.df:
            return []
        return self.df.search(service_type, properties or {})

    # ... additional methods
```

### Module 4: native_fallback.py (~350 LOC)

**Extract from orchestrator.py lines 528-1048:**

**Functions to move:**
- `_native_fallback(problem_text, domain)` - Main fallback router
- `_native_solve(problem_text)` - Algebraic solving
- `_geometry_fallback(problem_text)` - Geometry computations
- `_linalg_fallback(problem_text)` - Matrix operations
- `_stats_fallback(problem_text)` - Statistical computations
- `_discrete_fallback(problem_text)` - Discrete math
- `_native_determinant(matrix)` - Matrix determinant
- `_native_eigenvalues_2x2(matrix)` - 2x2 eigenvalues
- `_native_matrix_inverse_2x2(matrix)` - 2x2 inverse
- `_is_prime(n)` - Primality test

**Implementation:**
```python
# native_fallback.py template

import logging
import re
from typing import Any, Optional
from symbo_agentic_reasoners.agents.base.problem_analysis import MathDomain

logger = logging.getLogger('symbo_agentic_reasoners.orchestration.native_fallback')


class NativeFallbackEngine:
    """
    Native computation fallback engine.

    Provides basic computational capabilities when no specialized
    agents are available. Uses pure Python implementations.
    """

    def __init__(self):
        self.fallback_count = 0

    def compute_fallback(self, problem_text: str, domain: MathDomain) -> Optional[Any]:
        """
        Main fallback router - delegates to domain-specific fallback.

        (Copy implementation from orchestrator.py:528-679)
        """
        self.fallback_count += 1

        if domain == MathDomain.Algebra:
            return self._native_solve(problem_text)
        elif domain == MathDomain.Geometry:
            return self._geometry_fallback(problem_text)
        elif domain == MathDomain.LinearAlgebra:
            return self._linalg_fallback(problem_text)
        elif domain == MathDomain.Statistics:
            return self._stats_fallback(problem_text)
        elif domain == MathDomain.DiscreteMath:
            return self._discrete_fallback(problem_text)
        else:
            return None

    def _native_solve(self, problem_text: str) -> Optional[Any]:
        """Native algebraic solver."""
        pass  # TODO: Extract code from orchestrator.py

    def _geometry_fallback(self, problem_text: str) -> Optional[Any]:
        """Geometry fallback computations."""
        pass  # TODO: Extract code

    def _linalg_fallback(self, problem_text: str) -> Optional[Any]:
        """Linear algebra fallback."""
        pass  # TODO: Extract code

    # ... additional fallback methods
```

### Module 5: blackboard_integration.py (~200 LOC)

**Extract from orchestrator.py lines 1195-1340:**

**Functions to move:**
- `_post_task_to_blackboard(task)` - Post task for async execution
- `_await_verified_result(task, timeout)` - Wait for and retrieve result

**Implementation:**
```python
# blackboard_integration.py template

import logging
import time
from typing import Any, Optional
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType, EntryStatus
from symbo_agentic_reasoners.core.orchestration.data_structures import Task

logger = logging.getLogger('symbo_agentic_reasoners.orchestration.blackboard')


class BlackboardIntegration:
    """
    Manages orchestrator interaction with blackboard.

    Handles posting tasks and awaiting results from asynchronous agents.
    """

    def __init__(self, blackboard: Optional[Blackboard] = None):
        self.blackboard = blackboard
        self.blackboard_posts = 0

    def post_task(self, task: Task) -> bool:
        """
        Post task to blackboard for asynchronous agent execution.

        Args:
            task: Task to post

        Returns:
            True if posted successfully
        """
        if not self.blackboard:
            logger.warning("No blackboard available for async execution")
            return False

        # TODO: Extract implementation from orchestrator.py:1195-1260
        self.blackboard_posts += 1
        return True

    def await_result(self, task: Task, timeout: float = 60.0) -> Optional[Any]:
        """
        Wait for task completion and retrieve result from blackboard.

        Args:
            task: Task to await
            timeout: Maximum wait time in seconds

        Returns:
            Result from blackboard or None if timeout

        """
        if not self.blackboard or not task.blackboard_entry_id:
            return None

        # TODO: Extract implementation from orchestrator.py:1262-1340
        start_time = time.time()
        # Polling logic here
        pass
```

### Module 6: learning_memory.py (~150 LOC)

**Extract from orchestrator.py lines 1342-1409:**

**Functions to move:**
- `_look_before_leap(structured)` - Check knowledge cache
- `_record_solution(structured, result)` - Store solution in memory

**Implementation:**
```python
# learning_memory.py template

import logging
from typing import Any, Optional
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem

try:
    from symbo_agentic_reasoners.middleware.knowledge_management import (
        KnowledgeManagementTeam, RetrievalConfidence
    )
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False
    KnowledgeManagementTeam = None

logger = logging.getLogger('symbo_agentic_reasoners.orchestration.learning')


class LearningMemory:
    """
    Learning and memory management for orchestrator.

    Implements 'look-before-leap' pattern - check cache before solving.
    """

    def __init__(self, knowledge_team: Optional[KnowledgeManagementTeam] = None):
        self.knowledge_team = knowledge_team
        self.cache_hits = 0
        self.cache_misses = 0

    def look_before_leap(self, structured: StructuredProblem) -> Optional[Any]:
        """
        Check if we've solved this problem before (Phase 3 feature).

        Args:
            structured: Problem to check

        Returns:
            Cached result if found, None otherwise
        """
        if not self.knowledge_team or not KNOWLEDGE_AVAILABLE:
            self.cache_misses += 1
            return None

        # TODO: Extract implementation from orchestrator.py:1342-1377
        pass

    def record_solution(self, structured: StructuredProblem, result: Any):
        """
        Record successful solution for future retrieval (Phase 3 feature).

        Args:
            structured: Problem that was solved
            result: The solution
        """
        if not self.knowledge_team or not KNOWLEDGE_AVAILABLE:
            return

        # TODO: Extract implementation from orchestrator.py:1379-1409
        pass
```

### Module 7: Refactored orchestrator.py (~300 LOC)

**Keep in orchestrator.py:**
- `MainOrchestrator` class definition
- `__init__()` method
- `process()` main method (orchestrates all modules)
- `update_beliefs()`, `deliberate()`, `execute_step()` - BDI methods
- `get_statistics()` - Statistics reporting

**New implementation structure:**
```python
from symbo_agentic_reasoners.core.orchestration.data_structures import (
    NoAgentAvailableError, Task, get_pool_domain_key
)
from symbo_agentic_reasoners.core.orchestration.decomposition import DecompositionEngine
from symbo_agentic_reasoners.core.orchestration.agent_invocation import AgentInvoker
from symbo_agentic_reasoners.core.orchestration.native_fallback import NativeFallbackEngine
from symbo_agentic_reasoners.core.orchestration.blackboard_integration import BlackboardIntegration
from symbo_agentic_reasoners.core.orchestration.learning_memory import LearningMemory


class MainOrchestrator(BDIAgent):
    """Main Orchestrator - The Central Nervous System."""

    def __init__(self, agent_id: str, ...):
        super().__init__(agent_id, ...)

        # Initialize sub-engines
        self.decomposer = DecompositionEngine(agent_pool=self.agent_pool)
        self.invoker = AgentInvoker(df=self.df)
        self.fallback = NativeFallbackEngine()
        self.blackboard_ops = BlackboardIntegration(blackboard=self.blackboard)
        self.learning = LearningMemory(knowledge_team=self.knowledge_team)

    def process(self, problem_text: str) -> Optional[Any]:
        """Main orchestration logic using sub-engines."""
        # Parse problem
        structured = self.parser.parse(problem_text)

        # Learning: Look before leap
        cached = self.learning.look_before_leap(structured)
        if cached:
            return cached

        # Decompose
        subtasks = self.decomposer.decompose(structured)

        # Wake agents
        domain_key = get_pool_domain_key(structured.domain)
        self.decomposer.wake_domain_agents(domain_key)

        # Find supervisor
        supervisor = self._find_supervisor(structured.domain)

        # Invoke
        if supervisor:
            result = self.invoker.direct_invoke(structured, supervisor)
        else:
            # Fallback
            result = self.fallback.compute_fallback(problem_text, structured.domain)

        # Record
        if result:
            self.learning.record_solution(structured, result)

        return result
```

### Implementation Steps (Day-by-Day)

**Day 1: Extract agent_invocation.py**
```bash
# 1. Create file with AgentInvoker class
# 2. Copy methods: _direct_invoke, _invoke_specialist_directly,
#    _get_service_type, _find_capable_agents, _map_operation_to_service,
#    _create_specialist_for_operation, _call_specialist
# 3. Update imports
# 4. Test: pytest tests/test_orchestrator.py -v
```

**Day 2: Extract native_fallback.py**
```bash
# 1. Create file with NativeFallbackEngine class
# 2. Copy all fallback methods (_native_fallback, _native_solve,
#    _geometry_fallback, _linalg_fallback, _stats_fallback, _discrete_fallback)
# 3. Copy native computation helpers (_native_determinant, _native_eigenvalues_2x2, etc.)
# 4. Test: pytest tests/test_orchestrator.py -v
```

**Day 3: Extract blackboard_integration.py**
```bash
# 1. Create file with BlackboardIntegration class
# 2. Copy: _post_task_to_blackboard, _await_verified_result
# 3. Test: pytest tests/test_orchestrator.py -v
```

**Day 4: Extract learning_memory.py**
```bash
# 1. Create file with LearningMemory class
# 2. Copy: _look_before_leap, _record_solution
# 3. Test: pytest tests/test_orchestrator.py -v
```

**Day 5: Refactor MainOrchestrator**
```bash
# 1. Update orchestrator.py to import from sub-modules
# 2. Replace method calls with sub-engine calls
#    - self._decompose() → self.decomposer.decompose()
#    - self._wake_domain_agents() → self.decomposer.wake_domain_agents()
#    - self._direct_invoke() → self.invoker.direct_invoke()
#    - self._native_fallback() → self.fallback.compute_fallback()
#    - self._post_task_to_blackboard() → self.blackboard_ops.post_task()
#    - self._look_before_leap() → self.learning.look_before_leap()
# 3. Test: pytest tests/test_orchestrator.py -v
```

**Day 6: Create backward compatibility**
```bash
# Create orchestration/__init__.py with re-exports:

from .data_structures import (
    NoAgentAvailableError,
    DOMAIN_TO_POOL_KEY,
    get_pool_domain_key,
    Task
)
from .decomposition import DecompositionEngine
from .agent_invocation import AgentInvoker
from .native_fallback import NativeFallbackEngine
from .blackboard_integration import BlackboardIntegration
from .learning_memory import LearningMemory

# Re-export MainOrchestrator from parent for backward compat
# This allows: from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
# to still work
```

**Day 7: Full testing & commit**
```bash
# Run full test suite
pytest tests/ -v

# Commit
git add .
git commit -m "refactor: Decompose orchestrator.py (1,503→6 modules)

Supervisor-Specialist Pattern Applied:
- orchestrator.py (300 LOC) - MainOrchestrator coordinator
- data_structures.py (90 LOC) - Task, mappings
- decomposition.py (160 LOC) - HTN decomposition, agent lifecycle
- agent_invocation.py (250 LOC) - Direct invocation, specialist calling
- native_fallback.py (350 LOC) - Native computation fallbacks
- blackboard_integration.py (200 LOC) - Blackboard ops
- learning_memory.py (150 LOC) - Cache and memory

Each module <350 LOC, clear separation of concerns
All tests passing: 4,968 tests"
```

### Success Criteria
- ✅ orchestrator.py reduced from 1,503 → ~300 LOC
- ✅ 6 focused modules created (avg 200 LOC each)
- ✅ All tests passing
- ✅ No circular dependencies
- ✅ Backward compatibility maintained

---

## PHASE 5: Fix Remaining 9 Security Issues (3-4 Days)

### HIGH Priority (4 issues) - Days 1-2

**Issue #4: Unverified Agent Identity**
- **Files**: infrastructure/ams.py, infrastructure/directory_facilitator.py
- **Implementation**: Add HMAC-based agent authentication
- **Code**:
```python
# infrastructure/security/agent_auth.py (NEW FILE)

import hmac
import hashlib
import secrets
import time
import os
from typing import Optional

class AgentAuthenticator:
    """HMAC-based agent authentication."""

    def __init__(self, secret_key: Optional[str] = None):
        self._secret_key = secret_key or os.getenv('AGENT_AUTH_SECRET', secrets.token_hex(32))

    def generate_token(self, agent_id: str, timestamp: int = None) -> str:
        """Generate HMAC token for agent."""
        if timestamp is None:
            timestamp = int(time.time())
        message = f"{agent_id}:{timestamp}".encode('utf-8')
        return hmac.new(
            self._secret_key.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()

    def verify_token(self, agent_id: str, timestamp: int, token: str) -> bool:
        """Verify agent identity using HMAC token."""
        # Check timestamp freshness (5 minute window)
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:
            return False

        expected_token = self.generate_token(agent_id, timestamp)
        return hmac.compare_digest(token, expected_token)

# Update AMS.register_agent():
def register_agent(self, agent_id: str, agent_type: AgentType, token: str = None) -> bool:
    """Register agent with optional authentication."""
    if self.authenticator:
        timestamp = int(time.time())
        if not self.authenticator.verify_token(agent_id, timestamp, token):
            self.logger.warning(f"Agent authentication failed: {agent_id}")
            return False
    # Continue with registration...
```

**Issue #5: Session Hijacking via Rainbow Deployment**
- **File**: infrastructure/deployment/rainbow_deployment.py
- **Implementation**: Add sticky sessions
- **Code**: See detailed plan in docs (lines 767-811 from security analysis)

**Issue #6: Unbounded Message Queues**
- **File**: infrastructure/acc.py
- **Implementation**: Add BoundedMessageQueue class
- **Limits**: 1000 messages/agent, 60-minute TTL
- **Code**: See detailed plan (lines 813-860)

**Issue #7: No Message Integrity**
- **File**: core/message_bus.py, infrastructure/acc.py
- **Implementation**: Add HMAC message signing
- **Code**: See detailed plan (lines 862-897)

**Tests to Add** (Day 2):
```python
# tests/test_security_high_priority_fixes.py

def test_agent_authentication_prevents_spoofing():
    """Test HMAC authentication prevents agent ID spoofing."""
    pass

def test_sticky_sessions_maintain_state():
    """Test rainbow deployment maintains session consistency."""
    pass

def test_message_queue_bounds_enforced():
    """Test message queues respect size and TTL limits."""
    pass

def test_message_integrity_verified():
    """Test HMAC prevents message tampering."""
    pass
```

### MEDIUM Priority (2 issues) - Day 3

**Issue #8: Watchdog Thread Interruption Unreliable**
- **File**: infrastructure/watchdog.py
- **Implementation**: Add cooperative cancellation
- **Approach**: Use threading.Event for cancellation signal

**Issue #9: No Distributed Rate Limiting**
- **File**: infrastructure/hardening/security_monitor.py
- **Implementation**: Optional Redis-backed rate limiter
- **Fallback**: Keep local rate limiting as default

### LOW Priority (3 issues) - Day 4

**Issue #10: Audit Trail Truncation**
- **File**: infrastructure/hardening/security_monitor.py
- **Implementation**: Persistent append-only logging to file
- **Rotation**: Daily rotation with 30-day retention

**Issue #11: Policy Conflict Detection**
- **File**: infrastructure/hardening/security_monitor.py
- **Implementation**: Policy analyzer that detects overlapping/conflicting rules

**Tests to Add**:
- 30+ tests for MEDIUM/LOW priority fixes
- Integration tests for all 9 fixes combined

### Success Criteria
- ✅ All 12 security vulnerabilities fixed (3 critical + 9 remaining)
- ✅ Security score: 82 → 92+ (Tier 1)
- ✅ 50+ new security tests
- ✅ All tests passing

---

## PHASE 6: Increase Test-to-Code Ratio to 0.7 (2 weeks)

### Current Status
- **Current**: 90,384 test LOC / 170,812 source LOC = 0.53
- **Target**: 119,568 test LOC (ratio 0.7)
- **Gap**: +29,184 LOC tests needed

### Week 1: Property-Based Tests (+5,000 LOC)

**Create**: `tests/property_based/`

```python
# tests/property_based/test_symbolic_properties.py

from hypothesis import given, strategies as st, assume, settings
from hypothesis import HealthCheck
from symbo_agentic_reasoners.core.symbolic import Symbol, Integer, Add, Mul

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Addition should be commutative: a + b = b + a."""
    x = Add(Integer(a), Integer(b))
    y = Add(Integer(b), Integer(a))
    assert x.evaluate() == y.evaluate()

@given(st.integers(), st.integers(), st.integers())
def test_addition_associative(a, b, c):
    """Addition should be associative: (a+b)+c = a+(b+c)."""
    x = Add(Add(Integer(a), Integer(b)), Integer(c))
    y = Add(Integer(a), Add(Integer(b), Integer(c)))
    assert x.evaluate() == y.evaluate()

@given(st.integers(), st.integers())
def test_multiplication_commutative(a, b):
    """Multiplication should be commutative."""
    x = Mul(Integer(a), Integer(b))
    y = Mul(Integer(b), Integer(a))
    assert x.evaluate() == y.evaluate()

# Add 100+ property tests for:
# - Algebraic properties (commutativity, associativity, distributivity)
# - Numerical stability
# - Parser invariants
# - Simplification correctness
```

**Files to create** (Week 1):
- `test_symbolic_properties.py` (1,000 LOC, 200 tests)
- `test_calculus_properties.py` (800 LOC, 150 tests)
- `test_numeric_properties.py` (600 LOC, 120 tests)
- `test_parser_properties.py` (800 LOC, 150 tests)
- `test_solver_properties.py` (1,000 LOC, 180 tests)
- `test_matrix_properties.py` (800 LOC, 150 tests)

**Total**: ~5,000 LOC, 950+ property-based tests

### Week 2: Security & Infrastructure Tests (+8,000 LOC)

**Expand existing security tests:**

```python
# tests/test_security_exhaustive.py (NEW - 2,000 LOC)

class TestUnicodeAttackVectors:
    """Test all known Unicode exploits from OWASP."""

    UNICODE_ATTACKS = [
        # Load 1000+ Unicode exploit patterns
        "\u202e",  # Right-to-left override
        "\u200e",  # Left-to-right mark
        # ... 1000 more patterns
    ]

    @pytest.mark.parametrize("attack", UNICODE_ATTACKS)
    def test_unicode_attack_blocked(self, attack):
        """Test that Unicode attack is blocked."""
        monitor = SecurityMonitor(agent_id='test')
        result = monitor.validate_input(attack)
        assert not result  # Should be rejected
```

**Files to create** (Week 2):
- `test_security_exhaustive.py` (2,000 LOC, 1,000+ tests)
- `test_infrastructure_stress.py` (1,500 LOC, 300 tests)
- `test_resource_governor_comprehensive.py` (1,200 LOC, 200 tests)
- `test_watchdog_comprehensive.py` (1,000 LOC, 150 tests)
- `test_blackboard_comprehensive.py` (1,300 LOC, 250 tests)
- `test_message_bus_comprehensive.py` (1,000 LOC, 150 tests)

**Total**: ~8,000 LOC, 2,050+ tests

### Weeks 3-4: Agent Coverage Tests (+10,000 LOC)

**Strategy**: Create standardized test template for each specialist

```python
# tests/agents/test_specialist_template.py

class SpecialistTestTemplate:
    """Template for testing any specialist (15 tests each)."""

    def test_specialist_initialization(self, specialist_class):
        """Test specialist initializes correctly."""
        specialist = specialist_class(agent_id='test_001', df=None, blackboard=None)
        assert specialist.agent_id == 'test_001'

    def test_specialist_registers_with_df(self, specialist_class, mock_df):
        """Test specialist registers services."""
        specialist = specialist_class(agent_id='test_001', df=mock_df, blackboard=None)
        assert mock_df.register.called

    def test_specialist_handles_simple_problem(self, specialist_class, simple_problem):
        """Test specialist solves simple problem."""
        specialist = specialist_class(agent_id='test_001', df=None, blackboard=None)
        result = specialist.process(simple_problem)
        assert result is not None

    # ... 12 more standardized tests
```

**Apply template to all specialists:**
- 94 specialists × 15 tests = 1,410 new tests
- Estimated 7 LOC per test = ~10,000 LOC

**Files to create** (Weeks 3-4):
- `tests/agents/algebra/*.py` - 12 files for algebra specialists
- `tests/agents/calculus/*.py` - 8 files for calculus specialists
- `tests/agents/physics/*.py` - 12 files for physics specialists
- `tests/agents/linear_algebra/*.py` - 5 files
- `tests/agents/geometry/*.py` - 6 files
- ... (18 domain directories total)

### Week 5: Integration Tests (+6,000 LOC)

```python
# tests/integration/test_e2e_workflows.py (NEW - 2,000 LOC)

class TestEndToEndWorkflows:
    """Comprehensive end-to-end workflow tests."""

    def test_complex_calculus_problem(self):
        """Test problem requiring multiple specialists."""
        problem = "Find ∫(x²·sin(x) + e^x·cos(x)) dx from 0 to π"
        # Should involve: IntegrationSpecialist, TrigonometrySpecialist
        orchestrator = MainOrchestrator(...)
        result = orchestrator.process(problem)
        assert result.success
        assert result.verification_status == 'VERIFIED'

    def test_multi_domain_physics_problem(self):
        """Test problem spanning mechanics, calculus, linear algebra."""
        problem = "A projectile launched at 45° with initial velocity 20 m/s. Find trajectory equation and max height."
        # Physics → Calculus → Linear Algebra
        result = orchestrator.process(problem)
        assert result.success

    # ... 100+ integration tests
```

**Files to create** (Week 5):
- `test_e2e_workflows.py` (2,000 LOC, 100 tests)
- `test_multi_agent_coordination.py` (1,500 LOC, 75 tests)
- `test_error_propagation.py` (1,000 LOC, 50 tests)
- `test_resource_contention.py` (800 LOC, 40 tests)
- `test_concurrent_requests.py` (700 LOC, 35 tests)

**Total**: ~6,000 LOC, 300+ integration tests

### Total Phase 6 Impact
- **LOC Added**: ~29,000 LOC tests
- **Tests Added**: ~4,300 new tests
- **New Test-to-Code Ratio**: (90,384 + 29,000) / 170,812 = 0.70 ✅

---

## PHASE 7: Achieve 80% Documentation Coverage (1-2 Weeks)

### Current Status
- **Current**: 2,305 docstrings / ~3,500 functions = 65%
- **Target**: 2,800 documented functions (80%)
- **Gap**: 495 missing docstrings

### Automated Tool: scripts/generate_docstrings.py

```python
#!/usr/bin/env python3
"""
Docstring Generator Tool
========================

Scans codebase for undocumented functions and generates templates.

Usage:
    python scripts/generate_docstrings.py src/ --output=docstrings_todo.txt
    python scripts/generate_docstrings.py src/ --auto-add  # Adds templates directly
"""

import ast
import os
from pathlib import Path
from typing import List, Tuple

class DocstringAnalyzer:
    """Analyzes codebase for missing docstrings."""

    def analyze_file(self, filepath: Path) -> List[Tuple[int, str, str]]:
        """
        Analyze file for missing docstrings.

        Returns:
            List of (line_number, name, type) for undocumented items
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=str(filepath))
            except SyntaxError:
                return []

        missing = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    missing.append((node.lineno, node.name, 'function'))
            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    missing.append((node.lineno, node.name, 'class'))

        return missing

    def generate_template(self, node: ast.FunctionDef) -> str:
        """Generate docstring template for function."""
        params = [arg.arg for arg in node.args.args]
        param_section = '\n        '.join(f"{p}: Description" for p in params if p != 'self')

        template = f'''"""
    {self._humanize_name(node.name)}.

    Args:
        {param_section}

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input
    """'''
        return template

    def _humanize_name(self, name: str) -> str:
        """Convert function_name to 'Function name' description."""
        words = name.replace('_', ' ').split()
        return ' '.join(words).capitalize()

# CLI implementation
if __name__ == "__main__":
    analyzer = DocstringAnalyzer()
    # Scan and generate report
```

### Priority Modules (Week 1)

**Infrastructure (45 functions → 90% target)**
- ams.py (15 functions)
- directory_facilitator.py (8 functions)
- acc.py (10 functions)
- watchdog.py (12 functions)

**Core Symbolic (30 functions → 95% target)**
- type_system.py (10 functions)
- operations.py (8 functions)
- functions.py (12 functions)

### Supervisors (Week 2)

**All 20 supervisors (100 functions → 85% target)**
- Template for supervisor documentation
- Apply to: AlgebraSupervisor, CalculusSupervisor, LinearAlgebraSupervisor, etc.

### Specialists (Week 3)

**Top 30 specialists (188 functions → 80% target)**
- Focus on most-used specialists
- Algebra: ArithmeticSpecialist, PolynomialSpecialist, NumberTheorySpecialist
- Calculus: DifferentiationSpecialist, IntegrationSpecialist, LimitEvaluator
- Linear Algebra: MatrixOperationsSpecialist, DecompositionSpecialist

### Discovery/Phase 6 (Week 4)

**Phase 6 modules (80 functions → 75% target)**
- imagination_engine.py
- curiosity_engine.py
- conjecture_generator.py
- search_tree_manager.py

### Total Phase 7 Impact
- **Docstrings Added**: ~495 (7,500 LOC)
- **Coverage**: 65% → 82% ✅ (exceeds 80% target)

---

## PHASE 8: Clean Up Loose Files and Codebase (3-5 Days)

### Loose Files to Address

**Root Directory Cleanup:**
```bash
# Current root has 50+ loose JSON files
batch_results_*.json  # 50+ files
coverage.json
*.md files (some redundant)
```

**Actions**:
```bash
# Day 1: Organize batch results
mkdir -p data/batch_results/archive_2025/
mv batch_results_202512*.json data/batch_results/archive_2025/

# Day 2: Consolidate markdown docs
# Review and merge:
# - ALGEBRA_IMPROVEMENT_*.md
# - LOGIC_*.md
# - SECURITY_*.md
# Move to docs/ with proper naming

# Day 3: Clean .gitignore
# Add patterns:
*.pyc
__pycache__/
*.egg-info/
.pytest_cache/
htmlcov/
.coverage
*.log
batch_results_*.json
```

### Code Quality Cleanup

**Day 4: Remove TODO/FIXME items**
```bash
# Find all TODOs
grep -r "TODO\|FIXME" src/ | wc -l  # Found 10 occurrences

# Address each:
# - Implement if critical
# - Create GitHub issue if deferred
# - Remove if obsolete
```

**Day 5: Dependency Audit**
```bash
# Remove unused dependencies
pip install pipreqs
pipreqs src/symbo_agentic_reasoners --force

# Compare with requirements.txt
# Remove unused: kanren, scikit-optimize (if not referenced)
```

### Import Organization

**Apply isort to entire codebase:**
```bash
pip install isort
isort src/ tests/ scripts/ --profile black
```

**Apply black formatting:**
```bash
black src/ tests/ scripts/ --line-length 100
```

### Final Cleanup Checklist

- [ ] Move 50+ batch_results JSON files to archive
- [ ] Consolidate redundant markdown docs
- [ ] Update .gitignore with comprehensive patterns
- [ ] Address all 10 TODO/FIXME items
- [ ] Remove unused dependencies
- [ ] Format all code with black + isort
- [ ] Run full linter (ruff)
- [ ] Final regression test (all 8,000+ tests)

---

## SUMMARY TIMELINE

### Completed (Week 1)
- ✅ Phase 1: Delete archived code (Day 1)
- ✅ Phase 2: Remove SymPy (Days 2-3)
- ✅ Phase 3: Fix critical security (Days 4-5)

### Remaining (Weeks 2-6)

**Week 2:**
- Phase 4: Decompose orchestrator.py (Days 1-5)

**Week 3:**
- Phase 5: Fix 9 security issues (Days 1-4)
- Phase 6: Start property-based tests (Day 5)

**Week 4:**
- Phase 6: Security & infrastructure tests (Days 1-5)

**Week 5:**
- Phase 6: Agent coverage tests (Days 1-3)
- Phase 6: Integration tests (Days 4-5)

**Week 6:**
- Phase 7: Documentation push (Days 1-4)
- Phase 8: Cleanup (Day 5)

---

## Success Metrics

### Final Target State

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Total LOC | 244,000 | <240,000 | On track |
| Dead Code | 0 LOC | 0 LOC | ✅ |
| SymPy Dependency | None | None | ✅ |
| Security Vulnerabilities | 9 | 0 | In progress |
| Files >900 LOC | 1 (orchestrator) | 0 | In progress |
| Test-to-Code Ratio | 0.53 | 0.7 | Planned |
| Documentation | 65% | 80% | Planned |
| Security Score | 82/100 | 92/100 | Target |
| Overall Score | 84/100 | 92/100 | Target |

---

## Risk Mitigation

### Testing Strategy
- Run full test suite after each module extraction
- Maintain >4,900 passing tests throughout
- Add new tests incrementally (don't batch)

### Git Strategy
- Commit after each sub-task (small, atomic commits)
- Create feature branch: `feature/quality-improvement-phases-4-8`
- Merge to master only after full phase completion

### Rollback Points
- After Phase 4: orchestrator decomposition complete
- After Phase 5: All security issues fixed
- After Phase 6: Test ratio achieved
- After Phase 7: Documentation complete
- After Phase 8: Cleanup complete

---

**Plan Created**: December 17, 2025
**Estimated Completion**: Early January 2026 (3-4 weeks)
**Next Action**: Continue Phase 4 (orchestrator decomposition)
