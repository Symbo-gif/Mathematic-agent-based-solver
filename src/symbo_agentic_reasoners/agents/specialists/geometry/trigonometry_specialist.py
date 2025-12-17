# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
TRIGONOMETRY SPECIALIST (Tier 3)
================================

Handles trigonometric computations: identities, equations,
law of sines/cosines, inverse trig functions, and polar coordinates.

CAPABILITIES:
- Trig function evaluation
- Identity verification and simplification
- Law of sines and cosines
- Inverse trig functions
- Polar/rectangular coordinate conversion
- Trig equation solving
"""

from typing import Any, Dict, List, Optional, Tuple
import math
import re
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


# ============================================================================
# NATIVE TRIGONOMETRY ENGINE (NO SYMPY)
# ============================================================================

class NativeTrigEngine:
    """Pure Python trigonometry engine using explicit mathematical rules."""

    # Common trig identities for simplification
    IDENTITIES = {
        'sin^2+cos^2': 1,  # sin^2(x) + cos^2(x) = 1
        'tan=sin/cos': True,  # tan(x) = sin(x)/cos(x)
        '1+tan^2=sec^2': True,  # 1 + tan^2(x) = sec^2(x)
        '1+cot^2=csc^2': True,  # 1 + cot^2(x) = csc^2(x)
    }

    # Double angle formulas
    DOUBLE_ANGLE = {
        'sin_2x': lambda x: 2 * math.sin(x) * math.cos(x),
        'cos_2x': lambda x: math.cos(x)**2 - math.sin(x)**2,
        'tan_2x': lambda x: 2 * math.tan(x) / (1 - math.tan(x)**2) if abs(math.tan(x)) != 1 else float('inf'),
    }

    @staticmethod
    def evaluate_trig(func_name: str, value: float) -> float:
        """Evaluate a trig function at a numeric value."""
        funcs = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'asinh': math.asinh, 'acosh': math.acosh, 'atanh': math.atanh,
        }
        if func_name in funcs:
            return funcs[func_name](value)
        elif func_name == 'cot':
            return 1 / math.tan(value) if math.tan(value) != 0 else float('inf')
        elif func_name == 'sec':
            return 1 / math.cos(value) if math.cos(value) != 0 else float('inf')
        elif func_name == 'csc':
            return 1 / math.sin(value) if math.sin(value) != 0 else float('inf')
        raise ValueError(f"Unknown trig function: {func_name}")

    @staticmethod
    def simplify_trig_expr(expr_str: str) -> str:
        """
        Simplify trig expression using pattern matching and identities.
        Returns simplified string representation.
        """
        expr = expr_str.strip()

        # Pattern: sin(x)^2 + cos(x)^2 -> 1
        if re.search(r'sin\([^)]+\)\*\*2\s*\+\s*cos\([^)]+\)\*\*2', expr):
            return '1'
        if re.search(r'cos\([^)]+\)\*\*2\s*\+\s*sin\([^)]+\)\*\*2', expr):
            return '1'

        # Pattern: 1 - sin(x)^2 -> cos(x)^2
        match = re.search(r'1\s*-\s*sin\(([^)]+)\)\*\*2', expr)
        if match:
            return f'cos({match.group(1)})**2'

        # Pattern: 1 - cos(x)^2 -> sin(x)^2
        match = re.search(r'1\s*-\s*cos\(([^)]+)\)\*\*2', expr)
        if match:
            return f'sin({match.group(1)})**2'

        # Numeric evaluation if possible
        try:
            # Replace trig functions with math equivalents for eval
            eval_expr = expr
            for func in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']:
                eval_expr = eval_expr.replace(func, f'math.{func}')
            eval_expr = eval_expr.replace('pi', str(math.pi))
            result = eval(eval_expr)
            if isinstance(result, (int, float)):
                return str(result)
        except:
            pass

        return expr

    @staticmethod
    def expand_trig_expr(expr_str: str) -> str:
        """
        Expand trig expression using sum/difference formulas.
        """
        expr = expr_str.strip()

        # Pattern: sin(2*x) -> 2*sin(x)*cos(x)
        match = re.search(r'sin\(2\*([^)]+)\)', expr)
        if match:
            var = match.group(1)
            return expr.replace(f'sin(2*{var})', f'2*sin({var})*cos({var})')

        # Pattern: cos(2*x) -> cos(x)^2 - sin(x)^2
        match = re.search(r'cos\(2\*([^)]+)\)', expr)
        if match:
            var = match.group(1)
            return expr.replace(f'cos(2*{var})', f'cos({var})**2 - sin({var})**2')

        return expr

    @staticmethod
    def verify_identity(lhs: str, rhs: str, test_values: List[float] = None) -> bool:
        """
        Verify trig identity by numerical evaluation at multiple points.
        """
        if test_values is None:
            test_values = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5]

        for x in test_values:
            try:
                left_eval = lhs
                right_eval = rhs
                for func in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']:
                    left_eval = left_eval.replace(func, f'math.{func}')
                    right_eval = right_eval.replace(func, f'math.{func}')
                left_eval = left_eval.replace('x', str(x)).replace('pi', str(math.pi))
                right_eval = right_eval.replace('x', str(x)).replace('pi', str(math.pi))

                left_val = eval(left_eval)
                right_val = eval(right_eval)

                if abs(left_val - right_val) > 1e-10:
                    return False
            except:
                # Skip points where evaluation fails (e.g., division by zero)
                continue

        return True

    @staticmethod
    def solve_trig_equation(equation_str: str, variable: str = 'x') -> List[str]:
        """
        Solve simple trig equations using inverse functions.
        Returns solutions in [0, 2*pi) interval.
        """
        eq = equation_str.strip()
        solutions = []

        # Pattern: sin(x) = value
        match = re.match(r'sin\(([^)]+)\)\s*=\s*(-?[\d.]+)', eq)
        if match:
            var, val = match.groups()
            val = float(val)
            if -1 <= val <= 1:
                base = math.asin(val)
                solutions.append(str(base))
                solutions.append(str(math.pi - base))
            return solutions

        # Pattern: cos(x) = value
        match = re.match(r'cos\(([^)]+)\)\s*=\s*(-?[\d.]+)', eq)
        if match:
            var, val = match.groups()
            val = float(val)
            if -1 <= val <= 1:
                base = math.acos(val)
                solutions.append(str(base))
                solutions.append(str(2*math.pi - base))
            return solutions

        # Pattern: tan(x) = value
        match = re.match(r'tan\(([^)]+)\)\s*=\s*(-?[\d.]+)', eq)
        if match:
            var, val = match.groups()
            val = float(val)
            base = math.atan(val)
            solutions.append(str(base))
            solutions.append(str(base + math.pi))
            return solutions

        return ['No closed-form solution found']


class TrigonometrySpecialist(BDIAgent):
    """Specialist for trigonometric computations."""

    def __init__(
        self,
        agent_id: str = 'trigonometry_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        # Native trig engine
        self.trig_engine = NativeTrigEngine()

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.geometry.trigonometry',
                agent_id=agent_id,
                algorithm='native_trig',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='identities_equations_laws_polar'
            ))

        print(f"[{agent_id}] Trigonometry Specialist initialized (NO SYMPY)")
        print(f"  Capabilities: Identities, equations, law of sines/cosines, polar coords")

    def simplify_trig(self, expr_str: str) -> str:
        """Simplify trigonometric expression using native engine."""
        return NativeTrigEngine.simplify_trig_expr(expr_str)

    def expand_trig_expr(self, expr_str: str) -> str:
        """Expand trigonometric expression using identities (native)."""
        return NativeTrigEngine.expand_trig_expr(expr_str)

    def verify_identity(self, lhs: str, rhs: str) -> bool:
        """Verify if two trig expressions are identical (native numerical check)."""
        return NativeTrigEngine.verify_identity(lhs, rhs)

    def law_of_sines(self, **kwargs) -> Dict[str, Any]:
        """
        Apply law of sines: a/sin(A) = b/sin(B) = c/sin(C)
        Provide any 3 of: a, b, c, A, B, C (angles in radians)
        """
        known = {k: v for k, v in kwargs.items() if v is not None}
        result = dict(known)

        # If we have a side and its opposite angle, find the ratio
        ratio = None
        for side, angle in [('a', 'A'), ('b', 'B'), ('c', 'C')]:
            if side in known and angle in known:
                ratio = known[side] / math.sin(known[angle])
                break

        if ratio:
            for side, angle in [('a', 'A'), ('b', 'B'), ('c', 'C')]:
                if side not in result and angle in known:
                    result[side] = ratio * math.sin(known[angle])
                elif angle not in result and side in known:
                    result[angle] = math.asin(known[side] / ratio)

        return result

    def law_of_cosines(self, a: float = None, b: float = None, c: float = None,
                       C: float = None) -> Dict[str, Any]:
        """
        Apply law of cosines: c^2 = a^2 + b^2 - 2ab*cos(C)
        """
        result = {}
        if a and b and C:
            # Find c
            c_val = math.sqrt(a**2 + b**2 - 2*a*b*math.cos(C))
            result = {'a': a, 'b': b, 'C': C, 'c': c_val}
        elif a and b and c:
            # Find C
            cos_C = (a**2 + b**2 - c**2) / (2*a*b)
            C_val = math.acos(max(-1, min(1, cos_C)))
            result = {'a': a, 'b': b, 'c': c, 'C': C_val}
        return result

    def polar_to_rectangular(self, r: float, theta: float) -> Tuple[float, float]:
        """Convert polar (r, theta) to rectangular (x, y)."""
        return (r * math.cos(theta), r * math.sin(theta))

    def rectangular_to_polar(self, x: float, y: float) -> Tuple[float, float]:
        """Convert rectangular (x, y) to polar (r, theta)."""
        r = math.sqrt(x**2 + y**2)
        theta = math.atan2(y, x)
        return (r, theta)

    def solve_trig_equation(self, equation_str: str, variable: str = 'x') -> List[Any]:
        """Solve trigonometric equation using native engine."""
        return NativeTrigEngine.solve_trig_equation(equation_str, variable)

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a trigonometry task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'simplify')

        try:
            if operation == 'simplify':
                return {'result': self.simplify_trig(task['expr'])}
            elif operation == 'expand':
                return {'result': self.expand_trig_expr(task['expr'])}
            elif operation == 'verify_identity':
                return {'is_identity': self.verify_identity(task['lhs'], task['rhs'])}
            elif operation == 'law_of_sines':
                values = task.get('values', {k: v for k, v in task.items() if k != 'operation'})
                return self.law_of_sines(**values)
            elif operation == 'law_of_cosines':
                values = task.get('values', {k: v for k, v in task.items() if k != 'operation'})
                return self.law_of_cosines(**values)
            elif operation == 'polar_to_rect':
                return {'result': self.polar_to_rectangular(task['r'], task['theta'])}
            elif operation == 'rect_to_polar':
                return {'result': self.rectangular_to_polar(task['x'], task['y'])}
            elif operation == 'solve':
                return {'solutions': self.solve_trig_equation(task['equation'])}
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending trigonometry tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['math.geometry.trigonometry']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for trigonometry tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_trig_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute trigonometry computation via process()."""
        if not intention or not hasattr(intention, 'metadata'):
            return
        entry = intention.metadata.get('entry')
        if not entry:
            return
        action = intention.get_current_action()
        if action == 'accept_task':
            if self.blackboard:
                from symbo_agentic_reasoners.core.blackboard import EntryStatus
                self.blackboard.update_entry_status(entry.entry_id, EntryStatus.IN_PROGRESS)
            intention.advance()
        elif action == 'solve':
            task = entry.metadata if hasattr(entry, 'metadata') and entry.metadata else {}
            result = self.process(task)
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post_result':
            result = intention.metadata.get('result', {})
            if self.blackboard:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
                from symbo_agentic_reasoners.core.omdoc_schema import create_variable
                result_entry = create_entry(
                    entry_type=EntryType.RESULT,
                    content=create_variable(str(result)),
                    author_agent=self.agent_id,
                    status=EntryStatus.COMPLETED,
                    metadata={'result': result, 'result_str': str(result)}
                )
                self.blackboard.post(result_entry)
                self.blackboard.update_entry_status(entry.entry_id, EntryStatus.COMPLETED)
            del self.beliefs[f'task_{entry.entry_id}']
            intention.advance()

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
