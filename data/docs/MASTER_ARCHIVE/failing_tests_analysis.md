# Symbo Agentic Reasoners - Failing Tests Analysis

**Date:** 2025-12-14
**Auditor:** System Audit Agent
**Total Failing Tests:** 64
**Total Tests:** 3,647

---

## Executive Summary

The 64 failing tests in the Symbo Agentic Reasoners system fall into 8 distinct categories, with the primary root cause being **incomplete migration from SymPy to Native Symbolic Engine**. The system has a "NO SYMPY" philosophy but several tests and components still expect SymPy types or behaviors.

---

## Category 1: Test Expectations Using SymPy Types (CRITICAL)
**Count:** 14 tests
**Severity:** CRITICAL - Tests fundamentally incorrect
**Domain:** Cross-domain

### Affected Tests:
1. `test_conjecture_modules.py::TestConjectureFormalizer::test_operator_mappings`
2. `test_input_validation.py::TestSafeSympify::test_polynomial`
3. `test_input_validation.py::TestMathematicalConstraint::test_to_sympy_assumption`
4. `test_nano_tensor.py::TestNanoTensorInit::test_data_initialized_to_zero`
5. `test_nano_tensor.py::TestNanoTensorSymbolicOps::test_diff`
6. `test_nano_tensor.py::TestNanoTensorSymbolicOps::test_simplify`
7. `test_nano_tensor.py::TestNanoTensorDerivTree::test_deriv_tree`
8. `test_specialists_coverage.py::TestLimitEvaluator::test_detect_indeterminate_form_zero_over_zero`
9. `test_specialists_coverage.py::TestLimitEvaluator::test_apply_lhopital_tracking`
10. `test_verification.py::TestSimplifiedVerifierAgent::test_verify_derivative`
11. `test_verification.py::TestSimplifiedVerifierAgent::test_verify_integral`
12. `test_verification.py::TestSimplifiedVerifierAgent::test_verify_result_with_operation`
13. `test_verification.py::TestVerificationIntegration::test_two_stage_verification`
14. `test_curiosity_engine.py (unit)::TestInterestScorer::test_scorer_initialization`

### Root Cause:
Tests import `sympy as sp` and check for `sp.Add`, `sp.pi`, etc. but the implementation now uses `native_symbolic.Add`, `native_symbolic.pi`.

### Fix Required:
**File:** Multiple test files
**Action:** Update test assertions to use native symbolic types:
```python
# OLD (incorrect):
assert sp.Add in formalizer.OPERATOR_MAPPINGS
assert sp.pi in scorer.SPECIAL_VALUES

# NEW (correct):
from symbo_agentic_reasoners.core.native_symbolic import Add, pi
assert Add in formalizer.OPERATOR_MAPPINGS
assert pi in scorer.SPECIAL_VALUES or 'pi' in scorer.SPECIAL_VALUES
```

---

## Category 2: Parser Does Not Support Multi-Argument Functions (HIGH)
**Count:** 8 tests
**Severity:** HIGH - Core functionality gap
**Domain:** Parsing / Notation Translation

### Affected Tests:
1. `test_notation_translator.py::test_latex_to_sympy_sqrt`
2. `test_notation_translator.py::test_latex_to_sympy_trig`
3. `test_notation_translator.py::test_natural_to_sympy_derivative`
4. `test_notation_translator.py::test_natural_to_sympy_integral`
5. `test_notation_translator.py::test_sympy_latex_roundtrip`
6. `test_notation_translator.py::test_process_auto_detect`
7. `test_critical_coverage.py::TestNotationTranslatorComprehensive::test_latex_trig_functions`
8. `test_critical_coverage.py::TestNotationTranslatorComprehensive::test_latex_sqrt`

### Root Cause:
The LaTeX-to-native conversion creates invalid expressions like:
- `sqrt*(x)` instead of `sqrt(x)`
- `sin*(x) + cos*(x)` instead of `sin(x) + cos(x)`
- `diff*((x)**2, x)` instead of proper multi-arg function calls

Parser in `native_symbolic.py` does not handle:
1. Function calls without explicit parentheses
2. Multi-argument functions like `diff(expr, var)` or `integrate(expr, var)`

### Fix Required:
**File:** `src/symbo_agentic_reasoners/core/native_symbolic.py`
**Action:** Extend parser to handle:
1. Function application syntax `f(x)` where f is sin, cos, sqrt, etc.
2. Multi-argument functions `func(arg1, arg2, ...)`
3. LaTeX conversion should not insert `*` between function name and `(`

**File:** Notation translator (problem analysis team)
**Action:** Fix LaTeX/natural language conversion to produce valid native syntax

---

## Category 3: Equation System Solver - Eq() Parsing (HIGH)
**Count:** 4 tests
**Severity:** HIGH - Algebra solving broken
**Domain:** Algebra

### Affected Tests:
1. `test_specialists_coverage.py::TestEquationSystemSolver::test_solve_linear_system`
2. `test_specialists_coverage.py::TestEquationSystemSolver::test_solve_polynomial_system`
3. `test_specialists_coverage.py::TestEquationSystemSolver::test_classify_system_transcendental`
4. `test_hardcore_integration.py::TestHardEndToEndIntegration::test_full_pipeline_matrix_eigenvalue`

### Root Cause:
Parser fails on `Eq(x + y, 10)` syntax:
```
Failed to parse 'Eq(x + y, 10)': Unexpected token: Token(type=<TokenType.LPAREN: 8>, value='(')
```

The native parser does not support:
1. `Eq(lhs, rhs)` equation syntax
2. Matrix constructor `Matrix([[1, 2], [2, 1]])`

### Fix Required:
**File:** `src/symbo_agentic_reasoners/core/native_symbolic.py`
**Action:** Add support for:
1. `Eq` class and parsing of `Eq(lhs, rhs)`
2. `Matrix` class and parsing of nested list syntax

**Alternative:** Equation system solver should internally construct equations:
```python
# Instead of parsing "Eq(x + y, 10)"
# Directly create: Equation(parse_expr("x + y"), parse_expr("10"))
```

---

## Category 4: Limit Evaluation - Indeterminate Forms (HIGH)
**Count:** 4 tests
**Severity:** HIGH - Calculus functionality incomplete
**Domain:** Calculus

### Affected Tests:
1. `test_specialists_coverage.py::TestLimitEvaluator::test_evaluate_indeterminate_form`
2. `test_specialists_coverage.py::TestLimitEvaluator::test_evaluate_one_sided_limits`
3. `test_curiosity_engine.py::TestInterestScorer::test_special_value_detection`
4. `test_critical_coverage.py::TestFullPipelineIntegration::test_full_calculus_pipeline`

### Root Cause:
The native limit engine (`native_calculus.py`) cannot evaluate:
- `lim(sin(x)/x) as x -> 0` (returns NaN instead of 1)
- One-sided limits return `Mul(Integer(-1), Symbol('oo'))` instead of `-oo` (infinity)

Missing implementation:
1. L'Hopital's rule for 0/0 indeterminate forms
2. Proper infinity representation and comparison
3. Trigonometric limit identities

### Fix Required:
**File:** `src/symbo_agentic_reasoners/core/native_calculus.py`
**Action:** Implement:
1. L'Hopital's rule: `lim f(x)/g(x) = lim f'(x)/g'(x)` when 0/0 or inf/inf
2. Special limits table:
   - `sin(x)/x -> 1` as `x -> 0`
   - `(1 - cos(x))/x^2 -> 1/2` as `x -> 0`
   - `(e^x - 1)/x -> 1` as `x -> 0`
3. Proper negative infinity: `-oo` constant, not `Mul(-1, oo)`

---

## Category 5: Trigonometric Simplification (MEDIUM)
**Count:** 3 tests
**Severity:** MEDIUM - Common identity missing
**Domain:** Algebra/Trigonometry

### Affected Tests:
1. `test_hardcore_integration.py::TestHardEndToEndIntegration::test_full_pipeline_trigonometric_simplification`
2. `test_pilot_solver.py::TestPilotSolverEdgeCases::test_complex_expression`
3. `test_curiosity_engine.py::TestCuriosityEngineComprehensive::test_interest_scoring_zero`

### Root Cause:
`sin(x)**2 + cos(x)**2` is not simplified to `1`

The native symbolic engine's `simplify()` method does not apply trigonometric identities.

### Fix Required:
**File:** `src/symbo_agentic_reasoners/core/native_symbolic.py`
**Action:** In the `simplify()` method of `Add` class, add pattern matching for:
```python
# Pythagorean identity
sin(x)**2 + cos(x)**2 = 1
tan(x)**2 + 1 = sec(x)**2
1 + cot(x)**2 = csc(x)**2
```

Implementation approach:
```python
def simplify(self) -> Expr:
    # Check for sin^2 + cos^2 pattern
    terms = self.as_ordered_terms()
    sin_squared = None
    cos_squared = None
    for term in terms:
        if is_sin_squared(term):
            sin_squared = term
        if is_cos_squared(term):
            cos_squared = term
    if sin_squared and cos_squared and same_argument(sin_squared, cos_squared):
        # Replace sin^2(x) + cos^2(x) with 1
        remaining = [t for t in terms if t not in (sin_squared, cos_squared)]
        return Add(Integer(1), *remaining).simplify()
    ...
```

---

## Category 6: Polynomial Factoring (MEDIUM)
**Count:** 4 tests
**Severity:** MEDIUM - Algebra operation incomplete
**Domain:** Algebra

### Affected Tests:
1. `test_pilot_solver.py::TestPilotSolverExecution::test_execute_expand`
2. `test_pilot_solver.py::TestPilotSolverExecution::test_execute_factor`
3. `test_hardcore_integration.py::TestMultiTeamHandoff::test_algebra_to_calculus_handoff`
4. `test_specialists.py::TestPolynomialSpecialistOperations::test_process_factor`

### Root Cause:
1. `expand((1 + x)**2)` returns `(1 + x)**2` instead of `1 + 2*x + x**2`
2. `factor(x**2 + 2*x + 1)` returns `1 + x**2 + 2*x` instead of `(x + 1)**2`

The native symbolic engine:
- `expand()` is a stub that just calls `simplify()`
- `factor()` pattern recognition fails for perfect squares

### Fix Required:
**File:** `src/symbo_agentic_reasoners/core/native_symbolic.py`

1. **Implement `expand()`:**
```python
def expand(expr: Expr) -> Expr:
    """Expand products and powers."""
    if isinstance(expr, Pow):
        base, exp = expr.base, expr.exp
        if isinstance(exp, Integer) and exp.value > 0:
            # Use binomial expansion for (a + b)^n
            return binomial_expand(base, exp.value)
    if isinstance(expr, Mul):
        # Distribute multiplication over addition
        return distribute(expr)
    return expr
```

2. **Improve `factor()` pattern recognition:**
```python
def factor(expr: Expr) -> Expr:
    """Factor polynomial expressions."""
    # Perfect square: a^2 + 2ab + b^2 = (a + b)^2
    # Difference of squares: a^2 - b^2 = (a + b)(a - b)
    # Trial factorization for quadratics
    ...
```

---

## Category 7: Native Expression Method Compatibility (MEDIUM)
**Count:** 6 tests
**Severity:** MEDIUM - API mismatch
**Domain:** Core Infrastructure

### Affected Tests:
1. `test_input_validation.py::TestParsingPipelineIntegration::test_round_trip_preservation`
2. `test_nano_tensor.py::TestNanoTensorPolySolve::test_groebner_solve_system`
3. `test_nano_tensor.py::TestNanoTensorPolySolve::test_resultant`
4. `test_nano_tensor.py::TestNanoTensorTaylor::test_generate_taylor_with_value`
5. `test_nano_tensor.py::TestNanoTensorTaylor::test_compute_steady_state`
6. `test_input_validation.py::TestSafeSympify::test_polynomial`

### Root Cause:
Native `Expr` classes missing methods expected by tests:
- `Add.subs(symbol, value)` - takes wrong number of arguments (should be dict or two args)
- `Add.has(type)` - not implemented
- `Integer.subs()` - signature mismatch
- `NanoTensor.simplify()` - not implemented

### Fix Required:
**File:** `src/symbo_agentic_reasoners/core/native_symbolic.py`

Add missing method signatures:
```python
class Expr:
    def subs(self, *args, **kwargs) -> Expr:
        """Support both dict and positional argument forms."""
        if len(args) == 1 and isinstance(args[0], dict):
            return self._subs_dict(args[0])
        elif len(args) == 2:
            return self._subs_dict({args[0]: args[1]})
        raise TypeError(f"subs() expects dict or two arguments")

    def has(self, *types) -> bool:
        """Check if expression contains any of the given types."""
        if isinstance(self, types):
            return True
        for arg in self._get_args():
            if hasattr(arg, 'has') and arg.has(*types):
                return True
        return False
```

---

## Category 8: Prover Engine / Discovery System (LOW)
**Count:** 6 tests
**Severity:** LOW - Discovery features, not core math
**Domain:** Discovery/Deep Search

### Affected Tests:
1. `test_deep_search_comprehensive.py::TestSymPyProver::test_initialization`
2. `test_deep_search_comprehensive.py::TestSymPyProver::test_health_check`
3. `test_deep_search_comprehensive.py::TestSymPyProverExtended::test_has_transformations`
4. `test_deep_search_comprehensive.py::TestSymPyProverExtended::test_transformations_is_tuple`
5. `test_phase6_discovery.py::TestProverEngine::test_health_check`
6. `test_parallel_and_formalization_comprehensive.py::TestAutoFormalizationPipelineComplete::test_generate_sympy_implementation`

### Root Cause:
The `NativeSymbolicProver` class is missing:
- `transformations` attribute (expected to be a tuple)
- `health_check()` returns False

### Fix Required:
**File:** `src/symbo_agentic_reasoners/discovery/deep_search/prover_engine.py`
**Action:**
```python
class NativeSymbolicProver:
    def __init__(self):
        self.transformations = ()  # Add empty tuple
        ...

    def health_check(self) -> bool:
        """Return True if prover is operational."""
        return True  # Or implement actual health check
```

---

## Category 9: Test Expectation Mismatch (LOW)
**Count:** 5 tests
**Severity:** LOW - Test assertions need updating
**Domain:** Various

### Affected Tests:
1. `test_cli_coverage.py::TestMathSolverCLISolve::test_solve_problem_fallback_success`
2. `test_curiosity_engine.py::TestInterestScorer::test_score_zero_result`
3. `test_curiosity_engine.py::TestInterestScorer::test_score_unity_result`
4. `test_curiosity_engine.py::TestInterestScorer::test_score_pi_result`
5. `test_curiosity_engine.py (unit)::TestProblemGenerator::test_polynomial_factor_valid`

### Root Cause:
Test expectations don't match new native implementation:
- Test expects `specialist == 'sympy_fallback'` but native solver uses `'native_symbolic'`
- Interest scorer notes don't include expected keywords like "zero", "unity"
- Problem generator creates malformed expressions

### Fix Required:
**File:** Various test files
**Action:** Update assertions to match native implementation behavior

---

## Priority Fix Order

### Priority 1 - CRITICAL (Block Core Functionality)
1. **Parser multi-argument support** (Category 2) - Enables notation translation
2. **Eq() and Matrix parsing** (Category 3) - Enables equation solving
3. **L'Hopital's rule** (Category 4) - Enables limit evaluation

### Priority 2 - HIGH (Major Feature Gaps)
4. **Trigonometric simplification** (Category 5) - Common use case
5. **Polynomial expand/factor** (Category 6) - Core algebra operations
6. **subs() method signature** (Category 7) - API compatibility

### Priority 3 - MEDIUM (Cleanup)
7. **Update test assertions** (Categories 1, 9) - Test file corrections
8. **Prover engine attributes** (Category 8) - Discovery system

---

## Implementation Roadmap

### Phase 1: Parser Enhancement (2-3 days)
- Extend `native_symbolic.py` lexer/parser for multi-arg functions
- Add `Eq` class for equations
- Add `Matrix` class for linear algebra
- Fix notation translator LaTeX conversion

### Phase 2: Calculus Rules (2 days)
- Implement L'Hopital's rule in `native_calculus.py`
- Add special limits lookup table
- Fix infinity representation (`-oo` constant)

### Phase 3: Algebraic Operations (2 days)
- Implement proper `expand()` with binomial expansion
- Implement `factor()` with pattern recognition
- Add trigonometric identities to `simplify()`

### Phase 4: API Compatibility (1 day)
- Fix `subs()` method signatures
- Add `has()` method to Expr
- Update prover engine attributes

### Phase 5: Test Updates (1 day)
- Update test files to use native symbolic types
- Fix test expectations for native implementation

---

## Files to Modify

| File | Changes Required | Priority |
|------|-----------------|----------|
| `src/symbo_agentic_reasoners/core/native_symbolic.py` | Parser, Eq, Matrix, subs(), has(), expand(), factor(), trig identities | P1 |
| `src/symbo_agentic_reasoners/core/native_calculus.py` | L'Hopital, special limits, -oo constant | P1 |
| `src/symbo_agentic_reasoners/agents/teams/problem_analysis.py` | LaTeX conversion fixes | P1 |
| `src/symbo_agentic_reasoners/discovery/deep_search/prover_engine.py` | transformations attr, health_check | P3 |
| `tests/test_specialists_coverage.py` | Use native Symbol, sin imports | P3 |
| `tests/test_conjecture_modules.py` | Use native types | P3 |
| `tests/test_verification.py` | Define `sp` or use native | P3 |
| `tests/unit/test_curiosity_engine.py` | Use native pi, update assertions | P3 |
| `tests/test_cli_coverage.py` | Update specialist name assertion | P3 |

---

## Estimated Total Effort

- **Critical fixes:** 4-5 days
- **Test updates:** 1-2 days
- **Testing & validation:** 1-2 days
- **Total:** ~7-9 developer days

---

## Appendix: Full Failing Test List

```
1. test_cli_coverage.py::TestMathSolverCLISolve::test_solve_problem_fallback_success
2. test_conjecture_modules.py::TestConjectureFormalizer::test_operator_mappings
3. test_critical_coverage.py::TestE2EBlackbox::test_derivative_blackbox
4. test_critical_coverage.py::TestE2EBlackbox::test_integration_blackbox
5. test_critical_coverage.py::TestNotationTranslatorComprehensive::test_latex_trig_functions
6. test_critical_coverage.py::TestNotationTranslatorComprehensive::test_latex_sqrt
7. test_critical_coverage.py::TestNotationTranslatorComprehensive::test_natural_language_derivative
8. test_critical_coverage.py::TestNotationTranslatorComprehensive::test_natural_language_integral
9. test_critical_coverage.py::TestCuriosityEngineComprehensive::test_interest_scoring_zero
10. test_critical_coverage.py::TestCuriosityEngineComprehensive::test_interest_scoring_pi
11. test_critical_coverage.py::TestFullPipelineIntegration::test_full_calculus_pipeline
12. test_curiosity_engine.py::TestInterestScorer::test_special_value_detection
13. test_deep_search_comprehensive.py::TestSymPyProver::test_initialization
14. test_deep_search_comprehensive.py::TestSymPyProver::test_health_check
15. test_deep_search_comprehensive.py::TestSymPyProverExtended::test_has_transformations
16. test_deep_search_comprehensive.py::TestSymPyProverExtended::test_transformations_is_tuple
17. test_e2e_domain_problems.py::TestAlgebraDomain::test_simplify_rational
18. test_e2e_domain_problems.py::TestAnalysisDomain::test_geometric_series
19. test_e2e_domain_problems.py::TestFullAgentPipeline::test_integration_via_pipeline
20. test_hardcore_integration.py::TestHardEndToEndIntegration::test_full_pipeline_matrix_eigenvalue
21. test_hardcore_integration.py::TestHardEndToEndIntegration::test_full_pipeline_trigonometric_simplification
22. test_hardcore_integration.py::TestMultiTeamHandoff::test_algebra_to_calculus_handoff
23. test_input_validation.py::TestSafeSympify::test_polynomial
24. test_input_validation.py::TestMathematicalConstraint::test_to_sympy_assumption
25. test_input_validation.py::TestParsingPipelineIntegration::test_round_trip_preservation
26. test_nano_tensor.py::TestNanoTensorInit::test_data_initialized_to_zero
27. test_nano_tensor.py::TestNanoTensorSymbolicOps::test_diff
28. test_nano_tensor.py::TestNanoTensorSymbolicOps::test_simplify
29. test_nano_tensor.py::TestNanoTensorPolySolve::test_groebner_solve_system
30. test_nano_tensor.py::TestNanoTensorPolySolve::test_resultant
31. test_nano_tensor.py::TestNanoTensorTaylor::test_generate_taylor_with_value
32. test_nano_tensor.py::TestNanoTensorTaylor::test_compute_steady_state
33. test_nano_tensor.py::TestNanoTensorDerivTree::test_deriv_tree
34. test_parallel_and_formalization_comprehensive.py::TestAutoFormalizationPipelineComplete::test_generate_sympy_implementation
35. test_phase6_discovery.py::TestProverEngine::test_health_check
36. test_pilot_solver.py::TestPilotSolverExecution::test_execute_expand
37. test_pilot_solver.py::TestPilotSolverExecution::test_execute_factor
38. test_pilot_solver.py::TestPilotSolverEdgeCases::test_complex_expression
39. test_specialists.py::TestPolynomialSpecialistOperations::test_process_solve_quadratic
40. test_specialists.py::TestPolynomialSpecialistOperations::test_process_factor
41. test_specialists.py::TestPolynomialSpecialistInternalMethods::test_process_single_polynomial_solve
42. test_specialists.py::TestPolynomialSpecialistInternalMethods::test_process_single_polynomial_factor
43. test_specialists_coverage.py::TestEquationSystemSolver::test_solve_linear_system
44. test_specialists_coverage.py::TestEquationSystemSolver::test_solve_polynomial_system
45. test_specialists_coverage.py::TestEquationSystemSolver::test_classify_system_transcendental
46. test_specialists_coverage.py::TestLimitEvaluator::test_evaluate_indeterminate_form
47. test_specialists_coverage.py::TestLimitEvaluator::test_evaluate_one_sided_limits
48. test_specialists_coverage.py::TestLimitEvaluator::test_detect_indeterminate_form_zero_over_zero
49. test_specialists_coverage.py::TestLimitEvaluator::test_apply_lhopital_tracking
50. test_verification.py::TestSimplifiedVerifierAgent::test_verify_derivative
51. test_verification.py::TestSimplifiedVerifierAgent::test_verify_integral
52. test_verification.py::TestSimplifiedVerifierAgent::test_verify_result_with_operation
53. test_verification.py::TestVerificationIntegration::test_two_stage_verification
54. tests/unit/test_curiosity_engine.py::TestProblemGenerator::test_polynomial_factor_valid
55. tests/unit/test_curiosity_engine.py::TestInterestScorer::test_scorer_initialization
56. tests/unit/test_curiosity_engine.py::TestInterestScorer::test_score_zero_result
57. tests/unit/test_curiosity_engine.py::TestInterestScorer::test_score_unity_result
58. tests/unit/test_curiosity_engine.py::TestInterestScorer::test_score_pi_result
59. tests/unit/test_notation_translator.py::TestNotationTranslatorAgent::test_latex_to_sympy_sqrt
60. tests/unit/test_notation_translator.py::TestNotationTranslatorAgent::test_latex_to_sympy_trig
61. tests/unit/test_notation_translator.py::TestNotationTranslatorAgent::test_natural_to_sympy_derivative
62. tests/unit/test_notation_translator.py::TestNotationTranslatorAgent::test_natural_to_sympy_integral
63. tests/unit/test_notation_translator.py::TestRoundTrip::test_sympy_latex_roundtrip
64. tests/unit/test_notation_translator.py::TestProcessMethod::test_process_auto_detect
```

---

*Generated by System Audit Agent - 2025-12-14*
