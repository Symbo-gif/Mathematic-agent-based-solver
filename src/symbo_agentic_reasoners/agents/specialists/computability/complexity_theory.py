# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
# Licensed under the Apache License, Version 2.0

"""
COMPLEXITY THEORY SPECIALIST - P vs NP, complexity classes, reductions
======================================================================

Manages tasks related to computational complexity, complexity classes, and complexity-theoretic reductions.

CRITICAL ALGORITHMS:
-------------------
- Time Complexity Analysis: Analyze algorithm time complexity
- Space Complexity Analysis: Analyze algorithm space requirements
- Reduction Verification: Verify polynomial-time reductions
- Complexity Class Classification: Classify problems into P, NP, PSPACE, etc.

WHY THIS MATTERS:
----------------
Complexity theory is fundamental to:
- Understanding computational feasibility
- P vs NP problem (Millennium Prize)
- Algorithm efficiency analysis
- Cryptographic hardness assumptions

CAPABILITIES:
------------
- Analyze time and space complexity of algorithms
- Classify problems into complexity classes
- Verify polynomial-time reductions
- Analyze NP-completeness and hardness
- Compute complexity hierarchy relationships
- Assess problem tractability
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class ComplexityTheorySpecialist(BDIAgent):
    """
    Complexity Theory Specialist - P vs NP, complexity classes

    DIRECTIVE:
    ---------
    Handle all complexity theory operations with emphasis on:
    - Time and space complexity analysis
    - Complexity class classification
    - Reduction verification
    - Tractability assessment

    KEY ALGORITHMS:
    --------------
    - Complexity Analysis: Asymptotic analysis
    - Reduction Verification: Polynomial-time reductions
    - Class Membership: Determine complexity class membership

    OPERATIONS:
    ----------
    - analyze_time_complexity(algorithm)
    - analyze_space_complexity(algorithm)
    - verify_reduction(problem_a, problem_b, reduction_type)
    - classify_complexity_class(problem)
    - assess_tractability(problem)
    - compute_hierarchy_relations()
    """

    def __init__(self, agent_id='complexity_theory_specialist_001', df=None, blackboard=None):
        """
        Initialize Complexity Theory Specialist

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
        self.complexity_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.computability.complexity_theory',
                agent_id=self.agent_id,
                algorithm='complexity_theory',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process complexity theory task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of complexity theory operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'time_complexity')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'time_complexity':
                return self._process_time_complexity(metadata)
            elif problem_type == 'space_complexity':
                return self._process_space_complexity(metadata)
            elif problem_type == 'reduction':
                return self._process_reduction(metadata)
            elif problem_type == 'classify':
                return self._process_classify_complexity(metadata)
            elif problem_type == 'tractability':
                return self._process_tractability(metadata)
            elif problem_type == 'hierarchy':
                return self._process_hierarchy(metadata)
            else:
                return self._process_time_complexity(metadata)

        except Exception as e:
            return {
                'operation': 'complexity_theory',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_time_complexity(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process time complexity analysis request"""
        algorithm = metadata.get('algorithm', 'bubble_sort')

        result = self.analyze_time_complexity(algorithm)
        return {
            'operation': 'time_complexity_analysis',
            **result
        }

    def _process_space_complexity(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process space complexity analysis request"""
        algorithm = metadata.get('algorithm', 'bubble_sort')

        result = self.analyze_space_complexity(algorithm)
        return {
            'operation': 'space_complexity_analysis',
            **result
        }

    def _process_reduction(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process reduction verification request"""
        problem_a = metadata.get('problem_a', '3SAT')
        problem_b = metadata.get('problem_b', 'CLIQUE')
        reduction_type = metadata.get('reduction_type', 'polynomial')

        result = self.verify_reduction(problem_a, problem_b, reduction_type)
        return {
            'operation': 'verify_reduction',
            **result
        }

    def _process_classify_complexity(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process complexity class classification request"""
        problem = metadata.get('problem', 'SAT')

        result = self.classify_complexity_class(problem)
        return {
            'operation': 'classify_complexity_class',
            **result
        }

    def _process_tractability(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process tractability assessment request"""
        problem = metadata.get('problem', '3SAT')

        result = self.assess_tractability(problem)
        return {
            'operation': 'assess_tractability',
            **result
        }

    def _process_hierarchy(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process hierarchy relations request"""
        result = self.compute_hierarchy_relations()
        return {
            'operation': 'compute_hierarchy_relations',
            **result
        }

    def analyze_time_complexity(self, algorithm: str) -> Dict[str, Any]:
        """
        Analyze time complexity of an algorithm

        Args:
            algorithm: Algorithm name or description

        Returns:
            Dict containing:
                - algorithm: Algorithm name
                - time_complexity: Big-O notation
                - best_case, average_case, worst_case: Complexity bounds
                - explanation: Analysis
        """
        # Known algorithm complexities
        complexities = {
            'bubble_sort': {
                'best': 'O(n)',
                'average': 'O(n²)',
                'worst': 'O(n²)',
                'explanation': 'Quadratic time due to nested loops'
            },
            'merge_sort': {
                'best': 'O(n log n)',
                'average': 'O(n log n)',
                'worst': 'O(n log n)',
                'explanation': 'Divide-and-conquer with log n levels'
            },
            'quick_sort': {
                'best': 'O(n log n)',
                'average': 'O(n log n)',
                'worst': 'O(n²)',
                'explanation': 'Average case is divide-and-conquer, worst case with bad pivots'
            },
            'binary_search': {
                'best': 'O(1)',
                'average': 'O(log n)',
                'worst': 'O(log n)',
                'explanation': 'Halves search space at each step'
            },
            'linear_search': {
                'best': 'O(1)',
                'average': 'O(n)',
                'worst': 'O(n)',
                'explanation': 'Must check each element'
            },
            'dijkstra': {
                'best': 'O((V + E) log V)',
                'average': 'O((V + E) log V)',
                'worst': 'O((V + E) log V)',
                'explanation': 'Priority queue operations for graph with V vertices, E edges'
            },
            'matrix_multiply': {
                'best': 'O(n³)',
                'average': 'O(n³)',
                'worst': 'O(n³)',
                'explanation': 'Triple nested loops for n×n matrices (naïve algorithm)'
            },
            'traveling_salesman': {
                'best': 'O(n!)',
                'average': 'O(n!)',
                'worst': 'O(n!)',
                'explanation': 'Must check all permutations (brute force)'
            }
        }

        if algorithm in complexities:
            info = complexities[algorithm]
            return {
                'algorithm': algorithm,
                'best_case': info['best'],
                'average_case': info['average'],
                'worst_case': info['worst'],
                'explanation': info['explanation']
            }
        else:
            return {
                'algorithm': algorithm,
                'time_complexity': 'unknown',
                'explanation': f'Time complexity analysis not available for {algorithm}'
            }

    def analyze_space_complexity(self, algorithm: str) -> Dict[str, Any]:
        """
        Analyze space complexity of an algorithm

        Args:
            algorithm: Algorithm name or description

        Returns:
            Dict containing:
                - algorithm: Algorithm name
                - space_complexity: Space usage
                - explanation: Analysis
        """
        # Known algorithm space complexities
        space_complexities = {
            'bubble_sort': {
                'space': 'O(1)',
                'explanation': 'In-place sorting, constant extra space'
            },
            'merge_sort': {
                'space': 'O(n)',
                'explanation': 'Requires temporary arrays for merging'
            },
            'quick_sort': {
                'space': 'O(log n)',
                'explanation': 'Recursion stack depth (average case)'
            },
            'binary_search': {
                'space': 'O(1)',
                'explanation': 'Only needs a few variables (iterative)'
            },
            'dijkstra': {
                'space': 'O(V)',
                'explanation': 'Priority queue and distance array for V vertices'
            },
            'dynamic_programming': {
                'space': 'O(n²)',
                'explanation': 'Typical DP table for 2D problems'
            }
        }

        if algorithm in space_complexities:
            info = space_complexities[algorithm]
            return {
                'algorithm': algorithm,
                'space_complexity': info['space'],
                'explanation': info['explanation']
            }
        else:
            return {
                'algorithm': algorithm,
                'space_complexity': 'unknown',
                'explanation': f'Space complexity analysis not available for {algorithm}'
            }

    def verify_reduction(
        self,
        problem_a: str,
        problem_b: str,
        reduction_type: str = 'polynomial'
    ) -> Dict[str, Any]:
        """
        Verify reduction from problem A to problem B

        Args:
            problem_a: Source problem
            problem_b: Target problem
            reduction_type: Type of reduction ('polynomial', 'logspace', etc.)

        Returns:
            Dict containing:
                - valid: Whether reduction is valid
                - problem_a, problem_b: Problem names
                - reduction_type: Type of reduction
                - explanation: Details
        """
        # Known polynomial-time reductions
        poly_reductions = {
            ('3SAT', 'CLIQUE'): (True, 'Cook-Levin: 3SAT reduces to CLIQUE in polynomial time'),
            ('3SAT', 'VERTEX_COVER'): (True, '3SAT reduces to VERTEX_COVER (NP-complete)'),
            ('SAT', '3SAT'): (True, 'SAT reduces to 3SAT by clause splitting'),
            ('CLIQUE', 'INDEPENDENT_SET'): (True, 'Complement reduction: CLIQUE to INDEPENDENT_SET'),
            ('HAMILTONIAN_CYCLE', 'TSP'): (True, 'HAMILTONIAN_CYCLE reduces to TSP decision problem'),
            ('SUBSET_SUM', 'KNAPSACK'): (True, 'SUBSET_SUM is special case of KNAPSACK'),
        }

        key = (problem_a, problem_b)
        if reduction_type == 'polynomial' and key in poly_reductions:
            valid, explanation = poly_reductions[key]
            return {
                'valid': valid,
                'problem_a': problem_a,
                'problem_b': problem_b,
                'reduction_type': reduction_type,
                'notation': f'{problem_a} ≤_p {problem_b}',
                'explanation': explanation
            }
        else:
            return {
                'valid': None,
                'problem_a': problem_a,
                'problem_b': problem_b,
                'reduction_type': reduction_type,
                'explanation': f'Reduction {problem_a} to {problem_b} not determined'
            }

    def classify_complexity_class(self, problem: str) -> Dict[str, Any]:
        """
        Classify problem into complexity class

        Args:
            problem: Problem name

        Returns:
            Dict containing:
                - problem: Problem name
                - complexity_class: Complexity class (P, NP, NP-complete, etc.)
                - explanation: Classification details
        """
        # Known complexity class memberships
        classifications = {
            'SORTING': {
                'class': 'P',
                'explanation': 'Sorting is in P (O(n log n) algorithms exist)'
            },
            'SHORTEST_PATH': {
                'class': 'P',
                'explanation': 'Shortest path is in P (Dijkstra, Bellman-Ford)'
            },
            'SAT': {
                'class': 'NP-complete',
                'explanation': 'Boolean satisfiability is NP-complete (Cook-Levin theorem)'
            },
            '3SAT': {
                'class': 'NP-complete',
                'explanation': '3SAT is NP-complete, canonical NP-complete problem'
            },
            'CLIQUE': {
                'class': 'NP-complete',
                'explanation': 'Finding clique of size k is NP-complete'
            },
            'HAMILTONIAN_CYCLE': {
                'class': 'NP-complete',
                'explanation': 'Hamiltonian cycle is NP-complete'
            },
            'VERTEX_COVER': {
                'class': 'NP-complete',
                'explanation': 'Vertex cover decision problem is NP-complete'
            },
            'TSP': {
                'class': 'NP-complete',
                'explanation': 'Traveling salesman decision problem is NP-complete'
            },
            'SUBSET_SUM': {
                'class': 'NP-complete',
                'explanation': 'Subset sum is NP-complete'
            },
            'HALTING': {
                'class': 'Undecidable',
                'explanation': 'Halting problem is undecidable (not even in R)'
            },
            'TQBF': {
                'class': 'PSPACE-complete',
                'explanation': 'True quantified Boolean formulas is PSPACE-complete'
            }
        }

        if problem in classifications:
            info = classifications[problem]
            return {
                'problem': problem,
                'complexity_class': info['class'],
                'explanation': info['explanation']
            }
        else:
            return {
                'problem': problem,
                'complexity_class': 'unknown',
                'explanation': f'Complexity class unknown for {problem}'
            }

    def assess_tractability(self, problem: str) -> Dict[str, Any]:
        """
        Assess whether a problem is tractable

        Args:
            problem: Problem name

        Returns:
            Dict containing:
                - problem: Problem name
                - tractable: Boolean assessment
                - explanation: Tractability analysis
        """
        # Classify problem first
        classification = self.classify_complexity_class(problem)
        complexity_class = classification.get('complexity_class', 'unknown')

        # Assess tractability
        if complexity_class == 'P':
            tractable = True
            explanation = 'Problem is in P, hence tractable (polynomial-time solvable)'
        elif complexity_class == 'NP-complete':
            tractable = False
            explanation = 'Problem is NP-complete. No known polynomial-time algorithm (unless P=NP)'
        elif complexity_class == 'PSPACE-complete':
            tractable = False
            explanation = 'Problem is PSPACE-complete. Requires exponential time in worst case'
        elif complexity_class == 'Undecidable':
            tractable = False
            explanation = 'Problem is undecidable. No algorithm can solve all instances'
        else:
            tractable = None
            explanation = f'Tractability unknown for complexity class {complexity_class}'

        return {
            'problem': problem,
            'tractable': tractable,
            'complexity_class': complexity_class,
            'explanation': explanation,
            'note': 'Tractability typically means polynomial-time solvable'
        }

    def compute_hierarchy_relations(self) -> Dict[str, Any]:
        """
        Compute complexity hierarchy relationships

        Returns:
            Dict containing:
                - hierarchy: Known inclusions
                - separations: Known separations
                - open_problems: Major open questions
        """
        return {
            'hierarchy': {
                'known_inclusions': [
                    'P ⊆ NP',
                    'NP ⊆ PSPACE',
                    'PSPACE ⊆ EXPTIME',
                    'EXPTIME ⊆ R (recursive)',
                    'L ⊆ NL (logspace ⊆ nondeterministic logspace)',
                    'NL ⊆ P',
                    'coNP ⊆ PSPACE'
                ],
                'known_separations': [
                    'P ⊊ EXPTIME (time hierarchy theorem)',
                    'PSPACE ⊊ EXPSPACE (space hierarchy theorem)',
                    'L ⊊ PSPACE (space hierarchy)'
                ]
            },
            'open_problems': [
                'P vs NP (Millennium Prize Problem)',
                'NP vs coNP',
                'P vs PSPACE',
                'NP vs PSPACE',
                'L vs P',
                'NL vs P'
            ],
            'implications': {
                'if_P_equals_NP': [
                    'P = NP = coNP',
                    'All NP-complete problems tractable',
                    'Cryptography would collapse',
                    'Polynomial hierarchy collapses to P'
                ],
                'if_P_not_equal_NP': [
                    'NP-complete problems remain intractable',
                    'Public-key cryptography remains secure',
                    'Does not resolve NP vs coNP'
                ]
            },
            'note': 'P vs NP is the most important open problem in computer science'
        }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new complexity theory problems on blackboard
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []

        # Optimize cache if too many entries
        if self.tasks_executed > 100 and len(self.complexity_cache) > 50:
            intentions.append(Intention(
                action='optimize_cache',
                priority=1,
                description='Clear old complexity cache entries'
            ))

        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'optimize_cache':
            # Keep only recent cache entries
            if len(self.complexity_cache) > 50:
                keys = list(self.complexity_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.complexity_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.complexity_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
