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
Logic Specialists Package
=========================

Provides comprehensive logic reasoning specialists:
- PropositionalLogicSpecialist: Truth tables, SAT solving, CNF/DNF
- PredicateLogicSpecialist: First-order logic, quantifiers, unification
- ProofSpecialist: Natural deduction, resolution proofs
- ModalLogicSpecialist: Kripke frames, K/T/S4/S5 systems
- TemporalLogicSpecialist: LTL and CTL model checking
"""

from symbo_agentic_reasoners.agents.specialists.logic.propositional_specialist import PropositionalLogicSpecialist
from symbo_agentic_reasoners.agents.specialists.logic.predicate_specialist import PredicateLogicSpecialist
from symbo_agentic_reasoners.agents.specialists.logic.proof_specialist import ProofSpecialist
from symbo_agentic_reasoners.agents.specialists.logic.modal_logic_specialist import (
    ModalLogicSpecialist, ModalFormula, ModalResult, KripkeFrame, ModalSystem
)
from symbo_agentic_reasoners.agents.specialists.logic.temporal_logic_specialist import (
    TemporalLogicSpecialist, TemporalFormula, TemporalResult, KripkeStructure, TemporalLogicType
)
from symbo_agentic_reasoners.agents.specialists.logic.sat_solver_specialist import (
    SATSolverSpecialist, SATResult, Clause
)

__all__ = [
    # Core logic
    'PropositionalLogicSpecialist',
    'PredicateLogicSpecialist',
    'ProofSpecialist',
    # Modal logic
    'ModalLogicSpecialist',
    'ModalFormula',
    'ModalResult',
    'KripkeFrame',
    'ModalSystem',
    # Temporal logic
    'TemporalLogicSpecialist',
    'TemporalFormula',
    'TemporalResult',
    'KripkeStructure',
    'TemporalLogicType',
    # SAT solving
    'SATSolverSpecialist',
    'SATResult',
    'Clause',
]
