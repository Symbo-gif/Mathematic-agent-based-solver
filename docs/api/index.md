# SYMBO Agentic Reasoners – API & Operations

## Quick API Surface

- `symbo_agentic_reasoners.core.orchestrator.MainOrchestrator` – Tier 1 coordinator.
- `symbo_agentic_reasoners.core.blackboard.Blackboard` – Shared state and pub/sub.
- `symbo_agentic_reasoners.agents.supervisors.*` – Domain routers (calculus, algebra, logic, physics, etc.).
- `symbo_agentic_reasoners.agents.specialists.*` – Task executors for integration, limits, tensors, proofs, search.
- `symbo_agentic_reasoners.middleware.meta_learning` – Meta-cognitive learning, knowledge reuse.
- `symbo_agentic_reasoners.utils.logging` – Structured logging utilities.

```python
from symbo_agentic_reasoners.core import blackboard, orchestrator

bb = blackboard.Blackboard()
mgr = orchestrator.MainOrchestrator(blackboard=bb)
solution = mgr.solve("integrate(x**3, x)")
print(solution.solution, solution.explanation)
```

## Configuration Entry Points

- YAML defaults: `config.yaml`
- Environment overrides: `SYMBO_*` (see `.env.example`)
- Logging profile: `config/logging.json`

```bash
SYMBO_CONFIG_FILE=config.yaml SYMBO_LOG_LEVEL=DEBUG python main.py solve "cos(x)"
```

## Developer Tasks

```bash
make install       # install runtime
make install-dev   # install with dev tools
make lint          # ruff + black check
make test          # pytest with defaults
make coverage      # pytest with coverage xml
make docs          # basic docs build guard
```

## Architecture Notes

- BDI agents with blackboard-mediated coordination.
- Strict separation of orchestration (Tier 1), domain routing (Tier 2), and execution (Tier 3).
- Security features: message HMAC, timeout-enforced parser, resource governor thresholds.
- Observability: structured logging with correlation IDs, JSON format optional.
