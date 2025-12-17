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
FAILURE ANALYSIS TEAM - "The Trauma Surgeons"
==============================================

Phase 4 Step 2: Graceful Incompleteness Handling System

PURPOSE:
-------
Construct a three-agent team that intercepts all failure signals, diagnoses
the root cause, and autonomously reroutes the system to alternative solution
strategies. Ensures the system never "gives up" with a generic error.

WHY THIS MATTERS:
----------------
Standard mathematical systems return generic ERROR messages when solvers fail,
aborting entire sessions. This team distinguishes between:
- Computational Error: Timeout, Overflow, Memory Exhaustion
- Logical Error: Invalid inference, step mismatch
- Domain Error: Method inapplicable, precondition violation

AGENTS:
------
1. Error Classifier: Diagnostic interceptor (classifies errors)
2. Root Cause Analyzer: Traces failure to specific agent/step
3. Alternative Path Generator: "Plan B" engine

REFERENCE:
---------
- Phase_4_Build_Order_Breakdown.md: Step 2
- Phase 4 transforms this collection of agents into a Self-Correction Engine.md
"""

import sys
import os
import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import re
import traceback
import uuid
import threading

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Get module logger
logger = logging.getLogger('symbo_agentic_reasoners.phase4.failure_analysis')


# ===========================================================================
# ENUMS AND DATA CLASSES
# ===========================================================================

class ErrorType(Enum):
    """
    Three-Category Error Taxonomy

    COMPUTATIONAL: Resource-related failures (timeout, overflow, memory)
    LOGICAL: Reasoning failures (invalid inference, contradiction)
    DOMAIN: Method applicability failures (precondition violation)

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 2.1 (Error Classifier)
    """
    COMPUTATIONAL = auto()  # Timeout, Overflow, Memory Exhaustion
    LOGICAL = auto()        # Invalid inference, step mismatch
    DOMAIN = auto()         # Method inapplicable, precondition violation


class RemedyAction(Enum):
    """
    Prescribed remediation actions for each error type

    REQUEST_RESOURCES: Increase timeout/memory for computational errors
    TRIGGER_REFINEMENT: Engage "Thinker" loop for logical errors
    TRIGGER_ALTERNATIVE: Generate alternative plan for domain errors
    """
    REQUEST_RESOURCES = auto()   # For COMPUTATIONAL errors
    TRIGGER_REFINEMENT = auto()  # For LOGICAL errors
    TRIGGER_ALTERNATIVE = auto()  # For DOMAIN errors


class FailureStatus(Enum):
    """Status of a failure case"""
    DETECTED = auto()
    CLASSIFIED = auto()
    ANALYZING = auto()
    ROOT_CAUSE_FOUND = auto()
    ALTERNATIVE_GENERATED = auto()
    RECOVERED = auto()
    UNRECOVERABLE = auto()


@dataclass
class FailureReport:
    """
    Structured failure diagnosis

    Captures all information about a failure including classification,
    root cause analysis, and recommended recovery action.

    FIELDS:
    ------
    - failure_id: Unique failure identifier
    - error_type: Classified error type (COMPUTATIONAL/LOGICAL/DOMAIN)
    - remedy_action: Recommended action
    - failing_agent: Agent that produced the failure
    - failing_step: Specific step where failure occurred
    - error_message: Original error message
    - stack_trace: Full stack trace if available
    - root_cause: Detailed root cause analysis
    - alternative_plan: Generated alternative if applicable
    """
    failure_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    error_type: ErrorType = ErrorType.DOMAIN
    remedy_action: RemedyAction = RemedyAction.TRIGGER_ALTERNATIVE
    failing_agent: str = ""
    failing_step: Optional[str] = None
    error_message: str = ""
    stack_trace: Optional[str] = None
    root_cause: Optional[str] = None
    alternative_plan: Optional[Dict] = None
    conversation_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    status: FailureStatus = FailureStatus.DETECTED
    metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_recovered(self):
        """Mark this failure as recovered"""
        self.status = FailureStatus.RECOVERED

    def mark_unrecoverable(self, reason: str):
        """Mark this failure as unrecoverable"""
        self.status = FailureStatus.UNRECOVERABLE
        self.metadata['unrecoverable_reason'] = reason


@dataclass
class ExecutionStep:
    """
    Record of a single execution step for tracing

    Used by Root Cause Analyzer to trace failures back to specific steps.
    """
    step_id: str
    agent_id: str
    operation: str
    input_data: Any
    output_data: Optional[Any] = None
    success: bool = True
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ===========================================================================
# AGENT 2.1: THE ERROR CLASSIFIER
# ===========================================================================

class ErrorClassifier:
    """
    Agent 2.1: Diagnostic Interceptor

    DIRECTIVE:
    ---------
    Implement a diagnostic agent that intercepts ALL FAILURE signals from
    the Blackboard and classifies them into actionable categories.

    ERROR TAXONOMY:
    --------------
    1. Computational Error (Timeout, Overflow, Memory) -> REQUEST_RESOURCES
    2. Logical Error (Invalid inference, step mismatch) -> TRIGGER_REFINEMENT
    3. Domain Error (Method inapplicable) -> TRIGGER_ALTERNATIVE

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 2.1
    """

    # Pattern matching for error classification
    COMPUTATIONAL_PATTERNS = [
        r'timeout', r'timed?\s*out', r'overflow', r'memory',
        r'resource', r'exceeded', r'limit', r'oom',
        r'killed', r'vram', r'out\s*of\s*memory', r'exhausted',
        r'max.*iterations', r'stack.*overflow'
    ]

    LOGICAL_PATTERNS = [
        r'does\s*not\s*follow', r'invalid.*inference', r'contradiction',
        r'step.*mismatch', r'type.*error', r'assertion.*failed',
        r'inconsistent', r'circular', r'recursive.*limit',
        r'proof.*failed', r'verification.*failed', r'invalid.*step'
    ]

    DOMAIN_PATTERNS = [
        r'inapplicable', r'precondition', r'domain.*error',
        r'not.*defined', r'unsupported', r'cannot.*apply',
        r'no.*solution', r'undefined', r'singular', r'discontinuous',
        r'complex.*infinity', r'division.*zero', r'invalid.*input',
        r'constraint.*violation', r'out.*of.*domain'
    ]

    def __init__(self, blackboard=None):
        """
        Initialize Error Classifier

        Args:
            blackboard: Phase 0 Blackboard instance
        """
        self.blackboard = blackboard
        self._lock = threading.RLock()

        # Compile patterns for efficiency
        self._computational_regex = [
            re.compile(p, re.IGNORECASE) for p in self.COMPUTATIONAL_PATTERNS
        ]
        self._logical_regex = [
            re.compile(p, re.IGNORECASE) for p in self.LOGICAL_PATTERNS
        ]
        self._domain_regex = [
            re.compile(p, re.IGNORECASE) for p in self.DOMAIN_PATTERNS
        ]

        # Statistics
        self.failures_classified = 0
        self.computational_errors = 0
        self.logical_errors = 0
        self.domain_errors = 0

        if self.blackboard:
            self._subscribe_to_failures()

        print("    [OK] Error Classifier Agent initialized")

    def _subscribe_to_failures(self):
        """Subscribe to all FAILURE signals on Blackboard"""
        try:
            self.blackboard.subscribe(
                agent_id='error_classifier_001',
                tags=['FAILURE_SIGNAL'],
                callback=self._on_failure_signal
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to failures: {type(e).__name__}: {e}")

    def _on_failure_signal(self, entry):
        """Callback when FAILURE_SIGNAL is posted"""
        if hasattr(entry, 'metadata'):
            failure_data = entry.metadata.get('failure_data', {})
            if failure_data:
                self.classify_failure(failure_data)

    def classify_failure(self, failure_entry: Dict) -> FailureReport:
        """
        Classify failure into actionable category

        This is the main entry point for error classification.

        Args:
            failure_entry: Dictionary containing:
                - error_message: The error message
                - stack_trace: Optional stack trace
                - agent_id: Agent that failed
                - step: Optional step identifier
                - conversation_id: Conversation tracking ID

        Returns:
            FailureReport with classification and recommended action
        """
        with self._lock:
            self.failures_classified += 1

            error_msg = failure_entry.get('error_message', '')
            stack = failure_entry.get('stack_trace', '')

            # Pattern matching classification
            error_type, remedy = self._match_patterns(error_msg, stack)

            # Update statistics
            if error_type == ErrorType.COMPUTATIONAL:
                self.computational_errors += 1
            elif error_type == ErrorType.LOGICAL:
                self.logical_errors += 1
            else:
                self.domain_errors += 1

            report = FailureReport(
                failure_id=failure_entry.get('failure_id', str(uuid.uuid4())),
                error_type=error_type,
                remedy_action=remedy,
                failing_agent=failure_entry.get('agent_id', 'unknown'),
                failing_step=failure_entry.get('step'),
                error_message=error_msg,
                stack_trace=stack,
                conversation_id=failure_entry.get('conversation_id', ''),
                status=FailureStatus.CLASSIFIED
            )

            # Post classification for Root Cause Analyzer
            if self.blackboard:
                self._post_classification(report)

            print(f"    [CLASSIFIER] {error_type.name} error from {report.failing_agent}")
            print(f"                 Action: {remedy.name}")

            return report

    def _match_patterns(self, error_msg: str, stack: str) -> Tuple[ErrorType, RemedyAction]:
        """
        Match error against pattern taxonomy

        Returns:
            Tuple of (ErrorType, RemedyAction)
        """
        combined = f"{error_msg} {stack}".lower()

        # Check computational patterns first (usually most critical)
        for regex in self._computational_regex:
            if regex.search(combined):
                return ErrorType.COMPUTATIONAL, RemedyAction.REQUEST_RESOURCES

        # Check logical patterns
        for regex in self._logical_regex:
            if regex.search(combined):
                return ErrorType.LOGICAL, RemedyAction.TRIGGER_REFINEMENT

        # Check domain patterns
        for regex in self._domain_regex:
            if regex.search(combined):
                return ErrorType.DOMAIN, RemedyAction.TRIGGER_ALTERNATIVE

        # Default to domain error (safest assumption - try alternative method)
        return ErrorType.DOMAIN, RemedyAction.TRIGGER_ALTERNATIVE

    def _post_classification(self, report: FailureReport):
        """Post classification to Blackboard"""
        try:
            from symbo_agentic_reasoners_phase0.memory.blackboard import create_entry, EntryType
            entry = create_entry(
                entry_type=EntryType.TASK,
                content={
                    'failure_id': report.failure_id,
                    'error_type': report.error_type.name,
                    'remedy_action': report.remedy_action.name,
                    'failing_agent': report.failing_agent,
                    'failing_step': report.failing_step,
                    'error_message': report.error_message
                },
                author_agent='error_classifier_001',
                conversation_id=report.conversation_id,
                tags=['CLASSIFIED_FAILURE', report.failure_id],
                metadata={
                    'entry_type': 'CLASSIFIED_FAILURE',
                    'status': 'AWAITING_ROOT_CAUSE'
                }
            )
            self.blackboard.post(entry)
        except Exception as e:
            logger.debug(f"Could not post classified failure: {type(e).__name__}: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get classifier statistics"""
        return {
            'failures_classified': self.failures_classified,
            'computational_errors': self.computational_errors,
            'logical_errors': self.logical_errors,
            'domain_errors': self.domain_errors
        }


# ===========================================================================
# AGENT 2.2: THE ROOT CAUSE ANALYZER
# ===========================================================================

class RootCauseAnalyzer:
    """
    Agent 2.2: Failure Attribution System

    DIRECTIVE:
    ---------
    Trace the error back to the specific step or agent responsible
    for the failure.

    FUNCTION:
    --------
    Prevents the system from blaming the Orchestrator for a failure that
    occurred deep within the Linear Algebra Sub-team's decomposition agent.
    Creates precise failure attribution for targeted remediation.

    OUTPUT:
    ------
    ROOT_CAUSE_ANALYSIS report with:
    - failing_agent
    - failing_step
    - error_context
    - recommended_action

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 2.2
    """

    def __init__(self, blackboard=None):
        """
        Initialize Root Cause Analyzer

        Args:
            blackboard: Phase 0 Blackboard instance
        """
        self.blackboard = blackboard
        self._lock = threading.RLock()

        # Execution traces by conversation
        self.execution_traces: Dict[str, List[ExecutionStep]] = {}

        # Statistics
        self.analyses_performed = 0
        self.root_causes_found = 0

        if self.blackboard:
            self._subscribe_to_classified_failures()

        print("    [OK] Root Cause Analyzer Agent initialized")

    def _subscribe_to_classified_failures(self):
        """Subscribe to CLASSIFIED_FAILURE events"""
        try:
            self.blackboard.subscribe(
                agent_id='root_cause_analyzer_001',
                tags=['CLASSIFIED_FAILURE'],
                callback=self._on_classified_failure
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to classified failures: {type(e).__name__}: {e}")

    def _on_classified_failure(self, entry):
        """Callback for classified failures"""
        if hasattr(entry, 'content') and isinstance(entry.content, dict):
            self.analyze_root_cause(entry.content)

    def log_execution_step(self, conversation_id: str, step: ExecutionStep):
        """
        Log an execution step for later analysis

        Called by agents to log their execution steps. This builds
        the trace that allows root cause analysis.

        Args:
            conversation_id: Conversation tracking ID
            step: ExecutionStep to log
        """
        with self._lock:
            if conversation_id not in self.execution_traces:
                self.execution_traces[conversation_id] = []
            self.execution_traces[conversation_id].append(step)

    def analyze_root_cause(self, classified_data: Dict) -> Dict:
        """
        Trace failure to specific agent and step

        Args:
            classified_data: Classification from Error Classifier

        Returns:
            Analysis report with root cause and recommendations
        """
        with self._lock:
            self.analyses_performed += 1

            conversation_id = classified_data.get('conversation_id', '')
            failing_agent = classified_data.get('failing_agent', 'unknown')
            error_type = classified_data.get('error_type', 'DOMAIN')
            error_message = classified_data.get('error_message', '')

            # Get execution trace
            trace = self.execution_traces.get(conversation_id, [])

            # Find failure point in trace
            root_cause = self._find_failure_point(trace, failing_agent)

            # Attribute failure
            attribution = self._attribute_failure(root_cause, trace)

            # Generate recommendation
            recommendation = self._recommend_action(error_type, attribution)

            if root_cause.get('step_details'):
                self.root_causes_found += 1

            analysis = {
                'failure_id': classified_data.get('failure_id', ''),
                'conversation_id': conversation_id,
                'root_cause': root_cause,
                'attribution': attribution,
                'trace_depth': len(trace),
                'recommended_action': recommendation,
                'error_type': error_type
            }

            # Post for Alternative Path Generator
            if self.blackboard:
                self._post_analysis(analysis, classified_data)

            print(f"    [ANALYZER] Root cause: {attribution.get('responsible_agent', 'unknown')}")
            print(f"               Recommendation: {recommendation}")

            return analysis

    def _find_failure_point(self, trace: List[ExecutionStep],
                           failing_agent: str) -> Dict:
        """Find exact step where failure occurred"""
        for i, step in enumerate(reversed(trace)):
            if step.agent_id == failing_agent:
                return {
                    'step_index': len(trace) - i - 1,
                    'step_details': {
                        'step_id': step.step_id,
                        'agent_id': step.agent_id,
                        'operation': step.operation,
                        'input': step.input_data,
                        'success': step.success
                    },
                    'preceding_steps': [
                        {
                            'agent_id': s.agent_id,
                            'operation': s.operation,
                            'success': s.success
                        }
                        for s in trace[:len(trace) - i - 1]
                    ]
                }

        # Not found in trace
        return {
            'step_index': -1,
            'step_details': None,
            'preceding_steps': [
                {'agent_id': s.agent_id, 'operation': s.operation}
                for s in trace
            ]
        }

    def _attribute_failure(self, root_cause: Dict,
                          trace: List[ExecutionStep]) -> Dict:
        """Determine responsible component"""
        if not root_cause.get('step_details'):
            return {
                'responsible_agent': 'unknown',
                'responsible_operation': 'unknown',
                'confidence': 0.3
            }

        step = root_cause['step_details']

        # Check if failure was due to bad input from previous step
        preceding = root_cause.get('preceding_steps', [])
        bad_input_from = None

        if preceding:
            # Look for a preceding failed step
            for prev in reversed(preceding):
                if not prev.get('success', True):
                    bad_input_from = prev.get('agent_id')
                    break

        return {
            'responsible_agent': bad_input_from or step.get('agent_id', 'unknown'),
            'responsible_operation': step.get('operation', 'unknown'),
            'input_state': step.get('input'),
            'confidence': 0.9 if step else 0.5,
            'cascade_from': bad_input_from
        }

    def _recommend_action(self, error_type: str, attribution: Dict) -> str:
        """Generate specific recommendation based on error and attribution"""
        responsible = attribution.get('responsible_agent', 'unknown')
        operation = attribution.get('responsible_operation', 'unknown')

        recommendations = {
            'COMPUTATIONAL': f"Increase resources/timeout for {responsible}",
            'LOGICAL': f"Refine reasoning at {operation} in {responsible}",
            'DOMAIN': f"Generate alternative strategy avoiding {operation}"
        }

        return recommendations.get(error_type, "Generate alternative solution strategy")

    def _post_analysis(self, analysis: Dict, original_data: Dict):
        """Post analysis to Blackboard"""
        try:
            from symbo_agentic_reasoners_phase0.memory.blackboard import create_entry, EntryType
            entry = create_entry(
                entry_type=EntryType.TASK,
                content={
                    'analysis': analysis,
                    'original_report': original_data
                },
                author_agent='root_cause_analyzer_001',
                conversation_id=analysis.get('conversation_id', ''),
                tags=['ROOT_CAUSE_ANALYSIS', analysis.get('failure_id', '')],
                metadata={
                    'entry_type': 'ROOT_CAUSE_ANALYSIS',
                    'status': 'AWAITING_ALTERNATIVE'
                }
            )
            self.blackboard.post(entry)
        except Exception as e:
            logger.debug(f"Could not post root cause analysis: {type(e).__name__}: {e}")

    def clear_trace(self, conversation_id: str):
        """Clear execution trace for a completed conversation"""
        with self._lock:
            if conversation_id in self.execution_traces:
                del self.execution_traces[conversation_id]

    def get_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics"""
        return {
            'analyses_performed': self.analyses_performed,
            'root_causes_found': self.root_causes_found,
            'active_traces': len(self.execution_traces)
        }


# ===========================================================================
# AGENT 2.3: THE ALTERNATIVE PATH GENERATOR
# ===========================================================================

class AlternativePathGenerator:
    """
    Agent 2.3: The "Plan B" Engine

    DIRECTIVE:
    ---------
    Build the autonomous recovery engine that constructs alternative
    solution strategies.

    CRITICAL INTEGRATION:
    --------------------
    Connect directly to the Hypothesis Generator (Phase 3). When Error
    Classifier reports "Symbolic Integration Failed (Domain Error),"
    this agent immediately constructs a new plan: "Attempt Numerical
    Quadrature with high precision."

    MECHANISM:
    ---------
    Posts new plan to Blackboard, effectively "healing" the broken process
    without user intervention. The system continues seamlessly from the
    alternative strategy.

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 2.3
    """

    # Fallback strategy mappings
    # Maps failed method -> ordered list of alternatives
    FALLBACK_STRATEGIES = {
        # Integration fallbacks
        'symbolic_integration': ['numerical_quadrature', 'monte_carlo_integration', 'series_expansion'],
        'risch_algorithm': ['heuristic_integration', 'numerical_quadrature'],
        'integration_by_parts': ['u_substitution', 'numerical_quadrature'],
        'partial_fractions': ['numerical_quadrature', 'series_expansion'],

        # Differentiation fallbacks
        'symbolic_differentiation': ['numerical_differentiation', 'autodiff'],
        'chain_rule': ['numerical_differentiation', 'finite_difference'],

        # Algebraic solving fallbacks
        'algebraic_solving': ['numerical_root_finding', 'newton_raphson', 'bisection'],
        'groebner_basis': ['heuristic_factoring', 'numerical_solving'],
        'factorization': ['quadratic_formula', 'numerical_root_finding'],

        # Linear algebra fallbacks
        'matrix_inversion': ['pseudo_inverse', 'iterative_solver', 'lu_decomposition'],
        'eigenvalue_decomposition': ['power_method', 'qr_algorithm'],
        'svd': ['iterative_svd', 'randomized_svd'],

        # Limits and series fallbacks
        'symbolic_limit': ['epsilon_delta_approximation', 'series_expansion'],
        'taylor_series': ['pade_approximation', 'numerical_evaluation'],

        # Proof fallbacks
        'direct_proof': ['proof_by_contradiction', 'proof_by_induction'],
        'induction': ['strong_induction', 'structural_induction'],
    }

    def __init__(self, blackboard=None, hypothesis_generator=None):
        """
        Initialize Alternative Path Generator

        Args:
            blackboard: Phase 0 Blackboard instance
            hypothesis_generator: Phase 3 Hypothesis Generator for creative alternatives
        """
        self.blackboard = blackboard
        self.hypothesis_generator = hypothesis_generator
        self._lock = threading.RLock()

        # Statistics
        self.alternatives_generated = 0
        self.plans_executed = 0
        self.recoveries_successful = 0

        if self.blackboard:
            self._subscribe_to_root_cause()

        print("    [OK] Alternative Path Generator Agent initialized")

    def _subscribe_to_root_cause(self):
        """Subscribe to ROOT_CAUSE_ANALYSIS events"""
        try:
            self.blackboard.subscribe(
                agent_id='alternative_path_generator_001',
                tags=['ROOT_CAUSE_ANALYSIS'],
                callback=self._on_root_cause_analysis
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to root cause: {type(e).__name__}: {e}")

    def _on_root_cause_analysis(self, entry):
        """Callback for root cause analysis results"""
        if hasattr(entry, 'content') and isinstance(entry.content, dict):
            self.generate_alternative(entry.content)

    def generate_alternative(self, analysis_entry: Dict) -> Dict:
        """
        Construct alternative solution strategy

        This is the "Plan B" generation logic. Creates a new plan
        that avoids the failed method.

        Args:
            analysis_entry: Dictionary containing:
                - analysis: Root cause analysis
                - original_report: Original failure report

        Returns:
            Plan B dictionary ready for execution
        """
        with self._lock:
            self.alternatives_generated += 1

            analysis = analysis_entry.get('analysis', {})
            original_report = analysis_entry.get('original_report', {})

            # Get failed method/operation
            attribution = analysis.get('attribution', {})
            failed_method = attribution.get('responsible_operation', '')
            failed_agent = attribution.get('responsible_agent', '')
            error_type = analysis.get('error_type', 'DOMAIN')

            # Look up fallback strategies
            alternatives = self._get_fallbacks(failed_method)

            if not alternatives and self.hypothesis_generator:
                # Delegate to Hypothesis Generator for creative alternatives
                try:
                    problem_context = {
                        'failed_method': failed_method,
                        'failed_agent': failed_agent,
                        'error_type': error_type
                    }
                    strategies = self.hypothesis_generator.generate_hypotheses(
                        problem_context,
                        problem_type='recovery'
                    )
                    alternatives = [s.strategy.value for s in strategies
                                  if s.strategy.value != failed_method]
                except Exception as e:
                    logger.debug(f"Hypothesis generation failed, using defaults: {e}")

            if not alternatives:
                # Default fallback
                alternatives = ['numerical_fallback', 'heuristic_approach']

            # Construct Plan B
            plan_b = {
                'plan_type': 'ALTERNATIVE',
                'plan_id': f'plan_b_{uuid.uuid4().hex[:8]}',
                'original_failure': original_report.get('failure_id', ''),
                'failed_method': failed_method,
                'strategies': alternatives,
                'priority_order': self._rank_strategies(alternatives, analysis),
                'metadata': {
                    'generated_by': 'alternative_path_generator_001',
                    'reason': f"Fallback from {failed_method}",
                    'error_type': error_type,
                    'timestamp': datetime.now().isoformat()
                }
            }

            # Post Plan B to Blackboard
            if self.blackboard:
                self._post_alternative_plan(plan_b, analysis)

            print(f"    [PLAN B] Generated {len(alternatives)} alternatives")
            print(f"             Primary: {alternatives[0] if alternatives else 'none'}")

            return plan_b

    def _get_fallbacks(self, failed_method: str) -> List[str]:
        """Retrieve predefined fallback strategies"""
        if not failed_method:
            return []

        failed_lower = failed_method.lower()

        # Check exact match first
        for method, fallbacks in self.FALLBACK_STRATEGIES.items():
            if method == failed_lower:
                return fallbacks.copy()

        # Check partial match
        for method, fallbacks in self.FALLBACK_STRATEGIES.items():
            if method in failed_lower or failed_lower in method:
                return fallbacks.copy()

        return []

    def _rank_strategies(self, strategies: List[str],
                        analysis: Dict) -> List[Dict]:
        """Rank alternatives by expected success probability"""
        ranked = []
        attribution = analysis.get('attribution', {})
        error_type = analysis.get('error_type', 'DOMAIN')

        for i, strategy in enumerate(strategies):
            score = self._estimate_success(strategy, error_type, attribution)
            ranked.append({
                'strategy': strategy,
                'rank': i + 1,
                'estimated_success': score,
                'rationale': self._get_strategy_rationale(strategy, error_type)
            })

        return sorted(ranked, key=lambda x: x['estimated_success'], reverse=True)

    def _estimate_success(self, strategy: str, error_type: str,
                         attribution: Dict) -> float:
        """Estimate success probability based on context"""
        base_score = 0.5

        # Numerical methods often succeed as fallback
        if 'numerical' in strategy.lower():
            base_score += 0.25

        # Heuristic methods are reliable but less precise
        if 'heuristic' in strategy.lower():
            base_score += 0.15

        # Monte Carlo works well for intractable integrals
        if 'monte_carlo' in strategy.lower():
            base_score += 0.2

        # Iterative methods good for computational errors
        if error_type == 'COMPUTATIONAL' and 'iterative' in strategy.lower():
            base_score += 0.15

        # High attribution confidence suggests good diagnosis
        if attribution.get('confidence', 0) > 0.8:
            base_score += 0.1

        return min(base_score, 0.95)

    def _get_strategy_rationale(self, strategy: str, error_type: str) -> str:
        """Generate human-readable rationale for strategy"""
        rationales = {
            'numerical_quadrature': "Numerical integration bypasses symbolic limitations",
            'monte_carlo_integration': "Stochastic methods handle complex integrands",
            'numerical_root_finding': "Iterative methods find approximate solutions",
            'newton_raphson': "Fast convergence for well-behaved functions",
            'pseudo_inverse': "Handles singular/ill-conditioned matrices",
            'iterative_solver': "Memory-efficient for large systems",
            'heuristic_integration': "Pattern-based approach for common forms",
            'series_expansion': "Approximation via power series",
            'numerical_differentiation': "Finite differences avoid symbolic complexity",
        }
        return rationales.get(strategy.lower(), f"Alternative approach for {error_type} error")

    def _post_alternative_plan(self, plan_b: Dict, analysis: Dict):
        """Post Plan B to Blackboard and signal recovery"""
        try:
            from symbo_agentic_reasoners_phase0.memory.blackboard import create_entry, EntryType
            conversation_id = analysis.get('conversation_id', '')

            # Post Plan B
            plan_entry = create_entry(
                entry_type=EntryType.TASK,
                content=plan_b,
                author_agent='alternative_path_generator_001',
                conversation_id=conversation_id,
                tags=['ALTERNATIVE_PLAN', plan_b['plan_id']],
                metadata={
                    'entry_type': 'ALTERNATIVE_PLAN',
                    'status': 'READY_FOR_EXECUTION'
                }
            )
            self.blackboard.post(plan_entry)

            # Signal Orchestrator to continue with Plan B
            continue_entry = create_entry(
                entry_type=EntryType.TASK,
                content={
                    'new_plan': plan_b,
                    'original_conversation_id': conversation_id
                },
                author_agent='alternative_path_generator_001',
                conversation_id=conversation_id,
                tags=['WORKFLOW_CONTINUE', plan_b['plan_id']],
                metadata={
                    'entry_type': 'WORKFLOW_CONTINUE',
                    'plan_id': plan_b['plan_id']
                }
            )
            self.blackboard.post(continue_entry)

        except Exception as e:
            logger.error(f"Failed to post recovery plan: {type(e).__name__}: {e}")

    def mark_recovery_success(self, plan_id: str):
        """Mark a recovery plan as successful"""
        with self._lock:
            self.recoveries_successful += 1
            self.plans_executed += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get generator statistics"""
        return {
            'alternatives_generated': self.alternatives_generated,
            'plans_executed': self.plans_executed,
            'recoveries_successful': self.recoveries_successful,
            'recovery_rate': (self.recoveries_successful / max(1, self.plans_executed)) * 100
        }


# ===========================================================================
# FAILURE ANALYSIS TEAM COORDINATOR
# ===========================================================================

class FailureAnalysisTeam:
    """
    Coordinator for the Failure Analysis Team ("The Trauma Surgeons")

    Brings together the three agents:
    1. Error Classifier (Diagnostic interceptor)
    2. Root Cause Analyzer (Failure attribution)
    3. Alternative Path Generator (Plan B engine)

    KEY PROTOCOLS:
    -------------
    - handle_failure(): Full failure handling pipeline
    - classify_error(): Quick error classification
    - generate_recovery_plan(): Create alternative approach

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Step 2
    """

    def __init__(self, blackboard=None, hypothesis_generator=None):
        """
        Initialize the Failure Analysis Team

        Args:
            blackboard: Phase 0 Blackboard for coordination
            hypothesis_generator: Phase 3 Hypothesis Generator for creative recovery
        """
        print("  [FAILURE ANALYSIS TEAM - The Trauma Surgeons]")

        self.blackboard = blackboard
        self.hypothesis_generator = hypothesis_generator

        # Initialize agents
        self.error_classifier = ErrorClassifier(blackboard)
        self.root_cause_analyzer = RootCauseAnalyzer(blackboard)
        self.alternative_path_generator = AlternativePathGenerator(
            blackboard, hypothesis_generator
        )

        # Statistics
        self.failures_handled = 0
        self.recoveries_attempted = 0

        print("    [OK] Failure Analysis Team assembled")

    def handle_failure(self, failure_data: Dict) -> Dict:
        """
        Full failure handling pipeline

        This is the main entry point for failure analysis.

        Args:
            failure_data: Dictionary containing:
                - error_message: The error message
                - stack_trace: Optional stack trace
                - agent_id: Agent that failed
                - step: Optional step identifier
                - conversation_id: Conversation tracking ID

        Returns:
            Recovery plan or failure report
        """
        self.failures_handled += 1

        # Step 1: Classify the error
        report = self.error_classifier.classify_failure(failure_data)

        # Step 2: Analyze root cause
        classified_data = {
            'failure_id': report.failure_id,
            'error_type': report.error_type.name,
            'remedy_action': report.remedy_action.name,
            'failing_agent': report.failing_agent,
            'failing_step': report.failing_step,
            'error_message': report.error_message,
            'conversation_id': report.conversation_id
        }
        analysis = self.root_cause_analyzer.analyze_root_cause(classified_data)

        # Step 3: Generate alternative (if appropriate)
        if report.remedy_action == RemedyAction.TRIGGER_ALTERNATIVE:
            self.recoveries_attempted += 1
            analysis_entry = {
                'analysis': analysis,
                'original_report': classified_data
            }
            plan_b = self.alternative_path_generator.generate_alternative(analysis_entry)
            report.alternative_plan = plan_b
            report.status = FailureStatus.ALTERNATIVE_GENERATED

        return {
            'report': {
                'failure_id': report.failure_id,
                'error_type': report.error_type.name,
                'remedy_action': report.remedy_action.name,
                'status': report.status.name,
                'failing_agent': report.failing_agent,
                'root_cause': analysis.get('root_cause'),
                'recommendation': analysis.get('recommended_action')
            },
            'recovery_plan': report.alternative_plan
        }

    def log_step(self, conversation_id: str, agent_id: str,
                operation: str, input_data: Any, success: bool = True):
        """
        Log an execution step for failure analysis

        Should be called by agents to enable root cause analysis.
        """
        step = ExecutionStep(
            step_id=str(uuid.uuid4())[:8],
            agent_id=agent_id,
            operation=operation,
            input_data=input_data,
            success=success
        )
        self.root_cause_analyzer.log_execution_step(conversation_id, step)

    def classify_error(self, error_message: str) -> Tuple[ErrorType, RemedyAction]:
        """Quick error classification without full pipeline"""
        return self.error_classifier._match_patterns(error_message, '')

    def get_statistics(self) -> Dict[str, Any]:
        """Get team statistics"""
        return {
            'failures_handled': self.failures_handled,
            'recoveries_attempted': self.recoveries_attempted,
            'error_classifier': self.error_classifier.get_statistics(),
            'root_cause_analyzer': self.root_cause_analyzer.get_statistics(),
            'alternative_path_generator': self.alternative_path_generator.get_statistics()
        }


# ===========================================================================
# MODULE TEST
# ===========================================================================

if __name__ == "__main__":
    """Test Failure Analysis Team"""
    print("=" * 80)
    print("PHASE 4 - STEP 2: FAILURE ANALYSIS TEAM TEST")
    print("=" * 80)
    print()

    # Initialize team
    team = FailureAnalysisTeam()
    print()

    # Test case 1: Timeout error (Computational)
    print("TEST 1: Timeout Error (Computational)")
    print("-" * 40)

    result = team.handle_failure({
        'error_message': 'Timeout exceeded: integration took > 30s',
        'agent_id': 'symbolic_integration_001',
        'step': 'risch_algorithm',
        'conversation_id': 'test_001'
    })

    print(f"  Classification: {result['report']['error_type']}")
    print(f"  Action: {result['report']['remedy_action']}")
    print()

    # Test case 2: Domain error (should generate alternative)
    print("TEST 2: Domain Error (Method Inapplicable)")
    print("-" * 40)

    result = team.handle_failure({
        'error_message': 'Cannot apply Risch algorithm: function not elementary',
        'agent_id': 'symbolic_integration_001',
        'step': 'symbolic_integration',
        'conversation_id': 'test_002'
    })

    print(f"  Classification: {result['report']['error_type']}")
    print(f"  Action: {result['report']['remedy_action']}")
    if result['recovery_plan']:
        print(f"  Recovery Plan: {result['recovery_plan']['strategies']}")
    print()

    # Test case 3: Logical error
    print("TEST 3: Logical Error (Invalid Inference)")
    print("-" * 40)

    result = team.handle_failure({
        'error_message': 'Assertion failed: step 3 does not follow from step 2',
        'agent_id': 'proof_agent_001',
        'step': 'direct_proof',
        'conversation_id': 'test_003'
    })

    print(f"  Classification: {result['report']['error_type']}")
    print(f"  Action: {result['report']['remedy_action']}")
    print()

    # Statistics
    print("TEAM STATISTICS:")
    import json
    print(json.dumps(team.get_statistics(), indent=2))
    print()

    print("=" * 80)
    print("FAILURE ANALYSIS TEAM TEST COMPLETE")
    print("=" * 80)
