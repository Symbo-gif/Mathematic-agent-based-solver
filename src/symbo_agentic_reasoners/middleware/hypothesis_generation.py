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
HYPOTHESIS GENERATION TEAM - "The Scouts"
==========================================

Phase 3: Meta-Cognitive Middleware - Search Gap Resolution

PURPOSE:
-------
Construct the strategic planning layer that implements Tree-of-Thoughts (ToT)
reasoning. This team explores the "solution space" to find the optimal path
before committing computational resources. Instead of blindly executing the
first valid approach, the system evaluates multiple strategies and selects
the most promising one.

WHY THIS MATTERS:
----------------
Standard agents are linear - they blindly follow the first path they see.
For complex proofs, this leads to dead ends and wasted compute. The
Hypothesis Generation Team enforces strategic thinking: proposing multiple
approaches, evaluating their "promise scores," and enabling graceful
backtracking when the chosen path fails.

AGENTS:
------
1. Hypothesis Generator - Creative strategist (proposes, never solves)
2. Path Evaluator - Heuristic judge (predicts success)
3. Backtracking Manager - State time travel (handles failure)

REFERENCE:
---------
- Phase_3_Build_Order_Breakdown.md: Step 3
- Phase_3_installs_the_cognitive_immune_system.md: Actions 3.1-3.3
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable, Set
from enum import Enum, auto
from datetime import datetime
import copy
import hashlib
import logging
import re

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    parse_expr, Symbol, Expr, Integer, Float, Rational,
    Add, Mul, Pow, Sin, Cos, Tan, Exp, Log, Sqrt
)

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase3.hypothesis.hypothesis_generation')
except ImportError:
    logger = logging.getLogger(__name__)


# ===========================================================================
# STRATEGY AND PLAN TYPES
# ===========================================================================

class StrategyType(Enum):
    """Types of mathematical proof/solution strategies"""
    # Proof strategies
    INDUCTION = "proof_by_induction"
    CONTRADICTION = "proof_by_contradiction"
    DIRECT = "direct_proof"
    CONSTRUCTION = "proof_by_construction"
    CONTRAPOSITIVE = "proof_by_contrapositive"
    EXHAUSTION = "proof_by_exhaustion"

    # Computation strategies
    ALGEBRAIC_MANIPULATION = "algebraic_manipulation"
    SUBSTITUTION = "substitution"
    FACTORING = "factoring"
    COMPLETING_SQUARE = "completing_the_square"

    # Integration strategies
    INTEGRATION_BY_PARTS = "integration_by_parts"
    PARTIAL_FRACTIONS = "partial_fractions"
    TRIG_SUBSTITUTION = "trigonometric_substitution"
    U_SUBSTITUTION = "u_substitution"

    # Fallback
    NUMERICAL_FALLBACK = "numerical_approximation"


class PlanStatus(Enum):
    """Status of a solution plan"""
    PROPOSED = auto()      # Just generated
    EVALUATING = auto()    # Being scored
    SELECTED = auto()      # Chosen for execution
    EXECUTING = auto()     # Currently running
    COMPLETED = auto()     # Finished successfully
    FAILED = auto()        # Execution failed
    ABANDONED = auto()     # Discarded in favor of alternative


@dataclass
class SolutionPlan:
    """
    A proposed solution strategy

    Represents a high-level approach to solving a problem.
    Does NOT contain the actual solution - only the strategy.
    """
    plan_id: str
    strategy: StrategyType
    description: str
    prerequisite_checks: List[str]
    estimated_complexity: str  # 'low', 'medium', 'high'
    promise_score: float = 0.0
    status: PlanStatus = PlanStatus.PROPOSED
    execution_trace: List[str] = field(default_factory=list)
    failure_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        return f"Plan[{self.strategy.value}](score={self.promise_score:.2f}, status={self.status.name})"


@dataclass
class BlackboardSnapshot:
    """
    Snapshot of Blackboard state for backtracking

    Captures the complete state of a problem-solving session
    at a specific point in time, enabling "time travel" on failure.
    """
    snapshot_id: str
    timestamp: datetime
    conversation_id: str
    state_data: Dict[str, Any]
    active_plan_id: Optional[str]


@dataclass
class TreeNode:
    """
    Node in the Tree-of-Thoughts structure

    Represents a single node in the exploration tree,
    linking plans to their parent strategies and children.
    """
    node_id: str
    plan: SolutionPlan
    parent_id: Optional[str]
    children: List[str] = field(default_factory=list)
    depth: int = 0
    is_terminal: bool = False
    terminal_success: bool = False


# ===========================================================================
# AGENT 3.1: THE HYPOTHESIS GENERATOR
# ===========================================================================

class HypothesisGeneratorAgent:
    """
    Agent 3.1: The Hypothesis Generator - Creative Strategist

    Proposes solution strategies WITHOUT solving. Strictly forbidden
    from executing calculations; its role is strategic planning only.

    WHAT IT DOES:
    - Analyzes problem structure
    - Generates applicable strategies
    - Creates detailed plan descriptions
    - Identifies prerequisites for each strategy

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 3.1
    """

    # Strategy templates for different problem types
    PROOF_STRATEGIES = [
        StrategyType.INDUCTION,
        StrategyType.CONTRADICTION,
        StrategyType.DIRECT,
        StrategyType.CONTRAPOSITIVE,
    ]

    COMPUTATION_STRATEGIES = [
        StrategyType.ALGEBRAIC_MANIPULATION,
        StrategyType.SUBSTITUTION,
        StrategyType.FACTORING,
        StrategyType.COMPLETING_SQUARE,
    ]

    INTEGRATION_STRATEGIES = [
        StrategyType.INTEGRATION_BY_PARTS,
        StrategyType.PARTIAL_FRACTIONS,
        StrategyType.TRIG_SUBSTITUTION,
        StrategyType.U_SUBSTITUTION,
    ]

    DIFFERENTIATION_STRATEGIES = [
        StrategyType.DIRECT,
        StrategyType.ALGEBRAIC_MANIPULATION,
    ]

    def __init__(self):
        self.plan_counter = 0
        self.hypotheses_generated = 0
        print("    [OK] Hypothesis Generator Agent initialized")

    def generate_hypotheses(self, omdoc_object,
                          problem_type: str,
                          constraints: Dict[str, Any] = None
                          ) -> List[SolutionPlan]:
        """
        Generate multiple solution strategies for a problem.

        This method NEVER solves; it only proposes approaches.
        """
        self.hypotheses_generated += 1
        strategies = self._select_applicable_strategies(
            omdoc_object, problem_type
        )

        plans = []
        for strategy in strategies:
            plan = self._create_plan(strategy, omdoc_object, problem_type)
            plans.append(plan)

        return plans

    def _select_applicable_strategies(self, omdoc_object,
                                     problem_type: str) -> List[StrategyType]:
        """Select strategies applicable to this problem type"""
        problem_type_lower = problem_type.lower()

        if 'proof' in problem_type_lower:
            return self.PROOF_STRATEGIES.copy()
        elif 'integration' in problem_type_lower or 'integral' in problem_type_lower:
            return self.INTEGRATION_STRATEGIES.copy()
        elif 'differentiation' in problem_type_lower or 'derivative' in problem_type_lower:
            return self.DIFFERENTIATION_STRATEGIES.copy()
        elif 'equation' in problem_type_lower or 'solve' in problem_type_lower:
            return self.COMPUTATION_STRATEGIES.copy()
        else:
            # Default: try algebraic manipulation + numerical fallback
            return [
                StrategyType.ALGEBRAIC_MANIPULATION,
                StrategyType.DIRECT,
                StrategyType.NUMERICAL_FALLBACK
            ]

    def _create_plan(self, strategy: StrategyType,
                    omdoc_object,
                    problem_type: str) -> SolutionPlan:
        """Create a detailed plan for a strategy"""
        self.plan_counter += 1
        plan_id = f"plan_{self.plan_counter:04d}"

        # Strategy-specific descriptions and prerequisites
        descriptions = {
            StrategyType.INDUCTION: {
                'desc': "Attempt proof by mathematical induction: "
                        "establish base case P(0) or P(1), then prove P(n) implies P(n+1)",
                'prereqs': ['has_natural_number_variable', 'recursive_structure'],
                'complexity': 'medium'
            },
            StrategyType.CONTRADICTION: {
                'desc': "Attempt proof by contradiction: "
                        "assume the negation, derive a logical inconsistency",
                'prereqs': ['statement_is_negatable'],
                'complexity': 'medium'
            },
            StrategyType.DIRECT: {
                'desc': "Attempt direct algebraic proof: "
                        "manipulate expressions step-by-step to reach conclusion",
                'prereqs': [],
                'complexity': 'low'
            },
            StrategyType.CONTRAPOSITIVE: {
                'desc': "Prove the contrapositive: if not Q then not P, "
                        "which is equivalent to if P then Q",
                'prereqs': ['implication_structure'],
                'complexity': 'medium'
            },
            StrategyType.ALGEBRAIC_MANIPULATION: {
                'desc': "Apply algebraic transformations: "
                        "simplify, expand, factor as needed",
                'prereqs': [],
                'complexity': 'low'
            },
            StrategyType.SUBSTITUTION: {
                'desc': "Apply variable substitution to simplify the expression",
                'prereqs': ['has_compound_expression'],
                'complexity': 'medium'
            },
            StrategyType.FACTORING: {
                'desc': "Factor the expression to find roots or simplify",
                'prereqs': ['polynomial_expression'],
                'complexity': 'low'
            },
            StrategyType.COMPLETING_SQUARE: {
                'desc': "Complete the square to solve quadratic or simplify",
                'prereqs': ['quadratic_expression'],
                'complexity': 'low'
            },
            StrategyType.INTEGRATION_BY_PARTS: {
                'desc': "Apply integration by parts: integral(u dv) = uv - integral(v du). "
                        "Select u and dv based on LIATE rule (Log, Inverse trig, Algebraic, Trig, Exp)",
                'prereqs': ['product_of_functions'],
                'complexity': 'medium'
            },
            StrategyType.PARTIAL_FRACTIONS: {
                'desc': "Decompose rational function into partial fractions, "
                        "then integrate each term separately",
                'prereqs': ['rational_function', 'factorable_denominator'],
                'complexity': 'medium'
            },
            StrategyType.TRIG_SUBSTITUTION: {
                'desc': "Apply trigonometric substitution for expressions "
                        "involving sqrt(a^2-x^2), sqrt(a^2+x^2), or sqrt(x^2-a^2)",
                'prereqs': ['has_radical_form'],
                'complexity': 'high'
            },
            StrategyType.U_SUBSTITUTION: {
                'desc': "Apply u-substitution to simplify the integral. "
                        "Identify inner function u and check if du is present",
                'prereqs': ['has_composite_function'],
                'complexity': 'low'
            },
            StrategyType.NUMERICAL_FALLBACK: {
                'desc': "Fall back to numerical approximation methods "
                        "when symbolic methods fail or are intractable",
                'prereqs': [],
                'complexity': 'low'
            },
        }

        info = descriptions.get(strategy, {
            'desc': f"Apply {strategy.value} strategy",
            'prereqs': [],
            'complexity': 'medium'
        })

        return SolutionPlan(
            plan_id=plan_id,
            strategy=strategy,
            description=info['desc'],
            prerequisite_checks=info['prereqs'],
            estimated_complexity=info['complexity']
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'hypotheses_generated': self.hypotheses_generated,
            'plans_created': self.plan_counter
        }


# ===========================================================================
# AGENT 3.2: THE PATH EVALUATOR
# ===========================================================================

class PathEvaluatorAgent:
    """
    Agent 3.2: The Path Evaluator - Heuristic Judge

    Estimates the "Promise Score" of proposed plans without executing them.
    Analyzes problem structure to predict which strategy is most likely
    to succeed.

    WHAT IT DOES:
    - Extracts structural features from problems
    - Computes promise scores based on heuristics
    - Ranks plans by expected success
    - Penalizes plans with unmet prerequisites

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 3.2
    """

    def __init__(self):
        # Heuristic weights learned from historical performance
        self.strategy_base_scores = {
            StrategyType.INDUCTION: 0.7,
            StrategyType.CONTRADICTION: 0.5,
            StrategyType.DIRECT: 0.8,
            StrategyType.CONTRAPOSITIVE: 0.6,
            StrategyType.ALGEBRAIC_MANIPULATION: 0.85,
            StrategyType.SUBSTITUTION: 0.75,
            StrategyType.FACTORING: 0.8,
            StrategyType.COMPLETING_SQUARE: 0.75,
            StrategyType.INTEGRATION_BY_PARTS: 0.7,
            StrategyType.PARTIAL_FRACTIONS: 0.8,
            StrategyType.TRIG_SUBSTITUTION: 0.6,
            StrategyType.U_SUBSTITUTION: 0.85,
            StrategyType.NUMERICAL_FALLBACK: 0.95,  # Always works, but less desirable
        }

        # Problem features that boost certain strategies
        self.feature_bonuses = {
            'recursive_structure': {StrategyType.INDUCTION: 0.2},
            'has_natural_number_variable': {StrategyType.INDUCTION: 0.15},
            'product_of_functions': {StrategyType.INTEGRATION_BY_PARTS: 0.2},
            'rational_function': {StrategyType.PARTIAL_FRACTIONS: 0.25},
            'has_radical_form': {StrategyType.TRIG_SUBSTITUTION: 0.2},
            'polynomial_expression': {StrategyType.DIRECT: 0.1, StrategyType.FACTORING: 0.15},
            'quadratic_expression': {StrategyType.COMPLETING_SQUARE: 0.2, StrategyType.FACTORING: 0.1},
            'has_composite_function': {StrategyType.U_SUBSTITUTION: 0.25},
        }

        self.evaluations_performed = 0
        print("    [OK] Path Evaluator Agent initialized")

    def evaluate_plans(self, plans: List[SolutionPlan],
                      omdoc_object,
                      problem_features: Dict[str, bool] = None
                      ) -> List[SolutionPlan]:
        """
        Evaluate and rank plans by promise score.

        Returns plans sorted by promise score (highest first).
        """
        self.evaluations_performed += 1
        features = problem_features or self._extract_features(omdoc_object)

        for plan in plans:
            plan.promise_score = self._compute_promise_score(plan, features)
            plan.status = PlanStatus.EVALUATING

        # Sort by promise score descending
        plans.sort(key=lambda p: p.promise_score, reverse=True)

        return plans

    def _extract_features(self, omdoc_object) -> Dict[str, bool]:
        """Extract structural features from the problem - NO SYMPY"""
        features = {}
        expr = self._get_expression(omdoc_object)
        expr_str = str(expr)

        # Check for recursive/inductive structure
        features['recursive_structure'] = self._has_recursive_structure(expr)

        # Check for natural number variables
        features['has_natural_number_variable'] = self._has_natural_variable(omdoc_object)

        # Check for product of functions (for integration by parts)
        features['product_of_functions'] = self._has_product_structure_native(expr_str)

        # Check for rational function
        features['rational_function'] = self._is_rational_function_native(expr_str)

        # Check for radical forms
        features['has_radical_form'] = self._has_radical_form_native(expr_str)

        # Check for polynomial
        features['polynomial_expression'] = self._is_polynomial_native(expr_str)

        # Check for quadratic
        features['quadratic_expression'] = self._is_quadratic_native(expr_str)

        # Check for composite function
        features['has_composite_function'] = self._has_composite_function_native(expr_str)

        return features

    def _get_expression(self, omdoc_object) -> Any:
        """Extract expression from OMDoc object"""
        if hasattr(omdoc_object, 'expression_tree'):
            return omdoc_object.expression_tree
        elif hasattr(omdoc_object, 'expression'):
            return omdoc_object.expression
        elif hasattr(omdoc_object, 'content'):
            return omdoc_object.content
        return omdoc_object

    def _compute_promise_score(self, plan: SolutionPlan,
                              features: Dict[str, bool]) -> float:
        """Compute promise score for a plan given problem features"""
        # Start with base score
        score = self.strategy_base_scores.get(plan.strategy, 0.5)

        # Apply feature bonuses
        for feature, is_present in features.items():
            if is_present and feature in self.feature_bonuses:
                bonus = self.feature_bonuses[feature].get(plan.strategy, 0)
                score += bonus

        # Penalize for unmet prerequisites
        for prereq in plan.prerequisite_checks:
            if prereq in features and not features[prereq]:
                score -= 0.15

        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))

    def _has_recursive_structure(self, expr) -> bool:
        """Check if expression has recursive/inductive structure"""
        expr_str = str(expr)
        patterns = ['(n-1)', '(n+1)', 'factorial', 'fib', 'sum_', 'prod_']
        return any(p in expr_str for p in patterns)

    def _has_natural_variable(self, omdoc_object) -> bool:
        """Check for natural number domain variable"""
        metadata = getattr(omdoc_object, 'metadata', {})
        if isinstance(metadata, dict):
            constraints = metadata.get('constraints', [])
            for c in constraints:
                if hasattr(c, 'constraint_type') and c.constraint_type == 'integer':
                    return True
        return False

    def _has_product_structure_native(self, expr_str: str) -> bool:
        """Check for product of distinct function types using pattern matching - NO SYMPY"""
        try:
            # Check if expression contains multiple multiplied terms
            # e.g., x*sin(x), x*exp(x), etc.
            has_var = re.search(r'\b[a-z]\b', expr_str)
            has_func = re.search(r'\b(sin|cos|tan|exp|log|ln)\s*\(', expr_str, re.IGNORECASE)
            has_multiply = '*' in expr_str or (has_var and has_func)
            return has_multiply and has_func is not None
        except Exception as e:
            logger.debug(f"Could not check product structure: {e}")
            return False

    def _has_product_structure(self, expr) -> bool:
        """Wrapper for backward compatibility"""
        return self._has_product_structure_native(str(expr))

    def _is_rational_function_native(self, expr_str: str) -> bool:
        """Check if expression is a rational function using pattern matching - NO SYMPY"""
        try:
            # Check for division or negative exponents
            return '/' in expr_str or '**-' in expr_str
        except Exception as e:
            logger.debug(f"Could not check rational function: {e}")
            return False

    def _is_rational_function(self, expr) -> bool:
        """Wrapper for backward compatibility"""
        return self._is_rational_function_native(str(expr))

    def _has_radical_form_native(self, expr_str: str) -> bool:
        """Check for square root patterns using pattern matching - NO SYMPY"""
        try:
            return 'sqrt' in expr_str.lower() or '**0.5' in expr_str or '**(1/2)' in expr_str
        except Exception as e:
            logger.debug(f"Could not check radical form: {e}")
            return False

    def _has_radical_form(self, expr) -> bool:
        """Wrapper for backward compatibility"""
        return self._has_radical_form_native(str(expr))

    def _is_polynomial_native(self, expr_str: str) -> bool:
        """Check if expression is a polynomial using pattern matching - NO SYMPY"""
        try:
            # Polynomials contain only: variables, +, -, *, **, numbers
            # No functions like sin, cos, exp, log, sqrt
            has_transcendental = re.search(r'\b(sin|cos|tan|exp|log|ln|sqrt)\s*\(', expr_str, re.IGNORECASE)
            return not has_transcendental and not '/' in expr_str
        except Exception as e:
            logger.debug(f"Could not check polynomial: {e}")
            return False

    def _is_polynomial(self, expr) -> bool:
        """Wrapper for backward compatibility"""
        return self._is_polynomial_native(str(expr))

    def _is_quadratic_native(self, expr_str: str) -> bool:
        """Check if expression is quadratic using pattern matching - NO SYMPY"""
        try:
            # Check for x**2 or x^2 pattern and no higher powers
            has_square = re.search(r'\b[a-z]\s*\*\*\s*2\b', expr_str) or re.search(r'\b[a-z]\s*\^\s*2\b', expr_str)
            has_higher = re.search(r'\b[a-z]\s*\*\*\s*[3-9]\b', expr_str) or re.search(r'\b[a-z]\s*\^\s*[3-9]\b', expr_str)
            return has_square is not None and not has_higher
        except Exception as e:
            logger.debug(f"Could not check quadratic: {e}")
            return False

    def _is_quadratic(self, expr) -> bool:
        """Wrapper for backward compatibility"""
        return self._is_quadratic_native(str(expr))

    def _has_composite_function_native(self, expr_str: str) -> bool:
        """Check for composite function structure using pattern matching - NO SYMPY"""
        try:
            # Check for nested functions: sin(x**2), exp(sin(x)), etc.
            funcs = ['sin', 'cos', 'tan', 'exp', 'log', 'ln', 'sqrt']
            for func in funcs:
                # Check if function contains something other than just a simple variable
                pattern = rf'\b{func}\s*\(\s*([^)]+)\s*\)'
                match = re.search(pattern, expr_str, re.IGNORECASE)
                if match:
                    inner = match.group(1)
                    # If inner contains operators or other functions, it's composite
                    if any(op in inner for op in ['+', '-', '*', '/', '**', '^']) or \
                       any(f in inner.lower() for f in funcs):
                        return True
            return False
        except Exception as e:
            logger.debug(f"Could not check composite function: {e}")
            return False

    def _has_composite_function(self, expr) -> bool:
        """Wrapper for backward compatibility"""
        return self._has_composite_function_native(str(expr))

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'evaluations_performed': self.evaluations_performed
        }


# ===========================================================================
# AGENT 3.3: THE BACKTRACKING MANAGER
# ===========================================================================

class BacktrackingManagerAgent:
    """
    Agent 3.3: The Backtracking Manager - State Time Travel

    Manages Blackboard state snapshots and enables recovery from
    failed solution attempts. Implements "Time Travel" for the system.

    WHAT IT DOES:
    - Creates snapshots before plan execution
    - Restores state on failure
    - Manages alternative plan selection
    - Clears session data on completion

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Agent 3.3
    """

    def __init__(self, blackboard):
        """
        Initialize with Blackboard reference for state management.

        Args:
            blackboard: Phase 0 Blackboard instance
        """
        self.blackboard = blackboard
        self.snapshots: Dict[str, BlackboardSnapshot] = {}
        self.snapshot_stack: Dict[str, List[str]] = {}  # conversation_id -> [snapshot_ids]
        self.snapshots_created = 0
        self.restorations_performed = 0
        print("    [OK] Backtracking Manager Agent initialized")

    def create_snapshot(self, conversation_id: str,
                       plan_id: str) -> str:
        """
        Create a snapshot of current Blackboard state before plan execution.

        Called by Orchestrator before delegating to solvers.
        """
        snapshot_id = self._generate_snapshot_id(conversation_id)

        # Capture current Blackboard state
        state_data = self._capture_state(conversation_id)

        snapshot = BlackboardSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            conversation_id=conversation_id,
            state_data=copy.deepcopy(state_data),
            active_plan_id=plan_id
        )

        self.snapshots[snapshot_id] = snapshot

        # Push to conversation stack
        if conversation_id not in self.snapshot_stack:
            self.snapshot_stack[conversation_id] = []
        self.snapshot_stack[conversation_id].append(snapshot_id)

        self.snapshots_created += 1
        return snapshot_id

    def _capture_state(self, conversation_id: str) -> Dict[str, Any]:
        """Capture current Blackboard state for a conversation"""
        try:
            if hasattr(self.blackboard, 'get_full_state'):
                return self.blackboard.get_full_state(conversation_id)
            elif hasattr(self.blackboard, 'get_entries'):
                entries = self.blackboard.get_entries(conversation_id)
                return {'entries': entries}
            elif hasattr(self.blackboard, 'get_by_conversation'):
                entries = self.blackboard.get_by_conversation(conversation_id)
                return {'entries': [e for e in entries]}
        except (AttributeError, TypeError, KeyError) as e:
            logger.debug(f"Could not capture blackboard state for {conversation_id}: {e}")
        return {}

    def restore_snapshot(self, conversation_id: str,
                        snapshot_id: str = None) -> bool:
        """
        Restore Blackboard to a previous snapshot state.

        If snapshot_id is None, restores to most recent snapshot.
        This is the "Time Travel" operation.
        """
        # Get target snapshot
        if snapshot_id is None:
            stack = self.snapshot_stack.get(conversation_id, [])
            if not stack:
                return False
            snapshot_id = stack[-1]

        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            return False

        # Restore Blackboard state
        try:
            if hasattr(self.blackboard, 'restore_state'):
                self.blackboard.restore_state(conversation_id, snapshot.state_data)
            # Otherwise, restoration is not supported - just track the snapshot
        except (AttributeError, TypeError, ValueError) as e:
            logger.debug(f"Could not restore blackboard state for {conversation_id}: {e}")

        # Pop snapshots after this one
        stack = self.snapshot_stack.get(conversation_id, [])
        if snapshot_id in stack:
            idx = stack.index(snapshot_id)
            # Remove this and all later snapshots
            removed = stack[idx:]
            self.snapshot_stack[conversation_id] = stack[:idx]
            for sid in removed:
                if sid in self.snapshots:
                    del self.snapshots[sid]

        self.restorations_performed += 1
        return True

    def handle_plan_failure(self, conversation_id: str,
                           failed_plan: SolutionPlan,
                           alternative_plans: List[SolutionPlan]
                           ) -> Optional[SolutionPlan]:
        """
        Handle a failed plan by restoring state and selecting alternative.

        Returns the next plan to try, or None if no alternatives remain.
        """
        # Record failure
        failed_plan.status = PlanStatus.FAILED

        # Restore to pre-execution state
        success = self.restore_snapshot(conversation_id)
        if not success:
            # Even if restore fails, we can still try alternatives
            pass

        # Find next untried plan
        for plan in alternative_plans:
            if plan.status == PlanStatus.PROPOSED:
                plan.status = PlanStatus.SELECTED
                return plan

        return None  # All plans exhausted

    def _generate_snapshot_id(self, conversation_id: str) -> str:
        """Generate unique snapshot ID"""
        content = f"{conversation_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def clear_session(self, conversation_id: str) -> None:
        """Clear all snapshots for a completed session"""
        stack = self.snapshot_stack.get(conversation_id, [])
        for snapshot_id in stack:
            if snapshot_id in self.snapshots:
                del self.snapshots[snapshot_id]
        if conversation_id in self.snapshot_stack:
            del self.snapshot_stack[conversation_id]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'snapshots_created': self.snapshots_created,
            'restorations_performed': self.restorations_performed,
            'active_snapshots': len(self.snapshots),
            'active_sessions': len(self.snapshot_stack)
        }


# ===========================================================================
# HYPOTHESIS GENERATION TEAM COORDINATOR
# ===========================================================================

class HypothesisGenerationTeam:
    """
    Coordinator for the Hypothesis Generation Team.

    Implements Tree-of-Thoughts reasoning by coordinating hypothesis
    generation, evaluation, and backtracking.

    KEY PROTOCOLS:
    - scout(): Generate, evaluate, and select best strategy
    - handle_failure(): Backtrack and try alternative
    - clear_session(): Clean up after problem completion

    REFERENCE:
    ---------
    Phase_3_Build_Order_Breakdown.md: Team Coordinator
    """

    def __init__(self, blackboard):
        """
        Initialize the Hypothesis Generation Team.

        Args:
            blackboard: Phase 0 Blackboard for state management
        """
        print("  [HYPOTHESIS GENERATION TEAM - The Scouts]")
        self.hypothesis_generator = HypothesisGeneratorAgent()
        self.path_evaluator = PathEvaluatorAgent()
        self.backtracking_manager = BacktrackingManagerAgent(blackboard)

        # Tree structure for complex problems
        self.thought_trees: Dict[str, Dict[str, Any]] = {}
        print("    [OK] Hypothesis Generation Team assembled")

    def scout(self, omdoc_object,
             conversation_id: str,
             problem_type: str) -> Optional[SolutionPlan]:
        """
        The "Scouting" protocol for high-complexity problems.

        Generates hypotheses, evaluates them, and returns the best plan.
        Creates snapshot before execution begins.
        """
        # Step 1: Generate hypotheses
        plans = self.hypothesis_generator.generate_hypotheses(
            omdoc_object, problem_type
        )

        if not plans:
            return None

        # Step 2: Evaluate and rank
        ranked_plans = self.path_evaluator.evaluate_plans(
            plans, omdoc_object
        )

        # Step 3: Select best plan
        best_plan = ranked_plans[0]
        best_plan.status = PlanStatus.SELECTED

        # Step 4: Create snapshot before execution
        self.backtracking_manager.create_snapshot(
            conversation_id, best_plan.plan_id
        )

        # Store alternative plans for potential backtracking
        self._store_alternatives(conversation_id, ranked_plans[1:])

        return best_plan

    def handle_failure(self, conversation_id: str,
                      failed_plan: SolutionPlan) -> Optional[SolutionPlan]:
        """
        Handle plan failure and attempt backtracking to alternative.
        """
        alternatives = self._get_alternatives(conversation_id)
        return self.backtracking_manager.handle_plan_failure(
            conversation_id, failed_plan, alternatives
        )

    def _store_alternatives(self, conversation_id: str,
                           plans: List[SolutionPlan]) -> None:
        """Store alternative plans for backtracking"""
        if conversation_id not in self.thought_trees:
            self.thought_trees[conversation_id] = {}
        self.thought_trees[conversation_id]['alternatives'] = plans

    def _get_alternatives(self, conversation_id: str) -> List[SolutionPlan]:
        """Retrieve stored alternative plans"""
        tree_data = self.thought_trees.get(conversation_id, {})
        return tree_data.get('alternatives', [])

    def clear_session(self, conversation_id: str) -> None:
        """Clear session data after problem completion"""
        if conversation_id in self.thought_trees:
            del self.thought_trees[conversation_id]
        self.backtracking_manager.clear_session(conversation_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Get team statistics"""
        return {
            'hypothesis_generator': self.hypothesis_generator.get_statistics(),
            'path_evaluator': self.path_evaluator.get_statistics(),
            'backtracking_manager': self.backtracking_manager.get_statistics()
        }
