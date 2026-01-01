#!/usr/bin/env python3
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
Specialist Test Generator
=========================

Generates comprehensive test files for specialist agents from template.

Phase 6 - Week 1: Automates creation of 40+ specialist test suites.

Usage:
    python scripts/generate_specialist_tests.py --all
    python scripts/generate_specialist_tests.py --domain algebra
    python scripts/generate_specialist_tests.py --specialist ArithmeticSpecialist
"""

import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# Specialist definitions: (class_name, domain, module_path, service_type, simple_problem, complex_problem)
SPECIALISTS = [
    # Algebra (7)
    ('ArithmeticSpecialist', 'algebra', 'algebra.arithmetic_specialist', 'math.algebra.arithmetic',
     '2 + 2', '((12 * 5) + (8 / 2)) - 3'),
    ('PolynomialSpecialist', 'algebra', 'algebra.polynomial_specialist', 'math.algebra.polynomial',
     'x^2 + 2*x + 1', 'x^4 - 5*x^3 + 6*x^2 + 4*x - 8'),
    ('EquationSystemSolver', 'algebra', 'algebra.equation_system_solver', 'math.algebra.systems',
     'x + y = 5, x - y = 1', '2*x + 3*y + z = 10, x - y + 2*z = 5, 3*x + y - z = 8'),
    ('NumberTheorySpecialist', 'algebra', 'algebra.number_theory_specialist', 'math.algebra.numbertheory',
     'gcd(12, 8)', 'prime factorization of 1234567'),
    ('GroupRingTheoryAgent', 'algebra', 'algebra.group_ring_theory', 'math.algebra.structures',
     'Is Z_5 a group?', 'Find all subgroups of S_3'),

    # Calculus (8)
    ('DifferentiationSpecialist', 'calculus', 'calculus.differentiation_specialist', 'math.calculus.differentiation',
     'diff(x^2, x)', 'diff(x^3 * sin(x) * e^x, x)'),
    ('IntegrationSpecialist', 'calculus', 'calculus.integration_specialist', 'math.calculus.integration',
     'integrate(x^2, x)', 'integrate(x^2 * sin(x) * e^x, x)'),
    ('LimitEvaluator', 'calculus', 'calculus.limit_evaluator', 'math.calculus.limits',
     'limit(x^2, x, 0)', 'limit(sin(x)/x, x, 0)'),
    ('ODESolutionSpecialist', 'calculus', 'calculus.ode_specialist', 'math.calculus.ode',
     "dy/dx = y", "d²y/dx² + 4*dy/dx + 4*y = 0"),
    ('ODESolver', 'calculus', 'calculus.ode_solver', 'math.calculus.ode.solver',
     "solve dy/dx = x", "solve system of ODEs"),
    ('ODESystemsSpecialist', 'calculus', 'calculus.ode_systems_specialist', 'math.calculus.ode.systems',
     "solve dY/dt = AY with A=[[0,1],[-1,0]]", "phase plane analysis and stability"),
    ('SeriesSpecialist', 'calculus', 'calculus.series_specialist', 'math.calculus.series',
     'Taylor series of e^x', 'Laurent series of 1/(z*(z-1))'),
    ('FourierAnalysisSpecialist', 'calculus', 'calculus.fourier_specialist', 'math.calculus.fourier',
     'Fourier transform of exp(-x^2)', 'FFT of [1, 2, 3, 4]'),
    ('SpecialFunctionsSpecialist', 'calculus', 'calculus.special_functions_specialist', 'math.calculus.special',
     'gamma(5)', 'bessel_j(0, 1.5)'),

    # Linear Algebra (5)
    ('MatrixOperationsSpecialist', 'linear_algebra', 'linear_algebra.matrix_ops_specialist', 'math.linalg.operations',
     '[[1,2],[3,4]] * [[5,6],[7,8]]', 'matrix_power([[1,2],[3,4]], 10)'),
    ('DecompositionSpecialist', 'linear_algebra', 'linear_algebra.decomposition_specialist', 'math.linalg.decomposition',
     'LU([[1,2],[3,4]])', 'SVD([[1,2,3],[4,5,6],[7,8,9]])'),
    ('VectorSpaceAnalyst', 'linear_algebra', 'linear_algebra.vector_space_analyst', 'math.linalg.vectorspace',
     'basis of span([1,0], [0,1])', 'orthogonal basis of [[1,1],[1,2]]'),
    ('TensorOperationsAgent', 'linear_algebra', 'linear_algebra.tensor_operations', 'math.linalg.tensor',
     'tensor product of [1,2] and [3,4]', 'tensor contraction over indices'),
    ('AdvancedMatrixSpecialist', 'linear_algebra', 'linear_algebra.advanced_matrix_specialist', 'math.linalg.advanced',
     'Jordan canonical form', 'matrix exponential exp(A)'),

    # Geometry (6)
    ('EuclideanGeometrySpecialist', 'geometry', 'geometry.euclidean_specialist', 'math.geometry.euclidean',
     'distance from (0,0) to (3,4)', 'circle through points (0,0), (1,0), (0,1)'),
    ('AnalyticGeometrySpecialist', 'geometry', 'geometry.analytic_specialist', 'math.geometry.analytic',
     'line through two points', 'parabola equation from focus and directrix'),
    ('TransformationSpecialist', 'geometry', 'geometry.transformation_specialist', 'math.geometry.transformation',
     'rotate point 90 degrees', 'composition of transformations'),
    ('ComputationalGeometrySpecialist', 'geometry', 'geometry.computational_geometry_specialist', 'math.geometry.computational',
     'convex hull of points', 'Delaunay triangulation'),
    ('SolidGeometrySpecialist', 'geometry', 'geometry.solid_geometry_specialist', 'math.geometry.solid',
     'volume of sphere', 'surface area of irregular polyhedron'),
    ('TrigonometrySpecialist', 'geometry', 'geometry.trigonometry_specialist', 'math.geometry.trig',
     'sin(30 degrees)', 'solve sin(x) = 0.5 for 0 <= x <= 2*pi'),

    # Logic (6)
    ('PropositionalLogicSpecialist', 'logic', 'logic.propositional_specialist', 'math.logic.propositional',
     'A AND B', '(A OR B) AND (NOT A OR C)'),
    ('PredicateLogicSpecialist', 'logic', 'logic.predicate_specialist', 'math.logic.predicate',
     'forall x. P(x)', 'exists x. forall y. (P(x) -> Q(x,y))'),
    ('ModalLogicSpecialist', 'logic', 'logic.modal_logic_specialist', 'math.logic.modal',
     'necessarily P', 'possibly (P and Q)'),
    ('TemporalLogicSpecialist', 'logic', 'logic.temporal_logic_specialist', 'math.logic.temporal',
     'always P', 'eventually (P until Q)'),
    ('ProofSpecialist', 'logic', 'logic.proof_specialist', 'math.logic.proof',
     'prove P implies P', 'prove by induction n(n+1)/2'),
    ('SATSolverSpecialist', 'logic', 'logic.sat_solver_specialist', 'math.logic.sat',
     '(A OR B) AND (NOT A OR NOT B)', 'complex CNF formula'),

    # Statistics (6)
    ('DistributionSpecialist', 'statistics', 'statistics.distribution_specialist', 'math.stats.distributions',
     'normal(mu=0, sigma=1)', 'binomial(n=10, p=0.5)'),
    ('RegressionSpecialist', 'statistics', 'statistics.regression_specialist', 'math.stats.regression',
     'linear regression: y = mx + b', 'polynomial regression degree 3'),
    ('FrequentistAgent', 'statistics', 'statistics.frequentist_agent', 'math.stats.frequentist',
     't-test for means', 'chi-square independence test'),
    ('BayesianInferenceEngine', 'statistics', 'statistics.bayesian_engine', 'math.stats.bayesian',
     'posterior from prior and likelihood', 'MCMC sampling'),
    ('StochasticProcessAnalyzer', 'statistics', 'statistics.stochastic_process', 'math.stats.stochastic',
     'Markov chain transition', 'random walk analysis'),
    ('NonparametricSpecialist', 'statistics', 'statistics.nonparametric_specialist', 'math.stats.nonparametric',
     'Mann-Whitney U test', 'Wilcoxon signed-rank test'),

    # Physics (4)
    ('KinematicsSpecialist', 'physics', 'physics.mechanics.kinematics_specialist', 'math.physics.kinematics',
     'velocity from position x = t^2', 'acceleration of projectile'),
    ('DynamicsSpecialist', 'physics', 'physics.mechanics.dynamics_specialist', 'math.physics.dynamics',
     'F = ma with F=10, m=2', 'net force on object with multiple forces'),

    # Discrete Math (6)
    ('CombinatoricsAgent', 'discrete_math', 'discrete_math.combinatorics_agent', 'math.discrete.combinatorics',
     '5!', 'C(10, 3) - combinations'),
    ('GraphTheoryAgent', 'discrete_math', 'discrete_math.graph_theory_agent', 'math.discrete.graphs',
     'shortest path in graph', 'minimum spanning tree'),
    ('SetTheoryAgent', 'discrete_math', 'discrete_math.set_theory_agent', 'math.discrete.sets',
     'union of {1,2,3} and {2,3,4}', 'power set of {a,b,c}'),
    ('RecurrenceRelationAgent', 'discrete_math', 'discrete_math.recurrence_agent', 'math.discrete.recurrence',
     'solve a_n = a_{n-1} + 1', 'solve Fibonacci recurrence'),
    ('BooleanAlgebraAgent', 'discrete_math', 'discrete_math.boolean_algebra_agent', 'math.discrete.boolean',
     'simplify A AND (A OR B)', 'Quine-McCluskey minimization'),
    ('FiniteAutomataAgent', 'discrete_math', 'discrete_math.finite_automata_agent', 'math.discrete.automata',
     'DFA for (01)*', 'NFA to DFA conversion'),

    # Complex Analysis (5)
    ('AnalyticFunctionsSpecialist', 'complex_analysis', 'complex_analysis.analytic_functions_specialist', 'math.complex.analytic',
     'is f(z)=z^2 analytic?', 'Hadamard factorization and order/type'),
    ('ResidueCalculusSpecialist', 'complex_analysis', 'complex_analysis.residue_calculus_specialist', 'math.complex.residue',
     'residue of 1/z at z=0', 'contour integral using residue theorem'),
    ('ConformalMappingSpecialist', 'complex_analysis', 'complex_analysis.conformal_mapping_specialist', 'math.complex.conformal',
     'Mobius transformation w=1/z', 'Schwarz-Christoffel mapping'),
    ('ContourIntegrationSpecialist', 'complex_analysis', 'complex_analysis.contour_integration_specialist', 'math.complex.contour',
     'integrate f(z) around unit circle', 'evaluate real integral using contour'),
    ('EllipticFunctionsSpecialist', 'complex_analysis', 'complex_analysis.elliptic_functions_specialist', 'math.complex.elliptic',
     'Weierstrass p-function', 'elliptic integral of first kind'),

    # Real Analysis (4)
    ('MeasureTheorySpecialist', 'real_analysis', 'real_analysis.measure_theory_specialist', 'math.real.measure',
     'Lebesgue measure of [0,1]', 'dominated convergence theorem'),
    ('MetricSpaceSpecialist', 'real_analysis', 'real_analysis.metric_space_specialist', 'math.real.metric',
     'is R with d(x,y)=|x-y| complete?', 'Lipschitz continuity'),
    ('SequencesSeriesSpecialist', 'real_analysis', 'real_analysis.sequences_series_specialist', 'math.real.sequences',
     'does 1/n converge?', 'Stone-Weierstrass approximation'),
    ('FunctionSpacesSpecialist', 'real_analysis', 'real_analysis.function_spaces_specialist', 'math.real.function_spaces',
     'compute L2 norm', 'verify Hölder inequality'),

    # Numerical (7)
    ('NumericalMethodsSpecialist', 'numerical', 'numerical.numerical_methods_specialist', 'math.numerical.methods',
     'Newton-Raphson for x^2-2=0', 'numerical integration of sin(x)'),
    ('OptimizationSpecialist', 'numerical', 'numerical.optimization_specialist', 'math.numerical.optimization',
     'minimize f(x)=x^2-4x+3', 'BFGS optimization'),
    ('SplineSpecialist', 'numerical', 'numerical.spline_specialist', 'math.numerical.spline',
     'cubic spline through 3 points', 'Hermite interpolation'),
    ('LinearSystemsSpecialist', 'numerical', 'numerical.linear_systems_specialist', 'math.numerical.linear',
     'solve Ax=b with Jacobi', 'GMRES iterative solver'),
    ('PDESpecialist', 'numerical', 'numerical.pde_specialist', 'math.numerical.pde',
     'heat equation 1D', 'Laplace equation 2D'),
    ('AdvancedQuadratureSpecialist', 'numerical', 'numerical.advanced_quadrature_specialist', 'math.numerical.quadrature',
     'Gauss-Legendre quadrature', 'adaptive Simpson integration'),
    ('NumericalComputationUtility', 'numerical', 'numerical.numerical_utility', 'math.numerical.utility',
     'evaluate expression numerically', 'floating point error analysis'),

    # Cryptography (3)
    ('ModularArithmeticSpecialist', 'cryptography', 'cryptography.modular_arithmetic_specialist', 'math.crypto.modular',
     '7 mod 3', 'modular exponentiation 2^100 mod 13'),
    ('AsymmetricCryptoSpecialist', 'cryptography', 'cryptography.asymmetric_crypto_specialist', 'math.crypto.asymmetric',
     'RSA key generation', 'Diffie-Hellman key exchange'),
    ('HashSpecialist', 'cryptography', 'cryptography.hash_specialist', 'math.crypto.hash',
     'DJB2 hash of string', 'Merkle tree construction'),

    # Optimization (3)
    ('LinearProgrammingSpecialist', 'optimization', 'optimization.linear_programming_specialist', 'math.optimization.linear',
     'simplex method', 'two-phase simplex with constraints'),
    ('ConvexOptimizationSpecialist', 'optimization', 'optimization.convex_optimization_specialist', 'math.optimization.convex',
     'gradient descent', 'Newton method for convex function'),
    ('CombinatorialOptimizationSpecialist', 'optimization', 'optimization.combinatorial_specialist', 'math.optimization.combinatorial',
     'knapsack problem', 'traveling salesman heuristic'),

    # Information Theory (3)
    ('EntropySpecialist', 'information_theory', 'information_theory.entropy_specialist', 'math.info.entropy',
     'Shannon entropy of [0.5, 0.5]', 'KL divergence between distributions'),
    ('CodingTheorySpecialist', 'information_theory', 'information_theory.coding_theory_specialist', 'math.info.coding',
     'Huffman encoding', 'Hamming code construction'),
    ('ChannelCapacitySpecialist', 'information_theory', 'information_theory.channel_capacity_specialist', 'math.info.channel',
     'BSC capacity', 'AWGN channel capacity'),

    # Category Theory (5)
    ('MorphismSpecialist', 'category_theory', 'category_theory.morphism_specialist', 'math.category.morphism',
     'compose morphisms f and g', 'verify morphism properties'),
    ('FunctorSpecialist', 'category_theory', 'category_theory.functor_specialist', 'math.category.functor',
     'define functor F: C → D', 'Yoneda lemma application'),
    ('UniversalPropertiesSpecialist', 'category_theory', 'category_theory.universal_properties_specialist', 'math.category.universal',
     'product in category', 'coproduct and limits'),
    ('AdjunctionSpecialist', 'category_theory', 'category_theory.adjunction_specialist', 'math.category.adjunction',
     'Free ⊣ Forgetful adjunction', 'verify triangle identities'),
    ('MonoidalSpecialist', 'category_theory', 'category_theory.monoidal_specialist', 'math.category.monoidal',
     'tensor product ⊗ in category', 'verify pentagon axiom'),

    # Functional Analysis (3)
    ('BanachSpaceSpecialist', 'functional_analysis', 'functional_analysis.banach_space_specialist', 'math.functional.banach',
     'verify norm axioms', 'dual space of l^p'),
    ('HilbertSpaceSpecialist', 'functional_analysis', 'functional_analysis.hilbert_space_specialist', 'math.functional.hilbert',
     'inner product <u,v>', 'Gram-Schmidt orthogonalization'),
    ('OperatorTheorySpecialist', 'functional_analysis', 'functional_analysis.operator_theory_specialist', 'math.functional.operator',
     'spectrum of operator', 'resolvent of T'),

    # Additional Physics (10)
    ('EnergySpecialist', 'physics', 'physics.mechanics.energy_specialist', 'math.physics.energy',
     'kinetic energy KE=0.5*m*v^2', 'conservation of energy'),
    ('ElectrostaticsSpecialist', 'physics', 'physics.em.electrostatics_specialist', 'math.physics.electrostatics',
     'Coulomb force F=kq1q2/r^2', 'electric field of point charge'),
    ('MagnetismSpecialist', 'physics', 'physics.em.magnetism_specialist', 'math.physics.magnetism',
     'Lorentz force F=qvB', 'magnetic field of current loop'),
    ('CircuitsSpecialist', 'physics', 'physics.em.circuits_specialist', 'math.physics.circuits',
     'Ohm law V=IR', 'RLC circuit analysis'),
    ('HeatTransferSpecialist', 'physics', 'physics.thermo.heat_transfer_specialist', 'math.physics.heat',
     'Q = mcΔT', 'heat conduction Fourier law'),
    ('GasLawsSpecialist', 'physics', 'physics.thermo.gas_laws_specialist', 'math.physics.gas',
     'ideal gas PV=nRT', 'van der Waals equation'),
    ('WavefunctionSpecialist', 'physics', 'physics.quantum.wavefunction_specialist', 'math.physics.wavefunction',
     'normalize wavefunction', 'expectation value <x>'),
    ('OperatorsSpecialist', 'physics', 'physics.quantum.operators_specialist', 'math.physics.operators',
     'momentum operator', 'commutator [X,P]'),
    ('QuantumSystemsSpecialist', 'physics', 'physics.quantum.quantum_systems_specialist', 'math.physics.quantum',
     'particle in box', 'harmonic oscillator eigenvalues'),
    ('WaveOpticsSpecialist', 'physics', 'physics.waves.wave_optics_specialist', 'math.physics.waves',
     'double slit interference', 'diffraction grating'),

    # Phase 1 - Stochastic Processes (5)
    ('BrownianMotionSpecialist', 'stochastic', 'stochastic.brownian_motion', 'math.stochastic.brownian',
     'Compute E[W(1)^2] for standard Wiener process', 'First passage time for BM with drift mu=0.5'),
    ('SDESolverSpecialist', 'stochastic', 'stochastic.sde_solver', 'math.stochastic.sde',
     'Solve dX = 0.1*X dt + 0.2*X dW with Euler-Maruyama', 'GBM with mu=0.05, sigma=0.2 using exact solution'),
    ('LevyProcessSpecialist', 'stochastic', 'stochastic.levy_processes', 'math.stochastic.levy',
     'Generate compound Poisson with rate 2.0', 'Levy process with jumps N(0,1)'),
    ('MartingaleTheorySpecialist', 'stochastic', 'stochastic.martingale_theory', 'math.stochastic.martingale',
     'Verify Brownian motion is a martingale', 'Compute stopping time to barrier 1.5'),
    ('StochasticCalculusSpecialist', 'stochastic', 'stochastic.stochastic_calculus', 'math.stochastic.calculus',
     'Apply Ito lemma to f(x)=x^2', 'Girsanov theorem with drift change 0.1'),

    # Phase 1 - Analytic Number Theory (4)
    ('ZetaFunctionSpecialist', 'analytic_number_theory', 'algebra.number_theory.analytic.zeta_functions',
     'math.algebra.numbertheory.analytic.zeta', 'Compute zeta(2)', 'Evaluate zeta(3) numerically'),
    ('PrimeDistributionSpecialist', 'analytic_number_theory', 'algebra.number_theory.analytic.prime_distribution',
     'math.algebra.numbertheory.analytic.primes', 'Count primes up to 100', 'Prime number theorem approximation for x=10000'),
    ('ArithmeticFunctionsSpecialist', 'analytic_number_theory', 'algebra.number_theory.analytic.arithmetic_functions',
     'math.algebra.numbertheory.analytic.functions', 'Compute phi(12)', 'Mobius function mu(30)'),
    ('AnalyticContinuationSpecialist', 'analytic_number_theory', 'algebra.number_theory.analytic.analytic_continuation',
     'math.algebra.numbertheory.analytic.continuation', 'Functional equation for zeta', 'Analytic continuation to s=0.5'),

    # Phase 1 - Algebraic Number Theory (4)
    ('NumberFieldsSpecialist', 'algebraic_number_theory', 'algebra.number_theory.algebraic.number_fields',
     'math.algebra.numbertheory.algebraic.fields', 'Quadratic field Q(sqrt(-1))', 'Discriminant of number field Q(sqrt(-5))'),
    ('IdealTheorySpecialist', 'algebraic_number_theory', 'algebra.number_theory.algebraic.ideal_theory',
     'math.algebra.numbertheory.algebraic.ideals', 'Ideal class group of Q(sqrt(-5))', 'Unique factorization in Z[i]'),
    ('LocalFieldsSpecialist', 'algebraic_number_theory', 'algebra.number_theory.algebraic.local_fields',
     'math.algebra.numbertheory.algebraic.local', 'p-adic valuation v_2(16)', '2-adic expansion of 1/3'),
    ('ClassFieldTheorySpecialist', 'algebraic_number_theory', 'algebra.number_theory.algebraic.class_field_theory',
     'math.algebra.numbertheory.algebraic.classfield', 'Artin reciprocity law', 'Abelian extension of Q'),

    # Phase 1 - Spectral Graph Theory (5)
    ('LaplacianSpectrumSpecialist', 'spectral_graph', 'discrete_math.spectral_graphs.laplacian_spectrum',
     'math.discrete.graphs.spectral.laplacian', 'Laplacian eigenvalues of cycle C_5', 'Fiedler value of path graph P_10'),
    ('AdjacencySpectrumSpecialist', 'spectral_graph', 'discrete_math.spectral_graphs.adjacency_spectrum',
     'math.discrete.graphs.spectral.adjacency', 'Adjacency spectrum of K_5', 'Spectral radius of Petersen graph'),
    ('CheegerInequalitySpecialist', 'spectral_graph', 'discrete_math.spectral_graphs.cheeger_inequality',
     'math.discrete.graphs.spectral.cheeger', 'Cheeger bound for Fiedler=0.5', 'Graph conductance lower bound'),
    ('RandomWalkSpecialist', 'spectral_graph', 'discrete_math.spectral_graphs.random_walks',
     'math.discrete.graphs.spectral.randomwalk', 'Stationary distribution on K_4', 'Mixing time for cycle graph'),
    ('SpectralClusteringSpecialist', 'spectral_graph', 'discrete_math.spectral_graphs.spectral_clustering',
     'math.discrete.graphs.spectral.clustering', 'Cluster graph into 2 parts', 'Normalized cut for k=3 clusters'),

    # Phase 1 - Model Theory (4)
    ('CompactnessSpecialist', 'model_theory', 'model_theory.compactness',
     'math.modeltheory.compactness', 'Apply compactness theorem', 'Ultraproduct construction'),
    ('CategoricitySpecialist', 'model_theory', 'model_theory.categoricity',
     'math.modeltheory.categoricity', 'Is DLO omega-categorical?', 'Categoricity spectrum of theory'),
    ('QuantifierEliminationSpecialist', 'model_theory', 'model_theory.quantifier_elimination',
     'math.modeltheory.qe', 'QE for ACF', 'Eliminate quantifiers in exists x. x^2+1=0'),
    ('OMinimalitySpecialist', 'model_theory', 'model_theory.ominimality',
     'math.modeltheory.ominimal', 'Is R_exp o-minimal?', 'Cell decomposition in R_an'),

    # Phase 1 - Proof Theory (5)
    ('CutEliminationSpecialist', 'proof_theory', 'proof_theory.cut_elimination',
     'math.prooftheory.cutelimination', 'Cut elimination for sequent proof', 'Gentzen Hauptsatz application'),
    ('OrdinalAnalysisSpecialist', 'proof_theory', 'proof_theory.ordinal_analysis',
     'math.prooftheory.ordinals', 'Proof-theoretic ordinal of PA', 'Ordinal epsilon_0 for first-order arithmetic'),
    ('TypeTheorySpecialist', 'proof_theory', 'proof_theory.type_theory',
     'math.prooftheory.types', 'Type check lambda x. x', 'Dependent type for vectors'),
    ('CurryHowardSpecialist', 'proof_theory', 'proof_theory.curry_howard',
     'math.prooftheory.curryhoward', 'Curry-Howard for A->B', 'Proof term for conjunction'),
    ('ConstructiveMathSpecialist', 'proof_theory', 'proof_theory.constructive_math',
     'math.prooftheory.constructive', 'Is LEM constructively valid?', 'Constructive proof of intermediate value theorem'),

    # Phase 2 - Computability Theory (5)
    ('TuringCompletenessSpecialist', 'computability', 'computability.turing_completeness',
     'math.computability.turing', 'Simulate simple TM', 'Verify Python is Turing-complete'),
    ('RecursionTheorySpecialist', 'computability', 'computability.recursion_theory',
     'math.computability.recursion_theory', 'Compute factorial via primitive recursion', 'Ackermann A(3,3)'),
    ('TuringDegreesSpecialist', 'computability', 'computability.turing_degrees',
     'math.computability.turing_degrees', "Compute 0' jump", "Analyze Post's problem"),
    ('ComplexityTheorySpecialist', 'computability', 'computability.complexity_theory',
     'math.computability.complexity_theory', 'Analyze time complexity of bubble sort', 'Classify SAT problem'),
    ('KolmogorovComplexitySpecialist', 'computability', 'computability.kolmogorov_complexity',
     'math.computability.kolmogorov_complexity', 'Estimate K(x) for repeated string', 'Verify randomness of string'),

    # Phase 2 - Riemannian Geometry (5)
    ('MetricTensorSpecialist', 'riemannian', 'riemannian.metric',
     'math.riemannian.metric', 'Verify Euclidean metric signature', 'Check isometry for rotation'),
    ('CurvatureSpecialist', 'riemannian', 'riemannian.curvature',
     'math.riemannian.curvature', 'Compute scalar curvature of flat space', 'Riemann tensor for sphere'),
    ('GeodesicSpecialist', 'riemannian', 'riemannian.geodesic',
     'math.riemannian.geodesic', 'Solve geodesic on Euclidean space', 'Compute exponential map on sphere'),
    ('ComparisonTheoremsSpecialist', 'riemannian', 'riemannian.comparison',
     'math.riemannian.comparison', 'Apply Rauch comparison', 'Verify Myers theorem for positive Ricci'),
    ('HolonomySpecialist', 'riemannian', 'riemannian.holonomy',
     'math.riemannian.holonomy', 'Parallel transport along circle', 'Classify holonomy of Kahler manifold'),

    # Phase 2 - Bayesian Decision Theory (3)
    ('UtilityTheorySpecialist', 'bayesian_decision', 'statistics.bayesian_decision.utility_theory',
     'math.statistics.bayesian_decision.utility_theory', 'Compute expected utility', 'Measure risk aversion with log utility'),
    ('DecisionRulesSpecialist', 'bayesian_decision', 'statistics.bayesian_decision.decision_rules',
     'math.statistics.bayesian_decision.decision_rules', 'Compute Bayes risk', 'Find minimax rule for 2x2 game'),
    ('SequentialDecisionSpecialist', 'bayesian_decision', 'statistics.bayesian_decision.sequential_decision',
     'math.statistics.bayesian_decision.sequential_decision', 'SPRT for normal data', 'Solve optimal stopping problem'),

    # Phase 2 - Time Series Analysis (4)
    ('ARIMASpecialist', 'timeseries', 'statistics.timeseries.arima',
     'math.statistics.timeseries.arima', 'Fit AR(1) model', 'ARIMA(2,1,1) forecasting'),
    ('KalmanFilterSpecialist', 'timeseries', 'statistics.timeseries.kalman_filter',
     'math.statistics.timeseries.kalman_filter', 'Kalman filter for random walk', 'Extended Kalman filter for nonlinear system'),
    ('SpectralAnalysisSpecialist', 'timeseries', 'statistics.timeseries.spectral_analysis',
     'math.statistics.timeseries.spectral_analysis', 'Compute periodogram', 'Identify dominant frequencies'),
    ('NonlinearTimeSeriesSpecialist', 'timeseries', 'statistics.timeseries.nonlinear_timeseries',
     'math.statistics.timeseries.nonlinear_timeseries', 'Fit GARCH(1,1)', 'Detect chaos via Lyapunov exponent'),

    # Phase 3 - Algebraic Topology (5)
    ('HomotopySpecialist', 'algebraic_topology', 'algebraic_topology.homotopy',
     'math.algebraictopology.homotopy', 'Compute pi_1(circle)', 'Apply van Kampen theorem'),
    ('HomologySpecialist', 'algebraic_topology', 'algebraic_topology.homology',
     'math.algebraictopology.homology', 'Compute H_1(torus)', 'Compute Euler characteristic'),
    ('CohomologySpecialist', 'algebraic_topology', 'algebraic_topology.cohomology',
     'math.algebraictopology.cohomology', 'Compute cup product', 'Apply Poincare duality'),
    ('FundamentalGroupSpecialist', 'algebraic_topology', 'algebraic_topology.fundamental_group',
     'math.algebraictopology.fundamentalgroup', 'Compute pi_1 presentation', 'Classify covering spaces'),
    ('SpectralSequencesSpecialist', 'algebraic_topology', 'algebraic_topology.spectral_sequences',
     'math.algebraictopology.spectralsequences', 'Compute Leray-Serre E2 page', 'Check spectral sequence convergence'),

    # Phase 3 - Ergodic Theory (4)
    ('InvariantMeasureSpecialist', 'ergodic', 'ergodic.invariant_measures',
     'math.ergodic.invariant_measures', 'Verify invariant measure', 'Check ergodicity'),
    ('MixingSpecialist', 'ergodic', 'ergodic.mixing',
     'math.ergodic.mixing', 'Check strong mixing', 'Compute mixing rate'),
    ('ErgodicTheoremSpecialist', 'ergodic', 'ergodic.ergodic_theorems',
     'math.ergodic.ergodic_theorems', 'Apply Birkhoff theorem', 'Verify time vs space average'),
    ('DynamicalEntropySpecialist', 'ergodic', 'ergodic.dynamical_entropy',
     'math.ergodic.dynamical_entropy', 'Compute KS entropy', 'Apply Shannon-McMillan-Breiman'),

    # Phase 3 - Geometric Measure Theory (4)
    ('HausdorffMeasureSpecialist', 'geometric_measure', 'geometric_measure.hausdorff_measure',
     'math.geometricmeasure.hausdorff_measure', 'Compute Hausdorff dimension', 'Estimate fractal dimension'),
    ('RectifiabilitySpecialist', 'geometric_measure', 'geometric_measure.rectifiability',
     'math.geometricmeasure.rectifiability', 'Check rectifiability', 'Compute tangent space'),
    ('CurrentsSpecialist', 'geometric_measure', 'geometric_measure.currents',
     'math.geometricmeasure.currents', 'Construct current', 'Compute boundary operator'),
    ('MinimalSurfacesSpecialist', 'geometric_measure', 'geometric_measure.minimal_surfaces',
     'math.geometricmeasure.minimal_surfaces', 'Solve Plateau problem', 'Verify mean curvature zero'),

    # Phase 3 - Topological Data Analysis (4)
    ('PersistentHomologySpecialist', 'tda', 'tda.persistent_homology',
     'math.tda.persistent_homology', 'Compute persistence diagram', 'Compute bottleneck distance'),
    ('SimplicialComplexSpecialist', 'tda', 'tda.simplicial_complex',
     'math.tda.simplicial_complex', 'Construct VR complex', 'Compute nerve of covering'),
    ('MapperSpecialist', 'tda', 'tda.mapper',
     'math.tda.mapper', 'Construct Mapper graph', 'Analyze topological structure'),
    ('TopologicalInferenceSpecialist', 'tda', 'tda.topological_inference',
     'math.tda.topological_inference', 'Compute confidence sets', 'Bootstrap persistence diagram'),

    # Phase 4 - Advanced Optimization (6)
    ('NonconvexOptimizationSpecialist', 'optimization_advanced', 'optimization.advanced.nonconvex',
     'math.optimization.advanced.nonconvex', 'Trust region for f(x)=x^4-3x^3+2', 'SQP with augmented Lagrangian'),
    ('GlobalOptimizationSpecialist', 'optimization_advanced', 'optimization.advanced.global_optimization',
     'math.optimization.advanced.global', 'Simulated annealing for Rastrigin', 'Differential evolution for multi-modal'),
    ('VariationalCalculusSpecialist', 'optimization_advanced', 'optimization.advanced.variational_calculus',
     'math.optimization.advanced.variational', 'Euler-Lagrange for geodesic', 'Brachistochrone with constraints'),
    ('OptimalControlSpecialist', 'optimization_advanced', 'optimization.advanced.optimal_control',
     'math.optimization.advanced.control', 'PMP for linear control', 'HJB for LQR problem'),
    ('GameTheoryOptimizationSpecialist', 'optimization_advanced', 'optimization.advanced.game_theory',
     'math.optimization.advanced.game', 'Nash equilibrium 2x2', 'Find ESS for rock-paper-scissors'),
    ('MultiobjectiveOptimizationSpecialist', 'optimization_advanced', 'optimization.advanced.multiobjective',
     'math.optimization.advanced.multiobjective', 'Pareto front for bi-objective', 'NSGA-II population evolution'),
]


def load_template() -> str:
    """Load the specialist test template."""
    template_path = Path(__file__).parent.parent / 'tests' / 'agents' / 'specialists' / 'test_template.py'

    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_test_file(specialist: Tuple, template: str) -> Tuple[str, str]:
    """
    Generate test file from template.

    Args:
        specialist: (name, domain, module_path, service_type, simple_problem, complex_problem)
        template: Template content

    Returns:
        (output_path, generated_content)
    """
    name, domain, module_path, service_type, simple_prob, complex_prob = specialist

    # Replace placeholders
    content = template.replace('{{SPECIALIST_NAME}}', name)
    content = content.replace('{{DOMAIN}}', domain)
    content = content.replace('{{MODULE_PATH}}', module_path)
    content = content.replace('{{SERVICE_TYPE}}', service_type)
    content = content.replace('{{SIMPLE_PROBLEM}}', simple_prob)
    content = content.replace('{{COMPLEX_PROBLEM}}', complex_prob)

    # Generate filename
    filename = f"test_{name.lower()}_complete.py"
    output_path = Path(__file__).parent.parent / 'tests' / 'agents' / 'specialists' / domain / filename

    return str(output_path), content


def generate_all_tests(specialists: List[Tuple] = None, dry_run: bool = False):
    """Generate all specialist tests."""
    if specialists is None:
        specialists = SPECIALISTS

    template = load_template()
    generated_count = 0
    total_loc = 0

    print(f"Generating {len(specialists)} specialist test files...")
    print()

    for specialist in specialists:
        name, domain, _, _, _, _ = specialist

        output_path, content = generate_test_file(specialist, template)

        if not dry_run:
            # Create domain directory if needed
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

        loc = len(content.split('\n'))
        total_loc += loc
        generated_count += 1

        status = "[DRY RUN]" if dry_run else "[CREATED]"
        print(f"{status} {name:40} -> {output_path}")
        print(f"         {loc} LOC, ~12 tests")

    print()
    print(f"Summary:")
    print(f"  Files generated: {generated_count}")
    print(f"  Total LOC: {total_loc:,}")
    print(f"  Estimated tests: {generated_count * 12}")
    print(f"  Average LOC/file: {total_loc // generated_count if generated_count > 0 else 0}")


def main():
    parser = argparse.ArgumentParser(description='Generate specialist test files')
    parser.add_argument('--all', action='store_true', help='Generate all specialist tests')
    parser.add_argument('--domain', type=str, help='Generate tests for specific domain')
    parser.add_argument('--specialist', type=str, help='Generate test for specific specialist')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without creating files')
    parser.add_argument('--list', action='store_true', help='List all available specialists')

    args = parser.parse_args()

    if args.list:
        print("Available specialists:")
        for name, domain, _, _, _, _ in SPECIALISTS:
            print(f"  {domain:20} {name}")
        return

    if args.all:
        generate_all_tests(dry_run=args.dry_run)
    elif args.domain:
        filtered = [s for s in SPECIALISTS if s[1] == args.domain]
        if not filtered:
            print(f"No specialists found for domain: {args.domain}")
            return
        generate_all_tests(filtered, dry_run=args.dry_run)
    elif args.specialist:
        filtered = [s for s in SPECIALISTS if s[0] == args.specialist]
        if not filtered:
            print(f"Specialist not found: {args.specialist}")
            return
        generate_all_tests(filtered, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
