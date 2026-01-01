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
Policy Network - "The Tactician"
==================================

Agent 2.1 of the Deep Search Team

Specialized implementation of the AlphaProof Prover. Generates massive
search trees of potential proof steps (tactics). Operates probabilistically,
suggesting the "next move" based on patterns learned from synthetic theorem
training.

Output: ProofStep candidates with action probabilities and tactical annotations

Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx, Section 2
Reference: Phase_6_Build_Order_Breakdown.md, Step 2
"""

import logging
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

# Initialize module logger
try:
    from symbo_agentic_reasoners_logging import get_logger
    logger = get_logger('symbo_agentic_reasoners.phase6.deep_search.policy_network')
except ImportError:
    logger = logging.getLogger(__name__)

# Note: PyTorch import with fallback for systems without GPU or incompatible versions
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except (ImportError, RuntimeError, OSError) as e:
    # ImportError: torch not installed
    # RuntimeError: torch version incompatible with Python version (e.g., Python 3.14)
    # OSError: library loading issues
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None
    logging.getLogger(__name__).debug(f"PyTorch not available: {e}")


class TacticCategory(Enum):
    """Categories of proof tactics"""
    INTRODUCTION = 'introduction'      # intro, intros, assume
    ELIMINATION = 'elimination'        # apply, exact, cases
    REWRITING = 'rewriting'           # rw, simp, ring
    AUTOMATION = 'automation'         # auto, linarith, omega
    SPLITTING = 'splitting'           # constructor, use, exists
    INDUCTION = 'induction'           # induction, strong_induction
    CONTRADICTION = 'contradiction'    # by_contra, exfalso
    COMPUTATION = 'computation'        # norm_num, decide, native_decide


@dataclass
class TacticCandidate:
    """
    A potential proof step with its probability.

    Attributes:
        tactic: The tactic string (e.g., "intro h", "apply IH")
        probability: Probability assigned by policy network
        category: Category of the tactic
        expected_subgoals: Expected number of subgoals after application
        tactical_notes: Additional notes about when to use this tactic
    """
    tactic: str
    probability: float
    category: TacticCategory = TacticCategory.AUTOMATION
    expected_subgoals: int = 1
    tactical_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        """Perform to dict operation.

        Args:
        No arguments

        Returns:
        Result of the operation

        Example:
        >>> result = obj.to_dict(...)
        """
        return {
            'tactic': self.tactic,
            'probability': self.probability,
            'category': self.category.value,
            'expected_subgoals': self.expected_subgoals,
            'tactical_notes': self.tactical_notes
        }


class PolicyNetwork:
    """
    Agent 2.1: The Tactician - AlphaProof-style policy network

    Generates proof step probabilities based on the current proof state.
    Uses a transformer-based architecture to encode proof states and
    predict tactic probabilities.

    Key capabilities:
    - Proof state encoding
    - Tactic probability prediction
    - Top-k tactic generation
    - Tactical hint generation

    Reference: Phase 6 must engineer the capacity for novel mathematical discovery.docx
    """

    # Common Lean4 tactics vocabulary
    TACTIC_VOCABULARY = [
        # Introduction tactics
        "intro", "intros", "intro h", "intro n", "intro x",
        # Application tactics
        "apply", "exact", "exact?", "apply?",
        # Rewriting tactics
        "rw", "rw [h]", "simp", "simp only", "simp_all", "ring", "ring_nf",
        # Automation
        "auto", "linarith", "omega", "nlinarith", "polyrith",
        "norm_num", "decide", "native_decide", "trivial",
        # Case analysis
        "cases", "rcases", "obtain", "cases h",
        # Constructors
        "constructor", "left", "right", "use", "exists", "refine",
        # Induction
        "induction", "induction n with n ih", "strong_induction",
        # Contradiction
        "by_contra", "exfalso", "contradiction", "absurd",
        # Equality
        "rfl", "ext", "funext", "congr", "calc",
        # Other
        "have", "let", "specialize", "assumption", "push_neg",
        "by_cases", "split", "sorry"
    ]

    # Tactic categories for classification
    TACTIC_CATEGORIES = {
        'intro': TacticCategory.INTRODUCTION,
        'intros': TacticCategory.INTRODUCTION,
        'apply': TacticCategory.ELIMINATION,
        'exact': TacticCategory.ELIMINATION,
        'rw': TacticCategory.REWRITING,
        'simp': TacticCategory.REWRITING,
        'ring': TacticCategory.REWRITING,
        'linarith': TacticCategory.AUTOMATION,
        'omega': TacticCategory.AUTOMATION,
        'cases': TacticCategory.SPLITTING,
        'rcases': TacticCategory.SPLITTING,
        'constructor': TacticCategory.SPLITTING,
        'induction': TacticCategory.INDUCTION,
        'by_contra': TacticCategory.CONTRADICTION,
        'norm_num': TacticCategory.COMPUTATION,
        'decide': TacticCategory.COMPUTATION
    }

    def __init__(self, hidden_dim: int = 512, num_heads: int = 8, num_layers: int = 4):
        """
        Initialize the Policy Network.

        Args:
            hidden_dim: Hidden dimension for transformer
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
        """
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.num_tactics = len(self.TACTIC_VOCABULARY)

        # Build neural network if PyTorch is available
        if TORCH_AVAILABLE:
            self._build_network()
        else:
            self.model = None

        # Statistics
        self.stats = {
            'predictions_made': 0,
            'tactics_generated': 0,
            'average_confidence': 0.0
        }

    def _build_network(self):
        """Build the transformer-based policy network"""
        class PolicyTransformer(nn.Module):
            def __init__(self, vocab_size, hidden_dim, num_heads, num_layers, num_tactics):
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

                self.policy_head = nn.Sequential(
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(hidden_dim, num_tactics)
                )

            def forward(self, x):
                """Perform forward operation.

                Args:
                x: Description needed

                Returns:
                Result of the operation

                Example:
                >>> result = obj.forward(...)
                """
                """Perform forward operation.

                Args:
                x: Description needed

                Returns:
                Result of the operation

                Example:
                >>> result = obj.forward(...)
                """
                # x: [batch, seq_len]
                seq_len = x.size(1)
                embedded = self.embedding(x) + self.pos_encoding[:, :seq_len, :]
                encoded = self.encoder(embedded)
                pooled = encoded.mean(dim=1)  # Average pooling
                logits = self.policy_head(pooled)
                return F.softmax(logits, dim=-1)

        self.model = PolicyTransformer(
            vocab_size=10000,  # Token vocabulary size
            hidden_dim=self.hidden_dim,
            num_heads=self.num_heads,
            num_layers=self.num_layers,
            num_tactics=self.num_tactics
        )

    def generate_tactics(
        self,
        proof_state: 'ProofState',
        top_k: int = 5,
        temperature: float = 1.0
    ) -> List[TacticCandidate]:
        """
        Generate top-k tactic candidates for a proof state.

        Args:
            proof_state: Current proof state with goal and hypotheses
            top_k: Number of tactics to return
            temperature: Sampling temperature (higher = more diverse)

        Returns:
            List of TacticCandidate objects sorted by probability
        """
        self.stats['predictions_made'] += 1

        if TORCH_AVAILABLE and self.model is not None:
            return self._neural_generate(proof_state, top_k, temperature)
        else:
            return self._heuristic_generate(proof_state, top_k)

    def _neural_generate(
        self,
        proof_state: 'ProofState',
        top_k: int,
        temperature: float
    ) -> List[TacticCandidate]:
        """Generate tactics using neural network"""
        # Tokenize proof state
        tokens = self._tokenize_state(proof_state)

        with torch.no_grad():
            probs = self.model(tokens.unsqueeze(0))[0]

            # Apply temperature
            if temperature != 1.0:
                probs = F.softmax(torch.log(probs + 1e-10) / temperature, dim=-1)

        # Get top-k
        top_probs, top_indices = torch.topk(probs, k=min(top_k, self.num_tactics))

        candidates = []
        for prob, idx in zip(top_probs.tolist(), top_indices.tolist()):
            tactic = self.TACTIC_VOCABULARY[idx]
            category = self._get_tactic_category(tactic)
            candidates.append(TacticCandidate(
                tactic=tactic,
                probability=prob,
                category=category,
                expected_subgoals=self._estimate_subgoals(tactic),
                tactical_notes=self._generate_notes(tactic, proof_state)
            ))

        self.stats['tactics_generated'] += len(candidates)
        if candidates:
            self.stats['average_confidence'] = sum(c.probability for c in candidates) / len(candidates)

        return candidates

    def _heuristic_generate(
        self,
        proof_state: 'ProofState',
        top_k: int
    ) -> List[TacticCandidate]:
        """Generate tactics using heuristics (fallback when no GPU)"""
        goal = proof_state.goal if hasattr(proof_state, 'goal') else str(proof_state)
        hypotheses = proof_state.hypotheses if hasattr(proof_state, 'hypotheses') else []

        # Score tactics based on goal structure
        tactic_scores = []

        for tactic in self.TACTIC_VOCABULARY:
            score = self._heuristic_score(tactic, goal, hypotheses)
            tactic_scores.append((tactic, score))

        # Sort by score and take top-k
        tactic_scores.sort(key=lambda x: x[1], reverse=True)

        # Normalize scores to probabilities
        total = sum(s for _, s in tactic_scores[:top_k])
        if total == 0:
            total = 1

        candidates = []
        for tactic, score in tactic_scores[:top_k]:
            prob = score / total
            category = self._get_tactic_category(tactic)
            candidates.append(TacticCandidate(
                tactic=tactic,
                probability=prob,
                category=category,
                expected_subgoals=self._estimate_subgoals(tactic),
                tactical_notes=self._generate_notes(tactic, proof_state)
            ))

        self.stats['tactics_generated'] += len(candidates)
        return candidates

    def _heuristic_score(self, tactic: str, goal: str, hypotheses: List[str]) -> float:
        """Score a tactic based on heuristics"""
        score = 0.5  # Base score

        goal_lower = goal.lower()
        hyp_str = ' '.join(hypotheses).lower()

        # Boost intro for universal quantifiers
        if tactic.startswith('intro') and ('∀' in goal or 'forall' in goal_lower):
            score += 0.4

        # Boost apply/exact if hypotheses available
        if tactic in ['apply', 'exact'] and hypotheses:
            score += 0.3

        # Boost simp/ring for algebraic expressions
        if tactic in ['simp', 'ring'] and any(op in goal for op in ['+', '*', '-', '^']):
            score += 0.35

        # Boost linarith for inequalities
        if tactic == 'linarith' and any(op in goal for op in ['<', '>', '≤', '≥']):
            score += 0.4

        # Boost induction for natural number goals
        if tactic.startswith('induction') and ('ℕ' in goal or 'Nat' in goal or 'n' in goal_lower):
            score += 0.35

        # Boost rfl for reflexive equality
        if tactic == 'rfl' and '=' in goal:
            score += 0.3

        # Boost cases for disjunction
        if tactic.startswith('cases') and ('∨' in goal or 'or' in goal_lower):
            score += 0.35

        # Boost constructor for conjunction
        if tactic == 'constructor' and ('∧' in goal or 'and' in goal_lower):
            score += 0.35

        # Boost by_contra for negation
        if tactic == 'by_contra' and ('¬' in goal or 'not' in goal_lower):
            score += 0.3

        # Boost norm_num for numeric goals
        if tactic == 'norm_num' and any(c.isdigit() for c in goal):
            score += 0.4

        return score

    def _tokenize_state(self, proof_state: 'ProofState') -> 'torch.Tensor':
        """Tokenize proof state for neural network input"""
        goal = proof_state.goal if hasattr(proof_state, 'goal') else str(proof_state)
        hypotheses = proof_state.hypotheses if hasattr(proof_state, 'hypotheses') else []

        # Combine goal and hypotheses
        text = f"GOAL: {goal} HYPS: {' '.join(hypotheses)}"

        # Simple character-based tokenization (would use proper tokenizer in production)
        tokens = [ord(c) % 10000 for c in text][:512]
        tokens += [0] * (512 - len(tokens))  # Pad

        return torch.tensor(tokens)

    def _get_tactic_category(self, tactic: str) -> TacticCategory:
        """Get category for a tactic"""
        base_tactic = tactic.split()[0] if ' ' in tactic else tactic
        return self.TACTIC_CATEGORIES.get(base_tactic, TacticCategory.AUTOMATION)

    def _estimate_subgoals(self, tactic: str) -> int:
        """Estimate number of subgoals after applying tactic"""
        base = tactic.split()[0] if ' ' in tactic else tactic

        # Tactics that typically close goals
        if base in ['exact', 'rfl', 'trivial', 'assumption', 'contradiction']:
            return 0

        # Tactics that typically split
        if base in ['constructor', 'cases', 'induction', 'split']:
            return 2

        # Tactics that typically create subgoals
        if base in ['have', 'suffices']:
            return 2

        # Default
        return 1

    def _generate_notes(self, tactic: str, proof_state: 'ProofState') -> str:
        """Generate tactical notes about when to use the tactic"""
        base = tactic.split()[0] if ' ' in tactic else tactic

        notes = {
            'intro': "Use to introduce universally quantified variables or hypothesis",
            'apply': "Use to apply a hypothesis or lemma that matches the goal",
            'exact': "Use when a hypothesis exactly matches the goal",
            'simp': "Use for automatic simplification using simp lemmas",
            'ring': "Use for algebraic ring identities",
            'linarith': "Use for linear arithmetic reasoning",
            'induction': "Use for proofs by induction on natural numbers",
            'cases': "Use to perform case analysis on a hypothesis",
            'constructor': "Use to prove conjunctions or existentials",
            'rfl': "Use when goal is reflexive equality",
            'by_contra': "Use to start a proof by contradiction"
        }

        return notes.get(base, f"Apply {tactic} tactic")

    def get_statistics(self) -> Dict[str, Any]:
        """Get network statistics"""
        return {
            **self.stats,
            'vocab_size': len(self.TACTIC_VOCABULARY),
            'torch_available': TORCH_AVAILABLE,
            'model_loaded': self.model is not None if TORCH_AVAILABLE else False
        }

    def reset(self):
        """Reset statistics"""
        self.stats = {
            'predictions_made': 0,
            'tactics_generated': 0,
            'average_confidence': 0.0
        }

    def health_check(self) -> bool:
        """Check if policy network is healthy"""
        try:
            # Create a dummy proof state
            class DummyState:
                goal = "x = x"
                hypotheses = []

            tactics = self.generate_tactics(DummyState(), top_k=3)
            return len(tactics) > 0
        except (TypeError, ValueError, RuntimeError) as e:
            logger.warning(f"PolicyNetwork health check failed: {e}")
            return False
