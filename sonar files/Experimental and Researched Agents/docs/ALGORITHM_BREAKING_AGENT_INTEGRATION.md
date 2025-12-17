# Algorithm Breaking Agent - Integration Guide

## Overview

This document describes how to integrate the Algorithm Breaking Agent (ABA) with the existing Symbo Agentic Reasoners infrastructure.

---

## 1. Integration with Existing Agents

### 1.1 CrackFinderAgent Relationship

The ABA complements the existing `CrackFinderAgent` in `src/system_agents/crackfinder_agent.py`:

| Aspect | CrackFinderAgent | AlgorithmBreakingAgent |
|--------|------------------|------------------------|
| **Focus** | System-level testing | Algorithm-level testing |
| **Scope** | Infrastructure, API, integration | Mathematical algorithms |
| **Methods** | White-box, black-box, integration | Fuzzing, boundary, stability |
| **Output** | Test results, cracks | Vulnerabilities, test cases |

**Integration Pattern**:
```python
# In a combined testing session
crackfinder = CrackFinderAgent()
algorithm_breaker = AlgorithmBreakingAgent()

# Run system tests first
system_report = crackfinder.run_all_tests()

# Then run algorithm-specific tests
algo_report = algorithm_breaker.run_attack_campaign()

# Combine results
combined_vulnerabilities = (
    system_report.cracks +
    [convert_to_crack(v) for v in algo_report.vulnerabilities]
)
```

### 1.2 MathematicalCrackfinder Relationship

The ABA inherits test generation patterns from `MathematicalCrackfinder`:

| Feature | MathematicalCrackfinder | AlgorithmBreakingAgent |
|---------|-------------------------|------------------------|
| **Edge Cases** | generate_edge_cases() | ExpressionFuzzer.fuzz_* |
| **Ill-Conditioned** | generate_ill_conditioned_problems() | NumericalStabilityAnalyzer |
| **Verification** | verify_correctness() | CorrectnessVerifier (planned) |

### 1.3 SecurityStressTester Relationship

The ABA shares security attack vectors with `SecurityStressTester`:

| Attack Type | SecurityStressTester | AlgorithmBreakingAgent |
|-------------|---------------------|------------------------|
| **Injection** | Code injection payloads | Same + math-specific |
| **Resource** | Memory bombs, CPU exhaustion | Depth bombs, width bombs |
| **DoS** | Infinite loops, timeouts | Expression complexity DoS |

---

## 2. BDI Architecture Integration

### 2.1 Inheriting from BDIAgent

The ABA should fully inherit from `BDIAgent`:

```python
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Belief, Desire, Intention

class AlgorithmBreakingAgent(BDIAgent):
    """Full BDI implementation of ABA."""

    def __init__(self, agent_id: str = 'algorithm_breaking_agent'):
        super().__init__(agent_id)
        self._initialize_components()

    def initialize(self):
        """BDI initialization hook."""
        # Set up default desires
        self.add_desire('find_all_weaknesses', priority=9)
        self.add_desire('maximize_coverage', priority=7)
        self.add_desire('generate_test_cases', priority=5)

    def update_beliefs(self):
        """Perceive environment - read from Blackboard."""
        # Check for new test targets on Blackboard
        from symbo_agentic_reasoners.core.blackboard import Blackboard
        bb = Blackboard.get_instance()

        # Query for test requests
        requests = bb.query_entries(tags=['test_request', 'algorithm'])
        for request in requests:
            self.add_belief('test_request', request.content, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """Generate attack plans based on beliefs and desires."""
        new_intentions = []

        if self.has_belief('test_request') and self.has_desire('find_all_weaknesses'):
            target = self.get_belief('test_request').content

            # Create attack intention
            intention = Intention(
                plan_id=f'attack_{target}_{datetime.now().timestamp()}',
                steps=[
                    'setup_attack_vectors',
                    'run_parser_attacks',
                    'run_boundary_attacks',
                    'run_stability_attacks',
                    'analyze_results',
                    'generate_report'
                ],
                target_desire='find_all_weaknesses'
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """Execute one step of attack plan."""
        action = intention.get_current_action()

        if action == 'setup_attack_vectors':
            self._setup_attack_vectors()
        elif action == 'run_parser_attacks':
            results = self._run_parser_attacks()
            self.add_belief('parser_results', results, source='execution')
        elif action == 'run_boundary_attacks':
            results = self._run_boundary_attacks()
            self.add_belief('boundary_results', results, source='execution')
        # ... etc

        intention.advance()
```

### 2.2 Directory Facilitator Registration

Register ABA services with the Directory Facilitator:

```python
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)

def register_aba_services(agent: AlgorithmBreakingAgent, df: DirectoryFacilitator):
    """Register ABA services."""

    services = [
        ('testing.fuzzing', 'Expression fuzzing attack generation'),
        ('testing.boundary', 'Boundary value testing'),
        ('testing.stability', 'Numerical stability analysis'),
        ('testing.correctness', 'Algorithm correctness verification'),
        ('testing.performance', 'Performance stress testing'),
    ]

    for service_type, description in services:
        reg = create_service_registration(
            service_type=service_type,
            agent_id=agent.agent_id,
            algorithm='adversarial_testing',
            metadata={'description': description}
        )
        df.register(reg)
```

### 2.3 Agent Pool Integration

Add ABA to the Agent Pool:

```python
from symbo_agentic_reasoners.infrastructure import AgentPool, AgentSpec, AgentType

def register_aba_in_pool(pool: AgentPool):
    """Register ABA in the agent pool."""

    spec = AgentSpec(
        agent_id='algorithm_breaking_agent',
        agent_class=AlgorithmBreakingAgent,
        domain='testing.adversarial',
        tier=1,  # System-level agent
        agent_type=AgentType.INFRASTRUCTURAL,
        services=[
            'testing.fuzzing',
            'testing.boundary',
            'testing.stability',
            'testing.correctness',
            'testing.performance'
        ],
        wake_on_domains=['testing', 'adversarial', 'security']
    )

    pool.register_spec(spec)
```

---

## 3. Blackboard Communication

### 3.1 Posting Vulnerabilities

Post discovered vulnerabilities to the Blackboard:

```python
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

def post_vulnerability(bb: Blackboard, vuln: AlgorithmVulnerability, agent_id: str):
    """Post a vulnerability to the Blackboard."""

    entry = create_entry(
        entry_type=EntryType.PARTIAL_RESULT,
        content={
            'vuln_id': vuln.vuln_id,
            'severity': vuln.severity.value,
            'category': vuln.category.value,
            'title': vuln.title,
            'target': f"{vuln.target_module}.{vuln.target_function}",
            'proof_of_concept': vuln.proof_of_concept,
        },
        author_agent=agent_id,
        conversation_id=f'vuln_discovery_{vuln.vuln_id}',
        tags=['vulnerability', 'algorithm', vuln.severity.value.lower()],
        status=EntryStatus.VERIFIED,
        metadata={
            'full_vulnerability': vuln.to_dict()
        }
    )

    bb.post(entry)
```

### 3.2 Receiving Test Requests

Listen for test requests on the Blackboard:

```python
def check_test_requests(bb: Blackboard, agent_id: str) -> List[Dict]:
    """Check for pending test requests."""

    requests = bb.query_entries(
        entry_type=EntryType.TASK,
        tags=['test_request', 'algorithm'],
        status=EntryStatus.PENDING
    )

    # Filter for this agent
    return [r for r in requests if agent_id in r.metadata.get('target_agents', [agent_id])]
```

---

## 4. Message Bus Integration

### 4.1 FIPA-ACL Messages

Handle FIPA-ACL messages for inter-agent communication:

```python
from symbo_agentic_reasoners.core.agent_communication import (
    FIPAMessage, Performative, MessageBus
)

class AlgorithmBreakingAgent(BDIAgent):
    """With message handling."""

    def handle_message(self, message: FIPAMessage):
        """Process incoming FIPA-ACL message."""

        if message.performative == Performative.REQUEST:
            # Handle test request
            if message.content.get('action') == 'run_attacks':
                targets = message.content.get('targets', [])
                self.add_belief('test_request', targets, source='message')

        elif message.performative == Performative.QUERY_REF:
            # Handle query for vulnerabilities
            if message.content.get('query') == 'discovered_vulnerabilities':
                vulns = self.beliefs.get('discovered_vulnerabilities', [])
                self._send_inform(message.sender, vulns)

    def _send_inform(self, recipient: str, content: Any):
        """Send INFORM message."""
        bus = MessageBus.get_instance()
        msg = FIPAMessage(
            performative=Performative.INFORM,
            sender=self.agent_id,
            receiver=recipient,
            content=content
        )
        bus.send(msg)
```

---

## 5. File System Integration

### 5.1 Recommended Location

When fully implemented, move ABA to:

```
src/system_agents/algorithm_breaking/
├── __init__.py
├── agent.py                    # Main AlgorithmBreakingAgent
├── attack_vectors/
│   ├── __init__.py
│   ├── parser_attacks.py
│   ├── solver_attacks.py
│   ├── calculus_attacks.py
│   └── linalg_attacks.py
├── analyzers/
│   ├── __init__.py
│   ├── fuzzer.py
│   ├── boundary_tester.py
│   └── stability_analyzer.py
└── reporting/
    ├── __init__.py
    ├── vulnerability.py
    └── report_generator.py
```

### 5.2 Import Structure

```python
# Public API
from src.system_agents.algorithm_breaking import (
    AlgorithmBreakingAgent,
    run_attack_campaign,
    AlgorithmVulnerability,
    AttackCampaignReport
)

# Attack vectors
from src.system_agents.algorithm_breaking.attack_vectors import (
    ParserAttacks,
    SolverAttacks,
    CalculusAttacks,
    LinalgAttacks
)

# Analyzers
from src.system_agents.algorithm_breaking.analyzers import (
    ExpressionFuzzer,
    BoundaryValueTester,
    NumericalStabilityAnalyzer
)
```

---

## 6. CI/CD Integration

### 6.1 GitHub Actions

Add to `.github/workflows/test.yml`:

```yaml
- name: Run Algorithm Breaking Agent
  run: |
    python -c "
    from sonar_files.Experimental_and_Researched_Agents.prototypes.algorithm_breaking_agent import AlgorithmBreakingAgent
    agent = AlgorithmBreakingAgent()
    agent.verbose = False
    report = agent.run_attack_campaign(
        attack_types=['parser', 'boundary'],
        duration_minutes=5
    )
    if report.critical_count > 0:
        print('CRITICAL vulnerabilities found!')
        exit(2)
    elif report.high_count > 0:
        print('HIGH vulnerabilities found!')
        exit(1)
    print(f'No major vulnerabilities. {len(report.vulnerabilities)} findings.')
    "
```

### 6.2 Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: algorithm-breaking-agent
      name: Algorithm Breaking Agent Quick Scan
      entry: python -c "from ... import AlgorithmBreakingAgent; ..."
      language: python
      always_run: true
      stages: [commit]
```

---

## 7. Usage Examples

### 7.1 Basic Usage

```python
from sonar_files.Experimental_and_Researched_Agents.prototypes.algorithm_breaking_agent import (
    AlgorithmBreakingAgent
)

# Create agent
agent = AlgorithmBreakingAgent()

# Run quick scan
report = agent.run_attack_campaign(
    attack_types=['parser'],
    duration_minutes=2
)

# Check results
print(f"Vulnerabilities: {len(report.vulnerabilities)}")
for vuln in report.vulnerabilities:
    print(f"  [{vuln.severity.value}] {vuln.title}")
```

### 7.2 Full Integration

```python
from symbo_agentic_reasoners.infrastructure import (
    AgentPool, AgentManagementSystem, register_all_agents
)
from symbo_agentic_reasoners.core.blackboard import Blackboard
from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator

# Setup infrastructure
ams = AgentManagementSystem()
pool = AgentPool(ams)
bb = Blackboard()
df = DirectoryFacilitator()

# Register agents
register_all_agents(pool)

# Create and register ABA
from sonar_files.Experimental_and_Researched_Agents.prototypes.algorithm_breaking_agent import (
    AlgorithmBreakingAgent
)

aba = AlgorithmBreakingAgent()

# Run in BDI loop
pool.start()
pool.wake_agent('algorithm_breaking_agent')

# Post test request to Blackboard
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType

request = create_entry(
    entry_type=EntryType.TASK,
    content={'targets': ['symbolic'], 'attack_types': ['parser']},
    author_agent='orchestrator',
    conversation_id='test_session_001',
    tags=['test_request', 'algorithm']
)
bb.post(request)

# ABA will pick up and process
```

---

## 8. Metrics and Monitoring

### 8.1 Key Metrics

Track these metrics for ABA effectiveness:

| Metric | Description | Target |
|--------|-------------|--------|
| `attacks_executed` | Total attack attempts | > 1000/run |
| `vulnerabilities_found` | Unique vulnerabilities | Trend down |
| `coverage_percentage` | Code paths tested | > 80% |
| `false_positive_rate` | Invalid findings | < 5% |
| `avg_attack_duration_ms` | Attack execution time | < 100ms |

### 8.2 Logging

Use structured logging:

```python
import logging

logger = logging.getLogger('symbo.algorithm_breaking_agent')

logger.info("Attack campaign started", extra={
    'targets': targets,
    'attack_types': attack_types,
    'agent_id': self.agent_id
})

logger.warning("Vulnerability discovered", extra={
    'vuln_id': vuln.vuln_id,
    'severity': vuln.severity.value,
    'target': vuln.target_function
})
```

---

## 9. Next Steps

1. **Implement Full BDI**: Extend prototype to full BDIAgent inheritance
2. **Add More Attack Vectors**: Implement solver, calculus, linalg attacks
3. **Blackboard Integration**: Full read/write Blackboard communication
4. **DF Registration**: Register all services with Directory Facilitator
5. **CI/CD Hooks**: Add to automated testing pipeline
6. **Documentation**: Create user guide and API reference

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-15
