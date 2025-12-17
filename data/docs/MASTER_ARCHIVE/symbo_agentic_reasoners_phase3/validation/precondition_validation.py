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
PRECONDITION VALIDATION TEAM - "The Anesthesiologist"
======================================================

Phase 3: Meta-Cognitive Middleware - Assumption Gap Resolution

PURPOSE:
-------
Construct the mandatory validation layer that certifies every problem is
mathematically sound and well-defined before any solver touches it. This
team acts as the system's "immune system" against hallucination by preventing
computations on impossible premises.

WHY THIS MATTERS:
----------------
The Phase 2 workforce is powerful but brittle. If a supervisor routes a
negative number to a Logarithm Specialist, the system will crash. If asked
to find the real square root of -4, the system will hallucinate. The
Precondition Validation Team intercepts these invalid inputs BEFORE they
reach the solvers, saving compute resources and preventing mathematically
invalid outputs.

AGENTS:
------
1. Domain Checker - Solvability gatekeeper (decidable vs undecidable)
2. Assumption Validator - Constraint compliance checker
3. Edge Case Detector - Red Team saboteur (singularities, boundaries)
4. Constraint Propagator - Hierarchical constraint injection

REFERENCE:
---------
- Phase_3_Build_Order_Breakdown.md: Step 1
- Phase_3_is_designated_as_the_Meta-Cognitive_Middleware_implementation.md
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import sympy as sp
from sympy import Symbol, sympify, oo, zoo, nan
import numpy as np

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase3.validation.precondition_validation')
except ImportError:
    logger = logging.getLogger(__name__)


# ===========================================================================
# VALIDATION STATUS AND ERROR TYPES
# ===========================================================================

class ValidationStatus(Enum):
    """Status codes for precondition validation results"""
    VALID = auto()
    DOMAIN_MISMATCH = auto()
    CONSTRAINT_VIOLATION = auto()
    SINGULARITY_DETECTED = auto()
    UNDECIDABLE_FRAGMENT = auto()
    EDGE_CASE_FAILURE = auto()


class MathematicalDomain(Enum):
    """
    Mathematical domains for solvability checking

    DECIDABLE DOMAINS (system can handle):
    - REAL_ARITHMETIC: Operations on real numbers
    - COMPLEX_ARITHMETIC: Operations including imaginary numbers
    - INTEGER_ARITHMETIC: Operations on integers
    - RATIONAL_ARITHMETIC: Operations on rationals
    - REAL_CLOSED_FIELDS: First-order theory of real numbers
    - PRESBURGER_ARITHMETIC: Integer arithmetic without multiplication

    UNDECIDABLE DOMAINS (require special handling):
    - DIOPHANTINE: Integer solutions to polynomial equations
    - PEANO_ARITHMETIC: Full number theory
    """
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
    """
    Result of precondition validation

    Contains the validation status, any error messages, detected violations,
    edge cases, and propagated constraints for downstream agents.
    """
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

    def __repr__(self) -> str:
        status_str = "VALID" if self.is_valid else f"INVALID ({self.status.name})"
        return f"ValidationResult({status_str})"


@dataclass
class MathematicalConstraint:
    """
    Represents a mathematical constraint on a variable

    Examples:
    - MathematicalConstraint('x', 'positive') for ln(x) requiring x > 0
    - MathematicalConstraint('n', 'integer') for discrete domains
    - MathematicalConstraint('x', 'nonzero') for division
    """
    variable: str
    constraint_type: str  # 'positive', 'negative', 'nonzero', 'integer', 'real', etc.
    expression: Optional[Any] = None
    source: str = "inferred"  # 'user_defined', 'inferred', 'propagated'
    timestamp: datetime = field(default_factory=datetime.now)

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
            'nonpositive': {'nonpositive': True, 'real': True},
        }
        return mapping.get(self.constraint_type, {})

    def __repr__(self) -> str:
        return f"Constraint({self.variable}: {self.constraint_type}, source={self.source})"


# ===========================================================================
# AGENT 1.1: THE DOMAIN CHECKER
# ===========================================================================

class DomainCheckerAgent:
    """
    Agent 1.1: The Domain Checker - Solvability Gatekeeper

    Audits problems against the capabilities of available solvers.
    Prevents wasted compute on undecidable or unsupported problem classes.

    WHAT IT DOES:
    - Classifies problems into mathematical domains
    - Checks if domain is decidable/solvable
    - Verifies solver availability for the domain
    - Halts execution with DOMAIN_MISMATCH if unsolvable

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 1.1
    """

    # Decidable fragments that the system can handle
    DECIDABLE_DOMAINS = {
        MathematicalDomain.REAL_ARITHMETIC,
        MathematicalDomain.COMPLEX_ARITHMETIC,
        MathematicalDomain.RATIONAL_ARITHMETIC,
        MathematicalDomain.REAL_CLOSED_FIELDS,
        MathematicalDomain.PRESBURGER_ARITHMETIC,
        MathematicalDomain.INTEGER_ARITHMETIC,
    }

    # Undecidable domains requiring special handling
    UNDECIDABLE_DOMAINS = {
        MathematicalDomain.DIOPHANTINE,
        MathematicalDomain.PEANO_ARITHMETIC,
    }

    def __init__(self, available_solvers: Dict[str, Set[MathematicalDomain]] = None):
        """
        Initialize with registry of available solvers and their capabilities.

        Args:
            available_solvers: Maps solver_id to set of supported domains.
                             If None, default solver set is used.
        """
        self.available_solvers = available_solvers or self._default_solvers()
        self.solver_capabilities = self._compute_aggregate_capabilities()
        print("    [OK] Domain Checker Agent initialized")

    def _default_solvers(self) -> Dict[str, Set[MathematicalDomain]]:
        """Default solver capabilities from Phase 2"""
        return {
            'arithmetic_specialist': {
                MathematicalDomain.REAL_ARITHMETIC,
                MathematicalDomain.COMPLEX_ARITHMETIC,
                MathematicalDomain.INTEGER_ARITHMETIC,
                MathematicalDomain.RATIONAL_ARITHMETIC,
            },
            'polynomial_specialist': {
                MathematicalDomain.REAL_ARITHMETIC,
                MathematicalDomain.COMPLEX_ARITHMETIC,
            },
            'calculus_specialist': {
                MathematicalDomain.REAL_ARITHMETIC,
                MathematicalDomain.COMPLEX_ARITHMETIC,
            },
            'linalg_specialist': {
                MathematicalDomain.REAL_ARITHMETIC,
                MathematicalDomain.COMPLEX_ARITHMETIC,
            },
            'numerical_utility': {
                MathematicalDomain.REAL_ARITHMETIC,
            }
        }

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
        expr = self._get_expression(omdoc_object)

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

    def _get_expression(self, omdoc_object) -> Any:
        """Extract expression from various OMDoc structures"""
        if hasattr(omdoc_object, 'expression_tree'):
            return omdoc_object.expression_tree
        elif hasattr(omdoc_object, 'expression'):
            return omdoc_object.expression
        elif hasattr(omdoc_object, 'content'):
            return omdoc_object.content
        return omdoc_object

    def _is_diophantine(self, expr, omdoc_object) -> bool:
        """Detect Diophantine equation patterns"""
        # Check if problem explicitly requires integer solutions
        metadata = getattr(omdoc_object, 'metadata', {})
        if isinstance(metadata, dict):
            if metadata.get('solution_domain') == 'integers':
                return True
            # Check for polynomial equations with integer coefficient constraints
            if metadata.get('require_integer_solutions', False):
                return True
        return False

    def _requires_integer_domain(self, omdoc_object) -> bool:
        """Check if problem requires integer arithmetic"""
        metadata = getattr(omdoc_object, 'metadata', {})
        if isinstance(metadata, dict):
            constraints = metadata.get('constraints', [])
            for c in constraints:
                if isinstance(c, MathematicalConstraint) and c.constraint_type == 'integer':
                    return True
        return False

    def _requires_complex_domain(self, expr) -> bool:
        """Check if expression requires complex numbers"""
        try:
            sympy_expr = sympify(expr) if isinstance(expr, str) else expr
            # Check for imaginary unit or complex exponentials
            return sympy_expr.has(sp.I)
        except (sp.SympifyError, TypeError, AttributeError) as e:
            logger.debug(f"Could not check complex domain requirement: {e}")
            return False

    def check_solvability(self, omdoc_object) -> ValidationResult:
        """
        Main validation method: Check if problem is solvable by available solvers.

        Returns:
            ValidationResult with VALID or DOMAIN_MISMATCH/UNDECIDABLE status
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
            available = [d.value for d in self.solver_capabilities]
            return ValidationResult(
                status=ValidationStatus.DOMAIN_MISMATCH,
                is_valid=False,
                error_message=f"No solver available for domain: {domain.value}. "
                              f"Available domains: {available}",
                domain_classification=domain
            )

        return ValidationResult(
            status=ValidationStatus.VALID,
            is_valid=True,
            domain_classification=domain
        )


# ===========================================================================
# AGENT 1.2: THE ASSUMPTION VALIDATOR
# ===========================================================================

class AssumptionValidatorAgent:
    """
    Agent 1.2: The Assumption Validator - Constraint Compliance Checker

    Scans OMDoc structure for variable definitions and constraints.
    Enforces mathematical legality before solvers engage.

    WHAT IT DOES:
    - Extracts implicit constraints from functions (ln(x) -> x > 0)
    - Validates constraints against known variable values
    - Detects conflicts between constraints and values
    - Triggers CONSTRAINT_VIOLATION on conflicts

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 1.2
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
        print("    [OK] Assumption Validator Agent initialized")

    def extract_implicit_constraints(self, expr) -> List[MathematicalConstraint]:
        """
        Extract constraints implied by functions in the expression.

        For example:
        - ln(x) implies x > 0
        - sqrt(x) implies x >= 0
        - 1/x implies x != 0
        """
        constraints = []

        try:
            sympy_expr = sympify(expr) if isinstance(expr, str) else expr
        except (sp.SympifyError, TypeError, ValueError) as e:
            logger.debug(f"Could not parse expression for constraint extraction: {e}")
            return constraints

        # Check for logarithmic functions
        if sympy_expr.has(sp.log):
            for arg in sympy_expr.atoms(sp.log):
                var = self._extract_primary_variable(arg.args[0])
                if var:
                    constraints.append(MathematicalConstraint(
                        variable=str(var),
                        constraint_type='positive',
                        expression=arg.args[0] > 0,
                        source='inferred'
                    ))

        # Check for square roots (sqrt(x) is internally Pow(x, 1/2))
        # Note: sp.sqrt(x) returns Pow(x, 1/2), and .has(sp.sqrt) returns False
        for arg in sympy_expr.atoms(sp.Pow):
            # Check for half exponent (sqrt representation)
            try:
                exp = arg.exp
                is_sqrt = (exp == sp.S.Half or
                          exp == sp.Rational(1, 2) or
                          (hasattr(exp, 'is_Rational') and exp.is_Rational and
                           exp.p == 1 and exp.q == 2))
                if is_sqrt:
                    var = self._extract_primary_variable(arg.base)
                    if var:
                        constraints.append(MathematicalConstraint(
                            variable=str(var),
                            constraint_type='nonnegative',
                            expression=arg.base >= 0,
                            source='inferred'
                        ))
            except (AttributeError, TypeError) as e:
                logger.debug(f"Could not check sqrt constraint for {arg}: {e}")

        # Check for division (nonzero denominators)
        for atom in sympy_expr.atoms(sp.Pow):
            if atom.exp.is_negative:
                var = self._extract_primary_variable(atom.base)
                if var:
                    constraints.append(MathematicalConstraint(
                        variable=str(var),
                        constraint_type='nonzero',
                        expression=sp.Ne(atom.base, 0),
                        source='inferred'
                    ))

        # Check for asin, acos (bounded arguments)
        for func in [sp.asin, sp.acos]:
            if sympy_expr.has(func):
                for arg in sympy_expr.atoms(func):
                    var = self._extract_primary_variable(arg.args[0])
                    if var:
                        constraints.append(MathematicalConstraint(
                            variable=str(var),
                            constraint_type='bounded_neg1_pos1',
                            expression=sp.And(arg.args[0] >= -1, arg.args[0] <= 1),
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
        - Prior step results / known variable values
        """
        violations = []
        expr = self._get_expression(omdoc_object)

        # Extract implicit constraints
        implicit = self.extract_implicit_constraints(expr)

        # Combine with user-defined
        all_constraints = implicit + (user_defined_constraints or [])

        # Get variable values from metadata/prior steps
        metadata = getattr(omdoc_object, 'metadata', {})
        known_values = metadata.get('variable_values', {}) if isinstance(metadata, dict) else {}

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

    def _get_expression(self, omdoc_object) -> Any:
        """Extract expression from OMDoc object"""
        if hasattr(omdoc_object, 'expression_tree'):
            return omdoc_object.expression_tree
        elif hasattr(omdoc_object, 'expression'):
            return omdoc_object.expression
        elif hasattr(omdoc_object, 'content'):
            return omdoc_object.content
        return omdoc_object

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
            elif constraint.constraint_type == 'nonpositive':
                return float(value) <= 0
            elif constraint.constraint_type == 'integer':
                return float(value) == int(value)
            elif constraint.constraint_type == 'real':
                return not isinstance(value, complex)
            elif constraint.constraint_type == 'bounded_neg1_pos1':
                return -1 <= float(value) <= 1
        except (ValueError, TypeError) as e:
            logger.debug(f"Could not evaluate constraint {constraint.constraint_type} for value {value}: {e}")
            return True  # Can't evaluate, assume valid
        return True


# ===========================================================================
# AGENT 1.3: THE EDGE CASE DETECTOR (RED TEAM)
# ===========================================================================

class EdgeCaseDetectorAgent:
    """
    Agent 1.3: The Edge Case Detector - Red Team Saboteur

    Proactively hunts for singularities and boundary failures.
    Asks "What if?" to catch problems before they cause crashes.

    WHAT IT DOES:
    - Finds zeros in denominators (division by zero)
    - Detects undefined points in expressions
    - Checks matrix singularity before inversions
    - Identifies boundary failures at critical values

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 1.3
    """

    def __init__(self):
        self.critical_values = [0, 1, -1]
        print("    [OK] Edge Case Detector Agent initialized")

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
        except (sp.SympifyError, TypeError, AttributeError) as e:
            logger.debug(f"Could not parse expression for singularity detection: {e}")
            return edge_cases

        for var in variables:
            # Check for division by zero
            zeros = self._find_zeros_in_denominator(sympy_expr, var)
            for zero_point in zeros:
                edge_cases.append(
                    f"SINGULARITY: Division by zero when {var}={zero_point}"
                )

            # Check behavior at critical points
            for critical in self.critical_values:
                try:
                    result = sympy_expr.subs(var, critical)
                    if result in [oo, -oo, zoo, nan] or result.is_infinite or result.is_nan:
                        edge_cases.append(
                            f"BOUNDARY_FAILURE: Expression undefined at {var}={critical}"
                        )
                except (TypeError, AttributeError, ValueError) as e:
                    logger.debug(f"Could not evaluate at critical point {var}={critical}: {e}")

        return edge_cases

    def _find_zeros_in_denominator(self, expr, var) -> List[Any]:
        """Find values that make denominators zero"""
        zeros = []

        try:
            # Get the denominator
            numer, denom = expr.as_numer_denom()
            if denom != 1:
                solutions = sp.solve(denom, var)
                zeros.extend(solutions)
        except (TypeError, AttributeError, NotImplementedError) as e:
            logger.debug(f"Could not find denominator zeros for {var}: {e}")

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
        except np.linalg.LinAlgError as e:
            return True, f"Matrix singularity check failed (LinAlgError): {str(e)}"
        except (sp.SympifyError, ValueError, TypeError, NotImplementedError) as e:
            return True, f"Matrix singularity check failed: {str(e)}"

    def validate(self, omdoc_object, operation_type: str = None) -> ValidationResult:
        """
        Main validation method for edge case detection.
        """
        edge_cases = []

        expr = self._get_expression(omdoc_object)
        edge_cases.extend(self.detect_singularities(expr))

        # Check for matrix operations
        if operation_type == 'matrix_inversion':
            metadata = getattr(omdoc_object, 'metadata', {})
            matrix_data = metadata.get('matrix') if isinstance(metadata, dict) else None
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

    def _get_expression(self, omdoc_object) -> Any:
        """Extract expression from OMDoc object"""
        if hasattr(omdoc_object, 'expression_tree'):
            return omdoc_object.expression_tree
        elif hasattr(omdoc_object, 'expression'):
            return omdoc_object.expression
        elif hasattr(omdoc_object, 'content'):
            return omdoc_object.content
        return omdoc_object


# ===========================================================================
# AGENT 1.4: THE CONSTRAINT PROPAGATOR
# ===========================================================================

class ConstraintPropagatorAgent:
    """
    Agent 1.4: The Constraint Propagator - Hierarchical Constraint Injection

    Ensures that validated constraints are passed down to all downstream agents.
    Maintains the "laws of physics" across the entire agent hierarchy.

    WHAT IT DOES:
    - Registers constraints per conversation session
    - Propagates constraints to sub-tasks
    - Injects constraints into OMDoc metadata
    - Posts constraint updates to Blackboard

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 1.4
    """

    def __init__(self, blackboard):
        """
        Initialize with reference to the shared Blackboard.

        Args:
            blackboard: The Phase 0 Blackboard for constraint broadcasting
        """
        self.blackboard = blackboard
        self.active_constraints: Dict[str, Dict[str, MathematicalConstraint]] = {}
        print("    [OK] Constraint Propagator Agent initialized")

    def register_constraint(self, conversation_id: str,
                          constraint: MathematicalConstraint) -> None:
        """
        Register a validated constraint for a problem-solving session.
        """
        if conversation_id not in self.active_constraints:
            self.active_constraints[conversation_id] = {}

        self.active_constraints[conversation_id][constraint.variable] = constraint

        # Post to Blackboard for subscriber notification
        if self.blackboard:
            try:
                self.blackboard.post({
                    'entry_type': 'constraint_propagation',
                    'conversation_id': conversation_id,
                    'constraint': constraint,
                    'tags': ['constraint_update', constraint.variable]
                })
            except (TypeError, AttributeError, ValueError) as e:
                logger.debug(f"Could not post constraint to blackboard: {e}")

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
        variables = self._extract_variables(omdoc_object)
        relevant_constraints = self.get_constraints_for_subtask(
            conversation_id, variables
        )

        # Update OMDoc metadata
        if not hasattr(omdoc_object, 'metadata'):
            omdoc_object.metadata = {}

        if 'propagated_constraints' not in omdoc_object.metadata:
            omdoc_object.metadata['propagated_constraints'] = {}

        omdoc_object.metadata['propagated_constraints'].update(relevant_constraints)

        return omdoc_object

    def _extract_variables(self, omdoc_object) -> Set[str]:
        """Extract variable names from expression"""
        try:
            expr = self._get_expression(omdoc_object)
            sympy_expr = sympify(expr) if isinstance(expr, str) else expr
            return {str(s) for s in sympy_expr.free_symbols}
        except (sp.SympifyError, TypeError, AttributeError) as e:
            logger.debug(f"Could not extract variables from expression: {e}")
            return set()

    def _get_expression(self, omdoc_object) -> Any:
        """Extract expression from OMDoc object"""
        if hasattr(omdoc_object, 'expression_tree'):
            return omdoc_object.expression_tree
        elif hasattr(omdoc_object, 'expression'):
            return omdoc_object.expression
        return omdoc_object

    def clear_session(self, conversation_id: str) -> None:
        """Clear constraints for a completed session"""
        if conversation_id in self.active_constraints:
            del self.active_constraints[conversation_id]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'active_sessions': len(self.active_constraints),
            'total_constraints': sum(
                len(c) for c in self.active_constraints.values()
            )
        }


# ===========================================================================
# PRECONDITION VALIDATION TEAM COORDINATOR
# ===========================================================================

class PreconditionValidationTeam:
    """
    Coordinator for the Precondition Validation Team.

    Orchestrates the four agents in sequence to produce a comprehensive
    validation result before any solver engages.

    VALIDATION PIPELINE:
    1. Domain Check - Is the problem solvable at all?
    2. Assumption Validation - Are all constraints satisfied?
    3. Edge Case Detection - Are there hidden singularities?
    4. Constraint Propagation - Pass constraints downstream

    Only returns STATUS: VALID if ALL checks pass.

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Team Coordinator
    """

    def __init__(self, available_solvers: Dict[str, Set[MathematicalDomain]] = None,
                 blackboard = None):
        """
        Initialize the Precondition Validation Team.

        Args:
            available_solvers: Solver capabilities registry
            blackboard: Phase 0 Blackboard for constraint broadcasting
        """
        print("  [PRECONDITION VALIDATION TEAM - The Anesthesiologist]")
        self.domain_checker = DomainCheckerAgent(available_solvers)
        self.assumption_validator = AssumptionValidatorAgent()
        self.edge_case_detector = EdgeCaseDetectorAgent()
        self.constraint_propagator = ConstraintPropagatorAgent(blackboard)
        self.validation_count = 0
        self.rejection_count = 0
        print("    [OK] Precondition Validation Team assembled")

    def validate(self, omdoc_object, conversation_id: str,
                operation_type: str = None,
                user_constraints: List[MathematicalConstraint] = None
                ) -> ValidationResult:
        """
        Execute the full validation pipeline.

        Returns STATUS: VALID only if ALL checks pass.
        """
        self.validation_count += 1

        # Step 1: Domain Check
        domain_result = self.domain_checker.check_solvability(omdoc_object)
        if not domain_result.is_valid:
            self.rejection_count += 1
            return domain_result

        # Step 2: Assumption Validation
        assumption_result = self.assumption_validator.validate_constraints(
            omdoc_object, user_constraints
        )
        if not assumption_result.is_valid:
            self.rejection_count += 1
            return assumption_result

        # Step 3: Edge Case Detection
        edge_result = self.edge_case_detector.validate(omdoc_object, operation_type)
        if not edge_result.is_valid:
            self.rejection_count += 1
            return edge_result

        # Step 4: Propagate validated constraints
        for var, constraint in assumption_result.propagated_constraints.items():
            if isinstance(constraint, MathematicalConstraint):
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

    def clear_session(self, conversation_id: str) -> None:
        """Clear session data after problem completion"""
        self.constraint_propagator.clear_session(conversation_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get team statistics"""
        return {
            'validations_performed': self.validation_count,
            'rejections': self.rejection_count,
            'approval_rate': (self.validation_count - self.rejection_count) / max(1, self.validation_count) * 100,
            'constraint_propagator': self.constraint_propagator.get_statistics()
        }
