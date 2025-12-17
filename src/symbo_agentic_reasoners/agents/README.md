# Agent Hierarchy

The complete 3-tier agent workforce for mathematical problem solving, organized by domain and capability.

## Overview

The agents directory contains the entire workforce of cognitive agents that solve mathematical problems. This hierarchy implements a **hub-and-spoke architecture** where the orchestrator coordinates supervisors, and supervisors coordinate specialists.

**Total Agents**: 60+ cognitive agents
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
│ (12 agents)    │  │ (Continued)    │
│                │  │                │
│ • Calculus     │  │ • Logic        │
│ • Algebra      │  │ • Stats        │
│ • LinearAlg    │  │ • Physics (4)  │
│ • Geometry     │  │ • Unknown      │
└────────┬───────┘  └────────┬───────┘
         │                   │
    ┌────┴────┐         ┌────┴────┐
    │         │         │         │
┌───▼───┐ ┌──▼───┐ ┌───▼───┐ ┌──▼───┐
│ TIER 3: Specialists (45+ agents)  │
│ - Task execution                   │
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
├── supervisors/               # Tier 2: Domain coordinators (12)
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
│   └── physics_quantum_supervisor.py
│
├── specialists/               # Tier 3: Task executors (45+)
│   ├── calculus/              # 5 specialists
│   │   ├── differentiation_specialist.py
│   │   ├── integration_specialist.py
│   │   ├── limit_evaluator.py
│   │   ├── series_specialist.py
│   │   └── ode_solver.py
│   │
│   ├── algebra/               # 5 specialists
│   │   ├── polynomial_specialist.py
│   │   ├── arithmetic_specialist.py
│   │   ├── equation_system_solver.py
│   │   ├── number_theory_specialist.py
│   │   └── group_ring_theory.py
│   │
│   ├── linear_algebra/        # 4 specialists
│   │   ├── matrix_operations.py
│   │   ├── decomposition_specialist.py
│   │   ├── vector_space_specialist.py
│   │   └── tensor_operations.py
│   │
│   ├── geometry/              # 3 specialists
│   │   ├── euclidean_specialist.py
│   │   ├── analytic_geometry.py
│   │   └── trigonometry_specialist.py
│   │
│   ├── logic/                 # 3 specialists
│   │   ├── propositional_logic.py
│   │   ├── predicate_logic.py
│   │   └── proof_assistant.py
│   │
│   ├── discrete_math/         # 2 specialists
│   │   ├── combinatorics_specialist.py
│   │   └── graph_theory_specialist.py
│   │
│   ├── statistics/            # 3 specialists
│   │   ├── bayesian_specialist.py
│   │   ├── frequentist_specialist.py
│   │   └── distribution_specialist.py
│   │
│   ├── physics/               # 14 specialists
│   │   ├── mechanics/         # 4 specialists
│   │   │   ├── kinematics.py
│   │   │   ├── dynamics.py
│   │   │   ├── energy_conservation.py
│   │   │   └── rotational_mechanics.py
│   │   │
│   │   ├── electromagnetism/  # 4 specialists
│   │   │   ├── electrostatics.py
│   │   │   ├── magnetism.py
│   │   │   ├── circuits.py
│   │   │   └── em_waves.py
│   │   │
│   │   ├── thermodynamics/    # 3 specialists
│   │   │   ├── heat_transfer.py
│   │   │   ├── gas_laws.py
│   │   │   └── entropy.py
│   │   │
│   │   └── quantum/           # 3 specialists
│   │       ├── wave_functions.py
│   │       ├── operators.py
│   │       └── uncertainty.py
│   │
│   └── numerical/             # Numerical specialists
│       └── numerical_methods.py
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

## Tier 2: Supervisors (12 Agents)

Supervisors are **strategic routers** that coordinate specialists within their domain. They never compute - only route and coordinate.

### 1. CalculusSupervisor

**Domain**: Calculus (differentiation, integration, limits, series, ODEs)

**Specialists Managed**:
- DifferentiationSpecialist - Derivatives using chain rule, product rule, etc.
- IntegrationSpecialist - Integrals using substitution, parts, etc.
- LimitEvaluator - Limits using L'Hôpital's rule
- SeriesSpecialist - Taylor series, power series
- ODESolver - Ordinary differential equations

**Critical Decision**: Distinguish between exact (symbolic) and approximate (numerical) requests to avoid wasting resources on non-integrable functions.

**Routing Keywords**:
- "differentiate", "derivative", "gradient" → DifferentiationSpecialist
- "integrate", "antiderivative", "area under curve" → IntegrationSpecialist
- "limit", "approaches" → LimitEvaluator
- "series", "Taylor", "Maclaurin" → SeriesSpecialist
- "differential equation", "ODE" → ODESolver

---

### 2. AlgebraSupervisor

**Domain**: Algebra (polynomials, equations, arithmetic, number theory)

**Specialists Managed**:
- PolynomialSpecialist - Factorization, roots, division
- ArithmeticSpecialist - Basic operations, simplification
- EquationSystemSolver - Systems of linear/nonlinear equations
- NumberTheorySpecialist - Primes, GCD, modular arithmetic
- GroupRingTheory - Abstract algebra structures

**Routing Keywords**:
- "factor", "expand", "polynomial" → PolynomialSpecialist
- "solve", "equation" → EquationSystemSolver
- "prime", "divisor", "GCD" → NumberTheorySpecialist
- "group", "ring", "field" → GroupRingTheory

---

### 3. LinearAlgebraSupervisor

**Domain**: Linear algebra (matrices, vectors, eigenvalues, tensors)

**Specialists Managed**:
- MatrixOperations - Addition, multiplication, inverse, determinant
- DecompositionSpecialist - LU, QR, SVD, Cholesky
- VectorSpaceSpecialist - Basis, span, orthogonality
- TensorOperations - Tensor algebra and calculus

**Routing Keywords**:
- "matrix", "determinant", "inverse" → MatrixOperations
- "eigenvalue", "eigenvector", "decomposition" → DecompositionSpecialist
- "basis", "span", "orthogonal" → VectorSpaceSpecialist
- "tensor" → TensorOperations

---

### 4. GeometrySupervisor

**Domain**: Geometry (Euclidean, analytic, trigonometry)

**Specialists Managed**:
- EuclideanSpecialist - Classical geometry, proofs
- AnalyticGeometry - Coordinate geometry, conic sections
- TrigonometrySpecialist - Trig identities, solving triangles

**Routing Keywords**:
- "triangle", "circle", "polygon" → EuclideanSpecialist
- "distance", "midpoint", "conic" → AnalyticGeometry
- "sin", "cos", "tan", "trigonometric" → TrigonometrySpecialist

---

### 5. LogicSupervisor

**Domain**: Mathematical logic (propositional, predicate, proofs)

**Specialists Managed**:
- PropositionalLogic - Boolean logic, truth tables
- PredicateLogic - First-order logic, quantifiers
- ProofAssistant - Formal proof construction

**Routing Keywords**:
- "truth table", "boolean", "AND", "OR" → PropositionalLogic
- "forall", "exists", "predicate" → PredicateLogic
- "prove", "theorem" → ProofAssistant

---

### 6. DiscreteMathSupervisor

**Domain**: Discrete mathematics (combinatorics, graph theory)

**Specialists Managed**:
- CombinatoricsSpecialist - Permutations, combinations, counting
- GraphTheorySpecialist - Graphs, paths, connectivity

**Routing Keywords**:
- "permutation", "combination", "count" → CombinatoricsSpecialist
- "graph", "vertex", "edge", "path" → GraphTheorySpecialist

---

### 7. StatisticsSupervisor

**Domain**: Statistics and probability

**Specialists Managed**:
- BayesianSpecialist - Bayesian inference, priors
- FrequentistSpecialist - Hypothesis testing, confidence intervals
- DistributionSpecialist - Probability distributions, moments

**Routing Keywords**:
- "Bayesian", "prior", "posterior" → BayesianSpecialist
- "p-value", "hypothesis test", "confidence" → FrequentistSpecialist
- "distribution", "probability", "expected value" → DistributionSpecialist

---

### 8-11. Physics Supervisors (4 domains)

#### PhysicsMechanicsSupervisor
**Specialists**: Kinematics, Dynamics, EnergyConservation, RotationalMechanics

#### PhysicsEMSupervisor
**Specialists**: Electrostatics, Magnetism, Circuits, EMWaves

#### PhysicsThermoSupervisor
**Specialists**: HeatTransfer, GasLaws, Entropy

#### PhysicsQuantumSupervisor
**Specialists**: WaveFunctions, Operators, Uncertainty

---

### 12. UnknownDomainSupervisor

**Domain**: Unclassified problems

**Role**: Handles problems that don't fit standard domains, attempts general-purpose solving strategies.

---

## Tier 3: Specialists (45+ Agents)

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

- **Routing Decision**: <1ms per supervisor
- **Specialist Execution**: 10ms-10s depending on complexity
- **Native vs SymPy**: 100-1000x slower but fully transparent
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
Last Updated: 2025-12-14
