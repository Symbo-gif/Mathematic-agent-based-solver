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
PHASE 0 - STEP 5: The Cognitive Blueprint (BDI Framework)
=========================================================

Belief-Desire-Intention (BDI) Control Loop Template

PURPOSE:
-------
Defines the internal "operating system" that all future cognitive agents will
inherit, establishing a consistent and predictable model of rational behavior
based on the Belief-Desire-Intention (BDI) architecture.

REFERENCE:
---------
- Phase_0_Build_Order_Breakdown.md: Step 5 (Lines 424-505)
- Phase 0 Coding Strategy: Section 6.0 "The Cognitive Blueprint: The BDI Control Loop for Future Citizens"

ARCHITECTURE:
------------
The BDI architecture provides a structured process for decision-making that
critically separates deliberation (choosing a plan) from execution (carrying out the plan).

THREE BDI COMPONENTS:
--------------------
1. Beliefs (B): Agent's knowledge and understanding of the world
   - Internal model of reality
   - Example: "The value of x is 5", "This is a polynomial equation"

2. Desires (D): Agent's ultimate high-level goals
   - Objectives the agent wishes to achieve
   - Example: "I want to solve this integral", "I need to factor this polynomial"

3. Intentions (I): Agent's committed plan of action
   - Specific course chosen after deliberation
   - Example: "I will apply the Risch Algorithm", "I will use substitution u = sin(x)"

WHY THIS MATTERS:
----------------
The cognitive agents cannot be simple reactive scripts. They must be deliberative
entities capable of reasoning and planning. The BDI framework ensures:
  - Rational decision-making process
  - Separation of "what to do" from "how to do it"
  - Consistent behavior across all cognitive agents
  - Ability to reason about goals and plans

BDI CONTROL LOOP:
----------------
1. PERCEIVE: Update beliefs from environment (Blackboard, messages)
2. DELIBERATE: Compare beliefs against desires to generate new intentions
3. MEANS-END: Select concrete plans to achieve intentions
4. EXECUTE: Execute one step of current intention
5. Repeat

IMPORTANT: Cognitive agents NEVER compute directly. They delegate computation
to specialized tools (SymPy, numerical libraries) and reason about the results.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime
import logging

from symbo_agentic_reasoners.utils.logging import get_component_logger

# Setup logging for this module
logger = logging.getLogger('symbo_agentic_reasoners.bdi_agent')


@dataclass
class Belief:
    """
    Agent's knowledge about the world

    Represents a single piece of knowledge the agent holds. Beliefs have
    confidence levels and sources, allowing agents to reason about uncertainty.

    FIELDS:
    ------
    - predicate: The belief statement (e.g., 'problem_type', 'variable_value', 'theorem_applicable')
    - content: The believed fact (OMDoc object or value)
    - confidence: Certainty level [0, 1] where 1.0 = completely certain
    - source: How belief was acquired ('observation', 'inference', 'communication', 'axiom')
    - timestamp: When belief was created/updated

    EXAMPLES:
    --------
    Belief(predicate='problem_type', content='polynomial_equation', confidence=1.0, source='observation')
    Belief(predicate='variable_value', content='x=5', confidence=0.8, source='inference')
    Belief(predicate='integration_method', content='substitution', confidence=0.6, source='inference')

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 446-451
    """
    predicate: str              # e.g., 'problem_type', 'variable_value', 'theorem_applicable'
    content: Any                # The believed fact (OMDoc object)
    confidence: float = 1.0     # Certainty level [0, 1]
    source: str = 'observation' # 'observation', 'inference', 'communication', 'axiom'
    timestamp: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        """Human-readable representation"""
        content_str = str(self.content)[:50] + "..." if len(str(self.content)) > 50 else str(self.content)
        return f"Belief[{self.predicate}]({content_str}, conf={self.confidence:.2f}, from={self.source})"


@dataclass
class Desire:
    """
    Agent's goals

    Represents a high-level objective the agent wishes to achieve. Desires
    have priorities and success conditions.

    FIELDS:
    ------
    - goal: Goal description (e.g., 'solve_integral', 'verify_proof', 'factorize_polynomial')
    - priority: Priority level 1-10 (10 = highest priority)
    - success_condition: OMDoc condition for goal satisfaction
    - active: Whether this desire is currently being pursued
    - created_at: When desire was created
    - deadline: Optional deadline for achieving goal

    EXAMPLES:
    --------
    Desire(goal='solve_integral', priority=9, success_condition=integral_result)
    Desire(goal='verify_proof', priority=7, success_condition=proof_valid)
    Desire(goal='find_counterexample', priority=5, success_condition=counterexample_found)

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 453-458
    """
    goal: str                   # Goal description
    success_condition: Any = None      # OMDoc condition for goal satisfaction
    priority: int = 5           # Priority level 1-10
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None

    def __repr__(self) -> str:
        """Human-readable representation"""
        status = "active" if self.active else "inactive"
        return f"Desire[{self.goal}](priority={self.priority}, {status})"


@dataclass
class Intention:
    """
    Agent's committed plan

    Represents a specific plan of action the agent has committed to after
    deliberation. Intentions have concrete steps and track progress.

    FIELDS:
    ------
    - plan_id: Unique plan identifier
    - steps: Ordered list of action descriptions
    - current_step: Index of current step being executed
    - target_desire: Which desire this intention serves
    - committed: Whether agent is committed to this plan
    - created_at: When intention was created
    - metadata: Additional planning metadata

    EXAMPLES:
    --------
    Intention(plan_id='plan_risch_integration',
              steps=['identify_integrand_type', 'apply_risch_algorithm', 'verify_result'],
              target_desire='solve_integral')

    Intention(plan_id='plan_polynomial_factorization',
              steps=['check_degree', 'find_rational_roots', 'apply_factorization'],
              target_desire='factorize_polynomial')

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 460-467
    """
    plan_id: str
    steps: List[str]            # Ordered list of actions
    target_desire: str          # Which desire this serves
    current_step: int = 0
    committed: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_complete(self) -> bool:
        """Check if all steps have been executed"""
        return self.current_step >= len(self.steps)

    def get_current_action(self) -> Optional[str]:
        """Get current action to execute"""
        if self.is_complete():
            return None
        return self.steps[self.current_step]

    def advance(self):
        """Move to next step"""
        if not self.is_complete():
            self.current_step += 1

    def __repr__(self) -> str:
        """Human-readable representation"""
        progress = f"{self.current_step}/{len(self.steps)}"
        status = "complete" if self.is_complete() else "in_progress"
        return f"Intention[{self.plan_id}]({progress} steps, {status}, goal={self.target_desire})"


class BDIAgent(ABC):
    """
    Abstract base class for all cognitive agents

    Implements the BDI (Belief-Desire-Intention) control loop that defines
    how cognitive agents reason and act. All Phase 1+ cognitive agents
    (Orchestrator, Specialists, etc.) inherit from this class.

    THE BDI CONTROL LOOP:
    --------------------
    while True:
        1. PERCEIVE: update_beliefs() - Read Blackboard, process messages
        2. DELIBERATE: deliberate() - Compare beliefs to desires
        3. MEANS-END: Generate intentions (plans) to achieve desires
        4. EXECUTE: execute_step() - Execute one step of current intention

    CRITICAL PRINCIPLE:
    ------------------
    BDI agents NEVER compute directly. They:
      - Reason about problems (deliberation)
      - Generate plans (means-end reasoning)
      - Delegate computation to tools or specialist agents (execution)
      - Verify and interpret results (belief update)

    Example: An Integration Agent does NOT compute integrals itself.
    It reasons about integration strategies, delegates to SymPy,
    and interprets the results.

    SUBCLASS RESPONSIBILITIES:
    -------------------------
    Subclasses MUST implement:
      - update_beliefs(): How to perceive the environment
      - deliberate(): How to generate intentions from beliefs and desires
      - execute_step(): How to execute one action step

    Subclasses SHOULD override:
      - initialize(): Custom initialization
      - handle_message(): Process incoming FIPA-ACL messages
      - on_intention_complete(): React to completed intentions

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 469-505
    """

    def __init__(self, agent_id: str):
        """
        Initialize BDI Agent

        Args:
            agent_id: Unique agent identifier (e.g., 'algebra_specialist_001')
        """
        self.agent_id = agent_id
        self.beliefs: Dict[str, Belief] = {}
        self.desires: List[Desire] = []
        self.intentions: List[Intention] = []

        # State tracking
        self.running = False
        self.cycle_count = 0

        # Setup per-agent logger
        self._logger = get_component_logger(f'agents.{agent_id}')

        # Subclass can override this
        self.initialize()

    # ========================================================================
    # LOGGING HELPERS - Use these instead of print()
    # ========================================================================

    def _log_info(self, message: str, **kwargs):
        """Log info message with agent context"""
        extra = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
        full_msg = f"[{self.agent_id}] {message}"
        if extra:
            full_msg += f" | {extra}"
        self._logger.info(full_msg)

    def _log_debug(self, message: str, **kwargs):
        """Log debug message with agent context"""
        extra = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
        full_msg = f"[{self.agent_id}] {message}"
        if extra:
            full_msg += f" | {extra}"
        self._logger.debug(full_msg)

    def _log_warning(self, message: str, **kwargs):
        """Log warning message with agent context"""
        extra = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
        full_msg = f"[{self.agent_id}] {message}"
        if extra:
            full_msg += f" | {extra}"
        self._logger.warning(full_msg)

    def _log_error(self, message: str, exc: Optional[Exception] = None, **kwargs):
        """Log error message with agent context and optional exception"""
        extra = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
        full_msg = f"[{self.agent_id}] {message}"
        if extra:
            full_msg += f" | {extra}"
        self._logger.error(full_msg, exc_info=exc is not None)

    def initialize(self):
        """
        Subclass initialization hook

        Override this in subclasses to perform custom initialization.
        Called after base __init__ completes.
        """
        pass

    # ========================================================================
    # BDI CONTROL LOOP - Main reasoning cycle
    # ========================================================================

    def bdi_loop(self):
        """
        Main BDI control loop - runs continuously

        THE REASONING CYCLE:
        -------------------
        1. PERCEIVE: Update beliefs from environment
        2. DELIBERATE: Consider beliefs against desires, generate intentions
        3. EXECUTE: Execute one step of current intention
        4. Repeat

        This is the "heartbeat" of cognitive agents. Each cycle represents
        one reasoning step.

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 478-489
        """
        self.running = True

        while self.running:
            try:
                # STEP 1: PERCEIVE - Update beliefs from environment
                self.update_beliefs()

                # STEP 2: DELIBERATE - Generate new intentions
                new_intentions = self.deliberate()

                # STEP 3: MEANS-END - Adopt new intentions
                self.intentions.extend(new_intentions)

                # STEP 4: EXECUTE - Execute one step of highest priority intention
                if self.intentions:
                    current_intention = self.intentions[0]  # Highest priority
                    self.execute_step(current_intention)

                    # If intention complete, remove and notify
                    if current_intention.is_complete():
                        self.intentions.remove(current_intention)
                        self.on_intention_complete(current_intention)

                self.cycle_count += 1

            except Exception as e:
                logger.error(f"{self.agent_id} BDI loop error: {e}", exc_info=True)
                # Continue running despite errors

    def stop(self):
        """Stop the BDI control loop"""
        self.running = False

    # ========================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # ========================================================================

    @abstractmethod
    def update_beliefs(self):
        """
        Update beliefs from environment

        Subclasses implement this to:
          - Read messages from ACC
          - Query Blackboard for relevant entries
          - Update internal belief state

        EXAMPLE (Integration Specialist):
        ---------------------------------
        def update_beliefs(self):
            # Check for new integration requests on Blackboard
            tasks = blackboard.query_entries(tags=['integration'], status=PENDING)
            for task in tasks:
                self.add_belief('pending_task', task.content)

            # Check for messages from Orchestrator
            messages = acc.get_queued_messages(self.agent_id)
            for msg in messages:
                if msg.performative == REQUEST:
                    self.add_belief('integration_request', msg.content)

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 492-494
        """
        pass

    @abstractmethod
    def deliberate(self) -> List[Intention]:
        """
        Compare beliefs to desires, generate new intentions

        Subclasses implement this to:
          - Examine current beliefs
          - Compare to active desires
          - Generate plans (intentions) to achieve desires

        RETURNS:
        -------
        List of new Intention objects to adopt

        EXAMPLE (Integration Specialist):
        ---------------------------------
        def deliberate(self) -> List[Intention]:
            new_intentions = []

            # If we have an integration request belief and a solve_integral desire
            if self.has_belief('integration_request') and self.has_desire('solve_integral'):
                # Generate plan: analyze integrand, select method, execute
                plan = Intention(
                    plan_id='integrate_' + uuid.uuid4().hex[:8],
                    steps=['analyze_integrand', 'select_method', 'execute_integration', 'verify'],
                    target_desire='solve_integral'
                )
                new_intentions.append(plan)

            return new_intentions

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 496-499
        """
        pass

    @abstractmethod
    def execute_step(self, intention: Intention):
        """
        Execute next step in plan - NEVER compute, always delegate

        Subclasses implement this to:
          - Get current action from intention
          - Delegate computation to tools or other agents
          - Post results to Blackboard or send messages
          - Advance intention to next step

        CRITICAL: Agents NEVER compute directly. They delegate to:
          - SymPy for symbolic math
          - NumPy for numerical computation
          - Other specialist agents via FIPA-ACL messages

        EXAMPLE (Integration Specialist):
        ---------------------------------
        def execute_step(self, intention: Intention):
            action = intention.get_current_action()

            if action == 'analyze_integrand':
                # Delegate to SymPy to parse integrand
                integrand = self.get_belief('integration_request').content
                sympy_result = sympy.parse_expr(integrand)
                self.add_belief('parsed_integrand', sympy_result)
                intention.advance()

            elif action == 'select_method':
                # Reason about which integration method to use
                integrand_type = self.infer_integrand_type()
                method = self.select_integration_method(integrand_type)
                self.add_belief('integration_method', method)
                intention.advance()

            elif action == 'execute_integration':
                # Delegate to SymPy to compute integral
                method = self.get_belief('integration_method')
                integrand = self.get_belief('parsed_integrand')
                result = sympy.integrate(integrand, method=method)
                self.add_belief('integration_result', result)
                intention.advance()

            elif action == 'verify':
                # Verify result by differentiation
                result = self.get_belief('integration_result')
                derivative = sympy.diff(result)
                # Post result to Blackboard
                blackboard.post(create_entry('result', derivative, self.agent_id))
                intention.advance()

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 501-505
        """
        pass

    # ========================================================================
    # BELIEF MANAGEMENT
    # ========================================================================

    def add_belief(self, predicate: str, content: Any,
                  confidence: float = 1.0, source: str = 'observation') -> Belief:
        """
        Add or update belief

        Args:
            predicate: Belief predicate
            content: Belief content
            confidence: Confidence level [0, 1]
            source: Source of belief

        Returns:
            The created/updated Belief
        """
        belief = Belief(
            predicate=predicate,
            content=content,
            confidence=confidence,
            source=source
        )
        self.beliefs[predicate] = belief
        return belief

    def get_belief(self, predicate: str) -> Optional[Belief]:
        """Get belief by predicate"""
        return self.beliefs.get(predicate)

    def has_belief(self, predicate: str) -> bool:
        """Check if agent has belief"""
        return predicate in self.beliefs

    def remove_belief(self, predicate: str) -> bool:
        """Remove belief"""
        if predicate in self.beliefs:
            del self.beliefs[predicate]
            return True
        return False

    # ========================================================================
    # DESIRE MANAGEMENT
    # ========================================================================

    def add_desire(self, goal: str, priority: int = 5,
                  success_condition: Any = None) -> Desire:
        """
        Add desire (goal)

        Args:
            goal: Goal description
            priority: Priority 1-10
            success_condition: Condition for goal satisfaction

        Returns:
            The created Desire
        """
        desire = Desire(
            goal=goal,
            priority=priority,
            success_condition=success_condition
        )
        self.desires.append(desire)
        # Sort by priority (highest first)
        self.desires.sort(key=lambda d: d.priority, reverse=True)
        return desire

    def has_desire(self, goal: str) -> bool:
        """Check if agent has desire"""
        return any(d.goal == goal and d.active for d in self.desires)

    def remove_desire(self, goal: str) -> bool:
        """Remove desire"""
        before_len = len(self.desires)
        self.desires = [d for d in self.desires if d.goal != goal]
        return len(self.desires) < before_len

    def get_active_desires(self) -> List[Desire]:
        """Get all active desires"""
        return [d for d in self.desires if d.active]

    # ========================================================================
    # INTENTION MANAGEMENT
    # ========================================================================

    def add_intention(self, plan_id: str, steps: List[str],
                     target_desire: str, metadata: Dict[str, Any] = None) -> Intention:
        """
        Add intention (plan)

        Args:
            plan_id: Plan identifier
            steps: List of action steps
            target_desire: Goal this plan serves
            metadata: Additional metadata

        Returns:
            The created Intention
        """
        intention = Intention(
            plan_id=plan_id,
            steps=steps,
            target_desire=target_desire,
            metadata=metadata or {}
        )
        self.intentions.append(intention)
        return intention

    def get_current_intention(self) -> Optional[Intention]:
        """Get current (highest priority) intention"""
        if self.intentions:
            return self.intentions[0]
        return None

    # ========================================================================
    # HOOKS FOR SUBCLASSES
    # ========================================================================

    def on_intention_complete(self, intention: Intention):
        """
        Hook called when an intention completes

        Subclasses can override to react to completed plans.

        Args:
            intention: The completed intention
        """
        pass

    def handle_message(self, message):
        """
        Hook for handling FIPA-ACL messages

        Subclasses can override to process incoming messages.

        Args:
            message: FIPAMessage to process
        """
        pass

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'agent_id': self.agent_id,
            'beliefs': len(self.beliefs),
            'desires': len(self.desires),
            'active_desires': len(self.get_active_desires()),
            'intentions': len(self.intentions),
            'cycles': self.cycle_count,
            'running': self.running
        }

    def __repr__(self) -> str:
        """Human-readable representation"""
        return (f"BDIAgent[{self.agent_id}](beliefs={len(self.beliefs)}, "
                f"desires={len(self.desires)}, intentions={len(self.intentions)})")


if __name__ == "__main__":
    """Demonstration of BDI Framework"""
    print("=" * 80)
    print("PHASE 0 - STEP 5: BDI Cognitive Blueprint")
    print("=" * 80)
    print()

    # Example concrete BDI agent
    class ExampleMathAgent(BDIAgent):
        """Example concrete implementation of BDI agent"""

        def initialize(self):
            """Initialize with a goal"""
            self.add_desire('solve_problem', priority=9)
            print(f"{self.agent_id}: Initialized with desire to solve problems")

        def update_beliefs(self):
            """Simulate perception"""
            # In real implementation, would read from Blackboard/ACC
            if self.cycle_count == 0:
                self.add_belief('problem_received', 'x^2 + 2x + 1', source='observation')
                print(f"{self.agent_id}: Perceived problem x^2 + 2x + 1")

        def deliberate(self) -> List[Intention]:
            """Simulate deliberation"""
            new_intentions = []

            if self.has_belief('problem_received') and self.has_desire('solve_problem'):
                if not self.intentions:  # Don't create duplicate plans
                    plan = Intention(
                        plan_id='solve_polynomial',
                        steps=['parse_expression', 'identify_type', 'apply_method', 'verify'],
                        target_desire='solve_problem'
                    )
                    new_intentions.append(plan)
                    print(f"{self.agent_id}: Generated plan to solve polynomial")

            return new_intentions

        def execute_step(self, intention: Intention):
            """Simulate execution"""
            action = intention.get_current_action()
            print(f"{self.agent_id}: Executing step '{action}'")

            # Simulate delegation to tools
            if action == 'parse_expression':
                self.add_belief('parsed', 'Poly(x^2 + 2x + 1)', source='inference')
            elif action == 'identify_type':
                self.add_belief('problem_type', 'quadratic', source='inference')
            elif action == 'apply_method':
                self.add_belief('solution', 'x = -1 (double root)', source='inference')
            elif action == 'verify':
                print(f"{self.agent_id}: ✓ Solution verified")

            intention.advance()

        def on_intention_complete(self, intention: Intention):
            """React to completed plan"""
            print(f"{self.agent_id}: ✓ Plan '{intention.plan_id}' completed!")
            self.stop()  # Stop after one problem for demo

    # Create and run agent
    print("Example: Concrete BDI Agent Implementation")
    print()
    agent = ExampleMathAgent('example_math_agent_001')
    print(f"Created: {agent}")
    print()

    print("Running BDI loop for 5 cycles...")
    print()
    for i in range(5):
        if not agent.running:
            break
        # Manually execute one cycle (in production, would run in thread)
        agent.update_beliefs()
        new_intentions = agent.deliberate()
        agent.intentions.extend(new_intentions)
        if agent.intentions:
            current = agent.intentions[0]
            agent.execute_step(current)
            if current.is_complete():
                agent.intentions.remove(current)
                agent.on_intention_complete(current)
        agent.cycle_count += 1

    print()
    print("Final state:")
    import json
    stats = agent.get_statistics()
    print(json.dumps(stats, indent=2))
    print()

    print("✓ BDI Cognitive Blueprint implementation complete")
    print("  - Belief-Desire-Intention architecture ✓")
    print("  - Deliberation framework ✓")
    print("  - Separation of reasoning and execution ✓")
    print("  - Base template for all cognitive agents ✓")
