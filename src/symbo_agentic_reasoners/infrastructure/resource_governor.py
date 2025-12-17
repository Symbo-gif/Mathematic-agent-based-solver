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
RESOURCE GOVERNOR - Central Resource Management System
======================================================

Provides unified resource management integrating:
- AMS (Agent Management System) - VRAM/agent lifecycle
- Watchdog - Operation timeouts
- GPU Scheduler - GPU task management (optional)
- System metrics - CPU/RAM/Disk monitoring

ARCHITECTURE:
------------
                    +-------------------------+
                    |   RESOURCE GOVERNOR     |
                    |   (Central Coordinator) |
                    +-------------------------+
                              |
        +---------------------+---------------------+
        |                     |                     |
   +----v----+          +-----v-----+         +----v----+
   |   AMS   |          | Watchdog  |         |  GPU    |
   | (VRAM)  |          | (Timeouts)|         |Scheduler|
   +---------+          +-----------+         +---------+
        |                     |                     |
        +---------------------+---------------------+
                              |
                    +--------------------+
                    | THROTTLE DECISION  |
                    +--------------------+
                              |
        PROCEED          THROTTLE          EMERGENCY
        (< 80%)          (80-95%)           SHUTDOWN
                                            (>95%)

USAGE:
------
    from symbo_agentic_reasoners.infrastructure.resource_governor import (
        ResourceGovernor, get_governor
    )

    # Get singleton instance
    governor = get_governor()

    # Start monitoring
    governor.start()

    # Check if operation can proceed
    if governor.can_proceed():
        do_operation()

    # Get current resource status
    status = governor.get_status()

    # Register for emergency notifications
    governor.on_emergency(my_callback)
"""

import threading
import time
import logging
import json
from typing import Dict, Optional, Callable, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

logger = logging.getLogger('symbo_agentic_reasoners.resource_governor')

# Import AMS
from symbo_agentic_reasoners.infrastructure.ams import (
    AgentManagementSystem, EmergencyLevel, AgentType, AgentStatus,
    VRAM_THRESHOLD, RAM_THRESHOLD, CPU_THRESHOLD,
    VRAM_CRITICAL_THRESHOLD, RAM_CRITICAL_THRESHOLD
)

# Import Watchdog
from symbo_agentic_reasoners.infrastructure.watchdog import (
    Watchdog, WatchedTask, TaskStatus, get_watchdog
)

# Try to import psutil for additional metrics
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class ThrottleLevel(Enum):
    """Throttle levels for operation control"""
    NONE = 0          # No throttling, full speed
    LIGHT = 1         # Minor delays, reduced concurrency
    MODERATE = 2      # Significant delays, one operation at a time
    HEAVY = 3         # Emergency-only operations
    BLOCKED = 4       # No new operations allowed


@dataclass
class ResourceStatus:
    """Current resource status snapshot"""
    timestamp: datetime
    vram_utilization: float
    ram_utilization: float
    cpu_utilization: float
    disk_utilization: float
    emergency_level: EmergencyLevel
    throttle_level: ThrottleLevel
    active_tasks: int
    queued_agents: int
    can_proceed: bool
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "vram": round(self.vram_utilization, 3),
            "ram": round(self.ram_utilization, 3),
            "cpu": round(self.cpu_utilization, 3),
            "disk": round(self.disk_utilization, 3),
            "emergency_level": self.emergency_level.name,
            "throttle_level": self.throttle_level.name,
            "active_tasks": self.active_tasks,
            "queued_agents": self.queued_agents,
            "can_proceed": self.can_proceed,
            "warnings": self.warnings
        }


class ResourceGovernor:
    """
    Central resource management coordinator

    Integrates AMS, Watchdog, and optional GPU Scheduler to provide
    unified resource management and emergency response.
    """

    _instance: Optional['ResourceGovernor'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize Resource Governor

        Args:
            log_dir: Directory for resource logs
        """
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Core components
        self._ams: Optional[AgentManagementSystem] = None
        self._watchdog: Optional[Watchdog] = None
        self._gpu_scheduler = None  # Optional, may not be available

        # State
        self._running = False
        self._throttle_level = ThrottleLevel.NONE
        self._last_status: Optional[ResourceStatus] = None

        # Callbacks
        self._emergency_callbacks: List[Callable[[EmergencyLevel, Dict], None]] = []
        self._throttle_callbacks: List[Callable[[ThrottleLevel], None]] = []

        # Logging
        self._log_dir = Path(log_dir) if log_dir else Path("data/traces/resource")
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self._log_dir / f"resource_governor_{datetime.now().strftime('%Y%m%d')}.jsonl"

        # Statistics
        self._operations_allowed = 0
        self._operations_throttled = 0
        self._operations_blocked = 0
        self._emergency_events = 0

        self._initialized = True
        logger.info("ResourceGovernor initialized")

    def initialize(self, ams: Optional[AgentManagementSystem] = None,
                  watchdog: Optional[Watchdog] = None,
                  gpu_scheduler: Any = None):
        """
        Initialize with component instances

        Args:
            ams: AgentManagementSystem instance (created if not provided)
            watchdog: Watchdog instance (created if not provided)
            gpu_scheduler: Optional GPU scheduler instance
        """
        # Initialize AMS
        if ams is not None:
            self._ams = ams
        else:
            self._ams = AgentManagementSystem(
                error_log_dir=str(self._log_dir / "ams")
            )

        # Initialize Watchdog
        if watchdog is not None:
            self._watchdog = watchdog
        else:
            self._watchdog = get_watchdog()

        # Optional GPU scheduler
        self._gpu_scheduler = gpu_scheduler

        # Register for AMS emergency callbacks
        self._ams.register_emergency_callback(self._on_ams_emergency)

        # Register for Watchdog timeout callbacks
        self._watchdog.register_timeout_callback(self._on_task_timeout)

        logger.info("ResourceGovernor components initialized")

    def start(self):
        """Start all resource monitoring"""
        if self._ams is None:
            self.initialize()

        self._running = True

        # Start AMS monitoring
        self._ams.start()
        logger.info("  AMS monitoring started")

        # Start Watchdog monitoring
        self._watchdog.start()
        logger.info("  Watchdog monitoring started")

        # Start GPU scheduler if available
        if self._gpu_scheduler and hasattr(self._gpu_scheduler, 'start'):
            self._gpu_scheduler.start()
            logger.info("  GPU Scheduler started")

        logger.info("ResourceGovernor: All resource monitoring active")

    def stop(self):
        """Stop all resource monitoring"""
        self._running = False

        if self._ams:
            self._ams.stop()

        if self._watchdog:
            self._watchdog.stop()

        if self._gpu_scheduler and hasattr(self._gpu_scheduler, 'stop'):
            self._gpu_scheduler.stop()

        logger.info("ResourceGovernor stopped")

    def can_proceed(self, operation_type: str = "default") -> bool:
        """
        Check if an operation can proceed

        Args:
            operation_type: Type of operation (affects priority)

        Returns:
            True if operation should proceed
        """
        status = self.get_status()

        # Always allow critical operations
        if operation_type in ["emergency", "shutdown", "health_check"]:
            return True

        # Check throttle level
        if status.throttle_level == ThrottleLevel.BLOCKED:
            self._operations_blocked += 1
            return False

        if status.throttle_level == ThrottleLevel.HEAVY:
            # Only allow essential operations
            if operation_type not in ["essential", "recovery"]:
                self._operations_throttled += 1
                return False

        # Check emergency level
        if status.emergency_level.value >= EmergencyLevel.CRITICAL.value:
            self._operations_blocked += 1
            return False

        # Check if we can activate cognitive agents
        if operation_type == "cognitive_activation":
            if not self._ams.can_activate_cognitive_agent():
                self._operations_throttled += 1
                return False

        self._operations_allowed += 1
        return True

    def request_operation(self, operation_type: str = "default",
                         timeout: Optional[float] = None,
                         description: str = "") -> Optional[str]:
        """
        Request permission to perform an operation

        Checks resources and registers with watchdog if approved.

        Args:
            operation_type: Type of operation
            timeout: Operation timeout (uses default if not specified)
            description: Human-readable description

        Returns:
            Task ID if approved, None if blocked
        """
        if not self.can_proceed(operation_type):
            return None

        # Register with watchdog
        task_id = f"{operation_type}_{threading.get_ident()}_{time.time()}"
        self._watchdog.start_task(
            task_id=task_id,
            timeout=timeout,
            operation_type=operation_type,
            description=description
        )

        return task_id

    def complete_operation(self, task_id: str, success: bool = True):
        """Mark an operation as complete"""
        status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        self._watchdog.complete_task(task_id, status)

    def heartbeat(self, task_id: str):
        """Send heartbeat for a long-running operation"""
        self._watchdog.heartbeat(task_id)

    def get_status(self) -> ResourceStatus:
        """
        Get current resource status

        Returns:
            ResourceStatus snapshot
        """
        warnings = []

        # Get AMS metrics
        if self._ams:
            ams_snapshot = self._ams.get_resource_snapshot()
            vram = ams_snapshot["vram_utilization"]
            ram = ams_snapshot["ram_utilization"]
            cpu = ams_snapshot["cpu_utilization"]
            emergency_level = EmergencyLevel[ams_snapshot["emergency_level"]]
            queued_agents = ams_snapshot["queue_length"]
        else:
            vram = 0.0
            ram = 0.0
            cpu = 0.0
            emergency_level = EmergencyLevel.NORMAL
            queued_agents = 0

        # Get disk utilization
        disk = self._get_disk_utilization()

        # Get watchdog metrics
        if self._watchdog:
            watchdog_stats = self._watchdog.get_statistics()
            active_tasks = watchdog_stats["active_tasks"]
        else:
            active_tasks = 0

        # Calculate throttle level
        throttle_level = self._calculate_throttle_level(vram, ram, cpu, disk, emergency_level)

        # Generate warnings
        if vram > VRAM_THRESHOLD:
            warnings.append(f"VRAM utilization high: {vram:.1%}")
        if ram > RAM_THRESHOLD:
            warnings.append(f"RAM utilization high: {ram:.1%}")
        if cpu > CPU_THRESHOLD:
            warnings.append(f"CPU utilization high: {cpu:.1%}")
        if disk > 0.90:
            warnings.append(f"Disk utilization high: {disk:.1%}")

        # Determine if operations can proceed
        can_proceed = (
            emergency_level.value < EmergencyLevel.CRITICAL.value and
            throttle_level.value < ThrottleLevel.BLOCKED.value
        )

        status = ResourceStatus(
            timestamp=datetime.now(),
            vram_utilization=vram,
            ram_utilization=ram,
            cpu_utilization=cpu,
            disk_utilization=disk,
            emergency_level=emergency_level,
            throttle_level=throttle_level,
            active_tasks=active_tasks,
            queued_agents=queued_agents,
            can_proceed=can_proceed,
            warnings=warnings
        )

        self._last_status = status
        return status

    def _get_disk_utilization(self) -> float:
        """Get disk utilization for the data directory"""
        if HAS_PSUTIL:
            try:
                usage = psutil.disk_usage(str(self._log_dir))
                return usage.percent / 100.0
            except Exception as e:
                logger.warning(f"Could not get disk usage: {e}")
        return 0.0

    def _calculate_throttle_level(self, vram: float, ram: float, cpu: float,
                                 disk: float, emergency: EmergencyLevel) -> ThrottleLevel:
        """Calculate appropriate throttle level based on resources"""
        # Emergency level takes precedence
        if emergency == EmergencyLevel.EMERGENCY:
            return ThrottleLevel.BLOCKED
        if emergency == EmergencyLevel.CRITICAL:
            return ThrottleLevel.HEAVY

        # Check individual resource thresholds
        critical_count = sum([
            vram >= VRAM_CRITICAL_THRESHOLD,
            ram >= RAM_CRITICAL_THRESHOLD,
            disk >= 0.95
        ])

        if critical_count >= 2:
            return ThrottleLevel.HEAVY

        warning_count = sum([
            vram >= VRAM_THRESHOLD,
            ram >= RAM_THRESHOLD,
            cpu >= CPU_THRESHOLD,
            disk >= 0.90
        ])

        if warning_count >= 3:
            return ThrottleLevel.MODERATE
        if warning_count >= 2:
            return ThrottleLevel.LIGHT

        return ThrottleLevel.NONE

    def _on_ams_emergency(self, level: EmergencyLevel, context: Dict):
        """Handle AMS emergency level change"""
        logger.warning(f"ResourceGovernor: AMS emergency level changed to {level.name}")

        if level.value >= EmergencyLevel.CRITICAL.value:
            self._emergency_events += 1
            self._log_event("emergency", {
                "level": level.name,
                "context": context
            })

        # Update throttle level
        self._throttle_level = self._calculate_throttle_level(
            context.get("vram_utilization", 0),
            context.get("ram_utilization", 0),
            context.get("cpu_utilization", 0),
            self._get_disk_utilization(),
            level
        )

        # Notify callbacks
        for callback in self._emergency_callbacks:
            try:
                callback(level, context)
            except Exception as e:
                logger.error(f"Emergency callback error: {e}")

    def _on_task_timeout(self, task: WatchedTask):
        """Handle watchdog timeout"""
        logger.warning(f"ResourceGovernor: Task timeout - {task.task_id}")
        self._log_event("timeout", {
            "task_id": task.task_id,
            "elapsed": task.elapsed_seconds,
            "timeout": task.timeout_seconds
        })

    def on_emergency(self, callback: Callable[[EmergencyLevel, Dict], None]):
        """Register callback for emergency events"""
        self._emergency_callbacks.append(callback)

    def on_throttle_change(self, callback: Callable[[ThrottleLevel], None]):
        """Register callback for throttle level changes"""
        self._throttle_callbacks.append(callback)

    def _log_event(self, event_type: str, data: Dict):
        """Log an event to the resource log"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        try:
            with open(self._log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Could not write resource log: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get governor statistics"""
        stats = {
            "running": self._running,
            "operations_allowed": self._operations_allowed,
            "operations_throttled": self._operations_throttled,
            "operations_blocked": self._operations_blocked,
            "emergency_events": self._emergency_events,
            "current_throttle_level": self._throttle_level.name
        }

        if self._ams:
            stats["ams"] = self._ams.get_statistics()

        if self._watchdog:
            stats["watchdog"] = self._watchdog.get_statistics()

        if self._last_status:
            stats["last_status"] = self._last_status.to_dict()

        return stats

    def print_status(self):
        """Print current status to console"""
        status = self.get_status()
        print()
        print("=" * 60)
        print("RESOURCE GOVERNOR STATUS")
        print("=" * 60)
        print(f"  VRAM:  {status.vram_utilization:6.1%}  ", end="")
        print("█" * int(status.vram_utilization * 20) + "░" * (20 - int(status.vram_utilization * 20)))
        print(f"  RAM:   {status.ram_utilization:6.1%}  ", end="")
        print("█" * int(status.ram_utilization * 20) + "░" * (20 - int(status.ram_utilization * 20)))
        print(f"  CPU:   {status.cpu_utilization:6.1%}  ", end="")
        print("█" * int(status.cpu_utilization * 20) + "░" * (20 - int(status.cpu_utilization * 20)))
        print(f"  Disk:  {status.disk_utilization:6.1%}  ", end="")
        print("█" * int(status.disk_utilization * 20) + "░" * (20 - int(status.disk_utilization * 20)))
        print()
        print(f"  Emergency Level: {status.emergency_level.name}")
        print(f"  Throttle Level:  {status.throttle_level.name}")
        print(f"  Active Tasks:    {status.active_tasks}")
        print(f"  Queued Agents:   {status.queued_agents}")
        print(f"  Can Proceed:     {status.can_proceed}")
        if status.warnings:
            print()
            print("  Warnings:")
            for w in status.warnings:
                print(f"    - {w}")
        print("=" * 60)


# Global instance getter
def get_governor() -> ResourceGovernor:
    """Get the global ResourceGovernor instance"""
    return ResourceGovernor()


if __name__ == "__main__":
    """Test ResourceGovernor"""
    print("=" * 60)
    print("RESOURCE GOVERNOR TEST")
    print("=" * 60)
    print()

    # Initialize governor
    governor = get_governor()
    governor.initialize()
    governor.start()
    print()

    # Print initial status
    governor.print_status()
    print()

    # Test operation request
    print("Test: Request operation")
    task_id = governor.request_operation(
        operation_type="test",
        timeout=30,
        description="Test operation"
    )
    if task_id:
        print(f"  Operation approved: {task_id}")
        time.sleep(0.5)
        governor.heartbeat(task_id)
        time.sleep(0.5)
        governor.complete_operation(task_id, success=True)
        print("  Operation completed")
    else:
        print("  Operation blocked!")
    print()

    # Print statistics
    print("Statistics:")
    print(json.dumps(governor.get_statistics(), indent=2, default=str))
    print()

    # Stop
    governor.stop()
    print("ResourceGovernor test complete")
