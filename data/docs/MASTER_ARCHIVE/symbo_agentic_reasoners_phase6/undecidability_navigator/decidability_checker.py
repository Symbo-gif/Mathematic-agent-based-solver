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
Decidability Checker
=====================

Agent 4.1 of the Undecidability Navigator

Meta-analyst that inspects the logical structure of a problem before
the Deep Search Team commits resources. Classifies theories into:
- Decidable (e.g., Presburger Arithmetic, Real Closed Fields)
- Semi-decidable (e.g., First-Order Theorem Proving)
- Undecidable (e.g., Peano Arithmetic, Diophantine Equations)

Protocol: If undecidable, flags system to switch from Solver Mode to
Heuristic Search Mode with resource bounds.

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 4
Reference: Phase_6_Build_Order_Breakdown.md, Step 4
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime
from enum import Enum


class DecidabilityClass(Enum):
    """Classification of decidability for a problem"""
    DECIDABLE = 'decidable'
    SEMI_DECIDABLE = 'semi_decidable'
    UNDECIDABLE = 'undecidable'
    UNKNOWN = 'unknown'


class SearchMode(Enum):
    """Recommended search mode"""
    SOLVER = 'solver'                    # Full search is safe
    HEURISTIC = 'heuristic_search'       # Bounded heuristic search
    HUMAN_IN_LOOP = 'human_in_loop'      # Needs human guidance
    APPROXIMATE = 'approximate'           # Seek approximate solutions


@dataclass
class DecidabilityAssessment:
    """
    Assessment result from Decidability Checker.

    Attributes:
        problem_id: ID of the assessed problem
        decidability_class: Decidability classification
        theory_classification: Identified logical theory
        confidence: Confidence in the assessment (0-1)
        reasoning: Explanation for the classification
        recommended_mode: Recommended search mode
        resource_bounds: Suggested resource limits
        risk_factors: Identified risk factors
    """
    problem_id: str
    decidability_class: DecidabilityClass
    theory_classification: str
    confidence: float
    reasoning: str
    recommended_mode: SearchMode
    resource_bounds: Optional[Dict[str, int]] = None
    risk_factors: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'problem_id': self.problem_id,
            'decidability_class': self.decidability_class.value,
            'theory_classification': self.theory_classification,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'recommended_mode': self.recommended_mode.value,
            'resource_bounds': self.resource_bounds,
            'risk_factors': self.risk_factors
        }


class DecidabilityChecker:
    """
    Agent 4.1: Decidability Checker - Meta-analyst for decidability

    Classifies problems by decidability before committing search resources.
    Uses knowledge of decidable/undecidable theories to protect the system
    from infinite loops on undecidable problems.

    Key capabilities:
    - Theory classification based on problem structure
    - Decidability assessment with confidence scoring
    - Resource bound recommendations
    - Semi-decision procedure selection

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    # Known decidable theories
    DECIDABLE_THEORIES = {
        'presburger_arithmetic': {
            'description': 'First-order theory of natural numbers with addition',
            'indicators': ['addition', 'linear', 'no_multiplication'],
            'complexity': 'DOUBLY_EXPONENTIAL'
        },
        'real_closed_fields': {
            'description': 'First-order theory of real numbers with +, *, <',
            'indicators': ['polynomial', 'real', 'quantifier_elimination'],
            'complexity': 'DOUBLY_EXPONENTIAL'
        },
        'propositional_logic': {
            'description': 'Propositional satisfiability',
            'indicators': ['boolean', 'and', 'or', 'not', 'no_quantifier'],
            'complexity': 'NP_COMPLETE'
        },
        'monadic_second_order_logic_trees': {
            'description': 'MSO on trees',
            'indicators': ['tree', 'monadic', 'second_order'],
            'complexity': 'NON_ELEMENTARY'
        },
        'linear_arithmetic': {
            'description': 'Linear arithmetic over rationals/reals',
            'indicators': ['linear', 'arithmetic', 'inequality'],
            'complexity': 'POLYNOMIAL'
        },
        'boolean_satisfiability': {
            'description': 'SAT problem',
            'indicators': ['boolean', 'satisfiability', 'cnf'],
            'complexity': 'NP_COMPLETE'
        },
        'regular_languages': {
            'description': 'Membership in regular languages',
            'indicators': ['regular', 'automaton', 'regex'],
            'complexity': 'LINEAR'
        }
    }

    # Known undecidable theories
    UNDECIDABLE_THEORIES = {
        'peano_arithmetic': {
            'description': 'Full first-order arithmetic with multiplication',
            'indicators': ['multiplication', 'natural_numbers', 'induction'],
            'reason': "Gödel's First Incompleteness Theorem"
        },
        'diophantine_equations': {
            'description': 'Integer solutions to polynomial equations',
            'indicators': ['polynomial', 'integer_solutions', 'diophantine'],
            'reason': "Hilbert's 10th Problem (Matiyasevich)"
        },
        'first_order_logic': {
            'description': 'Full first-order logic validity',
            'indicators': ['universal', 'existential', 'predicates', 'functions'],
            'reason': "Church-Turing Theorem"
        },
        'word_problem_groups': {
            'description': 'Word problem in finitely presented groups',
            'indicators': ['group', 'word_problem', 'presentation'],
            'reason': "Novikov-Boone Theorem"
        },
        'halting_problem': {
            'description': 'Whether a program halts',
            'indicators': ['termination', 'loop', 'recursion', 'halting'],
            'reason': "Turing's Halting Theorem"
        },
        'post_correspondence': {
            'description': 'Post Correspondence Problem',
            'indicators': ['string_matching', 'sequence', 'correspondence'],
            'reason': "Emil Post (1946)"
        },
        'validity_first_order_logic': {
            'description': 'Validity in first-order logic',
            'indicators': ['validity', 'all_models', 'tautology'],
            'reason': "Undecidable reduction from halting"
        },
        'kolmogorov_complexity': {
            'description': 'Computing Kolmogorov complexity',
            'indicators': ['compression', 'shortest_program', 'complexity'],
            'reason': "Uncomputability theorem"
        }
    }

    # Semi-decidable theories (recognizable but not co-recognizable)
    SEMI_DECIDABLE_THEORIES = {
        'theorem_proving_first_order': {
            'description': 'First-order theorem proving',
            'indicators': ['theorem', 'proof', 'first_order'],
            'note': 'Can find proofs but cannot prove unprovability'
        },
        'satisfiability_first_order': {
            'description': 'First-order satisfiability',
            'indicators': ['satisfiable', 'model', 'first_order'],
            'note': 'Can find models but cannot prove unsatisfiability'
        },
        'type_inhabitation': {
            'description': 'Type inhabitation in rich type systems',
            'indicators': ['type', 'inhabit', 'lambda'],
            'note': 'Can find inhabitants but cannot prove emptiness'
        }
    }

    def __init__(self):
        """Initialize the Decidability Checker."""
        self.assessment_cache: Dict[str, DecidabilityAssessment] = {}

        # Statistics
        self.stats = {
            'assessments': 0,
            'decidable': 0,
            'semi_decidable': 0,
            'undecidable': 0,
            'unknown': 0,
            'cache_hits': 0
        }

    def assess(self, problem) -> DecidabilityAssessment:
        """
        Assess decidability of a problem before committing resources.

        Args:
            problem: CandidateConjecture or similar problem object

        Returns:
            DecidabilityAssessment with classification and recommendations
        """
        # Get problem ID
        problem_id = getattr(problem, 'conjecture_id', str(id(problem)))

        # Check cache
        if problem_id in self.assessment_cache:
            self.stats['cache_hits'] += 1
            return self.assessment_cache[problem_id]

        self.stats['assessments'] += 1

        # Extract problem content
        content = self._extract_content(problem)

        # Classify the theory
        theory, confidence = self._classify_theory(content)

        # Determine decidability
        decidability = self._determine_decidability(theory)

        # Update stats
        self.stats[decidability.value] = self.stats.get(decidability.value, 0) + 1

        # Generate reasoning
        reasoning = self._generate_reasoning(theory, decidability)

        # Get risk factors
        risk_factors = self._identify_risks(content, theory)

        # Recommend search mode
        recommended_mode = self._recommend_mode(decidability, risk_factors)

        # Compute resource bounds
        resource_bounds = self._compute_bounds(decidability, content, risk_factors)

        assessment = DecidabilityAssessment(
            problem_id=problem_id,
            decidability_class=decidability,
            theory_classification=theory,
            confidence=confidence,
            reasoning=reasoning,
            recommended_mode=recommended_mode,
            resource_bounds=resource_bounds,
            risk_factors=risk_factors
        )

        self.assessment_cache[problem_id] = assessment
        return assessment

    def _extract_content(self, problem) -> str:
        """Extract content string from problem object"""
        if hasattr(problem, 'source_theorem'):
            theorem = problem.source_theorem
            content = f"{theorem.domain} {theorem.to_natural_language()}"
            if hasattr(problem, 'lean4_statement') and problem.lean4_statement:
                content += f" {problem.lean4_statement}"
            return content
        elif hasattr(problem, 'goal'):
            return str(problem.goal)
        else:
            return str(problem)

    def _classify_theory(self, content: str) -> Tuple[str, float]:
        """Classify the logical theory of the content"""
        content_lower = content.lower()

        # Score each decidable theory
        decidable_scores = {}
        for theory, info in self.DECIDABLE_THEORIES.items():
            score = sum(1 for ind in info['indicators'] if ind in content_lower)
            if score > 0:
                decidable_scores[theory] = score

        # Score each undecidable theory
        undecidable_scores = {}
        for theory, info in self.UNDECIDABLE_THEORIES.items():
            score = sum(1 for ind in info['indicators'] if ind in content_lower)
            if score > 0:
                undecidable_scores[theory] = score

        # Score semi-decidable
        semi_scores = {}
        for theory, info in self.SEMI_DECIDABLE_THEORIES.items():
            score = sum(1 for ind in info['indicators'] if ind in content_lower)
            if score > 0:
                semi_scores[theory] = score

        # Apply domain-based heuristics
        if 'number_theory' in content_lower:
            undecidable_scores['peano_arithmetic'] = undecidable_scores.get('peano_arithmetic', 0) + 2
        if 'geometry' in content_lower or 'real' in content_lower:
            decidable_scores['real_closed_fields'] = decidable_scores.get('real_closed_fields', 0) + 2
        if 'linear' in content_lower and 'arithmetic' in content_lower:
            decidable_scores['linear_arithmetic'] = decidable_scores.get('linear_arithmetic', 0) + 3

        # Choose best match
        all_scores = {}
        all_scores.update(decidable_scores)
        all_scores.update(undecidable_scores)
        all_scores.update(semi_scores)

        if not all_scores:
            return 'unknown_theory', 0.3

        best_theory = max(all_scores, key=all_scores.get)
        max_score = all_scores[best_theory]

        # Confidence based on score
        confidence = min(0.95, 0.5 + max_score * 0.1)

        return best_theory, confidence

    def _determine_decidability(self, theory: str) -> DecidabilityClass:
        """Determine decidability class from theory"""
        if theory in self.DECIDABLE_THEORIES:
            return DecidabilityClass.DECIDABLE
        elif theory in self.UNDECIDABLE_THEORIES:
            return DecidabilityClass.UNDECIDABLE
        elif theory in self.SEMI_DECIDABLE_THEORIES:
            return DecidabilityClass.SEMI_DECIDABLE
        else:
            return DecidabilityClass.UNKNOWN

    def _generate_reasoning(self, theory: str, decidability: DecidabilityClass) -> str:
        """Generate explanation for the assessment"""
        if decidability == DecidabilityClass.DECIDABLE:
            info = self.DECIDABLE_THEORIES.get(theory, {})
            desc = info.get('description', theory)
            complexity = info.get('complexity', 'UNKNOWN')
            return f"Problem is in {theory} ({desc}), which is decidable with {complexity} complexity. Full search is safe."

        elif decidability == DecidabilityClass.UNDECIDABLE:
            info = self.UNDECIDABLE_THEORIES.get(theory, {})
            desc = info.get('description', theory)
            reason = info.get('reason', 'theoretical limits')
            return f"Problem involves {theory} ({desc}), which is undecidable ({reason}). Must use bounded heuristic search."

        elif decidability == DecidabilityClass.SEMI_DECIDABLE:
            info = self.SEMI_DECIDABLE_THEORIES.get(theory, {})
            desc = info.get('description', theory)
            note = info.get('note', 'may not terminate on negative instances')
            return f"Problem is semi-decidable ({desc}). {note}. Use bounded search with timeout."

        else:
            return f"Unable to classify {theory}. Proceed with caution using bounded resources."

    def _identify_risks(self, content: str, theory: str) -> List[str]:
        """Identify risk factors that might cause infinite loops"""
        risks = []
        content_lower = content.lower()

        # General risks
        if 'forall' in content_lower or '∀' in content:
            risks.append('Universal quantification may require infinite checking')

        if 'exists' in content_lower or '∃' in content:
            risks.append('Existential quantification may require unbounded search')

        if 'recursion' in content_lower or 'induction' in content_lower:
            risks.append('Recursive/inductive structure may not terminate')

        if 'infinite' in content_lower:
            risks.append('Problem explicitly mentions infinity')

        if theory in self.UNDECIDABLE_THEORIES:
            info = self.UNDECIDABLE_THEORIES[theory]
            risks.append(f"Theory {theory} is undecidable: {info.get('reason', 'known undecidable')}")

        # Specific patterns
        if re.search(r'\bx\s*=\s*y\s*\*\s*z\b', content_lower):
            risks.append('Multiplication of variables suggests Diophantine-like problem')

        return risks

    def _recommend_mode(self, decidability: DecidabilityClass, risks: List[str]) -> SearchMode:
        """Recommend search mode based on decidability and risks"""
        if decidability == DecidabilityClass.DECIDABLE:
            return SearchMode.SOLVER

        elif decidability == DecidabilityClass.UNDECIDABLE:
            if len(risks) > 3:
                return SearchMode.HUMAN_IN_LOOP
            return SearchMode.HEURISTIC

        elif decidability == DecidabilityClass.SEMI_DECIDABLE:
            return SearchMode.HEURISTIC

        else:
            if risks:
                return SearchMode.HEURISTIC
            return SearchMode.SOLVER  # Optimistic default

    def _compute_bounds(
        self,
        decidability: DecidabilityClass,
        content: str,
        risks: List[str]
    ) -> Optional[Dict[str, int]]:
        """Compute resource bounds for search"""
        if decidability == DecidabilityClass.DECIDABLE:
            return None  # No bounds needed

        # Base bounds
        bounds = {
            'max_depth': 30,
            'max_expansions': 10000,
            'timeout_seconds': 300,
            'max_memory_mb': 4096
        }

        # Adjust based on content complexity
        content_length = len(content)
        if content_length > 500:
            bounds['max_depth'] = int(bounds['max_depth'] * 1.5)
            bounds['max_expansions'] = int(bounds['max_expansions'] * 1.5)

        # Reduce bounds for risky problems
        risk_factor = len(risks)
        if risk_factor > 0:
            reduction = max(0.5, 1.0 - risk_factor * 0.1)
            bounds['max_depth'] = int(bounds['max_depth'] * reduction)
            bounds['max_expansions'] = int(bounds['max_expansions'] * reduction)
            bounds['timeout_seconds'] = int(bounds['timeout_seconds'] * reduction)

        return bounds

    def is_safe_to_search(self, problem, threshold: float = 0.7) -> Tuple[bool, str]:
        """
        Quick check if it's safe to commit search resources.

        Args:
            problem: Problem to check
            threshold: Confidence threshold for decidability

        Returns:
            (is_safe, reason)
        """
        assessment = self.assess(problem)

        if assessment.decidability_class == DecidabilityClass.DECIDABLE:
            return True, "Problem is decidable - safe to search"

        elif assessment.decidability_class == DecidabilityClass.UNDECIDABLE:
            return False, f"Problem is undecidable: {assessment.reasoning}"

        elif assessment.decidability_class == DecidabilityClass.SEMI_DECIDABLE:
            return True, "Problem is semi-decidable - search may not terminate"

        else:
            if assessment.confidence < threshold:
                return True, "Unknown decidability but low risk - proceed with caution"
            return True, "Unknown decidability - proceed with bounded search"

    def get_statistics(self) -> Dict[str, Any]:
        """Get checker statistics"""
        total = self.stats['assessments']
        if total > 0:
            decidable_rate = self.stats['decidable'] / total * 100
            undecidable_rate = self.stats['undecidable'] / total * 100
        else:
            decidable_rate = undecidable_rate = 0

        return {
            **self.stats,
            'cache_size': len(self.assessment_cache),
            'decidable_rate_percent': round(decidable_rate, 2),
            'undecidable_rate_percent': round(undecidable_rate, 2)
        }

    def reset(self):
        """Reset checker state"""
        self.assessment_cache.clear()
        for key in self.stats:
            self.stats[key] = 0

    def health_check(self) -> bool:
        """Check if checker is healthy"""
        return len(self.DECIDABLE_THEORIES) > 0 and len(self.UNDECIDABLE_THEORIES) > 0
