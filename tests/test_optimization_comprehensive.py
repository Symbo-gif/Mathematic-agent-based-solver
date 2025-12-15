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
Optimization Module Comprehensive Tests
=======================================

Tests for optimization modules to achieve 75%+ coverage:
- ComputeOptimizer
- GPUScheduler
- EvolutionaryFlywheel
- ThoughtTraceHarvester
- DistillationPipeline
- ResilienceTester
- SecurityMonitor
"""

import pytest


# =============================================================================
# ComputeOptimizer Tests
# =============================================================================


class TestWorkloadProfile:
    """Tests for WorkloadProfile dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import WorkloadProfile
        profile = WorkloadProfile(agent_id="agent1")
        assert profile.agent_id == "agent1"
        assert profile.cpu_usage_pct == 0.0

    def test_creation_with_values(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import WorkloadProfile
        profile = WorkloadProfile(
            agent_id="agent2",
            cpu_usage_pct=50.0,
            memory_usage_mb=1024,
            gpu_usage_pct=25.0
        )
        assert profile.cpu_usage_pct == 50.0
        assert profile.memory_usage_mb == 1024

    def test_to_dict(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import WorkloadProfile
        profile = WorkloadProfile(agent_id="agent3")
        d = profile.to_dict()
        assert d['agent_id'] == "agent3"
        assert 'cpu_pct' in d


class TestComputeNode:
    """Tests for ComputeNode dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import ComputeNode
        node = ComputeNode(
            node_id="node1",
            cpu_cores=8,
            memory_total_mb=16384
        )
        assert node.node_id == "node1"
        assert node.cpu_cores == 8

    def test_with_gpu(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import ComputeNode
        node = ComputeNode(
            node_id="node2",
            cpu_cores=16,
            memory_total_mb=32768,
            has_gpu=True,
            gpu_memory_mb=16384
        )
        assert node.has_gpu is True
        assert node.gpu_memory_mb == 16384

    def test_to_dict(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import ComputeNode
        node = ComputeNode(node_id="node3", cpu_cores=4, memory_total_mb=8192)
        d = node.to_dict()
        assert d['node_id'] == "node3"
        assert 'cpu_cores' in d


class TestPlacementDecision:
    """Tests for PlacementDecision dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import PlacementDecision
        decision = PlacementDecision(
            agent_id="agent1",
            target_node="node1",
            reason="load balancing",
            priority=5,
            estimated_improvement_pct=10.0
        )
        assert decision.agent_id == "agent1"
        assert decision.priority == 5

    def test_to_dict(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import PlacementDecision
        decision = PlacementDecision(
            agent_id="agent2",
            target_node="node2",
            reason="memory pressure",
            priority=10,
            estimated_improvement_pct=20.0
        )
        d = decision.to_dict()
        assert d['agent_id'] == "agent2"


class TestResourceType:
    """Tests for ResourceType enum."""

    def test_cpu(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import ResourceType
        assert ResourceType.CPU.value == "cpu"

    def test_gpu(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import ResourceType
        assert ResourceType.GPU.value == "gpu"

    def test_memory(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import ResourceType
        assert ResourceType.MEMORY.value == "memory"


class TestPlacementStrategy:
    """Tests for PlacementStrategy enum."""

    def test_balanced(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import PlacementStrategy
        assert PlacementStrategy.BALANCED.value == "balanced"

    def test_packed(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import PlacementStrategy
        assert PlacementStrategy.PACKED.value == "packed"


class TestComputeOptimizer:
    """Tests for ComputeOptimizer class."""

    @pytest.fixture
    def optimizer(self):
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import ComputeOptimizer
        return ComputeOptimizer()

    def test_initialization(self, optimizer):
        assert optimizer is not None

    def test_has_get_statistics(self, optimizer):
        assert hasattr(optimizer, 'get_statistics')

    def test_get_statistics(self, optimizer):
        stats = optimizer.get_statistics()
        assert isinstance(stats, dict)

    def test_has_update_beliefs(self, optimizer):
        assert hasattr(optimizer, 'update_beliefs')

    def test_has_deliberate(self, optimizer):
        assert hasattr(optimizer, 'deliberate')

    def test_get_topology_summary(self, optimizer):
        summary = optimizer.get_topology_summary()
        assert isinstance(summary, dict)


# =============================================================================
# GPUScheduler Tests
# =============================================================================


class TestTaskPriority:
    """Tests for TaskPriority enum."""

    def test_critical(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import TaskPriority
        assert TaskPriority.CRITICAL.value == 0

    def test_high(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import TaskPriority
        assert TaskPriority.HIGH.value == 1

    def test_normal(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import TaskPriority
        assert TaskPriority.NORMAL.value == 2

    def test_low(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import TaskPriority
        assert TaskPriority.LOW.value == 3


class TestExecutionTarget:
    """Tests for ExecutionTarget enum."""

    def test_gpu(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import ExecutionTarget
        assert ExecutionTarget.GPU.value == 'gpu'

    def test_cpu(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import ExecutionTarget
        assert ExecutionTarget.CPU.value == 'cpu'


class TestGPUTask:
    """Tests for GPUTask dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import GPUTask
        task = GPUTask(priority=1, task_id="task1")
        assert task.task_id == "task1"

    def test_with_priority(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import GPUTask, TaskPriority
        task = GPUTask(priority=TaskPriority.HIGH.value, task_id="task2")
        assert task.priority == TaskPriority.HIGH.value

    def test_to_dict(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import GPUTask
        task = GPUTask(priority=2, task_id="task3")
        d = task.to_dict()
        assert d['task_id'] == "task3"


class TestGPUStatus:
    """Tests for GPUStatus dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import GPUStatus
        status = GPUStatus(
            available=True,
            device_count=1,
            current_device=0,
            memory_total_mb=16384,
            memory_used_mb=4096,
            memory_free_mb=12288,
            device_name="Test GPU"
        )
        assert status.available is True
        assert status.memory_total_mb == 16384

    def test_to_dict(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import GPUStatus
        status = GPUStatus(
            available=False,
            device_count=0,
            current_device=-1,
            memory_total_mb=0,
            memory_used_mb=0,
            memory_free_mb=0,
            device_name="None"
        )
        d = status.to_dict()
        assert d['available'] is False


class TestGPUScheduler:
    """Tests for GPUScheduler class."""

    @pytest.fixture
    def scheduler(self):
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import GPUScheduler
        return GPUScheduler()

    def test_initialization(self, scheduler):
        assert scheduler is not None

    def test_has_get_statistics(self, scheduler):
        assert hasattr(scheduler, 'get_statistics')

    def test_get_statistics(self, scheduler):
        stats = scheduler.get_statistics()
        assert isinstance(stats, dict)

    def test_get_gpu_status(self, scheduler):
        status = scheduler.get_gpu_status()
        assert hasattr(status, 'available')

    def test_get_queue_status(self, scheduler):
        status = scheduler.get_queue_status()
        assert isinstance(status, dict)

    def test_has_update_beliefs(self, scheduler):
        assert hasattr(scheduler, 'update_beliefs')

    def test_has_deliberate(self, scheduler):
        assert hasattr(scheduler, 'deliberate')


# =============================================================================
# EvolutionaryFlywheel Tests
# =============================================================================


class TestEvolutionaryFlywheel:
    """Tests for EvolutionaryFlywheel class."""

    def test_import(self):
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        assert EvolutionaryFlywheel is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()
        assert flywheel is not None

    def test_has_get_statistics(self):
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()
        assert hasattr(flywheel, 'get_statistics')

    def test_get_statistics(self):
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import EvolutionaryFlywheel
        flywheel = EvolutionaryFlywheel()
        stats = flywheel.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# Distillation Harvester Tests
# =============================================================================


class TestVerificationStatus:
    """Tests for VerificationStatus enum."""

    def test_pending(self):
        from symbo_agentic_reasoners.optimization.distillation.harvester import VerificationStatus
        assert VerificationStatus.PENDING.value == 'pending'

    def test_verified(self):
        from symbo_agentic_reasoners.optimization.distillation.harvester import VerificationStatus
        assert VerificationStatus.VERIFIED.value == 'verified'


class TestThoughtTrace:
    """Tests for ThoughtTrace dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.optimization.distillation.harvester import ThoughtTrace, VerificationStatus
        from datetime import datetime
        trace = ThoughtTrace(
            trace_id="trace1",
            timestamp=datetime.now(),
            original_query="2+2",
            query_type="computation",
            complexity_score=0.1,
            orchestrator_decomposition=["add 2 and 2"],
            supervisor_strategy="algebra",
            specialist_agents_invoked=["arithmetic"],
            symbolic_expressions=["2+2", "4"],
            fitted_coefficients={},
            taylor_expansion_order=0,
            groebner_basis_used=False,
            verification_status=VerificationStatus.VERIFIED,
            formal_proof_lean4=None,
            debate_consensus_score=None,
            final_answer="4",
            confidence_score=1.0,
            total_latency_ms=100.0,
            agents_activated=1,
            symbolic_ops_count=1
        )
        assert trace.trace_id == "trace1"
        assert trace.original_query == "2+2"


class TestThoughtTraceHarvester:
    """Tests for ThoughtTraceHarvester class."""

    def test_import(self):
        from symbo_agentic_reasoners.optimization.distillation.harvester import ThoughtTraceHarvester
        assert ThoughtTraceHarvester is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.optimization.distillation.harvester import ThoughtTraceHarvester
        harvester = ThoughtTraceHarvester()
        assert harvester is not None

    def test_has_get_statistics(self):
        from symbo_agentic_reasoners.optimization.distillation.harvester import ThoughtTraceHarvester
        harvester = ThoughtTraceHarvester()
        assert hasattr(harvester, 'get_statistics')

    def test_get_statistics(self):
        from symbo_agentic_reasoners.optimization.distillation.harvester import ThoughtTraceHarvester
        harvester = ThoughtTraceHarvester()
        stats = harvester.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# Distillation Pipeline Tests
# =============================================================================


class TestDistillationPipeline:
    """Tests for DistillationPipeline class."""

    def test_import(self):
        from symbo_agentic_reasoners.optimization.distillation.pipeline import DistillationPipeline
        assert DistillationPipeline is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.optimization.distillation.pipeline import DistillationPipeline
        pipeline = DistillationPipeline()
        assert pipeline is not None

    def test_has_get_statistics(self):
        from symbo_agentic_reasoners.optimization.distillation.pipeline import DistillationPipeline
        pipeline = DistillationPipeline()
        assert hasattr(pipeline, 'get_statistics')

    def test_get_statistics(self):
        from symbo_agentic_reasoners.optimization.distillation.pipeline import DistillationPipeline
        pipeline = DistillationPipeline()
        stats = pipeline.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# ResilienceTester Tests
# =============================================================================


class TestResilienceTester:
    """Tests for ResilienceTester class."""

    def test_import(self):
        from symbo_agentic_reasoners.infrastructure.hardening.resilience_tester import ResilienceTester
        assert ResilienceTester is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.infrastructure.hardening.resilience_tester import ResilienceTester
        tester = ResilienceTester()
        assert tester is not None

    def test_has_get_statistics(self):
        from symbo_agentic_reasoners.infrastructure.hardening.resilience_tester import ResilienceTester
        tester = ResilienceTester()
        assert hasattr(tester, 'get_statistics')

    def test_get_statistics(self):
        from symbo_agentic_reasoners.infrastructure.hardening.resilience_tester import ResilienceTester
        tester = ResilienceTester()
        stats = tester.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# SecurityMonitor Tests
# =============================================================================


class TestSecurityMonitor:
    """Tests for SecurityMonitor class."""

    def test_import(self):
        from symbo_agentic_reasoners.infrastructure.hardening.security_monitor import SecurityMonitor
        assert SecurityMonitor is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.infrastructure.hardening.security_monitor import SecurityMonitor
        monitor = SecurityMonitor()
        assert monitor is not None

    def test_has_get_statistics(self):
        from symbo_agentic_reasoners.infrastructure.hardening.security_monitor import SecurityMonitor
        monitor = SecurityMonitor()
        assert hasattr(monitor, 'get_statistics')

    def test_get_statistics(self):
        from symbo_agentic_reasoners.infrastructure.hardening.security_monitor import SecurityMonitor
        monitor = SecurityMonitor()
        stats = monitor.get_statistics()
        assert isinstance(stats, dict)


# =============================================================================
# SymboLLM Tests
# =============================================================================


class TestLLMTask:
    """Tests for LLMTask dataclass."""

    def test_creation(self):
        from symbo_agentic_reasoners.optimization.symbo.symbo_llm import LLMTask
        task = LLMTask(
            prompt="test prompt",
            max_tokens=100
        )
        assert task.prompt == "test prompt"
        assert task.max_tokens == 100

    def test_with_context(self):
        from symbo_agentic_reasoners.optimization.symbo.symbo_llm import LLMTask
        task = LLMTask(
            prompt="solve x^2=4",
            context="find all real solutions",
            task_type="computation"
        )
        assert task.context == "find all real solutions"


class TestSymboLLMAdapter:
    """Tests for SymboLLMAdapter class."""

    def test_import(self):
        from symbo_agentic_reasoners.optimization.symbo.symbo_llm import SymboLLMAdapter
        assert SymboLLMAdapter is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.optimization.symbo.symbo_llm import SymboLLMAdapter
        adapter = SymboLLMAdapter()
        assert adapter is not None

    def test_has_generate(self):
        from symbo_agentic_reasoners.optimization.symbo.symbo_llm import SymboLLMAdapter
        adapter = SymboLLMAdapter()
        assert hasattr(adapter, 'generate')

    def test_has_handle_task(self):
        from symbo_agentic_reasoners.optimization.symbo.symbo_llm import SymboLLMAdapter
        adapter = SymboLLMAdapter()
        assert hasattr(adapter, 'handle_task')


class TestSymboLLMCore:
    """Tests for SymboLLMCore class."""

    def test_import(self):
        from symbo_agentic_reasoners.optimization.symbo.symbo_llm_core import SymboLLMCore
        assert SymboLLMCore is not None

    def test_initialization(self):
        from symbo_agentic_reasoners.optimization.symbo.symbo_llm_core import SymboLLMCore
        core = SymboLLMCore()
        assert core is not None


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
