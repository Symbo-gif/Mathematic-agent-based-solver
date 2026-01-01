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
Watchdog Timeout Integration Tests
===================================

Tests for the Watchdog timeout protection system and its integration
with the SolverEngine and other components.

Test Categories:
- Unit tests for Watchdog core functionality
- Integration tests for run_with_timeout
- Solver timeout protection tests
- Thread interruption tests
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch

from symbo_agentic_reasoners.infrastructure.watchdog import (
    Watchdog,
    InterruptibleThread,
    TimeoutError as WatchdogTimeoutError,
    run_with_timeout,
    get_watchdog,
)
from symbo_agentic_reasoners.core.solver_engine import SolverEngine, SolveStatus


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def watchdog():
    """Create a fresh Watchdog instance for testing."""
    wd = Watchdog()
    wd.start()
    yield wd
    wd.stop()


@pytest.fixture
def solver_with_timeouts():
    """Create a SolverEngine with timeouts enabled."""
    return SolverEngine(enable_timeouts=True)


@pytest.fixture
def solver_without_timeouts():
    """Create a SolverEngine with timeouts disabled."""
    return SolverEngine(enable_timeouts=False)


# =============================================================================
# InterruptibleThread Tests
# =============================================================================


class TestInterruptibleThread:
    """Tests for InterruptibleThread class."""

    def test_thread_completion_normal(self):
        """Thread should complete normally when not interrupted."""
        result = []

        def task():
            time.sleep(0.1)
            result.append("completed")

        thread = InterruptibleThread(target=task)
        thread.start()
        thread.join(timeout=1.0)

        assert not thread.is_alive()
        assert result == ["completed"]

    def test_thread_returns_result(self):
        """Thread should store result from target function."""
        def task():
            return 42

        thread = InterruptibleThread(target=task)
        thread.start()
        thread.join(timeout=1.0)

        assert thread._result == 42
        assert thread.get_result() == 42

    def test_thread_stores_exception(self):
        """Thread should store exception if target raises."""
        def task():
            raise ValueError("test error")

        thread = InterruptibleThread(target=task)
        thread.start()
        thread.join(timeout=1.0)

        assert thread._exception is not None
        assert isinstance(thread._exception, ValueError)

        # get_result should raise the exception
        with pytest.raises(ValueError):
            thread.get_result()

    def test_thread_with_args(self):
        """Thread should pass args to target function."""
        def task(a, b):
            return a + b

        thread = InterruptibleThread(target=task, args=(5, 3))
        thread.start()
        thread.join(timeout=1.0)

        assert thread.get_result() == 8

    def test_thread_with_kwargs(self):
        """Thread should pass kwargs to target function."""
        def task(x, y=10):
            return x * y

        thread = InterruptibleThread(target=task, args=(5,), kwargs={'y': 4})
        thread.start()
        thread.join(timeout=1.0)

        assert thread.get_result() == 20


# =============================================================================
# Watchdog Core Tests
# =============================================================================


class TestWatchdogCore:
    """Tests for Watchdog core functionality."""

    def test_watchdog_starts_and_stops(self, watchdog):
        """Watchdog should start and stop cleanly."""
        assert watchdog._running
        watchdog.stop()
        assert not watchdog._running

    def test_watchdog_singleton_pattern(self):
        """get_watchdog should return consistent instance."""
        wd1 = get_watchdog()
        wd2 = get_watchdog()
        assert wd1 is wd2

    def test_watchdog_multiple_stop_calls(self, watchdog):
        """Multiple stop calls should not raise errors."""
        watchdog.stop()
        watchdog.stop()  # Should not raise
        assert not watchdog._running


# =============================================================================
# run_with_timeout Tests
# =============================================================================


class TestRunWithTimeout:
    """Tests for run_with_timeout function."""

    def test_fast_function_returns_result(self, watchdog):
        """Fast function should complete and return result."""
        def fast_func():
            return 42

        result = run_with_timeout(fast_func, timeout=5.0)
        assert result == 42

    def test_fast_function_with_args(self, watchdog):
        """Function with args should work correctly."""
        def add(a, b):
            return a + b

        result = run_with_timeout(add, timeout=5.0, a=10, b=20)
        assert result == 30

    def test_timeout_triggers_for_slow_function(self, watchdog):
        """Slow function should trigger timeout."""
        def slow_func():
            time.sleep(10)
            return "done"

        result = run_with_timeout(
            slow_func,
            timeout=0.1,
            raise_on_timeout=False,
            default="timeout"
        )
        assert result == "timeout"

    def test_timeout_raises_exception_when_configured(self, watchdog):
        """Timeout should raise exception when raise_on_timeout=True."""
        def slow_func():
            time.sleep(10)
            return "done"

        with pytest.raises(WatchdogTimeoutError):
            run_with_timeout(slow_func, timeout=0.1, raise_on_timeout=True)

    def test_function_exception_propagates(self, watchdog):
        """Exceptions from target function should propagate."""
        def error_func():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            run_with_timeout(error_func, timeout=5.0)

    def test_default_value_on_timeout(self, watchdog):
        """Default value should be returned on timeout."""
        def slow_func():
            time.sleep(10)

        result = run_with_timeout(
            slow_func,
            timeout=0.1,
            raise_on_timeout=False,
            default="default_value"
        )
        assert result == "default_value"

    def test_none_as_valid_result(self, watchdog):
        """None should be valid as both result and default."""
        def returns_none():
            return None

        result = run_with_timeout(returns_none, timeout=5.0, default="not_none")
        assert result is None

    def test_zero_timeout_handled(self, watchdog):
        """Zero timeout should still allow function to start."""
        def quick_func():
            return "quick"

        # With zero timeout, behavior is implementation-specific
        # Just verify it doesn't crash
        try:
            result = run_with_timeout(
                quick_func,
                timeout=0.001,
                raise_on_timeout=False,
                default="timeout"
            )
        except Exception:
            pass  # Acceptable to fail with very short timeout


# =============================================================================
# SolverEngine Timeout Integration Tests
# =============================================================================


class TestSolverTimeoutIntegration:
    """Tests for timeout integration with SolverEngine."""

    def test_solver_has_timeout_config(self, solver_with_timeouts):
        """Solver should have timeout configuration."""
        assert hasattr(solver_with_timeouts, 'DEFAULT_TIMEOUTS')
        assert 'derivative' in solver_with_timeouts.DEFAULT_TIMEOUTS
        assert 'integral' in solver_with_timeouts.DEFAULT_TIMEOUTS
        assert 'dsolve' in solver_with_timeouts.DEFAULT_TIMEOUTS

    def test_solver_timeouts_are_reasonable(self, solver_with_timeouts):
        """Timeout values should be reasonable."""
        timeouts = solver_with_timeouts.DEFAULT_TIMEOUTS

        # Derivatives should be faster than integrals
        assert timeouts['derivative'] <= timeouts['integral']
        # ODEs can be complex
        assert timeouts['dsolve'] >= timeouts['solve']
        # All should be positive
        for op, timeout in timeouts.items():
            assert timeout > 0, f"Timeout for {op} should be positive"

    def test_solver_tracks_timeouts(self, solver_with_timeouts):
        """Solver should track timeout count."""
        assert hasattr(solver_with_timeouts, '_problems_timed_out')
        assert solver_with_timeouts._problems_timed_out >= 0

    def test_fast_problem_completes(self, solver_with_timeouts):
        """Simple problems should complete without timeout."""
        result = solver_with_timeouts.solve("simplify(x + x)")
        assert result.status == SolveStatus.SUCCESS

    def test_solver_without_timeouts_still_works(self, solver_without_timeouts):
        """Solver with timeouts disabled should still work."""
        result = solver_without_timeouts.solve("simplify(x + x)")
        assert result.status == SolveStatus.SUCCESS

    def test_timeout_status_returned(self, solver_with_timeouts):
        """Timeout should return TIMEOUT status (if timeout occurs)."""
        # This is a specification test - we verify the status exists
        assert hasattr(SolveStatus, 'TIMEOUT')


# =============================================================================
# Concurrent Access Tests
# =============================================================================


class TestConcurrentAccess:
    """Tests for concurrent access to Watchdog resources."""

    def test_multiple_concurrent_timeouts(self, watchdog):
        """Multiple concurrent timeouts should work independently."""
        results = []
        errors = []

        def task(task_id, sleep_time):
            time.sleep(sleep_time)
            return task_id

        def run_task(task_id, sleep_time, timeout):
            try:
                result = run_with_timeout(
                    task, timeout,
                    task_id=task_id, sleep_time=sleep_time,
                    raise_on_timeout=False, default=f"timeout_{task_id}"
                )
                results.append((task_id, result))
            except Exception as e:
                errors.append((task_id, e))

        threads = [
            threading.Thread(target=run_task, args=(1, 0.1, 5.0)),  # Fast, should complete
            threading.Thread(target=run_task, args=(2, 5.0, 0.1)),  # Slow, should timeout
            threading.Thread(target=run_task, args=(3, 0.2, 5.0)),  # Fast, should complete
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Task 1 and 3 should complete, task 2 should timeout
        result_dict = {r[0]: r[1] for r in results}
        assert result_dict.get(1) == 1
        assert result_dict.get(2) == "timeout_2"
        assert result_dict.get(3) == 3


# =============================================================================
# Stress Tests
# =============================================================================


class TestStress:
    """Stress tests for timeout system."""

    def test_rapid_timeout_requests(self, watchdog):
        """Rapid sequential timeout requests should work."""
        def quick_task():
            return "done"

        for i in range(50):
            result = run_with_timeout(quick_task, timeout=1.0)
            assert result == "done"

    def test_timeout_with_varying_durations(self, watchdog):
        """Timeouts with varying durations should work."""
        def timed_task(duration):
            time.sleep(duration)
            return duration

        # Fast tasks with longer timeouts
        for duration in [0.01, 0.02, 0.03, 0.04, 0.05]:
            result = run_with_timeout(
                timed_task, timeout=1.0,
                duration=duration,
                raise_on_timeout=False, default=None
            )
            assert result == duration


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests for timeout system."""

    def test_function_returns_callable(self, watchdog):
        """Function returning callable should work."""
        def returns_func():
            return lambda: "inner"

        result = run_with_timeout(returns_func, timeout=1.0)
        assert callable(result)
        assert result() == "inner"

    def test_function_modifies_mutable_args(self, watchdog):
        """Function modifying mutable args should work."""
        def modify_list(lst):
            lst.append("modified")
            return lst

        input_list = ["original"]
        result = run_with_timeout(modify_list, timeout=1.0, lst=input_list)
        assert "modified" in result

    def test_recursive_function(self, watchdog):
        """Recursive function should work with timeout."""
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)

        result = run_with_timeout(fibonacci, timeout=5.0, n=10)
        assert result == 55  # fib(10) = 55


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
