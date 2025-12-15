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
PHASE 5 - HD-1: GPU SCHEDULER (Tier 3)
=====================================

Schedules GPU-amenable tasks and manages GPU resource allocation.
Provides CPU fallback for systems without GPU support.

CAPABILITIES:
------------
- Monitor GPU availability and memory
- Queue and schedule GPU tasks
- Manage kernel execution
- Provide CPU fallback when GPU unavailable
- Track GPU memory usage

ALGORITHMIC BACKING:
-------------------
- PyTorch/CUDA for GPU detection
- Priority queue for task scheduling
- Memory-aware allocation

REFERENCE:
---------
- Agent_System_Audit.docx.md: HD-1 GPU Scheduler
- Phase_5_Optimization.md: Hybrid Deployment Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
from queue import PriorityQueue
import time

# Try to import torch for GPU detection
try:
    import torch
    HAS_TORCH = True
    CUDA_AVAILABLE = torch.cuda.is_available()
except (ImportError, RuntimeError, OSError):
    # ImportError: torch not installed
    # RuntimeError: torch version incompatible with Python version (e.g., Python 3.14)
    # OSError: library loading issues
    HAS_TORCH = False
    CUDA_AVAILABLE = False

logger = logging.getLogger('symbo_agentic_reasoners.phase5.gpu_scheduler')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class TaskPriority(Enum):
    """Priority levels for GPU tasks"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class ExecutionTarget(Enum):
    """Target device for execution"""
    GPU = "gpu"
    CPU = "cpu"
    AUTO = "auto"


@dataclass(order=True)
class GPUTask:
    """
    A task scheduled for GPU execution.
    
    Attributes:
        task_id: Unique identifier
        priority: Execution priority
        memory_required_mb: Estimated memory requirement
        compute_fn: Function to execute
        args: Function arguments
        created_at: Creation timestamp
        status: Current status
    """
    priority: int
    task_id: str = field(compare=False)
    memory_required_mb: int = field(compare=False, default=256)
    compute_fn: Optional[Callable] = field(compare=False, default=None)
    args: Dict[str, Any] = field(compare=False, default_factory=dict)
    created_at: datetime = field(compare=False, default_factory=datetime.now)
    status: str = field(compare=False, default="pending")
    result: Any = field(compare=False, default=None)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'priority': self.priority,
            'memory_mb': self.memory_required_mb,
            'status': self.status,
            'has_result': self.result is not None
        }


@dataclass
class GPUStatus:
    """Current GPU status"""
    available: bool
    device_count: int
    current_device: int
    memory_total_mb: int
    memory_used_mb: int
    memory_free_mb: int
    device_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'available': self.available,
            'device_count': self.device_count,
            'device_name': self.device_name,
            'memory_total_mb': self.memory_total_mb,
            'memory_used_mb': self.memory_used_mb,
            'memory_free_mb': self.memory_free_mb,
            'utilization': self.memory_used_mb / self.memory_total_mb if self.memory_total_mb > 0 else 0
        }


class GPUScheduler(BDIAgent):
    """
    HD-1: GPU Scheduler
    
    DIRECTIVE:
    ---------
    Schedule GPU-amenable tasks and manage GPU resources.
    Provides automatic CPU fallback when GPU is unavailable.
    
    INPUTS:
    ------
    - GPU-amenable task requests
    - GPU resource availability status
    - Priority specifications
    
    OUTPUTS:
    -------
    - GPU assignment allocations
    - Kernel launch directives
    - Execution results
    
    DEPENDENCIES:
    ------------
    - CNS-1 (PlannerAgent): For task coordination
    - CR-2 (ResourceContentionManager): For resource allocation
    
    FAILURE MODE: FALLBACK - Reverts to CPU execution
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 580-589
    """
    
    def __init__(
        self,
        agent_id: str = 'gpu_scheduler_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        max_queue_size: int = 100
    ):
        """
        Initialize GPU Scheduler
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            max_queue_size: Maximum task queue size
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        self.max_queue_size = max_queue_size
        
        # Task queue
        self.task_queue: PriorityQueue = PriorityQueue(maxsize=max_queue_size)
        self.completed_tasks: Dict[str, GPUTask] = {}
        
        # GPU memory tracking
        self.memory_maps: Dict[str, int] = {}  # task_id -> memory allocated
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.gpu_executions = 0
        self.cpu_fallbacks = 0
        
        # Initialize GPU status
        self._init_gpu_status()
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] GPU Scheduler initialized")
        print(f"  CUDA available: {CUDA_AVAILABLE}")
        print(f"  PyTorch available: {HAS_TORCH}")
        if CUDA_AVAILABLE:
            print(f"  GPU: {self.gpu_status.device_name}")
            print(f"  Memory: {self.gpu_status.memory_total_mb} MB")
    
    def _init_gpu_status(self):
        """Initialize GPU status"""
        if CUDA_AVAILABLE and HAS_TORCH:
            device = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(device)
            mem_total = props.total_memory // (1024 * 1024)
            mem_alloc = torch.cuda.memory_allocated(device) // (1024 * 1024)
            
            self.gpu_status = GPUStatus(
                available=True,
                device_count=torch.cuda.device_count(),
                current_device=device,
                memory_total_mb=mem_total,
                memory_used_mb=mem_alloc,
                memory_free_mb=mem_total - mem_alloc,
                device_name=props.name
            )
        else:
            self.gpu_status = GPUStatus(
                available=False,
                device_count=0,
                current_device=-1,
                memory_total_mb=0,
                memory_used_mb=0,
                memory_free_mb=0,
                device_name="CPU Only"
            )
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='system.compute.gpu',
            agent_id=self.agent_id,
            algorithm='gpu_scheduling',
            cost='medium',
            type='execution',
            tier='controller',
            algorithms='priority_queue_memory_aware'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: system.compute.gpu")
    
    def get_gpu_status(self) -> GPUStatus:
        """Get current GPU status"""
        if CUDA_AVAILABLE and HAS_TORCH:
            device = torch.cuda.current_device()
            mem_alloc = torch.cuda.memory_allocated(device) // (1024 * 1024)
            self.gpu_status.memory_used_mb = mem_alloc
            self.gpu_status.memory_free_mb = self.gpu_status.memory_total_mb - mem_alloc
        return self.gpu_status
    
    def submit_task(
        self,
        task_id: str,
        compute_fn: Callable,
        args: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        memory_required_mb: int = 256
    ) -> bool:
        """
        Submit a task for GPU execution.
        
        Args:
            task_id: Unique task identifier
            compute_fn: Function to execute
            args: Function arguments
            priority: Task priority
            memory_required_mb: Estimated memory requirement
            
        Returns:
            True if task was queued successfully
        """
        self.tasks_executed += 1
        
        try:
            task = GPUTask(
                priority=priority.value,
                task_id=task_id,
                memory_required_mb=memory_required_mb,
                compute_fn=compute_fn,
                args=args
            )
            
            if self.task_queue.full():
                logger.warning("Task queue is full")
                return False
            
            self.task_queue.put(task)
            logger.info(f"Task {task_id} queued with priority {priority.name}")
            
            return True
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Task submission failed: {type(e).__name__}: {e}")
            return False
    
    def execute_next(self) -> Optional[GPUTask]:
        """
        Execute the next task in the queue.
        
        Returns:
            Completed task or None if queue is empty
        """
        if self.task_queue.empty():
            return None
        
        task = self.task_queue.get()
        task.status = "running"
        
        try:
            # Determine execution target
            target = self._determine_target(task)
            
            if target == ExecutionTarget.GPU:
                result = self._execute_on_gpu(task)
                self.gpu_executions += 1
            else:
                result = self._execute_on_cpu(task)
                self.cpu_fallbacks += 1
            
            task.result = result
            task.status = "completed"
            self.tasks_succeeded += 1
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            self.tasks_failed += 1
            logger.warning(f"Task {task.task_id} failed: {type(e).__name__}: {e}")
        
        self.completed_tasks[task.task_id] = task
        return task
    
    def _determine_target(self, task: GPUTask) -> ExecutionTarget:
        """Determine whether to use GPU or CPU"""
        if not self.gpu_status.available:
            return ExecutionTarget.CPU
        
        # Check memory availability
        if task.memory_required_mb > self.gpu_status.memory_free_mb:
            logger.info(f"GPU memory insufficient for task {task.task_id}, falling back to CPU")
            return ExecutionTarget.CPU
        
        return ExecutionTarget.GPU
    
    def _execute_on_gpu(self, task: GPUTask) -> Any:
        """Execute task on GPU"""
        logger.info(f"Executing task {task.task_id} on GPU")
        
        if task.compute_fn is None:
            return {"status": "no_function", "target": "gpu"}
        
        try:
            # Track memory allocation
            self.memory_maps[task.task_id] = task.memory_required_mb
            
            # Execute function
            result = task.compute_fn(**task.args)
            
            # Clean up memory tracking
            del self.memory_maps[task.task_id]
            
            return result
            
        except Exception as e:
            if task.task_id in self.memory_maps:
                del self.memory_maps[task.task_id]
            raise
    
    def _execute_on_cpu(self, task: GPUTask) -> Any:
        """Execute task on CPU (fallback)"""
        logger.info(f"Executing task {task.task_id} on CPU (fallback)")
        
        if task.compute_fn is None:
            return {"status": "no_function", "target": "cpu"}
        
        return task.compute_fn(**task.args)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task"""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].to_dict()
        
        # Check queue (inefficient but works for small queues)
        for task in list(self.task_queue.queue):
            if task.task_id == task_id:
                return task.to_dict()
        
        return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            'queue_size': self.task_queue.qsize(),
            'max_size': self.max_queue_size,
            'completed_count': len(self.completed_tasks),
            'memory_allocated_mb': sum(self.memory_maps.values())
        }
    
    def process(self, task_entry: Any) -> Any:
        """Process GPU scheduling task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing GPU scheduling task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'status')
            
            if operation == 'status':
                gpu_status = self.get_gpu_status()
                queue_status = self.get_queue_status()
                result = {
                    'gpu': gpu_status.to_dict(),
                    'queue': queue_status
                }
                
            elif operation == 'submit':
                task_id = metadata.get('task_id', f'task_{time.time()}')
                priority = TaskPriority(metadata.get('priority', 2))
                memory = metadata.get('memory_mb', 256)
                
                # Note: compute_fn cannot be passed via metadata
                success = self.submit_task(
                    task_id=task_id,
                    compute_fn=None,
                    args={},
                    priority=priority,
                    memory_required_mb=memory
                )
                result = {'submitted': success, 'task_id': task_id}
                
            elif operation == 'execute_next':
                task = self.execute_next()
                if task:
                    result = task.to_dict()
                else:
                    result = {'status': 'queue_empty'}
                    
            elif operation == 'task_status':
                task_id = metadata.get('task_id')
                status = self.get_task_status(task_id)
                result = status or {'error': 'Task not found'}
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"GPU task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['gpu', 'scheduler'],
            status=EntryStatus.PENDING,
            metadata=result
        )
        
        self.blackboard.post(result_entry)
        return result_entry
    
    def _create_error_entry(self, task_entry: Any, error_msg: str) -> Any:
        """Create error entry for Blackboard"""
        if not self.blackboard:
            return None
        
        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'gpu'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """Monitor GPU status"""
        self._init_gpu_status()
    
    def deliberate(self):
        """Generate scheduling plans"""
        return []
    
    def execute_step(self, intention: Intention):
        """Execute scheduling step"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'gpu_executions': self.gpu_executions,
            'cpu_fallbacks': self.cpu_fallbacks,
            'gpu_available': self.gpu_status.available,
            'queue_size': self.task_queue.qsize()
        })
        return stats


if __name__ == "__main__":
    """Test GPU Scheduler"""
    print("=" * 80)
    print("PHASE 5 - GPU SCHEDULER TEST")
    print("=" * 80)
    print()
    
    # Initialize scheduler
    scheduler = GPUScheduler()
    print()
    
    # Test 1: Get GPU status
    print("Test 1: GPU Status")
    status = scheduler.get_gpu_status()
    print(f"  Available: {status.available}")
    print(f"  Device: {status.device_name}")
    if status.available:
        print(f"  Memory: {status.memory_free_mb}/{status.memory_total_mb} MB free")
    print()
    
    # Test 2: Submit tasks
    print("Test 2: Submit Tasks")
    
    def sample_task(**kwargs):
        return {"computed": True, **kwargs}
    
    scheduler.submit_task("task_1", sample_task, {"x": 1}, TaskPriority.HIGH)
    scheduler.submit_task("task_2", sample_task, {"x": 2}, TaskPriority.NORMAL)
    scheduler.submit_task("task_3", sample_task, {"x": 3}, TaskPriority.LOW)
    
    queue_status = scheduler.get_queue_status()
    print(f"  Queue size: {queue_status['queue_size']}")
    print()
    
    # Test 3: Execute tasks
    print("Test 3: Execute Tasks")
    while scheduler.task_queue.qsize() > 0:
        task = scheduler.execute_next()
        if task:
            print(f"  Executed: {task.task_id} -> {task.status}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(scheduler.get_statistics(), indent=2))
