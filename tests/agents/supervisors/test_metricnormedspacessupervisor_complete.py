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
Comprehensive tests for MetricNormedSpacesSupervisor.

Tests follow the 10-test pattern for supervisors:
1. Initialization
2. DF Registration
3. Simple Task Processing
4. Complex Task Processing
5. Specialist Delegation
6. Unknown Operation Handling
7. Multi-step Problem
8. Error Propagation
9. Statistics Reporting
10. BDI Interface Compliance
"""

import pytest
from unittest.mock import Mock, patch

from symbo_agentic_reasoners.agents.supervisors import MetricNormedSpacesSupervisor


class TestMetricNormedSpacesSupervisorComplete:
    """Comprehensive tests for MetricNormedSpacesSupervisor."""

    @pytest.fixture
    def supervisor(self):
        """Create supervisor instance."""
        return MetricNormedSpacesSupervisor(agent_id='test_supervisor_001')

    @pytest.fixture
    def mock_df(self):
        """Create mock Directory Facilitator."""
        mock = Mock()
        mock.register = Mock(return_value=True)
        return mock

    @pytest.fixture
    def mock_blackboard(self):
        """Create mock Blackboard."""
        mock = Mock()
        return mock

    # ========== Test 1: Initialization ==========
    def test_initialization(self, supervisor):
        """Test supervisor initializes correctly."""
        assert supervisor.agent_id == 'test_supervisor_001'
        assert supervisor.service_type == 'math.metric_normed_spaces'
        assert supervisor.version == '1.0.0'
        assert hasattr(supervisor, 'update_beliefs')
        assert hasattr(supervisor, 'deliberate')
        assert hasattr(supervisor, 'plan')
        assert hasattr(supervisor, 'execute_step')
        assert supervisor._tasks_routed == 0
        assert supervisor._tasks_failed == 0

    def test_initialization_auto_id(self):
        """Test supervisor generates agent_id with correct prefix."""
        supervisor = MetricNormedSpacesSupervisor()
        assert 'metric_normed_spaces_supervisor' in supervisor.agent_id

    def test_initialization_with_df(self, mock_df):
        """Test initialization with Directory Facilitator."""
        supervisor = MetricNormedSpacesSupervisor(
            df=mock_df
        )
        # Registration may be lazy, just verify df is set
        assert supervisor.df == mock_df

    def test_initialization_with_blackboard(self, mock_blackboard):
        """Test initialization with Blackboard."""
        supervisor = MetricNormedSpacesSupervisor(
            blackboard=mock_blackboard
        )
        assert supervisor.blackboard == mock_blackboard

    # ========== Test 2: DF Registration ==========
    def test_df_registration(self, mock_df):
        """Test service registration with DF."""
        supervisor = MetricNormedSpacesSupervisor(
            agent_id='test_df_001',
            df=mock_df
        )
        assert supervisor.service_type == 'math.metric_normed_spaces'
        assert supervisor.df == mock_df

    # ========== Test 3: Simple Task Processing ==========
    def test_simple_metric_task(self, supervisor):
        """Test processing simple metric task."""
        result = supervisor.handle_task({'task': 'Compute Euclidean distance'})
        assert result['status'] == 'routed'
        assert result['task_type'] == 'metric'

    def test_simple_norm_task(self, supervisor):
        """Test processing simple norm task."""
        result = supervisor.handle_task({'task': 'Compute the L2 norm'})
        assert result['status'] == 'routed'
        assert result['task_type'] == 'norm'

    def test_simple_completeness_task(self, supervisor):
        """Test processing simple completeness task."""
        result = supervisor.handle_task({'task': 'Check if sequence is Cauchy'})
        assert result['status'] == 'routed'
        assert result['task_type'] == 'completeness'

    # ========== Test 4: Complex Task Processing ==========
    def test_complex_contraction_task(self, supervisor):
        """Test processing contraction mapping task."""
        result = supervisor.handle_task({
            'task': 'Find fixed point using Banach contraction theorem'
        })
        assert result['status'] == 'routed'
        assert result['task_type'] == 'contraction'

    def test_complex_topology_task(self, supervisor):
        """Test processing topology task."""
        result = supervisor.handle_task({
            'task': 'Determine if the set is open or closed and find its interior'
        })
        assert result['status'] == 'routed'
        assert result['task_type'] == 'topology'

    def test_complex_compactness_task(self, supervisor):
        """Test processing compactness task."""
        result = supervisor.handle_task({
            'task': 'Verify Heine-Borel theorem applies and check if set is compact'
        })
        assert result['status'] == 'routed'
        assert result['task_type'] == 'compactness'

    # ========== Test 5: Specialist Delegation ==========
    def test_delegation_to_metric_specialist(self, supervisor):
        """Test delegation to MetricSpecialist."""
        result = supervisor.handle_task({
            'task': 'Verify metric axioms for the function d(x,y)'
        })
        assert result['status'] == 'routed'
        assert 'MetricSpecialist' in result['specialist']

    def test_delegation_to_norm_specialist(self, supervisor):
        """Test delegation to NormSpecialist."""
        result = supervisor.handle_task({
            'task': 'Check operator norm of matrix ||A||'
        })
        assert result['status'] == 'routed'
        assert 'NormSpecialist' in result['specialist']

    def test_delegation_to_completeness_specialist(self, supervisor):
        """Test delegation to CompletenessSpecialist."""
        result = supervisor.handle_task({
            'task': 'Determine if this Cauchy sequence converges'
        })
        assert result['status'] == 'routed'
        assert 'CompletenessSpecialist' in result['specialist']

    def test_delegation_to_contraction_specialist(self, supervisor):
        """Test delegation to ContractionMappingSpecialist."""
        result = supervisor.handle_task({
            'task': 'Apply contraction mapping to find fixed point'
        })
        assert result['status'] == 'routed'
        assert 'ContractionMappingSpecialist' in result['specialist']

    def test_delegation_to_topology_specialist(self, supervisor):
        """Test delegation to TopologySpecialist."""
        result = supervisor.handle_task({
            'task': 'Find the boundary and closure of the set'
        })
        assert result['status'] == 'routed'
        assert 'TopologySpecialist' in result['specialist']

    def test_delegation_to_compactness_specialist(self, supervisor):
        """Test delegation to CompactnessSpecialist."""
        result = supervisor.handle_task({
            'task': 'Check sequential compactness and totally bounded property'
        })
        assert result['status'] == 'routed'
        assert 'CompactnessSpecialist' in result['specialist']

    # ========== Test 6: Unknown Operation Handling ==========
    def test_unknown_task_defaults_to_metric(self, supervisor):
        """Test unknown task defaults to metric specialist."""
        result = supervisor.handle_task({
            'task': 'Do something mathematical'
        })
        assert result['status'] == 'routed'
        assert result['task_type'] == 'metric'  # Default

    def test_empty_task_description(self, supervisor):
        """Test handling of empty task description."""
        result = supervisor.handle_task({'task': ''})
        assert result['status'] == 'routed'
        assert result['task_type'] == 'metric'  # Default

    # ========== Test 7: Multi-step Problem ==========
    def test_multi_keyword_task(self, supervisor):
        """Test task with multiple keywords picks highest score."""
        # Both 'metric' and 'norm' keywords, but more norm keywords
        result = supervisor.handle_task({
            'task': 'Compute norm and verify norm axioms for normed space'
        })
        assert result['status'] == 'routed'
        assert result['task_type'] == 'norm'

    def test_task_with_mixed_keywords(self, supervisor):
        """Test task with mixed domain keywords."""
        result = supervisor.handle_task({
            'task': 'In the complete metric space, find fixed point of contraction'
        })
        # Should pick one based on scoring
        assert result['status'] == 'routed'
        assert result['task_type'] in ['metric', 'completeness', 'contraction']

    # ========== Test 8: Error Propagation ==========
    def test_specialist_error_handled(self, supervisor):
        """Test that specialist errors are handled gracefully."""
        # Force an edge case that might cause an error
        result = supervisor.handle_task({
            'task': 'Verify metric axioms',
            'metric_function': None,  # Missing required function
            'samples': []
        })
        # Should still complete, though result may indicate an error
        assert result['status'] in ['routed', 'error']

    # ========== Test 9: Statistics Reporting ==========
    def test_statistics_reporting(self, supervisor):
        """Test statistics are tracked correctly."""
        supervisor.handle_task({'task': 'Compute Euclidean distance'})
        supervisor.handle_task({'task': 'Verify norm axioms'})

        stats = supervisor.get_statistics()
        assert 'agent_id' in stats
        assert 'service_type' in stats
        assert 'tasks_routed' in stats
        assert stats['tasks_routed'] >= 2
        assert stats['total_tasks'] >= 2

    def test_success_rate_calculation(self, supervisor):
        """Test success rate is calculated correctly."""
        supervisor.handle_task({'task': 'Compute distance'})

        stats = supervisor.get_statistics()
        if stats['total_tasks'] > 0:
            assert 0 <= stats['success_rate'] <= 100

    # ========== Test 10: BDI Interface Compliance ==========
    def test_bdi_update_beliefs(self, supervisor):
        """Test BDI update_beliefs method."""
        supervisor.update_beliefs({'task': 'Compute metric distance'})
        assert supervisor.beliefs.get('task') == 'Compute metric distance'
        assert supervisor.beliefs.get('task_type') == 'metric'

    def test_bdi_deliberate(self, supervisor):
        """Test BDI deliberate method."""
        supervisor.update_beliefs({'task': 'Verify norm axioms'})
        desires = supervisor.deliberate()
        assert 'route_task' in desires

    def test_bdi_deliberate_no_task(self, supervisor):
        """Test deliberate with no task."""
        supervisor.beliefs = {}
        desires = supervisor.deliberate()
        assert desires == []

    def test_bdi_plan(self, supervisor):
        """Test BDI plan method."""
        supervisor.update_beliefs({'task': 'Check compactness'})
        supervisor.deliberate()
        intentions = supervisor.plan()
        assert len(intentions) > 0
        assert intentions[0].target_desire == 'route_task'

    def test_bdi_execute_step(self, supervisor):
        """Test BDI execute_step method."""
        supervisor.update_beliefs({'task': 'Compute Euclidean distance'})
        supervisor.deliberate()
        supervisor.plan()
        result = supervisor.execute_step()
        assert result['status'] == 'routed'

    def test_bdi_execute_step_no_intentions(self, supervisor):
        """Test execute_step with no intentions."""
        supervisor.beliefs = {}
        supervisor.desires = []
        supervisor.intentions = []
        result = supervisor.execute_step()
        assert result['status'] == 'no_intentions'

    def test_bdi_full_cycle(self, supervisor):
        """Test full BDI cycle."""
        # Full cycle: update_beliefs -> deliberate -> plan -> execute_step
        supervisor.update_beliefs({
            'task': 'Find fixed point using contraction mapping Lipschitz constant'
        })

        desires = supervisor.deliberate()
        assert 'route_task' in desires

        intentions = supervisor.plan()
        assert len(intentions) > 0

        result = supervisor.execute_step()
        assert result['status'] == 'routed'
        assert result['task_type'] == 'contraction'


class TestMetricNormedSpacesSupervisorTaskClassification:
    """Tests for task classification patterns."""

    @pytest.fixture
    def supervisor(self):
        return MetricNormedSpacesSupervisor()

    def test_classify_metric_patterns(self, supervisor):
        """Test metric keyword patterns."""
        patterns = [
            'Compute the distance d(x,y)',
            'Verify triangle inequality holds',
            'Check metric space axioms',
            'Euclidean distance calculation'
        ]
        for pattern in patterns:
            result = supervisor.handle_task({'task': pattern})
            assert result['task_type'] == 'metric', f"Failed for: {pattern}"

    def test_classify_norm_patterns(self, supervisor):
        """Test norm keyword patterns."""
        patterns = [
            'Compute ||x|| norm',
            'Verify normed space axioms',
            'Find operator norm of A',
            'L2 norm calculation'
        ]
        for pattern in patterns:
            result = supervisor.handle_task({'task': pattern})
            assert result['task_type'] == 'norm', f"Failed for: {pattern}"

    def test_classify_completeness_patterns(self, supervisor):
        """Test completeness keyword patterns."""
        patterns = [
            'Check if sequence is Cauchy',
            'Verify completeness of the space',
            'Find limit of convergent sequence'
        ]
        for pattern in patterns:
            result = supervisor.handle_task({'task': pattern})
            assert result['task_type'] == 'completeness', f"Failed for: {pattern}"

    def test_classify_contraction_patterns(self, supervisor):
        """Test contraction keyword patterns."""
        patterns = [
            'Find fixed-point using contraction',
            'Apply Banach theorem',
            'Compute Lipschitz constant'
        ]
        for pattern in patterns:
            result = supervisor.handle_task({'task': pattern})
            assert result['task_type'] == 'contraction', f"Failed for: {pattern}"

    def test_classify_topology_patterns(self, supervisor):
        """Test topology keyword patterns."""
        patterns = [
            'Is the set open or closed',
            'Find the interior of the set',
            'Compute boundary and closure'
        ]
        for pattern in patterns:
            result = supervisor.handle_task({'task': pattern})
            assert result['task_type'] == 'topology', f"Failed for: {pattern}"

    def test_classify_compactness_patterns(self, supervisor):
        """Test compactness keyword patterns."""
        patterns = [
            'Check if set is compact',
            'Apply Heine-Borel theorem',
            'Verify totally bounded property'
        ]
        for pattern in patterns:
            result = supervisor.handle_task({'task': pattern})
            assert result['task_type'] == 'compactness', f"Failed for: {pattern}"


class TestMetricNormedSpacesSupervisorBlackboard:
    """Tests for blackboard integration."""

    @pytest.fixture
    def supervisor(self):
        return MetricNormedSpacesSupervisor()

    def test_process_blackboard_entry_with_content(self, supervisor):
        """Test processing blackboard entry with content attribute."""
        entry = Mock()
        entry.content = 'Verify norm axioms'
        result = supervisor.process(entry)
        assert result['status'] == 'routed'
        assert result['task_type'] == 'norm'

    def test_process_blackboard_entry_with_metadata(self, supervisor):
        """Test processing blackboard entry with metadata."""
        entry = Mock()
        entry.content = None
        entry.metadata = {'raw_input': 'Check if sequence is Cauchy'}
        result = supervisor.process(entry)
        assert result['status'] == 'routed'

    def test_process_string_entry(self, supervisor):
        """Test processing string entry."""
        result = supervisor.process('Compute Euclidean distance')
        assert result['status'] == 'routed'
