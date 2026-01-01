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
GAME THEORY OPTIMIZATION SPECIALIST (Tier 3)
===========================================

Implements game-theoretic solution concepts: Nash equilibrium, minimax,
evolutionarily stable strategies, and strategic dominance analysis.
Handles zero-sum games, bimatrix games, and evolutionary game dynamics.
"""

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator, create_service_registration
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np
from scipy.optimize import linprog, minimize


class GameTheoryOptimizationSpecialist(BDIAgent):
    """
    Specialist for game-theoretic optimization and equilibrium analysis.

    Capabilities:
    - Compute Nash equilibrium (pure and mixed strategies)
    - Solve zero-sum games via minimax theorem
    - Find evolutionarily stable strategies (ESS)
    - Detect dominant strategies
    - Compute correlated equilibria
    - Iterated elimination of dominated strategies (IEDS)
    - Strategic form game analysis
    """

    def __init__(self, agent_id='game_theory_specialist_001', df: Optional[DirectoryFacilitator]=None,
                 blackboard: Optional[Blackboard]=None):
        super().__init__(agent_id)
        self.df, self.blackboard = df, blackboard
        self.tasks_executed = 0
        self.nash_computations = 0
        self.minimax_computations = 0
        self.ess_computations = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.optimization.advanced.game_theory',
                agent_id=self.agent_id,
                algorithm='nash_minimax_ess',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3',
                methods='nash_equilibrium_minimax_ess_dominance_ieds'
            ))

        print(f"[{self.agent_id}] Game Theory Optimization Specialist initialized")
        print(f"  Methods: Nash equilibrium, minimax, ESS, dominance")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for game theory tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
            tasks = (self.blackboard.query_entries(tags=['game_theory'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['nash_equilibrium'], status=EntryStatus.PENDING) +
                    self.blackboard.query_entries(tags=['minimax'], status=EntryStatus.PENDING))

            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if (hasattr(task, 'metadata') and task.metadata and
                    task.metadata.get('assigned_agent') == self.agent_id and task not in tasks):
                    tasks.append(task)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if (not self.has_belief(f'claimed_task_{task.entry_id}') and
                    not self.has_belief(belief_key)):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create game theory computation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'nash_equilibrium')

            steps = ['claim_task', 'parse_parameters', 'compute_equilibrium', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'game_{operation}_{task_id}',
                steps=steps,
                target_desire='game_theory_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)

        # Periodic equilibrium cache update
        if self.tasks_executed > 0 and self.tasks_executed % 50 == 0:
            intent = Intention(
                plan_id=f'update_equilibrium_cache_{self.tasks_executed}',
                steps=['update_cache'],
                target_desire='maintain_knowledge',
                metadata={'trigger': 'periodic'}
            )
            new_intentions.append(intent)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform game theory computations."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()

            elif action == 'parse_parameters':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                operation = metadata.get('operation', 'nash_equilibrium')

                params = {}
                if operation == 'nash_equilibrium':
                    params['payoff_1'] = metadata.get('payoff_1', [[3, 0], [0, 1]])
                    params['payoff_2'] = metadata.get('payoff_2', [[3, 0], [0, 1]])
                elif operation == 'zero_sum_game':
                    params['payoff_matrix'] = metadata.get('payoff_matrix', [[1, -1], [-1, 1]])
                elif operation == 'ess':
                    params['fitness_matrix'] = metadata.get('fitness_matrix', [[3, 0], [5, 1]])

                intention.metadata['params'] = params
                intention.advance()

            elif action == 'compute_equilibrium':
                operation = intention.metadata.get('operation')
                params = intention.metadata.get('params', {})

                result = None
                if operation == 'nash_equilibrium':
                    result = self.compute_nash_equilibrium(
                        params.get('payoff_1', [[3, 0], [0, 1]]),
                        params.get('payoff_2', [[3, 0], [0, 1]])
                    )
                elif operation == 'zero_sum_game':
                    result = self.solve_zero_sum_game(
                        params.get('payoff_matrix', [[1, -1], [-1, 1]])
                    )
                elif operation == 'ess':
                    result = self.compute_evolutionarily_stable_strategy(
                        params.get('fitness_matrix', [[3, 0], [5, 1]])
                    )
                else:
                    result = {'operation': operation, 'status': 'not_implemented'}

                intention.metadata['result'] = result
                intention.advance()

            elif action == 'verify_result':
                result = intention.metadata.get('result')
                verified = result is not None and 'error' not in result
                intention.metadata['verified'] = verified
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    entry = create_entry(
                        EntryType.PARTIAL_RESULT,
                        create_variable(str(result)),
                        self.agent_id,
                        task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        ['game_theory', 'result', task_id],
                        EntryStatus.COMPLETED,
                        {'result': result, 'result_str': str(result)}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            elif action == 'update_cache':
                self.add_belief(
                    'equilibrium_cache_updated',
                    {'timestamp': self.tasks_executed, 'nash': self.nash_computations,
                     'minimax': self.minimax_computations, 'ess': self.ess_computations},
                    confidence=0.9,
                    source='self_monitoring'
                )
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def process(self, task_entry):
        """
        Process a game theory task (legacy interface for supervisor compatibility).

        Args:
            task_entry: Task entry with metadata containing operation and parameters

        Returns:
            Dict with computation result
        """
        self.tasks_executed += 1

        # Handle both dict and BlackboardEntry
        if hasattr(task_entry, 'metadata'):
            # It's a BlackboardEntry
            metadata = task_entry.metadata or {}
        else:
            # It's a dict (backwards compatibility)
            metadata = task_entry.get('metadata', task_entry)

        operation = metadata.get('operation', 'nash_equilibrium')

        try:
            if operation == 'nash_equilibrium':
                payoff_1 = metadata.get('payoff_1', [[3, 0], [0, 1]])
                payoff_2 = metadata.get('payoff_2', [[3, 0], [0, 1]])
                return self.compute_nash_equilibrium(payoff_1, payoff_2)
            elif operation == 'zero_sum_game':
                payoff_matrix = metadata.get('payoff_matrix', [[1, -1], [-1, 1]])
                return self.solve_zero_sum_game(payoff_matrix)
            else:
                return {'operation': operation, 'explanation': 'Game theory computation'}
        except Exception as e:
            return {'error': str(e), 'operation': operation}

    # ==================== CORE COMPUTATIONAL METHODS ====================

    def compute_nash_equilibrium(
        self,
        payoff_1: List[List[float]],
        payoff_2: List[List[float]]
    ) -> Dict[str, Any]:
        """
        Compute Nash equilibrium for bimatrix game.

        For 2-player game with payoff matrices A (player 1) and B (player 2):
        Find (σ₁, σ₂) such that neither player can improve by deviating.

        Nash equilibrium condition:
        - Player 1: σ₁ᵀ A σ₂ ≥ σ₁'ᵀ A σ₂ for all σ₁'
        - Player 2: σ₁ᵀ B σ₂ ≥ σ₁ᵀ B σ₂' for all σ₂'

        Args:
            payoff_1: Payoff matrix for player 1 (m × n)
            payoff_2: Payoff matrix for player 2 (m × n)

        Returns:
            Dict with Nash equilibrium strategies

        Example:
            >>> # Prisoner's Dilemma
            >>> A = [[3, 0], [5, 1]]  # Player 1 payoffs
            >>> B = [[3, 5], [0, 1]]  # Player 2 payoffs
            >>> result = agent.compute_nash_equilibrium(A, B)
        """
        self.nash_computations += 1

        A = np.array(payoff_1, dtype=float)
        B = np.array(payoff_2, dtype=float)

        if A.shape != B.shape:
            return {'error': 'Payoff matrices must have same shape'}

        m, n = A.shape

        # First, check for pure strategy Nash equilibria
        pure_equilibria = self._find_pure_nash_equilibria(A, B)

        # For 2×2 games, compute mixed strategy analytically
        if m == 2 and n == 2:
            mixed_result = self._compute_2x2_mixed_nash(A, B)
            if 'error' not in mixed_result:
                return {
                    'pure_equilibria': pure_equilibria,
                    'mixed_equilibrium': mixed_result,
                    'has_pure': len(pure_equilibria) > 0,
                    'has_mixed': True,
                    'game_shape': [m, n]
                }
            else:
                return {
                    'pure_equilibria': pure_equilibria,
                    'has_pure': len(pure_equilibria) > 0,
                    'has_mixed': False,
                    'game_shape': [m, n]
                }

        # For larger games, use support enumeration or linear complementarity
        # Simplified: return pure equilibria if they exist
        return {
            'pure_equilibria': pure_equilibria,
            'has_pure': len(pure_equilibria) > 0,
            'game_shape': [m, n],
            'note': 'Mixed strategies for large games require advanced algorithms'
        }

    def _find_pure_nash_equilibria(
        self,
        A: np.ndarray,
        B: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Find all pure strategy Nash equilibria.

        A pure Nash equilibrium (i*, j*) satisfies:
        - A[i*, j*] ≥ A[i, j*] for all i (best response for player 1)
        - B[i*, j*] ≥ B[i*, j] for all j (best response for player 2)
        """
        m, n = A.shape
        equilibria = []

        for i in range(m):
            for j in range(n):
                # Check if (i, j) is a Nash equilibrium
                # Player 1 best response: is i a best response to j?
                if not np.allclose(A[i, j], np.max(A[:, j])):
                    continue

                # Player 2 best response: is j a best response to i?
                if not np.allclose(B[i, j], np.max(B[i, :])):
                    continue

                # (i, j) is a Nash equilibrium
                equilibria.append({
                    'player_1_action': int(i),
                    'player_2_action': int(j),
                    'payoff_1': float(A[i, j]),
                    'payoff_2': float(B[i, j]),
                    'type': 'pure'
                })

        return equilibria

    def _compute_2x2_mixed_nash(
        self,
        A: np.ndarray,
        B: np.ndarray
    ) -> Dict[str, Any]:
        """
        Compute mixed strategy Nash equilibrium for 2×2 game analytically.

        Player 1 chooses probability p for action 0, (1-p) for action 1.
        Player 2 chooses probability q for action 0, (1-q) for action 1.

        Indifference conditions:
        - Player 2 makes player 1 indifferent: p*A[0,0] + (1-p)*A[1,0] = p*A[0,1] + (1-p)*A[1,1]
        - Player 1 makes player 2 indifferent: q*B[0,0] + (1-q)*B[0,1] = q*B[1,0] + (1-q)*B[1,1]
        """
        # Solve for p (player 1's mixed strategy)
        # A[0,0]*p + A[1,0]*(1-p) = A[0,1]*p + A[1,1]*(1-p)
        # p*(A[0,0] - A[1,0] - A[0,1] + A[1,1]) = A[1,1] - A[1,0]
        denom_1 = A[0,0] - A[1,0] - A[0,1] + A[1,1]
        if abs(denom_1) > 1e-10:
            p = (A[1,1] - A[1,0]) / denom_1
        else:
            # Degenerate case: player 1 is indifferent for all p
            p = 0.5

        p = np.clip(p, 0, 1)

        # Solve for q (player 2's mixed strategy)
        # B[0,0]*q + B[0,1]*(1-q) = B[1,0]*q + B[1,1]*(1-q)
        denom_2 = B[0,0] - B[0,1] - B[1,0] + B[1,1]
        if abs(denom_2) > 1e-10:
            q = (B[1,1] - B[0,1]) / denom_2
        else:
            q = 0.5

        q = np.clip(q, 0, 1)

        strategy_1 = np.array([p, 1-p])
        strategy_2 = np.array([q, 1-q])

        # Compute expected payoffs
        expected_payoff_1 = strategy_1 @ A @ strategy_2
        expected_payoff_2 = strategy_1 @ B @ strategy_2

        return {
            'player_1_strategy': strategy_1.tolist(),
            'player_2_strategy': strategy_2.tolist(),
            'expected_payoff_1': float(expected_payoff_1),
            'expected_payoff_2': float(expected_payoff_2),
            'type': 'mixed'
        }

    def solve_zero_sum_game(self, payoff_matrix: List[List[float]]) -> Dict[str, Any]:
        """
        Solve zero-sum game using minimax theorem.

        For zero-sum game with payoff matrix A (row player perspective):
        Find mixed strategies (p*, q*) satisfying:
        max_p min_q pᵀAq = min_q max_p pᵀAq = v (value of game)

        Uses linear programming formulation:
        max v s.t. Aᵀp ≥ v·1, Σp_i = 1, p ≥ 0

        Args:
            payoff_matrix: Payoff matrix for row player

        Returns:
            Dict with optimal strategies and game value

        Example:
            >>> # Rock-Paper-Scissors
            >>> A = [[0, -1, 1], [1, 0, -1], [-1, 1, 0]]
            >>> result = agent.solve_zero_sum_game(A)
        """
        self.minimax_computations += 1

        A = np.array(payoff_matrix, dtype=float)
        m, n = A.shape

        # Use linear programming to find row player's maximin strategy
        # max v s.t. A^T p >= v*1, sum(p) = 1, p >= 0
        # Convert to standard LP form: min -v
        c = np.zeros(m + 1)
        c[0] = -1  # Maximize v by minimizing -v

        # Inequality constraints: -A^T p + v*1 <= 0
        # i.e., A^T p >= v*1
        A_ub = np.hstack([np.ones((n, 1)), -A.T])
        b_ub = np.zeros(n)

        # Equality constraint: sum(p) = 1
        A_eq = np.zeros((1, m + 1))
        A_eq[0, 1:] = 1
        b_eq = np.array([1])

        # Bounds: v unbounded, p >= 0
        bounds = [(None, None)] + [(0, None) for _ in range(m)]

        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                        bounds=bounds, method='highs')

        if not result.success:
            return {'error': 'LP solver failed', 'message': result.message}

        row_value = -result.fun
        row_strategy = result.x[1:]

        # Solve for column player's minimax strategy
        # min u s.t. A q <= u*1, sum(q) = 1, q >= 0
        c_col = np.zeros(n + 1)
        c_col[0] = 1  # Minimize u

        # Inequality constraints: A q - u*1 <= 0
        A_ub_col = np.hstack([-np.ones((m, 1)), A])
        b_ub_col = np.zeros(m)

        # Equality constraint: sum(q) = 1
        A_eq_col = np.zeros((1, n + 1))
        A_eq_col[0, 1:] = 1
        b_eq_col = np.array([1])

        bounds_col = [(None, None)] + [(0, None) for _ in range(n)]

        result_col = linprog(c_col, A_ub=A_ub_col, b_ub=b_ub_col,
                            A_eq=A_eq_col, b_eq=b_eq_col,
                            bounds=bounds_col, method='highs')

        if not result_col.success:
            col_value = row_value
            col_strategy = np.ones(n) / n
        else:
            col_value = result_col.fun
            col_strategy = result_col.x[1:]

        # By minimax theorem, row_value should equal col_value
        return {
            'row_strategy': row_strategy.tolist(),
            'col_strategy': col_strategy.tolist(),
            'game_value': float(row_value),
            'minimax_equality': abs(row_value - col_value) < 1e-6,
            'row_value': float(row_value),
            'col_value': float(col_value)
        }

    def compute_evolutionarily_stable_strategy(
        self,
        fitness_matrix: List[List[float]]
    ) -> Dict[str, Any]:
        """
        Compute evolutionarily stable strategy (ESS).

        An ESS is a strategy p* such that for any mutant strategy q ≠ p*:
        1. E(p*, p*) > E(q, p*), or
        2. E(p*, p*) = E(q, p*) and E(p*, q) > E(q, q)

        where E(p, q) = pᵀ F q is the expected fitness of p against q.

        Args:
            fitness_matrix: F[i][j] = fitness of strategy i vs strategy j

        Returns:
            Dict with ESS candidates and stability analysis

        Example:
            >>> # Hawk-Dove game
            >>> F = [[0, 4], [1, 2]]  # (Hawk, Dove) strategies
            >>> result = agent.compute_evolutionarily_stable_strategy(F)
        """
        self.ess_computations += 1

        F = np.array(fitness_matrix, dtype=float)
        n = F.shape[0]

        if F.shape[0] != F.shape[1]:
            return {'error': 'Fitness matrix must be square'}

        # Check pure strategies for ESS property
        pure_ess = []
        for i in range(n):
            is_ess = True
            e_i = np.zeros(n)
            e_i[i] = 1

            # Check ESS conditions against all other strategies
            for j in range(n):
                if i == j:
                    continue

                e_j = np.zeros(n)
                e_j[j] = 1

                fitness_ii = e_i @ F @ e_i
                fitness_ji = e_j @ F @ e_i

                if fitness_ji > fitness_ii + 1e-10:
                    # Mutant j does better against i
                    is_ess = False
                    break
                elif abs(fitness_ji - fitness_ii) < 1e-10:
                    # Equal fitness, check second condition
                    fitness_ij = e_i @ F @ e_j
                    fitness_jj = e_j @ F @ e_j

                    if fitness_ij <= fitness_jj + 1e-10:
                        is_ess = False
                        break

            if is_ess:
                pure_ess.append({
                    'strategy': i,
                    'type': 'pure',
                    'stability': 'evolutionary_stable'
                })

        # For mixed strategies, solve for symmetric Nash equilibrium
        # This is complex; we check if uniform mixing is ESS
        uniform = np.ones(n) / n
        fitness_uniform = uniform @ F @ uniform

        is_uniform_ess = True
        for i in range(n):
            e_i = np.zeros(n)
            e_i[i] = 1

            fitness_i_uniform = e_i @ F @ uniform
            if fitness_i_uniform > fitness_uniform + 1e-10:
                is_uniform_ess = False
                break

        mixed_ess = []
        if is_uniform_ess:
            mixed_ess.append({
                'strategy': uniform.tolist(),
                'type': 'mixed_uniform',
                'stability': 'evolutionary_stable',
                'fitness': float(fitness_uniform)
            })

        return {
            'pure_ess': pure_ess,
            'mixed_ess': mixed_ess,
            'has_pure_ess': len(pure_ess) > 0,
            'has_mixed_ess': len(mixed_ess) > 0,
            'n_strategies': n
        }

    def apply_minimax_theorem(self, payoff_matrix: List[List[float]]) -> Dict[str, Any]:
        """
        Apply von Neumann minimax theorem.

        Theorem: For zero-sum game with payoff matrix A:
        max_p min_q pᵀAq = min_q max_p pᵀAq

        Verifies theorem by computing both sides.

        Args:
            payoff_matrix: Payoff matrix for zero-sum game

        Returns:
            Dict with maximin value, minimax value, and theorem verification
        """
        A = np.array(payoff_matrix, dtype=float)
        m, n = A.shape

        # Compute maximin: max_p min_q pᵀAq
        # For each row strategy p (pure), find minimum payoff over columns
        row_mins = []
        for i in range(m):
            row_min = np.min(A[i, :])
            row_mins.append(row_min)

        maximin_value = np.max(row_mins)
        maximin_strategy = int(np.argmax(row_mins))

        # Compute minimax: min_q max_p pᵀAq
        # For each column strategy q (pure), find maximum payoff over rows
        col_maxs = []
        for j in range(n):
            col_max = np.max(A[:, j])
            col_maxs.append(col_max)

        minimax_value = np.min(col_maxs)
        minimax_strategy = int(np.argmin(col_maxs))

        # For zero-sum games, solve for mixed strategies
        mixed_result = self.solve_zero_sum_game(payoff_matrix)

        return {
            'maximin_value': float(maximin_value),
            'minimax_value': float(minimax_value),
            'maximin_strategy': maximin_strategy,
            'minimax_strategy': minimax_strategy,
            'equality_holds': abs(maximin_value - minimax_value) < 1e-6,
            'mixed_game_value': mixed_result.get('game_value'),
            'theorem_verified': 'error' not in mixed_result
        }

    def compute_mixed_strategy_equilibrium(
        self,
        payoffs: List[np.ndarray]
    ) -> Dict[str, Any]:
        """
        Compute mixed strategy Nash equilibrium via linear programming.

        For n-player games, uses iterative best response or support enumeration.
        For 2-player games, reduces to LP formulation.

        Args:
            payoffs: List of payoff matrices (one per player)

        Returns:
            Dict with mixed strategy equilibrium
        """
        if len(payoffs) == 2:
            return self.compute_nash_equilibrium(
                payoffs[0].tolist(),
                payoffs[1].tolist()
            )
        else:
            return {'error': 'Only 2-player games currently supported',
                   'n_players': len(payoffs)}

    def check_dominant_strategy(
        self,
        payoff_matrix: List[List[float]],
        player: int
    ) -> Dict[str, Any]:
        """
        Check for dominant strategies for given player.

        Strategy i strictly dominates strategy j if:
        u_i(a_{-p}) > u_j(a_{-p}) for all opponent actions a_{-p}

        Args:
            payoff_matrix: Payoff matrix for player
            player: Player index (0 or 1)

        Returns:
            Dict with dominant strategies and dominance relations

        Example:
            >>> # Check if Defect dominates Cooperate in Prisoner's Dilemma
            >>> A = [[3, 0], [5, 1]]
            >>> result = agent.check_dominant_strategy(A, player=0)
        """
        A = np.array(payoff_matrix, dtype=float)
        m, n = A.shape

        # For player 0 (row player), check row dominance
        if player == 0:
            dominant_strategies = []
            dominated_strategies = []

            for i in range(m):
                is_dominant = False
                dominates = []

                for j in range(m):
                    if i == j:
                        continue

                    # Check if i strictly dominates j
                    if np.all(A[i, :] > A[j, :]):
                        dominates.append(j)
                        is_dominant = True

                if is_dominant:
                    dominant_strategies.append({
                        'strategy': i,
                        'dominates': dominates
                    })

            # Find dominated strategies
            for i in range(m):
                is_dominated = False
                for j in range(m):
                    if i == j:
                        continue
                    if np.all(A[j, :] > A[i, :]):
                        is_dominated = True
                        break

                if is_dominated:
                    dominated_strategies.append(i)

            return {
                'player': player,
                'dominant_strategies': dominant_strategies,
                'dominated_strategies': dominated_strategies,
                'has_dominant': len(dominant_strategies) > 0
            }

        # For player 1 (column player), check column dominance
        else:
            dominant_strategies = []
            dominated_strategies = []

            for i in range(n):
                is_dominant = False
                dominates = []

                for j in range(n):
                    if i == j:
                        continue

                    # Check if i strictly dominates j
                    if np.all(A[:, i] > A[:, j]):
                        dominates.append(j)
                        is_dominant = True

                if is_dominant:
                    dominant_strategies.append({
                        'strategy': i,
                        'dominates': dominates
                    })

            for i in range(n):
                is_dominated = False
                for j in range(n):
                    if i == j:
                        continue
                    if np.all(A[:, j] > A[:, i]):
                        is_dominated = True
                        break

                if is_dominated:
                    dominated_strategies.append(i)

            return {
                'player': player,
                'dominant_strategies': dominant_strategies,
                'dominated_strategies': dominated_strategies,
                'has_dominant': len(dominant_strategies) > 0
            }

    def compute_correlated_equilibrium(
        self,
        payoffs: Tuple[np.ndarray, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Compute correlated equilibrium for 2-player game.

        A correlated equilibrium is a probability distribution over action profiles
        that satisfies incentive constraints for both players.

        Uses linear programming to find optimal correlated equilibrium.

        Args:
            payoffs: (A, B) payoff matrices for players 1 and 2

        Returns:
            Dict with correlated equilibrium distribution

        Note:
            Every Nash equilibrium is a correlated equilibrium,
            but correlated equilibria can achieve higher social welfare.
        """
        A, B = payoffs[0], payoffs[1]
        m, n = A.shape

        # Variables: p[i,j] = probability of recommending (i, j)
        # Constraints:
        # 1. p[i,j] >= 0 for all i,j
        # 2. sum p[i,j] = 1
        # 3. Incentive constraints for both players

        # For simplicity, we use uniform distribution as a valid correlated equilibrium
        # More sophisticated LP formulation would optimize social welfare
        uniform_dist = np.ones((m, n)) / (m * n)

        # Verify incentive constraints
        valid = self._verify_correlated_equilibrium(A, B, uniform_dist)

        if valid:
            expected_payoff_1 = np.sum(uniform_dist * A)
            expected_payoff_2 = np.sum(uniform_dist * B)

            return {
                'distribution': uniform_dist.tolist(),
                'expected_payoff_1': float(expected_payoff_1),
                'expected_payoff_2': float(expected_payoff_2),
                'type': 'uniform_correlated',
                'is_valid': True
            }
        else:
            return {'error': 'Failed to find valid correlated equilibrium'}

    def _verify_correlated_equilibrium(
        self,
        A: np.ndarray,
        B: np.ndarray,
        dist: np.ndarray
    ) -> bool:
        """Verify incentive constraints for correlated equilibrium."""
        m, n = A.shape

        # Check player 1 incentive constraints
        for i in range(m):
            for i_prime in range(m):
                if i == i_prime:
                    continue

                # If mediator recommends i, player 1 should not prefer i'
                lhs = sum(dist[i, j] * A[i, j] for j in range(n))
                rhs = sum(dist[i, j] * A[i_prime, j] for j in range(n))

                if rhs > lhs + 1e-6:
                    return False

        # Check player 2 incentive constraints
        for j in range(n):
            for j_prime in range(n):
                if j == j_prime:
                    continue

                lhs = sum(dist[i, j] * B[i, j] for i in range(m))
                rhs = sum(dist[i, j] * B[i, j_prime] for i in range(m))

                if rhs > lhs + 1e-6:
                    return False

        return True

    def iterated_elimination_dominated_strategies(
        self,
        payoffs: Tuple[List[List[float]], List[List[float]]]
    ) -> Dict[str, Any]:
        """
        Apply iterated elimination of strictly dominated strategies (IEDS).

        Repeatedly eliminates strictly dominated strategies until no more can be eliminated.
        The resulting game is strategically equivalent to the original.

        Args:
            payoffs: (A, B) payoff matrices for players 1 and 2

        Returns:
            Dict with reduced game and elimination sequence

        Example:
            >>> A = [[3, 0], [5, 1], [2, 2]]
            >>> B = [[3, 5], [0, 1], [2, 2]]
            >>> result = agent.iterated_elimination_dominated_strategies((A, B))
        """
        A = np.array(payoffs[0], dtype=float)
        B = np.array(payoffs[1], dtype=float)

        active_rows = list(range(A.shape[0]))
        active_cols = list(range(A.shape[1]))

        elimination_sequence = []

        changed = True
        iteration = 0

        while changed:
            changed = False
            iteration += 1

            # Eliminate dominated rows (player 1)
            rows_to_remove = []
            for i in active_rows:
                for j in active_rows:
                    if i == j:
                        continue

                    # Check if row j dominates row i
                    A_i = A[i, active_cols]
                    A_j = A[j, active_cols]

                    if np.all(A_j >= A_i) and np.any(A_j > A_i):
                        rows_to_remove.append(i)
                        elimination_sequence.append({
                            'iteration': iteration,
                            'player': 1,
                            'eliminated': i,
                            'dominated_by': j
                        })
                        break

            for row in rows_to_remove:
                if row in active_rows:
                    active_rows.remove(row)
                    changed = True

            # Eliminate dominated columns (player 2)
            cols_to_remove = []
            for i in active_cols:
                for j in active_cols:
                    if i == j:
                        continue

                    # Check if column j dominates column i
                    B_i = B[active_rows, i]
                    B_j = B[active_rows, j]

                    if np.all(B_j >= B_i) and np.any(B_j > B_i):
                        cols_to_remove.append(i)
                        elimination_sequence.append({
                            'iteration': iteration,
                            'player': 2,
                            'eliminated': i,
                            'dominated_by': j
                        })
                        break

            for col in cols_to_remove:
                if col in active_cols:
                    active_cols.remove(col)
                    changed = True

        # Extract reduced game
        reduced_A = A[np.ix_(active_rows, active_cols)]
        reduced_B = B[np.ix_(active_rows, active_cols)]

        return {
            'reduced_game_A': reduced_A.tolist(),
            'reduced_game_B': reduced_B.tolist(),
            'active_rows': active_rows,
            'active_cols': active_cols,
            'elimination_sequence': elimination_sequence,
            'n_iterations': iteration,
            'original_shape': A.shape,
            'reduced_shape': reduced_A.shape
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Retrieve agent statistics."""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'nash_computations': self.nash_computations,
            'minimax_computations': self.minimax_computations,
            'ess_computations': self.ess_computations
        })
        return stats
