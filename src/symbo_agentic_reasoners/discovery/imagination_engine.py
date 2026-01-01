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
Imagination Engine - Autonomous Background Mathematical Exploration
=====================================================================

The Imagination Engine provides autonomous mathematical exploration when the
system is idle (no user tasks to process). It continuously:

1. Generates novel mathematical problems across all domains
2. Solves them using the solver engine
3. Records interesting discoveries and patterns
4. Learns which mathematical areas are most fruitful
5. Builds a corpus of mathematical knowledge and intuition

This gives SYMBO_AGENTIC_REASONERS "mathematical imagination" - it explores
mathematics autonomously, discovering patterns and building expertise even
when no user is interacting with the system.

Architecture:
- IdleDetector: Monitors system activity to detect idle periods
- ExplorationScheduler: Manages exploration priorities and resource usage
- KnowledgeIntegrator: Feeds discoveries back into the knowledge base
- ImaginationEngine: Coordinates all components

Integration:
    # In main system
    from symbo_agentic_reasoners.discovery.imagination_engine import ImaginationEngine

    imagination = ImaginationEngine(solver_engine)
    imagination.start()  # Begins background exploration

    # System processes user requests normally...
    # During idle periods, imagination explores autonomously

    imagination.stop()  # Clean shutdown
"""

import threading
import time
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty

from symbo_agentic_reasoners.discovery.curiosity_engine import (
    CuriosityEngine, ExplorationResult, ExplorationCategory, InterestLevel,
    ProblemGenerator, InterestScorer
)
from symbo_agentic_reasoners.infrastructure.watchdog import (
    run_with_timeout, TimeoutError as WatchdogTimeoutError
)

logger = logging.getLogger('symbo_agentic_reasoners.imagination')


class SystemState(Enum):
    """Current state of the system"""
    IDLE = 'idle'           # No active tasks, can explore
    BUSY = 'busy'           # Processing user tasks
    EXPLORING = 'exploring' # Actively exploring
    PAUSED = 'paused'       # Exploration paused
    STOPPED = 'stopped'     # Engine stopped


@dataclass
class ExplorationPriority:
    """Priority settings for exploration categories"""
    category: ExplorationCategory
    weight: float = 1.0           # Relative exploration weight
    min_interval_seconds: float = 0  # Minimum time between explorations
    last_explored: Optional[datetime] = None
    success_rate: float = 0.5     # Adaptive success rate
    discovery_rate: float = 0.0   # Rate of interesting discoveries


@dataclass
class ImaginationStats:
    """Statistics for the imagination engine"""
    total_explorations: int = 0
    successful_explorations: int = 0
    interesting_discoveries: int = 0
    remarkable_discoveries: int = 0
    total_idle_time_seconds: float = 0
    total_exploration_time_seconds: float = 0
    explorations_by_category: Dict[str, int] = field(default_factory=dict)
    discoveries_by_category: Dict[str, int] = field(default_factory=dict)
    session_start: Optional[datetime] = None
    last_discovery: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'total_explorations': self.total_explorations,
            'successful_explorations': self.successful_explorations,
            'success_rate': self.successful_explorations / max(1, self.total_explorations) * 100,
            'interesting_discoveries': self.interesting_discoveries,
            'remarkable_discoveries': self.remarkable_discoveries,
            'discovery_rate': self.interesting_discoveries / max(1, self.total_explorations) * 100,
            'total_idle_time_seconds': round(self.total_idle_time_seconds, 1),
            'total_exploration_time_seconds': round(self.total_exploration_time_seconds, 1),
            'efficiency': round(self.total_exploration_time_seconds / max(1, self.total_idle_time_seconds) * 100, 1),
            'explorations_by_category': self.explorations_by_category,
            'discoveries_by_category': self.discoveries_by_category,
            'session_start': self.session_start.isoformat() if self.session_start else None,
            'last_discovery': self.last_discovery.isoformat() if self.last_discovery else None
        }


class IdleDetector:
    """
    Detects when the system is idle and available for exploration.

    Monitors:
    - Time since last user request
    - Current system load
    - Active task queue
    """

    def __init__(self, idle_threshold_seconds: float = 5.0):
        """
        Args:
            idle_threshold_seconds: Seconds of inactivity before considered idle
        """
        self.idle_threshold = idle_threshold_seconds
        self._last_activity = datetime.now()
        self._active_tasks = 0
        self._lock = threading.Lock()

    def record_activity(self):
        """Record that user activity occurred"""
        with self._lock:
            self._last_activity = datetime.now()

    def begin_task(self):
        """Record that a task has started"""
        with self._lock:
            self._active_tasks += 1
            self._last_activity = datetime.now()

    def end_task(self):
        """Record that a task has ended"""
        with self._lock:
            self._active_tasks = max(0, self._active_tasks - 1)

    def is_idle(self) -> bool:
        """Check if system is currently idle"""
        with self._lock:
            if self._active_tasks > 0:
                return False
            idle_duration = (datetime.now() - self._last_activity).total_seconds()
            return idle_duration >= self.idle_threshold

    def get_idle_duration(self) -> float:
        """Get current idle duration in seconds"""
        with self._lock:
            if self._active_tasks > 0:
                return 0.0
            return (datetime.now() - self._last_activity).total_seconds()


class ExplorationScheduler:
    """
    Schedules exploration activities based on priorities and resource constraints.

    Implements adaptive exploration that:
    - Prioritizes categories with high discovery rates
    - Balances exploration vs exploitation
    - Respects resource constraints
    """

    def __init__(self):
        self.priorities: Dict[ExplorationCategory, ExplorationPriority] = {}
        self._initialize_priorities()

    def _initialize_priorities(self):
        """Initialize default priorities for all categories"""
        for category in ExplorationCategory:
            self.priorities[category] = ExplorationPriority(category=category)

    def select_category(self) -> ExplorationCategory:
        """Select next category to explore based on priorities"""
        import random

        # Calculate weighted probabilities
        weights = []
        categories = []

        for category, priority in self.priorities.items():
            # Boost weight based on discovery rate
            effective_weight = priority.weight * (1 + priority.discovery_rate)

            # Reduce weight if recently explored
            if priority.last_explored:
                time_since = (datetime.now() - priority.last_explored).total_seconds()
                if time_since < priority.min_interval_seconds:
                    effective_weight *= 0.1  # Heavily reduce

            weights.append(effective_weight)
            categories.append(category)

        # Normalize and select
        total = sum(weights)
        if total == 0:
            return random.choice(list(ExplorationCategory))

        r = random.random() * total
        cumulative = 0
        for category, weight in zip(categories, weights):
            cumulative += weight
            if r <= cumulative:
                return category

        return categories[-1]

    def record_exploration(self, category: ExplorationCategory,
                          success: bool, interesting: bool):
        """Record exploration result to update priorities"""
        priority = self.priorities[category]
        priority.last_explored = datetime.now()

        # Update success rate (exponential moving average)
        alpha = 0.1
        priority.success_rate = (1 - alpha) * priority.success_rate + alpha * (1.0 if success else 0.0)

        # Update discovery rate
        if success:
            priority.discovery_rate = (1 - alpha) * priority.discovery_rate + alpha * (1.0 if interesting else 0.0)


class ImaginationEngine:
    """
    Main Imagination Engine - Autonomous Mathematical Exploration

    Runs in the background, exploring mathematics when the system is idle.
    Integrates with the solver engine and knowledge management systems.

    Usage:
        solver = SolverEngine()
        imagination = ImaginationEngine(solver)
        imagination.start()

        # ... system operates normally ...
        # Imagination explores during idle periods

        # Check discoveries
        discoveries = imagination.get_discoveries()

        imagination.stop()
    """

    def __init__(
        self,
        solver,
        idle_threshold: float = 5.0,
        exploration_interval: float = 1.0,
        max_exploration_time: float = 30.0,
        save_dir: Optional[Path] = None,
        on_discovery: Optional[Callable[[ExplorationResult], None]] = None
    ):
        """
        Initialize the Imagination Engine.

        Args:
            solver: SolverEngine instance for solving generated problems
            idle_threshold: Seconds of inactivity before exploring
            exploration_interval: Seconds between exploration attempts
            max_exploration_time: Max seconds per exploration attempt
            save_dir: Directory to save discoveries
            on_discovery: Callback when interesting discovery is made
        """
        self.solver = solver
        self.save_dir = save_dir or Path("data/imagination")
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # Core components
        self.curiosity = CuriosityEngine(solver, save_dir=self.save_dir / "curiosity")
        self.idle_detector = IdleDetector(idle_threshold)
        self.scheduler = ExplorationScheduler()

        # Configuration
        self.exploration_interval = exploration_interval
        self.max_exploration_time = max_exploration_time
        self.on_discovery = on_discovery

        # State
        self._state = SystemState.STOPPED
        self._state_lock = threading.Lock()
        self._exploration_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Statistics
        self.stats = ImaginationStats()

        # Discovery log
        self._discovery_log = self.save_dir / "imagination_discoveries.jsonl"

        logger.info("ImaginationEngine initialized")

    @property
    def state(self) -> SystemState:
        """Get current engine state"""
        with self._state_lock:
            return self._state

    def _set_state(self, state: SystemState):
        """Set engine state"""
        with self._state_lock:
            old_state = self._state
            self._state = state
            logger.debug(f"Imagination state: {old_state.value} -> {state.value}")

    def start(self):
        """Start the imagination engine background exploration"""
        if self.state != SystemState.STOPPED:
            logger.warning("ImaginationEngine already running")
            return

        self._stop_event.clear()
        self._set_state(SystemState.IDLE)
        self.stats.session_start = datetime.now()

        self._exploration_thread = threading.Thread(
            target=self._exploration_loop,
            daemon=True,
            name="Imagination-Explorer"
        )
        self._exploration_thread.start()

        logger.info("ImaginationEngine started - autonomous exploration active")

    def stop(self):
        """Stop the imagination engine"""
        if self.state == SystemState.STOPPED:
            return

        self._stop_event.set()
        self._set_state(SystemState.STOPPED)

        if self._exploration_thread:
            self._exploration_thread.join(timeout=5.0)

        # Save final stats
        self._save_stats()

        logger.info("ImaginationEngine stopped")

    def pause(self):
        """Pause exploration (e.g., when resources needed elsewhere)"""
        if self.state in [SystemState.IDLE, SystemState.EXPLORING]:
            self._set_state(SystemState.PAUSED)
            logger.info("ImaginationEngine paused")

    def resume(self):
        """Resume exploration after pause"""
        if self.state == SystemState.PAUSED:
            self._set_state(SystemState.IDLE)
            logger.info("ImaginationEngine resumed")

    def notify_activity(self):
        """Notify that user activity occurred (stops current exploration)"""
        self.idle_detector.record_activity()
        if self.state == SystemState.EXPLORING:
            self._set_state(SystemState.BUSY)

    def notify_task_start(self):
        """Notify that a user task is starting"""
        self.idle_detector.begin_task()
        self._set_state(SystemState.BUSY)

    def notify_task_end(self):
        """Notify that a user task has ended"""
        self.idle_detector.end_task()
        if self.idle_detector.is_idle() and self.state == SystemState.BUSY:
            self._set_state(SystemState.IDLE)

    def _exploration_loop(self):
        """Main exploration loop running in background thread"""
        logger.info("Exploration loop started")

        while not self._stop_event.is_set():
            try:
                # Check if we should explore
                if self.state == SystemState.PAUSED:
                    time.sleep(self.exploration_interval)
                    continue

                if not self.idle_detector.is_idle():
                    self._set_state(SystemState.BUSY)
                    time.sleep(self.exploration_interval)
                    continue

                # Track idle time
                idle_start = time.time()

                # We're idle - explore!
                self._set_state(SystemState.EXPLORING)

                try:
                    result = self._explore_one()

                    if result:
                        self._process_result(result)

                except Exception as e:
                    logger.error(f"Exploration error: {e}")

                # Track times
                exploration_time = time.time() - idle_start
                self.stats.total_exploration_time_seconds += exploration_time
                self.stats.total_idle_time_seconds += self.idle_detector.get_idle_duration()

                # Return to idle state
                if self.state == SystemState.EXPLORING:
                    self._set_state(SystemState.IDLE)

                # Wait before next exploration
                time.sleep(self.exploration_interval)

            except Exception as e:
                logger.error(f"Exploration loop error: {e}")
                time.sleep(self.exploration_interval)

        logger.info("Exploration loop ended")

    def _explore_one(self) -> Optional[ExplorationResult]:
        """Execute one exploration with timeout protection"""
        # Select category
        category = self.scheduler.select_category()

        try:
            # Run exploration with timeout
            result = run_with_timeout(
                self.curiosity.explore_one,
                self.max_exploration_time,
                category,
                raise_on_timeout=False,
                default=None
            )

            return result

        except Exception as e:
            logger.debug(f"Exploration failed: {e}")
            return None

    def _process_result(self, result: ExplorationResult):
        """Process an exploration result"""
        self.stats.total_explorations += 1

        # Update category stats
        cat_name = result.category.value
        self.stats.explorations_by_category[cat_name] = \
            self.stats.explorations_by_category.get(cat_name, 0) + 1

        if result.success:
            self.stats.successful_explorations += 1

        # Check if interesting
        is_interesting = result.interest_level.value >= InterestLevel.INTERESTING.value
        is_remarkable = result.interest_level.value >= InterestLevel.REMARKABLE.value

        if is_interesting:
            self.stats.interesting_discoveries += 1
            self.stats.discoveries_by_category[cat_name] = \
                self.stats.discoveries_by_category.get(cat_name, 0) + 1
            self.stats.last_discovery = datetime.now()

            # Log discovery
            self._log_discovery(result)

            # Callback
            if self.on_discovery:
                try:
                    self.on_discovery(result)
                except Exception as e:
                    logger.error(f"Discovery callback error: {e}")

        if is_remarkable:
            self.stats.remarkable_discoveries += 1
            logger.info(f"REMARKABLE DISCOVERY: {result.problem} -> {result.solution}")

        # Update scheduler
        self.scheduler.record_exploration(
            result.category,
            result.success,
            is_interesting
        )

    def _log_discovery(self, result: ExplorationResult):
        """Log a discovery to file"""
        try:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'source': 'imagination',
                **result.to_dict()
            }
            with open(self._discovery_log, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Could not log discovery: {e}")

    def _save_stats(self):
        """Save current statistics to file"""
        try:
            stats_file = self.save_dir / "imagination_stats.json"
            with open(stats_file, 'w') as f:
                json.dump(self.stats.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Could not save stats: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get imagination engine statistics"""
        return {
            'state': self.state.value,
            'curiosity': self.curiosity.get_statistics(),
            'imagination': self.stats.to_dict(),
            'scheduler': {
                cat.value: {
                    'success_rate': p.success_rate,
                    'discovery_rate': p.discovery_rate
                }
                for cat, p in self.scheduler.priorities.items()
            }
        }

    def get_discoveries(
        self,
        min_interest: InterestLevel = InterestLevel.NOTABLE,
        category: Optional[ExplorationCategory] = None,
        limit: int = 100
    ) -> List[ExplorationResult]:
        """Get discoveries from this session"""
        return self.curiosity.get_discoveries(min_interest, category, limit)

    def get_best_discoveries(self, limit: int = 10) -> List[ExplorationResult]:
        """Get the best discoveries from exploration"""
        all_discoveries = self.get_discoveries(InterestLevel.INTERESTING)
        sorted_discoveries = sorted(
            all_discoveries,
            key=lambda d: d.interest_level.value,
            reverse=True
        )
        return sorted_discoveries[:limit]


# Singleton instance
_imagination_engine: Optional[ImaginationEngine] = None
_engine_lock = threading.Lock()


def get_imagination_engine(solver=None) -> Optional[ImaginationEngine]:
    """Get or create the global ImaginationEngine instance"""
    global _imagination_engine

    with _engine_lock:
        if _imagination_engine is None and solver is not None:
            _imagination_engine = ImaginationEngine(solver)
        return _imagination_engine


def start_imagination(solver) -> ImaginationEngine:
    """Convenience function to start the imagination engine"""
    engine = get_imagination_engine(solver)
    if engine is None:
        engine = ImaginationEngine(solver)
        with _engine_lock:
            global _imagination_engine
            _imagination_engine = engine
    engine.start()
    return engine


def stop_imagination():
    """Convenience function to stop the imagination engine"""
    engine = get_imagination_engine()
    if engine:
        engine.stop()


if __name__ == "__main__":
    """Demo of the Imagination Engine"""
    print("=" * 70)
    print("IMAGINATION ENGINE DEMO")
    print("=" * 70)
    print()

    # Import solver
    from symbo_agentic_reasoners.core.solver_engine import SolverEngine

    # Create solver and imagination engine
    solver = SolverEngine(enable_timeouts=True)
    imagination = ImaginationEngine(
        solver,
        idle_threshold=1.0,  # Quick for demo
        exploration_interval=0.5,
        max_exploration_time=10.0,
        on_discovery=lambda r: print(f"  [!] Discovery: {r.problem[:50]}... -> {str(r.solution)[:30]}...")
    )

    print("Starting imagination engine...")
    imagination.start()

    print(f"State: {imagination.state.value}")
    print()
    print("Letting imagination explore for 30 seconds...")
    print()

    # Let it explore
    try:
        for i in range(30):
            time.sleep(1)
            if i % 5 == 0:
                stats = imagination.get_statistics()
                print(f"  [{i}s] Explorations: {stats['imagination']['total_explorations']}, "
                      f"Discoveries: {stats['imagination']['interesting_discoveries']}")
    except KeyboardInterrupt:
        print("\nInterrupted by user")

    print()
    print("Stopping imagination engine...")
    imagination.stop()

    print()
    print("Final Statistics:")
    print(json.dumps(imagination.get_statistics(), indent=2))

    print()
    print("Best Discoveries:")
    for d in imagination.get_best_discoveries(5):
        print(f"  [{d.interest_level.name}] {d.problem} = {d.solution}")
        if d.notes:
            print(f"      Note: {d.notes}")
