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
THOUGHT TRACE HARVESTER (Provenance Logger)
============================================

Step 1 of Phase 5 Build Order: The "Thought Trace" Harvest

OBJECTIVE:
---------
Convert ephemeral runtime operations of the Multi-Agent System into a
persistent, high-quality training dataset. Captures the complete causal
reasoning chains that constitute the "Gold Standard" corpus for knowledge
distillation.

KEY PRINCIPLE:
-------------
Intelligence cannot be distilled until it has been captured in a structured,
verifiable format. The Student model must learn not merely to predict answers,
but to predict the INTERNAL ROUTING LOGIC of the Orchestrator and the
ALGORITHMIC CHOICES of the Supervisors.

GOLD STANDARD FILTER:
--------------------
Only traces that receive STATUS: VERIFIED from the Ax-Prover loop (Phase 1)
or a consensus from the Debate Moderator (Phase 4) are flagged as Gold
Standard training data. This filters out the noise of failed attempts.

REFERENCE:
---------
- Phase_5_Build_Order_Breakdown.md: Section 2
- phase5_symbo_integration_architecture.py: ThoughtTraceHarvester class
"""

import os
import json
import hashlib
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

# Add parent paths for imports
# Path manipulation removed - using package imports


class VerificationStatus(Enum):
    """
    Verification status for thought traces.

    CRITICAL: Only VERIFIED traces enter the training corpus.
    This is the "Gold Standard Filter" from Phase 5 documentation.
    """
    PENDING = "pending"        # Awaiting verification
    VERIFIED = "verified"      # Passed Ax-Prover or Debate consensus
    REJECTED = "rejected"      # Failed verification
    ESCALATED = "escalated"    # Sent to full MAS for resolution


@dataclass
class ThoughtTrace:
    """
    Captures the full causal chain of a successful reasoning episode.

    This is the "Gold Standard" data unit for distillation - only traces
    with verification_status == VERIFIED enter the Student training set.

    DATA STRUCTURE (from Phase 5 Build Order):
    ------------------------------------------
    - trace_id: Unique identifier for the reasoning episode
    - original_query: User's mathematical query in natural language
    - orchestrator_decomposition: HTN subtask breakdown from the Orchestrator
    - supervisor_strategy: Which domain supervisor handled the problem and why
    - specialist_agents_invoked: List of Tier-3 specialists activated
    - symbolic_expressions: OMDoc/SymPy expressions at each reasoning step
    - fitted_coefficients: Compressed "thought trace" from perturbation methods
    - verification_status: PENDING | VERIFIED | REJECTED | ESCALATED
    - final_answer: The verified mathematical result

    REFERENCE:
    ---------
    Phase_5_Build_Order_Breakdown.md: Section 2.3.1
    """
    trace_id: str
    timestamp: datetime

    # Input specification
    original_query: str
    query_type: str  # "computation", "proof", "optimization", "symbolic"
    complexity_score: float  # 0-1 scale, used by Gatekeeper

    # Reasoning chain (the "thought trace" itself)
    orchestrator_decomposition: List[str]  # HTN subtasks
    supervisor_strategy: str  # Which domain supervisor handled it
    specialist_agents_invoked: List[str]  # e.g., ["Integration_Specialist", "SVD_Agent"]

    # Symbolic reasoning artifacts
    symbolic_expressions: List[str]  # OMDoc/SymPy expressions at each step
    fitted_coefficients: Dict[str, float]  # e.g., g_k, g_a from perturbation
    taylor_expansion_order: int
    groebner_basis_used: bool

    # Verification artifacts
    verification_status: VerificationStatus
    formal_proof_lean4: Optional[str]  # If applicable
    debate_consensus_score: Optional[float]  # If resolved via FMAD

    # Final output
    final_answer: str
    confidence_score: float

    # Resource metrics (for optimization)
    total_latency_ms: float
    agents_activated: int
    symbolic_ops_count: int

    # Metadata for evolution tracking
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_training_example(self) -> Dict[str, Any]:
        """
        Convert trace to Student model training format.

        KEY INSIGHT from Phase 5 documentation:
        We teach the Student to predict the ROUTING LOGIC and STRATEGIC CHOICES,
        not just the final answer.

        Returns:
            Dictionary with prompt, response, and metadata for training
        """
        # Build the "prompt" (what Student sees)
        prompt = f"""Query: {self.original_query}
Type: {self.query_type}
Complexity: {self.complexity_score:.2f}"""

        # Build the "response" (what Student learns to produce)
        response_parts = [
            f"Strategy: {self.supervisor_strategy}",
            f"Agents: {', '.join(self.specialist_agents_invoked)}",
        ]

        if self.fitted_coefficients:
            coeff_str = ", ".join([
                f"{k}={v:.6f}" for k, v in self.fitted_coefficients.items()
            ])
            response_parts.append(f"Coefficients: {coeff_str}")

        response_parts.append(f"Answer: {self.final_answer}")

        return {
            "prompt": prompt,
            "response": "\n".join(response_parts),
            "category": self.query_type,
            "complexity": self.complexity_score,
            "trace_id": self.trace_id,
            "confidence": self.confidence_score,
            "latency_ms": self.total_latency_ms,
            "agents_count": self.agents_activated
        }

    def compute_hash(self) -> str:
        """
        Deterministic hash for deduplication.

        Prevents duplicate traces from entering the training corpus.
        """
        content = f"{self.original_query}|{self.final_answer}|{self.supervisor_strategy}"
        return hashlib.md5(content.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert trace to dictionary for serialization"""
        return {
            'trace_id': self.trace_id,
            'timestamp': self.timestamp.isoformat(),
            'original_query': self.original_query,
            'query_type': self.query_type,
            'complexity_score': self.complexity_score,
            'orchestrator_decomposition': self.orchestrator_decomposition,
            'supervisor_strategy': self.supervisor_strategy,
            'specialist_agents_invoked': self.specialist_agents_invoked,
            'symbolic_expressions': self.symbolic_expressions,
            'fitted_coefficients': self.fitted_coefficients,
            'taylor_expansion_order': self.taylor_expansion_order,
            'groebner_basis_used': self.groebner_basis_used,
            'verification_status': self.verification_status.value,
            'formal_proof_lean4': self.formal_proof_lean4,
            'debate_consensus_score': self.debate_consensus_score,
            'final_answer': self.final_answer,
            'confidence_score': self.confidence_score,
            'total_latency_ms': self.total_latency_ms,
            'agents_activated': self.agents_activated,
            'symbolic_ops_count': self.symbolic_ops_count,
            'metadata': self.metadata
        }


class ThoughtTraceHarvester:
    """
    Harvests thought traces from the full multi-agent system (Teacher).

    Implements Phase 5 "Provenance Logger" - captures every successful
    reasoning chain for potential distillation.

    FILTERING LOGIC (Gold Standard Filter):
    ---------------------------------------
    Only traces that receive STATUS: VERIFIED from the Ax-Prover loop
    (Phase 1) or a consensus from the Debate Moderator (Phase 4) are
    flagged as Gold Standard training data.

    This filters out the noise of failed attempts, ensuring the distillation
    corpus consists purely of successful reasoning paths.

    INTEGRATION POINTS:
    ------------------
    - Phase 1: Verification Core (Ax-Prover) - provides VERIFIED status
    - Phase 4: Conflict Resolution Team - provides debate consensus
    - Phase 4: Meta-Learning Team - provides Performance Monitor data

    USAGE:
    -----
    harvester = ThoughtTraceHarvester()

    # Start recording
    trace_id = harvester.begin_trace(query="Integrate sin(x)", query_type="calculus")

    # Record reasoning steps
    harvester.record_symbolic_step(trace_id, expr, "integration", "Integration_Specialist")

    # Finalize (only VERIFIED traces enter corpus)
    harvester.finalize_trace(trace_id, answer, VerificationStatus.VERIFIED, 0.95, 150.0)

    # Get training data
    corpus = harvester.get_training_corpus()

    REFERENCE:
    ---------
    Phase_5_Build_Order_Breakdown.md: Section 2.4
    phase5_symbo_integration_architecture.py: lines 135-233
    """

    def __init__(self, storage_path: str = "./thought_traces", blackboard=None):
        """
        Initialize the Thought Trace Harvester.

        Args:
            storage_path: Path for persisting traces
            blackboard: Reference to Phase 0 Blackboard for integration
        """
        print("  [+] Initializing Thought Trace Harvester (Provenance Logger)")

        self.storage_path = storage_path
        self.blackboard = blackboard

        # Create storage directory if needed
        os.makedirs(storage_path, exist_ok=True)

        # Active traces (in-progress)
        self.pending_traces: Dict[str, ThoughtTrace] = {}

        # Completed verified traces (Gold Standard)
        self.verified_traces: List[ThoughtTrace] = []

        # Escalated traces (Student failed, Teacher succeeded)
        self.escalated_traces: List[ThoughtTrace] = []

        # Hash set for deduplication
        self.trace_hashes: set = set()

        # Statistics
        self.stats = {
            'traces_started': 0,
            'traces_verified': 0,
            'traces_rejected': 0,
            'traces_escalated': 0,
            'total_latency_ms': 0.0,
            'avg_agents_per_trace': 0.0
        }

        # Load persisted traces if available
        self._load_persisted_traces()

        print(f"      Loaded {len(self.verified_traces)} verified traces from storage")
        print("      Gold Standard Filter: ACTIVE")
        print("      [OK] Thought Trace Harvester ready")

    def begin_trace(self, query: str, query_type: str) -> str:
        """
        Start recording a new reasoning episode.

        Args:
            query: The user's mathematical query
            query_type: Type of problem ("computation", "proof", "optimization", "symbolic")

        Returns:
            trace_id: Unique identifier for this trace
        """
        trace_id = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.stats['traces_started']}"

        trace = ThoughtTrace(
            trace_id=trace_id,
            timestamp=datetime.now(),
            original_query=query,
            query_type=query_type,
            complexity_score=0.0,  # Will be computed during finalization
            orchestrator_decomposition=[],
            supervisor_strategy="",
            specialist_agents_invoked=[],
            symbolic_expressions=[],
            fitted_coefficients={},
            taylor_expansion_order=0,
            groebner_basis_used=False,
            verification_status=VerificationStatus.PENDING,
            formal_proof_lean4=None,
            debate_consensus_score=None,
            final_answer="",
            confidence_score=0.0,
            total_latency_ms=0.0,
            agents_activated=0,
            symbolic_ops_count=0
        )

        self.pending_traces[trace_id] = trace
        self.stats['traces_started'] += 1

        return trace_id

    def record_orchestrator_decomposition(self, trace_id: str, subtasks: List[str]):
        """
        Record the HTN decomposition from the Orchestrator.

        Args:
            trace_id: The trace identifier
            subtasks: List of subtask descriptions
        """
        trace = self._get_trace(trace_id)
        if trace:
            trace.orchestrator_decomposition = subtasks

    def record_supervisor_strategy(self, trace_id: str, strategy: str, supervisor_id: str):
        """
        Record which domain supervisor handled the problem.

        Args:
            trace_id: The trace identifier
            strategy: The strategy used (e.g., "symbolic_risch", "numerical_quadrature")
            supervisor_id: ID of the supervisor
        """
        trace = self._get_trace(trace_id)
        if trace:
            trace.supervisor_strategy = f"{supervisor_id}: {strategy}"

    def record_symbolic_step(
        self,
        trace_id: str,
        expression: str,
        operation: str,
        agent_name: str
    ):
        """
        Record a symbolic reasoning step.

        This captures the actual mathematical transformations performed
        by the specialist agents.

        Args:
            trace_id: The trace identifier
            expression: The symbolic expression (as string)
            operation: The operation performed (e.g., "differentiation", "factorization")
            agent_name: The agent that performed the operation
        """
        trace = self._get_trace(trace_id)
        if trace:
            trace.symbolic_expressions.append(f"{operation}: {expression}")
            if agent_name not in trace.specialist_agents_invoked:
                trace.specialist_agents_invoked.append(agent_name)
            trace.symbolic_ops_count += 1

    def record_perturbation_result(
        self,
        trace_id: str,
        fitted_coeffs: Dict[str, float],
        taylor_order: int
    ):
        """
        Record results from perturbation method.

        This captures the "compressed thought trace" from perturbation-based
        solving (e.g., g_k, g_a, g_epsilon, g_sigma coefficients).

        Args:
            trace_id: The trace identifier
            fitted_coeffs: Dictionary of fitted coefficients
            taylor_order: Order of Taylor expansion used
        """
        trace = self._get_trace(trace_id)
        if trace:
            trace.fitted_coefficients = fitted_coeffs
            trace.taylor_expansion_order = taylor_order
            trace.supervisor_strategy = "perturbation_solver"

    def record_groebner_solve(self, trace_id: str, basis_computed: bool = True):
        """
        Record that Grobner basis was used for solving.

        Args:
            trace_id: The trace identifier
            basis_computed: Whether Grobner basis was successfully computed
        """
        trace = self._get_trace(trace_id)
        if trace:
            trace.groebner_basis_used = basis_computed
            if "algebraic_geometry" not in trace.supervisor_strategy:
                trace.supervisor_strategy += " (Grobner)"

    def record_formal_proof(self, trace_id: str, lean4_proof: str):
        """
        Record a formal proof in Lean 4.

        Args:
            trace_id: The trace identifier
            lean4_proof: The Lean 4 proof code
        """
        trace = self._get_trace(trace_id)
        if trace:
            trace.formal_proof_lean4 = lean4_proof

    def record_debate_consensus(self, trace_id: str, consensus_score: float):
        """
        Record debate consensus from Phase 4 Conflict Resolution.

        Args:
            trace_id: The trace identifier
            consensus_score: The consensus score (0-1)
        """
        trace = self._get_trace(trace_id)
        if trace:
            trace.debate_consensus_score = consensus_score

    def finalize_trace(
        self,
        trace_id: str,
        final_answer: str,
        verification_status: VerificationStatus,
        confidence: float,
        latency_ms: float,
        escalated_from_student: bool = False
    ):
        """
        Finalize a trace after verification.

        GOLD STANDARD FILTER:
        Only traces with verification_status == VERIFIED enter the training corpus.
        This ensures 0% contamination from failed attempts.

        Args:
            trace_id: The trace identifier
            final_answer: The final mathematical result
            verification_status: VERIFIED, REJECTED, or ESCALATED
            confidence: Confidence score (0-1)
            latency_ms: Total latency in milliseconds
            escalated_from_student: Whether this was escalated from Student model
        """
        trace = self._get_trace(trace_id)
        if not trace:
            return

        # Update trace with final data
        trace.final_answer = final_answer
        trace.verification_status = verification_status
        trace.confidence_score = confidence
        trace.total_latency_ms = latency_ms
        trace.agents_activated = len(trace.specialist_agents_invoked)

        # Compute complexity score based on trace characteristics
        trace.complexity_score = self._compute_complexity(trace)

        # Mark if escalated from Student
        if escalated_from_student:
            trace.metadata['escalated_from_student'] = True
            trace.metadata['learning_priority'] = 'high'

        # GOLD STANDARD FILTER: Only VERIFIED traces enter corpus
        if verification_status == VerificationStatus.VERIFIED:
            trace_hash = trace.compute_hash()
            if trace_hash not in self.trace_hashes:
                self.verified_traces.append(trace)
                self.trace_hashes.add(trace_hash)
                self.stats['traces_verified'] += 1

                # Also track escalated traces separately for priority learning
                if escalated_from_student:
                    self.escalated_traces.append(trace)
                    self.stats['traces_escalated'] += 1

                # Persist immediately
                self._persist_trace(trace)

        elif verification_status == VerificationStatus.REJECTED:
            self.stats['traces_rejected'] += 1

        # Update latency stats
        self.stats['total_latency_ms'] += latency_ms

        # Remove from pending
        if trace_id in self.pending_traces:
            del self.pending_traces[trace_id]

    def _get_trace(self, trace_id: str) -> Optional[ThoughtTrace]:
        """Retrieve trace by ID from pending traces"""
        return self.pending_traces.get(trace_id)

    def _compute_complexity(self, trace: ThoughtTrace) -> float:
        """
        Compute complexity score for Gatekeeper routing decisions.

        Higher score = more likely to require full MAS (Teacher).

        Factors:
        1. Number of agents involved
        2. Symbolic operations count
        3. Taylor expansion order
        4. Grobner basis usage
        5. Query type complexity
        """
        score = 0.0

        # Factor 1: Number of agents involved
        score += min(len(trace.specialist_agents_invoked) * 0.1, 0.3)

        # Factor 2: Symbolic operations count
        score += min(trace.symbolic_ops_count * 0.02, 0.2)

        # Factor 3: Taylor expansion order
        score += trace.taylor_expansion_order * 0.05

        # Factor 4: Grobner basis usage (indicates polynomial system)
        if trace.groebner_basis_used:
            score += 0.2

        # Factor 5: Query type complexity
        type_weights = {
            "computation": 0.1,
            "symbolic": 0.2,
            "optimization": 0.25,
            "proof": 0.35
        }
        score += type_weights.get(trace.query_type, 0.15)

        return min(score, 1.0)

    def get_training_corpus(self) -> List[Dict[str, Any]]:
        """
        Extract verified traces as training examples for Student model.

        This is the Phase 5 "Gold Standard" corpus - only verified traces
        with successful outcomes enter the distillation pipeline.

        Returns:
            List of training examples with prompt/response pairs
        """
        return [trace.to_training_example() for trace in self.verified_traces]

    def get_escalated_traces(self) -> List[Dict[str, Any]]:
        """
        Get traces that were escalated from Student and resolved by Teacher.

        These are the Phase 5 "High-Priority Training Data" - cases where
        the Student failed but the Teacher succeeded. These receive priority
        weighting in the distillation pipeline.

        Returns:
            List of high-priority training examples
        """
        return [trace.to_training_example() for trace in self.escalated_traces]

    def _persist_trace(self, trace: ThoughtTrace):
        """Persist a verified trace to storage"""
        filepath = os.path.join(
            self.storage_path,
            f"{trace.trace_id}.json"
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(trace.to_dict(), f, indent=2)

    def _load_persisted_traces(self):
        """Load previously persisted traces from storage"""
        if not os.path.exists(self.storage_path):
            return

        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.storage_path, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Reconstruct trace
                    trace = ThoughtTrace(
                        trace_id=data['trace_id'],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        original_query=data['original_query'],
                        query_type=data['query_type'],
                        complexity_score=data['complexity_score'],
                        orchestrator_decomposition=data['orchestrator_decomposition'],
                        supervisor_strategy=data['supervisor_strategy'],
                        specialist_agents_invoked=data['specialist_agents_invoked'],
                        symbolic_expressions=data['symbolic_expressions'],
                        fitted_coefficients=data['fitted_coefficients'],
                        taylor_expansion_order=data['taylor_expansion_order'],
                        groebner_basis_used=data['groebner_basis_used'],
                        verification_status=VerificationStatus(data['verification_status']),
                        formal_proof_lean4=data.get('formal_proof_lean4'),
                        debate_consensus_score=data.get('debate_consensus_score'),
                        final_answer=data['final_answer'],
                        confidence_score=data['confidence_score'],
                        total_latency_ms=data['total_latency_ms'],
                        agents_activated=data['agents_activated'],
                        symbolic_ops_count=data['symbolic_ops_count'],
                        metadata=data.get('metadata', {})
                    )

                    # Add to verified traces
                    trace_hash = trace.compute_hash()
                    if trace_hash not in self.trace_hashes:
                        self.verified_traces.append(trace)
                        self.trace_hashes.add(trace_hash)

                        if trace.metadata.get('escalated_from_student'):
                            self.escalated_traces.append(trace)

                except Exception as e:
                    print(f"      Warning: Failed to load trace {filename}: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get harvester statistics"""
        total_traces = self.stats['traces_verified'] + self.stats['traces_rejected']

        return {
            'traces_started': self.stats['traces_started'],
            'traces_verified': self.stats['traces_verified'],
            'traces_rejected': self.stats['traces_rejected'],
            'traces_escalated': self.stats['traces_escalated'],
            'verification_rate': (
                self.stats['traces_verified'] / max(total_traces, 1)
            ) * 100,
            'corpus_size': len(self.verified_traces),
            'escalated_count': len(self.escalated_traces),
            'avg_latency_ms': (
                self.stats['total_latency_ms'] / max(self.stats['traces_verified'], 1)
            ),
            'pending_traces': len(self.pending_traces)
        }

    def add_trace(self, trace: ThoughtTrace) -> bool:
        """
        Add a pre-constructed trace directly to the corpus.

        This is a convenience method for cases where a trace is constructed
        externally (e.g., in MathSolver) and needs to be added without going
        through the begin_trace/finalize_trace workflow.

        Args:
            trace: A fully constructed ThoughtTrace object

        Returns:
            True if trace was added, False if duplicate
        """
        # Only add verified traces
        if trace.verification_status != VerificationStatus.VERIFIED:
            return False

        # Deduplication check
        trace_hash = trace.compute_hash()
        if trace_hash in self.trace_hashes:
            return False

        # Add to corpus
        self.verified_traces.append(trace)
        self.trace_hashes.add(trace_hash)
        self.stats['traces_verified'] += 1

        # Track escalated traces separately
        if trace.metadata.get('escalated_from_student'):
            self.escalated_traces.append(trace)
            self.stats['traces_escalated'] += 1

        # Persist immediately
        self._persist_trace(trace)

        return True

    def clear_corpus(self):
        """Clear all traces (for testing)"""
        self.verified_traces = []
        self.escalated_traces = []
        self.trace_hashes = set()
        self.pending_traces = {}
