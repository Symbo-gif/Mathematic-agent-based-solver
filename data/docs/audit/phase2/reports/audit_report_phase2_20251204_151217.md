# Phase 2 Audit Report: Vertical Domain Expansion

**Run ID**: `20251204_151217`
**Date**: 2025-12-04T15:12:33.152815

## Executive Summary

| Metric | Value |
|---|---|
| Total Tests | 7 |
| Passed | 4 |
| Failed | 0 |
| Errors | 3 |
| Success Rate | 57.1% |

**Overall Status**: ❌ FAILED

## Detailed Test Results

| Test Name | Status | Duration (s) | Message |
|---|---|---|---|
| test_end_to_end_solve (edge_tests.Phase2EdgeTest.test_end_to_end_solve) | ✅ PASS | 0.000 |  |
| test_integration_numerical (edge_tests.Phase2EdgeTest.test_integration_numerical) | ⚠️ ERROR | 0.000 | create_entry() got an unexpected keyword argument 'status' |
| test_integration_symbolic (edge_tests.Phase2EdgeTest.test_integration_symbolic) | ⚠️ ERROR | 0.000 | create_entry() got an unexpected keyword argument 'status' |
| test_polynomial_groebner (edge_tests.Phase2EdgeTest.test_polynomial_groebner) | ⚠️ ERROR | 0.000 | create_entry() got an unexpected keyword argument 'status' |
| test_component_initialization (smoke_tests.Phase2SmokeTest.test_component_initialization) | ✅ PASS | 0.000 |  |
| test_statistics_availability (smoke_tests.Phase2SmokeTest.test_statistics_availability) | ✅ PASS | 0.000 |  |
| test_system_health (smoke_tests.Phase2SmokeTest.test_system_health) | ✅ PASS | 0.000 |  |

## System Configuration

- **Phase**: 2 (Vertical Domain Expansion)
- **Status**: Fragile Genius
- **Components Tested**:
  - **Tier 2 Supervisors**: Algebra, Calculus, Linear Algebra, Statistics
  - **Tier 3 Specialists**:
    - Algebra: Arithmetic, Polynomial (Gröbner), Number Theory
    - Calculus: Differentiation, Integration (Dual-Engine), ODE, Series
    - Linear Algebra: Matrix Ops, Decomposition, Vector Space
    - Statistics: Distribution, Bayesian, Frequentist
    - Discrete: Combinatorics, Graph Theory
    - Numerical Fallback
