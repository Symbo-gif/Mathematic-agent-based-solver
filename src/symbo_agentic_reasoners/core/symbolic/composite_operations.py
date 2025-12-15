# Copyright 2025 Symbo Agentic Reasoners
# Licensed under the Apache License, Version 2.0

"""
Composite Operations - Add, Mul, Pow
=====================================

Defines composite expression types that combine other expressions.
NO SYMPY DEPENDENCY - Pure Python implementation.

This module provides:
- Add: Sum of expressions (a + b + c + ...)
- Mul: Product of expressions (a * b * c * ...)
- Pow: Power expression (a^b)

Each class includes simplification logic and differentiation rules.
"""

from __future__ import annotations
from typing import Set, Union, Dict, Tuple
from .type_system import Expr, Symbol, Integer, Float, Rational, _ensure_expr


# =============================================================================
# COMPOSITE EXPRESSIONS: Add, Mul, Pow
# =============================================================================

class Add(Expr):
    """
    Sum of expressions.

    Replaces sympy.Add.
    """

    def __init__(self, *args: Expr):
        self.args = tuple(_ensure_expr(a) for a in args)
        self._hash_cache = hash(('Add',) + tuple(hash(a) for a in sorted(self.args, key=str)))

    def __repr__(self) -> str:
        return f"Add({', '.join(repr(a) for a in self.args)})"

    def __str__(self) -> str:
        if not self.args:
            return "0"
        result = str(self.args[0])
        for arg in self.args[1:]:
            s = str(arg)
            if s.startswith('-'):
                result += f" - {s[1:]}"
            else:
                result += f" + {s}"
        return result

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Add):
            return set(self.args) == set(other.args)
        if len(self.args) == 1:
            return self.args[0] == other
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    @property
    def free_symbols(self) -> Set[Symbol]:
        return set().union(*(a.free_symbols for a in self.args))

    def subs(self, *args, **kwargs) -> Expr:
        """Substitute symbols. Supports both subs({x: val}) and subs(x, val) formats."""
        if len(args) == 1 and isinstance(args[0], dict):
            substitutions = args[0]
        elif len(args) == 2:
            # subs(x, val) format
            substitutions = {args[0]: args[1]}
        else:
            substitutions = kwargs
        return Add(*(a.subs(substitutions) if hasattr(a, 'subs') else a for a in self.args)).simplify()

    def diff(self, var: Symbol) -> Expr:
        return Add(*(a.diff(var) for a in self.args)).simplify()

    def simplify(self) -> Expr:
        # Flatten nested Adds and distribute negatives over Adds
        flat_args = []
        for arg in self.args:
            if isinstance(arg, Add):
                flat_args.extend(arg.args)
            elif isinstance(arg, Mul):
                # Check if this is -1 * Add(...) or coefficient * Add(...)
                # We need to distribute the coefficient
                coef = Integer(1)
                add_expr = None
                other_parts = []
                for factor in arg.args:
                    if isinstance(factor, (Integer, Float, Rational)):
                        coef = Mul(coef, factor)._combine_numbers()
                    elif isinstance(factor, Add) and add_expr is None:
                        add_expr = factor
                    else:
                        other_parts.append(factor)

                if add_expr is not None and len(other_parts) == 0:
                    # Distribute coefficient over the Add
                    for add_term in add_expr.args:
                        if coef.is_one:
                            flat_args.append(add_term)
                        elif isinstance(coef, Integer) and coef.value == -1:
                            flat_args.append(Mul(Integer(-1), add_term))
                        else:
                            flat_args.append(Mul(coef, add_term))
                else:
                    flat_args.append(arg)
            else:
                flat_args.append(arg)

        # Check for Pythagorean identity: sin²(x) + cos²(x) = 1
        # Look for pattern: sin(x)**2 + cos(x)**2
        # Lazy import to avoid circular dependency
        from .function_library import Sin, Cos

        sin_squared = None
        cos_squared = None
        sin_arg = None
        cos_arg = None
        other_terms = []

        for arg in flat_args:
            # Check for sin(x)**2 pattern
            if isinstance(arg, Pow) and isinstance(arg.exp, Integer) and arg.exp.value == 2:
                if isinstance(arg.base, Sin):
                    sin_squared = arg
                    sin_arg = arg.base.args[0] if arg.base.args else None
                    continue
                elif isinstance(arg.base, Cos):
                    cos_squared = arg
                    cos_arg = arg.base.args[0] if arg.base.args else None
                    continue
            other_terms.append(arg)

        # If we found sin²(x) + cos²(x) with same argument, simplify to 1
        if sin_squared and cos_squared and sin_arg and cos_arg:
            if str(sin_arg) == str(cos_arg):  # Same argument
                # Replace sin²(x) + cos²(x) with 1
                if not other_terms:
                    return Integer(1)
                else:
                    flat_args = [Integer(1)] + other_terms

        # Combine like terms
        coefficients: Dict[str, Tuple[Expr, Expr]] = {}  # key -> (base, coefficient)
        constant = Integer(0)

        for arg in flat_args:
            if isinstance(arg, (Integer, Float, Rational)):
                constant = Add(constant, arg)._combine_numbers()
            elif isinstance(arg, Mul):
                # Extract coefficient and base from Mul
                coef = Integer(1)
                base_parts = []
                for factor in arg.args:
                    if isinstance(factor, (Integer, Float, Rational)):
                        coef = Mul(coef, factor)._combine_numbers()
                    else:
                        base_parts.append(factor)

                # Construct the base
                if len(base_parts) == 0:
                    # All numeric - treat as constant
                    constant = Add(constant, coef)._combine_numbers()
                    continue
                elif len(base_parts) == 1:
                    base = base_parts[0]
                else:
                    base = Mul(*base_parts)

                # Use string representation as key for combining like terms
                base_key = str(base)
                if base_key in coefficients:
                    old_base, old_coef = coefficients[base_key]
                    coefficients[base_key] = (old_base, Add(old_coef, coef)._combine_numbers())
                else:
                    coefficients[base_key] = (base, coef)
            else:
                # Non-Mul, non-numeric term (e.g., Symbol, Pow, Function)
                base_key = str(arg)
                if base_key in coefficients:
                    old_base, old_coef = coefficients[base_key]
                    coefficients[base_key] = (old_base, Add(old_coef, Integer(1))._combine_numbers())
                else:
                    coefficients[base_key] = (arg, Integer(1))

        # Rebuild expression
        result_args = []
        if not constant.is_zero:
            result_args.append(constant)

        for base_key, (base, coef) in coefficients.items():
            if coef.is_zero:
                continue
            elif coef.is_one:
                result_args.append(base)
            elif isinstance(coef, Integer) and coef.value == -1:
                result_args.append(Mul(Integer(-1), base))
            else:
                result_args.append(Mul(coef, base))

        if not result_args:
            return Integer(0)
        if len(result_args) == 1:
            return result_args[0]
        return Add(*result_args)

    def _combine_numbers(self) -> Expr:
        """Combine numeric values."""
        total = 0.0
        has_float = False
        for arg in self.args:
            if isinstance(arg, Integer):
                total += arg.value
            elif isinstance(arg, Float):
                total += arg.value
                has_float = True
            elif isinstance(arg, Rational):
                total += arg.p / arg.q
                has_float = True

        if has_float:
            if total == int(total):
                return Integer(int(total))
            return Float(total)
        return Integer(int(total))

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            return sum(a.evalf(precision) for a in self.args)
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        if not self.args:
            return "0"
        result = self.args[0].to_latex()
        for arg in self.args[1:]:
            latex = arg.to_latex()
            if latex.startswith('-'):
                result += f" - {latex[1:]}"
            else:
                result += f" + {latex}"
        return result


class Mul(Expr):
    """
    Product of expressions.

    Replaces sympy.Mul.
    """

    def __init__(self, *args: Expr):
        # Flatten nested Muls during initialization
        flat_args = []
        for a in args:
            a = _ensure_expr(a)
            if isinstance(a, Mul):
                flat_args.extend(a.args)
            else:
                flat_args.append(a)
        self.args = tuple(flat_args)
        self._hash_cache = hash(('Mul',) + tuple(hash(a) for a in sorted(self.args, key=str)))

    def __repr__(self) -> str:
        return f"Mul({', '.join(repr(a) for a in self.args)})"

    def __str__(self) -> str:
        if not self.args:
            return "1"

        # Handle negative coefficient
        parts = []
        for arg in self.args:
            if isinstance(arg, Add):
                parts.append(f"({arg})")
            elif isinstance(arg, Pow) and isinstance(arg.exp, (Integer, Rational)) and (
                (isinstance(arg.exp, Integer) and arg.exp.value < 0) or
                (isinstance(arg.exp, Rational) and arg.exp.p < 0)
            ):
                # Handle 1/x type expressions
                parts.append(f"({arg})")
            else:
                parts.append(str(arg))

        return '*'.join(parts)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mul):
            return set(self.args) == set(other.args)
        if len(self.args) == 1:
            return self.args[0] == other
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    @property
    def free_symbols(self) -> Set[Symbol]:
        return set().union(*(a.free_symbols for a in self.args))

    def subs(self, *args_in, **kwargs) -> Expr:
        """Substitute symbols. Supports both subs({x: val}) and subs(x, val)."""
        if len(args_in) == 1 and isinstance(args_in[0], dict):
            substitutions = args_in[0]
        elif len(args_in) == 2:
            substitutions = {args_in[0]: args_in[1]}
        else:
            substitutions = kwargs
        return Mul(*(a.subs(substitutions) for a in self.args)).simplify()

    def diff(self, var: Symbol) -> Expr:
        # Product rule: (f*g)' = f'*g + f*g'
        if len(self.args) == 0:
            return Integer(0)
        if len(self.args) == 1:
            return self.args[0].diff(var)

        terms = []
        for i, arg in enumerate(self.args):
            other_args = list(self.args[:i]) + list(self.args[i+1:])
            term = Mul(arg.diff(var), *other_args)
            terms.append(term)
        return Add(*terms).simplify()

    def simplify(self) -> Expr:
        # Flatten nested Muls and simplify arguments
        flat_args = []
        for arg in self.args:
            # Simplify each argument first
            if hasattr(arg, 'simplify'):
                arg = arg.simplify()
            if isinstance(arg, Mul):
                flat_args.extend(arg.args)
            else:
                flat_args.append(arg)

        # Combine powers of same base
        powers: Dict[Expr, Expr] = {}
        coefficient = Integer(1)

        for arg in flat_args:
            if isinstance(arg, (Integer, Float, Rational)):
                coefficient = Mul(coefficient, arg)._combine_numbers()
            elif isinstance(arg, Pow):
                base, exp = arg.base, arg.exp
                # Simplify the exponent
                if hasattr(exp, 'simplify'):
                    exp = exp.simplify()
                if base in powers:
                    powers[base] = Add(powers[base], exp).simplify()
                else:
                    powers[base] = exp
            else:
                if arg in powers:
                    powers[arg] = Add(powers[arg], Integer(1)).simplify()
                else:
                    powers[arg] = Integer(1)

        # Check for zero coefficient
        if coefficient.is_zero:
            return Integer(0)

        # Rebuild expression
        result_args = []
        if not coefficient.is_one:
            result_args.append(coefficient)

        for base, exp in powers.items():
            if exp.is_zero:
                continue
            elif exp.is_one:
                result_args.append(base)
            else:
                result_args.append(Pow(base, exp))

        if not result_args:
            return Integer(1)
        if len(result_args) == 1:
            return result_args[0]
        return Mul(*result_args)

    def _combine_numbers(self) -> Expr:
        """Combine numeric values."""
        total = 1.0
        has_float = False
        for arg in self.args:
            if isinstance(arg, Integer):
                total *= arg.value
            elif isinstance(arg, Float):
                total *= arg.value
                has_float = True
            elif isinstance(arg, Rational):
                total *= arg.p / arg.q
                has_float = True

        if has_float:
            if total == int(total):
                return Integer(int(total))
            return Float(total)
        return Integer(int(total))

    def evalf(self, precision: int = 15) -> Union[float, Expr]:
        try:
            result = 1.0
            for a in self.args:
                result *= a.evalf(precision)
            return result
        except (TypeError, ValueError):
            return self

    def to_latex(self) -> str:
        if not self.args:
            return "1"

        # Separate numerator and denominator
        numer = []
        denom = []

        for arg in self.args:
            if isinstance(arg, Pow) and isinstance(arg.exp, Integer) and arg.exp.value < 0:
                # Negative exponent -> denominator
                if arg.exp.value == -1:
                    denom.append(arg.base.to_latex())
                else:
                    denom.append(Pow(arg.base, Integer(-arg.exp.value)).to_latex())
            elif isinstance(arg, Pow) and isinstance(arg.exp, Rational) and arg.exp.p < 0:
                denom.append(Pow(arg.base, Rational(-arg.exp.p, arg.exp.q)).to_latex())
            else:
                if isinstance(arg, Add):
                    numer.append(r'\left(' + arg.to_latex() + r'\right)')
                else:
                    numer.append(arg.to_latex())

        if not numer:
            numer = ['1']

        numer_str = ' '.join(numer)

        if denom:
            denom_str = ' '.join(denom)
            return rf'\frac{{{numer_str}}}{{{denom_str}}}'

        return numer_str


class Pow(Expr):
    """
    Power expression (base^exponent).

    Replaces sympy.Pow.
    """

    def __init__(self, base: Expr, exp: Expr):
        self._base = _ensure_expr(base)
        self._exponent = _ensure_expr(exp)
        self._hash_cache = hash(('Pow', hash(self._base), hash(self._exponent)))

    @property
    def base(self) -> Expr:
        """Return the base of this power."""
        return self._base

    @property
    def exp(self) -> Expr:
        """Return the exponent of this power."""
        return self._exponent

    @property
    def exponent(self) -> Expr:
        """Alias for exp - return the exponent of this power."""
        return self._exponent

    def __repr__(self) -> str:
        return f"Pow({self._base!r}, {self._exponent!r})"

    def __str__(self) -> str:
        base_str = str(self._base)
        exp_str = str(self._exponent)

        # Handle special cases
        if isinstance(self._exponent, Integer) and self._exponent.value == -1:
            return f"1/{base_str}"
        if isinstance(self._exponent, Rational) and self._exponent.p == 1 and self._exponent.q == 2:
            return f"sqrt({base_str})"

        if isinstance(self._base, (Add, Mul)):
            base_str = f"({base_str})"

        return f"{base_str}**{exp_str}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Pow):
            return self.base == other.base and self.exp == other.exp
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    @property
    def free_symbols(self) -> Set[Symbol]:
        return self.base.free_symbols | self.exp.free_symbols

    def subs(self, *args_in, **kwargs) -> Expr:
        """Substitute symbols. Supports both subs({x: val}) and subs(x, val)."""
        if len(args_in) == 1 and isinstance(args_in[0], dict):
            substitutions = args_in[0]
        elif len(args_in) == 2:
            substitutions = {args_in[0]: args_in[1]}
        else:
            substitutions = kwargs
        return Pow(
            self.base.subs(substitutions),
            self.exp.subs(substitutions)
        ).simplify()

    def diff(self, var: Symbol) -> Expr:
        # Lazy import to avoid circular dependency
        from .function_library import Log

        # Power rule: d/dx(f^g) = f^g * (g' * ln(f) + g * f'/f)
        # Special case: if g is constant: d/dx(f^n) = n * f^(n-1) * f'
        if var not in self.exp.free_symbols:
            # g is constant
            return Mul(
                self.exp,
                Pow(self.base, Add(self.exp, Integer(-1))),
                self.base.diff(var)
            ).simplify()

        # General case with logarithm (would need Log function)
        # For now, handle common case where base is constant
        if var not in self.base.free_symbols:
            # f is constant: d/dx(a^g) = a^g * ln(a) * g'
            return Mul(self, Log(self.base), self.exp.diff(var)).simplify()

        # Full general case: f^g = e^(g*ln(f))
        # d/dx = f^g * (g' * ln(f) + g * f'/f)
        return Mul(
            self,
            Add(
                Mul(self.exp.diff(var), Log(self.base)),
                Mul(self.exp, Mul(self.base.diff(var), Pow(self.base, Integer(-1))))
            )
        ).simplify()

    def simplify(self) -> Expr:
        base = self.base.simplify() if hasattr(self.base, 'simplify') else self.base
        exp = self.exp.simplify() if hasattr(self.exp, 'simplify') else self.exp

        # x^0 = 1
        if exp.is_zero:
            return Integer(1)

        # x^1 = x
        if exp.is_one:
            return base

        # 0^n = 0 (for n > 0)
        if base.is_zero and isinstance(exp, (Integer, Float)) and exp.evalf() > 0:
            return Integer(0)

        # 1^n = 1
        if base.is_one:
            return Integer(1)

        # Numeric evaluation
        if isinstance(base, (Integer, Float, Rational)) and isinstance(exp, Integer):
            try:
                result = float(base.evalf()) ** exp.value
                if result == int(result) and abs(result) < 1e15:
                    return Integer(int(result))
                return Float(result)
            except (OverflowError, ValueError):
                pass

        # (a^b)^c = a^(b*c)
        if isinstance(base, Pow):
            return Pow(base.base, Mul(base.exp, exp).simplify()).simplify()

        return Pow(base, exp)

    def evalf(self, precision: int = 15) -> Union[float, complex, Expr]:
        try:
            base_val = self.base.evalf(precision)
            exp_val = self.exp.evalf(precision)
            if isinstance(base_val, (int, float)) and isinstance(exp_val, (int, float)):
                return base_val ** exp_val
            return self
        except (TypeError, ValueError, OverflowError):
            return self

    def to_latex(self) -> str:
        # Special cases
        if isinstance(self.exp, Rational) and self.exp.p == 1:
            if self.exp.q == 2:
                return rf'\sqrt{{{self.base.to_latex()}}}'
            if self.exp.q == 3:
                return rf'\sqrt[3]{{{self.base.to_latex()}}}'
            return rf'\sqrt[{self.exp.q}]{{{self.base.to_latex()}}}'

        if isinstance(self.exp, Integer) and self.exp.value == -1:
            return rf'\frac{{1}}{{{self.base.to_latex()}}}'

        base_latex = self.base.to_latex()
        if isinstance(self.base, (Add, Mul)):
            base_latex = rf'\left({base_latex}\right)'

        return rf'{base_latex}^{{{self.exp.to_latex()}}}'


__all__ = [
    'Add',
    'Mul',
    'Pow',
]
