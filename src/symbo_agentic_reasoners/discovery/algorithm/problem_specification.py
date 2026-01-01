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
Problem Specification
======================

Defines the specification format for algorithm discovery problems.
Used by CodeEvolutionaryProposer and SandboxEvaluator.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Any, Callable, Optional, Dict


@dataclass
class ProblemSpecification:
    """
    Specification for an algorithm discovery problem.

    Attributes:
        problem_id: Unique identifier for the problem
        description: Human-readable description
        function_signature: Python function signature to implement
        test_cases: List of (input, expected_output) pairs
        fitness_fn: Optional custom fitness function
        timeout_seconds: Timeout for code execution
        problem_class: Category of problem (optimization, search, etc.)
        difficulty: Estimated difficulty (1-10)
    """
    problem_id: str
    description: str
    function_signature: str
    test_cases: List[Tuple[Any, Any]]
    fitness_fn: Optional[Callable] = None
    timeout_seconds: float = 5.0
    problem_class: str = 'optimization'
    difficulty: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'problem_id': self.problem_id,
            'description': self.description,
            'function_signature': self.function_signature,
            'num_test_cases': len(self.test_cases),
            'timeout_seconds': self.timeout_seconds,
            'problem_class': self.problem_class,
            'difficulty': self.difficulty
        }

    @classmethod
    def create_knapsack_problem(cls) -> 'ProblemSpecification':
        """Create a standard 0/1 knapsack problem specification"""
        return cls(
            problem_id='knapsack_01',
            description='0/1 Knapsack: maximize value without exceeding capacity',
            function_signature='def solve(weights: List[int], values: List[int], capacity: int) -> int',
            test_cases=[
                (([2, 3, 4, 5], [3, 4, 5, 6], 5), 7),
                (([1, 2, 3], [6, 10, 12], 5), 22),
                (([10, 20, 30], [60, 100, 120], 50), 220),
            ],
            problem_class='optimization',
            difficulty=5
        )

    @classmethod
    def create_subset_sum_problem(cls) -> 'ProblemSpecification':
        """Create a subset sum problem specification"""
        return cls(
            problem_id='subset_sum',
            description='Subset Sum: determine if subset sums to target',
            function_signature='def solve(items: List[int], target: int) -> bool',
            test_cases=[
                (([1, 2, 3, 4], 6), True),
                (([1, 2, 3], 7), False),
                (([5, 10, 15], 25), True),
                (([1, 5, 11, 5], 11), True),
            ],
            problem_class='decision',
            difficulty=4
        )

    @classmethod
    def create_sorting_problem(cls) -> 'ProblemSpecification':
        """Create a sorting problem specification"""
        return cls(
            problem_id='sorting',
            description='Sort a list of integers in ascending order',
            function_signature='def solve(items: List[int]) -> List[int]',
            test_cases=[
                (([3, 1, 4, 1, 5],), [1, 1, 3, 4, 5]),
                (([5, 4, 3, 2, 1],), [1, 2, 3, 4, 5]),
                (([1],), [1]),
                (([],), []),
            ],
            problem_class='sorting',
            difficulty=2
        )

    @classmethod
    def create_bin_packing_problem(cls) -> 'ProblemSpecification':
        """Create a bin packing problem specification"""
        return cls(
            problem_id='bin_packing',
            description='Bin Packing: minimize number of bins to pack items',
            function_signature='def solve(items: List[int], bin_capacity: int) -> int',
            test_cases=[
                (([4, 8, 1, 4, 2, 1], 10), 2),
                (([7, 5, 5, 2, 4, 2, 5, 1, 6], 10), 5),
                (([5, 5, 5, 5], 10), 2),
            ],
            problem_class='optimization',
            difficulty=6
        )
