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
Copy-Paste Artifact Cleaner
============================

Cleans up artifacts from copy-pasting rendered math from web pages/PDFs.
When math is rendered in HTML/PDF and then copied, subscripts and superscripts
often appear on separate lines. This module reconstructs the original expression.
"""


def cleanup_copypaste_artifacts(text: str) -> str:
    """
    Clean up artifacts from copy-pasting rendered math from web pages/PDFs.

    When math is rendered in HTML/PDF and then copied, subscripts and
    superscripts often appear on separate lines. This function reconstructs
    the original expression.

    Examples:
        'x\\n2\\n+ 3' (x² + 3 copy-pasted) → 'x**2 + 3'
        'f\\n′\\n(x)' (f′(x) copy-pasted) → "f'(x)"
        '∫\\na\\nb\\nf(x)dx' → '∫_a^b f(x)dx'

    Args:
        text: Input text potentially with copy-paste artifacts

    Returns:
        Cleaned text with artifacts reconstructed
    """
    if '\n' not in text and '\r' not in text:
        return text  # No multiline, nothing to do

    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    lines = [line.strip() for line in lines if line.strip()]

    if len(lines) <= 1:
        return text.strip()

    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for integral with bounds on next lines
        # Pattern: ∫ followed by lower bound, upper bound on separate lines
        if line in ('∫', 'Integral', '∫∫', '∫∫∫'):
            integral_sym = line
            # Look for bounds
            if i + 2 < len(lines):
                potential_lower = lines[i + 1]
                potential_upper = lines[i + 2]
                # Bounds are typically single chars/short expressions
                if len(potential_lower) <= 10 and len(potential_upper) <= 10:
                    # Check if they look like bounds (not operators or long expressions)
                    if not any(op in potential_lower for op in ['+', '-', '*', '/', '=']):
                        result.append(f'{integral_sym}_{{{potential_lower}}}^{{{potential_upper}}}')
                        i += 3
                        continue
            # No bounds found, just add integral
            result.append(integral_sym)
            i += 1
            continue

        # Check for prime notation on next line
        # Pattern: f followed by ′ or ' on next line, then (x)
        if i + 1 < len(lines) and lines[i + 1] in ("′", "'", "''", "'''", "′′", "′′′"):
            primes = lines[i + 1]
            # Convert Unicode primes to ASCII
            primes = primes.replace('′', "'")
            # Check if next line is function args
            if i + 2 < len(lines) and lines[i + 2].startswith('('):
                result.append(f"{line}{primes}{lines[i + 2]}")
                i += 3
                continue
            else:
                result.append(f"{line}{primes}")
                i += 2
                continue

        # Check for superscript on next line (single digit or small number)
        # Pattern: x followed by 2 → x**2
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            # If next line is just a number (likely a power)
            if next_line.isdigit() and len(next_line) <= 2:
                # Check it's not an operator before it
                if not line.endswith(('+', '-', '*', '/', '=')):
                    result.append(f"{line}**{next_line}")
                    i += 2
                    continue
            # If next line is 'n' or single letter (could be power)
            if len(next_line) == 1 and next_line.isalpha():
                # Could be x^n pattern - be conservative
                if len(line) == 1 and line.isalpha():
                    result.append(f"{line}**{next_line}")
                    i += 2
                    continue

        # Check for subscript pattern (variable followed by number)
        # Pattern: x followed by 1 where context suggests subscript (like x₁)
        # This is tricky - skip for now as it's less common

        # Default: just add the line
        result.append(line)
        i += 1

    # Join with spaces
    return ' '.join(result)
