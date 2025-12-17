# Infrastructure Layer

Phase 0 foundational infrastructure - the "civic infrastructure" enabling agent lifecycle management, service discovery, and resource governance.

## Overview

The infrastructure layer provides the essential systems that enable multi-agent coordination: agent lifecycle management, service discovery, message routing, resource governance, and timeout enforcement. These components form the "operating system" on which the cognitive agents run.

**Phase**: Phase 0 - Infrastructure
**Module Count**: 11 modules
**Architecture Pattern**: Simple Reflex and Model-Based Reflex Agents

## Core Philosophy

The infrastructure layer follows the **Bureaucratic Infrastructure** pattern, where specialized "civic agents" manage system-wide concerns:

- **AMS (Agent Management System)**: "City Hall" - Agent lifecycle and VRAM enforcement
- **Directory Facilitator**: "Yellow Pages" - Service discovery and registration
- **ACC (Agent Communication Channel)**: "Postal Service" - Message routing
- **Watchdog**: "Health Inspector" - Timeout enforcement
- **Resource Governor**: "Power Grid Manager" - System-wide resource throttling

## Architecture Pattern

```
┌─────────────────────────────────────────────────┐
│         Application Agents                      │
│    (Orchestrator, Supervisors, Specialists)     │
└──────────────────┬──────────────────────────────┘
                   │
    ┌──────────────┼──────────────────┐
    │              │                  │
    ▼              ▼                  ▼
┌────────┐  ┌──────────┐      ┌───────────┐
│  AMS   │  │    DF    │      │  Watchdog │
│(God    │  │(Yellow   │      │ (Health)  │
│Agent)  │  │Pages)    │      │           │
└────────┘  └──────────┘      └───────────┘
    │              │                  │
    └──────────────┴──────────────────┘
                   │
        ┌──────────▼──────────┐
        │  Resource Governor  │
        │  (System Control)   │
        └─────────────────────┘
```

## Key Components

### 1. Agent Management System (AMS)

#### ams.py
**Purpose**: "The God Agent" - Manages agent lifecycles and enforces VRAM constraints

**Role**: City Hall with ultimate authority over agent creation and destruction

**Critical Constraints**:
- **VRAM Bottleneck**: RTX 4060 has only 8GB VRAM
- **One-Model-At-A-Time**: Only ONE cognitive agent can be active at once
- **Automatic Swapping**: Queue-based agent activation/deactivation

**Key Classes**:
- `AgentState` - ACTIVE, SUSPENDED, IDLE, TERMINATED
- `AgentMetadata` - Agent lifecycle tracking
- `AMS` - Main agent management system

**Core Features**:
1. **Agent Registration**: Track all agents in system
2. **Lifecycle Management**: Create, activate, suspend, terminate
3. **VRAM Monitoring**: Real-time GPU memory tracking via nvidia-smi
4. **Queue Management**: Maintain waiting queue for VRAM slot
5. **Automatic Swapping**: Load/unload agents based on availability
6. **Emergency Shutdown**: Gracefully handle VRAM overflow

**Hardware Awareness**:
```
CPU:           AMD Ryzen 7 8700F (8-Core)
System RAM:    32 GB DDR5
GPU:           NVIDIA GeForce RTX 4060
VRAM:          8 GB GDDR6 (CRITICAL BOTTLENECK)
```

**VRAM Rules**:
- 7B parameter LLM requires ~5-6GB VRAM (4-bit quantized)
- 8GB VRAM = ONE active cognitive agent maximum
- AMS enforces this as fundamental law

**Usage**:
```python
from symbo_agentic_reasoners.infrastructure.ams import AMS, AgentMetadata

ams = AMS(max_vram_gb=8.0, max_agents=100)

# Register agent
agent_id = ams.register_agent(
    name="CalculusSupervisor",
    agent_type="supervisor",
    vram_required_gb=5.5
)

# Activate agent (waits for VRAM if needed)
ams.activate_agent(agent_id)

# Work with agent...

# Deactivate when done
ams.deactivate_agent(agent_id)
```

**Emergency Protocols**:
- VRAM overflow → Emergency shutdown of least-recently-used agents
- System RAM critical → Terminate idle agents
- Deadlock detection → Force-kill stalled agents

---

### 2. Directory Facilitator (DF)

#### directory_facilitator.py
**Purpose**: "Yellow Pages" - Dynamic service discovery and registration

**Role**: Enables agents to find services by capability, not by hardcoded names

**Key Classes**:
- `ServiceRegistration` - Service description
- `ServiceQuery` - Service search criteria
- `DirectoryFacilitator` - Main registry

**Core Features**:
1. **Service Registration**: Agents register capabilities
2. **Dynamic Discovery**: Find agents by service type, not ID
3. **Capability Matching**: Filter by algorithm, cost, performance
4. **Load Balancing**: Multiple agents can provide same service
5. **Hot-Swapping**: Add/remove agents without breaking system
6. **Health Tracking**: Monitor service availability

**Service Types** (Hierarchical):
```
math.calculus.integration
math.calculus.differentiation
math.algebra.polynomial.factorization
math.linalg.matrix.decomposition
math.logic.propositional
physics.mechanics.kinematics
...
```

**Usage**:
```python
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)

df = DirectoryFacilitator()

# Register service
service = create_service_registration(
    service_type="math.calculus.integration",
    agent_id="integration_specialist_1",
    algorithm="risch",
    cost_estimate=5.0,
    metadata={'max_complexity': 'high'}
)
df.register_service(service)

# Find services
integrators = df.search_services(
    service_type="math.calculus.integration",
    algorithm="risch"
)

# Select best agent
best_agent = df.select_best_service(
    service_type="math.calculus.integration",
    criteria={'cost': 'low', 'algorithm': 'risch'}
)
```

**Why This Matters**:
As system scales to 60+ agents, static routing becomes unmaintainable. DF enables:
- Agents discover each other dynamically
- Graceful degradation when agents fail
- Multiple implementations of same service
- Easy addition of new capabilities

---

### 3. Agent Communication Channel (ACC)

#### acc.py
**Purpose**: "Postal Service" - Message routing and delivery

**Role**: Central message broker for agent-to-agent communication

**Key Classes**:
- `MessageType` - REQUEST, INFORM, PROPOSE, ACCEPT, REJECT
- `Message` - FIPA-ACL compliant message structure
- `ACC` - Agent Communication Channel

**Core Features**:
1. **Message Routing**: Point-to-point and broadcast
2. **Queue Management**: Per-agent message queues
3. **Priority Handling**: Urgent messages jump queue
4. **Delivery Guarantees**: At-least-once delivery
5. **Dead Letter Queue**: Failed messages for debugging
6. **Message Filtering**: Subscribe to message types

**Message Protocol**: FIPA-ACL (Foundation for Intelligent Physical Agents - Agent Communication Language)

**Usage**:
```python
from symbo_agentic_reasoners.infrastructure.acc import ACC
from symbo_agentic_reasoners.protocols.fipa_acl import create_request

acc = ACC()

# Register agents
acc.register_agent("orchestrator")
acc.register_agent("calculus_supervisor")

# Send message
message = create_request(
    sender="orchestrator",
    receiver="calculus_supervisor",
    content="integrate sin(x) dx",
    conversation_id="task_001"
)
acc.send_message(message)

# Receive messages
messages = acc.receive_messages("calculus_supervisor")
```

---

### 4. Watchdog

#### watchdog.py
**Purpose**: "Health Inspector" - Timeout enforcement and process monitoring

**Role**: Prevents hung operations from starving system resources

**Key Classes**:
- `TaskStatus` - RUNNING, COMPLETED, TIMEOUT, FAILED
- `WatchdogTask` - Task metadata with heartbeat
- `Watchdog` - Main monitoring system

**Core Features**:
1. **Operation Timeouts**: Configurable timeout per task (default: 30s)
2. **Heartbeat Monitoring**: Long-running tasks send heartbeats
3. **Automatic Termination**: Kill stalled operations
4. **Timeout Decorator**: `@with_timeout(seconds)`
5. **Context Manager**: `with timeout_context(seconds)`
6. **Integration with AMS**: Report hung agents for emergency shutdown

**Default Timeouts**:
- Agent creation: 10s
- Specialist execution: 30s
- Supervisor routing: 5s
- Orchestrator synthesis: 60s
- Discovery operations: 300s (5 minutes)

**Usage**:
```python
from symbo_agentic_reasoners.infrastructure.watchdog import (
    Watchdog, with_timeout, TimeoutError
)

# Decorator usage
@with_timeout(30)
def risky_operation():
    # Will be killed if takes >30 seconds
    complex_computation()

# Context manager usage
watchdog = Watchdog()
with watchdog.timeout_context(60):
    long_running_task()

# Manual usage with heartbeat
task_id = watchdog.start_task("integration", timeout=30)
try:
    step1()
    watchdog.heartbeat(task_id)  # Keep alive
    step2()
    watchdog.heartbeat(task_id)
    step3()
finally:
    watchdog.complete_task(task_id)
```

**Why This Matters**:
Without timeouts, a single hung agent could deadlock entire system. Watchdog ensures:
- Failed operations don't block progress
- Resources are reclaimed from stalled tasks
- System remains responsive

---

### 5. Resource Governor

#### resource_governor.py (576 lines)
**Purpose**: "Power Grid Manager" - System-wide resource throttling

**Role**: Prevent system overload through adaptive throttling

**Key Classes**:
- `ResourceUsage` - Current system resource metrics
- `ThrottleLevel` - NONE, LOW, MEDIUM, HIGH, CRITICAL
- `ResourceGovernor` - Main governor

**Core Features**:
1. **Resource Monitoring**: CPU, RAM, VRAM, disk I/O
2. **Adaptive Throttling**: Slow down operations under high load
3. **Priority Queuing**: Critical tasks bypass throttling
4. **Circuit Breaker**: Stop new tasks when resources critical
5. **Backpressure**: Signal agents to reduce work rate
6. **Recovery**: Automatic restoration when resources available

**Throttle Thresholds**:
```
CPU > 80%    → Throttle Level: LOW
CPU > 90%    → Throttle Level: MEDIUM
RAM > 80%    → Throttle Level: HIGH
VRAM > 90%   → Throttle Level: CRITICAL (emergency shutdown)
```

**Usage**:
```python
from symbo_agentic_reasoners.infrastructure.resource_governor import ResourceGovernor

governor = ResourceGovernor()

# Start monitoring
governor.start()

# Check if operation allowed
if governor.can_start_operation("integration_task"):
    perform_integration()
else:
    # Queue or reject
    queue_for_later()

# Report resource usage
governor.report_usage(
    cpu_percent=45.0,
    ram_percent=60.0,
    vram_percent=75.0
)

# Get throttle recommendation
throttle = governor.get_throttle_level()
if throttle.level >= ThrottleLevel.HIGH:
    slow_down_operations()
```

---

### 6. Supporting Components

#### agent_pool.py
**Purpose**: Memory-efficient agent pooling and reuse

**Features**:
- Agent instance pooling
- Lazy initialization
- Domain-specific pools (calculus, algebra, etc.)
- Automatic cleanup of unused agents
- Statistics tracking

**Usage**:
```python
from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool

pool = AgentPool(max_agents=100)

# Get agent from pool (creates if needed)
agent = pool.get_agent("calculus", "differentiation_specialist")

# Use agent
result = agent.solve(problem)

# Return to pool
pool.release_agent(agent)
```

---

#### agent_registry.py
**Purpose**: Central registry of all agent types and capabilities

**Features**:
- Agent class registration
- Capability lookup
- Version management
- Factory pattern support

---

#### agent_factory.py
**Purpose**: Factory for creating agents with dependency injection

**Features**:
- Centralized agent creation
- Dependency injection
- Configuration management
- Testing support (mock agents)

**Usage**:
```python
from symbo_agentic_reasoners.infrastructure.agent_factory import AgentFactory

factory = AgentFactory()

# Create agent with dependencies
agent = factory.create_agent(
    agent_type="DifferentiationSpecialist",
    config={'timeout': 30},
    dependencies={'blackboard': blackboard}
)
```

---

#### hardware_detector.py
**Purpose**: Automatic hardware detection and configuration

**Features**:
- GPU detection (NVIDIA, AMD, none)
- VRAM measurement
- CPU core counting
- RAM detection
- Optimal configuration recommendations

**Usage**:
```python
from symbo_agentic_reasoners.infrastructure.hardware_detector import detect_hardware

hw_info = detect_hardware()
print(f"VRAM: {hw_info.vram_gb} GB")
print(f"CPU Cores: {hw_info.cpu_cores}")
print(f"Recommended max agents: {hw_info.recommended_max_agents}")
```

---

## Directory Structure

```
infrastructure/
├── __init__.py
│
├── ams.py                      # Agent Management System (AMS)
├── directory_facilitator.py    # Service discovery (DF)
├── acc.py                      # Agent Communication Channel
├── watchdog.py                 # Timeout enforcement
├── resource_governor.py        # Resource throttling (576 lines)
│
├── agent_pool.py               # Agent pooling and reuse
├── agent_registry.py           # Agent type registry
├── agent_factory.py            # Agent creation factory
│
└── hardware_detector.py        # Hardware detection
```

## Design Principles

### 1. Hardware Awareness

Infrastructure components are acutely aware of hardware constraints:
- **VRAM**: 8GB limit enforced by AMS
- **RAM**: 32GB monitored by Resource Governor
- **CPU**: 8 cores managed by throttling
- **Timeouts**: Prevent resource starvation

### 2. Graceful Degradation

When resources are scarce:
1. Throttle new operations
2. Queue instead of reject
3. Prioritize critical tasks
4. Emergency shutdown of low-priority agents
5. Automatic recovery when resources available

### 3. Transparency

All infrastructure operations are logged:
- Agent lifecycle events
- Resource usage metrics
- Timeout events
- Throttling decisions
- Emergency shutdowns

### 4. Fail-Safe Defaults

Infrastructure errs on side of caution:
- Conservative VRAM limits
- Short default timeouts
- Aggressive throttling
- Proactive emergency shutdown

### 5. Testing Support

Infrastructure components support testing:
- Mock hardware detection
- Configurable resource limits
- Timeout overrides
- Deterministic scheduling

---

## Integration Example

Complete system setup with infrastructure:

```python
from symbo_agentic_reasoners.infrastructure.ams import AMS
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
from symbo_agentic_reasoners.infrastructure.agent_pool import AgentPool
from symbo_agentic_reasoners.infrastructure.watchdog import Watchdog
from symbo_agentic_reasoners.infrastructure.resource_governor import ResourceGovernor

# Initialize infrastructure
ams = AMS(max_vram_gb=8.0, max_agents=100)
df = DirectoryFacilitator()
pool = AgentPool(max_agents=100)
watchdog = Watchdog(default_timeout=30)
governor = ResourceGovernor()

# Start monitoring
ams.start()
watchdog.start()
governor.start()

# Create and register agents
from symbo_agentic_reasoners.agents.supervisors.calculus_supervisor import CalculusSupervisor

supervisor_id = ams.register_agent(
    name="CalculusSupervisor",
    agent_type="supervisor",
    vram_required_gb=5.5
)

# Register services
df.register_service(
    service_type="math.calculus.coordination",
    agent_id=supervisor_id
)

# Activate agent
ams.activate_agent(supervisor_id)

# Use agent with timeout
with watchdog.timeout_context(60):
    supervisor = pool.get_agent("calculus", "supervisor")
    result = supervisor.solve(problem)
    pool.release_agent(supervisor)

# Shutdown
ams.shutdown()
watchdog.shutdown()
governor.shutdown()
```

---

## Performance Characteristics

- **Agent Registration**: <1ms per agent
- **Service Lookup**: <1ms for typical queries
- **Message Routing**: <1ms per message
- **VRAM Monitoring**: Every 1-5 seconds
- **Watchdog Check**: Every 100ms
- **Resource Throttling**: Dynamic based on load

---

## Testing

Infrastructure has comprehensive test coverage:

```bash
# Test AMS
pytest tests/test_phase0.py -k ams

# Test Directory Facilitator
pytest tests/test_phase0.py -k directory

# Test Watchdog
pytest tests/test_watchdog_integration.py

# Test Resource Governor
pytest tests/test_resource_governor.py

# All infrastructure tests
pytest tests/test_infrastructure_comprehensive.py
pytest tests/test_infrastructure_modules.py
```

---

## Monitoring and Observability

Infrastructure components provide rich telemetry:

### AMS Metrics
- Active agents count
- VRAM usage (current, peak)
- Agent creation/destruction rate
- Queue depth
- Emergency shutdown events

### Directory Facilitator Metrics
- Total services registered
- Service lookup rate
- Average lookup time
- Service health status

### Watchdog Metrics
- Active tasks
- Timeout events
- Average task duration
- Heartbeat frequency

### Resource Governor Metrics
- CPU utilization
- RAM usage
- VRAM usage
- Throttle level
- Operations queued/rejected

---

## Future Enhancements

1. **Distributed Infrastructure**: Multi-machine coordination
2. **Predictive Throttling**: ML-based resource prediction
3. **Auto-Scaling**: Dynamic agent pool sizing
4. **Advanced Scheduling**: Priority-based task scheduling
5. **Checkpointing**: State persistence for long tasks
6. **Health Dashboard**: Real-time system visualization

---

## Related Components

- `../core/` - Uses infrastructure for agent coordination
- `../agents/` - All agents managed by infrastructure
- `../middleware/` - Built on infrastructure foundation
- `../../tests/` - Infrastructure test suite

---

Generated by SYMBO Documentation System
Last Updated: 2025-12-14
