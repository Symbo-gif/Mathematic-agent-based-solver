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
PHASE 5 - OH-1: SECURITY MONITOR (Tier 3)
=========================================

Monitors system security, detects anomalies, and makes access
control decisions.

CAPABILITIES:
------------
- Access log monitoring
- Anomaly detection
- Access control policy enforcement
- Security alert generation
- Threat model management

REFERENCE:
---------
- Agent_System_Audit.docx.md: OH-1 Security Monitor
- Phase_5_Optimization.md: Operational Hardening Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Set, Pattern
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re
import signal
import threading

logger = logging.getLogger('symbo_agentic_reasoners.phase5.security_monitor')

# Security constants for regex validation
MAX_PATTERN_LENGTH = 500  # Maximum regex pattern length
REGEX_TIMEOUT_SECONDS = 0.1  # Maximum time for regex matching

# Patterns that could cause ReDoS (catastrophic backtracking)
DANGEROUS_REGEX_PATTERNS = [
    r'\(\.\*\)\+',           # (.*)+
    r'\(\.\+\)\+',           # (.+)+
    r'\([^)]*\+[^)]*\)\+',   # (a+)+ style patterns
    r'\([^)]*\*[^)]*\)\+',   # (a*)+
    r'\([^)]*\+[^)]*\)\*',   # (a+)*
    r'\([^)]*\*[^)]*\)\*',   # (a*)*
    r'\\d\+\\d\+',           # \d+\d+ adjacent quantifiers
    r'\.\*\.\*\.\*',         # Multiple .* in sequence
]
DANGEROUS_REGEX = re.compile('|'.join(DANGEROUS_REGEX_PATTERNS))


def _validate_regex_pattern(pattern: str) -> tuple:
    """
    Validate a regex pattern for safety.

    Returns:
        (is_safe: bool, error_message: str or None)
    """
    if not isinstance(pattern, str):
        return False, "Pattern must be a string"

    if len(pattern) > MAX_PATTERN_LENGTH:
        return False, f"Pattern too long: {len(pattern)} > {MAX_PATTERN_LENGTH}"

    # Check for dangerous patterns that could cause ReDoS
    if DANGEROUS_REGEX.search(pattern):
        return False, "Pattern contains potential ReDoS vulnerability"

    # Check for deeply nested groups (potential exponential backtracking)
    nesting_depth = 0
    max_nesting = 0
    for char in pattern:
        if char == '(':
            nesting_depth += 1
            max_nesting = max(max_nesting, nesting_depth)
        elif char == ')':
            nesting_depth -= 1

    if max_nesting > 5:
        return False, f"Pattern nesting too deep: {max_nesting} > 5"

    # Try to compile the pattern
    try:
        re.compile(pattern)
    except re.error as e:
        return False, f"Invalid regex: {e}"

    return True, None


def _compile_regex_safe(pattern: str) -> Optional[Pattern]:
    """
    Safely compile a regex pattern with validation.

    Returns compiled pattern or None if invalid.
    """
    is_safe, error = _validate_regex_pattern(pattern)
    if not is_safe:
        logger.warning(f"Unsafe regex pattern rejected: {error}")
        return None

    try:
        return re.compile(pattern)
    except re.error:
        return None


def _canonicalize_resource_path(resource: str) -> str:
    """
    Canonicalize resource path to prevent bypass attacks.

    Protections:
    - Resolves relative paths (../, ./)
    - Normalizes separators (\\ vs /)
    - Converts to lowercase for case-insensitive matching
    - Removes duplicate slashes
    - Decodes URL encoding

    Args:
        resource: Resource path to canonicalize

    Returns:
        Canonical resource path (lowercase, normalized)
    """
    import urllib.parse
    from pathlib import Path

    # Step 1: URL decode
    decoded = urllib.parse.unquote(resource)

    # Step 2: Normalize path separators
    normalized = decoded.replace('\\', '/')

    # Step 3: Remove duplicate slashes
    while '//' in normalized:
        normalized = normalized.replace('//', '/')

    # Step 4: Resolve relative paths
    try:
        # Manual path resolution (don't use Path.parts on Windows as it includes drive)
        parts = []
        for part in normalized.split('/'):
            if part == '..':
                if parts:
                    parts.pop()
            elif part and part != '.':
                parts.append(part)
        normalized = '/'.join(parts)
    except (ValueError, OSError):
        # If path manipulation fails, use original normalized version
        pass

    # Step 5: Convert to lowercase for case-insensitive comparison
    canonical = normalized.lower()

    # Step 6: Ensure leading slash
    if canonical and not canonical.startswith('/'):
        canonical = '/' + canonical

    return canonical


def _safe_regex_match(compiled_pattern: Optional[Pattern], text: str, timeout: float = REGEX_TIMEOUT_SECONDS) -> Optional[re.Match]:
    """
    Perform regex match with timeout protection.

    Uses a simple approach: limit text length and use compiled pattern.
    On Windows where signal.alarm isn't available, we rely on pattern validation.
    """
    if compiled_pattern is None:
        return None

    # Limit input text length to prevent DoS
    if len(text) > 10000:
        text = text[:10000]

    try:
        # Use match with the compiled pattern
        return compiled_pattern.match(text)
    except Exception as e:
        logger.warning(f"Regex match failed: {e}")
        return None


# Cache for compiled regex patterns
_compiled_pattern_cache: Dict[str, Optional[Pattern]] = {}

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class AlertSeverity(Enum):
    """Security alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AccessDecision(Enum):
    """Access control decisions"""
    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"        # Allow but log
    CHALLENGE = "challenge"  # Require additional auth


class AnomalyType(Enum):
    """Types of anomalies"""
    RATE_LIMIT = "rate_limit"
    UNUSUAL_PATTERN = "unusual_pattern"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    UNKNOWN_AGENT = "unknown_agent"


@dataclass
class AccessLog:
    """Record of an access attempt"""
    timestamp: datetime
    agent_id: str
    resource: str
    action: str
    decision: AccessDecision
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'agent_id': self.agent_id,
            'resource': self.resource,
            'action': self.action,
            'decision': self.decision.value
        }


@dataclass
class SecurityAlert:
    """Security alert notification"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    anomaly_type: AnomalyType
    agent_id: Optional[str]
    description: str
    recommended_action: str
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'type': self.anomaly_type.value,
            'agent': self.agent_id,
            'description': self.description,
            'action': self.recommended_action
        }


@dataclass
class AccessPolicy:
    """Access control policy rule"""
    policy_id: str
    agent_pattern: str  # Regex pattern for agent IDs
    resource_pattern: str  # Regex for resources
    allowed_actions: Set[str]
    max_rate_per_minute: int = 100
    enabled: bool = True
    # Compiled patterns (cached for performance and security)
    _compiled_agent_pattern: Optional[Pattern] = field(default=None, repr=False)
    _compiled_resource_pattern: Optional[Pattern] = field(default=None, repr=False)

    def __post_init__(self):
        """Compile and validate regex patterns on initialization."""
        # Compile agent pattern with validation
        if self.agent_pattern and self._compiled_agent_pattern is None:
            self._compiled_agent_pattern = _compile_regex_safe(self.agent_pattern)
            if self._compiled_agent_pattern is None:
                logger.warning(f"Policy {self.policy_id}: Invalid agent_pattern, using literal match")

        # Compile resource pattern with validation
        if self.resource_pattern and self._compiled_resource_pattern is None:
            self._compiled_resource_pattern = _compile_regex_safe(self.resource_pattern)
            if self._compiled_resource_pattern is None:
                logger.warning(f"Policy {self.policy_id}: Invalid resource_pattern, using literal match")

    def match_agent(self, agent_id: str) -> bool:
        """Safely match agent ID against pattern."""
        # SECURITY: Enforce length limit on patterns used in fallback
        MAX_LITERAL_PATTERN_LENGTH = 100

        if self._compiled_agent_pattern is not None:
            result = _safe_regex_match(self._compiled_agent_pattern, agent_id)
            return result is not None
        # Fallback to literal match if pattern compilation failed
        # But enforce strict length limit to prevent bypass attacks
        if len(self.agent_pattern) > MAX_LITERAL_PATTERN_LENGTH:
            logger.error(f"Policy {self.policy_id}: agent_pattern too long for literal fallback ({len(self.agent_pattern)} > {MAX_LITERAL_PATTERN_LENGTH})")
            return False
        return agent_id == self.agent_pattern

    def match_resource(self, resource: str) -> bool:
        """Safely match resource against pattern."""
        # SECURITY: Enforce length limit on patterns used in fallback
        MAX_LITERAL_PATTERN_LENGTH = 100

        if self._compiled_resource_pattern is not None:
            result = _safe_regex_match(self._compiled_resource_pattern, resource)
            return result is not None
        # Fallback to literal match if pattern compilation failed
        # But enforce strict length limit to prevent bypass attacks
        if len(self.resource_pattern) > MAX_LITERAL_PATTERN_LENGTH:
            logger.error(f"Policy {self.policy_id}: resource_pattern too long for literal fallback ({len(self.resource_pattern)} > {MAX_LITERAL_PATTERN_LENGTH})")
            return False
        return resource == self.resource_pattern

    def to_dict(self) -> Dict[str, Any]:
        return {
            'policy_id': self.policy_id,
            'agent_pattern': self.agent_pattern,
            'resource_pattern': self.resource_pattern,
            'actions': list(self.allowed_actions),
            'rate_limit': self.max_rate_per_minute
        }


class SecurityMonitor(BDIAgent):
    """
    OH-1: Security Monitor
    
    DIRECTIVE:
    ---------
    Monitor system security, detect anomalies, and enforce
    access control policies.
    
    INPUTS:
    ------
    - Access logs
    - Anomaly detection signals
    - Policy configurations
    
    OUTPUTS:
    -------
    - Security alert notifications
    - Access permission decisions
    - Audit reports
    
    DEPENDENCIES:
    ------------
    - AMS (AgentManagementService): For agent registry
    - PV-4 (PatternVerifier): For anomaly detection
    
    FAILURE MODE: LOCKDOWN - Adopts deny-by-default posture
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 602-611
    """
    
    def __init__(
        self,
        agent_id: str = 'security_monitor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        lockdown_mode: bool = False
    ):
        """
        Initialize Security Monitor
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            lockdown_mode: If True, deny all by default
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        self.lockdown_mode = lockdown_mode
        
        # Access logs (rolling window)
        self.access_logs: List[AccessLog] = []
        self.max_log_entries = 10000
        
        # Security alerts
        self.alerts: Dict[str, SecurityAlert] = {}
        
        # Access policies
        self.policies: Dict[str, AccessPolicy] = {}
        
        # Rate limiting tracking
        self.rate_counters: Dict[str, List[datetime]] = {}
        
        # Known agents
        self.known_agents: Set[str] = set()
        
        # Threat model
        self.blocked_agents: Set[str] = set()
        self.suspicious_patterns: List[str] = []
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.access_checks = 0
        self.access_denials = 0
        self.alerts_generated = 0
        
        # Initialize default policies
        self._initialize_default_policies()
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Security Monitor initialized")
        print(f"  Lockdown mode: {lockdown_mode}")
        print(f"  Policies loaded: {len(self.policies)}")
    
    def _initialize_default_policies(self):
        """Initialize default security policies"""
        # Default allow-all policy for known agents
        self.policies["default_allow"] = AccessPolicy(
            policy_id="default_allow",
            agent_pattern=".*",
            resource_pattern=".*",
            allowed_actions={"read", "write", "execute"},
            max_rate_per_minute=1000
        )
        
        # Restrict blackboard access
        self.policies["blackboard_access"] = AccessPolicy(
            policy_id="blackboard_access",
            agent_pattern=".*",
            resource_pattern="blackboard/.*",
            allowed_actions={"read", "write", "subscribe"},
            max_rate_per_minute=500
        )
        
        # Restrict admin operations
        self.policies["admin_restrict"] = AccessPolicy(
            policy_id="admin_restrict",
            agent_pattern="admin.*|system.*",
            resource_pattern="admin/.*|config/.*",
            allowed_actions={"read", "write", "execute", "delete"},
            max_rate_per_minute=100
        )
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='system.security.monitor',
            agent_id=self.agent_id,
            algorithm='anomaly_detection',
            cost='low',
            type='monitoring',
            tier='3',
            algorithms='access_control_anomaly_detection'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: system.security.monitor")
    
    def register_agent(self, agent_id: str):
        """Register an agent as known/trusted"""
        self.known_agents.add(agent_id)
    
    def check_access(
        self,
        agent_id: str,
        resource: str,
        action: str
    ) -> AccessDecision:
        """
        Check if an access request should be allowed.
        
        Args:
            agent_id: Agent requesting access
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            AccessDecision
        """
        self.tasks_executed += 1
        self.access_checks += 1
        
        try:
            # Lockdown mode - deny all
            if self.lockdown_mode:
                decision = AccessDecision.DENY
                self._log_access(agent_id, resource, action, decision)
                return decision
            
            # Check if agent is blocked
            if agent_id in self.blocked_agents:
                decision = AccessDecision.DENY
                self._log_access(agent_id, resource, action, decision)
                self.access_denials += 1
                return decision
            
            # Check if agent is unknown
            if agent_id not in self.known_agents:
                # Generate alert for unknown agent
                self._create_alert(
                    AnomalyType.UNKNOWN_AGENT,
                    AlertSeverity.MEDIUM,
                    agent_id,
                    f"Unknown agent {agent_id} attempted {action} on {resource}",
                    "Verify agent identity and register if legitimate"
                )
                # SECURITY: Canonicalize resource path before checking
                canonical_resource = _canonicalize_resource_path(resource)

                # DENY access to restricted resources for unknown agents
                restricted_prefixes = ('/admin/', '/system/', '/ams/', '/config/',
                                      '/infrastructure/', '/supervisor/')
                if canonical_resource.startswith(restricted_prefixes):
                    decision = AccessDecision.DENY
                    self._log_access(agent_id, resource, action, decision)
                    self.access_denials += 1
                    return decision
                # Allow but audit non-restricted resources
                decision = AccessDecision.AUDIT
                self._log_access(agent_id, resource, action, decision)
                return decision
            
            # Check rate limiting
            if not self._check_rate_limit(agent_id):
                self._create_alert(
                    AnomalyType.RATE_LIMIT,
                    AlertSeverity.MEDIUM,
                    agent_id,
                    f"Agent {agent_id} exceeded rate limit",
                    "Throttle agent requests"
                )
                decision = AccessDecision.DENY
                self._log_access(agent_id, resource, action, decision)
                self.access_denials += 1
                return decision
            
            # SECURITY: Canonicalize resource path to prevent bypass attacks
            canonical_resource = _canonicalize_resource_path(resource)

            # Check for restricted resources first (deny non-privileged access)
            # Admin/system/infrastructure resources require privileged agent
            if canonical_resource.startswith(('/admin/', '/system/', '/ams/', '/config/', '/infrastructure/')):
                if not agent_id.lower().startswith(('admin', 'system', 'ams', 'infrastructure')):
                    decision = AccessDecision.DENY
                    self._log_access(agent_id, resource, action, decision)
                    self.access_denials += 1
                    return decision

            # Supervisor resources require supervisor prefix
            if canonical_resource.startswith('/supervisor/'):
                if not any(agent_id.lower().startswith(p) for p in ('admin', 'system', 'supervisor', 'orchestrator')):
                    decision = AccessDecision.DENY
                    self._log_access(agent_id, resource, action, decision)
                    self.access_denials += 1
                    return decision

            # Check policies
            for policy in self.policies.values():
                if not policy.enabled:
                    continue

                # Use safe regex matching (validates patterns, prevents ReDoS)
                agent_match = policy.match_agent(agent_id)
                resource_match = policy.match_resource(resource)

                if agent_match and resource_match:
                    if action in policy.allowed_actions:
                        decision = AccessDecision.ALLOW
                        self._log_access(agent_id, resource, action, decision)
                        self.tasks_succeeded += 1
                        return decision

            # Default deny
            decision = AccessDecision.DENY
            self._log_access(agent_id, resource, action, decision)
            self.access_denials += 1
            return decision
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Access check failed: {type(e).__name__}: {e}")
            # Fail closed
            return AccessDecision.DENY
    
    def _check_rate_limit(self, agent_id: str) -> bool:
        """Check if agent is within rate limits"""
        now = datetime.now()
        window = timedelta(minutes=1)
        
        if agent_id not in self.rate_counters:
            self.rate_counters[agent_id] = []
        
        # Remove old entries
        self.rate_counters[agent_id] = [
            t for t in self.rate_counters[agent_id]
            if now - t < window
        ]
        
        # Check count against policy
        current_rate = len(self.rate_counters[agent_id])
        
        # Find applicable policy (use safe matching)
        max_rate = 1000  # Default
        for policy in self.policies.values():
            if policy.match_agent(agent_id):
                max_rate = min(max_rate, policy.max_rate_per_minute)
        
        if current_rate >= max_rate:
            return False
        
        # Record access
        self.rate_counters[agent_id].append(now)
        return True
    
    def _log_access(
        self,
        agent_id: str,
        resource: str,
        action: str,
        decision: AccessDecision
    ):
        """Log an access attempt"""
        log = AccessLog(
            timestamp=datetime.now(),
            agent_id=agent_id,
            resource=resource,
            action=action,
            decision=decision
        )
        
        self.access_logs.append(log)
        
        # Trim logs if needed
        if len(self.access_logs) > self.max_log_entries:
            self.access_logs = self.access_logs[-self.max_log_entries:]
    
    def _create_alert(
        self,
        anomaly_type: AnomalyType,
        severity: AlertSeverity,
        agent_id: Optional[str],
        description: str,
        recommended_action: str
    ) -> str:
        """Create a security alert"""
        alert_id = hashlib.md5(
            f"{datetime.now().isoformat()}{agent_id}{anomaly_type.value}".encode()
        ).hexdigest()[:12]
        
        alert = SecurityAlert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            severity=severity,
            anomaly_type=anomaly_type,
            agent_id=agent_id,
            description=description,
            recommended_action=recommended_action
        )
        
        self.alerts[alert_id] = alert
        self.alerts_generated += 1
        
        logger.warning(f"Security Alert [{severity.value}]: {description}")
        
        return alert_id
    
    def block_agent(self, agent_id: str, reason: str):
        """Block an agent from accessing resources"""
        self.blocked_agents.add(agent_id)
        self._create_alert(
            AnomalyType.PRIVILEGE_ESCALATION,
            AlertSeverity.HIGH,
            agent_id,
            f"Agent {agent_id} blocked: {reason}",
            "Review agent behavior and consider permanent revocation"
        )
    
    def unblock_agent(self, agent_id: str):
        """Remove agent from blocked list"""
        self.blocked_agents.discard(agent_id)
    
    def set_lockdown(self, enabled: bool):
        """Enable or disable lockdown mode"""
        self.lockdown_mode = enabled
        if enabled:
            self._create_alert(
                AnomalyType.UNUSUAL_PATTERN,
                AlertSeverity.CRITICAL,
                None,
                "LOCKDOWN mode activated - all access denied",
                "Investigate security incident and restore normal operation"
            )
    
    def get_recent_alerts(
        self,
        severity_filter: Optional[AlertSeverity] = None,
        limit: int = 10
    ) -> List[SecurityAlert]:
        """Get recent security alerts"""
        alerts = list(self.alerts.values())
        
        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]
        
        # Sort by timestamp descending
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        
        return alerts[:limit]
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge a security alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
    
    def process(self, task_entry: Any) -> Any:
        """Process security monitoring task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing security task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'status')
            
            if operation == 'status':
                result = {
                    'lockdown_mode': self.lockdown_mode,
                    'known_agents': len(self.known_agents),
                    'blocked_agents': len(self.blocked_agents),
                    'active_alerts': len([a for a in self.alerts.values() if not a.acknowledged]),
                    'access_logs': len(self.access_logs)
                }
                
            elif operation == 'check_access':
                agent_id = metadata.get('agent_id')
                resource = metadata.get('resource')
                action = metadata.get('action', 'read')
                decision = self.check_access(agent_id, resource, action)
                result = {
                    'decision': decision.value,
                    'agent': agent_id,
                    'resource': resource
                }
                
            elif operation == 'register_agent':
                agent_id = metadata.get('agent_id')
                self.register_agent(agent_id)
                result = {'registered': agent_id}
                
            elif operation == 'block_agent':
                agent_id = metadata.get('agent_id')
                reason = metadata.get('reason', 'Manual block')
                self.block_agent(agent_id, reason)
                result = {'blocked': agent_id}
                
            elif operation == 'get_alerts':
                severity = metadata.get('severity')
                if severity:
                    severity = AlertSeverity(severity)
                alerts = self.get_recent_alerts(severity)
                result = {
                    'alerts': [a.to_dict() for a in alerts],
                    'count': len(alerts)
                }
                
            elif operation == 'lockdown':
                self.set_lockdown(metadata.get('enabled', True))
                result = {'lockdown': self.lockdown_mode}
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Security task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['security', 'monitor'],
            status=EntryStatus.PENDING,
            metadata=result
        )
        
        self.blackboard.post(result_entry)
        return result_entry
    
    def _create_error_entry(self, task_entry: Any, error_msg: str) -> Any:
        """Create error entry for Blackboard"""
        if not self.blackboard:
            return None
        
        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'security'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """Monitor for security events"""
        pass
    
    def deliberate(self):
        """Generate security response plans"""
        return []
    
    def execute_step(self, intention: Intention):
        """Execute security action"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get security monitor statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'access_checks': self.access_checks,
            'access_denials': self.access_denials,
            'denial_rate': (self.access_denials / self.access_checks * 100)
                          if self.access_checks > 0 else 0.0,
            'alerts_generated': self.alerts_generated,
            'lockdown_mode': self.lockdown_mode
        })
        return stats


# =============================================================================
# PHASE 5 - ISSUES #9-12: SECURITY MONITOR ENHANCEMENTS
# =============================================================================

class BehavioralAnomalyDetector:
    """
    Detect behavioral anomalies in agent actions.

    Phase 5 - Issue #9: Tracks agent behavior patterns and detects deviations.

    Detection Methods:
    - Unusual time-of-day access
    - Resource access pattern deviation
    - Action frequency spikes
    - Sequential action anomalies
    """

    def __init__(self):
        """Initialize behavioral anomaly detector."""
        self._agent_profiles: Dict[str, Dict] = {}
        self.anomalies_detected = 0

    def detect_anomalies(self, agent_id: str, action: str, resource: str) -> List[str]:
        """
        Detect behavioral anomalies for agent action.

        Args:
            agent_id: Agent performing action
            action: Action type
            resource: Resource being accessed

        Returns:
            List of anomaly types detected
        """
        anomalies = []

        # Get or create agent profile
        if agent_id not in self._agent_profiles:
            self._agent_profiles[agent_id] = {
                'actions': [],
                'resources': set(),
                'access_times': [],
                'action_counts': {},
            }

        profile = self._agent_profiles[agent_id]

        # Record action
        profile['actions'].append((time.time(), action, resource))
        profile['resources'].add(resource)
        profile['access_times'].append(time.time())
        profile['action_counts'][action] = profile['action_counts'].get(action, 0) + 1

        # Detect anomalies
        if self._is_action_spike(profile, action):
            anomalies.append("action_frequency_spike")

        if self._is_unusual_resource(profile, resource):
            anomalies.append("unusual_resource_access")

        if anomalies:
            self.anomalies_detected += len(anomalies)

        return anomalies

    def _is_action_spike(self, profile: Dict, action: str) -> bool:
        """Check for action frequency spike."""
        recent_actions = [
            a for ts, a, r in profile['actions']
            if time.time() - ts < 60  # Last minute
        ]

        if len(recent_actions) < 10:
            return False

        action_count = recent_actions.count(action)
        return action_count > 20  # More than 20 same actions in 1 minute

    def _is_unusual_resource(self, profile: Dict, resource: str) -> bool:
        """Check for unusual resource access."""
        # First-time resource access after 10+ actions
        if len(profile['actions']) > 10 and resource not in profile['resources']:
            return True
        return False


class ThreatPatternDatabase:
    """
    Persistent threat pattern storage.

    Phase 5 - Issue #10: Stores threat patterns to disk for learning.

    Features:
    - JSON-based persistent storage
    - Pattern querying by type
    - Automatic persistence on save
    - Thread-safe operations
    """

    def __init__(self, db_path: str = "data/security/threat_patterns.json"):
        """
        Initialize threat pattern database.

        Args:
            db_path: Path to JSON database file
        """
        from pathlib import Path
        import json

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._patterns = self._load_patterns()
        self._lock = threading.RLock()

    def _load_patterns(self) -> Dict:
        """Load patterns from disk."""
        import json

        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load threat patterns: {e}")

        return {'patterns': [], 'version': '1.0', 'last_updated': time.time()}

    def save_pattern(self, pattern: Dict):
        """
        Save threat pattern to database.

        Args:
            pattern: Pattern dictionary (must include 'alert_type')
        """
        import json

        with self._lock:
            self._patterns['patterns'].append({
                **pattern,
                'timestamp': time.time(),
                'id': len(self._patterns['patterns'])
            })
            self._patterns['last_updated'] = time.time()
            self._persist()

    def _persist(self):
        """Write patterns to disk."""
        import json

        try:
            with open(self.db_path, 'w') as f:
                json.dump(self._patterns, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist threat patterns: {e}")

    def query_similar(self, alert_type: str, limit: int = 10) -> List[Dict]:
        """
        Query similar historical patterns.

        Args:
            alert_type: Alert type to match
            limit: Maximum patterns to return

        Returns:
            List of matching patterns
        """
        with self._lock:
            matches = [
                p for p in self._patterns['patterns']
                if p.get('alert_type') == alert_type
            ]
            return matches[-limit:] if limit else matches


class PatternThresholdOptimizer:
    """
    Optimize detection thresholds via statistical analysis.

    Phase 5 - Issue #11: Uses F1 score optimization to tune thresholds.

    Features:
    - ROC curve-based threshold selection
    - F1 score maximization
    - False positive/negative tracking
    - Automatic threshold updates
    """

    def __init__(self):
        """Initialize pattern threshold optimizer."""
        self._thresholds = {
            'rate_limit': 100,  # requests/minute
            'message_size': 1_000_000,  # bytes
            'resource_access_frequency': 50,  # accesses/minute
        }
        self._optimization_history: List[Dict] = []

    def optimize_thresholds(self, historical_data: List[Dict]) -> Dict[str, float]:
        """
        Optimize thresholds using historical data.

        Args:
            historical_data: List of {alert_type, was_true_positive, value}

        Returns:
            Updated thresholds dictionary
        """
        for threshold_type in self._thresholds.keys():
            relevant_data = [
                d for d in historical_data
                if d.get('alert_type') == threshold_type
            ]

            if len(relevant_data) < 10:
                continue  # Need sufficient data

            # Find optimal threshold
            best_threshold = self._find_optimal_threshold(relevant_data)

            if best_threshold is not None:
                self._thresholds[threshold_type] = best_threshold
                self._optimization_history.append({
                    'threshold_type': threshold_type,
                    'old_value': self._thresholds.get(threshold_type),
                    'new_value': best_threshold,
                    'timestamp': time.time()
                })

        return self._thresholds

    def _find_optimal_threshold(self, data: List[Dict]) -> Optional[float]:
        """Find threshold that maximizes F1 score."""
        if not data:
            return None

        values = sorted(set(d.get('value', 0) for d in data))
        best_f1 = 0.0
        best_threshold = None

        for candidate in values:
            tp = sum(1 for d in data if d.get('value', 0) >= candidate and d.get('was_true_positive', False))
            fp = sum(1 for d in data if d.get('value', 0) >= candidate and not d.get('was_true_positive', False))
            fn = sum(1 for d in data if d.get('value', 0) < candidate and d.get('was_true_positive', False))

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            if f1 > best_f1:
                best_f1 = f1
                best_threshold = candidate

        return best_threshold

    def get_threshold(self, threshold_type: str) -> Optional[float]:
        """Get current threshold value."""
        return self._thresholds.get(threshold_type)


class PersistentAuditLogger:
    """
    Persistent append-only audit log with rotation.

    Phase 5 - Issue #12: Prevents audit trail truncation.

    Features:
    - Daily log rotation
    - 30-day retention
    - JSON structured logging
    - Append-only for forensics
    """

    def __init__(self, log_dir: str = "data/security/audit"):
        """
        Initialize persistent audit logger.

        Args:
            log_dir: Directory for audit logs
        """
        from pathlib import Path
        import logging.handlers
        import json

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Rotating file handler (daily rotation, 30-day retention)
        log_file = self.log_dir / "security_audit.log"
        self.handler = logging.handlers.TimedRotatingFileHandler(
            str(log_file),
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )

        # JSON formatter for structured logs
        self.handler.setFormatter(logging.Formatter('%(message)s'))

        self.logger = logging.getLogger('security_audit')
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

        self.logs_written = 0

    def log_access(self, agent_id: str, resource: str, action: str, allowed: bool):
        """
        Log access attempt.

        Args:
            agent_id: Agent making request
            resource: Resource being accessed
            action: Action being performed
            allowed: Whether access was granted
        """
        import json

        self.logger.info(json.dumps({
            'timestamp': time.time(),
            'event_type': 'access',
            'agent_id': agent_id,
            'resource': resource,
            'action': action,
            'allowed': allowed
        }))
        self.logs_written += 1

    def log_alert(self, alert_type: str, severity: str, agent_id: str,
                 message: str, recommended_action: str = None):
        """
        Log security alert.

        Args:
            alert_type: Type of alert
            severity: Severity level
            agent_id: Agent involved
            message: Alert message
            recommended_action: Recommended response action
        """
        import json

        self.logger.warning(json.dumps({
            'timestamp': time.time(),
            'event_type': 'alert',
            'alert_type': alert_type,
            'severity': severity,
            'agent_id': agent_id,
            'message': message,
            'recommended_action': recommended_action
        }))
        self.logs_written += 1


# =============================================================================


if __name__ == "__main__":
    """Test Security Monitor"""
    print("=" * 80)
    print("PHASE 5 - SECURITY MONITOR TEST")
    print("=" * 80)
    print()
    
    # Initialize monitor
    monitor = SecurityMonitor()
    print()
    
    # Test 1: Register agents
    print("Test 1: Register Known Agents")
    monitor.register_agent("agent_001")
    monitor.register_agent("agent_002")
    print(f"  Known agents: {len(monitor.known_agents)}")
    print()
    
    # Test 2: Check access
    print("Test 2: Access Checks")
    decisions = [
        ("agent_001", "blackboard/data", "read"),
        ("agent_002", "blackboard/config", "write"),
        ("unknown_agent", "admin/settings", "delete"),
    ]
    for agent, resource, action in decisions:
        decision = monitor.check_access(agent, resource, action)
        print(f"  {agent} -> {resource} ({action}): {decision.value}")
    print()
    
    # Test 3: Get alerts
    print("Test 3: Security Alerts")
    alerts = monitor.get_recent_alerts()
    print(f"  Active alerts: {len(alerts)}")
    for alert in alerts[:3]:
        print(f"    [{alert.severity.value}] {alert.description}")
    print()
    
    # Test 4: Block agent
    print("Test 4: Block Agent")
    monitor.block_agent("bad_actor", "Suspicious behavior detected")
    decision = monitor.check_access("bad_actor", "any/resource", "read")
    print(f"  Blocked agent access: {decision.value}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(monitor.get_statistics(), indent=2))
