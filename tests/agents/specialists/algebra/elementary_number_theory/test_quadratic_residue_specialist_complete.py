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

"""Complete Test Suite for Quadratic Residue Specialist - 12-Test Pattern"""

import pytest
from symbo_agentic_reasoners.agents.specialists.algebra.elementary_number_theory import QuadraticResidueSpecialist
from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType


class TestQuadraticResidueSpecialist:
    @pytest.fixture
    def specialist(self, directory_facilitator, blackboard):
        return QuadraticResidueSpecialist(agent_id='test_qr_001', df=directory_facilitator, blackboard=blackboard)

    def test_initialization(self, specialist):
        assert specialist.agent_id == 'test_qr_001'
        assert specialist.tasks_executed == 0

    def test_df_registration(self, specialist):
        services = specialist.df.search(service_type='math.algebra.elementary_nt.quadratic_residue')
        assert len(services) > 0

    def test_simple_legendre_symbol(self, specialist):
        task = create_entry(EntryType.TASK, content="(2/7)", author_agent="test", conversation_id="test_001", metadata={'a': 2, 'p': 7})
        result = specialist.process(task)
        assert 'symbol' in result
        # (2/7) = 1 (2 is QR mod 7 since 3² ≡ 2 mod 7)
        assert result['symbol'] == 1

    def test_complex_non_residue(self, specialist):
        task = create_entry(EntryType.TASK, content="(3/7)", author_agent="test", conversation_id="test_001", metadata={'a': 3, 'p': 7})
        result = specialist.process(task)
        # (3/7) = -1 (3 is non-QR mod 7)
        assert result.get('symbol') == -1

    def test_edge_case_zero(self, specialist):
        task = create_entry(EntryType.TASK, content="(0/7)", author_agent="test", conversation_id="test_001", metadata={'a': 0, 'p': 7})
        result = specialist.process(task)
        # (0/p) = 0
        assert result.get('symbol') == 0

    def test_edge_case_multiple_of_p(self, specialist):
        task = create_entry(EntryType.TASK, content="(7/7)", author_agent="test", conversation_id="test_001", metadata={'a': 7, 'p': 7})
        result = specialist.process(task)
        # (p/p) = 0
        assert result.get('symbol') == 0

    def test_edge_case_one(self, specialist):
        task = create_entry(EntryType.TASK, content="(1/7)", author_agent="test", conversation_id="test_001", metadata={'a': 1, 'p': 7})
        result = specialist.process(task)
        # (1/p) = 1 always
        assert result.get('symbol') == 1

    def test_invalid_input(self, specialist):
        task = create_entry(EntryType.TASK, content="Invalid", author_agent="test", conversation_id="test_001", metadata={'a': 1, 'p': 0})
        result = specialist.process(task)
        assert 'error' in result

    def test_blackboard_integration(self, specialist, blackboard):
        task = create_entry(EntryType.TASK, content="Test", author_agent="test", conversation_id="test_001", metadata={'a': 2, 'p': 5})
        specialist.process(task)
        assert specialist.tasks_executed >= 1

    def test_statistics(self, specialist):
        stats = specialist.get_statistics()
        assert stats['tier'] == '3'

    def test_bdi_interface(self, specialist):
        specialist.update_beliefs()
        intentions = specialist.deliberate()
        assert isinstance(intentions, list)

    @pytest.mark.parametrize("a,p", [(2,3), (2,5), (2,7), (3,7), (5,11)])
    def test_multiple_legendre(self, specialist, a, p):
        task = create_entry(EntryType.TASK, content=f"({a}/{p})", author_agent="test", conversation_id="test_001", metadata={'a': a, 'p': p})
        result = specialist.process(task)
        assert result is not None
        assert 'symbol' in result


pytestmark = pytest.mark.phase4
