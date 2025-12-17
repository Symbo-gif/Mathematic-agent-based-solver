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
SYMBO_AGENTIC_REASONERS Infrastructure

Core infrastructure components including:
- AMS: Agent Management System (VRAM/lifecycle)
- Watchdog: Operation timeout system
- ResourceGovernor: Unified resource management
- DirectoryFacilitator: Service registry
- ACC: Agent Communication Channel
"""
from .ams import (
    AgentManagementSystem, AgentRecord, AgentStatus, AgentType,
    EmergencyLevel, MAX_VRAM_GB, MAX_RAM_GB, VRAM_THRESHOLD
)
from .directory_facilitator import (
    DirectoryFacilitator, ServiceRegistration, create_service_registration
)
from .acc import AgentCommunicationChannel, MessageEnvelope
from .watchdog import (
    Watchdog, WatchedTask, TaskStatus, TimeoutError,
    with_timeout, get_watchdog
)
from .resource_governor import (
    ResourceGovernor, ResourceStatus, ThrottleLevel, get_governor
)
from .agent_pool import (
    AgentPool, AgentSpec, PooledAgent, PoolState, activate_for_problem
)
from .agent_registry import (
    register_all_agents, register_domain, get_domain_agents, get_all_domains,
    AGENT_SPECS
)

__all__ = [
    # AMS
    "AgentManagementSystem", "AgentRecord", "AgentStatus", "AgentType",
    "EmergencyLevel", "MAX_VRAM_GB", "MAX_RAM_GB", "VRAM_THRESHOLD",
    # Directory Facilitator
    "DirectoryFacilitator", "ServiceRegistration", "create_service_registration",
    # ACC
    "AgentCommunicationChannel", "MessageEnvelope",
    # Watchdog
    "Watchdog", "WatchedTask", "TaskStatus", "TimeoutError",
    "with_timeout", "get_watchdog",
    # Resource Governor
    "ResourceGovernor", "ResourceStatus", "ThrottleLevel", "get_governor",
    # Agent Pool
    "AgentPool", "AgentSpec", "PooledAgent", "PoolState", "activate_for_problem",
    # Agent Registry
    "register_all_agents", "register_domain", "get_domain_agents", "get_all_domains",
    "AGENT_SPECS"
]
