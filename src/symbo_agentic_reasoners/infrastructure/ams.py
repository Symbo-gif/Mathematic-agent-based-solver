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
from typing import Dict, Optional, List, Set, Callable, Any
from enum import Enum
import subprocess
import threading
import time
import logging
import os
import json
from datetime import datetime
from pathlib import Path

# Try to import psutil for system monitoring
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Import agent authentication system (Phase 5 - Issue #4)
from symbo_agentic_reasoners.infrastructure.security.agent_auth import AgentAuthenticator

# Setup logging for resource events
logger = logging.getLogger('symbo_agentic_reasoners.ams')

# Import centralized configuration
try:
    from symbo_agentic_reasoners.config import get_config
    _config = get_config()

    # Hardware constraints from configuration
    MAX_VRAM_GB = _config.hardware.max_vram_gb
    MAX_RAM_GB = _config.hardware.max_ram_gb
    MAX_CPU_CORES = _config.hardware.max_cpu_cores

    # Threshold levels from configuration
    VRAM_THRESHOLD = _config.thresholds.vram_threshold
    VRAM_WARNING_THRESHOLD = _config.thresholds.vram_warning
    VRAM_CRITICAL_THRESHOLD = _config.thresholds.vram_critical
    VRAM_EMERGENCY_THRESHOLD = _config.thresholds.vram_emergency

    RAM_THRESHOLD = _config.thresholds.ram_threshold
    RAM_CRITICAL_THRESHOLD = _config.thresholds.ram_critical
    RAM_EMERGENCY_THRESHOLD = _config.thresholds.ram_emergency

    CPU_THRESHOLD = _config.thresholds.cpu_threshold
    CPU_CRITICAL_THRESHOLD = _config.thresholds.cpu_critical

    LLM_VRAM_REQUIREMENT = _config.hardware.llm_vram_requirement_gb
    INFRASTRUCTURAL_VRAM = _config.hardware.infrastructural_vram_gb

    logger.info("AMS: Loaded configuration from centralized config system")

except ImportError:
    # Fallback to defaults if config module not available
    logger.warning("AMS: Config module not available, using default values")

    # Hardware constraints (defaults for RTX 4060 + 32GB RAM + 8-core CPU)
    MAX_VRAM_GB = 8.0
    MAX_RAM_GB = 32.0
    MAX_CPU_CORES = 8

    # Threshold levels
    VRAM_THRESHOLD = 0.90
    VRAM_WARNING_THRESHOLD = 0.85
    VRAM_CRITICAL_THRESHOLD = 0.95
    VRAM_EMERGENCY_THRESHOLD = 0.98

    RAM_THRESHOLD = 0.85
    RAM_CRITICAL_THRESHOLD = 0.92
    RAM_EMERGENCY_THRESHOLD = 0.95

    CPU_THRESHOLD = 0.90
    CPU_CRITICAL_THRESHOLD = 0.95

    LLM_VRAM_REQUIREMENT = 5.5
    INFRASTRUCTURAL_VRAM = 0.5

# Emergency state tracking
class EmergencyLevel(Enum):
    """System emergency levels"""
    NORMAL = 0           # All systems nominal
    WARNING = 1          # Approaching limits, throttling active
    CRITICAL = 2         # At limits, new activations blocked
    EMERGENCY = 3        # Over limits, emergency shutdown in progress
    SHUTDOWN = 4         # System shutting down


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
    metadata: Dict[str, Any] = field(default_factory=dict)

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

    def __init__(self, error_log_dir: Optional[str] = None):
        """
        Initialize Agent Management System

        Args:
            error_log_dir: Directory for error logs. Defaults to data/traces/error/
        """
        self._agents: Dict[str, AgentRecord] = {}
        self._active_cognitive_agent: Optional[str] = None  # ONE MODEL AT A TIME
        self._agent_queue: List[str] = []  # Queue for VRAM access
        self._lock = threading.RLock()
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None

        # Emergency state tracking
        self._emergency_level = EmergencyLevel.NORMAL
        self._emergency_callbacks: List[Callable[[EmergencyLevel, Dict], None]] = []
        self._last_emergency_action = None
        self._throttle_active = False

        # Resource history for trend detection
        self._cpu_history: List[float] = []
        self._ram_history: List[float] = []
        self._vram_history: List[float] = []
        self._history_max_size = 12  # 1 minute of history at 5s intervals

        # Error logging setup
        self._error_log_dir = Path(error_log_dir) if error_log_dir else Path("data/traces/error")
        self._error_log_dir.mkdir(parents=True, exist_ok=True)
        self._error_log_file = self._error_log_dir / f"ams_errors_{datetime.now().strftime('%Y%m%d')}.jsonl"

        # Sustained high resource counters (for avoiding single-spike reactions)
        self._sustained_cpu_high_count = 0
        self._sustained_ram_high_count = 0
        self._sustained_vram_high_count = 0
        self._sustained_threshold = 3  # Must be high for 3 consecutive checks

        # Phase 5 - Issue #4: Agent Authentication System
        # Initialize HMAC-based authenticator for agent identity verification
        self.authenticator = AgentAuthenticator(enable_auth=True)
        logger.info("AMS: Agent authentication system initialized")

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
            logger.warning(f"Could not query VRAM usage: {e}")

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
        Get current system RAM usage using psutil

        Returns:
            float: Current RAM usage in GB
        """
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                return mem.used / (1024 ** 3)  # Convert bytes to GB
            except Exception as e:
                logger.warning(f"Could not query RAM usage: {e}")

        # Fallback: estimate based on registered agents
        with self._lock:
            total = 2.0  # Base OS overhead
            for agent in self._agents.values():
                if agent.status == AgentStatus.ACTIVE:
                    total += agent.ram_requirement
            return total

    def get_ram_utilization(self) -> float:
        """
        Get RAM utilization as a percentage (0.0-1.0)

        Returns:
            float: RAM utilization ratio
        """
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                return mem.percent / 100.0
            except Exception as e:
                logger.warning(f"Could not query RAM utilization: {e}")

        return self.get_ram_usage() / MAX_RAM_GB

    def get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage using psutil

        Returns:
            float: CPU usage as ratio (0.0-1.0)
        """
        if HAS_PSUTIL:
            try:
                # Use interval=None for non-blocking (uses cached value)
                # First call may return 0.0, subsequent calls are accurate
                return psutil.cpu_percent(interval=None) / 100.0
            except Exception as e:
                logger.warning(f"Could not query CPU usage: {e}")

        # Fallback: estimate based on active agents
        with self._lock:
            active_count = len([a for a in self._agents.values()
                              if a.status == AgentStatus.ACTIVE])
            # Rough estimate: each active agent uses ~10% CPU
            return min(active_count * 0.1, 1.0)

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
                    metadata: Dict[str, Any] = None,
                    auth_token: Optional[str] = None,
                    auth_timestamp: Optional[int] = None) -> bool:
        """
        Register new agent - gatekeeper for resource allocation

        Phase 5 - Issue #4: Now includes agent authentication verification.

        Args:
            agent_id: Unique agent identifier
            agent_type: INFRASTRUCTURAL or COGNITIVE
            vram_req: VRAM requirement in GB (default 0 for infrastructural, 5.5 for cognitive)
            ram_req: RAM requirement in GB
            services: List of service names (for DF registration)
            metadata: Additional metadata
            auth_token: Optional HMAC authentication token (Issue #4)
            auth_timestamp: Optional token timestamp (Issue #4)

        Returns:
            bool: True if agent was created successfully

        Security:
            If auth_token and auth_timestamp provided, verifies agent identity
            before registration. Prevents agent spoofing attacks.

        Reference: Phase_0_Build_Order_Breakdown.md: Lines 320-335
        """
        with self._lock:
            # Phase 5 - Issue #4: Verify agent credentials if provided
            if auth_token is not None and auth_timestamp is not None:
                if not self.authenticator.verify_credential(
                    agent_id, auth_token, auth_timestamp
                ):
                    logger.warning(
                        f"Agent creation DENIED (authentication failed): {agent_id}"
                    )
                    return False
                logger.debug(f"Agent authentication verified: {agent_id}")

            # Check if agent already exists
            if agent_id in self._agents:
                logger.warning(f"Agent {agent_id} already exists")
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
            logger.info(f"Agent {agent_id} registered as {agent_type.value}")
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
                logger.warning(f"Agent {agent_id} not found")
                return False

            record = self._agents[agent_id]

            # Cognitive agents must check VRAM availability
            if record.agent_type == AgentType.COGNITIVE:
                if not self.can_activate_cognitive_agent():
                    # Queue agent for later activation
                    if agent_id not in self._agent_queue:
                        record.status = AgentStatus.QUEUED
                        self._agent_queue.append(agent_id)
                        logger.info(f"Cognitive agent {agent_id} queued (position {len(self._agent_queue)})")
                    return False  # Must wait in queue

                # Claim the VRAM slot
                self._active_cognitive_agent = agent_id

            # Activate agent
            record.status = AgentStatus.ACTIVE
            record.activated_at = datetime.now()
            logger.info(f"Agent {agent_id} activated")
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
                logger.info(f"Cognitive agent {agent_id} deactivated, VRAM slot freed")

                # Activate next agent in queue
                if self._agent_queue:
                    next_agent = self._agent_queue.pop(0)
                    logger.info(f"Activating queued agent {next_agent}")
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
            logger.info(f"Agent {agent_id} terminated")
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
            logger.info(f"Agent {agent_id} suspended")
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

    # =========================================================================
    # PHASE 5 - ISSUE #4: AGENT AUTHENTICATION METHODS
    # =========================================================================

    def issue_agent_credential(self, agent_id: str) -> 'AgentCredential':
        """
        Issue authentication credential for agent.

        Phase 5 - Issue #4: Helper method for agents to obtain credentials
        before registration.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentCredential with HMAC token

        Example:
            credential = ams.issue_agent_credential('agent_001')
            ams.create_agent(
                agent_id='agent_001',
                agent_type=AgentType.COGNITIVE,
                auth_token=credential.token,
                auth_timestamp=credential.timestamp
            )
        """
        return self.authenticator.issue_credential(agent_id)

    def revoke_agent_credential(self, agent_id: str) -> bool:
        """
        Revoke agent authentication credential.

        Phase 5 - Issue #4: Invalidates agent's credential, preventing
        future authentication.

        Args:
            agent_id: Agent identifier

        Returns:
            True if credential was revoked
        """
        return self.authenticator.revoke_credential(agent_id)

    # =========================================================================

    def get_statistics(self) -> Dict[str, Any]:
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
                'ram_utilization': round(self.get_ram_utilization(), 2),
                'cpu_utilization': round(self.get_cpu_usage(), 2),
                'emergency_level': self._emergency_level.name,
                'throttled': self._throttle_active,
                'status_distribution': status_counts,
                'type_distribution': type_counts,
                'can_activate_cognitive': self.can_activate_cognitive_agent(),
                'psutil_available': HAS_PSUTIL,
                # Phase 5 - Issue #4: Authentication statistics
                'authentication': self.authenticator.get_statistics()
            }

    def _monitor_loop(self):
        """
        Background monitoring loop with emergency response

        Periodically checks resource usage, tracks trends, and takes
        corrective action when thresholds are exceeded.

        EMERGENCY RESPONSE LEVELS:
        - WARNING (85%): Log warning, enable throttling
        - CRITICAL (95%): Block new activations, attempt graceful reduction
        - EMERGENCY (98%): Force-terminate cognitive agents, save state
        """
        while self._running:
            try:
                # Gather all resource metrics
                vram_usage = self.get_vram_usage()
                vram_utilization = vram_usage / MAX_VRAM_GB
                ram_utilization = self.get_ram_utilization()
                cpu_utilization = self.get_cpu_usage()

                # Update history for trend detection
                self._update_resource_history(vram_utilization, ram_utilization, cpu_utilization)

                # Determine emergency level based on all resources
                new_level = self._calculate_emergency_level(
                    vram_utilization, ram_utilization, cpu_utilization
                )

                # Take action if emergency level changed or is elevated
                if new_level != self._emergency_level or new_level.value >= EmergencyLevel.CRITICAL.value:
                    self._handle_emergency_level_change(
                        new_level, vram_utilization, ram_utilization, cpu_utilization
                    )

                time.sleep(5.0)  # Check every 5 seconds

            except Exception as e:
                self._log_error("monitor_loop_error", str(e), {"exception_type": type(e).__name__})
                logger.error(f"AMS monitor error: {e}")

    def _update_resource_history(self, vram: float, ram: float, cpu: float):
        """Update resource history for trend detection"""
        self._vram_history.append(vram)
        self._ram_history.append(ram)
        self._cpu_history.append(cpu)

        # Trim to max size
        if len(self._vram_history) > self._history_max_size:
            self._vram_history.pop(0)
        if len(self._ram_history) > self._history_max_size:
            self._ram_history.pop(0)
        if len(self._cpu_history) > self._history_max_size:
            self._cpu_history.pop(0)

    def _calculate_emergency_level(self, vram: float, ram: float, cpu: float) -> EmergencyLevel:
        """
        Calculate current emergency level based on resource utilization

        Uses sustained high counters to avoid reacting to single spikes.
        """
        # Track sustained high conditions
        if vram >= VRAM_CRITICAL_THRESHOLD:
            self._sustained_vram_high_count += 1
        else:
            self._sustained_vram_high_count = max(0, self._sustained_vram_high_count - 1)

        if ram >= RAM_CRITICAL_THRESHOLD:
            self._sustained_ram_high_count += 1
        else:
            self._sustained_ram_high_count = max(0, self._sustained_ram_high_count - 1)

        if cpu >= CPU_CRITICAL_THRESHOLD:
            self._sustained_cpu_high_count += 1
        else:
            self._sustained_cpu_high_count = max(0, self._sustained_cpu_high_count - 1)

        # EMERGENCY: Any resource at emergency threshold (immediate action)
        if vram >= VRAM_EMERGENCY_THRESHOLD or ram >= RAM_EMERGENCY_THRESHOLD:
            return EmergencyLevel.EMERGENCY

        # CRITICAL: Sustained high on any critical resource
        if (self._sustained_vram_high_count >= self._sustained_threshold or
            self._sustained_ram_high_count >= self._sustained_threshold):
            return EmergencyLevel.CRITICAL

        # WARNING: Any resource above warning threshold
        if (vram >= VRAM_WARNING_THRESHOLD or
            ram >= RAM_THRESHOLD or
            cpu >= CPU_THRESHOLD):
            return EmergencyLevel.WARNING

        return EmergencyLevel.NORMAL

    def _handle_emergency_level_change(self, new_level: EmergencyLevel,
                                       vram: float, ram: float, cpu: float):
        """Handle emergency level transitions with appropriate actions"""
        old_level = self._emergency_level
        self._emergency_level = new_level

        context = {
            "vram_utilization": round(vram, 3),
            "ram_utilization": round(ram, 3),
            "cpu_utilization": round(cpu, 3),
            "old_level": old_level.name,
            "new_level": new_level.name,
            "active_cognitive_agent": self._active_cognitive_agent,
            "queue_length": len(self._agent_queue)
        }

        if new_level == EmergencyLevel.NORMAL:
            if old_level != EmergencyLevel.NORMAL:
                logger.info("Resource levels returned to NORMAL")
                self._log_event("emergency_cleared", context)
                self._throttle_active = False

        elif new_level == EmergencyLevel.WARNING:
            logger.warning(f"Resources elevated - VRAM:{vram:.1%} RAM:{ram:.1%} CPU:{cpu:.1%}")
            self._log_event("warning_threshold", context)
            self._throttle_active = True

        elif new_level == EmergencyLevel.CRITICAL:
            logger.error(f"Resources at limit - VRAM:{vram:.1%} RAM:{ram:.1%} CPU:{cpu:.1%}")
            self._log_error("critical_threshold", "Resource critical threshold exceeded", context)
            self._throttle_active = True
            # Block new activations (already handled by can_activate checks)

        elif new_level == EmergencyLevel.EMERGENCY:
            logger.critical(f"Initiating emergency response - VRAM:{vram:.1%} RAM:{ram:.1%}")
            self._log_error("emergency_shutdown", "Emergency shutdown initiated", context)
            self._execute_emergency_shutdown(context)

        # Notify callbacks
        for callback in self._emergency_callbacks:
            try:
                callback(new_level, context)
            except Exception as e:
                logger.error(f"Emergency callback error: {e}")

    def _execute_emergency_shutdown(self, context: Dict):
        """
        Execute emergency shutdown sequence

        1. Save current state
        2. Force-terminate all cognitive agents
        3. Clear queue
        4. Log for post-mortem
        """
        logger.critical("=" * 60)
        logger.critical("EMERGENCY SHUTDOWN SEQUENCE INITIATED")
        logger.critical("=" * 60)

        with self._lock:
            # Step 1: Save state before shutdown
            shutdown_state = {
                "timestamp": datetime.now().isoformat(),
                "trigger_context": context,
                "active_cognitive_agent": self._active_cognitive_agent,
                "queued_agents": list(self._agent_queue),
                "all_agents": {
                    aid: {
                        "type": a.agent_type.name,
                        "status": a.status.name,
                        "vram_req": a.vram_requirement
                    }
                    for aid, a in self._agents.items()
                }
            }

            # Save state to file
            state_file = self._error_log_dir / f"emergency_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(state_file, 'w') as f:
                    json.dump(shutdown_state, f, indent=2)
                logger.info(f"[SAVED] Emergency state to {state_file}")
            except Exception as e:
                logger.error(f"[ERROR] Could not save state: {e}")

            # Step 2: Force-terminate cognitive agent if active
            if self._active_cognitive_agent:
                agent_id = self._active_cognitive_agent
                logger.warning(f"[TERMINATING] Cognitive agent: {agent_id}")
                try:
                    self.kill_agent(agent_id)
                    logger.info(f"[OK] Agent {agent_id} terminated")
                except Exception as e:
                    logger.error(f"[ERROR] Could not terminate {agent_id}: {e}")

            # Step 3: Clear the queue
            cleared_count = len(self._agent_queue)
            for agent_id in list(self._agent_queue):
                if agent_id in self._agents:
                    self._agents[agent_id].status = AgentStatus.SUSPENDED
            self._agent_queue.clear()
            logger.info(f"[CLEARED] {cleared_count} agents from queue (suspended)")

            # Step 4: Update emergency level
            self._last_emergency_action = datetime.now()

        logger.critical("=" * 60)
        logger.critical("EMERGENCY SHUTDOWN COMPLETE")
        logger.critical("  System is now in reduced capacity mode")
        logger.critical("  Manual intervention may be required")
        logger.critical("=" * 60)

    def register_emergency_callback(self, callback: Callable[[EmergencyLevel, Dict], None]):
        """
        Register a callback to be notified of emergency level changes

        Args:
            callback: Function taking (EmergencyLevel, context_dict)
        """
        self._emergency_callbacks.append(callback)

    def _log_event(self, event_type: str, context: Dict):
        """Log a resource event to the log file"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "level": "INFO",
            "context": context
        }
        self._write_log_entry(entry)

    def _log_error(self, error_type: str, message: str, context: Dict):
        """Log an error to the error log file"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "level": "ERROR",
            "message": message,
            "context": context
        }
        self._write_log_entry(entry)
        logger.error(f"AMS {error_type}: {message}")

    def _write_log_entry(self, entry: Dict):
        """Write a log entry to the JSONL file"""
        try:
            with open(self._error_log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Could not write to error log: {e}")

    def get_emergency_level(self) -> EmergencyLevel:
        """Get current emergency level"""
        return self._emergency_level

    def is_throttled(self) -> bool:
        """Check if system is in throttled mode"""
        return self._throttle_active

    def get_resource_snapshot(self) -> Dict:
        """
        Get a snapshot of all current resource utilization

        Returns:
            Dict with vram, ram, cpu utilization and emergency level
        """
        vram = self.get_vram_usage() / MAX_VRAM_GB
        ram = self.get_ram_utilization()
        cpu = self.get_cpu_usage()

        return {
            "vram_utilization": round(vram, 3),
            "ram_utilization": round(ram, 3),
            "cpu_utilization": round(cpu, 3),
            "vram_gb": round(self.get_vram_usage(), 2),
            "ram_gb": round(self.get_ram_usage(), 2),
            "emergency_level": self._emergency_level.name,
            "throttled": self._throttle_active,
            "active_cognitive_agent": self._active_cognitive_agent,
            "queue_length": len(self._agent_queue)
        }

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
