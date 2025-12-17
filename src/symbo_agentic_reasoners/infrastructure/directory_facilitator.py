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
PHASE 0 - STEP 4: The Bureaucratic Infrastructure Team - DF
===========================================================

Directory Facilitator (DF) - "Yellow Pages" / Service Registry

PURPOSE:
-------
Provides dynamic lookup for agent services. Agents register their capabilities
(e.g., service: integration, algorithm: risch), allowing other agents to discover
and request services without knowing specific agent identifiers.

REFERENCE:
---------
- Phase_0_Build_Order_Breakdown.md: Step 4 - DF (Lines 365-423)
- Phase 0 Coding Strategy: Section 3.0 "The Civic Infrastructure"

AGENT TYPE:
----------
Model-Based Reflex Agent - Maintains internal model of service registry

ROLE & ANALOGY:
--------------
"Yellow Pages" - Enables dynamic service discovery. Instead of hardcoding
"send integration request to agent_XYZ", agents query DF: "Find me an integration
agent with algorithm=risch and cost=medium"

WHY THIS MATTERS:
----------------
As the system scales to 40-50 specialized agents, static agent addressing becomes
unmaintainable. DF enables:
  1. Dynamic discovery: Find agents by capability, not by name
  2. Load balancing: Multiple agents can provide same service
  3. Graceful degradation: If an agent fails, DF redirects to alternatives
  4. Hot-swapping: Agents can be added/removed without breaking the system

EXAMPLE USE CASE:
----------------
1. Integration Specialist registers: service='integration', algorithm='risch'
2. Orchestrator needs integration: queries DF for 'integration' service
3. DF returns list of agents providing integration
4. Orchestrator selects best agent based on cost, algorithm, availability
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import threading
import logging
from datetime import datetime

# Setup logging
logger = logging.getLogger('symbo_agentic_reasoners.directory_facilitator')


@dataclass
class ServiceRegistration:
    """
    Service description for DF registration

    Describes a service provided by an agent, including metadata about
    the service's characteristics and cost.

    FIELDS:
    ------
    - service_type: Hierarchical service identifier (e.g., 'math.calculus.integration')
    - agent_id: Provider agent identifier
    - algorithm: Specific algorithm used (e.g., 'risch', 'heuristic', 'symbolic')
    - cost: Resource cost indicator ('low', 'medium', 'high')
    - properties: Additional key-value properties for filtering
    - registered_at: Timestamp of registration
    - instance: Optional reference to the actual agent object

    EXAMPLE REGISTRATIONS:
    ---------------------
    Integration Specialist:
        service_type='math.calculus.integration'
        agent_id='integration_specialist_001'
        algorithm='risch'
        cost='high'
        properties={'type': 'symbolic', 'deterministic': 'true'}

    Algebra Specialist:
        service_type='math.algebra.polynomial_factorization'
        agent_id='algebra_specialist_001'
        algorithm='groebner_basis'
        cost='medium'
        properties={'max_degree': '10', 'field': 'rational'}

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 371-379
    """
    service_type: str       # e.g., 'math.calculus.integration'
    agent_id: str           # Provider agent identifier
    algorithm: str          # e.g., 'risch', 'heuristic'
    cost: str = 'medium'    # 'low', 'medium', 'high' (VRAM/compute)
    properties: Dict[str, str] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    instance: Optional[object] = None  # Optional reference to agent instance

    def matches_constraint(self, key: str, value: str) -> bool:
        """Check if this registration matches a constraint"""
        if key == 'algorithm':
            return self.algorithm == value
        elif key == 'cost':
            return self.cost == value
        elif key in self.properties:
            return self.properties[key] == value
        return False

    def __repr__(self) -> str:
        """Human-readable representation"""
        return (f"Service[{self.service_type}] by {self.agent_id} "
                f"({self.algorithm}, cost={self.cost})")


class DirectoryFacilitator:
    """
    Yellow Pages - Service registry for dynamic agent discovery

    DF maintains a registry of services provided by agents, enabling dynamic
    service discovery without hardcoded agent identifiers.

    THREAD SAFETY:
    -------------
    All operations are protected by a reentrant lock (threading.RLock) to ensure
    thread-safe access from multiple agents.

    TYPICAL WORKFLOW:
    ----------------
    1. Agent Registration Phase:
       - Integration Specialist registers 'integration' service
       - Algebra Specialist registers 'factorization' service
       - Verification Agent registers 'proof_checking' service

    2. Service Discovery Phase:
       - Orchestrator receives problem requiring integration
       - Orchestrator queries DF: search('math.calculus.integration')
       - DF returns list of agents providing integration
       - Orchestrator selects best match based on algorithm, cost, availability

    3. Dynamic Updates:
       - Agents can register/deregister services at runtime
       - Failed agents are removed from registry
       - New agents auto-discovered when they register

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 381-413
    """

    def __init__(self, enable_auth: bool = True):
        """
        Initialize Directory Facilitator

        Args:
            enable_auth: Enable agent authentication (Phase 5 - Issue #4)
        """
        self._services: Dict[str, List[ServiceRegistration]] = {}  # service_type -> registrations
        self._agent_services: Dict[str, List[str]] = {}  # agent_id -> service_types
        self._lock = threading.RLock()

        # Phase 5 - Issue #4: Agent Authentication System
        # Import here to avoid circular dependency
        from symbo_agentic_reasoners.infrastructure.security.agent_auth import AgentAuthenticator
        self.authenticator = AgentAuthenticator(enable_auth=enable_auth)
        logger.info("DF: Agent authentication system initialized")

    def register(self, registration: ServiceRegistration,
                auth_token: Optional[str] = None,
                auth_timestamp: Optional[int] = None) -> bool:
        """
        Register agent service capability

        Phase 5 - Issue #4: Now includes agent authentication verification.

        Args:
            registration: ServiceRegistration describing the service
            auth_token: Optional HMAC authentication token (Issue #4)
            auth_timestamp: Optional token timestamp (Issue #4)

        Returns:
            bool: True if registration successful

        Security:
            If auth_token and auth_timestamp provided, verifies agent identity
            before service registration. Prevents unauthorized service spoofing.

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 387-399
        """
        with self._lock:
            service_type = registration.service_type
            agent_id = registration.agent_id

            # Phase 5 - Issue #4: Verify agent credentials if provided
            if auth_token is not None and auth_timestamp is not None:
                if not self.authenticator.verify_credential(
                    agent_id, auth_token, auth_timestamp
                ):
                    logger.warning(
                        f"Service registration DENIED (authentication failed): "
                        f"{service_type} by {agent_id}"
                    )
                    return False
                logger.debug(f"Service registration authentication verified: {agent_id}")

            # Add to service index
            if service_type not in self._services:
                self._services[service_type] = []

            # Check for duplicate registration
            existing = [r for r in self._services[service_type]
                       if r.agent_id == agent_id and r.algorithm == registration.algorithm]
            if existing:
                logger.warning(f"Service already registered: {service_type} by {agent_id}")
                return False

            self._services[service_type].append(registration)

            # Track agent's services for cleanup
            if agent_id not in self._agent_services:
                self._agent_services[agent_id] = []
            if service_type not in self._agent_services[agent_id]:
                self._agent_services[agent_id].append(service_type)

            logger.info(f"Registered {registration}")
            return True

    def deregister(self, agent_id: str, service_type: Optional[str] = None) -> bool:
        """
        Deregister agent services

        Args:
            agent_id: Agent whose services to deregister
            service_type: Specific service to deregister (if None, deregister all)

        Returns:
            bool: True if any services were deregistered
        """
        with self._lock:
            if agent_id not in self._agent_services:
                return False

            deregistered = False

            if service_type:
                # Deregister specific service
                if service_type in self._services:
                    before_count = len(self._services[service_type])
                    self._services[service_type] = [
                        r for r in self._services[service_type]
                        if r.agent_id != agent_id
                    ]
                    after_count = len(self._services[service_type])
                    if before_count > after_count:
                        deregistered = True
                        logger.info(f"Deregistered {service_type} for {agent_id}")

                    # Clean up agent tracking
                    if service_type in self._agent_services[agent_id]:
                        self._agent_services[agent_id].remove(service_type)
            else:
                # Deregister all services for agent
                for svc_type in list(self._agent_services[agent_id]):
                    if svc_type in self._services:
                        self._services[svc_type] = [
                            r for r in self._services[svc_type]
                            if r.agent_id != agent_id
                        ]
                        deregistered = True
                        logger.info(f"Deregistered {svc_type} for {agent_id}")

                # Clean up agent tracking
                del self._agent_services[agent_id]

            return deregistered

    def search(self, service_type: str,
              constraints: Optional[Dict[str, str]] = None) -> List[ServiceRegistration]:
        """
        Find agents providing service (Orchestrator uses this)

        Args:
            service_type: Service to search for (e.g., 'math.calculus.integration')
            constraints: Optional constraints (e.g., {'algorithm': 'risch', 'cost': 'medium'})

        Returns:
            List of ServiceRegistration objects matching criteria

        MATCHING LOGIC:
        --------------
        - Exact match on service_type
        - All constraints must match (AND logic)
        - Results ordered by registration time (oldest first = most stable)

        EXAMPLE QUERIES:
        ---------------
        # Find any integration service:
        df.search('math.calculus.integration')

        # Find Risch algorithm integration:
        df.search('math.calculus.integration', {'algorithm': 'risch'})

        # Find low-cost symbolic integration:
        df.search('math.calculus.integration', {'cost': 'low', 'type': 'symbolic'})

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 401-413
        """
        with self._lock:
            # Find services matching type
            if service_type not in self._services:
                return []

            results = list(self._services[service_type])

            # Apply constraints (AND logic)
            if constraints:
                filtered_results = []
                for reg in results:
                    if all(reg.matches_constraint(k, v) for k, v in constraints.items()):
                        filtered_results.append(reg)
                results = filtered_results

            return results

    def search_by_prefix(self, service_prefix: str) -> List[ServiceRegistration]:
        """
        Search for services by prefix

        Useful for finding all services in a category.

        Args:
            service_prefix: Prefix to match (e.g., 'math.calculus')

        Returns:
            List of all ServiceRegistration objects with matching prefix

        EXAMPLE:
        -------
        # Find all calculus services:
        df.search_by_prefix('math.calculus')  # Returns integration, differentiation, etc.
        """
        with self._lock:
            results = []
            for service_type, registrations in self._services.items():
                if service_type.startswith(service_prefix):
                    results.extend(registrations)
            return results

    def get_agent_services(self, agent_id: str) -> List[ServiceRegistration]:
        """
        Get all services provided by a specific agent

        Args:
            agent_id: Agent identifier

        Returns:
            List of ServiceRegistration objects for this agent
        """
        with self._lock:
            if agent_id not in self._agent_services:
                return []

            results = []
            for service_type in self._agent_services[agent_id]:
                if service_type in self._services:
                    agent_regs = [r for r in self._services[service_type]
                                 if r.agent_id == agent_id]
                    results.extend(agent_regs)
            return results

    def list_all_services(self) -> List[str]:
        """
        List all registered service types

        Returns:
            List of service type strings
        """
        with self._lock:
            return list(self._services.keys())

    def get_service_providers(self, service_type: str) -> List[str]:
        """
        Get list of agent IDs providing a service

        Args:
            service_type: Service to query

        Returns:
            List of agent IDs
        """
        with self._lock:
            if service_type not in self._services:
                return []
            return list(set(r.agent_id for r in self._services[service_type]))

    # =========================================================================
    # PHASE 5 - ISSUE #4: AGENT AUTHENTICATION METHODS
    # =========================================================================

    def issue_agent_credential(self, agent_id: str) -> 'AgentCredential':
        """
        Issue authentication credential for agent.

        Phase 5 - Issue #4: Helper method for agents to obtain credentials
        before service registration.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentCredential with HMAC token
        """
        return self.authenticator.issue_credential(agent_id)

    def revoke_agent_credential(self, agent_id: str) -> bool:
        """
        Revoke agent authentication credential.

        Args:
            agent_id: Agent identifier

        Returns:
            True if credential was revoked
        """
        return self.authenticator.revoke_credential(agent_id)

    # =========================================================================

    def get_statistics(self) -> Dict[str, any]:
        """
        Get DF statistics

        Returns:
            Dictionary with statistics about registered services
        """
        with self._lock:
            total_registrations = sum(len(regs) for regs in self._services.values())

            service_counts = {
                svc_type: len(regs)
                for svc_type, regs in self._services.items()
            }

            return {
                'total_services': len(self._services),
                'total_registrations': total_registrations,
                'registered_agents': len(self._agent_services),
                'service_counts': service_counts,
                # Phase 5 - Issue #4: Authentication statistics
                'authentication': self.authenticator.get_statistics()
            }

    def __repr__(self) -> str:
        """Human-readable representation"""
        stats = self.get_statistics()
        return (f"DF(services={stats['total_services']}, "
                f"registrations={stats['total_registrations']}, "
                f"agents={stats['registered_agents']})")


# Helper function for creating registrations

def create_service_registration(service_type: str, agent_id: str,
                               algorithm: str = 'default',
                               cost: str = 'medium',
                               instance: object = None,
                               **properties) -> ServiceRegistration:
    """
    Helper function to create a ServiceRegistration

    Args:
        service_type: Hierarchical service identifier
        agent_id: Provider agent
        algorithm: Algorithm/method used
        cost: Resource cost ('low', 'medium', 'high')
        instance: Optional reference to the agent object for direct invocation
        **properties: Additional properties as keyword arguments

    Returns:
        ServiceRegistration ready to be registered

    EXAMPLE:
    -------
    reg = create_service_registration(
        service_type='math.calculus.integration',
        agent_id='integration_specialist_001',
        algorithm='risch',
        cost='high',
        instance=my_integration_specialist,  # Optional agent reference
        type='symbolic',
        deterministic='true'
    )
    """
    return ServiceRegistration(
        service_type=service_type,
        agent_id=agent_id,
        algorithm=algorithm,
        cost=cost,
        properties=properties,
        instance=instance
    )


if __name__ == "__main__":
    """Demonstration of DF functionality"""
    print("=" * 80)
    print("PHASE 0 - STEP 4: Directory Facilitator (DF)")
    print("=" * 80)
    print()

    # Initialize DF
    df = DirectoryFacilitator()
    print(f"Initialized: {df}")
    print()

    # Example 1: Register integration services
    print("Example 1: Registering integration services")
    df.register(create_service_registration(
        service_type='math.calculus.integration',
        agent_id='integration_specialist_001',
        algorithm='risch',
        cost='high',
        type='symbolic',
        deterministic='true'
    ))
    df.register(create_service_registration(
        service_type='math.calculus.integration',
        agent_id='integration_specialist_002',
        algorithm='heuristic',
        cost='medium',
        type='symbolic',
        deterministic='false'
    ))
    print(f"  {df}")
    print()

    # Example 2: Register other services
    print("Example 2: Registering diverse services")
    df.register(create_service_registration(
        service_type='math.algebra.polynomial_factorization',
        agent_id='algebra_specialist_001',
        algorithm='groebner_basis',
        cost='medium'
    ))
    df.register(create_service_registration(
        service_type='math.calculus.differentiation',
        agent_id='differentiation_agent_001',
        algorithm='symbolic',
        cost='low'
    ))
    print(f"  {df}")
    print()

    # Example 3: Search for integration services
    print("Example 3: Search for integration services")
    results = df.search('math.calculus.integration')
    print(f"  Found {len(results)} integration service(s):")
    for reg in results:
        print(f"    - {reg}")
    print()

    # Example 4: Search with constraints
    print("Example 4: Search for deterministic integration")
    results = df.search('math.calculus.integration',
                       constraints={'deterministic': 'true'})
    print(f"  Found {len(results)} deterministic integration service(s):")
    for reg in results:
        print(f"    - {reg}")
    print()

    # Example 5: Search by prefix
    print("Example 5: Search all calculus services")
    results = df.search_by_prefix('math.calculus')
    print(f"  Found {len(results)} calculus service(s):")
    for reg in results:
        print(f"    - {reg}")
    print()

    # Example 6: Get agent's services
    print("Example 6: Get services for integration_specialist_001")
    services = df.get_agent_services('integration_specialist_001')
    print(f"  Agent provides {len(services)} service(s):")
    for svc in services:
        print(f"    - {svc}")
    print()

    # Example 7: Statistics
    print("Example 7: DF Statistics")
    import json
    stats = df.get_statistics()
    print(json.dumps(stats, indent=2))
    print()

    print("✓ Directory Facilitator (DF) implementation complete")
    print("  - Service registration ✓")
    print("  - Dynamic service discovery ✓")
    print("  - Constraint-based search ✓")
    print("  - Agent service tracking ✓")
