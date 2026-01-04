# SYMBO Agentic Reasoners – API & Operations

## Quick API Surface

- `symbo_agentic_reasoners.api` – Public API (solve_expression, SolverConfig, SolveResult)
- `symbo_agentic_reasoners.core.orchestrator.MainOrchestrator` – Tier 1 coordinator.
- `symbo_agentic_reasoners.core.blackboard.Blackboard` – Shared state and pub/sub.
- `symbo_agentic_reasoners.agents.supervisors.*` – 38 domain routers (calculus, algebra, logic, physics, complex analysis, cryptography, etc.).
- `symbo_agentic_reasoners.agents.specialists.*` – 220+ task executors across 30 domains.
- `symbo_agentic_reasoners.middleware.meta_learning` – Meta-cognitive learning, knowledge reuse.
- `symbo_agentic_reasoners.utils.logging` – Structured logging utilities.

```python
from symbo_agentic_reasoners.core import blackboard, orchestrator

bb = blackboard.Blackboard()
mgr = orchestrator.MainOrchestrator(blackboard=bb)
solution = mgr.solve("integrate(x**3, x)")
print(solution.solution, solution.explanation)
```

### Public API (Recommended)

```python
from symbo_agentic_reasoners.api import solve_expression, SolverConfig

# Simple usage
result = solve_expression("2 + 2")
print(result.solution)  # "4"

# With configuration
config = SolverConfig(timeout_sec=30.0, max_steps=500)
result = solve_expression("diff(x**2, x)", config)
if result.status == "ok":
    print(result.solution)
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
