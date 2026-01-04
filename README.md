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

### CLI Commands

After installation, the `math-agent-solver` command is available:

```bash
# Solve a single problem
math-agent-solver solve "2 + 2"
math-agent-solver solve "diff(x**2, x)"

# Solve problems from a file
math-agent-solver solve-file problems.txt

# Batch process a directory
math-agent-solver batch ./data/problems/

# Show system status
math-agent-solver status

# Interactive mode
math-agent-solver
```

### Library Usage

```python
from symbo_agentic_reasoners.api import solve_expression, SolverConfig

# Simple usage with defaults
result = solve_expression("x**2 - 4")
print(result.solution)  # Shows the simplified expression

# Custom configuration
config = SolverConfig(timeout_sec=30.0, max_steps=500)
result = solve_expression("integrate(sin(x), x)", config=config)

# Check status
if result.status == "ok":
    print(f"Solution: {result.solution}")
else:
    print(f"Error: {result.error}")
```

### Batch Processing

```python
from symbo_agentic_reasoners.api import solve_file, solve_batch

# Solve from file
results = solve_file("problems.txt")
for r in results:
    print(f"{r.problem}: {r.solution if r.status == 'ok' else r.error}")

# Solve a list of problems
results = solve_batch(["2+2", "3*3", "diff(x**2, x)"])
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

### CLI Options

```bash
# Set timeout and log level
math-agent-solver --timeout 30 --log-level DEBUG solve "x**2"

# Use a config file
math-agent-solver --config my_config.yaml solve-file problems.txt
```

### Configuration File

Create a `config.yaml` with solver settings:

```yaml
solver:
  timeout_sec: 60.0
  max_steps: 1000
  max_parallel_problems: 4
  log_level: INFO
  log_format: pretty
```

### Environment Variables

Override settings via environment:

```bash
export MATH_SOLVER_TIMEOUT_SEC=120
export MATH_SOLVER_MAX_STEPS=2000
export MATH_SOLVER_LOG_LEVEL=DEBUG
math-agent-solver solve "complex_problem"
```

### Legacy Configuration

For advanced system-wide settings:

1. Copy `.env.example` to `.env` and adjust values (paths, timeouts, HMAC keys).
2. Point to YAML config (defaults in `config.yaml`):

```bash
export SYMBO_CONFIG_FILE=config.yaml
python main.py solve "sin(x)**2 + cos(x)**2"
```

## Production Usage

### Safety Limits

The solver enforces safety limits to prevent runaway operations:

- **Timeout**: Default 60 seconds per problem (configurable)
- **Max Steps**: Default 1000 solver steps per problem
- **Max Recursion**: Default 50 levels deep
- **Expression Limits**: Max depth 100, max length 10000 chars

### Structured Results

All API calls return structured `SolveResult` objects:

```python
result = solve_expression("2 + 2")

# Check status
if result.status == "ok":
    print(result.solution)
elif result.status == "timeout":
    print(f"Timed out: {result.error}")
elif result.status == "error":
    print(f"Error: {result.error}")

# Access diagnostics
print(f"Solved in {result.solve_time_ms}ms")
print(f"Domain: {result.domain}")
print(f"Specialist: {result.specialist_used}")
```

### Logging

Configure logging for observability:

```python
from symbo_agentic_reasoners.api import setup_logging

# Human-readable logs
setup_logging(level="INFO", log_format="pretty")

# JSON logs for log aggregation
setup_logging(level="INFO", log_format="json")
```

Correlation IDs are automatically included for request tracing.

### Parallel Processing

For batch workloads:

```python
config = SolverConfig(
    timeout_sec=30.0,
    max_parallel_problems=8,  # Use 8 parallel workers
)
results = solve_batch(problems, config)
```

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
