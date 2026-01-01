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
BRUTAL LOGIC DOMAIN STRESS TESTS
=================================

50 research-level tests designed to BREAK the logic specialist system.

Categories:
1. SAT Phase Transition (ratio ~4.26) - Tests 001-008
2. QBF with Alternating Quantifiers - Tests 009-014
3. Modal Logic / Infinite Kripke Frames - Tests 015-020
4. Temporal Logic Model Checking - Tests 021-026
5. First-Order Logic with Complex Terms - Tests 027-032
6. Resolution Proof Exponential Blowup - Tests 033-038
7. Non-Horn Clauses / Hidden Structure - Tests 039-042
8. Pigeonhole Principle Encodings - Tests 043-046
9. Graph Coloring SAT Encodings - Tests 047-049
10. Intuitionistic Logic Proofs - Test 050

Difficulty Levels:
- brutal: Will stress any solver significantly
- extreme: Likely to cause timeout or memory issues
- pathological: Mathematically proven to be intractable

Each test includes rationale explaining WHY it breaks solvers.
"""

import math
import itertools
from typing import List, Dict, Any, Optional

# ============================================================================
# HELPER FUNCTIONS FOR GENERATING HARD INSTANCES
# ============================================================================

def generate_random_3sat_at_threshold(n_vars: int, ratio: float = 4.26) -> List[List[int]]:
    """
    Generate random 3-SAT at the phase transition threshold.
    At ratio ~4.26 clauses/variable, instances are maximally hard.
    """
    import random
    n_clauses = int(n_vars * ratio)
    clauses = []
    for _ in range(n_clauses):
        clause = []
        vars_used = random.sample(range(1, n_vars + 1), 3)
        for v in vars_used:
            clause.append(v if random.random() > 0.5 else -v)
        clauses.append(clause)
    return clauses


def generate_pigeonhole(n_pigeons: int, n_holes: int) -> List[List[int]]:
    """
    Generate pigeonhole principle: n pigeons into n-1 holes.
    Variable p_i_j means pigeon i is in hole j.
    Requires exponential resolution proof.
    """
    clauses = []

    # Variable mapping: p[i][j] = i * n_holes + j + 1
    def var(pigeon: int, hole: int) -> int:
        return pigeon * n_holes + hole + 1

    # Each pigeon must be in at least one hole
    for i in range(n_pigeons):
        clause = [var(i, j) for j in range(n_holes)]
        clauses.append(clause)

    # No two pigeons in the same hole
    for j in range(n_holes):
        for i1 in range(n_pigeons):
            for i2 in range(i1 + 1, n_pigeons):
                clauses.append([-var(i1, j), -var(i2, j)])

    return clauses


def generate_graph_coloring_sat(n_nodes: int, n_colors: int,
                                 edges: List[tuple]) -> List[List[int]]:
    """
    Encode graph coloring as SAT.
    Variable x[i][c] means node i has color c.
    """
    clauses = []

    def var(node: int, color: int) -> int:
        return node * n_colors + color + 1

    # Each node has at least one color
    for i in range(n_nodes):
        clause = [var(i, c) for c in range(n_colors)]
        clauses.append(clause)

    # Each node has at most one color
    for i in range(n_nodes):
        for c1 in range(n_colors):
            for c2 in range(c1 + 1, n_colors):
                clauses.append([-var(i, c1), -var(i, c2)])

    # Adjacent nodes have different colors
    for (u, v) in edges:
        for c in range(n_colors):
            clauses.append([-var(u, c), -var(v, c)])

    return clauses


def generate_tseitin_transformation(depth: int) -> List[List[int]]:
    """
    Generate Tseitin transformation of a formula tree.
    Creates formulas with exponential number of satisfying assignments
    but polynomial CNF representation.
    """
    # Build a binary tree formula and encode it
    clauses = []
    var_count = 2 ** depth

    # Create XOR chains (hard for resolution)
    for level in range(depth):
        step = 2 ** (level + 1)
        for i in range(0, var_count, step):
            if i + step // 2 < var_count:
                v1 = i + 1
                v2 = i + step // 2 + 1
                # XOR constraint: x1 XOR x2 = result (creates 4 clauses)
                result_var = var_count + level * (var_count // 2) + i // step + 1
                clauses.append([v1, v2, -result_var])
                clauses.append([v1, -v2, result_var])
                clauses.append([-v1, v2, result_var])
                clauses.append([-v1, -v2, -result_var])

    return clauses


# ============================================================================
# 50 BRUTAL STRESS TESTS
# ============================================================================

BRUTAL_LOGIC_TESTS: List[Dict[str, Any]] = [

    # =========================================================================
    # CATEGORY 1: SAT PHASE TRANSITION (Tests 001-008)
    # =========================================================================

    {
        "test_id": "LOGIC_001",
        "category": "SAT_phase_transition",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "Random 3-SAT at phase transition, 50 variables",
            "generator": "generate_random_3sat_at_threshold(50, 4.26)",
            "n_vars": 50,
            "clause_var_ratio": 4.26
        },
        "expected": "SAT or UNSAT within timeout",
        "difficulty": "brutal",
        "rationale": "At clause/variable ratio ~4.26, random 3-SAT exhibits a phase transition where ~50% of instances are SAT. These instances are maximally hard because the solver cannot determine satisfiability easily - the search space is exactly balanced between satisfiable and unsatisfiable regions. DPLL/CDCL solvers exhibit exponential runtime variance here."
    },

    {
        "test_id": "LOGIC_002",
        "category": "SAT_phase_transition",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "Random 3-SAT at phase transition, 75 variables",
            "generator": "generate_random_3sat_at_threshold(75, 4.26)",
            "n_vars": 75,
            "clause_var_ratio": 4.26
        },
        "expected": "Likely timeout",
        "difficulty": "extreme",
        "rationale": "Scaling up the phase transition instance. At 75 variables with ratio 4.26, we have ~320 clauses. The solver must navigate an astronomically large search space (2^75 possible assignments) where unit propagation provides minimal pruning due to balanced clause structure."
    },

    {
        "test_id": "LOGIC_003",
        "category": "SAT_phase_transition",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "Random 3-SAT at phase transition, 100 variables",
            "generator": "generate_random_3sat_at_threshold(100, 4.26)",
            "n_vars": 100,
            "clause_var_ratio": 4.26
        },
        "expected": "Timeout expected",
        "difficulty": "pathological",
        "rationale": "At 100 variables and 426 clauses, the instance is at the computational complexity barrier. Even state-of-the-art solvers like Kissat or CaDiCaL struggle with such instances. The native CDCL implementation will almost certainly timeout or exhaust memory during conflict analysis."
    },

    {
        "test_id": "LOGIC_004",
        "category": "SAT_phase_transition",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "Barely-satisfiable 3-SAT at underconstrained boundary",
            "generator": "generate_random_3sat_at_threshold(60, 4.0)",
            "n_vars": 60,
            "clause_var_ratio": 4.0
        },
        "expected": "SAT (but hard to find)",
        "difficulty": "brutal",
        "rationale": "Just below the phase transition (ratio 4.0 vs 4.26), instances are typically SAT but finding the satisfying assignment requires extensive search. The solution space is sparse and VSIDS heuristics may repeatedly choose wrong branching variables."
    },

    {
        "test_id": "LOGIC_005",
        "category": "SAT_phase_transition",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "Barely-unsatisfiable 3-SAT at overconstrained boundary",
            "generator": "generate_random_3sat_at_threshold(60, 4.5)",
            "n_vars": 60,
            "clause_var_ratio": 4.5
        },
        "expected": "UNSAT (hard to prove)",
        "difficulty": "brutal",
        "rationale": "Just above the phase transition (ratio 4.5 vs 4.26), instances are typically UNSAT but proving unsatisfiability requires deriving the empty clause through resolution. The proof can be exponentially long if the unsatisfiability core is hard to identify."
    },

    {
        "test_id": "LOGIC_006",
        "category": "SAT_phase_transition",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "Random 4-SAT at its phase transition (ratio ~9.93)",
            "clauses": "[[1,2,3,4], [-1,-2,3,-4], [1,-2,-3,4], [-1,2,-3,-4], ...]",
            "n_vars": 40,
            "clause_var_ratio": 9.93
        },
        "expected": "Timeout likely",
        "difficulty": "extreme",
        "rationale": "4-SAT has a higher phase transition ratio (~9.93) but each clause has more literals, providing less unit propagation power. The solver must handle ~397 clauses over 40 variables with 4 literals each, making conflict analysis more complex."
    },

    {
        "test_id": "LOGIC_007",
        "category": "SAT_phase_transition",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "2-SAT disguised as 3-SAT at phase transition",
            "note": "Hidden structure: most clauses are 2-literal subclauses of 3-clauses",
            "n_vars": 80,
            "clause_var_ratio": 4.26
        },
        "expected": "SAT (hidden polynomial structure)",
        "difficulty": "brutal",
        "rationale": "This tests whether the solver can detect hidden 2-SAT structure within 3-SAT encoding. Pure 2-SAT is polynomial, but the overhead of the 3-SAT encoding hides this. A smart preprocessor would detect and exploit this structure; a naive solver will struggle."
    },

    {
        "test_id": "LOGIC_008",
        "category": "SAT_phase_transition",
        "input": {
            "type": "sat",
            "operation": "incremental_solve",
            "description": "Incremental SAT: start SAT, add clauses until UNSAT",
            "initial_clauses": "generate_random_3sat_at_threshold(50, 3.5)",
            "additional_clauses": "generate_random_3sat_at_threshold(50, 0.76)",
            "n_vars": 50
        },
        "expected": "Transition from SAT to UNSAT",
        "difficulty": "brutal",
        "rationale": "Tests incremental SAT solving capability. Starting at ratio 3.5 (SAT region) and adding clauses to reach ratio 4.26 (transition). The solver must efficiently reuse learned clauses across the transition point. Most solvers fail to maintain learned clause quality across such dramatic constraint changes."
    },

    # =========================================================================
    # CATEGORY 2: QBF WITH ALTERNATING QUANTIFIERS (Tests 009-014)
    # =========================================================================

    {
        "test_id": "LOGIC_009",
        "category": "QBF_alternating_quantifiers",
        "input": {
            "type": "qbf",
            "operation": "solve",
            "formula": "forall x1 exists x2 forall x3: (x1 or x2) and (not x2 or x3) and (not x1 or not x3)",
            "quantifier_prefix": ["forall", "exists", "forall"],
            "variables": ["x1", "x2", "x3"],
            "matrix": [[1, 2], [-2, 3], [-1, -3]]
        },
        "expected": "FALSE (adversary wins)",
        "difficulty": "brutal",
        "rationale": "QBF with 3 alternating quantifiers is PSPACE-complete. The forall-exists-forall pattern creates a 2-round game where the universal player chooses x1 and x3, and the existential player must find x2 satisfying the matrix. This requires game-tree search which the current SAT solver cannot handle."
    },

    {
        "test_id": "LOGIC_010",
        "category": "QBF_alternating_quantifiers",
        "input": {
            "type": "qbf",
            "operation": "solve",
            "formula": "exists x1 forall x2 exists x3 forall x4: matrix",
            "quantifier_prefix": ["exists", "forall", "exists", "forall"],
            "n_vars": 4,
            "alternations": 4,
            "matrix_description": "Random 3-CNF over variables"
        },
        "expected": "Requires QBF solver (not SAT)",
        "difficulty": "extreme",
        "rationale": "4 quantifier alternations creates a 4-level game tree. Each alternation roughly squares the complexity. The predicate specialist can handle exists/forall over finite domains, but QBF requires specialized QCDCL algorithms that are not implemented."
    },

    {
        "test_id": "LOGIC_011",
        "category": "QBF_alternating_quantifiers",
        "input": {
            "type": "qbf",
            "operation": "solve",
            "formula": "Nested alternation depth 6",
            "quantifier_prefix": ["exists", "forall", "exists", "forall", "exists", "forall"],
            "n_vars_per_block": 5,
            "total_vars": 30,
            "alternations": 6
        },
        "expected": "Timeout guaranteed",
        "difficulty": "pathological",
        "rationale": "6 quantifier alternations with 5 variables per block. The game tree has 2^5 = 32 branches at each level, giving roughly 32^6 = 10^9 nodes. QBF solvers use advanced techniques like cube learning and dependency schemes, none of which are implemented in the current specialists."
    },

    {
        "test_id": "LOGIC_012",
        "category": "QBF_alternating_quantifiers",
        "input": {
            "type": "qbf",
            "operation": "solve",
            "formula": "QBF encoding of 2-player game (simplified chess endgame)",
            "description": "King-rook vs King endgame encoded as QBF",
            "alternations": 8,
            "moves_per_turn": 3,
            "total_vars": 48
        },
        "expected": "TRUE (checkmate exists)",
        "difficulty": "pathological",
        "rationale": "Game-theoretic QBF encoding where quantifier alternation represents alternating moves. Even with simplification (3 moves per turn instead of full move set), 8 alternations creates an intractable instance. This is a canonical application of QBF that no SAT solver can handle."
    },

    {
        "test_id": "LOGIC_013",
        "category": "QBF_alternating_quantifiers",
        "input": {
            "type": "qbf_dependency",
            "operation": "solve",
            "formula": "DQBF: exists x1,x2(y) forall y: phi",
            "description": "Dependency QBF - x2 depends on y",
            "dependencies": {"x2": ["y"]},
            "n_vars": 10
        },
        "expected": "Requires DQBF solver",
        "difficulty": "extreme",
        "rationale": "Dependency QBF (DQBF) is NEXPTIME-complete, strictly harder than QBF. The existential variable x2 depends on universal y, breaking the linear quantifier prefix assumption. No current specialist handles dependency schemes."
    },

    {
        "test_id": "LOGIC_014",
        "category": "QBF_alternating_quantifiers",
        "input": {
            "type": "qbf",
            "operation": "model_counting",
            "formula": "Count satisfying Skolem functions",
            "quantifier_prefix": ["forall", "exists"],
            "n_universal": 10,
            "n_existential": 10
        },
        "expected": "2^100 possible functions (intractable)",
        "difficulty": "pathological",
        "rationale": "Counting Skolem functions for forall-exists QBF requires enumerating all 2^(2^n) functions from universal to existential variables. Even for n=10, this is 2^1024 functions to consider. Model counting is #P-complete even for SAT, and much harder for QBF."
    },

    # =========================================================================
    # CATEGORY 3: MODAL LOGIC / INFINITE KRIPKE FRAMES (Tests 015-020)
    # =========================================================================

    {
        "test_id": "LOGIC_015",
        "category": "modal_logic_infinite_frames",
        "input": {
            "type": "modal",
            "operation": "validity_check",
            "formula": "Box(p implies Diamond(q)) implies (Box(p) implies Diamond(Box(q)))",
            "system": "S5",
            "description": "Barcan-like formula mixing Box and Diamond"
        },
        "expected": "INVALID in general",
        "difficulty": "brutal",
        "rationale": "This formula involves complex interactions between necessity and possibility. In S5, the equivalence relation on worlds means Box and Diamond can 'see' everything, but nested modalities create combinatorial explosion in tableau expansion. The tableau must track formulas across all accessible worlds simultaneously."
    },

    {
        "test_id": "LOGIC_016",
        "category": "modal_logic_infinite_frames",
        "input": {
            "type": "modal",
            "operation": "validity_check",
            "formula": "Diamond(Box(Diamond(p))) implies Box(Diamond(Box(Diamond(p))))",
            "system": "K",
            "nesting_depth": 4,
            "description": "Deeply nested modalities in minimal logic K"
        },
        "expected": "INVALID (countermodel exists)",
        "difficulty": "extreme",
        "rationale": "In the minimal modal logic K (no frame conditions), each Box/Diamond can require a new world in the Kripke model. With nesting depth 4, the tableau may need to explore exponentially many worlds. The max_worlds=8 limit in the current implementation will likely truncate the search prematurely."
    },

    {
        "test_id": "LOGIC_017",
        "category": "modal_logic_infinite_frames",
        "input": {
            "type": "modal",
            "operation": "validity_check",
            "formula": "Loeb's formula: Box(Box(p) implies p) implies Box(p)",
            "system": "GL",
            "description": "Provability logic - requires transitive irreflexive frames"
        },
        "expected": "VALID in GL",
        "difficulty": "brutal",
        "rationale": "The system GL (Godel-Loeb logic) is the logic of provability with transitive, irreflexive, conversely well-founded frames. The current modal specialist only implements K, T, S4, S5, D, B - not GL. This test will fail due to missing system support, exposing a capability gap."
    },

    {
        "test_id": "LOGIC_018",
        "category": "modal_logic_infinite_frames",
        "input": {
            "type": "modal",
            "operation": "satisfiability",
            "formula": "p and Box(not p) and Diamond(Diamond(p))",
            "system": "T",
            "description": "Inconsistent modalities requiring infinite frame"
        },
        "expected": "SATISFIABLE (needs specific frame)",
        "difficulty": "extreme",
        "rationale": "In T (reflexive frames), Box(not p) means p is false at all accessible worlds including current (by reflexivity). But we also have p true at current world - contradiction. Yet Diamond(Diamond(p)) suggests p is possible 2 steps away. The tableau must carefully track accessibility to avoid false contradictions or false satisfiability claims."
    },

    {
        "test_id": "LOGIC_019",
        "category": "modal_logic_infinite_frames",
        "input": {
            "type": "modal",
            "operation": "validity_check",
            "formula": "Conjunction of 20 distinct Box formulas",
            "clauses": [f"Box(p{i})" for i in range(20)],
            "system": "K",
            "description": "Many modal atoms requiring world tracking"
        },
        "expected": "Timeout (world explosion)",
        "difficulty": "extreme",
        "rationale": "With 20 boxed propositions, each negation in the tableau may require a separate witness world. The world count can grow as O(2^n) for n propositions, quickly exceeding max_worlds=8. The solver must either be much smarter about world reuse or admit incompleteness."
    },

    {
        "test_id": "LOGIC_020",
        "category": "modal_logic_infinite_frames",
        "input": {
            "type": "multi_modal",
            "operation": "validity_check",
            "formula": "[a][b]p implies [b][a]p",
            "agents": ["a", "b"],
            "system": "KD45_multi",
            "description": "Multi-agent epistemic logic with non-commuting knowledge"
        },
        "expected": "INVALID (agents have independent knowledge)",
        "difficulty": "brutal",
        "rationale": "Multi-modal logic extends single-agent modal logic with separate accessibility relations for each agent. The formula asks if 'agent a knows that agent b knows p' implies 'agent b knows that agent a knows p' - generally false. Current implementation only handles single modality, so this will fail entirely."
    },

    # =========================================================================
    # CATEGORY 4: TEMPORAL LOGIC MODEL CHECKING (Tests 021-026)
    # =========================================================================

    {
        "test_id": "LOGIC_021",
        "category": "temporal_logic_model_checking",
        "input": {
            "type": "ltl",
            "operation": "model_check",
            "formula": "G(request implies F(grant))",
            "structure": {
                "states": 100,
                "transitions_per_state": 5,
                "labeling": "random"
            },
            "description": "Liveness property on medium state space"
        },
        "expected": "Timeout on bounded model check",
        "difficulty": "brutal",
        "rationale": "LTL model checking with G(p -> Fq) requires exploring all infinite paths to verify liveness. The bounded model check in the specialist limits path length to max_depth=100, but with 5 transitions per state, there are 5^100 possible paths. The path enumeration in _generate_paths will explode combinatorially."
    },

    {
        "test_id": "LOGIC_022",
        "category": "temporal_logic_model_checking",
        "input": {
            "type": "ltl",
            "operation": "model_check",
            "formula": "G(F(p)) and G(F(q)) and G(p implies X(not p))",
            "structure": {
                "states": 50,
                "description": "Alternating p and q forever"
            },
            "description": "Fairness + mutual exclusion"
        },
        "expected": "Complex counterexample search",
        "difficulty": "extreme",
        "rationale": "This combines two fairness constraints (infinitely often p and q) with a mutex-like constraint (p implies not-p next). Finding a witness path or proving no path exists requires sophisticated Buchi automata intersection, which the current bounded approach cannot handle correctly."
    },

    {
        "test_id": "LOGIC_023",
        "category": "temporal_logic_model_checking",
        "input": {
            "type": "ltl",
            "operation": "model_check",
            "formula": "(p U q) and (q U r) and (r U p)",
            "structure": {
                "states": 30,
                "cyclic": True
            },
            "description": "Cyclic Until chain"
        },
        "expected": "Requires careful Until semantics",
        "difficulty": "brutal",
        "rationale": "Three nested Until operators forming a cycle: p holds until q, q until r, r until p. This creates a constraint that can only be satisfied by specific cyclic paths. The Until operator is notoriously hard to reason about when combined, and the current evaluation may not correctly handle the 'strong until' semantics."
    },

    {
        "test_id": "LOGIC_024",
        "category": "temporal_logic_model_checking",
        "input": {
            "type": "ctl",
            "operation": "model_check",
            "formula": "AG(EF(reset) implies AX(AF(ready)))",
            "structure": {
                "states": 200,
                "transitions": 1000
            },
            "description": "Nested path quantifiers in large system"
        },
        "expected": "Fixed-point computation may not terminate",
        "difficulty": "extreme",
        "rationale": "CTL formula with alternating path quantifiers: AG (for all paths, globally), EF (exists path, eventually), AX (all paths, next), AF (all paths, eventually). Each quantifier requires fixed-point computation over the state space. With 200 states and 1000 transitions, the _af and _ag computations may iterate thousands of times."
    },

    {
        "test_id": "LOGIC_025",
        "category": "temporal_logic_model_checking",
        "input": {
            "type": "ctl_star",
            "operation": "model_check",
            "formula": "A(G(p) implies F(q))",
            "description": "CTL* formula requiring LTL-over-paths",
            "structure": {
                "states": 100,
                "branching": 3
            }
        },
        "expected": "Requires CTL* solver (not CTL)",
        "difficulty": "pathological",
        "rationale": "CTL* allows arbitrary combinations of path quantifiers and temporal operators. The formula A(G(p) implies F(q)) is NOT expressible in pure CTL - it requires checking an LTL property along each path. The current specialist only handles CTL and LTL separately, not their combination."
    },

    {
        "test_id": "LOGIC_026",
        "category": "temporal_logic_model_checking",
        "input": {
            "type": "ltl",
            "operation": "synthesis",
            "formula": "G(request implies F(grant)) and G(grant implies X(not grant))",
            "environment_vars": ["request"],
            "system_vars": ["grant"],
            "description": "LTL synthesis (reactive synthesis problem)"
        },
        "expected": "Requires 2QBF/game solving",
        "difficulty": "pathological",
        "rationale": "LTL synthesis asks: does there exist a strategy for the system to satisfy the specification against all environment behaviors? This is 2EXPTIME-complete and requires constructing a winning strategy in a two-player game. The current model checker can only verify, not synthesize."
    },

    # =========================================================================
    # CATEGORY 5: FIRST-ORDER LOGIC WITH COMPLEX TERMS (Tests 027-032)
    # =========================================================================

    {
        "test_id": "LOGIC_027",
        "category": "fol_complex_terms",
        "input": {
            "type": "fol",
            "operation": "unification",
            "term1": {"type": "function", "name": "f", "args": [
                {"type": "variable", "name": "x"},
                {"type": "function", "name": "g", "args": [{"type": "variable", "name": "y"}]}
            ]},
            "term2": {"type": "function", "name": "f", "args": [
                {"type": "function", "name": "g", "args": [{"type": "variable", "name": "z"}]},
                {"type": "variable", "name": "x"}
            ]},
            "description": "Unification requiring occurs check"
        },
        "expected": "FAIL (occurs check)",
        "difficulty": "brutal",
        "rationale": "Unifying f(x, g(y)) with f(g(z), x) would require x = g(z) and g(y) = x, leading to x = g(z) = g(y), thus z = y. But then x = g(z) and x appears in g(z) - an occurs check failure. The current unification in predicate_specialist does NOT implement occurs check, so it may produce unsound substitutions."
    },

    {
        "test_id": "LOGIC_028",
        "category": "fol_complex_terms",
        "input": {
            "type": "fol",
            "operation": "unification",
            "term1": {"type": "function", "name": "h", "args": [
                {"type": "function", "name": "f", "args": [
                    {"type": "function", "name": "g", "args": [{"type": "variable", "name": "x"}]}
                ]}
            ]},
            "term2": {"type": "function", "name": "h", "args": [
                {"type": "function", "name": "f", "args": [
                    {"type": "function", "name": "g", "args": [
                        {"type": "function", "name": "f", "args": [{"type": "variable", "name": "y"}]}
                    ]}
                ]}
            ]},
            "description": "Deeply nested function terms"
        },
        "expected": "{x -> f(y)}",
        "difficulty": "brutal",
        "rationale": "Deep nesting of function symbols tests the recursive unification algorithm. With nesting depth 4+, the substitution must be carefully propagated. The current implementation uses simple recursive unification which may stack overflow on very deep terms."
    },

    {
        "test_id": "LOGIC_029",
        "category": "fol_complex_terms",
        "input": {
            "type": "fol",
            "operation": "resolution",
            "clause1": "P(f(x), g(x)) or Q(x)",
            "clause2": "not P(f(a), y) or R(y)",
            "description": "Resolution with function symbols"
        },
        "expected": "Q(a) or R(g(a))",
        "difficulty": "brutal",
        "rationale": "First-order resolution requires unifying P(f(x), g(x)) with P(f(a), y), giving {x->a, y->g(a)}. The resolvent must correctly apply this substitution to both clauses. The ProofSpecialist implements propositional inference rules but not first-order resolution with unification."
    },

    {
        "test_id": "LOGIC_030",
        "category": "fol_complex_terms",
        "input": {
            "type": "fol",
            "operation": "skolemization",
            "formula": "forall x exists y forall z exists w: P(x,y,z,w)",
            "description": "Complex Skolem function introduction"
        },
        "expected": "forall x forall z: P(x, f(x), z, g(x,z))",
        "difficulty": "extreme",
        "rationale": "Skolemization replaces existential variables with Skolem functions of preceding universals. Here y depends on x (becomes f(x)) and w depends on x and z (becomes g(x,z)). The current system has no Skolemization capability, making first-order theorem proving impossible."
    },

    {
        "test_id": "LOGIC_031",
        "category": "fol_complex_terms",
        "input": {
            "type": "fol",
            "operation": "herbrand_model",
            "theory": [
                "forall x: P(x) implies P(f(x))",
                "P(a)"
            ],
            "query": "exists x: P(f(f(f(x))))",
            "description": "Herbrand model with infinite domain"
        },
        "expected": "TRUE (witness: x=a)",
        "difficulty": "extreme",
        "rationale": "The Herbrand universe is {a, f(a), f(f(a)), ...} - infinite. To answer the query, we need P(f(f(f(a)))), which follows from iterating the first clause 3 times on P(a). But the predicate specialist only handles finite domains passed explicitly; it cannot construct Herbrand models."
    },

    {
        "test_id": "LOGIC_032",
        "category": "fol_complex_terms",
        "input": {
            "type": "fol",
            "operation": "satisfiability",
            "formula": "exists x forall y: R(x,y) and forall x exists y: not R(x,y)",
            "description": "Inherently inconsistent first-order formula"
        },
        "expected": "UNSATISFIABLE",
        "difficulty": "brutal",
        "rationale": "The first conjunct says there's an x that R-relates to all y. The second says for every x there's a y it doesn't R-relate to. Together these are contradictory. Detecting this requires first-order reasoning about quantifier scope, which propositional methods cannot do."
    },

    # =========================================================================
    # CATEGORY 6: RESOLUTION PROOF EXPONENTIAL BLOWUP (Tests 033-038)
    # =========================================================================

    {
        "test_id": "LOGIC_033",
        "category": "resolution_exponential_proofs",
        "input": {
            "type": "sat",
            "operation": "prove_unsat",
            "clauses": "Pigeonhole PHP(5,4): 5 pigeons, 4 holes",
            "generator": "generate_pigeonhole(5, 4)",
            "n_pigeons": 5,
            "n_holes": 4
        },
        "expected": "UNSAT (exponential proof)",
        "difficulty": "brutal",
        "rationale": "The Pigeonhole Principle PHP(n+1,n) is UNSAT but requires resolution proofs of size Omega(2^n). For PHP(5,4), proofs require at least 2^4=16 resolution steps. CDCL can learn this faster via conflict analysis, but native resolution theorem proving will struggle."
    },

    {
        "test_id": "LOGIC_034",
        "category": "resolution_exponential_proofs",
        "input": {
            "type": "sat",
            "operation": "prove_unsat",
            "clauses": "Pigeonhole PHP(8,7): 8 pigeons, 7 holes",
            "generator": "generate_pigeonhole(8, 7)",
            "n_pigeons": 8,
            "n_holes": 7
        },
        "expected": "UNSAT (requires 2^7=128+ steps)",
        "difficulty": "extreme",
        "rationale": "PHP(8,7) is the classic benchmark for exponential resolution complexity. Any resolution-based proof requires at least 2^7=128 steps, and typical proofs are much longer. CDCL may timeout even with clause learning if it doesn't discover the critical lemmas."
    },

    {
        "test_id": "LOGIC_035",
        "category": "resolution_exponential_proofs",
        "input": {
            "type": "sat",
            "operation": "prove_unsat",
            "clauses": "Pigeonhole PHP(12,11): 12 pigeons, 11 holes",
            "generator": "generate_pigeonhole(12, 11)",
            "n_pigeons": 12,
            "n_holes": 11
        },
        "expected": "Timeout guaranteed",
        "difficulty": "pathological",
        "rationale": "PHP(12,11) requires proofs of size at least 2^11=2048 steps. Modern SAT solvers use symmetry-breaking preprocessing to handle pigeonhole, but the native solver lacks this. With 132 variables and 782 clauses, the search space is astronomical."
    },

    {
        "test_id": "LOGIC_036",
        "category": "resolution_exponential_proofs",
        "input": {
            "type": "sat",
            "operation": "prove_unsat",
            "clauses": "Tseitin transformation of parity formula",
            "generator": "generate_tseitin_transformation(6)",
            "depth": 6,
            "description": "XOR parity chain requires exponential tree-resolution"
        },
        "expected": "UNSAT (exponential tree-resolution)",
        "difficulty": "extreme",
        "rationale": "Tseitin formulas encoding XOR/parity are known to require exponential-size tree-like resolution proofs (Urquhart, 1987). While CDCL can be seen as dag-like resolution (more powerful), the conflict analysis on parity formulas tends to produce unhelpful learned clauses, causing degenerate behavior."
    },

    {
        "test_id": "LOGIC_037",
        "category": "resolution_exponential_proofs",
        "input": {
            "type": "sat",
            "operation": "prove_unsat",
            "clauses": "Random unsatisfiable k-CNF near threshold",
            "generator": "generate_random_3sat_at_threshold(80, 5.0)",
            "n_vars": 80,
            "clause_var_ratio": 5.0
        },
        "expected": "UNSAT (hard to prove)",
        "difficulty": "extreme",
        "rationale": "At ratio 5.0 (well above threshold 4.26), the formula is almost certainly UNSAT. But proving unsatisfiability requires identifying and chaining together many conflict clauses. With 400 clauses over 80 variables, the conflict graph is dense and learning progression is slow."
    },

    {
        "test_id": "LOGIC_038",
        "category": "resolution_exponential_proofs",
        "input": {
            "type": "resolution_proof",
            "operation": "verify",
            "premises": ["P or Q", "not P or R", "not Q or R", "not R"],
            "claimed_conclusion": "CONTRADICTION",
            "steps": ["P or R (from 1,2)", "Q or R (from 1,3)", "..."],
            "description": "Verify exponential resolution derivation"
        },
        "expected": "Proof verification timeout",
        "difficulty": "brutal",
        "rationale": "The ProofSpecialist can verify proof steps but not generate them. Given an exponentially long proof (as required for hard UNSAT formulas), even verification becomes expensive. With 100+ steps, tracking known_statements and checking references becomes quadratic."
    },

    # =========================================================================
    # CATEGORY 7: NON-HORN CLAUSES / HIDDEN STRUCTURE (Tests 039-042)
    # =========================================================================

    {
        "test_id": "LOGIC_039",
        "category": "non_horn_hidden_structure",
        "input": {
            "type": "sat",
            "operation": "solve",
            "clauses": "Randomly permuted XOR clauses encoded as CNF",
            "description": "XOR-SAT disguised as CNF",
            "n_vars": 50,
            "n_xor_constraints": 50
        },
        "expected": "SAT/UNSAT (linear algebra solvable)",
        "difficulty": "extreme",
        "rationale": "XOR constraints are linear equations over GF(2), solvable in polynomial time via Gaussian elimination. But when encoded as CNF (each XOR of k variables becomes 2^(k-1) clauses), standard DPLL/CDCL treats them as independent clauses and misses the linear structure. Specialized XOR-handling (like CryptoMiniSat) is needed."
    },

    {
        "test_id": "LOGIC_040",
        "category": "non_horn_hidden_structure",
        "input": {
            "type": "sat",
            "operation": "solve",
            "clauses": "Hidden Horn structure with symmetry",
            "description": "Formula is Horn after renaming half the variables",
            "n_vars": 60,
            "n_clauses": 180
        },
        "expected": "SAT (polynomial after renaming)",
        "difficulty": "brutal",
        "rationale": "Pure Horn-SAT is solvable in linear time via unit propagation. This formula is Horn after renaming: for each clause, if we flip certain variables' polarity, at most one literal is positive. Without detecting this 'hidden Horn' structure, the solver treats it as general 3-SAT and struggles unnecessarily."
    },

    {
        "test_id": "LOGIC_041",
        "category": "non_horn_hidden_structure",
        "input": {
            "type": "sat",
            "operation": "solve",
            "clauses": "Mutilated chessboard as SAT",
            "description": "Can a mutilated 8x8 chessboard be tiled by dominoes?",
            "encoding": "Edge covering constraints",
            "n_vars": 112,
            "n_clauses": 448
        },
        "expected": "UNSAT (classic proof by parity)",
        "difficulty": "extreme",
        "rationale": "The mutilated chessboard (opposite corners removed) cannot be tiled by dominoes because remaining squares have unequal black/white counts. SAT encoding loses this parity argument and must discover it through exhaustive search. Extended resolution can help, but standard CDCL may not find the right lemmas."
    },

    {
        "test_id": "LOGIC_042",
        "category": "non_horn_hidden_structure",
        "input": {
            "type": "sat",
            "operation": "solve",
            "clauses": "Factoring-based SAT encoding",
            "description": "SAT encoding of 'does N have a non-trivial factor?'",
            "N": 1000003,  # Prime number
            "bit_width": 20
        },
        "expected": "UNSAT (N is prime)",
        "difficulty": "pathological",
        "rationale": "Encoding integer factoring as SAT creates a formula where satisfiability equals existence of non-trivial factors. For a 20-bit prime, proving UNSAT essentially requires checking all 2^10 potential factors. This is a reduction from factoring to SAT, showing cryptographic hardness."
    },

    # =========================================================================
    # CATEGORY 8: PIGEONHOLE PRINCIPLE ENCODINGS (Tests 043-046)
    # =========================================================================

    {
        "test_id": "LOGIC_043",
        "category": "pigeonhole_variants",
        "input": {
            "type": "sat",
            "operation": "solve",
            "clauses": "Functional pigeonhole: each pigeon in exactly one hole",
            "generator": "generate_pigeonhole(6, 5)",
            "variant": "functional",
            "n_pigeons": 6,
            "n_holes": 5
        },
        "expected": "UNSAT (exponential proof)",
        "difficulty": "brutal",
        "rationale": "Functional PHP adds clauses saying each pigeon is in AT MOST one hole (in addition to at least one). This makes the encoding more constrained but doesn't change the fundamental exponential resolution lower bound. More clauses means more potential conflicts but also more search space."
    },

    {
        "test_id": "LOGIC_044",
        "category": "pigeonhole_variants",
        "input": {
            "type": "sat",
            "operation": "solve",
            "clauses": "Onto pigeonhole: each hole has at least one pigeon",
            "variant": "onto",
            "n_pigeons": 5,
            "n_holes": 6
        },
        "expected": "UNSAT (more holes than pigeons)",
        "difficulty": "brutal",
        "rationale": "Onto PHP requires each hole to contain at least one pigeon, plus the usual 'no two pigeons in same hole'. With more holes than pigeons, this is UNSAT by simple counting. But the SAT encoding requires deriving this counting argument through resolution, which is hard."
    },

    {
        "test_id": "LOGIC_045",
        "category": "pigeonhole_variants",
        "input": {
            "type": "sat",
            "operation": "solve",
            "clauses": "Weighted pigeonhole with cardinality constraints",
            "description": "Pigeons have sizes, holes have capacities",
            "n_pigeons": 10,
            "n_holes": 4,
            "pigeon_sizes": [2, 3, 1, 2, 2, 3, 1, 2, 2, 2],
            "hole_capacities": [5, 5, 5, 5]
        },
        "expected": "UNSAT (total size 20 > capacity 20-epsilon)",
        "difficulty": "extreme",
        "rationale": "Generalizing PHP to weighted assignment requires pseudo-boolean constraints (sums with integer coefficients). The SAT encoding uses binary counters or sorting networks, creating large formulas. Total pigeon size is 20, equal to total capacity, but actual assignment may still be impossible due to integer constraints."
    },

    {
        "test_id": "LOGIC_046",
        "category": "pigeonhole_variants",
        "input": {
            "type": "sat",
            "operation": "solve",
            "clauses": "Symmetric pigeonhole with random symmetry breaking",
            "n_pigeons": 9,
            "n_holes": 8,
            "symmetry_breaking": "random_partial"
        },
        "expected": "UNSAT (symmetry helps solver)",
        "difficulty": "brutal",
        "rationale": "PHP has extensive symmetry (pigeons are interchangeable, as are holes). Random partial symmetry breaking can either help (if it eliminates redundant search) or hurt (if it removes crucial symmetric witnesses). This tests whether the solver can exploit or is hindered by partial structure."
    },

    # =========================================================================
    # CATEGORY 9: GRAPH COLORING SAT ENCODINGS (Tests 047-049)
    # =========================================================================

    {
        "test_id": "LOGIC_047",
        "category": "graph_coloring_sat",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "3-color Petersen graph",
            "graph": "Petersen(10 vertices, 15 edges)",
            "n_colors": 3,
            "generator": "generate_graph_coloring_sat(10, 3, petersen_edges)"
        },
        "expected": "SAT (chromatic number is 3)",
        "difficulty": "brutal",
        "rationale": "The Petersen graph has chromatic number 3, so 3-coloring exists but is unique up to symmetry. Finding it requires navigating a constraint space of 3^10 = 59049 potential colorings with 15*3 = 45 edge exclusion constraints. The SAT solver must discover propagation chains efficiently."
    },

    {
        "test_id": "LOGIC_048",
        "category": "graph_coloring_sat",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "3-color random graph near colorability threshold",
            "graph": "Random G(50, 0.05) - near 3-colorability threshold",
            "n_vertices": 50,
            "edge_probability": 0.05,
            "n_colors": 3
        },
        "expected": "Borderline SAT/UNSAT",
        "difficulty": "extreme",
        "rationale": "Random graphs G(n,p) have a sharp colorability threshold. At edge density around p=0.05 for n=50, 3-colorability is marginal. Like SAT phase transition, instances here are maximally hard - the solver cannot easily determine colorability without extensive search."
    },

    {
        "test_id": "LOGIC_049",
        "category": "graph_coloring_sat",
        "input": {
            "type": "sat",
            "operation": "solve",
            "description": "Chromatic number of Latin square graph",
            "graph": "Latin_square_graph(n=4)",
            "n_vertices": 16,
            "n_colors": 4,
            "constraint": "Adjacent if same row/column or same symbol would create conflict"
        },
        "expected": "SAT (constructs Latin square)",
        "difficulty": "extreme",
        "rationale": "Graph coloring the Latin square construction graph is equivalent to constructing a valid Latin square. For n=4, there are 576 distinct Latin squares but a naive SAT encoding doesn't exploit this structure. The solver must find one of 576 needles in a 4^16 = 4 billion assignment haystack."
    },

    # =========================================================================
    # CATEGORY 10: INTUITIONISTIC LOGIC PROOFS (Test 050)
    # =========================================================================

    {
        "test_id": "LOGIC_050",
        "category": "intuitionistic_logic",
        "input": {
            "type": "intuitionistic",
            "operation": "prove",
            "formula": "not not (P or not P)",
            "description": "Double negation of excluded middle",
            "system": "intuitionistic_propositional"
        },
        "expected": "PROVABLE (but P or not P is not)",
        "difficulty": "pathological",
        "rationale": "In intuitionistic logic, P or not P (excluded middle) is NOT provable, but its double negation IS provable. This tests whether the system understands the distinction between classical and intuitionistic validity. The current propositional specialist implements classical logic only, treating double negation elimination as valid. An intuitionistic proof requires Kripke semantics where not all worlds know P or not P."
    },
]


# ============================================================================
# TEST SUMMARY AND STATISTICS
# ============================================================================

def get_test_summary() -> Dict[str, Any]:
    """Return summary statistics of the test suite."""
    categories = {}
    difficulties = {"brutal": 0, "extreme": 0, "pathological": 0}

    for test in BRUTAL_LOGIC_TESTS:
        cat = test["category"]
        diff = test["difficulty"]
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

    return {
        "total_tests": len(BRUTAL_LOGIC_TESTS),
        "by_category": categories,
        "by_difficulty": difficulties,
        "expected_failures": [
            "LOGIC_003 (100-var phase transition - pathological)",
            "LOGIC_011 (6-alternation QBF - pathological)",
            "LOGIC_012 (Game-theoretic QBF - pathological)",
            "LOGIC_014 (Skolem function counting - pathological)",
            "LOGIC_025 (CTL* - requires unsupported logic)",
            "LOGIC_026 (LTL synthesis - 2EXPTIME-complete)",
            "LOGIC_035 (PHP(12,11) - exponential proof)",
            "LOGIC_042 (Factoring as SAT - cryptographic)",
            "LOGIC_050 (Intuitionistic logic - unsupported)",
        ],
        "specialist_gaps_exposed": [
            "No QBF support (PredicateLogicSpecialist only handles finite domains)",
            "No Skolemization (first-order theorem proving impossible)",
            "No occurs check in unification (soundness issue)",
            "Modal logic limited to 6 systems (missing GL, multi-modal)",
            "CTL* not supported (only pure LTL or CTL)",
            "No synthesis capability (only model checking)",
            "Classical logic only (no intuitionistic support)",
            "max_worlds=8 limit (modal completeness compromised)",
            "Bounded model checking (cannot prove liveness properties)",
            "No symmetry breaking (pigeonhole/graph coloring struggle)",
        ]
    }


# ============================================================================
# HELPER: CONVERT TESTS TO EXECUTABLE FORMAT
# ============================================================================

def create_executable_test_cases():
    """
    Create executable test cases for pytest.
    Returns list of (test_id, test_fn) tuples.
    """
    # Implementation would go here for actual test execution
    # This is a generator module, not an execution module
    pass


if __name__ == "__main__":
    summary = get_test_summary()
    print("=" * 70)
    print("BRUTAL LOGIC DOMAIN STRESS TESTS - SUMMARY")
    print("=" * 70)
    print(f"Total tests: {summary['total_tests']}")
    print("\nBy difficulty:")
    for diff, count in summary['by_difficulty'].items():
        print(f"  {diff}: {count}")
    print("\nBy category:")
    for cat, count in sorted(summary['by_category'].items()):
        print(f"  {cat}: {count}")
    print("\nExpected hard failures:")
    for failure in summary['expected_failures']:
        print(f"  - {failure}")
    print("\nSpecialist capability gaps exposed:")
    for gap in summary['specialist_gaps_exposed']:
        print(f"  * {gap}")
