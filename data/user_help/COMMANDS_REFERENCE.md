# SYMBO_AGENTIC_REASONERS Commands Reference
## Complete Command Line and API Reference

---

## Table of Contents

1. [Command Line Interface](#command-line-interface)
2. [Python API Reference](#python-api-reference)
3. [Script Commands](#script-commands)
4. [Audit Commands](#audit-commands)
5. [System Management](#system-management)

---

## Command Line Interface

### Running Phase Systems

```bash
# Syntax: python -m <module_path>

# Phase 0: Infrastructure
python -m symbo_agentic_reasoners_phase0.phase0_system

# Phase 1: Cognitive Chassis
python -m symbo_agentic_reasoners_phase1.phase1_system

# Phase 2: Mathematical Workforce
python -m symbo_agentic_reasoners_phase2.phase2_system

# Phase 3: Meta-Cognitive Middleware
python -m symbo_agentic_reasoners_phase3.phase3_system

# Phase 4: Dynamic Governance
python -m symbo_agentic_reasoners_phase4.phase4_system

# Phase 5: Production Optimization
python -m symbo_agentic_reasoners_phase5.phase5_system

# Phase 6: Discovery Engine
python -m symbo_agentic_reasoners_phase6.phase6_system
```

### Running Tests

```bash
# All tests for a phase
python -m pytest tests/test_phase0.py -v
python -m pytest tests/test_phase1.py -v
python -m pytest tests/test_phase2.py -v
python -m pytest tests/test_phase3.py -v
python -m pytest tests/test_phase4.py -v

# Specific test
python -m pytest tests/test_phase1.py::TestPhase1System::test_solve_simple_math -v

# All tests
python -m pytest tests/ -v
```

---

## Python API Reference

### Phase 0: Infrastructure

```python
# === AMS (Agent Management Service) ===
from symbo_agentic_reasoners_phase0.infrastructure.ams import AgentManagementService

ams = AgentManagementService()
ams.register_agent(agent_id, agent_type, capabilities)
ams.activate_agent(agent_id)
ams.deactivate_agent(agent_id)
ams.get_agent_status(agent_id)
ams.get_statistics()

# === Directory Facilitator ===
from symbo_agentic_reasoners_phase0.infrastructure.directory_facilitator import DirectoryFacilitator

df = DirectoryFacilitator()
df.register_service(agent_id, service_type, description)
df.search_services(service_type=None, capability=None)
df.deregister_service(agent_id, service_type)

# === ACC (Agent Communication Channel) ===
from symbo_agentic_reasoners_phase0.infrastructure.acc import AgentCommunicationChannel

acc = AgentCommunicationChannel(ams)
acc.send_message(message)
acc.broadcast_message(message, agent_filter)
acc.get_pending_messages(agent_id)

# === Blackboard ===
from symbo_agentic_reasoners_phase0.memory.blackboard import Blackboard

bb = Blackboard()
entry_id = bb.post_task(task_content, author, conversation_id, tags)
bb.post_result(entry_id, result_content, author)
bb.update_status(entry_id, new_status)
entries = bb.get_entries(conversation_id, status, tags)

# === Vector Database ===
from symbo_agentic_reasoners_phase0.memory.vector_database import VectorDatabase

vdb = VectorDatabase(collection_name="theorems")
entry_id = vdb.store(content, metadata, embedding)
results = vdb.retrieve(query, n_results, metadata_filter)
similar = vdb.search_similar(content, n_results)

# === FIPA-ACL Messages ===
from symbo_agentic_reasoners_phase0.core.fipa_acl import create_request, create_inform, Performative

msg = create_request(sender, receiver, content)
msg = create_inform(sender, receiver, content, in_reply_to)

# === OMDoc ===
from symbo_agentic_reasoners_phase0.core.omdoc_schema import OMDocBuilder

builder = OMDocBuilder()
omdoc = builder.create_variable("x")
omdoc = builder.create_apply("Plus", [arg1, arg2])
omdoc = builder.create_bind("Lambda", ["x"], body)
```

### Phase 1: Cognitive Chassis

```python
from symbo_agentic_reasoners_phase1.phase1_system import Phase1System

# === System Lifecycle ===
system = Phase1System()
system.start()              # Initialize all components
system.shutdown()           # Clean shutdown

# === Problem Solving ===
result = system.solve(problem_text)
result = system.solve("Integrate x^2 dx")

# === Health Check ===
health = system.health_check()
stats = system.get_statistics()

# === Problem Analysis ===
from symbo_agentic_reasoners_phase1.agents.problem_analysis import ProblemAnalysisTeam

team = ProblemAnalysisTeam(blackboard, ams, df)
structured = team.analyze("Find derivative of sin(x)")
# Returns: StructuredProblem with type, domain, omdoc_tree

# === Verification ===
from symbo_agentic_reasoners_phase1.verification.verification_core import VerificationCore

vc = VerificationCore(blackboard, vector_db)
is_valid = vc.verify(solution_entry)
stats = vc.get_statistics()
```

### Phase 2: Mathematical Workforce

```python
from symbo_agentic_reasoners_phase2.phase2_system import Phase2System

# === System Operations ===
system = Phase2System()
system.start()
result = system.solve(problem)
system.shutdown()

# === Domain Supervisors ===
from symbo_agentic_reasoners_phase2.supervisors.calculus_supervisor import CalculusSupervisor
from symbo_agentic_reasoners_phase2.supervisors.algebra_supervisor import AlgebraSupervisor
from symbo_agentic_reasoners_phase2.supervisors.linalg_supervisor import LinearAlgebraSupervisor
from symbo_agentic_reasoners_phase2.supervisors.stats_supervisor import StatisticsSupervisor

supervisor = CalculusSupervisor(blackboard, vector_db, ams, df)
result = supervisor.delegate(task_context)

# === Specialist Agents ===
from symbo_agentic_reasoners_phase2.agents.calculus.integration_specialist import IntegrationSpecialist
from symbo_agentic_reasoners_phase2.agents.calculus.differentiation_specialist import DifferentiationSpecialist
from symbo_agentic_reasoners_phase2.agents.algebra.polynomial_specialist import PolynomialSpecialist

specialist = IntegrationSpecialist(blackboard, vector_db)
result = specialist.solve({
    'expression': 'x**2',
    'variable': 'x',
    'bounds': (0, 1)
})
```

### Phase 3: Meta-Cognitive Middleware

```python
from symbo_agentic_reasoners_phase3.phase3_system import Phase3System

# === System Operations ===
system = Phase3System()
system.start()

# === Problem Validation ===
validation = system.validate_problem(problem, conversation_id)
# Returns: {'valid': bool, 'violations': [...], 'domain': str}

# === Knowledge Management ===
context = system.get_context(problem, conversation_id)
system.record_result(result, conversation_id)

# === Full Solve ===
result = system.solve(problem, conversation_id)

system.shutdown()

# === Individual Teams ===
from symbo_agentic_reasoners_phase3.validation.precondition_validation import PreconditionValidationTeam
from symbo_agentic_reasoners_phase3.knowledge.knowledge_management import KnowledgeManagementTeam
from symbo_agentic_reasoners_phase3.hypothesis.hypothesis_generation import HypothesisGenerationTeam

validation_team = PreconditionValidationTeam(blackboard)
result = validation_team.validate(problem, conversation_id)

knowledge_team = KnowledgeManagementTeam(blackboard, vector_db, df)
context = knowledge_team.look_before_leap(problem, conversation_id)

hypothesis_team = HypothesisGenerationTeam(blackboard, df)
plan = hypothesis_team.scout(problem, conversation_id, 'integration')
```

### Phase 4: Dynamic Governance

```python
from symbo_agentic_reasoners_phase4.phase4_system import Phase4System

system = Phase4System()
system.start()

# Solve with governance
result = system.solve(problem)

# Get optimization suggestions
suggestions = system.optimize()

system.shutdown()

# === Individual Teams ===
from symbo_agentic_reasoners_phase4.governance.conflict_resolution import ConflictResolutionTeam
from symbo_agentic_reasoners_phase4.failure_analysis.failure_analysis_team import FailureAnalysisTeam
from symbo_agentic_reasoners_phase4.meta_learning.meta_learning_team import MetaLearningTeam

# Conflict Resolution
conflict_team = ConflictResolutionTeam(blackboard)
resolution = conflict_team.resolve(conflict_case)

# Failure Analysis
failure_team = FailureAnalysisTeam(blackboard)
analysis = failure_team.analyze(failure_context)

# Meta-Learning
meta_team = MetaLearningTeam(blackboard, vector_db)
optimizations = meta_team.suggest_optimizations()
```

### Phase 5: Production Optimization

```python
from symbo_agentic_reasoners_phase5.phase5_system import Phase5System

system = Phase5System(thought_trace_path="./traces")
system.start()

# Solve and capture traces
result = system.solve(problem)

# Run distillation
system.run_distillation()

# Get deployment router
router = system.get_router()
response = router.route(query)

system.shutdown()
```

### Phase 6: Mathematical Discovery

```python
from symbo_agentic_reasoners_phase6.phase6_system import Phase6System

system = Phase6System()
system.start()

# Run discovery cycle
result = system.run_discovery_cycle(
    num_theorems=100,
    search_budget=1000,
    max_candidates=10
)

# Get discoveries
discoveries = result.discoveries
proofs = result.proofs_succeeded

system.shutdown()
```

---

## Script Commands

### Available Scripts

```bash
# Convert Word documents to Markdown
python scripts/convert_docs.py

# Verify installation
python scripts/verify_installation.py

# Start full system
python scripts/start_full_system.py

# Run all audits
python scripts/run_all_audits.py

# Quick test
python scripts/quick_test.py
```

---

## Audit Commands

### Run Individual Audits

```bash
python -m audit.audit_runner              # Phase 0
python -m audit.phase1.audit_runner       # Phase 1
python -m audit.phase2.audit_runner       # Phase 2
python -m audit.phase3.audit_runner       # Phase 3
python -m audit.phase4.audit_runner       # Phase 4
python -m audit.phase5.audit_runner       # Phase 5
python -m audit.phase6.audit_runner       # Phase 6
```

### Audit Output Locations

```
audit/reports/                    # Phase 0 reports
audit/phase1/reports/            # Phase 1 reports
audit/phase2/reports/            # Phase 2 reports
audit/phase3/reports/            # Phase 3 reports
audit/phase4/reports/            # Phase 4 reports
audit/phase5/reports/            # Phase 5 reports
audit/phase6/reports/            # Phase 6 reports
```

---

## System Management

### Health Checks

```python
# Per-phase health check
system.health_check()  # Returns dict with component status

# Get statistics
stats = system.get_statistics()
```

### Graceful Shutdown

```python
# Always call shutdown for clean exit
system.shutdown()

# Or use context manager
with Phase1System() as system:
    system.start()
    result = system.solve(problem)
# Auto-shutdown on exit
```

### Logging Configuration

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Per-module logging
logging.getLogger('symbo_agentic_reasoners_phase1').setLevel(logging.DEBUG)
logging.getLogger('symbo_agentic_reasoners_phase2').setLevel(logging.INFO)
```

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| Run Phase 1 | `python -m symbo_agentic_reasoners_phase1.phase1_system` |
| Run Full System | `python scripts/start_full_system.py` |
| Run All Tests | `python -m pytest tests/ -v` |
| Run All Audits | `python scripts/run_all_audits.py` |
| Convert Docs | `python scripts/convert_docs.py` |
| Health Check | `system.health_check()` |
| Solve Problem | `system.solve("problem text")` |
| Get Stats | `system.get_statistics()` |
| Shutdown | `system.shutdown()` |
