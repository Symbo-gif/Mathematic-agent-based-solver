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
PHASE 0 - STEP 1: The Semantic Substrate (Lingua Franca)
=========================================================

OMDoc (Open Mathematical Documents) and OpenMath Standards Implementation

PURPOSE:
-------
Eliminates natural language ambiguity by providing a three-layer semantic encoding
system that transforms ambiguous text into precise mathematical objects.

REFERENCE:
---------
- Phase_0_Build_Order_Breakdown.md: Step 1 (Lines 32-105)
- Phase 0 Coding Strategy: Section 4.1 "The Lingua Franca: OMDoc for Semantic Precision"

ARCHITECTURE:
------------
Three-Layer Implementation:
  1. Object Level: Encodes formulae with specific variables and operations (x² + y, sin(θ))
  2. Statement Level: Encodes definitions, theorems, proofs as distinct entities
  3. Theory Level: Encodes modular mathematical theories providing context

WHY THIS MATTERS:
----------------
Raw text or LaTeX conveys *presentation* (how it looks) rather than *content* (what it means).
The string "x²" lacks true semantic meaning. OMDoc ensures that a "derivative" is understood
as a mathematical operator with specific semantics, not merely a text string.

Without this lingua franca, we risk a "Tower of Babel" scenario where capable agents
exist in isolation, unable to transmit mathematical semantic nuance.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum
import xml.etree.ElementTree as ET
import json


class MathOperator(Enum):
    """
    OpenMath Content Dictionary Operators

    Maps mathematical operations to their OpenMath Content Dictionary identifiers.
    Format: 'cd.symbol' where cd = Content Dictionary, symbol = operation name

    Reference: OpenMath Content Dictionaries (arith1, calculus1, transc1, etc.)
    """
    # Arithmetic operations (arith1 Content Dictionary)
    PLUS = 'arith1.plus'
    MINUS = 'arith1.minus'
    TIMES = 'arith1.times'
    DIVIDE = 'arith1.divide'
    POWER = 'arith1.power'
    ROOT = 'arith1.root'
    ABS = 'arith1.abs'
    UNARY_MINUS = 'arith1.unary_minus'

    # Calculus operations (calculus1 Content Dictionary)
    DIFF = 'calculus1.diff'              # Differentiation
    INT = 'calculus1.int'                # Indefinite integral
    DEFINT = 'calculus1.defint'          # Definite integral
    PARTIALDIFF = 'calculus1.partialdiff'  # Partial derivative

    # Transcendental functions (transc1 Content Dictionary)
    SIN = 'transc1.sin'
    COS = 'transc1.cos'
    TAN = 'transc1.tan'
    ARCSIN = 'transc1.arcsin'
    ARCCOS = 'transc1.arccos'
    ARCTAN = 'transc1.arctan'
    EXP = 'transc1.exp'
    LN = 'transc1.ln'
    LOG = 'transc1.log'

    # Logic operations (logic1 Content Dictionary)
    AND = 'logic1.and'
    OR = 'logic1.or'
    NOT = 'logic1.not'
    IMPLIES = 'logic1.implies'
    EQUIVALENT = 'logic1.equivalent'

    # Relation operations (relation1 Content Dictionary)
    EQ = 'relation1.eq'
    NEQ = 'relation1.neq'
    LT = 'relation1.lt'
    GT = 'relation1.gt'
    LE = 'relation1.le'
    GE = 'relation1.ge'


@dataclass
class OMObject:
    """
    OBJECT LEVEL: Mathematical expression tree

    Represents a single mathematical object with semantic meaning.
    Can be a variable (x), a value (5), or an operation (x² represented as POWER(x, 2)).

    EXAMPLES:
    --------
    - Variable x: OMObject(variable='x')
    - Integer 5: OMObject(value=5)
    - Expression x²: OMObject(operator=MathOperator.POWER,
                              operands=[OMObject(variable='x'), OMObject(value=2)])
    - Expression x² + y: OMObject(operator=MathOperator.PLUS,
                                   operands=[
                                       OMObject(operator=MathOperator.POWER,
                                               operands=[OMObject(variable='x'), OMObject(value=2)]),
                                       OMObject(variable='y')
                                   ])

    REFERENCE:
    ---------
    Phase_0_Build_Order_Breakdown.md: Lines 66-88
    """
    operator: Optional[MathOperator] = None
    operands: List['OMObject'] = field(default_factory=list)
    variable: Optional[str] = None
    value: Optional[Union[int, float, str]] = None

    def to_openmath_xml(self) -> ET.Element:
        """
        Serialize to OpenMath XML format

        OpenMath XML Elements:
        - OMV: Variable (e.g., <OMV name="x"/>)
        - OMI: Integer (e.g., <OMI>5</OMI>)
        - OMF: Float (e.g., <OMF dec="3.14"/>)
        - OMS: Symbol from Content Dictionary (e.g., <OMS cd="arith1" name="plus"/>)
        - OMA: Application of operator to operands

        Returns:
            ET.Element: OpenMath XML element
        """
        if self.variable:
            return ET.Element('OMV', name=self.variable)
        elif self.value is not None:
            if isinstance(self.value, int):
                elem = ET.Element('OMI')
                elem.text = str(self.value)
            elif isinstance(self.value, float):
                elem = ET.Element('OMF', dec=str(self.value))
            else:  # String value
                elem = ET.Element('OMSTR')
                elem.text = str(self.value)
            return elem
        elif self.operator:
            # OMA = OpenMath Application
            oma = ET.Element('OMA')
            cd, name = self.operator.value.split('.')
            oma.append(ET.Element('OMS', cd=cd, name=name))
            for op in self.operands:
                oma.append(op.to_openmath_xml())
            return oma
        else:
            raise ValueError("OMObject must have either variable, value, or operator")

    def to_xml_string(self) -> str:
        """Convert to XML string representation"""
        return ET.tostring(self.to_openmath_xml(), encoding='unicode')

    def serialize(self) -> dict:
        """
        Serialize to JSON-compatible dictionary for FIPA-ACL transmission

        Returns:
            dict: JSON-serializable representation
        """
        result = {}
        if self.operator:
            result['operator'] = self.operator.value
            result['operands'] = [op.serialize() for op in self.operands]
        if self.variable:
            result['variable'] = self.variable
        if self.value is not None:
            result['value'] = self.value
        return result

    @classmethod
    def deserialize(cls, data: dict) -> 'OMObject':
        """
        Deserialize from JSON-compatible dictionary

        Args:
            data: Dictionary representation of OMObject

        Returns:
            OMObject: Reconstructed OMObject
        """
        if 'operator' in data:
            operator = MathOperator(data['operator'])
            operands = [cls.deserialize(op) for op in data.get('operands', [])]
            return cls(operator=operator, operands=operands)
        elif 'variable' in data:
            return cls(variable=data['variable'])
        elif 'value' in data:
            return cls(value=data['value'])
        else:
            raise ValueError("Invalid OMObject serialization")

    def __repr__(self) -> str:
        """Human-readable representation"""
        if self.variable:
            return f"Var({self.variable})"
        elif self.value is not None:
            return f"Val({self.value})"
        elif self.operator:
            ops_repr = ', '.join(repr(op) for op in self.operands)
            return f"{self.operator.name}({ops_repr})"
        return "OMObject(empty)"


@dataclass
class OMDocStatement:
    """
    STATEMENT LEVEL: Theorem, Definition, Proof, Axiom

    Encodes mathematical statements as distinct logical entities with verifiable meaning.
    Statements have types (theorem, definition, proof, axiom) and belong to a theory context.

    EXAMPLES:
    --------
    - Theorem: Infinitude of Primes
    - Definition: Continuity of a function
    - Axiom: Parallel Postulate
    - Proof: Proof that sqrt(2) is irrational

    FIELDS:
    ------
    - statement_type: Type of statement ('theorem', 'definition', 'proof', 'axiom', 'lemma')
    - name: Unique identifier for the statement
    - content: The mathematical content as an OMObject
    - theory_context: Reference to the Theory this statement belongs to
    - dependencies: List of statement names this depends on
    - metadata: Additional information (author, date, tags, etc.)

    REFERENCE:
    ---------
    Phase_0_Build_Order_Breakdown.md: Lines 90-97
    """
    statement_type: str  # 'theorem', 'definition', 'proof', 'axiom', 'lemma'
    name: str
    content: OMObject
    theory_context: str  # Reference to Theory Level (e.g., 'GroupTheory', 'Calculus')
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def serialize(self) -> dict:
        """Serialize to JSON-compatible dictionary"""
        return {
            'statement_type': self.statement_type,
            'name': self.name,
            'content': self.content.serialize(),
            'theory_context': self.theory_context,
            'dependencies': self.dependencies,
            'metadata': self.metadata
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'OMDocStatement':
        """Deserialize from JSON-compatible dictionary"""
        return cls(
            statement_type=data['statement_type'],
            name=data['name'],
            content=OMObject.deserialize(data['content']),
            theory_context=data['theory_context'],
            dependencies=data.get('dependencies', []),
            metadata=data.get('metadata', {})
        )

    def __repr__(self) -> str:
        """Human-readable representation"""
        return f"{self.statement_type.upper()}[{self.name}] in {self.theory_context}"


@dataclass
class OMDocTheory:
    """
    THEORY LEVEL: Modular mathematical context

    Encodes modular mathematical theories that provide context for statements and objects.
    Theories can import other theories, creating a hierarchy of mathematical knowledge.

    EXAMPLES:
    --------
    - Theory: GroupTheory (imports: SetTheory)
    - Theory: Calculus (imports: RealAnalysis)
    - Theory: LinearAlgebra (imports: VectorSpaces)

    FIELDS:
    ------
    - name: Unique theory identifier
    - imports: List of other theory names this theory depends on
    - statements: List of OMDocStatements defined in this theory
    - symbols: Dictionary of named OMObjects specific to this theory
    - metadata: Additional information (description, author, version, etc.)

    REFERENCE:
    ---------
    Phase_0_Build_Order_Breakdown.md: Lines 99-105
    """
    name: str  # e.g., 'GroupTheory', 'Calculus', 'LinearAlgebra'
    imports: List[str] = field(default_factory=list)
    statements: List[OMDocStatement] = field(default_factory=list)
    symbols: Dict[str, OMObject] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)

    def add_statement(self, statement: OMDocStatement):
        """Add a statement to this theory"""
        if statement.theory_context != self.name:
            raise ValueError(f"Statement belongs to {statement.theory_context}, not {self.name}")
        self.statements.append(statement)

    def add_symbol(self, name: str, obj: OMObject):
        """Add a named symbol to this theory"""
        self.symbols[name] = obj

    def serialize(self) -> dict:
        """Serialize to JSON-compatible dictionary"""
        return {
            'name': self.name,
            'imports': self.imports,
            'statements': [stmt.serialize() for stmt in self.statements],
            'symbols': {name: obj.serialize() for name, obj in self.symbols.items()},
            'metadata': self.metadata
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'OMDocTheory':
        """Deserialize from JSON-compatible dictionary"""
        theory = cls(
            name=data['name'],
            imports=data.get('imports', []),
            metadata=data.get('metadata', {})
        )
        theory.statements = [OMDocStatement.deserialize(stmt) for stmt in data.get('statements', [])]
        theory.symbols = {name: OMObject.deserialize(obj) for name, obj in data.get('symbols', {}).items()}
        return theory

    def __repr__(self) -> str:
        """Human-readable representation"""
        imports_str = f", imports: {self.imports}" if self.imports else ""
        return f"Theory[{self.name}](statements={len(self.statements)}, symbols={len(self.symbols)}{imports_str})"


class OMDocBuilder:
    """
    Builder pattern for constructing OMDoc mathematical objects

    Provides a fluent interface for creating mathematical expressions
    without needing to directly manipulate OMObject instances.

    USAGE:
    -----
    builder = OMDocBuilder()
    expr = builder.create_apply("Plus", [
        builder.create_variable("x"),
        builder.create_integer(1)
    ])
    # Creates: x + 1

    REFERENCE:
    ---------
    Phase_0_Build_Order_Breakdown.md: OMDoc construction utilities
    """

    # Mapping from friendly names to MathOperator enum values
    OPERATOR_MAP = {
        # Arithmetic
        'Plus': MathOperator.PLUS,
        'Minus': MathOperator.MINUS,
        'Times': MathOperator.TIMES,
        'Divide': MathOperator.DIVIDE,
        'Power': MathOperator.POWER,
        'Root': MathOperator.ROOT,
        'Abs': MathOperator.ABS,
        'UnaryMinus': MathOperator.UNARY_MINUS,
        # Calculus
        'Diff': MathOperator.DIFF,
        'Int': MathOperator.INT,
        'DefInt': MathOperator.DEFINT,
        'PartialDiff': MathOperator.PARTIALDIFF,
        # Transcendental
        'Sin': MathOperator.SIN,
        'Cos': MathOperator.COS,
        'Tan': MathOperator.TAN,
        'ArcSin': MathOperator.ARCSIN,
        'ArcCos': MathOperator.ARCCOS,
        'ArcTan': MathOperator.ARCTAN,
        'Exp': MathOperator.EXP,
        'Ln': MathOperator.LN,
        'Log': MathOperator.LOG,
        # Logic
        'And': MathOperator.AND,
        'Or': MathOperator.OR,
        'Not': MathOperator.NOT,
        'Implies': MathOperator.IMPLIES,
        'Equivalent': MathOperator.EQUIVALENT,
        # Relations
        'Eq': MathOperator.EQ,
        'Neq': MathOperator.NEQ,
        'Lt': MathOperator.LT,
        'Gt': MathOperator.GT,
        'Le': MathOperator.LE,
        'Ge': MathOperator.GE,
    }

    def create_variable(self, name: str) -> OMObject:
        """
        Create a variable OMObject

        Args:
            name: Variable name (e.g., 'x', 'y', 'theta')

        Returns:
            OMObject representing the variable
        """
        return OMObject(variable=name)

    def create_integer(self, value: int) -> OMObject:
        """
        Create an integer OMObject

        Args:
            value: Integer value

        Returns:
            OMObject representing the integer
        """
        return OMObject(value=value)

    def create_float(self, value: float) -> OMObject:
        """
        Create a float OMObject

        Args:
            value: Float value

        Returns:
            OMObject representing the float
        """
        return OMObject(value=value)

    def create_string(self, value: str) -> OMObject:
        """
        Create a string OMObject

        Args:
            value: String value

        Returns:
            OMObject representing the string
        """
        return OMObject(value=value)

    def create_apply(self, operator_name: str, operands: List[OMObject]) -> OMObject:
        """
        Create an operation application OMObject

        Args:
            operator_name: Name of the operator (e.g., 'Plus', 'Times', 'Diff')
            operands: List of OMObject operands

        Returns:
            OMObject representing the operation application

        Raises:
            ValueError: If operator_name is not recognized
        """
        if operator_name not in self.OPERATOR_MAP:
            raise ValueError(
                f"Unknown operator: {operator_name}. "
                f"Available operators: {list(self.OPERATOR_MAP.keys())}"
            )
        return OMObject(
            operator=self.OPERATOR_MAP[operator_name],
            operands=operands
        )

    def create_statement(
        self,
        statement_type: str,
        name: str,
        content: OMObject,
        theory_context: str,
        dependencies: List[str] = None,
        metadata: Dict[str, str] = None
    ) -> OMDocStatement:
        """
        Create an OMDoc statement (theorem, definition, etc.)

        Args:
            statement_type: Type ('theorem', 'definition', 'proof', 'axiom', 'lemma')
            name: Unique statement name
            content: Mathematical content as OMObject
            theory_context: Theory this belongs to
            dependencies: Optional list of dependency names
            metadata: Optional metadata dictionary

        Returns:
            OMDocStatement instance
        """
        return OMDocStatement(
            statement_type=statement_type,
            name=name,
            content=content,
            theory_context=theory_context,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )

    def create_theory(
        self,
        name: str,
        imports: List[str] = None,
        metadata: Dict[str, str] = None
    ) -> OMDocTheory:
        """
        Create an OMDoc theory

        Args:
            name: Theory name
            imports: Optional list of imported theory names
            metadata: Optional metadata dictionary

        Returns:
            OMDocTheory instance
        """
        return OMDocTheory(
            name=name,
            imports=imports or [],
            metadata=metadata or {}
        )


# Helper functions for common mathematical constructions

def create_variable(name: str) -> OMObject:
    """Helper: Create a variable OMObject"""
    return OMObject(variable=name)


def create_number(value: Union[int, float]) -> OMObject:
    """Helper: Create a numeric OMObject"""
    return OMObject(value=value)


def create_operation(operator: MathOperator, *operands: OMObject) -> OMObject:
    """Helper: Create an operation OMObject"""
    return OMObject(operator=operator, operands=list(operands))


# Example constructions for testing and demonstration

def example_polynomial() -> OMObject:
    """
    Example: Create x² + 2x + 1

    Returns:
        OMObject representing (x²) + (2x) + 1
    """
    x = create_variable('x')
    x_squared = create_operation(MathOperator.POWER, x, create_number(2))
    two_x = create_operation(MathOperator.TIMES, create_number(2), x)
    return create_operation(MathOperator.PLUS,
                           create_operation(MathOperator.PLUS, x_squared, two_x),
                           create_number(1))


def example_derivative() -> OMObject:
    """
    Example: Create d/dx(sin(x))

    Returns:
        OMObject representing derivative of sin(x) with respect to x
    """
    x = create_variable('x')
    sin_x = create_operation(MathOperator.SIN, x)
    return create_operation(MathOperator.DIFF, sin_x, x)


def example_integral() -> OMObject:
    """
    Example: Create ∫x² dx

    Returns:
        OMObject representing indefinite integral of x²
    """
    x = create_variable('x')
    x_squared = create_operation(MathOperator.POWER, x, create_number(2))
    return create_operation(MathOperator.INT, x_squared, x)


if __name__ == "__main__":
    """Demonstration of OMDoc functionality"""
    print("=" * 80)
    print("PHASE 0 - STEP 1: OMDoc/OpenMath Semantic Substrate")
    print("=" * 80)
    print()

    # Example 1: Simple polynomial
    print("Example 1: Polynomial x² + 2x + 1")
    poly = example_polynomial()
    print(f"  Representation: {poly}")
    print(f"  Serialized: {json.dumps(poly.serialize(), indent=2)}")
    print()

    # Example 2: Derivative
    print("Example 2: Derivative d/dx(sin(x))")
    deriv = example_derivative()
    print(f"  Representation: {deriv}")
    print(f"  OpenMath XML: {deriv.to_xml_string()}")
    print()

    # Example 3: Statement
    print("Example 3: Theorem Statement")
    pythagorean = OMDocStatement(
        statement_type='theorem',
        name='pythagorean_theorem',
        content=create_variable('a²+b²=c²'),  # Simplified for demo
        theory_context='Geometry',
        dependencies=['euclidean_axioms'],
        metadata={'author': 'Pythagoras', 'importance': 'high'}
    )
    print(f"  {pythagorean}")
    print()

    # Example 4: Theory
    print("Example 4: Mathematical Theory")
    calculus_theory = OMDocTheory(
        name='BasicCalculus',
        imports=['RealAnalysis'],
        metadata={'description': 'Fundamental calculus operations'}
    )
    calculus_theory.add_symbol('derivative_operator', create_operation(MathOperator.DIFF,
                                                                        create_variable('f'),
                                                                        create_variable('x')))
    print(f"  {calculus_theory}")
    print()

    print("✓ OMDoc Semantic Substrate implementation complete")
    print("  - Object Level: Mathematical expressions ✓")
    print("  - Statement Level: Theorems, definitions, proofs ✓")
    print("  - Theory Level: Modular mathematical contexts ✓")
