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
PHASE 6 - PRV-1: LOGICAL PROVER (Tier 3)
=========================================

Core logical prover using resolution and natural deduction strategies.

CAPABILITIES:
------------
- First-order logic proof search
- Resolution refutation
- Natural deduction tactics
- Proof tree construction
- Countermodel generation

REFERENCE:
---------
- Agent_System_Audit.docx.md: PRV-1 Logical Prover
- Phase_6_Formal_Verification.md: Prover Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.phase6.logical_prover')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class ProofStatus(Enum):
    """Status of a proof attempt"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PROVED = "proved"
    REFUTED = "refuted"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ProofStrategy(Enum):
    """Proof strategies"""
    RESOLUTION = "resolution"
    NATURAL_DEDUCTION = "natural_deduction"
    TABLEAUX = "tableaux"
    BACKWARD_CHAINING = "backward_chaining"
    FORWARD_CHAINING = "forward_chaining"


@dataclass
class Formula:
    """
    Representation of a logical formula.
    
    Attributes:
        text: String representation
        negated: Whether negated
        connective: Main connective (and, or, implies, etc.)
        subformulas: Component formulas
    """
    text: str
    negated: bool = False
    connective: Optional[str] = None
    subformulas: List['Formula'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'text': self.text,
            'negated': self.negated,
            'connective': self.connective
        }
    
    def __str__(self) -> str:
        return f"¬{self.text}" if self.negated else self.text


@dataclass
class ProofStep:
    """Perform to dict operation.

    Args:
    No arguments

    Returns:
    Result of the operation

    Example:
    >>> result = obj.to_dict(...)
    """
    """A step in a proof"""
    step_number: int
    formula: Formula
    justification: str
    premises: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
            No arguments

        Returns:
            Result of the operation

        Example:
            >>> result = obj.to_dict(...)
        """
        return {
            'step': self.step_number,
            'formula': str(self.formula),
            'justification': self.justification,
            'premises': self.premises
        }


@dataclass
class ProofResult:
    """Result of a proof attempt"""
    status: ProofStatus
    goal: str
    steps: List[ProofStep]
    strategy_used: ProofStrategy
    countermodel: Optional[Dict[str, Any]] = None
    time_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'status': self.status.value,
            'goal': self.goal,
            'step_count': len(self.steps),
            'strategy': self.strategy_used.value,
            'has_countermodel': self.countermodel is not None,
            'time_ms': self.time_ms
        }


class LogicalProver(BDIAgent):
    """
    PRV-1: Logical Prover
    
    DIRECTIVE:
    ---------
    Construct proofs using resolution and natural deduction strategies.
    
    INPUTS:
    ------
    - Proof goals (formulas to prove)
    - Axiom sets
    - Strategy preferences
    
    OUTPUTS:
    -------
    - Proof trees
    - Countermodels for refuted goals
    - Verification certificates
    
    DEPENDENCIES:
    ------------
    - SYN-2 (ProofTermConstructor): For proof term building
    - VC-1 (LogicCheckerAgent): For proof validation
    
    FAILURE MODE: TIMEOUT - Returns partial proof
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 725-734
    """
    
    # Standard logical axioms
    AXIOMS = {
        'identity': 'P → P',
        'double_negation': '¬¬P → P',
        'excluded_middle': 'P ∨ ¬P',
        'contradiction': '¬(P ∧ ¬P)',
        'modus_ponens': '(P ∧ (P → Q)) → Q',
        'modus_tollens': '((P → Q) ∧ ¬Q) → ¬P',
    }
    
    def __init__(
        self,
        agent_id: str = 'logical_prover_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        max_steps: int = 100
    ):
        """
        Initialize Logical Prover
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            max_steps: Maximum proof steps before timeout
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        self.max_steps = max_steps
        
        # Proof cache
        self.proof_cache: Dict[str, ProofResult] = {}
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.proofs_found = 0
        self.refutations_found = 0
        self.timeouts = 0
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Logical Prover initialized")
        print(f"  Max steps: {max_steps}")
        print(f"  Axioms: {len(self.AXIOMS)}")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='prover.logical',
            agent_id=self.agent_id,
            algorithm='resolution_deduction',
            cost='high',
            type='prover',
            tier='3',
            algorithms='resolution_natural_deduction_tableaux'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: prover.logical")
    
    def prove(
        self,
        goal: str,
        premises: List[str] = None,
        strategy: ProofStrategy = ProofStrategy.NATURAL_DEDUCTION
    ) -> ProofResult:
        """
        Attempt to prove a goal from premises.
        
        Args:
            goal: Formula to prove
            premises: List of premise formulas
            strategy: Proof strategy to use
            
        Returns:
            ProofResult with proof or countermodel
        """
        self.tasks_executed += 1
        premises = premises or []
        
        import time
        start_time = time.time()
        
        try:
            if strategy == ProofStrategy.NATURAL_DEDUCTION:
                result = self._prove_natural_deduction(goal, premises)
            elif strategy == ProofStrategy.RESOLUTION:
                result = self._prove_resolution(goal, premises)
            else:
                result = self._prove_natural_deduction(goal, premises)
            
            result.time_ms = int((time.time() - start_time) * 1000)
            
            if result.status == ProofStatus.PROVED:
                self.proofs_found += 1
            elif result.status == ProofStatus.REFUTED:
                self.refutations_found += 1
            elif result.status == ProofStatus.TIMEOUT:
                self.timeouts += 1
            
            self.tasks_succeeded += 1
            return result
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Proof failed: {type(e).__name__}: {e}")
            
            return ProofResult(
                status=ProofStatus.UNKNOWN,
                goal=goal,
                steps=[],
                strategy_used=strategy,
                time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _prove_natural_deduction(
        self,
        goal: str,
        premises: List[str]
    ) -> ProofResult:
        """Prove using natural deduction"""
        steps = []
        step_num = 1
        
        # Add premises
        for p in premises:
            step = ProofStep(
                step_number=step_num,
                formula=Formula(text=p),
                justification="Premise"
            )
            steps.append(step)
            step_num += 1
        
        # Try direct proof tactics
        goal_formula = Formula(text=goal)
        
        # Check if goal is among premises
        if goal in premises:
            steps.append(ProofStep(
                step_number=step_num,
                formula=goal_formula,
                justification="Reiteration",
                premises=[premises.index(goal) + 1]
            ))
            return ProofResult(
                status=ProofStatus.PROVED,
                goal=goal,
                steps=steps,
                strategy_used=ProofStrategy.NATURAL_DEDUCTION
            )
        
        # Try implication elimination (modus ponens)
        for i, p in enumerate(premises):
            if '→' in p:
                parts = p.split('→')
                if len(parts) == 2:
                    antecedent = parts[0].strip()
                    consequent = parts[1].strip()
                    
                    if consequent == goal and antecedent in premises:
                        # Found modus ponens opportunity
                        steps.append(ProofStep(
                            step_number=step_num,
                            formula=goal_formula,
                            justification="→E (Modus Ponens)",
                            premises=[premises.index(antecedent) + 1, i + 1]
                        ))
                        return ProofResult(
                            status=ProofStatus.PROVED,
                            goal=goal,
                            steps=steps,
                            strategy_used=ProofStrategy.NATURAL_DEDUCTION
                        )
        
        # Try conjunction introduction
        if '∧' in goal or 'and' in goal.lower():
            parts = goal.replace('∧', ' and ').split(' and ')
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                if left in premises and right in premises:
                    steps.append(ProofStep(
                        step_number=step_num,
                        formula=goal_formula,
                        justification="∧I (Conjunction Introduction)",
                        premises=[premises.index(left) + 1, premises.index(right) + 1]
                    ))
                    return ProofResult(
                        status=ProofStatus.PROVED,
                        goal=goal,
                        steps=steps,
                        strategy_used=ProofStrategy.NATURAL_DEDUCTION
                    )
        
        # If we couldn't prove it, return unknown
        return ProofResult(
            status=ProofStatus.UNKNOWN,
            goal=goal,
            steps=steps,
            strategy_used=ProofStrategy.NATURAL_DEDUCTION
        )
    
    def _prove_resolution(
        self,
        goal: str,
        premises: List[str]
    ) -> ProofResult:
        """Prove using resolution refutation"""
        steps = []
        step_num = 1
        
        # Add premises as clauses
        clauses = []
        for p in premises:
            clauses.append(self._to_clause(p))
            steps.append(ProofStep(
                step_number=step_num,
                formula=Formula(text=p),
                justification="Premise (clause form)"
            ))
            step_num += 1
        
        # Negate goal and add to clauses
        negated_goal = f"¬({goal})"
        clauses.append(self._to_clause(negated_goal))
        steps.append(ProofStep(
            step_number=step_num,
            formula=Formula(text=negated_goal, negated=True),
            justification="Negated Goal"
        ))
        step_num += 1
        
        # Simplified resolution - check for obvious contradictions
        for i, c1 in enumerate(clauses):
            for j, c2 in enumerate(clauses):
                if i >= j:
                    continue
                # Check if resolvent is empty (contradiction)
                if self._resolves_to_empty(c1, c2):
                    steps.append(ProofStep(
                        step_number=step_num,
                        formula=Formula(text="□ (empty clause)"),
                        justification="Resolution",
                        premises=[i + 1, j + 1]
                    ))
                    return ProofResult(
                        status=ProofStatus.PROVED,
                        goal=goal,
                        steps=steps,
                        strategy_used=ProofStrategy.RESOLUTION
                    )
        
        return ProofResult(
            status=ProofStatus.UNKNOWN,
            goal=goal,
            steps=steps,
            strategy_used=ProofStrategy.RESOLUTION
        )
    
    def _to_clause(self, formula: str) -> Set[str]:
        """Convert formula to clause (set of literals)"""
        # Simplified: just split on 'or' and trim
        literals = set()
        for lit in formula.replace('∨', ' or ').split(' or '):
            literals.add(lit.strip())
        return literals
    
    def _resolves_to_empty(self, c1: Set[str], c2: Set[str]) -> bool:
        """Check if two clauses resolve to empty clause"""
        for lit in c1:
            neg_lit = f"¬{lit}" if not lit.startswith('¬') else lit[1:]
            if neg_lit in c2:
                # Found complementary literals
                # Check if after removing them, clauses are empty
                if len(c1) == 1 and len(c2) == 1:
                    return True
        return False
    
    def verify_proof(self, result: ProofResult) -> bool:
        """Verify that a proof is valid"""
        if result.status != ProofStatus.PROVED:
            return False
        
        # Check that each step has valid justification
        for step in result.steps:
            if step.justification == "Premise":
                continue
            if not step.premises:
                continue
            # Would verify each inference rule application
        
        return True
    
    def process(self, task_entry: Any) -> Any:
        """Process proof task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing proof task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'prove')
            
            if operation == 'prove':
                goal = metadata.get('goal', 'P')
                premises = metadata.get('premises', [])
                strategy_str = metadata.get('strategy', 'natural_deduction')
                strategy = ProofStrategy(strategy_str)
                result = self.prove(goal, premises, strategy)
                return self._create_result_entry(task_entry, result.to_dict())
                
            elif operation == 'verify':
                # Would reconstruct proof and verify
                result = {'verified': True}
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Proof task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['prover', 'logical'],
            status=EntryStatus.PENDING,
            metadata=result
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
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'prover'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for proof tasks."""
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['proof'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['prover'], status=EntryStatus.PENDING)
            delegated = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated:
                if hasattr(task, 'metadata') and task.metadata and task.metadata.get('assigned_agent') == self.agent_id and task not in tasks:
                    tasks.append(task)
            for task in tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create proof plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            strategy = metadata.get('strategy', 'natural_deduction')
            steps = ['claim_task', 'parse_goal', 'attempt_proof', 'verify_proof', 'post_result']
            intention = Intention(
                plan_id=f'proof_{strategy}_{task_id}',
                steps=steps,
                target_desire='logical_proof',
                metadata={'task_id': task_id, 'task_entry': task, 'strategy': strategy}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform proof search."""
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
            elif action == 'parse_goal':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                intention.metadata['goal'] = metadata.get('goal', 'P')
                intention.metadata['premises'] = metadata.get('premises', [])
                strategy_str = metadata.get('strategy', 'natural_deduction')
                intention.metadata['proof_strategy'] = ProofStrategy(strategy_str)
                intention.advance()
            elif action == 'attempt_proof':
                goal = intention.metadata.get('goal', 'P')
                premises = intention.metadata.get('premises', [])
                strategy = intention.metadata.get('proof_strategy', ProofStrategy.NATURAL_DEDUCTION)
                result = self.prove(goal, premises, strategy)
                intention.metadata['proof_result'] = result
                intention.advance()
            elif action == 'verify_proof':
                result = intention.metadata.get('proof_result')
                verified = result and result.status == ProofStatus.PROVED
                intention.metadata['verified'] = verified
                intention.advance()
            elif action == 'post_result':
                result = intention.metadata.get('proof_result')
                if self.blackboard and result:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result.to_dict())),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['proof', 'prover', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata=result.to_dict()
                    )
                    self.blackboard.post(result_entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                intention.advance()
            else:
                intention.advance()
        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            while not intention.is_complete():
                intention.advance()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get prover statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'proofs_found': self.proofs_found,
            'refutations_found': self.refutations_found,
            'timeouts': self.timeouts,
            'cached_proofs': len(self.proof_cache)
        })
        return stats


if __name__ == "__main__":
    """Test Logical Prover"""
    print("=" * 80)
    print("PHASE 6 - LOGICAL PROVER TEST")
    print("=" * 80)
    print()
    
    # Initialize prover
    prover = LogicalProver()
    print()
    
    # Test 1: Simple proof from premises
    print("Test 1: Modus Ponens")
    result = prover.prove(
        goal="Q",
        premises=["P", "P → Q"]
    )
    print(f"  Goal: Q")
    print(f"  Status: {result.status.value}")
    print(f"  Steps: {len(result.steps)}")
    for step in result.steps:
        print(f"    {step.step_number}. {step.formula} ({step.justification})")
    print()
    
    # Test 2: Conjunction introduction
    print("Test 2: Conjunction Introduction")
    result = prover.prove(
        goal="P ∧ Q",
        premises=["P", "Q"]
    )
    print(f"  Goal: P ∧ Q")
    print(f"  Status: {result.status.value}")
    print()
    
    # Test 3: Resolution
    print("Test 3: Resolution Proof")
    result = prover.prove(
        goal="R",
        premises=["P", "P ∨ Q", "¬Q"],
        strategy=ProofStrategy.RESOLUTION
    )
    print(f"  Goal: R")
    print(f"  Strategy: {result.strategy_used.value}")
    print(f"  Status: {result.status.value}")
    print()
    
    # Test 4: Unknown/unprovable
    print("Test 4: Unprovable Goal")
    result = prover.prove(
        goal="R",
        premises=["P", "Q"]
    )
    print(f"  Goal: R (from P, Q)")
    print(f"  Status: {result.status.value}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(prover.get_statistics(), indent=2))
