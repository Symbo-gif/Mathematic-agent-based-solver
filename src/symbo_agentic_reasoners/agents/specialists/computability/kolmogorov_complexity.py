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
KOLMOGOROV COMPLEXITY SPECIALIST - Descriptive complexity, algorithmic information
==================================================================================

Manages tasks related to Kolmogorov complexity, algorithmic information theory, and incompressibility.

CRITICAL ALGORITHMS:
-------------------
- Kolmogorov Complexity Estimation: Estimate K(x) via compression
- Compression Ratio Analysis: Upper bound on descriptive complexity
- Incompressibility Testing: Determine if string is incompressible
- Algorithmic Probability: Compute algorithmic probability estimates

WHY THIS MATTERS:
----------------
Kolmogorov complexity is fundamental to:
- Defining randomness and information content
- Understanding compression limits
- Foundations of algorithmic information theory
- Connections to probability and logic

CAPABILITIES:
------------
- Estimate Kolmogorov complexity K(x)
- Compute compression ratios as upper bounds
- Verify incompressibility conditions
- Calculate algorithmic probability
- Analyze mutual information K(x:y)
- Apply algorithmic suffix and prefix complexity
"""

from typing import Dict, Any, List, Optional, Tuple
import zlib
import math
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration


class KolmogorovComplexitySpecialist(BDIAgent):
    """
    Kolmogorov Complexity Specialist - Descriptive complexity

    DIRECTIVE:
    ---------
    Handle all Kolmogorov complexity operations with emphasis on:
    - Complexity estimation via compression
    - Incompressibility analysis
    - Algorithmic information theory
    - Randomness quantification

    KEY ALGORITHMS:
    --------------
    - Compression-based Estimation: K(x) ≈ |compressed(x)|
    - Incompressibility Test: K(x) ≥ |x| - c for random strings
    - Algorithmic Probability: m(x) = Σ 2^(-|p|) over programs p producing x

    OPERATIONS:
    ----------
    - estimate_kolmogorov_complexity(string)
    - compression_ratio(string)
    - verify_incompressibility(string)
    - compute_algorithmic_probability(string)
    - compute_mutual_information(string_x, string_y)
    - analyze_randomness(string)
    """

    def __init__(self, agent_id='kolmogorov_complexity_specialist_001', df=None, blackboard=None):
        """
        Initialize Kolmogorov Complexity Specialist

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
                service_type='math.computability.kolmogorov_complexity',
                agent_id=self.agent_id,
                algorithm='kolmogorov_complexity',
                cost='medium',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process Kolmogorov complexity task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of Kolmogorov complexity operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'estimate')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'estimate':
                return self._process_estimate_complexity(metadata)
            elif problem_type == 'compression':
                return self._process_compression_ratio(metadata)
            elif problem_type == 'incompressibility':
                return self._process_incompressibility(metadata)
            elif problem_type == 'algorithmic_probability':
                return self._process_algorithmic_probability(metadata)
            elif problem_type == 'mutual_information':
                return self._process_mutual_information(metadata)
            elif problem_type == 'randomness':
                return self._process_randomness(metadata)
            else:
                return self._process_estimate_complexity(metadata)

        except Exception as e:
            return {
                'operation': 'kolmogorov_complexity',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_estimate_complexity(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process complexity estimation request"""
        string = metadata.get('string', '01010101')

        result = self.estimate_kolmogorov_complexity(string)
        return {
            'operation': 'estimate_kolmogorov_complexity',
            **result
        }

    def _process_compression_ratio(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process compression ratio computation request"""
        string = metadata.get('string', '01010101')

        result = self.compression_ratio(string)
        return {
            'operation': 'compression_ratio',
            **result
        }

    def _process_incompressibility(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process incompressibility verification request"""
        string = metadata.get('string', '11010011')

        result = self.verify_incompressibility(string)
        return {
            'operation': 'verify_incompressibility',
            **result
        }

    def _process_algorithmic_probability(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process algorithmic probability computation request"""
        string = metadata.get('string', '0')

        result = self.compute_algorithmic_probability(string)
        return {
            'operation': 'compute_algorithmic_probability',
            **result
        }

    def _process_mutual_information(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process mutual information computation request"""
        string_x = metadata.get('string_x', '0110')
        string_y = metadata.get('string_y', '1001')

        result = self.compute_mutual_information(string_x, string_y)
        return {
            'operation': 'compute_mutual_information',
            **result
        }

    def _process_randomness(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process randomness analysis request"""
        string = metadata.get('string', '11010011')

        result = self.analyze_randomness(string)
        return {
            'operation': 'analyze_randomness',
            **result
        }

    def estimate_kolmogorov_complexity(self, string: str) -> Dict[str, Any]:
        """
        Estimate Kolmogorov complexity K(x)

        Note: K(x) is uncomputable. We use compression as an upper bound approximation.

        Args:
            string: Input string

        Returns:
            Dict containing:
                - string: Input string
                - estimated_complexity: Estimated K(x)
                - original_length: |x|
                - method: Estimation method
                - explanation: Analysis
        """
        if not string:
            return {
                'string': '',
                'estimated_complexity': 0,
                'original_length': 0,
                'explanation': 'Empty string has K(x) ≈ O(1) (constant)'
            }

        # Convert to bytes if string
        if isinstance(string, str):
            byte_string = string.encode('utf-8')
        else:
            byte_string = string

        # Use zlib compression as approximation
        compressed = zlib.compress(byte_string)
        compressed_length = len(compressed)

        original_length = len(byte_string)

        # Estimate K(x) as compressed length (upper bound)
        estimated_k = compressed_length

        return {
            'string': string[:100] + ('...' if len(string) > 100 else ''),
            'estimated_complexity': estimated_k,
            'original_length': original_length,
            'compressed_length': compressed_length,
            'method': 'zlib compression (upper bound)',
            'explanation': f'K(x) ≤ {estimated_k} bits (compression-based upper bound)',
            'note': 'Kolmogorov complexity is uncomputable in general',
            'properties': [
                'K(x) ≤ |x| + O(1) (any string has simple "print x" program)',
                f'K(x) ≈ {estimated_k} (compression estimate)',
                'True K(x) may be lower but cannot be computed'
            ]
        }

    def compression_ratio(self, string: str) -> Dict[str, Any]:
        """
        Compute compression ratio as upper bound on K(x)

        Args:
            string: Input string

        Returns:
            Dict containing:
                - ratio: Compression ratio
                - original_size: Original size
                - compressed_size: Compressed size
                - explanation: Analysis
        """
        if not string:
            return {
                'ratio': 1.0,
                'original_size': 0,
                'compressed_size': 0,
                'explanation': 'Empty string'
            }

        # Convert to bytes
        if isinstance(string, str):
            byte_string = string.encode('utf-8')
        else:
            byte_string = string

        # Compress
        compressed = zlib.compress(byte_string)

        original_size = len(byte_string)
        compressed_size = len(compressed)
        ratio = compressed_size / original_size if original_size > 0 else 1.0

        # Interpret ratio
        if ratio < 0.5:
            interpretation = 'Highly compressible (low Kolmogorov complexity)'
        elif ratio < 0.8:
            interpretation = 'Moderately compressible (medium complexity)'
        elif ratio < 1.0:
            interpretation = 'Slightly compressible (approaching random)'
        else:
            interpretation = 'Incompressible (near-random, high Kolmogorov complexity)'

        return {
            'ratio': ratio,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'interpretation': interpretation,
            'explanation': f'Compression ratio {ratio:.2%} indicates {interpretation.lower()}',
            'note': 'Lower ratio → lower complexity, Higher ratio → higher complexity'
        }

    def verify_incompressibility(self, string: str) -> Dict[str, Any]:
        """
        Verify if string is incompressible

        A string x is c-incompressible if K(x) ≥ |x| - c.
        Most strings of length n are incompressible (random).

        Args:
            string: Input string

        Returns:
            Dict containing:
                - incompressible: Boolean assessment
                - string: Input string
                - compression_ratio: Ratio
                - explanation: Analysis
        """
        # Compute compression ratio
        ratio_result = self.compression_ratio(string)
        ratio = ratio_result['ratio']

        # Threshold for incompressibility (ratio close to 1)
        threshold = 0.9

        incompressible = ratio >= threshold

        return {
            'incompressible': incompressible,
            'string': string[:100] + ('...' if len(string) > 100 else ''),
            'compression_ratio': ratio,
            'threshold': threshold,
            'explanation': f"String is {'incompressible' if incompressible else 'compressible'} (ratio {ratio:.2%} {'≥' if incompressible else '<'} {threshold:.0%})",
            'interpretation': 'Incompressible strings are algorithmically random',
            'note': 'Most strings are incompressible (Kolmogorov incompressibility theorem)'
        }

    def compute_algorithmic_probability(self, string: str) -> Dict[str, Any]:
        """
        Compute estimate of algorithmic probability m(x)

        Algorithmic probability: m(x) = Σ 2^(-|p|) over all programs p that output x
        Related to K(x) by: -log₂ m(x) ≈ K(x) (coding theorem)

        Args:
            string: Input string

        Returns:
            Dict containing:
                - string: Input string
                - algorithmic_probability: Estimated m(x)
                - log_probability: -log₂ m(x) ≈ K(x)
                - explanation: Analysis
        """
        # Estimate K(x)
        k_result = self.estimate_kolmogorov_complexity(string)
        estimated_k = k_result['estimated_complexity']

        # Algorithmic probability: m(x) ≈ 2^(-K(x))
        log_prob = -estimated_k  # log₂ m(x)
        m_x = 2.0 ** log_prob

        return {
            'string': string[:100] + ('...' if len(string) > 100 else ''),
            'algorithmic_probability': m_x,
            'log_probability': log_prob,
            'estimated_k': estimated_k,
            'explanation': f'm(x) ≈ 2^(-K(x)) = 2^({log_prob}) ≈ {m_x:.2e}',
            'coding_theorem': 'Coding theorem: -log₂ m(x) = K(x) + O(1)',
            'note': 'Lower K(x) → higher m(x) (simpler strings are more probable)'
        }

    def compute_mutual_information(
        self,
        string_x: str,
        string_y: str
    ) -> Dict[str, Any]:
        """
        Compute algorithmic mutual information K(x:y)

        K(x:y) = K(x) + K(y) - K(x,y)
        Measures information shared between x and y.

        Args:
            string_x, string_y: Input strings

        Returns:
            Dict containing:
                - mutual_information: K(x:y)
                - k_x, k_y: Individual complexities
                - k_xy: Joint complexity
                - explanation: Analysis
        """
        # Estimate individual complexities
        k_x = self.estimate_kolmogorov_complexity(string_x)['estimated_complexity']
        k_y = self.estimate_kolmogorov_complexity(string_y)['estimated_complexity']

        # Estimate joint complexity K(x,y)
        # Simple concatenation (could use more sophisticated pairing)
        joint = string_x + '|' + string_y
        k_xy = self.estimate_kolmogorov_complexity(joint)['estimated_complexity']

        # Mutual information
        mutual_info = k_x + k_y - k_xy

        # Interpret mutual information
        if mutual_info <= 0:
            interpretation = 'Independent (no shared information)'
        elif mutual_info < min(k_x, k_y) * 0.3:
            interpretation = 'Low correlation'
        elif mutual_info < min(k_x, k_y) * 0.7:
            interpretation = 'Moderate correlation'
        else:
            interpretation = 'High correlation (significant shared information)'

        return {
            'mutual_information': mutual_info,
            'k_x': k_x,
            'k_y': k_y,
            'k_xy': k_xy,
            'interpretation': interpretation,
            'explanation': f'K(x:y) = K(x) + K(y) - K(x,y) = {k_x} + {k_y} - {k_xy} = {mutual_info}',
            'properties': [
                'K(x:y) ≥ 0 (non-negative)',
                'K(x:y) = K(y:x) (symmetric)',
                'K(x:y) ≤ min(K(x), K(y)) (bounded by marginals)'
            ]
        }

    def analyze_randomness(self, string: str) -> Dict[str, Any]:
        """
        Analyze algorithmic randomness of a string

        A string is algorithmically random if K(x) ≥ |x| - c for small c.

        Args:
            string: Input string

        Returns:
            Dict containing:
                - random: Randomness assessment
                - k_estimate: Estimated K(x)
                - string_length: |x|
                - randomness_score: K(x) / |x|
                - explanation: Analysis
        """
        # Estimate K(x)
        k_result = self.estimate_kolmogorov_complexity(string)
        k_estimate = k_result['estimated_complexity']
        string_length = len(string.encode('utf-8') if isinstance(string, str) else string)

        # Randomness score: K(x) / |x|
        randomness_score = k_estimate / string_length if string_length > 0 else 0

        # Threshold for randomness (high ratio indicates randomness)
        threshold = 0.8

        is_random = randomness_score >= threshold

        # Classify randomness
        if randomness_score < 0.3:
            classification = 'Highly structured (low randomness)'
        elif randomness_score < 0.6:
            classification = 'Partially random'
        elif randomness_score < 0.9:
            classification = 'Algorithmically random'
        else:
            classification = 'Perfectly random (incompressible)'

        return {
            'random': is_random,
            'string': string[:100] + ('...' if len(string) > 100 else ''),
            'k_estimate': k_estimate,
            'string_length': string_length,
            'randomness_score': randomness_score,
            'classification': classification,
            'explanation': f'Randomness score K(x)/|x| = {randomness_score:.2%}. {classification}.',
            'note': 'Random strings satisfy K(x) ≥ |x| - c (incompressibility theorem)',
            'martin_lof_randomness': 'String passes algorithmic randomness test if K(x) ≈ |x|'
        }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            # Check for new Kolmogorov complexity problems on blackboard
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
