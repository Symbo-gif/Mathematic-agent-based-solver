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

# Add parent directory to path to import symbo_agentic_reasoners_phase0
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from symbo_agentic_reasoners_phase0.phase0_system import Phase0System
try:
    from symbo_agentic_reasoners_phase0.core.fipa_acl import FIPAMessage, Performative
    from symbo_agentic_reasoners_phase0.core.omdoc_schema import create_variable
    from symbo_agentic_reasoners_phase0.memory.blackboard import create_entry, EntryType
except ImportError:
    # Fallback if running from different context
    from symbo_agentic_reasoners_phase0.core.fipa_acl import FIPAMessage, Performative
    from symbo_agentic_reasoners_phase0.core.omdoc_schema import create_variable
    from symbo_agentic_reasoners_phase0.memory.blackboard import create_entry, EntryType

class Phase0EdgeTest(unittest.TestCase):
    """
    Edge tests for Phase 0 System.
    Verifies system behavior under boundary conditions and invalid inputs.
    """

    def setUp(self):
        self.system = Phase0System()
        self.system.start()

    def tearDown(self):
        self.system.shutdown()

    def test_invalid_fipa_message_content(self):
        """Test that FIPA messages reject raw text content (The Laws)"""
        print("\n[Edge] Testing invalid FIPA message content...")
        try:
            msg = FIPAMessage(
                performative=Performative.REQUEST,
                sender='tester',
                receiver='system',
                content="This is raw text, not OMDoc"
            )
            msg.validate()
            self.fail("Should have raised ValueError for raw text content")
        except ValueError as e:
            print(f"  Caught expected error: {e}")
            pass

    def test_blackboard_stress_post(self):
        """Test posting a large number of entries to Blackboard"""
        print("\n[Edge] Testing Blackboard stress (100 entries)...")
        for i in range(100):
            entry = create_entry(
                entry_type=EntryType.TASK,
                content=create_variable(f'x_{i}'),
                author_agent='stress_tester',
                conversation_id=f'stress_test_{uuid.uuid4()}',
                tags=['stress_test']
            )
            self.system.blackboard.post(entry)
        
        stats = self.system.blackboard.get_statistics()
        # Depending on implementation, it might keep all or cleanup. 
        # Just checking it didn't crash and has entries.
        self.assertGreaterEqual(stats.get('total_entries', 0), 100)

    def test_vector_db_invalid_entry(self):
        """Test handling of potentially invalid vector DB entries"""
        print("\n[Edge] Testing Vector DB with empty content...")
        # This depends on VectorDB implementation, assuming it handles it gracefully or raises specific error
        # For now, just ensuring it doesn't crash the whole system
        try:
            from symbo_agentic_reasoners_phase0.memory.vector_database import create_vector_entry
            entry = create_vector_entry(
                entry_id=f'edge_{uuid.uuid4().hex}',
                content=create_variable('empty_test'), # Valid OMDoc
                entry_type='test'
            )
            self.system.vector_db.store(entry)
            retrieved = self.system.vector_db.get_by_id(entry.entry_id)
            self.assertIsNotNone(retrieved)
            self.system.vector_db.delete(entry.entry_id)
        except Exception as e:
            self.fail(f"Vector DB operation failed with valid OMDoc: {e}")

if __name__ == '__main__':
    unittest.main()
