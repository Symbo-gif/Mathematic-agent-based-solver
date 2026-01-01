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
BRUTAL LINEAR ALGEBRA STRESS TESTS
==================================

50 research-level stress tests designed to BREAK the Linear Algebra domain:
- MatrixOperationsSpecialist
- DecompositionSpecialist
- VectorSpaceAnalyst
- TensorOperationsAgent
- AdvancedMatrixSpecialist

Categories:
-----------
1. Near-singular matrices (condition number > 10^15)
2. Large sparse matrices with specific eigenvalue distributions
3. Jordan blocks with repeated eigenvalues
4. SVD of rank-deficient matrices
5. QR decomposition of nearly parallel column vectors
6. Matrix exponentials of non-diagonalizable matrices
7. Pseudoinverse of matrices with clustered singular values
8. Tensor contractions in high dimensions
9. Eigenvalue problems with defective matrices
10. Schur decomposition edge cases

Each test includes:
- test_id: Unique identifier
- category: Classification of the test type
- input: Mathematical input specification
- expected: Expected result or behavior
- difficulty: brutal/extreme/pathological
- rationale: Why this test is particularly challenging
"""

import math

# =============================================================================
# BRUTAL LINEAR ALGEBRA STRESS TESTS
# =============================================================================

BRUTAL_LINALG_TESTS = [
    # =========================================================================
    # CATEGORY 1: NEAR-SINGULAR MATRICES (Condition Number > 10^15)
    # =========================================================================
    {
        "test_id": "LINALG_001",
        "category": "near_singular",
        "input": {
            "operation": "solve_system",
            "matrix": "Hilbert(15)",  # 15x15 Hilbert matrix
            "description": "Solve Ax=b for 15x15 Hilbert matrix with b=[1,1,...,1]"
        },
        "expected": "Solution with numerical instability detection, condition number ~10^17",
        "difficulty": "brutal",
        "rationale": "Hilbert matrices are notoriously ill-conditioned. The 15x15 Hilbert matrix has condition number ~10^17, causing catastrophic loss of precision in naive solvers."
    },
    {
        "test_id": "LINALG_002",
        "category": "near_singular",
        "input": {
            "operation": "inverse",
            "matrix": "[[1, 1-1e-16], [1+1e-16, 1]]",
            "description": "Invert a 2x2 matrix with determinant ~10^-16"
        },
        "expected": "Singular or near-singular warning, inverse elements ~10^16",
        "difficulty": "extreme",
        "rationale": "Determinant is at machine epsilon level. Standard inversion will produce garbage or overflow."
    },
    {
        "test_id": "LINALG_003",
        "category": "near_singular",
        "input": {
            "operation": "determinant",
            "matrix": "Vandermonde([1, 1+1e-14, 1+2e-14, 1+3e-14, 1+4e-14])",
            "description": "Compute determinant of Vandermonde matrix with near-identical nodes"
        },
        "expected": "Determinant ~10^-56, should detect near-singularity",
        "difficulty": "pathological",
        "rationale": "Vandermonde matrices become extremely ill-conditioned when nodes are close. This tests detection of catastrophic cancellation."
    },
    {
        "test_id": "LINALG_004",
        "category": "near_singular",
        "input": {
            "operation": "solve_system",
            "matrix": "[[1e-20, 1], [1, 1e-20]]",
            "description": "Solve system with extreme scaling imbalance"
        },
        "expected": "Correct solution with appropriate pivoting, or scaling warning",
        "difficulty": "brutal",
        "rationale": "Without proper pivoting and scaling, this system produces completely wrong answers due to underflow/overflow mixing."
    },
    {
        "test_id": "LINALG_005",
        "category": "near_singular",
        "input": {
            "operation": "condition_number",
            "matrix": "Cauchy(n=20)",  # Cauchy matrix 1/(i+j-1)
            "description": "Compute condition number of 20x20 Cauchy matrix"
        },
        "expected": "Condition number ~10^18, should handle without overflow",
        "difficulty": "extreme",
        "rationale": "Cauchy matrices are among the most ill-conditioned structured matrices. Tests handling of extreme condition numbers."
    },

    # =========================================================================
    # CATEGORY 2: LARGE SPARSE MATRICES WITH SPECIFIC EIGENVALUE DISTRIBUTIONS
    # =========================================================================
    {
        "test_id": "LINALG_006",
        "category": "sparse_eigenvalue",
        "input": {
            "operation": "eigenvalues",
            "matrix": "Sparse_Tridiagonal(1000, [-1, 2, -1])",
            "description": "Find eigenvalues of 1000x1000 tridiagonal discrete Laplacian"
        },
        "expected": "Eigenvalues = 4*sin^2(k*pi/(2*(n+1))) for k=1..n",
        "difficulty": "brutal",
        "rationale": "Large sparse matrix requiring efficient eigenvalue algorithms. Direct methods will time out or run out of memory."
    },
    {
        "test_id": "LINALG_007",
        "category": "sparse_eigenvalue",
        "input": {
            "operation": "eigenvalues",
            "matrix": "Random_Sparse(1000, density=0.01, eigenvalue_range=[0.001, 1000])",
            "description": "Find eigenvalues of sparse matrix with 6-order magnitude eigenvalue spread"
        },
        "expected": "All eigenvalues detected including small ones near threshold",
        "difficulty": "extreme",
        "rationale": "Wide eigenvalue spread causes iterative methods to converge very slowly for small eigenvalues while large ones dominate."
    },
    {
        "test_id": "LINALG_008",
        "category": "sparse_eigenvalue",
        "input": {
            "operation": "eigenvalues",
            "matrix": "Companion(polynomial_degree=50)",
            "description": "Find eigenvalues of 50x50 companion matrix (polynomial roots)"
        },
        "expected": "Roots of degree-50 polynomial with high accuracy",
        "difficulty": "brutal",
        "rationale": "Companion matrices are notoriously ill-conditioned for root-finding. Small perturbations cause large eigenvalue changes."
    },
    {
        "test_id": "LINALG_009",
        "category": "sparse_eigenvalue",
        "input": {
            "operation": "spectral_radius",
            "matrix": "PageRank_Graph(nodes=10000, edges=100000)",
            "description": "Compute spectral radius of web graph adjacency matrix"
        },
        "expected": "Spectral radius with power iteration or Arnoldi",
        "difficulty": "extreme",
        "rationale": "Real-world graph matrices are large, sparse, and non-symmetric. Tests scalability of eigenvalue algorithms."
    },
    {
        "test_id": "LINALG_010",
        "category": "sparse_eigenvalue",
        "input": {
            "operation": "smallest_eigenvalue",
            "matrix": "Stiffness_Matrix(FEM_mesh_size=100)",
            "description": "Find smallest eigenvalue of FEM stiffness matrix"
        },
        "expected": "Smallest eigenvalue via shift-invert or deflation",
        "difficulty": "pathological",
        "rationale": "FEM matrices have eigenvalues spanning many orders of magnitude. Finding the smallest is an inverse problem."
    },

    # =========================================================================
    # CATEGORY 3: JORDAN BLOCKS WITH REPEATED EIGENVALUES
    # =========================================================================
    {
        "test_id": "LINALG_011",
        "category": "jordan_blocks",
        "input": {
            "operation": "jordan_form",
            "matrix": "[[5, 1, 0, 0], [0, 5, 1, 0], [0, 0, 5, 1], [0, 0, 0, 5]]",
            "description": "Find Jordan form of 4x4 Jordan block with eigenvalue 5"
        },
        "expected": "Single 4x4 Jordan block with eigenvalue 5",
        "difficulty": "brutal",
        "rationale": "Pure Jordan block is the canonical example but requires correct chain construction."
    },
    {
        "test_id": "LINALG_012",
        "category": "jordan_blocks",
        "input": {
            "operation": "jordan_form",
            "matrix": "Perturbed_Jordan(4, eigenvalue=3, perturbation=1e-10)",
            "description": "Find Jordan form of perturbed Jordan block"
        },
        "expected": "Should detect near-degeneracy and return approximate Jordan structure",
        "difficulty": "extreme",
        "rationale": "Perturbation at machine epsilon level breaks theoretical Jordan structure. Tests numerical Jordan form computation."
    },
    {
        "test_id": "LINALG_013",
        "category": "jordan_blocks",
        "input": {
            "operation": "matrix_power",
            "matrix": "[[2, 1, 0], [0, 2, 1], [0, 0, 2]]",
            "power": 100,
            "description": "Compute A^100 for 3x3 Jordan block"
        },
        "expected": "A^n uses binomial expansion: J^n has entries involving C(n,k)*lambda^(n-k)",
        "difficulty": "brutal",
        "rationale": "Jordan blocks require special handling for matrix powers. Naive eigendecomposition fails."
    },
    {
        "test_id": "LINALG_014",
        "category": "jordan_blocks",
        "input": {
            "operation": "matrix_exp",
            "matrix": "[[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]]",
            "description": "Compute matrix exponential of nilpotent 4x4 matrix"
        },
        "expected": "e^N = I + N + N^2/2! + N^3/3! (finite sum for nilpotent)",
        "difficulty": "brutal",
        "rationale": "Nilpotent matrices are non-diagonalizable. Standard exp(diag) approach fails completely."
    },
    {
        "test_id": "LINALG_015",
        "category": "jordan_blocks",
        "input": {
            "operation": "jordan_form",
            "matrix": "Block_Diagonal([Jordan(2,3), Jordan(3,3), Jordan(2,3)])",
            "description": "Find Jordan form with multiple blocks of same eigenvalue"
        },
        "expected": "Three Jordan blocks: two 2x2 and one 3x3, all with eigenvalue 3",
        "difficulty": "extreme",
        "rationale": "Multiple Jordan blocks with same eigenvalue require careful dimension counting and chain construction."
    },

    # =========================================================================
    # CATEGORY 4: SVD OF RANK-DEFICIENT MATRICES
    # =========================================================================
    {
        "test_id": "LINALG_016",
        "category": "svd_rank_deficient",
        "input": {
            "operation": "svd",
            "matrix": "[[1, 2, 3], [2, 4, 6], [3, 6, 9]]",
            "description": "SVD of rank-1 matrix (outer product)"
        },
        "expected": "Only one non-zero singular value, rank=1",
        "difficulty": "brutal",
        "rationale": "Rank-deficient matrices produce zero singular values that must be handled correctly."
    },
    {
        "test_id": "LINALG_017",
        "category": "svd_rank_deficient",
        "input": {
            "operation": "svd",
            "matrix": "Random(100, 100) with rank=10 (sum of 10 rank-1 matrices)",
            "description": "SVD of 100x100 matrix with numerical rank 10"
        },
        "expected": "Exactly 10 significant singular values, 90 near-zero",
        "difficulty": "extreme",
        "rationale": "Numerical rank detection requires appropriate threshold selection. Tests truncated SVD implementation."
    },
    {
        "test_id": "LINALG_018",
        "category": "svd_rank_deficient",
        "input": {
            "operation": "svd",
            "matrix": "Tall_Skinny(1000, 10) with condition 10^12",
            "description": "SVD of tall matrix with extreme condition number"
        },
        "expected": "10 singular values spanning 12 orders of magnitude",
        "difficulty": "pathological",
        "rationale": "Tall matrices with poor conditioning stress both memory and numerical precision."
    },
    {
        "test_id": "LINALG_019",
        "category": "svd_rank_deficient",
        "input": {
            "operation": "truncated_svd",
            "matrix": "Noisy_Low_Rank(500, 500, true_rank=5, noise=1e-8)",
            "description": "Truncated SVD with optimal rank determination"
        },
        "expected": "Automatically determine rank=5 despite noise, reconstruct clean matrix",
        "difficulty": "extreme",
        "rationale": "Noise-contaminated low-rank matrices require careful gap detection in singular value spectrum."
    },
    {
        "test_id": "LINALG_020",
        "category": "svd_rank_deficient",
        "input": {
            "operation": "svd",
            "matrix": "[[1e-300, 0], [0, 1e300]]",
            "description": "SVD with extreme scaling (underflow/overflow regime)"
        },
        "expected": "Singular values 1e-300 and 1e300 without overflow/underflow errors",
        "difficulty": "pathological",
        "rationale": "Tests handling of floating-point extremes in decomposition algorithms."
    },

    # =========================================================================
    # CATEGORY 5: QR DECOMPOSITION OF NEARLY PARALLEL COLUMN VECTORS
    # =========================================================================
    {
        "test_id": "LINALG_021",
        "category": "qr_parallel_vectors",
        "input": {
            "operation": "qr",
            "matrix": "[[1, 1+1e-15], [1, 1+1e-15], [1, 1+1e-15]]",
            "description": "QR of matrix with nearly parallel columns (angle < 10^-15 radians)"
        },
        "expected": "Q should be orthogonal to machine precision, R nearly singular",
        "difficulty": "extreme",
        "rationale": "Classical Gram-Schmidt fails catastrophically. Tests modified GS or Householder implementation."
    },
    {
        "test_id": "LINALG_022",
        "category": "qr_parallel_vectors",
        "input": {
            "operation": "qr",
            "matrix": "Columns_Approaching_Parallel(10, angle=1e-12)",
            "description": "QR of 10 columns with pairwise angles ~10^-12"
        },
        "expected": "Loss of orthogonality detected, reorthogonalization applied",
        "difficulty": "pathological",
        "rationale": "Multiple nearly-parallel columns cause cascading loss of orthogonality."
    },
    {
        "test_id": "LINALG_023",
        "category": "qr_parallel_vectors",
        "input": {
            "operation": "qr_with_pivoting",
            "matrix": "Rank_Deficient_Columns(100, 50, rank=30)",
            "description": "QR with column pivoting for rank-deficient matrix"
        },
        "expected": "Reveal numerical rank via R diagonal, permutation matrix P",
        "difficulty": "brutal",
        "rationale": "Column pivoting QR (QRCP) must correctly identify rank and null space basis."
    },
    {
        "test_id": "LINALG_024",
        "category": "qr_parallel_vectors",
        "input": {
            "operation": "householder_qr",
            "matrix": "Kahan_Matrix(50, c=0.99999)",
            "description": "QR of Kahan matrix designed to defeat Householder"
        },
        "expected": "Loss of orthogonality warning, fallback to iterative refinement",
        "difficulty": "pathological",
        "rationale": "Kahan matrix is specifically constructed to cause maximal orthogonality loss in Householder QR."
    },
    {
        "test_id": "LINALG_025",
        "category": "qr_parallel_vectors",
        "input": {
            "operation": "least_squares",
            "matrix": "Vandermonde(100_points, degree=15)",
            "b": "noisy_polynomial_values",
            "description": "Solve overdetermined system via QR for polynomial fitting"
        },
        "expected": "Stable least-squares solution despite Vandermonde conditioning",
        "difficulty": "extreme",
        "rationale": "Vandermonde least-squares is notoriously ill-conditioned. QR must provide stable solution."
    },

    # =========================================================================
    # CATEGORY 6: MATRIX EXPONENTIALS OF NON-DIAGONALIZABLE MATRICES
    # =========================================================================
    {
        "test_id": "LINALG_026",
        "category": "matrix_exp_non_diag",
        "input": {
            "operation": "matrix_exp",
            "matrix": "[[1, 1], [0, 1]]",
            "description": "Matrix exponential of simplest defective matrix"
        },
        "expected": "e^A = e * [[1, 1], [0, 1]]",
        "difficulty": "brutal",
        "rationale": "Non-diagonalizable matrix requires Jordan form or Pade approximation."
    },
    {
        "test_id": "LINALG_027",
        "category": "matrix_exp_non_diag",
        "input": {
            "operation": "matrix_exp",
            "matrix": "[[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1]]",
            "description": "Matrix exponential of 4x4 Jordan block"
        },
        "expected": "e * [[1, 1, 1/2, 1/6], [0, 1, 1, 1/2], [0, 0, 1, 1], [0, 0, 0, 1]]",
        "difficulty": "extreme",
        "rationale": "Larger Jordan blocks require correct application of exponential series on nilpotent part."
    },
    {
        "test_id": "LINALG_028",
        "category": "matrix_exp_non_diag",
        "input": {
            "operation": "matrix_exp",
            "matrix": "Stiff_ODE_Matrix(100, stiffness_ratio=1e6)",
            "description": "Matrix exponential for stiff ODE system"
        },
        "expected": "Accurate exp(A) despite eigenvalue spread of 10^6",
        "difficulty": "pathological",
        "rationale": "Stiff matrices have widely separated eigenvalues causing numerical instability in exp computation."
    },
    {
        "test_id": "LINALG_029",
        "category": "matrix_exp_non_diag",
        "input": {
            "operation": "matrix_log",
            "matrix": "[[2, 1], [0, 2]]",
            "description": "Matrix logarithm of defective matrix"
        },
        "expected": "log(A) where A = [[2,1],[0,2]] = log(2)*I + [[0, 1/2], [0, 0]]",
        "difficulty": "brutal",
        "rationale": "Matrix log of non-diagonalizable matrix requires careful branch selection."
    },
    {
        "test_id": "LINALG_030",
        "category": "matrix_exp_non_diag",
        "input": {
            "operation": "matrix_exp",
            "matrix": "Large_Nilpotent(index=10, size=100)",
            "description": "Matrix exponential of large nilpotent matrix with high index"
        },
        "expected": "Finite polynomial in N up to N^9",
        "difficulty": "extreme",
        "rationale": "Large nilpotent index means exp(N) has many terms, testing series truncation."
    },

    # =========================================================================
    # CATEGORY 7: PSEUDOINVERSE OF MATRICES WITH CLUSTERED SINGULAR VALUES
    # =========================================================================
    {
        "test_id": "LINALG_031",
        "category": "pseudoinverse_clustered",
        "input": {
            "operation": "pseudoinverse",
            "matrix": "Singular_Values_Clustered([1, 1+1e-14, 1+2e-14, 0, 0])",
            "description": "Pseudoinverse with three singular values differing by 10^-14"
        },
        "expected": "Correct pseudoinverse despite near-identical singular values",
        "difficulty": "extreme",
        "rationale": "Clustered singular values cause numerical instability in pseudoinverse computation."
    },
    {
        "test_id": "LINALG_032",
        "category": "pseudoinverse_clustered",
        "input": {
            "operation": "pseudoinverse",
            "matrix": "Low_Rank_Plus_Noise(100, 100, rank=5, noise=1e-10)",
            "description": "Pseudoinverse of noisy low-rank matrix"
        },
        "expected": "Correctly threshold small singular values, return rank-5 approximation inverse",
        "difficulty": "brutal",
        "rationale": "Noise creates spurious small singular values that must be filtered."
    },
    {
        "test_id": "LINALG_033",
        "category": "pseudoinverse_clustered",
        "input": {
            "operation": "minimum_norm_solution",
            "matrix": "Underdetermined(50, 100)",
            "b": "random_vector",
            "description": "Find minimum norm solution to underdetermined system"
        },
        "expected": "Solution with minimum 2-norm among infinitely many",
        "difficulty": "brutal",
        "rationale": "Underdetermined systems have infinite solutions. Pseudoinverse gives minimum norm."
    },
    {
        "test_id": "LINALG_034",
        "category": "pseudoinverse_clustered",
        "input": {
            "operation": "regularized_inverse",
            "matrix": "Severely_Ill_Conditioned(100, condition=1e16)",
            "regularization": "tikhonov",
            "description": "Tikhonov-regularized pseudoinverse"
        },
        "expected": "(A^T A + lambda I)^(-1) A^T with optimal lambda selection",
        "difficulty": "extreme",
        "rationale": "Regularization is essential for stable inversion of ill-conditioned matrices."
    },
    {
        "test_id": "LINALG_035",
        "category": "pseudoinverse_clustered",
        "input": {
            "operation": "pseudoinverse",
            "matrix": "Zeros_And_Ones_Pattern(200, 200, density=0.1)",
            "description": "Pseudoinverse of sparse 0-1 matrix"
        },
        "expected": "Handle integer matrix with potentially integer-like singular values",
        "difficulty": "brutal",
        "rationale": "Integer matrices can have surprising singular value structures and near-cancellations."
    },

    # =========================================================================
    # CATEGORY 8: TENSOR CONTRACTIONS IN HIGH DIMENSIONS
    # =========================================================================
    {
        "test_id": "LINALG_036",
        "category": "tensor_contraction",
        "input": {
            "operation": "tensor_contract",
            "tensor_a": "Random_Tensor(shape=[20, 20, 20, 20])",
            "tensor_b": "Random_Tensor(shape=[20, 20, 20, 20])",
            "contraction": "indices (1,3) with (0,2)",
            "description": "Contract two rank-4 tensors on 2 index pairs"
        },
        "expected": "Resulting rank-4 tensor with shape [20, 20, 20, 20]",
        "difficulty": "brutal",
        "rationale": "High-dimensional tensor contraction is O(n^6) and memory-intensive."
    },
    {
        "test_id": "LINALG_037",
        "category": "tensor_contraction",
        "input": {
            "operation": "einstein_sum",
            "expression": "ijkl,klmn,mnop->ijop",
            "tensors": "[A(10,10,10,10), B(10,10,10,10), C(10,10,10,10)]",
            "description": "Three-tensor contraction via Einstein summation"
        },
        "expected": "Optimal contraction order to minimize operations",
        "difficulty": "extreme",
        "rationale": "Multi-tensor contraction order optimization is NP-hard. Tests heuristic path finding."
    },
    {
        "test_id": "LINALG_038",
        "category": "tensor_contraction",
        "input": {
            "operation": "trace",
            "tensor": "Rank_6_Tensor(shape=[5,5,5,5,5,5])",
            "trace_indices": "[(0,5), (1,4), (2,3)]",
            "description": "Full trace of rank-6 tensor to scalar"
        },
        "expected": "Scalar result, equivalent to triple matrix trace",
        "difficulty": "brutal",
        "rationale": "Multiple simultaneous traces require careful index management."
    },
    {
        "test_id": "LINALG_039",
        "category": "tensor_contraction",
        "input": {
            "operation": "tensor_svd",
            "tensor": "Random_Tensor(shape=[100, 100, 100])",
            "description": "Higher-order SVD (Tucker decomposition) of rank-3 tensor"
        },
        "expected": "Core tensor and factor matrices for each mode",
        "difficulty": "extreme",
        "rationale": "HOSVD generalizes matrix SVD to tensors with significant computational cost."
    },
    {
        "test_id": "LINALG_040",
        "category": "tensor_contraction",
        "input": {
            "operation": "tensor_rank_decomposition",
            "tensor": "Rank_3_Low_CP_Rank(shape=[50,50,50], cp_rank=5)",
            "description": "CP decomposition of tensor into sum of rank-1 tensors"
        },
        "expected": "5 factor vector triples that reconstruct original tensor",
        "difficulty": "pathological",
        "rationale": "CP decomposition is ill-posed (no closed-form solution) and requires iterative ALS."
    },

    # =========================================================================
    # CATEGORY 9: EIGENVALUE PROBLEMS WITH DEFECTIVE MATRICES
    # =========================================================================
    {
        "test_id": "LINALG_041",
        "category": "defective_eigenvalue",
        "input": {
            "operation": "eigendecomposition",
            "matrix": "[[3, 1, 0], [0, 3, 1], [0, 0, 3]]",
            "description": "Eigendecomposition of defective matrix with triple eigenvalue"
        },
        "expected": "Only one eigenvector for eigenvalue 3 (geometric mult=1, algebraic=3)",
        "difficulty": "brutal",
        "rationale": "Defective matrices cannot be diagonalized. Standard eigenvector routines may fail or give wrong count."
    },
    {
        "test_id": "LINALG_042",
        "category": "defective_eigenvalue",
        "input": {
            "operation": "generalized_eigenvectors",
            "matrix": "Defective(size=10, eigenvalue=2, jordan_blocks=[3,3,2,2])",
            "description": "Find generalized eigenvector chains for defective matrix"
        },
        "expected": "4 chains of lengths 3, 3, 2, 2 for eigenvalue 2",
        "difficulty": "extreme",
        "rationale": "Generalized eigenvectors require solving (A-lambda*I)^k v = 0 for increasing k."
    },
    {
        "test_id": "LINALG_043",
        "category": "defective_eigenvalue",
        "input": {
            "operation": "eigenvalues",
            "matrix": "Wilkinson(21)",
            "description": "Eigenvalues of Wilkinson matrix (tridiagonal with clustered eigenvalues)"
        },
        "expected": "21 eigenvalues clustered in pairs near integers",
        "difficulty": "extreme",
        "rationale": "Wilkinson matrix is designed to have extremely close eigenvalue pairs that defeat simple algorithms."
    },
    {
        "test_id": "LINALG_044",
        "category": "defective_eigenvalue",
        "input": {
            "operation": "schur_form",
            "matrix": "Perturbed_Defective(10, perturbation=1e-12)",
            "description": "Schur decomposition of nearly defective matrix"
        },
        "expected": "Quasi-triangular Schur form with 2x2 blocks for complex eigenvalue pairs",
        "difficulty": "pathological",
        "rationale": "Near-defective matrices have Schur form that is ill-conditioned to compute."
    },
    {
        "test_id": "LINALG_045",
        "category": "defective_eigenvalue",
        "input": {
            "operation": "spectral_projector",
            "matrix": "Block_Jordan([2,3,2], eigenvalue=5)",
            "description": "Compute spectral projector onto eigenspace"
        },
        "expected": "Projector P with P^2=P, rank=3 (sum of Jordan block sizes)",
        "difficulty": "brutal",
        "rationale": "Spectral projectors for defective matrices involve contour integrals or residue computations."
    },

    # =========================================================================
    # CATEGORY 10: SCHUR DECOMPOSITION EDGE CASES
    # =========================================================================
    {
        "test_id": "LINALG_046",
        "category": "schur_edge_cases",
        "input": {
            "operation": "real_schur",
            "matrix": "[[0, -1], [1, 0]]",
            "description": "Real Schur form of 2x2 rotation matrix (complex eigenvalues)"
        },
        "expected": "2x2 block [[0,-1],[1,0]] preserved (no real eigenvalues)",
        "difficulty": "brutal",
        "rationale": "Real Schur form must handle complex conjugate eigenvalue pairs as 2x2 blocks."
    },
    {
        "test_id": "LINALG_047",
        "category": "schur_edge_cases",
        "input": {
            "operation": "ordered_schur",
            "matrix": "Random_Complex(50, 50)",
            "ordering": "eigenvalues_by_real_part",
            "description": "Ordered Schur form with eigenvalues sorted by real part"
        },
        "expected": "Triangular T with diagonal sorted, unitary Q with A = Q T Q^H",
        "difficulty": "extreme",
        "rationale": "Reordering Schur form requires careful swap sequences that preserve similarity."
    },
    {
        "test_id": "LINALG_048",
        "category": "schur_edge_cases",
        "input": {
            "operation": "generalized_schur",
            "matrix_a": "Random(20, 20)",
            "matrix_b": "Singular_Random(20, 20, rank=15)",
            "description": "Generalized Schur decomposition with singular B"
        },
        "expected": "QZ decomposition A = Q S Z^H, B = Q T Z^H with infinite generalized eigenvalues",
        "difficulty": "pathological",
        "rationale": "Singular B creates infinite generalized eigenvalues that must be handled specially."
    },
    {
        "test_id": "LINALG_049",
        "category": "schur_edge_cases",
        "input": {
            "operation": "schur_vectors",
            "matrix": "Nearly_Orthogonal_Columns(100, angle_deviation=1e-10)",
            "description": "Extract Schur vectors (Q columns) with high accuracy"
        },
        "expected": "Q orthogonal to machine precision, ||Q Q^H - I|| < 1e-14",
        "difficulty": "extreme",
        "rationale": "Schur vector orthogonality degrades for ill-conditioned input matrices."
    },
    {
        "test_id": "LINALG_050",
        "category": "schur_edge_cases",
        "input": {
            "operation": "matrix_function_via_schur",
            "matrix": "Arbitrary_Complex(30, 30)",
            "function": "f(z) = z^0.5 + log(z) + exp(z)",
            "description": "Compute arbitrary matrix function via Schur-Parlett algorithm"
        },
        "expected": "f(A) computed accurately using Schur form and Frechet derivatives",
        "difficulty": "pathological",
        "rationale": "General matrix functions require Schur form plus careful handling of diagonal blocks."
    },
]


# =============================================================================
# HELPER FUNCTIONS FOR TEST GENERATION
# =============================================================================

def hilbert_matrix(n):
    """Generate n x n Hilbert matrix: H[i,j] = 1/(i+j+1)"""
    return [[1.0/(i+j+1) for j in range(n)] for i in range(n)]


def vandermonde_matrix(nodes):
    """Generate Vandermonde matrix for given nodes"""
    n = len(nodes)
    return [[nodes[i]**j for j in range(n)] for i in range(n)]


def jordan_block(size, eigenvalue):
    """Generate Jordan block of given size with given eigenvalue"""
    block = [[0.0]*size for _ in range(size)]
    for i in range(size):
        block[i][i] = eigenvalue
        if i < size - 1:
            block[i][i+1] = 1.0
    return block


def tridiagonal_matrix(n, diag, off_diag_lower, off_diag_upper):
    """Generate n x n tridiagonal matrix"""
    mat = [[0.0]*n for _ in range(n)]
    for i in range(n):
        mat[i][i] = diag
        if i > 0:
            mat[i][i-1] = off_diag_lower
        if i < n-1:
            mat[i][i+1] = off_diag_upper
    return mat


def wilkinson_matrix(n):
    """Generate Wilkinson's test matrix for eigenvalue clustering"""
    if n % 2 == 0:
        raise ValueError("Wilkinson matrix requires odd dimension")
    m = n // 2
    mat = [[0.0]*n for _ in range(n)]
    for i in range(n):
        mat[i][i] = abs(i - m)
        if i > 0:
            mat[i][i-1] = 1.0
        if i < n-1:
            mat[i][i+1] = 1.0
    return mat


def kahan_matrix(n, c):
    """Generate Kahan matrix designed to defeat Householder QR"""
    s = math.sqrt(1 - c*c)
    mat = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            if i == j:
                mat[i][j] = s ** i
            else:
                mat[i][j] = -c * s ** i
    return mat


# =============================================================================
# TEST STATISTICS
# =============================================================================

def get_test_statistics():
    """Return statistics about the test suite"""
    categories = {}
    difficulties = {"brutal": 0, "extreme": 0, "pathological": 0}

    for test in BRUTAL_LINALG_TESTS:
        cat = test["category"]
        diff = test["difficulty"]

        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] += 1

    return {
        "total_tests": len(BRUTAL_LINALG_TESTS),
        "categories": categories,
        "difficulties": difficulties,
        "category_count": len(categories)
    }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("BRUTAL LINEAR ALGEBRA STRESS TESTS")
    print("=" * 80)
    print()

    stats = get_test_statistics()

    print(f"Total Tests: {stats['total_tests']}")
    print()

    print("Tests by Category:")
    for cat, count in sorted(stats['categories'].items()):
        print(f"  {cat}: {count}")
    print()

    print("Tests by Difficulty:")
    for diff, count in stats['difficulties'].items():
        print(f"  {diff}: {count}")
    print()

    print("Sample Tests:")
    for i, test in enumerate(BRUTAL_LINALG_TESTS[:5]):
        print(f"\n[{test['test_id']}] {test['category']} ({test['difficulty']})")
        print(f"  Rationale: {test['rationale'][:80]}...")
