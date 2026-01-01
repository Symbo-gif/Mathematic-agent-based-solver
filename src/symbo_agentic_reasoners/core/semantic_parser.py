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
SEMANTIC PARSER - Internal AST Layer (SymPy Last Resort)
========================================================

This module provides the internal semantic AST layer that sits BEFORE SymPy
in the processing pipeline. It parses normalized input into OMDoc-derived
structures, identifies command forms, and enables domain-first routing.

ARCHITECTURE PRINCIPLES:
-----------------------
1. Parse to internal AST FIRST, sympify LAST (and only when needed)
2. Commands (solve, grad, dsolve) are recognized at this layer
3. Specialists receive structured semantic objects, not strings
4. SymPy is a computation engine, not a parser

FLOW:
----
Raw Input → InputNormalizer → SemanticParser → OMDoc AST → Router → Specialist
                                                                        ↓
                                                              (only if needed)
                                                                    SymPy

COMPONENTS:
----------
- CommandNode: Represents high-level commands (solve, dsolve, grad, etc.)
- ExpressionNode: Represents mathematical expressions
- SemanticParser: Parses normalized strings into semantic nodes
- NodeType: Classification of node types for routing

Reference:
---------
Second Opinion Analysis: "Introduce an internal 'semantic layer' before Sympify"
"""

import re
import ast
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union

from symbo_agentic_reasoners.core.omdoc_schema import (
    OMObject, MathOperator, create_variable, create_number, create_operation
)


class NodeType(Enum):
    """Classification of semantic node types for routing."""
    # Commands
    SOLVE = auto()          # solve(expr, var) - algebra solve
    DSOLVE = auto()         # dsolve(ode, func) - ODE solve
    GRAD = auto()           # grad(f, [vars]) - gradient
    DIV = auto()            # div([F], [vars]) - divergence
    CURL = auto()           # curl([F], [vars]) - curl
    LAPLACIAN = auto()      # laplacian(f, [vars])

    # Calculus operations
    DIFF = auto()           # differentiate
    INTEGRATE = auto()      # integrate
    LIMIT = auto()          # limit
    SERIES = auto()         # taylor/maclaurin series

    # Algebra operations
    FACTOR = auto()
    EXPAND = auto()
    SIMPLIFY = auto()

    # Linear algebra
    DET = auto()            # determinant
    EIGENVALS = auto()      # eigenvalues
    EIGENVECTS = auto()     # eigenvectors
    INVERSE = auto()        # matrix inverse

    # Expression types
    EQUATION = auto()       # expr = expr
    EXPRESSION = auto()     # pure expression
    MATRIX = auto()         # matrix literal
    VECTOR = auto()         # vector literal

    # Unknown - needs SymPy fallback
    UNKNOWN = auto()


@dataclass
class SemanticNode:
    """
    Base class for semantic AST nodes.

    All parsed mathematical content is represented as SemanticNodes,
    which can be processed by specialists without requiring SymPy.
    """
    node_type: NodeType
    raw_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Tracking for SymPy fallback
    needs_sympy: bool = False
    sympy_reason: Optional[str] = None


@dataclass
class CommandNode(SemanticNode):
    """
    Represents a high-level command like solve(), dsolve(), grad().

    Commands are distinguished from expressions because they have
    explicit target operations and parameters that direct routing.

    Examples:
    - solve(x^2 - 4 = 0, x) → CommandNode(SOLVE, expr="x^2 - 4 = 0", variable="x")
    - grad(f, [x, y]) → CommandNode(GRAD, expr="f", variables=["x", "y"])
    - dsolve(y'(x) + y(x) = 0, y(x)) → CommandNode(DSOLVE, expr="y'(x) + y(x) = 0", func="y(x)")
    """
    command_name: str = ""
    expression: Optional['ExpressionNode'] = None
    variables: List[str] = field(default_factory=list)
    function: Optional[str] = None  # For dsolve - the function being solved for
    domain: Optional[str] = None    # e.g., "R", "C", "Z"
    extra_args: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExpressionNode(SemanticNode):
    """
    Represents a mathematical expression.

    Can be converted to OMDoc for semantic representation,
    or to SymPy only when computation is needed.
    """
    omdoc: Optional[OMObject] = None

    # Structural information (parsed without SymPy)
    operators: List[str] = field(default_factory=list)  # ['+', '*', '**', etc.]
    variables: List[str] = field(default_factory=list)  # ['x', 'y', 'z', etc.]
    functions: List[str] = field(default_factory=list)  # ['sin', 'cos', 'exp', etc.]
    numbers: List[str] = field(default_factory=list)    # ['2', '3.14', '-1', etc.]

    # For equations
    is_equation: bool = False
    lhs: Optional['ExpressionNode'] = None
    rhs: Optional['ExpressionNode'] = None


@dataclass
class MatrixNode(SemanticNode):
    """Represents a matrix literal."""
    rows: List[List['ExpressionNode']] = field(default_factory=list)
    shape: Tuple[int, int] = (0, 0)


@dataclass
class ParseResult:
    """Result of semantic parsing."""
    success: bool
    node: Optional[SemanticNode] = None
    error: Optional[str] = None

    # Diagnostic information
    detected_type: Optional[NodeType] = None
    confidence: float = 1.0
    fallback_to_sympy: bool = False
    fallback_reason: Optional[str] = None


class SemanticParser:
    """
    Parses normalized mathematical input into semantic AST nodes.

    This is the core of the "SymPy last resort" architecture. It parses
    normalized strings into structured semantic nodes that can be
    processed by specialists without SymPy dependency.

    USAGE:
    -----
    parser = SemanticParser()
    result = parser.parse("solve(x^2 - 4 = 0, x)")

    if result.success:
        node = result.node
        # Route based on node.node_type
        if node.node_type == NodeType.SOLVE:
            # Send to polynomial specialist

    COMMAND PATTERNS:
    ----------------
    - solve(expr, var) → CommandNode(SOLVE)
    - dsolve(ode, func) → CommandNode(DSOLVE)
    - grad(f, [vars]) → CommandNode(GRAD)
    - div([F], [vars]) → CommandNode(DIV)
    - curl([F], [vars]) → CommandNode(CURL)
    - diff(expr, var) / derivative → ExpressionNode + metadata
    - integrate(expr, var) / integral → ExpressionNode + metadata
    """

    # Command patterns - detect before any SymPy involvement
    COMMAND_PATTERNS = {
        'solve': re.compile(
            r'^solve\s*\(\s*(.+?)\s*,\s*(\[?[\w,\s]+\]?)\s*(?:,\s*domain\s*=\s*(\w+))?\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'dsolve': re.compile(
            r'^dsolve\s*\(\s*(.+?)\s*,\s*(\w+\s*\(\s*\w+\s*\))\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'grad': re.compile(
            r'^grad\s*\(\s*(.+?)\s*,\s*\[([^\]]+)\]\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'div': re.compile(
            r'^div\s*\(\s*\[([^\]]+)\]\s*(?:,\s*\[([^\]]+)\])?\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'curl': re.compile(
            r'^curl\s*\(\s*\[([^\]]+)\]\s*,\s*\[([^\]]+)\]\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'diff': re.compile(
            r'^diff\s*\(\s*(.+?)\s*,\s*(\w+)(?:\s*,\s*(\d+))?\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'integrate': re.compile(
            r'^integrate\s*\(\s*(.+?)\s*,\s*(?:\(\s*(\w+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)|(\w+))\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'limit': re.compile(
            r'^limit\s*\(\s*(.+?)\s*,\s*(\w+)\s*,\s*(.+?)\s*(?:,\s*([+-]))?\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'det': re.compile(
            r'^det\s*\(\s*(.+)\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'eigenvals': re.compile(
            r'^eigenvals?\s*\(\s*(.+)\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'eigenvects': re.compile(
            r'^eigenvects?\s*\(\s*(.+)\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'factor': re.compile(
            r'^factor\s*\(\s*(.+)\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'expand': re.compile(
            r'^expand\s*\(\s*(.+)\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'simplify': re.compile(
            r'^simplify\s*\(\s*(.+)\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
        'series': re.compile(
            r'^(?:series|taylor|maclaurin)\s*\(\s*(.+?)\s*,\s*(\w+)\s*(?:,\s*(\w+|\d+))?\s*(?:,\s*(\d+))?\s*\)$',
            re.IGNORECASE | re.DOTALL
        ),
    }

    # Expression structure patterns (extract without SymPy)
    VARIABLE_PATTERN = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b')
    NUMBER_PATTERN = re.compile(r'(?<![a-zA-Z_])(-?\d+\.?\d*(?:[eE][+-]?\d+)?)')
    OPERATOR_PATTERN = re.compile(r'(\*\*|[+\-*/^]|==|!=|<=|>=|<|>|=)')
    FUNCTION_PATTERN = re.compile(r'\b(sin|cos|tan|exp|log|ln|sqrt|abs|floor|ceil|asin|acos|atan)\s*\(')

    # Known constants and functions (not variables)
    KNOWN_FUNCTIONS = {
        'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
        'asin', 'acos', 'atan', 'acot', 'asec', 'acsc',
        'sinh', 'cosh', 'tanh', 'coth', 'sech', 'csch',
        'asinh', 'acosh', 'atanh', 'acoth', 'asech', 'acsch',
        'exp', 'log', 'ln', 'sqrt', 'abs', 'sign',
        'floor', 'ceil', 'round',
        'diff', 'integrate', 'limit', 'Sum', 'Product',
        'factorial', 'binomial', 'gamma', 'beta',
        'solve', 'dsolve', 'grad', 'div', 'curl',
        'det', 'eigenvals', 'eigenvects', 'trace', 'transpose',
        'factor', 'expand', 'simplify', 'collect', 'cancel',
        'series', 'taylor', 'maclaurin',
        'Eq', 'Ne', 'Lt', 'Le', 'Gt', 'Ge',
        'Matrix', 'Array', 'list'
    }

    KNOWN_CONSTANTS = {
        'pi', 'e', 'E', 'I', 'oo', 'inf', 'nan',
        'true', 'false', 'True', 'False',
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta',
        'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu',
        'nu', 'xi', 'omicron', 'rho', 'sigma', 'tau',
        'upsilon', 'phi', 'chi', 'psi', 'omega'
    }

    def __init__(self):
        """Initialize the semantic parser."""
        pass

    def parse(self, text: str) -> ParseResult:
        """
        Parse normalized text into a semantic AST node.

        Args:
            text: Normalized mathematical text

        Returns:
            ParseResult with success status and parsed node
        """
        if not text or not text.strip():
            return ParseResult(
                success=False,
                error="Empty input"
            )

        text = text.strip()

        # Step 1: Try to parse as a command
        command_result = self._try_parse_command(text)
        if command_result.success:
            return command_result

        # Step 2: Try to parse as an equation
        equation_result = self._try_parse_equation(text)
        if equation_result.success:
            return equation_result

        # Step 3: Parse as a general expression
        expr_result = self._parse_expression(text)
        return expr_result

    def _try_parse_command(self, text: str) -> ParseResult:
        """
        Try to parse text as a command (solve, dsolve, grad, etc.).

        Returns:
            ParseResult - success if command pattern matched
        """
        for cmd_name, pattern in self.COMMAND_PATTERNS.items():
            match = pattern.match(text)
            if match:
                return self._build_command_node(cmd_name, match, text)

        return ParseResult(success=False)

    def _build_command_node(self, cmd_name: str, match: re.Match, raw_text: str) -> ParseResult:
        """Build a CommandNode from a regex match."""
        groups = match.groups()

        node_type_map = {
            'solve': NodeType.SOLVE,
            'dsolve': NodeType.DSOLVE,
            'grad': NodeType.GRAD,
            'div': NodeType.DIV,
            'curl': NodeType.CURL,
            'diff': NodeType.DIFF,
            'integrate': NodeType.INTEGRATE,
            'limit': NodeType.LIMIT,
            'det': NodeType.DET,
            'eigenvals': NodeType.EIGENVALS,
            'eigenvects': NodeType.EIGENVECTS,
            'factor': NodeType.FACTOR,
            'expand': NodeType.EXPAND,
            'simplify': NodeType.SIMPLIFY,
            'series': NodeType.SERIES,
        }

        node_type = node_type_map.get(cmd_name, NodeType.UNKNOWN)

        # Build command-specific node
        if cmd_name == 'solve':
            expr_text, var_text = groups[0], groups[1]
            domain = groups[2] if len(groups) > 2 else None

            # Parse variables (could be single or list)
            variables = self._parse_variable_list(var_text)

            # Parse the expression
            expr_result = self._parse_expression(expr_text)
            expr_node = expr_result.node if expr_result.success else None

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name='solve',
                expression=expr_node,
                variables=variables,
                domain=domain
            )

        elif cmd_name == 'dsolve':
            ode_text, func_text = groups[0], groups[1]

            expr_result = self._parse_expression(ode_text)
            expr_node = expr_result.node if expr_result.success else None

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name='dsolve',
                expression=expr_node,
                function=func_text.strip()
            )

        elif cmd_name == 'grad':
            expr_text, vars_text = groups[0], groups[1]
            variables = self._parse_variable_list(vars_text)

            expr_result = self._parse_expression(expr_text)
            expr_node = expr_result.node if expr_result.success else None

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name='grad',
                expression=expr_node,
                variables=variables
            )

        elif cmd_name == 'div':
            components_text = groups[0]
            vars_text = groups[1] if len(groups) > 1 and groups[1] else None

            components = [c.strip() for c in components_text.split(',')]
            variables = self._parse_variable_list(vars_text) if vars_text else []

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name='div',
                variables=variables,
                extra_args={'components': components}
            )

        elif cmd_name == 'curl':
            components_text, vars_text = groups[0], groups[1]

            components = [c.strip() for c in components_text.split(',')]
            variables = self._parse_variable_list(vars_text)

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name='curl',
                variables=variables,
                extra_args={'components': components}
            )

        elif cmd_name == 'diff':
            expr_text, var, order = groups[0], groups[1], groups[2] if len(groups) > 2 else '1'

            expr_result = self._parse_expression(expr_text)
            expr_node = expr_result.node if expr_result.success else None

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name='diff',
                expression=expr_node,
                variables=[var],
                extra_args={'order': int(order) if order else 1}
            )

        elif cmd_name == 'integrate':
            expr_text = groups[0]
            # Could be definite (with limits) or indefinite
            if groups[1]:  # Definite integral
                var, lower, upper = groups[1], groups[2], groups[3]
                node = CommandNode(
                    node_type=node_type,
                    raw_text=raw_text,
                    command_name='integrate',
                    expression=self._parse_expression(expr_text).node,
                    variables=[var],
                    extra_args={'definite': True, 'lower': lower, 'upper': upper}
                )
            else:  # Indefinite integral
                var = groups[4]
                node = CommandNode(
                    node_type=node_type,
                    raw_text=raw_text,
                    command_name='integrate',
                    expression=self._parse_expression(expr_text).node,
                    variables=[var] if var else [],
                    extra_args={'definite': False}
                )

        elif cmd_name == 'limit':
            expr_text, var, point, direction = groups

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name='limit',
                expression=self._parse_expression(expr_text).node,
                variables=[var],
                extra_args={'point': point, 'direction': direction}
            )

        elif cmd_name in ['det', 'eigenvals', 'eigenvects']:
            matrix_text = groups[0]

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name=cmd_name,
                extra_args={'matrix': matrix_text}
            )

        elif cmd_name in ['factor', 'expand', 'simplify']:
            expr_text = groups[0]

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name=cmd_name,
                expression=self._parse_expression(expr_text).node
            )

        elif cmd_name == 'series':
            expr_text = groups[0]
            var = groups[1]
            point = groups[2] if len(groups) > 2 and groups[2] else '0'
            order = groups[3] if len(groups) > 3 and groups[3] else '6'

            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name='series',
                expression=self._parse_expression(expr_text).node,
                variables=[var],
                extra_args={'point': point, 'order': int(order)}
            )

        else:
            # Generic command
            node = CommandNode(
                node_type=node_type,
                raw_text=raw_text,
                command_name=cmd_name
            )

        return ParseResult(
            success=True,
            node=node,
            detected_type=node_type,
            confidence=0.95
        )

    def _try_parse_equation(self, text: str) -> ParseResult:
        """
        Try to parse text as an equation (contains '=' but not '==').
        """
        # Check for equation (single =, not ==, !=, <=, >=)
        if '=' in text and '==' not in text and '!=' not in text:
            # Not inside Eq() already
            if not text.strip().startswith('Eq('):
                # Split on '='
                parts = text.split('=')
                if len(parts) == 2:
                    lhs_text = parts[0].strip()
                    rhs_text = parts[1].strip()

                    lhs_result = self._parse_expression(lhs_text)
                    rhs_result = self._parse_expression(rhs_text)

                    node = ExpressionNode(
                        node_type=NodeType.EQUATION,
                        raw_text=text,
                        is_equation=True,
                        lhs=lhs_result.node if lhs_result.success else None,
                        rhs=rhs_result.node if rhs_result.success else None
                    )

                    return ParseResult(
                        success=True,
                        node=node,
                        detected_type=NodeType.EQUATION,
                        confidence=0.9
                    )

        return ParseResult(success=False)

    def _parse_expression(self, text: str) -> ParseResult:
        """
        Parse text as a general mathematical expression.

        Extracts structural information without using SymPy.
        """
        if not text or not text.strip():
            return ParseResult(success=False, error="Empty expression")

        text = text.strip()

        # Extract structural information
        variables = self._extract_variables(text)
        operators = self.OPERATOR_PATTERN.findall(text)
        functions = self.FUNCTION_PATTERN.findall(text)
        numbers = self.NUMBER_PATTERN.findall(text)

        # Check for matrix/vector
        if text.startswith('[[') or text.startswith('['):
            node_type = NodeType.MATRIX if '[[' in text else NodeType.VECTOR
        else:
            node_type = NodeType.EXPRESSION

        node = ExpressionNode(
            node_type=node_type,
            raw_text=text,
            operators=operators,
            variables=variables,
            functions=functions,
            numbers=numbers
        )

        return ParseResult(
            success=True,
            node=node,
            detected_type=node_type,
            confidence=0.8
        )

    def _extract_variables(self, text: str) -> List[str]:
        """Extract variable names from text, excluding functions and constants."""
        matches = self.VARIABLE_PATTERN.findall(text)

        # Filter out known functions and constants
        variables = [
            m for m in matches
            if m not in self.KNOWN_FUNCTIONS
            and m not in self.KNOWN_CONSTANTS
            and not m.isdigit()
        ]

        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for v in variables:
            if v not in seen:
                seen.add(v)
                unique.append(v)

        return unique

    def _parse_variable_list(self, text: str) -> List[str]:
        """Parse a variable list like 'x' or '[x, y, z]' or 'x, y'."""
        if not text:
            return []

        text = text.strip()

        # Remove brackets if present
        if text.startswith('[') and text.endswith(']'):
            text = text[1:-1]

        # Split by comma
        parts = [p.strip() for p in text.split(',')]

        return [p for p in parts if p]

    def to_omdoc(self, node: SemanticNode) -> Optional[OMObject]:
        """
        Convert a semantic node to OMDoc representation.

        This enables full semantic encoding without SymPy.
        """
        if isinstance(node, CommandNode):
            return self._command_to_omdoc(node)
        elif isinstance(node, ExpressionNode):
            return self._expression_to_omdoc(node)
        else:
            return create_variable(node.raw_text)

    def _command_to_omdoc(self, node: CommandNode) -> OMObject:
        """Convert CommandNode to OMDoc."""
        # Map command types to operators
        operator_map = {
            NodeType.DIFF: MathOperator.DIFF,
            NodeType.INTEGRATE: MathOperator.INT,
        }

        if node.node_type in operator_map:
            expr_omdoc = self._expression_to_omdoc(node.expression) if node.expression else create_variable('_')
            var_omdoc = create_variable(node.variables[0]) if node.variables else create_variable('x')
            return create_operation(operator_map[node.node_type], expr_omdoc, var_omdoc)

        # For other commands, create a symbolic representation
        return create_variable(f"{node.command_name}({node.raw_text})")

    def _expression_to_omdoc(self, node: Optional[ExpressionNode]) -> OMObject:
        """Convert ExpressionNode to OMDoc."""
        if not node:
            return create_variable('_')

        if node.is_equation and node.lhs and node.rhs:
            lhs_omdoc = self._expression_to_omdoc(node.lhs)
            rhs_omdoc = self._expression_to_omdoc(node.rhs)
            return create_operation(MathOperator.EQ, lhs_omdoc, rhs_omdoc)

        # For simple expressions, create a variable with the raw text
        # Full expression tree building would require a proper expression parser
        return create_variable(node.raw_text)


def parse_to_semantic(text: str) -> ParseResult:
    """
    Convenience function to parse text to semantic AST.

    Usage:
        result = parse_to_semantic("solve(x^2 - 4 = 0, x)")
        if result.success:
            # Route based on result.node.node_type
    """
    parser = SemanticParser()
    return parser.parse(text)


def get_routing_info(node: SemanticNode) -> Dict[str, Any]:
    """
    Get routing information from a semantic node.

    Returns domain, specialist type, and operation for the router.
    """
    info = {
        'domain': None,
        'specialist': None,
        'operation': None,
        'needs_sympy': False
    }

    # Route based on node type
    type_routing = {
        NodeType.SOLVE: ('algebra', 'polynomial', 'solve'),
        NodeType.DSOLVE: ('calculus', 'ode', 'dsolve'),
        NodeType.GRAD: ('calculus', 'vector_calculus', 'grad'),
        NodeType.DIV: ('calculus', 'vector_calculus', 'div'),
        NodeType.CURL: ('calculus', 'vector_calculus', 'curl'),
        NodeType.DIFF: ('calculus', 'differentiation', 'diff'),
        NodeType.INTEGRATE: ('calculus', 'integration', 'integrate'),
        NodeType.LIMIT: ('calculus', 'limit', 'limit'),
        NodeType.SERIES: ('calculus', 'series', 'series'),
        NodeType.FACTOR: ('algebra', 'polynomial', 'factor'),
        NodeType.EXPAND: ('algebra', 'polynomial', 'expand'),
        NodeType.SIMPLIFY: ('algebra', 'arithmetic', 'simplify'),
        NodeType.DET: ('linear_algebra', 'matrix', 'determinant'),
        NodeType.EIGENVALS: ('linear_algebra', 'matrix', 'eigenvalues'),
        NodeType.EIGENVECTS: ('linear_algebra', 'matrix', 'eigenvectors'),
        NodeType.EQUATION: ('algebra', 'polynomial', 'solve'),
        NodeType.EXPRESSION: ('algebra', 'arithmetic', 'compute'),
        NodeType.MATRIX: ('linear_algebra', 'matrix', 'compute'),
        NodeType.UNKNOWN: (None, None, None),
    }

    if node.node_type in type_routing:
        domain, specialist, operation = type_routing[node.node_type]
        info['domain'] = domain
        info['specialist'] = specialist
        info['operation'] = operation

    info['needs_sympy'] = node.needs_sympy

    return info
