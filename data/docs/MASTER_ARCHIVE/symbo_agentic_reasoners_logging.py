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
import uuid
from datetime import datetime
from typing import Optional
from contextvars import ContextVar

# Context variable for correlation ID (thread-safe)
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')


class CorrelationFilter(logging.Filter):
    """Adds correlation ID to log records"""

    def filter(self, record):
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
        if self.json_format:
            import json
            log_dict = {
                'timestamp': datetime.utcnow().isoformat(),
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

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
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
            backupCount=backup_count
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


# Initialize default logging on import
_default_logger = setup_logging(level=logging.INFO)


# Convenience functions for quick logging
def log_error(logger: logging.Logger, message: str, exc: Exception = None, **kwargs):
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
