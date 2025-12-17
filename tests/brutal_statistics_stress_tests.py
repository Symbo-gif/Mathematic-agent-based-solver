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
BRUTAL STATISTICS STRESS TESTS
==============================

50 research-level stress tests designed to BREAK the statistics domain specialists:
- BayesianInferenceEngine
- DistributionSpecialist
- FrequentistAgent
- StochasticProcessAnalyzer
- RegressionSpecialist
- NonparametricSpecialist

These tests target fundamental numerical, algorithmic, and theoretical weaknesses.
Each test is designed to expose edge cases that would occur in real-world research
but that naive implementations fail to handle correctly.

Categories:
- MCMC_MULTIMODAL: Multimodal posteriors with 10+ modes
- HEAVY_TAIL: Heavy-tailed distributions (Cauchy, Pareto alpha<1)
- HYPOTHESIS_EDGE: Hypothesis testing edge cases
- MARKOV_PATHOLOGICAL: Near-periodic and reducible chains
- REGRESSION_SINGULAR: Perfect multicollinearity and ill-conditioning
- BOOTSTRAP_INFINITE: Bootstrap on infinite-variance distributions
- BAYESIAN_IMPROPER: Improper priors and non-conjugate combinations
- EXTREME_VALUE: Tail quantiles at 1e-9 probability
- NONPARAM_TIES: Massive ties in nonparametric tests
- MIXTURE_OVERLAP: Nearly-identical mixture components
"""

import math
from typing import Dict, Any, List, Optional

# ============================================================================
# BRUTAL STATISTICS STRESS TEST DEFINITIONS
# ============================================================================

BRUTAL_STATISTICS_TESTS: List[Dict[str, Any]] = [

    # ========================================================================
    # CATEGORY 1: MCMC ON MULTIMODAL POSTERIORS (Tests 001-005)
    # Target: BayesianInferenceEngine
    # ========================================================================

    {
        "test_id": "STAT_001",
        "category": "MCMC_MULTIMODAL",
        "input": {
            "operation": "mcmc_posterior",
            "prior": "uniform(-100, 100)",
            "likelihood": "mixture_gaussian",
            "modes": [
                {"mean": -80, "std": 0.5, "weight": 0.1},
                {"mean": -60, "std": 0.3, "weight": 0.1},
                {"mean": -40, "std": 0.4, "weight": 0.1},
                {"mean": -20, "std": 0.2, "weight": 0.1},
                {"mean": 0, "std": 0.5, "weight": 0.1},
                {"mean": 20, "std": 0.3, "weight": 0.1},
                {"mean": 40, "std": 0.4, "weight": 0.1},
                {"mean": 60, "std": 0.2, "weight": 0.1},
                {"mean": 80, "std": 0.5, "weight": 0.1},
                {"mean": 95, "std": 0.1, "weight": 0.1},
            ],
            "n_samples": 100000,
            "burn_in": 10000
        },
        "expected": {
            "type": "multimodal_posterior",
            "num_modes_detected": 10,
            "mode_recovery_accuracy": "> 0.95",
            "effective_sample_size": "> 1000"
        },
        "difficulty": "brutal",
        "rationale": "10 well-separated modes with varying variances requires sophisticated MCMC (parallel tempering or replica exchange). Standard Metropolis-Hastings will get stuck in one mode."
    },

    {
        "test_id": "STAT_002",
        "category": "MCMC_MULTIMODAL",
        "input": {
            "operation": "mcmc_posterior",
            "prior": "normal(0, 10)",
            "likelihood": "banana_shaped",
            "correlation": 0.999,
            "curvature": 0.1,
            "n_samples": 50000
        },
        "expected": {
            "type": "banana_posterior",
            "ess_per_sample": "> 0.01",
            "r_hat": "< 1.1"
        },
        "difficulty": "extreme",
        "rationale": "The Rosenbrock/banana-shaped posterior has extreme correlation and curvature, causing standard MCMC to have ESS/sample near zero. Requires HMC with tuned mass matrix."
    },

    {
        "test_id": "STAT_003",
        "category": "MCMC_MULTIMODAL",
        "input": {
            "operation": "mcmc_posterior",
            "prior": "cauchy(0, 1)",
            "likelihood": "multimodal_cauchy",
            "modes": [{"loc": i * 5, "scale": 0.1} for i in range(-10, 11)],
            "n_samples": 200000
        },
        "expected": {
            "type": "21_mode_posterior",
            "all_modes_visited": True,
            "mode_weights_accurate": "> 0.90"
        },
        "difficulty": "pathological",
        "rationale": "21 modes with Cauchy tails means infinite variance. Posterior mass at infinity is non-negligible. Standard MCMC theory breaks down completely."
    },

    {
        "test_id": "STAT_004",
        "category": "MCMC_MULTIMODAL",
        "input": {
            "operation": "mcmc_posterior",
            "prior": "uniform_sphere_500d",
            "likelihood": "gaussian_mixture_500d",
            "modes": 12,
            "dimension": 500,
            "mode_separation": "high",
            "n_samples": 1000000
        },
        "expected": {
            "type": "high_dim_multimodal",
            "modes_discovered": 12,
            "convergence": True
        },
        "difficulty": "pathological",
        "rationale": "500-dimensional space with 12 modes. Curse of dimensionality makes mode-hopping exponentially rare. Requires advanced methods like SMC or variational inference."
    },

    {
        "test_id": "STAT_005",
        "category": "MCMC_MULTIMODAL",
        "input": {
            "operation": "mcmc_posterior",
            "prior": "improper_flat",
            "likelihood": "funnel",
            "funnel_scale": 3.0,
            "dimension": 10,
            "n_samples": 100000
        },
        "expected": {
            "type": "neal_funnel",
            "top_samples_valid": True,
            "bottom_samples_valid": True
        },
        "difficulty": "extreme",
        "rationale": "Neal's funnel has a scale that varies by exp(3) = 20x across dimensions. Standard HMC diverges in the narrow part. Requires reparameterization or NUTS with adaptation."
    },

    # ========================================================================
    # CATEGORY 2: HEAVY-TAILED DISTRIBUTIONS (Tests 006-010)
    # Target: DistributionSpecialist
    # ========================================================================

    {
        "test_id": "STAT_006",
        "category": "HEAVY_TAIL",
        "input": {
            "operation": "pdf_cdf",
            "distribution": "cauchy",
            "location": 0,
            "scale": 1,
            "query_points": [1e-10, 1e-5, 0, 1e5, 1e10, 1e15]
        },
        "expected": {
            "pdf_at_1e15": "approximately 1/(pi * (1 + x^2)) = 3.18e-31",
            "cdf_at_1e15": "approximately 1 - 1/(pi*x) = 1 - 3.18e-16"
        },
        "difficulty": "brutal",
        "rationale": "Cauchy distribution has no mean or variance. Standard numerical CDF computation fails for extreme quantiles due to catastrophic cancellation."
    },

    {
        "test_id": "STAT_007",
        "category": "HEAVY_TAIL",
        "input": {
            "operation": "pdf_cdf",
            "distribution": "pareto",
            "alpha": 0.5,
            "scale": 1.0,
            "query_points": [1, 1e6, 1e12, 1e18]
        },
        "expected": {
            "mean": "undefined (alpha < 1)",
            "variance": "undefined",
            "pdf_at_1e18": "0.5 * 1e-9"
        },
        "difficulty": "extreme",
        "rationale": "Pareto with alpha=0.5 has no moments at all. PDF computation at extreme values requires careful handling of underflow. Tail probability P(X > x) = x^(-0.5) decays slowly."
    },

    {
        "test_id": "STAT_008",
        "category": "HEAVY_TAIL",
        "input": {
            "operation": "quantile",
            "distribution": "levy",
            "location": 0,
            "scale": 1,
            "probabilities": [0.5, 0.9, 0.99, 0.999, 0.9999, 1 - 1e-10]
        },
        "expected": {
            "quantile_0.5": "approximately 2.198",
            "quantile_0.9999": "extremely large (> 1e8)",
            "computation_stable": True
        },
        "difficulty": "extreme",
        "rationale": "Levy distribution has infinite mean and extremely heavy right tail. Quantile at p=1-1e-10 is astronomically large. Numerical inversion of CDF fails without special handling."
    },

    {
        "test_id": "STAT_009",
        "category": "HEAVY_TAIL",
        "input": {
            "operation": "moment_estimation",
            "distribution": "student_t",
            "df": 2.01,
            "sample_size": 1000000,
            "moments_requested": ["mean", "variance", "skewness", "kurtosis"]
        },
        "expected": {
            "mean": "0 (exists)",
            "variance": "approximately 201 (barely finite)",
            "skewness": "undefined (df < 3)",
            "kurtosis": "undefined (df < 4)"
        },
        "difficulty": "brutal",
        "rationale": "Student-t with df=2.01 has variance = 2.01/(2.01-2) = 201 but no skewness or kurtosis. Sample estimates will be wildly unstable even with 1M samples."
    },

    {
        "test_id": "STAT_010",
        "category": "HEAVY_TAIL",
        "input": {
            "operation": "convolution",
            "distributions": ["cauchy(0,1)", "cauchy(0,1)", "cauchy(0,1)"],
            "query_points": [-1e6, 0, 1e6]
        },
        "expected": {
            "result_distribution": "cauchy(0, 3)",
            "pdf_at_0": "1/(3*pi)",
            "convolution_exact": True
        },
        "difficulty": "brutal",
        "rationale": "Sum of Cauchy variables is Cauchy - but NOT via central limit theorem (which requires finite variance). Numerical convolution via FFT will fail due to infinite tails."
    },

    # ========================================================================
    # CATEGORY 3: HYPOTHESIS TESTING EDGE CASES (Tests 011-015)
    # Target: FrequentistAgent
    # ========================================================================

    {
        "test_id": "STAT_011",
        "category": "HYPOTHESIS_EDGE",
        "input": {
            "operation": "t_test",
            "sample_size": 10000000,
            "true_effect_size": 0.001,
            "alpha": 0.05,
            "population_mean": 100,
            "population_std": 1
        },
        "expected": {
            "p_value": "< 1e-20",
            "significant": True,
            "practical_significance": "negligible (d = 0.001)",
            "warning": "statistical_vs_practical_significance"
        },
        "difficulty": "brutal",
        "rationale": "With N=10M, even d=0.001 effect is statistically significant but practically meaningless. System should flag the discrepancy between statistical and practical significance."
    },

    {
        "test_id": "STAT_012",
        "category": "HYPOTHESIS_EDGE",
        "input": {
            "operation": "anova",
            "groups": 1000,
            "samples_per_group": 3,
            "true_effect": 0,
            "alpha": 0.05
        },
        "expected": {
            "expected_false_positives": "~50 at alpha=0.05",
            "multiple_comparison_correction": "required",
            "bonferroni_alpha": 0.00005,
            "fdr_control": "recommended"
        },
        "difficulty": "extreme",
        "rationale": "1000 comparisons with tiny samples and no true effect will yield ~50 false positives. Without multiple comparison correction, conclusions are invalid."
    },

    {
        "test_id": "STAT_013",
        "category": "HYPOTHESIS_EDGE",
        "input": {
            "operation": "t_test",
            "sample1": [1e15, 1e15 + 1, 1e15 + 2],
            "sample2": [1e15 + 3, 1e15 + 4, 1e15 + 5]
        },
        "expected": {
            "catastrophic_cancellation": "likely",
            "use_compensated_summation": True,
            "correct_t_statistic": "computable via differences"
        },
        "difficulty": "brutal",
        "rationale": "Computing variance of values near 1e15 causes catastrophic cancellation in standard formulas. Must use numerically stable algorithms (Welford's method)."
    },

    {
        "test_id": "STAT_014",
        "category": "HYPOTHESIS_EDGE",
        "input": {
            "operation": "chi_square_test",
            "observed": [1, 0, 0, 0, 0, 999],
            "expected_uniform": True,
            "n": 1000,
            "categories": 6
        },
        "expected": {
            "expected_per_cell": "166.67",
            "cells_with_expected_lt_5": 0,
            "chi_square_valid": True,
            "extreme_deviation": "final cell",
            "p_value": "essentially 0"
        },
        "difficulty": "brutal",
        "rationale": "Extreme deviation from uniformity with almost all mass in one cell. Tests whether chi-square handles near-deterministic data correctly."
    },

    {
        "test_id": "STAT_015",
        "category": "HYPOTHESIS_EDGE",
        "input": {
            "operation": "paired_t_test",
            "differences": [0.0] * 100,  # All differences exactly zero
            "alternative": "two-sided"
        },
        "expected": {
            "t_statistic": "undefined (0/0)",
            "p_value": "1.0 or undefined",
            "handling": "special case: no variation"
        },
        "difficulty": "pathological",
        "rationale": "Zero variance in differences makes t-statistic undefined (0/0). System must handle this edge case gracefully without NaN or division by zero error."
    },

    # ========================================================================
    # CATEGORY 4: MARKOV CHAIN PATHOLOGIES (Tests 016-020)
    # Target: StochasticProcessAnalyzer
    # ========================================================================

    {
        "test_id": "STAT_016",
        "category": "MARKOV_PATHOLOGICAL",
        "input": {
            "operation": "stationary_distribution",
            "transition_matrix": [
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
                [1, 0, 0, 0]
            ]
        },
        "expected": {
            "period": 4,
            "is_aperiodic": False,
            "stationary_distribution": [0.25, 0.25, 0.25, 0.25],
            "power_iteration_converges": False
        },
        "difficulty": "brutal",
        "rationale": "Purely periodic chain with period 4. Power iteration oscillates forever and never converges. Must use eigenvalue methods or detect periodicity."
    },

    {
        "test_id": "STAT_017",
        "category": "MARKOV_PATHOLOGICAL",
        "input": {
            "operation": "stationary_distribution",
            "transition_matrix": [
                [1, 0, 0, 0],
                [0.5, 0, 0.5, 0],
                [0, 0.5, 0, 0.5],
                [0, 0, 0, 1]
            ]
        },
        "expected": {
            "is_irreducible": False,
            "absorbing_states": [0, 3],
            "transient_states": [1, 2],
            "multiple_stationary_distributions": True
        },
        "difficulty": "extreme",
        "rationale": "Chain with two absorbing states has infinitely many stationary distributions (any convex combination of delta_0 and delta_3). Unique solution does not exist."
    },

    {
        "test_id": "STAT_018",
        "category": "MARKOV_PATHOLOGICAL",
        "input": {
            "operation": "stationary_distribution",
            "transition_matrix": [
                [1 - 1e-15, 1e-15],
                [1e-15, 1 - 1e-15]
            ]
        },
        "expected": {
            "stationary_distribution": [0.5, 0.5],
            "mixing_time": "~1e15 steps",
            "numerical_precision_required": "quad precision",
            "conditioning_number": "~1e15"
        },
        "difficulty": "pathological",
        "rationale": "Nearly absorbing chain has condition number ~1e15. Standard double-precision arithmetic fails. Mixing time is astronomically large."
    },

    {
        "test_id": "STAT_019",
        "category": "MARKOV_PATHOLOGICAL",
        "input": {
            "operation": "first_passage_time",
            "transition_matrix": [[0.999, 0.001], [0.001, 0.999]],
            "from_state": 0,
            "to_state": 1
        },
        "expected": {
            "mean_first_passage_time": 1000,
            "variance_first_passage_time": "approximately 999000",
            "distribution": "geometric-like with p=0.001"
        },
        "difficulty": "brutal",
        "rationale": "First passage time has mean 1000 but variance ~10^6, requiring careful numerical handling. Naive simulation would need millions of samples for accurate estimation."
    },

    {
        "test_id": "STAT_020",
        "category": "MARKOV_PATHOLOGICAL",
        "input": {
            "operation": "stationary_distribution",
            "transition_matrix": [[1/1000] * 1000 for _ in range(1000)],
            "chain_size": 1000
        },
        "expected": {
            "stationary_distribution": [0.001] * 1000,
            "is_doubly_stochastic": True,
            "eigenvalue_gap": "0 (degenerate)",
            "convergence_rate": "immediate"
        },
        "difficulty": "extreme",
        "rationale": "1000x1000 doubly stochastic uniform matrix has stationary distribution [1/1000, ...] but second eigenvalue is 0, making all distributions fixed points."
    },

    # ========================================================================
    # CATEGORY 5: REGRESSION SINGULARITIES (Tests 021-025)
    # Target: RegressionSpecialist
    # ========================================================================

    {
        "test_id": "STAT_021",
        "category": "REGRESSION_SINGULAR",
        "input": {
            "operation": "multiple_regression",
            "X": [[1, 2, 3], [2, 4, 6], [3, 6, 9], [4, 8, 12]],  # Perfect collinearity
            "y": [1, 2, 3, 4]
        },
        "expected": {
            "matrix_singular": True,
            "unique_solution": False,
            "rank_deficiency": 2,
            "handling": "detect and report or use pseudoinverse"
        },
        "difficulty": "brutal",
        "rationale": "X2 = 2*X1 and X3 = 3*X1, so rank is 1. Normal equations have infinitely many solutions. System must detect rank deficiency."
    },

    {
        "test_id": "STAT_022",
        "category": "REGRESSION_SINGULAR",
        "input": {
            "operation": "multiple_regression",
            "X": [[1, 1 + 1e-14], [2, 2 + 1e-14], [3, 3 + 1e-14]],  # Near collinearity
            "y": [1, 2, 3]
        },
        "expected": {
            "condition_number": "> 1e14",
            "coefficients_unstable": True,
            "small_perturbation_effect": "huge change in coefficients"
        },
        "difficulty": "extreme",
        "rationale": "Near-singular design matrix has condition number ~1e14. Coefficients are meaningless - tiny perturbations cause wild swings. Must detect ill-conditioning."
    },

    {
        "test_id": "STAT_023",
        "category": "REGRESSION_SINGULAR",
        "input": {
            "operation": "ridge_regression",
            "X": [[1, 1000000], [2, 2000000], [3, 3000000]],  # Scale mismatch
            "y": [1, 2, 3],
            "lambda": 1.0
        },
        "expected": {
            "without_standardization": "biased toward X1",
            "with_standardization": "balanced coefficients",
            "scale_sensitivity": "extreme"
        },
        "difficulty": "brutal",
        "rationale": "Lambda penalizes X2 1e12 times more than X1 due to scale. Without standardization, ridge regression is meaningless. Must standardize before regularization."
    },

    {
        "test_id": "STAT_024",
        "category": "REGRESSION_SINGULAR",
        "input": {
            "operation": "polynomial_regression",
            "x": list(range(100)),
            "y": [float(i)**20 for i in range(100)],  # Degree 20 polynomial
            "degree": 20
        },
        "expected": {
            "vandermonde_condition": "> 1e40",
            "numerical_instability": "severe",
            "use_orthogonal_polynomials": True
        },
        "difficulty": "pathological",
        "rationale": "Vandermonde matrix for degree-20 polynomial has astronomical condition number. Standard polynomial basis is numerically unstable; must use Chebyshev or Legendre basis."
    },

    {
        "test_id": "STAT_025",
        "category": "REGRESSION_SINGULAR",
        "input": {
            "operation": "logistic_regression",
            "X": [[i] for i in range(-5, 6)],
            "y": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]  # Perfect separation
        },
        "expected": {
            "maximum_likelihood_exists": False,
            "coefficients_diverge": True,
            "hauck_donner_effect": True,
            "handling": "detect separation, use Firth correction or regularization"
        },
        "difficulty": "extreme",
        "rationale": "Perfect separation means MLE does not exist - coefficients diverge to infinity. Naive gradient descent never converges. Must detect and handle specially."
    },

    # ========================================================================
    # CATEGORY 6: BOOTSTRAP ON INFINITE VARIANCE (Tests 026-030)
    # Target: NonparametricSpecialist (bootstrap methods)
    # ========================================================================

    {
        "test_id": "STAT_026",
        "category": "BOOTSTRAP_INFINITE",
        "input": {
            "operation": "bootstrap_mean",
            "sample": "cauchy_sample_n1000",
            "distribution": "cauchy(0, 1)",
            "n_bootstrap": 10000
        },
        "expected": {
            "population_mean": "undefined",
            "bootstrap_means_diverge": True,
            "confidence_interval": "invalid (infinite width)",
            "error_handling": "should warn about infinite variance"
        },
        "difficulty": "brutal",
        "rationale": "Cauchy distribution has no mean. Bootstrap CI for mean is meaningless - widths grow with sample size. System must detect heavy tails and warn user."
    },

    {
        "test_id": "STAT_027",
        "category": "BOOTSTRAP_INFINITE",
        "input": {
            "operation": "bootstrap_variance",
            "sample": "pareto_sample_alpha_1.5",
            "distribution": "pareto(alpha=1.5)",
            "n_bootstrap": 10000
        },
        "expected": {
            "population_variance": "infinite (alpha < 2)",
            "sample_variance_unstable": True,
            "bootstrap_coverage": "< 0.50 (wildly wrong)"
        },
        "difficulty": "extreme",
        "rationale": "Pareto with alpha=1.5 has finite mean but infinite variance. Bootstrap for variance fails catastrophically - coverage can be near 0%."
    },

    {
        "test_id": "STAT_028",
        "category": "BOOTSTRAP_INFINITE",
        "input": {
            "operation": "bootstrap_max",
            "sample": [1, 2, 3, 4, 100000],  # One extreme outlier
            "n_bootstrap": 10000
        },
        "expected": {
            "bootstrap_max_distribution": "mass at 100000 with prob ~1-(4/5)^n",
            "standard_bootstrap_fails": True,
            "use_subsampling": True
        },
        "difficulty": "brutal",
        "rationale": "Bootstrap of maximum fails when sample contains outliers. Max is almost always 100000 in bootstrap. Subsampling or m-out-of-n bootstrap required."
    },

    {
        "test_id": "STAT_029",
        "category": "BOOTSTRAP_INFINITE",
        "input": {
            "operation": "bootstrap_ratio",
            "numerator_sample": [1, 2, 3, 4, 5],
            "denominator_sample": [0.001, 0.002, 0.003, 0.004, 0.005]
        },
        "expected": {
            "ratio_distribution": "heavy-tailed",
            "bootstrap_CI_unstable": True,
            "occasional_division_by_near_zero": True
        },
        "difficulty": "extreme",
        "rationale": "Ratio of random variables has heavy tails when denominator can be small. Bootstrap resamples may include small denominator values, causing extreme ratios."
    },

    {
        "test_id": "STAT_030",
        "category": "BOOTSTRAP_INFINITE",
        "input": {
            "operation": "bootstrap_correlation",
            "x": [1, 2, 3, 4, 5],
            "y": [1, 2, 3, 4, 5],  # Perfect correlation
            "n_bootstrap": 10000
        },
        "expected": {
            "sample_correlation": 1.0,
            "bootstrap_correlation_distribution": "point mass at 1",
            "fisher_transform_fails": "arctanh(1) = infinity"
        },
        "difficulty": "pathological",
        "rationale": "Perfect correlation r=1 causes Fisher z-transform to blow up (arctanh(1) = inf). Bootstrap CI is degenerate at 1. Must handle boundary case."
    },

    # ========================================================================
    # CATEGORY 7: BAYESIAN WITH IMPROPER PRIORS (Tests 031-035)
    # Target: BayesianInferenceEngine
    # ========================================================================

    {
        "test_id": "STAT_031",
        "category": "BAYESIAN_IMPROPER",
        "input": {
            "operation": "bayesian_inference",
            "prior": "flat_improper",  # p(theta) = 1 for all theta
            "likelihood": "normal(theta, 1)",
            "data": [0]  # Single observation
        },
        "expected": {
            "posterior": "normal(0, 1)",
            "posterior_proper": True,
            "marginal_likelihood": "undefined (integral diverges)"
        },
        "difficulty": "brutal",
        "rationale": "Flat prior is improper (integral = infinity) but posterior can be proper. Marginal likelihood is undefined, making Bayes factors impossible."
    },

    {
        "test_id": "STAT_032",
        "category": "BAYESIAN_IMPROPER",
        "input": {
            "operation": "bayesian_inference",
            "prior": "jeffreys",
            "likelihood": "binomial(n=10, p=theta)",
            "data": [0]  # 0 successes in 10 trials
        },
        "expected": {
            "jeffreys_prior": "beta(0.5, 0.5)",
            "posterior": "beta(0.5, 10.5)",
            "posterior_mean": "0.5/11 = 0.045",
            "haldane_prior_comparison": "beta(0, 0) gives improper posterior with data = 0"
        },
        "difficulty": "extreme",
        "rationale": "Jeffreys prior for binomial is beta(0.5, 0.5), an improper prior. With 0 successes, posterior is proper but Haldane prior beta(0,0) gives improper posterior."
    },

    {
        "test_id": "STAT_033",
        "category": "BAYESIAN_IMPROPER",
        "input": {
            "operation": "bayesian_inference",
            "prior": "reference_prior_2d",
            "parameters": ["mu", "sigma"],
            "likelihood": "normal(mu, sigma)",
            "data": [1, 2, 3]
        },
        "expected": {
            "reference_prior": "p(mu, sigma) = 1/sigma",
            "posterior_for_sigma": "proper",
            "marginal_for_mu": "t-distribution",
            "order_dependence": "reference priors depend on parameter ordering"
        },
        "difficulty": "brutal",
        "rationale": "Reference priors for multiple parameters depend on the order of marginalization. Different orderings give different priors, violating intuition about 'objectivity'."
    },

    {
        "test_id": "STAT_034",
        "category": "BAYESIAN_IMPROPER",
        "input": {
            "operation": "bayesian_model_comparison",
            "model1": {"prior": "flat_improper", "likelihood": "normal(theta, 1)"},
            "model2": {"prior": "normal(0, 10)", "likelihood": "normal(theta, 1)"},
            "data": [0, 0, 0]
        },
        "expected": {
            "bayes_factor": "undefined (improper prior makes marginal likelihood undefined)",
            "lindley_paradox_possible": True,
            "intrinsic_bayes_factor": "alternative approach"
        },
        "difficulty": "extreme",
        "rationale": "Bayes factors with improper priors are undefined since marginal likelihoods are infinite. Intrinsic Bayes factors or training samples needed."
    },

    {
        "test_id": "STAT_035",
        "category": "BAYESIAN_IMPROPER",
        "input": {
            "operation": "hierarchical_bayesian",
            "prior_hyperparameters": "flat_on_variance",
            "group_means": [[1, 2], [3, 4], [5, 6]],
            "n_groups": 3
        },
        "expected": {
            "flat_prior_on_variance": "p(sigma^2) = 1",
            "improper_posterior_possible": True,
            "gelman_recommendation": "use half-cauchy(0, 25) on sd"
        },
        "difficulty": "brutal",
        "rationale": "Flat prior on variance in hierarchical model can lead to improper posterior when number of groups is small. Gelman recommends half-Cauchy on standard deviation."
    },

    # ========================================================================
    # CATEGORY 8: EXTREME VALUE TAIL QUANTILES (Tests 036-040)
    # Target: DistributionSpecialist
    # ========================================================================

    {
        "test_id": "STAT_036",
        "category": "EXTREME_VALUE",
        "input": {
            "operation": "quantile",
            "distribution": "normal(0, 1)",
            "probability": 1 - 1e-15
        },
        "expected": {
            "quantile": "approximately 7.94",
            "computation_method": "asymptotic expansion or special functions",
            "naive_inverse_cdf_fails": True
        },
        "difficulty": "brutal",
        "rationale": "Normal quantile at p=1-1e-15 requires computing Phi^(-1)(1-1e-15) which naive algorithms can't do. Needs asymptotic Mill's ratio expansion."
    },

    {
        "test_id": "STAT_037",
        "category": "EXTREME_VALUE",
        "input": {
            "operation": "tail_probability",
            "distribution": "chi_square(df=1)",
            "threshold": 100
        },
        "expected": {
            "probability": "approximately 1e-23",
            "log_probability": "approximately -52.5",
            "computation": "use log-scale throughout"
        },
        "difficulty": "extreme",
        "rationale": "P(chi^2_1 > 100) is astronomically small. Direct computation underflows to 0. Must use log-probabilities and special tail approximations."
    },

    {
        "test_id": "STAT_038",
        "category": "EXTREME_VALUE",
        "input": {
            "operation": "gev_quantile",
            "distribution": "GEV(mu=0, sigma=1, xi=0.5)",
            "probability": 0.999999
        },
        "expected": {
            "return_level": "approximately 1000-year return level",
            "quantile": "very large (xi > 0 means heavy tail)",
            "frechet_type": True
        },
        "difficulty": "brutal",
        "rationale": "Generalized Extreme Value with xi=0.5 (Frechet type) has heavy tail. High quantiles grow polynomially, not exponentially. Critical for risk assessment."
    },

    {
        "test_id": "STAT_039",
        "category": "EXTREME_VALUE",
        "input": {
            "operation": "multivariate_tail",
            "distribution": "bivariate_normal",
            "correlation": 0.99,
            "threshold": [5, 5]  # Both components > 5
        },
        "expected": {
            "joint_probability": "much larger than product of marginals",
            "asymptotic_dependence": True,
            "copula_approach": "required for accurate computation"
        },
        "difficulty": "extreme",
        "rationale": "Joint tail probability P(X>5, Y>5) for highly correlated normals is NOT simply P(X>5)*P(Y>5). Tail dependence structure matters enormously."
    },

    {
        "test_id": "STAT_040",
        "category": "EXTREME_VALUE",
        "input": {
            "operation": "order_statistic",
            "distribution": "exponential(1)",
            "n": 1000000,
            "order": "maximum"
        },
        "expected": {
            "expected_maximum": "approximately ln(1000000) = 13.8",
            "variance": "pi^2/6 (Gumbel)",
            "distribution": "converges to Gumbel(ln(n), 1)"
        },
        "difficulty": "brutal",
        "rationale": "Maximum of 1M exponentials follows Gumbel asymptotically. Direct simulation requires 1M samples per replicate. Must use EVT theory."
    },

    # ========================================================================
    # CATEGORY 9: NONPARAMETRIC TESTS WITH MASSIVE TIES (Tests 041-045)
    # Target: NonparametricSpecialist
    # ========================================================================

    {
        "test_id": "STAT_041",
        "category": "NONPARAM_TIES",
        "input": {
            "operation": "mann_whitney_u",
            "sample1": [1] * 500 + [2] * 500,
            "sample2": [1] * 500 + [2] * 500
        },
        "expected": {
            "ties_proportion": 1.0,
            "standard_formula_fails": True,
            "tie_correction_required": True,
            "p_value": "1.0 (identical distributions)"
        },
        "difficulty": "brutal",
        "rationale": "All values are tied. Standard Mann-Whitney U formula gives wrong variance. Must use tie-corrected variance formula which involves cubic terms."
    },

    {
        "test_id": "STAT_042",
        "category": "NONPARAM_TIES",
        "input": {
            "operation": "wilcoxon_signed_rank",
            "differences": [0] * 100 + [1] * 50  # 100 zeros
        },
        "expected": {
            "zeros_handling": "should be excluded",
            "effective_n": 50,
            "pratt_method": "alternative handling of zeros"
        },
        "difficulty": "extreme",
        "rationale": "Zero differences create ties at rank 0. Standard Wilcoxon excludes them, but Pratt method includes them. Different methods give different answers."
    },

    {
        "test_id": "STAT_043",
        "category": "NONPARAM_TIES",
        "input": {
            "operation": "kruskal_wallis",
            "groups": [[1] * 100] * 10  # 10 groups, all identical
        },
        "expected": {
            "h_statistic": 0,
            "tie_correction": "division by zero if all tied",
            "degenerate_case": True
        },
        "difficulty": "pathological",
        "rationale": "All observations identical means all tied. H statistic is 0 but tie correction factor can cause division by zero. Edge case handling critical."
    },

    {
        "test_id": "STAT_044",
        "category": "NONPARAM_TIES",
        "input": {
            "operation": "spearman_correlation",
            "x": [1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
            "y": [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
        },
        "expected": {
            "correlation": 1.0,
            "massive_ties": True,
            "average_rank_method": "required",
            "t_test_for_significance": "fails (perfect correlation)"
        },
        "difficulty": "brutal",
        "rationale": "Massive ties in both variables. Spearman = 1 but significance test using t-distribution gives 0/0 for perfect correlation."
    },

    {
        "test_id": "STAT_045",
        "category": "NONPARAM_TIES",
        "input": {
            "operation": "kendall_tau",
            "x": [1] * 1000 + [2] * 1000,
            "y": [1] * 500 + [2] * 500 + [1] * 500 + [2] * 500
        },
        "expected": {
            "concordant_pairs": "complex calculation with ties",
            "tau_a_vs_tau_b": "different tie handling",
            "variance_formula": "requires tie adjustment"
        },
        "difficulty": "extreme",
        "rationale": "Massive ties require tau-b (not tau-a) and adjusted variance formula. Tie groups of size 500+ make standard O(n^2) algorithm very slow."
    },

    # ========================================================================
    # CATEGORY 10: MIXTURE MODELS WITH OVERLAPPING COMPONENTS (Tests 046-050)
    # Target: BayesianInferenceEngine, DistributionSpecialist
    # ========================================================================

    {
        "test_id": "STAT_046",
        "category": "MIXTURE_OVERLAP",
        "input": {
            "operation": "mixture_em",
            "data": "sample_from_mixture",
            "true_mixture": {
                "components": [
                    {"mean": 0, "std": 1, "weight": 0.5},
                    {"mean": 0.1, "std": 1, "weight": 0.5}  # Nearly identical
                ]
            },
            "n_samples": 10000
        },
        "expected": {
            "identifiability": False,
            "label_switching": True,
            "em_convergence": "to degenerate solution",
            "means_distinguishable": False
        },
        "difficulty": "extreme",
        "rationale": "Components with means 0 and 0.1, same variance, are statistically indistinguishable. EM will not recover true parameters. Model is unidentifiable."
    },

    {
        "test_id": "STAT_047",
        "category": "MIXTURE_OVERLAP",
        "input": {
            "operation": "mixture_em",
            "data": "sample_from_mixture",
            "true_mixture": {
                "components": [
                    {"mean": 0, "std": 0.01, "weight": 0.001},
                    {"mean": 0, "std": 100, "weight": 0.999}
                ]
            },
            "n_samples": 10000
        },
        "expected": {
            "tiny_component_detection": "likely missed",
            "variance_ratio": 10000,
            "em_initialization_sensitive": True
        },
        "difficulty": "brutal",
        "rationale": "One component has 0.1% weight and 0.01 std (spike at 0), other has 99.9% weight and std=100. EM will likely miss the small component entirely."
    },

    {
        "test_id": "STAT_048",
        "category": "MIXTURE_OVERLAP",
        "input": {
            "operation": "gmm_bic_selection",
            "data": "sample_from_mixture",
            "true_k": 5,
            "test_k_range": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "n_samples": 500
        },
        "expected": {
            "bic_selected_k": "likely 2-4 (underestimates)",
            "aic_selected_k": "likely 6-8 (overestimates)",
            "sample_size_too_small": True
        },
        "difficulty": "brutal",
        "rationale": "With only 500 samples and 5 components, BIC underestimates k while AIC overestimates. Neither is reliable. Need much larger samples."
    },

    {
        "test_id": "STAT_049",
        "category": "MIXTURE_OVERLAP",
        "input": {
            "operation": "mixture_identifiability",
            "mixture1": {"means": [0, 2], "stds": [1, 1], "weights": [0.5, 0.5]},
            "mixture2": {"means": [0.5, 1.5], "stds": [1.1, 0.9], "weights": [0.5, 0.5]}
        },
        "expected": {
            "pdfs_nearly_identical": True,
            "max_pdf_difference": "< 0.01",
            "kl_divergence": "very small",
            "statistically_distinguishable": "requires n > 100000"
        },
        "difficulty": "extreme",
        "rationale": "Two different mixtures can have nearly identical PDFs. Distinguishing them requires enormous sample sizes. Mixture parameters are not identifiable from PDF."
    },

    {
        "test_id": "STAT_050",
        "category": "MIXTURE_OVERLAP",
        "input": {
            "operation": "mixture_mcmc",
            "data": "sample_from_symmetric_mixture",
            "true_mixture": {
                "components": [
                    {"mean": -1, "std": 1, "weight": 0.5},
                    {"mean": 1, "std": 1, "weight": 0.5}
                ]
            },
            "n_samples": 1000,
            "mcmc_samples": 100000
        },
        "expected": {
            "label_switching_problem": True,
            "posterior_bimodal": True,
            "relabeling_algorithm_required": True,
            "identifiability_constraints": ["order_means", "pivot_points"]
        },
        "difficulty": "pathological",
        "rationale": "Symmetric mixture causes label switching in MCMC - chains jump between (mu1=-1, mu2=1) and (mu1=1, mu2=-1). Posterior is bimodal. Requires post-processing."
    }
]


# ============================================================================
# UTILITY FUNCTIONS FOR TEST EXECUTION
# ============================================================================

def get_tests_by_category(category: str) -> List[Dict[str, Any]]:
    """Return all tests matching a specific category."""
    return [t for t in BRUTAL_STATISTICS_TESTS if t["category"] == category]


def get_tests_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """Return all tests matching a specific difficulty level."""
    return [t for t in BRUTAL_STATISTICS_TESTS if t["difficulty"] == difficulty]


def get_test_by_id(test_id: str) -> Optional[Dict[str, Any]]:
    """Return a specific test by ID."""
    for test in BRUTAL_STATISTICS_TESTS:
        if test["test_id"] == test_id:
            return test
    return None


def summarize_tests() -> Dict[str, Any]:
    """Summarize the test suite."""
    categories = {}
    difficulties = {}

    for test in BRUTAL_STATISTICS_TESTS:
        cat = test["category"]
        diff = test["difficulty"]
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

    return {
        "total_tests": len(BRUTAL_STATISTICS_TESTS),
        "by_category": categories,
        "by_difficulty": difficulties
    }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import json

    print("=" * 80)
    print("BRUTAL STATISTICS STRESS TESTS")
    print("=" * 80)
    print()

    summary = summarize_tests()
    print(f"Total Tests: {summary['total_tests']}")
    print()

    print("Tests by Category:")
    for cat, count in sorted(summary['by_category'].items()):
        print(f"  {cat}: {count}")
    print()

    print("Tests by Difficulty:")
    for diff, count in sorted(summary['by_difficulty'].items()):
        print(f"  {diff}: {count}")
    print()

    print("Sample Test (STAT_001):")
    print(json.dumps(BRUTAL_STATISTICS_TESTS[0], indent=2))
