# SYMBO Agentic Reasoners

A hierarchical multi-agent system for mathematical problem solving using Belief-Desire-Intention (BDI) cognitive architecture.

## Overview

SYMBO (Symbolic Mathematical Boundary Operations) is a sophisticated mathematical reasoning engine that employs a 3-tier agent hierarchy to solve complex mathematical problems across multiple domains. The system is built on a **NO SYMPY** philosophy, implementing native mathematical operations to ensure full control, transparency, and educational value.

**Version**: 0.6.0
**Architecture**: Hierarchical Hub-and-Spoke with BDI Cognitive Agents
**License**: Apache 2.0
**Total Agents**: 60+ (1 Orchestrator + 12 Supervisors + 45+ Specialists)

## Core Philosophy

### Design Principles

1. **NO SYMPY by Agents** - All agents use native implementations for transparency and control
2. **NON-INTERVENTION** - Orchestrator delegates, never computes directly
3. **Tier Separation** - Clear responsibility boundaries between orchestrator, supervisors, and specialists
4. **Resource Enforcement** - VRAM limits, timeouts, and system throttling
5. **Knowledge Persistence** - Learn from past solutions through meta-learning

### Architecture Pattern

```
Orchestrator (Tier 1)
    |
    +-- Supervisors (Tier 2) - Domain routing and coordination
    |       |
    |       +-- Specialists (Tier 3) - Task execution
    |
    +-- Infrastructure - Agent lifecycle, resources, discovery
    +-- Middleware - Meta-learning, knowledge management
    +-- Core - Blackboard, BDI framework, native engines
```

## Directory Structure

```
symbo_agentic_reasoners/
├── agents/                   # Agent hierarchy (60+ agents)
│   ├── base/                 # Problem analysis, notation translation
│   ├── supervisors/          # 12 domain supervisors
│   ├── specialists/          # 45+ task specialists
│   ├── synthesis/            # Proof synthesis agents
│   └── provers/              # Formal verification
│
├── core/                     # Core components (26 modules)
│   ├── bdi_agent.py          # BDI cognitive framework (765 lines)
│   ├── blackboard.py         # Centralized workspace (605 lines)
│   ├── orchestrator.py       # Main coordinator (1,262 lines)
│   ├── native_calculus.py    # Native calculus engine (13,213+ lines)
│   ├── solver_engine.py      # Problem routing (1,676 lines)
│   └── ...                   # Math solvers, parsers, state management
│
├── infrastructure/           # Phase 0: Infrastructure (11 modules)
│   ├── ams.py                # Agent Management System
│   ├── directory_facilitator.py  # Service discovery
│   ├── watchdog.py           # Timeout enforcement
│   ├── resource_governor.py  # System resource control
│   └── ...                   # Agent pools, registry, factories
│
├── middleware/               # Phase 3: Meta-cognitive (12 modules)
│   ├── knowledge_management.py   # Solution caching
│   ├── meta_learning.py          # Learning from failures
│   ├── conflict_resolution.py    # Multi-agent conflicts
│   ├── theorem_library.py        # Mathematical knowledge base
│   └── ...                       # Pattern indexing, failure analysis
│
├── discovery/                # Phase 6: Discovery (3 subsystems)
│   ├── deep_search/          # Search tree management, parallel search
│   ├── conjecture/           # Pattern recognition, formalization
│   ├── algorithm/            # Algorithm synthesis, evolution
│   └── formal/               # Formal verification
│
├── optimization/             # Phase 5: Optimization
│   ├── evolutionary/         # Evolutionary algorithms
│   ├── learning/             # Student-teacher learning
│   └── parallel/             # Parallel execution
│
├── verification/             # Result verification
│   ├── second_opinion.py     # Multi-strategy verification
│   └── ...                   # Verification agents
│
├── solvers/                  # Domain-specific solvers
├── specialists/              # Specialist implementations
├── protocols/                # Communication protocols
├── monitoring/               # System monitoring
├── utils/                    # Utilities and helpers
├── integration/              # External integrations
└── config/                   # Configuration management
```

## Six-Phase Development

### Phase 0: Infrastructure
- Agent Management System (AMS) with VRAM enforcement
- Directory Facilitator for service discovery
- Agent Communication Channel (ACC)
- Watchdog for timeout enforcement
- Resource Governor for system throttling

### Phase 1: Cognitive Chassis
- BDI Agent framework (Belief-Desire-Intention)
- Blackboard system for shared workspace
- Message Bus for agent communication
- State Manager for system state

### Phase 2: Mathematical Workforce
- 12 Domain Supervisors
- 45+ Task Specialists
- Native mathematical engines (calculus, algebra, geometry, etc.)
- Domain detection and routing

### Phase 3: Meta-Cognitive Layer
- Knowledge Management (Look-Before-Leap)
- Meta-Learning from failures
- Conflict Resolution
- Theorem Library and Pattern Indexer

### Phase 4: Governance
- Security monitoring
- Resource coordination
- Fallback strategies
- Error handling and recovery

### Phase 5: Optimization
- Evolutionary algorithms
- Student-Teacher learning
- Parallel execution strategies
- Performance optimization

### Phase 6: Discovery
- Deep search with tree management
- Conjecture generation and formalization
- Algorithm synthesis
- Formal verification

## Agent Hierarchy

### Tier 1: Orchestrator (1 agent)
- **MainOrchestrator** - Problem decomposition, supervisor routing, result synthesis

### Tier 2: Supervisors (12 agents)
| Supervisor | Responsibility |
|------------|----------------|
| CalculusSupervisor | Routes to differentiation/integration/limits/series/ODE |
| AlgebraSupervisor | Routes to polynomial/equation/arithmetic specialists |
| LinearAlgebraSupervisor | Routes to matrix/decomposition/vector/tensor ops |
| GeometrySupervisor | Routes to euclidean/analytic/trigonometry |
| LogicSupervisor | Routes to propositional/predicate/proof logic |
| DiscreteMathSupervisor | Routes to combinatorics/graph theory |
| StatisticsSupervisor | Routes to Bayesian/frequentist/distribution |
| PhysicsMechanicsSupervisor | Routes to kinematics/dynamics/energy |
| PhysicsEMSupervisor | Routes to electrostatics/magnetism/circuits |
| PhysicsThermoSupervisor | Routes to thermodynamics/heat transfer |
| PhysicsQuantumSupervisor | Routes to quantum mechanics specialists |
| UnknownDomainSupervisor | Handles unclassified problems |

### Tier 3: Specialists (45+ agents)
Organized by domain:
- **Calculus**: Differentiation, Integration, Limit, Series, ODE (5 specialists)
- **Algebra**: Polynomial, Arithmetic, EquationSystem, NumberTheory (4 specialists)
- **Linear Algebra**: Matrix, Decomposition, VectorSpace, Tensor (4 specialists)
- **Geometry**: Euclidean, Analytic, Trigonometry (3 specialists)
- **Logic**: Propositional, Predicate, Proof (3 specialists)
- **Discrete**: Combinatorics, GraphTheory (2 specialists)
- **Statistics**: Bayesian, Frequentist, Distribution (3 specialists)
- **Physics**: 14 specialists across 4 physics domains

## Key Components

### Core Engine (core/)
- **BDI Framework**: Cognitive architecture with beliefs, desires, intentions
- **Blackboard**: Centralized workspace with pub-sub notifications
- **Native Calculus**: 13,213+ lines of pure Python calculus (differentiation, integration, limits, series)
- **Solver Engine**: Problem routing and domain detection
- **Native Symbolic**: Symbolic expression manipulation without SymPy
- **Native Complex**: Complex number operations
- **Safe Parser**: Expression parsing with security

### Infrastructure (infrastructure/)
- **AMS**: Agent lifecycle with memory enforcement (max 100 agents)
- **Directory Facilitator**: Service registration and discovery
- **Agent Pool**: Memory-efficient agent pooling
- **Watchdog**: Timeout enforcement (default 30s per agent)
- **Resource Governor**: System-wide throttling and limits

### Middleware (middleware/)
- **Knowledge Management**: Solution caching with Look-Before-Leap
- **Meta-Learning**: Learn from failures and successes
- **Theorem Library**: Mathematical knowledge base
- **Pattern Indexer**: Pattern recognition and matching
- **Conflict Resolution**: Multi-agent conflict mediation

### Discovery (discovery/)
- **Deep Search**: Search tree management with parallel exploration
- **Conjecture**: Pattern-based conjecture generation
- **Algorithm Synthesis**: Evolutionary algorithm generation
- **Formal Verification**: Proof verification

## Usage Examples

### Basic Problem Solving
```python
from symbo_agentic_reasoners.core.system import SymboSystem

# Initialize system
system = SymboSystem()

# Solve a calculus problem
result = system.solve("differentiate x^2 + 2x + 1")

# Solve an algebra problem
result = system.solve("solve x^2 - 5x + 6 = 0")

# Solve a linear algebra problem
result = system.solve("eigenvalues of [[1, 2], [2, 1]]")
```

### Advanced Usage with Configuration
```python
from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
from symbo_agentic_reasoners.infrastructure.ams import AMS

# Configure system
config = {
    'max_agents': 100,
    'agent_timeout': 30,
    'enable_meta_learning': True,
    'enable_knowledge_cache': True
}

# Initialize infrastructure
ams = AMS(config)

# Create orchestrator
orchestrator = MainOrchestrator(ams=ams)

# Solve with context
result = orchestrator.solve_problem(
    problem="integrate sin(x) * cos(x) dx",
    context={'domain': 'calculus', 'difficulty': 'intermediate'}
)
```

### Batch Processing
```python
from symbo_agentic_reasoners.batch_processor import BatchProcessor

processor = BatchProcessor()
problems = [
    "differentiate x^3",
    "integrate x^2 dx",
    "solve x^2 = 4"
]

results = processor.process_batch(problems, parallel=True)
```

## Dependencies

### Core Dependencies
- **Python**: >=3.9
- **SymPy**: >=1.12 (used minimally, agents use native implementations)
- **NumPy**: >=1.24.0
- **SciPy**: >=1.10.0
- **mpmath**: >=1.3.0

### Optional Dependencies
- **ML**: PyTorch >=2.0.0 (for neural-symbolic integration)
- **Vector**: ChromaDB, sentence-transformers (for semantic search)
- **Graph**: NetworkX >=3.0 (for graph theory)
- **Optimization**: scikit-optimize
- **Logic**: kanren (for logic programming)
- **Visualization**: matplotlib, plotly

## Installation

```bash
# Basic installation
pip install -e .

# With all features
pip install -e ".[full]"

# Development mode
pip install -e ".[dev]"
```

## Testing

```bash
# Run all tests
pytest

# Run specific phase tests
pytest -m phase0  # Infrastructure
pytest -m phase1  # Cognitive chassis
pytest -m phase2  # Mathematical workforce
pytest -m phase3  # Meta-cognitive
pytest -m phase4  # Governance
pytest -m phase5  # Optimization
pytest -m phase6  # Discovery

# Run with coverage
pytest --cov=src/symbo_agentic_reasoners --cov-report=html
```

## Documentation

- **System Architecture**: See `sonar files/system_structure_catalog.txt`
- **Research Synthesis**: See `sonar files/research_synthesis.md`
- **Phase Documentation**: See individual phase READMEs
- **Agent Documentation**: See `agents/README.md`

## Performance Characteristics

- **Agent Pool**: 100 max concurrent agents
- **Agent Timeout**: 30 seconds default
- **VRAM Enforcement**: Automatic agent cleanup
- **Parallel Execution**: Multi-strategy verification, parallel search
- **Caching**: Solution caching with Look-Before-Leap pattern

## Related Directories

- `../system_agents/` - System management agents (audit, cleanup, documentation)
- `../../tests/` - Comprehensive test suite (111+ test files)
- `../../scripts/` - Utility scripts and tools
- `../../docs/` - Additional documentation

## Contributing

When extending the system:

1. **Respect tier boundaries** - Orchestrator routes, Supervisors coordinate, Specialists execute
2. **Use native implementations** - Avoid SymPy in agent logic
3. **Add tests** - Include unit and integration tests
4. **Update documentation** - Keep READMEs current
5. **Follow BDI pattern** - Use beliefs, desires, intentions for cognitive agents

## License

Apache 2.0 - See NOTICE file for details

---

Generated by SYMBO Documentation System
Last Updated: 2025-12-14
