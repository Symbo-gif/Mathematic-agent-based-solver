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
FUNCTIONAL ANALYSIS BRUTAL STRESS TESTS
========================================

50 research-level stress tests designed to BREAK the system.
Targets: BanachSpaceSpecialist, HilbertSpaceSpecialist, OperatorTheorySpecialist

These tests exploit:
- Numerical instabilities near singularities
- Ill-conditioned operators approaching unboundedness
- Pathological function spaces and functionals
- Edge cases in spectral theory
- Non-normal operators defying spectral decomposition
- Near-degenerate subspaces
- Discontinuous functionals on continuous duals

Author: Mathematical Crackfinder Agent
"""

import numpy as np
from typing import Dict, Any, List

# =============================================================================
# 50 BRUTAL FUNCTIONAL ANALYSIS STRESS TESTS
# =============================================================================

FUNCTIONAL_ANALYSIS_STRESS_TESTS: List[Dict[str, Any]] = [
    # =========================================================================
    # CATEGORY 1: OPERATOR NORMS OF NEARLY UNBOUNDED OPERATORS (FUNC_001-005)
    # =========================================================================
    {
        "test_id": "FUNC_001",
        "category": "operator_norm_unbounded",
        "input": {
            "description": "Diagonal operator with eigenvalues 1/epsilon approaching infinity",
            "matrix": "diag([1, 10, 100, 1000, 10000, 100000, 1e6, 1e7, 1e8, 1e9])",
            "operation": "compute_operator_norm"
        },
        "expected": {
            "operator_norm": 1e9,
            "is_bounded": True,
            "numerical_stability": "should handle large norm without overflow"
        },
        "difficulty": "brutal",
        "rationale": "Tests operator norm computation when eigenvalues span 9 orders of magnitude. "
                     "Numerical underflow in normalization of extremal eigenvectors can corrupt results."
    },
    {
        "test_id": "FUNC_002",
        "category": "operator_norm_unbounded",
        "input": {
            "description": "Volterra-like integral operator discretization (quasi-nilpotent)",
            "matrix": "np.triu(np.ones((100, 100))) / 100",
            "operation": "compute_operator_norm"
        },
        "expected": {
            "operator_norm_approx": 0.637,  # 2/pi for Volterra
            "spectral_radius": 0.01,
            "note": "||T|| >> r(T) for non-normal operators"
        },
        "difficulty": "brutal",
        "rationale": "The Volterra operator has spectral radius 0 but operator norm 2/pi. "
                     "Demonstrates failure of spectral radius as norm proxy for non-normal operators."
    },
    {
        "test_id": "FUNC_003",
        "category": "operator_norm_unbounded",
        "input": {
            "description": "Shift operator on truncated l2 with periodic extension",
            "matrix": "circulant_matrix([0,1,0,0,...,0]) dimension 500",
            "operation": "operator_norm",
            "p_norm": 2
        },
        "expected": {
            "operator_norm": 1.0,
            "is_isometry": True,
            "numerical_precision": "1e-12"
        },
        "difficulty": "extreme",
        "rationale": "Circular shift is unitary but power iteration may not converge for unit eigenvalues. "
                     "Tests whether the system recognizes isometries without SVD."
    },
    {
        "test_id": "FUNC_004",
        "category": "operator_norm_unbounded",
        "input": {
            "description": "Nearly singular operator: I + epsilon*nilpotent, epsilon=1e-14",
            "matrix": "np.eye(50) + 1e-14 * np.triu(np.ones((50,50)), k=1)",
            "operation": "operator_norm"
        },
        "expected": {
            "operator_norm_approx": 1.0,
            "condition_number": "very large due to nilpotent perturbation",
            "stability_test": "norm should be 1 +/- machine epsilon"
        },
        "difficulty": "pathological",
        "rationale": "Perturbation is at machine epsilon level. Tests whether operator norm computation "
                     "distinguishes identity from nearly-identity under floating point arithmetic."
    },
    {
        "test_id": "FUNC_005",
        "category": "operator_norm_unbounded",
        "input": {
            "description": "Cesaro averaging operator (compact, non-normal)",
            "matrix": "C[i,j] = 1/(i+1) if j <= i else 0, dimension 200",
            "operation": "operator_norm"
        },
        "expected": {
            "operator_norm": 2.0,  # Exact for Cesaro on l2
            "spectral_radius": 1.0,
            "compactness": True
        },
        "difficulty": "brutal",
        "rationale": "Cesaro operator is bounded on l2 with norm 2 but spectral radius 1. "
                     "Tests handling of compact non-self-adjoint operators."
    },

    # =========================================================================
    # CATEGORY 2: SPECTRUM OF COMPACT OPERATORS (FUNC_006-010)
    # =========================================================================
    {
        "test_id": "FUNC_006",
        "category": "spectrum_compact",
        "input": {
            "description": "Hilbert-Schmidt operator with rapidly decaying singular values",
            "matrix": "diag([1/n^2 for n in 1..1000])",
            "operation": "compute_spectrum"
        },
        "expected": {
            "point_spectrum": "[1, 1/4, 1/9, 1/16, ..., 1/1000000]",
            "accumulation_point": 0,
            "spectral_radius": 1.0
        },
        "difficulty": "brutal",
        "rationale": "Spectrum has 1000 distinct eigenvalues converging to 0. Tests whether system "
                     "correctly identifies accumulation at 0 and handles multiplicity 1 throughout."
    },
    {
        "test_id": "FUNC_007",
        "category": "spectrum_compact",
        "input": {
            "description": "Nuclear operator with super-exponential decay",
            "matrix": "diag([exp(-n*n) for n in 1..100])",
            "operation": "compute_spectrum"
        },
        "expected": {
            "trace_class": True,
            "nuclear_norm_approx": "sum of singular values",
            "smallest_eigenvalue_order": "1e-4343"
        },
        "difficulty": "pathological",
        "rationale": "Eigenvalues decay faster than any exponential. The smallest eigenvalues are below "
                     "machine epsilon by factor of 10^4000, testing underflow handling."
    },
    {
        "test_id": "FUNC_008",
        "category": "spectrum_compact",
        "input": {
            "description": "Rank-one perturbation of diagonal: D + uv^T",
            "matrix": "diag([1,2,3,...,50]) + outer_product([1,1,...,1], [1,-1,1,-1,...])",
            "operation": "compute_spectrum"
        },
        "expected": {
            "eigenvalue_shift": "non-trivial perturbation of diagonal spectrum",
            "interlacing": "partial interlacing may apply",
            "secular_equation": "det(D - lambda I + uv^T) = 0"
        },
        "difficulty": "extreme",
        "rationale": "Rank-one perturbations shift eigenvalues according to secular equation. "
                     "Tests whether spectrum computation handles non-diagonal perturbations correctly."
    },
    {
        "test_id": "FUNC_009",
        "category": "spectrum_compact",
        "input": {
            "description": "Toeplitz operator from singular symbol",
            "matrix": "toeplitz_matrix(symbol = |z-1|^0.5 on unit circle, dim=100)",
            "operation": "compute_spectrum"
        },
        "expected": {
            "essential_spectrum": "depends on essential range of symbol",
            "eigenvalues_outside_essential": "possible for non-normal Toeplitz",
            "spectral_inclusion": "should contain essential range"
        },
        "difficulty": "pathological",
        "rationale": "Singular symbols produce Toeplitz operators with spectra beyond essential range. "
                     "Tests spectral approximation for non-normal operators."
    },
    {
        "test_id": "FUNC_010",
        "category": "spectrum_compact",
        "input": {
            "description": "Finite-section approximation of multiplication operator M_f, f(x)=x",
            "matrix": "tridiagonal with 0 on diagonal, 1/2 on off-diagonals, dim=500",
            "operation": "compute_spectrum"
        },
        "expected": {
            "eigenvalues": "cos(k*pi/(n+1)) for k=1..n",
            "spectral_range": "(-1, 1)",
            "limiting_spectrum": "[-1, 1] as n -> infinity"
        },
        "difficulty": "brutal",
        "rationale": "Discrete Laplacian spectrum converges to continuous [-1,1]. Tests whether "
                     "finite approximations capture continuous spectrum correctly."
    },

    # =========================================================================
    # CATEGORY 3: PROJECTIONS ONTO NON-CLOSED SUBSPACES (FUNC_011-015)
    # =========================================================================
    {
        "test_id": "FUNC_011",
        "category": "projection_non_closed",
        "input": {
            "description": "Projection onto span of {e_n/n : n=1,2,...,100} in l2",
            "vectors": "[e_1, e_2/2, e_3/3, ..., e_100/100]",
            "target_vector": "e_1 + e_2 + ... + e_100",
            "operation": "project_onto_subspace"
        },
        "expected": {
            "projection_exists": True,
            "subspace_not_closed_in_limit": "in infinite dim, closure includes 0",
            "gram_matrix_condition": "ill-conditioned due to decaying norms"
        },
        "difficulty": "brutal",
        "rationale": "The vectors have decreasing norms, making the Gram matrix increasingly ill-conditioned. "
                     "Tests numerical stability of projection onto nearly-degenerate subspaces."
    },
    {
        "test_id": "FUNC_012",
        "category": "projection_non_closed",
        "input": {
            "description": "Projection onto range of compact non-injective operator",
            "operator_matrix": "np.outer([1,0,0,...], [1,0,0,...]) in R^100",
            "target_vector": "[1,1,1,...,1]",
            "operation": "project_onto_range"
        },
        "expected": {
            "range_is_closed": True,  # Range of rank-1 is closed
            "projection": "[1, 0, 0, ..., 0]",
            "distance_to_range": "sqrt(99)"
        },
        "difficulty": "extreme",
        "rationale": "Rank-1 operator has 1D closed range. Tests whether projection onto degenerate ranges "
                     "is computed correctly without pseudo-inverse instabilities."
    },
    {
        "test_id": "FUNC_013",
        "category": "projection_non_closed",
        "input": {
            "description": "Orthogonal projection with nearly parallel basis vectors",
            "basis": "[v1, v2] where angle(v1, v2) = 1e-10 radians in R^100",
            "target_vector": "random unit vector",
            "operation": "project_onto_subspace"
        },
        "expected": {
            "projection_unstable": True,
            "condition_of_gram_matrix": "~1e20",
            "numerical_error_expected": "catastrophic cancellation"
        },
        "difficulty": "pathological",
        "rationale": "Near-parallel vectors produce Gram matrix with condition number ~1/angle^2. "
                     "Projection computation suffers from catastrophic cancellation."
    },
    {
        "test_id": "FUNC_014",
        "category": "projection_non_closed",
        "input": {
            "description": "Projection onto kernel of nearly rank-deficient matrix",
            "matrix": "random 100x100 with smallest singular value 1e-14",
            "operation": "project_onto_kernel"
        },
        "expected": {
            "kernel_dimension": "effectively 0 or 1 depending on tolerance",
            "numerical_rank": "ambiguous at machine precision",
            "projection_sensitivity": "high"
        },
        "difficulty": "pathological",
        "rationale": "The kernel is numerically ambiguous when singular values approach machine epsilon. "
                     "Tests tolerance handling in kernel projection."
    },
    {
        "test_id": "FUNC_015",
        "category": "projection_non_closed",
        "input": {
            "description": "Projection onto graph of unbounded operator (finite approximation)",
            "operator": "differentiation operator D, domain H^1[0,1]",
            "discretization": "finite differences, n=200 grid points",
            "operation": "project_onto_graph"
        },
        "expected": {
            "graph_closure_issues": "graph not closed for unbounded D",
            "projection_may_fail": "depending on target vector",
            "domain_compatibility": "must check membership"
        },
        "difficulty": "extreme",
        "rationale": "Graphs of unbounded operators are not closed. Finite discretization hides this, "
                     "but projection may give misleading results."
    },

    # =========================================================================
    # CATEGORY 4: GRAM-SCHMIDT ON NEARLY LINEARLY DEPENDENT VECTORS (FUNC_016-020)
    # =========================================================================
    {
        "test_id": "FUNC_016",
        "category": "gram_schmidt_degenerate",
        "input": {
            "description": "Gram-Schmidt on [v, v + 1e-15*w, v + 2e-15*w, ...] for 20 vectors",
            "vectors": "v = [1,0,...,0], w = [0,1,0,...,0] in R^100",
            "perturbation": "1e-15 per vector increment",
            "operation": "gram_schmidt"
        },
        "expected": {
            "orthonormal_set_size": "1 or 2 depending on precision",
            "linear_dependence_detected": True,
            "numerical_rank": "between 1 and 20"
        },
        "difficulty": "pathological",
        "rationale": "Vectors differ by machine epsilon multiples. Classical Gram-Schmidt will fail; "
                     "modified Gram-Schmidt may partially succeed. Tests rank detection."
    },
    {
        "test_id": "FUNC_017",
        "category": "gram_schmidt_degenerate",
        "input": {
            "description": "Krylov basis [b, Ab, A^2b, ..., A^50b] for nearly defective A",
            "matrix_A": "Jordan block J_50(lambda=1) + 1e-10 * random perturbation",
            "starting_vector": "b = [1,1,...,1]/sqrt(50)",
            "operation": "gram_schmidt_krylov"
        },
        "expected": {
            "krylov_space_collapses": "after ~15-20 iterations due to floating point",
            "loss_of_orthogonality": "exponential growth",
            "reorthogonalization_required": True
        },
        "difficulty": "extreme",
        "rationale": "Krylov methods on nearly defective matrices suffer from breakdown. "
                     "The Krylov basis becomes nearly linearly dependent, destroying orthogonality."
    },
    {
        "test_id": "FUNC_018",
        "category": "gram_schmidt_degenerate",
        "input": {
            "description": "Fourier basis truncation with aliasing: sin(nx) for n=1..100 sampled at 101 points",
            "sampling_points": "uniform grid [0, 2*pi] with 101 points",
            "operation": "gram_schmidt_discrete_fourier"
        },
        "expected": {
            "aliasing_creates_dependence": "sin((n+101)x) = -sin(nx) at sample points",
            "orthogonality_approximate": "discrete inner product vs continuous differ",
            "gram_matrix_rank_deficiency": "possible at Nyquist frequency"
        },
        "difficulty": "brutal",
        "rationale": "Discrete sampling aliases high frequencies. Gram-Schmidt may produce spurious "
                     "dependencies or fail to detect true rank."
    },
    {
        "test_id": "FUNC_019",
        "category": "gram_schmidt_degenerate",
        "input": {
            "description": "Polynomial basis [1, x, x^2, ..., x^30] on [0,1] with uniform inner product",
            "inner_product": "integral from 0 to 1 of f*g dx (approximated)",
            "operation": "gram_schmidt_legendre"
        },
        "expected": {
            "hilbert_matrix_condition": "condition number ~ 10^20 for n=30",
            "orthogonalization_unstable": True,
            "should_produce_legendre": "P_0, P_1, ..., P_30 (scaled)"
        },
        "difficulty": "pathological",
        "rationale": "The Gram matrix is the infamous Hilbert matrix with exponentially growing condition number. "
                     "Gram-Schmidt on monomial basis is notoriously unstable beyond degree ~15."
    },
    {
        "test_id": "FUNC_020",
        "category": "gram_schmidt_degenerate",
        "input": {
            "description": "Complex exponentials with near-integer frequencies",
            "vectors": "[exp(2*pi*i*f_k*t) for f_k = k + 1e-12*k^2, k=0..49] at t=0,1,...,99",
            "operation": "gram_schmidt"
        },
        "expected": {
            "beat_frequency_interference": "near-integer frequencies create slow beats",
            "near_linear_dependence": True,
            "spectral_leakage": "DFT cannot resolve 1e-12 frequency differences"
        },
        "difficulty": "extreme",
        "rationale": "Frequencies differing by 1e-12 are indistinguishable over finite observation. "
                     "Tests ability to detect frequency-domain near-dependencies."
    },

    # =========================================================================
    # CATEGORY 5: SPECTRAL DECOMPOSITION OF NON-NORMAL OPERATORS (FUNC_021-025)
    # =========================================================================
    {
        "test_id": "FUNC_021",
        "category": "spectral_non_normal",
        "input": {
            "description": "Jordan block J_n(0) for n=50 (maximally non-diagonalizable)",
            "matrix": "strictly upper triangular 50x50 with 1s on superdiagonal",
            "operation": "spectral_decomposition"
        },
        "expected": {
            "eigenvalue": 0,
            "multiplicity_algebraic": 50,
            "multiplicity_geometric": 1,
            "diagonalizable": False,
            "spectral_decomposition_fails": "no eigenspaces, only generalized eigenspaces"
        },
        "difficulty": "brutal",
        "rationale": "Jordan blocks have no spectral decomposition in the usual sense. "
                     "Tests whether system correctly identifies non-diagonalizability."
    },
    {
        "test_id": "FUNC_022",
        "category": "spectral_non_normal",
        "input": {
            "description": "Companion matrix of Wilkinson polynomial p(x) = prod(x-k) for k=1..20",
            "polynomial_roots": "[1, 2, 3, ..., 20]",
            "matrix_type": "companion",
            "operation": "compute_spectrum"
        },
        "expected": {
            "true_eigenvalues": "[1, 2, ..., 20]",
            "computed_eigenvalues": "highly perturbed due to ill-conditioning",
            "eigenvalue_condition_numbers": "up to 10^14 for middle eigenvalues"
        },
        "difficulty": "pathological",
        "rationale": "Wilkinson polynomial eigenvalues are extremely sensitive. Companion matrix "
                     "amplifies this: tiny coefficient perturbations cause O(1) eigenvalue shifts."
    },
    {
        "test_id": "FUNC_023",
        "category": "spectral_non_normal",
        "input": {
            "description": "Kreiss matrix: diag([0.9^n for n=1..100]) + nilpotent N",
            "nilpotent_part": "strictly upper triangular with 1s",
            "operation": "compute_resolvent_norm_near_circle"
        },
        "expected": {
            "eigenvalues_inside_disk": True,
            "resolvent_norm_on_circle": "unbounded as n->infinity (transient growth)",
            "kreiss_constant": "large despite stability"
        },
        "difficulty": "extreme",
        "rationale": "Kreiss matrix is stable (eigenvalues in unit disk) but exhibits massive "
                     "transient growth. Resolvent norm near boundary reveals non-normality."
    },
    {
        "test_id": "FUNC_024",
        "category": "spectral_non_normal",
        "input": {
            "description": "Block upper triangular with identical diagonal blocks",
            "blocks": "[[1,1],[0,1]] repeated 25 times on diagonal, arbitrary upper blocks",
            "dimension": 50,
            "operation": "spectral_decomposition"
        },
        "expected": {
            "eigenvalue": 1,
            "algebraic_multiplicity": 50,
            "geometric_multiplicity": 25,
            "jordan_structure": "25 Jordan blocks of size 2"
        },
        "difficulty": "brutal",
        "rationale": "Repeated Jordan blocks test whether system detects block structure. "
                     "Standard eigensolvers may compute incorrect multiplicities."
    },
    {
        "test_id": "FUNC_025",
        "category": "spectral_non_normal",
        "input": {
            "description": "Orr-Sommerfeld discretization (convection-diffusion)",
            "reynolds_number": 10000,
            "discretization_points": 100,
            "operation": "compute_pseudospectrum"
        },
        "expected": {
            "eigenvalues_stable": True,
            "pseudospectrum_extends_far": "epsilon-pseudospectrum extends into RHP",
            "transient_amplification": "can be O(Re^3)"
        },
        "difficulty": "pathological",
        "rationale": "Orr-Sommerfeld is the canonical example of pseudospectral instability. "
                     "Eigenvalues are stable but system exhibits huge transient growth."
    },

    # =========================================================================
    # CATEGORY 6: RESOLVENT COMPUTATION NEAR SPECTRUM (FUNC_026-030)
    # =========================================================================
    {
        "test_id": "FUNC_026",
        "category": "resolvent_near_spectrum",
        "input": {
            "description": "Resolvent at z = lambda + 1e-14 where lambda is simple eigenvalue",
            "matrix": "diag([1, 2, 3, 4, 5])",
            "z_value": "3 + 1e-14",
            "operation": "compute_resolvent"
        },
        "expected": {
            "resolvent_norm": "~1e14",
            "numerical_instability": "severe",
            "eigenvalue_detection": "z is effectively in spectrum"
        },
        "difficulty": "pathological",
        "rationale": "Resolvent norm blows up as 1/dist(z, spectrum). At machine epsilon distance, "
                     "computation becomes meaningless."
    },
    {
        "test_id": "FUNC_027",
        "category": "resolvent_near_spectrum",
        "input": {
            "description": "Resolvent of defective matrix at eigenvalue plus epsilon",
            "matrix": "Jordan block J_10(1)",
            "z_value": "1 + 1e-8",
            "operation": "compute_resolvent"
        },
        "expected": {
            "resolvent_norm": "~1e80 (grows as 1/epsilon^n for n-block)",
            "polynomial_growth": True,
            "resolvent_formula": "(zI - J)^(-1) has entries 1/(z-1)^k"
        },
        "difficulty": "pathological",
        "rationale": "Near defective eigenvalue, resolvent norm grows as 1/epsilon^(block_size). "
                     "For size-10 block at epsilon=1e-8, norm is astronomical."
    },
    {
        "test_id": "FUNC_028",
        "category": "resolvent_near_spectrum",
        "input": {
            "description": "Resolvent identity verification at nearly singular points",
            "matrix": "random 20x20 normal matrix",
            "z1": "closest eigenvalue + 1e-10",
            "z2": "closest eigenvalue + 2e-10",
            "operation": "verify_resolvent_identity"
        },
        "expected": {
            "first_resolvent_identity": "R(z1) - R(z2) = (z2-z1)*R(z1)*R(z2)",
            "numerical_verification": "may fail due to cancellation",
            "error_amplification": "product of nearly singular resolvents"
        },
        "difficulty": "extreme",
        "rationale": "Resolvent identity involves product of nearly singular operators. "
                     "Numerical verification requires careful scaling to avoid overflow."
    },
    {
        "test_id": "FUNC_029",
        "category": "resolvent_near_spectrum",
        "input": {
            "description": "Contour integral of resolvent (Riesz projection)",
            "matrix": "block diagonal with eigenvalues 0, 1, 2 having multiplicities 3, 2, 1",
            "contour": "circle of radius 0.5 centered at eigenvalue 1",
            "operation": "compute_riesz_projection"
        },
        "expected": {
            "projection_rank": 2,
            "projection_onto": "eigenspace of lambda=1",
            "contour_integral_formula": "P = (1/2*pi*i) * integral(R(z) dz)"
        },
        "difficulty": "brutal",
        "rationale": "Riesz projection via contour integral tests resolvent computation at multiple points. "
                     "Quadrature errors accumulate; projection may lose rank or idempotence."
    },
    {
        "test_id": "FUNC_030",
        "category": "resolvent_near_spectrum",
        "input": {
            "description": "Resolvent of banded Toeplitz matrix near essential spectrum boundary",
            "symbol": "f(z) = z + 1/z (essential spectrum is [-2, 2])",
            "z_value": "2 + 1e-6",
            "dimension": 200,
            "operation": "compute_resolvent"
        },
        "expected": {
            "resolvent_norm": "grows as n for z near essential spectrum",
            "finite_section_instability": True,
            "szego_limit_applies": "for determinants"
        },
        "difficulty": "extreme",
        "rationale": "Near essential spectrum of Toeplitz, resolvent norm grows with matrix size. "
                     "Tests handling of spectral pollution in finite approximations."
    },

    # =========================================================================
    # CATEGORY 7: FUNCTIONAL CALCULUS WITH DISCONTINUOUS FUNCTIONS (FUNC_031-035)
    # =========================================================================
    {
        "test_id": "FUNC_031",
        "category": "functional_calculus_discontinuous",
        "input": {
            "description": "Heaviside step function applied to matrix with eigenvalue at jump",
            "matrix": "diag([-1, -0.5, 0, 0.5, 1])",
            "function": "H(x) = 0 if x < 0, 1 if x >= 0",
            "operation": "apply_function"
        },
        "expected": {
            "f_A": "diag([0, 0, 1, 1, 1])",
            "ambiguity_at_zero": "H(0) is convention-dependent",
            "borel_functional_calculus": "requires spectral measure"
        },
        "difficulty": "brutal",
        "rationale": "Step function applied to self-adjoint matrix requires spectral projection. "
                     "Ambiguity at discontinuity tests convention handling."
    },
    {
        "test_id": "FUNC_032",
        "category": "functional_calculus_discontinuous",
        "input": {
            "description": "Sign function on matrix with eigenvalue cluster near zero",
            "matrix": "diag([1e-15, 1e-14, 1e-13, 0.1, 0.2, 0.3])",
            "function": "sign(x) = x/|x| for x != 0",
            "operation": "apply_function"
        },
        "expected": {
            "sign_matrix": "diag([1, 1, 1, 1, 1, 1])",
            "numerical_instability": "eigenvalues near zero cause sign(A) instability",
            "polar_decomposition_connection": "A = |A| * sign(A)"
        },
        "difficulty": "pathological",
        "rationale": "Sign function is discontinuous at 0. Eigenvalues at 1e-15 are indistinguishable "
                     "from zero numerically, making sign(A) computation unstable."
    },
    {
        "test_id": "FUNC_033",
        "category": "functional_calculus_discontinuous",
        "input": {
            "description": "Characteristic function of interval applied to non-normal matrix",
            "matrix": "random 20x20 non-normal matrix",
            "function": "chi_{[0,1]}(x) = 1 if x in [0,1], 0 otherwise",
            "operation": "apply_function"
        },
        "expected": {
            "spectral_calculus_fails": "f(A) undefined for non-normal A and non-polynomial f",
            "error_expected": True,
            "alternative": "would need holomorphic functional calculus extension"
        },
        "difficulty": "extreme",
        "rationale": "Functional calculus for non-normal operators requires holomorphic functions. "
                     "Characteristic functions are not holomorphic; operation should fail or warn."
    },
    {
        "test_id": "FUNC_034",
        "category": "functional_calculus_discontinuous",
        "input": {
            "description": "Floor function applied to matrix",
            "matrix": "diag([0.1, 0.9, 1.1, 1.9, 2.1])",
            "function": "floor(x) = largest integer <= x",
            "operation": "apply_function"
        },
        "expected": {
            "floor_A": "diag([0, 0, 1, 1, 2])",
            "integer_eigenvalues_problematic": "floor(1.0) vs floor(0.9999...99)",
            "numerical_ambiguity": "at integer boundaries"
        },
        "difficulty": "brutal",
        "rationale": "Floor function has infinitely many discontinuities. Near integers, floating-point "
                     "representation ambiguity makes floor(A) ill-defined."
    },
    {
        "test_id": "FUNC_035",
        "category": "functional_calculus_discontinuous",
        "input": {
            "description": "Dirichlet function (1 on rationals, 0 on irrationals) on matrix",
            "matrix": "diag([1, sqrt(2), 2, pi, e])",
            "function": "D(x) = 1 if x rational, 0 if x irrational",
            "operation": "apply_function"
        },
        "expected": {
            "D_A": "diag([1, 0, 1, 0, 0])",
            "unmeasurable_function": "D is not Borel measurable",
            "spectral_theorem_inapplicable": "D(A) is not definable via spectral theorem"
        },
        "difficulty": "pathological",
        "rationale": "Dirichlet function is nowhere continuous and not measurable. No functional calculus "
                     "can handle it. Tests whether system recognizes inadmissible functions."
    },

    # =========================================================================
    # CATEGORY 8: POLAR DECOMPOSITION OF RANK-DEFICIENT OPERATORS (FUNC_036-040)
    # =========================================================================
    {
        "test_id": "FUNC_036",
        "category": "polar_decomposition_degenerate",
        "input": {
            "description": "Polar decomposition of zero matrix",
            "matrix": "np.zeros((10, 10))",
            "operation": "polar_decomposition"
        },
        "expected": {
            "U": "any unitary (non-unique)",
            "P": "zero matrix",
            "uniqueness_failure": "U is completely arbitrary for A=0"
        },
        "difficulty": "brutal",
        "rationale": "Zero matrix has polar decomposition 0 = U * 0 for any unitary U. "
                     "Tests handling of complete degeneracy."
    },
    {
        "test_id": "FUNC_037",
        "category": "polar_decomposition_degenerate",
        "input": {
            "description": "Polar decomposition of rank-1 matrix",
            "matrix": "np.outer([1,2,3,4,5], [5,4,3,2,1])",
            "operation": "polar_decomposition"
        },
        "expected": {
            "U": "partial isometry of rank 1",
            "P": "rank-1 positive semidefinite",
            "kernel_handling": "U maps kernel of A to kernel of A"
        },
        "difficulty": "extreme",
        "rationale": "Rank-1 matrices have unique U only on image(A*). Tests whether polar decomposition "
                     "correctly handles large kernel."
    },
    {
        "test_id": "FUNC_038",
        "category": "polar_decomposition_degenerate",
        "input": {
            "description": "Polar decomposition with singular value at machine epsilon",
            "matrix": "U_0 @ diag([1, 0.5, 1e-16, 0, 0]) @ V_0.T for random unitary U_0, V_0",
            "operation": "polar_decomposition"
        },
        "expected": {
            "numerical_rank": "2 or 3 depending on tolerance",
            "U_depends_on_tolerance": True,
            "P_condition_number": "infinite (singular)"
        },
        "difficulty": "pathological",
        "rationale": "Singular value at machine epsilon makes rank ambiguous. Polar factor U depends "
                     "on whether 1e-16 is treated as zero or nonzero."
    },
    {
        "test_id": "FUNC_039",
        "category": "polar_decomposition_degenerate",
        "input": {
            "description": "Polar decomposition of rectangular matrix 10x5",
            "matrix": "np.random.randn(10, 5)",
            "operation": "polar_decomposition"
        },
        "expected": {
            "U": "partial isometry (10x5)",
            "P": "5x5 positive definite (generically)",
            "left_vs_right": "A = UP (right) vs A = PU (left)"
        },
        "difficulty": "brutal",
        "rationale": "Rectangular matrices have non-square polar factors. Tests whether implementation "
                     "handles dimension mismatch correctly."
    },
    {
        "test_id": "FUNC_040",
        "category": "polar_decomposition_degenerate",
        "input": {
            "description": "Polar decomposition of skew-symmetric matrix",
            "matrix": "A where A = -A.T (5x5 random skew-symmetric)",
            "operation": "polar_decomposition"
        },
        "expected": {
            "P": "sqrt(A.T @ A) = sqrt(-A @ A)",
            "U": "orthogonal (not symmetric)",
            "eigenvalues_of_A": "purely imaginary or zero",
            "special_structure": "U has determinant +1 or -1"
        },
        "difficulty": "extreme",
        "rationale": "Skew-symmetric matrices have purely imaginary eigenvalues. Polar decomposition "
                     "reveals special structure that generic algorithms might miss."
    },

    # =========================================================================
    # CATEGORY 9: NUMERICAL RANGE OF NILPOTENT MATRICES (FUNC_041-045)
    # =========================================================================
    {
        "test_id": "FUNC_041",
        "category": "numerical_range_nilpotent",
        "input": {
            "description": "Numerical range of 2x2 nilpotent [[0,1],[0,0]]",
            "matrix": "[[0, 1], [0, 0]]",
            "operation": "compute_numerical_range"
        },
        "expected": {
            "numerical_range": "disk of radius 1/2 centered at 0",
            "boundary": "ellipse degenerating to circle for nilpotent",
            "spectrum": "{0} is subset of W(A)"
        },
        "difficulty": "brutal",
        "rationale": "2x2 nilpotent has circular numerical range. Tests whether numerical range "
                     "computation produces correct convex set."
    },
    {
        "test_id": "FUNC_042",
        "category": "numerical_range_nilpotent",
        "input": {
            "description": "Numerical range of Jordan block J_n(0) for n=10",
            "matrix": "upper shift matrix 10x10",
            "operation": "compute_numerical_range"
        },
        "expected": {
            "numerical_range": "disk of radius cos(pi/(n+1))",
            "haagerup_formula": "r = cos(pi/(n+1)) for W(J_n(0))",
            "boundary_sampling_difficult": True
        },
        "difficulty": "extreme",
        "rationale": "Numerical range radius for nilpotent Jordan block follows Haagerup's formula. "
                     "Random sampling may miss boundary; tests geometric characterization."
    },
    {
        "test_id": "FUNC_043",
        "category": "numerical_range_nilpotent",
        "input": {
            "description": "Numerical range of nilpotent with very small non-zero element",
            "matrix": "J_5(0) + 1e-15 * E_{5,1} (perturbation breaks nilpotency)",
            "operation": "compute_numerical_range"
        },
        "expected": {
            "eigenvalues": "five 5th roots of 1e-15",
            "spectral_radius": "~0.001 (5th root of 1e-15)",
            "numerical_range_expands": "W(A) may expand slightly due to perturbation"
        },
        "difficulty": "pathological",
        "rationale": "Infinitesimal perturbation creates 5 distinct eigenvalues. Tests sensitivity "
                     "of numerical range to tiny structural changes."
    },
    {
        "test_id": "FUNC_044",
        "category": "numerical_range_nilpotent",
        "input": {
            "description": "Numerical range of direct sum of nilpotents",
            "matrix": "block_diag(J_3(0), J_4(0), J_5(0))",
            "operation": "compute_numerical_range"
        },
        "expected": {
            "numerical_range": "convex hull of individual ranges",
            "largest_block_dominates": "radius from 5x5 block = cos(pi/6)",
            "convexity_test": True
        },
        "difficulty": "brutal",
        "rationale": "Direct sum numerical range is convex hull of parts. Tests whether implementation "
                     "recognizes block structure and applies hull correctly."
    },
    {
        "test_id": "FUNC_045",
        "category": "numerical_range_nilpotent",
        "input": {
            "description": "q-numerical range W_q(A) for nilpotent A and q close to 1",
            "matrix": "J_4(0)",
            "q_value": 0.99,
            "operation": "compute_q_numerical_range"
        },
        "expected": {
            "c_numerical_range": "generalization for q in (0,1]",
            "W_1_equals_W": "W_1(A) = W(A)",
            "W_q_shrinks_for_small_q": True
        },
        "difficulty": "extreme",
        "rationale": "C-numerical range W_q(A) = {<Ax,y>: ||x||=||y||=1, <x,y>=q} generalizes numerical range. "
                     "Tests advanced functional analysis concepts."
    },

    # =========================================================================
    # CATEGORY 10: RIESZ REPRESENTATION FOR DISCONTINUOUS FUNCTIONALS (FUNC_046-050)
    # =========================================================================
    {
        "test_id": "FUNC_046",
        "category": "riesz_discontinuous",
        "input": {
            "description": "Riesz representation of point evaluation delta_0 on H^1[0,1]",
            "space": "Sobolev space H^1[0,1]",
            "functional": "f(u) = u(0)",
            "operation": "riesz_representation"
        },
        "expected": {
            "representer_exists": True,  # H^1 embeds continuously into C[0,1]
            "representer": "Green's function-like element",
            "unbounded_on_L2": "delta_0 is unbounded on L^2"
        },
        "difficulty": "brutal",
        "rationale": "Point evaluation is bounded on H^1 (Sobolev embedding) but unbounded on L^2. "
                     "Tests whether system recognizes space-dependent boundedness."
    },
    {
        "test_id": "FUNC_047",
        "category": "riesz_discontinuous",
        "input": {
            "description": "Riesz representation of delta functional on finite-dim approximation",
            "space": "R^1000 with weighted inner product approximating L^2[0,1]",
            "functional": "f(u) = u[500] (point evaluation at midpoint)",
            "operation": "riesz_representation"
        },
        "expected": {
            "representer": "standard basis vector e_500 (scaled)",
            "norm_grows_with_dimension": "||representer|| ~ sqrt(n) for delta-like",
            "convergence_fails": "discrete representers don't converge in L^2"
        },
        "difficulty": "extreme",
        "rationale": "In finite dimension, all functionals have Riesz representation. But as dimension "
                     "increases, delta-like representers have unbounded norm, revealing L^2 unboundedness."
    },
    {
        "test_id": "FUNC_048",
        "category": "riesz_discontinuous",
        "input": {
            "description": "Riesz representation for functional defined only on dense subspace",
            "space": "l^2 (Hilbert space)",
            "functional": "f: c_00 -> R defined by f(x) = sum(x_n) (unbounded extension)",
            "operation": "riesz_representation"
        },
        "expected": {
            "no_bounded_extension": "f unbounded on l^2",
            "riesz_fails": "no y in l^2 with f(x) = <x,y>",
            "unboundedness_witness": "x = (1, 1/2, 1/3, ..., 1/n, 0, 0, ...)"
        },
        "difficulty": "pathological",
        "rationale": "sum(x_n) is bounded on finite sequences but unbounded on l^2. No Riesz representer "
                     "exists. Tests whether system detects unboundedness."
    },
    {
        "test_id": "FUNC_049",
        "category": "riesz_discontinuous",
        "input": {
            "description": "Hahn-Banach extension of bounded functional on subspace",
            "space": "R^100",
            "subspace": "span of first 10 basis vectors",
            "functional_on_subspace": "f(x) = sum(x_i) for i=1..10",
            "operation": "hahn_banach_extend"
        },
        "expected": {
            "extension_exists": True,
            "extension_not_unique": "in Hilbert space, unique via orthogonal projection",
            "norm_preserving": "||F|| = ||f|| for minimal extension"
        },
        "difficulty": "brutal",
        "rationale": "Hahn-Banach guarantees extension but not uniqueness (except in Hilbert spaces). "
                     "Tests whether system computes correct Hilbert space extension."
    },
    {
        "test_id": "FUNC_050",
        "category": "riesz_discontinuous",
        "input": {
            "description": "Riesz representation with numerically singular Gram matrix",
            "space": "R^50 with inner product from nearly singular positive matrix",
            "gram_matrix": "random positive definite with condition number 1e16",
            "functional": "random linear functional",
            "operation": "riesz_representation"
        },
        "expected": {
            "representer_computation_unstable": True,
            "system_to_solve": "Gy = c where G has cond(G) = 1e16",
            "numerical_error": "~1e-16 * 1e16 = O(1) relative error"
        },
        "difficulty": "pathological",
        "rationale": "Riesz representation requires solving system with Gram matrix. At condition number "
                     "1e16, backward error equals forward error, making result meaningless."
    }
]


# =============================================================================
# HELPER FUNCTIONS FOR TEST EXECUTION
# =============================================================================

def get_test_by_id(test_id: str) -> Dict[str, Any]:
    """Retrieve a specific test by its ID."""
    for test in FUNCTIONAL_ANALYSIS_STRESS_TESTS:
        if test["test_id"] == test_id:
            return test
    raise ValueError(f"Test {test_id} not found")


def get_tests_by_category(category: str) -> List[Dict[str, Any]]:
    """Retrieve all tests in a category."""
    return [t for t in FUNCTIONAL_ANALYSIS_STRESS_TESTS if t["category"] == category]


def get_tests_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """Retrieve all tests of a given difficulty level."""
    return [t for t in FUNCTIONAL_ANALYSIS_STRESS_TESTS if t["difficulty"] == difficulty]


def get_category_summary() -> Dict[str, int]:
    """Get count of tests per category."""
    categories = {}
    for test in FUNCTIONAL_ANALYSIS_STRESS_TESTS:
        cat = test["category"]
        categories[cat] = categories.get(cat, 0) + 1
    return categories


def get_difficulty_summary() -> Dict[str, int]:
    """Get count of tests per difficulty."""
    difficulties = {}
    for test in FUNCTIONAL_ANALYSIS_STRESS_TESTS:
        diff = test["difficulty"]
        difficulties[diff] = difficulties.get(diff, 0) + 1
    return difficulties


# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("FUNCTIONAL ANALYSIS BRUTAL STRESS TESTS - SUMMARY")
    print("=" * 80)
    print(f"\nTotal tests: {len(FUNCTIONAL_ANALYSIS_STRESS_TESTS)}")

    print("\n--- Tests by Category ---")
    for cat, count in sorted(get_category_summary().items()):
        print(f"  {cat}: {count}")

    print("\n--- Tests by Difficulty ---")
    for diff, count in sorted(get_difficulty_summary().items()):
        print(f"  {diff}: {count}")

    print("\n--- Test IDs ---")
    for test in FUNCTIONAL_ANALYSIS_STRESS_TESTS:
        print(f"  {test['test_id']}: {test['category']} [{test['difficulty']}]")
