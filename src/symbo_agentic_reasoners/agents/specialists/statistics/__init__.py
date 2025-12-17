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

"""Statistics Specialists"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'DistributionSpecialist':
        from .distribution_specialist import DistributionSpecialist
        return DistributionSpecialist
    elif name == 'BayesianInferenceEngine':
        from .bayesian_engine import BayesianInferenceEngine
        return BayesianInferenceEngine
    elif name == 'NonparametricSpecialist':
        from .nonparametric_specialist import NonparametricSpecialist
        return NonparametricSpecialist
    elif name == 'TestResult':
        from .nonparametric_specialist import TestResult
        return TestResult
    elif name == 'RegressionSpecialist':
        from .regression_specialist import RegressionSpecialist
        return RegressionSpecialist
    elif name == 'RegressionResult':
        from .regression_specialist import RegressionResult
        return RegressionResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Class exports (lazy loaded)
    "DistributionSpecialist",
    "BayesianInferenceEngine",
    "NonparametricSpecialist",
    "RegressionSpecialist",
    # Supporting types
    "TestResult",
    "RegressionResult",
    # Module aliases
    "distribution_specialist",
    "bayesian_engine",
    "frequentist_agent",
    "nonparametric_specialist",
    "regression_specialist",
]