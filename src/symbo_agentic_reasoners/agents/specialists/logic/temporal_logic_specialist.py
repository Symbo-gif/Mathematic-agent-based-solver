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
TEMPORAL LOGIC SPECIALIST (Tier 3)
===================================

Linear and branching temporal logic reasoning.

CAPABILITIES:
------------
- Linear Temporal Logic (LTL)
- Computation Tree Logic (CTL)
- Temporal operators (X, F, G, U, R)
- Path quantifiers (A, E)
- Model checking
- Buchi automata

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

logger = logging.getLogger('symbo_agentic_reasoners.specialists.temporal_logic')


class TemporalLogicType(Enum):
    """Type of temporal logic."""
    LTL = "LTL"   # Linear Temporal Logic
    CTL = "CTL"   # Computation Tree Logic


@dataclass
class TemporalFormula:
    """Representation of a temporal formula."""
    type: str  # 'atom', 'not', 'and', 'or', 'implies', 'X', 'F', 'G', 'U', 'R', 'A', 'E'
    value: Optional[str] = None  # For atoms
    left: Optional['TemporalFormula'] = None
    right: Optional['TemporalFormula'] = None
    subformula: Optional['TemporalFormula'] = None

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
        elif self.type == 'X':
            return f"X{self.subformula}"
        elif self.type == 'F':
            return f"F{self.subformula}"
        elif self.type == 'G':
            return f"G{self.subformula}"
        elif self.type == 'U':
            return f"({self.left} U {self.right})"
        elif self.type == 'R':
            return f"({self.left} R {self.right})"
        elif self.type == 'A':
            return f"A{self.subformula}"
        elif self.type == 'E':
            return f"E{self.subformula}"
        return "?"


@dataclass
class KripkeStructure:
    """Kripke structure for model checking."""
    states: Set[str]
    initial_states: Set[str]
    transitions: Dict[str, Set[str]]  # state -> successor states
    labeling: Dict[str, Set[str]]  # state -> propositions true at state


@dataclass
class TemporalResult:
    """Result of temporal logic operation."""
    satisfied: bool
    satisfying_states: Optional[Set[str]] = None
    witness_path: Optional[List[str]] = None
    counterexample: Optional[List[str]] = None
    logic_type: TemporalLogicType = TemporalLogicType.LTL


class TemporalLogicSpecialist(BDIAgent):
    """
    Temporal Logic Specialist - Reasoning about Time

    DIRECTIVE:
    ---------
    Provide temporal logic reasoning and model checking for
    LTL and CTL formulas.

    OPERATIONS:
    ----------
    - check_ltl: Check LTL formula on Kripke structure
    - check_ctl: Check CTL formula on Kripke structure
    - evaluate_path: Evaluate LTL formula on execution path
    - find_satisfying_states: Find all states satisfying CTL formula
    """

    def __init__(
        self,
        agent_id: str = "temporal_logic_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "temporal_logic_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {
            'ltl_checks': 0,
            'ctl_checks': 0,
            'model_checks': 0,
        }

    def _register_services(self):
        """Register specialist services with Directory Facilitator."""
        if self.df:
            services = [
                create_service_registration(
                    agent_id=self.agent_id,
                    service_type="temporal_logic",
                    description="Temporal logic reasoning (LTL, CTL)"
                ),
            ]
            for service in services:
                self.df.register_service(service)

    # ==================== FORMULA CONSTRUCTORS ====================

    def atom(self, name: str) -> TemporalFormula:
        """Create atomic proposition."""
        return TemporalFormula(type='atom', value=name)

    def neg(self, formula: TemporalFormula) -> TemporalFormula:
        """Create negation."""
        return TemporalFormula(type='not', subformula=formula)

    def conj(self, left: TemporalFormula, right: TemporalFormula) -> TemporalFormula:
        """Create conjunction."""
        return TemporalFormula(type='and', left=left, right=right)

    def disj(self, left: TemporalFormula, right: TemporalFormula) -> TemporalFormula:
        """Create disjunction."""
        return TemporalFormula(type='or', left=left, right=right)

    def implies(self, left: TemporalFormula, right: TemporalFormula) -> TemporalFormula:
        """Create implication."""
        return TemporalFormula(type='implies', left=left, right=right)

    # LTL Operators
    def next(self, formula: TemporalFormula) -> TemporalFormula:
        """Next operator (X): true at next state."""
        return TemporalFormula(type='X', subformula=formula)

    def eventually(self, formula: TemporalFormula) -> TemporalFormula:
        """Eventually operator (F): true at some future state."""
        return TemporalFormula(type='F', subformula=formula)

    def always(self, formula: TemporalFormula) -> TemporalFormula:
        """Always operator (G): true at all future states."""
        return TemporalFormula(type='G', subformula=formula)

    def until(self, left: TemporalFormula, right: TemporalFormula) -> TemporalFormula:
        """Until operator (U): left holds until right becomes true."""
        return TemporalFormula(type='U', left=left, right=right)

    def release(self, left: TemporalFormula, right: TemporalFormula) -> TemporalFormula:
        """Release operator (R): dual of until."""
        return TemporalFormula(type='R', left=left, right=right)

    # CTL Path Quantifiers
    def forall(self, formula: TemporalFormula) -> TemporalFormula:
        """Universal path quantifier (A): all paths."""
        return TemporalFormula(type='A', subformula=formula)

    def exists(self, formula: TemporalFormula) -> TemporalFormula:
        """Existential path quantifier (E): some path."""
        return TemporalFormula(type='E', subformula=formula)

    # ==================== KRIPKE STRUCTURE ====================

    def create_structure(
        self,
        states: List[str],
        initial: List[str],
        transitions: Dict[str, List[str]],
        labeling: Dict[str, List[str]],
    ) -> KripkeStructure:
        """Create a Kripke structure."""
        return KripkeStructure(
            states=set(states),
            initial_states=set(initial),
            transitions={s: set(t) for s, t in transitions.items()},
            labeling={s: set(props) for s, props in labeling.items()}
        )

    # ==================== LTL MODEL CHECKING ====================

    def check_ltl(
        self,
        formula: TemporalFormula,
        structure: KripkeStructure,
        max_depth: int = 100,
    ) -> TemporalResult:
        """
        Check if LTL formula is satisfied by Kripke structure.

        Uses bounded model checking approach.

        Args:
            formula: LTL formula
            structure: Kripke structure
            max_depth: Maximum path length to check

        Returns:
            TemporalResult with satisfaction and witness/counterexample
        """
        self._stats['ltl_checks'] += 1
        self._stats['model_checks'] += 1

        # Check from all initial states
        for init_state in structure.initial_states:
            # Generate paths and check formula
            paths = self._generate_paths(structure, init_state, max_depth)

            for path in paths:
                if not self._evaluate_ltl_path(formula, structure, path, 0):
                    # Found counterexample
                    return TemporalResult(
                        satisfied=False,
                        counterexample=path,
                        logic_type=TemporalLogicType.LTL
                    )

        # No counterexample found within bound
        return TemporalResult(
            satisfied=True,
            logic_type=TemporalLogicType.LTL
        )

    def _generate_paths(
        self,
        structure: KripkeStructure,
        start: str,
        max_length: int,
    ) -> List[List[str]]:
        """Generate paths from start state (bounded)."""
        paths = []

        def dfs(current: str, path: List[str], depth: int):
            """Perform dfs operation.

            Args:
            current: Description needed
            path: Description needed
            depth: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.dfs(...)
            """
            if depth >= max_length:
                paths.append(path.copy())
                return

            successors = structure.transitions.get(current, set())
            if not successors:
                paths.append(path.copy())
                return

            for succ in successors:
                # Detect loop
                if succ in path:
                    # Complete the loop and stop
                    paths.append(path + [succ])
                else:
                    path.append(succ)
                    dfs(succ, path, depth + 1)
                    path.pop()

        dfs(start, [start], 0)
        return paths

    def _evaluate_ltl_path(
        self,
        formula: TemporalFormula,
        structure: KripkeStructure,
        path: List[str],
        index: int,
    ) -> bool:
        """Evaluate LTL formula on path at position index."""
        if index >= len(path):
            # Assume path loops at last state
            index = len(path) - 1

        current_state = path[index]

        if formula.type == 'atom':
            return formula.value in structure.labeling.get(current_state, set())

        elif formula.type == 'not':
            return not self._evaluate_ltl_path(formula.subformula, structure, path, index)

        elif formula.type == 'and':
            return (self._evaluate_ltl_path(formula.left, structure, path, index) and
                    self._evaluate_ltl_path(formula.right, structure, path, index))

        elif formula.type == 'or':
            return (self._evaluate_ltl_path(formula.left, structure, path, index) or
                    self._evaluate_ltl_path(formula.right, structure, path, index))

        elif formula.type == 'implies':
            return (not self._evaluate_ltl_path(formula.left, structure, path, index) or
                    self._evaluate_ltl_path(formula.right, structure, path, index))

        elif formula.type == 'X':
            return self._evaluate_ltl_path(formula.subformula, structure, path, index + 1)

        elif formula.type == 'F':
            # Eventually: true at some future position
            for i in range(index, len(path)):
                if self._evaluate_ltl_path(formula.subformula, structure, path, i):
                    return True
            return False

        elif formula.type == 'G':
            # Always: true at all future positions
            for i in range(index, len(path)):
                if not self._evaluate_ltl_path(formula.subformula, structure, path, i):
                    return False
            return True

        elif formula.type == 'U':
            # Until: left holds until right becomes true
            for i in range(index, len(path)):
                if self._evaluate_ltl_path(formula.right, structure, path, i):
                    return True
                if not self._evaluate_ltl_path(formula.left, structure, path, i):
                    return False
            return False

        elif formula.type == 'R':
            # Release: right holds until and including when left becomes true
            for i in range(index, len(path)):
                if self._evaluate_ltl_path(formula.left, structure, path, i):
                    return self._evaluate_ltl_path(formula.right, structure, path, i)
                if not self._evaluate_ltl_path(formula.right, structure, path, i):
                    return False
            return True

        return False

    # ==================== CTL MODEL CHECKING ====================

    def check_ctl(
        self,
        formula: TemporalFormula,
        structure: KripkeStructure,
    ) -> TemporalResult:
        """
        Check CTL formula using labeling algorithm.

        Args:
            formula: CTL formula
            structure: Kripke structure

        Returns:
            TemporalResult with satisfying states
        """
        self._stats['ctl_checks'] += 1
        self._stats['model_checks'] += 1

        # Compute set of states satisfying formula
        sat_states = self._ctl_labeling(formula, structure)

        # Check if all initial states satisfy formula
        satisfied = structure.initial_states <= sat_states

        return TemporalResult(
            satisfied=satisfied,
            satisfying_states=sat_states,
            logic_type=TemporalLogicType.CTL
        )

    def _ctl_labeling(
        self,
        formula: TemporalFormula,
        structure: KripkeStructure,
    ) -> Set[str]:
        """CTL labeling algorithm - returns states satisfying formula."""

        if formula.type == 'atom':
            return {s for s in structure.states
                    if formula.value in structure.labeling.get(s, set())}

        elif formula.type == 'not':
            return structure.states - self._ctl_labeling(formula.subformula, structure)

        elif formula.type == 'and':
            return (self._ctl_labeling(formula.left, structure) &
                    self._ctl_labeling(formula.right, structure))

        elif formula.type == 'or':
            return (self._ctl_labeling(formula.left, structure) |
                    self._ctl_labeling(formula.right, structure))

        elif formula.type == 'implies':
            not_left = structure.states - self._ctl_labeling(formula.left, structure)
            right = self._ctl_labeling(formula.right, structure)
            return not_left | right

        elif formula.type == 'A':
            # A(path formula) - must handle inner formula
            return self._ctl_labeling_a(formula.subformula, structure)

        elif formula.type == 'E':
            # E(path formula) - must handle inner formula
            return self._ctl_labeling_e(formula.subformula, structure)

        elif formula.type == 'X':
            # AX or EX depending on context - default to EX
            return self._ex(formula.subformula, structure)

        elif formula.type == 'F':
            # EF - exists eventually
            return self._ef(formula.subformula, structure)

        elif formula.type == 'G':
            # EG - exists globally
            return self._eg(formula.subformula, structure)

        elif formula.type == 'U':
            # EU - exists until
            return self._eu(formula.left, formula.right, structure)

        return set()

    def _ctl_labeling_a(
        self,
        formula: TemporalFormula,
        structure: KripkeStructure,
    ) -> Set[str]:
        """Handle A (forall paths) quantifier."""
        if formula.type == 'X':
            return self._ax(formula.subformula, structure)
        elif formula.type == 'F':
            return self._af(formula.subformula, structure)
        elif formula.type == 'G':
            return self._ag(formula.subformula, structure)
        elif formula.type == 'U':
            return self._au(formula.left, formula.right, structure)
        return self._ctl_labeling(formula, structure)

    def _ctl_labeling_e(
        self,
        formula: TemporalFormula,
        structure: KripkeStructure,
    ) -> Set[str]:
        """Handle E (exists path) quantifier."""
        if formula.type == 'X':
            return self._ex(formula.subformula, structure)
        elif formula.type == 'F':
            return self._ef(formula.subformula, structure)
        elif formula.type == 'G':
            return self._eg(formula.subformula, structure)
        elif formula.type == 'U':
            return self._eu(formula.left, formula.right, structure)
        return self._ctl_labeling(formula, structure)

    def _ex(self, formula: TemporalFormula, structure: KripkeStructure) -> Set[str]:
        """EX φ: exists a successor satisfying φ."""
        phi_states = self._ctl_labeling(formula, structure)
        result = set()
        for s in structure.states:
            successors = structure.transitions.get(s, set())
            if successors & phi_states:
                result.add(s)
        return result

    def _ax(self, formula: TemporalFormula, structure: KripkeStructure) -> Set[str]:
        """AX φ: all successors satisfy φ."""
        phi_states = self._ctl_labeling(formula, structure)
        result = set()
        for s in structure.states:
            successors = structure.transitions.get(s, set())
            if successors and successors <= phi_states:
                result.add(s)
        return result

    def _ef(self, formula: TemporalFormula, structure: KripkeStructure) -> Set[str]:
        """EF φ: exists a path where φ eventually holds."""
        phi_states = self._ctl_labeling(formula, structure)
        return self._reachable_backward(phi_states, structure)

    def _af(self, formula: TemporalFormula, structure: KripkeStructure) -> Set[str]:
        """AF φ: on all paths, φ eventually holds."""
        phi_states = self._ctl_labeling(formula, structure)

        # Fixed point: AF φ = φ ∨ AX(AF φ)
        result = phi_states.copy()
        changed = True

        while changed:
            changed = False
            for s in structure.states - result:
                successors = structure.transitions.get(s, set())
                if successors and successors <= result:
                    result.add(s)
                    changed = True

        return result

    def _eg(self, formula: TemporalFormula, structure: KripkeStructure) -> Set[str]:
        """EG φ: exists a path where φ always holds."""
        phi_states = self._ctl_labeling(formula, structure)

        # Greatest fixed point
        result = phi_states.copy()
        changed = True

        while changed:
            changed = False
            for s in list(result):
                successors = structure.transitions.get(s, set())
                if not (successors & result):
                    result.discard(s)
                    changed = True

        return result

    def _ag(self, formula: TemporalFormula, structure: KripkeStructure) -> Set[str]:
        """AG φ: on all paths, φ always holds."""
        # AG φ = ¬EF(¬φ)
        not_phi = self.neg(formula)
        ef_not_phi = self._ef(not_phi, structure)
        return structure.states - ef_not_phi

    def _eu(
        self,
        phi: TemporalFormula,
        psi: TemporalFormula,
        structure: KripkeStructure
    ) -> Set[str]:
        """E[φ U ψ]: exists path where φ until ψ."""
        phi_states = self._ctl_labeling(phi, structure)
        psi_states = self._ctl_labeling(psi, structure)

        # Least fixed point
        result = psi_states.copy()
        changed = True

        while changed:
            changed = False
            for s in phi_states - result:
                successors = structure.transitions.get(s, set())
                if successors & result:
                    result.add(s)
                    changed = True

        return result

    def _au(
        self,
        phi: TemporalFormula,
        psi: TemporalFormula,
        structure: KripkeStructure
    ) -> Set[str]:
        """A[φ U ψ]: on all paths, φ until ψ."""
        phi_states = self._ctl_labeling(phi, structure)
        psi_states = self._ctl_labeling(psi, structure)

        # Least fixed point
        result = psi_states.copy()
        changed = True

        while changed:
            changed = False
            for s in phi_states - result:
                successors = structure.transitions.get(s, set())
                if successors and successors <= result:
                    result.add(s)
                    changed = True

        return result

    def _reachable_backward(
        self,
        target: Set[str],
        structure: KripkeStructure
    ) -> Set[str]:
        """Compute states from which target is reachable."""
        result = target.copy()
        changed = True

        while changed:
            changed = False
            for s in structure.states - result:
                successors = structure.transitions.get(s, set())
                if successors & result:
                    result.add(s)
                    changed = True

        return result

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming BDI message."""
        action = message.get('action', '')
        params = message.get('params', {})

        if action == 'check_ltl':
            result = self.check_ltl(**params)
            return {'status': 'success', 'result': result}
        elif action == 'check_ctl':
            result = self.check_ctl(**params)
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
    'TemporalLogicSpecialist',
    'TemporalFormula',
    'TemporalResult',
    'KripkeStructure',
    'TemporalLogicType',
]
