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
PHASE 6 - SYN-3: CONJECTURE GENERATOR (Tier 3)
===============================================

Generates mathematical conjectures from patterns and data.

CAPABILITIES:
------------
- Pattern-based conjecture generation
- Property discovery
- Counterexample checking
- Conjecture ranking
- Hypothesis refinement

REFERENCE:
---------
- Agent_System_Audit.docx.md: SYN-3 Conjecture Generator
- Phase_6_Formal_Verification.md: Synthesis Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random

logger = logging.getLogger('symbo_agentic_reasoners.phase6.conjecture_generator')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class ConjectureStatus(Enum):
    """Status of a conjecture"""
    PROPOSED = "proposed"
    TESTING = "testing"
    VERIFIED = "verified"
    REFUTED = "refuted"
    OPEN = "open"


class ConjectureType(Enum):
    """Types of conjectures"""
    UNIVERSAL = "universal"       # ∀x: P(x)
    EXISTENTIAL = "existential"  # ∃x: P(x)
    CONDITIONAL = "conditional"  # P → Q
    BICONDITIONAL = "biconditional"  # P ↔ Q
    INEQUALITY = "inequality"
    IDENTITY = "identity"


@dataclass
class Conjecture:
    """
    A mathematical conjecture.
    
    Attributes:
        conjecture_id: Unique identifier
        statement: The conjecture statement
        conjecture_type: Type of conjecture
        domain: Mathematical domain
        variables: Variables involved
        evidence_for: Supporting evidence
        evidence_against: Counterevidence
        status: Current status
        confidence: Confidence score (0-1)
    """
    conjecture_id: str
    statement: str
    conjecture_type: ConjectureType
    domain: str
    variables: List[str] = field(default_factory=list)
    evidence_for: List[str] = field(default_factory=list)
    evidence_against: List[str] = field(default_factory=list)
    status: ConjectureStatus = ConjectureStatus.PROPOSED
    confidence: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.conjecture_id,
            'statement': self.statement[:100] + '...' if len(self.statement) > 100 else self.statement,
            'type': self.conjecture_type.value,
            'domain': self.domain,
            'status': self.status.value,
            'confidence': round(self.confidence, 2)
        }


@dataclass
class GenerationResult:
    """Result of conjecture generation"""
    conjectures: List[Conjecture]
    pattern_source: str
    generation_method: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'count': len(self.conjectures),
            'source': self.pattern_source,
            'method': self.generation_method,
            'conjectures': [c.to_dict() for c in self.conjectures]
        }


class ConjectureGenerator(BDIAgent):
    """
    SYN-3: Conjecture Generator
    
    DIRECTIVE:
    ---------
    Generate mathematical conjectures from patterns and data.
    
    INPUTS:
    ------
    - Observed patterns
    - Mathematical data
    - Domain constraints
    
    OUTPUTS:
    -------
    - Generated conjectures
    - Confidence rankings
    - Supporting evidence
    
    DEPENDENCIES:
    ------------
    - KM-2 (PatternIndexer): For pattern detection
    - PRV-1 (LogicalProver): For verification attempts
    
    FAILURE MODE: DEGRADED - Returns lower-confidence conjectures
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 703-712
    """
    
    # Templates for conjecture generation
    TEMPLATES = {
        'universal': "For all {var} in {domain}, {property}",
        'existential': "There exists {var} in {domain} such that {property}",
        'conditional': "If {antecedent}, then {consequent}",
        'identity': "{lhs} = {rhs}",
        'inequality': "{lhs} {op} {rhs}",
    }
    
    def __init__(
        self,
        agent_id: str = 'conjecture_generator_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Conjecture Generator
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        
        # Conjecture catalog
        self.conjectures: Dict[str, Conjecture] = {}
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.conjectures_generated = 0
        self.conjectures_verified = 0
        self.conjectures_refuted = 0
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Conjecture Generator initialized")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='synthesis.conjecture',
            agent_id=self.agent_id,
            algorithm='pattern_conjecture',
            cost='high',
            type='synthesis',
            tier='3',
            algorithms='pattern_based_hypothesis_generation'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: synthesis.conjecture")
    
    def generate_from_pattern(
        self,
        pattern: str,
        domain: str,
        variables: List[str]
    ) -> List[Conjecture]:
        """
        Generate conjectures from a pattern.
        
        Args:
            pattern: The observed pattern
            domain: Mathematical domain
            variables: Variables in the pattern
            
        Returns:
            List of generated conjectures
        """
        self.tasks_executed += 1
        conjectures = []
        
        try:
            # Generate universal conjecture
            universal = Conjecture(
                conjecture_id=f"conj_{len(self.conjectures)}",
                statement=f"For all {', '.join(variables)} in {domain}: {pattern}",
                conjecture_type=ConjectureType.UNIVERSAL,
                domain=domain,
                variables=variables,
                confidence=0.5
            )
            conjectures.append(universal)
            self.conjectures[universal.conjecture_id] = universal
            
            # Generate conditional variant
            if len(variables) > 0:
                conditional = Conjecture(
                    conjecture_id=f"conj_{len(self.conjectures)}",
                    statement=f"If {variables[0]} satisfies P, then {pattern}",
                    conjecture_type=ConjectureType.CONDITIONAL,
                    domain=domain,
                    variables=variables,
                    confidence=0.4
                )
                conjectures.append(conditional)
                self.conjectures[conditional.conjecture_id] = conditional
            
            self.conjectures_generated += len(conjectures)
            self.tasks_succeeded += 1
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Pattern generation failed: {type(e).__name__}: {e}")
        
        return conjectures
    
    def generate_from_examples(
        self,
        examples: List[Dict[str, Any]],
        domain: str
    ) -> List[Conjecture]:
        """
        Generate conjectures from examples.
        
        Args:
            examples: List of example data points
            domain: Mathematical domain
            
        Returns:
            List of generated conjectures
        """
        self.tasks_executed += 1
        conjectures = []
        
        try:
            if not examples:
                return conjectures
            
            # Find common properties
            keys = set(examples[0].keys())
            for ex in examples[1:]:
                keys &= set(ex.keys())
            
            for key in keys:
                values = [ex.get(key) for ex in examples]
                
                # Check for constant property
                if len(set(str(v) for v in values)) == 1:
                    conj = Conjecture(
                        conjecture_id=f"conj_{len(self.conjectures)}",
                        statement=f"{key} = {values[0]} for all examples",
                        conjecture_type=ConjectureType.IDENTITY,
                        domain=domain,
                        evidence_for=[f"Observed in {len(examples)} examples"],
                        confidence=0.8
                    )
                    conjectures.append(conj)
                    self.conjectures[conj.conjecture_id] = conj
                
                # Check for monotonic property (if numeric)
                if all(isinstance(v, (int, float)) for v in values):
                    if values == sorted(values):
                        conj = Conjecture(
                            conjecture_id=f"conj_{len(self.conjectures)}",
                            statement=f"{key} is monotonically non-decreasing",
                            conjecture_type=ConjectureType.UNIVERSAL,
                            domain=domain,
                            confidence=0.6
                        )
                        conjectures.append(conj)
                        self.conjectures[conj.conjecture_id] = conj
            
            self.conjectures_generated += len(conjectures)
            self.tasks_succeeded += 1
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Example generation failed: {type(e).__name__}: {e}")
        
        return conjectures
    
    def generate_from_template(
        self,
        template_type: str,
        **kwargs
    ) -> Conjecture:
        """
        Generate a conjecture from a template.
        
        Args:
            template_type: Type of template to use
            **kwargs: Template parameters
            
        Returns:
            Generated conjecture
        """
        self.tasks_executed += 1
        self.conjectures_generated += 1
        
        template = self.TEMPLATES.get(template_type, "{statement}")
        
        try:
            statement = template.format(**kwargs)
        except KeyError as e:
            statement = f"INCOMPLETE: {template} (missing {e})"
        
        conj_type = {
            'universal': ConjectureType.UNIVERSAL,
            'existential': ConjectureType.EXISTENTIAL,
            'conditional': ConjectureType.CONDITIONAL,
            'identity': ConjectureType.IDENTITY,
            'inequality': ConjectureType.INEQUALITY
        }.get(template_type, ConjectureType.UNIVERSAL)
        
        conj = Conjecture(
            conjecture_id=f"conj_{len(self.conjectures)}",
            statement=statement,
            conjecture_type=conj_type,
            domain=kwargs.get('domain', 'general'),
            variables=list(kwargs.get('variables', [])),
            confidence=0.5
        )
        
        self.conjectures[conj.conjecture_id] = conj
        self.tasks_succeeded += 1
        
        return conj
    
    def add_evidence(
        self,
        conjecture_id: str,
        evidence: str,
        supports: bool
    ):
        """
        Add evidence for or against a conjecture.
        
        Args:
            conjecture_id: Conjecture to update
            evidence: Evidence description
            supports: True if supporting, False if against
        """
        if conjecture_id not in self.conjectures:
            return
        
        conj = self.conjectures[conjecture_id]
        
        if supports:
            conj.evidence_for.append(evidence)
            conj.confidence = min(1.0, conj.confidence + 0.1)
        else:
            conj.evidence_against.append(evidence)
            conj.confidence = max(0.0, conj.confidence - 0.15)
        
        # Update status based on evidence
        if conj.confidence >= 0.9 and len(conj.evidence_for) > 3:
            conj.status = ConjectureStatus.VERIFIED
            self.conjectures_verified += 1
        elif conj.confidence <= 0.1 or len(conj.evidence_against) > 2:
            conj.status = ConjectureStatus.REFUTED
            self.conjectures_refuted += 1
        elif len(conj.evidence_for) + len(conj.evidence_against) > 5:
            conj.status = ConjectureStatus.OPEN
    
    def test_conjecture(
        self,
        conjecture_id: str,
        test_cases: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """
        Test a conjecture against test cases.
        
        Args:
            conjecture_id: Conjecture to test
            test_cases: Cases to test against
            
        Returns:
            Tuple of (all_passed, list of failure descriptions)
        """
        conj = self.conjectures.get(conjecture_id)
        if not conj:
            return False, ["Conjecture not found"]
        
        conj.status = ConjectureStatus.TESTING
        failures = []
        
        for i, case in enumerate(test_cases):
            # Simplified testing - would delegate to actual evaluator
            if "counterexample" in case:
                failures.append(f"Case {i+1}: {case['counterexample']}")
                self.add_evidence(conjecture_id, f"Failed case {i+1}", False)
        
        if not failures:
            self.add_evidence(conjecture_id, f"Passed {len(test_cases)} tests", True)
        
        return len(failures) == 0, failures
    
    def rank_conjectures(
        self,
        domain: Optional[str] = None
    ) -> List[Conjecture]:
        """
        Rank conjectures by confidence and evidence.
        
        Args:
            domain: Optional domain filter
            
        Returns:
            Sorted list of conjectures
        """
        conjs = list(self.conjectures.values())
        
        if domain:
            conjs = [c for c in conjs if c.domain == domain]
        
        # Sort by confidence, then by evidence balance
        conjs.sort(
            key=lambda c: (c.confidence, len(c.evidence_for) - len(c.evidence_against)),
            reverse=True
        )
        
        return conjs
    
    def process(self, task_entry: Any) -> Any:
        """Process conjecture generation task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing conjecture task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'generate')
            
            if operation == 'from_pattern':
                pattern = metadata.get('pattern', '')
                domain = metadata.get('domain', 'general')
                variables = metadata.get('variables', [])
                conjs = self.generate_from_pattern(pattern, domain, variables)
                result = {'conjectures': [c.to_dict() for c in conjs]}
                
            elif operation == 'from_examples':
                examples = metadata.get('examples', [])
                domain = metadata.get('domain', 'general')
                conjs = self.generate_from_examples(examples, domain)
                result = {'conjectures': [c.to_dict() for c in conjs]}
                
            elif operation == 'from_template':
                template = metadata.get('template', 'universal')
                kwargs = metadata.get('params', {})
                conj = self.generate_from_template(template, **kwargs)
                result = conj.to_dict()
                
            elif operation == 'rank':
                domain = metadata.get('domain')
                ranked = self.rank_conjectures(domain)
                result = {'ranked': [c.to_dict() for c in ranked]}
                
            elif operation == 'test':
                conj_id = metadata.get('conjecture_id')
                cases = metadata.get('test_cases', [])
                passed, failures = self.test_conjecture(conj_id, cases)
                result = {'passed': passed, 'failures': failures}
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Conjecture task failed: {type(e).__name__}: {e}")
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
            tags=['conjecture', 'synthesis'],
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
            tags=['error', 'conjecture'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for conjecture generation tasks."""
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['conjecture'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['synthesis'], status=EntryStatus.PENDING)
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
        """DELIBERATE: Create conjecture generation plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'from_pattern')
            steps = ['claim_task', 'parse_input', f'generate_{operation}', 'rank_results', 'post_result']
            intention = Intention(
                plan_id=f'conjecture_{operation}_{task_id}',
                steps=steps,
                target_desire='conjecture_generation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform conjecture generation."""
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
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                intention.metadata['pattern'] = metadata.get('pattern', '')
                intention.metadata['domain'] = metadata.get('domain', 'general')
                intention.metadata['variables'] = metadata.get('variables', [])
                intention.metadata['examples'] = metadata.get('examples', [])
                intention.advance()
            elif action == 'generate_from_pattern':
                pattern = intention.metadata.get('pattern', '')
                domain = intention.metadata.get('domain', 'general')
                variables = intention.metadata.get('variables', [])
                conjs = self.generate_from_pattern(pattern, domain, variables)
                intention.metadata['conjectures'] = conjs
                intention.advance()
            elif action == 'generate_from_examples':
                examples = intention.metadata.get('examples', [])
                domain = intention.metadata.get('domain', 'general')
                conjs = self.generate_from_examples(examples, domain)
                intention.metadata['conjectures'] = conjs
                intention.advance()
            elif action == 'rank_results':
                conjs = intention.metadata.get('conjectures', [])
                ranked = sorted(conjs, key=lambda c: c.confidence, reverse=True)
                intention.metadata['ranked_conjectures'] = ranked
                intention.advance()
            elif action == 'post_result':
                ranked = intention.metadata.get('ranked_conjectures', [])
                result = {'conjectures': [c.to_dict() for c in ranked]}
                if self.blackboard:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result)),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['conjecture', 'synthesis', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'result': str(result), 'result_str': str(result)}
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
        """Get generator statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'conjectures_generated': self.conjectures_generated,
            'conjectures_verified': self.conjectures_verified,
            'conjectures_refuted': self.conjectures_refuted,
            'open_conjectures': sum(1 for c in self.conjectures.values()
                                   if c.status == ConjectureStatus.OPEN)
        })
        return stats


if __name__ == "__main__":
    """Test Conjecture Generator"""
    print("=" * 80)
    print("PHASE 6 - CONJECTURE GENERATOR TEST")
    print("=" * 80)
    print()
    
    # Initialize generator
    generator = ConjectureGenerator()
    print()
    
    # Test 1: Generate from pattern
    print("Test 1: Generate from Pattern")
    conjs = generator.generate_from_pattern(
        pattern="n² > n for n > 1",
        domain="natural numbers",
        variables=["n"]
    )
    for c in conjs:
        print(f"  - {c.statement}")
        print(f"    Confidence: {c.confidence}")
    print()
    
    # Test 2: Generate from examples
    print("Test 2: Generate from Examples")
    examples = [
        {"x": 1, "y": 1},
        {"x": 2, "y": 4},
        {"x": 3, "y": 9},
        {"x": 4, "y": 16}
    ]
    conjs = generator.generate_from_examples(examples, "integers")
    for c in conjs:
        print(f"  - {c.statement}")
    print()
    
    # Test 3: Generate from template
    print("Test 3: Generate from Template")
    conj = generator.generate_from_template(
        'universal',
        var="p",
        domain="primes",
        property="p > 1"
    )
    print(f"  Statement: {conj.statement}")
    print()
    
    # Test 4: Add evidence and rank
    print("Test 4: Add Evidence and Rank")
    generator.add_evidence(conj.conjecture_id, "Verified for p < 1000", True)
    generator.add_evidence(conj.conjecture_id, "Follows from definition", True)
    
    ranked = generator.rank_conjectures()
    print(f"  Ranked conjectures: {len(ranked)}")
    for c in ranked[:3]:
        print(f"    - {c.statement[:50]}... ({c.confidence:.2f})")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(generator.get_statistics(), indent=2))
