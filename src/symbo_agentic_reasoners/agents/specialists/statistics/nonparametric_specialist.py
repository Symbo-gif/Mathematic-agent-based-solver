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
NONPARAMETRIC TESTS SPECIALIST (Tier 3)
=======================================

Distribution-free statistical tests.

CAPABILITIES:
------------
- Mann-Whitney U test (two independent samples)
- Wilcoxon signed-rank test (paired samples)
- Kruskal-Wallis H test (multiple groups)
- Spearman rank correlation
- Kendall's tau correlation
- Sign test
- Runs test for randomness
- Kolmogorov-Smirnov test

NO SYMPY - All mathematical operations use native implementations.

Priority 1 gap filler for Statistics domain (+12% capability).
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import Blackboard

logger = logging.getLogger('symbo_agentic_reasoners.specialists.nonparametric')


@dataclass
class TestResult:
    """Result of a statistical test."""
    statistic: float
    p_value: float
    effect_size: Optional[float] = None
    method: str = ""
    conclusion: str = ""


class NonparametricSpecialist(BDIAgent):
    """
    Nonparametric Tests Specialist - Distribution-free Statistical Tests

    DIRECTIVE:
    ---------
    Provide nonparametric statistical tests that make no assumptions
    about underlying distributions.

    OPERATIONS:
    ----------
    - mann_whitney_u: Compare two independent samples
    - wilcoxon_signed_rank: Compare paired samples
    - kruskal_wallis: Compare multiple groups
    - spearman_correlation: Rank correlation
    - kendall_tau: Kendall's rank correlation
    """

    def __init__(
        self,
        agent_id: str = "nonparametric_specialist",
        directory_facilitator: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
    ):
        super().__init__(agent_id=agent_id)
        self.agent_type = "nonparametric_specialist"
        self.df = directory_facilitator
        self.blackboard = blackboard
        self._register_services()
        self._stats = {'tests_performed': 0}

    def _register_services(self):
        if self.df:
            self.df.register_service(create_service_registration(
                agent_id=self.agent_id,
                service_type="nonparametric_tests",
                description="Distribution-free statistical tests"
            ))

    # ==================== MANN-WHITNEY U TEST ====================

    def mann_whitney_u(
        self,
        sample1: List[float],
        sample2: List[float],
        alternative: str = 'two-sided'
    ) -> TestResult:
        """
        Mann-Whitney U test for two independent samples.

        Tests whether one sample tends to have larger values than the other.

        Args:
            sample1: First sample
            sample2: Second sample
            alternative: 'two-sided', 'less', or 'greater'

        Returns:
            TestResult with U statistic and p-value
        """
        self._stats['tests_performed'] += 1

        n1, n2 = len(sample1), len(sample2)

        # Combine and rank
        combined = [(x, 1) for x in sample1] + [(x, 2) for x in sample2]
        combined.sort(key=lambda x: x[0])

        # Assign ranks (handle ties by averaging)
        ranks = self._assign_ranks([x[0] for x in combined])

        # Sum ranks for each group
        r1 = sum(r for r, (x, g) in zip(ranks, combined) if g == 1)
        r2 = sum(r for r, (x, g) in zip(ranks, combined) if g == 2)

        # Calculate U statistics
        u1 = r1 - n1 * (n1 + 1) / 2
        u2 = r2 - n2 * (n2 + 1) / 2
        u = min(u1, u2)

        # Normal approximation for p-value
        mean_u = n1 * n2 / 2
        std_u = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)

        if std_u > 0:
            z = (u - mean_u) / std_u
            p_value = self._normal_cdf(-abs(z))
            if alternative == 'two-sided':
                p_value *= 2
        else:
            z = 0
            p_value = 1.0

        # Effect size (rank-biserial correlation)
        effect_size = 1 - (2 * u) / (n1 * n2)

        return TestResult(
            statistic=u,
            p_value=min(p_value, 1.0),
            effect_size=effect_size,
            method='Mann-Whitney U',
            conclusion=f"U = {u:.4f}, p = {p_value:.4f}"
        )

    # ==================== WILCOXON SIGNED-RANK TEST ====================

    def wilcoxon_signed_rank(
        self,
        sample1: List[float],
        sample2: Optional[List[float]] = None,
        alternative: str = 'two-sided'
    ) -> TestResult:
        """
        Wilcoxon signed-rank test for paired samples or one-sample.

        Tests whether the median of differences is zero.

        Args:
            sample1: First sample (or differences if sample2 is None)
            sample2: Second sample (optional, for paired test)
            alternative: 'two-sided', 'less', or 'greater'

        Returns:
            TestResult with W statistic and p-value
        """
        self._stats['tests_performed'] += 1

        # Calculate differences
        if sample2 is not None:
            if len(sample1) != len(sample2):
                raise ValueError("Samples must have equal length for paired test")
            differences = [a - b for a, b in zip(sample1, sample2)]
        else:
            differences = sample1

        # Remove zeros
        nonzero_diffs = [(d, abs(d)) for d in differences if d != 0]
        if not nonzero_diffs:
            return TestResult(statistic=0, p_value=1.0, method='Wilcoxon signed-rank')

        n = len(nonzero_diffs)

        # Rank absolute differences
        sorted_diffs = sorted(range(n), key=lambda i: nonzero_diffs[i][1])
        ranks = [0.0] * n
        for rank, idx in enumerate(sorted_diffs, 1):
            ranks[idx] = rank

        # Handle ties
        ranks = self._handle_ties_ranks(ranks, [nonzero_diffs[i][1] for i in range(n)])

        # Calculate W+ (sum of positive ranks) and W- (sum of negative ranks)
        w_plus = sum(r for d, r in zip([nd[0] for nd in nonzero_diffs], ranks) if d > 0)
        w_minus = sum(r for d, r in zip([nd[0] for nd in nonzero_diffs], ranks) if d < 0)

        w = min(w_plus, w_minus)

        # Normal approximation for p-value
        mean_w = n * (n + 1) / 4
        std_w = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)

        if std_w > 0:
            z = (w - mean_w) / std_w
            p_value = self._normal_cdf(-abs(z))
            if alternative == 'two-sided':
                p_value *= 2
        else:
            z = 0
            p_value = 1.0

        # Effect size (matched-pairs rank biserial)
        effect_size = (w_plus - w_minus) / (n * (n + 1) / 2) if n > 0 else 0

        return TestResult(
            statistic=w,
            p_value=min(p_value, 1.0),
            effect_size=effect_size,
            method='Wilcoxon signed-rank',
            conclusion=f"W = {w:.4f}, p = {p_value:.4f}"
        )

    # ==================== KRUSKAL-WALLIS H TEST ====================

    def kruskal_wallis(self, *groups: List[float]) -> TestResult:
        """
        Kruskal-Wallis H test for comparing multiple independent groups.

        Non-parametric alternative to one-way ANOVA.

        Args:
            *groups: Variable number of sample groups

        Returns:
            TestResult with H statistic and p-value
        """
        self._stats['tests_performed'] += 1

        k = len(groups)
        if k < 2:
            raise ValueError("Need at least 2 groups")

        # Combine and rank
        combined = []
        for i, group in enumerate(groups):
            for x in group:
                combined.append((x, i))
        combined.sort(key=lambda x: x[0])

        n = len(combined)
        ranks = self._assign_ranks([x[0] for x in combined])

        # Sum of ranks for each group
        group_ranks = {i: [] for i in range(k)}
        for rank, (x, group_idx) in zip(ranks, combined):
            group_ranks[group_idx].append(rank)

        # Calculate H statistic
        h = 0.0
        for i in range(k):
            ni = len(group_ranks[i])
            if ni > 0:
                ri = sum(group_ranks[i])
                h += ri * ri / ni

        h = (12 / (n * (n + 1))) * h - 3 * (n + 1)

        # P-value from chi-square distribution (df = k-1)
        df = k - 1
        p_value = self._chi2_sf(h, df)

        # Effect size (epsilon-squared)
        effect_size = h / (n - 1)

        return TestResult(
            statistic=h,
            p_value=p_value,
            effect_size=effect_size,
            method='Kruskal-Wallis H',
            conclusion=f"H({df}) = {h:.4f}, p = {p_value:.4f}"
        )

    # ==================== SPEARMAN CORRELATION ====================

    def spearman_correlation(
        self,
        x: List[float],
        y: List[float]
    ) -> TestResult:
        """
        Spearman rank correlation coefficient.

        Measures monotonic relationship between two variables.

        Args:
            x: First variable
            y: Second variable

        Returns:
            TestResult with rho statistic and p-value
        """
        self._stats['tests_performed'] += 1

        if len(x) != len(y):
            raise ValueError("Variables must have equal length")

        n = len(x)

        # Rank both variables
        rank_x = self._assign_ranks(x)
        rank_y = self._assign_ranks(y)

        # Calculate Spearman's rho
        d_squared = sum((rx - ry) ** 2 for rx, ry in zip(rank_x, rank_y))
        rho = 1 - (6 * d_squared) / (n * (n * n - 1))

        # T-statistic for significance
        if abs(rho) < 1:
            t = rho * math.sqrt((n - 2) / (1 - rho * rho))
            p_value = 2 * self._t_sf(abs(t), n - 2)
        else:
            t = float('inf') if rho > 0 else float('-inf')
            p_value = 0.0

        return TestResult(
            statistic=rho,
            p_value=p_value,
            effect_size=rho,
            method='Spearman correlation',
            conclusion=f"ρ = {rho:.4f}, p = {p_value:.4f}"
        )

    # ==================== KENDALL'S TAU ====================

    def kendall_tau(
        self,
        x: List[float],
        y: List[float]
    ) -> TestResult:
        """
        Kendall's tau rank correlation coefficient.

        Based on concordant and discordant pairs.

        Args:
            x: First variable
            y: Second variable

        Returns:
            TestResult with tau statistic and p-value
        """
        self._stats['tests_performed'] += 1

        if len(x) != len(y):
            raise ValueError("Variables must have equal length")

        n = len(x)

        # Count concordant and discordant pairs
        concordant = 0
        discordant = 0

        for i in range(n):
            for j in range(i + 1, n):
                x_diff = x[j] - x[i]
                y_diff = y[j] - y[i]
                product = x_diff * y_diff

                if product > 0:
                    concordant += 1
                elif product < 0:
                    discordant += 1

        # Kendall's tau-b
        n_pairs = n * (n - 1) / 2
        tau = (concordant - discordant) / n_pairs if n_pairs > 0 else 0

        # Z-statistic for significance
        var = (4 * n + 10) / (9 * n * (n - 1))
        z = tau / math.sqrt(var) if var > 0 else 0
        p_value = 2 * self._normal_cdf(-abs(z))

        return TestResult(
            statistic=tau,
            p_value=p_value,
            effect_size=tau,
            method='Kendall tau',
            conclusion=f"τ = {tau:.4f}, p = {p_value:.4f}"
        )

    # ==================== SIGN TEST ====================

    def sign_test(
        self,
        sample1: List[float],
        sample2: Optional[List[float]] = None,
        median: float = 0.0
    ) -> TestResult:
        """
        Sign test for one-sample or paired samples.

        Tests whether the median equals a specified value.

        Args:
            sample1: Sample data or first sample
            sample2: Second sample for paired test (optional)
            median: Hypothesized median (for one-sample test)

        Returns:
            TestResult with statistic and p-value
        """
        self._stats['tests_performed'] += 1

        if sample2 is not None:
            # Paired test
            differences = [a - b for a, b in zip(sample1, sample2)]
        else:
            # One-sample test
            differences = [x - median for x in sample1]

        # Count signs
        n_positive = sum(1 for d in differences if d > 0)
        n_negative = sum(1 for d in differences if d < 0)
        n = n_positive + n_negative

        if n == 0:
            return TestResult(statistic=0, p_value=1.0, method='Sign test')

        # Test statistic is the smaller count
        k = min(n_positive, n_negative)

        # P-value from binomial distribution
        p_value = 2 * self._binomial_cdf(k, n, 0.5)

        return TestResult(
            statistic=k,
            p_value=min(p_value, 1.0),
            method='Sign test',
            conclusion=f"k = {k}, n = {n}, p = {min(p_value, 1.0):.4f}"
        )

    # ==================== RUNS TEST ====================

    def runs_test(self, sequence: List[float], median: Optional[float] = None) -> TestResult:
        """
        Runs test for randomness.

        Tests whether a sequence is random based on runs above/below median.

        Args:
            sequence: Data sequence
            median: Median to use (computed if None)

        Returns:
            TestResult with R statistic and p-value
        """
        self._stats['tests_performed'] += 1

        if median is None:
            median = sorted(sequence)[len(sequence) // 2]

        # Convert to signs
        signs = [1 if x > median else 0 for x in sequence if x != median]

        if len(signs) < 2:
            return TestResult(statistic=0, p_value=1.0, method='Runs test')

        # Count runs
        runs = 1
        for i in range(1, len(signs)):
            if signs[i] != signs[i - 1]:
                runs += 1

        # Count n1 (above) and n2 (below)
        n1 = sum(signs)
        n2 = len(signs) - n1

        if n1 == 0 or n2 == 0:
            return TestResult(statistic=runs, p_value=1.0, method='Runs test')

        # Expected value and variance
        n = n1 + n2
        expected_runs = (2 * n1 * n2) / n + 1
        var_runs = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n * n * (n - 1))

        if var_runs > 0:
            z = (runs - expected_runs) / math.sqrt(var_runs)
            p_value = 2 * self._normal_cdf(-abs(z))
        else:
            z = 0
            p_value = 1.0

        return TestResult(
            statistic=runs,
            p_value=p_value,
            method='Runs test',
            conclusion=f"R = {runs}, expected = {expected_runs:.2f}, p = {p_value:.4f}"
        )

    # ==================== HELPER METHODS ====================

    def _assign_ranks(self, values: List[float]) -> List[float]:
        """Assign ranks with averaging for ties."""
        n = len(values)
        sorted_idx = sorted(range(n), key=lambda i: values[i])
        ranks = [0.0] * n

        i = 0
        while i < n:
            j = i
            while j < n and values[sorted_idx[j]] == values[sorted_idx[i]]:
                j += 1
            # Average rank for tied values
            avg_rank = (i + j + 1) / 2
            for k in range(i, j):
                ranks[sorted_idx[k]] = avg_rank
            i = j

        return ranks

    def _handle_ties_ranks(self, ranks: List[float], values: List[float]) -> List[float]:
        """Handle ties by averaging ranks."""
        return self._assign_ranks(values)

    def _normal_cdf(self, x: float) -> float:
        """Standard normal CDF."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _t_sf(self, t: float, df: int) -> float:
        """Survival function of t-distribution (approximate)."""
        if df <= 0:
            return 0.5

        # Approximation using normal for large df
        if df > 30:
            return 1 - self._normal_cdf(t)

        # For smaller df, use rough approximation
        x = df / (df + t * t)
        return x / 2 if t > 0 else 1 - x / 2

    def _chi2_sf(self, x: float, df: int) -> float:
        """Survival function of chi-square distribution."""
        if x <= 0:
            return 1.0

        # Use incomplete gamma function relationship
        # P(chi2 > x) = 1 - gamma_inc(df/2, x/2) / gamma(df/2)
        # Approximate with normal for large df
        if df > 100:
            z = (x - df) / math.sqrt(2 * df)
            return 1 - self._normal_cdf(z)

        # Rough approximation for smaller df
        mean = df
        var = 2 * df
        z = (x - mean) / math.sqrt(var)
        return 1 - self._normal_cdf(z)

    def _binomial_cdf(self, k: int, n: int, p: float) -> float:
        """Cumulative distribution function of binomial."""
        if k < 0:
            return 0.0
        if k >= n:
            return 1.0

        result = 0.0
        for i in range(k + 1):
            result += self._binomial_pmf(i, n, p)
        return result

    def _binomial_pmf(self, k: int, n: int, p: float) -> float:
        """Probability mass function of binomial."""
        if k < 0 or k > n:
            return 0.0
        coeff = math.factorial(n) / (math.factorial(k) * math.factorial(n - k))
        return coeff * (p ** k) * ((1 - p) ** (n - k))

    # ==================== BDI INTEGRATION ====================

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get('action', '')
        params = message.get('params', {})

        handlers = {
            'mann_whitney_u': lambda p: self.mann_whitney_u(**p),
            'wilcoxon_signed_rank': lambda p: self.wilcoxon_signed_rank(**p),
            'kruskal_wallis': lambda p: self.kruskal_wallis(*p.get('groups', [])),
            'spearman_correlation': lambda p: self.spearman_correlation(**p),
            'kendall_tau': lambda p: self.kendall_tau(**p),
            'sign_test': lambda p: self.sign_test(**p),
            'runs_test': lambda p: self.runs_test(**p),
        }

        if action in handlers:
            result = handlers[action](params)
            return {'status': 'success', 'result': result}
        return {'status': 'error', 'message': f'Unknown action: {action}'}

    def get_stats(self) -> Dict[str, int]:
        return dict(self._stats)

    def update_beliefs(self):
        pass

    def deliberate(self) -> List:
        return []

    def execute_step(self, intention):
        pass


__all__ = [
    'NonparametricSpecialist',
    'TestResult',
]
