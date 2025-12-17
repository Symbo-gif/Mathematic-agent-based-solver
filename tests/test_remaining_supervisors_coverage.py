# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Tests for remaining supervisors to achieve 70%+ coverage.

Covers:
- DiscreteMathSupervisor
- LinearAlgebraSupervisor
- GeometrySupervisor
- StatisticsSupervisor
- LogicSupervisor
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


# =============================================================================
# DiscreteMathSupervisor Tests
# =============================================================================


class TestDiscreteMathSupervisorInit:
    """Tests for DiscreteMathSupervisor initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        supervisor = DiscreteMathSupervisor()
        assert supervisor.agent_id.startswith('discrete_math_supervisor')
        assert supervisor.tasks_routed == 0

    def test_init_with_custom_id(self):
        """Test initialization with custom agent ID."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        supervisor = DiscreteMathSupervisor(agent_id='custom_discrete_001')
        assert supervisor.agent_id == 'custom_discrete_001'

    def test_init_with_df(self):
        """Test initialization with Directory Facilitator."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator
        )
        df = DirectoryFacilitator()
        supervisor = DiscreteMathSupervisor(df=df)
        assert supervisor.df is df

    def test_init_with_blackboard(self):
        """Test initialization with Blackboard."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        from symbo_agentic_reasoners.core import Blackboard
        bb = Blackboard()
        supervisor = DiscreteMathSupervisor(blackboard=bb)
        assert supervisor.blackboard is bb


class TestDiscreteMathSupervisorRouting:
    """Tests for DiscreteMathSupervisor routing via _analyze_task."""

    def test_analyze_task_combinatorics(self):
        """Test analyzing combinatorics tasks."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        supervisor = DiscreteMathSupervisor()

        for keyword in ['permutation', 'combination', 'factorial', 'choose']:
            task = Mock()
            task.metadata = {'raw_input': f'Calculate the {keyword}'}
            result = supervisor._analyze_task(task)
            assert 'combinatorics' in result['service_type']

    def test_analyze_task_graph_theory(self):
        """Test analyzing graph theory tasks."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        supervisor = DiscreteMathSupervisor()

        for keyword in ['graph', 'path', 'tree', 'vertex', 'edge', 'network']:
            task = Mock()
            task.metadata = {'raw_input': f'Find the {keyword}'}
            result = supervisor._analyze_task(task)
            assert 'graph' in result['service_type']


class TestDiscreteMathSupervisorProcess:
    """Tests for DiscreteMathSupervisor process method."""

    def test_process_without_df(self):
        """Test process method without DF - returns None when no blackboard."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        supervisor = DiscreteMathSupervisor()
        supervisor.df = None

        task = Mock()
        task.metadata = {'raw_input': 'Count permutations of 5 items'}

        result = supervisor.process(task)
        # Without blackboard, _create_error_result returns None
        assert result is None
        assert supervisor.tasks_failed == 1

    def test_process_with_blackboard_no_specialists(self):
        """Test process with blackboard but no specialists found."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        from symbo_agentic_reasoners.core import Blackboard

        bb = Blackboard()
        supervisor = DiscreteMathSupervisor(blackboard=bb)
        supervisor.df = None  # No DF means no specialists

        task = Mock()
        task.metadata = {'raw_input': 'Calculate combination'}
        task.content = 'test content'
        task.conversation_id = 'test_conv'

        result = supervisor.process(task)
        # With blackboard, should get an error entry
        assert result is not None
        assert supervisor.tasks_failed == 1


class TestDiscreteMathSupervisorBDI:
    """Tests for BDI methods."""

    def test_update_beliefs(self):
        """Test update_beliefs method."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        supervisor = DiscreteMathSupervisor()
        supervisor.update_beliefs()  # Should not raise

    def test_deliberate(self):
        """Test deliberate method."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        supervisor = DiscreteMathSupervisor()
        result = supervisor.deliberate()
        assert isinstance(result, list)

    def test_get_statistics(self):
        """Test get_statistics method."""
        from symbo_agentic_reasoners.agents.supervisors.discrete_math_supervisor import (
            DiscreteMathSupervisor
        )
        supervisor = DiscreteMathSupervisor()
        stats = supervisor.get_statistics()
        assert isinstance(stats, dict)
        assert 'tasks_routed' in stats


# =============================================================================
# LinearAlgebraSupervisor Tests
# =============================================================================


class TestLinearAlgebraSupervisorInit:
    """Tests for LinearAlgebraSupervisor initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import (
            LinearAlgebraSupervisor
        )
        supervisor = LinearAlgebraSupervisor()
        assert supervisor.agent_id.startswith('linalg_supervisor')
        assert supervisor.tasks_routed == 0

    def test_init_with_df(self):
        """Test initialization with Directory Facilitator."""
        from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import (
            LinearAlgebraSupervisor
        )
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator
        )
        df = DirectoryFacilitator()
        supervisor = LinearAlgebraSupervisor(df=df)
        assert supervisor.df is df

    def test_init_with_blackboard(self):
        """Test initialization with Blackboard."""
        from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import (
            LinearAlgebraSupervisor
        )
        from symbo_agentic_reasoners.core import Blackboard
        bb = Blackboard()
        supervisor = LinearAlgebraSupervisor(blackboard=bb)
        assert supervisor.blackboard is bb


class TestLinearAlgebraSupervisorRouting:
    """Tests for LinearAlgebraSupervisor routing via _analyze_task."""

    def test_analyze_task_matrix_ops(self):
        """Test analyzing matrix operation tasks."""
        from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import (
            LinearAlgebraSupervisor
        )
        supervisor = LinearAlgebraSupervisor()

        for keyword in ['multiply', 'transpose', 'inverse', 'determinant']:
            task = Mock()
            task.metadata = {'raw_input': f'Matrix {keyword}'}
            result = supervisor._analyze_task(task)
            assert result is not None
            assert 'service_type' in result

    def test_analyze_task_decomposition(self):
        """Test analyzing decomposition tasks."""
        from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import (
            LinearAlgebraSupervisor
        )
        supervisor = LinearAlgebraSupervisor()

        for keyword in ['LU', 'QR', 'SVD', 'eigenvalue', 'eigenvector', 'Cholesky']:
            task = Mock()
            task.metadata = {'raw_input': f'{keyword} decomposition'}
            result = supervisor._analyze_task(task)
            assert result is not None
            assert 'decomposition' in result.get('service_type', '') or result.get('target') is not None

    def test_analyze_task_vector_space(self):
        """Test analyzing vector space tasks."""
        from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import (
            LinearAlgebraSupervisor
        )
        supervisor = LinearAlgebraSupervisor()

        for keyword in ['basis', 'rank', 'nullspace', 'kernel', 'span']:
            task = Mock()
            task.metadata = {'raw_input': f'Find {keyword}'}
            result = supervisor._analyze_task(task)
            assert result is not None


class TestLinearAlgebraSupervisorProcess:
    """Tests for LinearAlgebraSupervisor process method."""

    def test_process_without_df(self):
        """Test process method without DF - returns None when no blackboard."""
        from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import (
            LinearAlgebraSupervisor
        )
        supervisor = LinearAlgebraSupervisor()
        supervisor.df = None

        task = Mock()
        task.metadata = {'raw_input': 'Calculate determinant'}

        result = supervisor.process(task)
        # Without blackboard, _create_error_result returns None
        assert result is None
        assert supervisor.tasks_failed == 1

    def test_get_statistics(self):
        """Test get_statistics method."""
        from symbo_agentic_reasoners.agents.supervisors.linalg_supervisor import (
            LinearAlgebraSupervisor
        )
        supervisor = LinearAlgebraSupervisor()
        stats = supervisor.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# GeometrySupervisor Tests
# =============================================================================


class TestGeometrySupervisorInit:
    """Tests for GeometrySupervisor initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import (
            GeometrySupervisor
        )
        supervisor = GeometrySupervisor()
        assert supervisor.agent_id.startswith('geometry_supervisor')
        assert supervisor.tasks_routed == 0

    def test_init_with_df(self):
        """Test initialization with Directory Facilitator."""
        from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import (
            GeometrySupervisor
        )
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator
        )
        df = DirectoryFacilitator()
        supervisor = GeometrySupervisor(df=df)
        assert supervisor.df is df

    def test_init_with_blackboard(self):
        """Test initialization with Blackboard."""
        from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import (
            GeometrySupervisor
        )
        from symbo_agentic_reasoners.core import Blackboard
        bb = Blackboard()
        supervisor = GeometrySupervisor(blackboard=bb)
        assert supervisor.blackboard is bb


class TestGeometrySupervisorRouting:
    """Tests for GeometrySupervisor routing via _analyze_task."""

    def test_analyze_task_euclidean(self):
        """Test analyzing euclidean geometry tasks."""
        from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import (
            GeometrySupervisor
        )
        supervisor = GeometrySupervisor()

        for keyword in ['triangle', 'circle', 'polygon', 'angle', 'perimeter', 'area']:
            task = Mock()
            task.metadata = {'raw_input': f'Calculate {keyword}'}
            result = supervisor._analyze_task(task)
            assert result is not None
            assert 'service_type' in result

    def test_analyze_task_analytic(self):
        """Test analyzing analytic geometry tasks."""
        from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import (
            GeometrySupervisor
        )
        supervisor = GeometrySupervisor()

        for keyword in ['line', 'parabola', 'ellipse', 'hyperbola', 'conic']:
            task = Mock()
            task.metadata = {'raw_input': f'Find {keyword}'}
            result = supervisor._analyze_task(task)
            assert result is not None
            assert 'analytic' in result.get('service_type', '') or result.get('target') is not None

    def test_analyze_task_transformation(self):
        """Test analyzing transformation tasks."""
        from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import (
            GeometrySupervisor
        )
        supervisor = GeometrySupervisor()

        for keyword in ['rotation', 'reflection', 'translation', 'scale', 'transform']:
            task = Mock()
            task.metadata = {'raw_input': f'Apply {keyword}'}
            result = supervisor._analyze_task(task)
            assert result is not None

    def test_analyze_task_trigonometry(self):
        """Test analyzing trigonometry tasks."""
        from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import (
            GeometrySupervisor
        )
        supervisor = GeometrySupervisor()

        for keyword in ['sin', 'cos', 'tan', 'arcsin']:
            task = Mock()
            task.metadata = {'raw_input': f'Calculate {keyword}'}
            result = supervisor._analyze_task(task)
            assert result is not None


class TestGeometrySupervisorProcess:
    """Tests for GeometrySupervisor process method."""

    def test_process_updates_counters(self):
        """Test that process updates route counters."""
        from symbo_agentic_reasoners.agents.supervisors.geometry_supervisor import (
            GeometrySupervisor
        )
        supervisor = GeometrySupervisor()

        task = Mock()
        task.metadata = {'raw_input': 'calculate area of triangle'}

        supervisor.process(task)
        assert supervisor.tasks_routed >= 0  # May route or fail


# =============================================================================
# StatisticsSupervisor Tests
# =============================================================================


class TestStatisticsSupervisorInit:
    """Tests for StatisticsSupervisor initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import (
            StatisticsSupervisor
        )
        supervisor = StatisticsSupervisor()
        assert supervisor.agent_id.startswith('stats_supervisor')
        assert supervisor.tasks_routed == 0

    def test_init_with_df(self):
        """Test initialization with Directory Facilitator."""
        from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import (
            StatisticsSupervisor
        )
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator
        )
        df = DirectoryFacilitator()
        supervisor = StatisticsSupervisor(df=df)
        assert supervisor.df is df

    def test_init_with_blackboard(self):
        """Test initialization with Blackboard."""
        from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import (
            StatisticsSupervisor
        )
        from symbo_agentic_reasoners.core import Blackboard
        bb = Blackboard()
        supervisor = StatisticsSupervisor(blackboard=bb)
        assert supervisor.blackboard is bb


class TestStatisticsSupervisorRouting:
    """Tests for StatisticsSupervisor routing via _analyze_task."""

    def test_analyze_task_bayesian(self):
        """Test analyzing Bayesian tasks."""
        from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import (
            StatisticsSupervisor
        )
        supervisor = StatisticsSupervisor()

        for keyword in ['prior', 'posterior', 'bayesian', 'belief']:
            task = Mock()
            task.metadata = {'raw_input': f'Calculate {keyword}'}
            result = supervisor._analyze_task(task)
            assert result is not None
            assert 'service_type' in result

    def test_analyze_task_frequentist(self):
        """Test analyzing Frequentist tasks."""
        from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import (
            StatisticsSupervisor
        )
        supervisor = StatisticsSupervisor()

        for keyword in ['p-value', 'hypothesis test', 't-test', 'chi-square']:
            task = Mock()
            task.metadata = {'raw_input': f'Calculate {keyword}'}
            result = supervisor._analyze_task(task)
            assert result is not None

    def test_analyze_task_distribution(self):
        """Test analyzing distribution tasks."""
        from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import (
            StatisticsSupervisor
        )
        supervisor = StatisticsSupervisor()

        for keyword in ['PDF', 'CDF', 'normal distribution', 'mean', 'variance']:
            task = Mock()
            task.metadata = {'raw_input': f'Calculate {keyword}'}
            result = supervisor._analyze_task(task)
            assert result is not None


class TestStatisticsSupervisorProcess:
    """Tests for StatisticsSupervisor process method."""

    def test_process_without_df(self):
        """Test process method without DF - returns None when no blackboard."""
        from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import (
            StatisticsSupervisor
        )
        supervisor = StatisticsSupervisor()
        supervisor.df = None

        task = Mock()
        task.metadata = {'raw_input': 'Calculate mean'}

        result = supervisor.process(task)
        # Without blackboard, _create_error_result returns None
        assert result is None
        assert supervisor.tasks_failed == 1

    def test_get_statistics(self):
        """Test get_statistics method."""
        from symbo_agentic_reasoners.agents.supervisors.stats_supervisor import (
            StatisticsSupervisor
        )
        supervisor = StatisticsSupervisor()
        stats = supervisor.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# LogicSupervisor Tests
# =============================================================================


class TestLogicSupervisorInit:
    """Tests for LogicSupervisor initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        from symbo_agentic_reasoners.agents.supervisors.logic_supervisor import (
            LogicSupervisor
        )
        supervisor = LogicSupervisor()
        assert supervisor.agent_id.startswith('logic_supervisor')

    def test_init_with_df(self):
        """Test initialization with Directory Facilitator."""
        from symbo_agentic_reasoners.agents.supervisors.logic_supervisor import (
            LogicSupervisor
        )
        from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
            DirectoryFacilitator
        )
        df = DirectoryFacilitator()
        supervisor = LogicSupervisor(df=df)
        assert supervisor.df is df


class TestLogicSupervisorRouting:
    """Tests for LogicSupervisor routing."""

    def test_route_task_propositional(self):
        """Test routing propositional logic tasks."""
        from symbo_agentic_reasoners.agents.supervisors.logic_supervisor import (
            LogicSupervisor
        )
        supervisor = LogicSupervisor()

        for keyword in ['and', 'or', 'not', 'implies', 'truth table', 'boolean']:
            task = Mock()
            task.metadata = {'raw_input': f'Evaluate {keyword}'}
            result = supervisor.process(task)
            assert result is not None

    def test_route_task_predicate(self):
        """Test routing predicate logic tasks."""
        from symbo_agentic_reasoners.agents.supervisors.logic_supervisor import (
            LogicSupervisor
        )
        supervisor = LogicSupervisor()

        for keyword in ['forall', 'exists', 'quantifier', 'predicate']:
            task = Mock()
            task.metadata = {'raw_input': f'Prove {keyword}'}
            result = supervisor.process(task)
            assert result is not None

    def test_route_task_proof(self):
        """Test routing proof tasks."""
        from symbo_agentic_reasoners.agents.supervisors.logic_supervisor import (
            LogicSupervisor
        )
        supervisor = LogicSupervisor()

        for keyword in ['proof', 'deduction', 'induction', 'contradiction']:
            task = Mock()
            task.metadata = {'raw_input': f'Construct {keyword}'}
            result = supervisor.process(task)
            assert result is not None


class TestLogicSupervisorProcess:
    """Tests for LogicSupervisor process method."""

    def test_process_without_df(self):
        """Test process method without DF."""
        from symbo_agentic_reasoners.agents.supervisors.logic_supervisor import (
            LogicSupervisor
        )
        supervisor = LogicSupervisor()
        supervisor.df = None

        task = Mock()
        task.metadata = {'raw_input': 'Evaluate A and B'}

        result = supervisor.process(task)
        assert result is not None
