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
PHASE 2 - STEP 2.1: CALCULUS SUPERVISOR (Tier 2)
================================================

The Calculus Supervisor acts as the primary gatekeeper for calculus tasks,
possessing the crucial decision logic to route problems to the correct engine.

CRITICAL FUNCTION:
-----------------
Must distinguish between requests for exact solutions (symbolic) and
approximate solutions (numerical) to prevent wasted computation on
non-integrable functions.

ROUTING LOGIC:
-------------
- "Find the exact integral" → Integration Specialist (Symbolic Engine)
- "Approximate the area" → Integration Specialist (Numerical Engine)
- "Derivative" / "gradient" → Differentiation Specialist
- "Differential equation" / "ODE" / "PDE" → Differential Equation Solver
- "Series" / "Taylor" / "Fourier" → Series Specialist

WHY THIS MATTERS:
----------------
This is the most complex domain in Phase 2. Many functions are NOT
analytically integrable (no closed-form antiderivative exists). Sending
these to symbolic engines wastes resources. The supervisor's intelligence
prevents this failure mode.

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 96-99 (Agent 2.1)
- Phase 2 Coding Strategy: Section 3.2 "The Analysis Layer"
"""

import sys
import os
from typing import List, Dict, Any, Optional
import uuid

# Add paths for imports
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)


class CalculusSupervisor(BDIAgent):
    """
    Calculus Supervisor - Tier 2 Strategic Router with Critical Decision Logic

    ROLE:
    ----
    Acts as gatekeeper for calculus tasks with emphasis on the critical
    distinction between symbolic (exact) and numerical (approximate) methods.

    CRITICAL DECISION:
    -----------------
    The most important routing decision is determining whether to use:
    - Symbolic Engine (Risch algorithm) for exact closed-form results
    - Numerical Engine (Quadrature) for approximate numerical results

    This decision prevents wasted resources on non-integrable functions.

    ROUTING STRATEGY:
    ----------------
    Keyword-based routing (Phase 2 simplified):
    - "exact", "closed form", "antiderivative" → Symbolic
    - "approximate", "numerical", "area", "estimate" → Numerical
    - "derivative", "gradient" → Differentiation
    - "ODE", "PDE", "differential equation" → Differential Equation Solver
    - "series", "Taylor", "Fourier" → Series Specialist

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 96-99
    """

    def __init__(
        self,
        agent_id: str = 'calculus_supervisor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Calculus Supervisor

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
        self.symbolic_routes = 0
        self.numerical_routes = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Calculus Supervisor initialized")
        print(f"  Role: Strategic router with symbolic/numerical decision logic")
        print(f"  Critical Function: Prevent resource waste on non-integrable functions")
        print(f"  Mode: Analysis and delegation only - NEVER computes")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Line 99
        "DF REGISTRATION: service: math.calculus"
        """
        registration = create_service_registration(
            service_type='math.calculus',
            agent_id=self.agent_id,
            algorithm='routing',
            cost='low',
            instance=self,  # Register instance for direct invocation
            type='supervisor',
            domain='calculus',
            tier='2',
            decision_logic='symbolic_vs_numerical'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.calculus (supervisor with decision logic)")

    def process(self, task_entry: Any) -> Any:
        """
        Process calculus task by routing to appropriate specialist

        Args:
            task_entry: Blackboard entry containing task

        Returns:
            Result from specialist (via Blackboard)
        """
        print(f"\n[{self.agent_id}] Processing calculus task")

        # Extract task metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()

        print(f"  Task: {raw_input}")

        # Analyze task to determine routing
        routing_decision = self._analyze_task(task_entry)

        print(f"  Routing decision: {routing_decision['target']}")
        print(f"  Engine: {routing_decision.get('engine', 'N/A')}")
        print(f"  Reasoning: {routing_decision['reason']}")

        # Track routing statistics
        if routing_decision.get('engine') == 'symbolic':
            self.symbolic_routes += 1
        elif routing_decision.get('engine') == 'numerical':
            self.numerical_routes += 1

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

        This implements the critical decision logic for symbolic vs numerical
        methods. This is the MOST IMPORTANT function of this supervisor.

        Args:
            task_entry: Task to analyze

        Returns:
            Routing decision with target service type and reasoning
        """
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        raw_input = metadata.get('raw_input', '').lower()
        operation = metadata.get('operation', 'compute')

        # Priority 1: Differential Equations - Specific ODE types
        if any(kw in raw_input for kw in ['ode', 'pde', 'differential equation', 'dy/dx', "d'", 'boundary', 'dsolve']):
            # Sub-route to specific ODE specialist based on type
            ode_type = self._classify_ode_type(raw_input)

            if ode_type == 'separable':
                return {
                    'target': 'Separable ODE Specialist',
                    'service_type': 'math.calculus.ode.separable',
                    'reason': 'Detected separable ODE pattern'
                }
            elif ode_type == 'linear_nonhomogeneous':
                return {
                    'target': 'Linear Nonhomogeneous ODE Specialist',
                    'service_type': 'math.calculus.ode.linear_nonhomogeneous',
                    'reason': 'Detected linear first-order ODE pattern'
                }
            elif ode_type == 'bernoulli':
                return {
                    'target': 'Bernoulli ODE Specialist',
                    'service_type': 'math.calculus.ode.bernoulli',
                    'reason': 'Detected Bernoulli ODE pattern'
                }
            elif ode_type == 'exact':
                return {
                    'target': 'Exact ODE Specialist',
                    'service_type': 'math.calculus.ode.exact',
                    'reason': 'Detected exact ODE pattern'
                }
            elif ode_type == 'riccati':
                return {
                    'target': 'Riccati ODE Specialist',
                    'service_type': 'math.calculus.ode.riccati',
                    'reason': 'Detected Riccati ODE pattern'
                }
            else:
                # Fallback to general ODE specialist
                return {
                    'target': 'Differential Equation Solver',
                    'service_type': 'math.calculus.ode',
                    'reason': 'General differential equation (no specific pattern detected)'
                }

        # Priority 2: Series Expansion
        if any(kw in raw_input for kw in ['series', 'taylor', 'fourier', 'expansion', 'convergence']):
            return {
                'target': 'Series Specialist',
                'service_type': 'math.calculus.series',
                'reason': 'Detected series expansion keywords'
            }

        # Priority 2.5: Summation (infinite series)
        if any(kw in raw_input for kw in ['summation', 'sum(', 'sum_', '\\sum']):
            return {
                'target': 'Series Specialist',
                'service_type': 'math.calculus.series',
                'reason': 'Detected summation keywords'
            }

        # Priority 2.6: Limits - route to limit specialist or native limit
        if any(kw in raw_input for kw in ['limit', 'lim_', 'lim{', 'lim ', '->']) or operation == 'limit':
            return {
                'target': 'Limit Specialist',
                'service_type': 'math.calculus.limit',
                'reason': 'Detected limit keywords'
            }

        # Priority 3: Differentiation
        if any(kw in raw_input for kw in ['derivative', 'differentiate', 'gradient', 'jacobian', 'hessian', "d/dx"]):
            return {
                'target': 'Differentiation Specialist',
                'service_type': 'math.calculus.diff',
                'reason': 'Detected differentiation keywords'
            }

        # Priority 4: Integration - THE CRITICAL SPLIT
        if any(kw in raw_input for kw in ['integrate', 'integral', 'antiderivative', 'area', 'accumulation']):
            # Check for advanced integration patterns requiring specialized handling
            complexity = self._assess_integration_complexity(raw_input, metadata)

            if complexity == 'advanced':
                return {
                    'target': 'Advanced Integration Specialist',
                    'service_type': 'math.calculus.integration.advanced',
                    'reason': 'Detected complex pattern requiring advanced techniques (exp×trig, tabular, or substitution)'
                }

            # CRITICAL DECISION: Symbolic or Numerical?

            # Symbolic indicators
            if any(kw in raw_input for kw in ['exact', 'closed form', 'antiderivative', 'find the integral']):
                return {
                    'target': 'Integration Specialist',
                    'service_type': 'math.calculus.integration',
                    'engine': 'symbolic',
                    'reason': 'Exact/symbolic integration requested'
                }

            # Numerical indicators
            if any(kw in raw_input for kw in ['approximate', 'numerical', 'area', 'estimate', 'compute']):
                return {
                    'target': 'Integration Specialist',
                    'service_type': 'math.calculus.integration',
                    'engine': 'numerical',
                    'reason': 'Approximate/numerical integration requested'
                }

            # Default for integration: Try symbolic first
            return {
                'target': 'Integration Specialist',
                'service_type': 'math.calculus.integration',
                'engine': 'symbolic',
                'reason': 'Default to symbolic integration (will fallback to numerical if needed)'
            }

        # Default: Route to differentiation (most common calculus operation)
        return {
            'target': 'Differentiation Specialist',
            'service_type': 'math.calculus.diff',
            'reason': 'Default routing for general calculus computation'
        }

    def _assess_integration_complexity(self, raw_input: str, metadata: Dict) -> str:
        """
        Assess integration complexity to route to specialized handlers.

        Detects patterns requiring advanced integration techniques:
        - advanced: Complex patterns requiring AdvancedIntegrationSpecialist coordinator
        - basic: Standard patterns handled by basic IntegrationSpecialist

        Advanced patterns include:
        - exp(ax) × [sin|cos](bx) products
        - High-degree polynomial × transcendental (tabular)
        - Chain rule patterns (substitution)
        - Trig powers

        Args:
            raw_input: Raw input string
            metadata: Task metadata

        Returns:
            Complexity level: 'advanced' or 'basic'
        """
        import re

        # Get expression from metadata if available
        expression = metadata.get('expression', raw_input)
        expr_lower = expression.lower()

        # Pattern 1: exp×trig products
        exp_trig_pattern = r'exp\([^)]+\)\s*\*\s*(sin|cos)\([^)]+\)'
        if re.search(exp_trig_pattern, expression):
            return 'advanced'

        # Alternative exp×trig check
        if 'exp' in expr_lower and ('sin' in expr_lower or 'cos' in expr_lower):
            if '*' in expression or '·' in expression:
                return 'advanced'

        # Pattern 2: High-degree polynomial × transcendental
        high_poly_pattern = r'x\s*\*\*\s*[3-9]|x\^[3-9]'
        if re.search(high_poly_pattern, expression):
            if any(func in expr_lower for func in ['exp', 'sin', 'cos', 'ln', 'log']):
                return 'advanced'

        # Pattern 3: Nested functions (chain rule indicators)
        if '(' in expression and ')' in expression:
            # Look for function composition
            if any(f in expr_lower for f in ['sin(', 'cos(', 'exp(', 'ln(', 'log(']):
                # Count nesting depth
                if expression.count('(') >= 2:  # Nested function
                    return 'advanced'

        # Pattern 4: Trig powers (might be complex)
        trig_power_pattern = r'(sin|cos)\([^)]+\)\s*\*\*\s*[4-9]'
        if re.search(trig_power_pattern, expr_lower):
            return 'advanced'

        return 'basic'

    def _classify_ode_type(self, raw_input: str) -> str:
        """
        Classify ODE type to route to appropriate specialist.

        Detects:
            - separable: dy/dx = f(x)g(y)
            - linear_nonhomogeneous: y' + P(x)y = Q(x)
            - bernoulli: y' + P(x)y = Q(x)y^n
            - exact: M(x,y)dx + N(x,y)dy = 0
            - riccati: y' = P(x) + Q(x)y + R(x)y^2

        Args:
            raw_input: Raw input string

        Returns:
            ODE type: 'separable', 'linear_nonhomogeneous', 'bernoulli', 'exact', 'riccati', or 'general'
        """
        # Keywords for specific ODE types
        if any(kw in raw_input for kw in ['separable', 'separate variables', 'separation of variables']):
            return 'separable'

        if any(kw in raw_input for kw in ['linear', 'integrating factor', 'first order linear']):
            # Check if nonhomogeneous
            if any(kw in raw_input for kw in ['nonhomogeneous', 'non-homogeneous', 'q(x)', '= q', '= x', '= sin', '= cos', '= exp']):
                return 'linear_nonhomogeneous'
            return 'linear_nonhomogeneous'  # Default to nonhomogeneous for linear

        if any(kw in raw_input for kw in ['bernoulli', 'y^n', 'y**n']):
            return 'bernoulli'

        if any(kw in raw_input for kw in ['exact', 'exactness', 'potential function', 'mdx', 'ndy']):
            return 'exact'

        if any(kw in raw_input for kw in ['riccati', 'y^2', 'y**2', 'particular solution']):
            return 'riccati'

        # Pattern-based detection (if no explicit keywords)
        # Look for variable coefficients or products
        if 'x*y' in raw_input.replace(' ', '') or 'y*x' in raw_input.replace(' ', ''):
            # Could be separable: dy/dx = x*y
            return 'separable'

        # Look for y' + ... y = ... pattern (linear)
        if ("y'" in raw_input or 'dy/dx' in raw_input) and '+' in raw_input and '=' in raw_input:
            # Check if y appears in multiple terms (suggests linear)
            y_count = raw_input.count('y')
            if y_count >= 2:  # y' and y term
                return 'linear_nonhomogeneous'

        # Default: general
        return 'general'

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
            'engine': routing_decision.get('engine', 'default')
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
    # The Calculus Supervisor's BDI loop is about ROUTING with CRITICAL DECISION:
    #   1. update_beliefs() - Find calculus tasks on Blackboard
    #   2. deliberate() - Decide which specialist + engine (symbolic vs numerical)
    #   3. execute_step() - Delegate to specialist, track results
    #
    # CRITICAL: Supervisors NEVER compute. They analyze, decide, and delegate.
    # The most important decision is symbolic vs numerical for integration.
    # ==========================================================================

    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for calculus tasks that need routing.

        The supervisor looks for:
        1. New calculus tasks that haven't been routed yet
        2. Completed delegated tasks (to aggregate results)
        3. Failed delegated tasks (to handle errors or retry with different engine)
        """
        if not self.blackboard:
            return

        try:
            # Find pending calculus tasks
            pending_tasks = self.blackboard.query_entries(
                tags=['calculus'],
                status=EntryStatus.PENDING
            )

            # Also find general tasks that might be calculus-related
            task_entries = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            # Filter to calculus-related tasks
            for task in task_entries:
                domain = ''
                if hasattr(task, 'metadata') and task.metadata:
                    domain = task.metadata.get('domain', '').lower()

                if domain in ['calculus', ''] and task not in pending_tasks:
                    # Check if it's actually a calculus task
                    raw_input = task.metadata.get('raw_input', '').lower() if task.metadata else ''
                    calculus_keywords = ['derivative', 'integral', 'integrate', 'differentiate',
                                        'limit', 'series', 'taylor', 'ode', 'differential']
                    if any(kw in raw_input for kw in calculus_keywords):
                        pending_tasks.append(task)

            # Add beliefs about unrouted tasks
            for task in pending_tasks:
                belief_key = f'pending_calculus_{task.entry_id}'

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
                        self.add_belief(f'result_{delegation_id}', results[0], source='specialist')
                        self.remove_belief(predicate)
                        self.tasks_completed += 1

                    # Check for failures - might need to retry with different engine
                    failures = self.blackboard.query_entries(
                        tags=[delegation_id],
                        status=EntryStatus.FAILED
                    )

                    if failures:
                        engine_used = delegation_info.get('engine', 'symbolic')
                        # If symbolic failed, mark for numerical retry
                        if engine_used == 'symbolic':
                            self.add_belief(f'retry_numerical_{delegation_id}', delegation_info, source='failure')
                        self.remove_belief(predicate)
                        self.tasks_failed += 1

        except Exception as e:
            print(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """
        DELIBERATE: Create routing plans for pending calculus tasks.

        For each pending task, the supervisor:
        1. Analyzes what kind of calculus problem it is
        2. Makes CRITICAL DECISION: symbolic vs numerical for integration
        3. Creates an intention to delegate

        Returns:
            List of new Intention objects for routing tasks
        """
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_calculus_'):
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
                target_desire='route_calculus_task',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'routing_decision': routing_decision
                }
            )

            new_intentions.append(intention)
            engine_info = f" (engine: {routing_decision.get('engine', 'N/A')})" if 'engine' in routing_decision else ""
            print(f"[{self.agent_id}] Created routing plan for {task_id} -> {routing_decision['target']}{engine_info}")

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Execute one step of the routing plan.

        Steps:
        1. analyze_task - Determine task type + engine (already done in deliberate)
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
                engine = routing.get('engine', 'default')
                print(f"[{self.agent_id}] Task analysis: {routing.get('reason', 'unknown')}")
                print(f"[{self.agent_id}] Engine: {engine}")
                if 'integration' in routing.get('service_type', ''):
                    if engine == 'symbolic':
                        self.symbolic_routes += 1
                    else:
                        self.numerical_routes += 1
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
        service_type = routing.get('service_type', 'math.calculus.diff')

        specialists = self._find_specialists(service_type)

        if specialists:
            intention.metadata['specialist'] = specialists[0]
            print(f"[{self.agent_id}] Found specialist: {specialists[0].agent_id}")
            intention.advance()
        else:
            # Try fallback to differentiation
            if service_type != 'math.calculus.diff':
                print(f"[{self.agent_id}] No {service_type} specialist, trying differentiation")
                fallback = self._find_specialists('math.calculus.diff')
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
            'engine': routing.get('engine', 'default'),
            'original_task_id': task_id
        })

        # Determine tags based on specialist type
        specialist_tag = routing.get('service_type', 'calculus').split('.')[-1]

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
            'engine': routing.get('engine', 'default'),
            'delegated_entry_id': delegated_entry.entry_id
        })

        # Update original task status
        self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)

        # Clean up pending belief
        self.remove_belief(f'pending_calculus_{task_id}')

        self.tasks_routed += 1
        print(f"[{self.agent_id}] Delegated task {task_id} to {specialist.agent_id} (delegation: {delegation_id})")

        intention.advance()

    def _execute_track_result(self, intention: Intention, task_id: str):
        """Track result - handled asynchronously by update_beliefs"""
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
            self.remove_belief(f'pending_calculus_{task_id}')

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
            'symbolic_routes': self.symbolic_routes,
            'numerical_routes': self.numerical_routes
        })
        return stats


if __name__ == "__main__":
    """Test Calculus Supervisor"""
    print("=" * 80)
    print("PHASE 2 - CALCULUS SUPERVISOR TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.system import Phase0System

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Calculus Supervisor
    supervisor = CalculusSupervisor(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    print("=" * 80)
    print("CALCULUS SUPERVISOR INITIALIZED")
    print("=" * 80)
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.calculus')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")
        print(f"    Decision Logic: {service.properties.get('decision_logic')}")

    print()
    print("Statistics:")
    import json
    print(json.dumps(supervisor.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
