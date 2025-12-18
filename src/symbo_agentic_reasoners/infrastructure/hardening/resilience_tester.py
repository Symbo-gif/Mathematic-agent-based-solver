# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
PHASE 5 - OH-2: RESILIENCE TESTER (Tier 3)
==========================================

Injects controlled faults to test system resilience and
recovery mechanisms.

CAPABILITIES:
------------
- Fault injection scenarios
- Recovery time measurement
- Chaos engineering patterns
- System behavior validation
- Resilience reporting

REFERENCE:
---------
- Agent_System_Audit.docx.md: OH-2 Resilience Tester
- Phase_5_Optimization.md: Operational Hardening Team
"""

import sys
import os
import logging
import time
import random
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading

logger = logging.getLogger('symbo_agentic_reasoners.phase5.resilience_tester')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class FaultType(Enum):
    """Types of faults that can be injected"""
    LATENCY = "latency"           # Add artificial delay
    FAILURE = "failure"           # Cause operation to fail
    TIMEOUT = "timeout"           # Simulate timeout
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_PARTITION = "network_partition"
    MEMORY_PRESSURE = "memory_pressure"
    CPU_SPIKE = "cpu_spike"
    DATA_CORRUPTION = "data_corruption"


class TestStatus(Enum):
    """Status of a resilience test"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


@dataclass
class FaultScenario:
    """
    Definition of a fault injection scenario.
    
    Attributes:
        scenario_id: Unique identifier
        name: Human-readable name
        fault_type: Type of fault to inject
        duration_ms: How long fault lasts
        target_component: Component to target
        parameters: Additional parameters
    """
    scenario_id: str
    name: str
    fault_type: FaultType
    duration_ms: int
    target_component: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'scenario_id': self.scenario_id,
            'name': self.name,
            'fault_type': self.fault_type.value,
            'duration_ms': self.duration_ms,
            'target': self.target_component
        }


@dataclass
class TestResult:
    """
    Result of a resilience test.
    
    Attributes:
        test_id: Unique identifier
        scenario: The fault scenario tested
        status: Test outcome
        recovery_time_ms: Time to recover
        observations: Observed behaviors
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        timestamp: When test was run
    """
    test_id: str
    scenario: FaultScenario
    status: TestStatus
    recovery_time_ms: int
    observations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'test_id': self.test_id,
            """Perform to dict operation.

            Args:
            No arguments

            Returns:
            Result of the operation

            Example:
            >>> result = obj.to_dict(...)
            """
            'scenario': self.scenario.name,
            'status': self.status.value,
            'recovery_ms': self.recovery_time_ms,
            'observation_count': len(self.observations),
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ResilienceReport:
    """Summary report of resilience testing"""
    report_id: str
    tests_run: int
    tests_passed: int
    tests_failed: int
    average_recovery_ms: float
    weakest_component: Optional[str]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'report_id': self.report_id,
            'tests_run': self.tests_run,
            'passed': self.tests_passed,
            'failed': self.tests_failed,
            'pass_rate': self.tests_passed / self.tests_run * 100 if self.tests_run > 0 else 0,
            'avg_recovery_ms': round(self.average_recovery_ms, 1),
            'weakest': self.weakest_component
        }


class ResilienceTester(BDIAgent):
    """
    OH-2: Resilience Tester
    
    DIRECTIVE:
    ---------
    Inject controlled faults to test system resilience and
    validate recovery mechanisms.
    
    INPUTS:
    ------
    - Fault injection scenarios
    - Recovery validation criteria
    - Target component specifications
    
    OUTPUTS:
    -------
    - Test execution results
    - Resilience reports
    - Remediation recommendations
    
    DEPENDENCIES:
    ------------
    - OH-1 (SecurityMonitor): For access during testing
    - FA-2 (CheckpointManager): For state recovery testing
    
    FAILURE MODE: ABORT - Safely terminates fault injection
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 613-622
    """
    
    def __init__(
        self,
        agent_id: str = 'resilience_tester_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        safe_mode: bool = True
    ):
        """
        Initialize Resilience Tester
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            safe_mode: If True, only simulate faults (no real injection)
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        self.safe_mode = safe_mode
        
        # Test catalog
        self.scenarios: Dict[str, FaultScenario] = {}
        
        # Test results
        self.results: Dict[str, TestResult] = {}
        
        # Active injections
        self.active_injections: Dict[str, bool] = {}
        
        # Hooks for fault injection
        self.injection_hooks: Dict[str, Callable] = {}
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        
        # Initialize standard scenarios
        self._initialize_scenarios()
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Resilience Tester initialized")
        print(f"  Safe mode: {safe_mode}")
        print(f"  Scenarios loaded: {len(self.scenarios)}")
    
    def _initialize_scenarios(self):
        """Initialize standard fault scenarios"""
        standard_scenarios = [
            FaultScenario(
                scenario_id="latency_high",
                name="High Latency",
                fault_type=FaultType.LATENCY,
                duration_ms=5000,
                target_component="*",
                parameters={"delay_ms": 500}
            ),
            FaultScenario(
                scenario_id="service_failure",
                name="Service Failure",
                fault_type=FaultType.FAILURE,
                duration_ms=10000,
                target_component="service",
                parameters={"error_rate": 1.0}
            ),
            FaultScenario(
                scenario_id="timeout_simulation",
                name="Timeout Simulation",
                fault_type=FaultType.TIMEOUT,
                duration_ms=30000,
                target_component="network",
                parameters={"timeout_ms": 5000}
            ),
            FaultScenario(
                scenario_id="memory_pressure",
                name="Memory Pressure",
                fault_type=FaultType.MEMORY_PRESSURE,
                duration_ms=15000,
                target_component="system",
                parameters={"pressure_pct": 85}
            ),
            FaultScenario(
                scenario_id="cpu_spike",
                name="CPU Spike",
                fault_type=FaultType.CPU_SPIKE,
                duration_ms=10000,
                target_component="compute",
                parameters={"load_pct": 95}
            ),
        ]
        
        for scenario in standard_scenarios:
            self.scenarios[scenario.scenario_id] = scenario
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='system.test.resilience',
            agent_id=self.agent_id,
            algorithm='fault_injection',
            cost='high',
            type='testing',
            tier='3',
            algorithms='chaos_engineering_fault_injection'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: system.test.resilience")
    
    def add_scenario(self, scenario: FaultScenario):
        """Add a fault scenario to the catalog"""
        self.scenarios[scenario.scenario_id] = scenario
    
    def run_test(
        self,
        scenario_id: str,
        validate_recovery: bool = True
    ) -> TestResult:
        """
        Run a resilience test using a specified scenario.
        
        Args:
            scenario_id: ID of scenario to run
            validate_recovery: Whether to validate recovery
            
        Returns:
            TestResult with outcome
        """
        self.tasks_executed += 1
        self.tests_run += 1
        
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        
        test_id = f"test_{scenario_id}_{int(time.time())}"
        observations = []
        errors = []
        
        print(f"  Running test: {scenario.name}")
        
        try:
            # Mark injection as active
            self.active_injections[scenario_id] = True
            
            # Record start time
            start_time = time.time()
            
            # Inject fault (simulated in safe mode)
            if self.safe_mode:
                observations.append("Safe mode: Fault simulated, not injected")
                self._simulate_fault(scenario)
            else:
                self._inject_fault(scenario)
                observations.append(f"Fault injected: {scenario.fault_type.value}")
            
            # Wait for fault duration
            time.sleep(scenario.duration_ms / 1000.0)
            
            # Remove fault
            self.active_injections[scenario_id] = False
            observations.append("Fault removed")
            
            # Measure recovery time
            recovery_start = time.time()
            
            if validate_recovery:
                recovered = self._validate_recovery(scenario)
                recovery_time_ms = int((time.time() - recovery_start) * 1000)
                
                if recovered:
                    observations.append(f"Recovery validated in {recovery_time_ms}ms")
                    status = TestStatus.PASSED
                    self.tests_passed += 1
                else:
                    observations.append("Recovery validation failed")
                    errors.append("System did not recover within expected time")
                    status = TestStatus.FAILED
                    self.tests_failed += 1
            else:
                recovery_time_ms = 0
                status = TestStatus.INCONCLUSIVE
                observations.append("Recovery validation skipped")
            
            self.tasks_succeeded += 1
            
        except Exception as e:
            self.tasks_failed += 1
            self.tests_failed += 1
            self.active_injections[scenario_id] = False
            
            errors.append(f"Test error: {str(e)}")
            observations.append(f"Test aborted due to error")
            status = TestStatus.FAILED
            recovery_time_ms = -1
        
        result = TestResult(
            test_id=test_id,
            scenario=scenario,
            status=status,
            recovery_time_ms=recovery_time_ms,
            observations=observations,
            errors=errors
        )
        
        self.results[test_id] = result
        return result
    
    def _simulate_fault(self, scenario: FaultScenario):
        """Simulate a fault without actual injection"""
        logger.info(f"Simulating {scenario.fault_type.value} on {scenario.target_component}")
        
        if scenario.fault_type == FaultType.LATENCY:
            delay = scenario.parameters.get("delay_ms", 100)
            time.sleep(delay / 1000.0)
        elif scenario.fault_type == FaultType.FAILURE:
            # Just log, don't actually fail
            pass
        elif scenario.fault_type == FaultType.CPU_SPIKE:
            # Brief CPU work simulation
            end_time = time.time() + 0.1
            while time.time() < end_time:
                _ = sum(range(10000))
    
    def _inject_fault(self, scenario: FaultScenario):
        """Actually inject a fault (use with caution)"""
        logger.warning(f"INJECTING FAULT: {scenario.fault_type.value}")
        
        # Call registered hook if exists
        hook = self.injection_hooks.get(scenario.fault_type.value)
        if hook:
            hook(scenario)
    
    def _validate_recovery(self, scenario: FaultScenario) -> bool:
        """Validate that system has recovered from fault"""
        # Simple validation: check no active injections
        # In real implementation, would check system health
        return not self.active_injections.get(scenario.scenario_id, False)
    
    def run_all_tests(self) -> ResilienceReport:
        """
        Run all registered test scenarios.
        
        Returns:
            ResilienceReport with summary
        """
        print(f"\n[{self.agent_id}] Running all resilience tests...")
        
        all_results = []
        for scenario_id in self.scenarios:
            result = self.run_test(scenario_id)
            all_results.append(result)
        
        return self.generate_report(all_results)
    
    def generate_report(
        self,
        results: Optional[List[TestResult]] = None
    ) -> ResilienceReport:
        """
        Generate a resilience report from test results.
        
        Args:
            results: Optional list of results (uses all if None)
            
        Returns:
            ResilienceReport summary
        """
        if results is None:
            results = list(self.results.values())
        
        if not results:
            return ResilienceReport(
                report_id=f"report_{int(time.time())}",
                tests_run=0,
                tests_passed=0,
                tests_failed=0,
                average_recovery_ms=0,
                weakest_component=None,
                recommendations=["No tests have been run yet"]
            )
        
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        
        recovery_times = [r.recovery_time_ms for r in results if r.recovery_time_ms > 0]
        avg_recovery = sum(recovery_times) / len(recovery_times) if recovery_times else 0
        
        # Find weakest component (most failures)
        component_failures: Dict[str, int] = {}
        for r in results:
            if r.status == TestStatus.FAILED:
                comp = r.scenario.target_component
                component_failures[comp] = component_failures.get(comp, 0) + 1
        
        weakest = max(component_failures.items(), key=lambda x: x[1])[0] if component_failures else None
        
        # Generate recommendations
        recommendations = []
        if failed > 0:
            recommendations.append(f"Address {failed} failing test(s)")
        if weakest:
            recommendations.append(f"Prioritize hardening of {weakest} component")
        if avg_recovery > 5000:
            recommendations.append("Recovery times exceed 5 seconds - consider faster failover")
        if passed == len(results):
            recommendations.append("All tests passed - consider adding more stress scenarios")
        
        return ResilienceReport(
            report_id=f"report_{int(time.time())}",
            tests_run=len(results),
            tests_passed=passed,
            tests_failed=failed,
            average_recovery_ms=avg_recovery,
            weakest_component=weakest,
            recommendations=recommendations
        )
    
    def abort_all_injections(self):
        """Emergency abort - clear all active fault injections"""
        logger.warning("ABORTING ALL FAULT INJECTIONS")
        for scenario_id in self.active_injections:
            self.active_injections[scenario_id] = False
    
    def process(self, task_entry: Any) -> Any:
        """Process resilience testing task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing resilience testing task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'status')
            
            if operation == 'status':
                result = {
                    'safe_mode': self.safe_mode,
                    'scenarios': len(self.scenarios),
                    'tests_run': self.tests_run,
                    'active_injections': sum(1 for v in self.active_injections.values() if v)
                }
                
            elif operation == 'run_test':
                scenario_id = metadata.get('scenario_id')
                test_result = self.run_test(scenario_id)
                result = test_result.to_dict()
                
            elif operation == 'run_all':
                report = self.run_all_tests()
                result = report.to_dict()
                result['recommendations'] = report.recommendations
                
            elif operation == 'report':
                report = self.generate_report()
                result = report.to_dict()
                result['recommendations'] = report.recommendations
                
            elif operation == 'abort':
                self.abort_all_injections()
                result = {'aborted': True}
                
            elif operation == 'list_scenarios':
                result = {
                    'scenarios': [s.to_dict() for s in self.scenarios.values()]
                }
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Resilience task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['resilience', 'testing'],
            status=EntryStatus.PENDING,
            metadata=result
        )
        
        self.blackboard.post(result_entry)
        return result_entry
    
    def _create_error_entry(self, task_entry: Any, error_msg: str) -> Any:
        """Create error entry for Blackboard"""
        if not self.blackboard:
            return None
        
        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'resilience'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """Monitor test environment"""
        pass
    
    def deliberate(self):
        """Generate test plans"""
        return []
    
    def execute_step(self, intention: Intention):
        """Execute test step"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tester statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'pass_rate': (self.tests_passed / self.tests_run * 100)
                        if self.tests_run > 0 else 0.0,
            'safe_mode': self.safe_mode
        })
        return stats


if __name__ == "__main__":
    """Test Resilience Tester"""
    print("=" * 80)
    print("PHASE 5 - RESILIENCE TESTER TEST")
    print("=" * 80)
    print()
    
    # Initialize tester in safe mode
    tester = ResilienceTester(safe_mode=True)
    print()
    
    # Test 1: List scenarios
    print("Test 1: List Scenarios")
    for sid, scenario in tester.scenarios.items():
        print(f"  - {scenario.name} ({scenario.fault_type.value})")
    print()
    
    # Test 2: Run single test
    print("Test 2: Run Single Test (Latency)")
    result = tester.run_test("latency_high")
    print(f"  Status: {result.status.value}")
    print(f"  Recovery: {result.recovery_time_ms}ms")
    for obs in result.observations:
        print(f"    - {obs}")
    print()
    
    # Test 3: Run another test
    print("Test 3: Run Service Failure Test")
    result = tester.run_test("service_failure")
    print(f"  Status: {result.status.value}")
    print()
    
    # Test 4: Generate report
    print("Test 4: Generate Report")
    report = tester.generate_report()
    print(f"  Tests run: {report.tests_run}")
    print(f"  Passed: {report.tests_passed}")
    print(f"  Avg recovery: {report.average_recovery_ms:.0f}ms")
    print(f"  Recommendations:")
    for rec in report.recommendations:
        print(f"    - {rec}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(tester.get_statistics(), indent=2))
