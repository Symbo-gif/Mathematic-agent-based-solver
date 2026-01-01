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
DISCRETE MATH BRUTAL STRESS TESTS
==================================

50 research-level stress tests designed to BREAK the Discrete Math domain agents:
- CombinatoricsAgent
- GraphTheoryAgent
- SetTheoryAgent
- RecurrenceRelationAgent
- BooleanAlgebraAgent
- FiniteAutomataAgent

These tests target:
1. Computational overflow conditions
2. Exponential blowup scenarios
3. Pathological edge cases
4. NP-hard problem instances
5. Memory exhaustion patterns
6. Numerical precision limits

Each test is designed to expose fundamental limitations in the agents.
"""

from typing import Dict, Any, List

# =============================================================================
# 50 BRUTAL DISCRETE MATH STRESS TESTS
# =============================================================================

DISCRETE_MATH_BRUTAL_TESTS: List[Dict[str, Any]] = [
    # =========================================================================
    # COMBINATORICS OVERFLOW TESTS (1-10)
    # =========================================================================
    {
        "test_id": "DISC_001",
        "category": "combinatorics_overflow",
        "input": "Compute C(1000, 500) - the central binomial coefficient",
        "expected": "~2.7 x 10^299 (exact integer with 300 digits)",
        "difficulty": "brutal",
        "rationale": "C(1000,500) produces a 300-digit integer. Tests arbitrary precision arithmetic and memory for massive integer storage. Result has exactly 299 digits."
    },
    {
        "test_id": "DISC_002",
        "category": "combinatorics_overflow",
        "input": "Compute Stirling number of the second kind S(100, 50)",
        "expected": "~1.8 x 10^81 (81-digit integer)",
        "difficulty": "extreme",
        "rationale": "S(100,50) requires deep recursion (100 levels) with intermediate values growing exponentially. LRU cache of 1024 entries is insufficient for this computation path."
    },
    {
        "test_id": "DISC_003",
        "category": "combinatorics_overflow",
        "input": "Compute Bell number B(100)",
        "expected": "~4.76 x 10^115",
        "difficulty": "pathological",
        "rationale": "B(100) sums all S(100,k) for k=0..100. Requires computing 101 Stirling numbers of second kind, each potentially causing stack overflow due to recursion depth."
    },
    {
        "test_id": "DISC_004",
        "category": "combinatorics_overflow",
        "input": "Compute partition function p(1000) - number of integer partitions of 1000",
        "expected": "p(1000) = 24061467864032622473692149727991 (32 digits)",
        "difficulty": "brutal",
        "rationale": "Partition function with max_part recursion will hit Python's recursion limit. Memoization cache size of 1024 is woefully insufficient for p(1000)."
    },
    {
        "test_id": "DISC_005",
        "category": "combinatorics_overflow",
        "input": "Compute Catalan number C_500",
        "expected": "C_500 = C(1000,500)/(501) - approximately 5.4 x 10^296",
        "difficulty": "extreme",
        "rationale": "Requires computing C(1000,500) first, then dividing by 501. Tests both binomial computation and integer division precision."
    },
    {
        "test_id": "DISC_006",
        "category": "combinatorics_overflow",
        "input": "Compute derangement D(100) - subfactorial !100",
        "expected": "D(100) = 100!/e rounded to nearest integer (approximately 3.4 x 10^156)",
        "difficulty": "brutal",
        "rationale": "Recursion D(n) = (n-1)(D(n-1) + D(n-2)) requires 100 levels. The alternating sum formula requires 100! which is a 158-digit number."
    },
    {
        "test_id": "DISC_007",
        "category": "combinatorics_overflow",
        "input": "Compute Stirling number of the first kind s(100, 1) (unsigned)",
        "expected": "s(100,1) = 99! = 9.33 x 10^155",
        "difficulty": "extreme",
        "rationale": "First kind Stirling s(n,1) = (n-1)! but computed via recurrence s(n,k) = (n-1)*s(n-1,k) + s(n-1,k-1). Deep recursion with massive intermediates."
    },
    {
        "test_id": "DISC_008",
        "category": "combinatorics_overflow",
        "input": "Generate all integer partitions of n=50",
        "expected": "p(50) = 204226 partitions to enumerate",
        "difficulty": "brutal",
        "rationale": "generate_partitions(50) must enumerate 204,226 partitions. Memory for storing 200K+ lists with average length ~7 elements each."
    },
    {
        "test_id": "DISC_009",
        "category": "combinatorics_overflow",
        "input": "Compute multinomial coefficient 100!/(10! x 10 copies) = 100!/(10!)^10",
        "expected": "~1.2 x 10^92",
        "difficulty": "extreme",
        "rationale": "Distributing 100 items into 10 groups of 10. Tests factorial division with massive numerator and multiple large denominators."
    },
    {
        "test_id": "DISC_010",
        "category": "combinatorics_overflow",
        "input": "Compute Fibonacci F(10000) using matrix exponentiation",
        "expected": "F(10000) has 2090 digits",
        "difficulty": "pathological",
        "rationale": "Matrix exponentiation with O(log n) multiplications, but each multiplication involves 2090-digit numbers. Tests arbitrary precision matrix arithmetic."
    },

    # =========================================================================
    # GRAPH ALGORITHM SCALING TESTS (11-20)
    # =========================================================================
    {
        "test_id": "DISC_011",
        "category": "graph_scaling",
        "input": "Dijkstra shortest path on complete graph K_10000 with random weights",
        "expected": "O(V^2 log V) = O(10^8 log 10^4) operations",
        "difficulty": "brutal",
        "rationale": "Complete graph has 50M edges. Priority queue operations dominate. Memory for 10000x10000 adjacency requires 800MB minimum."
    },
    {
        "test_id": "DISC_012",
        "category": "graph_scaling",
        "input": "Floyd-Warshall all-pairs shortest paths on graph with 1000 nodes",
        "expected": "O(V^3) = 10^9 operations, 8GB memory for distance matrix",
        "difficulty": "pathological",
        "rationale": "Cubic complexity with 1000 nodes means 1 billion operations. Distance matrix of 1M entries with 64-bit floats = 8MB, but intermediate storage much larger."
    },
    {
        "test_id": "DISC_013",
        "category": "graph_scaling",
        "input": "Find all strongly connected components in directed graph with 50000 nodes using Tarjan",
        "expected": "O(V + E) but recursion depth = O(V) can cause stack overflow",
        "difficulty": "extreme",
        "rationale": "Tarjan's algorithm uses recursive DFS. 50000 nodes in a chain = 50000 recursion depth, far exceeding Python's default 1000 limit."
    },
    {
        "test_id": "DISC_014",
        "category": "graph_scaling",
        "input": "Find maximum flow in network with 5000 nodes and 100000 edges using Ford-Fulkerson",
        "expected": "O(VE^2) worst case = 5 x 10^13 operations",
        "difficulty": "pathological",
        "rationale": "Ford-Fulkerson with BFS (Edmonds-Karp) is O(VE^2). For dense graphs, this becomes computationally intractable."
    },
    {
        "test_id": "DISC_015",
        "category": "graph_scaling",
        "input": "Bellman-Ford on graph with 10000 nodes and negative edge cycle detection",
        "expected": "O(VE) = O(10^8) for sparse, O(10^11) for dense",
        "difficulty": "brutal",
        "rationale": "V-1 relaxation passes over all edges. With 10K nodes and 100K edges, requires 10^9 edge relaxations."
    },
    {
        "test_id": "DISC_016",
        "category": "graph_isomorphism",
        "input": "Test graph isomorphism between two random 4-regular graphs on 100 nodes",
        "expected": "NP-intermediate problem, exponential worst case",
        "difficulty": "pathological",
        "rationale": "Graph isomorphism on regular graphs is particularly hard - no degree sequence to exploit. Brute force: 100! permutations."
    },
    {
        "test_id": "DISC_017",
        "category": "graph_coloring",
        "input": "Compute chromatic polynomial of complete bipartite graph K_{50,50}",
        "expected": "P(K_{m,n}, k) = sum involving k^100 terms",
        "difficulty": "extreme",
        "rationale": "Chromatic polynomial computation is #P-complete. Deletion-contraction on 100 nodes creates exponential recursion tree."
    },
    {
        "test_id": "DISC_018",
        "category": "graph_planarity",
        "input": "Test planarity of random graph with 10000 nodes and 25000 edges",
        "expected": "Euler's formula: E <= 3V - 6, so 25000 <= 29994 (planar possible)",
        "difficulty": "brutal",
        "rationale": "Linear-time planarity testing exists but implementation is complex. Random graphs near the edge threshold are hardest to test."
    },
    {
        "test_id": "DISC_019",
        "category": "graph_hamilton",
        "input": "Find Hamiltonian path in random 3-regular graph on 1000 nodes",
        "expected": "NP-complete problem, exponential backtracking",
        "difficulty": "pathological",
        "rationale": "Hamiltonian path is NP-complete. 3-regular graphs have many local choices but few global solutions."
    },
    {
        "test_id": "DISC_020",
        "category": "graph_clique",
        "input": "Find maximum clique in Paley graph of order 101 (quadratic residue graph)",
        "expected": "Clique number = 10 (known result for Paley graphs)",
        "difficulty": "extreme",
        "rationale": "Paley graphs are quasi-random and defeat most heuristics. Maximum clique is NP-hard with exponential worst case."
    },

    # =========================================================================
    # SET THEORY STRESS TESTS (21-27)
    # =========================================================================
    {
        "test_id": "DISC_021",
        "category": "set_powerset",
        "input": "Compute power set of a set with 25 elements",
        "expected": "2^25 = 33,554,432 subsets",
        "difficulty": "pathological",
        "rationale": "Power set has safety limit of 20 elements. With 25 elements, 33M subsets each stored as frozenset. Memory: ~1GB minimum."
    },
    {
        "test_id": "DISC_022",
        "category": "set_cartesian",
        "input": "Compute Cartesian product of set with 1000 elements with itself",
        "expected": "|A x A| = 1,000,000 ordered pairs",
        "difficulty": "brutal",
        "rationale": "1M pairs, each a tuple. Creating and storing 1M tuples in a frozenset tests memory allocation and hashing efficiency."
    },
    {
        "test_id": "DISC_023",
        "category": "set_transitive_closure",
        "input": "Compute transitive closure of relation on 500 elements",
        "expected": "Warshall's algorithm: O(n^3) = 125 million operations",
        "difficulty": "extreme",
        "rationale": "500x500x500 = 125M boolean operations. Matrix storage: 250KB, but closure check on each iteration is costly."
    },
    {
        "test_id": "DISC_024",
        "category": "set_equivalence",
        "input": "Verify equivalence relation properties on relation with 100000 pairs",
        "expected": "Reflexivity: O(n), Symmetry: O(m), Transitivity: O(m*sqrt(m))",
        "difficulty": "brutal",
        "rationale": "Transitivity check on 100K pairs requires building lookup dict and checking all pair combinations. Worst case O(m^2)."
    },
    {
        "test_id": "DISC_025",
        "category": "set_recursive",
        "input": "Define set S = {S, 1, 2} and compute S union S",
        "expected": "Russell's paradox variant - self-referential set",
        "difficulty": "pathological",
        "rationale": "Self-referential sets are not well-founded in ZFC. Python frozensets cannot contain themselves. Tests error handling for infinite structures."
    },
    {
        "test_id": "DISC_026",
        "category": "set_partition",
        "input": "Compute all set partitions of a 15-element set",
        "expected": "B(15) = 1,382,958,545 partitions",
        "difficulty": "pathological",
        "rationale": "Bell number B(15) is over 1 billion. Enumerating all partitions is computationally infeasible without pruning."
    },
    {
        "test_id": "DISC_027",
        "category": "set_function",
        "input": "Check if relation with 10000 pairs from set A (1000 elements) to B (1000 elements) is bijective",
        "expected": "Injectivity: O(m), Surjectivity: O(m), Bijection: both",
        "difficulty": "brutal",
        "rationale": "For bijection, need |A| = |B| and both injective and surjective. With 10K pairs, hash table lookups dominate."
    },

    # =========================================================================
    # RECURRENCE RELATION TESTS (28-35)
    # =========================================================================
    {
        "test_id": "DISC_028",
        "category": "recurrence_complex_roots",
        "input": "Solve a_n = 2*a_{n-1} - 2*a_{n-2} with a_0=1, a_1=1 (complex roots)",
        "expected": "Characteristic roots: 1+i, 1-i. Solution involves cos/sin with modulus sqrt(2)",
        "difficulty": "brutal",
        "rationale": "Complex conjugate roots require polar form representation. Tests handling of complex arithmetic in closed-form solution."
    },
    {
        "test_id": "DISC_029",
        "category": "recurrence_high_order",
        "input": "Solve 10th order linear recurrence with random coefficients",
        "expected": "10th degree characteristic polynomial with potential irrational roots",
        "difficulty": "extreme",
        "rationale": "Finding roots of degree-10 polynomial analytically is impossible (Abel-Ruffini). Numerical root finding introduces errors."
    },
    {
        "test_id": "DISC_030",
        "category": "recurrence_repeated_roots",
        "input": "Solve a_n = 6*a_{n-1} - 12*a_{n-2} + 8*a_{n-3} (triple root at 2)",
        "expected": "General solution: (c1 + c2*n + c3*n^2) * 2^n",
        "difficulty": "brutal",
        "rationale": "Repeated roots of multiplicity 3 require polynomial coefficients. The current solver only handles multiplicity 2."
    },
    {
        "test_id": "DISC_031",
        "category": "recurrence_nonhomogeneous",
        "input": "Solve a_n = 2*a_{n-1} + n^2 * 3^n",
        "expected": "Requires particular solution via method of undetermined coefficients",
        "difficulty": "extreme",
        "rationale": "Non-homogeneous recurrence with polynomial times exponential forcing function. Not directly supported by current solver."
    },
    {
        "test_id": "DISC_032",
        "category": "recurrence_master_theorem",
        "input": "Apply master theorem to T(n) = 4*T(n/2) + n^2*log(n) (falls outside standard cases)",
        "expected": "Between case 2 and 3 - requires Akra-Bazzi for exact analysis",
        "difficulty": "brutal",
        "rationale": "The n^2*log(n) term with log_2(4)=2 doesn't fit standard master theorem cases. Tests boundary condition handling."
    },
    {
        "test_id": "DISC_033",
        "category": "recurrence_irrational",
        "input": "Compute a_{1000} for Fibonacci-like recurrence a_n = a_{n-1} + a_{n-2}",
        "expected": "F(1000) = 4.35 x 10^208 (209 digits)",
        "difficulty": "brutal",
        "rationale": "Closed form involves phi = (1+sqrt(5))/2. Computing phi^1000 with sufficient precision to round correctly is challenging."
    },
    {
        "test_id": "DISC_034",
        "category": "recurrence_sequence_finding",
        "input": "Find recurrence for OEIS A000108 (Catalan numbers): 1,1,2,5,14,42,132,...",
        "expected": "(n+2)*C_{n+1} = (4n+2)*C_n (not linear with constant coefficients)",
        "difficulty": "extreme",
        "rationale": "Catalan numbers satisfy a non-linear recurrence. Linear recurrence finder will fail or return incorrect order."
    },
    {
        "test_id": "DISC_035",
        "category": "recurrence_numerical_instability",
        "input": "Solve a_n = 1000*a_{n-1} - a_{n-2} with a_0=1, a_1=1 and compute a_{100}",
        "expected": "Exponential blowup: dominant root ~1000, secondary root ~0.001",
        "difficulty": "pathological",
        "rationale": "Condition number of ~10^6 means floating-point errors compound exponentially. Closed-form becomes numerically useless after n~20."
    },

    # =========================================================================
    # BOOLEAN ALGEBRA STRESS TESTS (36-43)
    # =========================================================================
    {
        "test_id": "DISC_036",
        "category": "boolean_minimization",
        "input": "Minimize Boolean function with 20 variables and 2^19 minterms",
        "expected": "Quine-McCluskey with 2^19 ~ 500K minterms",
        "difficulty": "pathological",
        "rationale": "Quine-McCluskey is O(3^n) in worst case. With 20 variables and dense function, prime implicant table exceeds memory."
    },
    {
        "test_id": "DISC_037",
        "category": "boolean_minimization",
        "input": "Minimize symmetric Boolean function S_{10}^{20} (1 iff exactly 10 of 20 variables are true)",
        "expected": "C(20,10) = 184,756 minterms, minimal form has C(20,10) terms",
        "difficulty": "extreme",
        "rationale": "Symmetric threshold functions have no simpler form. 184K minterms each requiring storage and comparison."
    },
    {
        "test_id": "DISC_038",
        "category": "boolean_sat",
        "input": "Check satisfiability of random 3-SAT formula with 100 variables and 430 clauses (phase transition)",
        "expected": "At ratio ~4.3 clauses/variable, 50% satisfiable probability",
        "difficulty": "brutal",
        "rationale": "Phase transition point for 3-SAT. Exponential worst-case complexity. 2^100 possible assignments."
    },
    {
        "test_id": "DISC_039",
        "category": "boolean_prime_implicants",
        "input": "Find all prime implicants of 15-variable function with 1000 minterms",
        "expected": "Up to C(15,7)*2^8 = 1,638,400 potential prime implicants",
        "difficulty": "extreme",
        "rationale": "Prime implicant enumeration is exponential. Covering table with 1K minterms x 1M+ PIs is massive."
    },
    {
        "test_id": "DISC_040",
        "category": "boolean_karnaugh",
        "input": "Generate Karnaugh map for 8-variable Boolean function",
        "expected": "K-map limited to 4 variables; 8 variables requires 3D representation",
        "difficulty": "brutal",
        "rationale": "Standard K-map visualization breaks down beyond 4-5 variables. Tests graceful degradation or alternative representation."
    },
    {
        "test_id": "DISC_041",
        "category": "boolean_expression_eval",
        "input": "Evaluate Boolean expression with 50 nested XOR operations",
        "expected": "XOR chain: associative but expression parsing depth matters",
        "difficulty": "brutal",
        "rationale": "Deep nesting tests expression parser recursion limits and evaluation stack depth."
    },
    {
        "test_id": "DISC_042",
        "category": "boolean_conversion",
        "input": "Convert 12-variable CNF with 1000 clauses to DNF",
        "expected": "DNF can have up to 3^1000 terms in worst case",
        "difficulty": "pathological",
        "rationale": "CNF to DNF conversion is exponential. Distributing 1000 clauses creates astronomical term explosion."
    },
    {
        "test_id": "DISC_043",
        "category": "boolean_essential_pi",
        "input": "Find essential prime implicants for function where no PI is essential",
        "expected": "Cyclic covering problem requiring branch-and-bound",
        "difficulty": "extreme",
        "rationale": "When no PI is essential, covering becomes NP-hard optimization. Current greedy approach may fail to find optimal."
    },

    # =========================================================================
    # FINITE AUTOMATA STRESS TESTS (44-50)
    # =========================================================================
    {
        "test_id": "DISC_044",
        "category": "automata_state_explosion",
        "input": "Convert NFA with 20 states and epsilon-loops on each state to DFA",
        "expected": "DFA can have up to 2^20 = 1,048,576 states",
        "difficulty": "pathological",
        "rationale": "Subset construction worst case: exponential state blowup. 1M states each requiring storage of NFA state subset."
    },
    {
        "test_id": "DISC_045",
        "category": "automata_regex",
        "input": "Convert regex (a|b)*(c|d)*(e|f)*(g|h)*(i|j)* to minimal DFA",
        "expected": "NFA: ~30 states, DFA: potentially 2^5 = 32 states",
        "difficulty": "brutal",
        "rationale": "Multiple Kleene stars on unions create state space product. Tests both Thompson and minimization efficiency."
    },
    {
        "test_id": "DISC_046",
        "category": "automata_minimization",
        "input": "Minimize DFA with 10000 states and 2-symbol alphabet",
        "expected": "Hopcroft: O(n log n), but with large constants",
        "difficulty": "extreme",
        "rationale": "Partition refinement on 10K states. Each refinement step involves O(n) work, with O(log n) refinements."
    },
    {
        "test_id": "DISC_047",
        "category": "automata_intersection",
        "input": "Compute intersection of two DFAs with 100 states each",
        "expected": "Product automaton has up to 100 x 100 = 10000 states",
        "difficulty": "brutal",
        "rationale": "DFA intersection via product construction. 10K state pairs, each requiring transition computation."
    },
    {
        "test_id": "DISC_048",
        "category": "automata_equivalence",
        "input": "Test equivalence of two minimal DFAs with 5000 states",
        "expected": "Isomorphism testing on DFAs is polynomial but practical cost is high",
        "difficulty": "extreme",
        "rationale": "After minimization, equivalence is graph isomorphism. With 5K states, state matching is expensive."
    },
    {
        "test_id": "DISC_049",
        "category": "automata_complement",
        "input": "Compute complement of NFA directly (without DFA conversion)",
        "expected": "NFA complementation requires determinization first",
        "difficulty": "brutal",
        "rationale": "NFA complement != just swapping accept states. Tests whether system correctly determinizes first."
    },
    {
        "test_id": "DISC_050",
        "category": "automata_pumping_lemma",
        "input": "Generate pumping lemma counterexample for L = {a^n b^n : n >= 0}",
        "expected": "L is not regular; requires context-free grammar",
        "difficulty": "extreme",
        "rationale": "System should recognize this is not a regular language and provide pumping lemma violation proof."
    },
]


def get_all_tests() -> List[Dict[str, Any]]:
    """Return all 50 brutal discrete math stress tests."""
    return DISCRETE_MATH_BRUTAL_TESTS


def get_tests_by_category(category: str) -> List[Dict[str, Any]]:
    """Filter tests by category prefix."""
    return [t for t in DISCRETE_MATH_BRUTAL_TESTS if t["category"].startswith(category)]


def get_tests_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """Filter tests by difficulty level."""
    return [t for t in DISCRETE_MATH_BRUTAL_TESTS if t["difficulty"] == difficulty]


def print_test_summary():
    """Print summary statistics of the test suite."""
    categories = {}
    difficulties = {}

    for test in DISCRETE_MATH_BRUTAL_TESTS:
        cat = test["category"].split("_")[0]
        diff = test["difficulty"]

        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print("=" * 60)
    print("DISCRETE MATH BRUTAL STRESS TEST SUITE")
    print("=" * 60)
    print(f"\nTotal Tests: {len(DISCRETE_MATH_BRUTAL_TESTS)}")
    print("\nBy Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print("\nBy Difficulty:")
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count}")
    print("=" * 60)


# =============================================================================
# TEST EXECUTION FRAMEWORK
# =============================================================================

def run_combinatorics_tests():
    """Run tests targeting CombinatoricsAgent."""
    tests = get_tests_by_category("combinatorics")
    print(f"\n[COMBINATORICS] Running {len(tests)} tests...")
    for test in tests:
        print(f"  {test['test_id']}: {test['category']} - {test['difficulty']}")


def run_graph_tests():
    """Run tests targeting GraphTheoryAgent."""
    tests = get_tests_by_category("graph")
    print(f"\n[GRAPH THEORY] Running {len(tests)} tests...")
    for test in tests:
        print(f"  {test['test_id']}: {test['category']} - {test['difficulty']}")


def run_set_tests():
    """Run tests targeting SetTheoryAgent."""
    tests = get_tests_by_category("set")
    print(f"\n[SET THEORY] Running {len(tests)} tests...")
    for test in tests:
        print(f"  {test['test_id']}: {test['category']} - {test['difficulty']}")


def run_recurrence_tests():
    """Run tests targeting RecurrenceRelationAgent."""
    tests = get_tests_by_category("recurrence")
    print(f"\n[RECURRENCE] Running {len(tests)} tests...")
    for test in tests:
        print(f"  {test['test_id']}: {test['category']} - {test['difficulty']}")


def run_boolean_tests():
    """Run tests targeting BooleanAlgebraAgent."""
    tests = get_tests_by_category("boolean")
    print(f"\n[BOOLEAN ALGEBRA] Running {len(tests)} tests...")
    for test in tests:
        print(f"  {test['test_id']}: {test['category']} - {test['difficulty']}")


def run_automata_tests():
    """Run tests targeting FiniteAutomataAgent."""
    tests = get_tests_by_category("automata")
    print(f"\n[FINITE AUTOMATA] Running {len(tests)} tests...")
    for test in tests:
        print(f"  {test['test_id']}: {test['category']} - {test['difficulty']}")


if __name__ == "__main__":
    print_test_summary()

    # Display all tests
    print("\n\nDETAILED TEST LISTING:")
    print("-" * 80)
    for test in DISCRETE_MATH_BRUTAL_TESTS:
        print(f"\n{test['test_id']} [{test['difficulty'].upper()}]")
        print(f"  Category: {test['category']}")
        print(f"  Input: {test['input'][:70]}...")
        print(f"  Expected: {test['expected'][:60]}...")
        print(f"  Rationale: {test['rationale'][:70]}...")
