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
Algebra Specialist Tests
========================

Comprehensive tests for algebra specialist agents:
- ArithmeticSpecialist
- PolynomialSpecialist
- NumberTheorySpecialist
- EquationSystemSolver
- GroupRingTheoryAgent
"""

import pytest


# =============================================================================
# ArithmeticSpecialist Tests
# =============================================================================


class TestArithmeticSpecialist:
    """Tests for ArithmeticSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create ArithmeticSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.algebra.arithmetic_specialist import (
            ArithmeticSpecialist
        )
        return ArithmeticSpecialist()

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


# =============================================================================
# PolynomialSpecialist Tests
# =============================================================================


class TestPolynomialSpecialist:
    """Tests for PolynomialSpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create PolynomialSpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.algebra.polynomial_specialist import (
            PolynomialSpecialist
        )
        return PolynomialSpecialist()

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


# =============================================================================
# NumberTheorySpecialist Tests
# =============================================================================


class TestNumberTheorySpecialist:
    """Tests for NumberTheorySpecialist."""

    @pytest.fixture
    def specialist(self):
        """Create NumberTheorySpecialist instance."""
        from symbo_agentic_reasoners.agents.specialists.algebra.number_theory_specialist import (
            NumberTheorySpecialist
        )
        return NumberTheorySpecialist()

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


# =============================================================================
# EquationSystemSolver Tests
# =============================================================================


class TestEquationSystemSolver:
    """Tests for EquationSystemSolver."""

    @pytest.fixture
    def specialist(self):
        """Create EquationSystemSolver instance."""
        from symbo_agentic_reasoners.agents.specialists.algebra.equation_system_solver import (
            EquationSystemSolver
        )
        return EquationSystemSolver()

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


class TestEquationSystemEnums:
    """Tests for equation system enums and data classes."""

    def test_system_type_enum(self):
        """SystemType enum should exist."""
        from symbo_agentic_reasoners.agents.specialists.algebra.equation_system_solver import (
            SystemType
        )
        assert SystemType is not None
        assert len(list(SystemType)) > 0

    def test_substitution_step_exists(self):
        """SubstitutionStep class should exist."""
        from symbo_agentic_reasoners.agents.specialists.algebra.equation_system_solver import (
            SubstitutionStep
        )
        assert SubstitutionStep is not None

    def test_system_solution_exists(self):
        """SystemSolution class should exist."""
        from symbo_agentic_reasoners.agents.specialists.algebra.equation_system_solver import (
            SystemSolution
        )
        assert SystemSolution is not None


# =============================================================================
# GroupRingTheoryAgent Tests
# =============================================================================


class TestGroupRingTheoryAgent:
    """Tests for GroupRingTheoryAgent."""

    @pytest.fixture
    def specialist(self):
        """Create GroupRingTheoryAgent instance."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupRingTheoryAgent
        )
        return GroupRingTheoryAgent()

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


class TestGroupRingEnums:
    """Tests for group/ring theory enums."""

    def test_structure_type_enum(self):
        """StructureType enum should exist."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            StructureType
        )
        assert StructureType is not None
        assert len(list(StructureType)) > 0

    def test_group_property_enum(self):
        """GroupProperty enum should exist."""
        from symbo_agentic_reasoners.agents.specialists.algebra.group_ring_theory import (
            GroupProperty
        )
        assert GroupProperty is not None
        assert len(list(GroupProperty)) > 0


# =============================================================================
# Main Test Runner
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
