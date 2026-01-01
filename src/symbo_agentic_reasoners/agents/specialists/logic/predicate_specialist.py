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
PREDICATE LOGIC SPECIALIST (Tier 3)
===================================

Handles first-order predicate logic: quantifiers, predicates,
substitution, and basic inference.

CAPABILITIES:
- Universal and existential quantification
- Predicate evaluation
- Substitution
- Prenex normal form
- Basic unification
"""

from typing import Any, Dict, List, Optional, Set, Callable
import ast
import operator
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class SafePredicateEvaluator:
    """
    Safe evaluator for predicate expressions without using eval().
    Parses lambda expressions and only allows safe mathematical operations.
    """

    # Allowed binary operators
    BINOPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
    }

    # Allowed unary operators
    UNARYOPS = {
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Not: operator.not_,
    }

    # Allowed safe functions
    SAFE_FUNCS = {
        'abs': abs,
        'min': min,
        'max': max,
        'len': len,
        'sum': sum,
        'round': round,
        'int': int,
        'float': float,
        'bool': bool,
        'str': str,
    }

    @classmethod
    def parse_predicate(cls, predicate_str: str) -> Callable:
        """
        Parse a predicate string (lambda expression) into a safe callable.
        Example: "lambda x: x > 0" -> callable
        """
        try:
            tree = ast.parse(predicate_str, mode='eval')
            if not isinstance(tree.body, ast.Lambda):
                raise ValueError("Predicate must be a lambda expression")

            lambda_node = tree.body
            param_names = [arg.arg for arg in lambda_node.args.args]

            def safe_predicate(*args):
                """Perform safe predicate operation.

                Args:
                No arguments

                Returns:
                Result of the operation

                Example:
                >>> result = obj.safe_predicate(...)
                """
                if len(args) != len(param_names):
                    raise ValueError(f"Expected {len(param_names)} args, got {len(args)}")
                variables = dict(zip(param_names, args))
                return cls._eval_node(lambda_node.body, variables)

            return safe_predicate
        except SyntaxError as e:
            raise ValueError(f"Invalid predicate syntax: {e}")

    @classmethod
    def _eval_node(cls, node, variables: Dict):
        """Recursively evaluate AST nodes safely."""
        if isinstance(node, ast.Constant):
            return node.value

        # Python 3.7 compatibility (ast.Num/Str/NameConstant deprecated in 3.8, removed in 3.12)
        if hasattr(ast, 'Num') and isinstance(node, ast.Num):
            return node.n

        if hasattr(ast, 'Str') and isinstance(node, ast.Str):
            return node.s

        if hasattr(ast, 'NameConstant') and isinstance(node, ast.NameConstant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]
            if node.id in ('True', 'False', 'None'):
                return {'True': True, 'False': False, 'None': None}[node.id]
            raise ValueError(f"Unknown variable: {node.id}")

        if isinstance(node, ast.BinOp):
            op_func = cls.BINOPS.get(type(node.op))
            if not op_func:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            left = cls._eval_node(node.left, variables)
            right = cls._eval_node(node.right, variables)
            return op_func(left, right)

        if isinstance(node, ast.UnaryOp):
            op_func = cls.UNARYOPS.get(type(node.op))
            if not op_func:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op_func(cls._eval_node(node.operand, variables))

        if isinstance(node, ast.Compare):
            left = cls._eval_node(node.left, variables)
            for op, comparator in zip(node.ops, node.comparators):
                op_func = cls.BINOPS.get(type(op))
                if not op_func:
                    raise ValueError(f"Unsupported comparison: {type(op).__name__}")
                right = cls._eval_node(comparator, variables)
                if not op_func(left, right):
                    return False
                left = right
            return True

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(cls._eval_node(v, variables) for v in node.values)
            elif isinstance(node.op, ast.Or):
                return any(cls._eval_node(v, variables) for v in node.values)
            raise ValueError(f"Unsupported boolean operator: {type(node.op).__name__}")

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in cls.SAFE_FUNCS:
                    args = [cls._eval_node(arg, variables) for arg in node.args]
                    return cls.SAFE_FUNCS[func_name](*args)
            raise ValueError(f"Unsupported function call")

        if isinstance(node, ast.IfExp):
            test = cls._eval_node(node.test, variables)
            if test:
                return cls._eval_node(node.body, variables)
            return cls._eval_node(node.orelse, variables)

        if isinstance(node, ast.List):
            return [cls._eval_node(elt, variables) for elt in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(cls._eval_node(elt, variables) for elt in node.elts)

        if isinstance(node, ast.Subscript):
            value = cls._eval_node(node.value, variables)
            if isinstance(node.slice, ast.Index):  # Python 3.8-
                idx = cls._eval_node(node.slice.value, variables)
            else:  # Python 3.9+
                idx = cls._eval_node(node.slice, variables)
            return value[idx]

        raise ValueError(f"Unsupported expression type: {type(node).__name__}")


class PredicateLogicSpecialist(BDIAgent):
    """Specialist for predicate logic problems."""

    def __init__(
        self,
        agent_id: str = 'predicate_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.logic.predicate',
                agent_id=agent_id,
                algorithm='first_order_logic',
                cost='medium',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='quantifiers_predicates_unification'
            ))

        print(f"[{agent_id}] Predicate Logic Specialist initialized")
        print(f"  Operations: Quantifiers, Predicates, Unification")

    def universal_quantification(self, domain: List[Any],
                                  predicate: Callable[[Any], bool]) -> Dict[str, Any]:
        """
        Check if predicate holds for all elements in domain.
        forall x in domain: P(x)
        """
        all_true = True
        counterexamples = []

        for element in domain:
            if not predicate(element):
                all_true = False
                counterexamples.append(element)

        return {
            'forall': all_true,
            'domain_size': len(domain),
            'counterexamples': counterexamples[:5]
        }

    def existential_quantification(self, domain: List[Any],
                                    predicate: Callable[[Any], bool]) -> Dict[str, Any]:
        """
        Check if predicate holds for at least one element.
        exists x in domain: P(x)
        """
        witnesses = []

        for element in domain:
            if predicate(element):
                witnesses.append(element)

        return {
            'exists': len(witnesses) > 0,
            'domain_size': len(domain),
            'witnesses': witnesses[:5],
            'count': len(witnesses)
        }

    def count_quantification(self, domain: List[Any],
                              predicate: Callable[[Any], bool],
                              count: int) -> Dict[str, Any]:
        """
        Check if exactly 'count' elements satisfy predicate.
        """
        satisfying = [x for x in domain if predicate(x)]

        return {
            'exactly_n': len(satisfying) == count,
            'expected': count,
            'actual': len(satisfying),
            'satisfying_elements': satisfying[:10]
        }

    def evaluate_predicate_over_domain(self, domain: List[Any],
                                        predicate: Callable[[Any], bool]) -> Dict[str, Any]:
        """
        Evaluate a predicate over all elements in a domain.
        """
        results = {}
        true_count = 0

        for element in domain:
            result = predicate(element)
            results[str(element)] = result
            if result:
                true_count += 1

        return {
            'results': results,
            'true_count': true_count,
            'false_count': len(domain) - true_count,
            'truth_ratio': true_count / len(domain) if domain else 0
        }

    def substitution(self, expression: str, variable: str,
                     value: str) -> Dict[str, Any]:
        """
        Substitute a value for a variable in an expression.
        """
        result = expression.replace(variable, value)
        return {
            'original': expression,
            'variable': variable,
            'value': value,
            """Perform unify terms operation.

            Args:
            t1: Description needed
            t2: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.unify_terms(...)
            """
            'result': result
        }

    def unify(self, term1: Dict, term2: Dict) -> Dict[str, Any]:
        """
        Basic unification of two terms.
        Terms are represented as dicts with 'type' and 'value' or 'args'.
        """
        substitutions = {}

        def unify_terms(t1, t2):
            """Unify two first-order logic terms using Robinson's unification algorithm."""
            if t1 == t2:
                return True

            # Variable unification
            if isinstance(t1, dict) and t1.get('type') == 'variable':
                substitutions[t1['name']] = t2
                return True
            if isinstance(t2, dict) and t2.get('type') == 'variable':
                substitutions[t2['name']] = t1
                return True

            # Function unification
            if (isinstance(t1, dict) and isinstance(t2, dict) and
                t1.get('type') == 'function' and t2.get('type') == 'function'):
                if t1['name'] != t2['name']:
                    return False
                if len(t1.get('args', [])) != len(t2.get('args', [])):
                    return False
                for a1, a2 in zip(t1['args'], t2['args']):
                    if not unify_terms(a1, a2):
                        return False
                return True

            return False

        success = unify_terms(term1, term2)

        return {
            'unifiable': success,
            'substitutions': substitutions if success else None,
            'term1': term1,
            'term2': term2
        }

    def negate_quantifier(self, quantifier: str, predicate: str,
                          variable: str) -> Dict[str, Any]:
        """
        Apply negation to a quantified statement.
        ~(forall x: P(x)) = exists x: ~P(x)
        ~(exists x: P(x)) = forall x: ~P(x)
        """
        if quantifier.lower() == 'forall':
            return {
                'original': f'forall {variable}: {predicate}',
                'negated': f'exists {variable}: ~({predicate})',
                'rule': 'quantifier_negation'
            }
        elif quantifier.lower() == 'exists':
            return {
                'original': f'exists {variable}: {predicate}',
                'negated': f'forall {variable}: ~({predicate})',
                'rule': 'quantifier_negation'
            }
        else:
            return {'error': f'Unknown quantifier: {quantifier}'}

    def _get_predicate(self, predicate_input) -> Callable:
        """
        Convert predicate input to a safe callable.
        Accepts either a lambda string or an already-callable predicate.
        """
        if callable(predicate_input):
            return predicate_input
        if isinstance(predicate_input, str):
            return SafePredicateEvaluator.parse_predicate(predicate_input)
        raise ValueError(f"Predicate must be a callable or lambda string, got {type(predicate_input)}")

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a predicate logic task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'forall')

        try:
            if operation == 'forall':
                predicate = self._get_predicate(task['predicate'])
                return self.universal_quantification(task['domain'], predicate)
            elif operation == 'exists':
                predicate = self._get_predicate(task['predicate'])
                return self.existential_quantification(task['domain'], predicate)
            elif operation == 'count':
                predicate = self._get_predicate(task['predicate'])
                return self.count_quantification(
                    task['domain'], predicate, task['count']
                )
            elif operation == 'evaluate':
                predicate = self._get_predicate(task['predicate'])
                return self.evaluate_predicate_over_domain(
                    task['domain'], predicate
                )
            elif operation == 'substitute':
                return self.substitution(
                    task['expression'], task['variable'], task['value']
                )
            elif operation == 'unify':
                return self.unify(task['term1'], task['term2'])
            elif operation == 'negate_quantifier':
                return self.negate_quantifier(
                    task['quantifier'], task['predicate'], task['variable']
                )
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending predicate logic tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['math.logic.predicate']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for predicate logic tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_predicate_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute predicate logic computation via process()."""
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
        >>> specialist = PredicateLogicSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
