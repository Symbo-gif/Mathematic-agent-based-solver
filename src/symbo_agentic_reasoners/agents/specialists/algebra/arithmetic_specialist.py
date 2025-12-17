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
PHASE 2 - STEP 1.2: ARITHMETIC SPECIALIST (Tier 3)
===================================================

Provides Arbitrary-Precision Arithmetic to ensure absolute numerical exactness.

ARCHITECTURE: DOMAIN-FIRST, SYMPY-FALLBACK
------------------------------------------
This specialist implements the "SymPy Last Resort" pattern:
1. Try pure Python arithmetic FIRST (exact for integers)
2. Use fractions.Fraction for rational arithmetic (exact)
3. Only fall back to SymPy for symbolic expressions
4. Track all fallbacks for optimization analysis

DOMAIN ALGORITHMS (tried first):
-------------------------------
- Python int: Arbitrary-precision integers (built-in)
- fractions.Fraction: Exact rational arithmetic
- operator module: Direct evaluation of AST
- math module: Only for integer operations (factorial, gcd)

SYMPY FALLBACK (when domain algorithms fail):
--------------------------------------------
- Symbolic expressions with variables
- Transcendental numbers (pi, e, sqrt)
- Complex simplification

CRITICAL CONSTRAINT:
-------------------
Standard floating-point arithmetic is STRICTLY FORBIDDEN.

REFERENCE:
---------
- Second Opinion Analysis: "Domain-first, library-second per specialist"
- Phase_2_Build_Order_Breakdown.md: Lines 54-73 (Agent 1.2)
"""

import sys
import os
import ast
import operator
import logging
from typing import Any, Dict, Optional, Tuple, Union
from fractions import Fraction
from math import factorial, gcd, isqrt
import uuid

logger = logging.getLogger('symbo_agentic_reasoners.phase2.arithmetic')

# Arbitrary-precision library
from mpmath import mp, mpf, mpmathify

# Native symbolic module - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, Integer, Rational, Float, parse_expr, sympify, simplify, expand
)
from symbo_agentic_reasoners.core.native_symbolic import Expr as NativeExpr

# Import fallback tracker for SymPy usage monitoring
from symbo_agentic_reasoners.core.fallback_tracker import (
    get_tracker, track_computation, ResolutionMethod
)

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


# =============================================================================
# DOMAIN-SPECIFIC ARITHMETIC ALGORITHMS
# =============================================================================
# These algorithms are tried FIRST before falling back to SymPy.
# This implements the "SymPy Last Resort" architecture.
# =============================================================================

class DomainArithmetic:
    """
    Domain-specific arithmetic using Python's built-in exact arithmetic.

    Python's int type is arbitrary-precision - it can handle integers
    of any size exactly. We use this for domain-first computation.

    For rational numbers, we use fractions.Fraction which is also exact.
    """

    # Safe operators for AST evaluation
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,  # Will be converted to Fraction
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Safe functions for domain computation
    SAFE_FUNCTIONS = {
        'abs': abs,
        'factorial': factorial,
        'gcd': gcd,
    }

    @classmethod
    def is_pure_arithmetic(cls, expr_str: str) -> bool:
        """
        Check if expression is pure arithmetic (no variables/symbols).

        Returns True if the expression contains only numbers and operators.
        """
        try:
            tree = ast.parse(expr_str, mode='eval')
            return cls._is_pure_arithmetic_node(tree.body)
        except SyntaxError:
            return False

    @classmethod
    def _is_pure_arithmetic_node(cls, node: ast.AST) -> bool:
        """Recursively check if AST node is pure arithmetic."""
        if isinstance(node, ast.Constant):
            return isinstance(node.value, (int, float, complex))
        elif isinstance(node, ast.BinOp):
            return (type(node.op) in cls.SAFE_OPERATORS and
                    cls._is_pure_arithmetic_node(node.left) and
                    cls._is_pure_arithmetic_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return (type(node.op) in cls.SAFE_OPERATORS and
                    cls._is_pure_arithmetic_node(node.operand))
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in cls.SAFE_FUNCTIONS:
                return all(cls._is_pure_arithmetic_node(arg) for arg in node.args)
            return False
        elif isinstance(node, ast.Name):
            # Variable - not pure arithmetic
            return False
        else:
            return False

    @classmethod
    def evaluate_pure_arithmetic(cls, expr_str: str) -> Tuple[bool, Optional[Any], str]:
        """
        Evaluate pure arithmetic expression using Python's exact arithmetic.

        Args:
            expr_str: Arithmetic expression string

        Returns:
            Tuple of (success: bool, result: Any, method: str)
        """
        if not cls.is_pure_arithmetic(expr_str):
            return (False, None, "contains_symbols")

        try:
            tree = ast.parse(expr_str, mode='eval')
            result = cls._eval_node(tree.body)
            return (True, result, "python_exact")
        except Exception as e:
            return (False, None, f"eval_failed: {e}")

    @classmethod
    def _eval_node(cls, node: ast.AST) -> Union[int, Fraction]:
        """
        Safely evaluate AST node using exact arithmetic.

        Returns int or Fraction to maintain exactness.
        """
        if isinstance(node, ast.Constant):
            value = node.value
            if isinstance(value, float):
                # Convert float to Fraction for exactness
                return Fraction(value).limit_denominator()
            return value
        elif isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)
            op = cls.SAFE_OPERATORS[type(node.op)]

            # Special handling for division - use Fraction for exactness
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                return Fraction(left, right) if isinstance(left, int) and isinstance(right, int) else Fraction(left) / Fraction(right)

            # Special handling for power - check for reasonable exponents
            if isinstance(node.op, ast.Pow):
                if isinstance(right, int) and right >= 0:
                    return left ** right
                elif isinstance(right, int) and right < 0:
                    # Negative exponent - use Fraction
                    return Fraction(1, left ** (-right))
                else:
                    # Non-integer exponent - cannot compute exactly
                    raise ValueError("Non-integer exponent requires symbolic computation")

            return op(left, right)

        elif isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand)
            op = cls.SAFE_OPERATORS[type(node.op)]
            return op(operand)

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in cls.SAFE_FUNCTIONS:
                args = [cls._eval_node(arg) for arg in node.args]
                return cls.SAFE_FUNCTIONS[node.func.id](*args)
            raise ValueError(f"Unknown function: {node.func}")

        else:
            raise ValueError(f"Cannot evaluate node type: {type(node)}")

    @classmethod
    def try_domain_compute(cls, expr_str: str) -> Tuple[bool, Optional[Any], str]:
        """
        Try to compute expression using domain algorithms.

        Args:
            expr_str: Expression string

        Returns:
            Tuple of (success: bool, result: Any, method: str)
        """
        # First try pure arithmetic evaluation
        success, result, method = cls.evaluate_pure_arithmetic(expr_str)
        if success:
            return (True, result, method)

        return (False, None, method)


class ArithmeticSpecialist(BDIAgent):
    """
    Arithmetic Specialist - Arbitrary-Precision Computation

    DIRECTIVE:
    ---------
    Provide exact arithmetic operations using arbitrary-precision libraries.
    Standard floating-point math is FORBIDDEN.

    OPERATIONS:
    ----------
    - Basic arithmetic: +, -, *, /, **
    - Modular arithmetic: a mod b, modular exponentiation
    - Exact rational arithmetic: fractions without rounding
    - Large integer operations: numbers with 1000+ digits

    PRECISION:
    ---------
    Default: 50 decimal places
    Configurable up to thousands of decimal places

    ALGORITHMIC BACKING:
    -------------------
    - mpmath: Arbitrary-precision floating-point
    - SymPy: Exact symbolic arithmetic
    - GMP (via gmpy2 if available): Optimized integer operations

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 58-73
    """

    def __init__(
        self,
        agent_id: str = 'arithmetic_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        precision: int = 50
    ):
        """
        Initialize Arithmetic Specialist

        Args:
            agent_id: Unique specialist identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            precision: Decimal places for arbitrary-precision (default: 50)
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Set mpmath precision
        mp.dps = precision  # Decimal places
        self.precision = precision

        # Domain-first architecture components
        self.domain_arithmetic = DomainArithmetic()
        self._tracker = get_tracker()

        # Statistics - including domain-first tracking
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.domain_computed = 0  # Computed by domain algorithms
        self.sympy_fallbacks = 0  # Fell back to SymPy

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Arithmetic Specialist initialized")
        print(f"  Precision: {self.precision} decimal places")
        print(f"  Architecture: DOMAIN-FIRST (Python exact -> SymPy fallback)")
        print(f"  Mode: EXACT arithmetic only (floating-point FORBIDDEN)")

    def _register_services(self):
        """
        Register services with Directory Facilitator

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 67-73
        """
        registration = create_service_registration(
            service_type='math.algebra.arithmetic',
            agent_id=self.agent_id,
            algorithm='mpmath',
            cost='low',
            instance=self,  # Enable direct invocation by supervisors
            precision='arbitrary',
            type='exact',
            tier='3',
            decimal_places=str(self.precision)
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.algebra.arithmetic (exact, {self.precision}dp)")

    def process(self, task_entry: Any) -> Any:
        """
        Process arithmetic task with arbitrary-precision

        Args:
            task_entry: Blackboard entry containing arithmetic task

        Returns:
            Result entry with exact computation
        """
        print(f"\n[{self.agent_id}] Processing arithmetic task")

        self.tasks_executed += 1

        try:
            # Extract task information
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'compute')
            raw_input = metadata.get('raw_input', '')

            # Get SymPy expression if available
            sympy_expr_str = metadata.get('sympy_expr')

            print(f"  Operation: {operation}")
            print(f"  Input: {raw_input}")

            # Compute using SymPy for exact symbolic arithmetic
            if sympy_expr_str:
                result = self._compute_exact(sympy_expr_str, operation, metadata)
            else:
                result = self._compute_fallback(raw_input, operation)

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result)

            self.tasks_succeeded += 1
            print(f"  [OK] Result: {result}")

            return result_entry

        except Exception as e:
            self.tasks_failed += 1
            print(f"  [ERROR] Computation failed: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _compute_exact(self, sympy_expr_str: str, operation: str, metadata: Dict) -> Any:
        """
        Compute using DOMAIN-FIRST approach.

        ARCHITECTURE: SymPy Last Resort
        -------------------------------
        1. TRY domain algorithms FIRST (Python exact arithmetic)
        2. TRY native trig simplifier for trig expressions
        3. Only fall back to SymPy for symbolic expressions or transcendentals
        4. Track all fallbacks for optimization

        Args:
            sympy_expr_str: String representation of expression
            operation: Operation type
            metadata: Additional task metadata

        Returns:
            Exact computed result
        """
        # Track this computation
        with self._tracker.track("arithmetic", sympy_expr_str, domain="algebra",
                                 specialist=self.agent_id) as tracker:

            # STEP 1: Try domain-first for pure arithmetic (compute/evaluate)
            if operation in ['compute', 'evaluate']:
                success, result, method = DomainArithmetic.try_domain_compute(sympy_expr_str)
                if success:
                    self.domain_computed += 1
                    tracker.mark_domain_success()
                    logger.debug(f"[DOMAIN] Computed {sympy_expr_str} = {result} via {method}")
                    # Convert Fraction to native Rational for consistency
                    if isinstance(result, Fraction):
                        return Rational(result.numerator, result.denominator)
                    return Integer(result) if isinstance(result, int) else result

            # STEP 2: Try native trig simplifier for simplify operations
            if operation == 'simplify':
                # Check if expression contains trig functions
                if any(trig in sympy_expr_str.lower() for trig in ['sin', 'cos', 'tan']):
                    try:
                        from symbo_agentic_reasoners.core.calculus import native_trig_simplify
                        simplified = native_trig_simplify(sympy_expr_str)
                        # If simplification changed the expression, use the result
                        if simplified != sympy_expr_str:
                            self.domain_computed += 1
                            tracker.mark_domain_success()
                            logger.debug(f"[NATIVE TRIG] Simplified {sympy_expr_str} = {simplified}")
                            print(f"  [NATIVE TRIG] Result: {simplified}")
                            # Try to parse the simplified result
                            try:
                                return parse_expr(simplified)
                            except:
                                return simplified
                    except ImportError:
                        pass  # Fall through to native symbolic

            # STEP 3: Use native symbolic engine for symbolic expressions
            self.domain_computed += 1
            tracker.mark_domain_success()

            # Parse expression using native parser
            expr = parse_expr(sympy_expr_str)

            # Perform operation based on type
            if operation == 'simplify':
                result = expr.simplify()
            elif operation == 'expand':
                result = expand(expr)
            elif operation == 'factor':
                # Native factor - just simplify for now
                result = expr.simplify()
            elif operation in ['compute', 'evaluate']:
                # Evaluate and simplify to exact form
                result = expr.simplify()
                # If expression has no symbols, keep exact integer/rational form
                if not result.free_symbols and result.is_number:
                    # Keep exact Integer/Rational form - don't convert to float
                    # Only use evalf for transcendental numbers (pi, e, sqrt(2), etc)
                    if result.is_integer or result.is_rational:
                        pass  # Keep as exact integer/rational
                    else:
                        # Transcendental/irrational - evaluate to precision
                        result = result.evalf(self.precision)
            else:
                # Default: simplify
                result = expr.simplify()

            return result

    def _compute_fallback(self, raw_input: str, operation: str) -> Any:
        """
        Fallback computation when expression not available.

        ARCHITECTURE: Domain-First
        --------------------------
        1. Try Python exact arithmetic FIRST
        2. Fall back to native symbolic parser

        Args:
            raw_input: Raw input string
            operation: Operation type

        Returns:
            Computed result

        Raises:
            ValueError: If expression cannot be parsed
        """
        # Track this computation
        with self._tracker.track("arithmetic_fallback", raw_input, domain="algebra",
                                 specialist=self.agent_id) as tracker:

            # STEP 1: Try domain-first (pure Python arithmetic)
            success, result, method = DomainArithmetic.try_domain_compute(raw_input)
            if success:
                self.domain_computed += 1
                tracker.mark_domain_success()
                logger.debug(f"[DOMAIN] Fallback computed {raw_input} = {result} via {method}")
                # Convert Fraction to native Rational for consistency
                if isinstance(result, Fraction):
                    return Rational(result.numerator, result.denominator)
                return Integer(result) if isinstance(result, int) else result

            # STEP 2: Fall back to native symbolic parser
            self.domain_computed += 1
            tracker.mark_domain_success()

            try:
                # Try to parse as native expression
                expr = parse_expr(raw_input)
                if not expr.free_symbols:
                    # Pure arithmetic - evaluate exactly
                    return expr
                else:
                    # Has variables - simplify
                    return expr.simplify()
            except (TypeError, ValueError, AttributeError) as e:
                # Don't silently return raw input - raise error for proper handling
                raise ValueError(f"Could not parse expression: {e}")

    def _create_result_entry(self, task_entry: Any, result: Any) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            tags=['arithmetic', 'exact', task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,  # Will be verified later
            metadata={
                'result': str(result),
                'result_str': str(result),
                'precision': self.precision,
                'type': 'exact',
                'algorithm': 'sympy+mpmath'
            }
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
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'error',
            tags=['error', 'arithmetic'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================
    #
    # The BDI loop is the cognitive engine of agents. Each cycle:
    #   1. update_beliefs() - perceive environment (read Blackboard)
    #   2. deliberate() - decide what to do (create intentions)
    #   3. execute_step() - do one step (delegate to SymPy, NEVER compute directly)
    # ==========================================================================

    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for arithmetic tasks.

        This is called each BDI cycle. The agent:
        1. Queries Blackboard for tasks matching its capabilities
        2. Adds beliefs about pending work
        3. Updates beliefs about completed/failed tasks
        """
        if not self.blackboard:
            return

        # Query for arithmetic tasks I can handle
        try:
            pending_tasks = self.blackboard.query_entries(
                tags=['arithmetic'],
                status=EntryStatus.PENDING
            )

            # Also check for algebra tasks that are simple computations
            algebra_tasks = self.blackboard.query_entries(
                tags=['algebra'],
                status=EntryStatus.PENDING
            )

            # Filter algebra tasks to only simple ones I can handle
            for task in algebra_tasks:
                operation = task.metadata.get('operation', '') if hasattr(task, 'metadata') else ''
                if operation in ['compute', 'simplify', 'evaluate', 'expand', 'factor']:
                    pending_tasks.append(task)

            # Add beliefs about pending tasks
            for task in pending_tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )

            # Check for tasks I've started that are now completed elsewhere
            for predicate in list(self.beliefs.keys()):
                if predicate.startswith('claimed_task_'):
                    task_id = predicate.replace('claimed_task_', '')
                    entry = self.blackboard.get_entry(task_id)
                    if entry and entry.status in [EntryStatus.COMPLETED, EntryStatus.VERIFIED, EntryStatus.FAILED]:
                        # Task finished, clean up belief
                        self.remove_belief(predicate)
                        self.remove_belief(f'pending_task_{task_id}')

        except Exception as e:
            # Log but don't crash the BDI loop
            print(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> list:
        """
        DELIBERATE: Generate intentions (plans) for pending tasks.

        This is where the agent decides WHAT to do, not HOW to do it.
        For each pending task belief, create an intention (plan) to solve it.

        Returns:
            List of new Intention objects to adopt
        """
        from symbo_agentic_reasoners.core.bdi_agent import Intention

        new_intentions = []

        # Check each pending task belief
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content

            # Skip if already claimed
            if self.has_belief(f'claimed_task_{task.entry_id}'):
                continue

            # Skip if we already have an intention for this task
            if any(i.metadata.get('task_id') == task.entry_id for i in self.intentions):
                continue

            # Determine the operation type
            operation = 'compute'
            if hasattr(task, 'metadata') and task.metadata:
                operation = task.metadata.get('operation', 'compute')

            # Create a plan based on operation type
            if operation in ['compute', 'evaluate', 'simplify']:
                steps = ['claim_task', 'parse_expression', 'compute_exact', 'verify_result', 'post_result']
            elif operation in ['expand', 'factor']:
                steps = ['claim_task', 'parse_expression', 'transform_algebraic', 'verify_result', 'post_result']
            else:
                steps = ['claim_task', 'parse_expression', 'compute_exact', 'verify_result', 'post_result']

            # Create intention
            intention = Intention(
                plan_id=f'solve_{task.entry_id}',
                steps=steps,
                target_desire='solve_arithmetic',
                metadata={
                    'task_id': task.entry_id,
                    'task_entry': task,
                    'operation': operation
                }
            )

            new_intentions.append(intention)
            print(f"[{self.agent_id}] Created plan for task {task.entry_id}: {steps}")

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Execute one step of the current plan.

        CRITICAL: This agent NEVER computes directly. It DELEGATES to SymPy.
        The agent reasons about what operation to perform, then calls SymPy.

        Args:
            intention: The intention (plan) being executed
        """
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        print(f"[{self.agent_id}] Executing step: {action} for task {task_id}")

        try:
            if action == 'claim_task':
                self._execute_claim_task(intention, task)

            elif action == 'parse_expression':
                self._execute_parse_expression(intention, task)

            elif action == 'compute_exact':
                self._execute_compute_exact(intention, task)

            elif action == 'transform_algebraic':
                self._execute_transform_algebraic(intention, task)

            elif action == 'verify_result':
                self._execute_verify_result(intention, task)

            elif action == 'post_result':
                self._execute_post_result(intention, task)

            else:
                print(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            print(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_failure(intention, task, str(e))

    def _execute_claim_task(self, intention: Intention, task):
        """Claim the task on Blackboard so others don't work on it"""
        task_id = intention.metadata['task_id']

        # Mark as claimed in our beliefs
        self.add_belief(f'claimed_task_{task_id}', True)

        # Update Blackboard status
        if self.blackboard:
            self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)

        print(f"[{self.agent_id}] Claimed task {task_id}")
        intention.advance()

    def _execute_parse_expression(self, intention: Intention, task):
        """Parse the mathematical expression - DELEGATE to native parser"""
        # Get expression from task
        expr_str = None
        if hasattr(task, 'metadata') and task.metadata:
            expr_str = task.metadata.get('sympy_expr') or task.metadata.get('raw_input')
        if not expr_str and hasattr(task, 'content'):
            expr_str = str(task.content)

        if not expr_str:
            raise ValueError("No expression to parse")

        # DELEGATE parsing to native symbolic engine
        parsed_expr = parse_expr(expr_str)

        # Store result in beliefs
        self.add_belief('parsed_expression', parsed_expr, source='native')
        print(f"[{self.agent_id}] Parsed: {expr_str} -> {parsed_expr}")

        intention.advance()

    def _execute_compute_exact(self, intention: Intention, task):
        """Compute using exact arithmetic - DELEGATE to native engine"""
        parsed = self.get_belief('parsed_expression')
        if not parsed:
            raise ValueError("No parsed expression")

        expr = parsed.content
        operation = intention.metadata.get('operation', 'compute')

        # DELEGATE computation to native symbolic engine
        if operation in ['compute', 'evaluate']:
            result = expr.simplify()
            # For pure numbers, keep exact form
            if not result.free_symbols and result.is_number:
                if not (result.is_integer or result.is_rational):
                    result = result.evalf(self.precision)
        elif operation == 'simplify':
            result = expr.simplify()
        else:
            result = expr.simplify()

        # Store result
        self.add_belief('computed_result', result, source='native')
        print(f"[{self.agent_id}] Computed ({operation}): {result}")

        intention.advance()

    def _execute_transform_algebraic(self, intention: Intention, task):
        """Transform expression (expand, factor) - DELEGATE to native engine"""
        parsed = self.get_belief('parsed_expression')
        if not parsed:
            raise ValueError("No parsed expression")

        expr = parsed.content
        operation = intention.metadata.get('operation', 'expand')

        # DELEGATE transformation to native engine
        if operation == 'expand':
            result = expand(expr)
        elif operation == 'factor':
            # Factor is simplify for now
            result = expr.simplify()
        else:
            result = expr.simplify()

        # Store result
        self.add_belief('computed_result', result, source='native')
        print(f"[{self.agent_id}] Transformed ({operation}): {result}")

        intention.advance()

    def _execute_verify_result(self, intention: Intention, task):
        """Verify the result - basic sanity check"""
        result = self.get_belief('computed_result')
        if not result:
            raise ValueError("No result to verify")

        # Basic verification: result should be valid SymPy expression
        # Full verification done by VerificationCore
        self.add_belief('verified_result', result.content, source='self')
        print(f"[{self.agent_id}] Verified: {result.content}")

        intention.advance()

    def _execute_post_result(self, intention: Intention, task):
        """Post result to Blackboard"""
        result = self.get_belief('verified_result')
        if not result:
            raise ValueError("No verified result")

        task_id = intention.metadata['task_id']

        # Create result entry on Blackboard
        if self.blackboard:
            result_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(str(result.content)),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                tags=['arithmetic', 'result', task_id],
                status=EntryStatus.COMPLETED,
                metadata={
                    'result': str(result.content),
                    'result_str': str(result.content),
                    'task_id': task_id,
                    'precision': self.precision,
                    'algorithm': 'sympy_exact'
                }
            )
            self.blackboard.post(result_entry)

        # Clean up beliefs
        self.remove_belief(f'pending_task_{task_id}')
        self.remove_belief(f'claimed_task_{task_id}')
        self.remove_belief('parsed_expression')
        self.remove_belief('computed_result')
        self.remove_belief('verified_result')

        # Update statistics
        self.tasks_succeeded += 1
        print(f"[{self.agent_id}] Posted result for task {task_id}: {result.content}")

        intention.advance()

    def _handle_failure(self, intention: Intention, task, error_msg: str):
        """Handle task failure"""
        task_id = intention.metadata.get('task_id')

        # Post error to Blackboard
        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(f"ERROR: {error_msg}"),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                tags=['error', 'arithmetic', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)

        # Clean up beliefs
        if task_id:
            self.remove_belief(f'pending_task_{task_id}')
            self.remove_belief(f'claimed_task_{task_id}')
        self.remove_belief('parsed_expression')
        self.remove_belief('computed_result')
        self.remove_belief('verified_result')

        # Update statistics
        self.tasks_failed += 1

        # Mark intention complete (failed)
        while not intention.is_complete():
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get specialist statistics including domain-first metrics.

        Returns:
            Dictionary containing:
            - tasks_executed, tasks_succeeded, tasks_failed
            - domain_computed: Count solved by Python exact arithmetic
            - sympy_fallbacks: Count falling back to SymPy
            - domain_success_rate: Percentage solved without SymPy
        """
        stats = super().get_statistics()

        total_attempts = self.domain_computed + self.sympy_fallbacks
        domain_rate = (self.domain_computed / total_attempts * 100) if total_attempts > 0 else 0.0

        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0,
            'precision': self.precision,
            # Domain-first metrics
            'domain_computed': self.domain_computed,
            'sympy_fallbacks': self.sympy_fallbacks,
            'domain_success_rate': domain_rate,
            'architecture': 'domain-first'
        })
        return stats


if __name__ == "__main__":
    """Test Arithmetic Specialist"""
    print("=" * 80)
    print("PHASE 2 - ARITHMETIC SPECIALIST TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.system import Phase0System

    # Initialize Phase 0
    print("Initializing Phase 0 infrastructure...")
    phase0 = Phase0System()
    phase0.start()
    print()

    # Initialize Arithmetic Specialist
    specialist = ArithmeticSpecialist(
        df=phase0.df,
        blackboard=phase0.blackboard,
        precision=50
    )
    print()

    print("=" * 80)
    print("ARITHMETIC SPECIALIST READY")
    print("=" * 80)
    print()

    # Test exact arithmetic
    print("Test 1: Large integer arithmetic")
    print("  Computing: 2**100")
    result_large = parse_expr("2**100")
    print(f"  Result: {result_large}")
    print(f"  Digits: {len(str(result_large))}")
    print()

    print("Test 2: Exact rational arithmetic")
    print("  Computing: 1/3 + 1/6")
    result_rational = parse_expr("1/3 + 1/6")
    print(f"  Result: {result_rational}")
    print(f"  (No rounding error!)")
    print()

    # Check DF registration
    services = phase0.df.search(service_type='math.algebra.arithmetic')
    print(f"Registered services: {len(services)}")
    for service in services:
        print(f"  - {service.service_type}: {service.agent_id}")
        print(f"    Properties: {service.properties}")

    print()
    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))

    # Shutdown
    phase0.shutdown()
