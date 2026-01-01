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
PHASE 1 - STEP 1: THE GATEKEEPERS (Problem Analysis Team)
=========================================================

The Problem Analysis Team sanitizes chaotic natural language and LaTeX inputs
into structured, unambiguous mathematical objects before the Orchestrator sees them.

COMPONENTS:
----------
1. SyntaxParserAgent: Translates natural language/LaTeX to OMDoc
2. StructureRecognizerAgent: Classifies problem types

REFERENCE:
---------
- Phase_1_Build_Order_Breakdown.md: Lines 45-106 (STEP 1)
- Phase 1 Coding Strategy: Section 3.1 "The Gatekeepers"
"""

import sys
import os
import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Dict, List
from datetime import datetime

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    parse_expr as native_parse_expr, Symbol, Expr, Integer, Float, Rational,
    Add, Mul, Pow, Sin, Cos, Tan, Exp, Log, Sqrt, symbols, simplify
)

from symbo_agentic_reasoners.core.safe_parser import safe_parse, validate_input, SecurityError
from symbo_agentic_reasoners.core.input_normalizer import (
    normalize_input, validate_normalized, normalize_and_extract_command
)

logger = logging.getLogger('symbo_agentic_reasoners.phase1.problem_analysis')

# Add parent to path for Phase 0 imports
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.core.omdoc_schema import (
    create_variable, create_number, create_operation,
    OMObject, MathOperator
)
from symbo_agentic_reasoners.protocols.fipa_acl import create_inform
from symbo_agentic_reasoners.agents.base.notation_translator import (
    NotationTranslatorAgent, NotationFormat
)


class ProblemType(Enum):
    """
    Classification of mathematical problem types

    COMPUTATION: Calculate or simplify something
    PROOF: Prove a theorem or statement
    OPTIMIZATION: Find maximum/minimum
    """
    COMPUTATION = 'computation'
    PROOF = 'proof'
    OPTIMIZATION = 'optimization'
    UNKNOWN = 'unknown'


class MathDomain(Enum):
    """
    Mathematical domain classification
    """
    CALCULUS = 'Calculus'
    ALGEBRA = 'Algebra'
    LINEAR_ALGEBRA = 'LinearAlgebra'
    GEOMETRY = 'Geometry'
    LOGIC = 'Logic'
    NUMBER_THEORY = 'NumberTheory'
    STATISTICS = 'Statistics'
    DISCRETE_MATH = 'DiscreteMath'
    # Physics domains
    PHYSICS_MECHANICS = 'PhysicsMechanics'
    PHYSICS_EM = 'PhysicsEM'
    PHYSICS_THERMO = 'PhysicsThermo'
    PHYSICS_QUANTUM = 'PhysicsQuantum'
    UNKNOWN = 'Unknown'


@dataclass
class StructuredProblem:
    """
    Structured mathematical problem in OMDoc format

    This is the output of the Problem Analysis Team - a fully sanitized,
    classified mathematical object ready for the Orchestrator.

    FIELDS:
    ------
    - raw_input: Original natural language input
    - omdoc_content: Parsed OMDoc/OpenMath expression tree
    - problem_type: Classification (COMPUTATION, PROOF, OPTIMIZATION)
    - domain: Mathematical domain (CALCULUS, ALGEBRA, etc.)
    - sympy_expr: Parsed SymPy expression (if applicable)
    - metadata: Additional classification metadata

    REFERENCE:
    ---------
    Phase_1_Build_Order_Breakdown.md: Lines 73-79 (OMDocObject definition)
    """
    raw_input: str
    omdoc_content: OMObject
    problem_type: ProblemType
    domain: MathDomain
    sympy_expr: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        return (f"StructuredProblem(type={self.problem_type.value}, "
                f"domain={self.domain.value}, input='{self.raw_input[:50]}...')")


class SyntaxParserAgent(BDIAgent):
    """
    Agent 1.1: Syntax Parser & Autoformalizer

    DIRECTIVE:
    ---------
    Translate natural language and LaTeX into structured OMDoc/OpenMath
    expression trees. Functions as the system's "transducer."

    ARCHITECTURE:
    ------------
    - Receives raw text input
    - Parses into SymPy expression
    - Converts to OMDoc/OpenMath semantic object
    - Passes to Structure Recognizer

    CRITICAL:
    --------
    This agent ensures downstream agents receive semantic objects,
    not ambiguous text strings.

    REFERENCE:
    ---------
    - Phase_1_Build_Order_Breakdown.md: Lines 52-60 (Agent 1.1 specification)
    - Phase 1 Coding Strategy: "The Syntax Parser converts 'integral of x'
      into OpenMath object ensuring downstream agents receive semantic objects"
    """

    def __init__(self, agent_id: str = 'syntax_parser_001'):
        """Initialize Syntax Parser Agent"""
        super().__init__(agent_id)

        # Notation translator for standardizing input formats
        self.notation_translator = NotationTranslatorAgent(f"{agent_id}_translator")

        # Parsing patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for mathematical operations"""
        self.patterns = {
            # ODE patterns - MUST come before other patterns to match first
            'ode_first_order': re.compile(
                r'd([a-zA-Z])/d([a-zA-Z])\s*(.+)',
                re.IGNORECASE
            ),
            'ode_second_order': re.compile(
                r'd2([a-zA-Z])/d([a-zA-Z])2\s*(.+)',
                re.IGNORECASE
            ),
            'ode_higher_order': re.compile(
                r'd(\d+)([a-zA-Z])/d([a-zA-Z])\^?(\d+)\s*(.+)',
                re.IGNORECASE
            ),
            'derivative': re.compile(
                r'(derivative|differentiate|diff|d/dx)\s+(?:of\s+)?(.*?)(?:\s+with respect to\s+(\w+))?$',
                re.IGNORECASE
            ),
            'integral': re.compile(
                r'(integral|integrate)\s+(?:of\s+)?(.*?)(?:\s+with respect to\s+(\w+))?$',
                re.IGNORECASE
            ),
            'limit': re.compile(
                r'limit\s+(?:of\s+)?(.*?)\s+as\s+(\w+)\s+(?:approaches|->|→)\s+(.*?)$',
                re.IGNORECASE
            ),
            # LaTeX-style limit: lim_{x→∞} f(x), lim_{x->0} f(x), lim_{n→∞} a_n
            'limit_latex': re.compile(
                r'lim_?\{\s*(\w+)\s*(?:->|→|\\to)\s*([^}]+)\}\s*(.+)$',
                re.IGNORECASE
            ),
            'solve': re.compile(
                r'(solve)\s+(.+?)(?:\s+for\s+(\w+))?$',
                re.IGNORECASE
            ),
            'simplify': re.compile(
                r'(simplify)\s+(.+)$',
                re.IGNORECASE
            ),
            'factor': re.compile(
                r'(factor(?:ize)?)\s+(.+)$',
                re.IGNORECASE
            ),
            'expand': re.compile(
                r'(expand)\s+(.+)$',
                re.IGNORECASE
            ),
            'dsolve': re.compile(
                r'(dsolve)\s*\((.+)\)',
                re.IGNORECASE
            ),
            'series': re.compile(
                r'(series|taylor|maclaurin)\s+(?:of\s+)?(.+?)(?:\s+(?:around|at|about)\s+(.+))?$',
                re.IGNORECASE
            )
        }

    def parse(self, raw_input: str) -> StructuredProblem:
        """
        Parse natural language/LaTeX into structured OMDoc object

        Args:
            raw_input: Raw natural language or LaTeX string

        Returns:
            StructuredProblem with OMDoc expression tree

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 83-90 (parse method implementation)
        """
        # Extract operation from RAW input first (before cleaning removes equation signs)
        operation, expression, variable, extra_meta = self._extract_operation(raw_input)

        # Clean and normalize the expression for parsing
        cleaned = self._clean_input(expression)

        # Parse expression to SymPy
        try:
            sympy_expr = self._parse_to_sympy(cleaned, variable)
        except (ValueError, SyntaxError, TypeError) as e:
            # If parsing fails, create a text placeholder
            sympy_expr = None
            logger.debug(f"Could not parse '{expression}': {type(e).__name__}: {e}")

        # Convert to OMDoc
        omdoc_content = self._sympy_to_omdoc(sympy_expr, operation, variable)

        # Build metadata dict with operation info and any extras (bounds, etc.)
        metadata = {
            'operation': operation,
            'variable': variable,
            'expression': expression  # Store expression string for native engine fallback
        }
        metadata.update(extra_meta)  # Add bounds for definite integrals, etc.

        # Create structured problem (classification added by Structure Recognizer)
        structured = StructuredProblem(
            raw_input=raw_input,
            omdoc_content=omdoc_content,
            problem_type=ProblemType.UNKNOWN,  # Set by StructureRecognizer
            domain=MathDomain.UNKNOWN,  # Set by StructureRecognizer
            sympy_expr=sympy_expr,
            metadata=metadata
        )

        return structured

    def _clean_input(self, raw: str) -> str:
        """
        Clean and normalize input text.

        Uses the centralized InputNormalizer for Unicode/format conversion,
        then applies notation translation for LaTeX/natural language.
        """
        # Step 1: Use centralized normalizer for Unicode, whitespace, etc.
        # Don't add implicit multiplication here - let notation translator handle it
        cleaned = normalize_input(raw, add_multiplication=False, close_parens=False)

        # Step 2: Use notation translator to detect and standardize input format
        detected_format = self.notation_translator.detect_format(cleaned)

        # If not already SymPy format, try to translate
        if detected_format != NotationFormat.SYMPY:
            result = self.notation_translator.translate(
                cleaned, detected_format, NotationFormat.SYMPY
            )
            if result.success and result.translated_text:
                cleaned = result.translated_text

        # Step 3: Final cleanup - ensure ^ is ** after translator
        cleaned = cleaned.replace('^', '**')

        # Step 4: Handle equation format "expr = 0" -> "expr"
        # This allows "solve x^2 - 9 = 0" to parse correctly
        if '=' in cleaned:
            parts = cleaned.split('=')
            if len(parts) == 2:
                rhs = parts[1].strip()
                # If right side is 0 or just whitespace, use left side
                if rhs in ('0', '0.0', ''):
                    cleaned = cleaned[:cleaned.index('=')].strip()

        return cleaned

    def _extract_operation(self, text: str) -> tuple:
        """
        Extract operation type and mathematical expression

        Handles BOTH:
        - Function-call syntax: solve(x**2-4, x), diff(x**3, x), etc.
        - Natural language: "solve x^2 - 4 for x", "differentiate x**3", etc.

        Returns:
            (operation, expression, variable, extra_meta) tuple
            extra_meta is a dict with additional info like bounds for definite integrals
        """
        # FIRST: Check for SymPy function-call syntax (solve(expr, x), diff(expr, x), etc.)
        # This handles the "solve() wrapper breaking routing" issue from Second Opinion
        normalized, cmd_meta = normalize_and_extract_command(text)
        if cmd_meta:
            command = cmd_meta.get('command', 'compute')
            # Map command names to operation names
            op_map = {
                'solve': 'solve',
                'solve_system': 'solve_system',  # System of equations
                'differentiate': 'derivative',
                'integrate': 'integral',
                'integrate_2d': 'integral_2d',  # Double integral: integrate(f, (x,a,b), (y,c,d))
                'factor': 'factor',
                'expand': 'expand',
                'simplify': 'simplify',
                'limit': 'limit',
                'grad': 'gradient',     # gradient returns full vector [df/dx, df/dy, df/dz]
                'gradient': 'gradient',
                'div': 'divergence',   # divergence returns scalar sum
                'divergence': 'divergence',
                'curl': 'curl',        # curl returns full vector
                'complex_modulus': 'complex_modulus',  # abs(complex)
                'complex_argument': 'complex_argument',  # arg(complex)
                'complex_simplify': 'complex_simplify',  # simplify complex expressions
                'summation': 'summation',  # infinite series: summation(1/n**2, (n, 1, oo))
                'product': 'product',      # infinite product: product(expr, (n, 1, oo))
                'diophantine': 'diophantine',  # diophantine equation solving
                'det': 'determinant',      # matrix determinant
            }
            operation = op_map.get(command, command)
            expression = cmd_meta.get('expression', cmd_meta.get('equation', normalized))
            variable = cmd_meta.get('variable', 'x')
            # Extract extra metadata (bounds for definite integrals, series bounds, etc.)
            extra_meta = {}
            if cmd_meta.get('is_definite'):
                extra_meta['is_definite'] = True
                extra_meta['lower_bound'] = cmd_meta.get('lower_bound')
                extra_meta['upper_bound'] = cmd_meta.get('upper_bound')
            # 2D integral metadata
            if cmd_meta.get('is_2d'):
                extra_meta['is_2d'] = True
                extra_meta['variable2'] = cmd_meta.get('variable2')
                extra_meta['lower_bound2'] = cmd_meta.get('lower_bound2')
                extra_meta['upper_bound2'] = cmd_meta.get('upper_bound2')
            # Series/summation metadata
            if cmd_meta.get('start') is not None:
                extra_meta['start'] = cmd_meta.get('start')
                extra_meta['end'] = cmd_meta.get('end')
            # Limit metadata (point and direction)
            if cmd_meta.get('point') is not None:
                extra_meta['point'] = cmd_meta.get('point')
                extra_meta['direction'] = cmd_meta.get('direction', '+-')
            logger.debug(f"[CMD UNWRAP] {text} -> op={operation}, expr={expression}, var={variable}, extra={extra_meta}")
            return operation, expression, variable, extra_meta

        # SECOND: Try natural language patterns
        for op_name, pattern in self.patterns.items():
            match = pattern.search(text)
            if match:
                groups = match.groups()

                # Special handling for ODE patterns
                if op_name == 'ode_first_order':
                    # groups = (dependent_var, independent_var, rest_of_equation)
                    # Example: "dy/dx + y = 0" -> ('y', 'x', '+ y = 0')
                    dependent_var = groups[0]
                    independent_var = groups[1]
                    # Return full text as expression for ODE solver
                    return 'ode', text, independent_var, {'dependent_var': dependent_var, 'order': 1}

                elif op_name == 'ode_second_order':
                    # groups = (dependent_var, independent_var, rest_of_equation)
                    # Example: "d2y/dx2 + 4y' + 4y = 0" -> ('y', 'x', '+ 4y' + 4y = 0')
                    dependent_var = groups[0]
                    independent_var = groups[1]
                    return 'ode', text, independent_var, {'dependent_var': dependent_var, 'order': 2}

                elif op_name == 'ode_higher_order':
                    # groups = (order_num, dependent_var, independent_var, order_num2, rest)
                    order = int(groups[0])
                    dependent_var = groups[1]
                    independent_var = groups[2]
                    return 'ode', text, independent_var, {'dependent_var': dependent_var, 'order': order}

                # Special handling for limit_latex: groups = (variable, point, expression)
                elif op_name == 'limit_latex':
                    operation = 'limit'
                    variable = groups[0]
                    point = groups[1].strip()
                    expression = groups[2].strip() if len(groups) > 2 else text
                    return operation, expression, variable, {'point': point}

                # Default handling for other patterns
                operation = op_name
                expression = groups[1] if len(groups) > 1 else text
                variable = groups[2] if len(groups) > 2 else 'x'
                return operation, expression.strip(), variable, {}

        # Check if this is an equation (contains = sign) - should be solved
        if '=' in text:
            parts = text.split('=', 1)  # Split only on first =
            if len(parts) == 2:
                lhs = parts[0].strip()
                rhs = parts[1].strip()

                # Check for ASSIGNMENT syntax: identifier = expression
                # Assignment LHS is a simple identifier (e.g., "basel", "zeta4", "my_var")
                # NOT an expression like "x^2" or "2*x + 1"
                import re
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', lhs):
                    # This is an assignment like "basel = summation(...)
                    # Process the RHS as the expression to evaluate
                    # Recursively extract operation from RHS
                    rhs_op, rhs_expr, rhs_var, rhs_extra = self._extract_operation(rhs)
                    # Return with assignment metadata
                    rhs_extra['assignment_target'] = lhs
                    return rhs_op, rhs_expr, rhs_var, rhs_extra

                # Equation like "x^2 + 2x - 3 = 0" or "x^2 = 4"
                # Extract expression for solving
                if rhs in ('0', '0.0', ''):
                    return 'solve', lhs, 'x', {}
                else:
                    # Equation like "x^2 = 4" -> solve x^2 - 4 = 0
                    return 'solve', f"({lhs}) - ({rhs})", 'x', {}

        # No pattern matched - assume direct expression computation
        return 'compute', text, 'x', {}

    def _parse_to_sympy(self, expression: str, variable: str = 'x') -> Any:
        """
        Parse expression string to native symbolic object

        Args:
            expression: Mathematical expression string
            variable: Primary variable name

        Returns:
            Native symbolic expression object (Expr)

        Note: Uses native_symbolic module - NO SYMPY
        """
        try:
            # Validate input security first
            validate_input(expression)

            # Try safe parser first (wrapper around native)
            try:
                expr = safe_parse(expression)
                return expr
            except Exception:
                pass

            # Fallback to native parser
            expr = native_parse_expr(expression)
            return expr
        except SecurityError as e:
            logger.warning(f"Security violation in expression: {expression[:50]} - {e}")
            raise ValueError(f"Invalid expression (security): {e}") from e
        except (SyntaxError, TypeError, AttributeError, ValueError) as e:
            # Final fallback - try native parser directly
            try:
                expr = native_parse_expr(expression)
                return expr
            except Exception as e2:
                logger.debug(f"Expression parse failed: {expression} - {type(e2).__name__}: {e2}")
                raise ValueError(f"Could not parse expression: {expression}") from e

    def _sympy_to_omdoc(self, sympy_expr: Any, operation: str, variable: str) -> OMObject:
        """
        Convert SymPy expression to OMDoc/OpenMath object

        Args:
            sympy_expr: SymPy expression
            operation: Operation type (derivative, integral, etc.)
            variable: Variable name

        Returns:
            OMDoc expression tree

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 54-55
        "Converts 'integral of x' into OpenMath object ensuring
        downstream agents receive semantic objects"
        """
        if sympy_expr is None:
            # Fallback: create simple variable
            return create_variable('unknown')

        # Convert SymPy to OMDoc based on operation
        if operation == 'derivative':
            # Create derivative application
            # <OMA><OMS cd="calculus1" name="diff"/>
            #      <OMV name="x"/>
            #      <expression>
            # </OMA>
            expr_omdoc = self._sympy_expr_to_omdoc(sympy_expr)
            var_omdoc = create_variable(variable)

            omdoc = create_operation(
                MathOperator.DIFF,
                expr_omdoc,
                var_omdoc
            )
            return omdoc

        elif operation == 'integral':
            # Create integral application
            expr_omdoc = self._sympy_expr_to_omdoc(sympy_expr)
            var_omdoc = create_variable(variable)

            omdoc = create_operation(
                MathOperator.INT,
                expr_omdoc,
                var_omdoc
            )
            return omdoc

        else:
            # Default: just convert expression
            return self._sympy_expr_to_omdoc(sympy_expr)

    def _sympy_expr_to_omdoc(self, expr: Any) -> OMObject:
        """
        Recursively convert native symbolic expression to OMDoc

        Uses native symbolic types - NO SYMPY.

        This is a simplified converter - full implementation would
        handle all expression types.
        """
        if expr is None:
            return create_variable('none')

        # Convert based on native symbolic expression type
        # Import locally to avoid circular imports
        from symbo_agentic_reasoners.core.native_symbolic import (
            Symbol as NativeSymbol, Add as NativeAdd, Mul as NativeMul,
            Pow as NativePow, Integer as NativeInteger, Float as NativeFloat,
            Rational as NativeRational, Expr as NativeExpr
        )

        if isinstance(expr, NativeSymbol):
            return create_variable(str(expr))

        elif isinstance(expr, (NativeInteger, int)):
            return create_variable(str(expr))

        elif isinstance(expr, (NativeFloat, float, NativeRational)):
            return create_variable(str(expr))

        elif isinstance(expr, NativeAdd):
            # Addition: (+ arg1 arg2 ...)
            args = [self._sympy_expr_to_omdoc(arg) for arg in expr.args]
            return create_operation(MathOperator.PLUS, *args)

        elif isinstance(expr, NativeMul):
            # Multiplication: (* arg1 arg2 ...)
            args = [self._sympy_expr_to_omdoc(arg) for arg in expr.args]
            return create_operation(MathOperator.TIMES, *args)

        elif isinstance(expr, NativePow):
            # Power: (^ base exponent)
            base = self._sympy_expr_to_omdoc(expr.base)
            exp = self._sympy_expr_to_omdoc(expr.exp)
            return create_operation(MathOperator.POWER, base, exp)

        else:
            # Fallback: string representation
            return create_variable(str(expr))

    # BDI Implementation (simplified - not using full BDI loop in Phase 1)
    def update_beliefs(self):
        """Update beliefs from environment"""
        pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions"""
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step"""
        pass


class StructureRecognizerAgent(BDIAgent):
    """
    Agent 1.2: Structure Recognizer

    DIRECTIVE:
    ---------
    Meta-classifier that tags problem type and mathematical domain.
    Does NOT solve - only categorizes.

    LOGIC:
    -----
    Distinguishes between:
    - COMPUTATION: "Calculate this"
    - PROOF: "Show that..."
    - OPTIMIZATION: "Find the maximum..."

    Tags domain:
    - CALCULUS: derivatives, integrals, limits
    - ALGEBRA: equations, polynomials
    - etc.

    REFERENCE:
    ---------
    - Phase_1_Build_Order_Breakdown.md: Lines 56-60 (Agent 1.2 specification)
    - Phase 1 Coding Strategy: "This agent does not solve; it categorizes"
    """

    def __init__(self, agent_id: str = 'structure_recognizer_001'):
        """Initialize Structure Recognizer Agent"""
        super().__init__(agent_id)

        # Classification keywords
        self.problem_type_keywords = {
            ProblemType.PROOF: [
                'prove', 'show that', 'demonstrate', 'verify that',
                'establish', 'theorem', 'lemma', 'proposition'
            ],
            ProblemType.OPTIMIZATION: [
                'maximize', 'minimize', 'optimize', 'maximum', 'minimum',
                'extrema', 'critical points', 'largest', 'smallest'
            ],
            ProblemType.COMPUTATION: [
                'calculate', 'compute', 'evaluate', 'find', 'solve',
                'simplify', 'determine', 'what is', 'derivative', 'integral'
            ]
        }

        self.domain_keywords = {
            MathDomain.CALCULUS: [
                'derivative', 'integral', 'limit', 'continuity',
                'differentiate', 'integrate', 'tangent', 'rate of change',
                'd/dx', 'antiderivative', 'dsolve', 'diff', 'ode', 'pde',
                'differential equation', 'series', 'taylor', 'maclaurin',
                'laplace', 'fourier',
                'lim', 'lim_', 'summation', 'sum(', 'Sum('
            ],
            MathDomain.LINEAR_ALGEBRA: [
                'matrix', 'matrices', 'vector', 'determinant', 'eigenvalue',
                'eigenvector', 'transpose', 'inverse', 'rank', 'nullspace',
                'kernel', 'span', 'basis', 'orthogonal', 'orthonormal',
                'svd', 'singular value', 'decomposition', 'lu', 'qr',
                'cholesky', 'trace', 'dot product', 'cross product',
                'linear transformation', 'linear system',
                'det(', 'det ', 'eye(', 'identity', 'diag(', 'zeros(',
                'ones(', 'trace('
            ],
            MathDomain.ALGEBRA: [
                'equation', 'polynomial', 'factor', 'expand', 'solve',
                'root', 'quadratic', 'expression', 'simplify',
                '+', '-', '*', '/', '**', '^', 'add', 'subtract', 'multiply',
                'divide', 'power', 'sqrt', 'square', 'cube', 'arithmetic'
            ],
            MathDomain.STATISTICS: [
                'probability', 'distribution', 'mean', 'median', 'variance',
                'standard deviation', 'hypothesis', 'p-value', 'confidence',
                'bayesian', 'prior', 'posterior', 'likelihood', 'regression',
                'correlation', 'sample', 'population', 'normal', 'binomial'
            ],
            MathDomain.DISCRETE_MATH: [
                'permutation', 'combination', 'graph', 'vertex', 'edge',
                'path', 'cycle', 'tree', 'combinatorics', 'recurrence',
                'counting', 'factorial', 'binomial coefficient'
            ],
            MathDomain.NUMBER_THEORY: [
                'diophantine', 'diophantine(', 'prime', 'primality', 'gcd',
                'lcm', 'modular', 'congruence', 'divisor', 'divisible',
                'coprime', 'euler', 'totient', 'fermat', 'chinese remainder',
                'quadratic residue', 'legendre', 'jacobi', 'continued fraction',
                'pell equation', 'pythagorean triple', 'integer solution'
            ],
            MathDomain.GEOMETRY: [
                'triangle', 'circle', 'angle', 'area', 'volume',
                'perimeter', 'pythagorean', 'distance', 'parallel',
                'radius', 'diameter', 'polygon', 'rectangle', 'square',
                'ellipse', 'parabola', 'hyperbola', 'conic', 'line',
                'slope', 'intercept', 'coordinate', 'rotation', 'reflection',
                'translation', 'transformation', 'sine', 'cosine', 'tangent',
                'trigonometry', 'trig', 'polar', 'radian', 'degree'
            ],
            MathDomain.LOGIC: [
                'implies', 'if and only if', 'contradiction', 'tautology',
                'logical', 'truth table', 'proposition', 'proof', 'prove',
                'theorem', 'lemma', 'corollary', 'forall', 'exists',
                'quantifier', 'predicate', 'induction', 'contrapositive',
                'modus ponens', 'modus tollens', 'boolean', 'cnf', 'dnf'
            ],
            MathDomain.PHYSICS_MECHANICS: [
                'velocity', 'acceleration', 'force', 'newton', 'motion',
                'projectile', 'friction', 'momentum', 'impulse', 'collision',
                'kinetic energy', 'potential energy', 'work', 'power',
                'incline', 'circular motion', 'centripetal', 'dynamics',
                'kinematics', 'free fall', 'mass', 'weight', 'gravity'
            ],
            MathDomain.PHYSICS_EM: [
                'electric', 'magnetic', 'charge', 'coulomb', 'field',
                'voltage', 'current', 'resistance', 'capacitor', 'inductor',
                'circuit', 'ohm', 'kirchhoff', 'faraday', 'ampere',
                'lorentz', 'flux', 'electromagnetic', 'solenoid', 'emf'
            ],
            MathDomain.PHYSICS_THERMO: [
                'heat', 'temperature', 'thermal', 'entropy', 'gas',
                'pressure', 'volume', 'ideal gas', 'isothermal', 'adiabatic',
                'carnot', 'specific heat', 'latent heat', 'conduction',
                'convection', 'radiation', 'stefan-boltzmann', 'thermodynamic'
            ],
            MathDomain.PHYSICS_QUANTUM: [
                'quantum', 'wavefunction', 'wave function', 'schrodinger',
                'hydrogen atom', 'bohr', 'photon', 'planck', 'de broglie',
                'heisenberg', 'uncertainty', 'spin', 'orbital', 'tunneling',
                'eigenvalue', 'eigenstate', 'angular momentum', 'commutator'
            ]
        }

    def classify(self, structured: StructuredProblem) -> StructuredProblem:
        """
        Classify problem type and domain

        Args:
            structured: StructuredProblem from SyntaxParser

        Returns:
            StructuredProblem with type and domain classifications

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 92-106 (classify method)
        """
        text = structured.raw_input.lower()

        # Classify problem type
        structured.problem_type = self._classify_problem_type(text)

        # Classify domain
        structured.domain = self._classify_domain(text, structured.metadata)

        # Add classification metadata
        structured.metadata['classified_at'] = datetime.now()
        structured.metadata['classifier'] = self.agent_id

        return structured

    def _classify_problem_type(self, text: str) -> ProblemType:
        """
        Classify problem type based on keywords

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 96-102
        """
        scores = {ptype: 0 for ptype in ProblemType}

        for ptype, keywords in self.problem_type_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[ptype] += 1

        # Get highest scoring type
        max_score = max(scores.values())
        if max_score == 0:
            return ProblemType.COMPUTATION  # Default

        for ptype, score in scores.items():
            if score == max_score:
                return ptype

        return ProblemType.UNKNOWN

    def _classify_domain(self, text: str, metadata: Dict) -> MathDomain:
        """
        Classify mathematical domain

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 103-106
        """
        scores = {domain: 0 for domain in MathDomain}

        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[domain] += 1

        # Check metadata for operation hints - operation is more reliable than text keywords
        # Give a strong boost to ensure operation type overrides incidental operator matches
        if 'operation' in metadata:
            op = metadata['operation']
            if op in ['derivative', 'integral', 'integral_2d', 'limit', 'limit_latex', 'dsolve', 'ode', 'diff', 'series', 'summation', 'product']:
                scores[MathDomain.CALCULUS] += 10  # Strong boost for calculus operations (including series, limits, 2D integrals)
            elif op in ['solve', 'factor', 'expand', 'simplify']:
                scores[MathDomain.ALGEBRA] += 5

        # Get highest scoring domain
        max_score = max(scores.values())
        if max_score == 0:
            # Default to ALGEBRA for pure expressions without keywords
            # This handles cases like "2 + 2" or "x^2"
            return MathDomain.ALGEBRA

        for domain, score in scores.items():
            if score == max_score:
                return domain

        return MathDomain.ALGEBRA  # Default fallback

    # BDI Implementation (simplified)
    def update_beliefs(self):
        """Update beliefs from environment"""
        pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions"""
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step"""
        pass


class ProblemAnalysisTeam:
    """
    Integrated Problem Analysis Team

    Combines Syntax Parser and Structure Recognizer into a unified
    team that processes raw input into structured, classified OMDoc objects.

    USAGE:
    -----
    team = ProblemAnalysisTeam()
    structured = team.process("Calculate the derivative of x squared")
    # Returns: StructuredProblem(type=COMPUTATION, domain=CALCULUS, ...)
    """

    def __init__(self):
        """Initialize Problem Analysis Team"""
        self.parser = SyntaxParserAgent()
        self.recognizer = StructureRecognizerAgent()

        print(f"[Problem Analysis Team] Initialized")
        print(f"  - {self.parser.agent_id}: Syntax Parser ready")
        print(f"  - {self.recognizer.agent_id}: Structure Recognizer ready")

    def process(self, raw_input: str) -> StructuredProblem:
        """
        Process raw input through full analysis pipeline

        Args:
            raw_input: Raw natural language or LaTeX

        Returns:
            Fully structured and classified problem
        """
        # Safe print - handle Unicode characters that can't be encoded in console
        try:
            print(f"\n[Problem Analysis Team] Processing: '{raw_input}'")
        except UnicodeEncodeError:
            safe_input = raw_input.encode('ascii', 'replace').decode('ascii')
            print(f"\n[Problem Analysis Team] Processing: '{safe_input}'")

        # Step 1: Parse to OMDoc
        print(f"  [{self.parser.agent_id}] Parsing to OMDoc...")
        structured = self.parser.parse(raw_input)

        # Step 2: Classify
        print(f"  [{self.recognizer.agent_id}] Classifying...")
        structured = self.recognizer.classify(structured)

        print(f"  [Result] Type: {structured.problem_type.value}, Domain: {structured.domain.value}")

        return structured


if __name__ == "__main__":
    """Test Problem Analysis Team"""
    print("=" * 80)
    print("PHASE 1 - STEP 1: PROBLEM ANALYSIS TEAM TEST")
    print("=" * 80)
    print()

    # Initialize team
    team = ProblemAnalysisTeam()
    print()

    # Test cases
    test_inputs = [
        "Calculate the derivative of x² + 1",
        "Find the integral of sin(x)",
        "Prove that the limit of 1/x as x approaches infinity is 0",
        "Maximize the function f(x) = -x² + 4x",
        "Simplify the expression (x + 1)(x - 1)"
    ]

    print("Testing with sample problems...")
    print()

    for test_input in test_inputs:
        structured = team.process(test_input)
        print()

    print("=" * 80)
    print("PROBLEM ANALYSIS TEAM TEST COMPLETE")
    print("=" * 80)
