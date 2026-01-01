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
Utils and Logging Tests
=======================

Comprehensive tests for utility modules:
- Path constants
- Logging configuration
- Correlation IDs
- Log formatting
"""

import pytest
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from symbo_agentic_reasoners.utils import (
    PROJECT_ROOT,
    SRC_ROOT,
    DATA_DIR,
    TRACE_DIR,
    OUTPUT_DIR,
)
from symbo_agentic_reasoners.utils.logging import (
    CorrelationFilter,
    SYMBO_AGENTIC_REASONERSFormatter,
    setup_logging,
    get_logger,
    set_correlation_id,
    get_correlation_id,
    log_error,
    log_warning,
    log_info,
    log_debug,
    get_component_logger,
    ensure_initialized,
)


# =============================================================================
# Path Constants Tests
# =============================================================================


class TestPathConstants:
    """Tests for path constants in utils.__init__."""

    def test_project_root_exists(self):
        """PROJECT_ROOT should be a valid Path."""
        assert isinstance(PROJECT_ROOT, Path)

    def test_src_root_is_under_project(self):
        """SRC_ROOT should be under PROJECT_ROOT."""
        assert isinstance(SRC_ROOT, Path)
        assert PROJECT_ROOT in SRC_ROOT.parents or SRC_ROOT == PROJECT_ROOT / "src"

    def test_data_dir_path(self):
        """DATA_DIR should be a Path object."""
        assert isinstance(DATA_DIR, Path)

    def test_trace_dir_is_under_data(self):
        """TRACE_DIR should be under DATA_DIR."""
        assert isinstance(TRACE_DIR, Path)
        assert DATA_DIR in TRACE_DIR.parents or TRACE_DIR == DATA_DIR / "traces"

    def test_output_dir_is_under_data(self):
        """OUTPUT_DIR should be under DATA_DIR."""
        assert isinstance(OUTPUT_DIR, Path)
        assert DATA_DIR in OUTPUT_DIR.parents or OUTPUT_DIR == DATA_DIR / "output"


# =============================================================================
# CorrelationFilter Tests
# =============================================================================


class TestCorrelationFilter:
    """Tests for CorrelationFilter."""

    def test_filter_adds_correlation_id(self):
        """Filter should add correlation_id to record."""
        filter_obj = CorrelationFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = filter_obj.filter(record)

        assert result is True
        assert hasattr(record, 'correlation_id')

    def test_filter_uses_context_correlation_id(self):
        """Filter should use correlation ID from context."""
        set_correlation_id("test-123")
        filter_obj = CorrelationFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        filter_obj.filter(record)

        assert record.correlation_id == "test-123"


# =============================================================================
# Formatter Tests
# =============================================================================


class TestSYMBO_AGENTIC_REASONERSFormatter:
    """Tests for SYMBO_AGENTIC_REASONERSFormatter."""

    def test_text_format(self):
        """Should format in text mode by default."""
        formatter = SYMBO_AGENTIC_REASONERSFormatter(json_format=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.correlation_id = "abc123"

        formatted = formatter.format(record)

        assert "Test message" in formatted
        assert "INFO" in formatted

    def test_json_format(self):
        """Should format as JSON when enabled."""
        import json

        formatter = SYMBO_AGENTIC_REASONERSFormatter(json_format=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.correlation_id = "abc123"

        formatted = formatter.format(record)

        # Should be valid JSON
        data = json.loads(formatted)
        assert data['message'] == "Test message"
        assert data['level'] == "INFO"
        assert data['correlation_id'] == "abc123"

    def test_json_format_with_exception(self):
        """Should include exception in JSON format."""
        import json

        formatter = SYMBO_AGENTIC_REASONERSFormatter(json_format=True)

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        record.correlation_id = "err123"

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert 'exception' in data
        assert 'ValueError' in data['exception']


# =============================================================================
# setup_logging Tests
# =============================================================================


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_returns_logger(self):
        """Should return a logger."""
        logger = setup_logging()

        assert isinstance(logger, logging.Logger)
        assert logger.name == 'symbo_agentic_reasoners'

    def test_setup_with_level(self):
        """Should set specified level."""
        logger = setup_logging(level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_setup_with_file(self):
        """Should create file handler when log_file specified."""
        tmpdir = tempfile.mkdtemp()
        try:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logging(log_file=log_file)

            # Log something
            logger.info("Test message")

            # Check file was created
            assert os.path.exists(log_file)

            # Clean up handlers to release file
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        finally:
            # Try to clean up (may fail on Windows)
            try:
                import shutil
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass

    def test_setup_clears_existing_handlers(self):
        """Should clear existing handlers."""
        logger = setup_logging()
        initial_handlers = len(logger.handlers)

        # Setup again
        logger = setup_logging()

        # Should have same number (not doubled)
        assert len(logger.handlers) == initial_handlers


# =============================================================================
# get_logger Tests
# =============================================================================


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Should return a logger."""
        logger = get_logger("test.module")

        assert isinstance(logger, logging.Logger)

    def test_get_logger_prefixes_name(self):
        """Should prefix name with symbo_agentic_reasoners."""
        logger = get_logger("my_module")

        assert logger.name == "symbo_agentic_reasoners.my_module"

    def test_get_logger_keeps_prefix(self):
        """Should not double-prefix."""
        logger = get_logger("symbo_agentic_reasoners.existing")

        assert logger.name == "symbo_agentic_reasoners.existing"


# =============================================================================
# Correlation ID Tests
# =============================================================================


class TestCorrelationId:
    """Tests for correlation ID functions."""

    def test_set_correlation_id_returns_id(self):
        """set_correlation_id should return the ID."""
        cid = set_correlation_id("my-id-123")

        assert cid == "my-id-123"

    def test_set_correlation_id_auto_generates(self):
        """Should auto-generate ID when None."""
        cid = set_correlation_id(None)

        assert cid is not None
        assert len(cid) == 8  # First 8 chars of UUID

    def test_get_correlation_id_returns_set_id(self):
        """get_correlation_id should return the set ID."""
        set_correlation_id("test-abc")
        cid = get_correlation_id()

        assert cid == "test-abc"

    def test_correlation_id_thread_context(self):
        """Correlation ID should be context-local."""
        set_correlation_id("ctx-123")

        assert get_correlation_id() == "ctx-123"


# =============================================================================
# Log Helper Functions Tests
# =============================================================================


class TestLogHelpers:
    """Tests for log helper functions."""

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        return Mock(spec=logging.Logger)

    def test_log_error_basic(self, mock_logger):
        """log_error should call logger.error."""
        log_error(mock_logger, "Error message")

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "Error message" in call_args

    def test_log_error_with_exception(self, mock_logger):
        """log_error should include exception info."""
        exc = ValueError("Test error")
        log_error(mock_logger, "Error occurred", exc=exc)

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "ValueError" in call_args

    def test_log_error_with_kwargs(self, mock_logger):
        """log_error should include extra kwargs."""
        log_error(mock_logger, "Error", operation="test", count=5)

        call_args = mock_logger.error.call_args[0][0]
        assert "operation=test" in call_args
        assert "count=5" in call_args

    def test_log_warning(self, mock_logger):
        """log_warning should call logger.warning."""
        log_warning(mock_logger, "Warning message", level="high")

        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args[0][0]
        assert "Warning message" in call_args
        assert "level=high" in call_args

    def test_log_info(self, mock_logger):
        """log_info should call logger.info."""
        log_info(mock_logger, "Info message", status="ok")

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "Info message" in call_args
        assert "status=ok" in call_args

    def test_log_debug(self, mock_logger):
        """log_debug should call logger.debug."""
        log_debug(mock_logger, "Debug message", detail="xyz")

        mock_logger.debug.assert_called_once()
        call_args = mock_logger.debug.call_args[0][0]
        assert "Debug message" in call_args
        assert "detail=xyz" in call_args


# =============================================================================
# Component Logger Tests
# =============================================================================


class TestGetComponentLogger:
    """Tests for get_component_logger function."""

    def test_get_component_logger_returns_logger(self):
        """Should return a logger for component."""
        logger = get_component_logger("watchdog")

        assert isinstance(logger, logging.Logger)
        assert "watchdog" in logger.name

    def test_get_component_logger_caches(self):
        """Should cache loggers."""
        logger1 = get_component_logger("test_component")
        logger2 = get_component_logger("test_component")

        assert logger1 is logger2

    def test_different_components_different_loggers(self):
        """Different components should get different loggers."""
        logger1 = get_component_logger("comp1")
        logger2 = get_component_logger("comp2")

        assert logger1 is not logger2


# =============================================================================
# Initialization Tests
# =============================================================================


class TestLoggingInitialization:
    """Tests for logging initialization."""

    def test_ensure_initialized_runs(self):
        """ensure_initialized should run without error."""
        # Just verify it doesn't raise
        ensure_initialized()


# =============================================================================
# Integration Tests
# =============================================================================


class TestLoggingIntegration:
    """Integration tests for logging system."""

    def test_full_logging_workflow(self):
        """Test complete logging workflow."""
        # Setup with correlation ID
        set_correlation_id("int-test-123")

        # Get logger
        logger = get_logger("integration.test")

        # Create handler with our formatter
        handler = logging.StreamHandler()
        formatter = SYMBO_AGENTIC_REASONERSFormatter(json_format=False)
        handler.setFormatter(formatter)
        handler.addFilter(CorrelationFilter())

        # Log should work without error
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.info("Integration test message")

    def test_json_logging_workflow(self):
        """Test JSON logging workflow."""
        import json

        set_correlation_id("json-test")

        # Create logger with JSON formatter
        logger = logging.getLogger("json.test")
        handler = logging.StreamHandler()
        formatter = SYMBO_AGENTIC_REASONERSFormatter(json_format=True)
        handler.setFormatter(formatter)
        handler.addFilter(CorrelationFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        # Should be able to log without error
        logger.info("JSON test message")


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
