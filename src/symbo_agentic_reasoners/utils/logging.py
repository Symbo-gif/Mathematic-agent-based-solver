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
SYMBO_AGENTIC_REASONERS Centralized Logging Configuration
=======================================

Provides structured logging for all SYMBO_AGENTIC_REASONERS phases with:
- Configurable log levels
- File and console handlers
- JSON formatting option for production
- Correlation IDs for request tracing
"""

import logging
import logging.handlers
import os
import sys
import io
import uuid
from datetime import datetime, timezone
from typing import Optional
from contextvars import ContextVar


# Unicode to ASCII replacements for console output
UNICODE_REPLACEMENTS = {
    '\u222b': 'INT',      # ∫ integral symbol
    '\u221e': 'inf',      # ∞ infinity
    '\u03c0': 'pi',       # π pi
    '\u03b1': 'alpha',    # α alpha
    '\u03b2': 'beta',     # β beta
    '\u03b3': 'gamma',    # γ gamma
    '\u03b4': 'delta',    # δ delta
    '\u03bb': 'lambda',   # λ lambda
    '\u03bc': 'mu',       # μ mu
    '\u03c3': 'sigma',    # σ sigma
    '\u03c9': 'omega',    # ω omega
    '\u2192': '->',       # → arrow
    '\u2211': 'SUM',      # ∑ summation
    '\u220f': 'PROD',     # ∏ product
    '\u2202': 'd',        # ∂ partial derivative
    '\u221a': 'sqrt',     # √ square root
    '\u00b2': '^2',       # ² superscript 2
    '\u00b3': '^3',       # ³ superscript 3
    '\u2260': '!=',       # ≠ not equal
    '\u2264': '<=',       # ≤ less than or equal
    '\u2265': '>=',       # ≥ greater than or equal
    '\u00b1': '+/-',      # ± plus minus
}


def sanitize_for_console(text: str) -> str:
    """
    Replace Unicode math symbols with ASCII equivalents for console safety.

    Args:
        text: Input text possibly containing Unicode math symbols

    Returns:
        ASCII-safe version of the text
    """
    result = text
    for unicode_char, ascii_replacement in UNICODE_REPLACEMENTS.items():
        result = result.replace(unicode_char, ascii_replacement)
    # Also replace any remaining non-ASCII characters with '?'
    try:
        result.encode('ascii')
    except UnicodeEncodeError:
        result = result.encode('ascii', errors='replace').decode('ascii')
    return result


class SafeStreamHandler(logging.StreamHandler):
    """StreamHandler that safely handles Unicode encoding on Windows console."""

    def emit(self, record):
        """Perform emit operation.

        Args:
        record: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.emit(...)
        """
        """Perform emit operation.

        Args:
        record: Description needed

        Returns:
        Result of the operation

        Example:
        >>> result = obj.emit(...)
        """
        try:
            msg = self.format(record)
            stream = self.stream
            # Try to write normally first
            try:
                stream.write(msg + self.terminator)
                self.flush()
            except UnicodeEncodeError:
                # Fallback to ASCII-safe version
                safe_msg = sanitize_for_console(msg)
                stream.write(safe_msg + self.terminator)
                self.flush()
        except RecursionError:
            raise
        except Exception:
            """Perform filter operation.

            Args:
            record: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.filter(...)
            """
            self.handleError(record)

# Context variable for correlation ID (thread-safe)
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')


class CorrelationFilter(logging.Filter):
    """Adds correlation ID to log records"""

    def filter(self, record):
        """Add correlation ID to log record.

        Args:
            record: LogRecord to filter

        Returns:
            bool: Always True (all records pass)
        """
        record.correlation_id = correlation_id.get() or '-'
        return True


class SYMBO_AGENTIC_REASONERSFormatter(logging.Formatter):
    """Custom formatter with optional JSON output"""

    def __init__(self, json_format: bool = False):
        self.json_format = json_format
        if json_format:
            super().__init__()
        else:
            super().__init__(
                fmt='%(asctime)s [%(levelname)-8s] %(name)-30s [%(correlation_id)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

    def format(self, record):
        """Format log record as JSON or colored text.

        Args:
            record: LogRecord to format

        Returns:
            str: Formatted log message (JSON or colored text)
        """
        if self.json_format:
            import json
            log_dict = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'correlation_id': getattr(record, 'correlation_id', '-'),
                'message': record.getMessage(),
                'module': record.module,
                'line': record.lineno
            }
            if record.exc_info:
                log_dict['exception'] = self.formatException(record.exc_info)
            return json.dumps(log_dict)
        return super().format(record)


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    json_format: bool = False,
    max_bytes: int = 10_000_000,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure SYMBO_AGENTIC_REASONERS logging system.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        json_format: Use JSON formatting (for production)
        max_bytes: Max size before log rotation
        backup_count: Number of backup files to keep

    Returns:
        Root SYMBO_AGENTIC_REASONERS logger
    """
    # Create root SYMBO_AGENTIC_REASONERS logger
    root_logger = logging.getLogger('symbo_agentic_reasoners')
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add correlation filter
    corr_filter = CorrelationFilter()

    # Console handler - use SafeStreamHandler for Unicode safety on Windows
    console_handler = SafeStreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(SYMBO_AGENTIC_REASONERSFormatter(json_format=False))
    console_handler.addFilter(corr_filter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(SYMBO_AGENTIC_REASONERSFormatter(json_format=json_format))
        file_handler.addFilter(corr_filter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (e.g., 'symbo_agentic_reasoners.phase4.conflict_resolution')

    Returns:
        Logger instance
    """
    if not name.startswith('symbo_agentic_reasoners'):
        name = f'symbo_agentic_reasoners.{name}'
    return logging.getLogger(name)


def set_correlation_id(cid: Optional[str] = None) -> str:
    """
    Set correlation ID for current context.

    Args:
        cid: Correlation ID (auto-generated if None)

    Returns:
        The correlation ID
    """
    if cid is None:
        cid = str(uuid.uuid4())[:8]
    correlation_id.set(cid)
    return cid


def get_correlation_id() -> str:
    """Get current correlation ID"""
    return correlation_id.get() or '-'


# Track initialization state
_initialized = False
_default_logger: Optional[logging.Logger] = None


def initialize_logging(
    level: Optional[int] = None,
    log_file: Optional[str] = None,
    json_format: Optional[bool] = None,
) -> logging.Logger:
    """
    Initialize logging system with configuration.

    This should be called once at application startup. If not called,
    logging will be auto-initialized on first get_logger() call.

    Args:
        level: Override log level (default: from config or INFO)
        log_file: Override log file path (default: from config)
        json_format: Override JSON format (default: from config)

    Returns:
        Root SYMBO_AGENTIC_REASONERS logger
    """
    global _initialized, _default_logger

    # Get settings from config if not overridden
    try:
        from symbo_agentic_reasoners.config import get_config
        config = get_config()

        if level is None:
            level_str = config.logging.default_level
            level = getattr(logging, level_str.upper(), logging.INFO)

        if log_file is None and config.logging.log_to_file:
            from pathlib import Path
            log_dir = Path(config.paths.logs_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = str(log_dir / "symbo_agentic_reasoners.log")

        if json_format is None:
            json_format = config.logging.use_json_format

        max_bytes = config.logging.log_file_max_bytes
        backup_count = config.logging.log_file_backup_count

    except ImportError:
        # Config not available, use defaults
        if level is None:
            level = logging.INFO
        if json_format is None:
            json_format = False
        max_bytes = 10_000_000
        backup_count = 5

    _default_logger = setup_logging(
        level=level,
        log_file=log_file,
        json_format=json_format or False,
        max_bytes=max_bytes,
        backup_count=backup_count
    )
    _initialized = True

    return _default_logger


def ensure_initialized() -> None:
    """Ensure logging is initialized."""
    global _initialized
    if not _initialized:
        initialize_logging()


# Convenience functions for quick logging
def log_error(logger: logging.Logger, message: str, exc: Optional[Exception] = None, **kwargs):
    """Log an error with optional exception details"""
    extra_info = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
    full_message = f"{message} | {extra_info}" if extra_info else message
    if exc:
        logger.error(f"{full_message} | error_type={type(exc).__name__} | error={exc}", exc_info=True)
    else:
        logger.error(full_message)


def log_warning(logger: logging.Logger, message: str, **kwargs):
    """Log a warning with context"""
    extra_info = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
    full_message = f"{message} | {extra_info}" if extra_info else message
    logger.warning(full_message)


def log_info(logger: logging.Logger, message: str, **kwargs):
    """Log an info message with context"""
    extra_info = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
    full_message = f"{message} | {extra_info}" if extra_info else message
    logger.info(full_message)


def log_debug(logger: logging.Logger, message: str, **kwargs):
    """Log a debug message with context"""
    extra_info = ' | '.join(f'{k}={v}' for k, v in kwargs.items())
    full_message = f"{message} | {extra_info}" if extra_info else message
    logger.debug(full_message)


# Module-level loggers for common components (lazy initialized)
_component_loggers: dict = {}


def get_component_logger(component: str) -> logging.Logger:
    """
    Get a logger for a specific component.

    This ensures logging is initialized and returns a cached logger.

    Args:
        component: Component name (e.g., 'ams', 'watchdog', 'orchestrator')

    Returns:
        Logger instance for the component
    """
    ensure_initialized()

    if component not in _component_loggers:
        _component_loggers[component] = get_logger(component)

    return _component_loggers[component]


# Auto-initialize on import with defaults
# (will be properly configured when initialize_logging() is called)
try:
    _default_logger = setup_logging(level=logging.INFO)
    _initialized = True
except Exception:
    pass  # Allow import even if logging setup fails
