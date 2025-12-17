<!-- Converted from: Phase_3_Build_Order_Breakdown.docx -->

# Phase 3 Build Order Breakdown
*Meta-Cognitive Middleware Implementation*
Autonomous Mathematical Discovery Engine
───────────────────────────────────────────────────────────────────
# 1. Executive Overview
Phase 3 is designated as the Meta-Cognitive Middleware implementation. While Phase 2 populated the system with "Muscle" (mathematical solvers), Phase 3 installs the "Conscience" and "Memory." Without these agents, the Phase 2 workforce is brittle: it will confidently compute results for impossible problems (hallucination) and waste resources re-solving known lemmas (amnesia). Phase 3 introduces three critical cross-cutting teams to address the Assumption Gap (Gap 3), the Memory Gap (Gap 2), and the Search Gap (Gap 1).
## 1.1 Strategic Context
Following the completion of Phase 0 (infrastructural bedrock), Phase 1 (cognitive chassis), and Phase 2 (vertical domain expansion), the system possesses a functional "Central Nervous System" (Orchestrator) and a powerful workforce of 18 mathematical specialists. However, this workforce currently operates as a "Fragile Genius"—mathematically powerful but brittle. Phase 3 transforms this into a "Resilient Professional" by installing the cognitive immune system that creates resilience, context, and foresight.
## 1.2 Phase 3 Agent Count
Phase 3 deploys 10 agents organized into 3 specialized teams, plus critical updates to the existing Tier 1 Orchestrator:

| Team | Agent Count | Gap Addressed |
| --- | --- | --- |
| Precondition Validation Team | 4 | Assumption Gap (Gap 3) |
| Knowledge Management Team | 3 | Memory Gap (Gap 2) |
| Hypothesis Generation Team | 3 | Search Gap (Gap 1) |
| TOTAL | 10 | All Three Gaps |


## 1.3 Source Documentation Reference
This build order synthesizes specifications from the following authoritative project documentation:

| Document | Content Scope |
| --- | --- |
| Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx | Detailed agent team specifications with directives and mechanisms |
| Phase_3_installs_the_cognitive_immune_system.docx | Step-by-step technical specification with action items |
| phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx | Overall roadmap and phase integration context |
| architectural_roadmap.docx | 65-agent system architecture overview and agent count specifications |
| phase_3_Building_The_Resilient_AI_Brain.pdf | Visual blueprint and architectural diagrams |
| phase_3_Genius_to_Stability.pdf | Transition documentation from Fragile Genius to Resilient Professional |
| phase_3_mindmap.png | Visual mind map of Phase 3 components |


───────────────────────────────────────────────────────────────────
# 2. Core Architectural Principles
The successful deployment of the Meta-Cognitive Middleware hinges upon strict adherence to a set of core architectural principles. These principles ensure that the new layer of agents integrates seamlessly with the existing Phase 0-2 infrastructure while addressing the three critical gaps in the system's cognitive architecture.
## 2.1 The "Never Trust, Always Verify" Mandate
The Precondition Validation Team embodies the core reliability principle: no solver may execute until mathematical validity is certified. This prevents the system from producing "correct calculations based on impossible premises."
## 2.2 The "Shared Memory" Mandate
The Knowledge Management Team transforms the system from stateless isolation to collective consciousness. Insights discovered by one agent become instantly available to all others, preventing the "Tower of Babel" where Agent A solves a lemma that Agent B needs but cannot see.
## 2.3 The "Explore Before Commit" Mandate
The Hypothesis Generation Team implements Tree-of-Thoughts (ToT) reasoning, exploring the solution space before committing computational resources. Standard agents blindly execute the first valid move they see; this team ensures strategic path selection.
## 2.4 Control Loop Evolution
The Orchestrator's control loop must evolve from the Phase 1 pattern:
   Phase 1-2: Plan → Solve
   Phase 3:   Analyze → Hypothesize → Validate → Solve
───────────────────────────────────────────────────────────────────
# 3. Build Order: Step-by-Step Implementation
## STEP 1: The Precondition Validation Team (The "Anesthesiologist")
### WHAT: Pre-Flight Checklist for Mathematical Validity
Construct the mandatory validation layer that certifies every problem is mathematically sound and well-defined before any solver touches it. This team acts as the system's "immune system" against hallucination by preventing computations on impossible premises.
### WHY: Addressing the Assumption Gap (Gap 3)
The Phase 2 workforce is powerful but brittle. If a supervisor routes a negative number to a Logarithm Specialist, the system will crash. If asked to find the real square root of -4, the system will hallucinate. The Precondition Validation Team intercepts these invalid inputs BEFORE they reach the solvers, saving compute resources and preventing mathematically invalid outputs.
📚 Reference: Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx, Section 1
### HOW: Four-Agent Implementation
Agent 1.1: The Domain Checker
Directive: Implement an agent that audits the problem against the capabilities of the available solvers. It functions as a solvability gatekeeper.
Logic: Verifies if the problem falls within a decidable fragment of mathematics. If the input requires solving a Diophantine equation (undecidable in general) and the system only possesses Real arithmetic solvers, this agent halts execution immediately with a DOMAIN_MISMATCH error, preventing infinite loops or wasted compute.
Agent 1.2: The Assumption Validator
Directive: Build an agent strictly for checking variable definitions and constraints. A rigorous compliance agent that scans the OMDoc/OpenMath structure.
Mechanism: Enforces mathematical legality. For example, if the problem contains ln(x), this agent asserts the constraint x > 0. If a prior step or user input defined x = -5, the Validator triggers a CONSTRAINT_VIOLATION error before the Logarithm Specialist is ever invoked.
Agent 1.3: The Edge Case Detector (Red Team)
Directive: Implement a "Red Team" agent that proactively hunts for singularities and boundary failures. A proactive "saboteur" agent.
Task: Interrogates the problem state with "What if?" scenarios. "What breaks if the denominator is zero?" or "Is this matrix singular?" If the Linear Algebra Supervisor attempts to invert a matrix, this agent first calculates the determinant. If det(A) = 0, it blocks the operation, saving the system from a computational crash.
Agent 1.4: The Constraint Propagator
Directive: Establish a mechanism to pass validated constraints down the hierarchy. Ensures that the "laws of physics" established for the problem are respected by all downstream agents.
Function: If the Orchestrator determines n must be an integer, the Propagator injects this constraint into the context of every sub-task. This ensures the Integration Expert does not attempt algorithms valid only for continuous real variables on a discrete variable.
### CODE: Precondition Validation Team Implementation
# precondition_validation.py - The "Anesthesiologist" Team
# Phase 3: Meta-Cognitive Middleware - Assumption Gap Resolution

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple
from abc import ABC, abstractmethod
import sympy as sp
from sympy import Symbol, sympify, oo, zoo, nan
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION STATUS AND ERROR TYPES
# ═══════════════════════════════════════════════════════════════════════════

class ValidationStatus(Enum):
    """Status codes for precondition validation results"""
    VALID = auto()
    DOMAIN_MISMATCH = auto()
    CONSTRAINT_VIOLATION = auto()
    SINGULARITY_DETECTED = auto()
    UNDECIDABLE_FRAGMENT = auto()
    EDGE_CASE_FAILURE = auto()

class MathematicalDomain(Enum):
    """Mathematical domains for solvability checking"""
    REAL_ARITHMETIC = "real_arithmetic"
    COMPLEX_ARITHMETIC = "complex_arithmetic"
    INTEGER_ARITHMETIC = "integer_arithmetic"
    RATIONAL_ARITHMETIC = "rational_arithmetic"
    REAL_CLOSED_FIELDS = "real_closed_fields"
    PRESBURGER_ARITHMETIC = "presburger_arithmetic"
    DIOPHANTINE = "diophantine"  # Generally undecidable
    PEANO_ARITHMETIC = "peano_arithmetic"  # Undecidable

@dataclass
class ValidationResult:
    """Result of precondition validation"""
    status: ValidationStatus
    is_valid: bool
    error_message: Optional[str] = None
    constraint_violations: List[str] = field(default_factory=list)
    edge_cases_detected: List[str] = field(default_factory=list)
    propagated_constraints: Dict[str, Any] = field(default_factory=dict)
    domain_classification: Optional[MathematicalDomain] = None
    
    def to_fipa_token(self) -> str:
        """Generate FIPA-ACL compatible status token"""
        return f"STATUS: {self.status.name}"

@dataclass
class MathematicalConstraint:
    """Represents a mathematical constraint on a variable"""
    variable: str
    constraint_type: str  # 'positive', 'negative', 'nonzero', 'integer', 'real', etc.
    expression: Optional[Any] = None
    source: str = "inferred"  # 'user_defined', 'inferred', 'propagated'
    
    def to_sympy_assumption(self) -> Dict[str, bool]:
        """Convert to SymPy assumption dictionary"""
        mapping = {
            'positive': {'positive': True, 'real': True},
            'negative': {'negative': True, 'real': True},
            'nonzero': {'zero': False},
            'integer': {'integer': True},
            'real': {'real': True},
            'complex': {'complex': True},
            'nonnegative': {'nonnegative': True, 'real': True},
        }
        return mapping.get(self.constraint_type, {})

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 1.1: THE DOMAIN CHECKER
# ═══════════════════════════════════════════════════════════════════════════

class DomainCheckerAgent:
    """
    Agent 1.1: The Domain Checker - Solvability Gatekeeper
    
    Audits problems against the capabilities of available solvers.
    Prevents wasted compute on undecidable or unsupported problem classes.
    
    📚 Reference: Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx
    """
    
    # Decidable fragments that the system can handle
    DECIDABLE_DOMAINS = {
        MathematicalDomain.REAL_ARITHMETIC,
        MathematicalDomain.COMPLEX_ARITHMETIC,
        MathematicalDomain.RATIONAL_ARITHMETIC,
        MathematicalDomain.REAL_CLOSED_FIELDS,
        MathematicalDomain.PRESBURGER_ARITHMETIC,
    }
    
    # Undecidable domains requiring special handling
    UNDECIDABLE_DOMAINS = {
        MathematicalDomain.DIOPHANTINE,
        MathematicalDomain.PEANO_ARITHMETIC,
    }
    
    def __init__(self, available_solvers: Dict[str, Set[MathematicalDomain]]):
        """
        Initialize with registry of available solvers and their capabilities.
        
        Args:
            available_solvers: Maps solver_id to set of supported domains
        """
        self.available_solvers = available_solvers
        self.solver_capabilities = self._compute_aggregate_capabilities()
        
    def _compute_aggregate_capabilities(self) -> Set[MathematicalDomain]:
        """Compute union of all solver capabilities"""
        capabilities = set()
        for domains in self.available_solvers.values():
            capabilities.update(domains)
        return capabilities
    
    def classify_domain(self, omdoc_object) -> MathematicalDomain:
        """
        Classify the mathematical domain of a problem.
        
        Inspects the OMDoc structure to determine which mathematical
        fragment the problem belongs to.
        """
        # Extract expression from OMDoc
        expr = omdoc_object.expression_tree
        
        # Check for Diophantine markers (integer-only solutions required)
        if self._is_diophantine(expr, omdoc_object):
            return MathematicalDomain.DIOPHANTINE
            
        # Check variable domains from constraints
        if self._requires_integer_domain(omdoc_object):
            return MathematicalDomain.INTEGER_ARITHMETIC
            
        # Check for complex domain requirements
        if self._requires_complex_domain(expr):
            return MathematicalDomain.COMPLEX_ARITHMETIC
            
        # Default to real arithmetic for most problems
        return MathematicalDomain.REAL_ARITHMETIC
    
    def _is_diophantine(self, expr, omdoc_object) -> bool:
        """Detect Diophantine equation patterns"""
        # Check if problem explicitly requires integer solutions
        metadata = omdoc_object.metadata
        if metadata.get('solution_domain') == 'integers':
            return True
        # Check for polynomial equations with integer coefficient constraints
        return False
    
    def _requires_integer_domain(self, omdoc_object) -> bool:
        """Check if problem requires integer arithmetic"""
        constraints = omdoc_object.metadata.get('constraints', [])
        for c in constraints:
            if isinstance(c, MathematicalConstraint) and c.constraint_type == 'integer':
                return True
        return False
    
    def _requires_complex_domain(self, expr) -> bool:
        """Check if expression requires complex numbers"""
        try:
            sympy_expr = sympify(expr) if isinstance(expr, str) else expr
            return sympy_expr.has(sp.I) or sympy_expr.has(sp.exp)
        except:
            return False
    
    def check_solvability(self, omdoc_object) -> ValidationResult:
        """
        Main validation method: Check if problem is solvable by available solvers.
        
        Returns:
            ValidationResult with VALID or DOMAIN_MISMATCH status
        """
        domain = self.classify_domain(omdoc_object)
        
        # Check for undecidable domains
        if domain in self.UNDECIDABLE_DOMAINS:
            return ValidationResult(
                status=ValidationStatus.UNDECIDABLE_FRAGMENT,
                is_valid=False,
                error_message=f"Problem falls in undecidable fragment: {domain.value}. "
                              f"System cannot guarantee termination.",
                domain_classification=domain
            )
        
        # Check if any solver supports this domain
        if domain not in self.solver_capabilities:
            return ValidationResult(
                status=ValidationStatus.DOMAIN_MISMATCH,
                is_valid=False,
                error_message=f"No solver available for domain: {domain.value}. "
                              f"Available domains: {[d.value for d in self.solver_capabilities]}",
                domain_classification=domain
            )
        
        return ValidationResult(
            status=ValidationStatus.VALID,
            is_valid=True,
            domain_classification=domain
        )

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 1.2: THE ASSUMPTION VALIDATOR
# ═══════════════════════════════════════════════════════════════════════════

class AssumptionValidatorAgent:
    """
    Agent 1.2: The Assumption Validator - Constraint Compliance Checker
    
    Scans OMDoc structure for variable definitions and constraints.
    Enforces mathematical legality before solvers engage.
    
    📚 Reference: Phase_3_installs_the_cognitive_immune_system.docx, Action 1.2
    """
    
    # Implicit constraints for common functions
    FUNCTION_CONSTRAINTS = {
        'ln': {'arg': 'positive'},
        'log': {'arg': 'positive'},
        'sqrt': {'arg': 'nonnegative'},
        'asin': {'arg': ('bounded', -1, 1)},
        'acos': {'arg': ('bounded', -1, 1)},
        'tan': {'arg': 'not_odd_multiple_pi_half'},
        'cot': {'arg': 'not_multiple_pi'},
        'csc': {'arg': 'not_multiple_pi'},
        'sec': {'arg': 'not_odd_multiple_pi_half'},
    }
    
    def __init__(self):
        self.known_constraints: Dict[str, List[MathematicalConstraint]] = {}
        
    def extract_implicit_constraints(self, expr) -> List[MathematicalConstraint]:
        """
        Extract constraints implied by functions in the expression.
        
        For example, ln(x) implies x > 0.
        """
        constraints = []
        
        try:
            sympy_expr = sympify(expr) if isinstance(expr, str) else expr
        except:
            return constraints
            
        # Check for logarithmic functions
        if sympy_expr.has(sp.log) or sympy_expr.has(sp.ln):
            for arg in sympy_expr.atoms(sp.log):
                var = self._extract_primary_variable(arg.args[0])
                if var:
                    constraints.append(MathematicalConstraint(
                        variable=str(var),
                        constraint_type='positive',
                        expression=arg.args[0] > 0,
                        source='inferred'
                    ))
        
        # Check for square roots
        if sympy_expr.has(sp.sqrt):
            for arg in sympy_expr.atoms(sp.Pow):
                if arg.exp == sp.Rational(1, 2):
                    var = self._extract_primary_variable(arg.base)
                    if var:
                        constraints.append(MathematicalConstraint(
                            variable=str(var),
                            constraint_type='nonnegative',
                            expression=arg.base >= 0,
                            source='inferred'
                        ))
        
        # Check for division (nonzero denominators)
        for atom in sympy_expr.atoms(sp.Pow):
            if atom.exp.is_negative:
                var = self._extract_primary_variable(atom.base)
                if var:
                    constraints.append(MathematicalConstraint(
                        variable=str(var),
                        constraint_type='nonzero',
                        expression=atom.base != 0,
                        source='inferred'
                    ))
        
        return constraints
    
    def _extract_primary_variable(self, expr) -> Optional[Symbol]:
        """Extract the primary variable from an expression"""
        symbols = expr.free_symbols if hasattr(expr, 'free_symbols') else set()
        return next(iter(symbols)) if symbols else None
    
    def validate_constraints(self, omdoc_object, 
                           user_defined_constraints: List[MathematicalConstraint] = None
                           ) -> ValidationResult:
        """
        Validate that all constraints are satisfied.
        
        Checks for conflicts between:
        - User-defined constraints
        - Implicit function constraints
        - Prior step results
        """
        violations = []
        expr = omdoc_object.expression_tree
        
        # Extract implicit constraints
        implicit = self.extract_implicit_constraints(expr)
        
        # Combine with user-defined
        all_constraints = implicit + (user_defined_constraints or [])
        
        # Get variable values from metadata/prior steps
        known_values = omdoc_object.metadata.get('variable_values', {})
        
        # Check each constraint against known values
        for constraint in all_constraints:
            var_name = constraint.variable
            if var_name in known_values:
                value = known_values[var_name]
                if not self._check_constraint_satisfied(constraint, value):
                    violations.append(
                        f"Variable {var_name}={value} violates constraint "
                        f"'{constraint.constraint_type}' (required for {constraint.source})"
                    )
        
        if violations:
            return ValidationResult(
                status=ValidationStatus.CONSTRAINT_VIOLATION,
                is_valid=False,
                error_message="Mathematical constraints violated",
                constraint_violations=violations
            )
        
        return ValidationResult(
            status=ValidationStatus.VALID,
            is_valid=True,
            propagated_constraints={c.variable: c for c in all_constraints}
        )
    
    def _check_constraint_satisfied(self, constraint: MathematicalConstraint, 
                                   value: Any) -> bool:
        """Check if a value satisfies a constraint"""
        try:
            if constraint.constraint_type == 'positive':
                return float(value) > 0
            elif constraint.constraint_type == 'negative':
                return float(value) < 0
            elif constraint.constraint_type == 'nonzero':
                return float(value) != 0
            elif constraint.constraint_type == 'nonnegative':
                return float(value) >= 0
            elif constraint.constraint_type == 'integer':
                return float(value) == int(value)
            elif constraint.constraint_type == 'real':
                return not isinstance(value, complex)
        except (ValueError, TypeError):
            return True  # Can't evaluate, assume valid
        return True

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 1.3: THE EDGE CASE DETECTOR (RED TEAM)
# ═══════════════════════════════════════════════════════════════════════════

class EdgeCaseDetectorAgent:
    """
    Agent 1.3: The Edge Case Detector - Red Team Saboteur
    
    Proactively hunts for singularities and boundary failures.
    Asks "What if?" to catch problems before they cause crashes.
    
    📚 Reference: Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx
    """
    
    def __init__(self):
        self.critical_values = [0, 1, -1, float('inf'), float('-inf')]
        
    def detect_singularities(self, expr) -> List[str]:
        """
        Hunt for singularities in the expression.
        
        Identifies points where the expression becomes undefined,
        infinite, or otherwise problematic.
        """
        edge_cases = []
        
        try:
            sympy_expr = sympify(expr) if isinstance(expr, str) else expr
            variables = list(sympy_expr.free_symbols)
        except:
            return edge_cases
        
        for var in variables:
            # Check for division by zero
            zeros = self._find_zeros_in_denominator(sympy_expr, var)
            for zero_point in zeros:
                edge_cases.append(
                    f"SINGULARITY: Division by zero when {var}={zero_point}"
                )
            
            # Check behavior at critical points
            for critical in [0, 1, -1]:
                try:
                    result = sympy_expr.subs(var, critical)
                    if result in [oo, -oo, zoo, nan]:
                        edge_cases.append(
                            f"BOUNDARY_FAILURE: Expression undefined at {var}={critical}"
                        )
                except:
                    pass
        
        return edge_cases
    
    def _find_zeros_in_denominator(self, expr, var) -> List[Any]:
        """Find values that make denominators zero"""
        zeros = []
        
        # Get the denominator
        numer, denom = expr.as_numer_denom()
        if denom != 1:
            solutions = sp.solve(denom, var)
            zeros.extend(solutions)
        
        return zeros
    
    def check_matrix_singularity(self, matrix_data) -> Tuple[bool, Optional[str]]:
        """
        Check if a matrix is singular before inversion attempts.
        
        Called before Linear Algebra Supervisor operations.
        """
        try:
            if isinstance(matrix_data, np.ndarray):
                det = np.linalg.det(matrix_data)
            else:
                matrix = sp.Matrix(matrix_data)
                det = matrix.det()
            
            if abs(float(det)) < 1e-10:
                return True, f"Matrix is singular (det={det}). Inversion blocked."
            return False, None
        except Exception as e:
            return True, f"Matrix singularity check failed: {str(e)}"
    
    def validate(self, omdoc_object, operation_type: str = None) -> ValidationResult:
        """
        Main validation method for edge case detection.
        """
        edge_cases = []
        
        expr = omdoc_object.expression_tree
        edge_cases.extend(self.detect_singularities(expr))
        
        # Check for matrix operations
        if operation_type == 'matrix_inversion':
            matrix_data = omdoc_object.metadata.get('matrix')
            if matrix_data is not None:
                is_singular, msg = self.check_matrix_singularity(matrix_data)
                if is_singular:
                    edge_cases.append(f"MATRIX_SINGULARITY: {msg}")
        
        if edge_cases:
            return ValidationResult(
                status=ValidationStatus.EDGE_CASE_FAILURE,
                is_valid=False,
                error_message="Edge cases detected that could cause computational failure",
                edge_cases_detected=edge_cases
            )
        
        return ValidationResult(
            status=ValidationStatus.VALID,
            is_valid=True
        )

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 1.4: THE CONSTRAINT PROPAGATOR
# ═══════════════════════════════════════════════════════════════════════════

class ConstraintPropagatorAgent:
    """
    Agent 1.4: The Constraint Propagator - Hierarchical Constraint Injection
    
    Ensures that validated constraints are passed down to all downstream agents.
    Maintains the "laws of physics" across the entire agent hierarchy.
    
    📚 Reference: Phase_3_installs_the_cognitive_immune_system.docx, Action 1.4
    """
    
    def __init__(self, blackboard):
        """
        Initialize with reference to the shared Blackboard.
        
        Args:
            blackboard: The Phase 0 Blackboard for constraint broadcasting
        """
        self.blackboard = blackboard
        self.active_constraints: Dict[str, Dict[str, MathematicalConstraint]] = {}
        
    def register_constraint(self, conversation_id: str, 
                          constraint: MathematicalConstraint) -> None:
        """
        Register a validated constraint for a problem-solving session.
        """
        if conversation_id not in self.active_constraints:
            self.active_constraints[conversation_id] = {}
        
        self.active_constraints[conversation_id][constraint.variable] = constraint
        
        # Post to Blackboard for subscriber notification
        self.blackboard.post({
            'entry_type': 'constraint_propagation',
            'conversation_id': conversation_id,
            'constraint': constraint,
            'tags': ['constraint_update', constraint.variable]
        })
    
    def get_constraints_for_subtask(self, conversation_id: str,
                                   relevant_variables: Set[str]
                                   ) -> Dict[str, MathematicalConstraint]:
        """
        Retrieve constraints relevant to a specific sub-task.
        
        Filters the active constraints to return only those
        affecting the variables used in the sub-task.
        """
        session_constraints = self.active_constraints.get(conversation_id, {})
        return {
            var: constraint 
            for var, constraint in session_constraints.items()
            if var in relevant_variables
        }
    
    def inject_constraints_into_context(self, omdoc_object,
                                       conversation_id: str) -> Any:
        """
        Inject propagated constraints into an OMDoc object's context.
        
        Modifies the OMDoc metadata to include all relevant constraints,
        ensuring downstream agents respect the established rules.
        """
        variables = self._extract_variables(omdoc_object.expression_tree)
        relevant_constraints = self.get_constraints_for_subtask(
            conversation_id, variables
        )
        
        # Update OMDoc metadata
        if 'propagated_constraints' not in omdoc_object.metadata:
            omdoc_object.metadata['propagated_constraints'] = {}
        
        omdoc_object.metadata['propagated_constraints'].update(relevant_constraints)
        
        return omdoc_object
    
    def _extract_variables(self, expr) -> Set[str]:
        """Extract variable names from expression"""
        try:
            sympy_expr = sympify(expr) if isinstance(expr, str) else expr
            return {str(s) for s in sympy_expr.free_symbols}
        except:
            return set()
    
    def clear_session(self, conversation_id: str) -> None:
        """Clear constraints for a completed session"""
        if conversation_id in self.active_constraints:
            del self.active_constraints[conversation_id]

# ═══════════════════════════════════════════════════════════════════════════
# PRECONDITION VALIDATION TEAM COORDINATOR
# ═══════════════════════════════════════════════════════════════════════════

class PreconditionValidationTeam:
    """
    Coordinator for the Precondition Validation Team.
    
    Orchestrates the four agents in sequence to produce a comprehensive
    validation result before any solver engages.
    
    📚 Reference: Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx
    """
    
    def __init__(self, available_solvers: Dict[str, Set[MathematicalDomain]],
                 blackboard):
        self.domain_checker = DomainCheckerAgent(available_solvers)
        self.assumption_validator = AssumptionValidatorAgent()
        self.edge_case_detector = EdgeCaseDetectorAgent()
        self.constraint_propagator = ConstraintPropagatorAgent(blackboard)
        
    def validate(self, omdoc_object, conversation_id: str,
                operation_type: str = None,
                user_constraints: List[MathematicalConstraint] = None
                ) -> ValidationResult:
        """
        Execute the full validation pipeline.
        
        Returns STATUS: VALID only if ALL checks pass.
        """
        # Step 1: Domain Check
        domain_result = self.domain_checker.check_solvability(omdoc_object)
        if not domain_result.is_valid:
            return domain_result
        
        # Step 2: Assumption Validation
        assumption_result = self.assumption_validator.validate_constraints(
            omdoc_object, user_constraints
        )
        if not assumption_result.is_valid:
            return assumption_result
        
        # Step 3: Edge Case Detection
        edge_result = self.edge_case_detector.validate(omdoc_object, operation_type)
        if not edge_result.is_valid:
            return edge_result
        
        # Step 4: Propagate validated constraints
        for var, constraint in assumption_result.propagated_constraints.items():
            self.constraint_propagator.register_constraint(conversation_id, constraint)
        
        # Inject constraints into context
        self.constraint_propagator.inject_constraints_into_context(
            omdoc_object, conversation_id
        )
        
        # All checks passed
        return ValidationResult(
            status=ValidationStatus.VALID,
            is_valid=True,
            domain_classification=domain_result.domain_classification,
            propagated_constraints=assumption_result.propagated_constraints
        )

───────────────────────────────────────────────────────────────────
## STEP 2: The Knowledge Management Team (The "Librarians")
### WHAT: Shared Memory and RAG Integration
Construct the knowledge infrastructure that transforms the system from stateless isolation to collective consciousness. This team manages the flow of information between the active Blackboard (short-term memory) and the Vector Database (long-term memory), implementing Retrieval-Augmented Generation (RAG) to short-circuit solving when known theorems exist.
### WHY: Addressing the Memory Gap (Gap 2)
Without shared memory, the system suffers from the "Tower of Babel" problem: Agent A solves a lemma that Agent B needs but cannot see. The system wastes resources re-solving known theorems. Research indicates that RAG integration improves accuracy by ~15-20% while dramatically reducing computation time for problems with known solutions.
📚 Reference: Phase_3_installs_the_cognitive_immune_system.docx, Step 2
### HOW: Three-Agent Implementation
Agent 2.1: The Context Extractor
Directive: Implement an agent that sits between the User/Orchestrator and the Blackboard. An information filter that parses the full problem history.
Function: Filters signal from noise. Extracts only the variables, definitions, and constraints relevant to the current sub-task, ensuring solvers are not overwhelmed by irrelevant token context. Prevents "distraction" by irrelevant data.
Agent 2.2: The Memory Indexer
Directive: Build the archivist agent responsible for writing to the Vector Database (Long-Term Memory). Connects the Blackboard to persistent storage.
Mechanism: When a Supervisor confirms a result (e.g., "∫x²dx = x³/3"), the Memory Indexer embeds this result and stores it. This creates a persistent record that survives beyond the current execution cycle, allowing the system to recall this lemma in future problems.
Agent 2.3: The Retrieval Specialist (RAG Integration)
Directive: Implement an agent responsible for external lookups. An external liaison agent that queries vast mathematical repositories.
Capability: Connects to formal libraries like Mathlib, Loogle, or internal historical logs. Before a solver attempts a proof, this agent queries: "Do we already have a theorem for this?" If a match is found, it retrieves the theorem, effectively short-circuiting the solving process.
### CODE: Knowledge Management Team Implementation
# knowledge_management.py - The "Librarians" Team
# Phase 3: Meta-Cognitive Middleware - Memory Gap Resolution

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum, auto
import hashlib
import json
from datetime import datetime
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════
# RETRIEVAL RESULT TYPES
# ═══════════════════════════════════════════════════════════════════════════

class RetrievalConfidence(Enum):
    """Confidence levels for retrieved knowledge"""
    EXACT_MATCH = auto()      # Identical theorem found
    HIGH_SIMILARITY = auto()  # Very similar, likely applicable
    MODERATE = auto()         # Related, may be useful
    LOW = auto()              # Loosely related
    NO_MATCH = auto()         # Nothing relevant found

@dataclass
class RetrievalResult:
    """Result from knowledge retrieval"""
    confidence: RetrievalConfidence
    theorem_id: Optional[str] = None
    theorem_content: Optional[str] = None
    proof_sketch: Optional[str] = None
    source: str = "internal"  # 'internal', 'mathlib', 'loogle'
    similarity_score: float = 0.0
    
    def should_skip_solving(self) -> bool:
        """Determine if retrieval is good enough to skip solving"""
        return self.confidence in [
            RetrievalConfidence.EXACT_MATCH,
            RetrievalConfidence.HIGH_SIMILARITY
        ]

@dataclass
class ContextPacket:
    """Filtered context for a sub-task"""
    relevant_variables: Dict[str, Any]
    active_constraints: Dict[str, Any]
    prior_results: List[Dict[str, Any]]
    problem_summary: str
    token_count: int

@dataclass
class MemoryEntry:
    """Entry in the long-term memory (Vector Database)"""
    entry_id: str
    timestamp: datetime
    problem_signature: str
    result: Any
    proof_trace: Optional[str]
    embedding: Optional[np.ndarray]
    metadata: Dict[str, Any] = field(default_factory=dict)

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 2.1: THE CONTEXT EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════════

class ContextExtractorAgent:
    """
    Agent 2.1: The Context Extractor - Information Filter
    
    Sits between the User/Orchestrator and the Blackboard.
    Filters signal from noise to ensure solvers operate on clean,
    token-efficient context.
    
    📚 Reference: Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx
    """
    
    def __init__(self, blackboard, max_context_tokens: int = 2048):
        """
        Initialize with Blackboard reference and token budget.
        
        Args:
            blackboard: Phase 0 Blackboard instance
            max_context_tokens: Maximum tokens to include in context
        """
        self.blackboard = blackboard
        self.max_context_tokens = max_context_tokens
        
    def extract_context(self, conversation_id: str,
                       target_variables: set,
                       problem_type: str) -> ContextPacket:
        """
        Extract relevant context for a sub-task.
        
        Filters the full problem history to return only information
        that directly impacts the current sub-task.
        """
        # Retrieve all entries for this conversation
        all_entries = self.blackboard.get_entries(conversation_id)
        
        # Filter for relevance
        relevant_entries = self._filter_relevant(
            all_entries, target_variables, problem_type
        )
        
        # Extract structured information
        variables = self._extract_variable_values(relevant_entries)
        constraints = self._extract_constraints(relevant_entries)
        prior_results = self._extract_prior_results(relevant_entries)
        
        # Compute problem summary
        summary = self._generate_summary(relevant_entries)
        
        # Estimate token count
        token_count = self._estimate_tokens(variables, constraints, 
                                           prior_results, summary)
        
        # Truncate if exceeds budget
        if token_count > self.max_context_tokens:
            prior_results = self._truncate_to_budget(
                prior_results, 
                self.max_context_tokens - self._estimate_tokens(
                    variables, constraints, [], summary
                )
            )
        
        return ContextPacket(
            relevant_variables=variables,
            active_constraints=constraints,
            prior_results=prior_results,
            problem_summary=summary,
            token_count=token_count
        )
    
    def _filter_relevant(self, entries: List[Dict], 
                        target_variables: set,
                        problem_type: str) -> List[Dict]:
        """Filter entries for relevance to current sub-task"""
        relevant = []
        
        for entry in entries:
            # Check if entry mentions target variables
            entry_vars = set(entry.get('variables', []))
            if entry_vars.intersection(target_variables):
                relevant.append(entry)
                continue
            
            # Check if entry is a constraint
            if entry.get('entry_type') == 'constraint_propagation':
                relevant.append(entry)
                continue
            
            # Check if entry is a confirmed result
            if entry.get('status') == 'VERIFIED':
                relevant.append(entry)
        
        return relevant
    
    def _extract_variable_values(self, entries: List[Dict]) -> Dict[str, Any]:
        """Extract known variable values from entries"""
        values = {}
        for entry in entries:
            if 'variable_values' in entry:
                values.update(entry['variable_values'])
        return values
    
    def _extract_constraints(self, entries: List[Dict]) -> Dict[str, Any]:
        """Extract active constraints"""
        constraints = {}
        for entry in entries:
            if entry.get('entry_type') == 'constraint_propagation':
                constraint = entry.get('constraint')
                if constraint:
                    constraints[constraint.variable] = constraint
        return constraints
    
    def _extract_prior_results(self, entries: List[Dict]) -> List[Dict]:
        """Extract verified prior results"""
        results = []
        for entry in entries:
            if entry.get('status') == 'VERIFIED':
                results.append({
                    'expression': entry.get('content'),
                    'result': entry.get('result'),
                    'method': entry.get('method')
                })
        return results
    
    def _generate_summary(self, entries: List[Dict]) -> str:
        """Generate concise problem summary"""
        # Extract key problem information
        problem_types = set()
        operations = []
        
        for entry in entries:
            if 'problem_type' in entry:
                problem_types.add(entry['problem_type'])
            if 'operation' in entry:
                operations.append(entry['operation'])
        
        return f"Problem types: {problem_types}. Operations: {operations[:5]}"
    
    def _estimate_tokens(self, variables, constraints, 
                        results, summary) -> int:
        """Rough token count estimation"""
        # Simple estimation: ~4 chars per token
        total_chars = (
            len(json.dumps(variables)) +
            len(json.dumps({str(k): str(v) for k, v in constraints.items()})) +
            len(json.dumps(results)) +
            len(summary)
        )
        return total_chars // 4
    
    def _truncate_to_budget(self, results: List[Dict], 
                           budget: int) -> List[Dict]:
        """Truncate results to fit token budget"""
        # Keep most recent results that fit
        truncated = []
        current_tokens = 0
        
        for result in reversed(results):
            result_tokens = len(json.dumps(result)) // 4
            if current_tokens + result_tokens <= budget:
                truncated.insert(0, result)
                current_tokens += result_tokens
            else:
                break
        
        return truncated

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 2.2: THE MEMORY INDEXER
# ═══════════════════════════════════════════════════════════════════════════

class MemoryIndexerAgent:
    """
    Agent 2.2: The Memory Indexer - Vector Database Archivist
    
    Responsible for writing confirmed results to the Vector Database.
    Transforms the Blackboard from temporary scratchpad to persistent
    long-term memory.
    
    📚 Reference: Phase_3_installs_the_cognitive_immune_system.docx, Action 2.2
    """
    
    def __init__(self, vector_db, embedding_model):
        """
        Initialize with Vector Database and embedding model.
        
        Args:
            vector_db: Phase 0 Vector Database instance (e.g., Milvus/Pinecone)
            embedding_model: Model for generating mathematical embeddings
        """
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.index_count = 0
        
    def index_result(self, conversation_id: str,
                    problem_statement: str,
                    result: Any,
                    proof_trace: Optional[str] = None,
                    metadata: Dict[str, Any] = None) -> str:
        """
        Index a confirmed result in the Vector Database.
        
        Called when a Supervisor confirms a result.
        Creates a permanent record for future retrieval.
        """
        # Generate unique ID
        entry_id = self._generate_entry_id(conversation_id, problem_statement)
        
        # Generate problem signature for matching
        signature = self._compute_problem_signature(problem_statement)
        
        # Generate embedding for semantic search
        embedding = self._generate_embedding(problem_statement, result)
        
        # Create memory entry
        entry = MemoryEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            problem_signature=signature,
            result=result,
            proof_trace=proof_trace,
            embedding=embedding,
            metadata=metadata or {}
        )
        
        # Store in Vector Database
        self._store_entry(entry)
        
        self.index_count += 1
        return entry_id
    
    def _generate_entry_id(self, conversation_id: str, 
                          problem_statement: str) -> str:
        """Generate unique ID for memory entry"""
        content = f"{conversation_id}:{problem_statement}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _compute_problem_signature(self, problem_statement: str) -> str:
        """
        Compute canonical signature for problem matching.
        
        Normalizes the problem to enable matching of equivalent
        formulations (e.g., "∫x²dx" vs "integrate x squared").
        """
        # Simple normalization - in production, use OMDoc canonicalization
        normalized = problem_statement.lower()
        normalized = normalized.replace(" ", "")
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _generate_embedding(self, problem: str, result: Any) -> np.ndarray:
        """
        Generate vector embedding for semantic search.
        
        Combines problem statement and result for comprehensive embedding.
        """
        combined = f"{problem} => {result}"
        
        # Use embedding model (placeholder - use actual model in production)
        if self.embedding_model:
            return self.embedding_model.encode(combined)
        else:
            # Fallback: simple hash-based pseudo-embedding
            hash_val = int(hashlib.md5(combined.encode()).hexdigest(), 16)
            np.random.seed(hash_val % (2**32))
            return np.random.randn(256).astype(np.float32)
    
    def _store_entry(self, entry: MemoryEntry) -> None:
        """Store entry in Vector Database"""
        self.vector_db.insert({
            'id': entry.entry_id,
            'embedding': entry.embedding.tolist() if entry.embedding is not None else [],
            'signature': entry.problem_signature,
            'result': str(entry.result),
            'proof_trace': entry.proof_trace,
            'timestamp': entry.timestamp.isoformat(),
            'metadata': entry.metadata
        })

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 2.3: THE RETRIEVAL SPECIALIST (RAG INTEGRATION)
# ═══════════════════════════════════════════════════════════════════════════

class RetrievalSpecialistAgent:
    """
    Agent 2.3: The Retrieval Specialist - RAG Integration
    
    External liaison responsible for querying mathematical repositories.
    Implements "Look-Before-You-Leap" pattern to short-circuit solving.
    
    📚 Reference: Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx
    """
    
    # Similarity thresholds for confidence classification
    EXACT_THRESHOLD = 0.98
    HIGH_THRESHOLD = 0.85
    MODERATE_THRESHOLD = 0.70
    LOW_THRESHOLD = 0.50
    
    def __init__(self, vector_db, embedding_model,
                 external_sources: List[str] = None):
        """
        Initialize with Vector Database and external source connections.
        
        Args:
            vector_db: Phase 0 Vector Database for internal lookups
            embedding_model: Model for query embedding
            external_sources: List of external libraries (e.g., ['mathlib', 'loogle'])
        """
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.external_sources = external_sources or []
        
    def query(self, problem_statement: str,
             problem_type: str = None,
             top_k: int = 5) -> RetrievalResult:
        """
        Query for existing theorems/results matching the problem.
        
        This is the core "Look-Before-You-Leap" method.
        Should be called BEFORE engaging solvers.
        """
        # Generate query embedding
        query_embedding = self._generate_query_embedding(problem_statement)
        
        # Search internal Vector Database first
        internal_results = self._search_internal(query_embedding, top_k)
        
        # Check for exact signature match
        signature = self._compute_signature(problem_statement)
        exact_match = self._check_exact_match(signature)
        if exact_match:
            return RetrievalResult(
                confidence=RetrievalConfidence.EXACT_MATCH,
                theorem_id=exact_match['id'],
                theorem_content=exact_match['result'],
                proof_sketch=exact_match.get('proof_trace'),
                source='internal',
                similarity_score=1.0
            )
        
        # Check internal semantic matches
        if internal_results:
            best = internal_results[0]
            confidence = self._classify_confidence(best['similarity'])
            if confidence != RetrievalConfidence.NO_MATCH:
                return RetrievalResult(
                    confidence=confidence,
                    theorem_id=best['id'],
                    theorem_content=best['result'],
                    proof_sketch=best.get('proof_trace'),
                    source='internal',
                    similarity_score=best['similarity']
                )
        
        # Query external sources if internal fails
        for source in self.external_sources:
            external_result = self._query_external(source, problem_statement)
            if external_result and external_result.confidence != RetrievalConfidence.NO_MATCH:
                return external_result
        
        # No relevant results found
        return RetrievalResult(
            confidence=RetrievalConfidence.NO_MATCH,
            similarity_score=0.0
        )
    
    def _generate_query_embedding(self, problem: str) -> np.ndarray:
        """Generate embedding for the query"""
        if self.embedding_model:
            return self.embedding_model.encode(problem)
        else:
            hash_val = int(hashlib.md5(problem.encode()).hexdigest(), 16)
            np.random.seed(hash_val % (2**32))
            return np.random.randn(256).astype(np.float32)
    
    def _search_internal(self, query_embedding: np.ndarray,
                        top_k: int) -> List[Dict]:
        """Search internal Vector Database"""
        results = self.vector_db.search(
            query_vector=query_embedding.tolist(),
            top_k=top_k
        )
        return results
    
    def _compute_signature(self, problem: str) -> str:
        """Compute problem signature for exact matching"""
        normalized = problem.lower().replace(" ", "")
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _check_exact_match(self, signature: str) -> Optional[Dict]:
        """Check for exact signature match in database"""
        result = self.vector_db.get_by_signature(signature)
        return result
    
    def _classify_confidence(self, similarity: float) -> RetrievalConfidence:
        """Classify confidence based on similarity score"""
        if similarity >= self.EXACT_THRESHOLD:
            return RetrievalConfidence.EXACT_MATCH
        elif similarity >= self.HIGH_THRESHOLD:
            return RetrievalConfidence.HIGH_SIMILARITY
        elif similarity >= self.MODERATE_THRESHOLD:
            return RetrievalConfidence.MODERATE
        elif similarity >= self.LOW_THRESHOLD:
            return RetrievalConfidence.LOW
        else:
            return RetrievalConfidence.NO_MATCH
    
    def _query_external(self, source: str, 
                       problem: str) -> Optional[RetrievalResult]:
        """Query external mathematical library"""
        # Placeholder for external API calls
        # In production, implement Mathlib/Loogle API clients
        if source == 'mathlib':
            return self._query_mathlib(problem)
        elif source == 'loogle':
            return self._query_loogle(problem)
        return None
    
    def _query_mathlib(self, problem: str) -> Optional[RetrievalResult]:
        """Query Mathlib for matching theorems"""
        # Placeholder - implement actual Mathlib API
        return None
    
    def _query_loogle(self, problem: str) -> Optional[RetrievalResult]:
        """Query Loogle for matching theorems"""
        # Placeholder - implement actual Loogle API
        return None

# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE MANAGEMENT TEAM COORDINATOR
# ═══════════════════════════════════════════════════════════════════════════

class KnowledgeManagementTeam:
    """
    Coordinator for the Knowledge Management Team.
    
    Provides unified interface for context extraction, memory indexing,
    and retrieval operations.
    
    📚 Reference: Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx
    """
    
    def __init__(self, blackboard, vector_db, embedding_model,
                 external_sources: List[str] = None):
        self.context_extractor = ContextExtractorAgent(blackboard)
        self.memory_indexer = MemoryIndexerAgent(vector_db, embedding_model)
        self.retrieval_specialist = RetrievalSpecialistAgent(
            vector_db, embedding_model, external_sources
        )
        
    def look_before_leap(self, problem_statement: str) -> RetrievalResult:
        """
        The "Look-Before-You-Leap" protocol.
        
        Should be called by Orchestrator immediately after classification.
        Returns high-confidence match if available.
        """
        return self.retrieval_specialist.query(problem_statement)
    
    def extract_context(self, conversation_id: str,
                       target_variables: set,
                       problem_type: str) -> ContextPacket:
        """Extract relevant context for a sub-task"""
        return self.context_extractor.extract_context(
            conversation_id, target_variables, problem_type
        )
    
    def record_result(self, conversation_id: str,
                     problem: str,
                     result: Any,
                     proof_trace: str = None) -> str:
        """Record a confirmed result for future retrieval"""
        return self.memory_indexer.index_result(
            conversation_id, problem, result, proof_trace
        )

───────────────────────────────────────────────────────────────────
## STEP 3: The Hypothesis Generation Team (The "Scouts")
### WHAT: Tree-of-Thoughts Strategic Planning
Construct the strategic planning layer that implements Tree-of-Thoughts (ToT) reasoning. This team explores the "solution space" to find the optimal path before committing computational resources. Instead of blindly executing the first valid approach, the system now evaluates multiple strategies and selects the most promising one.
### WHY: Addressing the Search Gap (Gap 1)
Standard agents are linear—they blindly follow the first path they see. For complex proofs, this leads to dead ends and wasted compute. The Hypothesis Generation Team enforces strategic thinking: proposing multiple approaches, evaluating their "promise scores," and enabling graceful backtracking when the chosen path fails.
📚 Reference: Phase_3_installs_the_cognitive_immune_system.docx, Step 3
### HOW: Three-Agent Implementation
Agent 3.1: The Hypothesis Generator
Directive: Build a creative agent strictly forbidden from solving. Its job is to propose strategies, not execute them. A creative planner rather than an executor.
Output: Generates high-level plans. For a complex proof, it might output:
    1. "Plan A: Attempt Proof by Induction."
    2. "Plan B: Attempt Proof by Contradiction."
    3. "Plan C: Direct Algebraic Manipulation."
Agent 3.2: The Path Evaluator
Directive: Implement a heuristic agent that estimates the "Promise Score" of proposed plans. A judge that predicts success without executing.
Logic: Analyzes problem structure to predict success. "This problem has a recursive structure, so 'Induction' has a 90% promise score; 'Contradiction' has 20%." The system then executes the highest-scoring plan first, avoiding dead ends.
Agent 3.3: The Backtracking Manager
Directive: Implement the state-management agent responsible for "Time Travel." Handles failure gracefully through state restoration.
Mechanism: If Plan A (Induction) hits a dead end, this agent resets the Blackboard state to the "pre-solving" snapshot and triggers Plan B (Contradiction). This prevents the system from getting stuck in a failed state.
### CODE: Hypothesis Generation Team Implementation
# hypothesis_generation.py - The "Scouts" Team
# Phase 3: Meta-Cognitive Middleware - Search Gap Resolution

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
from enum import Enum, auto
from datetime import datetime
import copy
import hashlib

# ═══════════════════════════════════════════════════════════════════════════
# STRATEGY AND PLAN TYPES
# ═══════════════════════════════════════════════════════════════════════════

class StrategyType(Enum):
    """Types of mathematical proof/solution strategies"""
    INDUCTION = "proof_by_induction"
    CONTRADICTION = "proof_by_contradiction"
    DIRECT = "direct_proof"
    CONSTRUCTION = "proof_by_construction"
    CONTRAPOSITIVE = "proof_by_contrapositive"
    EXHAUSTION = "proof_by_exhaustion"
    ALGEBRAIC_MANIPULATION = "algebraic_manipulation"
    SUBSTITUTION = "substitution"
    INTEGRATION_BY_PARTS = "integration_by_parts"
    PARTIAL_FRACTIONS = "partial_fractions"
    TRIG_SUBSTITUTION = "trigonometric_substitution"
    NUMERICAL_FALLBACK = "numerical_approximation"

class PlanStatus(Enum):
    """Status of a solution plan"""
    PROPOSED = auto()
    EVALUATING = auto()
    SELECTED = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()
    ABANDONED = auto()

@dataclass
class SolutionPlan:
    """A proposed solution strategy"""
    plan_id: str
    strategy: StrategyType
    description: str
    prerequisite_checks: List[str]
    estimated_complexity: str  # 'low', 'medium', 'high'
    promise_score: float = 0.0
    status: PlanStatus = PlanStatus.PROPOSED
    execution_trace: List[str] = field(default_factory=list)
    failure_reason: Optional[str] = None
    
@dataclass
class BlackboardSnapshot:
    """Snapshot of Blackboard state for backtracking"""
    snapshot_id: str
    timestamp: datetime
    conversation_id: str
    state_data: Dict[str, Any]
    active_plan_id: Optional[str]

@dataclass
class TreeNode:
    """Node in the Tree-of-Thoughts structure"""
    node_id: str
    plan: SolutionPlan
    parent_id: Optional[str]
    children: List[str] = field(default_factory=list)
    depth: int = 0
    is_terminal: bool = False
    terminal_success: bool = False

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 3.1: THE HYPOTHESIS GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class HypothesisGeneratorAgent:
    """
    Agent 3.1: The Hypothesis Generator - Creative Strategist
    
    Proposes solution strategies WITHOUT solving. Strictly forbidden
    from executing calculations; its role is strategic planning only.
    
    📚 Reference: Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx
    """
    
    # Strategy templates for different problem types
    PROOF_STRATEGIES = [
        StrategyType.INDUCTION,
        StrategyType.CONTRADICTION,
        StrategyType.DIRECT,
        StrategyType.CONTRAPOSITIVE,
    ]
    
    COMPUTATION_STRATEGIES = [
        StrategyType.ALGEBRAIC_MANIPULATION,
        StrategyType.SUBSTITUTION,
    ]
    
    INTEGRATION_STRATEGIES = [
        StrategyType.INTEGRATION_BY_PARTS,
        StrategyType.PARTIAL_FRACTIONS,
        StrategyType.TRIG_SUBSTITUTION,
        StrategyType.SUBSTITUTION,
    ]
    
    def __init__(self):
        self.plan_counter = 0
        
    def generate_hypotheses(self, omdoc_object,
                          problem_type: str,
                          constraints: Dict[str, Any] = None
                          ) -> List[SolutionPlan]:
        """
        Generate multiple solution strategies for a problem.
        
        This method NEVER solves; it only proposes approaches.
        """
        strategies = self._select_applicable_strategies(
            omdoc_object, problem_type
        )
        
        plans = []
        for strategy in strategies:
            plan = self._create_plan(strategy, omdoc_object, problem_type)
            plans.append(plan)
        
        return plans
    
    def _select_applicable_strategies(self, omdoc_object,
                                     problem_type: str) -> List[StrategyType]:
        """Select strategies applicable to this problem type"""
        if problem_type == 'proof':
            return self.PROOF_STRATEGIES.copy()
        elif problem_type == 'integration':
            return self.INTEGRATION_STRATEGIES.copy()
        elif problem_type == 'computation':
            return self.COMPUTATION_STRATEGIES.copy()
        else:
            # Default: try algebraic manipulation + numerical fallback
            return [
                StrategyType.ALGEBRAIC_MANIPULATION,
                StrategyType.NUMERICAL_FALLBACK
            ]
    
    def _create_plan(self, strategy: StrategyType,
                    omdoc_object,
                    problem_type: str) -> SolutionPlan:
        """Create a detailed plan for a strategy"""
        self.plan_counter += 1
        plan_id = f"plan_{self.plan_counter:04d}"
        
        # Strategy-specific descriptions and prerequisites
        descriptions = {
            StrategyType.INDUCTION: {
                'desc': "Attempt proof by mathematical induction: "
                        "establish base case, then prove P(n) → P(n+1)",
                'prereqs': ['has_natural_number_variable', 'recursive_structure'],
                'complexity': 'medium'
            },
            StrategyType.CONTRADICTION: {
                'desc': "Attempt proof by contradiction: "
                        "assume negation, derive logical inconsistency",
                'prereqs': ['statement_is_negatable'],
                'complexity': 'medium'
            },
            StrategyType.DIRECT: {
                'desc': "Attempt direct algebraic proof: "
                        "manipulate expressions to reach conclusion",
                'prereqs': [],
                'complexity': 'low'
            },
            StrategyType.INTEGRATION_BY_PARTS: {
                'desc': "Apply integration by parts: ∫u dv = uv - ∫v du. "
                        "Select u and dv based on LIATE rule",
                'prereqs': ['product_of_functions'],
                'complexity': 'medium'
            },
            StrategyType.PARTIAL_FRACTIONS: {
                'desc': "Decompose rational function into partial fractions, "
                        "then integrate each term",
                'prereqs': ['rational_function', 'factorable_denominator'],
                'complexity': 'medium'
            },
            StrategyType.TRIG_SUBSTITUTION: {
                'desc': "Apply trigonometric substitution for expressions "
                        "involving √(a²-x²), √(a²+x²), or √(x²-a²)",
                'prereqs': ['has_radical_form'],
                'complexity': 'high'
            },
            StrategyType.NUMERICAL_FALLBACK: {
                'desc': "Fall back to numerical approximation methods "
                        "when symbolic methods fail",
                'prereqs': [],
                'complexity': 'low'
            },
        }
        
        info = descriptions.get(strategy, {
            'desc': f"Apply {strategy.value} strategy",
            'prereqs': [],
            'complexity': 'medium'
        })
        
        return SolutionPlan(
            plan_id=plan_id,
            strategy=strategy,
            description=info['desc'],
            prerequisite_checks=info['prereqs'],
            estimated_complexity=info['complexity']
        )

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 3.2: THE PATH EVALUATOR
# ═══════════════════════════════════════════════════════════════════════════

class PathEvaluatorAgent:
    """
    Agent 3.2: The Path Evaluator - Heuristic Judge
    
    Estimates the "Promise Score" of proposed plans without executing them.
    Analyzes problem structure to predict which strategy is most likely
    to succeed.
    
    📚 Reference: Phase_3_installs_the_cognitive_immune_system.docx, Action 3.2
    """
    
    def __init__(self):
        # Heuristic weights learned from historical performance
        self.strategy_base_scores = {
            StrategyType.INDUCTION: 0.7,
            StrategyType.CONTRADICTION: 0.5,
            StrategyType.DIRECT: 0.8,
            StrategyType.CONTRAPOSITIVE: 0.6,
            StrategyType.ALGEBRAIC_MANIPULATION: 0.85,
            StrategyType.SUBSTITUTION: 0.75,
            StrategyType.INTEGRATION_BY_PARTS: 0.7,
            StrategyType.PARTIAL_FRACTIONS: 0.8,
            StrategyType.TRIG_SUBSTITUTION: 0.6,
            StrategyType.NUMERICAL_FALLBACK: 0.95,  # Always works, but less desirable
        }
        
        # Problem features that boost certain strategies
        self.feature_bonuses = {
            'recursive_structure': {StrategyType.INDUCTION: 0.2},
            'has_natural_number_variable': {StrategyType.INDUCTION: 0.15},
            'product_of_functions': {StrategyType.INTEGRATION_BY_PARTS: 0.2},
            'rational_function': {StrategyType.PARTIAL_FRACTIONS: 0.25},
            'has_radical_form': {StrategyType.TRIG_SUBSTITUTION: 0.2},
            'polynomial_expression': {StrategyType.DIRECT: 0.1},
        }
        
    def evaluate_plans(self, plans: List[SolutionPlan],
                      omdoc_object,
                      problem_features: Dict[str, bool] = None
                      ) -> List[SolutionPlan]:
        """
        Evaluate and rank plans by promise score.
        
        Returns plans sorted by promise score (highest first).
        """
        features = problem_features or self._extract_features(omdoc_object)
        
        for plan in plans:
            plan.promise_score = self._compute_promise_score(plan, features)
        
        # Sort by promise score descending
        plans.sort(key=lambda p: p.promise_score, reverse=True)
        
        return plans
    
    def _extract_features(self, omdoc_object) -> Dict[str, bool]:
        """Extract structural features from the problem"""
        features = {}
        expr = omdoc_object.expression_tree
        
        # Check for recursive/inductive structure
        features['recursive_structure'] = self._has_recursive_structure(expr)
        
        # Check for natural number variables
        features['has_natural_number_variable'] = self._has_natural_variable(omdoc_object)
        
        # Check for product of functions (for integration by parts)
        features['product_of_functions'] = self._has_product_structure(expr)
        
        # Check for rational function
        features['rational_function'] = self._is_rational_function(expr)
        
        # Check for radical forms
        features['has_radical_form'] = self._has_radical_form(expr)
        
        # Check for polynomial
        features['polynomial_expression'] = self._is_polynomial(expr)
        
        return features
    
    def _compute_promise_score(self, plan: SolutionPlan,
                              features: Dict[str, bool]) -> float:
        """Compute promise score for a plan given problem features"""
        # Start with base score
        score = self.strategy_base_scores.get(plan.strategy, 0.5)
        
        # Apply feature bonuses
        for feature, is_present in features.items():
            if is_present and feature in self.feature_bonuses:
                bonus = self.feature_bonuses[feature].get(plan.strategy, 0)
                score += bonus
        
        # Penalize for unmet prerequisites
        for prereq in plan.prerequisite_checks:
            if prereq in features and not features[prereq]:
                score -= 0.15
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))
    
    def _has_recursive_structure(self, expr) -> bool:
        """Check if expression has recursive/inductive structure"""
        # Look for patterns like f(n-1), f(n+1), factorial, etc.
        expr_str = str(expr)
        patterns = ['(n-1)', '(n+1)', 'factorial', 'fib', 'sum_']
        return any(p in expr_str for p in patterns)
    
    def _has_natural_variable(self, omdoc_object) -> bool:
        """Check for natural number domain variable"""
        constraints = omdoc_object.metadata.get('constraints', [])
        for c in constraints:
            if hasattr(c, 'constraint_type') and c.constraint_type == 'integer':
                return True
        return False
    
    def _has_product_structure(self, expr) -> bool:
        """Check for product of distinct function types"""
        # Simplified check - look for multiplication patterns
        try:
            import sympy as sp
            sympy_expr = sp.sympify(expr) if isinstance(expr, str) else expr
            # Check if it's a multiplication of different function types
            if sympy_expr.is_Mul:
                return len(sympy_expr.args) >= 2
        except:
            pass
        return False
    
    def _is_rational_function(self, expr) -> bool:
        """Check if expression is a rational function"""
        try:
            import sympy as sp
            sympy_expr = sp.sympify(expr) if isinstance(expr, str) else expr
            numer, denom = sympy_expr.as_numer_denom()
            return denom != 1
        except:
            return False
    
    def _has_radical_form(self, expr) -> bool:
        """Check for square root patterns"""
        try:
            import sympy as sp
            sympy_expr = sp.sympify(expr) if isinstance(expr, str) else expr
            return sympy_expr.has(sp.sqrt)
        except:
            return False
    
    def _is_polynomial(self, expr) -> bool:
        """Check if expression is a polynomial"""
        try:
            import sympy as sp
            sympy_expr = sp.sympify(expr) if isinstance(expr, str) else expr
            return sympy_expr.is_polynomial()
        except:
            return False

# ═══════════════════════════════════════════════════════════════════════════
# AGENT 3.3: THE BACKTRACKING MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class BacktrackingManagerAgent:
    """
    Agent 3.3: The Backtracking Manager - State Time Travel
    
    Manages Blackboard state snapshots and enables recovery from
    failed solution attempts. Implements "Time Travel" for the system.
    
    📚 Reference: Phase_3_installs_the_cognitive_immune_system.docx, Action 3.3
    """
    
    def __init__(self, blackboard):
        """
        Initialize with Blackboard reference for state management.
        
        Args:
            blackboard: Phase 0 Blackboard instance
        """
        self.blackboard = blackboard
        self.snapshots: Dict[str, BlackboardSnapshot] = {}
        self.snapshot_stack: Dict[str, List[str]] = {}  # conversation_id -> [snapshot_ids]
        
    def create_snapshot(self, conversation_id: str,
                       plan_id: str) -> str:
        """
        Create a snapshot of current Blackboard state before plan execution.
        
        Called by Orchestrator before delegating to solvers.
        """
        snapshot_id = self._generate_snapshot_id(conversation_id)
        
        # Capture current Blackboard state
        state_data = self.blackboard.get_full_state(conversation_id)
        
        snapshot = BlackboardSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            conversation_id=conversation_id,
            state_data=copy.deepcopy(state_data),
            active_plan_id=plan_id
        )
        
        self.snapshots[snapshot_id] = snapshot
        
        # Push to conversation stack
        if conversation_id not in self.snapshot_stack:
            self.snapshot_stack[conversation_id] = []
        self.snapshot_stack[conversation_id].append(snapshot_id)
        
        return snapshot_id
    
    def restore_snapshot(self, conversation_id: str,
                        snapshot_id: str = None) -> bool:
        """
        Restore Blackboard to a previous snapshot state.
        
        If snapshot_id is None, restores to most recent snapshot.
        This is the "Time Travel" operation.
        """
        # Get target snapshot
        if snapshot_id is None:
            stack = self.snapshot_stack.get(conversation_id, [])
            if not stack:
                return False
            snapshot_id = stack[-1]
        
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            return False
        
        # Restore Blackboard state
        self.blackboard.restore_state(conversation_id, snapshot.state_data)
        
        # Pop snapshots after this one
        stack = self.snapshot_stack.get(conversation_id, [])
        if snapshot_id in stack:
            idx = stack.index(snapshot_id)
            # Remove this and all later snapshots
            removed = stack[idx:]
            self.snapshot_stack[conversation_id] = stack[:idx]
            for sid in removed:
                if sid in self.snapshots:
                    del self.snapshots[sid]
        
        return True
    
    def handle_plan_failure(self, conversation_id: str,
                           failed_plan: SolutionPlan,
                           alternative_plans: List[SolutionPlan]
                           ) -> Optional[SolutionPlan]:
        """
        Handle a failed plan by restoring state and selecting alternative.
        
        Returns the next plan to try, or None if no alternatives remain.
        """
        # Record failure
        failed_plan.status = PlanStatus.FAILED
        
        # Restore to pre-execution state
        success = self.restore_snapshot(conversation_id)
        if not success:
            return None
        
        # Find next untried plan
        for plan in alternative_plans:
            if plan.status == PlanStatus.PROPOSED:
                plan.status = PlanStatus.SELECTED
                return plan
        
        return None  # All plans exhausted
    
    def _generate_snapshot_id(self, conversation_id: str) -> str:
        """Generate unique snapshot ID"""
        content = f"{conversation_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def clear_session(self, conversation_id: str) -> None:
        """Clear all snapshots for a completed session"""
        stack = self.snapshot_stack.get(conversation_id, [])
        for snapshot_id in stack:
            if snapshot_id in self.snapshots:
                del self.snapshots[snapshot_id]
        if conversation_id in self.snapshot_stack:
            del self.snapshot_stack[conversation_id]

# ═══════════════════════════════════════════════════════════════════════════
# HYPOTHESIS GENERATION TEAM COORDINATOR
# ═══════════════════════════════════════════════════════════════════════════

class HypothesisGenerationTeam:
    """
    Coordinator for the Hypothesis Generation Team.
    
    Implements Tree-of-Thoughts reasoning by coordinating hypothesis
    generation, evaluation, and backtracking.
    
    📚 Reference: Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx
    """
    
    def __init__(self, blackboard):
        self.hypothesis_generator = HypothesisGeneratorAgent()
        self.path_evaluator = PathEvaluatorAgent()
        self.backtracking_manager = BacktrackingManagerAgent(blackboard)
        
        # Tree structure for complex problems
        self.thought_trees: Dict[str, Dict[str, TreeNode]] = {}
        
    def scout(self, omdoc_object,
             conversation_id: str,
             problem_type: str) -> SolutionPlan:
        """
        The "Scouting" protocol for high-complexity problems.
        
        Generates hypotheses, evaluates them, and returns the best plan.
        Creates snapshot before execution begins.
        """
        # Step 1: Generate hypotheses
        plans = self.hypothesis_generator.generate_hypotheses(
            omdoc_object, problem_type
        )
        
        # Step 2: Evaluate and rank
        ranked_plans = self.path_evaluator.evaluate_plans(
            plans, omdoc_object
        )
        
        # Step 3: Select best plan
        if not ranked_plans:
            return None
        
        best_plan = ranked_plans[0]
        best_plan.status = PlanStatus.SELECTED
        
        # Step 4: Create snapshot before execution
        self.backtracking_manager.create_snapshot(
            conversation_id, best_plan.plan_id
        )
        
        # Store alternative plans for potential backtracking
        self._store_alternatives(conversation_id, ranked_plans[1:])
        
        return best_plan
    
    def handle_failure(self, conversation_id: str,
                      failed_plan: SolutionPlan) -> Optional[SolutionPlan]:
        """
        Handle plan failure and attempt backtracking to alternative.
        """
        alternatives = self._get_alternatives(conversation_id)
        return self.backtracking_manager.handle_plan_failure(
            conversation_id, failed_plan, alternatives
        )
    
    def _store_alternatives(self, conversation_id: str,
                           plans: List[SolutionPlan]) -> None:
        """Store alternative plans for backtracking"""
        if conversation_id not in self.thought_trees:
            self.thought_trees[conversation_id] = {
                'alternatives': plans
            }
        else:
            self.thought_trees[conversation_id]['alternatives'] = plans
    
    def _get_alternatives(self, conversation_id: str) -> List[SolutionPlan]:
        """Retrieve stored alternative plans"""
        tree_data = self.thought_trees.get(conversation_id, {})
        return tree_data.get('alternatives', [])

───────────────────────────────────────────────────────────────────
## STEP 4: Wiring the "Meta-Brain" (Orchestrator Update)
### WHAT: Control Loop Evolution
Update the Phase 1 Tier 1 Orchestrator to integrate the three new teams. The control loop must evolve from the simple Plan → Solve pattern to a robust Analyze → Hypothesize → Validate → Solve cycle. This requires implementing three new mandatory protocols.
### WHY: Integrating the Meta-Cognitive Layer
The Phase 3 teams provide critical capabilities, but they must be wired into the Orchestrator's decision-making process to take effect. Without these protocol updates, the new agents would exist but never be invoked, leaving the system as brittle as before.
📚 Reference: Phase_3_installs_the_cognitive_immune_system.docx, Step 4
### HOW: Three Protocol Updates
Protocol 1: The "Pre-Flight" Check
Constraint: The Orchestrator is now hard-coded to NEVER delegate a task to a Tier 2 Domain Supervisor until the Precondition Validation Team returns a STATUS: VALID token. Any other status halts execution and returns an error to the user.
Protocol 2: The "Look-Before-You-Leap" Check
Constraint: Immediately after problem classification, the Orchestrator must query the Knowledge Management Team. If the Retrieval Specialist finds a high-confidence match (e.g., "This is a known identity"), the solving phase is skipped entirely and the retrieved proof is returned directly.
Protocol 3: The "Scouting" Check
Constraint: For problems tagged "High Complexity" by the Analysis Team, the Orchestrator must invoke the Hypothesis Generator first. It then delegates the selected strategy (e.g., "Use Induction") to the Domain Supervisors, rather than just the raw problem.
### CODE: Updated Orchestrator Implementation
# orchestrator_phase3.py - Updated Tier 1 Orchestrator
# Phase 3: Meta-Cognitive Middleware Integration

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum, auto

# Import Phase 0-2 components
# from phase0 import DirectoryFacilitator, Blackboard, FIPAMessage
# from phase1 import StructureRecognizerAgent, ProblemType
# from phase2 import DomainSupervisor

# Import Phase 3 teams
# from precondition_validation import PreconditionValidationTeam, ValidationStatus
# from knowledge_management import KnowledgeManagementTeam, RetrievalConfidence
# from hypothesis_generation import HypothesisGenerationTeam, SolutionPlan

class ComplexityLevel(Enum):
    """Problem complexity classification"""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()

@dataclass
class OrchestratorDecision:
    """Record of Orchestrator decision for logging/debugging"""
    conversation_id: str
    decision_type: str
    validation_status: Optional[str] = None
    retrieval_result: Optional[str] = None
    selected_strategy: Optional[str] = None
    delegated_to: Optional[str] = None
    skip_solving: bool = False
    error_message: Optional[str] = None

class Phase3Orchestrator:
    """
    Tier 1 Orchestrator with Phase 3 Meta-Cognitive Integration
    
    Implements the evolved control loop:
    Analyze → Hypothesize → Validate → Solve
    
    📚 Reference: Phase_3_installs_the_cognitive_immune_system.docx, Step 4
    """
    
    # Complexity threshold for scouting protocol
    HIGH_COMPLEXITY_THRESHOLD = 0.7
    
    def __init__(self, 
                 directory_facilitator,
                 blackboard,
                 vector_db,
                 embedding_model,
                 available_solvers: Dict[str, set]):
        """
        Initialize Orchestrator with Phase 0-3 infrastructure.
        
        Args:
            directory_facilitator: Phase 0 DF for agent discovery
            blackboard: Phase 0 Blackboard for shared memory
            vector_db: Phase 0 Vector Database for RAG
            embedding_model: Model for knowledge retrieval
            available_solvers: Registry of solver capabilities
        """
        self.df = directory_facilitator
        self.blackboard = blackboard
        
        # Initialize Phase 3 teams
        self.precondition_team = PreconditionValidationTeam(
            available_solvers, blackboard
        )
        self.knowledge_team = KnowledgeManagementTeam(
            blackboard, vector_db, embedding_model,
            external_sources=['mathlib', 'loogle']
        )
        self.hypothesis_team = HypothesisGenerationTeam(blackboard)
        
        # Decision log for debugging
        self.decision_log: List[OrchestratorDecision] = []
        
    def process(self, omdoc_object, conversation_id: str) -> Any:
        """
        Main processing method with Phase 3 protocol integration.
        
        Implements: Analyze → Hypothesize → Validate → Solve
        """
        decision = OrchestratorDecision(
            conversation_id=conversation_id,
            decision_type="process_start"
        )
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 1: ANALYZE (Problem Classification)
        # ═══════════════════════════════════════════════════════════════
        problem_type = omdoc_object.problem_type.value
        complexity = self._assess_complexity(omdoc_object)
        
        # ═══════════════════════════════════════════════════════════════
        # PROTOCOL 1: "PRE-FLIGHT" CHECK
        # CONSTRAINT: NEVER delegate until validation returns VALID
        # ═══════════════════════════════════════════════════════════════
        validation_result = self.precondition_team.validate(
            omdoc_object,
            conversation_id,
            operation_type=self._infer_operation_type(omdoc_object)
        )
        
        decision.validation_status = validation_result.status.name
        
        if not validation_result.is_valid:
            # HALT: Preconditions not met
            decision.error_message = validation_result.error_message
            decision.decision_type = "halted_preflight"
            self.decision_log.append(decision)
            
            return {
                'status': 'ERROR',
                'code': validation_result.status.name,
                'message': validation_result.error_message,
                'violations': validation_result.constraint_violations,
                'edge_cases': validation_result.edge_cases_detected
            }
        
        # ═══════════════════════════════════════════════════════════════
        # PROTOCOL 2: "LOOK-BEFORE-YOU-LEAP" CHECK
        # Query Knowledge Management Team for existing solutions
        # ═══════════════════════════════════════════════════════════════
        problem_statement = self._extract_problem_statement(omdoc_object)
        retrieval_result = self.knowledge_team.look_before_leap(problem_statement)
        
        decision.retrieval_result = retrieval_result.confidence.name
        
        if retrieval_result.should_skip_solving():
            # SHORT-CIRCUIT: Known theorem found
            decision.decision_type = "retrieved_solution"
            decision.skip_solving = True
            self.decision_log.append(decision)
            
            return {
                'status': 'SUCCESS',
                'source': 'retrieved',
                'theorem_id': retrieval_result.theorem_id,
                'result': retrieval_result.theorem_content,
                'proof': retrieval_result.proof_sketch,
                'confidence': retrieval_result.similarity_score
            }
        
        # ═══════════════════════════════════════════════════════════════
        # PROTOCOL 3: "SCOUTING" CHECK (For High Complexity Problems)
        # Invoke Hypothesis Generation Team before solving
        # ═══════════════════════════════════════════════════════════════
        selected_strategy = None
        
        if complexity == ComplexityLevel.HIGH:
            plan = self.hypothesis_team.scout(
                omdoc_object,
                conversation_id,
                problem_type
            )
            
            if plan:
                selected_strategy = plan
                decision.selected_strategy = plan.strategy.value
                decision.decision_type = "strategy_selected"
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 4: SOLVE (Delegate to Domain Supervisors)
        # ═══════════════════════════════════════════════════════════════
        # Discover appropriate supervisor via DF
        supervisor = self._discover_supervisor(omdoc_object.domain_tag)
        
        if not supervisor:
            decision.error_message = f"No supervisor for domain: {omdoc_object.domain_tag}"
            decision.decision_type = "no_supervisor"
            self.decision_log.append(decision)
            return {'status': 'ERROR', 'message': decision.error_message}
        
        decision.delegated_to = supervisor.agent_id
        
        # Prepare task with strategy context (if scouting was done)
        task_context = {
            'omdoc': omdoc_object,
            'conversation_id': conversation_id,
            'constraints': validation_result.propagated_constraints,
            'strategy': selected_strategy
        }
        
        # Delegate to supervisor
        result = self._delegate_to_supervisor(supervisor, task_context)
        
        # ═══════════════════════════════════════════════════════════════
        # PHASE 5: HANDLE RESULT (Including Backtracking)
        # ═══════════════════════════════════════════════════════════════
        if result.get('status') == 'FAILED' and selected_strategy:
            # Attempt backtracking to alternative strategy
            alternative = self.hypothesis_team.handle_failure(
                conversation_id, selected_strategy
            )
            
            if alternative:
                # Retry with alternative strategy
                decision.decision_type = "backtracking"
                task_context['strategy'] = alternative
                result = self._delegate_to_supervisor(supervisor, task_context)
        
        # Record successful result for future retrieval
        if result.get('status') == 'SUCCESS':
            self.knowledge_team.record_result(
                conversation_id,
                problem_statement,
                result.get('result'),
                result.get('proof_trace')
            )
        
        self.decision_log.append(decision)
        return result
    
    def _assess_complexity(self, omdoc_object) -> ComplexityLevel:
        """Assess problem complexity for scouting protocol"""
        # Complexity heuristics
        expr = omdoc_object.expression_tree
        
        # Count operations
        expr_str = str(expr)
        op_count = sum(expr_str.count(op) for op in ['+', '-', '*', '/', '^', 'sqrt', 'log', 'sin', 'cos'])
        
        # Count variables
        try:
            import sympy as sp
            sympy_expr = sp.sympify(expr) if isinstance(expr, str) else expr
            var_count = len(sympy_expr.free_symbols)
        except:
            var_count = 1
        
        # Compute complexity score
        score = (op_count / 20) + (var_count / 5)
        
        if score >= self.HIGH_COMPLEXITY_THRESHOLD:
            return ComplexityLevel.HIGH
        elif score >= 0.3:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.LOW
    
    def _infer_operation_type(self, omdoc_object) -> Optional[str]:
        """Infer operation type for edge case detection"""
        raw = omdoc_object.raw_input.lower()
        if 'invert' in raw or 'inverse' in raw:
            return 'matrix_inversion'
        return None
    
    def _extract_problem_statement(self, omdoc_object) -> str:
        """Extract canonical problem statement for retrieval"""
        return f"{omdoc_object.problem_type.value}: {omdoc_object.expression_tree}"
    
    def _discover_supervisor(self, domain_tag: str):
        """Discover appropriate Domain Supervisor via DF"""
        service_type = f"supervisor.{domain_tag.lower()}"
        results = self.df.search(service_type=service_type)
        return results[0] if results else None
    
    def _delegate_to_supervisor(self, supervisor, task_context: Dict) -> Dict:
        """Delegate task to Domain Supervisor via FIPA-ACL"""
        # Create FIPA-ACL REQUEST message
        message = {
            'performative': 'REQUEST',
            'sender': 'orchestrator_001',
            'receiver': supervisor.agent_id,
            'conversation_id': task_context['conversation_id'],
            'content': task_context,
            'ontology': 'mathematics',
            'protocol': 'fipa-request'
        }
        
        # Post to Blackboard for supervisor pickup
        self.blackboard.post({
            'entry_type': 'task_delegation',
            'message': message,
            'status': 'PENDING'
        })
        
        # In production, this would be async; simplified here
        # Wait for result on Blackboard
        result = self._wait_for_result(task_context['conversation_id'])
        
        return result
    
    def _wait_for_result(self, conversation_id: str, timeout: int = 300) -> Dict:
        """Wait for solver result (simplified synchronous version)"""
        # Placeholder - actual implementation would poll Blackboard
        return {'status': 'SUCCESS', 'result': 'placeholder'}

───────────────────────────────────────────────────────────────────
# 4. Phase 3 Deliverable: The "Resilient" System
At the conclusion of Phase 3, the system has transformed from a "Fragile Genius" into a "Resilient Professional." The Meta-Cognitive Middleware provides the cognitive immune system that creates resilience, context, and foresight.
## 4.1 Behavior Changes
Example 1 - Hallucination Prevention: If asked to "Calculate the real square root of -4," the Phase 2 system would crash or output an imaginary number (hallucination). The Phase 3 system's Assumption Validator catches the domain constraint violation and returns:
   "Error: Real domain constraint violated. √(-4) has no real solution."
Example 2 - Efficiency Gains: If asked a complex combinatorics question, the Hypothesis Generator evaluates strategic paths, and the Retrieval Specialist might find that it's a solved identity in Mathlib, answering in milliseconds rather than minutes of calculation.
## 4.2 Control Loop Comparison

| Phase | Control Loop |
| --- | --- |
| Phase 1-2 | Plan → Solve |
| Phase 3 | Analyze → Hypothesize → Validate → Solve |


───────────────────────────────────────────────────────────────────
# 5. Verification Checklist
Phase 3 is complete when ALL of the following conditions are met:
- ☐  All 4 Precondition Validation agents (Domain Checker, Assumption Validator, Edge Case Detector, Constraint Propagator) are instantiated and registered with DF
- ☐  All 3 Knowledge Management agents (Context Extractor, Memory Indexer, Retrieval Specialist) are instantiated and connected to Vector Database
- ☐  All 3 Hypothesis Generation agents (Hypothesis Generator, Path Evaluator, Backtracking Manager) are instantiated and managing Blackboard state
- ☐  Orchestrator Protocol 1 (Pre-Flight Check) blocks invalid problems with STATUS: DOMAIN_MISMATCH or CONSTRAINT_VIOLATION
- ☐  Orchestrator Protocol 2 (Look-Before-You-Leap) successfully retrieves and returns known theorems without solving
- ☐  Orchestrator Protocol 3 (Scouting) generates and ranks strategies for high-complexity problems
- ☐  Backtracking Manager successfully restores state and triggers alternative plans on failure
- ☐  End-to-end test: Request √(-4) in real domain → Returns constraint violation error (not crash)
- ☐  End-to-end test: Request known integral → Returns retrieved solution without computation
- ☐  End-to-end test: Complex proof → Generates multiple strategies, selects highest-scoring plan
───────────────────────────────────────────────────────────────────
# 6. Transition to Phase 4
With the Resilient Professional now operational, the system is prepared for Phase 4: Dynamic Governance & Resilience. Phase 4 will teach the system to:
- Resolve conflicts between agents when they disagree (Conflict Resolution Team)
- Diagnose and recover from failures autonomously (Failure Analysis Team)
- Optimize its own routing logic based on performance history (Meta-Learning Team)

The Phase 3 foundation—with its validation, memory, and strategic planning capabilities—provides the stable substrate required for these advanced self-improvement mechanisms.
───────────────────────────────────────────────────────────────────
# 7. Source Documentation Reference
This build order document synthesizes information from the following project documentation:
- Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.docx — Detailed agent team specifications with directives and mechanisms
- Phase_3_installs_the_cognitive_immune_system.docx — Step-by-step technical specification with action items
- phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx — Overall roadmap and phase integration context
- architectural_roadmap.docx — 65-agent system architecture overview and agent count specifications
- phase_3_Building_The_Resilient_AI_Brain.pdf — Visual blueprint and architectural diagrams
- phase_3_Genius_to_Stability.pdf — Transition documentation from Fragile Genius to Resilient Professional
- phase_3_mindmap.png — Visual mind map of Phase 3 components
- Phase_0_Build_Order_Breakdown.docx — Phase 0 infrastructure dependencies (Blackboard, Vector DB, DF)
- Phase_1_Build_Order_Breakdown.docx — Phase 1 Orchestrator and Verification Core foundations
- Phase_2_Build_Order_Breakdown.docx — Phase 2 Domain Supervisors and Specialists to be validated

— End of Phase 3 Build Order Breakdown —