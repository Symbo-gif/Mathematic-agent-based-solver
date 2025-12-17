# Proposed New Specialist Agents

## System Analysis Summary

Based on comprehensive system analysis, the following capability gaps have been identified:

| Domain | Current Score | Target Score | Gap Analysis |
|--------|---------------|--------------|--------------|
| ODE Solving | 55/100 | 85/100 | Limited method selection, no stiffness detection |
| Physics | 44/100 | 80/100 | Formula lookup only, no actual problem solving |
| Linear Algebra Robustness | 66/100 | 90/100 | No numerical stability monitoring |
| Series | 68/100 | 88/100 | Missing Fourier analysis, limited convergence tests |
| Limits | 72/100 | 90/100 | Good foundation, needs special function support |

---

## Agent 1: ODEMethodSelector

### 1.1 Agent Name and Purpose

**Agent ID:** `ode_method_selector_001`
**Tier:** 2.5 (Intermediate between Supervisor and Specialist)
**Service Type:** `math.calculus.ode.routing`

**Purpose:**
The ODEMethodSelector acts as an intelligent router that analyzes ODE characteristics and selects the optimal solving technique. Unlike the current simplified ODE solver, this agent inspects equation properties (linearity, order, coefficients, stiffness indicators) and routes to specialized sub-solvers.

**Gap Addressed:**
Current ODE solving (55/100) fails because it applies a one-size-fits-all approach. Complex ODEs like stiff systems, Bessel equations, or Bernoulli equations require specific methods.

### 1.2 Mathematical Rules (Native, No SymPy)

```python
# =============================================================================
# ODE CLASSIFICATION RULES (Native Implementation)
# =============================================================================

class ODEClassifier:
    """
    Native ODE classification without SymPy.

    CLASSIFICATION TREE:
    1. ORDER: First-order, Second-order, Higher-order
    2. LINEARITY: Linear vs Nonlinear
    3. COEFFICIENT TYPE: Constant vs Variable coefficients
    4. SPECIAL FORMS: Separable, Exact, Bernoulli, Riccati, Bessel, Legendre
    5. STIFFNESS: Estimated eigenvalue ratio for numerical stability
    """

    # Rule 1: Order Detection
    # Count maximum derivative order by finding dy/dx patterns or y'', y''' notation
    ORDER_PATTERNS = {
        r"y''''|d4y/dx4": 4,
        r"y'''|d3y/dx3": 3,
        r"y''|d2y/dx2": 2,
        r"y'|dy/dx": 1,
    }

    # Rule 2: Linearity Check
    # Linear if: a_n(x)*y^(n) + ... + a_1(x)*y' + a_0(x)*y = g(x)
    # Nonlinear if: y*y', y^2, sin(y), etc.
    NONLINEAR_INDICATORS = [
        r"y\s*\*\s*y'",      # y*y'
        r"y\*\*2",           # y^2
        r"y\^2",             # y^2
        r"sin\(y\)",         # sin(y)
        r"cos\(y\)",         # cos(y)
        r"exp\(y\)",         # exp(y)
        r"\(y'\)\*\*2",      # (y')^2
    ]

    # Rule 3: Separable Form Detection
    # dy/dx = f(x)*g(y) is separable
    # Pattern: Expression can be factored into x-only and y-only parts

    # Rule 4: Exact Equation Detection
    # M(x,y)dx + N(x,y)dy = 0 is exact if dM/dy = dN/dx

    # Rule 5: Bernoulli Form Detection
    # y' + P(x)*y = Q(x)*y^n (n != 0, 1)
    BERNOULLI_PATTERN = r"y'\s*\+.*y\s*=.*y\*\*"

    # Rule 6: Riccati Form Detection
    # y' = P(x) + Q(x)*y + R(x)*y^2

    # Rule 7: Bessel Equation Detection
    # x^2*y'' + x*y' + (x^2 - n^2)*y = 0
    BESSEL_PATTERN = r"x\*\*2\s*\*\s*y''\s*\+\s*x\s*\*\s*y'"

    # Rule 8: Legendre Equation Detection
    # (1-x^2)*y'' - 2*x*y' + n*(n+1)*y = 0
    LEGENDRE_PATTERN = r"\(1\s*-\s*x\*\*2\)\s*\*\s*y''"

    # Rule 9: Stiffness Estimation
    # Stiff if eigenvalue ratio > 1000 (estimate from coefficients)
    STIFFNESS_THRESHOLD = 1000


# =============================================================================
# ODE SOLVING METHODS (Native Implementation)
# =============================================================================

class NativeODESolvers:
    """
    Native ODE solving methods without SymPy.
    """

    @staticmethod
    def solve_separable(expr_str: str, var: str = 'x') -> Tuple[bool, str, str]:
        """
        Separable ODE: dy/dx = f(x)*g(y)

        Method:
        1. Separate: dy/g(y) = f(x)dx
        2. Integrate both sides
        3. Solve for y if possible

        Returns: (success, solution, method_name)
        """
        pass

    @staticmethod
    def solve_first_order_linear(expr_str: str, var: str = 'x') -> Tuple[bool, str, str]:
        """
        First-order linear: y' + P(x)*y = Q(x)

        Method: Integrating Factor
        1. Compute mu(x) = exp(integral(P(x)dx))
        2. Solution: y = (1/mu) * integral(mu * Q dx) + C/mu

        Returns: (success, solution, method_name)
        """
        pass

    @staticmethod
    def solve_second_order_constant_coeff(expr_str: str, var: str = 'x') -> Tuple[bool, str, str]:
        """
        Second-order constant coefficient: ay'' + by' + cy = g(x)

        Method: Characteristic Equation
        1. Find roots of ar^2 + br + c = 0
        2. Distinct real: y = C1*exp(r1*x) + C2*exp(r2*x)
        3. Repeated real: y = (C1 + C2*x)*exp(r*x)
        4. Complex: y = exp(alpha*x)*(C1*cos(beta*x) + C2*sin(beta*x))
        5. Add particular solution for g(x) != 0

        Returns: (success, solution, method_name)
        """
        pass

    @staticmethod
    def solve_bernoulli(expr_str: str, var: str = 'x') -> Tuple[bool, str, str]:
        """
        Bernoulli: y' + P(x)*y = Q(x)*y^n

        Method: Substitution v = y^(1-n)
        1. Substitute to get linear ODE in v
        2. Solve linear ODE
        3. Back-substitute: y = v^(1/(1-n))

        Returns: (success, solution, method_name)
        """
        pass

    @staticmethod
    def solve_exact(M: str, N: str, var: str = 'x') -> Tuple[bool, str, str]:
        """
        Exact: M(x,y)dx + N(x,y)dy = 0 where dM/dy = dN/dx

        Method:
        1. F(x,y) = integral(M dx) treating y as constant
        2. Add h(y) where h'(y) = N - dF/dy
        3. Solution: F(x,y) = C

        Returns: (success, solution, method_name)
        """
        pass

    @staticmethod
    def runge_kutta_4(f, y0: float, x0: float, x_end: float,
                      h: float = 0.01) -> List[Tuple[float, float]]:
        """
        4th-order Runge-Kutta for numerical ODE solving.

        dy/dx = f(x, y), y(x0) = y0

        Algorithm:
        k1 = f(x_n, y_n)
        k2 = f(x_n + h/2, y_n + h*k1/2)
        k3 = f(x_n + h/2, y_n + h*k2/2)
        k4 = f(x_n + h, y_n + h*k3)
        y_{n+1} = y_n + (h/6)*(k1 + 2*k2 + 2*k3 + k4)

        Returns: List of (x, y) points
        """
        pass

    @staticmethod
    def adaptive_step_rk45(f, y0: float, x0: float, x_end: float,
                           tol: float = 1e-6) -> List[Tuple[float, float]]:
        """
        Runge-Kutta-Fehlberg (RK45) with adaptive step size.

        Uses embedded 4th and 5th order methods to estimate error
        and adjust step size dynamically.

        Good for: Non-stiff problems requiring accuracy control

        Returns: List of (x, y) points with adaptive spacing
        """
        pass

    @staticmethod
    def implicit_euler(f, y0: float, x0: float, x_end: float,
                       h: float = 0.01) -> List[Tuple[float, float]]:
        """
        Implicit (Backward) Euler for stiff ODEs.

        y_{n+1} = y_n + h*f(x_{n+1}, y_{n+1})

        Requires Newton iteration to solve for y_{n+1}
        Good for: Stiff problems where explicit methods fail

        Returns: List of (x, y) points
        """
        pass
```

### 1.3 Supervisor Hierarchy Position

```
                    CalculusSupervisor (Tier 2)
                           |
                           v
                  ODEMethodSelector (Tier 2.5)  <-- NEW
                    /    |    |    \
                   v     v    v     v
              Separable  Linear  Bernoulli  Numerical
              Solver     Solver  Solver     Solver
              (Tier 3)  (Tier 3) (Tier 3)   (Tier 3)
```

**Routing Logic:**
1. CalculusSupervisor detects "ODE" keywords and routes to ODEMethodSelector
2. ODEMethodSelector analyzes equation structure
3. Routes to appropriate sub-solver based on classification
4. Maintains fallback chain: Symbolic -> Numerical -> Unevaluated

### 1.4 Key Methods Exposed

```python
class ODEMethodSelector(BDIAgent):
    """
    Tier 2.5 ODE Method Selection Agent

    Service Registration:
        service_type: 'math.calculus.ode.routing'
        algorithm: 'classification_based'
        cost: 'low'
        tier: '2.5'
    """

    def classify_ode(self, expr_str: str) -> ODEClassification:
        """
        Analyze ODE and return classification.

        Returns:
            ODEClassification with:
            - order: int
            - is_linear: bool
            - is_homogeneous: bool
            - special_form: Optional[str]  # 'separable', 'exact', 'bernoulli', etc.
            - is_stiff: bool
            - recommended_method: str
            - confidence: float
        """
        pass

    def select_solver(self, classification: ODEClassification) -> str:
        """
        Select optimal solver based on classification.

        Returns: Service type of recommended solver
        """
        pass

    def estimate_stiffness(self, expr_str: str, params: Dict) -> float:
        """
        Estimate stiffness ratio for numerical method selection.

        Stiff ODEs require implicit methods (backward Euler, BDF)
        Non-stiff ODEs can use explicit methods (RK4, RK45)

        Returns: Estimated eigenvalue ratio
        """
        pass

    def process(self, task_entry: Any) -> Any:
        """
        Main BDI processing: Classify -> Select -> Delegate
        """
        pass
```

### 1.5 File Location and Structure

```
src/symbo_agentic_reasoners/agents/specialists/calculus/
    ode_method_selector.py     # Main agent (NEW)
    ode_classifier.py          # Classification logic (NEW)
    ode_solvers/
        __init__.py
        separable_solver.py    # Separable ODE solver (NEW)
        linear_solver.py       # First/second order linear (NEW)
        bernoulli_solver.py    # Bernoulli equation solver (NEW)
        numerical_solver.py    # RK4, RK45, Implicit methods (NEW)
```

---

## Agent 2: PhysicsEquationSolver

### 2.1 Agent Name and Purpose

**Agent ID:** `physics_equation_solver_001`
**Tier:** 2.5 (Intermediate - coordinates physics domain)
**Service Type:** `math.physics.solver`

**Purpose:**
The PhysicsEquationSolver bridges the gap between physics formula lookup and actual problem solving. Current physics specialists (44/100) only provide formulas but don't solve word problems or multi-step derivations. This agent:
1. Extracts physical quantities from problem statements
2. Identifies applicable conservation laws and equations
3. Sets up and solves the resulting mathematical system
4. Validates units and physical reasonableness

**Gap Addressed:**
Physics score of 44/100 comes from agents that know formulas but can't apply them. A student asking "A ball is thrown upward at 20 m/s. When does it reach maximum height?" gets F=ma but not the answer t=2.04s.

### 2.2 Mathematical Rules (Native, No SymPy)

```python
# =============================================================================
# PHYSICS EQUATION SOLVING ENGINE (Native Implementation)
# =============================================================================

class PhysicsQuantityExtractor:
    """
    Extract physical quantities and their values from problem text.
    """

    # Standard physics quantities with unit patterns
    QUANTITY_PATTERNS = {
        'mass': {
            'symbols': ['m', 'M', 'mass'],
            'units': ['kg', 'g', 'lb'],
            'pattern': r'mass\s*(?:of|is|=)?\s*([\d.]+)\s*(kg|g|lb)?'
        },
        'velocity': {
            'symbols': ['v', 'V', 'u', 'velocity', 'speed'],
            'units': ['m/s', 'km/h', 'ft/s', 'mph'],
            'pattern': r'(?:velocity|speed)\s*(?:of|is|=)?\s*([\d.]+)\s*(m/s|km/h)?'
        },
        'acceleration': {
            'symbols': ['a', 'g'],
            'units': ['m/s^2', 'm/s2'],
            'pattern': r'acceleration\s*(?:of|is|=)?\s*([\d.]+)\s*(m/s\^?2)?'
        },
        'time': {
            'symbols': ['t', 'T', 'time'],
            'units': ['s', 'min', 'h', 'hr'],
            'pattern': r'(?:time|after)\s*(?:of|is|=)?\s*([\d.]+)\s*(s|sec|min|h)?'
        },
        'force': {
            'symbols': ['F', 'f'],
            'units': ['N', 'kN', 'lb'],
            'pattern': r'force\s*(?:of|is|=)?\s*([\d.]+)\s*(N|kN)?'
        },
        'energy': {
            'symbols': ['E', 'KE', 'PE', 'W'],
            'units': ['J', 'kJ', 'eV'],
            'pattern': r'energy\s*(?:of|is|=)?\s*([\d.]+)\s*(J|kJ|eV)?'
        },
        'distance': {
            'symbols': ['s', 'd', 'x', 'h', 'height', 'distance'],
            'units': ['m', 'km', 'ft', 'mi'],
            'pattern': r'(?:distance|height|displacement)\s*(?:of|is|=)?\s*([\d.]+)\s*(m|km|ft)?'
        },
        'angle': {
            'symbols': ['theta', 'phi', 'angle'],
            'units': ['deg', 'degrees', 'rad'],
            'pattern': r'angle\s*(?:of|is|=)?\s*([\d.]+)\s*(deg|degrees|rad)?'
        },
        'charge': {
            'symbols': ['q', 'Q'],
            'units': ['C', 'mC', 'uC'],
            'pattern': r'charge\s*(?:of|is|=)?\s*([\d.]+)\s*(C|mC|uC)?'
        },
        'current': {
            'symbols': ['I', 'i'],
            'units': ['A', 'mA'],
            'pattern': r'current\s*(?:of|is|=)?\s*([\d.]+)\s*(A|mA)?'
        },
        'voltage': {
            'symbols': ['V', 'U', 'emf'],
            'units': ['V', 'kV', 'mV'],
            'pattern': r'(?:voltage|potential)\s*(?:of|is|=)?\s*([\d.]+)\s*(V|kV|mV)?'
        },
        'resistance': {
            'symbols': ['R'],
            'units': ['ohm', 'kohm'],
            'pattern': r'resistance\s*(?:of|is|=)?\s*([\d.]+)\s*(ohm|kohm)?'
        }
    }


class PhysicsLawDatabase:
    """
    Database of physics laws and equations for problem solving.

    Each law entry contains:
    - equation: The mathematical relationship
    - variables: List of involved quantities
    - solve_for: Methods to isolate each variable
    - applicability: Conditions when law applies
    """

    MECHANICS_LAWS = {
        'newton_second': {
            'equation': 'F = m * a',
            'variables': ['F', 'm', 'a'],
            'solve_for': {
                'F': lambda m, a: m * a,
                'm': lambda F, a: F / a,
                'a': lambda F, m: F / m
            },
            'applicability': 'constant_mass_system'
        },
        'kinematic_v': {
            'equation': 'v = v0 + a * t',
            'variables': ['v', 'v0', 'a', 't'],
            'solve_for': {
                'v': lambda v0, a, t: v0 + a * t,
                'v0': lambda v, a, t: v - a * t,
                'a': lambda v, v0, t: (v - v0) / t,
                't': lambda v, v0, a: (v - v0) / a
            },
            'applicability': 'constant_acceleration'
        },
        'kinematic_x': {
            'equation': 'x = x0 + v0 * t + 0.5 * a * t^2',
            'variables': ['x', 'x0', 'v0', 'a', 't'],
            'solve_for': {
                'x': lambda x0, v0, a, t: x0 + v0 * t + 0.5 * a * t**2,
                # Others require quadratic formula
            },
            'applicability': 'constant_acceleration'
        },
        'kinematic_v_squared': {
            'equation': 'v^2 = v0^2 + 2 * a * (x - x0)',
            'variables': ['v', 'v0', 'a', 'x', 'x0'],
            'solve_for': {
                'v': lambda v0, a, x, x0: math.sqrt(v0**2 + 2 * a * (x - x0)),
                'a': lambda v, v0, x, x0: (v**2 - v0**2) / (2 * (x - x0))
            },
            'applicability': 'constant_acceleration'
        },
        'gravitational_pe': {
            'equation': 'PE = m * g * h',
            'variables': ['PE', 'm', 'g', 'h'],
            'solve_for': {
                'PE': lambda m, g, h: m * g * h,
                'h': lambda PE, m, g: PE / (m * g),
                'm': lambda PE, g, h: PE / (g * h)
            },
            'applicability': 'near_earth_surface'
        },
        'kinetic_energy': {
            'equation': 'KE = 0.5 * m * v^2',
            'variables': ['KE', 'm', 'v'],
            'solve_for': {
                'KE': lambda m, v: 0.5 * m * v**2,
                'v': lambda KE, m: math.sqrt(2 * KE / m),
                'm': lambda KE, v: 2 * KE / v**2
            },
            'applicability': 'non_relativistic'
        },
        'energy_conservation': {
            'equation': 'KE_i + PE_i = KE_f + PE_f',
            'variables': ['KE_i', 'PE_i', 'KE_f', 'PE_f'],
            'applicability': 'conservative_forces_only'
        },
        'momentum_conservation': {
            'equation': 'p_i = p_f',
            'variables': ['p_i', 'p_f'],
            'applicability': 'no_external_forces'
        },
        'work_energy': {
            'equation': 'W = F * d * cos(theta)',
            'variables': ['W', 'F', 'd', 'theta'],
            'solve_for': {
                'W': lambda F, d, theta: F * d * math.cos(theta),
                'F': lambda W, d, theta: W / (d * math.cos(theta)),
                'd': lambda W, F, theta: W / (F * math.cos(theta))
            },
            'applicability': 'constant_force'
        },
        'centripetal_force': {
            'equation': 'F_c = m * v^2 / r',
            'variables': ['F_c', 'm', 'v', 'r'],
            'solve_for': {
                'F_c': lambda m, v, r: m * v**2 / r,
                'v': lambda F_c, m, r: math.sqrt(F_c * r / m),
                'r': lambda m, v, F_c: m * v**2 / F_c
            },
            'applicability': 'circular_motion'
        }
    }

    ELECTROMAGNETISM_LAWS = {
        'ohms_law': {
            'equation': 'V = I * R',
            'variables': ['V', 'I', 'R'],
            'solve_for': {
                'V': lambda I, R: I * R,
                'I': lambda V, R: V / R,
                'R': lambda V, I: V / I
            }
        },
        'coulombs_law': {
            'equation': 'F = k * q1 * q2 / r^2',
            'variables': ['F', 'k', 'q1', 'q2', 'r'],
            'solve_for': {
                'F': lambda k, q1, q2, r: k * q1 * q2 / r**2,
                'r': lambda k, q1, q2, F: math.sqrt(k * q1 * q2 / F)
            }
        },
        'capacitance': {
            'equation': 'C = Q / V',
            'variables': ['C', 'Q', 'V'],
            'solve_for': {
                'C': lambda Q, V: Q / V,
                'Q': lambda C, V: C * V,
                'V': lambda Q, C: Q / C
            }
        },
        'power_electrical': {
            'equation': 'P = I * V = I^2 * R = V^2 / R',
            'variables': ['P', 'I', 'V', 'R'],
            'solve_for': {
                'P': lambda I, V: I * V,
                'I': lambda P, V: P / V
            }
        }
    }

    THERMODYNAMICS_LAWS = {
        'ideal_gas': {
            'equation': 'P * V = n * R * T',
            'variables': ['P', 'V', 'n', 'R', 'T'],
            'solve_for': {
                'P': lambda n, R, T, V: n * R * T / V,
                'V': lambda n, R, T, P: n * R * T / P,
                'T': lambda P, V, n, R: P * V / (n * R)
            }
        },
        'heat_capacity': {
            'equation': 'Q = m * c * delta_T',
            'variables': ['Q', 'm', 'c', 'delta_T'],
            'solve_for': {
                'Q': lambda m, c, dT: m * c * dT,
                'dT': lambda Q, m, c: Q / (m * c)
            }
        },
        'first_law': {
            'equation': 'delta_U = Q - W',
            'variables': ['delta_U', 'Q', 'W'],
            'solve_for': {
                'delta_U': lambda Q, W: Q - W,
                'Q': lambda dU, W: dU + W,
                'W': lambda Q, dU: Q - dU
            }
        }
    }


class PhysicsProblemSolver:
    """
    Native physics problem solver using constraint propagation.
    """

    def __init__(self):
        self.laws = PhysicsLawDatabase()
        self.extractor = PhysicsQuantityExtractor()

    def solve(self, problem_text: str, find: str) -> Dict[str, Any]:
        """
        Solve a physics word problem.

        Steps:
        1. Extract known quantities from problem text
        2. Identify what quantity to find
        3. Select applicable physics laws
        4. Set up equations
        5. Solve system (substitution/elimination)
        6. Validate units and reasonableness

        Returns:
            Dict with 'answer', 'value', 'unit', 'steps', 'equations_used'
        """
        pass

    def unit_conversion(self, value: float, from_unit: str,
                        to_unit: str) -> float:
        """Convert between units within same dimension."""
        pass

    def validate_dimensional_consistency(self, equation: str) -> bool:
        """Check that equation has consistent dimensions."""
        pass
```

### 2.3 Supervisor Hierarchy Position

```
                    MainOrchestrator (Tier 1)
                           |
           +---------------+---------------+
           |               |               |
    AlgebraSupervisor  CalculusSupervisor  PhysicsSupervisor (Tier 2)
                                               |
                                    +----------+----------+
                                    |                     |
                         PhysicsEquationSolver      MechanicsSupervisor
                               (Tier 2.5)                 |
                                    |              +------+------+
                                    v              |             |
                            [Solves multi-step   Kinematics  Dynamics
                             physics problems]   Specialist  Specialist
```

**Integration:**
- PhysicsEquationSolver is invoked when problem requires solving, not just formula lookup
- Coordinates with domain-specific supervisors (Mechanics, EM, Thermo) for specialized knowledge
- Uses algebra agents for equation manipulation

### 2.4 Key Methods Exposed

```python
class PhysicsEquationSolver(BDIAgent):
    """
    Tier 2.5 Physics Problem Solving Agent

    Service Registration:
        service_type: 'math.physics.solver'
        algorithm: 'constraint_propagation'
        cost: 'medium'
        tier: '2.5'
        capabilities: 'word_problems, multi_step, unit_analysis'
    """

    def parse_problem(self, problem_text: str) -> PhysicsProblemSpec:
        """
        Parse physics word problem into structured specification.

        Returns:
            PhysicsProblemSpec with:
            - known_quantities: Dict[str, QuantityValue]
            - unknown_quantities: List[str]
            - domain: str  # 'mechanics', 'em', 'thermo', etc.
            - sub_domain: str  # 'kinematics', 'dynamics', etc.
            - constraints: List[str]
            - assumptions: List[str]
        """
        pass

    def select_equations(self, problem_spec: PhysicsProblemSpec) -> List[str]:
        """
        Select applicable physics equations for the problem.

        Uses knowledge of which equations connect which variables.
        Minimizes number of equations needed.
        """
        pass

    def solve_system(self, equations: List[str],
                     knowns: Dict[str, float],
                     unknowns: List[str]) -> Dict[str, float]:
        """
        Solve system of physics equations.

        Uses:
        1. Direct substitution for single-equation problems
        2. Gaussian elimination for linear systems
        3. Symbolic manipulation for nonlinear systems
        """
        pass

    def generate_solution_steps(self, problem_spec: PhysicsProblemSpec,
                                 solution: Dict[str, float]) -> List[str]:
        """
        Generate human-readable solution steps.

        Shows:
        1. Given quantities
        2. Equations used
        3. Substitution steps
        4. Final answer with units
        """
        pass

    def validate_answer(self, answer: float, quantity: str,
                        problem_context: Dict) -> ValidationResult:
        """
        Validate answer for physical reasonableness.

        Checks:
        - Correct units
        - Reasonable magnitude
        - Sign consistency
        - Conservation law compliance
        """
        pass

    def process(self, task_entry: Any) -> Any:
        """Main BDI processing: Parse -> Select -> Solve -> Validate"""
        pass
```

### 2.5 File Location and Structure

```
src/symbo_agentic_reasoners/agents/specialists/physics/
    equation_solver.py         # Main agent (NEW)
    problem_parser.py          # NLP for physics problems (NEW)
    physics_laws_db.py         # Law database (NEW)
    unit_system.py             # Unit conversion (NEW)
    validation/
        __init__.py
        dimensional_analysis.py  # Unit checking (NEW)
        reasonableness.py        # Value validation (NEW)
```

---

## Agent 3: ConditionMonitor

### 3.1 Agent Name and Purpose

**Agent ID:** `condition_monitor_001`
**Tier:** 3 (Specialist - operates alongside other specialists)
**Service Type:** `math.numerical.stability`

**Purpose:**
The ConditionMonitor tracks numerical stability throughout computations, preventing catastrophic precision loss in linear algebra operations. Current Linear Algebra score (66/100) suffers because operations proceed without checking condition numbers, leading to garbage results on ill-conditioned matrices.

**Gap Addressed:**
When solving Ax=b, if cond(A) > 10^10, the solution is unreliable. Current system doesn't detect this. ConditionMonitor provides real-time stability assessment.

### 3.2 Mathematical Rules (Native, No SymPy)

```python
# =============================================================================
# NUMERICAL STABILITY MONITORING (Native Implementation)
# =============================================================================

class ConditionNumberEstimator:
    """
    Native condition number estimation without external libraries.

    The condition number kappa(A) = ||A|| * ||A^-1||

    For solving Ax = b:
    - kappa(A) ~ 1: Well-conditioned, results reliable
    - kappa(A) ~ 10^3: Moderate conditioning, some precision loss
    - kappa(A) ~ 10^6: Ill-conditioned, significant precision loss
    - kappa(A) ~ 10^15: Near-singular, results unreliable

    Rule of thumb: Lose log10(kappa) digits of precision.
    """

    @staticmethod
    def matrix_norm_1(A: List[List[float]]) -> float:
        """
        1-norm (maximum column sum).
        ||A||_1 = max_j (sum_i |a_ij|)
        """
        n = len(A)
        m = len(A[0]) if A else 0
        return max(sum(abs(A[i][j]) for i in range(n)) for j in range(m))

    @staticmethod
    def matrix_norm_inf(A: List[List[float]]) -> float:
        """
        Infinity-norm (maximum row sum).
        ||A||_inf = max_i (sum_j |a_ij|)
        """
        return max(sum(abs(x) for x in row) for row in A)

    @staticmethod
    def matrix_norm_frobenius(A: List[List[float]]) -> float:
        """
        Frobenius norm.
        ||A||_F = sqrt(sum_ij |a_ij|^2)
        """
        import math
        return math.sqrt(sum(sum(x*x for x in row) for row in A))

    @staticmethod
    def estimate_condition_1(A: List[List[float]]) -> float:
        """
        Estimate condition number using 1-norm.

        Uses iterative refinement to estimate ||A^-1||_1 without
        explicitly computing the inverse.

        Algorithm: LAPACK's DLACON-style estimation
        """
        pass

    @staticmethod
    def estimate_condition_via_svd(A: List[List[float]]) -> float:
        """
        Estimate condition number via SVD: kappa = sigma_max / sigma_min

        Uses power iteration to find largest and smallest singular values.
        """
        pass


class StabilityAdvisor:
    """
    Advise on numerical stability based on condition analysis.
    """

    # Stability thresholds
    WELL_CONDITIONED = 1e3
    MODERATELY_CONDITIONED = 1e6
    ILL_CONDITIONED = 1e10
    NEAR_SINGULAR = 1e14

    @staticmethod
    def assess_stability(condition_number: float) -> Dict[str, Any]:
        """
        Assess stability and provide recommendations.

        Returns:
            Dict with:
            - status: 'stable', 'caution', 'warning', 'unstable'
            - precision_loss: Estimated digits of precision lost
            - recommendation: Suggested action
            - can_proceed: bool
        """
        import math

        digits_lost = math.log10(max(condition_number, 1))

        if condition_number < StabilityAdvisor.WELL_CONDITIONED:
            return {
                'status': 'stable',
                'precision_loss': digits_lost,
                'recommendation': 'Proceed normally',
                'can_proceed': True
            }
        elif condition_number < StabilityAdvisor.MODERATELY_CONDITIONED:
            return {
                'status': 'caution',
                'precision_loss': digits_lost,
                'recommendation': 'Use higher precision if available',
                'can_proceed': True
            }
        elif condition_number < StabilityAdvisor.ILL_CONDITIONED:
            return {
                'status': 'warning',
                'precision_loss': digits_lost,
                'recommendation': 'Consider regularization or preconditioning',
                'can_proceed': True,
                'alternatives': ['tikhonov_regularization', 'iterative_refinement']
            }
        else:
            return {
                'status': 'unstable',
                'precision_loss': digits_lost,
                'recommendation': 'Matrix is effectively singular. Use pseudo-inverse or verify problem setup.',
                'can_proceed': False,
                'alternatives': ['pseudo_inverse', 'least_squares', 'regularization']
            }


class PivotMonitor:
    """
    Monitor pivot quality during Gaussian elimination.
    """

    @staticmethod
    def assess_pivot(pivot: float, row_scale: float,
                     iteration: int) -> Dict[str, Any]:
        """
        Assess pivot quality relative to row scale.

        Small pivots indicate potential instability.

        Returns:
            Dict with pivot quality assessment
        """
        import math

        relative_pivot = abs(pivot) / (row_scale + 1e-300)

        if relative_pivot < 1e-14:
            return {
                'quality': 'critical',
                'relative_size': relative_pivot,
                'recommendation': 'Pivot too small - matrix likely singular',
                'action': 'abort_or_use_pseudoinverse'
            }
        elif relative_pivot < 1e-10:
            return {
                'quality': 'poor',
                'relative_size': relative_pivot,
                'recommendation': 'Pivot is very small - results may be inaccurate',
                'action': 'proceed_with_warning'
            }
        else:
            return {
                'quality': 'good',
                'relative_size': relative_pivot,
                'action': 'proceed'
            }


class IterativeRefinement:
    """
    Iterative refinement to improve solution accuracy.

    Given approximate solution x, compute:
    r = b - Ax (residual)
    Solve Ad = r for correction d
    x_new = x + d

    Repeat until ||r|| < tolerance
    """

    @staticmethod
    def refine_solution(A: List[List[float]], b: List[float],
                        x: List[float], tol: float = 1e-10,
                        max_iter: int = 10) -> Tuple[List[float], int]:
        """
        Refine solution using iterative refinement.

        Returns:
            (refined_solution, iterations_used)
        """
        pass
```

### 3.3 Supervisor Hierarchy Position

```
                    LinearAlgebraSupervisor (Tier 2)
                              |
            +-----------------+-----------------+
            |                 |                 |
    MatrixOpsSpecialist  DecompositionSpec  ConditionMonitor (Tier 3)
         (Tier 3)           (Tier 3)              (NEW)
                                |
                        [Provides stability
                         assessment to all
                         linalg operations]
```

**Integration:**
- ConditionMonitor is consulted BEFORE major linear algebra operations
- Can veto operations that would produce garbage results
- Provides alternative methods when standard approach is unstable
- Tracks stability across chains of operations

### 3.4 Key Methods Exposed

```python
class ConditionMonitor(BDIAgent):
    """
    Tier 3 Numerical Stability Monitoring Agent

    Service Registration:
        service_type: 'math.numerical.stability'
        algorithm: 'condition_estimation'
        cost: 'low'
        tier: '3'
        capabilities: 'condition_number, pivot_monitoring, refinement'
    """

    def estimate_condition(self, matrix: List[List[float]],
                           norm: str = '2') -> float:
        """
        Estimate condition number of matrix.

        Args:
            matrix: Input matrix
            norm: '1', '2', 'inf', or 'fro'

        Returns:
            Estimated condition number
        """
        pass

    def assess_operation_stability(self, operation: str,
                                   operands: Dict[str, Any]) -> StabilityReport:
        """
        Assess stability of proposed operation.

        Args:
            operation: 'solve_system', 'invert', 'eigenvalues', etc.
            operands: Operation inputs (matrices, vectors)

        Returns:
            StabilityReport with:
            - can_proceed: bool
            - estimated_accuracy: float (digits)
            - warnings: List[str]
            - recommendations: List[str]
        """
        pass

    def monitor_elimination(self, pivot: float, iteration: int,
                            row_norms: List[float]) -> PivotAssessment:
        """
        Real-time monitoring during Gaussian elimination.

        Called at each pivot selection to detect instability early.
        """
        pass

    def suggest_preconditioner(self, matrix: List[List[float]]) -> str:
        """
        Suggest preconditioning strategy for ill-conditioned system.

        Options:
        - 'jacobi': Diagonal scaling
        - 'ilu': Incomplete LU
        - 'equilibration': Row/column scaling
        """
        pass

    def apply_iterative_refinement(self, A: List[List[float]],
                                   b: List[float],
                                   x: List[float]) -> List[float]:
        """
        Apply iterative refinement to improve solution accuracy.
        """
        pass

    def process(self, task_entry: Any) -> Any:
        """Main processing: Estimate -> Assess -> Advise"""
        pass
```

### 3.5 File Location and Structure

```
src/symbo_agentic_reasoners/agents/specialists/numerical/
    condition_monitor.py       # Main agent (NEW)
    stability_analysis.py      # Stability assessment (NEW)
    matrix_norms.py            # Norm computations (NEW)
    iterative_refinement.py    # Solution refinement (NEW)
    preconditioners.py         # Preconditioning strategies (NEW)
```

---

## Agent 4: SpecialFunctionEvaluator

### 4.1 Agent Name and Purpose

**Agent ID:** `special_function_evaluator_001`
**Tier:** 3 (Specialist)
**Service Type:** `math.functions.special`

**Purpose:**
The SpecialFunctionEvaluator provides native implementations of special mathematical functions (Bessel, Legendre, Gamma, Beta, etc.) that appear frequently in physics and engineering but are missing from the current system. This directly improves Limits (72/100) and Series (68/100) scores by enabling evaluation of limits and series involving special functions.

**Gap Addressed:**
Current system cannot evaluate `lim(x->0) J_0(x)` (Bessel function) or compute `Gamma(5.5)` because special functions aren't implemented. This agent fills that gap with native implementations.

### 4.2 Mathematical Rules (Native, No SymPy)

```python
# =============================================================================
# SPECIAL FUNCTIONS (Native Implementation)
# =============================================================================

import math
from typing import Union, Tuple, List, Optional
from fractions import Fraction


class GammaFunction:
    """
    Native Gamma function implementation.

    Gamma(n) = (n-1)! for positive integers
    Gamma(z) = integral from 0 to inf of t^(z-1) * e^(-t) dt

    Uses Lanczos approximation for general complex arguments.
    """

    # Lanczos coefficients for g=7
    LANCZOS_COEFF = [
        0.99999999999980993,
        676.5203681218851,
        -1259.1392167224028,
        771.32342877765313,
        -176.61502916214059,
        12.507343278686905,
        -0.13857109526572012,
        9.9843695780195716e-6,
        1.5056327351493116e-7
    ]

    @staticmethod
    def gamma(z: Union[int, float]) -> float:
        """
        Compute Gamma(z) using Lanczos approximation.

        Gamma(z+1) = z * Gamma(z)
        Gamma(1) = 1
        Gamma(1/2) = sqrt(pi)
        """
        if z <= 0 and z == int(z):
            raise ValueError("Gamma undefined for non-positive integers")

        if z < 0.5:
            # Reflection formula: Gamma(z) * Gamma(1-z) = pi / sin(pi*z)
            return math.pi / (math.sin(math.pi * z) * GammaFunction.gamma(1 - z))

        z -= 1
        g = 7
        c = GammaFunction.LANCZOS_COEFF

        x = c[0]
        for i in range(1, g + 2):
            x += c[i] / (z + i)

        t = z + g + 0.5
        return math.sqrt(2 * math.pi) * (t ** (z + 0.5)) * math.exp(-t) * x

    @staticmethod
    def log_gamma(z: float) -> float:
        """
        Compute ln(Gamma(z)) for better numerical stability with large z.
        """
        if z <= 0 and z == int(z):
            raise ValueError("Log gamma undefined for non-positive integers")

        # Stirling's approximation for large z
        if z > 10:
            return (z - 0.5) * math.log(z) - z + 0.5 * math.log(2 * math.pi) + \
                   1/(12*z) - 1/(360*z**3) + 1/(1260*z**5)

        return math.log(abs(GammaFunction.gamma(z)))

    @staticmethod
    def factorial(n: int) -> int:
        """Factorial n! = Gamma(n+1)"""
        if n < 0:
            raise ValueError("Factorial undefined for negative integers")
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result


class BetaFunction:
    """
    Beta function: B(a, b) = Gamma(a) * Gamma(b) / Gamma(a+b)
                          = integral from 0 to 1 of t^(a-1) * (1-t)^(b-1) dt
    """

    @staticmethod
    def beta(a: float, b: float) -> float:
        """Compute Beta(a, b)."""
        return math.exp(GammaFunction.log_gamma(a) +
                        GammaFunction.log_gamma(b) -
                        GammaFunction.log_gamma(a + b))

    @staticmethod
    def incomplete_beta(x: float, a: float, b: float) -> float:
        """
        Incomplete beta function I_x(a, b).
        Uses continued fraction expansion.
        """
        pass


class BesselFunctions:
    """
    Native Bessel function implementations.

    J_n(x): Bessel function of first kind
    Y_n(x): Bessel function of second kind (Weber)
    I_n(x): Modified Bessel function of first kind
    K_n(x): Modified Bessel function of second kind
    """

    @staticmethod
    def bessel_j(n: int, x: float, terms: int = 50) -> float:
        """
        Bessel function of first kind J_n(x).

        Series: J_n(x) = sum_{k=0}^inf (-1)^k / (k! * Gamma(n+k+1)) * (x/2)^(n+2k)

        For |x| < n, use series.
        For |x| >= n, use asymptotic expansion or Miller's algorithm.
        """
        if x == 0:
            return 1.0 if n == 0 else 0.0

        # Series expansion
        result = 0.0
        x_half = x / 2

        for k in range(terms):
            term = ((-1) ** k) / (GammaFunction.factorial(k) *
                                   GammaFunction.gamma(n + k + 1))
            term *= (x_half) ** (n + 2 * k)
            result += term

            # Check convergence
            if abs(term) < 1e-15 * abs(result):
                break

        return result

    @staticmethod
    def bessel_j0(x: float) -> float:
        """J_0(x) - Bessel function of first kind, order 0."""
        return BesselFunctions.bessel_j(0, x)

    @staticmethod
    def bessel_j1(x: float) -> float:
        """J_1(x) - Bessel function of first kind, order 1."""
        return BesselFunctions.bessel_j(1, x)

    @staticmethod
    def bessel_y(n: int, x: float) -> float:
        """
        Bessel function of second kind Y_n(x) (Weber/Neumann function).

        Y_n(x) = (J_n(x) * cos(n*pi) - J_{-n}(x)) / sin(n*pi)

        For integer n, use limit form.
        """
        if x <= 0:
            raise ValueError("Y_n(x) undefined for x <= 0")
        pass

    @staticmethod
    def bessel_i(n: int, x: float, terms: int = 50) -> float:
        """
        Modified Bessel function of first kind I_n(x).

        I_n(x) = sum_{k=0}^inf 1 / (k! * Gamma(n+k+1)) * (x/2)^(n+2k)
        """
        result = 0.0
        x_half = x / 2

        for k in range(terms):
            term = 1 / (GammaFunction.factorial(k) *
                        GammaFunction.gamma(n + k + 1))
            term *= (x_half) ** (n + 2 * k)
            result += term

            if abs(term) < 1e-15 * abs(result):
                break

        return result

    @staticmethod
    def spherical_bessel_j(n: int, x: float) -> float:
        """
        Spherical Bessel function j_n(x).

        j_n(x) = sqrt(pi / (2x)) * J_{n+1/2}(x)

        Special cases:
        j_0(x) = sin(x) / x
        j_1(x) = sin(x)/x^2 - cos(x)/x
        """
        if x == 0:
            return 1.0 if n == 0 else 0.0

        if n == 0:
            return math.sin(x) / x
        elif n == 1:
            return math.sin(x) / (x * x) - math.cos(x) / x
        else:
            # Use recurrence: j_{n+1}(x) = (2n+1)/x * j_n(x) - j_{n-1}(x)
            j_prev = math.sin(x) / x
            j_curr = math.sin(x) / (x * x) - math.cos(x) / x

            for m in range(1, n):
                j_next = (2 * m + 1) / x * j_curr - j_prev
                j_prev = j_curr
                j_curr = j_next

            return j_curr


class LegendrePolynomials:
    """
    Legendre polynomials P_n(x) and associated Legendre functions.

    P_n(x) satisfies: (1-x^2)y'' - 2xy' + n(n+1)y = 0

    Rodrigues formula: P_n(x) = 1/(2^n * n!) * d^n/dx^n [(x^2-1)^n]
    """

    @staticmethod
    def legendre_p(n: int, x: float) -> float:
        """
        Legendre polynomial P_n(x) using recurrence relation.

        P_0(x) = 1
        P_1(x) = x
        (n+1) P_{n+1}(x) = (2n+1) x P_n(x) - n P_{n-1}(x)
        """
        if n == 0:
            return 1.0
        if n == 1:
            return float(x)

        p_prev = 1.0
        p_curr = float(x)

        for k in range(1, n):
            p_next = ((2 * k + 1) * x * p_curr - k * p_prev) / (k + 1)
            p_prev = p_curr
            p_curr = p_next

        return p_curr

    @staticmethod
    def associated_legendre(n: int, m: int, x: float) -> float:
        """
        Associated Legendre function P_n^m(x).

        P_n^m(x) = (-1)^m * (1-x^2)^(m/2) * d^m/dx^m [P_n(x)]
        """
        if abs(x) > 1:
            raise ValueError("Associated Legendre requires |x| <= 1")
        pass

    @staticmethod
    def spherical_harmonic(l: int, m: int,
                           theta: float, phi: float) -> complex:
        """
        Spherical harmonic Y_l^m(theta, phi).

        Y_l^m = sqrt((2l+1)/(4pi) * (l-m)!/(l+m)!) * P_l^m(cos(theta)) * e^(i*m*phi)
        """
        pass


class HermitePolynomials:
    """
    Hermite polynomials H_n(x) - appear in quantum harmonic oscillator.

    H_n(x) satisfies: y'' - 2xy' + 2ny = 0
    """

    @staticmethod
    def hermite(n: int, x: float) -> float:
        """
        Hermite polynomial H_n(x) using recurrence.

        H_0(x) = 1
        H_1(x) = 2x
        H_{n+1}(x) = 2x H_n(x) - 2n H_{n-1}(x)
        """
        if n == 0:
            return 1.0
        if n == 1:
            return 2.0 * x

        h_prev = 1.0
        h_curr = 2.0 * x

        for k in range(1, n):
            h_next = 2 * x * h_curr - 2 * k * h_prev
            h_prev = h_curr
            h_curr = h_next

        return h_curr


class LaguerrePolynomials:
    """
    Laguerre polynomials L_n(x) - appear in hydrogen atom solution.
    """

    @staticmethod
    def laguerre(n: int, x: float) -> float:
        """
        Laguerre polynomial L_n(x) using recurrence.

        L_0(x) = 1
        L_1(x) = 1 - x
        (n+1) L_{n+1}(x) = (2n+1-x) L_n(x) - n L_{n-1}(x)
        """
        if n == 0:
            return 1.0
        if n == 1:
            return 1.0 - x

        l_prev = 1.0
        l_curr = 1.0 - x

        for k in range(1, n):
            l_next = ((2 * k + 1 - x) * l_curr - k * l_prev) / (k + 1)
            l_prev = l_curr
            l_curr = l_next

        return l_curr

    @staticmethod
    def associated_laguerre(n: int, alpha: float, x: float) -> float:
        """Associated Laguerre polynomial L_n^alpha(x)."""
        pass


class ErrorFunction:
    """
    Error function and related functions.

    erf(x) = 2/sqrt(pi) * integral from 0 to x of e^(-t^2) dt
    erfc(x) = 1 - erf(x)
    """

    @staticmethod
    def erf(x: float) -> float:
        """
        Error function erf(x).

        Uses Taylor series for small x, asymptotic expansion for large x.
        """
        # Approximation using Horner's method
        # Abramowitz and Stegun approximation 7.1.26
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911

        sign = 1 if x >= 0 else -1
        x = abs(x)

        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)

        return sign * y

    @staticmethod
    def erfc(x: float) -> float:
        """Complementary error function erfc(x) = 1 - erf(x)."""
        return 1.0 - ErrorFunction.erf(x)


class EllipticIntegrals:
    """
    Elliptic integrals K(k) and E(k).
    """

    @staticmethod
    def elliptic_k(k: float) -> float:
        """
        Complete elliptic integral of first kind K(k).

        K(k) = integral from 0 to pi/2 of 1/sqrt(1 - k^2*sin^2(theta)) d(theta)

        Uses arithmetic-geometric mean for computation.
        """
        if abs(k) >= 1:
            raise ValueError("K(k) undefined for |k| >= 1")

        # AGM method
        a = 1.0
        b = math.sqrt(1 - k * k)

        while abs(a - b) > 1e-15:
            a_new = (a + b) / 2
            b = math.sqrt(a * b)
            a = a_new

        return math.pi / (2 * a)

    @staticmethod
    def elliptic_e(k: float) -> float:
        """
        Complete elliptic integral of second kind E(k).

        E(k) = integral from 0 to pi/2 of sqrt(1 - k^2*sin^2(theta)) d(theta)
        """
        pass
```

### 4.3 Supervisor Hierarchy Position

```
                    CalculusSupervisor (Tier 2)
                           |
         +-----------------+-----------------+
         |                 |                 |
    LimitEvaluator  SeriesSpecialist  SpecialFunctionEvaluator
       (Tier 3)        (Tier 3)            (Tier 3) (NEW)
                                              |
                                    [Provides function values
                                     to limits/series agents]
```

**Integration:**
- Called by LimitEvaluator when limit involves special functions
- Called by SeriesSpecialist for series involving Bessel/Legendre/etc.
- Can be called directly for function evaluation
- Provides derivatives of special functions for calculus operations

### 4.4 Key Methods Exposed

```python
class SpecialFunctionEvaluator(BDIAgent):
    """
    Tier 3 Special Function Evaluation Agent

    Service Registration:
        service_type: 'math.functions.special'
        algorithm: 'native_special_functions'
        cost: 'low'
        tier: '3'
        capabilities: 'bessel,legendre,gamma,beta,erf,elliptic'
    """

    def evaluate(self, func_name: str, *args) -> float:
        """
        Evaluate special function.

        Args:
            func_name: 'gamma', 'bessel_j', 'legendre_p', etc.
            *args: Function arguments

        Returns:
            Function value
        """
        pass

    def derivative(self, func_name: str, *args) -> float:
        """
        Compute derivative of special function.

        Uses known derivative relations, e.g.:
        d/dx J_n(x) = (J_{n-1}(x) - J_{n+1}(x)) / 2
        """
        pass

    def series_expansion(self, func_name: str, x: float,
                         order: int, center: float = 0) -> str:
        """
        Return series expansion of special function.
        """
        pass

    def asymptotic_expansion(self, func_name: str, x: float,
                             direction: str = 'infinity') -> str:
        """
        Return asymptotic expansion for large/small arguments.
        """
        pass

    def list_functions(self) -> List[str]:
        """List all available special functions."""
        return [
            'gamma', 'log_gamma', 'factorial', 'beta',
            'bessel_j', 'bessel_j0', 'bessel_j1', 'bessel_y',
            'bessel_i', 'bessel_k', 'spherical_bessel_j',
            'legendre_p', 'associated_legendre', 'spherical_harmonic',
            'hermite', 'laguerre', 'associated_laguerre',
            'erf', 'erfc', 'elliptic_k', 'elliptic_e'
        ]

    def process(self, task_entry: Any) -> Any:
        """Main processing: Identify function -> Evaluate -> Return"""
        pass
```

### 4.5 File Location and Structure

```
src/symbo_agentic_reasoners/agents/specialists/functions/
    __init__.py
    special_function_evaluator.py  # Main agent (NEW)
    gamma_functions.py             # Gamma, Beta (NEW)
    bessel_functions.py            # All Bessel variants (NEW)
    orthogonal_polynomials.py      # Legendre, Hermite, Laguerre (NEW)
    error_functions.py             # erf, erfc (NEW)
    elliptic_functions.py          # Elliptic integrals (NEW)
```

---

## Agent 5: FourierSeriesAgent

### 5.1 Agent Name and Purpose

**Agent ID:** `fourier_series_agent_001`
**Tier:** 3 (Specialist)
**Service Type:** `math.calculus.fourier`

**Purpose:**
The FourierSeriesAgent handles Fourier analysis including Fourier series computation, Fourier transforms, and convergence analysis. This fills a major gap in the Series score (68/100) where Fourier analysis is currently missing entirely.

**Gap Addressed:**
Current SeriesSpecialist only handles Taylor series. For functions with discontinuities or periodic behavior, Fourier series is essential. Engineers and physicists frequently need Fourier analysis for signal processing and PDE solutions.

### 5.2 Mathematical Rules (Native, No SymPy)

```python
# =============================================================================
# FOURIER ANALYSIS (Native Implementation)
# =============================================================================

import math
from typing import Callable, List, Tuple, Dict, Any, Optional
from fractions import Fraction


class FourierCoefficients:
    """
    Compute Fourier coefficients for periodic functions.

    For function f(x) with period 2L:

    f(x) = a_0/2 + sum_{n=1}^inf [a_n*cos(n*pi*x/L) + b_n*sin(n*pi*x/L)]

    where:
    a_0 = (1/L) * integral from -L to L of f(x) dx
    a_n = (1/L) * integral from -L to L of f(x)*cos(n*pi*x/L) dx
    b_n = (1/L) * integral from -L to L of f(x)*sin(n*pi*x/L) dx
    """

    @staticmethod
    def compute_a0(f: Callable, L: float, num_points: int = 1000) -> float:
        """
        Compute a_0 coefficient using numerical integration.

        a_0 = (1/L) * integral from -L to L of f(x) dx
        """
        # Simpson's rule integration
        h = 2 * L / num_points
        total = f(-L) + f(L)

        for i in range(1, num_points):
            x = -L + i * h
            if i % 2 == 0:
                total += 2 * f(x)
            else:
                total += 4 * f(x)

        integral = (h / 3) * total
        return integral / L

    @staticmethod
    def compute_an(f: Callable, n: int, L: float,
                   num_points: int = 1000) -> float:
        """
        Compute a_n coefficient.

        a_n = (1/L) * integral from -L to L of f(x)*cos(n*pi*x/L) dx
        """
        def integrand(x):
            return f(x) * math.cos(n * math.pi * x / L)

        h = 2 * L / num_points
        total = integrand(-L) + integrand(L)

        for i in range(1, num_points):
            x = -L + i * h
            if i % 2 == 0:
                total += 2 * integrand(x)
            else:
                total += 4 * integrand(x)

        integral = (h / 3) * total
        return integral / L

    @staticmethod
    def compute_bn(f: Callable, n: int, L: float,
                   num_points: int = 1000) -> float:
        """
        Compute b_n coefficient.

        b_n = (1/L) * integral from -L to L of f(x)*sin(n*pi*x/L) dx
        """
        def integrand(x):
            return f(x) * math.sin(n * math.pi * x / L)

        h = 2 * L / num_points
        total = integrand(-L) + integrand(L)

        for i in range(1, num_points):
            x = -L + i * h
            if i % 2 == 0:
                total += 2 * integrand(x)
            else:
                total += 4 * integrand(x)

        integral = (h / 3) * total
        return integral / L

    @staticmethod
    def symbolic_square_wave(L: float, n_terms: int) -> Dict[str, Any]:
        """
        Analytic Fourier series for square wave.

        f(x) = 1 for 0 < x < L, -1 for -L < x < 0

        Series: f(x) = (4/pi) * sum_{n=1,3,5,...} sin(n*pi*x/L) / n
        """
        coefficients = []
        for n in range(1, 2 * n_terms, 2):  # Odd terms only
            coefficients.append({
                'n': n,
                'type': 'sin',
                'coefficient': 4 / (n * math.pi)
            })

        return {
            'a0': 0,
            'series_type': 'odd_function',
            'terms': coefficients,
            'formula': f"(4/pi) * sum_{{n=1,3,5,...}} sin(n*pi*x/{L}) / n"
        }

    @staticmethod
    def symbolic_sawtooth(L: float, n_terms: int) -> Dict[str, Any]:
        """
        Analytic Fourier series for sawtooth wave.

        f(x) = x/L for -L < x < L

        Series: f(x) = (2/pi) * sum_{n=1}^inf (-1)^{n+1} * sin(n*pi*x/L) / n
        """
        coefficients = []
        for n in range(1, n_terms + 1):
            coefficients.append({
                'n': n,
                'type': 'sin',
                'coefficient': 2 * ((-1) ** (n + 1)) / (n * math.pi)
            })

        return {
            'a0': 0,
            'series_type': 'odd_function',
            'terms': coefficients
        }

    @staticmethod
    def symbolic_triangle_wave(L: float, n_terms: int) -> Dict[str, Any]:
        """
        Analytic Fourier series for triangle wave.

        f(x) = |x| for -L < x < L

        Series: f(x) = L/2 - (4L/pi^2) * sum_{n=1,3,5,...} cos(n*pi*x/L) / n^2
        """
        coefficients = []
        for n in range(1, 2 * n_terms, 2):  # Odd terms only
            coefficients.append({
                'n': n,
                'type': 'cos',
                'coefficient': -4 * L / (n * n * math.pi * math.pi)
            })

        return {
            'a0': L,
            'series_type': 'even_function',
            'terms': coefficients
        }


class FourierTransform:
    """
    Discrete and continuous Fourier transforms.
    """

    @staticmethod
    def dft(signal: List[float]) -> List[complex]:
        """
        Discrete Fourier Transform.

        X[k] = sum_{n=0}^{N-1} x[n] * e^{-2*pi*i*k*n/N}

        Time complexity: O(N^2)
        """
        N = len(signal)
        result = []

        for k in range(N):
            total = 0 + 0j
            for n in range(N):
                angle = -2 * math.pi * k * n / N
                total += signal[n] * (math.cos(angle) + 1j * math.sin(angle))
            result.append(total)

        return result

    @staticmethod
    def fft(signal: List[float]) -> List[complex]:
        """
        Fast Fourier Transform using Cooley-Tukey algorithm.

        Time complexity: O(N log N)
        Requires N to be power of 2.
        """
        N = len(signal)

        # Base case
        if N == 1:
            return [complex(signal[0])]

        # Check power of 2
        if N & (N - 1) != 0:
            # Pad to next power of 2
            next_pow2 = 1
            while next_pow2 < N:
                next_pow2 *= 2
            signal = signal + [0.0] * (next_pow2 - N)
            N = next_pow2

        # Split into even and odd
        even = FourierTransform.fft(signal[0::2])
        odd = FourierTransform.fft(signal[1::2])

        # Combine
        result = [0j] * N
        for k in range(N // 2):
            angle = -2 * math.pi * k / N
            twiddle = math.cos(angle) + 1j * math.sin(angle)

            result[k] = even[k] + twiddle * odd[k]
            result[k + N // 2] = even[k] - twiddle * odd[k]

        return result

    @staticmethod
    def ifft(spectrum: List[complex]) -> List[complex]:
        """
        Inverse FFT.

        x[n] = (1/N) * sum_{k=0}^{N-1} X[k] * e^{2*pi*i*k*n/N}
        """
        N = len(spectrum)

        # Conjugate, FFT, conjugate, scale
        conjugated = [z.conjugate() for z in spectrum]
        transformed = FourierTransform.fft([z.real for z in conjugated])  # Simplified
        result = [z.conjugate() / N for z in transformed]

        return result


class FourierConvergence:
    """
    Analyze convergence of Fourier series.
    """

    @staticmethod
    def pointwise_convergence_test(f: Callable, x: float, L: float,
                                    n_terms: int) -> Dict[str, Any]:
        """
        Test pointwise convergence at a specific point.

        At points where f is continuous, Fourier series converges to f(x).
        At jump discontinuities, converges to (f(x+) + f(x-))/2.
        """
        a0 = FourierCoefficients.compute_a0(f, L)

        partial_sums = []
        current_sum = a0 / 2

        for n in range(1, n_terms + 1):
            an = FourierCoefficients.compute_an(f, n, L)
            bn = FourierCoefficients.compute_bn(f, n, L)

            term = an * math.cos(n * math.pi * x / L) + \
                   bn * math.sin(n * math.pi * x / L)
            current_sum += term

            partial_sums.append({
                'n': n,
                'partial_sum': current_sum,
                'error': abs(current_sum - f(x)) if callable(f) else None
            })

        return {
            'x': x,
            'f_x': f(x),
            'series_value': current_sum,
            'partial_sums': partial_sums,
            'convergence_rate': 'analyzing...'
        }

    @staticmethod
    def gibbs_phenomenon_analysis(f: Callable, discontinuity: float,
                                   L: float, n_terms: int) -> Dict[str, Any]:
        """
        Analyze Gibbs phenomenon near discontinuity.

        At jump discontinuities, Fourier series overshoots by about 9%.
        """
        # Sample near discontinuity
        samples = []
        for n in [10, 50, 100, 500]:
            if n > n_terms:
                break

            # Evaluate just to the right of discontinuity
            x = discontinuity + L / (10 * n)
            partial_sum = FourierCoefficients.compute_a0(f, L) / 2

            for k in range(1, n + 1):
                an = FourierCoefficients.compute_an(f, k, L)
                bn = FourierCoefficients.compute_bn(f, k, L)
                partial_sum += an * math.cos(k * math.pi * x / L) + \
                              bn * math.sin(k * math.pi * x / L)

            samples.append({
                'n_terms': n,
                'x': x,
                'series_value': partial_sum,
                'expected_overshoot': 0.0895  # Gibbs constant ~ 8.95%
            })

        return {
            'discontinuity_at': discontinuity,
            'samples': samples,
            'gibbs_constant': 0.0895,
            'note': 'Overshoot does not decrease with more terms, only gets narrower'
        }

    @staticmethod
    def l2_convergence(f: Callable, L: float, n_terms: int,
                       num_points: int = 100) -> Dict[str, Any]:
        """
        Analyze L2 (mean square) convergence.

        ||f - S_n||_2 -> 0 as n -> infinity
        for all square-integrable functions.
        """
        errors = []

        for n in range(1, n_terms + 1):
            # Compute L2 error
            l2_error_sq = 0
            h = 2 * L / num_points

            for i in range(num_points + 1):
                x = -L + i * h

                # Compute partial sum
                partial_sum = FourierCoefficients.compute_a0(f, L) / 2
                for k in range(1, n + 1):
                    an = FourierCoefficients.compute_an(f, k, L)
                    bn = FourierCoefficients.compute_bn(f, k, L)
                    partial_sum += an * math.cos(k * math.pi * x / L) + \
                                  bn * math.sin(k * math.pi * x / L)

                l2_error_sq += (f(x) - partial_sum) ** 2

            l2_error = math.sqrt(l2_error_sq * h)
            errors.append({'n': n, 'l2_error': l2_error})

        return {
            'errors': errors,
            'converges': errors[-1]['l2_error'] < errors[0]['l2_error']
        }


class CommonFourierSeries:
    """
    Symbolic Fourier series for common functions.
    """

    KNOWN_SERIES = {
        'square_wave': {
            'formula': '(4/pi) * sum_{n=1,3,5,...}^inf sin(nx)/n',
            'a0': 0,
            'an': 0,
            'bn': '4/(n*pi) for odd n, 0 for even n',
            'convergence': 'pointwise except at discontinuities'
        },
        'sawtooth': {
            'formula': '(2/pi) * sum_{n=1}^inf (-1)^{n+1} * sin(nx)/n',
            'a0': 0,
            'an': 0,
            'bn': '2*(-1)^{n+1}/(n*pi)',
            'convergence': 'pointwise except at discontinuities'
        },
        'triangle_wave': {
            'formula': '(8/pi^2) * sum_{n=1,3,5,...}^inf (-1)^{(n-1)/2} * sin(nx)/n^2',
            'a0': 0,
            'an': 0,
            'bn': '8*(-1)^{(n-1)/2}/(n^2*pi^2) for odd n',
            'convergence': 'uniform'
        },
        'parabola': {
            'formula': 'pi^2/3 + 4*sum_{n=1}^inf (-1)^n * cos(nx)/n^2',
            'a0': '2*pi^2/3',
            'an': '4*(-1)^n/n^2',
            'bn': 0,
            'convergence': 'uniform'
        },
        'full_wave_rectifier': {
            'formula': '2/pi - (4/pi) * sum_{n=1}^inf cos(2nx)/(4n^2-1)',
            'a0': '4/pi',
            'an': '-4/(pi*(4n^2-1))',
            'bn': 0,
            'convergence': 'uniform'
        }
    }

    @staticmethod
    def get_series(function_name: str, period: float = 2 * math.pi,
                   n_terms: int = 10) -> Dict[str, Any]:
        """Get Fourier series for known function."""
        if function_name not in CommonFourierSeries.KNOWN_SERIES:
            return {'error': f'Unknown function: {function_name}'}

        info = CommonFourierSeries.KNOWN_SERIES[function_name]
        return {
            'function': function_name,
            'period': period,
            **info
        }
```

### 5.3 Supervisor Hierarchy Position

```
                    CalculusSupervisor (Tier 2)
                           |
         +-----------------+-----------------+
         |                 |                 |
    SeriesSpecialist  FourierSeriesAgent  LimitEvaluator
       (Tier 3)          (Tier 3)           (Tier 3)
         |                  NEW
    [Taylor only]      [Fourier series,
                        transforms,
                        convergence]
```

**Routing Logic:**
1. CalculusSupervisor detects "fourier" keyword -> routes to FourierSeriesAgent
2. SeriesSpecialist for general series may delegate to FourierSeriesAgent for periodic functions
3. Can be called directly for FFT computations

### 5.4 Key Methods Exposed

```python
class FourierSeriesAgent(BDIAgent):
    """
    Tier 3 Fourier Analysis Agent

    Service Registration:
        service_type: 'math.calculus.fourier'
        algorithm: 'fourier_analysis'
        cost: 'medium'
        tier: '3'
        capabilities: 'fourier_series,fft,convergence_analysis'
    """

    def compute_fourier_series(self, f: Callable, L: float,
                                n_terms: int) -> FourierSeriesResult:
        """
        Compute Fourier series coefficients.

        Returns:
            FourierSeriesResult with:
            - a0: DC component
            - an: List of cosine coefficients
            - bn: List of sine coefficients
            - formula: Symbolic representation
        """
        pass

    def evaluate_series(self, coefficients: Dict, x: float,
                        L: float) -> float:
        """
        Evaluate Fourier series at point x.
        """
        pass

    def compute_fft(self, signal: List[float]) -> List[complex]:
        """
        Compute Fast Fourier Transform.
        """
        pass

    def compute_ifft(self, spectrum: List[complex]) -> List[complex]:
        """
        Compute Inverse FFT.
        """
        pass

    def analyze_convergence(self, f: Callable, L: float,
                            n_terms: int) -> ConvergenceReport:
        """
        Analyze convergence properties.

        Returns:
            ConvergenceReport with:
            - convergence_type: 'uniform', 'pointwise', 'L2'
            - rate: Convergence rate estimate
            - gibbs: Whether Gibbs phenomenon occurs
            - discontinuities: List of jump points
        """
        pass

    def get_known_series(self, function_type: str) -> Dict[str, Any]:
        """
        Get symbolic Fourier series for known functions.

        Args:
            function_type: 'square_wave', 'sawtooth', 'triangle', etc.
        """
        pass

    def power_spectrum(self, signal: List[float]) -> List[float]:
        """
        Compute power spectrum |X[k]|^2.
        """
        pass

    def process(self, task_entry: Any) -> Any:
        """Main processing: Identify task -> Compute -> Return"""
        pass
```

### 5.5 File Location and Structure

```
src/symbo_agentic_reasoners/agents/specialists/calculus/
    fourier/
        __init__.py
        fourier_series_agent.py    # Main agent (NEW)
        fourier_coefficients.py    # Coefficient computation (NEW)
        fourier_transform.py       # DFT/FFT implementation (NEW)
        convergence_analysis.py    # Convergence tests (NEW)
        known_series.py            # Library of known series (NEW)
```

---

## Implementation Priority

Based on impact analysis:

| Priority | Agent | Expected Score Improvement | Effort |
|----------|-------|---------------------------|--------|
| 1 | PhysicsEquationSolver | +36 (44 -> 80) | High |
| 2 | ODEMethodSelector | +30 (55 -> 85) | High |
| 3 | FourierSeriesAgent | +20 (68 -> 88) | Medium |
| 4 | SpecialFunctionEvaluator | +18 (72 -> 90) | Medium |
| 5 | ConditionMonitor | +24 (66 -> 90) | Low |

**Recommended Implementation Order:**
1. **ConditionMonitor** - Low effort, immediate stability improvement
2. **SpecialFunctionEvaluator** - Enables other improvements
3. **FourierSeriesAgent** - Completes series capability
4. **ODEMethodSelector** - Major ODE improvement
5. **PhysicsEquationSolver** - Largest impact, requires most integration

---

## Integration Requirements

### Directory Facilitator Registrations

Each agent must register with appropriate service types:

```python
# ODEMethodSelector
service_type='math.calculus.ode.routing'

# PhysicsEquationSolver
service_type='math.physics.solver'

# ConditionMonitor
service_type='math.numerical.stability'

# SpecialFunctionEvaluator
service_type='math.functions.special'

# FourierSeriesAgent
service_type='math.calculus.fourier'
```

### Blackboard Tags

Standard tags for task routing:

```python
# ODE tasks
tags=['ode', 'differential_equation', 'calculus']

# Physics tasks
tags=['physics', 'mechanics', 'em', 'thermo', 'word_problem']

# Stability checks
tags=['matrix', 'stability', 'condition_number']

# Special functions
tags=['special_function', 'bessel', 'legendre', 'gamma']

# Fourier tasks
tags=['fourier', 'series', 'fft', 'spectrum']
```

### Cross-Agent Dependencies

```
ODEMethodSelector
  -> uses SpecialFunctionEvaluator (for Bessel/Legendre ODEs)
  -> uses ConditionMonitor (for stiffness assessment)

PhysicsEquationSolver
  -> uses AlgebraSupervisor (equation manipulation)
  -> uses CalculusSupervisor (derivatives/integrals)
  -> uses ODEMethodSelector (when physics leads to ODE)

FourierSeriesAgent
  -> uses SpecialFunctionEvaluator (for special function series)
  -> uses IntegrationSpecialist (coefficient computation)

ConditionMonitor
  -> used by MatrixOperationsSpecialist
  -> used by DecompositionSpecialist
  -> used by ODEMethodSelector (stiffness)
```

---

## Validation Criteria

Each agent should pass these tests before deployment:

### ODEMethodSelector
- [ ] Correctly classifies 10+ ODE types
- [ ] Routes to appropriate solver 95% of time
- [ ] Detects stiffness with < 10% false negative rate

### PhysicsEquationSolver
- [ ] Solves 20+ standard physics word problems
- [ ] Correct unit handling for all SI units
- [ ] Validates answer reasonableness

### ConditionMonitor
- [ ] Accurate condition estimates to within 10x
- [ ] Correctly identifies ill-conditioned matrices
- [ ] Provides useful recommendations

### SpecialFunctionEvaluator
- [ ] Bessel J_0, J_1 accurate to 10 digits
- [ ] Gamma function accurate to 10 digits
- [ ] Legendre polynomials exact for n < 20

### FourierSeriesAgent
- [ ] FFT matches DFT to 10 digits
- [ ] Correct coefficients for known waveforms
- [ ] Proper Gibbs phenomenon analysis

---

## Document Metadata

- **Created:** 2025-12-14
- **Author:** Agent Architect (Claude)
- **Version:** 1.0
- **Status:** PROPOSED
- **Review Required:** Yes

---

*This document is part of the Symbo Agentic Reasoners system architecture documentation.*
