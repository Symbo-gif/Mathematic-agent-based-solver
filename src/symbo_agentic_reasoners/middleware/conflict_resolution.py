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
CONFLICT RESOLUTION TEAM - "The Supreme Court"
===============================================

Phase 4 Step 1: Evidence-Based Adjudication System

PURPOSE:
-------
Construct a three-agent team that replaces random selection with structured,
evidence-based adjudication when agents produce conflicting results.

IMPLEMENTS:
----------
FMAD (Feedback-based Multi-Agent Debate) protocol - creating a judicial
system for mathematical disputes.

WHY THIS MATTERS:
----------------
In a high-density ecosystem of 40-50 specialized agents, disagreements are
structurally inevitable. The Symbolic Integration Agent may return
"No closed-form solution exists" while the Numerical Agent finds a valid
approximation to arbitrary precision. Without this team, the system either:
- Randomly selects an answer (compromising accuracy)
- Silently ignores conflicts (compromising reliability)
- Crashes entirely (compromising availability)

AGENTS:
------
1. Debate Moderator: FMAD Protocol - manages the "courtroom"
2. Evidence Weigher: Hierarchy of Mathematical Truth evaluation
3. Consensus Builder: Expertise-weighted voting for tied cases

REFERENCE:
---------
- Phase_4_Build_Order_Breakdown.md: Step 1
- Phase 4 transforms this collection of agents into a Self-Correction Engine.md
"""

import sys
import os
import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
import uuid
import threading

# Add parent paths for imports
# Path manipulation removed - using package imports
# Path manipulation removed - using package imports

# Get module logger
logger = logging.getLogger('symbo_agentic_reasoners.phase4.conflict_resolution')


# ===========================================================================
# ENUMS AND DATA CLASSES
# ===========================================================================

class EvidenceType(Enum):
    """
    Hierarchy of Mathematical Truth - IMMUTABLE

    This hierarchy is hard-coded and cannot be changed. It represents
    the fundamental ordering of evidence quality in mathematical reasoning.

    ORDERING:
    --------
    FORMAL_PROOF > SYMBOLIC_DERIVATION > NUMERICAL_APPROXIMATION > HEURISTIC_GUESS

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 1.2 (Evidence Weigher)
    "Formal Proof (Ax-Prover verified) > Symbolic Derivation >
     Numerical Approximation > Heuristic Guess"
    """
    FORMAL_PROOF = 4          # Ax-Prover verified - highest authority
    SYMBOLIC_DERIVATION = 3   # Algebraic/symbolic methods
    NUMERICAL_APPROXIMATION = 2  # Numerical methods with tolerance
    HEURISTIC_GUESS = 1       # Pattern matching, intuition


class ConflictStatus(Enum):
    """Status of a conflict case"""
    DETECTED = auto()         # Conflict just detected
    ARGUMENTS_REQUESTED = auto()  # Waiting for agent arguments
    ARGUMENTS_RECEIVED = auto()   # All arguments collected
    WEIGHING = auto()         # Evidence Weigher analyzing
    CONSENSUS_REQUIRED = auto()   # Same hierarchy level - needs voting
    RESOLVED = auto()         # Final ruling issued
    TIMEOUT = auto()          # Resolution timed out


@dataclass
class ConflictCase:
    """
    Represents a dispute between agents

    Captures all information about a conflict including the conflicting
    results, arguments from each side, and the final ruling.

    FIELDS:
    ------
    - case_id: Unique case identifier
    - subtask_id: The subtask that produced conflicting results
    - conflicting_results: List of results from different agents
    - arguments: Collected arguments from agents
    - ruling: Final ruling (if resolved)
    - status: Current status of the case
    - timestamp: When conflict was detected
    - domain: Mathematical domain of the problem
    """
    case_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subtask_id: str = ""
    conversation_id: str = ""
    conflicting_results: List[Dict] = field(default_factory=list)
    arguments: List[Dict] = field(default_factory=list)
    ruling: Optional[Dict] = None
    status: ConflictStatus = ConflictStatus.DETECTED
    timestamp: datetime = field(default_factory=datetime.now)
    domain: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_argument(self, argument: Dict) -> None:
        """Add an argument from an agent"""
        self.arguments.append(argument)
        if len(self.arguments) >= len(self.conflicting_results):
            self.status = ConflictStatus.ARGUMENTS_RECEIVED

    def set_ruling(self, ruling: Dict) -> None:
        """Set the final ruling"""
        self.ruling = ruling
        self.status = ConflictStatus.RESOLVED


@dataclass
class Ruling:
    """
    A conflict resolution ruling

    FIELDS:
    ------
    - ruling_type: 'AUTOMATIC' (clear hierarchy winner) or 'CONSENSUS' (voting)
    - winner_agent: Agent ID of the winner
    - winning_result: The accepted result
    - evidence_type: Type of evidence that won
    - rationale: Explanation of the ruling
    - confidence: Confidence in the ruling (0-1)
    - vote_breakdown: Details of voting (if consensus)
    """
    ruling_type: str
    winner_agent: str
    winning_result: Any
    evidence_type: str
    rationale: str
    confidence: float = 1.0
    vote_breakdown: Optional[Dict] = None


# ===========================================================================
# AGENT 1.1: THE DEBATE MODERATOR
# ===========================================================================

class DebateModerator:
    """
    Agent 1.1: FMAD Protocol Implementation

    DIRECTIVE:
    ---------
    Implement the Feedback-based Multi-Agent Debate (FMAD) protocol.
    This agent does not solve mathematics; it manages the "courtroom"
    where disputes are resolved.

    TRIGGER:
    -------
    When the Blackboard detects conflicting results for the same subtask-id
    (two or more agents posting different solutions to identical problems).

    MECHANISM:
    ---------
    1. Freeze workflow
    2. Issue PROPOSE-ARGUMENT commands to conflicting agents
    3. Collect structured justifications
    4. Forward to Evidence Weigher

    OUTPUT:
    ------
    Structured debate transcript posted to Blackboard for analysis.

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 1.1
    """

    def __init__(self, blackboard=None, acc=None, df=None):
        """
        Initialize Debate Moderator

        Args:
            blackboard: Phase 0 Blackboard instance
            acc: Agent Communication Channel
            df: Directory Facilitator
        """
        self.blackboard = blackboard
        self.acc = acc
        self.df = df
        self.active_cases: Dict[str, ConflictCase] = {}
        self._lock = threading.RLock()

        # Statistics
        self.conflicts_detected = 0
        self.arguments_collected = 0
        self.cases_forwarded = 0

        # Register with DF if available
        if self.df:
            self._register_with_df()

        # Subscribe to conflicts if blackboard available
        if self.blackboard:
            self._subscribe_to_conflicts()

        print("    [OK] Debate Moderator Agent initialized")

    def _register_with_df(self):
        """Register adjudication service with Directory Facilitator"""
        try:
            from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
                create_service_registration
            )
            registration = create_service_registration(
                service_type='governance.conflict_resolution',
                agent_id='debate_moderator_001',
                algorithm='fmad',
                cost='low',
                role='moderator',
                protocol='FMAD'
            )
            self.df.register(registration)
        except Exception as e:
            logger.warning(f"Could not register with DF: {type(e).__name__}: {e}")

    def _subscribe_to_conflicts(self):
        """Subscribe to CONFLICT_FLAG on Blackboard"""
        try:
            self.blackboard.subscribe(
                agent_id='debate_moderator_001',
                tags=['CONFLICT_FLAG'],
                callback=self._on_conflict_flag
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to conflicts: {type(e).__name__}: {e}")

    def _on_conflict_flag(self, entry):
        """Callback when CONFLICT_FLAG is posted to Blackboard"""
        if hasattr(entry, 'metadata'):
            conflict_data = entry.metadata.get('conflict_data', {})
            if conflict_data:
                self.on_conflict_detected(conflict_data)

    def on_conflict_detected(self, conflict_entry: Dict) -> str:
        """
        Trigger FMAD protocol when conflict detected

        This is the main entry point for conflict resolution.
        Called when the system detects conflicting results.

        Args:
            conflict_entry: Dictionary containing:
                - subtask_id: ID of the subtask with conflicts
                - results: List of conflicting results from agents
                - conversation_id: Optional conversation tracking ID
                - domain: Mathematical domain

        Returns:
            case_id: Unique identifier for this conflict case
        """
        with self._lock:
            self.conflicts_detected += 1

            # Create conflict case
            case = ConflictCase(
                subtask_id=conflict_entry.get('subtask_id', ''),
                conversation_id=conflict_entry.get('conversation_id', ''),
                conflicting_results=conflict_entry.get('results', []),
                domain=conflict_entry.get('domain', 'general')
            )
            case.status = ConflictStatus.ARGUMENTS_REQUESTED
            self.active_cases[case.case_id] = case

            # FREEZE workflow by posting to Blackboard
            if self.blackboard:
                self._post_workflow_freeze(case)

            # Issue PROPOSE-ARGUMENT to each conflicting agent
            for result in case.conflicting_results:
                self._request_argument(
                    result.get('agent_id', 'unknown'),
                    case.case_id,
                    result
                )

            print(f"    [FMAD] Conflict detected: {len(case.conflicting_results)} agents disagree")
            print(f"           Case ID: {case.case_id[:8]}...")

            return case.case_id

    def _post_workflow_freeze(self, case: ConflictCase):
        """Post WORKFLOW_FREEZE to Blackboard"""
        try:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType
            entry = create_entry(
                entry_type=EntryType.TASK,
                content={'freeze': True, 'case_id': case.case_id},
                author_agent='debate_moderator_001',
                conversation_id=case.conversation_id,
                tags=['WORKFLOW_FREEZE', case.case_id],
                metadata={
                    'entry_type': 'WORKFLOW_FREEZE',
                    'case_id': case.case_id,
                    'status': 'ADJUDICATION_IN_PROGRESS'
                }
            )
            self.blackboard.post(entry)
        except Exception as e:
            logger.debug(f"Could not post to blackboard: {type(e).__name__}: {e}")

    def _request_argument(self, agent_id: str, case_id: str, result: Dict):
        """
        Send FIPA-ACL PROPOSE-ARGUMENT command

        Requests that the agent provide justification for their result.
        """
        message = {
            'performative': 'REQUEST',
            'sender': 'debate_moderator_001',
            'receiver': agent_id,
            'conversation_id': case_id,
            'content': {
                'action': 'PROPOSE-ARGUMENT',
                'case_id': case_id,
                'your_result': result.get('result'),
                'required_fields': [
                    'method_used',
                    'assumptions',
                    'evidence_type',
                    'confidence'
                ]
            },
            'protocol': 'fipa-fmad'
        }

        # Send via ACC if available
        if self.acc:
            try:
                self.acc.send(message)
            except Exception as e:
                logger.warning(f"Failed to send ACC message: {type(e).__name__}: {e}")

        # For immediate testing, auto-generate argument if result has method info
        if 'method_used' in result or 'evidence_type' in result:
            argument = {
                'agent_id': agent_id,
                'result': result.get('result'),
                'method_used': result.get('method_used', 'unknown'),
                'assumptions': result.get('assumptions', []),
                'evidence_type': result.get('evidence_type', ''),
                'confidence': result.get('confidence', 0.5),
                'ax_prover_verified': result.get('ax_prover_verified', False)
            }
            self.receive_argument(case_id, argument)

    def receive_argument(self, case_id: str, argument: Dict) -> bool:
        """
        Collect argument from agent

        Called when an agent submits their argument for a conflict case.

        Args:
            case_id: The conflict case ID
            argument: Agent's argument containing method_used, evidence_type, etc.

        Returns:
            True if all arguments collected and case forwarded to weigher
        """
        with self._lock:
            if case_id not in self.active_cases:
                return False

            case = self.active_cases[case_id]
            case.add_argument(argument)
            self.arguments_collected += 1

            # Check if all arguments received
            if len(case.arguments) >= len(case.conflicting_results):
                return self._forward_to_weigher(case)

            return False

    def _forward_to_weigher(self, case: ConflictCase) -> bool:
        """Forward complete case to Evidence Weigher"""
        case.status = ConflictStatus.WEIGHING
        self.cases_forwarded += 1

        # Post to Blackboard for Evidence Weigher
        if self.blackboard:
            try:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType
                entry = create_entry(
                    entry_type=EntryType.TASK,
                    content=self._serialize_case(case),
                    author_agent='debate_moderator_001',
                    conversation_id=case.conversation_id,
                    tags=['CASE_FOR_WEIGHING', case.case_id],
                    metadata={
                        'entry_type': 'CASE_FOR_WEIGHING',
                        'case_id': case.case_id,
                        'status': 'AWAITING_RULING'
                    }
                )
                self.blackboard.post(entry)
            except Exception as e:
                logger.debug(f"Could not post case to blackboard: {type(e).__name__}: {e}")

        print(f"    [FMAD] Case {case.case_id[:8]}... forwarded to Evidence Weigher")
        return True

    def _serialize_case(self, case: ConflictCase) -> Dict:
        """Serialize case for Blackboard storage"""
        return {
            'case_id': case.case_id,
            'subtask_id': case.subtask_id,
            'conversation_id': case.conversation_id,
            'conflicting_results': case.conflicting_results,
            'arguments': case.arguments,
            'status': case.status.name,
            'domain': case.domain,
            'timestamp': case.timestamp.isoformat()
        }

    def get_case(self, case_id: str) -> Optional[ConflictCase]:
        """Retrieve a case by ID"""
        return self.active_cases.get(case_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get moderator statistics"""
        return {
            'conflicts_detected': self.conflicts_detected,
            'arguments_collected': self.arguments_collected,
            'cases_forwarded': self.cases_forwarded,
            'active_cases': len(self.active_cases)
        }


# ===========================================================================
# AGENT 1.2: THE EVIDENCE WEIGHER
# ===========================================================================

class EvidenceWeigher:
    """
    Agent 1.2: Logic Engine for Justification Evaluation

    DIRECTIVE:
    ---------
    Build the logic engine that evaluates the quality of justifications,
    not merely the results themselves.

    CRITICAL IMPLEMENTATION - HIERARCHY OF MATHEMATICAL TRUTH:
    ---------------------------------------------------------
    Hard-coded IMMUTABLE hierarchy:
        Formal Proof (Ax-Prover verified) > Symbolic Derivation >
        Numerical Approximation > Heuristic Guess

    AUTOMATIC RULING:
    ----------------
    If Agent A provides a formal proof and Agent B provides a heuristic guess,
    the Evidence Weigher rules in favor of Agent A automatically, regardless
    of Agent B's confidence score.

    OUTPUT:
    ------
    RULING message with winning_agent, evidence_type, and confidence_level.

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 1.2
    """

    # IMMUTABLE: Hierarchy of Mathematical Truth
    # DO NOT MODIFY THIS HIERARCHY
    TRUTH_HIERARCHY = {
        EvidenceType.FORMAL_PROOF: 4,
        EvidenceType.SYMBOLIC_DERIVATION: 3,
        EvidenceType.NUMERICAL_APPROXIMATION: 2,
        EvidenceType.HEURISTIC_GUESS: 1
    }

    def __init__(self, blackboard=None):
        """
        Initialize Evidence Weigher

        Args:
            blackboard: Phase 0 Blackboard instance
        """
        self.blackboard = blackboard

        # Statistics
        self.cases_evaluated = 0
        self.automatic_rulings = 0
        self.consensus_required = 0

        if self.blackboard:
            self._subscribe_to_cases()

        print("    [OK] Evidence Weigher Agent initialized")
        print("         Truth Hierarchy: FORMAL_PROOF > SYMBOLIC > NUMERICAL > HEURISTIC")

    def _subscribe_to_cases(self):
        """Subscribe to CASE_FOR_WEIGHING on Blackboard"""
        try:
            self.blackboard.subscribe(
                agent_id='evidence_weigher_001',
                tags=['CASE_FOR_WEIGHING'],
                callback=self._on_case_for_weighing
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to cases: {type(e).__name__}: {e}")

    def _on_case_for_weighing(self, entry):
        """Callback for cases posted to Blackboard"""
        if hasattr(entry, 'content') and isinstance(entry.content, dict):
            self.evaluate_case(entry.content)

    def evaluate_case(self, case_data: Dict) -> Ruling:
        """
        Evaluate arguments based on evidence hierarchy

        This is the core logic of the Evidence Weigher. It classifies
        each argument's evidence type and applies the immutable hierarchy.

        Args:
            case_data: Dictionary containing case information and arguments

        Returns:
            Ruling object with winner and rationale
        """
        self.cases_evaluated += 1
        arguments = case_data.get('arguments', [])

        if not arguments:
            return Ruling(
                ruling_type='NO_ARGUMENTS',
                winner_agent='none',
                winning_result=None,
                evidence_type='NONE',
                rationale='No arguments provided',
                confidence=0.0
            )

        # Classify each argument's evidence type
        classified = []
        for arg in arguments:
            evidence_type = self._classify_evidence(arg)
            hierarchy_score = self.TRUTH_HIERARCHY[evidence_type]

            classified.append({
                'agent_id': arg.get('agent_id', 'unknown'),
                'result': arg.get('result'),
                'evidence_type': evidence_type,
                'hierarchy_score': hierarchy_score,
                'confidence': arg.get('confidence', 0.5),
                'method_used': arg.get('method_used', 'unknown')
            })

        # Sort by hierarchy score (highest wins), then by confidence
        classified.sort(
            key=lambda x: (x['hierarchy_score'], x['confidence']),
            reverse=True
        )

        winner = classified[0]

        # AUTOMATIC RULING if clear hierarchy difference
        if len(classified) >= 2:
            runner_up = classified[1]

            if winner['hierarchy_score'] > runner_up['hierarchy_score']:
                # Clear winner by evidence hierarchy
                self.automatic_rulings += 1
                ruling = Ruling(
                    ruling_type='AUTOMATIC',
                    winner_agent=winner['agent_id'],
                    winning_result=winner['result'],
                    evidence_type=winner['evidence_type'].name,
                    rationale=f"Higher evidence type: {winner['evidence_type'].name} "
                              f"beats {runner_up['evidence_type'].name}",
                    confidence=0.95
                )
            else:
                # Same hierarchy level - requires consensus
                self.consensus_required += 1
                tied = [c for c in classified
                       if c['hierarchy_score'] == winner['hierarchy_score']]
                ruling = Ruling(
                    ruling_type='CONSENSUS_REQUIRED',
                    winner_agent=winner['agent_id'],  # Tentative
                    winning_result=winner['result'],
                    evidence_type=winner['evidence_type'].name,
                    rationale=f"Tied evidence types ({winner['evidence_type'].name}), "
                              f"consensus voting required",
                    confidence=winner['confidence']
                )
        else:
            # Single argument - automatic win
            self.automatic_rulings += 1
            ruling = Ruling(
                ruling_type='AUTOMATIC',
                winner_agent=winner['agent_id'],
                winning_result=winner['result'],
                evidence_type=winner['evidence_type'].name,
                rationale='Single argument - no conflict',
                confidence=0.9
            )

        # Post ruling to Blackboard
        if self.blackboard:
            self._post_ruling(case_data.get('case_id', ''), ruling, classified)

        print(f"    [WEIGHER] Ruling: {ruling.ruling_type}")
        print(f"              Winner: {ruling.winner_agent}")
        print(f"              Evidence: {ruling.evidence_type}")

        return ruling

    def _classify_evidence(self, argument: Dict) -> EvidenceType:
        """
        Classify argument into evidence hierarchy

        Classification rules:
        1. If ax_prover_verified == True -> FORMAL_PROOF
        2. If method contains 'symbolic'/'algebraic'/'closed-form' -> SYMBOLIC_DERIVATION
        3. If method contains 'numerical'/'approximation' -> NUMERICAL_APPROXIMATION
        4. Otherwise -> HEURISTIC_GUESS
        """
        # Check for explicit evidence_type first
        explicit_type = argument.get('evidence_type', '').upper()
        if explicit_type:
            for et in EvidenceType:
                if et.name == explicit_type:
                    return et

        # Check for formal proof verification
        if argument.get('ax_prover_verified', False):
            return EvidenceType.FORMAL_PROOF

        # Classify by method
        method = argument.get('method_used', '').lower()

        symbolic_indicators = [
            'symbolic', 'algebraic', 'closed-form', 'exact',
            'analytic', 'risch', 'groebner', 'factorization'
        ]
        numerical_indicators = [
            'numerical', 'approximation', 'newton', 'iterative',
            'quadrature', 'monte carlo', 'tolerance'
        ]

        if any(ind in method for ind in symbolic_indicators):
            return EvidenceType.SYMBOLIC_DERIVATION
        elif any(ind in method for ind in numerical_indicators):
            return EvidenceType.NUMERICAL_APPROXIMATION
        else:
            return EvidenceType.HEURISTIC_GUESS

    def _post_ruling(self, case_id: str, ruling: Ruling, classified: List[Dict]):
        """Post ruling to Blackboard"""
        try:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType
            entry = create_entry(
                entry_type=EntryType.TASK,
                content={
                    'case_id': case_id,
                    'ruling_type': ruling.ruling_type,
                    'winner': ruling.winner_agent,
                    'winning_result': ruling.winning_result,
                    'evidence_type': ruling.evidence_type,
                    'rationale': ruling.rationale,
                    'confidence': ruling.confidence,
                    'classification': classified
                },
                author_agent='evidence_weigher_001',
                conversation_id=case_id,
                tags=['RULING', case_id],
                metadata={
                    'entry_type': 'RULING',
                    'ruling_type': ruling.ruling_type
                }
            )
            self.blackboard.post(entry)
        except Exception as e:
            logger.debug(f"Could not post ruling to blackboard: {type(e).__name__}: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get weigher statistics"""
        return {
            'cases_evaluated': self.cases_evaluated,
            'automatic_rulings': self.automatic_rulings,
            'consensus_required': self.consensus_required
        }


# ===========================================================================
# AGENT 1.3: THE CONSENSUS BUILDER
# ===========================================================================

class ConsensusBuilder:
    """
    Agent 1.3: Voting with Expertise Weighting

    DIRECTIVE:
    ---------
    Implement a "Voting with Expertise Weighting" mechanism for cases
    where no formal proof exists and evidence types are tied.

    EXPERTISE WEIGHTING LOGIC:
    -------------------------
    Domain Supervisors receive higher voting weight in their domain:
    - Calculus Supervisor's vote counts x2 on integral disputes
    - Algebra Supervisor's vote counts x2 on polynomial disputes
    - etc.

    OUTPUT:
    ------
    Synthesized final answer with CONFIDENCE: COMPOSITE tag indicating
    aggregated origin.

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 1.3
    """

    # Domain expertise multipliers
    EXPERTISE_WEIGHTS = {
        'calculus_supervisor': {
            'calculus': 2.0, 'integration': 2.0, 'differentiation': 2.0,
            'limits': 1.8, 'series': 1.5, 'analysis': 1.5
        },
        'algebra_supervisor': {
            'algebra': 2.0, 'polynomial': 2.0, 'equation': 1.8,
            'factorization': 1.5, 'simplification': 1.5
        },
        'linear_algebra_supervisor': {
            'matrix': 2.0, 'vector': 2.0, 'linear_algebra': 2.0,
            'eigenvalue': 1.8, 'decomposition': 1.5
        },
        'statistics_supervisor': {
            'probability': 2.0, 'statistics': 2.0, 'distribution': 1.8,
            'bayesian': 1.5, 'hypothesis': 1.5
        },
        'discrete_supervisor': {
            'combinatorics': 2.0, 'graph': 2.0, 'discrete': 2.0,
            'counting': 1.5, 'permutation': 1.5
        }
    }

    def __init__(self, blackboard=None, df=None):
        """
        Initialize Consensus Builder

        Args:
            blackboard: Phase 0 Blackboard instance
            df: Directory Facilitator for expertise lookup
        """
        self.blackboard = blackboard
        self.df = df

        # Statistics
        self.consensus_votes = 0
        self.tie_breakers = 0

        if self.blackboard:
            self._subscribe_to_rulings()

        print("    [OK] Consensus Builder Agent initialized")

    def _subscribe_to_rulings(self):
        """Subscribe to RULING events that require consensus"""
        try:
            self.blackboard.subscribe(
                agent_id='consensus_builder_001',
                tags=['RULING'],
                callback=self._on_ruling
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to rulings: {type(e).__name__}: {e}")

    def _on_ruling(self, entry):
        """Handle rulings that require consensus"""
        if hasattr(entry, 'content') and isinstance(entry.content, dict):
            ruling_data = entry.content
            if ruling_data.get('ruling_type') == 'CONSENSUS_REQUIRED':
                self.build_consensus(ruling_data)

    def build_consensus(self, ruling_data: Dict) -> Ruling:
        """
        Build consensus through expertise-weighted voting

        Called when Evidence Weigher determines tied evidence types.

        Args:
            ruling_data: Dictionary containing case information and tied agents

        Returns:
            Final Ruling with consensus result
        """
        self.consensus_votes += 1

        case_id = ruling_data.get('case_id', '')
        classification = ruling_data.get('classification', [])
        domain = ruling_data.get('domain', 'general')

        # Get tied agents (same hierarchy score)
        top_score = classification[0]['hierarchy_score'] if classification else 0
        tied_agents = [c for c in classification if c['hierarchy_score'] == top_score]

        # Calculate weighted votes
        weighted_votes = {}
        for agent_data in tied_agents:
            agent_id = agent_data['agent_id']
            base_confidence = agent_data.get('confidence', 0.5)

            # Get expertise weight for this agent in this domain
            weight = self._get_expertise_weight(agent_id, domain)

            weighted_score = base_confidence * weight
            weighted_votes[agent_id] = {
                'result': agent_data['result'],
                'base_confidence': base_confidence,
                'expertise_weight': weight,
                'weighted_score': weighted_score,
                'evidence_type': agent_data['evidence_type'].name
            }

        # Select winner by weighted score
        if weighted_votes:
            winner_id = max(weighted_votes.keys(),
                          key=lambda k: weighted_votes[k]['weighted_score'])
            winner_data = weighted_votes[winner_id]

            # Check for true tie
            max_score = winner_data['weighted_score']
            true_ties = [aid for aid, data in weighted_votes.items()
                        if abs(data['weighted_score'] - max_score) < 0.001]

            if len(true_ties) > 1:
                self.tie_breakers += 1
                # True tie - use the one with higher raw confidence
                winner_id = max(true_ties,
                              key=lambda k: weighted_votes[k]['base_confidence'])
                winner_data = weighted_votes[winner_id]
        else:
            # Fallback
            winner_id = 'none'
            winner_data = {
                'result': None,
                'evidence_type': 'NONE',
                'weighted_score': 0.0
            }

        ruling = Ruling(
            ruling_type='CONSENSUS',
            winner_agent=winner_id,
            winning_result=winner_data['result'],
            evidence_type=winner_data.get('evidence_type', 'UNKNOWN'),
            rationale=f"Consensus vote: weighted score {winner_data['weighted_score']:.3f}",
            confidence=min(0.85, winner_data['weighted_score']),  # Cap at 0.85 for consensus
            vote_breakdown=weighted_votes
        )

        # Post final ruling to Blackboard
        if self.blackboard:
            self._post_final_ruling(case_id, ruling)

        print(f"    [CONSENSUS] Winner: {winner_id}")
        print(f"                Score: {winner_data['weighted_score']:.3f}")

        return ruling

    def _get_expertise_weight(self, agent_id: str, domain: str) -> float:
        """
        Get expertise multiplier for agent in domain

        Looks up the agent's expertise weight for the given domain.
        Returns 1.0 for non-supervisors or unknown domains.
        """
        agent_lower = agent_id.lower()
        domain_lower = domain.lower()

        for supervisor_pattern, domains in self.EXPERTISE_WEIGHTS.items():
            if supervisor_pattern in agent_lower:
                # Found a supervisor - check domain expertise
                for domain_pattern, weight in domains.items():
                    if domain_pattern in domain_lower:
                        return weight
                return 1.2  # Supervisor but not exact domain match

        # Check if agent name suggests domain expertise
        if domain_lower in agent_lower:
            return 1.3  # Agent name matches domain

        return 1.0  # Default weight for non-supervisors

    def _post_final_ruling(self, case_id: str, ruling: Ruling):
        """Post final ruling and unfreeze workflow"""
        try:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType

            # Post final ruling
            ruling_entry = create_entry(
                entry_type=EntryType.TASK,
                content={
                    'case_id': case_id,
                    'ruling_type': ruling.ruling_type,
                    'winner': ruling.winner_agent,
                    'winning_result': ruling.winning_result,
                    'confidence_tag': 'COMPOSITE',
                    'vote_breakdown': ruling.vote_breakdown
                },
                author_agent='consensus_builder_001',
                conversation_id=case_id,
                tags=['FINAL_RULING', case_id],
                metadata={
                    'entry_type': 'FINAL_RULING',
                    'status': 'RESOLVED'
                }
            )
            self.blackboard.post(ruling_entry)

            # Post workflow unfreeze
            unfreeze_entry = create_entry(
                entry_type=EntryType.TASK,
                content={
                    'case_id': case_id,
                    'accepted_result': ruling.winning_result
                },
                author_agent='consensus_builder_001',
                conversation_id=case_id,
                tags=['WORKFLOW_UNFREEZE', case_id],
                metadata={
                    'entry_type': 'WORKFLOW_UNFREEZE',
                    'accepted_result': ruling.winning_result
                }
            )
            self.blackboard.post(unfreeze_entry)

        except Exception as e:
            logger.error(f"Failed to finalize consensus ruling: {type(e).__name__}: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get consensus builder statistics"""
        return {
            'consensus_votes': self.consensus_votes,
            'tie_breakers': self.tie_breakers
        }


# ===========================================================================
# CONFLICT RESOLUTION TEAM COORDINATOR
# ===========================================================================

class ConflictResolutionTeam:
    """
    Coordinator for the Conflict Resolution Team ("The Supreme Court")

    Brings together the three agents:
    1. Debate Moderator (FMAD Protocol)
    2. Evidence Weigher (Truth Hierarchy)
    3. Consensus Builder (Expertise Voting)

    KEY PROTOCOLS:
    -------------
    - resolve_conflict(): Full conflict resolution pipeline
    - check_for_conflict(): Detect if results conflict
    - get_ruling(): Get ruling for a case

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Step 1
    """

    def __init__(self, blackboard=None, acc=None, df=None):
        """
        Initialize the Conflict Resolution Team

        Args:
            blackboard: Phase 0 Blackboard for coordination
            acc: Agent Communication Channel
            df: Directory Facilitator
        """
        print("  [CONFLICT RESOLUTION TEAM - The Supreme Court]")

        self.blackboard = blackboard
        self.acc = acc
        self.df = df

        # Initialize agents
        self.debate_moderator = DebateModerator(blackboard, acc, df)
        self.evidence_weigher = EvidenceWeigher(blackboard)
        self.consensus_builder = ConsensusBuilder(blackboard, df)

        # Statistics
        self.conflicts_resolved = 0

        print("    [OK] Conflict Resolution Team assembled")

    def check_for_conflict(self, results: List[Dict]) -> bool:
        """
        Check if a list of results contains conflicts

        Args:
            results: List of result dictionaries from different agents

        Returns:
            True if conflicting results detected
        """
        if len(results) < 2:
            return False

        # Compare results
        first_result = results[0].get('result')
        for result in results[1:]:
            if result.get('result') != first_result:
                return True

        return False

    def resolve_conflict(self, conflict_data: Dict,
                        timeout: float = 30.0) -> Optional[Ruling]:
        """
        Full conflict resolution pipeline

        This is the main entry point for resolving conflicts.

        Args:
            conflict_data: Dictionary containing:
                - subtask_id: ID of the subtask
                - results: List of conflicting results
                - conversation_id: Optional conversation ID
                - domain: Mathematical domain
            timeout: Maximum time to wait for resolution

        Returns:
            Ruling object if resolved, None if timeout
        """
        # Step 1: Debate Moderator detects and collects arguments
        case_id = self.debate_moderator.on_conflict_detected(conflict_data)
        case = self.debate_moderator.get_case(case_id)

        if not case or case.status != ConflictStatus.ARGUMENTS_RECEIVED:
            # Arguments not auto-collected, need to wait
            import time
            start = time.time()
            while time.time() - start < timeout:
                case = self.debate_moderator.get_case(case_id)
                if case and case.status in [
                    ConflictStatus.WEIGHING,
                    ConflictStatus.RESOLVED
                ]:
                    break
                time.sleep(0.1)

        # Step 2: Evidence Weigher evaluates
        case_data = self.debate_moderator._serialize_case(case)
        ruling = self.evidence_weigher.evaluate_case(case_data)

        # Step 3: If consensus required, use Consensus Builder
        if ruling.ruling_type == 'CONSENSUS_REQUIRED':
            case_data['case_id'] = case_id
            case_data['domain'] = conflict_data.get('domain', 'general')
            case_data['classification'] = []

            # Build classification from arguments
            for arg in case.arguments:
                evidence_type = self.evidence_weigher._classify_evidence(arg)
                case_data['classification'].append({
                    'agent_id': arg.get('agent_id', 'unknown'),
                    'result': arg.get('result'),
                    'evidence_type': evidence_type,
                    'hierarchy_score': self.evidence_weigher.TRUTH_HIERARCHY[evidence_type],
                    'confidence': arg.get('confidence', 0.5)
                })

            ruling = self.consensus_builder.build_consensus(case_data)

        # Update case
        if case:
            case.set_ruling({
                'ruling_type': ruling.ruling_type,
                'winner': ruling.winner_agent,
                'winning_result': ruling.winning_result,
                'confidence': ruling.confidence
            })

        self.conflicts_resolved += 1

        return ruling

    def get_ruling(self, case_id: str) -> Optional[Ruling]:
        """Get the ruling for a case"""
        case = self.debate_moderator.get_case(case_id)
        if case and case.ruling:
            return Ruling(
                ruling_type=case.ruling.get('ruling_type', 'UNKNOWN'),
                winner_agent=case.ruling.get('winner', 'unknown'),
                winning_result=case.ruling.get('winning_result'),
                evidence_type=case.ruling.get('evidence_type', 'UNKNOWN'),
                rationale=case.ruling.get('rationale', ''),
                confidence=case.ruling.get('confidence', 0.0)
            )
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get team statistics"""
        return {
            'conflicts_resolved': self.conflicts_resolved,
            'debate_moderator': self.debate_moderator.get_statistics(),
            'evidence_weigher': self.evidence_weigher.get_statistics(),
            'consensus_builder': self.consensus_builder.get_statistics()
        }


# ===========================================================================
# MODULE TEST
# ===========================================================================

if __name__ == "__main__":
    """Test Conflict Resolution Team"""
    print("=" * 80)
    print("PHASE 4 - STEP 1: CONFLICT RESOLUTION TEAM TEST")
    print("=" * 80)
    print()

    # Initialize team (without infrastructure for basic test)
    team = ConflictResolutionTeam()
    print()

    # Test case: Symbolic vs Numerical conflict
    print("TEST: Symbolic vs Numerical Agent Conflict")
    print("-" * 40)

    conflict_data = {
        'subtask_id': 'integrate_sin_x',
        'conversation_id': 'test_001',
        'domain': 'calculus',
        'results': [
            {
                'agent_id': 'symbolic_integration_001',
                'result': '-cos(x) + C',
                'method_used': 'symbolic_risch_algorithm',
                'evidence_type': 'SYMBOLIC_DERIVATION',
                'confidence': 0.95
            },
            {
                'agent_id': 'numerical_integration_001',
                'result': '-0.9999999cos(x)',
                'method_used': 'numerical_quadrature',
                'evidence_type': 'NUMERICAL_APPROXIMATION',
                'confidence': 0.99
            }
        ]
    }

    print(f"  Symbolic Agent: {conflict_data['results'][0]['result']}")
    print(f"  Numerical Agent: {conflict_data['results'][1]['result']}")
    print()

    ruling = team.resolve_conflict(conflict_data)

    print()
    print("RULING:")
    print(f"  Type: {ruling.ruling_type}")
    print(f"  Winner: {ruling.winner_agent}")
    print(f"  Result: {ruling.winning_result}")
    print(f"  Evidence: {ruling.evidence_type}")
    print(f"  Rationale: {ruling.rationale}")
    print()

    # Test case 2: Formal proof wins
    print("TEST: Formal Proof vs Heuristic")
    print("-" * 40)

    conflict_data_2 = {
        'subtask_id': 'prove_theorem',
        'conversation_id': 'test_002',
        'domain': 'algebra',
        'results': [
            {
                'agent_id': 'formal_prover_001',
                'result': 'QED',
                'method_used': 'ax_prover_coq',
                'ax_prover_verified': True,
                'confidence': 1.0
            },
            {
                'agent_id': 'heuristic_solver_001',
                'result': 'Likely true',
                'method_used': 'pattern_matching',
                'confidence': 0.7
            }
        ]
    }

    ruling_2 = team.resolve_conflict(conflict_data_2)

    print(f"  Winner: {ruling_2.winner_agent}")
    print(f"  Evidence: {ruling_2.evidence_type}")
    print(f"  (Formal proof automatically wins)")
    print()

    # Statistics
    print("TEAM STATISTICS:")
    import json
    print(json.dumps(team.get_statistics(), indent=2))
    print()

    print("=" * 80)
    print("CONFLICT RESOLUTION TEAM TEST COMPLETE")
    print("=" * 80)
