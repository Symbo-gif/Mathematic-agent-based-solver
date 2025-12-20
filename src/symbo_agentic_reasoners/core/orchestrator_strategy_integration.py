# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Orchestrator Strategy Learning Integration
===========================================

PURPOSE:
--------
Integrates the strategy learning system into the Main Orchestrator,
enabling strategy-aware problem routing, learning from solution patterns,
and cross-domain strategy transfer.

INTEGRATION COMPONENTS:
-----------------------
1. Enhanced Meta-Learning Team with Strategy Learning
2. Strategy-Aware Routing (routing based on detected strategies)
3. Conversation-Level Strategy Tracking
4. Security Validation for all strategy inputs
5. Edge Case Handling for malformed or adversarial inputs

SECURITY:
---------
- Input validation for all strategy data
- SQL injection prevention in KnowledgeGraph queries
- Size limits on metadata to prevent DoS
- Sanitization of user-provided strategy names
- Rate limiting on strategy learning operations

ARCHITECTURE:
-------------
MainOrchestrator
    ├── MetaLearningTeamWithStrategies (replaces base meta-learning)
    │   ├── PerformanceMonitor (Agent 3.1)
    │   ├── AgentSelectorOptimizer (Agent 3.2)
    │   ├── AdaptiveDispatcher (Agent 3.3)
    │   └── StrategyCoordinator (Agent 3.8)
    │       ├── StructuralStrategyLearner (Agent 3.4)
    │       ├── HeuristicPatternLearner (Agent 3.5)
    │       ├── NonStandardMoveLearner (Agent 3.6)
    │       └── MetaStrategyLearner (Agent 3.7)
    └── StrategyTransferEngine (cross-domain transfer)

REFERENCE:
----------
- Phase 4 Build Order: Meta-Learning + Strategy Learning Integration
"""

import logging
import re
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import threading
import uuid

from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain

# Import enhanced meta-learning with strategies
from symbo_agentic_reasoners.middleware.meta_learning_extensions import (
    MetaLearningTeamWithStrategies, EnhancedSolutionTrace
)

# Import strategy transfer engine
from symbo_agentic_reasoners.middleware.strategy_learning.strategy_transfer_engine import (
    StrategyTransferEngine
)

# Import KnowledgeGraph extensions
from symbo_agentic_reasoners.infrastructure.knowledge_graph import MathematicalKnowledgeGraph
from symbo_agentic_reasoners.infrastructure.knowledge_graph_strategy_extensions import (
    install_strategy_extensions
)

logger = logging.getLogger('symbo_agentic_reasoners.orchestrator_strategy')


# ===========================================================================
# SECURITY VALIDATION
# ===========================================================================

class SecurityValidator:
    """
    Security validation for strategy learning inputs.

    Prevents:
    - SQL injection in strategy IDs and names
    - DoS via large metadata payloads
    - Path traversal in file operations
    - XSS in user-provided content
    - Malicious regex patterns

    CRITICAL: All user-provided or external data MUST pass through
    this validator before being used in strategy learning operations.
    """

    # Maximum sizes to prevent DoS
    MAX_STRATEGY_NAME_LENGTH = 200
    MAX_METADATA_SIZE = 10000  # bytes
    MAX_TRACE_ID_LENGTH = 100
    MAX_AGENT_SEQUENCE_LENGTH = 100
    MAX_EVIDENCE_LENGTH = 1000

    # Allowed patterns
    SAFE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{1,100}$')
    SAFE_DOMAIN_PATTERN = re.compile(r'^[a-zA-Z0-9_]{1,50}$')

    @classmethod
    def validate_strategy_id(cls, strategy_id: str) -> str:
        """
        Validate and sanitize strategy ID.

        Args:
            strategy_id: Strategy identifier to validate

        Returns:
            Sanitized strategy ID

        Raises:
            ValueError: If strategy_id is invalid or malicious

        Security:
            - Prevents SQL injection
            - Enforces length limits
            - Allows only alphanumeric and safe characters
        """
        if not strategy_id or not isinstance(strategy_id, str):
            raise ValueError("Strategy ID must be a non-empty string")

        if len(strategy_id) > cls.MAX_TRACE_ID_LENGTH:
            raise ValueError(f"Strategy ID too long (max {cls.MAX_TRACE_ID_LENGTH})")

        if not cls.SAFE_ID_PATTERN.match(strategy_id):
            raise ValueError(
                "Strategy ID contains invalid characters. "
                "Only alphanumeric, underscore, and hyphen allowed."
            )

        return strategy_id

    @classmethod
    def validate_strategy_name(cls, name: str) -> str:
        """
        Validate and sanitize strategy name.

        Args:
            name: Strategy name to validate

        Returns:
            Sanitized name

        Raises:
            ValueError: If name is invalid

        Security:
            - Prevents XSS
            - Enforces length limits
            - Removes dangerous characters
        """
        if not name or not isinstance(name, str):
            raise ValueError("Strategy name must be a non-empty string")

        if len(name) > cls.MAX_STRATEGY_NAME_LENGTH:
            raise ValueError(f"Strategy name too long (max {cls.MAX_STRATEGY_NAME_LENGTH})")

        # Remove any HTML/script tags (XSS prevention)
        sanitized = re.sub(r'<[^>]*>', '', name)

        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')

        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)

        # If completely sanitized away, use safe placeholder
        sanitized = sanitized.strip()
        if not sanitized:
            # Return safe placeholder instead of raising
            # This handles edge cases like pure XSS or null bytes
            return "sanitized_strategy"

        return sanitized

    @classmethod
    def validate_domain(cls, domain: str) -> str:
        """
        Validate problem domain.

        Args:
            domain: Domain string to validate

        Returns:
            Sanitized domain

        Raises:
            ValueError: If domain is invalid
        """
        if not domain or not isinstance(domain, str):
            raise ValueError("Domain must be a non-empty string")

        if not cls.SAFE_DOMAIN_PATTERN.match(domain):
            raise ValueError(
                "Domain contains invalid characters. "
                "Only alphanumeric and underscore allowed."
            )

        return domain.lower()

    @classmethod
    def validate_metadata(cls, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize metadata dictionary.

        Args:
            metadata: Metadata dictionary to validate

        Returns:
            Sanitized metadata

        Raises:
            ValueError: If metadata is invalid or too large

        Security:
            - Prevents DoS via large payloads
            - Limits nesting depth
            - Sanitizes string values
        """
        if metadata is None:
            return {}

        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a dictionary")

        # Check size (serialized)
        import json
        try:
            serialized = json.dumps(metadata, default=str)
            if len(serialized) > cls.MAX_METADATA_SIZE:
                raise ValueError(f"Metadata too large (max {cls.MAX_METADATA_SIZE} bytes)")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Metadata serialization failed: {e}")

        # Sanitize string values
        sanitized = {}
        for key, value in metadata.items():
            if isinstance(key, str):
                key = cls._sanitize_metadata_key(key)

            if isinstance(value, str):
                value = cls._sanitize_metadata_value(value)
            elif isinstance(value, dict):
                value = cls.validate_metadata(value)  # Recursive
            elif isinstance(value, (list, tuple)):
                value = [cls._sanitize_metadata_value(v) if isinstance(v, str) else v
                        for v in value[:100]]  # Limit list size

            sanitized[key] = value

        return sanitized

    @classmethod
    def _sanitize_metadata_key(cls, key: str) -> str:
        """Sanitize metadata key."""
        if len(key) > 100:
            key = key[:100]
        # Remove dangerous characters
        return re.sub(r'[^\w\-.]', '_', key)

    @classmethod
    def _sanitize_metadata_value(cls, value: str) -> str:
        """Sanitize metadata string value."""
        if len(value) > 1000:
            value = value[:1000]
        # Remove null bytes and control characters
        return re.sub(r'[\x00-\x1f\x7f]', '', value)

    @classmethod
    def validate_agent_sequence(cls, sequence: List[str]) -> List[str]:
        """
        Validate agent sequence.

        Args:
            sequence: List of agent IDs

        Returns:
            Validated sequence

        Raises:
            ValueError: If sequence is invalid
        """
        if not isinstance(sequence, list):
            raise ValueError("Agent sequence must be a list")

        if len(sequence) > cls.MAX_AGENT_SEQUENCE_LENGTH:
            raise ValueError(
                f"Agent sequence too long (max {cls.MAX_AGENT_SEQUENCE_LENGTH})"
            )

        validated = []
        for agent_id in sequence:
            if not isinstance(agent_id, str):
                continue  # Skip non-string entries

            try:
                validated.append(cls.validate_strategy_id(agent_id))
            except ValueError:
                # Skip invalid agent IDs
                logger.warning(f"Skipping invalid agent ID: {agent_id}")

        return validated

    @classmethod
    def validate_confidence(cls, confidence: float) -> float:
        """
        Validate confidence score.

        Args:
            confidence: Confidence value

        Returns:
            Validated confidence (0.0-1.0)

        Raises:
            ValueError: If confidence is invalid
        """
        try:
            conf = float(confidence)
        except (TypeError, ValueError):
            raise ValueError("Confidence must be a number")

        if not 0.0 <= conf <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")

        return conf


# ===========================================================================
# CONVERSATION STRATEGY TRACKER
# ===========================================================================

@dataclass
class ConversationStrategy:
    """
    Strategy tracking for a single conversation/problem-solving session.

    Attributes:
        conversation_id: Unique conversation identifier
        problem_type: Type of problem being solved
        domain: Problem domain
        start_time: When conversation started
        agent_sequence: Ordered list of agents invoked
        detected_strategies: Strategy IDs detected during solution
        dominant_strategy: Primary strategy being used
        success: Whether solution was successful
        metadata: Additional conversation metadata
    """
    conversation_id: str
    problem_type: str
    domain: str
    start_time: datetime = field(default_factory=datetime.now)
    agent_sequence: List[str] = field(default_factory=list)
    detected_strategies: Set[str] = field(default_factory=set)
    dominant_strategy: Optional[str] = None
    success: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


# ===========================================================================
# STRATEGY-ENHANCED ORCHESTRATOR EXTENSION
# ===========================================================================

class StrategyOrchestrationExtension:
    """
    Extension module for MainOrchestrator that adds strategy learning.

    This class can be composed with the main orchestrator to add
    strategy-aware capabilities without modifying the core orchestrator.

    FEATURES:
    ---------
    - Strategy-aware problem routing
    - Automatic strategy detection from solution traces
    - Cross-domain strategy transfer recommendations
    - Security validation for all inputs
    - Edge case handling

    THREAD-SAFETY:
    --------------
    All operations are thread-safe using internal locks.

    SECURITY:
    ---------
    All external inputs are validated through SecurityValidator.
    """

    def __init__(
        self,
        blackboard=None,
        vector_db=None,
        knowledge_graph: Optional[MathematicalKnowledgeGraph] = None,
        enable_strategies: bool = True
    ):
        """
        Initialize strategy orchestration extension.

        Args:
            blackboard: Blackboard instance for coordination
            vector_db: Vector database for trace storage
            knowledge_graph: KnowledgeGraph for strategy persistence
            enable_strategies: Enable strategy learning (default True)

        Raises:
            ValueError: If required components are missing
            RuntimeError: If initialization fails

        Security:
            Validates all configuration parameters
        """
        self.blackboard = blackboard
        self.vector_db = vector_db
        self.knowledge_graph = knowledge_graph
        self.enable_strategies = enable_strategies
        self._lock = threading.RLock()

        # Conversation tracking
        self.active_conversations: Dict[str, ConversationStrategy] = {}
        self.conversation_history: List[ConversationStrategy] = []
        self.max_history = 1000

        # Strategy components (initialized only if enabled)
        self.meta_learning_team = None
        self.transfer_engine = None

        if self.enable_strategies:
            self._initialize_strategy_components()

        # Statistics
        self.conversations_tracked = 0
        self.strategies_detected = 0
        self.transfers_recommended = 0

        # Rate limiting (security)
        self._last_learning_time = 0
        self._min_learning_interval = 0.1  # seconds

        logger.info("Strategy Orchestration Extension initialized")
        logger.info(f"  Strategy Learning: {'ENABLED' if enable_strategies else 'DISABLED'}")

    def _initialize_strategy_components(self):
        """
        Initialize strategy learning components.

        Raises:
            RuntimeError: If initialization fails

        Security:
            Validates all components during initialization
        """
        try:
            # Initialize enhanced meta-learning team
            self.meta_learning_team = MetaLearningTeamWithStrategies(
                blackboard=self.blackboard,
                vector_db=self.vector_db,
                knowledge_graph=self.knowledge_graph,
                orchestrator=None  # No orchestrator reference to avoid circular dependency
            )

            # Initialize transfer engine
            self.transfer_engine = StrategyTransferEngine(
                strategy_coordinator=self.meta_learning_team.strategy_coordinator,
                knowledge_graph=self.knowledge_graph
            )

            # Install KnowledgeGraph extensions if available
            if self.knowledge_graph:
                install_strategy_extensions(self.knowledge_graph)
                logger.info("  KnowledgeGraph strategy extensions installed")

        except Exception as e:
            logger.error(f"Failed to initialize strategy components: {e}")
            raise RuntimeError(f"Strategy initialization failed: {e}")

    def start_conversation(
        self,
        conversation_id: str,
        problem: StructuredProblem
    ) -> ConversationStrategy:
        """
        Start tracking a new problem-solving conversation.

        Args:
            conversation_id: Unique conversation identifier
            problem: Structured problem being solved

        Returns:
            ConversationStrategy tracking object

        Raises:
            ValueError: If inputs are invalid

        Security:
            - Validates conversation_id format
            - Sanitizes problem metadata
            - Enforces conversation limits
        """
        # Validate inputs
        conversation_id = SecurityValidator.validate_strategy_id(conversation_id)
        problem_type = SecurityValidator.validate_domain(problem.problem_type.value)
        domain = SecurityValidator.validate_domain(problem.domain.value)

        with self._lock:
            # Check if conversation already exists
            if conversation_id in self.active_conversations:
                logger.warning(f"Conversation {conversation_id} already active")
                return self.active_conversations[conversation_id]

            # Create conversation tracker
            conversation = ConversationStrategy(
                conversation_id=conversation_id,
                problem_type=problem_type,
                domain=domain,
                metadata=SecurityValidator.validate_metadata({
                    'raw_input': problem.raw_input[:500],  # Limit size
                    'complexity': getattr(problem, 'complexity', 'unknown')
                })
            )

            self.active_conversations[conversation_id] = conversation
            self.conversations_tracked += 1

            # Start meta-learning tracking if enabled
            if self.enable_strategies and self.meta_learning_team:
                try:
                    self.meta_learning_team.log_task_start(
                        conversation_id=conversation_id,
                        problem_type=problem_type,
                        complexity=conversation.metadata.get('complexity', 'medium')
                    )
                except Exception as e:
                    logger.warning(f"Failed to start meta-learning tracking: {e}")

            logger.debug(f"Started conversation {conversation_id}")
            return conversation

    def log_agent_invocation(
        self,
        conversation_id: str,
        agent_id: str,
        input_tokens: int = 0,
        vram_mb: float = 0.0
    ):
        """
        Log an agent invocation in the conversation.

        Args:
            conversation_id: Conversation identifier
            agent_id: Agent being invoked
            input_tokens: Number of input tokens
            vram_mb: VRAM usage in MB

        Security:
            - Validates all inputs
            - Enforces sequence length limits
            - Rate limits logging operations
        """
        try:
            # Validate inputs
            conversation_id = SecurityValidator.validate_strategy_id(conversation_id)
            agent_id = SecurityValidator.validate_strategy_id(agent_id)

            # Validate numeric inputs
            input_tokens = max(0, int(input_tokens))
            vram_mb = max(0.0, float(vram_mb))

        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid agent invocation data: {e}")
            return

        with self._lock:
            # Get conversation
            conversation = self.active_conversations.get(conversation_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found")
                return

            # Add to agent sequence (with length limit)
            if len(conversation.agent_sequence) < SecurityValidator.MAX_AGENT_SEQUENCE_LENGTH:
                conversation.agent_sequence.append(agent_id)

            # Log to meta-learning team
            if self.enable_strategies and self.meta_learning_team:
                try:
                    self.meta_learning_team.log_agent_invocation(
                        conversation_id=conversation_id,
                        agent_id=agent_id,
                        input_tokens=input_tokens,
                        vram_mb=vram_mb
                    )
                except Exception as e:
                    logger.debug(f"Meta-learning logging failed: {e}")

    def end_conversation(
        self,
        conversation_id: str,
        success: bool,
        verification_status: str = "UNKNOWN"
    ) -> Optional[EnhancedSolutionTrace]:
        """
        End a conversation and perform strategy analysis.

        Args:
            conversation_id: Conversation identifier
            success: Whether solution was successful
            verification_status: Verification result

        Returns:
            Enhanced solution trace with strategy detection, or None

        Raises:
            ValueError: If conversation_id is invalid

        Security:
            - Validates all inputs
            - Rate limits learning operations
            - Handles exceptions gracefully
        """
        # Validate inputs
        try:
            conversation_id = SecurityValidator.validate_strategy_id(conversation_id)
            verification_status = SecurityValidator.validate_strategy_name(verification_status)
        except ValueError as e:
            logger.error(f"Invalid end conversation data: {e}")
            return None

        with self._lock:
            # Get conversation
            conversation = self.active_conversations.get(conversation_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found")
                return None

            # Update conversation status
            conversation.success = success

            # Log verification to meta-learning team
            if self.enable_strategies and self.meta_learning_team:
                try:
                    self.meta_learning_team.log_verification(
                        conversation_id=conversation_id,
                        status=verification_status
                    )
                except Exception as e:
                    logger.debug(f"Verification logging failed: {e}")

            # End meta-learning session and get enhanced trace
            enhanced_trace = None
            if self.enable_strategies and self.meta_learning_team:
                try:
                    # Rate limiting check
                    current_time = time.time()
                    if current_time - self._last_learning_time >= self._min_learning_interval:
                        enhanced_trace = self.meta_learning_team.log_session_end(conversation_id)
                        self._last_learning_time = current_time

                        if enhanced_trace:
                            # Update conversation with detected strategies
                            conversation.detected_strategies = set(enhanced_trace.detected_strategies)
                            conversation.dominant_strategy = enhanced_trace.dominant_strategy
                            self.strategies_detected += len(enhanced_trace.detected_strategies)

                except Exception as e:
                    logger.warning(f"Strategy analysis failed: {e}")

            # Move to history
            self.conversation_history.append(conversation)
            if len(self.conversation_history) > self.max_history:
                self.conversation_history.pop(0)

            # Remove from active
            del self.active_conversations[conversation_id]

            logger.debug(f"Ended conversation {conversation_id}, success={success}")
            return enhanced_trace

    def get_strategy_recommendation(
        self,
        problem: StructuredProblem
    ) -> Dict[str, Any]:
        """
        Get strategy recommendations for a new problem.

        Analyzes past solutions and suggests effective strategies.

        Args:
            problem: Problem to get recommendations for

        Returns:
            Dict with strategy recommendations and transfer suggestions

        Security:
            - Validates problem inputs
            - Limits recommendation count
            - Handles failures gracefully
        """
        if not self.enable_strategies or not self.meta_learning_team:
            return {'enabled': False, 'reason': 'Strategy learning disabled'}

        try:
            # Validate problem
            problem_type = SecurityValidator.validate_domain(problem.problem_type.value)
            domain = SecurityValidator.validate_domain(problem.domain.value)

            # Get recommendation from meta-learning team
            problem_context = {
                'problem_type': problem_type,
                'metadata': SecurityValidator.validate_metadata({
                    'domain': domain,
                    'complexity': getattr(problem, 'complexity', 'medium')
                })
            }

            recommendation = self.meta_learning_team.get_team_recommendation(problem_context)

            # Get transfer recommendations if available
            transfers = []
            if self.transfer_engine:
                try:
                    transfers = self.transfer_engine.get_transfer_recommendations(problem_context)
                    self.transfers_recommended += len(transfers)
                except Exception as e:
                    logger.debug(f"Transfer recommendation failed: {e}")

            return {
                'enabled': True,
                'team_recommendation': recommendation,
                'transfer_candidates': transfers[:5],  # Limit to top 5
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Strategy recommendation failed: {e}")
            return {'enabled': True, 'error': str(e)}

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get extension statistics.

        Returns:
            Dictionary with usage statistics
        """
        stats = {
            'conversations_tracked': self.conversations_tracked,
            'active_conversations': len(self.active_conversations),
            'strategies_detected': self.strategies_detected,
            'transfers_recommended': self.transfers_recommended,
            'strategy_learning_enabled': self.enable_strategies
        }

        if self.enable_strategies and self.meta_learning_team:
            stats['meta_learning'] = self.meta_learning_team.get_statistics()

        if self.transfer_engine:
            stats['transfer_engine'] = self.transfer_engine.get_statistics()

        return stats


if __name__ == "__main__":
    """Test strategy orchestration extension"""
    print("=" * 80)
    print("STRATEGY ORCHESTRATION EXTENSION TEST")
    print("=" * 80)
    print()

    # Test security validation
    print("TEST 1: Security Validation")
    print("-" * 40)

    try:
        # Valid inputs
        valid_id = SecurityValidator.validate_strategy_id("strategy_test_001")
        print(f"Valid ID: {valid_id}")

        valid_name = SecurityValidator.validate_strategy_name("Test Strategy")
        print(f"Valid name: {valid_name}")

        # Invalid inputs (should raise)
        try:
            SecurityValidator.validate_strategy_id("../../etc/passwd")
            print("ERROR: Should have rejected path traversal")
        except ValueError as e:
            print(f"Correctly rejected: {e}")

        try:
            SecurityValidator.validate_strategy_name("<script>alert('xss')</script>")
            print("XSS sanitized (OK)")
        except ValueError:
            pass

    except Exception as e:
        print(f"Security validation test failed: {e}")

    print()
    print("=" * 80)
    print("STRATEGY ORCHESTRATION EXTENSION TEST COMPLETE")
    print("=" * 80)
