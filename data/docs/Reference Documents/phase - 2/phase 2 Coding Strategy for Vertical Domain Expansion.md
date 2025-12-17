<!-- Converted from: phase 2 Coding Strategy for Vertical Domain Expansion.docx -->

# Phase 2 Technical Specification: A Coding Strategy for Vertical Domain Expansion
## 1.0 Strategic Mandate for Phase 2
This document outlines the technical specification for Phase 2 of the multi-agent collective initiative, representing a logical evolution from the foundational work of prior phases. While Phase 0 constructed the system's immutable "city"—the core infrastructure and communication protocols—and Phase 1 instantiated its "brain" in the form of the Tier 1 Orchestrator, Phase 2 is mandated to build the "Body." This entails creating a specialized and powerful workforce of mathematical agents. The core strategic objective of this phase is **Domain Decomposition**: a systematic effort to break down the monolithic concept of a general "Math Agent" into a hierarchical collective of granular, expert agents. This approach is critical to preventing the "Jack of all trades, master of none" failure mode that plagues generalized systems. This document provides the actionable build plan for the engineering teams tasked with this vertical domain expansion.
## 2.0 Core Architectural Principles
The successful expansion of the agent collective hinges on the strict adherence to a set of core architectural principles. These principles are non-negotiable and are designed to ensure that the rapid growth in agent capabilities remains coherent, robust, and aligned with the system's foundational architecture established in Phase 0. All development in Phase 2 must conform to the following directives.
**Embrace Granular Specialization** The primary strategy is to avoid a single, monolithic "Math Agent" and instead create a collective of highly specialized sub-teams. Each agent will be tasked with a narrow, specific mathematical function. This ensures that every operation is handled by a true expert, maximizing both accuracy and efficiency.
**Prioritize Algorithmic Wrappers over Generic Prediction** To guarantee mathematical precision and eliminate the risk of hallucination inherent in generic LLM predictions, agents must wrap specific, optimized, and deterministic algorithms for their core functions. For example, the Integration Specialist will use the Risch algorithm for symbolic integration, and the Arithmetic Specialist will use the GNU Multiple Precision Arithmetic Library (GMP) for arbitrary-precision calculations. LLM-based reasoning is for orchestration and strategy, not for raw computation.
**Adhere to the Tiered Hierarchy** The system will be organized into a three-tiered structure to manage complexity and delegate responsibility effectively. The existing **Tier 1 Orchestrator** from Phase 1 will continue to act as the central brain. Phase 2 will introduce **Tier 2 Supervisors**, which act as strategic routers for major mathematical domains (e.g., Algebra, Calculus), and **Tier 3 Specialists**, which are the computational workhorses that execute specific algorithmic tasks.
**Strictly Enforce Separation of Concerns** It is critical to separate agent roles based on fundamental mathematical and philosophical distinctions. This prevents algorithmic and logical conflicts. Two key examples of this principle are mandatory for Phase 2 implementation: the split between **Symbolic (exact) vs. Numerical (approximate)** methods within the Calculus team, and the separation of **Bayesian vs. Frequentist** reasoning into distinct agents within the Statistics team.
These principles will guide the construction of the detailed agent blueprints that follow.
## 3.0 Actionable Build Plan: The Agent Hierarchy
The following subsections provide the detailed technical specifications for instantiating the required agent teams. The build plan is organized by mathematical domain, reflecting a layered approach that builds from foundational capabilities to more abstract ones.
### 3.1 Step 1: The Foundation Layer (Algebra Team)
This layer serves as the computational substrate for the entire system. Most higher-level mathematics depends on robust and precise algebraic manipulation. A failure or weakness in this foundational team will cause a cascading failure throughout the entire agent hierarchy.

| Agent Designation | Core Directive | Technical Specification & Key Algorithms |
| --- | --- | --- |
| Algebra Supervisor (Tier 2) | Act as the foreman for all algebraic tasks. Focus on simplification strategy and task delegation, not direct computation. | Receives high-level algebra tasks from the Tier 1 Orchestrator and routes them to the appropriate specialist. Must understand task prerequisites (e.g., factoring before finding roots). |
| Arithmetic Specialist | Perform Arbitrary-Precision Arithmetic to ensure absolute numerical exactness. | Must wrap libraries like GMP or mpmath. Standard floating-point arithmetic is strictly forbidden. Capable of handling integers with thousands of digits and performing precise modular arithmetic. |
| Polynomial Manipulation Specialist | Specialize in the structural manipulation of polynomials and systems of polynomial equations. | Must implement wrappers for Gröbner Bases (e.g., Buchberger’s algorithm) to reliably solve systems of polynomial equations. |
| Number Theory Specialist | Manage tasks related to discrete integers and prime structures. | Capabilities must include primality testing (e.g., Miller-Rabin), integer factorization (e.g., Pollard’s rho, Quadratic Sieve), and solving Diophantine equations. |

### 3.2 Step 2: The Analysis Layer (Calculus Team)
The objective of this layer is to handle problems of continuous change. This is the most complex domain in Phase 2 and requires the strictest adherence to the principle of separating symbolic (exact) from numerical (approximate) methods to prevent resource waste and incorrect results.

| Agent Designation | Core Directive | Technical Specification & Key Algorithms |
| --- | --- | --- |
| Calculus Supervisor (Tier 2) | Act as the primary gatekeeper for calculus tasks, possessing the crucial decision logic to route problems to the correct engine. | Must distinguish between requests for exact solutions (symbolic) and approximate solutions (numerical) to prevent wasted computation on non-integrable functions. |
| Differentiation Specialist | Compute derivatives for single and multi-variable functions. | Must be capable of calculating gradients, Jacobians, and Hessians, which are essential for multi-variable optimization and analysis. |
| Integration Specialist (The Critical Split) | Provide both exact and approximate solutions for integrals using a dual-engine approach to mitigate LLM hallucination. | Symbolic Engine: Must wrap a Risch Algorithm solver for finding closed-form antiderivatives. <br> Numerical Engine: Must fall back to Quadrature methods (e.g., adaptive Simpson's rule) upon symbolic failure. |
| Differential Equation Solver | Solve Ordinary Differential Equations (ODEs) and Partial Differential Equations (PDEs). | Must be able to recognize boundary value problems and select between exact symbolic matches and numerical solvers like Runge-Kutta. |
| Series Specialist | Specialize in series expansions and convergence analysis. | Dedicated to Taylor and Fourier series expansions, often used to approximate functions that cannot be handled analytically. |

### 3.3 Step 3: The Vector Layer (Linear Algebra Team)
This layer's objective is to handle high-dimensional data, vector spaces, and matrices. This domain requires different computational stability considerations than scalar algebra, as rounding errors can compound catastrophically in large matrix operations. This makes specialized, algorithmically-backed agents not just a preference, but a non-negotiable requirement for system integrity.

| Agent Designation | Core Directive | Technical Specification & Key Algorithms |
| --- | --- | --- |
| Linear Algebra Supervisor (Tier 2) | Analyze incoming linear algebra tasks and select the optimal algorithm based on matrix properties. | Must identify properties like sparse vs. dense, symmetric, and positive-definite to ensure computational stability and efficiency. |
| Matrix Operations Specialist | Handle fundamental matrix arithmetic and property calculations. | Responsible for matrix addition/multiplication, traces, determinants, and transposes. |
| Decomposition Specialist | Perform the "heavy lifting" of matrix factorizations, which are foundational to many advanced applications. | Must support SVD (Singular Value Decomposition), QR, LU, and Cholesky decompositions. |
| Vector Space Analyst | Calculate the abstract properties of matrices and vector spaces. | Bridges the gap between raw computation and abstract theory by calculating Basis, Rank, Nullspace, and Eigenvalues/Eigenvectors. |

### 3.4 Step 4: The Logic Layer (Discrete Math Team)
This section specifies the agents responsible for handling discrete structures, which require unique data representations and rigid algorithmic approaches.
**Combinatorics Agent:** Responsible for counting, permutations, and combinations. This agent requires rigid algorithmic backing (e.g., using generating functions) as this is a known area of weakness for generative AI.
**Graph Theory Agent:** Wraps canonical graph algorithms. It must operate on structured data representations like an adjacency matrix or list, not raw natural language descriptions. Core capabilities include Dijkstra's algorithm, Breadth-First Search (BFS), Depth-First Search (DFS), and Max Flow.
### 3.5 Step 5: The Uncertainty Layer (Probability & Statistics Team)
This layer handles reasoning under uncertainty, requiring a strict philosophical separation of methodologies.
**Probability & Statistics Supervisor (Tier 2):** Its primary directive is to enforce a strict philosophical separation by routing requests based on the required reasoning framework. For example, queries for 'confidence intervals' *must* be routed to the Frequentist Agent, while requests for 'posterior updates' *must* be routed to the Bayesian agent.
**Distribution Specialist:** Manages Probability Density Functions (PDFs) and Cumulative Distribution Functions (CDFs) for various statistical distributions.
**Bayesian Inference Engine:** A dedicated agent for posterior calculations using **Markov Chain Monte Carlo (MCMC)** methods and managing probabilistic graphical models.
**Frequentist Agent:** Handles classical hypothesis testing (e.g., t-tests, calculating p-values) and the construction of confidence intervals.
### 3.6 Step 6: The Numerical Fallback (The System Safety Net)
This agent plays a critical role as the ultimate fallback for all other supervisors. Its objective is to ensure the system can always provide a high-quality approximate answer when a symbolic or exact solution is computationally intractable or mathematically impossible (e.g., per the Abel-Ruffini theorem).

| Agent Designation | Core Directive | Technical Specification & Key Algorithms |
| --- | --- | --- |
| Numerical Computation Utility (Tier 3) | Serve as the high-performance computational engine for all teams. This agent does not "reason"; it "crunches." | Must wrap a high-performance numerical library such as NumPy/SciPy or Julia. Acts as the fallback destination for any supervisor that cannot obtain a symbolic solution. |

With these agents specified, the final step is to ensure they are correctly integrated into the system's architecture.
## 4.0 System Integration & Wiring Protocol
Instantiating the agents is insufficient; they must be correctly connected to the system's "central nervous system"—the communication and discovery infrastructure established in Phase 0. The following protocols for integration are non-negotiable and ensure seamless scalability.
### 4.1 Directory Facilitator (DF) Registration
Every new Supervisor and Specialist agent created in Phase 2 **must** register its specific capabilities with the Directory Facilitator (DF). This registration must include both the service name and key properties that describe its function, allowing for precise service discovery.
**Example:** The Integration Specialist registers service: math.calculus.integration with properties type:symbolic and algorithm:risch.
### 4.2 Dynamic Orchestration
Proper registration with the DF enables dynamic orchestration. Because the Tier 1 Orchestrator queries the DF in real-time to find available services, it will automatically "see" and be able to delegate tasks to the newly created agents without any modification to its core code. The Orchestrator's capabilities expand organically as new tools are added to its "rolodex," fulfilling the architectural promise of a modular, scalable system.
This dynamic integration completes the primary construction goals of Phase 2, leading to a new, more powerful system state.
## 5.0 Phase 2 Definition of Done: The "Fragile Genius"
Upon the successful completion of all development and integration tasks outlined in this specification, the system will have achieved the state of a "Fragile Genius." This deliverable represents a massive leap in computational power, but it also introduces inherent risks that must be acknowledged.
**The Genius:** The system now possesses immense and verifiable mathematical power. It can execute complex, multi-step tasks that were previously impossible, such as performing Singular Value Decompositions (SVDs), finding closed-form integrals for complex functions, and proving number theory lemmas using deterministic algorithms.
**The Fragility:** The system is now powerful but brittle. Its specialized agents lack robust precondition validation. A supervisor routing a negative number to a Logarithm Specialist will cause a component crash, as no systemic error-handling layer yet exists to intercept such invalid inputs. If the symbolic and numerical integration agents produce conflicting results, there is no higher-level mechanism to adjudicate the disagreement.
This fragility is an expected outcome of Phase 2. It explicitly necessitates the next major development cycle, **Phase 3**, which will focus on implementing the "Meta-Cognitive Middleware." This future phase will introduce the precondition validation, knowledge management, and conflict resolution systems required to stabilize this powerful but brittle workforce.
