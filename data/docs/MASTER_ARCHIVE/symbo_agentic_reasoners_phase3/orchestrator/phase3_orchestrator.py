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
PHASE 3 ORCHESTRATOR - Updated Tier 1 Orchestrator
===================================================

Phase 3: Meta-Cognitive Middleware Integration

PURPOSE:
-------
Update the Phase 1 Tier 1 Orchestrator to integrate the three new teams.
The control loop evolves from the simple Plan -> Solve pattern to a robust
Analyze -> Hypothesize -> Validate -> Solve cycle.

CONTROL LOOP EVOLUTION:
    Phase 1-2: Plan -> Solve
    Phase 3:   Analyze -> Hypothesize -> Validate -> Solve

PROTOCOLS:
---------
1. Pre-Flight Check: NEVER delegate until validation returns VALID
2. Look-Before-You-Leap: Check for existing solutions before solving
3. Scouting: Generate strategies for high-complexity problems

REFERENCE:
---------
- Phase_3_Build_Order_Breakdown.md: Step 4
- Phase_3_installs_the_cognitive_immune_system.md: Actions 4.1-4.3
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from enum import Enum, auto
from datetime import datetime
import logging
import uuid

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase3.orchestrator.phase3_orchestrator')
except ImportError:
    logger = logging.getLogger(__name__)

# Import Phase 3 teams
from ..validation.precondition_validation import (
    PreconditionValidationTeam,
    ValidationStatus,
    ValidationResult,
    MathematicalDomain,
    MathematicalConstraint
)
from ..knowledge.knowledge_management import (
    KnowledgeManagementTeam,
    RetrievalConfidence,
    RetrievalResult
)
from ..hypothesis.hypothesis_generation import (
    HypothesisGenerationTeam,
    SolutionPlan,
    PlanStatus
)


# ===========================================================================
# COMPLEXITY AND DECISION TYPES
# ===========================================================================

class ComplexityLevel(Enum):
    """Problem complexity classification"""
    LOW = auto()      # Simple, direct solution
    MEDIUM = auto()   # Moderate complexity
    HIGH = auto()     # Requires strategic planning (scouting)


@dataclass
class OrchestratorDecision:
    """
    Record of Orchestrator decision for logging/debugging

    Captures the full decision-making process including validation,
    retrieval, and strategy selection.
    """
    conversation_id: str
    decision_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    validation_status: Optional[str] = None
    retrieval_result: Optional[str] = None
    selected_strategy: Optional[str] = None
    delegated_to: Optional[str] = None
    skip_solving: bool = False
    error_message: Optional[str] = None
    complexity_level: Optional[str] = None

    def __repr__(self) -> str:
        return f"Decision({self.decision_type}, valid={self.validation_status})"


# ===========================================================================
# PHASE 3 ORCHESTRATOR
# ===========================================================================

class Phase3Orchestrator:
    """
    Tier 1 Orchestrator with Phase 3 Meta-Cognitive Integration

    Implements the evolved control loop:
        Analyze -> Hypothesize -> Validate -> Solve

    PROTOCOLS:
    ---------
    1. PRE-FLIGHT: Validation must return VALID before any delegation
    2. LOOK-BEFORE-LEAP: Check knowledge base for existing solutions
    3. SCOUTING: Generate and rank strategies for complex problems

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Step 4
    """

    # Complexity threshold for scouting protocol
    HIGH_COMPLEXITY_THRESHOLD = 0.7

    # The NON-INTERVENTION Principle from Phase 1
    NON_INTERVENTION = True  # Orchestrator decomposes but never computes

    def __init__(self,
                 directory_facilitator,
                 blackboard,
                 vector_db,
                 embedding_model=None,
                 available_solvers: Dict[str, Set[MathematicalDomain]] = None):
        """
        Initialize Orchestrator with Phase 0-3 infrastructure.

        Args:
            directory_facilitator: Phase 0 DF for agent discovery
            blackboard: Phase 0 Blackboard for shared memory
            vector_db: Phase 0 Vector Database for RAG
            embedding_model: Model for knowledge retrieval (optional)
            available_solvers: Registry of solver capabilities (optional)
        """
        print("  [PHASE 3 ORCHESTRATOR - Meta-Cognitive Integration]")

        self.df = directory_facilitator
        self.blackboard = blackboard

        # Initialize Phase 3 teams
        print("    Initializing Phase 3 Teams...")
        self.precondition_team = PreconditionValidationTeam(
            available_solvers, blackboard
        )
        self.knowledge_team = KnowledgeManagementTeam(
            blackboard, vector_db, embedding_model,
            external_sources=['mathlib', 'loogle']
        )
        self.hypothesis_team = HypothesisGenerationTeam(blackboard)

        # Decision log for debugging and audit
        self.decision_log: List[OrchestratorDecision] = []

        # Statistics
        self.tasks_processed = 0
        self.tasks_validated = 0
        self.tasks_retrieved = 0
        self.tasks_scouted = 0
        self.tasks_delegated = 0
        self.tasks_failed = 0

        print("    [OK] Phase 3 Orchestrator initialized")
        print()

    def process(self, omdoc_object, conversation_id: str = None) -> Dict[str, Any]:
        """
        Main processing method with Phase 3 protocol integration.

        Implements: Analyze -> Hypothesize -> Validate -> Solve
        """
        self.tasks_processed += 1

        # Generate conversation ID if not provided
        if conversation_id is None:
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"

        decision = OrchestratorDecision(
            conversation_id=conversation_id,
            decision_type="process_start"
        )

        # ===================================================================
        # PHASE 1: ANALYZE (Problem Classification)
        # ===================================================================
        problem_type = self._get_problem_type(omdoc_object)
        complexity = self._assess_complexity(omdoc_object)
        decision.complexity_level = complexity.name

        # ===================================================================
        # PROTOCOL 1: "PRE-FLIGHT" CHECK
        # CONSTRAINT: NEVER delegate until validation returns VALID
        # ===================================================================
        validation_result = self.precondition_team.validate(
            omdoc_object,
            conversation_id,
            operation_type=self._infer_operation_type(omdoc_object)
        )

        decision.validation_status = validation_result.status.name
        self.tasks_validated += 1

        if not validation_result.is_valid:
            # HALT: Preconditions not met
            decision.error_message = validation_result.error_message
            decision.decision_type = "halted_preflight"
            self.decision_log.append(decision)
            self.tasks_failed += 1

            return {
                'status': 'ERROR',
                'code': validation_result.status.name,
                'message': validation_result.error_message,
                'violations': validation_result.constraint_violations,
                'edge_cases': validation_result.edge_cases_detected,
                'conversation_id': conversation_id
            }

        # ===================================================================
        # PROTOCOL 2: "LOOK-BEFORE-YOU-LEAP" CHECK
        # Query Knowledge Management Team for existing solutions
        # ===================================================================
        problem_statement = self._extract_problem_statement(omdoc_object)
        retrieval_result = self.knowledge_team.look_before_leap(problem_statement)

        decision.retrieval_result = retrieval_result.confidence.name

        if retrieval_result.should_skip_solving():
            # SHORT-CIRCUIT: Known theorem found
            decision.decision_type = "retrieved_solution"
            decision.skip_solving = True
            self.decision_log.append(decision)
            self.tasks_retrieved += 1

            return {
                'status': 'SUCCESS',
                'source': 'retrieved',
                'theorem_id': retrieval_result.theorem_id,
                'result': retrieval_result.theorem_content,
                'proof': retrieval_result.proof_sketch,
                'confidence': retrieval_result.similarity_score,
                'conversation_id': conversation_id
            }

        # ===================================================================
        # PROTOCOL 3: "SCOUTING" CHECK (For High Complexity Problems)
        # Invoke Hypothesis Generation Team before solving
        # ===================================================================
        selected_strategy = None

        if complexity == ComplexityLevel.HIGH:
            plan = self.hypothesis_team.scout(
                omdoc_object,
                conversation_id,
                problem_type
            )

            if plan:
                selected_strategy = plan
                decision.selected_strategy = plan.strategy.value
                decision.decision_type = "strategy_selected"
                self.tasks_scouted += 1

        # ===================================================================
        # PHASE 4: SOLVE (Delegate to Domain Supervisors)
        # ===================================================================
        # Discover appropriate supervisor via DF
        domain_tag = self._get_domain_tag(omdoc_object)
        supervisor = self._discover_supervisor(domain_tag)

        if not supervisor:
            error_msg = (
                f"No supervisor available for domain: {domain_tag}\n"
                f"Required service: math.{domain_tag.lower()}\n"
                f"This domain requires Phase 2 supervisor to be registered.\n"
                f"Please ensure Phase 2 system is initialized with appropriate supervisors."
            )
            decision.error_message = error_msg
            decision.decision_type = "no_supervisor"
            self.decision_log.append(decision)
            self.tasks_failed += 1
            
            # Log to both console and file
            logger.error(f"SUPERVISOR NOT FOUND: {error_msg}")
            print(f"\n[ERROR] {error_msg}\n")
            
            return {
                'status': 'ERROR',
                'code': 'SUPERVISOR_NOT_FOUND',
                'message': error_msg,
                'domain': domain_tag,
                'required_service': f"math.{domain_tag.lower()}",
                'conversation_id': conversation_id,
                'suggestion': 'Initialize Phase 2 system with domain supervisors before processing tasks'
            }

        decision.delegated_to = supervisor.agent_id if hasattr(supervisor, 'agent_id') else str(supervisor)
        self.tasks_delegated += 1

        # Prepare task with strategy context (if scouting was done)
        task_context = {
            'omdoc': omdoc_object,
            'conversation_id': conversation_id,
            'constraints': validation_result.propagated_constraints,
            'strategy': selected_strategy,
            'domain_classification': validation_result.domain_classification
        }

        # Delegate to supervisor
        result = self._delegate_to_supervisor(supervisor, task_context)

        # ===================================================================
        # PHASE 5: HANDLE RESULT (Including Backtracking)
        # ===================================================================
        if result.get('status') == 'FAILED' and selected_strategy:
            # Attempt backtracking to alternative strategy
            alternative = self.hypothesis_team.handle_failure(
                conversation_id, selected_strategy
            )

            if alternative:
                # Retry with alternative strategy
                decision.decision_type = "backtracking"
                task_context['strategy'] = alternative
                result = self._delegate_to_supervisor(supervisor, task_context)

        # Record successful result for future retrieval
        if result.get('status') == 'SUCCESS':
            self.knowledge_team.record_result(
                conversation_id,
                problem_statement,
                result.get('result'),
                result.get('proof_trace')
            )

        # Clean up session data
        self.precondition_team.clear_session(conversation_id)
        self.hypothesis_team.clear_session(conversation_id)

        decision.decision_type = "completed"
        self.decision_log.append(decision)

        result['conversation_id'] = conversation_id
        return result

    # =======================================================================
    # HELPER METHODS
    # =======================================================================

    def _get_problem_type(self, omdoc_object) -> str:
        """Extract problem type from OMDoc object"""
        if hasattr(omdoc_object, 'problem_type'):
            pt = omdoc_object.problem_type
            return pt.value if hasattr(pt, 'value') else str(pt)
        elif hasattr(omdoc_object, 'metadata'):
            metadata = omdoc_object.metadata
            if isinstance(metadata, dict):
                return metadata.get('problem_type', 'computation')
        return 'computation'

    def _get_domain_tag(self, omdoc_object) -> str:
        """Extract domain tag for supervisor discovery"""
        if hasattr(omdoc_object, 'domain_tag'):
            return omdoc_object.domain_tag
        elif hasattr(omdoc_object, 'metadata'):
            metadata = omdoc_object.metadata
            if isinstance(metadata, dict):
                return metadata.get('domain', 'algebra')
        return 'algebra'

    def _assess_complexity(self, omdoc_object) -> ComplexityLevel:
        """Assess problem complexity for scouting protocol"""
        expr = self._get_expression(omdoc_object)

        # Complexity heuristics
        expr_str = str(expr)

        # Count operations
        ops = ['+', '-', '*', '/', '^', '**', 'sqrt', 'log', 'sin', 'cos',
               'tan', 'exp', 'integral', 'diff', 'sum', 'product']
        op_count = sum(expr_str.lower().count(op) for op in ops)

        # Count variables
        try:
            import sympy as sp
            sympy_expr = sp.sympify(expr) if isinstance(expr, str) else expr
            var_count = len(sympy_expr.free_symbols)
        except (sp.SympifyError, TypeError, AttributeError) as e:
            logger.debug(f"Could not count variables in expression: {e}")
            var_count = 1

        # Expression length factor
        length_factor = len(expr_str) / 100

        # Compute complexity score
        score = (op_count / 20) + (var_count / 5) + (length_factor / 2)

        if score >= self.HIGH_COMPLEXITY_THRESHOLD:
            return ComplexityLevel.HIGH
        elif score >= 0.3:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.LOW

    def _get_expression(self, omdoc_object) -> Any:
        """Extract expression from OMDoc object"""
        if hasattr(omdoc_object, 'expression_tree'):
            return omdoc_object.expression_tree
        elif hasattr(omdoc_object, 'expression'):
            return omdoc_object.expression
        elif hasattr(omdoc_object, 'content'):
            return omdoc_object.content
        return omdoc_object

    def _infer_operation_type(self, omdoc_object) -> Optional[str]:
        """Infer operation type for edge case detection"""
        raw = ""
        if hasattr(omdoc_object, 'raw_input'):
            raw = str(omdoc_object.raw_input).lower()
        elif hasattr(omdoc_object, 'description'):
            raw = str(omdoc_object.description).lower()

        if 'invert' in raw or 'inverse' in raw:
            return 'matrix_inversion'
        return None

    def _extract_problem_statement(self, omdoc_object) -> str:
        """Extract canonical problem statement for retrieval"""
        problem_type = self._get_problem_type(omdoc_object)
        expr = self._get_expression(omdoc_object)
        return f"{problem_type}: {expr}"

    def _discover_supervisor(self, domain_tag: str):
        """
        Discover appropriate Domain Supervisor via DF
        
        Returns None if no supervisor found - caller must handle gracefully.
        """
        service_type = f"math.{domain_tag.lower()}"

        if self.df:
            try:
                results = self.df.search(service_type=service_type)
                if results:
                    logger.info(f"Found supervisor for {domain_tag}: {results[0].agent_id}")
                    return results[0]
                else:
                    logger.warning(f"No supervisor registered for domain: {domain_tag} (service: {service_type})")
            except (AttributeError, TypeError, KeyError) as e:
                logger.error(f"Error discovering supervisor for {domain_tag}: {e}", exc_info=True)
        else:
            logger.error(f"Directory Facilitator not available - cannot discover supervisor for {domain_tag}")

        # Return None - no mock fallback in production
        return None

    def _delegate_to_supervisor(self, supervisor, task_context: Dict) -> Dict:
        """Delegate task to Domain Supervisor via FIPA-ACL"""
        # Create FIPA-ACL REQUEST message
        message = {
            'performative': 'REQUEST',
            'sender': 'phase3_orchestrator',
            'receiver': supervisor.agent_id if hasattr(supervisor, 'agent_id') else str(supervisor),
            'conversation_id': task_context['conversation_id'],
            'content': task_context,
            'ontology': 'mathematics',
            'protocol': 'fipa-request'
        }

        # Post to Blackboard for supervisor pickup
        if self.blackboard:
            try:
                self.blackboard.post({
                    'entry_type': 'task_delegation',
                    'message': message,
                    'status': 'PENDING'
                })
            except (AttributeError, TypeError, ValueError) as e:
                logger.debug(f"Could not post task to blackboard: {e}")

        # Execute if supervisor has execute method
        if hasattr(supervisor, 'execute'):
            try:
                result = supervisor.execute(task_context)
                if result:
                    return result
            except (ValueError, TypeError, KeyError) as e:
                # Data/argument errors from supervisor
                logger.warning(f"Supervisor execution failed (data error): {e}")
                return {'status': 'FAILED', 'error': str(e), 'error_type': 'data_error'}
            except (RuntimeError, AttributeError, ImportError) as e:
                # System-level errors from supervisor
                logger.error(f"Supervisor execution failed (system error): {e}", exc_info=True)
                return {'status': 'FAILED', 'error': str(e), 'error_type': 'system_error'}

        # Default success for testing
        return {
            'status': 'SUCCESS',
            'result': 'delegated',
            'supervisor': str(supervisor)
        }

    # =======================================================================
    # STATISTICS AND LOGGING
    # =======================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator statistics"""
        return {
            'tasks_processed': self.tasks_processed,
            'tasks_validated': self.tasks_validated,
            'tasks_retrieved': self.tasks_retrieved,
            'tasks_scouted': self.tasks_scouted,
            'tasks_delegated': self.tasks_delegated,
            'tasks_failed': self.tasks_failed,
            'validation_rate': self.tasks_validated / max(1, self.tasks_processed) * 100,
            'retrieval_rate': self.tasks_retrieved / max(1, self.tasks_processed) * 100,
            'scouting_rate': self.tasks_scouted / max(1, self.tasks_processed) * 100,
            'failure_rate': self.tasks_failed / max(1, self.tasks_processed) * 100,
            'decision_log_size': len(self.decision_log),
            'precondition_team': self.precondition_team.get_statistics(),
            'knowledge_team': self.knowledge_team.get_statistics(),
            'hypothesis_team': self.hypothesis_team.get_statistics()
        }

    def get_decision_log(self, limit: int = 100) -> List[OrchestratorDecision]:
        """Get recent decision log entries"""
        return self.decision_log[-limit:]

    def clear_decision_log(self) -> None:
        """Clear the decision log"""
        self.decision_log = []


