<!-- Converted from: Phase 0 Coding Strategy_ Architecting the Foundational Infrastructure for a Multi-Agent Collective.docx -->

# Phase 0 Coding Strategy: Architecting the Foundational Infrastructure for a Multi-Agent Collective

## 1.0 Strategic Mandate: Building the Digital Bedrock

This initial phase of development is not about solving mathematical problems, but about architecting the fundamental rules of the system's reality. It is a strategic mandate to codify the laws of physics, the civic infrastructure, and the legal code of a digital society before its first inhabitants arrive. We are, in effect, building the city before the citizens arrive, establishing an immutable foundation upon which a future multi-agent collective can thrive.

The ultimate goal of this project is to build a system capable of supporting a thriving collective of 40-50 specialized agents collaborating to solve complex mathematical problems. However, this entire digital society must exist on a specific physical machine, and its architecture must be calibrated to respect the hard limits of its hardware. The primary challenge, therefore, is to engineer a system that can scale in intelligence without violating its physical constraints.

The non-negotiable hardware foundation that defines these constraints is detailed below:

Component	Specification CPU	AMD Ryzen 7 8700F System RAM	32 GB GPU	NVIDIA GeForce RTX 4060 Dedicated VRAM	8 GB

This hardware profile dictates every architectural decision that follows, with the single most critical constraint—the VRAM bottleneck—shaping the very laws that govern our system's existence.

## 2.0 The Laws of Physics: Calibrating to Hardware Reality

Resource scarcity is the most fundamental law of this digital society. Before a single line of problem-solving code is written, the Phase 0 architecture must be made ruthlessly efficient from the start. This requires confronting and designing for the two primary bottlenecks inherent in the target hardware: the severe limitations on VRAM and the finite capacity of the model's context window.



## 2.1 The VRAM Bottleneck and the "One-Model-At-A-Time" Mandate

The Core Problem: A single 7-billion parameter Large Language Model (LLM) requires approximately 5-6GB of VRAM even when quantized. The target system's NVIDIA GeForce RTX 4060, with its 8GB of dedicated VRAM, can barely hold one active reasoning agent at any given moment. This physical reality makes the concurrent operation of parallel cognitive agents physically impossible.

The Architectural Solution: To address this, the Phase 0 mandate is to implement a Stateful Serialization Protocol. This protocol ensures that the system lives within its means by preventing VRAM overflow.

Implementation Responsibility: The Agent Management System (AMS) must be coded to act as a critical gatekeeper, enforcing a strict "One-Model-At-A-Time" rule. This may involve swapping entire agent weights in and out of VRAM as required, or more efficiently, routing requests from lightweight agents to a single, central cognitive service that acts as a shared brain. Cognitive agents will exist in a queue, waiting for their turn to occupy the single active "workstation" in VRAM.

## 2.2 The Token Economy: Preserving the Context Window

The Associated Problem: Passing full, raw text conversation histories between agents is a grossly inefficient practice. This approach rapidly bloats the context window, consumes precious system RAM, degrades performance, and creates a significant risk of "out of memory" (OOM) crashes.

The Protocol-Level Solution: The system must enforce a strict token economy from its inception. The following protocols are non-negotiable:

Agents are forbidden from passing raw text history to one another. Communication must be conducted by passing compressed OMDoc mathematical state objects, conveying only the essential mathematical state and not conversational fluff.
The FIPA-ACL implementation must use Mandatory Conversation IDs. This mechanism allows agents to track specific problem-solving threads and reference prior context without passing redundant historical data in every message, thus conserving the context window.

These hardware-aware protocols are the foundational physics of our system, and they will be enforced by a set of dedicated infrastructural agents.

## 3.0 The Civic Infrastructure: Implementing the "Silent" Governance Agents

Before any problem-solving "mathematician" agents are instantiated, the system requires a class of "bureaucrat" agents to manage the city itself. These agents are computationally active and essential for the society's function, but they produce no mathematical output. They are the silent, foundational infrastructure that makes collaboration possible. This "Triumvirate of System Management" forms the core of the system's civic operations.

Agent	Role & Analogy	Core Function & Type Agent Management System (AMS)	The "City Hall" or "God Agent"	Manages agent lifecycles (create, kill, suspend). Critically, it monitors VRAM/RAM usage to enforce the one-model rule. It is the gatekeeper of system resources. Type: Simple Reflex Agent. Directory Facilitator (DF)	The "Yellow Pages" or "Service Registry"	Provides a dynamic lookup for agent services. Agents register their capabilities (e.g., service: integration), allowing for dynamic discovery by other agents. Type: Model-Based Reflex Agent. Agent Communication Channel (ACC)	The "Postmaster"	Guarantees the routing of FIPA-ACL messages between agents. It is responsible for queuing messages for agents that are currently inactive or swapped out of VRAM. Type: Transport/Routing Agent.

With these civic agents in place to manage the system, we must define the unambiguous rules that govern how they, and all future agents, interact.

## 4.0 The Official Language & Legal Code: Architecting Unambiguous Communication

To prevent a "Tower of Babel" scenario—where capable agents operate in isolation, unable to understand one another—agent communication cannot be based on ambiguous natural language. The Phase 0 mandate requires the establishment of both a formal language for expressing mathematical concepts and a legal framework for governing interactions and ensuring explicit intent.

## 4.1 The Lingua Franca: OMDoc for Semantic Precision

The Problem: Raw text, such as the string $x^2$, lacks true semantic meaning. It conveys presentation—how a formula looks—but not its mathematical content. This ambiguity is unacceptable for a system requiring precision.

The Technical Standard: All inter-agent communication must use the OMDoc (Open Mathematical Documents) standard. Its implementation will adhere to the following three-layer schema, which is a non-negotiable requirement for ensuring semantic precision:

Object Level: Encodes formulae, capturing specific variables and operations like x^2 + y.
Statement Level: Encodes definitions, theorems, and proofs as distinct logical entities with verifiable meaning.
Theory Level: Encodes the modular mathematical theories (e.g., "Calculus") that provide context for the statements and objects.

## 4.2 The Rule of Law: FIPA-ACL for Explicit Intent

The Problem: The content of a message is insufficient for clear communication. An agent receiving a message must know the intent behind it. Is it a request for information? An order to perform a task? A confirmation that a task is complete? Without this clarity, interactions are inefficient and prone to error.

The Legal Framework: The system will implement the FIPA-ACL (Agent Communication Language) protocol, which is based on Speech Act Theory. This framework treats every message as a formal, binding action, not just an exchange of information.

Two mechanisms are critical to this implementation:

The 'Performative' Field: This mandatory field in every FIPA-ACL message makes the sender's intent explicit and binding. Performatives like REQUEST, INFORM, or REFUSE turn a simple message into a formal action, eliminating ambiguity about the sender's purpose.
Mandatory Conversation IDs: This mechanism allows agents to track specific problem-solving threads across multiple asynchronous interactions. By referencing a unique conversation ID, an agent can link a new message to a prior request without needing to pass the entire redundant conversational history, thereby conserving the precious context window.

With the rules of communication codified, the final piece of foundational architecture is the system for shared knowledge.

## 5.0 The Public Memory: Building a Collective Consciousness

For a collective to be truly intelligent, its members cannot be stateless entities operating in a vacuum. They must be able to contribute to and draw from a shared pool of knowledge, successes, and failures. This collective consciousness is architected as a two-part memory system: a dynamic workspace for active collaboration and a long-term archive for institutional learning.

Memory Component	Function, Mechanism, & Implementation Notes The Blackboard (Shared Workspace)	Functionally, it is a central workspace for posting partial results and lemmas. Its mechanism is a Publish-Subscribe system, enabling emergent collaboration where agents can subscribe to relevant data updates (e.g., a Geometry agent subscribing to updates on variable 'x' from an Algebra agent). The Vector Database (Long-Term Archive)	Serves as the prerequisite infrastructure for Retrieval-Augmented Generation (RAG) by indexing mathematical "thought traces" and theorems, allowing the system to recognize recurring problem patterns over time. Implementation is mandated to use a lightweight store (e.g., Milvus, Chroma) to conserve system RAM.

This two-part memory architecture serves as the collective's brain; now we must define the blueprint for the individual agent's mind.

## 6.0 The Cognitive Blueprint: The BDI Control Loop for Future Citizens

The cognitive agents that will eventually inhabit this system cannot be simple, reactive scripts; they must be deliberative entities capable of reasoning and planning. Therefore, Phase 0 must define the internal "operating system" that all future cognitive agents will inherit, ensuring a consistent and predictable model of rational behavior.

The official Phase 0 mandate is that all future cognitive agents will be built on the Belief-Desire-Intention (BDI) control loop template. This framework provides a structured process for reasoning and decision-making.

The BDI control loop is composed of three key components:

Beliefs (B): This represents the agent's current knowledge and understanding of the world. It is the agent's internal model of reality (e.g., "The value of x is 5.").
Desires (D): This represents the agent's ultimate, high-level goals. These are the objectives the agent wishes to achieve (e.g., "I want to solve this integral.").
Intentions (I): This represents the agent's committed plan of action. After deliberation, an intention is the specific, chosen course of action the agent will pursue to satisfy a desire (e.g., "I will apply the Risch Algorithm.").

The strategic significance of this architecture is that it critically separates deliberation (the process of assessing beliefs and desires to choose a plan) from execution (the act of carrying out the plan). This separation is essential for managing the complexity of high-level mathematical reasoning.

## 7.0 Phase 0 Definition of Done: Computationally Alive, Mathematically Inert

At the conclusion of a successful Phase 0, the system is fully operational but has not yet solved a single mathematical problem. It is computationally alive but mathematically inert. We have built the city, but the streets are empty. This state is not a failure but the intended outcome, signifying that a robust, stable, and resource-aware foundation is ready for its first inhabitants.

The completion criteria for this phase are as follows:

The Office Building is Built: The core civic infrastructure (AMS, DF, ACC) is deployed and running.
The City Manager is Hired: The AMS is actively monitoring system resources to enforce hardware constraints.
The Laws are Written: FIPA-ACL and OMDoc protocols are implemented and govern all potential interactions.
The Library is Open: The Blackboard and Vector Database are deployed and ready to store and retrieve knowledge.

With this immutable bedrock in place, the stage is set for Phase 1. We can now proceed with the confidence that the system is prepared to safely instantiate its first cognitive agents: the Tier 1 Orchestrator, the Autoformalization Pipeline, and the first Specialist Agents.
