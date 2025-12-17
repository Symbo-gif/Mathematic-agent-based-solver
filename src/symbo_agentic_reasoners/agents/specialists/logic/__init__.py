# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

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
