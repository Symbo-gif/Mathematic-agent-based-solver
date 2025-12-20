# Benchmark-Driven Improvement Roadmap

**Created**: December 19, 2025
**Based On**: ODE Benchmark (999 problems), GSM8K Sample (5 problems), Infrastructure Validation
**System**: Symbo Agentic Reasoners v1.0 (248 BDI Agents)
**Timeline**: 6 months (Q1-Q2 2026)

---

## Vision

Transform the Symbo Agentic Reasoners system from **architectural excellence** (248 agents, 35 domains) into **computational excellence** (80%+ accuracy across 100,000+ benchmark problems) by implementing core ODE algorithms, enhancing verification capabilities, and expanding problem coverage.

**Target State (6 Months)**:
- 52,000 ODE problems: 80%+ accuracy ✓
- 1,000 University problems: 85%+ accuracy ✓
- Comprehensive documentation ✓
- Competitive with SymPy in symbolic mathematics ✓

---

## Phase 1: Critical Fixes (Weeks 1-6) - ODE Solver Implementation

### Goal: Unlock 52,000-problem ODE benchmark with 75%+ accuracy

---

### Week 1-2: First-Order Linear ODEs

**Objective**: Implement integrating factor method for dy/dx + p(x)y = q(x)

#### Tasks

**Day 1-2: Algorithm Design**
- Research integrating factor method
- Design API for `solve_first_order_linear(equation, initial_condition)`
- Plan integration with native symbolic engine (NO SYMPY)
- Review existing Integration Specialist for reuse

**Day 3-5: Implementation**

**File to Create**: `src/symbo_agentic_reasoners/core/calculus/ode_algorithms.py`

```python
def solve_first_order_linear(p_coefficient, q_function, var='x', ic=None):
    """
    Solve dy/dx + p(x)*y = q(x) using integrating factor method.

    Algorithm:
    1. Compute integrating factor: μ = exp(∫p(x)dx)
    2. Multiply equation by μ
    3. Recognize LHS as d/dx[μ*y]
    4. Integrate RHS: ∫μ*q(x)dx
    5. Solve: y = (1/μ)*(∫μ*q dx + C)
    6. Apply IC if provided to find C

    Args:
        p_coefficient: Coefficient p(x)
        q_function: Right-hand side q(x)
        var: Independent variable
        ic: Initial condition tuple (var_value, y_value)

    Returns:
        Solution expression (general or particular)
    """
    # Implementation here using native symbolic engine
```

**Key Challenges**:
- Integration of p(x) for integrating factor
- Integration of μ*q(x) for particular solution
- Handling non-integrable functions (fallback to numeric)

**Day 6-8: Testing**

**File to Create**: `tests/test_ode_first_order_linear.py`

Test Cases (minimum 20):
- Homogeneous (q=0): dy/dx + y = 0
- Constant coefficients: dy/dx + 3y = 5
- Variable coefficients: dy/dx + (1/x)*y = x
- With exp(x): dy/dx + 2y = exp(x)
- With sin(x): dy/dx + y = sin(x)
- With initial conditions
- Edge cases: p(x) = 0, q(x) = 0

**Day 9-10: Integration & Validation**

**File to Modify**: `src/symbo_agentic_reasoners/agents/specialists/calculus/ode_specialist.py`

Update stub:
```python
# OLD
def solve(self, equation):
    return "ODE solution (Phase 2: Simplified solver)"

# NEW
def solve(self, equation):
    # Parse ODE to extract p(x), q(x)
    p, q, var = self.parse_first_order_linear(equation)

    if p is not None and q is not None:
        # Use algorithm
        from symbo_agentic_reasoners.core.calculus.ode_algorithms import solve_first_order_linear
        solution = solve_first_order_linear(p, q, var, self.get_initial_condition())
        return solution

    # Fallback to other methods...
```

**Success Metrics**:
- ✅ 20+ unit tests passing
- ✅ 70%+ accuracy on first-order linear subset (334/999 problems)
- ✅ Algorithm integrated into ODE specialist
- ✅ Results match SymPy on simple cases

---

### Week 3-4: First-Order Separable ODEs

**Objective**: Implement separation of variables for dy/dx = f(x)*g(y)

#### Tasks

**Day 1-2: Algorithm Design**

**Method**: Separation of Variables
1. Rearrange: dy/g(y) = f(x)*dx
2. Integrate both sides
3. Solve for y (if possible)
4. Apply initial condition

**Day 3-6: Implementation**

**Function to Add**: `solve_first_order_separable(f_x, g_y, var, ic=None)`

**Challenges**:
- Detecting separable form: dy/dx = f(x)*g(y)
- Handling g(y) = 0 (singular solutions)
- Inverting after integration (y as function of x)

**Day 7-8: Testing**

Test Cases (20+):
- Simple: dy/dx = x*y
- Polynomial: dy/dx = x*y²
- Trigonometric: dy/dx = sin(x)*cos(y)
- Exponential: dy/dx = exp(x)*y
- Edge cases: Non-separable ODEs (should detect and reject)

**Day 9-10: Integration**

Modify ODE specialist to detect separable form and apply method.

**Success Metrics**:
- ✅ 20+ unit tests passing
- ✅ 70%+ on separable subset (333/999)
- ✅ Combined: 60%+ accuracy on 667 first-order problems

---

### Week 5-6: Second-Order Constant Coefficients

**Objective**: Implement characteristic equation method for ay'' + by' + cy = f(x)

#### Tasks

**Day 1-3: Homogeneous Solutions**

**Algorithm**: Characteristic Equation
1. Substitute y = exp(rx)
2. Characteristic equation: ar² + br + c = 0
3. Solve quadratic for roots r1, r2
4. General solution based on root type:
   - **Real distinct**: y = C1*exp(r1*x) + C2*exp(r2*x)
   - **Real repeated**: y = (C1 + C2*x)*exp(r*x)
   - **Complex conjugate**: y = exp(αx)*(C1*cos(βx) + C2*sin(βx))

**Implementation**: `solve_second_order_constant_homogeneous(a, b, c, var)`

**Day 4-6: Non-Homogeneous Solutions**

**Methods**:
1. **Undetermined Coefficients** (for polynomial, exp, sin, cos RHS)
2. **Variation of Parameters** (general method)

**Implementation**:
- `solve_second_order_constant_nonhomogeneous(a, b, c, f_x, var)`
- Helper: `get_particular_solution(characteristic_roots, f_x)`

**Day 7-9: Testing**

Test Cases (25+):
- Real roots: y'' - 5y' + 6y = 0
- Repeated roots: y'' - 2y' + y = 0
- Complex roots: y'' + 4y = 0
- Non-homogeneous (poly): y'' + y = x²
- Non-homogeneous (exp): y'' + y = exp(x)
- Non-homogeneous (trig): y'' + 4y = sin(2x)
- With initial conditions

**Day 10: Integration & Validation**

Update ODE specialist with second-order solver.

**Success Metrics**:
- ✅ 25+ unit tests passing
- ✅ 75%+ on second-order subset (332/999)
- ✅ **Overall: 75%+ on full 999-problem suite**

---

### Week 6: Integration, Optimization, Validation

**Day 1-2: Method Selection Heuristics**

Implement intelligent ODE type detection:
```python
def classify_ode(equation):
    """
    Classify ODE type and select appropriate method.

    Returns:
        (ode_type, method, confidence)
    """
    if is_first_order_linear(equation):
        return "first_order_linear", "integrating_factor", 0.95

    if is_separable(equation):
        return "first_order_separable", "separation", 0.90

    if is_second_order_constant(equation):
        return "second_order_constant", "characteristic", 0.95

    return "unknown", None, 0.0
```

**Day 3-4: Performance Optimization**

Profile and optimize:
- Integration speed (used heavily in ODE solving)
- Symbolic simplification
- Pattern matching efficiency
- Target: <5s per ODE on average

**Day 5: Full Re-Test**

Run complete 999-problem suite:
- Measure accuracy improvement
- Analyze remaining failures
- Identify additional algorithm needs

**Day 6-7: Documentation**

- Update ODE solver documentation
- Create algorithm reference guide
- Document test results and improvements

**Milestone**: 75%+ accuracy on 999 problems, ready for full 52k suite

---

## Phase 2: Expansion & Refinement (Weeks 7-12)

### Week 7-8: Advanced ODE Methods

**Objective**: Handle remaining 10-20% of ODEs

#### Tasks

**Systems of ODEs**:
```python
def solve_ode_system(equations, variables):
    """
    Solve system of first-order ODEs.

    Method: Matrix exponential or eigenvalue method
    """
```

**Higher-Order ODEs**:
```python
def solve_higher_order(equation, order):
    """
    Solve nth-order ODE.

    Method: Order reduction or characteristic equation extension
    """
```

**Boundary Value Problems**:
```python
def solve_bvp(equation, boundary_conditions):
    """
    Solve ODE with boundary conditions.

    Method: Shooting method or finite differences
    """
```

**Success Metrics**:
- 85%+ accuracy on 999-problem suite
- Support for 90% of ODE types in full 52k suite

---

### Week 9-10: Answer Verification Enhancement

**Objective**: Implement ODE solution verification

#### Tasks

**File**: `src/symbo_agentic_reasoners/benchmarks/answer_comparators.py`

**New Function**:
```python
def verify_ode_solution(solution, ode_equation, initial_conditions=None):
    """
    Verify ODE solution by substitution.

    Steps:
    1. Differentiate solution to get dy/dx, d2y/dx2, etc.
    2. Substitute into original ODE
    3. Simplify and check if equals RHS
    4. If IC provided, check y(x0) = y0

    Returns:
        (is_valid, error) tuple
    """
    # Differentiate solution
    dy_dx = differentiate(solution, var)

    # Substitute into LHS of ODE
    lhs_substituted = substitute_into_ode(ode_equation, solution, dy_dx)

    # Simplify
    lhs_simplified = simplify(lhs_substituted)

    # Check if equals RHS
    rhs = extract_rhs(ode_equation)

    if symbolically_equivalent(lhs_simplified, rhs):
        return True, "Solution verified by substitution"

    return False, f"Substitution failed: {lhs_simplified} ≠ {rhs}"
```

**Testing**:
- 30 test cases with known ODE solutions
- Verify correct solutions pass
- Verify incorrect solutions fail

**Success Metrics**:
- ✅ Can verify 95%+ of ODE solutions by substitution
- ✅ Zero false positives (incorrect solutions marked correct)
- ✅ <5% false negatives (correct solutions marked incorrect)

---

### Week 11-12: Full 52k ODE Suite Execution

**Objective**: Run complete 52,000-problem ODE benchmark

#### Tasks

**Day 1: Generate Full Suite**
```bash
python scripts/generate_ode_test_suite.py --total 51500
```
- Creates 51,500 synthetic ODEs
- Adds to existing 999 (subtotal 52,499)
- Total with 500 existing: ~52,000 problems

**Day 2-7: Execution** (Continuous run)

Estimated time:
- 52,000 problems × 3s/problem = 43 hours continuous
- With 4 parallel workers: ~11 hours wall-clock time

Monitor:
- Progress every 1,000 problems
- Checkpoint every 100 problems
- Resource usage (memory, CPU)

**Day 8-10: Analysis**

Run `scripts/analyze_benchmark_results.py`:
- Overall accuracy
- Accuracy by ODE type
- Time distribution
- Failure analysis
- Specialist performance

**Day 11-12: Documentation**

Create:
- `docs/benchmarks/ODE_FULL_BENCHMARK_RESULTS.md`
- Comparison vs SymPy/Mathematica
- Competitive positioning
- Remaining gaps and recommendations

**Milestone**: 80%+ accuracy on 52,000 ODE problems

---

## Phase 3: University Benchmark Development (Weeks 13-20)

### Week 13-16: Problem Curation

**Objective**: Curate 1,000 university-level problems

#### Source Distribution

**Textbooks (400 problems)**:
- Abstract Algebra: Dummit & Foote (80 problems)
- Analysis: Rudin, Folland (80 problems)
- Topology: Munkres, Hatcher (80 problems)
- Number Theory: Ireland & Rosen (40 problems)
- Geometry: Do Carmo, Lee (40 problems)
- Others: Category theory, logic, etc. (80 problems)

**Qualifying Exams (400 problems)**:
- MIT Pure Math Quals (2015-2024): 100 problems
- Princeton General Exams: 100 problems
- Berkeley Preliminaries: 100 problems
- Stanford Quals: 100 problems

**Competition Problems (200 problems)**:
- Putnam (2015-2024 hardest): 100 problems
- IMO Shortlist (algebra, number theory): 100 problems

#### Curation Process

**Week 13**:
- Collect problems from digital sources
- Create standardized JSON format
- 250 problems collected

**Week 14**:
- Continue collection and formatting
- 500 problems collected (cumulative)

**Week 15**:
- Continue collection and formatting
- 750 problems collected (cumulative)

**Week 16**:
- Final collection push
- Quality review
- 1,000 problems collected ✓

**File Created**: `data/benchmarks/university/university_problems_v1.json`

---

### Week 17-18: University Benchmark Execution

**Objective**: Execute 1,000 university problems and analyze results

#### Execution

**Day 1-2: Run Benchmark**
```bash
python scripts/run_university_benchmark.py
```

Estimated time: 1,000 problems × 30s/problem = 8.3 hours

**Day 3-5: Analysis**

By Tier:
- Undergraduate (300-400 level): Expected 90%+ accuracy
- Graduate (500-600 level): Expected 85%+ accuracy
- Advanced (700+ level): Expected 75%+ accuracy

By Domain (35 domains):
- Topology: Expected 90%+ (system strength)
- Abstract Algebra: Expected 88%+
- Analysis: Expected 85%+
- Number Theory: Expected 85%+
- Others: 75-90%

**Day 6-7: Specialist Performance Analysis**

Identify:
- Top-performing specialists
- Under-performing specialists
- Gaps in coverage

---

### Week 19-20: University Benchmark Documentation

**Objective**: Create comprehensive analysis

#### Documents to Create

1. **`UNIVERSITY_BENCHMARK_RESULTS.md`**
   - Overall accuracy: Expected 85%+
   - By domain breakdown
   - By tier analysis
   - Specialist utilization
   - Competitive comparison

2. **`UNIVERSITY_BENCHMARK_SHORTCOMINGS.md`**
   - Domains below 80% accuracy
   - Missing capabilities
   - Proof verification gaps

3. **`UNIVERSITY_IMPROVEMENT_PLAN.md`**
   - Specialist enhancements needed
   - Algorithm additions
   - 6-month roadmap to 90%+

**Milestone**: 85%+ accuracy on 1,000 university problems

---

## Phase 4: Optimization & Scale (Weeks 21-24)

### Week 21-22: Performance Optimization

**Objective**: Reduce average solve time by 30%

#### Hot Path Profiling

Run profiler on 1,000 diverse problems:
```bash
python -m cProfile -o profile.stats scripts/run_all_benchmarks.py --limit-ode 100 --limit-university 100
```

Identify bottlenecks:
- Integration algorithms
- Polynomial factorization
- Matrix operations
- Symbolic simplification

#### Optimization Targets

**Target 1: Integration Speed** (2x faster)
- Current: 100ms per indefinite integral
- Target: 50ms
- Method: Cache common integrals, optimize pattern matching

**Target 2: ODE Solving** (30% faster)
- Current (projected): 3s per ODE
- Target: 2s per ODE
- Method: Optimized integrating factor, pre-computed forms

**Target 3: Symbolic Simplification** (50% faster)
- Method: Add algebraic rule caching, optimize expression tree traversal

**Success Metrics**:
- Mean time reduced by 30%
- P95 time reduced by 25%
- No accuracy degradation

---

### Week 23-24: Full Benchmark Execution & Reporting

**Objective**: Run all available benchmarks and create master report

#### Execution Plan

**Day 1**: Setup
- Verify all datasets ready
- Configure parallel execution
- Set up monitoring

**Day 2-7**: Execute Benchmarks (Parallel where possible)

| Benchmark | Problems | Estimated Time | Priority |
|-----------|----------|----------------|----------|
| ODE Suite | 52,000 | 11 hours (4 workers) | ✓ Run |
| GSM8K | 8,792 | 1.5 hours | ✓ Run (limited value) |
| University | 1,000 | 8 hours | ✓ Run |
| **Total** | **61,792** | **~21 hours** | - |

**MATH**: Skip (dataset unavailable)
**AIME**: Skip (manual curation not worth effort for 60 problems)

**Day 8-10**: Analysis

Run comprehensive analysis:
- Aggregate statistics across all benchmarks
- Domain-wise performance
- Specialist utilization across 61k problems
- Competitive comparisons
- Strategic insights

**Day 11-14**: Master Documentation

Create final documents:
1. `FULL_BENCHMARK_RESULTS.md` - Complete results
2. `COMPETITIVE_COMPARISON.md` - vs SymPy, Mathematica, o3
3. `MASTER_BENCHMARK_REPORT.md` - Executive summary
4. `QUICK_REFERENCE.md` - One-page summary

**Milestone**: Complete benchmark documentation suite

---

## Resource Requirements

### Personnel

| Role | FTE | Duration | Tasks |
|------|-----|----------|-------|
| **Senior Developer** | 1.0 | Weeks 1-6 | ODE algorithm implementation |
| **Developer** | 0.5 | Weeks 7-12 | Advanced ODE methods, verification |
| **Curator** | 1.0 | Weeks 13-16 | University problem collection |
| **Analyst** | 0.5 | Weeks 17-24 | Analysis, documentation |

**Total**: ~2.5 FTE over 24 weeks

### Infrastructure

- **Compute**: Standard workstation (4-8 cores sufficient)
- **Storage**: ~5 GB for datasets and results
- **Network**: For HuggingFace dataset downloads
- **Time**: ~40 hours total execution time across 24 weeks

### Budget

| Item | Cost | Notes |
|------|------|-------|
| Personnel (2.5 FTE × 6 months) | $0 | Internal team |
| Compute | $0 | Local execution |
| Datasets | $0 | All free/open-source |
| **Total** | **$0** | Zero incremental cost |

**ROI**: Infinite (zero cost, high value)

---

## Risk Management

### Risk 1: ODE Implementation Complexity

**Risk**: Algorithms harder to implement than estimated
**Probability**: Medium (30%)
**Impact**: High (delays Phase 2-4)

**Mitigation**:
- Start with simplest algorithms (integrating factor)
- Validate each algorithm before moving to next
- Keep SymPy fallback as backup

**Contingency**:
- Extend Week 1-6 to 8 weeks if needed
- Reduce scope: Skip advanced methods, focus on core 3

---

### Risk 2: University Problem Curation Takes Too Long

**Risk**: 1,000 problem curation exceeds 4 weeks
**Probability**: High (60%)
**Impact**: Medium (delays documentation)

**Mitigation**:
- Start curation in parallel with ODE implementation (Week 2)
- Focus on quality over quantity (600 problems acceptable)
- Use existing problem databases (less manual typing)

**Contingency**:
- Reduce scope to 600 problems (still comprehensive)
- Focus on system-strength domains (topology, algebra, analysis)

---

### Risk 3: Performance Optimization Insufficient

**Risk**: Can't achieve 30% speedup target
**Probability**: Low (20%)
**Impact**: Low (slower execution acceptable)

**Mitigation**:
- Profile early and often
- Focus on top 3 bottlenecks only
- Acceptable result: 15-20% speedup

**Contingency**:
- Accept longer execution times
- Use overnight runs for large benchmarks

---

### Risk 4: Accuracy Below Targets

**Risk**: ODE solver achieves only 60% vs 75% target
**Probability**: Medium (40%)
**Impact**: Medium (lower competitive positioning)

**Mitigation**:
- Extensive testing during implementation
- Add algorithm fallbacks (multiple methods per ODE type)
- Iterate on failure cases

**Contingency**:
- 60% is still viable (shows capability)
- Document remaining gaps
- Plan Phase 5 for gap closure

---

## Success Criteria

### 3-Month Checkpoint (End of Week 12)

- [ ] ODE solver implemented (integrating factor, separation, characteristic)
- [ ] 75%+ accuracy on 999-problem ODE test
- [ ] 85%+ accuracy on first-order linear ODEs
- [ ] 80%+ accuracy on second-order constant ODEs
- [ ] 50+ unit tests passing
- [ ] Documentation: ODE algorithm guide complete

**Pass/Fail**: Must achieve 70%+ on 999 problems to proceed to Phase 3

---

### 6-Month Completion (End of Week 24)

- [ ] Full 52,000 ODE suite executed
- [ ] 80%+ accuracy on ODE benchmark
- [ ] 1,000 university problems curated
- [ ] 85%+ accuracy on university benchmark
- [ ] Comprehensive documentation (6 documents)
- [ ] Competitive analysis vs SymPy, Mathematica, o3
- [ ] Improvement roadmap for next 6 months
- [ ] Zero-crash execution on 60,000+ problems

**Pass/Fail**: Must achieve 75%+ on ODE AND 80%+ on University

---

## Measurement & Tracking

### Weekly Metrics

**Code Metrics**:
- LOC added/modified
- Unit tests added
- Test coverage percentage

**Performance Metrics**:
- Problems tested (cumulative)
- Accuracy rate (overall and by domain)
- Average solve time
- Timeout rate

**Progress Tracking**:
- Milestones hit vs planned
- Blockers identified and resolved
- Risk actualization

### Reporting Cadence

- **Daily**: Progress logs during benchmark execution
- **Weekly**: Status report (metrics + risks)
- **Monthly**: Executive summary (3 months, 6 months)

---

## Alternative Scenarios

### Scenario A: Fast-Track ODE Only (4 weeks)

If resource-constrained, focus exclusively on ODE:

- Week 1-2: First-order methods
- Week 3-4: Second-order methods
- Skip: University benchmark, advanced methods
- Result: 70%+ on 52k ODEs in 1 month

**Trade-off**: Narrow scope but faster delivery

---

### Scenario B: University-First (Skip ODE)

If strategic pivot to pure mathematics:

- Weeks 1-4: University problem curation
- Weeks 5-6: Execution and analysis
- Skip: ODE implementation
- Result: 85%+ on 1,000 pure math problems

**Trade-off**: Plays to strengths but smaller dataset

---

### Scenario C: Hybrid Approach (Recommended)

Balanced approach as outlined in main roadmap:

- Phase 1 (6 weeks): ODE solver
- Phase 2 (6 weeks): Advanced ODE + Verification
- Phase 3 (8 weeks): University benchmark
- Phase 4 (4 weeks): Optimization + Full execution

**Trade-off**: Longer timeline but comprehensive coverage

---

## Lessons Learned from Testing

### What Worked

1. **Incremental Testing**: Testing 10 → 999 problems caught issues early
2. **Routing Fix**: Systematic pattern matching solved classification
3. **Infrastructure-First**: Solid foundation enables rapid iteration
4. **Comprehensive Logging**: Made debugging trivial

### What Didn't Work

1. **Assuming Algorithm Implementation**: Many "specialists" are stubs
2. **Dataset Availability**: External dependencies can fail (MATH dataset)
3. **One-Size-Fits-All Comparison**: Need domain-specific answer validation

### Best Practices Going Forward

1. **Validate Existence Before Planning**: Check algorithm implementation before benchmarking
2. **Start Small**: 10-problem tests before 1000-problem tests
3. **Document Limitations**: Stub implementations should be clearly marked
4. **Flexible Scoping**: Be ready to pivot based on findings

---

## Priority Matrix

| Task | Impact | Effort | ROI | Priority | Weeks |
|------|--------|--------|-----|----------|-------|
| **ODE Solver (1st order)** | Very High | Medium | ★★★★★ | P0 | 1-2 |
| **ODE Solver (2nd order)** | Very High | Medium | ★★★★★ | P0 | 3-4 |
| **ODE Solver (advanced)** | High | High | ★★★★☆ | P1 | 5-6 |
| **Answer Verification** | High | Low | ★★★★★ | P1 | 9-10 |
| **University Curation** | High | Very High | ★★★☆☆ | P2 | 13-16 |
| **Performance Optimization** | Medium | Medium | ★★★☆☆ | P2 | 21-22 |
| **NL Translator** | Low | Very High | ★☆☆☆☆ | P3 | Not planned |

---

## Conclusion

The benchmark testing revealed a **structurally sound system with implementation gaps**. The 0% ODE accuracy is **entirely due to placeholder code**, not architectural flaws. With focused 6-week effort, the system can achieve 75-90% accuracy on 52,000 ODE problems, establishing it as a competitive symbolic mathematics engine.

**Key Recommendations**:

1. **Invest in ODE solver** (P0, 6 weeks) - Highest ROI
2. **Build university benchmark** (P2, 4 weeks) - Showcases strengths
3. **Skip GSM8K/NL parsing** (P3) - Not core competency
4. **Document limitations transparently** - Set correct expectations

**Expected Outcome**: By end of Q2 2026, achieve 80%+ accuracy on 53,000+ problems (52k ODE + 1k University), positioning system as **leading open-source symbolic mathematics engine with formal verification**.

---

**End of Improvement Roadmap**
