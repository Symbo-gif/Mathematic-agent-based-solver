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
Critic Network - "The Evaluator"
==================================

Agent 2.2 of the Deep Search Team

Value-function agent that estimates the probability that a specific
branch of the search tree will lead to a successful proof. Enables
early pruning of dead ends, managing computational explosion in
undecidable domains.

Architecture: Transformer-based value estimator with proof-state embeddings

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 2
Reference: Phase_6_Build_Order_Breakdown.md, Step 2
"""

import logging
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.deep_search.critic_network')
except ImportError:
    logger = logging.getLogger(__name__)

# Note: PyTorch import with fallback for systems without GPU
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None


@dataclass
class ValueEstimate:
    """
    Value estimate for a proof state.

    Attributes:
        value: Estimated probability of proof success (0-1)
        confidence: Confidence in the estimate (0-1)
        features: Key features that influenced the estimate
        reasoning: Explanation for the value
    """
    value: float
    confidence: float
    features: Dict[str, float]
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value,
            'confidence': self.confidence,
            'features': self.features,
            'reasoning': self.reasoning
        }


class CriticNetwork:
    """
    Agent 2.2: The Evaluator - AlphaProof-style critic network

    Estimates the value (probability of proof success) for proof states.
    Used by SearchTreeManager to prioritize promising branches and prune
    dead ends without fully expanding them.

    Key capabilities:
    - Proof state value estimation
    - Confidence-weighted predictions
    - Feature extraction for interpretability
    - Dead-end detection

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    # Feature weights for heuristic evaluation
    FEATURE_WEIGHTS = {
        'goal_complexity': -0.3,      # Simpler goals are easier
        'hypothesis_count': 0.2,      # More hypotheses = more tools
        'depth': -0.15,               # Deeper = harder
        'pattern_match': 0.4,         # Known patterns are good
        'variable_count': -0.1,       # Fewer variables = easier
        'quantifier_count': -0.2,     # Fewer quantifiers = easier
        'has_equality': 0.15,         # Equality goals often tractable
        'has_inequality': -0.1,       # Inequalities can be tricky
        'tactic_options': 0.25        # More options = better chance
    }

    def __init__(self, hidden_dim: int = 512, num_heads: int = 8, num_layers: int = 4):
        """
        Initialize the Critic Network.

        Args:
            hidden_dim: Hidden dimension for transformer
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
        """
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.num_layers = num_layers

        # Build neural network if PyTorch is available
        if TORCH_AVAILABLE:
            self._build_network()
        else:
            self.model = None

        # Statistics
        self.stats = {
            'evaluations': 0,
            'average_value': 0.0,
            'dead_ends_detected': 0,
            'high_value_states': 0
        }

        # Running average for stats
        self._value_sum = 0.0

    def _build_network(self):
        """Build the transformer-based critic network"""
        class CriticTransformer(nn.Module):
            def __init__(self, vocab_size, hidden_dim, num_heads, num_layers):
                super().__init__()
                self.embedding = nn.Embedding(vocab_size, hidden_dim)
                self.pos_encoding = nn.Parameter(torch.randn(1, 512, hidden_dim))

                encoder_layer = nn.TransformerEncoderLayer(
                    d_model=hidden_dim,
                    nhead=num_heads,
                    dim_feedforward=hidden_dim * 4,
                    dropout=0.1,
                    batch_first=True
                )
                self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

                self.value_head = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(hidden_dim, 1),
                    nn.Sigmoid()
                )

            def forward(self, x):
                # x: [batch, seq_len]
                seq_len = x.size(1)
                embedded = self.embedding(x) + self.pos_encoding[:, :seq_len, :]
                encoded = self.encoder(embedded)
                pooled = encoded.mean(dim=1)  # Average pooling
                value = self.value_head(pooled)
                return value

        self.model = CriticTransformer(
            vocab_size=10000,
            hidden_dim=self.hidden_dim,
            num_heads=self.num_heads,
            num_layers=self.num_layers
        )

    def evaluate(self, proof_state: 'ProofState') -> float:
        """
        Evaluate a single proof state and return its value.

        Args:
            proof_state: The proof state to evaluate

        Returns:
            Value estimate between 0 and 1
        """
        estimate = self.evaluate_detailed(proof_state)
        return estimate.value

    def evaluate_detailed(self, proof_state: 'ProofState') -> ValueEstimate:
        """
        Evaluate a proof state with detailed explanation.

        Args:
            proof_state: The proof state to evaluate

        Returns:
            ValueEstimate with value, confidence, features, and reasoning
        """
        self.stats['evaluations'] += 1

        if TORCH_AVAILABLE and self.model is not None:
            value, confidence = self._neural_evaluate(proof_state)
        else:
            value, confidence = self._heuristic_evaluate(proof_state)

        # Extract features for interpretability
        features = self._extract_features(proof_state)

        # Generate reasoning
        reasoning = self._generate_reasoning(value, features)

        # Update statistics
        self._value_sum += value
        self.stats['average_value'] = self._value_sum / self.stats['evaluations']

        if value < 0.1:
            self.stats['dead_ends_detected'] += 1
        elif value > 0.7:
            self.stats['high_value_states'] += 1

        return ValueEstimate(
            value=value,
            confidence=confidence,
            features=features,
            reasoning=reasoning
        )

    def evaluate_batch(self, proof_states: List['ProofState']) -> List[float]:
        """
        Evaluate a batch of proof states.

        Args:
            proof_states: List of proof states

        Returns:
            List of value estimates
        """
        return [self.evaluate(state) for state in proof_states]

    def _neural_evaluate(self, proof_state: 'ProofState') -> Tuple[float, float]:
        """Evaluate using neural network"""
        tokens = self._tokenize_state(proof_state)

        with torch.no_grad():
            value = self.model(tokens.unsqueeze(0))[0, 0].item()

        # Confidence based on value extremity (more extreme = more confident)
        confidence = abs(value - 0.5) * 2

        return value, confidence

    def _heuristic_evaluate(self, proof_state: 'ProofState') -> Tuple[float, float]:
        """Evaluate using heuristics (fallback when no GPU)"""
        features = self._extract_features(proof_state)

        # Compute weighted sum
        value = 0.5  # Base value
        for feature, weight in self.FEATURE_WEIGHTS.items():
            if feature in features:
                value += weight * features[feature]

        # Clamp to [0, 1]
        value = max(0.0, min(1.0, value))

        # Confidence based on feature coverage
        coverage = len([f for f in features if features[f] != 0]) / len(self.FEATURE_WEIGHTS)
        confidence = 0.3 + 0.5 * coverage

        return value, confidence

    def _extract_features(self, proof_state: 'ProofState') -> Dict[str, float]:
        """Extract features from proof state for evaluation"""
        goal = proof_state.goal if hasattr(proof_state, 'goal') else str(proof_state)
        hypotheses = proof_state.hypotheses if hasattr(proof_state, 'hypotheses') else []
        depth = proof_state.depth if hasattr(proof_state, 'depth') else 0

        features = {}

        # Goal complexity (normalized by length)
        features['goal_complexity'] = min(1.0, len(goal) / 200)

        # Hypothesis count (normalized)
        features['hypothesis_count'] = min(1.0, len(hypotheses) / 10)

        # Depth (normalized)
        features['depth'] = min(1.0, depth / 50)

        # Pattern matching - check for known solvable patterns
        features['pattern_match'] = self._check_patterns(goal)

        # Variable count
        var_count = sum(1 for c in goal if c.islower() and c.isalpha())
        features['variable_count'] = min(1.0, var_count / 20)

        # Quantifier count
        quantifiers = goal.count('∀') + goal.count('∃') + goal.lower().count('forall') + goal.lower().count('exists')
        features['quantifier_count'] = min(1.0, quantifiers / 5)

        # Goal structure features
        features['has_equality'] = 1.0 if '=' in goal else 0.0
        features['has_inequality'] = 1.0 if any(op in goal for op in ['<', '>', '≤', '≥']) else 0.0

        # Estimate tactic options
        features['tactic_options'] = self._estimate_tactic_options(goal, hypotheses)

        return features

    def _check_patterns(self, goal: str) -> float:
        """Check for known solvable patterns"""
        score = 0.0

        # Reflexive equality is easy
        if '= ' in goal:
            parts = goal.split('=')
            if len(parts) == 2 and parts[0].strip() == parts[1].strip():
                score += 0.5

        # Simple numeric goals
        if any(c.isdigit() for c in goal) and len(goal) < 30:
            score += 0.3

        # True/trivial goals
        if goal.strip() in ['True', '⊤', 'trivial']:
            score += 0.8

        # Linear arithmetic patterns
        if all(c in '0123456789+-*/<>=() xyz' for c in goal.replace(' ', '')):
            score += 0.2

        return min(1.0, score)

    def _estimate_tactic_options(self, goal: str, hypotheses: List[str]) -> float:
        """Estimate how many tactics might be applicable"""
        options = 0

        # Always have simp, auto
        options += 2

        # Intro for quantifiers
        if '∀' in goal or 'forall' in goal.lower():
            options += 1

        # Apply if we have hypotheses
        if hypotheses:
            options += len(hypotheses)

        # Ring for algebraic expressions
        if any(op in goal for op in ['+', '*', '-', '^']):
            options += 1

        # Linarith for inequalities
        if any(op in goal for op in ['<', '>', '≤', '≥']):
            options += 1

        # Cases for disjunctions
        if '∨' in goal or 'or' in goal.lower():
            options += 1

        # Constructor for conjunctions
        if '∧' in goal or 'and' in goal.lower():
            options += 1

        return min(1.0, options / 10)

    def _generate_reasoning(self, value: float, features: Dict[str, float]) -> str:
        """Generate human-readable reasoning for the value estimate"""
        if value < 0.2:
            verdict = "This state appears to be a dead end."
        elif value < 0.4:
            verdict = "This state has low promise."
        elif value < 0.6:
            verdict = "This state has moderate promise."
        elif value < 0.8:
            verdict = "This state looks promising."
        else:
            verdict = "This state is highly promising."

        # Find top positive and negative factors
        sorted_features = sorted(
            [(f, v * self.FEATURE_WEIGHTS.get(f, 0)) for f, v in features.items()],
            key=lambda x: abs(x[1]),
            reverse=True
        )

        positive = [f for f, v in sorted_features if v > 0][:2]
        negative = [f for f, v in sorted_features if v < 0][:2]

        parts = [verdict]
        if positive:
            parts.append(f"Positive factors: {', '.join(positive)}")
        if negative:
            parts.append(f"Negative factors: {', '.join(negative)}")

        return " ".join(parts)

    def _tokenize_state(self, proof_state: 'ProofState') -> 'torch.Tensor':
        """Tokenize proof state for neural network input"""
        goal = proof_state.goal if hasattr(proof_state, 'goal') else str(proof_state)
        hypotheses = proof_state.hypotheses if hasattr(proof_state, 'hypotheses') else []

        text = f"GOAL: {goal} HYPS: {' '.join(hypotheses)}"
        tokens = [ord(c) % 10000 for c in text][:512]
        tokens += [0] * (512 - len(tokens))

        return torch.tensor(tokens)

    def is_dead_end(self, proof_state: 'ProofState', threshold: float = 0.1) -> bool:
        """
        Check if a proof state is likely a dead end.

        Args:
            proof_state: The state to check
            threshold: Value below which to consider dead end

        Returns:
            True if state is likely a dead end
        """
        value = self.evaluate(proof_state)
        return value < threshold

    def get_statistics(self) -> Dict[str, Any]:
        """Get network statistics"""
        return {
            **self.stats,
            'torch_available': TORCH_AVAILABLE,
            'model_loaded': self.model is not None if TORCH_AVAILABLE else False
        }

    def reset(self):
        """Reset statistics"""
        self.stats = {
            'evaluations': 0,
            'average_value': 0.0,
            'dead_ends_detected': 0,
            'high_value_states': 0
        }
        self._value_sum = 0.0

    def health_check(self) -> bool:
        """Check if critic network is healthy"""
        try:
            class DummyState:
                goal = "x = x"
                hypotheses = []
                depth = 0

            value = self.evaluate(DummyState())
            return 0 <= value <= 1
        except (TypeError, ValueError, RuntimeError) as e:
            logger.warning(f"CriticNetwork health check failed: {e}")
            return False
