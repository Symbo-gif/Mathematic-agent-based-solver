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
PHASE 2 - PROBABILITY & STATISTICS SUPERVISOR (Tier 2)
=====================================================

Enforces strict philosophical separation between Bayesian and Frequentist methods.
Routes tasks to appropriate specialists based on statistical paradigm and task type.

DIRECTIVE:
---------
Route statistics tasks based on:
- Philosophical approach (Bayesian vs Frequentist)
- Distribution type (continuous, discrete, multivariate)
- Analysis type (inference, estimation, testing)

ROUTING LOGIC:
-------------
- Prior/posterior, belief updates -> Bayesian Engine
- Confidence intervals, p-values, hypothesis tests -> Frequentist Agent
- Distribution operations (PDF, CDF, moments) -> Distribution Specialist

CRITICAL:
--------
This supervisor enforces philosophical coherence. Mixing Bayesian and
Frequentist approaches in the same analysis is FORBIDDEN.

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Statistics Domain
- Phase 2 Coding Strategy: Section 3.4 "Statistics Team"
"""

from typing import List, Dict, Any, Optional
import uuid

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)


class StatisticsSupervisor(BDIAgent):
    """
    Statistics Supervisor - Tier 2 Strategic Router

    ROLE:
    ----
    Acts as foreman for all statistics tasks. Routes tasks based on
    statistical paradigm (Bayesian vs Frequentist) and analysis type.

    CRITICAL:
    --------
    This supervisor enforces philosophical coherence:
    1. Bayesian tasks go ONLY to Bayesian Engine
    2. Frequentist tasks go ONLY to Frequentist Agent
    3. NEVER mix paradigms in the same analysis

    ROUTING STRATEGY:
    ----------------
    - Prior/posterior, belief update, credible intervals -> Bayesian
    - Confidence intervals, p-values, null hypothesis -> Frequentist
    - PDF, CDF, moments, sampling -> Distribution Specialist
    """

    def __init__(
        self,
        agent_id: str = 'stats_supervisor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Statistics Supervisor

        Args:
            agent_id: Unique supervisor identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.bayesian_routes = 0
        self.frequentist_routes = 0
        self.distribution_routes = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Statistics Supervisor initialized")
        print(f"  Role: Bayesian vs Frequentist routing")
        print(f"  Mode: Philosophical coherence enforcement")

    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.stats',
            agent_id=self.agent_id,
            algorithm='routing',
            cost='low',
            instance=self,
            type='supervisor',
            domain='statistics',
            decision_logic='bayesian_vs_frequentist',
            tier='2'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.stats (supervisor)")

    def process(self, task_entry: Any) -> Any:
        """
        Process statistics task by routing to appropriate specialist

        Args:
            task_entry: Blackboard entry containing task

        Returns:
            Result from specialist (via Blackboard)
        """
        print(f"\n[{self.agent_id}] Processing statistics task")

        # Extract task metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '')

        print(f"  Task: {raw_input}")

        # Analyze task to determine routing
        routing_decision = self._analyze_task(task_entry)

        print(f"  Routing decision: {routing_decision['target']}")
        print(f"  Paradigm: {routing_decision.get('paradigm', 'N/A')}")
        print(f"  Reasoning: {routing_decision['reason']}")

        # Update paradigm counters
        paradigm = routing_decision.get('paradigm')
        if paradigm == 'bayesian':
            self.bayesian_routes += 1
        elif paradigm == 'frequentist':
            self.frequentist_routes += 1
        else:
            self.distribution_routes += 1

        # Query DF for appropriate specialist
        specialist_service = routing_decision['service_type']
        specialists = self._find_specialists(specialist_service)

        if not specialists:
            error_msg = f"No specialist available for: {specialist_service}"
            print(f"  [ERROR] {error_msg}")
            return self._create_error_result(task_entry, error_msg)

        print(f"  Found specialist: {specialists[0].agent_id}")

        # Delegate to specialist via Blackboard
        result = self._delegate_to_specialist(task_entry, specialists[0], routing_decision)

        self.tasks_routed += 1

        return result

    def _analyze_task(self, task_entry: Any) -> Dict[str, Any]:
        """
        Analyze task to determine routing strategy

        This implements the supervisor's strategic logic for determining
        the correct statistical paradigm and specialist.

        Args:
            task_entry: Task to analyze

        Returns:
            Routing decision with target service type, paradigm, and reasoning
        """
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()
        operation = metadata.get('operation', 'compute')

        # TIME SERIES (BEFORE general stats - Phase 2)
        timeseries_keywords = [
            'time series', 'arima', 'autoregressive', 'moving average',
            'kalman filter', 'state space', 'forecasting', 'trend', 'seasonality',
            'acf', 'pacf', 'stationarity', 'box-jenkins'
        ]
        if any(kw in raw_input for kw in timeseries_keywords):
            return {
                'target': 'Time Series Specialist',
                'service_type': 'math.statistics.timeseries',
                'paradigm': 'timeseries',
                'reason': 'Detected time series keywords (ARIMA/forecasting/etc)'
            }

        # BAYESIAN DECISION THEORY (BEFORE general Bayesian - Phase 2)
        bayesian_decision_keywords = [
            'utility', 'decision theory', 'loss function', 'bayes risk',
            'minimax', 'admissible', 'decision rule', 'optimal stopping',
            'multi-armed bandit', 'sequential decision', 'posterior risk'
        ]
        if any(kw in raw_input for kw in bayesian_decision_keywords):
            return {
                'target': 'Bayesian Decision Specialist',
                'service_type': 'math.statistics.bayesian.decision',
                'paradigm': 'bayesian_decision',
                'reason': 'Detected Bayesian decision theory keywords (utility/loss/etc)'
            }

        # Bayesian keywords (highest priority for paradigm enforcement)
        bayesian_keywords = [
            'prior', 'posterior', 'bayes', 'bayesian', 'belief',
            'credible interval', 'likelihood', 'conjugate',
            'mcmc', 'markov chain', 'gibbs', 'metropolis',
            'update belief', 'probabilistic inference'
        ]
        if any(kw in raw_input for kw in bayesian_keywords):
            return {
                'target': 'Bayesian Engine',
                'service_type': 'math.statistics.bayesian',
                'paradigm': 'bayesian',
                'reason': 'Detected Bayesian inference keywords'
            }

        # Frequentist keywords
        frequentist_keywords = [
            'confidence interval', 'p-value', 'p value', 'pvalue',
            'null hypothesis', 'alternative hypothesis', 'significance',
            'alpha level', 'type i error', 'type ii error',
            't-test', 'z-test', 'chi-square', 'anova', 'f-test',
            'regression coefficient', 'standard error', 'reject'
        ]
        if any(kw in raw_input for kw in frequentist_keywords):
            return {
                'target': 'Frequentist Agent',
                'service_type': 'math.statistics.frequentist',
                'paradigm': 'frequentist',
                'reason': 'Detected Frequentist inference keywords'
            }

        # Distribution operations (paradigm-neutral)
        distribution_keywords = [
            'distribution', 'pdf', 'cdf', 'pmf', 'probability density',
            'cumulative', 'quantile', 'percentile', 'moment',
            'mean', 'variance', 'standard deviation', 'skewness', 'kurtosis',
            'normal', 'gaussian', 'binomial', 'poisson', 'exponential',
            'uniform', 'gamma', 'beta', 'sample', 'random'
        ]
        if any(kw in raw_input for kw in distribution_keywords):
            return {
                'target': 'Distribution Specialist',
                'service_type': 'math.statistics.distributions',
                'paradigm': 'neutral',
                'reason': 'Detected distribution/probability keywords'
            }

        # Default to Distribution Specialist for general stats
        return {
            'target': 'Distribution Specialist',
            'service_type': 'math.statistics.distributions',
            'paradigm': 'neutral',
            'reason': 'Default routing for general statistics'
        }

    def _find_specialists(self, service_type: str) -> List[Any]:
        """Query Directory Facilitator for specialists"""
        if not self.df:
            return []
        return self.df.search(service_type=service_type)

    def _delegate_to_specialist(
        self,
        task_entry: Any,
        specialist: Any,
        routing_decision: Dict[str, Any]
    ) -> Any:
        """
        Delegate task to specialist via Blackboard

        Args:
            task_entry: Original task
            specialist: Specialist service registration
            routing_decision: Routing analysis

        Returns:
            Delegation result
        """
        if not self.blackboard:
            return self._create_error_result(task_entry, "No Blackboard available")

        # Create delegated task entry
        delegation_id = f'delegation_{uuid.uuid4().hex[:8]}'

        # Update task metadata to include routing info
        delegated_metadata = dict(task_entry.metadata) if hasattr(task_entry, 'metadata') else {}
        delegated_metadata.update({
            'delegated_by': self.agent_id,
            'delegation_id': delegation_id,
            'assigned_agent': specialist.agent_id,
            'routing_reason': routing_decision['reason'],
            'paradigm': routing_decision.get('paradigm', 'neutral')
        })

        # Post delegated task
        delegated_entry = create_entry(
            entry_type=EntryType.TASK,
            content=task_entry.content,
            author_agent=self.agent_id,
            conversation_id=delegation_id,
            tags=[routing_decision['service_type'].split('.')[-1], 'delegated', delegation_id],
            metadata=delegated_metadata
        )

        self.blackboard.post(delegated_entry)

        print(f"  [OK] Delegated to {specialist.agent_id}")

        return delegated_entry

    def _create_error_result(self, task_entry: Any, error_msg: str) -> Any:
        """Create error result entry"""
        self.tasks_failed += 1

        if not self.blackboard:
            return None

        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=task_entry.content if hasattr(task_entry, 'content') else None,
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
            tags=['error'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================
    #
    # The Supervisor's BDI loop is about ROUTING, not computing:
    #   1. update_beliefs() - Find statistics tasks on Blackboard
    #   2. deliberate() - Decide which specialist should handle each
    #   3. execute_step() - Delegate to specialist, track results
    #
    # CRITICAL: Supervisors NEVER compute. They analyze, decide, and delegate.
    # ==========================================================================

    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for statistics tasks that need routing.

        The supervisor looks for:
        1. New stats tasks that haven't been routed yet
        2. Completed delegated tasks (to aggregate results)
        3. Failed delegated tasks (to handle errors or retry)
        """
        if not self.blackboard:
            return

        try:
            # Find pending stats tasks
            pending_tasks = self.blackboard.query_entries(
                tags=['stats', 'statistics'],
                status=EntryStatus.PENDING
            )

            # Also find tasks tagged with 'task' that might be stats
            task_entries = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            # Filter to stats-related tasks
            for task in task_entries:
                domain = ''
                if hasattr(task, 'metadata') and task.metadata:
                    domain = task.metadata.get('domain', '').lower()

                # Include if domain is stats or unspecified (we'll analyze it)
                if domain in ['stats', 'statistics', ''] and task not in pending_tasks:
                    pending_tasks.append(task)

            # Add beliefs about unrouted tasks
            for task in pending_tasks:
                belief_key = f'pending_stats_{task.entry_id}'

                # Skip if already being handled
                if self.has_belief(f'routed_{task.entry_id}'):
                    continue
                if self.has_belief(f'delegated_{task.entry_id}'):
                    continue

                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )

            # Check on delegated tasks
            for predicate in list(self.beliefs.keys()):
                if predicate.startswith('delegated_'):
                    delegation_info = self.get_belief(predicate).content
                    delegation_id = delegation_info.get('delegation_id')

                    # Check if specialist has completed the task
                    results = self.blackboard.query_entries(
                        tags=[delegation_id, 'result'],
                        status=EntryStatus.COMPLETED
                    )

                    if results:
                        # Task completed - add belief about result
                        self.add_belief(
                            f'result_{delegation_id}',
                            results[0],
                            source='specialist'
                        )
                        self.remove_belief(predicate)
                        self.tasks_completed += 1

                    # Also check for failures
                    failures = self.blackboard.query_entries(
                        tags=[delegation_id],
                        status=EntryStatus.FAILED
                    )

                    if failures:
                        self.add_belief(
                            f'failed_{delegation_id}',
                            failures[0],
                            source='specialist'
                        )
                        self.remove_belief(predicate)
                        self.tasks_failed += 1

        except Exception as e:
            print(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """
        DELIBERATE: Create routing plans for pending statistics tasks.

        For each pending task, the supervisor:
        1. Analyzes what kind of statistics problem it is
        2. Determines the best specialist (enforcing Bayesian vs Frequentist paradigm)
        3. Creates an intention to delegate

        Returns:
            List of new Intention objects for routing tasks
        """
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_stats_'):
                continue

            task = belief.content
            task_id = task.entry_id

            # Skip if already have an intention for this task
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            # Analyze the task to determine routing
            routing_decision = self._analyze_task(task)

            # Create routing intention
            intention = Intention(
                plan_id=f'route_{task_id}',
                steps=['analyze_task', 'find_specialist', 'delegate_task', 'track_result'],
                target_desire='route_stats_task',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'routing_decision': routing_decision
                }
            )

            new_intentions.append(intention)
            print(f"[{self.agent_id}] Created routing plan for {task_id} -> {routing_decision['target']} ({routing_decision.get('paradigm', 'neutral')})")

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Execute one step of the routing plan.

        Steps:
        1. analyze_task - Determine task type (already done in deliberate)
        2. find_specialist - Query DF for appropriate specialist
        3. delegate_task - Post delegated task to Blackboard
        4. track_result - Monitor for completion (handled by update_beliefs)

        CRITICAL: Supervisor NEVER computes. It only routes.
        """
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')
        routing = intention.metadata.get('routing_decision', {})

        print(f"[{self.agent_id}] Executing step: {action} for task {task_id}")

        try:
            if action == 'analyze_task':
                # Analysis already done in deliberate, just advance
                print(f"[{self.agent_id}] Task analysis: {routing.get('reason', 'unknown')}")
                intention.advance()

            elif action == 'find_specialist':
                self._execute_find_specialist(intention, routing)

            elif action == 'delegate_task':
                self._execute_delegate_task(intention, task, routing)

            elif action == 'track_result':
                self._execute_track_result(intention, task_id)

            else:
                print(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            print(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_routing_failure(intention, task, str(e))

    def _execute_find_specialist(self, intention: Intention, routing: Dict[str, Any]):
        """Find appropriate specialist via Directory Facilitator"""
        service_type = routing.get('service_type', 'math.statistics.distributions')

        specialists = self._find_specialists(service_type)

        if specialists:
            # Store found specialist in intention metadata
            intention.metadata['specialist'] = specialists[0]
            print(f"[{self.agent_id}] Found specialist: {specialists[0].agent_id}")
            intention.advance()
        else:
            # No specialist found - try fallback to distribution specialist
            if service_type != 'math.statistics.distributions':
                print(f"[{self.agent_id}] No {service_type} specialist, trying distributions")
                fallback = self._find_specialists('math.statistics.distributions')
                if fallback:
                    intention.metadata['specialist'] = fallback[0]
                    intention.advance()
                    return

            raise ValueError(f"No specialist available for {service_type}")

    def _execute_delegate_task(self, intention: Intention, task: Any, routing: Dict[str, Any]):
        """Delegate task to specialist via Blackboard"""
        specialist = intention.metadata.get('specialist')
        task_id = intention.metadata['task_id']

        if not specialist:
            raise ValueError("No specialist found for delegation")

        if not self.blackboard:
            raise ValueError("No Blackboard available")

        # Create delegation ID
        delegation_id = f'delegation_{uuid.uuid4().hex[:8]}'

        # Prepare delegated task metadata
        delegated_metadata = dict(task.metadata) if hasattr(task, 'metadata') else {}
        delegated_metadata.update({
            'delegated_by': self.agent_id,
            'delegation_id': delegation_id,
            'assigned_agent': specialist.agent_id,
            'routing_reason': routing.get('reason', ''),
            'paradigm': routing.get('paradigm', 'neutral'),
            'original_task_id': task_id
        })

        # Determine tags based on specialist type
        specialist_tag = routing.get('service_type', 'distributions').split('.')[-1]

        # Post delegated task to Blackboard
        delegated_entry = create_entry(
            entry_type=EntryType.TASK,
            content=task.content,
            author_agent=self.agent_id,
            conversation_id=delegation_id,
            tags=[specialist_tag, 'delegated', delegation_id, 'task'],
            status=EntryStatus.PENDING,
            metadata=delegated_metadata
        )

        self.blackboard.post(delegated_entry)

        # Mark original task as routed
        self.add_belief(f'routed_{task_id}', True)

        # Track delegation
        self.add_belief(f'delegated_{task_id}', {
            'delegation_id': delegation_id,
            'specialist': specialist.agent_id,
            'delegated_entry_id': delegated_entry.entry_id
        })

        # Update original task status
        self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)

        # Clean up pending belief
        self.remove_belief(f'pending_stats_{task_id}')

        self.tasks_routed += 1
        print(f"[{self.agent_id}] Delegated task {task_id} to {specialist.agent_id} (delegation: {delegation_id})")

        intention.advance()

    def _execute_track_result(self, intention: Intention, task_id: str):
        """
        Track result - this is handled asynchronously by update_beliefs.
        For now, just mark the routing as complete.
        """
        # The actual result tracking happens in update_beliefs
        # This step just marks the routing intention as complete
        print(f"[{self.agent_id}] Routing complete for task {task_id}, awaiting specialist result")
        intention.advance()

    def _handle_routing_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle routing failure"""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            # Post error to Blackboard
            error_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=task.content if hasattr(task, 'content') else None,
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                tags=['error', 'routing_failed', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)

        # Clean up beliefs
        if task_id:
            self.remove_belief(f'pending_stats_{task_id}')

        self.tasks_failed += 1

        # Mark intention complete (failed)
        while not intention.is_complete():
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Get supervisor statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'bayesian_routes': self.bayesian_routes,
            'frequentist_routes': self.frequentist_routes,
            'distribution_routes': self.distribution_routes
        })
        return stats


if __name__ == "__main__":
    """Test Statistics Supervisor"""
    print("=" * 80)
    print("STATISTICS SUPERVISOR TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.system import Phase0System

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Statistics Supervisor
    supervisor = StatisticsSupervisor(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    # Test routing analysis
    print("Testing routing decisions:")

    class MockEntry:
        def __init__(self, raw_input):
            self.metadata = {'raw_input': raw_input}
            self.content = None

    test_cases = [
        ("Update the posterior distribution", "Bayesian"),
        ("Calculate the 95% confidence interval", "Frequentist"),
        ("Find the PDF of a normal distribution", "Distribution"),
        ("Compute the p-value for the test", "Frequentist"),
        ("What is the credible interval?", "Bayesian"),
        ("Sample from a Poisson distribution", "Distribution"),
        ("Run a t-test on the data", "Frequentist"),
        ("Compute prior probability", "Bayesian"),
    ]

    for test, expected in test_cases:
        decision = supervisor._analyze_task(MockEntry(test))
        actual = decision['target'].split()[0]
        status = 'OK' if expected in decision['target'] else 'MISMATCH'
        print(f"  [{status}] \"{test[:35]}...\" -> {decision['target']} ({decision.get('paradigm', 'N/A')})")

    print()
    print("Statistics:")
    import json
    print(json.dumps(supervisor.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
