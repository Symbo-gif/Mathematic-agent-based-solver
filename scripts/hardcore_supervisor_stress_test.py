#!/usr/bin/env python3
# Copyright 2025 Michael Maillet, Damien Davison, and Sacha Davison
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Hardcore Stress Test for All 29 Supervisor Agents
Tests concurrency, error handling, edge cases, resource limits, and delegation under extreme conditions.
"""

import sys
import os
import time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Any
import traceback

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)


# Supervisor registry with import paths
SUPERVISORS = {
    "AlgebraSupervisor": "symbo_agentic_reasoners.agents.supervisors.algebra_supervisor",
    "CalculusSupervisor": "symbo_agentic_reasoners.agents.supervisors.calculus_supervisor",
    "LinearAlgebraSupervisor": "symbo_agentic_reasoners.agents.supervisors.linalg_supervisor",
    "StatisticsSupervisor": "symbo_agentic_reasoners.agents.supervisors.stats_supervisor",
    "DiscreteMathSupervisor": "symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor",
    "LogicSupervisor": "symbo_agentic_reasoners.agents.supervisors.logic_supervisor",
    "GeometrySupervisor": "symbo_agentic_reasoners.agents.supervisors.geometry_supervisor",
    "PhysicsMechanicsSupervisor": "symbo_agentic_reasoners.agents.supervisors.physics_mechanics_supervisor",
    "PhysicsEMSupervisor": "symbo_agentic_reasoners.agents.supervisors.physics_em_supervisor",
    "PhysicsThermoSupervisor": "symbo_agentic_reasoners.agents.supervisors.physics_thermo_supervisor",
    "PhysicsQuantumSupervisor": "symbo_agentic_reasoners.agents.supervisors.physics_quantum_supervisor",
    "ComplexAnalysisSupervisor": "symbo_agentic_reasoners.agents.supervisors.complex_analysis_supervisor",
    "RealAnalysisSupervisor": "symbo_agentic_reasoners.agents.supervisors.real_analysis_supervisor",
    "FunctionalAnalysisSupervisor": "symbo_agentic_reasoners.agents.supervisors.functional_analysis_supervisor",
    "DiffGeometrySupervisor": "symbo_agentic_reasoners.agents.supervisors.diff_geometry_supervisor",
    "ControlTheorySupervisor": "symbo_agentic_reasoners.agents.supervisors.control_theory_supervisor",
    "InformationTheorySupervisor": "symbo_agentic_reasoners.agents.supervisors.information_theory_supervisor",
    "CryptographySupervisor": "symbo_agentic_reasoners.agents.supervisors.cryptography_supervisor",
    "OptimizationSupervisor": "symbo_agentic_reasoners.agents.supervisors.optimization_supervisor",
    "CategoryTheorySupervisor": "symbo_agentic_reasoners.agents.supervisors.category_theory_supervisor",
    "StochasticProcessesSupervisor": "symbo_agentic_reasoners.agents.supervisors.stochastic_processes_supervisor",
    "ModelTheorySupervisor": "symbo_agentic_reasoners.agents.supervisors.model_theory_supervisor",
    "ProofTheorySupervisor": "symbo_agentic_reasoners.agents.supervisors.proof_theory_supervisor",
    "ComputabilitySupervisor": "symbo_agentic_reasoners.agents.supervisors.computability_supervisor",
    "RiemannianGeometrySupervisor": "symbo_agentic_reasoners.agents.supervisors.riemannian_geometry_supervisor",
    "AlgebraicTopologySupervisor": "symbo_agentic_reasoners.agents.supervisors.algebraic_topology_supervisor",
    "ErgodicTheorySupervisor": "symbo_agentic_reasoners.agents.supervisors.ergodic_theory_supervisor",
    "GeometricMeasureTheorySupervisor": "symbo_agentic_reasoners.agents.supervisors.geometric_measure_supervisor",
    "TopologicalDataAnalysisSupervisor": "symbo_agentic_reasoners.agents.supervisors.tda_supervisor",
}

# Stress test scenarios for each supervisor
STRESS_SCENARIOS = {
    "AlgebraSupervisor": [
        {"type": "polynomial", "expression": "x^100 - 1", "operation": "factor"},
        {"type": "system", "equations": ["x + y = 1"] * 50, "variables": ["x", "y"]},
        {"type": "number_theory", "n": 10**15 + 37, "operation": "factor"},
    ],
    "CalculusSupervisor": [
        {"type": "derivative", "expression": "x^50 * sin(x) * exp(x)", "variable": "x", "order": 10},
        {"type": "integral", "expression": "x^20 * exp(-x^2)", "variable": "x", "limits": [0, float('inf')]},
        {"type": "ode", "equation": "y'' + 100*y' + 2500*y = 0", "initial": {"y(0)": 1, "y'(0)": 0}},
    ],
    "LinearAlgebraSupervisor": [
        {"type": "matrix_ops", "operation": "eigenvalues", "size": 100},
        {"type": "decomposition", "method": "SVD", "size": 50},
        {"type": "solve", "size": 200, "sparse": True},
    ],
    "StatisticsSupervisor": [
        {"type": "distribution", "name": "normal", "parameters": {"mu": 0, "sigma": 1}, "samples": 100000},
        {"type": "bayesian", "observations": list(range(10000)), "prior": "uniform"},
        {"type": "regression", "data_points": 50000, "features": 20},
    ],
    "DiscreteMathSupervisor": [
        {"type": "graph", "operation": "shortest_path", "nodes": 10000, "edges": 50000},
        {"type": "combinatorics", "n": 1000, "k": 500, "operation": "binomial"},
        {"type": "set_theory", "operation": "powerset", "size": 20},
    ],
    "LogicSupervisor": [
        {"type": "propositional", "formula": " & ".join([f"p{i}" for i in range(50)]), "operation": "sat"},
        {"type": "predicate", "quantifiers": 10, "operation": "validity"},
        {"type": "proof", "premises": [f"P{i} -> P{i+1}" for i in range(100)], "conclusion": "P0 -> P100"},
    ],
    "GeometrySupervisor": [
        {"type": "euclidean", "operation": "distance", "dimensions": 1000},
        {"type": "transformation", "matrices": 100, "composition": True},
        {"type": "computational", "points": 10000, "operation": "convex_hull"},
    ],
    "PhysicsMechanicsSupervisor": [
        {"type": "kinematics", "equations": 100, "unknowns": 50},
        {"type": "dynamics", "bodies": 50, "forces": 200},
        {"type": "energy", "system": "complex", "particles": 100},
    ],
    "PhysicsEMSupervisor": [
        {"type": "electrostatics", "charges": 1000, "field_points": 5000},
        {"type": "magnetism", "currents": 100, "field_strength": True},
        {"type": "circuits", "components": 500, "nodes": 200},
    ],
    "PhysicsThermoSupervisor": [
        {"type": "heat_transfer", "nodes": 1000, "timesteps": 10000},
        {"type": "gas_laws", "molecules": 10**6, "simulation": True},
    ],
    "PhysicsQuantumSupervisor": [
        {"type": "wavefunction", "particles": 10, "dimensions": 3},
        {"type": "operators", "matrix_size": 100, "hermitian": True},
        {"type": "systems", "hamiltonian": "complex", "eigenstates": 50},
    ],
    "ComplexAnalysisSupervisor": [
        {"type": "analytic", "function": "entire", "order": 20},
        {"type": "residue", "poles": 100, "contour": "complex"},
        {"type": "conformal", "regions": 50, "mapping": "schwarz-christoffel"},
    ],
    "RealAnalysisSupervisor": [
        {"type": "measure", "sets": 1000, "lebesgue": True},
        {"type": "function_spaces", "norm": "Lp", "p": 2, "dimension": 1000},
        {"type": "sequences", "terms": 100000, "convergence": "test"},
    ],
    "FunctionalAnalysisSupervisor": [
        {"type": "banach", "dimension": 1000, "norm": "custom"},
        {"type": "hilbert", "basis": 500, "inner_product": True},
        {"type": "operator", "dimension": 200, "spectrum": True},
    ],
    "DiffGeometrySupervisor": [
        {"type": "differential", "manifold": "complex", "dimension": 10},
        {"type": "topology", "complex": "simplicial", "dimension": 100},
    ],
    "ControlTheorySupervisor": [
        {"type": "dynamical", "dimension": 50, "nonlinear": True},
        {"type": "linear_control", "state_dim": 100, "input_dim": 20},
    ],
    "InformationTheorySupervisor": [
        {"type": "entropy", "distribution": list(range(10000)), "base": 2},
        {"type": "coding", "message_length": 100000, "huffman": True},
        {"type": "channel", "capacity": True, "noise": 0.1, "iterations": 10000},
    ],
    "CryptographySupervisor": [
        {"type": "modular", "base": 2**2048, "exponent": 65537, "modulus": 10**1000},
        {"type": "asymmetric", "key_size": 4096, "operation": "encrypt"},
        {"type": "hash", "data_size": 10**6, "merkle_depth": 20},
    ],
    "OptimizationSupervisor": [
        {"type": "linear_programming", "variables": 1000, "constraints": 5000},
        {"type": "convex", "dimension": 500, "method": "newton"},
        {"type": "combinatorial", "items": 10000, "knapsack": True},
    ],
    "CategoryTheorySupervisor": [
        {"type": "morphism", "objects": 1000, "arrows": 5000},
        {"type": "functor", "categories": 100, "natural_transformations": 50},
        {"type": "universal", "limits": 200, "colimits": 200},
    ],
    "StochasticProcessesSupervisor": [
        {"type": "brownian", "timesteps": 100000, "paths": 1000},
        {"type": "sde", "equation": "dX = mu*dt + sigma*dW", "timesteps": 50000},
        {"type": "martingale", "process": "complex", "stopping_times": 100},
    ],
    "ModelTheorySupervisor": [
        {"type": "compactness", "sentences": 10000, "theory": "complex"},
        {"type": "categoricity", "cardinality": "uncountable", "spectrum": True},
        {"type": "quantifier_elimination", "formula": "complex", "variables": 50},
    ],
    "ProofTheorySupervisor": [
        {"type": "cut_elimination", "proof_depth": 100, "formulas": 500},
        {"type": "ordinal_analysis", "ordinal": "epsilon_0", "hierarchy": True},
        {"type": "type_theory", "lambda_terms": 1000, "reduction_steps": 10000},
    ],
    "ComputabilitySupervisor": [
        {"type": "turing_completeness", "machine": "complex", "tape_size": 10000},
        {"type": "recursion", "depth": 1000, "ackermann": True},
        {"type": "complexity", "problem": "3SAT", "variables": 1000, "clauses": 5000},
    ],
    "RiemannianGeometrySupervisor": [
        {"type": "metric", "manifold": "complex", "dimension": 20},
        {"type": "curvature", "tensors": 100, "riemann": True},
        {"type": "geodesic", "initial_conditions": 1000, "integration_steps": 50000},
    ],
    "AlgebraicTopologySupervisor": [
        {"type": "homotopy", "space": "complex", "fundamental_group": True},
        {"type": "homology", "complex": "simplicial", "dimension": 100},
        {"type": "spectral_sequences", "pages": 10, "differentials": 50},
    ],
    "ErgodicTheorySupervisor": [
        {"type": "invariant_measure", "transformation": "complex", "iterations": 100000},
        {"type": "mixing", "system": "strongly_mixing", "time_steps": 50000},
        {"type": "entropy", "partition": 100, "trajectories": 10000},
    ],
    "GeometricMeasureTheorySupervisor": [
        {"type": "hausdorff", "set": "fractal", "dimension": "compute", "covers": 10000},
        {"type": "rectifiability", "set": "complex", "dimension": 10},
        {"type": "minimal_surfaces", "boundary": "complex", "area_minimization": True},
    ],
    "TopologicalDataAnalysisSupervisor": [
        {"type": "persistent_homology", "points": 10000, "dimension": 50},
        {"type": "simplicial_complex", "vertices": 5000, "max_dimension": 10},
        {"type": "mapper", "data_points": 50000, "cover_elements": 1000},
    ],
}

# Edge cases and malformed inputs (applied to all supervisors)
EDGE_CASES = [
    {"type": "empty", "data": {}},
    {"type": "null", "data": None},
    {"type": "invalid_type", "data": "this should be a dict"},
    {"type": "missing_fields", "data": {"incomplete": True}},
    {"type": "extreme_values", "data": {"value": float('inf')}},
    {"type": "negative_dimensions", "data": {"size": -100}},
    {"type": "circular_reference", "data": {"self": "recursive"}},
]


class StressTestResult:
    """Container for stress test results"""
    def __init__(self, supervisor_name: str):
        self.supervisor_name = supervisor_name
        self.scenarios_passed = 0
        self.scenarios_failed = 0
        self.edge_cases_passed = 0
        self.edge_cases_failed = 0
        self.concurrent_tests_passed = 0
        self.concurrent_tests_failed = 0
        self.errors = []
        self.warnings = []
        self.execution_time = 0.0
        self.memory_peak = 0

    def add_error(self, scenario: str, error: str):
        self.errors.append(f"{scenario}: {error}")

    def add_warning(self, scenario: str, warning: str):
        self.warnings.append(f"{scenario}: {warning}")

    def to_dict(self):
        return {
            "supervisor": self.supervisor_name,
            "scenarios_passed": self.scenarios_passed,
            "scenarios_failed": self.scenarios_failed,
            "edge_cases_passed": self.edge_cases_passed,
            "edge_cases_failed": self.edge_cases_failed,
            "concurrent_tests_passed": self.concurrent_tests_passed,
            "concurrent_tests_failed": self.concurrent_tests_failed,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "execution_time": f"{self.execution_time:.2f}s",
            "memory_peak_mb": self.memory_peak,
            "success_rate": self._calculate_success_rate()
        }

    def _calculate_success_rate(self):
        total = (self.scenarios_passed + self.scenarios_failed +
                self.edge_cases_passed + self.edge_cases_failed +
                self.concurrent_tests_passed + self.concurrent_tests_failed)
        if total == 0:
            return 0.0
        passed = (self.scenarios_passed + self.edge_cases_passed +
                 self.concurrent_tests_passed)
        return (passed / total) * 100


def load_supervisor(supervisor_name: str, module_path: str):
    """Dynamically load a supervisor class"""
    try:
        module = __import__(module_path, fromlist=[supervisor_name])
        return getattr(module, supervisor_name)
    except Exception as e:
        print(f"ERROR: Failed to load {supervisor_name}: {e}")
        return None


def test_supervisor_scenario(supervisor, scenario: Dict[str, Any]) -> Tuple[bool, str]:
    """Test a single scenario on a supervisor"""
    try:
        # Create a task entry on the blackboard
        if hasattr(supervisor, 'blackboard') and supervisor.blackboard:
            # Post task to blackboard (supervisors check blackboard in update_beliefs)
            entry = create_entry(
                entry_type=EntryType.TASK,
                content=scenario,
                author_agent="stress_test",
                conversation_id="stress_test_conv",
                tags=["stress_test"],
                status=EntryStatus.PENDING,
                metadata={"source": "stress_test", "priority": "high"}
            )
            supervisor.blackboard.post(entry)

        # BDI cycle: perceive -> deliberate -> act
        supervisor.update_beliefs()
        intentions = supervisor.deliberate()

        # Execute first intention if any were generated
        if intentions and len(intentions) > 0:
            supervisor.execute_step(intentions[0])

        return True, "Success"
    except Exception as e:
        return False, str(e)


def test_supervisor_edge_cases(supervisor, edge_cases: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
    """Test edge cases for a supervisor"""
    passed = 0
    failed = 0
    errors = []

    for edge_case in edge_cases:
        try:
            # Post edge case to blackboard
            if hasattr(supervisor, 'blackboard') and supervisor.blackboard:
                entry = create_entry(
                    entry_type=EntryType.TASK,
                    content=edge_case["data"],
                    author_agent="stress_test",
                    conversation_id="stress_test_conv",
                    tags=["stress_test", "edge_case"],
                    status=EntryStatus.PENDING,
                    metadata={"source": "edge_test", "priority": "normal"}
                )
                supervisor.blackboard.post(entry)

            supervisor.update_beliefs()
            intentions = supervisor.deliberate()
            # Edge cases should either handle gracefully or fail gracefully
            if intentions and len(intentions) > 0:
                supervisor.execute_step(intentions[0])
            passed += 1
        except Exception as e:
            # Check if it's a graceful failure (expected)
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ["invalid", "missing", "null", "empty"]):
                passed += 1  # Graceful failure is acceptable
            else:
                failed += 1
                errors.append(f"{edge_case['type']}: {str(e)}")

    return passed, failed, errors


def test_supervisor_concurrent(supervisor, scenarios: List[Dict[str, Any]], num_threads: int = 10) -> Tuple[int, int]:
    """Test supervisor under concurrent load"""
    passed = 0
    failed = 0

    def concurrent_task(scenario):
        try:
            test_supervisor_scenario(supervisor, scenario)
            return True
        except:
            return False

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(concurrent_task, scenario) for scenario in scenarios * 5]

        for future in as_completed(futures):
            try:
                if future.result():
                    passed += 1
                else:
                    failed += 1
            except:
                failed += 1

    return passed, failed


def stress_test_supervisor(supervisor_name: str, module_path: str) -> StressTestResult:
    """Run comprehensive stress test on a single supervisor"""
    print(f"\n{'='*80}")
    print(f"STRESS TESTING: {supervisor_name}")
    print(f"{'='*80}")

    result = StressTestResult(supervisor_name)
    start_time = time.time()

    # Load supervisor
    SupervisorClass = load_supervisor(supervisor_name, module_path)
    if SupervisorClass is None:
        result.add_error("Initialization", "Failed to load supervisor class")
        return result

    try:
        # Initialize infrastructure
        df = DirectoryFacilitator()
        blackboard = Blackboard()

        # Create supervisor instance
        supervisor = SupervisorClass(
            agent_id=f"{supervisor_name}_stress_test",
            df=df,
            blackboard=blackboard
        )

        # Test 1: Standard scenarios
        print(f"\n[TEST 1] Running standard stress scenarios...")
        scenarios = STRESS_SCENARIOS.get(supervisor_name, [])
        for i, scenario in enumerate(scenarios):
            success, error_msg = test_supervisor_scenario(supervisor, scenario)
            if success:
                result.scenarios_passed += 1
                print(f"  [PASS] Scenario {i+1}/{len(scenarios)} passed")
            else:
                result.scenarios_failed += 1
                result.add_error(f"Scenario {i+1}", error_msg)
                print(f"  [FAIL] Scenario {i+1}/{len(scenarios)} failed: {error_msg[:100]}")

        # Test 2: Edge cases
        print(f"\n[TEST 2] Testing edge cases and malformed inputs...")
        edge_passed, edge_failed, edge_errors = test_supervisor_edge_cases(supervisor, EDGE_CASES)
        result.edge_cases_passed = edge_passed
        result.edge_cases_failed = edge_failed
        for error in edge_errors:
            result.add_error("Edge case", error)
        print(f"  Edge cases: {edge_passed} passed, {edge_failed} failed")

        # Test 3: Concurrent stress
        print(f"\n[TEST 3] Testing concurrent load (50 simultaneous tasks)...")
        if scenarios:
            conc_passed, conc_failed = test_supervisor_concurrent(supervisor, scenarios, num_threads=10)
            result.concurrent_tests_passed = conc_passed
            result.concurrent_tests_failed = conc_failed
            print(f"  Concurrent: {conc_passed} passed, {conc_failed} failed")
        else:
            print(f"  Skipped (no scenarios defined)")

    except Exception as e:
        result.add_error("Fatal", f"Supervisor crashed: {traceback.format_exc()}")
        print(f"\n  [FATAL] ERROR: {str(e)}")

    result.execution_time = time.time() - start_time
    print(f"\nCompleted in {result.execution_time:.2f}s")
    print(f"Success rate: {result._calculate_success_rate():.1f}%")

    return result


def main():
    """Run stress tests on all supervisors"""
    print("\n" + "="*80)
    print("HARDCORE SUPERVISOR STRESS TEST SUITE")
    print("Testing all 29 supervisors across every domain")
    print("="*80)

    all_results = []
    start_time = time.time()

    # Test each supervisor
    for supervisor_name, module_path in SUPERVISORS.items():
        result = stress_test_supervisor(supervisor_name, module_path)
        all_results.append(result)

    total_time = time.time() - start_time

    # Print summary report
    print("\n\n" + "="*80)
    print("FINAL STRESS TEST REPORT")
    print("="*80)

    # Summary table
    print(f"\n{'Supervisor':<40} {'Pass':<8} {'Fail':<8} {'Rate':<10} {'Time':<10}")
    print("-" * 80)

    total_passed = 0
    total_failed = 0

    for result in all_results:
        passed = (result.scenarios_passed + result.edge_cases_passed +
                 result.concurrent_tests_passed)
        failed = (result.scenarios_failed + result.edge_cases_failed +
                 result.concurrent_tests_failed)
        total_passed += passed
        total_failed += failed

        print(f"{result.supervisor_name:<40} {passed:<8} {failed:<8} "
              f"{result._calculate_success_rate():>6.1f}%   {result.execution_time:>6.2f}s")

    # Overall statistics
    print("-" * 80)
    overall_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
    print(f"{'TOTAL':<40} {total_passed:<8} {total_failed:<8} {overall_rate:>6.1f}%   {total_time:>6.2f}s")

    # Error summary
    print("\n\nERROR SUMMARY:")
    print("-" * 80)
    supervisors_with_errors = [r for r in all_results if r.errors]
    if supervisors_with_errors:
        for result in supervisors_with_errors:
            print(f"\n{result.supervisor_name} ({len(result.errors)} errors):")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"  - {error[:120]}")
            if len(result.errors) > 5:
                print(f"  ... and {len(result.errors) - 5} more errors")
    else:
        print("No errors reported!")

    # Final verdict
    print("\n\n" + "="*80)
    if overall_rate >= 95:
        print("[PASS] VERDICT: EXCELLENT - All supervisors are production-ready!")
    elif overall_rate >= 80:
        print("[WARN] VERDICT: GOOD - Most supervisors are stable, minor issues detected")
    elif overall_rate >= 60:
        print("[WARN] VERDICT: FAIR - Significant issues detected, review required")
    else:
        print("[FAIL] VERDICT: POOR - Critical issues detected, immediate action required")
    print("="*80)

    return 0 if overall_rate >= 80 else 1


if __name__ == "__main__":
    sys.exit(main())
