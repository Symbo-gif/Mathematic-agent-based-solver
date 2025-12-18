# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
TURING DEGREES SPECIALIST - Turing degrees, jump operator, Post's problem
=========================================================================

Manages tasks related to Turing reducibility, Turing degrees, and the jump operator.

CRITICAL ALGORITHMS:
-------------------
- Turing Reduction: Check if A ≤_T B (A is Turing-reducible to B)
- Jump Operator: Compute A' (jump of A)
- Degree Classification: Classify Turing degrees (0, 0', 0'', ...)
- Post's Problem: Analyze intermediate degrees between 0 and 0'

WHY THIS MATTERS:
----------------
Turing degrees are fundamental to:
- Classifying computational problems by relative difficulty
- Understanding the structure of unsolvable problems
- Measuring information content and computational power
- Foundation for reverse mathematics

CAPABILITIES:
------------
- Compute Turing reductions between sets
- Apply jump operator to compute halting information
- Classify Turing degrees
- Analyze Post's problem and intermediate degrees
- Verify degree inequalities
- Compute degree arithmetic (join, meet)
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class TuringDegreesSpecialist(BDIAgent):
    """
    Turing Degrees Specialist - Turing reducibility and jump operator

    DIRECTIVE:
    ---------
    Handle all Turing degree operations with emphasis on:
    - Turing reduction verification
    - Jump operator computation
    - Degree classification and comparison
    - Post's problem analysis

    KEY ALGORITHMS:
    --------------
    - Turing Reduction: Oracle-based reduction A ≤_T B
    - Jump Operator: A' = {e : φ_e^A(e) halts}
    - Degree Arithmetic: Join (a ⊕ b), meet (a ∧ b)

    OPERATIONS:
    ----------
    - compute_turing_reduction(problem_a, problem_b)
    - compute_jump_operator(degree)
    - classify_degree(problem)
    - analyze_posts_problem()
    - verify_degree_inequality(deg_a, deg_b)
    - compute_degree_join(deg_a, deg_b)
    """

    def __init__(self, agent_id='turing_degrees_specialist_001', df=None, blackboard=None):
        """
        Initialize Turing Degrees Specialist

        Args:
            agent_id: Unique identifier for this agent
            df: Directory Facilitator instance
            blackboard: Shared blackboard instance
        """
        super().__init__(agent_id)
        self.df = df
        self.blackboard = blackboard
        self.tasks_executed = 0
        self.recent_tasks = []
        self.degree_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.computability.turing_degrees',
                agent_id=self.agent_id,
                algorithm='turing_degrees',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process Turing degrees task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of Turing degrees operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'reduction')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'reduction':
                return self._process_turing_reduction(metadata)
            elif problem_type == 'jump':
                return self._process_jump_operator(metadata)
            elif problem_type == 'classify':
                return self._process_classify_degree(metadata)
            elif problem_type == 'posts_problem':
                return self._process_posts_problem(metadata)
            elif problem_type == 'degree_inequality':
                return self._process_degree_inequality(metadata)
            elif problem_type == 'degree_join':
                return self._process_degree_join(metadata)
            else:
                return self._process_turing_reduction(metadata)

        except Exception as e:
            return {
                'operation': 'turing_degrees',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_turing_reduction(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Turing reduction verification request"""
        problem_a = metadata.get('problem_a', 'computable')
        problem_b = metadata.get('problem_b', 'halting')

        result = self.compute_turing_reduction(problem_a, problem_b)
        return {
            'operation': 'turing_reduction',
            **result
        }

    def _process_jump_operator(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process jump operator computation request"""
        degree = metadata.get('degree', '0')

        result = self.compute_jump_operator(degree)
        return {
            'operation': 'jump_operator',
            **result
        }

    def _process_classify_degree(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process degree classification request"""
        problem = metadata.get('problem', 'halting')

        result = self.classify_degree(problem)
        return {
            'operation': 'classify_degree',
            **result
        }

    def _process_posts_problem(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Post's problem analysis request"""
        result = self.analyze_posts_problem()
        return {
            'operation': 'posts_problem_analysis',
            **result
        }

    def _process_degree_inequality(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process degree inequality verification request"""
        deg_a = metadata.get('deg_a', '0')
        deg_b = metadata.get('deg_b', "0'")

        result = self.verify_degree_inequality(deg_a, deg_b)
        return {
            'operation': 'verify_degree_inequality',
            **result
        }

    def _process_degree_join(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process degree join computation request"""
        deg_a = metadata.get('deg_a', '0')
        deg_b = metadata.get('deg_b', "0'")

        result = self.compute_degree_join(deg_a, deg_b)
        return {
            'operation': 'compute_degree_join',
            **result
        }

    def compute_turing_reduction(
        self,
        problem_a: str,
        problem_b: str
    ) -> Dict[str, Any]:
        """
        Check if problem A is Turing-reducible to problem B (A ≤_T B)

        A is Turing-reducible to B if A can be computed using B as an oracle.

        Args:
            problem_a: First problem name
            problem_b: Second problem name

        Returns:
            Dict containing:
                - reducible: Whether A ≤_T B
                - problem_a, problem_b: Problem names
                - explanation: Why/how reduction works
        """
        # Known Turing reductions
        reductions = {
            ('computable', 'computable'): (True, 'Any computable set reduces to any other'),
            ('computable', 'halting'): (True, 'Computable sets reduce to halting problem'),
            ('halting', 'halting'): (True, 'Halting problem reduces to itself (trivially)'),
            ('halting', 'computable'): (False, 'Halting problem does not reduce to computable sets'),
            ('totality', 'halting'): (False, 'Totality problem (Π₂⁰) does not reduce to halting (Σ₁⁰)'),
            ('halting', 'totality'): (True, 'Halting reduces to totality (Σ₁⁰ ≤ Π₂⁰ via complement)'),
            ('jump', 'original'): (False, "Jump A' does not reduce to A"),
            ('original', 'jump'): (True, 'Original A reduces to its jump A\''),
        }

        key = (problem_a, problem_b)
        if key in reductions:
            reducible, explanation = reductions[key]
            return {
                'reducible': reducible,
                'problem_a': problem_a,
                'problem_b': problem_b,
                'notation': f'{problem_a} {"≤_T" if reducible else "≰_T"} {problem_b}',
                'explanation': explanation
            }
        else:
            # Generic analysis
            return {
                'reducible': None,
                'problem_a': problem_a,
                'problem_b': problem_b,
                'explanation': f'Reduction {problem_a} ≤_T {problem_b} not determined',
                'note': 'Turing reduction requires oracle computation analysis'
            }

    def compute_jump_operator(self, degree: str) -> Dict[str, Any]:
        """
        Compute the jump of a Turing degree

        The jump operator: A' = {e : φ_e^A(e) halts}
        (The halting problem relative to A)

        Args:
            degree: Degree notation (e.g., '0', "0'", "0''")

        Returns:
            Dict containing:
                - jump: The jump degree
                - original: Original degree
                - explanation: Description
        """
        # Compute jump
        if degree == '0':
            jump = "0'"
            explanation = "Jump of computable: 0' = halting problem (Turing degrees of K)"
        elif degree == "0'":
            jump = "0''"
            explanation = "Double jump: 0'' = totality problem (halting problem for 0'-oracle machines)"
        elif degree == "0''":
            jump = "0'''"
            explanation = "Triple jump: 0''' (third level of arithmetic hierarchy)"
        elif degree.startswith("0") and degree.endswith("'"):
            # Count primes
            num_primes = degree.count("'")
            jump = "0" + "'" * (num_primes + 1)
            explanation = f"{num_primes + 1}-fold jump: {jump} (level {num_primes + 1} of arithmetic hierarchy)"
        else:
            # Generic degree
            jump = f"{degree}'"
            explanation = f"Jump of {degree} is {degree}' (halting problem relative to {degree})"

        return {
            'jump': jump,
            'original': degree,
            'explanation': explanation,
            'properties': [
                f'{degree} <_T {jump} (strictly greater)',
                f'{jump} is Σ₁⁰-complete relative to {degree}',
                'Jump operator is definable but not computable'
            ]
        }

    def classify_degree(self, problem: str) -> Dict[str, Any]:
        """
        Classify the Turing degree of a problem

        Args:
            problem: Problem name

        Returns:
            Dict containing:
                - degree: Turing degree
                - problem: Problem name
                - hierarchy_level: Position in arithmetic hierarchy
                - explanation: Classification details
        """
        # Known degree classifications
        classifications = {
            'computable': {
                'degree': '0',
                'hierarchy': 'Δ₁⁰ (computable)',
                'explanation': 'Computable sets have degree 0'
            },
            'halting': {
                'degree': "0'",
                'hierarchy': 'Σ₁⁰-complete',
                'explanation': 'Halting problem has degree 0\' (first jump)'
            },
            'totality': {
                'degree': "0''",
                'hierarchy': 'Π₂⁰-complete',
                'explanation': 'Totality problem has degree 0\'\' (second jump)'
            },
            'finite_set': {
                'degree': '0',
                'hierarchy': 'Δ₁⁰ (computable)',
                'explanation': 'All finite sets are computable (degree 0)'
            },
            'arithmetic': {
                'degree': '≤ 0^(ω)',
                'hierarchy': 'Arithmetic hierarchy',
                'explanation': 'Arithmetically definable sets have degrees ≤ 0^(ω)'
            }
        }

        if problem in classifications:
            info = classifications[problem]
            return {
                'problem': problem,
                'degree': info['degree'],
                'hierarchy_level': info['hierarchy'],
                'explanation': info['explanation']
            }
        else:
            return {
                'problem': problem,
                'degree': 'unknown',
                'hierarchy_level': 'unknown',
                'explanation': f'Degree classification unknown for {problem}'
            }

    def analyze_posts_problem(self) -> Dict[str, Any]:
        """
        Analyze Post's problem

        Post's Problem: Does there exist an intermediate Turing degree strictly between 0 and 0'?
        Answer (Friedberg-Muchnik 1956): YES

        Returns:
            Dict containing:
                - problem: Problem statement
                - answer: YES (solved)
                - solution_method: Priority method
                - explanation: Details
        """
        return {
            'problem': "Post's Problem: ∃d (0 <_T d <_T 0')?",
            'answer': 'YES',
            'solved_by': 'Friedberg and Muchnik (independently, 1956-1957)',
            'solution_method': 'Priority method (finite injury)',
            'explanation': 'There exist incomparable c.e. sets A and B with degrees strictly between 0 and 0\'',
            'key_result': 'The Turing degrees are not linearly ordered',
            'structure': {
                'upper_semilattice': True,
                'lattice': False,
                'dense': True,
                'countable_ideal': True
            },
            'open_problems': [
                'Density of Turing degrees (solved: true)',
                'Definability of Turing jump (solved: no first-order definition)',
                'Biinterpretability of degree structures'
            ]
        }

    def verify_degree_inequality(
        self,
        deg_a: str,
        deg_b: str
    ) -> Dict[str, Any]:
        """
        Verify Turing degree inequality deg_a ≤_T deg_b

        Args:
            deg_a, deg_b: Degree notations

        Returns:
            Dict containing:
                - inequality_holds: Boolean
                - deg_a, deg_b: Degrees
                - explanation: Justification
        """
        # Parse degree levels (count primes)
        def degree_level(deg):
            """Extract the jump hierarchy level from degree notation (count primes in 0', 0'', etc.)."""
            if deg == '0':
                return 0
            elif deg.startswith('0') and all(c == "'" for c in deg[1:]):
                return len(deg) - 1
            else:
                return None

        level_a = degree_level(deg_a)
        level_b = degree_level(deg_b)

        if level_a is not None and level_b is not None:
            inequality_holds = level_a <= level_b
            return {
                'inequality_holds': inequality_holds,
                'deg_a': deg_a,
                'deg_b': deg_b,
                'notation': f'{deg_a} {"≤_T" if inequality_holds else "≰_T"} {deg_b}',
                'explanation': f'Level {level_a} {"≤" if inequality_holds else ">"} level {level_b} in jump hierarchy'
            }
        else:
            return {
                'inequality_holds': None,
                'deg_a': deg_a,
                'deg_b': deg_b,
                'explanation': 'Cannot determine inequality for non-standard degrees'
            }

    def compute_degree_join(
        self,
        deg_a: str,
        deg_b: str
    ) -> Dict[str, Any]:
        """
        Compute the join (supremum) of two Turing degrees

        The join a ⊕ b is the least upper bound of a and b.

        Args:
            deg_a, deg_b: Degree notations

        Returns:
            Dict containing:
                - join: The join degree
                - deg_a, deg_b: Input degrees
                - explanation: Description
        """
        # Parse degree levels
        def degree_level(deg):
            """Extract the jump hierarchy level from degree notation (count primes in 0', 0'', etc.)."""
            if deg == '0':
                return 0
            elif deg.startswith('0') and all(c == "'" for c in deg[1:]):
                return len(deg) - 1
            else:
                return None

        level_a = degree_level(deg_a)
        level_b = degree_level(deg_b)

        if level_a is not None and level_b is not None:
            # Join is maximum level
            join_level = max(level_a, level_b)
            join = '0' + "'" * join_level
            return {
                'join': join,
                'deg_a': deg_a,
                'deg_b': deg_b,
                'notation': f'{deg_a} ⊕ {deg_b} = {join}',
                'explanation': f'Join of degrees at levels {level_a} and {level_b} is level {join_level}',
                'properties': [
                    f'{deg_a} ≤_T {join}',
                    f'{deg_b} ≤_T {join}',
                    f'{join} is least upper bound'
                ]
            }
        else:
            return {
                'join': f'{deg_a} ⊕ {deg_b}',
                'deg_a': deg_a,
                'deg_b': deg_b,
                'explanation': 'Join computation for non-standard degrees',
                'note': 'Join always exists (Turing degrees form upper semilattice)'
            }

    def compute_degree_meet(
        self,
        deg_a: str,
        deg_b: str
    ) -> Dict[str, Any]:
        """
        Attempt to compute the meet (infimum) of two Turing degrees

        Note: Turing degrees do NOT always have meets (not a lattice).

        Args:
            deg_a, deg_b: Degree notations

        Returns:
            Dict containing analysis of potential meet
        """
        return {
            'deg_a': deg_a,
            'deg_b': deg_b,
            'meet_exists': None,
            'explanation': 'Turing degrees do not form a lattice - meets do not always exist',
            'note': 'The structure of Turing degrees is an upper semilattice, not a lattice',
            'example': 'Incomparable c.e. degrees (from Post\'s problem solution) have no meet'
        }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new Turing degree problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Optimize cache if too many entries
        if self.tasks_executed > 100 and len(self.degree_cache) > 50:
            intentions.append(Intention(
                action='optimize_cache',
                priority=1,
                description='Clear old degree cache entries'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'optimize_cache':
            # Keep only recent cache entries
            if len(self.degree_cache) > 50:
                keys = list(self.degree_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.degree_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.degree_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
