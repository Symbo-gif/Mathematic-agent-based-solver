#!/usr/bin/env python3
"""
Comprehensive Stress Tests for Phase 1-4 Domains
=================================================

Hard stress testing for all 40 specialists across 9 mathematical domains.
Tests cover:
- Extreme numerical values
- Pathological edge cases
- Performance under load
- Numerical stability
- Correctness validation
"""

import pytest
import numpy as np
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from symbo_agentic_reasoners.core.blackboard import Blackboard
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
from symbo_agentic_reasoners.infrastructure.agent_communication import AgentCommunicationChannel
from symbo_agentic_reasoners.infrastructure.agent_management_system import AgentManagementSystem


# ============================================================================
# PHASE 1 - STOCHASTIC PROCESSES STRESS TESTS
# ============================================================================

class TestStochasticStress:
    """Stress tests for stochastic processes domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test infrastructure."""
        self.blackboard = Blackboard()
        self.df = DirectoryFacilitator()
        self.acc = AgentCommunicationChannel()
        self.ams = AgentManagementSystem()

    def test_brownian_motion_extreme_time(self):
        """Test Brownian motion with very large time values."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.brownian_motion import BrownianMotionSpecialist

        agent = BrownianMotionSpecialist(
            agent_id='bm_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # Test large time value (should still compute E[W(t)^2] = t)
        result = agent.compute_moments(t=1000.0, moment=2)
        assert abs(result['E[W^2]'] - 1000.0) < 1.0, "Large time moment computation failed"

    def test_sde_solver_stiff_system(self):
        """Test SDE solver with stiff equations."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.sde_solver import SDESolverSpecialist

        agent = SDESolverSpecialist(
            agent_id='sde_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # GBM with extreme volatility
        result = agent.solve_gbm(x0=1.0, mu=0.0, sigma=5.0, T=1.0, n_steps=1000)
        assert result['success'], "High volatility GBM failed"
        assert len(result['path']) == 1001, "Path length incorrect"

    def test_levy_process_high_frequency(self):
        """Test Levy process with high jump frequency."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.levy_processes import LevyProcessSpecialist

        agent = LevyProcessSpecialist(
            agent_id='levy_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # High rate compound Poisson
        result = agent.generate_compound_poisson(rate=100.0, T=1.0, n_samples=1000)
        assert result['success'], "High frequency Levy process failed"
        assert result['n_jumps'] > 50, "Expected many jumps"


# ============================================================================
# PHASE 2 - COMPUTABILITY THEORY STRESS TESTS
# ============================================================================

class TestComputabilityStress:
    """Stress tests for computability theory domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test infrastructure."""
        self.blackboard = Blackboard()
        self.df = DirectoryFacilitator()
        self.acc = AgentCommunicationChannel()
        self.ams = AgentManagementSystem()

    def test_ackermann_large_values(self):
        """Test Ackermann function with moderately large inputs."""
        from symbo_agentic_reasoners.agents.specialists.computability.recursion_theory import RecursionTheorySpecialist

        agent = RecursionTheorySpecialist(
            agent_id='rec_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # A(3,3) should compute without timeout
        result = agent.compute_ackermann(m=3, n=3)
        assert result['success'], "Ackermann A(3,3) failed"
        assert result['value'] == 61, f"Expected 61, got {result['value']}"

    def test_kolmogorov_complexity_various_strings(self):
        """Test Kolmogorov complexity estimation on diverse strings."""
        from symbo_agentic_reasoners.agents.specialists.computability.kolmogorov_complexity import KolmogorovComplexitySpecialist

        agent = KolmogorovComplexitySpecialist(
            agent_id='kolm_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        test_strings = [
            "0" * 1000,  # Highly compressible
            "".join(map(str, range(100))),  # Pattern
            "qwrtyuiopasdfghjklzxcvbnm" * 40,  # Random-ish
        ]

        for s in test_strings:
            result = agent.estimate_complexity(s)
            assert result['success'], f"Failed on string length {len(s)}"
            assert 0 < result['estimated_K'] <= len(s), "K estimate out of bounds"


# ============================================================================
# PHASE 2 - RIEMANNIAN GEOMETRY STRESS TESTS
# ============================================================================

class TestRiemannianStress:
    """Stress tests for Riemannian geometry domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test infrastructure."""
        self.blackboard = Blackboard()
        self.df = DirectoryFacilitator()
        self.acc = AgentCommunicationChannel()
        self.ams = AgentManagementSystem()

    def test_geodesic_long_path(self):
        """Test geodesic computation over long paths."""
        from symbo_agentic_reasoners.agents.specialists.riemannian.geodesic import GeodesicSpecialist

        agent = GeodesicSpecialist(
            agent_id='geod_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # Long time geodesic
        result = agent.compute_geodesic(
            metric_type='euclidean',
            start_point=[0.0, 0.0],
            end_point=[100.0, 100.0],
            n_points=1000
        )
        assert result['success'], "Long geodesic failed"
        assert len(result['path']) == 1000, "Path resolution incorrect"

    def test_curvature_high_dimension(self):
        """Test curvature computation in higher dimensions."""
        from symbo_agentic_reasoners.agents.specialists.riemannian.curvature import CurvatureSpecialist

        agent = CurvatureSpecialist(
            agent_id='curv_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # Euclidean 4D space should have zero curvature
        result = agent.compute_scalar_curvature(metric_type='euclidean', dimension=4)
        assert result['success'], "4D curvature failed"
        assert abs(result['scalar_curvature']) < 1e-10, "Flat space should have zero curvature"


# ============================================================================
# PHASE 3 - ALGEBRAIC TOPOLOGY STRESS TESTS
# ============================================================================

class TestAlgebraicTopologyStress:
    """Stress tests for algebraic topology domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test infrastructure."""
        self.blackboard = Blackboard()
        self.df = DirectoryFacilitator()
        self.acc = AgentCommunicationChannel()
        self.ams = AgentManagementSystem()

    def test_homology_complex_space(self):
        """Test homology computation for complex spaces."""
        from symbo_agentic_reasoners.agents.specialists.algebraic_topology.homology import HomologySpecialist

        agent = HomologySpecialist(
            agent_id='hom_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # Multiple handles
        result = agent.compute_homology(space_type='surface', genus=5)
        assert result['success'], "High genus surface failed"
        assert result['H1_rank'] == 10, f"Expected rank 10, got {result['H1_rank']}"

    def test_fundamental_group_presentations(self):
        """Test fundamental group with complex presentations."""
        from symbo_agentic_reasoners.agents.specialists.algebraic_topology.fundamental_group import FundamentalGroupSpecialist

        agent = FundamentalGroupSpecialist(
            agent_id='pi1_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # Complex space
        result = agent.compute_pi1(space_type='wedge_circles', n=10)
        assert result['success'], "Wedge of 10 circles failed"
        assert result['rank'] == 10, "Free group rank incorrect"


# ============================================================================
# PHASE 3 - ERGODIC THEORY STRESS TESTS
# ============================================================================

class TestErgodicStress:
    """Stress tests for ergodic theory domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test infrastructure."""
        self.blackboard = Blackboard()
        self.df = DirectoryFacilitator()
        self.acc = AgentCommunicationChannel()
        self.ams = AgentManagementSystem()

    def test_entropy_high_partitions(self):
        """Test entropy computation with fine partitions."""
        from symbo_agentic_reasoners.agents.specialists.ergodic.dynamical_entropy import DynamicalEntropySpecialist

        agent = DynamicalEntropySpecialist(
            agent_id='ent_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # Fine partition
        result = agent.compute_ks_entropy(
            transformation_type='doubling_map',
            n_partitions=32,
            n_iterates=50
        )
        assert result['success'], "Fine partition entropy failed"
        assert result['ks_entropy'] > 0, "Doubling map should have positive entropy"

    def test_mixing_long_time(self):
        """Test mixing convergence over long time."""
        from symbo_agentic_reasoners.agents.specialists.ergodic.mixing import MixingSpecialist

        agent = MixingSpecialist(
            agent_id='mix_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # Many iterations
        result = agent.check_strong_mixing(
            transformation_type='baker_map',
            n_iterations=200
        )
        assert result['success'], "Long-time mixing failed"


# ============================================================================
# PHASE 4 - ADVANCED OPTIMIZATION STRESS TESTS
# ============================================================================

class TestOptimizationAdvancedStress:
    """Stress tests for advanced optimization domain."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test infrastructure."""
        self.blackboard = Blackboard()
        self.df = DirectoryFacilitator()
        self.acc = AgentCommunicationChannel()
        self.ams = AgentManagementSystem()

    def test_global_optimization_rastrigin(self):
        """Test global optimization on Rastrigin function (highly multi-modal)."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.global_optimization import GlobalOptimizationSpecialist

        agent = GlobalOptimizationSpecialist(
            agent_id='glob_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # High-dimensional Rastrigin
        result = agent.simulated_annealing(
            function_type='rastrigin',
            dimension=10,
            max_iter=5000
        )
        assert result['success'], "High-dim Rastrigin failed"
        assert result['final_value'] < 50.0, "Failed to find reasonable minimum"

    def test_game_theory_large_payoff_matrix(self):
        """Test game theory with larger strategy spaces."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.game_theory import GameTheoryOptimizationSpecialist

        agent = GameTheoryOptimizationSpecialist(
            agent_id='game_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # 5x5 game
        payoff_A = np.random.randn(5, 5)
        payoff_B = -payoff_A  # Zero-sum
        result = agent.find_nash_equilibrium(payoff_A=payoff_A, payoff_B=payoff_B)
        assert result['success'], "5x5 game failed"

    def test_variational_calculus_stiff_functional(self):
        """Test variational calculus with stiff functionals."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.variational_calculus import VariationalCalculusSpecialist

        agent = VariationalCalculusSpecialist(
            agent_id='var_stress',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        # Brachistochrone with large height difference
        result = agent.solve_brachistochrone(x_a=0.0, y_a=0.0, x_b=10.0, y_b=-10.0)
        assert result['success'], "Large brachistochrone failed"
        assert result['time_of_descent'] > 0, "Time must be positive"


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

class TestPerformanceBenchmarks:
    """Performance benchmarks for all domains."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test infrastructure."""
        self.blackboard = Blackboard()
        self.df = DirectoryFacilitator()
        self.acc = AgentCommunicationChannel()
        self.ams = AgentManagementSystem()

    def test_response_time_stochastic(self):
        """Benchmark response time for stochastic specialists."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.brownian_motion import BrownianMotionSpecialist

        agent = BrownianMotionSpecialist(
            agent_id='bm_bench',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        start = time.time()
        result = agent.compute_moments(t=10.0, moment=2)
        elapsed = time.time() - start

        assert result['success'], "Benchmark computation failed"
        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s (expected < 1.0s)"

    def test_response_time_optimization(self):
        """Benchmark response time for optimization specialists."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.nonconvex import NonconvexOptimizationSpecialist

        agent = NonconvexOptimizationSpecialist(
            agent_id='nonconvex_bench',
            blackboard=self.blackboard,
            df=self.df,
            acc=self.acc,
            ams=self.ams
        )

        start = time.time()
        result = agent.trust_region_method(
            function_type='quartic',
            x0=[2.0, 2.0],
            max_iter=50
        )
        elapsed = time.time() - start

        assert result['success'], "Benchmark optimization failed"
        assert elapsed < 2.0, f"Too slow: {elapsed:.3f}s (expected < 2.0s)"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
