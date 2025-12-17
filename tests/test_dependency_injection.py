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

import unittest
from unittest.mock import MagicMock
from symbo_agentic_reasoners.core.system import Phase6System
from symbo_agentic_reasoners.discovery.deep_search.prover_engine import ProverEngine

class TestDependencyInjection(unittest.TestCase):
    def test_inject_prover(self):
        # Create a mock prover
        mock_prover = MagicMock(spec=ProverEngine)
        mock_prover.health_check.return_value = True
        
        # Inject it into the system
        system = Phase6System(prover_engine=mock_prover)
        
        # Verify it was used
        self.assertEqual(system.prover_engine, mock_prover)
        self.assertEqual(system.search_tree_manager.prover_engine, mock_prover)
        
        # Verify health check calls our mock
        system.health_check()
        mock_prover.health_check.assert_called()

    def test_inject_multiple_components(self):
        # Mock multiple components
        mock_gen = MagicMock()
        mock_gen.health_check.return_value = True
        
        mock_policy = MagicMock()
        mock_policy.health_check.return_value = True
        
        system = Phase6System(
            synthetic_data_generator=mock_gen,
            policy_network=mock_policy
        )
        
        self.assertEqual(system.synthetic_data_generator, mock_gen)
        self.assertEqual(system.policy_network, mock_policy)

if __name__ == '__main__':
    unittest.main()
