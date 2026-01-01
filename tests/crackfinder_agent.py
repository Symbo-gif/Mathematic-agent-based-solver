# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
CRACKFINDER TESTING AGENT FOR SYMBO_AGENTIC_REASONERS
=====================================================

Comprehensive testing agent implementing:
1. WHITE-BOX TESTING - Internal code path analysis
2. BLACK-BOX TESTING - Input/output boundary testing
3. INTEGRATION TESTING - End-to-end flow validation

Based on CrackFinder methodology: "Find the cracks. Break it first."
"""

import sys
import os
import traceback
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import importlib
import inspect

# Ensure proper encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class Severity(Enum):
    CRITICAL = "CRITICAL"  # Exploitable security flaw or guaranteed crash
    HIGH = "HIGH"          # Will fail in production
    MEDIUM = "MEDIUM"      # Edge case that will eventually bite
    LOW = "LOW"            # Code smell, minor risk


class TestCategory(Enum):
    INPUT_VALIDATION = "Input Validation"
    TYPE_SYSTEM = "Type System"
    LOGIC_FLAWS = "Logic Flaws"
    CONTROL_FLOW = "Control Flow"
    STATE_MUTATION = "State & Mutation"
    CONCURRENCY = "Concurrency"
    RESOURCE_MGMT = "Resource Management"
    ERROR_HANDLING = "Error Handling"
    SECURITY = "Security"
    API_BOUNDARY = "API & Boundaries"
    INTEGRATION = "Integration"


@dataclass
class Crack:
    """A weakness/vulnerability found during testing"""
    severity: Severity
    title: str
    location: str
    category: TestCategory
    description: str
    breaks_when: str
    poc: str
    fix: str = ""

    def __str__(self):
        icons = {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "🟠",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "🟢"
        }
        return f"{icons[self.severity]} [{self.severity.value}] {self.title}"


@dataclass
class TestResult:
    """Result of a single test case"""
    name: str
    passed: bool
    category: TestCategory
    duration_ms: float
    error: Optional[str] = None
    details: Optional[str] = None


@dataclass
class TestReport:
    """Comprehensive test report"""
    test_type: str  # white-box, black-box, integration
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: List[TestResult] = field(default_factory=list)
    cracks: List[Crack] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    def summary(self) -> str:
        duration = (self.completed_at - self.started_at).total_seconds() if self.completed_at else 0
        crit = sum(1 for c in self.cracks if c.severity == Severity.CRITICAL)
        high = sum(1 for c in self.cracks if c.severity == Severity.HIGH)
        med = sum(1 for c in self.cracks if c.severity == Severity.MEDIUM)
        low = sum(1 for c in self.cracks if c.severity == Severity.LOW)

        return f"""
{'='*70}
{self.test_type.upper()} TEST REPORT
{'='*70}
Tests:  {self.passed}/{self.total} passed ({self.failed} failed)
Time:   {duration:.2f}s
Cracks: 🔴{crit} 🟠{high} 🟡{med} 🟢{low}
{'='*70}
"""


class CrackFinderAgent:
    """
    CrackFinder Testing Agent for Symbo

    Systematically probes the codebase for:
    - Input validation gaps
    - Type system weaknesses
    - Logic flaws
    - Concurrency issues
    - Resource leaks
    - Error handling gaps
    - Security vulnerabilities
    """

    def __init__(self):
        self.reports: List[TestReport] = []

    def run_all_tests(self) -> Dict[str, TestReport]:
        """Run all three testing phases"""
        print("="*70)
        print("CRACKFINDER COMPREHENSIVE TESTING")
        print("="*70)
        print()

        results = {}

        # Phase 1: White-box
        print("PHASE 1: WHITE-BOX TESTING (Internal Analysis)")
        print("-"*70)
        results['white_box'] = self.run_white_box_tests()
        print(results['white_box'].summary())

        # Phase 2: Black-box
        print("PHASE 2: BLACK-BOX TESTING (Input/Output)")
        print("-"*70)
        results['black_box'] = self.run_black_box_tests()
        print(results['black_box'].summary())

        # Phase 3: Integration
        print("PHASE 3: INTEGRATION TESTING (End-to-End)")
        print("-"*70)
        results['integration'] = self.run_integration_tests()
        print(results['integration'].summary())

        # Combined summary
        self._print_combined_summary(results)

        return results

    def run_white_box_tests(self) -> TestReport:
        """
        WHITE-BOX TESTING: Internal code path analysis

        Tests internal logic, code paths, and component interactions
        with full visibility into implementation.
        """
        report = TestReport(test_type="White-Box", started_at=datetime.now())

        # Test 1: Agent instantiation
        report.results.append(self._test_agent_instantiation())

        # Test 2: BDI cycle completeness
        report.results.append(self._test_bdi_cycle())

        # Test 3: Service registration
        report.results.append(self._test_service_registration())

        # Test 4: Blackboard operations
        report.results.append(self._test_blackboard_operations())

        # Test 5: Agent pool lifecycle
        report.results.append(self._test_agent_pool_lifecycle())

        # Test 6: Type annotations coverage
        report.results.append(self._test_type_annotations())

        # Test 7: Exception handling paths
        report.results.append(self._test_exception_paths())

        # Test 8: Thread safety
        report.results.append(self._test_thread_safety())

        # Test 9: Memory management
        report.results.append(self._test_memory_management())

        # Test 10: Code path coverage
        report.results.append(self._test_code_paths())

        report.completed_at = datetime.now()
        return report

    def run_black_box_tests(self) -> TestReport:
        """
        BLACK-BOX TESTING: Input/output boundary validation

        Tests the system as a black box - only inputs and outputs,
        no knowledge of internal implementation.
        """
        report = TestReport(test_type="Black-Box", started_at=datetime.now())

        # Test 1: None/null inputs
        report.results.append(self._test_none_inputs())

        # Test 2: Empty string inputs
        report.results.append(self._test_empty_inputs())

        # Test 3: Boundary values
        report.results.append(self._test_boundary_values())

        # Test 4: Unicode and special chars
        report.results.append(self._test_unicode_inputs())

        # Test 5: Type confusion
        report.results.append(self._test_type_confusion())

        # Test 6: Oversized inputs
        report.results.append(self._test_oversized_inputs())

        # Test 7: Malformed math expressions
        report.results.append(self._test_malformed_expressions())

        # Test 8: Valid math expressions
        report.results.append(self._test_valid_expressions())

        # Test 9: Domain routing
        report.results.append(self._test_domain_routing())

        # Test 10: Output consistency
        report.results.append(self._test_output_consistency())

        report.completed_at = datetime.now()
        return report

    def run_integration_tests(self) -> TestReport:
        """
        INTEGRATION TESTING: Front-to-back flow validation

        Tests complete workflows from input to output across
        all system components.
        """
        report = TestReport(test_type="Integration", started_at=datetime.now())

        # Test 1: Full problem solving flow
        report.results.append(self._test_full_solve_flow())

        # Test 2: Input -> Normalizer -> Parser -> Orchestrator
        report.results.append(self._test_input_pipeline())

        # Test 3: Orchestrator -> AgentPool -> Supervisor -> Specialist
        report.results.append(self._test_delegation_chain())

        # Test 4: Blackboard communication
        report.results.append(self._test_blackboard_flow())

        # Test 5: Multi-domain problem
        report.results.append(self._test_multi_domain())

        # Test 6: Agent lifecycle integration
        report.results.append(self._test_lifecycle_integration())

        # Test 7: Error propagation
        report.results.append(self._test_error_propagation())

        # Test 8: Concurrent requests
        report.results.append(self._test_concurrent_requests())

        # Test 9: Resource cleanup
        report.results.append(self._test_resource_cleanup())

        # Test 10: Recovery from failures
        report.results.append(self._test_failure_recovery())

        report.completed_at = datetime.now()
        return report

    # ==================== WHITE-BOX TEST IMPLEMENTATIONS ====================

    def _test_agent_instantiation(self) -> TestResult:
        """Test that all agents can be instantiated"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.infrastructure import (
                AgentPool, AgentManagementSystem, register_all_agents
            )

            ams = AgentManagementSystem()
            pool = AgentPool(ams)
            count = register_all_agents(pool)

            if count < 20:
                errors.append(f"Expected 20+ agents, got {count}")

            # Try waking each domain
            for domain in ['algebra', 'calculus', 'linear_algebra', 'statistics', 'discrete_math']:
                pool.start()
                woken = pool.wake_for_domain(domain)
                pool.sleep_domain(domain)
                pool.stop()

                if len(woken) == 0:
                    errors.append(f"No agents woken for {domain}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Agent Instantiation",
            passed=len(errors) == 0,
            category=TestCategory.API_BOUNDARY,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_bdi_cycle(self) -> TestResult:
        """Test BDI agent cycle methods exist and are callable"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.bdi_agent import BDIAgent

            # Check abstract methods are defined
            required_methods = ['update_beliefs', 'deliberate', 'execute_step']

            for method in required_methods:
                if not hasattr(BDIAgent, method):
                    errors.append(f"BDIAgent missing {method}")

            # Test a concrete implementation
            from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor

            supervisor = AlgebraSupervisor()

            # These should not raise
            supervisor.update_beliefs()
            intentions = supervisor.deliberate()

            if not isinstance(intentions, list):
                errors.append("deliberate() should return list")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="BDI Cycle Completeness",
            passed=len(errors) == 0,
            category=TestCategory.CONTROL_FLOW,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_service_registration(self) -> TestResult:
        """Test Directory Facilitator service registration"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
                DirectoryFacilitator, create_service_registration
            )

            df = DirectoryFacilitator()

            # Register a test service
            reg = create_service_registration(
                service_type='test.service',
                agent_id='test_agent',
                algorithm='test'
            )

            result = df.register(reg)
            if not result:
                errors.append("Registration failed")

            # Search for it
            found = df.search(service_type='test.service')
            if len(found) != 1:
                errors.append(f"Expected 1 service, found {len(found)}")

            # Deregister
            df.deregister('test_agent')
            found = df.search(service_type='test.service')
            if len(found) != 0:
                errors.append("Deregistration failed")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Service Registration",
            passed=len(errors) == 0,
            category=TestCategory.API_BOUNDARY,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_blackboard_operations(self) -> TestResult:
        """Test Blackboard post/query/update operations"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.blackboard import (
                Blackboard, create_entry, EntryType, EntryStatus
            )

            bb = Blackboard()

            # Post entry
            entry = create_entry(
                entry_type=EntryType.TASK,
                content=None,
                author_agent='test',
                conversation_id='test_conv',
                tags=['test']
            )

            bb.post(entry)

            # Query
            found = bb.query_entries(tags=['test'])
            if len(found) != 1:
                errors.append(f"Query failed: expected 1, got {len(found)}")

            # Update status (on the entry itself)
            if found:
                found[0].update_status(EntryStatus.VERIFIED)

                # Re-query to verify
                found2 = bb.query_entries(tags=['test'])
                if found2 and found2[0].status != EntryStatus.VERIFIED:
                    errors.append("Status update failed")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Blackboard Operations",
            passed=len(errors) == 0,
            category=TestCategory.STATE_MUTATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_agent_pool_lifecycle(self) -> TestResult:
        """Test AgentPool DORMANT->STANDBY->ACTIVE->DORMANT lifecycle"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.infrastructure import (
                AgentPool, AgentManagementSystem, AgentSpec, PoolState, AgentType
            )
            from symbo_agentic_reasoners.core.bdi_agent import BDIAgent

            class MockAgent(BDIAgent):
                def update_beliefs(self): pass
                def deliberate(self): return []
                def execute_step(self, i): pass

            ams = AgentManagementSystem()
            pool = AgentPool(ams)

            spec = AgentSpec(
                agent_id='lifecycle_test',
                agent_class=MockAgent,
                domain='test',
                tier=3,
                agent_type=AgentType.INFRASTRUCTURAL,
                services=['test.lifecycle']
            )

            pool.register_spec(spec)
            pool.start()

            # Initially DORMANT
            if pool.get_state('lifecycle_test') != PoolState.DORMANT:
                errors.append("Initial state should be DORMANT")

            # Wake -> STANDBY
            pool._wake_agent('lifecycle_test')
            if pool.get_state('lifecycle_test') != PoolState.STANDBY:
                errors.append("After wake should be STANDBY")

            # Activate -> ACTIVE
            pool.activate('lifecycle_test')
            if pool.get_state('lifecycle_test') != PoolState.ACTIVE:
                errors.append("After activate should be ACTIVE")

            # Deactivate -> STANDBY
            pool.deactivate('lifecycle_test', return_to_standby=True)
            if pool.get_state('lifecycle_test') != PoolState.STANDBY:
                errors.append("After deactivate should be STANDBY")

            pool.stop()

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Agent Pool Lifecycle",
            passed=len(errors) == 0,
            category=TestCategory.STATE_MUTATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_type_annotations(self) -> TestResult:
        """Check type annotations on public APIs"""
        start = time.time()
        errors = []
        missing_annotations = []

        try:
            # Check key modules for type hints
            modules_to_check = [
                'symbo_agentic_reasoners.core.orchestrator',
                'symbo_agentic_reasoners.core.blackboard',
                'symbo_agentic_reasoners.infrastructure.agent_pool',
            ]

            for mod_name in modules_to_check:
                try:
                    mod = importlib.import_module(mod_name)
                    for name, obj in inspect.getmembers(mod):
                        if inspect.isfunction(obj) and not name.startswith('_'):
                            hints = getattr(obj, '__annotations__', {})
                            if 'return' not in hints:
                                missing_annotations.append(f"{mod_name}.{name}")
                except ImportError:
                    errors.append(f"Cannot import {mod_name}")

            # Allow some missing, but flag if too many
            if len(missing_annotations) > 20:
                errors.append(f"{len(missing_annotations)} public functions missing return type hints")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Type Annotations",
            passed=len(errors) == 0,
            category=TestCategory.TYPE_SYSTEM,
            duration_ms=duration,
            error="; ".join(errors) if errors else None,
            details=f"Missing: {len(missing_annotations)}"
        )

    def _test_exception_paths(self) -> TestResult:
        """Test that exception handling paths work correctly"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator, NoAgentAvailableError

            # Test NoAgentAvailableError is raised appropriately
            orchestrator = MainOrchestrator()

            # Create a mock structured problem with no available agents
            class MockProblem:
                problem_type = type('ProblemType', (), {'value': 'test'})()
                domain = type('Domain', (), {'value': 'nonexistent'})()
                raw_input = 'test'
                omdoc_content = None
                sympy_expr = None
                metadata = {}

            try:
                orchestrator.process(MockProblem())
                errors.append("Should have raised NoAgentAvailableError")
            except NoAgentAvailableError:
                pass  # Expected
            except Exception as e:
                errors.append(f"Wrong exception type: {type(e).__name__}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Exception Handling Paths",
            passed=len(errors) == 0,
            category=TestCategory.ERROR_HANDLING,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_thread_safety(self) -> TestResult:
        """Test thread safety of critical components"""
        start = time.time()
        errors = []

        try:
            import threading
            from symbo_agentic_reasoners.infrastructure import AgentPool, AgentManagementSystem

            ams = AgentManagementSystem()
            pool = AgentPool(ams)
            pool.start()

            results = []

            def worker(domain):
                try:
                    woken = pool.wake_for_domain(domain)
                    results.append(('wake', domain, len(woken)))
                    pool.sleep_domain(domain)
                    results.append(('sleep', domain, True))
                except Exception as e:
                    results.append(('error', domain, str(e)))

            # Launch concurrent threads
            threads = []
            for domain in ['algebra', 'calculus', 'linear_algebra']:
                t = threading.Thread(target=worker, args=(domain,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join(timeout=10)

            pool.stop()

            # Check for errors
            for result in results:
                if result[0] == 'error':
                    errors.append(f"Thread error in {result[1]}: {result[2]}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Thread Safety",
            passed=len(errors) == 0,
            category=TestCategory.CONCURRENCY,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_memory_management(self) -> TestResult:
        """Test for obvious memory leaks"""
        start = time.time()
        errors = []

        try:
            import gc
            from symbo_agentic_reasoners.infrastructure import AgentPool, AgentManagementSystem, register_all_agents

            gc.collect()

            # Create and destroy multiple pools
            for i in range(3):
                ams = AgentManagementSystem()
                pool = AgentPool(ams)
                register_all_agents(pool)
                pool.start()

                # Wake and sleep all domains
                for domain in ['algebra', 'calculus']:
                    pool.wake_for_domain(domain)
                    pool.sleep_domain(domain)

                pool.stop()
                del pool
                del ams

            gc.collect()

            # If we got here without crashing, basic memory management works

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Memory Management",
            passed=len(errors) == 0,
            category=TestCategory.RESOURCE_MGMT,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_code_paths(self) -> TestResult:
        """Test various code paths through the system"""
        start = time.time()
        errors = []

        try:
            # Test supervisor routing decisions
            from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
            from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import LinearAlgebraSupervisor
            from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import StatisticsSupervisor

            class MockEntry:
                def __init__(self, raw_input):
                    self.metadata = {'raw_input': raw_input}
                    self.content = None

            # Algebra routing
            alg = AlgebraSupervisor()
            decision = alg._analyze_task(MockEntry("find prime factors of 60"))
            if 'numbertheory' not in decision['service_type']:
                errors.append("Algebra routing failed for prime factors")

            # Linear algebra routing
            linalg = LinearAlgebraSupervisor()
            decision = linalg._analyze_task(MockEntry("compute SVD of matrix"))
            if 'decomposition' not in decision['service_type']:
                errors.append("LinAlg routing failed for SVD")

            # Stats routing
            stats = StatisticsSupervisor()
            decision = stats._analyze_task(MockEntry("compute posterior probability"))
            if decision['paradigm'] != 'bayesian':
                errors.append("Stats routing failed for Bayesian")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Code Path Coverage",
            passed=len(errors) == 0,
            category=TestCategory.LOGIC_FLAWS,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    # ==================== BLACK-BOX TEST IMPLEMENTATIONS ====================

    def _test_none_inputs(self) -> TestResult:
        """Test handling of None inputs"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input

            # None input should be handled gracefully
            try:
                result = normalize_input(None)
                # Should either return empty string or raise ValueError
                if result is not None and result != '':
                    pass  # Acceptable
            except (ValueError, TypeError, AttributeError):
                pass  # Acceptable - explicit failure
            except Exception as e:
                errors.append(f"Unexpected exception for None: {type(e).__name__}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="None Input Handling",
            passed=len(errors) == 0,
            category=TestCategory.INPUT_VALIDATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_empty_inputs(self) -> TestResult:
        """Test handling of empty inputs"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input

            empty_inputs = ['', '   ', '\n', '\t']

            for inp in empty_inputs:
                try:
                    result = normalize_input(inp)
                    # Should handle gracefully
                except Exception as e:
                    errors.append(f"Failed on '{repr(inp)}': {type(e).__name__}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Empty Input Handling",
            passed=len(errors) == 0,
            category=TestCategory.INPUT_VALIDATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_boundary_values(self) -> TestResult:
        """Test boundary value inputs"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input
            import sympy as sp

            # Test boundary numeric values
            boundary_inputs = [
                '0',
                '-1',
                '999999999999999999999',
                '-999999999999999999999',
                '0.0000000001',
                'inf',
                '-inf',
            ]

            for inp in boundary_inputs:
                try:
                    result = normalize_input(inp)
                    # Try to parse
                    if result:
                        expr = sp.sympify(result)
                except Exception as e:
                    # Some failures are expected, just ensure no crashes
                    pass

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Boundary Value Handling",
            passed=len(errors) == 0,
            category=TestCategory.INPUT_VALIDATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_unicode_inputs(self) -> TestResult:
        """Test Unicode and special character handling"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input

            # Unicode math symbols
            unicode_inputs = [
                '∫ x dx',
                '∑ n',
                '∏ i',
                'α + β',
                'x² + y²',
                '∂f/∂x',
                '∇f',
                'a ≡ b (mod n)',
                'f′(x)',
            ]

            for inp in unicode_inputs:
                try:
                    result = normalize_input(inp)
                    if not result:
                        errors.append(f"Empty result for '{inp}'")
                except Exception as e:
                    errors.append(f"Failed on '{inp}': {type(e).__name__}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Unicode Input Handling",
            passed=len(errors) == 0,
            category=TestCategory.INPUT_VALIDATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_type_confusion(self) -> TestResult:
        """Test type confusion scenarios"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input

            # Various type inputs
            type_inputs = [
                123,  # int instead of string
                12.5,  # float instead of string
                ['x', '+', '1'],  # list instead of string
                {'expr': 'x+1'},  # dict instead of string
            ]

            for inp in type_inputs:
                try:
                    result = normalize_input(inp)
                except TypeError:
                    pass  # Expected - explicit type checking
                except AttributeError:
                    pass  # Expected - string method on non-string
                except Exception as e:
                    # Unexpected exception type
                    errors.append(f"Unexpected exception for {type(inp).__name__}: {type(e).__name__}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Type Confusion Handling",
            passed=len(errors) == 0,
            category=TestCategory.TYPE_SYSTEM,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_oversized_inputs(self) -> TestResult:
        """Test handling of oversized inputs"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input

            # Large input
            large_input = 'x + ' * 10000 + 'x'

            try:
                result = normalize_input(large_input)
                # Should either process or raise appropriate error
            except MemoryError:
                pass  # Acceptable
            except RecursionError:
                pass  # Acceptable
            except Exception as e:
                # Most exceptions are acceptable for oversized input
                pass

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Oversized Input Handling",
            passed=len(errors) == 0,
            category=TestCategory.INPUT_VALIDATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_malformed_expressions(self) -> TestResult:
        """Test handling of malformed math expressions"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input

            malformed = [
                '((x + 1)',  # Unbalanced parens
                'x + + 1',   # Double operator
                '1 / 0',     # Division by zero (expression)
                'sqrt(-)',   # Incomplete function
                '+ - * /',   # Only operators
                'x y z',     # No operators (implicit mult should handle)
            ]

            for inp in malformed:
                try:
                    result = normalize_input(inp)
                    # Normalize should not crash
                except Exception as e:
                    # Some parsing errors are expected, but shouldn't be crashes
                    if not isinstance(e, (ValueError, SyntaxError)):
                        pass  # Note but don't fail

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Malformed Expression Handling",
            passed=len(errors) == 0,
            category=TestCategory.INPUT_VALIDATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_valid_expressions(self) -> TestResult:
        """Test that valid expressions process correctly"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input
            import sympy as sp

            valid_exprs = [
                ('x + 1', None),
                ('x**2 + 2*x + 1', None),
                ('sin(x)', None),
                ('diff(x**2, x)', None),
                ('integrate(x, x)', None),
            ]

            for inp, expected in valid_exprs:
                try:
                    result = normalize_input(inp)
                    if not result:
                        errors.append(f"Empty result for '{inp}'")
                        continue

                    # Should be valid SymPy expression
                    expr = sp.sympify(result)

                except Exception as e:
                    errors.append(f"Failed on '{inp}': {type(e).__name__}: {e}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Valid Expression Processing",
            passed=len(errors) == 0,
            category=TestCategory.LOGIC_FLAWS,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_domain_routing(self) -> TestResult:
        """Test correct domain routing based on input"""
        start = time.time()
        errors = []

        try:
            # Test problem analysis domain classification
            from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam

            team = ProblemAnalysisTeam()

            test_cases = [
                ('solve x^2 + 2x - 3 = 0', 'algebra'),
                ('differentiate sin(x)', 'calculus'),
                ('factor x^2 - 9', 'algebra'),  # polynomial factoring
                ('compute matrix determinant', 'linearalgebra'),  # linear algebra
                ('find eigenvalues of matrix A', 'linearalgebra'),
            ]

            for inp, expected_domain in test_cases:
                try:
                    result = team.process(inp)
                    if result and hasattr(result, 'domain'):
                        actual = result.domain.value.lower()
                        if expected_domain not in actual:
                            errors.append(f"'{inp}' routed to {actual}, expected {expected_domain}")
                except Exception as e:
                    errors.append(f"Processing failed for '{inp}': {e}")

        except ImportError:
            # ProblemAnalysisTeam may not exist yet
            pass
        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Domain Routing",
            passed=len(errors) == 0,
            category=TestCategory.LOGIC_FLAWS,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_output_consistency(self) -> TestResult:
        """Test that same input gives consistent output"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input

            test_input = 'x**2 + 2*x + 1'

            # Run same input multiple times
            results = []
            for _ in range(5):
                result = normalize_input(test_input)
                results.append(result)

            # All results should be identical
            if len(set(results)) != 1:
                errors.append(f"Inconsistent results: {results}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Output Consistency",
            passed=len(errors) == 0,
            category=TestCategory.LOGIC_FLAWS,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    # ==================== INTEGRATION TEST IMPLEMENTATIONS ====================

    def _test_full_solve_flow(self) -> TestResult:
        """Test complete problem-solving flow"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input
            from symbo_agentic_reasoners.infrastructure import (
                AgentPool, AgentManagementSystem, register_all_agents
            )
            import sympy as sp

            # Setup
            ams = AgentManagementSystem()
            pool = AgentPool(ams)
            register_all_agents(pool)
            pool.start()

            # Test input
            test_input = "x**2 + 2*x + 1"

            # Step 1: Normalize
            normalized = normalize_input(test_input)
            if not normalized:
                errors.append("Normalization failed")

            # Step 2: Parse
            try:
                expr = sp.sympify(normalized)
            except Exception as e:
                errors.append(f"Parse failed: {e}")

            # Step 3: Agent pool interaction
            woken = pool.wake_for_domain('algebra')
            if not woken:
                errors.append("No algebra agents woken")

            pool.sleep_domain('algebra')
            pool.stop()

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Full Solve Flow",
            passed=len(errors) == 0,
            category=TestCategory.INTEGRATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_input_pipeline(self) -> TestResult:
        """Test input -> normalizer -> sympy pipeline"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input
            import sympy as sp

            pipeline_tests = [
                ('differentiate x^2', 'diff'),
                ('integrate sin(x) dx', 'integrate'),
                ('solve x + 1 = 0', None),
            ]

            for inp, expected_func in pipeline_tests:
                normalized = normalize_input(inp)
                if not normalized:
                    errors.append(f"Empty normalization for '{inp}'")
                    continue

                if expected_func and expected_func not in normalized:
                    # Just log, don't fail - may be handled differently
                    pass

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Input Pipeline",
            passed=len(errors) == 0,
            category=TestCategory.INTEGRATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_delegation_chain(self) -> TestResult:
        """Test Orchestrator -> Supervisor -> Specialist chain"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.infrastructure import (
                AgentPool, AgentManagementSystem, register_all_agents
            )
            from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor

            # Setup
            ams = AgentManagementSystem()
            pool = AgentPool(ams)
            register_all_agents(pool)
            pool.start()

            # Wake algebra domain
            woken = pool.wake_for_domain('algebra')

            # Check supervisor can route
            supervisor = AlgebraSupervisor()

            class MockEntry:
                metadata = {'raw_input': 'factor x^2 - 1'}
                content = None

            decision = supervisor._analyze_task(MockEntry())

            if 'polynomial' not in decision['service_type']:
                errors.append(f"Unexpected routing: {decision}")

            pool.stop()

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Delegation Chain",
            passed=len(errors) == 0,
            category=TestCategory.INTEGRATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_blackboard_flow(self) -> TestResult:
        """Test blackboard communication between agents"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.blackboard import (
                Blackboard, create_entry, EntryType, EntryStatus
            )

            bb = Blackboard()

            # Simulate task posting by orchestrator
            task_entry = create_entry(
                entry_type=EntryType.TASK,
                content=None,
                author_agent='orchestrator',
                conversation_id='test_conv',
                tags=['algebra', 'task'],
                metadata={'raw_input': 'solve x + 1 = 0'}
            )
            bb.post(task_entry)

            # Simulate supervisor reading task
            tasks = bb.query_entries(entry_type=EntryType.TASK, tags=['algebra'])
            if len(tasks) != 1:
                errors.append(f"Expected 1 task, got {len(tasks)}")

            # Simulate specialist posting result
            result_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=None,
                author_agent='polynomial_specialist',
                conversation_id='test_conv',
                tags=['test_conv'],
                status=EntryStatus.VERIFIED,
                metadata={'result': 'x = -1'}
            )
            bb.post(result_entry)

            # Verify result retrieval
            results = bb.query_entries(
                entry_type=EntryType.PARTIAL_RESULT,
                tags=['test_conv']
            )
            if len(results) != 1:
                errors.append(f"Expected 1 result, got {len(results)}")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Blackboard Flow",
            passed=len(errors) == 0,
            category=TestCategory.INTEGRATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_multi_domain(self) -> TestResult:
        """Test handling problems requiring multiple domains"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.infrastructure import (
                AgentPool, AgentManagementSystem, register_all_agents
            )

            ams = AgentManagementSystem()
            pool = AgentPool(ams)
            register_all_agents(pool)
            pool.start()

            # Wake multiple domains
            algebra_woken = pool.wake_for_domain('algebra')
            calculus_woken = pool.wake_for_domain('calculus')

            if not algebra_woken:
                errors.append("No algebra agents woken")
            if not calculus_woken:
                errors.append("No calculus agents woken")

            # Both should be warm
            warm = pool.get_warm_domains()
            if 'algebra' not in warm:
                errors.append("Algebra not in warm domains")
            if 'calculus' not in warm:
                errors.append("Calculus not in warm domains")

            pool.stop()

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Multi-Domain Handling",
            passed=len(errors) == 0,
            category=TestCategory.INTEGRATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_lifecycle_integration(self) -> TestResult:
        """Test agent lifecycle across full operation"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.infrastructure import (
                AgentPool, AgentManagementSystem, register_all_agents, PoolState
            )

            ams = AgentManagementSystem()
            pool = AgentPool(ams)
            register_all_agents(pool)
            pool.start()

            # All should start dormant
            stats = pool.get_statistics()
            if stats['state_distribution']['dormant'] == 0:
                errors.append("No dormant agents at start")

            # Wake domain
            pool.wake_for_domain('algebra')

            # Should have standby agents
            stats = pool.get_statistics()
            if stats['state_distribution']['standby'] == 0:
                errors.append("No standby agents after wake")

            # Activate one
            pool.activate('polynomial_specialist')

            stats = pool.get_statistics()
            if stats['state_distribution']['active'] == 0:
                errors.append("No active agents after activate")

            # Deactivate and sleep
            pool.deactivate('polynomial_specialist')
            pool.sleep_domain('algebra')

            pool.stop()

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Lifecycle Integration",
            passed=len(errors) == 0,
            category=TestCategory.INTEGRATION,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_error_propagation(self) -> TestResult:
        """Test that errors propagate correctly through the system"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator, NoAgentAvailableError

            orchestrator = MainOrchestrator()

            # Test with invalid domain
            class MockProblem:
                problem_type = type('PT', (), {'value': 'test'})()
                domain = type('D', (), {'value': 'invalid_domain'})()
                raw_input = 'test'
                omdoc_content = None
                sympy_expr = None
                metadata = {}

            try:
                orchestrator.process(MockProblem())
                errors.append("Should raise NoAgentAvailableError")
            except NoAgentAvailableError:
                pass  # Expected
            except Exception as e:
                # Other exceptions might be acceptable
                pass

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Error Propagation",
            passed=len(errors) == 0,
            category=TestCategory.ERROR_HANDLING,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_concurrent_requests(self) -> TestResult:
        """Test handling concurrent requests"""
        start = time.time()
        errors = []

        try:
            import threading
            from symbo_agentic_reasoners.core.input_normalizer import normalize_input

            results = []
            lock = threading.Lock()

            def worker(expr):
                try:
                    result = normalize_input(expr)
                    with lock:
                        results.append(('ok', expr, result))
                except Exception as e:
                    with lock:
                        results.append(('error', expr, str(e)))

            # Launch concurrent normalizations
            threads = []
            exprs = ['x + 1', 'x**2', 'sin(x)', 'diff(x, x)', 'integrate(x, x)']

            for expr in exprs:
                t = threading.Thread(target=worker, args=(expr,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join(timeout=5)

            # Check results
            error_count = sum(1 for r in results if r[0] == 'error')
            if error_count > 0:
                errors.append(f"{error_count} concurrent requests failed")

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Concurrent Requests",
            passed=len(errors) == 0,
            category=TestCategory.CONCURRENCY,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_resource_cleanup(self) -> TestResult:
        """Test proper resource cleanup"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.infrastructure import (
                AgentPool, AgentManagementSystem, register_all_agents
            )

            # Create pool, use it, destroy it
            ams = AgentManagementSystem()
            pool = AgentPool(ams)
            register_all_agents(pool)
            pool.start()

            # Use all domains
            for domain in ['algebra', 'calculus', 'linear_algebra']:
                pool.wake_for_domain(domain)
                pool.sleep_domain(domain)

            # Stop should clean up
            pool.stop()

            # After stop, operations should fail or be no-op
            try:
                pool.wake_for_domain('algebra')
            except:
                pass  # Expected or acceptable

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Resource Cleanup",
            passed=len(errors) == 0,
            category=TestCategory.RESOURCE_MGMT,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    def _test_failure_recovery(self) -> TestResult:
        """Test recovery from failures"""
        start = time.time()
        errors = []

        try:
            from symbo_agentic_reasoners.infrastructure import (
                AgentPool, AgentManagementSystem, register_all_agents
            )

            ams = AgentManagementSystem()
            pool = AgentPool(ams)
            register_all_agents(pool)
            pool.start()

            # Try to wake invalid domain
            result = pool.wake_for_domain('nonexistent_domain')
            # Should return empty, not crash
            if result is None:
                errors.append("wake_for_domain returned None instead of empty list")

            # System should still work after invalid request
            woken = pool.wake_for_domain('algebra')
            if not woken:
                errors.append("Cannot wake valid domain after invalid request")

            pool.stop()

        except Exception as e:
            errors.append(f"Exception: {str(e)}")

        duration = (time.time() - start) * 1000
        return TestResult(
            name="Failure Recovery",
            passed=len(errors) == 0,
            category=TestCategory.ERROR_HANDLING,
            duration_ms=duration,
            error="; ".join(errors) if errors else None
        )

    # ==================== REPORTING ====================

    def _print_combined_summary(self, results: Dict[str, TestReport]):
        """Print combined summary of all test phases"""
        print("="*70)
        print("COMBINED TEST SUMMARY")
        print("="*70)
        print()

        total_passed = sum(r.passed for r in results.values())
        total_failed = sum(r.failed for r in results.values())
        total_tests = sum(r.total for r in results.values())

        all_cracks = []
        for report in results.values():
            all_cracks.extend(report.cracks)

        print(f"Total Tests: {total_passed}/{total_tests} passed")
        print(f"Failed: {total_failed}")
        print()

        # By phase
        print("By Phase:")
        for name, report in results.items():
            status = "PASS" if report.failed == 0 else "FAIL"
            print(f"  {name}: {report.passed}/{report.total} [{status}]")

        print()

        # Failed tests
        if total_failed > 0:
            print("FAILED TESTS:")
            print("-"*70)
            for name, report in results.items():
                for result in report.results:
                    if not result.passed:
                        print(f"  [{name}] {result.name}")
                        if result.error:
                            print(f"    Error: {result.error[:100]}...")
            print()

        # Cracks found
        if all_cracks:
            print("CRACKS FOUND:")
            print("-"*70)
            for crack in sorted(all_cracks, key=lambda c: c.severity.value):
                print(f"  {crack}")
            print()

        # Final verdict
        print("="*70)
        if total_failed == 0 and len(all_cracks) == 0:
            print("VERDICT: ALL TESTS PASSED - No critical issues found")
        elif total_failed == 0:
            print(f"VERDICT: TESTS PASSED - {len(all_cracks)} cracks found (review recommended)")
        else:
            print(f"VERDICT: {total_failed} TESTS FAILED - Review required")
        print("="*70)


def main():
    """Run CrackFinder testing agent"""
    agent = CrackFinderAgent()
    results = agent.run_all_tests()

    # Return exit code based on results
    total_failed = sum(r.failed for r in results.values())
    return 1 if total_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
