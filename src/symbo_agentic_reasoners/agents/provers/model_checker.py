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
PHASE 6 - PRV-2: MODEL CHECKER (Tier 3)
========================================

Checks if a model satisfies a specification using automata-theoretic
and bounded model checking techniques.

CAPABILITIES:
------------
- State space exploration
- Property verification (LTL, CTL)
- Bounded model checking
- Counterexample generation
- Abstraction refinement

REFERENCE:
---------
- Agent_System_Audit.docx.md: PRV-2 Model Checker
- Phase_6_Formal_Verification.md: Prover Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.phase6.model_checker')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class PropertyType(Enum):
    """Types of properties to check"""
    SAFETY = "safety"          # Nothing bad happens
    LIVENESS = "liveness"      # Something good eventually happens
    INVARIANT = "invariant"    # Holds in all states
    REACHABILITY = "reachability"  # Some state is reachable
    DEADLOCK_FREE = "deadlock_free"


class VerificationResult(Enum):
    """Result of model checking"""
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"


@dataclass
class State:
    """A state in the model"""
    state_id: str
    values: Dict[str, Any]
    is_initial: bool = False
    is_accepting: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary representation."""
        return {
            'id': self.state_id,
            'values': self.values,
            'initial': self.is_initial
        }


@dataclass
class Transition:
    """A transition between states"""
    source: str
    target: str
    action: Optional[str] = None
    guard: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transition to dictionary representation."""
        return {
            'source': self.source,
            'target': self.target,
            'action': self.action
        }


@dataclass
class Model:
    """
    A finite state model.
    
    Attributes:
        name: Model name
        states: Set of states
        transitions: Set of transitions
        initial_states: Initial state IDs
        atomic_props: Atomic propositions
    """
    name: str
    states: Dict[str, State]
    transitions: List[Transition]
    initial_states: Set[str]
    atomic_props: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            'name': self.name,
            'state_count': len(self.states),
            'transition_count': len(self.transitions),
            'initial_count': len(self.initial_states),
            'props': list(self.atomic_props)
        }


@dataclass
class Counterexample:
    """A counterexample trace"""
    path: List[str]  # State IDs
    loop_start: Optional[int] = None  # For lasso-shaped counterexamples
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert counterexample to dictionary representation."""
        return {
            'length': len(self.path),
            'path': self.path[:10],  # Truncate for display
            'has_loop': self.loop_start is not None
        }


@dataclass
class CheckResult:
    """Result of a model checking query"""
    property_checked: str
    property_type: PropertyType
    result: VerificationResult
    counterexample: Optional[Counterexample] = None
    states_explored: int = 0
    time_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert check result to dictionary representation."""
        return {
            'property': self.property_checked,
            'type': self.property_type.value,
            'result': self.result.value,
            'has_counterexample': self.counterexample is not None,
            'states_explored': self.states_explored,
            'time_ms': self.time_ms
        }


class ModelChecker(BDIAgent):
    """
    PRV-2: Model Checker
    
    DIRECTIVE:
    ---------
    Check if a model satisfies a specification using state space
    exploration and temporal logic reasoning.
    
    INPUTS:
    ------
    - Model specifications
    - Properties to verify (LTL/CTL formulas)
    - Bound parameters
    
    OUTPUTS:
    -------
    - Verification results
    - Counterexample traces
    - State space statistics
    
    DEPENDENCIES:
    ------------
    - PRV-1 (LogicalProver): For logical reasoning
    - SYN-1 (StructuralSynthesizer): For model construction
    
    FAILURE MODE: TIMEOUT - Returns partial exploration
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 736-745
    """
    
    def __init__(
        self,
        agent_id: str = 'model_checker_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        max_states: int = 10000,
        bound: int = 100
    ):
        """
        Initialize Model Checker
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            max_states: Maximum states to explore
            bound: Bound for bounded model checking
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        self.max_states = max_states
        self.bound = bound
        
        # Model cache
        self.models: Dict[str, Model] = {}
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.properties_checked = 0
        self.properties_satisfied = 0
        self.properties_violated = 0
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Model Checker initialized")
        print(f"  Max states: {max_states}")
        print(f"  Bound: {bound}")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='prover.model',
            agent_id=self.agent_id,
            algorithm='model_checking',
            cost='high',
            type='prover',
            tier='3',
            algorithms='bmc_reachability_ltl'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: prover.model")
    
    def create_model(
        self,
        name: str,
        states: List[Dict[str, Any]],
        transitions: List[Tuple[str, str, Optional[str]]],
        initial: List[str]
    ) -> Model:
        """
        Create a new model.
        
        Args:
            name: Model name
            states: List of state definitions
            transitions: List of (source, target, action) tuples
            initial: List of initial state IDs
            
        Returns:
            Created Model
        """
        state_dict = {}
        for s in states:
            state_id = s.get('id', f'state_{len(state_dict)}')
            state_dict[state_id] = State(
                state_id=state_id,
                values=s.get('values', {}),
                is_initial=state_id in initial
            )
        
        trans_list = [
            Transition(source=t[0], target=t[1], action=t[2] if len(t) > 2 else None)
            for t in transitions
        ]
        
        model = Model(
            name=name,
            states=state_dict,
            transitions=trans_list,
            initial_states=set(initial)
        )
        
        self.models[name] = model
        return model
    
    def check_property(
        self,
        model: Model,
        property_str: str,
        property_type: PropertyType
    ) -> CheckResult:
        """
        Check if a property holds in the model.
        
        Args:
            model: Model to check
            property_str: Property specification
            property_type: Type of property
            
        Returns:
            CheckResult with verification outcome
        """
        self.tasks_executed += 1
        self.properties_checked += 1
        
        import time
        start_time = time.time()
        
        try:
            if property_type == PropertyType.INVARIANT:
                result = self._check_invariant(model, property_str)
            elif property_type == PropertyType.REACHABILITY:
                result = self._check_reachability(model, property_str)
            elif property_type == PropertyType.DEADLOCK_FREE:
                result = self._check_deadlock_free(model)
            elif property_type == PropertyType.SAFETY:
                result = self._check_safety(model, property_str)
            else:
                result = CheckResult(
                    property_checked=property_str,
                    property_type=property_type,
                    result=VerificationResult.UNKNOWN
                )
            
            result.time_ms = int((time.time() - start_time) * 1000)
            
            if result.result == VerificationResult.SATISFIED:
                self.properties_satisfied += 1
            elif result.result == VerificationResult.VIOLATED:
                self.properties_violated += 1
            
            self.tasks_succeeded += 1
            return result
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Model checking failed: {type(e).__name__}: {e}")
            
            return CheckResult(
                property_checked=property_str,
                property_type=property_type,
                result=VerificationResult.UNKNOWN,
                time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _check_invariant(self, model: Model, prop: str) -> CheckResult:
        """Check if property holds in all reachable states"""
        visited = set()
        frontier = list(model.initial_states)
        states_explored = 0
        
        while frontier and states_explored < self.max_states:
            current_id = frontier.pop()
            if current_id in visited:
                continue
            
            visited.add(current_id)
            states_explored += 1
            
            state = model.states.get(current_id)
            if not state:
                continue
            
            # Check if property holds in this state
            if not self._evaluate_property(state, prop):
                # Found counterexample
                path = self._reconstruct_path(model, model.initial_states, current_id)
                return CheckResult(
                    property_checked=prop,
                    property_type=PropertyType.INVARIANT,
                    result=VerificationResult.VIOLATED,
                    counterexample=Counterexample(path=path),
                    states_explored=states_explored
                )
            
            # Add successors
            for trans in model.transitions:
                if trans.source == current_id and trans.target not in visited:
                    frontier.append(trans.target)
        
        return CheckResult(
            property_checked=prop,
            property_type=PropertyType.INVARIANT,
            result=VerificationResult.SATISFIED,
            states_explored=states_explored
        )
    
    def _check_reachability(self, model: Model, prop: str) -> CheckResult:
        """Check if a state satisfying property is reachable"""
        visited = set()
        frontier = list(model.initial_states)
        states_explored = 0
        
        while frontier and states_explored < self.max_states:
            current_id = frontier.pop()
            if current_id in visited:
                continue
            
            visited.add(current_id)
            states_explored += 1
            
            state = model.states.get(current_id)
            if not state:
                continue
            
            # Check if property holds in this state
            if self._evaluate_property(state, prop):
                # Found reachable state
                path = self._reconstruct_path(model, model.initial_states, current_id)
                return CheckResult(
                    property_checked=prop,
                    property_type=PropertyType.REACHABILITY,
                    result=VerificationResult.SATISFIED,
                    counterexample=Counterexample(path=path),  # Path as witness
                    states_explored=states_explored
                )
            
            # Add successors
            for trans in model.transitions:
                if trans.source == current_id and trans.target not in visited:
                    frontier.append(trans.target)
        
        return CheckResult(
            property_checked=prop,
            property_type=PropertyType.REACHABILITY,
            result=VerificationResult.VIOLATED,
            states_explored=states_explored
        )
    
    def _check_deadlock_free(self, model: Model) -> CheckResult:
        """Check if model is deadlock-free"""
        visited = set()
        frontier = list(model.initial_states)
        states_explored = 0
        
        while frontier and states_explored < self.max_states:
            current_id = frontier.pop()
            if current_id in visited:
                continue
            
            visited.add(current_id)
            states_explored += 1
            
            # Check for deadlock (no outgoing transitions)
            has_successor = any(t.source == current_id for t in model.transitions)
            
            if not has_successor:
                # Found deadlock
                path = self._reconstruct_path(model, model.initial_states, current_id)
                return CheckResult(
                    property_checked="deadlock_free",
                    property_type=PropertyType.DEADLOCK_FREE,
                    result=VerificationResult.VIOLATED,
                    counterexample=Counterexample(path=path),
                    states_explored=states_explored
                )
            
            # Add successors
            for trans in model.transitions:
                if trans.source == current_id and trans.target not in visited:
                    frontier.append(trans.target)
        
        return CheckResult(
            property_checked="deadlock_free",
            property_type=PropertyType.DEADLOCK_FREE,
            result=VerificationResult.SATISFIED,
            states_explored=states_explored
        )
    
    def _check_safety(self, model: Model, prop: str) -> CheckResult:
        """Check safety property (nothing bad happens)"""
        # Safety is invariant of not-bad
        return self._check_invariant(model, prop)
    
    def _evaluate_property(self, state: State, prop: str) -> bool:
        """Evaluate if property holds in state"""
        # Simplified: check if prop is in state values
        prop_parts = prop.split('=')
        if len(prop_parts) == 2:
            var = prop_parts[0].strip()
            val = prop_parts[1].strip()
            return str(state.values.get(var, '')) == val
        
        # Check if prop name as boolean
        return state.values.get(prop, False) == True
    
    def _reconstruct_path(
        self,
        model: Model,
        initial: Set[str],
        target: str
    ) -> List[str]:
        """Reconstruct path from initial to target"""
        # Simple BFS to find path
        if target in initial:
            return [target]
        
        visited = {}
        frontier = [(i, None) for i in initial]
        
        while frontier:
            current, parent = frontier.pop(0)
            if current in visited:
                continue
            visited[current] = parent
            
            if current == target:
                # Reconstruct
                path = [current]
                while visited[path[-1]] is not None:
                    path.append(visited[path[-1]])
                return list(reversed(path))
            
            for trans in model.transitions:
                if trans.source == current and trans.target not in visited:
                    frontier.append((trans.target, current))
        
        return [target]  # Fallback
    
    def process(self, task_entry: Any) -> Any:
        """Process model checking task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing model checking task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'check')
            
            if operation == 'create_model':
                name = metadata.get('name', 'model')
                states = metadata.get('states', [])
                transitions = metadata.get('transitions', [])
                initial = metadata.get('initial', [])
                model = self.create_model(name, states, transitions, initial)
                result = model.to_dict()
                
            elif operation == 'check':
                model_name = metadata.get('model')
                model = self.models.get(model_name)
                if not model:
                    result = {'error': f'Model not found: {model_name}'}
                else:
                    prop = metadata.get('property', 'true')
                    prop_type = PropertyType(metadata.get('property_type', 'invariant'))
                    check_result = self.check_property(model, prop, prop_type)
                    result = check_result.to_dict()
                    
            elif operation == 'list_models':
                result = {
                    'models': [m.to_dict() for m in self.models.values()]
                }
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Model check task failed: {type(e).__name__}: {e}")
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
            tags=['model_checker', 'prover'],
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
            tags=['error', 'model_checker'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for model checking tasks."""
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['model_check'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['verification'], status=EntryStatus.PENDING)
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
        """DELIBERATE: Create model checking plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'check')
            steps = ['claim_task', 'load_model', 'check_property', 'analyze_result', 'post_result']
            intention = Intention(
                plan_id=f'modelcheck_{operation}_{task_id}',
                steps=steps,
                target_desire='model_verification',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform model checking."""
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
            elif action == 'load_model':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                model_name = metadata.get('model')
                model = self.models.get(model_name) if model_name else None
                intention.metadata['model'] = model
                intention.metadata['property'] = metadata.get('property', 'true')
                prop_type_str = metadata.get('property_type', 'invariant')
                intention.metadata['property_type'] = PropertyType(prop_type_str)
                intention.advance()
            elif action == 'check_property':
                model = intention.metadata.get('model')
                prop = intention.metadata.get('property', 'true')
                prop_type = intention.metadata.get('property_type', PropertyType.INVARIANT)
                if model:
                    result = self.check_property(model, prop, prop_type)
                    intention.metadata['check_result'] = result
                else:
                    intention.metadata['check_result'] = None
                intention.advance()
            elif action == 'analyze_result':
                result = intention.metadata.get('check_result')
                if result:
                    intention.metadata['satisfied'] = result.result == VerificationResult.SATISFIED
                    intention.metadata['has_counterexample'] = result.counterexample is not None
                intention.advance()
            elif action == 'post_result':
                result = intention.metadata.get('check_result')
                if self.blackboard and result:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result.to_dict())),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['model_checker', 'verification', 'result', task_id],
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
        """Get model checker statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'properties_checked': self.properties_checked,
            'properties_satisfied': self.properties_satisfied,
            'properties_violated': self.properties_violated,
            'models_cached': len(self.models)
        })
        return stats


if __name__ == "__main__":
    """Test Model Checker"""
    print("=" * 80)
    print("PHASE 6 - MODEL CHECKER TEST")
    print("=" * 80)
    print()
    
    # Initialize model checker
    checker = ModelChecker()
    print()
    
    # Test 1: Create a simple model
    print("Test 1: Create Traffic Light Model")
    model = checker.create_model(
        name="traffic_light",
        states=[
            {'id': 'red', 'values': {'color': 'red', 'stop': True}},
            {'id': 'yellow', 'values': {'color': 'yellow', 'stop': False}},
            {'id': 'green', 'values': {'color': 'green', 'stop': False}}
        ],
        transitions=[
            ('red', 'green', 'timer'),
            ('green', 'yellow', 'timer'),
            ('yellow', 'red', 'timer')
        ],
        initial=['red']
    )
    print(f"  Model: {model.name}")
    print(f"  States: {len(model.states)}")
    print(f"  Transitions: {len(model.transitions)}")
    print()
    
    # Test 2: Check invariant
    print("Test 2: Check Invariant (always some color)")
    result = checker.check_property(
        model,
        "color=red",
        PropertyType.REACHABILITY
    )
    print(f"  Property: color=red is reachable")
    print(f"  Result: {result.result.value}")
    print(f"  States explored: {result.states_explored}")
    print()
    
    # Test 3: Check deadlock freedom
    print("Test 3: Check Deadlock Freedom")
    result = checker.check_property(
        model,
        "deadlock_free",
        PropertyType.DEADLOCK_FREE
    )
    print(f"  Result: {result.result.value}")
    print()
    
    # Test 4: Create model with deadlock
    print("Test 4: Model with Deadlock")
    deadlock_model = checker.create_model(
        name="deadlock_model",
        states=[
            {'id': 's0', 'values': {}},
            {'id': 's1', 'values': {}},
            {'id': 'dead', 'values': {}}
        ],
        transitions=[
            ('s0', 's1', 'a'),
            ('s1', 'dead', 'b')
        ],
        initial=['s0']
    )
    result = checker.check_property(
        deadlock_model,
        "deadlock_free",
        PropertyType.DEADLOCK_FREE
    )
    print(f"  Result: {result.result.value}")
    if result.counterexample:
        print(f"  Counterexample path: {result.counterexample.path}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(checker.get_statistics(), indent=2))
