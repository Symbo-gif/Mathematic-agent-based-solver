# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
Security Monitor Enhancement Tests
===================================

Phase 5 - Issues #9-12: Tests for all security monitor enhancements.

Test Coverage:
- Issue #9: Behavioral anomaly detection
- Issue #10: Threat pattern database
- Issue #11: Pattern threshold optimization
- Issue #12: Persistent audit logging
"""

import pytest
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile

from symbo_agentic_reasoners.infrastructure.hardening.security_monitor import (
    BehavioralAnomalyDetector,
    ThreatPatternDatabase,
    PatternThresholdOptimizer,
    PersistentAuditLogger
)


class TestBehavioralAnomalyDetector:
    """Test BehavioralAnomalyDetector class (Issue #9)."""

    def test_detector_initialization(self):
        """Test detector initializes correctly."""
        detector = BehavioralAnomalyDetector()
        assert detector.anomalies_detected == 0
        assert len(detector._agent_profiles) == 0

    def test_detects_action_spike(self):
        """Test detection of action frequency spikes."""
        detector = BehavioralAnomalyDetector()

        # Simulate 25 identical actions in rapid succession
        for _ in range(25):
            anomalies = detector.detect_anomalies('agent_001', 'read', 'file.txt')

        # Should detect spike after threshold
        assert 'action_frequency_spike' in anomalies

    def test_detects_unusual_resource(self):
        """Test detection of unusual resource access."""
        detector = BehavioralAnomalyDetector()

        # Establish normal pattern
        for i in range(15):
            detector.detect_anomalies('agent_001', 'read', 'normal_file.txt')

        # Access new resource
        anomalies = detector.detect_anomalies('agent_001', 'read', 'sensitive_file.txt')

        # Should detect unusual resource
        assert 'unusual_resource_access' in anomalies

    def test_tracks_multiple_agents(self):
        """Test detector tracks multiple agents separately."""
        detector = BehavioralAnomalyDetector()

        detector.detect_anomalies('agent_001', 'read', 'file1.txt')
        detector.detect_anomalies('agent_002', 'write', 'file2.txt')

        assert 'agent_001' in detector._agent_profiles
        assert 'agent_002' in detector._agent_profiles
        assert len(detector._agent_profiles) == 2


class TestThreatPatternDatabase:
    """Test ThreatPatternDatabase class (Issue #10)."""

    def test_database_initialization(self):
        """Test database initializes and creates directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/threat_patterns.json"
            db = ThreatPatternDatabase(db_path=db_path)

            assert db.db_path.exists()

    def test_save_and_query_pattern(self):
        """Test saving and querying patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/threat_patterns.json"
            db = ThreatPatternDatabase(db_path=db_path)

            # Save pattern
            pattern = {
                'alert_type': 'rate_limit_exceeded',
                'agent_id': 'agent_001',
                'details': 'Too many requests'
            }
            db.save_pattern(pattern)

            # Query
            matches = db.query_similar('rate_limit_exceeded')

            assert len(matches) == 1
            assert matches[0]['agent_id'] == 'agent_001'

    def test_persistence_across_instances(self):
        """Test patterns persist across database instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/threat_patterns.json"

            # First instance - save pattern
            db1 = ThreatPatternDatabase(db_path=db_path)
            db1.save_pattern({'alert_type': 'test', 'data': 'value'})

            # Second instance - should load pattern
            db2 = ThreatPatternDatabase(db_path=db_path)
            matches = db2.query_similar('test')

            assert len(matches) == 1


class TestPatternThresholdOptimizer:
    """Test PatternThresholdOptimizer class (Issue #11)."""

    def test_optimizer_initialization(self):
        """Test optimizer initializes with default thresholds."""
        optimizer = PatternThresholdOptimizer()

        assert optimizer.get_threshold('rate_limit') == 100
        assert optimizer.get_threshold('message_size') == 1_000_000

    def test_optimize_thresholds_with_data(self):
        """Test threshold optimization with historical data."""
        optimizer = PatternThresholdOptimizer()

        # Historical data: values and whether they were true positives
        historical_data = [
            {'alert_type': 'rate_limit', 'value': 50, 'was_true_positive': False},
            {'alert_type': 'rate_limit', 'value': 80, 'was_true_positive': False},
            {'alert_type': 'rate_limit', 'value': 120, 'was_true_positive': True},
            {'alert_type': 'rate_limit', 'value': 150, 'was_true_positive': True},
            {'alert_type': 'rate_limit', 'value': 200, 'was_true_positive': True},
        ]

        # Duplicate data to meet minimum threshold
        historical_data = historical_data * 3

        # Optimize
        updated = optimizer.optimize_thresholds(historical_data)

        # Should have updated threshold
        assert 'rate_limit' in updated

    def test_insufficient_data_no_change(self):
        """Test thresholds unchanged with insufficient data."""
        optimizer = PatternThresholdOptimizer()
        original = optimizer.get_threshold('rate_limit')

        # Only 5 data points (need 10+)
        historical_data = [
            {'alert_type': 'rate_limit', 'value': i * 10, 'was_true_positive': True}
            for i in range(5)
        ]

        optimizer.optimize_thresholds(historical_data)

        # Should remain unchanged
        assert optimizer.get_threshold('rate_limit') == original


class TestPersistentAuditLogger:
    """Test PersistentAuditLogger class (Issue #12)."""

    def test_logger_initialization(self):
        """Test audit logger initializes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = PersistentAuditLogger(log_dir=tmpdir)

            assert logger.log_dir.exists()
            assert logger.logs_written == 0

    def test_log_access_attempt(self):
        """Test logging access attempts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = PersistentAuditLogger(log_dir=tmpdir)

            logger.log_access(
                agent_id='agent_001',
                resource='file.txt',
                action='read',
                allowed=True
            )

            assert logger.logs_written == 1

    def test_log_security_alert(self):
        """Test logging security alerts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = PersistentAuditLogger(log_dir=tmpdir)

            logger.log_alert(
                alert_type='unauthorized_access',
                severity='HIGH',
                agent_id='agent_001',
                message='Unauthorized access detected',
                recommended_action='Block agent'
            )

            assert logger.logs_written == 1

    def test_logs_persisted_to_file(self):
        """Test logs are written to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = PersistentAuditLogger(log_dir=tmpdir)

            logger.log_access('agent_001', 'resource', 'action', True)

            # Check log file exists
            log_files = list(Path(tmpdir).glob('*.log*'))
            assert len(log_files) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
