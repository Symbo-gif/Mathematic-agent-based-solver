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
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

logger = logging.getLogger('symbo_agentic_reasoners.phase1.problem_analysis')

# Add parent to path for Phase 0 imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from symbo_agentic_reasoners_phase0.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners_phase0.core.omdoc_schema import (
    create_variable, create_number, create_operation,
    OMObject, MathOperator
)
from symbo_agentic_reasoners_phase0.core.fipa_acl import create_inform


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
    GEOMETRY = 'Geometry'
    LOGIC = 'Logic'
    NUMBER_THEORY = 'NumberTheory'
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

        # SymPy transformations for parsing
        self.transformations = (standard_transformations +
                               (implicit_multiplication_application,))

        # Parsing patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for mathematical operations"""
        self.patterns = {
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
            'solve': re.compile(
                r'solve\s+(.*?)(?:\s+for\s+(\w+))?$',
                re.IGNORECASE
            ),
            'simplify': re.compile(
                r'simplify\s+(.*?)$',
                re.IGNORECASE
            ),
            'factor': re.compile(
                r'factor(?:ize)?\s+(.*?)$',
                re.IGNORECASE
            ),
            'expand': re.compile(
                r'expand\s+(.*?)$',
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
        # Clean and normalize input
        cleaned = self._clean_input(raw_input)

        # Extract operation and expression
        operation, expression, variable = self._extract_operation(cleaned)

        # Parse expression to SymPy
        try:
            sympy_expr = self._parse_to_sympy(expression, variable)
        except (ValueError, SyntaxError, TypeError) as e:
            # If parsing fails, create a text placeholder
            sympy_expr = None
            logger.debug(f"Could not parse '{expression}': {type(e).__name__}: {e}")

        # Convert to OMDoc
        omdoc_content = self._sympy_to_omdoc(sympy_expr, operation, variable)

        # Create structured problem (classification added by Structure Recognizer)
        structured = StructuredProblem(
            raw_input=raw_input,
            omdoc_content=omdoc_content,
            problem_type=ProblemType.UNKNOWN,  # Set by StructureRecognizer
            domain=MathDomain.UNKNOWN,  # Set by StructureRecognizer
            sympy_expr=sympy_expr,
            metadata={
                'operation': operation,
                'variable': variable
            }
        )

        return structured

    def _clean_input(self, raw: str) -> str:
        """Clean and normalize input text"""
        # Remove extra whitespace
        cleaned = ' '.join(raw.split())

        # Normalize common mathematical notation
        cleaned = cleaned.replace('^', '**')  # LaTeX power to Python
        cleaned = cleaned.replace('²', '**2')
        cleaned = cleaned.replace('³', '**3')

        return cleaned

    def _extract_operation(self, text: str) -> tuple:
        """
        Extract operation type and mathematical expression

        Returns:
            (operation, expression, variable) tuple
        """
        # Try each pattern
        for op_name, pattern in self.patterns.items():
            match = pattern.search(text)
            if match:
                groups = match.groups()
                operation = op_name
                expression = groups[1] if len(groups) > 1 else text
                variable = groups[2] if len(groups) > 2 else 'x'
                return operation, expression.strip(), variable

        # No pattern matched - assume direct expression
        return 'compute', text, 'x'

    def _parse_to_sympy(self, expression: str, variable: str = 'x') -> Any:
        """
        Parse expression string to SymPy object

        Args:
            expression: Mathematical expression string
            variable: Primary variable name

        Returns:
            SymPy expression object
        """
        try:
            # Parse with implicit multiplication
            expr = parse_expr(expression, transformations=self.transformations)
            return expr
        except (SyntaxError, TypeError, AttributeError) as e:
            # Try without transformations
            try:
                expr = parse_expr(expression)
                return expr
            except (SyntaxError, TypeError, AttributeError) as e2:
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
        Recursively convert SymPy expression to OMDoc

        This is a simplified converter - full implementation would
        handle all SymPy expression types.
        """
        if expr is None:
            return create_variable('none')

        # Convert based on SymPy expression type
        from sympy import Symbol, Add, Mul, Pow, Integer, Number

        if isinstance(expr, Symbol):
            return create_variable(str(expr))

        elif isinstance(expr, (Integer, int)):
            return create_variable(str(expr))

        elif isinstance(expr, Number):
            return create_variable(str(float(expr)))

        elif isinstance(expr, Add):
            # Addition: (+ arg1 arg2 ...)
            args = [self._sympy_expr_to_omdoc(arg) for arg in expr.args]
            return create_operation(MathOperator.PLUS, *args)

        elif isinstance(expr, Mul):
            # Multiplication: (* arg1 arg2 ...)
            args = [self._sympy_expr_to_omdoc(arg) for arg in expr.args]
            return create_operation(MathOperator.TIMES, *args)

        elif isinstance(expr, Pow):
            # Power: (^ base exponent)
            base = self._sympy_expr_to_omdoc(expr.args[0])
            exp = self._sympy_expr_to_omdoc(expr.args[1])
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
                'd/dx', 'antiderivative'
            ],
            MathDomain.ALGEBRA: [
                'equation', 'polynomial', 'factor', 'expand', 'solve',
                'root', 'quadratic', 'linear', 'expression', 'simplify',
                '+', '-', '*', '/', '**', '^', 'add', 'subtract', 'multiply',
                'divide', 'power', 'sqrt', 'square', 'cube', 'arithmetic'
            ],
            MathDomain.GEOMETRY: [
                'triangle', 'circle', 'angle', 'area', 'volume',
                'perimeter', 'pythagorean', 'distance', 'parallel'
            ],
            MathDomain.LOGIC: [
                'implies', 'if and only if', 'contradiction', 'tautology',
                'logical', 'truth table', 'proposition'
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

        # Also check metadata for operation hints
        if 'operation' in metadata:
            op = metadata['operation']
            if op in ['derivative', 'integral', 'limit']:
                scores[MathDomain.CALCULUS] += 2
            elif op in ['solve', 'factor', 'expand', 'simplify']:
                scores[MathDomain.ALGEBRA] += 2

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
        print(f"\n[Problem Analysis Team] Processing: '{raw_input}'")

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
