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
PHASE 2 - SET THEORY AGENT (Tier 3)
====================================

Handles set-theoretic operations fundamental to discrete mathematics.

Operations:
- Basic set operations (union, intersection, difference, symmetric difference)
- Cartesian products
- Power sets
- Relations (reflexive, symmetric, transitive, equivalence, partial order)
- Functions (injective, surjective, bijective)
- Transitive closure
- Equivalence classes and partitions

NO SYMPY - All implementations are native Python.
"""

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, FrozenSet, Tuple, Set
import re
import ast
import logging

logger = logging.getLogger('symbo_agentic_reasoners.set_theory')


# =============================================================================
# NATIVE SET OPERATIONS (NO SYMPY)
# =============================================================================

class NativeSetOperations:
    """
    Pure Python set theory operations.
    Sets are represented as frozensets for immutability and hashability.
    Relations as sets of tuples.
    """

    @staticmethod
    def union(A: frozenset, B: frozenset) -> frozenset:
        """A U B = {x : x in A or x in B}"""
        return A | B

    @staticmethod
    def intersection(A: frozenset, B: frozenset) -> frozenset:
        """A n B = {x : x in A and x in B}"""
        return A & B

    @staticmethod
    def difference(A: frozenset, B: frozenset) -> frozenset:
        """A - B = {x : x in A and x not in B}"""
        return A - B

    @staticmethod
    def symmetric_difference(A: frozenset, B: frozenset) -> frozenset:
        """A delta B = (A - B) U (B - A)"""
        return A ^ B

    @staticmethod
    def cartesian_product(A: frozenset, B: frozenset) -> frozenset:
        """A x B = {(a, b) : a in A, b in B}"""
        return frozenset((a, b) for a in A for b in B)

    @staticmethod
    def power_set(A: frozenset) -> frozenset:
        """
        P(A) = set of all subsets of A
        |P(A)| = 2^|A|
        Uses binary representation for subset generation.
        """
        elements = list(A)
        n = len(elements)
        if n > 20:  # Safety limit
            raise ValueError("Set too large for power set (max 20 elements)")
        result = []
        for i in range(2**n):
            subset = frozenset(elements[j] for j in range(n) if (i >> j) & 1)
            result.append(subset)
        return frozenset(result)

    @staticmethod
    def is_subset(A: frozenset, B: frozenset) -> bool:
        """A subseteq B iff every element of A is in B"""
        return A <= B

    @staticmethod
    def is_proper_subset(A: frozenset, B: frozenset) -> bool:
        """A subset B iff A subseteq B and A != B"""
        return A < B

    @staticmethod
    def cardinality(A: frozenset) -> int:
        """|A| = number of elements in A"""
        return len(A)


class RelationOperations:
    """Operations on relations (sets of ordered pairs)."""

    @staticmethod
    def domain(R: frozenset) -> frozenset:
        """dom(R) = {a : (a,b) in R for some b}"""
        return frozenset(a for a, _ in R)

    @staticmethod
    def range_set(R: frozenset) -> frozenset:
        """ran(R) = {b : (a,b) in R for some a}"""
        return frozenset(b for _, b in R)

    @staticmethod
    def compose(R: frozenset, S: frozenset) -> frozenset:
        """
        R o S = {(a,c) : exists b such that (a,b) in S and (b,c) in R}
        Note: Composition reads right-to-left
        """
        S_dict: Dict[Any, Set] = {}
        for a, b in S:
            if a not in S_dict:
                S_dict[a] = set()
            S_dict[a].add(b)

        result = set()
        for b, c in R:
            if b in S_dict:
                for a in S_dict[b]:
                    result.add((a, c))
        return frozenset(result)

    @staticmethod
    def inverse(R: frozenset) -> frozenset:
        """R^-1 = {(b,a) : (a,b) in R}"""
        return frozenset((b, a) for a, b in R)

    @staticmethod
    def is_reflexive(R: frozenset, A: frozenset) -> bool:
        """R is reflexive on A iff (a,a) in R for all a in A"""
        return all((a, a) in R for a in A)

    @staticmethod
    def is_symmetric(R: frozenset) -> bool:
        """R is symmetric iff (a,b) in R implies (b,a) in R"""
        return all((b, a) in R for a, b in R)

    @staticmethod
    def is_antisymmetric(R: frozenset) -> bool:
        """R is antisymmetric iff (a,b) in R and (b,a) in R implies a = b"""
        for a, b in R:
            if a != b and (b, a) in R:
                return False
        return True

    @staticmethod
    def is_transitive(R: frozenset) -> bool:
        """R is transitive iff (a,b) in R and (b,c) in R implies (a,c) in R"""
        R_dict: Dict[Any, Set] = {}
        for a, b in R:
            if a not in R_dict:
                R_dict[a] = set()
            R_dict[a].add(b)

        for a, b in R:
            if b in R_dict:
                for c in R_dict[b]:
                    if (a, c) not in R:
                        return False
        return True

    @staticmethod
    def is_equivalence_relation(R: frozenset, A: frozenset) -> bool:
        """Equivalence relation = reflexive + symmetric + transitive"""
        return (RelationOperations.is_reflexive(R, A) and
                RelationOperations.is_symmetric(R) and
                RelationOperations.is_transitive(R))

    @staticmethod
    def is_partial_order(R: frozenset, A: frozenset) -> bool:
        """Partial order = reflexive + antisymmetric + transitive"""
        return (RelationOperations.is_reflexive(R, A) and
                RelationOperations.is_antisymmetric(R) and
                RelationOperations.is_transitive(R))

    @staticmethod
    def equivalence_classes(R: frozenset, A: frozenset) -> frozenset:
        """
        Compute equivalence classes for equivalence relation R on A.
        Returns partition of A.
        """
        classes = []
        remaining = set(A)

        while remaining:
            a = remaining.pop()
            eq_class = {a}
            for b in list(remaining):
                if (a, b) in R:
                    eq_class.add(b)
                    remaining.remove(b)
            classes.append(frozenset(eq_class))

        return frozenset(classes)

    @staticmethod
    def transitive_closure(R: frozenset) -> frozenset:
        """
        Compute R+ = R U R^2 U R^3 U ...
        Uses Warshall's algorithm.
        """
        elements = set()
        for a, b in R:
            elements.add(a)
            elements.add(b)
        elements_list = list(elements)
        n = len(elements_list)
        idx = {e: i for i, e in enumerate(elements_list)}

        closure = [[False] * n for _ in range(n)]
        for a, b in R:
            closure[idx[a]][idx[b]] = True

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    closure[i][j] = closure[i][j] or (closure[i][k] and closure[k][j])

        result = set()
        for i in range(n):
            for j in range(n):
                if closure[i][j]:
                    result.add((elements_list[i], elements_list[j]))

        return frozenset(result)


class FunctionOperations:
    """
    Operations on functions (special relations where each domain element
    maps to exactly one range element).
    """

    @staticmethod
    def is_function(R: frozenset, A: frozenset, B: frozenset) -> bool:
        """Check if R is a function from A to B"""
        domain_check = RelationOperations.domain(R) == A

        seen: Dict[Any, Any] = {}
        for a, b in R:
            if a in seen:
                if seen[a] != b:
                    return False
            seen[a] = b

        for _, b in R:
            if b not in B:
                return False

        return domain_check

    @staticmethod
    def is_injective(R: frozenset) -> bool:
        """f is injective (one-to-one) iff f(a) = f(b) implies a = b"""
        seen_outputs = set()
        for _, b in R:
            if b in seen_outputs:
                return False
            seen_outputs.add(b)
        return True

    @staticmethod
    def is_surjective(R: frozenset, B: frozenset) -> bool:
        """f is surjective (onto) iff every b in B has preimage"""
        range_r = RelationOperations.range_set(R)
        return range_r == B

    @staticmethod
    def is_bijective(R: frozenset, A: frozenset, B: frozenset) -> bool:
        """f is bijective iff injective and surjective"""
        return (FunctionOperations.is_injective(R) and
                FunctionOperations.is_surjective(R, B))


# =============================================================================
# SET THEORY AGENT (Tier 3)
# =============================================================================

class SetTheoryAgent(BDIAgent):
    """
    Set Theory Specialist - Tier 3

    Handles:
    - Set operations (union, intersection, difference, symmetric difference)
    - Cartesian products
    - Power sets
    - Relations (reflexive, symmetric, transitive, equivalence, partial order)
    - Functions (injective, surjective, bijective)
    - Transitive closure
    - Equivalence classes and partitions
    """

    def __init__(
        self,
        agent_id: str = 'set_theory_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.discrete.sets',
                agent_id=agent_id,
                algorithm='native_set_ops',
                cost='low',
                instance=self,
                tier='3',
                operations='union_intersection_powerset_relations_functions'
            ))

        logger.info(f"[{agent_id}] Set Theory Agent initialized")
        logger.info(f"  Algorithm: Native set operations")
        logger.info(f"  Operations: Sets, relations, functions")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for set theory tasks."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus

            tasks = self.blackboard.query_entries(
                tags=['sets', 'set_theory'],
                status=EntryStatus.PENDING
            )

            delegated = self.blackboard.query_entries(
                entry_type=EntryType.TASK,
                status=EntryStatus.PENDING
            )

            for task in delegated:
                if hasattr(task, 'metadata') and task.metadata:
                    if task.metadata.get('assigned_agent') == self.agent_id and task not in tasks:
                        tasks.append(task)

            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if self.has_belief(f'claimed_task_{task.entry_id}'):
                    continue
                if not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')

        except Exception as e:
            logger.error(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create computation plans for set theory tasks."""
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

            operation = self._determine_operation(raw_input)

            steps = ['claim_task', 'parse_sets', f'compute_{operation}', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'set_{operation}_{task_id}',
                steps=steps,
                target_desire='solve_set_theory',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation, 'raw_input': raw_input}
            )
            new_intentions.append(intention)

        return new_intentions

    def _determine_operation(self, raw_input: str) -> str:
        """Determine which set operation to perform."""
        if 'union' in raw_input or '∪' in raw_input:
            return 'union'
        elif 'intersection' in raw_input or '∩' in raw_input:
            return 'intersection'
        elif 'difference' in raw_input and 'symmetric' in raw_input:
            return 'symmetric_difference'
        elif 'difference' in raw_input or '-' in raw_input:
            return 'difference'
        elif 'cartesian' in raw_input or 'product' in raw_input or '×' in raw_input:
            return 'cartesian_product'
        elif 'power' in raw_input:
            return 'power_set'
        elif 'subset' in raw_input:
            return 'subset_check'
        elif 'equivalence' in raw_input and 'class' in raw_input:
            return 'equivalence_classes'
        elif 'equivalence' in raw_input:
            return 'is_equivalence'
        elif 'partial order' in raw_input:
            return 'is_partial_order'
        elif 'reflexive' in raw_input:
            return 'is_reflexive'
        elif 'symmetric' in raw_input:
            return 'is_symmetric'
        elif 'transitive' in raw_input and 'closure' in raw_input:
            return 'transitive_closure'
        elif 'transitive' in raw_input:
            return 'is_transitive'
        elif 'injective' in raw_input or 'one-to-one' in raw_input:
            return 'is_injective'
        elif 'surjective' in raw_input or 'onto' in raw_input:
            return 'is_surjective'
        elif 'bijective' in raw_input:
            return 'is_bijective'
        elif 'domain' in raw_input:
            return 'domain'
        elif 'range' in raw_input:
            return 'range'
        elif 'inverse' in raw_input:
            return 'inverse'
        elif 'compose' in raw_input:
            return 'compose'
        else:
            return 'union'  # Default

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute set theory computation (native implementations)."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')

        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()

            elif action == 'parse_sets':
                raw = intention.metadata.get('raw_input', '')
                sets = self._parse_sets(raw)
                intention.metadata['sets'] = sets
                intention.advance()

            elif action.startswith('compute_'):
                operation = action.replace('compute_', '')
                sets = intention.metadata.get('sets', [])
                result = self._compute_operation(operation, sets)
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()

            elif action == 'verify_result':
                intention.metadata['verified'] = intention.metadata.get('result') is not None
                intention.advance()

            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    result_str = self._format_result(result)
                    entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(result_str),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['sets', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'result': result_str, 'result_str': result_str}
                    )
                    self.blackboard.post(entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.tasks_executed += 1
                intention.advance()

            else:
                intention.advance()

        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()

    def _parse_sets(self, raw: str) -> List[frozenset]:
        """Parse sets from input string."""
        sets = []
        set_pattern = r'\{([^}]*)\}'
        matches = re.findall(set_pattern, raw)

        for match in matches:
            try:
                elements = [x.strip() for x in match.split(',') if x.strip()]
                parsed_elements = []
                for elem in elements:
                    try:
                        parsed_elements.append(int(elem))
                    except ValueError:
                        try:
                            parsed_elements.append(float(elem))
                        except ValueError:
                            parsed_elements.append(elem)
                sets.append(frozenset(parsed_elements))
            except Exception:
                continue

        return sets

    def _compute_operation(self, operation: str, sets: List[frozenset]) -> Any:
        """Execute the specified set operation."""
        if not sets:
            return frozenset()

        A = sets[0] if len(sets) > 0 else frozenset()
        B = sets[1] if len(sets) > 1 else frozenset()

        if operation == 'union':
            return NativeSetOperations.union(A, B)
        elif operation == 'intersection':
            return NativeSetOperations.intersection(A, B)
        elif operation == 'difference':
            return NativeSetOperations.difference(A, B)
        elif operation == 'symmetric_difference':
            return NativeSetOperations.symmetric_difference(A, B)
        elif operation == 'cartesian_product':
            return NativeSetOperations.cartesian_product(A, B)
        elif operation == 'power_set':
            return NativeSetOperations.power_set(A)
        elif operation == 'subset_check':
            return NativeSetOperations.is_subset(A, B)
        elif operation == 'is_reflexive':
            R = self._parse_relation(sets)
            return RelationOperations.is_reflexive(R, A)
        elif operation == 'is_symmetric':
            R = self._parse_relation(sets)
            return RelationOperations.is_symmetric(R)
        elif operation == 'is_transitive':
            R = self._parse_relation(sets)
            return RelationOperations.is_transitive(R)
        elif operation == 'is_equivalence':
            R = self._parse_relation(sets)
            return RelationOperations.is_equivalence_relation(R, A)
        elif operation == 'is_partial_order':
            R = self._parse_relation(sets)
            return RelationOperations.is_partial_order(R, A)
        elif operation == 'transitive_closure':
            R = self._parse_relation(sets)
            return RelationOperations.transitive_closure(R)
        elif operation == 'equivalence_classes':
            R = self._parse_relation(sets)
            return RelationOperations.equivalence_classes(R, A)
        elif operation == 'domain':
            R = self._parse_relation(sets)
            return RelationOperations.domain(R)
        elif operation == 'range':
            R = self._parse_relation(sets)
            return RelationOperations.range_set(R)
        elif operation == 'inverse':
            R = self._parse_relation(sets)
            return RelationOperations.inverse(R)
        elif operation == 'compose':
            R = self._parse_relation([sets[0]] if sets else [])
            S = self._parse_relation([sets[1]] if len(sets) > 1 else [])
            return RelationOperations.compose(R, S)
        elif operation == 'is_injective':
            R = self._parse_relation(sets)
            return FunctionOperations.is_injective(R)
        elif operation == 'is_surjective':
            R = self._parse_relation(sets)
            return FunctionOperations.is_surjective(R, B)
        elif operation == 'is_bijective':
            R = self._parse_relation(sets)
            return FunctionOperations.is_bijective(R, A, B)
        else:
            return A

    def _parse_relation(self, sets: List[frozenset]) -> frozenset:
        """Convert set of pairs to relation."""
        if not sets:
            return frozenset()

        result = set()
        for s in sets:
            for elem in s:
                if isinstance(elem, tuple) and len(elem) == 2:
                    result.add(elem)
        return frozenset(result)

    def _format_result(self, result: Any) -> str:
        """Format result for output."""
        if isinstance(result, frozenset):
            if all(isinstance(x, frozenset) for x in result):
                inner = ', '.join('{' + ', '.join(str(e) for e in s) + '}' for s in result)
                return '{' + inner + '}'
            elements = sorted([str(x) for x in result])
            return '{' + ', '.join(elements) + '}'
        elif isinstance(result, bool):
            return str(result)
        else:
            return str(result)

    def process(self, task_entry) -> Any:
        """Direct invocation entry point for supervisor delegation."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()

            operation = self._determine_operation(raw_input)
            sets = self._parse_sets(raw_input)
            result = self._compute_operation(operation, sets)
            result_str = self._format_result(result)

            self.tasks_executed += 1

            return create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(result_str),
                author_agent=self.agent_id,
                conversation_id=getattr(task_entry, 'conversation_id', 'direct'),
                tags=['sets', 'result'],
                status=EntryStatus.COMPLETED,
                metadata={'result': result_str, 'result_str': result_str}
            )

        except Exception as e:
            logger.error(f"[{self.agent_id}] process error: {e}")
            return create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=f"Error: {e}",
                author_agent=self.agent_id,
                conversation_id=getattr(task_entry, 'conversation_id', 'direct'),
                tags=['sets', 'error'],
                status=EntryStatus.FAILED,
                metadata={'error': str(e)}
            )

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed})
        return stats
