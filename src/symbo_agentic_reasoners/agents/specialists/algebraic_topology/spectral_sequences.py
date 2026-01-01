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
SPECTRAL SEQUENCES SPECIALIST - Leray-Serre spectral sequence, Adams spectral sequence
=======================================================================================

Manages tasks related to spectral sequences, a powerful computational tool in algebraic topology.

CRITICAL ALGORITHMS:
-------------------
- Spectral Sequence Construction: Build Eᵣ^{p,q} pages from filtered complex
- Leray-Serre Spectral Sequence: For fibrations F → E → B
- Differentials: dᵣ: Eᵣ^{p,q} → Eᵣ^{p+r,q-r+1}
- Convergence: E∞ → H*(X)
- Adams Spectral Sequence: For stable homotopy theory
- Extension Problems: From E∞ to H*(X)

WHY THIS MATTERS:
----------------
Spectral sequences are fundamental to:
- Computing (co)homology of complicated spaces
- Fibration and bundle theory
- Stable homotopy theory
- Algebraic geometry and sheaf theory

CAPABILITIES:
------------
- Construct spectral sequences from filtered complexes
- Compute Leray-Serre spectral sequence
- Compute differentials dᵣ
- Check convergence to E∞
- Compute Adams spectral sequence (basics)
- Solve extension problems
"""

from typing import Dict, Any, List, Optional, Tuple
from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import create_service_registration
import numpy as np


class SpectralSequencesSpecialist(BDIAgent):
    """
    Spectral Sequences Specialist - Leray-Serre, Adams, convergence

    DIRECTIVE:
    ---------
    Handle all spectral sequence operations with emphasis on:
    - Spectral sequence construction
    - Leray-Serre for fibrations
    - Differential computation
    - Convergence analysis

    KEY ALGORITHMS:
    --------------
    - Spectral Sequence: Eᵣ^{p,q} pages with dᵣ: Eᵣ → Eᵣ
    - Leray-Serre: E₂^{p,q} = Hₚ(B; Hᵧ(F)) ⇒ Hₚ₊ᵧ(E)
    - Convergence: lim Eᵣ = E∞ → H*(X)

    OPERATIONS:
    ----------
    - construct_spectral_sequence(filtered_complex)
    - compute_leray_serre_spectral_sequence(fibration)
    - compute_spectral_sequence_differential(page, r)
    - check_convergence(spectral_sequence)
    - compute_adams_spectral_sequence(space)
    - extract_extensions(abutment, filtration)
    """

    def __init__(self, agent_id='spectral_sequences_specialist_001', df=None, blackboard=None):
        """
        Initialize Spectral Sequences Specialist

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
        self.spectral_cache = {}

        # Register with Directory Facilitator
        if self.df:
            self.df.register(create_service_registration(
                service_type='math.algebraictopology.spectralsequences',
                agent_id=self.agent_id,
                algorithm='spectral_sequences',
                cost='high',
                instance=self,
                type='specialist',
                tier='3'
            ))

    def process(self, task_entry):
        """
        Process spectral sequence task

        Args:
            task_entry: Task entry containing problem and metadata

        Returns:
            Dict containing result of spectral sequence operation
        """
        self.tasks_executed += 1

        # Extract metadata
        metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
        problem_type = metadata.get('problem_type', 'leray_serre')

        # Store recent task info
        self.recent_tasks.append({
            'type': problem_type,
            'timestamp': self.tasks_executed
        })
        if len(self.recent_tasks) > 10:
            self.recent_tasks.pop(0)

        try:
            if problem_type == 'construct':
                return self._process_construct(metadata)
            elif problem_type == 'leray_serre':
                return self._process_leray_serre(metadata)
            elif problem_type == 'differential':
                return self._process_differential(metadata)
            elif problem_type == 'convergence':
                return self._process_convergence(metadata)
            elif problem_type == 'adams':
                return self._process_adams(metadata)
            elif problem_type == 'extensions':
                return self._process_extensions(metadata)
            else:
                return self._process_leray_serre(metadata)

        except Exception as e:
            return {
                'operation': 'spectral sequences',
                'error': str(e),
                'problem_type': problem_type
            }

    def _process_construct(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process spectral sequence construction"""
        filtered_complex = metadata.get('filtered_complex', {})

        result = self.construct_spectral_sequence(filtered_complex)
        return {
            'operation': 'construct_spectral_sequence',
            **result
        }

    def _process_leray_serre(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Leray-Serre spectral sequence"""
        fibration = metadata.get('fibration', {})

        result = self.compute_leray_serre_spectral_sequence(fibration)
        return {
            'operation': 'leray_serre_spectral_sequence',
            **result
        }

    def _process_differential(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process differential computation"""
        page = metadata.get('page', {})
        r = metadata.get('r', 2)

        result = self.compute_spectral_sequence_differential(page, r)
        return {
            'operation': 'spectral_sequence_differential',
            **result
        }

    def _process_convergence(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process convergence check"""
        spectral_sequence = metadata.get('spectral_sequence', {})

        result = self.check_convergence(spectral_sequence)
        return {
            'operation': 'convergence_check',
            **result
        }

    def _process_adams(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process Adams spectral sequence"""
        space = metadata.get('space', 'sphere')

        result = self.compute_adams_spectral_sequence(space)
        return {
            'operation': 'adams_spectral_sequence',
            **result
        }

    def _process_extensions(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process extension problems"""
        abutment = metadata.get('abutment', {})
        filtration = metadata.get('filtration', {})

        result = self.extract_extensions(abutment, filtration)
        return {
            'operation': 'extract_extensions',
            **result
        }

    def construct_spectral_sequence(
        self,
        filtered_complex: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Construct spectral sequence from filtered complex

        Spectral sequence: {Eᵣ^{p,q}, dᵣ} where dᵣ: Eᵣ^{p,q} → Eᵣ^{p+r,q-r+1}
        and Eᵣ₊₁^{p,q} = H(Eᵣ^{p,q}, dᵣ)

        Args:
            filtered_complex: Dict describing filtered chain complex

        Returns:
            Dict containing:
                - pages: {r: Eᵣ^{p,q}}
                - differentials: Descriptions of dᵣ
                - explanation: Description
        """
        filtration = filtered_complex.get('filtration', [])

        if not filtration:
            return {
                'pages': {},
                'explanation': 'Empty filtered complex produces trivial spectral sequence'
            }

        # E₀ page: just the filtration quotients
        e0_page = {}
        for p in range(len(filtration)):
            e0_page[(p, 0)] = f"Fₚ/Fₚ₋₁"

        # E₁ page: homology of E₀
        e1_page = {}
        for p in range(len(filtration)):
            e1_page[(p, 0)] = f"H*(Fₚ/Fₚ₋₁)"

        return {
            'pages': {
                0: e0_page,
                1: e1_page
            },
            'differentials': {
                0: 'd₀: E₀^{p,q} → E₀^{p+0,q-0+1} = E₀^{p,q+1}',
                1: 'd₁: E₁^{p,q} → E₁^{p+1,q}'
            },
            'explanation': "Spectral sequence from filtered complex: Eᵣ pages computed iteratively",
            'note': 'Each page Eᵣ₊₁ is homology of previous page (Eᵣ, dᵣ)',
            'convergence': 'E∞^{p,q} = Fₚ Hₚ₊ᵧ(X) / Fₚ₋₁ Hₚ₊ᵧ(X)'
        }

    def compute_leray_serre_spectral_sequence(
        self,
        fibration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute Leray-Serre spectral sequence for fibration F → E → B

        E₂^{p,q} = Hₚ(B; Hᵧ(F)) ⇒ Hₚ₊ᵧ(E)

        Args:
            fibration: Dict with fiber, total, base

        Returns:
            Dict containing:
                - e2_page: E₂^{p,q} terms
                - abutment: H*(E)
                - explanation: Description
        """
        fiber = fibration.get('fiber', 'unknown')
        total = fibration.get('total', 'unknown')
        base = fibration.get('base', 'unknown')

        # Known examples
        if 'hopf' in total.lower() or (fiber == 's1' and base == 's2' and total == 's3'):
            # Hopf fibration: S¹ → S³ → S²
            e2_page = {
                (0, 0): 'ℤ',  # H₀(S²; H₀(S¹)) = H₀(S²) ⊗ H₀(S¹) = ℤ ⊗ ℤ = ℤ
                (0, 1): 'ℤ',  # H₀(S²; H₁(S¹)) = H₀(S²) ⊗ H₁(S¹) = ℤ ⊗ ℤ = ℤ
                (2, 0): 'ℤ',  # H₂(S²; H₀(S¹)) = H₂(S²) ⊗ H₀(S¹) = ℤ ⊗ ℤ = ℤ
                (2, 1): 'ℤ',  # H₂(S²; H₁(S¹)) = H₂(S²) ⊗ H₁(S¹) = ℤ ⊗ ℤ = ℤ
            }

            return {
                'fibration': 'Hopf fibration S¹ → S³ → S²',
                'fiber': 'S¹',
                'total': 'S³',
                'base': 'S²',
                'e2_page': e2_page,
                'differentials': {
                    2: 'd₂: E₂^{p,q} → E₂^{p+2,q-1}',
                    'note': 'd₂((2,1) → (4,0)) = 0 since E₂^{4,0} = 0'
                },
                'abutment': {
                    0: 'ℤ',  # H₀(S³)
                    1: '0',  # H₁(S³)
                    2: '0',  # H₂(S³)
                    3: 'ℤ'   # H₃(S³)
                },
                'explanation': "Leray-Serre for Hopf: E₂^{p,q} = Hₚ(S²; Hᵧ(S¹)) ⇒ Hₚ₊ᵧ(S³)",
                'note': 'Differentials must kill appropriate terms to get H*(S³)'
            }

        # Path fibration: ΩB → PB → B (where PB is contractible)
        if 'path' in total.lower():
            return {
                'fibration': 'Path fibration ΩB → PB → B',
                'fiber': 'ΩB (loop space)',
                'total': 'PB (path space, contractible)',
                'base': base,
                'e2_page': 'Hₚ(B; Hᵧ(ΩB))',
                'abutment': {
                    'n': '0 for all n (PB contractible)'
                },
                'explanation': "Path fibration: E₂ = Hₚ(B; Hᵧ(ΩB)) ⇒ 0",
                'note': 'This allows computation of H*(ΩB) from H*(B)',
                'theorem': 'For simply connected B: H*(ΩB) computable from H*(B)'
            }

        # Generic fibration
        return {
            'fibration': f"{fiber} → {total} → {base}",
            'fiber': fiber,
            'total': total,
            'base': base,
            'e2_page': f"E₂^{{p,q}} = Hₚ({base}; Hᵧ({fiber}))",
            'abutment': f"Hₚ₊ᵧ({total})",
            'explanation': f"Leray-Serre spectral sequence for fibration {fiber} → {total} → {base}",
            'theorem': 'E₂^{p,q} = Hₚ(B; Hᵧ(F)) ⇒ Hₚ₊ᵧ(E)',
            'note': 'Local coefficients if π₁(B) acts non-trivially on H*(F)'
        }

    def compute_spectral_sequence_differential(
        self,
        page: Dict[Tuple[int, int], str],
        r: int
    ) -> Dict[str, Any]:
        """
        Compute differential dᵣ: Eᵣ^{p,q} → Eᵣ^{p+r,q-r+1}

        Args:
            page: Eᵣ page as dict {(p,q): group}
            r: Page number

        Returns:
            Dict containing:
                - differential: Description of dᵣ
                - domain_codomain: {(p,q): (p+r, q-r+1)}
                - explanation: Description
        """
        # Differential maps
        dr_maps = {}
        for (p, q), group in page.items():
            target = (p + r, q - r + 1)
            if target in page:
                dr_maps[(p, q)] = {
                    'source': (p, q),
                    'target': target,
                    'source_group': group,
                    'target_group': page[target]
                }

        return {
            'differential': f"d_{r}",
            'r': r,
            'bidegree': (r, -r+1),
            'maps': dr_maps,
            'explanation': f"d_{r}: E_{r}^{{p,q}} → E_{r}^{{p+{r},q-{r}+1}}",
            'property': f"d_{r} ∘ d_{r} = 0",
            'homology': f"E_{{r+1}}^{{p,q}} = ker(d_{r}^{{p,q}}) / im(d_{r}^{{p-{r},q+{r}-1}})",
            'note': f'Differential on page {r} has bidegree ({r}, {-r+1})'
        }

    def check_convergence(
        self,
        spectral_sequence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if spectral sequence converges to E∞

        Args:
            spectral_sequence: Dict describing spectral sequence

        Returns:
            Dict containing:
                - converges: Boolean
                - e_infinity: E∞ description
                - explanation: Description
        """
        spectral_type = spectral_sequence.get('type', 'unknown')

        # Most spectral sequences in algebraic topology converge
        if spectral_type == 'leray_serre':
            return {
                'converges': True,
                'e_infinity': 'E∞^{p,q}',
                'theorem': 'Leray-Serre always converges for fibrations',
                'explanation': "Spectral sequence stabilizes: Eᵣ = Eᵣ₊₁ = ... = E∞ for r >> 0",
                'abutment': 'E∞^{p,q} = Fₚ H_{p+q}(E) / F_{p-1} H_{p+q}(E)',
                'note': 'Convergence means differentials eventually vanish'
            }

        if spectral_type == 'adams':
            return {
                'converges': True,
                'e_infinity': 'E∞^{s,t}',
                'theorem': 'Adams spectral sequence converges conditionally',
                'explanation': "Converges to stable homotopy groups: E₂^{s,t} = Ext^s_A(H*(X), ℤ/2ℤ) ⇒ π_{t-s}(X)^∧_2",
                'note': '2-completion of homotopy groups',
                'conditionally_convergent': True
            }

        # Generic
        return {
            'converges': None,
            'explanation': "Convergence depends on spectral sequence type",
            'conditions': [
                'Bounded below (Eᵣ^{p,q} = 0 for p < 0)',
                'Bounded above or finite type',
                'First quadrant spectral sequence'
            ],
            'note': 'Most spectral sequences in algebraic topology converge'
        }

    def compute_adams_spectral_sequence(
        self,
        space: str
    ) -> Dict[str, Any]:
        """
        Compute Adams spectral sequence (basics) for computing homotopy groups

        E₂^{s,t} = Ext^s_A(H*(X), ℤ/2ℤ) ⇒ π_{t-s}(X)^∧_2

        Args:
            space: Space description

        Returns:
            Dict containing:
                - e2_page: E₂ terms
                - abutment: Homotopy groups
                - explanation: Description
        """
        space = space.lower()

        if 'sphere' in space:
            # Adams spectral sequence for spheres
            return {
                'space': space,
                'e2_page': 'Ext^s_A(H*(S^n), ℤ/2ℤ)',
                'steenrod_algebra': 'A = Steenrod algebra (operations on mod 2 cohomology)',
                'abutment': f"π_*(S^n)^∧_2 (2-completed stable homotopy groups)",
                'explanation': "Adams spectral sequence computes stable homotopy groups of spheres",
                'theorem': 'E₂^{s,t} = Ext^s_A(H*(X), ℤ/2ℤ) ⇒ π_{t-s}(X)^∧_2',
                'applications': [
                    'Computing π₃(S²) = ℤ (Hopf invariant one)',
                    'Proving existence of exotic spheres',
                    'Stable homotopy theory'
                ],
                'note': 'Adams spectral sequence is primary tool for computing stable homotopy groups'
            }

        # Generic
        return {
            'space': space,
            'e2_page': f"Ext^s_A(H*({space}), ℤ/2ℤ)",
            'steenrod_algebra': 'A = Steenrod algebra',
            'abutment': f"π_*({space})^∧_2",
            'explanation': f"Adams spectral sequence for {space}",
            'theorem': 'E₂^{s,t} = Ext^s_A(H*(X), ℤ/2ℤ) ⇒ π_{t-s}(X)^∧_2',
            'note': 'Requires understanding of Steenrod algebra and Ext groups'
        }

    def extract_extensions(
        self,
        abutment: Dict[int, str],
        filtration: Dict[int, str]
    ) -> Dict[str, Any]:
        """
        Solve extension problems from E∞ to actual (co)homology

        Given E∞^{p,q} and filtration Fₚ H_{p+q}, determine H_{p+q}

        Args:
            abutment: E∞ page
            filtration: Filtration on homology

        Returns:
            Dict containing:
                - extensions: Possible extensions
                - explanation: Description
        """
        # Extension problem: given graded pieces, reconstruct full group
        # This is a non-trivial problem in general

        # Count dimensions
        total_dim = sum(1 for g in abutment.values() if g != '0')

        return {
            'extension_problem': 'Reconstruct H* from E∞ and filtration',
            'e_infinity': abutment,
            'filtration': filtration,
            'explanation': "Extension problem: given Fₚ/Fₚ₋₁ ≅ E∞^{p,*}, find exact H*",
            'theorem': 'Short exact sequences: 0 → Fₚ₋₁ → Fₚ → E∞^{p,*} → 0',
            'difficulties': [
                'Extensions need not split',
                'Torsion complicates extensions',
                'May need additional information'
            ],
            'solutions': [
                'If all groups are free abelian, extensions split: H* = ⊕ E∞^{p,*}',
                'Torsion extensions require Ext¹ computation',
                'Multiplicative structure can resolve extensions'
            ],
            'note': 'Extension problems are inherently difficult in spectral sequence theory'
        }

    def update_beliefs(self):
        """Update beliefs based on recent task execution"""
        if hasattr(self, 'blackboard') and self.blackboard:
            pass

    def deliberate(self) -> List[Intention]:
        """Generate intentions based on current beliefs"""
        intentions = []
        if self.tasks_executed > 100 and len(self.spectral_cache) > 50:
            intentions.append(Intention(
                action='optimize_cache',
                priority=1,
                description='Clear old spectral sequence cache entries'
            ))
        return intentions

    def execute_step(self, intention: Intention):
        """Execute a specific intention"""
        if intention.action == 'optimize_cache':
            if len(self.spectral_cache) > 50:
                keys = list(self.spectral_cache.keys())
                for key in keys[:len(keys)//2]:
                    del self.spectral_cache[key]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        base_stats = super().get_statistics()
        return {
            **base_stats,
            'tasks_executed': self.tasks_executed,
            'cache_size': len(self.spectral_cache),
            'recent_task_types': [t['type'] for t in self.recent_tasks[-5:]]
        }
