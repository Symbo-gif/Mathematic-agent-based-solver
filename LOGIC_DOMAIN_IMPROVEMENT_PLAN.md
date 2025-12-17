# Logic Domain Improvement Plan: 60% → 90%+ Capability

**Author:** Claude Opus 4.5
**Date:** 2025-12-15
**Current Score:** 60/100
**Target Score:** 90+/100
**Current Specialists:** 3 (PropositionalLogicSpecialist, PredicateLogicSpecialist, ProofSpecialist)

---

## Executive Summary

The Logic domain currently scores 60/100 with only 3 specialists covering basic propositional logic, first-order predicate logic, and proof verification. To reach 90%+ capability, we need to expand into **8 critical logic subsystems** with **11 new specialists** implementing advanced reasoning algorithms using pure Python (NO SYMPY).

**Key Gaps Identified:**
1. **Modal Logic** (necessity/possibility operators)
2. **Temporal Logic** (time-based reasoning)
3. **Fuzzy Logic** (partial truth)
4. **Description Logic** (knowledge representation)
5. **Constraint Satisfaction** (CSP solving)
6. **Advanced SAT/SMT** (satisfiability modulo theories)
7. **Automated Theorem Proving** (advanced proof search)
8. **Logic Programming** (Prolog-style inference)

---

## Current State Analysis

### Existing Specialists (3)

#### 1. **PropositionalLogicSpecialist** (`propositional_specialist.py`)
**Capabilities:**
- Truth table generation (all boolean combinations)
- Logical equivalence checking
- Tautology/contradiction/satisfiability detection
- Basic inference rules (modus ponens, modus tollens)
- Safe AST-based expression evaluation (no eval())

**Limitations:**
- No CNF/DNF conversion implementation (claimed but missing)
- Basic SAT solver (exhaustive search only, O(2^n))
- No DPLL or CDCL algorithms
- No Boolean constraint propagation
- No circuit SAT or optimization

**Coverage:** ~50% of propositional logic capabilities

---

#### 2. **PredicateLogicSpecialist** (`predicate_specialist.py`)
**Capabilities:**
- Universal/existential quantification over finite domains
- Predicate evaluation with safe lambda parsing
- Basic unification (term matching)
- Substitution and quantifier negation
- Count quantification

**Limitations:**
- Only finite domain support (no infinite domains)
- Primitive unification (no occurs check, no full algorithm)
- No Skolemization
- No Herbrand universe construction
- No resolution for FOL
- No prenex normal form implementation
- No clause form conversion

**Coverage:** ~40% of first-order logic capabilities

---

#### 3. **ProofSpecialist** (`proof_specialist.py`)
**Capabilities:**
- Direct proof verification (step validation)
- Mathematical induction (base + inductive step)
- Strong induction
- Proof by contradiction/contrapositive
- Case analysis
- Basic inference rule registry

**Limitations:**
- Manual proof checking only (requires human-provided steps)
- No automated proof search
- No tactic application
- No proof term construction
- No semantic tableau method
- No sequent calculus
- Limited to 9 inference rules

**Coverage:** ~35% of proof theory capabilities

---

#### 4. **LogicalProver** (Phase 6, `provers/logical_prover.py`)
**Capabilities:**
- Natural deduction (basic modus ponens, conjunction intro)
- Resolution refutation (simplified, clause form)
- Proof tree construction
- Proof caching

**Limitations:**
- Very basic proof search (no heuristics)
- Resolution only handles unit clauses
- No factoring, subsumption, or paramodulation
- No backward/forward chaining
- No semantic guidance
- Timeout-prone on complex goals

**Coverage:** ~45% of automated reasoning capabilities

---

### Test Coverage Analysis

**File:** `tests/test_logic_specialists.py`

**Problems:**
- Only 17 tests total (6 per specialist)
- Tests only check method existence, not functionality
- No algorithmic correctness tests
- No edge case testing
- No performance benchmarks
- No integration with LogicSupervisor testing

**Test Coverage:** ~10% of logic functionality tested

---

## Gap Analysis: Missing Logic Systems

### 1. **Modal Logic** (0% coverage)

**What's Missing:**
- Possible worlds semantics
- Accessibility relations
- Necessity (□) and possibility (◇) operators
- Modal axiom systems: K, T, S4, S5
- Kripke models
- Modal proof systems (K-axiom, necessitation rule)

**Applications:**
- Epistemic logic (knowledge representation)
- Doxastic logic (belief systems)
- Deontic logic (obligation/permission)
- Multi-agent systems
- Security protocol verification

**Algorithms Needed:**
- Kripke model construction
- Modal tableau method
- Bisimulation checking
- Frame correspondence
- Translation to FOL

---

### 2. **Temporal Logic** (0% coverage)

**What's Missing:**
- Linear Temporal Logic (LTL)
- Computation Tree Logic (CTL/CTL*)
- Temporal operators: G (always), F (eventually), X (next), U (until)
- Model checking algorithms
- Büchi automata

**Applications:**
- Reactive system verification
- Hardware/software specification
- Planning and scheduling
- Workflow verification
- Real-time system reasoning

**Algorithms Needed:**
- LTL to Büchi automaton conversion
- CTL model checking (SAT-based)
- Bounded model checking
- Tableau for temporal logic
- Path quantifier elimination

---

### 3. **Fuzzy Logic** (0% coverage)

**What's Missing:**
- Fuzzy membership functions
- Fuzzy inference (Mamdani, Sugeno)
- Fuzzy operators (t-norms, t-conorms)
- Defuzzification methods
- Fuzzy rule bases

**Applications:**
- Approximate reasoning
- Control systems
- Decision making under uncertainty
- Natural language processing
- Pattern recognition

**Algorithms Needed:**
- Membership function evaluation
- Compositional rule of inference
- Centroid defuzzification
- Fuzzy clustering
- Linguistic variable handling

---

### 4. **Description Logic** (0% coverage)

**What's Missing:**
- ALC (Attributive Language with Complements)
- Concepts and roles
- TBox (terminological) and ABox (assertional) reasoning
- Subsumption checking
- Instance checking
- Consistency checking

**Applications:**
- Ontology reasoning (OWL)
- Semantic web
- Knowledge graphs
- Database schema reasoning
- Information integration

**Algorithms Needed:**
- Tableau for ALC
- Concept normalization
- Role expansion
- Blocking for termination
- Classification algorithms

---

### 5. **Constraint Satisfaction Problems (CSP)** (0% coverage)

**What's Missing:**
- Variable domains and constraints
- Arc consistency (AC-3, AC-4)
- Backtracking search
- Constraint propagation
- Global constraints (all-different, etc.)

**Applications:**
- Scheduling problems
- Resource allocation
- Sudoku solving
- Graph coloring
- Configuration problems

**Algorithms Needed:**
- AC-3 arc consistency
- Backjumping
- Forward checking
- Conflict-directed backjumping
- Constraint learning

---

### 6. **Advanced SAT/SMT Solving** (5% coverage)

**Current:** Basic exhaustive SAT in PropositionalLogicSpecialist

**What's Missing:**
- DPLL algorithm (Davis-Putnam-Logemann-Loveland)
- Conflict-Driven Clause Learning (CDCL)
- Unit propagation
- Pure literal elimination
- Watched literals
- SMT theories: integer arithmetic, arrays, bit-vectors
- Theory solvers integration

**Applications:**
- Formal verification
- Bounded model checking
- Program analysis
- Test case generation
- Planning

**Algorithms Needed:**
- DPLL with backtracking
- Conflict analysis and clause learning
- Restart strategies
- Decision heuristics (VSIDS)
- Theory propagation (SMT)
- Nelson-Oppen combination

---

### 7. **Advanced Automated Theorem Proving** (15% coverage)

**Current:** Basic resolution in LogicalProver

**What's Missing:**
- Complete resolution for FOL
- Paramodulation (equality reasoning)
- Rewriting systems
- Completion procedures (Knuth-Bendix)
- Higher-order unification
- Semantic guidance
- Proof reconstruction

**Applications:**
- Mathematical theorem proving
- Software verification
- Hardware verification
- Formal mathematics
- Proof assistants

**Algorithms Needed:**
- Robinson's resolution
- Factoring and subsumption
- Set-of-support strategy
- Paramodulation with ordering
- Superposition calculus
- E-matching for quantifier instantiation

---

### 8. **Logic Programming** (0% coverage)

**What's Missing:**
- Prolog-style backward chaining
- Horn clause resolution
- SLD resolution (Selective Linear Definite clause)
- Unification with occurs check
- Negation as failure
- Constraint logic programming

**Applications:**
- Expert systems
- Natural language processing
- Symbolic AI
- Database queries
- Planning

**Algorithms Needed:**
- SLD resolution with backtracking
- Full unification algorithm (with occurs check)
- Cut (!) implementation
- Negation as failure
- Tabling/memoization
- Answer set programming

---

## Proposed New Specialists (11 Agents)

### Architecture Compliance

All new specialists must:
1. **NO SYMPY** - Pure Python implementations only
2. **BDI Pattern** - Implement `update_beliefs()`, `deliberate()`, `execute_step()`
3. **Service Registration** - Register with DirectoryFacilitator
4. **Tier 3** - Computational specialists (not routers)
5. **Lazy Loading** - Avoid circular dependencies
6. **Blackboard Integration** - Query/post entries for coordination

---

### Specialist #1: **ModalLogicSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/modal_logic_specialist.py`

**Service Type:** `math.logic.modal`

**Capabilities:**
- Kripke model construction and evaluation
- Modal formula parsing (□, ◇ operators)
- Modal tableau proof search
- Frame axiom verification (K, T, S4, S5)
- Bisimulation checking
- Accessibility relation analysis

**Key Algorithms (Pure Python):**
```python
class KripkeModel:
    """
    Kripke model: (W, R, V)
    - W: set of possible worlds
    - R: accessibility relation (dict of sets)
    - V: valuation function (dict world -> dict prop -> bool)
    """

def modal_tableau(formula: ModalFormula, frame_axioms: Set[str]) -> ProofResult:
    """
    Semantic tableau for modal logic
    - Expand using modal rules
    - Track world accessibility
    - Detect contradictions or construct countermodel
    """

def check_frame_axiom(model: KripkeModel, axiom: str) -> bool:
    """
    Verify frame properties:
    - T: reflexive (∀w: wRw)
    - 4: transitive (∀u,v,w: uRv ∧ vRw → uRw)
    - 5: euclidean (∀u,v,w: uRv ∧ uRw → vRw)
    - B: symmetric (∀u,v: uRv → vRu)
    """
```

**Operations:**
- `operation='evaluate'` - Evaluate modal formula in Kripke model
- `operation='tableau'` - Prove/refute using modal tableau
- `operation='frame_check'` - Verify frame properties
- `operation='bisimulation'` - Check modal equivalence
- `operation='translate_fol'` - Convert to first-order logic

**Expected Performance:**
- Small models (< 20 worlds): < 100ms
- Medium models (< 100 worlds): < 1s
- Tableau depth limit: 50

---

### Specialist #2: **TemporalLogicSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/temporal_logic_specialist.py`

**Service Type:** `math.logic.temporal`

**Capabilities:**
- LTL formula parsing (G, F, X, U operators)
- CTL formula parsing (EG, EF, AG, AF, etc.)
- Model checking for finite state systems
- Büchi automaton construction (LTL)
- Bounded model checking

**Key Algorithms (Pure Python):**
```python
class TransitionSystem:
    """
    Kripke structure: (S, S0, R, L)
    - S: states
    - S0: initial states
    - R: transition relation
    - L: labeling function (state -> propositions)
    """

def ltl_to_buchi(ltl_formula: LTLFormula) -> BuchiAutomaton:
    """
    Convert LTL formula to Büchi automaton
    - Use tableau-based construction
    - Build states from formula closures
    - Define acceptance conditions
    """

def ctl_model_check(system: TransitionSystem, ctl_formula: CTLFormula) -> bool:
    """
    CTL model checking algorithm
    - Bottom-up evaluation
    - SAT set computation for subformulas
    - Fixed-point iteration for EG/AF
    """
```

**Operations:**
- `operation='ltl_check'` - LTL model checking
- `operation='ctl_check'` - CTL model checking
- `operation='bmc'` - Bounded model checking (k steps)
- `operation='ltl_to_buchi'` - Convert LTL to automaton
- `operation='generate_counterexample'` - Extract trace

**Expected Performance:**
- State space < 1000 states: < 500ms
- LTL to Büchi: < 200ms for formulas with < 10 operators
- BMC depth: up to 30 steps

---

### Specialist #3: **FuzzyLogicSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/fuzzy_logic_specialist.py`

**Service Type:** `math.logic.fuzzy`

**Capabilities:**
- Fuzzy set operations (union, intersection, complement)
- Membership function evaluation (triangular, trapezoidal, gaussian)
- Fuzzy inference (Mamdani, Sugeno)
- Defuzzification (centroid, bisector, MOM)
- Fuzzy rule base evaluation

**Key Algorithms (Pure Python):**
```python
class FuzzySet:
    """
    Fuzzy set with membership function
    - universe: domain of discourse
    - membership_func: callable x -> [0, 1]
    """

def triangular_mf(x: float, a: float, b: float, c: float) -> float:
    """Triangular membership function"""
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)

def mamdani_inference(rules: List[FuzzyRule], inputs: Dict[str, float]) -> FuzzySet:
    """
    Mamdani fuzzy inference
    1. Fuzzification
    2. Rule evaluation (min for AND)
    3. Aggregation (max of outputs)
    4. Return aggregated fuzzy set
    """

def centroid_defuzzification(fuzzy_set: FuzzySet, samples: int = 100) -> float:
    """
    Centroid defuzzification
    - Integrate membership * x / integrate membership
    - Use discrete approximation
    """
```

**Operations:**
- `operation='evaluate_membership'` - Compute membership value
- `operation='fuzzy_inference'` - Apply fuzzy rules
- `operation='defuzzify'` - Convert fuzzy output to crisp
- `operation='fuzzy_union'` - Compute union of sets
- `operation='fuzzy_implication'` - Apply fuzzy implication

**Expected Performance:**
- Membership evaluation: < 1ms
- Rule base (< 50 rules): < 50ms
- Defuzzification: < 20ms

---

### Specialist #4: **DescriptionLogicSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/description_logic_specialist.py`

**Service Type:** `math.logic.description`

**Capabilities:**
- ALC concept parsing and normalization
- Subsumption checking (C ⊑ D)
- Instance checking (a : C)
- Consistency checking (TBox + ABox)
- Concept satisfiability
- Classification (compute hierarchy)

**Key Algorithms (Pure Python):**
```python
class Concept:
    """
    ALC concept
    - Atomic: Thing, Nothing, concept_name
    - Negation: ¬C
    - Conjunction: C ⊓ D
    - Disjunction: C ⊔ D
    - Existential: ∃R.C
    - Universal: ∀R.C
    """

def normalize_concept(concept: Concept) -> Concept:
    """
    Convert to negation normal form
    - Push negations inward
    - Eliminate implications
    """

def alc_tableau(concept: Concept, tbox: TBox) -> TableauResult:
    """
    Tableau algorithm for ALC
    - Apply expansion rules
    - Track individual nodes
    - Implement blocking for termination
    - Detect clashes
    """

def subsumption_check(c1: Concept, c2: Concept, tbox: TBox) -> bool:
    """
    Check C1 ⊑ C2
    - Equivalent to checking C1 ⊓ ¬C2 unsatisfiable
    - Use tableau
    """
```

**Operations:**
- `operation='subsumption'` - C ⊑ D checking
- `operation='satisfiability'` - Concept satisfiability
- `operation='instance_check'` - a : C
- `operation='consistency'` - KB consistency
- `operation='classify'` - Build concept hierarchy

**Expected Performance:**
- Simple subsumption: < 50ms
- Complex concepts (depth < 5): < 500ms
- Blocking limit: 100 nodes

---

### Specialist #5: **ConstraintSatisfactionSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/constraint_satisfaction_specialist.py`

**Service Type:** `math.logic.csp`

**Capabilities:**
- CSP problem definition and solving
- Arc consistency (AC-3 algorithm)
- Backtracking search with pruning
- Forward checking
- Constraint propagation
- Global constraints (all-different, etc.)

**Key Algorithms (Pure Python):**
```python
class CSP:
    """
    Constraint Satisfaction Problem
    - variables: set of variable names
    - domains: dict var -> set of values
    - constraints: list of Constraint objects
    """

def ac3(csp: CSP) -> Tuple[bool, CSP]:
    """
    AC-3 arc consistency algorithm
    - Maintain queue of arcs (Xi, Xj)
    - Remove inconsistent values from domains
    - Return (consistent, reduced_csp)
    """

def backtracking_search(csp: CSP, assignment: Dict = None) -> Optional[Dict]:
    """
    Backtracking search with heuristics
    - Select unassigned variable (MRV heuristic)
    - Order domain values (LCV heuristic)
    - Apply forward checking
    - Return solution or None
    """

def all_different_constraint(variables: List[str]) -> Constraint:
    """
    Global all-different constraint
    - All variables must have different values
    - Optimized propagation
    """
```

**Operations:**
- `operation='solve'` - Find CSP solution
- `operation='ac3'` - Apply arc consistency
- `operation='all_solutions'` - Enumerate all solutions
- `operation='optimize'` - Find optimal solution (with objective)
- `operation='check_consistency'` - Check if CSP is consistent

**Expected Performance:**
- Small CSPs (< 20 vars): < 100ms
- Medium CSPs (< 100 vars): < 5s
- AC-3 iterations: typically < 50

---

### Specialist #6: **SATSolverSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/sat_solver_specialist.py`

**Service Type:** `math.logic.sat`

**Capabilities:**
- DPLL algorithm
- Conflict-Driven Clause Learning (CDCL)
- Unit propagation
- Pure literal elimination
- VSIDS decision heuristic
- Clause learning and minimization

**Key Algorithms (Pure Python):**
```python
class CNFFormula:
    """
    Formula in Conjunctive Normal Form
    - clauses: list of sets of literals
    - n_vars: number of variables
    """

def dpll(formula: CNFFormula, assignment: Dict[int, bool] = None) -> Tuple[bool, Optional[Dict]]:
    """
    DPLL SAT solver
    1. Unit propagation
    2. Pure literal elimination
    3. Choose literal (heuristic)
    4. Recursively try assignment
    """

def cdcl_solve(formula: CNFFormula) -> SATResult:
    """
    CDCL SAT solver
    - Two-watched literals data structure
    - Conflict analysis (1-UIP scheme)
    - Clause learning
    - Backjumping
    - Restarts
    """

def unit_propagate(formula: CNFFormula, assignment: Dict) -> Tuple[bool, Dict]:
    """
    Boolean constraint propagation
    - Find unit clauses (all but one literal assigned)
    - Force remaining literal
    - Detect conflicts
    """
```

**Operations:**
- `operation='solve'` - SAT solving
- `operation='dpll'` - DPLL algorithm
- `operation='cdcl'` - CDCL algorithm
- `operation='max_sat'` - Maximum satisfiability
- `operation='all_sat'` - Enumerate all solutions (up to limit)

**Expected Performance:**
- Small formulas (< 100 clauses): < 50ms
- Medium formulas (< 1000 clauses): < 1s
- Industrial instances: may timeout (5s limit)

---

### Specialist #7: **SMTSolverSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/smt_solver_specialist.py`

**Service Type:** `math.logic.smt`

**Capabilities:**
- Linear integer arithmetic (LIA)
- Equality with uninterpreted functions (EUF)
- Theory combination (Nelson-Oppen)
- Lazy SMT solving (DPLL(T))
- Theory propagation

**Key Algorithms (Pure Python):**
```python
class SMTTheory:
    """
    Abstract SMT theory
    - check_sat: partial assignment -> conflict clause or None
    - propagate: partial assignment -> implied literals
    """

class LinearArithmeticTheory(SMTTheory):
    """
    Linear integer/real arithmetic
    - Simplex-based checking
    - Bounds propagation
    """

def dpll_t(formula: CNFFormula, theory: SMTTheory) -> SMTResult:
    """
    DPLL(T) algorithm
    1. SAT solver suggests assignment
    2. Theory solver checks consistency
    3. If inconsistent, learn conflict clause
    4. Iterate until SAT + theory-consistent or UNSAT
    """

def simplex_check(constraints: List[LinearConstraint]) -> Tuple[bool, Optional[Dict]]:
    """
    Simplex algorithm for linear arithmetic
    - Check feasibility of linear constraints
    - Return satisfying assignment or infeasibility proof
    """
```

**Operations:**
- `operation='solve'` - SMT solving
- `operation='theory_check'` - Check theory consistency
- `operation='lia_solve'` - Linear integer arithmetic
- `operation='euf_solve'` - Equality with uninterpreted functions
- `operation='theory_combine'` - Combined theories

**Expected Performance:**
- Simple constraints (< 20): < 100ms
- Theory checking: < 50ms per call
- Complex problems: may timeout (10s limit)

---

### Specialist #8: **TheoremProvingSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/theorem_proving_specialist.py`

**Service Type:** `math.logic.atp`

**Capabilities:**
- Full resolution for FOL
- Paramodulation (equality)
- Subsumption and simplification
- Set-of-support strategy
- Demodulation
- Proof reconstruction

**Key Algorithms (Pure Python):**
```python
class Clause:
    """
    First-order clause (disjunction of literals)
    - literals: list of Literal objects
    - weight: for ordering
    """

def resolution(c1: Clause, c2: Clause) -> List[Clause]:
    """
    Binary resolution
    - Find complementary literals
    - Unify and resolve
    - Return resolvents
    """

def paramodulation(c1: Clause, c2: Clause, ordering) -> List[Clause]:
    """
    Paramodulation inference rule
    - Equality l=r in c1
    - Replace occurrence of l in c2 with r
    - Return new clauses
    """

def subsumes(c1: Clause, c2: Clause) -> bool:
    """
    Subsumption check
    - c1 subsumes c2 if c1 is "more general"
    - Use unification
    """

def sos_prover(axioms: List[Clause], negated_goal: Clause, max_iter: int) -> ProofResult:
    """
    Set-of-support strategy
    - Maintain SOS (set of support) and usable clauses
    - Prefer inferences involving SOS clauses
    - Apply resolution, paramodulation, subsumption
    """
```

**Operations:**
- `operation='prove'` - Automated theorem proving
- `operation='resolution'` - Resolution inference
- `operation='paramodulation'` - Equality reasoning
- `operation='refute'` - Refutation proof
- `operation='reconstruct_proof'` - Generate human-readable proof

**Expected Performance:**
- Simple theorems: < 500ms
- Medium theorems (depth < 10): < 5s
- Complex theorems: may timeout (30s limit)

---

### Specialist #9: **LogicProgrammingSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/logic_programming_specialist.py`

**Service Type:** `math.logic.prolog`

**Capabilities:**
- Prolog-style query answering
- SLD resolution (backward chaining)
- Full unification with occurs check
- Negation as failure
- Horn clause reasoning
- Answer extraction

**Key Algorithms (Pure Python):**
```python
class HornClause:
    """
    Horn clause: head :- body1, body2, ..., bodyN
    - head: single atom or None (for queries)
    - body: list of atoms
    """

def unify(term1: Term, term2: Term, subst: Dict = None) -> Optional[Dict]:
    """
    Full unification algorithm
    - Robinson's unification with occurs check
    - Return most general unifier (MGU) or None
    """

def sld_resolution(query: List[Atom], kb: List[HornClause]) -> List[Dict]:
    """
    SLD resolution (Selective Linear Definite clause)
    - Backward chaining from query
    - Select goal, unify with clause head
    - Substitute and add body goals
    - Backtrack on failure
    - Return all answers
    """

def negation_as_failure(goal: Atom, kb: List[HornClause]) -> bool:
    """
    Negation as failure
    - Try to prove goal
    - If fails, return True (not provable)
    - If succeeds, return False
    """
```

**Operations:**
- `operation='query'` - Answer Prolog query
- `operation='unify'` - Term unification
- `operation='prove'` - Prove goal from Horn clauses
- `operation='all_answers'` - Find all solutions
- `operation='naf'` - Negation as failure

**Expected Performance:**
- Simple queries (depth < 10): < 100ms
- Recursive queries: < 1s (with depth limit 50)
- Backtracking branches: up to 1000

---

### Specialist #10: **EquationalReasoningSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/equational_reasoning_specialist.py`

**Service Type:** `math.logic.equality`

**Capabilities:**
- Equality reasoning
- Rewrite rule application
- Knuth-Bendix completion
- Congruence closure
- E-matching for quantifier instantiation

**Key Algorithms (Pure Python):**
```python
class RewriteRule:
    """
    Rewrite rule: lhs -> rhs
    - lhs: left-hand side term
    - rhs: right-hand side term
    - conditions: optional conditions
    """

def rewrite(term: Term, rules: List[RewriteRule]) -> Term:
    """
    Apply rewrite rules to term
    - Match lhs pattern
    - Substitute and replace with rhs
    - Repeat until no rule applies
    """

def congruence_closure(equations: List[Tuple[Term, Term]]) -> EquivalenceClasses:
    """
    Congruence closure algorithm
    - Build equivalence classes of terms
    - Propagate equalities through function symbols
    - Detect contradictions
    """

def knuth_bendix(equations: List[Equation], ordering) -> List[RewriteRule]:
    """
    Knuth-Bendix completion
    - Orient equations into rewrite rules
    - Compute critical pairs
    - Add new rules until confluent
    - May not terminate
    """
```

**Operations:**
- `operation='rewrite'` - Apply rewrite rules
- `operation='congruence_closure'` - Equality reasoning
- `operation='completion'` - Knuth-Bendix completion
- `operation='e_matching'` - Quantifier instantiation
- `operation='normalize'` - Normalize term to canonical form

**Expected Performance:**
- Rewriting (< 10 rules): < 20ms
- Congruence closure (< 100 terms): < 200ms
- Completion: may not terminate (iteration limit 100)

---

### Specialist #11: **HigherOrderLogicSpecialist**

**File:** `src/symbo_agentic_reasoners/agents/specialists/logic/higher_order_logic_specialist.py`

**Service Type:** `math.logic.hol`

**Capabilities:**
- Simple type theory
- Lambda calculus (beta/eta reduction)
- Higher-order unification (pattern fragment)
- Type checking and inference
- Polymorphic types

**Key Algorithms (Pure Python):**
```python
class Type:
    """
    Simple type
    - TVar: type variable
    - TConst: base type (bool, nat, etc.)
    - TApp: type application (List[int])
    - TArrow: function type (a -> b)
    """

class LambdaTerm:
    """
    Lambda term
    - Var: variable
    - App: application (f x)
    - Abs: abstraction (λx. e)
    - Const: constant
    """

def beta_reduce(term: LambdaTerm) -> LambdaTerm:
    """
    Beta reduction (λx. e) y -> e[y/x]
    - Substitute and simplify
    - Repeat until normal form
    """

def type_infer(term: LambdaTerm, context: Dict[str, Type]) -> Type:
    """
    Type inference (Hindley-Milner style)
    - Generate constraints
    - Solve by unification
    - Return principal type
    """

def ho_unify(term1: LambdaTerm, term2: LambdaTerm) -> Optional[Dict]:
    """
    Higher-order unification (pattern fragment)
    - Restricted to ensure decidability
    - Return substitution or None
    """
```

**Operations:**
- `operation='beta_reduce'` - Lambda reduction
- `operation='type_check'` - Type checking
- `operation='type_infer'` - Type inference
- `operation='ho_unify'` - Higher-order unification
- `operation='eta_expand'` - Eta expansion

**Expected Performance:**
- Beta reduction (depth < 20): < 50ms
- Type inference (term size < 100): < 100ms
- HO unification: < 200ms (pattern fragment only)

---

## Updates to LogicSupervisor

**File:** `src/symbo_agentic_reasoners/agents/supervisors/logic_supervisor.py`

**New Routing Keywords:**

```python
# Modal logic
MODAL_KEYWORDS = [
    'modal', 'necessity', 'possibility', 'kripke', 'possible world',
    'accessible', 'epistemic', 'doxastic', 'deontic', '□', '◇'
]

# Temporal logic
TEMPORAL_KEYWORDS = [
    'temporal', 'ltl', 'ctl', 'always', 'eventually', 'until', 'next',
    'liveness', 'safety', 'fairness', 'model check', 'büchi'
]

# Fuzzy logic
FUZZY_KEYWORDS = [
    'fuzzy', 'membership', 'defuzzify', 'linguistic', 'mamdani',
    'sugeno', 'approximate', 'partial truth'
]

# Description logic
DESCRIPTION_KEYWORDS = [
    'description logic', 'ontology', 'concept', 'role', 'subsumption',
    'tbox', 'abox', 'alc', 'owl'
]

# CSP
CSP_KEYWORDS = [
    'constraint', 'csp', 'arc consistency', 'backtracking', 'sudoku',
    'scheduling', 'all different', 'propagation'
]

# SAT/SMT
SAT_KEYWORDS = [
    'sat', 'satisfiability', 'dpll', 'cdcl', 'cnf', 'clause learning',
    'smt', 'theory', 'linear arithmetic'
]

# Automated theorem proving
ATP_KEYWORDS = [
    'theorem', 'automated', 'resolution', 'paramodulation', 'first order',
    'fol', 'refutation', 'subsumption'
]

# Logic programming
PROLOG_KEYWORDS = [
    'prolog', 'horn', 'backward chaining', 'sld', 'logic programming',
    'query', 'clause', 'unification'
]

# Equality reasoning
EQUALITY_KEYWORDS = [
    'equality', 'rewrite', 'congruence', 'knuth bendix', 'completion',
    'e-matching', 'equational'
]

# Higher-order logic
HOL_KEYWORDS = [
    'higher order', 'lambda', 'type theory', 'polymorphic', 'beta reduce',
    'curry howard'
]
```

**Updated Routing Logic:**

```python
def route_task(self, task: Dict[str, Any]) -> str:
    """Determine which specialist should handle the task."""
    problem = str(task.get('problem', '')).lower()
    operation = str(task.get('operation', '')).lower()

    # Check in order of specificity
    keyword_map = [
        (self.MODAL_KEYWORDS, 'math.logic.modal'),
        (self.TEMPORAL_KEYWORDS, 'math.logic.temporal'),
        (self.FUZZY_KEYWORDS, 'math.logic.fuzzy'),
        (self.DESCRIPTION_KEYWORDS, 'math.logic.description'),
        (self.CSP_KEYWORDS, 'math.logic.csp'),
        (self.SAT_KEYWORDS, 'math.logic.sat'),
        (self.ATP_KEYWORDS, 'math.logic.atp'),
        (self.PROLOG_KEYWORDS, 'math.logic.prolog'),
        (self.EQUALITY_KEYWORDS, 'math.logic.equality'),
        (self.HOL_KEYWORDS, 'math.logic.hol'),
        (self.PROOF_KEYWORDS, 'math.logic.proof'),
        (self.PREDICATE_KEYWORDS, 'math.logic.predicate'),
        (self.PROPOSITIONAL_KEYWORDS, 'math.logic.propositional'),
    ]

    for keywords, service_type in keyword_map:
        for keyword in keywords:
            if keyword in problem or keyword in operation:
                return service_type

    # Default to propositional
    return 'math.logic.propositional'
```

---

## Testing Strategy

### Test File Structure

```
tests/
├── test_logic_specialists.py (existing - expand)
├── test_modal_logic.py (NEW)
├── test_temporal_logic.py (NEW)
├── test_fuzzy_logic.py (NEW)
├── test_description_logic.py (NEW)
├── test_csp_solver.py (NEW)
├── test_sat_smt_solvers.py (NEW)
├── test_theorem_proving.py (NEW)
├── test_logic_programming.py (NEW)
├── test_equational_reasoning.py (NEW)
├── test_higher_order_logic.py (NEW)
└── integration/
    └── test_logic_integration.py (NEW)
```

### Test Coverage Goals

**Unit Tests (per specialist):**
- Algorithm correctness: 20 tests
- Edge cases: 10 tests
- Performance benchmarks: 5 tests
- Error handling: 5 tests
- **Total: 40 tests per specialist**

**Integration Tests:**
- LogicSupervisor routing: 15 tests
- Multi-specialist coordination: 10 tests
- Blackboard integration: 10 tests
- End-to-end scenarios: 15 tests
- **Total: 50 integration tests**

**Overall Test Count:**
- Existing logic tests: 17
- New specialist tests: 11 × 40 = 440
- Integration tests: 50
- **Grand Total: 507 logic tests**

---

## Implementation Timeline

### Phase 1: Foundation (Week 1-2)
**Specialists:** SAT, CSP, Logic Programming

**Rationale:** These are foundational and relatively self-contained

**Deliverables:**
1. SATSolverSpecialist with DPLL + basic CDCL
2. ConstraintSatisfactionSpecialist with AC-3 + backtracking
3. LogicProgrammingSpecialist with SLD resolution + unification
4. 120 unit tests (40 each)
5. Updated LogicSupervisor routing

**Acceptance Criteria:**
- All tests passing
- Benchmarks: 3-SAT instances < 1s, CSP sudoku < 100ms, Prolog queries < 50ms

---

### Phase 2: Modal & Temporal (Week 3-4)
**Specialists:** Modal Logic, Temporal Logic

**Rationale:** Related semantics (possible worlds)

**Deliverables:**
1. ModalLogicSpecialist with Kripke models + tableau
2. TemporalLogicSpecialist with LTL/CTL model checking
3. 80 unit tests (40 each)
4. Integration tests for modal/temporal interaction

**Acceptance Criteria:**
- Modal formulas in S5 decidable
- LTL model checking for 20-state systems < 500ms

---

### Phase 3: Knowledge Representation (Week 5-6)
**Specialists:** Description Logic, Fuzzy Logic

**Rationale:** Both used for knowledge representation

**Deliverables:**
1. DescriptionLogicSpecialist with ALC tableau
2. FuzzyLogicSpecialist with Mamdani/Sugeno inference
3. 80 unit tests
4. Ontology reasoning examples

**Acceptance Criteria:**
- ALC subsumption checking for depth-5 concepts < 500ms
- Fuzzy inference with 20 rules < 50ms

---

### Phase 4: Advanced Reasoning (Week 7-8)
**Specialists:** SMT, Theorem Proving, Equational Reasoning

**Rationale:** Advanced automated reasoning techniques

**Deliverables:**
1. SMTSolverSpecialist with LIA theory
2. TheoremProvingSpecialist with resolution + paramodulation
3. EquationalReasoningSpecialist with congruence closure
4. 120 unit tests
5. Integration with existing ProofSpecialist

**Acceptance Criteria:**
- SMT solving for 20-constraint LIA problems < 500ms
- ATP for simple FOL theorems < 5s
- Congruence closure for 100 terms < 200ms

---

### Phase 5: Higher-Order & Polish (Week 9-10)
**Specialists:** Higher-Order Logic

**Deliverables:**
1. HigherOrderLogicSpecialist with lambda calculus + type inference
2. 40 unit tests
3. 50 integration tests (all specialists)
4. Performance optimization across all specialists
5. Documentation and examples

**Acceptance Criteria:**
- All 507 tests passing
- Integration test coverage > 90%
- Performance benchmarks met

---

## Performance Targets

| Specialist | Small Problem | Medium Problem | Large Problem |
|------------|---------------|----------------|---------------|
| Modal | < 50ms (5 worlds) | < 200ms (20 worlds) | < 2s (100 worlds) |
| Temporal | < 100ms (10 states) | < 500ms (50 states) | < 5s (500 states) |
| Fuzzy | < 10ms (5 rules) | < 50ms (20 rules) | < 200ms (100 rules) |
| Description | < 50ms (depth 2) | < 500ms (depth 5) | < 5s (depth 10) |
| CSP | < 50ms (10 vars) | < 500ms (50 vars) | < 10s (200 vars) |
| SAT | < 50ms (50 clauses) | < 1s (500 clauses) | < 30s (5000 clauses) |
| SMT | < 100ms (10 constr) | < 1s (50 constr) | < 10s (200 constr) |
| ATP | < 500ms (simple) | < 5s (medium) | < 30s (complex) |
| Prolog | < 50ms (depth 5) | < 500ms (depth 20) | < 5s (depth 50) |
| Equational | < 20ms (5 rules) | < 200ms (20 rules) | < 2s (100 rules) |
| HOL | < 50ms (size 20) | < 200ms (size 100) | < 2s (size 500) |

---

## Success Metrics

### Capability Score Projection

**Current State:**
- 3 specialists
- Basic algorithms only
- Score: 60/100

**After Phase 1 (Foundation):**
- 6 specialists
- Foundational algorithms (SAT, CSP, Prolog)
- Score: **72/100** (+12 points)

**After Phase 2 (Modal/Temporal):**
- 8 specialists
- Modal and temporal reasoning
- Score: **78/100** (+6 points)

**After Phase 3 (Knowledge Rep):**
- 10 specialists
- Knowledge representation systems
- Score: **84/100** (+6 points)

**After Phase 4 (Advanced Reasoning):**
- 13 specialists
- Automated reasoning (SMT, ATP, equality)
- Score: **90/100** (+6 points)

**After Phase 5 (Higher-Order):**
- 14 specialists
- Higher-order logic
- Score: **92/100** (+2 points)

**Final Capability Breakdown:**

| Subsystem | Weight | Before | After | Contribution |
|-----------|--------|--------|-------|--------------|
| Propositional Logic | 15% | 50% | 95% | +6.75 |
| Predicate Logic | 15% | 40% | 90% | +7.50 |
| Proof Theory | 10% | 35% | 85% | +5.00 |
| Modal Logic | 10% | 0% | 85% | +8.50 |
| Temporal Logic | 8% | 0% | 80% | +6.40 |
| SAT/SMT | 12% | 5% | 90% | +10.20 |
| ATP | 10% | 15% | 85% | +7.00 |
| CSP | 8% | 0% | 90% | +7.20 |
| Knowledge Rep | 7% | 0% | 75% | +5.25 |
| Other (Fuzzy, HOL, etc.) | 5% | 0% | 70% | +3.50 |
| **TOTAL** | **100%** | **60%** | **92.3%** | **+32.3** |

---

## Algorithm Reference Library

### Pure Python Implementation Notes

All algorithms must be implemented without SymPy or external CAS libraries. Here are key data structures and patterns:

#### **Graph Representation** (for accessibility relations, Kripke models, transition systems)

```python
# Adjacency list representation
graph = {
    'node1': {'node2', 'node3'},  # set of successors
    'node2': {'node3'},
    'node3': set()
}

# For labeled edges (e.g., transitions with actions)
graph = {
    'state1': [('action_a', 'state2'), ('action_b', 'state3')],
    'state2': [('action_c', 'state1')],
}
```

#### **Term Representation** (for FOL, HOL)

```python
from dataclasses import dataclass
from typing import Union, List

@dataclass
class Var:
    name: str

@dataclass
class Const:
    name: str

@dataclass
class Func:
    name: str
    args: List['Term']

Term = Union[Var, Const, Func]
```

#### **Unification Algorithm** (core for FOL, Prolog, ATP)

```python
def unify(term1: Term, term2: Term, subst: Dict[str, Term] = None) -> Optional[Dict[str, Term]]:
    """
    Robinson's unification algorithm with occurs check.
    Returns MGU (most general unifier) or None if unification fails.
    """
    if subst is None:
        subst = {}

    # Dereference
    if isinstance(term1, Var) and term1.name in subst:
        return unify(subst[term1.name], term2, subst)
    if isinstance(term2, Var) and term2.name in subst:
        return unify(term1, subst[term2.name], subst)

    # Same variable
    if isinstance(term1, Var) and isinstance(term2, Var) and term1.name == term2.name:
        return subst

    # Variable binding
    if isinstance(term1, Var):
        if occurs_check(term1.name, term2, subst):
            return None  # Occurs check failed
        subst[term1.name] = term2
        return subst
    if isinstance(term2, Var):
        if occurs_check(term2.name, term1, subst):
            return None
        subst[term2.name] = term1
        return subst

    # Constants
    if isinstance(term1, Const) and isinstance(term2, Const):
        return subst if term1.name == term2.name else None

    # Functions
    if isinstance(term1, Func) and isinstance(term2, Func):
        if term1.name != term2.name or len(term1.args) != len(term2.args):
            return None
        for arg1, arg2 in zip(term1.args, term2.args):
            subst = unify(arg1, arg2, subst)
            if subst is None:
                return None
        return subst

    return None  # Type mismatch
```

#### **Clause Representation** (for resolution, SAT)

```python
# Clause as set of literals (strings with optional '¬' prefix)
Clause = Set[str]

# Example: {¬P, Q, ¬R} represents ¬P ∨ Q ∨ ¬R
clause1 = {'¬P', 'Q'}
clause2 = {'P', 'R'}

def resolve(c1: Clause, c2: Clause) -> Optional[Clause]:
    """Binary resolution"""
    for lit in c1:
        neg_lit = negate_literal(lit)
        if neg_lit in c2:
            # Found complementary literals
            resolvent = (c1 - {lit}) | (c2 - {neg_lit})
            return resolvent
    return None

def negate_literal(lit: str) -> str:
    return lit[1:] if lit.startswith('¬') else f'¬{lit}'
```

---

## Documentation Requirements

Each new specialist must include:

1. **Module docstring** with:
   - Specialist purpose
   - Capabilities list
   - Algorithm references
   - Performance characteristics

2. **Class docstring** with:
   - BDI implementation notes
   - Service registration details
   - Operation types supported
   - Example usage

3. **Method docstrings** with:
   - Parameter descriptions
   - Return value specification
   - Time complexity (Big-O)
   - Example calls

4. **Inline comments** for:
   - Complex algorithm steps
   - Edge case handling
   - Performance optimizations

5. **Example file** in `docs/examples/logic/`:
   - Demonstrates all operations
   - Includes expected outputs
   - Performance benchmarks

---

## Integration with Existing System

### Blackboard Entries

**Task Entry Metadata:**
```python
{
    'operation': 'sat_solve',  # or 'modal_check', 'ltl_verify', etc.
    'domain': 'logic',
    'subdomain': 'sat',  # or 'modal', 'temporal', etc.
    'problem_data': {
        # Specialist-specific problem encoding
    },
    'timeout_ms': 5000,
    'priority': 1.0
}
```

**Result Entry Metadata:**
```python
{
    'result_type': 'satisfiable',  # or 'proved', 'refuted', 'unknown', etc.
    'solution': {...},  # Specialist-specific solution data
    'time_ms': 125,
    'algorithm_used': 'dpll_cdcl',
    'statistics': {...}
}
```

### Directory Facilitator Registration

All specialists register with hierarchical service types:

```
math.logic.propositional
math.logic.predicate
math.logic.proof
math.logic.modal        (NEW)
math.logic.temporal     (NEW)
math.logic.fuzzy        (NEW)
math.logic.description  (NEW)
math.logic.csp          (NEW)
math.logic.sat          (NEW)
math.logic.smt          (NEW)
math.logic.atp          (NEW)
math.logic.prolog       (NEW)
math.logic.equality     (NEW)
math.logic.hol          (NEW)
```

---

## Risk Mitigation

### Risk 1: Algorithm Complexity Without Libraries

**Mitigation:**
- Start with simplified versions (e.g., basic DPLL before CDCL)
- Implement optimizations incrementally
- Use well-documented pseudocode from textbooks
- Extensive unit testing for correctness

### Risk 2: Performance Without Optimized Libraries

**Mitigation:**
- Set realistic timeout limits
- Implement heuristics (e.g., VSIDS for SAT)
- Use efficient data structures (sets, dicts for O(1) lookup)
- Profile and optimize hot paths
- Consider Numba JIT for critical loops (still pure Python)

### Risk 3: Implementation Time

**Mitigation:**
- Phased rollout (Phases 1-5)
- Prioritize high-impact specialists (SAT, Modal, Temporal)
- Reuse common components (unification, term structures)
- Test-driven development (write tests first)

### Risk 4: Integration Bugs

**Mitigation:**
- Comprehensive integration test suite
- Blackboard monitoring and logging
- Graceful degradation (specialists return 'unknown' on timeout)
- Supervisor fallback routing

---

## Resource Requirements

### Development Time

- **Phase 1 (Foundation):** 80 hours
- **Phase 2 (Modal/Temporal):** 60 hours
- **Phase 3 (Knowledge Rep):** 60 hours
- **Phase 4 (Advanced):** 80 hours
- **Phase 5 (HOL + Polish):** 60 hours
- **Total:** 340 hours (~8.5 weeks at 40 hrs/week)

### Testing Time

- **Unit tests:** 11 specialists × 10 hours = 110 hours
- **Integration tests:** 30 hours
- **Performance tuning:** 40 hours
- **Total:** 180 hours (~4.5 weeks)

### Documentation Time

- **Specialist docs:** 11 × 4 hours = 44 hours
- **Examples:** 11 × 2 hours = 22 hours
- **Integration guide:** 10 hours
- **Total:** 76 hours (~2 weeks)

**Grand Total:** 596 hours (~15 weeks of full-time development)

---

## Conclusion

This improvement plan will elevate the Logic domain from 60% to 92%+ capability by adding **11 new specialists** implementing **8 critical logic subsystems**. The phased approach ensures steady progress with measurable milestones, while the pure Python implementation requirement maintains architectural consistency.

**Key Success Factors:**
1. **Comprehensive Coverage:** Modal, temporal, fuzzy, description, CSP, SAT/SMT, ATP, Prolog, equality, HOL
2. **Pure Python:** All implementations use native Python (NO SYMPY)
3. **BDI Architecture:** Every specialist follows the BDI pattern
4. **Robust Testing:** 507 total tests ensure correctness
5. **Performance:** Realistic benchmarks with timeout protection
6. **Incremental Delivery:** 5 phases with clear acceptance criteria

**Expected Outcome:**
- Logic domain score: **92/100** (from 60/100)
- Total specialists: **14** (from 3)
- Test coverage: **507 tests** (from 17)
- Capability ranking: **Top 3 domains** (currently 7th of 9)

---

## Appendix: Algorithm Complexity Reference

| Algorithm | Time Complexity | Space Complexity | Decidability |
|-----------|----------------|------------------|--------------|
| **Propositional SAT (DPLL)** | O(2^n) worst | O(n) | Decidable (NP-complete) |
| **CDCL SAT** | O(2^n) worst, much better average | O(n + m) | Decidable (NP-complete) |
| **Modal K Tableau** | O(2^(n × w)) | O(n × w) | Decidable |
| **Modal S4 Tableau** | O(2^(n × w^2)) | O(n × w^2) | Decidable |
| **LTL Model Checking** | O(\|M\| × 2^{\|φ\|}) | O(\|M\| × 2^{\|φ\|}) | Decidable (PSPACE) |
| **CTL Model Checking** | O(\|M\| × \|φ\|) | O(\|M\|) | Decidable (P) |
| **ALC Tableau** | ExpTime | ExpTime | Decidable (ExpTime-complete) |
| **FOL Resolution** | Undecidable (semi-decidable) | Unbounded | Semi-decidable |
| **Unification** | O(n) (near-linear) | O(n) | Decidable (linear) |
| **AC-3 (CSP)** | O(ed^3) | O(e) | Decidable (NP-complete) |
| **Congruence Closure** | O(n log n) | O(n) | Decidable |
| **Knuth-Bendix** | Undecidable | Unbounded | May not terminate |
| **Type Inference (HM)** | O(n) (near-linear) | O(n) | Decidable (DEXPTIME) |

Legend:
- n = number of variables/propositions
- w = number of worlds (Kripke)
- |M| = state space size
- |φ| = formula size
- e = number of constraints/edges
- d = domain size
- m = number of clauses

---

**END OF IMPROVEMENT PLAN**
