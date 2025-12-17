"""
BRUTAL Research-Level Stress Tests for Differential Geometry & Topology

50 pathological test cases designed to BREAK the DifferentialGeometrySpecialist
and TopologySpecialist agents.

Categories covered:
- Christoffel symbols at coordinate singularities
- Riemann curvature tensor for metrics with discontinuities
- Geodesics through conjugate points
- Parallel transport around closed loops with holonomy
- Homology computation of Klein bottle, projective spaces
- Simplicial complexes with thousands of simplices
- Betti numbers of high-dimensional manifolds
- Euler characteristic of non-orientable surfaces
- Gaussian curvature at umbilical points
- Geodesic deviation in highly curved spaces

Each test is designed to expose fundamental limitations in numerical
differential geometry and computational topology implementations.
"""

import numpy as np
from typing import Dict, Any, List, Callable


# =============================================================================
# DIFFERENTIAL GEOMETRY STRESS TESTS (DIFF_001 - DIFF_030)
# =============================================================================

DIFFERENTIAL_GEOMETRY_TESTS: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # CHRISTOFFEL SYMBOLS AT COORDINATE SINGULARITIES (DIFF_001 - DIFF_006)
    # --------------------------------------------------------------------------
    {
        "test_id": "DIFF_001",
        "category": "christoffel_singularity",
        "input": {
            "description": "Christoffel symbols at r=0 for polar coordinates",
            "metric_type": "polar",
            "metric_formula": "ds^2 = dr^2 + r^2 dphi^2",
            "point": [0.0, 0.0],  # r=0 is singular
            "coordinate_system": "polar (r, phi)",
        },
        "expected": "Gamma^phi_r_phi = 1/r diverges at r=0; Gamma^r_phi_phi = -r vanishes",
        "difficulty": "brutal",
        "rationale": "The polar metric has g_22 = r^2, making the metric degenerate (det=0) "
                    "at the origin. Christoffel symbols Gamma^2_12 = 1/r blow up. "
                    "Any numerical scheme using finite differences will produce NaN/Inf "
                    "or catastrophic cancellation near r=0."
    },
    {
        "test_id": "DIFF_002",
        "category": "christoffel_singularity",
        "input": {
            "description": "Christoffel symbols at theta=0,pi for sphere",
            "metric_type": "sphere",
            "metric_formula": "ds^2 = R^2(dtheta^2 + sin^2(theta) dphi^2)",
            "point": [0.0, 0.0],  # North pole: theta=0
            "coordinate_system": "spherical (theta, phi)",
        },
        "expected": "Gamma^phi_theta_phi = cot(theta) diverges at poles; metric singular",
        "difficulty": "brutal",
        "rationale": "Spherical coordinates have coordinate singularities at poles where "
                    "sin(theta)=0. The inverse metric g^{phi phi} = 1/(R^2 sin^2 theta) "
                    "blows up, and Christoffel symbols involving phi become undefined. "
                    "This tests handling of metric degeneracy in 2D Riemannian geometry."
    },
    {
        "test_id": "DIFF_003",
        "category": "christoffel_singularity",
        "input": {
            "description": "Schwarzschild metric at event horizon r=2M",
            "metric_type": "schwarzschild",
            "metric_formula": "ds^2 = -(1-2M/r)dt^2 + (1-2M/r)^{-1}dr^2 + r^2 dOmega^2",
            "point": [2.0, 0.0],  # r=2M for M=1 (event horizon)
            "M": 1.0,
            "coordinate_system": "Schwarzschild (t, r)",
        },
        "expected": "Coordinate singularity at r=2M; Christoffel symbols finite in "
                   "Eddington-Finkelstein coordinates but infinite in Schwarzschild",
        "difficulty": "extreme",
        "rationale": "The Schwarzschild event horizon is a coordinate singularity where "
                    "g_tt->0 and g_rr->inf. However, this is NOT a curvature singularity - "
                    "the Riemann tensor is perfectly finite. Tests whether the system "
                    "distinguishes coordinate artifacts from true geometric singularities."
    },
    {
        "test_id": "DIFF_004",
        "category": "christoffel_singularity",
        "input": {
            "description": "Metric with removable singularity",
            "metric_type": "custom_removable",
            "metric_formula": "g = [[sin(x)^2/x^2, 0], [0, 1]] at x=0",
            "point": [0.0, 0.0],
            "coordinate_system": "cartesian",
        },
        "expected": "Limit at x=0 gives g_11 = 1 (removable); Christoffel requires L'Hopital",
        "difficulty": "extreme",
        "rationale": "The metric component sin(x)^2/x^2 -> 1 as x->0, but derivatives "
                    "involve quotient rule with 0/0 forms. Computing Christoffel symbols "
                    "at x=0 requires analytic continuation or sophisticated limiting "
                    "procedures that pure numerical differentiation cannot handle."
    },
    {
        "test_id": "DIFF_005",
        "category": "christoffel_singularity",
        "input": {
            "description": "Conical singularity metric",
            "metric_type": "cone",
            "metric_formula": "ds^2 = dr^2 + (alpha*r)^2 dphi^2, alpha != 1",
            "point": [0.0, 0.0],  # Cone apex
            "alpha": 0.5,  # Deficit angle
            "coordinate_system": "polar-like",
        },
        "expected": "Curvature concentrated as delta-function at apex; Christoffel "
                   "symbols behave like 1/r but integrated curvature gives deficit angle",
        "difficulty": "pathological",
        "rationale": "A cone is flat everywhere except at the apex where curvature is "
                    "distributional (delta function). Standard tensor calculus fails; "
                    "requires Regge calculus or distributional geometry. Tests whether "
                    "the system recognizes non-smooth curvature concentration."
    },
    {
        "test_id": "DIFF_006",
        "category": "christoffel_singularity",
        "input": {
            "description": "Eguchi-Hanson metric near NUT singularity",
            "metric_type": "eguchi_hanson",
            "metric_formula": "Asymptotically locally flat 4D metric with NUT charge",
            "point": [1e-10, 0.0, 0.0, 0.0],  # Near r=a
            "coordinate_system": "Eguchi-Hanson (r, theta, phi, psi)",
        },
        "expected": "Apparent singularity at r=a is removable if period of psi is correct",
        "difficulty": "pathological",
        "rationale": "The Eguchi-Hanson metric is a non-trivial gravitational instanton "
                    "that appears singular at r=a but is actually smooth if the angular "
                    "coordinate psi has period 2pi. Tests understanding of topological "
                    "restrictions on coordinate ranges for regularity."
    },

    # --------------------------------------------------------------------------
    # RIEMANN CURVATURE WITH DISCONTINUITIES (DIFF_007 - DIFF_012)
    # --------------------------------------------------------------------------
    {
        "test_id": "DIFF_007",
        "category": "riemann_discontinuity",
        "input": {
            "description": "Metric with step-function discontinuity",
            "metric_type": "step_discontinuous",
            "metric_formula": "g = [[1, 0], [0, 1 + Heaviside(x)]]",
            "point": [0.0, 0.0],  # At discontinuity
            "coordinate_system": "cartesian",
        },
        "expected": "Riemann tensor contains Dirac delta; curvature is distributional",
        "difficulty": "pathological",
        "rationale": "A discontinuous metric has distributional second derivatives, "
                    "making Christoffel symbols discontinuous and Riemann tensor "
                    "containing delta functions. This is the mathematical model of "
                    "junction conditions in general relativity (Israel formalism)."
    },
    {
        "test_id": "DIFF_008",
        "category": "riemann_discontinuity",
        "input": {
            "description": "Metric interpolating between Euclidean and hyperbolic",
            "metric_type": "transitional",
            "metric_formula": "g = [[1/y^(2*tanh(x)), 0], [0, 1/y^(2*tanh(x))]]",
            "point": [0.0, 1.0],  # Transition region
            "coordinate_system": "half-plane",
        },
        "expected": "Curvature smoothly transitions from 0 to -1",
        "difficulty": "extreme",
        "rationale": "This metric smoothly interpolates between Euclidean (x<<0) and "
                    "Poincare hyperbolic (x>>0) geometry. Computing curvature requires "
                    "careful handling of the tanh transition and derivatives of "
                    "y^(2*tanh(x)) which involves both power and exponential rules."
    },
    {
        "test_id": "DIFF_009",
        "category": "riemann_discontinuity",
        "input": {
            "description": "Metric with C^0 but not C^1 connection",
            "metric_type": "cusped",
            "metric_formula": "g = [[(1+|x|)^2, 0], [0, 1]]",
            "point": [0.0, 0.0],  # Cusp at x=0
            "coordinate_system": "cartesian",
        },
        "expected": "Metric continuous but not differentiable at x=0; Christoffel "
                   "symbols have jump discontinuity; Riemann has delta contribution",
        "difficulty": "extreme",
        "rationale": "The absolute value creates a cusp where left and right derivatives "
                    "differ. This models a 'fold' in the manifold and tests handling "
                    "of one-sided derivatives in differential geometry."
    },
    {
        "test_id": "DIFF_010",
        "category": "riemann_discontinuity",
        "input": {
            "description": "Wheeler-DeWitt superspace metric near classical singularity",
            "metric_type": "minisuperspace",
            "metric_formula": "G_ab = diag(-a, a^3, a^3) on (a, beta+, beta-)",
            "point": [1e-8, 0.0, 0.0],  # Near a=0 (big bang)
            "coordinate_system": "Misner (a, beta+, beta-)",
        },
        "expected": "Supermetric degenerates at a=0; DeWitt metric has essential singularity",
        "difficulty": "pathological",
        "rationale": "The DeWitt superspace metric on the space of 3-geometries "
                    "degenerates at the big bang a=0. This is a configuration-space "
                    "singularity in quantum cosmology that tests geometric reasoning "
                    "in infinite-dimensional settings reduced to minisuperspace."
    },
    {
        "test_id": "DIFF_011",
        "category": "riemann_discontinuity",
        "input": {
            "description": "Metric with oscillatory singularity",
            "metric_type": "oscillatory",
            "metric_formula": "g = [[1 + sin(1/x)/x, 0], [0, 1]]",
            "point": [1e-6, 0.0],  # Near essential singularity
            "coordinate_system": "cartesian",
        },
        "expected": "Oscillation frequency -> infinity as x->0; curvature oscillates unboundedly",
        "difficulty": "pathological",
        "rationale": "The sin(1/x)/x term creates infinitely many oscillations near x=0, "
                    "making numerical derivatives completely unreliable. This is an "
                    "essential singularity of the metric function itself."
    },
    {
        "test_id": "DIFF_012",
        "category": "riemann_discontinuity",
        "input": {
            "description": "Metric constructed from Weierstrass nowhere-differentiable function",
            "metric_type": "weierstrass",
            "metric_formula": "g_11 = 1 + W(x) where W is Weierstrass function",
            "point": [0.5, 0.0],
            "coordinate_system": "cartesian",
        },
        "expected": "Christoffel symbols undefined everywhere; pathological geometry",
        "difficulty": "pathological",
        "rationale": "The Weierstrass function is continuous but nowhere differentiable. "
                    "A metric involving it has no classical Christoffel symbols - this "
                    "represents the absolute limit of differential geometry's applicability."
    },

    # --------------------------------------------------------------------------
    # GEODESICS THROUGH CONJUGATE POINTS (DIFF_013 - DIFF_018)
    # --------------------------------------------------------------------------
    {
        "test_id": "DIFF_013",
        "category": "geodesic_conjugate",
        "input": {
            "description": "Great circle geodesic through antipodal points on sphere",
            "metric_type": "sphere",
            "initial_point": [0.0, 0.0],  # North pole
            "initial_velocity": [1.0, 0.0],  # Southward along meridian
            "t_max": np.pi + 0.1,  # Past conjugate point (south pole)
            "R": 1.0,
        },
        "expected": "Geodesic reaches south pole (conjugate point) at t=pi; "
                   "Jacobi field vanishes; geodesic not minimizing beyond",
        "difficulty": "brutal",
        "rationale": "On a sphere, antipodal points are conjugate - there are infinitely "
                    "many geodesics connecting them. Past the conjugate point, geodesics "
                    "cease to be length-minimizing. Tests detection of conjugate points "
                    "via Jacobi fields and geodesic stability analysis."
    },
    {
        "test_id": "DIFF_014",
        "category": "geodesic_conjugate",
        "input": {
            "description": "Geodesic on ellipsoid through umbilical point",
            "metric_type": "ellipsoid",
            "semi_axes": [1.0, 1.0, 2.0],  # Prolate spheroid
            "initial_point": [0.0, 0.0],  # On equator
            "initial_velocity": [1.0, 0.5],
            "t_max": 10.0,
        },
        "expected": "Geodesic may or may not reach conjugate point depending on direction; "
                   "umbilical points have isotropic curvature",
        "difficulty": "extreme",
        "rationale": "Ellipsoid geodesics are integrable (Jacobi's solution) but the "
                    "location of conjugate points depends on initial direction. Umbilical "
                    "points where principal curvatures coincide have special behavior."
    },
    {
        "test_id": "DIFF_015",
        "category": "geodesic_conjugate",
        "input": {
            "description": "Geodesic in de Sitter space approaching horizon",
            "metric_type": "de_sitter",
            "metric_formula": "ds^2 = -(1-r^2/R^2)dt^2 + (1-r^2/R^2)^{-1}dr^2 + r^2 dOmega^2",
            "initial_point": [0.0, 0.5],  # Inside cosmological horizon
            "initial_velocity": [1.0, 0.1],  # Nearly radial outward
            "R": 1.0,  # de Sitter radius
            "t_max": 5.0,
        },
        "expected": "Timelike geodesic never reaches r=R; null geodesics reach in "
                   "infinite affine parameter; conjugate point structure differs from sphere",
        "difficulty": "extreme",
        "rationale": "de Sitter space has cosmological horizons that behave differently "
                    "from black hole horizons. The conjugate point structure is non-trivial "
                    "and depends on the geodesic type (timelike/null/spacelike)."
    },
    {
        "test_id": "DIFF_016",
        "category": "geodesic_conjugate",
        "input": {
            "description": "Geodesic spray near focal point in lens space",
            "metric_type": "lens_space",
            "metric_formula": "L(p,q) quotient of S^3",
            "p": 7,
            "q": 2,
            "initial_point": [0.0, 0.0, 0.0],
            "t_max": 2*np.pi/7,  # First focal time
        },
        "expected": "Multiple conjugate points at t = 2*pi*k/p; topology affects geodesic flow",
        "difficulty": "pathological",
        "rationale": "Lens spaces L(p,q) are quotients of S^3 with non-trivial fundamental "
                    "group. Geodesic flow reflects the quotient structure, creating conjugate "
                    "points at specific rational multiples of pi determined by p and q."
    },
    {
        "test_id": "DIFF_017",
        "category": "geodesic_conjugate",
        "input": {
            "description": "Geodesic in negatively curved space (no conjugate points)",
            "metric_type": "hyperbolic",
            "initial_point": [0.0, 1.0],  # In Poincare half-plane
            "initial_velocity": [1.0, 0.0],  # Horizontal
            "t_max": 100.0,  # Long integration time
        },
        "expected": "Cartan-Hadamard theorem: no conjugate points in complete simply-connected "
                   "negative curvature; geodesics diverge exponentially",
        "difficulty": "brutal",
        "rationale": "Hyperbolic space has no conjugate points by Cartan-Hadamard theorem. "
                    "However, numerical integration over long times in exponentially diverging "
                    "flows leads to massive numerical errors, testing integrator stability."
    },
    {
        "test_id": "DIFF_018",
        "category": "geodesic_conjugate",
        "input": {
            "description": "Geodesic near caustic in gravitational lensing",
            "metric_type": "schwarzschild_weak_field",
            "metric_formula": "Linearized Schwarzschild for light deflection",
            "source_position": [0.0, 10.0],  # Far from lens
            "lens_mass": 1.0,
            "impact_parameters": [2.1, 2.5, 3.0],  # Near Einstein radius
        },
        "expected": "Multiple images form; caustic structure at critical curves; "
                   "magnification diverges at caustics (conjugate points)",
        "difficulty": "extreme",
        "rationale": "Gravitational lensing creates caustics where multiple light rays "
                    "converge - these are conjugate points of the null geodesic congruence. "
                    "Tests geometric optics in curved spacetime."
    },

    # --------------------------------------------------------------------------
    # PARALLEL TRANSPORT AND HOLONOMY (DIFF_019 - DIFF_024)
    # --------------------------------------------------------------------------
    {
        "test_id": "DIFF_019",
        "category": "parallel_transport_holonomy",
        "input": {
            "description": "Parallel transport around equator of sphere",
            "metric_type": "sphere",
            "initial_vector": [1.0, 0.0],  # Tangent to equator
            "loop_path": "equator",  # Closed loop
            "R": 1.0,
        },
        "expected": "Vector rotates by angle equal to solid angle enclosed (2*pi for hemisphere) "
                   "= 2*pi; holonomy group is SO(2)",
        "difficulty": "brutal",
        "rationale": "The holonomy around the equator equals the Gaussian curvature times "
                    "enclosed area (Gauss-Bonnet). For hemisphere: K=1, A=2*pi, so rotation "
                    "is 2*pi (returns to original). Tests Ambrose-Singer theorem."
    },
    {
        "test_id": "DIFF_020",
        "category": "parallel_transport_holonomy",
        "input": {
            "description": "Parallel transport around closed loop in Kerr spacetime",
            "metric_type": "kerr",
            "mass": 1.0,
            "spin": 0.9,  # Near extremal
            "initial_vector": [1.0, 0.0, 0.0, 0.0],
            "loop_path": "circular_orbit_equator",
            "radius": 6.0,  # ISCO region
        },
        "expected": "Frame-dragging causes additional rotation beyond geometric holonomy; "
                   "gravitomagnetic effect",
        "difficulty": "extreme",
        "rationale": "Kerr spacetime has gravitomagnetic effects that cause gyroscope "
                    "precession even in flat regions (Lense-Thirring effect). The holonomy "
                    "includes both curvature and frame-dragging contributions."
    },
    {
        "test_id": "DIFF_021",
        "category": "parallel_transport_holonomy",
        "input": {
            "description": "Holonomy of SU(2) connection on S^3 (Hopf fibration)",
            "metric_type": "hopf_bundle",
            "base_loop": "S^2_equator",
            "fiber": "S^1",
            "connection": "canonical",
        },
        "expected": "Holonomy in U(1) fiber over S^2 loop equals magnetic flux through loop; "
                   "Berry phase analog",
        "difficulty": "pathological",
        "rationale": "The Hopf fibration S^1 -> S^3 -> S^2 has non-trivial holonomy that "
                    "relates to Dirac monopoles and Berry phase in quantum mechanics. "
                    "Tests understanding of fiber bundle geometry beyond Riemannian setting."
    },
    {
        "test_id": "DIFF_022",
        "category": "parallel_transport_holonomy",
        "input": {
            "description": "Parallel transport around cone apex (concentrated curvature)",
            "metric_type": "cone",
            "alpha": 0.5,  # Deficit angle pi
            "initial_vector": [1.0, 0.0],
            "loop_radius": 0.001,  # Very small loop around apex
        },
        "expected": "Holonomy = 2*pi*(1-alpha) = pi for alpha=0.5; deficit angle captured "
                   "regardless of loop size",
        "difficulty": "brutal",
        "rationale": "A cone has zero curvature everywhere except at apex where curvature "
                    "is a delta function. Any loop encircling the apex picks up holonomy "
                    "equal to deficit angle, regardless of loop size. Tests distributional curvature."
    },
    {
        "test_id": "DIFF_023",
        "category": "parallel_transport_holonomy",
        "input": {
            "description": "Restricted holonomy of Calabi-Yau manifold",
            "metric_type": "calabi_yau",
            "complex_dimension": 3,
            "manifold": "quintic_3fold",
        },
        "expected": "Holonomy is SU(3), not full SO(6); parallel spinors exist",
        "difficulty": "pathological",
        "rationale": "Calabi-Yau manifolds have restricted holonomy SU(n) instead of SO(2n), "
                    "implying parallel spinors and Ricci-flatness. This is fundamental to "
                    "string theory compactifications. Tests recognition of special holonomy."
    },
    {
        "test_id": "DIFF_024",
        "category": "parallel_transport_holonomy",
        "input": {
            "description": "Parallel transport in pp-wave spacetime",
            "metric_type": "pp_wave",
            "metric_formula": "ds^2 = 2dudv + H(u,x,y)(du)^2 + dx^2 + dy^2",
            "H_function": "x^2 - y^2",  # Quadrupole wave
            "initial_vector": [0.0, 1.0, 0.0, 0.0],
            "path": "u_line",  # Along wave direction
        },
        "expected": "Transverse vectors undergo shearing but not rotation; holonomy is "
                   "nilpotent (Heisenberg group)",
        "difficulty": "extreme",
        "rationale": "pp-wave spacetimes have nilpotent (non-abelian but solvable) holonomy "
                    "groups. They are exact solutions to Einstein's equations describing "
                    "gravitational waves. Tests non-compact holonomy groups."
    },

    # --------------------------------------------------------------------------
    # GAUSSIAN CURVATURE AND UMBILICAL POINTS (DIFF_025 - DIFF_030)
    # --------------------------------------------------------------------------
    {
        "test_id": "DIFF_025",
        "category": "gaussian_curvature_umbilical",
        "input": {
            "description": "Gaussian curvature of torus at inner/outer equator",
            "metric_type": "torus",
            "major_radius": 3.0,
            "minor_radius": 1.0,
            "points": [[np.pi/2, 0.0], [3*np.pi/2, 0.0]],  # Inner and outer
        },
        "expected": "K_outer = 1/(R*(R+r)) > 0; K_inner = -1/(R*(R-r)) < 0; "
                   "K changes sign at theta = pi/2, 3pi/2",
        "difficulty": "brutal",
        "rationale": "The torus has positive curvature on the outer equator and negative "
                    "on the inner. The Gauss-Bonnet theorem requires total curvature = 0, "
                    "verified by the integral. Tests sign changes of curvature."
    },
    {
        "test_id": "DIFF_026",
        "category": "gaussian_curvature_umbilical",
        "input": {
            "description": "Gaussian curvature at saddle point (monkey saddle)",
            "surface_type": "monkey_saddle",
            "parametrization": "z = Re(x + iy)^3 = x^3 - 3xy^2",
            "point": [0.0, 0.0],  # The triple saddle point
        },
        "expected": "K = 0 at origin (flat point); principal curvatures both zero; "
                   "third-order umbilical point",
        "difficulty": "extreme",
        "rationale": "The monkey saddle has a degenerate (third-order) umbilical point where "
                    "both principal curvatures vanish. This creates a flat point that is "
                    "NOT planar - the surface curves in a special way. Tests degenerate cases."
    },
    {
        "test_id": "DIFF_027",
        "category": "gaussian_curvature_umbilical",
        "input": {
            "description": "Umbilical points of ellipsoid",
            "surface_type": "ellipsoid",
            "semi_axes": [1.0, 2.0, 3.0],  # a < b < c
            "find": "all_umbilical_points",
        },
        "expected": "Four umbilical points at (0, +/-b*sqrt(1-a^2/c^2), +/-c*sqrt(1-a^2/b^2)); "
                   "principal curvatures equal",
        "difficulty": "extreme",
        "rationale": "A generic ellipsoid has exactly 4 umbilical points where principal "
                    "curvatures coincide. Their location depends non-trivially on the axes. "
                    "Tests surface classification and special point detection."
    },
    {
        "test_id": "DIFF_028",
        "category": "gaussian_curvature_umbilical",
        "input": {
            "description": "Gaussian curvature of minimal surface (catenoid)",
            "surface_type": "catenoid",
            "parametrization": "(cosh(v)*cos(u), cosh(v)*sin(u), v)",
            "point": [0.0, 0.0],  # At neck
        },
        "expected": "K = -1/cosh(v)^4 < 0 everywhere; K -> 0 as v -> +/-infinity; "
                   "mean curvature H = 0",
        "difficulty": "brutal",
        "rationale": "The catenoid is a minimal surface (H=0) with negative Gaussian curvature. "
                    "At the neck (v=0), K = -1 is minimum (most negative). Tests minimal "
                    "surface properties and relation between K and H."
    },
    {
        "test_id": "DIFF_029",
        "category": "gaussian_curvature_umbilical",
        "input": {
            "description": "Gaussian curvature near cusp (pinched sphere)",
            "surface_type": "pinched_sphere",
            "parametrization": "Standard sphere but with z -> z^3/|z|^2 near poles",
            "point": [0.0, 0.0, 1.0],  # Near pinch point
        },
        "expected": "Curvature diverges at pinch; surface is not C^2 at that point",
        "difficulty": "pathological",
        "rationale": "Pinching a sphere creates a cusp where the surface fails to be smooth. "
                    "Curvature is undefined or infinite at the pinch. Tests handling of "
                    "geometric singularities in surfaces."
    },
    {
        "test_id": "DIFF_030",
        "category": "gaussian_curvature_umbilical",
        "input": {
            "description": "Scalar curvature of 4D Einstein manifold",
            "metric_type": "fubini_study",
            "manifold": "CP^2",  # Complex projective plane
            "point": [1.0, 0.0, 0.0, 0.0],
        },
        "expected": "R = 24 (for unit radius); space is Einstein with R_ij = 6 g_ij",
        "difficulty": "pathological",
        "rationale": "CP^2 with the Fubini-Study metric is a 4D Einstein manifold (Ricci = const * g). "
                    "Computing scalar curvature requires full Riemann tensor in 4D, which has "
                    "20 independent components. Tests higher-dimensional computations."
    },
]


# =============================================================================
# TOPOLOGY STRESS TESTS (TOPO_001 - TOPO_020)
# =============================================================================

TOPOLOGY_TESTS: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # HOMOLOGY OF NON-TRIVIAL SPACES (TOPO_001 - TOPO_007)
    # --------------------------------------------------------------------------
    {
        "test_id": "TOPO_001",
        "category": "homology_computation",
        "input": {
            "description": "Homology of Klein bottle",
            "space": "klein_bottle",
            "coefficients": "Z",  # Integer coefficients
        },
        "expected": {
            "H_0": "Z",
            "H_1": "Z + Z/2Z",  # Has torsion!
            "H_2": "0",
            "euler_characteristic": 0,
            "betti_numbers": [1, 1, 0],  # b_1 counts free part only
            "torsion": {1: ["Z/2Z"]},
        },
        "difficulty": "brutal",
        "rationale": "The Klein bottle has torsion in H_1 (Z/2Z factor) which requires "
                    "computing Smith normal form of boundary matrices. Most implementations "
                    "only compute Betti numbers, missing the torsion information."
    },
    {
        "test_id": "TOPO_002",
        "category": "homology_computation",
        "input": {
            "description": "Homology of real projective plane RP^2",
            "space": "projective_plane",
            "coefficients": "Z",
        },
        "expected": {
            "H_0": "Z",
            "H_1": "Z/2Z",  # Pure torsion!
            "H_2": "0",
            "euler_characteristic": 1,
            "betti_numbers": [1, 0, 0],
            "torsion": {1: ["Z/2Z"]},
        },
        "difficulty": "brutal",
        "rationale": "RP^2 has H_1 = Z/2Z which is pure torsion. The Betti number b_1 = 0, "
                    "but H_1 is non-trivial. Tests whether torsion is computed correctly."
    },
    {
        "test_id": "TOPO_003",
        "category": "homology_computation",
        "input": {
            "description": "Homology of higher-dimensional projective space RP^4",
            "space": "RP^4",
            "coefficients": "Z",
        },
        "expected": {
            "H_0": "Z",
            "H_1": "Z/2Z",
            "H_2": "0",
            "H_3": "Z/2Z",
            "H_4": "0",
            "euler_characteristic": 1,
        },
        "difficulty": "extreme",
        "rationale": "RP^n has H_k = Z/2Z for odd k < n and 0 for even k > 0. Computing "
                    "this requires a triangulation with many simplices and large boundary matrices."
    },
    {
        "test_id": "TOPO_004",
        "category": "homology_computation",
        "input": {
            "description": "Homology of 3-torus T^3",
            "space": "3_torus",
            "coefficients": "Z",
        },
        "expected": {
            "H_0": "Z",
            "H_1": "Z^3",
            "H_2": "Z^3",
            "H_3": "Z",
            "euler_characteristic": 0,
            "betti_numbers": [1, 3, 3, 1],
        },
        "difficulty": "extreme",
        "rationale": "T^3 = S^1 x S^1 x S^1 has Betti numbers following the binomial coefficients "
                    "(Kunneth formula). Triangulating T^3 and computing 3D homology is expensive."
    },
    {
        "test_id": "TOPO_005",
        "category": "homology_computation",
        "input": {
            "description": "Homology of lens space L(7,2)",
            "space": "lens_space",
            "p": 7,
            "q": 2,
            "coefficients": "Z",
        },
        "expected": {
            "H_0": "Z",
            "H_1": "Z/7Z",  # Cyclic group of order p
            "H_2": "0",
            "H_3": "Z",
            "fundamental_group": "Z/7Z",
        },
        "difficulty": "pathological",
        "rationale": "Lens spaces L(p,q) are quotients of S^3 with pi_1 = Z/pZ. Different q values "
                    "give homeomorphic but not diffeomorphic manifolds. Tests 3-manifold topology."
    },
    {
        "test_id": "TOPO_006",
        "category": "homology_computation",
        "input": {
            "description": "Homology of orientable surface of genus g=10",
            "space": "surface_genus_g",
            "genus": 10,
            "coefficients": "Z",
        },
        "expected": {
            "H_0": "Z",
            "H_1": "Z^20",  # 2g generators
            "H_2": "Z",
            "euler_characteristic": -18,  # 2 - 2g
            "betti_numbers": [1, 20, 1],
        },
        "difficulty": "brutal",
        "rationale": "High-genus surfaces require large triangulations. A genus-10 surface needs "
                    "at least 60 triangles (10*6) and computing H_1 rank requires SVD of a "
                    "large boundary matrix."
    },
    {
        "test_id": "TOPO_007",
        "category": "homology_computation",
        "input": {
            "description": "Homology of wedge sum of spheres",
            "space": "wedge_sum",
            "components": ["S^2", "S^2", "S^3", "S^3", "S^3"],
        },
        "expected": {
            "H_0": "Z",
            "H_1": "0",
            "H_2": "Z^2",
            "H_3": "Z^3",
            "euler_characteristic": 2,  # wedge: 1 + sum(chi_i - 1) = 1 + 2*(1) + 3*(-1) = 0... actually 2
        },
        "difficulty": "extreme",
        "rationale": "Wedge sums have homology that is direct sum of reduced homologies. "
                    "Tests understanding of how homology behaves under basic topological operations."
    },

    # --------------------------------------------------------------------------
    # LARGE SIMPLICIAL COMPLEXES (TOPO_008 - TOPO_012)
    # --------------------------------------------------------------------------
    {
        "test_id": "TOPO_008",
        "category": "large_complex",
        "input": {
            "description": "Homology of simplicial complex with 1000 triangles",
            "complex_type": "random_triangulation",
            "num_triangles": 1000,
            "genus_target": 5,  # Try to approximate genus-5 surface
        },
        "expected": {
            "approximate_euler_characteristic": -8,
            "computation_challenge": "1000x boundary matrices",
            "expected_H_1_rank": 10,  # 2g
        },
        "difficulty": "brutal",
        "rationale": "Computing homology of a 1000-triangle complex requires boundary matrices "
                    "of size ~1000x1000. Smith normal form is O(n^3) minimum, causing severe "
                    "computational bottleneck."
    },
    {
        "test_id": "TOPO_009",
        "category": "large_complex",
        "input": {
            "description": "Homology of complete graph K_10 clique complex",
            "complex_type": "clique_complex",
            "graph": "K_10",  # Complete graph on 10 vertices
        },
        "expected": {
            "f_vector": [10, 45, 120, 210, 252, 210, 120, 45, 10, 1],
            "euler_characteristic": 1,
            "is_contractible": True,  # Clique complex of K_n is (n-2)-simplex
            "all_betti_zero_above_0": True,
        },
        "difficulty": "extreme",
        "rationale": "The clique complex of K_10 is a 9-simplex with over 1000 faces. "
                    "While it's contractible (trivial homology), computing this requires "
                    "processing all 2^10 - 1 = 1023 simplices."
    },
    {
        "test_id": "TOPO_010",
        "category": "large_complex",
        "input": {
            "description": "Homology of 4-dimensional complex with 5000 simplices",
            "complex_type": "random_4d",
            "num_4_simplices": 500,
            "num_3_simplices": 2000,
            "num_2_simplices": 3000,
        },
        "expected": {
            "boundary_matrix_d4_size": "~2000 x 500",
            "computational_complexity": "O(n^3) for each boundary",
            "expected_runtime": "potentially hours",
        },
        "difficulty": "pathological",
        "rationale": "4D homology requires computing four boundary matrices and their ranks. "
                    "For thousands of simplices, this becomes computationally prohibitive "
                    "without specialized algorithms (persistent homology software)."
    },
    {
        "test_id": "TOPO_011",
        "category": "large_complex",
        "input": {
            "description": "Vietoris-Rips complex of point cloud",
            "complex_type": "vietoris_rips",
            "num_points": 500,
            "dimension_limit": 3,
            "epsilon": 0.5,
        },
        "expected": {
            "potentially_exponential_size": True,
            "num_simplices_bound": "O(n^d) = O(500^3) = O(10^8)",
            "requires_filtration": True,
        },
        "difficulty": "pathological",
        "rationale": "Vietoris-Rips complexes grow combinatorially with point count. "
                    "500 points can generate billions of simplices at dimension 3, "
                    "making naive homology computation infeasible."
    },
    {
        "test_id": "TOPO_012",
        "category": "large_complex",
        "input": {
            "description": "Cech complex of random point cloud in R^4",
            "complex_type": "cech",
            "num_points": 200,
            "ambient_dimension": 4,
            "epsilon": 1.0,
        },
        "expected": {
            "nerve_theorem_applies": True,
            "homotopy_type": "union of epsilon-balls",
            "computational_challenge": "requires convex hull computations in R^4",
        },
        "difficulty": "extreme",
        "rationale": "Cech complexes are the 'correct' construction for point-cloud topology "
                    "but require checking all k-tuples for common intersection. In R^4, "
                    "this is geometrically complex."
    },

    # --------------------------------------------------------------------------
    # BETTI NUMBERS OF HIGH-DIMENSIONAL MANIFOLDS (TOPO_013 - TOPO_016)
    # --------------------------------------------------------------------------
    {
        "test_id": "TOPO_013",
        "category": "high_dimensional_betti",
        "input": {
            "description": "Betti numbers of CP^3 (complex projective 3-space)",
            "manifold": "CP^3",
            "real_dimension": 6,
        },
        "expected": {
            "betti_numbers": [1, 0, 1, 0, 1, 0, 1],
            "euler_characteristic": 4,
            "cohomology_ring": "Z[x]/(x^4) where deg(x)=2",
        },
        "difficulty": "extreme",
        "rationale": "CP^n has non-trivial even-dimensional cohomology only. A 6-dimensional "
                    "triangulation would require huge numbers of simplices to compute directly."
    },
    {
        "test_id": "TOPO_014",
        "category": "high_dimensional_betti",
        "input": {
            "description": "Betti numbers of Grassmannian Gr(2,4)",
            "manifold": "Gr(2,4)",
            "real_dimension": 8,  # 2*(4-2) complex = 8 real
        },
        "expected": {
            "betti_numbers": [1, 0, 1, 0, 2, 0, 1, 0, 1],
            "euler_characteristic": 6,
            "schubert_cells": ["1", "sigma_1", "sigma_2", "sigma_11", "sigma_21", "sigma_22"],
        },
        "difficulty": "pathological",
        "rationale": "Grassmannians have rich topology computed via Schubert calculus. "
                    "Direct simplicial computation in 8 dimensions is impractical."
    },
    {
        "test_id": "TOPO_015",
        "category": "high_dimensional_betti",
        "input": {
            "description": "Betti numbers of 5-sphere S^5",
            "manifold": "S^5",
            "triangulation": "minimal",
        },
        "expected": {
            "betti_numbers": [1, 0, 0, 0, 0, 1],
            "euler_characteristic": 2,
            "minimal_triangulation_vertices": 7,  # n+2 for n-sphere
            "num_5_simplices": 7,
        },
        "difficulty": "brutal",
        "rationale": "The minimal triangulation of S^5 has 7 vertices but boundary matrices "
                    "still grow factorially with dimension. Tests efficiency of 5D computation."
    },
    {
        "test_id": "TOPO_016",
        "category": "high_dimensional_betti",
        "input": {
            "description": "Betti numbers of product S^2 x S^3",
            "manifold": "S^2 x S^3",
            "real_dimension": 5,
        },
        "expected": {
            "betti_numbers": [1, 0, 1, 1, 0, 1],  # Kunneth formula
            "euler_characteristic": 0,  # chi(S^2)*chi(S^3) = 2*0 = 0
        },
        "difficulty": "extreme",
        "rationale": "Product topology requires Kunneth theorem. A direct triangulation of "
                    "S^2 x S^3 would need the product of triangulations, exponentially many simplices."
    },

    # --------------------------------------------------------------------------
    # EULER CHARACTERISTIC OF NON-ORIENTABLE SURFACES (TOPO_017 - TOPO_020)
    # --------------------------------------------------------------------------
    {
        "test_id": "TOPO_017",
        "category": "euler_nonorientable",
        "input": {
            "description": "Euler characteristic of Mobius strip",
            "surface": "mobius_strip",
            "boundary": "single S^1",
        },
        "expected": {
            "euler_characteristic": 0,
            "is_orientable": False,
            "is_closed": False,  # Has boundary
            "H_1": "Z",
            "H_0": "Z",
        },
        "difficulty": "brutal",
        "rationale": "The Mobius strip is non-orientable with boundary. Its Euler characteristic "
                    "is 0, same as cylinder, but it has different embedding properties."
    },
    {
        "test_id": "TOPO_018",
        "category": "euler_nonorientable",
        "input": {
            "description": "Euler characteristic of connected sum of 3 projective planes",
            "surface": "3RP^2",  # = RP^2 # RP^2 # RP^2
            "representation": "polygon with 6 sides identified",
        },
        "expected": {
            "euler_characteristic": -1,  # chi = 2 - k for non-orientable
            "crosscap_number": 3,
            "H_1": "Z + Z/2Z",
            "H_0": "Z",
            "H_2": "0",
        },
        "difficulty": "extreme",
        "rationale": "Non-orientable surfaces are classified by crosscap number k, with "
                    "chi = 2 - k. Testing connected sums requires proper triangulation merging."
    },
    {
        "test_id": "TOPO_019",
        "category": "euler_nonorientable",
        "input": {
            "description": "Classification of surface with chi = -5, non-orientable",
            "euler_characteristic": -5,
            "is_orientable": False,
        },
        "expected": {
            "surface": "connected sum of 7 projective planes",
            "crosscap_number": 7,  # chi = 2 - 7 = -5
            "fundamental_group_abelianization": "Z^6 + Z/2Z",
        },
        "difficulty": "brutal",
        "rationale": "Given Euler characteristic and orientability, classify the surface. "
                    "Tests understanding of surface classification theorem."
    },
    {
        "test_id": "TOPO_020",
        "category": "euler_nonorientable",
        "input": {
            "description": "Verify Gauss-Bonnet for non-orientable surface",
            "surface": "klein_bottle",
            "verification": "integral of K over surface",
        },
        "expected": {
            "euler_characteristic": 0,
            "gauss_bonnet_integral": "2*pi*chi = 0",
            "note": "Gauss-Bonnet works but orientation-dependent forms need care",
        },
        "difficulty": "extreme",
        "rationale": "Gauss-Bonnet theorem extends to non-orientable surfaces using densities "
                    "instead of differential forms. Tests the generalized theorem."
    },
]


# =============================================================================
# COMBINED TEST DICTIONARY
# =============================================================================

DIFF_GEOMETRY_TOPOLOGY_STRESS_TESTS = DIFFERENTIAL_GEOMETRY_TESTS + TOPOLOGY_TESTS


def get_all_tests() -> List[Dict[str, Any]]:
    """Return all 50 stress tests."""
    return DIFF_GEOMETRY_TOPOLOGY_STRESS_TESTS


def get_tests_by_category(category: str) -> List[Dict[str, Any]]:
    """Return tests filtered by category."""
    return [t for t in DIFF_GEOMETRY_TOPOLOGY_STRESS_TESTS if t["category"] == category]


def get_tests_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """Return tests filtered by difficulty level."""
    return [t for t in DIFF_GEOMETRY_TOPOLOGY_STRESS_TESTS if t["difficulty"] == difficulty]


def get_test_by_id(test_id: str) -> Dict[str, Any]:
    """Return a specific test by ID."""
    for t in DIFF_GEOMETRY_TOPOLOGY_STRESS_TESTS:
        if t["test_id"] == test_id:
            return t
    raise ValueError(f"Test {test_id} not found")


# Statistics
def print_test_statistics():
    """Print statistics about the test suite."""
    all_tests = get_all_tests()

    print("=" * 70)
    print("DIFFERENTIAL GEOMETRY & TOPOLOGY STRESS TEST SUITE")
    print("=" * 70)
    print(f"\nTotal tests: {len(all_tests)}")

    # By category
    categories = {}
    for t in all_tests:
        cat = t["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\nBy Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    # By difficulty
    difficulties = {}
    for t in all_tests:
        diff = t["difficulty"]
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print("\nBy Difficulty:")
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count}")

    # Differential Geometry vs Topology
    diff_geom = [t for t in all_tests if t["test_id"].startswith("DIFF")]
    topo = [t for t in all_tests if t["test_id"].startswith("TOPO")]
    print(f"\nDifferential Geometry tests: {len(diff_geom)}")
    print(f"Topology tests: {len(topo)}")


if __name__ == "__main__":
    print_test_statistics()
    print("\n" + "=" * 70)
    print("Sample Test Cases:")
    print("=" * 70)

    # Print first test from each category
    printed_categories = set()
    for test in get_all_tests():
        if test["category"] not in printed_categories:
            printed_categories.add(test["category"])
            print(f"\n[{test['test_id']}] {test['category'].upper()}")
            print(f"  Description: {test['input'].get('description', 'N/A')}")
            print(f"  Difficulty: {test['difficulty']}")
            print(f"  Expected: {str(test['expected'])[:80]}...")
            print(f"  Rationale: {test['rationale'][:80]}...")
