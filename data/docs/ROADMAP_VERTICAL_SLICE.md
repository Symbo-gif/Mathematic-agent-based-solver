# SYMBO_AGENTIC_REASONERS: Vertical Slice Roadmap

## Executive Summary

This roadmap transforms SYMBO from a well-architected framework into a functioning
mathematical reasoning system. The strategy is **vertical slice first**: make one
complete path work end-to-end before expanding horizontally.

**Target Vertical Slice**: Arithmetic + Algebra (basic to polynomial)
**End Goal**: Problems solved via real BDI agents → verified → train SymboLLM

---

## Phase 0: Foundation Repairs (Week 1-2)

### 0.1 Dynamic Resource Detection

**Current**: Hardcoded 8GB VRAM, 32GB RAM
**Target**: Detect actual hardware, adjust constraints dynamically

```python
# infrastructure/hardware_detector.py
class HardwareDetector:
    def detect_vram(self) -> float:
        """Query nvidia-smi for actual VRAM"""
    def detect_ram(self) -> float:
        """Query psutil for actual RAM"""
    def calculate_max_concurrent_agents(self) -> int:
        """Based on actual resources, how many cognitive agents?"""
```

**Files to modify**:
- `infrastructure/ams.py`: Replace hardcoded MAX_VRAM_GB with detection
- `config.py`: Add auto-detect mode

### 0.2 Remove SolverEngine Bypass

**Current**: `SolverEngine.solve()` bypasses all agent infrastructure
**Target**: Route ALL solving through proper Orchestrator → Supervisor → Specialist pipeline

**Files to modify**:
- `core/solver_engine.py`: Make it a thin wrapper that calls `MainOrchestrator.process()`
- OR: Create `core/user_interface.py` that properly uses the agent system

```python
# New approach
class MathSolver:
    """User-facing API that uses the full agent pipeline"""

    def __init__(self):
        self.phase0 = Phase0System()
        self.orchestrator = MainOrchestrator(
            df=self.phase0.df,
            blackboard=self.phase0.blackboard,
            agent_pool=AgentPool(ams=self.phase0.ams)
        )
        self.harvester = ThoughtTraceHarvester()

    def solve(self, problem: str) -> SolveResult:
        # Parse
        structured = ProblemAnalysisTeam().process(problem)

        # Solve via agents
        result = self.orchestrator.process(structured)

        # Harvest trace if verified
        if result.status == VERIFIED:
            self.harvester.capture_trace(...)

        return result
```

---

## Phase 1: Implement Real BDI for Algebra Slice (Week 2-4)

### 1.1 BDI Implementation Pattern

Every agent currently has stub BDI methods. We need a working pattern.

**Target Architecture**:
```
update_beliefs():  Read Blackboard for tasks matching my domain
deliberate():      If task found → create Intention with steps
execute_step():    Execute current step, post result to Blackboard
```

### 1.2 Implement ArithmeticSpecialist BDI (First Agent)

**File**: `agents/specialists/algebra/arithmetic_specialist.py`

```python
class ArithmeticSpecialist(BDIAgent):

    def update_beliefs(self):
        """Read pending arithmetic tasks from Blackboard"""
        if not self.blackboard:
            return

        # Query for tasks I can handle
        tasks = self.blackboard.query_entries(
            tags=['arithmetic', 'task'],
            status=EntryStatus.PENDING
        )

        for task in tasks:
            # Add belief about pending work
            self.add_belief(
                predicate=f'pending_task_{task.entry_id}',
                content=task,
                confidence=1.0,
                source='blackboard'
            )

    def deliberate(self) -> List[Intention]:
        """Create intentions for pending tasks"""
        intentions = []

        for predicate, belief in self.beliefs.items():
            if predicate.startswith('pending_task_') and belief.content.status == EntryStatus.PENDING:
                task = belief.content

                # Analyze operation needed
                operation = task.metadata.get('operation', 'compute')

                # Create plan based on operation
                if operation in ['add', 'subtract', 'multiply', 'divide', 'compute']:
                    steps = ['claim_task', 'parse_expression', 'compute', 'verify', 'post_result']
                else:
                    steps = ['claim_task', 'analyze', 'compute', 'verify', 'post_result']

                intention = Intention(
                    plan_id=f'solve_{task.entry_id}',
                    steps=steps,
                    target_desire='solve_arithmetic',
                    metadata={'task_entry': task}
                )
                intentions.append(intention)

        return intentions

    def execute_step(self, intention: Intention):
        """Execute one step - delegate to SymPy, never compute directly"""
        action = intention.get_current_action()
        task = intention.metadata['task_entry']

        if action == 'claim_task':
            # Mark task as in-progress
            self.blackboard.update_entry_status(task.entry_id, EntryStatus.IN_PROGRESS)
            intention.advance()

        elif action == 'parse_expression':
            # Delegate parsing to safe_sympify
            expr_str = task.metadata.get('sympy_expr') or task.metadata.get('raw_input')
            try:
                expr = safe_sympify(expr_str)
                self.add_belief('parsed_expr', expr)
                intention.advance()
            except Exception as e:
                self._post_failure(task, str(e))

        elif action == 'compute':
            # Delegate to SymPy
            expr = self.get_belief('parsed_expr').content
            operation = task.metadata.get('operation', 'compute')

            try:
                result = self._delegate_to_sympy(expr, operation)
                self.add_belief('computed_result', result)
                intention.advance()
            except Exception as e:
                self._post_failure(task, str(e))

        elif action == 'verify':
            # Basic verification - TODO: integrate with VerificationCore
            result = self.get_belief('computed_result').content
            self.add_belief('verified_result', result)
            intention.advance()

        elif action == 'post_result':
            # Post result to Blackboard
            result = self.get_belief('verified_result').content
            self._post_success(task, result)

            # Clean up beliefs
            self.remove_belief(f'pending_task_{task.entry_id}')
            self.remove_belief('parsed_expr')
            self.remove_belief('computed_result')
            self.remove_belief('verified_result')
            intention.advance()

    def _delegate_to_sympy(self, expr, operation: str):
        """Delegate computation to SymPy - agent NEVER computes"""
        if operation == 'compute':
            return sp.simplify(expr)
        elif operation == 'factor':
            return sp.factor(expr)
        elif operation == 'expand':
            return sp.expand(expr)
        # ... etc
```

### 1.3 Implement AlgebraSupervisor BDI

The supervisor's job is to route, not compute.

```python
class AlgebraSupervisor(BDIAgent):

    def update_beliefs(self):
        """Read pending algebra tasks from Blackboard"""
        tasks = self.blackboard.query_entries(
            tags=['algebra', 'task'],
            status=EntryStatus.PENDING
        )
        for task in tasks:
            self.add_belief(f'pending_algebra_{task.entry_id}', task)

    def deliberate(self) -> List[Intention]:
        """Decide which specialist should handle each task"""
        intentions = []

        for predicate, belief in self.beliefs.items():
            if predicate.startswith('pending_algebra_'):
                task = belief.content

                # Analyze and route
                specialist = self._determine_specialist(task)

                intention = Intention(
                    plan_id=f'route_{task.entry_id}',
                    steps=['analyze_task', 'route_to_specialist', 'await_result', 'aggregate'],
                    target_desire='delegate_algebra',
                    metadata={'task': task, 'target_specialist': specialist}
                )
                intentions.append(intention)

        return intentions

    def _determine_specialist(self, task) -> str:
        """Route based on task analysis"""
        raw_input = task.metadata.get('raw_input', '')
        operation = task.metadata.get('operation', '')

        # Routing logic
        if any(kw in raw_input.lower() for kw in ['prime', 'factor', 'gcd', 'modulo']):
            return 'number_theory'
        elif any(kw in operation for kw in ['polynomial', 'roots', 'groebner']):
            return 'polynomial'
        else:
            return 'arithmetic'
```

### 1.4 Implement MainOrchestrator BDI

```python
class MainOrchestrator(BDIAgent):

    def update_beliefs(self):
        """Orchestrator reads from input queue and Blackboard"""
        # Check for new problems in input queue
        # Check for completed results on Blackboard
        results = self.blackboard.query_entries(
            entry_type=EntryType.PARTIAL_RESULT,
            status=EntryStatus.VERIFIED
        )
        for result in results:
            task_id = result.metadata.get('task_id')
            self.add_belief(f'completed_{task_id}', result)

    def deliberate(self) -> List[Intention]:
        """Generate routing intentions"""
        # This is called by process() when a new problem arrives
        # The intention is to decompose and route
        pass
```

---

## Phase 2: Integrate Verification Core (Week 4-5)

### 2.1 Fix LogicChecker

**Current**: Pattern matching with `pass` stubs
**Target**: Real SymPy-based verification

```python
class LogicCheckerAgent(BDIAgent):

    def check(self, candidate_result, original_problem) -> tuple:
        """Verify result using symbolic computation"""
        violations = []

        # Get original expression and result
        original_expr = original_problem.get('sympy_expr')
        result_expr = safe_sympify(str(candidate_result))

        # Check 1: For equations, verify solution satisfies
        if original_problem.get('operation') == 'solve':
            for var, val in self._extract_solutions(result_expr):
                substituted = original_expr.subs(var, val)
                if not sp.simplify(substituted) == 0:
                    violations.append(f'solution_invalid: {var}={val}')

        # Check 2: For derivatives, verify by integration
        if original_problem.get('operation') in ['diff', 'derivative']:
            # d/dx(result) should equal original if we integrate
            pass

        # Check 3: Domain violations
        violations.extend(self._check_domain_violations(result_expr))

        return (len(violations) == 0, violations)
```

### 2.2 Add Z3 Solver for Algebraic Verification

```python
# verification/z3_checker.py
from z3 import *

class Z3Verifier:
    """Use Z3 SMT solver for algebraic verification"""

    def verify_equality(self, expr1, expr2, variables: List[str]) -> bool:
        """Verify two expressions are equivalent for all variable values"""
        solver = Solver()

        # Convert SymPy to Z3
        z3_expr1 = self._sympy_to_z3(expr1, variables)
        z3_expr2 = self._sympy_to_z3(expr2, variables)

        # Check if they can ever be different
        solver.add(z3_expr1 != z3_expr2)

        # If unsatisfiable, they're always equal
        return solver.check() == unsat
```

---

## Phase 3: Add Lean4 Integration (Week 5-7)

### 3.1 Lean4 Subprocess Wrapper

```python
# verification/lean4_verifier.py
import subprocess
import tempfile

class Lean4Verifier:
    """Formal verification via Lean4 subprocess"""

    def __init__(self, lean_path: str = "lean"):
        self.lean_path = lean_path
        self._check_installation()

    def verify_proof(self, statement: str, proof: str) -> bool:
        """Submit statement+proof to Lean4, return if it type-checks"""
        lean_code = self._generate_lean_file(statement, proof)

        with tempfile.NamedTemporaryFile(suffix='.lean', delete=False) as f:
            f.write(lean_code.encode())
            f.flush()

            result = subprocess.run(
                [self.lean_path, f.name],
                capture_output=True,
                timeout=60
            )

            return result.returncode == 0

    def _generate_lean_file(self, statement: str, proof: str) -> str:
        """Generate Lean4 file from mathematical statement"""
        return f'''
import Mathlib.Tactic

theorem symbo_verification : {statement} := by
  {proof}
'''
```

### 3.2 Integrate with FormalTranslator

The existing `FormalTranslator` agent should be enhanced to output Lean4.

```python
class FormalLanguageTranslator(BDIAgent):

    def translate_to_lean4(self, sympy_expr, statement_type: str) -> str:
        """Convert SymPy expression to Lean4 syntax"""
        # Map SymPy operations to Lean4 Mathlib
        pass
```

---

## Phase 4: Thought Trace Harvesting Pipeline (Week 7-8)

### 4.1 Wire Harvester into Solve Pipeline

```python
class ThoughtTraceCapture:
    """Captures reasoning trace during problem solving"""

    def __init__(self):
        self.trace = ThoughtTrace(
            trace_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            original_query="",
            # ... initialize all fields
        )

    def record_orchestrator_decision(self, decomposition: List[str]):
        self.trace.orchestrator_decomposition = decomposition

    def record_specialist_invocation(self, agent_id: str, operation: str):
        self.trace.specialist_agents_invoked.append(agent_id)

    def record_symbolic_step(self, expr: str):
        self.trace.symbolic_expressions.append(expr)

    def finalize(self, result: str, status: VerificationStatus):
        self.trace.final_answer = result
        self.trace.verification_status = status
        return self.trace
```

### 4.2 Integrate with Agent BDI Loops

Every agent should report to the trace capture:

```python
def execute_step(self, intention: Intention):
    action = intention.get_current_action()

    # Record to trace
    if self.trace_capture:
        self.trace_capture.record_specialist_invocation(self.agent_id, action)

    # ... rest of execution
```

---

## Phase 5: SymboLLM Training Integration (Week 8-10)

### 5.1 Training Data Format

```python
@dataclass
class TrainingExample:
    """Single training example for SymboLLM"""
    prompt: str           # Problem statement
    reasoning_trace: str  # Step-by-step reasoning
    answer: str          # Final answer
    category: str        # Domain (algebra, calculus, etc.)
    complexity: float    # For curriculum learning
```

### 5.2 Auto-Training Trigger

```python
class SymboLLMTrainer:
    """Manages continuous learning from verified traces"""

    def __init__(self, model: SymboLLMCore, min_batch_size: int = 32):
        self.model = model
        self.pending_examples = []
        self.min_batch_size = min_batch_size

    def add_verified_trace(self, trace: ThoughtTrace):
        """Add verified trace to training queue"""
        example = self._trace_to_example(trace)
        self.pending_examples.append(example)

        if len(self.pending_examples) >= self.min_batch_size:
            self._train_batch()

    def _train_batch(self):
        """Train on accumulated examples"""
        if not TORCH_AVAILABLE:
            # Store for later
            return

        # Convert to tensors
        # Run training step
        # Save checkpoint
        self.model.training_examples += len(self.pending_examples)
        self.pending_examples = []
        self.model.save_checkpoint("data/models/symbo_llm_latest.pt")
```

---

## Phase 6: Multi-Agent Scaling (Week 10-12)

### 6.1 Dynamic Agent Activation Based on Resources

```python
class SmartAgentPool:
    """Resource-aware agent lifecycle management"""

    def __init__(self, ams: AgentManagementSystem):
        self.ams = ams
        self.available_vram = self._detect_vram()
        self.vram_per_cognitive_agent = 5.5  # GB, configurable

    def max_concurrent_cognitive_agents(self) -> int:
        """How many cognitive agents can run simultaneously?"""
        # Reserve 2GB for system
        usable = self.available_vram - 2.0
        return max(1, int(usable / self.vram_per_cognitive_agent))

    def can_activate_parallel(self, count: int) -> bool:
        """Check if we can run N agents in parallel"""
        return count <= self.max_concurrent_cognitive_agents()
```

### 6.2 Enable Parallel Solving for Conflict Detection

With sufficient resources, allow multiple specialists to solve same problem:

```python
class ParallelSolver:
    """Solve with multiple specialists for consensus"""

    async def solve_with_consensus(self, problem) -> Result:
        if self.agent_pool.can_activate_parallel(2):
            # Run two specialists in parallel
            result1 = await self.specialist1.solve(problem)
            result2 = await self.specialist2.solve(problem)

            if result1 != result2:
                # Trigger conflict resolution
                return await self.conflict_resolver.resolve(result1, result2)

            return result1
        else:
            # Fall back to single specialist
            return await self.specialist1.solve(problem)
```

---

## Implementation Order (Strict Sequence)

### Sprint 1: Foundation (Week 1-2)
1. [ ] Hardware detection in AMS
2. [ ] Remove SolverEngine bypass, create proper MathSolver facade
3. [ ] Write integration test: problem → orchestrator → result

### Sprint 2: First Working Agent (Week 2-4)
4. [ ] Implement ArithmeticSpecialist BDI (full cycle)
5. [ ] Implement AlgebraSupervisor BDI (routing)
6. [ ] Implement MainOrchestrator BDI
7. [ ] End-to-end test: "2 + 2" through full pipeline

### Sprint 3: Verification (Week 4-5)
8. [ ] Fix LogicChecker with real SymPy verification
9. [ ] Add Z3 algebraic verification
10. [ ] Integration test: bad result gets rejected

### Sprint 4: Lean4 (Week 5-7)
11. [ ] Lean4 subprocess wrapper
12. [ ] FormalTranslator enhancement
13. [ ] Test: polynomial identity formally verified

### Sprint 5: Training Pipeline (Week 7-8)
14. [ ] Thought trace capture wired to agents
15. [ ] Harvester persists verified traces
16. [ ] Test: solve problem → trace saved to data/traces/

### Sprint 6: SymboLLM Learning (Week 8-10)
17. [ ] Training integration with harvester
18. [ ] Curriculum learning by complexity
19. [ ] Test: 100 problems → model improves

### Sprint 7: Scale Up (Week 10-12)
20. [ ] Resource-aware parallel activation
21. [ ] Conflict resolution with real conflicts
22. [ ] Full algebra domain working

---

## Success Criteria

### Vertical Slice Complete When:
1. `MathSolver.solve("factor x^2 - 4")` returns `(x-2)(x+2)` via:
   - MainOrchestrator (BDI deliberation)
   - AlgebraSupervisor (routes to polynomial)
   - PolynomialSpecialist (delegates to SymPy)
   - VerificationCore (confirms via differentiation)
   - Result marked VERIFIED

2. ThoughtTrace captured includes:
   - orchestrator_decomposition: ["route_to_algebra"]
   - supervisor_strategy: "polynomial_specialist"
   - specialist_agents_invoked: ["polynomial_specialist_001"]
   - verification_status: VERIFIED

3. After 100 verified problems:
   - `symbo_llm_latest.pt` checkpoint exists
   - `model.training_examples >= 100`
   - Knowledge store has entries

### Full System Complete When:
- All 6 math domains have working BDI agents
- Conflict resolution handles actual disagreements
- Lean4 verification for formal proofs
- SymboLLM assists (not replaces) specialists
- Imagination Engine generates, solves, and learns

---

## Files to Create/Modify

### New Files:
- `infrastructure/hardware_detector.py`
- `core/math_solver.py` (proper user API)
- `verification/z3_checker.py`
- `verification/lean4_verifier.py`
- `training/symbo_trainer.py`

### Major Modifications:
- `core/orchestrator.py` - Implement real BDI methods
- `agents/supervisors/*.py` - Implement real BDI methods
- `agents/specialists/**/*.py` - Implement real BDI methods
- `verification/verification_core.py` - Real verification logic
- `optimization/distillation/harvester.py` - Wire to solve pipeline

### Configuration:
- `config.py` - Add hardware auto-detection
- `pyproject.toml` - Add z3-solver, lean4 deps

---

## Resource Requirements

### Development:
- Python 3.10+
- PyTorch (for SymboLLM training)
- Z3 Solver (`pip install z3-solver`)
- Lean4 (external installation)

### Runtime (Minimum):
- 8GB VRAM: Single cognitive agent mode
- 16GB RAM: Full agent pool in standby
- SSD: For trace persistence

### Runtime (Recommended for parallel):
- 16GB+ VRAM: 2-3 parallel cognitive agents
- 32GB RAM: Full system with training
- GPU: CUDA-capable for SymboLLM training
