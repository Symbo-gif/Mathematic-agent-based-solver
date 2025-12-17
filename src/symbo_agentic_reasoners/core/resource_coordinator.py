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
Resource Coordinator - Agent Lifecycle and Resource Management
================================================================

Tier 1 agent responsible for:
- Activating/deactivating agents based on workload
- Managing parallel worker pools
- Auto-selecting partitioning strategies
- Resource-aware scheduling
- Graceful shutdown with state persistence
- Hardware monitoring (CPU, RAM, disk)

The user never manually switches strategies or manages agents.
Everything is automatic based on problem characteristics.
"""

import os
import sys
import json
import signal
import threading
import time
# SECURITY: Removed unused 'import pickle' - pickle is unsafe for untrusted data
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Hardware monitoring
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logger.warning("psutil not available - hardware monitoring disabled")

# Import centralized configuration
try:
    from symbo_agentic_reasoners.config import get_config
    _config = get_config()
    _USE_CONFIG = True
except ImportError:
    _USE_CONFIG = False
    logger.debug("ResourceCoordinator: Config module not available, using defaults")


class AgentState(Enum):
    """State of an agent in the pool."""
    INACTIVE = "inactive"      # Not loaded
    STANDBY = "standby"        # Loaded but idle
    ACTIVE = "active"          # Processing work
    SUSPENDED = "suspended"    # Paused, can resume
    FAILED = "failed"          # Error state


@dataclass
class AgentInfo:
    """Information about a managed agent."""
    agent_id: str
    agent_type: str
    tier: int
    state: AgentState = AgentState.INACTIVE
    instance: Optional[Any] = None
    last_active: Optional[datetime] = None
    tasks_completed: int = 0
    memory_estimate_mb: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'tier': self.tier,
            'state': self.state.value,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'tasks_completed': self.tasks_completed
        }


@dataclass
class HardwareMetrics:
    """Current hardware resource metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_available_mb: float = 0.0
    disk_percent: float = 0.0
    disk_free_gb: float = 0.0
    process_memory_mb: float = 0.0
    process_cpu_percent: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'cpu_percent': round(self.cpu_percent, 1),
            'memory_percent': round(self.memory_percent, 1),
            'memory_used_mb': round(self.memory_used_mb, 1),
            'memory_available_mb': round(self.memory_available_mb, 1),
            'disk_percent': round(self.disk_percent, 1),
            'disk_free_gb': round(self.disk_free_gb, 2),
            'process_memory_mb': round(self.process_memory_mb, 1),
            'process_cpu_percent': round(self.process_cpu_percent, 1),
            'timestamp': self.timestamp.isoformat()
        }


def _get_default_limits() -> Dict[str, Any]:
    """Get resource limits from config or use defaults."""
    if _USE_CONFIG:
        return {
            'max_active_agents': _config.agent_pool.max_active_agents,
            'max_parallel_workers': _config.agent_pool.max_parallel_workers,
            'max_memory_mb': _config.agent_pool.total_agent_memory_mb,
            'idle_timeout_seconds': _config.agent_pool.specialist_standby_timeout,
            'cpu_warning_threshold': _config.thresholds.cpu_warning,
            'cpu_critical_threshold': _config.thresholds.cpu_critical,
            'memory_warning_threshold': _config.thresholds.ram_warning,
            'memory_critical_threshold': _config.thresholds.ram_critical,
            'disk_warning_threshold': _config.thresholds.disk_warning,
        }
    return {
        'max_active_agents': 8,
        'max_parallel_workers': 4,
        'max_memory_mb': 4096.0,
        'idle_timeout_seconds': 300.0,
        'cpu_warning_threshold': 0.80,
        'cpu_critical_threshold': 0.95,
        'memory_warning_threshold': 0.80,
        'memory_critical_threshold': 0.95,
        'disk_warning_threshold': 0.90,
    }


@dataclass
class ResourceLimits:
    """Resource constraints for the system."""
    max_active_agents: int = 8
    max_parallel_workers: int = 4
    max_memory_mb: float = 4096.0
    idle_timeout_seconds: float = 300.0  # Deactivate after 5 min idle
    # Hardware thresholds (0.0 to 1.0)
    cpu_warning_threshold: float = 0.80
    cpu_critical_threshold: float = 0.95
    memory_warning_threshold: float = 0.80
    memory_critical_threshold: float = 0.95
    disk_warning_threshold: float = 0.90

    @classmethod
    def from_config(cls) -> 'ResourceLimits':
        """Create ResourceLimits from centralized configuration."""
        defaults = _get_default_limits()
        return cls(**defaults)


@dataclass
class SystemState:
    """Complete system state for persistence."""
    agents: Dict[str, Dict] = field(default_factory=dict)
    pending_problems: List[str] = field(default_factory=list)
    completed_count: int = 0
    failed_count: int = 0
    session_start: str = ""
    last_checkpoint: str = ""

    def to_dict(self) -> Dict:
        return {
            'agents': self.agents,
            'pending_problems': self.pending_problems,
            'completed_count': self.completed_count,
            'failed_count': self.failed_count,
            'session_start': self.session_start,
            'last_checkpoint': self.last_checkpoint
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SystemState':
        return cls(**data)


class ResourceCoordinator:
    """
    Central resource coordinator for the math solver system.

    Responsibilities:
    - Agent lifecycle management (activate/deactivate/suspend)
    - Automatic strategy selection (spectral vs balanced)
    - Worker pool management for parallel search
    - Resource monitoring and throttling
    - Graceful shutdown with state persistence
    """

    def __init__(
        self,
        state_dir: Optional[Path] = None,
        limits: Optional[ResourceLimits] = None
    ):
        """
        Initialize the Resource Coordinator.

        Args:
            state_dir: Directory for state persistence (default: data/state)
            limits: Resource limits (default: sensible defaults)
        """
        self.state_dir = state_dir or Path("data/state")
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.limits = limits or ResourceLimits()

        # Agent registry
        self._agents: Dict[str, AgentInfo] = {}
        self._agent_factories: Dict[str, Callable] = {}

        # State
        self._running = False
        self._shutdown_requested = False
        self._lock = threading.RLock()

        # Statistics
        self._system_state = SystemState(
            session_start=datetime.now().isoformat()
        )

        # Partition selector (auto-choosing)
        self._partition_selector = None

        # Register signal handlers
        self._original_sigint = None
        self._original_sigterm = None

        # Hardware monitoring
        self._hardware_metrics: Optional[HardwareMetrics] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_interval = 5.0  # seconds between hardware checks
        self._process = psutil.Process() if HAS_PSUTIL else None

        logger.info("ResourceCoordinator initialized")

    def start(self):
        """Start the coordinator and restore any saved state."""
        if self._running:
            return

        self._running = True
        self._shutdown_requested = False

        # Install signal handlers
        self._install_signal_handlers()

        # Try to restore previous state
        self._restore_state()

        # Initialize adaptive partition selector
        from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
            AdaptivePartitionSelector
        )
        self._partition_selector = AdaptivePartitionSelector()

        # Start hardware monitoring thread
        self._start_hardware_monitor()

        # Initial hardware metrics
        self._hardware_metrics = self._collect_hardware_metrics()

        logger.info("ResourceCoordinator started")

    def stop(self, save_state: bool = True):
        """
        Stop the coordinator gracefully.

        Args:
            save_state: Whether to save state for later resumption
        """
        if not self._running:
            return

        logger.info("ResourceCoordinator stopping...")
        self._shutdown_requested = True

        # Stop hardware monitoring
        self._stop_hardware_monitor()

        # Deactivate all agents
        with self._lock:
            for agent_id in list(self._agents.keys()):
                self._deactivate_agent(agent_id)

        # Save state
        if save_state:
            self._save_state()

        # Restore original signal handlers
        self._restore_signal_handlers()

        self._running = False
        logger.info("ResourceCoordinator stopped")

    def register_agent_factory(
        self,
        agent_type: str,
        factory: Callable[[], Any],
        tier: int = 3,
        memory_estimate_mb: float = 100.0
    ):
        """
        Register a factory function for creating agents on demand.

        Args:
            agent_type: Type identifier (e.g., "algebra_supervisor")
            factory: Function that creates the agent instance
            tier: Agent tier (1=orchestrator, 2=supervisor, 3=specialist)
            memory_estimate_mb: Estimated memory usage
        """
        self._agent_factories[agent_type] = {
            'factory': factory,
            'tier': tier,
            'memory_mb': memory_estimate_mb
        }
        logger.debug(f"Registered agent factory: {agent_type} (tier {tier})")

    def get_or_activate_agent(self, agent_type: str) -> Optional[Any]:
        """
        Get an agent instance, activating it if necessary.

        This is the main entry point for getting agents. The coordinator
        decides whether to:
        - Return existing active agent
        - Activate a standby agent
        - Create a new agent (if within limits)
        - Deactivate idle agents to make room

        Args:
            agent_type: Type of agent needed

        Returns:
            Agent instance or None if unavailable
        """
        with self._lock:
            # Check for existing active agent
            for agent_id, info in self._agents.items():
                if info.agent_type == agent_type and info.state == AgentState.ACTIVE:
                    info.last_active = datetime.now()
                    return info.instance

            # Check for standby agent
            for agent_id, info in self._agents.items():
                if info.agent_type == agent_type and info.state == AgentState.STANDBY:
                    return self._activate_agent(agent_id)

            # Need to create new agent
            return self._create_and_activate_agent(agent_type)

    def release_agent(self, agent_type: str):
        """
        Release an agent back to standby.

        Called when a task is complete. Agent goes to standby
        rather than being destroyed, for faster reuse.
        """
        with self._lock:
            for agent_id, info in self._agents.items():
                if info.agent_type == agent_type and info.state == AgentState.ACTIVE:
                    info.state = AgentState.STANDBY
                    info.last_active = datetime.now()
                    info.tasks_completed += 1
                    logger.debug(f"Agent {agent_id} -> standby")
                    break

    def get_optimal_worker_count(self) -> int:
        """
        Get optimal number of parallel workers based on current load.

        Returns:
            Recommended worker count (1 to max_parallel_workers)
        """
        active_count = sum(
            1 for info in self._agents.values()
            if info.state == AgentState.ACTIVE
        )

        # Reduce workers if many agents are active
        if active_count > self.limits.max_active_agents // 2:
            return max(1, self.limits.max_parallel_workers // 2)

        return self.limits.max_parallel_workers

    def get_adaptive_partition(self, states: Dict, num_workers: int = None):
        """
        Get partition assignment using automatic strategy selection.

        Args:
            states: Dict of state_id -> ProofState
            num_workers: Number of workers (default: optimal)

        Returns:
            WorkerAssignment with automatically chosen strategy
        """
        if num_workers is None:
            num_workers = self.get_optimal_worker_count()

        if self._partition_selector is None:
            from symbo_agentic_reasoners.discovery.deep_search.spectral_partitioner import (
                adaptive_partition
            )
            return adaptive_partition(states, num_workers)

        return self._partition_selector.partition(states, num_workers)

    def get_partition_decision_info(self) -> Dict[str, Any]:
        """Get info about the last partitioning decision."""
        if self._partition_selector:
            return self._partition_selector.get_decision_info()
        return {}

    def add_pending_problem(self, problem: str):
        """Add a problem to the pending queue."""
        with self._lock:
            self._system_state.pending_problems.append(problem)

    def get_next_problem(self) -> Optional[str]:
        """Get next problem from queue."""
        with self._lock:
            if self._system_state.pending_problems:
                return self._system_state.pending_problems.pop(0)
            return None

    def mark_problem_completed(self, success: bool = True):
        """Mark a problem as completed."""
        with self._lock:
            if success:
                self._system_state.completed_count += 1
            else:
                self._system_state.failed_count += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get current system statistics including hardware metrics."""
        with self._lock:
            active = sum(1 for i in self._agents.values() if i.state == AgentState.ACTIVE)
            standby = sum(1 for i in self._agents.values() if i.state == AgentState.STANDBY)

            stats = {
                'running': self._running,
                'agents': {
                    'active': active,
                    'standby': standby,
                    'total': len(self._agents)
                },
                'problems': {
                    'pending': len(self._system_state.pending_problems),
                    'completed': self._system_state.completed_count,
                    'failed': self._system_state.failed_count
                },
                'limits': {
                    'max_agents': self.limits.max_active_agents,
                    'max_workers': self.limits.max_parallel_workers
                },
                'partition_strategy': self.get_partition_decision_info()
            }

            # Add hardware metrics
            if self._hardware_metrics:
                stats['hardware'] = self._hardware_metrics.to_dict()
                stats['hardware_warnings'] = self._get_hardware_warnings()

            return stats

    def get_hardware_metrics(self) -> Optional[HardwareMetrics]:
        """Get current hardware metrics (cached, updated by monitor thread)."""
        return self._hardware_metrics

    def get_hardware_status(self) -> Dict[str, Any]:
        """Get detailed hardware status with warnings and recommendations."""
        metrics = self._collect_hardware_metrics()
        self._hardware_metrics = metrics

        warnings = self._get_hardware_warnings()
        can_proceed = self._can_proceed_based_on_hardware()

        return {
            'metrics': metrics.to_dict(),
            'warnings': warnings,
            'can_proceed': can_proceed,
            'recommendations': self._get_hardware_recommendations()
        }

    def can_proceed_with_task(self) -> bool:
        """Check if system resources allow proceeding with new task."""
        return self._can_proceed_based_on_hardware()

    def request_shutdown(self):
        """Request graceful shutdown (called by signal handler)."""
        logger.info("Shutdown requested")
        self._shutdown_requested = True

    def is_shutdown_requested(self) -> bool:
        """Check if shutdown has been requested."""
        return self._shutdown_requested

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _activate_agent(self, agent_id: str) -> Optional[Any]:
        """Activate a standby agent."""
        info = self._agents.get(agent_id)
        if not info:
            return None

        info.state = AgentState.ACTIVE
        info.last_active = datetime.now()
        logger.debug(f"Agent {agent_id} -> active")
        return info.instance

    def _deactivate_agent(self, agent_id: str):
        """Deactivate an agent."""
        info = self._agents.get(agent_id)
        if not info:
            return

        info.state = AgentState.INACTIVE
        info.instance = None
        logger.debug(f"Agent {agent_id} -> inactive")

    def _create_and_activate_agent(self, agent_type: str) -> Optional[Any]:
        """Create a new agent and activate it."""
        if agent_type not in self._agent_factories:
            logger.warning(f"No factory for agent type: {agent_type}")
            return None

        # Check limits
        active_count = sum(
            1 for i in self._agents.values()
            if i.state == AgentState.ACTIVE
        )

        if active_count >= self.limits.max_active_agents:
            # Try to deactivate idle agents
            self._cleanup_idle_agents()

            # Recheck
            active_count = sum(
                1 for i in self._agents.values()
                if i.state == AgentState.ACTIVE
            )
            if active_count >= self.limits.max_active_agents:
                logger.warning("Cannot activate agent: at limit")
                return None

        # Create agent
        factory_info = self._agent_factories[agent_type]
        try:
            instance = factory_info['factory']()
            agent_id = f"{agent_type}_{len(self._agents)}"

            info = AgentInfo(
                agent_id=agent_id,
                agent_type=agent_type,
                tier=factory_info['tier'],
                state=AgentState.ACTIVE,
                instance=instance,
                last_active=datetime.now(),
                memory_estimate_mb=factory_info['memory_mb']
            )

            self._agents[agent_id] = info
            logger.info(f"Created and activated agent: {agent_id}")
            return instance

        except Exception as e:
            logger.error(f"Failed to create agent {agent_type}: {e}")
            return None

    def _cleanup_idle_agents(self):
        """Deactivate agents that have been idle too long."""
        now = datetime.now()
        timeout = self.limits.idle_timeout_seconds

        for agent_id, info in list(self._agents.items()):
            if info.state == AgentState.STANDBY and info.last_active:
                idle_time = (now - info.last_active).total_seconds()
                if idle_time > timeout:
                    self._deactivate_agent(agent_id)

    def _save_state(self):
        """Save system state to disk."""
        self._system_state.last_checkpoint = datetime.now().isoformat()
        self._system_state.agents = {
            aid: info.to_dict() for aid, info in self._agents.items()
        }

        state_file = self.state_dir / "coordinator_state.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(self._system_state.to_dict(), f, indent=2)
            logger.info(f"State saved to {state_file}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _restore_state(self):
        """Restore system state from disk."""
        state_file = self.state_dir / "coordinator_state.json"
        if not state_file.exists():
            return

        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
            self._system_state = SystemState.from_dict(data)
            logger.info(
                f"Restored state: {len(self._system_state.pending_problems)} pending, "
                f"{self._system_state.completed_count} completed"
            )
        except Exception as e:
            logger.warning(f"Failed to restore state: {e}")

    def _install_signal_handlers(self):
        """Install graceful shutdown handlers."""
        def handler(signum, frame):
            print("\n\nReceived shutdown signal. Saving state...")
            self.request_shutdown()

        try:
            self._original_sigint = signal.signal(signal.SIGINT, handler)
            if hasattr(signal, 'SIGTERM'):
                self._original_sigterm = signal.signal(signal.SIGTERM, handler)
        except (ValueError, OSError):
            # Can't set signal handler (e.g., not main thread)
            pass

    def _restore_signal_handlers(self):
        """Restore original signal handlers."""
        try:
            if self._original_sigint:
                signal.signal(signal.SIGINT, self._original_sigint)
            if self._original_sigterm and hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, self._original_sigterm)
        except (ValueError, OSError):
            pass

    # =========================================================================
    # Hardware Monitoring Methods
    # =========================================================================

    def _start_hardware_monitor(self):
        """Start background thread for hardware monitoring."""
        if not HAS_PSUTIL:
            logger.info("Hardware monitoring disabled (psutil not available)")
            return

        self._monitor_thread = threading.Thread(
            target=self._hardware_monitor_loop,
            daemon=True,
            name="HardwareMonitor"
        )
        self._monitor_thread.start()
        logger.info("Hardware monitoring thread started")

    def _stop_hardware_monitor(self):
        """Stop the hardware monitoring thread."""
        # Thread is daemon, will stop when main process exits
        # But we signal it via _running flag
        pass

    def _hardware_monitor_loop(self):
        """Background loop that periodically collects hardware metrics."""
        while self._running and not self._shutdown_requested:
            try:
                self._hardware_metrics = self._collect_hardware_metrics()

                # Check for critical conditions
                if self._hardware_metrics:
                    self._check_critical_conditions()

            except Exception as e:
                logger.warning(f"Hardware monitoring error: {e}")

            time.sleep(self._monitor_interval)

    def _collect_hardware_metrics(self) -> HardwareMetrics:
        """Collect current hardware metrics using psutil."""
        if not HAS_PSUTIL:
            return HardwareMetrics()

        try:
            # System-wide metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Process-specific metrics
            proc_memory = 0.0
            proc_cpu = 0.0
            if self._process:
                try:
                    proc_memory = self._process.memory_info().rss / (1024 * 1024)
                    proc_cpu = self._process.cpu_percent(interval=0.1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return HardwareMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_percent=disk.percent,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                process_memory_mb=proc_memory,
                process_cpu_percent=proc_cpu,
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.warning(f"Failed to collect hardware metrics: {e}")
            return HardwareMetrics()

    def _get_hardware_warnings(self) -> List[str]:
        """Generate warning messages based on current hardware state."""
        warnings = []
        if not self._hardware_metrics:
            return warnings

        m = self._hardware_metrics
        l = self.limits

        if m.cpu_percent >= l.cpu_critical_threshold * 100:
            warnings.append(f"CRITICAL: CPU at {m.cpu_percent:.1f}%")
        elif m.cpu_percent >= l.cpu_warning_threshold * 100:
            warnings.append(f"WARNING: CPU at {m.cpu_percent:.1f}%")

        if m.memory_percent >= l.memory_critical_threshold * 100:
            warnings.append(f"CRITICAL: Memory at {m.memory_percent:.1f}%")
        elif m.memory_percent >= l.memory_warning_threshold * 100:
            warnings.append(f"WARNING: Memory at {m.memory_percent:.1f}%")

        if m.disk_percent >= l.disk_warning_threshold * 100:
            warnings.append(f"WARNING: Disk at {m.disk_percent:.1f}%")

        return warnings

    def _can_proceed_based_on_hardware(self) -> bool:
        """Determine if system can accept new tasks based on hardware state."""
        if not self._hardware_metrics:
            return True  # No data = assume OK

        m = self._hardware_metrics
        l = self.limits

        # Block if any resource is at critical level
        if m.cpu_percent >= l.cpu_critical_threshold * 100:
            return False
        if m.memory_percent >= l.memory_critical_threshold * 100:
            return False

        return True

    def _get_hardware_recommendations(self) -> List[str]:
        """Generate recommendations based on hardware state."""
        recommendations = []
        if not self._hardware_metrics:
            return recommendations

        m = self._hardware_metrics
        l = self.limits

        # CPU recommendations
        if m.cpu_percent >= l.cpu_warning_threshold * 100:
            active_agents = sum(1 for i in self._agents.values() if i.state == AgentState.ACTIVE)
            if active_agents > 1:
                recommendations.append(f"Consider reducing active agents (currently {active_agents})")

        # Memory recommendations
        if m.memory_percent >= l.memory_warning_threshold * 100:
            if m.memory_available_mb < 1024:
                recommendations.append("Less than 1GB memory available - consider cleanup")
            recommendations.append("Consider deactivating idle agents to free memory")

        # Disk recommendations
        if m.disk_percent >= l.disk_warning_threshold * 100:
            recommendations.append(f"Disk space low ({m.disk_free_gb:.1f}GB free)")

        return recommendations

    def _check_critical_conditions(self):
        """Check for critical conditions and take automatic action."""
        if not self._hardware_metrics:
            return

        m = self._hardware_metrics
        l = self.limits

        # Emergency memory cleanup
        if m.memory_percent >= l.memory_critical_threshold * 100:
            logger.warning("Critical memory pressure - cleaning up idle agents")
            self._cleanup_idle_agents()

        # Emergency CPU relief
        if m.cpu_percent >= l.cpu_critical_threshold * 100:
            logger.warning("Critical CPU pressure detected")
            # Could implement throttling here


# Global coordinator instance
_coordinator: Optional[ResourceCoordinator] = None


def get_coordinator() -> ResourceCoordinator:
    """Get or create the global coordinator instance."""
    global _coordinator
    if _coordinator is None:
        _coordinator = ResourceCoordinator()
    return _coordinator


def shutdown_coordinator():
    """Shutdown the global coordinator."""
    global _coordinator
    if _coordinator:
        _coordinator.stop()
        _coordinator = None
