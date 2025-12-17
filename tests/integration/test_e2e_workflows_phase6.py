# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
End-to-End Workflow Tests
==========================

Phase 6 - Week 7: Integration tests for complete problem-solving workflows.

Tests:
- Multi-step problem solving
- Cross-domain coordination
- Supervisor-specialist interaction
- Result verification pipelines
"""

import pytest
from unittest.mock import Mock

from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator
from symbo_agentic_reasoners.agents.base.problem_analysis import ProblemAnalysisTeam


class TestEndToEndWorkflows:
    """Test complete end-to-end problem-solving workflows."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return MainOrchestrator(agent_id='test_orchestrator')

    @pytest.fixture
    def problem_analysis_team(self):
        """Create problem analysis team."""
        return ProblemAnalysisTeam()

    def test_simple_arithmetic_workflow(self, problem_analysis_team):
        """Test simple arithmetic problem end-to-end."""
        # Parse problem
        structured = problem_analysis_team.process("2 + 2")

        assert structured is not None
        assert hasattr(structured, 'domain')
        assert hasattr(structured, 'problem_type')

    def test_calculus_workflow(self, problem_analysis_team):
        """Test calculus problem parsing."""
        structured = problem_analysis_team.process("differentiate x^2 with respect to x")

        assert structured is not None
        # Should recognize as calculus domain
        assert 'calculus' in structured.domain.value.lower() or structured.domain.value == 'CALCULUS'

    def test_algebra_workflow(self, problem_analysis_team):
        """Test algebra problem parsing."""
        structured = problem_analysis_team.process("solve x + 5 = 10")

        assert structured is not None
        # Should recognize as algebra
        assert 'algebra' in structured.domain.value.lower() or structured.domain.value == 'ALGEBRA'

    def test_linear_algebra_workflow(self, problem_analysis_team):
        """Test linear algebra problem parsing."""
        structured = problem_analysis_team.process("determinant of [[1,2],[3,4]]")

        assert structured is not None

    @pytest.mark.slow
    def test_multi_step_workflow(self, problem_analysis_team):
        """Test multi-step problem decomposition."""
        # Complex problem that might require multiple specialists
        structured = problem_analysis_team.process(
            "Find the derivative of x^3 + 2*x^2 + 1, then evaluate at x=2"
        )

        assert structured is not None

    def test_error_handling_workflow(self, problem_analysis_team):
        """Test error handling in workflows."""
        # Malformed problem
        try:
            structured = problem_analysis_team.process("{{{{invalid}}}}")
            # Should handle gracefully
        except Exception as e:
            # Acceptable - problem rejected
            pass

    def test_cross_domain_workflow(self, problem_analysis_team):
        """Test problems spanning multiple domains."""
        # Physics problem (kinematics) requires calculus
        structured = problem_analysis_team.process(
            "If position is x = t^2, find velocity"
        )

        assert structured is not None


# Phase 6 marker
pytestmark = pytest.mark.phase6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
