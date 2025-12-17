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
PHASE 2 - BOOLEAN ALGEBRA AGENT (Tier 3)
=========================================

Extends logic capabilities with Boolean algebra and minimization.

Capabilities:
- Boolean operations (AND, OR, NOT, XOR, NAND, NOR, etc.)
- Normal forms (DNF, CNF)
- Quine-McCluskey minimization
- Karnaugh map generation
- Truth table generation
- Prime implicant identification

NO SYMPY - All implementations are native Python.
"""

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, Set, Tuple, FrozenSet
from itertools import combinations
import re
import logging

logger = logging.getLogger('symbo_agentic_reasoners.boolean_algebra')


# =============================================================================
# NATIVE BOOLEAN ALGEBRA (NO SYMPY)
# =============================================================================

class BooleanAlgebra:
    """Native Boolean algebra operations."""

    @staticmethod
    def AND(a: bool, b: bool) -> bool:
        return a and b

    @staticmethod
    def OR(a: bool, b: bool) -> bool:
        return a or b

    @staticmethod
    def NOT(a: bool) -> bool:
        return not a

    @staticmethod
    def XOR(a: bool, b: bool) -> bool:
        return a != b

    @staticmethod
    def NAND(a: bool, b: bool) -> bool:
        return not (a and b)

    @staticmethod
    def NOR(a: bool, b: bool) -> bool:
        return not (a or b)

    @staticmethod
    def IMPLIES(a: bool, b: bool) -> bool:
        return (not a) or b

    @staticmethod
    def IFF(a: bool, b: bool) -> bool:
        return a == b


class NormalForms:
    """Conversion to and from normal forms."""

    @staticmethod
    def to_minterm(term: int, n_vars: int) -> str:
        """
        Convert minterm number to expression.
        Minterm m_i = conjunction where variable is complemented if bit is 0.
        Example: minterm 5 with 3 vars (ABC) = 101 = A AND NOT(B) AND C
        """
        vars_list = [chr(ord('A') + i) for i in range(n_vars)]
        result = []
        for i in range(n_vars):
            bit = (term >> (n_vars - 1 - i)) & 1
            if bit:
                result.append(vars_list[i])
            else:
                result.append(f"{vars_list[i]}'")
        return ''.join(result)

    @staticmethod
    def to_maxterm(term: int, n_vars: int) -> str:
        """
        Convert maxterm number to expression.
        Maxterm M_i = disjunction where variable is complemented if bit is 1.
        """
        vars_list = [chr(ord('A') + i) for i in range(n_vars)]
        result = []
        for i in range(n_vars):
            bit = (term >> (n_vars - 1 - i)) & 1
            if bit:
                result.append(f"{vars_list[i]}'")
            else:
                result.append(vars_list[i])
        return ' + '.join(result)

    @staticmethod
    def truth_table_to_dnf(minterms: List[int], n_vars: int) -> str:
        """Convert list of minterms (where function = 1) to DNF."""
        if not minterms:
            return "0"
        terms = [NormalForms.to_minterm(m, n_vars) for m in minterms]
        return ' + '.join(terms)

    @staticmethod
    def truth_table_to_cnf(maxterms: List[int], n_vars: int) -> str:
        """Convert list of maxterms (where function = 0) to CNF."""
        if not maxterms:
            return "1"
        terms = [f"({NormalForms.to_maxterm(m, n_vars)})" for m in maxterms]
        return ' * '.join(terms)


class QuineMcCluskey:
    """
    Quine-McCluskey algorithm for Boolean function minimization.

    Algorithm:
    1. Group minterms by number of 1s
    2. Combine adjacent groups (differ by 1 bit)
    3. Repeat until no more combinations
    4. Select essential prime implicants
    5. Cover remaining minterms
    """

    @staticmethod
    def minimize(
        minterms: List[int],
        dont_cares: List[int],
        n_vars: int
    ) -> Dict[str, Any]:
        """
        Minimize Boolean function given minterms and don't cares.

        Args:
            minterms: List of minterm numbers where f=1
            dont_cares: List of don't care terms
            n_vars: Number of variables

        Returns:
            Dictionary with prime implicants, essential PIs, and minimal expression
        """
        all_terms = set(minterms) | set(dont_cares)

        def count_ones(n: int) -> int:
            return bin(n).count('1')

        def term_to_str(term: int, mask: int, n: int) -> str:
            """Convert term to string with dashes for combined bits."""
            result = []
            for i in range(n - 1, -1, -1):
                if (mask >> i) & 1:
                    result.append('-')
                elif (term >> i) & 1:
                    result.append('1')
                else:
                    result.append('0')
            return ''.join(result)

        current = [(m, 0, frozenset([m])) for m in all_terms]
        prime_implicants = []

        while current:
            groups: Dict[int, List[Tuple[int, int, FrozenSet[int]]]] = {}
            for term, mask, covered in current:
                ones = count_ones(term & ~mask)
                if ones not in groups:
                    groups[ones] = []
                groups[ones].append((term, mask, covered))

            next_round = []
            used: Set[Tuple[int, int]] = set()

            sorted_groups = sorted(groups.keys())
            for i in range(len(sorted_groups) - 1):
                g1, g2 = sorted_groups[i], sorted_groups[i + 1]
                if g2 - g1 != 1:
                    continue

                for t1, m1, c1 in groups[g1]:
                    for t2, m2, c2 in groups[g2]:
                        if m1 != m2:
                            continue

                        diff = (t1 ^ t2) & ~m1
                        if diff and (diff & (diff - 1)) == 0:
                            new_term = t1 & t2
                            new_mask = m1 | diff
                            new_covered = c1 | c2

                            next_round.append((new_term, new_mask, new_covered))
                            used.add((t1, m1))
                            used.add((t2, m2))

            for term, mask, covered in current:
                if (term, mask) not in used:
                    prime_implicants.append((term, mask, covered))

            seen_next: Set[Tuple[int, int]] = set()
            unique_next = []
            for item in next_round:
                key = (item[0], item[1])
                if key not in seen_next:
                    seen_next.add(key)
                    unique_next.append(item)
            current = unique_next

        seen: Set[Tuple[int, int]] = set()
        unique_pis = []
        for term, mask, covered in prime_implicants:
            key = (term, mask)
            if key not in seen:
                seen.add(key)
                unique_pis.append((term, mask, covered))

        minterm_set = set(minterms)
        essential = []
        covered_by: Dict[int, List[int]] = {m: [] for m in minterms}

        for idx, (term, mask, covered) in enumerate(unique_pis):
            for m in covered & minterm_set:
                covered_by[m].append(idx)

        essential_indices: Set[int] = set()
        for m, indices in covered_by.items():
            if len(indices) == 1:
                essential_indices.add(indices[0])

        essential = [unique_pis[i] for i in essential_indices]

        covered_minterms: Set[int] = set()
        for _, _, covered in essential:
            covered_minterms |= (covered & minterm_set)

        remaining = minterm_set - covered_minterms
        selected = list(essential)
        remaining_pis = [p for i, p in enumerate(unique_pis) if i not in essential_indices]

        while remaining:
            best_pi = None
            best_count = 0
            for pi in remaining_pis:
                count = len(pi[2] & remaining)
                if count > best_count:
                    best_count = count
                    best_pi = pi

            if best_pi:
                selected.append(best_pi)
                remaining -= best_pi[2]
                remaining_pis.remove(best_pi)
            else:
                break

        def pi_to_expr(term: int, mask: int, n: int) -> str:
            vars_list = [chr(ord('A') + i) for i in range(n)]
            parts = []
            for i in range(n):
                bit_pos = n - 1 - i
                if not ((mask >> bit_pos) & 1):
                    if (term >> bit_pos) & 1:
                        parts.append(vars_list[i])
                    else:
                        parts.append(f"{vars_list[i]}'")
            return ''.join(parts) if parts else '1'

        minimal_expr = ' + '.join(pi_to_expr(t, m, n_vars) for t, m, _ in selected)

        return {
            'prime_implicants': [(term_to_str(t, m, n_vars), list(c)) for t, m, c in unique_pis],
            'essential_prime_implicants': [(term_to_str(t, m, n_vars), list(c)) for t, m, c in essential],
            'minimal_expression': minimal_expr if minimal_expr else '0',
            'num_terms': len(selected),
            'method': 'quine_mccluskey'
        }


class KarnaughMap:
    """Karnaugh map for up to 4 variables."""

    @staticmethod
    def generate_kmap(minterms: List[int], n_vars: int) -> Dict[str, Any]:
        """
        Generate Karnaugh map representation.

        Args:
            minterms: List of minterm numbers where f=1
            n_vars: Number of variables (2, 3, or 4)

        Returns:
            Dictionary with K-map grid and labels
        """
        if n_vars < 2 or n_vars > 4:
            return {'error': 'K-map supports 2-4 variables'}

        minterm_set = set(minterms)

        if n_vars == 2:
            grid = [[1 if (r * 2 + c) in minterm_set else 0
                    for c in [0, 1]] for r in [0, 1]]
            return {
                'n_vars': 2,
                'row_labels': ['A=0', 'A=1'],
                'col_labels': ['B=0', 'B=1'],
                'grid': grid
            }

        elif n_vars == 3:
            col_order = [0, 1, 3, 2]  # Gray code
            grid = []
            for r in [0, 1]:
                row = []
                for c in col_order:
                    term = r * 4 + c
                    row.append(1 if term in minterm_set else 0)
                grid.append(row)

            return {
                'n_vars': 3,
                'row_labels': ['A=0', 'A=1'],
                'col_labels': ['BC=00', 'BC=01', 'BC=11', 'BC=10'],
                'grid': grid
            }

        else:  # n_vars == 4
            row_order = [0, 1, 3, 2]
            col_order = [0, 1, 3, 2]

            grid = []
            for r in row_order:
                row = []
                for c in col_order:
                    term = r * 4 + c
                    row.append(1 if term in minterm_set else 0)
                grid.append(row)

            return {
                'n_vars': 4,
                'row_labels': ['AB=00', 'AB=01', 'AB=11', 'AB=10'],
                'col_labels': ['CD=00', 'CD=01', 'CD=11', 'CD=10'],
                'grid': grid
            }

    @staticmethod
    def format_kmap(kmap: Dict[str, Any]) -> str:
        """Format K-map for display."""
        if 'error' in kmap:
            return kmap['error']

        lines = []
        col_labels = kmap['col_labels']
        row_labels = kmap['row_labels']
        grid = kmap['grid']

        header = '     ' + '  '.join(f'{l:>5}' for l in col_labels)
        lines.append(header)
        lines.append('-' * len(header))

        for i, row in enumerate(grid):
            row_str = f'{row_labels[i]:>4} |' + '  '.join(f'{v:>5}' for v in row)
            lines.append(row_str)

        return '\n'.join(lines)


class TruthTableGenerator:
    """Generate truth tables for Boolean expressions."""

    @staticmethod
    def generate(expression: str, n_vars: int) -> Dict[str, Any]:
        """
        Generate truth table for a Boolean expression.

        Args:
            expression: Boolean expression (uses AND, OR, NOT, ', +, *)
            n_vars: Number of variables

        Returns:
            Dictionary with table data
        """
        vars_list = [chr(ord('A') + i) for i in range(n_vars)]
        rows = []
        minterms = []
        maxterms = []

        for i in range(2**n_vars):
            var_values = {}
            for j, var in enumerate(vars_list):
                var_values[var] = (i >> (n_vars - 1 - j)) & 1

            try:
                result = TruthTableGenerator._evaluate(expression, var_values)
            except Exception:
                result = 0

            row = [var_values[v] for v in vars_list] + [result]
            rows.append(row)

            if result:
                minterms.append(i)
            else:
                maxterms.append(i)

        return {
            'variables': vars_list,
            'rows': rows,
            'minterms': minterms,
            'maxterms': maxterms,
            'expression': expression
        }

    @staticmethod
    def _evaluate(expr: str, var_values: Dict[str, int]) -> int:
        """Evaluate Boolean expression with given variable values."""
        expr = expr.replace("'", " NOT ")
        expr = expr.replace("*", " AND ")
        expr = expr.replace("+", " OR ")
        expr = expr.replace(".", " AND ")

        for var, val in var_values.items():
            expr = re.sub(rf'\b{var}\b', str(val), expr)

        expr = expr.replace('NOT 0', '1')
        expr = expr.replace('NOT 1', '0')
        expr = expr.replace('NOT(0)', '1')
        expr = expr.replace('NOT(1)', '0')

        expr = re.sub(r'1\s+AND\s+1', '1', expr)
        expr = re.sub(r'1\s+AND\s+0', '0', expr)
        expr = re.sub(r'0\s+AND\s+1', '0', expr)
        expr = re.sub(r'0\s+AND\s+0', '0', expr)

        expr = re.sub(r'1\s+OR\s+1', '1', expr)
        expr = re.sub(r'1\s+OR\s+0', '1', expr)
        expr = re.sub(r'0\s+OR\s+1', '1', expr)
        expr = re.sub(r'0\s+OR\s+0', '0', expr)

        expr = expr.strip()
        if expr in ('0', '1'):
            return int(expr)

        try:
            safe_expr = re.sub(r'[^01\s]', '', expr)
            if safe_expr in ('0', '1'):
                return int(safe_expr)
        except Exception:
            pass

        return 0


# =============================================================================
# BOOLEAN ALGEBRA AGENT (Tier 3)
# =============================================================================

class BooleanAlgebraAgent(BDIAgent):
    """
    Boolean Algebra Specialist - Tier 3

    Handles:
    - Boolean operations (AND, OR, NOT, XOR, etc.)
    - Normal forms (DNF, CNF)
    - Quine-McCluskey minimization
    - Karnaugh map generation
    - Truth table generation
    - Prime implicant identification
    """

    def __init__(
        self,
        agent_id: str = 'boolean_algebra_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.discrete.boolean',
                agent_id=agent_id,
                algorithm='quine_mccluskey',
                cost='medium',
                instance=self,
                tier='3',
                operations='minimize_dnf_cnf_karnaugh_truth_table'
            ))

        logger.info(f"[{agent_id}] Boolean Algebra Agent initialized")
        logger.info(f"  Algorithm: Quine-McCluskey minimization")
        logger.info(f"  Operations: Minimization, normal forms, K-maps")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for boolean algebra tasks."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus

            tasks = self.blackboard.query_entries(
                tags=['boolean', 'logic', 'minimize'],
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
        """DELIBERATE: Create plans for boolean algebra tasks."""
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

            steps = ['claim_task', 'parse_input', f'compute_{operation}', 'verify_result', 'post_result']

            intention = Intention(
                plan_id=f'bool_{operation}_{task_id}',
                steps=steps,
                target_desire='solve_boolean',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation, 'raw_input': raw_input}
            )
            new_intentions.append(intention)

        return new_intentions

    def _determine_operation(self, raw_input: str) -> str:
        """Determine which boolean operation to perform."""
        if 'minimize' in raw_input or 'quine' in raw_input or 'simplify' in raw_input:
            return 'minimize'
        elif 'karnaugh' in raw_input or 'k-map' in raw_input or 'kmap' in raw_input:
            return 'karnaugh'
        elif 'dnf' in raw_input or 'disjunctive' in raw_input:
            return 'to_dnf'
        elif 'cnf' in raw_input or 'conjunctive' in raw_input:
            return 'to_cnf'
        elif 'truth' in raw_input and 'table' in raw_input:
            return 'truth_table'
        elif 'prime' in raw_input and 'implicant' in raw_input:
            return 'prime_implicants'
        elif 'minterm' in raw_input:
            return 'to_minterm'
        elif 'maxterm' in raw_input:
            return 'to_maxterm'
        else:
            return 'minimize'

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute boolean algebra computation."""
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

            elif action == 'parse_input':
                raw = intention.metadata.get('raw_input', '')
                parsed = self._parse_boolean_input(raw)
                intention.metadata.update(parsed)
                intention.advance()

            elif action.startswith('compute_'):
                operation = action.replace('compute_', '')
                result = self._compute_operation(operation, intention.metadata)
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
                        tags=['boolean', 'result', task_id],
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

    def _parse_boolean_input(self, raw: str) -> Dict[str, Any]:
        """Parse boolean expression input."""
        result = {'minterms': [], 'dont_cares': [], 'n_vars': 3, 'expression': ''}

        numbers = [int(n) for n in re.findall(r'\d+', raw)]

        minterm_match = re.search(r'minterm[s]?\s*[:\(]?\s*([\d,\s]+)', raw, re.IGNORECASE)
        if minterm_match:
            result['minterms'] = [int(n) for n in re.findall(r'\d+', minterm_match.group(1))]

        dc_match = re.search(r"don'?t\s*care[s]?\s*[:\(]?\s*([\d,\s]+)", raw, re.IGNORECASE)
        if dc_match:
            result['dont_cares'] = [int(n) for n in re.findall(r'\d+', dc_match.group(1))]

        var_match = re.search(r'(\d+)\s*var', raw, re.IGNORECASE)
        if var_match:
            result['n_vars'] = int(var_match.group(1))
        elif result['minterms']:
            max_term = max(result['minterms'] + result['dont_cares']) if result['minterms'] or result['dont_cares'] else 0
            result['n_vars'] = max(3, (max_term).bit_length())

        if not result['minterms'] and numbers:
            result['minterms'] = numbers

        expr_match = re.search(r'f\s*=\s*([A-Z\'+\*\(\)\s]+)', raw, re.IGNORECASE)
        if expr_match:
            result['expression'] = expr_match.group(1).strip()

        return result

    def _compute_operation(self, operation: str, metadata: Dict[str, Any]) -> Any:
        """Execute the specified boolean operation."""
        minterms = metadata.get('minterms', [])
        dont_cares = metadata.get('dont_cares', [])
        n_vars = metadata.get('n_vars', 3)
        expression = metadata.get('expression', '')

        if operation == 'minimize':
            return QuineMcCluskey.minimize(minterms, dont_cares, n_vars)
        elif operation == 'karnaugh':
            return KarnaughMap.generate_kmap(minterms, n_vars)
        elif operation == 'to_dnf':
            return {'dnf': NormalForms.truth_table_to_dnf(minterms, n_vars)}
        elif operation == 'to_cnf':
            all_terms = set(range(2**n_vars))
            maxterms = list(all_terms - set(minterms) - set(dont_cares))
            return {'cnf': NormalForms.truth_table_to_cnf(maxterms, n_vars)}
        elif operation == 'truth_table':
            if expression:
                return TruthTableGenerator.generate(expression, n_vars)
            return {'error': 'No expression provided'}
        elif operation == 'prime_implicants':
            result = QuineMcCluskey.minimize(minterms, dont_cares, n_vars)
            return {'prime_implicants': result['prime_implicants']}
        elif operation == 'to_minterm':
            if minterms:
                return {'minterm': NormalForms.to_minterm(minterms[0], n_vars)}
            return {'error': 'No minterm number provided'}
        elif operation == 'to_maxterm':
            if minterms:
                return {'maxterm': NormalForms.to_maxterm(minterms[0], n_vars)}
            return {'error': 'No maxterm number provided'}
        else:
            return QuineMcCluskey.minimize(minterms, dont_cares, n_vars)

    def _format_result(self, result: Any) -> str:
        """Format result for output."""
        if isinstance(result, dict):
            if 'minimal_expression' in result:
                return f"Minimal: {result['minimal_expression']} ({result['num_terms']} terms)"
            elif 'grid' in result:
                return KarnaughMap.format_kmap(result)
            elif 'dnf' in result:
                return f"DNF: {result['dnf']}"
            elif 'cnf' in result:
                return f"CNF: {result['cnf']}"
            elif 'prime_implicants' in result:
                pis = result['prime_implicants']
                return f"Prime Implicants: {', '.join(pi[0] for pi in pis)}"
            elif 'rows' in result:
                lines = [' '.join(result['variables']) + ' | F']
                for row in result['rows']:
                    lines.append(' '.join(str(v) for v in row[:-1]) + ' | ' + str(row[-1]))
                return '\n'.join(lines)
            elif 'error' in result:
                return f"Error: {result['error']}"
            return str(result)
        return str(result)

    def process(self, task_entry) -> Any:
        """Direct invocation entry point for supervisor delegation."""
        from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType, EntryStatus
        from symbo_agentic_reasoners.core.omdoc_schema import create_variable

        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            raw_input = metadata.get('raw_input', '').lower()

            operation = self._determine_operation(raw_input)
            parsed = self._parse_boolean_input(raw_input)
            result = self._compute_operation(operation, parsed)
            result_str = self._format_result(result)

            self.tasks_executed += 1

            return create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(result_str),
                author_agent=self.agent_id,
                conversation_id=getattr(task_entry, 'conversation_id', 'direct'),
                tags=['boolean', 'result'],
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
                tags=['boolean', 'error'],
                status=EntryStatus.FAILED,
                metadata={'error': str(e)}
            )

    def get_statistics(self) -> Dict[str, Any]:
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed})
        return stats
