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
Control Theory Domain - Brutal Research-Level Stress Tests
============================================================

50 BRUTAL stress tests designed to BREAK the system.

Targets:
- DynamicalSystemsSpecialist
- LinearControlSpecialist

Categories:
1. Non-hyperbolic equilibria and center manifold analysis
2. Lyapunov exponents of chaotic systems
3. Bifurcation detection (especially Hopf)
4. LQR with uncontrollable/unobservable modes
5. Repeated eigenvalues and Jordan form issues
6. Stability boundary conditions
7. Pole placement with complex constraints
8. Gramian conditioning issues
9. Homoclinic/heteroclinic orbits
10. Non-minimum phase systems

NO SYMPY - Pure Python/NumPy stress tests.
"""

import numpy as np
from typing import Dict, Any, List

# =============================================================================
# BRUTAL CONTROL THEORY STRESS TESTS
# =============================================================================

CONTROL_THEORY_STRESS_TESTS: List[Dict[str, Any]] = [
    # =========================================================================
    # CATEGORY 1: NON-HYPERBOLIC EQUILIBRIA (Tests 001-005)
    # =========================================================================
    {
        "test_id": "CTRL_001",
        "category": "non_hyperbolic_equilibria",
        "input": {
            "system": "dx/dt = x^2, dy/dt = -y",
            "vector_field": "lambda X: np.array([X[0]**2, -X[1]])",
            "fixed_point": "[0, 0]",
            "task": "classify_fixed_point"
        },
        "expected": {
            "stability": "semi-stable (saddle-node at origin)",
            "eigenvalues": [0, -1],
            "center_manifold": "x-axis is center manifold",
            "notes": "Linearization fails: zero eigenvalue requires center manifold reduction"
        },
        "difficulty": "brutal",
        "rationale": "Zero eigenvalue makes linearization degenerate. The origin is a saddle-node where the center manifold theorem is needed. Standard eigenvalue classification will incorrectly report 'degenerate' without understanding the semi-stable nature."
    },
    {
        "test_id": "CTRL_002",
        "category": "non_hyperbolic_equilibria",
        "input": {
            "system": "dx/dt = y, dy/dt = -sin(x)",
            "vector_field": "lambda X: np.array([X[1], -np.sin(X[0])])",
            "fixed_point": "[0, 0]",
            "task": "classify_fixed_point"
        },
        "expected": {
            "stability": "center (non-hyperbolic)",
            "eigenvalues": [1j, -1j],
            "notes": "Pure imaginary eigenvalues - Hamiltonian system with energy conservation. Linearization suggests center but nonlinear analysis confirms closed orbits exist (pendulum)."
        },
        "difficulty": "brutal",
        "rationale": "Pure imaginary eigenvalues at the origin. The simple pendulum is a textbook case where linearization gives a center, but the nonlinear system has bounded oscillations. The specialist must correctly identify this as a true center, not a focus."
    },
    {
        "test_id": "CTRL_003",
        "category": "non_hyperbolic_equilibria",
        "input": {
            "system": "dx/dt = x^2 - y^2, dy/dt = 2xy",
            "vector_field": "lambda X: np.array([X[0]**2 - X[1]**2, 2*X[0]*X[1]])",
            "fixed_point": "[0, 0]",
            "task": "classify_fixed_point"
        },
        "expected": {
            "stability": "degenerate with double zero eigenvalue",
            "eigenvalues": [0, 0],
            "notes": "Both eigenvalues are zero. This is f(z) = z^2 in complex coordinates. Blowup analysis required."
        },
        "difficulty": "extreme",
        "rationale": "Double zero eigenvalue at origin. This is a nilpotent singularity requiring blowup techniques. The Jacobian is the zero matrix, making all standard classification methods fail. The topological type is a 'cusp'."
    },
    {
        "test_id": "CTRL_004",
        "category": "non_hyperbolic_equilibria",
        "input": {
            "system": "dx/dt = -y + x*(x^2+y^2), dy/dt = x + y*(x^2+y^2)",
            "vector_field": "lambda X: np.array([-X[1] + X[0]*(X[0]**2+X[1]**2), X[0] + X[1]*(X[0]**2+X[1]**2)])",
            "fixed_point": "[0, 0]",
            "task": "classify_fixed_point"
        },
        "expected": {
            "stability": "unstable focus (spiral source)",
            "eigenvalues": [1j, -1j],
            "notes": "Linearization gives pure imaginary eigenvalues (center), but nonlinear terms make it an unstable spiral. This is a TRAP - the correct answer contradicts linearization!"
        },
        "difficulty": "extreme",
        "rationale": "Classic counterexample to naive linearization. The linear part suggests a center, but in polar coordinates dr/dt = r^3 > 0 shows trajectories spiral outward. The specialist must compute higher-order terms or simulate to detect the true instability."
    },
    {
        "test_id": "CTRL_005",
        "category": "non_hyperbolic_equilibria",
        "input": {
            "system": "Bogdanov-Takens normal form: dx/dt = y, dy/dt = x^2 + xy",
            "vector_field": "lambda X: np.array([X[1], X[0]**2 + X[0]*X[1]])",
            "fixed_point": "[0, 0]",
            "task": "classify_fixed_point"
        },
        "expected": {
            "stability": "Bogdanov-Takens bifurcation point (codimension-2)",
            "eigenvalues": [0, 0],
            "notes": "Double zero eigenvalue with nontrivial Jordan block. Unfolds to saddle-node and Hopf bifurcations. Requires normal form theory."
        },
        "difficulty": "pathological",
        "rationale": "The Bogdanov-Takens bifurcation is a codimension-2 singularity with a double zero eigenvalue. Standard classification completely fails. This requires computing the nilpotent Jordan structure and recognizing the specific normal form."
    },

    # =========================================================================
    # CATEGORY 2: LYAPUNOV EXPONENTS OF CHAOTIC SYSTEMS (Tests 006-010)
    # =========================================================================
    {
        "test_id": "CTRL_006",
        "category": "lyapunov_exponents",
        "input": {
            "system": "Lorenz system: sigma=10, rho=28, beta=8/3",
            "vector_field": "lambda X: np.array([10*(X[1]-X[0]), X[0]*(28-X[2])-X[1], X[0]*X[1]-8/3*X[2]])",
            "initial_condition": "[1, 1, 1]",
            "t_total": 1000,
            "task": "compute_lyapunov_exponents"
        },
        "expected": {
            "lyapunov_exponents": [0.906, 0.0, -14.57],
            "is_chaotic": True,
            "notes": "Lambda_1 > 0 confirms chaos. Lambda_2 = 0 is marginal direction along trajectory. Sum of exponents matches divergence (trace of Jacobian averaged over attractor)."
        },
        "difficulty": "brutal",
        "rationale": "The Lorenz system is the canonical chaotic system. Computing accurate Lyapunov exponents requires very long integration times (t > 500) with careful QR re-orthogonalization. Numerical errors accumulate, and the specialist must handle the sensitive dependence on initial conditions."
    },
    {
        "test_id": "CTRL_007",
        "category": "lyapunov_exponents",
        "input": {
            "system": "Rossler system: a=0.2, b=0.2, c=5.7",
            "vector_field": "lambda X: np.array([-X[1]-X[2], X[0]+0.2*X[1], 0.2+X[2]*(X[0]-5.7)])",
            "initial_condition": "[0.1, 0.1, 0.1]",
            "t_total": 2000,
            "task": "compute_lyapunov_exponents"
        },
        "expected": {
            "lyapunov_exponents": [0.071, 0.0, -5.39],
            "is_chaotic": True,
            "kaplan_yorke_dimension": 2.013,
            "notes": "Smaller positive exponent than Lorenz means chaos is 'weaker'. The Kaplan-Yorke dimension slightly above 2 indicates a nearly 2D attractor."
        },
        "difficulty": "brutal",
        "rationale": "The Rossler attractor has a smaller positive Lyapunov exponent than Lorenz, making it harder to distinguish from numerical noise. The specialist must integrate for very long times (t > 1000) to get accurate estimates, and the folding is more subtle."
    },
    {
        "test_id": "CTRL_008",
        "category": "lyapunov_exponents",
        "input": {
            "system": "Chen system: a=35, b=3, c=28",
            "vector_field": "lambda X: np.array([35*(X[1]-X[0]), -7*X[0]-X[0]*X[2]+28*X[1], X[0]*X[1]-3*X[2]])",
            "initial_condition": "[1, 1, 1]",
            "t_total": 1500,
            "task": "compute_lyapunov_exponents"
        },
        "expected": {
            "lyapunov_exponents": [2.027, 0.0, -12.027],
            "is_chaotic": True,
            "notes": "Chen system has larger positive exponent than Lorenz - more chaotic. The specialist must handle the faster separation rate."
        },
        "difficulty": "extreme",
        "rationale": "The Chen attractor has a larger positive Lyapunov exponent, meaning nearby trajectories separate faster. This strains the numerical integrator and QR decomposition frequency. If the specialist re-orthogonalizes too infrequently, vectors will overflow."
    },
    {
        "test_id": "CTRL_009",
        "category": "lyapunov_exponents",
        "input": {
            "system": "4D hyperchaotic Lorenz: parameters as Rossler-hyperchaotic",
            "vector_field": "lambda X: np.array([10*(X[1]-X[0])+X[3], 28*X[0]-X[1]-X[0]*X[2], X[0]*X[1]-8/3*X[2], -X[0]-X[3]])",
            "initial_condition": "[1, 1, 1, 1]",
            "t_total": 2000,
            "task": "compute_lyapunov_exponents"
        },
        "expected": {
            "lyapunov_exponents": [0.37, 0.12, 0.0, -14.09],
            "is_hyperchaotic": True,
            "notes": "TWO positive Lyapunov exponents = hyperchaos. Trajectories separate exponentially in two independent directions simultaneously."
        },
        "difficulty": "extreme",
        "rationale": "Hyperchaotic systems have two positive Lyapunov exponents, creating a 2D unstable manifold. The specialist must accurately compute all four exponents and correctly identify hyperchaos vs regular chaos. The 4D state space makes QR decomposition more expensive."
    },
    {
        "test_id": "CTRL_010",
        "category": "lyapunov_exponents",
        "input": {
            "system": "Lorenz at rho=166.07 (metastable chaos)",
            "vector_field": "lambda X: np.array([10*(X[1]-X[0]), X[0]*(166.07-X[2])-X[1], X[0]*X[1]-8/3*X[2]])",
            "initial_condition": "[1, 1, 1]",
            "t_total": 5000,
            "task": "compute_lyapunov_exponents"
        },
        "expected": {
            "lyapunov_exponents": "complex behavior - intermittent chaos",
            "notes": "At rho=166.07, the Lorenz system exhibits metastable chaos with long transients between two attractors. Lyapunov exponents are ill-defined over finite time due to intermittency."
        },
        "difficulty": "pathological",
        "rationale": "At certain parameter values, the Lorenz system exhibits intermittency and metastability. The Lyapunov exponents computed over finite time depend strongly on which basin the trajectory visits. The specialist will give inconsistent results depending on initial conditions and integration time."
    },

    # =========================================================================
    # CATEGORY 3: BIFURCATION DETECTION NEAR HOPF (Tests 011-015)
    # =========================================================================
    {
        "test_id": "CTRL_011",
        "category": "hopf_bifurcation",
        "input": {
            "system": "dx/dt = mu*x - y - x*(x^2+y^2), dy/dt = x + mu*y - y*(x^2+y^2)",
            "vector_field_param": "lambda X, mu: np.array([mu*X[0] - X[1] - X[0]*(X[0]**2+X[1]**2), X[0] + mu*X[1] - X[1]*(X[0]**2+X[1]**2)])",
            "param_range": [-0.5, 0.5],
            "task": "detect_hopf_bifurcation"
        },
        "expected": {
            "bifurcation_type": "supercritical Hopf",
            "critical_parameter": 0.0,
            "eigenvalues_at_critical": [1j, -1j],
            "limit_cycle_radius": "sqrt(mu) for mu > 0",
            "notes": "Stable limit cycle born for mu > 0. The amplitude grows as sqrt(mu). First Lyapunov coefficient is negative (supercritical)."
        },
        "difficulty": "brutal",
        "rationale": "This is the canonical supercritical Hopf normal form. The specialist must detect the bifurcation at mu=0 and ideally determine it is supercritical (stable limit cycle emerges). Simply detecting stability change is not enough - the type matters."
    },
    {
        "test_id": "CTRL_012",
        "category": "hopf_bifurcation",
        "input": {
            "system": "dx/dt = mu*x - y + x*(x^2+y^2), dy/dt = x + mu*y + y*(x^2+y^2)",
            "vector_field_param": "lambda X, mu: np.array([mu*X[0] - X[1] + X[0]*(X[0]**2+X[1]**2), X[0] + mu*X[1] + X[1]*(X[0]**2+X[1]**2)])",
            "param_range": [-0.5, 0.5],
            "task": "detect_hopf_bifurcation"
        },
        "expected": {
            "bifurcation_type": "subcritical Hopf",
            "critical_parameter": 0.0,
            "notes": "UNSTABLE limit cycle exists for mu < 0 and disappears at mu=0. The stable focus becomes unstable focus but no stable periodic orbit nearby. First Lyapunov coefficient is positive (subcritical)."
        },
        "difficulty": "extreme",
        "rationale": "Subcritical Hopf is much harder to detect numerically because the limit cycle is unstable and cannot be found by forward integration. The specialist must compute the first Lyapunov coefficient (Floquet exponent) to distinguish subcritical from supercritical."
    },
    {
        "test_id": "CTRL_013",
        "category": "hopf_bifurcation",
        "input": {
            "system": "Brusselator: dx/dt = 1 - (b+1)x + ax^2y, dy/dt = bx - ax^2y",
            "vector_field_param": "lambda X, b: np.array([1 - (b+1)*X[0] + 2*X[0]**2*X[1], b*X[0] - 2*X[0]**2*X[1]])",
            "fixed_parameter": {"a": 2},
            "param_range": [0.5, 3.5],
            "task": "detect_hopf_bifurcation"
        },
        "expected": {
            "bifurcation_type": "supercritical Hopf",
            "critical_parameter": "b_crit = 1 + a = 3 (for a=2)",
            "fixed_point": "[1, b/a] = [1, b/2]",
            "notes": "Brusselator has Hopf bifurcation at b = 1 + a. Limit cycle amplitude grows as sqrt(b - b_crit). Classic chemical oscillator model."
        },
        "difficulty": "brutal",
        "rationale": "The Brusselator is a classic 2D chemical kinetics model. The fixed point is at (1, b/a) and undergoes Hopf bifurcation at b = 1 + a. The specialist must correctly identify the fixed point, track it as b varies, and detect the bifurcation."
    },
    {
        "test_id": "CTRL_014",
        "category": "hopf_bifurcation",
        "input": {
            "system": "Van der Pol near zero damping: dx/dt = y, dy/dt = mu*(1-x^2)*y - x",
            "vector_field_param": "lambda X, mu: np.array([X[1], mu*(1-X[0]**2)*X[1] - X[0]])",
            "param_range": [-0.1, 0.1],
            "task": "detect_hopf_bifurcation"
        },
        "expected": {
            "bifurcation_type": "degenerate Hopf at mu=0",
            "notes": "At mu=0, system is conservative (linear oscillator). For any mu != 0, there exists a stable limit cycle. The bifurcation at mu=0 is degenerate - not a standard Hopf."
        },
        "difficulty": "extreme",
        "rationale": "The Van der Pol oscillator at mu=0 is a simple harmonic oscillator (center). For any mu > 0 OR mu < 0, a unique stable limit cycle exists. This is NOT a standard Hopf bifurcation but a degenerate one where the limit cycle exists on both sides."
    },
    {
        "test_id": "CTRL_015",
        "category": "hopf_bifurcation",
        "input": {
            "system": "3D Hopf: dx/dt = mu*x - y - x*r^2, dy/dt = x + mu*y - y*r^2, dz/dt = -z",
            "vector_field_param": "lambda X, mu: np.array([mu*X[0] - X[1] - X[0]*(X[0]**2+X[1]**2), X[0] + mu*X[1] - X[1]*(X[0]**2+X[1]**2), -X[2]])",
            "param_range": [-0.5, 0.5],
            "task": "detect_hopf_bifurcation"
        },
        "expected": {
            "bifurcation_type": "Hopf in 2D subspace, stable in z",
            "eigenvalues_at_critical": [1j, -1j, -1],
            "notes": "The z-direction is always stable (eigenvalue -1). Hopf occurs in the (x,y) plane. The 3D analysis must correctly identify the 2D center manifold."
        },
        "difficulty": "extreme",
        "rationale": "In 3D, the Hopf bifurcation occurs on a 2D center manifold while the third direction is hyperbolic. The specialist must correctly identify that the bifurcation is in the (x,y) subspace and not be confused by the stable z-direction."
    },

    # =========================================================================
    # CATEGORY 4: LQR WITH UNCONTROLLABLE MODES (Tests 016-020)
    # =========================================================================
    {
        "test_id": "CTRL_016",
        "category": "lqr_uncontrollable",
        "input": {
            "system": {
                "A": [[0, 1, 0], [0, 0, 0], [0, 0, -1]],
                "B": [[0], [1], [0]]
            },
            "Q": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "R": [[1]],
            "task": "design_lqr"
        },
        "expected": {
            "status": "partially_stabilizable",
            "controllable_modes": ["double integrator in (x1, x2)"],
            "uncontrollable_modes": ["x3 with eigenvalue -1 (stable, ok)"],
            "notes": "The mode x3 is uncontrollable but stable, so LQR can still work for the controllable subsystem. The Riccati equation has a solution but K will not affect x3."
        },
        "difficulty": "brutal",
        "rationale": "This system has an uncontrollable mode at eigenvalue -1. Since it is stable, the system is stabilizable and LQR has a solution. However, the specialist must recognize that the gain K will only affect the controllable subspace."
    },
    {
        "test_id": "CTRL_017",
        "category": "lqr_uncontrollable",
        "input": {
            "system": {
                "A": [[0, 1, 0], [0, 0, 0], [0, 0, 1]],
                "B": [[0], [1], [0]]
            },
            "Q": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "R": [[1]],
            "task": "design_lqr"
        },
        "expected": {
            "status": "not_stabilizable",
            "controllable_modes": ["double integrator in (x1, x2)"],
            "uncontrollable_modes": ["x3 with eigenvalue +1 (UNSTABLE)"],
            "notes": "The mode x3 is uncontrollable AND unstable (eigenvalue +1). LQR CANNOT stabilize this system. Riccati equation has no stabilizing solution."
        },
        "difficulty": "extreme",
        "rationale": "This system has an uncontrollable UNSTABLE mode. No state feedback can stabilize it. The iterative Riccati solver will diverge or give a non-stabilizing result. The specialist must detect this and refuse to give a meaningless answer."
    },
    {
        "test_id": "CTRL_018",
        "category": "lqr_uncontrollable",
        "input": {
            "system": {
                "A": [[1, 0, 0], [0, -2, 0], [0, 0, 0.5]],
                "B": [[1], [0], [1]]
            },
            "Q": "identity",
            "R": [[0.01]],
            "task": "design_lqr"
        },
        "expected": {
            "status": "check_stabilizability",
            "notes": "Mode 2 (eigenvalue -2) is uncontrollable (B[1]=0). Modes 1 and 3 are controllable. System is stabilizable because the uncontrollable mode is stable. Small R causes high gains - conditioning issue."
        },
        "difficulty": "brutal",
        "rationale": "Mixing controllable and uncontrollable modes with small R (cheap control) leads to numerical conditioning issues. The Riccati solution will have elements spanning many orders of magnitude, challenging the iterative solver."
    },
    {
        "test_id": "CTRL_019",
        "category": "lqr_uncontrollable",
        "input": {
            "system": {
                "A": [[0, 1], [-2, -3]],
                "B": [[0], [0]]
            },
            "Q": [[1, 0], [0, 1]],
            "R": [[1]],
            "task": "design_lqr"
        },
        "expected": {
            "status": "completely_uncontrollable",
            "notes": "B = 0 means no control authority at all. The system is completely uncontrollable. LQR is meaningless. The specialist should reject this case."
        },
        "difficulty": "extreme",
        "rationale": "With B=0, the input has no effect on the state. The controllability matrix is zero. Any LQR result is meaningless. The specialist must detect this degenerate case and refuse to compute a gain."
    },
    {
        "test_id": "CTRL_020",
        "category": "lqr_uncontrollable",
        "input": {
            "system": {
                "A": [[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]],
                "B": [[0], [0], [0], [1]]
            },
            "Q": "identity",
            "R": [[1e-6]],
            "task": "design_lqr"
        },
        "expected": {
            "notes": "Quadruple integrator chain with very cheap control. System is controllable (from x4 only). Extremely ill-conditioned Riccati equation due to the long chain and small R. Gains will span 12+ orders of magnitude."
        },
        "difficulty": "pathological",
        "rationale": "A 4th-order integrator chain with R=1e-6 creates an extremely ill-conditioned problem. The controllability matrix has condition number ~ 1e12. The Riccati solution will have entries from ~1 to ~1e12, causing numerical overflow in the iterative solver."
    },

    # =========================================================================
    # CATEGORY 5: REPEATED EIGENVALUES AND JORDAN FORMS (Tests 021-025)
    # =========================================================================
    {
        "test_id": "CTRL_021",
        "category": "repeated_eigenvalues",
        "input": {
            "system": {
                "A": [[2, 1], [0, 2]],
                "B": [[0], [1]]
            },
            "task": "check_controllability"
        },
        "expected": {
            "is_controllable": True,
            "rank": 2,
            "notes": "Jordan block with eigenvalue 2 (multiplicity 2). Single eigenvector. Controllable because B excites the generalized eigenvector direction. The controllability matrix is [[0,1],[1,2]] with rank 2."
        },
        "difficulty": "brutal",
        "rationale": "Repeated eigenvalue with Jordan block. The system is controllable despite B pointing into the generalized eigenvector. Many controllability tests fail to handle non-diagonalizable A matrices correctly."
    },
    {
        "test_id": "CTRL_022",
        "category": "repeated_eigenvalues",
        "input": {
            "system": {
                "A": [[2, 0], [0, 2]],
                "B": [[1], [0]]
            },
            "task": "check_controllability"
        },
        "expected": {
            "is_controllable": False,
            "rank": 1,
            "notes": "Repeated eigenvalue 2 with diagonal Jordan form (two independent eigenvectors). B only excites first eigenvector direction. The mode along [0,1] is uncontrollable."
        },
        "difficulty": "brutal",
        "rationale": "When A has repeated eigenvalues but IS diagonalizable, controllability requires B to span all eigenvector directions. Here B = [1,0]^T misses the [0,1] eigenvector, making the system uncontrollable."
    },
    {
        "test_id": "CTRL_023",
        "category": "repeated_eigenvalues",
        "input": {
            "system": {
                "A": [[0, 1, 0], [0, 0, 1], [0, 0, 0]],
                "B": [[0], [0], [1]]
            },
            "desired_poles": [-1, -2, -3],
            "task": "pole_placement"
        },
        "expected": {
            "is_controllable": True,
            "notes": "Triple zero eigenvalue in Jordan form (nilpotent). Controllable from x3. Ackermann's formula works but requires computing A^3 = 0. The gain K will place poles at -1, -2, -3."
        },
        "difficulty": "extreme",
        "rationale": "A is nilpotent (A^3 = 0). Ackermann's formula involves computing the characteristic polynomial of desired poles evaluated at A. With nilpotent A, this simplifies but the specialist must handle A^k = 0 for k >= 3."
    },
    {
        "test_id": "CTRL_024",
        "category": "repeated_eigenvalues",
        "input": {
            "system": {
                "A": [[-1, 1, 0, 0], [0, -1, 1, 0], [0, 0, -1, 1], [0, 0, 0, -1]],
                "B": [[0], [0], [0], [1]]
            },
            "task": "check_controllability"
        },
        "expected": {
            "is_controllable": True,
            "notes": "4x4 Jordan block with eigenvalue -1. Single eigenvector but three generalized eigenvectors. Controllable from x4. The controllability matrix is upper triangular with nonzero diagonal."
        },
        "difficulty": "extreme",
        "rationale": "Large Jordan block with single eigenvalue -1 repeated 4 times. The specialist must correctly identify that despite having only one eigenvector, the system is controllable because B excites the generalized eigenvector chain."
    },
    {
        "test_id": "CTRL_025",
        "category": "repeated_eigenvalues",
        "input": {
            "system": {
                "A": [[-1, 1, 0, 0], [0, -1, 0, 0], [0, 0, -1, 1], [0, 0, 0, -1]],
                "B": [[0], [1], [0], [1]]
            },
            "task": "check_controllability"
        },
        "expected": {
            "is_controllable": True,
            "notes": "Two 2x2 Jordan blocks both with eigenvalue -1. B excites both chains at x2 and x4. Controllable because B reaches into both Jordan chains."
        },
        "difficulty": "extreme",
        "rationale": "Multiple Jordan blocks with the same eigenvalue. Controllability requires B to have components in each Jordan chain. The specialist must correctly identify the Jordan structure and verify B excites all chains."
    },

    # =========================================================================
    # CATEGORY 6: STABILITY BOUNDARY CONDITIONS (Tests 026-030)
    # =========================================================================
    {
        "test_id": "CTRL_026",
        "category": "stability_boundary",
        "input": {
            "system": {
                "A": [[0, 1], [-1, 0]],
                "B": [[0], [1]]
            },
            "task": "check_stability"
        },
        "expected": {
            "is_stable": False,
            "is_marginally_stable": True,
            "eigenvalues": [1j, -1j],
            "notes": "Pure imaginary eigenvalues = marginally stable. Trajectories neither converge nor diverge but oscillate. The slightest perturbation to A could make it stable or unstable."
        },
        "difficulty": "brutal",
        "rationale": "Eigenvalues exactly on the imaginary axis. The system is on the stability boundary. Numerical eigenvalue computation may introduce small real parts that incorrectly classify it as stable or unstable."
    },
    {
        "test_id": "CTRL_027",
        "category": "stability_boundary",
        "input": {
            "system": {
                "A": [[-1e-10, 1], [-1, -1e-10]],
                "B": [[0], [1]]
            },
            "task": "check_stability"
        },
        "expected": {
            "is_stable": True,
            "eigenvalues": "-1e-10 +/- i (approximately)",
            "notes": "Eigenvalues have real part -1e-10, technically stable but BARELY. Any numerical noise could flip the classification. Time constant is 1e10 seconds (317 years)."
        },
        "difficulty": "extreme",
        "rationale": "The eigenvalues have real part -1e-10, which is stable but smaller than typical floating-point tolerances. The specialist's epsilon threshold must be chosen carefully. Declaring this 'stable' is technically correct but practically meaningless."
    },
    {
        "test_id": "CTRL_028",
        "category": "stability_boundary",
        "input": {
            "system": {
                "A": [[0, 0], [0, -1]],
                "B": [[1], [0]]
            },
            "task": "check_stability"
        },
        "expected": {
            "is_stable": False,
            "is_marginally_stable": True,
            "eigenvalues": [0, -1],
            "notes": "One eigenvalue at origin (marginally stable), one at -1 (stable). The zero eigenvalue makes the overall system marginally stable, not asymptotically stable."
        },
        "difficulty": "brutal",
        "rationale": "A zero eigenvalue means the system has a line of equilibria. The specialist must correctly identify this as marginally stable, not stable. The mode at -1 is stable but the zero mode prevents asymptotic stability."
    },
    {
        "test_id": "CTRL_029",
        "category": "stability_boundary",
        "input": {
            "system_discrete": {
                "A": [[0, 1], [-1, 0]],
                "B": [[0], [1]],
                "dt": 0.1
            },
            "task": "check_stability"
        },
        "expected": {
            "is_stable": False,
            "is_marginally_stable": True,
            "eigenvalues_magnitude": 1.0,
            "notes": "Discrete-time: eigenvalues on unit circle (magnitude exactly 1). Marginally stable discrete system. The continuous equivalent has eigenvalues at +/- i."
        },
        "difficulty": "brutal",
        "rationale": "For discrete-time systems, stability requires |eigenvalues| < 1. Eigenvalues exactly on the unit circle are marginally stable. The specialist must correctly apply discrete-time stability criteria."
    },
    {
        "test_id": "CTRL_030",
        "category": "stability_boundary",
        "input": {
            "system": {
                "A": [[-1, 100], [0, -1]],
                "B": [[0], [1]]
            },
            "task": "check_stability_and_transient"
        },
        "expected": {
            "is_stable": True,
            "eigenvalues": [-1, -1],
            "transient_growth": "LARGE (up to 100x before decay)",
            "notes": "Stable (eigenvalue -1) but highly non-normal. The off-diagonal 100 causes massive transient growth before eventual decay. Pseudospectrum extends far into right half plane."
        },
        "difficulty": "extreme",
        "rationale": "A stable but highly non-normal matrix. Eigenvalue analysis says stable (Re(lambda) = -1) but the pseudospectrum shows epsilon-pseudoeigenvalues in the right half plane for small epsilon. The specialist must recognize that asymptotic stability does not imply good transient behavior."
    },

    # =========================================================================
    # CATEGORY 7: POLE PLACEMENT WITH COMPLEX CONSTRAINTS (Tests 031-035)
    # =========================================================================
    {
        "test_id": "CTRL_031",
        "category": "pole_placement",
        "input": {
            "system": {
                "A": [[0, 1], [-2, -3]],
                "B": [[0], [1]]
            },
            "desired_poles": [-1+2j, -1-2j],
            "task": "pole_placement"
        },
        "expected": {
            "K": "[[3, 2]]",
            "closed_loop_A": "[[0, 1], [-5, -5]]",
            "notes": "Complex conjugate pair placement. The gain K must be real even though poles are complex. Ackermann's formula handles this naturally."
        },
        "difficulty": "brutal",
        "rationale": "Complex conjugate pole placement is standard but the specialist must ensure K is real-valued. The characteristic polynomial is (s+1)^2 + 4 = s^2 + 2s + 5, giving closed-loop A with trace=-2 and det=5."
    },
    {
        "test_id": "CTRL_032",
        "category": "pole_placement",
        "input": {
            "system": {
                "A": [[0, 1, 0], [0, 0, 1], [-6, -11, -6]],
                "B": [[0], [0], [1]]
            },
            "desired_poles": [-10, -10, -10],
            "task": "pole_placement"
        },
        "expected": {
            "notes": "All three poles at -10 (repeated). Ackermann computes (A+10I)^3 = 0 for nilpotent part. High gains needed to move poles from (-1,-2,-3) to (-10,-10,-10). K elements will be large."
        },
        "difficulty": "extreme",
        "rationale": "Placing all poles at the same location requires the closed-loop A to have a specific Jordan structure. With a SISO system, this is achievable but leads to high gains when moving poles far from their open-loop locations."
    },
    {
        "test_id": "CTRL_033",
        "category": "pole_placement",
        "input": {
            "system": {
                "A": [[0, 1], [0, 0]],
                "B": [[0, 1], [1, 0]]
            },
            "desired_poles": [-1, -2],
            "task": "pole_placement"
        },
        "expected": {
            "notes": "MIMO pole placement (2 inputs, 2 states). Infinitely many K matrices can achieve the desired poles. The specialist must pick one (often minimum norm). Ackermann's formula does not apply directly."
        },
        "difficulty": "extreme",
        "rationale": "MIMO pole placement has non-unique solutions. The set of valid K matrices forms an affine subspace. The specialist's simple iterative method may not converge to any specific solution and may give inconsistent results."
    },
    {
        "test_id": "CTRL_034",
        "category": "pole_placement",
        "input": {
            "system": {
                "A": [[0, 1], [-2, -3]],
                "B": [[1], [0]]
            },
            "desired_poles": [-5, -6],
            "task": "pole_placement"
        },
        "expected": {
            "notes": "Controllable system with B in 'wrong' direction. The controllability matrix [[1,0],[0,1]] is still full rank (via AB). Ackermann works but the gain structure is different from the B=[0,1] case."
        },
        "difficulty": "brutal",
        "rationale": "When B affects x1 directly instead of x2, the control effort propagates differently through the system. The specialist must correctly compute the controllability matrix inverse for Ackermann's formula."
    },
    {
        "test_id": "CTRL_035",
        "category": "pole_placement",
        "input": {
            "system": {
                "A": [[1, 0], [0, -1]],
                "B": [[1], [0]]
            },
            "desired_poles": [-1, -2],
            "task": "pole_placement"
        },
        "expected": {
            "status": "partially_achievable",
            "notes": "Mode 2 (eigenvalue -1) is uncontrollable. We can only move eigenvalue 1 to -1. The eigenvalue -1 stays at -1 regardless of K. Desired poles [-1,-2] are NOT achievable."
        },
        "difficulty": "extreme",
        "rationale": "Pole placement fails for uncontrollable modes. The specialist should detect that the system is not fully controllable and report that only controllable pole locations can be changed. Placing the unstable pole at +1 to -1 is possible, but -2 is not achievable."
    },

    # =========================================================================
    # CATEGORY 8: OBSERVABILITY GRAMIAN CONDITIONING (Tests 036-040)
    # =========================================================================
    {
        "test_id": "CTRL_036",
        "category": "observability_gramian",
        "input": {
            "system": {
                "A": [[-1, 0], [0, -100]],
                "B": [[1], [1]],
                "C": [[1, 1]]
            },
            "task": "compute_observability_gramian"
        },
        "expected": {
            "observability_matrix_condition": "~100 (moderate)",
            "gramian_condition": "~10000 (severe)",
            "notes": "Fast mode (eigenvalue -100) is hard to observe from the sum output C=[1,1]. The observability Gramian W_o = integral(exp(A't) C'C exp(At)) will have condition number ~ (100/1)^2 = 10000."
        },
        "difficulty": "brutal",
        "rationale": "When eigenvalues are widely separated, the observability Gramian becomes ill-conditioned. The fast mode decays quickly, making it hard to observe. The specialist must compute the Gramian via Lyapunov equation and handle the conditioning."
    },
    {
        "test_id": "CTRL_037",
        "category": "observability_gramian",
        "input": {
            "system": {
                "A": [[-1, 0], [0, -1.001]],
                "B": [[1], [1]],
                "C": [[1, -1]]
            },
            "task": "compute_observability_gramian"
        },
        "expected": {
            "observability_matrix_rank": 2,
            "notes": "Nearly repeated eigenvalues (-1 and -1.001) with C measuring their DIFFERENCE. Observable but nearly unobservable. The observability matrix is [[1,-1], [-1, 1.001]] - nearly rank deficient."
        },
        "difficulty": "extreme",
        "rationale": "When eigenvalues are nearly equal and C measures a near-null direction, the observability Gramian is nearly singular. The specialist must detect this near-unobservability and report the conditioning issue."
    },
    {
        "test_id": "CTRL_038",
        "category": "observability_gramian",
        "input": {
            "system": {
                "A": [[-0.001, 0], [0, -1000]],
                "B": [[1], [1]],
                "C": [[1, 0]]
            },
            "task": "compute_observability_gramian"
        },
        "expected": {
            "notes": "Extreme timescale separation: 6 orders of magnitude between eigenvalues. C observes only slow mode directly. Fast mode is observable through A but Gramian condition number is ~ 10^12."
        },
        "difficulty": "pathological",
        "rationale": "Eigenvalue ratio of 10^6 creates a Gramian condition number of 10^12. The Lyapunov solver for the Gramian will fail due to numerical issues. The specialist must recognize this as a pathological case."
    },
    {
        "test_id": "CTRL_039",
        "category": "observability_gramian",
        "input": {
            "system": {
                "A": [[0, 1], [-1, 0]],
                "B": [[0], [1]],
                "C": [[1, 0]]
            },
            "task": "compute_observability_gramian"
        },
        "expected": {
            "notes": "Marginally stable system (eigenvalues +/- i). The observability Gramian integral diverges because exp(At) does not decay. Gramian is UNDEFINED for non-asymptotically-stable systems."
        },
        "difficulty": "extreme",
        "rationale": "The observability Gramian integral requires A to be stable. For marginally stable systems (eigenvalues on imaginary axis), the integral diverges. The specialist must detect this and report that the Gramian does not exist."
    },
    {
        "test_id": "CTRL_040",
        "category": "observability_gramian",
        "input": {
            "system": {
                "A": [[-1, 1e6], [0, -2]],
                "B": [[0], [1]],
                "C": [[1, 0]]
            },
            "task": "compute_observability_gramian"
        },
        "expected": {
            "notes": "Highly non-normal A with large off-diagonal. Observable but the Gramian reflects the non-normality. The 1e6 coupling means fast mode affects slow observation significantly. Gramian elements will span many orders of magnitude."
        },
        "difficulty": "extreme",
        "rationale": "Non-normal A matrices have Gramians that do not simply depend on eigenvalues. The large off-diagonal coupling creates numerical challenges in the Lyapunov solver. The specialist must handle the wide range of matrix entries."
    },

    # =========================================================================
    # CATEGORY 9: PHASE PORTRAITS WITH HOMOCLINIC ORBITS (Tests 041-045)
    # =========================================================================
    {
        "test_id": "CTRL_041",
        "category": "homoclinic_orbits",
        "input": {
            "system": "Duffing oscillator: dx/dt = y, dy/dt = x - x^3",
            "vector_field": "lambda X: np.array([X[1], X[0] - X[0]**3])",
            "task": "find_homoclinic_orbits"
        },
        "expected": {
            "saddle_point": "[0, 0]",
            "homoclinic_orbit": "figure-8 shaped orbit connecting origin to itself",
            "notes": "The origin is a saddle (eigenvalues +/- 1). Homoclinic orbits connect the saddle to itself. Energy level H = y^2/2 - x^2/2 + x^4/4 = 0 gives the homoclinic."
        },
        "difficulty": "brutal",
        "rationale": "Finding homoclinic orbits requires integrating backward and forward in time from the saddle point along its stable/unstable manifolds. Standard trajectory integration will miss these special orbits. The specialist must compute manifolds explicitly."
    },
    {
        "test_id": "CTRL_042",
        "category": "homoclinic_orbits",
        "input": {
            "system": "Pendulum: dx/dt = y, dy/dt = -sin(x)",
            "vector_field": "lambda X: np.array([X[1], -np.sin(X[0])])",
            "task": "find_separatrix"
        },
        "expected": {
            "saddle_points": "[+/- pi, 0], [+/- 3pi, 0], ...",
            "heteroclinic_orbits": "orbits connecting adjacent saddles",
            "notes": "The separatrix is the energy level H = y^2/2 - cos(x) = 1. It connects neighboring saddle points at x = +/- pi. This is heteroclinic, not homoclinic."
        },
        "difficulty": "extreme",
        "rationale": "The pendulum's separatrix is a heteroclinic orbit connecting different saddle points. The specialist must distinguish heteroclinic from homoclinic and identify the separatrix as the boundary between oscillation and rotation."
    },
    {
        "test_id": "CTRL_043",
        "category": "homoclinic_orbits",
        "input": {
            "system": "Perturbed Duffing: dx/dt = y, dy/dt = x - x^3 - 0.1*y + 0.2*cos(t)",
            "vector_field": "NON-AUTONOMOUS (time-dependent)",
            "task": "detect_homoclinic_tangles"
        },
        "expected": {
            "notes": "Time-dependent perturbation breaks the homoclinic orbit into transverse intersections of stable and unstable manifolds. This creates a homoclinic tangle - signature of chaos. Melnikov analysis gives condition for tangle."
        },
        "difficulty": "pathological",
        "rationale": "Non-autonomous systems with periodic forcing can break homoclinic orbits into homoclinic tangles - the hallmark of chaos. The specialist cannot handle non-autonomous systems directly and would need Poincare section analysis."
    },
    {
        "test_id": "CTRL_044",
        "category": "homoclinic_orbits",
        "input": {
            "system": "Lorenz at rho = 13.926... (homoclinic explosion)",
            "vector_field": "lambda X: np.array([10*(X[1]-X[0]), X[0]*(13.926-X[2])-X[1], X[0]*X[1]-8/3*X[2]])",
            "task": "detect_homoclinic_orbit"
        },
        "expected": {
            "notes": "At rho ~ 13.926, the Lorenz system has a homoclinic orbit to the origin. Just above this value, the homoclinic explodes into a strange attractor. This is the onset of chaos via homoclinic bifurcation."
        },
        "difficulty": "pathological",
        "rationale": "The Lorenz system at the homoclinic bifurcation point has an orbit that asymptotically approaches the origin both forward and backward in time. Finding this exact parameter value and orbit is extremely sensitive to numerical precision."
    },
    {
        "test_id": "CTRL_045",
        "category": "homoclinic_orbits",
        "input": {
            "system": "Shilnikov spiral: dx/dt = y, dy/dt = z, dz/dt = -z + y + x^2",
            "vector_field": "lambda X: np.array([X[1], X[2], -X[2] + X[1] + X[0]**2])",
            "task": "detect_shilnikov_chaos"
        },
        "expected": {
            "notes": "Shilnikov chaos occurs when a homoclinic orbit connects a saddle-focus to itself with eigenvalues satisfying |Re(complex)| < |real|. This creates infinitely many horseshoes and chaotic dynamics."
        },
        "difficulty": "pathological",
        "rationale": "Shilnikov chaos is a 3D phenomenon requiring a homoclinic orbit to a saddle-focus fixed point. The specialist would need to find the homoclinic orbit and verify the Shilnikov condition on eigenvalues. This is research-level analysis."
    },

    # =========================================================================
    # CATEGORY 10: NON-MINIMUM PHASE AND RHP ZEROS (Tests 046-050)
    # =========================================================================
    {
        "test_id": "CTRL_046",
        "category": "rhp_zeros",
        "input": {
            "system": {
                "A": [[0, 1], [-2, -3]],
                "B": [[0], [1]],
                "C": [[1, -1]],
                "D": [[0]]
            },
            "task": "compute_zeros"
        },
        "expected": {
            "zeros": "[2] (in RHP)",
            "is_minimum_phase": False,
            "notes": "Transfer function has a zero at s=2 (right half plane). Non-minimum phase systems have fundamental limitations: inverse response, bandwidth limits, cannot be perfectly tracked."
        },
        "difficulty": "brutal",
        "rationale": "RHP zeros cause fundamental control limitations. The specialist must compute transmission zeros from the state-space realization and identify their location relative to the imaginary axis. The zero at s=2 limits achievable bandwidth."
    },
    {
        "test_id": "CTRL_047",
        "category": "rhp_zeros",
        "input": {
            "system": {
                "A": [[-1, 0], [0, -2]],
                "B": [[1], [1]],
                "C": [[1, -2]],
                "D": [[0]]
            },
            "task": "compute_zeros_and_limitations"
        },
        "expected": {
            "zeros": "s = -3 (in LHP, minimum phase)",
            "notes": "Despite C = [1,-2] mixing modes differently, the zero is at s=-3 (stable). This is minimum phase. But the zero close to poles (-1,-2) still limits bandwidth."
        },
        "difficulty": "brutal",
        "rationale": "Computing transmission zeros requires finding s where [sI-A, -B; C, D] drops rank. The specialist must implement this calculation correctly. The zero at -3 is between the poles, which is still a performance limitation even though stable."
    },
    {
        "test_id": "CTRL_048",
        "category": "rhp_zeros",
        "input": {
            "system": {
                "A": [[-1]],
                "B": [[1]],
                "C": [[1]],
                "D": [[-0.5]]
            },
            "task": "compute_zeros"
        },
        "expected": {
            "zeros": "[2] (RHP, from D feedthrough)",
            "notes": "Non-minimum phase due to D term. Transfer function is (s-2)/(s+1). The D=-0.5 creates the RHP zero. System cannot track step inputs perfectly due to inverse response."
        },
        "difficulty": "extreme",
        "rationale": "When D is nonzero, zeros can appear that are not from the A,B,C matrices alone. The specialist must include D in the zero computation. The transfer function is C(sI-A)^(-1)B + D = 1/(s+1) - 0.5 = (1-0.5(s+1))/(s+1) = (0.5-0.5s)/(s+1) = -0.5(s-2)/(s+1)."
    },
    {
        "test_id": "CTRL_049",
        "category": "rhp_zeros",
        "input": {
            "system": {
                "A": [[0, 1, 0], [0, 0, 1], [-1, -3, -3]],
                "B": [[0], [0], [1]],
                "C": [[1, 0, -1]],
                "D": [[0]]
            },
            "task": "compute_zeros_and_pole_zero_cancellation"
        },
        "expected": {
            "poles": "[-1, -1, -1] (triple pole)",
            "zeros": "compute from Rosenbrock system matrix",
            "notes": "Triple pole at -1. The zeros depend on C choice. If a zero equals a pole, there is pole-zero cancellation reducing the system order. This affects controllability/observability of that mode."
        },
        "difficulty": "extreme",
        "rationale": "Pole-zero cancellation indicates uncontrollable or unobservable modes. The specialist must compute both poles and zeros, identify any matches, and relate cancellations to the controllability/observability defects."
    },
    {
        "test_id": "CTRL_050",
        "category": "rhp_zeros",
        "input": {
            "system": {
                "A": [[0, 1], [1, 0]],
                "B": [[0], [1]],
                "C": [[1, 0]],
                "D": [[0]]
            },
            "Q": [[1, 0], [0, 1]],
            "R": [[1]],
            "task": "lqr_with_rhp_zero"
        },
        "expected": {
            "open_loop_poles": "[1, -1] (one unstable)",
            "zeros": "[none visible from C,D]",
            "notes": "Unstable open-loop pole at +1. LQR will stabilize but the closed-loop bandwidth is limited by the unstable pole location. Minimum gain margin is constrained by RHP pole, not zero in this case."
        },
        "difficulty": "brutal",
        "rationale": "LQR with an unstable open-loop pole has guaranteed stability margins, but the closed-loop bandwidth and disturbance rejection are fundamentally limited. The specialist must correctly stabilize and report the closed-loop properties."
    }
]


def get_control_theory_stress_tests() -> List[Dict[str, Any]]:
    """Return the list of 50 brutal control theory stress tests."""
    return CONTROL_THEORY_STRESS_TESTS


def print_test_summary():
    """Print summary statistics of the test suite."""
    tests = get_control_theory_stress_tests()

    print("=" * 70)
    print("CONTROL THEORY STRESS TEST SUITE - SUMMARY")
    print("=" * 70)
    print(f"\nTotal tests: {len(tests)}")

    # Count by category
    categories = {}
    for t in tests:
        cat = t["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\nTests by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    # Count by difficulty
    difficulties = {}
    for t in tests:
        diff = t["difficulty"]
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print("\nTests by difficulty:")
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    print_test_summary()

    print("\nFirst 5 tests preview:")
    print("-" * 70)
    for test in CONTROL_THEORY_STRESS_TESTS[:5]:
        print(f"\n{test['test_id']}: {test['category']}")
        print(f"  Difficulty: {test['difficulty']}")
        print(f"  Rationale: {test['rationale'][:100]}...")
