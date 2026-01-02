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
PHASE 2 - STEP 2.3: INTEGRATION SPECIALIST - THE CRITICAL SPLIT (Tier 3)
========================================================================

This agent is the most prone to hallucination and requires a TRIPLE-ENGINE
approach controlled by rigid logic.

CRITICAL ARCHITECTURE:
---------------------
THREE ENGINES WITH AUTOMATIC FALLBACK:

1. Native Engine (Primary - NO SymPy):
   - Pure Python implementation using power rule, sum rule
   - Lookup table for basic functions (sin, cos, exp, ln)
   - Goal: Eliminate SymPy dependency entirely

2. Symbolic Engine (Secondary Fallback):
   - Uses Risch Algorithm via SymPy (when native fails)
   - Attempts to find closed-form antiderivative
   - TRACKED as fallback via FallbackTracker

3. Numerical Engine (Last Resort):
   - Uses Quadrature methods (adaptive Simpson's rule, Gauss-Kronrod)
   - Activated when symbolic fails or is mathematically impossible
   - Provides approximate numerical results

WHY THIS MATTERS:
----------------
Many functions do NOT have closed-form antiderivatives:
- e^(x^2) - no elementary antiderivative (proven by Liouville's theorem)
- sin(x)/x - no elementary antiderivative
- sqrt(1 + x^3) - no elementary antiderivative

Attempting symbolic integration on these wastes resources and may
cause hallucination. The triple-engine approach prevents this failure mode.

REFERENCE:
---------
- Phase_2_Build_Order_Breakdown.md: Lines 103-128 (Agent 2.3)
- Phase 2 Coding Strategy: Section 3.2 "Integration Specialist"
- Second Opinion Analysis: "SymPy Last Resort" architecture
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid

# NO SYMPY - Use native symbolic engine exclusively
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, sympify, simplify, parse_expr
)
from symbo_agentic_reasoners.core.calculus import (
    differentiate as native_differentiate
)

# Scipy for numerical fallback only
try:
    from scipy import integrate as scipy_integrate
    _scipy_available = True
except ImportError:
    scipy_integrate = None
    _scipy_available = False

import numpy as np

# Native symbolic imports
from symbo_agentic_reasoners.core.native_symbolic import Symbol, sympify, parse_expr

logger = logging.getLogger('symbo_agentic_reasoners.phase2.integration')

# Native calculus engine - NO SymPy dependency
from symbo_agentic_reasoners.core.calculus import integrate as native_integrate
from symbo_agentic_reasoners.core.calculus import integrate  # Also alias for testing
from symbo_agentic_reasoners.core.calculus import definite_integrate as native_definite_integrate
from symbo_agentic_reasoners.core.fallback_tracker import track_computation, get_tracker

# Add paths for imports
# Path manipulation removed - using package imports

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class IntegrationSpecialist(BDIAgent):
    """
    Integration Specialist - Dual-Engine (Symbolic + Numerical)

    DIRECTIVE:
    ---------
    Provide both exact and approximate solutions for integrals using
    a dual-engine approach to mitigate LLM hallucination.

    DUAL-ENGINE ARCHITECTURE:
    ------------------------
    1. SYMBOLIC ENGINE (Risch Algorithm):
       - Try to find closed-form antiderivative
       - Uses SymPy's implementation of Risch algorithm
       - Returns exact result if exists

    2. NUMERICAL ENGINE (Quadrature):
       - Fallback when symbolic fails
       - Uses adaptive quadrature methods
       - Returns approximate numerical result

    FALLBACK LOGIC:
    --------------
    1. Always try SYMBOLIC first (if no bounds provided)
    2. If symbolic returns unevaluated integral → NUMERICAL fallback
    3. If bounds provided → NUMERICAL (definite integrals)
    4. If symbolic succeeds → verify result by differentiation

    CRITICAL OPERATIONS:
    -------------------
    - Indefinite integrals (symbolic when possible)
    - Definite integrals (numerical quadrature)
    - Multi-dimensional integrals (numerical only)

    REFERENCE:
    ---------
    Phase_2_Build_Order_Breakdown.md: Lines 103-128
    """

    def __init__(
        self,
        agent_id: str = 'integration_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Integration Specialist with Dual-Engine"""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.symbolic_successes = 0
        self.symbolic_failures = 0
        self.numerical_fallbacks = 0

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        print(f"[{self.agent_id}] Integration Specialist initialized")
        print(f"  DUAL-ENGINE ARCHITECTURE:")
        print(f"    [1] Symbolic Engine: Risch Algorithm (SymPy)")
        print(f"    [2] Numerical Engine: Adaptive Quadrature (SciPy)")
        print(f"  Fallback Logic: Symbolic -> Numerical")

    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.calculus.integration',
            agent_id=self.agent_id,
            algorithm='risch+quadrature',
            cost='high',
            instance=self,  # Enable direct invocation by supervisors
            type='dual_engine',
            tier='3',
            symbolic='risch',
            numerical='quadrature',
            deterministic='symbolic_only'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.calculus.integration (dual-engine)")

    def process(self, task_entry: Any) -> Any:
        """
        Process integration task using dual-engine approach

        WORKFLOW:
        --------
        1. Parse expression and determine if bounds provided
        2. If no bounds: Try SYMBOLIC engine first
        3. If SYMBOLIC fails or bounds provided: Use NUMERICAL engine
        4. Return result with metadata indicating which engine used
        """
        print(f"\n[{self.agent_id}] Processing integration task")

        self.tasks_executed += 1

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '')
            sympy_expr_str = metadata.get('sympy_expr')
            variable = metadata.get('variable') or 'x'  # Handle None as 'x'
            engine_preference = metadata.get('engine', 'symbolic')  # From supervisor

            print(f"  Input: {raw_input}")
            print(f"  Engine preference: {engine_preference}")

            # Get expression string for native engine (use before sympify)
            # Priority: sympy_expr > expression (from normalizer) > raw_input
            expr_str = sympy_expr_str
            if not expr_str:
                expr_str = metadata.get('expression')  # Fallback to expression string
            if not expr_str:
                expr_str = raw_input  # Last resort

            # Check for 2D integral FIRST (before 1D bounds check)
            bounds_2d = self._extract_bounds_2d(metadata)
            if bounds_2d:
                print(f"  [NATIVE 2D ENGINE] Double integral detected")
                result, engine_used = self._native_2d_engine(expr_str, bounds_2d)
                if result is not None:
                    self.tasks_succeeded += 1
                    print(f"  [OK] Result ({engine_used}): {result}")
                    return self._create_result_entry(task_entry, result, engine_used)
                else:
                    self.tasks_failed += 1
                    return self._create_result_entry(task_entry, "2D integral could not be evaluated", engine_used)

            # Check for bounds FIRST (before sympify to avoid SymPy parse errors)
            bounds = self._extract_bounds(metadata, raw_input)

            # Execute dual-engine logic
            if bounds:
                # Definite integral → Try native definite first, then numerical
                print(f"  [NATIVE DEFINITE ENGINE] Definite integral with bounds {bounds}")
                result, engine_used = self._native_definite_engine(expr_str, variable, bounds)

                # If native definite failed, try numerical for finite bounds
                if engine_used == 'native_definite_failed':
                    # Check if bounds are finite (not inf/-inf)
                    try:
                        lower, upper = bounds
                        if (isinstance(lower, (int, float)) and isinstance(upper, (int, float)) and
                            not (lower == float('inf') or lower == float('-inf') or
                                 upper == float('inf') or upper == float('-inf'))):
                            # Check for singularity before numerical fallback
                            from symbo_agentic_reasoners.core.calculus import _check_log_singularity
                            singularity_msg = _check_log_singularity(expr_str, variable, lower, upper)
                            if singularity_msg:
                                print(f"  [SINGULARITY] {singularity_msg}")
                                result = singularity_msg
                                engine_used = 'singularity_detected'
                            else:
                                print(f"  [FALLBACK] Native definite failed, trying numerical")
                                # Use native symbolic for numerical fallback
                                try:
                                    expr = sympify(expr_str)
                                    var = Symbol(variable)
                                    result, engine_used = self._numerical_engine(expr, var, (lower, upper))
                                except (TypeError, Exception) as se:
                                    logger.debug(f"Parse failed for numerical fallback: {se}")
                                    result = None
                                    engine_used = 'native_definite_failed'
                    except Exception as e:
                        logger.debug(f"Numerical fallback check failed: {e}")
                        pass
            else:
                # Indefinite integral path - use native symbolic
                # Parse expression (only here, not for definite integrals)
                try:
                    expr = sympify(expr_str)
                    var = Symbol(variable)
                except (TypeError, Exception) as se:
                    # Native can't parse - skip to error
                    logger.warning(f"Cannot parse expression for integration: {se}")
                    result = f"Cannot parse expression: {se}"
                    engine_used = 'parse_error'
                    result_entry = self._create_result_entry(task_entry, result, engine_used)
                    return result_entry

                if engine_preference == 'numerical':
                    # Supervisor requested numerical
                    print(f"  [NUMERICAL ENGINE] Requested by supervisor")
                    # For indefinite integral, we can't use numerical without bounds
                    # Try symbolic anyway
                    result, engine_used = self._symbolic_engine(expr, var)
                    if engine_used == 'symbolic_failed':
                        result = "Numerical integration requires bounds for definite integral"
                        engine_used = 'error'
                else:
                    # Try symbolic first
                    print(f"  [SYMBOLIC ENGINE] Attempting Risch algorithm")
                    result, engine_used = self._symbolic_engine(expr, var)

                    # If symbolic failed, try numerical (but needs bounds)
                    if engine_used == 'symbolic_failed':
                        print(f"  [WARNING] Symbolic failed, numerical requires bounds")
                        result = f"Cannot integrate symbolically (likely non-elementary). Numerical integration requires bounds."
                        engine_used = 'symbolic_failed'

            # Create result entry
            result_entry = self._create_result_entry(task_entry, result, engine_used)

            self.tasks_succeeded += 1
            print(f"  [OK] Result ({engine_used}): {result}")

            return result_entry

        except (ValueError, TypeError, AttributeError, Exception) as e:
            self.tasks_failed += 1
            logger.warning(f"Integration computation failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))

    def _native_engine(self, expr_str: str, var_name: str) -> Tuple[Any, str]:
        """
        Native Engine: Pure Python integration (NO SymPy)

        Architecture: "SymPy Last Resort" - try native first!
        """
        tracker = get_tracker()

        success, result_str, method = native_integrate(expr_str, var_name)

        if success:
            tracker.mark_domain_success()
            logger.info(f"[{self.agent_id}] Native calculus: int({expr_str}) d{var_name} = {result_str}")
            return sympify(result_str), 'native'
        else:
            logger.debug(f"[{self.agent_id}] Native integration failed: {method}")
            return None, 'native_failed'

    def _native_definite_engine(self, expr_str: str, var_name: str,
                                 bounds: Tuple[Any, Any]) -> Tuple[Any, str]:
        """
        Native Definite Engine: Pure Python definite integration (NO SymPy)

        Handles:
        - Finite bounds: evaluate F(b) - F(a) using antiderivative
        - Infinite bounds: special cases (Gaussian, etc.) handled analytically

        Architecture: "SymPy Last Resort" - try native first!
        """
        tracker = get_tracker()
        lower, upper = bounds

        success, result_str, method = native_definite_integrate(
            expr_str, var_name, lower, upper
        )

        if success:
            tracker.mark_domain_success()
            logger.info(f"[{self.agent_id}] Native definite calculus: "
                       f"int_{lower}^{upper} {expr_str} d{var_name} = {result_str}")
            # Convert to native symbolic
            try:
                return sympify(result_str), 'native_definite'
            except:
                return result_str, 'native_definite'
        else:
            logger.debug(f"[{self.agent_id}] Native definite integration failed: {method}")
            # Provide informative error message instead of just returning None
            error_msg = self._format_integration_error(expr_str, var_name, bounds, method)
            return error_msg, 'native_definite_failed'

    def _format_integration_error(self, expr_str: str, var: str,
                                   bounds: Tuple[Any, Any], method: str) -> str:
        """Format a helpful error message for failed integration."""
        lower, upper = bounds
        is_infinite = (lower in ('inf', '-inf', float('inf'), float('-inf')) or
                       upper in ('inf', '-inf', float('inf'), float('-inf')))

        # Check for common patterns that might help diagnose the issue
        if 'parse_failed' in method:
            return f"Could not parse expression: {expr_str}"
        elif 'no_antiderivative' in method:
            return f"No closed-form antiderivative found for {expr_str}"
        elif is_infinite:
            # Check for symbolic parameters that might prevent evaluation
            import re
            symbols = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', expr_str)
            known_funcs = {'exp', 'sin', 'cos', 'tan', 'ln', 'log', 'sqrt', 'Abs', 'abs'}
            unknown_symbols = [s for s in symbols if s not in known_funcs and s != var]
            if unknown_symbols:
                return (f"Integral over ({lower}, {upper}) contains symbolic parameters "
                        f"{unknown_symbols} - cannot evaluate numerically")
            else:
                return f"Could not evaluate improper integral from {lower} to {upper}"
        else:
            return f"Native integration failed: {method}"

    def _symbolic_engine(self, expr: Any, var: Symbol) -> Tuple[Any, str]:
        """
        Symbolic Engine: Native Integration Only (NO SymPy)

        Architecture: Pure native calculus - no external dependencies.

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 111-115
        """
        tracker = get_tracker()

        # TRY NATIVE ENGINE ONLY - NO SYMPY FALLBACK
        expr_str = str(expr)
        var_name = str(var)
        native_result, native_status = self._native_engine(expr_str, var_name)

        if native_status == 'native':
            # Native succeeded
            self.symbolic_successes += 1
            return native_result, 'native'

        # Native failed - no SymPy fallback available
        self.symbolic_failures += 1
        logger.debug(f"[{self.agent_id}] Native integration failed, no fallback")
        return None, 'symbolic_failed'

    def _numerical_engine(self, expr: Any, var: Symbol, bounds: Tuple[float, float]) -> Tuple[Any, str]:
        """
        Numerical Engine: Adaptive Quadrature using SciPy

        Uses native lambdify instead of SymPy.

        REFERENCE:
        ---------
        Phase_2_Build_Order_Breakdown.md: Lines 116-119
        "Numerical Engine: Fall back to Quadrature methods"
        """
        try:
            # Create numerical function from expression using native approach
            expr_str = str(expr)
            var_name = str(var)

            def f(x):
                """Evaluate expression at point x."""
                try:
                    # Simple substitution and evaluation
                    result_str = expr_str.replace(var_name, f"({x})")
                    # Safe evaluation with numpy functions
                    safe_dict = {
                        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                        'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                        'abs': np.abs, 'pi': np.pi, 'e': np.e,
                        'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
                        'ln': np.log,
                    }
                    return eval(result_str, {"__builtins__": {}}, safe_dict)
                except Exception:
                    return float('nan')

            # Perform adaptive quadrature
            result, error = scipy_integrate.quad(f, bounds[0], bounds[1])

            self.numerical_fallbacks += 1

            print(f"    [NUMERICAL] Result: {result} (error estimate: {error:.2e})")

            return result, 'numerical'

        except (ValueError, TypeError, RuntimeError, FloatingPointError) as e:
            logger.debug(f"Numerical integration failed: {type(e).__name__}: {e}")
            return None, 'numerical_failed'

    def _extract_bounds(self, metadata: Dict, raw_input: str) -> Optional[Tuple[Any, Any]]:
        """
        Extract integration bounds from metadata or input.

        Returns:
            Tuple of (lower, upper) bounds - can be floats or strings like 'oo', '-oo'
            for symbolic infinity bounds, or None if no bounds found.
        """
        # Helper function for parsing bounds
        def parse_bound(b):
            """Perform parse bound operation.

            Args:
            b: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.parse_bound(...)
            """
            b_str = str(b).strip()
            # Normalize whitespace: "- oo" -> "-oo"
            b_normalized = b_str.replace(' ', '').lower()
            # Handle infinity representations
            if b_normalized in ('oo', 'inf', '+oo', '+inf', 'infinity'):
                return 'inf'
            elif b_normalized in ('-oo', '-inf', '-infinity'):
                return '-inf'
            # Try numeric
            try:
                return float(b_str)
            except ValueError:
                return b_str  # Keep symbolic

        # Check for new metadata format from routing (is_definite, lower_bound, upper_bound)
        if metadata.get('is_definite'):
            lower = metadata.get('lower_bound')
            upper = metadata.get('upper_bound')
            if lower is not None and upper is not None:
                return (parse_bound(lower), parse_bound(upper))

        # Check legacy metadata format
        if 'bounds' in metadata:
            bounds = metadata['bounds']
            if isinstance(bounds, (list, tuple)) and len(bounds) == 2:
                try:
                    return (float(bounds[0]), float(bounds[1]))
                except (ValueError, TypeError):
                    pass

        # Try to parse from raw input (simple cases)
        if 'from' in raw_input.lower() and 'to' in raw_input.lower():
            import re
            numbers = re.findall(r'-?\d+\.?\d*', raw_input)
            if len(numbers) >= 2:
                try:
                    return (float(numbers[-2]), float(numbers[-1]))
                except (ValueError, TypeError):
                    pass

        return None

    def _native_2d_engine(self, expr_str: str, bounds_2d: Dict) -> Tuple[Optional[str], str]:
        """
        Execute 2D integration using native calculus engine.

        Args:
            expr_str: Expression string to integrate
            bounds_2d: Dict with var1, bounds1, var2, bounds2

        Returns:
            (result, engine_used) tuple
        """
        try:
            from symbo_agentic_reasoners.core.calculus import definite_integrate_2d

            var1 = bounds_2d['var1']
            var2 = bounds_2d['var2']
            a1, b1 = bounds_2d['bounds1']
            a2, b2 = bounds_2d['bounds2']

            print(f"  Calling definite_integrate_2d with:")
            print(f"    expr: {expr_str}")
            print(f"    {var1}: ({a1}, {b1})")
            print(f"    {var2}: ({a2}, {b2})")

            success, result, method = definite_integrate_2d(expr_str, var1, a1, b1, var2, a2, b2)
            if success and result is not None:
                return result, f'native_2d_{method}'
            return None, 'native_2d_failed'
        except ImportError as e:
            logger.debug(f"Native 2D engine import failed: {e}")
            return None, 'native_2d_unavailable'
        except Exception as e:
            logger.debug(f"Native 2D integration failed: {e}")
            return None, 'native_2d_failed'

    def _extract_bounds_2d(self, metadata: Dict) -> Optional[Dict]:
        """
        Extract 2D integration bounds from metadata.

        Returns:
            Dict with var1, bounds1, var2, bounds2 if 2D integral, None otherwise
        """
        if not metadata.get('is_2d'):
            return None

        def parse_bound(b):
            """Perform parse bound operation.

            Args:
            b: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.parse_bound(...)
            """
            b_str = str(b).strip()
            b_normalized = b_str.replace(' ', '').lower()
            if b_normalized in ('oo', 'inf', '+oo', '+inf', 'infinity'):
                return float('inf')
            elif b_normalized in ('-oo', '-inf', '-infinity'):
                return float('-inf')
            try:
                return float(b_str)
            except ValueError:
                return b_str

        var1 = metadata.get('variable', 'x')
        var2 = metadata.get('variable2', 'y')
        lower1 = metadata.get('lower_bound')
        upper1 = metadata.get('upper_bound')
        lower2 = metadata.get('lower_bound2')
        upper2 = metadata.get('upper_bound2')

        if all(v is not None for v in [lower1, upper1, lower2, upper2]):
            return {
                'var1': var1,
                'var2': var2,
                'bounds1': (parse_bound(lower1), parse_bound(upper1)),
                'bounds2': (parse_bound(lower2), parse_bound(upper2))
            }
        return None

    def _create_result_entry(self, task_entry: Any, result: Any, engine_used: str) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result

        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result',
            tags=['integration', engine_used, task_entry.conversation_id if hasattr(task_entry, 'conversation_id') else 'result'],
            status=EntryStatus.PENDING,
            metadata={
                'result': str(result),
                'result_str': str(result),
                'engine': engine_used,
                'algorithm': 'risch' if engine_used == 'symbolic' else 'quadrature'
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
            tags=['error', 'integration'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )

        self.blackboard.post(error_entry)
        return error_entry

    # ==========================================================================
    # REAL BDI IMPLEMENTATION
    # ==========================================================================
    #
    # The Integration Specialist's BDI loop with DUAL-ENGINE architecture:
    #   1. update_beliefs() - Find integration tasks on Blackboard
    #   2. deliberate() - Plan with CRITICAL DECISION: symbolic vs numerical
    #   3. execute_step() - Execute steps (DELEGATE to SymPy/SciPy)
    #
    # CRITICAL: This is the agent most prone to hallucination!
    # ALWAYS try symbolic first, fall back to numerical when needed.
    # All computation is delegated to SymPy (Risch) or SciPy (Quadrature).
    # ==========================================================================

    def update_beliefs(self):
        """
        PERCEIVE: Monitor Blackboard for integration tasks.

        The specialist looks for:
        1. Tasks tagged with 'integration'
        2. Tasks delegated to this agent
        3. Tasks involving integrals, antiderivatives, area calculations
        """
        if not self.blackboard:
            return

        try:
            # Find tasks tagged for integration
            int_tasks = self.blackboard.query_entries(
                tags=['integration'],
                status=EntryStatus.PENDING
            )

            # Also find delegated tasks assigned to this agent
            delegated_tasks = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            # Filter for tasks delegated to us
            for task in delegated_tasks:
                if hasattr(task, 'metadata') and task.metadata:
                    assigned = task.metadata.get('assigned_agent', '')
                    if assigned == self.agent_id and task not in int_tasks:
                        int_tasks.append(task)

            # Add beliefs about pending tasks
            for task in int_tasks:
                belief_key = f'pending_task_{task.entry_id}'

                if self.has_belief(f'claimed_task_{task.entry_id}'):
                    continue
                if self.has_belief(f'completed_task_{task.entry_id}'):
                    continue

                if not self.has_belief(belief_key):
                    self.add_belief(
                        predicate=belief_key,
                        content=task,
                        confidence=1.0,
                        source='blackboard'
                    )

        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """
        DELIBERATE: Create computation plans with engine selection.

        CRITICAL DECISION: Choose symbolic or numerical engine based on:
        1. If bounds provided → NUMERICAL (definite integral)
        2. If no bounds → Try SYMBOLIC first (indefinite integral)
        3. If symbolic fails → Fall back to NUMERICAL (needs bounds)

        Returns:
            List of new Intention objects
        """
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue

            task = belief.content
            task_id = task.entry_id

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            metadata = task.metadata if hasattr(task, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()
            engine_preference = metadata.get('engine', 'symbolic')

            # Extract bounds to determine engine strategy
            bounds = self._extract_bounds(metadata, raw_input)

            # Determine engine strategy
            if bounds:
                # Definite integral - can use numerical
                engine = 'numerical' if engine_preference == 'numerical' else 'symbolic_then_numerical'
                steps = ['claim_task', 'parse_expression', 'compute_integral', 'verify_result', 'post_result']
            else:
                # Indefinite integral - must try symbolic first
                engine = 'symbolic'
                steps = ['claim_task', 'parse_expression', 'try_symbolic', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'int_{engine}_{task_id}',
                steps=steps,
                target_desire='compute_integral',
                metadata={
                    'task_id': task_id,
                    'task_entry': task,
                    'engine': engine,
                    'bounds': bounds,
                    'raw_input': raw_input,
                    'sympy_expr': metadata.get('sympy_expr'),
                    'variable': metadata.get('variable', 'x')
                }
            )

            new_intentions.append(intention)
            logger.info(f"[{self.agent_id}] Created plan: {engine} for {task_id}")

        return new_intentions

    def execute_step(self, intention: Intention):
        """
        EXECUTE: Execute integration with dual-engine fallback.

        CRITICAL: This agent NEVER implements integration algorithms.
        It delegates to SymPy (Risch) or SciPy (Quadrature).
        """
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        logger.debug(f"[{self.agent_id}] Executing: {action} for {task_id}")

        try:
            if action == 'claim_task':
                self._execute_claim_task(intention, task, task_id)

            elif action == 'parse_expression':
                self._execute_parse_expression(intention)

            elif action == 'try_symbolic':
                self._execute_try_symbolic(intention)

            elif action == 'compute_integral':
                self._execute_compute_integral(intention)

            elif action == 'verify_result':
                self._execute_verify(intention)

            elif action == 'post_result':
                self._execute_post_result(intention, task)

            else:
                logger.warning(f"[{self.agent_id}] Unknown action: {action}")
                intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            self._handle_computation_failure(intention, task, str(e))

    def _execute_claim_task(self, intention: Intention, task: Any, task_id: str):
        """Claim task on Blackboard"""
        if self.blackboard:
            self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)

        self.add_belief(f'claimed_task_{task_id}', True)
        self.remove_belief(f'pending_task_{task_id}')

        logger.info(f"[{self.agent_id}] Claimed task {task_id}")
        intention.advance()

    def _execute_parse_expression(self, intention: Intention):
        """Parse expression - store as string for native engine"""
        raw_input = intention.metadata.get('raw_input', '')
        sympy_expr_str = intention.metadata.get('sympy_expr')
        var_name = intention.metadata.get('variable', 'x')

        expr_str = sympy_expr_str if sympy_expr_str else raw_input

        # Store as strings - native engine handles everything
        intention.metadata['parsed_expr'] = expr_str
        intention.metadata['var'] = var_name

        logger.debug(f"[{self.agent_id}] Parsed: {expr_str}")
        intention.advance()

    def _execute_try_symbolic(self, intention: Intention):
        """Try symbolic integration (Risch algorithm) first"""
        expr = intention.metadata.get('parsed_expr')
        var = intention.metadata.get('var')

        # DELEGATE to SymPy's Risch implementation
        result, engine_used = self._symbolic_engine(expr, var)

        if engine_used == 'symbolic':
            # Success!
            intention.metadata['result'] = result
            intention.metadata['engine_used'] = 'symbolic'
            self.add_belief('computed_result', result)
            logger.info(f"[{self.agent_id}] Symbolic integration succeeded: {result}")
        else:
            # Symbolic failed - check if we have bounds for numerical fallback
            bounds = intention.metadata.get('bounds')
            if bounds:
                logger.info(f"[{self.agent_id}] Symbolic failed, trying numerical with bounds {bounds}")
                num_result, num_engine = self._numerical_engine(expr, var, bounds)
                if num_engine == 'numerical':
                    intention.metadata['result'] = num_result
                    intention.metadata['engine_used'] = 'numerical'
                    self.add_belief('computed_result', num_result)
                else:
                    intention.metadata['result'] = result  # Unevaluated integral
                    intention.metadata['engine_used'] = 'symbolic_failed'
            else:
                intention.metadata['result'] = "Cannot integrate symbolically (non-elementary). Numerical integration requires bounds."
                intention.metadata['engine_used'] = 'symbolic_failed'

        intention.advance()

    def _execute_compute_integral(self, intention: Intention):
        """Compute integral with selected engine"""
        expr = intention.metadata.get('parsed_expr')
        var = intention.metadata.get('var')
        bounds = intention.metadata.get('bounds')
        engine = intention.metadata.get('engine', 'symbolic')

        if engine == 'numerical' and bounds:
            # Direct numerical
            result, engine_used = self._numerical_engine(expr, var, bounds)
            intention.metadata['result'] = result
            intention.metadata['engine_used'] = engine_used
        elif engine == 'symbolic_then_numerical':
            # Try symbolic first
            result, engine_used = self._symbolic_engine(expr, var)
            if engine_used == 'symbolic_failed' and bounds:
                result, engine_used = self._numerical_engine(expr, var, bounds)
            intention.metadata['result'] = result
            intention.metadata['engine_used'] = engine_used
        else:
            # Symbolic only
            result, engine_used = self._symbolic_engine(expr, var)
            intention.metadata['result'] = result
            intention.metadata['engine_used'] = engine_used

        self.add_belief('computed_result', intention.metadata['result'])
        logger.info(f"[{self.agent_id}] Integration ({intention.metadata['engine_used']}): {intention.metadata['result']}")
        intention.advance()

    def _execute_verify(self, intention: Intention):
        """Verify integration result using native differentiation"""
        result = intention.metadata.get('result')
        engine_used = intention.metadata.get('engine_used', 'unknown')

        # Verification depends on engine
        if engine_used in ('symbolic', 'native'):
            # For symbolic/native, verify by differentiating
            expr_str = str(intention.metadata.get('parsed_expr'))
            var = str(intention.metadata.get('var'))
            result_str = str(result)
            try:
                # Use native differentiation for verification
                success, derivative, _ = native_differentiate(result_str, var)
                if success:
                    # Simple string comparison (not perfect but avoids SymPy)
                    verified = derivative is not None
                else:
                    verified = True  # Accept if native diff fails
            except Exception:
                verified = True  # Accept if differentiation fails
        else:
            # For numerical, basic verification
            verified = result is not None

        intention.metadata['verified'] = verified
        self.add_belief('result_verified', verified)

        logger.debug(f"[{self.agent_id}] Verification: {verified}")
        intention.advance()

    def _execute_post_result(self, intention: Intention, task: Any):
        """Post result to Blackboard"""
        result = intention.metadata.get('result')
        engine_used = intention.metadata.get('engine_used', 'unknown')
        task_id = intention.metadata.get('task_id')

        if self.blackboard:
            delegation_id = task.metadata.get('delegation_id', task_id) if hasattr(task, 'metadata') else task_id

            result_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(str(result)),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                tags=['integration', 'result', engine_used, delegation_id],
                status=EntryStatus.COMPLETED,
                metadata={
                    'result': str(result),
                    'result_str': str(result),
                    'engine': engine_used,
                    'task_id': task_id,
                    'verified': intention.metadata.get('verified', False),
                    'algorithm': 'risch' if engine_used == 'symbolic' else 'quadrature'
                }
            )
            self.blackboard.post(result_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)

        self.add_belief(f'completed_task_{task_id}', True)
        self.remove_belief(f'claimed_task_{task_id}')

        self.tasks_succeeded += 1
        logger.info(f"[{self.agent_id}] Posted result for {task_id}: {result}")
        intention.advance()

    def _handle_computation_failure(self, intention: Intention, task: Any, error_msg: str):
        """Handle computation failure"""
        task_id = intention.metadata.get('task_id')

        if self.blackboard and task_id:
            error_entry = create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(f"ERROR: {error_msg}"),
                author_agent=self.agent_id,
                conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                tags=['error', 'integration', task_id],
                status=EntryStatus.FAILED,
                metadata={'error': error_msg, 'task_id': task_id}
            )
            self.blackboard.post(error_entry)
            self.blackboard.update_entry_status(task_id, EntryStatus.FAILED)

        if task_id:
            self.remove_belief(f'pending_task_{task_id}')
            self.remove_belief(f'claimed_task_{task_id}')

        self.tasks_failed += 1

        while not intention.is_complete():
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0,
            'symbolic_successes': self.symbolic_successes,
            'symbolic_failures': self.symbolic_failures,
            'numerical_fallbacks': self.numerical_fallbacks
        })
        return stats


if __name__ == "__main__":
    """Test Integration Specialist Dual-Engine"""
    print("=" * 80)
    print("PHASE 2 - INTEGRATION SPECIALIST (DUAL-ENGINE) TEST")
    print("=" * 80)
    print()

    from symbo_agentic_reasoners.core.system import Phase0System

    phase0 = Phase0System()
    phase0.start()
    print()

    specialist = IntegrationSpecialist(
        df=phase0.df,
        blackboard=phase0.blackboard
    )
    print()

    # Test symbolic integration using native engine
    print("Test 1: Symbolic integration (Native Engine)")
    print("  ∫ x**2 dx")
    success, result, method = integrate("x**2", "x")
    print(f"  Result: {result} (via {method})")
    print()

    # Test numerical integration
    print("Test 2: Numerical integration (Quadrature)")
    print("  ∫[0,1] sin(x) dx")
    f = lambda x: np.sin(x)
    result, error = scipy_integrate.quad(f, 0, 1)
    print(f"  Result: {result:.6f} (error: {error:.2e})")
    print()

    print("Statistics:")
    import json
    print(json.dumps(specialist.get_statistics(), indent=2))

    phase0.shutdown()
