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
LEARNING ENHANCEMENT TEAM - Curriculum Specialist (Tier 3)
===========================================================

Implements curriculum learning for progressive difficulty scheduling.
Selects problems at appropriate difficulty levels and adapts based
on learning success/failure rates.

CURRICULUM LEARNING:
-------------------
1. Start with simple problems (difficulty ~0.3)
2. Track success/failure streaks
3. Advance difficulty after consistent success (10+ in a row)
4. Retreat difficulty after repeated failures (5+ in a row)
5. Gradually progress to expert-level problems

DIFFICULTY ADAPTATION:
---------------------
- Success streak >= 10: Increase difficulty by 0.05
- Failure streak >= 5: Decrease difficulty by 0.05
- Difficulty range: [0.1, 1.0]
- Window for selection: current_difficulty +/- 0.15

REFERENCE:
---------
- Plan: lexical-leaping-tower.md Phase 3 Priority 7
"""

import random
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

from . import CurriculumState, ComplexityScore

logger = logging.getLogger('symbo_agentic_reasoners.learning.curriculum')


class CurriculumSpecialist(BDIAgent):
    """
    Curriculum Specialist - Tier 3

    Implements curriculum learning with progressive difficulty scheduling.
    Selects appropriate problems and adapts difficulty based on performance.

    ROLE:
    ----
    1. Select problems at current difficulty level
    2. Track success/failure to adjust difficulty
    3. Ensure smooth progression from easy to hard
    4. Prevent both overwhelming and under-challenging

    ADAPTATION STRATEGY:
    -------------------
    - Consecutive successes → increase difficulty
    - Consecutive failures → decrease difficulty
    - Mixed results → maintain current level

    Example:
        >>> curriculum = CurriculumSpecialist()
        >>> batch = curriculum.next_batch(problems, batch_size=32)
        >>> # After learning...
        >>> curriculum.update(success=True)
    """

    # Configuration
    DEFAULT_DIFFICULTY = 0.3        # Starting difficulty
    MIN_DIFFICULTY = 0.1            # Minimum difficulty
    MAX_DIFFICULTY = 1.0            # Maximum difficulty
    DIFFICULTY_WINDOW = 0.15        # Selection window (+/-)
    DIFFICULTY_STEP = 0.05          # Step size for adjustments
    SUCCESS_THRESHOLD = 10          # Successes to advance
    FAILURE_THRESHOLD = 5           # Failures to retreat

    def __init__(
        self,
        agent_id: str = 'curriculum_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        initial_difficulty: float = 0.3,
        complexity_scorer: Optional[Any] = None
    ):
        """
        Initialize Curriculum Specialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
            initial_difficulty: Starting difficulty level (0.0-1.0)
            complexity_scorer: ComplexityScorerSpecialist for scoring problems
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard
        self.complexity_scorer = complexity_scorer

        # Curriculum state
        self.state = CurriculumState(
            current_difficulty=initial_difficulty,
            success_streak=0,
            failure_streak=0,
            total_attempts=0,
            difficulty_history=[]
        )

        # Statistics
        self.batches_selected = 0
        self.problems_processed = 0
        self.total_successes = 0
        self.total_failures = 0

        # Domain-specific tracking
        self.domain_progress: Dict[str, CurriculumState] = defaultdict(
            lambda: CurriculumState(current_difficulty=initial_difficulty)
        )

        # BDI state
        self.beliefs: Dict[str, Any] = {
            'learning_rate': 0.0,
            'plateau_detected': False,
            'domain_imbalance': False
        }

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Curriculum Specialist initialized at difficulty {initial_difficulty}")

    def _register_services(self) -> None:
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            agent_id=self.agent_id,
            service_type='learning.curriculum',
            description='Progressive difficulty scheduling for learning',
            capabilities=['next_batch', 'update', 'get_state', 'analyze']
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered with DF")

    def next_batch(
        self,
        problems: List[Dict[str, Any]],
        batch_size: int = 32,
        domain: str = None
    ) -> Dict[str, Any]:
        """
        Select next batch of problems at current difficulty.

        Args:
            problems: List of problem dicts (must have 'complexity' or 'problem')
            batch_size: Number of problems to select
            domain: Optional domain filter

        Returns:
            Dict with 'batch', 'difficulty', 'avg_complexity'
        """
        self.batches_selected += 1

        # Get appropriate difficulty for domain
        if domain:
            state = self.domain_progress[domain]
            current_diff = state.current_difficulty
        else:
            current_diff = self.state.current_difficulty

        # Ensure problems have complexity scores
        scored_problems = self._ensure_scored(problems)

        # Filter by domain if specified
        if domain:
            scored_problems = [p for p in scored_problems if p.get('domain') == domain]

        # Select problems within difficulty window
        window = self.DIFFICULTY_WINDOW
        min_diff = max(0.0, current_diff - window)
        max_diff = min(1.0, current_diff + window)

        # Filter by difficulty window
        filtered = [
            p for p in scored_problems
            if min_diff <= p.get('complexity', 0.5) <= max_diff
        ]

        # If not enough problems in window, expand selection
        if len(filtered) < batch_size:
            # Sort by distance from target difficulty
            sorted_problems = sorted(
                scored_problems,
                key=lambda p: abs(p.get('complexity', 0.5) - current_diff)
            )
            filtered = sorted_problems[:batch_size]

        # Random sample from filtered
        if len(filtered) > batch_size:
            batch = random.sample(filtered, batch_size)
        else:
            batch = filtered

        # Calculate average complexity
        if batch:
            avg_complexity = sum(p.get('complexity', 0.5) for p in batch) / len(batch)
        else:
            avg_complexity = current_diff

        self.problems_processed += len(batch)

        return {
            'batch': batch,
            'batch_size': len(batch),
            'target_difficulty': current_diff,
            'difficulty_window': (min_diff, max_diff),
            'avg_complexity': avg_complexity,
            'domain': domain
        }

    def _ensure_scored(self, problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure all problems have complexity scores."""
        result = []

        for p in problems:
            if 'complexity' not in p:
                if self.complexity_scorer:
                    # Use scorer to get complexity
                    score = self.complexity_scorer.score(
                        problem=p.get('problem', ''),
                        answer=p.get('answer', ''),
                        domain=p.get('domain', 'unknown')
                    )
                    p = dict(p)  # Copy
                    p['complexity'] = score.score
                else:
                    # Estimate based on problem length
                    problem_text = p.get('problem', '')
                    p = dict(p)
                    p['complexity'] = min(1.0, len(problem_text) / 200)

            result.append(p)

        return result

    def update(
        self,
        success: bool,
        domain: str = None
    ) -> Dict[str, Any]:
        """
        Update curriculum based on learning outcome.

        Args:
            success: Whether learning was successful
            domain: Problem domain (for domain-specific tracking)

        Returns:
            Updated state information
        """
        # Update global state
        self._update_state(self.state, success)
        self.state.total_attempts += 1

        # Update domain-specific state
        if domain:
            domain_state = self.domain_progress[domain]
            self._update_state(domain_state, success)
            domain_state.total_attempts += 1

        # Track overall stats
        if success:
            self.total_successes += 1
        else:
            self.total_failures += 1

        return self.get_state(domain)

    def _update_state(self, state: CurriculumState, success: bool) -> None:
        """Update a curriculum state based on outcome."""
        old_difficulty = state.current_difficulty

        if success:
            state.success_streak += 1
            state.failure_streak = 0

            # Advance difficulty after threshold
            if state.success_streak >= self.SUCCESS_THRESHOLD:
                state.current_difficulty = min(
                    self.MAX_DIFFICULTY,
                    state.current_difficulty + self.DIFFICULTY_STEP
                )
                state.success_streak = 0  # Reset streak

        else:
            state.failure_streak += 1
            state.success_streak = 0

            # Retreat difficulty after threshold
            if state.failure_streak >= self.FAILURE_THRESHOLD:
                state.current_difficulty = max(
                    self.MIN_DIFFICULTY,
                    state.current_difficulty - self.DIFFICULTY_STEP
                )
                state.failure_streak = 0  # Reset streak

        # Record history if difficulty changed
        if old_difficulty != state.current_difficulty:
            state.difficulty_history.append({
                'old': old_difficulty,
                'new': state.current_difficulty,
                'success': success,
                'timestamp': datetime.now().isoformat()
            })

            # Limit history size
            if len(state.difficulty_history) > 100:
                state.difficulty_history = state.difficulty_history[-50:]

    def get_state(self, domain: str = None) -> Dict[str, Any]:
        """
        Get current curriculum state.

        Args:
            domain: Optional domain to get domain-specific state

        Returns:
            Current state information
        """
        if domain:
            state = self.domain_progress[domain]
            prefix = f'{domain}_'
        else:
            state = self.state
            prefix = ''

        return {
            f'{prefix}current_difficulty': state.current_difficulty,
            f'{prefix}success_streak': state.success_streak,
            f'{prefix}failure_streak': state.failure_streak,
            f'{prefix}total_attempts': state.total_attempts,
            f'{prefix}recent_changes': state.difficulty_history[-5:] if state.difficulty_history else []
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get curriculum statistics."""
        # Calculate success rate
        total = self.total_successes + self.total_failures
        success_rate = self.total_successes / total if total > 0 else 0.0

        # Domain stats
        domain_stats = {}
        for domain, state in self.domain_progress.items():
            domain_stats[domain] = {
                'difficulty': state.current_difficulty,
                'attempts': state.total_attempts
            }

        return {
            'current_difficulty': self.state.current_difficulty,
            'success_streak': self.state.success_streak,
            'failure_streak': self.state.failure_streak,
            'total_attempts': self.state.total_attempts,
            'batches_selected': self.batches_selected,
            'problems_processed': self.problems_processed,
            'total_successes': self.total_successes,
            'total_failures': self.total_failures,
            'success_rate': success_rate,
            'domain_progress': domain_stats,
            'difficulty_changes': len(self.state.difficulty_history)
        }

    def analyze_progress(self) -> Dict[str, Any]:
        """
        Analyze learning progress and generate insights.

        Returns:
            Analysis with progress metrics and recommendations
        """
        stats = self.get_stats()

        # Calculate progress metrics
        if self.state.difficulty_history:
            initial_diff = self.state.difficulty_history[0].get('old', self.DEFAULT_DIFFICULTY)
            current_diff = self.state.current_difficulty
            progress = current_diff - initial_diff
        else:
            progress = 0.0

        # Detect plateau (no difficulty change in many attempts)
        recent_attempts = self.state.total_attempts % 100
        recent_changes = len([h for h in self.state.difficulty_history[-10:]
                             if 'new' in h])
        plateau = recent_attempts > 50 and recent_changes == 0

        # Detect domain imbalance
        domain_diffs = [s.current_difficulty for s in self.domain_progress.values()]
        if domain_diffs:
            domain_variance = max(domain_diffs) - min(domain_diffs)
            domain_imbalance = domain_variance > 0.3
        else:
            domain_imbalance = False

        # Generate recommendations
        recommendations = self._generate_recommendations(
            stats, progress, plateau, domain_imbalance
        )

        return {
            'current_difficulty': self.state.current_difficulty,
            'progress': progress,
            'success_rate': stats['success_rate'],
            'plateau_detected': plateau,
            'domain_imbalance': domain_imbalance,
            'domains_tracked': len(self.domain_progress),
            'total_difficulty_changes': len(self.state.difficulty_history),
            'recommendations': recommendations
        }

    def _generate_recommendations(
        self,
        stats: Dict,
        progress: float,
        plateau: bool,
        domain_imbalance: bool
    ) -> List[str]:
        """Generate curriculum recommendations."""
        recommendations = []

        if plateau:
            recommendations.append(
                "Learning plateau detected. Consider adjusting thresholds or "
                "introducing more varied problem types."
            )

        if domain_imbalance:
            recommendations.append(
                "Significant domain imbalance detected. Some domains are progressing "
                "much faster than others. Consider targeted practice."
            )

        if stats['success_rate'] > 0.9:
            recommendations.append(
                "Very high success rate. Could increase difficulty faster to "
                "challenge the learner more."
            )

        if stats['success_rate'] < 0.5:
            recommendations.append(
                "Low success rate. Consider slowing progression or providing "
                "more foundational problems."
            )

        if progress < 0.1 and stats['total_attempts'] > 100:
            recommendations.append(
                "Minimal difficulty progression after many attempts. May need "
                "intervention or different problem types."
            )

        if self.state.current_difficulty > 0.9:
            recommendations.append(
                "Approaching maximum difficulty. Learner is performing at expert level."
            )

        return recommendations

    def reset(self, domain: str = None) -> Dict[str, Any]:
        """
        Reset curriculum to initial state.

        Args:
            domain: Optional domain to reset (None = reset global)

        Returns:
            New state after reset
        """
        if domain:
            self.domain_progress[domain] = CurriculumState(
                current_difficulty=self.DEFAULT_DIFFICULTY
            )
            logger.info(f"Reset curriculum for domain: {domain}")
        else:
            self.state = CurriculumState(
                current_difficulty=self.DEFAULT_DIFFICULTY
            )
            logger.info("Reset global curriculum")

        return self.get_state(domain)

    def set_difficulty(
        self,
        difficulty: float,
        domain: str = None
    ) -> Dict[str, Any]:
        """
        Manually set difficulty level.

        Args:
            difficulty: New difficulty (0.0-1.0)
            domain: Optional domain to set

        Returns:
            Updated state
        """
        difficulty = max(self.MIN_DIFFICULTY, min(self.MAX_DIFFICULTY, difficulty))

        if domain:
            old_diff = self.domain_progress[domain].current_difficulty
            self.domain_progress[domain].current_difficulty = difficulty
        else:
            old_diff = self.state.current_difficulty
            self.state.current_difficulty = difficulty

        logger.info(f"Manually set difficulty: {old_diff} -> {difficulty}")

        return self.get_state(domain)

    # BDI Agent methods
    def update_beliefs(self, percept: Dict[str, Any] = None) -> None:
        """Update beliefs based on current state."""
        total = self.total_successes + self.total_failures
        if total > 0:
            self.beliefs['learning_rate'] = self.total_successes / total

        # Check for plateau
        analysis = self.analyze_progress()
        self.beliefs['plateau_detected'] = analysis['plateau_detected']
        self.beliefs['domain_imbalance'] = analysis['domain_imbalance']

    def deliberate(self) -> Optional[Intention]:
        """Deliberate on current beliefs."""
        if self.beliefs.get('plateau_detected', False):
            return Intention(
                plan_id='break_plateau',
                steps=['analyze_failures', 'adjust_thresholds', 'introduce_variety'],
                target_desire='continuous_progress'
            )

        if self.beliefs.get('domain_imbalance', False):
            return Intention(
                plan_id='balance_domains',
                steps=['identify_lagging', 'focus_practice', 'rebalance'],
                target_desire='balanced_learning'
            )

        return None

    def execute_step(self) -> bool:
        """Execute one step of agent processing."""
        if self.blackboard:
            # Would check for pending curriculum tasks
            pass
        return False

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the supervisor.

        Args:
            task_entry: Task with 'action' and relevant data

        Returns:
            Processing result
        """
        action = task_entry.get('action', 'get_state')

        if action == 'next_batch':
            return self.next_batch(
                problems=task_entry.get('problems', []),
                batch_size=task_entry.get('batch_size', 32),
                domain=task_entry.get('domain')
            )

        elif action == 'update':
            return self.update(
                success=task_entry.get('success', True),
                domain=task_entry.get('domain')
            )

        elif action == 'get_state':
            return self.get_state(task_entry.get('domain'))

        elif action == 'get_stats':
            return self.get_stats()

        elif action == 'analyze':
            return self.analyze_progress()

        elif action == 'reset':
            return self.reset(task_entry.get('domain'))

        elif action == 'set_difficulty':
            return self.set_difficulty(
                difficulty=task_entry.get('difficulty', 0.5),
                domain=task_entry.get('domain')
            )

        else:
            return {'error': f'Unknown action: {action}'}
