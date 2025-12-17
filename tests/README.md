# Test Suite

Comprehensive test suite for the SYMBO Mathematical Multi-Agentic Reasoning System.

## Overview

The test suite provides extensive coverage across all system phases, components, and integration scenarios. Tests are organized by phase, category, and purpose to ensure systematic validation of the entire system.

**Test Count**: 111+ test files
**Coverage**: All 6 phases + integration + stress tests
**Test Types**: Unit, integration, stress, benchmark, edge case
**Framework**: pytest with custom markers and fixtures

## Test Organization

### By Phase

```
Phase 0 (Infrastructure):     test_phase0.py, test_infrastructure_*.py
Phase 1 (Cognitive Chassis):  test_phase1.py, test_bdi_agent.py
Phase 2 (Mathematical):       test_phase2.py, test_*_specialists.py, test_supervisors.py
Phase 3 (Meta-Cognitive):     test_phase3.py, test_meta_learning.py, test_conflict_resolution.py
Phase 4 (Governance):         test_phase4.py, test_security.py, test_resource_governor.py
Phase 5 (Optimization):       test_phase5_*.py, test_optimization_*.py
Phase 6 (Discovery):          test_phase6_*.py, test_discovery_*.py, test_deep_search_*.py
```

### By Category

```
Unit Tests:           tests/unit/
Integration Tests:    tests/integration/
Stress Tests:         test_stress_*.py, test_comprehensive_stress.py
Edge Case Tests:      test_ultra_edge_*.py, test_edgy_*.py
Benchmark Tests:      benchmark_tests.py
Coverage Tests:       test_*_coverage.py
```

### By Component

```
Core:                 test_bdi_agent.py, test_blackboard.py, test_orchestrator.py
Agents:               test_supervisors.py, test_specialists.py, test_*_specialists.py
Infrastructure:       test_infrastructure_*.py, test_watchdog_*.py, test_resource_governor.py
Middleware:           test_meta_learning.py, test_theorem_library.py, test_conflict_resolution.py
Discovery:            test_discovery_*.py, test_deep_search_*.py, test_conjecture_*.py
```

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and pytest configuration
│
├── unit/                          # Unit tests (isolated component tests)
│   ├── test_curiosity_engine.py
│   ├── test_notation_translator.py
│   ├── test_spectral_partitioner.py
│   └── test_new_domains.py
│
├── integration/                   # Integration tests (multi-component)
│   ├── multi_agent_test.py
│   ├── test_agent_interactions.py
│   ├── test_agent_registration.py
│   └── test_error_handling.py
│
├── fixtures/                      # Test data and fixtures
│   └── (test data files)
│
├── mocks/                         # Mock objects and stubs
│   └── (mock implementations)
│
├── Phase Tests/                   # Phase-specific comprehensive tests
│   ├── test_phase0.py             # Infrastructure layer
│   ├── test_phase1.py             # Cognitive chassis
│   ├── test_phase2.py             # Mathematical workforce
│   ├── test_phase2_health.py
│   ├── test_phase3.py             # Meta-cognitive layer
│   ├── test_phase3_integration.py
│   ├── test_phase4.py             # Governance
│   ├── test_phase5_optimization.py
│   ├── test_phase5_phase6_integration.py
│   └── test_phase6_discovery.py   # Discovery system
│
├── Component Tests/               # Individual component tests
│   ├── test_bdi_agent.py
│   ├── test_bdi_integration.py
│   ├── test_blackboard.py
│   ├── test_orchestrator.py
│   ├── test_config.py
│   ├── test_cli.py
│   ├── test_cli_coverage.py
│   └── test_vector_database.py
│
├── Agent Tests/                   # Agent-specific tests
│   ├── test_supervisors.py
│   ├── test_specialists.py
│   ├── test_specialists_coverage.py
│   ├── test_calculus_specialists.py
│   ├── test_algebra_specialists.py
│   ├── test_linear_algebra_specialists.py
│   ├── test_geometry_specialists.py
│   ├── test_logic_specialists.py
│   ├── test_statistics_specialists.py
│   ├── test_physics_specialists.py
│   ├── test_physics_supervisors_coverage.py
│   └── test_remaining_supervisors_coverage.py
│
├── Infrastructure Tests/          # Infrastructure layer tests
│   ├── test_infrastructure_comprehensive.py
│   ├── test_infrastructure_modules.py
│   ├── test_watchdog_integration.py
│   ├── test_resource_governor.py
│   ├── test_dependencies.py
│   └── test_dependency_injection.py
│
├── Middleware Tests/              # Meta-cognitive layer tests
│   ├── test_meta_learning.py
│   ├── test_theorem_library.py
│   ├── test_conflict_resolution.py
│   ├── test_pattern_indexer.py
│   └── test_core_inference.py
│
├── Discovery Tests/               # Phase 6 discovery tests
│   ├── test_discovery_extended.py
│   ├── test_discovery_system_comprehensive.py
│   ├── test_discovery_algorithm_comprehensive.py
│   ├── test_discovery_conjecture_comprehensive.py
│   ├── test_deep_search_modules.py
│   ├── test_deep_search_comprehensive.py
│   ├── test_search_tree_manager_comprehensive.py
│   ├── test_conjecture_modules.py
│   ├── test_algorithm_modules.py
│   ├── test_algorithm_synthesizer.py
│   ├── test_curiosity_engine.py
│   └── test_imagination_engine.py
│
├── Optimization Tests/            # Phase 5 optimization tests
│   ├── test_optimization_comprehensive.py
│   └── test_parallel_and_formalization_comprehensive.py
│
├── Integration Tests/             # Multi-component integration
│   ├── test_e2e_integration.py
│   ├── test_e2e_domain_problems.py
│   ├── test_inter_component.py
│   ├── test_hardcore_integration.py
│   ├── multi_agent_integration_test.py
│   ├── multi_agent_test_suite.py
│   └── test_symbo_spectral_handoff.py
│
├── Stress Tests/                  # System stress and edge cases
│   ├── stress_test_runner.py
│   ├── stress_test_equations.py
│   ├── test_comprehensive_stress.py
│   ├── test_ultra_edge_13.py      # 13 ultra-edge equations
│   ├── test_ultra_edge_25.py      # 25 ultra-edge equations
│   ├── test_input_validation.py
│   └── test_resilience_tester.py
│
├── Coverage Tests/                # Test coverage improvement
│   ├── test_65_percent_coverage.py
│   ├── test_additional_65_coverage.py
│   ├── test_core_modules_coverage.py
│   ├── test_critical_coverage.py
│   ├── test_final_coverage.py
│   ├── test_remaining_coverage.py
│   ├── test_low_coverage_modules.py
│   ├── test_synthesis_coverage.py
│   ├── test_synthesis_modules_coverage.py
│   └── test_structural_synthesizer_coverage.py
│
├── Verification Tests/            # Verification layer tests
│   ├── test_verification.py
│   └── test_omdoc_schema.py
│
├── Security Tests/                # Security and safety tests
│   ├── test_security.py
│   └── test_security_monitor.py
│
├── Benchmark Tests/               # Performance benchmarks
│   └── benchmark_tests.py
│
├── Utility Tests/                 # Utility module tests
│   ├── test_utils_logging.py
│   └── test_nano_tensor.py
│
└── Special Tests/                 # Special-purpose tests
    ├── test_pilot_solver.py
    ├── crackfinder_agent.py       # Bug detection agent
    └── test_mock_embeddings_fix.py
```

## Test Markers

Tests are tagged with markers for selective execution:

### Phase Markers
```bash
pytest -m phase0    # Infrastructure tests
pytest -m phase1    # Cognitive chassis tests
pytest -m phase2    # Mathematical workforce tests
pytest -m phase3    # Meta-cognitive tests
pytest -m phase4    # Governance tests
pytest -m phase5    # Optimization tests
pytest -m phase6    # Discovery tests
```

### Category Markers
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Long-running tests
pytest -m security      # Security tests
```

### Negative Selection
```bash
pytest -m "not slow"    # Skip slow tests
pytest -m "not phase6"  # Skip phase 6 tests
```

## Shared Fixtures (conftest.py)

### Core Infrastructure Fixtures

```python
@pytest.fixture
def blackboard():
    """Fresh Blackboard instance"""

@pytest.fixture
def ams():
    """AgentManagementSystem instance"""

@pytest.fixture
def directory_facilitator():
    """DirectoryFacilitator instance"""

@pytest.fixture
def watchdog():
    """Watchdog instance"""

@pytest.fixture
def resource_governor():
    """ResourceGovernor instance"""
```

### System Fixtures

```python
@pytest.fixture
def phase0_system():
    """Complete Phase 0 infrastructure system"""

@pytest.fixture
def phase1_system():
    """Phase 1 system with cognitive chassis"""

@pytest.fixture
def phase2_system():
    """Phase 2 system with mathematical agents"""

@pytest.fixture
def full_system():
    """Complete SYMBO system (all phases)"""
```

### Agent Fixtures

```python
@pytest.fixture
def mock_supervisor():
    """Mock supervisor agent"""

@pytest.fixture
def mock_specialist():
    """Mock specialist agent"""

@pytest.fixture
def calculus_supervisor():
    """Real CalculusSupervisor instance"""

@pytest.fixture
def integration_specialist():
    """Real IntegrationSpecialist instance"""
```

### Problem Fixtures

```python
@pytest.fixture
def simple_problems():
    """Simple test problems"""

@pytest.fixture
def medium_problems():
    """Medium difficulty problems"""

@pytest.fixture
def edge_case_problems():
    """Edge case problems"""

@pytest.fixture
def ultra_edge_problems():
    """Ultra-edge pathological cases"""
```

## Running Tests

### All Tests
```bash
# Run entire test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src/symbo_agentic_reasoners --cov-report=html
```

### By Phase
```bash
pytest -m phase0    # Infrastructure
pytest -m phase1    # Cognitive
pytest -m phase2    # Mathematical
pytest -m phase3    # Meta-cognitive
pytest -m phase4    # Governance
pytest -m phase5    # Optimization
pytest -m phase6    # Discovery
```

### By Category
```bash
pytest tests/unit/                   # Unit tests
pytest tests/integration/            # Integration tests
pytest -k "stress"                   # Stress tests
pytest -k "edge"                     # Edge case tests
pytest tests/benchmark_tests.py      # Benchmarks
```

### By Component
```bash
# Core components
pytest tests/test_bdi_agent.py
pytest tests/test_blackboard.py
pytest tests/test_orchestrator.py

# Agents
pytest tests/test_supervisors.py
pytest tests/test_specialists.py
pytest tests/test_calculus_specialists.py

# Infrastructure
pytest tests/test_infrastructure_comprehensive.py
pytest tests/test_watchdog_integration.py

# Middleware
pytest tests/test_meta_learning.py
pytest tests/test_theorem_library.py

# Discovery
pytest tests/test_phase6_discovery.py
pytest tests/test_deep_search_comprehensive.py
```

### Specific Tests
```bash
# Run specific test file
pytest tests/test_orchestrator.py

# Run specific test function
pytest tests/test_orchestrator.py::test_problem_decomposition

# Run tests matching pattern
pytest -k "integration and not slow"

# Run failed tests only
pytest --lf  # last failed
pytest --ff  # failed first
```

### Fast vs Comprehensive
```bash
# Fast (skip slow tests)
pytest -m "not slow"

# Comprehensive (all tests including slow)
pytest

# Ultra-comprehensive (with stress tests)
pytest -v --tb=short
```

## Test Coverage

### Current Coverage
```bash
# Generate coverage report
pytest --cov=src/symbo_agentic_reasoners --cov-report=html
open htmlcov/index.html

# Coverage by module
pytest --cov=src/symbo_agentic_reasoners --cov-report=term-missing

# Coverage threshold (configured in pyproject.toml)
pytest --cov=src/symbo_agentic_reasoners --cov-fail-under=65
```

### Coverage Goals
- **Overall**: 65%+ (current threshold)
- **Core Components**: 80%+
- **Agents**: 70%+
- **Infrastructure**: 75%+
- **Middleware**: 70%+

## Test Patterns

### Unit Test Pattern
```python
def test_component_behavior():
    """Test isolated component behavior."""
    # Arrange
    component = MyComponent()

    # Act
    result = component.do_something()

    # Assert
    assert result == expected_value
```

### Integration Test Pattern
```python
@pytest.mark.integration
def test_multi_component_interaction(blackboard, supervisor, specialist):
    """Test interaction between components."""
    # Setup
    blackboard.post_entry(task)

    # Execute
    supervisor.route_task(task)
    result = specialist.solve(task)

    # Verify
    assert result.success
    assert blackboard.get_result(task.id) == expected
```

### Stress Test Pattern
```python
@pytest.mark.slow
def test_system_under_load():
    """Test system with high load."""
    problems = generate_problems(count=1000)

    results = []
    for problem in problems:
        result = system.solve(problem)
        results.append(result)

    # Verify success rate
    success_rate = sum(r.success for r in results) / len(results)
    assert success_rate > 0.95  # 95% success
```

### Edge Case Test Pattern
```python
@pytest.mark.parametrize("edge_case", [
    "1/0",  # Division by zero
    "log(0)",  # Undefined log
    "sqrt(-1)",  # Complex result
    "integrate exp(x^2) dx"  # Non-elementary
])
def test_edge_cases(edge_case):
    """Test edge case handling."""
    result = system.solve(edge_case)

    # Should handle gracefully
    assert not result.crashed
    assert result.error_message is not None
```

## Test Data

### Test Problem Sets

Located in `tests/fixtures/`:
- Simple problems (basic operations)
- Medium problems (standard techniques)
- Complex problems (multi-step)
- Edge cases (pathological)
- Ultra-edge cases (adversarial)

### Example Test Problems

**Calculus**:
- Simple: `differentiate x^2`
- Medium: `integrate x * sin(x) dx`
- Complex: `solve dy/dx = y^2 + x`
- Edge: `limit of sin(x)/x as x approaches 0`
- Ultra-edge: `integrate exp(x^2) dx` (non-elementary)

**Algebra**:
- Simple: `solve x + 2 = 5`
- Medium: `factor x^2 - 5x + 6`
- Complex: `solve system [x + y = 5, x - y = 1]`
- Edge: `solve x^2 + 1 = 0` (complex roots)
- Ultra-edge: `factor x^100 - 1`

## Debugging Tests

### Verbose Output
```bash
pytest -v              # Verbose
pytest -vv             # More verbose
pytest -vv --tb=long   # Full tracebacks
```

### Stop on Failure
```bash
pytest -x              # Stop on first failure
pytest --maxfail=3     # Stop after 3 failures
```

### Print Debugging
```bash
pytest -s              # Don't capture stdout (show prints)
pytest --capture=no    # Same as -s
```

### Specific Test Debugging
```bash
# Debug specific test
pytest tests/test_orchestrator.py::test_problem_decomposition -vv -s

# With pdb on failure
pytest --pdb

# With trace
pytest --trace
```

## Continuous Integration

Tests are designed for CI/CD:

```bash
# Fast CI (pre-commit)
pytest -m "not slow" --tb=short

# Full CI (pre-merge)
pytest --cov=src/symbo_agentic_reasoners --cov-fail-under=65

# Nightly (comprehensive)
pytest -v --cov=src/symbo_agentic_reasoners --cov-report=html
```

## Test Maintenance

### Adding New Tests

1. **Choose location**: unit/, integration/, or root
2. **Add appropriate markers**: @pytest.mark.phase2, etc.
3. **Use existing fixtures**: See conftest.py
4. **Follow naming**: test_*.py, test_*()
5. **Add docstrings**: Explain what test verifies

### Updating Tests

When code changes:
1. Run affected tests
2. Update assertions if behavior changed
3. Add new tests for new functionality
4. Ensure coverage doesn't drop

### Test Review Checklist

- [ ] Test name clearly describes what's tested
- [ ] Uses appropriate fixtures
- [ ] Has proper phase/category markers
- [ ] Includes docstring
- [ ] Asserts specific behavior
- [ ] Handles cleanup (if needed)
- [ ] Passes in isolation
- [ ] Maintains/improves coverage

## Performance

### Test Execution Time

- **Fast tests**: <1 second
- **Medium tests**: 1-10 seconds
- **Slow tests**: >10 seconds (marked with @pytest.mark.slow)
- **Full suite**: ~5-15 minutes

### Optimization Tips

```bash
# Parallel execution
pytest -n auto  # Use all CPUs (requires pytest-xdist)

# Faster failures
pytest --exitfirst  # Stop on first failure

# Incremental
pytest --stepwise  # Stop on failure, resume from failure
```

## Related Resources

- **pytest docs**: https://docs.pytest.org/
- **Coverage docs**: https://coverage.readthedocs.io/
- **pyproject.toml**: Test configuration
- **conftest.py**: Shared fixtures

---

Generated by SYMBO Documentation System
Last Updated: 2025-12-14
