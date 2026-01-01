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
PHASE 2 - FINITE AUTOMATA AGENT (Tier 3)
=========================================

Formal language theory and automata operations.

Capabilities:
- DFA construction and simulation
- NFA construction and simulation
- NFA to DFA conversion (subset construction)
- Regular expression to NFA (Thompson's construction)
- DFA minimization (Hopcroft's algorithm)
- Language operations (union, intersection, complement)
- String acceptance testing

NO SYMPY - All implementations are native Python.
"""

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard
from typing import Dict, Any, List, Optional, Set, Tuple, FrozenSet
from dataclasses import dataclass, field
from collections import deque
import re
import logging

logger = logging.getLogger('symbo_agentic_reasoners.finite_automata')


# =============================================================================
# NATIVE FINITE AUTOMATA (NO SYMPY)
# =============================================================================

@dataclass
class DFA:
    """
    Deterministic Finite Automaton.

    A DFA is defined by (Q, Sigma, delta, q0, F) where:
    - Q: finite set of states
    - Sigma: input alphabet
    - delta: transition function Q x Sigma -> Q
    - q0: start state
    - F: set of accepting states
    """
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[Tuple[str, str], str]  # (state, symbol) -> next_state
    start_state: str
    accept_states: Set[str]

    def accepts(self, input_string: str) -> bool:
        """Check if DFA accepts the input string."""
        current = self.start_state
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False
            key = (current, symbol)
            if key not in self.transitions:
                return False
            current = self.transitions[key]
        return current in self.accept_states

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'states': list(self.states),
            'alphabet': list(self.alphabet),
            'transitions': {f"({s},{a})": t for (s, a), t in self.transitions.items()},
            'start_state': self.start_state,
            'accept_states': list(self.accept_states)
        }


@dataclass
class NFA:
    """
    Nondeterministic Finite Automaton with epsilon transitions.

    NFA allows:
    - Multiple transitions from same state on same symbol
    - Epsilon (empty string) transitions
    """
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[Tuple[str, str], Set[str]]  # (state, symbol) -> {next_states}
    start_state: str
    accept_states: Set[str]
    epsilon: str = ''  # epsilon symbol

    def epsilon_closure(self, states: Set[str]) -> Set[str]:
        """Compute epsilon closure of a set of states."""
        closure = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            key = (state, self.epsilon)
            if key in self.transitions:
                for next_state in self.transitions[key]:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)

        return closure

    def move(self, states: Set[str], symbol: str) -> Set[str]:
        """Compute states reachable on symbol from any state in states."""
        result: Set[str] = set()
        for state in states:
            key = (state, symbol)
            if key in self.transitions:
                result |= self.transitions[key]
        return result

    def accepts(self, input_string: str) -> bool:
        """Check if NFA accepts the input string."""
        current = self.epsilon_closure({self.start_state})

        for symbol in input_string:
            if symbol not in self.alphabet:
                return False
            current = self.epsilon_closure(self.move(current, symbol))

        return bool(current & self.accept_states)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'states': list(self.states),
            'alphabet': list(self.alphabet),
            'transitions': {f"({s},{a})": list(t) for (s, a), t in self.transitions.items()},
            'start_state': self.start_state,
            'accept_states': list(self.accept_states)
        }


class AutomataOperations:
    """Operations on finite automata."""

    @staticmethod
    def nfa_to_dfa(nfa: NFA) -> DFA:
        """
        Convert NFA to DFA using subset construction.

        Each DFA state represents a set of NFA states.
        """
        dfa_states: Set[FrozenSet[str]] = set()
        dfa_transitions: Dict[Tuple[FrozenSet[str], str], FrozenSet[str]] = {}
        dfa_accept: Set[FrozenSet[str]] = set()

        start_closure = frozenset(nfa.epsilon_closure({nfa.start_state}))
        dfa_start = start_closure

        worklist = [start_closure]
        dfa_states.add(start_closure)

        while worklist:
            current = worklist.pop()

            for symbol in nfa.alphabet:
                next_states = nfa.epsilon_closure(nfa.move(set(current), symbol))
                next_frozen = frozenset(next_states)

                if next_frozen:
                    dfa_transitions[(current, symbol)] = next_frozen

                    if next_frozen not in dfa_states:
                        dfa_states.add(next_frozen)
                        worklist.append(next_frozen)

        for state in dfa_states:
            if state & nfa.accept_states:
                dfa_accept.add(state)

        state_names: Dict[FrozenSet[str], str] = {}
        for i, state in enumerate(sorted(dfa_states, key=lambda s: sorted(s))):
            state_names[state] = f"q{i}"

        dfa_trans: Dict[Tuple[str, str], str] = {}
        for (state, symbol), next_state in dfa_transitions.items():
            dfa_trans[(state_names[state], symbol)] = state_names[next_state]

        return DFA(
            states={state_names[s] for s in dfa_states},
            alphabet=nfa.alphabet.copy(),
            transitions=dfa_trans,
            start_state=state_names[dfa_start],
            accept_states={state_names[s] for s in dfa_accept}
        )

    @staticmethod
    def minimize_dfa(dfa: DFA) -> DFA:
        """
        Minimize DFA using Hopcroft's algorithm.

        Removes unreachable states and merges equivalent states.
        """
        # Remove unreachable states
        reachable: Set[str] = {dfa.start_state}
        worklist = [dfa.start_state]

        while worklist:
            state = worklist.pop()
            for symbol in dfa.alphabet:
                key = (state, symbol)
                if key in dfa.transitions:
                    next_state = dfa.transitions[key]
                    if next_state not in reachable:
                        reachable.add(next_state)
                        worklist.append(next_state)

        # Initial partition: accepting vs non-accepting
        accepting = dfa.accept_states & reachable
        non_accepting = reachable - accepting

        partitions: List[Set[str]] = []
        if accepting:
            partitions.append(accepting)
        if non_accepting:
            partitions.append(non_accepting)

        # Refine partitions
        worklist_p = list(partitions)

        while worklist_p:
            A = worklist_p.pop()

            for symbol in dfa.alphabet:
                X: Set[str] = set()
                for state in reachable:
                    key = (state, symbol)
                    if key in dfa.transitions and dfa.transitions[key] in A:
                        X.add(state)

                new_partitions = []
                for Y in partitions:
                    intersection = Y & X
                    difference = Y - X

                    if intersection and difference:
                        new_partitions.append(intersection)
                        new_partitions.append(difference)

                        if Y in worklist_p:
                            worklist_p.remove(Y)
                            worklist_p.append(intersection)
                            worklist_p.append(difference)
                        else:
                            if len(intersection) <= len(difference):
                                worklist_p.append(intersection)
                            else:
                                worklist_p.append(difference)
                    else:
                        new_partitions.append(Y)

                partitions = new_partitions

        # Build minimized DFA
        state_to_partition: Dict[str, int] = {}
        for i, partition in enumerate(partitions):
            for state in partition:
                state_to_partition[state] = i

        min_states = {f"q{i}" for i in range(len(partitions))}
        min_trans: Dict[Tuple[str, str], str] = {}
        min_accept: Set[str] = set()
        min_start = f"q{state_to_partition[dfa.start_state]}"

        for i, partition in enumerate(partitions):
            rep = next(iter(partition))
            for symbol in dfa.alphabet:
                key = (rep, symbol)
                if key in dfa.transitions:
                    next_state = dfa.transitions[key]
                    min_trans[(f"q{i}", symbol)] = f"q{state_to_partition[next_state]}"

            if partition & dfa.accept_states:
                min_accept.add(f"q{i}")

        return DFA(
            states=min_states,
            alphabet=dfa.alphabet.copy(),
            transitions=min_trans,
            start_state=min_start,
            accept_states=min_accept
        )

    @staticmethod
    def union(dfa1: DFA, dfa2: DFA) -> NFA:
        """Construct NFA accepting L(dfa1) U L(dfa2)."""
        # Create new start state with epsilon to both DFAs
        new_start = "q_start"
        states = {new_start}
        transitions: Dict[Tuple[str, str], Set[str]] = {}

        # Add epsilon transitions from new start
        transitions[(new_start, '')] = {f"1_{dfa1.start_state}", f"2_{dfa2.start_state}"}

        # Add DFA1 states and transitions
        for state in dfa1.states:
            states.add(f"1_{state}")
        for (s, a), t in dfa1.transitions.items():
            key = (f"1_{s}", a)
            if key not in transitions:
                transitions[key] = set()
            transitions[key].add(f"1_{t}")

        # Add DFA2 states and transitions
        for state in dfa2.states:
            states.add(f"2_{state}")
        for (s, a), t in dfa2.transitions.items():
            key = (f"2_{s}", a)
            if key not in transitions:
                transitions[key] = set()
            transitions[key].add(f"2_{t}")

        accept = {f"1_{s}" for s in dfa1.accept_states} | {f"2_{s}" for s in dfa2.accept_states}
        alphabet = dfa1.alphabet | dfa2.alphabet

        return NFA(
            states=states,
            alphabet=alphabet,
            transitions=transitions,
            start_state=new_start,
            accept_states=accept
        )

    @staticmethod
    def complement(dfa: DFA) -> DFA:
        """Construct DFA accepting complement of L(dfa)."""
        # Add dead state for missing transitions
        dead_state = "q_dead"
        new_states = dfa.states | {dead_state}
        new_trans = dict(dfa.transitions)

        for state in new_states:
            for symbol in dfa.alphabet:
                if (state, symbol) not in new_trans:
                    new_trans[(state, symbol)] = dead_state

        # Swap accepting and non-accepting states
        new_accept = new_states - dfa.accept_states

        return DFA(
            states=new_states,
            alphabet=dfa.alphabet.copy(),
            transitions=new_trans,
            start_state=dfa.start_state,
            accept_states=new_accept
        )


class RegexToNFA:
    """
    Convert regular expressions to NFA using Thompson's construction.

    Supported operators:
    - Concatenation (implicit)
    - Union (|)
    - Kleene star (*)
    - Plus (+)
    - Optional (?)
    - Parentheses for grouping
    """

    def __init__(self):
        self.state_counter = 0

    def new_state(self) -> str:
        """Perform new state operation.

        Args:


        Returns:
        Result of the operation

        Example:
        >>> specialist = RegexToNFA()
        >>> result = specialist.new_state(...)
        # Returns result
        """
        self.state_counter += 1
        return f"s{self.state_counter}"

    def regex_to_nfa(self, regex: str) -> NFA:
        """Convert regex to NFA."""
        self.state_counter = 0
        alphabet = set(c for c in regex if c.isalnum())
        postfix = self._to_postfix(regex)
        return self._build_nfa(postfix, alphabet)

    def _to_postfix(self, regex: str) -> str:
        """Convert infix regex to postfix with explicit concatenation."""
        explicit = self._add_concat_symbol(regex)
        return self._infix_to_postfix(explicit)

    def _add_concat_symbol(self, regex: str) -> str:
        """Add explicit concatenation symbol '.'."""
        result = []
        i = 0
        while i < len(regex):
            c = regex[i]
            result.append(c)

            if i + 1 < len(regex):
                next_c = regex[i + 1]
                if (c.isalnum() or c in '*+?)') and (next_c.isalnum() or next_c == '('):
                    result.append('.')
                elif c == ')' and (next_c.isalnum() or next_c == '('):
                    result.append('.')

            i += 1
        return ''.join(result)

    def _infix_to_postfix(self, regex: str) -> str:
        """Convert infix to postfix using shunting-yard algorithm."""
        precedence = {'|': 1, '.': 2, '?': 3, '+': 3, '*': 3}
        output = []
        stack = []

        for c in regex:
            if c.isalnum():
                output.append(c)
            elif c == '(':
                stack.append(c)
            elif c == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()
            else:
                while (stack and stack[-1] != '(' and
                       stack[-1] in precedence and
                       precedence.get(stack[-1], 0) >= precedence.get(c, 0)):
                    output.append(stack.pop())
                stack.append(c)

        while stack:
            output.append(stack.pop())

        return ''.join(output)

    def _build_nfa(self, postfix: str, alphabet: Set[str]) -> NFA:
        """Build NFA from postfix expression."""
        stack: List[Tuple[str, str, Dict, Set]] = []

        for c in postfix:
            if c.isalnum():
                start = self.new_state()
                end = self.new_state()
                trans = {(start, c): {end}}
                stack.append((start, end, trans, {start, end}))

            elif c == '.':  # Concatenation
                s2, e2, t2, st2 = stack.pop()
                s1, e1, t1, st1 = stack.pop()

                t1.update(t2)
                key = (e1, '')
                if key not in t1:
                    t1[key] = set()
                t1[key].add(s2)

                stack.append((s1, e2, t1, st1 | st2))

            elif c == '|':  # Union
                s2, e2, t2, st2 = stack.pop()
                s1, e1, t1, st1 = stack.pop()

                new_start = self.new_state()
                new_end = self.new_state()

                t1.update(t2)
                t1[(new_start, '')] = {s1, s2}
                if (e1, '') not in t1:
                    t1[(e1, '')] = set()
                t1[(e1, '')].add(new_end)
                if (e2, '') not in t1:
                    t1[(e2, '')] = set()
                t1[(e2, '')].add(new_end)

                stack.append((new_start, new_end, t1, st1 | st2 | {new_start, new_end}))

            elif c == '*':  # Kleene star
                s, e, t, st = stack.pop()

                new_start = self.new_state()
                new_end = self.new_state()

                t[(new_start, '')] = {s, new_end}
                if (e, '') not in t:
                    t[(e, '')] = set()
                t[(e, '')].update({s, new_end})

                stack.append((new_start, new_end, t, st | {new_start, new_end}))

            elif c == '+':  # One or more
                s, e, t, st = stack.pop()

                new_start = self.new_state()
                new_end = self.new_state()

                t[(new_start, '')] = {s}
                if (e, '') not in t:
                    t[(e, '')] = set()
                t[(e, '')].update({s, new_end})

                stack.append((new_start, new_end, t, st | {new_start, new_end}))

            elif c == '?':  # Optional
                s, e, t, st = stack.pop()

                new_start = self.new_state()
                new_end = self.new_state()

                t[(new_start, '')] = {s, new_end}
                if (e, '') not in t:
                    t[(e, '')] = set()
                t[(e, '')].add(new_end)

                stack.append((new_start, new_end, t, st | {new_start, new_end}))

        if not stack:
            start = self.new_state()
            return NFA(
                states={start},
                alphabet=alphabet,
                transitions={},
                start_state=start,
                accept_states={start}
            )

        start, end, transitions, states = stack.pop()

        return NFA(
            states=states,
            alphabet=alphabet,
            transitions=transitions,
            start_state=start,
            accept_states={end}
        )


# =============================================================================
# FINITE AUTOMATA AGENT (Tier 3)
# =============================================================================

class FiniteAutomataAgent(BDIAgent):
    """
    Finite Automata Specialist - Tier 3

    Handles:
    - DFA and NFA construction
    - NFA to DFA conversion
    - DFA minimization
    - Regular expression to NFA
    - String acceptance testing
    - Language operations (union, complement)
    """

    def __init__(
        self,
        agent_id: str = 'finite_automata_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.discrete.automata',
                agent_id=agent_id,
                algorithm='thompson_hopcroft',
                cost='medium',
                instance=self,
                tier='3',
                operations='dfa_nfa_minimize_regex_accept'
            ))

        logger.info(f"[{agent_id}] Finite Automata Agent initialized")
        logger.info(f"  Algorithm: Thompson's construction, Hopcroft minimization")
        logger.info(f"  Operations: DFA, NFA, regex, minimization")

    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for automata tasks."""
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus

            tasks = self.blackboard.query_entries(
                tags=['automata', 'dfa', 'nfa', 'regex'],
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
        """DELIBERATE: Create plans for automata tasks."""
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
                plan_id=f'auto_{operation}_{task_id}',
                steps=steps,
                target_desire='solve_automata',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation, 'raw_input': raw_input}
            )
            new_intentions.append(intention)

        return new_intentions

    def _determine_operation(self, raw_input: str) -> str:
        """Determine which automata operation to perform."""
        if 'minimize' in raw_input:
            return 'minimize'
        elif 'nfa' in raw_input and 'dfa' in raw_input:
            return 'nfa_to_dfa'
        elif 'regex' in raw_input or 'regular expression' in raw_input:
            return 'regex_to_nfa'
        elif 'accept' in raw_input or 'test' in raw_input:
            return 'test_string'
        elif 'complement' in raw_input:
            return 'complement'
        elif 'union' in raw_input:
            return 'union'
        elif 'build' in raw_input and 'dfa' in raw_input:
            return 'build_dfa'
        elif 'build' in raw_input and 'nfa' in raw_input:
            return 'build_nfa'
        else:
            return 'test_string'

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute automata computation."""
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
                parsed = self._parse_automata_input(raw)
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
                        tags=['automata', 'result', task_id],
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

    def _parse_automata_input(self, raw: str) -> Dict[str, Any]:
        """Parse automata input."""
        result: Dict[str, Any] = {'regex': '', 'test_string': '', 'dfa': None}

        regex_match = re.search(r'regex[:\s]*([a-zA-Z0-9\(\)\*\+\?\|]+)', raw, re.IGNORECASE)
        if regex_match:
            result['regex'] = regex_match.group(1)

        string_match = re.search(r'string[:\s]*"?([a-zA-Z0-9]*)"?', raw, re.IGNORECASE)
        if string_match:
            result['test_string'] = string_match.group(1)

        test_match = re.search(r'test[:\s]*"?([a-zA-Z0-9]*)"?', raw, re.IGNORECASE)
        if test_match:
            result['test_string'] = test_match.group(1)

        accept_match = re.search(r'accept[s]?\s+"?([a-zA-Z0-9]+)"?', raw, re.IGNORECASE)
        if accept_match:
            result['test_string'] = accept_match.group(1)

        return result

    def _compute_operation(self, operation: str, metadata: Dict[str, Any]) -> Any:
        """Execute the specified automata operation."""
        regex = metadata.get('regex', '')
        test_string = metadata.get('test_string', '')

        if operation == 'regex_to_nfa':
            if regex:
                converter = RegexToNFA()
                nfa = converter.regex_to_nfa(regex)
                return {'nfa': nfa.to_dict(), 'regex': regex}
            return {'error': 'No regex provided'}

        elif operation == 'test_string':
            if regex and test_string:
                converter = RegexToNFA()
                nfa = converter.regex_to_nfa(regex)
                accepted = nfa.accepts(test_string)
                return {
                    'regex': regex,
                    'test_string': test_string,
                    'accepted': accepted
                }
            return {'error': 'Need both regex and test string'}

        elif operation == 'nfa_to_dfa':
            if regex:
                converter = RegexToNFA()
                nfa = converter.regex_to_nfa(regex)
                dfa = AutomataOperations.nfa_to_dfa(nfa)
                return {
                    'dfa': dfa.to_dict(),
                    'num_states': len(dfa.states)
                }
            return {'error': 'No regex provided'}

        elif operation == 'minimize':
            if regex:
                converter = RegexToNFA()
                nfa = converter.regex_to_nfa(regex)
                dfa = AutomataOperations.nfa_to_dfa(nfa)
                minimized = AutomataOperations.minimize_dfa(dfa)
                return {
                    'original_states': len(dfa.states),
                    'minimized_states': len(minimized.states),
                    'minimized_dfa': minimized.to_dict()
                }
            return {'error': 'No regex provided'}

        elif operation == 'complement':
            if regex:
                converter = RegexToNFA()
                nfa = converter.regex_to_nfa(regex)
                dfa = AutomataOperations.nfa_to_dfa(nfa)
                complement = AutomataOperations.complement(dfa)
                return {'complement_dfa': complement.to_dict()}
            return {'error': 'No regex provided'}

        else:
            return {'error': f'Unknown operation: {operation}'}

    def _format_result(self, result: Any) -> str:
        """Format result for output."""
        if isinstance(result, dict):
            if 'accepted' in result:
                status = 'ACCEPTED' if result['accepted'] else 'REJECTED'
                return f"String '{result['test_string']}' is {status} by regex '{result['regex']}'"
            elif 'minimized_states' in result:
                return f"Minimized: {result['original_states']} -> {result['minimized_states']} states"
            elif 'dfa' in result:
                return f"DFA with {result.get('num_states', len(result['dfa'].get('states', [])))} states"
            elif 'nfa' in result:
                return f"NFA built from regex '{result['regex']}'"
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
            parsed = self._parse_automata_input(raw_input)
            result = self._compute_operation(operation, parsed)
            result_str = self._format_result(result)

            self.tasks_executed += 1

            return create_entry(
                entry_type=EntryType.PARTIAL_RESULT,
                content=create_variable(result_str),
                author_agent=self.agent_id,
                conversation_id=getattr(task_entry, 'conversation_id', 'direct'),
                tags=['automata', 'result'],
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
                tags=['automata', 'error'],
                status=EntryStatus.FAILED,
                metadata={'error': str(e)}
            )

    def get_statistics(self) -> Dict[str, Any]:
        """Compute get statistics using mathematical formula.

        Returns:
        Computed numerical or symbolic result

        Example:
        >>> specialist = FiniteAutomataAgent()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats.update({'tasks_executed': self.tasks_executed})
        return stats
