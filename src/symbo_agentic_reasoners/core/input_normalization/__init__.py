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
Input Normalization Package - Modular Supervisor-Specialist Architecture
=========================================================================

This package provides input normalization for mathematical expressions WITHOUT
SymPy dependency. It has been decomposed from the monolithic input_normalizer.py
into a modular architecture for better maintainability and testability.

Public API (Backward Compatible):
----------------------------------
```python
from symbo_agentic_reasoners.core.input_normalization import (
    normalize_input,
    normalize_and_extract_command,
    safe_normalize,
)

# Full normalization pipeline
result = normalize_input("x^2 + 2x + 1")
# result: "x**2 + 2*x + 1"

# With command extraction
expr, metadata = normalize_and_extract_command("solve(x^2 - 4, x)")
# expr: "x**2 - 4", metadata: {"command": "solve", "variable": "x"}
```

Architecture:
-------------
- pipeline.py: Main orchestrator (combines all normalization steps)
- unicode_handler.py: Unicode to ASCII conversion
- expression_splitter.py: Multi-expression detection and splitting
- equation_normalizer.py: Equation and parenthesis handling
- vector_calculus.py: Vector calculus expansion (grad, div, curl)
- multiplication.py: Implicit multiplication handling
- artifact_cleaner.py: Copy-paste artifact cleanup
- whitespace_handler.py: Whitespace normalization
- notation_preprocessor.py: Prime/probability/matrix notation
- pattern_applier.py: Derivative/integral/modular patterns
- function_handler.py: Function name normalization
- operator_normalizer.py: Operator standardization
- exponent_handler.py: Exponent precedence fixes
- validator.py: Expression validation
- diagnostics.py: Error diagnostics
"""

# Pipeline (main orchestrator)
from .pipeline import (
    normalize_input,
    normalize_and_extract_command,
    safe_normalize,
    InputNormalizationPipeline,
)

# Unicode handling
from .unicode_handler import (
    normalize_unicode,
    GREEK_MAP,
    SYMBOL_MAP,
)

# Expression splitting
from .expression_splitter import (
    split_multi_expressions,
    detect_multiple_problems,
    get_problem_count,
)

# Equation normalization
from .equation_normalizer import (
    normalize_equation_equals,
    close_unclosed_parens,
)

# Vector calculus expansion
from .vector_calculus import expand_vector_calculus

# Multiplication handling
from .multiplication import (
    enhanced_implicit_multiplication,
    remove_spurious_multiplication,
    add_implicit_multiplication,
)

# Artifact cleanup
from .artifact_cleaner import cleanup_copypaste_artifacts

# Whitespace handling
from .whitespace_handler import normalize_whitespace

# Notation preprocessing
from .notation_preprocessor import (
    preprocess_prime_notation,
    preprocess_probability_symbols,
    preprocess_matrix_notation,
    preprocess_special_notations,
)

# Pattern application
from .pattern_applier import (
    apply_modular_patterns,
    apply_derivative_patterns,
    apply_integral_patterns,
    apply_word_patterns,
)

# Function handling
from .function_handler import (
    normalize_function_names,
    add_function_parens,
)

# Operator normalization
from .operator_normalizer import normalize_operators

# Exponent handling
from .exponent_handler import fix_exponent_precedence

# Validation
from .validator import validate_normalized

# Diagnostics
from .diagnostics import InputDiagnostic


__all__ = [
    # Main pipeline API
    'normalize_input',
    'normalize_and_extract_command',
    'safe_normalize',
    'InputNormalizationPipeline',

    # Unicode
    'normalize_unicode',
    'GREEK_MAP',
    'SYMBOL_MAP',

    # Splitting
    'split_multi_expressions',
    'detect_multiple_problems',
    'get_problem_count',

    # Equation normalization
    'normalize_equation_equals',
    'close_unclosed_parens',

    # Vector calculus
    'expand_vector_calculus',

    # Multiplication
    'enhanced_implicit_multiplication',
    'remove_spurious_multiplication',
    'add_implicit_multiplication',

    # Artifact cleanup
    'cleanup_copypaste_artifacts',

    # Whitespace
    'normalize_whitespace',

    # Notation preprocessing
    'preprocess_prime_notation',
    'preprocess_probability_symbols',
    'preprocess_matrix_notation',
    'preprocess_special_notations',

    # Pattern application
    'apply_modular_patterns',
    'apply_derivative_patterns',
    'apply_integral_patterns',
    'apply_word_patterns',

    # Function handling
    'normalize_function_names',
    'add_function_parens',

    # Operators
    'normalize_operators',

    # Exponents
    'fix_exponent_precedence',

    # Validation
    'validate_normalized',

    # Diagnostics
    'InputDiagnostic',
]

__version__ = '2.0.0'
__architecture__ = 'supervisor-specialist'
