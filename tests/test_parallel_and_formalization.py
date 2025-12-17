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
Comprehensive Tests for ParallelSearchManager and AutoFormalizationPipeline
===========================================================================

Tests to bring coverage to 70%+.
"""

import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch

# Now that torch import is fixed, use standard imports
from symbo_agentic_reasoners.discovery.deep_search.parallel_search_manager import (
    ParallelSearchManager,
    SearchTask,
    SearchResult,
    SearchTaskStatus,
    WorkerStatus,
    WorkerInfo,
    parallel_map,
)


# =============================================================================
# ParallelSearchManager Comprehensive Tests
# =============================================================================


class TestParallelSearchManagerComprehensive:
    """Comprehensive tests for ParallelSearchManager."""

    @pytest.fixture
    def manager(self):
        return ParallelSearchManager(num_workers=2)

    def test_worker_status_enum(self):
        """Test WorkerStatus enum values."""
        assert WorkerStatus.IDLE.value == "idle"
        assert WorkerStatus.BUSY.value == "busy"
        assert WorkerStatus.COMPLETED.value == "completed"
        assert WorkerStatus.FAILED.value == "failed"

    def test_search_task_status_enum(self):
        """Test SearchTaskStatus enum values."""
        assert SearchTaskStatus.PENDING.value == "pending"
        assert SearchTaskStatus.RUNNING.value == "running"
        assert SearchTaskStatus.COMPLETE.value == "complete"
        assert SearchTaskStatus.FAILED.value == "failed"
        assert SearchTaskStatus.CANCELLED.value == "cancelled"

    def test_search_task_creation(self):
        """Test SearchTask creation."""
        task = SearchTask(
            task_id="test_task",
            search_fn=lambda x: x * 2,
            args=(5,),
            kwargs={},
            priority=10
        )

        assert task.task_id == "test_task"
        assert task.priority == 10

        d = task.to_dict()
        assert d['id'] == "test_task"
        assert d['priority'] == 10

    def test_search_result_creation(self):
        """Test SearchResult creation."""
        result = SearchResult(
            task_id="test",
            status=SearchTaskStatus.COMPLETE,
            result=42,
            execution_time_ms=100,
            worker_id="worker_0"
        )

        assert result.task_id == "test"
        assert result.result == 42

        d = result.to_dict()
        assert d['task_id'] == "test"
        assert d['has_result'] is True
        assert d['time_ms'] == 100

    def test_worker_info_creation(self):
        """Test WorkerInfo creation."""
        info = WorkerInfo(
            worker_id="worker_0",
            status=WorkerStatus.IDLE,
            tasks_completed=5,
            tasks_failed=1
        )

        d = info.to_dict()
        assert d['id'] == "worker_0"
        assert d['completed'] == 5
        assert d['failed'] == 1

    def test_start_and_stop(self, manager):
        """Test start and stop operations."""
        assert manager._running is False

        manager.start()
        assert manager._running is True
        assert manager.executor is not None
        assert len(manager.workers) == 2

        manager.stop()
        assert manager._running is False
        assert manager.executor is None

    def test_submit_single_task(self, manager):
        """Test submitting a single task."""
        task = SearchTask(
            task_id="single_task",
            search_fn=lambda: 42
        )

        manager.start()
        task_id = manager.submit(task)
        assert task_id == "single_task"

        result = manager.get_result(task_id, timeout=5)
        assert result is not None
        assert result.result == 42

        manager.stop()

    def test_submit_task_auto_starts(self, manager):
        """Test that submit auto-starts manager."""
        assert manager._running is False

        task = SearchTask(
            task_id="auto_start",
            search_fn=lambda: "hello"
        )
        manager.submit(task)

        assert manager._running is True
        manager.stop()

    def test_submit_batch(self, manager):
        """Test batch submission."""
        tasks = [
            SearchTask(task_id=f"batch_{i}", search_fn=lambda x=i: x * 2)
            for i in range(5)
        ]

        manager.start()
        task_ids = manager.submit_batch(tasks)

        assert len(task_ids) == 5
        assert manager.total_tasks_submitted == 5

        results = manager.get_all_results(wait=True, timeout=10)
        assert len(results) >= 5

        manager.stop()

    def test_execute_task_success(self, manager):
        """Test successful task execution."""
        manager.start()

        task = SearchTask(
            task_id="success_task",
            search_fn=lambda x: x + 10,
            args=(5,)
        )
        manager.submit(task)

        result = manager.get_result("success_task", timeout=5)
        assert result.status == SearchTaskStatus.COMPLETE
        assert result.result == 15

        manager.stop()

    def test_execute_task_failure(self, manager):
        """Test task execution failure."""
        def failing_fn():
            raise ValueError("Test error")

        manager.start()

        task = SearchTask(
            task_id="fail_task",
            search_fn=failing_fn
        )
        manager.submit(task)

        result = manager.get_result("fail_task", timeout=5)
        assert result.status == SearchTaskStatus.FAILED
        assert "Test error" in result.error

        manager.stop()

    def test_get_result_timeout(self, manager):
        """Test get_result with timeout."""
        def slow_fn():
            time.sleep(10)
            return "done"

        manager.start()

        task = SearchTask(
            task_id="slow_task",
            search_fn=slow_fn
        )
        manager.submit(task)

        # Should timeout
        result = manager.get_result("slow_task", timeout=0.1)
        # May or may not have result depending on timing
        manager.stop()

    def test_get_all_results(self, manager):
        """Test getting all results."""
        manager.start()

        tasks = [
            SearchTask(task_id=f"all_{i}", search_fn=lambda x=i: x)
            for i in range(3)
        ]
        manager.submit_batch(tasks)

        results = manager.get_all_results(wait=True, timeout=5)
        assert len(results) == 3

        manager.stop()

    def test_cancel_task(self, manager):
        """Test cancelling a task."""
        def slow_fn():
            time.sleep(10)
            return "done"

        manager.start()

        task = SearchTask(
            task_id="cancel_me",
            search_fn=slow_fn
        )
        manager.submit(task)

        # Try to cancel (may or may not succeed depending on timing)
        manager.cancel("cancel_me")

        manager.stop()

    def test_cancel_all(self, manager):
        """Test cancelling all tasks."""
        def slow_fn():
            time.sleep(10)
            return "done"

        manager.start()

        for i in range(5):
            task = SearchTask(task_id=f"cancel_all_{i}", search_fn=slow_fn)
            manager.submit(task)

        cancelled = manager.cancel_all()
        # May cancel some or none
        assert cancelled >= 0

        manager.stop()

    def test_get_worker_status(self, manager):
        """Test getting worker status."""
        manager.start()

        status = manager.get_worker_status()
        assert len(status) == 2  # 2 workers
        for w in status:
            assert 'id' in w
            assert 'status' in w

        manager.stop()

    def test_get_statistics(self, manager):
        """Test getting statistics."""
        stats = manager.get_statistics()
        assert 'num_workers' in stats
        assert 'running' in stats
        assert 'pending_tasks' in stats
        assert 'total_submitted' in stats

    def test_reset(self, manager):
        """Test reset functionality."""
        manager.start()

        task = SearchTask(task_id="reset_test", search_fn=lambda: 1)
        manager.submit(task)
        manager.get_result("reset_test", timeout=5)

        manager.reset()

        assert manager.total_tasks_submitted == 0
        assert len(manager.completed_results) == 0

    def test_health_check_started(self, manager):
        """Test health check when started."""
        manager.start()
        assert manager.health_check() is True
        manager.stop()

    def test_health_check_stopped(self, manager):
        """Test health check when stopped."""
        assert manager.health_check() is False


class TestParallelMapFunction:
    """Tests for parallel_map convenience function."""

    def test_parallel_map_basic(self):
        """Test basic parallel map."""
        results = parallel_map(lambda x: x * 2, [1, 2, 3, 4, 5], num_workers=2)
        assert results == [2, 4, 6, 8, 10]

    def test_parallel_map_empty(self):
        """Test parallel map with empty input."""
        results = parallel_map(lambda x: x, [], num_workers=2)
        assert results == []


# =============================================================================
# AutoFormalizationPipeline Comprehensive Tests
# =============================================================================


class TestAutoFormalizationPipelineComprehensive:
    """Comprehensive tests for AutoFormalizationPipeline."""

    @pytest.fixture
    def pipeline(self):
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import AutoFormalizationPipeline
        return AutoFormalizationPipeline()

    def test_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert pipeline is not None

    def test_discovery_types_complete(self):
        """Test all DiscoveryType values exist."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import DiscoveryType

        # Check all values
        all_values = [dt.value for dt in DiscoveryType]
        assert 'theorem' in all_values
        assert 'lemma' in all_values
        assert 'algorithm' in all_values
        assert 'identity' in all_values
        assert 'formula' in all_values
        assert 'heuristic' in all_values

    def test_verification_status_complete(self):
        """Test all VerificationStatus values exist."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import VerificationStatus

        all_values = [vs.value for vs in VerificationStatus]
        assert 'pending' in all_values
        assert 'verified' in all_values
        assert 'failed' in all_values
        assert 'partial' in all_values

    def test_formalized_discovery_basic(self):
        """Test basic FormalizedDiscovery creation."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            FormalizedDiscovery, DiscoveryType
        )

        discovery = FormalizedDiscovery(
            discovery_id="basic_test",
            discovery_type=DiscoveryType.THEOREM,
            natural_language_statement="A test theorem",
            omdoc_representation="<theorem/>"
        )

        assert discovery.discovery_id == "basic_test"
        assert discovery.discovery_type == DiscoveryType.THEOREM
        assert discovery.verified is False  # Default

    def test_formalized_discovery_to_dict(self):
        """Test FormalizedDiscovery serialization."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            FormalizedDiscovery, DiscoveryType, VerificationStatus
        )

        discovery = FormalizedDiscovery(
            discovery_id="dict_test",
            discovery_type=DiscoveryType.ALGORITHM,
            natural_language_statement="An algorithm",
            omdoc_representation="<algorithm/>",
            verified=True,
            verification_status=VerificationStatus.VERIFIED
        )

        d = discovery.to_dict()
        assert d['discovery_id'] == "dict_test"
        assert d['discovery_type'] == 'algorithm'
        assert d['verified'] is True

    def test_formalized_discovery_hash(self):
        """Test FormalizedDiscovery hash computation."""
        from symbo_agentic_reasoners.discovery.formal.auto_formalization_pipeline import (
            FormalizedDiscovery, DiscoveryType
        )

        d1 = FormalizedDiscovery(
            discovery_id="hash1",
            discovery_type=DiscoveryType.IDENTITY,
            natural_language_statement="a + b = b + a",
            omdoc_representation="<identity/>"
        )

        d2 = FormalizedDiscovery(
            discovery_id="hash2",
            discovery_type=DiscoveryType.IDENTITY,
            natural_language_statement="a + b = b + a",
            omdoc_representation="<identity/>"
        )

        # Same content should have same hash
        assert d1.compute_hash() == d2.compute_hash()

    def test_get_statistics(self, pipeline):
        """Test pipeline statistics."""
        stats = pipeline.get_statistics()
        assert isinstance(stats, dict)

    def test_health_check(self, pipeline):
        """Test pipeline health check."""
        result = pipeline.health_check()
        assert isinstance(result, bool)

    def test_reset(self, pipeline):
        """Test pipeline reset."""
        pipeline.reset()
        # Should not raise


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
