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
Statistics Specialist Tests
===========================

Comprehensive tests for statistics specialist agents:
- StochasticProcessAnalyzer
- FrequentistAgent
- BayesianInferenceEngine
- DistributionSpecialist
"""

import pytest


# =============================================================================
# StochasticProcessAnalyzer Tests
# =============================================================================


class TestStochasticProcessAnalyzer:
    """Tests for StochasticProcessAnalyzer."""

    @pytest.fixture
    def specialist(self):
        """Create StochasticProcessAnalyzer instance."""
        from symbo_agentic_reasoners.agents.specialists.statistics.stochastic_process import (
            StochasticProcessAnalyzer
        )
        return StochasticProcessAnalyzer()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_process_method(self, specialist):
        """Should have process method."""
        assert hasattr(specialist, 'process')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


class TestStochasticEnums:
    """Tests for stochastic process enums and data classes."""

    def test_process_type_enum(self):
        """ProcessType enum should exist."""
        from symbo_agentic_reasoners.agents.specialists.statistics.stochastic_process import (
            ProcessType
        )
        assert ProcessType is not None
        assert len(list(ProcessType)) > 0

    def test_markov_chain_properties_exists(self):
        """MarkovChainProperties class should exist."""
        from symbo_agentic_reasoners.agents.specialists.statistics.stochastic_process import (
            MarkovChainProperties
        )
        assert MarkovChainProperties is not None


# =============================================================================
# FrequentistAgent Tests
# =============================================================================


class TestFrequentistAgent:
    """Tests for FrequentistAgent."""

    @pytest.fixture
    def specialist(self):
        """Create FrequentistAgent instance."""
        from symbo_agentic_reasoners.agents.specialists.statistics.frequentist_agent import (
            FrequentistAgent
        )
        return FrequentistAgent()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# BayesianInferenceEngine Tests
# =============================================================================


class TestBayesianInferenceEngine:
    """Tests for BayesianInferenceEngine."""

    @pytest.fixture
    def specialist(self):
        """Create BayesianInferenceEngine instance."""
        from symbo_agentic_reasoners.agents.specialists.statistics.bayesian_engine import (
            BayesianInferenceEngine
        )
        return BayesianInferenceEngine()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# DistributionSpecialist Tests
# =============================================================================


class TestDistributionSpecialist:
    """Tests for DistributionSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create DistributionSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.statistics.distribution_specialist import (
            DistributionSpecialist
        )
        return DistributionSpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
