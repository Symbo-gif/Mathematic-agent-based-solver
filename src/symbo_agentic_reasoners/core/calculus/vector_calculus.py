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
Vector Calculus Specialist - Gradient, Divergence, and Curl Operations
=======================================================================

This module provides vector calculus operations for scalar and vector fields.
All operations are implemented using the native differentiation engine without
SymPy dependency.

Operations:
-----------
- gradient: Computes the gradient of a scalar function (∇f)
- divergence: Computes the divergence of a vector field (∇·F)
- curl: Computes the curl of a 3D vector field (∇×F)

Examples:
---------
```python
from symbo_agentic_reasoners.core.calculus import gradient, divergence, curl

# Gradient of scalar function f(x,y,z) = x**2 + y**2 + z**2
success, grad, method = gradient("x**2 + y**2 + z**2", ["x", "y", "z"])
# result: ["2*x", "2*y", "2*z"]

# Divergence of vector field F = <x, y, z>
success, div, method = divergence(["x", "y", "z"], ["x", "y", "z"])
# result: "3"

# Curl of vector field F = <y, -x, 0>
success, curl_result, method = curl(["y", "-x", "0"], ["x", "y", "z"])
# result: ["0", "0", "-2"]
```

Architecture:
-------------
This specialist integrates with the calculus supervisor by using the
differentiate() function for partial derivatives. It handles:
- Multi-variable differentiation for gradients
- Component-wise differentiation for divergence
- Cross-product formulation for curl

Note:
-----
These functions were extracted from native_calculus.py as part of the
modular supervisor-specialist architecture migration.
"""

import logging
import re
from typing import List, Optional, Tuple

from .calculus_supervisor import differentiate

logger = logging.getLogger('symbo_agentic_reasoners.calculus.vector_calculus')


def _simplify_output(s: str) -> str:
    """Clean up output string."""
    # FIRST: Convert x**-1 to (1/x) BEFORE other cleanup
    # This must happen first so 1* removal doesn't break **-1
    def fix_negative_one_power(match):
        var = match.group(1)
        return f"(1/{var})"

    s = re.sub(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\*\*-1\b', fix_negative_one_power, s)

    # Remove 1* prefix (but not after ** or inside numbers)
    s = re.sub(r'(?<!\*)\b1\*', '', s)
    # Remove *1 suffix
    s = re.sub(r'\*1\b', '', s)
    # Clean up **1
    s = re.sub(r'\*\*1\b', '', s)
    # Clean up 0 + or + 0 (but not 0.5 + or + 0.5)
    s = re.sub(r'(?<![.\d])0 \+ ', '', s)
    s = re.sub(r' \+ 0(?![.\d])', '', s)
    # Clean up double negatives
    s = re.sub(r'--', '', s)

    # Fix patterns like x*(1/a) to x/a
    s = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\*\(1/([a-zA-Z_][a-zA-Z0-9_]*)\)', r'\1/\2', s)

    # Clean up (1/a)* prefix to be clearer: (1/a)*atan(...) → atan(...)/a
    def fix_one_over_times(match):
        denom = match.group(1)
        rest = match.group(2)
        return f"{rest}/{denom}"

    s = re.sub(r'\(1/([a-zA-Z_][a-zA-Z0-9_]*)\)\*([a-zA-Z_][a-zA-Z0-9_]*\([^)]+\))', fix_one_over_times, s)

    return s


def gradient(expr_str: str, variables: List[str]) -> Tuple[bool, Optional[List[str]], str]:
    """
    Compute gradient of scalar function.

    Args:
        expr_str: Scalar function expression
        variables: List of variables, e.g. ['x', 'y', 'z']

    Returns:
        (success, result_list, method)
        - success: True if gradient was computed
        - result_list: List of partial derivative strings
        - method: "native_calculus" or error description
    """
    try:
        results = []
        for var in variables:
            success, deriv, method = differentiate(expr_str, var)
            if not success:
                return False, None, f"gradient_failed_on_{var}: {method}"
            results.append(deriv)
        return True, results, "native_calculus"
    except Exception as e:
        logger.debug(f"Native gradient failed: {e}")
        return False, None, f"error: {e}"


def divergence(components: List[str], variables: List[str]) -> Tuple[bool, Optional[str], str]:
    """
    Compute divergence of vector field.

    div(F) = dF_x/dx + dF_y/dy + dF_z/dz

    Args:
        components: Vector field components, e.g. ['P', 'Q', 'R']
        variables: Variables, e.g. ['x', 'y', 'z']

    Returns:
        (success, result_string, method)
    """
    try:
        if len(components) != len(variables):
            return False, None, "mismatched_dimensions"

        terms = []
        for comp, var in zip(components, variables):
            success, deriv, method = differentiate(comp, var)
            if not success:
                return False, None, f"divergence_failed_on_d{comp}/d{var}: {method}"
            terms.append(deriv)

        # Sum the terms
        result = ' + '.join(terms)
        result = _simplify_output(result)
        return True, result, "native_calculus"
    except Exception as e:
        logger.debug(f"Native divergence failed: {e}")
        return False, None, f"error: {e}"


def curl(components: List[str], variables: List[str]) -> Tuple[bool, Optional[List[str]], str]:
    """
    Compute curl of 3D vector field.

    curl(F) = (dR/dy - dQ/dz, dP/dz - dR/dx, dQ/dx - dP/dy)

    Args:
        components: Vector field components [P, Q, R]
        variables: Variables [x, y, z]

    Returns:
        (success, result_list, method)
    """
    try:
        if len(components) != 3 or len(variables) != 3:
            return False, None, "curl_requires_3d"

        P, Q, R = components
        x, y, z = variables

        # Compute each component of curl
        # curl_x = dR/dy - dQ/dz
        success1, dR_dy, _ = differentiate(R, y)
        success2, dQ_dz, _ = differentiate(Q, z)
        if not (success1 and success2):
            return False, None, "curl_failed_on_x_component"
        curl_x = f"({dR_dy}) - ({dQ_dz})"

        # curl_y = dP/dz - dR/dx
        success3, dP_dz, _ = differentiate(P, z)
        success4, dR_dx, _ = differentiate(R, x)
        if not (success3 and success4):
            return False, None, "curl_failed_on_y_component"
        curl_y = f"({dP_dz}) - ({dR_dx})"

        # curl_z = dQ/dx - dP/dy
        success5, dQ_dx, _ = differentiate(Q, x)
        success6, dP_dy, _ = differentiate(P, y)
        if not (success5 and success6):
            return False, None, "curl_failed_on_z_component"
        curl_z = f"({dQ_dx}) - ({dP_dy})"

        results = [
            _simplify_output(curl_x),
            _simplify_output(curl_y),
            _simplify_output(curl_z)
        ]
        return True, results, "native_calculus"
    except Exception as e:
        logger.debug(f"Native curl failed: {e}")
        return False, None, f"error: {e}"
