# SYMBO_AGENTIC_REASONERS Project Structure - BEFORE Reorganization
## Captured: 2025-12-06

This document captures the project structure before the src-layout reorganization.

## Root Directory Structure

```
Mathematic-agent-based-solver/
├── symbo_agentic_reasoners_phase0/                    # Phase 0: Foundational Infrastructure
│   ├── __init__.py
│   ├── phase0_system.py
│   ├── README.md
│   ├── core/
│   │   ├── __init__.py
│   │   ├── bdi_agent.py           # BDI cognitive framework
│   │   ├── fipa_acl.py            # FIPA-ACL communication
│   │   └── omdoc_schema.py        # OMDoc mathematical encoding
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── acc.py                 # Agent Communication Channel
│   │   ├── ams.py                 # Agent Management System
│   │   └── directory_facilitator.py
│   └── memory/
│       ├── __init__.py
│       ├── blackboard.py          # Shared memory workspace
│       └── vector_database.py     # Long-term RAG memory
│
├── symbo_agentic_reasoners_phase1/                    # Phase 1: Cognitive Chassis
│   ├── __init__.py
│   ├── phase1_system.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── problem_analysis.py    # Problem Analysis Team
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── main_orchestrator.py   # Main Orchestrator (Tier 1)
│   ├── solvers/
│   │   ├── __init__.py
│   │   └── pilot_solver.py        # Pilot Solver (SymPy wrapper)
│   └── verification/
│       ├── __init__.py
│       └── verification_core.py   # Verification Core
│
├── symbo_agentic_reasoners_phase2/                    # Phase 2: Vertical Domain Expansion
│   ├── __init__.py
│   ├── phase2_system.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── algebra/
│   │   │   ├── __init__.py
│   │   │   ├── arithmetic_specialist.py
│   │   │   ├── number_theory_specialist.py
│   │   │   └── polynomial_specialist.py
│   │   ├── calculus/
│   │   │   ├── __init__.py
│   │   │   ├── differentiation_specialist.py
│   │   │   ├── integration_specialist.py
│   │   │   ├── ode_solver.py
│   │   │   └── series_specialist.py
│   │   ├── discrete_math/
│   │   │   ├── __init__.py
│   │   │   ├── combinatorics_agent.py
│   │   │   └── graph_theory_agent.py
│   │   ├── linear_algebra/
│   │   │   ├── __init__.py
│   │   │   ├── decomposition_specialist.py
│   │   │   ├── matrix_ops_specialist.py
│   │   │   └── vector_space_analyst.py
│   │   ├── numerical/
│   │   │   ├── __init__.py
│   │   │   └── numerical_utility.py
│   │   └── statistics/
│   │       ├── __init__.py
│   │       ├── bayesian_engine.py
│   │       ├── distribution_specialist.py
│   │       └── frequentist_agent.py
│   └── supervisors/
│       ├── __init__.py
│       ├── algebra_supervisor.py
│       ├── calculus_supervisor.py
│       ├── linalg_supervisor.py
│       └── stats_supervisor.py
│
├── symbo_agentic_reasoners_phase3/                    # Phase 3: Meta-Cognitive Middleware
│   ├── __init__.py
│   ├── phase3_system.py
│   ├── hypothesis/
│   │   ├── __init__.py
│   │   └── hypothesis_generation.py
│   ├── knowledge/
│   │   ├── __init__.py
│   │   └── knowledge_management.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── phase3_orchestrator.py
│   └── validation/
│       ├── __init__.py
│       └── precondition_validation.py
│
├── symbo_agentic_reasoners_phase4/                    # Phase 4: Self-Correction Engine
│   ├── __init__.py
│   ├── phase4_system.py
│   ├── failure_analysis/
│   │   ├── __init__.py
│   │   └── failure_analysis_team.py
│   ├── governance/
│   │   ├── __init__.py
│   │   └── conflict_resolution.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── protocol_updates.py
│   └── meta_learning/
│       ├── __init__.py
│       └── meta_learning_team.py
│
├── symbo_agentic_reasoners_phase5/                    # Phase 5: Production Optimization
│   ├── __init__.py
│   ├── phase5_system.py
│   ├── distillation/
│   │   ├── __init__.py
│   │   ├── distillation_pipeline.py
│   │   └── thought_trace_harvester.py
│   ├── evolution/
│   │   ├── __init__.py
│   │   └── evolutionary_flywheel.py
│   ├── hardening/
│   │   ├── __init__.py
│   │   ├── identity_manager.py
│   │   └── user_simulator.py
│   ├── hybrid_deployment/
│   │   ├── __init__.py
│   │   ├── complexity_gatekeeper.py
│   │   └── confidence_fallback.py
│   ├── monitoring/
│   │   ├── __init__.py
│   │   └── dependency_monitor.py
│   └── symbo/
│       ├── __init__.py
│       ├── nano_tensor.py
│       ├── symbo_llm.py
│       └── symbo_llm_core.py
│
├── symbo_agentic_reasoners_phase6/                    # Phase 6: Discovery Engine
│   ├── __init__.py
│   ├── phase6_system.py
│   ├── algorithm_discovery/
│   │   ├── __init__.py
│   │   ├── code_evolutionary_proposer.py
│   │   ├── heuristic_distiller.py
│   │   ├── problem_specification.py
│   │   └── sandbox_evaluator.py
│   ├── conjecture_generation/
│   │   ├── __init__.py
│   │   ├── conjecture_formalizer.py
│   │   ├── pattern_recognizer.py
│   │   └── synthetic_data_generator.py
│   ├── deep_search/
│   │   ├── __init__.py
│   │   ├── critic_network.py
│   │   ├── policy_network.py
│   │   ├── prover_engine.py
│   │   ├── search_tree_manager.py
│   │   └── types.py
│   ├── formal_knowledge_integration/
│   │   ├── __init__.py
│   │   ├── auto_formalization_pipeline.py
│   │   └── vector_database_updater.py
│   └── undecidability_navigator/
│       ├── __init__.py
│       ├── decidability_checker.py
│       └── interactive_guidance_liaison.py
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── mocks/
│   │   ├── __init__.py
│   │   ├── mock_prover.py
│   │   ├── mock_student.py
│   │   ├── mock_supervisor.py
│   │   └── mock_vector_db.py
│   ├── test_dependencies.py
│   ├── test_dependency_injection.py
│   ├── test_mock_embeddings_fix.py
│   ├── test_phase0.py
│   ├── test_phase1.py
│   ├── test_phase2.py
│   ├── test_phase2_health.py
│   ├── test_phase3.py
│   ├── test_phase3_integration.py
│   ├── test_phase3_supervisor_fix.py
│   ├── test_phase4.py
│   ├── test_phase5_phase6_integration.py
│   ├── test_phase5_student_fix.py
│   ├── test_phase6_prover_fix.py
│   └── test_vector_database.py
│
├── audit/                          # Audit infrastructure
│   ├── __init__.py
│   ├── audit_runner.py
│   ├── comprehensive/
│   ├── phase1/ - phase6/          # Per-phase audit tools
│   ├── reporters/
│   ├── reports/
│   └── tests/
│
├── scripts/                        # Utility scripts
│   ├── __init__.py
│   ├── build_remaining_agents.py
│   ├── convert_docs.py
│   ├── quick_test.py
│   ├── run_all_audits.py
│   ├── start_full_system.py
│   └── verify_installation.py
│
├── docs/                           # Documentation
│   ├── SIMULATION_BOUNDARIES.md
│   └── TEST_RESULTS.md
│
├── Archive assessments/            # Archived assessment documents
├── critical assessments/           # Active critical assessments
├── Reference Documents/            # Phase reference documentation
├── user_help/                      # User documentation
├── output/                         # Runtime output
├── thought_traces/                 # Agent reasoning traces
├── audit_thought_traces/           # Audit logging traces
├── test_thought_traces/            # Test run traces
│
├── symbo_agentic_reasoners_logging.py                 # Root-level logging module
├── pyproject.toml                  # Package configuration
├── requirements.txt                # Core dependencies
├── requirements-dev.txt            # Development dependencies
└── requirements-full.txt           # Full dependencies
```

## Identified Issues

1. **Root-level module pollution**: `symbo_agentic_reasoners_logging.py` at root level
2. **Phase folder fragmentation**: 7 separate `symbo_agentic_reasoners_phaseN/` folders
3. **Scattered trace directories**: 3 trace folders at root
4. **Space-containing folder names**: "Archive assessments", "critical assessments"
5. **No src-layout**: Packages directly at root, not in `src/`
6. **Import complexity**: Cross-phase imports use `sys.path` manipulation

## Current Import Pattern

```python
# Current pattern (Phase 1 importing Phase 0):
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from symbo_agentic_reasoners_phase0.core.bdi_agent import BDIAgent
from symbo_agentic_reasoners_phase0.memory.blackboard import Blackboard
```

## Package Configuration (Current)

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["symbo_agentic_reasoners_phase*", "symbo_agentic_reasoners_logging"]
```
