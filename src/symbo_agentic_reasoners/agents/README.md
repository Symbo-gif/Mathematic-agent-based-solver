# Agent Hierarchy

The complete 3-tier agent workforce for mathematical problem solving, organized by domain and capability.

## Overview

The agents directory contains the entire workforce of cognitive agents that solve mathematical problems. This hierarchy implements a **hub-and-spoke architecture** where the orchestrator coordinates supervisors, and supervisors coordinate specialists.

**Total Agents**: 260+ cognitive agents
**Organization**: 3 tiers (Orchestrator → Supervisors → Specialists)
**Architecture**: BDI (Belief-Desire-Intention) cognitive model

## Architecture Pattern

```
┌─────────────────────────────────────────────────┐
│  TIER 1: Orchestrator (1 agent)                │
│  - MainOrchestrator: Problem decomposition      │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼────────┐
│ TIER 2:        │  │ TIER 2:        │
│ Supervisors    │  │ Supervisors    │
│ (38 agents)    │  │ (Continued)    │
│                │  │                │
│ • Calculus     │  │ • Complex      │
│ • Algebra      │  │ • Category     │
│ • LinearAlg    │  │ • Crypto       │
│ • Geometry     │  │ • Info Theory  │
│ • Logic        │  │ • Control      │
│ • Stats        │  │ • Optimization │
│ • Physics (4)  │  │ • And 20+ more │
└────────┬───────┘  └────────┬───────┘
         │                   │
    ┌────┴────┐         ┌────┴────┐
    │         │         │         │
┌───▼───┐ ┌──▼───┐ ┌───▼───┐ ┌──▼───┐
│ TIER 3: Specialists (220+ agents)│
│ - Task execution across 30 domains│
│ - Native mathematical operations   │
└────────────────────────────────────┘
```

## Directory Structure

```
agents/
├── __init__.py
│
├── base/                      # Problem analysis agents
│   ├── problem_analysis.py    # Problem decomposition & domain detection
│   └── notation_translator.py # Mathematical notation conversion
│
├── supervisors/               # Tier 2: Domain coordinators (38)
│   ├── calculus_supervisor.py
│   ├── algebra_supervisor.py
│   ├── linalg_supervisor.py
│   ├── geometry_supervisor.py
│   ├── logic_supervisor.py
│   ├── discrete_math_supervisor.py
│   ├── stats_supervisor.py
│   ├── physics_mechanics_supervisor.py
│   ├── physics_em_supervisor.py
│   ├── physics_thermo_supervisor.py
│   ├── physics_quantum_supervisor.py
│   ├── complex_analysis_supervisor.py
│   ├── real_analysis_supervisor.py
│   ├── functional_analysis_supervisor.py
│   ├── category_theory_supervisor.py
│   ├── algebraic_topology_supervisor.py
│   ├── diff_geometry_supervisor.py
│   ├── riemannian_geometry_supervisor.py
│   ├── cryptography_supervisor.py
│   ├── information_theory_supervisor.py
│   ├── control_theory_supervisor.py
│   ├── optimization_supervisor.py
│   ├── stochastic_processes_supervisor.py
│   ├── elementary_number_theory_supervisor.py
│   ├── algebraic_number_theory_supervisor.py
│   ├── analytic_number_theory_supervisor.py
│   ├── finite_fields_supervisor.py
│   ├── model_theory_supervisor.py
│   ├── proof_theory_supervisor.py
│   ├── computability_supervisor.py
│   ├── spectral_graph_theory_supervisor.py
│   ├── tda_supervisor.py
│   ├── ergodic_theory_supervisor.py
│   ├── geometric_measure_supervisor.py
│   ├── inequalities_convexity_supervisor.py
│   ├── bayesian_decision_theory_supervisor.py
│   ├── timeseries_supervisor.py
│   └── learning_enhancement_supervisor.py
│
├── specialists/               # Tier 3: Task executors (220+ across 30 domains)
│   ├── algebra/               # Polynomial, Arithmetic, Equations, Number Theory
│   ├── algebraic_topology/    # Homology, Homotopy, Cohomology
│   ├── calculus/              # Differentiation, Integration, Limits, Series, ODE
│   ├── category_theory/       # Functors, Natural Transformations
│   ├── complex_analysis/      # Contour Integration, Residues
│   ├── computability/         # Turing Machines, Decidability
│   ├── control_theory/        # Stability, Controllability
│   ├── cryptography/          # Encryption, Digital Signatures
│   ├── diff_geometry/         # Manifolds, Curvature
│   ├── discrete_math/         # Combinatorics, Graph Theory
│   ├── ergodic/               # Dynamical Systems, Measure Theory
│   ├── functional_analysis/   # Operators, Banach Spaces
│   ├── geometric_measure/     # Hausdorff Dimension, Fractals
│   ├── geometry/              # Euclidean, Analytic, Trigonometry
│   ├── inequalities/          # Convex Analysis, Inequalities
│   ├── information_theory/    # Entropy, Coding Theory
│   ├── learning/              # Meta-learning, Adaptation
│   ├── linear_algebra/        # Matrix, Decomposition, Vector Space
│   ├── logic/                 # Propositional, Predicate, Proof
│   ├── model_theory/          # Model Theory, Satisfiability
│   ├── numerical/             # Numerical Methods
│   ├── optimization/          # Convex, Nonlinear Optimization
│   ├── physics/               # Mechanics, EM, Thermo, Quantum
│   ├── proof_theory/          # Formal Proofs, Type Theory
│   ├── real_analysis/         # Measure Theory, Convergence
│   ├── riemannian/            # Metric Tensors, Geodesics
│   ├── statistics/            # Bayesian, Frequentist, Distribution
│   ├── stochastic/            # Markov Chains, Random Processes
│   └── tda/                   # Persistent Homology, Topology
│
├── synthesis/                 # Result synthesis
│   ├── proof_synthesizer.py
│   └── solution_formatter.py
│
└── provers/                   # Formal verification
    ├── theorem_prover.py
    └── proof_validator.py
```

## Tier 1: Orchestrator

### MainOrchestrator (in ../core/orchestrator.py)

**Role**: The "General Contractor" - coordinates entire problem-solving process

**Responsibilities**:
1. Receive problem from user
2. Decompose into subtasks using HTN (Hierarchical Task Network)
3. Route subtasks to appropriate supervisors
4. Synthesize partial results into final solution
5. Coordinate meta-learning and knowledge caching

**CRITICAL CONSTRAINT**:
**NON-INTERVENTION DIRECTIVE** - Orchestrator NEVER performs calculations. If it sees "2+2", it must delegate, never compute.

**Workflow**:
```
User Problem
    ↓
[Analyze Problem] → Problem Structure, Domain, Complexity
    ↓
[Decompose] → Subtask 1, Subtask 2, ..., Subtask N
    ↓
[Route] → Supervisor 1, Supervisor 2, ...
    ↓
[Collect Partial Results]
    ↓
[Synthesize Final Solution]
    ↓
Return to User
```

---

## Tier 2: Supervisors (38 Agents)

Supervisors are **strategic routers** that coordinate specialists within their domain. They never compute - only route and coordinate.

### Core Mathematical Supervisors

#### CalculusSupervisor
**Domain**: Calculus (differentiation, integration, limits, series, ODEs)

#### AlgebraSupervisor
**Domain**: Algebra (polynomials, equations, arithmetic, number theory)

#### LinearAlgebraSupervisor (linalg)
**Domain**: Linear algebra (matrices, vectors, eigenvalues, tensors)

#### GeometrySupervisor
**Domain**: Geometry (Euclidean, analytic, trigonometry)

#### LogicSupervisor
**Domain**: Mathematical logic (propositional, predicate, proofs)

#### DiscreteMathSupervisor
**Domain**: Discrete mathematics (combinatorics, graph theory)

#### StatsSupervisor
**Domain**: Statistics and probability

### Physics Supervisors

#### PhysicsMechanicsSupervisor
**Domain**: Classical mechanics (kinematics, dynamics, energy)

#### PhysicsEMSupervisor
**Domain**: Electromagnetism (electrostatics, magnetism, circuits)

#### PhysicsThermoSupervisor
**Domain**: Thermodynamics (heat transfer, gas laws, entropy)

#### PhysicsQuantumSupervisor
**Domain**: Quantum mechanics (wave functions, operators)

### Advanced Analysis Supervisors

#### ComplexAnalysisSupervisor
**Domain**: Complex analysis (contour integration, residues, conformal mapping)

#### RealAnalysisSupervisor
**Domain**: Real analysis (measure theory, convergence, Lebesgue integration)

#### FunctionalAnalysisSupervisor
**Domain**: Functional analysis (operators, Banach/Hilbert spaces)

### Algebra & Number Theory Supervisors

#### ElementaryNumberTheorySupervisor
**Domain**: Elementary number theory (primes, divisibility, modular arithmetic)

#### AlgebraicNumberTheorySupervisor
**Domain**: Algebraic number theory (algebraic integers, ideals)

#### AnalyticNumberTheorySupervisor
**Domain**: Analytic number theory (Riemann zeta, L-functions)

#### FiniteFieldsSupervisor
**Domain**: Finite fields and Galois theory

### Geometry & Topology Supervisors

#### DiffGeometrySupervisor
**Domain**: Differential geometry (manifolds, curvature)

#### RiemannianGeometrySupervisor
**Domain**: Riemannian geometry (metric tensors, geodesics)

#### AlgebraicTopologySupervisor
**Domain**: Algebraic topology (homology, homotopy, cohomology)

#### GeometricMeasureSupervisor
**Domain**: Geometric measure theory (Hausdorff dimension, fractals)

### Logic & Foundations Supervisors

#### ModelTheorySupervisor
**Domain**: Model theory (structures, satisfiability)

#### ProofTheorySupervisor
**Domain**: Proof theory (formal proofs, type theory)

#### ComputabilitySupervisor
**Domain**: Computability theory (Turing machines, decidability)

#### CategoryTheorySupervisor
**Domain**: Category theory (functors, natural transformations)

### Applied Mathematics Supervisors

#### CryptographySupervisor
**Domain**: Cryptography (encryption, digital signatures, protocols)

#### InformationTheorySupervisor
**Domain**: Information theory (entropy, channel capacity, coding)

#### ControlTheorySupervisor
**Domain**: Control theory (stability, controllability, observers)

#### OptimizationSupervisor
**Domain**: Optimization (convex, nonlinear, combinatorial)

#### StochasticProcessesSupervisor
**Domain**: Stochastic processes (Markov chains, random processes)

#### BayesianDecisionTheorySupervisor
**Domain**: Decision theory (risk analysis, utility theory)

#### TimeseriesSupervisor
**Domain**: Time series analysis (forecasting, ARIMA, spectral)

### Specialized Domain Supervisors

#### SpectralGraphTheorySupervisor
**Domain**: Spectral graph theory (graph eigenvalues, Laplacians)

#### TDASupervisor
**Domain**: Topological data analysis (persistent homology, Betti numbers)

#### ErgodicTheorySupervisor
**Domain**: Ergodic theory (dynamical systems, measure-preserving)

#### InequalitiesConvexitySupervisor
**Domain**: Inequalities and convex analysis

#### LearningEnhancementSupervisor
**Domain**: Meta-learning and adaptive strategies

---

## Tier 3: Specialists (220+ Agents)

Specialists are **task executors** - they actually perform mathematical computations using native implementations.

### Key Specialist Examples

#### DifferentiationSpecialist

**Capabilities**:
- Power rule, product rule, quotient rule, chain rule
- Implicit differentiation
- Partial derivatives
- Higher-order derivatives

**Native Implementation**: Uses pure Python differentiation engine (no SymPy)

**Example**:
```python
from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import DifferentiationSpecialist

specialist = DifferentiationSpecialist()
result = specialist.solve("differentiate x^2 * sin(x) with respect to x")
# Result: "2*x*sin(x) + x^2*cos(x)"
```

---

#### IntegrationSpecialist

**Capabilities**:
- Substitution method
- Integration by parts
- Trigonometric integrals
- Partial fractions
- Numerical integration (when symbolic fails)

**Critical Feature**: Detects when function is not analytically integrable and falls back to numerical methods.

**Example**:
```python
from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist

specialist = IntegrationSpecialist()
result = specialist.solve("integrate x * exp(x) dx")
# Result: "x*exp(x) - exp(x) + C"
```

---

#### PolynomialSpecialist

**Capabilities**:
- Factorization (quadratic, cubic, quartic)
- Root finding (analytical and numerical)
- Polynomial division
- GCD of polynomials

**Example**:
```python
from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import PolynomialSpecialist

specialist = PolynomialSpecialist()
result = specialist.solve("factor x^2 - 5*x + 6")
# Result: "(x - 2)(x - 3)"
```

---

#### MatrixOperations

**Capabilities**:
- Matrix multiplication, addition
- Determinant calculation
- Matrix inversion
- Rank computation
- Trace computation

**Example**:
```python
from symbo_agentic_reasoners.agents.specialists.linear_algebra.matrix_operations import MatrixOperations

specialist = MatrixOperations()
result = specialist.solve("find eigenvalues of [[1, 2], [2, 1]]")
# Result: "[-1, 3]"
```

---

## Base Agents

### problem_analysis.py

**Purpose**: Analyze and decompose problems into structured representations

**Key Classes**:
- `MathDomain` - Enum of mathematical domains
- `StructuredProblem` - Problem representation with metadata
- `ProblemAnalyzer` - Analysis and decomposition logic

**Functions**:
- Domain detection from keywords
- Complexity assessment
- Dependency analysis
- Subtask generation

---

### notation_translator.py

**Purpose**: Convert between different mathematical notations

**Functions**:
- LaTeX to plaintext
- Plaintext to SymPy-compatible
- Unicode symbol handling
- Notation normalization

---

## Design Principles

### 1. Tier Separation

**Orchestrator** (Tier 1):
- Coordinates and delegates
- NEVER computes
- Synthesizes results

**Supervisors** (Tier 2):
- Route to specialists
- Coordinate within domain
- NEVER compute

**Specialists** (Tier 3):
- Execute computations
- Use native implementations
- Return results

### 2. NO SYMPY by Agents

All specialists use **native Python implementations** for mathematical operations. SymPy may be used for verification only, never for primary computation.

**Why?**
- Full transparency and control
- Educational value
- No external dependency for core logic
- Easier debugging and understanding

### 3. BDI Cognitive Architecture

All agents inherit from `BDIAgent` and implement:
- **Beliefs**: Knowledge about the problem
- **Desires**: Goals to achieve
- **Intentions**: Plans to execute

### 4. Specialization Over Generalization

Each specialist is narrowly focused on one task type. This ensures:
- Expert-level performance in specialty
- Clear responsibility boundaries
- Easier testing and maintenance
- Modular replacement/improvement

### 5. Fallback Strategies

When primary strategy fails:
1. Try alternative strategy
2. Request help from related specialist
3. Escalate to supervisor
4. Return partial result with explanation

---

## Agent Communication

Agents communicate via:

1. **Blackboard**: Post tasks, retrieve results
2. **Message Bus**: Direct agent-to-agent messages
3. **Directory Facilitator**: Service discovery
4. **FIPA-ACL Protocol**: Standardized messages

**Example Flow**:
```
Orchestrator → [Blackboard] → Post "integrate sin(x) dx"
                    ↓
CalculusSupervisor → Subscribe to "calculus" tag
                    ↓
                 Retrieve task
                    ↓
IntegrationSpecialist → Solve → Post result "-cos(x) + C"
                    ↓
Orchestrator → Retrieve result → Synthesize solution
```

---

## Testing

Each agent has dedicated unit tests:

```bash
# Test supervisors
pytest tests/test_supervisors.py

# Test calculus specialists
pytest tests/test_calculus_specialists.py

# Test algebra specialists
pytest tests/test_algebra_specialists.py

# Test all specialists
pytest tests/test_specialists.py

# Integration tests
pytest tests/test_phase2.py
pytest tests/multi_agent_test_suite.py
```

---

## Usage Examples

### Using a Supervisor Directly

```python
from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor
from symbo_agentic_reasoners.core.blackboard import Blackboard

blackboard = Blackboard()
supervisor = CalculusSupervisor(blackboard=blackboard)

result = supervisor.route_task({
    'operation': 'differentiate',
    'expression': 'x^2 + 2*x',
    'variable': 'x'
})
```

### Using a Specialist Directly

```python
from symbo_agentic_reasoners.agents.specialists.calculus.differentiation_specialist import DifferentiationSpecialist

specialist = DifferentiationSpecialist()
derivative = specialist.differentiate("sin(x) * cos(x)", "x")
# Result: "cos(x)*cos(x) - sin(x)*sin(x)"
```

### Full System Integration

```python
from symbo_agentic_reasoners.core.system import SymboSystem

system = SymboSystem()
result = system.solve("solve x^2 - 5x + 6 = 0")
# Automatically routes through: Orchestrator → AlgebraSupervisor → EquationSystemSolver
```

---

## Performance Characteristics

- **Agent Count**: 260+ agents (1 orchestrator + 38 supervisors + 220+ specialists)
- **Domain Coverage**: 30+ specialized mathematical domains
- **Routing Decision**: <1ms per supervisor
- **Specialist Execution**: 10ms-10s depending on complexity
- **Native Implementations**: Full transparency and control
- **Concurrent Execution**: Multiple specialists can run in parallel

---

## Future Enhancements

1. **Dynamic Specialist Generation**: Create specialists on-the-fly for rare tasks
2. **Meta-Supervisors**: Higher-level coordination for cross-domain problems
3. **Learning Routing**: Supervisors learn optimal routing from past problems
4. **Specialist Collaboration**: Direct specialist-to-specialist communication

---

## Related Components

- `../core/` - BDI framework, Blackboard, Orchestrator
- `../infrastructure/` - AMS, Directory Facilitator, Agent Pool
- `../middleware/` - Knowledge Management, Meta-Learning
- `../../tests/` - Comprehensive agent tests

---

Generated by SYMBO Documentation System
Last Updated: 2026-01-04
