<!-- Converted from: Phase 2 is designated as Vertical Domain Expansion.docx -->

Phase 2 is designated as Vertical Domain Expansion.
In Phase 1, you successfully constructed the "Central Nervous System" (the Orchestrator) and the "Conscience" (the Verification Core). Phase 2 is the construction of the Body. The strategic objective here is Domain Decomposition: the systematic fragmentation of the monolithic "Math Agent" concept into a granular hierarchy of highly specialized sub-teams. This phase prevents the "Jack of all trades, master of none" failure mode by ensuring that specific mathematical operations are executed by agents wrapping specific, optimized algorithms (e.g., utilizing the Risch algorithm for integration rather than a generic LLM prediction) [1], [2].
Here is the expanded, step-by-step technical specification for the agent teams required in Phase 2.
- 
1. The Algebra Supervisor & Sub-Team (The Foundation)
Objective: Establish the computational substrate. Because almost all higher-level mathematics (Calculus, Physics, Combinatorics) relies on algebraic manipulation, this layer must be robust. If the Algebra team fails to simplify a polynomial correctly, the Calculus team cannot integrate it.
- Agent 1.1: The Algebra Supervisor (Tier 2)
    ◦ Directive: Instantiate the "Foreman" for Algebra. Its primary logic is not calculation, but simplification strategy. It must understand that factoring a polynomial is often a prerequisite for finding roots, and route tasks accordingly.
    ◦ Routing Logic: It receives high-level "Algebra" tasks from the Orchestrator and delegates to the specific sub-specialist [3], [4].
- Agent 1.2: The Arithmetic Specialist
    ◦ Directive: Build an agent strictly for Arbitrary-Precision Arithmetic.
    ◦ Technical Spec: This agent must wrap libraries like GMP or mpmath. Standard floating-point math is forbidden here; this agent handles integers with thousands of digits and modular arithmetic without rounding errors, ensuring exactness for Number Theory applications [3], [4].
- Agent 1.3: The Polynomial Manipulation Specialist
    ◦ Directive: Build an agent specialized in the structure of polynomials.
    ◦ Key Algorithm: Implement wrappers for Gröbner Bases (e.g., Buchberger’s algorithm). This allows the system to solve systems of polynomial equations—a task impossible for standard LLMs to perform reliably via prediction alone [3], [4].
- Agent 1.4: The Number Theory Specialist
    ◦ Directive: Build an agent for discrete integers and prime structures.
    ◦ Capabilities: Primality testing (Miller-Rabin), Integer Factorization (Pollard’s rho/Quadratic Sieve), and Diophantine equation solving. This agent manages the "discrete" side of algebra [3], [4].
- 
2. The Calculus Supervisor & Sub-Team (The Analysis Layer)
Objective: Handle continuous change. This is the most complex domain requiring the strictest separation between Symbolic (exact) and Numerical (approximate) methods.
- Agent 2.1: The Calculus Supervisor (Tier 2)
    ◦ Directive: Instantiate the Supervisor. Crucially, this agent must possess the Decision Logic to distinguish between "Find the exact integral" (Symbolic) and "Approximate the area" (Numerical). It acts as the gatekeeper to prevent the system from wasting resources trying to symbolically integrate non-integrable functions [5], [6].
- Agent 2.2: The Differentiation Specialist
    ◦ Directive: Implement an agent for computing derivatives, including multi-variable gradients, Jacobians, and Hessians.
- Agent 2.3: The Integration Specialist (The Critical Split)
    ◦ Directive: This agent is the most prone to hallucination and requires a dual-engine approach controlled by rigid logic.
    ◦ Symbolic Engine: Must implement or wrap a Risch Algorithm solver (like in SymPy/Mathematica) for finding closed-form antiderivatives.
    ◦ Numerical Engine: If symbolic failure occurs (or is impossible), it must fall back to Quadrature methods (e.g., adaptive Simpson's rule or tanh-sinh quadrature) [5], [6].
- Agent 2.4: The Differential Equation Solver
    ◦ Directive: Implement an agent specifically for ODEs and PDEs. It must recognize boundary value problems and select between exact symbolic matches and numerical solvers like Runge-Kutta or lsoda [5], [6].
- Agent 2.5: The Series Specialist
    ◦ Directive: A specialist dedicated to Taylor/Fourier series expansions and convergence analysis, often required to approximate functions that cannot be handled analytically [7], [8].
- 
3. The Linear Algebra Supervisor & Sub-Team (The Vector Layer)
Objective: Handle high-dimensional data. This requires fundamentally different stability considerations than scalar algebra; matrix multiplication errors compound differently than scalar errors.
- Agent 3.1: The Linear Algebra Supervisor (Tier 2)
    ◦ Directive: Instantiate the Supervisor. It must identify matrix properties (sparse vs. dense, symmetric vs. non-symmetric, positive-definite) to select the correct algorithm, optimizing for computational stability [9], [10].
- Agent 3.2: The Matrix Operations Specialist
    ◦ Directive: Handle basic arithmetic, traces, determinants, and transposes.
- Agent 3.3: The Decomposition Specialist
    ◦ Directive: A highly specialized agent for matrix factorizations.
    ◦ Capabilities: Must support SVD (Singular Value Decomposition), QR, LU, and Cholesky decompositions. These are the "heavy lifting" algorithms required for everything from data compression to solving linear systems [9], [10].
- Agent 3.4: The Vector Space Analyst
    ◦ Directive: Build an agent to calculate abstract properties: Basis, Rank, Nullspace, and Eigenvalues/Eigenvectors. This agent bridges the gap between computation and abstract vector space theory [9], [10].
- 
4. The Probability & Statistics Supervisor & Sub-Team (The Uncertainty Layer)
Objective: Handle probabilistic reasoning. This domain requires a strict philosophical and algorithmic separation between Bayesian and Frequentist methods to prevent incoherence.
- Agent 4.1: The Probability & Statistics Supervisor (Tier 2)
    ◦ Directive: This supervisor determines the framework required. If the user asks for a "confidence interval," it routes to the Frequentist agent. If the user asks for a "posterior update," it routes to the Bayesian agent [11], [12].
- Agent 4.2: The Distribution Specialist
    ◦ Directive: Manages Probability Density Functions (PDFs) and Cumulative Distribution Functions (CDFs).
- Agent 4.3: The Bayesian Inference Engine
    ◦ Directive: A dedicated agent for posterior calculation using Markov Chain Monte Carlo (MCMC) methods and managing factor graphs [11], [12].
- Agent 4.4: The Frequentist Agent
    ◦ Directive: Handles Hypothesis Testing (t-tests, p-values) and Confidence Intervals using classical statistical methods [11], [12].
- 
5. The Numerical Computation Utility (The Safety Net)
Objective: Ensure the system never "gives up" when symbolic math is impossible. This serves as the fallback engine for all domains.
- Agent 5.1: The Numerical Computation Utility (Tier 3)
    ◦ Directive: Wrap a high-performance numerical library (e.g., NumPy/SciPy or Julia).
    ◦ Role: This agent does not "reason"; it "crunches." It is the fallback for all other supervisors. If the Algebra Supervisor cannot solve a polynomial degree 5+ symbolically (Abel-Ruffini theorem), it routes to this agent for a numerical root approximation [13], [14].
- 
6. System Wiring (The Nervous System Connection)
Objective: Connect these new "organs" to the brain (Phase 1 Orchestrator).
- Action 6.1: Directory Facilitator (DF) Registration
    ◦ Directive: Every new Specialist and Supervisor must register their capabilities with the Directory Facilitator built in Phase 0.
    ◦ Example: The Integration Specialist registers service: math.calculus.integration with properties type:symbolic and algorithm:risch.
- Action 6.2: Dynamic Orchestrator Update
    ◦ Result: Because the Orchestrator (Tier 1) queries the DF dynamically, it now "sees" these new agents. You do not need to rewrite the Orchestrator's code; it simply has more tools in its rolodex to delegate to [15], [16].
Phase 2 Deliverable: The "Fragile Genius"
At the end of Phase 2, you have a system with immense mathematical power. It can solve SVDs, integrate complex functions, and prove number theory lemmas.
- The Risk: It is currently "brittle." If the Calculus Supervisor sends a negative number to the Logarithm Specialist, it will crash. If the Symbolic and Numerical agents disagree, there is no one to judge them.
- Next Step: This necessitates Phase 3, where you install the "Meta-Cognitive Middleware" (Precondition Validation and Knowledge Management) to stabilize this powerful workforce [17], [18].