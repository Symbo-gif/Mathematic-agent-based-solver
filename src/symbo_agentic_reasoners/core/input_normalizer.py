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
INPUT NORMALIZER - Backward Compatibility Layer
=================================================

DEPRECATED: This file has been decomposed into the modular input_normalization/ package.

For new code, import from input_normalization/ directly:
    from symbo_agentic_reasoners.core.input_normalization import normalize_input

This compatibility wrapper will remain indefinitely to support existing code.

Original File: 2,762 lines (decomposed on 2025-12-15)
New Architecture: Supervisor-Specialist pattern in input_normalization/ package

Migration Path:
---------------
```python
# OLD (still works - uses this compatibility layer)
from symbo_agentic_reasoners.core.input_normalizer import normalize_input

# NEW (recommended - direct import from modular package)
from symbo_agentic_reasoners.core.input_normalization import normalize_input
```

Package Structure (new modular architecture):
----------------------------------------------
input_normalization/
├── __init__.py                     # Public API (backward compatible)
├── pipeline.py                     # Main orchestrator (13-step pipeline)
├── unicode_handler.py              # Greek letters, symbols, superscripts
├── whitespace_handler.py           # Whitespace normalization
├── artifact_cleaner.py             # Copy-paste artifact cleanup
├── notation_preprocessor.py        # Prime, probability, matrix notation
├── pattern_applier.py              # Derivative, integral, modular patterns
├── vector_calculus.py              # Gradient, divergence, curl expansion
├── operator_normalizer.py          # Operator standardization
├── multiplication.py               # Implicit multiplication handling
├── function_handler.py             # Function name/parens normalization
├── exponent_handler.py             # Exponent precedence fixes
├── equation_normalizer.py          # Equation and parenthesis handling
├── expression_splitter.py          # Multi-expression detection
├── validator.py                    # Expression validation
└── diagnostics.py                  # Error diagnostics
"""

import warnings

# Issue deprecation warning (can be disabled with warnings.filterwarnings)
warnings.warn(
    "input_normalizer.py is a compatibility wrapper. "
    "For new code, use: from symbo_agentic_reasoners.core.input_normalization import ...",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from the new modular input_normalization package
from .input_normalization import *

# Explicitly import __all__ to maintain the export list
from .input_normalization import __all__

# Version info - mark as compatibility layer
__compatibility_layer__ = True
__migration_date__ = '2025-12-15'
__original_lines__ = 2762
__new_architecture__ = 'supervisor-specialist (input_normalization/ package)'
__deprecation_status__ = 'deprecated_but_maintained'
