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
Heuristic Distiller
====================

Agent 3.3 of the Algorithm Discovery Unit

Analyzes successful code to extract the underlying mathematical principle
into human-readable form. Converts "black box" code success into:
- Prose explanation
- Formal specification
- Applicable problem classes

This allows the discovered algorithms to be integrated into the system's
knowledge base for future use.

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 3
Reference: Phase_6_Build_Order_Breakdown.md, Step 3
"""

import re
import ast
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from .code_evolutionary_proposer import CodeCandidate


@dataclass
class DistilledHeuristic:
    """
    A mathematical heuristic extracted from successful code.

    Attributes:
        heuristic_id: Unique identifier
        candidate_id: Source candidate ID
        prose_explanation: Human-readable explanation
        algorithmic_class: Classification (greedy, DP, etc.)
        key_patterns: Key algorithmic patterns identified
        applicable_domains: Problem domains where this applies
        formal_properties: Formal properties (complexity, correctness)
        code: Original successful code
        fitness_score: Fitness of the source candidate
    """
    heuristic_id: str
    candidate_id: str
    prose_explanation: str
    algorithmic_class: str
    key_patterns: List[str]
    applicable_domains: List[str]
    formal_properties: Dict[str, Any]
    code: str
    fitness_score: float
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'heuristic_id': self.heuristic_id,
            'candidate_id': self.candidate_id,
            'prose_explanation': self.prose_explanation,
            'algorithmic_class': self.algorithmic_class,
            'key_patterns': self.key_patterns,
            'applicable_domains': self.applicable_domains,
            'formal_properties': self.formal_properties,
            'fitness_score': self.fitness_score,
            'code_length': len(self.code)
        }


class HeuristicDistiller:
    """
    Agent 3.3: Heuristic Distiller - Extract principles from code

    Analyzes successful algorithms to extract and formalize the
    underlying mathematical principles for knowledge integration.

    Key capabilities:
    - Code structure analysis
    - Algorithm classification
    - Pattern extraction
    - Complexity analysis
    - Prose explanation generation

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    # Algorithm classifications
    ALGORITHM_CLASSES = {
        'dynamic_programming': ['dp', 'memo', 'cache', 'lru_cache', '[['],
        'greedy': ['sorted', 'sort', 'max(', 'min(', 'greedy'],
        'divide_and_conquer': ['mid', '// 2', 'merge', 'left', 'right'],
        'backtracking': ['backtrack', 'return True', 'return False'],
        'branch_and_bound': ['bound', 'prune', 'best_so_far'],
        'memoized_recursion': ['@lru_cache', 'memo[', 'cache['],
        'iterative': ['for ', 'while ', 'iterate'],
        'graph_search': ['visited', 'queue', 'stack', 'bfs', 'dfs'],
        'probabilistic': ['random', 'prob', 'monte_carlo'],
    }

    # Pattern descriptions
    PATTERN_DESCRIPTIONS = {
        'sorting': "Sorting as a preprocessing step to enable efficient selection",
        'memoization': "Caching computed results to avoid redundant calculations",
        'greedy_selection': "Making locally optimal choices at each step",
        'dp_table': "Building solutions bottom-up using a dynamic programming table",
        'recursion': "Breaking the problem into smaller subproblems recursively",
        'early_termination': "Returning early when a solution is found",
        'pruning': "Eliminating branches that cannot lead to optimal solutions",
        'sliding_window': "Maintaining a window of elements for efficient processing",
        'two_pointers': "Using two pointers to scan the data efficiently",
        'heap': "Using a heap data structure for efficient min/max operations",
    }

    def __init__(self, llm_client=None):
        """
        Initialize the Heuristic Distiller.

        Args:
            llm_client: Optional LLM client for enhanced explanations
        """
        self.llm = llm_client

        # Statistics
        self.stats = {
            'heuristics_distilled': 0,
            'patterns_identified': 0,
            'by_class': {}
        }

    def distill(self, candidate: CodeCandidate) -> DistilledHeuristic:
        """
        Extract mathematical heuristic from successful code.

        Args:
            candidate: Successful CodeCandidate to analyze

        Returns:
            DistilledHeuristic with explanation and properties
        """
        self.stats['heuristics_distilled'] += 1

        # Analyze code structure
        analysis = self._analyze_code_structure(candidate.code)

        # Classify algorithm
        algo_class = self._classify_algorithm(candidate.code, analysis)
        self.stats['by_class'][algo_class] = self.stats['by_class'].get(algo_class, 0) + 1

        # Extract patterns
        patterns = self._extract_patterns(candidate.code, analysis)
        self.stats['patterns_identified'] += len(patterns)

        # Identify applicable domains
        domains = self._identify_domains(algo_class, patterns)

        # Analyze formal properties
        properties = self._analyze_formal_properties(candidate.code, analysis)

        # Generate explanation
        explanation = self._generate_explanation(algo_class, patterns, properties)

        return DistilledHeuristic(
            heuristic_id=f"heur_{candidate.candidate_id}",
            candidate_id=candidate.candidate_id,
            prose_explanation=explanation,
            algorithmic_class=algo_class,
            key_patterns=patterns,
            applicable_domains=domains,
            formal_properties=properties,
            code=candidate.code,
            fitness_score=candidate.fitness_score
        )

    def _analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """Analyze the structure of the code"""
        analysis = {
            'has_recursion': False,
            'has_memoization': False,
            'has_loops': False,
            'has_sorting': False,
            'has_dp_table': False,
            'has_early_return': False,
            'has_heap': False,
            'num_functions': 0,
            'max_nesting': 0,
            'uses_builtin_funcs': [],
        }

        # Check for patterns
        analysis['has_recursion'] = self._has_recursion(code)
        analysis['has_memoization'] = 'lru_cache' in code or 'memo' in code.lower()
        analysis['has_loops'] = 'for ' in code or 'while ' in code
        analysis['has_sorting'] = 'sorted' in code or '.sort()' in code
        analysis['has_dp_table'] = '[[' in code and 'for ' in code
        analysis['has_early_return'] = code.count('return') > 1
        analysis['has_heap'] = 'heapq' in code or 'heappush' in code

        # Count functions
        analysis['num_functions'] = code.count('def ')

        # Find max nesting
        analysis['max_nesting'] = self._compute_max_nesting(code)

        # Find used builtins
        builtins = ['max', 'min', 'sum', 'len', 'sorted', 'range', 'enumerate', 'zip']
        analysis['uses_builtin_funcs'] = [b for b in builtins if b + '(' in code]

        return analysis

    def _has_recursion(self, code: str) -> bool:
        """Check if code has recursive calls"""
        # Find function names
        func_names = re.findall(r'def\s+(\w+)\s*\(', code)

        # Check if any function calls itself
        for name in func_names:
            if re.search(rf'{name}\s*\(', code.replace(f'def {name}', '')):
                return True
        return False

    def _compute_max_nesting(self, code: str) -> int:
        """Compute maximum nesting level"""
        max_indent = 0
        for line in code.split('\n'):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4)
        return max_indent

    def _classify_algorithm(self, code: str, analysis: Dict[str, Any]) -> str:
        """Classify the algorithm type"""
        code_lower = code.lower()

        # Score each class
        scores = {}
        for algo_class, keywords in self.ALGORITHM_CLASSES.items():
            score = sum(1 for kw in keywords if kw in code_lower)
            scores[algo_class] = score

        # Use analysis to adjust scores
        if analysis['has_dp_table']:
            scores['dynamic_programming'] = scores.get('dynamic_programming', 0) + 3
        if analysis['has_recursion'] and analysis['has_memoization']:
            scores['memoized_recursion'] = scores.get('memoized_recursion', 0) + 3
        if analysis['has_sorting'] and not analysis['has_dp_table']:
            scores['greedy'] = scores.get('greedy', 0) + 2
        if analysis['has_recursion'] and not analysis['has_memoization']:
            if 'True' in code and 'False' in code:
                scores['backtracking'] = scores.get('backtracking', 0) + 2

        # Return highest scoring class
        if scores:
            best_class = max(scores, key=scores.get)
            if scores[best_class] > 0:
                return best_class

        # Default classification
        if analysis['has_loops'] and not analysis['has_recursion']:
            return 'iterative'

        return 'heuristic'

    def _extract_patterns(self, code: str, analysis: Dict[str, Any]) -> List[str]:
        """Extract key algorithmic patterns"""
        patterns = []

        if analysis['has_sorting']:
            patterns.append("Sorting as preprocessing step")
        if analysis['has_memoization']:
            patterns.append("Memoization for subproblem caching")
        if analysis['has_dp_table']:
            patterns.append("Dynamic programming table construction")
        if analysis['has_early_return']:
            patterns.append("Early termination optimization")
        if analysis['has_heap']:
            patterns.append("Heap-based priority handling")
        if 'max(' in code:
            patterns.append("Greedy maximum selection")
        if 'min(' in code:
            patterns.append("Greedy minimum selection")
        if 'for i in range' in code:
            patterns.append("Linear iteration pattern")
        if 'while ' in code:
            patterns.append("Condition-based iteration")
        if '+ 1' in code or '- 1' in code:
            patterns.append("Incremental update strategy")
        if 'if not ' in code or 'if len(' in code:
            patterns.append("Base case handling")

        return patterns

    def _identify_domains(self, algo_class: str, patterns: List[str]) -> List[str]:
        """Identify problem domains where this heuristic applies"""
        domains = []

        # Class-based domains
        class_domains = {
            'dynamic_programming': ['optimization', 'counting', 'shortest_path'],
            'greedy': ['scheduling', 'selection', 'interval'],
            'memoized_recursion': ['tree_problems', 'graph_problems', 'optimization'],
            'backtracking': ['constraint_satisfaction', 'combinatorial_search'],
            'divide_and_conquer': ['sorting', 'searching', 'matrix_operations'],
            'graph_search': ['pathfinding', 'connectivity', 'cycle_detection'],
        }

        domains.extend(class_domains.get(algo_class, ['general']))

        # Pattern-based domains
        if 'Sorting' in str(patterns):
            domains.append('sorting_based')
        if 'Heap' in str(patterns):
            domains.append('priority_based')
        if 'Dynamic programming' in str(patterns):
            domains.append('optimal_substructure')

        return list(set(domains))

    def _analyze_formal_properties(self, code: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze formal properties of the algorithm"""
        properties = {
            'time_complexity': self._estimate_time_complexity(code, analysis),
            'space_complexity': self._estimate_space_complexity(code, analysis),
            'is_deterministic': 'random' not in code.lower(),
            'is_complete': self._is_complete(code, analysis),
            'is_optimal': self._is_likely_optimal(code, analysis),
        }

        return properties

    def _estimate_time_complexity(self, code: str, analysis: Dict[str, Any]) -> str:
        """Estimate time complexity"""
        # Count nested loops
        nested_loops = 0
        for line in code.split('\n'):
            if 'for ' in line or 'while ' in line:
                indent = len(line) - len(line.lstrip())
                nested_loops = max(nested_loops, indent // 4)

        if analysis['has_recursion'] and not analysis['has_memoization']:
            return 'O(2^n) - exponential (unoptimized recursion)'
        elif analysis['has_dp_table']:
            if nested_loops >= 2:
                return 'O(n*m) or O(n^2) - pseudo-polynomial'
            return 'O(n) - linear'
        elif analysis['has_sorting']:
            return 'O(n log n) - sorting dominated'
        elif nested_loops >= 3:
            return 'O(n^3) - cubic'
        elif nested_loops >= 2:
            return 'O(n^2) - quadratic'
        elif analysis['has_loops']:
            return 'O(n) - linear'
        else:
            return 'O(1) - constant'

    def _estimate_space_complexity(self, code: str, analysis: Dict[str, Any]) -> str:
        """Estimate space complexity"""
        if analysis['has_dp_table']:
            if code.count('[') > 3:
                return 'O(n*m) - 2D table'
            return 'O(n) - 1D table or optimized'
        elif analysis['has_memoization']:
            return 'O(n) to O(n^2) - memoization cache'
        elif analysis['has_recursion']:
            return 'O(n) - call stack'
        elif 'set(' in code or 'dict(' in code:
            return 'O(n) - auxiliary data structure'
        else:
            return 'O(1) - constant'

    def _is_complete(self, code: str, analysis: Dict[str, Any]) -> bool:
        """Check if algorithm appears to be complete (always finds a solution)"""
        # Greedy and DP algorithms are typically complete
        if analysis['has_dp_table']:
            return True
        if analysis['has_sorting'] and 'max(' in code:
            return True
        # Backtracking might not find solutions
        if 'return False' in code and 'return True' in code:
            return True  # Decision problem - complete
        return True

    def _is_likely_optimal(self, code: str, analysis: Dict[str, Any]) -> bool:
        """Check if algorithm is likely optimal"""
        # DP typically gives optimal solutions
        if analysis['has_dp_table']:
            return True
        if analysis['has_recursion'] and analysis['has_memoization']:
            return True
        # Greedy is often not optimal
        if analysis['has_sorting'] and not analysis['has_dp_table']:
            return False
        return False

    def _generate_explanation(
        self,
        algo_class: str,
        patterns: List[str],
        properties: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation of the heuristic"""
        # Build explanation
        class_descriptions = {
            'dynamic_programming': "uses a dynamic programming approach to build optimal solutions from subproblems",
            'greedy': "employs a greedy strategy, making locally optimal choices at each step",
            'memoized_recursion': "combines recursive problem decomposition with memoization to avoid redundant computation",
            'backtracking': "uses backtracking to explore the solution space, pruning invalid branches early",
            'divide_and_conquer': "divides the problem into smaller subproblems, solves them independently, and combines the results",
            'iterative': "uses an iterative approach to process elements sequentially",
            'graph_search': "employs graph search techniques to explore the solution space",
            'heuristic': "uses a custom heuristic approach",
        }

        explanation = f"This algorithm {class_descriptions.get(algo_class, 'uses a custom approach')}. "

        if patterns:
            explanation += f"Key techniques include: {', '.join(patterns[:3])}. "

        if properties.get('is_optimal'):
            explanation += "The algorithm is designed to find optimal solutions. "
        else:
            explanation += "The algorithm may find approximate solutions. "

        explanation += f"Time complexity: {properties.get('time_complexity', 'unknown')}. "
        explanation += f"Space complexity: {properties.get('space_complexity', 'unknown')}."

        return explanation

    def get_statistics(self) -> Dict[str, Any]:
        """Get distiller statistics"""
        return {
            **self.stats,
            'unique_classes': len(self.stats['by_class']),
            'class_distribution': self.stats['by_class']
        }

    def reset(self):
        """Reset distiller state"""
        self.stats = {
            'heuristics_distilled': 0,
            'patterns_identified': 0,
            'by_class': {}
        }

    def health_check(self) -> bool:
        """Check if distiller is healthy"""
        return True
