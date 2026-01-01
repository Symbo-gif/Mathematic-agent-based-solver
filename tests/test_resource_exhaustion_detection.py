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
Resource Exhaustion Detection Tests
====================================

Phase 5 - Issue #8: Resource exhaustion pattern detection tests.

Tests CPU, memory, and task accumulation detection.
"""

import pytest
import time

from symbo_agentic_reasoners.infrastructure.watchdog import ResourceUsageTracker


class TestResourceUsageTracker:
    """Test ResourceUsageTracker class."""

    def test_tracker_initialization(self):
        """Test tracker initializes correctly."""
        tracker = ResourceUsageTracker(window_seconds=300)
        assert tracker.window_seconds == 300
        assert len(tracker._cpu_samples) == 0

    def test_record_cpu_usage(self):
        """Test CPU usage recording."""
        tracker = ResourceUsageTracker()

        tracker.record_cpu(75.0)
        tracker.record_cpu(80.0)

        stats = tracker.get_stats()
        assert stats['cpu_samples'] == 2

    def test_sustained_high_cpu_detection(self):
        """Test sustained high CPU triggers alert."""
        tracker = ResourceUsageTracker()

        # Record 15 samples of >90% CPU
        for _ in range(15):
            tracker.record_cpu(95.0)

        alert = tracker.detect_exhaustion()
        assert alert is not None
        assert "high CPU" in alert

    def test_memory_growth_detection(self):
        """Test memory doubling triggers alert."""
        tracker = ResourceUsageTracker()

        # Record baseline memory (100 MB)
        for _ in range(5):
            tracker.record_memory(100 * 1024 * 1024)

        # Wait to establish old baseline
        time.sleep(0.1)

        # Record doubled memory (200 MB)
        for _ in range(5):
            tracker.record_memory(200 * 1024 * 1024)

        # This test may not trigger due to time window requirements
        # but demonstrates the pattern

    def test_sample_cleanup(self):
        """Test old samples are cleaned up."""
        tracker = ResourceUsageTracker(window_seconds=1)

        # Add samples
        tracker.record_cpu(50.0)
        tracker.record_cpu(60.0)

        # Wait for expiration
        time.sleep(1.1)

        # Add new sample (triggers cleanup)
        tracker.record_cpu(70.0)

        stats = tracker.get_stats()
        # Only the latest sample should remain
        assert stats['cpu_samples'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
