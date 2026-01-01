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
ANALYTIC NUMBER THEORY SUPERVISOR (Tier 2)
==========================================

Routes analytic number theory problems to appropriate specialists.
Never computes directly - only delegates to Tier 3 specialists.

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class AnalyticNumberTheorySupervisor(BDIAgent):
    """
    Supervisor for analytic number theory domain.

    Routes to:
    - ZetaFunctionSpecialist: Riemann zeta, Dirichlet L-functions
    - PrimeDistributionSpecialist: Prime counting, prime number theorem
    - ArithmeticFunctionsSpecialist: Euler phi, Mobius mu, divisor functions
    - AnalyticContinuationSpecialist: Functional equations, Euler products
    - ExplicitFormulaSpecialist: Explicit formulas, von Mangoldt, prime-zero connections
    - ZeroDensitySpecialist: Zero-density estimates, critical strip analysis
    - LFunctionAdvancedSpecialist: Dedekind zeta, Hecke L-functions, class numbers

    This supervisor NEVER computes - only routes.
    """

    # Keywords for routing
    ZETA_KEYWORDS = ['zeta', 'riemann', 'dirichlet', 'l-function', 'functional equation',
                     'critical line', 'trivial zero', 'non-trivial zero']
    PRIME_KEYWORDS = ['prime', 'pi(x)', 'prime counting', 'prime number theorem',
                      'sieve', 'eratosthenes', 'prime gap', 'prime density']
    ARITHMETIC_KEYWORDS = ['euler phi', 'totient', 'mobius', 'divisor', 'tau', 'sigma',
                          'multiplicative', 'additive', 'arithmetic function']
    CONTINUATION_KEYWORDS = ['analytic continuation', 'euler product', 'continuation',
                            'pole', 'residue', 'convergence', 'domain extension']
    EXPLICIT_FORMULA_KEYWORDS = ['explicit formula', 'von mangoldt', 'chebyshev',
                                 'mangoldt function', 'prime-zero connection', 'oscillatory term']
    ZERO_DENSITY_KEYWORDS = ['zero density', 'zero-density', 'critical strip', 'zero count',
                            'density estimate', 'zero-free region', 'n(t)', 'n(sigma, t)']
    L_FUNCTION_ADVANCED_KEYWORDS = ['dedekind zeta', 'hecke l-function', 'artin l-function',
                                   'class number', 'number field', 'kronecker symbol']

    def __init__(self, agent_id: str = 'analytic_number_theory_supervisor_001', df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard

        # Lazy-loaded specialists
        self._zeta_specialist = None
        self._prime_specialist = None
        self._arithmetic_specialist = None
        self._continuation_specialist = None
        self._explicit_formula_specialist = None
        self._zero_density_specialist = None
        self._l_function_advanced_specialist = None

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.algebra.numbertheory.analytic',
                agent_id=agent_id,
                algorithm='router',
                cost='minimal',
                instance=self,
                tier='2',
                capabilities='zeta_prime_arithmetic_continuation_explicit_zero_density_l_function_routing'
            ))

        logger.info(f"[{agent_id}] Analytic Number Theory Supervisor initialized")

    @property
    def zeta_specialist(self):
        """Lazy load zeta function specialist."""
        if self._zeta_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.analytic.zeta_functions import ZetaFunctionSpecialist
            self._zeta_specialist = ZetaFunctionSpecialist(
                agent_id='zeta_function_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._zeta_specialist

    @property
    def prime_specialist(self):
        """Lazy load prime distribution specialist."""
        if self._prime_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.analytic.prime_distribution import PrimeDistributionSpecialist
            self._prime_specialist = PrimeDistributionSpecialist(
                agent_id='prime_distribution_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._prime_specialist

    @property
    def arithmetic_specialist(self):
        """Lazy load arithmetic functions specialist."""
        if self._arithmetic_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.analytic.arithmetic_functions import ArithmeticFunctionsSpecialist
            self._arithmetic_specialist = ArithmeticFunctionsSpecialist(
                agent_id='arithmetic_functions_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._arithmetic_specialist

    @property
    def continuation_specialist(self):
        """Lazy load analytic continuation specialist."""
        if self._continuation_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.analytic.analytic_continuation import AnalyticContinuationSpecialist
            self._continuation_specialist = AnalyticContinuationSpecialist(
                agent_id='analytic_continuation_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._continuation_specialist

    @property
    def explicit_formula_specialist(self):
        """Lazy load explicit formula specialist."""
        if self._explicit_formula_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.analytic.explicit_formula import ExplicitFormulaSpecialist
            self._explicit_formula_specialist = ExplicitFormulaSpecialist(
                agent_id='explicit_formula_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._explicit_formula_specialist

    @property
    def zero_density_specialist(self):
        """Lazy load zero-density specialist."""
        if self._zero_density_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.analytic.zero_density import ZeroDensitySpecialist
            self._zero_density_specialist = ZeroDensitySpecialist(
                agent_id='zero_density_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._zero_density_specialist

    @property
    def l_function_advanced_specialist(self):
        """Lazy load L-function advanced specialist."""
        if self._l_function_advanced_specialist is None:
            from symbo_agentic_reasoners.agents.specialists.algebra.number_theory.analytic.l_function_advanced import LFunctionAdvancedSpecialist
            self._l_function_advanced_specialist = LFunctionAdvancedSpecialist(
                agent_id='l_function_advanced_specialist_001',
                df=self.df,
                blackboard=self.blackboard
            )
        return self._l_function_advanced_specialist

    def update_beliefs(self):
        """PERCEIVE: Monitor for analytic number theory tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['analytic_number_theory'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['zeta'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['prime_distribution'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['arithmetic_functions'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'routed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create routing plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            target_specialist = self._determine_specialist(task)

            steps = ['route_task']
            intention = Intention(
                plan_id=f'route_analytic_nt_{task_id}',
                steps=steps,
                target_desire='analytic_number_theory_routing',
                metadata={'task_id': task_id, 'task_entry': task, 'target': target_specialist}
            )
            new_intentions.append(intention)
        return new_intentions

    def _determine_specialist(self, task) -> str:
        """Determine which specialist should handle this task."""
        metadata = task.metadata if hasattr(task, 'metadata') else {}
        content = str(task.content).lower() if hasattr(task, 'content') else ''
        operation = metadata.get('operation', '').lower()

        combined_text = f"{content} {operation}"

        # Check explicit operations
        zeta_ops = ['zeta', 'riemann_zeta', 'dirichlet_l', 'l_function']
        prime_ops = ['prime_count', 'pi_x', 'prime_gap', 'sieve']
        arithmetic_ops = ['euler_phi', 'mobius', 'divisor_function', 'tau', 'sigma']
        continuation_ops = ['continue', 'euler_product', 'functional_equation']
        explicit_formula_ops = ['explicit_formula', 'von_mangoldt', 'chebyshev', 'prime_zero_connection']
        zero_density_ops = ['zero_density', 'zero_count', 'critical_strip', 'density_estimate']
        l_function_advanced_ops = ['dedekind_zeta', 'hecke_l', 'artin_l', 'class_number']

        if operation in zeta_ops:
            return 'zeta'
        if operation in prime_ops:
            return 'prime'
        if operation in arithmetic_ops:
            return 'arithmetic'
        if operation in continuation_ops:
            return 'continuation'
        if operation in explicit_formula_ops:
            return 'explicit_formula'
        if operation in zero_density_ops:
            return 'zero_density'
        if operation in l_function_advanced_ops:
            return 'l_function_advanced'

        # Check keywords
        zeta_score = sum(1 for kw in self.ZETA_KEYWORDS if kw in combined_text)
        prime_score = sum(1 for kw in self.PRIME_KEYWORDS if kw in combined_text)
        arithmetic_score = sum(1 for kw in self.ARITHMETIC_KEYWORDS if kw in combined_text)
        continuation_score = sum(1 for kw in self.CONTINUATION_KEYWORDS if kw in combined_text)
        explicit_formula_score = sum(1 for kw in self.EXPLICIT_FORMULA_KEYWORDS if kw in combined_text)
        zero_density_score = sum(1 for kw in self.ZERO_DENSITY_KEYWORDS if kw in combined_text)
        l_function_advanced_score = sum(1 for kw in self.L_FUNCTION_ADVANCED_KEYWORDS if kw in combined_text)

        scores = {
            'zeta': zeta_score,
            'prime': prime_score,
            'arithmetic': arithmetic_score,
            'continuation': continuation_score,
            'explicit_formula': explicit_formula_score,
            'zero_density': zero_density_score,
            'l_function_advanced': l_function_advanced_score
        }

        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'zeta'

    def execute_step(self, intention: Intention):
        """EXECUTE: Route to appropriate specialist."""
        action = intention.get_current_action()

        if action == 'route_task':
            task = intention.metadata.get('task_entry')
            target = intention.metadata.get('target', 'zeta')

            self.add_belief(f'routed_task_{task.entry_id}', True, confidence=1.0)

            if target == 'zeta':
                specialist = self.zeta_specialist
            elif target == 'prime':
                specialist = self.prime_specialist
            elif target == 'arithmetic':
                specialist = self.arithmetic_specialist
            elif target == 'continuation':
                specialist = self.continuation_specialist
            elif target == 'explicit_formula':
                specialist = self.explicit_formula_specialist
            elif target == 'zero_density':
                specialist = self.zero_density_specialist
            elif target == 'l_function_advanced':
                specialist = self.l_function_advanced_specialist
            else:
                specialist = self.zeta_specialist  # Default fallback

            logger.info(f"[{self.agent_id}] Routing task {task.entry_id} to {target} specialist")

            specialist.update_beliefs()
            new_intentions = specialist.deliberate()
            for new_intention in new_intentions:
                specialist.intentions.append(new_intention)

            intention.mark_completed()

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Direct solve interface for analytic number theory problems.

        Args:
            problem: Dictionary with 'type' and relevant parameters

        Returns:
            Solution dictionary
        """
        problem_type = problem.get('type', '').lower()

        # Route to appropriate specialist based on problem type
        if any(kw in problem_type for kw in ['zeta', 'riemann', 'dirichlet', 'l_function']):
            return self.zeta_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['prime', 'pi_x', 'sieve']):
            return self.prime_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['euler', 'mobius', 'divisor', 'totient']):
            return self.arithmetic_specialist.solve(problem)
        elif any(kw in problem_type for kw in ['continuation', 'euler_product']):
            return self.continuation_specialist.solve(problem)

        return {'error': f'Unknown problem type: {problem_type}'}

    def get_statistics(self) -> Dict[str, Any]:
        """Return supervisor statistics."""
        stats = {
            'agent_id': self.agent_id,
            'tier': 2,
            'role': 'supervisor',
            'specialists': ['zeta', 'prime', 'arithmetic', 'continuation']
        }

        if self._zeta_specialist:
            stats['zeta_tasks'] = getattr(self._zeta_specialist, 'tasks_executed', 0)
        if self._prime_specialist:
            stats['prime_tasks'] = getattr(self._prime_specialist, 'tasks_executed', 0)
        if self._arithmetic_specialist:
            stats['arithmetic_tasks'] = getattr(self._arithmetic_specialist, 'tasks_executed', 0)
        if self._continuation_specialist:
            stats['continuation_tasks'] = getattr(self._continuation_specialist, 'tasks_executed', 0)

        return stats
