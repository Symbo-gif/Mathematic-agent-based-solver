"""
Research-Grade Mathematical Equations for Stress Testing
600 equations covering calculus, algebra, number theory, statistics,
differential equations, geometry, physics, and theoretical mathematics.

Compiled from MIT Integration Bee, Putnam Competition, and research-level mathematics.
"""

# =============================================================================
# CATEGORY 1: DEFINITE INTEGRALS (100 equations)
# =============================================================================

DEFINITE_INTEGRALS = [
    # Gaussian and Exponential Integrals (1-20)
    "integrate(exp(-x**2), (x, -oo, oo))",  # sqrt(pi)
    "integrate(exp(-x**2/2), (x, -oo, oo))",  # sqrt(2*pi)
    "integrate(x**2 * exp(-x**2), (x, -oo, oo))",  # sqrt(pi)/2
    "integrate(x**4 * exp(-x**2), (x, -oo, oo))",  # 3*sqrt(pi)/4
    "integrate(exp(-x**2) * cos(x), (x, -oo, oo))",  # sqrt(pi)*exp(-1/4)
    "integrate(exp(-x**2 - y**2), (x, -oo, oo), (y, -oo, oo))",  # pi
    "integrate(exp(-abs(x)), (x, -oo, oo))",  # 2
    "integrate(x * exp(-x), (x, 0, oo))",  # 1
    "integrate(x**2 * exp(-x), (x, 0, oo))",  # 2
    "integrate(x**3 * exp(-x), (x, 0, oo))",  # 6
    "integrate(exp(-x) * sin(x), (x, 0, oo))",  # 1/2
    "integrate(exp(-x) * cos(x), (x, 0, oo))",  # 1/2
    "integrate(exp(-x**2) * sin(x**2), (x, 0, oo))",  # complex
    "integrate(exp(-a*x**2), (x, 0, oo))",  # sqrt(pi)/(2*sqrt(a))
    "integrate(x * exp(-a*x**2), (x, 0, oo))",  # 1/(2*a)
    "integrate(exp(-x) / x, (x, 1, oo))",  # Exponential integral
    "integrate(exp(-x**2) / x**2, (x, 1, oo))",  # special
    "integrate(exp(-x) * log(x), (x, 0, oo))",  # -gamma (Euler-Mascheroni)
    "integrate(exp(-x**2) * log(x), (x, 0, oo))",  # special
    "integrate(x**n * exp(-x), (x, 0, oo))",  # n! (Gamma function)

    # Trigonometric Integrals (21-40)
    "integrate(sin(x)/x, (x, 0, oo))",  # pi/2
    "integrate(sin(x)**2/x**2, (x, 0, oo))",  # pi/2
    "integrate(sin(x)**3/x**3, (x, 0, oo))",  # 3*pi/8
    "integrate(sin(x)**4/x**4, (x, 0, oo))",  # pi/3
    "integrate(sin(x) * cos(x) / x, (x, 0, oo))",  # pi/4
    "integrate(sin(a*x) / x, (x, 0, oo))",  # pi/2 * sign(a)
    "integrate(sin(x)**2 / x, (x, 0, oo))",  # diverges logarithmically
    "integrate((1 - cos(x)) / x**2, (x, 0, oo))",  # pi/2
    "integrate(sin(x**2), (x, 0, oo))",  # sqrt(pi/8) Fresnel
    "integrate(cos(x**2), (x, 0, oo))",  # sqrt(pi/8) Fresnel
    "integrate(sin(x) / (1 + x**2), (x, 0, oo))",  # special
    "integrate(cos(x) / (1 + x**2), (x, 0, oo))",  # pi*exp(-1)/(2)
    "integrate(sin(x)**2, (x, 0, pi))",  # pi/2
    "integrate(cos(x)**2, (x, 0, pi))",  # pi/2
    "integrate(sin(x)**4, (x, 0, pi))",  # 3*pi/8
    "integrate(cos(x)**4, (x, 0, pi))",  # 3*pi/8
    "integrate(sin(x)**2 * cos(x)**2, (x, 0, pi))",  # pi/8
    "integrate(sin(2*x) * sin(3*x), (x, 0, pi))",  # 0
    "integrate(cos(2*x) * cos(3*x), (x, 0, pi))",  # 0
    "integrate(sin(n*x) * sin(m*x), (x, 0, pi))",  # 0 or pi/2

    # Logarithmic Integrals (41-60)
    "integrate(log(x), (x, 0, 1))",  # -1
    "integrate(log(x)**2, (x, 0, 1))",  # 2
    "integrate(log(x)**3, (x, 0, 1))",  # -6
    "integrate(x * log(x), (x, 0, 1))",  # -1/4
    "integrate(x**2 * log(x), (x, 0, 1))",  # -1/9
    "integrate(log(1 + x) / x, (x, 0, 1))",  # pi**2/12
    "integrate(log(1 - x) / x, (x, 0, 1))",  # -pi**2/6
    "integrate(log(x) / (1 + x), (x, 0, 1))",  # -pi**2/12
    "integrate(log(x) / (1 - x), (x, 0, 1))",  # -pi**2/6
    "integrate(log(x) * log(1 - x), (x, 0, 1))",  # 2 - pi**2/6
    "integrate(log(sin(x)), (x, 0, pi/2))",  # -pi*log(2)/2
    "integrate(log(cos(x)), (x, 0, pi/2))",  # -pi*log(2)/2
    "integrate(x * log(sin(x)), (x, 0, pi/2))",  # special
    "integrate(log(1 + sin(x)), (x, 0, pi/2))",  # special
    "integrate(log(1 + cos(x)), (x, 0, pi/2))",  # special
    "integrate(log(x) / sqrt(1 - x**2), (x, 0, 1))",  # -pi*log(2)/2
    "integrate(log(x) / sqrt(x), (x, 0, 1))",  # -4
    "integrate(log(x)**2 / sqrt(x), (x, 0, 1))",  # 8
    "integrate(log(x) / (x**2 + 1), (x, 0, oo))",  # 0
    "integrate(log(x)**2 / (x**2 + 1), (x, 0, oo))",  # pi**3/8

    # Rational Function Integrals (61-80)
    "integrate(1/(x**2 + 1), (x, -oo, oo))",  # pi
    "integrate(1/(x**2 + a**2), (x, -oo, oo))",  # pi/a
    "integrate(1/(x**4 + 1), (x, -oo, oo))",  # pi/sqrt(2)
    "integrate(1/(x**4 + a**4), (x, -oo, oo))",  # pi/(a**3*sqrt(2))
    "integrate(x**2/(x**4 + 1), (x, -oo, oo))",  # pi/sqrt(2)
    "integrate(1/(x**6 + 1), (x, -oo, oo))",  # 2*pi/3
    "integrate(1/((x**2 + 1)*(x**2 + 4)), (x, -oo, oo))",  # pi/6
    "integrate(1/((x**2 + 1)**2), (x, -oo, oo))",  # pi/2
    "integrate(x**2/((x**2 + 1)**2), (x, -oo, oo))",  # pi/2
    "integrate(1/((x**2 + 1)**3), (x, -oo, oo))",  # 3*pi/8
    "integrate(1/(x**2 - 1), (x, 2, 3))",  # log((2*3)/(1*4))/2
    "integrate(x/(x**2 - 1), (x, 2, 3))",  # log(8/3)/2
    "integrate(1/(x**3 + 1), (x, 0, oo))",  # 2*pi/(3*sqrt(3))
    "integrate(1/(x**3 - 1), (x, 2, oo))",  # special
    "integrate(x/(x**4 + 1), (x, 0, oo))",  # pi/4
    "integrate(1/(x**2 + x + 1), (x, 0, oo))",  # 2*pi/(3*sqrt(3))
    "integrate(x/(x**2 + x + 1), (x, 0, oo))",  # diverges
    "integrate(1/(x**4 + x**2 + 1), (x, 0, oo))",  # pi/(2*sqrt(3))
    "integrate(1/sqrt(x**2 + 1), (x, 0, 1))",  # asinh(1)
    "integrate(1/sqrt(x**2 - 1), (x, 2, 3))",  # special

    # Integration by Parts / Reduction (81-100)
    "integrate(x * sin(x), (x, 0, pi))",  # pi
    "integrate(x * cos(x), (x, 0, pi))",  # -2
    "integrate(x**2 * sin(x), (x, 0, pi))",  # pi**2 - 4
    "integrate(x**2 * cos(x), (x, 0, pi))",  # -2*pi
    "integrate(x**3 * sin(x), (x, 0, pi))",  # special
    "integrate(x * exp(x), (x, 0, 1))",  # 1
    "integrate(x**2 * exp(x), (x, 0, 1))",  # e - 2
    "integrate(x**3 * exp(x), (x, 0, 1))",  # 6 - 2e
    "integrate(x * log(x), (x, 1, e))",  # (e**2 + 1)/4
    "integrate(x**2 * log(x), (x, 1, e))",  # special
    "integrate(log(x)**2, (x, 1, e))",  # e - 2
    "integrate(x * arctan(x), (x, 0, 1))",  # (pi - 2 + 2*log(2))/4
    "integrate(x * arcsin(x), (x, 0, 1))",  # pi/4 - 1/2
    "integrate(arctan(x), (x, 0, 1))",  # pi/4 - log(2)/2
    "integrate(arcsin(x), (x, 0, 1))",  # pi/2 - 1
    "integrate(arccos(x), (x, 0, 1))",  # 1
    "integrate(x / (exp(x) - 1), (x, 0, oo))",  # pi**2/6
    "integrate(x**2 / (exp(x) - 1), (x, 0, oo))",  # 2*zeta(3)
    "integrate(x**3 / (exp(x) - 1), (x, 0, oo))",  # pi**4/15
    "integrate(x / (exp(x) + 1), (x, 0, oo))",  # pi**2/12
]

# =============================================================================
# CATEGORY 2: INDEFINITE INTEGRALS (50 equations)
# =============================================================================

INDEFINITE_INTEGRALS = [
    # Basic Integrals
    "integrate(x**n, x)",
    "integrate(1/x, x)",
    "integrate(exp(x), x)",
    "integrate(sin(x), x)",
    "integrate(cos(x), x)",
    "integrate(tan(x), x)",
    "integrate(sec(x), x)",
    "integrate(csc(x), x)",
    "integrate(cot(x), x)",
    "integrate(sec(x)**2, x)",

    # Exponential and Log
    "integrate(exp(a*x), x)",
    "integrate(x * exp(x), x)",
    "integrate(x**2 * exp(x), x)",
    "integrate(exp(x) * sin(x), x)",
    "integrate(exp(x) * cos(x), x)",
    "integrate(log(x), x)",
    "integrate(x * log(x), x)",
    "integrate(log(x)**2, x)",
    "integrate(1/(x * log(x)), x)",
    "integrate(log(log(x)) / x, x)",

    # Trigonometric
    "integrate(sin(x)**2, x)",
    "integrate(cos(x)**2, x)",
    "integrate(sin(x)**3, x)",
    "integrate(cos(x)**3, x)",
    "integrate(sin(x)**4, x)",
    "integrate(tan(x)**2, x)",
    "integrate(sec(x)**3, x)",
    "integrate(sin(x) * cos(x), x)",
    "integrate(sin(2*x) * cos(3*x), x)",
    "integrate(1/(1 + sin(x)), x)",

    # Rational Functions
    "integrate(1/(x**2 + 1), x)",
    "integrate(1/(x**2 - 1), x)",
    "integrate(x/(x**2 + 1), x)",
    "integrate(1/(x**2 + a**2), x)",
    "integrate(1/((x - 1)*(x - 2)), x)",
    "integrate(x/((x - 1)*(x - 2)), x)",
    "integrate(1/(x**3 + 1), x)",
    "integrate(x/(x**4 + 1), x)",
    "integrate(1/(x**2 + x + 1), x)",
    "integrate(x/(x**2 + x + 1), x)",

    # Radical Functions
    "integrate(sqrt(x), x)",
    "integrate(1/sqrt(x), x)",
    "integrate(sqrt(1 - x**2), x)",
    "integrate(1/sqrt(1 - x**2), x)",
    "integrate(sqrt(x**2 + 1), x)",
    "integrate(1/sqrt(x**2 + 1), x)",
    "integrate(sqrt(x**2 - 1), x)",
    "integrate(x * sqrt(1 - x**2), x)",
    "integrate(x / sqrt(1 + x**2), x)",
    "integrate(1/(x * sqrt(x**2 - 1)), x)",
]

# =============================================================================
# CATEGORY 3: INFINITE SERIES (100 equations)
# =============================================================================

INFINITE_SERIES = [
    # Convergent Geometric Series
    "summation((1/2)**n, (n, 0, oo))",  # 2
    "summation((1/3)**n, (n, 0, oo))",  # 3/2
    "summation((2/3)**n, (n, 0, oo))",  # 3
    "summation((1/4)**n, (n, 1, oo))",  # 1/3
    "summation((-1/2)**n, (n, 0, oo))",  # 2/3
    "summation((3/4)**n, (n, 0, oo))",  # 4
    "summation(2**(-n), (n, 1, oo))",  # 1
    "summation(3**(-n), (n, 1, oo))",  # 1/2
    "summation((1/10)**n, (n, 0, oo))",  # 10/9
    "summation(r**n, (n, 0, oo))",  # 1/(1-r) for |r|<1

    # Exponential Series
    "summation(1/factorial(n), (n, 0, oo))",  # e
    "summation((-1)**n/factorial(n), (n, 0, oo))",  # 1/e
    "summation(2**n/factorial(n), (n, 0, oo))",  # e^2
    "summation((-1)**n * 2**n/factorial(n), (n, 0, oo))",  # e^(-2)
    "summation(x**n/factorial(n), (n, 0, oo))",  # e^x
    "summation(5**n/factorial(n), (n, 0, oo))",  # e^5
    "summation(n/factorial(n), (n, 1, oo))",  # e
    "summation(n**2/factorial(n), (n, 0, oo))",  # 2e
    "summation((n+1)/factorial(n), (n, 0, oo))",  # 2e
    "summation(1/factorial(2*n), (n, 0, oo))",  # cosh(1)

    # Zeta Function and p-Series
    "summation(1/n**2, (n, 1, oo))",  # pi^2/6
    "summation(1/n**3, (n, 1, oo))",  # zeta(3) Apery
    "summation(1/n**4, (n, 1, oo))",  # pi^4/90
    "summation(1/n**5, (n, 1, oo))",  # zeta(5)
    "summation(1/n**6, (n, 1, oo))",  # pi^6/945
    "summation((-1)**(n+1)/n**2, (n, 1, oo))",  # pi^2/12
    "summation((-1)**(n+1)/n**3, (n, 1, oo))",  # 3*zeta(3)/4
    "summation((-1)**(n+1)/n**4, (n, 1, oo))",  # 7*pi^4/720
    "summation(1/(2*n-1)**2, (n, 1, oo))",  # pi^2/8
    "summation(1/(2*n-1)**4, (n, 1, oo))",  # pi^4/96

    # Alternating Series
    "summation((-1)**n/n, (n, 1, oo))",  # -log(2)
    "summation((-1)**n/(2*n+1), (n, 0, oo))",  # pi/4 (Leibniz)
    "summation((-1)**n/(2*n+1)**3, (n, 0, oo))",  # pi^3/32
    "summation((-1)**(n+1) * n/(n+1), (n, 1, oo))",  # 1 - log(2)
    "summation((-1)**n * x**n, (n, 0, oo))",  # 1/(1+x)
    "summation((-1)**n * x**(2*n), (n, 0, oo))",  # 1/(1+x^2)
    "summation((-1)**n * x**(2*n+1)/(2*n+1), (n, 0, oo))",  # arctan(x)
    "summation((-1)**n/(3*n+1), (n, 0, oo))",  # special
    "summation((-1)**n/(4*n+1), (n, 0, oo))",  # special
    "summation((-1)**n * n**2/2**n, (n, 1, oo))",  # special

    # Telescoping and Partial Fractions
    "summation(1/(n*(n+1)), (n, 1, oo))",  # 1
    "summation(1/(n*(n+2)), (n, 1, oo))",  # 3/4
    "summation(1/(n*(n+1)*(n+2)), (n, 1, oo))",  # 1/4
    "summation(1/((2*n-1)*(2*n+1)), (n, 1, oo))",  # 1/2
    "summation(1/((3*n-2)*(3*n+1)), (n, 1, oo))",  # 1/3
    "summation(n/(n+1)!, (n, 1, oo))",  # 1
    "summation(1/(n**2 - 1), (n, 2, oo))",  # 3/4
    "summation(1/(4*n**2 - 1), (n, 1, oo))",  # 1/2
    "summation((2*n+1)/(n**2*(n+1)**2), (n, 1, oo))",  # 1
    "summation(1/(n*(n+1)**2), (n, 1, oo))",  # 2 - pi^2/6

    # Power Series
    "summation(x**n/n, (n, 1, oo))",  # -log(1-x)
    "summation(x**(2*n)/(2*n), (n, 1, oo))",  # -log(1-x^2)/2
    "summation(x**n/n**2, (n, 1, oo))",  # Li_2(x)
    "summation(n * x**n, (n, 1, oo))",  # x/(1-x)^2
    "summation(n**2 * x**n, (n, 1, oo))",  # x(1+x)/(1-x)^3
    "summation(x**(2*n+1)/(2*n+1), (n, 0, oo))",  # arctanh(x)
    "summation((-1)**n * x**(2*n)/(2*n)!, (n, 0, oo))",  # cos(x)
    "summation((-1)**n * x**(2*n+1)/(2*n+1)!, (n, 0, oo))",  # sin(x)
    "summation(x**(2*n)/(2*n)!, (n, 0, oo))",  # cosh(x)
    "summation(x**(2*n+1)/(2*n+1)!, (n, 0, oo))",  # sinh(x)

    # Divergent Series Tests
    "summation(1/n, (n, 1, oo))",  # divergent (harmonic)
    "summation(1/sqrt(n), (n, 1, oo))",  # divergent (p=1/2)
    "summation(n/(n+1), (n, 1, oo))",  # divergent (limit != 0)
    "summation((n+1)/n, (n, 1, oo))",  # divergent
    "summation(1/log(n), (n, 2, oo))",  # divergent
    "summation(n**2/(n**3+1), (n, 1, oo))",  # divergent
    "summation((2*n+1)/(3*n+2), (n, 1, oo))",  # divergent (limit = 2/3)
    "summation(sin(1/n), (n, 1, oo))",  # divergent (compare 1/n)
    "summation(1/(n * log(n)), (n, 2, oo))",  # divergent
    "summation((-1)**n * n, (n, 1, oo))",  # divergent (oscillating)

    # Special Series
    "summation(1/(n * 2**n), (n, 1, oo))",  # log(2)
    "summation(1/(n**2 * 2**n), (n, 1, oo))",  # pi^2/12 - log(2)^2/2
    "summation(n/2**n, (n, 1, oo))",  # 2
    "summation(n**2/2**n, (n, 1, oo))",  # 6
    "summation(n**3/2**n, (n, 1, oo))",  # 26
    "summation((-1)**(n+1)/n**2, (n, 1, oo))",  # pi^2/12
    "summation(1/(n * (n+1) * 2**n), (n, 1, oo))",  # 2*log(2) - 1
    "summation(H_n/n**2, (n, 1, oo))",  # 2*zeta(3)
    "summation(1/binomial(2*n, n), (n, 1, oo))",  # special
    "summation((-1)**n/binomial(2*n, n), (n, 0, oo))",  # special

    # Factorial and Combinatorial
    "summation(1/(n!), (n, 0, oo))",  # e
    "summation(n/(n!), (n, 1, oo))",  # e
    "summation((n+1)/(n!), (n, 0, oo))",  # 2e
    "summation(n**2/(n!), (n, 0, oo))",  # 2e
    "summation((-1)**n/(2*n+1)!, (n, 0, oo))",  # sin(1)
    "summation(1/((2*n)!), (n, 0, oo))",  # cosh(1)
    "summation(1/((2*n+1)!), (n, 0, oo))",  # sinh(1)
    "summation(n!/n**n, (n, 1, oo))",  # converges (Stirling)
    "summation(1/(n! * (n+1)!), (n, 0, oo))",  # I_1(2)
    "summation((-1)**n/(n! * (n+2)!), (n, 0, oo))",  # J_2(2)/2
]

# =============================================================================
# CATEGORY 4: LIMITS (100 equations)
# =============================================================================

LIMITS = [
    # Basic Limits
    "limit((x**2 - 1)/(x - 1), x, 1)",  # 2
    "limit((x**3 - 8)/(x - 2), x, 2)",  # 12
    "limit((x**n - a**n)/(x - a), x, a)",  # n*a^(n-1)
    "limit((sqrt(x+1) - 1)/x, x, 0)",  # 1/2
    "limit((sqrt(x+4) - 2)/x, x, 0)",  # 1/4
    "limit((1/x - 1/a)/(x - a), x, a)",  # -1/a^2
    "limit(x/(sqrt(x+1) - 1), x, 0)",  # 2
    "limit((x - 1)/(sqrt(x) - 1), x, 1)",  # 2
    "limit((sqrt(x) - sqrt(a))/(x - a), x, a)",  # 1/(2*sqrt(a))
    "limit((x**2 - 4)/(x**2 - 3*x + 2), x, 2)",  # 4

    # Trigonometric Limits
    "limit(sin(x)/x, x, 0)",  # 1
    "limit((1 - cos(x))/x, x, 0)",  # 0
    "limit((1 - cos(x))/x**2, x, 0)",  # 1/2
    "limit(tan(x)/x, x, 0)",  # 1
    "limit((sin(x) - x)/x**3, x, 0)",  # -1/6
    "limit((tan(x) - x)/x**3, x, 0)",  # 1/3
    "limit((tan(x) - sin(x))/x**3, x, 0)",  # 1/2
    "limit(sin(a*x)/sin(b*x), x, 0)",  # a/b
    "limit((sin(x) - tan(x))/x**3, x, 0)",  # -1/2
    "limit(x * sin(1/x), x, oo)",  # 1

    # Exponential Limits
    "limit((1 + 1/n)**n, n, oo)",  # e
    "limit((1 + x/n)**n, n, oo)",  # e^x
    "limit((1 - 1/n)**n, n, oo)",  # 1/e
    "limit((1 + a/n)**(b*n), n, oo)",  # e^(a*b)
    "limit(n * (exp(1/n) - 1), n, oo)",  # 1
    "limit((exp(x) - 1)/x, x, 0)",  # 1
    "limit((exp(x) - 1 - x)/x**2, x, 0)",  # 1/2
    "limit((exp(a*x) - exp(b*x))/x, x, 0)",  # a - b
    "limit(exp(x)/x**n, x, oo)",  # oo
    "limit(x**n/exp(x), x, oo)",  # 0

    # Logarithmic Limits
    "limit(log(x)/x, x, oo)",  # 0
    "limit(x * log(x), x, 0)",  # 0 (from right)
    "limit((log(1+x))/x, x, 0)",  # 1
    "limit((log(1+x) - x)/x**2, x, 0)",  # -1/2
    "limit(log(x)**n/x, x, oo)",  # 0
    "limit(x**a * log(x), x, 0)",  # 0 for a > 0
    "limit((x**a - 1)/a, a, 0)",  # log(x)
    "limit(n * (x**(1/n) - 1), n, oo)",  # log(x)
    "limit((1 + log(x)/x)**x, x, oo)",  # e
    "limit(log(log(x))/log(x), x, oo)",  # 0

    # L'Hopital Cases
    "limit(x/sin(x), x, 0)",  # 1
    "limit(log(x)/cot(x), x, 0)",  # 0 (from right)
    "limit((x - sin(x))/(x - tan(x)), x, 0)",  # -1/2
    "limit(x**x, x, 0)",  # 1 (from right)
    "limit((1/x)**sin(x), x, 0)",  # 1 (from right)
    "limit(x**(1/x), x, oo)",  # 1
    "limit((1 + sin(x))**(1/x), x, 0)",  # e
    "limit(((sin(x))/x)**(1/x**2), x, 0)",  # e^(-1/6)
    "limit((cos(x))**(1/x**2), x, 0)",  # e^(-1/2)
    "limit((tan(x)/x)**(1/x**2), x, 0)",  # e^(1/3)

    # Infinite Limits at Infinity
    "limit((x**2 + x)/(x + 1), x, oo)",  # oo
    "limit((2*x**3 - x)/(3*x**3 + 1), x, oo)",  # 2/3
    "limit((x**2 - 1)/(x**3 + 1), x, oo)",  # 0
    "limit(sqrt(x**2 + x) - x, x, oo)",  # 1/2
    "limit(sqrt(x**2 + a*x) - x, x, oo)",  # a/2
    "limit(x * (sqrt(x**2 + 1) - x), x, oo)",  # 1/2
    "limit((sqrt(x + sqrt(x)) - sqrt(x)), x, oo)",  # 1/2
    "limit(x**2 * (sqrt(1 + 1/x) - 1), x, oo)",  # 1/2
    "limit(n**2 * (1 - cos(1/n)), n, oo)",  # 1/2
    "limit(n * sin(1/n), n, oo)",  # 1

    # Squeeze Theorem / Bounded
    "limit(sin(x) * cos(1/x), x, 0)",  # 0
    "limit(x * sin(1/x), x, 0)",  # 0
    "limit(x**2 * sin(1/x), x, 0)",  # 0
    "limit(exp(-1/x**2), x, 0)",  # 0
    "limit(x * exp(-x), x, oo)",  # 0
    "limit(x**2 * exp(-x), x, oo)",  # 0
    "limit(sin(x)/x, x, oo)",  # 0
    "limit(cos(x)/x, x, oo)",  # 0
    "limit(arctan(x), x, oo)",  # pi/2
    "limit(arctan(x), x, -oo)",  # -pi/2

    # Special Functions
    "limit((1 + 1/x)**x, x, oo)",  # e
    "limit((1 + a/x)**x, x, oo)",  # e^a
    "limit((1 + 1/n)**n, n, oo)",  # e
    "limit((n/e)**n / n!, n, oo)",  # 1/sqrt(2*pi) (Stirling)
    "limit(n! / (n/e)**n / sqrt(2*pi*n), n, oo)",  # 1
    "limit(gamma(n+1)/(n/e)**n/sqrt(2*pi*n), n, oo)",  # 1
    "limit((1 + 1/n)**(n + 1/2) / e, n, oo)",  # 1
    "limit(binomial(2*n, n) / 4**n * sqrt(pi*n), n, oo)",  # 1
    "limit(n * (zeta(1 + 1/n) - n), n, oo)",  # gamma
    "limit((H_n - log(n)), n, oo)",  # gamma (Euler-Mascheroni)

    # Directional Limits
    "limit(1/x, x, 0, '+')",  # +oo
    "limit(1/x, x, 0, '-')",  # -oo
    "limit(exp(1/x), x, 0, '+')",  # +oo
    "limit(exp(1/x), x, 0, '-')",  # 0
    "limit(floor(x), x, 1, '-')",  # 0
    "limit(floor(x), x, 1, '+')",  # 1
    "limit(abs(x)/x, x, 0, '+')",  # 1
    "limit(abs(x)/x, x, 0, '-')",  # -1
    "limit(tan(x), x, pi/2, '-')",  # +oo
    "limit(tan(x), x, pi/2, '+')",  # -oo

    # Iterated Limits / Nested
    "limit(limit((x*y)/(x**2 + y**2), y, 0), x, 0)",  # 0
    "limit(limit(sin(x*y)/(x*y), y, 0), x, 0)",  # 1 (needs care)
    "limit((1 + 1/(n*m))**(n*m), n, oo)",  # e (fixed m)
    "limit(sum(1/k, (k, 1, n))/log(n), n, oo)",  # 1
    "limit(product((1 + 1/k**2), (k, 1, n)), n, oo)",  # sinh(pi)/(pi)
    "limit(sum(1/k**2, (k, 1, n)), n, oo)",  # pi^2/6
    "limit(n * (sum(1/k, (k, 1, n)) - log(n) - gamma), n, oo)",  # 1/2
    "limit(sum(k/2**k, (k, 1, n)), n, oo)",  # 2
    "limit(product(1 - 1/k**2, (k, 2, n)), n, oo)",  # 1/2
    "limit(product((1 - 1/(4*k**2)), (k, 1, n)), n, oo)",  # 2/pi
]

# =============================================================================
# CATEGORY 5: DERIVATIVES (50 equations)
# =============================================================================

DERIVATIVES = [
    # Basic Derivatives
    "diff(x**n, x)",
    "diff(exp(x), x)",
    "diff(log(x), x)",
    "diff(sin(x), x)",
    "diff(cos(x), x)",
    "diff(tan(x), x)",
    "diff(arcsin(x), x)",
    "diff(arccos(x), x)",
    "diff(arctan(x), x)",
    "diff(sinh(x), x)",

    # Chain Rule
    "diff(sin(x**2), x)",
    "diff(exp(sin(x)), x)",
    "diff(log(sin(x)), x)",
    "diff(sqrt(1 + x**2), x)",
    "diff((1 + x**2)**n, x)",
    "diff(sin(cos(x)), x)",
    "diff(exp(x**2), x)",
    "diff(log(log(x)), x)",
    "diff(arctan(exp(x)), x)",
    "diff(sin(x)**cos(x), x)",

    # Product/Quotient Rule
    "diff(x * sin(x), x)",
    "diff(x**2 * exp(x), x)",
    "diff(x * log(x), x)",
    "diff(sin(x) * cos(x), x)",
    "diff(exp(x) / x, x)",
    "diff(sin(x) / x, x)",
    "diff(x / (1 + x**2), x)",
    "diff(log(x) / x, x)",
    "diff(x**2 / sin(x), x)",
    "diff(tan(x) / sec(x), x)",

    # Higher Derivatives
    "diff(sin(x), x, 2)",
    "diff(exp(x), x, 3)",
    "diff(log(x), x, 4)",
    "diff(x**n, x, n)",
    "diff(sin(a*x), x, n)",
    "diff(exp(a*x), x, n)",
    "diff(x**3 * exp(x), x, 2)",
    "diff(sin(x)**2, x, 2)",
    "diff(1/(1+x**2), x, 2)",
    "diff(arctan(x), x, 2)",

    # Implicit / Special
    "diff(x**x, x)",
    "diff(x**(1/x), x)",
    "diff(x**sin(x), x)",
    "diff((sin(x))**x, x)",
    "diff(log(x)**x, x)",
    "diff(x**(x**x), x)",
    "diff(exp(x*log(x)), x)",
    "diff(gamma(x), x)",
    "diff(erf(x), x)",
    "diff(Si(x), x)",  # Sine integral
]

# =============================================================================
# CATEGORY 6: DIFFERENTIAL EQUATIONS (50 equations)
# =============================================================================

DIFFERENTIAL_EQUATIONS = [
    # First Order Linear
    "dsolve(diff(y(x), x) - y(x), y(x))",
    "dsolve(diff(y(x), x) + 2*y(x) - 4, y(x))",
    "dsolve(diff(y(x), x) + y(x)/x - x, y(x))",
    "dsolve(x*diff(y(x), x) + y(x) - x**2, y(x))",
    "dsolve(diff(y(x), x) + y(x)*tan(x) - sec(x), y(x))",
    "dsolve(diff(y(x), x) - 2*x*y(x), y(x))",
    "dsolve(diff(y(x), x) + y(x) - exp(-x), y(x))",
    "dsolve((1 + x**2)*diff(y(x), x) + 2*x*y(x) - 1, y(x))",
    "dsolve(diff(y(x), x) + y(x) - sin(x), y(x))",
    "dsolve(x*diff(y(x), x) - 2*y(x) - x**3, y(x))",

    # Separable
    "dsolve(diff(y(x), x) - x*y(x), y(x))",
    "dsolve(diff(y(x), x) - y(x)**2, y(x))",
    "dsolve(diff(y(x), x) - x/y(x), y(x))",
    "dsolve(diff(y(x), x) - (1 + y(x)**2), y(x))",
    "dsolve(x*diff(y(x), x) - y(x)*log(y(x)), y(x))",
    "dsolve(diff(y(x), x) - exp(x - y(x)), y(x))",
    "dsolve(diff(y(x), x) - sqrt(1 - y(x)**2), y(x))",
    "dsolve(y(x)*diff(y(x), x) - x, y(x))",
    "dsolve(diff(y(x), x) - y(x)*(1 - y(x)), y(x))",
    "dsolve((1 + x)*diff(y(x), x) - (1 + y(x)), y(x))",

    # Second Order Constant Coefficients
    "dsolve(diff(y(x), x, 2) + y(x), y(x))",
    "dsolve(diff(y(x), x, 2) - y(x), y(x))",
    "dsolve(diff(y(x), x, 2) + 4*y(x), y(x))",
    "dsolve(diff(y(x), x, 2) - 4*y(x), y(x))",
    "dsolve(diff(y(x), x, 2) + 2*diff(y(x), x) + y(x), y(x))",
    "dsolve(diff(y(x), x, 2) - 2*diff(y(x), x) + y(x), y(x))",
    "dsolve(diff(y(x), x, 2) + 4*diff(y(x), x) + 3*y(x), y(x))",
    "dsolve(diff(y(x), x, 2) - 5*diff(y(x), x) + 6*y(x), y(x))",
    "dsolve(diff(y(x), x, 2) + diff(y(x), x) - 2*y(x), y(x))",
    "dsolve(diff(y(x), x, 2) + 2*diff(y(x), x) + 5*y(x), y(x))",

    # Non-homogeneous
    "dsolve(diff(y(x), x, 2) + y(x) - x, y(x))",
    "dsolve(diff(y(x), x, 2) - y(x) - exp(x), y(x))",
    "dsolve(diff(y(x), x, 2) + y(x) - sin(x), y(x))",
    "dsolve(diff(y(x), x, 2) + y(x) - cos(2*x), y(x))",
    "dsolve(diff(y(x), x, 2) - 4*diff(y(x), x) + 4*y(x) - x*exp(2*x), y(x))",
    "dsolve(diff(y(x), x, 2) + 4*y(x) - sec(2*x), y(x))",
    "dsolve(diff(y(x), x, 2) - y(x) - 1/cosh(x), y(x))",
    "dsolve(diff(y(x), x, 2) + y(x) - tan(x), y(x))",
    "dsolve(diff(y(x), x, 2) - 2*diff(y(x), x) + y(x) - exp(x)/x, y(x))",
    "dsolve(diff(y(x), x, 2) + diff(y(x), x) - x**2, y(x))",

    # Higher Order and Special
    "dsolve(diff(y(x), x, 3) - y(x), y(x))",
    "dsolve(diff(y(x), x, 3) + diff(y(x), x), y(x))",
    "dsolve(diff(y(x), x, 4) - y(x), y(x))",
    "dsolve(x**2*diff(y(x), x, 2) + x*diff(y(x), x) - y(x), y(x))",  # Euler
    "dsolve(x**2*diff(y(x), x, 2) + x*diff(y(x), x) - 4*y(x), y(x))",
    "dsolve(x**2*diff(y(x), x, 2) - 2*y(x), y(x))",
    "dsolve((1 - x**2)*diff(y(x), x, 2) - 2*x*diff(y(x), x) + 2*y(x), y(x))",  # Legendre
    "dsolve(x*diff(y(x), x, 2) + diff(y(x), x) + x*y(x), y(x))",  # Bessel
    "dsolve(diff(y(x), x, 2) - 2*x*diff(y(x), x) + 2*n*y(x), y(x))",  # Hermite
    "dsolve(x*diff(y(x), x, 2) + (1 - x)*diff(y(x), x) + n*y(x), y(x))",  # Laguerre
]

# =============================================================================
# CATEGORY 7: LINEAR ALGEBRA (50 equations)
# =============================================================================

LINEAR_ALGEBRA = [
    # Determinants
    "det(Matrix([[1, 2], [3, 4]]))",
    "det(Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))",
    "det(Matrix([[a, b], [c, d]]))",
    "det(Matrix([[1, 1, 1], [a, b, c], [a**2, b**2, c**2]]))",  # Vandermonde
    "det(Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]))",
    "det(Matrix([[n, 1, 1], [1, n, 1], [1, 1, n]]))",
    "det(eye(n))",
    "det(Matrix([[cos(t), -sin(t)], [sin(t), cos(t)]]))",  # rotation
    "det(Matrix([[1, 2, 3], [0, 1, 4], [5, 6, 0]]))",
    "det(Matrix([[a, b, c], [d, e, f], [g, h, i]]))",

    # Eigenvalues
    "eigenvals(Matrix([[1, 2], [2, 1]]))",
    "eigenvals(Matrix([[4, 1], [2, 3]]))",
    "eigenvals(Matrix([[0, 1], [-1, 0]]))",
    "eigenvals(Matrix([[1, 1, 0], [0, 1, 1], [0, 0, 1]]))",
    "eigenvals(Matrix([[2, 0, 0], [0, 3, 0], [0, 0, 5]]))",
    "eigenvals(Matrix([[0, 1, 0], [0, 0, 1], [1, 0, 0]]))",
    "eigenvals(Matrix([[1, 2, 0], [2, 1, 0], [0, 0, 3]]))",
    "eigenvals(Matrix([[a, b], [b, a]]))",
    "eigenvals(Matrix([[cos(t), sin(t)], [-sin(t), cos(t)]]))",
    "eigenvals(Matrix([[1, 1], [0, 1]]))",  # defective

    # Matrix Operations
    "Matrix([[1, 2], [3, 4]]) * Matrix([[5, 6], [7, 8]])",
    "Matrix([[1, 2, 3], [4, 5, 6]]) * Matrix([[1, 2], [3, 4], [5, 6]])",
    "Matrix([[1, 2], [3, 4]])**2",
    "Matrix([[1, 2], [3, 4]])**(-1)",
    "Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])**n",
    "Matrix([[1, 1], [0, 1]])**n",
    "Matrix([[0, 1], [1, 0]])**100",
    "Matrix([[1, 2], [0, 1]]) + Matrix([[0, 1], [1, 0]])",
    "transpose(Matrix([[1, 2, 3], [4, 5, 6]]))",
    "Matrix([[1, 2], [3, 4]]).trace()",

    # Rank and Nullity
    "Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]).rank()",
    "Matrix([[1, 2, 3, 4], [2, 4, 6, 8]]).rank()",
    "Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 0]]).rank()",
    "Matrix([[1, 2], [2, 4], [3, 6]]).rank()",
    "nullspace(Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))",
    "nullspace(Matrix([[1, 2, 1], [2, 4, 2]]))",
    "columnspace(Matrix([[1, 2], [3, 4], [5, 6]]))",
    "rowspace(Matrix([[1, 2, 3], [4, 5, 6]]))",
    "Matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]).rref()",
    "Matrix([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]).rref()",

    # Systems of Equations
    "linsolve([x + y - 3, x - y - 1], [x, y])",
    "linsolve([x + 2*y + z - 6, 2*x - y + z - 3, x + y - z - 2], [x, y, z])",
    "linsolve([2*x + 3*y - 5, 4*x + 6*y - 10], [x, y])",  # infinite
    "linsolve([x + y - 1, x + y - 2], [x, y])",  # no solution
    "Matrix([[1, 2], [3, 4]]).LUdecomposition()",
    "Matrix([[4, 12, -16], [12, 37, -43], [-16, -43, 98]]).cholesky()",
    "QRdecomposition(Matrix([[1, 2], [3, 4], [5, 6]]))",
    "Matrix([[1, 2], [2, 1]]).diagonalize()",
    "Matrix([[1, 1], [0, 1]]).jordan_form()",
    "svd(Matrix([[1, 2], [3, 4], [5, 6]]))",
]

# =============================================================================
# CATEGORY 8: NUMBER THEORY (50 equations)
# =============================================================================

NUMBER_THEORY = [
    # GCD and LCM
    "gcd(12, 18)",
    "gcd(48, 180)",
    "gcd(1071, 462)",
    "gcd(a, b)",  # symbolic
    "lcm(12, 18)",
    "lcm(15, 20)",
    "gcd(gcd(a, b), c)",
    "gcd(n, n+1)",  # always 1
    "gcd(2**n - 1, 2**m - 1)",  # = 2^gcd(n,m) - 1
    "gcd(fib(n), fib(m))",  # = fib(gcd(n,m))

    # Modular Arithmetic
    "Mod(17, 5)",
    "Mod(123, 11)",
    "Mod(2**100, 7)",
    "Mod(3**100, 13)",
    "Mod(7**222, 11)",
    "mod_inverse(3, 7)",  # 3^(-1) mod 7
    "mod_inverse(17, 43)",
    "discrete_log(2, 3, 5)",  # 3^x = 2 mod 5
    "Mod(factorial(100), 101)",  # Wilson: -1
    "Mod(fib(n), fib(m))",

    # Prime Numbers
    "isprime(97)",
    "isprime(1009)",
    "nextprime(100)",
    "prevprime(100)",
    "prime(100)",  # 100th prime
    "primepi(100)",  # primes <= 100
    "factorint(360)",
    "factorint(2**31 - 1)",  # Mersenne
    "factorint(1000000007)",
    "totient(100)",  # Euler's phi

    # Diophantine Equations
    "diophantine(3*x + 5*y - 7)",  # Linear
    "diophantine(x**2 + y**2 - 25)",  # Pythagorean
    "diophantine(x**2 - 2*y**2 - 1)",  # Pell
    "diophantine(x**2 - 3*y**2 - 1)",
    "diophantine(x**2 + y**2 + z**2 - 100)",
    "diophantine(x*y - 12)",
    "diophantine(x**2 - y**3 - 1)",
    "diophantine(x**3 + y**3 - z**3)",  # Fermat (x,y,z coprime)
    "diophantine(4*x + 6*y - 10)",
    "diophantine(a*x + b*y - c)",

    # Sequences and Identities
    "fibonacci(100)",
    "lucas(50)",
    "catalan(20)",
    "bernoulli(10)",
    "euler(8)",
    "stirling(n, k, 1)",  # first kind
    "stirling(n, k, 2)",  # second kind
    "bell(10)",
    "partition(50)",
    "Sum(1/p, (p, primes, n))",  # ~ log(log(n))
]

# =============================================================================
# CATEGORY 9: PROBABILITY AND STATISTICS (50 equations)
# =============================================================================

PROBABILITY_STATISTICS = [
    # Combinatorics
    "binomial(10, 3)",
    "binomial(20, 10)",
    "binomial(n, k)",
    "factorial(10)",
    "factorial(20)/factorial(10)",
    "binomial(n, 0) + binomial(n, 1) + binomial(n, 2)",  # = 2^n partial
    "Sum(binomial(n, k), (k, 0, n))",  # = 2^n
    "Sum(k * binomial(n, k), (k, 0, n))",  # = n * 2^(n-1)
    "Sum(binomial(n, k)**2, (k, 0, n))",  # = binomial(2n, n)
    "Product(k, (k, 1, n))",  # = n!

    # Discrete Distributions
    "binomial(n, k) * p**k * (1-p)**(n-k)",  # Binomial PMF
    "exp(-lambda) * lambda**k / factorial(k)",  # Poisson PMF
    "p * (1-p)**(k-1)",  # Geometric PMF
    "binomial(k-1, r-1) * p**r * (1-p)**(k-r)",  # Negative Binomial
    "binomial(K, k) * binomial(N-K, n-k) / binomial(N, n)",  # Hypergeometric
    "1/N",  # Uniform discrete
    "Sum(k * binomial(n, k) * p**k * (1-p)**(n-k), (k, 0, n))",  # E[Binomial]
    "n*p*(1-p)",  # Var[Binomial]
    "Sum(k * exp(-lambda) * lambda**k / factorial(k), (k, 0, oo))",  # E[Poisson]
    "1/p",  # E[Geometric]

    # Continuous Distributions
    "integrate(exp(-x**2/2)/sqrt(2*pi), (x, -oo, oo))",  # Normal normalization
    "integrate(x * exp(-x**2/2)/sqrt(2*pi), (x, -oo, oo))",  # E[Normal(0,1)]
    "integrate(x**2 * exp(-x**2/2)/sqrt(2*pi), (x, -oo, oo))",  # Var[Normal]
    "integrate(lambda * exp(-lambda * x), (x, 0, oo))",  # Exponential norm
    "integrate(x * lambda * exp(-lambda * x), (x, 0, oo))",  # E[Exponential]
    "1/lambda",  # E[Exp(lambda)]
    "integrate(x**(a-1) * (1-x)**(b-1), (x, 0, 1))",  # Beta normalization
    "a/(a+b)",  # E[Beta(a,b)]
    "integrate(x**(k-1) * exp(-x), (x, 0, oo))",  # Gamma norm
    "k",  # E[Gamma(k,1)]

    # Moment Generating Functions
    "Sum(exp(t*k) * binomial(n, k) * p**k * (1-p)**(n-k), (k, 0, n))",  # MGF Binomial
    "(p*exp(t) + 1 - p)**n",  # MGF Binomial closed
    "exp(lambda*(exp(t) - 1))",  # MGF Poisson
    "p*exp(t) / (1 - (1-p)*exp(t))",  # MGF Geometric
    "exp(mu*t + sigma**2*t**2/2)",  # MGF Normal
    "lambda / (lambda - t)",  # MGF Exponential
    "(1 - t/lambda)**(-k)",  # MGF Gamma
    "diff(exp(t*X), t)",  # E[X] from MGF
    "diff(exp(t*X), t, 2) - diff(exp(t*X), t)**2",  # Var from MGF
    "log(E[exp(t*X)])",  # Cumulant generating function

    # Statistical Measures
    "Sum(x_i, (i, 1, n)) / n",  # Sample mean
    "Sum((x_i - xbar)**2, (i, 1, n)) / (n-1)",  # Sample variance
    "Sum((x_i - xbar)**3, (i, 1, n)) / (n * s**3)",  # Skewness
    "Sum((x_i - xbar)**4, (i, 1, n)) / (n * s**4) - 3",  # Excess kurtosis
    "Sum(x_i * y_i, (i, 1, n)) / n - xbar * ybar",  # Covariance
    "Cov(X, Y) / (std(X) * std(Y))",  # Correlation
    "E[X] * E[Y]",  # Independence: E[XY] = E[X]E[Y]
    "Var(X + Y)",  # = Var(X) + Var(Y) + 2Cov(X,Y)
    "Var(a*X + b)",  # = a^2 Var(X)
    "E[g(X)]",  # Law of unconscious statistician
]

# =============================================================================
# CATEGORY 10: PHYSICS AND APPLIED MATH (50 equations)
# =============================================================================

PHYSICS_APPLIED = [
    # Classical Mechanics
    "diff(r(t), t)",  # velocity
    "diff(r(t), t, 2)",  # acceleration
    "m * diff(r(t), t, 2) - F",  # Newton's 2nd law
    "integrate(F, (x, a, b))",  # Work
    "m * v**2 / 2",  # Kinetic energy
    "m * g * h",  # Potential energy
    "m1*v1 + m2*v2",  # Momentum conservation
    "I * omega",  # Angular momentum
    "I * diff(theta, t, 2) + m*g*l*sin(theta)",  # Pendulum
    "m * diff(x, t, 2) + k * x",  # Harmonic oscillator

    # Waves and Oscillations
    "A * sin(k*x - omega*t)",  # Traveling wave
    "A * sin(k*x) * cos(omega*t)",  # Standing wave
    "omega / k",  # Phase velocity
    "diff(omega, k)",  # Group velocity
    "1 / (2*pi) * sqrt(k/m)",  # Natural frequency
    "exp(-gamma*t) * cos(omega_d*t)",  # Damped oscillation
    "A1 * sin(omega*t) + A2 * sin((omega + delta)*t)",  # Beats
    "diff(u, t, 2) - c**2 * diff(u, x, 2)",  # Wave equation
    "Sum(A_n * sin(n*pi*x/L), (n, 1, oo))",  # Fourier sine series
    "sqrt(T/mu)",  # Wave speed on string

    # Electromagnetism
    "q1 * q2 / (4*pi*epsilon_0 * r**2)",  # Coulomb's law
    "integrate(E, (x, a, b))",  # Voltage
    "I * R",  # Ohm's law
    "V * I",  # Power
    "q * v x B",  # Lorentz force (cross product)
    "mu_0 * I / (2*pi*r)",  # Magnetic field from wire
    "-diff(Phi_B, t)",  # Faraday's law
    "L * diff(I, t)",  # Inductor voltage
    "C * diff(V, t)",  # Capacitor current
    "1 / sqrt(L*C)",  # LC resonance frequency

    # Thermodynamics
    "n * R * T / V",  # Ideal gas law
    "3/2 * n * R * T",  # Internal energy (ideal gas)
    "C_v * diff(T, t)",  # Heat capacity
    "k * A * diff(T, x)",  # Heat conduction
    "diff(T, t) - alpha * diff(T, x, 2)",  # Heat equation 1D
    "sigma * T**4",  # Stefan-Boltzmann
    "h * nu / (exp(h*nu/(k*T)) - 1)",  # Planck distribution
    "k * T * log(Omega)",  # Boltzmann entropy
    "-n*R*T*log(V2/V1)",  # Isothermal work
    "C_p - C_v",  # = R for ideal gas

    # Quantum Mechanics
    "-hbar**2/(2*m) * diff(psi, x, 2) + V*psi",  # Schrodinger 1D
    "exp(i*(k*x - omega*t))",  # Plane wave
    "A * exp(-alpha * x**2)",  # Gaussian packet
    "integrate(psi * conjugate(psi), (x, -oo, oo))",  # Normalization
    "integrate(psi * x * conjugate(psi), (x, -oo, oo))",  # <x>
    "-i * hbar * diff(psi, x)",  # Momentum operator
    "hbar * omega * (n + 1/2)",  # Harmonic oscillator energy
    "E_n * exp(-i*E_n*t/hbar)",  # Time evolution
    "integrate(psi_m * psi_n, (x, -oo, oo))",  # Orthogonality
    "hbar**2 / (2*m*a**2) * n**2",  # Particle in box
]

# =============================================================================
# COMBINE ALL EQUATIONS
# =============================================================================

ALL_EQUATIONS = (
    DEFINITE_INTEGRALS +      # 100
    INDEFINITE_INTEGRALS +    # 50
    INFINITE_SERIES +         # 100
    LIMITS +                  # 100
    DERIVATIVES +             # 50
    DIFFERENTIAL_EQUATIONS +  # 50
    LINEAR_ALGEBRA +          # 50
    NUMBER_THEORY +           # 50
    PROBABILITY_STATISTICS +  # 50
    PHYSICS_APPLIED           # 50
)  # Total: 600 equations

# Category mapping for analysis
CATEGORIES = {
    "definite_integrals": DEFINITE_INTEGRALS,
    "indefinite_integrals": INDEFINITE_INTEGRALS,
    "infinite_series": INFINITE_SERIES,
    "limits": LIMITS,
    "derivatives": DERIVATIVES,
    "differential_equations": DIFFERENTIAL_EQUATIONS,
    "linear_algebra": LINEAR_ALGEBRA,
    "number_theory": NUMBER_THEORY,
    "probability_statistics": PROBABILITY_STATISTICS,
    "physics_applied": PHYSICS_APPLIED,
}

if __name__ == "__main__":
    print(f"Total equations: {len(ALL_EQUATIONS)}")
    for name, eqs in CATEGORIES.items():
        print(f"  {name}: {len(eqs)}")
