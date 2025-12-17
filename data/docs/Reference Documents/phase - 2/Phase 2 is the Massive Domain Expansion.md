<!-- Converted from: Phase 2 is the Massive Domain Expansion.docx -->

Phase 2 is the Massive Domain Expansion.
In Phase 1, you built the "Central Nervous System" (Orchestrator) and the "Conscience" (Verifier). Now, in Phase 2, you build the Body. The strategic objective is Domain Decomposition: systematically shattering the concept of a monolithic "Math Agent" into granular, highly specialized sub-teams. This prevents the "Jack of all trades, master of none" failure mode by ensuring that specific mathematical operations are handled by agents wrapping specific, optimized algorithms (e.g., using the Risch algorithm for integration rather than a generic LLM prediction) [1], [2].
Here is the expanded, step-by-step technical specification for Phase 2: Vertical Domain Expansion.
- 
Step 1: The Foundation Layer (Algebra Supervisor & Team)
Objective: Establish the computational substrate. Almost all higher-level math (Calculus, Physics) relies on algebraic manipulation. If this layer is weak, the entire hierarchy collapses.
- Action 1.1: The Algebra Supervisor (Tier 2)
    ◦ Directive: Instantiate the "Foreman" for Algebra. Its primary logic is not solving, but simplification strategy. It must know that factoring a polynomial is often a prerequisite for finding roots.
    ◦ Routing Logic: It receives "Algebra" tasks from the Orchestrator and delegates to the sub-team.
- Action 1.2: The Arithmetic Specialist
    ◦ Directive: Build an agent strictly for Arbitrary-Precision Arithmetic.
    ◦ Technical Spec: It must wrap libraries like GMP or mpmath. Standard floating-point math is forbidden here; this agent handles integers with thousands of digits and modular arithmetic without rounding errors [3], [4].
- Action 1.3: The Polynomial Manipulation Specialist
    ◦ Directive: Build an agent specialized in the structure of polynomials.
    ◦ Key Algorithm: Implement wrappers for Gröbner Bases (e.g., Buchberger’s algorithm). This allows the system to solve systems of polynomial equations—a task impossible for standard LLMs [5], [6].
- Action 1.4: The Number Theory Specialist
    ◦ Directive: Build an agent for discrete integers.
    ◦ Capabilities: Primality testing (Miller-Rabin), Integer Factorization (Pollard’s rho/Quadratic Sieve), and Diophantine equation solving [3], [4].
- 
Step 2: The Analysis Layer (Calculus Supervisor & Team)
Objective: Handle continuous change. This is the most complex domain requiring the strictest separation between symbolic and numerical methods.
- Action 2.1: The Calculus Supervisor (Tier 2)
    ◦ Directive: Instantiate the Supervisor. Crucially, this agent must possess the Decision Logic to distinguish between "Find the exact integral" (Symbolic) and "Approximate the area" (Numerical) [2].
- Action 2.2: The Differentiation Specialist
    ◦ Directive: Implement an agent for computing derivatives, including multi-variable gradients and Jacobians.
- Action 2.3: The Integration Specialist (The Critical Split)
    ◦ Directive: This agent is the most prone to hallucination and requires a dual-engine approach.
    ◦ Symbolic Engine: Must implement or wrap a Risch Algorithm solver (like in SymPy/Mathematica) for finding closed-form antiderivatives [5], [7].
    ◦ Numerical Engine: If symbolic failure occurs, it must fall back to Quadrature methods (e.g., adaptive Simpson's rule) [7], [8].
- Action 2.4: The Differential Equation Solver
    ◦ Directive: Implement an agent specifically for ODEs and PDEs. It must recognize boundary value problems and select between exact symbolic matches and numerical solvers like Runge-Kutta [7], [9].
- 
Step 3: The Vector Layer (Linear Algebra Supervisor & Team)
Objective: Handle high-dimensional data. This requires fundamentally different stability considerations than scalar algebra.
- Action 3.1: The Linear Algebra Supervisor (Tier 2)
    ◦ Directive: Instantiate the Supervisor. It must identify matrix properties (sparse vs. dense, symmetric vs. non-symmetric) to select the correct algorithm [10].
- Action 3.2: The Matrix Operations Specialist
    ◦ Directive: Handle basic arithmetic, traces, determinants, and transposes.
- Action 3.3: The Decomposition Specialist
    ◦ Directive: A highly specialized agent for matrix factorizations.
    ◦ Capabilities: Must support SVD (Singular Value Decomposition), QR, LU, and Cholesky decompositions. These are the "heavy lifting" algorithms required for everything from data compression to solving linear systems [3], [6].
- Action 3.4: The Vector Space Analyst
    ◦ Directive: Build an agent to calculate abstract properties: Basis, Rank, Nullspace, and Eigenvalues/Eigenvectors [3], [4].
- 
Step 4: The Logic & Uncertainty Layer (Discrete & Prob Supervisors)
Objective: Handle discrete structures and probabilistic reasoning. These domains require distinct representation formats (graphs vs. distributions).
- Action 4.1: The Discrete Math Team
    ◦ Combinatorics Agent: Handles counting, permutations, and combinations. Note: Current AI is weak here; this agent requires rigid algorithmic backing (generating functions) [11], [12].
    ◦ Graph Theory Agent: Wraps graph algorithms (Dijkstra, BFS/DFS, Max Flow). It requires an adjacency matrix or list representation, not text [12].
- Action 4.2: The Probability & Statistics Team
    ◦ Directive: You must split Bayesian and Frequentist reasoning into separate agents to avoid philosophical and algorithmic conflict.
    ◦ Bayesian Inference Engine: Uses Markov Chain Monte Carlo (MCMC) and posterior calculations [13].
    ◦ Frequentist Agent: Handles Hypothesis Testing (p-values, t-tests) and Confidence Intervals [14].
- 
Step 5: The Numerical Fallback (The Safety Net)
Objective: Ensure the system never "gives up" when symbolic math is impossible.
- Action 5.1: The Numerical Computation Utility (Tier 3)
    ◦ Directive: Wrap a high-performance numerical library (e.g., NumPy/SciPy or Julia).
    ◦ Role: This agent does not "reason"; it "crunches." It is the fallback for all other supervisors. If the Algebra Supervisor cannot solve a polynomial degree 5+ symbolically, it routes to this agent for a numerical root approximation [15], [2].
- 
Step 6: Registration & Wiring (The Nervous System Connection)
Objective: Connect these new "organs" to the brain (Phase 1 Orchestrator).
- Action 6.1: DF Registration
    ◦ Directive: Every new Specialist and Supervisor must register their capabilities with the Directory Facilitator (DF) built in Phase 0.
    ◦ Example: The Integration Specialist registers service: math.calculus.integration with properties type:symbolic and algorithm:risch.
- Action 6.2: Orchestrator Update (Dynamic)
    ◦ Result: Because the Orchestrator queries the DF dynamically, it now "sees" these new agents. You do not need to rewrite the Orchestrator's code; it simply has more tools in its rolodex [16], [17].
Phase 2 Deliverable: The "Fragile Genius"
At the end of Phase 2, you have a system with immense mathematical power. It can solve SVDs, integrate complex functions, and prove number theory lemmas.
- The Risk: It is currently "brittle." If the Calculus Supervisor sends a negative number to the Logarithm Specialist, it will crash. If the Symbolic and Numerical agents disagree, there is no one to judge them.
- Next Step: This necessitates Phase 3, where you install the "Meta-Cognitive Middleware" (Precondition Validation and Knowledge Management) to stabilize this powerful workforce [18], [19].