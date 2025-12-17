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
MULTI-DOMAIN TEAM COORDINATOR (Tier 1)
======================================

Meta-level coordinator that orchestrates multiple domain supervisors
for complex problems spanning multiple mathematical domains.

This coordinator:
- Analyzes problems to identify required domains
- Decomposes problems into domain-specific subtasks
- Routes subtasks to appropriate supervisors
- Synthesizes results from multiple domains
- Handles dependencies between domain results

NO SYMPY - Pure native mathematical reasoning.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention

logger = logging.getLogger(__name__)


class DomainType(Enum):
    """Mathematical domain types."""
    ALGEBRA = 'algebra'
    CALCULUS = 'calculus'
    LINEAR_ALGEBRA = 'linear_algebra'
    STATISTICS = 'statistics'
    GEOMETRY = 'geometry'
    DISCRETE_MATH = 'discrete_math'
    LOGIC = 'logic'
    INFORMATION_THEORY = 'information_theory'
    CRYPTOGRAPHY = 'cryptography'
    OPTIMIZATION = 'optimization'
    CATEGORY_THEORY = 'category_theory'
    PHYSICS = 'physics'
    NUMERICAL = 'numerical'


@dataclass
class DomainTask:
    """Represents a subtask for a specific domain."""
    task_id: str
    domain: DomainType
    description: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)  # IDs of tasks this depends on
    result: Optional[Dict[str, Any]] = None
    status: str = 'pending'  # pending, running, completed, failed


@dataclass
class TeamPlan:
    """Represents a multi-domain execution plan."""
    plan_id: str
    problem_description: str
    tasks: List[DomainTask]
    execution_order: List[List[str]]  # Batches of task IDs that can run in parallel
    final_synthesis: str  # Description of how to combine results


class MultiDomainTeamCoordinator(BDIAgent):
    """
    Tier 1 Coordinator for multi-domain mathematical problems.

    This coordinator sits above domain supervisors and orchestrates
    complex problems that require multiple mathematical domains.

    Capabilities:
    - Problem analysis and domain detection
    - Task decomposition across domains
    - Dependency graph construction
    - Parallel task execution scheduling
    - Result synthesis from multiple domains
    """

    # Domain detection keywords
    DOMAIN_KEYWORDS = {
        DomainType.ALGEBRA: [
            'polynomial', 'equation', 'factor', 'root', 'solve', 'quadratic',
            'linear equation', 'system of equations', 'algebraic', 'expression'
        ],
        DomainType.CALCULUS: [
            'derivative', 'integral', 'limit', 'differentiate', 'integrate',
            'differential equation', 'ode', 'pde', 'taylor', 'series', 'convergence'
        ],
        DomainType.LINEAR_ALGEBRA: [
            'matrix', 'vector', 'eigenvalue', 'eigenvector', 'determinant',
            'rank', 'null space', 'linear transformation', 'svd', 'decomposition'
        ],
        DomainType.STATISTICS: [
            'probability', 'distribution', 'mean', 'variance', 'hypothesis',
            'regression', 'correlation', 'bayesian', 'markov', 'random variable'
        ],
        DomainType.GEOMETRY: [
            'triangle', 'circle', 'polygon', 'angle', 'coordinate', 'distance',
            'area', 'volume', 'perimeter', 'euclidean', 'transformation'
        ],
        DomainType.DISCRETE_MATH: [
            'graph', 'tree', 'combinatorics', 'permutation', 'combination',
            'recurrence', 'partition', 'counting', 'path', 'cycle'
        ],
        DomainType.LOGIC: [
            'proof', 'theorem', 'proposition', 'predicate', 'quantifier',
            'satisfiable', 'valid', 'implication', 'conjunction', 'disjunction'
        ],
        DomainType.INFORMATION_THEORY: [
            'entropy', 'mutual information', 'channel capacity', 'coding',
            'huffman', 'hamming', 'compression', 'bit rate', 'information'
        ],
        DomainType.CRYPTOGRAPHY: [
            'encrypt', 'decrypt', 'rsa', 'modular', 'prime', 'hash',
            'signature', 'key exchange', 'diffie-hellman', 'elgamal'
        ],
        DomainType.OPTIMIZATION: [
            'minimize', 'maximize', 'optimal', 'constraint', 'simplex',
            'gradient descent', 'knapsack', 'linear program', 'convex'
        ],
        DomainType.CATEGORY_THEORY: [
            'functor', 'morphism', 'category', 'natural transformation',
            'limit', 'colimit', 'product', 'coproduct', 'universal'
        ],
        DomainType.PHYSICS: [
            'force', 'energy', 'momentum', 'velocity', 'acceleration',
            'wave', 'circuit', 'field', 'quantum', 'thermodynamic'
        ],
        DomainType.NUMERICAL: [
            'numerical', 'approximation', 'iteration', 'newton-raphson',
            'interpolation', 'floating point', 'precision', 'convergence rate'
        ]
    }

    def __init__(self, agent_id: str = 'multi_domain_coordinator_001',
                 df=None, blackboard=None):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        # Lazy-loaded supervisors
        self._supervisors: Dict[DomainType, Any] = {}

        # Active plans
        self.plans: Dict[str, TeamPlan] = {}

        if self.df:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
            self.df.register(create_service_registration(
                service_type='math.coordinator',
                agent_id=agent_id,
                algorithm='multi_domain_orchestration',
                cost='low',
                instance=self,
                tier='1',
                capabilities='domain_detection_decomposition_synthesis'
            ))

        logger.info(f"[{agent_id}] Multi-Domain Team Coordinator initialized")

    def _get_supervisor(self, domain: DomainType):
        """Lazy load a domain supervisor."""
        if domain not in self._supervisors:
            if domain == DomainType.ALGEBRA:
                from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
                self._supervisors[domain] = AlgebraSupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.CALCULUS:
                from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor
                self._supervisors[domain] = CalculusSupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.LINEAR_ALGEBRA:
                from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import LinearAlgebraSupervisor
                self._supervisors[domain] = LinearAlgebraSupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.STATISTICS:
                from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import StatisticsSupervisor
                self._supervisors[domain] = StatisticsSupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.GEOMETRY:
                from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import GeometrySupervisor
                self._supervisors[domain] = GeometrySupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.DISCRETE_MATH:
                from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import DiscreteMathSupervisor
                self._supervisors[domain] = DiscreteMathSupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.LOGIC:
                from symbo_agentic_reasoners.agents.supervisors.logic_supervisor import LogicSupervisor
                self._supervisors[domain] = LogicSupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.INFORMATION_THEORY:
                from symbo_agentic_reasoners.agents.supervisors.information_theory_supervisor import InformationTheorySupervisor
                self._supervisors[domain] = InformationTheorySupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.CRYPTOGRAPHY:
                from symbo_agentic_reasoners.agents.supervisors.cryptography_supervisor import CryptographySupervisor
                self._supervisors[domain] = CryptographySupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.OPTIMIZATION:
                from symbo_agentic_reasoners.agents.supervisors.optimization_supervisor import OptimizationSupervisor
                self._supervisors[domain] = OptimizationSupervisor(df=self.df, blackboard=self.blackboard)
            elif domain == DomainType.CATEGORY_THEORY:
                from symbo_agentic_reasoners.agents.supervisors.category_theory_supervisor import CategoryTheorySupervisor
                self._supervisors[domain] = CategoryTheorySupervisor(df=self.df, blackboard=self.blackboard)
            # Physics supervisors are split by subdomain
            elif domain == DomainType.PHYSICS:
                from symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor import PhysicsMechanicsSupervisor
                self._supervisors[domain] = PhysicsMechanicsSupervisor(df=self.df, blackboard=self.blackboard)
            else:
                logger.warning(f"No supervisor found for domain: {domain}")
                return None

        return self._supervisors.get(domain)

    def update_beliefs(self):
        """PERCEIVE: Monitor for multi-domain tasks."""
        if not self.blackboard:
            return
        try:
            from symbo_agentic_reasoners.core.blackboard import EntryStatus
            tasks = self.blackboard.query_entries(tags=['multi_domain'], status=EntryStatus.PENDING)
            tasks += self.blackboard.query_entries(tags=['complex_problem'], status=EntryStatus.PENDING)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'coordinated_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create multi-domain coordination plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            steps = ['analyze_problem', 'create_plan', 'execute_plan', 'synthesize_results']
            intention = Intention(
                plan_id=f'coordinate_{task_id}',
                steps=steps,
                target_desire='multi_domain_coordination',
                metadata={'task_id': task_id, 'task_entry': task}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Coordinate multi-domain tasks."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')

        if action == 'analyze_problem':
            self.add_belief(f'coordinated_task_{task.entry_id}', True, confidence=1.0)
            domains = self.detect_domains(str(task.content))
            intention.metadata['detected_domains'] = domains
            intention.advance()
        elif action == 'create_plan':
            self._create_plan(intention)
        elif action == 'execute_plan':
            self._execute_plan(intention)
        elif action == 'synthesize_results':
            self._synthesize_results(intention)

    # =========================================================================
    # DOMAIN DETECTION
    # =========================================================================

    def detect_domains(self, problem_text: str) -> List[DomainType]:
        """
        Detect which mathematical domains are involved in a problem.

        Args:
            problem_text: The problem description

        Returns:
            List of detected domains, ordered by relevance
        """
        text_lower = problem_text.lower()
        domain_scores: Dict[DomainType, int] = {}

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                domain_scores[domain] = score

        # Sort by score descending
        sorted_domains = sorted(domain_scores.keys(),
                                key=lambda d: domain_scores[d],
                                reverse=True)

        return sorted_domains

    def analyze_problem(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive problem analysis.

        Args:
            problem: Problem specification

        Returns:
            Analysis results including domains, complexity, and suggested approach
        """
        description = problem.get('description', '')
        expression = problem.get('expression', '')
        full_text = f"{description} {expression}"

        detected_domains = self.detect_domains(full_text)

        # Estimate complexity
        complexity = 'simple'
        if len(detected_domains) > 1:
            complexity = 'moderate'
        if len(detected_domains) > 2:
            complexity = 'complex'

        # Suggest approach
        if len(detected_domains) == 1:
            approach = 'single_domain'
        elif len(detected_domains) == 2:
            approach = 'sequential_domains'
        else:
            approach = 'parallel_decomposition'

        return {
            'detected_domains': [d.value for d in detected_domains],
            'primary_domain': detected_domains[0].value if detected_domains else None,
            'complexity': complexity,
            'suggested_approach': approach,
            'requires_coordination': len(detected_domains) > 1
        }

    # =========================================================================
    # TASK DECOMPOSITION
    # =========================================================================

    def decompose_problem(self, problem: Dict[str, Any]) -> TeamPlan:
        """
        Decompose a complex problem into domain-specific subtasks.

        Args:
            problem: The problem to decompose

        Returns:
            TeamPlan with subtasks and execution order
        """
        description = problem.get('description', '')
        detected_domains = self.detect_domains(description)

        plan_id = f"plan_{hash(description) % 10000}"
        tasks = []
        task_counter = 0

        # Create tasks for each detected domain
        for domain in detected_domains:
            task_id = f"task_{task_counter}"
            task_counter += 1

            # Extract domain-specific parameters
            domain_params = self._extract_domain_parameters(problem, domain)

            task = DomainTask(
                task_id=task_id,
                domain=domain,
                description=f"{domain.value} component of: {description[:100]}",
                parameters=domain_params
            )
            tasks.append(task)

        # Determine execution order (simple: sequential for now)
        execution_order = [[t.task_id] for t in tasks]

        plan = TeamPlan(
            plan_id=plan_id,
            problem_description=description,
            tasks=tasks,
            execution_order=execution_order,
            final_synthesis="Combine results from all domain tasks"
        )

        self.plans[plan_id] = plan
        return plan

    def _extract_domain_parameters(self, problem: Dict[str, Any],
                                   domain: DomainType) -> Dict[str, Any]:
        """Extract parameters relevant to a specific domain."""
        params = {}

        # Copy general parameters
        for key in ['expression', 'equations', 'constraints', 'objective', 'data']:
            if key in problem:
                params[key] = problem[key]

        # Add domain-specific type hints
        params['domain'] = domain.value

        return params

    # =========================================================================
    # PLAN EXECUTION
    # =========================================================================

    def _create_plan(self, intention: Intention):
        """Create execution plan from detected domains."""
        task = intention.metadata.get('task_entry')
        domains = intention.metadata.get('detected_domains', [])

        problem = {
            'description': str(task.content) if hasattr(task, 'content') else '',
            **(task.metadata if hasattr(task, 'metadata') else {})
        }

        plan = self.decompose_problem(problem)
        intention.metadata['plan'] = plan
        intention.advance()

    def _execute_plan(self, intention: Intention):
        """Execute the plan by routing to domain supervisors."""
        plan = intention.metadata.get('plan')
        if not plan:
            intention.advance()
            return

        results = {}

        for task_batch in plan.execution_order:
            for task_id in task_batch:
                task = next((t for t in plan.tasks if t.task_id == task_id), None)
                if task:
                    task.status = 'running'
                    result = self._execute_domain_task(task)
                    task.result = result
                    task.status = 'completed' if 'error' not in result else 'failed'
                    results[task_id] = result

        intention.metadata['domain_results'] = results
        intention.advance()

    def _execute_domain_task(self, task: DomainTask) -> Dict[str, Any]:
        """Execute a single domain task."""
        supervisor = self._get_supervisor(task.domain)

        if not supervisor:
            return {'error': f'No supervisor for domain: {task.domain.value}'}

        try:
            # Try to use the supervisor's solve method if available
            if hasattr(supervisor, 'solve'):
                return supervisor.solve(task.parameters)
            else:
                return {
                    'domain': task.domain.value,
                    'status': 'delegated',
                    'message': 'Task delegated to supervisor'
                }
        except Exception as e:
            logger.error(f"Domain task execution failed: {e}")
            return {'error': str(e), 'domain': task.domain.value}

    def _synthesize_results(self, intention: Intention):
        """Synthesize results from multiple domains."""
        domain_results = intention.metadata.get('domain_results', {})
        plan = intention.metadata.get('plan')

        synthesis = {
            'plan_id': plan.plan_id if plan else 'unknown',
            'domains_involved': [t.domain.value for t in (plan.tasks if plan else [])],
            'domain_results': domain_results,
            'synthesis': self._combine_results(domain_results),
            'method': 'multi_domain_coordination'
        }

        intention.metadata['final_result'] = synthesis
        self.tasks_executed += 1
        intention.mark_completed()

    def _combine_results(self, domain_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine results from multiple domains into a coherent answer."""
        combined = {
            'success': all('error' not in r for r in domain_results.values()),
            'partial_results': [],
            'errors': []
        }

        for task_id, result in domain_results.items():
            if 'error' in result:
                combined['errors'].append({
                    'task': task_id,
                    'error': result['error']
                })
            else:
                combined['partial_results'].append({
                    'task': task_id,
                    'result': result
                })

        return combined

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def solve(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a potentially multi-domain mathematical problem.

        Args:
            problem: Problem specification with 'description' and relevant data

        Returns:
            Solution dictionary with results from all involved domains
        """
        # Analyze the problem
        analysis = self.analyze_problem(problem)

        if not analysis['requires_coordination']:
            # Single domain - delegate directly
            if analysis['primary_domain'] is None:
                return {'error': 'No mathematical domain detected in problem'}
            primary_domain = DomainType(analysis['primary_domain'])
            supervisor = self._get_supervisor(primary_domain)
            if supervisor and hasattr(supervisor, 'solve'):
                return supervisor.solve(problem)
            return {'error': f'No solver for domain: {analysis["primary_domain"]}'}

        # Multi-domain problem - decompose and coordinate
        plan = self.decompose_problem(problem)
        results = {}

        for task_batch in plan.execution_order:
            for task_id in task_batch:
                task = next((t for t in plan.tasks if t.task_id == task_id), None)
                if task:
                    result = self._execute_domain_task(task)
                    task.result = result
                    results[task_id] = result

        return {
            'analysis': analysis,
            'plan_id': plan.plan_id,
            'domain_results': results,
            'synthesis': self._combine_results(results),
            'method': 'multi_domain_team_coordination'
        }

    def solve_with_dependencies(self, problem: Dict[str, Any],
                                 dependencies: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Solve a problem with explicit dependencies between domain tasks.

        Args:
            problem: Problem specification
            dependencies: List of (prerequisite_domain, dependent_domain) pairs

        Returns:
            Solution with results respecting dependencies
        """
        plan = self.decompose_problem(problem)

        # Build dependency graph
        task_by_domain = {t.domain.value: t for t in plan.tasks}

        for prereq, dependent in dependencies:
            if prereq in task_by_domain and dependent in task_by_domain:
                task_by_domain[dependent].dependencies.append(
                    task_by_domain[prereq].task_id
                )

        # Topological sort for execution order
        execution_order = self._topological_sort(plan.tasks)
        plan.execution_order = execution_order

        # Execute with dependencies
        results = {}
        for batch in execution_order:
            for task_id in batch:
                task = next((t for t in plan.tasks if t.task_id == task_id), None)
                if task:
                    # Pass prerequisite results to dependent tasks
                    for dep_id in task.dependencies:
                        if dep_id in results:
                            task.parameters['prerequisite_results'] = results[dep_id]

                    result = self._execute_domain_task(task)
                    task.result = result
                    results[task_id] = result

        return {
            'plan_id': plan.plan_id,
            'execution_order': execution_order,
            'domain_results': results,
            'synthesis': self._combine_results(results)
        }

    def _topological_sort(self, tasks: List[DomainTask]) -> List[List[str]]:
        """Topological sort tasks based on dependencies."""
        # Simple implementation - group tasks by dependency level
        task_dict = {t.task_id: t for t in tasks}
        levels: List[List[str]] = []
        remaining = set(t.task_id for t in tasks)
        completed = set()

        while remaining:
            # Find tasks with all dependencies satisfied
            ready = []
            for task_id in remaining:
                task = task_dict[task_id]
                if all(d in completed for d in task.dependencies):
                    ready.append(task_id)

            if not ready:
                # Circular dependency or error - just add remaining
                levels.append(list(remaining))
                break

            levels.append(ready)
            completed.update(ready)
            remaining -= set(ready)

        return levels

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Return coordinator statistics."""
        loaded_supervisors = [d.value for d in self._supervisors.keys()]

        return {
            'agent_id': self.agent_id,
            'tier': 1,
            'role': 'coordinator',
            'tasks_executed': self.tasks_executed,
            'active_plans': len(self.plans),
            'loaded_supervisors': loaded_supervisors,
            'available_domains': [d.value for d in DomainType],
            'capabilities': [
                'domain_detection', 'problem_decomposition',
                'parallel_execution', 'result_synthesis',
                'dependency_handling'
            ]
        }
