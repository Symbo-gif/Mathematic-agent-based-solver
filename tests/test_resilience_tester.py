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
Resilience Tester Tests
=======================

Comprehensive tests for the Resilience Tester module:
- FaultType enum
- TestStatus enum
- FaultScenario dataclass
- TestResult dataclass
- ResilienceReport dataclass
- ResilienceTester BDI agent
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from symbo_agentic_reasoners.infrastructure.hardening.resilience_tester import (
    ResilienceTester,
    FaultType,
    TestStatus,
    FaultScenario,
    TestResult,
    ResilienceReport,
)


# =============================================================================
# FaultType Tests
# =============================================================================


class TestFaultType:
    """Tests for FaultType enum."""

    def test_fault_types_exist(self):
        """Should have all fault types."""
        assert FaultType.LATENCY.value == "latency"
        assert FaultType.FAILURE.value == "failure"
        assert FaultType.TIMEOUT.value == "timeout"
        assert FaultType.RESOURCE_EXHAUSTION.value == "resource_exhaustion"
        assert FaultType.NETWORK_PARTITION.value == "network_partition"
        assert FaultType.MEMORY_PRESSURE.value == "memory_pressure"
        assert FaultType.CPU_SPIKE.value == "cpu_spike"
        assert FaultType.DATA_CORRUPTION.value == "data_corruption"

    def test_fault_type_count(self):
        """Should have correct number of fault types."""
        assert len(FaultType) == 8


# =============================================================================
# TestStatus Tests
# =============================================================================


class TestTestStatus:
    """Tests for TestStatus enum."""

    def test_test_statuses_exist(self):
        """Should have all test statuses."""
        assert TestStatus.PENDING.value == "pending"
        assert TestStatus.RUNNING.value == "running"
        assert TestStatus.PASSED.value == "passed"
        assert TestStatus.FAILED.value == "failed"
        assert TestStatus.INCONCLUSIVE.value == "inconclusive"

    def test_test_status_count(self):
        """Should have correct number of statuses."""
        assert len(TestStatus) == 5


# =============================================================================
# FaultScenario Tests
# =============================================================================


class TestFaultScenario:
    """Tests for FaultScenario dataclass."""

    def test_create_fault_scenario(self):
        """Should create scenario with all fields."""
        scenario = FaultScenario(
            scenario_id="test_scenario",
            name="Test Scenario",
            fault_type=FaultType.LATENCY,
            duration_ms=5000,
            target_component="service",
            parameters={"delay_ms": 100}
        )

        assert scenario.scenario_id == "test_scenario"
        assert scenario.name == "Test Scenario"
        assert scenario.fault_type == FaultType.LATENCY
        assert scenario.duration_ms == 5000
        assert scenario.target_component == "service"
        assert scenario.parameters["delay_ms"] == 100

    def test_fault_scenario_default_parameters(self):
        """Should default parameters to empty dict."""
        scenario = FaultScenario(
            scenario_id="simple",
            name="Simple",
            fault_type=FaultType.FAILURE,
            duration_ms=1000,
            target_component="*"
        )

        assert scenario.parameters == {}

    def test_fault_scenario_to_dict(self):
        """Should convert to dictionary."""
        scenario = FaultScenario(
            scenario_id="test_id",
            name="Test Name",
            fault_type=FaultType.TIMEOUT,
            duration_ms=3000,
            target_component="network"
        )

        d = scenario.to_dict()

        assert d["scenario_id"] == "test_id"
        assert d["name"] == "Test Name"
        assert d["fault_type"] == "timeout"
        assert d["duration_ms"] == 3000
        assert d["target"] == "network"


# =============================================================================
# TestResult Tests
# =============================================================================


class TestTestResult:
    """Tests for TestResult dataclass."""

    @pytest.fixture
    def sample_scenario(self):
        """Create sample scenario for tests."""
        return FaultScenario(
            scenario_id="sample",
            name="Sample Scenario",
            fault_type=FaultType.LATENCY,
            duration_ms=1000,
            target_component="service"
        )

    def test_create_test_result(self, sample_scenario):
        """Should create result with all fields."""
        result = TestResult(
            test_id="test_001",
            scenario=sample_scenario,
            status=TestStatus.PASSED,
            recovery_time_ms=150,
            observations=["Fault injected", "Recovery complete"]
        )

        assert result.test_id == "test_001"
        assert result.scenario is sample_scenario
        assert result.status == TestStatus.PASSED
        assert result.recovery_time_ms == 150
        assert len(result.observations) == 2

    def test_test_result_default_timestamp(self, sample_scenario):
        """Should default timestamp to now."""
        result = TestResult(
            test_id="test",
            scenario=sample_scenario,
            status=TestStatus.PENDING,
            recovery_time_ms=0,
            observations=[]
        )

        assert isinstance(result.timestamp, datetime)

    def test_test_result_default_errors(self, sample_scenario):
        """Should default errors to empty list."""
        result = TestResult(
            test_id="test",
            scenario=sample_scenario,
            status=TestStatus.PASSED,
            recovery_time_ms=100,
            observations=[]
        )

        assert result.errors == []

    def test_test_result_with_errors(self, sample_scenario):
        """Should accept errors list."""
        result = TestResult(
            test_id="test",
            scenario=sample_scenario,
            status=TestStatus.FAILED,
            recovery_time_ms=-1,
            observations=["Test aborted"],
            errors=["Connection refused", "Timeout exceeded"]
        )

        assert len(result.errors) == 2
        assert "Connection refused" in result.errors

    def test_test_result_to_dict(self, sample_scenario):
        """Should convert to dictionary."""
        result = TestResult(
            test_id="test_123",
            scenario=sample_scenario,
            status=TestStatus.PASSED,
            recovery_time_ms=200,
            observations=["obs1", "obs2", "obs3"]
        )

        d = result.to_dict()

        assert d["test_id"] == "test_123"
        assert d["scenario"] == "Sample Scenario"
        assert d["status"] == "passed"
        assert d["recovery_ms"] == 200
        assert d["observation_count"] == 3
        assert "timestamp" in d


# =============================================================================
# ResilienceReport Tests
# =============================================================================


class TestResilienceReport:
    """Tests for ResilienceReport dataclass."""

    def test_create_resilience_report(self):
        """Should create report with all fields."""
        report = ResilienceReport(
            report_id="report_001",
            tests_run=10,
            tests_passed=8,
            tests_failed=2,
            average_recovery_ms=250.5,
            weakest_component="network",
            recommendations=["Improve network handling"]
        )

        assert report.report_id == "report_001"
        assert report.tests_run == 10
        assert report.tests_passed == 8
        assert report.tests_failed == 2
        assert report.average_recovery_ms == 250.5
        assert report.weakest_component == "network"
        assert len(report.recommendations) == 1

    def test_resilience_report_default_timestamp(self):
        """Should default timestamp to now."""
        report = ResilienceReport(
            report_id="report",
            tests_run=0,
            tests_passed=0,
            tests_failed=0,
            average_recovery_ms=0,
            weakest_component=None,
            recommendations=[]
        )

        assert isinstance(report.generated_at, datetime)

    def test_resilience_report_to_dict(self):
        """Should convert to dictionary."""
        report = ResilienceReport(
            report_id="report_test",
            tests_run=5,
            tests_passed=4,
            tests_failed=1,
            average_recovery_ms=123.456,
            weakest_component="service",
            recommendations=[]
        )

        d = report.to_dict()

        assert d["report_id"] == "report_test"
        assert d["tests_run"] == 5
        assert d["passed"] == 4
        assert d["failed"] == 1
        assert d["pass_rate"] == 80.0
        assert d["avg_recovery_ms"] == 123.5
        assert d["weakest"] == "service"

    def test_resilience_report_zero_tests(self):
        """Should handle zero tests in pass_rate calculation."""
        report = ResilienceReport(
            report_id="empty",
            tests_run=0,
            tests_passed=0,
            tests_failed=0,
            average_recovery_ms=0,
            weakest_component=None,
            recommendations=[]
        )

        d = report.to_dict()

        assert d["pass_rate"] == 0


# =============================================================================
# ResilienceTester Initialization Tests
# =============================================================================


class TestResilienceTesterInit:
    """Tests for ResilienceTester initialization."""

    def test_basic_initialization(self):
        """Should initialize with defaults."""
        tester = ResilienceTester()

        assert tester.agent_id == 'resilience_tester_001'
        assert tester.safe_mode is True
        assert tester.df is None
        assert tester.blackboard is None
        assert len(tester.scenarios) >= 5  # Standard scenarios

    def test_custom_initialization(self):
        """Should accept custom parameters."""
        df = Mock()
        bb = Mock()
        tester = ResilienceTester(
            agent_id='custom_tester',
            df=df,
            blackboard=bb,
            safe_mode=False
        )

        assert tester.agent_id == 'custom_tester'
        assert tester.safe_mode is False
        assert tester.df is df
        assert tester.blackboard is bb

    def test_statistics_initialized(self):
        """Should initialize statistics to zero."""
        tester = ResilienceTester()

        assert tester.tasks_executed == 0
        assert tester.tasks_succeeded == 0
        assert tester.tasks_failed == 0
        assert tester.tests_run == 0
        assert tester.tests_passed == 0
        assert tester.tests_failed == 0

    def test_standard_scenarios_loaded(self):
        """Should load standard fault scenarios."""
        tester = ResilienceTester()

        assert "latency_high" in tester.scenarios
        assert "service_failure" in tester.scenarios
        assert "timeout_simulation" in tester.scenarios
        assert "memory_pressure" in tester.scenarios
        assert "cpu_spike" in tester.scenarios

    def test_registers_with_df(self):
        """Should register with Directory Facilitator."""
        df = Mock()
        df.register = Mock()

        tester = ResilienceTester(df=df)

        df.register.assert_called_once()


# =============================================================================
# ResilienceTester Scenario Management Tests
# =============================================================================


class TestScenarioManagement:
    """Tests for scenario management."""

    def test_add_scenario(self):
        """Should add scenario to catalog."""
        tester = ResilienceTester()
        initial_count = len(tester.scenarios)

        custom_scenario = FaultScenario(
            scenario_id="custom_test",
            name="Custom Test",
            fault_type=FaultType.DATA_CORRUPTION,
            duration_ms=2000,
            target_component="database"
        )
        tester.add_scenario(custom_scenario)

        assert len(tester.scenarios) == initial_count + 1
        assert "custom_test" in tester.scenarios
        assert tester.scenarios["custom_test"].name == "Custom Test"


# =============================================================================
# ResilienceTester Run Test Tests
# =============================================================================


class TestRunTest:
    """Tests for run_test method."""

    @pytest.fixture
    def tester(self):
        """Create tester in safe mode."""
        return ResilienceTester(safe_mode=True)

    def test_run_test_unknown_scenario(self, tester):
        """Should raise for unknown scenario."""
        with pytest.raises(ValueError, match="Unknown scenario"):
            tester.run_test("nonexistent_scenario")

    def test_run_test_latency(self, tester):
        """Should run latency test successfully."""
        # Override duration for faster test
        tester.scenarios["latency_high"].duration_ms = 10

        result = tester.run_test("latency_high")

        assert isinstance(result, TestResult)
        assert result.status in [TestStatus.PASSED, TestStatus.INCONCLUSIVE]
        assert len(result.observations) >= 1
        assert tester.tests_run == 1

    def test_run_test_failure(self, tester):
        """Should run failure test."""
        tester.scenarios["service_failure"].duration_ms = 10

        result = tester.run_test("service_failure")

        assert isinstance(result, TestResult)
        assert tester.tasks_executed == 1

    def test_run_test_increments_counters(self, tester):
        """Should increment statistics counters."""
        tester.scenarios["latency_high"].duration_ms = 10

        tester.run_test("latency_high")

        assert tester.tasks_executed == 1
        assert tester.tests_run == 1
        # Either passed or succeeded
        assert tester.tasks_succeeded >= 0

    def test_run_test_without_validation(self, tester):
        """Should skip recovery validation."""
        tester.scenarios["latency_high"].duration_ms = 10

        result = tester.run_test("latency_high", validate_recovery=False)

        assert result.status == TestStatus.INCONCLUSIVE
        assert "Recovery validation skipped" in result.observations

    def test_run_test_records_result(self, tester):
        """Should store result in results dict."""
        tester.scenarios["latency_high"].duration_ms = 10

        result = tester.run_test("latency_high")

        assert result.test_id in tester.results
        assert tester.results[result.test_id] is result

    def test_run_test_safe_mode_simulation(self, tester):
        """Should simulate fault in safe mode."""
        tester.scenarios["latency_high"].duration_ms = 10

        result = tester.run_test("latency_high")

        assert any("Safe mode" in obs for obs in result.observations)


# =============================================================================
# ResilienceTester Fault Injection Tests
# =============================================================================


class TestFaultInjection:
    """Tests for fault injection methods."""

    def test_simulate_fault_latency(self):
        """Should simulate latency fault."""
        tester = ResilienceTester(safe_mode=True)
        scenario = FaultScenario(
            scenario_id="lat",
            name="Latency",
            fault_type=FaultType.LATENCY,
            duration_ms=100,
            target_component="*",
            parameters={"delay_ms": 50}
        )

        start = time.time()
        tester._simulate_fault(scenario)
        elapsed = time.time() - start

        # Should have some delay
        assert elapsed >= 0.04  # 50ms with some tolerance

    def test_simulate_fault_cpu_spike(self):
        """Should simulate CPU spike."""
        tester = ResilienceTester(safe_mode=True)
        scenario = FaultScenario(
            scenario_id="cpu",
            name="CPU Spike",
            fault_type=FaultType.CPU_SPIKE,
            duration_ms=100,
            target_component="compute"
        )

        # Should not raise
        tester._simulate_fault(scenario)

    def test_simulate_fault_failure(self):
        """Should simulate failure type (logs only)."""
        tester = ResilienceTester(safe_mode=True)
        scenario = FaultScenario(
            scenario_id="fail",
            name="Failure",
            fault_type=FaultType.FAILURE,
            duration_ms=100,
            target_component="service"
        )

        # Should not raise
        tester._simulate_fault(scenario)

    def test_inject_fault_calls_hook(self):
        """Should call registered injection hook."""
        tester = ResilienceTester(safe_mode=False)
        hook = Mock()
        tester.injection_hooks["latency"] = hook

        scenario = FaultScenario(
            scenario_id="hook_test",
            name="Hook Test",
            fault_type=FaultType.LATENCY,
            duration_ms=100,
            target_component="*"
        )

        tester._inject_fault(scenario)

        hook.assert_called_once_with(scenario)


# =============================================================================
# ResilienceTester Recovery Validation Tests
# =============================================================================


class TestRecoveryValidation:
    """Tests for recovery validation."""

    def test_validate_recovery_no_active_injection(self):
        """Should return True when no active injection."""
        tester = ResilienceTester()
        scenario = FaultScenario(
            scenario_id="test",
            name="Test",
            fault_type=FaultType.FAILURE,
            duration_ms=100,
            target_component="*"
        )

        result = tester._validate_recovery(scenario)

        assert result is True

    def test_validate_recovery_with_active_injection(self):
        """Should return False when injection active."""
        tester = ResilienceTester()
        scenario = FaultScenario(
            scenario_id="test",
            name="Test",
            fault_type=FaultType.FAILURE,
            duration_ms=100,
            target_component="*"
        )
        tester.active_injections["test"] = True

        result = tester._validate_recovery(scenario)

        assert result is False


# =============================================================================
# ResilienceTester Run All Tests
# =============================================================================


class TestRunAllTests:
    """Tests for run_all_tests method."""

    def test_run_all_tests(self):
        """Should run all scenarios."""
        tester = ResilienceTester(safe_mode=True)
        # Reduce durations for faster testing
        for scenario in tester.scenarios.values():
            scenario.duration_ms = 10

        report = tester.run_all_tests()

        assert isinstance(report, ResilienceReport)
        assert report.tests_run == len(tester.scenarios)


# =============================================================================
# ResilienceTester Report Generation Tests
# =============================================================================


class TestGenerateReport:
    """Tests for generate_report method."""

    def test_generate_report_no_results(self):
        """Should handle no results."""
        tester = ResilienceTester()

        report = tester.generate_report([])

        assert report.tests_run == 0
        assert report.tests_passed == 0
        assert report.tests_failed == 0
        assert "No tests have been run yet" in report.recommendations

    def test_generate_report_all_passed(self):
        """Should report all passed."""
        tester = ResilienceTester()
        scenario = FaultScenario(
            scenario_id="test",
            name="Test",
            fault_type=FaultType.LATENCY,
            duration_ms=100,
            target_component="*"
        )
        results = [
            TestResult(
                test_id="t1",
                scenario=scenario,
                status=TestStatus.PASSED,
                recovery_time_ms=100,
                observations=[]
            ),
            TestResult(
                test_id="t2",
                scenario=scenario,
                status=TestStatus.PASSED,
                recovery_time_ms=200,
                observations=[]
            ),
        ]

        report = tester.generate_report(results)

        assert report.tests_run == 2
        assert report.tests_passed == 2
        assert report.tests_failed == 0
        assert report.average_recovery_ms == 150.0
        assert report.weakest_component is None

    def test_generate_report_with_failures(self):
        """Should identify weakest component."""
        tester = ResilienceTester()
        scenario_net = FaultScenario(
            scenario_id="net",
            name="Network Test",
            fault_type=FaultType.NETWORK_PARTITION,
            duration_ms=100,
            target_component="network"
        )
        scenario_svc = FaultScenario(
            scenario_id="svc",
            name="Service Test",
            fault_type=FaultType.FAILURE,
            duration_ms=100,
            target_component="service"
        )
        results = [
            TestResult(
                test_id="t1",
                scenario=scenario_net,
                status=TestStatus.FAILED,
                recovery_time_ms=-1,
                observations=[]
            ),
            TestResult(
                test_id="t2",
                scenario=scenario_net,
                status=TestStatus.FAILED,
                recovery_time_ms=-1,
                observations=[]
            ),
            TestResult(
                test_id="t3",
                scenario=scenario_svc,
                status=TestStatus.PASSED,
                recovery_time_ms=100,
                observations=[]
            ),
        ]

        report = tester.generate_report(results)

        assert report.tests_failed == 2
        assert report.weakest_component == "network"
        assert any("network" in rec for rec in report.recommendations)

    def test_generate_report_slow_recovery(self):
        """Should recommend faster failover for slow recovery."""
        tester = ResilienceTester()
        scenario = FaultScenario(
            scenario_id="test",
            name="Test",
            fault_type=FaultType.LATENCY,
            duration_ms=100,
            target_component="*"
        )
        results = [
            TestResult(
                test_id="t1",
                scenario=scenario,
                status=TestStatus.PASSED,
                recovery_time_ms=6000,  # > 5000ms
                observations=[]
            )
        ]

        report = tester.generate_report(results)

        assert any("5 seconds" in rec for rec in report.recommendations)


# =============================================================================
# ResilienceTester Abort Tests
# =============================================================================


class TestAbort:
    """Tests for abort functionality."""

    def test_abort_all_injections(self):
        """Should clear all active injections."""
        tester = ResilienceTester()
        tester.active_injections = {
            "test1": True,
            "test2": True,
            "test3": True
        }

        tester.abort_all_injections()

        for active in tester.active_injections.values():
            assert active is False


# =============================================================================
# ResilienceTester Process Tests
# =============================================================================


class TestProcess:
    """Tests for process method."""

    @pytest.fixture
    def tester(self):
        """Create tester with mock blackboard."""
        bb = Mock()
        bb.post = Mock()
        tester = ResilienceTester(blackboard=bb, safe_mode=True)
        # Reduce durations
        for s in tester.scenarios.values():
            s.duration_ms = 10
        return tester

    def test_process_status_operation(self, tester):
        """Should handle status operation."""
        task_entry = Mock()
        task_entry.metadata = {'operation': 'status'}

        result = tester.process(task_entry)

        assert 'safe_mode' in result.metadata
        assert 'scenarios' in result.metadata

    def test_process_run_test_operation(self, tester):
        """Should handle run_test operation."""
        task_entry = Mock()
        task_entry.metadata = {
            'operation': 'run_test',
            'scenario_id': 'latency_high'
        }

        result = tester.process(task_entry)

        assert result.metadata['status'] in ['passed', 'failed', 'inconclusive']

    def test_process_list_scenarios_operation(self, tester):
        """Should handle list_scenarios operation."""
        task_entry = Mock()
        task_entry.metadata = {'operation': 'list_scenarios'}

        result = tester.process(task_entry)

        assert 'scenarios' in result.metadata
        assert len(result.metadata['scenarios']) >= 5

    def test_process_abort_operation(self, tester):
        """Should handle abort operation."""
        tester.active_injections["test"] = True
        task_entry = Mock()
        task_entry.metadata = {'operation': 'abort'}

        result = tester.process(task_entry)

        assert result.metadata['aborted'] is True

    def test_process_report_operation(self, tester):
        """Should handle report operation."""
        task_entry = Mock()
        task_entry.metadata = {'operation': 'report'}

        result = tester.process(task_entry)

        assert 'tests_run' in result.metadata

    def test_process_unknown_operation(self, tester):
        """Should handle unknown operation."""
        task_entry = Mock()
        task_entry.metadata = {'operation': 'unknown_op'}

        result = tester.process(task_entry)

        assert 'error' in result.metadata

    def test_process_without_blackboard(self):
        """Should work without blackboard."""
        tester = ResilienceTester(blackboard=None, safe_mode=True)
        task_entry = Mock()
        task_entry.metadata = {'operation': 'status'}

        result = tester.process(task_entry)

        assert isinstance(result, dict)
        assert 'safe_mode' in result


# =============================================================================
# ResilienceTester BDI Interface Tests
# =============================================================================


class TestBDIInterface:
    """Tests for BDI interface methods."""

    def test_update_beliefs(self):
        """update_beliefs should not raise."""
        tester = ResilienceTester()
        tester.update_beliefs()  # Should not raise

    def test_deliberate(self):
        """deliberate should return list."""
        tester = ResilienceTester()
        result = tester.deliberate()

        assert isinstance(result, list)

    def test_execute_step(self):
        """execute_step should not raise."""
        tester = ResilienceTester()
        intention = Mock()

        tester.execute_step(intention)  # Should not raise


# =============================================================================
# ResilienceTester Statistics Tests
# =============================================================================


class TestStatistics:
    """Tests for statistics methods."""

    def test_get_statistics(self):
        """Should return statistics dict."""
        tester = ResilienceTester()

        stats = tester.get_statistics()

        assert isinstance(stats, dict)
        assert 'tasks_executed' in stats
        assert 'tasks_succeeded' in stats
        assert 'tasks_failed' in stats
        assert 'tests_run' in stats
        assert 'tests_passed' in stats
        assert 'tests_failed' in stats
        assert 'pass_rate' in stats
        assert 'safe_mode' in stats

    def test_statistics_after_test(self):
        """Should track statistics after running tests."""
        tester = ResilienceTester(safe_mode=True)
        tester.scenarios["latency_high"].duration_ms = 10

        tester.run_test("latency_high")

        stats = tester.get_statistics()
        assert stats['tasks_executed'] == 1
        assert stats['tests_run'] == 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestResilienceTesterIntegration:
    """Integration tests for ResilienceTester."""

    def test_full_workflow(self):
        """Test complete resilience testing workflow."""
        # Create tester
        tester = ResilienceTester(safe_mode=True)

        # Reduce durations
        for s in tester.scenarios.values():
            s.duration_ms = 10

        # Add custom scenario
        custom = FaultScenario(
            scenario_id="custom",
            name="Custom Test",
            fault_type=FaultType.LATENCY,
            duration_ms=10,
            target_component="custom"
        )
        tester.add_scenario(custom)

        # Run specific test
        result = tester.run_test("custom")
        assert result.status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.INCONCLUSIVE]

        # Generate report
        report = tester.generate_report()
        assert report.tests_run >= 1

        # Check statistics
        stats = tester.get_statistics()
        assert stats['tests_run'] >= 1


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
