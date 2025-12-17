# Discrete Mathematics Capability Improvement Plan

## Executive Summary

**Current Score:** 55/100
**Target Score:** 70/100 (27% improvement)
**Gap Analysis:** +15 points required through 4 new specialists and 2 enhancements

This document provides a comprehensive plan to improve the discrete mathematics capability in the Symbo Agentic Reasoners system from 55/100 to 70/100. The improvement focuses on adding coverage for missing subdisciplines while maintaining the project's NO SYMPY philosophy.

---

## Current State Analysis

### Existing Discrete Math Specialists (2 agents)

#### 1. CombinatoricsAgent (`combinatorics_agent.py`)
**Location:** `src/symbo_agentic_reasoners/agents/specialists/discrete_math/combinatorics_agent.py`

**Current Capabilities:**
- Factorial computation (native `math.factorial`)
- Binomial coefficients (multiplicative formula)
- Permutations: P(n,r) = n! / (n-r)!
- Combinations: C(n,r) = n! / (k! * (n-k)!)

**Gaps:**
- No generating functions support (mentioned in docstring but not implemented)
- No partitions
- No Stirling numbers
- No Catalan numbers
- No derangements
- No multinomial coefficients
- No inclusion-exclusion principle

#### 2. GraphTheoryAgent (`graph_theory_agent.py`)
**Location:** `src/symbo_agentic_reasoners/agents/specialists/discrete_math/graph_theory_agent.py`

**Current Capabilities:**
- Dijkstra's shortest path
- BFS traversal
- DFS traversal
- Max flow (simplified/placeholder)

**Gaps:**
- No minimum spanning tree (Prim/Kruskal)
- No topological sorting
- No strongly connected components (Tarjan/Kosaraju)
- No bipartite matching
- No graph coloring
- No Eulerian/Hamiltonian path detection
- No cycle detection beyond DFS

### Related Specialists in Other Domains

#### NumberTheorySpecialist (in Algebra)
**Location:** `src/symbo_agentic_reasoners/agents/specialists/algebra/number_theory_specialist.py`

Already implements:
- Miller-Rabin primality test
- Pollard's rho factorization
- GCD/LCM (Extended Euclidean)
- Modular arithmetic
- Euler's totient
- Chinese Remainder Theorem

#### PropositionalLogicSpecialist (in Logic)
**Location:** `src/symbo_agentic_reasoners/agents/specialists/logic/propositional_specialist.py`

Already implements:
- Truth table generation (safe evaluator)
- Tautology/contradiction detection
- Satisfiability checking
- Logical equivalence
- Modus ponens/tollens

### Native Number Theory Module
**Location:** `src/symbo_agentic_reasoners/core/number_theory_native.py`

Provides robust foundation with:
- Prime sieve (Eratosthenes)
- Mobius function
- Von Mangoldt function
- Totient function
- Divisor functions
- Liouville function
- Dirichlet convolution
- Chebyshev functions

---

## Gap Analysis by Subdiscipline

| Subdiscipline | Current Coverage | Gap | Priority |
|--------------|-----------------|-----|----------|
| Combinatorics | 40% | Generating functions, partitions, advanced counting | HIGH |
| Graph Theory | 50% | MST, SCC, coloring, matching | HIGH |
| Set Theory | 0% | All operations missing | HIGH |
| Recurrence Relations | 0% | Solving, characteristic equations | MEDIUM |
| Boolean Algebra | 30% | CNF/DNF, minimization, Karnaugh | MEDIUM |
| Finite Automata | 0% | DFA, NFA, regex, grammar | LOW |
| Cryptographic Math | 10% | RSA, discrete log, elliptic basics | LOW |
| Number Theory | 80% | Already strong via algebra specialist | - |

---

## Proposed New Specialists

### 1. SetTheoryAgent (NEW - HIGH PRIORITY)
**Estimated Score Impact:** +4 points

**Purpose:** Handle set-theoretic operations that are fundamental to discrete mathematics.

**File Location:** `src/symbo_agentic_reasoners/agents/specialists/discrete_math/set_theory_agent.py`

**Service Registration:**
```python
service_type = 'math.discrete.sets'
algorithm = 'native_set_ops'
tier = '3'
```

**Mathematical Rules (Native Implementation):**

```python
class NativeSetOperations:
    """
    Pure Python set theory operations.

    Sets are represented as frozensets for immutability and hashability.
    Relations as sets of tuples.
    """

    # Basic Set Operations
    @staticmethod
    def union(A: frozenset, B: frozenset) -> frozenset:
        """A U B = {x : x in A or x in B}"""
        return A | B

    @staticmethod
    def intersection(A: frozenset, B: frozenset) -> frozenset:
        """A n B = {x : x in A and x in B}"""
        return A & B

    @staticmethod
    def difference(A: frozenset, B: frozenset) -> frozenset:
        """A - B = {x : x in A and x not in B}"""
        return A - B

    @staticmethod
    def symmetric_difference(A: frozenset, B: frozenset) -> frozenset:
        """A delta B = (A - B) U (B - A)"""
        return A ^ B

    @staticmethod
    def cartesian_product(A: frozenset, B: frozenset) -> frozenset:
        """A x B = {(a, b) : a in A, b in B}"""
        return frozenset((a, b) for a in A for b in B)

    @staticmethod
    def power_set(A: frozenset) -> frozenset:
        """
        P(A) = set of all subsets of A
        |P(A)| = 2^|A|

        Uses binary representation for subset generation.
        """
        elements = list(A)
        n = len(elements)
        result = []
        for i in range(2**n):
            subset = frozenset(elements[j] for j in range(n) if (i >> j) & 1)
            result.append(subset)
        return frozenset(result)

    @staticmethod
    def is_subset(A: frozenset, B: frozenset) -> bool:
        """A subseteq B iff every element of A is in B"""
        return A <= B

    @staticmethod
    def is_proper_subset(A: frozenset, B: frozenset) -> bool:
        """A subset B iff A subseteq B and A != B"""
        return A < B

    @staticmethod
    def cardinality(A: frozenset) -> int:
        """|A| = number of elements in A"""
        return len(A)

class RelationOperations:
    """
    Operations on relations (sets of ordered pairs).
    """

    @staticmethod
    def domain(R: frozenset) -> frozenset:
        """dom(R) = {a : (a,b) in R for some b}"""
        return frozenset(a for a, _ in R)

    @staticmethod
    def range_set(R: frozenset) -> frozenset:
        """ran(R) = {b : (a,b) in R for some a}"""
        return frozenset(b for _, b in R)

    @staticmethod
    def compose(R: frozenset, S: frozenset) -> frozenset:
        """
        R o S = {(a,c) : exists b such that (a,b) in S and (b,c) in R}
        Note: Composition reads right-to-left
        """
        S_dict = {}
        for a, b in S:
            if a not in S_dict:
                S_dict[a] = set()
            S_dict[a].add(b)

        result = set()
        for b, c in R:
            if b in S_dict:
                for a in S_dict[b]:
                    result.add((a, c))
        return frozenset(result)

    @staticmethod
    def inverse(R: frozenset) -> frozenset:
        """R^-1 = {(b,a) : (a,b) in R}"""
        return frozenset((b, a) for a, b in R)

    @staticmethod
    def is_reflexive(R: frozenset, A: frozenset) -> bool:
        """R is reflexive on A iff (a,a) in R for all a in A"""
        return all((a, a) in R for a in A)

    @staticmethod
    def is_symmetric(R: frozenset) -> bool:
        """R is symmetric iff (a,b) in R implies (b,a) in R"""
        return all((b, a) in R for a, b in R)

    @staticmethod
    def is_antisymmetric(R: frozenset) -> bool:
        """R is antisymmetric iff (a,b) in R and (b,a) in R implies a = b"""
        for a, b in R:
            if a != b and (b, a) in R:
                return False
        return True

    @staticmethod
    def is_transitive(R: frozenset) -> bool:
        """R is transitive iff (a,b) in R and (b,c) in R implies (a,c) in R"""
        for a, b in R:
            for c, d in R:
                if b == c and (a, d) not in R:
                    return False
        return True

    @staticmethod
    def is_equivalence_relation(R: frozenset, A: frozenset) -> bool:
        """Equivalence relation = reflexive + symmetric + transitive"""
        return (RelationOperations.is_reflexive(R, A) and
                RelationOperations.is_symmetric(R) and
                RelationOperations.is_transitive(R))

    @staticmethod
    def is_partial_order(R: frozenset, A: frozenset) -> bool:
        """Partial order = reflexive + antisymmetric + transitive"""
        return (RelationOperations.is_reflexive(R, A) and
                RelationOperations.is_antisymmetric(R) and
                RelationOperations.is_transitive(R))

    @staticmethod
    def equivalence_classes(R: frozenset, A: frozenset) -> frozenset:
        """
        Compute equivalence classes for equivalence relation R on A.
        Returns partition of A.
        """
        classes = []
        remaining = set(A)

        while remaining:
            a = remaining.pop()
            eq_class = {a}
            for b in list(remaining):
                if (a, b) in R:
                    eq_class.add(b)
                    remaining.remove(b)
            classes.append(frozenset(eq_class))

        return frozenset(classes)

    @staticmethod
    def transitive_closure(R: frozenset) -> frozenset:
        """
        Compute R+ = R U R^2 U R^3 U ...
        Uses Warshall's algorithm.
        """
        # Build adjacency matrix representation
        elements = set()
        for a, b in R:
            elements.add(a)
            elements.add(b)
        elements = list(elements)
        n = len(elements)
        idx = {e: i for i, e in enumerate(elements)}

        # Initialize closure matrix
        closure = [[False] * n for _ in range(n)]
        for a, b in R:
            closure[idx[a]][idx[b]] = True

        # Warshall's algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    closure[i][j] = closure[i][j] or (closure[i][k] and closure[k][j])

        # Convert back to relation
        result = set()
        for i in range(n):
            for j in range(n):
                if closure[i][j]:
                    result.add((elements[i], elements[j]))

        return frozenset(result)

class FunctionOperations:
    """
    Operations on functions (special relations where each domain element
    maps to exactly one range element).
    """

    @staticmethod
    def is_function(R: frozenset, A: frozenset, B: frozenset) -> bool:
        """Check if R is a function from A to B"""
        domain_check = RelationOperations.domain(R) == A

        # Check single-valued
        seen = set()
        for a, b in R:
            if a in seen:
                # Check if maps to same value
                for x, y in R:
                    if x == a and y != b:
                        return False
            seen.add(a)

        # Check codomain
        for _, b in R:
            if b not in B:
                return False

        return domain_check

    @staticmethod
    def is_injective(R: frozenset) -> bool:
        """f is injective (one-to-one) iff f(a) = f(b) implies a = b"""
        seen_outputs = set()
        for a, b in R:
            if b in seen_outputs:
                return False
            seen_outputs.add(b)
        return True

    @staticmethod
    def is_surjective(R: frozenset, B: frozenset) -> bool:
        """f is surjective (onto) iff every b in B has preimage"""
        range_r = RelationOperations.range_set(R)
        return range_r == B

    @staticmethod
    def is_bijective(R: frozenset, A: frozenset, B: frozenset) -> bool:
        """f is bijective iff injective and surjective"""
        return (FunctionOperations.is_injective(R) and
                FunctionOperations.is_surjective(R, B))
```

**Agent Structure:**
```python
class SetTheoryAgent(BDIAgent):
    """
    Set Theory Specialist - Tier 3

    Handles:
    - Set operations (union, intersection, difference, symmetric difference)
    - Cartesian products
    - Power sets
    - Relations (reflexive, symmetric, transitive, equivalence, partial order)
    - Functions (injective, surjective, bijective)
    - Transitive closure
    - Equivalence classes and partitions
    """

    def __init__(self, agent_id='set_theory_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.discrete.sets',
                agent_id=agent_id,
                algorithm='native_set_ops',
                cost='low',
                instance=self,
                tier='3',
                operations='union_intersection_powerset_relations_functions'
            ))

    # BDI methods: update_beliefs, deliberate, execute_step
    # Similar pattern to CombinatoricsAgent
```

---

### 2. RecurrenceRelationAgent (NEW - MEDIUM PRIORITY)
**Estimated Score Impact:** +3 points

**Purpose:** Solve recurrence relations analytically and numerically.

**File Location:** `src/symbo_agentic_reasoners/agents/specialists/discrete_math/recurrence_agent.py`

**Service Registration:**
```python
service_type = 'math.discrete.recurrence'
algorithm = 'characteristic_equation'
tier = '3'
```

**Mathematical Rules (Native Implementation):**

```python
import math
from typing import List, Tuple, Dict, Any, Optional, Callable
from fractions import Fraction

class RecurrenceSolver:
    """
    Native recurrence relation solver.

    Supports:
    - Linear homogeneous recurrences with constant coefficients
    - Linear non-homogeneous recurrences
    - Characteristic equation method
    - Generating function approach (recognition)
    - Numerical iteration
    """

    @staticmethod
    def solve_linear_homogeneous(
        coefficients: List[float],  # [a_1, a_2, ..., a_k] for a_n = a_1*a_{n-1} + ... + a_k*a_{n-k}
        initial_values: List[float]  # [a_0, a_1, ..., a_{k-1}]
    ) -> Dict[str, Any]:
        """
        Solve linear homogeneous recurrence with constant coefficients.

        Method: Characteristic equation
        a_n = c_1*a_{n-1} + c_2*a_{n-2} + ... + c_k*a_{n-k}

        Characteristic equation: r^k = c_1*r^{k-1} + c_2*r^{k-2} + ... + c_k
        Or: r^k - c_1*r^{k-1} - c_2*r^{k-2} - ... - c_k = 0
        """
        k = len(coefficients)

        if k == 1:
            # First order: a_n = c*a_{n-1}
            # Solution: a_n = a_0 * c^n
            c = coefficients[0]
            return {
                'type': 'first_order',
                'solution': f'a_n = {initial_values[0]} * {c}^n',
                'closed_form': lambda n: initial_values[0] * (c ** n),
                'method': 'direct'
            }

        if k == 2:
            # Second order: a_n = c_1*a_{n-1} + c_2*a_{n-2}
            # Characteristic: r^2 - c_1*r - c_2 = 0
            c1, c2 = coefficients

            # Quadratic formula
            discriminant = c1**2 + 4*c2

            if discriminant > 0:
                # Two distinct real roots
                r1 = (c1 + math.sqrt(discriminant)) / 2
                r2 = (c1 - math.sqrt(discriminant)) / 2

                # Solve for constants: a_0 = A + B, a_1 = A*r1 + B*r2
                a0, a1 = initial_values[0], initial_values[1]
                # A + B = a0
                # A*r1 + B*r2 = a1
                # A = (a1 - a0*r2) / (r1 - r2)
                A = (a1 - a0*r2) / (r1 - r2)
                B = a0 - A

                return {
                    'type': 'second_order_distinct_real',
                    'roots': (r1, r2),
                    'solution': f'a_n = {A:.6f}*({r1:.6f})^n + {B:.6f}*({r2:.6f})^n',
                    'closed_form': lambda n: A * (r1**n) + B * (r2**n),
                    'method': 'characteristic_equation'
                }

            elif discriminant == 0:
                # Repeated root
                r = c1 / 2

                # a_n = (A + B*n) * r^n
                a0, a1 = initial_values[0], initial_values[1]
                A = a0
                B = (a1 - a0*r) / r if r != 0 else a1

                return {
                    'type': 'second_order_repeated',
                    'root': r,
                    'solution': f'a_n = ({A:.6f} + {B:.6f}*n) * ({r:.6f})^n',
                    'closed_form': lambda n: (A + B*n) * (r**n),
                    'method': 'characteristic_equation'
                }

            else:
                # Complex conjugate roots
                real_part = c1 / 2
                imag_part = math.sqrt(-discriminant) / 2
                r = math.sqrt(real_part**2 + imag_part**2)
                theta = math.atan2(imag_part, real_part)

                # a_n = r^n * (A*cos(n*theta) + B*sin(n*theta))
                a0, a1 = initial_values[0], initial_values[1]
                A = a0
                # a1 = r*(A*cos(theta) + B*sin(theta))
                B = (a1/r - A*math.cos(theta)) / math.sin(theta) if math.sin(theta) != 0 else 0

                return {
                    'type': 'second_order_complex',
                    'modulus': r,
                    'argument': theta,
                    'solution': f'a_n = ({r:.6f})^n * ({A:.6f}*cos({theta:.6f}*n) + {B:.6f}*sin({theta:.6f}*n))',
                    'closed_form': lambda n: (r**n) * (A*math.cos(theta*n) + B*math.sin(theta*n)),
                    'method': 'characteristic_equation'
                }

        # Higher order - return numerical solution
        return RecurrenceSolver.solve_numerically(coefficients, initial_values)

    @staticmethod
    def solve_numerically(
        coefficients: List[float],
        initial_values: List[float],
        n_terms: int = 100
    ) -> Dict[str, Any]:
        """
        Compute terms numerically via iteration.
        """
        k = len(coefficients)
        sequence = list(initial_values)

        for n in range(k, n_terms):
            next_term = sum(coefficients[i] * sequence[n-1-i] for i in range(k))
            sequence.append(next_term)

        return {
            'type': 'numerical',
            'sequence': sequence,
            'method': 'iteration',
            'closed_form': None
        }

    @staticmethod
    def solve_fibonacci_type(a: int, b: int, F0: int = 0, F1: int = 1) -> Dict[str, Any]:
        """
        Solve generalized Fibonacci: F_n = a*F_{n-1} + b*F_{n-2}

        Standard Fibonacci: a=1, b=1
        Lucas numbers: a=1, b=1, F0=2, F1=1
        Pell numbers: a=2, b=1
        """
        return RecurrenceSolver.solve_linear_homogeneous([a, b], [F0, F1])

    @staticmethod
    def solve_divide_and_conquer(
        a: int,  # Number of subproblems
        b: int,  # Factor by which problem size shrinks
        f_n: str  # Work at each level: 'n', 'n*log(n)', 'n^2', 'log(n)', '1'
    ) -> Dict[str, Any]:
        """
        Master theorem for T(n) = a*T(n/b) + f(n)

        Cases:
        1. If f(n) = O(n^c) where c < log_b(a): T(n) = Theta(n^{log_b(a)})
        2. If f(n) = Theta(n^c) where c = log_b(a): T(n) = Theta(n^c * log(n))
        3. If f(n) = Omega(n^c) where c > log_b(a): T(n) = Theta(f(n))
        """
        log_b_a = math.log(a) / math.log(b)

        # Parse f_n to determine c
        if f_n == '1':
            c = 0
        elif f_n == 'log(n)':
            c = 0  # Technically log, but asymptotically less than n^epsilon
        elif f_n == 'n':
            c = 1
        elif f_n == 'n*log(n)':
            c = 1  # With log factor
        elif f_n == 'n^2':
            c = 2
        else:
            c = 1  # Default

        if c < log_b_a:
            complexity = f'Theta(n^{log_b_a:.4f})'
            case = 1
        elif abs(c - log_b_a) < 0.001:
            complexity = f'Theta(n^{c} * log(n))'
            case = 2
        else:
            complexity = f'Theta({f_n})'
            case = 3

        return {
            'recurrence': f'T(n) = {a}*T(n/{b}) + {f_n}',
            'log_b_a': log_b_a,
            'f_exponent': c,
            'master_theorem_case': case,
            'complexity': complexity,
            'method': 'master_theorem'
        }

    @staticmethod
    def recognize_known_sequence(sequence: List[int]) -> Optional[Dict[str, Any]]:
        """
        Recognize common sequences from first few terms.
        """
        known = {
            (0, 1, 1, 2, 3, 5, 8): {'name': 'Fibonacci', 'formula': 'F_n = F_{n-1} + F_{n-2}'},
            (2, 1, 3, 4, 7, 11): {'name': 'Lucas', 'formula': 'L_n = L_{n-1} + L_{n-2}'},
            (0, 1, 2, 5, 12, 29): {'name': 'Pell', 'formula': 'P_n = 2*P_{n-1} + P_{n-2}'},
            (1, 1, 2, 5, 14, 42): {'name': 'Catalan', 'formula': 'C_n = (2n)! / ((n+1)! * n!)'},
            (1, 2, 6, 24, 120, 720): {'name': 'Factorial', 'formula': 'n!'},
            (1, 1, 2, 3, 5, 7, 11): {'name': 'Tribonacci (partial)', 'formula': 'T_n = T_{n-1} + T_{n-2} + T_{n-3}'},
        }

        seq_tuple = tuple(sequence[:7]) if len(sequence) >= 7 else tuple(sequence)

        for pattern, info in known.items():
            if seq_tuple[:len(pattern)] == pattern[:len(seq_tuple)]:
                return info

        return None

    @staticmethod
    def find_recurrence(sequence: List[int], max_order: int = 5) -> Optional[Dict[str, Any]]:
        """
        Attempt to find a linear recurrence that generates the sequence.

        Uses Berlekamp-Massey algorithm concept.
        """
        n = len(sequence)

        for order in range(1, min(max_order + 1, n // 2)):
            # Try to find coefficients for order-k recurrence
            # Set up system: for i in range(order, n):
            #   sequence[i] = sum(c_j * sequence[i-1-j] for j in range(order))

            # Build matrix equation Ac = b
            A = []
            b = []
            for i in range(order, min(n, order + order + 5)):
                row = [sequence[i-1-j] for j in range(order)]
                A.append(row)
                b.append(sequence[i])

            # Solve using least squares / Gaussian elimination
            # Simplified: try exact match
            try:
                # Use simple Gaussian elimination
                coeffs = RecurrenceSolver._solve_linear_system(A, b)
                if coeffs:
                    # Verify
                    valid = True
                    for i in range(order, n):
                        predicted = sum(coeffs[j] * sequence[i-1-j] for j in range(order))
                        if abs(predicted - sequence[i]) > 0.001:
                            valid = False
                            break

                    if valid:
                        return {
                            'order': order,
                            'coefficients': coeffs,
                            'formula': f'a_n = ' + ' + '.join(f'{c:.4f}*a_{{n-{j+1}}}' for j, c in enumerate(coeffs))
                        }
            except:
                continue

        return None

    @staticmethod
    def _solve_linear_system(A: List[List[float]], b: List[float]) -> Optional[List[float]]:
        """Simple Gaussian elimination for square systems."""
        n = len(A)
        m = len(A[0]) if A else 0

        if n < m:
            return None

        # Augmented matrix
        aug = [row[:] + [b[i]] for i, row in enumerate(A[:m])]

        # Forward elimination
        for i in range(m):
            # Find pivot
            max_row = i
            for k in range(i + 1, m):
                if abs(aug[k][i]) > abs(aug[max_row][i]):
                    max_row = k
            aug[i], aug[max_row] = aug[max_row], aug[i]

            if abs(aug[i][i]) < 1e-10:
                return None

            for k in range(i + 1, m):
                factor = aug[k][i] / aug[i][i]
                for j in range(i, m + 1):
                    aug[k][j] -= factor * aug[i][j]

        # Back substitution
        x = [0.0] * m
        for i in range(m - 1, -1, -1):
            x[i] = aug[i][m]
            for j in range(i + 1, m):
                x[i] -= aug[i][j] * x[j]
            x[i] /= aug[i][i]

        return x
```

**Agent Structure:**
```python
class RecurrenceRelationAgent(BDIAgent):
    """
    Recurrence Relation Specialist - Tier 3

    Handles:
    - Linear homogeneous recurrences (characteristic equation)
    - Fibonacci-type recurrences
    - Divide-and-conquer analysis (Master theorem)
    - Sequence recognition
    - Recurrence finding from sequence
    - Numerical iteration
    """
```

---

### 3. BooleanAlgebraAgent (NEW - MEDIUM PRIORITY)
**Estimated Score Impact:** +3 points

**Purpose:** Extend logic capabilities with Boolean algebra and minimization.

**File Location:** `src/symbo_agentic_reasoners/agents/specialists/discrete_math/boolean_algebra_agent.py`

**Service Registration:**
```python
service_type = 'math.discrete.boolean'
algorithm = 'quine_mccluskey'
tier = '3'
```

**Mathematical Rules (Native Implementation):**

```python
from typing import List, Set, Dict, Tuple, Any, Optional
from itertools import combinations

class BooleanAlgebra:
    """
    Native Boolean algebra operations and minimization.
    """

    # Boolean operations
    @staticmethod
    def AND(a: bool, b: bool) -> bool:
        return a and b

    @staticmethod
    def OR(a: bool, b: bool) -> bool:
        return a or b

    @staticmethod
    def NOT(a: bool) -> bool:
        return not a

    @staticmethod
    def XOR(a: bool, b: bool) -> bool:
        return a != b

    @staticmethod
    def NAND(a: bool, b: bool) -> bool:
        return not (a and b)

    @staticmethod
    def NOR(a: bool, b: bool) -> bool:
        return not (a or b)

    @staticmethod
    def IMPLIES(a: bool, b: bool) -> bool:
        return (not a) or b

    @staticmethod
    def IFF(a: bool, b: bool) -> bool:
        return a == b


class NormalForms:
    """
    Conversion to and from normal forms.
    """

    @staticmethod
    def to_minterm(term: int, n_vars: int) -> str:
        """
        Convert minterm number to expression.
        Minterm m_i = conjunction where variable is complemented if bit is 0.

        Example: minterm 5 with 3 vars (ABC) = 101 = A AND NOT(B) AND C
        """
        vars = [chr(ord('A') + i) for i in range(n_vars)]
        result = []
        for i in range(n_vars):
            bit = (term >> (n_vars - 1 - i)) & 1
            if bit:
                result.append(vars[i])
            else:
                result.append(f"NOT({vars[i]})")
        return " AND ".join(result)

    @staticmethod
    def to_maxterm(term: int, n_vars: int) -> str:
        """
        Convert maxterm number to expression.
        Maxterm M_i = disjunction where variable is complemented if bit is 1.

        Example: maxterm 5 with 3 vars (ABC) = 101 = NOT(A) OR B OR NOT(C)
        """
        vars = [chr(ord('A') + i) for i in range(n_vars)]
        result = []
        for i in range(n_vars):
            bit = (term >> (n_vars - 1 - i)) & 1
            if bit:
                result.append(f"NOT({vars[i]})")
            else:
                result.append(vars[i])
        return " OR ".join(result)

    @staticmethod
    def truth_table_to_dnf(minterms: List[int], n_vars: int) -> str:
        """
        Convert list of minterms (where function = 1) to DNF.
        DNF = disjunction of minterms.
        """
        if not minterms:
            return "FALSE"
        terms = [NormalForms.to_minterm(m, n_vars) for m in minterms]
        return " OR ".join(f"({t})" for t in terms)

    @staticmethod
    def truth_table_to_cnf(maxterms: List[int], n_vars: int) -> str:
        """
        Convert list of maxterms (where function = 0) to CNF.
        CNF = conjunction of maxterms.
        """
        if not maxterms:
            return "TRUE"
        terms = [NormalForms.to_maxterm(m, n_vars) for m in maxterms]
        return " AND ".join(f"({t})" for t in terms)


class QuineMcCluskey:
    """
    Quine-McCluskey algorithm for Boolean function minimization.

    Algorithm:
    1. Group minterms by number of 1s
    2. Combine adjacent groups (differ by 1 bit)
    3. Repeat until no more combinations
    4. Select essential prime implicants
    5. Cover remaining minterms
    """

    @staticmethod
    def minimize(minterms: List[int], dont_cares: List[int], n_vars: int) -> Dict[str, Any]:
        """
        Minimize Boolean function given minterms and don't cares.

        Args:
            minterms: List of minterm numbers where f=1
            dont_cares: List of don't care terms
            n_vars: Number of variables

        Returns:
            Dictionary with prime implicants, essential PIs, and minimal expression
        """
        all_terms = set(minterms) | set(dont_cares)

        # Step 1: Group by number of 1s
        def count_ones(n: int) -> int:
            return bin(n).count('1')

        def term_to_str(term: int, mask: int, n: int) -> str:
            """Convert term to string with dashes for combined bits."""
            result = []
            for i in range(n - 1, -1, -1):
                if (mask >> i) & 1:
                    result.append('-')
                elif (term >> i) & 1:
                    result.append('1')
                else:
                    result.append('0')
            return ''.join(result)

        # Initial: each minterm is (value, mask=0, covered_minterms)
        current = [(m, 0, frozenset([m])) for m in all_terms]
        prime_implicants = []

        while current:
            # Group by number of 1s
            groups = {}
            for term, mask, covered in current:
                ones = count_ones(term & ~mask)
                if ones not in groups:
                    groups[ones] = []
                groups[ones].append((term, mask, covered))

            next_round = []
            used = set()

            # Try to combine adjacent groups
            sorted_groups = sorted(groups.keys())
            for i in range(len(sorted_groups) - 1):
                g1, g2 = sorted_groups[i], sorted_groups[i + 1]
                if g2 - g1 != 1:
                    continue

                for t1, m1, c1 in groups[g1]:
                    for t2, m2, c2 in groups[g2]:
                        if m1 != m2:
                            continue

                        # Check if differ by exactly one bit
                        diff = (t1 ^ t2) & ~m1
                        if diff and (diff & (diff - 1)) == 0:  # Power of 2
                            # Can combine
                            new_term = t1 & t2
                            new_mask = m1 | diff
                            new_covered = c1 | c2

                            next_round.append((new_term, new_mask, new_covered))
                            used.add((t1, m1))
                            used.add((t2, m2))

            # Prime implicants are those not used in combination
            for term, mask, covered in current:
                if (term, mask) not in used:
                    prime_implicants.append((term, mask, covered))

            current = list(set(next_round))

        # Remove duplicates
        seen = set()
        unique_pis = []
        for term, mask, covered in prime_implicants:
            key = (term, mask)
            if key not in seen:
                seen.add(key)
                unique_pis.append((term, mask, covered))

        # Step 2: Find essential prime implicants
        # PI is essential if it's the only one covering some minterm
        minterm_set = set(minterms)
        essential = []
        covered_by = {m: [] for m in minterms}

        for idx, (term, mask, covered) in enumerate(unique_pis):
            for m in covered & minterm_set:
                covered_by[m].append(idx)

        essential_indices = set()
        for m, indices in covered_by.items():
            if len(indices) == 1:
                essential_indices.add(indices[0])

        essential = [unique_pis[i] for i in essential_indices]

        # Covered minterms
        covered_minterms = set()
        for _, _, covered in essential:
            covered_minterms |= (covered & minterm_set)

        # Step 3: Cover remaining (greedy)
        remaining = minterm_set - covered_minterms
        selected = list(essential)
        remaining_pis = [p for i, p in enumerate(unique_pis) if i not in essential_indices]

        while remaining:
            # Select PI that covers most remaining
            best_pi = None
            best_count = 0
            for pi in remaining_pis:
                count = len(pi[2] & remaining)
                if count > best_count:
                    best_count = count
                    best_pi = pi

            if best_pi:
                selected.append(best_pi)
                remaining -= best_pi[2]
                remaining_pis.remove(best_pi)
            else:
                break

        # Format output
        def pi_to_expr(term: int, mask: int, n: int) -> str:
            vars = [chr(ord('A') + i) for i in range(n)]
            parts = []
            for i in range(n):
                bit_pos = n - 1 - i
                if not ((mask >> bit_pos) & 1):  # Not a don't care
                    if (term >> bit_pos) & 1:
                        parts.append(vars[i])
                    else:
                        parts.append(f"{vars[i]}'")
            return ''.join(parts) if parts else '1'

        minimal_expr = ' + '.join(pi_to_expr(t, m, n_vars) for t, m, _ in selected)

        return {
            'prime_implicants': [(term_to_str(t, m, n_vars), list(c)) for t, m, c in unique_pis],
            'essential_prime_implicants': [(term_to_str(t, m, n_vars), list(c)) for t, m, c in essential],
            'minimal_expression': minimal_expr,
            'num_terms': len(selected),
            'method': 'quine_mccluskey'
        }


class KarnaughMap:
    """
    Karnaugh map for up to 4 variables.
    Primarily for visualization and education.
    """

    @staticmethod
    def generate_kmap(minterms: List[int], n_vars: int) -> Dict[str, Any]:
        """
        Generate Karnaugh map representation.

        Args:
            minterms: List of minterm numbers where f=1
            n_vars: Number of variables (2, 3, or 4)

        Returns:
            Dictionary with K-map grid and groupings
        """
        if n_vars < 2 or n_vars > 4:
            return {'error': 'K-map supports 2-4 variables'}

        minterm_set = set(minterms)

        if n_vars == 2:
            # 2x2 grid
            # Gray code order: 00, 01, 11, 10
            col_order = [0, 1]
            row_order = [0, 1]
            grid = [[1 if (r * 2 + c) in minterm_set else 0
                    for c in col_order] for r in row_order]

            return {
                'n_vars': 2,
                'row_labels': ['A=0', 'A=1'],
                'col_labels': ['B=0', 'B=1'],
                'grid': grid
            }

        elif n_vars == 3:
            # 2x4 grid with Gray code
            # Rows: A, Cols: BC
            row_order = [0, 1]
            col_order = [0, 1, 3, 2]  # Gray code: 00, 01, 11, 10

            grid = []
            for r in row_order:
                row = []
                for c in col_order:
                    term = r * 4 + c
                    row.append(1 if term in minterm_set else 0)
                grid.append(row)

            return {
                'n_vars': 3,
                'row_labels': ['A=0', 'A=1'],
                'col_labels': ['BC=00', 'BC=01', 'BC=11', 'BC=10'],
                'grid': grid
            }

        else:  # n_vars == 4
            # 4x4 grid with Gray code
            # Rows: AB, Cols: CD
            row_order = [0, 1, 3, 2]  # Gray code
            col_order = [0, 1, 3, 2]

            grid = []
            for r in row_order:
                row = []
                for c in col_order:
                    term = r * 4 + c
                    row.append(1 if term in minterm_set else 0)
                grid.append(row)

            return {
                'n_vars': 4,
                'row_labels': ['AB=00', 'AB=01', 'AB=11', 'AB=10'],
                'col_labels': ['CD=00', 'CD=01', 'CD=11', 'CD=10'],
                'grid': grid
            }
```

---

### 4. FiniteAutomataAgent (NEW - LOW PRIORITY)
**Estimated Score Impact:** +2 points

**Purpose:** Handle formal languages and automata theory.

**File Location:** `src/symbo_agentic_reasoners/agents/specialists/discrete_math/automata_agent.py`

**Service Registration:**
```python
service_type = 'math.discrete.automata'
algorithm = 'finite_state'
tier = '3'
```

**Mathematical Rules (Native Implementation):**

```python
from typing import Dict, Set, Tuple, List, Optional, Any
from collections import deque

class DFA:
    """
    Deterministic Finite Automaton.

    5-tuple: (Q, Sigma, delta, q0, F)
    - Q: Set of states
    - Sigma: Alphabet
    - delta: Transition function Q x Sigma -> Q
    - q0: Start state
    - F: Set of accepting states
    """

    def __init__(
        self,
        states: Set[str],
        alphabet: Set[str],
        transitions: Dict[Tuple[str, str], str],
        start_state: str,
        accept_states: Set[str]
    ):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def accepts(self, string: str) -> bool:
        """Check if DFA accepts the string."""
        current = self.start_state
        for symbol in string:
            if symbol not in self.alphabet:
                return False
            key = (current, symbol)
            if key not in self.transitions:
                return False
            current = self.transitions[key]
        return current in self.accept_states

    def minimize(self) -> 'DFA':
        """
        Minimize DFA using Hopcroft's algorithm.

        Algorithm:
        1. Remove unreachable states
        2. Partition states into equivalence classes
        3. Merge equivalent states
        """
        # Step 1: Find reachable states
        reachable = set()
        queue = deque([self.start_state])
        reachable.add(self.start_state)

        while queue:
            state = queue.popleft()
            for symbol in self.alphabet:
                key = (state, symbol)
                if key in self.transitions:
                    next_state = self.transitions[key]
                    if next_state not in reachable:
                        reachable.add(next_state)
                        queue.append(next_state)

        # Step 2: Table-filling algorithm for equivalence
        states = list(reachable)
        n = len(states)
        state_idx = {s: i for i, s in enumerate(states)}

        # Mark pairs as distinguishable
        distinguishable = [[False] * n for _ in range(n)]

        # Initial: accept vs non-accept
        for i in range(n):
            for j in range(i + 1, n):
                if (states[i] in self.accept_states) != (states[j] in self.accept_states):
                    distinguishable[i][j] = True
                    distinguishable[j][i] = True

        # Iterate until no changes
        changed = True
        while changed:
            changed = False
            for i in range(n):
                for j in range(i + 1, n):
                    if distinguishable[i][j]:
                        continue

                    for symbol in self.alphabet:
                        key_i = (states[i], symbol)
                        key_j = (states[j], symbol)

                        if key_i in self.transitions and key_j in self.transitions:
                            next_i = state_idx[self.transitions[key_i]]
                            next_j = state_idx[self.transitions[key_j]]

                            if distinguishable[next_i][next_j]:
                                distinguishable[i][j] = True
                                distinguishable[j][i] = True
                                changed = True
                                break

        # Step 3: Build equivalence classes
        # (Simplified: union-find would be more efficient)
        class_of = list(range(n))
        for i in range(n):
            for j in range(i + 1, n):
                if not distinguishable[i][j]:
                    # Merge classes
                    old_class = class_of[j]
                    new_class = class_of[i]
                    for k in range(n):
                        if class_of[k] == old_class:
                            class_of[k] = new_class

        # Build minimized DFA
        # Get unique class representatives
        class_repr = {}
        for i, c in enumerate(class_of):
            if c not in class_repr:
                class_repr[c] = states[i]

        new_states = set(class_repr.values())
        new_start = class_repr[class_of[state_idx[self.start_state]]]
        new_accept = {class_repr[class_of[state_idx[s]]] for s in self.accept_states if s in reachable}

        new_transitions = {}
        for (state, symbol), next_state in self.transitions.items():
            if state in reachable:
                new_from = class_repr[class_of[state_idx[state]]]
                new_to = class_repr[class_of[state_idx[next_state]]]
                new_transitions[(new_from, symbol)] = new_to

        return DFA(new_states, self.alphabet, new_transitions, new_start, new_accept)


class NFA:
    """
    Nondeterministic Finite Automaton with epsilon transitions.

    5-tuple: (Q, Sigma, delta, q0, F)
    - delta: Q x (Sigma U {epsilon}) -> P(Q)
    """

    EPSILON = ''  # Empty string represents epsilon

    def __init__(
        self,
        states: Set[str],
        alphabet: Set[str],
        transitions: Dict[Tuple[str, str], Set[str]],
        start_state: str,
        accept_states: Set[str]
    ):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

    def epsilon_closure(self, states: Set[str]) -> Set[str]:
        """Compute epsilon closure of a set of states."""
        closure = set(states)
        queue = deque(states)

        while queue:
            state = queue.popleft()
            key = (state, self.EPSILON)
            if key in self.transitions:
                for next_state in self.transitions[key]:
                    if next_state not in closure:
                        closure.add(next_state)
                        queue.append(next_state)

        return closure

    def accepts(self, string: str) -> bool:
        """Check if NFA accepts the string."""
        current = self.epsilon_closure({self.start_state})

        for symbol in string:
            next_states = set()
            for state in current:
                key = (state, symbol)
                if key in self.transitions:
                    next_states |= self.transitions[key]
            current = self.epsilon_closure(next_states)

        return bool(current & self.accept_states)

    def to_dfa(self) -> DFA:
        """
        Convert NFA to DFA using subset construction.
        """
        start_closure = self.epsilon_closure({self.start_state})
        start_name = self._set_to_name(start_closure)

        dfa_states = {start_name}
        dfa_transitions = {}
        dfa_accept = set()

        queue = deque([start_closure])
        processed = {frozenset(start_closure)}

        while queue:
            current_set = queue.popleft()
            current_name = self._set_to_name(current_set)

            if current_set & self.accept_states:
                dfa_accept.add(current_name)

            for symbol in self.alphabet:
                next_set = set()
                for state in current_set:
                    key = (state, symbol)
                    if key in self.transitions:
                        next_set |= self.transitions[key]
                next_set = self.epsilon_closure(next_set)

                if next_set:
                    next_name = self._set_to_name(next_set)
                    dfa_transitions[(current_name, symbol)] = next_name

                    if frozenset(next_set) not in processed:
                        processed.add(frozenset(next_set))
                        queue.append(next_set)
                        dfa_states.add(next_name)

        return DFA(dfa_states, self.alphabet, dfa_transitions, start_name, dfa_accept)

    def _set_to_name(self, state_set: Set[str]) -> str:
        """Convert set of states to a single state name."""
        return '{' + ','.join(sorted(state_set)) + '}'


class RegexToNFA:
    """
    Convert regular expression to NFA using Thompson's construction.

    Supported operators:
    - Concatenation (implicit)
    - Union |
    - Kleene star *
    - Kleene plus +
    - Optional ?
    - Parentheses ()
    """

    @staticmethod
    def convert(regex: str) -> NFA:
        """Convert regex to NFA."""
        # This is a simplified implementation
        # Full implementation would use proper parsing

        state_counter = [0]

        def new_state() -> str:
            s = f'q{state_counter[0]}'
            state_counter[0] += 1
            return s

        def build_single(char: str) -> Tuple[str, str, Dict]:
            """Build NFA for single character."""
            s = new_state()
            e = new_state()
            return (s, e, {(s, char): {e}})

        def build_concat(nfa1, nfa2) -> Tuple[str, str, Dict]:
            """Concatenate two NFAs."""
            s1, e1, t1 = nfa1
            s2, e2, t2 = nfa2

            # Connect e1 to s2 via epsilon
            transitions = {**t1, **t2}
            key = (e1, NFA.EPSILON)
            if key in transitions:
                transitions[key] = transitions[key] | {s2}
            else:
                transitions[key] = {s2}

            return (s1, e2, transitions)

        def build_union(nfa1, nfa2) -> Tuple[str, str, Dict]:
            """Union of two NFAs."""
            s1, e1, t1 = nfa1
            s2, e2, t2 = nfa2

            s = new_state()
            e = new_state()

            transitions = {**t1, **t2}
            transitions[(s, NFA.EPSILON)] = {s1, s2}

            key1 = (e1, NFA.EPSILON)
            key2 = (e2, NFA.EPSILON)
            transitions[key1] = transitions.get(key1, set()) | {e}
            transitions[key2] = transitions.get(key2, set()) | {e}

            return (s, e, transitions)

        def build_star(nfa1) -> Tuple[str, str, Dict]:
            """Kleene star."""
            s1, e1, t1 = nfa1

            s = new_state()
            e = new_state()

            transitions = {**t1}
            transitions[(s, NFA.EPSILON)] = {s1, e}

            key = (e1, NFA.EPSILON)
            transitions[key] = transitions.get(key, set()) | {s1, e}

            return (s, e, transitions)

        # Simple recursive descent parser would go here
        # For now, handle simple cases

        if len(regex) == 1 and regex.isalnum():
            s, e, t = build_single(regex)
            states = set(t.keys())
            states = {s for s, _ in t.keys()} | {s for targets in t.values() for s in targets}
            states.add(s)
            states.add(e)
            alphabet = {regex}
            return NFA(states, alphabet, t, s, {e})

        # Placeholder for complex regex
        return NFA({'q0', 'q1'}, set(regex), {}, 'q0', {'q1'})


class GrammarOperations:
    """
    Operations on context-free grammars.
    """

    @staticmethod
    def is_regular(grammar: Dict[str, List[str]]) -> bool:
        """
        Check if grammar is regular (right-linear or left-linear).

        Right-linear: A -> aB or A -> a or A -> epsilon
        Left-linear: A -> Ba or A -> a or A -> epsilon
        """
        # Determine direction
        right_linear = True
        left_linear = True

        for lhs, productions in grammar.items():
            for prod in productions:
                if prod == '':  # epsilon
                    continue

                # Check right-linear: terminal* followed by optional non-terminal
                has_non_terminal = False
                non_terminal_pos = -1

                for i, symbol in enumerate(prod):
                    if symbol.isupper():
                        if has_non_terminal:
                            right_linear = False
                            left_linear = False
                        else:
                            has_non_terminal = True
                            non_terminal_pos = i

                if has_non_terminal:
                    if non_terminal_pos != len(prod) - 1:
                        right_linear = False
                    if non_terminal_pos != 0:
                        left_linear = False

        return right_linear or left_linear

    @staticmethod
    def remove_epsilon_productions(grammar: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Remove epsilon productions from CFG."""
        # Find nullable non-terminals
        nullable = set()
        changed = True

        while changed:
            changed = False
            for lhs, productions in grammar.items():
                if lhs in nullable:
                    continue
                for prod in productions:
                    if prod == '' or all(s in nullable for s in prod if s.isupper()):
                        nullable.add(lhs)
                        changed = True
                        break

        # Generate new productions
        new_grammar = {}

        for lhs, productions in grammar.items():
            new_prods = set()
            for prod in productions:
                if prod == '':
                    continue

                # Find positions of nullable non-terminals
                nullable_positions = [i for i, s in enumerate(prod) if s.isupper() and s in nullable]

                # Generate all combinations
                from itertools import combinations
                for r in range(len(nullable_positions) + 1):
                    for combo in combinations(nullable_positions, r):
                        new_prod = ''.join(s for i, s in enumerate(prod) if i not in combo)
                        if new_prod:
                            new_prods.add(new_prod)

            new_grammar[lhs] = list(new_prods)

        return new_grammar
```

---

## Enhancements to Existing Specialists

### Enhancement 1: CombinatoricsAgent Upgrade

**Additional Algorithms:**

```python
# Add to combinatorics_agent.py

def stirling_first(n: int, k: int) -> int:
    """
    Stirling number of the first kind s(n,k).
    Number of permutations of n elements with k cycles.

    Recurrence: s(n,k) = s(n-1,k-1) - (n-1)*s(n-1,k)
    """
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    if k > n:
        return 0

    # Use DP
    dp = [[0] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 1

    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            dp[i][j] = dp[i-1][j-1] - (i-1) * dp[i-1][j]

    return abs(dp[n][k])  # Unsigned Stirling

def stirling_second(n: int, k: int) -> int:
    """
    Stirling number of the second kind S(n,k).
    Number of ways to partition n elements into k non-empty subsets.

    Recurrence: S(n,k) = k*S(n-1,k) + S(n-1,k-1)
    """
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0
    if k > n:
        return 0

    dp = [[0] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 1

    for i in range(1, n + 1):
        for j in range(1, min(i, k) + 1):
            dp[i][j] = j * dp[i-1][j] + dp[i-1][j-1]

    return dp[n][k]

def catalan(n: int) -> int:
    """
    Catalan number C_n.

    C_n = (2n)! / ((n+1)! * n!) = binomial(2n, n) / (n+1)

    Applications:
    - Number of valid parentheses sequences
    - Number of full binary trees with n+1 leaves
    - Number of paths on grid that don't cross diagonal
    """
    return binomial(2*n, n) // (n + 1)

def bell(n: int) -> int:
    """
    Bell number B_n.
    Total number of ways to partition n elements.

    B_n = sum_{k=0}^{n} S(n,k) where S is Stirling second kind
    """
    return sum(stirling_second(n, k) for k in range(n + 1))

def partition_count(n: int) -> int:
    """
    Number of integer partitions of n.

    Uses recurrence based on pentagonal number theorem.
    """
    if n < 0:
        return 0
    if n == 0:
        return 1

    # Use dynamic programming
    p = [0] * (n + 1)
    p[0] = 1

    for i in range(1, n + 1):
        k = 1
        while True:
            # Generalized pentagonal numbers: k(3k-1)/2 and k(3k+1)/2
            pent1 = k * (3 * k - 1) // 2
            pent2 = k * (3 * k + 1) // 2

            if pent1 > i:
                break

            sign = 1 if k % 2 == 1 else -1
            p[i] += sign * p[i - pent1]

            if pent2 <= i:
                p[i] += sign * p[i - pent2]

            k += 1

    return p[n]

def derangements(n: int) -> int:
    """
    Number of derangements D_n (permutations with no fixed points).

    D_n = n! * sum_{k=0}^{n} (-1)^k / k!
    D_n = (n-1) * (D_{n-1} + D_{n-2})
    """
    if n == 0:
        return 1
    if n == 1:
        return 0

    prev2, prev1 = 1, 0
    for i in range(2, n + 1):
        curr = (i - 1) * (prev1 + prev2)
        prev2, prev1 = prev1, curr

    return prev1

def multinomial(n: int, groups: List[int]) -> int:
    """
    Multinomial coefficient: n! / (k1! * k2! * ... * km!)

    Number of ways to partition n elements into groups of sizes k1, k2, ...
    """
    if sum(groups) != n:
        raise ValueError("Group sizes must sum to n")

    result = factorial(n)
    for k in groups:
        result //= factorial(k)
    return result

def inclusion_exclusion(sets: List[Set]) -> int:
    """
    Compute |A1 U A2 U ... U An| using inclusion-exclusion.

    |A1 U ... U An| = sum |Ai| - sum |Ai n Aj| + sum |Ai n Aj n Ak| - ...
    """
    n = len(sets)
    total = 0

    for r in range(1, n + 1):
        for combo in combinations(range(n), r):
            intersection = sets[combo[0]]
            for idx in combo[1:]:
                intersection = intersection & sets[idx]

            if r % 2 == 1:
                total += len(intersection)
            else:
                total -= len(intersection)

    return total
```

### Enhancement 2: GraphTheoryAgent Upgrade

**Additional Algorithms:**

```python
# Add to graph_theory_agent.py

def prim_mst(graph: Dict[int, List[Tuple[int, float]]]) -> List[Tuple[int, int, float]]:
    """
    Prim's algorithm for Minimum Spanning Tree.

    Args:
        graph: Adjacency list {node: [(neighbor, weight), ...]}

    Returns:
        List of edges (u, v, weight) in MST
    """
    import heapq

    if not graph:
        return []

    start = next(iter(graph))
    visited = {start}
    edges = []
    mst = []

    # Add all edges from start to heap
    for neighbor, weight in graph[start]:
        heapq.heappush(edges, (weight, start, neighbor))

    while edges and len(visited) < len(graph):
        weight, u, v = heapq.heappop(edges)

        if v in visited:
            continue

        visited.add(v)
        mst.append((u, v, weight))

        for neighbor, w in graph.get(v, []):
            if neighbor not in visited:
                heapq.heappush(edges, (w, v, neighbor))

    return mst

def kruskal_mst(nodes: Set[int], edges: List[Tuple[int, int, float]]) -> List[Tuple[int, int, float]]:
    """
    Kruskal's algorithm for Minimum Spanning Tree.

    Uses Union-Find for cycle detection.
    """
    # Union-Find
    parent = {n: n for n in nodes}
    rank = {n: 0 for n in nodes}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False
        if rank[px] < rank[py]:
            parent[px] = py
        elif rank[px] > rank[py]:
            parent[py] = px
        else:
            parent[py] = px
            rank[px] += 1
        return True

    # Sort edges by weight
    sorted_edges = sorted(edges, key=lambda e: e[2])

    mst = []
    for u, v, w in sorted_edges:
        if union(u, v):
            mst.append((u, v, w))
            if len(mst) == len(nodes) - 1:
                break

    return mst

def topological_sort(graph: Dict[int, List[int]]) -> Optional[List[int]]:
    """
    Topological sort using Kahn's algorithm.

    Returns None if cycle detected (not a DAG).
    """
    # Compute in-degrees
    in_degree = {n: 0 for n in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] = in_degree.get(neighbor, 0) + 1

    # Start with nodes having no incoming edges
    queue = deque([n for n in graph if in_degree[n] == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(graph):
        return None  # Cycle detected

    return result

def tarjan_scc(graph: Dict[int, List[int]]) -> List[Set[int]]:
    """
    Tarjan's algorithm for Strongly Connected Components.
    """
    index_counter = [0]
    index = {}
    lowlink = {}
    on_stack = {}
    stack = []
    sccs = []

    def strongconnect(v):
        index[v] = index_counter[0]
        lowlink[v] = index_counter[0]
        index_counter[0] += 1
        on_stack[v] = True
        stack.append(v)

        for w in graph.get(v, []):
            if w not in index:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack.get(w, False):
                lowlink[v] = min(lowlink[v], index[w])

        if lowlink[v] == index[v]:
            scc = set()
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.add(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in graph:
        if v not in index:
            strongconnect(v)

    return sccs

def is_bipartite(graph: Dict[int, List[int]]) -> Tuple[bool, Optional[Tuple[Set, Set]]]:
    """
    Check if graph is bipartite using BFS coloring.

    Returns (is_bipartite, (set1, set2) or None)
    """
    color = {}

    for start in graph:
        if start in color:
            continue

        queue = deque([start])
        color[start] = 0

        while queue:
            node = queue.popleft()
            for neighbor in graph.get(node, []):
                if neighbor not in color:
                    color[neighbor] = 1 - color[node]
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:
                    return (False, None)

    set0 = {n for n, c in color.items() if c == 0}
    set1 = {n for n, c in color.items() if c == 1}

    return (True, (set0, set1))

def chromatic_number_upper_bound(graph: Dict[int, List[int]]) -> int:
    """
    Greedy coloring gives upper bound on chromatic number.
    """
    color = {}

    for node in graph:
        neighbor_colors = {color[n] for n in graph.get(node, []) if n in color}

        # Find smallest available color
        c = 0
        while c in neighbor_colors:
            c += 1
        color[node] = c

    return max(color.values()) + 1 if color else 0

def has_eulerian_path(graph: Dict[int, List[int]]) -> Tuple[bool, Optional[str]]:
    """
    Check if graph has Eulerian path.

    Eulerian path exists iff:
    - Undirected: All vertices have even degree, or exactly 2 have odd degree
    - Directed: At most 1 vertex with out-in=1, at most 1 with in-out=1, rest equal
    """
    # Compute degrees
    degree = {}
    for node in graph:
        degree[node] = degree.get(node, 0) + len(graph[node])
        for neighbor in graph[node]:
            degree[neighbor] = degree.get(neighbor, 0) + 1

    odd_degree = [n for n, d in degree.items() if d % 2 == 1]

    if len(odd_degree) == 0:
        return (True, 'eulerian_circuit')
    elif len(odd_degree) == 2:
        return (True, 'eulerian_path')
    else:
        return (False, None)

def has_hamiltonian_path(graph: Dict[int, List[int]]) -> bool:
    """
    Check if graph has Hamiltonian path (visits every vertex exactly once).

    NP-complete - uses backtracking with pruning.
    """
    n = len(graph)
    if n == 0:
        return False

    def backtrack(path: List[int], visited: Set[int]) -> bool:
        if len(path) == n:
            return True

        current = path[-1]
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                if backtrack(path, visited):
                    return True
                path.pop()
                visited.remove(neighbor)

        return False

    for start in graph:
        if backtrack([start], {start}):
            return True

    return False
```

---

## Implementation Roadmap

### Phase 1: High Priority (Weeks 1-2)
**Target: +7 points**

1. **SetTheoryAgent** (+4 points)
   - Day 1-2: Implement `NativeSetOperations`
   - Day 3-4: Implement `RelationOperations`
   - Day 5: Implement `FunctionOperations`
   - Day 6-7: Agent wrapper, BDI integration, tests

2. **CombinatoricsAgent Enhancement** (+3 points)
   - Day 8-9: Add Stirling numbers, Catalan, Bell numbers
   - Day 10: Add partition count, derangements
   - Day 11-12: Add multinomial, inclusion-exclusion
   - Day 13-14: Integration tests, supervisor update

### Phase 2: Medium Priority (Weeks 3-4)
**Target: +6 points**

3. **RecurrenceRelationAgent** (+3 points)
   - Day 15-17: Characteristic equation solver
   - Day 18-19: Master theorem, sequence recognition
   - Day 20-21: Agent wrapper, tests

4. **BooleanAlgebraAgent** (+3 points)
   - Day 22-24: Quine-McCluskey implementation
   - Day 25-26: Karnaugh map generation
   - Day 27-28: Agent wrapper, tests

### Phase 3: Lower Priority (Weeks 5-6)
**Target: +2 points**

5. **GraphTheoryAgent Enhancement** (+1 point)
   - Day 29-30: MST algorithms (Prim, Kruskal)
   - Day 31: Topological sort, SCC
   - Day 32: Bipartite check, coloring

6. **FiniteAutomataAgent** (+1 point)
   - Day 33-35: DFA, NFA implementation
   - Day 36-37: NFA to DFA conversion
   - Day 38-40: Regex to NFA, grammar operations

---

## Supervisor Updates Required

### DiscreteMathSupervisor Modifications

```python
# Update discrete_math_supervisor.py

# Add new routing keywords
SET_KEYWORDS = [
    'set', 'union', 'intersection', 'subset', 'powerset',
    'relation', 'equivalence', 'partial order', 'reflexive',
    'symmetric', 'transitive', 'cartesian product', 'function',
    'injective', 'surjective', 'bijective', 'domain', 'range'
]

RECURRENCE_KEYWORDS = [
    'recurrence', 'recursive', 'fibonacci', 'sequence',
    'master theorem', 'divide and conquer', 'closed form',
    'characteristic equation', 'homogeneous', 'linear recurrence'
]

BOOLEAN_KEYWORDS = [
    'boolean', 'karnaugh', 'k-map', 'minterm', 'maxterm',
    'dnf', 'cnf', 'minimize', 'prime implicant', 'quine',
    'logic gate', 'nand', 'nor', 'xor'
]

AUTOMATA_KEYWORDS = [
    'automaton', 'automata', 'dfa', 'nfa', 'regex',
    'regular expression', 'finite state', 'grammar',
    'language', 'accept', 'transition'
]

def _analyze_task(self, task_entry):
    # ... existing code ...

    # Add new routing paths
    if any(kw in raw_input for kw in SET_KEYWORDS):
        return {
            'target': 'Set Theory Agent',
            'service_type': 'math.discrete.sets',
            'reason': 'Detected set theory keywords'
        }

    if any(kw in raw_input for kw in RECURRENCE_KEYWORDS):
        return {
            'target': 'Recurrence Relation Agent',
            'service_type': 'math.discrete.recurrence',
            'reason': 'Detected recurrence relation keywords'
        }

    if any(kw in raw_input for kw in BOOLEAN_KEYWORDS):
        return {
            'target': 'Boolean Algebra Agent',
            'service_type': 'math.discrete.boolean',
            'reason': 'Detected boolean algebra keywords'
        }

    if any(kw in raw_input for kw in AUTOMATA_KEYWORDS):
        return {
            'target': 'Finite Automata Agent',
            'service_type': 'math.discrete.automata',
            'reason': 'Detected automata/formal language keywords'
        }

    # ... existing routing ...
```

---

## Testing Strategy

### Unit Tests for Each New Agent

```python
# tests/test_discrete_math_new_agents.py

class TestSetTheoryAgent:
    def test_basic_operations(self):
        agent = SetTheoryAgent()
        A = frozenset({1, 2, 3})
        B = frozenset({2, 3, 4})

        assert NativeSetOperations.union(A, B) == frozenset({1, 2, 3, 4})
        assert NativeSetOperations.intersection(A, B) == frozenset({2, 3})
        assert NativeSetOperations.difference(A, B) == frozenset({1})

    def test_power_set(self):
        A = frozenset({1, 2})
        ps = NativeSetOperations.power_set(A)
        assert len(ps) == 4

    def test_equivalence_relation(self):
        # Congruence mod 3 on {0,1,2,3,4,5}
        R = frozenset((a, b) for a in range(6) for b in range(6) if a % 3 == b % 3)
        A = frozenset(range(6))
        assert RelationOperations.is_equivalence_relation(R, A)

class TestRecurrenceAgent:
    def test_fibonacci(self):
        result = RecurrenceSolver.solve_linear_homogeneous([1, 1], [0, 1])
        # Verify first few terms
        for n in range(10):
            fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34][n]
            assert abs(result['closed_form'](n) - fib) < 0.001

    def test_master_theorem(self):
        # Merge sort: T(n) = 2T(n/2) + n
        result = RecurrenceSolver.solve_divide_and_conquer(2, 2, 'n')
        assert result['master_theorem_case'] == 2
        assert 'log' in result['complexity']

class TestBooleanAlgebraAgent:
    def test_quine_mccluskey(self):
        # f(A,B,C) = sum(0,1,2,5,6,7)
        result = QuineMcCluskey.minimize([0, 1, 2, 5, 6, 7], [], 3)
        assert result['num_terms'] <= 3

    def test_karnaugh(self):
        kmap = KarnaughMap.generate_kmap([0, 1, 3], 2)
        assert kmap['grid'][0][0] == 1  # minterm 0
        assert kmap['grid'][0][1] == 1  # minterm 1
```

---

## Expected Score Breakdown

| Component | Current | After Phase 1 | After Phase 2 | After Phase 3 |
|-----------|---------|---------------|---------------|---------------|
| Combinatorics | 40% | 55% | 60% | 65% |
| Graph Theory | 50% | 50% | 55% | 65% |
| Set Theory | 0% | 70% | 75% | 80% |
| Recurrence | 0% | 0% | 60% | 70% |
| Boolean Algebra | 30% | 30% | 65% | 70% |
| Automata | 0% | 0% | 0% | 40% |
| **Overall** | **55** | **62** | **68** | **70** |

---

## File Structure Summary

```
src/symbo_agentic_reasoners/agents/specialists/discrete_math/
    __init__.py                    # UPDATE: Export new agents
    combinatorics_agent.py         # ENHANCE: Add advanced counting
    graph_theory_agent.py          # ENHANCE: Add MST, SCC, etc.
    set_theory_agent.py            # NEW: Set operations
    recurrence_agent.py            # NEW: Recurrence solving
    boolean_algebra_agent.py       # NEW: Boolean minimization
    automata_agent.py              # NEW: Finite automata

src/symbo_agentic_reasoners/agents/supervisors/
    discrete_math_supervisor.py    # UPDATE: Add new routing

tests/
    test_discrete_math_specialists.py  # NEW: Comprehensive tests
```

---

## Conclusion

This improvement plan addresses the discrete mathematics coverage gaps through:

1. **4 New Specialists**: SetTheoryAgent, RecurrenceRelationAgent, BooleanAlgebraAgent, FiniteAutomataAgent
2. **2 Enhanced Specialists**: CombinatoricsAgent and GraphTheoryAgent upgrades
3. **All Native Implementations**: No SymPy or external symbolic libraries

The phased approach prioritizes high-impact improvements (Set Theory, advanced Combinatorics) while building toward comprehensive coverage of discrete mathematics subdisciplines.

**Expected Outcome**: Discrete Math score improves from 55/100 to 70/100 (+27%)
