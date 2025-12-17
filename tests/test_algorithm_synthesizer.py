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
Algorithm Synthesizer Tests
===========================

Comprehensive tests for the Algorithm Synthesizer module.
"""

import pytest


class TestAlgorithmCategory:
    """Tests for AlgorithmCategory enum."""

    def test_enum_exists(self):
        """AlgorithmCategory enum should exist."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmCategory
        )
        assert AlgorithmCategory is not None

    def test_sorting_category(self):
        """Should have SORTING category."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmCategory
        )
        assert AlgorithmCategory.SORTING.value == "sorting"

    def test_searching_category(self):
        """Should have SEARCHING category."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmCategory
        )
        assert AlgorithmCategory.SEARCHING.value == "searching"

    def test_graph_category(self):
        """Should have GRAPH category."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmCategory
        )
        assert AlgorithmCategory.GRAPH.value == "graph"

    def test_dp_category(self):
        """Should have DYNAMIC_PROGRAMMING category."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmCategory
        )
        assert AlgorithmCategory.DYNAMIC_PROGRAMMING.value == "dynamic_programming"


class TestSynthesisStatus:
    """Tests for SynthesisStatus enum."""

    def test_enum_exists(self):
        """SynthesisStatus enum should exist."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            SynthesisStatus
        )
        assert SynthesisStatus is not None

    def test_pending_status(self):
        """Should have PENDING status."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            SynthesisStatus
        )
        assert SynthesisStatus.PENDING.value == "pending"

    def test_complete_status(self):
        """Should have COMPLETE status."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            SynthesisStatus
        )
        assert SynthesisStatus.COMPLETE.value == "complete"

    def test_failed_status(self):
        """Should have FAILED status."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            SynthesisStatus
        )
        assert SynthesisStatus.FAILED.value == "failed"


class TestAlgorithmSpec:
    """Tests for AlgorithmSpec dataclass."""

    def test_creation(self):
        """Should create AlgorithmSpec."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmSpec
        )
        spec = AlgorithmSpec(
            spec_id="test_001",
            name="test_algorithm",
            description="A test algorithm",
            inputs=[{"arr": "List[int]"}],
            outputs={"result": "int"}
        )
        assert spec.spec_id == "test_001"
        assert spec.name == "test_algorithm"

    def test_to_dict(self):
        """AlgorithmSpec to_dict should work."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmSpec
        )
        spec = AlgorithmSpec(
            spec_id="test_001",
            name="test_algorithm",
            description="A test algorithm",
            inputs=[{"arr": "List[int]"}],
            outputs={"result": "int"},
            constraints=["arr must be sorted"],
            examples=[{"input": [1, 2, 3], "output": 6}]
        )
        d = spec.to_dict()
        assert d['id'] == "test_001"
        assert d['name'] == "test_algorithm"
        assert d['inputs'] == 1
        assert d['constraints'] == 1
        assert d['examples'] == 1


class TestSynthesizedAlgorithm:
    """Tests for SynthesizedAlgorithm dataclass."""

    def test_creation(self):
        """Should create SynthesizedAlgorithm."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmSpec, SynthesizedAlgorithm, AlgorithmCategory, SynthesisStatus
        )
        spec = AlgorithmSpec(
            spec_id="test_001",
            name="test_algorithm",
            description="A test algorithm",
            inputs=[{"arr": "List[int]"}],
            outputs={"result": "int"}
        )
        algo = SynthesizedAlgorithm(
            algorithm_id="algo_001",
            spec=spec,
            code="def test_algorithm(arr): return sum(arr)",
            category=AlgorithmCategory.NUMERICAL,
            time_complexity="O(n)",
            space_complexity="O(1)",
            correctness_notes=["Verified for positive integers"]
        )
        assert algo.algorithm_id == "algo_001"
        assert algo.status == SynthesisStatus.COMPLETE

    def test_to_dict(self):
        """SynthesizedAlgorithm to_dict should work."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmSpec, SynthesizedAlgorithm, AlgorithmCategory
        )
        spec = AlgorithmSpec(
            spec_id="test_001",
            name="test_algorithm",
            description="A test",
            inputs=[],
            outputs={}
        )
        algo = SynthesizedAlgorithm(
            algorithm_id="algo_001",
            spec=spec,
            code="pass",
            category=AlgorithmCategory.SORTING,
            time_complexity="O(n log n)",
            space_complexity="O(n)",
            correctness_notes=[],
            test_results=[{"passed": True}, {"passed": False}]
        )
        d = algo.to_dict()
        assert d['id'] == "algo_001"
        assert d['time'] == "O(n log n)"
        assert d['tests_passed'] == 1


class TestAlgorithmSynthesizer:
    """Tests for AlgorithmSynthesizer class."""

    @pytest.fixture
    def synthesizer(self):
        """Create AlgorithmSynthesizer instance."""
        from symbo_agentic_reasoners.discovery.algorithm.algorithm_synthesizer import (
            AlgorithmSynthesizer
        )
        return AlgorithmSynthesizer()

    def test_initialization(self, synthesizer):
        """Should initialize correctly."""
        assert synthesizer is not None
        assert synthesizer.specs_processed == 0

    def test_has_templates(self, synthesizer):
        """Should have algorithm templates."""
        assert hasattr(synthesizer, 'TEMPLATES')
        assert 'binary_search' in synthesizer.TEMPLATES
        assert 'merge_sort' in synthesizer.TEMPLATES
        assert 'dfs' in synthesizer.TEMPLATES
        assert 'bfs' in synthesizer.TEMPLATES

    def test_has_synthesized_dict(self, synthesizer):
        """Should have synthesized algorithms cache."""
        assert hasattr(synthesizer, 'synthesized')
        assert isinstance(synthesizer.synthesized, dict)

    def test_has_get_statistics(self, synthesizer):
        """Should have get_statistics method."""
        assert hasattr(synthesizer, 'get_statistics')

    def test_has_health_check(self, synthesizer):
        """Should have health_check method."""
        assert hasattr(synthesizer, 'health_check')

    def test_get_statistics_returns_dict(self, synthesizer):
        """get_statistics should return dict."""
        stats = synthesizer.get_statistics()
        assert isinstance(stats, dict)

    def test_health_check_exists(self, synthesizer):
        """health_check should exist."""
        assert hasattr(synthesizer, 'health_check')


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
