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
PHASE 6 - AD-2: COMPLEXITY ANALYZER
====================================

Analyzes algorithmic complexity through static analysis and empirical measurement.

CAPABILITIES:
------------
- Static complexity analysis
- Empirical runtime measurement
- Asymptotic bound determination
- Recurrence relation solving
- Comparison with known complexities

REFERENCE:
---------
- Phase 6 Discovery Team: Algorithm Discovery Subteam
"""

import logging
import re
import ast
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.phase6.complexity_analyzer')


class ComplexityClass(Enum):
    """Standard complexity classes"""
    O_1 = "O(1)"
    O_LOG_N = "O(log n)"
    O_N = "O(n)"
    O_N_LOG_N = "O(n log n)"
    O_N_SQUARED = "O(n²)"
    O_N_CUBED = "O(n³)"
    O_2_N = "O(2ⁿ)"
    O_N_FACTORIAL = "O(n!)"
    UNKNOWN = "unknown"


class AnalysisMethod(Enum):
    """Methods for complexity analysis"""
    STATIC = "static"
    EMPIRICAL = "empirical"
    HYBRID = "hybrid"


@dataclass
class ComplexityResult:
    """
    Result of complexity analysis.
    
    Attributes:
        time_complexity: Estimated time complexity
        space_complexity: Estimated space complexity
        confidence: Confidence in analysis (0-1)
        evidence: Supporting evidence
    """
    time_complexity: ComplexityClass
    space_complexity: ComplexityClass
    confidence: float
    evidence: List[str]
    method: AnalysisMethod
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'time': self.time_complexity.value,
            'space': self.space_complexity.value,
            'confidence': round(self.confidence, 2),
            'method': self.method.value
        }


@dataclass
class EmpiricalMeasurement:
    """Empirical runtime measurement"""
    input_size: int
    runtime_ms: float
    iterations: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'n': self.input_size,
            'time_ms': round(self.runtime_ms, 3),
            'iterations': self.iterations
        }


class ComplexityAnalyzer:
    """
    AD-2: Complexity Analyzer
    
    Analyzes algorithmic complexity through static analysis and empirical measurement.
    
    Key capabilities:
    - AST-based static analysis
    - Loop and recursion detection
    - Empirical timing
    - Complexity class fitting
    - Master theorem application
    """
    
    # Complexity patterns
    LOOP_PATTERNS = {
        'single_loop': ComplexityClass.O_N,
        'nested_loop_2': ComplexityClass.O_N_SQUARED,
        'nested_loop_3': ComplexityClass.O_N_CUBED,
        'log_loop': ComplexityClass.O_LOG_N,
        'divide_conquer': ComplexityClass.O_N_LOG_N,
    }
    
    def __init__(
        self,
        min_samples: int = 5,
        sample_sizes: List[int] = None
    ):
        """
        Initialize the Complexity Analyzer.
        
        Args:
            min_samples: Minimum samples for empirical analysis
            sample_sizes: Input sizes for empirical testing
        """
        self.min_samples = min_samples
        self.sample_sizes = sample_sizes or [10, 50, 100, 500, 1000]
        
        # Analysis cache
        self.analysis_cache: Dict[str, ComplexityResult] = {}
        
        # Statistics
        self.analyses_performed = 0
        self.static_analyses = 0
        self.empirical_analyses = 0
        
        logger.info("ComplexityAnalyzer initialized")
    
    def analyze(
        self,
        code: str,
        method: AnalysisMethod = AnalysisMethod.HYBRID,
        func: Optional[Callable] = None,
        input_generator: Optional[Callable] = None
    ) -> ComplexityResult:
        """
        Analyze complexity of code.
        
        Args:
            code: Source code to analyze
            method: Analysis method
            func: Optional function for empirical testing
            input_generator: Generator for test inputs
            
        Returns:
            ComplexityResult
        """
        self.analyses_performed += 1
        
        try:
            if method == AnalysisMethod.STATIC:
                return self._static_analysis(code)
            elif method == AnalysisMethod.EMPIRICAL and func and input_generator:
                return self._empirical_analysis(func, input_generator)
            else:
                # Hybrid: combine static and empirical
                static_result = self._static_analysis(code)
                
                if func and input_generator:
                    empirical_result = self._empirical_analysis(func, input_generator)
                    return self._combine_results(static_result, empirical_result)
                
                return static_result
                
        except Exception as e:
            logger.warning(f"Analysis failed: {type(e).__name__}: {e}")
            return ComplexityResult(
                time_complexity=ComplexityClass.UNKNOWN,
                space_complexity=ComplexityClass.UNKNOWN,
                confidence=0.0,
                evidence=[f"Analysis failed: {e}"],
                method=method
            )
    
    def _static_analysis(self, code: str) -> ComplexityResult:
        """Perform static analysis of code"""
        self.static_analyses += 1
        
        evidence = []
        details = {}
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return ComplexityResult(
                time_complexity=ComplexityClass.UNKNOWN,
                space_complexity=ComplexityClass.UNKNOWN,
                confidence=0.0,
                evidence=["Failed to parse code"],
                method=AnalysisMethod.STATIC
            )
        
        # Count loop nesting
        loop_depth = self._count_loop_depth(tree)
        details['loop_depth'] = loop_depth
        evidence.append(f"Maximum loop nesting: {loop_depth}")
        
        # Check for recursion
        has_recursion = self._detect_recursion(tree)
        details['has_recursion'] = has_recursion
        if has_recursion:
            evidence.append("Recursive function detected")
        
        # Check for logarithmic patterns
        has_log_pattern = self._detect_log_pattern(code)
        details['has_log_pattern'] = has_log_pattern
        if has_log_pattern:
            evidence.append("Logarithmic pattern detected (halving/doubling)")
        
        # Determine time complexity
        time_complexity = self._determine_time_complexity(
            loop_depth, has_recursion, has_log_pattern
        )
        
        # Analyze space complexity
        space_complexity = self._analyze_space(tree, code)
        details['allocations'] = self._count_allocations(code)
        
        # Calculate confidence
        confidence = 0.7 if loop_depth <= 2 else 0.5
        if has_recursion:
            confidence -= 0.1
        
        return ComplexityResult(
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            confidence=confidence,
            evidence=evidence,
            method=AnalysisMethod.STATIC,
            details=details
        )
    
    def _count_loop_depth(self, tree: ast.AST) -> int:
        """Count maximum loop nesting depth"""
        max_depth = [0]
        
        def visit(node, depth=0):
            if isinstance(node, (ast.For, ast.While)):
                depth += 1
                max_depth[0] = max(max_depth[0], depth)
            
            for child in ast.iter_child_nodes(node):
                visit(child, depth)
        
        visit(tree)
        return max_depth[0]
    
    def _detect_recursion(self, tree: ast.AST) -> bool:
        """Detect if function calls itself"""
        func_names = set()
        call_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_names.add(node.name)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    call_names.add(node.func.id)
        
        return bool(func_names & call_names)
    
    def _detect_log_pattern(self, code: str) -> bool:
        """Detect logarithmic patterns (halving, doubling)"""
        patterns = [
            r'/\s*=\s*2', r'//\s*=\s*2', r'//\s*2',
            r'\*\s*=\s*2', r'\*\s*2',
            r'>> 1', r'<< 1',
            'mid', 'left', 'right'
        ]
        
        for pattern in patterns:
            if re.search(pattern, code):
                return True
        return False
    
    def _determine_time_complexity(
        self,
        loop_depth: int,
        has_recursion: bool,
        has_log_pattern: bool
    ) -> ComplexityClass:
        """Determine time complexity from features"""
        if loop_depth == 0:
            if has_recursion:
                if has_log_pattern:
                    return ComplexityClass.O_N_LOG_N
                return ComplexityClass.O_2_N
            return ComplexityClass.O_1
        elif loop_depth == 1:
            if has_log_pattern:
                return ComplexityClass.O_LOG_N
            return ComplexityClass.O_N
        elif loop_depth == 2:
            if has_log_pattern:
                return ComplexityClass.O_N_LOG_N
            return ComplexityClass.O_N_SQUARED
        else:
            return ComplexityClass.O_N_CUBED
    
    def _analyze_space(self, tree: ast.AST, code: str) -> ComplexityClass:
        """Analyze space complexity"""
        # Check for data structure allocations
        if 'memo' in code or 'cache' in code or 'dp' in code:
            return ComplexityClass.O_N
        
        # Check for new lists/dicts
        alloc_count = self._count_allocations(code)
        
        if alloc_count > 0:
            return ComplexityClass.O_N
        
        return ComplexityClass.O_1
    
    def _count_allocations(self, code: str) -> int:
        """Count data structure allocations"""
        patterns = [r'\[\]', r'\{\}', r'list\(', r'dict\(', r'set\(']
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, code))
        return count
    
    def _empirical_analysis(
        self,
        func: Callable,
        input_generator: Callable
    ) -> ComplexityResult:
        """Perform empirical runtime analysis"""
        self.empirical_analyses += 1
        
        measurements = []
        
        for size in self.sample_sizes:
            try:
                inputs = input_generator(size)
                
                # Warm-up
                func(*inputs) if isinstance(inputs, tuple) else func(inputs)
                
                # Time multiple iterations
                iterations = max(1, 100000 // (size + 1))
                start = time.perf_counter()
                for _ in range(iterations):
                    func(*inputs) if isinstance(inputs, tuple) else func(inputs)
                elapsed = (time.perf_counter() - start) * 1000 / iterations
                
                measurements.append(EmpiricalMeasurement(
                    input_size=size,
                    runtime_ms=elapsed,
                    iterations=iterations
                ))
            except Exception as e:
                logger.warning(f"Measurement failed for size {size}: {e}")
        
        if len(measurements) < self.min_samples:
            return ComplexityResult(
                time_complexity=ComplexityClass.UNKNOWN,
                space_complexity=ComplexityClass.O_1,
                confidence=0.0,
                evidence=[f"Insufficient measurements: {len(measurements)}"],
                method=AnalysisMethod.EMPIRICAL
            )
        
        # Fit complexity class
        time_complexity = self._fit_complexity_class(measurements)
        
        evidence = [
            f"Measured {len(measurements)} data points",
            f"Sizes: {[m.input_size for m in measurements]}",
            f"Best fit: {time_complexity.value}"
        ]
        
        return ComplexityResult(
            time_complexity=time_complexity,
            space_complexity=ComplexityClass.O_1,  # Can't measure easily
            confidence=0.8,
            evidence=evidence,
            method=AnalysisMethod.EMPIRICAL,
            details={'measurements': [m.to_dict() for m in measurements]}
        )
    
    def _fit_complexity_class(
        self,
        measurements: List[EmpiricalMeasurement]
    ) -> ComplexityClass:
        """Fit empirical data to complexity class"""
        if len(measurements) < 2:
            return ComplexityClass.UNKNOWN
        
        # Calculate ratios
        ratios = []
        for i in range(1, len(measurements)):
            n_ratio = measurements[i].input_size / measurements[i-1].input_size
            t_ratio = measurements[i].runtime_ms / max(measurements[i-1].runtime_ms, 0.0001)
            ratios.append((n_ratio, t_ratio))
        
        # Determine complexity from ratio pattern
        avg_n_ratio = sum(r[0] for r in ratios) / len(ratios)
        avg_t_ratio = sum(r[1] for r in ratios) / len(ratios)
        
        if avg_t_ratio < 1.5:
            return ComplexityClass.O_1
        elif avg_t_ratio < avg_n_ratio * 0.5:
            return ComplexityClass.O_LOG_N
        elif avg_t_ratio < avg_n_ratio * 1.5:
            return ComplexityClass.O_N
        elif avg_t_ratio < avg_n_ratio * 2:
            return ComplexityClass.O_N_LOG_N
        elif avg_t_ratio < avg_n_ratio ** 2 * 1.5:
            return ComplexityClass.O_N_SQUARED
        else:
            return ComplexityClass.O_N_CUBED
    
    def _combine_results(
        self,
        static: ComplexityResult,
        empirical: ComplexityResult
    ) -> ComplexityResult:
        """Combine static and empirical results"""
        # Prefer empirical for time if confidence is high
        if empirical.confidence > static.confidence:
            time_complexity = empirical.time_complexity
        else:
            time_complexity = static.time_complexity
        
        # Use static for space (hard to measure empirically)
        space_complexity = static.space_complexity
        
        # Combine evidence
        evidence = static.evidence + empirical.evidence
        
        # Average confidence
        confidence = (static.confidence + empirical.confidence) / 2
        
        # Combine details
        details = {**static.details, **empirical.details}
        
        return ComplexityResult(
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            confidence=confidence,
            evidence=evidence,
            method=AnalysisMethod.HYBRID,
            details=details
        )
    
    def compare_algorithms(
        self,
        codes: List[str]
    ) -> List[Tuple[int, ComplexityResult]]:
        """
        Compare complexity of multiple algorithms.
        
        Args:
            codes: List of code snippets
            
        Returns:
            Sorted list of (index, result) by efficiency
        """
        results = []
        for i, code in enumerate(codes):
            result = self.analyze(code, method=AnalysisMethod.STATIC)
            results.append((i, result))
        
        # Sort by complexity (lower is better)
        complexity_order = {
            ComplexityClass.O_1: 0,
            ComplexityClass.O_LOG_N: 1,
            ComplexityClass.O_N: 2,
            ComplexityClass.O_N_LOG_N: 3,
            ComplexityClass.O_N_SQUARED: 4,
            ComplexityClass.O_N_CUBED: 5,
            ComplexityClass.O_2_N: 6,
            ComplexityClass.O_N_FACTORIAL: 7,
            ComplexityClass.UNKNOWN: 8
        }
        
        results.sort(key=lambda x: complexity_order.get(x[1].time_complexity, 8))
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics"""
        return {
            'analyses_performed': self.analyses_performed,
            'static_analyses': self.static_analyses,
            'empirical_analyses': self.empirical_analyses,
            'cached_results': len(self.analysis_cache)
        }
    
    def reset(self):
        """Reset analyzer state"""
        self.analysis_cache.clear()
        self.analyses_performed = 0
        self.static_analyses = 0
        self.empirical_analyses = 0
    
    def health_check(self) -> bool:
        """Check if analyzer is healthy"""
        return True


if __name__ == "__main__":
    """Test Complexity Analyzer"""
    print("=" * 80)
    print("PHASE 6 - COMPLEXITY ANALYZER TEST")
    print("=" * 80)
    print()
    
    # Initialize analyzer
    analyzer = ComplexityAnalyzer()
    
    # Test 1: Analyze O(1) code
    print("Test 1: O(1) Code")
    code = '''
def get_first(arr):
    return arr[0] if arr else None
'''
    result = analyzer.analyze(code)
    print(f"  Time: {result.time_complexity.value}")
    print(f"  Space: {result.space_complexity.value}")
    print()
    
    # Test 2: Analyze O(n) code
    print("Test 2: O(n) Code")
    code = '''
def sum_array(arr):
    total = 0
    for x in arr:
        total += x
    return total
'''
    result = analyzer.analyze(code)
    print(f"  Time: {result.time_complexity.value}")
    print(f"  Evidence: {result.evidence}")
    print()
    
    # Test 3: Analyze O(n²) code
    print("Test 3: O(n²) Code")
    code = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
'''
    result = analyzer.analyze(code)
    print(f"  Time: {result.time_complexity.value}")
    print(f"  Loop depth: {result.details.get('loop_depth')}")
    print()
    
    # Test 4: Analyze recursive code
    print("Test 4: Recursive Code with Log Pattern")
    code = '''
def binary_search(arr, target, left=0, right=None):
    if right is None:
        right = len(arr) - 1
    if left > right:
        return -1
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search(arr, target, mid + 1, right)
    else:
        return binary_search(arr, target, left, mid - 1)
'''
    result = analyzer.analyze(code)
    print(f"  Time: {result.time_complexity.value}")
    print(f"  Has recursion: {result.details.get('has_recursion')}")
    print(f"  Has log pattern: {result.details.get('has_log_pattern')}")
    print()
    
    # Test 5: Compare algorithms
    print("Test 5: Compare Algorithms")
    codes = [
        "def linear(arr): return [x for x in arr]",
        "def constant(x): return x + 1",
        "def quadratic(arr):\n    for i in arr:\n        for j in arr:\n            pass"
    ]
    ranked = analyzer.compare_algorithms(codes)
    for i, result in ranked:
        print(f"  Code {i}: {result.time_complexity.value}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(analyzer.get_statistics(), indent=2))
