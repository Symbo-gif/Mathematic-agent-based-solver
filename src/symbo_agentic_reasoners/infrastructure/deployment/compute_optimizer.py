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
PHASE 5 - HD-2: COMPUTE OPTIMIZER (Tier 3)
==========================================

Optimizes compute resource allocation and provides agent placement
decisions based on workload profiles and hardware topology.

CAPABILITIES:
------------
- Workload profiling and analysis
- Agent placement optimization
- Migration recommendations
- Topology-aware scheduling
- Load balancing

REFERENCE:
---------
- Agent_System_Audit.docx.md: HD-2 Compute Optimizer
- Phase_5_Optimization.md: Hybrid Deployment Team
"""

import sys
import os
import logging
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger('symbo_agentic_reasoners.phase5.compute_optimizer')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class ResourceType(Enum):
    """Types of compute resources"""
    CPU = "cpu"
    GPU = "gpu"
    MEMORY = "memory"
    IO = "io"


class PlacementStrategy(Enum):
    """Agent placement strategies"""
    BALANCED = "balanced"        # Distribute evenly
    PACKED = "packed"           # Minimize resource waste
    SPREAD = "spread"           # Maximize fault tolerance
    AFFINITY = "affinity"       # Co-locate related agents


@dataclass
class WorkloadProfile:
    """
    Profile of an agent's workload.
    
    Attributes:
        agent_id: Agent identifier
        cpu_usage_pct: Average CPU usage percentage
        memory_usage_mb: Average memory usage
        gpu_usage_pct: Average GPU usage percentage
        io_ops_per_sec: I/O operations per second
        samples: Number of samples collected
    """
    agent_id: str
    cpu_usage_pct: float = 0.0
    memory_usage_mb: int = 0
    gpu_usage_pct: float = 0.0
    io_ops_per_sec: float = 0.0
    samples: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'agent_id': self.agent_id,
            'cpu_pct': round(self.cpu_usage_pct, 1),
            'memory_mb': self.memory_usage_mb,
            'gpu_pct': round(self.gpu_usage_pct, 1),
            'io_ops': round(self.io_ops_per_sec, 1),
            'samples': self.samples
        }


@dataclass
class ComputeNode:
    """Perform to dict operation.

    Args:
    No arguments

    Returns:
    Result of the operation

    Example:
    >>> result = obj.to_dict(...)
    """
    """Represents a compute node in the topology"""
    node_id: str
    cpu_cores: int
    memory_total_mb: int
    has_gpu: bool = False
    gpu_memory_mb: int = 0
    current_load_pct: float = 0.0
    assigned_agents: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'node_id': self.node_id,
            'cpu_cores': self.cpu_cores,
            'memory_mb': self.memory_total_mb,
            'has_gpu': self.has_gpu,
            'load_pct': round(self.current_load_pct, 1),
            'agent_count': len(self.assigned_agents)
        }


@dataclass
class PlacementDecision:
    """Agent placement decision"""
    agent_id: str
    target_node: str
    """Perform to dict operation.

    Args:
    No arguments

    Returns:
    Result of the operation

    Example:
    >>> result = obj.to_dict(...)
    """
    reason: str
    priority: int
    estimated_improvement_pct: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'agent_id': self.agent_id,
            'target_node': self.target_node,
            'reason': self.reason,
            'improvement_pct': round(self.estimated_improvement_pct, 1)
        }


@dataclass
class MigrationPlan:
    """Plan for migrating agents between nodes"""
    plan_id: str
    migrations: List[PlacementDecision]
    estimated_downtime_ms: int
    risk_level: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'plan_id': self.plan_id,
            'migration_count': len(self.migrations),
            'downtime_ms': self.estimated_downtime_ms,
            'risk': self.risk_level
        }


class ComputeOptimizer(BDIAgent):
    """
    HD-2: Compute Optimizer
    
    DIRECTIVE:
    ---------
    Optimize compute resource allocation through workload profiling
    and intelligent agent placement.
    
    INPUTS:
    ------
    - Workload execution profiles
    - Hardware topology information
    - Agent resource requirements
    
    OUTPUTS:
    -------
    - Agent placement decisions
    - Migration plan proposals
    - Load balancing recommendations
    
    DEPENDENCIES:
    ------------
    - HD-1 (GPUScheduler): For GPU resource information
    - FA-3 (FaultPredictor): For reliability considerations
    
    FAILURE MODE: STABLE - Maintains current placement configuration
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 591-600
    """
    
    def __init__(
        self,
        agent_id: str = 'compute_optimizer_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Compute Optimizer
        
        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        
        # Workload profiles
        self.workload_profiles: Dict[str, WorkloadProfile] = {}
        
        # Topology graph
        self.topology: Dict[str, ComputeNode] = {}
        
        # Placement history
        self.placement_history: List[PlacementDecision] = []
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.optimizations_performed = 0
        self.migrations_suggested = 0
        
        # Initialize default topology
        self._initialize_default_topology()
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Compute Optimizer initialized")
        print(f"  Topology nodes: {len(self.topology)}")
    
    def _initialize_default_topology(self):
        """Initialize with a default single-node topology"""
        # Default: single local node
        import platform
        import psutil
        
        try:
            cpu_count = psutil.cpu_count() or 4
            memory_mb = psutil.virtual_memory().total // (1024 * 1024)
        except Exception:
            cpu_count = 4
            memory_mb = 8192
        
        local_node = ComputeNode(
            node_id="local",
            cpu_cores=cpu_count,
            memory_total_mb=memory_mb,
            has_gpu=False  # Conservative default
        )
        self.topology["local"] = local_node
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='system.compute.optimize',
            agent_id=self.agent_id,
            algorithm='placement_optimization',
            cost='medium',
            type='analysis',
            tier='3',
            algorithms='profiling_placement_migration'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: system.compute.optimize")
    
    def update_workload_profile(
        self,
        agent_id: str,
        cpu_usage: float,
        memory_usage: int,
        gpu_usage: float = 0.0,
        io_ops: float = 0.0
    ):
        """
        Update workload profile for an agent.
        
        Args:
            agent_id: Agent identifier
            cpu_usage: CPU usage percentage (0-100)
            memory_usage: Memory usage in MB
            gpu_usage: GPU usage percentage (0-100)
            io_ops: I/O operations per second
        """
        if agent_id not in self.workload_profiles:
            self.workload_profiles[agent_id] = WorkloadProfile(agent_id=agent_id)
        
        profile = self.workload_profiles[agent_id]
        
        # Exponential moving average
        alpha = 0.2
        profile.cpu_usage_pct = (1 - alpha) * profile.cpu_usage_pct + alpha * cpu_usage
        profile.memory_usage_mb = int((1 - alpha) * profile.memory_usage_mb + alpha * memory_usage)
        profile.gpu_usage_pct = (1 - alpha) * profile.gpu_usage_pct + alpha * gpu_usage
        profile.io_ops_per_sec = (1 - alpha) * profile.io_ops_per_sec + alpha * io_ops
        profile.samples += 1
        profile.last_updated = datetime.now()
    
    def add_compute_node(self, node: ComputeNode):
        """Add a compute node to the topology"""
        self.topology[node.node_id] = node
    
    def optimize_placement(
        self,
        strategy: PlacementStrategy = PlacementStrategy.BALANCED
    ) -> List[PlacementDecision]:
        """
        Generate optimized placement decisions.
        
        Args:
            strategy: Placement strategy to use
            
        Returns:
            List of placement decisions
        """
        self.tasks_executed += 1
        self.optimizations_performed += 1
        
        try:
            decisions = []
            
            if strategy == PlacementStrategy.BALANCED:
                decisions = self._optimize_balanced()
            elif strategy == PlacementStrategy.PACKED:
                decisions = self._optimize_packed()
            elif strategy == PlacementStrategy.SPREAD:
                decisions = self._optimize_spread()
            else:
                decisions = self._optimize_balanced()
            
            self.placement_history.extend(decisions)
            self.tasks_succeeded += 1
            
            return decisions
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Optimization failed: {type(e).__name__}: {e}")
            return []
    
    def _optimize_balanced(self) -> List[PlacementDecision]:
        """Balance load across nodes"""
        decisions = []
        
        # Calculate current load per node
        node_loads = {}
        for node_id, node in self.topology.items():
            total_cpu = 0.0
            for agent_id in node.assigned_agents:
                if agent_id in self.workload_profiles:
                    total_cpu += self.workload_profiles[agent_id].cpu_usage_pct
            node_loads[node_id] = total_cpu / (node.cpu_cores * 100) * 100
        
        if not node_loads:
            return decisions
        
        avg_load = sum(node_loads.values()) / len(node_loads)
        
        # Find overloaded and underloaded nodes
        overloaded = [n for n, l in node_loads.items() if l > avg_load * 1.2]
        underloaded = [n for n, l in node_loads.items() if l < avg_load * 0.8]
        
        # Suggest migrations from overloaded to underloaded
        for over_node in overloaded:
            if not underloaded:
                break
            
            node = self.topology[over_node]
            for agent_id in node.assigned_agents[:1]:  # Move one at a time
                target = underloaded[0]
                improvement = (node_loads[over_node] - avg_load) / 2
                
                decision = PlacementDecision(
                    agent_id=agent_id,
                    target_node=target,
                    reason=f"Balance load from {over_node} ({node_loads[over_node]:.0f}%) to {target}",
                    priority=1,
                    estimated_improvement_pct=improvement
                )
                decisions.append(decision)
                self.migrations_suggested += 1
        
        return decisions
    
    def _optimize_packed(self) -> List[PlacementDecision]:
        """Pack agents to minimize resource waste"""
        return []  # Placeholder for packed strategy
    
    def _optimize_spread(self) -> List[PlacementDecision]:
        """Spread agents for fault tolerance"""
        return []  # Placeholder for spread strategy
    
    def generate_migration_plan(
        self,
        decisions: List[PlacementDecision]
    ) -> MigrationPlan:
        """
        Generate a migration plan from placement decisions.
        
        Args:
            decisions: List of placement decisions
            
        Returns:
            MigrationPlan with execution details
        """
        # Estimate downtime (100ms per migration)
        downtime_ms = len(decisions) * 100
        
        # Assess risk
        if len(decisions) > 5:
            risk = "high"
        elif len(decisions) > 2:
            risk = "medium"
        else:
            risk = "low"
        
        plan = MigrationPlan(
            plan_id=f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            migrations=decisions,
            estimated_downtime_ms=downtime_ms,
            risk_level=risk
        )
        
        return plan
    
    def get_topology_summary(self) -> Dict[str, Any]:
        """Get summary of current topology"""
        summary = {
            'node_count': len(self.topology),
            'nodes': [node.to_dict() for node in self.topology.values()],
            'total_cpu_cores': sum(n.cpu_cores for n in self.topology.values()),
            'total_memory_mb': sum(n.memory_total_mb for n in self.topology.values()),
            'gpu_nodes': sum(1 for n in self.topology.values() if n.has_gpu)
        }
        return summary
    
    def process(self, task_entry: Any) -> Any:
        """Process compute optimization task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing compute optimization task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'status')
            
            if operation == 'status':
                result = {
                    'topology': self.get_topology_summary(),
                    'profiles': {k: v.to_dict() for k, v in self.workload_profiles.items()}
                }
                
            elif operation == 'update_profile':
                agent_id = metadata.get('agent_id')
                self.update_workload_profile(
                    agent_id=agent_id,
                    cpu_usage=metadata.get('cpu_usage', 0),
                    memory_usage=metadata.get('memory_usage', 0),
                    gpu_usage=metadata.get('gpu_usage', 0),
                    io_ops=metadata.get('io_ops', 0)
                )
                result = {'updated': agent_id}
                
            elif operation == 'optimize':
                strategy_str = metadata.get('strategy', 'balanced')
                strategy = PlacementStrategy(strategy_str)
                decisions = self.optimize_placement(strategy)
                result = {
                    'decisions': [d.to_dict() for d in decisions],
                    'count': len(decisions)
                }
                
            elif operation == 'migration_plan':
                strategy_str = metadata.get('strategy', 'balanced')
                strategy = PlacementStrategy(strategy_str)
                decisions = self.optimize_placement(strategy)
                plan = self.generate_migration_plan(decisions)
                result = plan.to_dict()
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Optimization task failed: {type(e).__name__}: {e}")
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
            tags=['compute', 'optimizer'],
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
            tags=['error', 'compute'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """Monitor workload profiles"""
        pass
    
    def deliberate(self):
        """Generate optimization plans"""
        return []
    
    def execute_step(self, intention: Intention):
        """Execute optimization step"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get optimizer statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'optimizations_performed': self.optimizations_performed,
            'migrations_suggested': self.migrations_suggested,
            'profiles_tracked': len(self.workload_profiles),
            'topology_nodes': len(self.topology)
        })
        return stats


if __name__ == "__main__":
    """Test Compute Optimizer"""
    print("=" * 80)
    print("PHASE 5 - COMPUTE OPTIMIZER TEST")
    print("=" * 80)
    print()
    
    # Initialize optimizer
    optimizer = ComputeOptimizer()
    print()
    
    # Test 1: Get topology
    print("Test 1: Topology Summary")
    summary = optimizer.get_topology_summary()
    print(f"  Nodes: {summary['node_count']}")
    print(f"  Total CPU cores: {summary['total_cpu_cores']}")
    print(f"  Total memory: {summary['total_memory_mb']} MB")
    print()
    
    # Test 2: Add workload profiles
    print("Test 2: Update Workload Profiles")
    optimizer.update_workload_profile("agent_1", cpu_usage=75, memory_usage=512)
    optimizer.update_workload_profile("agent_2", cpu_usage=30, memory_usage=256)
    optimizer.update_workload_profile("agent_3", cpu_usage=90, memory_usage=1024)
    
    for agent_id, profile in optimizer.workload_profiles.items():
        print(f"  {agent_id}: CPU={profile.cpu_usage_pct:.0f}%, Mem={profile.memory_usage_mb}MB")
    print()
    
    # Test 3: Add nodes and agents
    print("Test 3: Multi-node Topology")
    node2 = ComputeNode(node_id="node2", cpu_cores=8, memory_total_mb=16384)
    optimizer.add_compute_node(node2)
    
    # Assign agents
    optimizer.topology["local"].assigned_agents = ["agent_1", "agent_3"]
    optimizer.topology["node2"].assigned_agents = ["agent_2"]
    
    for node_id, node in optimizer.topology.items():
        print(f"  {node_id}: {len(node.assigned_agents)} agents")
    print()
    
    # Test 4: Optimize placement
    print("Test 4: Optimize Placement (Balanced)")
    decisions = optimizer.optimize_placement(PlacementStrategy.BALANCED)
    print(f"  Decisions: {len(decisions)}")
    for d in decisions:
        print(f"    - Move {d.agent_id} to {d.target_node}: {d.reason}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(optimizer.get_statistics(), indent=2))
