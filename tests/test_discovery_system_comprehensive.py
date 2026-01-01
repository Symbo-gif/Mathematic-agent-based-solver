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
Discovery System Comprehensive Tests
=====================================

Tests for Phase 6 system, Undecidability, and CuriosityEngine modules.
"""

import pytest


# =============================================================================
# Phase6System Tests
# =============================================================================


class TestSystemStatus:
    """Tests for SystemStatus enum."""

    def test_import(self):
        from symbo_agentic_reasoners.discovery.phase6_system import SystemStatus
        assert SystemStatus is not None

    def test_stopped(self):
        from symbo_agentic_reasoners.discovery.phase6_system import SystemStatus
        assert SystemStatus.STOPPED.value == 'stopped'

    def test_starting(self):
        from symbo_agentic_reasoners.discovery.phase6_system import SystemStatus
        assert SystemStatus.STARTING.value == 'starting'

    def test_running(self):
        from symbo_agentic_reasoners.discovery.phase6_system import SystemStatus
        assert SystemStatus.RUNNING.value == 'running'

    def test_paused(self):
        from symbo_agentic_reasoners.discovery.phase6_system import SystemStatus
        assert SystemStatus.PAUSED.value == 'paused'

    def test_error(self):
        from symbo_agentic_reasoners.discovery.phase6_system import SystemStatus
        assert SystemStatus.ERROR.value == 'error'


class TestDiscoveryCycleResult:
    """Tests for DiscoveryCycleResult dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.discovery.phase6_system import DiscoveryCycleResult
        result = DiscoveryCycleResult(
            cycle_id="cycle_001",
            theorems_generated=10,
            conjectures_filtered=5,
            proofs_attempted=3,
            proofs_succeeded=2,
            discoveries_integrated=1,
            time_elapsed_ms=500.0
        )
        assert result.cycle_id == "cycle_001"
        assert result.theorems_generated == 10
        assert result.proofs_succeeded == 2

    def test_to_dict(self):
        from symbo_agentic_reasoners.discovery.phase6_system import DiscoveryCycleResult
        result = DiscoveryCycleResult(
            cycle_id="cycle_002",
            theorems_generated=20,
            conjectures_filtered=10,
            proofs_attempted=8,
            proofs_succeeded=4,
            discoveries_integrated=2,
            time_elapsed_ms=1000.0
        )
        d = result.to_dict()
        assert d['cycle_id'] == "cycle_002"
        assert d['success_rate'] == 50.0  # 4/8 * 100

    def test_to_dict_zero_attempts(self):
        from symbo_agentic_reasoners.discovery.phase6_system import DiscoveryCycleResult
        result = DiscoveryCycleResult(
            cycle_id="cycle_003",
            theorems_generated=0,
            conjectures_filtered=0,
            proofs_attempted=0,
            proofs_succeeded=0,
            discoveries_integrated=0,
            time_elapsed_ms=100.0
        )
        d = result.to_dict()
        assert d['success_rate'] == 0.0  # Division by max(1, 0) = 1


class TestPhase6System:
    """Tests for Phase6System class."""

    @pytest.fixture
    def system(self):
        from symbo_agentic_reasoners.discovery.phase6_system import Phase6System
        return Phase6System()

    def test_initialization(self, system):
        assert system is not None
        assert system.status == 'stopped'

    def test_start(self, system):
        system.start()
        assert system.status == 'running'

    def test_shutdown(self, system):
        system.start()
        system.shutdown()
        assert system.status == 'stopped'

    def test_health_check(self, system):
        system.start()
        health = system.health_check()
        assert isinstance(health, dict)
        assert 'overall' in health
        assert 'conjecture_generation' in health
        assert 'deep_search' in health

    def test_get_statistics(self, system):
        stats = system.get_statistics()
        assert isinstance(stats, dict)
        assert 'system' in stats

    def test_has_synthetic_data_generator(self, system):
        assert system.synthetic_data_generator is not None

    def test_has_pattern_recognizer(self, system):
        assert system.pattern_recognizer is not None

    def test_has_policy_network(self, system):
        assert system.policy_network is not None

    def test_has_critic_network(self, system):
        assert system.critic_network is not None

    def test_has_prover_engine(self, system):
        assert system.prover_engine is not None


# =============================================================================
# Undecidability Module Tests
# =============================================================================


class TestDecidabilityClass:
    """Tests for DecidabilityClass enum."""

    def test_import(self):
        from symbo_agentic_reasoners.discovery.undecidability import DecidabilityClass
        assert DecidabilityClass is not None

    def test_decidable(self):
        from symbo_agentic_reasoners.discovery.undecidability import DecidabilityClass
        assert DecidabilityClass.DECIDABLE.value == 'decidable'

    def test_undecidable(self):
        from symbo_agentic_reasoners.discovery.undecidability import DecidabilityClass
        assert DecidabilityClass.UNDECIDABLE.value == 'undecidable'

    def test_unknown(self):
        from symbo_agentic_reasoners.discovery.undecidability import DecidabilityClass
        assert DecidabilityClass.UNKNOWN.value == 'unknown'


class TestDecidabilityChecker:
    """Tests for DecidabilityChecker class."""

    @pytest.fixture
    def checker(self):
        from symbo_agentic_reasoners.discovery.undecidability import DecidabilityChecker
        return DecidabilityChecker()

    def test_initialization(self, checker):
        assert checker is not None

    def test_assess(self, checker):
        result = checker.assess("test candidate")
        assert result is not None
        assert hasattr(result, 'decidability_class')

    def test_health_check(self, checker):
        assert checker.health_check() is True

    def test_reset(self, checker):
        # Should not raise
        checker.reset()


class TestInteractiveGuidanceLiaison:
    """Tests for InteractiveGuidanceLiaison class."""

    @pytest.fixture
    def liaison(self):
        from symbo_agentic_reasoners.discovery.undecidability import InteractiveGuidanceLiaison
        return InteractiveGuidanceLiaison()

    def test_initialization(self, liaison):
        assert liaison is not None

    def test_initialization_with_callback(self):
        from symbo_agentic_reasoners.discovery.undecidability import InteractiveGuidanceLiaison
        callback = lambda x: print(x)
        liaison = InteractiveGuidanceLiaison(notification_callback=callback)
        assert liaison is not None

    def test_request_guidance(self, liaison):
        request = liaison.request_guidance("problem", "state")
        assert request is not None
        assert hasattr(request, 'summary')

    def test_receive_guidance(self, liaison):
        result = liaison.receive_guidance("request_id", "guidance")
        assert result is True

    def test_get_pending_requests(self, liaison):
        pending = liaison.get_pending_requests()
        assert isinstance(pending, list)

    def test_health_check(self, liaison):
        assert liaison.health_check() is True

    def test_reset(self, liaison):
        liaison.reset()  # Should not raise

    def test_get_statistics(self, liaison):
        stats = liaison.get_statistics()
        assert isinstance(stats, dict)


class TestProofStateSummary:
    """Tests for ProofStateSummary dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.discovery.undecidability import ProofStateSummary
        summary = ProofStateSummary()
        assert summary.problem_id == ""
        assert summary.current_state == ""

    def test_creation_with_values(self):
        from symbo_agentic_reasoners.discovery.undecidability import ProofStateSummary
        summary = ProofStateSummary(problem_id="prob_001", current_state="initial")
        assert summary.problem_id == "prob_001"
        assert summary.current_state == "initial"


# =============================================================================
# CuriosityEngine Tests
# =============================================================================


class TestExplorationCategory:
    """Tests for ExplorationCategory enum."""

    def test_import(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import ExplorationCategory
        assert ExplorationCategory is not None


class TestInterestLevel:
    """Tests for InterestLevel enum."""

    def test_import(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import InterestLevel
        assert InterestLevel is not None


class TestCuriosityEngine:
    """Tests for CuriosityEngine class."""

    def test_import(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import CuriosityEngine
        assert CuriosityEngine is not None

    def test_requires_solver(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import CuriosityEngine
        # CuriosityEngine requires a solver argument
        with pytest.raises(TypeError):
            CuriosityEngine()

    def test_initialization_with_mock_solver(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import CuriosityEngine

        # Create minimal mock solver
        class MockSolver:
            def solve(self, problem):
                return {"success": True, "solution": "x = 1"}

        engine = CuriosityEngine(solver=MockSolver())
        assert engine is not None

    def test_has_get_statistics_with_mock(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import CuriosityEngine

        class MockSolver:
            def solve(self, problem):
                return {"success": True, "solution": "x = 1"}

        engine = CuriosityEngine(solver=MockSolver())
        assert hasattr(engine, 'get_statistics')
        stats = engine.get_statistics()
        assert isinstance(stats, dict)


class TestProblemGenerator:
    """Tests for ProblemGenerator class."""

    def test_import(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import ProblemGenerator
        assert ProblemGenerator is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import ProblemGenerator
        gen = ProblemGenerator()
        assert gen is not None


class TestInterestScorer:
    """Tests for InterestScorer class."""

    def test_import(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import InterestScorer
        assert InterestScorer is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.discovery.curiosity_engine import InterestScorer
        scorer = InterestScorer()
        assert scorer is not None


# =============================================================================
# ImaginationEngine Tests
# =============================================================================


class TestSystemState:
    """Tests for SystemState enum in imagination_engine."""

    def test_import(self):
        from symbo_agentic_reasoners.discovery.imagination_engine import SystemState
        assert SystemState is not None

    def test_idle(self):
        from symbo_agentic_reasoners.discovery.imagination_engine import SystemState
        assert SystemState.IDLE.value == 'idle'

    def test_busy(self):
        from symbo_agentic_reasoners.discovery.imagination_engine import SystemState
        assert SystemState.BUSY.value == 'busy'

    def test_exploring(self):
        from symbo_agentic_reasoners.discovery.imagination_engine import SystemState
        assert SystemState.EXPLORING.value == 'exploring'

    def test_paused(self):
        from symbo_agentic_reasoners.discovery.imagination_engine import SystemState
        assert SystemState.PAUSED.value == 'paused'

    def test_stopped(self):
        from symbo_agentic_reasoners.discovery.imagination_engine import SystemState
        assert SystemState.STOPPED.value == 'stopped'


class TestExplorationPriority:
    """Tests for ExplorationPriority dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.discovery.imagination_engine import ExplorationPriority
        from symbo_agentic_reasoners.discovery.curiosity_engine import ExplorationCategory
        priority = ExplorationPriority(category=ExplorationCategory.ALGEBRA)
        assert priority.category == ExplorationCategory.ALGEBRA
        assert priority.weight == 1.0

    def test_with_custom_values(self):
        from symbo_agentic_reasoners.discovery.imagination_engine import ExplorationPriority
        from symbo_agentic_reasoners.discovery.curiosity_engine import ExplorationCategory
        priority = ExplorationPriority(
            category=ExplorationCategory.NUMBER_THEORY,
            weight=2.0,
            min_interval_seconds=30.0,
            success_rate=0.8
        )
        assert priority.weight == 2.0
        assert priority.min_interval_seconds == 30.0
        assert priority.success_rate == 0.8


class TestImaginationStats:
    """Tests for ImaginationStats dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.discovery.imagination_engine import ImaginationStats
        stats = ImaginationStats()
        assert stats.total_explorations == 0
        assert stats.successful_explorations == 0
        assert stats.interesting_discoveries == 0


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
