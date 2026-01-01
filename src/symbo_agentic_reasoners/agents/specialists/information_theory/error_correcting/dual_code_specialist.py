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
DUAL CODE SPECIALIST (Tier 3)
==============================

Handles dual code construction and MacWilliams identity.

CAPABILITIES:
------------
- construct_dual: Build dual code C⊥ from generator/parity matrix
- verify_self_dual: Check if code equals its dual (C = C⊥)
- macwilliams_transform: Transform weight enumerator W_C → W_{C⊥}
- is_doubly_even: Check if all codeword weights ≡ 0 (mod 4)
- is_even: Check if all codeword weights are even

FORMULATION:
-----------
Dual Code Definition:
  C⊥ = {x ∈ GF(q)^n : x·c = 0 for all c ∈ C}

For [n,k] code C:
- dim(C⊥) = n - k
- (C⊥)⊥ = C

Generator/Parity Duality:
- G for C → H for C (parity check)
- H for C → G for C⊥ (generator of dual)
- If C has G = [I_k | P], then C⊥ has G = [-P^T | I_{n-k}]

MacWilliams Identity:
  W_{C⊥}(x,y) = |C|^{-1} W_C(x+y, x-y)

For binary codes:
  W_{C⊥}(x,y) = (1/|C|) Σ_{w=0}^n A_w (x+y)^{n-w} (x-y)^w

Self-Dual Properties:
- Self-dual: C = C⊥ (requires n = 2k)
- Self-orthogonal: C ⊆ C⊥
- Doubly-even: all weights ≡ 0 (mod 4)
- Singly-even: all weights even, some ≢ 0 (mod 4)

ALGORITHMIC BACKING:
-------------------
Native GF(q) linear algebra from core/coding_theory_native.py

NO SYMPY - Pure native mathematical reasoning.

REFERENCE:
---------
- MacWilliams & Sloane (1977), Chapter 5: Dual Codes
- Huffman & Pless (2003), Fundamentals of Error-Correcting Codes, Ch 1.5
"""

import logging
from typing import Any, Dict, List, Optional

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.coding_theory_native import (
    gf2_matrix_multiply, gf2_rref, gf2_rank, hamming_weight, binomial
)

logger = logging.getLogger(__name__)


class DualCodeSpecialist(BDIAgent):
    """
    Dual Code Specialist - Dual Code and MacWilliams Identity Operations

    DIRECTIVE:
    ---------
    Handle dual code construction and weight enumerator transformations.

    OPERATIONS:
    ----------
    - construct_dual: Build C⊥ from G or H
    - verify_self_dual: Check C = C⊥
    - macwilliams_transform: Transform weight enumerator
    - is_doubly_even: Check weight divisibility by 4
    - is_even: Check all weights even

    FORMULATION:
    -----------
    The dual C⊥ consists of all vectors orthogonal to every codeword.
    For systematic G = [I_k | P], dual has G_⊥ = [-P^T | I_{n-k}].

    REFERENCE:
    ---------
    - MacWilliams & Sloane (1977), Theory of Error-Correcting Codes
    """

    def __init__(
        self,
        agent_id: str = 'dual_code_specialist_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None
    ):
        """Initialize Dual Code Specialist."""
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard

        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.duals_constructed = 0
        self.self_dual_checks = 0
        self.macwilliams_transforms = 0
        self.doubly_even_checks = 0

        if self.df:
            self._register_services()

    def _register_services(self):
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            service_type='math.information_theory.error_correction.dual',
            agent_id=self.agent_id,
            algorithm='dual_code_construction',
            cost='medium',
            instance=self,
            type='specialist',
            tier='3',
            operations='dual_self_dual_macwilliams_even'
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered as dual code specialist")

    # ========================================
    # Core Operations
    # ========================================

    def construct_dual(
        self,
        G: Optional[List[List[int]]] = None,
        H: Optional[List[List[int]]] = None,
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Construct dual code C⊥ from generator or parity-check matrix.

        For [n,k] code C with G = [I_k | P]:
        - C⊥ is [n, n-k] code
        - G_⊥ = [-P^T | I_{n-k}] = [P^T | I_{n-k}] in GF(2)

        Args:
            G: Generator matrix of C (k×n)
            H: Parity-check matrix of C (r×n where r = n-k)
            q: Field size

        Returns:
            Dual code generator matrix
        """
        if G is None and H is None:
            return {'success': False, 'error': 'Must provide either G or H'}

        try:
            if H is not None:
                # H of C becomes G of C⊥
                G_dual = [row[:] for row in H]
                k_dual = len(H)
                n = len(H[0]) if H else 0

                self.duals_constructed += 1
                return {
                    'success': True,
                    'dual_generator': G_dual,
                    'n': n,
                    'k_dual': k_dual,
                    'k_original': n - k_dual,
                    'method': 'H_to_G_dual'
                }

            # Have G, need to construct H first, then H becomes G_dual
            if not G or not G[0]:
                return {'success': False, 'error': 'Generator matrix cannot be empty'}

            k = len(G)
            n = len(G[0])

            if q == 2:
                # Convert G to systematic form [I_k | P]
                G_sys, pivot_cols = gf2_rref(G)

                # Check if we got full rank
                rank = gf2_rank(G)
                if rank < k:
                    return {
                        'success': False,
                        'error': f'Generator matrix not full rank: rank={rank}, k={k}'
                    }

                # Need to rearrange columns to get systematic form
                # For simplicity, check if already systematic
                is_systematic = True
                for i in range(k):
                    for j in range(k):
                        expected = 1 if i == j else 0
                        if G_sys[i][j] != expected:
                            is_systematic = False
                            break
                    if not is_systematic:
                        break

                if is_systematic:
                    # Extract P from G = [I_k | P]
                    P = [row[k:] for row in G_sys]

                    # H = [P^T | I_{n-k}] (in GF(2), -P^T = P^T)
                    r = n - k
                    H = []
                    for i in range(r):
                        row = [0] * n
                        # P^T part
                        for j in range(k):
                            row[j] = P[j][i]
                        # Identity part
                        row[k + i] = 1
                        H.append(row)

                    # H is the generator for C⊥
                    G_dual = H
                else:
                    # Not systematic - use null space approach
                    # G_dual = null space of G^T
                    # For now, return with guidance
                    return {
                        'success': False,
                        'error': 'Non-systematic generator: convert to systematic form first'
                    }
            else:
                return {'success': False, 'error': f'Non-binary (q={q}) not yet supported'}

            self.duals_constructed += 1

            return {
                'success': True,
                'dual_generator': G_dual,
                'original_generator': G,
                'n': n,
                'k_original': k,
                'k_dual': n - k,
                'method': 'systematic_construction'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def verify_self_dual(
        self,
        G: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Check if code is self-dual (C = C⊥).

        A code is self-dual if and only if:
        1. n = 2k (dimension equals co-dimension)
        2. G · G^T = 0 (all codewords orthogonal)

        Args:
            G: Generator matrix (k×n)
            q: Field size

        Returns:
            Whether code is self-dual
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        try:
            k = len(G)
            n = len(G[0])

            # Condition 1: n = 2k
            if n != 2 * k:
                self.self_dual_checks += 1
                return {
                    'success': True,
                    'is_self_dual': False,
                    'reason': f'n={n} ≠ 2k=2*{k}: code cannot be self-dual',
                    'n': n,
                    'k': k,
                    'method': 'dimension_check'
                }

            # Condition 2: G · G^T = 0
            # For self-dual, every pair of rows must be orthogonal
            is_self_orthogonal = True
            non_orthogonal_pair = None

            for i in range(k):
                for j in range(i, k):
                    # Compute inner product g_i · g_j
                    if q == 2:
                        inner = 0
                        for t in range(n):
                            inner ^= G[i][t] & G[j][t]
                    else:
                        inner = 0
                        for t in range(n):
                            inner = (inner + G[i][t] * G[j][t]) % q

                    if inner != 0:
                        is_self_orthogonal = False
                        non_orthogonal_pair = (i, j)
                        break
                if not is_self_orthogonal:
                    break

            self.self_dual_checks += 1

            if is_self_orthogonal:
                return {
                    'success': True,
                    'is_self_dual': True,
                    'n': n,
                    'k': k,
                    'reason': 'Code satisfies G·G^T = 0 with n = 2k',
                    'method': 'orthogonality_check'
                }
            else:
                return {
                    'success': True,
                    'is_self_dual': False,
                    'n': n,
                    'k': k,
                    'reason': f'Rows {non_orthogonal_pair} not orthogonal',
                    'method': 'orthogonality_check'
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def is_self_orthogonal(
        self,
        G: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Check if code is self-orthogonal (C ⊆ C⊥).

        A code is self-orthogonal if G · G^T = 0.

        Args:
            G: Generator matrix
            q: Field size

        Returns:
            Whether code is self-orthogonal
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        try:
            k = len(G)
            n = len(G[0])

            # Check G · G^T = 0
            for i in range(k):
                for j in range(i, k):
                    if q == 2:
                        inner = 0
                        for t in range(n):
                            inner ^= G[i][t] & G[j][t]
                    else:
                        inner = 0
                        for t in range(n):
                            inner = (inner + G[i][t] * G[j][t]) % q

                    if inner != 0:
                        return {
                            'success': True,
                            'is_self_orthogonal': False,
                            'reason': f'Rows {i} and {j} not orthogonal',
                            'n': n,
                            'k': k,
                            'method': 'inner_product_check'
                        }

            return {
                'success': True,
                'is_self_orthogonal': True,
                'n': n,
                'k': k,
                'reason': 'All row pairs orthogonal: C ⊆ C⊥',
                'method': 'inner_product_check'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def macwilliams_transform(
        self,
        weight_enum: Dict[int, int],
        n: int,
        k: int,
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Apply MacWilliams identity to transform weight enumerator.

        W_{C⊥}(x,y) = |C|^{-1} W_C(x+y, x-y)

        For binary codes, the transform is:
        B_j = (1/2^k) Σ_{i=0}^n A_i K_j(i)

        where K_j(i) = Σ_{s=0}^j (-1)^s C(i,s) C(n-i, j-s) (Krawtchouk polynomial)

        Args:
            weight_enum: Weight enumerator {weight: count}
            n: Code length
            k: Code dimension
            q: Field size

        Returns:
            Dual weight enumerator
        """
        if k < 0 or k > n:
            return {'success': False, 'error': f'Invalid k={k} for n={n}'}

        try:
            if q != 2:
                return {'success': False, 'error': 'MacWilliams for q≠2 not implemented'}

            # |C| = 2^k, |C⊥| = 2^(n-k)
            code_size = 1 << k

            # Compute dual weight enumerator using Krawtchouk polynomials
            dual_enum = {}

            for j in range(n + 1):
                B_j = 0.0

                for i, A_i in weight_enum.items():
                    if i < 0 or i > n:
                        continue

                    # Krawtchouk polynomial K_j(i)
                    K_j_i = self._krawtchouk(n, j, i, q)
                    B_j += A_i * K_j_i

                B_j /= code_size

                # Should be integer for valid code
                B_j_int = int(round(B_j))
                if B_j_int > 0:
                    dual_enum[j] = B_j_int

            self.macwilliams_transforms += 1

            # Verify: dual should have |C⊥| = 2^(n-k) codewords
            total_dual = sum(dual_enum.values())
            expected_dual = 1 << (n - k)

            return {
                'success': True,
                'original_weight_enum': weight_enum,
                'dual_weight_enum': dual_enum,
                'n': n,
                'k_original': k,
                'k_dual': n - k,
                'code_size': code_size,
                'dual_size': total_dual,
                'expected_dual_size': expected_dual,
                'valid': total_dual == expected_dual,
                'method': 'krawtchouk_transform'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _krawtchouk(self, n: int, k: int, x: int, q: int = 2) -> float:
        """
        Compute Krawtchouk polynomial K_k^(n)(x; q).

        K_k(x) = Σ_{j=0}^k (-1)^j (q-1)^{k-j} C(x,j) C(n-x, k-j)

        For binary (q=2): K_k(x) = Σ_{j=0}^k (-1)^j C(x,j) C(n-x, k-j)
        """
        result = 0.0
        for j in range(k + 1):
            if j > x or (k - j) > (n - x):
                continue
            term = ((-1) ** j) * ((q - 1) ** (k - j))
            term *= binomial(x, j) * binomial(n - x, k - j)
            result += term
        return result

    def is_doubly_even(
        self,
        codewords: List[List[int]]
    ) -> Dict[str, Any]:
        """
        Check if code is doubly-even (all weights ≡ 0 mod 4).

        Doubly-even codes have special properties:
        - Only exist for n ≡ 0 (mod 8) if self-dual
        - Extended Golay (24,12,8) is doubly-even

        Args:
            codewords: List of all codewords

        Returns:
            Whether code is doubly-even
        """
        if not codewords:
            return {'success': False, 'error': 'Codeword list cannot be empty'}

        try:
            weights_mod_4 = set()
            example_non_divisible = None

            for cw in codewords:
                w = hamming_weight(cw)
                mod4 = w % 4
                weights_mod_4.add(mod4)

                if mod4 != 0 and example_non_divisible is None:
                    example_non_divisible = (cw, w)

            is_doubly_even = (weights_mod_4 == {0})
            is_even = (0 not in weights_mod_4 or weights_mod_4 <= {0, 2})

            # Actually is_even means all weights are even (mod 2 = 0)
            all_even = all(hamming_weight(cw) % 2 == 0 for cw in codewords)

            self.doubly_even_checks += 1

            return {
                'success': True,
                'is_doubly_even': is_doubly_even,
                'is_singly_even': all_even and not is_doubly_even,
                'is_even': all_even,
                'weight_classes_mod_4': sorted(weights_mod_4),
                'num_codewords': len(codewords),
                'example_non_divisible': example_non_divisible,
                'method': 'weight_divisibility_check'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def is_even(
        self,
        codewords: List[List[int]]
    ) -> Dict[str, Any]:
        """
        Check if code is even (all weights divisible by 2).

        Args:
            codewords: List of all codewords

        Returns:
            Whether code is even
        """
        if not codewords:
            return {'success': False, 'error': 'Codeword list cannot be empty'}

        try:
            odd_weight_codeword = None

            for cw in codewords:
                w = hamming_weight(cw)
                if w % 2 == 1:
                    odd_weight_codeword = (cw, w)
                    break

            is_even = (odd_weight_codeword is None)

            return {
                'success': True,
                'is_even': is_even,
                'num_codewords': len(codewords),
                'odd_weight_example': odd_weight_codeword,
                'method': 'weight_parity_check'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def hull_dimension(
        self,
        G: List[List[int]],
        q: int = 2
    ) -> Dict[str, Any]:
        """
        Compute hull of code: Hull(C) = C ∩ C⊥.

        The hull measures "how self-orthogonal" the code is.
        - dim(Hull) = 0: LCD code (linear complementary dual)
        - dim(Hull) = k: self-orthogonal code

        Args:
            G: Generator matrix
            q: Field size

        Returns:
            Hull dimension and properties
        """
        if not G or not G[0]:
            return {'success': False, 'error': 'Generator matrix cannot be empty'}

        try:
            k = len(G)
            n = len(G[0])

            if q != 2:
                return {'success': False, 'error': 'Hull for q≠2 not implemented'}

            # Compute G · G^T (k × k matrix)
            GGT = [[0] * k for _ in range(k)]
            for i in range(k):
                for j in range(k):
                    inner = 0
                    for t in range(n):
                        inner ^= G[i][t] & G[j][t]
                    GGT[i][j] = inner

            # Hull dimension = k - rank(G · G^T)
            rank_GGT = gf2_rank(GGT)
            hull_dim = k - rank_GGT

            is_lcd = (hull_dim == 0)
            is_self_orthogonal = (hull_dim == k)

            return {
                'success': True,
                'hull_dimension': hull_dim,
                'k': k,
                'n': n,
                'rank_GGT': rank_GGT,
                'is_lcd': is_lcd,
                'is_self_orthogonal': is_self_orthogonal,
                'method': 'GGT_rank'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ========================================
    # Task Processing
    # ========================================

    def process(self, task_entry: Any) -> Any:
        """Process dual code task."""
        self.tasks_executed += 1

        try:
            if hasattr(task_entry, 'metadata'):
                metadata = task_entry.metadata or {}
            elif isinstance(task_entry, dict):
                metadata = task_entry
            else:
                metadata = {'operation': str(task_entry)}

            operation = metadata.get('operation', 'construct_dual')
            G = metadata.get('generator') or metadata.get('G')
            H = metadata.get('parity_check') or metadata.get('H')
            codewords = metadata.get('codewords')
            weight_enum = metadata.get('weight_enum') or metadata.get('weight_distribution')
            n = metadata.get('n')
            k = metadata.get('k')
            q = metadata.get('q', 2)

            if operation in ['dual', 'construct_dual', 'build_dual']:
                result = self.construct_dual(G, H, q)
            elif operation in ['self_dual', 'verify_self_dual', 'is_self_dual']:
                result = self.verify_self_dual(G, q)
            elif operation in ['self_orthogonal', 'is_self_orthogonal']:
                result = self.is_self_orthogonal(G, q)
            elif operation in ['macwilliams', 'macwilliams_transform', 'transform']:
                result = self.macwilliams_transform(weight_enum, n, k, q)
            elif operation in ['doubly_even', 'is_doubly_even']:
                result = self.is_doubly_even(codewords)
            elif operation in ['even', 'is_even']:
                result = self.is_even(codewords)
            elif operation in ['hull', 'hull_dimension']:
                result = self.hull_dimension(G, q)
            else:
                if G is not None:
                    result = self.construct_dual(G, H, q)
                else:
                    result = {'success': False, 'error': f'Unknown operation: {operation}'}

            if result.get('success', False):
                self.tasks_succeeded += 1
            else:
                self.tasks_failed += 1

            if self.blackboard and hasattr(task_entry, 'conversation_id'):
                return create_entry(
                    EntryType.PARTIAL_RESULT,
                    str(result),
                    self.agent_id,
                    task_entry.conversation_id,
                    ['error_correction', 'dual_code', 'macwilliams'],
                    EntryStatus.COMPLETED if result.get('success') else EntryStatus.FAILED,
                    {'result': result}
                )

            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[{self.agent_id}] Task processing failed: {e}")
            return {'success': False, 'error': str(e)}

    # ========================================
    # BDI Interface
    # ========================================

    def update_beliefs(self):
        """PERCEIVE: Monitor blackboard for dual code tasks."""
        if not self.blackboard:
            return

        entries = self.blackboard.query_entries(
            tags=['dual_code', 'dual', 'macwilliams', 'self_dual'],
            status=EntryStatus.PENDING
        )

        for entry in entries:
            belief_key = f'pending_dual_{entry.entry_id}'
            if not self.has_belief(belief_key):
                self.add_belief(belief_key, entry, confidence=1.0, source='blackboard')

    def deliberate(self) -> List[Intention]:
        """DELIBERATE: Create plans from beliefs."""
        new_intentions = []

        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_dual_'):
                continue

            task = belief.content
            task_id = task.entry_id if hasattr(task, 'entry_id') else str(task)

            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue

            intention = Intention(
                goal=f'solve_dual_{task_id}',
                plan=['claim', 'solve', 'post'],
                priority=5,
                metadata={'task_id': task_id, 'task_entry': task}
            )
            new_intentions.append(intention)

        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Run one action from plan."""
        action = intention.get_current_action()

        if action == 'claim':
            intention.advance()
        elif action == 'solve':
            task_entry = intention.metadata.get('task_entry')
            result = self.process(task_entry)
            intention.metadata['result'] = result
            intention.advance()
        elif action == 'post':
            result = intention.metadata.get('result')
            if self.blackboard and result and hasattr(result, 'entry_type'):
                self.blackboard.post(result)
            intention.complete()

    # ========================================
    # Statistics
    # ========================================

    def get_stats(self) -> Dict[str, int]:
        """Return computation statistics."""
        return {
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'duals_constructed': self.duals_constructed,
            'self_dual_checks': self.self_dual_checks,
            'macwilliams_transforms': self.macwilliams_transforms,
            'doubly_even_checks': self.doubly_even_checks,
        }
