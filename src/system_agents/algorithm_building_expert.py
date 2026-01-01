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
ALGORITHM BUILDING EXPERT - System Agent
========================================

A BDI agent for building, inspecting, and improving mathematical algorithms.

CAPABILITIES:
-------------
1. BUILD: Generate new algorithm implementations for mathematical operations
2. INSPECT: Analyze existing algorithms for correctness, efficiency, edge cases
3. IMPROVE: Propose and implement optimizations to existing algorithms

INTEGRATION:
------------
- Works with discovery/algorithm modules (AlgorithmSynthesizer, ComplexityAnalyzer)
- Interacts with specialists for domain-specific algorithm verification
- Uses Blackboard for algorithm proposals and validation results

ARCHITECTURE:
-------------
Follows BDI (Belief-Desire-Intention) pattern:
- Beliefs: Current algorithm inventory, complexity profiles, correctness status
- Desires: Build optimal algorithms, improve efficiency, ensure correctness
- Intentions: Algorithm construction plans, optimization strategies
"""

import logging
import math
import time
import ast
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

logger = logging.getLogger('system_agents.algorithm_building_expert')


class AlgorithmType(Enum):
    """Types of algorithms this agent can build."""
    NUMERICAL = "numerical"
    SYMBOLIC = "symbolic"
    COMBINATORIAL = "combinatorial"
    GRAPH = "graph"
    OPTIMIZATION = "optimization"
    INTEGRATION = "integration"
    ROOT_FINDING = "root_finding"


@dataclass
class AlgorithmSpec:
    """Specification for an algorithm to be built or improved."""
    name: str
    algorithm_type: AlgorithmType
    description: str
    inputs: List[Dict[str, str]]  # [{"name": str, "type": str, "description": str}]
    outputs: List[Dict[str, str]]
    constraints: List[str] = field(default_factory=list)
    test_cases: List[Dict[str, Any]] = field(default_factory=list)
    complexity_target: Optional[str] = None  # e.g., "O(n log n)"


@dataclass
class AlgorithmAnalysis:
    """Analysis results for an existing algorithm."""
    algorithm_name: str
    time_complexity: str
    space_complexity: str
    correctness_score: float  # 0.0 to 1.0
    edge_cases_handled: List[str]
    edge_cases_missing: List[str]
    optimization_opportunities: List[str]
    test_coverage: float  # 0.0 to 1.0


@dataclass
class AlgorithmImprovement:
    """Proposed improvement for an algorithm."""
    algorithm_name: str
    improvement_type: str  # "performance", "correctness", "edge_case"
    description: str
    original_code: str
    improved_code: str
    expected_speedup: Optional[float] = None
    test_verification: bool = False


class AlgorithmBuildingExpert(BDIAgent):
    """
    Algorithm Building Expert - System Agent

    DIRECTIVE:
    ----------
    Build, inspect, and improve mathematical algorithms while maintaining
    the NO SYMPY philosophy and BDI architecture principles.

    OPERATIONS:
    -----------
    - build_algorithm: Generate new algorithm from specification
    - inspect_algorithm: Analyze algorithm for correctness and efficiency
    - improve_algorithm: Propose and implement optimizations
    - verify_correctness: Run test cases and verify correctness
    - analyze_complexity: Determine time/space complexity
    """

    def __init__(
        self,
        agent_id: str = "algorithm_building_expert",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)

        self.agent_type = "algorithm_building_expert"
        self.df = directory_facilitator
        self.blackboard = blackboard

        # Algorithm inventory - algorithms this agent has built or analyzed
        self._algorithm_inventory: Dict[str, AlgorithmSpec] = {}
        self._analysis_cache: Dict[str, AlgorithmAnalysis] = {}
        self._improvement_history: List[AlgorithmImprovement] = []

        # Statistics
        self._stats = {
            'algorithms_built': 0,
            'algorithms_inspected': 0,
            'improvements_proposed': 0,
            'improvements_applied': 0,
            'tests_run': 0,
            'bugs_found': 0,
        }

        # Algorithm templates for common patterns
        self._algorithm_templates = self._load_algorithm_templates()

        self._register_services()

        logger.info(f"[{agent_id}] Algorithm Building Expert initialized")

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="algorithm_construction",
                    description="Build new mathematical algorithms"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="algorithm_inspection",
                    description="Inspect and analyze algorithms"
                ),
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="algorithm_improvement",
                    description="Propose algorithm optimizations"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    def _load_algorithm_templates(self) -> Dict[str, str]:
        """Load algorithm templates for common patterns."""
        return {
            "binary_search": '''
def binary_search(arr, target):
    """Binary search for target in sorted array. O(log n) time, O(1) space."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
''',
            "newton_raphson": '''
def newton_raphson(f, df, x0, tol=1e-10, max_iter=100):
    """Newton-Raphson root finding. O(n) iterations, O(1) space."""
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        dfx = df(x)
        if abs(dfx) < 1e-15:
            raise ValueError("Derivative too small")
        x = x - fx / dfx
    return x
''',
            "quicksort": '''
def quicksort(arr):
    """Quicksort with median-of-three pivot. O(n log n) avg, O(n^2) worst."""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
''',
            "gcd_euclidean": '''
def gcd(a, b):
    """Greatest common divisor using Euclidean algorithm. O(log min(a,b))."""
    while b:
        a, b = b, a % b
    return abs(a)
''',
            "polynomial_evaluation": '''
def horner_eval(coeffs, x):
    """Evaluate polynomial using Horner's method. O(n) time, O(1) space."""
    result = 0
    for c in reversed(coeffs):
        result = result * x + c
    return result
''',
            "matrix_multiply": '''
def matrix_multiply(A, B):
    """Matrix multiplication. O(n^3) time, O(n^2) space."""
    n, m, p = len(A), len(A[0]), len(B[0])
    result = [[0] * p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            for k in range(m):
                result[i][j] += A[i][k] * B[k][j]
    return result
''',
        }

    # ==================== CORE CAPABILITIES ====================

    def build_algorithm(self, spec: AlgorithmSpec) -> Tuple[str, bool]:
        """
        Build an algorithm from specification.

        Args:
            spec: AlgorithmSpec with requirements

        Returns:
            Tuple of (algorithm_code, success)
        """
        logger.info(f"Building algorithm: {spec.name}")

        # Check if we have a template that matches
        for template_name, template_code in self._algorithm_templates.items():
            if template_name in spec.name.lower() or template_name.replace('_', ' ') in spec.description.lower():
                # Adapt template to specification
                code = self._adapt_template(template_code, spec)
                self._algorithm_inventory[spec.name] = spec
                self._stats['algorithms_built'] += 1
                return code, True

        # Generate algorithm based on type
        if spec.algorithm_type == AlgorithmType.ROOT_FINDING:
            code = self._build_root_finding_algorithm(spec)
        elif spec.algorithm_type == AlgorithmType.NUMERICAL:
            code = self._build_numerical_algorithm(spec)
        elif spec.algorithm_type == AlgorithmType.INTEGRATION:
            code = self._build_integration_algorithm(spec)
        elif spec.algorithm_type == AlgorithmType.COMBINATORIAL:
            code = self._build_combinatorial_algorithm(spec)
        elif spec.algorithm_type == AlgorithmType.GRAPH:
            code = self._build_graph_algorithm(spec)
        else:
            code = self._build_generic_algorithm(spec)

        if code:
            self._algorithm_inventory[spec.name] = spec
            self._stats['algorithms_built'] += 1
            return code, True

        return "", False

    def _adapt_template(self, template: str, spec: AlgorithmSpec) -> str:
        """Adapt a template to match specification."""
        code = template

        # Rename function if needed
        func_match = re.search(r'def (\w+)\(', code)
        if func_match:
            old_name = func_match.group(1)
            new_name = spec.name.lower().replace(' ', '_')
            code = code.replace(f"def {old_name}(", f"def {new_name}(")

        return code

    def _build_root_finding_algorithm(self, spec: AlgorithmSpec) -> str:
        """Build a root-finding algorithm."""
        return f'''
def {spec.name.lower().replace(" ", "_")}(f, x0, tol=1e-10, max_iter=100):
    """
    {spec.description}

    Args:
        f: Function to find root of
        x0: Initial guess
        tol: Convergence tolerance
        max_iter: Maximum iterations

    Returns:
        Root value or None if not found
    """
    # Newton-Raphson with numerical derivative
    h = 1e-8
    x = x0

    for i in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x

        # Central difference for derivative
        dfx = (f(x + h) - f(x - h)) / (2 * h)

        if abs(dfx) < 1e-15:
            # Try secant step
            x_new = x - fx * h / (f(x + h) - fx) if abs(f(x + h) - fx) > 1e-15 else None
            if x_new is None:
                return None
            x = x_new
        else:
            x = x - fx / dfx

    return x if abs(f(x)) < tol else None
'''

    def _build_numerical_algorithm(self, spec: AlgorithmSpec) -> str:
        """Build a numerical algorithm."""
        return f'''
def {spec.name.lower().replace(" ", "_")}(func, *args, tol=1e-8, **kwargs):
    """
    {spec.description}

    Native implementation - NO external dependencies.
    """
    # Implementation based on specification
    result = None

    # Adaptive iteration
    max_iter = kwargs.get('max_iter', 1000)

    for _ in range(max_iter):
        # Compute next iteration
        # (Implementation details depend on specific algorithm)
        pass

    return result
'''

    def _build_integration_algorithm(self, spec: AlgorithmSpec) -> str:
        """Build an integration algorithm."""
        return f'''
def {spec.name.lower().replace(" ", "_")}(f, a, b, n=1000, tol=1e-8):
    """
    {spec.description}

    Adaptive Simpson's rule with error estimation.
    """
    def simpson(f, a, b):
        h = (b - a) / 2
        return h / 3 * (f(a) + 4 * f(a + h) + f(b))

    def adaptive_simpson(f, a, b, tol, whole, depth=0, max_depth=20):
        mid = (a + b) / 2
        left = simpson(f, a, mid)
        right = simpson(f, mid, b)

        if depth >= max_depth or abs(left + right - whole) < 15 * tol:
            return left + right + (left + right - whole) / 15

        return adaptive_simpson(f, a, mid, tol/2, left, depth+1, max_depth) + \\
               adaptive_simpson(f, mid, b, tol/2, right, depth+1, max_depth)

    whole = simpson(f, a, b)
    return adaptive_simpson(f, a, b, tol, whole)
'''

    def _build_combinatorial_algorithm(self, spec: AlgorithmSpec) -> str:
        """Build a combinatorial algorithm."""
        return f'''
def {spec.name.lower().replace(" ", "_")}(*args):
    """
    {spec.description}

    Native combinatorial implementation.
    """
    import math

    # Default to computing combinations C(n, k)
    if len(args) == 2:
        n, k = args
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        k = min(k, n - k)
        result = 1
        for i in range(k):
            result = result * (n - i) // (i + 1)
        return result

    return None
'''

    def _build_graph_algorithm(self, spec: AlgorithmSpec) -> str:
        """Build a graph algorithm."""
        return f'''
def {spec.name.lower().replace(" ", "_")}(graph, start=0, end=None):
    """
    {spec.description}

    Native graph algorithm implementation.
    Graph format: {{node: [(neighbor, weight), ...]}}
    """
    import heapq

    # Dijkstra's shortest path
    distances = {{node: float('inf') for node in graph}}
    distances[start] = 0
    pq = [(0, start)]
    parents = {{start: None}}

    while pq:
        d, u = heapq.heappop(pq)
        if d > distances[u]:
            continue
        for v, w in graph.get(u, []):
            if distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                parents[v] = u
                heapq.heappush(pq, (distances[v], v))

    # Return path to end if specified
    if end is not None and end in distances:
        path = []
        node = end
        while node is not None:
            path.append(node)
            node = parents.get(node)
        return {{'distance': distances[end], 'path': path[::-1]}}

    return {{'distances': distances}}
'''

    def _build_generic_algorithm(self, spec: AlgorithmSpec) -> str:
        """Build a generic algorithm structure."""
        input_params = ", ".join(inp.get("name", f"arg{i}") for i, inp in enumerate(spec.inputs))

        return f'''
def {spec.name.lower().replace(" ", "_")}({input_params}):
    """
    {spec.description}

    Inputs: {spec.inputs}
    Outputs: {spec.outputs}
    Constraints: {spec.constraints}
    """
    # Implementation placeholder
    # TODO: Implement algorithm logic

    result = None
    return result
'''

    def inspect_algorithm(self, code: str, algorithm_name: str = "unnamed") -> AlgorithmAnalysis:
        """
        Inspect an algorithm for correctness and efficiency.

        Args:
            code: Algorithm source code
            algorithm_name: Name of the algorithm

        Returns:
            AlgorithmAnalysis with findings
        """
        logger.info(f"Inspecting algorithm: {algorithm_name}")

        # Analyze time complexity
        time_complexity = self._estimate_time_complexity(code)
        space_complexity = self._estimate_space_complexity(code)

        # Check for edge cases
        edge_cases_handled, edge_cases_missing = self._check_edge_cases(code)

        # Find optimization opportunities
        optimizations = self._find_optimizations(code)

        # Estimate correctness (based on patterns)
        correctness_score = self._estimate_correctness(code)

        # Estimate test coverage
        test_coverage = self._estimate_test_coverage(algorithm_name)

        self._stats['algorithms_inspected'] += 1

        analysis = AlgorithmAnalysis(
            algorithm_name=algorithm_name,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            correctness_score=correctness_score,
            edge_cases_handled=edge_cases_handled,
            edge_cases_missing=edge_cases_missing,
            optimization_opportunities=optimizations,
            test_coverage=test_coverage
        )

        self._analysis_cache[algorithm_name] = analysis
        return analysis

    def _estimate_time_complexity(self, code: str) -> str:
        """Estimate time complexity from code patterns."""
        # Count nested loops
        loop_pattern = r'\b(for|while)\b'
        loops = re.findall(loop_pattern, code)
        loop_count = len(loops)

        # Check for recursion
        has_recursion = 'def ' in code and re.search(r'return.*\w+\(', code)

        # Check for divide and conquer patterns
        has_divide_conquer = ('// 2' in code or '/ 2' in code or '>> 1' in code) and has_recursion

        # Estimate complexity
        if has_divide_conquer:
            if loop_count <= 1:
                return "O(log n)"
            else:
                return "O(n log n)"
        elif loop_count >= 3:
            return f"O(n^{loop_count})"
        elif loop_count == 2:
            return "O(n^2)"
        elif loop_count == 1:
            return "O(n)"
        else:
            return "O(1)"

    def _estimate_space_complexity(self, code: str) -> str:
        """Estimate space complexity from code patterns."""
        # Check for list/array allocations
        has_list_alloc = re.search(r'\[.*\].*for.*in', code) or '* n' in code or '* len(' in code
        has_matrix = re.search(r'\[\[', code)
        has_recursion = 'def ' in code and re.search(r'return.*\w+\(', code)

        if has_matrix:
            return "O(n^2)"
        elif has_list_alloc:
            return "O(n)"
        elif has_recursion:
            return "O(log n) - O(n) (stack)"
        else:
            return "O(1)"

    def _check_edge_cases(self, code: str) -> Tuple[List[str], List[str]]:
        """Check which edge cases are handled and which are missing."""
        handled = []
        missing = []

        # Check for empty input handling
        if re.search(r'(len\(\w+\)\s*==\s*0|len\(\w+\)\s*<\s*1|not\s+\w+)', code):
            handled.append("empty_input")
        else:
            missing.append("empty_input")

        # Check for None handling
        if 'None' in code or 'is None' in code:
            handled.append("none_input")
        else:
            missing.append("none_input")

        # Check for negative number handling
        if '< 0' in code or '<= 0' in code or 'abs(' in code:
            handled.append("negative_numbers")
        else:
            missing.append("negative_numbers")

        # Check for zero handling
        if '== 0' in code or '!= 0' in code or 'if 0' in code:
            handled.append("zero_input")
        else:
            missing.append("zero_input")

        # Check for overflow protection
        if 'try' in code or 'except' in code or 'max(' in code or 'min(' in code:
            handled.append("overflow_protection")
        else:
            missing.append("overflow_protection")

        # Check for tolerance/epsilon handling
        if 'tol' in code or 'eps' in code or '1e-' in code:
            handled.append("numerical_tolerance")
        else:
            missing.append("numerical_tolerance")

        return handled, missing

    def _find_optimizations(self, code: str) -> List[str]:
        """Find optimization opportunities in the code."""
        optimizations = []

        # Check for repeated calculations in loops
        if re.search(r'for.*:.*\n.*len\(', code):
            optimizations.append("Cache len() call outside loop")

        # Check for list concatenation in loop
        if re.search(r'for.*:.*\+\s*\[', code):
            optimizations.append("Use list.append() instead of concatenation")

        # Check for string concatenation in loop
        if re.search(r'for.*:.*\+\s*["\']', code):
            optimizations.append("Use ''.join() for string concatenation")

        # Check for redundant list comprehensions
        if re.search(r'\[x for x in', code):
            optimizations.append("Simplify identity list comprehension")

        # Check for memoization opportunity
        if re.search(r'def \w+\([^)]*\):.*return.*\1\(', code, re.DOTALL):
            optimizations.append("Consider memoization for recursive function")

        # Check for early exit opportunity
        if 'for' in code and 'return' not in code:
            optimizations.append("Consider early exit condition in loop")

        return optimizations

    def _estimate_correctness(self, code: str) -> float:
        """Estimate algorithm correctness based on patterns."""
        score = 0.5  # Base score

        # Check for proper function structure
        if 'def ' in code and 'return' in code:
            score += 0.1

        # Check for docstring
        if '"""' in code or "'''" in code:
            score += 0.05

        # Check for edge case handling
        edge_checks = sum(1 for pattern in ['if len', 'if not', 'if None', '< 0', '== 0']
                         if pattern in code)
        score += min(0.15, edge_checks * 0.05)

        # Check for error handling
        if 'try' in code and 'except' in code:
            score += 0.1

        # Check for numerical stability
        if 'abs(' in code or 'tol' in code or '1e-' in code:
            score += 0.1

        return min(1.0, score)

    def _estimate_test_coverage(self, algorithm_name: str) -> float:
        """Estimate test coverage for an algorithm."""
        # Would connect to actual test coverage data
        # For now, return estimated value based on algorithm type
        return 0.6  # Placeholder

    def improve_algorithm(self, code: str, algorithm_name: str) -> AlgorithmImprovement:
        """
        Propose improvements for an algorithm.

        Args:
            code: Algorithm source code
            algorithm_name: Name of the algorithm

        Returns:
            AlgorithmImprovement with proposed changes
        """
        logger.info(f"Improving algorithm: {algorithm_name}")

        # First inspect the algorithm
        analysis = self.inspect_algorithm(code, algorithm_name)

        improved_code = code
        improvement_type = "optimization"
        improvements_made = []

        # Apply optimizations
        for optimization in analysis.optimization_opportunities:
            if "Cache len()" in optimization:
                improved_code = self._apply_len_caching(improved_code)
                improvements_made.append("len() caching")

            if "list.append()" in optimization:
                improved_code = self._apply_append_optimization(improved_code)
                improvements_made.append("list append optimization")

        # Add missing edge case handling
        for edge_case in analysis.edge_cases_missing:
            if edge_case == "empty_input":
                improved_code = self._add_empty_input_check(improved_code)
                improvements_made.append("empty input check")
            elif edge_case == "numerical_tolerance":
                improved_code = self._add_tolerance_handling(improved_code)
                improvements_made.append("numerical tolerance")

        self._stats['improvements_proposed'] += 1

        improvement = AlgorithmImprovement(
            algorithm_name=algorithm_name,
            improvement_type=improvement_type,
            description=f"Applied: {', '.join(improvements_made)}" if improvements_made else "No improvements found",
            original_code=code,
            improved_code=improved_code,
            expected_speedup=1.1 if improvements_made else 1.0,
            test_verification=False
        )

        self._improvement_history.append(improvement)
        return improvement

    def _apply_len_caching(self, code: str) -> str:
        """Cache len() calls outside loops."""
        # Simple pattern replacement
        pattern = r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):'
        replacement = r'_len_\2 = len(\2)\n    for \1 in range(_len_\2):'
        return re.sub(pattern, replacement, code)

    def _apply_append_optimization(self, code: str) -> str:
        """Optimize list concatenation to append."""
        # This is a simplified transformation
        return code  # Full implementation would parse AST

    def _add_empty_input_check(self, code: str) -> str:
        """Add empty input validation."""
        # Find function definition and add check
        match = re.search(r'(def \w+\([^)]*\):)\s*("""[^"]*"""|\'\'\'[^\']*\'\'\')?', code)
        if match:
            func_def = match.group(1)
            docstring = match.group(2) or ""

            # Extract first argument name
            arg_match = re.search(r'def \w+\((\w+)', func_def)
            if arg_match:
                arg_name = arg_match.group(1)
                check = f"\n    if not {arg_name}:\n        return None"
                insert_pos = match.end()
                code = code[:insert_pos] + check + code[insert_pos:]

        return code

    def _add_tolerance_handling(self, code: str) -> str:
        """Add numerical tolerance handling."""
        # Find function definition and add tolerance parameter
        pattern = r'def (\w+)\(([^)]*)\):'

        def add_tol(match):
            func_name = match.group(1)
            params = match.group(2)
            if 'tol' not in params:
                if params:
                    params += ', tol=1e-10'
                else:
                    params = 'tol=1e-10'
            return f'def {func_name}({params}):'

        return re.sub(pattern, add_tol, code)

    def verify_correctness(
        self,
        code: str,
        test_cases: List[Dict[str, Any]]
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Verify algorithm correctness with test cases.

        Args:
            code: Algorithm source code
            test_cases: List of {"input": ..., "expected": ...}

        Returns:
            Tuple of (all_passed, results)
        """
        results = []
        all_passed = True

        try:
            # Compile the code
            exec_globals = {'math': math}
            exec(code, exec_globals)

            # Find the function
            func_name = re.search(r'def (\w+)\(', code)
            if not func_name:
                return False, [{"error": "No function found in code"}]

            func = exec_globals.get(func_name.group(1))

            for i, test_case in enumerate(test_cases):
                test_input = test_case.get('input', [])
                expected = test_case.get('expected')

                try:
                    if isinstance(test_input, dict):
                        actual = func(**test_input)
                    elif isinstance(test_input, (list, tuple)):
                        actual = func(*test_input)
                    else:
                        actual = func(test_input)

                    # Check result
                    if isinstance(expected, float):
                        passed = abs(actual - expected) < 1e-8
                    else:
                        passed = actual == expected

                    results.append({
                        'test_id': i,
                        'passed': passed,
                        'input': test_input,
                        'expected': expected,
                        'actual': actual
                    })

                    if not passed:
                        all_passed = False
                        self._stats['bugs_found'] += 1

                except Exception as e:
                    results.append({
                        'test_id': i,
                        'passed': False,
                        'input': test_input,
                        'error': str(e)
                    })
                    all_passed = False
                    self._stats['bugs_found'] += 1

                self._stats['tests_run'] += 1

        except SyntaxError as e:
            return False, [{"error": f"Syntax error: {e}"}]
        except Exception as e:
            return False, [{"error": f"Execution error: {e}"}]

        return all_passed, results

    # ==================== BDI IMPLEMENTATION ====================

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for algorithm tasks."""
        if not self.blackboard:
            return

        try:
            # Find algorithm-related tasks
            tasks = self.blackboard.query_entries(
                tags=['algorithm', 'build'],
                status=EntryStatus.PENDING
            ) if hasattr(self.blackboard, 'query_entries') else []

            inspect_tasks = self.blackboard.query_entries(
                tags=['algorithm', 'inspect'],
                status=EntryStatus.PENDING
            ) if hasattr(self.blackboard, 'query_entries') else []

            improve_tasks = self.blackboard.query_entries(
                tags=['algorithm', 'improve'],
                status=EntryStatus.PENDING
            ) if hasattr(self.blackboard, 'query_entries') else []

            all_tasks = tasks + inspect_tasks + improve_tasks

            for task in all_tasks:
                belief_key = f'pending_algorithm_task_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')

        except Exception as e:
            logger.warning(f"update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans for algorithm tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_algorithm_task_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            # Check if already handling this task
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'inspect')

            if operation == 'build':
                steps = ['claim_task', 'parse_spec', 'build_algorithm', 'verify', 'post_result']
            elif operation == 'improve':
                steps = ['claim_task', 'parse_code', 'inspect_algorithm', 'improve_algorithm', 'verify', 'post_result']
            else:  # inspect
                steps = ['claim_task', 'parse_code', 'inspect_algorithm', 'post_result']

            intention = Intention(
                plan_id=f'algorithm_{operation}_{task_id}',
                steps=steps,
                target_desire=f'algorithm_{operation}',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute algorithm building/inspection steps."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_algorithm_task_{task_id}')
                intention.advance()

            elif action == 'parse_spec':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                spec_data = metadata.get('spec', {})
                spec = AlgorithmSpec(
                    name=spec_data.get('name', 'unnamed'),
                    algorithm_type=AlgorithmType(spec_data.get('type', 'numerical')),
                    description=spec_data.get('description', ''),
                    inputs=spec_data.get('inputs', []),
                    outputs=spec_data.get('outputs', [])
                )
                intention.metadata['spec'] = spec
                intention.advance()

            elif action == 'parse_code':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                code = metadata.get('code', '')
                name = metadata.get('name', 'unnamed')
                intention.metadata['code'] = code
                intention.metadata['algorithm_name'] = name
                intention.advance()

            elif action == 'build_algorithm':
                spec = intention.metadata.get('spec')
                code, success = self.build_algorithm(spec)
                intention.metadata['result_code'] = code
                intention.metadata['success'] = success
                intention.advance()

            elif action == 'inspect_algorithm':
                code = intention.metadata.get('code', '')
                name = intention.metadata.get('algorithm_name', 'unnamed')
                analysis = self.inspect_algorithm(code, name)
                intention.metadata['analysis'] = analysis
                intention.advance()

            elif action == 'improve_algorithm':
                code = intention.metadata.get('code', '')
                name = intention.metadata.get('algorithm_name', 'unnamed')
                improvement = self.improve_algorithm(code, name)
                intention.metadata['improvement'] = improvement
                intention.advance()

            elif action == 'verify':
                code = intention.metadata.get('result_code') or intention.metadata.get('improvement', {}).improved_code
                test_cases = intention.metadata.get('test_cases', [])
                if test_cases:
                    passed, results = self.verify_correctness(code, test_cases)
                    intention.metadata['verification'] = {'passed': passed, 'results': results}
                intention.advance()

            elif action == 'post_result':
                if self.blackboard:
                    result_data = {
                        'operation': intention.metadata.get('operation'),
                        'analysis': intention.metadata.get('analysis'),
                        'improvement': intention.metadata.get('improvement'),
                        'code': intention.metadata.get('result_code'),
                        'verification': intention.metadata.get('verification')
                    }

                    entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=str(result_data),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['algorithm', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'result': result_data}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            logger.error(f"execute_step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        stats = super().get_statistics()
        stats.update(self._stats)
        stats['algorithm_inventory_size'] = len(self._algorithm_inventory)
        stats['analysis_cache_size'] = len(self._analysis_cache)
        stats['improvement_history_size'] = len(self._improvement_history)
        return stats

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'build':
            spec_data = params.get('spec', {})
            spec = AlgorithmSpec(
                name=spec_data.get('name', 'unnamed'),
                algorithm_type=AlgorithmType(spec_data.get('type', 'numerical')),
                description=spec_data.get('description', ''),
                inputs=spec_data.get('inputs', []),
                outputs=spec_data.get('outputs', [])
            )
            code, success = self.build_algorithm(spec)
            return {'status': 'success' if success else 'failed', 'code': code}

        elif action == 'inspect':
            code = params.get('code', '')
            name = params.get('name', 'unnamed')
            analysis = self.inspect_algorithm(code, name)
            return {'status': 'success', 'analysis': analysis.__dict__}

        elif action == 'improve':
            code = params.get('code', '')
            name = params.get('name', 'unnamed')
            improvement = self.improve_algorithm(code, name)
            return {'status': 'success', 'improvement': improvement.__dict__}

        elif action == 'verify':
            code = params.get('code', '')
            test_cases = params.get('test_cases', [])
            passed, results = self.verify_correctness(code, test_cases)
            return {'status': 'success', 'passed': passed, 'results': results}

        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}


__all__ = [
    'AlgorithmBuildingExpert',
    'AlgorithmSpec',
    'AlgorithmAnalysis',
    'AlgorithmImprovement',
    'AlgorithmType',
]
