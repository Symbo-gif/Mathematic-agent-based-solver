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
GEOMETRY BRUTAL STRESS TESTS
============================

50 research-level stress tests designed to BREAK the geometry specialists:
- EuclideanGeometrySpecialist
- AnalyticGeometrySpecialist
- TransformationSpecialist
- TrigonometrySpecialist
- ComputationalGeometrySpecialist
- SolidGeometrySpecialist

These tests exploit:
- Numerical precision limits (IEEE 754 floating-point edge cases)
- Degenerate geometric configurations
- Algorithmic complexity attacks
- Accumulated floating-point error
- Near-singular matrices and transformations
- Pathological polygon configurations
"""

import math


# =============================================================================
# BRUTAL GEOMETRY STRESS TEST SUITE (50 Tests)
# =============================================================================

GEOMETRY_BRUTAL_TESTS = [
    # =========================================================================
    # CATEGORY 1: CONVEX HULL STRESS TESTS (1-5)
    # =========================================================================
    {
        "test_id": "GEOM_001",
        "category": "convex_hull",
        "input": {
            "operation": "convex_hull",
            "points": [(i * 1e-15, i * 1e-15 + 1e-16 * (i % 7)) for i in range(100000)],
            "description": "100,000 nearly collinear points with microscopic y-deviations"
        },
        "expected": "Hull should contain only 2 extreme points (or very few)",
        "difficulty": "pathological",
        "rationale": "Tests O(n log n) performance under degenerate near-collinearity. "
                     "The 1e-15 scale is at the edge of IEEE 754 double precision (epsilon ~2.2e-16). "
                     "Most convex hull algorithms fail on collinear points due to CCW test precision."
    },
    {
        "test_id": "GEOM_002",
        "category": "convex_hull",
        "input": {
            "operation": "convex_hull",
            "points": [(math.cos(2*math.pi*i/1000000), math.sin(2*math.pi*i/1000000))
                      for i in range(1000000)],
            "description": "1 million points on unit circle - all should be on hull"
        },
        "expected": "All 1M points on convex hull (circular arrangement)",
        "difficulty": "extreme",
        "rationale": "Stress tests memory and O(nh) worst case for Jarvis march. "
                     "Graham scan should handle this in O(n log n) but angular sorting "
                     "near identical angles may cause instability."
    },
    {
        "test_id": "GEOM_003",
        "category": "convex_hull",
        "input": {
            "operation": "convex_hull",
            "points": [(1e308, 1e308), (-1e308, -1e308), (1e308, -1e308), (-1e308, 1e308),
                      (0, 0)] + [(1e-308, 1e-308 * i) for i in range(1000)],
            "description": "Points spanning full IEEE 754 double range with subnormals"
        },
        "expected": "4-point hull at extremes, handling overflow/underflow gracefully",
        "difficulty": "pathological",
        "rationale": "Tests numerical range handling. Cross products of 1e308 values overflow. "
                     "Subnormal numbers (1e-308) may flush to zero on some systems."
    },
    {
        "test_id": "GEOM_004",
        "category": "convex_hull",
        "input": {
            "operation": "convex_hull",
            "points": [(0, 0)] * 50000 + [(1, 0), (0, 1), (1, 1)],
            "description": "50,000 duplicate points plus 3 distinct vertices"
        },
        "expected": "Triangle hull with vertices at (0,0), (1,0), (0,1), (1,1)",
        "difficulty": "brutal",
        "rationale": "Tests duplicate point handling. Many implementations fail with "
                     "division by zero when computing polar angles from identical points."
    },
    {
        "test_id": "GEOM_005",
        "category": "convex_hull",
        "input": {
            "operation": "convex_hull",
            "points": [(i, (-1)**i * 1e-15) for i in range(100000)],
            "description": "100,000 points alternating above/below x-axis by machine epsilon"
        },
        "expected": "Long thin hull or 2-point hull depending on precision handling",
        "difficulty": "pathological",
        "rationale": "The alternating +/- pattern at epsilon scale creates a zig-zag that "
                     "should collapse to a line but CCW tests will give inconsistent results."
    },

    # =========================================================================
    # CATEGORY 2: TRIANGULATION STRESS TESTS (6-10)
    # =========================================================================
    {
        "test_id": "GEOM_006",
        "category": "triangulation",
        "input": {
            "operation": "triangulate",
            "polygon": [(0, 0), (1e6, 0), (1e6, 1e-10), (0, 1e-10)],
            "description": "Extremely thin rectangle (aspect ratio 1e16:1)"
        },
        "expected": "2 triangles, but numerical instability likely",
        "difficulty": "brutal",
        "rationale": "Aspect ratio of 10^16 causes catastrophic cancellation in area "
                     "calculations and ear-detection. The polygon is nearly degenerate."
    },
    {
        "test_id": "GEOM_007",
        "category": "triangulation",
        "input": {
            "operation": "triangulate",
            "polygon": [(math.cos(2*math.pi*i/1000), math.sin(2*math.pi*i/1000))
                       for i in range(1000)] + [(0.5, 0)],  # interior point
            "description": "Near-circular 1000-gon with interior point (invalid simple polygon)"
        },
        "expected": "Should detect/reject non-simple polygon or produce valid triangulation",
        "difficulty": "extreme",
        "rationale": "Tests handling of self-intersecting or invalid polygon input. "
                     "Ear-clipping assumes simple polygon; interior points break this."
    },
    {
        "test_id": "GEOM_008",
        "category": "triangulation",
        "input": {
            "operation": "triangulate",
            "polygon": [(i, 0) for i in range(10000)] + [(9999, 1), (0, 1)],
            "description": "Extremely long thin polygon with 10,000 collinear bottom vertices"
        },
        "expected": "~10,000 thin triangles (sliver triangles)",
        "difficulty": "pathological",
        "rationale": "Creates pathological 'sliver' triangles with near-zero area. "
                     "Ear detection will struggle with collinear sequences."
    },
    {
        "test_id": "GEOM_009",
        "category": "triangulation",
        "input": {
            "operation": "triangulate",
            "polygon": [(0, 0), (1, 1e-16), (2, 0), (3, 1e-16), (4, 0),
                       (4, 1), (0, 1)],
            "description": "Polygon with vertices offset by machine epsilon creating fake ears"
        },
        "expected": "Valid triangulation despite near-collinear vertices",
        "difficulty": "brutal",
        "rationale": "The 1e-16 offsets are at machine epsilon. CCW tests will give "
                     "inconsistent results for ear detection depending on operation order."
    },
    {
        "test_id": "GEOM_010",
        "category": "triangulation",
        "input": {
            "operation": "triangulate",
            "polygon": [(0, 0), (1, 0), (0.5, 1e-300), (1, 1), (0, 1)],
            "description": "Polygon with subnormal coordinate (below normal float range)"
        },
        "expected": "Triangulation handling subnormal numbers correctly",
        "difficulty": "extreme",
        "rationale": "Subnormal floats (below ~2.2e-308) have reduced precision and "
                     "may flush to zero, causing geometric tests to fail unexpectedly."
    },

    # =========================================================================
    # CATEGORY 3: CLOSEST PAIR PRECISION TESTS (11-15)
    # =========================================================================
    {
        "test_id": "GEOM_011",
        "category": "closest_pair",
        "input": {
            "operation": "closest_pair",
            "points": [(0, 0), (1e-15, 0), (2e-15, 0), (1e-15, 1e-15)],
            "description": "Four points with distances at machine epsilon scale"
        },
        "expected": "Closest pair with distance ~1e-15, but precision may fail",
        "difficulty": "pathological",
        "rationale": "At 1e-15 scale, distance calculations lose all significant digits. "
                     "The divide-and-conquer strip check uses distance comparison that fails here."
    },
    {
        "test_id": "GEOM_012",
        "category": "closest_pair",
        "input": {
            "operation": "closest_pair",
            "points": [(i, 0) for i in range(100000)] + [(50000, 1e-15)],
            "description": "100,000 collinear points with one offset by 10^-15"
        },
        "expected": "Closest pair: (50000, 0) and (50000, 1e-15), distance 1e-15",
        "difficulty": "brutal",
        "rationale": "Tests whether the strip-based merge step correctly identifies "
                     "cross-boundary closest pairs at extreme precision limits."
    },
    {
        "test_id": "GEOM_013",
        "category": "closest_pair",
        "input": {
            "operation": "closest_pair",
            "points": [(1.0, 0), (1.0 + 2.2204460492503131e-16, 0)],  # exact machine epsilon
            "description": "Two points separated by exactly machine epsilon"
        },
        "expected": "Distance = machine epsilon (2.22e-16) or 0 due to comparison failure",
        "difficulty": "pathological",
        "rationale": "This is the smallest representable difference for 1.0 in IEEE 754. "
                     "1.0 + eps = 1.0 in floating point, so subtraction gives 0."
    },
    {
        "test_id": "GEOM_014",
        "category": "closest_pair",
        "input": {
            "operation": "closest_pair",
            "points": [(float('inf'), 0), (float('inf'), 1), (0, 0), (1, 0)],
            "description": "Points including infinity values"
        },
        "expected": "Should handle inf gracefully or reject invalid input",
        "difficulty": "extreme",
        "rationale": "IEEE 754 infinity arithmetic: inf - inf = nan, inf * 0 = nan. "
                     "Distance calculations will produce nan, breaking comparisons."
    },
    {
        "test_id": "GEOM_015",
        "category": "closest_pair",
        "input": {
            "operation": "closest_pair",
            "points": [(i * 1e-10, (i * 1e-10) ** 2) for i in range(1, 100001)],
            "description": "100,000 points on parabola y=x^2 with 1e-10 spacing"
        },
        "expected": "Closest pair near origin where curve density is highest",
        "difficulty": "brutal",
        "rationale": "Parabola has non-uniform point density. The closest pair is near "
                     "x=0 where the curve is flattest. Tests adaptive precision handling."
    },

    # =========================================================================
    # CATEGORY 4: ROTATION/GIMBAL LOCK TESTS (16-20)
    # =========================================================================
    {
        "test_id": "GEOM_016",
        "category": "rotation",
        "input": {
            "operation": "rotation_matrix_3d",
            "rotations": [("y", math.pi/2), ("x", math.pi/4), ("z", math.pi/3)],
            "description": "Euler angles with Y at 90 degrees (gimbal lock configuration)"
        },
        "expected": "Rotation matrix loses one degree of freedom at gimbal lock",
        "difficulty": "brutal",
        "rationale": "When Y rotation = 90 degrees, X and Z rotations become equivalent, "
                     "causing loss of one degree of freedom. The matrix is still valid "
                     "but inverse operations become ambiguous."
    },
    {
        "test_id": "GEOM_017",
        "category": "rotation",
        "input": {
            "operation": "rotation_matrix_3d",
            "axis": "z",
            "angle": 1e-16,
            "description": "Rotation by machine epsilon angle"
        },
        "expected": "Matrix should be identity (rotation too small to represent)",
        "difficulty": "extreme",
        "rationale": "cos(1e-16) = 1.0, sin(1e-16) = 1e-16 in double precision. "
                     "The rotation is effectively zero but sin value may not be exactly zero."
    },
    {
        "test_id": "GEOM_018",
        "category": "rotation",
        "input": {
            "operation": "compose_rotations",
            "rotations": [(2*math.pi/1000, "z") for _ in range(1000)],
            "description": "1000 small rotations that should sum to 2*pi (identity)"
        },
        "expected": "Final matrix should be identity, but accumulated error prevents this",
        "difficulty": "pathological",
        "rationale": "Each rotation introduces ~1e-16 error. After 1000 compositions, "
                     "accumulated error ~1e-13 makes the matrix measurably non-identity."
    },
    {
        "test_id": "GEOM_019",
        "category": "rotation",
        "input": {
            "operation": "rotate_point_3d",
            "point": (1, 0, 0),
            "rotations": [("x", math.pi), ("y", math.pi), ("z", math.pi)],
            "description": "Three 180-degree rotations (net effect: 180 degree rotation)"
        },
        "expected": "Point at (-1, 0, 0) but sign errors possible",
        "difficulty": "brutal",
        "rationale": "180-degree rotations involve cos(pi)=-1, sin(pi)=0. "
                     "sin(pi) is approximately 1.2e-16 in IEEE 754, not exactly 0."
    },
    {
        "test_id": "GEOM_020",
        "category": "rotation",
        "input": {
            "operation": "rotation_matrix_3d",
            "axis": "arbitrary",
            "axis_vector": (1e-100, 1e-100, 1e-100),
            "angle": math.pi/4,
            "description": "Rotation around near-zero axis vector"
        },
        "expected": "Should normalize axis or reject degenerate input",
        "difficulty": "extreme",
        "rationale": "Axis vector normalization divides by magnitude ~1.7e-100. "
                     "This is representable but subsequent operations may underflow."
    },

    # =========================================================================
    # CATEGORY 5: LINE/PLANE INTERSECTION TESTS (21-25)
    # =========================================================================
    {
        "test_id": "GEOM_021",
        "category": "line_intersection",
        "input": {
            "operation": "line_intersection",
            "line1": [(0, 0), (1, 1e-15)],
            "line2": [(0, 1e-15), (1, 0)],
            "description": "Two lines that are nearly parallel (angle < 1e-15 radians)"
        },
        "expected": "Intersection far from origin or 'parallel' detection",
        "difficulty": "pathological",
        "rationale": "The determinant for intersection is ~2e-15, near the tolerance "
                     "threshold. Result is highly sensitive to tolerance choice."
    },
    {
        "test_id": "GEOM_022",
        "category": "line_intersection",
        "input": {
            "operation": "line_intersection",
            "line1": [(0, 0), (1e15, 1e15)],
            "line2": [(1e15, 0), (0, 1e15)],
            "description": "Lines defined by points at 1e15 scale"
        },
        "expected": "Intersection at (0.5e15, 0.5e15) but precision lost",
        "difficulty": "brutal",
        "rationale": "At 1e15 scale, we have only ~1 digit of precision after decimal. "
                     "The intersection calculation involves subtraction of large similar values."
    },
    {
        "test_id": "GEOM_023",
        "category": "plane_intersection",
        "input": {
            "operation": "plane_intersection",
            "plane1": {"a": 1, "b": 0, "c": 0, "d": 0},
            "plane2": {"a": 1, "b": 1e-15, "c": 0, "d": 1},
            "description": "Two nearly parallel planes (normal vectors differ by 1e-15)"
        },
        "expected": "Line of intersection very far from origin or 'parallel' detection",
        "difficulty": "extreme",
        "rationale": "The cross product of nearly parallel normals has magnitude ~1e-15. "
                     "Direction of intersection line is numerically unstable."
    },
    {
        "test_id": "GEOM_024",
        "category": "ray_plane_intersection",
        "input": {
            "operation": "ray_plane_intersection",
            "ray_origin": (0, 0, 0),
            "ray_direction": (1, 1e-16, 0),
            "plane": {"a": 0, "b": 1, "c": 0, "d": -1},
            "description": "Ray nearly parallel to plane (angle < 1e-16 radians)"
        },
        "expected": "Intersection at enormous distance or 'parallel' detection",
        "difficulty": "pathological",
        "rationale": "The dot product of ray direction and plane normal is 1e-16. "
                     "Division by this gives intersection at t~1e16, beyond useful precision."
    },
    {
        "test_id": "GEOM_025",
        "category": "line_intersection",
        "input": {
            "operation": "line_segment_intersection",
            "seg1": [(0, 0), (1, 0)],
            "seg2": [(0.5, 0), (0.5, 1)],
            "description": "T-intersection where segment endpoint lies on other segment"
        },
        "expected": "Intersection at (0.5, 0) - endpoint inclusion case",
        "difficulty": "brutal",
        "rationale": "Degenerate case where one segment endpoint exactly touches the other. "
                     "Requires careful handling of the t=0 or t=1 boundary conditions."
    },

    # =========================================================================
    # CATEGORY 6: VORONOI/DELAUNAY DEGENERATE TESTS (26-30)
    # =========================================================================
    {
        "test_id": "GEOM_026",
        "category": "delaunay",
        "input": {
            "operation": "delaunay_triangulation",
            "points": [(0, 0), (1, 0), (0.5, math.sqrt(3)/2), (0.5, math.sqrt(3)/6)],
            "description": "Four cocircular points (all lie on same circle)"
        },
        "expected": "Two valid triangulations exist - algorithm must choose one",
        "difficulty": "brutal",
        "rationale": "Cocircular points create ambiguous Delaunay triangulation. "
                     "The incircle test returns exactly 0, causing tie-breaking issues."
    },
    {
        "test_id": "GEOM_027",
        "category": "voronoi",
        "input": {
            "operation": "voronoi_diagram",
            "points": [(i, 0) for i in range(1000)],
            "description": "1000 collinear points - degenerate Voronoi configuration"
        },
        "expected": "Voronoi cells are infinite half-planes (degenerate)",
        "difficulty": "pathological",
        "rationale": "Collinear points have no bounded Voronoi cells. "
                     "The algorithm must handle unbounded cells or detect degeneracy."
    },
    {
        "test_id": "GEOM_028",
        "category": "delaunay",
        "input": {
            "operation": "delaunay_triangulation",
            "points": [(math.cos(2*math.pi*i/100), math.sin(2*math.pi*i/100))
                      for i in range(100)],
            "description": "100 points on unit circle - all cocircular"
        },
        "expected": "Fan triangulation from any vertex, but many valid choices",
        "difficulty": "extreme",
        "rationale": "All points are cocircular, making every triangulation technically valid. "
                     "The incircle predicate is zero for all point quadruples."
    },
    {
        "test_id": "GEOM_029",
        "category": "voronoi",
        "input": {
            "operation": "voronoi_diagram",
            "points": [(0, 0), (1e-15, 0), (0, 1e-15), (1e-15, 1e-15)],
            "description": "Four points forming square with side 1e-15"
        },
        "expected": "Voronoi diagram at microscopic scale, precision collapse",
        "difficulty": "pathological",
        "rationale": "The perpendicular bisectors are separated by ~5e-16, "
                     "below machine epsilon relative to point coordinates."
    },
    {
        "test_id": "GEOM_030",
        "category": "delaunay",
        "input": {
            "operation": "delaunay_triangulation",
            "points": [(i, j) for i in range(100) for j in range(100)],
            "description": "10,000 points on regular grid - maximum degeneracy"
        },
        "expected": "Grid creates maximum cocircular point configurations",
        "difficulty": "extreme",
        "rationale": "Every 2x2 square of grid points is cocircular. "
                     "This is the worst-case input for Delaunay algorithms."
    },

    # =========================================================================
    # CATEGORY 7: 3D SOLID GEOMETRY GRAZING TESTS (31-35)
    # =========================================================================
    {
        "test_id": "GEOM_031",
        "category": "ray_sphere",
        "input": {
            "operation": "ray_sphere_intersection",
            "ray_origin": (0, 1 + 1e-15, 0),
            "ray_direction": (1, 0, 0),
            "sphere_center": (0, 0, 0),
            "sphere_radius": 1,
            "description": "Ray grazing sphere at distance 1e-15 from surface"
        },
        "expected": "Tangent intersection or miss depending on precision",
        "difficulty": "pathological",
        "rationale": "The discriminant is approximately -2e-15, making hit/miss determination "
                     "entirely dependent on floating-point rounding in the quadratic formula."
    },
    {
        "test_id": "GEOM_032",
        "category": "ray_plane",
        "input": {
            "operation": "ray_plane_intersection",
            "ray_origin": (0, 0, 0),
            "ray_direction": (1e-8, 1e-8, 1),
            "plane": {"a": 0, "b": 0, "c": 1, "d": -1e16},
            "description": "Ray intersecting plane at distance 1e16"
        },
        "expected": "Intersection point with 0 precision (beyond representable range)",
        "difficulty": "extreme",
        "rationale": "At t=1e16, the ray direction scaled by t has x,y components of 1e8, "
                     "but we lose all precision in the z-component calculation."
    },
    {
        "test_id": "GEOM_033",
        "category": "tetrahedron",
        "input": {
            "operation": "volume_tetrahedron",
            "vertices": [(0, 0, 0), (1, 0, 0), (0.5, 1e-15, 0), (0.5, 0.5e-15, 1)],
            "description": "Nearly degenerate tetrahedron (three vertices nearly collinear)"
        },
        "expected": "Volume ~5e-16, at or below numerical noise",
        "difficulty": "brutal",
        "rationale": "The scalar triple product involves terms that cancel to 15+ decimal places. "
                     "The computed volume may be zero or have wrong sign."
    },
    {
        "test_id": "GEOM_034",
        "category": "point_in_solid",
        "input": {
            "operation": "point_in_tetrahedron",
            "point": (0.25, 0.25, 0.25 + 1e-15),
            "tetrahedron": [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)],
            "description": "Point on tetrahedron surface offset by 1e-15"
        },
        "expected": "Inside/outside determination at boundary precision limit",
        "difficulty": "pathological",
        "rationale": "The point is exactly on the plane x+y+z=0.75 offset by 1e-15. "
                     "Barycentric coordinate tests will give values of ~1e-15 magnitude."
    },
    {
        "test_id": "GEOM_035",
        "category": "3d_distance",
        "input": {
            "operation": "distance_point_plane",
            "point": (1e100, 1e100, 1e100),
            "plane": {"a": 1, "b": 1, "c": 1, "d": 0},
            "description": "Point at 1e100 scale, plane through origin"
        },
        "expected": "Distance ~1.73e100, but intermediate calculations overflow",
        "difficulty": "extreme",
        "rationale": "Computing a^2 + b^2 + c^2 = 3 is fine, but ax + by + cz = 3e100 "
                     "and the division is stable. However, other formulations may overflow."
    },

    # =========================================================================
    # CATEGORY 8: TRIGONOMETRIC IDENTITY TESTS (36-40)
    # =========================================================================
    {
        "test_id": "GEOM_036",
        "category": "trig_identity",
        "input": {
            "operation": "verify_identity",
            "lhs": "sin(pi/12)",
            "rhs": "(sqrt(6) - sqrt(2))/4",
            "description": "Exact value of sin(15 degrees)"
        },
        "expected": "Identity verified: sin(pi/12) = (sqrt(6)-sqrt(2))/4",
        "difficulty": "brutal",
        "rationale": "pi/12 = 15 degrees has exact algebraic value. Numerical evaluation "
                     "gives ~0.2588, and (sqrt(6)-sqrt(2))/4 also gives ~0.2588, "
                     "but they differ in the 16th decimal place."
    },
    {
        "test_id": "GEOM_037",
        "category": "trig_identity",
        "input": {
            "operation": "verify_identity",
            "lhs": "tan(x) + tan(y) + tan(z)",
            "rhs": "tan(x)*tan(y)*tan(z)",
            "constraint": "x + y + z = pi",
            "description": "Tangent sum identity for angles summing to pi"
        },
        "expected": "Identity holds when x+y+z=pi (special case)",
        "difficulty": "extreme",
        "rationale": "This identity requires symbolic reasoning about the constraint. "
                     "Numerical verification at random points will fail because the "
                     "identity only holds when the constraint is satisfied."
    },
    {
        "test_id": "GEOM_038",
        "category": "trig_evaluation",
        "input": {
            "operation": "evaluate",
            "expression": "sin(1e-20)",
            "description": "Sine of extremely small angle (below precision threshold)"
        },
        "expected": "sin(1e-20) = 1e-20 exactly (small angle approximation)",
        "difficulty": "pathological",
        "rationale": "For x < 1e-8, sin(x) = x to machine precision. "
                     "But the math library may lose precision for 1e-20 input."
    },
    {
        "test_id": "GEOM_039",
        "category": "trig_evaluation",
        "input": {
            "operation": "evaluate",
            "expression": "cos(pi/2 - 1e-15)",
            "description": "Cosine near zero (complementary angle at precision limit)"
        },
        "expected": "cos(pi/2 - 1e-15) = sin(1e-15) ~ 1e-15",
        "difficulty": "brutal",
        "rationale": "pi/2 cannot be represented exactly. pi/2 in float is ~1.5707963267948966, "
                     "and subtracting 1e-15 may not change the value due to magnitude difference."
    },
    {
        "test_id": "GEOM_040",
        "category": "trig_identity",
        "input": {
            "operation": "simplify",
            "expression": "sin(x)^4 - cos(x)^4 + cos(2*x)",
            "description": "Expression that should simplify to 0"
        },
        "expected": "Simplifies to 0 (using sin^4 - cos^4 = -cos(2x) identity)",
        "difficulty": "extreme",
        "rationale": "Requires applying multiple identities in correct order: "
                     "sin^4 - cos^4 = (sin^2-cos^2)(sin^2+cos^2) = -cos(2x), "
                     "so expression = -cos(2x) + cos(2x) = 0."
    },

    # =========================================================================
    # CATEGORY 9: TRANSFORMATION ACCUMULATED ERROR (41-45)
    # =========================================================================
    {
        "test_id": "GEOM_041",
        "category": "transform_composition",
        "input": {
            "operation": "compose_transforms",
            "transforms": [
                {"type": "rotate", "angle": 2*math.pi/360}
            ] * 360,
            "point": (1, 0),
            "description": "360 one-degree rotations (should return to start)"
        },
        "expected": "Point should return to (1, 0), but accumulated error ~1e-13",
        "difficulty": "pathological",
        "rationale": "Each rotation matrix multiplication introduces ~1e-16 error. "
                     "After 360 multiplications, error accumulates to ~1e-13."
    },
    {
        "test_id": "GEOM_042",
        "category": "transform_inverse",
        "input": {
            "operation": "verify_inverse",
            "matrix": [
                [1, 1e-15, 0],
                [0, 1, 1e-15],
                [1e-15, 0, 1]
            ],
            "description": "Near-identity matrix (condition number ~1e15)"
        },
        "expected": "M * M^-1 should be identity, but condition number causes errors",
        "difficulty": "extreme",
        "rationale": "The matrix has condition number ~1e15, meaning inverse computation "
                     "amplifies input errors by factor 1e15. M*M^-1 will deviate from I."
    },
    {
        "test_id": "GEOM_043",
        "category": "coordinate_transform",
        "input": {
            "operation": "polar_to_cartesian_chain",
            "start": (1, 0),
            "conversions": 10000,
            "description": "10,000 round-trip polar/Cartesian conversions"
        },
        "expected": "Point should remain at (1, 0), but error accumulates",
        "difficulty": "brutal",
        "rationale": "Each conversion involves atan2, sin, cos, sqrt. "
                     "After 10,000 round trips, accumulated error is significant."
    },
    {
        "test_id": "GEOM_044",
        "category": "transform_determinant",
        "input": {
            "operation": "rotation_determinant",
            "rotations": [
                {"axis": "x", "angle": math.pi/7},
                {"axis": "y", "angle": math.pi/11},
                {"axis": "z", "angle": math.pi/13}
            ] * 1000,
            "description": "Determinant after 3000 rotation compositions"
        },
        "expected": "Determinant should be exactly 1.0 (rotation preserves volume)",
        "difficulty": "pathological",
        "rationale": "Rotation matrices have det=1 by definition. But accumulated "
                     "floating-point errors cause det to drift from 1.0 after many compositions."
    },
    {
        "test_id": "GEOM_045",
        "category": "reflection_composition",
        "input": {
            "operation": "compose_reflections",
            "reflections": [
                {"line_angle": i * math.pi / 1000}
                for i in range(1000)
            ],
            "description": "1000 reflections across lines at incrementing angles"
        },
        "expected": "Net transformation (reflection or rotation depending on count)",
        "difficulty": "extreme",
        "rationale": "Two reflections = rotation by twice the angle between reflection lines. "
                     "1000 reflections creates complex accumulated transformation."
    },

    # =========================================================================
    # CATEGORY 10: POLYGON/AREA CATASTROPHIC CANCELLATION (46-50)
    # =========================================================================
    {
        "test_id": "GEOM_046",
        "category": "polygon_area",
        "input": {
            "operation": "polygon_area",
            "vertices": [
                (1e15, 1e15), (1e15 + 1, 1e15), (1e15 + 1, 1e15 + 1), (1e15, 1e15 + 1)
            ],
            "description": "Unit square at coordinates 1e15 (catastrophic cancellation)"
        },
        "expected": "Area = 1.0, but computation loses all precision",
        "difficulty": "pathological",
        "rationale": "Shoelace formula computes x1*(y2-yn) + ... with 1e15 scale coordinates. "
                     "The differences y2-yn are ~1, so we compute 1e15 * 1 and sum terms "
                     "that cancel to get 1.0, losing 15 digits of precision."
    },
    {
        "test_id": "GEOM_047",
        "category": "polygon_centroid",
        "input": {
            "operation": "polygon_centroid",
            "vertices": [(1e8 + i, 1e8 + (i**2 % 100)) for i in range(1000)],
            "description": "1000-vertex polygon at 1e8 offset with small variations"
        },
        "expected": "Centroid computation with severe loss of precision",
        "difficulty": "brutal",
        "rationale": "Centroid formula involves products and sums at 1e8 scale. "
                     "Small variations (0-99) are lost in the noise of 1e8 operations."
    },
    {
        "test_id": "GEOM_048",
        "category": "point_in_polygon",
        "input": {
            "operation": "point_in_polygon",
            "point": (0.5, 0.5 + 1e-15),
            "polygon": [(0, 0), (1, 0), (1, 1), (0, 1)],
            "description": "Point 1e-15 above center of unit square"
        },
        "expected": "Inside, but ray-casting may give wrong answer at precision limit",
        "difficulty": "extreme",
        "rationale": "Ray casting tests involve computing intersection t-values. "
                     "At 1e-15 offset, the comparison t >= 0 is at precision limit."
    },
    {
        "test_id": "GEOM_049",
        "category": "polygon_convexity",
        "input": {
            "operation": "is_convex",
            "vertices": [(math.cos(2*math.pi*i/1000) + (1e-14 if i == 500 else 0),
                         math.sin(2*math.pi*i/1000)) for i in range(1000)],
            "description": "Circle polygon with one vertex offset by 1e-14 (non-convex)"
        },
        "expected": "Non-convex due to single indented vertex, but precision may miss it",
        "difficulty": "pathological",
        "rationale": "The 1e-14 inward offset at vertex 500 creates a tiny non-convexity. "
                     "The CCW test comparing adjacent angles may not detect this."
    },
    {
        "test_id": "GEOM_050",
        "category": "triangle_center",
        "input": {
            "operation": "circumcenter",
            "triangle": [(0, 0), (1e10, 1e-10), (5e9, 1e10)],
            "description": "Triangle with extreme aspect ratio spanning 20 orders of magnitude"
        },
        "expected": "Circumcenter calculation with catastrophic precision loss",
        "difficulty": "pathological",
        "rationale": "The circumcenter formula involves determinant of coordinates. "
                     "With coordinates spanning 1e-10 to 1e10, we lose 20+ digits in computation. "
                     "The circumcenter may be computed with 0 significant figures."
    },
]


# =============================================================================
# ACCESSOR FUNCTION
# =============================================================================

def get_brutal_geometry_tests():
    """Return the list of 50 brutal geometry stress tests."""
    return GEOMETRY_BRUTAL_TESTS


def get_tests_by_category(category):
    """Return tests filtered by category."""
    return [t for t in GEOMETRY_BRUTAL_TESTS if t["category"] == category]


def get_tests_by_difficulty(difficulty):
    """Return tests filtered by difficulty level."""
    return [t for t in GEOMETRY_BRUTAL_TESTS if t["difficulty"] == difficulty]


# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

def print_test_summary():
    """Print summary statistics for the test suite."""
    categories = {}
    difficulties = {}

    for test in GEOMETRY_BRUTAL_TESTS:
        cat = test["category"]
        diff = test["difficulty"]
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print("=" * 60)
    print("GEOMETRY BRUTAL STRESS TEST SUITE - SUMMARY")
    print("=" * 60)
    print(f"\nTotal Tests: {len(GEOMETRY_BRUTAL_TESTS)}")
    print("\nBy Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print("\nBy Difficulty:")
    for diff, count in sorted(difficulties.items(), key=lambda x: x[1], reverse=True):
        print(f"  {diff}: {count}")
    print("=" * 60)


if __name__ == "__main__":
    print_test_summary()
    print("\nSample test:")
    import json
    print(json.dumps(GEOMETRY_BRUTAL_TESTS[0], indent=2))
