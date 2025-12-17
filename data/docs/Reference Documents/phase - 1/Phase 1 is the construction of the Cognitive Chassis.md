<!-- Converted from: Phase 1 is the construction of the Cognitive Chassis.docx -->

Phase 1 is the construction of the Cognitive Chassis. The objective here is not to build a system that can solve every mathematical problem, but to build a system that can legally and verifiably solve a single problem without hallucinating.
You are moving from the static infrastructure of Phase 0 (the Blackboard and FIPA protocols) to the first dynamic "heartbeat" of the system. This phase establishes the Orchestrator-Prover-Verifier loop, ensuring that from the very first moment of operation, neural creativity is shackled to symbolic rigor.
Here is the expanded, step-by-step technical specification for Phase 1: The Cognitive Chassis.
- 
Step 1: The Gatekeepers (The Problem Analysis Team)
Objective: Construct the interface that sanitizes and structures chaotic natural language into strict mathematical objects before the Orchestrator ever sees them. This prevents the "Garbage In, Garbage Out" failure mode.
- Action 1.1: The Syntax Parser & Autoformalizer
    ◦ Directive: Implement an agent specialized in translating natural language (e.g., "Find the derivative of x squared") and LaTeX into the OMDoc/OpenMath standards established in Phase 0.
    ◦ Architecture: This agent functions as the system's "transducer." It must parse the input text and output a structured expression tree. For example, it converts "integral of x" into an OpenMath object ``. This ensures downstream agents receive semantic objects, not text strings [1], [2].
- Action 1.2: The Structure Recognizer
    ◦ Directive: Implement the meta-classifier that tags the problem type.
    ◦ Logic: This agent does not solve; it categorizes. It must distinguish between Computation ("Calculate this"), Proof ("Show that..."), and Optimization ("Find the maximum..."). This tag is appended to the problem metadata on the Blackboard, which the Orchestrator will later use for routing logic [2], [3].
- 
Step 2: The Central Nervous System (The Main Orchestrator)
Objective: Instantiate the Tier 1 agent. This is the "General Contractor" whose sole job is management, enforcing the strict separation of Problem Understanding from Problem Solving.
- Action 2.1: The Decomposition Engine
    ◦ Directive: Program the Orchestrator with Hierarchical Task Network (HTN) logic. It must be capable of breaking a request into sub-goals.
    ◦ Constraint: You must hard-code a "Non-Intervention" directive. The Orchestrator is strictly forbidden from performing calculations. If it detects a request like "2+2", it must delegate, never compute. This enforces the architectural discipline required for scaling [4], [5].
- Action 2.2: The Routing Logic (The Rolodex)
    ◦ Directive: Connect the Orchestrator to the Directory Facilitator (DF) built in Phase 0.
    ◦ Mechanism: When the Orchestrator identifies a "Calculus" tag (from Step 1), it queries the DF for available agents with that capability. Currently, it will only find the "Pilot Solver" (Step 3), but this dynamic lookup ensures that when you add 50 agents in Phase 2, the Orchestrator detects them automatically without code changes [6], [7].
- 
Step 3: The Pilot Solver (The Symbolic Wrapper)
Objective: Create a temporary "stand-in" for the future workforce. We need a functional worker to test the pipeline, even before we build the specialized Tier 2 Supervisors.
- Action 3.1: The SymPy Wrapper Agent
    ◦ Directive: Encapsulate a robust Computer Algebra System (CAS), specifically SymPy, inside a standard agent shell.
    ◦ Function: This agent acts as the "Prover" or "Executor." It receives OMDoc inputs from the Blackboard, executes deterministic symbolic operations (like sympy.diff or sympy.integrate), and posts the result back to the Blackboard.
    ◦ Strategic Purpose: This serves as the "tracer bullet." It proves that a mathematical payload can travel from User
rightarrow Orchestrator
rightarrow Blackboard
rightarrow Solver and back, verifying the plumbing of the entire system [1], [8].
- 
Step 4: The Immune System (The Verification Core)
Objective: Implement the Ax-Prover pattern immediately. This is the most critical step for preventing hallucination. No result from the Pilot Solver is allowed to leave the system until this team stamps it "Approved."
- Action 4.1: The Logic Checker
    ◦ Directive: Build a rule-based agent that inspects the logical flow of the solution.
    ◦ Logic: It checks for "illegal moves," such as dividing by a variable without confirming it is non-zero, or applying a real-domain logarithm to a negative number. This addresses the "Assumption Gap" early [9], [10].
- Action 4.2: The Formal Verifier Wrapper
    ◦ Directive: Wrap a formal theorem prover (e.g., Lean 4, Coq, or Isabelle) into a "Verifier Agent."
    ◦ The Neural-Symbolic Loop: Configure the system so that the Pilot Solver's output is treated as a "candidate proof." The Verifier Agent attempts to compile this candidate. * If it compiles: The result is marked "Verified" and released to the user. * If it fails: An error flag is raised on the Blackboard, triggering a feedback loop to the Orchestrator to retry [11], [12], [13].
- 
Step 5: The "First Breath" (Integration & Testing)
Objective: Run the first end-to-end trace to validate the Cognitive Chassis.
- The Test Case: Submit the query: "Calculate the derivative of x
2
 +1."
    1. Analysis Team: Parses text
rightarrow OMDoc object ``. Tags as "Calculus/Computation".
    2. Orchestrator: Reads tag, looks up "Calculus" service in DF, finds Pilot Solver. Posts task to Blackboard.
    3. Pilot Solver: Subscribes to task. Calls sympy.diff(x**2 + 1). Result: 2*x. Posts to Blackboard.
    4. Verifier: Intercepts result. Checks constraints. Marks "Valid."
    5. Orchestrator: Retrieves valid result, converts to natural language, outputs "The answer is 2x."
- Phase 1 Deliverable:**At the end of Phase 1, you have a system that is mathematically limited (dependent on SymPy) but architecturally complete. You have successfully separated planning from execution and intuition from verification. You are now ready to replace the single "Pilot Solver" with the massive, specialized workforce of Phase 2.