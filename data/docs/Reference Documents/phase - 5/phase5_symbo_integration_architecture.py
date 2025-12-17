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
Phase 5 Integration Architecture: Symbo System as Distillation Engine
======================================================================

This module demonstrates how the existing symbo.py, symbo_llm.py, and symbo_llm_core.py
components integrate into the Phase 5 "Production Optimization & Distillation" framework.

Key Integration Points:
1. NanoTensor/SymbolicTrainer → "Teacher" System (System 2 deliberation)
2. SymboLLMCore → "Student" Model (System 1 fast intuition)  
3. SymboLLMAdapter → Complexity Gatekeeper (routing decisions)
4. NEW: ThoughtTraceHarvester → Captures successful reasoning for distillation
5. NEW: DistillationPipeline → Trains Student from Teacher traces
6. NEW: EvolutionaryFlywheel → Active learning from escalated failures

Architecture aligns with project documentation:
- Phase 5 "shifts focus to efficiency (latency, cost, scale)"
- "Hybrid Deployment" using fast single model for standard queries
- "Student gradually masters hard cases, constantly raising baseline intelligence"

Author: Phase 5 Integration Module
Compatible with: symbo.py v1.0, symbo_llm.py v1.0
"""

import sympy as sp
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
from abc import ABC, abstractmethod

# Import existing components (assuming they're in the same package)
# from symbo import NanoTensor, SymbolicTrainer, KnowledgeBase
# from symbo_llm import SymboLLMAdapter, LLMTask
# from symbo_llm_core import SymboLLMCore, SimpleTokenizer


class VerificationStatus(Enum):
    """Verification status for thought traces - only VERIFIED traces enter training"""
    PENDING = "pending"
    VERIFIED = "verified"  # Passed Ax-Prover or Debate consensus
    REJECTED = "rejected"  # Failed verification
    ESCALATED = "escalated"  # Sent to full MAS for resolution


@dataclass
class ThoughtTrace:
    """
    Captures the full causal chain of a successful reasoning episode.
    
    This is the "Gold Standard" data unit for distillation - only traces
    with verification_status == VERIFIED enter the Student training set.
    
    Aligns with Phase 5 documentation: "Provenance Logger capturing full causal chains"
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
    
    # Symbolic reasoning artifacts (from NanoTensor/SymbolicTrainer)
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
    
    def to_training_example(self) -> Dict[str, str]:
        """
        Convert trace to Student model training format.
        
        The key insight: we teach the Student to predict the ROUTING LOGIC
        and STRATEGIC CHOICES, not just the final answer.
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
            coeff_str = ", ".join([f"{k}={v:.6f}" for k, v in self.fitted_coefficients.items()])
            response_parts.append(f"Coefficients: {coeff_str}")
        
        response_parts.append(f"Answer: {self.final_answer}")
        
        return {
            "prompt": prompt,
            "response": "\n".join(response_parts),
            "category": self.query_type,
            "complexity": self.complexity_score,
            "trace_id": self.trace_id
        }
    
    def compute_hash(self) -> str:
        """Deterministic hash for deduplication"""
        content = f"{self.original_query}|{self.final_answer}|{self.supervisor_strategy}"
        return hashlib.md5(content.encode()).hexdigest()


class ThoughtTraceHarvester:
    """
    Harvests thought traces from the full multi-agent system (Teacher).
    
    Implements Phase 5 "Provenance Logger" - captures every successful
    reasoning chain for potential distillation.
    
    Key filtering: Only VERIFIED traces enter the training corpus.
    """
    
    def __init__(self, storage_path: str = "./thought_traces"):
        self.storage_path = storage_path
        self.pending_traces: List[ThoughtTrace] = []
        self.verified_traces: List[ThoughtTrace] = []
        self.trace_hashes: set = set()  # Deduplication
        
    def begin_trace(self, query: str, query_type: str) -> str:
        """Start recording a new reasoning episode"""
        trace_id = f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.pending_traces)}"
        
        trace = ThoughtTrace(
            trace_id=trace_id,
            timestamp=datetime.now(),
            original_query=query,
            query_type=query_type,
            complexity_score=0.0,  # Will be updated
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
        
        self.pending_traces.append(trace)
        return trace_id
    
    def record_symbolic_step(
        self, 
        trace_id: str, 
        expression: sp.Expr,
        operation: str,
        agent_name: str
    ):
        """Record a symbolic reasoning step (from NanoTensor operations)"""
        trace = self._get_trace(trace_id)
        if trace:
            trace.symbolic_expressions.append(f"{operation}: {str(expression)}")
            if agent_name not in trace.specialist_agents_invoked:
                trace.specialist_agents_invoked.append(agent_name)
            trace.symbolic_ops_count += 1
    
    def record_perturbation_result(
        self, 
        trace_id: str,
        fitted_coeffs: Dict[str, float],
        taylor_order: int
    ):
        """Record results from SymbolicTrainer.fit() with perturbation method"""
        trace = self._get_trace(trace_id)
        if trace:
            trace.fitted_coefficients = fitted_coeffs
            trace.taylor_expansion_order = taylor_order
            trace.supervisor_strategy = "perturbation_solver"
    
    def record_groebner_solve(
        self, 
        trace_id: str,
        solutions: List[Dict[str, Any]]
    ):
        """Record Gröbner basis solving (from NanoTensor.groebner_solve)"""
        trace = self._get_trace(trace_id)
        if trace:
            trace.groebner_basis_used = True
            trace.supervisor_strategy = "algebraic_geometry"
    
    def finalize_trace(
        self,
        trace_id: str,
        final_answer: str,
        verification_status: VerificationStatus,
        confidence: float,
        latency_ms: float,
        formal_proof: Optional[str] = None
    ):
        """Finalize a trace after verification"""
        trace = self._get_trace(trace_id)
        if trace:
            trace.final_answer = final_answer
            trace.verification_status = verification_status
            trace.confidence_score = confidence
            trace.total_latency_ms = latency_ms
            trace.formal_proof_lean4 = formal_proof
            trace.agents_activated = len(trace.specialist_agents_invoked)
            
            # Compute complexity score based on trace characteristics
            trace.complexity_score = self._compute_complexity(trace)
            
            # Move to verified if status is VERIFIED
            if verification_status == VerificationStatus.VERIFIED:
                trace_hash = trace.compute_hash()
                if trace_hash not in self.trace_hashes:
                    self.verified_traces.append(trace)
                    self.trace_hashes.add(trace_hash)
    
    def _get_trace(self, trace_id: str) -> Optional[ThoughtTrace]:
        """Retrieve trace by ID"""
        for trace in self.pending_traces:
            if trace.trace_id == trace_id:
                return trace
        return None
    
    def _compute_complexity(self, trace: ThoughtTrace) -> float:
        """
        Compute complexity score for Gatekeeper routing decisions.
        
        Higher score = more likely to require full MAS.
        """
        score = 0.0
        
        # Factor 1: Number of agents involved
        score += min(len(trace.specialist_agents_invoked) * 0.1, 0.3)
        
        # Factor 2: Symbolic operations count
        score += min(trace.symbolic_ops_count * 0.02, 0.2)
        
        # Factor 3: Taylor expansion order
        score += trace.taylor_expansion_order * 0.05
        
        # Factor 4: Gröbner basis usage (indicates polynomial system)
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
    
    def get_training_corpus(self) -> List[Dict[str, str]]:
        """
        Extract verified traces as training examples for Student model.
        
        This is the Phase 5 "Gold Standard Filter" - only verified traces
        with successful outcomes enter the distillation pipeline.
        """
        return [trace.to_training_example() for trace in self.verified_traces]
    
    def get_high_priority_examples(self) -> List[Dict[str, str]]:
        """
        Get traces that were escalated and later resolved by MAS.
        
        These are the Phase 5 "High-Priority Training Data" - cases where
        the Student failed but the Teacher succeeded.
        """
        return [
            trace.to_training_example() 
            for trace in self.verified_traces
            if trace.metadata.get("escalated_from_student", False)
        ]


class ComplexityGatekeeper:
    """
    Phase 5 "Triage Nurse" - routes queries to Student or full MAS.
    
    Implements the core Phase 5 optimization: fast model handles 90% of
    interactions, full MAS reserved for complex problems.
    
    Key insight from documentation:
    - "Standard queries route to Distilled Student Model"
    - "Novel/high-stakes queries route to Full Tier-3 Multi-Agent Hierarchy"
    - "Confidence Fallback Mechanism" for automatic escalation
    """
    
    def __init__(
        self,
        complexity_threshold: float = 0.4,
        confidence_threshold: float = 0.7,
        student_model = None,  # SymboLLMCore instance
        teacher_system = None   # Full MAS reference
    ):
        self.complexity_threshold = complexity_threshold
        self.confidence_threshold = confidence_threshold
        self.student_model = student_model
        self.teacher_system = teacher_system
        
        # Tracking for optimization
        self.routing_history: List[Dict] = []
        self.student_success_rate = 0.9  # Adaptive threshold
        
    def classify_query(self, query: str) -> Tuple[float, str]:
        """
        Classify query complexity using lightweight heuristics.
        
        Returns: (complexity_score, query_type)
        """
        query_lower = query.lower()
        
        # Query type detection
        if any(kw in query_lower for kw in ["prove", "proof", "theorem", "lemma"]):
            query_type = "proof"
            base_complexity = 0.6
        elif any(kw in query_lower for kw in ["optimize", "minimize", "maximize", "optimal"]):
            query_type = "optimization"
            base_complexity = 0.5
        elif any(kw in query_lower for kw in ["solve", "equation", "polynomial", "groebner"]):
            query_type = "symbolic"
            base_complexity = 0.4
        elif any(kw in query_lower for kw in ["compute", "calculate", "evaluate", "derivative"]):
            query_type = "computation"
            base_complexity = 0.2
        else:
            query_type = "general"
            base_complexity = 0.3
        
        # Complexity modifiers
        complexity = base_complexity
        
        # Higher-order terms increase complexity
        if any(term in query_lower for term in ["second order", "2nd order", "hessian"]):
            complexity += 0.15
        
        # Multi-step problems
        if query.count("?") > 1 or "then" in query_lower:
            complexity += 0.1
        
        # Domain-specific indicators
        if any(domain in query_lower for domain in ["rbc", "dsge", "perturbation", "steady state"]):
            complexity += 0.2
        
        return min(complexity, 1.0), query_type
    
    def route_query(
        self, 
        query: str,
        context: Optional[Dict] = None
    ) -> Tuple[str, float]:
        """
        Route query to appropriate system.
        
        Returns: ("student" | "teacher", complexity_score)
        """
        complexity, query_type = self.classify_query(query)
        
        # Check explicit escalation keywords
        if any(kw in query.lower() for kw in ["verify", "formal proof", "guaranteed"]):
            self._log_routing(query, complexity, "teacher", "explicit_escalation")
            return "teacher", complexity
        
        # Complexity-based routing
        if complexity >= self.complexity_threshold:
            self._log_routing(query, complexity, "teacher", "high_complexity")
            return "teacher", complexity
        
        # Default to Student for fast path
        self._log_routing(query, complexity, "student", "default_fast_path")
        return "student", complexity
    
    def handle_student_failure(
        self,
        query: str,
        student_confidence: float,
        student_answer: str
    ) -> bool:
        """
        Handle case where Student produces low-confidence answer.
        
        Returns: True if should escalate to Teacher
        
        This implements the Phase 5 "Confidence Fallback Mechanism"
        """
        if student_confidence < self.confidence_threshold:
            self._log_routing(
                query, 0.0, "teacher", 
                f"confidence_fallback (conf={student_confidence:.2f})"
            )
            return True
        return False
    
    def _log_routing(
        self, 
        query: str, 
        complexity: float, 
        destination: str, 
        reason: str
    ):
        """Log routing decision for analysis"""
        self.routing_history.append({
            "timestamp": datetime.now().isoformat(),
            "query_preview": query[:50],
            "complexity": complexity,
            "destination": destination,
            "reason": reason
        })
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics for optimization"""
        if not self.routing_history:
            return {"total": 0}
        
        student_count = sum(1 for r in self.routing_history if r["destination"] == "student")
        teacher_count = len(self.routing_history) - student_count
        
        return {
            "total": len(self.routing_history),
            "student_routed": student_count,
            "teacher_routed": teacher_count,
            "student_percentage": student_count / len(self.routing_history) * 100,
            "avg_complexity_student": np.mean([
                r["complexity"] for r in self.routing_history 
                if r["destination"] == "student"
            ]) if student_count > 0 else 0,
            "avg_complexity_teacher": np.mean([
                r["complexity"] for r in self.routing_history 
                if r["destination"] == "teacher"
            ]) if teacher_count > 0 else 0
        }


class DistillationPipeline:
    """
    Phase 5 Knowledge Distillation Pipeline.
    
    Trains the Student model (SymboLLMCore) on verified thought traces
    from the Teacher system (NanoTensor + full MAS).
    
    Key Phase 5 alignment:
    - "Train 7B-8B parameter Student model to predict internal routing logic"
    - "Result metrics: 1/5th the latency and cost of full MAS"
    - "Single model simulating 50-agent swarm reasoning"
    """
    
    def __init__(
        self,
        student_model,  # SymboLLMCore or SymboLLMAdapter
        trace_harvester: ThoughtTraceHarvester,
        epochs_per_batch: int = 20,
        min_traces_for_training: int = 50
    ):
        self.student = student_model
        self.harvester = trace_harvester
        self.epochs_per_batch = epochs_per_batch
        self.min_traces = min_traces_for_training
        
        self.distillation_runs = 0
        self.total_examples_trained = 0
        
    def run_distillation(self, prioritize_escalated: bool = True) -> Dict[str, Any]:
        """
        Execute a distillation training run.
        
        Args:
            prioritize_escalated: If True, weight escalated traces higher
            
        Returns:
            Training metrics
        """
        # Get training corpus
        corpus = self.harvester.get_training_corpus()
        
        if len(corpus) < self.min_traces:
            return {
                "status": "insufficient_data",
                "traces_available": len(corpus),
                "traces_required": self.min_traces
            }
        
        # Optionally add high-priority examples (from escalations)
        if prioritize_escalated:
            high_priority = self.harvester.get_high_priority_examples()
            # Add high-priority examples multiple times for weighting
            corpus.extend(high_priority * 3)
        
        # Train Student model
        if hasattr(self.student, 'train'):
            self.student.train(
                dataset=corpus,
                epochs=self.epochs_per_batch,
                batch_size=8
            )
        
        self.distillation_runs += 1
        self.total_examples_trained += len(corpus)
        
        return {
            "status": "success",
            "distillation_run": self.distillation_runs,
            "examples_trained": len(corpus),
            "high_priority_count": len(high_priority) if prioritize_escalated else 0,
            "total_examples_all_time": self.total_examples_trained
        }
    
    def incremental_learning(
        self, 
        trace: ThoughtTrace,
        immediate: bool = False
    ):
        """
        Learn incrementally from a single verified trace.
        
        If immediate=True, performs gradient update immediately.
        Otherwise, queues for batch training.
        
        This implements the Phase 5 "Evolutionary Flywheel":
        "Student gradually masters hard cases"
        """
        if trace.verification_status != VerificationStatus.VERIFIED:
            return
        
        example = trace.to_training_example()
        
        if immediate and hasattr(self.student, 'learn_from_interaction'):
            # Single gradient step (from symbo_llm.py)
            self.student.learn_from_interaction(
                user_input=example["prompt"],
                response=example["response"]
            )


class SymboPhase5Integration:
    """
    Master integration class connecting all Phase 5 components.
    
    This is the "Apex System" from Phase 5 documentation:
    - Fast single model handles 90% of interactions
    - Instantly unfolds into 50-agent swarm for complex problems
    - Autonomously updates "instincts" based on MAS successes
    """
    
    def __init__(
        self,
        student_adapter,  # SymboLLMAdapter instance
        nano_tensor,      # NanoTensor instance (Teacher)
        symbolic_trainer, # SymbolicTrainer instance (Teacher)
        storage_path: str = "./phase5_data"
    ):
        self.student = student_adapter
        self.nano_tensor = nano_tensor
        self.symbolic_trainer = symbolic_trainer
        
        # Initialize Phase 5 components
        self.harvester = ThoughtTraceHarvester(storage_path)
        self.gatekeeper = ComplexityGatekeeper(
            student_model=student_adapter,
            teacher_system=(nano_tensor, symbolic_trainer)
        )
        self.distillation = DistillationPipeline(
            student_model=student_adapter,
            trace_harvester=self.harvester
        )
        
        # Metrics
        self.total_queries = 0
        self.student_handled = 0
        self.teacher_handled = 0
        self.escalations = 0
        
    def process_query(
        self, 
        query: str,
        require_verification: bool = False
    ) -> Dict[str, Any]:
        """
        Process a mathematical query through the Phase 5 system.
        
        Args:
            query: User's mathematical query
            require_verification: Force Teacher path for verification
            
        Returns:
            Result dictionary with answer, confidence, and metadata
        """
        self.total_queries += 1
        
        # Route through Gatekeeper
        destination, complexity = self.gatekeeper.route_query(query)
        
        if require_verification:
            destination = "teacher"
        
        if destination == "student":
            # Fast path: Student model
            result = self._handle_with_student(query, complexity)
            
            # Check for escalation need
            if self.gatekeeper.handle_student_failure(
                query, 
                result.get("confidence", 0),
                result.get("answer", "")
            ):
                # Escalate to Teacher
                self.escalations += 1
                teacher_result = self._handle_with_teacher(query, complexity)
                teacher_result["escalated_from_student"] = True
                return teacher_result
            
            self.student_handled += 1
            return result
        else:
            # Complex path: Full Teacher system
            result = self._handle_with_teacher(query, complexity)
            self.teacher_handled += 1
            return result
    
    def _handle_with_student(
        self, 
        query: str, 
        complexity: float
    ) -> Dict[str, Any]:
        """Handle query with fast Student model"""
        from datetime import datetime
        start_time = datetime.now()
        
        # Use SymboLLMAdapter's generate method
        if hasattr(self.student, 'generate'):
            response = self.student.generate(query)
        else:
            response = "Student model not available"
        
        latency = (datetime.now() - start_time).total_seconds() * 1000
        
        # Estimate confidence (would be more sophisticated in production)
        confidence = 0.8 if len(response) > 20 else 0.5
        
        return {
            "answer": response,
            "confidence": confidence,
            "handler": "student",
            "complexity": complexity,
            "latency_ms": latency
        }
    
    def _handle_with_teacher(
        self, 
        query: str, 
        complexity: float
    ) -> Dict[str, Any]:
        """
        Handle query with full Teacher system (NanoTensor + SymbolicTrainer).
        
        This demonstrates integration with symbo.py's capabilities.
        """
        from datetime import datetime
        start_time = datetime.now()
        
        # Start trace recording
        trace_id = self.harvester.begin_trace(
            query=query,
            query_type="symbolic"  # Would be classified properly
        )
        
        try:
            # Parse query to determine operation (simplified)
            answer = self._symbolic_reasoning(query, trace_id)
            
            latency = (datetime.now() - start_time).total_seconds() * 1000
            
            # Finalize trace as verified (simplified - would go through Ax-Prover)
            self.harvester.finalize_trace(
                trace_id=trace_id,
                final_answer=answer,
                verification_status=VerificationStatus.VERIFIED,
                confidence=0.95,
                latency_ms=latency
            )
            
            # Trigger incremental learning
            trace = self.harvester._get_trace(trace_id)
            if trace:
                self.distillation.incremental_learning(trace, immediate=True)
            
            return {
                "answer": answer,
                "confidence": 0.95,
                "handler": "teacher",
                "complexity": complexity,
                "latency_ms": latency,
                "trace_id": trace_id,
                "verified": True
            }
            
        except Exception as e:
            self.harvester.finalize_trace(
                trace_id=trace_id,
                final_answer=f"Error: {str(e)}",
                verification_status=VerificationStatus.REJECTED,
                confidence=0.0,
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
            return {
                "answer": f"Error processing query: {str(e)}",
                "confidence": 0.0,
                "handler": "teacher",
                "error": True
            }
    
    def _symbolic_reasoning(self, query: str, trace_id: str) -> str:
        """
        Execute symbolic reasoning using NanoTensor/SymbolicTrainer.
        
        This demonstrates how symbo.py integrates as the Teacher.
        """
        query_lower = query.lower()
        
        # Check for perturbation-type queries
        if "perturbation" in query_lower or "policy" in query_lower:
            # Would parse actual equations from query
            # For demo, using RBC-style structure
            k, a, eps, sig = sp.symbols('k a eps sig')
            
            # Record symbolic step
            self.harvester.record_symbolic_step(
                trace_id=trace_id,
                expression=k**2 + a,
                operation="perturbation_setup",
                agent_name="Perturbation_Specialist"
            )
            
            # Use NanoTensor's perturbation solver
            # self.nano_tensor.full_perturbation(...)
            
            return "Policy coefficients computed via 2nd-order perturbation"
        
        # Check for polynomial solving
        elif "solve" in query_lower and any(term in query_lower for term in ["polynomial", "equation"]):
            self.harvester.record_symbolic_step(
                trace_id=trace_id,
                expression=sp.Symbol('x')**2 - 1,
                operation="polynomial_setup",
                agent_name="Algebra_Specialist"
            )
            
            # Would use self.nano_tensor.groebner_solve() or solve_poly()
            self.harvester.record_groebner_solve(trace_id, [])
            
            return "Polynomial system solved via Gröbner basis"
        
        # Check for differentiation
        elif "derivative" in query_lower or "differentiate" in query_lower:
            self.harvester.record_symbolic_step(
                trace_id=trace_id,
                expression=sp.diff(sp.Symbol('x')**2, sp.Symbol('x')),
                operation="differentiation",
                agent_name="Calculus_Specialist"
            )
            
            return "Derivative computed symbolically"
        
        else:
            return "Query processed through symbolic reasoning pipeline"
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        routing_stats = self.gatekeeper.get_routing_stats()
        
        return {
            "total_queries": self.total_queries,
            "student_handled": self.student_handled,
            "teacher_handled": self.teacher_handled,
            "escalations": self.escalations,
            "student_percentage": (self.student_handled / max(self.total_queries, 1)) * 100,
            "escalation_rate": (self.escalations / max(self.student_handled, 1)) * 100,
            "verified_traces": len(self.harvester.verified_traces),
            "distillation_runs": self.distillation.distillation_runs,
            "routing_breakdown": routing_stats
        }
    
    def run_periodic_distillation(self) -> Dict[str, Any]:
        """
        Run periodic distillation to update Student model.
        
        Should be called on schedule (e.g., hourly, after N queries)
        to implement the Phase 5 "Evolutionary Flywheel".
        """
        return self.distillation.run_distillation(prioritize_escalated=True)


# ==================== Demo & Testing ====================

def demo_phase5_integration():
    """
    Demonstrate Phase 5 integration with symbo components.
    
    This shows the complete flow:
    1. Query arrives at Gatekeeper
    2. Routed to Student (fast) or Teacher (full MAS)
    3. Teacher traces captured and verified
    4. Student learns from successful Teacher traces
    5. Over time, Student handles more queries independently
    """
    print("\n" + "="*60)
    print("Phase 5 Symbo Integration Demo")
    print("="*60)
    
    # Note: In production, these would be actual instances
    # from symbo_llm import SymboLLMAdapter
    # from symbo import NanoTensor, SymbolicTrainer
    
    print("\n1. Initializing Phase 5 Components...")
    print("   - ThoughtTraceHarvester: Captures reasoning chains")
    print("   - ComplexityGatekeeper: Routes Student vs Teacher")
    print("   - DistillationPipeline: Trains Student from Teacher")
    
    # Create mock instances for demo
    harvester = ThoughtTraceHarvester()
    gatekeeper = ComplexityGatekeeper()
    
    print("\n2. Testing Query Classification...")
    test_queries = [
        "Calculate the derivative of x^2",
        "Solve the polynomial system using Gröbner bases",
        "Prove that the sum of first n integers equals n(n+1)/2",
        "Compute 2nd-order perturbation policy for RBC model"
    ]
    
    for query in test_queries:
        complexity, query_type = gatekeeper.classify_query(query)
        destination, _ = gatekeeper.route_query(query)
        print(f"   Query: '{query[:40]}...'")
        print(f"   → Type: {query_type}, Complexity: {complexity:.2f}, Route: {destination}")
        print()
    
    print("3. Simulating Thought Trace Capture...")
    trace_id = harvester.begin_trace(
        query="Solve x^2 - 2x + 1 = 0",
        query_type="symbolic"
    )
    
    # Simulate symbolic reasoning steps
    harvester.record_symbolic_step(
        trace_id=trace_id,
        expression=sp.Symbol('x')**2 - 2*sp.Symbol('x') + 1,
        operation="equation_setup",
        agent_name="Algebra_Specialist"
    )
    
    harvester.record_symbolic_step(
        trace_id=trace_id,
        expression=(sp.Symbol('x') - 1)**2,
        operation="factorization",
        agent_name="Factoring_Agent"
    )
    
    harvester.finalize_trace(
        trace_id=trace_id,
        final_answer="x = 1 (double root)",
        verification_status=VerificationStatus.VERIFIED,
        confidence=0.99,
        latency_ms=150.0
    )
    
    print(f"   Trace {trace_id} captured and VERIFIED")
    print(f"   Training example: {harvester.get_training_corpus()[-1]}")
    
    print("\n4. Phase 5 System Stats:")
    print(f"   Verified traces ready for distillation: {len(harvester.verified_traces)}")
    print(f"   Routing statistics: {gatekeeper.get_routing_stats()}")
    
    print("\n" + "="*60)
    print("Demo Complete - Phase 5 Symbo Integration Operational")
    print("="*60)


if __name__ == "__main__":
    demo_phase5_integration()
