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
LEARNING ENHANCEMENT TEAM - Negative Learner Specialist (Tier 3)
=================================================================

Learns from failures using contrastive learning. Stores failure patterns
and generates contrastive pairs (anchor, positive, negative) for training.

KEY CONCEPTS:
-------------
1. Negative Examples: Store patterns that led to incorrect/bad responses
2. Contrastive Learning: Train to push apart good/bad response embeddings
3. Pattern Detection: Identify known bad patterns before learning
4. Failure Analysis: Track failure types for system improvement

FAILURE TYPES:
--------------
- symbolic_placeholder: Incomplete symbolic processing ("symbolic")
- unknown_placeholder: Failed resolution ("unknown")
- empty_result: No solution found ("[]", "{}")
- malformed_expression: Syntax errors, broken expressions
- echo_response: Input echoed as output
- timeout: Computation exceeded time limit
- numerical_instability: Overflow, underflow, NaN

CONTRASTIVE LOSS:
----------------
For triplet (anchor=problem, positive=correct, negative=bad):
  loss = max(0, margin - cos(anchor, positive) + cos(anchor, negative))

This pushes correct responses closer and bad responses farther from problems.

REFERENCE:
---------
- Plan: lexical-leaping-tower.md Phase 3 Priority 3
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
from pathlib import Path

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

from . import NegativeExample, ContrastivePair, FailureType

logger = logging.getLogger('symbo_agentic_reasoners.learning.negative_learner')


class NegativeLearnerSpecialist(BDIAgent):
    """
    Negative Learner Specialist - Tier 3

    Learns from failures using contrastive learning. Stores patterns that
    led to incorrect responses and uses them to improve model training.

    ROLE:
    ----
    1. Store failure patterns for future avoidance
    2. Generate contrastive pairs for training
    3. Detect known bad patterns before learning
    4. Analyze failure distributions for insights

    CONTRASTIVE LEARNING:
    --------------------
    Uses triplet loss to push apart embeddings:
    - Anchor: The problem text
    - Positive: Correct/good response
    - Negative: Incorrect/bad response

    This teaches the model to distinguish good from bad responses.

    Example:
        >>> learner = NegativeLearnerSpecialist()
        >>> learner.add_negative("solve(x^2 + 1 = 0)", "symbolic", "placeholder")
        >>> is_bad, reason = learner.is_known_bad("symbolic")
        >>> is_bad  # True
    """

    # Known bad response patterns
    BAD_PATTERNS = {
        'placeholders': ['symbolic', 'unknown', 'error', 'failed', 'none'],
        'empty': ['[]', '{}', '()', '', 'null', 'nil'],
        'errors': ['exception', 'traceback', 'error:', 'failed:'],
    }

    # Malformed expression patterns
    MALFORMED_PATTERNS = [
        r'^sqrt\(.*\*1\*.*\)$',      # sqrt((5 - 1*1*-1*1*7)**2)
        r'^\+$|^-$|^\*$|^/$',        # Single operator
        r'^\($|^\)$|^\[$|^\]$',      # Single bracket
        r'.*NaN.*',                   # Contains NaN
        r'.*inf.*',                   # Contains infinity (suspicious)
    ]

    def __init__(
        self,
        agent_id: str = 'negative_learner_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        max_examples: int = 10000,
        persistence_path: Optional[str] = None
    ):
        """
        Initialize Negative Learner Specialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
            max_examples: Maximum negative examples to store
            persistence_path: Path to persist negative examples
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard
        self.max_examples = max_examples
        self.persistence_path = persistence_path

        # Storage for negative examples
        self.negative_examples: Dict[str, NegativeExample] = {}
        self.failure_counts: Dict[str, int] = defaultdict(int)

        # Mapping to correct answers (for contrastive pairs)
        self.correct_answers: Dict[str, str] = {}

        # Statistics
        self.checks_performed = 0
        self.bad_patterns_detected = 0
        self.examples_added = 0

        # BDI state
        self.beliefs: Dict[str, Any] = {
            'most_common_failure': None,
            'cleanup_needed': False
        }

        # Load persisted examples if available
        if persistence_path:
            self._load_from_disk()

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Negative Learner initialized with {len(self.negative_examples)} examples")

    def _register_services(self) -> None:
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            agent_id=self.agent_id,
            service_type='learning.negative_learning',
            description='Learns from failures using contrastive learning',
            capabilities=['check_bad', 'add_negative', 'get_contrastive_pairs', 'analyze']
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered with DF")

    def add_negative(
        self,
        problem: str,
        bad_response: str,
        reason: str,
        domain: str = None,
        correct_answer: str = None
    ) -> Dict[str, Any]:
        """
        Add a negative example to the store.

        Args:
            problem: The input problem
            bad_response: The incorrect/bad response
            reason: Why this is considered bad
            domain: Problem domain
            correct_answer: The correct answer (for contrastive pairs)

        Returns:
            Status dict with 'added' or 'updated'
        """
        # Determine failure type
        failure_type = self._classify_failure(bad_response, reason)

        # Normalize problem for key
        key = self._normalize(problem)

        if key in self.negative_examples:
            # Update occurrence count
            self.negative_examples[key].occurrences += 1
            status = 'updated'
        else:
            # Add new example
            self.negative_examples[key] = NegativeExample(
                problem=problem,
                bad_response=bad_response,
                reason=reason,
                failure_type=failure_type,
                domain=domain,
                occurrences=1
            )
            self.examples_added += 1
            status = 'added'

        # Store correct answer if provided
        if correct_answer:
            self.correct_answers[key] = correct_answer

        # Update failure counts
        self.failure_counts[failure_type.value] += 1

        # Enforce max size
        self._enforce_max_size()

        # Persist if path configured
        if self.persistence_path:
            self._save_to_disk()

        return {
            'status': status,
            'key': key,
            'failure_type': failure_type.value,
            'total_examples': len(self.negative_examples)
        }

    def is_known_bad(self, response: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a response matches known bad patterns.

        Args:
            response: The response to check

        Returns:
            Tuple of (is_bad, reason)
        """
        self.checks_performed += 1
        response_clean = response.strip().lower()

        # Check placeholder patterns
        for placeholder in self.BAD_PATTERNS['placeholders']:
            if response_clean == placeholder:
                self.bad_patterns_detected += 1
                return True, f'placeholder_response: {placeholder}'

        # Check empty patterns
        for empty in self.BAD_PATTERNS['empty']:
            if response_clean == empty:
                self.bad_patterns_detected += 1
                return True, 'empty_response'

        # Check error patterns
        for error in self.BAD_PATTERNS['errors']:
            if error in response_clean:
                self.bad_patterns_detected += 1
                return True, 'error_in_response'

        # Check malformed expression patterns
        for pattern in self.MALFORMED_PATTERNS:
            if re.match(pattern, response, re.IGNORECASE):
                self.bad_patterns_detected += 1
                return True, 'malformed_expression'

        # Check if too short (likely incomplete)
        if len(response.strip()) < 2 and not response.strip().isdigit():
            if response.strip() not in ['0', '1', 'x', 'y', 'e', 'i', 'n', 'k']:
                self.bad_patterns_detected += 1
                return True, 'too_short'

        return False, None

    def _classify_failure(self, bad_response: str, reason: str) -> FailureType:
        """Classify the type of failure."""
        response_lower = bad_response.lower().strip()
        reason_lower = reason.lower()

        if response_lower == 'symbolic':
            return FailureType.SYMBOLIC_PLACEHOLDER
        elif response_lower == 'unknown':
            return FailureType.UNKNOWN_PLACEHOLDER
        elif response_lower in ['[]', '{}', '', 'none']:
            return FailureType.EMPTY_RESULT
        elif 'timeout' in reason_lower:
            return FailureType.TIMEOUT
        elif 'nan' in response_lower or 'inf' in response_lower:
            return FailureType.NUMERICAL_INSTABILITY
        elif 'malformed' in reason_lower:
            return FailureType.MALFORMED_EXPRESSION
        elif 'echo' in reason_lower:
            return FailureType.ECHO_RESPONSE
        else:
            return FailureType.VALIDATION_FAILED

    def _normalize(self, text: str) -> str:
        """Normalize text for consistent keying."""
        # Remove extra whitespace, lowercase
        normalized = ' '.join(text.lower().split())
        return normalized

    def _enforce_max_size(self) -> None:
        """Remove oldest examples if over max size."""
        if len(self.negative_examples) > self.max_examples:
            # Sort by timestamp, remove oldest
            sorted_keys = sorted(
                self.negative_examples.keys(),
                key=lambda k: self.negative_examples[k].timestamp
            )

            # Remove oldest 10%
            remove_count = len(sorted_keys) - int(self.max_examples * 0.9)
            for key in sorted_keys[:remove_count]:
                del self.negative_examples[key]
                if key in self.correct_answers:
                    del self.correct_answers[key]

    def get_contrastive_pairs(self, batch_size: int = 32) -> List[ContrastivePair]:
        """
        Get contrastive triplets for training.

        Returns triplets (anchor=problem, positive=correct, negative=bad)
        for contrastive loss training.

        Args:
            batch_size: Number of pairs to return

        Returns:
            List of ContrastivePair objects
        """
        pairs = []

        # Only include examples where we have correct answers
        for key, example in list(self.negative_examples.items())[:batch_size]:
            correct = self.correct_answers.get(key)
            if correct:
                pairs.append(ContrastivePair(
                    anchor=example.problem,
                    positive=correct,
                    negative=example.bad_response
                ))

        return pairs

    def get_failure_stats(self) -> Dict[str, Any]:
        """Get failure statistics."""
        total_failures = sum(self.failure_counts.values())

        # Calculate percentages
        percentages = {}
        for failure_type, count in self.failure_counts.items():
            if total_failures > 0:
                percentages[failure_type] = count / total_failures * 100

        # Find most common
        most_common = max(self.failure_counts.items(), key=lambda x: x[1]) if self.failure_counts else (None, 0)

        return {
            'total_negative_examples': len(self.negative_examples),
            'total_failures_tracked': total_failures,
            'failure_counts': dict(self.failure_counts),
            'failure_percentages': percentages,
            'most_common_failure': most_common[0],
            'checks_performed': self.checks_performed,
            'bad_patterns_detected': self.bad_patterns_detected,
            'detection_rate': self.bad_patterns_detected / self.checks_performed if self.checks_performed > 0 else 0
        }

    def analyze_failures(self) -> Dict[str, Any]:
        """
        Analyze failure patterns for insights.

        Returns:
            Analysis with patterns, recommendations
        """
        if not self.negative_examples:
            return {'error': 'No negative examples to analyze'}

        # Group by domain
        domain_failures = defaultdict(list)
        for key, example in self.negative_examples.items():
            domain = example.domain or 'unknown'
            domain_failures[domain].append(example)

        # Calculate domain failure rates
        domain_stats = {}
        for domain, examples in domain_failures.items():
            failure_types = defaultdict(int)
            for ex in examples:
                failure_types[ex.failure_type.value] += 1

            domain_stats[domain] = {
                'total': len(examples),
                'failure_types': dict(failure_types)
            }

        # Find problematic patterns
        common_patterns = defaultdict(int)
        for example in self.negative_examples.values():
            # Extract pattern features
            if 'sqrt' in example.bad_response:
                common_patterns['sqrt_related'] += 1
            if example.bad_response.count('(') != example.bad_response.count(')'):
                common_patterns['unbalanced_parens'] += 1
            if len(example.bad_response) < 5:
                common_patterns['very_short'] += 1

        # Generate recommendations
        recommendations = self._generate_recommendations(domain_stats, common_patterns)

        return {
            'total_failures': len(self.negative_examples),
            'domain_breakdown': domain_stats,
            'common_patterns': dict(common_patterns),
            'recommendations': recommendations
        }

    def _generate_recommendations(
        self,
        domain_stats: Dict,
        common_patterns: Dict
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Check for domain-specific issues
        for domain, stats in domain_stats.items():
            if stats['total'] > 100:
                recommendations.append(
                    f"Domain '{domain}' has {stats['total']} failures. "
                    f"Consider specialized handling."
                )

        # Check for pattern issues
        if common_patterns.get('sqrt_related', 0) > 50:
            recommendations.append(
                "Many sqrt-related failures. Review square root simplification logic."
            )

        if common_patterns.get('unbalanced_parens', 0) > 20:
            recommendations.append(
                "Unbalanced parentheses detected. Check expression parsing."
            )

        if common_patterns.get('very_short', 0) > 100:
            recommendations.append(
                "Many very short responses. May indicate early termination issues."
            )

        return recommendations

    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        return {
            'negative_examples': len(self.negative_examples),
            'correct_answers_stored': len(self.correct_answers),
            'checks_performed': self.checks_performed,
            'bad_patterns_detected': self.bad_patterns_detected,
            'examples_added': self.examples_added,
            'failure_counts': dict(self.failure_counts)
        }

    def _save_to_disk(self) -> None:
        """Persist negative examples to disk."""
        if not self.persistence_path:
            return

        try:
            path = Path(self.persistence_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'negative_examples': {
                    k: v.to_dict() for k, v in self.negative_examples.items()
                },
                'correct_answers': self.correct_answers,
                'failure_counts': dict(self.failure_counts),
                'saved_at': datetime.now().isoformat()
            }

            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved {len(self.negative_examples)} negative examples to {path}")

        except Exception as e:
            logger.error(f"Failed to save negative examples: {e}")

    def _load_from_disk(self) -> None:
        """Load negative examples from disk."""
        if not self.persistence_path:
            return

        path = Path(self.persistence_path)
        if not path.exists():
            return

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            # Restore negative examples
            for key, example_dict in data.get('negative_examples', {}).items():
                self.negative_examples[key] = NegativeExample(
                    problem=example_dict['problem'],
                    bad_response=example_dict['bad_response'],
                    reason=example_dict['reason'],
                    failure_type=FailureType(example_dict['failure_type']),
                    domain=example_dict.get('domain'),
                    occurrences=example_dict.get('occurrences', 1)
                )

            # Restore correct answers
            self.correct_answers = data.get('correct_answers', {})

            # Restore failure counts
            self.failure_counts = defaultdict(int, data.get('failure_counts', {}))

            logger.info(f"Loaded {len(self.negative_examples)} negative examples from {path}")

        except Exception as e:
            logger.error(f"Failed to load negative examples: {e}")

    # BDI Agent methods
    def update_beliefs(self, percept: Dict[str, Any] = None) -> None:
        """Update beliefs based on current state."""
        # Find most common failure type
        if self.failure_counts:
            self.beliefs['most_common_failure'] = max(
                self.failure_counts.items(),
                key=lambda x: x[1]
            )[0]

        # Check if cleanup needed
        self.beliefs['cleanup_needed'] = len(self.negative_examples) > self.max_examples * 0.9

    def deliberate(self) -> Optional[Intention]:
        """Deliberate on current beliefs."""
        if self.beliefs.get('cleanup_needed', False):
            return Intention(
                plan_id='cleanup_examples',
                steps=['sort_by_age', 'remove_oldest', 'persist'],
                target_desire='maintain_size_limit'
            )
        return None

    def execute_step(self) -> bool:
        """Execute one step of agent processing."""
        if self.blackboard:
            # Would check for pending negative learning tasks
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
        action = task_entry.get('action', 'check')

        if action == 'check':
            is_bad, reason = self.is_known_bad(task_entry.get('response', ''))
            return {'is_bad': is_bad, 'reason': reason}

        elif action == 'add_negative':
            return self.add_negative(
                problem=task_entry.get('problem', ''),
                bad_response=task_entry.get('bad_response', ''),
                reason=task_entry.get('reason', 'unknown'),
                domain=task_entry.get('domain'),
                correct_answer=task_entry.get('correct_answer')
            )

        elif action == 'get_contrastive_pairs':
            pairs = self.get_contrastive_pairs(task_entry.get('batch_size', 32))
            return {
                'pairs': [
                    {'anchor': p.anchor, 'positive': p.positive, 'negative': p.negative}
                    for p in pairs
                ]
            }

        elif action == 'get_stats':
            return self.get_failure_stats()

        elif action == 'analyze':
            return self.analyze_failures()

        else:
            return {'error': f'Unknown action: {action}'}
