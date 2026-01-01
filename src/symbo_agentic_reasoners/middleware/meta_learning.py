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
META-LEARNING TEAM - "The Optimizer"
=====================================

Phase 4 Step 3: AutoMaAS Pattern Implementation

PURPOSE:
-------
Construct a three-agent team that implements the AutoMaAS (Automated
Multi-Agent System) pattern - capturing process metadata from every
solution, analyzing efficiency patterns, and dynamically updating the
Orchestrator's routing tables.

WHY THIS MATTERS:
----------------
Without the Meta-Learning Team, the system solves the 1000th cubic equation
with the same trial-and-error randomness as the first. Phase 3's Knowledge
Management Team provides memory of *facts*, but the system lacks memory of
*process*. This team installs the "memory of process" that makes the system
smarter with every interaction.

AGENTS:
------
1. Performance Monitor: "Black Box Recorder" - logs solution traces
2. Agent Selector Optimizer: AutoMaAS logic - computes routing heuristics
3. Adaptive Dispatcher: Dynamic scaling controller

EXPECTED IMPACT:
---------------
- Optimizes cost-per-token by 10-15%
- Matches resource allocation to problem complexity
- Learns which agents succeed for which problem types

REFERENCE:
---------
- Phase_4_Build_Order_Breakdown.md: Step 3
- Phase 4 transforms this collection of agents into a Self-Correction Engine.md
"""

import sys
import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
from enum import Enum, auto
import threading
import uuid
import json
import math

# Add parent paths for imports
# Path manipulation removed - using package imports
# Path manipulation removed - using package imports

# Get module logger
logger = logging.getLogger('symbo_agentic_reasoners.phase4.meta_learning')


# ===========================================================================
# DATA CLASSES
# ===========================================================================

@dataclass
class SolutionTrace:
    """
    Performance metadata for a single solution

    This is the core data structure captured by the Performance Monitor.
    It focuses on HOW the solution was achieved, not WHAT the solution was.

    FIELDS:
    ------
    - trace_id: Unique trace identifier
    - problem_type: Classification from Structure Recognizer (e.g., 'integration')
    - agent_sequence: Ordered list of agents that touched the problem
    - time_taken_ms: Wall-clock time for complete solution
    - cpu_time_ms: CPU time per agent (approximate)
    - verification_status: Final status from Ax-Prover
    - token_count: Total tokens consumed
    - vram_peak_mb: Peak VRAM usage
    - success: Whether solution was verified correct
    - timestamp: When solution was completed

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 3.1 (Performance Monitor)
    """
    trace_id: str = field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:8]}")
    conversation_id: str = ""
    problem_type: str = "unknown"
    problem_complexity: str = "medium"  # low, medium, high
    agent_sequence: List[str] = field(default_factory=list)
    time_taken_ms: float = 0.0
    cpu_time_ms: float = 0.0
    agent_times: Dict[str, float] = field(default_factory=dict)
    verification_status: str = "UNKNOWN"  # VERIFIED, FAILED, PARTIAL
    token_count: int = 0
    vram_peak_mb: float = 0.0
    success: bool = False
    error_occurred: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'trace_id': self.trace_id,
            'conversation_id': self.conversation_id,
            'problem_type': self.problem_type,
            'problem_complexity': self.problem_complexity,
            'agent_sequence': self.agent_sequence,
            'time_taken_ms': self.time_taken_ms,
            'cpu_time_ms': self.cpu_time_ms,
            'agent_times': self.agent_times,
            'verification_status': self.verification_status,
            'token_count': self.token_count,
            'vram_peak_mb': self.vram_peak_mb,
            'success': self.success,
            'error_occurred': self.error_occurred,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class RoutingHeuristic:
    """
    Routing weight for an agent on a specific problem type

    Encodes learned preferences for agent selection.
    """
    agent_id: str
    problem_type: str
    weight: float  # Higher = prefer this agent
    success_rate: float
    avg_time_ms: float
    sample_size: int
    last_updated: datetime = field(default_factory=datetime.now)


class ComplexityLevel(Enum):
    """Problem complexity levels for team sizing"""
    SIMPLE = auto()      # Skeleton Crew (2-3 agents)
    STANDARD = auto()    # Standard Team (4-6 agents)
    COMPLEX = auto()     # Full Debate Team (10+ agents)


# ===========================================================================
# AGENT 3.1: THE PERFORMANCE MONITOR
# ===========================================================================

class PerformanceMonitor:
    """
    Agent 3.1: Black Box Recorder

    DIRECTIVE:
    ---------
    Implement a background agent that logs the "Trace" of every successful
    solution.

    DATA CAPTURED (Process Metadata):
    --------------------------------
    - Problem Type (classification from Structure Recognizer)
    - Agent Sequence Used (ordered list of agents that touched the problem)
    - Time Taken (wall-clock and CPU time per agent)
    - Final Verification Status (from Ax-Prover)
    - Resource Consumption (tokens, VRAM peaks, memory)

    CRITICAL NOTE:
    -------------
    This agent ignores the mathematics itself and focuses exclusively on
    the metadata of efficiency - HOW the solution was achieved, not WHAT
    the solution was.

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 3.1
    """

    def __init__(self, blackboard=None, vector_db=None):
        """
        Initialize Performance Monitor

        Args:
            blackboard: Phase 0 Blackboard for event subscription
            vector_db: Vector database for trace storage and retrieval
        """
        self.blackboard = blackboard
        self.vector_db = vector_db
        self._lock = threading.RLock()

        # Active traces by conversation
        self.active_traces: Dict[str, Dict] = {}

        # Completed traces (recent history)
        self.completed_traces: List[SolutionTrace] = []
        self.max_trace_history = 1000

        # Statistics
        self.traces_recorded = 0
        self.successful_traces = 0
        self.failed_traces = 0

        if self.blackboard:
            self._subscribe_to_events()

        print("    [OK] Performance Monitor Agent initialized")

    def _subscribe_to_events(self):
        """Subscribe to solution lifecycle events"""
        try:
            self.blackboard.subscribe(
                agent_id='performance_monitor_001',
                tags=['TASK_START'],
                callback=lambda e: self._on_event(e, 'TASK_START')
            )
            self.blackboard.subscribe(
                agent_id='performance_monitor_001',
                tags=['AGENT_INVOKED'],
                callback=lambda e: self._on_event(e, 'AGENT_INVOKED')
            )
            self.blackboard.subscribe(
                agent_id='performance_monitor_001',
                tags=['VERIFICATION_COMPLETE'],
                callback=lambda e: self._on_event(e, 'VERIFICATION_COMPLETE')
            )
            self.blackboard.subscribe(
                agent_id='performance_monitor_001',
                tags=['SESSION_END'],
                callback=lambda e: self._on_event(e, 'SESSION_END')
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to blackboard events: {type(e).__name__}: {e}")

    def _on_event(self, entry, event_type: str):
        """Handle Blackboard events"""
        metadata = getattr(entry, 'metadata', {})
        if event_type == 'TASK_START':
            self.on_task_start(metadata)
        elif event_type == 'AGENT_INVOKED':
            self.on_agent_invoked(metadata)
        elif event_type == 'VERIFICATION_COMPLETE':
            self.on_verification(metadata)
        elif event_type == 'SESSION_END':
            self.on_session_end(metadata)

    def on_task_start(self, event: Dict):
        """
        Initialize trace for new task

        Called when a new problem-solving task begins.
        """
        with self._lock:
            conversation_id = event.get('conversation_id', str(uuid.uuid4()))
            self.active_traces[conversation_id] = {
                'trace_id': f"trace_{conversation_id[:8]}",
                'conversation_id': conversation_id,
                'problem_type': event.get('problem_type', 'unknown'),
                'problem_complexity': event.get('complexity', 'medium'),
                'agent_sequence': [],
                'start_time': datetime.now(),
                'agent_times': {},
                'token_count': 0,
                'vram_readings': [],
                'metadata': event.get('metadata', {})
            }

    def on_agent_invoked(self, event: Dict):
        """
        Log agent invocation in trace

        Called each time an agent is invoked during problem-solving.
        """
        with self._lock:
            conversation_id = event.get('conversation_id', '')
            if conversation_id not in self.active_traces:
                return

            trace = self.active_traces[conversation_id]
            agent_id = event.get('agent_id', 'unknown')

            trace['agent_sequence'].append(agent_id)
            trace['agent_times'][agent_id] = {
                'start': datetime.now(),
                'tokens': event.get('input_tokens', 0)
            }

            # Track VRAM
            vram = event.get('vram_mb', 0)
            if vram:
                trace['vram_readings'].append(vram)

            # Accumulate tokens
            trace['token_count'] += event.get('input_tokens', 0)

    def on_verification(self, event: Dict):
        """
        Record verification outcome

        Called when verification is complete (success or failure).
        """
        with self._lock:
            conversation_id = event.get('conversation_id', '')
            if conversation_id in self.active_traces:
                trace = self.active_traces[conversation_id]
                trace['verification_status'] = event.get('status', 'UNKNOWN')
                trace['success'] = event.get('status') == 'VERIFIED'

    def on_session_end(self, event: Dict):
        """
        Finalize and store trace

        Called when a problem-solving session completes.
        Returns the completed trace for analysis.
        """
        with self._lock:
            conversation_id = event.get('conversation_id', '')
            if conversation_id not in self.active_traces:
                return None

            trace_data = self.active_traces[conversation_id]
            end_time = datetime.now()

            # Calculate total time
            start_time = trace_data.get('start_time', end_time)
            time_taken = (end_time - start_time).total_seconds() * 1000

            # Calculate approximate CPU time per agent
            cpu_time = 0
            for agent_id, timing in trace_data.get('agent_times', {}).items():
                if 'start' in timing:
                    agent_time = (end_time - timing['start']).total_seconds() * 1000
                    trace_data['agent_times'][agent_id]['duration_ms'] = agent_time
                    cpu_time += agent_time

            # Create SolutionTrace
            solution_trace = SolutionTrace(
                trace_id=trace_data['trace_id'],
                conversation_id=conversation_id,
                problem_type=trace_data.get('problem_type', 'unknown'),
                problem_complexity=trace_data.get('problem_complexity', 'medium'),
                agent_sequence=trace_data.get('agent_sequence', []),
                time_taken_ms=time_taken,
                cpu_time_ms=cpu_time,
                agent_times={
                    k: v.get('duration_ms', 0)
                    for k, v in trace_data.get('agent_times', {}).items()
                },
                verification_status=trace_data.get('verification_status', 'UNKNOWN'),
                token_count=trace_data.get('token_count', 0),
                vram_peak_mb=max(trace_data.get('vram_readings', [0]) or [0]),
                success=trace_data.get('success', False),
                metadata=trace_data.get('metadata', {})
            )

            # Store trace
            self._store_trace(solution_trace)

            # Update statistics
            self.traces_recorded += 1
            if solution_trace.success:
                self.successful_traces += 1
            else:
                self.failed_traces += 1

            # Post for AutoMaAS analysis
            if self.blackboard:
                self._post_trace(solution_trace)

            # Clean up
            del self.active_traces[conversation_id]

            return solution_trace

    def _store_trace(self, trace: SolutionTrace):
        """Store trace in vector database and history"""
        # Add to local history
        self.completed_traces.append(trace)
        if len(self.completed_traces) > self.max_trace_history:
            self.completed_traces.pop(0)

        # Store in vector DB if available
        if self.vector_db:
            try:
                embedding = self._create_trace_embedding(trace)
                self.vector_db.insert({
                    'id': trace.trace_id,
                    'embedding': embedding,
                    'metadata': trace.to_dict()
                })
            except Exception as e:
                logger.debug(f"Could not store trace in vector DB: {type(e).__name__}: {e}")

    def _create_trace_embedding(self, trace: SolutionTrace) -> List[float]:
        """
        Create embedding for trace (for similarity search)

        Simple hash-based embedding for demo; would use proper
        embedding model in production.
        """
        # Create a simple numerical representation
        features = [
            hash(trace.problem_type) % 1000 / 1000,
            trace.time_taken_ms / 10000,
            len(trace.agent_sequence) / 10,
            1.0 if trace.success else 0.0,
            trace.token_count / 10000
        ]
        # Pad to consistent length
        return features + [0.0] * (64 - len(features))

    def _post_trace(self, trace: SolutionTrace):
        """Post trace to Blackboard for analysis"""
        try:
            from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType
            entry = create_entry(
                entry_type=EntryType.TASK,
                content=trace.to_dict(),
                author_agent='performance_monitor_001',
                conversation_id=trace.conversation_id,
                tags=['SOLUTION_TRACE', trace.trace_id],
                metadata={
                    'entry_type': 'SOLUTION_TRACE',
                    'status': 'LOGGED'
                }
            )
            self.blackboard.post(entry)
        except Exception as e:
            logger.debug(f"Could not post trace to blackboard: {type(e).__name__}: {e}")

    def get_recent_traces(self, problem_type: str = None,
                         limit: int = 100) -> List[SolutionTrace]:
        """Get recent traces, optionally filtered by problem type"""
        with self._lock:
            traces = self.completed_traces[-limit:]
            if problem_type:
                traces = [t for t in traces if t.problem_type == problem_type]
            return traces

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitor statistics"""
        return {
            'traces_recorded': self.traces_recorded,
            'successful_traces': self.successful_traces,
            'failed_traces': self.failed_traces,
            'success_rate': (self.successful_traces / max(1, self.traces_recorded)) * 100,
            'active_traces': len(self.active_traces)
        }


# ===========================================================================
# AGENT 3.2: THE AGENT SELECTOR OPTIMIZER
# ===========================================================================

class AgentSelectorOptimizer:
    """
    Agent 3.2: AutoMaAS Pattern Implementation

    DIRECTIVE:
    ---------
    Implement the AutoMaAS (Automated Multi-Agent System) logic that
    analyzes performance logs and generates updated routing heuristics.

    PATTERN RECOGNITION:
    -------------------
    Identifies correlations such as:
    "For 'Optimization' problems, the 'Geometric Agent' fails 80% of the time,
    while the 'Gradient Descent Agent' succeeds."

    OUTPUT:
    ------
    Updated Routing Tables (Heuristics) for the Main Orchestrator, encoding
    learned preferences as weighted routing rules.

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 3.2
    """

    def __init__(self, blackboard=None, vector_db=None):
        """
        Initialize Agent Selector Optimizer

        Args:
            blackboard: Phase 0 Blackboard
            vector_db: Vector database for trace retrieval
        """
        self.blackboard = blackboard
        self.vector_db = vector_db
        self._lock = threading.RLock()

        # Routing tables: problem_type -> {agent_id -> RoutingHeuristic}
        self.routing_tables: Dict[str, Dict[str, Dict]] = {}

        # Performance statistics
        # Structure: problem_type -> agent_id -> list of performance records
        self.performance_stats: Dict[str, Dict[str, List[Dict]]] = \
            defaultdict(lambda: defaultdict(list))

        # Statistics
        self.traces_analyzed = 0
        self.routing_updates = 0
        self.patterns_discovered = 0

        if self.blackboard:
            self._subscribe_to_traces()

        print("    [OK] Agent Selector Optimizer (AutoMaAS) initialized")

    def _subscribe_to_traces(self):
        """Subscribe to SOLUTION_TRACE events"""
        try:
            self.blackboard.subscribe(
                agent_id='agent_selector_optimizer_001',
                tags=['SOLUTION_TRACE'],
                callback=self._on_solution_trace
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to traces: {type(e).__name__}: {e}")

    def _on_solution_trace(self, entry):
        """Handle new solution trace"""
        if hasattr(entry, 'content') and isinstance(entry.content, dict):
            self.analyze_trace(entry.content)

    def analyze_trace(self, trace: Dict):
        """
        Extract patterns from solution trace

        Updates internal performance statistics for later routing
        table computation.

        Args:
            trace: Solution trace dictionary
        """
        with self._lock:
            self.traces_analyzed += 1

            problem_type = trace.get('problem_type', 'unknown')
            agent_sequence = trace.get('agent_sequence', [])
            success = trace.get('success', False)
            time_taken = trace.get('time_taken_ms', 0)

            # Update statistics for each agent in the sequence
            time_per_agent = time_taken / max(1, len(agent_sequence))

            for i, agent in enumerate(agent_sequence):
                self.performance_stats[problem_type][agent].append({
                    'success': success,
                    'time_ms': time_per_agent,
                    'sequence_position': i,
                    'total_agents': len(agent_sequence),
                    'timestamp': datetime.now().isoformat()
                })

    def compute_routing_tables(self) -> Dict[str, Dict]:
        """
        Generate optimized routing heuristics

        Analyzes all collected performance statistics and computes
        optimal routing weights for each agent/problem-type combination.

        Returns:
            Dictionary of routing tables by problem type
        """
        with self._lock:
            self.routing_updates += 1

            for problem_type, agent_stats in self.performance_stats.items():
                self.routing_tables[problem_type] = {}

                for agent_id, performances in agent_stats.items():
                    if not performances:
                        continue

                    # Calculate statistics
                    total = len(performances)
                    successes = sum(1 for p in performances if p['success'])
                    success_rate = successes / total

                    times = [p['time_ms'] for p in performances]
                    avg_time = sum(times) / len(times) if times else 0

                    # Compute routing weight
                    weight = self._compute_weight(success_rate, avg_time, total)

                    self.routing_tables[problem_type][agent_id] = {
                        'weight': weight,
                        'success_rate': success_rate,
                        'avg_time_ms': avg_time,
                        'sample_size': total,
                        'last_updated': datetime.now().isoformat()
                    }

            return self.routing_tables

    def _compute_weight(self, success_rate: float, avg_time: float,
                       sample_size: int) -> float:
        """
        Compute routing weight from performance metrics

        Weight formula considers:
        - Success rate (primary factor)
        - Time efficiency (faster = higher weight)
        - Sample size confidence (more samples = more confidence)
        """
        # Success rate is primary factor (0-100)
        base_weight = success_rate * 100

        # Time efficiency bonus (faster = higher weight)
        # Bonus up to +10 for sub-second agents
        if avg_time > 0:
            time_bonus = max(0, min(10, (10000 - avg_time) / 1000))
        else:
            time_bonus = 5

        # Confidence adjustment based on sample size
        # Full confidence at 50 samples
        confidence = min(sample_size / 50, 1.0)

        final_weight = (base_weight + time_bonus) * confidence
        return round(final_weight, 2)

    def get_pattern_insights(self) -> List[Dict]:
        """
        Generate human-readable insights from patterns

        Returns actionable insights about agent performance.
        """
        with self._lock:
            insights = []

            for problem_type, agents in self.routing_tables.items():
                if len(agents) < 2:
                    continue

                sorted_agents = sorted(
                    agents.items(),
                    key=lambda x: x[1]['weight'],
                    reverse=True
                )

                if len(sorted_agents) >= 2:
                    best = sorted_agents[0]
                    worst = sorted_agents[-1]

                    # Generate insight if significant difference
                    if (best[1]['success_rate'] > 0.7 and
                        worst[1]['success_rate'] < 0.4):
                        self.patterns_discovered += 1
                        insights.append({
                            'problem_type': problem_type,
                            'insight': (
                                f"For '{problem_type}' problems, "
                                f"'{worst[0]}' fails {(1-worst[1]['success_rate'])*100:.0f}% "
                                f"of the time, while '{best[0]}' succeeds "
                                f"{best[1]['success_rate']*100:.0f}%."
                            ),
                            'recommendation': f"Prefer {best[0]} over {worst[0]} for {problem_type}",
                            'best_agent': best[0],
                            'worst_agent': worst[0],
                            'confidence': min(best[1]['sample_size'], worst[1]['sample_size'])
                        })

            return insights

    def get_best_agents(self, problem_type: str, count: int = 3) -> List[str]:
        """
        Get the best agents for a problem type

        Args:
            problem_type: Type of problem
            count: Number of agents to return

        Returns:
            List of agent IDs sorted by routing weight
        """
        with self._lock:
            agents = self.routing_tables.get(problem_type, {})
            if not agents:
                return []

            sorted_agents = sorted(
                agents.items(),
                key=lambda x: x[1]['weight'],
                reverse=True
            )
            return [agent_id for agent_id, _ in sorted_agents[:count]]

    def get_statistics(self) -> Dict[str, Any]:
        """Get optimizer statistics"""
        return {
            'traces_analyzed': self.traces_analyzed,
            'routing_updates': self.routing_updates,
            'patterns_discovered': self.patterns_discovered,
            'problem_types_tracked': len(self.routing_tables)
        }


# ===========================================================================
# AGENT 3.3: THE ADAPTIVE DISPATCHER
# ===========================================================================

class AdaptiveDispatcher:
    """
    Agent 3.3: Dynamic Scaling Controller

    DIRECTIVE:
    ---------
    Connect the Optimizer's output to the Orchestrator's routing logic,
    enabling dynamic scaling based on query complexity.

    DYNAMIC SCALING LOGIC:
    ---------------------
    - Simple Tasks: Deploy "Skeleton Crew" (2-3 agents)
    - Standard Tasks: Deploy "Standard Team" (4-6 agents)
    - Complex Proofs: Deploy "Full Debate Team" (10+ agents)

    EXPECTED IMPACT:
    ---------------
    Optimizes cost-per-token by 10-15% by matching resource allocation
    to problem complexity.

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Agent 3.3
    """

    # Complexity thresholds
    SIMPLE_THRESHOLD = 0.3
    STANDARD_THRESHOLD = 0.7
    # Above STANDARD_THRESHOLD = Complex

    # Team sizes
    SKELETON_CREW_SIZE = 3
    STANDARD_TEAM_SIZE = 6
    FULL_DEBATE_SIZE = 12

    def __init__(self, blackboard=None, optimizer: AgentSelectorOptimizer = None,
                 orchestrator=None):
        """
        Initialize Adaptive Dispatcher

        Args:
            blackboard: Phase 0 Blackboard
            optimizer: Agent Selector Optimizer reference
            orchestrator: Main Orchestrator reference (for routing updates)
        """
        self.blackboard = blackboard
        self.optimizer = optimizer
        self.orchestrator = orchestrator
        self._lock = threading.RLock()

        # Statistics
        self.dispatches = 0
        self.skeleton_crew_dispatches = 0
        self.standard_dispatches = 0
        self.full_team_dispatches = 0
        self.routing_pushes = 0

        if self.blackboard:
            self._subscribe_to_routing_updates()

        print("    [OK] Adaptive Dispatcher Agent initialized")

    def _subscribe_to_routing_updates(self):
        """Receive updated routing tables from optimizer"""
        try:
            self.blackboard.subscribe(
                agent_id='adaptive_dispatcher_001',
                tags=['ROUTING_UPDATE'],
                callback=self._on_routing_update
            )
        except Exception as e:
            logger.warning(f"Could not subscribe to routing updates: {type(e).__name__}: {e}")

    def _on_routing_update(self, entry):
        """Handle routing table updates"""
        if hasattr(entry, 'content') and isinstance(entry.content, dict):
            routing_tables = entry.content.get('routing_tables', {})
            self.update_orchestrator(routing_tables)

    def update_orchestrator(self, routing_tables: Dict):
        """
        Push new routing tables to Orchestrator

        Args:
            routing_tables: New routing heuristics from optimizer
        """
        with self._lock:
            self.routing_pushes += 1

            if self.orchestrator:
                try:
                    if hasattr(self.orchestrator, 'update_routing_heuristics'):
                        self.orchestrator.update_routing_heuristics(routing_tables)
                except Exception as e:
                    logger.warning(f"Failed to update orchestrator routing: {type(e).__name__}: {e}")

    def determine_team_size(self, problem_context: Dict) -> int:
        """
        Dynamically scale team size based on complexity

        Args:
            problem_context: Dictionary with problem information

        Returns:
            Recommended team size
        """
        complexity = self._estimate_complexity(problem_context)

        with self._lock:
            self.dispatches += 1

            if complexity < self.SIMPLE_THRESHOLD:
                self.skeleton_crew_dispatches += 1
                return self.SKELETON_CREW_SIZE
            elif complexity < self.STANDARD_THRESHOLD:
                self.standard_dispatches += 1
                return self.STANDARD_TEAM_SIZE
            else:
                self.full_team_dispatches += 1
                return self.FULL_DEBATE_SIZE

    def get_complexity_level(self, problem_context: Dict) -> ComplexityLevel:
        """
        Get complexity level enum for a problem

        Args:
            problem_context: Dictionary with problem information

        Returns:
            ComplexityLevel enum value
        """
        complexity = self._estimate_complexity(problem_context)

        if complexity < self.SIMPLE_THRESHOLD:
            return ComplexityLevel.SIMPLE
        elif complexity < self.STANDARD_THRESHOLD:
            return ComplexityLevel.STANDARD
        else:
            return ComplexityLevel.COMPLEX

    def _estimate_complexity(self, context: Dict) -> float:
        """
        Estimate problem complexity from context

        Returns a value between 0 and 1.
        """
        score = 0.4  # Base complexity

        # Factors that increase complexity
        if context.get('involves_proof', False):
            score += 0.25
        if context.get('domain_count', 1) > 2:
            score += 0.15
        if context.get('novel_pattern', False):
            score += 0.2
        if context.get('verification_required', False):
            score += 0.1
        if context.get('multiple_steps', False):
            score += 0.15

        # Problem type complexity
        problem_type = context.get('problem_type', '').lower()
        if 'proof' in problem_type:
            score += 0.2
        elif 'optimization' in problem_type:
            score += 0.15
        elif 'integration' in problem_type:
            score += 0.1

        # Factors that decrease complexity
        if context.get('similar_solved_recently', False):
            score -= 0.25
        if context.get('standard_form', False):
            score -= 0.15
        if context.get('simple_expression', False):
            score -= 0.2

        return max(0.0, min(1.0, score))

    def select_agents(self, problem_type: str, team_size: int) -> List[str]:
        """
        Select optimal agents based on routing tables

        Args:
            problem_type: Type of problem to solve
            team_size: Number of agents to select

        Returns:
            List of agent IDs to deploy
        """
        if not self.optimizer:
            return []

        # Get best agents from optimizer
        best_agents = self.optimizer.get_best_agents(problem_type, team_size)

        if len(best_agents) >= team_size:
            return best_agents[:team_size]

        # Not enough historical data - use defaults
        return self._default_selection(problem_type, team_size)

    def _default_selection(self, problem_type: str, team_size: int) -> List[str]:
        """Default agent selection when no historical data exists"""
        # Would query Directory Facilitator for available agents
        # For now, return empty list (orchestrator will handle)
        return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get dispatcher statistics"""
        total = max(1, self.dispatches)
        return {
            'total_dispatches': self.dispatches,
            'skeleton_crew_dispatches': self.skeleton_crew_dispatches,
            'standard_dispatches': self.standard_dispatches,
            'full_team_dispatches': self.full_team_dispatches,
            'routing_pushes': self.routing_pushes,
            'skeleton_crew_rate': (self.skeleton_crew_dispatches / total) * 100,
            'full_team_rate': (self.full_team_dispatches / total) * 100
        }


# ===========================================================================
# META-LEARNING TEAM COORDINATOR
# ===========================================================================

class MetaLearningTeam:
    """
    Coordinator for the Meta-Learning Team ("The Optimizer")

    Brings together the three agents:
    1. Performance Monitor (Black Box Recorder)
    2. Agent Selector Optimizer (AutoMaAS)
    3. Adaptive Dispatcher (Dynamic Scaling)

    KEY PROTOCOLS:
    -------------
    - log_task_start(): Begin recording a solution trace
    - log_agent_invocation(): Record agent involvement
    - log_session_end(): Complete trace and trigger analysis
    - run_batch_optimization(): Compute new routing tables
    - get_team_recommendation(): Get optimal team for a problem

    REFERENCE:
    ---------
    Phase_4_Build_Order_Breakdown.md: Step 3
    """

    def __init__(self, blackboard=None, vector_db=None, orchestrator=None):
        """
        Initialize the Meta-Learning Team

        Args:
            blackboard: Phase 0 Blackboard for coordination
            vector_db: Vector database for trace storage
            orchestrator: Main Orchestrator for routing updates
        """
        print("  [META-LEARNING TEAM - The Optimizer]")

        self.blackboard = blackboard
        self.vector_db = vector_db
        self.orchestrator = orchestrator

        # Initialize agents
        self.performance_monitor = PerformanceMonitor(blackboard, vector_db)
        self.optimizer = AgentSelectorOptimizer(blackboard, vector_db)
        self.dispatcher = AdaptiveDispatcher(blackboard, self.optimizer, orchestrator)

        # Statistics
        self.optimization_runs = 0

        print("    [OK] Meta-Learning Team assembled")

    def log_task_start(self, conversation_id: str, problem_type: str,
                      complexity: str = 'medium', **metadata):
        """
        Begin recording a solution trace

        Should be called when a new problem-solving task begins.
        """
        self.performance_monitor.on_task_start({
            'conversation_id': conversation_id,
            'problem_type': problem_type,
            'complexity': complexity,
            'metadata': metadata
        })

    def log_agent_invocation(self, conversation_id: str, agent_id: str,
                            input_tokens: int = 0, vram_mb: float = 0):
        """
        Record agent involvement in a solution

        Should be called each time an agent is invoked.
        """
        self.performance_monitor.on_agent_invoked({
            'conversation_id': conversation_id,
            'agent_id': agent_id,
            'input_tokens': input_tokens,
            'vram_mb': vram_mb
        })

    def log_verification(self, conversation_id: str, status: str):
        """
        Record verification outcome

        Should be called when verification completes.
        """
        self.performance_monitor.on_verification({
            'conversation_id': conversation_id,
            'status': status
        })

    def log_session_end(self, conversation_id: str) -> Optional[SolutionTrace]:
        """
        Complete trace and trigger analysis

        Should be called when a problem-solving session completes.
        Returns the completed trace.
        """
        trace = self.performance_monitor.on_session_end({
            'conversation_id': conversation_id
        })

        if trace:
            # Analyze the trace
            self.optimizer.analyze_trace(trace.to_dict())

        return trace

    def run_batch_optimization(self) -> Dict:
        """
        Execute batch optimization

        Computes new routing tables and generates insights.
        Called during low-load periods or after SESSION_END.

        Returns:
            Optimization results with insights
        """
        self.optimization_runs += 1

        # Compute new routing tables
        new_tables = self.optimizer.compute_routing_tables()

        # Generate insights
        insights = self.optimizer.get_pattern_insights()

        # Push updates via dispatcher
        if self.blackboard:
            try:
                from symbo_agentic_reasoners.core.blackboard import create_entry, EntryType
                entry = create_entry(
                    entry_type=EntryType.TASK,
                    content={
                        'routing_tables': new_tables,
                        'insights': insights,
                        'optimization_run': datetime.now().isoformat()
                    },
                    author_agent='meta_learning_team',
                    conversation_id='optimization',
                    tags=['ROUTING_UPDATE', 'OPTIMIZATION_COMPLETE'],
                    metadata={
                        'entry_type': 'ROUTING_UPDATE'
                    }
                )
                self.blackboard.post(entry)
            except Exception as e:
                logger.debug(f"Could not post routing update: {type(e).__name__}: {e}")

        return {
            'tables_updated': len(new_tables),
            'insights_generated': len(insights),
            'insights': insights
        }

    def get_team_recommendation(self, problem_context: Dict) -> Dict:
        """
        Get optimal team configuration for a problem

        Args:
            problem_context: Dictionary with problem information

        Returns:
            Recommendation with team size and suggested agents
        """
        team_size = self.dispatcher.determine_team_size(problem_context)
        complexity = self.dispatcher.get_complexity_level(problem_context)
        problem_type = problem_context.get('problem_type', 'unknown')

        agents = self.dispatcher.select_agents(problem_type, team_size)

        return {
            'team_size': team_size,
            'complexity_level': complexity.name,
            'suggested_agents': agents,
            'rationale': f"{complexity.name} complexity -> {team_size} agents"
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get team statistics"""
        return {
            'optimization_runs': self.optimization_runs,
            'performance_monitor': self.performance_monitor.get_statistics(),
            'optimizer': self.optimizer.get_statistics(),
            'dispatcher': self.dispatcher.get_statistics()
        }


# ===========================================================================
# MODULE TEST
# ===========================================================================

if __name__ == "__main__":
    """Test Meta-Learning Team"""
    print("=" * 80)
    print("PHASE 4 - STEP 3: META-LEARNING TEAM TEST")
    print("=" * 80)
    print()

    # Initialize team
    team = MetaLearningTeam()
    print()

    # Simulate some solution traces
    print("SIMULATING SOLUTION TRACES")
    print("-" * 40)

    # Trace 1: Successful integration
    print("Trace 1: Successful integration")
    team.log_task_start('conv_001', 'integration')
    team.log_agent_invocation('conv_001', 'symbolic_integration_001', 100)
    team.log_verification('conv_001', 'VERIFIED')
    team.log_session_end('conv_001')

    # Trace 2: Failed integration, recovered with numerical
    print("Trace 2: Failed symbolic, numerical fallback")
    team.log_task_start('conv_002', 'integration')
    team.log_agent_invocation('conv_002', 'symbolic_integration_001', 100)
    team.log_agent_invocation('conv_002', 'numerical_integration_001', 50)
    team.log_verification('conv_002', 'VERIFIED')
    team.log_session_end('conv_002')

    # Trace 3: Successful algebra
    print("Trace 3: Successful algebra")
    team.log_task_start('conv_003', 'algebra')
    team.log_agent_invocation('conv_003', 'algebra_specialist_001', 80)
    team.log_verification('conv_003', 'VERIFIED')
    team.log_session_end('conv_003')

    # More integration traces to build statistics
    for i in range(10):
        conv_id = f'conv_{100+i}'
        team.log_task_start(conv_id, 'integration')
        if i % 3 == 0:  # Some fail
            team.log_agent_invocation(conv_id, 'symbolic_integration_001', 100)
            team.log_verification(conv_id, 'FAILED')
        else:  # Most succeed
            team.log_agent_invocation(conv_id, 'numerical_integration_001', 50)
            team.log_verification(conv_id, 'VERIFIED')
        team.log_session_end(conv_id)

    print()

    # Run batch optimization
    print("RUNNING BATCH OPTIMIZATION")
    print("-" * 40)
    results = team.run_batch_optimization()
    print(f"Tables updated: {results['tables_updated']}")
    print(f"Insights generated: {results['insights_generated']}")
    if results['insights']:
        for insight in results['insights']:
            print(f"  - {insight['insight']}")
    print()

    # Test team recommendation
    print("TEAM RECOMMENDATIONS")
    print("-" * 40)

    simple_problem = {
        'problem_type': 'algebra',
        'simple_expression': True,
        'standard_form': True
    }
    rec = team.get_team_recommendation(simple_problem)
    print(f"Simple algebra: {rec['team_size']} agents ({rec['complexity_level']})")

    complex_problem = {
        'problem_type': 'proof',
        'involves_proof': True,
        'multiple_steps': True,
        'novel_pattern': True
    }
    rec = team.get_team_recommendation(complex_problem)
    print(f"Complex proof: {rec['team_size']} agents ({rec['complexity_level']})")
    print()

    # Statistics
    print("TEAM STATISTICS:")
    import json
    print(json.dumps(team.get_statistics(), indent=2))
    print()

    print("=" * 80)
    print("META-LEARNING TEAM TEST COMPLETE")
    print("=" * 80)
