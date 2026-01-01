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
Linear Algebra Specialist Tests
===============================

Comprehensive tests for linear algebra specialist agents:
- TensorOperationsAgent
- DecompositionSpecialist
- MatrixOperationsSpecialist
- VectorSpaceAnalyst
"""

import pytest
import sympy as sp


# =============================================================================
# TensorOperationsAgent Tests
# =============================================================================


class TestTensorOperationsAgent:
    """Tests for TensorOperationsAgent."""

    @pytest.fixture
    def specialist(self):
        """Create TensorOperationsAgent instance."""
        from symbo_agentic_reasoners.agents.specialists.linear_algebra.tensor_operations import (
            TensorOperationsAgent
        )
        return TensorOperationsAgent()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_process_method(self, specialist):
        """Should have process method."""
        assert hasattr(specialist, 'process')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


class TestTensorEnums:
    """Tests for tensor-related enums and data classes."""

    def test_tensor_type_enum(self):
        """TensorType enum should exist."""
        from symbo_agentic_reasoners.agents.specialists.linear_algebra.tensor_operations import (
            TensorType
        )
        assert TensorType is not None
        assert len(list(TensorType)) > 0

    def test_index_type_enum(self):
        """IndexType enum should exist."""
        from symbo_agentic_reasoners.agents.specialists.linear_algebra.tensor_operations import (
            IndexType
        )
        assert IndexType is not None
        assert len(list(IndexType)) > 0

    def test_tensor_index_exists(self):
        """TensorIndex class should exist."""
        from symbo_agentic_reasoners.agents.specialists.linear_algebra.tensor_operations import (
            TensorIndex
        )
        assert TensorIndex is not None


# =============================================================================
# DecompositionSpecialist Tests
# =============================================================================


class TestDecompositionSpecialist:
    """Tests for DecompositionSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create DecompositionSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.linear_algebra.decomposition_specialist import (
            DecompositionSpecialist
        )
        return DecompositionSpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# MatrixOperationsSpecialist Tests
# =============================================================================


class TestMatrixOperationsSpecialist:
    """Tests for MatrixOperationsSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create MatrixOperationsSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.linear_algebra.matrix_ops_specialist import (
            MatrixOperationsSpecialist
        )
        return MatrixOperationsSpecialist()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# VectorSpaceAnalyst Tests
# =============================================================================


class TestVectorSpaceAnalyst:
    """Tests for VectorSpaceAnalyst."""

    @pytest.fixture
    def specialist(self):
        """Create VectorSpaceAnalyst instance."""
        from symbo_agentic_reasoners.agents.specialists.linear_algebra.vector_space_analyst import (
            VectorSpaceAnalyst
        )
        return VectorSpaceAnalyst()

    def test_initialization(self, specialist):
        """Should initialize correctly."""
        assert specialist is not None

    def test_has_agent_id(self, specialist):
        """Should have agent_id."""
        assert hasattr(specialist, 'agent_id')

    def test_has_update_beliefs_method(self, specialist):
        """Should have update_beliefs method."""
        assert hasattr(specialist, 'update_beliefs')

    def test_has_deliberate_method(self, specialist):
        """Should have deliberate method."""
        assert hasattr(specialist, 'deliberate')

    def test_update_beliefs_runs(self, specialist):
        """update_beliefs should run without error."""
        specialist.update_beliefs()

    def test_deliberate_returns_list(self, specialist):
        """deliberate should return list."""
        result = specialist.deliberate()
        assert isinstance(result, list)


# =============================================================================
# DecompositionSpecialist Tests (updated)
# =============================================================================


class TestDecompositionSpecialistBasics:
    """Basic tests for DecompositionSpecialist."""

    def test_can_import(self):
        """DecompositionSpecialist should be importable."""
        from symbo_agentic_reasoners.agents.specialists.linear_algebra.decomposition_specialist import (
            DecompositionSpecialist
        )
        assert DecompositionSpecialist is not None


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
