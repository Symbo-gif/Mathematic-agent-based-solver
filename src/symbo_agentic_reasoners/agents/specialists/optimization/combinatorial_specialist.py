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
COMBINATORIAL OPTIMIZATION SPECIALIST (Tier 3)
==============================================

Native Python implementation for combinatorial optimization.
Implements algorithms for TSP, knapsack, assignment, and related problems.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from itertools import permutations
import heapq

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class CombinatorialOptimizationSpecialist(BDIAgent):
    """
    Specialist for combinatorial optimization problems.

    Capabilities:
    - Knapsack (0/1 and fractional)
    - Traveling Salesman Problem (nearest neighbor, 2-opt)
    - Assignment problem (Hungarian algorithm)
    - Set cover (greedy)
    - Bin packing
    """

    def __init__(self, agent_id: str = 'combinatorial_specialist_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.optimization.combinatorial',
                agent_id=agent_id,
                algorithm='native_combinatorial',
                cost='high',
                instance=self,
                tier='3',
                capabilities='knapsack_tsp_assignment_setcover'
            ))

        logger.info(f"[{agent_id}] Combinatorial Optimization Specialist initialized")

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for combinatorial tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['combinatorial'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['knapsack'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['tsp'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create optimization plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'knapsack')

            steps = ['claim_task', 'optimize', 'post_result']
            intention = Intention(
                plan_id=f'combinatorial_{operation}_{task_id}',
                steps=steps,
                target_desire='combinatorial_optimization',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Solve combinatorial problems."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'claim_task':
            self.add_belief(f'claimed_task_{task.entry_id}', True, confidence=1.0)
            intention.advance()
        elif action == 'optimize':
            self._optimize(intention)
        elif action == 'post_result':
            self._post_result(intention)

    def _optimize(self, intention: Intention):
        """Run optimization algorithm."""
        task = intention.metadata.get('task_entry')
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        operation = metadata.get('operation', 'knapsack')

        try:
            if operation == 'knapsack_01':
                weights = metadata.get('weights', [])
                values = metadata.get('values', [])
                capacity = metadata.get('capacity', 0)
                result = self.knapsack_01(weights, values, capacity)
            elif operation == 'knapsack_fractional':
                weights = metadata.get('weights', [])
                values = metadata.get('values', [])
                capacity = metadata.get('capacity', 0)
                result = self.knapsack_fractional(weights, values, capacity)
            elif operation == 'tsp_nearest_neighbor':
                distances = metadata.get('distances', [])
                start = metadata.get('start', 0)
                result = self.tsp_nearest_neighbor(distances, start)
            elif operation == 'tsp_2opt':
                distances = metadata.get('distances', [])
                result = self.tsp_2opt(distances)
            elif operation == 'assignment':
                cost_matrix = metadata.get('cost_matrix', [])
                result = self.assignment_hungarian(cost_matrix)
            elif operation == 'set_cover':
                universe = metadata.get('universe', [])
                subsets = metadata.get('subsets', [])
                costs = metadata.get('costs', None)
                result = self.set_cover_greedy(universe, subsets, costs)
            elif operation == 'bin_packing':
                items = metadata.get('items', [])
                bin_capacity = metadata.get('bin_capacity', 0)
                result = self.bin_packing_first_fit(items, bin_capacity)
            else:
                result = {'error': f'Unknown operation: {operation}'}

            intention.metadata['result'] = result
            self.tasks_executed += 1
            intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Optimization failed: {e}")
            intention.metadata['result'] = {'error': str(e)}
            intention.advance()

    def _post_result(self, intention: Intention):
        """Post result to blackboard."""
        if self.blackboard:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
            task = intention.metadata.get('task_entry')
            result = intention.metadata.get('result', {})

            result_entry = create_entry(
                content=result,
                entry_type=EntryType.RESULT,
                tags=['combinatorial', 'optimization', 'result'],
                metadata={'source_task': task.entry_id, 'agent': self.agent_id}
            )
            self.blackboard.post_entry(result_entry)
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.COMPLETED)

        intention.mark_completed()

    # =========================================================================
    # KNAPSACK PROBLEMS
    # =========================================================================

    @staticmethod
    def knapsack_01(weights: List[int], values: List[int], capacity: int) -> Dict[str, Any]:
        """
        0/1 Knapsack problem using dynamic programming.

        Args:
            weights: Item weights
            values: Item values
            capacity: Knapsack capacity

        Returns:
            Dictionary with optimal selection and value
        """
        if not weights or not values or len(weights) != len(values):
            return {'error': 'Invalid input'}

        n = len(weights)

        # DP table: dp[i][w] = max value using items 0..i-1 with capacity w
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            for w in range(capacity + 1):
                if weights[i-1] <= w:
                    dp[i][w] = max(
                        dp[i-1][w],  # Don't take item i
                        dp[i-1][w - weights[i-1]] + values[i-1]  # Take item i
                    )
                else:
                    dp[i][w] = dp[i-1][w]

        # Backtrack to find selected items
        selected = []
        w = capacity
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selected.append(i - 1)
                w -= weights[i-1]

        selected.reverse()

        return {
            'max_value': dp[n][capacity],
            'selected_items': selected,
            'total_weight': sum(weights[i] for i in selected),
            'method': 'native_knapsack_01_dp'
        }

    @staticmethod
    def knapsack_fractional(weights: List[float], values: List[float],
                            capacity: float) -> Dict[str, Any]:
        """
        Fractional knapsack problem (greedy solution).

        Args:
            weights: Item weights
            values: Item values
            capacity: Knapsack capacity

        Returns:
            Dictionary with optimal fractions and value
        """
        if not weights or not values or len(weights) != len(values):
            return {'error': 'Invalid input'}

        n = len(weights)

        # Sort by value/weight ratio
        items = [(values[i] / weights[i], weights[i], values[i], i) for i in range(n)]
        items.sort(reverse=True)

        total_value = 0
        fractions = [0.0] * n
        remaining = capacity

        for ratio, w, v, idx in items:
            if remaining >= w:
                # Take whole item
                fractions[idx] = 1.0
                total_value += v
                remaining -= w
            else:
                # Take fraction
                fraction = remaining / w
                fractions[idx] = fraction
                total_value += fraction * v
                remaining = 0
                break

        return {
            'max_value': total_value,
            'fractions': fractions,
            'method': 'native_fractional_knapsack'
        }

    # =========================================================================
    # TRAVELING SALESMAN PROBLEM
    # =========================================================================

    @staticmethod
    def tsp_nearest_neighbor(distances: List[List[float]], start: int = 0) -> Dict[str, Any]:
        """
        Nearest neighbor heuristic for TSP.

        Args:
            distances: Distance matrix
            start: Starting city

        Returns:
            Dictionary with tour and total distance
        """
        n = len(distances)
        if n == 0:
            return {'error': 'Empty distance matrix'}

        visited = [False] * n
        tour = [start]
        visited[start] = True
        total_distance = 0

        current = start
        for _ in range(n - 1):
            # Find nearest unvisited city
            best_next = -1
            best_dist = float('inf')

            for j in range(n):
                if not visited[j] and distances[current][j] < best_dist:
                    best_dist = distances[current][j]
                    best_next = j

            if best_next == -1:
                break

            tour.append(best_next)
            visited[best_next] = True
            total_distance += best_dist
            current = best_next

        # Return to start
        total_distance += distances[current][start]
        tour.append(start)

        return {
            'tour': tour,
            'total_distance': total_distance,
            'method': 'native_tsp_nearest_neighbor'
        }

    @staticmethod
    def tsp_2opt(distances: List[List[float]], max_iterations: int = 1000) -> Dict[str, Any]:
        """
        2-opt improvement heuristic for TSP.

        Args:
            distances: Distance matrix
            max_iterations: Max improvement iterations

        Returns:
            Dictionary with optimized tour
        """
        n = len(distances)
        if n == 0:
            return {'error': 'Empty distance matrix'}

        # Start with nearest neighbor tour
        nn_result = CombinatorialOptimizationSpecialist.tsp_nearest_neighbor(distances, 0)
        tour = nn_result['tour'][:-1]  # Remove duplicate end

        def tour_length(t):
            return sum(distances[t[i]][t[(i+1) % n]] for i in range(n))

        best_distance = tour_length(tour)

        improved = True
        iteration = 0

        while improved and iteration < max_iterations:
            improved = False
            iteration += 1

            for i in range(n - 1):
                for j in range(i + 2, n):
                    if j == n - 1 and i == 0:
                        continue

                    # Try reversing segment [i+1, j]
                    new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
                    new_distance = tour_length(new_tour)

                    if new_distance < best_distance - 1e-10:
                        tour = new_tour
                        best_distance = new_distance
                        improved = True

        tour.append(tour[0])  # Complete the cycle

        return {
            'tour': tour,
            'total_distance': best_distance,
            'iterations': iteration,
            'method': 'native_tsp_2opt'
        }

    # =========================================================================
    # ASSIGNMENT PROBLEM
    # =========================================================================

    @staticmethod
    def assignment_hungarian(cost_matrix: List[List[float]]) -> Dict[str, Any]:
        """
        Hungarian algorithm for assignment problem.

        Simplified implementation using augmenting paths.

        Args:
            cost_matrix: n x n cost matrix

        Returns:
            Dictionary with optimal assignment
        """
        cost = np.array(cost_matrix, dtype=float)
        n = cost.shape[0]

        if cost.shape[0] != cost.shape[1]:
            return {'error': 'Cost matrix must be square'}

        # Make a copy and perform reductions
        cost = cost.copy()

        # Row reduction
        for i in range(n):
            cost[i, :] -= cost[i, :].min()

        # Column reduction
        for j in range(n):
            cost[:, j] -= cost[:, j].min()

        # Find assignment using greedy + refinement
        assignment = [-1] * n  # assignment[i] = j means row i assigned to col j

        def find_assignment():
            row_covered = [False] * n
            col_covered = [False] * n
            assignment = [-1] * n

            # Greedy initial assignment on zeros
            for i in range(n):
                for j in range(n):
                    if cost[i, j] == 0 and not col_covered[j]:
                        assignment[i] = j
                        col_covered[j] = True
                        break

            return assignment

        assignment = find_assignment()

        # If not all assigned, use augmenting paths (simplified)
        unassigned = [i for i in range(n) if assignment[i] == -1]

        for _ in range(n * n):  # Max iterations
            if not unassigned:
                break

            # Find minimum uncovered value and adjust
            row_covered = [assignment[i] != -1 for i in range(n)]
            col_covered = [False] * n
            for i in range(n):
                if assignment[i] != -1:
                    col_covered[assignment[i]] = True

            min_val = float('inf')
            for i in range(n):
                if not row_covered[i]:
                    for j in range(n):
                        if not col_covered[j]:
                            min_val = min(min_val, cost[i, j])

            if min_val == float('inf'):
                break

            for i in range(n):
                for j in range(n):
                    if not row_covered[i] and not col_covered[j]:
                        cost[i, j] -= min_val
                    elif row_covered[i] and col_covered[j]:
                        cost[i, j] += min_val

            assignment = find_assignment()
            unassigned = [i for i in range(n) if assignment[i] == -1]

        # Calculate total cost
        original_cost = np.array(cost_matrix, dtype=float)
        total_cost = sum(original_cost[i, assignment[i]] for i in range(n) if assignment[i] != -1)

        return {
            'assignment': assignment,
            'total_cost': total_cost,
            'method': 'native_hungarian'
        }

    # =========================================================================
    # SET COVER
    # =========================================================================

    @staticmethod
    def set_cover_greedy(universe: List[Any], subsets: List[List[Any]],
                          costs: List[float] = None) -> Dict[str, Any]:
        """
        Greedy approximation for weighted set cover.

        Args:
            universe: Elements to cover
            subsets: List of subsets
            costs: Cost of each subset (default: 1 for all)

        Returns:
            Dictionary with selected subsets
        """
        if not universe or not subsets:
            return {'error': 'Empty input'}

        universe_set = set(universe)
        n_subsets = len(subsets)

        if costs is None:
            costs = [1.0] * n_subsets

        # Convert subsets to sets
        subset_sets = [set(s) for s in subsets]

        covered = set()
        selected = []
        total_cost = 0

        while covered != universe_set:
            # Find subset with best cost-effectiveness
            best_idx = -1
            best_ratio = float('inf')

            for i in range(n_subsets):
                if i in selected:
                    continue

                new_elements = subset_sets[i] - covered
                if len(new_elements) == 0:
                    continue

                ratio = costs[i] / len(new_elements)
                if ratio < best_ratio:
                    best_ratio = ratio
                    best_idx = i

            if best_idx == -1:
                return {'error': 'Cannot cover all elements'}

            selected.append(best_idx)
            covered |= subset_sets[best_idx]
            total_cost += costs[best_idx]

        return {
            'selected_subsets': selected,
            'total_cost': total_cost,
            'num_subsets': len(selected),
            'method': 'native_greedy_set_cover'
        }

    # =========================================================================
    # BIN PACKING
    # =========================================================================

    @staticmethod
    def bin_packing_first_fit(items: List[float], bin_capacity: float) -> Dict[str, Any]:
        """
        First-fit decreasing bin packing.

        Args:
            items: List of item sizes
            bin_capacity: Capacity of each bin

        Returns:
            Dictionary with bin assignments
        """
        if not items:
            return {'error': 'Empty items list'}

        # Sort items in decreasing order
        sorted_items = sorted(enumerate(items), key=lambda x: -x[1])

        bins = []  # Each bin is a list of (original_index, size)
        bin_remaining = []  # Remaining capacity in each bin

        for original_idx, size in sorted_items:
            if size > bin_capacity:
                return {'error': f'Item {original_idx} exceeds bin capacity'}

            # Find first bin that fits
            placed = False
            for i, remaining in enumerate(bin_remaining):
                if remaining >= size:
                    bins[i].append((original_idx, size))
                    bin_remaining[i] -= size
                    placed = True
                    break

            if not placed:
                # Create new bin
                bins.append([(original_idx, size)])
                bin_remaining.append(bin_capacity - size)

        # Format output
        bin_contents = [[idx for idx, _ in b] for b in bins]
        bin_loads = [bin_capacity - r for r in bin_remaining]

        return {
            'num_bins': len(bins),
            'bin_contents': bin_contents,
            'bin_loads': bin_loads,
            'method': 'native_first_fit_decreasing'
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Return agent statistics."""
        return {
            'agent_id': self.agent_id,
            'tasks_executed': self.tasks_executed,
            'capabilities': [
                'knapsack_01', 'knapsack_fractional',
                'tsp_nearest_neighbor', 'tsp_2opt',
                'assignment_hungarian', 'set_cover_greedy',
                'bin_packing_first_fit'
            ]
        }
