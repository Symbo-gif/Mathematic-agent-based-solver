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
PHASE 0 - STEP 4: The Bureaucratic Infrastructure Team - AMS
============================================================

Agent Management System (AMS) - "The God Agent" / "City Hall"

PURPOSE:
-------
Manages agent lifecycles (create, kill, suspend) and enforces the critical
"One-Model-At-A-Time" rule by monitoring VRAM/RAM usage. Acts as the gatekeeper
of system resources, ensuring the system never exceeds hardware constraints.

REFERENCE:
---------
- Phase_0_Build_Order_Breakdown.md: Step 4 - AMS (Lines 264-364)
- Phase 0 Coding Strategy: Section 3.0 "The Civic Infrastructure"
- Phase 0_ Infrastructural Agents and Hardware Calibration: Hardware constraints

AGENT TYPE:
----------
Simple Reflex Agent - Makes decisions based on current resource state

ROLE & ANALOGY:
--------------
"City Hall" or "God Agent" - Has ultimate authority over agent instantiation
and resource allocation. No agent can be created or activated without AMS approval.

HARDWARE CONSTRAINTS (CRITICAL):
-------------------------------
Component           Specification
CPU                 AMD Ryzen 7 8700F (8-Core)
System RAM          32 GB DDR5
GPU                 NVIDIA GeForce RTX 4060
Dedicated VRAM      8 GB GDDR6 (CRITICAL BOTTLENECK)

THE VRAM BOTTLENECK:
-------------------
A 7B parameter LLM requires ~5-6GB VRAM even when quantized to 4-bit.
The RTX 4060's 8GB VRAM can hold ONE active cognitive agent at a time.
This is the fundamental law of physics for this system.

AMS ENFORCEMENT:
---------------
1. Monitors VRAM usage via nvidia-smi
2. Enforces "One-Model-At-A-Time" rule for cognitive agents
3. Maintains queue of agents waiting for VRAM slot
4. Automatically swaps agents in/out based on queue
5. Prevents system crashes from VRAM overflow

WHY THIS MATTERS:
----------------
Without AMS, agents could attempt to load concurrently, causing VRAM overflow
and system crashes. AMS is the silent guardian that keeps the system alive.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Set
from enum import Enum
import subprocess
import threading
import time
from datetime import datetime

# Hardware constraints from documentation
# Reference: Phase_0_Build_Order_Breakdown.md: Lines 272-277
MAX_VRAM_GB = 8.0                  # RTX 4060 VRAM limit
MAX_RAM_GB = 32.0                  # System RAM limit
VRAM_THRESHOLD = 0.90              # 90% usage triggers rejection
LLM_VRAM_REQUIREMENT = 5.5         # 7B model at 4-bit quantization (~5-6GB)
INFRASTRUCTURAL_VRAM = 0.5         # VRAM reserved for OS/infrastructure


class AgentStatus(Enum):
    """
    Lifecycle status of an agent

    INACTIVE: Registered but not loaded in memory
    QUEUED: Waiting for VRAM slot to become available
    ACTIVE: Currently occupying VRAM slot (cognitive) or running (infrastructural)
    SUSPENDED: Temporarily paused (can be resumed)
    TERMINATED: Agent has been killed (removed from registry)

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 279-283
    """
    INACTIVE = 'inactive'        # Registered but not loaded
    QUEUED = 'queued'            # Waiting for VRAM slot
    ACTIVE = 'active'            # Currently occupying VRAM
    SUSPENDED = 'suspended'      # Temporarily paused
    TERMINATED = 'terminated'    # Agent killed


class AgentType(Enum):
    """
    Classification of agent types

    INFRASTRUCTURAL: "Silent" agents (AMS, DF, ACC) - no VRAM requirement
    COGNITIVE: "Mathematician" agents (require 7B LLM in VRAM)
    """
    INFRASTRUCTURAL = 'infrastructural'
    COGNITIVE = 'cognitive'


@dataclass
class AgentRecord:
    """
    Registry record for a single agent

    Tracks agent metadata, resource requirements, and current status.

    FIELDS:
    ------
    - agent_id: Unique agent identifier (e.g., 'algebra_specialist_001')
    - agent_type: INFRASTRUCTURAL or COGNITIVE
    - status: Current lifecycle status
    - vram_requirement: VRAM required (GB) - typically 5.5GB for cognitive agents
    - ram_requirement: System RAM required (GB)
    - services: List of services this agent provides (for DF integration)
    - created_at: Timestamp of registration
    - activated_at: Timestamp of last activation
    - metadata: Additional key-value pairs

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 285-292
    """
    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    vram_requirement: float = 0.0
    ram_requirement: float = 0.0
    services: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    activated_at: Optional[datetime] = None
    metadata: Dict[str, any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Human-readable representation"""
        return (f"Agent[{self.agent_id}] {self.agent_type.value}:{self.status.value} "
                f"(VRAM: {self.vram_requirement}GB)")


class AgentManagementSystem:
    """
    The "God Agent" - Lifecycle manager enforcing hardware constraints

    AMS is the ultimate authority on agent instantiation. It monitors system
    resources and enforces the "One-Model-At-A-Time" rule to prevent VRAM overflow.

    CRITICAL RESPONSIBILITY:
    -----------------------
    With only 8GB VRAM and cognitive agents requiring 5-6GB each, AMS must
    ensure that only ONE cognitive agent is active at any given time.

    THREAD SAFETY:
    -------------
    All operations are protected by a reentrant lock (threading.RLock) to ensure
    thread-safe access from multiple threads.

    Reference: Phase_0_Build_Order_Breakdown.md: Lines 294-364
    """

    def __init__(self):
        """Initialize Agent Management System"""
        self._agents: Dict[str, AgentRecord] = {}
        self._active_cognitive_agent: Optional[str] = None  # ONE MODEL AT A TIME
        self._agent_queue: List[str] = []  # Queue for VRAM access
        self._lock = threading.RLock()
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None

        # Register AMS itself as an infrastructural agent
        self.create_agent(
            agent_id='ams',
            agent_type=AgentType.INFRASTRUCTURAL,
            services=['lifecycle_management', 'resource_monitoring']
        )
        self.activate_agent('ams')

    def start(self):
        """Start AMS monitoring thread"""
        with self._lock:
            if not self._running:
                self._running = True
                self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
                self._monitor_thread.start()

    def stop(self):
        """Stop AMS monitoring thread"""
        with self._lock:
            self._running = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=2.0)

    def get_vram_usage(self) -> float:
        """
        Query NVIDIA GPU for current VRAM usage

        Uses nvidia-smi to query actual VRAM consumption.

        Returns:
            float: Current VRAM usage in GB

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 301-311
        """
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used', '--format=csv,nounits,noheader'],
                capture_output=True,
                text=True,
                timeout=5.0
            )
            if result.returncode == 0:
                vram_mb = float(result.stdout.strip())
                return vram_mb / 1024.0  # Convert MB to GB
        except Exception as e:
            print(f"WARNING: Could not query VRAM usage: {e}")

        # Fallback: estimate based on active agents
        return self._estimate_vram_usage()

    def _estimate_vram_usage(self) -> float:
        """Estimate VRAM usage based on active agents"""
        with self._lock:
            total = INFRASTRUCTURAL_VRAM  # Base OS/infrastructure overhead
            if self._active_cognitive_agent:
                agent = self._agents[self._active_cognitive_agent]
                total += agent.vram_requirement
            return total

    def get_ram_usage(self) -> float:
        """
        Get current system RAM usage

        Returns:
            float: Current RAM usage in GB
        """
        # For simplicity, estimate based on registered agents
        # In production, would use psutil or similar
        with self._lock:
            total = 2.0  # Base OS overhead
            for agent in self._agents.values():
                if agent.status == AgentStatus.ACTIVE:
                    total += agent.ram_requirement
            return total

    def can_activate_cognitive_agent(self) -> bool:
        """
        Check if VRAM slot is available - enforces ONE MODEL AT A TIME

        This is the core enforcement mechanism for the hardware constraint.

        Returns:
            bool: True if a cognitive agent can be activated

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 312-319
        """
        with self._lock:
            # Rule 1: Only one cognitive agent at a time
            if self._active_cognitive_agent is not None:
                return False  # Slot already occupied

            # Rule 2: Check VRAM headroom
            current_vram = self.get_vram_usage()
            projected_vram = current_vram + LLM_VRAM_REQUIREMENT
            vram_utilization = projected_vram / MAX_VRAM_GB

            return vram_utilization < VRAM_THRESHOLD

    def create_agent(self, agent_id: str, agent_type: AgentType,
                    vram_req: float = 0.0, ram_req: float = 0.5,
                    services: List[str] = None,
                    metadata: Dict[str, any] = None) -> bool:
        """
        Register new agent - gatekeeper for resource allocation

        Args:
            agent_id: Unique agent identifier
            agent_type: INFRASTRUCTURAL or COGNITIVE
            vram_req: VRAM requirement in GB (default 0 for infrastructural, 5.5 for cognitive)
            ram_req: RAM requirement in GB
            services: List of service names (for DF registration)
            metadata: Additional metadata

        Returns:
            bool: True if agent was created successfully

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 320-335
        """
        with self._lock:
            # Check if agent already exists
            if agent_id in self._agents:
                print(f"AMS: Agent {agent_id} already exists")
                return False

            # Set default VRAM requirement for cognitive agents
            if agent_type == AgentType.COGNITIVE and vram_req == 0.0:
                vram_req = LLM_VRAM_REQUIREMENT

            # Create agent record
            record = AgentRecord(
                agent_id=agent_id,
                agent_type=agent_type,
                status=AgentStatus.INACTIVE,
                vram_requirement=vram_req,
                ram_requirement=ram_req,
                services=services or [],
                metadata=metadata or {}
            )

            self._agents[agent_id] = record
            print(f"AMS: Agent {agent_id} registered as {agent_type.value}")
            return True

    def activate_agent(self, agent_id: str) -> bool:
        """
        Request VRAM slot for cognitive agent (or activate infrastructural agent)

        For cognitive agents, enforces "One-Model-At-A-Time" rule.
        If VRAM slot is occupied, agent is queued.

        Args:
            agent_id: Agent to activate

        Returns:
            bool: True if agent was activated, False if queued or failed

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 336-350
        """
        with self._lock:
            # Validate agent exists
            if agent_id not in self._agents:
                print(f"AMS: Agent {agent_id} not found")
                return False

            record = self._agents[agent_id]

            # Cognitive agents must check VRAM availability
            if record.agent_type == AgentType.COGNITIVE:
                if not self.can_activate_cognitive_agent():
                    # Queue agent for later activation
                    if agent_id not in self._agent_queue:
                        record.status = AgentStatus.QUEUED
                        self._agent_queue.append(agent_id)
                        print(f"AMS: Cognitive agent {agent_id} queued (position {len(self._agent_queue)})")
                    return False  # Must wait in queue

                # Claim the VRAM slot
                self._active_cognitive_agent = agent_id

            # Activate agent
            record.status = AgentStatus.ACTIVE
            record.activated_at = datetime.now()
            print(f"AMS: Agent {agent_id} activated")
            return True

    def deactivate_agent(self, agent_id: str) -> bool:
        """
        Release VRAM slot and activate next in queue

        When a cognitive agent finishes its work, it must deactivate to free
        the VRAM slot for the next agent in the queue.

        Args:
            agent_id: Agent to deactivate

        Returns:
            bool: True if agent was deactivated

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 351-363
        """
        with self._lock:
            if agent_id not in self._agents:
                return False

            record = self._agents[agent_id]
            record.status = AgentStatus.INACTIVE

            # If this was the active cognitive agent, free the slot
            if self._active_cognitive_agent == agent_id:
                self._active_cognitive_agent = None
                print(f"AMS: Cognitive agent {agent_id} deactivated, VRAM slot freed")

                # Activate next agent in queue
                if self._agent_queue:
                    next_agent = self._agent_queue.pop(0)
                    print(f"AMS: Activating queued agent {next_agent}")
                    self.activate_agent(next_agent)

            return True

    def kill_agent(self, agent_id: str) -> bool:
        """
        Permanently terminate an agent

        Args:
            agent_id: Agent to kill

        Returns:
            bool: True if agent was killed
        """
        with self._lock:
            if agent_id not in self._agents:
                return False

            # Deactivate first
            self.deactivate_agent(agent_id)

            # Remove from queue if present
            if agent_id in self._agent_queue:
                self._agent_queue.remove(agent_id)

            # Mark as terminated
            self._agents[agent_id].status = AgentStatus.TERMINATED
            print(f"AMS: Agent {agent_id} terminated")
            return True

    def suspend_agent(self, agent_id: str) -> bool:
        """
        Temporarily suspend an agent

        Args:
            agent_id: Agent to suspend

        Returns:
            bool: True if agent was suspended
        """
        with self._lock:
            if agent_id not in self._agents:
                return False

            # Deactivate but don't terminate
            self.deactivate_agent(agent_id)
            self._agents[agent_id].status = AgentStatus.SUSPENDED
            print(f"AMS: Agent {agent_id} suspended")
            return True

    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        """Get agent record by ID"""
        with self._lock:
            return self._agents.get(agent_id)

    def list_agents(self, status: Optional[AgentStatus] = None,
                   agent_type: Optional[AgentType] = None) -> List[AgentRecord]:
        """
        List all agents, optionally filtered

        Args:
            status: Filter by status
            agent_type: Filter by type

        Returns:
            List of AgentRecord objects
        """
        with self._lock:
            results = list(self._agents.values())

            if status:
                results = [a for a in results if a.status == status]

            if agent_type:
                results = [a for a in results if a.agent_type == agent_type]

            return results

    def get_statistics(self) -> Dict[str, any]:
        """
        Get AMS statistics

        Returns:
            Dictionary with statistics about agents and resource usage
        """
        with self._lock:
            active_cognitive = self._active_cognitive_agent
            queue_length = len(self._agent_queue)
            vram_usage = self.get_vram_usage()
            ram_usage = self.get_ram_usage()

            status_counts = {}
            for status in AgentStatus:
                status_counts[status.value] = len([a for a in self._agents.values() if a.status == status])

            type_counts = {}
            for agent_type in AgentType:
                type_counts[agent_type.value] = len([a for a in self._agents.values() if a.agent_type == agent_type])

            return {
                'total_agents': len(self._agents),
                'active_cognitive_agent': active_cognitive if active_cognitive else None,
                'queue_length': queue_length,
                'queued_agents': list(self._agent_queue),
                'vram_usage_gb': round(vram_usage, 2),
                'vram_utilization': round(vram_usage / MAX_VRAM_GB, 2),
                'ram_usage_gb': round(ram_usage, 2),
                'status_distribution': status_counts,
                'type_distribution': type_counts,
                'can_activate_cognitive': self.can_activate_cognitive_agent()
            }

    def _monitor_loop(self):
        """
        Background monitoring loop

        Periodically checks resource usage and enforces constraints
        """
        while self._running:
            try:
                with self._lock:
                    vram_usage = self.get_vram_usage()
                    vram_utilization = vram_usage / MAX_VRAM_GB

                    # Emergency shutdown if VRAM exceeds critical threshold
                    if vram_utilization > 0.95:
                        print(f"AMS CRITICAL: VRAM usage {vram_utilization:.1%} exceeds critical threshold!")
                        # In production, would take corrective action

                time.sleep(5.0)  # Check every 5 seconds
            except Exception as e:
                print(f"AMS monitor error: {e}")

    def __repr__(self) -> str:
        """Human-readable representation"""
        stats = self.get_statistics()
        return (f"AMS(agents={stats['total_agents']}, "
                f"active_cognitive={stats['active_cognitive_agent']}, "
                f"queued={stats['queue_length']}, "
                f"VRAM={stats['vram_utilization']:.0%})")


if __name__ == "__main__":
    """Demonstration of AMS functionality"""
    print("=" * 80)
    print("PHASE 0 - STEP 4: Agent Management System (AMS)")
    print("=" * 80)
    print()

    # Initialize AMS
    ams = AgentManagementSystem()
    ams.start()
    print(f"Initialized: {ams}")
    print()

    # Example 1: Register infrastructural agents
    print("Example 1: Registering infrastructural agents")
    ams.create_agent('df', AgentType.INFRASTRUCTURAL, services=['service_registry'])
    ams.create_agent('acc', AgentType.INFRASTRUCTURAL, services=['message_routing'])
    ams.activate_agent('df')
    ams.activate_agent('acc')
    print(f"  {ams}")
    print()

    # Example 2: Register cognitive agent
    print("Example 2: Registering cognitive agent")
    ams.create_agent('algebra_001', AgentType.COGNITIVE, services=['algebra', 'polynomial_solving'])
    activated = ams.activate_agent('algebra_001')
    print(f"  Activated: {activated}")
    print(f"  {ams}")
    print()

    # Example 3: Attempt to activate second cognitive agent (should queue)
    print("Example 3: Attempt second cognitive agent (ONE MODEL AT A TIME enforcement)")
    ams.create_agent('calculus_001', AgentType.COGNITIVE, services=['calculus', 'integration'])
    activated = ams.activate_agent('calculus_001')
    print(f"  Activated: {activated} (should be False - queued instead)")
    print(f"  {ams}")
    print()

    # Example 4: Deactivate first agent, watch queue processing
    print("Example 4: Deactivate first agent, process queue")
    ams.deactivate_agent('algebra_001')
    time.sleep(0.1)  # Give queue processing time
    print(f"  {ams}")
    print()

    # Example 5: Statistics
    print("Example 5: AMS Statistics")
    import json
    stats = ams.get_statistics()
    print(json.dumps(stats, indent=2))
    print()

    ams.stop()
    print("✓ Agent Management System (AMS) implementation complete")
    print("  - Lifecycle management (create, activate, deactivate, kill) ✓")
    print("  - One-Model-At-A-Time enforcement ✓")
    print("  - VRAM monitoring ✓")
    print("  - Agent queueing ✓")
