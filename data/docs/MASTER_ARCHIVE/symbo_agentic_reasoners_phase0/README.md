# Phase 0: Foundational Infrastructure

**Status**: ✅ Complete - Computationally Alive, Mathematically Inert

## Overview

Phase 0 implements the foundational bedrock of the Autonomous Mathematical Discovery Engine (SYMBO_AGENTIC_REASONERS). This phase establishes the "laws of physics," civic infrastructure, and legal frameworks that govern the entire 65-agent system.

**Key Principle**: Phase 0 is not concerned with solving mathematical problems. It builds the city before the citizens arrive.

## Hardware Constraints

| Component | Specification | Impact |
|-----------|---------------|--------|
| CPU | AMD Ryzen 7 8700F (8-Core) | Multi-threading support |
| System RAM | 32 GB DDR5 | Limited - must reserve for LLM context |
| GPU | NVIDIA GeForce RTX 4060 | Enables local inference |
| **VRAM** | **8 GB GDDR6** | **CRITICAL BOTTLENECK** |

**The VRAM Bottleneck**: A 7B parameter LLM requires ~5-6GB VRAM when quantized. The RTX 4060 can hold **ONE** cognitive agent at a time. This constraint shapes the entire architecture.

## Architecture

### Step 1: Semantic Substrate (Lingua Franca)
**File**: [`core/omdoc_schema.py`](core/omdoc_schema.py)

Implements OMDoc (Open Mathematical Documents) and OpenMath standards for unambiguous mathematical communication.

**Three Layers**:
1. **Object Level**: Mathematical expressions (x², sin(θ), ∫f(x)dx)
2. **Statement Level**: Theorems, definitions, proofs
3. **Theory Level**: Modular mathematical contexts (Calculus, GroupTheory)

**Why**: Raw text "x²" lacks semantic meaning. OMDoc ensures precise mathematical semantics.

**Key Classes**:
- `OMObject`: Mathematical expression tree
- `OMDocStatement`: Theorem, definition, proof
- `OMDocTheory`: Mathematical theory container

### Step 2: Constitutional Law (FIPA-ACL Protocols)
**File**: [`core/fipa_acl.py`](core/fipa_acl.py)

Implements FIPA-ACL (Agent Communication Language) based on Speech Act Theory.

**Key Mechanisms**:
1. **Performatives**: Explicit intent (REQUEST, INFORM, QUERY, REFUSE, etc.)
2. **Conversation IDs**: Thread tracking without redundant history
3. **Content Encoding**: OMDoc only - raw text forbidden

**Why**: Message content alone is insufficient. Intent must be explicit.

**Key Classes**:
- `FIPAMessage`: Structured message with mandatory fields
- `Performative`: Speech act types
- Validation enforces OMDoc content

### Step 3: Active Memory Architecture
**Files**: [`memory/blackboard.py`](memory/blackboard.py), [`memory/vector_database.py`](memory/vector_database.py)

Two-part memory system for collective consciousness.

**Blackboard (Active Workspace)**:
- Centralized workspace for collaboration
- Publish-Subscribe mechanism
- Agents post partial results, subscribe to updates
- Enables emergent parallel problem-solving

**Vector Database (Long-Term Archive)**:
- Persistent knowledge storage
- Indexes mathematical "thought traces"
- Enables future RAG (Retrieval-Augmented Generation)
- Uses ChromaDB in persistent mode to conserve RAM

**Key Classes**:
- `Blackboard`: Pub/sub workspace
- `BlackboardEntry`: Task, lemma, partial result
- `VectorDatabase`: Persistent knowledge store

### Step 4: Bureaucratic Infrastructure Team
**Files**: [`infrastructure/ams.py`](infrastructure/ams.py), [`infrastructure/directory_facilitator.py`](infrastructure/directory_facilitator.py), [`infrastructure/acc.py`](infrastructure/acc.py)

Three "silent" agents that manage the system.

#### AMS: Agent Management System ("City Hall")
**Type**: Simple Reflex Agent

**Responsibilities**:
- Agent lifecycle management (create, activate, deactivate, kill)
- **Critical**: Enforces "One-Model-At-A-Time" rule
- Monitors VRAM usage via nvidia-smi
- Queues cognitive agents waiting for VRAM slot
- Prevents system crashes from resource overflow

#### DF: Directory Facilitator ("Yellow Pages")
**Type**: Model-Based Reflex Agent

**Responsibilities**:
- Service registry for dynamic agent discovery
- Agents register capabilities (e.g., service: integration, algorithm: risch)
- Enables discovery by capability, not by name
- Supports load balancing and graceful degradation

#### ACC: Agent Communication Channel ("Postmaster")
**Type**: Transport/Routing Agent

**Responsibilities**:
- Routes FIPA-ACL messages between agents
- Queues messages for inactive agents
- Delivers queued messages when agents activate
- Critical for "One-Model-At-A-Time" asynchronous operation

### Step 5: Cognitive Blueprint (BDI Framework)
**File**: [`core/bdi_agent.py`](core/bdi_agent.py)

Belief-Desire-Intention architecture for all future cognitive agents.

**Three Components**:
1. **Beliefs (B)**: Agent's knowledge about the world
   - Example: "This is a polynomial equation"
2. **Desires (D)**: Agent's high-level goals
   - Example: "I want to solve this integral"
3. **Intentions (I)**: Agent's committed plans
   - Example: "I will apply the Risch Algorithm"

**BDI Control Loop**:
1. PERCEIVE: Update beliefs from environment
2. DELIBERATE: Generate intentions from beliefs and desires
3. EXECUTE: Execute one step of current intention
4. Repeat

**Critical Principle**: BDI agents NEVER compute directly. They reason and delegate computation to tools.

**Key Classes**:
- `BDIAgent`: Abstract base class for all cognitive agents
- `Belief`: Knowledge about the world
- `Desire`: Goals to achieve
- `Intention`: Committed plans

## Phase 0 Definition of Done

At the conclusion of Phase 0, the system is **Computationally Alive, Mathematically Inert**.

### Checklist

| ✓ | Criterion | Verification |
|---|-----------|--------------|
| ✅ | **The Office Building is Built** | AMS, DF, ACC are deployed and responsive |
| ✅ | **The City Manager is Hired** | AMS monitors resources, enforces One-Model-At-A-Time |
| ✅ | **The Laws are Written** | FIPA-ACL and OMDoc enforced; raw text rejected |
| ✅ | **The Library is Open** | Blackboard pub/sub works; Vector DB stores/retrieves |

## Installation & Usage

### Prerequisites
```bash
# Required
pip install chromadb  # For vector database (optional but recommended)

# For VRAM monitoring (if NVIDIA GPU available)
# nvidia-smi should be available in PATH
```

### Quick Start
```python
from symbo_agentic_reasoners_phase0.phase0_system import Phase0System

# Initialize Phase 0 system
system = Phase0System()
system.start()

# Perform health check
health = system.health_check()

# Get statistics
system.print_statistics()

# Shutdown when done
system.shutdown()
```

### Running Tests
```bash
# Run system demonstration
cd symbo_agentic_reasoners_phase0
python phase0_system.py

# Run individual component demos
python core/omdoc_schema.py
python core/fipa_acl.py
python memory/blackboard.py
python infrastructure/ams.py
python infrastructure/directory_facilitator.py
python infrastructure/acc.py
python core/bdi_agent.py
```

## Project Structure

```
symbo_agentic_reasoners_phase0/
├── __init__.py                      # Package exports
├── README.md                        # This file
├── phase0_system.py                 # Integrated system
│
├── core/                            # Core protocols
│   ├── __init__.py
│   ├── omdoc_schema.py             # Step 1: OMDoc/OpenMath
│   ├── fipa_acl.py                 # Step 2: FIPA-ACL
│   └── bdi_agent.py                # Step 5: BDI Framework
│
├── infrastructure/                  # Infrastructure agents
│   ├── __init__.py
│   ├── ams.py                      # Agent Management System
│   ├── directory_facilitator.py    # Service Registry
│   └── acc.py                      # Message Routing
│
└── memory/                          # Memory systems
    ├── __init__.py
    ├── blackboard.py               # Active workspace
    └── vector_database.py          # Long-term memory
```

## Reference Documentation

All implementation based on official SYMBO_AGENTIC_REASONERS documentation:

- **Phase_0_Build_Order_Breakdown.md**: Step-by-step implementation guide with code
- **Phase 0 Coding Strategy**: Architectural vision and strategic mandate
- **Phase 0_ Infrastructural Agents and Hardware Calibration**: Hardware constraints
- **phases 0-6 for the Autonomous Mathematical Discovery Engine.md**: Complete roadmap
- **Phased Evolution of the 65-Agent System Architecture.md**: Full 65-agent breakdown

## Key Concepts

### The "One-Model-At-A-Time" Mandate
With only 8GB VRAM, only ONE cognitive agent can be active at any time. AMS enforces this through:
- VRAM monitoring
- Agent queueing
- Automatic swapping

### Token Economy
Agents cannot pass raw conversation history (context window bloat). Instead:
- Use compressed OMDoc mathematical state
- Reference conversation IDs for threading
- Preserve precious context window

### Stateful Serialization Protocol
Agents exist in three states:
- **INACTIVE**: Registered but not in VRAM
- **QUEUED**: Waiting for VRAM slot
- **ACTIVE**: Currently occupying VRAM slot

### The Tower of Babel Problem
Without OMDoc, capable agents cannot communicate mathematical nuance. OMDoc is the shared semantic substrate that prevents isolation.

## Next Phase: Phase 1 - Cognitive Chassis

With Phase 0 complete, the system is ready for Phase 1:

**Phase 1 Agents** (6 cognitive agents):
1. **Orchestrator**: High-level problem decomposition
2. **CNS (Central Nervous System)**: VRAM management coordinator
3. **Algebra Specialist**: Algebraic manipulation
4. **Calculus Specialist**: Differentiation and integration
5. **Numerical Fallback**: Numerical methods when symbolic fails
6. **Verification Agent**: Solution verification

Phase 1 transforms the system from "mathematically inert" to capable of solving basic mathematical problems.

## License & Attribution

Part of the Autonomous Mathematical Discovery Engine (SYMBO_AGENTIC_REASONERS) project.

**Hardware Target**: AMD Ryzen 7 8700F, RTX 4060 (8GB VRAM), 32GB RAM

**Version**: Phase 0.1.0

---

*"Phase 0 is not merely a preparatory step; it is the construction of the digital ontology and legislative framework that governs the entire system's reality."*
