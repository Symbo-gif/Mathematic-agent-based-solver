# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0

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
        self.text = text.replace(' ', '')
        self.pos = 0

    def peek(self) -> str:
        if self.pos < len(self.text):
            return self.text[self.pos]
        return ''

    def advance(self) -> str:
        char = self.peek()
        self.pos += 1
        return char

    def tokenize(self) -> List[Token]:
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
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, None)

    def advance(self) -> Token:
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        token = self.advance()
        if token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {token.type}")
        return token

    def parse(self) -> Expr:
        result = self.parse_expr()
        if self.peek().type != TokenType.EOF:
            raise SyntaxError(f"Unexpected token: {self.peek()}")
        return result

    def parse_expr(self) -> Expr:
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
        base = self.parse_unary()

        if self.peek().type == TokenType.POWER:
            self.advance()
            exp = self.parse_power()  # Right associative
            return Pow(base, exp)

        return base

    def parse_unary(self) -> Expr:
        if self.peek().type == TokenType.MINUS:
            self.advance()
            return Mul(Integer(-1), self.parse_unary())

        return self.parse_primary()

    def parse_primary(self) -> Expr:
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
