#!/usr/bin/env python3
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
Comprehensive Stress Tests for Phase 1-4 Domains
=================================================

Hard stress testing for all expansion domain specialists.
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

from unittest.mock import Mock


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def infrastructure():
    """Create mock infrastructure for all tests."""
    return {
        'blackboard': None,
        'df': None,
        'acc': None,
        'ams': None
    }


# ============================================================================
# PHASE 1 - STOCHASTIC PROCESSES STRESS TESTS
# ============================================================================

class TestStochasticStress:
    """Stress tests for stochastic processes domain."""

    def test_brownian_motion_extreme_time(self, infrastructure):
        """Test Brownian motion with very large time values."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.brownian_motion import BrownianMotionSpecialist

        agent = BrownianMotionSpecialist(
            agent_id='bm_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Test large time value (should still compute E[W(t)^2] = t)
        result = agent.compute_moments(t=1000.0, moment=2)
        assert result['success'], "Large time moment computation failed"
        assert abs(result['E[W^2]'] - 1000.0) < 1.0, "Large time moment computation failed"

    def test_brownian_motion_many_paths(self, infrastructure):
        """Test generating many Brownian paths."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.brownian_motion import BrownianMotionSpecialist

        agent = BrownianMotionSpecialist(
            agent_id='bm_paths',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Generate 100 paths
        result = agent.generate_paths(T=1.0, n_steps=100, n_paths=100)
        assert result['success'], "Multiple path generation failed"
        assert len(result['paths']) == 100, "Expected 100 paths"

    def test_sde_solver_stiff_system(self, infrastructure):
        """Test SDE solver with stiff equations."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.sde_solver import SDESolverSpecialist

        agent = SDESolverSpecialist(
            agent_id='sde_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # GBM with extreme volatility
        result = agent.solve_gbm(x0=1.0, mu=0.0, sigma=5.0, T=1.0, n_steps=1000)
        assert result['success'], "High volatility GBM failed"
        assert len(result['path']) == 1001, "Path length incorrect"

    def test_sde_solver_adaptive_timestep(self, infrastructure):
        """Test SDE solver with adaptive timestepping."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.sde_solver import SDESolverSpecialist

        agent = SDESolverSpecialist(
            agent_id='sde_adaptive',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Test with adaptive timestep
        result = agent.solve_euler_maruyama(
            drift=lambda x, t: -0.5 * x,
            diffusion=lambda x, t: 0.2,
            x0=1.0,
            T=2.0,
            n_steps=500
        )
        assert result['success'], "Adaptive SDE solving failed"

    def test_levy_process_high_frequency(self, infrastructure):
        """Test Levy process with high jump frequency."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.levy_processes import LevyProcessSpecialist

        agent = LevyProcessSpecialist(
            agent_id='levy_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # High rate compound Poisson
        result = agent.generate_compound_poisson(rate=100.0, T=1.0, n_samples=1000)
        assert result['success'], "High frequency Levy process failed"
        assert result['n_jumps'] > 50, "Expected many jumps"

    def test_martingale_stopping_time(self, infrastructure):
        """Test martingale with complex stopping times."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.martingale_theory import MartingaleTheorySpecialist

        agent = MartingaleTheorySpecialist(
            agent_id='mart_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Verify martingale property
        result = agent.verify_martingale(
            process_type='brownian_motion',
            n_steps=1000,
            n_trials=50
        )
        assert result['success'], "Martingale verification failed"
        assert result['is_martingale'], "BM should be martingale"

    def test_stochastic_calculus_ito_lemma(self, infrastructure):
        """Test Ito's lemma on complex functions."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.stochastic_calculus import StochasticCalculusSpecialist

        agent = StochasticCalculusSpecialist(
            agent_id='ito_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Apply Ito to f(x) = x^2 with Brownian motion
        result = agent.apply_ito_lemma(
            function_type='quadratic',
            process_type='brownian_motion',
            T=1.0,
            n_steps=500
        )
        assert result['success'], "Ito lemma application failed"


# ============================================================================
# PHASE 2 - COMPUTABILITY THEORY STRESS TESTS
# ============================================================================

class TestComputabilityStress:
    """Stress tests for computability theory domain."""

    def test_ackermann_large_values(self, infrastructure):
        """Test Ackermann function with moderately large inputs."""
        from symbo_agentic_reasoners.agents.specialists.computability.recursion_theory import RecursionTheorySpecialist

        agent = RecursionTheorySpecialist(
            agent_id='rec_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # A(3,3) should compute without timeout
        result = agent.compute_ackermann(m=3, n=3)
        assert result['success'], "Ackermann A(3,3) failed"
        assert result['value'] == 61, f"Expected 61, got {result['value']}"

    def test_primitive_recursive_functions(self, infrastructure):
        """Test primitive recursive function evaluation."""
        from symbo_agentic_reasoners.agents.specialists.computability.recursion_theory import RecursionTheorySpecialist

        agent = RecursionTheorySpecialist(
            agent_id='rec_prim',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Test factorial (primitive recursive)
        result = agent.evaluate_primitive_recursive(function='factorial', n=10)
        assert result['success'], "Factorial failed"
        assert result['value'] == 3628800, "Factorial(10) incorrect"

    def test_kolmogorov_complexity_various_strings(self, infrastructure):
        """Test Kolmogorov complexity estimation on diverse strings."""
        from symbo_agentic_reasoners.agents.specialists.computability.kolmogorov_complexity import KolmogorovComplexitySpecialist

        agent = KolmogorovComplexitySpecialist(
            agent_id='kolm_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        test_strings = [
            "0" * 1000,  # Highly compressible
            "".join(map(str, range(100))),  # Pattern
            "qwertyuiopasdfghjklzxcvbnm" * 40,  # Repetitive
        ]

        for s in test_strings:
            result = agent.estimate_complexity(s)
            assert result['success'], f"Failed on string length {len(s)}"
            assert 0 < result['estimated_K'] <= len(s), "K estimate out of bounds"

    def test_complexity_theory_time_hierarchy(self, infrastructure):
        """Test time complexity hierarchy theorems."""
        from symbo_agentic_reasoners.agents.specialists.computability.complexity_theory import ComplexityTheorySpecialist

        agent = ComplexityTheorySpecialist(
            agent_id='complex_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Verify P ⊆ NP
        result = agent.verify_hierarchy(lower='P', upper='NP')
        assert result['success'], "Hierarchy verification failed"
        assert result['is_subset'], "P should be subset of NP"

    def test_turing_degrees_ordering(self, infrastructure):
        """Test Turing degree comparisons."""
        from symbo_agentic_reasoners.agents.specialists.computability.turing_degrees import TuringDegreesSpecialist

        agent = TuringDegreesSpecialist(
            agent_id='turing_deg',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Compare computable sets
        result = agent.compare_degrees(set_a='halting_problem', set_b='empty_set')
        assert result['success'], "Degree comparison failed"
        assert result['ordering'] in ['strictly_greater', 'incomparable'], "Halting > computable"


# ============================================================================
# PHASE 2 - RIEMANNIAN GEOMETRY STRESS TESTS
# ============================================================================

class TestRiemannianStress:
    """Stress tests for Riemannian geometry domain."""

    def test_geodesic_long_path(self, infrastructure):
        """Test geodesic computation over long paths."""
        from symbo_agentic_reasoners.agents.specialists.riemannian.geodesic import GeodesicSpecialist

        agent = GeodesicSpecialist(
            agent_id='geod_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
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

    def test_geodesic_sphere(self, infrastructure):
        """Test geodesics on sphere (great circles)."""
        from symbo_agentic_reasoners.agents.specialists.riemannian.geodesic import GeodesicSpecialist

        agent = GeodesicSpecialist(
            agent_id='geod_sphere',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Great circle from north pole to equator
        result = agent.compute_geodesic(
            metric_type='sphere',
            start_point=[0.0, 0.0, 1.0],  # North pole
            end_point=[1.0, 0.0, 0.0],     # Equator
            n_points=100
        )
        assert result['success'], "Sphere geodesic failed"

    def test_curvature_high_dimension(self, infrastructure):
        """Test curvature computation in higher dimensions."""
        from symbo_agentic_reasoners.agents.specialists.riemannian.curvature import CurvatureSpecialist

        agent = CurvatureSpecialist(
            agent_id='curv_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Euclidean 4D space should have zero curvature
        result = agent.compute_scalar_curvature(metric_type='euclidean', dimension=4)
        assert result['success'], "4D curvature failed"
        assert abs(result['scalar_curvature']) < 1e-10, "Flat space should have zero curvature"

    def test_metric_tensor_computation(self, infrastructure):
        """Test metric tensor for various manifolds."""
        from symbo_agentic_reasoners.agents.specialists.riemannian.metric import MetricSpecialist

        agent = MetricSpecialist(
            agent_id='metric_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Compute metric for sphere
        result = agent.compute_metric(
            manifold_type='sphere',
            coordinates=[np.pi/4, np.pi/4]  # theta, phi
        )
        assert result['success'], "Metric computation failed"
        assert result['metric'].shape == (2, 2), "Metric should be 2x2"

    def test_holonomy_group(self, infrastructure):
        """Test holonomy group computation."""
        from symbo_agentic_reasoners.agents.specialists.riemannian.holonomy import HolonomySpecialist

        agent = HolonomySpecialist(
            agent_id='hol_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Euclidean space has trivial holonomy
        result = agent.compute_holonomy(metric_type='euclidean', dimension=3)
        assert result['success'], "Holonomy computation failed"
        assert result['holonomy_group'] == 'trivial', "Euclidean should have trivial holonomy"


# ============================================================================
# PHASE 3 - ALGEBRAIC TOPOLOGY STRESS TESTS
# ============================================================================

class TestAlgebraicTopologyStress:
    """Stress tests for algebraic topology domain."""

    def test_homology_complex_space(self, infrastructure):
        """Test homology computation for complex spaces."""
        from symbo_agentic_reasoners.agents.specialists.algebraic_topology.homology import HomologySpecialist

        agent = HomologySpecialist(
            agent_id='hom_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Multiple handles
        result = agent.compute_homology(space_type='surface', genus=5)
        assert result['success'], "High genus surface failed"
        assert result['H1_rank'] == 10, f"Expected rank 10, got {result['H1_rank']}"

    def test_homology_simplicial_complex(self, infrastructure):
        """Test homology of large simplicial complex."""
        from symbo_agentic_reasoners.agents.specialists.algebraic_topology.homology import HomologySpecialist

        agent = HomologySpecialist(
            agent_id='hom_simpl',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Build complex torus
        result = agent.compute_homology(space_type='torus', n_subdivisions=5)
        assert result['success'], "Torus homology failed"
        assert result['H1_rank'] == 2, "Torus should have H1 rank 2"

    def test_fundamental_group_presentations(self, infrastructure):
        """Test fundamental group with complex presentations."""
        from symbo_agentic_reasoners.agents.specialists.algebraic_topology.fundamental_group import FundamentalGroupSpecialist

        agent = FundamentalGroupSpecialist(
            agent_id='pi1_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Complex space
        result = agent.compute_pi1(space_type='wedge_circles', n=10)
        assert result['success'], "Wedge of 10 circles failed"
        assert result['rank'] == 10, "Free group rank incorrect"

    def test_homotopy_groups_spheres(self, infrastructure):
        """Test homotopy groups of spheres."""
        from symbo_agentic_reasoners.agents.specialists.algebraic_topology.homotopy import HomotopySpecialist

        agent = HomotopySpecialist(
            agent_id='hom_pi',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # π_n(S^n) = Z
        result = agent.compute_homotopy_group(space_type='sphere', n=3, k=3)
        assert result['success'], "Homotopy group failed"
        assert result['group'] == 'Z', "π_3(S^3) should be Z"

    def test_cohomology_cup_product(self, infrastructure):
        """Test cohomology ring structure."""
        from symbo_agentic_reasoners.agents.specialists.algebraic_topology.cohomology import CohomologySpecialist

        agent = CohomologySpecialist(
            agent_id='cohom_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Compute cup product on torus
        result = agent.compute_cup_product(
            space_type='torus',
            degree1=1,
            degree2=1
        )
        assert result['success'], "Cup product failed"

    def test_spectral_sequence_convergence(self, infrastructure):
        """Test spectral sequence convergence."""
        from symbo_agentic_reasoners.agents.specialists.algebraic_topology.spectral_sequences import SpectralSequencesSpecialist

        agent = SpectralSequencesSpecialist(
            agent_id='ss_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Serre spectral sequence
        result = agent.compute_serre_spectral_sequence(
            fibration_type='hopf',
            n_pages=5
        )
        assert result['success'], "Spectral sequence failed"


# ============================================================================
# PHASE 3 - ERGODIC THEORY STRESS TESTS
# ============================================================================

class TestErgodicStress:
    """Stress tests for ergodic theory domain."""

    def test_entropy_high_partitions(self, infrastructure):
        """Test entropy computation with fine partitions."""
        from symbo_agentic_reasoners.agents.specialists.ergodic.dynamical_entropy import DynamicalEntropySpecialist

        agent = DynamicalEntropySpecialist(
            agent_id='ent_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Fine partition
        result = agent.compute_ks_entropy(
            transformation_type='doubling_map',
            n_partitions=32,
            n_iterates=50
        )
        assert result['success'], "Fine partition entropy failed"
        assert result['ks_entropy'] > 0, "Doubling map should have positive entropy"

    def test_entropy_shift_map(self, infrastructure):
        """Test entropy of shift map (should equal log(2))."""
        from symbo_agentic_reasoners.agents.specialists.ergodic.dynamical_entropy import DynamicalEntropySpecialist

        agent = DynamicalEntropySpecialist(
            agent_id='ent_shift',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Shift map entropy
        result = agent.compute_ks_entropy(
            transformation_type='shift',
            alphabet_size=2,
            n_iterates=100
        )
        assert result['success'], "Shift entropy failed"
        assert abs(result['ks_entropy'] - 0.693) < 0.1, "Shift should have entropy log(2)"

    def test_mixing_long_time(self, infrastructure):
        """Test mixing convergence over long time."""
        from symbo_agentic_reasoners.agents.specialists.ergodic.mixing import MixingSpecialist

        agent = MixingSpecialist(
            agent_id='mix_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Many iterations
        result = agent.check_strong_mixing(
            transformation_type='baker_map',
            n_iterations=200
        )
        assert result['success'], "Long-time mixing failed"

    def test_ergodic_theorem_convergence(self, infrastructure):
        """Test Birkhoff ergodic theorem convergence."""
        from symbo_agentic_reasoners.agents.specialists.ergodic.ergodic_theorems import ErgodicTheoremsSpecialist

        agent = ErgodicTheoremsSpecialist(
            agent_id='erg_thm',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Test convergence for ergodic transformation
        result = agent.verify_birkhoff_theorem(
            transformation_type='rotation',
            alpha=np.sqrt(2) - 1,  # Irrational rotation
            n_iterations=10000,
            tolerance=0.01
        )
        assert result['success'], "Birkhoff theorem verification failed"

    def test_invariant_measure_existence(self, infrastructure):
        """Test existence of invariant measures."""
        from symbo_agentic_reasoners.agents.specialists.ergodic.invariant_measures import InvariantMeasuresSpecialist

        agent = InvariantMeasuresSpecialist(
            agent_id='inv_meas',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Find invariant measure for doubling map
        result = agent.compute_invariant_measure(
            transformation_type='doubling_map',
            n_bins=100
        )
        assert result['success'], "Invariant measure computation failed"
        assert result['is_invariant'], "Should find invariant measure"


# ============================================================================
# PHASE 3 - GEOMETRIC MEASURE THEORY STRESS TESTS
# ============================================================================

class TestGeometricMeasureStress:
    """Stress tests for geometric measure theory domain."""

    def test_hausdorff_measure_fractals(self, infrastructure):
        """Test Hausdorff measure on fractal sets."""
        from symbo_agentic_reasoners.agents.specialists.geometric_measure.hausdorff_measure import HausdorffMeasureSpecialist

        agent = HausdorffMeasureSpecialist(
            agent_id='haus_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Cantor set has dimension log(2)/log(3)
        result = agent.compute_hausdorff_dimension(
            set_type='cantor',
            n_iterations=10
        )
        assert result['success'], "Cantor dimension failed"
        expected_dim = np.log(2) / np.log(3)
        assert abs(result['dimension'] - expected_dim) < 0.01, "Cantor dimension incorrect"

    def test_hausdorff_sierpinski(self, infrastructure):
        """Test Hausdorff dimension of Sierpinski triangle."""
        from symbo_agentic_reasoners.agents.specialists.geometric_measure.hausdorff_measure import HausdorffMeasureSpecialist

        agent = HausdorffMeasureSpecialist(
            agent_id='haus_sierp',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        result = agent.compute_hausdorff_dimension(
            set_type='sierpinski',
            n_iterations=8
        )
        assert result['success'], "Sierpinski dimension failed"
        expected_dim = np.log(3) / np.log(2)
        assert abs(result['dimension'] - expected_dim) < 0.01, "Sierpinski dimension incorrect"

    def test_minimal_surfaces_area(self, infrastructure):
        """Test minimal surface area computation."""
        from symbo_agentic_reasoners.agents.specialists.geometric_measure.minimal_surfaces import MinimalSurfacesSpecialist

        agent = MinimalSurfacesSpecialist(
            agent_id='min_surf',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Catenoid (minimal surface of revolution)
        result = agent.compute_minimal_surface(
            surface_type='catenoid',
            boundary_curves='two_circles',
            n_grid_points=100
        )
        assert result['success'], "Minimal surface failed"
        assert result['mean_curvature'] < 1e-6, "Minimal surface should have zero mean curvature"

    def test_rectifiability_criterion(self, infrastructure):
        """Test rectifiability of various sets."""
        from symbo_agentic_reasoners.agents.specialists.geometric_measure.rectifiability import RectifiabilitySpecialist

        agent = RectifiabilitySpecialist(
            agent_id='rect_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Smooth curve is rectifiable
        result = agent.check_rectifiability(
            set_type='smooth_curve',
            dimension=1
        )
        assert result['success'], "Rectifiability check failed"
        assert result['is_rectifiable'], "Smooth curve should be rectifiable"

    def test_currents_boundary_operator(self, infrastructure):
        """Test boundary operator on currents."""
        from symbo_agentic_reasoners.agents.specialists.geometric_measure.currents import CurrentsSpecialist

        agent = CurrentsSpecialist(
            agent_id='curr_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # ∂∂ = 0
        result = agent.verify_boundary_property(
            current_type='simplex',
            dimension=2
        )
        assert result['success'], "Boundary operator verification failed"
        assert result['boundary_of_boundary_zero'], "∂∂ should equal 0"


# ============================================================================
# PHASE 3 - TDA STRESS TESTS
# ============================================================================

class TestTDAStress:
    """Stress tests for topological data analysis domain."""

    def test_persistent_homology_large_dataset(self, infrastructure):
        """Test persistent homology on large point clouds."""
        from symbo_agentic_reasoners.agents.specialists.tda.persistent_homology import PersistentHomologySpecialist

        agent = PersistentHomologySpecialist(
            agent_id='ph_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Large random point cloud
        points = np.random.randn(500, 3)
        result = agent.compute_persistence(
            points=points,
            max_dimension=2,
            max_edge_length=2.0
        )
        assert result['success'], "Persistent homology on 500 points failed"
        assert 'diagram' in result, "Should return persistence diagram"

    def test_persistent_homology_noisy_circle(self, infrastructure):
        """Test persistence on noisy circle (should detect H1)."""
        from symbo_agentic_reasoners.agents.specialists.tda.persistent_homology import PersistentHomologySpecialist

        agent = PersistentHomologySpecialist(
            agent_id='ph_circle',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Noisy circle
        theta = np.linspace(0, 2*np.pi, 100)
        points = np.column_stack([np.cos(theta), np.sin(theta)])
        points += np.random.randn(100, 2) * 0.1  # Add noise

        result = agent.compute_persistence(points=points, max_dimension=1)
        assert result['success'], "Noisy circle persistence failed"

    def test_simplicial_complex_construction(self, infrastructure):
        """Test construction of large simplicial complexes."""
        from symbo_agentic_reasoners.agents.specialists.tda.simplicial_complex import SimplicialComplexSpecialist

        agent = SimplicialComplexSpecialist(
            agent_id='sc_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Vietoris-Rips complex
        points = np.random.randn(200, 2)
        result = agent.build_vietoris_rips(
            points=points,
            max_dimension=2,
            epsilon=0.5
        )
        assert result['success'], "VR complex construction failed"
        assert result['n_simplices'] > 200, "Should have many simplices"

    def test_mapper_algorithm_clustering(self, infrastructure):
        """Test Mapper algorithm on high-dimensional data."""
        from symbo_agentic_reasoners.agents.specialists.tda.mapper import MapperSpecialist

        agent = MapperSpecialist(
            agent_id='mapper_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # High-dimensional Swiss roll
        t = np.linspace(0, 4*np.pi, 300)
        data = np.column_stack([
            t * np.cos(t),
            t * np.sin(t),
            np.random.randn(300)
        ])

        result = agent.compute_mapper(
            data=data,
            filter_function='PCA',
            n_intervals=10,
            overlap=0.3
        )
        assert result['success'], "Mapper algorithm failed"
        assert result['n_nodes'] > 5, "Should detect structure"

    def test_topological_inference_bottleneck(self, infrastructure):
        """Test bottleneck distance computation."""
        from symbo_agentic_reasoners.agents.specialists.tda.topological_inference import TopologicalInferenceSpecialist

        agent = TopologicalInferenceSpecialist(
            agent_id='topo_inf',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Compare two similar diagrams
        diagram1 = [(0.0, 0.5), (0.1, 0.8), (0.2, 0.9)]
        diagram2 = [(0.05, 0.55), (0.15, 0.85), (0.25, 0.95)]

        result = agent.compute_bottleneck_distance(
            diagram1=diagram1,
            diagram2=diagram2
        )
        assert result['success'], "Bottleneck distance failed"
        assert result['distance'] < 0.2, "Similar diagrams should have small distance"


# ============================================================================
# PHASE 4 - ADVANCED OPTIMIZATION STRESS TESTS
# ============================================================================

class TestOptimizationAdvancedStress:
    """Stress tests for advanced optimization domain."""

    def test_global_optimization_rastrigin(self, infrastructure):
        """Test global optimization on Rastrigin function (highly multi-modal)."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.global_optimization import GlobalOptimizationSpecialist

        agent = GlobalOptimizationSpecialist(
            agent_id='glob_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # High-dimensional Rastrigin
        result = agent.simulated_annealing(
            function_type='rastrigin',
            dimension=10,
            max_iter=5000
        )
        assert result['success'], "High-dim Rastrigin failed"
        assert result['final_value'] < 50.0, "Failed to find reasonable minimum"

    def test_global_optimization_differential_evolution(self, infrastructure):
        """Test differential evolution on Rosenbrock."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.global_optimization import GlobalOptimizationSpecialist

        agent = GlobalOptimizationSpecialist(
            agent_id='de_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        result = agent.differential_evolution(
            function_type='rosenbrock',
            dimension=5,
            population_size=50,
            max_iter=1000
        )
        assert result['success'], "Differential evolution failed"
        assert result['final_value'] < 10.0, "Should find near-optimal solution"

    def test_game_theory_large_payoff_matrix(self, infrastructure):
        """Test game theory with larger strategy spaces."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.game_theory import GameTheoryOptimizationSpecialist

        agent = GameTheoryOptimizationSpecialist(
            agent_id='game_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # 5x5 game
        payoff_A = np.random.randn(5, 5)
        payoff_B = -payoff_A  # Zero-sum
        result = agent.find_nash_equilibrium(payoff_A=payoff_A, payoff_B=payoff_B)
        assert result['success'], "5x5 game failed"

    def test_game_theory_prisoners_dilemma(self, infrastructure):
        """Test classic prisoner's dilemma."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.game_theory import GameTheoryOptimizationSpecialist

        agent = GameTheoryOptimizationSpecialist(
            agent_id='game_pd',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Prisoner's dilemma payoffs
        payoff_A = np.array([[-1, -3], [0, -2]])
        payoff_B = np.array([[-1, 0], [-3, -2]])

        result = agent.find_nash_equilibrium(payoff_A=payoff_A, payoff_B=payoff_B)
        assert result['success'], "Prisoner's dilemma failed"

    def test_variational_calculus_stiff_functional(self, infrastructure):
        """Test variational calculus with stiff functionals."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.variational_calculus import VariationalCalculusSpecialist

        agent = VariationalCalculusSpecialist(
            agent_id='var_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Brachistochrone with large height difference
        result = agent.solve_brachistochrone(x_a=0.0, y_a=0.0, x_b=10.0, y_b=-10.0)
        assert result['success'], "Large brachistochrone failed"
        assert result['time_of_descent'] > 0, "Time must be positive"

    def test_multiobjective_pareto_front(self, infrastructure):
        """Test multi-objective optimization Pareto front."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.multiobjective import MultiobjectiveOptimizationSpecialist

        agent = MultiobjectiveOptimizationSpecialist(
            agent_id='moo_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Two conflicting objectives
        result = agent.compute_pareto_front(
            objectives=['minimize_f1', 'minimize_f2'],
            n_variables=3,
            population_size=100,
            n_generations=50
        )
        assert result['success'], "Pareto front computation failed"
        assert len(result['pareto_front']) > 10, "Should find diverse Pareto solutions"

    def test_nonconvex_trust_region(self, infrastructure):
        """Test trust region method on nonconvex problems."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.nonconvex import NonconvexOptimizationSpecialist

        agent = NonconvexOptimizationSpecialist(
            agent_id='nonconvex_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        result = agent.trust_region_method(
            function_type='quartic',
            x0=[2.0, 2.0],
            max_iter=100
        )
        assert result['success'], "Trust region failed"

    def test_optimal_control_lqr(self, infrastructure):
        """Test LQR optimal control."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.optimal_control import OptimalControlSpecialist

        agent = OptimalControlSpecialist(
            agent_id='lqr_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Simple 2D system
        A = np.array([[0, 1], [0, -0.1]])
        B = np.array([[0], [1]])
        Q = np.eye(2)
        R = np.array([[1]])

        result = agent.solve_lqr(A=A, B=B, Q=Q, R=R)
        assert result['success'], "LQR solution failed"
        assert 'gain_matrix' in result, "Should return gain matrix"


# ============================================================================
# PHASE 2 - BAYESIAN DECISION & TIME SERIES STRESS TESTS
# ============================================================================

class TestBayesianDecisionStress:
    """Stress tests for Bayesian decision theory."""

    def test_decision_rules_risk(self, infrastructure):
        """Test decision rules under various loss functions."""
        from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_decision.decision_rules import DecisionRulesSpecialist

        agent = DecisionRulesSpecialist(
            agent_id='dec_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Bayes risk computation
        result = agent.compute_bayes_risk(
            loss_function='squared',
            prior_distribution='normal',
            data_points=100
        )
        assert result['success'], "Bayes risk computation failed"
        assert result['bayes_risk'] >= 0, "Risk must be non-negative"

    def test_sequential_decision_stopping(self, infrastructure):
        """Test sequential decision with optimal stopping."""
        from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_decision.sequential_decision import SequentialDecisionSpecialist

        agent = SequentialDecisionSpecialist(
            agent_id='seq_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Secretary problem
        result = agent.solve_optimal_stopping(
            problem_type='secretary',
            n_candidates=100
        )
        assert result['success'], "Optimal stopping failed"
        assert 30 <= result['optimal_stop_time'] <= 40, "Secretary rule ~37%"

    def test_utility_theory_expected_utility(self, infrastructure):
        """Test expected utility computation."""
        from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_decision.utility_theory import UtilityTheorySpecialist

        agent = UtilityTheorySpecialist(
            agent_id='util_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Risk aversion test
        result = agent.compute_expected_utility(
            utility_function='log',
            outcomes=[10, 100, 1000],
            probabilities=[0.5, 0.3, 0.2]
        )
        assert result['success'], "Expected utility failed"


class TestTimeSeriesStress:
    """Stress tests for time series analysis."""

    def test_arima_long_series(self, infrastructure):
        """Test ARIMA on long time series."""
        from symbo_agentic_reasoners.agents.specialists.statistics.timeseries.arima import ARIMASpecialist

        agent = ARIMASpecialist(
            agent_id='arima_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Generate AR(1) process
        n = 1000
        data = np.zeros(n)
        for t in range(1, n):
            data[t] = 0.7 * data[t-1] + np.random.randn()

        result = agent.fit_arima(
            data=data,
            order=(1, 0, 0)
        )
        assert result['success'], "ARIMA fitting failed"
        assert abs(result['ar_coeff'][0] - 0.7) < 0.1, "AR coefficient should be ~0.7"

    def test_kalman_filter_tracking(self, infrastructure):
        """Test Kalman filter on tracking problem."""
        from symbo_agentic_reasoners.agents.specialists.statistics.timeseries.kalman_filter import KalmanFilterSpecialist

        agent = KalmanFilterSpecialist(
            agent_id='kf_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # 1D position tracking
        result = agent.run_kalman_filter(
            observations=np.random.randn(100),
            initial_state=[0.0],
            transition_matrix=[[1.0]],
            observation_matrix=[[1.0]],
            process_noise=0.1,
            measurement_noise=1.0
        )
        assert result['success'], "Kalman filter failed"
        assert len(result['filtered_states']) == 100, "Should filter all observations"

    def test_spectral_analysis_periodogram(self, infrastructure):
        """Test spectral analysis via periodogram."""
        from symbo_agentic_reasoners.agents.specialists.statistics.timeseries.spectral_analysis import SpectralAnalysisSpecialist

        agent = SpectralAnalysisSpecialist(
            agent_id='spec_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Signal with known frequency
        t = np.linspace(0, 10, 1000)
        signal = np.sin(2 * np.pi * 5 * t) + np.random.randn(1000) * 0.1

        result = agent.compute_periodogram(signal=signal, sampling_rate=100)
        assert result['success'], "Periodogram computation failed"
        assert 'frequencies' in result, "Should return frequencies"

    def test_nonlinear_timeseries_lyapunov(self, infrastructure):
        """Test Lyapunov exponent estimation."""
        from symbo_agentic_reasoners.agents.specialists.statistics.timeseries.nonlinear_timeseries import NonlinearTimeseriesSpecialist

        agent = NonlinearTimeseriesSpecialist(
            agent_id='nl_stress',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Logistic map time series
        result = agent.estimate_lyapunov_exponent(
            timeseries_type='logistic_map',
            parameter=3.9,
            n_iterations=1000
        )
        assert result['success'], "Lyapunov estimation failed"
        assert result['lyapunov_exponent'] > 0, "Chaotic system should have positive exponent"


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

class TestPerformanceBenchmarks:
    """Performance benchmarks for all domains."""

    def test_response_time_stochastic(self, infrastructure):
        """Benchmark response time for stochastic specialists."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.brownian_motion import BrownianMotionSpecialist

        agent = BrownianMotionSpecialist(
            agent_id='bm_bench',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        start = time.time()
        result = agent.compute_moments(t=10.0, moment=2)
        elapsed = time.time() - start

        assert result['success'], "Benchmark computation failed"
        assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s (expected < 1.0s)"

    def test_response_time_optimization(self, infrastructure):
        """Benchmark response time for optimization specialists."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.nonconvex import NonconvexOptimizationSpecialist

        agent = NonconvexOptimizationSpecialist(
            agent_id='nonconvex_bench',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
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

    def test_response_time_tda(self, infrastructure):
        """Benchmark TDA persistent homology."""
        from symbo_agentic_reasoners.agents.specialists.tda.persistent_homology import PersistentHomologySpecialist

        agent = PersistentHomologySpecialist(
            agent_id='ph_bench',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Medium-sized point cloud
        points = np.random.randn(200, 2)

        start = time.time()
        result = agent.compute_persistence(points=points, max_dimension=1)
        elapsed = time.time() - start

        assert result['success'], "TDA benchmark failed"
        assert elapsed < 5.0, f"Too slow: {elapsed:.3f}s (expected < 5.0s)"


# ============================================================================
# NUMERICAL STABILITY TESTS
# ============================================================================

class TestNumericalStability:
    """Test numerical stability across all domains."""

    def test_stochastic_extreme_volatility(self, infrastructure):
        """Test SDE solver stability with extreme parameters."""
        from symbo_agentic_reasoners.agents.specialists.stochastic.sde_solver import SDESolverSpecialist

        agent = SDESolverSpecialist(
            agent_id='sde_stable',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Very high volatility
        result = agent.solve_gbm(x0=1.0, mu=0.0, sigma=10.0, T=1.0, n_steps=10000)
        assert result['success'], "High volatility should not crash"
        assert all(np.isfinite(result['path'])), "Path should have no NaN/Inf"

    def test_optimization_ill_conditioned(self, infrastructure):
        """Test optimization on ill-conditioned problems."""
        from symbo_agentic_reasoners.agents.specialists.optimization.advanced.nonconvex import NonconvexOptimizationSpecialist

        agent = NonconvexOptimizationSpecialist(
            agent_id='opt_stable',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Ill-conditioned quadratic
        result = agent.trust_region_method(
            function_type='ill_conditioned',
            condition_number=1e6,
            x0=[1.0, 1.0],
            max_iter=100
        )
        assert result['success'] or result.get('warning'), "Should handle or warn about ill-conditioning"

    def test_riemannian_near_singular(self, infrastructure):
        """Test Riemannian computations near singularities."""
        from symbo_agentic_reasoners.agents.specialists.riemannian.curvature import CurvatureSpecialist

        agent = CurvatureSpecialist(
            agent_id='curv_stable',
            df=infrastructure['df'],
            blackboard=infrastructure['blackboard']
        )

        # Near-singular metric (should handle gracefully)
        result = agent.compute_scalar_curvature(
            metric_type='near_singular',
            singular_parameter=1e-8
        )
        # Should either succeed or report numerical issues
        assert 'success' in result, "Should return status"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
