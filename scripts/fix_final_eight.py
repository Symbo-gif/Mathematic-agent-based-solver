#!/usr/bin/env python3
"""Fix the final 8 nested function docstrings."""

import re

# graph_theory_agent.py - Fix 3 methods
file1 = "src/symbo_agentic_reasoners/agents/specialists/discrete_math/graph_theory_agent.py"

with open(file1, 'r') as f:
    content = f.read()

# Remove malformed docstrings first
content = re.sub(
    r'            """Perform (bfs|dfs) operation\.\n\n            Args:\n.*?>>> result = obj\.(bfs|dfs)\(\.\.\.\)\n            """\n',
    '',
    content,
    flags=re.DOTALL
)

with open(file1, 'w') as f:
    f.write(content)

print(f"Fixed {file1}")

# numerical_methods_specialist.py - Fix 3 evaluator methods
file2 = "src/symbo_agentic_reasoners/agents/specialists/numerical/numerical_methods_specialist.py"

with open(file2, 'r') as f:
    content = f.read()

# Remove malformed docstrings
content = re.sub(
    r'        """Perform evaluator operation\.\n\n        Args:\n.*?>>> result = obj\.evaluator\(\.\.\.\)\n        """\n',
    '',
    content,
    flags=re.DOTALL
)

# Add proper docstrings to the 3 evaluator functions
# Line ~699: Lagrange interpolation evaluator
content = content.replace(
    '        def evaluator(x):\n            result = 0.0',
    '        def evaluator(x):\n            """Evaluate Lagrange polynomial at point x."""\n            result = 0.0'
)

# Line ~741: Newton divided difference evaluator
content = content.replace(
    '        def evaluator(x):\n            result = coeffs[0]',
    '        def evaluator(x):\n            """Evaluate Newton divided difference polynomial at point x."""\n            result = coeffs[0]'
)

# Line ~768: Piecewise linear evaluator
content = content.replace(
    '        def evaluator(x):\n            # Find interval',
    '        def evaluator(x):\n            """Evaluate piecewise linear interpolation at point x."""\n            # Find interval'
)

with open(file2, 'w') as f:
    f.write(content)

print(f"Fixed {file2}")

# analytic_functions_specialist.py - Fix 1 method
file3 = "src/symbo_agentic_reasoners/agents/specialists/complex_analysis/analytic_functions_specialist.py"

with open(file3, 'r') as f:
    content = f.read()

# Remove malformed
content = re.sub(
    r'        """Perform make_series_func operation\.\n\n        Args:\n.*?>>> result = obj\.make_series_func\(\.\.\.\)\n        """\n',
    '',
    content,
    flags=re.DOTALL
)

# Add proper docstring
content = content.replace(
    '        def make_series_func(z):',
    '        def make_series_func(z):\n            """Generate series function for numerical evaluation."""'
)

with open(file3, 'w') as f:
    f.write(content)

print(f"Fixed {file3}")

# predicate_specialist.py - Fix 1 method
file4 = "src/symbo_agentic_reasoners/agents/specialists/logic/predicate_specialist.py"

with open(file4, 'r') as f:
    content = f.read()

# Remove malformed
content = re.sub(
    r'            """Perform unify_terms operation\.\n\n            Args:\n.*?>>> result = obj\.unify_terms\(\.\.\.\)\n            """\n',
    '',
    content,
    flags=re.DOTALL
)

# Add proper docstring
content = content.replace(
    '            def unify_terms(t1, t2):',
    '            def unify_terms(t1, t2):\n                """Unify two first-order logic terms."""'
)

with open(file4, 'w') as f:
    f.write(content)

print(f"Fixed {file4}")

print("\n✅ All 8 methods fixed!")
print("Run: python scripts/docstring_coverage_report.py")
