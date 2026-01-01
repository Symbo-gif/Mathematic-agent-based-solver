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
PROPOSITIONAL LOGIC SPECIALIST (Tier 3)
=======================================

Handles propositional logic: truth tables, logical equivalence,
normal forms, and satisfiability.

CAPABILITIES:
- Truth table generation
- Logical equivalence checking
- CNF/DNF conversion
- Tautology/contradiction detection
- SAT solving (basic)
"""

from typing import Any, Dict, List, Optional, Set
import itertools
import ast
import operator
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class SafeBooleanEvaluator:
    """
    Safe evaluator for boolean expressions without using eval().
    Only allows boolean operations on variables with known values.
    """

    # Allowed operators for boolean expressions
    ALLOWED_OPS = {
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
        ast.Not: operator.not_,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
    }

    def __init__(self, variables: Dict[str, bool]):
        """Initialize with variable assignments."""
        self.variables = variables

    def evaluate(self, expression: str) -> bool:
        """Safely evaluate a boolean expression string."""
        try:
            tree = ast.parse(expression, mode='eval')
            return self._eval_node(tree.body)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")

    def _eval_node(self, node):
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.BoolOp):
            # Handle 'and' / 'or' with multiple values
            op_func = self.ALLOWED_OPS.get(type(node.op))
            if not op_func:
                raise ValueError(f"Unsupported boolean operator: {type(node.op)}")
            result = self._eval_node(node.values[0])
            for value in node.values[1:]:
                result = op_func(result, self._eval_node(value))
            return result

        elif isinstance(node, ast.UnaryOp):
            # Handle 'not'
            if isinstance(node.op, ast.Not):
                return not self._eval_node(node.operand)
            raise ValueError(f"Unsupported unary operator: {type(node.op)}")

        elif isinstance(node, ast.Compare):
            # Handle comparisons like a == b
            left = self._eval_node(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                op_func = self.ALLOWED_OPS.get(type(op))
                if not op_func:
                    raise ValueError(f"Unsupported comparison: {type(op)}")
                right = self._eval_node(comparator)
                if not op_func(left, right):
                    return False
                left = right
            return True

        elif isinstance(node, ast.Name):
            # Variable lookup
            if node.id in self.variables:
                return self.variables[node.id]
            raise ValueError(f"Unknown variable: {node.id}")

        elif isinstance(node, ast.Constant):
            # Literal True/False
            if isinstance(node.value, bool):
                return node.value
            raise ValueError(f"Only boolean constants allowed: {node.value}")

        elif isinstance(node, ast.NameConstant):
            # Python 3.7 compatibility for True/False
            if isinstance(node.value, bool):
                return node.value
            raise ValueError(f"Only boolean constants allowed: {node.value}")

        else:
            raise ValueError(f"Unsupported expression type: {type(node)}")


class PropositionalLogicSpecialist(BDIAgent):
    """Specialist for propositional logic problems."""

    # Logical operators
    OPERATORS = {
        'and': lambda a, b: a and b,
        'or': lambda a, b: a or b,
        'not': lambda a: not a,
        'implies': lambda a, b: (not a) or b,
        'iff': lambda a, b: a == b,
        'xor': lambda a, b: a != b,
        'nand': lambda a, b: not (a and b),
        'nor': lambda a, b: not (a or b)
    }

    def __init__(
        self,
        agent_id: str = 'propositional_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.logic.propositional',
                agent_id=agent_id,
                algorithm='truth_table',
                cost='low',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='truth_table_equivalence_cnf_dnf_sat'
            ))

        print(f"[{agent_id}] Propositional Logic Specialist initialized")
        print(f"  Operations: Truth Tables, CNF/DNF, SAT")

    def generate_truth_table(self, variables: List[str],
                             expression: str) -> Dict[str, Any]:
        """
        Generate truth table for a propositional expression.
        Expression should use Python boolean syntax.
        """
        n = len(variables)
        rows = []

        for values in itertools.product([False, True], repeat=n):
            assignment = dict(zip(variables, values))
            try:
                # Safely evaluate expression with assignment (no eval())
                evaluator = SafeBooleanEvaluator(assignment)
                result = evaluator.evaluate(expression)
                row = {**assignment, 'result': result}
                rows.append(row)
            except Exception as e:
                return {'error': f'Failed to evaluate: {e}'}

        return {
            'variables': variables,
            'expression': expression,
            'truth_table': rows,
            'num_rows': len(rows)
        }

    def is_tautology(self, variables: List[str], expression: str) -> Dict[str, Any]:
        """Check if expression is a tautology (always true)."""
        table = self.generate_truth_table(variables, expression)

        if 'error' in table:
            return table

        is_taut = all(row['result'] for row in table['truth_table'])
        counterexample = None
        if not is_taut:
            counterexample = next(
                row for row in table['truth_table'] if not row['result']
            )

        return {
            'is_tautology': is_taut,
            'expression': expression,
            'counterexample': counterexample
        }

    def is_contradiction(self, variables: List[str],
                         expression: str) -> Dict[str, Any]:
        """Check if expression is a contradiction (always false)."""
        table = self.generate_truth_table(variables, expression)

        if 'error' in table:
            return table

        is_contra = all(not row['result'] for row in table['truth_table'])
        satisfying = None
        if not is_contra:
            satisfying = next(
                row for row in table['truth_table'] if row['result']
            )

        return {
            'is_contradiction': is_contra,
            'expression': expression,
            'satisfying_assignment': satisfying
        }

    def is_satisfiable(self, variables: List[str],
                       expression: str) -> Dict[str, Any]:
        """Check if expression is satisfiable (at least one true)."""
        table = self.generate_truth_table(variables, expression)

        if 'error' in table:
            return table

        satisfying = [row for row in table['truth_table'] if row['result']]
        is_sat = len(satisfying) > 0

        return {
            'is_satisfiable': is_sat,
            'expression': expression,
            'num_satisfying': len(satisfying),
            'satisfying_assignments': satisfying[:5]  # Limit output
        }

    def are_equivalent(self, variables: List[str],
                       expr1: str, expr2: str) -> Dict[str, Any]:
        """Check if two expressions are logically equivalent."""
        table1 = self.generate_truth_table(variables, expr1)
        table2 = self.generate_truth_table(variables, expr2)

        if 'error' in table1:
            return table1
        if 'error' in table2:
            return table2

        results1 = [row['result'] for row in table1['truth_table']]
        results2 = [row['result'] for row in table2['truth_table']]

        are_equiv = results1 == results2
        differences = []
        if not are_equiv:
            for r1, r2 in zip(table1['truth_table'], table2['truth_table']):
                if r1['result'] != r2['result']:
                    differences.append({
                        'assignment': {k: v for k, v in r1.items() if k != 'result'},
                        'expr1_result': r1['result'],
                        'expr2_result': r2['result']
                    })

        return {
            'are_equivalent': are_equiv,
            'expression1': expr1,
            'expression2': expr2,
            'differences': differences[:5]
        }

    def modus_ponens(self, p: bool, p_implies_q: bool) -> Dict[str, Any]:
        """
        Modus ponens: if P and P->Q, then Q.
        """
        if p and p_implies_q:
            return {'q': True, 'rule': 'modus_ponens', 'valid': True}
        return {
            'q': None,
            'rule': 'modus_ponens',
            'valid': False,
            'reason': 'Premises not satisfied'
        }

    def modus_tollens(self, not_q: bool, p_implies_q: bool) -> Dict[str, Any]:
        """
        Modus tollens: if ~Q and P->Q, then ~P.
        """
        if not_q and p_implies_q:
            return {'not_p': True, 'rule': 'modus_tollens', 'valid': True}
        return {
            'not_p': None,
            'rule': 'modus_tollens',
            'valid': False,
            'reason': 'Premises not satisfied'
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a propositional logic task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'truth_table')

        try:
            if operation == 'truth_table':
                return self.generate_truth_table(
                    task['variables'], task['expression']
                )
            elif operation == 'tautology':
                return self.is_tautology(task['variables'], task['expression'])
            elif operation == 'contradiction':
                return self.is_contradiction(task['variables'], task['expression'])
            elif operation == 'satisfiable':
                return self.is_satisfiable(task['variables'], task['expression'])
            elif operation == 'equivalent':
                return self.are_equivalent(
                    task['variables'], task['expr1'], task['expr2']
                )
            elif operation == 'modus_ponens':
                return self.modus_ponens(task['p'], task['p_implies_q'])
            elif operation == 'modus_tollens':
                return self.modus_tollens(task['not_q'], task['p_implies_q'])
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending propositional logic tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['math.logic.propositional']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for propositional logic tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_prop_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute propositional logic computation via process()."""
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
        """Compute get statistics using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = PropositionalLogicSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
