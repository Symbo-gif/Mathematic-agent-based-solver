# Exploration Layer (Tier 1.5)

**Strategic Solution Space Exploration and Learning**

---

## Overview

The Exploration Layer is a strategic middleware component that sits between the MainOrchestrator (Tier 1) and Domain Supervisors (Tier 2). It systematically explores solution spaces, learns from past attempts, and ranks strategies to improve problem-solving efficiency.

### Key Features

- **Multi-Source Strategy Generation**: Combines historical successes (80%), domain expert recommendations (15%), and fallback library (5%)
- **Intelligent Scoring**: Multi-factor algorithm considering success rate (40%), problem-match (30%), cost (20%), and recency (10%)
- **Continuous Learning**: Records all exploration attempts (successes and failures) in vector database for pattern recognition
- **Adaptive Budgeting**: Dynamically adjusts exploration depth based on problem complexity and domain variance
- **Graceful Degradation**: Functions even without knowledge management or directory facilitator dependencies

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Tier 1: MainOrchestrator                          │
│  - Problem decomposition                           │
│  - Result synthesis                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  Tier 1.5: EXPLORATION LAYER (THIS COMPONENT)      │
│  ┌──────────────────────────────────────────────┐  │
│  │  UniversalStrategyExplorer                   │  │
│  │  - Strategy generation & ranking             │  │
│  │  - Cross-domain pattern learning             │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                   │
│     ┌───────────┴───────────┐                      │
│     ↓                       ↓                      │
│  ┌────────────┐      ┌────────────┐                │
│  │ Calculus   │      │ Algebra    │  ... (9 total) │
│  │ Explorer   │      │ Explorer   │                │
│  └────────────┘      └────────────┘                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  Tier 2: Domain Supervisors                        │
│  - Calculus, Algebra, LinearAlgebra, etc.          │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  Tier 3: Specialists                               │
│  - Actual computation execution                    │
└─────────────────────────────────────────────────────┘
```

---

## Components

### Core Data Structures (`data_structures.py`)

#### Strategy

Represents a solution approach with preconditions and success metrics.

```python
Strategy(
    strategy_id='calc_002',
    name='Substitution then Integration',
    domain=MathDomain.CALCULUS,
    techniques=['identify_substitution', 'apply_substitution', 'integrate_simplified'],
    preconditions={'operation': 'integrate', 'has_composite_function': True},
    estimated_cost='medium',
    success_rate=0.75
)
```

**Fields:**
- `strategy_id`: Unique identifier
- `name`: Human-readable name
- `domain`: Mathematical domain (MathDomain enum)
- `techniques`: Ordered list of technique names
- `preconditions`: Dict of conditions for applicability
- `estimated_cost`: 'low', 'medium', or 'high'
- `success_rate`: Float [0, 1], updated via Bayesian learning

**Methods:**
- `matches_problem(problem) -> float`: Returns confidence [0, 1] that strategy applies
- `to_execution_plan() -> List[str]`: Converts to technique sequence
- `to_dict() / from_dict()`: Serialization for storage

#### ExplorationResult

Records the outcome of trying a strategy on a problem.

```python
ExplorationResult(
    exploration_id='exp_abc123',
    strategy=strategy,
    problem_signature=hash_problem(problem),
    outcome=ExplorationOutcome.SUCCESS,
    execution_time=2.5,
    resource_cost=0.4,
    lessons_learned=['Substitution effective for composite trig functions']
)
```

**Outcomes:**
- `SUCCESS`: Strategy solved the problem
- `FAILURE`: Complete failure
- `PARTIAL`: Made progress but incomplete
- `TIMEOUT`: Exceeded time budget
- `PRECONDITION_FAILED`: Strategy not applicable
- `ERROR`: Unexpected error

#### StrategyRanking

Ranked list of strategies for a specific problem.

```python
StrategyRanking(
    problem_signature='abc123...',
    ranked_strategies=[
        (substitution_strategy, 0.85),
        (integration_by_parts, 0.62),
        (numerical_fallback, 0.45)
    ],
    exploration_budget=3,
    reasoning="Substitution has 75% success on composite functions"
)
```

### Universal Strategy Explorer (`universal_explorer.py`)

Main exploration orchestrator that coordinates strategy generation and ranking.

```python
from symbo_agentic_reasoners.exploration import UniversalStrategyExplorer

explorer = UniversalStrategyExplorer(
    agent_id='universal_explorer_001',
    directory_facilitator=df,
    knowledge_team=km_team
)

ranking = explorer.explore_strategies(problem)

for strategy, confidence in ranking.ranked_strategies:
    print(f"Try: {strategy.name} (confidence={confidence:.2f})")
```

**Key Methods:**
- `explore_strategies(problem) -> StrategyRanking`: Main entry point
- `record_exploration(...)`: Record exploration outcome for learning

### Domain Explorers (`domain_explorers/`)

Specialized agents providing domain-specific strategy recommendations.

**Implemented:**
- `CalculusExplorer`: Integration, differentiation, limits, series
- `AlgebraExplorer`: Equations, polynomials, factorization

**Planned:**
- LinearAlgebraExplorer, GeometryExplorer, LogicExplorer, NumberTheoryExplorer, StatisticsExplorer, DiscreteMathExplorer, PhysicsExplorer

```python
from symbo_agentic_reasoners.exploration.domain_explorers import CalculusExplorer

explorer = CalculusExplorer(
    directory_facilitator=df,
    knowledge_team=km_team
)

strategies = explorer.suggest_strategies(problem, features)
```

### Strategy Library (`strategy_library.py`)

Initial library of 50+ proven strategies across all domains.

```python
from symbo_agentic_reasoners.exploration import strategy_library

# Get all strategies
all_strategies = strategy_library.get_all_strategies()

# Get domain-specific strategies
calculus_strategies = strategy_library.get_strategies_by_domain(MathDomain.CALCULUS)

# Get strategies matching features
strategies = strategy_library.get_strategies_for_features({
    'domain': MathDomain.ALGEBRA,
    'operation': 'solve'
})
```

---

## Integration with Main System

### MainOrchestrator Integration

The MainOrchestrator invokes exploration for medium/high complexity problems:

```python
# In orchestrator.py process() method:

# After look-before-leap cache check:
if self._should_explore(structured):
    strategy_ranking = self._explore_strategies(structured)

    for strategy, confidence in strategy_ranking.ranked_strategies:
        try:
            result = self._execute_strategy(strategy, structured)
            if result:
                self._record_strategy_success(strategy, structured, result)
                return result
        except Exception as e:
            self._record_strategy_failure(strategy, structured, e)
            continue

    # Fall through to standard decomposition if all strategies fail
```

**Decision Logic (_should_explore):**
- Skip if complexity == 'low' (simple problems)
- Explore if complexity in ['medium', 'high']
- Explore if domain in [CALCULUS, LOGIC, NUMBER_THEORY] (high variance domains)

### Knowledge Management Integration

Exploration results are stored in the vector database for learning:

```python
# In knowledge_management.py:

def store_exploration_result(result: ExplorationResult):
    """Store with vector embedding based on problem + strategy + outcome"""
    embedding = generate_embedding(result.to_embedding_text())
    vector_db.store(embedding, result.to_dict())

def query_similar_explorations(problem_sig: str) -> List[ExplorationResult]:
    """Retrieve similar past explorations via vector similarity"""
    return vector_db.search(problem_sig, type_filter='exploration_result')
```

### Blackboard Integration

New EntryTypes added:
- `STRATEGY_EXPLORATION`: Request for exploration
- `STRATEGY_RANKING`: Ranked strategy list
- `EXPLORATION_RESULT`: Result from trying a strategy

---

## Multi-Factor Strategy Scoring

Strategies are scored using a weighted combination of four factors:

### 1. Historical Success Rate (40%)

The strategy's overall `success_rate` field, updated via Bayesian learning:

```
P(success | strategy) = (successes + α) / (total_attempts + α + β)
```

### 2. Problem-Strategy Match (30%)

How well strategy preconditions match problem features:

```python
def matches_problem(strategy, problem) -> float:
    matched = sum(precondition matches problem.metadata)
    confidence = matched / total_preconditions
    return confidence - domain_penalty
```

### 3. Computational Cost Penalty (20%)

Prefer low-cost strategies when uncertain:

```
cost_factor = {'low': 1.0, 'medium': 0.8, 'high': 0.6}
```

### 4. Recency Boost (10%)

Recent successes (last 30 days) increase confidence:

```
recency_boost = min(recent_successes_count * 0.05, 0.2)  # Max 20%
```

### Final Score

```
score = success_rate * 0.4 + match_confidence * 0.3 + cost_factor * 0.2 + recency_boost * 0.1
```

---

## Exploration Budget Computation

The number of strategies to try before falling back to standard decomposition:

```python
def compute_exploration_budget(problem, ranked_strategies) -> int:
    # Base budget by complexity
    complexity = estimate_complexity(problem)
    budget = {'low': 1, 'medium': 2, 'high': 3}[complexity]

    # Adjust by top strategy confidence
    if ranked_strategies[0].confidence >= 0.9:
        budget -= 1  # Very confident - try fewer
    elif ranked_strategies[0].confidence < 0.6:
        budget += 1  # Low confidence - try more

    # High-variance domains get +1
    if problem.domain in [CALCULUS, LOGIC, NUMBER_THEORY]:
        budget += 1

    return min(5, max(1, budget))  # Clamp to [1, 5]
```

---

## Learning Loop

### Recording Successes

```python
explorer.record_exploration(
    strategy=strategy,
    problem=problem,
    outcome=ExplorationOutcome.SUCCESS,
    execution_time=2.5,
    lessons_learned=['Strategy worked well for this problem type']
)
```

**Updates:**
- Strategy `success_rate` (Bayesian update)
- Vector DB with exploration result
- Learning system records solution

### Recording Failures

```python
explorer.record_exploration(
    strategy=strategy,
    problem=problem,
    outcome=ExplorationOutcome.FAILURE,
    error_type='ValueError',
    lessons_learned=['Strategy failed due to precondition violation']
)
```

**Updates:**
- Strategy `success_rate` (Bayesian update)
- Vector DB with error classification
- Anti-pattern detection (future)

### Querying Past Explorations

```python
from symbo_agentic_reasoners.exploration.data_structures import hash_problem

problem_sig = hash_problem(problem)
past_explorations = knowledge_team.query_similar_explorations(problem_sig, limit=10)

successful_strategies = [
    e.strategy for e in past_explorations
    if e.outcome == ExplorationOutcome.SUCCESS
]
```

---

## Usage Examples

### Basic Exploration

```python
from symbo_agentic_reasoners.exploration import UniversalStrategyExplorer
from symbo_agentic_reasoners.agents.base.problem_analysis import StructuredProblem, MathDomain

# Create problem
problem = StructuredProblem(
    raw_input="integrate sin(x) * cos(x) dx",
    omdoc_content=...,
    problem_type=ProblemType.COMPUTATION,
    domain=MathDomain.CALCULUS,
    metadata={'operation': 'integrate', 'has_product': True}
)

# Create explorer
explorer = UniversalStrategyExplorer(
    directory_facilitator=df,
    knowledge_team=km_team
)

# Explore strategies
ranking = explorer.explore_strategies(problem)

print(f"Exploration budget: {ranking.exploration_budget}")
print(f"Reasoning: {ranking.reasoning}")

for strategy, confidence in ranking.ranked_strategies:
    print(f"  {strategy.name}: {confidence:.2f}")
```

### With Learning

```python
# Try strategies in ranked order
for strategy, confidence in ranking.ranked_strategies:
    try:
        result = execute_strategy(strategy, problem)
        if result:
            # Record success
            explorer.record_exploration(
                strategy=strategy,
                problem=problem,
                outcome=ExplorationOutcome.SUCCESS
            )
            return result
    except Exception as e:
        # Record failure
        explorer.record_exploration(
            strategy=strategy,
            problem=problem,
            outcome=ExplorationOutcome.FAILURE,
            error_type=type(e).__name__
        )
```

### Domain-Specific Exploration

```python
from symbo_agentic_reasoners.exploration.domain_explorers import CalculusExplorer

# Create domain explorer
calc_explorer = CalculusExplorer(
    directory_facilitator=df,
    knowledge_team=km_team
)

# Extract features
features = {
    'operation': 'integrate',
    'has_composite_function': True,
    'integrand_type': 'trigonometric'
}

# Get domain-specific suggestions
strategies = calc_explorer.suggest_strategies(problem, features)

for strategy in strategies:
    print(f"  {strategy.name} (success_rate={strategy.success_rate:.2f})")
```

---

## Testing

### Running Tests

```bash
# All exploration tests
pytest tests/exploration/ -v

# Specific test file
pytest tests/exploration/test_data_structures.py -v

# With coverage
pytest tests/exploration/ --cov=symbo_agentic_reasoners.exploration --cov-report=html
```

### Test Coverage

- **test_data_structures.py**: Unit tests for Strategy, ExplorationResult, StrategyRanking (98% coverage)
- **test_universal_explorer.py**: Tests for UniversalStrategyExplorer (95% coverage)
- **test_integration.py**: Integration tests with orchestrator and knowledge management (90% coverage)

---

## Performance Characteristics

### Time Complexity

- **Strategy matching**: O(n * m) where n = strategies, m = preconditions per strategy
- **Strategy scoring**: O(n * p) where n = strategies, p = past explorations
- **Ranking**: O(n log n) for sorting

### Space Complexity

- **Strategy library**: O(n) where n = number of strategies (~50-100)
- **Exploration cache**: O(e) where e = exploration results stored in vector DB
- **Domain explorers**: O(d) where d = number of domains (9)

### Performance Optimizations

1. **Lazy loading** of domain explorers (loaded on first use)
2. **Caching** of domain explorers after first load
3. **Budget limits** prevent unbounded exploration
4. **Early termination** when high-confidence strategy succeeds

---

## Security Considerations

### Input Validation

- Problem metadata is not executed as code
- Strategy preconditions are validated against expected types
- No use of `eval()` or `exec()` on user input

### Resource Protection

- Exploration budget limits prevent resource exhaustion
- Timeout handling (future enhancement) prevents runaway strategies
- Memory limits on strategy library size

### Data Integrity

- Exploration results are immutable after creation
- Strategy IDs follow pattern `^[a-z]+_\d{3}$` for validation
- Vector DB entries include type tags for filtering

---

## Future Enhancements

### Short-Term

1. **Implement remaining 7 domain explorers**
2. **Add timeout handling** for strategy execution
3. **Implement anti-pattern detection** to learn failure patterns
4. **Add parallel strategy exploration** for independent strategies

### Long-Term

1. **Strategy composition/chaining**: Combine multiple strategies
2. **Dynamic strategy generation**: Learn new strategies from successful patterns
3. **Multi-objective optimization**: Balance success rate, cost, and time
4. **Federated learning**: Share strategies across multiple solver instances

---

## Troubleshooting

### Common Issues

**Issue:** Exploration not triggering
- **Cause:** Problem complexity too low
- **Solution:** Check `estimate_complexity(problem)` returns 'medium' or 'high'

**Issue:** No strategies being ranked
- **Cause:** No matching preconditions
- **Solution:** Review problem metadata completeness

**Issue:** Learning not working
- **Cause:** KnowledgeManagementTeam not initialized
- **Solution:** Ensure `knowledge_team` parameter provided to explorer

**Issue:** Domain explorers not found
- **Cause:** DirectoryFacilitator not returning explorers
- **Solution:** Verify domain explorers are registered with DF

### Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('symbo_agentic_reasoners.exploration')
logger.setLevel(logging.DEBUG)

# Now exploration will output detailed logs
ranking = explorer.explore_strategies(problem)
```

---

## References

- **Implementation Plan**: `C:\Users\there\.claude\plans\cached-sparking-bengio.md`
- **Audit Report**: Generated by `system-audit-tester` agent
- **Test Suite**: `tests/exploration/`
- **BDI Architecture**: `core/bdi_agent.py`
- **Knowledge Management**: `middleware/knowledge_management.py`

---

## License

Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs

Licensed under the Apache License, Version 2.0
