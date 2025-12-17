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
IDENTITY MANAGER (IAM Agent)
============================

Step 4 of Phase 5 Build Order: Operational Hardening

OBJECTIVE:
---------
Assign unique Agent Identities to every sub-agent in the system, treating
agents as "First-Class Principals" with enforced access controls.

SECURITY PRINCIPLES:
-------------------
1. Least-Privilege Access: Each agent can only access resources explicitly
   required for its function

2. Domain Isolation: The "Graph Theory Agent" cannot access memory logs
   of the "Financial Optimization Agent"

3. Audit Trail: All inter-agent communications logged with principal
   identities

IDENTITY STRUCTURE:
-----------------
Each agent receives:
- Unique ID (UUID)
- Domain classification
- Access level (Tier 1-3)
- Capability set (what operations allowed)
- Creation timestamp
- Status (active/suspended)

REFERENCE:
---------
- Phase_5_Build_Order_Breakdown.md: Section 5.2.2
"""

import os
import sys
import uuid
from enum import Enum
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class AccessLevel(Enum):
    """Agent access levels (Tier-based)"""
    TIER_1 = "tier_1"  # Orchestrator level - can access all domains
    TIER_2 = "tier_2"  # Supervisor level - can access own domain + children
    TIER_3 = "tier_3"  # Specialist level - can access own capabilities only
    SYSTEM = "system"  # System-level access (AMS, DF, ACC)


class AgentStatus(Enum):
    """Agent status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


@dataclass
class AgentIdentity:
    """
    Unique identity for an agent in the system.

    Every agent is treated as a "First-Class Principal" with
    specific access rights and capabilities.
    """
    agent_id: str
    agent_name: str
    agent_type: str
    domain: str
    access_level: AccessLevel
    capabilities: Set[str]
    created_at: datetime
    status: AgentStatus = AgentStatus.ACTIVE
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def can_access(self, resource_domain: str) -> bool:
        """Check if agent can access a resource domain"""
        if self.access_level == AccessLevel.SYSTEM:
            return True
        if self.access_level == AccessLevel.TIER_1:
            return True
        if self.access_level == AccessLevel.TIER_2:
            return resource_domain == self.domain or resource_domain == "shared"
        if self.access_level == AccessLevel.TIER_3:
            return resource_domain == self.domain
        return False

    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities or "*" in self.capabilities

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'domain': self.domain,
            'access_level': self.access_level.value,
            'capabilities': list(self.capabilities),
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'parent_id': self.parent_id
        }


@dataclass
class AuditLogEntry:
    """Record of an access attempt for audit trail"""
    timestamp: datetime
    agent_id: str
    action: str
    resource: str
    resource_domain: str
    granted: bool
    reason: str


class IdentityManager:
    """
    Identity Manager - IAM Agent for the multi-agent system.

    Manages agent identities, access control, and maintains an audit
    trail of all inter-agent communications.

    KEY RESPONSIBILITIES:
    --------------------
    1. Identity Assignment: Create unique identities for all agents
    2. Access Control: Enforce least-privilege access
    3. Domain Isolation: Prevent cross-domain access violations
    4. Audit Logging: Record all access attempts

    DOMAIN STRUCTURE:
    ----------------
    - infrastructure: AMS, DF, ACC
    - orchestration: Main Orchestrator, Phase 3 Orchestrator
    - algebra: Algebra specialists
    - calculus: Calculus specialists
    - linear_algebra: Linear algebra specialists
    - statistics: Statistics specialists
    - discrete_math: Discrete math specialists
    - validation: Precondition Validation Team
    - knowledge: Knowledge Management Team
    - hypothesis: Hypothesis Generation Team
    - governance: Conflict Resolution Team
    - failure: Failure Analysis Team
    - meta_learning: Meta-Learning Team
    - distillation: Phase 5 Distillation Team
    - deployment: Phase 5 Hybrid Deployment Team
    - hardening: Phase 5 Hardening Team

    USAGE:
    -----
    iam = IdentityManager()

    # Register an agent
    identity = iam.register_agent(
        agent_name="Integration_Specialist",
        agent_type="specialist",
        domain="calculus",
        access_level=AccessLevel.TIER_3,
        capabilities={"integrate", "symbolic_solve"}
    )

    # Check access
    allowed = iam.check_access(identity.agent_id, "calculus_logs", "read")

    # Get audit trail
    trail = iam.get_audit_trail(agent_id=identity.agent_id)

    REFERENCE:
    ---------
    Phase_5_Build_Order_Breakdown.md: Section 5.2.2
    """

    # Valid domains in the system
    VALID_DOMAINS = {
        'infrastructure', 'orchestration',
        'algebra', 'calculus', 'linear_algebra', 'statistics', 'discrete_math', 'numerical',
        'validation', 'knowledge', 'hypothesis',
        'governance', 'failure', 'meta_learning',
        'distillation', 'deployment', 'hardening', 'evolution',
        'shared'  # Shared resources accessible by multiple domains
    }

    # Capability sets by agent type
    DEFAULT_CAPABILITIES = {
        'orchestrator': {'decompose', 'route', 'delegate', 'aggregate'},
        'supervisor': {'route', 'delegate', 'coordinate'},
        'specialist': {'compute', 'verify'},
        'system': {'*'},  # All capabilities
        'monitor': {'read', 'log'},
        'validator': {'validate', 'reject', 'flag'}
    }

    def __init__(self):
        """Initialize the Identity Manager"""
        print("  [+] Initializing Identity Manager (IAM Agent)")

        # Identity registry
        self.identities: Dict[str, AgentIdentity] = {}

        # Audit log
        self.audit_log: List[AuditLogEntry] = []

        # Statistics
        self.stats = {
            'agents_registered': 0,
            'access_granted': 0,
            'access_denied': 0,
            'violations': 0
        }

        print("      Security model: Least-Privilege")
        print("      Domain isolation: ENABLED")
        print("      Audit logging: ACTIVE")
        print("      [OK] Identity Manager ready")

    def register_agent(
        self,
        agent_name: str,
        agent_type: str,
        domain: str,
        access_level: AccessLevel,
        capabilities: Set[str] = None,
        parent_id: str = None
    ) -> AgentIdentity:
        """
        Register a new agent and assign identity.

        Args:
            agent_name: Human-readable agent name
            agent_type: Type of agent (orchestrator, supervisor, specialist, etc.)
            domain: Primary domain of operation
            access_level: Access tier
            capabilities: Set of allowed capabilities
            parent_id: ID of parent agent (for hierarchy)

        Returns:
            AgentIdentity object
        """
        # Validate domain
        if domain not in self.VALID_DOMAINS:
            raise ValueError(f"Invalid domain: {domain}")

        # Generate unique ID
        agent_id = f"{agent_type}_{domain}_{uuid.uuid4().hex[:8]}"

        # Get default capabilities if not provided
        if capabilities is None:
            capabilities = self.DEFAULT_CAPABILITIES.get(agent_type, {'compute'})

        identity = AgentIdentity(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            domain=domain,
            access_level=access_level,
            capabilities=capabilities,
            created_at=datetime.now(),
            parent_id=parent_id
        )

        self.identities[agent_id] = identity
        self.stats['agents_registered'] += 1

        # Log registration
        self._log_audit(
            agent_id=agent_id,
            action='register',
            resource='identity_system',
            resource_domain='infrastructure',
            granted=True,
            reason='agent_registration'
        )

        return identity

    def check_access(
        self,
        agent_id: str,
        resource: str,
        action: str,
        resource_domain: str = None
    ) -> bool:
        """
        Check if an agent can access a resource.

        Implements least-privilege access control.

        Args:
            agent_id: ID of the requesting agent
            resource: Resource being accessed
            action: Action being performed (read, write, execute)
            resource_domain: Domain of the resource

        Returns:
            True if access is granted
        """
        identity = self.identities.get(agent_id)

        if not identity:
            self._log_audit(
                agent_id=agent_id,
                action=action,
                resource=resource,
                resource_domain=resource_domain or 'unknown',
                granted=False,
                reason='unknown_agent'
            )
            self.stats['access_denied'] += 1
            self.stats['violations'] += 1
            return False

        # Check agent status
        if identity.status != AgentStatus.ACTIVE:
            self._log_audit(
                agent_id=agent_id,
                action=action,
                resource=resource,
                resource_domain=resource_domain or 'unknown',
                granted=False,
                reason='agent_not_active'
            )
            self.stats['access_denied'] += 1
            return False

        # Infer resource domain if not provided
        if resource_domain is None:
            resource_domain = self._infer_domain(resource)

        # Check domain access
        domain_allowed = identity.can_access(resource_domain)

        # Check capability
        capability_allowed = identity.has_capability(action)

        granted = domain_allowed and capability_allowed
        reason = 'allowed' if granted else f"domain:{domain_allowed},capability:{capability_allowed}"

        # Log access attempt
        self._log_audit(
            agent_id=agent_id,
            action=action,
            resource=resource,
            resource_domain=resource_domain,
            granted=granted,
            reason=reason
        )

        if granted:
            self.stats['access_granted'] += 1
        else:
            self.stats['access_denied'] += 1
            if not domain_allowed:
                self.stats['violations'] += 1

        return granted

    def _infer_domain(self, resource: str) -> str:
        """Infer domain from resource name"""
        resource_lower = resource.lower()
        for domain in self.VALID_DOMAINS:
            if domain in resource_lower:
                return domain
        return 'shared'

    def _log_audit(
        self,
        agent_id: str,
        action: str,
        resource: str,
        resource_domain: str,
        granted: bool,
        reason: str
    ):
        """Log an access attempt to the audit trail"""
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            agent_id=agent_id,
            action=action,
            resource=resource,
            resource_domain=resource_domain,
            granted=granted,
            reason=reason
        )
        self.audit_log.append(entry)

    def suspend_agent(self, agent_id: str, reason: str = "administrative"):
        """Suspend an agent's access"""
        if agent_id in self.identities:
            self.identities[agent_id].status = AgentStatus.SUSPENDED
            self._log_audit(
                agent_id=agent_id,
                action='suspend',
                resource='identity',
                resource_domain='infrastructure',
                granted=True,
                reason=reason
            )

    def activate_agent(self, agent_id: str):
        """Activate a suspended agent"""
        if agent_id in self.identities:
            self.identities[agent_id].status = AgentStatus.ACTIVE
            self._log_audit(
                agent_id=agent_id,
                action='activate',
                resource='identity',
                resource_domain='infrastructure',
                granted=True,
                reason='reactivation'
            )

    def get_identity(self, agent_id: str) -> Optional[AgentIdentity]:
        """Get an agent's identity"""
        return self.identities.get(agent_id)

    def get_agents_by_domain(self, domain: str) -> List[AgentIdentity]:
        """Get all agents in a domain"""
        return [
            identity for identity in self.identities.values()
            if identity.domain == domain
        ]

    def get_audit_trail(
        self,
        agent_id: str = None,
        action: str = None,
        granted: bool = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get audit trail with optional filters.

        Args:
            agent_id: Filter by agent ID
            action: Filter by action
            granted: Filter by granted status
            limit: Maximum entries to return

        Returns:
            List of audit entries
        """
        entries = self.audit_log

        if agent_id:
            entries = [e for e in entries if e.agent_id == agent_id]
        if action:
            entries = [e for e in entries if e.action == action]
        if granted is not None:
            entries = [e for e in entries if e.granted == granted]

        return [
            {
                'timestamp': e.timestamp.isoformat(),
                'agent_id': e.agent_id,
                'action': e.action,
                'resource': e.resource,
                'resource_domain': e.resource_domain,
                'granted': e.granted,
                'reason': e.reason
            }
            for e in entries[-limit:]
        ]

    def get_violations(self, limit: int = 50) -> List[Dict]:
        """Get access violations (denied cross-domain access)"""
        return self.get_audit_trail(granted=False, limit=limit)

    def get_statistics(self) -> Dict[str, Any]:
        """Get IAM statistics"""
        return {
            'agents_registered': self.stats['agents_registered'],
            'access_granted': self.stats['access_granted'],
            'access_denied': self.stats['access_denied'],
            'violations': self.stats['violations'],
            'audit_entries': len(self.audit_log),
            'active_agents': sum(
                1 for i in self.identities.values()
                if i.status == AgentStatus.ACTIVE
            ),
            'domains_active': len(set(
                i.domain for i in self.identities.values()
            ))
        }

    def register_phase_agents(self, phase: int) -> List[AgentIdentity]:
        """
        Register all agents for a specific phase.

        Utility method to bulk-register agents from a phase.

        Args:
            phase: Phase number (0-5)

        Returns:
            List of registered identities
        """
        identities = []

        # Define phase agent registrations
        phase_definitions = {
            0: [
                ('AMS', 'system', 'infrastructure', AccessLevel.SYSTEM),
                ('DF', 'system', 'infrastructure', AccessLevel.SYSTEM),
                ('ACC', 'system', 'infrastructure', AccessLevel.SYSTEM),
            ],
            1: [
                ('Orchestrator', 'orchestrator', 'orchestration', AccessLevel.TIER_1),
                ('Syntax_Parser', 'specialist', 'orchestration', AccessLevel.TIER_3),
                ('Structure_Recognizer', 'specialist', 'orchestration', AccessLevel.TIER_3),
                ('Pilot_Solver', 'specialist', 'shared', AccessLevel.TIER_3),
                ('Logic_Checker', 'validator', 'validation', AccessLevel.TIER_3),
                ('Formal_Verifier', 'validator', 'validation', AccessLevel.TIER_3),
            ],
            5: [
                ('Thought_Trace_Harvester', 'monitor', 'distillation', AccessLevel.TIER_2),
                ('Student_Model_Trainer', 'specialist', 'distillation', AccessLevel.TIER_2),
                ('Complexity_Gatekeeper', 'validator', 'deployment', AccessLevel.TIER_2),
                ('Confidence_Fallback', 'validator', 'deployment', AccessLevel.TIER_2),
                ('User_Simulator', 'specialist', 'hardening', AccessLevel.TIER_2),
                ('Identity_Manager', 'system', 'hardening', AccessLevel.SYSTEM),
            ]
        }

        if phase in phase_definitions:
            for name, agent_type, domain, access_level in phase_definitions[phase]:
                identity = self.register_agent(
                    agent_name=name,
                    agent_type=agent_type,
                    domain=domain,
                    access_level=access_level
                )
                identities.append(identity)

        return identities
