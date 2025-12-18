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
MODAL LOGIC SPECIALIST (Tier 3)
================================

Modal logic reasoning with necessity and possibility operators.

CAPABILITIES:
------------
- Kripke frame semantics
- Modal operators (Box/Diamond)
- K, T, S4, S5 logics
- Tableau method for validity checking
- Model checking in possible worlds

ALGORITHMS:
-----------
Native implementation - NO external dependencies

NO SYMPY - All mathematical operations use native implementations.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.modal_logic')


class ModalSystem(Enum):
    """Modal logic systems with their characteristic axioms."""
    K = "K"       # Basic modal logic (distribution axiom only)
    T = "T"       # K + reflexivity (Box p -> p)
    S4 = "S4"     # T + transitivity (Box p -> Box Box p)
    S5 = "S5"     # S4 + symmetry (Diamond p -> Box Diamond p)
    D = "D"       # K + seriality (Box p -> Diamond p)
    B = "B"       # T + symmetry (p -> Box Diamond p)


@dataclass
class ModalFormula:
    """Representation of a modal formula."""
    type: str  # 'atom', 'not', 'and', 'or', 'implies', 'box', 'diamond'
    value: Optional[str] = None  # For atoms
    left: Optional['ModalFormula'] = None
    right: Optional['ModalFormula'] = None
    subformula: Optional['ModalFormula'] = None  # For box/diamond/not

    def __str__(self) -> str:
        if self.type == 'atom':
            return self.value
        elif self.type == 'not':
            return f"¬{self.subformula}"
        elif self.type == 'and':
            return f"({self.left} ∧ {self.right})"
        elif self.type == 'or':
            return f"({self.left} ∨ {self.right})"
        elif self.type == 'implies':
            return f"({self.left} → {self.right})"
        elif self.type == 'box':
            return f"□{self.subformula}"
        elif self.type == 'diamond':
            return f"◇{self.subformula}"
        return "?"


@dataclass
class KripkeFrame:
    """A Kripke frame (W, R) with valuation."""
    worlds: Set[str]
    accessibility: Dict[str, Set[str]]  # world -> {accessible worlds}
    valuation: Dict[str, Set[str]]  # atom -> {worlds where true}


@dataclass
class ModalResult:
    """Result of modal logic operation."""
    valid: bool
    satisfiable: bool
    countermodel: Optional[KripkeFrame] = None
    proof_tree: Optional[List[str]] = None
    system: ModalSystem = ModalSystem.K


class ModalLogicSpecialist(BDIAgent):
    """
    Modal Logic Specialist - Reasoning about Necessity and Possibility

    DIRECTIVE:
    ---------
    Provide modal logic reasoning using Kripke semantics,
    supporting multiple modal systems (K, T, S4, S5).

    OPERATIONS:
    ----------
    - evaluate: Evaluate formula in Kripke model
    - check_validity: Check if formula is valid in modal system
    - check_satisfiability: Find satisfying model
    - build_tableau: Build modal tableau proof
    """

    def __init__(
        self,
        agent_id: str = "modal_logic_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        default_system: ModalSystem = ModalSystem.K,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "modal_logic_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self.default_system = default_system
        self._register_services()
        self._stats = {
            'evaluations': 0,
            'validity_checks': 0,
            'tableaux_built': 0,
        }

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="modal_logic",
                    description="Modal logic reasoning (K, T, S4, S5)"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== FORMULA CONSTRUCTORS ====================

    def atom(self, name: str) -> ModalFormula:
        """Create atomic proposition."""
        return ModalFormula(type='atom', value=name)

    def neg(self, formula: ModalFormula) -> ModalFormula:
        """Create negation."""
        return ModalFormula(type='not', subformula=formula)

    def conj(self, left: ModalFormula, right: ModalFormula) -> ModalFormula:
        """Create conjunction."""
        return ModalFormula(type='and', left=left, right=right)

    def disj(self, left: ModalFormula, right: ModalFormula) -> ModalFormula:
        """Create disjunction."""
        return ModalFormula(type='or', left=left, right=right)

    def implies(self, left: ModalFormula, right: ModalFormula) -> ModalFormula:
        """Create implication."""
        return ModalFormula(type='implies', left=left, right=right)

    def box(self, formula: ModalFormula) -> ModalFormula:
        """Create necessity (Box) operator."""
        return ModalFormula(type='box', subformula=formula)

    def diamond(self, formula: ModalFormula) -> ModalFormula:
        """Create possibility (Diamond) operator."""
        return ModalFormula(type='diamond', subformula=formula)

    # ==================== KRIPKE FRAME OPERATIONS ====================

    def create_frame(
        self,
        worlds: List[str],
        accessibility: Dict[str, List[str]],
        valuation: Dict[str, List[str]],
    ) -> KripkeFrame:
        """Create a Kripke frame."""
        return KripkeFrame(
            worlds=set(worlds),
            accessibility={w: set(acc) for w, acc in accessibility.items()},
            valuation={p: set(ws) for p, ws in valuation.items()}
        )

    def make_reflexive(self, frame: KripkeFrame) -> KripkeFrame:
        """Make accessibility relation reflexive."""
        new_acc = {w: frame.accessibility.get(w, set()) | {w}
                   for w in frame.worlds}
        return KripkeFrame(frame.worlds, new_acc, frame.valuation)

    def make_transitive(self, frame: KripkeFrame) -> KripkeFrame:
        """Make accessibility relation transitive (Floyd-Warshall style)."""
        new_acc = {w: set(frame.accessibility.get(w, set()))
                   for w in frame.worlds}

        changed = True
        while changed:
            changed = False
            for w1 in frame.worlds:
                for w2 in list(new_acc.get(w1, set())):
                    for w3 in list(new_acc.get(w2, set())):
                        if w3 not in new_acc.get(w1, set()):
                            new_acc.setdefault(w1, set()).add(w3)
                            changed = True

        return KripkeFrame(frame.worlds, new_acc, frame.valuation)

    def make_symmetric(self, frame: KripkeFrame) -> KripkeFrame:
        """Make accessibility relation symmetric."""
        new_acc = {w: set(frame.accessibility.get(w, set()))
                   for w in frame.worlds}

        for w1 in frame.worlds:
            for w2 in list(new_acc.get(w1, set())):
                new_acc.setdefault(w2, set()).add(w1)

        return KripkeFrame(frame.worlds, new_acc, frame.valuation)

    # ==================== EVALUATION ====================

    def evaluate(
        self,
        formula: ModalFormula,
        frame: KripkeFrame,
        world: str,
    ) -> bool:
        """
        Evaluate modal formula at a world in a Kripke frame.

        Args:
            formula: Modal formula to evaluate
            frame: Kripke frame (W, R, V)
            world: Current world

        Returns:
            True if formula is true at world
        """
        self._stats['evaluations'] += 1

        if formula.type == 'atom':
            return world in frame.valuation.get(formula.value, set())

        elif formula.type == 'not':
            return not self.evaluate(formula.subformula, frame, world)

        elif formula.type == 'and':
            return (self.evaluate(formula.left, frame, world) and
                    self.evaluate(formula.right, frame, world))

        elif formula.type == 'or':
            return (self.evaluate(formula.left, frame, world) or
                    self.evaluate(formula.right, frame, world))

        elif formula.type == 'implies':
            return (not self.evaluate(formula.left, frame, world) or
                    self.evaluate(formula.right, frame, world))

        elif formula.type == 'box':
            accessible = frame.accessibility.get(world, set())
            return all(self.evaluate(formula.subformula, frame, w)
                      for w in accessible)

        elif formula.type == 'diamond':
            accessible = frame.accessibility.get(world, set())
            return any(self.evaluate(formula.subformula, frame, w)
                      for w in accessible)

        return False

    def evaluate_all_worlds(
        self,
        formula: ModalFormula,
        frame: KripkeFrame,
    ) -> Dict[str, bool]:
        """Evaluate formula at all worlds."""
        return {w: self.evaluate(formula, frame, w) for w in frame.worlds}

    # ==================== VALIDITY CHECKING ====================

    def check_validity(
        self,
        formula: ModalFormula,
        system: Optional[ModalSystem] = None,
        max_worlds: int = 8,
    ) -> ModalResult:
        """
        Check if formula is valid in given modal system.

        Uses tableau method with appropriate closure rules for the system.

        Args:
            formula: Modal formula to check
            system: Modal system (K, T, S4, S5)
            max_worlds: Maximum worlds to consider

        Returns:
            ModalResult with validity and potential countermodel
        """
        self._stats['validity_checks'] += 1
        system = system or self.default_system

        # Try to build countermodel (model where negation is satisfiable)
        neg_formula = self.neg(formula)

        # Use tableau method
        result = self._tableau_satisfiability(neg_formula, system, max_worlds)

        if result['satisfiable']:
            return ModalResult(
                valid=False,
                satisfiable=True,
                countermodel=result.get('model'),
                system=system
            )
        else:
            return ModalResult(
                valid=True,
                satisfiable=False,
                proof_tree=result.get('proof'),
                system=system
            )

    def _tableau_satisfiability(
        self,
        formula: ModalFormula,
        system: ModalSystem,
        max_worlds: int,
    ) -> Dict[str, Any]:
        """
        Tableau method for modal satisfiability.

        Builds a tableau (proof tree) trying to find satisfying assignment.
        """
        self._stats['tableaux_built'] += 1

        # Initialize with single world
        worlds = {'w0'}
        accessibility: Dict[str, Set[str]] = {'w0': set()}
        formulas_at_world: Dict[str, Set[Tuple[ModalFormula, bool]]] = {
            'w0': {(formula, True)}  # formula must be true at w0
        }

        # Apply frame conditions based on system
        if system in [ModalSystem.T, ModalSystem.S4, ModalSystem.S5, ModalSystem.B]:
            accessibility['w0'].add('w0')  # Reflexivity

        world_counter = [1]
        proof_steps = []

        def add_world() -> Optional[str]:
            """Perform add world operation.

            Args:
            No arguments

            Returns:
            Result of the operation

            Example:
            >>> result = obj.add_world(...)
            """
            if len(worlds) >= max_worlds:
                return None
            w = f"w{world_counter[0]}"
            world_counter[0] += 1
            worlds.add(w)
            accessibility[w] = set()

            # Apply reflexivity if needed
            if system in [ModalSystem.T, ModalSystem.S4, ModalSystem.S5, ModalSystem.B]:
                accessibility[w].add(w)

            formulas_at_world[w] = set()
            return w

        def propagate(max_iterations: int = 100) -> bool:
            """Propagate constraints. Returns False if contradiction found."""
            for _ in range(max_iterations):
                changed = False

                for world in list(worlds):
                    formulas = list(formulas_at_world.get(world, set()))

                    for f, sign in formulas:
                        result = self._apply_tableau_rule(
                            f, sign, world, worlds, accessibility,
                            formulas_at_world, add_world, system
                        )

                        if result == 'contradiction':
                            return False
                        elif result == 'changed':
                            changed = True

                if not changed:
                    break

            return True

        # Run tableau
        if propagate():
            # Build model from tableau
            valuation: Dict[str, Set[str]] = {}
            for w in worlds:
                for f, sign in formulas_at_world.get(w, set()):
                    if f.type == 'atom' and sign:
                        valuation.setdefault(f.value, set()).add(w)

            model = KripkeFrame(worlds, accessibility, valuation)
            return {'satisfiable': True, 'model': model}
        else:
            return {'satisfiable': False, 'proof': proof_steps}

    def _apply_tableau_rule(
        self,
        formula: ModalFormula,
        sign: bool,
        world: str,
        worlds: Set[str],
        accessibility: Dict[str, Set[str]],
        formulas_at_world: Dict[str, Set[Tuple[ModalFormula, bool]]],
        add_world,
        system: ModalSystem,
    ) -> str:
        """Apply single tableau rule. Returns 'contradiction', 'changed', or 'none'."""

        def add_formula(w: str, f: ModalFormula, s: bool) -> str:
            """Perform add formula operation.

            Args:
            w: Description needed
            f: Description needed
            s: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.add_formula(...)
            """
            key = (f.type, str(f), s)
            existing = formulas_at_world.get(w, set())

            # Check for contradiction
            for ef, es in existing:
                if str(ef) == str(f) and es != s:
                    return 'contradiction'

            if (f, s) not in existing:
                formulas_at_world.setdefault(w, set()).add((f, s))
                return 'changed'
            return 'none'

        if formula.type == 'atom':
            return 'none'

        elif formula.type == 'not':
            return add_formula(world, formula.subformula, not sign)

        elif formula.type == 'and':
            if sign:  # A ∧ B true
                r1 = add_formula(world, formula.left, True)
                r2 = add_formula(world, formula.right, True)
                if 'contradiction' in [r1, r2]:
                    return 'contradiction'
                return 'changed' if 'changed' in [r1, r2] else 'none'
            else:  # A ∧ B false - branching (take one branch)
                return add_formula(world, formula.left, False)

        elif formula.type == 'or':
            if sign:  # A ∨ B true - branching (take one branch)
                return add_formula(world, formula.left, True)
            else:  # A ∨ B false
                r1 = add_formula(world, formula.left, False)
                r2 = add_formula(world, formula.right, False)
                if 'contradiction' in [r1, r2]:
                    return 'contradiction'
                return 'changed' if 'changed' in [r1, r2] else 'none'

        elif formula.type == 'implies':
            if sign:  # A → B true
                return add_formula(world, formula.right, True)
            else:  # A → B false
                r1 = add_formula(world, formula.left, True)
                r2 = add_formula(world, formula.right, False)
                if 'contradiction' in [r1, r2]:
                    return 'contradiction'
                return 'changed' if 'changed' in [r1, r2] else 'none'

        elif formula.type == 'box':
            if sign:  # □φ true: φ must be true in all accessible worlds
                changed = False
                for w in accessibility.get(world, set()):
                    r = add_formula(w, formula.subformula, True)
                    if r == 'contradiction':
                        return 'contradiction'
                    if r == 'changed':
                        changed = True
                return 'changed' if changed else 'none'
            else:  # □φ false: need witness world where φ is false
                new_world = add_world()
                if new_world:
                    accessibility.setdefault(world, set()).add(new_world)

                    # Apply transitivity for S4/S5
                    if system in [ModalSystem.S4, ModalSystem.S5]:
                        for w in accessibility.get(world, set()):
                            accessibility.setdefault(new_world, set()).update(
                                accessibility.get(w, set())
                            )

                    # Apply symmetry for S5/B
                    if system in [ModalSystem.S5, ModalSystem.B]:
                        accessibility.setdefault(new_world, set()).add(world)

                    return add_formula(new_world, formula.subformula, False)
                return 'none'

        elif formula.type == 'diamond':
            if sign:  # ◇φ true: need witness world where φ is true
                new_world = add_world()
                if new_world:
                    accessibility.setdefault(world, set()).add(new_world)

                    if system in [ModalSystem.S4, ModalSystem.S5]:
                        for w in accessibility.get(world, set()):
                            accessibility.setdefault(new_world, set()).update(
                                accessibility.get(w, set())
                            )

                    if system in [ModalSystem.S5, ModalSystem.B]:
                        accessibility.setdefault(new_world, set()).add(world)

                    return add_formula(new_world, formula.subformula, True)
                return 'none'
            else:  # ◇φ false: φ must be false in all accessible worlds
                changed = False
                for w in accessibility.get(world, set()):
                    r = add_formula(w, formula.subformula, False)
                    if r == 'contradiction':
                        return 'contradiction'
                    if r == 'changed':
                        changed = True
                return 'changed' if changed else 'none'

        return 'none'

    # ==================== COMMON MODAL FORMULAS ====================

    def axiom_k(self, p: ModalFormula, q: ModalFormula) -> ModalFormula:
        """Distribution axiom: □(p → q) → (□p → □q)"""
        return self.implies(
            self.box(self.implies(p, q)),
            self.implies(self.box(p), self.box(q))
        )

    def axiom_t(self, p: ModalFormula) -> ModalFormula:
        """Reflexivity axiom: □p → p"""
        return self.implies(self.box(p), p)

    def axiom_4(self, p: ModalFormula) -> ModalFormula:
        """Transitivity axiom: □p → □□p"""
        return self.implies(self.box(p), self.box(self.box(p)))

    def axiom_5(self, p: ModalFormula) -> ModalFormula:
        """Euclidean axiom: ◇p → □◇p"""
        return self.implies(self.diamond(p), self.box(self.diamond(p)))

    def axiom_b(self, p: ModalFormula) -> ModalFormula:
        """Symmetry axiom: p → □◇p"""
        return self.implies(p, self.box(self.diamond(p)))

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'evaluate':
            result = self.evaluate(**params)
            return {'status': 'success', 'result': result}
        elif action == 'check_validity':
            result = self.check_validity(**params)
            return {'status': 'success', 'result': result}
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        """Return computation statistics."""
        return dict(self._stats)

    def update_beliefs(self):
        """Update beliefs from environment."""
        pass

    def deliberate(self) -> List:
        """Generate intentions from beliefs."""
        return []

    def execute_step(self, intention):
        """Execute next step in plan."""
        pass


__all__ = [
    'ModalLogicSpecialist',
    'ModalFormula',
    'ModalResult',
    'KripkeFrame',
    'ModalSystem',
]
