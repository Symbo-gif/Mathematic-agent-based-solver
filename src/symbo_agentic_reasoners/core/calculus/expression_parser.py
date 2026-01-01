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
Expression Parser - String to AST Conversion
=============================================

Parses mathematical string expressions into internal AST representation.

Supports:
- Numbers (int, float)
- Symbols (variables like x, y, z)
- Binary operators: +, -, *, /, **, ^
- Unary operators: - (negation)
- Parentheses for grouping
- Function calls: sin(x), cos(x), exp(x), etc.
- Special constants: pi, E
"""

import logging
from typing import Optional, List, Tuple
from .ast_types import (
    Expr, Num, Sym, Add, Mul, Pow, Neg, Func,
    add, mul, power, neg,
    PI, E
)

logger = logging.getLogger(__name__)


class ExprParser:
    """
    Parse mathematical string to AST.

    Supports: numbers, symbols, +, -, *, /, **, parentheses, functions
    """

    # Operator precedence (higher = binds tighter)
    PRECEDENCE = {
        '+': 1, '-': 1,
        '*': 2, '/': 2,
        '^': 3, '**': 3,
        'unary-': 4,
    }

    # Known functions
    FUNCTIONS = {
        'sin', 'cos', 'tan', 'sec', 'csc', 'cot',
        'asin', 'acos', 'atan',
        'sinh', 'cosh', 'tanh',
        'exp', 'ln', 'log', 'sqrt', 'cbrt',
        'Abs', 'abs',
    }

    def parse(self, text: str) -> Optional[Expr]:
        """Parse string to AST."""
        try:
            tokens = self._tokenize(text)
            expr, pos = self._parse_expr(tokens, 0)
            return expr
        except Exception as e:
            logger.debug(f"Parse failed for '{text}': {e}")
            return None

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize input string."""
        tokens = []
        i = 0
        text = text.strip()

        while i < len(text):
            c = text[i]

            # Skip whitespace
            if c.isspace():
                i += 1
                continue

            # Number (including decimals)
            if c.isdigit() or (c == '.' and i + 1 < len(text) and text[i + 1].isdigit()):
                j = i
                while j < len(text) and (text[j].isdigit() or text[j] == '.'):
                    j += 1
                tokens.append(text[i:j])
                i = j
                continue

            # Identifier (symbol or function)
            if c.isalpha() or c == '_':
                j = i
                while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                    j += 1
                tokens.append(text[i:j])
                i = j
                continue

            # ** operator
            if c == '*' and i + 1 < len(text) and text[i + 1] == '*':
                tokens.append('**')
                i += 2
                continue

            # Single character operators and parens
            if c in '+-*/^()':
                tokens.append(c)
                i += 1
                continue

            # Skip unknown characters
            i += 1

        return tokens

    def _parse_expr(self, tokens: List[str], pos: int, min_prec: int = 0) -> Tuple[Expr, int]:
        """Parse expression using precedence climbing."""
        left, pos = self._parse_atom(tokens, pos)

        while pos < len(tokens):
            op = tokens[pos]
            if op not in self.PRECEDENCE or self.PRECEDENCE[op] < min_prec:
                break

            prec = self.PRECEDENCE[op]
            pos += 1

            # Right associative for **
            next_min_prec = prec + 1 if op in ('^', '**') else prec

            right, pos = self._parse_expr(tokens, pos, next_min_prec)

            # Build AST node
            if op in ('+',):
                left = add(left, right)
            elif op == '-':
                left = add(left, neg(right))
            elif op == '*':
                left = mul(left, right)
            elif op == '/':
                left = mul(left, power(right, Num(-1)))
            elif op in ('^', '**'):
                left = power(left, right)

        return left, pos

    def _parse_atom(self, tokens: List[str], pos: int) -> Tuple[Expr, int]:
        """Parse atomic expression (number, symbol, function, parenthesized)."""
        if pos >= len(tokens):
            raise ValueError("Unexpected end of expression")

        token = tokens[pos]

        # Unary minus
        if token == '-':
            expr, pos = self._parse_atom(tokens, pos + 1)
            return neg(expr), pos

        # Unary plus (ignore)
        if token == '+':
            return self._parse_atom(tokens, pos + 1)

        # Parenthesized expression
        if token == '(':
            expr, pos = self._parse_expr(tokens, pos + 1)
            if pos < len(tokens) and tokens[pos] == ')':
                pos += 1
            return expr, pos

        # Number
        if token[0].isdigit() or token[0] == '.':
            if '.' in token:
                return Num(float(token)), pos + 1
            else:
                return Num(int(token)), pos + 1

        # Function call or symbol
        if token[0].isalpha():
            # Check if function call
            if pos + 1 < len(tokens) and tokens[pos + 1] == '(':
                fname = token
                pos += 2  # skip name and (
                arg, pos = self._parse_expr(tokens, pos)
                if pos < len(tokens) and tokens[pos] == ')':
                    pos += 1
                return Func(fname, arg), pos
            else:
                # Symbol (including constants)
                if token == 'pi':
                    return PI, pos + 1
                elif token in ('E', 'e'):
                    return E, pos + 1
                else:
                    return Sym(token), pos + 1

        raise ValueError(f"Unexpected token: {token}")
