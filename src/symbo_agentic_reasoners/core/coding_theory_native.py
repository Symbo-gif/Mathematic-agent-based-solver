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
NATIVE CODING THEORY ENGINE
===========================

Pure Python implementation for error-correcting code operations.

MODULES:
--------
1. GF(2) Arithmetic
   - Matrix addition/multiplication over GF(2)
   - Row echelon form in GF(2)
   - Rank computation

2. Bounds and Inequalities
   - Singleton bound: d ≤ n - k + 1
   - Hamming (sphere-packing) bound
   - Plotkin bound
   - Griesmer bound
   - Gilbert-Varshamov bound

3. Combinatorial Functions
   - Binomial coefficients
   - Hamming sphere volumes V_q(n, t)
   - Weight enumerators

Part of the SYMBO_AGENTIC_REASONERS native computation engine.

NO SYMPY - Pure native mathematical reasoning.

REFERENCES:
----------
- MacWilliams, F. J., & Sloane, N. J. A. (1977). The Theory of Error-Correcting Codes. North-Holland.
- Lin, S., & Costello, D. J. (2004). Error Control Coding (2nd ed.). Pearson.
- Brouwer, A. E. (1998). Bounds on the size of linear codes. Handbook of Coding Theory.
"""

import logging
import math
from typing import List, Tuple, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


# ========================================
# GF(2) Matrix Operations
# ========================================

def gf2_matrix_add(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    """
    Add two matrices over GF(2) (binary field).

    In GF(2), addition is XOR: 0+0=0, 0+1=1, 1+0=1, 1+1=0.

    Args:
        A: First matrix (m×n)
        B: Second matrix (m×n)

    Returns:
        Sum matrix A + B

    Raises:
        ValueError: If dimensions don't match
    """
    if len(A) != len(B) or (A and len(A[0]) != len(B[0])):
        raise ValueError("Matrix dimensions must match for addition")

    return [[(A[i][j] ^ B[i][j]) for j in range(len(A[0]))] for i in range(len(A))]


def gf2_matrix_multiply(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    """
    Multiply two matrices over GF(2).

    Multiplication: AND operation (0×0=0, 0×1=0, 1×0=0, 1×1=1)
    Addition: XOR operation

    Args:
        A: First matrix (m×n)
        B: Second matrix (n×p)

    Returns:
        Product matrix A × B (m×p)

    Raises:
        ValueError: If inner dimensions don't match
    """
    if not A or not B:
        return [[]]

    if len(A[0]) != len(B):
        raise ValueError(f"Cannot multiply {len(A)}×{len(A[0])} with {len(B)}×{len(B[0])} matrices")

    m, n, p = len(A), len(A[0]), len(B[0])
    result = [[0 for _ in range(p)] for _ in range(m)]

    for i in range(m):
        for j in range(p):
            # Compute dot product in GF(2): sum of AND operations, then mod 2
            dot_product = sum(A[i][k] & B[k][j] for k in range(n))
            result[i][j] = dot_product % 2

    return result


def gf2_matrix_transpose(A: List[List[int]]) -> List[List[int]]:
    """
    Transpose matrix over GF(2).

    Args:
        A: Matrix (m×n)

    Returns:
        Transposed matrix A^T (n×m)
    """
    if not A or not A[0]:
        return [[]]

    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def gf2_rref(matrix: List[List[int]]) -> Tuple[List[List[int]], int]:
    """
    Compute row reduced echelon form (RREF) of matrix over GF(2).

    Uses Gaussian elimination with partial pivoting.

    Args:
        matrix: Input matrix (m×n)

    Returns:
        Tuple of (RREF matrix, rank)
    """
    if not matrix or not matrix[0]:
        return matrix, 0

    # Make a copy to avoid modifying original
    A = [row[:] for row in matrix]
    m, n = len(A), len(A[0])

    pivot_row = 0
    for col in range(n):
        # Find pivot
        found_pivot = False
        for row in range(pivot_row, m):
            if A[row][col] == 1:
                # Swap rows
                A[pivot_row], A[row] = A[row], A[pivot_row]
                found_pivot = True
                break

        if not found_pivot:
            continue

        # Eliminate all other 1s in this column
        for row in range(m):
            if row != pivot_row and A[row][col] == 1:
                # Add pivot row to current row (XOR in GF(2))
                for j in range(n):
                    A[row][j] ^= A[pivot_row][j]

        pivot_row += 1

    rank = pivot_row
    return A, rank


def gf2_rank(matrix: List[List[int]]) -> int:
    """
    Compute rank of matrix over GF(2).

    Args:
        matrix: Input matrix

    Returns:
        Rank (number of linearly independent rows)
    """
    _, rank = gf2_rref(matrix)
    return rank


def gf2_null_space(matrix: List[List[int]]) -> List[List[int]]:
    """
    Compute basis for null space (kernel) of matrix over GF(2).

    Null space = {x : Ax = 0}.

    Args:
        matrix: Input matrix (m×n)

    Returns:
        List of basis vectors for null space
    """
    if not matrix or not matrix[0]:
        return [[]]

    m, n = len(matrix), len(matrix[0])
    rref, rank = gf2_rref(matrix)

    # Identify pivot and free columns
    pivot_cols = []
    current_row = 0
    for col in range(n):
        if current_row < rank and rref[current_row][col] == 1:
            pivot_cols.append(col)
            current_row += 1

    free_cols = [col for col in range(n) if col not in pivot_cols]

    if not free_cols:
        # Trivial null space {0}
        return [[0] * n]

    # Build null space basis
    null_basis = []
    for free_col in free_cols:
        vector = [0] * n
        vector[free_col] = 1

        # For each pivot column, set corresponding entry
        for i, pivot_col in enumerate(pivot_cols):
            if i < rank:
                vector[pivot_col] = rref[i][free_col]

        null_basis.append(vector)

    return null_basis


# ========================================
# Combinatorial Functions
# ========================================

@lru_cache(maxsize=10000)
def binomial(n: int, k: int) -> int:
    """
    Compute binomial coefficient C(n, k) = n! / (k! * (n-k)!).

    Uses dynamic programming to handle large values.

    Args:
        n: Total items
        k: Items to choose

    Returns:
        Binomial coefficient C(n, k)
    """
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1

    # Use symmetry: C(n, k) = C(n, n-k)
    if k > n - k:
        k = n - k

    # Calculate using multiplicative formula
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)

    return result


def sphere_volume(n: int, t: int, q: int = 2) -> int:
    """
    Compute volume of Hamming sphere of radius t in F_q^n.

    V_q(n, t) = Σ(i=0 to t) C(n, i) * (q-1)^i

    This is the number of vectors within Hamming distance t from any given vector.

    Args:
        n: Dimension (code length)
        t: Radius (error correction capability)
        q: Alphabet size (default 2 for binary)

    Returns:
        Sphere volume V_q(n, t)
    """
    volume = 0
    for i in range(t + 1):
        volume += binomial(n, i) * ((q - 1) ** i)

    return volume


def hamming_weight(vector: List[int]) -> int:
    """
    Compute Hamming weight (number of nonzero entries) of vector.

    Args:
        vector: Binary or q-ary vector

    Returns:
        Number of nonzero positions
    """
    return sum(1 for x in vector if x != 0)


def hamming_distance(x: List[int], y: List[int]) -> int:
    """
    Compute Hamming distance between two vectors.

    d_H(x, y) = |{i : x_i ≠ y_i}|

    Args:
        x: First vector
        y: Second vector

    Returns:
        Hamming distance

    Raises:
        ValueError: If vectors have different lengths
    """
    if len(x) != len(y):
        raise ValueError("Vectors must have same length")

    return sum(1 for i in range(len(x)) if x[i] != y[i])


# ========================================
# Code Parameter Bounds
# ========================================

def singleton_bound(n: int, k: int, q: int = 2) -> int:
    """
    Singleton bound on minimum distance.

    d ≤ n - k + 1

    This is the tightest bound and holds for all linear codes.
    Codes achieving this bound are called Maximum Distance Separable (MDS).

    Args:
        n: Code length
        k: Dimension
        q: Alphabet size

    Returns:
        Upper bound on minimum distance
    """
    return n - k + 1


def hamming_bound(n: int, k: int, t: int, q: int = 2) -> bool:
    """
    Check if [n,k] code with error correction capability t satisfies Hamming bound.

    Hamming (sphere-packing) bound:
    M ≤ q^n / V_q(n, t)

    Where M = q^k is the number of codewords.

    Codes achieving this bound are called perfect codes.

    Args:
        n: Code length
        k: Dimension
        t: Error correction capability (t = floor((d-1)/2))
        q: Alphabet size

    Returns:
        True if code satisfies Hamming bound
    """
    M = q ** k
    max_M = (q ** n) // sphere_volume(n, t, q)

    return M <= max_M


def plotkin_bound(n: int, d: int, q: int = 2) -> int:
    """
    Plotkin bound on number of codewords.

    For binary codes (q=2):
    - If d is even: M ≤ 2d / (2d - n)  (for n < 2d)
    - If d is odd:  M ≤ 2(d+1) / (2(d+1) - n)  (for n < 2d+1)

    Args:
        n: Code length
        d: Minimum distance
        q: Alphabet size

    Returns:
        Upper bound on number of codewords M

    Raises:
        ValueError: If parameters are invalid
    """
    if q == 2:
        if d % 2 == 0:
            if n < 2 * d:
                return 2 * d // (2 * d - n)
            else:
                return float('inf')  # No bound
        else:
            if n < 2 * d + 1:
                return 2 * (d + 1) // (2 * (d + 1) - n)
            else:
                return float('inf')
    else:
        # General Plotkin bound
        theta = 1 - 1 / q
        if n < d / theta:
            return int((d / theta) / (d / theta - n))
        else:
            return float('inf')


def griesmer_bound(k: int, d: int, q: int = 2) -> int:
    """
    Griesmer bound on code length.

    n ≥ Σ(i=0 to k-1) ceil(d / q^i)

    This gives a lower bound on n for a given k and d.

    Args:
        k: Dimension
        d: Minimum distance
        q: Alphabet size

    Returns:
        Lower bound on code length n
    """
    n_min = 0
    for i in range(k):
        n_min += math.ceil(d / (q ** i))

    return n_min


def gilbert_varshamov_bound(n: int, d: int, q: int = 2) -> int:
    """
    Gilbert-Varshamov bound on dimension.

    Existence bound: There exists an [n,k,d]_q code if:
    q^k ≤ q^n / V_q(n, d-1)

    Args:
        n: Code length
        d: Minimum distance
        q: Alphabet size

    Returns:
        Lower bound on dimension k
    """
    if d <= 1:
        return n  # Trivial

    vol = sphere_volume(n, d - 1, q)
    max_k = n - math.ceil(math.log(vol, q))

    return max_k


def is_perfect_code(n: int, k: int, d: int, q: int = 2) -> bool:
    """
    Check if [n,k,d]_q is a perfect code.

    Perfect code: M * V_q(n, t) = q^n, where t = floor((d-1)/2)

    Known perfect codes:
    - Hamming codes: [2^r-1, 2^r-r-1, 3] for r ≥ 2
    - Golay codes: [23,12,7] (binary), [11,6,5] (ternary)
    - Trivial codes: Repetition, single parity check

    Args:
        n: Code length
        k: Dimension
        d: Minimum distance
        q: Alphabet size

    Returns:
        True if code is perfect
    """
    M = q ** k
    t = (d - 1) // 2
    sphere_vol = sphere_volume(n, t, q)

    return M * sphere_vol == q ** n


# ========================================
# Weight Distributions
# ========================================

def weight_distribution(codewords: List[List[int]]) -> Dict[int, int]:
    """
    Compute weight distribution of code.

    A_w = number of codewords of weight w

    Args:
        codewords: List of codewords (each a binary/q-ary vector)

    Returns:
        Dictionary mapping weight → count
    """
    distribution = {}

    for codeword in codewords:
        weight = hamming_weight(codeword)
        distribution[weight] = distribution.get(weight, 0) + 1

    return distribution


def macwilliams_identity(weight_enum: Dict[int, int], k: int, q: int = 2) -> Dict[int, int]:
    """
    Apply MacWilliams identity to transform weight enumerator of code to its dual.

    For binary codes (q=2):
    W_{C⊥}(x, y) = (1/2^k) * W_C(x + y, x - y)

    In terms of weight distribution:
    A'_w = (1/|C|) * Σ(i=0 to n) A_i * K_w(i)

    where K_w(i) are Krawtchouk polynomials.

    Args:
        weight_enum: Weight distribution {w: A_w} of code C
        k: Dimension of code C
        q: Alphabet size

    Returns:
        Weight distribution of dual code C⊥
    """
    if q != 2:
        raise NotImplementedError("MacWilliams identity currently only implemented for binary codes")

    n = max(weight_enum.keys()) if weight_enum else 0
    M = 2 ** k

    dual_enum = {}

    for w in range(n + 1):
        # Compute A'_w using Krawtchouk polynomials
        sum_val = 0
        for i, A_i in weight_enum.items():
            K_w_i = krawtchouk_polynomial(w, i, n, q)
            sum_val += A_i * K_w_i

        dual_enum[w] = sum_val // M

    return dual_enum


@lru_cache(maxsize=10000)
def krawtchouk_polynomial(j: int, x: int, n: int, q: int = 2) -> int:
    """
    Compute Krawtchouk polynomial K_j(x; n, q).

    K_j(x) = Σ(i=0 to j) (-1)^i * (q-1)^(j-i) * C(x, i) * C(n-x, j-i)

    Args:
        j: Polynomial index
        x: Evaluation point
        n: Length parameter
        q: Alphabet size

    Returns:
        K_j(x; n, q)
    """
    if j < 0 or j > n or x < 0 or x > n:
        return 0

    result = 0
    for i in range(min(j, x) + 1):
        term = ((-1) ** i *
                ((q - 1) ** (j - i)) *
                binomial(x, i) *
                binomial(n - x, j - i))
        result += term

    return result


# ========================================
# Utility Functions
# ========================================

def check_parameters_valid(n: int, k: int, d: int, q: int = 2) -> Tuple[bool, str]:
    """
    Validate code parameters [n,k,d]_q against theoretical bounds.

    Args:
        n: Code length
        k: Dimension
        d: Minimum distance
        q: Alphabet size

    Returns:
        Tuple of (is_valid, error_message)
    """
    if n <= 0 or k <= 0 or d <= 0:
        return False, "All parameters must be positive"

    if k > n:
        return False, f"Dimension k={k} cannot exceed length n={n}"

    # Check Singleton bound
    singleton = singleton_bound(n, k, q)
    if d > singleton:
        return False, f"Minimum distance d={d} violates Singleton bound d ≤ {singleton}"

    # Check Griesmer bound
    griesmer = griesmer_bound(k, d, q)
    if n < griesmer:
        return False, f"Length n={n} violates Griesmer bound n ≥ {griesmer}"

    # Check if parameters are feasible
    M = q ** k
    if M > q ** n:
        return False, f"Number of codewords q^k={M} exceeds alphabet size q^n={q**n}"

    return True, "Parameters are valid"


def minimum_distance_brute_force(codewords: List[List[int]]) -> int:
    """
    Compute minimum distance by brute force.

    d_min = min {d_H(c_i, c_j) : i ≠ j}
        = min {wt(c_i - c_j) : i ≠ j}
        = min {wt(c) : c ≠ 0} for linear codes

    Args:
        codewords: List of all codewords

    Returns:
        Minimum Hamming distance
    """
    if len(codewords) < 2:
        return 0

    min_dist = len(codewords[0])  # Maximum possible

    for i in range(len(codewords)):
        for j in range(i + 1, len(codewords)):
            dist = hamming_distance(codewords[i], codewords[j])
            if dist < min_dist:
                min_dist = dist

    return min_dist


def is_systematic_form(generator: List[List[int]]) -> Tuple[bool, List[int]]:
    """
    Check if generator matrix is in systematic form [I_k | P].

    Args:
        generator: Generator matrix G (k×n)

    Returns:
        Tuple of (is_systematic, identity_columns)
    """
    if not generator or not generator[0]:
        return False, []

    k = len(generator)
    n = len(generator[0])

    if k > n:
        return False, []

    # Check if first k columns form identity matrix
    for i in range(k):
        for j in range(k):
            expected = 1 if i == j else 0
            if generator[i][j] != expected:
                return False, []

    return True, list(range(k))
