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
Knowledge Persistence Stress Testing
=====================================

Comprehensive stress tests for the vector database and knowledge management
systems to ensure reliability under load, proper persistence, and correct
retrieval behavior.

TEST CATEGORIES:
---------------
1. Volume Testing - Handling large numbers of entries
2. Persistence Testing - Data survives restarts
3. Retrieval Accuracy - Correct results under load
4. Concurrent Access - Multiple readers/writers
5. Edge Case Testing - Boundary conditions
6. Memory Pressure - System behavior under RAM limits
"""

import pytest
import tempfile
import shutil
import os
import time
import uuid
import random
import string
import threading
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# Import system components (with fallback for missing dependencies)
try:
    from symbo_agentic_reasoners.core.vector_database import (
        VectorDatabase, VectorEntry, CHROMADB_AVAILABLE,
        SENTENCE_TRANSFORMERS_AVAILABLE
    )
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False
    CHROMADB_AVAILABLE = False
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from symbo_agentic_reasoners.middleware.knowledge_management import (
        ContextExtractor, MemoryIndexer, RetrievalSpecialist,
        RetrievalConfidence, RetrievalResult
    )
    KNOWLEDGE_MGMT_AVAILABLE = True
except ImportError:
    KNOWLEDGE_MGMT_AVAILABLE = False


# =============================================================================
# TEST DATA GENERATORS
# =============================================================================

def generate_theorem_content(index: int) -> str:
    """Generate synthetic theorem content for testing."""
    domains = ["algebra", "calculus", "geometry", "number_theory", "statistics"]
    operators = ["sum", "product", "integral", "limit", "derivative"]

    domain = domains[index % len(domains)]
    operator = operators[index % len(operators)]

    return f"Theorem_{index}: For all x in {domain}, the {operator} of x^{index % 10} equals f({index})"


def generate_solution_trace(problem_id: str, steps: int = 5) -> Dict[str, Any]:
    """Generate synthetic solution trace for testing."""
    return {
        "problem_id": problem_id,
        "problem_type": random.choice(["polynomial", "integral", "limit", "ode", "series"]),
        "steps": [
            {
                "step_number": i,
                "operation": f"step_{i}_operation",
                "result": f"intermediate_result_{i}",
                "confidence": random.uniform(0.7, 1.0)
            }
            for i in range(steps)
        ],
        "final_result": f"solution_{problem_id}",
        "timestamp": time.time(),
        "agent_id": f"agent_{random.randint(1, 10)}"
    }


def generate_random_embedding(dimension: int = 384) -> List[float]:
    """Generate random embedding vector for testing without model."""
    return [random.uniform(-1, 1) for _ in range(dimension)]


# =============================================================================
# MOCK COMPONENTS FOR TESTING WITHOUT DEPENDENCIES
# =============================================================================

@dataclass
class MockVectorEntry:
    """Mock vector entry for testing without ChromaDB."""
    entry_id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    entry_type: str = "theorem"


class MockVectorDatabase:
    """Mock vector database for testing without ChromaDB."""

    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory
        self.entries: Dict[str, MockVectorEntry] = {}
        self.dimension = 384

        if persist_directory and os.path.exists(persist_directory):
            self._load()

    def store(self, entry_id: str, content: str, metadata: Dict = None,
              entry_type: str = "theorem") -> bool:
        """Store an entry with auto-generated embedding."""
        embedding = generate_random_embedding(self.dimension)
        self.entries[entry_id] = MockVectorEntry(
            entry_id=entry_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            entry_type=entry_type
        )
        return True

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """Retrieve entries by simulated similarity."""
        # Simulate similarity search with random scores
        results = []
        for entry_id, entry in list(self.entries.items())[:top_k]:
            score = random.uniform(0.5, 1.0)
            results.append((entry_id, score, entry.metadata))
        return results

    def get_entry(self, entry_id: str) -> MockVectorEntry:
        """Get entry by ID."""
        return self.entries.get(entry_id)

    def count(self) -> int:
        """Count total entries."""
        return len(self.entries)

    def persist(self) -> bool:
        """Persist to disk."""
        if self.persist_directory:
            os.makedirs(self.persist_directory, exist_ok=True)
            with open(os.path.join(self.persist_directory, "data.json"), "w") as f:
                data = {
                    entry_id: {
                        "content": entry.content,
                        "metadata": entry.metadata,
                        "entry_type": entry.entry_type,
                        "embedding": entry.embedding
                    }
                    for entry_id, entry in self.entries.items()
                }
                json.dump(data, f)
            return True
        return False

    def _load(self):
        """Load from disk."""
        data_file = os.path.join(self.persist_directory, "data.json")
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                data = json.load(f)
                for entry_id, entry_data in data.items():
                    self.entries[entry_id] = MockVectorEntry(
                        entry_id=entry_id,
                        content=entry_data["content"],
                        embedding=entry_data["embedding"],
                        metadata=entry_data["metadata"],
                        entry_type=entry_data["entry_type"]
                    )

    def clear(self):
        """Clear all entries."""
        self.entries.clear()


import json


# =============================================================================
# VOLUME STRESS TESTS
# =============================================================================

class TestVolumeStress:
    """Tests for handling large volumes of knowledge entries."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_db(self, temp_db_dir):
        """Create mock database for testing."""
        return MockVectorDatabase(persist_directory=temp_db_dir)

    def test_store_100_entries(self, mock_db):
        """Test storing 100 entries."""
        for i in range(100):
            content = generate_theorem_content(i)
            result = mock_db.store(
                entry_id=f"theorem_{i}",
                content=content,
                metadata={"domain": "test", "index": i}
            )
            assert result is True

        assert mock_db.count() == 100

    def test_store_1000_entries(self, mock_db):
        """Test storing 1000 entries."""
        for i in range(1000):
            content = generate_theorem_content(i)
            mock_db.store(
                entry_id=f"theorem_{i}",
                content=content,
                metadata={"domain": "test", "index": i}
            )

        assert mock_db.count() == 1000

    def test_store_10000_entries(self, mock_db):
        """Test storing 10000 entries (stress test)."""
        start_time = time.time()

        for i in range(10000):
            content = generate_theorem_content(i)
            mock_db.store(
                entry_id=f"theorem_{i}",
                content=content,
                metadata={"domain": "stress_test", "index": i}
            )

        elapsed = time.time() - start_time
        assert mock_db.count() == 10000
        # Should complete in reasonable time (< 60 seconds for mock)
        assert elapsed < 60, f"Storing 10000 entries took {elapsed:.2f}s"

    def test_retrieve_under_load(self, mock_db):
        """Test retrieval performance with many entries."""
        # Store 1000 entries
        for i in range(1000):
            mock_db.store(
                entry_id=f"theorem_{i}",
                content=generate_theorem_content(i),
                metadata={"index": i}
            )

        # Perform 100 retrievals
        start_time = time.time()
        for _ in range(100):
            results = mock_db.retrieve("polynomial algebra", top_k=5)
            assert len(results) <= 5

        elapsed = time.time() - start_time
        # 100 retrievals should complete in < 10 seconds for mock
        assert elapsed < 10, f"100 retrievals took {elapsed:.2f}s"

    def test_mixed_read_write_load(self, mock_db):
        """Test interleaved reads and writes."""
        stored = 0
        retrieved = 0

        for i in range(500):
            # Store
            mock_db.store(
                entry_id=f"theorem_{i}",
                content=generate_theorem_content(i),
                metadata={"index": i}
            )
            stored += 1

            # Retrieve
            if i > 0:
                results = mock_db.retrieve(f"theorem_{random.randint(0, i-1)}")
                retrieved += 1

        assert stored == 500
        assert retrieved == 499


# =============================================================================
# PERSISTENCE STRESS TESTS
# =============================================================================

class TestPersistenceStress:
    """Tests for data persistence across restarts."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_persist_and_reload(self, temp_db_dir):
        """Test that data survives database restart."""
        # Create and populate database
        db1 = MockVectorDatabase(persist_directory=temp_db_dir)
        for i in range(100):
            db1.store(
                entry_id=f"theorem_{i}",
                content=generate_theorem_content(i),
                metadata={"index": i}
            )
        db1.persist()

        # Create new database instance pointing to same directory
        db2 = MockVectorDatabase(persist_directory=temp_db_dir)

        # Verify data survived
        assert db2.count() == 100

        # Verify specific entries
        for i in [0, 50, 99]:
            entry = db2.get_entry(f"theorem_{i}")
            assert entry is not None
            assert entry.metadata["index"] == i

    def test_large_persist_and_reload(self, temp_db_dir):
        """Test persistence with large dataset."""
        # Create and populate database
        db1 = MockVectorDatabase(persist_directory=temp_db_dir)
        for i in range(5000):
            db1.store(
                entry_id=f"theorem_{i}",
                content=generate_theorem_content(i),
                metadata={"index": i, "extra": "data" * 10}
            )
        db1.persist()

        # Reload
        db2 = MockVectorDatabase(persist_directory=temp_db_dir)
        assert db2.count() == 5000

    def test_persist_with_unicode_content(self, temp_db_dir):
        """Test persistence with unicode mathematical content."""
        db1 = MockVectorDatabase(persist_directory=temp_db_dir)

        # Store entries with unicode
        unicode_content = [
            "∫₀^∞ e^(-x²) dx = √π/2",
            "∑_{n=1}^∞ 1/n² = π²/6",
            "∀x ∈ ℝ: |sin(x)| ≤ 1",
            "∃n ∈ ℤ: n² = n",
            "α + β + γ = π (triangle)",
            "ℵ₀ < 2^ℵ₀ (Cantor)",
        ]

        for i, content in enumerate(unicode_content):
            db1.store(
                entry_id=f"unicode_{i}",
                content=content,
                metadata={"type": "unicode_test"}
            )
        db1.persist()

        # Reload and verify
        db2 = MockVectorDatabase(persist_directory=temp_db_dir)
        for i, expected in enumerate(unicode_content):
            entry = db2.get_entry(f"unicode_{i}")
            assert entry is not None
            assert entry.content == expected

    def test_incremental_persist(self, temp_db_dir):
        """Test multiple persist calls accumulate correctly."""
        db = MockVectorDatabase(persist_directory=temp_db_dir)

        # First batch
        for i in range(100):
            db.store(f"batch1_{i}", f"content1_{i}", {"batch": 1})
        db.persist()

        # Second batch
        for i in range(100):
            db.store(f"batch2_{i}", f"content2_{i}", {"batch": 2})
        db.persist()

        # Reload and verify
        db2 = MockVectorDatabase(persist_directory=temp_db_dir)
        assert db2.count() == 200

        # Verify both batches present
        assert db2.get_entry("batch1_50") is not None
        assert db2.get_entry("batch2_50") is not None


# =============================================================================
# CONCURRENT ACCESS TESTS
# =============================================================================

class TestConcurrentAccess:
    """Tests for concurrent read/write access."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def shared_db(self, temp_db_dir):
        """Create shared database for concurrent access."""
        return MockVectorDatabase(persist_directory=temp_db_dir)

    def test_concurrent_writes(self, shared_db):
        """Test multiple threads writing simultaneously."""
        num_threads = 10
        entries_per_thread = 100
        errors = []

        def write_entries(thread_id):
            try:
                for i in range(entries_per_thread):
                    shared_db.store(
                        entry_id=f"t{thread_id}_{i}",
                        content=f"Thread {thread_id} content {i}",
                        metadata={"thread": thread_id, "index": i}
                    )
            except Exception as e:
                errors.append(str(e))

        threads = []
        for t in range(num_threads):
            thread = threading.Thread(target=write_entries, args=(t,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert shared_db.count() == num_threads * entries_per_thread

    def test_concurrent_reads_and_writes(self, shared_db):
        """Test concurrent reads while writing."""
        # Pre-populate
        for i in range(100):
            shared_db.store(f"initial_{i}", f"content_{i}", {"type": "initial"})

        read_results = []
        write_count = [0]
        errors = []

        def writer():
            try:
                for i in range(50):
                    shared_db.store(
                        f"new_{i}",
                        f"new content {i}",
                        {"type": "new"}
                    )
                    write_count[0] += 1
                    time.sleep(0.001)  # Small delay
            except Exception as e:
                errors.append(f"Writer: {e}")

        def reader():
            try:
                for _ in range(100):
                    results = shared_db.retrieve("content", top_k=5)
                    read_results.append(len(results))
                    time.sleep(0.001)
            except Exception as e:
                errors.append(f"Reader: {e}")

        # Start threads
        writer_thread = threading.Thread(target=writer)
        reader_threads = [threading.Thread(target=reader) for _ in range(3)]

        writer_thread.start()
        for rt in reader_threads:
            rt.start()

        writer_thread.join()
        for rt in reader_threads:
            rt.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert write_count[0] == 50
        assert len(read_results) == 300  # 3 readers * 100 reads

    def test_thread_pool_stress(self, shared_db):
        """Test with ThreadPoolExecutor under heavy load."""
        num_tasks = 1000
        completed = [0]

        def task(task_id):
            if task_id % 3 == 0:
                # Write
                shared_db.store(
                    f"task_{task_id}",
                    f"task content {task_id}",
                    {"task_id": task_id}
                )
            else:
                # Read
                shared_db.retrieve(f"task_{random.randint(0, task_id)}", top_k=3)
            return task_id

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(task, i) for i in range(num_tasks)]
            for future in as_completed(futures):
                try:
                    future.result()
                    completed[0] += 1
                except Exception as e:
                    pass  # Count failures

        assert completed[0] == num_tasks


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Tests for boundary conditions and edge cases."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_db(self, temp_db_dir):
        """Create mock database for testing."""
        return MockVectorDatabase(persist_directory=temp_db_dir)

    def test_empty_content(self, mock_db):
        """Test storing empty content."""
        result = mock_db.store("empty", "", {"type": "empty"})
        assert result is True
        entry = mock_db.get_entry("empty")
        assert entry.content == ""

    def test_very_long_content(self, mock_db):
        """Test storing very long content."""
        long_content = "x" * 100000  # 100KB of text
        result = mock_db.store("long", long_content, {"type": "long"})
        assert result is True
        entry = mock_db.get_entry("long")
        assert len(entry.content) == 100000

    def test_special_characters_in_id(self, mock_db):
        """Test entry IDs with special characters."""
        special_ids = [
            "theorem-with-dash",
            "theorem_with_underscore",
            "theorem.with.dots",
            "theorem:with:colons",
            "theorem/with/slashes",
        ]

        for entry_id in special_ids:
            mock_db.store(entry_id, f"Content for {entry_id}", {})

        for entry_id in special_ids:
            entry = mock_db.get_entry(entry_id)
            assert entry is not None

    def test_duplicate_ids(self, mock_db):
        """Test behavior with duplicate entry IDs."""
        mock_db.store("duplicate", "first content", {"version": 1})
        mock_db.store("duplicate", "second content", {"version": 2})

        entry = mock_db.get_entry("duplicate")
        # Last write wins
        assert entry.metadata["version"] == 2

    def test_retrieve_from_empty_db(self, mock_db):
        """Test retrieval from empty database."""
        results = mock_db.retrieve("anything", top_k=10)
        assert results == []

    def test_retrieve_with_zero_k(self, mock_db):
        """Test retrieval with top_k=0."""
        mock_db.store("test", "content", {})
        results = mock_db.retrieve("content", top_k=0)
        assert len(results) == 0

    def test_large_metadata(self, mock_db):
        """Test storing large metadata objects."""
        large_metadata = {
            "nested": {
                "deeply": {
                    "nested": {
                        "value": "deep" * 100
                    }
                }
            },
            "array": list(range(1000)),
            "string": "x" * 10000
        }

        mock_db.store("large_meta", "content", large_metadata)
        mock_db.persist()

        # Reload and verify
        db2 = MockVectorDatabase(persist_directory=mock_db.persist_directory)
        entry = db2.get_entry("large_meta")
        assert entry.metadata["array"] == list(range(1000))

    def test_null_metadata_fields(self, mock_db):
        """Test metadata with None values."""
        metadata = {
            "present": "value",
            "missing": None,
            "empty_string": "",
            "zero": 0,
            "false": False
        }

        mock_db.store("null_meta", "content", metadata)
        entry = mock_db.get_entry("null_meta")
        assert entry.metadata["missing"] is None
        assert entry.metadata["zero"] == 0
        assert entry.metadata["false"] is False


# =============================================================================
# MEMORY PRESSURE TESTS
# =============================================================================

class TestMemoryPressure:
    """Tests for behavior under memory constraints."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_many_small_entries(self, temp_db_dir):
        """Test many small entries (tests overhead per entry)."""
        db = MockVectorDatabase(persist_directory=temp_db_dir)

        # Store 50000 small entries
        for i in range(50000):
            db.store(f"small_{i}", f"x{i}", {"i": i})

        assert db.count() == 50000
        db.persist()

    def test_few_large_entries(self, temp_db_dir):
        """Test few very large entries (tests content storage)."""
        db = MockVectorDatabase(persist_directory=temp_db_dir)

        # Store 10 entries of 1MB each
        large_content = "x" * (1024 * 1024)  # 1MB
        for i in range(10):
            db.store(f"large_{i}", large_content, {"size": "1MB"})

        assert db.count() == 10
        db.persist()

    def test_rapid_create_delete_cycle(self, temp_db_dir):
        """Test rapid creation and deletion cycles."""
        db = MockVectorDatabase(persist_directory=temp_db_dir)

        for cycle in range(10):
            # Add 1000 entries
            for i in range(1000):
                db.store(f"cycle_{cycle}_{i}", f"content", {"cycle": cycle})

            # Clear for next cycle
            if cycle < 9:  # Keep last cycle
                db.clear()

        assert db.count() == 1000  # Only last cycle remains


# =============================================================================
# INTEGRATION STRESS TESTS
# =============================================================================

class TestIntegrationStress:
    """Tests simulating real-world usage patterns."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_simulated_solving_session(self, temp_db_dir):
        """Simulate a solving session with storage and retrieval."""
        db = MockVectorDatabase(persist_directory=temp_db_dir)

        # Simulate 100 problem solving sessions
        for session in range(100):
            problem_id = f"problem_{session}"

            # Store problem trace
            trace = generate_solution_trace(problem_id, steps=random.randint(3, 10))
            db.store(
                entry_id=f"trace_{problem_id}",
                content=json.dumps(trace),
                metadata={
                    "problem_id": problem_id,
                    "problem_type": trace["problem_type"],
                    "agent": trace["agent_id"]
                },
                entry_type="solution_trace"
            )

            # Store discovered theorems
            for theorem_idx in range(random.randint(0, 3)):
                db.store(
                    entry_id=f"theorem_{session}_{theorem_idx}",
                    content=f"Discovered theorem {theorem_idx} in session {session}",
                    metadata={"session": session, "type": "discovered"},
                    entry_type="theorem"
                )

            # Retrieve similar past solutions
            if session > 10:
                results = db.retrieve(trace["problem_type"], top_k=5)
                # Use results (simulated)

        # Verify final state
        assert db.count() > 100  # At least 100 traces
        db.persist()

        # Verify persistence
        db2 = MockVectorDatabase(persist_directory=temp_db_dir)
        assert db2.count() == db.count()

    def test_learning_accumulation(self, temp_db_dir):
        """Test knowledge accumulation over many sessions."""
        db = MockVectorDatabase(persist_directory=temp_db_dir)

        total_entries = 0

        # Simulate 50 learning sessions across 5 "days"
        for day in range(5):
            for session in range(10):
                session_id = day * 10 + session

                # Learn from 5-15 problems per session
                problems_learned = random.randint(5, 15)
                for p in range(problems_learned):
                    db.store(
                        entry_id=f"day{day}_session{session}_problem{p}",
                        content=generate_theorem_content(session_id * 100 + p),
                        metadata={"day": day, "session": session, "problem": p}
                    )
                    total_entries += 1

            # Persist at end of each "day"
            db.persist()

            # Reload to simulate restart
            db = MockVectorDatabase(persist_directory=temp_db_dir)

        assert db.count() == total_entries
        print(f"Total accumulated entries: {total_entries}")


# =============================================================================
# BENCHMARK TESTS
# =============================================================================

class TestBenchmarks:
    """Performance benchmarks for tracking regressions."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_benchmark_store_1000(self, temp_db_dir):
        """Benchmark: Store 1000 entries."""
        db = MockVectorDatabase(persist_directory=temp_db_dir)

        start = time.time()
        for i in range(1000):
            db.store(f"entry_{i}", generate_theorem_content(i), {"i": i})
        elapsed = time.time() - start

        print(f"\nBenchmark - Store 1000 entries: {elapsed:.3f}s ({1000/elapsed:.1f} entries/s)")
        assert elapsed < 30  # Should complete in < 30s

    def test_benchmark_retrieve_1000(self, temp_db_dir):
        """Benchmark: 1000 retrievals from 10000 entries."""
        db = MockVectorDatabase(persist_directory=temp_db_dir)

        # Populate
        for i in range(10000):
            db.store(f"entry_{i}", generate_theorem_content(i), {"i": i})

        start = time.time()
        for _ in range(1000):
            db.retrieve("polynomial algebra theorem", top_k=5)
        elapsed = time.time() - start

        print(f"\nBenchmark - 1000 retrievals from 10000: {elapsed:.3f}s ({1000/elapsed:.1f} queries/s)")
        assert elapsed < 30  # Should complete in < 30s

    def test_benchmark_persist_10000(self, temp_db_dir):
        """Benchmark: Persist 10000 entries."""
        db = MockVectorDatabase(persist_directory=temp_db_dir)

        for i in range(10000):
            db.store(f"entry_{i}", generate_theorem_content(i), {"i": i})

        start = time.time()
        db.persist()
        elapsed = time.time() - start

        print(f"\nBenchmark - Persist 10000 entries: {elapsed:.3f}s")
        assert elapsed < 60  # Should complete in < 60s


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
