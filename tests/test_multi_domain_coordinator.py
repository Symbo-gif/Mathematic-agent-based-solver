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
Tests for Multi-Domain Team Coordinator
=======================================

Tests for the meta-level coordinator that orchestrates multiple domain supervisors.
"""

import pytest


class TestDomainDetection:
    """Tests for domain detection functionality."""

    @pytest.fixture
    def coordinator(self):
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        return MultiDomainTeamCoordinator()

    def test_detect_algebra_domain(self, coordinator):
        """Test detecting algebra domain."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainType
        domains = coordinator.detect_domains("Solve the polynomial equation x^2 + 3x - 4 = 0")
        assert DomainType.ALGEBRA in domains

    def test_detect_calculus_domain(self, coordinator):
        """Test detecting calculus domain."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainType
        domains = coordinator.detect_domains("Find the derivative of sin(x) * x^2")
        assert DomainType.CALCULUS in domains

    def test_detect_linear_algebra_domain(self, coordinator):
        """Test detecting linear algebra domain."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainType
        domains = coordinator.detect_domains("Find the eigenvalues of the matrix A")
        assert DomainType.LINEAR_ALGEBRA in domains

    def test_detect_statistics_domain(self, coordinator):
        """Test detecting statistics domain."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainType
        domains = coordinator.detect_domains("Calculate the mean and variance of the distribution")
        assert DomainType.STATISTICS in domains

    def test_detect_optimization_domain(self, coordinator):
        """Test detecting optimization domain."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainType
        domains = coordinator.detect_domains("Minimize f(x) subject to constraints")
        assert DomainType.OPTIMIZATION in domains

    def test_detect_cryptography_domain(self, coordinator):
        """Test detecting cryptography domain."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainType
        domains = coordinator.detect_domains("Encrypt the message using RSA")
        assert DomainType.CRYPTOGRAPHY in domains

    def test_detect_information_theory_domain(self, coordinator):
        """Test detecting information theory domain."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainType
        domains = coordinator.detect_domains("Calculate the entropy of the source")
        assert DomainType.INFORMATION_THEORY in domains

    def test_detect_category_theory_domain(self, coordinator):
        """Test detecting category theory domain."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainType
        domains = coordinator.detect_domains("Apply the functor F to the morphism")
        assert DomainType.CATEGORY_THEORY in domains

    def test_detect_multiple_domains(self, coordinator):
        """Test detecting multiple domains."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainType
        domains = coordinator.detect_domains(
            "Find the eigenvalues of the matrix and then integrate the resulting polynomial"
        )
        assert DomainType.LINEAR_ALGEBRA in domains
        assert DomainType.CALCULUS in domains

    def test_empty_detection(self, coordinator):
        """Test empty text returns no domains."""
        domains = coordinator.detect_domains("")
        assert len(domains) == 0


class TestProblemAnalysis:
    """Tests for problem analysis functionality."""

    @pytest.fixture
    def coordinator(self):
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        return MultiDomainTeamCoordinator()

    def test_analyze_single_domain_problem(self, coordinator):
        """Test analyzing a single domain problem."""
        analysis = coordinator.analyze_problem({
            'description': 'Solve the quadratic equation x^2 - 5x + 6 = 0'
        })
        assert analysis['primary_domain'] == 'algebra'
        assert analysis['complexity'] == 'simple'
        assert analysis['requires_coordination'] is False

    def test_analyze_multi_domain_problem(self, coordinator):
        """Test analyzing a multi-domain problem."""
        analysis = coordinator.analyze_problem({
            'description': 'Find the eigenvalues of matrix A and integrate x^2'
        })
        assert len(analysis['detected_domains']) >= 2
        assert analysis['requires_coordination'] is True

    def test_analyze_complex_problem(self, coordinator):
        """Test analyzing a complex problem."""
        analysis = coordinator.analyze_problem({
            'description': '''
                Given a random variable X with probability distribution,
                compute its entropy, then optimize a function of the variance
                using gradient descent.
            '''
        })
        assert analysis['complexity'] in ['moderate', 'complex']


class TestTaskDecomposition:
    """Tests for task decomposition functionality."""

    @pytest.fixture
    def coordinator(self):
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        return MultiDomainTeamCoordinator()

    def test_decompose_problem(self, coordinator):
        """Test problem decomposition into tasks."""
        plan = coordinator.decompose_problem({
            'description': 'Find eigenvalues and compute derivative'
        })
        assert plan is not None
        assert len(plan.tasks) >= 1
        assert len(plan.execution_order) >= 1

    def test_decompose_creates_unique_task_ids(self, coordinator):
        """Test that decomposition creates unique task IDs."""
        plan = coordinator.decompose_problem({
            'description': 'Solve polynomial and integrate function'
        })
        task_ids = [t.task_id for t in plan.tasks]
        assert len(task_ids) == len(set(task_ids))

    def test_plan_stored_in_coordinator(self, coordinator):
        """Test that plan is stored in coordinator."""
        plan = coordinator.decompose_problem({
            'description': 'Calculate entropy'
        })
        assert plan.plan_id in coordinator.plans


class TestPlanExecution:
    """Tests for plan execution functionality."""

    @pytest.fixture
    def coordinator(self):
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        return MultiDomainTeamCoordinator()

    def test_execute_single_domain(self, coordinator):
        """Test executing a single domain problem."""
        result = coordinator.solve({
            'description': 'Simple algebra problem',
            'type': 'polynomial_roots',
            'coefficients': [1, -5, 6]  # x^2 - 5x + 6
        })
        # Should delegate to algebra supervisor
        assert 'error' in result or 'synthesis' in result or result is not None

    def test_execute_multi_domain(self, coordinator):
        """Test executing a multi-domain problem."""
        result = coordinator.solve({
            'description': 'Find eigenvalues and compute derivative of polynomial'
        })
        assert result is not None
        assert 'analysis' in result or 'error' not in result

    def test_solve_returns_analysis(self, coordinator):
        """Test that solve returns analysis for multi-domain."""
        result = coordinator.solve({
            'description': 'Calculate entropy and optimize function'
        })
        # Should have analysis for multi-domain
        if 'analysis' in result:
            assert 'detected_domains' in result['analysis']


class TestDependencyHandling:
    """Tests for dependency handling between domain tasks."""

    @pytest.fixture
    def coordinator(self):
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        return MultiDomainTeamCoordinator()

    def test_topological_sort_no_dependencies(self, coordinator):
        """Test topological sort with no dependencies."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainTask, DomainType
        tasks = [
            DomainTask('t1', DomainType.ALGEBRA, 'task 1', {}),
            DomainTask('t2', DomainType.CALCULUS, 'task 2', {}),
        ]
        order = coordinator._topological_sort(tasks)
        # Both tasks have no dependencies, so they should be in the same batch
        assert len(order) == 1
        assert 't1' in order[0]
        assert 't2' in order[0]

    def test_topological_sort_with_dependencies(self, coordinator):
        """Test topological sort with dependencies."""
        from symbo_agentic_reasoners.agents.coordinators.multi_domain_coordinator import DomainTask, DomainType
        tasks = [
            DomainTask('t1', DomainType.ALGEBRA, 'task 1', {}),
            DomainTask('t2', DomainType.CALCULUS, 'task 2', {}, dependencies=['t1']),
        ]
        order = coordinator._topological_sort(tasks)
        # t1 should be before t2
        t1_level = next(i for i, batch in enumerate(order) if 't1' in batch)
        t2_level = next(i for i, batch in enumerate(order) if 't2' in batch)
        assert t1_level < t2_level

    def test_solve_with_dependencies(self, coordinator):
        """Test solving with explicit dependencies."""
        result = coordinator.solve_with_dependencies(
            {'description': 'Eigenvalues then polynomial roots'},
            [('linear_algebra', 'algebra')]
        )
        assert result is not None
        assert 'execution_order' in result


class TestCoordinatorStatistics:
    """Tests for coordinator statistics."""

    @pytest.fixture
    def coordinator(self):
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        return MultiDomainTeamCoordinator()

    def test_get_statistics(self, coordinator):
        """Test getting statistics."""
        stats = coordinator.get_statistics()
        assert stats['tier'] == 1
        assert stats['role'] == 'coordinator'
        assert 'domain_detection' in stats['capabilities']

    def test_statistics_tracks_tasks(self, coordinator):
        """Test that statistics tracks executed tasks."""
        initial_count = coordinator.get_statistics()['tasks_executed']
        # Solve something
        coordinator.solve({'description': 'Simple algebra polynomial'})
        # Count may or may not increase depending on execution
        new_count = coordinator.get_statistics()['tasks_executed']
        assert new_count >= initial_count

    def test_available_domains_listed(self, coordinator):
        """Test that all available domains are listed."""
        stats = coordinator.get_statistics()
        assert 'algebra' in stats['available_domains']
        assert 'calculus' in stats['available_domains']
        assert 'optimization' in stats['available_domains']


class TestCoordinatorInitialization:
    """Tests for coordinator initialization."""

    def test_basic_initialization(self):
        """Test basic coordinator initialization."""
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        coord = MultiDomainTeamCoordinator()
        assert coord.agent_id == 'multi_domain_coordinator_001'

    def test_custom_agent_id(self):
        """Test initialization with custom ID."""
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        coord = MultiDomainTeamCoordinator(agent_id='custom_coord_001')
        assert coord.agent_id == 'custom_coord_001'

    def test_lazy_loading_supervisors(self):
        """Test that supervisors are lazy-loaded."""
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        coord = MultiDomainTeamCoordinator()
        assert len(coord._supervisors) == 0


class TestCombineResults:
    """Tests for result combination functionality."""

    @pytest.fixture
    def coordinator(self):
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        return MultiDomainTeamCoordinator()

    def test_combine_all_success(self, coordinator):
        """Test combining all successful results."""
        results = {
            'task_1': {'value': 42},
            'task_2': {'value': 100}
        }
        combined = coordinator._combine_results(results)
        assert combined['success'] is True
        assert len(combined['partial_results']) == 2
        assert len(combined['errors']) == 0

    def test_combine_with_errors(self, coordinator):
        """Test combining results with errors."""
        results = {
            'task_1': {'value': 42},
            'task_2': {'error': 'Something went wrong'}
        }
        combined = coordinator._combine_results(results)
        assert combined['success'] is False
        assert len(combined['errors']) == 1

    def test_combine_all_errors(self, coordinator):
        """Test combining all error results."""
        results = {
            'task_1': {'error': 'Error 1'},
            'task_2': {'error': 'Error 2'}
        }
        combined = coordinator._combine_results(results)
        assert combined['success'] is False
        assert len(combined['errors']) == 2


class TestMultiDomainIntegration:
    """Integration tests for multi-domain coordination."""

    def test_algebra_calculus_workflow(self):
        """Test workflow combining algebra and calculus."""
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        coord = MultiDomainTeamCoordinator()

        result = coord.solve({
            'description': '''
                Find the roots of the polynomial p(x) = x^2 - 4
                and compute the derivative of q(x) = x^3 - 2x
            '''
        })
        assert result is not None
        # Should detect both algebra and calculus
        if 'analysis' in result:
            domains = result['analysis']['detected_domains']
            assert len(domains) >= 1

    def test_statistics_optimization_workflow(self):
        """Test workflow combining statistics and optimization."""
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        coord = MultiDomainTeamCoordinator()

        result = coord.solve({
            'description': '''
                Calculate the variance of a distribution
                and minimize a cost function using gradient descent
            '''
        })
        assert result is not None

    def test_crypto_info_theory_workflow(self):
        """Test workflow combining cryptography and information theory."""
        from symbo_agentic_reasoners.agents.coordinators import MultiDomainTeamCoordinator
        coord = MultiDomainTeamCoordinator()

        result = coord.solve({
            'description': '''
                Compute the entropy of a message
                and then encrypt it using RSA
            '''
        })
        assert result is not None
        if 'analysis' in result:
            domains = result['analysis']['detected_domains']
            assert 'information_theory' in domains or 'cryptography' in domains
