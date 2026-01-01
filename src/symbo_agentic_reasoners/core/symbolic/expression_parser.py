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

Lexer and Parser for mathematical expressions.
NO SYMPY DEPENDENCY - Pure Python implementation.
"""

from __future__ import annotations
import logging
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Any, Union

from .type_system import Expr, Symbol, Integer, Float, _ensure_expr
from .composite_operations import Add, Mul, Pow
from .function_library import (
    Sin, Cos, Tan, Exp, Log, Sqrt, Abs, Sign, GenericFunction,
    Factorial, Gamma, Gcd, Floor, Ceil, Fraction
)

logger = logging.getLogger('symbo_agentic_reasoners.symbolic.parser')


# =============================================================================
# TOKEN TYPES
# =============================================================================

class TokenType(Enum):
    NUMBER = auto()
    SYMBOL = auto()
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDE = auto()
    POWER = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    FUNCTION = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Any


# =============================================================================
# LEXER
# =============================================================================

class Lexer:
    """Tokenizer for mathematical expressions."""

    FUNCTIONS = {
        'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
        'asin', 'acos', 'atan', 'acot', 'asec', 'acsc',
        'sinh', 'cosh', 'tanh', 'coth', 'sech', 'csch',
        'asinh', 'acosh', 'atanh',
        'exp', 'log', 'ln', 'sqrt', 'cbrt',
        'abs', 'sign', 'floor', 'ceil',
        'gamma', 'factorial',
        'gcd',  # Number theory
        'fraction', 'rational',  # Fraction constructors
        # Calculus operations
        'diff', 'integrate', 'limit', 'derivative',
    }

    def __init__(self, text: str):
        """Initialize lexer with mathematical expression text.

        Preprocesses the input by removing all whitespace characters for
        simpler tokenization.

        Args:
            text: Mathematical expression string (e.g., "sin(x**2) + 3*y")

        Example:
            >>> lexer = Lexer("2 * x + 1")
            >>> lexer.text
            '2*x+1'
        """
        self.text = text.replace(' ', '')
        self.pos = 0

    def peek(self) -> str:
        """Look ahead at current character without consuming it.

        Returns:
            Current character at position, or empty string if at end

        Example:
            >>> lexer = Lexer("abc")
            >>> lexer.peek()
            'a'
            >>> lexer.peek()  # Still 'a', not consumed
            'a'
        """
        if self.pos < len(self.text):
            return self.text[self.pos]
        return ''

    def advance(self) -> str:
        """Consume current character and advance position by 1.

        Returns:
            Character that was consumed

        Example:
            >>> lexer = Lexer("abc")
            >>> lexer.advance()
            'a'
            >>> lexer.advance()
            'b'
        """
        char = self.peek()
        self.pos += 1
        return char

    def tokenize(self) -> List[Token]:
        """Convert mathematical expression text into token stream.

        Main entry point for lexical analysis. Scans through the input text
        character by character, recognizing numbers, identifiers, operators,
        and punctuation.

        Returns:
            List of tokens ending with EOF token

        Raises:
            ValueError: If number parsing fails (malformed number)

        Example:
            >>> lexer = Lexer("sin(x**2)")
            >>> tokens = lexer.tokenize()
            >>> [t.type.name for t in tokens]
            ['FUNCTION', 'LPAREN', 'SYMBOL', 'POWER', 'NUMBER', 'RPAREN', 'EOF']

        Notes:
            - Recognizes operators: +, -, *, /, ^, **
            - Handles function names (sin, cos, exp, etc.)
            - Supports scientific notation (1.23e-4)
            - Unknown characters are silently skipped
        """
        tokens = []

        while self.pos < len(self.text):
            char = self.peek()

            if char.isdigit() or char == '.':
                tokens.append(self._read_number())
            elif char.isalpha() or char == '_':
                tokens.append(self._read_identifier())
            elif char == '+':
                tokens.append(Token(TokenType.PLUS, '+'))
                self.advance()
            elif char == '-':
                tokens.append(Token(TokenType.MINUS, '-'))
                self.advance()
            elif char == '*':
                self.advance()
                if self.peek() == '*':
                    self.advance()
                    tokens.append(Token(TokenType.POWER, '**'))
                else:
                    tokens.append(Token(TokenType.TIMES, '*'))
            elif char == '/':
                tokens.append(Token(TokenType.DIVIDE, '/'))
                self.advance()
            elif char == '^':
                tokens.append(Token(TokenType.POWER, '^'))
                self.advance()
            elif char == '(':
                tokens.append(Token(TokenType.LPAREN, '('))
                self.advance()
            elif char == ')':
                tokens.append(Token(TokenType.RPAREN, ')'))
                self.advance()
            elif char == ',':
                tokens.append(Token(TokenType.COMMA, ','))
                self.advance()
            else:
                self.advance()  # Skip unknown characters

        tokens.append(Token(TokenType.EOF, None))
        return tokens

    def _read_number(self) -> Token:
        """Parse numeric literal from current position.

        Recognizes integers, floating-point numbers, and scientific notation.
        Supports formats: 42, 3.14, 1.23e-4, 5E+2

        Returns:
            Token with NUMBER type and int or float value

        Example:
            >>> lexer = Lexer("3.14e-2")
            >>> token = lexer._read_number()
            >>> token.value
            0.0314
            >>> isinstance(token.value, float)
            True

        Notes:
            - Returns int if no decimal point or exponent
            - Returns float for decimals or scientific notation
            - Exponent can have optional +/- sign
            - Malformed numbers fall back to type inference
        """
        start = self.pos
        has_dot = False
        has_exp = False

        while self.pos < len(self.text):
            char = self.peek()
            if char.isdigit():
                self.advance()
            elif char == '.' and not has_dot and not has_exp:
                has_dot = True
                self.advance()
            elif char in ('e', 'E') and not has_exp:
                # Scientific notation
                has_exp = True
                self.advance()
                # Check for optional +/- after e
                if self.peek() in ('+', '-'):
                    self.advance()
            else:
                break

        value = self.text[start:self.pos]
        try:
            if has_dot or has_exp:
                return Token(TokenType.NUMBER, float(value))
            return Token(TokenType.NUMBER, int(value))
        except ValueError:
            # Fallback for malformed numbers
            return Token(TokenType.NUMBER, float(value) if '.' in value or 'e' in value.lower() else int(value))

    def _read_identifier(self) -> Token:
        """Parse identifier (symbol or function name) from current position.

        Reads alphanumeric characters and underscores. Classifies result as
        either a FUNCTION (if in FUNCTIONS set) or SYMBOL.

        Returns:
            Token with FUNCTION or SYMBOL type

        Example:
            >>> lexer = Lexer("sin")
            >>> token = lexer._read_identifier()
            >>> token.type.name
            'FUNCTION'
            >>> token.value
            'sin'

            >>> lexer = Lexer("x_1")
            >>> token = lexer._read_identifier()
            >>> token.type.name
            'SYMBOL'

        Notes:
            - Function names are case-insensitive (Sin → sin)
            - Supports underscores in identifiers
            - Recognized functions include: sin, cos, exp, log, sqrt, etc.
        """
        start = self.pos

        while self.pos < len(self.text):
            char = self.peek()
            if char.isalnum() or char == '_':
                self.advance()
            else:
                break

        name = self.text[start:self.pos]

        if name.lower() in self.FUNCTIONS:
            return Token(TokenType.FUNCTION, name.lower())

        return Token(TokenType.SYMBOL, name)


# =============================================================================
# PARSER
# =============================================================================

class Parser:
    """
    Recursive descent parser for mathematical expressions.

    Grammar:
        expr     -> term (('+' | '-') term)*
        term     -> power (('*' | '/') power)*
        power    -> unary ('^' | '**' unary)*
        unary    -> '-' unary | primary
        primary  -> NUMBER | SYMBOL | FUNCTION '(' args ')' | '(' expr ')'
        args     -> expr (',' expr)*
    """

    FUNCTION_MAP = {
        'sin': Sin, 'cos': Cos, 'tan': Tan,
        'exp': Exp, 'log': Log, 'ln': Log,
        'sqrt': Sqrt, 'abs': Abs, 'sign': Sign,
        'factorial': Factorial, 'gamma': Gamma,
        'gcd': Gcd, 'floor': Floor, 'ceil': Ceil,
        'fraction': Fraction, 'rational': Fraction,
    }

    def __init__(self, tokens: List[Token]):
        """Initialize parser with token stream from lexer.

        Args:
            tokens: List of tokens ending with EOF, from Lexer.tokenize()

        Example:
            >>> lexer = Lexer("x + 1")
            >>> tokens = lexer.tokenize()
            >>> parser = Parser(tokens)
            >>> parser.pos
            0
        """
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        """Look ahead at current token without consuming it.

        Returns:
            Current token at position, or EOF token if at end

        Example:
            >>> tokens = [Token(TokenType.NUMBER, 42), Token(TokenType.EOF, None)]
            >>> parser = Parser(tokens)
            >>> parser.peek().type.name
            'NUMBER'
            >>> parser.peek().type.name  # Still NUMBER, not consumed
            'NUMBER'
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, None)

    def advance(self) -> Token:
        """Consume current token and advance position by 1.

        Returns:
            Token that was consumed

        Example:
            >>> tokens = [Token(TokenType.NUMBER, 42), Token(TokenType.PLUS, '+'), Token(TokenType.EOF, None)]
            >>> parser = Parser(tokens)
            >>> parser.advance().value
            42
            >>> parser.advance().value
            '+'
        """
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Assert current token matches expected type, then consume it.

        Args:
            token_type: Expected token type (e.g., TokenType.LPAREN)

        Returns:
            Consumed token if type matches

        Raises:
            SyntaxError: If current token type doesn't match expected type

        Example:
            >>> tokens = [Token(TokenType.LPAREN, '('), Token(TokenType.EOF, None)]
            >>> parser = Parser(tokens)
            >>> parser.expect(TokenType.LPAREN).value
            '('
            >>> parser.expect(TokenType.RPAREN)  # SyntaxError: Expected RPAREN, got EOF
            Traceback (most recent call last):
                ...
            SyntaxError: Expected TokenType.RPAREN, got TokenType.EOF

        Notes:
            - Used for required punctuation (parentheses, commas)
            - More strict than advance() which doesn't validate type
        """
        token = self.advance()
        if token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {token.type}")
        return token

    def parse(self) -> Expr:
        """Parse complete expression and ensure no trailing tokens.

        Top-level entry point for parsing. Parses the full expression
        and verifies that all tokens were consumed (only EOF remains).

        Returns:
            Parsed expression tree

        Raises:
            SyntaxError: If tokens remain after parsing complete expression

        Example:
            >>> lexer = Lexer("2 + 3 * x")
            >>> parser = Parser(lexer.tokenize())
            >>> expr = parser.parse()
            >>> # Returns: Add(Integer(2), Mul(Integer(3), Symbol('x')))

        Notes:
            - Ensures entire input is parsed (no leftover tokens)
            - Delegates to parse_expr() for actual parsing
            - Simplifies result before returning
        """
        result = self.parse_expr()
        if self.peek().type != TokenType.EOF:
            raise SyntaxError(f"Unexpected token: {self.peek()}")
        return result

    def parse_expr(self) -> Expr:
        """Parse addition and subtraction expressions.

        Implements grammar rule: expr -> term (('+' | '-') term)*
        This is the lowest precedence level in the expression grammar.

        Returns:
            Expr: Parsed expression, potentially an Add node with multiple terms

        Example:
            >>> lexer = Lexer("a + b - c")
            >>> parser = Parser(lexer.tokenize())
            >>> expr = parser.parse_expr()
            >>> # Returns: Add(Symbol('a'), Symbol('b'), Mul(Integer(-1), Symbol('c')))

        Notes:
            - Left-associative: (a + b) + c not a + (b + c)
            - Subtraction converted to addition of negated term: a - b = a + (-1)*b
            - Delegates to parse_term() for higher precedence operations
            - Consumes all PLUS and MINUS tokens at this precedence level
        """
        left = self.parse_term()

        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.parse_term()
            if op.type == TokenType.PLUS:
                left = Add(left, right)
            else:
                left = Add(left, Mul(Integer(-1), right))

        return left

    def parse_term(self) -> Expr:
        """Parse multiplication and division expressions.

        Implements grammar rule: term -> power (('*' | '/') power)*
        This is the middle precedence level (higher than +/- but lower than ^).

        Returns:
            Expr: Parsed expression, potentially a Mul node with multiple factors

        Example:
            >>> lexer = Lexer("a * b / c")
            >>> parser = Parser(lexer.tokenize())
            >>> expr = parser.parse_term()
            >>> # Returns: Mul(Symbol('a'), Symbol('b'), Pow(Symbol('c'), Integer(-1)))

        Notes:
            - Left-associative: (a * b) * c not a * (b * c)
            - Division converted to multiplication by reciprocal: a / b = a * b^(-1)
            - Delegates to parse_power() for higher precedence (exponentiation)
            - Consumes all TIMES and DIVIDE tokens at this level
        """
        left = self.parse_power()

        while self.peek().type in (TokenType.TIMES, TokenType.DIVIDE):
            op = self.advance()
            right = self.parse_power()
            if op.type == TokenType.TIMES:
                left = Mul(left, right)
            else:
                left = Mul(left, Pow(right, Integer(-1)))

        return left

    def parse_power(self) -> Expr:
        """Parse exponentiation expressions.

        Implements grammar rule: power -> unary ('^' | '**' unary)*
        This is the highest precedence binary operator in the grammar.

        Returns:
            Expr: Parsed expression, potentially a Pow node

        Example:
            >>> lexer = Lexer("x^2^3")
            >>> parser = Parser(lexer.tokenize())
            >>> expr = parser.parse_power()
            >>> # Returns: Pow(Symbol('x'), Pow(Integer(2), Integer(3)))  [right-associative]

        Notes:
            - Right-associative: x^2^3 = x^(2^3) = x^8 not (x^2)^3 = x^6
            - Recursively calls parse_power() for exponent (right associativity)
            - Delegates to parse_unary() for unary minus and atoms
            - Accepts both ^ and ** operators
        """
        base = self.parse_unary()

        if self.peek().type == TokenType.POWER:
            self.advance()
            exp = self.parse_power()  # Right associative
            return Pow(base, exp)

        return base

    def parse_unary(self) -> Expr:
        """Parse unary minus operator.

        Implements grammar rule: unary -> '-' unary | primary
        Handles prefix negation with right-to-left associativity.

        Returns:
            Expr: Negated expression or primary expression

        Example:
            >>> lexer = Lexer("--x")
            >>> parser = Parser(lexer.tokenize())
            >>> expr = parser.parse_unary()
            >>> # Returns: Mul(Integer(-1), Mul(Integer(-1), Symbol('x')))  [double negation]

        Notes:
            - Right-associative for multiple negations: --x = -(-x)
            - Negation represented as multiplication by -1
            - Delegates to parse_primary() for atoms (numbers, symbols, functions)
            - No unary plus operator (would be identity operation)
        """
        if self.peek().type == TokenType.MINUS:
            self.advance()
            return Mul(Integer(-1), self.parse_unary())

        return self.parse_primary()

    def parse_primary(self) -> Expr:
        """Parse atomic expressions (numbers, symbols, functions, parentheses).

        Implements grammar rule: primary -> NUMBER | SYMBOL | FUNCTION '(' args ')' | '(' expr ')'
        This is the highest precedence level, parsing indivisible units.

        Returns:
            Expr: Integer, Float, Symbol, function call, or parenthesized subexpression

        Raises:
            SyntaxError: If token doesn't match any primary production

        Example:
            >>> lexer = Lexer("sin(x)")
            >>> parser = Parser(lexer.tokenize())
            >>> expr = parser.parse_primary()
            >>> # Returns: Sin(Symbol('x'))

            >>> lexer = Lexer("(2 + 3)")
            >>> parser = Parser(lexer.tokenize())
            >>> expr = parser.parse_primary()
            >>> # Returns: Add(Integer(2), Integer(3))

        Notes:
            - NUMBER tokens become Integer or Float nodes
            - SYMBOL tokens become Symbol nodes
            - FUNCTION tokens parse arguments and create function nodes
            - Parentheses allow arbitrary expression nesting
            - Special handling for implicit multiplication: x(y) = x * y
            - Calculus operations (diff, integrate, limit) handled specially
        """
        token = self.peek()

        if token.type == TokenType.NUMBER:
            self.advance()
            if isinstance(token.value, int):
                return Integer(token.value)
            return Float(token.value)

        if token.type == TokenType.SYMBOL:
            self.advance()
            # Check for implicit multiplication: x(...)
            if self.peek().type == TokenType.LPAREN:
                # Could be function application or multiplication
                # For now, treat single-letter as multiplication
                if len(token.value) == 1:
                    self.advance()  # consume (
                    arg = self.parse_expr()
                    self.expect(TokenType.RPAREN)
                    return Mul(Symbol(token.value), arg)
            return Symbol(token.value)

        if token.type == TokenType.FUNCTION:
            self.advance()
            self.expect(TokenType.LPAREN)
            args = self.parse_args()
            self.expect(TokenType.RPAREN)

            func_class = self.FUNCTION_MAP.get(token.value)
            if func_class:
                return func_class(*args)

            # Special handling for calculus operations
            if token.value in ('diff', 'derivative'):
                if len(args) >= 2:
                    expr = args[0]
                    var = args[1]
                    if hasattr(expr, 'diff'):
                        return expr.diff(var)
                return GenericFunction('diff', *args)

            if token.value == 'integrate':
                # Return unevaluated integral representation
                return GenericFunction('integrate', *args)

            if token.value == 'limit':
                # Return unevaluated limit representation
                return GenericFunction('limit', *args)

            # Unknown function - create generic
            return GenericFunction(token.value, *args)

        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return expr

        raise SyntaxError(f"Unexpected token: {token}")

    def parse_args(self) -> List[Expr]:
        """Parse comma-separated function arguments.

        Implements grammar rule: args -> expr (',' expr)*
        Used for multi-argument functions like gcd(a, b) or diff(f, x).

        Returns:
            List of parsed expressions (at least one)

        Example:
            >>> lexer = Lexer("gcd(12, 18)")
            >>> parser = Parser(lexer.tokenize())
            >>> parser.advance()  # consume 'gcd'
            Token(type=<TokenType.FUNCTION: 11>, value='gcd')
            >>> parser.advance()  # consume '('
            Token(type=<TokenType.LPAREN: 8>, value='(')
            >>> args = parser.parse_args()
            >>> # Returns: [Integer(12), Integer(18)]

        Notes:
            - Always parses at least one expression
            - Each argument is a full expression (can contain operators)
            - Stops at closing parenthesis or end of token stream
            - Used by parse_primary() for function call parsing
        """
        args = [self.parse_expr()]

        while self.peek().type == TokenType.COMMA:
            self.advance()
            args.append(self.parse_expr())

        return args


# =============================================================================
# PUBLIC API
# =============================================================================

def parse_expr(text: str) -> Expr:
    """
    Parse a mathematical expression string into an Expr.

    This replaces sympy.sympify and sympy.parsing.parse_expr.
    """
    if not text or not text.strip():
        return Integer(0)

    try:
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser.parse().simplify()
    except Exception as e:
        logger.warning(f"Failed to parse '{text}': {e}")
        raise ValueError(f"Failed to parse expression: {text}") from e


def sympify(obj: Any) -> Expr:
    """
    Convert object to Expr.

    This replaces sympy.sympify.
    """
    return _ensure_expr(obj)


__all__ = [
    'Lexer',
    'Parser',
    'TokenType',
    'Token',
    'parse_expr',
    'sympify',
]
