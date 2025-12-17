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

"""Linear Algebra Specialists"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'MatrixOperationsSpecialist':
        from .matrix_ops_specialist import MatrixOperationsSpecialist
        return MatrixOperationsSpecialist
    elif name == 'DecompositionSpecialist':
        from .decomposition_specialist import DecompositionSpecialist
        return DecompositionSpecialist
    elif name == 'VectorSpaceAnalyst':
        from .vector_space_analyst import VectorSpaceAnalyst
        return VectorSpaceAnalyst
    elif name == 'AdvancedMatrixSpecialist':
        from .advanced_matrix_specialist import AdvancedMatrixSpecialist
        return AdvancedMatrixSpecialist
    elif name == 'JordanDecomposition':
        from .advanced_matrix_specialist import JordanDecomposition
        return JordanDecomposition
    elif name == 'MatrixFunctionResult':
        from .advanced_matrix_specialist import MatrixFunctionResult
        return MatrixFunctionResult
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Class exports (lazy loaded)
    "MatrixOperationsSpecialist",
    "DecompositionSpecialist",
    "VectorSpaceAnalyst",
    "AdvancedMatrixSpecialist",
    # Supporting types
    "JordanDecomposition",
    "MatrixFunctionResult",
    # Module aliases
    "matrix_ops_specialist",
    "decomposition_specialist",
    "vector_space_analyst",
    "advanced_matrix_specialist",
]