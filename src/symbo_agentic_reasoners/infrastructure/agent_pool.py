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
AGENT POOL - Dynamic Agent Lifecycle Management
================================================

Extends AMS with problem-aware agent activation. Agents are kept dormant
until needed, then brought to standby, then activated only when their
turn comes in the problem-solving workflow.

AGENT LIFECYCLE:
---------------
DORMANT -> STANDBY -> ACTIVE -> STANDBY -> DORMANT
    ^         |         |         |
    |         |         v         |
    |         +-----> SUSPENDED <-+
    |                    |
    +--------------------+

STATES:
------
- DORMANT: Agent class exists but no instance created. Zero memory footprint.
- STANDBY: Instance created, minimal state loaded, ready for quick activation.
- ACTIVE: Fully operational, may hold VRAM slot if cognitive.
- SUSPENDED: Paused mid-computation, state preserved.

PROBLEM-AWARE ACTIVATION:
------------------------
When a problem arrives:
1. Orchestrator classifies problem domain (algebra, calculus, etc.)
2. AgentPool wakes required supervisor (DORMANT -> STANDBY)
3. Supervisor determines which specialists are needed
4. Specialists are activated in order (STANDBY -> ACTIVE)
5. After solving, agents return to STANDBY or DORMANT based on recency

RESOURCE EFFICIENCY:
-------------------
- Only 1 cognitive agent active at a time (AMS enforcement)
- Specialists for unneeded domains stay DORMANT
- Recently-used agents stay in STANDBY for quick reactivation
- Timeout moves STANDBY agents back to DORMANT
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Type, Callable, Any
from enum import Enum
from datetime import datetime, timedelta
import threading
import logging

from symbo_agentic_reasoners.infrastructure.ams import (
    AgentManagementSystem, AgentStatus, AgentType, AgentRecord
)

logger = logging.getLogger('symbo_agentic_reasoners.agent_pool')


class PoolState(Enum):
    """Extended lifecycle states for agent pool management"""
    DORMANT = 'dormant'      # Class registered, no instance
    STANDBY = 'standby'      # Instance created, minimal memory
    ACTIVE = 'active'        # Fully operational
    SUSPENDED = 'suspended'  # Paused with state preserved


@dataclass
class AgentSpec:
    """
    Specification for an agent that can be instantiated on demand.

    Agents are registered with the pool via their spec, but instances
    are only created when needed.
    """
    agent_id: str
    agent_class: Type  # The class to instantiate
    domain: str        # e.g., 'algebra', 'calculus', 'statistics'
    tier: int          # 1=orchestrator, 2=supervisor, 3=specialist
    agent_type: AgentType
    services: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Required agents
    init_args: Dict[str, Any] = field(default_factory=dict)
    vram_requirement: float = 0.0
    ram_requirement: float = 0.1  # Minimal RAM for standby
    standby_timeout_seconds: int = 300  # 5 min before returning to dormant


@dataclass
class PooledAgent:
    """Runtime state for a pooled agent"""
    spec: AgentSpec
    state: PoolState = PoolState.DORMANT
    instance: Optional[Any] = None
    last_active: Optional[datetime] = None
    activation_count: int = 0
    total_active_time: timedelta = field(default_factory=lambda: timedelta())


class AgentPool:
    """
    Manages a pool of agents with lazy instantiation and automatic cleanup.

    Works alongside AMS - AgentPool handles the higher-level lifecycle
    (dormant/standby), while AMS handles resource enforcement (active/queued).
    """

    # Domain -> Required Supervisors/Specialists mapping
    DOMAIN_AGENTS = {
        'algebra': {
            'supervisor': 'algebra_supervisor',
            'specialists': [
                'arithmetic_specialist',
                'polynomial_specialist',
                'equation_system_solver',
                'number_theory_specialist',
            ]
        },
        'calculus': {
            'supervisor': 'calculus_supervisor',
            'specialists': [
                'differentiation_specialist',
                'integration_specialist',
                'limit_evaluator',
                'ode_solver',
                'series_specialist',
            ]
        },
        'linear_algebra': {
            'supervisor': 'linalg_supervisor',
            'specialists': [
                'matrix_ops_specialist',
                'decomposition_specialist',
                'vector_space_analyst',
            ]
        },
        'statistics': {
            'supervisor': 'stats_supervisor',
            'specialists': [
                'bayesian_engine',
                'distribution_specialist',
                'frequentist_agent',
            ]
        },
        'discrete_math': {
            'supervisor': 'discrete_math_supervisor',
            'specialists': [
                'graph_theory_agent',
                'combinatorics_agent',
            ]
        },
    }

    def __init__(self, ams: AgentManagementSystem):
        """
        Initialize agent pool.

        Args:
            ams: The Agent Management System for resource enforcement
        """
        self.ams = ams
        self._specs: Dict[str, AgentSpec] = {}
        self._agents: Dict[str, PooledAgent] = {}
        self._lock = threading.RLock()
        self._running = False
        self._cleanup_thread: Optional[threading.Thread] = None

        # Track which domains are currently "warm" (have standby agents)
        self._warm_domains: Set[str] = set()

        # Callbacks for lifecycle events
        self._on_activate: List[Callable[[str], None]] = []
        self._on_deactivate: List[Callable[[str], None]] = []

        logger.info("AgentPool initialized")

    def register_spec(self, spec: AgentSpec) -> bool:
        """
        Register an agent specification.

        The agent won't be instantiated until needed.

        Args:
            spec: Agent specification

        Returns:
            True if registered successfully
        """
        with self._lock:
            if spec.agent_id in self._specs:
                logger.warning(f"Agent {spec.agent_id} already registered")
                return False

            self._specs[spec.agent_id] = spec
            self._agents[spec.agent_id] = PooledAgent(spec=spec)

            logger.info(f"Registered agent spec: {spec.agent_id} "
                       f"(domain={spec.domain}, tier={spec.tier})")
            return True

    def get_state(self, agent_id: str) -> Optional[PoolState]:
        """Get current state of an agent"""
        with self._lock:
            if agent_id in self._agents:
                return self._agents[agent_id].state
            return None

    def wake_for_domain(self, domain: str) -> List[str]:
        """
        Wake all agents needed for a domain (DORMANT -> STANDBY).

        This doesn't activate them (no VRAM allocation), just prepares
        them for quick activation.

        Args:
            domain: Problem domain (e.g., 'algebra', 'calculus')

        Returns:
            List of agent IDs that were woken
        """
        woken = []

        with self._lock:
            # Find all registered agents for this domain
            domain_agents = [
                (aid, pooled) for aid, pooled in self._agents.items()
                if pooled.spec.domain == domain
            ]

            if not domain_agents:
                # Fallback to DOMAIN_AGENTS for backwards compatibility
                if domain not in self.DOMAIN_AGENTS:
                    logger.warning(f"Unknown domain: {domain}")
                    return []

                domain_config = self.DOMAIN_AGENTS[domain]
                # Wake supervisor first
                supervisor_id = domain_config['supervisor']
                if self._wake_agent(supervisor_id):
                    woken.append(supervisor_id)
                # Wake specialists
                for specialist_id in domain_config['specialists']:
                    if self._wake_agent(specialist_id):
                        woken.append(specialist_id)
            else:
                # Wake agents by tier (supervisors first, then specialists)
                domain_agents.sort(key=lambda x: x[1].spec.tier)
                for agent_id, _ in domain_agents:
                    if self._wake_agent(agent_id):
                        woken.append(agent_id)

            if woken:
                self._warm_domains.add(domain)

        logger.info(f"Woke {len(woken)} agents for domain '{domain}': {woken}")
        return woken

    def _wake_agent(self, agent_id: str) -> bool:
        """
        Wake a single agent from DORMANT to STANDBY.

        Creates instance but doesn't allocate VRAM.
        """
        if agent_id not in self._agents:
            logger.warning(f"Agent {agent_id} not registered")
            return False

        pooled = self._agents[agent_id]

        if pooled.state != PoolState.DORMANT:
            return False  # Already awake

        spec = pooled.spec

        try:
            # Create instance with minimal initialization
            instance = spec.agent_class(
                agent_id=spec.agent_id,
                **spec.init_args
            )

            pooled.instance = instance
            pooled.state = PoolState.STANDBY

            # Register with AMS (but don't activate)
            self.ams.create_agent(
                agent_id=spec.agent_id,
                agent_type=spec.agent_type,
                vram_req=spec.vram_requirement,
                ram_req=spec.ram_requirement,
                services=spec.services
            )

            logger.debug(f"Woke agent {agent_id}: DORMANT -> STANDBY")
            return True

        except Exception as e:
            logger.error(f"Failed to wake agent {agent_id}: {e}")
            return False

    def activate(self, agent_id: str) -> bool:
        """
        Activate an agent (STANDBY -> ACTIVE).

        For cognitive agents, this requests the VRAM slot from AMS.

        Args:
            agent_id: Agent to activate

        Returns:
            True if activated (or queued), False if failed
        """
        with self._lock:
            if agent_id not in self._agents:
                return False

            pooled = self._agents[agent_id]

            # Must be in standby to activate
            if pooled.state == PoolState.DORMANT:
                if not self._wake_agent(agent_id):
                    return False

            if pooled.state != PoolState.STANDBY:
                logger.warning(f"Cannot activate {agent_id} from state {pooled.state}")
                return False

            # Request activation from AMS
            if self.ams.activate_agent(agent_id):
                pooled.state = PoolState.ACTIVE
                pooled.last_active = datetime.now()
                pooled.activation_count += 1

                for callback in self._on_activate:
                    try:
                        callback(agent_id)
                    except Exception as e:
                        logger.error(f"Activation callback error: {e}")

                logger.info(f"Activated agent {agent_id}")
                return True
            else:
                # Agent was queued by AMS
                logger.info(f"Agent {agent_id} queued for activation")
                return True  # Still counts as success (will activate when slot available)

    def deactivate(self, agent_id: str, return_to_standby: bool = True) -> bool:
        """
        Deactivate an agent (ACTIVE -> STANDBY or DORMANT).

        Args:
            agent_id: Agent to deactivate
            return_to_standby: If True, stay in STANDBY; if False, go DORMANT

        Returns:
            True if deactivated successfully
        """
        with self._lock:
            if agent_id not in self._agents:
                return False

            pooled = self._agents[agent_id]

            if pooled.state != PoolState.ACTIVE:
                return False

            # Track active time
            if pooled.last_active:
                pooled.total_active_time += datetime.now() - pooled.last_active

            # Deactivate in AMS (frees VRAM slot)
            self.ams.deactivate_agent(agent_id)

            if return_to_standby:
                pooled.state = PoolState.STANDBY
                pooled.last_active = datetime.now()  # Track for standby timeout
            else:
                self._sleep_agent(agent_id)

            for callback in self._on_deactivate:
                try:
                    callback(agent_id)
                except Exception as e:
                    logger.error(f"Deactivation callback error: {e}")

            logger.info(f"Deactivated agent {agent_id} -> "
                       f"{'STANDBY' if return_to_standby else 'DORMANT'}")
            return True

    def _sleep_agent(self, agent_id: str) -> bool:
        """
        Return agent to DORMANT state (destroy instance).
        """
        if agent_id not in self._agents:
            return False

        pooled = self._agents[agent_id]

        if pooled.state == PoolState.DORMANT:
            return True  # Already dormant

        if pooled.state == PoolState.ACTIVE:
            self.deactivate(agent_id, return_to_standby=False)
            return True

        # Cleanup instance
        pooled.instance = None
        pooled.state = PoolState.DORMANT

        # Remove from AMS registry
        self.ams.kill_agent(agent_id)

        logger.debug(f"Slept agent {agent_id}: -> DORMANT")
        return True

    def sleep_domain(self, domain: str) -> int:
        """
        Return all agents in a domain to DORMANT state.

        Returns:
            Number of agents put to sleep
        """
        if domain not in self.DOMAIN_AGENTS:
            return 0

        domain_config = self.DOMAIN_AGENTS[domain]
        count = 0

        with self._lock:
            # Sleep specialists first
            for specialist_id in domain_config['specialists']:
                if self._sleep_agent(specialist_id):
                    count += 1

            # Sleep supervisor
            if self._sleep_agent(domain_config['supervisor']):
                count += 1

            self._warm_domains.discard(domain)

        logger.info(f"Slept {count} agents in domain '{domain}'")
        return count

    def get_active_agents(self) -> List[str]:
        """Get list of currently active agent IDs"""
        with self._lock:
            return [aid for aid, pooled in self._agents.items()
                   if pooled.state == PoolState.ACTIVE]

    def get_standby_agents(self) -> List[str]:
        """Get list of agents in standby state"""
        with self._lock:
            return [aid for aid, pooled in self._agents.items()
                   if pooled.state == PoolState.STANDBY]

    def get_warm_domains(self) -> Set[str]:
        """Get set of domains with agents in STANDBY or ACTIVE state"""
        return self._warm_domains.copy()

    def get_statistics(self) -> Dict:
        """Get pool statistics"""
        with self._lock:
            state_counts = {state.value: 0 for state in PoolState}
            domain_counts = {}

            for pooled in self._agents.values():
                state_counts[pooled.state.value] += 1

                domain = pooled.spec.domain
                if domain not in domain_counts:
                    domain_counts[domain] = {'dormant': 0, 'standby': 0, 'active': 0}
                domain_counts[domain][pooled.state.value] = \
                    domain_counts[domain].get(pooled.state.value, 0) + 1

            return {
                'total_registered': len(self._specs),
                'state_distribution': state_counts,
                'domain_distribution': domain_counts,
                'warm_domains': list(self._warm_domains),
                'ams_stats': self.ams.get_statistics()
            }

    def start(self):
        """Start the agent pool (and AMS if not running)"""
        self.ams.start()

        with self._lock:
            if not self._running:
                self._running = True
                self._cleanup_thread = threading.Thread(
                    target=self._cleanup_loop, daemon=True
                )
                self._cleanup_thread.start()

        logger.info("AgentPool started")

    def stop(self):
        """Stop the agent pool"""
        with self._lock:
            self._running = False

        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=2.0)

        # Sleep all agents
        for agent_id in list(self._agents.keys()):
            self._sleep_agent(agent_id)

        logger.info("AgentPool stopped")

    def _cleanup_loop(self):
        """
        Background loop to return idle STANDBY agents to DORMANT.

        Agents that haven't been used for their standby_timeout are
        put back to sleep to free memory.
        """
        while self._running:
            try:
                now = datetime.now()

                with self._lock:
                    for agent_id, pooled in self._agents.items():
                        if pooled.state != PoolState.STANDBY:
                            continue

                        if pooled.last_active is None:
                            continue

                        idle_time = now - pooled.last_active
                        timeout = timedelta(seconds=pooled.spec.standby_timeout_seconds)

                        if idle_time > timeout:
                            logger.debug(f"Agent {agent_id} standby timeout "
                                        f"({idle_time.total_seconds():.0f}s > "
                                        f"{timeout.total_seconds():.0f}s)")
                            self._sleep_agent(agent_id)

                # Check every 30 seconds
                import time
                time.sleep(30)

            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")


# Convenience function for problem-based activation
def activate_for_problem(pool: AgentPool, problem_domains: List[str]) -> Dict[str, List[str]]:
    """
    Activate agents needed for a problem based on its domains.

    Args:
        pool: The agent pool
        problem_domains: List of domains the problem requires
                        (e.g., ['algebra', 'calculus'])

    Returns:
        Dict mapping domain -> list of activated agent IDs
    """
    result = {}

    for domain in problem_domains:
        woken = pool.wake_for_domain(domain)
        result[domain] = woken

    return result


if __name__ == "__main__":
    """Demonstration of AgentPool"""
    print("=" * 70)
    print("AGENT POOL - Dynamic Lifecycle Management Demo")
    print("=" * 70)
    print()

    # Create AMS and Pool
    ams = AgentManagementSystem()
    pool = AgentPool(ams)
    pool.start()

    print("Initial state:")
    print(f"  Registered agents: {len(pool._specs)}")
    print(f"  Warm domains: {pool.get_warm_domains()}")
    print()

    # Note: In real usage, agent specs would be registered during startup
    # This demo just shows the concept

    print("Concept demonstration:")
    print("  1. Problem arrives: 'Solve x^2 + 2x - 3 = 0'")
    print("  2. Orchestrator classifies: domain = 'algebra'")
    print("  3. AgentPool.wake_for_domain('algebra')")
    print("     -> Algebra Supervisor: DORMANT -> STANDBY")
    print("     -> Polynomial Specialist: DORMANT -> STANDBY")
    print("     -> Other algebra specialists: DORMANT -> STANDBY")
    print("  4. Supervisor activates Polynomial Specialist")
    print("     -> Polynomial Specialist: STANDBY -> ACTIVE (gets VRAM)")
    print("  5. Problem solved, specialist deactivates")
    print("     -> Polynomial Specialist: ACTIVE -> STANDBY")
    print("  6. After 5 min idle, cleanup runs")
    print("     -> All algebra agents: STANDBY -> DORMANT")
    print()

    stats = pool.get_statistics()
    print("Statistics:")
    import json
    print(json.dumps(stats, indent=2))

    pool.stop()
    print()
    print("AgentPool demonstration complete")
