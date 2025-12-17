# Core Components

The foundational infrastructure and cognitive architecture for the SYMBO mathematical reasoning system.

## Overview

The `core` directory contains the essential components that power the entire multi-agent system, including the BDI cognitive framework, the shared Blackboard workspace, native mathematical engines, and the main orchestrator. These modules form the "operating system" on which all agents run.

**Module Count**: 26 modules
**Total Lines**: ~20,000+ LOC
**Key Component**: Native Calculus Engine (13,213+ lines)

## Architecture Pattern

The core follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│         Orchestrator (Coordination)         │
├─────────────────────────────────────────────┤
│    BDI Framework (Cognitive Architecture)   │
├─────────────────────────────────────────────┤
│   Blackboard (Shared Memory & Messaging)    │
├─────────────────────────────────────────────┤
│  Native Engines (Mathematical Operations)   │
├─────────────────────────────────────────────┤
│   Parsers & Utilities (Infrastructure)      │
└─────────────────────────────────────────────┘
```

## Key Components

### 1. BDI Cognitive Framework

#### bdi_agent.py (765 lines)
**Purpose**: Belief-Desire-Intention cognitive architecture for all agents

**Key Classes**:
- `Belief` - Knowledge representation with confidence levels
- `Desire` - Goals and objectives with priorities
- `Intention` - Committed plans with execution status
- `BDIAgent` - Abstract base class for all cognitive agents

**BDI Control Loop**:
1. **PERCEIVE**: Update beliefs from environment (Blackboard, messages)
2. **DELIBERATE**: Compare beliefs against desires to generate intentions
3. **MEANS-END**: Select concrete plans to achieve intentions
4. **EXECUTE**: Execute one step of current intention
5. **Repeat**

**Usage**:
```python
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Belief, Desire

class MyAgent(BDIAgent):
    def perceive(self):
        # Update beliefs from environment
        pass

    def deliberate(self):
        # Form intentions based on beliefs and desires
        pass

    def execute_intention(self):
        # Execute current plan
        pass
```

**Design Philosophy**:
- **NO COMPUTATION**: Cognitive agents NEVER compute directly - they delegate
- **Rational Deliberation**: Separation of "what to do" from "how to do it"
- **Consistent Behavior**: All agents inherit same cognitive model

---

### 2. Blackboard System

#### blackboard.py (605 lines)
**Purpose**: Centralized workspace for agent collaboration with pub-sub messaging

**Key Classes**:
- `EntryType` - TASK, SUBTASK, LEMMA, PARTIAL_RESULT, PROOF_STEP
- `EntryStatus` - PENDING, IN_PROGRESS, COMPLETED, FAILED, VERIFIED
- `BlackboardEntry` - Individual workspace entries
- `Blackboard` - Main blackboard with subscription management

**Core Features**:
- **Publish-Subscribe**: Agents subscribe to tags, get notified on matches
- **Entry Lifecycle**: Track status from creation to verification
- **Hierarchical Structure**: Entries can have parent-child relationships
- **Thread-Safe**: Concurrent access from multiple agents

**Usage**:
```python
from symbo_agentic_reasoners.core.blackboard import Blackboard, EntryType

blackboard = Blackboard()

# Post a task
entry_id = blackboard.post_entry(
    entry_type=EntryType.TASK,
    content="solve x^2 = 4",
    tags=["algebra", "quadratic"],
    agent_id="orchestrator"
)

# Subscribe to tasks
def on_task(entry):
    print(f"New task: {entry.content}")

blackboard.subscribe(tags=["algebra"], callback=on_task)
```

**Why This Matters**:
Enables emergent collaborative problem-solving. Agents work together by posting partial results and subscribing to relevant updates, creating a "collective consciousness."

---

### 3. Main Orchestrator

#### orchestrator.py (1,262 lines)
**Purpose**: Tier 1 coordinator - the "general contractor" of the system

**Key Class**: `MainOrchestrator`

**Core Responsibilities**:
1. **Problem Decomposition**: Break complex problems into subtasks
2. **Dynamic Routing**: Route subtasks to appropriate supervisors
3. **Result Synthesis**: Combine partial results into final solution
4. **Knowledge Integration**: Leverage meta-learning and caching

**CRITICAL CONSTRAINT**:
**NON-INTERVENTION DIRECTIVE** - Orchestrator is FORBIDDEN from performing calculations. It delegates, never computes.

**Workflow**:
```
Problem Input
    ↓
[Analyze & Decompose]
    ↓
[Route to Supervisors] → Supervisor 1, Supervisor 2, ...
    ↓
[Collect Results]
    ↓
[Synthesize Solution]
    ↓
Final Solution
```

**Usage**:
```python
from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator

orchestrator = MainOrchestrator(
    agent_pool=pool,
    directory_facilitator=df,
    blackboard=blackboard
)

result = orchestrator.solve_problem("differentiate x^2 + 2x + 1")
```

---

### 4. Native Mathematical Engines

#### native_calculus.py (13,213+ lines)
**Purpose**: Complete calculus implementation without SymPy dependency

**Core Capabilities**:
- **Differentiation**: 7 differentiation rules (power, product, chain, etc.)
- **Integration**: 15+ integration strategies (substitution, parts, trigonometric, etc.)
- **Limits**: L'Hôpital's rule, infinity handling, indeterminate forms
- **Series**: Taylor series, power series, convergence tests
- **Special Functions**: Exponentials, logarithms, trigonometric

**Key Classes**:
- `NativeCalculusEngine` - Main engine
- `DifferentiationEngine` - Derivative computation
- `IntegrationEngine` - Integral computation
- `LimitEvaluator` - Limit evaluation
- `SeriesAnalyzer` - Series analysis

**Example**:
```python
from symbo_agentic_reasoners.core.native_calculus import NativeCalculusEngine

engine = NativeCalculusEngine()

# Differentiate
result = engine.differentiate("x^2 + 2*x + 1", "x")
# Result: "2*x + 2"

# Integrate
result = engine.integrate("sin(x)", "x")
# Result: "-cos(x) + C"

# Evaluate limit
result = engine.limit("sin(x)/x", "x", 0)
# Result: 1
```

**Design Philosophy**:
Native implementation provides full transparency, educational value, and eliminates external dependencies for agents.

---

#### native_symbolic.py
**Purpose**: Symbolic expression manipulation without SymPy

**Features**:
- Expression parsing and simplification
- Algebraic operations (expand, factor, collect)
- Substitution and evaluation
- Polynomial operations

---

#### native_complex.py
**Purpose**: Complex number operations

**Features**:
- Complex arithmetic
- Polar/rectangular conversion
- Complex functions (exp, log, trig)
- Argument and modulus

---

#### number_theory_native.py
**Purpose**: Number theory operations

**Features**:
- Prime factorization
- GCD/LCM computation
- Modular arithmetic
- Diophantine equations

---

### 5. Solver Engine

#### solver_engine.py (1,676 lines)
**Purpose**: Problem routing and domain detection

**Key Class**: `SolverEngine`

**Core Functions**:
- **Domain Detection**: Identify mathematical domain (calculus, algebra, etc.)
- **Problem Routing**: Direct problems to appropriate supervisors
- **Fallback Coordination**: Handle cases where primary solver fails
- **Result Verification**: Coordinate verification strategies

**Usage**:
```python
from symbo_agentic_reasoners.core.solver_engine import SolverEngine

engine = SolverEngine()
domain = engine.detect_domain("differentiate x^2")
# Returns: MathDomain.Calculus

supervisor = engine.route_to_supervisor(domain)
# Returns: CalculusSupervisor instance
```

---

### 6. Parsing & Analysis

#### safe_parser.py
**Purpose**: Secure expression parsing with sandboxing

**Features**:
- Safe evaluation (no arbitrary code execution)
- Syntax validation
- Expression tree construction
- Error handling

---

#### semantic_parser.py
**Purpose**: Extract semantic meaning from expressions

**Features**:
- Variable identification
- Operator extraction
- Dependency analysis
- Domain hints

---

#### expression_analyzer.py
**Purpose**: Deep analysis of mathematical expressions

**Features**:
- Complexity assessment
- Subexpression identification
- Optimization opportunities
- Transformation suggestions

---

### 7. Communication & State

#### message_bus.py
**Purpose**: Asynchronous message routing between agents

**Features**:
- FIPA-ACL protocol support
- Message queuing
- Topic-based routing
- Delivery guarantees

---

#### agent_communication.py
**Purpose**: High-level agent communication abstractions

**Features**:
- Request/response patterns
- Broadcast messaging
- Negotiation protocols
- Conversation management

---

#### state_manager.py
**Purpose**: System state persistence and recovery

**Features**:
- State snapshots
- Rollback capabilities
- State validation
- Recovery procedures

---

### 8. Supporting Components

#### error_handler.py
**Purpose**: Centralized error handling and recovery

**Features**:
- Error classification
- Recovery strategies
- Error logging
- Graceful degradation

---

#### fallback_coordinator.py
**Purpose**: Coordinate fallback strategies when primary solutions fail

**Features**:
- Strategy selection
- Fallback chains
- Success tracking
- Learning from failures

---

#### fallback_tracker.py
**Purpose**: Track fallback usage and success rates

---

#### input_normalizer.py
**Purpose**: Normalize user input into standard form

**Features**:
- Format standardization
- Unit conversion
- Notation normalization
- Validation

---

#### resource_coordinator.py
**Purpose**: Coordinate resource usage across agents

**Features**:
- Resource allocation
- Priority management
- Conflict resolution
- Load balancing

---

#### vector_database.py
**Purpose**: Semantic search over mathematical knowledge

**Features**:
- Embedding generation
- Similarity search
- Knowledge retrieval
- Pattern matching

---

#### omdoc_schema.py
**Purpose**: OpenMath Document (OMDoc) representation

**Features**:
- Mathematical object representation
- Semantic markup
- Knowledge exchange format
- Proof representation

---

#### math_solver.py
**Purpose**: High-level solver interface

**Features**:
- Unified solving API
- Strategy selection
- Result formatting
- Error handling

---

#### system.py
**Purpose**: Main system entry point

**Features**:
- System initialization
- Component coordination
- Configuration management
- Shutdown procedures

---

## Directory Structure

```
core/
├── __init__.py
│
├── bdi_agent.py              # BDI cognitive framework (765 lines)
├── blackboard.py             # Shared workspace (605 lines)
├── orchestrator.py           # Main coordinator (1,262 lines)
│
├── native_calculus.py        # Calculus engine (13,213+ lines)
├── native_symbolic.py        # Symbolic operations
├── native_complex.py         # Complex number ops
├── number_theory_native.py   # Number theory
│
├── solver_engine.py          # Problem routing (1,676 lines)
├── safe_parser.py            # Secure parsing
├── semantic_parser.py        # Semantic analysis
├── expression_analyzer.py    # Expression analysis
│
├── message_bus.py            # Message routing
├── agent_communication.py    # Agent communication
├── state_manager.py          # State management
│
├── error_handler.py          # Error handling
├── fallback_coordinator.py   # Fallback strategies
├── fallback_tracker.py       # Fallback tracking
│
├── input_normalizer.py       # Input normalization
├── resource_coordinator.py   # Resource coordination
├── vector_database.py        # Semantic search
├── omdoc_schema.py          # OMDoc representation
│
├── math_solver.py           # High-level solver API
├── system.py                # System entry point
│
└── calculus/                # Modular calculus components
    └── (decomposed modules)
```

## Design Principles

### 1. NO SYMPY by Agents
All mathematical operations are implemented natively. SymPy may be used for verification only, never by agents for computation.

### 2. Separation of Concerns
- **BDI Framework**: Cognitive architecture
- **Blackboard**: Memory and communication
- **Engines**: Mathematical operations
- **Orchestrator**: Coordination only (no computation)

### 3. Cognitive Architecture
All agents inherit from `BDIAgent`, ensuring consistent rational behavior through the BDI control loop.

### 4. Transparency
Native implementations provide full visibility into mathematical operations, essential for educational applications and debugging.

### 5. Robustness
Comprehensive error handling, fallback strategies, and resource coordination ensure system reliability.

## Dependencies

**Internal**:
- `../infrastructure/` - AMS, Directory Facilitator, Agent Pool
- `../agents/` - Supervisors and Specialists
- `../middleware/` - Knowledge Management, Meta-Learning
- `../protocols/` - FIPA-ACL communication
- `../utils/` - Logging, utilities

**External**:
- `numpy` - Numerical operations
- `mpmath` - Arbitrary precision arithmetic
- `sympy` - Verification only (not used by agents)

## Usage Examples

### Basic System Setup
```python
from symbo_agentic_reasoners.core.system import SymboSystem

# Initialize complete system
system = SymboSystem()

# Solve a problem
result = system.solve("integrate sin(x) * cos(x) dx")
```

### Custom Orchestrator Configuration
```python
from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
from symbo_agentic_reasoners.core.blackboard import Blackboard
from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool

# Create components
blackboard = Blackboard()
pool = AgentPool(max_agents=100)
orchestrator = MainOrchestrator(
    blackboard=blackboard,
    agent_pool=pool,
    enable_knowledge_cache=True
)

# Solve with metadata
result = orchestrator.solve_problem(
    problem="differentiate x^3",
    context={'priority': 'high', 'timeout': 60}
)
```

### Direct Engine Usage
```python
from symbo_agentic_reasoners.core.native_calculus import NativeCalculusEngine

engine = NativeCalculusEngine()

# Differentiation
dx = engine.differentiate("x^2 * sin(x)", "x")

# Integration with strategy
integral = engine.integrate(
    expression="x^2 * exp(x)",
    variable="x",
    strategy="integration_by_parts"
)

# Limit
limit = engine.evaluate_limit(
    expression="(1 - cos(x)) / x^2",
    variable="x",
    point=0,
    method="lhopital"
)
```

## Testing

Core components have extensive test coverage:

```bash
# Test BDI framework
pytest tests/test_bdi_agent.py

# Test Blackboard
pytest tests/test_blackboard.py

# Test Orchestrator
pytest tests/test_orchestrator.py

# Test Native Calculus
pytest tests/test_calculus_specialists.py

# Test all core modules
pytest tests/test_core_modules_coverage.py
```

## Performance Characteristics

- **Orchestrator**: Sub-millisecond routing decisions
- **Blackboard**: Thread-safe concurrent access, 10,000+ ops/sec
- **Native Calculus**: 100-1000x slower than SymPy, but fully transparent
- **Message Bus**: Asynchronous, non-blocking

## Future Enhancements

1. **Native Calculus Decomposition**: Break 13K+ line file into modular components
2. **Parallel Orchestration**: Concurrent subtask execution
3. **Adaptive Routing**: Learn optimal routing from past problems
4. **Enhanced Caching**: Semantic similarity-based solution retrieval

## Related Components

- `../agents/` - Agent hierarchy using BDI framework
- `../infrastructure/` - AMS, Watchdog, Resource Governor
- `../middleware/` - Knowledge Management, Meta-Learning
- `../solvers/` - Domain-specific solver implementations

---

Generated by SYMBO Documentation System
Last Updated: 2025-12-14
