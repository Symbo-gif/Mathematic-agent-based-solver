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
Infrastructure Modules Tests
============================

Additional tests to improve coverage for infrastructure modules.
"""

import pytest


# =============================================================================
# ACC (Agent Coordination Center) Tests
# =============================================================================


class TestACC:
    """Tests for ACC module."""

    def test_import_module(self):
        """ACC module should be importable."""
        from symbo_agentic_reasoners.infrastructure import acc
        assert acc is not None


# =============================================================================
# Agent Pool Tests
# =============================================================================


class TestAgentPool:
    """Tests for AgentPool."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.infrastructure.agent_pool import (
            AgentPool
        )
        assert AgentPool is not None


# =============================================================================
# Watchdog Tests
# =============================================================================


class TestWatchdog:
    """Tests for Watchdog."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.infrastructure.watchdog import (
            Watchdog
        )
        assert Watchdog is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.infrastructure.watchdog import (
            Watchdog
        )
        watchdog = Watchdog()
        assert watchdog is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.infrastructure.watchdog import (
            Watchdog
        )
        watchdog = Watchdog()
        assert hasattr(watchdog, 'get_statistics')


# =============================================================================
# Agent Registry Tests
# =============================================================================


class TestAgentRegistry:
    """Tests for agent_registry module."""

    def test_import_module(self):
        """agent_registry module should be importable."""
        from symbo_agentic_reasoners.infrastructure import agent_registry
        assert agent_registry is not None


# =============================================================================
# Resource Governor Tests
# =============================================================================


class TestResourceGovernor:
    """Tests for ResourceGovernor."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.infrastructure.resource_governor import (
            ResourceGovernor
        )
        assert ResourceGovernor is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.infrastructure.resource_governor import (
            ResourceGovernor
        )
        governor = ResourceGovernor()
        assert governor is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.infrastructure.resource_governor import (
            ResourceGovernor
        )
        governor = ResourceGovernor()
        assert hasattr(governor, 'get_statistics')


# =============================================================================
# AMS Tests
# =============================================================================


class TestAMS:
    """Tests for AgentManagementSystem."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.infrastructure.ams import (
            AgentManagementSystem
        )
        assert AgentManagementSystem is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.infrastructure.ams import (
            AgentManagementSystem
        )
        ams = AgentManagementSystem()
        assert ams is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.infrastructure.ams import (
            AgentManagementSystem
        )
        ams = AgentManagementSystem()
        assert hasattr(ams, 'get_statistics')


# =============================================================================
# Optimization Module Tests
# =============================================================================


class TestComputeOptimizer:
    """Tests for ComputeOptimizer."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import (
            ComputeOptimizer
        )
        assert ComputeOptimizer is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import (
            ComputeOptimizer
        )
        optimizer = ComputeOptimizer()
        assert optimizer is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.infrastructure.deployment.compute_optimizer import (
            ComputeOptimizer
        )
        optimizer = ComputeOptimizer()
        assert hasattr(optimizer, 'get_statistics')


class TestGPUScheduler:
    """Tests for GPUScheduler."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import (
            GPUScheduler
        )
        assert GPUScheduler is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import (
            GPUScheduler
        )
        scheduler = GPUScheduler()
        assert scheduler is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.infrastructure.deployment.gpu_scheduler import (
            GPUScheduler
        )
        scheduler = GPUScheduler()
        assert hasattr(scheduler, 'get_statistics')


class TestEvolutionaryFlywheel:
    """Tests for EvolutionaryFlywheel."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import (
            EvolutionaryFlywheel
        )
        assert EvolutionaryFlywheel is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import (
            EvolutionaryFlywheel
        )
        flywheel = EvolutionaryFlywheel()
        assert flywheel is not None

    def test_has_get_statistics(self):
        """Should have get_statistics."""
        from symbo_agentic_reasoners.optimization.evolutionary_flywheel import (
            EvolutionaryFlywheel
        )
        flywheel = EvolutionaryFlywheel()
        assert hasattr(flywheel, 'get_statistics')


# =============================================================================
# Verification Core Tests
# =============================================================================


class TestVerificationCore:
    """Tests for VerificationCore."""

    def test_import(self):
        """Should be importable."""
        from symbo_agentic_reasoners.verification.verification_core import (
            VerificationCore
        )
        assert VerificationCore is not None

    def test_initialization(self):
        """Should initialize."""
        from symbo_agentic_reasoners.verification.verification_core import (
            VerificationCore
        )
        core = VerificationCore()
        assert core is not None


# =============================================================================
# Integration Protocol Tests
# =============================================================================


class TestProtocolUpdates:
    """Tests for protocol_updates module."""

    def test_import_module(self):
        """protocol_updates module should be importable."""
        from symbo_agentic_reasoners.integration import protocol_updates
        assert protocol_updates is not None


# =============================================================================
# SymboLLM Tests
# =============================================================================


class TestSymboLLM:
    """Tests for symbo_llm module."""

    def test_import_module(self):
        """symbo_llm module should be importable."""
        from symbo_agentic_reasoners.optimization.symbo import symbo_llm
        assert symbo_llm is not None


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
