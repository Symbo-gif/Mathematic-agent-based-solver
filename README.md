# Mathematic Agent-Based Solver (SYMBO_AGENTIC_REASONERS)

Hierarchical, multi-agent mathematical discovery engine (v0.6.0) with BDI cognitive architecture, structured messaging, and native mathematical computation (NO SYMPY inside agents).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .[dev]        # Installs runtime + dev/test tooling
```

For minimal runtime only:

```bash
pip install -e .
```

## Quick Start

Interactive CLI:

```bash
python main.py
```

Solve a single problem:

```bash
python main.py solve "integrate(x**2, x)"
```

Batch a directory of problems:

```bash
python main.py batch ./data/problems/
```

## Core API Examples

```python
from symbo_agentic_reasoners.core.blackboard import Blackboard
from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator

blackboard = Blackboard()
orchestrator = MainOrchestrator(blackboard=blackboard)
result = orchestrator.solve("x^2 + 2x + 1 = 0")
print(result.solution)
```

Structured logging:

```python
from symbo_agentic_reasoners.utils.logging import setup_logging

setup_logging(json_format=True, level="INFO")
```

## Architecture Overview

- **Tier 1 Orchestrator:** Delegates problems, synthesizes results.
- **Tier 2 Supervisors (12 domains):** Calculus, Algebra, Linear Algebra, Geometry, Logic, Discrete Math, Statistics, Physics (4), Unknown Domain.
- **Tier 3 Specialists (45+):** Domain task executors (integration, limits, matrix ops, proofs, etc.).
- **Core:** BDI framework, blackboard, native calculus/ algebra engines, safe parser, solver engine.
- **Middleware:** Knowledge management, meta-learning, conflict resolution, theorem library.
- **Infrastructure:** AMS, Directory Facilitator, Watchdog, Resource Governor, monitoring.
- **Discovery & Optimization:** Deep search, conjecture, evolutionary synthesis, student/teacher learning.

## Configuration

1. Copy `.env.example` to `.env` and adjust values (paths, timeouts, HMAC keys).
2. Point to YAML config (defaults in `config.yaml`):

```bash
export SYMBO_CONFIG_FILE=config.yaml
python main.py solve "sin(x)**2 + cos(x)**2"
```

Structured logging config is available at `config/logging.json` (JSON formatter, rotating file handler).

## Testing & Coverage

Run focused tests:

```bash
pytest tests/unit -m "not slow"
```

Full suite with coverage:

```bash
pytest --cov=src/symbo_agentic_reasoners --cov-report=term --cov-report=xml
```

## Documentation

- API and architecture notes live in `docs/api/`.
- Build static docs (Markdown sources):

```bash
make docs
```

## Contributing

1. Create a virtualenv and install with `pip install -e .[dev]`.
2. Run `make lint` and `make test` before opening a PR.
3. Ensure new public functions/classes include docstrings.
4. Add or update tests and keep coverage trending toward 80%+.

## Release & Packaging

- Version is managed in `pyproject.toml`.
- Build artifacts with `python -m build` (requires `pip install build`).
- Publish via standard PyPI flow after CI green and CHANGELOG update.
