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
SYMBO Agentic Reasoners - Public API
=====================================

Production-ready public API for the mathematical solver engine.

This module provides:
- Unified configuration via SolverConfig
- Structured results via SolveResult
- High-level solve functions with safety limits
- Batch processing capabilities

Quick Start:
------------
```python
from symbo_agentic_reasoners.api import solve_expression, SolverConfig

# Simple usage with defaults
result = solve_expression("x**2 - 4")
print(result.solution)  # "(x - 2)*(x + 2)" or simplified form

# Custom configuration
config = SolverConfig(timeout_sec=30.0, max_steps=100)
result = solve_expression("integrate(sin(x), x)", config=config)

# Check status
if result.status == "ok":
    print(f"Solution: {result.solution}")
else:
    print(f"Error: {result.error}")
```

Batch Processing:
-----------------
```python
from symbo_agentic_reasoners.api import solve_file

results = solve_file("problems.txt")
for r in results:
    print(f"{r.problem}: {r.solution if r.status == 'ok' else r.error}")
```
"""

from .config import SolverConfig
from .result import SolveResult
from .solver import solve_expression, solve_file, solve_batch
from .logging_setup import setup_logging

__all__ = [
    # Configuration
    "SolverConfig",
    # Results
    "SolveResult",
    # Solving functions
    "solve_expression",
    "solve_file",
    "solve_batch",
    # Utilities
    "setup_logging",
]
