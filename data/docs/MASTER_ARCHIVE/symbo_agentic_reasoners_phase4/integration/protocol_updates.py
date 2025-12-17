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
PHASE 4 INTEGRATION - Protocol Updates
======================================

System Integration: Wiring Phase 4 Teams into Existing Hierarchy

PURPOSE:
-------
Phase 4 teams do not operate in isolation - they must be wired into the
existing Phase 1/2/3 infrastructure through two critical protocol updates
to the Main Orchestrator.

PROTOCOLS:
---------
1. Appellate Protocol (4.1)
   - Update the Main Orchestrator's logic
   - It is no longer allowed to accept a result immediately
   - MANDATORY: Check Blackboard for CONFLICT_FLAG before returning any result
   - If CONFLICT_FLAG == true: Delegate to Debate Moderator before proceeding

2. Post-Mortem Protocol (4.2)
   - Update system lifecycle to trigger optimization after every session
   - After every SESSION_END event, Meta-Learning Team runs batch analysis
   - Updates routing weights for continuous evolutionary improvement

OUTCOME:
-------
The system is slightly smarter at the start of Day N+1 than it was at Day N,
implementing continuous evolutionary improvement.

REFERENCE:
---------
Phase_4_Build_Order_Breakdown.md: Step 4 (System Integration)
"""

import sys
import os
import logging
from typing import Dict, Optional, Any, Callable
from datetime import datetime
import time
import threading

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Get module logger
logger = logging.getLogger('symbo_agentic_reasoners.phase4.protocol_updates')


class ConflictResolutionError(Exception):
    """
    Raised when conflict cannot be resolved within timeout

    This exception indicates that the Conflict Resolution Team
    was unable to reach a ruling within the allowed time.
    """
    pass


class OrchestratorPhase4Update:
    """
    Updates to Main Orchestrator for Phase 4 Integration

    This class wraps an existing Orchestrator and installs the two
    critical Phase 4 protocols:

    1. Appellate Protocol: Mandatory conflict check before result acceptance
    2. Post-Mortem Protocol: Trigger optimization after every session

    USAGE:
    -----
    # Wrap existing orchestrator
    update = OrchestratorPhase4Update(
        orchestrator=main_orchestrator,
        blackboard=blackboard,
        debate_moderator=conflict_team.debate_moderator,
        meta_learning_team=meta_team
    )

    # Protocols are now installed and active

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Step 4
    """

    def __init__(self, orchestrator=None, blackboard=None,
                 debate_moderator=None, meta_learning_team=None,
                 conflict_resolution_team=None):
        """
        Initialize Phase 4 protocol updates

        Args:
            orchestrator: Main Orchestrator instance to update
            blackboard: Phase 0 Blackboard instance
            debate_moderator: Debate Moderator agent from Conflict Resolution Team
            meta_learning_team: Meta-Learning Team coordinator
            conflict_resolution_team: Full Conflict Resolution Team (optional)
        """
        self.orchestrator = orchestrator
        self.blackboard = blackboard
        self.debate_moderator = debate_moderator
        self.meta_learning_team = meta_learning_team
        self.conflict_resolution_team = conflict_resolution_team
        self._lock = threading.RLock()

        # Protocol state
        self.appellate_active = False
        self.postmortem_active = False

        # Statistics
        self.conflict_checks = 0
        self.conflicts_detected = 0
        self.resolutions_completed = 0
        self.postmortem_triggers = 0
        self.optimization_runs = 0

        # Original methods (saved for restoration)
        self._original_accept_result = None

        # Install protocols
        if orchestrator:
            self._install_appellate_protocol()
        if blackboard:
            self._install_post_mortem_protocol()

        print("    [OK] Phase 4 Protocol Updates installed")

    def _install_appellate_protocol(self):
        """
        Protocol 4.1: Mandatory conflict check before result acceptance

        This protocol wraps the Orchestrator's accept_result method to
        enforce conflict checking before any result is accepted.

        BEHAVIOR:
        --------
        Before accepting any result:
        1. Check Blackboard for CONFLICT_FLAG with matching subtask_id
        2. If conflict exists, delegate to Debate Moderator
        3. Wait for resolution
        4. Return resolved result instead of original

        REFERENCE:
        ---------
        Phase_4_Build_Order_Breakdown.md: Protocol 4.1
        """
        # Check if orchestrator has accept_result method
        if not hasattr(self.orchestrator, 'accept_result'):
            # Create the method if it doesn't exist
            self.orchestrator.accept_result = lambda r: r
            self._original_accept_result = lambda r: r
        else:
            self._original_accept_result = self.orchestrator.accept_result

        # Create wrapped version
        def appellate_wrapped_accept(result: Dict) -> Dict:
            """Wrapped accept_result with conflict check"""
            with self._lock:
                self.conflict_checks += 1

                # MANDATORY: Check for conflict flag
                conflict_entry = self._check_for_conflict(result)

                if conflict_entry:
                    self.conflicts_detected += 1
                    print(f"    [APPELLATE] Conflict detected for subtask {result.get('subtask_id', 'unknown')}")

                    # DELEGATE to Conflict Resolution Team
                    try:
                        resolved = self._resolve_conflict(conflict_entry, result)
                        if resolved:
                            self.resolutions_completed += 1
                            return resolved
                        else:
                            raise ConflictResolutionError(
                                f"Failed to resolve conflict for {result.get('subtask_id')}"
                            )
                    except Exception as e:
                        raise ConflictResolutionError(str(e))

                # No conflict - proceed with original acceptance
                return self._original_accept_result(result)

        # Replace original method
        self.orchestrator.accept_result = appellate_wrapped_accept
        self.appellate_active = True
        print("      [+] Appellate Protocol installed")

    def _check_for_conflict(self, result: Dict) -> Optional[Dict]:
        """
        Check Blackboard for CONFLICT_FLAG

        Args:
            result: Result being accepted

        Returns:
            Conflict entry if found, None otherwise
        """
        if not self.blackboard:
            return None

        subtask_id = result.get('subtask_id', '')

        try:
            # Query blackboard for conflict flags
            entries = self.blackboard.query_entries(
                tags=['CONFLICT_FLAG']
            )

            for entry in entries:
                # Check if this conflict matches our subtask
                if hasattr(entry, 'metadata'):
                    entry_subtask = entry.metadata.get('subtask_id', '')
                    status = entry.metadata.get('status', '')

                    if entry_subtask == subtask_id and status == 'UNRESOLVED':
                        return {
                            'subtask_id': subtask_id,
                            'conflicting_results': entry.metadata.get('results', []),
                            'conversation_id': result.get('conversation_id', '')
                        }
        except Exception as e:
            logger.debug(f"Error checking conflict flag: {type(e).__name__}: {e}")

        return None

    def _resolve_conflict(self, conflict_entry: Dict, original_result: Dict,
                         timeout: int = 300) -> Optional[Dict]:
        """
        Resolve conflict through Conflict Resolution Team

        Args:
            conflict_entry: Detected conflict information
            original_result: Original result being accepted
            timeout: Maximum wait time in seconds

        Returns:
            Resolved result or None
        """
        if self.conflict_resolution_team:
            # Use full team for resolution
            ruling = self.conflict_resolution_team.resolve_conflict(
                conflict_entry, timeout=timeout
            )
            if ruling:
                return {
                    'result': ruling.winning_result,
                    'subtask_id': original_result.get('subtask_id'),
                    'conversation_id': original_result.get('conversation_id'),
                    'resolved_by': 'conflict_resolution_team',
                    'ruling_type': ruling.ruling_type,
                    'confidence': ruling.confidence
                }

        elif self.debate_moderator:
            # Use moderator only
            case_id = self.debate_moderator.on_conflict_detected(conflict_entry)

            # Wait for resolution
            resolution = self._wait_for_resolution(case_id, timeout)
            if resolution:
                return {
                    'result': resolution.get('accepted_result'),
                    'subtask_id': original_result.get('subtask_id'),
                    'conversation_id': original_result.get('conversation_id'),
                    'resolved_by': 'debate_moderator',
                    'case_id': case_id
                }

        return None

    def _wait_for_resolution(self, case_id: str, timeout: int = 300) -> Optional[Dict]:
        """Wait for conflict resolution from Blackboard"""
        if not self.blackboard:
            return None

        start = time.time()

        while time.time() - start < timeout:
            try:
                # Check for resolution
                entries = self.blackboard.query_entries(
                    tags=['WORKFLOW_UNFREEZE', case_id]
                )

                for entry in entries:
                    if hasattr(entry, 'metadata'):
                        return entry.metadata
            except Exception as e:
                logger.debug(f"Error polling for resolution: {e}")

            time.sleep(0.5)

        return None

    def _install_post_mortem_protocol(self):
        """
        Protocol 4.2: Trigger optimization after every session

        This protocol subscribes to SESSION_END events and triggers
        the Meta-Learning Team's batch optimization process.

        BEHAVIOR:
        --------
        1. Subscribe to SESSION_END events on Blackboard
        2. When session ends, trigger trace logging
        3. Schedule batch optimization for low-load periods

        OUTCOME:
        -------
        The system is slightly smarter at the start of Day N+1 than at Day N.

        REFERENCE:
        ---------
        Phase_4_Build_Order_Breakdown.md: Protocol 4.2
        """
        def on_session_end(entry):
            """Post-mortem hook for session completion"""
            with self._lock:
                self.postmortem_triggers += 1

            if hasattr(entry, 'metadata'):
                conversation_id = entry.metadata.get('conversation_id', '')

                # Let Performance Monitor complete the trace
                if self.meta_learning_team:
                    try:
                        self.meta_learning_team.log_session_end(conversation_id)
                    except Exception as e:
                        logger.debug(f"Meta learning session end logging failed: {e}")

                # Schedule batch optimization
                self._schedule_optimization(entry.metadata)

        try:
            self.blackboard.subscribe(
                agent_id='phase4_postmortem',
                tags=['SESSION_END'],
                callback=on_session_end
            )
            self.postmortem_active = True
            print("      [+] Post-Mortem Protocol installed")
        except Exception as e:
            print(f"      [!] Post-Mortem Protocol installation failed: {e}")

    def _schedule_optimization(self, event: Dict):
        """
        Schedule batch optimization

        Currently runs immediately; in production would batch
        and run during low-load periods.
        """
        # Post optimization trigger to Blackboard
        if self.blackboard:
            try:
                from symbo_agentic_reasoners_phase0.memory.blackboard import create_entry, EntryType
                entry = create_entry(
                    entry_type=EntryType.TASK,
                    content={
                        'session_id': event.get('conversation_id', ''),
                        'timestamp': datetime.now().isoformat(),
                        'priority': 'BATCH'
                    },
                    author_agent='phase4_postmortem',
                    conversation_id='optimization',
                    tags=['OPTIMIZATION_TRIGGER'],
                    metadata={
                        'entry_type': 'OPTIMIZATION_TRIGGER'
                    }
                )
                self.blackboard.post(entry)
            except Exception as e:
                logger.debug(f"Could not post optimization trigger: {e}")

    def run_batch_optimization(self) -> Dict:
        """
        Execute batch optimization (called by scheduler or manually)

        Returns:
            Optimization results
        """
        with self._lock:
            self.optimization_runs += 1

        if not self.meta_learning_team:
            return {'error': 'Meta-Learning Team not available'}

        # Run optimization
        results = self.meta_learning_team.run_batch_optimization()

        # Log insights
        insights = results.get('insights', [])
        if insights:
            print(f"    [POST-MORTEM] {len(insights)} pattern(s) discovered:")
            for insight in insights[:3]:  # Show top 3
                print(f"      - {insight.get('recommendation', '')}")

        return results

    def detect_and_flag_conflict(self, subtask_id: str, results: list,
                                conversation_id: str = '') -> bool:
        """
        Detect conflict and post CONFLICT_FLAG to Blackboard

        Utility method for detecting conflicts between agent results.

        Args:
            subtask_id: ID of the subtask with potential conflict
            results: List of results from different agents
            conversation_id: Conversation tracking ID

        Returns:
            True if conflict was detected and flagged
        """
        if len(results) < 2:
            return False

        # Check for conflicting results
        first_result = results[0].get('result')
        has_conflict = False

        for result in results[1:]:
            if result.get('result') != first_result:
                has_conflict = True
                break

        if has_conflict and self.blackboard:
            try:
                from symbo_agentic_reasoners_phase0.memory.blackboard import create_entry, EntryType
                entry = create_entry(
                    entry_type=EntryType.TASK,
                    content={
                        'subtask_id': subtask_id,
                        'results': results
                    },
                    author_agent='phase4_conflict_detector',
                    conversation_id=conversation_id,
                    tags=['CONFLICT_FLAG', subtask_id],
                    metadata={
                        'entry_type': 'CONFLICT_FLAG',
                        'subtask_id': subtask_id,
                        'status': 'UNRESOLVED',
                        'results': results
                    }
                )
                self.blackboard.post(entry)
                return True
            except Exception as e:
                logger.warning(f"Could not post conflict flag: {type(e).__name__}: {e}")

        return False

    def uninstall_protocols(self):
        """
        Uninstall Phase 4 protocols (for testing)

        Restores original Orchestrator behavior.
        """
        if self.orchestrator and self._original_accept_result:
            self.orchestrator.accept_result = self._original_accept_result
            self.appellate_active = False

        # Note: Cannot easily unsubscribe from Blackboard
        self.postmortem_active = False

    def get_statistics(self) -> Dict[str, Any]:
        """Get protocol statistics"""
        return {
            'appellate_protocol': {
                'active': self.appellate_active,
                'conflict_checks': self.conflict_checks,
                'conflicts_detected': self.conflicts_detected,
                'resolutions_completed': self.resolutions_completed
            },
            'postmortem_protocol': {
                'active': self.postmortem_active,
                'triggers': self.postmortem_triggers,
                'optimization_runs': self.optimization_runs
            }
        }


# ===========================================================================
# CONFLICT DETECTION HELPER
# ===========================================================================

class ConflictDetector:
    """
    Helper class for detecting conflicts between agent results

    Used by the system to identify when multiple agents produce
    different results for the same problem.
    """

    def __init__(self, blackboard=None, tolerance: float = 1e-10):
        """
        Initialize Conflict Detector

        Args:
            blackboard: Phase 0 Blackboard
            tolerance: Numerical tolerance for comparing results
        """
        self.blackboard = blackboard
        self.tolerance = tolerance
        self.conflicts_detected = 0

    def check_results(self, results: list) -> bool:
        """
        Check if a list of results contains conflicts

        Args:
            results: List of result dictionaries

        Returns:
            True if conflicting results detected
        """
        if len(results) < 2:
            return False

        first_result = results[0].get('result')

        for result in results[1:]:
            if not self._results_match(first_result, result.get('result')):
                self.conflicts_detected += 1
                return True

        return False

    def _results_match(self, r1, r2) -> bool:
        """
        Check if two results match (considering numerical tolerance)
        """
        if r1 == r2:
            return True

        # Try numerical comparison
        try:
            if isinstance(r1, (int, float)) and isinstance(r2, (int, float)):
                return abs(r1 - r2) < self.tolerance
        except (TypeError, ValueError):
            pass

        # String comparison (normalize whitespace)
        try:
            if isinstance(r1, str) and isinstance(r2, str):
                return r1.strip().lower() == r2.strip().lower()
        except (TypeError, AttributeError):
            pass

        return False

    def flag_conflict(self, subtask_id: str, results: list,
                     conversation_id: str = ''):
        """
        Post conflict flag to Blackboard
        """
        if not self.blackboard:
            return

        try:
            from symbo_agentic_reasoners_phase0.memory.blackboard import create_entry, EntryType
            entry = create_entry(
                entry_type=EntryType.TASK,
                content={'subtask_id': subtask_id, 'results': results},
                author_agent='conflict_detector',
                conversation_id=conversation_id,
                tags=['CONFLICT_FLAG', subtask_id],
                metadata={
                    'entry_type': 'CONFLICT_FLAG',
                    'subtask_id': subtask_id,
                    'status': 'UNRESOLVED',
                    'results': results
                }
            )
            self.blackboard.post(entry)
        except Exception as e:
            logger.warning(f"Could not flag conflict: {type(e).__name__}: {e}")


# ===========================================================================
# MODULE TEST
# ===========================================================================

if __name__ == "__main__":
    """Test Protocol Updates"""
    print("=" * 80)
    print("PHASE 4 - STEP 4: PROTOCOL UPDATES TEST")
    print("=" * 80)
    print()

    # Create mock orchestrator
    class MockOrchestrator:
        def __init__(self):
            self.results_accepted = 0

        def accept_result(self, result):
            self.results_accepted += 1
            return result

    orchestrator = MockOrchestrator()

    # Initialize protocol updates (without full infrastructure)
    print("Installing Protocol Updates...")
    update = OrchestratorPhase4Update(
        orchestrator=orchestrator,
        blackboard=None,  # No blackboard for basic test
        debate_moderator=None,
        meta_learning_team=None
    )
    print()

    # Test appellate protocol
    print("TEST: Appellate Protocol")
    print("-" * 40)

    result = orchestrator.accept_result({
        'result': 'x^2',
        'subtask_id': 'test_001'
    })
    print(f"  Result accepted: {result}")
    print(f"  Conflict checks: {update.conflict_checks}")
    print()

    # Test conflict detection
    print("TEST: Conflict Detection")
    print("-" * 40)

    detector = ConflictDetector()

    results_match = [
        {'agent_id': 'a1', 'result': 'x^2'},
        {'agent_id': 'a2', 'result': 'x^2'}
    ]
    print(f"  Same results conflict: {detector.check_results(results_match)}")

    results_conflict = [
        {'agent_id': 'a1', 'result': 'x^2'},
        {'agent_id': 'a2', 'result': 'x^2 + 1'}
    ]
    print(f"  Different results conflict: {detector.check_results(results_conflict)}")

    results_numerical = [
        {'agent_id': 'a1', 'result': 3.14159265},
        {'agent_id': 'a2', 'result': 3.14159266}
    ]
    print(f"  Numerical close: {detector.check_results(results_numerical)}")
    print()

    # Statistics
    print("PROTOCOL STATISTICS:")
    import json
    print(json.dumps(update.get_statistics(), indent=2))
    print()

    print("=" * 80)
    print("PROTOCOL UPDATES TEST COMPLETE")
    print("=" * 80)
