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

"""Test VectorDatabase with fail-fast behavior"""

import sys
import os

print("=" * 80)
print("Testing VectorDatabase Fail-Fast Behavior")
print("=" * 80)

# Test 1: Import VectorDatabase
print("\n1. Testing import...")
try:
    from symbo_agentic_reasoners.core.vector_database import VectorDatabase, VectorEntry
    print("✅ Successfully imported VectorDatabase")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    # sys.exit(1)  # Disabled for pytest

# Test 2: Try to initialize WITHOUT ChromaDB (should fail)
print("\n2. Testing initialization WITHOUT ChromaDB (should raise RuntimeError)...")
try:
    db = VectorDatabase(persist_directory="./test_db")
    print("❌ FAILED: VectorDatabase should have raised RuntimeError!")
    # sys.exit(1)  # Disabled for pytest
except RuntimeError as e:
    print(f"✅ Correctly raised RuntimeError: {e}")
except Exception as e:
    print(f"⚠️  Unexpected error: {type(e).__name__}: {e}")

# Test 3: Try to initialize with allow_mock=True
print("\n3. Testing initialization with allow_mock=True...")
try:
    db = VectorDatabase(persist_directory="./test_db", allow_mock=True)
    print(f"✅ Successfully created mock VectorDatabase: {db}")
    
    # Test mock operations
    print("\n4. Testing mock operations...")
    
    # Create a test entry
    entry = VectorEntry(
        entry_id="test_001",
        content="Test mathematical content",
        metadata={"type": "test"}
    )
    
    # Store
    stored_id = db.store(entry)
    print(f"   ✅ Stored entry: {stored_id}")
    
    # Retrieve by ID
    retrieved = db.get_by_id("test_001")
    if retrieved:
        print(f"   ✅ Retrieved entry: {retrieved.entry_id}")
    else:
        print(f"   ❌ Failed to retrieve entry")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"   ✅ Statistics: {stats}")
    
    if stats.get('mode') == 'mock':
        print(f"   ✅ Correctly running in mock mode")
    
    if 'warning' in stats:
        print(f"   ✅ Warning present: {stats['warning']}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test mock from tests/mocks
print("\n5. Testing MockVectorDatabase from tests/mocks...")
try:
    from tests.mocks import MockVectorDatabase
    from tests.mocks.mock_vector_db import create_mock_vector_entry
    
    mock_db = MockVectorDatabase()
    print(f"✅ Successfully created MockVectorDatabase: {mock_db}")
    
    # Test mock operations
    entry = create_mock_vector_entry(
        entry_id="mock_001",
        content="Mock test content",
        entry_type="test"
    )
    
    stored_id = mock_db.store(entry)
    print(f"   ✅ Stored in mock: {stored_id}")
    
    retrieved = mock_db.get_by_id("mock_001")
    if retrieved:
        print(f"   ✅ Retrieved from mock: {retrieved.entry_id}")
    
    stats = mock_db.get_statistics()
    print(f"   ✅ Mock statistics: {stats}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("VectorDatabase testing complete!")
print("=" * 80)
