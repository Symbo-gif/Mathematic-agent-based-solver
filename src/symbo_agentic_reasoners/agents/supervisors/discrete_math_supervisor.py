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
PHASE 2 - DISCRETE MATHEMATICS SUPERVISOR (Tier 2)
==================================================

Strategic router for discrete mathematics tasks including combinatorics,
graph theory, set theory, Boolean algebra, recurrences, and automata.

DIRECTIVE:
---------
Route discrete math tasks to appropriate specialists based on:
- Problem structure (counting, graphs, sets, logic circuits)
- Algorithm requirements (traversal, enumeration, optimization, minimization)
- Complexity considerations

ROUTING LOGIC (6 specialists):
-----------------------------
- Counting, permutations, combinations -> Combinatorics Agent
- Graphs, paths, trees, networks -> Graph Theory Agent
- Sets, relations, functions -> Set Theory Agent
- Recurrences, sequences, Master theorem -> Recurrence Relation Agent
- Boolean minimization, Karnaugh maps -> Boolean Algebra Agent
- DFA, NFA, regex, automata -> Finite Automata Agent

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Discrete Math Domain
- Phase 2 Coding Strategy: Section 3.5 "Discrete Math Team"
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


class DiscreteMathSupervisor(BDIAgent):
    """
    Discrete Mathematics Supervisor - Tier 2 Strategic Router

    ROLE:
    ----
    Acts as foreman for all discrete mathematics tasks. Routes tasks to
    appropriate specialists based on problem structure and algorithm needs.

    CRITICAL:
    --------
    Like all supervisors, this agent NEVER computes. It only:
    1. Analyzes problem structure
    2. Determines optimal algorithm/specialist
    3. Routes to appropriate specialist
    4. Aggregates results

    ROUTING STRATEGY:
    ----------------
    - Counting, arrangements, selections -> Combinatorics
    - Graphs, networks, paths, cycles -> Graph Theory
    """

    def __init__(
        self,
        agent_id: str = 'discrete_math_supervisor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Discrete Mathematics Supervisor

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
        self.combinatorics_routes = 0
        self.graph_theory_routes = 0
        self.set_theory_routes = 0
        self.recurrence_routes = 0
        self.boolean_algebra_routes = 0
        self.automata_routes = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Discrete Math Supervisor initialized")
        print(f"  Role: Strategic router for combinatorics/graph theory")
        print(f"  Mode: Analysis and delegation only - NEVER computes")

    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.discrete',
            agent_id=self.agent_id,
            algorithm='routing',
            cost='low',
            instance=self,
            type='supervisor',
            domain='discrete_math',
            tier='2'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.discrete (supervisor)")

    def process(self, task_entry: Any) -> Any:
        """
        Process discrete math task by routing to appropriate specialist

        Args:
            task_entry: Blackboard entry containing task

        Returns:
            Result from specialist (via Blackboard)
        """
        print(f"\n[{self.agent_id}] Processing discrete math task")

        # Extract task metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '')

        print(f"  Task: {raw_input}")

        # Analyze task to determine routing
        routing_decision = self._analyze_task(task_entry)

        print(f"  Routing decision: {routing_decision['target']}")
        print(f"  Reasoning: {routing_decision['reason']}")

        # Update category counters
        service_type = routing_decision['service_type']
        if 'combinatorics' in service_type:
            self.combinatorics_routes += 1
        elif 'graphs' in service_type:
            self.graph_theory_routes += 1
        elif 'sets' in service_type:
            self.set_theory_routes += 1
        elif 'recurrence' in service_type:
            self.recurrence_routes += 1
        elif 'boolean' in service_type:
            self.boolean_algebra_routes += 1
        elif 'automata' in service_type:
            self.automata_routes += 1

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

        This implements the supervisor's strategic logic for understanding
        discrete math problem structure.

        Routes to 6 specialists:
        - CombinatoricsAgent: counting, permutations, combinations
        - GraphTheoryAgent: graphs, networks, paths
        - SetTheoryAgent: sets, relations, functions
        - RecurrenceRelationAgent: recurrences, sequences
        - BooleanAlgebraAgent: Boolean minimization, Karnaugh maps
        - FiniteAutomataAgent: DFA, NFA, regex

        Args:
            task_entry: Task to analyze

        Returns:
            Routing decision with target service type and reasoning
        """
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()
        operation = metadata.get('operation', 'compute')

        # === FINITE AUTOMATA (highest priority for explicit keywords) ===
        automata_keywords = [
            'automaton', 'automata', 'dfa', 'nfa', 'finite state',
            'regular expression', 'regex', 'regexp',
            'state machine', 'transition', 'accept',
            'thompson', 'hopcroft', 'subset construction',
            'language accepted', 'regular language', 'kleene'
        ]
        if any(kw in raw_input for kw in automata_keywords):
            return {
                'target': 'Finite Automata Agent',
                'service_type': 'math.discrete.automata',
                'reason': 'Detected automata/regex keywords'
            }

        # === BOOLEAN ALGEBRA ===
        boolean_keywords = [
            'boolean', 'minimize', 'minterm', 'maxterm',
            'karnaugh', 'k-map', 'kmap', 'quine', 'mccluskey',
            'truth table', 'dnf', 'cnf', 'disjunctive', 'conjunctive',
            'prime implicant', 'logic circuit', 'digital logic',
            'nand', 'nor', 'xor', 'logic gate', 'simplify boolean'
        ]
        if any(kw in raw_input for kw in boolean_keywords):
            return {
                'target': 'Boolean Algebra Agent',
                'service_type': 'math.discrete.boolean',
                'reason': 'Detected Boolean algebra/minimization keywords'
            }

        # === RECURRENCE RELATIONS ===
        recurrence_keywords = [
            'recurrence', 'recursive', 'fibonacci', 'lucas',
            'characteristic equation', 'linear recurrence',
            'master theorem', 'divide and conquer', 'complexity',
            'a_n', 'f(n)', 'sequence solve', 'closed form',
            'homogeneous', 'non-homogeneous', 'particular solution'
        ]
        if any(kw in raw_input for kw in recurrence_keywords):
            return {
                'target': 'Recurrence Relation Agent',
                'service_type': 'math.discrete.recurrence',
                'reason': 'Detected recurrence relation keywords'
            }

        # === SET THEORY ===
        set_keywords = [
            'set', 'union', 'intersection', 'difference', 'complement',
            'power set', 'cartesian', 'product', 'relation',
            'reflexive', 'symmetric', 'transitive', 'equivalence',
            'partial order', 'antisymmetric', 'function', 'injective',
            'surjective', 'bijective', 'domain', 'range', 'codomain',
            'subset', 'superset', 'element', 'cardinality'
        ]
        if any(kw in raw_input for kw in set_keywords):
            return {
                'target': 'Set Theory Agent',
                'service_type': 'math.discrete.sets',
                'reason': 'Detected set theory keywords'
            }

        # === SPECTRAL GRAPH THEORY (BEFORE general graph theory) ===
        spectral_graph_keywords = [
            'spectral graph', 'laplacian matrix', 'graph laplacian',
            'eigenvalue graph', 'adjacency spectrum', 'laplacian spectrum',
            'algebraic connectivity', 'fiedler', 'cheeger',
            'spectral clustering', 'expander graph', 'expansion',
            'graph eigenvalue', 'spectral gap', 'spectral radius graph'
        ]
        if any(kw in raw_input for kw in spectral_graph_keywords):
            return {
                'target': 'Spectral Graph Theory Specialist',
                'service_type': 'math.discrete.graphs.spectral',
                'reason': 'Detected spectral graph theory keywords (eigenvalues/Laplacian/etc)'
            }

        # === GRAPH THEORY ===
        graph_keywords = [
            'graph', 'vertex', 'vertices', 'edge', 'node',
            'path', 'cycle', 'tree', 'forest', 'spanning',
            'shortest path', 'dijkstra', 'bellman', 'floyd',
            'connected', 'component', 'degree', 'adjacency',
            'hamiltonian', 'eulerian', 'bipartite', 'planar',
            'coloring', 'chromatic', 'clique', 'independent set',
            'network', 'flow', 'cut', 'matching', 'traverse',
            'bfs', 'dfs', 'topological', 'strongly connected',
            'mst', 'kruskal', 'prim', 'minimum spanning'
        ]
        if any(kw in raw_input for kw in graph_keywords):
            return {
                'target': 'Graph Theory Agent',
                'service_type': 'math.discrete.graphs',
                'reason': 'Detected graph theory keywords'
            }

        # === COMBINATORICS (default for counting) ===
        combinatorics_keywords = [
            'permutation', 'combination', 'arrange', 'select',
            'choose', 'factorial', 'binomial', 'multinomial',
            'partition', 'derangement', 'stirling', 'catalan',
            'count', 'enumerate', 'ways', 'how many',
            'generating function', 'inclusion-exclusion',
            'pigeonhole', 'balls', 'boxes', 'distribute',
            'stars and bars', 'lattice path'
        ]
        if any(kw in raw_input for kw in combinatorics_keywords):
            return {
                'target': 'Combinatorics Agent',
                'service_type': 'math.discrete.combinatorics',
                'reason': 'Detected combinatorics keywords'
            }

        # Default to Combinatorics for general discrete math
        return {
            'target': 'Combinatorics Agent',
            'service_type': 'math.discrete.combinatorics',
            'reason': 'Default routing for general discrete math'
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
            'routing_reason': routing_decision['reason']
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

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for discrete math tasks that need routing."""
        if not self.blackboard:
            return

        try:
            # Find pending discrete math tasks
            pending_tasks = self.blackboard.query_entries(
                tags=['discrete', 'discrete_math'],
                status=EntryStatus.PENDING
            )

            task_entries = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            for task in task_entries:
                domain = ''
                if hasattr(task, 'metadata') and task.metadata:
                    domain = task.metadata.get('domain', '').lower()

                if domain in ['discrete', 'discrete_math', ''] and task not in pending_tasks:
                    pending_tasks.append(task)

            for task in pending_tasks:
                belief_key = f'pending_discrete_{task.entry_id}'

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

                    results = self.blackboard.query_entries(
                        tags=[delegation_id, 'result'],
                        status=EntryStatus.COMPLETED
                    )

                    if results:
                        self.add_belief(
                            f'result_{delegation_id}',
                            results[0],
                            source='specialist'
                        )
                        self.remove_belief(predicate)
                        self.tasks_completed += 1

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
        """DELIBERATE: Create routing plans for pending discrete math tasks."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_discrete_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            routing_decision = self._analyze_task(task)

            intention = Intention(
                plan_id=f'route_{task_id}',
                steps=['analyze_task', 'find_specialist', 'delegate_task', 'track_result'],
                target_desire='route_discrete_task',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'routing_decision': routing_decision
                }
            )

            new_intentions.append(intention)
            print(f"[{self.agent_id}] Created routing plan for {task_id} -> {routing_decision['target']}")

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute one step of the routing plan."""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')
        routing = intention.metadata.get('routing_decision', {})

        print(f"[{self.agent_id}] Executing step: {action} for task {task_id}")

        try:
            if action == 'analyze_task':
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
        service_type = routing.get('service_type', 'math.discrete.combinatorics')
        specialists = self._find_specialists(service_type)

        if specialists:
            intention.metadata['specialist'] = specialists[0]
            print(f"[{self.agent_id}] Found specialist: {specialists[0].agent_id}")
            intention.advance()
        else:
            if service_type != 'math.discrete.combinatorics':
                print(f"[{self.agent_id}] No {service_type} specialist, trying combinatorics")
                fallback = self._find_specialists('math.discrete.combinatorics')
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

        delegation_id = f'delegation_{uuid.uuid4().hex[:8]}'

        delegated_metadata = dict(task.metadata) if hasattr(task, 'metadata') else {}
        delegated_metadata.update({
            'delegated_by': self.agent_id,
            'delegation_id': delegation_id,
            'assigned_agent': specialist.agent_id,
            'routing_reason': routing.get('reason', ''),
            'original_task_id': task_id
        })

        specialist_tag = routing.get('service_type', 'combinatorics').split('.')[-1]

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

        self.add_belief(f'routed_{task_id}', True)

        self.add_belief(f'delegated_{task_id}', {
            'delegation_id': delegation_id,
            'specialist': specialist.agent_id,
            'delegated_entry_id': delegated_entry.entry_id
        })

        self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)

        self.remove_belief(f'pending_discrete_{task_id}')

        self.tasks_routed += 1
        print(f"[{self.agent_id}] Delegated task {task_id} to {specialist.agent_id} (delegation: {delegation_id})")

        intention.advance()

    def _execute_track_result(self, intention: Intention, task_id: str):
        """Track result - handled asynchronously by update_beliefs."""
        print(f"[{self.agent_id}] Routing complete for task {task_id}, awaiting specialist result")
        intention.advance()

    def _handle_routing_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle routing failure"""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
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

        if task_id:
            self.remove_belief(f'pending_discrete_{task_id}')

        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Get supervisor statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'combinatorics_routes': self.combinatorics_routes,
            'graph_theory_routes': self.graph_theory_routes,
            'set_theory_routes': self.set_theory_routes,
            'recurrence_routes': self.recurrence_routes,
            'boolean_algebra_routes': self.boolean_algebra_routes,
            'automata_routes': self.automata_routes
        })
        return stats


if __name__ == "__main__":
    """Test Discrete Math Supervisor"""
    print("=" * 80)
    print("DISCRETE MATH SUPERVISOR TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.system import Phase0System

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Discrete Math Supervisor
    supervisor = DiscreteMathSupervisor(
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
        ("Find the shortest path between A and B", "Graph"),
        ("How many permutations of 5 elements?", "Combinatorics"),
        ("Is this graph connected?", "Graph"),
        ("Calculate 10 choose 3", "Combinatorics"),
        ("Find a spanning tree", "Graph"),
        ("Count the number of ways to arrange", "Combinatorics"),
        ("Traverse the graph using DFS", "Graph"),
        ("What is 7 factorial?", "Combinatorics"),
    ]

    for test, expected in test_cases:
        decision = supervisor._analyze_task(MockEntry(test))
        status = 'OK' if expected in decision['target'] else 'MISMATCH'
        print(f"  [{status}] \"{test[:35]}...\" -> {decision['target']}")

    print()
    print("Statistics:")
    import json
    print(json.dumps(supervisor.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
