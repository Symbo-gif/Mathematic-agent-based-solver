# SYMBO_AGENTIC_REASONERS Developer Guide
## Agent-based Mathematical Deduction Engine

This guide explains the reorganized SYMBO_AGENTIC_REASONERS project structure for developers.

---

## Quick Start

```bash
# Install in development mode
pip install -e .

# Verify installation
python -c "from symbo_agentic_reasoners.core import Blackboard, BDIAgent; print('OK')"

# Run tests
python -m pytest tests/ -v
```

---

## Project Structure Overview

```
src/symbo_agentic_reasoners/              # Main package
├── core/              # Foundation (BDI, Blackboard, Orchestrator)
├── protocols/         # Communication (FIPA-ACL)
├── infrastructure/    # Services (AMS, ACC, DF)
├── agents/            # Agent hierarchy
│   ├── supervisors/   # Tier 2: Domain coordinators
│   └── specialists/   # Tier 3: Task agents
├── verification/      # Formal verification
├── middleware/        # Meta-cognitive (Phase 3-4)
├── solvers/           # Math engines (SymPy wrapper)
├── discovery/         # Discovery engine (Phase 6)
├── optimization/      # Performance (Phase 5)
└── utils/             # Utilities & config
```

---

## Import Conventions

### Core Components
```python
from symbo_agentic_reasoners.core import (
    OMObject, OMDocStatement, MathOperator,
    create_variable, create_number, create_operation,
    BDIAgent, Belief, Desire, Intention,
    Blackboard, BlackboardEntry, EntryStatus, EntryType,
)
```

### Protocols
```python
from symbo_agentic_reasoners.protocols import (
    FIPAMessage, Performative, FIPAProtocol,
    create_request, create_inform, create_failure,
)
```

### Infrastructure
```python
from symbo_agentic_reasoners.infrastructure import (
    AgentManagementSystem, AgentRecord, AgentStatus,
    DirectoryFacilitator, create_service_registration,
    AgentCommunicationChannel, MessageEnvelope,
)
```

### Agents
```python
# Supervisors (Tier 2)
from symbo_agentic_reasoners.agents.supervisors.algebra_supervisor import AlgebraSupervisor
from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor

# Specialists (Tier 3)
from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import ArithmeticSpecialist
from symbo_agentic_reasoners.agents.specialists.calculus.integration_specialist import IntegrationSpecialist
```

### System
```python
from symbo_agentic_reasoners.core.system import Phase0System
```

---

## Directory Mapping

| Old Location | New Location | Purpose |
|-------------|--------------|---------|
| `symbo_agentic_reasoners_phase0/core/` | `src/symbo_agentic_reasoners/core/` | BDI, OMDoc |
| `symbo_agentic_reasoners_phase0/memory/` | `src/symbo_agentic_reasoners/core/` | Blackboard, VectorDB |
| `symbo_agentic_reasoners_phase0/infrastructure/` | `src/symbo_agentic_reasoners/infrastructure/` | AMS, ACC, DF |
| `symbo_agentic_reasoners_phase1/orchestrator/` | `src/symbo_agentic_reasoners/core/` | Main Orchestrator |
| `symbo_agentic_reasoners_phase1/verification/` | `src/symbo_agentic_reasoners/verification/` | Verification Core |
| `symbo_agentic_reasoners_phase1/solvers/` | `src/symbo_agentic_reasoners/solvers/` | Pilot Solver |
| `symbo_agentic_reasoners_phase2/supervisors/` | `src/symbo_agentic_reasoners/agents/supervisors/` | Domain Supervisors |
| `symbo_agentic_reasoners_phase2/agents/` | `src/symbo_agentic_reasoners/agents/specialists/` | Specialists |
| `symbo_agentic_reasoners_phase3/` | `src/symbo_agentic_reasoners/middleware/` | Meta-cognitive |
| `symbo_agentic_reasoners_phase4/` | `src/symbo_agentic_reasoners/middleware/` | Self-correction |
| `symbo_agentic_reasoners_phase5/` | `src/symbo_agentic_reasoners/optimization/` | Distillation, SymboLLM |
| `symbo_agentic_reasoners_phase6/` | `src/symbo_agentic_reasoners/discovery/` | Discovery Engine |
| `thought_traces/` | `data/traces/thought/` | Agent reasoning |
| `audit_thought_traces/` | `data/traces/audit/` | Audit logs |
| `Archive assessments/` | `docs/assessments/archive/` | Historical |
| `critical assessments/` | `docs/assessments/critical/` | Current |

---

## Data Paths

Use the utility constants for consistent paths:

```python
from symbo_agentic_reasoners.utils import PROJECT_ROOT, DATA_DIR, TRACE_DIR, OUTPUT_DIR

# Write traces to correct location
trace_file = TRACE_DIR / "thought" / "my_trace.json"

# Output files
output_file = OUTPUT_DIR / "results.txt"
```

---

## Agent Hierarchy

```
Tier 1: Main Orchestrator
    └── symbo_agentic_reasoners.core.orchestrator.MainOrchestrator

Tier 2: Domain Supervisors
    ├── symbo_agentic_reasoners.agents.supervisors.algebra_supervisor
    ├── symbo_agentic_reasoners.agents.supervisors.calculus_supervisor
    ├── symbo_agentic_reasoners.agents.supervisors.linalg_supervisor
    └── symbo_agentic_reasoners.agents.supervisors.stats_supervisor

Tier 3: Task Specialists
    ├── algebra/
    │   ├── arithmetic_specialist
    │   ├── polynomial_specialist
    │   └── number_theory_specialist
    ├── calculus/
    │   ├── differentiation_specialist
    │   ├── integration_specialist
    │   ├── ode_solver
    │   └── series_specialist
    ├── linear_algebra/
    ├── discrete_math/
    ├── statistics/
    └── numerical/
```

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_phase1.py -v

# Run with coverage
python -m pytest tests/ --cov=symbo_agentic_reasoners --cov-report=html
```

---

## Common Tasks

### Creating a New Agent

```python
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure import DirectoryFacilitator

class MyAgent(BDIAgent):
    def __init__(self, agent_id: str, df: DirectoryFacilitator):
        super().__init__(agent_id)
        self.df = df

    def update_beliefs(self):
        # Read from blackboard/messages
        pass

    def deliberate(self) -> list[Intention]:
        # Generate plans based on beliefs/desires
        return []

    def execute_step(self, intention: Intention):
        # Execute one step, NEVER compute directly
        pass
```

### Using the Blackboard

```python
from symbo_agentic_reasoners.core import Blackboard, create_entry, EntryType, EntryStatus

bb = Blackboard()

# Subscribe to updates
def on_task(entry):
    print(f"New task: {entry}")

bb.subscribe("my_agent", ["math_task"], on_task)

# Post an entry
entry = create_entry(
    entry_type=EntryType.TASK,
    content=my_omdoc_content,
    author_agent="orchestrator",
    conversation_id="conv_123",
    tags=["math_task", "algebra"]
)
bb.post(entry)
```

### Sending FIPA-ACL Messages

```python
from symbo_agentic_reasoners.protocols import create_request, Performative
from symbo_agentic_reasoners.core import create_variable

# Create a request
msg = create_request(
    sender="orchestrator",
    receiver="algebra_supervisor",
    content=create_variable("x")  # Must be OMDoc!
)

# Create a reply
reply = msg.create_reply(
    performative=Performative.INFORM,
    content=result_content
)
```

---

## Legacy Code Reference

The original `symbo_agentic_reasoners_phase*` folders remain in the repository for reference. They are NOT part of the installed package. If you need to understand historical implementation, refer to:

- `symbo_agentic_reasoners_phase0/` - Original Phase 0 implementation
- `symbo_agentic_reasoners_phase1/` - Original Phase 1 implementation
- ... etc.

---

## Version History

- **v0.6.0** (2025-12-06): Major reorganization to src-layout
- **v0.1.0**: Initial multi-phase implementation
