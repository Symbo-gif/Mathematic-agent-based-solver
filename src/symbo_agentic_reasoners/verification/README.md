# Verification

Mathematical result verification and proof checking for the Symbo Mathematical Multi-Agentic Reasoning System.

## Overview

The Verification module implements the "conscience" of the system - the components that enforce mathematical truth. NO result from any solver is permitted to be presented to the user until stamped "Approved" by the verification layer.

**Phase**: Phase 1 - Cognitive Chassis (Step 4: The Immune System)
**Core Philosophy**: "Trust but Verify" - All results must be formally verified before output

## Problem Being Solved

**The Hallucination Risk**: LLMs can generate plausible-looking but incorrect mathematical results. Without verification:
- False solutions presented as truth
- Calculation errors compound through multi-step problems
- Assumption gaps lead to invalid derivations
- User trust eroded by unreliable results

The verification layer eliminates this risk through two-layered defense.

## Architecture

```
Mathematical Result
        |
        v
+------------------+
|  Logic Checker   |  <-- First Line of Defense
|  (Rule-Based)    |      Detects illegal moves
+------------------+
        |
        v (if passed)
+------------------+
|   Ax-Prover      |  <-- Second Line of Defense
| (Computational   |      Verifies by recomputation
|  Verification)   |
+------------------+
        |
        v
  APPROVED / REJECTED
```

## Core Components

### LogicCheckerAgent
**First Line of Defense - Rule-Based Validation**

| Responsibility | Description |
|----------------|-------------|
| Division by Zero | Ensures denominators verified non-zero |
| Log of Negative | Detects log applied to negative values |
| Sqrt Domain | Checks sqrt of negative in real domain |
| Undefined Limits | Identifies undefined limit expressions |
| Domain Violations | General domain constraint checking |

**Illegal Moves Detected:**
- Division by variable without confirming non-zero
- Logarithm of negative number (real domain)
- Square root of negative (real domain)
- Undefined mathematical operations
- Unstated assumptions in derivations

**Usage:**
```python
from symbo_agentic_reasoners.verification.verification_core import LogicCheckerAgent

checker = LogicCheckerAgent('logic_checker_001')

# Check candidate solution
candidate_result = "x = 5 / (y - 2)"
original_problem = {"equation": "5x = y - 2"}

is_valid, violations = checker.check(candidate_result, original_problem)

if not is_valid:
    print(f"Violations found: {violations}")
    # violations might be ['division_by_zero'] if y=2 not excluded
```

**Why This Matters:**
Logic checking catches the "Assumption Gap" - unstated assumptions that make solutions conditionally valid. For example:
- Solution: `x = 1/(y-2)`
- Assumption Gap: Assumes y ≠ 2 without stating it
- Logic Checker: Flags division_by_zero violation

### SimplifiedVerifierAgent
**Second Line of Defense - Computational Verification**

**Verification Strategy:**
1. **Re-Computation**: Solve problem independently using native engine
2. **Solution Comparison**: Compare candidate vs verified solution
3. **Substitution Check**: Substitute solution back into original equation
4. **Numerical Validation**: Check solution within tolerance

**Usage:**
```python
from symbo_agentic_reasoners.verification.verification_core import SimplifiedVerifierAgent

verifier = SimplifiedVerifierAgent('verifier_001')

# Verify candidate solution
problem = "solve x^2 - 5x + 6 = 0"
candidate_solution = "x = 2 or x = 3"

verification_status = verifier.verify(problem, candidate_solution)

# verification_status in ['VERIFIED', 'REJECTED', 'INCONCLUSIVE']
```

**Verification Results:**
- **VERIFIED**: Solution confirmed correct
- **REJECTED**: Solution proven incorrect
- **INCONCLUSIVE**: Could not verify (problem too complex, timeout, etc.)

### AxProverAgent (Phase 2 Enhancement)
**Formal Theorem Prover Integration**

Future enhancement connecting to formal proof assistants:
- Lean 4 - For pure mathematics
- Coq - For constructive proofs
- Isabelle - For HOL proofs

Currently simplified to computational verification in Phase 1.

## Verification Workflow

```
1. SOLUTION GENERATED
   └─> Specialist/Supervisor produces result

2. LOGIC CHECKING (Fast)
   └─> LogicCheckerAgent scans for illegal moves
       ├─> If violations found → REJECT
       └─> If clean → Continue

3. COMPUTATIONAL VERIFICATION (Moderate)
   └─> SimplifiedVerifierAgent re-solves
       ├─> Solutions match → VERIFIED
       ├─> Solutions differ → REJECTED
       └─> Timeout → INCONCLUSIVE

4. FORMAL PROOF (Slow - Phase 2)
   └─> AxProverAgent generates formal proof
       ├─> Proof valid → FORMALLY_VERIFIED
       ├─> Proof invalid → REJECTED
       └─> Timeout → Fallback to computational

5. STAMP RESULT
   └─> Attach verification status to solution
       └─> Only VERIFIED/FORMALLY_VERIFIED output to user
```

## Verification Guarantees

**What Verification DOES Guarantee:**
- No division by zero in final answer
- No domain violations (log negative, sqrt negative real, etc.)
- Solution satisfies original equation (within numerical tolerance)
- Derivation steps are logically valid

**What Verification DOES NOT Guarantee (Yet):**
- Complete formal proof (Phase 1 version)
- Optimal solution (may be correct but not simplest)
- Uniqueness (may miss other valid solutions)
- Proof of impossibility (if no solution exists)

## Integration Points

**Called By:**
- Orchestrator - Before returning result to user
- Specialists - Self-check before submission
- Supervisors - Validate specialist work

**Calls:**
- Native Solver Engine - For re-computation
- Blackboard - To log verification results
- Error Handler - When verification fails

## Configuration

```python
from symbo_agentic_reasoners.config import get_config

config = get_config()

# Verification timeouts
logic_check_timeout = config.timeouts.verification_logic_check
proof_timeout = config.timeouts.proof
verification_tolerance = config.verification.numerical_tolerance
```

## Design Principles

### 1. NO SYMPY PHILOSOPHY COMPLIANCE

**Critical**: Verification uses native solver engine for re-computation, NOT SymPy. This ensures:
- Same computational path as original solve
- Consistent numerical precision
- No SymPy dependency creep

### 2. Defense in Depth

Multiple verification layers catch different error types:
- Logic Checker: Fast, catches obvious errors
- Computational Verifier: Moderate, catches calculation errors
- Formal Prover (Phase 2): Slow, provides mathematical certainty

### 3. Conservative Rejection

When in doubt, verification **rejects**. Better to:
- Reject correct solution (ask user to retry)
- Than accept incorrect solution (erode trust)

### 4. Transparency

All verification results logged:
- What was checked
- Which tests passed/failed
- Why rejected (if applicable)
- Time taken for verification

## Testing

```bash
# Test logic checker
pytest tests/test_verification.py -k logic_checker

# Test simplified verifier
pytest tests/test_verification.py -k simplified_verifier

# Comprehensive verification tests
pytest tests/test_verification.py

# Integration tests
pytest tests/test_phase1.py -k verification
```

## Example Verification Results

**Success Case:**
```python
Problem: "solve x^2 - 4 = 0"
Candidate: "x = 2 or x = -2"

Logic Check: ✓ No illegal moves
Computational: ✓ Solutions verified
Status: VERIFIED
```

**Rejection - Division by Zero:**
```python
Problem: "solve (x+1)/(x-2) = 3"
Candidate: "x = 7"

Logic Check: ✓ No illegal moves in final answer
Computational: ✓ x=7 satisfies equation
But Rejected: Domain restriction x ≠ 2 not stated
Status: REJECTED (missing domain constraint)
```

**Rejection - Wrong Answer:**
```python
Problem: "integrate x^2 dx"
Candidate: "x^3"  # Missing constant and coefficient

Logic Check: ✓ No illegal moves
Computational: ✗ Derivative of x^3 is 3x^2, not x^2
Status: REJECTED (incorrect solution)
```

## Future Enhancements (Phase 2+)

1. **Formal Proof Integration**
   - Lean 4 backend for pure math
   - Coq for constructive proofs
   - Automated theorem proving

2. **Proof Generation**
   - Generate human-readable proof steps
   - LaTeX export of formal proofs
   - Interactive proof exploration

3. **Counter-Example Search**
   - Automated search for counter-examples
   - Disproof by example
   - Domain boundary testing

4. **Proof Caching**
   - Cache verified proofs for reuse
   - Proof library integration
   - Lemma extraction and storage

## Key Insights

**Why Two Layers?**

Logic Checker is fast (milliseconds) but limited to rule-based patterns.
Computational Verifier is thorough but slower (seconds).
Together they provide fast-path for simple cases, deep verification for complex ones.

**The Assumption Gap:**

Many "wrong" mathematical solutions are conditionally correct - they work IF certain unstated assumptions hold. Logic Checker specializes in finding these gaps.

Example:
- Problem: Solve (x+1)/(x-2) = 3
- Solution: x = 7
- Gap: Works IF x ≠ 2 (unstated domain restriction)

**Why Not Just Re-Solve Every Time?**

We DO re-solve for verification, but we also check logic first because:
- Some errors detectable without re-solving (faster)
- Re-solving might reproduce same error (need independent check)
- Logic rules catch assumption gaps re-solving might miss

## Related Components

- `/core/solver_engine.py` - Used for re-computation verification
- `/core/native_calculus.py` - Native math for verification
- `/middleware/precondition_validation.py` - Pre-solve validation
- `/core/error_handler.py` - Handles verification failures

## Error Handling

**When Verification Fails:**
1. Log detailed failure reason
2. Optionally return problem to solver for retry
3. If repeated failures, escalate to supervisor
4. Never output unverified result to user

**Verification Error Types:**
- `VerificationTimeout`: Verification took too long
- `VerificationFailure`: Solution proven incorrect
- `LogicViolation`: Illegal mathematical operation detected
- `DomainError`: Solution outside valid domain

---

**Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs**
**Licensed under Apache License 2.0**
