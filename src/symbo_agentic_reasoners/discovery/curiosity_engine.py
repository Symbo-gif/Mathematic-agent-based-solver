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
Curiosity Engine - Autonomous Mathematical Exploration
=======================================================

When the system is idle (no user input), the Curiosity Engine:
1. Generates novel mathematical problems to explore
2. Solves them using the solver engine
3. Records interesting discoveries and patterns
4. Learns which areas are most fruitful for exploration
5. Builds mathematical intuition over time

This gives the system "mathematical curiosity" - it explores math
for its own sake, not just on command.

Architecture:
- ProblemGenerator: Creates random but meaningful math problems
- ExplorationTracker: Records what has been explored and learned
- InterestScorer: Evaluates which results are "interesting"
- CuriosityAgent: Coordinates autonomous exploration
"""

import random
import time
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, symbols, Sqrt, Sin, Cos, Tan, Exp, Log,
    pi, E, oo, parse_expr, simplify, expand, Integer, Expr
)

logger = logging.getLogger('symbo_agentic_reasoners.discovery.curiosity')


class ExplorationCategory(Enum):
    """Categories of mathematical exploration."""
    ALGEBRA = 'algebra'
    CALCULUS = 'calculus'
    NUMBER_THEORY = 'number_theory'
    LINEAR_ALGEBRA = 'linear_algebra'
    COMBINATORICS = 'combinatorics'
    ANALYSIS = 'analysis'
    GEOMETRY = 'geometry'


class InterestLevel(Enum):
    """How interesting a discovery is."""
    MUNDANE = 0        # Expected result, nothing special
    NOTABLE = 1        # Somewhat interesting pattern
    INTERESTING = 2    # Worth remembering
    SURPRISING = 3     # Unexpected result
    REMARKABLE = 4     # Significant discovery


@dataclass
class ExplorationResult:
    """Result of an autonomous exploration."""
    problem: str
    category: ExplorationCategory
    solution: Any
    success: bool
    interest_level: InterestLevel
    solve_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""
    related_problems: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'problem': self.problem,
            'category': self.category.value,
            'solution': str(self.solution),
            'success': self.success,
            'interest_level': self.interest_level.value,
            'solve_time_ms': self.solve_time_ms,
            'timestamp': self.timestamp.isoformat(),
            'notes': self.notes,
            'related_problems': self.related_problems
        }


@dataclass
class ExplorationStats:
    """Statistics about exploration sessions."""
    problems_generated: int = 0
    problems_solved: int = 0
    problems_failed: int = 0
    interesting_discoveries: int = 0
    total_time_ms: float = 0
    categories_explored: Dict[str, int] = field(default_factory=dict)
    best_discoveries: List[ExplorationResult] = field(default_factory=list)


class ProblemGenerator:
    """
    Generates random but meaningful mathematical problems.

    Strategies:
    1. Random polynomial generation
    2. Random function composition
    3. Pattern exploration (sequences, series)
    4. Equation system generation
    5. Integration/differentiation of random functions
    6. Number theory explorations
    """

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

        # Common variables
        self.x, self.y, self.z = symbols('x y z')
        self.n, self.k = symbols('n k', integer=True, positive=True)

        # Template functions for composition
        self.base_functions = [
            lambda v: v**2,
            lambda v: v**3,
            lambda v: Sqrt(v),
            lambda v: Sin(v),
            lambda v: Cos(v),
            lambda v: Exp(v),
            lambda v: Log(v),
            lambda v: Integer(1)/v,
            lambda v: v/(v+Integer(1)),
        ]

        # Interesting constants
        self.constants = [Integer(1), Integer(2), Integer(3), Integer(5), Integer(7), pi, E]

    def generate(self, category: Optional[ExplorationCategory] = None) -> Tuple[str, ExplorationCategory]:
        """
        Generate a random problem in the given category.

        Returns:
            Tuple of (problem_string, category)
        """
        if category is None:
            category = random.choice(list(ExplorationCategory))

        generators = {
            ExplorationCategory.ALGEBRA: self._generate_algebra,
            ExplorationCategory.CALCULUS: self._generate_calculus,
            ExplorationCategory.NUMBER_THEORY: self._generate_number_theory,
            ExplorationCategory.LINEAR_ALGEBRA: self._generate_linear_algebra,
            ExplorationCategory.COMBINATORICS: self._generate_combinatorics,
            ExplorationCategory.ANALYSIS: self._generate_analysis,
            ExplorationCategory.GEOMETRY: self._generate_geometry,
        }

        problem = generators[category]()
        return problem, category

    def _generate_algebra(self) -> str:
        """Generate an algebra problem."""
        problem_types = [
            self._random_polynomial_factor,
            self._random_equation_solve,
            self._random_simplification,
            self._random_expansion,
        ]
        return random.choice(problem_types)()

    def _random_polynomial_factor(self) -> str:
        """Generate a polynomial to factor."""
        # Create a polynomial with known factors
        degree = random.randint(2, 4)
        roots = [random.randint(-5, 5) for _ in range(degree)]

        # Build polynomial from roots
        poly = Integer(1)
        for r in roots:
            poly = poly * (self.x - Integer(r))

        expanded = expand(poly)
        return f"factor({expanded})"

    def _random_equation_solve(self) -> str:
        """Generate an equation to solve."""
        # Quadratic or cubic
        a = random.randint(1, 3)
        b = random.randint(-5, 5)
        c = random.randint(-10, 10)

        expr = a * self.x**2 + b * self.x + c
        return f"solve({expr}, x)"

    def _random_simplification(self) -> str:
        """Generate an expression to simplify."""
        # Create a complicated-looking but simplifiable expression
        templates = [
            lambda: (self.x**2 - Integer(1))/(self.x - Integer(1)),
            lambda: (self.x**2 + Integer(2)*self.x + Integer(1))/(self.x + Integer(1)),
            lambda: Sin(self.x)**2 + Cos(self.x)**2,
            lambda: (self.x + Integer(1))**2 - self.x**2 - Integer(2)*self.x,
            lambda: Sqrt(self.x**2),
        ]
        return f"simplify({random.choice(templates)()})"

    def _random_expansion(self) -> str:
        """Generate an expression to expand."""
        n = random.randint(2, 5)
        base = random.choice([self.x + Integer(1), self.x - Integer(1), self.x + Integer(2), Integer(2)*self.x + Integer(1)])
        return f"expand(({base})**{n})"

    def _generate_calculus(self) -> str:
        """Generate a calculus problem."""
        problem_types = [
            self._random_derivative,
            self._random_integral,
            self._random_limit,
            self._random_series,
        ]
        return random.choice(problem_types)()

    def _random_derivative(self) -> str:
        """Generate a differentiation problem."""
        # Compose random functions
        func = self._random_function_composition()
        order = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]

        if order == 1:
            return f"diff({func}, x)"
        else:
            return f"diff({func}, x, {order})"

    def _random_integral(self) -> str:
        """Generate an integration problem."""
        # Use functions known to have closed forms
        integrable = [
            self.x**random.randint(1, 5),
            Sin(self.x),
            Cos(self.x),
            Exp(self.x),
            Integer(1)/(Integer(1) + self.x**2),
            self.x * Exp(-self.x**2),
            Sin(self.x) * Cos(self.x),
        ]
        func = random.choice(integrable)
        return f"integrate({func}, x)"

    def _random_limit(self) -> str:
        """Generate a limit problem."""
        limits = [
            (Sin(self.x)/self.x, 0),
            ((Integer(1) + Integer(1)/self.x)**self.x, oo),
            ((self.x**2 - Integer(1))/(self.x - Integer(1)), 1),
            (Exp(self.x)/self.x**random.randint(1, 5), oo),
            ((Integer(1) - Cos(self.x))/self.x**2, 0),
        ]
        func, point = random.choice(limits)
        return f"limit({func}, x, {point})"

    def _random_series(self) -> str:
        """Generate a Taylor series problem."""
        functions = [Sin(self.x), Cos(self.x), Exp(self.x), Log(Integer(1) + self.x), Integer(1)/(Integer(1) - self.x)]
        func = random.choice(functions)
        order = random.randint(3, 7)
        return f"series({func}, x, 0, {order})"

    def _random_function_composition(self) -> Any:
        """Create a random composed function."""
        # Start with x
        result = self.x

        # Apply 1-3 random transformations
        num_transforms = random.randint(1, 3)
        for _ in range(num_transforms):
            try:
                transform = random.choice(self.base_functions)
                result = transform(result)
            except Exception:
                pass

        return result

    def _generate_number_theory(self) -> str:
        """Generate a number theory problem."""
        problem_types = [
            self._random_factorization,
            self._random_prime_check,
            self._random_gcd_lcm,
            self._random_modular,
        ]
        return random.choice(problem_types)()

    def _random_factorization(self) -> str:
        """Generate a factorization problem."""
        n = random.randint(100, 10000)
        return f"factorint({n})"

    def _random_prime_check(self) -> str:
        """Generate a primality check."""
        n = random.randint(1000, 100000)
        return f"isprime({n})"

    def _random_gcd_lcm(self) -> str:
        """Generate GCD/LCM problem."""
        a = random.randint(10, 1000)
        b = random.randint(10, 1000)
        if random.random() < 0.5:
            return f"gcd({a}, {b})"
        else:
            return f"lcm({a}, {b})"

    def _random_modular(self) -> str:
        """Generate modular arithmetic problem."""
        base = random.randint(2, 10)
        exp_val = random.randint(10, 100)
        mod = random.randint(7, 31)
        return f"pow({base}, {exp_val}, {mod})"

    def _generate_linear_algebra(self) -> str:
        """Generate a linear algebra problem."""
        problem_types = [
            self._random_matrix_det,
            self._random_matrix_eigenvalues,
            self._random_matrix_inverse,
        ]
        return random.choice(problem_types)()

    def _random_matrix_det(self) -> str:
        """Generate a determinant problem."""
        size = random.randint(2, 4)
        entries = [[random.randint(-5, 5) for _ in range(size)] for _ in range(size)]
        matrix_str = str(entries)
        return f"Matrix({matrix_str}).det()"

    def _random_matrix_eigenvalues(self) -> str:
        """Generate an eigenvalue problem."""
        size = random.randint(2, 3)
        entries = [[random.randint(-3, 3) for _ in range(size)] for _ in range(size)]
        matrix_str = str(entries)
        return f"Matrix({matrix_str}).eigenvals()"

    def _random_matrix_inverse(self) -> str:
        """Generate a matrix inverse problem."""
        # Generate invertible matrix
        size = random.randint(2, 3)
        entries = [[random.randint(-3, 3) for _ in range(size)] for _ in range(size)]
        # Make diagonal dominant to ensure invertibility
        for i in range(size):
            entries[i][i] = sum(abs(entries[i][j]) for j in range(size) if j != i) + 1
        matrix_str = str(entries)
        return f"Matrix({matrix_str}).inv()"

    def _generate_combinatorics(self) -> str:
        """Generate a combinatorics problem."""
        n = random.randint(5, 20)
        k = random.randint(1, min(n, 10))

        if random.random() < 0.5:
            return f"binomial({n}, {k})"
        else:
            return f"factorial({n})"

    def _generate_analysis(self) -> str:
        """Generate an analysis problem."""
        # Infinite series, products, etc.
        problem_types = [
            lambda: f"summation(1/n**2, (n, 1, oo))",
            lambda: f"summation(1/factorial(n), (n, 0, oo))",
            lambda: f"summation((-1)**n/n, (n, 1, oo))",
            lambda: f"product((1 - 1/n**2), (n, 2, oo))",
        ]
        return random.choice(problem_types)()

    def _generate_geometry(self) -> str:
        """Generate a geometry problem (via analytic geometry)."""
        # Distance, area calculations
        x1, y1 = random.randint(-10, 10), random.randint(-10, 10)
        x2, y2 = random.randint(-10, 10), random.randint(-10, 10)

        return f"sqrt(({x2} - {x1})**2 + ({y2} - {y1})**2)"


class InterestScorer:
    """
    Evaluates how "interesting" a mathematical result is.

    Criteria for interest:
    - Unexpected simplification (complex -> simple)
    - Special values (0, 1, pi, e, golden ratio)
    - Pattern recognition
    - Novel relationships
    """

    SPECIAL_VALUES = {
        0: "zero",
        1: "unity",
        -1: "negative unity",
        2: "two",
        "pi": "pi",
        "E": "e",
        "oo": "infinity",
    }

    def score(self, problem: str, solution: Any, solve_time_ms: float) -> Tuple[InterestLevel, str]:
        """
        Score how interesting a result is.

        Returns:
            Tuple of (InterestLevel, explanation)
        """
        notes = []
        interest = InterestLevel.MUNDANE

        def upgrade_interest(new_level: InterestLevel):
            """Upgrade interest to new level if it's higher."""
            nonlocal interest
            if new_level.value > interest.value:
                interest = new_level

        if solution is None:
            return InterestLevel.MUNDANE, "Failed to solve"

        # Check for special values
        try:
            # Use native simplify for Expr types, otherwise try to convert
            if isinstance(solution, Expr):
                simplified = simplify(solution)
            else:
                simplified = solution

            # Check for symbolic constants (pi, E, etc.)
            solution_str = str(solution).lower()
            if 'pi' in solution_str:
                notes.append("Result contains pi")
                upgrade_interest(InterestLevel.NOTABLE)
            if solution_str == 'e' or 'exp(1)' in solution_str:
                notes.append("Result contains Euler's number e")
                upgrade_interest(InterestLevel.NOTABLE)

            # Check for special numeric values
            for special, name in self.SPECIAL_VALUES.items():
                if isinstance(special, (int, float)):
                    try:
                        if isinstance(simplified, (int, float)):
                            if simplified == special:
                                notes.append(f"Result equals {name}")
                                upgrade_interest(InterestLevel.NOTABLE)
                        # Check native Integer type
                        elif hasattr(simplified, 'value') and isinstance(simplified.value, (int, float)):
                            if simplified.value == special:
                                notes.append(f"Result equals {name}")
                                upgrade_interest(InterestLevel.NOTABLE)
                        elif hasattr(simplified, 'evalf'):
                            val = simplified.evalf()
                            if isinstance(val, (int, float)) and abs(val - special) < 1e-10:
                                notes.append(f"Result equals {name}")
                                upgrade_interest(InterestLevel.NOTABLE)
                    except Exception:
                        pass

            # Check if result is surprisingly simple
            if isinstance(solution, (int, float)) or (hasattr(solution, 'is_number') and solution.is_number):
                if len(str(problem)) > 30:
                    notes.append("Complex problem simplified to a number")
                    upgrade_interest(InterestLevel.INTERESTING)

            # Check for integer results from non-obvious problems
            if hasattr(simplified, 'is_integer') and simplified.is_integer:
                if 'sqrt' in problem or 'sin' in problem or 'cos' in problem:
                    notes.append("Transcendental expression yields integer")
                    upgrade_interest(InterestLevel.SURPRISING)

            # Fast solutions to complex problems are interesting
            if solve_time_ms < 10 and len(problem) > 50:
                notes.append("Complex problem solved very quickly")
                upgrade_interest(InterestLevel.NOTABLE)

        except Exception:
            pass

        return interest, "; ".join(notes) if notes else ""


class CuriosityEngine:
    """
    Main curiosity engine that coordinates autonomous exploration.

    Usage:
        engine = CuriosityEngine(solver)

        # Explore while idle
        while idle:
            result = engine.explore_one()
            if result.interest_level >= InterestLevel.INTERESTING:
                print(f"Found something interesting: {result}")
    """

    def __init__(self, solver, save_dir: Optional[Path] = None):
        """
        Initialize curiosity engine.

        Args:
            solver: The solver engine to use for solving generated problems
            save_dir: Directory to save discoveries (default: data/curiosity)
        """
        self.solver = solver
        self.generator = ProblemGenerator()
        self.scorer = InterestScorer()

        self.save_dir = save_dir or Path("data/curiosity")
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.stats = ExplorationStats()
        self.explored_problems: Set[str] = set()
        self.discoveries: List[ExplorationResult] = []

        # Configuration
        self.max_solve_time_ms = 5000  # Skip problems that take too long
        self.min_interest_to_save = InterestLevel.NOTABLE

        # Load previous discoveries
        self._load_discoveries()

        print(f"[CuriosityEngine] Initialized with {len(self.discoveries)} previous discoveries")

    def explore_one(self, category: Optional[ExplorationCategory] = None) -> ExplorationResult:
        """
        Generate and solve one random problem.

        Args:
            category: Optional category to explore (random if None)

        Returns:
            ExplorationResult with the outcome
        """
        # Generate problem
        problem, cat = self.generator.generate(category)

        # Skip if already explored
        if problem in self.explored_problems:
            # Try again with a different problem
            return self.explore_one(category)

        self.explored_problems.add(problem)
        self.stats.problems_generated += 1

        # Update category stats
        cat_name = cat.value
        self.stats.categories_explored[cat_name] = self.stats.categories_explored.get(cat_name, 0) + 1

        # Solve
        start_time = time.time()
        success = False
        solution = None

        try:
            solve_result = self.solver.solve(problem)
            success = solve_result.status.value == 'success'
            solution = solve_result.result if success else None
        except Exception as e:
            logger.debug(f"Exploration failed: {e}")

        solve_time_ms = (time.time() - start_time) * 1000
        self.stats.total_time_ms += solve_time_ms

        if success:
            self.stats.problems_solved += 1
        else:
            self.stats.problems_failed += 1

        # Score interest
        interest, notes = self.scorer.score(problem, solution, solve_time_ms)

        if interest.value >= InterestLevel.INTERESTING.value:
            self.stats.interesting_discoveries += 1

        # Create result
        result = ExplorationResult(
            problem=problem,
            category=cat,
            solution=solution,
            success=success,
            interest_level=interest,
            solve_time_ms=solve_time_ms,
            notes=notes
        )

        # Save interesting discoveries
        if interest.value >= self.min_interest_to_save.value:
            self.discoveries.append(result)
            self._save_discovery(result)

            # Keep track of best discoveries
            if len(self.stats.best_discoveries) < 10:
                self.stats.best_discoveries.append(result)
            elif interest.value > min(d.interest_level.value for d in self.stats.best_discoveries):
                # Replace least interesting
                self.stats.best_discoveries.sort(key=lambda d: d.interest_level.value)
                self.stats.best_discoveries[0] = result

        return result

    def explore_session(self, duration_seconds: float = 60,
                       verbose: bool = True) -> List[ExplorationResult]:
        """
        Run an exploration session for a given duration.

        Args:
            duration_seconds: How long to explore
            verbose: Whether to print progress

        Returns:
            List of interesting discoveries from this session
        """
        if verbose:
            print(f"\n[Curiosity] Starting exploration session ({duration_seconds}s)...")

        start_time = time.time()
        session_discoveries = []
        problems_this_session = 0

        while time.time() - start_time < duration_seconds:
            result = self.explore_one()
            problems_this_session += 1

            if result.interest_level.value >= InterestLevel.NOTABLE.value:
                session_discoveries.append(result)

                if verbose and result.interest_level.value >= InterestLevel.INTERESTING.value:
                    print(f"  [!] Found: {result.problem[:60]}...")
                    print(f"      -> {result.solution}")
                    if result.notes:
                        print(f"      Note: {result.notes}")

        if verbose:
            elapsed = time.time() - start_time
            rate = problems_this_session / elapsed if elapsed > 0 else 0
            print(f"\n[Curiosity] Session complete:")
            print(f"  Problems explored: {problems_this_session}")
            print(f"  Interesting finds: {len(session_discoveries)}")
            print(f"  Rate: {rate:.1f} problems/sec")

        return session_discoveries

    def get_statistics(self) -> Dict[str, Any]:
        """Get exploration statistics."""
        return {
            'problems_generated': self.stats.problems_generated,
            'problems_solved': self.stats.problems_solved,
            'problems_failed': self.stats.problems_failed,
            'success_rate': (self.stats.problems_solved / max(1, self.stats.problems_generated)) * 100,
            'interesting_discoveries': self.stats.interesting_discoveries,
            'total_discoveries': len(self.discoveries),
            'categories_explored': self.stats.categories_explored,
            'avg_solve_time_ms': self.stats.total_time_ms / max(1, self.stats.problems_generated),
            'best_discoveries': [d.to_dict() for d in self.stats.best_discoveries[:5]]
        }

    def get_discoveries(self,
                       min_interest: InterestLevel = InterestLevel.NOTABLE,
                       category: Optional[ExplorationCategory] = None,
                       limit: int = 100) -> List[ExplorationResult]:
        """
        Get discoveries matching criteria.

        Args:
            min_interest: Minimum interest level
            category: Filter by category (None for all)
            limit: Maximum number to return

        Returns:
            List of matching discoveries
        """
        results = []

        for d in reversed(self.discoveries):  # Most recent first
            if d.interest_level.value >= min_interest.value:
                if category is None or d.category == category:
                    results.append(d)
                    if len(results) >= limit:
                        break

        return results

    def _save_discovery(self, result: ExplorationResult):
        """Save a discovery to disk."""
        try:
            # Append to discoveries file
            discoveries_file = self.save_dir / "discoveries.jsonl"
            with open(discoveries_file, 'a') as f:
                f.write(json.dumps(result.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Failed to save discovery: {e}")

    def _load_discoveries(self):
        """Load previous discoveries from disk."""
        try:
            discoveries_file = self.save_dir / "discoveries.jsonl"
            if discoveries_file.exists():
                with open(discoveries_file, 'r') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            result = ExplorationResult(
                                problem=data['problem'],
                                category=ExplorationCategory(data['category']),
                                solution=data['solution'],
                                success=data['success'],
                                interest_level=InterestLevel(data['interest_level']),
                                solve_time_ms=data['solve_time_ms'],
                                timestamp=datetime.fromisoformat(data['timestamp']),
                                notes=data.get('notes', '')
                            )
                            self.discoveries.append(result)
                            self.explored_problems.add(result.problem)
                        except Exception:
                            continue
        except Exception as e:
            logger.debug(f"Could not load discoveries: {e}")

    def suggest_exploration(self) -> ExplorationCategory:
        """
        Suggest which category to explore based on history.

        Uses a simple heuristic:
        - Explore less-explored categories more often
        - But also revisit fruitful categories
        """
        # Count explorations per category
        totals = self.stats.categories_explored

        if not totals:
            # No history - pick random
            return random.choice(list(ExplorationCategory))

        # Find least explored
        all_categories = list(ExplorationCategory)
        min_explored = min(totals.get(c.value, 0) for c in all_categories)

        # Pick from least explored (with some randomness)
        least_explored = [c for c in all_categories
                        if totals.get(c.value, 0) <= min_explored + 2]

        return random.choice(least_explored)


# Convenience function for quick exploration
def explore_mathematics(solver, duration_seconds: float = 30) -> List[ExplorationResult]:
    """
    Quick function to explore mathematics autonomously.

    Args:
        solver: The solver engine
        duration_seconds: How long to explore

    Returns:
        List of interesting discoveries
    """
    engine = CuriosityEngine(solver)
    return engine.explore_session(duration_seconds)


if __name__ == "__main__":
    # Demo - just test problem generation
    print("=== Curiosity Engine Demo ===\n")

    generator = ProblemGenerator()
    scorer = InterestScorer()

    print("Generating sample problems:\n")
    for category in ExplorationCategory:
        problem, cat = generator.generate(category)
        print(f"[{cat.value:15}] {problem}")

    print("\n\nTo use with the solver:")
    print("  from symbo_agentic_reasoners.discovery.curiosity_engine import CuriosityEngine")
    print("  engine = CuriosityEngine(solver)")
    print("  discoveries = engine.explore_session(60)  # Explore for 60 seconds")
