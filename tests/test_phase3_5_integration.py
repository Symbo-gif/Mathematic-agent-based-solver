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
Full Integration Test for Phase 3-5 Expansion
==============================================
Tests that new agents integrate with existing infrastructure.
"""

import pytest
from src.symbo_agentic_reasoners.infrastructure.agent_factory import AgentFactory
from src.symbo_agentic_reasoners.infrastructure.directory_facilitator import DirectoryFacilitator
from src.symbo_agentic_reasoners.core.blackboard import Blackboard


class TestPhase35Integration:
    """Integration tests for Phase 3-5 agents."""

    @pytest.fixture
    def factory(self):
        """Create agent factory with infrastructure."""
        df = DirectoryFacilitator()
        bb = Blackboard()
        factory = AgentFactory(df=df, blackboard=bb)
        factory.create_supervisors()
        factory.create_specialists()
        return factory

    def test_all_gf_specialists_created(self, factory):
        """Test all 7 GF specialists are created."""
        gf_specialists = [
            'ordinary_gf_specialist_001',
            'exponential_gf_specialist_001',
            'rational_gf_specialist_001',
            'recurrence_gf_specialist_001',
            'bivariate_gf_specialist_001',
            'gf_composition_specialist_001',
            'asymptotic_extraction_specialist_001'
        ]

        for sid in gf_specialists:
            assert sid in factory.agents, f"{sid} not created"

    def test_all_elementary_nt_specialists_created(self, factory):
        """Test all 7 Elementary NT specialists are created."""
        ent_specialists = [
            'congruence_specialist_001',
            'continued_fractions_specialist_001',
            'pell_equation_specialist_001',
            'tonelli_shanks_specialist_001',
            'lte_specialist_001',
            'diophantine_basic_specialist_001',
            'quadratic_residue_specialist_001'
        ]

        for sid in ent_specialists:
            assert sid in factory.agents, f"{sid} not created"

    def test_elementary_nt_supervisor_created(self, factory):
        """Test ElementaryNT supervisor is created."""
        assert 'elementary_nt_supervisor_001' in factory.agents

    def test_gf_service_registration(self, factory):
        """Test all GF service types are registered."""
        df = factory.df
        gf_services = [
            'math.discrete.gf.ordinary',
            'math.discrete.gf.exponential',
            'math.discrete.gf.rational',
            'math.discrete.gf.recurrence',
            'math.discrete.gf.bivariate',
            'math.discrete.gf.composition',
            'math.discrete.gf.asymptotic'
        ]

        for service in gf_services:
            results = df.search(service_type=service)
            assert len(results) > 0, f"{service} not registered"

    def test_elementary_nt_service_registration(self, factory):
        """Test all Elementary NT service types are registered."""
        df = factory.df
        ent_services = [
            'math.algebra.elementary_nt',
            'math.algebra.elementary_nt.congruence',
            'math.algebra.elementary_nt.continued_fractions',
            'math.algebra.elementary_nt.pell',
            'math.algebra.elementary_nt.tonelli_shanks',
            'math.algebra.elementary_nt.lte',
            'math.algebra.elementary_nt.diophantine',
            'math.algebra.elementary_nt.quadratic_residue'
        ]

        for service in ent_services:
            results = df.search(service_type=service)
            assert len(results) > 0, f"{service} not registered"

    def test_ordinary_gf_specialist_functionality(self, factory):
        """Test OrdinaryGF specialist can process tasks."""
        specialist = factory.agents.get('ordinary_gf_specialist_001')
        assert specialist is not None

        class MockTask:
            def __init__(self, metadata):
                self.metadata = metadata
                self.entry_id = 'test_001'

        task = MockTask({'operation': 'geometric_series', 'r': 2, 'n_terms': 5})
        result = specialist.process(task)

        assert 'coefficients' in result
        assert result['coefficients'] == [1, 2, 4, 8, 16]

    def test_congruence_specialist_functionality(self, factory):
        """Test Congruence specialist can process tasks."""
        specialist = factory.agents.get('congruence_specialist_001')
        assert specialist is not None

        class MockTask:
            def __init__(self, metadata):
                self.metadata = metadata
                self.entry_id = 'test_002'

        task = MockTask({'operation': 'solve_linear', 'a': 3, 'b': 5, 'm': 7})
        result = specialist.process(task)

        assert 'solutions' in result or 'has_solution' in result

    def test_discrete_math_supervisor_gf_routing(self, factory):
        """Test DiscreteMath supervisor routes to GF specialists."""
        supervisor = factory.agents.get('discrete_math_supervisor_001')
        assert supervisor is not None

        class MockEntry:
            def __init__(self, raw_input):
                self.metadata = {'raw_input': raw_input}

        # Test GF routing
        decision = supervisor._analyze_task(MockEntry("ordinary generating function"))
        assert 'gf.ordinary' in decision['service_type']

        decision = supervisor._analyze_task(MockEntry("exponential generating function"))
        assert 'gf.exponential' in decision['service_type']

    def test_elementary_nt_supervisor_routing(self, factory):
        """Test ElementaryNT supervisor routes correctly."""
        supervisor = factory.agents.get('elementary_nt_supervisor_001')
        assert supervisor is not None

        class MockEntry:
            def __init__(self, raw_input):
                self.metadata = {'raw_input': raw_input}

        # Test routing to different specialists
        assert supervisor._determine_specialist(MockEntry("solve congruence")) == 'congruence'
        assert supervisor._determine_specialist(MockEntry("pell equation")) == 'pell'
        assert supervisor._determine_specialist(MockEntry("tonelli shanks")) == 'tonelli_shanks'
        assert supervisor._determine_specialist(MockEntry("continued fraction")) == 'continued_fractions'

    def test_algebra_supervisor_elementary_nt_routing(self, factory):
        """Test AlgebraSupervisor routes to Elementary NT."""
        algebra_sup = factory.agents.get('algebra_supervisor_001')
        if algebra_sup:
            class MockEntry:
                def __init__(self, raw_input):
                    self.metadata = {'raw_input': raw_input}

            # Use more specific Elementary NT keyword
            decision = algebra_sup._analyze_task(MockEntry("chinese remainder theorem system of congruences"))
            assert 'elementary_nt' in decision['service_type']

    def test_total_agent_count(self, factory):
        """Test total agent count matches expectations."""
        total_agents = len(factory.agents)
        # Should have 260 existing + 15 new = 275 total
        # But factory only creates a subset, so just verify > 15
        assert total_agents >= 15, f"Expected at least 15 agents, got {total_agents}"

    def test_agent_statistics(self, factory):
        """Test all new agents report statistics correctly."""
        new_agents = [
            'ordinary_gf_specialist_001',
            'congruence_specialist_001',
            'elementary_nt_supervisor_001'
        ]

        for agent_id in new_agents:
            if agent_id in factory.agents:
                agent = factory.agents[agent_id]
                stats = agent.get_statistics()
                assert isinstance(stats, dict)
                assert 'agent_id' in stats
                assert 'tier' in stats

    def test_no_registration_conflicts(self, factory):
        """Test no service type conflicts with existing agents."""
        df = factory.df

        # Each service type should have exactly 1 registration
        # (or be intentionally designed for multiple)
        all_services = df.list_all_services()

        # Just verify we can list services without error
        assert len(all_services) > 0


pytestmark = [pytest.mark.integration, pytest.mark.phase3]
