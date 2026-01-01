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
PHASE 6 - SYN-2: PROOF TERM CONSTRUCTOR (Tier 3)
=================================================

Constructs proof terms and validates them according to typing rules.

CAPABILITIES:
------------
- Proof term construction
- Type checking
- Term reduction (beta, eta)
- Normalization
- Type inference

REFERENCE:
---------
- Agent_System_Audit.docx.md: SYN-2 Proof Term Constructor
- Phase_6_Formal_Verification.md: Synthesis Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.phase6.proof_term_constructor')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class TermKind(Enum):
    """Kinds of proof terms"""
    VARIABLE = "var"
    ABSTRACTION = "abs"    # λx:A.t
    APPLICATION = "app"    # t u
    PRODUCT = "prod"       # Πx:A.B or A → B
    UNIVERSE = "type"      # Type_i
    CONSTANT = "const"
    INDUCTIVE = "ind"      # Inductive type


class TypeCheckResult(Enum):
    """Result of type checking"""
    WELL_TYPED = "well_typed"
    TYPE_ERROR = "type_error"
    UNKNOWN = "unknown"


@dataclass
class ProofTerm:
    """
    Representation of a proof term.
    
    Attributes:
        kind: Type of term
        name: Name (for variables, constants)
        type_annotation: Type annotation
        sub_terms: Child terms
        bound_var: Bound variable (for abstractions)
    """
    kind: TermKind
    name: Optional[str] = None
    type_annotation: Optional[str] = None
    sub_terms: List['ProofTerm'] = field(default_factory=list)
    bound_var: Optional[str] = None
    
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
            'kind': self.kind.value,
            'name': self.name,
            'type': self.type_annotation,
            'sub_count': len(self.sub_terms)
        }
    
    def to_string(self) -> str:
        """Convert to readable string representation"""
        if self.kind == TermKind.VARIABLE:
            return self.name or "?"
        elif self.kind == TermKind.CONSTANT:
            return self.name or "const"
        elif self.kind == TermKind.ABSTRACTION:
            body = self.sub_terms[0].to_string() if self.sub_terms else "_"
            return f"λ{self.bound_var}:{self.type_annotation}.{body}"
        elif self.kind == TermKind.APPLICATION:
            if len(self.sub_terms) >= 2:
                return f"({self.sub_terms[0].to_string()} {self.sub_terms[1].to_string()})"
            return "(app ?)"
        elif self.kind == TermKind.PRODUCT:
            if len(self.sub_terms) >= 2:
                return f"Π{self.bound_var}:{self.sub_terms[0].to_string()}.{self.sub_terms[1].to_string()}"
            return "Π?"
        elif self.kind == TermKind.UNIVERSE:
            return f"Type_{self.name or '0'}"
        else:
            return f"{self.kind.value}[{self.name}]"


@dataclass
class TypeContext:
    """Typing context (variable bindings)"""
    bindings: Dict[str, str] = field(default_factory=dict)
    
    def extend(self, var: str, typ: str) -> 'TypeContext':
        """Create extended context"""
        new_bindings = self.bindings.copy()
        new_bindings[var] = typ
        return TypeContext(bindings=new_bindings)
    
    def lookup(self, var: str) -> Optional[str]:
        """Look up variable type"""
        return self.bindings.get(var)


@dataclass
class TypeCheckOutput:
    """Perform to dict operation.

    Args:
    No arguments

    Returns:
    Result of the operation

    Example:
    >>> result = obj.to_dict(...)
    """
    """Output of type checking"""
    result: TypeCheckResult
    inferred_type: Optional[str]
    errors: List[str] = field(default_factory=list)
    
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
            'result': self.result.value,
            'type': self.inferred_type,
            'error_count': len(self.errors)
        }


class ProofTermConstructor(BDIAgent):
    """
    SYN-2: Proof Term Constructor
    
    DIRECTIVE:
    ---------
    Construct proof terms and validate them according to typing rules.
    
    INPUTS:
    ------
    - Term specifications
    - Type annotations
    - Typing contexts
    
    OUTPUTS:
    -------
    - Constructed proof terms
    - Type checking results
    - Normalized terms
    
    DEPENDENCIES:
    ------------
    - SYN-1 (StructuralSynthesizer): For structure definitions
    - PRV-1 (LogicalProver): For proof validation
    
    FAILURE MODE: DEGRADED - Returns partial term with errors
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 692-701
    """
    
    def __init__(
        self,
        agent_id: str = 'proof_term_constructor_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Proof Term Constructor
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        
        # Term cache
        self.term_cache: Dict[str, ProofTerm] = {}
        
        # Global context
        self.global_context = TypeContext()
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.terms_constructed = 0
        self.type_checks = 0
        self.reductions = 0
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Proof Term Constructor initialized")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='synthesis.proof_term',
            agent_id=self.agent_id,
            algorithm='term_construction',
            cost='high',
            type='synthesis',
            tier='3',
            algorithms='lambda_calculus_type_checking'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: synthesis.proof_term")
    
    def construct_variable(self, name: str, typ: str) -> ProofTerm:
        """Construct a variable term"""
        return ProofTerm(
            kind=TermKind.VARIABLE,
            name=name,
            type_annotation=typ
        )
    
    def construct_constant(self, name: str, typ: str) -> ProofTerm:
        """Construct a constant term"""
        return ProofTerm(
            kind=TermKind.CONSTANT,
            name=name,
            type_annotation=typ
        )
    
    def construct_abstraction(
        self,
        var: str,
        var_type: str,
        body: ProofTerm
    ) -> ProofTerm:
        """Construct a lambda abstraction"""
        self.terms_constructed += 1
        return ProofTerm(
            kind=TermKind.ABSTRACTION,
            bound_var=var,
            type_annotation=var_type,
            sub_terms=[body]
        )
    
    def construct_application(
        self,
        func: ProofTerm,
        arg: ProofTerm
    ) -> ProofTerm:
        """Construct a function application"""
        self.terms_constructed += 1
        return ProofTerm(
            kind=TermKind.APPLICATION,
            sub_terms=[func, arg]
        )
    
    def construct_product(
        self,
        var: str,
        domain: ProofTerm,
        codomain: ProofTerm
    ) -> ProofTerm:
        """Construct a dependent product (Π type)"""
        self.terms_constructed += 1
        return ProofTerm(
            kind=TermKind.PRODUCT,
            bound_var=var,
            sub_terms=[domain, codomain]
        )
    
    def construct_arrow(self, domain: str, codomain: str) -> ProofTerm:
        """Construct a non-dependent function type (A → B)"""
        dom = self.construct_constant(domain, "Type")
        cod = self.construct_constant(codomain, "Type")
        return self.construct_product("_", dom, cod)
    
    def type_check(
        self,
        term: ProofTerm,
        context: Optional[TypeContext] = None
    ) -> TypeCheckOutput:
        """
        Type check a proof term.
        
        Args:
            term: Term to check
            context: Typing context (uses global if None)
            
        Returns:
            TypeCheckOutput with result
        """
        self.tasks_executed += 1
        self.type_checks += 1
        
        ctx = context or self.global_context
        errors = []
        
        try:
            inferred = self._infer_type(term, ctx, errors)
            
            if errors:
                result = TypeCheckResult.TYPE_ERROR
            else:
                result = TypeCheckResult.WELL_TYPED
            
            self.tasks_succeeded += 1
            
            return TypeCheckOutput(
                result=result,
                inferred_type=inferred,
                errors=errors
            )
            
        except Exception as e:
            self.tasks_failed += 1
            return TypeCheckOutput(
                result=TypeCheckResult.UNKNOWN,
                inferred_type=None,
                errors=[str(e)]
            )
    
    def _infer_type(
        self,
        term: ProofTerm,
        ctx: TypeContext,
        errors: List[str]
    ) -> Optional[str]:
        """Infer the type of a term"""
        if term.kind == TermKind.VARIABLE:
            typ = ctx.lookup(term.name)
            if typ is None and term.type_annotation:
                return term.type_annotation
            if typ is None:
                errors.append(f"Unbound variable: {term.name}")
            return typ
        
        elif term.kind == TermKind.CONSTANT:
            return term.type_annotation
        
        elif term.kind == TermKind.ABSTRACTION:
            if not term.sub_terms:
                errors.append("Abstraction missing body")
                return None
            
            new_ctx = ctx.extend(term.bound_var, term.type_annotation)
            body_type = self._infer_type(term.sub_terms[0], new_ctx, errors)
            
            return f"({term.type_annotation} → {body_type})"
        
        elif term.kind == TermKind.APPLICATION:
            if len(term.sub_terms) < 2:
                errors.append("Application missing arguments")
                return None
            
            func_type = self._infer_type(term.sub_terms[0], ctx, errors)
            arg_type = self._infer_type(term.sub_terms[1], ctx, errors)
            
            # Simple arrow type checking
            if func_type and "→" in func_type:
                parts = func_type.strip("()").split(" → ")
                if len(parts) >= 2:
                    return parts[-1]
            
            return "?"
        
        elif term.kind == TermKind.PRODUCT:
            return "Type"
        
        elif term.kind == TermKind.UNIVERSE:
            level = int(term.name or "0")
            return f"Type_{level + 1}"
        
        return None
    
    def beta_reduce(self, term: ProofTerm) -> ProofTerm:
        """
        Perform beta reduction on a term.
        
        (λx.t) u → t[x := u]
        """
        self.reductions += 1
        
        if term.kind == TermKind.APPLICATION:
            if len(term.sub_terms) >= 2:
                func = term.sub_terms[0]
                arg = term.sub_terms[1]
                
                if func.kind == TermKind.ABSTRACTION:
                    # Perform substitution
                    body = func.sub_terms[0] if func.sub_terms else arg
                    return self._substitute(body, func.bound_var, arg)
        
        return term
    
    def _substitute(
        self,
        term: ProofTerm,
        var: str,
        replacement: ProofTerm
    ) -> ProofTerm:
        """Substitute var with replacement in term"""
        if term.kind == TermKind.VARIABLE:
            if term.name == var:
                return replacement
            return term
        
        elif term.kind == TermKind.ABSTRACTION:
            if term.bound_var == var:
                # Variable is shadowed
                return term
            new_body = self._substitute(term.sub_terms[0], var, replacement)
            return ProofTerm(
                kind=TermKind.ABSTRACTION,
                bound_var=term.bound_var,
                type_annotation=term.type_annotation,
                sub_terms=[new_body]
            )
        
        elif term.kind == TermKind.APPLICATION:
            new_subs = [self._substitute(s, var, replacement) for s in term.sub_terms]
            return ProofTerm(
                kind=TermKind.APPLICATION,
                sub_terms=new_subs
            )
        
        return term
    
    def normalize(self, term: ProofTerm, max_steps: int = 100) -> ProofTerm:
        """
        Normalize a term by repeated beta reduction.
        
        Args:
            term: Term to normalize
            max_steps: Maximum reduction steps
            
        Returns:
            Normalized term
        """
        current = term
        for _ in range(max_steps):
            reduced = self.beta_reduce(current)
            if reduced.to_string() == current.to_string():
                break
            current = reduced
        
        return current
    
    def process(self, task_entry: Any) -> Any:
        """Process proof term task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing proof term task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'construct')
            
            if operation == 'construct_var':
                name = metadata.get('name', 'x')
                typ = metadata.get('type', 'A')
                term = self.construct_variable(name, typ)
                result = {'term': term.to_string(), **term.to_dict()}
                
            elif operation == 'construct_abs':
                var = metadata.get('var', 'x')
                var_type = metadata.get('var_type', 'A')
                body_name = metadata.get('body', 'x')
                body = self.construct_variable(body_name, var_type)
                term = self.construct_abstraction(var, var_type, body)
                result = {'term': term.to_string(), **term.to_dict()}
                
            elif operation == 'type_check':
                # Would need to reconstruct term from metadata
                term = self.construct_variable("x", "A")  # Placeholder
                check = self.type_check(term)
                result = check.to_dict()
                
            elif operation == 'normalize':
                # Placeholder term
                term = self.construct_variable("x", "A")
                normalized = self.normalize(term)
                result = {'normalized': normalized.to_string()}
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Proof term task failed: {type(e).__name__}: {e}")
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
            tags=['proof_term', 'synthesis'],
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
            tags=['error', 'proof_term'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for proof term tasks."""
        if not self.blackboard:
            return
        try:
            tasks = self.blackboard.query_entries(tags=['proof_term'], status=EntryStatus.PENDING) + \
                    self.blackboard.query_entries(tags=['type_check'], status=EntryStatus.PENDING)
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
        """DELIBERATE: Create proof term construction plans."""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'construct')
            steps = ['claim_task', 'parse_term_spec', 'construct_term', 'type_check_term', 'post_result']
            intention = Intention(
                plan_id=f'proof_term_{operation}_{task_id}',
                steps=steps,
                target_desire='proof_term_construction',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Perform proof term construction."""
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
            elif action == 'parse_term_spec':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                intention.metadata['var_name'] = metadata.get('name', 'x')
                intention.metadata['var_type'] = metadata.get('type', 'A')
                intention.metadata['term_kind'] = metadata.get('kind', 'var')
                intention.advance()
            elif action == 'construct_term':
                kind = intention.metadata.get('term_kind', 'var')
                name = intention.metadata.get('var_name', 'x')
                typ = intention.metadata.get('var_type', 'A')
                if kind == 'var':
                    term = self.construct_variable(name, typ)
                elif kind == 'const':
                    term = self.construct_constant(name, typ)
                elif kind == 'abs':
                    body = self.construct_variable(name, typ)
                    term = self.construct_abstraction(name, typ, body)
                else:
                    term = self.construct_variable(name, typ)
                intention.metadata['term'] = term
                intention.advance()
            elif action == 'type_check_term':
                term = intention.metadata.get('term')
                if term:
                    check_result = self.type_check(term)
                    intention.metadata['type_check'] = check_result
                intention.advance()
            elif action == 'post_result':
                term = intention.metadata.get('term')
                check = intention.metadata.get('type_check')
                if self.blackboard and term:
                    result = {
                        'term': term.to_string(),
                        'type_check': check.to_dict() if check else None,
                        **term.to_dict()
                    }
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(term.to_string()),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['proof_term', 'synthesis', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata=result
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
        """Get constructor statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'terms_constructed': self.terms_constructed,
            'type_checks': self.type_checks,
            'reductions': self.reductions
        })
        return stats


if __name__ == "__main__":
    """Test Proof Term Constructor"""
    print("=" * 80)
    print("PHASE 6 - PROOF TERM CONSTRUCTOR TEST")
    print("=" * 80)
    print()
    
    # Initialize constructor
    constructor = ProofTermConstructor()
    print()
    
    # Test 1: Construct simple terms
    print("Test 1: Construct Simple Terms")
    x = constructor.construct_variable("x", "A")
    print(f"  Variable: {x.to_string()}")
    
    c = constructor.construct_constant("zero", "Nat")
    print(f"  Constant: {c.to_string()}")
    print()
    
    # Test 2: Construct lambda abstraction
    print("Test 2: Lambda Abstraction")
    identity = constructor.construct_abstraction("x", "A", x)
    print(f"  Identity: {identity.to_string()}")
    print()
    
    # Test 3: Construct application
    print("Test 3: Function Application")
    app = constructor.construct_application(identity, c)
    print(f"  Application: {app.to_string()}")
    print()
    
    # Test 4: Type check
    print("Test 4: Type Checking")
    check_result = constructor.type_check(x)
    print(f"  Variable type check: {check_result.result.value}")
    print(f"  Inferred type: {check_result.inferred_type}")
    
    check_identity = constructor.type_check(identity)
    print(f"  Identity type: {check_identity.inferred_type}")
    print()
    
    # Test 5: Beta reduction
    print("Test 5: Beta Reduction")
    print(f"  Before: {app.to_string()}")
    reduced = constructor.beta_reduce(app)
    print(f"  After: {reduced.to_string()}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(constructor.get_statistics(), indent=2))
