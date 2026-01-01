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
Vector Calculus Handler
========================

Handles expansion of vector calculus operators (grad, div, curl) to
explicit derivative expressions.
"""

import re


# Command patterns for vector calculus operators
COMMAND_PATTERNS = {
    # grad(f, [x, y]) or grad(f, [x, y, z]) -> gradient vector
    'grad': re.compile(
        r'\bgrad\s*\(\s*(.+?)\s*,\s*\[\s*(.+?)\s*\]\s*\)',
        re.IGNORECASE
    ),
    # grad(f) - simple form without explicit variable list (infer from expression)
    'grad_simple': re.compile(
        r'\bgrad(?:ient)?\s*\(\s*([^,\[\]]+?)\s*\)',
        re.IGNORECASE
    ),
    # gradient of f - natural language form
    'gradient_natural': re.compile(
        r'\bgradient\s+(?:of\s+)?(.+)',
        re.IGNORECASE
    ),
    # grad f - space-separated form
    'grad_space': re.compile(
        r'\bgrad\s+([^\[\]\(\)]+)',
        re.IGNORECASE
    ),
    # div([Fx, Fy, Fz], [x, y, z]) -> divergence
    'div': re.compile(
        r'\bdiv\s*\(\s*\[\s*(.+?)\s*\]\s*(?:,\s*\[\s*(.+?)\s*\])?\s*\)',
        re.IGNORECASE
    ),
    # curl([Fx, Fy, Fz], [x, y, z]) -> curl vector
    'curl': re.compile(
        r'\bcurl\s*\(\s*\[\s*(.+?)\s*\]\s*,\s*\[\s*(.+?)\s*\]\s*\)',
        re.IGNORECASE
    ),
}


def expand_vector_calculus(text: str) -> str:
    """
    Expand vector calculus operators to derivative expressions.

    grad(f, [x, y]) -> [diff(f, x), diff(f, y)]
    div([P, Q], [x, y]) -> diff(P, x) + diff(Q, y)
    curl([P, Q, R], [x, y, z]) -> [diff(R,y)-diff(Q,z), diff(P,z)-diff(R,x), diff(Q,x)-diff(P,y)]

    Args:
        text: Input text with vector calculus operators

    Returns:
        Text with operators expanded to derivatives
    """
    result = text

    # Gradient: grad(f, [x, y, z]) -> [diff(f, x), diff(f, y), diff(f, z)]
    grad_match = COMMAND_PATTERNS['grad'].search(result)
    if grad_match:
        func = grad_match.group(1).strip()
        vars_str = grad_match.group(2).strip()
        variables = [v.strip() for v in vars_str.split(',')]
        grad_components = [f'diff({func}, {v})' for v in variables]
        grad_expr = '[' + ', '.join(grad_components) + ']'
        result = result[:grad_match.start()] + grad_expr + result[grad_match.end():]

    # Divergence: div([P, Q, R], [x, y, z]) -> diff(P, x) + diff(Q, y) + diff(R, z)
    div_match = COMMAND_PATTERNS['div'].search(result)
    if div_match:
        components_str = div_match.group(1).strip()
        vars_str = div_match.group(2)
        components = [c.strip() for c in components_str.split(',')]

        if vars_str:
            variables = [v.strip() for v in vars_str.split(',')]
        else:
            # Default variables x, y, z based on component count
            default_vars = ['x', 'y', 'z']
            variables = default_vars[:len(components)]

        div_terms = [f'diff({c}, {v})' for c, v in zip(components, variables)]
        div_expr = ' + '.join(div_terms)
        result = result[:div_match.start()] + div_expr + result[div_match.end():]

    # Curl: curl([P, Q, R], [x, y, z]) -> vector cross product with nabla
    curl_match = COMMAND_PATTERNS['curl'].search(result)
    if curl_match:
        components_str = curl_match.group(1).strip()
        vars_str = curl_match.group(2).strip()
        components = [c.strip() for c in components_str.split(',')]
        variables = [v.strip() for v in vars_str.split(',')]

        if len(components) == 3 and len(variables) == 3:
            P, Q, R = components
            x, y, z = variables
            curl_components = [
                f'diff({R}, {y}) - diff({Q}, {z})',
                f'diff({P}, {z}) - diff({R}, {x})',
                f'diff({Q}, {x}) - diff({P}, {y})'
            ]
            curl_expr = '[' + ', '.join(curl_components) + ']'
            result = result[:curl_match.start()] + curl_expr + result[curl_match.end():]

    return result
