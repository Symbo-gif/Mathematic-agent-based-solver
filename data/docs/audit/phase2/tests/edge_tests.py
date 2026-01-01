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

import sys
import os
import unittest
import uuid
from typing import Dict, Any

# Add parent directory to path to import symbo_agentic_reasoners_phase2, symbo_agentic_reasoners_phase1, symbo_agentic_reasoners_phase0
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from symbo_agentic_reasoners_phase2.phase2_system import Phase2System
from symbo_agentic_reasoners_phase0.memory.blackboard import create_entry, EntryType
from symbo_agentic_reasoners_phase0.core.omdoc_schema import create_variable

class Phase2EdgeTest(unittest.TestCase):
    """
    Edge tests for Phase 2 System.
    Verifies specific capabilities of the Mathematical Workforce.
    """

    def setUp(self):
        self.system = Phase2System()
        self.system.start()

    def tearDown(self):
        self.system.shutdown()

    def test_polynomial_groebner(self):
        """Test solving system of equations using Gröbner bases"""
        print("\n[Edge] Testing Polynomial Specialist (Gröbner bases)...")
        
        # Create task entry
        # System: x + y = 2, x - y = 0 -> x=1, y=1
        # SymPy expects expressions equal to zero
        input_str = "x + y - 2, x - y"
        
        entry = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("solve system"),
            author_agent='tester',
            conversation_id=f'test_poly_{uuid.uuid4()}',
            metadata={
                'operation': 'solve',
                'raw_input': input_str,
                'sympy_expr': input_str
            }
        )
        
        result_entry = self.system.polynomial_specialist.process(entry)
        result = result_entry.metadata.get('result')
        
        print(f"  Result: {result}")
        
        # Verify result
        # Result should be a list of dicts or similar
        # Expected: [{'x': 1, 'y': 1}] (values might be SymPy numbers)
        self.assertIsNotNone(result)
        self.assertTrue(str(result).find('1') != -1, "Result should contain 1")

    def test_integration_symbolic(self):
        """Test symbolic integration (Risch algorithm)"""
        print("\n[Edge] Testing Integration Specialist (Symbolic)...")
        
        entry = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("integrate"),
            author_agent='tester',
            conversation_id=f'test_int_sym_{uuid.uuid4()}',
            metadata={
                'raw_input': 'x**2',
                'sympy_expr': 'x**2',
                'variable': 'x',
                'engine': 'symbolic'
            }
        )
        
        result_entry = self.system.integration_specialist.process(entry)
        result = result_entry.metadata.get('result_str')
        engine = result_entry.metadata.get('engine')
        
        print(f"  Result: {result}")
        print(f"  Engine: {engine}")
        
        self.assertEqual(engine, 'symbolic')
        self.assertIn('x**3', result.replace(' ', ''))

    def test_integration_numerical(self):
        """Test numerical integration (Quadrature)"""
        print("\n[Edge] Testing Integration Specialist (Numerical)...")
        
        # Integrate sin(x) from 0 to pi -> 2
        entry = create_entry(
            entry_type=EntryType.TASK,
            content=create_variable("integrate numerical"),
            author_agent='tester',
            conversation_id=f'test_int_num_{uuid.uuid4()}',
            metadata={
                'raw_input': 'sin(x)',
                'sympy_expr': 'sin(x)',
                'variable': 'x',
                'bounds': (0, 3.14159265359),
                'engine': 'numerical'
            }
        )
        
        result_entry = self.system.integration_specialist.process(entry)
        result = float(result_entry.metadata.get('result'))
        engine = result_entry.metadata.get('engine')
        
        print(f"  Result: {result}")
        print(f"  Engine: {engine}")
        
        self.assertEqual(engine, 'numerical')
        self.assertAlmostEqual(result, 2.0, places=5)

    def test_end_to_end_solve(self):
        """Test end-to-end solution via Orchestrator"""
        print("\n[Edge] Testing End-to-End Solve (Orchestrator -> Specialist)...")
        
        # Simple problem that Orchestrator should route to Calculus -> Differentiation
        problem = "derivative of x**3"
        
        try:
            result = self.system.phase1.solve(problem)
            print(f"  Result: {result}")
            self.assertIn("3*x**2", result.replace(" ", ""))
        except Exception as e:
            print(f"  [WARNING] End-to-end solve failed: {e}")
            # This might fail if Orchestrator logic isn't fully updated or if NLP parsing fails
            # But Phase 1 solve worked in Phase 1 audit, so it should work here too
            # unless Phase 2 broke something.
            # We'll allow it to fail but print warning, or fail test?
            # Let's fail test to be strict.
            self.fail(f"End-to-end solve failed: {e}")

if __name__ == '__main__':
    unittest.main()
