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

# Symbo: Neural-Symbolic Mathematical Reasoning Engine
# =====================================================
#
# This package provides the core LLM-like capabilities for SYMBO_AGENTIC_REASONERS:
# - NanoTensor: Symbolic tensor operations with Gröbner basis solving
# - SymbolicTrainer: Training for symbolic tensors
# - SymboLLMCore: Trainable transformer model for mathematical reasoning
# - SymboLLMAdapter: High-level interface for the LLM
#
# Integration with SYMBO_AGENTIC_REASONERS Phase 5:
# - Thought trace harvesting feeds into training
# - Hybrid deployment routes between Symbo and symbolic specialists
# - Continuous learning from verified solutions

from .nano_tensor import NanoTensor, SymbolicTrainer, HybridTrainer, KnowledgeBase
from .symbo_llm_core import SymboLLMCore, TransformerBlock, SimpleTokenizer
from .symbo_llm import SymboLLMAdapter, LLMTask

__all__ = [
    'NanoTensor',
    'SymbolicTrainer',
    'HybridTrainer',
    'KnowledgeBase',
    'SymboLLMCore',
    'TransformerBlock',
    'SimpleTokenizer',
    'SymboLLMAdapter',
    'LLMTask',
]
