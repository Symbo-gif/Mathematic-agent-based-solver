# Symbo Agentic Reasoners - Project Guidelines

## Core Philosophy: NO SYMPY

This project implements **100% native mathematical reasoning** without external symbolic math libraries.
All symbolic mathematics is pure Python - no SymPy, no SageMath, no external CAS dependencies.

---

## System Agent Inventory (127 BDI Agents)

### Summary Statistics

| Category | Count | Description |
|----------|-------|-------------|
| **Coordinators** | 1 | Multi-domain orchestration (Tier 1) |
| **Supervisors** | 20 | Domain routers (Tier 2) |
| **Specialists** | 91 | Computational experts (Tier 3) |
| **Base Agents** | 3 | Utility/analysis agents (Tier 1) |
| **Synthesis Agents** | 4 | Phase 6 formal verification |
| **Prover Agents** | 2 | Phase 6 proof verification |
| **System Agents** | 6 | Codebase management (BDI) |
| **TOTAL BDI** | **127** | All BDI agents |

---

### TIER 1: COORDINATORS (1 Multi-Domain Orchestrator)

| Coordinator | File | Purpose |
|-------------|------|---------|
| **MultiDomainTeamCoordinator** | `agents/coordinators/multi_domain_coordinator.py` | Orchestrates multiple supervisors for complex problems |

---

### TIER 2: SUPERVISORS (20 Domain Routers)

| Supervisor | File | Domain |
|------------|------|--------|
| AlgebraSupervisor | `agents/supervisors/algebra_supervisor.py` | Algebra |
| CalculusSupervisor | `agents/supervisors/calculus_supervisor.py` | Calculus |
| LinearAlgebraSupervisor | `agents/supervisors/linalg_supervisor.py` | Linear Algebra |
| StatisticsSupervisor | `agents/supervisors/stats_supervisor.py` | Statistics |
| DiscreteMathSupervisor | `agents/supervisors/discrete_math_supervisor.py` | Discrete Math |
| LogicSupervisor | `agents/supervisors/logic_supervisor.py` | Logic |
| GeometrySupervisor | `agents/supervisors/geometry_supervisor.py` | Geometry |
| PhysicsMechanicsSupervisor | `agents/supervisors/physics_mechanics_supervisor.py` | Physics-Mechanics |
| PhysicsEMSupervisor | `agents/supervisors/physics_em_supervisor.py` | Physics-EM |
| PhysicsThermoSupervisor | `agents/supervisors/physics_thermo_supervisor.py` | Physics-Thermo |
| PhysicsQuantumSupervisor | `agents/supervisors/physics_quantum_supervisor.py` | Physics-Quantum |
| ComplexAnalysisSupervisor | `agents/supervisors/complex_analysis_supervisor.py` | Complex Analysis |
| RealAnalysisSupervisor | `agents/supervisors/real_analysis_supervisor.py` | Real Analysis |
| FunctionalAnalysisSupervisor | `agents/supervisors/functional_analysis_supervisor.py` | Functional Analysis |
| DiffGeometrySupervisor | `agents/supervisors/diff_geometry_supervisor.py` | Differential Geometry |
| ControlTheorySupervisor | `agents/supervisors/control_theory_supervisor.py` | Control Theory |
| InformationTheorySupervisor | `agents/supervisors/information_theory_supervisor.py` | Information Theory |
| CryptographySupervisor | `agents/supervisors/cryptography_supervisor.py` | Cryptography |
| OptimizationSupervisor | `agents/supervisors/optimization_supervisor.py` | Optimization |
| **CategoryTheorySupervisor** | `agents/supervisors/category_theory_supervisor.py` | Category Theory |

---

### TIER 3: SPECIALISTS BY DOMAIN (91 Total)

#### Algebra Specialists (7)

| Specialist | File | Capabilities |
|------------|------|--------------|
| ArithmeticSpecialist | `algebra/arithmetic_specialist.py` | Arbitrary-precision arithmetic |
| PolynomialSpecialist | `algebra/polynomial_specialist.py` | Polynomial operations |
| EquationSystemSolver | `algebra/equation_system_solver.py` | System solving |
| NumberTheorySpecialist | `algebra/number_theory_specialist.py` | Primes, factorization |
| GroupRingTheoryAgent | `algebra/group_ring_theory.py` | Algebraic structures |

**Polynomial Sub-Specialists** (in `algebra/polynomial/`):
- PolynomialSpecialist (agent), polynomial_factors, polynomial_solvers
- domain_solver, numeric_roots, rational_equations
- polynomial_gcd - Euclidean GCD, Extended GCD, Resultants, Subresultant PRS

#### Calculus Specialists (8)

| Specialist | File | Capabilities |
|------------|------|--------------|
| DifferentiationSpecialist | `calculus/differentiation_specialist.py` | Derivatives, gradients |
| IntegrationSpecialist | `calculus/integration_specialist.py` | Integrals |
| LimitEvaluator | `calculus/limit_evaluator.py` | Limits, L'Hôpital |
| ODESolutionSpecialist | `calculus/ode_specialist.py` | ODEs (separable, linear) |
| ODESolver | `calculus/ode_solver.py` | Alternative ODE methods |
| SeriesSpecialist | `calculus/series_specialist.py` | Taylor/power series |
| FourierAnalysisSpecialist | `calculus/fourier_specialist.py` | FFT, convolution, filtering |
| SpecialFunctionsSpecialist | `calculus/special_functions_specialist.py` | Gamma, erf, Bessel, Elliptic, Zeta |

#### Linear Algebra Specialists (5)

| Specialist | File | Capabilities |
|------------|------|--------------|
| MatrixOperationsSpecialist | `linear_algebra/matrix_ops_specialist.py` | Matrix arithmetic |
| DecompositionSpecialist | `linear_algebra/decomposition_specialist.py` | LU, QR, SVD |
| VectorSpaceAnalyst | `linear_algebra/vector_space_analyst.py` | Bases, spans |
| TensorOperationsAgent | `linear_algebra/tensor_operations.py` | Tensor operations |
| AdvancedMatrixSpecialist | `linear_algebra/advanced_matrix_specialist.py` | Jordan form, matrix exp/log/sqrt |

#### Geometry Specialists (6)

| Specialist | File | Capabilities |
|------------|------|--------------|
| EuclideanGeometrySpecialist | `geometry/euclidean_specialist.py` | Points, lines, circles |
| AnalyticGeometrySpecialist | `geometry/analytic_specialist.py` | Coordinate geometry |
| TransformationSpecialist | `geometry/transformation_specialist.py` | Rotations, translations |
| TrigonometrySpecialist | `geometry/trigonometry_specialist.py` | Trig functions |
| ComputationalGeometrySpecialist | `geometry/computational_geometry_specialist.py` | Convex hull, triangulation |
| SolidGeometrySpecialist | `geometry/solid_geometry_specialist.py` | 3D geometry, volumes |

#### Discrete Math Specialists (6)

| Specialist | File | Capabilities |
|------------|------|--------------|
| CombinatoricsAgent | `discrete_math/combinatorics_agent.py` | Permutations, combinations, Stirling |
| GraphTheoryAgent | `discrete_math/graph_theory_agent.py` | Paths, connectivity, MST, SCC |
| SetTheoryAgent | `discrete_math/set_theory_agent.py` | Set operations, relations |
| RecurrenceRelationAgent | `discrete_math/recurrence_agent.py` | Solving recurrences |
| BooleanAlgebraAgent | `discrete_math/boolean_algebra_agent.py` | Quine-McCluskey, Karnaugh |
| FiniteAutomataAgent | `discrete_math/finite_automata_agent.py` | DFA, NFA, regex |

#### Logic Specialists (6)

| Specialist | File | Capabilities |
|------------|------|--------------|
| PropositionalLogicSpecialist | `logic/propositional_specialist.py` | Truth tables, SAT |
| PredicateLogicSpecialist | `logic/predicate_specialist.py` | Quantifiers, FOL |
| ProofSpecialist | `logic/proof_specialist.py` | Proof verification |
| ModalLogicSpecialist | `logic/modal_logic_specialist.py` | Kripke frames, K/T/S4/S5 |
| TemporalLogicSpecialist | `logic/temporal_logic_specialist.py` | LTL, CTL model checking |
| SATSolverSpecialist | `logic/sat_solver_specialist.py` | DPLL with CDCL, VSIDS |

#### Statistics Specialists (6)

| Specialist | File | Capabilities |
|------------|------|--------------|
| BayesianInferenceEngine | `statistics/bayesian_engine.py` | MCMC, posteriors |
| DistributionSpecialist | `statistics/distribution_specialist.py` | Probability distributions |
| FrequentistAgent | `statistics/frequentist_agent.py` | Hypothesis testing |
| StochasticProcessAnalyzer | `statistics/stochastic_process.py` | Markov chains |
| RegressionSpecialist | `statistics/regression_specialist.py` | Linear, polynomial, logistic |
| NonparametricSpecialist | `statistics/nonparametric_specialist.py` | Mann-Whitney, Wilcoxon |

#### Physics Specialists (12)

**Mechanics (3):** KinematicsSpecialist, DynamicsSpecialist, EnergySpecialist

**Electromagnetism (3):** ElectrostaticsSpecialist, MagnetismSpecialist, CircuitsSpecialist

**Thermodynamics (2):** HeatTransferSpecialist, GasLawsSpecialist

**Quantum (3):** WavefunctionSpecialist, OperatorsSpecialist, QuantumSystemsSpecialist

**Waves & Optics (1):** WaveOpticsSpecialist

#### Numerical Specialists (7)

| Specialist | File | Capabilities |
|------------|------|--------------|
| NumericalMethodsSpecialist | `numerical/numerical_methods_specialist.py` | Integration, ODE, roots |
| NumericalComputationUtility | `numerical/numerical_utility.py` | Floating-point |
| OptimizationSpecialist | `numerical/optimization_specialist.py` | BFGS, L-BFGS, Nelder-Mead |
| SplineSpecialist | `numerical/spline_specialist.py` | Cubic, Hermite, Akima |
| LinearSystemsSpecialist | `numerical/linear_systems_specialist.py` | Jacobi, Gauss-Seidel, GMRES |
| PDESpecialist | `numerical/pde_specialist.py` | Heat, wave, Laplace, Poisson |
| AdvancedQuadratureSpecialist | `numerical/advanced_quadrature_specialist.py` | Gauss-Hermite/Laguerre/Chebyshev |

#### Complex Analysis Specialists (4)

| Specialist | File | Capabilities |
|------------|------|--------------|
| AnalyticFunctionsSpecialist | `complex_analysis/analytic_functions_specialist.py` | Cauchy-Riemann, singularities |
| ResidueCalculusSpecialist | `complex_analysis/residue_calculus_specialist.py` | Residue computation, winding |
| ConformalMappingSpecialist | `complex_analysis/conformal_mapping_specialist.py` | Möbius, Schwarz-Christoffel |
| ContourIntegrationSpecialist | `complex_analysis/contour_integration_specialist.py` | Complex line integrals |

#### Real Analysis Specialists (3)

| Specialist | File | Capabilities |
|------------|------|--------------|
| MeasureTheorySpecialist | `real_analysis/measure_theory_specialist.py` | Lebesgue measure/integration |
| MetricSpaceSpecialist | `real_analysis/metric_space_specialist.py` | Completeness, Lipschitz |
| SequencesSeriesSpecialist | `real_analysis/sequences_series_specialist.py` | Convergence tests |

#### Functional Analysis Specialists (3)

| Specialist | File | Capabilities |
|------------|------|--------------|
| BanachSpaceSpecialist | `functional_analysis/banach_space_specialist.py` | Norm verification, dual spaces |
| HilbertSpaceSpecialist | `functional_analysis/hilbert_space_specialist.py` | Inner products, Gram-Schmidt |
| OperatorTheorySpecialist | `functional_analysis/operator_theory_specialist.py` | Spectrum, resolvent |

#### Differential Geometry & Topology Specialists (2)

| Specialist | File | Capabilities |
|------------|------|--------------|
| DifferentialGeometrySpecialist | `diff_geometry/differential_geometry_specialist.py` | Metrics, Christoffel, geodesics |
| TopologySpecialist | `diff_geometry/topology_specialist.py` | Simplicial complexes, homology |

#### Control Theory Specialists (2)

| Specialist | File | Capabilities |
|------------|------|--------------|
| DynamicalSystemsSpecialist | `control_theory/dynamical_systems_specialist.py` | Fixed points, Lyapunov |
| LinearControlSpecialist | `control_theory/linear_control_specialist.py` | State-space, LQR |

#### Information Theory Specialists (3)

| Specialist | File | Capabilities |
|------------|------|--------------|
| EntropySpecialist | `information_theory/entropy_specialist.py` | Shannon, KL divergence, mutual info |
| CodingTheorySpecialist | `information_theory/coding_theory_specialist.py` | Huffman, Hamming codes |
| ChannelCapacitySpecialist | `information_theory/channel_capacity_specialist.py` | BSC, BEC, AWGN, Blahut-Arimoto |

#### Cryptography Specialists (3)

| Specialist | File | Capabilities |
|------------|------|--------------|
| ModularArithmeticSpecialist | `cryptography/modular_arithmetic_specialist.py` | Mod exp, CRT, Miller-Rabin |
| AsymmetricCryptoSpecialist | `cryptography/asymmetric_crypto_specialist.py` | RSA, Diffie-Hellman, ElGamal |
| HashSpecialist | `cryptography/hash_specialist.py` | DJB2, Merkle trees, birthday |

#### Optimization Specialists (3)

| Specialist | File | Capabilities |
|------------|------|--------------|
| LinearProgrammingSpecialist | `optimization/linear_programming_specialist.py` | Simplex, two-phase, sensitivity |
| ConvexOptimizationSpecialist | `optimization/convex_optimization_specialist.py` | Gradient descent, Newton, QP |
| CombinatorialOptimizationSpecialist | `optimization/combinatorial_specialist.py` | Knapsack, TSP, assignment |

#### Category Theory Specialists (3)

| Specialist | File | Capabilities |
|------------|------|--------------|
| MorphismSpecialist | `category_theory/morphism_specialist.py` | Categories, morphisms, composition, classification |
| FunctorSpecialist | `category_theory/functor_specialist.py` | Functors, natural transformations, hom-functors |
| UniversalPropertiesSpecialist | `category_theory/universal_properties_specialist.py` | Products, coproducts, limits, colimits |

---

### PHASE 6 AGENTS (6 Total)

#### Synthesis Agents (4)

| Agent | File | Purpose |
|-------|------|---------|
| StructuralSynthesizer | `synthesis/structural_synthesizer.py` | Build structures from axioms |
| ProofTermConstructor | `synthesis/proof_term_constructor.py` | Construct proof terms |
| ConjectureGenerator | `synthesis/conjecture_generator.py` | Generate conjectures |
| FormalLanguageTranslator | `synthesis/formal_translator.py` | Translate formal notations |

#### Prover Agents (2)

| Agent | File | Purpose |
|-------|------|---------|
| LogicalProver | `provers/logical_prover.py` | Resolution, natural deduction |
| ModelChecker | `provers/model_checker.py` | State space exploration |

---

### SYSTEM AGENTS (11 in `src/system_agents/`)

| Agent | File | BDI? | Purpose |
|-------|------|------|---------|
| AlgorithmBuildingExpert | `algorithm_building_expert.py` | Yes | Algorithm construction |
| AlgorithmBreakingAgent | `algorithm_breaking_agent.py` | Yes | Adversarial testing |
| CrackFinderAgent | `crackfinder_agent.py` | Yes | Vulnerability scanning |
| SecurityStressTester | `security_stress_tester.py` | Yes | Security testing |
| AuditAgent | `audit_agent.py` | No | System integrity |
| CleanupAgent | `cleanup_agent.py` | No | Temp file management |
| CodeChunkingAgent | `code_chunking_agent.py` | No | Code splitting |
| DocumentationAgent | `documentation_agent.py` | No | Doc generation |
| MathematicalCrackfinder | `mathematical_cracker.py` | No | Adversarial cases |
| ScriptDecomposer | `script_decomposer.py` | No | Script decomposition |
| StructureCataloger | `structure_cataloger.py` | No | Codebase cataloging |

---

### BASE AGENTS (3 in `agents/base/`)

| Agent | File | Purpose |
|-------|------|---------|
| NotationTranslatorAgent | `notation_translator.py` | LaTeX ↔ SymPy ↔ NL |
| SyntaxParserAgent | `problem_analysis.py` | Expression parsing |
| StructureRecognizerAgent | `problem_analysis.py` | Problem type detection |

---

## Project Structure

```
Mathematic agent based solver/
├── src/                          # Source code (main package)
│   └── symbo_agentic_reasoners/
│       ├── agents/               # BDI agents organized by role
│       │   ├── base/             # Base agent classes (3)
│       │   ├── coordinators/     # Multi-domain coordinators (1)
│       │   ├── supervisors/      # Domain supervisors (20)
│       │   ├── specialists/      # Domain specialists (91)
│       │   ├── provers/          # Proof agents (2)
│       │   └── synthesis/        # Synthesis agents (4)
│       ├── core/                 # Core infrastructure
│       │   ├── calculus/         # Calculus subsystem
│       │   ├── solver/           # Solver engine
│       │   ├── symbolic/         # Native symbolic math (NO SYMPY)
│       │   └── input_normalization/
│       ├── infrastructure/       # System infrastructure
│       └── ...
│   └── system_agents/            # System management agents (11)
├── tests/                        # Test files
├── scripts/                      # Utility scripts
├── main.py                       # Entry point
├── pyproject.toml               # Project configuration
└── config.yaml                  # Runtime configuration
```

---

## Architecture: Supervisor-Specialist Pattern

### Tier Hierarchy

```
Tier 1: Coordinators (1)     - Multi-domain orchestration
Tier 1: Base Agents (3)      - Utility/analysis
Tier 2: Supervisors (20)     - Domain routing (never compute)
Tier 3: Specialists (91)     - Domain computation
Phase 6: Provers (2) + Synthesis (4) - Formal verification
System: Management (11)      - Codebase operations (6 BDI)
```

### Infrastructure (Phase 0)
- **AMS**: Agent Management System
- **DF**: Directory Facilitator (service registry)
- **ACC**: Agent Communication Channel
- **Blackboard**: Shared memory

---

## Key Guidelines

1. **No SymPy**: All symbolic math uses native implementations in `core/symbolic/`
2. **Lazy Loading**: Supervisors use lazy imports to avoid circular dependencies
3. **Service Registration**: Specialists must register with DF to be discoverable
4. **Thin Wrappers**: Decomposed modules export through backward-compatible wrappers
5. **Test Coverage**: Maintain tests in `tests/` for all new functionality
6. **BDI Pattern**: All agents implement update_beliefs(), deliberate(), execute_step()

---

## When Adding New Agents

1. **New specialist?** → `src/symbo_agentic_reasoners/agents/specialists/<domain>/`
2. **New supervisor?** → `src/symbo_agentic_reasoners/agents/supervisors/`
3. **New system agent?** → `src/system_agents/`
4. **Update inventory** → Add to this CLAUDE.md file

---

## Mathematical Domain Coverage (20 Domains)

| Domain | Supervisor | Specialists | Coverage |
|--------|------------|-------------|----------|
| Algebra | Yes | 7 | 92% |
| Calculus | Yes | 8 | 92% |
| Linear Algebra | Yes | 5 | 92% |
| Statistics | Yes | 6 | 92% |
| Geometry | Yes | 6 | 90% |
| Physics | Yes (4) | 12 | 90% |
| Logic | Yes | 6 | 92% |
| Discrete Math | Yes | 6 | 90% |
| Numerical | Yes | 7 | 92% |
| Complex Analysis | Yes | 4 | 85% |
| Real Analysis | Yes | 3 | 85% |
| Functional Analysis | Yes | 3 | 85% |
| Diff. Geometry | Yes | 2 | 80% |
| Control Theory | Yes | 2 | 85% |
| Information Theory | Yes | 3 | 90% |
| Cryptography | Yes | 3 | 85% |
| Optimization | Yes | 3 | 90% |
| **Category Theory** | Yes | 3 | 90% |

### Multi-Domain Coordination

The **MultiDomainTeamCoordinator** orchestrates problems spanning multiple domains:
- Automatic domain detection via keyword analysis
- Task decomposition into domain-specific subtasks
- Dependency-aware execution scheduling
- Result synthesis from multiple domains

---

**Last Updated**: December 17, 2025
**Total BDI Agents**: 127
**Total Agent Classes**: 133 (including non-BDI utilities)
**Test Count**: 4,700+ passing
