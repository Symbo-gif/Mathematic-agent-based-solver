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
Logging Setup
=============

Centralized logging configuration for consistent output format.
"""

import sys
import logging
import uuid
from contextvars import ContextVar
from typing import Optional, Literal
from datetime import datetime, timezone


# Context variable for correlation IDs
_correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


def get_correlation_id() -> str:
    """Get the current correlation ID, generating one if needed."""
    cid = _correlation_id.get()
    if cid is None:
        cid = str(uuid.uuid4())[:8]
        _correlation_id.set(cid)
    return cid


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context."""
    _correlation_id.set(correlation_id)


class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        return True


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, 'correlation_id', None),
        }

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
                          'message', 'correlation_id'):
                if not key.startswith('_'):
                    log_obj[key] = value

        return json.dumps(log_obj)


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
    log_format: Literal["pretty", "json"] = "pretty",
    include_correlation_id: bool = True,
) -> None:
    """
    Initialize logging for the application.

    Call this once at the entrypoint (CLI main or HTTP server startup).

    Args:
        level: Logging level
        log_format: "pretty" for human-readable, "json" for structured logs
        include_correlation_id: Whether to include correlation IDs

    Example:
        >>> from symbo_agentic_reasoners.api import setup_logging
        >>> setup_logging(level="DEBUG", log_format="json")
    """
    # Get root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers.clear()

    # Set level
    root_logger.setLevel(getattr(logging, level))

    # Create handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(getattr(logging, level))

    # Add correlation filter if enabled
    if include_correlation_id:
        handler.addFilter(CorrelationFilter())

    # Set formatter
    if log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        if include_correlation_id:
            fmt = "%(asctime)s [%(levelname)-8s] [%(correlation_id)s] %(name)s: %(message)s"
        else:
            fmt = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S"))

    root_logger.addHandler(handler)

    # Reduce noise from some libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logging.info(f"Logging initialized: level={level}, format={log_format}")
