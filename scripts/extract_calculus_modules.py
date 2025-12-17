#!/usr/bin/env python3
"""
Automated extraction script for decomposing native_calculus.py

This script automatically extracts different components from the monolithic
native_calculus.py file and creates modular specialist files.

Usage:
    python scripts/extract_calculus_modules.py
"""

import re
from pathlib import Path
from typing import List, Tuple


# Apache License header
LICENSE_HEADER = """# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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


def read_source_file(source_path: Path) -> List[str]:
    """Read source file and return lines."""
    with open(source_path, 'r', encoding='utf-8') as f:
        return f.readlines()


def extract_class_with_methods(lines: List[str], class_name: str, start_line: int, end_line: int) -> str:
    """Extract a class definition with all its methods."""
    class_lines = lines[start_line-1:end_line]
    return ''.join(class_lines)


def create_differentiation_specialist(source_lines: List[str], target_dir: Path):
    """Extract DifferentiationEngine (lines 360-544)."""
    print("Creating differentiation_specialist.py...")

    module_doc = '''"""
Differentiation Specialist
==========================

Pure Python symbolic differentiation engine implementing standard calculus rules.

Differentiation Rules:
- Constants: d/dx(c) = 0
- Power rule: d/dx(x^n) = n*x^(n-1)
- Sum rule: d/dx(f + g) = f' + g'
- Product rule: d/dx(f * g) = f'*g + f*g'
- Quotient rule: d/dx(f/g) = (f'*g - f*g') / g^2
- Chain rule: d/dx(f(g(x))) = f'(g(x)) * g'(x)
- Standard functions: sin, cos, tan, exp, ln, etc.
"""

import logging
from typing import Dict, Callable
from fractions import Fraction
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg

logger = logging.getLogger(__name__)

'''

    # Extract class definition (lines 360-544)
    class_content = extract_class_with_methods(source_lines, 'DifferentiationEngine', 360, 544)

    full_content = LICENSE_HEADER + module_doc + class_content

    # Write to file
    output_path = target_dir / "differentiation_specialist.py"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"  Created: {output_path}")
    print(f"  Lines: {len(full_content.splitlines())}")


def create_integration_specialist(source_lines: List[str], target_dir: Path):
    """Extract IntegrationEngine (lines 550-2183)."""
    print("Creating integration_specialist.py...")

    module_doc = '''"""
Integration Specialist
======================

Pure Python symbolic integration engine using pattern-based rules.

Integration Methods:
- Basic table lookup (sin, cos, exp, etc.)
- Power rule: ∫x^n dx = x^(n+1)/(n+1)
- Constant multiple rule: ∫c*f dx = c*∫f dx
- Sum rule: ∫(f+g) dx = ∫f dx + ∫g dx
- Integration by parts using LIATE rule
- Simple u-substitution patterns
- Trig power reduction (sin^n, cos^n)
- Partial fractions (limited)
"""

import logging
from typing import Optional, List
from fractions import Fraction
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from .differentiation_specialist import DifferentiationEngine

logger = logging.getLogger(__name__)

'''

    # Extract class definition (lines 550-2183)
    class_content = extract_class_with_methods(source_lines, 'IntegrationEngine', 550, 2183)

    full_content = LICENSE_HEADER + module_doc + class_content

    # Write to file
    output_path = target_dir / "integration_specialist.py"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"  Created: {output_path}")
    print(f"  Lines: {len(full_content.splitlines())}")


def create_limit_specialist(source_lines: List[str], target_dir: Path):
    """Extract LimitEngine (lines 2188-3273 + 9619-13282)."""
    print("Creating limit_specialist.py...")

    module_doc = '''"""
Limit Specialist
================

Evaluates limits using direct substitution, L'Hôpital's rule, and pattern recognition.

Handles:
- Direct substitution when possible
- Indeterminate forms: 0/0, ∞/∞, 0*∞, ∞-∞, 0^0, 1^∞, ∞^0
- L'Hôpital's rule for 0/0 and ∞/∞
- Known limit patterns (derivative definitions, exponential vs polynomial, etc.)
- Limits at infinity
- One-sided limits
"""

import logging
import re
from typing import Optional, Tuple, Dict, Any
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func, add, mul, power, neg
from .differentiation_specialist import DifferentiationEngine

logger = logging.getLogger(__name__)

'''

    # Extract LimitEngine class (lines 2188-3273)
    class_content_part1 = extract_class_with_methods(source_lines, 'LimitEngine', 2188, 3273)

    # Extract KNOWN_LIMIT_PATTERNS and helpers (lines 9619-13282)
    patterns_content = ''.join(source_lines[9619-1:13282])

    full_content = LICENSE_HEADER + module_doc + class_content_part1 + "\n\n" + patterns_content

    # Write to file
    output_path = target_dir / "limit_specialist.py"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"  Created: {output_path}")
    print(f"  Lines: {len(full_content.splitlines())}")


def create_calculus_utils(source_lines: List[str], target_dir: Path):
    """Extract shared utility functions."""
    print("Creating calculus_utils.py...")

    module_doc = '''"""
Calculus Utilities
==================

Shared utility functions used across calculus specialists.

Functions:
- _get_symbols: Extract all symbol names from an expression
- _evaluate_at_numeric: Numerically evaluate expression at a point
- _try_evaluate_const: Try to evaluate expression as a constant
- _simplify_output: Clean up output string representation
- _contains_var: Check if expression contains a variable
- _subtract_one, _add_one: Arithmetic helpers
"""

import re
import math
import logging
from typing import Optional, Set
from .ast_types import Expr, Num, Sym, Add, Mul, Pow, Neg, Func

logger = logging.getLogger(__name__)

'''

    # Extract utility functions
    # _get_symbols (lines 4006-4028)
    get_symbols = ''.join(source_lines[4006-1:4028])

    # _evaluate_at_numeric (lines 4031-4080)
    evaluate_at_numeric = ''.join(source_lines[4031-1:4080])

    # _try_evaluate_const (lines 5126-5170)
    try_evaluate_const = ''.join(source_lines[5126-1:5170])

    # _simplify_output (lines 8676-8710)
    simplify_output = ''.join(source_lines[8676-1:8710])

    full_content = LICENSE_HEADER + module_doc + get_symbols + "\n\n" + evaluate_at_numeric + "\n\n" + try_evaluate_const + "\n\n" + simplify_output

    # Add helper functions for contains_var, subtract_one, add_one
    helpers = '''

def _contains_var(expr: Expr, var: str) -> bool:
    """Check if expression contains the variable."""
    if isinstance(expr, Num):
        return False
    if isinstance(expr, Sym):
        return expr.name == var
    if isinstance(expr, Neg):
        return _contains_var(expr.arg, var)
    if isinstance(expr, Add):
        return any(_contains_var(t, var) for t in expr.terms)
    if isinstance(expr, Mul):
        return any(_contains_var(f, var) for f in expr.factors)
    if isinstance(expr, Pow):
        return _contains_var(expr.base, var) or _contains_var(expr.exp, var)
    if isinstance(expr, Func):
        return _contains_var(expr.arg, var)
    return False


def _subtract_one(expr: Expr) -> Expr:
    """Subtract 1 from expression (for power rule)."""
    from .ast_types import add, Num
    if isinstance(expr, Num):
        return Num(expr.value - 1)
    return add(expr, Num(-1))


def _add_one(expr: Expr) -> Expr:
    """Add 1 to expression."""
    from .ast_types import add, Num
    if isinstance(expr, Num):
        return Num(expr.value + 1)
    return add(expr, Num(1))
'''

    full_content += helpers

    # Write to file
    output_path = target_dir / "calculus_utils.py"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"  Created: {output_path}")
    print(f"  Lines: {len(full_content.splitlines())}")


def main():
    """Main extraction orchestrator."""
    print("=" * 70)
    print("CALCULUS MODULE DECOMPOSITION")
    print("=" * 70)

    # Paths
    base_dir = Path(__file__).parent.parent
    source_file = base_dir / "src" / "symbo_agentic_reasoners" / "core" / "native_calculus.py"
    target_dir = base_dir / "src" / "symbo_agentic_reasoners" / "core" / "calculus"

    # Verify source exists
    if not source_file.exists():
        print(f"ERROR: Source file not found: {source_file}")
        return 1

    # Create target directory if needed
    target_dir.mkdir(parents=True, exist_ok=True)

    # Read source
    print(f"\nReading source: {source_file}")
    source_lines = read_source_file(source_file)
    print(f"  Total lines: {len(source_lines)}")

    print("\n" + "-" * 70)
    print("EXTRACTING MODULES")
    print("-" * 70 + "\n")

    # Extract each module
    try:
        create_calculus_utils(source_lines, target_dir)
        print()
        create_differentiation_specialist(source_lines, target_dir)
        print()
        create_integration_specialist(source_lines, target_dir)
        print()
        create_limit_specialist(source_lines, target_dir)
        print()

        print("-" * 70)
        print("EXTRACTION COMPLETE")
        print("-" * 70)
        print("\nNext steps:")
        print("1. Create series_specialist.py")
        print("2. Create special_integrals_specialist.py")
        print("3. Create calculus_supervisor.py")
        print("4. Create __init__.py")
        print("5. Update imports in solver_engine.py")
        print("6. Run tests to verify functionality")

        return 0

    except Exception as e:
        print(f"\nERROR during extraction: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
