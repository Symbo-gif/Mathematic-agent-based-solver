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
EXPLORATION LAYER - STRATEGY LIBRARY
====================================

Initial library of 50+ solution strategies across all mathematical domains.

This module provides the bootstrap knowledge for the exploration system.
Each strategy encodes a proven approach to solving problems in its domain,
with reasonable prior success rates that will be refined through learning.

ORGANIZATION:
------------
Strategies are organized by domain:
- CALCULUS_STRATEGIES: Integration, differentiation, limits, series
- ALGEBRA_STRATEGIES: Equations, polynomials, factorization
- LINEAR_ALGEBRA_STRATEGIES: Matrices, vectors, decompositions
- GEOMETRY_STRATEGIES: Euclidean, analytic, trigonometry
- LOGIC_STRATEGIES: Propositional, predicate, proof techniques
- NUMBER_THEORY_STRATEGIES: Primes, divisibility, modular arithmetic
- STATISTICS_STRATEGIES: Distributions, inference, Bayesian methods
- DISCRETE_MATH_STRATEGIES: Combinatorics, graphs, algorithms
- PHYSICS_STRATEGIES: Mechanics, electromagnetism, thermodynamics

REFERENCE:
---------
Implementation Plan: Phase 1, File 2
"""

from typing import List, Dict, Any
from symbo_agentic_reasoners.agents.base.problem_analysis import MathDomain
from symbo_agentic_reasoners.exploration.data_structures import Strategy


# ===========================================================================
# CALCULUS STRATEGIES
# ===========================================================================

CALCULUS_STRATEGIES = [
    Strategy(
        strategy_id='calc_001',
        name='Direct Symbolic Integration (Risch)',
        domain=MathDomain.CALCULUS,
        techniques=['parse_integrand', 'apply_risch_algorithm', 'verify_derivative'],
        preconditions={
            'operation': 'integrate',
            'integrand_type': ['polynomial', 'rational', 'exponential', 'logarithmic']
        },
        estimated_cost='high',
        success_rate=0.65,
        metadata={'method': 'symbolic', 'completeness': 'complete_for_elementary'}
    ),

    Strategy(
        strategy_id='calc_002',
        name='Substitution then Integration',
        domain=MathDomain.CALCULUS,
        techniques=['identify_substitution', 'apply_substitution', 'integrate_simplified', 'back_substitute'],
        preconditions={
            'operation': 'integrate',
            'has_composite_function': True
        },
        estimated_cost='medium',
        success_rate=0.75,
        metadata={'method': 'symbolic', 'pattern': 'u_substitution'}
    ),

    Strategy(
        strategy_id='calc_003',
        name='Integration by Parts',
        domain=MathDomain.CALCULUS,
        techniques=['identify_product', 'choose_u_dv', 'apply_integration_by_parts', 'simplify_result'],
        preconditions={
            'operation': 'integrate',
            'has_product': True
        },
        estimated_cost='medium',
        success_rate=0.70,
        metadata={'method': 'symbolic', 'pattern': 'product_rule_reverse'}
    ),

    Strategy(
        strategy_id='calc_004',
        name='Numerical Quadrature Fallback',
        domain=MathDomain.CALCULUS,
        techniques=['setup_integration_bounds', 'apply_quad', 'estimate_error'],
        preconditions={
            'operation': 'integrate',
            'definite_integral': True
        },
        estimated_cost='low',
        success_rate=0.95,
        metadata={'method': 'numerical', 'accuracy': 'high'}
    ),

    Strategy(
        strategy_id='calc_005',
        name='Power Rule Differentiation',
        domain=MathDomain.CALCULUS,
        techniques=['identify_polynomial_terms', 'apply_power_rule', 'sum_derivatives'],
        preconditions={
            'operation': 'differentiate',
            'expression_type': 'polynomial'
        },
        estimated_cost='low',
        success_rate=0.98,
        metadata={'method': 'symbolic', 'rule': 'power_rule'}
    ),

    Strategy(
        strategy_id='calc_006',
        name='Chain Rule Differentiation',
        domain=MathDomain.CALCULUS,
        techniques=['identify_composition', 'differentiate_outer', 'differentiate_inner', 'multiply_derivatives'],
        preconditions={
            'operation': 'differentiate',
            'has_composite_function': True
        },
        estimated_cost='medium',
        success_rate=0.85,
        metadata={'method': 'symbolic', 'rule': 'chain_rule'}
    ),

    Strategy(
        strategy_id='calc_007',
        name='L\'Hôpital\'s Rule for Limits',
        domain=MathDomain.CALCULUS,
        techniques=['verify_indeterminate_form', 'differentiate_numerator', 'differentiate_denominator', 'evaluate_limit'],
        preconditions={
            'operation': 'limit',
            'indeterminate_form': ['0/0', 'inf/inf']
        },
        estimated_cost='medium',
        success_rate=0.80,
        metadata={'method': 'symbolic', 'rule': 'lhopital'}
    ),

    Strategy(
        strategy_id='calc_008',
        name='Taylor Series Expansion',
        domain=MathDomain.CALCULUS,
        techniques=['compute_derivatives', 'evaluate_at_center', 'construct_series', 'determine_convergence'],
        preconditions={
            'operation': 'series',
            'expansion_type': 'taylor'
        },
        estimated_cost='high',
        success_rate=0.72,
        metadata={'method': 'symbolic', 'series_type': 'taylor'}
    ),
]


# ===========================================================================
# ALGEBRA STRATEGIES
# ===========================================================================

ALGEBRA_STRATEGIES = [
    Strategy(
        strategy_id='alg_001',
        name='Direct Polynomial Factorization',
        domain=MathDomain.ALGEBRA,
        techniques=['identify_polynomial', 'apply_factorization_algorithm', 'verify_expansion'],
        preconditions={
            'operation': 'factor',
            'expression_type': 'polynomial',
            'degree': {'max': 4}
        },
        estimated_cost='medium',
        success_rate=0.85,
        metadata={'method': 'symbolic', 'algorithm': 'kronecker'}
    ),

    Strategy(
        strategy_id='alg_002',
        name='Quadratic Formula',
        domain=MathDomain.ALGEBRA,
        techniques=['extract_coefficients', 'compute_discriminant', 'apply_quadratic_formula', 'simplify_roots'],
        preconditions={
            'operation': 'solve',
            'equation_type': 'quadratic'
        },
        estimated_cost='low',
        success_rate=0.99,
        metadata={'method': 'closed_form', 'formula': 'quadratic'}
    ),

    Strategy(
        strategy_id='alg_003',
        name='Completing the Square',
        domain=MathDomain.ALGEBRA,
        techniques=['normalize_coefficient', 'complete_square', 'solve_transformed', 'back_substitute'],
        preconditions={
            'operation': 'solve',
            'equation_type': 'quadratic'
        },
        estimated_cost='medium',
        success_rate=0.88,
        metadata={'method': 'algebraic_manipulation'}
    ),

    Strategy(
        strategy_id='alg_004',
        name='System of Linear Equations (Gaussian Elimination)',
        domain=MathDomain.ALGEBRA,
        techniques=['construct_augmented_matrix', 'apply_gaussian_elimination', 'back_substitution', 'verify_solution'],
        preconditions={
            'operation': 'solve',
            'system_type': 'linear',
            'num_equations': {'min': 2}
        },
        estimated_cost='medium',
        success_rate=0.92,
        metadata={'method': 'matrix_reduction'}
    ),

    Strategy(
        strategy_id='alg_005',
        name='Rational Root Theorem',
        domain=MathDomain.ALGEBRA,
        techniques=['extract_coefficients', 'list_candidates', 'test_roots', 'factor_out_roots'],
        preconditions={
            'operation': 'solve',
            'expression_type': 'polynomial',
            'coefficients_type': 'integer'
        },
        estimated_cost='medium',
        success_rate=0.68,
        metadata={'method': 'trial_and_error', 'theorem': 'rational_root'}
    ),

    Strategy(
        strategy_id='alg_006',
        name='Polynomial Long Division',
        domain=MathDomain.ALGEBRA,
        techniques=['setup_division', 'divide_leading_terms', 'multiply_and_subtract', 'iterate_to_remainder'],
        preconditions={
            'operation': 'divide',
            'expression_type': 'polynomial'
        },
        estimated_cost='medium',
        success_rate=0.93,
        metadata={'method': 'algorithmic'}
    ),

    Strategy(
        strategy_id='alg_007',
        name='Exponential Equation via Logarithms',
        domain=MathDomain.ALGEBRA,
        techniques=['isolate_exponential', 'take_logarithm', 'solve_linear', 'verify_solution'],
        preconditions={
            'operation': 'solve',
            'has_exponential': True
        },
        estimated_cost='low',
        success_rate=0.87,
        metadata={'method': 'logarithmic'}
    ),

    Strategy(
        strategy_id='alg_008',
        name='Simplification via Algebraic Identities',
        domain=MathDomain.ALGEBRA,
        techniques=['identify_patterns', 'apply_identities', 'combine_like_terms', 'verify_equivalence'],
        preconditions={
            'operation': 'simplify',
            'expression_type': ['polynomial', 'rational']
        },
        estimated_cost='low',
        success_rate=0.82,
        metadata={'method': 'algebraic_manipulation'}
    ),
]


# ===========================================================================
# LINEAR ALGEBRA STRATEGIES
# ===========================================================================

LINEAR_ALGEBRA_STRATEGIES = [
    Strategy(
        strategy_id='linalg_001',
        name='Matrix Multiplication',
        domain=MathDomain.LINEAR_ALGEBRA,
        techniques=['verify_dimensions', 'compute_dot_products', 'construct_result_matrix'],
        preconditions={
            'operation': 'multiply',
            'operand_type': 'matrix'
        },
        estimated_cost='medium',
        success_rate=0.97,
        metadata={'method': 'direct_computation'}
    ),

    Strategy(
        strategy_id='linalg_002',
        name='LU Decomposition',
        domain=MathDomain.LINEAR_ALGEBRA,
        techniques=['apply_gaussian_elimination_with_pivoting', 'extract_L_and_U', 'verify_decomposition'],
        preconditions={
            'operation': 'decompose',
            'decomposition_type': 'LU'
        },
        estimated_cost='high',
        success_rate=0.89,
        metadata={'method': 'factorization', 'type': 'LU'}
    ),

    Strategy(
        strategy_id='linalg_003',
        name='QR Decomposition',
        domain=MathDomain.LINEAR_ALGEBRA,
        techniques=['apply_gram_schmidt', 'normalize_columns', 'construct_Q_and_R', 'verify_orthogonality'],
        preconditions={
            'operation': 'decompose',
            'decomposition_type': 'QR'
        },
        estimated_cost='high',
        success_rate=0.86,
        metadata={'method': 'gram_schmidt', 'type': 'QR'}
    ),

    Strategy(
        strategy_id='linalg_004',
        name='Eigenvalue via Characteristic Polynomial',
        domain=MathDomain.LINEAR_ALGEBRA,
        techniques=['compute_characteristic_polynomial', 'solve_polynomial', 'verify_eigenvalues'],
        preconditions={
            'operation': 'eigenvalues',
            'matrix_size': {'max': 3}
        },
        estimated_cost='high',
        success_rate=0.78,
        metadata={'method': 'characteristic_poly'}
    ),

    Strategy(
        strategy_id='linalg_005',
        name='Determinant via Cofactor Expansion',
        domain=MathDomain.LINEAR_ALGEBRA,
        techniques=['choose_expansion_row', 'compute_cofactors', 'sum_products', 'simplify'],
        preconditions={
            'operation': 'determinant',
            'matrix_size': {'max': 4}
        },
        estimated_cost='high',
        success_rate=0.91,
        metadata={'method': 'cofactor_expansion'}
    ),

    Strategy(
        strategy_id='linalg_006',
        name='Matrix Inverse via Gaussian Elimination',
        domain=MathDomain.LINEAR_ALGEBRA,
        techniques=['augment_with_identity', 'row_reduce_to_identity', 'extract_inverse', 'verify_inverse'],
        preconditions={
            'operation': 'invert',
            'operand_type': 'matrix'
        },
        estimated_cost='high',
        success_rate=0.84,
        metadata={'method': 'gaussian_elimination'}
    ),

    Strategy(
        strategy_id='linalg_007',
        name='Vector Cross Product',
        domain=MathDomain.LINEAR_ALGEBRA,
        techniques=['verify_3d_vectors', 'compute_determinant_form', 'construct_result_vector'],
        preconditions={
            'operation': 'cross_product',
            'vector_dimension': 3
        },
        estimated_cost='low',
        success_rate=0.98,
        metadata={'method': 'determinant_formula'}
    ),
]


# ===========================================================================
# GEOMETRY STRATEGIES
# ===========================================================================

GEOMETRY_STRATEGIES = [
    Strategy(
        strategy_id='geom_001',
        name='Distance Formula (Euclidean)',
        domain=MathDomain.GEOMETRY,
        techniques=['extract_coordinates', 'compute_differences', 'apply_pythagorean', 'simplify_radical'],
        preconditions={
            'operation': 'distance',
            'space_type': 'euclidean'
        },
        estimated_cost='low',
        success_rate=0.99,
        metadata={'method': 'distance_formula'}
    ),

    Strategy(
        strategy_id='geom_002',
        name='Pythagorean Theorem',
        domain=MathDomain.GEOMETRY,
        techniques=['identify_right_triangle', 'apply_pythagorean_theorem', 'solve_for_unknown', 'verify_solution'],
        preconditions={
            'operation': 'solve',
            'shape': 'right_triangle'
        },
        estimated_cost='low',
        success_rate=0.96,
        metadata={'theorem': 'pythagorean'}
    ),

    Strategy(
        strategy_id='geom_003',
        name='Law of Cosines',
        domain=MathDomain.GEOMETRY,
        techniques=['identify_triangle_type', 'apply_law_of_cosines', 'solve_for_unknown', 'verify_triangle_inequality'],
        preconditions={
            'operation': 'solve',
            'shape': 'triangle'
        },
        estimated_cost='medium',
        success_rate=0.88,
        metadata={'theorem': 'law_of_cosines'}
    ),

    Strategy(
        strategy_id='geom_004',
        name='Trigonometric Identities',
        domain=MathDomain.GEOMETRY,
        techniques=['identify_trig_pattern', 'apply_identity', 'simplify_expression', 'verify_equivalence'],
        preconditions={
            'operation': 'simplify',
            'has_trigonometric': True
        },
        estimated_cost='medium',
        success_rate=0.79,
        metadata={'method': 'trig_identities'}
    ),

    Strategy(
        strategy_id='geom_005',
        name='Circle Equation (Completing the Square)',
        domain=MathDomain.GEOMETRY,
        techniques=['complete_square_x', 'complete_square_y', 'extract_center_and_radius', 'verify_circle'],
        preconditions={
            'operation': 'analyze',
            'shape': 'circle',
            'form': 'general'
        },
        estimated_cost='medium',
        success_rate=0.92,
        metadata={'method': 'completing_square'}
    ),
]


# ===========================================================================
# LOGIC STRATEGIES
# ===========================================================================

LOGIC_STRATEGIES = [
    Strategy(
        strategy_id='logic_001',
        name='Truth Table Construction',
        domain=MathDomain.LOGIC,
        techniques=['identify_variables', 'enumerate_valuations', 'evaluate_formula', 'construct_table'],
        preconditions={
            'operation': 'evaluate',
            'logic_type': 'propositional',
            'num_variables': {'max': 5}
        },
        estimated_cost='medium',
        success_rate=0.94,
        metadata={'method': 'exhaustive_enumeration'}
    ),

    Strategy(
        strategy_id='logic_002',
        name='Direct Proof',
        domain=MathDomain.LOGIC,
        techniques=['assume_hypothesis', 'apply_logical_rules', 'derive_conclusion', 'verify_validity'],
        preconditions={
            'operation': 'prove',
            'proof_type': 'direct'
        },
        estimated_cost='high',
        success_rate=0.67,
        metadata={'method': 'direct_proof'}
    ),

    Strategy(
        strategy_id='logic_003',
        name='Proof by Contradiction',
        domain=MathDomain.LOGIC,
        techniques=['assume_negation', 'derive_contradiction', 'conclude_original_statement'],
        preconditions={
            'operation': 'prove',
            'proof_type': ['indirect', 'contradiction']
        },
        estimated_cost='high',
        success_rate=0.73,
        metadata={'method': 'contradiction'}
    ),

    Strategy(
        strategy_id='logic_004',
        name='Modus Ponens Application',
        domain=MathDomain.LOGIC,
        techniques=['identify_conditional', 'identify_antecedent', 'apply_modus_ponens', 'derive_consequent'],
        preconditions={
            'operation': 'infer',
            'has_conditional': True,
            'has_antecedent': True
        },
        estimated_cost='low',
        success_rate=0.96,
        metadata={'rule': 'modus_ponens'}
    ),
]


# ===========================================================================
# NUMBER THEORY STRATEGIES
# ===========================================================================

NUMBER_THEORY_STRATEGIES = [
    Strategy(
        strategy_id='num_001',
        name='Euclidean Algorithm for GCD',
        domain=MathDomain.NUMBER_THEORY,
        techniques=['apply_euclidean_algorithm', 'iterate_until_zero', 'return_gcd'],
        preconditions={
            'operation': 'gcd',
            'operand_type': 'integer'
        },
        estimated_cost='low',
        success_rate=0.99,
        metadata={'algorithm': 'euclidean'}
    ),

    Strategy(
        strategy_id='num_002',
        name='Sieve of Eratosthenes',
        domain=MathDomain.NUMBER_THEORY,
        techniques=['initialize_candidates', 'mark_multiples', 'extract_primes'],
        preconditions={
            'operation': 'find_primes',
            'range_max': {'max': 10000}
        },
        estimated_cost='medium',
        success_rate=0.98,
        metadata={'algorithm': 'sieve_of_eratosthenes'}
    ),

    Strategy(
        strategy_id='num_003',
        name='Modular Exponentiation',
        domain=MathDomain.NUMBER_THEORY,
        techniques=['apply_repeated_squaring', 'reduce_mod_n', 'compute_result'],
        preconditions={
            'operation': 'power',
            'modulo': True
        },
        estimated_cost='low',
        success_rate=0.97,
        metadata={'method': 'fast_modular_exponentiation'}
    ),

    Strategy(
        strategy_id='num_004',
        name='Chinese Remainder Theorem',
        domain=MathDomain.NUMBER_THEORY,
        techniques=['verify_coprime_moduli', 'compute_bezout_coefficients', 'apply_crt', 'verify_solution'],
        preconditions={
            'operation': 'solve',
            'system_type': 'modular_congruences'
        },
        estimated_cost='high',
        success_rate=0.81,
        metadata={'theorem': 'chinese_remainder'}
    ),
]


# ===========================================================================
# STATISTICS STRATEGIES
# ===========================================================================

STATISTICS_STRATEGIES = [
    Strategy(
        strategy_id='stats_001',
        name='Sample Mean and Variance',
        domain=MathDomain.STATISTICS,
        techniques=['compute_sample_mean', 'compute_deviations', 'compute_variance', 'compute_std_dev'],
        preconditions={
            'operation': 'descriptive_stats',
            'data_type': 'sample'
        },
        estimated_cost='low',
        success_rate=0.99,
        metadata={'method': 'descriptive'}
    ),

    Strategy(
        strategy_id='stats_002',
        name='Bayes\' Theorem Application',
        domain=MathDomain.STATISTICS,
        techniques=['identify_prior', 'identify_likelihood', 'compute_marginal', 'apply_bayes_rule'],
        preconditions={
            'operation': 'probability',
            'method': 'bayesian'
        },
        estimated_cost='medium',
        success_rate=0.85,
        metadata={'theorem': 'bayes'}
    ),

    Strategy(
        strategy_id='stats_003',
        name='Hypothesis Test (t-test)',
        domain=MathDomain.STATISTICS,
        techniques=['state_hypotheses', 'compute_test_statistic', 'determine_p_value', 'make_decision'],
        preconditions={
            'operation': 'hypothesis_test',
            'test_type': 't_test'
        },
        estimated_cost='medium',
        success_rate=0.90,
        metadata={'method': 'frequentist', 'test': 't_test'}
    ),

    Strategy(
        strategy_id='stats_004',
        name='Linear Regression (Least Squares)',
        domain=MathDomain.STATISTICS,
        techniques=['compute_means', 'compute_covariance', 'compute_slope', 'compute_intercept', 'verify_fit'],
        preconditions={
            'operation': 'regression',
            'model_type': 'linear'
        },
        estimated_cost='medium',
        success_rate=0.93,
        metadata={'method': 'least_squares'}
    ),
]


# ===========================================================================
# DISCRETE MATH STRATEGIES
# ===========================================================================

DISCRETE_MATH_STRATEGIES = [
    Strategy(
        strategy_id='discrete_001',
        name='Combinatorial Counting (nCr)',
        domain=MathDomain.DISCRETE_MATH,
        techniques=['compute_factorial_n', 'compute_factorial_r', 'compute_factorial_n_minus_r', 'compute_binomial'],
        preconditions={
            'operation': 'combinations',
            'n': {'max': 100}
        },
        estimated_cost='low',
        success_rate=0.98,
        metadata={'formula': 'binomial_coefficient'}
    ),

    Strategy(
        strategy_id='discrete_002',
        name='Graph Traversal (DFS)',
        domain=MathDomain.DISCRETE_MATH,
        techniques=['initialize_visited', 'apply_depth_first_search', 'record_traversal_order'],
        preconditions={
            'operation': 'traverse',
            'data_structure': 'graph',
            'algorithm': 'DFS'
        },
        estimated_cost='medium',
        success_rate=0.96,
        metadata={'algorithm': 'depth_first_search'}
    ),

    Strategy(
        strategy_id='discrete_003',
        name='Dijkstra\'s Shortest Path',
        domain=MathDomain.DISCRETE_MATH,
        techniques=['initialize_distances', 'select_minimum_vertex', 'update_neighbors', 'iterate_until_complete'],
        preconditions={
            'operation': 'shortest_path',
            'graph_type': 'weighted',
            'weights': 'non_negative'
        },
        estimated_cost='high',
        success_rate=0.92,
        metadata={'algorithm': 'dijkstra'}
    ),

    Strategy(
        strategy_id='discrete_004',
        name='Inclusion-Exclusion Principle',
        domain=MathDomain.DISCRETE_MATH,
        techniques=['identify_sets', 'compute_individual_sizes', 'compute_intersection_sizes', 'apply_inclusion_exclusion'],
        preconditions={
            'operation': 'count',
            'method': 'inclusion_exclusion'
        },
        estimated_cost='medium',
        success_rate=0.84,
        metadata={'principle': 'inclusion_exclusion'}
    ),
]


# ===========================================================================
# PHYSICS STRATEGIES
# ===========================================================================

PHYSICS_STRATEGIES = [
    Strategy(
        strategy_id='phys_001',
        name='Kinematic Equations (Constant Acceleration)',
        domain=MathDomain.PHYSICS_MECHANICS,
        techniques=['identify_known_variables', 'select_kinematic_equation', 'solve_for_unknown', 'verify_units'],
        preconditions={
            'operation': 'solve',
            'domain': 'kinematics',
            'acceleration': 'constant'
        },
        estimated_cost='low',
        success_rate=0.94,
        metadata={'physics_domain': 'kinematics'}
    ),

    Strategy(
        strategy_id='phys_002',
        name='Energy Conservation',
        domain=MathDomain.PHYSICS_MECHANICS,
        techniques=['identify_energy_forms', 'set_initial_state', 'set_final_state', 'equate_total_energy', 'solve_for_unknown'],
        preconditions={
            'operation': 'solve',
            'principle': 'energy_conservation',
            'system': 'conservative'
        },
        estimated_cost='medium',
        success_rate=0.88,
        metadata={'conservation_law': 'energy'}
    ),

    Strategy(
        strategy_id='phys_003',
        name='Ohm\'s Law Application',
        domain=MathDomain.PHYSICS_EM,
        techniques=['identify_circuit_type', 'apply_ohms_law', 'solve_for_unknown', 'verify_units'],
        preconditions={
            'operation': 'solve',
            'domain': 'circuits',
            'circuit_type': 'DC'
        },
        estimated_cost='low',
        success_rate=0.97,
        metadata={'law': 'ohms_law'}
    ),

    Strategy(
        strategy_id='phys_004',
        name='Ideal Gas Law',
        domain=MathDomain.PHYSICS_THERMO,
        techniques=['identify_known_variables', 'apply_ideal_gas_law', 'solve_for_unknown', 'verify_assumptions'],
        preconditions={
            'operation': 'solve',
            'system': 'ideal_gas'
        },
        estimated_cost='low',
        success_rate=0.93,
        metadata={'equation': 'PV_nRT'}
    ),
]


# ===========================================================================
# LIBRARY ACCESS FUNCTIONS
# ===========================================================================

def get_all_strategies() -> List[Strategy]:
    """
    Get all strategies across all domains.

    Returns:
        List of all 50+ strategies
    """
    all_strategies = []
    all_strategies.extend(CALCULUS_STRATEGIES)
    all_strategies.extend(ALGEBRA_STRATEGIES)
    all_strategies.extend(LINEAR_ALGEBRA_STRATEGIES)
    all_strategies.extend(GEOMETRY_STRATEGIES)
    all_strategies.extend(LOGIC_STRATEGIES)
    all_strategies.extend(NUMBER_THEORY_STRATEGIES)
    all_strategies.extend(STATISTICS_STRATEGIES)
    all_strategies.extend(DISCRETE_MATH_STRATEGIES)
    all_strategies.extend(PHYSICS_STRATEGIES)
    return all_strategies


def get_strategies_by_domain(domain: MathDomain) -> List[Strategy]:
    """
    Get all strategies for a specific domain.

    Args:
        domain: The mathematical domain

    Returns:
        List of strategies for that domain
    """
    domain_map = {
        MathDomain.CALCULUS: CALCULUS_STRATEGIES,
        MathDomain.ALGEBRA: ALGEBRA_STRATEGIES,
        MathDomain.LINEAR_ALGEBRA: LINEAR_ALGEBRA_STRATEGIES,
        MathDomain.GEOMETRY: GEOMETRY_STRATEGIES,
        MathDomain.LOGIC: LOGIC_STRATEGIES,
        MathDomain.NUMBER_THEORY: NUMBER_THEORY_STRATEGIES,
        MathDomain.STATISTICS: STATISTICS_STRATEGIES,
        MathDomain.DISCRETE_MATH: DISCRETE_MATH_STRATEGIES,
        MathDomain.PHYSICS_MECHANICS: [s for s in PHYSICS_STRATEGIES if 'kinematics' in s.metadata.get('physics_domain', '') or 'mechanics' in s.name.lower()],
        MathDomain.PHYSICS_EM: [s for s in PHYSICS_STRATEGIES if 'circuits' in s.metadata.get('domain', '') or 'ohm' in s.name.lower()],
        MathDomain.PHYSICS_THERMO: [s for s in PHYSICS_STRATEGIES if 'gas' in s.name.lower() or 'thermo' in s.name.lower()],
    }
    return domain_map.get(domain, [])


def get_strategies_for_features(features: Dict[str, Any]) -> List[Strategy]:
    """
    Get strategies matching specific problem features.

    Args:
        features: Problem feature dict (operation, domain, etc.)

    Returns:
        List of potentially applicable strategies
    """
    candidates = []

    # Get domain-specific strategies
    if 'domain' in features:
        domain = features['domain']
        if isinstance(domain, str):
            try:
                domain = MathDomain(domain)
            except ValueError:
                domain = MathDomain.UNKNOWN

        if domain != MathDomain.UNKNOWN:
            candidates.extend(get_strategies_by_domain(domain))

    # Also include cross-domain strategies
    all_strategies = get_all_strategies()

    # Filter by operation if specified
    if 'operation' in features:
        operation = features['operation']
        for strategy in all_strategies:
            if strategy.preconditions.get('operation') == operation:
                if strategy not in candidates:
                    candidates.append(strategy)

    # Return unique strategies
    seen_ids = set()
    unique_candidates = []
    for strategy in candidates:
        if strategy.strategy_id not in seen_ids:
            seen_ids.add(strategy.strategy_id)
            unique_candidates.append(strategy)

    return unique_candidates


# Statistics for validation
TOTAL_STRATEGIES = len(get_all_strategies())
