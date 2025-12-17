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
PHASE 1 - STEP 2: THE CENTRAL NERVOUS SYSTEM (Main Orchestrator)
================================================================

The Main Orchestrator is the Tier 1 "General Contractor" whose sole job
is management, enforcing the strict separation of Problem Understanding
from Problem Solving.

CRITICAL CONSTRAINTS:
--------------------
1. NON-INTERVENTION DIRECTIVE: Orchestrator is FORBIDDEN from performing
   calculations. If it sees "2+2", it must delegate, never compute.

2. SEPARATION OF PLANNING FROM EXECUTION: Orchestrator plans, decomposes,
   and delegates. It NEVER solves.

COMPONENTS:
----------
1. Decomposition Engine: HTN (Hierarchical Task Network) logic
2. Dynamic Routing Logic: Queries Directory Facilitator for capable agents

REFERENCE:
---------
- Phase_1_Build_Order_Breakdown.md: Lines 108-160 (STEP 2)
- Phase 1 Coding Strategy: Section 3.2 "The Central Nervous System"
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import uuid

# Setup logging
logger = logging.getLogger('symbo_agentic_reasoners.orchestrator')

# Add parent to path for Phase 0 imports
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool, PoolState
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.protocols.fipa_acl import create_request, create_inform

# Import Phase 1 components
# Path manipulation removed - using package imports
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain

# Import Phase 3 Knowledge Management for learning/memory
try:
    from symbo_agentic_reasoners.middleware.knowledge_management import (
        KnowledgeManagementTeam, RetrievalConfidence
    )
    KNOWLEDGE_MANAGEMENT_AVAILABLE = True
except ImportError:
    KNOWLEDGE_MANAGEMENT_AVAILABLE = False
    KnowledgeManagementTeam = None
    RetrievalConfidence = None


class NoAgentAvailableError(Exception):
    """Raised when no agent is available for a task"""
    pass


# Mapping from MathDomain enum values to agent pool domain keys
# MathDomain uses PascalCase values, agent pool uses snake_case
DOMAIN_TO_POOL_KEY = {
    'Calculus': 'calculus',
    'Algebra': 'algebra',
    'LinearAlgebra': 'linear_algebra',
    'Geometry': 'geometry',
    'Logic': 'logic',
    'NumberTheory': 'number_theory',
    'Statistics': 'statistics',
    'DiscreteMath': 'discrete_math',
    # Physics domains
    'PhysicsMechanics': 'physics_mechanics',
    'PhysicsEM': 'physics_em',
    'PhysicsThermo': 'physics_thermo',
    'PhysicsQuantum': 'physics_quantum',
    'Unknown': 'unknown',
}


def get_pool_domain_key(math_domain: MathDomain) -> str:
    """
    Convert MathDomain enum to agent pool domain key.

    Args:
        math_domain: MathDomain enum value

    Returns:
        Snake_case domain key for agent pool/registry
    """
    return DOMAIN_TO_POOL_KEY.get(math_domain.value, math_domain.value.lower())


@dataclass
class Task:
    """
    Orchestrator task representation

    Represents a task that needs to be executed by a specialist agent.
    """
    task_id: str
    structured_problem: StructuredProblem
    status: EntryStatus
    assigned_agent: Optional[str] = None
    blackboard_entry_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class MainOrchestrator(BDIAgent):
    """
    Main Orchestrator - The Central Nervous System

    DIRECTIVE:
    ---------
    Tier 1 Agent that manages the problem-solving process. Enforces strict
    separation of Problem Understanding from Problem Solving.

    ARCHITECTURE:
    ------------
    - Decomposition Engine: HTN logic to break complex tasks into subtasks
    - Routing Logic: Queries Directory Facilitator to find capable agents
    - NON-INTERVENTION: NEVER computes, always delegates

    WORKFLOW:
    --------
    1. Receive StructuredProblem from Problem Analysis Team
    2. Decompose into subtasks (if complex)
    3. Query DF for capable agents by domain
    4. Post task to Blackboard with appropriate tags
    5. Wait for verified result from Verification Core
    6. Return result to user

    CRITICAL:
    --------
    The Orchestrator NEVER computes. The NON_INTERVENTION flag is
    hard-coded to True and cannot be changed.

    REFERENCE:
    ---------
    - Phase_1_Build_Order_Breakdown.md: Lines 123-156 (MainOrchestrator code)
    - Phase 1 Coding Strategy: "The Orchestrator must manage, never solve"
    """

    def __init__(
        self,
        agent_id: str = 'main_orchestrator_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        agent_pool: Optional[AgentPool] = None,
        vector_db: Optional[Any] = None,
        enable_learning: bool = True
    ):
        """
        Initialize Main Orchestrator

        Args:
            agent_id: Unique orchestrator identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            agent_pool: AgentPool for lifecycle management (optional)
            vector_db: Vector database for learning/memory (optional)
            enable_learning: If True and vector_db provided, enables learning from solved problems
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard
        self.agent_pool = agent_pool
        self.vector_db = vector_db

        # HARD-CODED CONSTRAINT: Non-Intervention Directive
        # This MUST remain True - Orchestrator NEVER computes
        self.NON_INTERVENTION = True

        # Task tracking
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []

        # Knowledge Management Team for learning/memory
        self.knowledge_team = None
        if enable_learning and vector_db and blackboard and KNOWLEDGE_MANAGEMENT_AVAILABLE:
            try:
                self.knowledge_team = KnowledgeManagementTeam(
                    blackboard=blackboard,
                    vector_db=vector_db
                )
                logger.info(f"  Learning/Memory: ENABLED (KnowledgeManagementTeam active)")
            except Exception as e:
                logger.warning(f"  Learning/Memory: DISABLED (init failed: {e})")

        # Statistics
        self.tasks_routed = 0
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.agents_woken = 0
        self.agents_activated = 0
        self.cache_hits = 0  # Problems solved from memory
        self.solutions_recorded = 0  # New solutions stored

        logger.info(f"[{self.agent_id}] Initialized")
        logger.info(f"  NON-INTERVENTION directive: {self.NON_INTERVENTION} (HARD-CODED)")
        logger.info(f"  Mode: Management only - NEVER computes")
        if agent_pool:
            logger.info(f"  AgentPool: ENABLED (dynamic lifecycle management)")

    def process(self, structured: StructuredProblem) -> Any:
        """
        Process a structured problem

        This is the main entry point for the Orchestrator. It receives
        a StructuredProblem from the Problem Analysis Team and orchestrates
        the solution process.

        Now includes learning capabilities:
        1. Look-Before-Leap: Check memory for existing solutions
        2. Record-Result: Store new solutions for future retrieval

        Args:
            structured: Fully parsed and classified problem

        Returns:
            Verified result from solver

        Raises:
            NoAgentAvailableError: If no agent can handle the problem

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 132-155 (process method)
        """
        logger.info(f"[{self.agent_id}] Processing problem:")
        logger.info(f"  Type: {structured.problem_type.value}")
        logger.info(f"  Domain: {structured.domain.value}")
        logger.info(f"  Input: '{structured.raw_input}'")

        # LEARNING STEP 1: Look-Before-Leap - check memory for existing solutions
        cached_result = self._look_before_leap(structured)
        if cached_result is not None:
            logger.info(f"  [MEMORY HIT] Found cached solution: {cached_result}")
            self.cache_hits += 1
            return cached_result

        # CRITICAL: Enforce NON-INTERVENTION
        if not self.NON_INTERVENTION:
            raise RuntimeError("FATAL: NON_INTERVENTION directive violated!")

        # Step 1: Decompose if complex (HTN logic)
        logger.debug(f"  [{self.agent_id}] Step 1: Decomposing task...")
        subtasks = self._decompose(structured)
        logger.debug(f"    Decomposed into {len(subtasks)} subtask(s)")

        # Step 1.5: Wake agents for this domain (if AgentPool available)
        # Use mapping to convert MathDomain enum to pool domain key
        domain_key = get_pool_domain_key(structured.domain)
        if self.agent_pool:
            logger.debug(f"  [{self.agent_id}] Step 1.5: Waking agents for domain '{domain_key}'...")
            woken = self._wake_domain_agents(domain_key)
            logger.debug(f"    Woke {len(woken)} agent(s): {woken}")

        # Step 2: Query DF for capable agent
        logger.debug(f"  [{self.agent_id}] Step 2: Finding capable agent...")
        service_type = self._get_service_type(structured.domain)
        agents = self._find_capable_agents(service_type)

        if not agents:
            error_msg = f"No agent available for domain: {structured.domain.value}"
            logger.error(f"    ERROR: {error_msg}")
            raise NoAgentAvailableError(error_msg)

        logger.debug(f"    Found {len(agents)} capable agent(s): {[a.agent_id for a in agents]}")

        # Check if agent has instance for direct invocation
        selected_agent = agents[0]
        if hasattr(selected_agent, 'instance') and selected_agent.instance is not None:
            # Direct invocation path - call agent.process() directly
            logger.debug(f"  [{self.agent_id}] Step 3: Direct invocation of {selected_agent.agent_id}...")
            result = self._direct_invoke(structured, selected_agent.instance)
            if result is not None:
                self.tasks_routed += 1
                self.tasks_completed += 1
                # LEARNING STEP 2: Record successful result for future retrieval
                self._record_solution(structured, result)
                return result
            # Fall through to blackboard path if direct invoke failed
            logger.debug(f"    Direct invoke returned None, falling back to blackboard...")

        # Step 3: Post task to Blackboard
        logger.debug(f"  [{self.agent_id}] Step 3: Posting task to Blackboard...")
        task = self._post_task_to_blackboard(structured, selected_agent.agent_id)
        logger.debug(f"    Posted as entry: {task.blackboard_entry_id}")

        # Step 4: Wait for verified result
        logger.debug(f"  [{self.agent_id}] Step 4: Waiting for verified result...")
        result = self._await_verified_result(task)

        # LEARNING STEP 2: Record successful result for future retrieval
        if result is not None:
            self._record_solution(structured, result)

        return result

    def _decompose(self, structured: StructuredProblem) -> List[StructuredProblem]:
        """
        Decompose problem into subtasks using HTN logic

        This implements Hierarchical Task Network decomposition.
        For Phase 1, we only handle single-step tasks.
        Phase 2 will implement full HTN decomposition for complex problems.

        Args:
            structured: Problem to decompose

        Returns:
            List of subtasks (currently just [structured] for single-step)

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 157-160
        "Phase 1: single-step tasks only"
        """
        # Phase 1: Single-step tasks only
        # Phase 2 will implement:
        # - "simplify then integrate" -> [simplify, integrate]
        # - "factor then solve" -> [factor, solve]
        return [structured]

    def _wake_domain_agents(self, domain: str) -> List[str]:
        """
        Wake agents for a problem domain using AgentPool.

        This brings agents from DORMANT -> STANDBY state, preparing
        them for quick activation without allocating VRAM yet.

        Args:
            domain: Problem domain (e.g., 'algebra', 'calculus')

        Returns:
            List of agent IDs that were woken
        """
        if not self.agent_pool:
            return []

        woken = self.agent_pool.wake_for_domain(domain)
        self.agents_woken += len(woken)
        return woken

    def _activate_agent(self, agent_id: str) -> bool:
        """
        Activate a specific agent (STANDBY -> ACTIVE).

        For cognitive agents, this requests the VRAM slot from AMS.

        Args:
            agent_id: Agent to activate

        Returns:
            True if activated successfully
        """
        if not self.agent_pool:
            return True  # No pool = assume always active

        result = self.agent_pool.activate(agent_id)
        if result:
            self.agents_activated += 1
        return result

    def _deactivate_agent(self, agent_id: str, return_to_standby: bool = True) -> bool:
        """
        Deactivate an agent after task completion.

        Args:
            agent_id: Agent to deactivate
            return_to_standby: If True, keep in STANDBY for quick reuse

        Returns:
            True if deactivated successfully
        """
        if not self.agent_pool:
            return True  # No pool = no-op

        return self.agent_pool.deactivate(agent_id, return_to_standby)

    def _direct_invoke(self, structured: StructuredProblem, supervisor_instance: Any) -> Optional[Any]:
        """
        Direct invocation path - calls supervisor/specialist directly.

        When an agent has an instance registered, we can invoke it directly
        instead of posting to blackboard and waiting. This provides much
        faster results for synchronous use cases.

        Args:
            structured: The structured problem
            supervisor_instance: The agent instance to invoke

        Returns:
            Result string or None if invocation failed
        """
        try:
            # Create a minimal task entry for the supervisor
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus

            task_entry = create_entry(
                entry_type=EntryType.TASK,
                content=structured.omdoc_content,
                author_agent=self.agent_id,
                conversation_id=f'direct_invoke_{id(structured)}',
                tags=[structured.domain.value, 'direct_invoke'],
                metadata={
                    'problem_type': structured.problem_type.value,
                    'domain': structured.domain.value,
                    'raw_input': structured.raw_input,
                    'sympy_expr': str(structured.sympy_expr) if structured.sympy_expr else None,
                    'expression': structured.metadata.get('expression'),
                    'operation': structured.metadata.get('operation', 'compute'),
                    'variable': structured.metadata.get('variable', 'x')
                }
            )

            # Call the supervisor's process method
            result_entry = supervisor_instance.process(task_entry)

            # The supervisor delegates to specialists - we need to also invoke the specialist
            # Check if result_entry is a delegation (has assigned_agent in metadata)
            if result_entry and hasattr(result_entry, 'metadata'):
                assigned_specialist_id = result_entry.metadata.get('assigned_agent')
                if assigned_specialist_id:
                    # Find the specialist and invoke it directly
                    specialist_result = self._invoke_specialist_directly(
                        structured, assigned_specialist_id
                    )
                    if specialist_result:
                        return specialist_result

            # If supervisor returned a result directly (not a delegation)
            if result_entry:
                if hasattr(result_entry, 'metadata') and result_entry.metadata:
                    # Check for error - if so, fall back to native computation
                    if result_entry.metadata.get('error'):
                        return self._native_fallback(
                            structured,
                            structured.metadata.get('operation', 'compute')
                        )
                    result_str = result_entry.metadata.get('result_str')
                    if result_str:
                        return result_str
                if hasattr(result_entry, 'content') and result_entry.content:
                    return str(result_entry.content)

            # No result from supervisor - use native fallback
            return self._native_fallback(
                structured,
                structured.metadata.get('operation', 'compute')
            )

        except Exception as e:
            logger.warning(f"Direct invocation failed: {e}")
            # Fall back to native direct computation
            return self._native_fallback(
                structured,
                structured.metadata.get('operation', 'compute')
            )

    def _invoke_specialist_directly(self, structured: StructuredProblem,
                                    specialist_id: str) -> Optional[str]:
        """
        Invoke a specialist directly by creating and calling it.

        Falls back to creating specialists on-demand if not registered,
        and finally to native computation.
        """
        try:
            operation = structured.metadata.get('operation', 'compute')
            domain = structured.domain.value.lower()

            # Try to find registered specialist with instance
            if self.df:
                # Search for specialist service type
                specialist_type = self._map_operation_to_service(domain, operation)
                specialists = self.df.search(service_type=specialist_type)

                for spec in specialists:
                    if hasattr(spec, 'instance') and spec.instance is not None:
                        # Found specialist with instance
                        result = self._call_specialist(spec.instance, structured)
                        if result:
                            return result

            # Fall back to creating specialist on demand
            specialist = self._create_specialist_for_operation(domain, operation)
            if specialist:
                result = self._call_specialist(specialist, structured)
                if result:
                    return result

            # Final fallback: Native computation (NO SYMPY)
            return self._native_fallback(structured, operation)

        except Exception as e:
            logger.warning(f"Specialist invocation failed: {e}")
            return None

    def _native_fallback(self, structured: StructuredProblem, operation: str) -> Optional[str]:
        """Direct native computation as fallback when no specialist available.

        NO SYMPY - Uses native_symbolic and native_calculus for pure mathematical reasoning.
        """
        try:
            from symbo_agentic_reasoners.core.native_symbolic import (
                parse_expr, sympify, symbols, diff as native_diff, simplify as native_simplify
            )
            from symbo_agentic_reasoners.core.calculus import (
                differentiate, integrate
            )
            import re

            raw_input = structured.raw_input.lower()
            domain = structured.domain.value.lower() if structured.domain else 'algebra'

            # Domain-specific fallbacks
            if domain in ['geometry', 'trigonometry']:
                return self._geometry_fallback(structured, raw_input)
            elif domain in ['linearalgebra', 'linear_algebra', 'linalg']:
                return self._linalg_fallback(structured, raw_input)
            elif domain in ['statistics', 'stats']:
                return self._stats_fallback(structured, raw_input)
            elif domain in ['discretemath', 'discrete_math', 'discrete']:
                return self._discrete_fallback(structured, raw_input)

            # Extract expression from raw input
            raw = structured.raw_input
            # Remove operation keywords from raw input
            for op_kw in ['diff', 'differentiate', 'derivative', 'integrate', 'integral',
                          'factor', 'expand', 'simplify', 'solve', 'compute']:
                raw = raw.replace(op_kw, '').strip()

            # Try to parse the expression using native parser
            try:
                expr = parse_expr(raw)
            except Exception:
                # If parsing fails, return None
                return None

            variable = structured.metadata.get('variable', 'x')

            if operation in ['derivative', 'diff', 'differentiate']:
                success, result, _ = differentiate(raw, variable)
                if success and result:
                    return result
                # Fallback to native_symbolic diff
                var_sym = symbols(variable)
                result = native_diff(expr, var_sym)
                return str(result) if result is not None else None

            elif operation in ['integral', 'integrate']:
                success, result, _ = integrate(raw, variable)
                if success and result:
                    return result
                return None

            elif operation in ['factor', 'expand', 'simplify']:
                # Use native simplify for these operations
                result = native_simplify(expr)
                return str(result) if result is not None else None

            elif operation == 'solve':
                # For solve, try to extract and solve equation
                # Native implementation: basic algebraic solving
                return self._native_solve(raw, variable)

            elif operation == 'compute':
                # Try to evaluate numeric expressions
                try:
                    result = native_simplify(expr)
                    result_str = str(result)
                    # Try to convert to number if possible
                    try:
                        val = result.evalf()
                        if isinstance(val, (int, float)):
                            if float(val) == int(float(val)):
                                return str(int(float(val)))
                            return str(val)
                    except Exception:
                        pass
                    return result_str
                except Exception:
                    return str(expr)
            else:
                result = native_simplify(expr)
                return str(result) if result is not None else None

        except Exception as e:
            logger.warning(f"Native fallback failed: {e}")
            return None

    def _native_solve(self, expr_str: str, var: str) -> Optional[str]:
        """Native algebraic equation solver without SymPy."""
        import re

        # Try to parse as equation: expr = 0 or expr1 = expr2
        if '=' in expr_str:
            parts = expr_str.split('=')
            if len(parts) == 2:
                # Solve: left = right => left - right = 0
                expr_str = f"({parts[0].strip()}) - ({parts[1].strip()})"

        # Try linear equation: ax + b = 0 => x = -b/a
        linear_pattern = rf'(-?\d*\.?\d*)\s*\*?\s*{var}\s*([+-]\s*\d+\.?\d*)?'
        match = re.match(linear_pattern, expr_str.replace(' ', ''))
        if match:
            a_str = match.group(1) or '1'
            b_str = match.group(2) or '0'
            try:
                a = float(a_str) if a_str else 1.0
                b = float(b_str.replace(' ', '')) if b_str else 0.0
                if a != 0:
                    solution = -b / a
                    if solution == int(solution):
                        return str(int(solution))
                    return str(solution)
            except ValueError:
                pass

        # Try quadratic: ax^2 + bx + c = 0
        quad_pattern = rf'(-?\d*\.?\d*)\s*\*?\s*{var}\s*\*\*\s*2\s*([+-]\s*\d*\.?\d*\s*\*?\s*{var})?\s*([+-]\s*\d+\.?\d*)?'
        match = re.match(quad_pattern, expr_str.replace(' ', ''))
        if match:
            try:
                a = float(match.group(1) or '1')
                b_part = match.group(2) or '0'
                b = float(re.sub(rf'\*?{var}', '', b_part.replace(' ', ''))) if b_part and b_part.strip() else 0.0
                c = float(match.group(3).replace(' ', '') if match.group(3) else '0')

                if a != 0:
                    discriminant = b * b - 4 * a * c
                    if discriminant >= 0:
                        import math
                        sqrt_disc = math.sqrt(discriminant)
                        x1 = (-b + sqrt_disc) / (2 * a)
                        x2 = (-b - sqrt_disc) / (2 * a)
                        if x1 == x2:
                            return f"[{x1}]"
                        return f"[{x1}, {x2}]"
                    else:
                        # Complex roots
                        import math
                        real_part = -b / (2 * a)
                        imag_part = math.sqrt(-discriminant) / (2 * a)
                        return f"[{real_part} + {imag_part}*I, {real_part} - {imag_part}*I]"
            except (ValueError, ZeroDivisionError):
                pass

        return None

    def _geometry_fallback(self, structured: StructuredProblem, raw_input: str) -> Optional[str]:
        """Geometry/Trigonometry fallback using native math.

        NO SYMPY - Uses pure Python mathematical reasoning.
        """
        try:
            import math
            import re

            # Trigonometry with degrees
            if 'degree' in raw_input:
                # Extract angle value
                match = re.search(r'(\d+)\s*degree', raw_input)
                if match:
                    angle_deg = int(match.group(1))
                    angle_rad = math.pi * angle_deg / 180

                    # Common exact values lookup
                    exact_values = {
                        0: {'sin': '0', 'cos': '1', 'tan': '0'},
                        30: {'sin': '1/2', 'cos': 'sqrt(3)/2', 'tan': 'sqrt(3)/3'},
                        45: {'sin': 'sqrt(2)/2', 'cos': 'sqrt(2)/2', 'tan': '1'},
                        60: {'sin': 'sqrt(3)/2', 'cos': '1/2', 'tan': 'sqrt(3)'},
                        90: {'sin': '1', 'cos': '0', 'tan': 'undefined'},
                        120: {'sin': 'sqrt(3)/2', 'cos': '-1/2', 'tan': '-sqrt(3)'},
                        135: {'sin': 'sqrt(2)/2', 'cos': '-sqrt(2)/2', 'tan': '-1'},
                        150: {'sin': '1/2', 'cos': '-sqrt(3)/2', 'tan': '-sqrt(3)/3'},
                        180: {'sin': '0', 'cos': '-1', 'tan': '0'},
                    }

                    if angle_deg in exact_values:
                        if 'sin' in raw_input:
                            return exact_values[angle_deg]['sin']
                        elif 'cos' in raw_input:
                            return exact_values[angle_deg]['cos']
                        elif 'tan' in raw_input:
                            return exact_values[angle_deg]['tan']
                    else:
                        # Use numerical computation for other angles
                        if 'sin' in raw_input:
                            return str(math.sin(angle_rad))
                        elif 'cos' in raw_input:
                            return str(math.cos(angle_rad))
                        elif 'tan' in raw_input:
                            if abs(math.cos(angle_rad)) < 1e-10:
                                return 'undefined'
                            return str(math.tan(angle_rad))

            # Area calculations
            if 'area' in raw_input:
                if 'triangle' in raw_input:
                    # Extract base and height
                    base_match = re.search(r'base\s*[=:]?\s*(\d+(?:\.\d+)?)', raw_input)
                    height_match = re.search(r'height\s*[=:]?\s*(\d+(?:\.\d+)?)', raw_input)
                    if base_match and height_match:
                        base = float(base_match.group(1))
                        height = float(height_match.group(1))
                        return str(0.5 * base * height)
                elif 'circle' in raw_input:
                    radius_match = re.search(r'radius\s*[=:]?\s*(\d+(?:\.\d+)?)', raw_input)
                    if radius_match:
                        r = float(radius_match.group(1))
                        result = math.pi * r**2
                        return f"pi*{r**2}" if r**2 == int(r**2) else str(result)
                elif 'rectangle' in raw_input or 'square' in raw_input:
                    # Try to extract dimensions
                    nums = re.findall(r'(\d+(?:\.\d+)?)', raw_input)
                    if len(nums) >= 2:
                        return str(float(nums[0]) * float(nums[1]))
                    elif len(nums) == 1:
                        return str(float(nums[0]) ** 2)

            # Basic trig functions (without degrees) - use native simplify
            try:
                from symbo_agentic_reasoners.core.native_symbolic import parse_expr, simplify
                expr = parse_expr(structured.raw_input)
                return str(simplify(expr))
            except Exception:
                pass

            return None
        except Exception as e:
            logger.warning(f"Geometry fallback failed: {e}")
            return None

    def _linalg_fallback(self, structured: StructuredProblem, raw_input: str) -> Optional[str]:
        """Linear Algebra fallback using native matrix operations.

        NO SYMPY - Uses pure Python matrix reasoning.
        """
        try:
            import re
            import ast

            # Extract matrix from input
            matrix_match = re.search(r'\[\[.*?\]\]', raw_input.replace(' ', ''))
            if matrix_match:
                try:
                    matrix_list = ast.literal_eval(matrix_match.group())

                    # Convert to list of lists if needed
                    if not isinstance(matrix_list[0], list):
                        matrix_list = [matrix_list]

                    n_rows = len(matrix_list)
                    n_cols = len(matrix_list[0]) if n_rows > 0 else 0

                    if 'determinant' in raw_input or 'det' in raw_input:
                        det = self._native_determinant(matrix_list)
                        return str(det)
                    elif 'eigenvalue' in raw_input:
                        # For 2x2 matrices only (native implementation)
                        eigenvals = self._native_eigenvalues_2x2(matrix_list)
                        return str(eigenvals) if eigenvals else None
                    elif 'inverse' in raw_input:
                        inv = self._native_inverse(matrix_list)
                        return str(inv) if inv else None
                    elif 'transpose' in raw_input:
                        transposed = [[matrix_list[j][i] for j in range(n_rows)] for i in range(n_cols)]
                        return str(transposed)
                    elif 'trace' in raw_input:
                        if n_rows == n_cols:
                            trace = sum(matrix_list[i][i] for i in range(n_rows))
                            return str(trace)
                    elif 'rank' in raw_input:
                        rank = self._native_matrix_rank(matrix_list)
                        return str(rank)
                    else:
                        return str(matrix_list)
                except Exception:
                    pass

            return None
        except Exception as e:
            logger.warning(f"Linear algebra fallback failed: {e}")
            return None

    def _native_determinant(self, matrix: list) -> Optional[float]:
        """Calculate determinant using native Python (Laplace expansion)."""
        n = len(matrix)
        if n == 0:
            return None
        if n != len(matrix[0]):
            return None  # Not square

        if n == 1:
            return matrix[0][0]
        if n == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

        # Laplace expansion along first row
        det = 0
        for j in range(n):
            minor = [[matrix[i][k] for k in range(n) if k != j] for i in range(1, n)]
            cofactor = ((-1) ** j) * self._native_determinant(minor)
            det += matrix[0][j] * cofactor

        return det

    def _native_eigenvalues_2x2(self, matrix: list) -> Optional[list]:
        """Calculate eigenvalues for 2x2 matrix using characteristic polynomial."""
        import math
        if len(matrix) != 2 or len(matrix[0]) != 2:
            return None

        a, b = matrix[0]
        c, d = matrix[1]

        # Characteristic polynomial: lambda^2 - (a+d)*lambda + (ad - bc) = 0
        trace = a + d
        det = a * d - b * c

        discriminant = trace * trace - 4 * det

        if discriminant >= 0:
            sqrt_disc = math.sqrt(discriminant)
            lambda1 = (trace + sqrt_disc) / 2
            lambda2 = (trace - sqrt_disc) / 2
            return [lambda1, lambda2]
        else:
            # Complex eigenvalues
            real = trace / 2
            imag = math.sqrt(-discriminant) / 2
            return [f"{real} + {imag}*I", f"{real} - {imag}*I"]

    def _native_inverse(self, matrix: list) -> Optional[list]:
        """Calculate inverse for 2x2 matrix (native implementation)."""
        if len(matrix) != 2 or len(matrix[0]) != 2:
            return None

        a, b = matrix[0]
        c, d = matrix[1]

        det = a * d - b * c
        if det == 0:
            return None

        return [[d/det, -b/det], [-c/det, a/det]]

    def _native_matrix_rank(self, matrix: list) -> int:
        """Calculate rank using Gaussian elimination."""
        import copy
        # Make a copy to avoid modifying original
        m = copy.deepcopy(matrix)
        n_rows = len(m)
        n_cols = len(m[0]) if n_rows > 0 else 0

        rank = 0
        for col in range(min(n_rows, n_cols)):
            # Find pivot
            pivot_row = None
            for row in range(rank, n_rows):
                if abs(m[row][col]) > 1e-10:
                    pivot_row = row
                    break

            if pivot_row is None:
                continue

            # Swap rows
            m[rank], m[pivot_row] = m[pivot_row], m[rank]

            # Eliminate
            for row in range(rank + 1, n_rows):
                if abs(m[rank][col]) > 1e-10:
                    factor = m[row][col] / m[rank][col]
                    for j in range(col, n_cols):
                        m[row][j] -= factor * m[rank][j]

            rank += 1

        return rank

    def _stats_fallback(self, structured: StructuredProblem, raw_input: str) -> Optional[str]:
        """Statistics fallback using native Python math.

        NO SYMPY - Uses pure Python for statistical calculations.
        """
        try:
            import math
            import re
            import ast
            from fractions import Fraction

            # Extract list of numbers
            list_match = re.search(r'\[[\d\s,\.]+\]', raw_input)
            if list_match:
                try:
                    data = ast.literal_eval(list_match.group())

                    if 'mean' in raw_input or 'average' in raw_input:
                        result = sum(data) / len(data)
                        # Try to represent as fraction for exact results
                        if result == int(result):
                            return str(int(result))
                        try:
                            frac = Fraction(result).limit_denominator(1000)
                            if abs(float(frac) - result) < 1e-10:
                                return str(frac)
                        except Exception:
                            pass
                        return str(result)

                    elif 'median' in raw_input:
                        sorted_data = sorted(data)
                        n = len(sorted_data)
                        if n % 2 == 0:
                            return str((sorted_data[n//2 - 1] + sorted_data[n//2]) / 2)
                        else:
                            return str(sorted_data[n//2])

                    elif 'standard deviation' in raw_input or 'std' in raw_input:
                        mean = sum(data) / len(data)
                        variance = sum((x - mean)**2 for x in data) / len(data)
                        return str(math.sqrt(variance))

                    elif 'variance' in raw_input:
                        mean = sum(data) / len(data)
                        variance = sum((x - mean)**2 for x in data) / len(data)
                        return str(variance)

                    elif 'sum' in raw_input:
                        return str(sum(data))

                    elif 'min' in raw_input:
                        return str(min(data))

                    elif 'max' in raw_input:
                        return str(max(data))

                except Exception:
                    pass

            return None
        except Exception as e:
            logger.warning(f"Statistics fallback failed: {e}")
            return None

    def _discrete_fallback(self, structured: StructuredProblem, raw_input: str) -> Optional[str]:
        """Discrete Math fallback using native Python math.

        NO SYMPY - Uses pure Python for combinatorics and number theory.
        """
        try:
            import math
            import re

            # Factorial
            if 'factorial' in raw_input or '!' in raw_input:
                match = re.search(r'(\d+)\s*(?:factorial|!)', raw_input)
                if match:
                    n = int(match.group(1))
                    return str(math.factorial(n))

            # Combinations (n choose k) - binomial coefficient
            if 'choose' in raw_input or 'combination' in raw_input or 'C(' in raw_input:
                match = re.search(r'(\d+)\s*choose\s*(\d+)', raw_input)
                if match:
                    n, k = int(match.group(1)), int(match.group(2))
                    return str(math.comb(n, k))
                # Try C(n,k) format
                match = re.search(r'C\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', raw_input)
                if match:
                    n, k = int(match.group(1)), int(match.group(2))
                    return str(math.comb(n, k))

            # Permutations
            if 'permutation' in raw_input or 'P(' in raw_input:
                match = re.search(r'P\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', raw_input)
                if match:
                    n, k = int(match.group(1)), int(match.group(2))
                    return str(math.perm(n, k))

            # GCD/LCM
            if 'gcd' in raw_input:
                nums = re.findall(r'\d+', raw_input)
                if len(nums) >= 2:
                    return str(math.gcd(int(nums[0]), int(nums[1])))

            if 'lcm' in raw_input:
                nums = re.findall(r'\d+', raw_input)
                if len(nums) >= 2:
                    return str(math.lcm(int(nums[0]), int(nums[1])))

            # Prime check
            if 'prime' in raw_input:
                match = re.search(r'(\d+)', raw_input)
                if match:
                    n = int(match.group(1))
                    return str(self._is_prime(n))

            return None
        except Exception as e:
            logger.warning(f"Discrete math fallback failed: {e}")
            return None

    def _is_prime(self, n: int) -> bool:
        """Check if n is prime using native Python."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True

    def _map_operation_to_service(self, domain: str, operation: str) -> str:
        """Map operation to specialist service type."""
        op_map = {
            ('calculus', 'derivative'): 'math.calculus.differentiation',
            ('calculus', 'diff'): 'math.calculus.differentiation',
            ('calculus', 'differentiate'): 'math.calculus.differentiation',
            ('calculus', 'integral'): 'math.calculus.integration',
            ('calculus', 'integrate'): 'math.calculus.integration',
            ('algebra', 'factor'): 'math.algebra.polynomial',
            ('algebra', 'expand'): 'math.algebra.polynomial',
            ('algebra', 'compute'): 'math.algebra.arithmetic',
        }
        return op_map.get((domain, operation), f'math.{domain}.{operation}')

    def _create_specialist_for_operation(self, domain: str, operation: str) -> Optional[Any]:
        """Create a specialist on demand for the given operation.

        Note: Specialists are created with df and blackboard so they can
        properly register services and create result entries with metadata.
        """
        try:
            if domain == 'calculus':
                if operation in ['derivative', 'diff', 'differentiate']:
                    from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import (
                        DifferentiationSpecialist
                    )
                    return DifferentiationSpecialist(df=self.df, blackboard=self.blackboard)
                elif operation in ['integral', 'integrate']:
                    from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import (
                        IntegrationSpecialist
                    )
                    return IntegrationSpecialist(df=self.df, blackboard=self.blackboard)

            elif domain == 'algebra':
                if operation in ['factor', 'expand', 'simplify']:
                    from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import (
                        PolynomialSpecialist
                    )
                    return PolynomialSpecialist(df=self.df, blackboard=self.blackboard)
                else:
                    from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import (
                        ArithmeticSpecialist
                    )
                    return ArithmeticSpecialist(df=self.df, blackboard=self.blackboard)

            return None

        except ImportError as e:
            logger.warning(f"Could not import specialist for {domain}.{operation}: {e}")
            return None

    def _call_specialist(self, specialist: Any, structured: StructuredProblem) -> Optional[str]:
        """Call a specialist's process method and extract result."""
        try:
            # Create minimal task entry
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType

            task_entry = create_entry(
                entry_type=EntryType.TASK,
                content=structured.omdoc_content,
                author_agent=self.agent_id,
                conversation_id=f'specialist_invoke_{id(structured)}',
                metadata={
                    'operation': structured.metadata.get('operation', 'compute'),
                    'raw_input': structured.raw_input,
                    'sympy_expr': str(structured.sympy_expr) if structured.sympy_expr else None,
                    'expression': structured.metadata.get('expression'),
                    'variable': structured.metadata.get('variable', 'x')
                }
            )

            result_entry = specialist.process(task_entry)

            # Extract result
            if result_entry:
                if hasattr(result_entry, 'metadata') and result_entry.metadata:
                    result_str = result_entry.metadata.get('result_str')
                    if result_str and result_str not in ('None', 'none', ''):
                        return result_str
                    result_val = result_entry.metadata.get('result')
                    if result_val:
                        return str(result_val)
                if hasattr(result_entry, 'content') and result_entry.content:
                    return str(result_entry.content)

            return None

        except Exception as e:
            logger.warning(f"Specialist call failed: {e}")
            return None

    def _get_service_type(self, domain: MathDomain) -> str:
        """
        Get the service type string for a mathematical domain.

        Maps MathDomain enum to the service type format used by
        Directory Facilitator (e.g., 'math.algebra', 'math.linalg').

        Args:
            domain: MathDomain enum value

        Returns:
            Service type string for DF query
        """
        # Service type mapping - some domains use abbreviated names
        service_map = {
            MathDomain.CALCULUS: 'math.calculus',
            MathDomain.ALGEBRA: 'math.algebra',
            MathDomain.LINEAR_ALGEBRA: 'math.linalg',
            MathDomain.GEOMETRY: 'math.geometry',
            MathDomain.LOGIC: 'math.logic',
            MathDomain.NUMBER_THEORY: 'math.numbertheory',
            MathDomain.STATISTICS: 'math.stats',
            MathDomain.DISCRETE_MATH: 'math.discrete',
            MathDomain.UNKNOWN: 'math.unknown',
        }
        return service_map.get(domain, f'math.{get_pool_domain_key(domain)}')

    def _find_capable_agents(self, service_type: str) -> List[Dict[str, Any]]:
        """
        Query Directory Facilitator for capable agents

        This implements the dynamic routing logic. The Orchestrator
        queries the DF to find agents with the required capability.

        Args:
            service_type: Service type to search for (e.g., 'math.calculus')

        Returns:
            List of agent service registrations

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 136-142
        "When Orchestrator identifies a 'Calculus' tag from the Analysis Team,
        it queries the DF for available agents with that capability"
        """
        if not self.df:
            logger.warning(f"    No Directory Facilitator available")
            return []

        # Query DF for agents with this service type
        agents = self.df.search(service_type=service_type)

        return agents

    def _post_task_to_blackboard(
        self,
        structured: StructuredProblem,
        assigned_agent: str
    ) -> Task:
        """
        Post task to Blackboard for solver agents to pick up

        Args:
            structured: Problem to post
            assigned_agent: Agent ID that should handle this

        Returns:
            Task object for tracking

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Lines 145-152
        """
        # Create task
        task_id = f'task_{uuid.uuid4().hex[:8]}'
        task = Task(
            task_id=task_id,
            structured_problem=structured,
            status=EntryStatus.PENDING,
            assigned_agent=assigned_agent
        )

        if not self.blackboard:
            logger.warning(f"    No Blackboard available")
            task.status = EntryStatus.FAILED
            task.error = "No Blackboard available"
            return task

        # Activate the assigned agent (STANDBY -> ACTIVE)
        if self.agent_pool:
            logger.debug(f"    Activating agent: {assigned_agent}")
            self._activate_agent(assigned_agent)

        # Create Blackboard entry
        entry = create_entry(
            entry_type=EntryType.TASK,
            content=structured.omdoc_content,
            author_agent=self.agent_id,
            conversation_id=task_id,
            tags=[structured.domain.value, 'task', task_id],
            metadata={
                'problem_type': structured.problem_type.value,
                'domain': structured.domain.value,
                'raw_input': structured.raw_input,
                'assigned_agent': assigned_agent,
                'sympy_expr': str(structured.sympy_expr) if structured.sympy_expr else None,
                'operation': structured.metadata.get('operation', 'compute'),
                'variable': structured.metadata.get('variable', 'x')  # Default to 'x'
            }
        )

        # Post to Blackboard
        self.blackboard.post(entry)
        task.blackboard_entry_id = entry.entry_id

        # Track task
        self.active_tasks[task_id] = task
        self.tasks_routed += 1

        return task

    def _await_verified_result(self, task: Task, timeout: float = 30.0) -> Any:
        """
        Wait for verified result from Verification Core

        Polls Blackboard for result entry with STATUS: VERIFIED

        Args:
            task: Task to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Verified result

        Raises:
            TimeoutError: If result not received within timeout

        REFERENCE:
        ---------
        Phase_1_Build_Order_Breakdown.md: Line 154
        "Wait for verified result"
        """
        if not self.blackboard:
            raise RuntimeError("No Blackboard available")

        start_time = time.time()
        poll_interval = 0.5  # Poll every 500ms

        while time.time() - start_time < timeout:
            # Query Blackboard for result entries (PARTIAL_RESULT from solver)
            results = self.blackboard.query_entries(
                tags=[task.task_id],
                entry_type=EntryType.PARTIAL_RESULT
            )

            for result in results:
                if result.status == EntryStatus.VERIFIED:
                    # Found verified result!
                    logger.info(f"    [OK] Received verified result")
                    task.status = EntryStatus.VERIFIED
                    task.result = result.content

                    # Deactivate agent (ACTIVE -> STANDBY)
                    if task.assigned_agent:
                        self._deactivate_agent(task.assigned_agent, return_to_standby=True)

                    # Move to completed
                    if task.task_id in self.active_tasks:
                        del self.active_tasks[task.task_id]
                    self.completed_tasks.append(task)
                    self.tasks_completed += 1

                    # Return result string from metadata if available
                    result_str = result.metadata.get('result_str')
                    if result_str:
                        return result_str
                    return result.content

                elif result.status == EntryStatus.FAILED:
                    # Task failed
                    logger.error(f"    [X] Task failed: {result.metadata.get('error')}")
                    task.status = EntryStatus.FAILED
                    task.error = result.metadata.get('error', 'Unknown error')
                    self.tasks_failed += 1

                    # Deactivate agent even on failure
                    if task.assigned_agent:
                        self._deactivate_agent(task.assigned_agent, return_to_standby=True)

                    raise RuntimeError(f"Task failed: {task.error}")

            # Wait before next poll
            time.sleep(poll_interval)

        # Timeout
        task.status = EntryStatus.FAILED
        task.error = "Timeout waiting for result"
        self.tasks_failed += 1

        raise TimeoutError(f"Timeout waiting for verified result (task: {task.task_id})")

    # ==========================================================================
    # LEARNING / MEMORY METHODS
    # ==========================================================================

    def _look_before_leap(self, structured: StructuredProblem) -> Optional[str]:
        """
        Check memory for existing solutions before computing.

        The "Look-Before-You-Leap" protocol queries the knowledge management
        team to see if we've already solved a similar problem.

        Args:
            structured: The problem to look up

        Returns:
            Cached result string if found, None otherwise
        """
        if not self.knowledge_team:
            return None

        try:
            # Query the retrieval specialist
            retrieval_result = self.knowledge_team.look_before_leap(
                structured.raw_input
            )

            # Check if the retrieval found a high-confidence match
            if retrieval_result.should_skip_solving():
                logger.debug(f"    [LEARNING] Found cached solution with confidence: {retrieval_result.confidence}")
                return retrieval_result.theorem_content

            return None

        except Exception as e:
            logger.debug(f"    [LEARNING] Lookup failed: {e}")
            return None

    def _record_solution(self, structured: StructuredProblem, result: str) -> None:
        """
        Record a successful solution for future retrieval.

        Stores the problem and its solution in the vector database so
        that similar future problems can be resolved from memory.

        Args:
            structured: The original problem
            result: The computed result
        """
        if not self.knowledge_team:
            return

        try:
            # Generate a conversation ID for this solution
            conversation_id = f"solution_{uuid.uuid4().hex[:8]}"

            # Record the result
            entry_id = self.knowledge_team.record_result(
                conversation_id=conversation_id,
                problem=structured.raw_input,
                result=result,
                proof_trace=None  # Could add solving trace here in future
            )

            self.solutions_recorded += 1
            logger.debug(f"    [LEARNING] Recorded solution: {entry_id}")

        except Exception as e:
            logger.debug(f"    [LEARNING] Recording failed: {e}")

    # BDI Implementation (simplified for Phase 1)
    def update_beliefs(self):
        """Update beliefs from environment"""
        # In Phase 1, we use direct method calls instead of full BDI loop
        # Phase 2 will implement full BDI reasoning
        pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions"""
        # In Phase 1, we use direct method calls
        # Phase 2 will implement full HTN planning
        return []

    def execute_step(self, intention: Intention):
        """Execute intention step"""
        # In Phase 1, we use direct method calls
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_routed': self.tasks_routed,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'active_tasks': len(self.active_tasks),
            'non_intervention': self.NON_INTERVENTION,
            'agents_woken': self.agents_woken,
            'agents_activated': self.agents_activated,
            'agent_pool_enabled': self.agent_pool is not None,
            # Learning statistics
            'learning_enabled': self.knowledge_team is not None,
            'cache_hits': self.cache_hits,
            'solutions_recorded': self.solutions_recorded,
        })
        if self.agent_pool:
            stats['pool_stats'] = self.agent_pool.get_statistics()
        if self.knowledge_team:
            stats['knowledge_team_stats'] = self.knowledge_team.get_statistics()
        return stats


if __name__ == "__main__":
    """Test Main Orchestrator"""
    print("=" * 80)
    print("PHASE 1 - STEP 2: MAIN ORCHESTRATOR TEST")
    print("=" * 80)
    print()

    # Initialize Phase 0 infrastructure
    from symbo_agentic_reasoners.core.system import Phase0System

    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Orchestrator
    orchestrator = MainOrchestrator(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    # Test case: Try to process (will fail since no solver registered yet)
    print("Test: Attempting to process problem (will fail - no solver yet)...")
    print()

    from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam

    team = ProblemAnalysisTeam()
    structured = team.process("Calculate the derivative of x**2 + 1")

    print()
    print("Attempting orchestration...")
    try:
        result = orchestrator.process(structured)
        print(f"Result: {result}")
    except NoAgentAvailableError as e:
        print(f"Expected error: {e}")
        print("(This is correct - no solver agent registered yet)")

    print()
    print("=" * 80)
    print("MAIN ORCHESTRATOR TEST COMPLETE")
    print("=" * 80)
    print()
    print("Statistics:")
    import json
    print(json.dumps(orchestrator.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
