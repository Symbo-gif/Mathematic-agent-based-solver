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
PROTOCOL UPDATES - Phase 4 Integration
=======================================

This module provides integration components that connect Phase 4 functionality
(Conflict Resolution, Failure Analysis, Meta-Learning) with the Phase 1
Orchestrator and Phase 3 middleware.

PURPOSE:
-------
Enables the Orchestrator to:
1. Detect conflicts between agent results
2. Trigger appellate protocol when conflicts arise
3. Handle failure recovery through alternative paths
4. Update routing based on meta-learning insights

COMPONENTS:
----------
- OrchestratorPhase4Update: Extends orchestrator with Phase 4 capabilities
- ConflictDetector: Detects conflicts between agent results
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class ConflictDetector:
    """
    Conflict Detection System

    Analyzes results from multiple agents to detect conflicts that require
    resolution via the Appellate Protocol.

    CONFLICT TYPES:
    --------------
    1. Direct Contradiction: Agent A says "x=5", Agent B says "x=7"
    2. Numerical Tolerance: Results differ beyond acceptable tolerance
    3. Method Disagreement: Different methods produce different results
    """

    def __init__(self, tolerance: float = 1e-6):
        """
        Initialize Conflict Detector

        Args:
            tolerance: Numerical tolerance for floating point comparisons
        """
        self.tolerance = tolerance
        self.conflicts_detected = 0

    def check_results(self, results: List[Dict]) -> bool:
        """
        Check if results contain conflicts

        Args:
            results: List of result dictionaries from different agents
                Each should have 'result' and optionally 'agent_id'

        Returns:
            True if conflict detected, False otherwise
        """
        if len(results) < 2:
            return False

        # Extract result values
        values = []
        for r in results:
            result = r.get('result')
            if result is not None:
                values.append(result)

        if len(values) < 2:
            return False

        # Check for conflicts
        first = values[0]

        for other in values[1:]:
            if self._values_conflict(first, other):
                self.conflicts_detected += 1
                return True

        return False

    def _values_conflict(self, val1: Any, val2: Any) -> bool:
        """
        Determine if two values conflict

        Handles different types: numbers, strings, complex objects
        """
        # Same value - no conflict
        if val1 == val2:
            return False

        # Try numerical comparison with tolerance
        try:
            num1 = float(val1)
            num2 = float(val2)
            return abs(num1 - num2) > self.tolerance
        except (ValueError, TypeError):
            pass

        # String comparison
        if isinstance(val1, str) and isinstance(val2, str):
            # Normalize and compare
            return val1.strip().lower() != val2.strip().lower()

        # Different types or values - conflict
        return True

    def analyze_conflict(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Analyze conflict details

        Args:
            results: List of conflicting results

        Returns:
            Conflict analysis with details
        """
        return {
            'conflict_detected': True,
            'num_results': len(results),
            'results': results,
            'conflict_type': self._classify_conflict(results),
            'requires_resolution': True
        }

    def _classify_conflict(self, results: List[Dict]) -> str:
        """Classify the type of conflict"""
        # Simple classification based on result types
        result_types = set()
        for r in results:
            result = r.get('result')
            if result is not None:
                result_types.add(type(result).__name__)

        if len(result_types) > 1:
            return 'TYPE_MISMATCH'

        # Check if numerical
        try:
            values = [float(r.get('result')) for r in results if r.get('result') is not None]
            if values:
                return 'NUMERICAL_DISAGREEMENT'
        except (ValueError, TypeError):
            pass

        return 'VALUE_DISAGREEMENT'


class OrchestratorPhase4Update:
    """
    Phase 4 Integration for Orchestrator

    Extends the Main Orchestrator with Phase 4 capabilities:
    - Conflict detection and resolution
    - Failure recovery
    - Meta-learning integration
    - Adaptive routing

    USAGE:
    -----
    This class wraps an existing orchestrator and adds Phase 4 functionality.

    Example:
        orchestrator = MainOrchestrator(...)
        phase4_update = OrchestratorPhase4Update(
            orchestrator=orchestrator,
            conflict_resolution_team=conflict_team,
            failure_analysis_team=failure_team,
            meta_learning_team=meta_team
        )
    """

    def __init__(
        self,
        orchestrator,
        conflict_resolution_team=None,
        failure_analysis_team=None,
        meta_learning_team=None
    ):
        """
        Initialize Phase 4 integration

        Args:
            orchestrator: Main Orchestrator instance
            conflict_resolution_team: Conflict Resolution Team instance
            failure_analysis_team: Failure Analysis Team instance
            meta_learning_team: Meta-Learning Team instance
        """
        self.orchestrator = orchestrator
        self.conflict_resolution_team = conflict_resolution_team
        self.failure_analysis_team = failure_analysis_team
        self.meta_learning_team = meta_learning_team

        # Conflict detector
        self.conflict_detector = ConflictDetector()

        # Appellate protocol state
        self.appellate_active = True
        self.appellate_invocations = 0

        # Statistics
        self.conflicts_resolved = 0
        self.failures_recovered = 0
        self.routing_updates = 0

        logger.info("Phase 4 integration initialized for orchestrator")

    def process_with_conflict_detection(self, problem: Any, agents: List[str]) -> Dict:
        """
        Process problem with automatic conflict detection

        Delegates to multiple agents and checks for conflicts.
        If conflict detected, triggers appellate protocol.

        Args:
            problem: Problem to solve
            agents: List of agent IDs to consult

        Returns:
            Result dictionary with conflict resolution if needed
        """
        # Collect results from agents
        results = []
        for agent_id in agents:
            try:
                result = self._invoke_agent(agent_id, problem)
                results.append({
                    'agent_id': agent_id,
                    'result': result.get('result'),
                    'method_used': result.get('method'),
                    'confidence': result.get('confidence', 0.5)
                })
            except Exception as e:
                logger.warning(f"Agent {agent_id} failed: {e}")
                # Handle failure via failure analysis team
                if self.failure_analysis_team:
                    self._handle_agent_failure(agent_id, problem, str(e))

        # Check for conflicts
        if self.conflict_detector.check_results(results):
            return self._resolve_conflict(problem, results)

        # No conflict - return best result
        return self._select_best_result(results)

    def _invoke_agent(self, agent_id: str, problem: Any) -> Dict:
        """
        Invoke an agent to solve a problem

        This is a placeholder - actual implementation would delegate
        to the orchestrator's agent invocation mechanism.
        """
        # In real implementation, would use orchestrator's agent registry
        return {
            'result': None,
            'method': 'unknown',
            'confidence': 0.5
        }

    def _resolve_conflict(self, problem: Any, results: List[Dict]) -> Dict:
        """
        Resolve conflict using Conflict Resolution Team

        Triggers the Appellate Protocol (FMAD).
        """
        self.appellate_invocations += 1

        if not self.conflict_resolution_team:
            # No conflict resolution available - return first result
            logger.warning("Conflict detected but no resolution team available")
            return {'result': results[0] if results else None, 'status': 'CONFLICT_UNRESOLVED'}

        # Prepare conflict data
        conflict_data = {
            'subtask_id': f'conflict_{self.appellate_invocations}',
            'domain': getattr(problem, 'domain', 'unknown'),
            'results': results
        }

        # Invoke conflict resolution
        try:
            ruling = self.conflict_resolution_team.resolve_conflict(conflict_data)
            self.conflicts_resolved += 1

            return {
                'result': ruling.winner_result if hasattr(ruling, 'winner_result') else None,
                'status': 'CONFLICT_RESOLVED',
                'ruling': ruling,
                'original_results': results
            }
        except Exception as e:
            logger.error(f"Conflict resolution failed: {e}")
            return {'result': results[0] if results else None, 'status': 'RESOLUTION_FAILED'}

    def _select_best_result(self, results: List[Dict]) -> Dict:
        """
        Select best result when no conflict exists

        Uses confidence scores and other heuristics.
        """
        if not results:
            return {'result': None, 'status': 'NO_RESULTS'}

        # Sort by confidence
        sorted_results = sorted(
            results,
            key=lambda r: r.get('confidence', 0),
            reverse=True
        )

        best = sorted_results[0]
        return {
            'result': best.get('result'),
            'status': 'SUCCESS',
            'agent_id': best.get('agent_id'),
            'method': best.get('method'),
            'confidence': best.get('confidence')
        }

    def _handle_agent_failure(self, agent_id: str, problem: Any, error: str):
        """
        Handle agent failure via Failure Analysis Team

        Triggers failure analysis and alternative path generation.
        """
        if not self.failure_analysis_team:
            return

        failure_data = {
            'error_message': error,
            'agent_id': agent_id,
            'step': 'problem_solving',
            'conversation_id': getattr(problem, 'conversation_id', 'unknown')
        }

        try:
            recovery = self.failure_analysis_team.handle_failure(failure_data)
            if recovery.get('recovery_plan'):
                self.failures_recovered += 1
                logger.info(f"Generated recovery plan for {agent_id} failure")
        except Exception as e:
            logger.error(f"Failure analysis failed: {e}")

    def update_routing_from_meta_learning(self):
        """
        Update orchestrator routing based on meta-learning insights

        Called periodically to incorporate learned routing preferences.
        """
        if not self.meta_learning_team:
            return

        try:
            # Trigger batch optimization
            results = self.meta_learning_team.run_batch_optimization()

            # Update routing
            self.routing_updates += 1

            logger.info(
                f"Routing updated: {results.get('tables_updated', 0)} tables, "
                f"{results.get('insights_generated', 0)} insights"
            )

        except Exception as e:
            logger.error(f"Meta-learning update failed: {e}")

    def get_team_recommendation(self, problem_context: Dict) -> Dict:
        """
        Get optimal team configuration for a problem

        Delegates to Meta-Learning Team for adaptive team sizing.
        """
        if not self.meta_learning_team:
            return {'team_size': 6, 'complexity_level': 'STANDARD'}

        try:
            return self.meta_learning_team.get_team_recommendation(problem_context)
        except Exception as e:
            logger.error(f"Team recommendation failed: {e}")
            return {'team_size': 6, 'complexity_level': 'STANDARD'}

    def accept_result(self, result: Any) -> Any:
        """
        Accept and process a result

        Placeholder for result acceptance logic.
        """
        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get Phase 4 integration statistics"""
        return {
            'appellate_invocations': self.appellate_invocations,
            'conflicts_resolved': self.conflicts_resolved,
            'failures_recovered': self.failures_recovered,
            'routing_updates': self.routing_updates,
            'conflicts_detected': self.conflict_detector.conflicts_detected
        }


# ===========================================================================
# MODULE TEST
# ===========================================================================

if __name__ == "__main__":
    """Test Protocol Updates"""
    print("=" * 80)
    print("PHASE 4: PROTOCOL UPDATES TEST")
    print("=" * 80)
    print()

    # Test ConflictDetector
    print("TEST 1: Conflict Detection")
    print("-" * 40)

    detector = ConflictDetector()

    # No conflict
    results_same = [
        {'agent_id': 'a1', 'result': 'x^2'},
        {'agent_id': 'a2', 'result': 'x^2'}
    ]
    print(f"Same results: Conflict = {detector.check_results(results_same)}")

    # Conflict
    results_diff = [
        {'agent_id': 'a1', 'result': 'x^2'},
        {'agent_id': 'a2', 'result': 'x^2 + 1'}
    ]
    print(f"Different results: Conflict = {detector.check_results(results_diff)}")

    # Numerical tolerance
    results_close = [
        {'agent_id': 'a1', 'result': 3.14159265},
        {'agent_id': 'a2', 'result': 3.14159266}
    ]
    print(f"Close numbers: Conflict = {detector.check_results(results_close)}")
    print()

    # Test OrchestratorPhase4Update
    print("TEST 2: Orchestrator Integration")
    print("-" * 40)

    class MockOrchestrator:
        def accept_result(self, r):
            """Perform accept result operation.

            Args:
            r: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.accept_result(...)
            """
            """Perform accept result operation.

            Args:
            r: Description needed

            Returns:
            Result of the operation

            Example:
            >>> result = obj.accept_result(...)
            """
            return r

    update = OrchestratorPhase4Update(
        orchestrator=MockOrchestrator()
    )

    print(f"Appellate active: {update.appellate_active}")
    print(f"Statistics: {update.get_statistics()}")
    print()

    print("=" * 80)
    print("PROTOCOL UPDATES TEST COMPLETE")
    print("=" * 80)
