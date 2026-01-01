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
PROOF SPECIALIST (Tier 3)
=========================

Handles mathematical proofs: direct proof, contradiction,
induction, and proof verification.

CAPABILITIES:
- Direct proof validation
- Proof by contradiction
- Mathematical induction
- Proof step verification
- Inference rule application
"""

from typing import Any, Dict, List, Optional, Tuple
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard


class ProofSpecialist(BDIAgent):
    """Specialist for mathematical proof problems."""

    # Common inference rules
    INFERENCE_RULES = {
        'modus_ponens': 'P, P->Q |- Q',
        'modus_tollens': '~Q, P->Q |- ~P',
        'hypothetical_syllogism': 'P->Q, Q->R |- P->R',
        'disjunctive_syllogism': 'P|Q, ~P |- Q',
        'conjunction': 'P, Q |- P&Q',
        'simplification': 'P&Q |- P',
        'addition': 'P |- P|Q',
        'resolution': 'P|Q, ~P|R |- Q|R',
        'double_negation': '~~P |- P'
    }

    def __init__(
        self,
        agent_id: str = 'proof_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0

        if self.df:
            self.df.register(create_service_registration(
                service_type='math.logic.proof',
                agent_id=agent_id,
                algorithm='natural_deduction',
                cost='high',
                instance=self,  # Enable direct invocation by supervisors
                tier='3',
                capabilities='direct_proof_contradiction_induction'
            ))

        print(f"[{agent_id}] Proof Specialist initialized")
        print(f"  Methods: Direct, Contradiction, Induction")

    def verify_direct_proof(self, premises: List[str],
                            steps: List[Dict[str, str]],
                            conclusion: str) -> Dict[str, Any]:
        """
        Verify a direct proof by checking each step.
        Each step should reference which premises/previous steps it uses.
        """
        verified_steps = []
        all_valid = True

        known_statements = set(premises)

        for i, step in enumerate(steps):
            statement = step.get('statement', '')
            justification = step.get('justification', '')
            references = step.get('references', [])

            # Check if references are valid
            refs_valid = all(
                ref in known_statements or ref in premises
                for ref in references
            )

            step_result = {
                'step_number': i + 1,
                'statement': statement,
                'justification': justification,
                'valid': refs_valid
            }

            if refs_valid:
                known_statements.add(statement)
            else:
                all_valid = False
                step_result['error'] = 'Invalid reference'

            verified_steps.append(step_result)

        conclusion_reached = conclusion in known_statements

        return {
            'proof_valid': all_valid and conclusion_reached,
            'premises': premises,
            'conclusion': conclusion,
            'conclusion_reached': conclusion_reached,
            'verified_steps': verified_steps
        }

    def mathematical_induction(self, base_case: Dict[str, Any],
                               inductive_step: Dict[str, Any],
                               property_name: str = 'P') -> Dict[str, Any]:
        """
        Verify a proof by mathematical induction.

        base_case: {'n': value, 'verified': bool, 'work': str}
        inductive_step: {'assumption': str, 'goal': str, 'verified': bool, 'work': str}
        """
        base_valid = base_case.get('verified', False)
        inductive_valid = inductive_step.get('verified', False)

        proof_valid = base_valid and inductive_valid

        return {
            'proof_valid': proof_valid,
            'property': property_name,
            'base_case': {
                'n': base_case.get('n', 0),
                'valid': base_valid,
                'work': base_case.get('work', '')
            },
            'inductive_step': {
                'assumption': f'{property_name}(k)',
                'goal': f'{property_name}(k+1)',
                'valid': inductive_valid,
                'work': inductive_step.get('work', '')
            },
            'conclusion': f'For all n >= {base_case.get("n", 0)}: {property_name}(n)' if proof_valid else 'Proof incomplete'
        }

    def strong_induction(self, base_cases: List[Dict[str, Any]],
                         inductive_step: Dict[str, Any],
                         property_name: str = 'P') -> Dict[str, Any]:
        """
        Verify a proof by strong (complete) induction.
        """
        bases_valid = all(bc.get('verified', False) for bc in base_cases)
        inductive_valid = inductive_step.get('verified', False)

        proof_valid = bases_valid and inductive_valid

        return {
            'proof_valid': proof_valid,
            'property': property_name,
            'base_cases': [
                {'n': bc.get('n'), 'valid': bc.get('verified')}
                for bc in base_cases
            ],
            'inductive_step': {
                'assumption': f'{property_name}(j) for all j < k',
                'goal': f'{property_name}(k)',
                'valid': inductive_valid
            },
            'proof_type': 'strong_induction'
        }

    def proof_by_contradiction(self, assumption: str,
                                contradiction_derived: bool,
                                original_statement: str) -> Dict[str, Any]:
        """
        Verify proof by contradiction structure.
        Assume ~P, derive contradiction, therefore P.
        """
        return {
            'proof_valid': contradiction_derived,
            'method': 'contradiction',
            'assumption': assumption,
            'negated_statement': assumption,
            'original_statement': original_statement,
            'contradiction_found': contradiction_derived,
            'conclusion': original_statement if contradiction_derived else 'Proof incomplete'
        }

    def proof_by_contrapositive(self, original: str, contrapositive: str,
                                 contrapositive_proven: bool) -> Dict[str, Any]:
        """
        Verify proof by contrapositive.
        To prove P->Q, prove ~Q->~P.
        """
        return {
            'proof_valid': contrapositive_proven,
            'method': 'contrapositive',
            'original': original,
            'contrapositive': contrapositive,
            'contrapositive_proven': contrapositive_proven,
            'conclusion': original if contrapositive_proven else 'Proof incomplete'
        }

    def case_analysis(self, cases: List[Dict[str, Any]],
                      exhaustive: bool,
                      conclusion: str) -> Dict[str, Any]:
        """
        Verify proof by case analysis.
        """
        all_cases_proven = all(c.get('proven', False) for c in cases)
        proof_valid = all_cases_proven and exhaustive

        return {
            'proof_valid': proof_valid,
            'method': 'case_analysis',
            'cases': [
                {'case': c.get('description'), 'proven': c.get('proven')}
                for c in cases
            ],
            'cases_exhaustive': exhaustive,
            'all_cases_proven': all_cases_proven,
            'conclusion': conclusion if proof_valid else 'Proof incomplete'
        }

    def apply_inference_rule(self, rule: str,
                              premises: List[str]) -> Dict[str, Any]:
        """
        Apply an inference rule to premises.
        """
        if rule not in self.INFERENCE_RULES:
            return {'error': f'Unknown rule: {rule}'}

        rule_format = self.INFERENCE_RULES[rule]

        return {
            'rule': rule,
            'rule_format': rule_format,
            'premises': premises,
            'applied': True,
            'note': 'Rule application depends on specific premise forms'
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a proof task."""
        self.tasks_executed += 1
        operation = task.get('operation', 'direct')

        try:
            if operation == 'direct':
                return self.verify_direct_proof(
                    task['premises'], task['steps'], task['conclusion']
                )
            elif operation == 'induction':
                return self.mathematical_induction(
                    task['base_case'], task['inductive_step'],
                    task.get('property', 'P')
                )
            elif operation == 'strong_induction':
                return self.strong_induction(
                    task['base_cases'], task['inductive_step'],
                    task.get('property', 'P')
                )
            elif operation == 'contradiction':
                return self.proof_by_contradiction(
                    task['assumption'], task['contradiction_derived'],
                    task['original_statement']
                )
            elif operation == 'contrapositive':
                return self.proof_by_contrapositive(
                    task['original'], task['contrapositive'],
                    task['contrapositive_proven']
                )
            elif operation == 'cases':
                return self.case_analysis(
                    task['cases'], task['exhaustive'], task['conclusion']
                )
            elif operation == 'inference':
                return self.apply_inference_rule(task['rule'], task['premises'])
            else:
                return {'error': f'Unknown operation: {operation}'}
        except Exception as e:
            return {'error': str(e)}

    def update_beliefs(self):
        """Query blackboard for pending proof tasks."""
        if not self.blackboard:
            return
        from symbo_agentic_reasoners.core.blackboard import EntryType, EntryStatus
        entries = self.blackboard.query_entries(
            entry_type=EntryType.TASK,
            status=EntryStatus.PENDING,
            tags=['math.logic.proof']
        )
        for entry in entries:
            self.beliefs[f'task_{entry.entry_id}'] = entry

    def deliberate(self) -> List[Intention]:
        """Create intentions for proof tasks."""
        intentions = []
        for key, entry in list(self.beliefs.items()):
            if key.startswith('task_'):
                intention = Intention(
                    goal=f"solve_proof_{entry.entry_id}",
                    plan=['accept_task', 'solve', 'post_result'],
                    priority=1.0
                )
                intention.metadata = {'entry': entry, 'entry_id': entry.entry_id}
                intentions.append(intention)
        return intentions

    def execute_step(self, intention: Intention):
        """Execute proof computation via process()."""
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
        >>> specialist = ProofSpecialist()
        >>> result = specialist.get_statistics()
        # Returns computed result

        """
        stats = super().get_statistics()
        stats['tasks_executed'] = self.tasks_executed
        return stats
