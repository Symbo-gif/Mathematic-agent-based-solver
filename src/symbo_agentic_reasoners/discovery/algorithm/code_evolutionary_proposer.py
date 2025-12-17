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
Code Evolutionary Proposer
===========================

Agent 3.1 of the Algorithm Discovery Unit

LLM-based agent that generates Python/Julia code snippets representing
heuristics. Does not solve the math directly - writes the program to solve
the math. Uses evolutionary logic, taking best code from previous generation
and mutating to find optimizations.

Examples of discoveries:
- "A new way to pack bins"
- "A faster matrix multiplication algorithm"
- "An improved primality test"

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 3
Reference: Phase_6_Build_Order_Breakdown.md, Step 3
"""

import logging
import re
import random
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from .problem_specification import ProblemSpecification

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.algorithm_discovery.code_evolutionary_proposer')
except ImportError:
    logger = logging.getLogger(__name__)


class MutationType(Enum):
    """Types of code mutations"""
    TWEAK_CONSTANT = 'tweak_constant'
    SWAP_OPERATORS = 'swap_operators'
    ADD_CONDITION = 'add_condition'
    REMOVE_CODE = 'remove_code'
    RESTRUCTURE_LOOP = 'restructure_loop'
    COMBINE_PARENTS = 'combine_parents'
    INSERT_OPTIMIZATION = 'insert_optimization'
    CHANGE_DATA_STRUCTURE = 'change_data_structure'


@dataclass
class CodeCandidate:
    """
    A candidate code solution in the evolutionary search.

    Attributes:
        candidate_id: Unique identifier
        code: Python code implementing the solution
        generation: Generation number in evolution
        parent_id: Parent candidate ID (if mutated)
        fitness_score: Overall fitness (0-1)
        execution_time_ms: Execution time
        correctness_score: Fraction of test cases passed
        mutation_type: Type of mutation that created this
    """
    candidate_id: str
    code: str
    generation: int
    parent_id: Optional[str] = None
    fitness_score: float = 0.0
    execution_time_ms: float = 0.0
    correctness_score: float = 0.0
    mutation_type: str = 'initial'
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'candidate_id': self.candidate_id,
            'generation': self.generation,
            'parent_id': self.parent_id,
            'fitness_score': self.fitness_score,
            'correctness_score': self.correctness_score,
            'execution_time_ms': self.execution_time_ms,
            'mutation_type': self.mutation_type,
            'code_length': len(self.code)
        }


class CodeEvolutionaryProposer:
    """
    Agent 3.1: Code Evolutionary Proposer - FunSearch-style code evolution

    Evolves code solutions through mutation and selection. Uses multiple
    mutation strategies to explore the solution space efficiently.

    Key capabilities:
    - Template-based initial population generation
    - Multiple mutation strategies
    - Elite preservation
    - Crossover between high-fitness candidates

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    # Available mutation types
    MUTATION_TYPES = list(MutationType)

    def __init__(
        self,
        llm_client=None,
        problem_spec: ProblemSpecification = None,
        elite_size: int = 10,
        mutation_rate: float = 0.8,
        crossover_rate: float = 0.2
    ):
        """
        Initialize the Code Evolutionary Proposer.

        Args:
            llm_client: Optional LLM client for advanced mutations
            problem_spec: Problem specification
            elite_size: Number of elite candidates to preserve
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
        """
        self.llm = llm_client
        self.problem_spec = problem_spec
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

        self.population: List[CodeCandidate] = []
        self.generation = 0
        self.best_candidate: Optional[CodeCandidate] = None

        # Statistics
        self.stats = {
            'generations_evolved': 0,
            'total_candidates': 0,
            'best_fitness': 0.0,
            'mutations_applied': 0,
            'crossovers_applied': 0
        }

    def initialize_population(self, size: int = 20) -> List[CodeCandidate]:
        """
        Generate initial population of code candidates.

        Args:
            size: Population size

        Returns:
            List of initial CodeCandidate objects
        """
        candidates = []
        templates = self._get_templates()

        for i in range(size):
            # Select template and apply variation
            template = random.choice(templates)
            code = self._apply_initial_variation(template)

            candidate = CodeCandidate(
                candidate_id=f"gen0_{uuid.uuid4().hex[:6]}",
                code=code,
                generation=0,
                mutation_type='initial'
            )
            candidates.append(candidate)
            self.stats['total_candidates'] += 1

        self.population = candidates
        return candidates

    def generate_initial_population(
        self,
        problem_spec: ProblemSpecification,
        size: int = 20
    ) -> List[CodeCandidate]:
        """
        Generate initial population for a given problem.

        Args:
            problem_spec: Problem specification
            size: Population size

        Returns:
            List of initial CodeCandidate objects
        """
        self.problem_spec = problem_spec
        return self.initialize_population(size)

    def _get_templates(self) -> List[str]:
        """Get code templates based on problem specification"""
        if self.problem_spec is None:
            return [self._generic_template()]

        problem_class = self.problem_spec.problem_class
        signature = self.problem_spec.function_signature

        templates = []

        # Add class-specific templates
        if problem_class == 'optimization':
            templates.extend([
                self._greedy_template(signature),
                self._dp_template(signature),
                self._recursive_template(signature)
            ])
        elif problem_class == 'decision':
            templates.extend([
                self._backtracking_template(signature),
                self._dp_template(signature),
                self._iterative_template(signature)
            ])
        elif problem_class == 'sorting':
            templates.extend([
                self._quicksort_template(signature),
                self._mergesort_template(signature),
                self._heapsort_template(signature)
            ])
        else:
            templates.append(self._generic_template())

        return templates

    def _generic_template(self) -> str:
        """Generic solution template"""
        return '''
def solve(*args):
    """Generic solution"""
    if not args:
        return None
    data = args[0]
    result = []
    for item in data:
        result.append(item)
    return result
'''

    def _greedy_template(self, signature: str) -> str:
        """Greedy algorithm template"""
        return f'''
{signature}:
    """Greedy approach - select best local choice"""
    from typing import List

    if not weights or not values:
        return 0

    # Sort by value-to-weight ratio
    items = list(zip(weights, values, range(len(weights))))
    items.sort(key=lambda x: x[1]/max(x[0], 1), reverse=True)

    total_value = 0
    remaining = capacity

    for w, v, i in items:
        if w <= remaining:
            total_value += v
            remaining -= w

    return total_value
'''

    def _dp_template(self, signature: str) -> str:
        """Dynamic programming template"""
        return f'''
{signature}:
    """Dynamic programming approach"""
    from typing import List

    if not weights or not values:
        return 0

    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(
                    dp[i-1][w],
                    dp[i-1][w - weights[i-1]] + values[i-1]
                )
            else:
                dp[i][w] = dp[i-1][w]

    return dp[n][capacity]
'''

    def _recursive_template(self, signature: str) -> str:
        """Recursive with memoization template"""
        return f'''
{signature}:
    """Recursive approach with memoization"""
    from typing import List
    from functools import lru_cache

    if not weights or not values:
        return 0

    n = len(weights)

    @lru_cache(maxsize=None)
    def helper(i, remaining):
        if i >= n or remaining <= 0:
            return 0

        skip = helper(i + 1, remaining)
        take = 0
        if weights[i] <= remaining:
            take = values[i] + helper(i + 1, remaining - weights[i])

        return max(skip, take)

    return helper(0, capacity)
'''

    def _backtracking_template(self, signature: str) -> str:
        """Backtracking template for decision problems"""
        return f'''
{signature}:
    """Backtracking approach"""
    from typing import List

    if target == 0:
        return True
    if not items:
        return target == 0

    def backtrack(index, remaining):
        if remaining == 0:
            return True
        if remaining < 0 or index >= len(items):
            return False

        # Try including current item
        if backtrack(index + 1, remaining - items[index]):
            return True

        # Try excluding current item
        return backtrack(index + 1, remaining)

    return backtrack(0, target)
'''

    def _iterative_template(self, signature: str) -> str:
        """Iterative template"""
        return f'''
{signature}:
    """Iterative approach with set"""
    from typing import List

    reachable = {{0}}

    for item in items:
        new_reachable = set()
        for s in reachable:
            new_sum = s + item
            if new_sum == target:
                return True
            if new_sum < target:
                new_reachable.add(new_sum)
        reachable.update(new_reachable)

    return target in reachable
'''

    def _quicksort_template(self, signature: str) -> str:
        """Quicksort template"""
        return f'''
{signature}:
    """Quicksort approach"""
    from typing import List

    if len(items) <= 1:
        return list(items)

    pivot = items[len(items) // 2]
    left = [x for x in items if x < pivot]
    middle = [x for x in items if x == pivot]
    right = [x for x in items if x > pivot]

    return solve(left) + middle + solve(right)
'''

    def _mergesort_template(self, signature: str) -> str:
        """Mergesort template"""
        return f'''
{signature}:
    """Mergesort approach"""
    from typing import List

    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = solve(items[:mid])
    right = solve(items[mid:])

    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])

    return result
'''

    def _heapsort_template(self, signature: str) -> str:
        """Heapsort template"""
        return f'''
{signature}:
    """Heapsort approach"""
    from typing import List
    import heapq

    heap = list(items)
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(len(heap))]
'''

    def _apply_initial_variation(self, template: str) -> str:
        """Apply random variation to initial template"""
        # Small random tweaks to constants
        code = template

        # Randomly modify numeric constants
        def tweak_number(match):
            val = int(match.group())
            if random.random() < 0.3:
                return str(val + random.randint(-2, 2))
            return str(val)

        code = re.sub(r'\b([2-9]|1[0-9])\b', tweak_number, code)

        return code

    def evolve(self, evaluated_population: List[CodeCandidate]) -> List[CodeCandidate]:
        """
        Evolve population based on fitness.

        Args:
            evaluated_population: Population with fitness scores

        Returns:
            New generation of candidates
        """
        self.generation += 1
        self.stats['generations_evolved'] += 1

        # Sort by fitness
        sorted_pop = sorted(
            evaluated_population,
            key=lambda c: c.fitness_score,
            reverse=True
        )

        # Update best candidate
        if sorted_pop and (self.best_candidate is None or
                          sorted_pop[0].fitness_score > self.best_candidate.fitness_score):
            self.best_candidate = sorted_pop[0]
            self.stats['best_fitness'] = sorted_pop[0].fitness_score

        # Keep elite
        elite = sorted_pop[:self.elite_size]

        # Generate new population
        new_population = list(elite)
        target_size = len(evaluated_population)

        while len(new_population) < target_size:
            if random.random() < self.crossover_rate and len(elite) >= 2:
                # Crossover
                parent1, parent2 = random.sample(elite, 2)
                child = self._crossover(parent1, parent2)
                self.stats['crossovers_applied'] += 1
            else:
                # Mutation
                parent = random.choice(elite)
                child = self._mutate(parent)
                self.stats['mutations_applied'] += 1

            new_population.append(child)
            self.stats['total_candidates'] += 1

        self.population = new_population
        return new_population

    def _mutate(self, parent: CodeCandidate) -> CodeCandidate:
        """Apply mutation to create child"""
        mutation_type = random.choice(self.MUTATION_TYPES)
        mutated_code = self._apply_mutation(parent.code, mutation_type)

        return CodeCandidate(
            candidate_id=f"gen{self.generation}_{uuid.uuid4().hex[:6]}",
            code=mutated_code,
            generation=self.generation,
            parent_id=parent.candidate_id,
            mutation_type=mutation_type.value
        )

    def _apply_mutation(self, code: str, mutation_type: MutationType) -> str:
        """Apply specific mutation type to code"""
        if mutation_type == MutationType.TWEAK_CONSTANT:
            return self._tweak_constants(code)
        elif mutation_type == MutationType.SWAP_OPERATORS:
            return self._swap_operators(code)
        elif mutation_type == MutationType.ADD_CONDITION:
            return self._add_condition(code)
        elif mutation_type == MutationType.REMOVE_CODE:
            return self._remove_code(code)
        elif mutation_type == MutationType.RESTRUCTURE_LOOP:
            return self._restructure_loop(code)
        elif mutation_type == MutationType.INSERT_OPTIMIZATION:
            return self._insert_optimization(code)
        elif mutation_type == MutationType.CHANGE_DATA_STRUCTURE:
            return self._change_data_structure(code)
        else:
            return code

    def _tweak_constants(self, code: str) -> str:
        """Tweak numeric constants in code"""
        def tweak(match):
            val = float(match.group())
            if val == 0:
                return str(random.randint(0, 2))
            new_val = val * random.uniform(0.5, 2.0)
            if '.' not in match.group():
                return str(int(new_val))
            return str(round(new_val, 2))

        # Only tweak some numbers
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if random.random() < 0.3:
                lines[i] = re.sub(r'\b\d+\.?\d*\b', tweak, line)

        return '\n'.join(lines)

    def _swap_operators(self, code: str) -> str:
        """Swap operators in code"""
        swaps = [
            (r'\+', '-'), (r'-', '+'),
            (r'\*', '/'), (r'/', '*'),
            (r'>', '<'), (r'<', '>'),
            (r'>=', '<='), (r'<=', '>='),
            (r'max', 'min'), (r'min', 'max'),
            (r'and', 'or'), (r'or', 'and'),
        ]

        old, new = random.choice(swaps)
        # Only replace first occurrence
        return re.sub(old, new, code, count=1)

    def _add_condition(self, code: str) -> str:
        """Add a conditional check"""
        conditions = [
            "if len(items) == 0: return 0\n    ",
            "if remaining <= 0: return result\n    ",
            "if i >= len(items): break\n    ",
        ]

        lines = code.split('\n')
        # Find a good place to insert
        for i, line in enumerate(lines):
            if 'for' in line or 'while' in line:
                indent = len(line) - len(line.lstrip())
                condition = ' ' * (indent + 4) + random.choice(conditions).strip()
                lines.insert(i + 1, condition)
                break

        return '\n'.join(lines)

    def _remove_code(self, code: str) -> str:
        """Remove a line of code (carefully)"""
        lines = code.split('\n')

        # Find removable lines (not def, return, or essential)
        removable = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped and
                not stripped.startswith('def ') and
                not stripped.startswith('return ') and
                not stripped.startswith('"""') and
                not stripped.startswith('#') and
                'import' not in stripped):
                removable.append(i)

        if removable and len(lines) > 5:
            idx = random.choice(removable)
            lines.pop(idx)

        return '\n'.join(lines)

    def _restructure_loop(self, code: str) -> str:
        """Restructure a loop (for <-> while, list comp)"""
        # Convert simple for loops to list comprehensions
        for_pattern = r'for (\w+) in (.+):\s*\n\s+(\w+)\.append\(([^)]+)\)'
        match = re.search(for_pattern, code)
        if match:
            var, iterable, list_var, expr = match.groups()
            replacement = f"{list_var} = [{expr} for {var} in {iterable}]"
            code = re.sub(for_pattern, replacement, code, count=1)

        return code

    def _insert_optimization(self, code: str) -> str:
        """Insert common optimization patterns"""
        optimizations = [
            # Early return
            ("if not items:", "if not items: return 0 if 'int' in str(type(items)) else []"),
            # Memoization hint
            ("def helper(", "@lru_cache(maxsize=None)\n    def helper("),
            # Sorting for greedy
            ("for item in items:", "items = sorted(items, reverse=True)\n    for item in items:"),
        ]

        for pattern, replacement in optimizations:
            if pattern in code and replacement not in code:
                code = code.replace(pattern, replacement, 1)
                break

        return code

    def _change_data_structure(self, code: str) -> str:
        """Change data structure (list <-> set, dict)"""
        changes = [
            (r'\[\]', 'set()'),
            (r'\.append\(', '.add('),
            (r'list\(', 'set('),
        ]

        if random.random() < 0.5:
            old, new = random.choice(changes)
            code = re.sub(old, new, code, count=1)

        return code

    def _crossover(self, parent1: CodeCandidate, parent2: CodeCandidate) -> CodeCandidate:
        """Combine two parents to create child"""
        lines1 = parent1.code.split('\n')
        lines2 = parent2.code.split('\n')

        # Simple crossover: take some lines from each
        crossover_point = len(lines1) // 2
        child_lines = lines1[:crossover_point]

        # Add lines from parent2 that aren't duplicates
        for line in lines2[crossover_point:]:
            if line not in child_lines:
                child_lines.append(line)

        return CodeCandidate(
            candidate_id=f"gen{self.generation}_{uuid.uuid4().hex[:6]}",
            code='\n'.join(child_lines),
            generation=self.generation,
            parent_id=f"{parent1.candidate_id}+{parent2.candidate_id}",
            mutation_type='crossover'
        )

    def get_best(self) -> Optional[CodeCandidate]:
        """Get best candidate found so far"""
        return self.best_candidate

    def get_statistics(self) -> Dict[str, Any]:
        """Get proposer statistics"""
        return {
            **self.stats,
            'current_generation': self.generation,
            'population_size': len(self.population)
        }

    def reset(self):
        """Reset proposer state"""
        self.population.clear()
        self.generation = 0
        self.best_candidate = None
        for key in self.stats:
            self.stats[key] = 0

    def set_problem(self, problem_spec: ProblemSpecification):
        """Set the problem specification."""
        self.problem_spec = problem_spec

    def health_check(self) -> bool:
        """Check if proposer is healthy"""
        try:
            templates = self._get_templates()
            return len(templates) > 0
        except (TypeError, ValueError, RuntimeError) as e:
            logger.warning(f"CodeEvolutionaryProposer health check failed: {e}")
            return False
