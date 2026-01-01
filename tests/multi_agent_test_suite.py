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

import unittest
from symbo_agentic_reasoners.core.orchestrator import MainOrchestrator as OrchestratorAgent


class TestMultiAgentSystem(unittest.TestCase):
    def setUp(self):
        self.orchestrator = OrchestratorAgent()
        
    def test_calculus_specialist_routing(self):
        problem = "limit((x^2 + 1)/(x - 1), x, infinity)"
        result = self.orchestrator.solve_problem(problem)
        
        self.assertIn('calculus', result['verification']['verification']['debate_history'][0][0].lower())
        self.assertGreater(result['confidence'], 0.85)
        
    def test_symbolic_specialist_routing(self):
        problem = "solve(x^2 + 5x + 6 = 0, x)"
        result = self.orchestrator.solve_problem(problem)
        
        self.assertIn('symbolic', result['verification']['verification']['debate_history'][0][0].lower())
        self.assertEqual(len(result['solution']['solutions']), 2)
        
    def test_multi_agent_debate_validation(self):
        problem = "zeta(1 + 1/x) as x approaches infinity"
        result = self.orchestrator.solve_problem(problem)
        
        # Verify debate history exists
        self.assertTrue(len(result['verification']['verification']['debate_history']) > 0)
        
        # Verify confidence score is based on debate
        self.assertGreater(result['confidence'], 0.0)
        
    def test_error_recovery(self):
        # Test with malformed input
        problem = "limit((x^2 + 1)/(x - 1)"
        result = self.orchestrator.solve_problem(problem)
        
        # Should be auto-corrected by input normalizer
        self.assertIsNotNone(result['solution'])
        self.assertIn('auto-corrected', result['verification']['verification']['issues'][0].lower())
        
    def test_special_function_recognition(self):
        problem = "Gamma(1/2)"
        result = self.orchestrator.solve_problem(problem)
        
        self.assertEqual(result['solution']['value'], "sqrt(pi)")
        

if __name__ == '__main__':
    unittest.main()
