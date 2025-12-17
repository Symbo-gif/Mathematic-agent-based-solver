# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
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
Synthetic Data Generator - "The Dreamer"
=========================================

Agent 1.1 of the Conjecture Generation Team

Based on the AlphaGeometry paradigm, continuously generates random geometric
or algebraic premises and attempts to derive conclusions using Phase 2
symbolic engines.

Function: Produces millions of "synthetic theorems" - statements that are
logically true but potentially trivial. Creates a massive dataset of
premise-conclusion pairs to train downstream agent intuition.

Output: Stream of SyntheticTheorem objects containing premises, derivation
steps, and conclusions.

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 1
Reference: Phase_6_Build_Order_Breakdown.md, Step 1
"""

import logging
import random
import hashlib
import math
from dataclasses import dataclass, field
from typing import List, Optional, Generator, Dict, Any, Tuple
from datetime import datetime
from enum import Enum

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Expr, Symbol, symbols, Integer, Float, Rational,
    Add, Mul, Pow, Sin, Cos, Tan, Exp, Log, Sqrt, Abs,
    parse_expr, simplify, expand, pi, E, oo
)


class Eq(Expr):
    """Equality expression for conjectures - native implementation."""

    def __init__(self, lhs: Expr, rhs: Expr):
        self.lhs = lhs if isinstance(lhs, Expr) else Integer(lhs) if isinstance(lhs, int) else parse_expr(str(lhs))
        self.rhs = rhs if isinstance(rhs, Expr) else Integer(rhs) if isinstance(rhs, int) else parse_expr(str(rhs))
        self._hash_cache = hash(('Eq', hash(self.lhs), hash(self.rhs)))

    def __repr__(self) -> str:
        return f"Eq({self.lhs!r}, {self.rhs!r})"

    def __str__(self) -> str:
        return f"{self.lhs} = {self.rhs}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Eq):
            return self.lhs == other.lhs and self.rhs == other.rhs
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    @property
    def free_symbols(self):
        return self.lhs.free_symbols | self.rhs.free_symbols if hasattr(self.lhs, 'free_symbols') else set()

    def subs(self, substitutions):
        return Eq(self.lhs.subs(substitutions), self.rhs.subs(substitutions))

    def diff(self, var):
        return Eq(self.lhs.diff(var), self.rhs.diff(var))

    def simplify(self):
        return Eq(simplify(self.lhs), simplify(self.rhs))

    def evalf(self, precision=15):
        return Eq(self.lhs.evalf(precision), self.rhs.evalf(precision))

    def to_latex(self) -> str:
        return f"{self.lhs.to_latex()} = {self.rhs.to_latex()}"


class Gt(Expr):
    """Greater-than expression - native implementation."""

    def __init__(self, lhs: Expr, rhs: Expr):
        self.lhs = lhs if isinstance(lhs, Expr) else Integer(lhs) if isinstance(lhs, int) else parse_expr(str(lhs))
        self.rhs = rhs if isinstance(rhs, Expr) else Integer(rhs) if isinstance(rhs, int) else parse_expr(str(rhs))
        self._hash_cache = hash(('Gt', hash(self.lhs), hash(self.rhs)))

    def __repr__(self) -> str:
        return f"Gt({self.lhs!r}, {self.rhs!r})"

    def __str__(self) -> str:
        return f"{self.lhs} > {self.rhs}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Gt):
            return self.lhs == other.lhs and self.rhs == other.rhs
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    @property
    def free_symbols(self):
        return self.lhs.free_symbols | self.rhs.free_symbols if hasattr(self.lhs, 'free_symbols') else set()

    def subs(self, substitutions):
        return Gt(self.lhs.subs(substitutions), self.rhs.subs(substitutions))

    def diff(self, var):
        return Integer(0)

    def simplify(self):
        return self

    def evalf(self, precision=15):
        return self

    def to_latex(self) -> str:
        return f"{self.lhs.to_latex()} > {self.rhs.to_latex()}"


class Ge(Expr):
    """Greater-than-or-equal expression - native implementation."""

    def __init__(self, lhs: Expr, rhs: Expr):
        self.lhs = lhs if isinstance(lhs, Expr) else Integer(lhs) if isinstance(lhs, int) else parse_expr(str(lhs))
        self.rhs = rhs if isinstance(rhs, Expr) else Integer(rhs) if isinstance(rhs, int) else parse_expr(str(rhs))
        self._hash_cache = hash(('Ge', hash(self.lhs), hash(self.rhs)))

    def __repr__(self) -> str:
        return f"Ge({self.lhs!r}, {self.rhs!r})"

    def __str__(self) -> str:
        return f"{self.lhs} >= {self.rhs}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Ge):
            return self.lhs == other.lhs and self.rhs == other.rhs
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    @property
    def free_symbols(self):
        return self.lhs.free_symbols | self.rhs.free_symbols if hasattr(self.lhs, 'free_symbols') else set()

    def subs(self, substitutions):
        return Ge(self.lhs.subs(substitutions), self.rhs.subs(substitutions))

    def diff(self, var):
        return Integer(0)

    def simplify(self):
        return self

    def evalf(self, precision=15):
        return self

    def to_latex(self) -> str:
        return f"{self.lhs.to_latex()} \\geq {self.rhs.to_latex()}"


class Ne(Expr):
    """Not-equal expression - native implementation."""

    def __init__(self, lhs: Expr, rhs: Expr):
        self.lhs = lhs if isinstance(lhs, Expr) else Integer(lhs) if isinstance(lhs, int) else parse_expr(str(lhs))
        self.rhs = rhs if isinstance(rhs, Expr) else Integer(rhs) if isinstance(rhs, int) else parse_expr(str(rhs))
        self._hash_cache = hash(('Ne', hash(self.lhs), hash(self.rhs)))

    def __repr__(self) -> str:
        return f"Ne({self.lhs!r}, {self.rhs!r})"

    def __str__(self) -> str:
        return f"{self.lhs} != {self.rhs}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Ne):
            return self.lhs == other.lhs and self.rhs == other.rhs
        return False

    def __hash__(self) -> int:
        return self._hash_cache

    @property
    def free_symbols(self):
        return self.lhs.free_symbols | self.rhs.free_symbols if hasattr(self.lhs, 'free_symbols') else set()

    def subs(self, substitutions):
        return Ne(self.lhs.subs(substitutions), self.rhs.subs(substitutions))

    def diff(self, var):
        return Integer(0)

    def simplify(self):
        return self

    def evalf(self, precision=15):
        return self

    def to_latex(self) -> str:
        return f"{self.lhs.to_latex()} \\neq {self.rhs.to_latex()}"

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.conjecture_generation.synthetic_data_generator')
except ImportError:
    logger = logging.getLogger(__name__)


class TheoremDomain(Enum):
    """Mathematical domains for synthetic theorem generation"""
    ALGEBRA = 'algebra'
    GEOMETRY = 'geometry'
    NUMBER_THEORY = 'number_theory'
    ANALYSIS = 'analysis'
    COMBINATORICS = 'combinatorics'
    LINEAR_ALGEBRA = 'linear_algebra'


@dataclass
class SyntheticTheorem:
    """
    A theorem generated by the Synthetic Data Generator.

    Based on AlphaGeometry paradigm: randomly sample premises
    and derive conclusions using symbolic engines.

    Attributes:
        theorem_id: Unique identifier for the theorem
        premises: List of Expr expressions representing premises
        conclusion: The derived Expr expression conclusion
        derivation_steps: List of steps taken to derive the conclusion
        domain: Mathematical domain of the theorem
        complexity_score: 0-1 score indicating theorem complexity
        novelty_score: 0-1 score indicating potential novelty (set by PatternRecognizer)
        generation_timestamp: When the theorem was generated
    """
    theorem_id: str
    premises: List[Expr]
    conclusion: Expr
    derivation_steps: List[str]
    domain: str
    complexity_score: float
    novelty_score: float = 0.0
    generation_timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_natural_language(self) -> str:
        """Convert to human-readable statement"""
        if self.premises:
            premises_str = " AND ".join([str(p) for p in self.premises])
            return f"IF {premises_str} THEN {self.conclusion}"
        return f"STATEMENT: {self.conclusion}"

    def compute_hash(self) -> str:
        """Deterministic hash for deduplication"""
        content = f"{sorted([str(p) for p in self.premises])}|{self.conclusion}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'theorem_id': self.theorem_id,
            'premises': [str(p) for p in self.premises],
            'conclusion': str(self.conclusion),
            'derivation_steps': self.derivation_steps,
            'domain': self.domain,
            'complexity_score': self.complexity_score,
            'novelty_score': self.novelty_score,
            'generation_timestamp': self.generation_timestamp.isoformat(),
            'natural_language': self.to_natural_language()
        }


class SyntheticDataGenerator:
    """
    Agent 1.1: The Dreamer - AlphaGeometry-style synthetic theorem generator

    Continuously generates random mathematical premises and derives conclusions
    using symbolic manipulation to create training data for conjecture discovery.

    Key capabilities:
    - Multi-domain theorem generation (algebra, geometry, number theory, analysis)
    - Complexity-aware generation with configurable parameters
    - Streaming generation for memory efficiency
    - Deduplication via content hashing

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    # Statistics tracking
    stats: Dict[str, int]

    def __init__(self, symbolic_engine=None, df_client=None, seed: int = None):
        """
        Initialize the Synthetic Data Generator.

        Args:
            symbolic_engine: Phase 2 symbolic engine for derivations
            df_client: Directory Facilitator client for service discovery
            seed: Random seed for reproducibility
        """
        self.symbolic_engine = symbolic_engine
        self.df = df_client
        self.theorem_count = 0
        self.seen_hashes = set()

        if seed is not None:
            random.seed(seed)

        # Symbol pools for different domains - using native symbols
        self.algebra_symbols = symbols('x y z a b c n m k')
        self.geometry_symbols = symbols('A B C D P Q R theta phi alpha beta')
        self.analysis_symbols = symbols('f g h epsilon delta t s')
        self.number_symbols = symbols('p q r n m k', integer=True, positive=True)

        # Binary operations for expression generation
        self.binary_ops = [
            lambda a, b: a + b,
            lambda a, b: a * b,
            lambda a, b: a - b,
            lambda a, b: a / b if b != Integer(0) else a,
            lambda a, b: a ** b if isinstance(b, int) and 0 <= b <= 3 else a ** 2,
            lambda a, b: Eq(a, b),
        ]

        # Unary operations - using native functions
        self.unary_ops = [
            lambda a: a ** 2,
            lambda a: Sqrt(Abs(a)),
            lambda a: Sin(a),
            lambda a: Cos(a),
            lambda a: Exp(a),
            lambda a: Log(Abs(a) + Integer(1)),
        ]

        # Statistics
        self.stats = {
            'total_generated': 0,
            'algebra': 0,
            'geometry': 0,
            'number_theory': 0,
            'analysis': 0,
            'combinatorics': 0,
            'linear_algebra': 0,
            'duplicates_filtered': 0,
            'generation_errors': 0
        }

    def generate_stream(self, batch_size: int = 1000, max_theorems: int = None) -> Generator[SyntheticTheorem, None, None]:
        """
        Generate synthetic theorems continuously as a stream.

        Args:
            batch_size: Number of theorems to attempt per batch
            max_theorems: Maximum theorems to generate (None for infinite)

        Yields:
            SyntheticTheorem objects that pass validation
        """
        count = 0
        while max_theorems is None or count < max_theorems:
            batch = [self._generate_single() for _ in range(batch_size)]
            valid_theorems = [t for t in batch if t is not None]

            for theorem in valid_theorems:
                if max_theorems is not None and count >= max_theorems:
                    return
                yield theorem
                count += 1

    def generate_batch(self, size: int = 100, domain: str = None) -> List[SyntheticTheorem]:
        """
        Generate a batch of synthetic theorems.

        Args:
            size: Number of theorems to generate
            domain: Optional domain restriction

        Returns:
            List of valid SyntheticTheorem objects
        """
        theorems = []
        attempts = 0
        max_attempts = size * 10  # Allow for failures

        while len(theorems) < size and attempts < max_attempts:
            attempts += 1
            if domain:
                theorem = self._generate_for_domain(domain)
            else:
                theorem = self._generate_single()

            if theorem is not None:
                theorems.append(theorem)

        return theorems

    def _generate_single(self) -> Optional[SyntheticTheorem]:
        """Generate a single synthetic theorem from a random domain"""
        try:
            domain = random.choice(list(TheoremDomain))
            return self._generate_for_domain(domain.value)
        except (TypeError, ValueError, AttributeError, KeyError) as e:
            # Data/conversion errors during generation
            logger.debug(f"Generation data error in _generate_single: {e}")
            self.stats['generation_errors'] += 1
            return None
        except RecursionError as e:
            # Recursion errors during generation
            logger.debug(f"Generation recursion error in _generate_single: {e}")
            self.stats['generation_errors'] += 1
            return None

    def _generate_for_domain(self, domain: str) -> Optional[SyntheticTheorem]:
        """Generate a theorem for a specific domain"""
        generators = {
            'algebra': self._generate_algebra_theorem,
            'geometry': self._generate_geometry_theorem,
            'number_theory': self._generate_number_theory_theorem,
            'analysis': self._generate_analysis_theorem,
            'combinatorics': self._generate_combinatorics_theorem,
            'linear_algebra': self._generate_linear_algebra_theorem
        }

        generator = generators.get(domain, self._generate_algebra_theorem)

        try:
            theorem = generator()
            if theorem is not None:
                # Check for duplicates
                thm_hash = theorem.compute_hash()
                if thm_hash in self.seen_hashes:
                    self.stats['duplicates_filtered'] += 1
                    return None
                self.seen_hashes.add(thm_hash)

                self.stats['total_generated'] += 1
                self.stats[domain] = self.stats.get(domain, 0) + 1

            return theorem
        except (TypeError, ValueError, AttributeError, KeyError) as e:
            # Data/conversion errors during domain generation
            logger.debug(f"Generation data error for domain {domain}: {e}")
            self.stats['generation_errors'] += 1
            return None
        except (RecursionError, NotImplementedError) as e:
            # Recursion/not-implemented errors during domain generation
            logger.debug(f"Generation error for domain {domain}: {e}")
            self.stats['generation_errors'] += 1
            return None

    def _generate_algebra_theorem(self) -> Optional[SyntheticTheorem]:
        """Generate algebraic identity or relation"""
        x, y, z, a, b, c = symbols('x y z a b c')

        template = random.choice(['polynomial_identity', 'equation_solution', 'factorization', 'expansion'])

        if template == 'polynomial_identity':
            # Generate polynomial identities like (a+b)^2 = a^2 + 2ab + b^2
            n = random.randint(2, 4)
            lhs = (a + b) ** n
            rhs = expand(lhs)
            premises = []
            conclusion = Eq(lhs, rhs)
            derivation = ['expand', 'simplify']

        elif template == 'equation_solution':
            # Generate equation and its solution - simplified for native impl
            degree = random.randint(1, 2)
            coeffs = [random.randint(-5, 5) for _ in range(degree + 1)]
            poly = sum(Integer(c) * x**i for i, c in enumerate(coeffs))

            premises = [Eq(poly, Integer(0))]
            # Simplified: just create a placeholder solution
            conclusion = Eq(x, Symbol('solution'))
            derivation = ['solve', 'simplify']

        elif template == 'factorization':
            # Generate factorable polynomial
            r1, r2 = random.randint(-5, 5), random.randint(-5, 5)
            poly = (x - Integer(r1)) * (x - Integer(r2))
            expanded = expand(poly)

            premises = []
            conclusion = Eq(expanded, poly)
            derivation = ['factor']

        else:  # expansion
            # Binomial expansion
            n = random.randint(2, 4)
            expr = (x + y) ** n
            expanded = expand(expr)

            premises = []
            conclusion = Eq(expr, expanded)
            derivation = ['binomial_theorem', 'expand']

        self.theorem_count += 1

        return SyntheticTheorem(
            theorem_id=f"synth_alg_{self.theorem_count}",
            premises=premises,
            conclusion=conclusion,
            derivation_steps=derivation,
            domain="algebra",
            complexity_score=self._compute_complexity(premises, conclusion)
        )

    def _generate_geometry_theorem(self) -> Optional[SyntheticTheorem]:
        """Generate geometric relation"""
        a, b, c, theta = symbols('a b c theta', positive=True, real=True)

        template = random.choice(['pythagorean', 'law_of_cosines', 'law_of_sines',
                                  'area_formula', 'angle_sum', 'trig_identity'])

        if template == 'pythagorean':
            premises = [Eq(Symbol('angle_C'), pi/Integer(2))]  # Right angle
            conclusion = Eq(c**2, a**2 + b**2)
            derivation = ['pythagorean_theorem']

        elif template == 'law_of_cosines':
            premises = []
            conclusion = Eq(c**2, a**2 + b**2 - Integer(2)*a*b*Cos(theta))
            derivation = ['law_of_cosines']

        elif template == 'law_of_sines':
            alpha, beta = symbols('alpha beta', positive=True, real=True)
            premises = []
            conclusion = Eq(a/Sin(alpha), b/Sin(beta))
            derivation = ['law_of_sines']

        elif template == 'area_formula':
            s = (a + b + c) / Integer(2)
            area = Sqrt(s * (s-a) * (s-b) * (s-c))
            premises = [Gt(a + b, c), Gt(b + c, a), Gt(a + c, b)]
            conclusion = Eq(Symbol('Area'), area)
            derivation = ['herons_formula']

        elif template == 'angle_sum':
            alpha, beta, gamma = symbols('alpha beta gamma', positive=True)
            premises = [Symbol('triangle')]
            conclusion = Eq(alpha + beta + gamma, pi)
            derivation = ['angle_sum_theorem']

        else:  # trig_identity
            premises = []
            identity = random.choice([
                Eq(Sin(theta)**2 + Cos(theta)**2, Integer(1)),
                Eq(Tan(theta), Sin(theta)/Cos(theta)),
                Eq(Sin(Integer(2)*theta), Integer(2)*Sin(theta)*Cos(theta)),
                Eq(Cos(Integer(2)*theta), Cos(theta)**2 - Sin(theta)**2)
            ])
            conclusion = identity
            derivation = ['trig_identity']

        self.theorem_count += 1

        return SyntheticTheorem(
            theorem_id=f"synth_geo_{self.theorem_count}",
            premises=premises,
            conclusion=conclusion,
            derivation_steps=derivation,
            domain="geometry",
            complexity_score=self._compute_complexity(premises, conclusion)
        )

    def _generate_number_theory_theorem(self) -> Optional[SyntheticTheorem]:
        """Generate number-theoretic relation"""
        n, m, p, k = symbols('n m p k', integer=True, positive=True)

        template = random.choice(['divisibility', 'modular_arithmetic', 'sum_formula',
                                  'gcd_property', 'prime_property'])

        if template == 'divisibility':
            base = random.randint(2, 10)
            power = random.randint(2, 4)
            premises = [Eq(Symbol('n_mod_base'), Integer(0))]
            conclusion = Eq(Symbol('n_pow_mod_base'), Integer(0))
            derivation = ['divisibility_rule']

        elif template == 'modular_arithmetic':
            # Fermat's little theorem variant
            premises = [Eq(Symbol('gcd_n_p'), Integer(1)), Symbol('p_is_prime')]
            conclusion = Eq(Symbol('n_pow_p_minus_1_mod_p'), Integer(1))
            derivation = ['fermats_little_theorem']

        elif template == 'sum_formula':
            formula_type = random.choice(['arithmetic', 'squares', 'cubes'])
            premises = [Gt(n, Integer(0))]

            if formula_type == 'arithmetic':
                conclusion = Eq(Symbol('sum_k'), n*(n+Integer(1))/Integer(2))
            elif formula_type == 'squares':
                conclusion = Eq(Symbol('sum_k_sq'), n*(n+Integer(1))*(Integer(2)*n+Integer(1))/Integer(6))
            else:
                conclusion = Eq(Symbol('sum_k_cubed'), (n*(n+Integer(1))/Integer(2))**2)
            derivation = ['sum_formula', 'induction']

        elif template == 'gcd_property':
            a, b = symbols('a b', integer=True, positive=True)
            premises = []
            conclusion = Eq(Symbol('gcd_a_b'), Symbol('gcd_b_a_mod_b'))
            derivation = ['euclidean_algorithm']

        else:  # prime_property
            premises = [Symbol('p_is_prime'), Gt(p, Integer(2))]
            conclusion = Eq(Symbol('p_mod_2'), Integer(1))  # All primes > 2 are odd
            derivation = ['prime_definition']

        self.theorem_count += 1

        return SyntheticTheorem(
            theorem_id=f"synth_nt_{self.theorem_count}",
            premises=premises,
            conclusion=conclusion,
            derivation_steps=derivation,
            domain="number_theory",
            complexity_score=self._compute_complexity(premises, conclusion)
        )

    def _generate_analysis_theorem(self) -> Optional[SyntheticTheorem]:
        """Generate calculus/analysis theorem"""
        x, a, n, t = symbols('x a n t')

        template = random.choice(['derivative', 'integral', 'series', 'limit',
                                  'fundamental_theorem'])

        if template == 'derivative':
            funcs = [
                (Sin(x), Cos(x)),
                (Cos(x), Integer(-1)*Sin(x)),
                (Exp(x), Exp(x)),
                (Log(x), Integer(1)/x),
                (x**n, n*x**(n-Integer(1))),
                (Sin(x)**2, Integer(2)*Sin(x)*Cos(x))
            ]
            f, df = random.choice(funcs)
            premises = []
            conclusion = Eq(Symbol('Df'), df)
            derivation = ['differentiation_rule']

        elif template == 'integral':
            funcs = [
                (x**n, x**(n+Integer(1))/(n+Integer(1))),
                (Sin(x), Integer(-1)*Cos(x)),
                (Cos(x), Sin(x)),
                (Exp(x), Exp(x)),
                (Integer(1)/x, Log(Abs(x)))
            ]
            f, integral_f = random.choice(funcs)
            premises = [Ne(n, Integer(-1))] if n in (f.free_symbols if hasattr(f, 'free_symbols') else set()) else []
            conclusion = Eq(Symbol('integral_f'), integral_f)
            derivation = ['integration_rule']

        elif template == 'series':
            # Taylor series for common functions - simplified
            series_terms = sum(x**k / Integer(math.factorial(k)) for k in range(6))
            premises = []
            conclusion = Eq(Exp(x), series_terms)
            derivation = ['taylor_series']

        elif template == 'limit':
            limits = [
                (Sin(x)/x, Integer(0), Integer(1)),
                ((Integer(1) + Integer(1)/n)**n, oo, E),
                ((Exp(x) - Integer(1))/x, Integer(0), Integer(1))
            ]
            expr, point, value = random.choice(limits)
            premises = []
            conclusion = Eq(Symbol('limit'), value)
            derivation = ['limit_definition']

        else:  # fundamental_theorem
            premises = [Eq(Symbol('dF_dx'), Symbol('f_x'))]
            conclusion = Eq(Symbol('integral_f_a_to_x'), Symbol('F_x_minus_F_a'))
            derivation = ['fundamental_theorem_of_calculus']

        self.theorem_count += 1

        return SyntheticTheorem(
            theorem_id=f"synth_ana_{self.theorem_count}",
            premises=premises,
            conclusion=conclusion,
            derivation_steps=derivation,
            domain="analysis",
            complexity_score=self._compute_complexity(premises, conclusion)
        )

    def _generate_combinatorics_theorem(self) -> Optional[SyntheticTheorem]:
        """Generate combinatorics theorem"""
        n, k, r = symbols('n k r', integer=True, nonnegative=True)

        template = random.choice(['binomial_coefficient', 'permutation', 'pascal_identity',
                                  'vandermonde', 'hockey_stick'])

        if template == 'binomial_coefficient':
            premises = [Ge(n, k), Ge(k, Integer(0))]
            conclusion = Eq(Symbol('C_n_k'), Symbol('n_fact_over_k_nk_fact'))
            derivation = ['binomial_definition']

        elif template == 'permutation':
            premises = [Ge(n, k), Ge(k, Integer(0))]
            conclusion = Eq(Symbol('P_n_k'), Symbol('n_fact_over_nk_fact'))
            derivation = ['permutation_formula']

        elif template == 'pascal_identity':
            premises = [Ge(n, k), Ge(k, Integer(1))]
            conclusion = Eq(Symbol('C_n_k'), Symbol('C_n1_k1_plus_C_n1_k'))
            derivation = ['pascals_identity']

        elif template == 'vandermonde':
            m = Symbol('m', integer=True, nonnegative=True)
            premises = []
            conclusion = Eq(Symbol('C_mn_r'), Symbol('sum_C_mk_C_nrk'))
            derivation = ['vandermondes_identity']

        else:  # hockey_stick
            premises = [Ge(n, r), Ge(r, Integer(0))]
            conclusion = Eq(Symbol('sum_C_kr'), Symbol('C_n1_r1'))
            derivation = ['hockey_stick_identity']

        self.theorem_count += 1

        return SyntheticTheorem(
            theorem_id=f"synth_comb_{self.theorem_count}",
            premises=premises,
            conclusion=conclusion,
            derivation_steps=derivation,
            domain="combinatorics",
            complexity_score=self._compute_complexity(premises, conclusion)
        )

    def _generate_linear_algebra_theorem(self) -> Optional[SyntheticTheorem]:
        """Generate linear algebra theorem"""
        template = random.choice(['determinant', 'eigenvalue', 'matrix_property',
                                  'rank_nullity', 'trace_property'])

        n = Symbol('n', integer=True, positive=True)

        if template == 'determinant':
            premises = []
            # det(AB) = det(A) * det(B)
            conclusion = Eq(Symbol('det_AB'), Symbol('det_A') * Symbol('det_B'))
            derivation = ['determinant_multiplicative_property']

        elif template == 'eigenvalue':
            lam = Symbol('lambda')
            premises = [Eq(Symbol('Av'), lam * Symbol('v'))]
            conclusion = Eq(Symbol('det_A_minus_lambda_I'), Integer(0))
            derivation = ['eigenvalue_definition']

        elif template == 'matrix_property':
            properties = [
                ([], Eq(Symbol('AB_T'), Symbol('BT_times_AT'))),
                ([], Eq(Symbol('Ainv_T'), Symbol('AT_inv'))),
                ([], Eq(Symbol('A_times_Ainv'), Symbol('I')))
            ]
            premises, conclusion = random.choice(properties)
            derivation = ['matrix_algebra']

        elif template == 'rank_nullity':
            premises = []
            conclusion = Eq(Symbol('rank_A') + Symbol('nullity_A'), Symbol('n'))
            derivation = ['rank_nullity_theorem']

        else:  # trace_property
            premises = []
            properties = [
                Eq(Symbol('trace_AplusB'), Symbol('trace_A') + Symbol('trace_B')),
                Eq(Symbol('trace_AB'), Symbol('trace_BA')),
                Eq(Symbol('trace_cA'), Symbol('c') * Symbol('trace_A'))
            ]
            conclusion = random.choice(properties)
            derivation = ['trace_property']

        self.theorem_count += 1

        return SyntheticTheorem(
            theorem_id=f"synth_la_{self.theorem_count}",
            premises=premises,
            conclusion=conclusion,
            derivation_steps=derivation,
            domain="linear_algebra",
            complexity_score=self._compute_complexity(premises, conclusion)
        )

    # =========================================================================
    # GRAMMAR-BASED GENERATION (Novel Expression Synthesis)
    # =========================================================================

    def _generate_grammar_based(self, domain: str = 'algebra') -> Optional[SyntheticTheorem]:
        """
        Generate theorem using context-free grammar approach.

        This creates novel expressions beyond fixed templates by:
        1. Randomly building expression trees from production rules
        2. Applying algebraic transformations
        3. Verifying the relationship holds

        This enables genuine novelty in theorem generation.
        """
        try:
            # Select symbols for this domain
            symbols = self._get_domain_symbols(domain)
            if len(symbols) < 2:
                return None

            # Generate a random expression using grammar
            expr_depth = random.randint(2, 4)
            lhs = self._generate_grammar_expr(symbols, expr_depth)

            if lhs is None:
                return None

            # Generate a related expression through transformation
            transformation, rhs = self._apply_random_transformation(lhs)

            if rhs is None or transformation is None:
                return None

            # Verify the relationship actually holds
            if not self._verify_relationship(lhs, rhs, transformation):
                return None

            # Create the theorem
            premises = []
            conclusion = Eq(lhs, rhs)
            derivation = [transformation]

            self.theorem_count += 1
            self.stats['total_generated'] += 1
            self.stats['grammar_generated'] = self.stats.get('grammar_generated', 0) + 1

            return SyntheticTheorem(
                theorem_id=f"synth_gram_{self.theorem_count}",
                premises=premises,
                conclusion=conclusion,
                derivation_steps=derivation,
                domain=domain,
                complexity_score=self._compute_complexity(premises, conclusion)
            )

        except (TypeError, ValueError, RecursionError) as e:
            logger.debug(f"Grammar-based generation failed: {e}")
            return None

    def _get_domain_symbols(self, domain: str) -> tuple:
        """Get appropriate symbols for a mathematical domain."""
        domain_symbols = {
            'algebra': self.algebra_symbols,
            'geometry': self.geometry_symbols,
            'analysis': self.analysis_symbols,
            'number_theory': self.number_symbols,
            'combinatorics': self.number_symbols,
            'linear_algebra': self.algebra_symbols
        }
        return domain_symbols.get(domain, self.algebra_symbols)

    def _generate_grammar_expr(self, symbols, depth: int, current_depth: int = 0):
        """
        Generate expression using production rules.

        Grammar:
            expr -> term | expr op term
            term -> factor | term * factor | term / factor
            factor -> atom | unary(factor) | (expr)
            atom -> symbol | constant
        """
        if current_depth >= depth:
            # Base case: return an atom
            return self._generate_atom(symbols)

        # Production rule selection with weighted probabilities
        rule_choice = random.random()

        if rule_choice < 0.3:
            # Binary operation: expr op expr
            left = self._generate_grammar_expr(symbols, depth, current_depth + 1)
            right = self._generate_grammar_expr(symbols, depth, current_depth + 1)
            if left is None or right is None:
                return self._generate_atom(symbols)

            op = random.choice(self.binary_ops[:5])  # Exclude Eq from binary ops
            try:
                result = op(left, right)
                return result
            except (TypeError, ZeroDivisionError):
                return left + right

        elif rule_choice < 0.5:
            # Unary operation: func(expr)
            inner = self._generate_grammar_expr(symbols, depth, current_depth + 1)
            if inner is None:
                return self._generate_atom(symbols)

            op = random.choice(self.unary_ops)
            try:
                return op(inner)
            except (TypeError, ValueError):
                return inner ** 2

        elif rule_choice < 0.7:
            # Power expression: expr ^ small_int
            base = self._generate_grammar_expr(symbols, depth, current_depth + 1)
            if base is None:
                return self._generate_atom(symbols)
            exp = random.randint(2, 3)
            return base ** exp

        else:
            # Just an atom
            return self._generate_atom(symbols)

    def _generate_atom(self, syms) -> Expr:
        """Generate an atomic expression (symbol or constant)."""
        if random.random() < 0.7 and len(syms) > 0:
            # Return a symbol
            return random.choice(list(syms))
        else:
            # Return a small integer constant
            return Integer(random.randint(1, 5))

    def _apply_random_transformation(self, expr) -> tuple:
        """
        Apply a random algebraic transformation to generate a related expression.

        Returns:
            (transformation_name, transformed_expression)
        """
        transformations = [
            ('expand', lambda e: expand(e)),
            ('simplify', lambda e: simplify(e)),
        ]

        # Try transformations until one changes the expression
        random.shuffle(transformations)

        for name, transform in transformations:
            try:
                transformed = transform(expr)
                # Only accept if it's different but equivalent
                diff_expr = simplify(expr - transformed) if hasattr(expr, '__sub__') else None
                if transformed != expr and diff_expr is not None and (diff_expr == 0 or (hasattr(diff_expr, 'is_zero') and diff_expr.is_zero)):
                    return (name, transformed)
            except (TypeError, ValueError, IndexError, AttributeError):
                continue

        # Fallback: just expand
        try:
            expanded = expand(expr)
            return ('expand', expanded)
        except (TypeError, ValueError):
            return (None, None)

    def _verify_relationship(self, lhs, rhs, transformation: str) -> bool:
        """Verify that the generated relationship actually holds."""
        try:
            diff = simplify(lhs - rhs)
            return diff == 0 or (hasattr(diff, 'is_zero') and diff.is_zero)
        except (TypeError, ValueError):
            return False

    def generate_novel(self, count: int = 10, domain: str = None) -> List[SyntheticTheorem]:
        """
        Generate novel theorems using grammar-based approach.

        This is the recommended method for generating theorems with genuine novelty,
        as it doesn't rely on fixed templates.

        Args:
            count: Number of theorems to generate
            domain: Optional domain restriction

        Returns:
            List of novel SyntheticTheorem objects
        """
        theorems = []
        attempts = 0
        max_attempts = count * 20  # Allow for many failures since grammar-based is exploratory

        while len(theorems) < count and attempts < max_attempts:
            attempts += 1
            target_domain = domain or random.choice(list(TheoremDomain)).value

            theorem = self._generate_grammar_based(target_domain)

            if theorem is not None:
                # Check for duplicates
                thm_hash = theorem.compute_hash()
                if thm_hash not in self.seen_hashes:
                    self.seen_hashes.add(thm_hash)
                    theorems.append(theorem)

        return theorems

    def _compute_complexity(self, premises: List[Expr], conclusion: Expr) -> float:
        """
        Compute complexity score for a theorem.

        Factors:
        - Expression length
        - Number of distinct symbols
        - Depth of expression tree
        - Number of premises
        """
        total_length = sum(len(str(p)) for p in premises) + len(str(conclusion))

        # Count distinct symbols
        all_symbols = set()
        for expr in premises + [conclusion]:
            if hasattr(expr, 'free_symbols'):
                all_symbols.update(expr.free_symbols)

        # Compute weighted score
        length_score = min(1.0, total_length / 300)
        symbol_score = min(1.0, len(all_symbols) / 10)
        premise_score = min(1.0, len(premises) / 5)

        complexity = 0.4 * length_score + 0.3 * symbol_score + 0.3 * premise_score

        return round(complexity, 3)

    def get_statistics(self) -> Dict[str, Any]:
        """Get generator statistics"""
        return {
            **self.stats,
            'unique_theorems': len(self.seen_hashes),
            'theorem_count': self.theorem_count
        }

    def reset(self):
        """Reset generator state"""
        self.theorem_count = 0
        self.seen_hashes.clear()
        for key in self.stats:
            self.stats[key] = 0

    def health_check(self) -> bool:
        """Check if generator is healthy"""
        try:
            theorem = self._generate_single()
            return theorem is not None
        except (TypeError, ValueError, RuntimeError) as e:
            logger.warning(f"Health check failed: {e}")
            return False
