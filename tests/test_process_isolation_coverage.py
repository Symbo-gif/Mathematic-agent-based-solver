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
Tests for Process Isolation Module
===================================

Comprehensive tests for sandboxed execution infrastructure.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


class TestIsolationResult:
    """Tests for IsolationResult dataclass."""

    def test_default_values(self):
        """Test default initialization."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolationResult
        )
        result = IsolationResult(success=True, result="42")
        assert result.success is True
        assert result.result == "42"
        assert result.error is None
        assert result.execution_time == 0.0
        assert result.timed_out is False
        assert result.memory_exceeded is False

    def test_error_result(self):
        """Test error result."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolationResult
        )
        result = IsolationResult(
            success=False,
            result=None,
            error="Division by zero",
            execution_time=0.5
        )
        assert result.success is False
        assert result.error == "Division by zero"

    def test_timeout_result(self):
        """Test timeout result."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolationResult
        )
        result = IsolationResult(
            success=False,
            result=None,
            error="Execution timed out",
            timed_out=True,
            execution_time=5.0
        )
        assert result.timed_out is True

    def test_memory_exceeded_result(self):
        """Test memory exceeded result."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolationResult
        )
        result = IsolationResult(
            success=False,
            result=None,
            error="Memory limit exceeded",
            memory_exceeded=True
        )
        assert result.memory_exceeded is True


class TestIsolationErrors:
    """Tests for isolation error classes."""

    def test_isolation_error(self):
        """Test IsolationError exception."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolationError
        )
        with pytest.raises(IsolationError):
            raise IsolationError("Test error")

    def test_isolation_timeout_error(self):
        """Test IsolationTimeoutError exception."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolationTimeoutError
        )
        with pytest.raises(IsolationTimeoutError):
            raise IsolationTimeoutError("Timeout!")

    def test_isolation_memory_error(self):
        """Test IsolationMemoryError exception."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolationMemoryError
        )
        with pytest.raises(IsolationMemoryError):
            raise IsolationMemoryError("Memory exceeded!")

    def test_error_inheritance(self):
        """Test error class inheritance."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolationError, IsolationTimeoutError, IsolationMemoryError
        )
        assert issubclass(IsolationTimeoutError, IsolationError)
        assert issubclass(IsolationMemoryError, IsolationError)


class TestIsolatedExecutor:
    """Tests for IsolatedExecutor class."""

    def test_init_default(self):
        """Test default initialization."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor()
        assert executor.timeout == 5.0
        assert executor.max_memory_mb == 100
        assert executor._worker_file is None

    def test_init_custom_timeout(self):
        """Test custom timeout."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(timeout=10.0)
        assert executor.timeout == 10.0

    def test_init_custom_memory(self):
        """Test custom memory limit."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(max_memory_mb=200)
        assert executor.max_memory_mb == 200

    def test_init_custom_python_path(self):
        """Test custom Python path."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(python_path="/usr/bin/python3")
        assert executor.python_path == "/usr/bin/python3"

    def test_get_worker_script_creates_file(self):
        """Test worker script creation."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor()
        try:
            path = executor._get_worker_script()
            assert path is not None
            assert os.path.exists(path)
            assert path.endswith('.py')
        finally:
            executor.cleanup()

    def test_execute_simple_expression(self):
        """Test executing a simple expression."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(timeout=10.0)
        try:
            result = executor.execute("2 + 2")
            assert result.success is True
            assert result.result == "4"
        finally:
            executor.cleanup()

    def test_execute_math_function(self):
        """Test executing math functions."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(timeout=10.0)
        try:
            result = executor.execute("sqrt(16)")
            assert result.success is True
            assert float(result.result) == 4.0
        finally:
            executor.cleanup()

    def test_execute_expression_too_long(self):
        """Test rejecting expressions that are too long."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor()
        long_expr = "x" * 20000
        result = executor.execute(long_expr)
        assert result.success is False
        assert "too long" in result.error

    def test_execute_syntax_error(self):
        """Test handling syntax errors."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(timeout=10.0)
        try:
            # Use an actual syntax error
            result = executor.execute("2 + (")
            assert result.success is False
        finally:
            executor.cleanup()

    def test_execute_blocked_import(self):
        """Test blocking dangerous imports."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(timeout=10.0)
        try:
            result = executor.execute("__import__('os').system('ls')")
            assert result.success is False
        finally:
            executor.cleanup()

    def test_cleanup(self):
        """Test cleanup removes worker file."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor()
        path = executor._get_worker_script()
        assert os.path.exists(path)
        executor.cleanup()
        assert not os.path.exists(path)

    def test_cleanup_no_file(self):
        """Test cleanup when no file exists."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor()
        # Should not raise
        executor.cleanup()


class TestIsolatedExecutorEdgeCases:
    """Edge case tests for IsolatedExecutor."""

    def test_execute_pi_constant(self):
        """Test using pi constant."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(timeout=10.0)
        try:
            result = executor.execute("pi")
            assert result.success is True
            assert abs(float(result.result) - 3.14159265359) < 0.0001
        finally:
            executor.cleanup()

    def test_execute_e_constant(self):
        """Test using e constant."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(timeout=10.0)
        try:
            result = executor.execute("e")
            assert result.success is True
            assert abs(float(result.result) - 2.71828) < 0.001
        finally:
            executor.cleanup()

    def test_execute_trigonometric(self):
        """Test trigonometric functions."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(timeout=10.0)
        try:
            result = executor.execute("sin(0)")
            assert result.success is True
            assert abs(float(result.result)) < 0.0001
        finally:
            executor.cleanup()

    def test_execute_floor_ceil(self):
        """Test floor and ceil functions."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            IsolatedExecutor
        )
        executor = IsolatedExecutor(timeout=10.0)
        try:
            result = executor.execute("floor(3.7)")
            assert result.success is True
            assert result.result == "3"

            result = executor.execute("ceil(3.2)")
            assert result.success is True
            assert result.result == "4"
        finally:
            executor.cleanup()


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_module_imports(self):
        """Test module imports correctly."""
        from symbo_agentic_reasoners.infrastructure.hardening import process_isolation
        assert process_isolation is not None

    def test_worker_script_exists(self):
        """Test _WORKER_SCRIPT constant exists."""
        from symbo_agentic_reasoners.infrastructure.hardening.process_isolation import (
            _WORKER_SCRIPT
        )
        assert _WORKER_SCRIPT is not None
        assert len(_WORKER_SCRIPT) > 0
        assert "blocked_modules" in _WORKER_SCRIPT


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
