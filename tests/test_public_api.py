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
Tests for Public API
=====================

Tests for the production-ready public API including:
- SolverConfig configuration
- SolveResult structured results
- solve_expression function
- solve_file function
- solve_batch function
- Timeout handling
- Error handling
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

from symbo_agentic_reasoners.api import (
    SolverConfig,
    SolveResult,
    solve_expression,
    solve_file,
    solve_batch,
    setup_logging,
)


class TestSolverConfig:
    """Tests for SolverConfig."""

    def test_default_values(self):
        """Config should have sensible defaults."""
        config = SolverConfig()

        assert config.timeout_sec == 60.0
        assert config.max_steps == 1000
        assert config.max_recursion_depth == 50
        assert config.max_parallel_problems == 4
        assert config.log_level == "INFO"
        assert config.log_format == "pretty"
        assert config.enable_timeouts is True
        assert config.strict_mode is False

    def test_custom_values(self):
        """Config should accept custom values."""
        config = SolverConfig(
            timeout_sec=30.0,
            max_steps=500,
            log_level="DEBUG",
        )

        assert config.timeout_sec == 30.0
        assert config.max_steps == 500
        assert config.log_level == "DEBUG"

    def test_validation_rejects_invalid_timeout(self):
        """Config should reject invalid timeout."""
        with pytest.raises(ValueError, match="timeout_sec must be positive"):
            SolverConfig(timeout_sec=-1)

    def test_validation_rejects_invalid_max_steps(self):
        """Config should reject invalid max_steps."""
        with pytest.raises(ValueError, match="max_steps must be positive"):
            SolverConfig(max_steps=0)

    def test_validation_rejects_invalid_log_level(self):
        """Config should reject invalid log_level."""
        with pytest.raises(ValueError, match="Invalid log_level"):
            SolverConfig(log_level="INVALID")

    def test_to_dict(self):
        """Config should convert to dictionary."""
        config = SolverConfig(timeout_sec=45.0)
        data = config.to_dict()

        assert data["timeout_sec"] == 45.0
        assert "max_steps" in data
        assert "log_level" in data

    def test_from_env(self):
        """Config should load from environment variables."""
        os.environ["MATH_SOLVER_TIMEOUT_SEC"] = "120.0"
        os.environ["MATH_SOLVER_MAX_STEPS"] = "2000"

        try:
            config = SolverConfig.from_env()
            assert config.timeout_sec == 120.0
            assert config.max_steps == 2000
        finally:
            del os.environ["MATH_SOLVER_TIMEOUT_SEC"]
            del os.environ["MATH_SOLVER_MAX_STEPS"]

    def test_from_file_json(self):
        """Config should load from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"solver": {"timeout_sec": 90.0, "max_steps": 1500}}, f)
            config_file = f.name

        try:
            config = SolverConfig.from_file(config_file)
            assert config.timeout_sec == 90.0
            assert config.max_steps == 1500
        finally:
            os.unlink(config_file)

    def test_from_file_missing(self):
        """Config should use defaults for missing file."""
        config = SolverConfig.from_file("/nonexistent/config.json")
        assert config.timeout_sec == 60.0  # Default


class TestSolveResult:
    """Tests for SolveResult."""

    def test_success_result(self):
        """SolveResult.success should create success result."""
        result = SolveResult.success(solution="4", problem="2+2", solve_time_ms=5.0)

        assert result.status == "ok"
        assert result.solution == "4"
        assert result.problem == "2+2"
        assert result.is_success is True
        assert result.is_error is False

    def test_failure_result(self):
        """SolveResult.failure should create failure result."""
        result = SolveResult.failure(error="Parse error", problem="invalid")

        assert result.status == "error"
        assert result.error == "Parse error"
        assert result.is_error is True
        assert result.is_success is False

    def test_timeout_result(self):
        """SolveResult.timeout should create timeout result."""
        result = SolveResult.timeout(problem="complex", timeout_sec=60.0)

        assert result.status == "timeout"
        assert result.is_timeout is True
        assert "60.0" in result.error

    def test_to_dict(self):
        """SolveResult should convert to dictionary."""
        result = SolveResult.success(solution="4", problem="2+2")
        data = result.to_dict()

        assert data["status"] == "ok"
        assert data["solution"] == "4"
        assert data["problem"] == "2+2"

    def test_to_json(self):
        """SolveResult should convert to JSON."""
        result = SolveResult.success(solution="4")
        json_str = result.to_json()

        assert '"status": "ok"' in json_str
        assert '"solution": "4"' in json_str


class TestSolveExpression:
    """Tests for solve_expression function."""

    def test_solve_arithmetic(self):
        """Should solve basic arithmetic."""
        result = solve_expression("2 + 2")

        assert result.status == "ok"
        assert "4" in result.solution

    def test_solve_algebra(self):
        """Should handle algebraic expressions."""
        result = solve_expression("x**2")

        assert result.status == "ok"

    def test_solve_with_config(self):
        """Should accept custom config."""
        config = SolverConfig(timeout_sec=30.0)
        result = solve_expression("3 * 3", config)

        assert result.status == "ok"
        assert "9" in result.solution

    def test_returns_structured_result(self):
        """Should return SolveResult type."""
        result = solve_expression("1 + 1")

        assert isinstance(result, SolveResult)
        assert hasattr(result, 'status')
        assert hasattr(result, 'solution')
        assert hasattr(result, 'error')

    def test_handles_invalid_expression(self):
        """Should handle invalid expressions gracefully."""
        result = solve_expression("")

        # Should not crash - returns either error or empty result
        assert isinstance(result, SolveResult)


class TestSolveFile:
    """Tests for solve_file function."""

    def test_solve_txt_file(self):
        """Should solve problems from text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("1+1\n2+2\n3+3\n")
            file_path = f.name

        try:
            results = solve_file(file_path)
            assert len(results) == 3
            assert all(isinstance(r, SolveResult) for r in results)
        finally:
            os.unlink(file_path)

    def test_solve_json_file(self):
        """Should solve problems from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(["4+4", "5+5"], f)
            file_path = f.name

        try:
            results = solve_file(file_path)
            assert len(results) == 2
        finally:
            os.unlink(file_path)

    def test_missing_file_returns_error(self):
        """Should return error for missing file."""
        results = solve_file("/nonexistent/file.txt")

        assert len(results) == 1
        assert results[0].status == "error"
        assert "not found" in results[0].error.lower()

    def test_ignores_comments(self):
        """Should ignore comment lines in text files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# This is a comment\n1+1\n# Another comment\n2+2\n")
            file_path = f.name

        try:
            results = solve_file(file_path)
            assert len(results) == 2  # Only non-comment lines
        finally:
            os.unlink(file_path)


class TestSolveBatch:
    """Tests for solve_batch function."""

    def test_solve_multiple_problems(self):
        """Should solve multiple problems."""
        problems = ["1+1", "2+2", "3+3"]
        results = solve_batch(problems)

        assert len(results) == 3
        assert all(isinstance(r, SolveResult) for r in results)

    def test_empty_list(self):
        """Should handle empty problem list."""
        results = solve_batch([])
        assert results == []

    def test_preserves_order(self):
        """Should return results in same order as input."""
        problems = ["10-5", "20-10", "30-15"]
        results = solve_batch(problems)

        assert len(results) == len(problems)
        # Each result should have the corresponding problem
        for i, (problem, result) in enumerate(zip(problems, results)):
            # The problem is stored in the result
            assert result.problem == problem or result.problem is None

    def test_with_custom_config(self):
        """Should use custom config for all problems."""
        config = SolverConfig(timeout_sec=10.0, max_parallel_problems=2)
        problems = ["1+1", "2+2"]
        results = solve_batch(problems, config)

        assert len(results) == 2


class TestLogging:
    """Tests for logging setup."""

    def test_setup_logging_does_not_crash(self):
        """setup_logging should not crash."""
        # Should not raise
        setup_logging(level="WARNING", log_format="pretty")

    def test_setup_logging_json_format(self):
        """setup_logging should support JSON format."""
        # Should not raise
        setup_logging(level="INFO", log_format="json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
