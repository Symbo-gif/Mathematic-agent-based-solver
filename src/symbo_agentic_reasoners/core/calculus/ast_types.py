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
AST Type Definitions for Native Calculus Engine
================================================

This module defines the internal Abstract Syntax Tree (AST) representation
used throughout the calculus engine. All AST nodes are immutable dataclasses.

Node Types:
----------
- Num: Numeric constants (int, float, Fraction)
- Sym: Symbolic variables (e.g., 'x', 'y', 'pi')
- Add: Sum of expressions
- Mul: Product of expressions
- Pow: Power expression (base^exponent)
- Neg: Negation
- Func: Function application (e.g., sin(x), exp(x))
"""

from dataclasses import dataclass
from typing import Union, List
from fractions import Fraction
from enum import Enum, auto


class NodeType(Enum):
    """Types of AST nodes."""
    NUMBER = auto()
    SYMBOL = auto()
    ADD = auto()
    MUL = auto()
    POW = auto()
    NEG = auto()
    FUNC = auto()


@dataclass
class Expr:
    """Base expression node."""
    pass


@dataclass
class Num(Expr):
    """Numeric constant."""
    value: Union[int, float, Fraction]

    def __str__(self):
        if isinstance(self.value, Fraction):
            if self.value.denominator == 1:
                return str(self.value.numerator)
            return f"({self.value.numerator}/{self.value.denominator})"
        if isinstance(self.value, float) and self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, Num):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)


@dataclass
class Sym(Expr):
    """Symbol (variable)."""
    name: str

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Sym):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)


@dataclass
class Add(Expr):
    """Sum of expressions."""
    terms: List[Expr]

    def __str__(self):
        if not self.terms:
            return "0"
        result = str(self.terms[0])
        for term in self.terms[1:]:
            s = str(term)
            if s.startswith('-'):
                result += f" - {s[1:]}"
            else:
                result += f" + {s}"
        return result

    def __eq__(self, other):
        if isinstance(other, Add):
            return self.terms == other.terms
        return False

    def __hash__(self):
        return hash(tuple(self.terms))


@dataclass
class Mul(Expr):
    """Product of expressions."""
    factors: List[Expr]

    def __str__(self):
        if not self.factors:
            return "1"
        parts = []
        for f in self.factors:
            s = str(f)
            if isinstance(f, Add) and len(f.terms) > 1:
                s = f"({s})"
            parts.append(s)
        return "*".join(parts)

    def __eq__(self, other):
        if isinstance(other, Mul):
            return self.factors == other.factors
        return False

    def __hash__(self):
        return hash(tuple(self.factors))


@dataclass
class Pow(Expr):
    """Power expression: base^exponent."""
    base: Expr
    exp: Expr

    def __str__(self):
        base_str = str(self.base)
        exp_str = str(self.exp)
        if isinstance(self.base, (Add, Mul)):
            base_str = f"({base_str})"
        if isinstance(self.exp, (Add, Mul, Pow)):
            exp_str = f"({exp_str})"
        return f"{base_str}**{exp_str}"

    def __eq__(self, other):
        if isinstance(other, Pow):
            return self.base == other.base and self.exp == other.exp
        return False

    def __hash__(self):
        return hash((self.base, self.exp))


@dataclass
class Neg(Expr):
    """Negation."""
    arg: Expr

    def __str__(self):
        s = str(self.arg)
        if isinstance(self.arg, (Add, Mul)):
            return f"-({s})"
        return f"-{s}"

    def __eq__(self, other):
        if isinstance(other, Neg):
            return self.arg == other.arg
        return False

    def __hash__(self):
        return hash(self.arg)


@dataclass
class Func(Expr):
    """Function call: name(arg)."""
    name: str
    arg: Expr

    def __str__(self):
        return f"{self.name}({self.arg})"

    def __eq__(self, other):
        if isinstance(other, Func):
            return self.name == other.name and self.arg == other.arg
        return False

    def __hash__(self):
        return hash((self.name, self.arg))


# Special constants
PI = Sym('pi')
E = Sym('E')


# =============================================================================
# AST CONSTRUCTORS (convenience)
# =============================================================================

def num(n: Union[int, float, Fraction]) -> Num:
    """Create a number node."""
    return Num(n)


def sym(name: str) -> Sym:
    """Create a symbol node."""
    return Sym(name)


def add(*terms: Expr) -> Expr:
    """Create a sum, simplifying if possible."""
    flat = []
    for t in terms:
        if isinstance(t, Add):
            flat.extend(t.terms)
        elif isinstance(t, Num) and t.value == 0:
            continue
        else:
            flat.append(t)
    if not flat:
        return Num(0)
    if len(flat) == 1:
        return flat[0]
    return Add(flat)


def mul(*factors: Expr) -> Expr:
    """Create a product, simplifying if possible."""
    flat = []
    coeff = 1
    for f in factors:
        if isinstance(f, Mul):
            flat.extend(f.factors)
        elif isinstance(f, Num):
            coeff *= f.value
        else:
            flat.append(f)

    if coeff == 0:
        return Num(0)
    if coeff != 1:
        flat.insert(0, Num(coeff))

    if not flat:
        return Num(1)
    if len(flat) == 1:
        return flat[0]
    return Mul(flat)


def power(base: Expr, exp: Expr) -> Expr:
    """Create a power, simplifying if possible."""
    if isinstance(exp, Num) and exp.value == 0:
        return Num(1)
    if isinstance(exp, Num) and exp.value == 1:
        return base
    if isinstance(base, Num) and base.value == 0:
        return Num(0)
    if isinstance(base, Num) and base.value == 1:
        return Num(1)
    return Pow(base, exp)


def neg(expr: Expr) -> Expr:
    """Create a negation."""
    if isinstance(expr, Num):
        return Num(-expr.value)
    if isinstance(expr, Neg):
        return expr.arg
    return Neg(expr)


def func(name: str, arg: Expr) -> Func:
    """Create a function call."""
    return Func(name, arg)
