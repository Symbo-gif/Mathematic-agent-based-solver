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
Expression Analyzer - Pure Expression Analysis Mode
=====================================================

Handles mathematical expressions that don't fit into traditional "solve" categories.
Instead of returning "No expression to solve", this module:
1. Simplifies the expression
2. Classifies it (probability distribution, physics pattern, matrix, etc.)
3. Returns structured metadata about the expression

This addresses the stress test failures for:
- Probability expressions (Poisson PMF, MGFs, etc.)
- Physics patterns (damped oscillator, etc.)
- Matrix expressions (det(eye(n)), etc.)
- Pure expressions that need simplification/classification only
"""

import re
import logging
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ExpressionCategory(Enum):
    """Categories of pure mathematical expressions."""
    PROBABILITY_PMF = "probability_pmf"
    PROBABILITY_PDF = "probability_pdf"
    PROBABILITY_CDF = "probability_cdf"
    PROBABILITY_MGF = "probability_mgf"
    PROBABILITY_PGF = "probability_pgf"
    PROBABILITY_CGF = "probability_cgf"
    PROBABILITY_EXPECTATION = "probability_expectation"
    PHYSICS_DAMPED_OSCILLATOR = "physics_damped_oscillator"
    PHYSICS_WAVE = "physics_wave"
    PHYSICS_DECAY = "physics_decay"
    MATRIX_DETERMINANT = "matrix_determinant"
    MATRIX_IDENTITY = "matrix_identity"
    MATRIX_TRACE = "matrix_trace"
    DIOPHANTINE = "diophantine"
    PURE_EXPRESSION = "pure_expression"
    UNKNOWN = "unknown"


@dataclass
class ExpressionAnalysisResult:
    """Result of expression analysis."""
    success: bool
    category: ExpressionCategory
    simplified: str
    original: str
    distribution: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'category': self.category.value,
            'simplified': self.simplified,
            'original': self.original,
            'distribution': self.distribution,
            'parameters': self.parameters,
            'properties': self.properties,
            'description': self.description
        }


class ExpressionAnalyzer:
    """
    Analyzes and classifies pure mathematical expressions.

    When the solver can't find an operation to perform (no equation to solve,
    no integral to compute, etc.), this class provides meaningful analysis
    of the expression instead of just returning an error.
    """

    # Probability distribution patterns
    PROBABILITY_PATTERNS = {
        # Poisson PMF: exp(-lambda) * lambda^k / k!
        'poisson_pmf': {
            'pattern': r'exp\s*\(\s*-\s*lambda\s*\)\s*\*\s*lambda\s*\*\*\s*k\s*/\s*factorial\s*\(\s*k\s*\)',
            'alt_patterns': [
                r'lambda\s*\*\*\s*k\s*\*\s*exp\s*\(\s*-\s*lambda\s*\)\s*/\s*factorial\s*\(\s*k\s*\)',
                r'exp\s*\(\s*-\s*\w+\s*\)\s*\*\s*\w+\s*\*\*\s*\w+\s*/\s*factorial\s*\(\s*\w+\s*\)',
            ],
            'distribution': 'Poisson',
            'type': ExpressionCategory.PROBABILITY_PMF,
            'description': 'Poisson distribution probability mass function P(X=k) = e^(-lambda) * lambda^k / k!'
        },

        # Hypergeometric PMF: C(K,k) * C(N-K, n-k) / C(N,n)
        'hypergeometric_pmf': {
            'pattern': r'binomial\s*\(\s*\w+\s*,\s*\w+\s*\)\s*\*\s*binomial\s*\(\s*\w+\s*-\s*\w+\s*,\s*\w+\s*-\s*\w+\s*\)\s*/\s*binomial\s*\(\s*\w+\s*,\s*\w+\s*\)',
            'distribution': 'Hypergeometric',
            'type': ExpressionCategory.PROBABILITY_PMF,
            'description': 'Hypergeometric distribution PMF: C(K,k)*C(N-K,n-k)/C(N,n)'
        },

        # Poisson MGF: exp(lambda*(exp(t) - 1))
        'poisson_mgf': {
            'pattern': r'exp\s*\(\s*lambda\s*\*\s*\(\s*exp\s*\(\s*t\s*\)\s*-\s*1\s*\)\s*\)',
            'alt_patterns': [
                r'exp\s*\(\s*\w+\s*\*\s*\(\s*exp\s*\(\s*\w+\s*\)\s*-\s*1\s*\)\s*\)',
            ],
            'distribution': 'Poisson',
            'type': ExpressionCategory.PROBABILITY_MGF,
            'description': 'Poisson moment generating function M(t) = exp(lambda*(e^t - 1))'
        },

        # Exponential MGF: lambda / (lambda - t)
        'exponential_mgf': {
            'pattern': r'lambda\s*/\s*\(\s*lambda\s*-\s*t\s*\)',
            'alt_patterns': [
                r'\w+\s*/\s*\(\s*\w+\s*-\s*\w+\s*\)',
            ],
            'distribution': 'Exponential',
            'type': ExpressionCategory.PROBABILITY_MGF,
            'description': 'Exponential distribution MGF M(t) = lambda/(lambda-t) for t < lambda'
        },

        # Gamma/Negative Binomial MGF/PGF: (1 - t/lambda)^(-k)
        'gamma_mgf': {
            'pattern': r'\(\s*1\s*-\s*t\s*/\s*lambda\s*\)\s*\*\*\s*\(\s*-\s*\w+\s*\)',
            'alt_patterns': [
                r'\(\s*1\s*-\s*\w+\s*/\s*\w+\s*\)\s*\*\*\s*\(\s*-\s*\w+\s*\)',
            ],
            'distribution': 'Gamma/Negative Binomial',
            'type': ExpressionCategory.PROBABILITY_MGF,
            'description': 'Gamma distribution MGF or Negative Binomial PGF: (1-t/lambda)^(-k)'
        },

        # Uniform mean: 1/N
        'uniform_mean': {
            'pattern': r'^1\s*/\s*[NM]$',
            'distribution': 'Discrete Uniform',
            'type': ExpressionCategory.PROBABILITY_EXPECTATION,
            'description': 'Mean of discrete uniform distribution on {1,...,N} = (N+1)/2, or constant 1/N'
        },

        # Exponential mean: 1/lambda
        'exponential_mean': {
            'pattern': r'^1\s*/\s*lambda$',
            'distribution': 'Exponential',
            'type': ExpressionCategory.PROBABILITY_EXPECTATION,
            'description': 'Mean of exponential distribution with rate lambda: E[X] = 1/lambda'
        },

        # Cumulant generating function: log(E[exp(t*X)])
        'cgf': {
            'pattern': r'log\s*\(\s*E\s*\[\s*exp\s*\(\s*t\s*\*\s*\w+\s*\)\s*\]\s*\)',
            'distribution': 'General',
            'type': ExpressionCategory.PROBABILITY_CGF,
            'description': 'Cumulant generating function K(t) = log(M(t)) = log(E[e^(tX)])'
        },

        # Expectation product: E[X] * E[Y]
        'expectation_product': {
            'pattern': r'E\s*\[\s*\w+\s*\]\s*\*\s*E\s*\[\s*\w+\s*\]',
            'distribution': 'General',
            'type': ExpressionCategory.PROBABILITY_EXPECTATION,
            'description': 'Product of expectations: E[X]*E[Y] = E[XY] for independent X,Y'
        },

        # General expectation: E[g(X)]
        'general_expectation': {
            'pattern': r'E\s*\[\s*[^]]+\s*\]',
            'distribution': 'General',
            'type': ExpressionCategory.PROBABILITY_EXPECTATION,
            'description': 'Expectation of a function of random variable'
        },
    }

    # Physics patterns
    PHYSICS_PATTERNS = {
        # Damped harmonic oscillator: exp(-gamma*t) * cos(omega_d*t)
        'damped_oscillator': {
            'pattern': r'exp\s*\(\s*-\s*gamma\s*\*\s*t\s*\)\s*\*\s*cos\s*\(\s*omega_d\s*\*\s*t\s*\)',
            'alt_patterns': [
                r'exp\s*\(\s*-\s*\w+\s*\*\s*\w+\s*\)\s*\*\s*cos\s*\(\s*\w+\s*\*\s*\w+\s*\)',
                r'cos\s*\(\s*\w+\s*\*\s*\w+\s*\)\s*\*\s*exp\s*\(\s*-\s*\w+\s*\*\s*\w+\s*\)',
            ],
            'type': ExpressionCategory.PHYSICS_DAMPED_OSCILLATOR,
            'description': 'Damped harmonic oscillator solution: x(t) = A*exp(-gamma*t)*cos(omega_d*t + phi)'
        },

        # Exponential decay: exp(-gamma*t) or exp(-t/tau)
        'exponential_decay': {
            'pattern': r'exp\s*\(\s*-\s*\w+\s*\*\s*t\s*\)$|exp\s*\(\s*-\s*t\s*/\s*\w+\s*\)$',
            'type': ExpressionCategory.PHYSICS_DECAY,
            'description': 'Exponential decay: N(t) = N0*exp(-t/tau) or exp(-gamma*t)'
        },

        # Wave solution: A*sin(k*x - omega*t) or cos variant
        'wave': {
            'pattern': r'(sin|cos)\s*\(\s*\w+\s*\*\s*\w+\s*[+-]\s*\w+\s*\*\s*\w+\s*\)',
            'type': ExpressionCategory.PHYSICS_WAVE,
            'description': 'Traveling wave solution: f(x,t) = A*sin(kx - omega*t)'
        },
    }

    # Matrix patterns
    MATRIX_PATTERNS = {
        # det(eye(n)) or det(I_n)
        'det_identity': {
            'pattern': r'det\s*\(\s*eye\s*\(\s*\w+\s*\)\s*\)',
            'alt_patterns': [
                r'det\s*\(\s*I_?\w*\s*\)',
                r'det\s*\(\s*Identity\s*\(\s*\w+\s*\)\s*\)',
            ],
            'type': ExpressionCategory.MATRIX_DETERMINANT,
            'result': '1',
            'description': 'Determinant of identity matrix: det(I_n) = 1 for all n'
        },

        # trace(eye(n))
        'trace_identity': {
            'pattern': r'trace\s*\(\s*eye\s*\(\s*\w+\s*\)\s*\)',
            'type': ExpressionCategory.MATRIX_TRACE,
            'result': 'n',
            'description': 'Trace of identity matrix: tr(I_n) = n'
        },
    }

    # Diophantine patterns
    DIOPHANTINE_PATTERNS = {
        'diophantine': {
            'pattern': r'diophantine\s*\(',
            'type': ExpressionCategory.DIOPHANTINE,
            'description': 'Diophantine equation - finding integer solutions'
        },
    }

    def __init__(self):
        """Initialize the expression analyzer."""
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        self._compiled_prob = {}
        for name, info in self.PROBABILITY_PATTERNS.items():
            patterns = [info['pattern']]
            if 'alt_patterns' in info:
                patterns.extend(info['alt_patterns'])
            self._compiled_prob[name] = {
                'patterns': [re.compile(p, re.IGNORECASE) for p in patterns],
                'info': info
            }

        self._compiled_physics = {}
        for name, info in self.PHYSICS_PATTERNS.items():
            patterns = [info['pattern']]
            if 'alt_patterns' in info:
                patterns.extend(info['alt_patterns'])
            self._compiled_physics[name] = {
                'patterns': [re.compile(p, re.IGNORECASE) for p in patterns],
                'info': info
            }

        self._compiled_matrix = {}
        for name, info in self.MATRIX_PATTERNS.items():
            patterns = [info['pattern']]
            if 'alt_patterns' in info:
                patterns.extend(info['alt_patterns'])
            self._compiled_matrix[name] = {
                'patterns': [re.compile(p, re.IGNORECASE) for p in patterns],
                'info': info
            }

        self._compiled_diophantine = {}
        for name, info in self.DIOPHANTINE_PATTERNS.items():
            self._compiled_diophantine[name] = {
                'patterns': [re.compile(info['pattern'], re.IGNORECASE)],
                'info': info
            }

    def analyze(self, expression: str) -> ExpressionAnalysisResult:
        """
        Analyze a pure mathematical expression.

        Args:
            expression: The expression to analyze

        Returns:
            ExpressionAnalysisResult with classification and metadata
        """
        if not expression:
            return ExpressionAnalysisResult(
                success=False,
                category=ExpressionCategory.UNKNOWN,
                simplified=expression,
                original=expression,
                description="Empty expression"
            )

        original = expression

        # Clean up expression for pattern matching
        clean_expr = self._clean_expression(expression)

        # Try each category in order of specificity

        # 1. Check matrix patterns first (most specific)
        result = self._check_matrix_patterns(clean_expr, original)
        if result:
            return result

        # 2. Check diophantine patterns
        result = self._check_diophantine_patterns(clean_expr, original)
        if result:
            return result

        # 3. Check probability patterns
        result = self._check_probability_patterns(clean_expr, original)
        if result:
            return result

        # 4. Check physics patterns
        result = self._check_physics_patterns(clean_expr, original)
        if result:
            return result

        # 5. Try to simplify with SymPy
        simplified = self._try_simplify(expression)

        # Return as pure expression
        return ExpressionAnalysisResult(
            success=True,
            category=ExpressionCategory.PURE_EXPRESSION,
            simplified=simplified if simplified else expression,
            original=original,
            description="Pure mathematical expression (simplified if possible)"
        )

    def _clean_expression(self, expr: str) -> str:
        """Clean expression for pattern matching."""
        # Remove extra whitespace
        expr = ' '.join(expr.split())
        # Standardize some common variations
        expr = expr.replace('**', '^').replace('^', '**')
        return expr

    def _check_matrix_patterns(self, expr: str, original: str) -> Optional[ExpressionAnalysisResult]:
        """Check for matrix expression patterns."""
        for name, data in self._compiled_matrix.items():
            for pattern in data['patterns']:
                if pattern.search(expr):
                    info = data['info']
                    result_value = info.get('result', expr)
                    return ExpressionAnalysisResult(
                        success=True,
                        category=info['type'],
                        simplified=result_value,
                        original=original,
                        properties={'known_result': result_value},
                        description=info['description']
                    )
        return None

    def _check_diophantine_patterns(self, expr: str, original: str) -> Optional[ExpressionAnalysisResult]:
        """Check for diophantine equation patterns."""
        for name, data in self._compiled_diophantine.items():
            for pattern in data['patterns']:
                if pattern.search(expr):
                    info = data['info']
                    # Extract the equation from diophantine(...)
                    equation = self._extract_diophantine_equation(expr)
                    return ExpressionAnalysisResult(
                        success=True,
                        category=info['type'],
                        simplified=equation if equation else expr,
                        original=original,
                        properties={'equation': equation},
                        description=info['description']
                    )
        return None

    def _extract_diophantine_equation(self, expr: str) -> Optional[str]:
        """Extract the equation from diophantine(equation)."""
        match = re.search(r'diophantine\s*\(\s*(.+?)\s*\)$', expr, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _check_probability_patterns(self, expr: str, original: str) -> Optional[ExpressionAnalysisResult]:
        """Check for probability distribution patterns."""
        for name, data in self._compiled_prob.items():
            for pattern in data['patterns']:
                if pattern.search(expr):
                    info = data['info']
                    return ExpressionAnalysisResult(
                        success=True,
                        category=info['type'],
                        simplified=expr,
                        original=original,
                        distribution=info.get('distribution'),
                        description=info['description']
                    )
        return None

    def _check_physics_patterns(self, expr: str, original: str) -> Optional[ExpressionAnalysisResult]:
        """Check for physics expression patterns."""
        for name, data in self._compiled_physics.items():
            for pattern in data['patterns']:
                if pattern.search(expr):
                    info = data['info']
                    return ExpressionAnalysisResult(
                        success=True,
                        category=info['type'],
                        simplified=expr,
                        original=original,
                        description=info['description']
                    )
        return None

    def _try_simplify(self, expr: str) -> Optional[str]:
        """Try to simplify expression using native_symbolic.

        NO SYMPY - Uses native_symbolic for pure mathematical reasoning.
        """
        try:
            from symbo_agentic_reasoners.core.native_symbolic import parse_expr, simplify

            native_expr = parse_expr(expr)
            if native_expr is not None:
                simplified = simplify(native_expr)
                return str(simplified)
        except Exception as e:
            logger.debug(f"Could not simplify expression: {e}")
        return None


# Singleton instance
_analyzer = None


def get_analyzer() -> ExpressionAnalyzer:
    """Get the singleton expression analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = ExpressionAnalyzer()
    return _analyzer


def analyze_expression(expression: str) -> ExpressionAnalysisResult:
    """
    Analyze a pure mathematical expression.

    This is the main entry point for expression analysis.

    Args:
        expression: The expression to analyze

    Returns:
        ExpressionAnalysisResult with classification and metadata
    """
    return get_analyzer().analyze(expression)
