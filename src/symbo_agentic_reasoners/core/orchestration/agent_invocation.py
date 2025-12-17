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
Orchestration Agent Invocation
===============================

Handles direct agent invocation and specialist calling logic.

Responsibilities:
- Direct supervisor/specialist invocation
- Service type mapping
- Specialist factory pattern
- Directory Facilitator queries
"""

import logging
from typing import Any, Optional, List, Dict
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
from symbo_agentic_reasoners.core.blackboard import Blackboard, create_entry, EntryType

logger = logging.getLogger('symbo_agentic_reasoners.orchestration.agent_invocation')


class AgentInvoker:
    """
    Handles agent invocation and specialist calling.

    Manages direct invocation of supervisors and specialists,
    service discovery via Directory Facilitator, and specialist
    factory creation.
    """

    def __init__(
        self,
        agent_id: str,
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize agent invoker.

        Args:
            agent_id: ID of the orchestrator (for task attribution)
            df: Directory Facilitator for service discovery
            blackboard: Blackboard for agent coordination
        """
        self.agent_id = agent_id
        self.df = df
        self.blackboard = blackboard
        self.invocations = 0

    def direct_invoke(
        self,
        structured: StructuredProblem,
        supervisor_instance: Any,
        fallback_callback=None
    ) -> Optional[Any]:
        """
        Direct invocation path - calls supervisor/specialist directly.

        When an agent has an instance registered, we can invoke it directly
        instead of posting to blackboard and waiting. This provides much
        faster results for synchronous use cases.

        Args:
            structured: The structured problem
            supervisor_instance: The agent instance to invoke
            fallback_callback: Optional callback for fallback computation

        Returns:
            Result string or None if invocation failed
        """
        try:
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

            # Check if result_entry is a delegation (has assigned_agent in metadata)
            if result_entry and hasattr(result_entry, 'metadata'):
                assigned_specialist_id = result_entry.metadata.get('assigned_agent')
                if assigned_specialist_id:
                    # Find the specialist and invoke it directly
                    specialist_result = self.invoke_specialist_directly(
                        structured, assigned_specialist_id, fallback_callback
                    )
                    if specialist_result:
                        self.invocations += 1
                        return specialist_result

            # If supervisor returned a result directly (not a delegation)
            if result_entry:
                if hasattr(result_entry, 'metadata') and result_entry.metadata:
                    # Check for error - if so, fall back
                    if result_entry.metadata.get('error'):
                        if fallback_callback:
                            return fallback_callback(
                                structured,
                                structured.metadata.get('operation', 'compute')
                            )
                    result_str = result_entry.metadata.get('result_str')
                    if result_str:
                        self.invocations += 1
                        return result_str
                if hasattr(result_entry, 'content') and result_entry.content:
                    self.invocations += 1
                    return str(result_entry.content)

            # No result from supervisor - use fallback
            if fallback_callback:
                return fallback_callback(
                    structured,
                    structured.metadata.get('operation', 'compute')
                )
            return None

        except Exception as e:
            logger.warning(f"Direct invocation failed: {e}")
            # Fall back if callback provided
            if fallback_callback:
                return fallback_callback(
                    structured,
                    structured.metadata.get('operation', 'compute')
                )
            return None

    def invoke_specialist_directly(
        self,
        structured: StructuredProblem,
        specialist_id: str,
        fallback_callback=None
    ) -> Optional[str]:
        """
        Invoke a specialist directly by creating and calling it.

        Falls back to creating specialists on-demand if not registered,
        and finally to native computation.

        Args:
            structured: Problem to solve
            specialist_id: ID of specialist to invoke
            fallback_callback: Optional fallback computation

        Returns:
            Result string or None
        """
        try:
            operation = structured.metadata.get('operation', 'compute')
            domain = structured.domain.value.lower()

            # Try to find registered specialist with instance
            if self.df:
                specialist_type = self.map_operation_to_service(domain, operation)
                specialists = self.df.search(service_type=specialist_type)

                for spec in specialists:
                    if hasattr(spec, 'instance') and spec.instance is not None:
                        result = self.call_specialist(spec.instance, structured)
                        if result:
                            return result

            # Fall back to creating specialist on demand
            specialist = self.create_specialist_for_operation(domain, operation)
            if specialist:
                result = self.call_specialist(specialist, structured)
                if result:
                    return result

            # Final fallback
            if fallback_callback:
                return fallback_callback(structured, operation)
            return None

        except Exception as e:
            logger.warning(f"Specialist invocation failed: {e}")
            return None

    def map_operation_to_service(self, domain: str, operation: str) -> str:
        """
        Map operation to specialist service type.

        Args:
            domain: Problem domain
            operation: Operation type

        Returns:
            Service type string for DF query
        """
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

    def create_specialist_for_operation(self, domain: str, operation: str) -> Optional[Any]:
        """
        Create a specialist on demand for the given operation.

        Note: Specialists are created with df and blackboard so they can
        properly register services and create result entries with metadata.

        Args:
            domain: Problem domain
            operation: Operation to perform

        Returns:
            Specialist instance or None
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

    def call_specialist(self, specialist: Any, structured: StructuredProblem) -> Optional[str]:
        """
        Call a specialist's process method and extract result.

        Args:
            specialist: Specialist instance
            structured: Problem to solve

        Returns:
            Result string or None
        """
        try:
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

    def get_service_type(self, domain: MathDomain) -> str:
        """
        Get the service type string for a mathematical domain.

        Maps MathDomain enum to the service type format used by
        Directory Facilitator (e.g., 'math.algebra', 'math.linalg').

        Args:
            domain: MathDomain enum value

        Returns:
            Service type string for DF query
        """
        from symbo_agentic_reasoners.core.orchestration.data_structures import get_pool_domain_key

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

    def find_capable_agents(self, service_type: str) -> List[Dict[str, Any]]:
        """
        Query Directory Facilitator for capable agents.

        Args:
            service_type: Service type to search for (e.g., 'math.calculus')

        Returns:
            List of agent service registrations
        """
        if not self.df:
            logger.warning("No Directory Facilitator available")
            return []

        agents = self.df.search(service_type=service_type)
        return agents


__all__ = [
    'AgentInvoker',
]
