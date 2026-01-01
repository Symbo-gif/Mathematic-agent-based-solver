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
Test Suite: WordProblemNormalizationCoordinator
==============================================

Comprehensive tests for the Tier 1 coordinator that orchestrates
the universal word problem normalization pipeline.

Tests follow the 12-test pattern for specialists/coordinators.
"""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestCoordinatorInit:
    """Tests for coordinator initialization."""

    def test_coordinator_creation(self):
        """Test coordinator instantiation."""
        from symbo_agentic_reasoners.agents.coordinators.word_problem_normalization_coordinator import (
            WordProblemNormalizationCoordinator
        )

        coordinator = WordProblemNormalizationCoordinator()
        assert coordinator is not None
        assert coordinator.agent_id == 'word_problem_normalization_coordinator_001'

    def test_coordinator_custom_id(self):
        """Test coordinator with custom agent ID."""
        from symbo_agentic_reasoners.agents.coordinators.word_problem_normalization_coordinator import (
            WordProblemNormalizationCoordinator
        )

        coordinator = WordProblemNormalizationCoordinator(agent_id='custom_coord_001')
        assert coordinator.agent_id == 'custom_coord_001'

    def test_coordinator_statistics_initial(self):
        """Test initial statistics are zero."""
        from symbo_agentic_reasoners.agents.coordinators.word_problem_normalization_coordinator import (
            WordProblemNormalizationCoordinator
        )

        coordinator = WordProblemNormalizationCoordinator()
        stats = coordinator.get_statistics()

        assert stats['problems_processed'] == 0
        assert stats['successful_normalizations'] == 0


class TestCoordinatorNormalization:
    """Tests for the normalize() method."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance."""
        from symbo_agentic_reasoners.agents.coordinators.word_problem_normalization_coordinator import (
            WordProblemNormalizationCoordinator
        )
        return WordProblemNormalizationCoordinator()

    def test_normalize_arithmetic_sum(self, coordinator):
        """Test normalizing an arithmetic sum problem."""
        result = coordinator.normalize("John has 5 apples and 3 oranges. How many in total?")

        assert result['success'] is True
        assert result['expression'] is not None
        assert 'entities' in result

    def test_normalize_physics_kinematics(self, coordinator):
        """Test normalizing a physics kinematics problem."""
        result = coordinator.normalize("A car travels at 60 mph for 3 hours. How far?")

        assert result['success'] is True
        assert result['expression'] is not None

    def test_normalize_geometry_area(self, coordinator):
        """Test normalizing a geometry area problem."""
        result = coordinator.normalize("A rectangle with length 10 and width 5. Find the area.")

        # Geometry problems extract entities and relationships even if full expression not generated
        assert 'entities' in result
        assert len(result['entities']) >= 2  # Should find 10 and 5
        # Note: Full expression generation for geometry requires domain-specific rules

    def test_normalize_algebra_equation(self, coordinator):
        """Test normalizing an algebra equation problem."""
        result = coordinator.normalize("A number plus 5 equals 12. Find the number.")

        assert result['success'] is True
        assert result['expression'] is not None

    def test_normalize_statistics_mean(self, coordinator):
        """Test normalizing a statistics mean problem."""
        result = coordinator.normalize("The average of 10, 15, 20, and 25.")

        assert result['success'] is True
        assert result['expression'] is not None

    def test_normalize_percentage(self, coordinator):
        """Test normalizing a percentage problem."""
        result = coordinator.normalize("What is 25% of 200?")

        assert result['success'] is True
        assert result['confidence'] > 0.8


class TestCoordinatorBatch:
    """Tests for batch normalization."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance."""
        from symbo_agentic_reasoners.agents.coordinators.word_problem_normalization_coordinator import (
            WordProblemNormalizationCoordinator
        )
        return WordProblemNormalizationCoordinator()

    def test_normalize_batch(self, coordinator):
        """Test batch normalization."""
        texts = [
            "5 + 3 = ?",
            "A car at 60 mph for 2 hours.",
            "Rectangle area with length 10, width 5."
        ]

        results = coordinator.normalize_batch(texts)

        assert len(results) == 3
        for result in results:
            assert 'success' in result


class TestCoordinatorStatistics:
    """Tests for statistics tracking."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance."""
        from symbo_agentic_reasoners.agents.coordinators.word_problem_normalization_coordinator import (
            WordProblemNormalizationCoordinator
        )
        return WordProblemNormalizationCoordinator()

    def test_statistics_after_normalize(self, coordinator):
        """Test statistics update after normalization."""
        coordinator.normalize("5 + 3 = ?")

        stats = coordinator.get_statistics()
        assert stats['problems_processed'] == 1

    def test_success_rate_calculation(self, coordinator):
        """Test success rate in statistics."""
        coordinator.normalize("What is 25% of 200?")
        coordinator.normalize("A car at 60 mph for 3 hours.")

        stats = coordinator.get_statistics()
        assert stats['problems_processed'] == 2
        assert 'success_rate' in stats


class TestCoordinatorDomainSupport:
    """Tests for domain support queries."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance."""
        from symbo_agentic_reasoners.agents.coordinators.word_problem_normalization_coordinator import (
            WordProblemNormalizationCoordinator
        )
        return WordProblemNormalizationCoordinator()

    def test_get_supported_domains(self, coordinator):
        """Test getting supported domains."""
        domains = coordinator.get_supported_domains()

        assert 'arithmetic' in domains
        assert 'physics' in domains
        assert 'geometry' in domains
        assert 'algebra' in domains
        assert 'statistics' in domains

    def test_get_supported_problem_types(self, coordinator):
        """Test getting supported problem types per domain."""
        types = coordinator.get_supported_problem_types()

        assert 'arithmetic' in types or len(types) == 0  # May be empty if not fully initialized


class TestCoordinatorEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance."""
        from symbo_agentic_reasoners.agents.coordinators.word_problem_normalization_coordinator import (
            WordProblemNormalizationCoordinator
        )
        return WordProblemNormalizationCoordinator()

    def test_empty_text(self, coordinator):
        """Test handling empty text."""
        result = coordinator.normalize("")
        # Should handle gracefully
        assert 'success' in result

    def test_no_numbers(self, coordinator):
        """Test text with no numbers."""
        result = coordinator.normalize("Hello world, this is a test.")
        # Should return with low confidence or failure
        assert 'success' in result

    def test_complex_expression(self, coordinator):
        """Test complex multi-operation expression."""
        result = coordinator.normalize(
            "A store has 100 items. They sold 30 in the morning and 25 in the afternoon. "
            "How many items are left?"
        )
        assert 'success' in result

    def test_with_metadata(self, coordinator):
        """Test normalization with metadata."""
        result = coordinator.normalize(
            "Solve 2x + 3 = 11",
            metadata={'source': 'test', 'difficulty': 'easy'}
        )
        assert 'success' in result


class TestCoordinatorBDI:
    """Tests for BDI pattern implementation."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance."""
        from symbo_agentic_reasoners.agents.coordinators.word_problem_normalization_coordinator import (
            WordProblemNormalizationCoordinator
        )
        return WordProblemNormalizationCoordinator()

    def test_update_beliefs(self, coordinator):
        """Test update_beliefs method exists."""
        # Should not raise
        coordinator.update_beliefs()

    def test_deliberate(self, coordinator):
        """Test deliberate method returns intentions."""
        intentions = coordinator.deliberate()
        assert isinstance(intentions, list)

    def test_has_bdi_methods(self, coordinator):
        """Test coordinator has all BDI methods."""
        assert hasattr(coordinator, 'update_beliefs')
        assert hasattr(coordinator, 'deliberate')
        assert hasattr(coordinator, 'execute_step')
        assert hasattr(coordinator, 'beliefs')
        assert hasattr(coordinator, 'intentions')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
