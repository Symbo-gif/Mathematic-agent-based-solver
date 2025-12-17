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
PHASE 2 - LA-4: TENSOR OPERATIONS AGENT (Tier 3)
================================================

Specializes in tensor algebra operations including contractions,
outer products, and invariant computations.

CAPABILITIES:
------------
- Tensor construction and indexing
- Tensor contraction operations
- Outer products (tensor products)
- Index raising/lowering with metrics
- Invariant computation (trace, determinant)
- Einstein summation convention

ALGORITHMIC BACKING:
-------------------
- SymPy's tensor module for symbolic operations
- NumPy/PyTorch backends for numerical operations
- Custom index tracking system

REFERENCE:
---------
- Agent_System_Audit.docx.md: LA-4 Tensor Operations Agent
- Phase_2_Build_Order_Breakdown.md: Linear Algebra Team
"""

import sys
import os
import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from itertools import permutations

# Native symbolic imports - NO SYMPY
from symbo_agentic_reasoners.core.native_symbolic import (
    Symbol, symbols, parse_expr, Expr, Integer, Float, Rational,
    Add, Mul, Pow
)

# Require numpy for tensor operations
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

logger = logging.getLogger('symbo_agentic_reasoners.phase2.tensor_operations')

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)
from symbo_agentic_reasoners.core.omdoc_schema import create_variable


class TensorType(Enum):
    """Types of tensors based on rank"""
    SCALAR = "scalar"        # Rank 0
    VECTOR = "vector"        # Rank 1
    MATRIX = "matrix"        # Rank 2
    TENSOR_3 = "tensor_3"    # Rank 3
    TENSOR_N = "tensor_n"    # Rank > 3


class IndexType(Enum):
    """Types of tensor indices"""
    CONTRAVARIANT = "upper"   # Upper index (superscript)
    COVARIANT = "lower"       # Lower index (subscript)


@dataclass
class TensorIndex:
    """Represents a tensor index"""
    name: str
    position: int
    index_type: IndexType
    dimension: Optional[int] = None


@dataclass
class TensorInfo:
    """
    Information about a tensor.
    
    Attributes:
        name: Tensor name/identifier
        rank: Number of indices
        shape: Dimensions along each axis
        indices: List of index specifications
        is_symmetric: Whether tensor is symmetric
        is_antisymmetric: Whether tensor is antisymmetric
    """
    name: str
    rank: int
    shape: Tuple[int, ...]
    indices: List[TensorIndex] = field(default_factory=list)
    is_symmetric: bool = False
    is_antisymmetric: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'rank': self.rank,
            'shape': self.shape,
            'is_symmetric': self.is_symmetric,
            'is_antisymmetric': self.is_antisymmetric
        }


@dataclass
class ContractionResult:
    """Result of tensor contraction"""
    result_tensor: Any
    contracted_indices: List[Tuple[int, int]]
    original_rank: int
    result_rank: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'contracted_indices': self.contracted_indices,
            'original_rank': self.original_rank,
            'result_rank': self.result_rank
        }


class TensorOperationsAgent(BDIAgent):
    """
    LA-4: Tensor Operations Agent
    
    DIRECTIVE:
    ---------
    Handle tensor algebra operations including contractions, products,
    and invariant computations.
    
    INPUTS:
    ------
    - Tensor data (arrays or symbolic)
    - Contraction index specifications
    - Operation type (contraction, product, etc.)
    
    OUTPUTS:
    -------
    - Contracted tensors
    - Invariant quantities
    - Tensor products
    
    DEPENDENCIES:
    ------------
    - LA-1 (MatrixOperationsSpecialist): For matrix-level operations
    
    FAILURE MODE: RECOVERABLE
    
    REFERENCE:
    ---------
    Agent_System_Audit.docx.md: Lines 283-293
    """
    
    def __init__(
        self,
        agent_id: str = 'tensor_operations_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        use_gpu: bool = False
    ):
        """
        Initialize Tensor Operations Agent
        
        Args:
            agent_id: Unique specialist identifier
            df: Directory Facilitator instance
            blackboard: Blackboard instance
            use_gpu: Whether to use GPU for numerical operations
        """
        super().__init__(agent_id)
        
        self.df = df
        self.blackboard = blackboard
        self.use_gpu = use_gpu
        
        # Index tracking system
        self.index_registry: Dict[str, TensorIndex] = {}
        
        # Statistics
        self.tasks_executed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.contractions_performed = 0
        self.products_computed = 0
        
        # Register with Directory Facilitator
        if self.df:
            self._register_services()
        
        print(f"[{self.agent_id}] Tensor Operations Agent initialized")
        print(f"  Capabilities: Contraction, Tensor product, Invariants")
        print(f"  NumPy available: {HAS_NUMPY}")
        print(f"  GPU enabled: {use_gpu}")
    
    def _register_services(self):
        """Register services with Directory Facilitator"""
        registration = create_service_registration(
            service_type='math.linear_algebra.tensor',
            agent_id=self.agent_id,
            algorithm='tensor_contraction',
            cost='high',
            instance=self,  # Enable direct invocation by supervisors
            type='exact',
            tier='3',
            algorithms='contraction_product_invariant'
        )
        self.df.register(registration)
        print(f"  [DF] Registered: math.linear_algebra.tensor")
    
    def create_tensor(
        self,
        data: Union[List, 'np.ndarray'],
        name: str = "T"
    ) -> Tuple['np.ndarray', TensorInfo]:
        """
        Create a tensor from data.

        Uses numpy arrays - NO SYMPY.

        Args:
            data: Tensor data (nested lists or numpy array)
            name: Name for the tensor

        Returns:
            Tuple of (numpy array, TensorInfo)
        """
        self.tasks_executed += 1

        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for tensor operations")

            # Convert to numpy array
            if isinstance(data, np.ndarray):
                tensor = data.astype(float)
            else:
                tensor = np.array(data, dtype=float)

            shape = tensor.shape
            rank = len(shape)

            # Determine tensor type
            if rank == 0:
                tensor_type = TensorType.SCALAR
            elif rank == 1:
                tensor_type = TensorType.VECTOR
            elif rank == 2:
                tensor_type = TensorType.MATRIX
            elif rank == 3:
                tensor_type = TensorType.TENSOR_3
            else:
                tensor_type = TensorType.TENSOR_N

            # Create index specifications
            indices = []
            for i, dim in enumerate(shape):
                idx = TensorIndex(
                    name=f"i{i}",
                    position=i,
                    index_type=IndexType.COVARIANT,
                    dimension=dim
                )
                indices.append(idx)

            info = TensorInfo(
                name=name,
                rank=rank,
                shape=shape,
                indices=indices
            )

            self.tasks_succeeded += 1
            return tensor, info

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Tensor creation failed: {type(e).__name__}: {e}")
            raise
    
    def tensor_product(
        self,
        tensor_a: 'np.ndarray',
        tensor_b: 'np.ndarray'
    ) -> ContractionResult:
        """
        Compute the outer (tensor) product of two tensors.

        Uses numpy outer product - NO SYMPY.

        A (x) B creates a tensor with rank(A) + rank(B)

        Args:
            tensor_a: First tensor (numpy array)
            tensor_b: Second tensor (numpy array)

        Returns:
            ContractionResult with product tensor
        """
        self.tasks_executed += 1
        self.products_computed += 1

        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for tensor product")

            # Convert to numpy if needed
            a = np.array(tensor_a, dtype=float)
            b = np.array(tensor_b, dtype=float)

            # Outer product using numpy
            result = np.outer(a.flatten(), b.flatten()).reshape(a.shape + b.shape)

            original_rank = len(a.shape) + len(b.shape)
            result_rank = len(result.shape)

            self.tasks_succeeded += 1

            return ContractionResult(
                result_tensor=result,
                contracted_indices=[],
                original_rank=original_rank,
                result_rank=result_rank
            )

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Tensor product failed: {type(e).__name__}: {e}")
            raise
    
    def contract(
        self,
        tensor: 'np.ndarray',
        index_pairs: List[Tuple[int, int]]
    ) -> ContractionResult:
        """
        Contract a tensor over specified index pairs.

        Uses numpy einsum - NO SYMPY.

        Contraction sums over paired indices, reducing rank by 2 per pair.

        Args:
            tensor: The tensor to contract (numpy array)
            index_pairs: List of (i, j) index pairs to contract

        Returns:
            ContractionResult with contracted tensor
        """
        self.tasks_executed += 1
        self.contractions_performed += 1

        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for tensor contraction")

            t = np.array(tensor, dtype=float)
            original_rank = len(t.shape)

            # Apply contractions using numpy einsum
            result = t
            for pair in index_pairs:
                i, j = pair
                # Use trace-like operation for contraction
                result = np.trace(result, axis1=i, axis2=j)

            result_rank = len(result.shape) if hasattr(result, 'shape') else 0

            self.tasks_succeeded += 1

            return ContractionResult(
                result_tensor=result,
                contracted_indices=index_pairs,
                original_rank=original_rank,
                result_rank=result_rank
            )

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Contraction failed: {type(e).__name__}: {e}")
            raise
    
    def trace(self, tensor: 'np.ndarray') -> float:
        """
        Compute the trace of a rank-2 tensor (matrix).

        Uses numpy trace - NO SYMPY.

        Args:
            tensor: A rank-2 tensor (matrix)

        Returns:
            The trace (sum of diagonal elements)
        """
        self.tasks_executed += 1

        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for trace computation")

            t = np.array(tensor, dtype=float)

            if len(t.shape) != 2:
                raise ValueError(f"Trace requires rank-2 tensor, got rank {len(t.shape)}")

            if t.shape[0] != t.shape[1]:
                raise ValueError(f"Trace requires square matrix, got shape {t.shape}")

            # Use numpy trace
            result = float(np.trace(t))

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Trace computation failed: {type(e).__name__}: {e}")
            raise

    def determinant(self, tensor: 'np.ndarray') -> float:
        """
        Compute the determinant of a rank-2 tensor (matrix).

        Uses numpy linalg.det - NO SYMPY.

        Args:
            tensor: A rank-2 tensor (matrix)

        Returns:
            The determinant
        """
        self.tasks_executed += 1

        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for determinant computation")

            t = np.array(tensor, dtype=float)

            if len(t.shape) != 2:
                raise ValueError(f"Determinant requires rank-2 tensor, got rank {len(t.shape)}")

            # Use numpy determinant
            result = float(np.linalg.det(t))

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Determinant computation failed: {type(e).__name__}: {e}")
            raise
    
    def einstein_sum(
        self,
        expression: str,
        tensors: Dict[str, 'np.ndarray']
    ) -> 'np.ndarray':
        """
        Evaluate Einstein summation expression.

        Uses numpy einsum - NO SYMPY.

        Example: "ij,jk->ik" for matrix multiplication

        Args:
            expression: Einstein notation string
            tensors: Dictionary of tensor name to numpy array

        Returns:
            Result tensor (numpy array)
        """
        self.tasks_executed += 1

        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for Einstein summation")

            # Convert all tensors to numpy
            np_tensors = {}
            for name, tensor in tensors.items():
                if isinstance(tensor, np.ndarray):
                    np_tensors[name] = tensor.astype(float)
                else:
                    np_tensors[name] = np.array(tensor, dtype=float)

            # Get tensor list in order
            tensor_list = [np_tensors[name] for name in tensors.keys()]

            # Use numpy einsum
            result = np.einsum(expression, *tensor_list)

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Einstein sum failed: {type(e).__name__}: {e}")
            raise
    
    def symmetrize(self, tensor: 'np.ndarray') -> 'np.ndarray':
        """
        Symmetrize a tensor over all indices.

        Uses numpy transpose - NO SYMPY.

        Args:
            tensor: Input tensor (numpy array)

        Returns:
            Symmetrized tensor (numpy array)
        """
        self.tasks_executed += 1

        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for symmetrization")

            t = np.array(tensor, dtype=float)
            rank = len(t.shape)

            if rank < 2:
                self.tasks_succeeded += 1
                return t

            # Generate all permutations and average
            perms = list(permutations(range(rank)))
            result = t.copy()

            for perm in perms[1:]:  # Skip identity
                permuted = np.transpose(t, perm)
                result = result + permuted

            result = result / len(perms)

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Symmetrization failed: {type(e).__name__}: {e}")
            raise

    def antisymmetrize(self, tensor: 'np.ndarray') -> 'np.ndarray':
        """
        Antisymmetrize a tensor over all indices.

        Uses numpy transpose - NO SYMPY.

        Args:
            tensor: Input tensor (numpy array)

        Returns:
            Antisymmetrized tensor (numpy array)
        """
        self.tasks_executed += 1

        try:
            if not HAS_NUMPY:
                raise ImportError("NumPy required for antisymmetrization")

            t = np.array(tensor, dtype=float)
            rank = len(t.shape)

            if rank < 2:
                self.tasks_succeeded += 1
                return t

            # Generate all permutations with signs
            def parity(perm):
                """Compute parity of permutation"""
                perm = list(perm)
                n = len(perm)
                sign = 1
                for i in range(n):
                    for j in range(i + 1, n):
                        if perm[i] > perm[j]:
                            sign *= -1
                return sign

            perms = list(permutations(range(rank)))
            result = np.zeros_like(t)

            for perm in perms:
                permuted = np.transpose(t, perm)
                result = result + parity(perm) * permuted

            result = result / len(perms)

            self.tasks_succeeded += 1
            return result

        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Antisymmetrization failed: {type(e).__name__}: {e}")
            raise
    
    def process(self, task_entry: Any) -> Any:
        """Process tensor operation task from Blackboard"""
        print(f"\n[{self.agent_id}] Processing tensor task")
        
        try:
            metadata = task_entry.metadata if hasattr(task_entry, 'metadata') else {}
            operation = metadata.get('operation', 'create')
            
            if operation == 'create':
                data = metadata.get('data', [[1, 0], [0, 1]])
                name = metadata.get('name', 'T')
                tensor, info = self.create_tensor(data, name)
                result = {'tensor': str(tensor), 'info': info.to_dict()}
                
            elif operation == 'contract':
                data = metadata.get('data')
                pairs = metadata.get('index_pairs', [(0, 1)])
                tensor, _ = self.create_tensor(data)
                contract_result = self.contract(tensor, pairs)
                result = contract_result.to_dict()
                result['result'] = str(contract_result.result_tensor)
                
            elif operation == 'trace':
                data = metadata.get('data')
                tensor, _ = self.create_tensor(data)
                trace_val = self.trace(tensor)
                result = {'trace': str(trace_val)}
                
            elif operation == 'determinant':
                data = metadata.get('data')
                tensor, _ = self.create_tensor(data)
                det_val = self.determinant(tensor)
                result = {'determinant': str(det_val)}
                
            elif operation == 'product':
                data_a = metadata.get('tensor_a')
                data_b = metadata.get('tensor_b')
                tensor_a, _ = self.create_tensor(data_a)
                tensor_b, _ = self.create_tensor(data_b)
                prod_result = self.tensor_product(tensor_a, tensor_b)
                result = prod_result.to_dict()
                result['result'] = str(prod_result.result_tensor)
                
            else:
                result = {'error': f'Unknown operation: {operation}'}
            
            return self._create_result_entry(task_entry, result)
            
        except Exception as e:
            self.tasks_failed += 1
            logger.warning(f"Tensor task failed: {type(e).__name__}: {e}")
            return self._create_error_entry(task_entry, str(e))
    
    def _create_result_entry(self, task_entry: Any, result: Dict) -> Any:
        """Create result entry for Blackboard"""
        if not self.blackboard:
            return result
        
        result_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(str(result)),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'result'),
            tags=['tensor', 'linear_algebra'],
            status=EntryStatus.PENDING,
            metadata=result
        )
        
        self.blackboard.post(result_entry)
        return result_entry
    
    def _create_error_entry(self, task_entry: Any, error_msg: str) -> Any:
        """Create error entry for Blackboard"""
        if not self.blackboard:
            return None
        
        error_entry = create_entry(
            entry_type=EntryType.PARTIAL_RESULT,
            content=create_variable(f"ERROR: {error_msg}"),
            author_agent=self.agent_id,
            conversation_id=getattr(task_entry, 'conversation_id', 'error'),
            tags=['error', 'tensor'],
            status=EntryStatus.FAILED,
            metadata={'error': error_msg}
        )
        
        self.blackboard.post(error_entry)
        return error_entry
    
    # BDI Implementation
    def update_beliefs(self):
        """PERCEIVE: Monitor Blackboard for tensor tasks"""
        if not self.blackboard:
            return
        try:
            tensor_tasks = self.blackboard.query_entries(tags=['tensor'], status=EntryStatus.PENDING)
            delegated_tasks = self.blackboard.query_entries(entry_type=EntryType.TASK, status=EntryStatus.PENDING)
            for task in delegated_tasks:
                if hasattr(task, 'metadata') and task.metadata:
                    if task.metadata.get('assigned_agent') == self.agent_id and task not in tensor_tasks:
                        tensor_tasks.append(task)
            for task in tensor_tasks:
                belief_key = f'pending_task_{task.entry_id}'
                if not self.has_belief(f'claimed_task_{task.entry_id}') and not self.has_belief(belief_key):
                    self.add_belief(belief_key, task, confidence=1.0, source='blackboard')
        except Exception as e:
            logger.warning(f"[{self.agent_id}] update_beliefs error: {e}")

    def deliberate(self):
        """DELIBERATE: Generate computation plans for tensor operations"""
        new_intentions = []
        for predicate, belief in list(self.beliefs.items()):
            if not predicate.startswith('pending_task_'):
                continue
            task = belief.content
            task_id = task.entry_id
            if any(i.metadata.get('task_id') == task_id for i in self.intentions):
                continue
            metadata = task.metadata if hasattr(task, 'metadata') else {}
            operation = metadata.get('operation', 'contract')
            steps = ['claim_task', 'parse_tensors', 'compute_operation', 'verify_result', 'post_result']
            intention = Intention(
                plan_id=f'tensor_{operation}_{task_id}',
                steps=steps,
                target_desire='tensor_computation',
                metadata={'task_id': task_id, 'task_entry': task, 'operation': operation}
            )
            new_intentions.append(intention)
        return new_intentions

    def execute_step(self, intention: Intention):
        """EXECUTE: Execute tensor computation step (DELEGATE to SymPy tensor functions)"""
        action = intention.get_current_action()
        task = intention.metadata.get('task_entry')
        task_id = intention.metadata.get('task_id')
        try:
            if action == 'claim_task':
                if self.blackboard:
                    self.blackboard.update_entry_status(task_id, EntryStatus.IN_PROGRESS)
                self.add_belief(f'claimed_task_{task_id}', True)
                self.remove_belief(f'pending_task_{task_id}')
                intention.advance()
            elif action == 'parse_tensors':
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                data = metadata.get('data', [[1, 0], [0, 1]])
                tensor, info = self.create_tensor(data)
                intention.metadata['tensor'] = tensor
                intention.metadata['tensor_info'] = info
                intention.advance()
            elif action == 'compute_operation':
                operation = intention.metadata.get('operation', 'trace')
                tensor = intention.metadata.get('tensor')
                metadata = task.metadata if hasattr(task, 'metadata') else {}
                if operation == 'trace':
                    result = self.trace(tensor)
                elif operation == 'determinant':
                    result = self.determinant(tensor)
                elif operation == 'contract':
                    pairs = metadata.get('index_pairs', [(0, 1)])
                    result = self.contract(tensor, pairs).result_tensor
                elif operation == 'symmetrize':
                    result = self.symmetrize(tensor)
                elif operation == 'antisymmetrize':
                    result = self.antisymmetrize(tensor)
                else:
                    result = tensor
                intention.metadata['result'] = result
                self.add_belief('computed_result', result)
                intention.advance()
            elif action == 'verify_result':
                result = intention.metadata.get('result')
                verified = result is not None
                intention.metadata['verified'] = verified
                intention.advance()
            elif action == 'post_result':
                result = intention.metadata.get('result')
                if self.blackboard:
                    result_entry = create_entry(
                        entry_type=EntryType.PARTIAL_RESULT,
                        content=create_variable(str(result)),
                        author_agent=self.agent_id,
                        conversation_id=task.conversation_id if hasattr(task, 'conversation_id') else task_id,
                        tags=['tensor', 'result', task_id],
                        status=EntryStatus.COMPLETED,
                        metadata={'result': str(result), 'result_str': str(result), 'task_id': task_id}
                    )
                    self.blackboard.post(result_entry)
                    self.blackboard.update_entry_status(task_id, EntryStatus.COMPLETED)
                self.add_belief(f'completed_task_{task_id}', True)
                self.remove_belief(f'claimed_task_{task_id}')
                self.tasks_succeeded += 1
                intention.advance()
            else:
                intention.advance()
        except Exception as e:
            logger.error(f"[{self.agent_id}] Step {action} failed: {e}")
            self.remove_belief(f'pending_task_{task_id}')
            self.remove_belief(f'claimed_task_{task_id}')
            self.tasks_failed += 1
            while not intention.is_complete():
                intention.advance()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get specialist statistics"""
        stats = super().get_statistics()
        stats.update({
            'tasks_executed': self.tasks_executed,
            'tasks_succeeded': self.tasks_succeeded,
            'tasks_failed': self.tasks_failed,
            'success_rate': (self.tasks_succeeded / self.tasks_executed * 100)
                           if self.tasks_executed > 0 else 0.0,
            'contractions_performed': self.contractions_performed,
            'products_computed': self.products_computed,
            'numpy_available': HAS_NUMPY
        })
        return stats


if __name__ == "__main__":
    """Test Tensor Operations Agent"""
    print("=" * 80)
    print("PHASE 2 - TENSOR OPERATIONS AGENT TEST")
    print("=" * 80)
    print()
    
    # Initialize agent
    agent = TensorOperationsAgent()
    print()
    
    # Test 1: Create tensor
    print("Test 1: Create Tensor")
    data = [[1, 2], [3, 4]]
    tensor, info = agent.create_tensor(data, "A")
    print(f"  Tensor: {tensor}")
    print(f"  Rank: {info.rank}, Shape: {info.shape}")
    print()
    
    # Test 2: Trace
    print("Test 2: Compute Trace")
    trace_val = agent.trace(tensor)
    print(f"  Trace: {trace_val}")
    print()
    
    # Test 3: Determinant
    print("Test 3: Compute Determinant")
    det_val = agent.determinant(tensor)
    print(f"  Determinant: {det_val}")
    print()
    
    # Test 4: Tensor product
    print("Test 4: Tensor Product")
    v1, _ = agent.create_tensor([1, 2, 3], "v1")
    v2, _ = agent.create_tensor([4, 5], "v2")
    product = agent.tensor_product(v1, v2)
    print(f"  v1 ⊗ v2 shape: {product.result_tensor.shape}")
    print(f"  Result: {product.result_tensor}")
    print()
    
    # Test 5: Contraction
    print("Test 5: Tensor Contraction")
    rank3, _ = agent.create_tensor([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], "T3")
    print(f"  Original shape: {rank3.shape}")
    contracted = agent.contract(rank3, [(0, 1)])
    print(f"  After contraction (0,1): {contracted.result_tensor}")
    print()
    
    print("Statistics:")
    import json
    print(json.dumps(agent.get_statistics(), indent=2))
