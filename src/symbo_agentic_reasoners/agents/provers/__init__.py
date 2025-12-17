# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
"""
Prover Team Agents - Phase 6
============================

This package contains agents for formal proof construction and verification:

- PRV-1: LogicalProver - Resolution and natural deduction proofs
- PRV-2: ModelChecker - State space exploration and model checking
"""

from .logical_prover import LogicalProver
from .model_checker import ModelChecker

__all__ = [
    'LogicalProver',
    'ModelChecker'
]
