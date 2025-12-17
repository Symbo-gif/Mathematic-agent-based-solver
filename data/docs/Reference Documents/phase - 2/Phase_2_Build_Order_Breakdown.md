<!-- Converted from: Phase_2_Build_Order_Breakdown.docx -->

# Phase 2 Build Order Breakdown
Vertical Domain Expansion: Constructing the Mathematical Workforce
*Autonomous Mathematical Discovery Engine*
# 1. Executive Summary
Phase 2 represents the systematic transformation of the multi-agent collective from a cognitive nucleus (established in Phase 1) into a fully operational mathematical workforce. The strategic mandate—designated as **Domain Decomposition**—requires the deliberate fragmentation of the monolithic "Math Agent" concept into a hierarchical collective of granular, highly specialized sub-teams. This architectural philosophy explicitly prevents the "Jack of all trades, master of none" failure mode by ensuring that specific mathematical operations are executed by agents wrapping specific, optimized algorithms rather than relying on generic LLM predictions.
## 1.1 Strategic Context
Following the completion of Phase 0 (infrastructural bedrock) and Phase 1 (cognitive chassis), the system possesses a functional "Central Nervous System" (Orchestrator) and "Conscience" (Verification Core). Phase 2 is mandated to construct the **"Body"**—a powerful workforce of mathematical specialists organized into a three-tiered hierarchy that maximizes both accuracy and computational efficiency.
## 1.2 Source Documentation Reference
This build order synthesizes specifications from the following authoritative project documentation:

| Document | Content Scope |
| --- | --- |
| phase_2_Coding_Strategy_for_Vertical_Domain_Expansion.docx | Primary technical specification with agent blueprints and integration protocols |
| Phase_2_is_designated_as_Vertical_Domain_Expansion.docx | Detailed agent team specifications with algorithm requirements |
| Phase_2_is_the_Massive_Domain_Expansion.docx | Step-by-step technical specification with action items |
| phases_0-6_for_the_Autonomous_Mathematical_Discovery_Engine.docx | Overall roadmap and phase integration context |
| symbo.py | Reference implementation with Gröbner bases, symbolic algebra, and perturbation methods |
| Phase_0_Build_Order_Breakdown.docx | Directory Facilitator and AMS code templates for integration |


# 2. Core Architectural Principles
The successful expansion of the agent collective hinges upon strict adherence to a set of core architectural principles. These principles are **non-negotiable** and ensure that rapid growth in agent capabilities remains coherent, robust, and aligned with the foundational Phase 0 infrastructure.
## 2.1 Embrace Granular Specialization
- WHAT: Avoid a single, monolithic "Math Agent" and instead create a collective of highly specialized sub-teams
- WHY: Ensures every mathematical operation is handled by a true expert, maximizing both accuracy and efficiency
- HOW: Each agent is tasked with a narrow, specific mathematical function backed by deterministic algorithms
## 2.2 Prioritize Algorithmic Wrappers over Generic Prediction
- WHAT: Agents must wrap specific, optimized, and deterministic algorithms for their core functions
- WHY: Guarantees mathematical precision and eliminates hallucination risk inherent in generic LLM predictions
- EXAMPLES: Integration Specialist uses Risch algorithm; Arithmetic Specialist uses GMP/mpmath for arbitrary-precision
## 2.3 Adhere to the Tiered Hierarchy
The system is organized into a three-tiered structure to manage complexity and delegate responsibility effectively:

| Tier | Role | Function |
| --- | --- | --- |
| Tier 1 | Orchestrator | Central brain from Phase 1; queries DF for available services |
| Tier 2 | Supervisors | Strategic routers for major domains (Algebra, Calculus, etc.) |
| Tier 3 | Specialists | Computational workhorses executing specific algorithmic tasks |

## 2.4 Strictly Enforce Separation of Concerns
Agent roles must be separated based on fundamental mathematical and philosophical distinctions to prevent algorithmic and logical conflicts:
- Symbolic vs. Numerical: Mandatory split within the Calculus team between exact (Risch algorithm) and approximate (Quadrature) methods
- Bayesian vs. Frequentist: Strict separation within Statistics team to avoid philosophical incoherence in probabilistic reasoning

# 3. Build Order: Step-by-Step Implementation
## Step 1: The Foundation Layer (Algebra Team)
**OBJECTIVE: **Establish the computational substrate upon which all higher-level mathematics depends. Almost all advanced operations (Calculus, Physics, Combinatorics) rely on algebraic manipulation. If this layer is weak, the entire hierarchy collapses.
### Agent 1.1: Algebra Supervisor (Tier 2)
- DIRECTIVE: Instantiate the "Foreman" for Algebra. Its primary logic is not calculation, but simplification strategy.
- ROUTING LOGIC: Must understand that factoring a polynomial is often a prerequisite for finding roots. Receives high-level "Algebra" tasks from the Orchestrator and delegates to appropriate sub-specialists.
- DF REGISTRATION: service: math.algebra, properties: {type: 'supervisor', domain: 'algebra'}
### Agent 1.2: Arithmetic Specialist (Tier 3)
- DIRECTIVE: Build an agent strictly for Arbitrary-Precision Arithmetic.
- TECHNICAL SPEC: Must wrap libraries like GMP or mpmath. Standard floating-point math is FORBIDDEN. Handles integers with thousands of digits and modular arithmetic without rounding errors.
- WHY: Ensures absolute numerical exactness required for Number Theory applications.
# arithmetic_specialist.py
from mpmath import mp, mpf
mp.dps = 50  # 50 decimal places precision

class ArithmeticSpecialist:
    def __init__(self, df: DirectoryFacilitator):
        self.df = df
        self._register_services()

    def _register_services(self):
        self.df.register(ServiceRegistration(
            service_type='math.algebra.arithmetic',
            agent_id='arithmetic_specialist_001',
            algorithm='gmp',
            properties={'precision': 'arbitrary', 'type': 'exact'}
        ))
### Agent 1.3: Polynomial Manipulation Specialist (Tier 3)
- DIRECTIVE: Build an agent specialized in the structure of polynomials and systems of polynomial equations.
- KEY ALGORITHM: Must implement wrappers for Gröbner Bases (e.g., Buchberger's algorithm). This allows the system to solve systems of polynomial equations—a task impossible for standard LLMs to perform reliably.
# From symbo.py - Gröbner basis implementation
from sympy import groebner, solve

def groebner_solve(self, poly_system: List[sp.Expr],
                   vars_to_solve: List[sp.Symbol] = None):
    G = groebner(poly_system, *vars_to_solve, order='lex')
    solutions = solve(poly_system, *vars_to_solve, dict=True)
    # Filter for real solutions
    real_solutions = []
    for sol in solutions:
        if all(abs(v.as_real_imag()[1]) < 1e-8 for v in sol.values()):
            real_solutions.append({str(k): v for k, v in sol.items()})
    return real_solutions
### Agent 1.4: Number Theory Specialist (Tier 3)
- DIRECTIVE: Build an agent for discrete integers and prime structures.
- CAPABILITIES: Primality testing (Miller-Rabin), Integer Factorization (Pollard's rho/Quadratic Sieve), and Diophantine equation solving.

## Step 2: The Analysis Layer (Calculus Team)
**OBJECTIVE: **Handle problems of continuous change. This is the most complex domain requiring the strictest separation between Symbolic (exact) and Numerical (approximate) methods.
### Agent 2.1: Calculus Supervisor (Tier 2)
- DIRECTIVE: Instantiate the Supervisor with crucial Decision Logic.
- CRITICAL FUNCTION: Must distinguish between "Find the exact integral" (Symbolic) and "Approximate the area" (Numerical). Acts as gatekeeper to prevent wasting resources on non-integrable functions.
- DF REGISTRATION: service: math.calculus, properties: {type: 'supervisor', decision_logic: 'symbolic_vs_numerical'}
### Agent 2.2: Differentiation Specialist (Tier 3)
- DIRECTIVE: Implement an agent for computing derivatives.
- CAPABILITIES: Single and multi-variable functions, gradients, Jacobians, and Hessians—essential for optimization and analysis.
### Agent 2.3: Integration Specialist — THE CRITICAL SPLIT (Tier 3)
**DIRECTIVE: **This agent is the most prone to hallucination and requires a DUAL-ENGINE approach controlled by rigid logic.

| Engine | Technical Specification |
| --- | --- |
| Symbolic Engine | Must wrap a Risch Algorithm solver (like in SymPy/Mathematica) for finding closed-form antiderivatives. Gold standard for exact integration. |
| Numerical Engine | If symbolic failure occurs (or is mathematically impossible), fall back to Quadrature methods (adaptive Simpson's rule, tanh-sinh quadrature). |

# integration_specialist.py
import sympy as sp
from scipy import integrate

class IntegrationSpecialist:
    def integrate(self, expr, var, bounds=None):
        # Try symbolic first (Risch algorithm)
        try:
            result = sp.integrate(expr, var)
            if not result.has(sp.Integral):  # Success
                return {'type': 'symbolic', 'result': result}
        except: pass
        # Fall back to numerical quadrature
        if bounds:
            f = sp.lambdify(var, expr)
            result, _ = integrate.quad(f, *bounds)
            return {'type': 'numerical', 'result': result}
        return {'type': 'failure', 'result': None}
### Agent 2.4: Differential Equation Solver (Tier 3)
- DIRECTIVE: Implement an agent specifically for ODEs and PDEs.
- CAPABILITIES: Must recognize boundary value problems and select between exact symbolic matches and numerical solvers (Runge-Kutta, lsoda).
### Agent 2.5: Series Specialist (Tier 3)
- DIRECTIVE: A specialist dedicated to Taylor/Fourier series expansions and convergence analysis.
- PURPOSE: Often required to approximate functions that cannot be handled analytically.

## Step 3: The Vector Layer (Linear Algebra Team)
**OBJECTIVE: **Handle high-dimensional data, vector spaces, and matrices. This domain requires fundamentally different stability considerations than scalar algebra—rounding errors compound catastrophically in large matrix operations.
### Agent 3.1: Linear Algebra Supervisor (Tier 2)
- DIRECTIVE: Analyze incoming linear algebra tasks and select the optimal algorithm based on matrix properties.
- PROPERTIES TO IDENTIFY: Sparse vs. dense, symmetric vs. non-symmetric, positive-definite—ensures computational stability and efficiency.
### Agent 3.2: Matrix Operations Specialist (Tier 3)
- CAPABILITIES: Matrix addition/multiplication, traces, determinants, and transposes.
### Agent 3.3: Decomposition Specialist (Tier 3)
- DIRECTIVE: Perform the "heavy lifting" of matrix factorizations.
- REQUIRED DECOMPOSITIONS: SVD (Singular Value Decomposition), QR, LU, and Cholesky. Foundational for data compression, solving linear systems, and machine learning.
### Agent 3.4: Vector Space Analyst (Tier 3)
- DIRECTIVE: Calculate the abstract properties of matrices and vector spaces.
- CAPABILITIES: Basis, Rank, Nullspace, and Eigenvalues/Eigenvectors. Bridges raw computation and abstract vector space theory.
## Step 4: The Logic & Uncertainty Layers
### 4.1 The Discrete Math Team
- Combinatorics Agent: Handles counting, permutations, and combinations. NOTE: Current AI is weak here; this agent requires rigid algorithmic backing using generating functions.
- Graph Theory Agent: Wraps canonical graph algorithms (Dijkstra, BFS/DFS, Max Flow). MUST operate on structured data representations (adjacency matrix/list), NOT raw natural language.
### 4.2 The Probability & Statistics Team
**OBJECTIVE: **Handle probabilistic reasoning with a strict philosophical and algorithmic separation between Bayesian and Frequentist methods.
- Probability & Statistics Supervisor (Tier 2): Determines the framework required. Routes 'confidence intervals' → Frequentist; 'posterior updates' → Bayesian.
- Distribution Specialist: Manages PDFs (Probability Density Functions) and CDFs (Cumulative Distribution Functions).
- Bayesian Inference Engine: Dedicated agent for posterior calculation using MCMC methods and probabilistic graphical models.
- Frequentist Agent: Handles hypothesis testing (t-tests, p-values) and confidence intervals.

## Step 5: The Numerical Fallback (System Safety Net)
**OBJECTIVE: **Ensure the system NEVER "gives up" when symbolic math is computationally intractable or mathematically impossible (e.g., per the Abel-Ruffini theorem for polynomials degree 5+).
### Agent 5.1: Numerical Computation Utility (Tier 3)
- DIRECTIVE: Wrap a high-performance numerical library (NumPy/SciPy or Julia).
- ROLE: This agent does NOT "reason"; it "crunches." Acts as the fallback destination for ANY supervisor that cannot obtain a symbolic solution.
- EXAMPLE: If the Algebra Supervisor cannot solve a degree-5+ polynomial symbolically, it routes to this agent for numerical root approximation.
## Step 6: System Wiring (Nervous System Connection)
**OBJECTIVE: **Connect these new "organs" to the brain (Phase 1 Orchestrator) via the Directory Facilitator infrastructure established in Phase 0.
### 6.1 Directory Facilitator (DF) Registration
Every new Supervisor and Specialist agent created in Phase 2 **MUST** register its specific capabilities with the Directory Facilitator. This registration must include both the service name and key properties describing its function.
# From Phase_0_Build_Order_Breakdown.docx - DF Registration Pattern
df.register(ServiceRegistration(
    service_type='math.calculus.integration',
    agent_id='integration_specialist_001',
    algorithm='risch',
    cost='high',
    properties={'type': 'symbolic', 'deterministic': 'true'}
))
### 6.2 Dynamic Orchestration
Because the Tier 1 Orchestrator queries the DF in real-time to find available services, it will automatically "see" and delegate tasks to newly created agents **WITHOUT any modification to its core code**. The Orchestrator's capabilities expand organically as new tools are added to its "rolodex."

# 4. Complete Phase 2 Agent Registry

| Agent | Tier | Key Algorithm | DF Service |
| --- | --- | --- | --- |
| Algebra Supervisor | 2 | Simplification Strategy | math.algebra |
| Arithmetic Specialist | 3 | GMP/mpmath | math.algebra.arithmetic |
| Polynomial Specialist | 3 | Gröbner Bases | math.algebra.polynomial |
| Number Theory Specialist | 3 | Miller-Rabin, Pollard's rho | math.algebra.numbertheory |
| Calculus Supervisor | 2 | Symbolic/Numerical Decision | math.calculus |
| Differentiation Specialist | 3 | Symbolic Differentiation | math.calculus.diff |
| Integration Specialist | 3 | Risch + Quadrature | math.calculus.integration |
| Differential Eq Solver | 3 | Runge-Kutta, lsoda | math.calculus.ode |
| Series Specialist | 3 | Taylor/Fourier | math.calculus.series |
| Linear Algebra Supervisor | 2 | Matrix Property Analysis | math.linalg |
| Matrix Operations Specialist | 3 | Matrix Arithmetic | math.linalg.ops |
| Decomposition Specialist | 3 | SVD, QR, LU, Cholesky | math.linalg.decomp |
| Vector Space Analyst | 3 | Eigen/Null/Rank Analysis | math.linalg.vectorspace |
| Prob & Stats Supervisor | 2 | Bayesian/Frequentist Split | math.stats |
| Distribution Specialist | 3 | PDF/CDF Management | math.stats.distributions |
| Bayesian Inference Engine | 3 | MCMC, Factor Graphs | math.stats.bayesian |
| Frequentist Agent | 3 | t-tests, p-values, CI | math.stats.frequentist |
| Numerical Computation Utility | 3 | NumPy/SciPy/Julia | math.numerical |


# 5. Phase 2 Definition of Done: The "Fragile Genius"
Upon successful completion of all development and integration tasks outlined in this specification, the system will have achieved the state of a ***"Fragile Genius."*** This deliverable represents a massive leap in computational power, but introduces inherent risks that must be acknowledged.
## 5.1 The Genius
The system now possesses immense and verifiable mathematical power. It can execute complex, multi-step tasks that were previously impossible:
- Perform Singular Value Decompositions (SVDs)
- Find closed-form integrals for complex functions using the Risch algorithm
- Prove number theory lemmas using deterministic algorithms
- Solve systems of polynomial equations via Gröbner bases
- Perform arbitrary-precision arithmetic without rounding errors
## 5.2 The Fragility
The system is now powerful but **brittle**. Its specialized agents lack robust precondition validation:
- A supervisor routing a negative number to a Logarithm Specialist will cause a component crash
- No systemic error-handling layer exists to intercept invalid inputs
- If symbolic and numerical agents produce conflicting results, there is no higher-level mechanism to adjudicate the disagreement
## 5.3 Transition to Phase 3
This fragility is an **expected outcome** of Phase 2. It explicitly necessitates **Phase 3: Meta-Cognitive Middleware**, which will introduce the precondition validation, knowledge management, and conflict resolution systems required to stabilize this powerful but brittle workforce.
# 6. Verification Checklist
Phase 2 is complete when ALL of the following conditions are met:
- All 6 Tier 2 Supervisors (Algebra, Calculus, Linear Algebra, Discrete Math, Prob/Stats, Numerical) are instantiated and registered with DF
- All Tier 3 Specialists are registered with appropriate service types and algorithm properties
- Integration Specialist demonstrates dual-engine (Symbolic + Numerical) fallback behavior
- Polynomial Specialist successfully solves a system of equations using Gröbner bases
- Decomposition Specialist successfully performs SVD, QR, LU, and Cholesky decompositions
- Tier 1 Orchestrator queries DF and successfully discovers all new agents dynamically
- End-to-end test case: Complex integral routed Orchestrator → Calculus Supervisor → Integration Specialist → returns verified result
- Bayesian and Frequentist agents operate independently without philosophical conflict
*— End of Phase 2 Build Order Breakdown —*