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
WATCHDOG TIMEOUT SYSTEM
=======================

Provides timeout enforcement for operations to prevent hung processes
from starving system resources.

FEATURES:
---------
1. Operation timeouts with configurable defaults
2. Heartbeat monitoring for long-running tasks
3. Automatic termination of stalled operations
4. Integration with AMS emergency system

USAGE:
------
    from symbo_agentic_reasoners.infrastructure.watchdog import (
        Watchdog, with_timeout, TimeoutError
    )

    # Decorator usage
    @with_timeout(30)  # 30 second timeout
    def my_operation():
        ...

    # Context manager usage
    with Watchdog.timeout_context(60):  # 60 second timeout
        long_running_operation()

    # Manual usage
    watchdog = Watchdog()
    task_id = watchdog.start_task("my_task", timeout=30)
    try:
        do_work()
        watchdog.heartbeat(task_id)  # Keep alive
        do_more_work()
    finally:
        watchdog.complete_task(task_id)
"""

import threading
import time
import logging
import functools
import signal
import ctypes
import sys
from typing import Dict, Optional, Callable, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import traceback
import json
from pathlib import Path

logger = logging.getLogger('symbo_agentic_reasoners.watchdog')

# Import centralized configuration
try:
    from symbo_agentic_reasoners.config import get_config
    _config = get_config()
    _USE_CONFIG = True
except ImportError:
    _USE_CONFIG = False
    logger.debug("Watchdog: Config module not available, using defaults")


class TaskStatus(Enum):
    """Status of a watched task"""
    RUNNING = "running"
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TimeoutError(Exception):
    """Raised when an operation exceeds its timeout"""
    def __init__(self, task_id: str, timeout: float, elapsed: float):
        """Initialize TimeoutError with task details.

        Args:
            task_id: Identifier of timed-out task
            timeout: Timeout limit in seconds
            elapsed: Actual elapsed time in seconds
        """
        self.task_id = task_id
        self.timeout = timeout
        self.elapsed = elapsed
        super().__init__(f"Task '{task_id}' timed out after {elapsed:.1f}s (limit: {timeout}s)")


class InterruptibleThread(threading.Thread):
    """
    A thread that can be interrupted/terminated.

    Uses ctypes to raise an exception in the target thread, forcing it to stop.
    This is a last-resort mechanism - cooperative cancellation is preferred.
    """

    def __init__(self, *args, **kwargs):
        """Initialize interruptible thread.

        Args:
            *args: Thread positional arguments
            **kwargs: Thread keyword arguments (target, name, etc.)

        Notes:
            - Captures result or exception from target function
            - Can be forcefully interrupted via interrupt() method
            - Used for hard timeout enforcement
        """
        super().__init__(*args, **kwargs)
        self._result = None
        self._exception = None
        self._interrupted = threading.Event()

    def run(self):
        """Run the thread target and capture result/exception."""
        try:
            if self._target:
                self._result = self._target(*self._args, **self._kwargs)
        except SystemExit:
            # Thread was interrupted
            self._exception = TimeoutError("thread", 0, 0)
        except Exception as e:
            self._exception = e

    def get_result(self):
        """Get the result or raise the exception."""
        if self._exception:
            raise self._exception
        return self._result

    def interrupt(self) -> bool:
        """
        Attempt to interrupt this thread.

        Returns True if interruption was attempted, False if not possible.
        Note: This is a forceful interruption and may leave resources in bad state.
        """
        self._interrupted.set()

        if not self.is_alive():
            return False

        # Try to raise SystemExit in the thread
        try:
            thread_id = self.ident
            if thread_id is None:
                return False

            # Use ctypes to raise exception in thread (works on CPython)
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_ulong(thread_id),
                ctypes.py_object(SystemExit)
            )

            if res == 0:
                logger.warning(f"Thread {thread_id} not found")
                return False
            elif res > 1:
                # Reset if more than one thread affected (shouldn't happen)
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_ulong(thread_id),
                    None
                )
                logger.error(f"Thread interruption affected multiple threads")
                return False

            logger.debug(f"Interrupted thread {thread_id}")
            return True

        except (AttributeError, TypeError) as e:
            # ctypes approach not available (e.g., non-CPython)
            logger.warning(f"Thread interruption not supported: {e}")
            return False

    @property
    def was_interrupted(self) -> bool:
        """Check if thread was interrupted."""
        return self._interrupted.is_set()


@dataclass
class WatchedTask:
    """A task being monitored by the watchdog"""
    task_id: str
    timeout_seconds: float
    started_at: datetime
    last_heartbeat: datetime
    status: TaskStatus = TaskStatus.RUNNING
    description: str = ""
    agent_id: Optional[str] = None
    thread_id: Optional[int] = None
    thread_ref: Optional['InterruptibleThread'] = None  # Reference to actual thread for interruption
    callback_on_timeout: Optional[Callable] = None
    interruptible: bool = False  # Whether to attempt thread interruption on timeout
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def elapsed_seconds(self) -> float:
        """Seconds since task started"""
        return (datetime.now() - self.started_at).total_seconds()

    @property
    def seconds_since_heartbeat(self) -> float:
        """Seconds since last heartbeat"""
        return (datetime.now() - self.last_heartbeat).total_seconds()

    @property
    def remaining_seconds(self) -> float:
        """Seconds remaining before timeout"""
        return max(0, self.timeout_seconds - self.elapsed_seconds)

    @property
    def is_expired(self) -> bool:
        """Check if task has exceeded its timeout"""
        return self.elapsed_seconds > self.timeout_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert task tracker to dictionary for serialization.

        Returns:
            Dict with task_id, timeout, elapsed, remaining, status, agent_id, description
        """
        return {
            "task_id": self.task_id,
            "timeout": self.timeout_seconds,
            "elapsed": round(self.elapsed_seconds, 2),
            "remaining": round(self.remaining_seconds, 2),
            "status": self.status.value,
            "agent_id": self.agent_id,
            "description": self.description
        }


class Watchdog:
    """
    Watchdog timer system for monitoring operation timeouts

    Provides:
    - Task registration with timeout limits
    - Background monitoring thread
    - Heartbeat mechanism for long tasks
    - Automatic timeout handling
    - Integration hooks for AMS
    """

    # Default timeouts by operation type (seconds)
    # These can be overridden via configuration
    @staticmethod
    def _get_default_timeouts() -> Dict[str, float]:
        """Get timeout defaults from config or use hardcoded fallbacks."""
        if _USE_CONFIG:
            return {
                "default": _config.timeouts.default,
                "llm_inference": _config.timeouts.llm_inference,
                "symbolic_solve": _config.timeouts.symbolic_solve,
                "integration": _config.timeouts.integration,
                "proof": _config.timeouts.proof,
                "search": _config.timeouts.search,
                "message": _config.timeouts.message,
                "differentiation": _config.timeouts.differentiation,
                "series_expansion": _config.timeouts.series_expansion,
                "matrix_operations": _config.timeouts.matrix_operations,
            }
        return {
            "default": 60,
            "llm_inference": 120,
            "symbolic_solve": 90,
            "integration": 180,
            "proof": 300,
            "search": 30,
            "message": 10,
        }

    DEFAULT_TIMEOUTS = {
        "default": 60,           # General operations
        "llm_inference": 120,    # LLM calls (can be slow)
        "symbolic_solve": 90,    # SymPy operations
        "integration": 180,      # Complex integrals
        "proof": 300,            # Proof attempts
        "search": 30,            # Directory/service lookups
        "message": 10,           # Message routing
    }

    _instance: Optional['Watchdog'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern for global watchdog instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, check_interval: float = 1.0, log_dir: Optional[str] = None):
        """
        Initialize Watchdog

        Args:
            check_interval: How often to check for timeouts (seconds)
            log_dir: Directory for timeout logs
        """
        # Avoid re-initialization on subsequent calls
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._tasks: Dict[str, WatchedTask] = {}
        self._task_lock = threading.RLock()
        self._check_interval = check_interval
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None

        # Timeout callbacks (e.g., AMS emergency handler)
        self._timeout_callbacks: List[Callable[[WatchedTask], None]] = []

        # Logging
        self._log_dir = Path(log_dir) if log_dir else Path("data/traces/error")
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self._log_dir / f"watchdog_{datetime.now().strftime('%Y%m%d')}.jsonl"

        # Statistics
        self._tasks_started = 0
        self._tasks_completed = 0
        self._tasks_timed_out = 0
        self._tasks_failed = 0

        self._initialized = True
        logger.info("Watchdog initialized")

    def start(self):
        """Start the watchdog monitoring thread"""
        with self._task_lock:
            if not self._running:
                self._running = True
                self._monitor_thread = threading.Thread(
                    target=self._monitor_loop,
                    daemon=True,
                    name="Watchdog-Monitor"
                )
                self._monitor_thread.start()
                logger.info("Watchdog monitoring started")

    def stop(self):
        """Stop the watchdog monitoring thread"""
        with self._task_lock:
            self._running = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=2.0)
                logger.info("Watchdog monitoring stopped")

    def start_task(
        self,
        task_id: str,
        timeout: Optional[float] = None,
        operation_type: str = "default",
        description: str = "",
        agent_id: Optional[str] = None,
        callback_on_timeout: Optional[Callable] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Register a task with the watchdog

        Args:
            task_id: Unique task identifier
            timeout: Timeout in seconds (uses default if not specified)
            operation_type: Type of operation (for default timeout lookup)
            description: Human-readable description
            agent_id: Agent performing the task
            callback_on_timeout: Function to call if task times out
            metadata: Additional metadata

        Returns:
            task_id for reference
        """
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUTS.get(operation_type, self.DEFAULT_TIMEOUTS["default"])

        with self._task_lock:
            now = datetime.now()
            task = WatchedTask(
                task_id=task_id,
                timeout_seconds=timeout,
                started_at=now,
                last_heartbeat=now,
                description=description,
                agent_id=agent_id,
                thread_id=threading.get_ident(),
                callback_on_timeout=callback_on_timeout,
                metadata=metadata or {}
            )
            self._tasks[task_id] = task
            self._tasks_started += 1

        logger.debug(f"Watchdog: Started task '{task_id}' with {timeout}s timeout")
        return task_id

    def heartbeat(self, task_id: str):
        """
        Send heartbeat for a running task

        Call periodically during long operations to prevent timeout.
        """
        with self._task_lock:
            if task_id in self._tasks:
                self._tasks[task_id].last_heartbeat = datetime.now()

    def complete_task(self, task_id: str, status: TaskStatus = TaskStatus.COMPLETED):
        """
        Mark a task as completed

        Args:
            task_id: Task to complete
            status: Final status (COMPLETED or FAILED)
        """
        with self._task_lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.status = status

                if status == TaskStatus.COMPLETED:
                    self._tasks_completed += 1
                elif status == TaskStatus.FAILED:
                    self._tasks_failed += 1

                # Remove from active tracking
                del self._tasks[task_id]
                logger.debug(f"Watchdog: Task '{task_id}' {status.value} after {task.elapsed_seconds:.1f}s")

    def cancel_task(self, task_id: str):
        """Cancel a running task"""
        with self._task_lock:
            if task_id in self._tasks:
                self._tasks[task_id].status = TaskStatus.CANCELLED
                del self._tasks[task_id]

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a task"""
        with self._task_lock:
            if task_id in self._tasks:
                return self._tasks[task_id].to_dict()
        return None

    def get_active_tasks(self) -> List[Dict]:
        """Get all active tasks"""
        with self._task_lock:
            return [t.to_dict() for t in self._tasks.values()]

    def register_timeout_callback(self, callback: Callable[[WatchedTask], None]):
        """Register a callback to be notified when tasks timeout"""
        self._timeout_callbacks.append(callback)

    def _monitor_loop(self):
        """Background thread monitoring for timeouts"""
        while self._running:
            try:
                self._check_timeouts()
                time.sleep(self._check_interval)
            except Exception as e:
                logger.error(f"Watchdog monitor error: {e}")

    def _check_timeouts(self):
        """Check all tasks for timeouts"""
        expired_tasks = []

        with self._task_lock:
            for task_id, task in list(self._tasks.items()):
                if task.is_expired and task.status == TaskStatus.RUNNING:
                    expired_tasks.append(task)
                    task.status = TaskStatus.TIMED_OUT
                    self._tasks_timed_out += 1

        # Handle timeouts outside the lock
        for task in expired_tasks:
            self._handle_timeout(task)

    def _handle_timeout(self, task: WatchedTask):
        """Handle a timed-out task"""
        logger.warning(f"Watchdog: Task '{task.task_id}' TIMED OUT after {task.elapsed_seconds:.1f}s")

        # Attempt thread interruption if enabled and thread reference available
        interrupted = False
        if task.interruptible and task.thread_ref is not None:
            logger.info(f"Watchdog: Attempting to interrupt task '{task.task_id}'")
            try:
                interrupted = task.thread_ref.interrupt()
                if interrupted:
                    logger.info(f"Watchdog: Successfully interrupted task '{task.task_id}'")
                    # Give thread a moment to die
                    task.thread_ref.join(timeout=1.0)
                else:
                    logger.warning(f"Watchdog: Could not interrupt task '{task.task_id}'")
            except Exception as e:
                logger.error(f"Watchdog: Error interrupting task '{task.task_id}': {e}")

        # Log to file
        self._log_timeout(task, interrupted=interrupted)

        # Call task-specific callback
        if task.callback_on_timeout:
            try:
                task.callback_on_timeout(task)
            except Exception as e:
                logger.error(f"Timeout callback error for {task.task_id}: {e}")

        # Notify global callbacks
        for callback in self._timeout_callbacks:
            try:
                callback(task)
            except Exception as e:
                logger.error(f"Global timeout callback error: {e}")

        # Remove from active tasks
        with self._task_lock:
            if task.task_id in self._tasks:
                del self._tasks[task.task_id]

    def _log_timeout(self, task: WatchedTask, interrupted: bool = False):
        """Log timeout event to file"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "timeout",
            "task_id": task.task_id,
            "timeout_seconds": task.timeout_seconds,
            "elapsed_seconds": round(task.elapsed_seconds, 2),
            "agent_id": task.agent_id,
            "description": task.description,
            "thread_id": task.thread_id,
            "interruptible": task.interruptible,
            "interrupted": interrupted,
            "metadata": task.metadata
        }
        try:
            with open(self._log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Could not write timeout log: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get watchdog statistics"""
        with self._task_lock:
            active_count = len(self._tasks)
            oldest_task = None
            if self._tasks:
                oldest = min(self._tasks.values(), key=lambda t: t.started_at)
                oldest_task = {
                    "task_id": oldest.task_id,
                    "elapsed": round(oldest.elapsed_seconds, 2),
                    "remaining": round(oldest.remaining_seconds, 2)
                }

        return {
            "running": self._running,
            "active_tasks": active_count,
            "tasks_started": self._tasks_started,
            "tasks_completed": self._tasks_completed,
            "tasks_timed_out": self._tasks_timed_out,
            "tasks_failed": self._tasks_failed,
            "timeout_rate": round(
                self._tasks_timed_out / max(1, self._tasks_started) * 100, 1
            ),
            "oldest_active_task": oldest_task
        }

    @contextmanager
    def timeout_context(self, timeout: float, task_id: Optional[str] = None,
                       operation_type: str = "default", **kwargs):
        """
        Context manager for timeout-protected operations

        Usage:
            with watchdog.timeout_context(30, "my_operation"):
                do_something()

        Args:
            timeout: Timeout in seconds
            task_id: Task identifier (auto-generated if not provided)
            operation_type: Type of operation
            **kwargs: Additional arguments for start_task
        """
        if task_id is None:
            task_id = f"task_{threading.get_ident()}_{time.time()}"

        self.start_task(task_id, timeout=timeout, operation_type=operation_type, **kwargs)
        try:
            yield task_id
            self.complete_task(task_id, TaskStatus.COMPLETED)
        except Exception as e:
            self.complete_task(task_id, TaskStatus.FAILED)
            raise


def with_timeout(timeout: float = None, operation_type: str = "default"):
    """
    Decorator for adding timeout to functions

    Usage:
        @with_timeout(30)
        def my_function():
            ...

        @with_timeout(operation_type="llm_inference")
        def call_llm():
            ...
    """
    def decorator(func: Callable) -> Callable:
        """Decorator factory for timeout enforcement.

        Args:
            func: Function to wrap with timeout

        Returns:
            Wrapped function with automatic timeout tracking
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapped function with timeout monitoring."""
            watchdog = Watchdog()
            task_id = f"{func.__name__}_{threading.get_ident()}_{time.time()}"

            effective_timeout = timeout
            if effective_timeout is None:
                effective_timeout = watchdog.DEFAULT_TIMEOUTS.get(
                    operation_type,
                    watchdog.DEFAULT_TIMEOUTS["default"]
                )

            watchdog.start_task(
                task_id=task_id,
                timeout=effective_timeout,
                operation_type=operation_type,
                description=f"Function: {func.__name__}"
            )

            try:
                result = func(*args, **kwargs)
                watchdog.complete_task(task_id, TaskStatus.COMPLETED)
                return result
            except Exception as e:
                watchdog.complete_task(task_id, TaskStatus.FAILED)
                raise

        return wrapper
    return decorator


def run_with_timeout(
    func: Callable,
    timeout: float,
    *args,
    default: Any = None,
    raise_on_timeout: bool = True,
    **kwargs
) -> Any:
    """
    Run a function with a hard timeout that actually interrupts execution.

    This function runs the target in a separate thread and forcefully interrupts
    it if the timeout is exceeded. This is more reliable than the decorator
    approach for CPU-bound operations.

    Args:
        func: Function to execute
        timeout: Maximum execution time in seconds
        *args: Positional arguments for func
        default: Value to return on timeout (if raise_on_timeout=False)
        raise_on_timeout: Whether to raise TimeoutError on timeout
        **kwargs: Keyword arguments for func

    Returns:
        Result of func, or default if timed out and raise_on_timeout=False

    Raises:
        TimeoutError: If timeout exceeded and raise_on_timeout=True
    """
    result_container = {'result': None, 'exception': None}

    def target():
        """Thread target that captures result or exception.

        Notes:
            - Executes func in separate thread
            - Stores result in result_container
            - Captures exceptions for re-raising in main thread
        """
        try:
            result_container['result'] = func(*args, **kwargs)
        except Exception as e:
            result_container['exception'] = e

    thread = InterruptibleThread(target=target)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        # Thread still running - attempt interruption
        logger.warning(f"Function {func.__name__} exceeded timeout of {timeout}s, interrupting...")
        thread.interrupt()
        thread.join(timeout=1.0)  # Give it a moment to die

        if thread.is_alive():
            logger.error(f"Could not interrupt function {func.__name__}, thread still alive")

        if raise_on_timeout:
            raise TimeoutError(func.__name__, timeout, timeout)
        return default

    # Thread completed - check for exceptions
    if result_container['exception']:
        raise result_container['exception']

    return result_container['result']


def run_with_timeout_fallback(
    func: Callable,
    timeout: float,
    fallback_func: Optional[Callable] = None,
    *args,
    **kwargs
) -> Tuple[Any, bool]:
    """
    Run a function with timeout, falling back to a simpler function if needed.

    Args:
        func: Primary function to execute
        timeout: Maximum execution time for primary function
        fallback_func: Fallback function to use on timeout (same signature)
        *args: Arguments for both functions
        **kwargs: Keyword arguments for both functions

    Returns:
        Tuple of (result, used_fallback)
    """
    try:
        result = run_with_timeout(func, timeout, *args, raise_on_timeout=True, **kwargs)
        return result, False
    except TimeoutError:
        if fallback_func is not None:
            logger.info(f"Primary function timed out, using fallback")
            try:
                result = fallback_func(*args, **kwargs)
                return result, True
            except Exception as e:
                logger.error(f"Fallback function also failed: {e}")
                raise
        raise


# =============================================================================
# PHASE 5 - ISSUE #8: RESOURCE EXHAUSTION DETECTION
# =============================================================================

class ResourceUsageTracker:
    """
    Track resource usage patterns for exhaustion detection.

    Phase 5 - Issue #8: Detects sustained high CPU, memory leaks,
    and task accumulation patterns that indicate resource attacks.

    Security Features:
    - Sustained high CPU detection (>90% for 5+ minutes)
    - Memory growth trend analysis (leak detection)
    - Task accumulation detection (possible deadlock)
    - Configurable time window (default 5 minutes)
    """

    def __init__(self, window_seconds: int = 300):
        """
        Initialize resource usage tracker.

        Args:
            window_seconds: Observation window in seconds (default 300 = 5 minutes)
        """
        self.window_seconds = window_seconds
        self._cpu_samples: List[Tuple[float, float]] = []  # (timestamp, usage)
        self._memory_samples: List[Tuple[float, int]] = []  # (timestamp, bytes)
        self._task_samples: List[Tuple[float, int]] = []  # (timestamp, count)

    def record_cpu(self, usage_percent: float):
        """Record CPU usage sample."""
        self._cpu_samples.append((time.time(), usage_percent))
        self._cleanup_old_samples()

    def record_memory(self, usage_bytes: int):
        """Record memory usage sample."""
        self._memory_samples.append((time.time(), usage_bytes))
        self._cleanup_old_samples()

    def record_task_count(self, count: int):
        """Record active task count."""
        self._task_samples.append((time.time(), count))
        self._cleanup_old_samples()

    def detect_exhaustion(self) -> Optional[str]:
        """
        Detect resource exhaustion patterns.

        Returns:
            Alert message if exhaustion detected, None otherwise
        """
        # Check sustained high CPU (>90% for 5+ minutes)
        if self._check_sustained_high_cpu():
            return "Sustained high CPU usage detected (>90% for 5+ min)"

        # Check memory growth trend
        if self._check_memory_growth():
            return "Rapid memory growth detected (possible leak)"

        # Check task accumulation
        if self._check_task_accumulation():
            return "Task accumulation detected (possible deadlock)"

        return None

    def _check_sustained_high_cpu(self) -> bool:
        """Check for sustained high CPU usage."""
        recent_samples = [
            usage for ts, usage in self._cpu_samples
            if time.time() - ts < 300  # Last 5 minutes
        ]

        if len(recent_samples) < 10:
            return False

        avg_cpu = sum(recent_samples) / len(recent_samples)
        return avg_cpu > 90.0

    def _check_memory_growth(self) -> bool:
        """Check for rapid memory growth (doubling)."""
        if len(self._memory_samples) < 10:
            return False

        current_time = time.time()

        # Compare memory from 4 minutes ago vs last minute
        old_samples = [mem for ts, mem in self._memory_samples if current_time - ts > 240]
        new_samples = [mem for ts, mem in self._memory_samples if current_time - ts < 60]

        if not old_samples or not new_samples:
            return False

        old_avg = sum(old_samples) / len(old_samples)
        new_avg = sum(new_samples) / len(new_samples)

        # Alert if memory doubled
        return new_avg > (old_avg * 2)

    def _check_task_accumulation(self) -> bool:
        """Check for task accumulation (possible deadlock)."""
        if len(self._task_samples) < 10:
            return False

        current_time = time.time()

        # Get tasks from last 5 minutes
        recent_tasks = [count for ts, count in self._task_samples if current_time - ts < 300]

        if not recent_tasks:
            return False

        # Check if task count consistently increasing
        if len(recent_tasks) >= 10:
            # Check if last 5 samples > first 5 samples
            first_half = recent_tasks[:len(recent_tasks)//2]
            second_half = recent_tasks[len(recent_tasks)//2:]

            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)

            # Alert if tasks increased by 50%+
            return avg_second > (avg_first * 1.5)

        return False

    def _cleanup_old_samples(self):
        """Remove samples outside time window."""
        cutoff = time.time() - self.window_seconds
        self._cpu_samples = [(ts, val) for ts, val in self._cpu_samples if ts > cutoff]
        self._memory_samples = [(ts, val) for ts, val in self._memory_samples if ts > cutoff]
        self._task_samples = [(ts, val) for ts, val in self._task_samples if ts > cutoff]

    def get_stats(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        self._cleanup_old_samples()
        return {
            'cpu_samples': len(self._cpu_samples),
            'memory_samples': len(self._memory_samples),
            'task_samples': len(self._task_samples),
            'window_seconds': self.window_seconds,
        }


# =============================================================================


# Global watchdog instance getter
def get_watchdog() -> Watchdog:
    """Get the global Watchdog instance"""
    return Watchdog()


if __name__ == "__main__":
    """Test watchdog functionality"""
    print("=" * 60)
    print("WATCHDOG TIMEOUT SYSTEM TEST")
    print("=" * 60)
    print()

    # Initialize watchdog
    watchdog = Watchdog(check_interval=0.5)
    watchdog.start()
    print(f"Watchdog started: {watchdog.get_statistics()}")
    print()

    # Test 1: Normal completion
    print("Test 1: Normal completion")
    task_id = watchdog.start_task("test_normal", timeout=5, description="Normal task")
    time.sleep(0.5)
    watchdog.complete_task(task_id)
    print(f"  Task completed normally")
    print()

    # Test 2: Timeout
    print("Test 2: Timeout detection")
    timeout_detected = [False]

    def on_timeout(task):
        """Callback function for timeout event (test function)."""
        timeout_detected[0] = True
        print(f"  Timeout callback fired for: {task.task_id}")

    task_id = watchdog.start_task(
        "test_timeout",
        timeout=1,
        description="Should timeout",
        callback_on_timeout=on_timeout
    )
    time.sleep(2)  # Wait for timeout
    print(f"  Timeout detected: {timeout_detected[0]}")
    print()

    # Test 3: Context manager
    print("Test 3: Context manager")
    try:
        with watchdog.timeout_context(5, "context_test"):
            print("  Inside timeout context")
            time.sleep(0.5)
        print("  Context completed successfully")
    except Exception as e:
        print(f"  Context failed: {e}")
    print()

    # Test 4: Decorator
    print("Test 4: Decorator")

    @with_timeout(5)
    def quick_operation():
        """Test function for timeout decorator."""
        time.sleep(0.2)
        return "done"

    result = quick_operation()
    print(f"  Decorated function returned: {result}")
    print()

    # Test 5: run_with_timeout - successful completion
    print("Test 5: run_with_timeout (success)")

    def compute_something(x, y):
        """Test function for run_with_timeout (successful completion)."""
        time.sleep(0.1)
        return x + y

    result = run_with_timeout(compute_something, 5.0, 10, 20)
    print(f"  Result: {result}")
    print()

    # Test 6: run_with_timeout - timeout with interruption
    print("Test 6: run_with_timeout (timeout)")

    def slow_computation():
        """Test function with long CPU-bound computation (timeout test)."""
        total = 0
        for i in range(10**8):  # Long running computation
            total += i
        return total

    try:
        result = run_with_timeout(slow_computation, 0.5)
        print(f"  Result: {result}")
    except TimeoutError as e:
        print(f"  Caught timeout: {e}")
    print()

    # Test 7: run_with_timeout with fallback
    print("Test 7: run_with_timeout_fallback")

    def expensive_solve(n):
        """Test function simulating expensive solver with timeout."""
        # Simulate expensive solver that takes too long
        time.sleep(n * 10)
        return f"expensive_result_{n}"

    def cheap_solve(n):
        """Test function simulating quick fallback solver."""
        # Quick fallback
        return f"cheap_result_{n}"

    result, used_fallback = run_with_timeout_fallback(
        expensive_solve, 0.5, cheap_solve, 5
    )
    print(f"  Result: {result}, Used fallback: {used_fallback}")
    print()

    # Test 8: run_with_timeout with default on timeout
    print("Test 8: run_with_timeout with default value")
    result = run_with_timeout(
        slow_computation, 0.5,
        default="computation_skipped",
        raise_on_timeout=False
    )
    print(f"  Result: {result}")
    print()

    # Statistics
    print("Final Statistics:")
    print(json.dumps(watchdog.get_statistics(), indent=2))

    watchdog.stop()
    print()
    print("Watchdog test complete")
