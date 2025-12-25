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
LEARNING ENHANCEMENT TEAM - Complexity Scorer Specialist (Tier 3)
==================================================================

Scores problem complexity for weighted learning. More complex problems
get stronger learning signals to ensure the model prioritizes difficult
mathematical concepts.

SCORING FACTORS:
---------------
1. Token Complexity (0.0-0.25): Length/token count of problem
2. Nesting Depth (0.0-0.25): Parenthesis/bracket nesting
3. Variable Diversity (0.0-0.15): Number of unique variables
4. Domain Weight (0.0-0.20): Difficulty multiplier by domain
5. Solve Time (0.0-0.15): Empirical difficulty from solve time

DOMAIN WEIGHTS:
--------------
- calculus: 1.5
- differential_equations: 2.0
- number_theory: 1.3
- algebra: 1.0
- geometry: 1.2
- linear_algebra: 1.4
- complex_analysis: 1.8
- real_analysis: 1.6

REFERENCE:
---------
- Plan: lexical-leaping-tower.md Phase 3 Priority 2
"""

import re
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
from collections import defaultdict

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

from . import ComplexityScore, ComplexityLevel

logger = logging.getLogger('symbo_agentic_reasoners.learning.complexity_scorer')


class ComplexityScorerSpecialist(BDIAgent):
    """
    Complexity Scorer Specialist - Tier 3

    Scores problem complexity to weight learning signals appropriately.
    More complex problems receive stronger gradient updates to ensure
    the model prioritizes difficult mathematical concepts.

    ROLE:
    ----
    Before learning a problem, score its complexity (0.0-1.0) and
    provide a learning weight multiplier. This ensures:
    - Trivial problems (2+2=4) don't overwhelm learning
    - Complex problems (ODEs, proofs) get priority

    SCORING FACTORS:
    ---------------
    1. Token Complexity - Problem length and structure
    2. Nesting Depth - Parenthesis/bracket depth
    3. Variable Diversity - Unique variables used
    4. Domain Weight - Inherent domain difficulty
    5. Solve Time - Empirical difficulty measure

    Example:
        >>> scorer = ComplexityScorerSpecialist()
        >>> result = scorer.score("Solve: d^2y/dx^2 + 3dy/dx + 2y = e^x", domain="differential_equations")
        >>> result.score  # ~0.75
        >>> result.learning_weight  # 1.75 (1.0 + 0.75)
    """

    # Domain difficulty weights (based on cognitive load research)
    DOMAIN_WEIGHTS = {
        'calculus': 1.5,
        'differential_equations': 2.0,
        'ode': 2.0,
        'pde': 2.2,
        'number_theory': 1.3,
        'algebra': 1.0,
        'linear_algebra': 1.4,
        'geometry': 1.2,
        'trigonometry': 1.1,
        'complex_analysis': 1.8,
        'real_analysis': 1.6,
        'functional_analysis': 1.9,
        'topology': 1.7,
        'statistics': 1.2,
        'probability': 1.3,
        'combinatorics': 1.4,
        'graph_theory': 1.3,
        'logic': 1.2,
        'proof_theory': 1.6,
        'category_theory': 1.8,
        'cryptography': 1.5,
        'optimization': 1.4,
        'physics': 1.5,
        'unknown': 1.0,
    }

    # Keywords that indicate complexity
    COMPLEXITY_KEYWORDS = {
        'high': ['prove', 'theorem', 'lemma', 'corollary', 'iff', 'if and only if',
                 'derivative', 'integral', 'limit', 'series', 'convergence',
                 'eigenvalue', 'eigenvector', 'determinant', 'differential',
                 'partial', 'gradient', 'divergence', 'curl', 'laplacian'],
        'medium': ['solve', 'find', 'evaluate', 'compute', 'simplify',
                   'expand', 'factor', 'substitute', 'transform'],
        'low': ['calculate', 'add', 'subtract', 'multiply', 'divide']
    }

    def __init__(
        self,
        agent_id: str = 'complexity_scorer_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """
        Initialize Complexity Scorer Specialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.scores_computed = 0
        self.score_history: List[Dict[str, Any]] = []
        self.domain_stats: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {'count': 0, 'total_score': 0.0, 'avg_score': 0.0}
        )

        # BDI state
        self.beliefs: Dict[str, Any] = {
            'avg_score': 0.5,
            'score_distribution': {},
            'calibration_needed': False
        }

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] Complexity Scorer initialized")

    def _register_services(self) -> None:
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            agent_id=self.agent_id,
            service_type='learning.complexity_scoring',
            description='Scores problem complexity for weighted learning',
            capabilities=['score', 'batch_score', 'analyze']
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered with DF")

    def score(
        self,
        problem: str,
        answer: str = '',
        domain: str = 'unknown',
        solve_time_ms: Optional[float] = None
    ) -> ComplexityScore:
        """
        Calculate complexity score for a problem.

        Args:
            problem: The problem text
            answer: The solution (optional, used for answer complexity)
            domain: Problem domain
            solve_time_ms: Time taken to solve (empirical difficulty)

        Returns:
            ComplexityScore with score, level, and learning weight
        """
        self.scores_computed += 1
        components = {}

        # 1. Token Complexity (0.0-0.25)
        token_score = self._score_tokens(problem)
        components['tokens'] = token_score

        # 2. Nesting Depth (0.0-0.25)
        nesting_score = self._score_nesting(problem)
        components['nesting'] = nesting_score

        # 3. Variable Diversity (0.0-0.15)
        variable_score = self._score_variables(problem)
        components['variables'] = variable_score

        # 4. Domain Weight (0.0-0.20)
        domain_score = self._score_domain(domain)
        components['domain'] = domain_score

        # 5. Solve Time (0.0-0.15)
        time_score = self._score_solve_time(solve_time_ms)
        components['solve_time'] = time_score

        # 6. Keyword Complexity (bonus 0.0-0.10)
        keyword_score = self._score_keywords(problem)
        components['keywords'] = keyword_score

        # Calculate total score (capped at 1.0)
        total_score = min(1.0, sum(components.values()))

        # Determine level
        level = self._score_to_level(total_score)

        # Calculate learning weight (1.0 + score for complexity boost)
        learning_weight = 1.0 + total_score

        result = ComplexityScore(
            score=total_score,
            level=level,
            learning_weight=learning_weight,
            components=components
        )

        # Update statistics
        self._update_stats(domain, total_score)

        # Record history (keep last 1000)
        if len(self.score_history) >= 1000:
            self.score_history = self.score_history[-500:]

        self.score_history.append({
            'problem': problem[:100],
            'domain': domain,
            'score': total_score,
            'level': level.value,
            'timestamp': datetime.now().isoformat()
        })

        return result

    def _score_tokens(self, text: str) -> float:
        """
        Score based on token count.

        Longer problems are generally more complex.
        Max contribution: 0.25
        """
        # Split by whitespace and operators
        tokens = re.split(r'[\s+\-*/=<>()[\]{}]+', text)
        tokens = [t for t in tokens if t]

        token_count = len(tokens)

        # Scale: 0 tokens = 0, 100+ tokens = 0.25
        score = min(token_count / 100, 0.25)

        return score

    def _score_nesting(self, text: str) -> float:
        """
        Score based on parenthesis/bracket nesting depth.

        Deeper nesting indicates more complex expressions.
        Max contribution: 0.25
        """
        max_depth = 0
        current_depth = 0

        for char in text:
            if char in '([{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ')]}':
                current_depth = max(0, current_depth - 1)

        # Scale: 0 depth = 0, 10+ depth = 0.25
        score = min(max_depth / 10, 0.25)

        return score

    def _score_variables(self, text: str) -> float:
        """
        Score based on variable diversity.

        More unique variables = more complex problem.
        Max contribution: 0.15
        """
        # Find single-letter variables (but not common words like 'a', 'I')
        potential_vars = re.findall(r'\b([a-zA-Z])\b', text)

        # Filter out common non-variable letters
        non_vars = {'a', 'A', 'I', 'O', 'o'}
        variables = set(v for v in potential_vars if v not in non_vars)

        # Also find subscripted variables like x_1, y_2
        subscripted = re.findall(r'([a-zA-Z])_?\d+', text)
        variables.update(subscripted)

        var_count = len(variables)

        # Scale: 0 vars = 0, 10+ vars = 0.15
        score = min(var_count / 10, 0.15)

        return score

    def _score_domain(self, domain: str) -> float:
        """
        Score based on domain difficulty.

        Some domains are inherently more complex.
        Max contribution: 0.20
        """
        domain_lower = domain.lower().replace(' ', '_')

        # Get domain weight (default 1.0)
        weight = self.DOMAIN_WEIGHTS.get(domain_lower, 1.0)

        # Scale weight to 0.0-0.20
        # Weight 1.0 = 0.0, Weight 2.0 = 0.20
        score = min((weight - 1.0) * 0.2, 0.20)

        return max(0.0, score)

    def _score_solve_time(self, solve_time_ms: Optional[float]) -> float:
        """
        Score based on empirical solve time.

        Longer solve times indicate harder problems.
        Max contribution: 0.15
        """
        if solve_time_ms is None:
            return 0.0

        # Scale: 0ms = 0, 10000ms+ = 0.15
        score = min(solve_time_ms / 10000, 0.15)

        return score

    def _score_keywords(self, text: str) -> float:
        """
        Score based on complexity-indicating keywords.

        Certain keywords indicate mathematical complexity.
        Max contribution: 0.10
        """
        text_lower = text.lower()
        score = 0.0

        # High complexity keywords (+0.02 each, max 0.10)
        for keyword in self.COMPLEXITY_KEYWORDS['high']:
            if keyword in text_lower:
                score += 0.02

        # Medium complexity keywords (+0.01 each)
        for keyword in self.COMPLEXITY_KEYWORDS['medium']:
            if keyword in text_lower:
                score += 0.01

        # Low complexity keywords (-0.01 each, can reduce score)
        for keyword in self.COMPLEXITY_KEYWORDS['low']:
            if keyword in text_lower:
                score -= 0.005

        return max(0.0, min(score, 0.10))

    def _score_to_level(self, score: float) -> ComplexityLevel:
        """Convert numeric score to complexity level."""
        if score < 0.2:
            return ComplexityLevel.TRIVIAL
        elif score < 0.4:
            return ComplexityLevel.EASY
        elif score < 0.6:
            return ComplexityLevel.MEDIUM
        elif score < 0.8:
            return ComplexityLevel.HARD
        else:
            return ComplexityLevel.EXPERT

    def _update_stats(self, domain: str, score: float) -> None:
        """Update running statistics."""
        stats = self.domain_stats[domain]
        stats['count'] += 1
        stats['total_score'] += score
        stats['avg_score'] = stats['total_score'] / stats['count']

    def batch_score(
        self,
        problems: List[Dict[str, Any]]
    ) -> List[ComplexityScore]:
        """
        Score multiple problems in batch.

        Args:
            problems: List of problem dicts with 'problem', 'answer', 'domain'

        Returns:
            List of ComplexityScore results
        """
        results = []

        for p in problems:
            result = self.score(
                problem=p.get('problem', ''),
                answer=p.get('answer', ''),
                domain=p.get('domain', 'unknown'),
                solve_time_ms=p.get('solve_time_ms')
            )
            results.append(result)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get scoring statistics."""
        # Calculate score distribution
        if self.score_history:
            scores = [h['score'] for h in self.score_history]
            distribution = {
                'trivial': sum(1 for s in scores if s < 0.2),
                'easy': sum(1 for s in scores if 0.2 <= s < 0.4),
                'medium': sum(1 for s in scores if 0.4 <= s < 0.6),
                'hard': sum(1 for s in scores if 0.6 <= s < 0.8),
                'expert': sum(1 for s in scores if s >= 0.8)
            }
        else:
            distribution = {}

        return {
            'scores_computed': self.scores_computed,
            'average_score': sum(h['score'] for h in self.score_history) / len(self.score_history)
                            if self.score_history else 0.0,
            'score_distribution': distribution,
            'domain_stats': dict(self.domain_stats)
        }

    def analyze_corpus(
        self,
        problems: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze complexity distribution of a problem corpus.

        Args:
            problems: List of problem dicts

        Returns:
            Analysis including distribution, outliers, recommendations
        """
        scores = self.batch_score(problems)

        if not scores:
            return {'error': 'No problems to analyze'}

        score_values = [s.score for s in scores]

        # Calculate statistics
        avg_score = sum(score_values) / len(score_values)
        min_score = min(score_values)
        max_score = max(score_values)

        # Distribution by level
        level_counts = defaultdict(int)
        for s in scores:
            level_counts[s.level.value] += 1

        # Domain breakdown
        domain_breakdown = defaultdict(lambda: {'count': 0, 'avg_score': 0.0, 'total': 0.0})
        for p, s in zip(problems, scores):
            domain = p.get('domain', 'unknown')
            domain_breakdown[domain]['count'] += 1
            domain_breakdown[domain]['total'] += s.score

        for domain in domain_breakdown:
            stats = domain_breakdown[domain]
            stats['avg_score'] = stats['total'] / stats['count']
            del stats['total']

        return {
            'total_problems': len(problems),
            'average_complexity': avg_score,
            'min_complexity': min_score,
            'max_complexity': max_score,
            'level_distribution': dict(level_counts),
            'domain_breakdown': dict(domain_breakdown),
            'recommendations': self._generate_recommendations(avg_score, level_counts)
        }

    def _generate_recommendations(
        self,
        avg_score: float,
        level_counts: Dict[str, int]
    ) -> List[str]:
        """Generate recommendations based on corpus analysis."""
        recommendations = []

        total = sum(level_counts.values())
        if total == 0:
            return recommendations

        trivial_pct = level_counts.get('trivial', 0) / total
        expert_pct = level_counts.get('expert', 0) / total

        if trivial_pct > 0.5:
            recommendations.append(
                "High proportion of trivial problems. Consider adding more challenging content."
            )

        if expert_pct < 0.1:
            recommendations.append(
                "Low proportion of expert problems. Add advanced topics for comprehensive coverage."
            )

        if avg_score < 0.4:
            recommendations.append(
                "Overall corpus is relatively simple. This may limit learning depth."
            )

        if avg_score > 0.7:
            recommendations.append(
                "Corpus is quite complex. Ensure foundational problems are included."
            )

        return recommendations

    # BDI Agent methods
    def update_beliefs(self, percept: Dict[str, Any] = None) -> None:
        """Update beliefs based on current state and percepts."""
        if self.score_history:
            scores = [h['score'] for h in self.score_history[-100:]]
            self.beliefs['avg_score'] = sum(scores) / len(scores)

            # Check if calibration needed (score distribution is skewed)
            trivial = sum(1 for s in scores if s < 0.2)
            expert = sum(1 for s in scores if s >= 0.8)

            if trivial / len(scores) > 0.7 or expert / len(scores) > 0.7:
                self.beliefs['calibration_needed'] = True
            else:
                self.beliefs['calibration_needed'] = False

    def deliberate(self) -> Optional[Intention]:
        """Deliberate on current beliefs to form intentions."""
        if self.beliefs.get('calibration_needed', False):
            return Intention(
                plan_id='recalibrate_scoring',
                steps=['analyze_distribution', 'adjust_weights', 'validate'],
                target_desire='balanced_scoring'
            )
        return None

    def execute_step(self) -> bool:
        """Execute one step of agent processing."""
        # Check blackboard for scoring requests
        if self.blackboard:
            # Would check for pending scoring requests
            pass
        return False

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a scoring task from the supervisor.

        Args:
            task_entry: Task with 'action', 'problem', 'domain', etc.

        Returns:
            Processing result
        """
        action = task_entry.get('action', 'score')

        if action == 'score':
            result = self.score(
                problem=task_entry.get('problem', ''),
                answer=task_entry.get('answer', ''),
                domain=task_entry.get('domain', 'unknown'),
                solve_time_ms=task_entry.get('solve_time_ms')
            )
            return result.to_dict()

        elif action == 'batch_score':
            results = self.batch_score(task_entry.get('problems', []))
            return {'scores': [r.to_dict() for r in results]}

        elif action == 'analyze':
            return self.analyze_corpus(task_entry.get('problems', []))

        elif action == 'get_stats':
            return self.get_stats()

        else:
            return {'error': f'Unknown action: {action}'}
