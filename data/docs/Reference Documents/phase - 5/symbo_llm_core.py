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
Symbo LLM Core - Real Neural Language Model

This is the actual neural network architecture for the Symbo LLM.
Supports:
- Real training with backpropagation
- Persistent model checkpoints
- Continuous learning from interactions
- Knowledge base integration
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any
import os
import json
import pickle
from datetime import datetime
import numpy as np


class SymboLLMCore(nn.Module):
    """
    Simple but functional transformer-based language model for Genesis.

    Architecture:
    - Token embedding layer
    - Positional encoding
    - Multi-head attention layers
    - Feed-forward layers
    - Output projection

    This is designed to be trainable and persistent.
    """

    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 256,
        num_heads: int = 4,
        num_layers: int = 3,
        ff_dim: int = 512,
        max_seq_len: int = 512,
        dropout: float = 0.1,
        device: str = "cuda"
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len
        self.device = device

        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)

        # Positional encoding
        self.pos_encoding = nn.Parameter(
            torch.zeros(1, max_seq_len, embed_dim)
        )

        # Transformer layers
        self.transformer_layers = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, ff_dim, dropout)
            for _ in range(num_layers)
        ])

        # Output projection
        self.output_proj = nn.Linear(embed_dim, vocab_size)

        # Dropout
        self.dropout = nn.Dropout(dropout)

        # Knowledge base for retrieval-augmented generation
        self.knowledge_store: Dict[str, Dict[str, Any]] = {}

        # Training stats
        self.training_examples = 0
        self.training_epochs = 0
        self.last_loss = 0.0

        self.to(device)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass

        Args:
            x: Input tensor of shape (batch_size, seq_len) with token IDs

        Returns:
            Logits of shape (batch_size, seq_len, vocab_size)
        """
        batch_size, seq_len = x.shape

        # Embed tokens
        x = self.token_embedding(x)  # (batch, seq_len, embed_dim)

        # Add positional encoding
        x = x + self.pos_encoding[:, :seq_len, :]

        # Dropout
        x = self.dropout(x)

        # Pass through transformer layers
        for layer in self.transformer_layers:
            x = layer(x)

        # Project to vocabulary
        logits = self.output_proj(x)  # (batch, seq_len, vocab_size)

        return logits

    def generate(
        self,
        prompt_tokens: List[int],
        max_new_tokens: int = 50,
        temperature: float = 0.8,
        top_k: int = 50,
        repetition_penalty: float = 1.2
    ) -> List[int]:
        """
        Generate tokens given a prompt

        Args:
            prompt_tokens: List of token IDs for the prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_k: Only sample from top k tokens
            repetition_penalty: Penalty for repeating tokens (>1.0 discourages repetition)

        Returns:
            List of generated token IDs (including prompt)
        """
        self.eval()

        # Special token IDs
        PAD_ID = 0
        UNK_ID = 1
        BOS_ID = 2
        EOS_ID = 3

        generated = prompt_tokens.copy()
        consecutive_eos = 0

        with torch.no_grad():
            for _ in range(max_new_tokens):
                # Prepare input
                input_seq = torch.tensor([generated[-self.max_seq_len:]],
                                        dtype=torch.long, device=self.device)

                # Get logits
                logits = self(input_seq)  # (1, seq_len, vocab_size)

                # Get last token logits
                next_token_logits = logits[0, -1, :] / temperature

                # Apply repetition penalty
                if repetition_penalty != 1.0:
                    for prev_token in set(generated[-50:]):  # Look at last 50 tokens
                        next_token_logits[prev_token] /= repetition_penalty

                # Penalize special tokens to encourage content generation
                next_token_logits[PAD_ID] = float('-inf')
                next_token_logits[BOS_ID] = float('-inf')
                next_token_logits[EOS_ID] -= 5.0  # Strong penalty but not impossible

                # Apply top-k filtering
                if top_k > 0:
                    top_k_vals, _ = torch.topk(next_token_logits, min(top_k, next_token_logits.size(-1)))
                    indices_to_remove = next_token_logits < top_k_vals[-1]
                    next_token_logits[indices_to_remove] = float('-inf')

                # Sample
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1).item()

                # Track consecutive EOS tokens
                if next_token == EOS_ID:
                    consecutive_eos += 1
                    if consecutive_eos >= 2:  # Stop after 2 consecutive EOS
                        break
                else:
                    consecutive_eos = 0

                generated.append(next_token)

                # Also check for PAD as end signal
                if next_token == PAD_ID:
                    break

        return generated

    def compute_loss(
        self,
        input_ids: torch.Tensor,
        target_ids: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute cross-entropy loss

        Args:
            input_ids: Input token IDs (batch, seq_len)
            target_ids: Target token IDs (batch, seq_len)

        Returns:
            Loss value
        """
        logits = self(input_ids)  # (batch, seq_len, vocab_size)

        # Reshape for cross entropy
        logits = logits.view(-1, self.vocab_size)
        target_ids = target_ids.view(-1)

        loss = F.cross_entropy(logits, target_ids, ignore_index=0)

        return loss

    def add_to_knowledge_store(
        self,
        key: str,
        data: Dict[str, Any]
    ):
        """
        Add entry to knowledge store

        Args:
            key: Unique key for the entry
            data: Dictionary containing the data
        """
        self.knowledge_store[key] = {
            **data,
            'added_at': datetime.now().isoformat()
        }

    def query_knowledge_store(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query knowledge store with improved matching that prioritizes exact matches

        Args:
            query: Query string
            top_k: Number of results to return

        Returns:
            List of matching entries
        """
        query_lower = query.lower().strip()
        query_normalized = query_lower.replace('?', '').replace('.', '').replace('!', '').strip()

        # Extract query words (remove common stop words)
        stop_words = {'what', 'is', 'the', 'a', 'an', 'how', 'why', 'when', 'where',
                      'does', 'do', 'can', 'could', 'would', 'should', 'are', 'was',
                      'were', 'be', 'been', 'being', 'have', 'has', 'had', 'to', 'of',
                      'in', 'for', 'on', 'with', 'at', 'by', 'from', 'it', 'this', 'that'}

        query_words = set(
            word.lower().strip('?.,!')
            for word in query.split()
            if len(word) > 1 and word.lower() not in stop_words
        )

        if not query_words:
            query_words = {query_lower}

        results = []
        for key, data in self.knowledge_store.items():
            score = 0

            if 'prompt' not in data:
                continue

            prompt_lower = data['prompt'].lower().strip()
            prompt_normalized = prompt_lower.replace('?', '').replace('.', '').replace('!', '').strip()

            # EXACT MATCH - highest priority (score 1000)
            if query_normalized == prompt_normalized:
                score = 1000
            elif query_lower in prompt_lower or prompt_lower in query_lower:
                # Very close match
                score = 500

            # If no exact match, do word-based scoring
            if score < 500:
                prompt_words = set(
                    word.strip('?.,!').lower()
                    for word in prompt_lower.split()
                    if len(word) > 1
                )

                # Word overlap - but only count significant words
                significant_overlap = query_words & prompt_words
                score += len(significant_overlap) * 15

                # Bonus for matching numbers exactly
                query_nums = set(w for w in query_words if w.isdigit())
                prompt_nums = set(w for w in prompt_words if w.isdigit())
                if query_nums and query_nums == prompt_nums:
                    score += 50

                # Penalize if lengths are very different (prevents short prompts matching everything)
                len_ratio = len(prompt_lower) / max(len(query_lower), 1)
                if len_ratio < 0.3 or len_ratio > 3.0:
                    score = int(score * 0.5)

            # Category bonus
            if 'category' in data:
                cat_lower = data['category'].lower()
                for qw in query_words:
                    if qw in cat_lower:
                        score += 5

            if score > 0:
                results.append((score, data))

        # Sort by score and return top_k
        results.sort(key=lambda x: x[0], reverse=True)
        return [data for _, data in results[:top_k]]

    def save_checkpoint(self, filepath: str):
        """
        Save model checkpoint with all state (atomic save to prevent corruption)

        Args:
            filepath: Path to save checkpoint
        """
        checkpoint = {
            'model_state_dict': self.state_dict(),
            'vocab_size': self.vocab_size,
            'embed_dim': self.embed_dim,
            'max_seq_len': self.max_seq_len,
            'knowledge_store': self.knowledge_store,
            'training_examples': self.training_examples,
            'training_epochs': self.training_epochs,
            'last_loss': self.last_loss,
            'timestamp': datetime.now().isoformat()
        }

        # Atomic save: write to temp file first, then rename
        temp_filepath = filepath + '.tmp'
        try:
            torch.save(checkpoint, temp_filepath)
            # Verify the temp file was written correctly
            if os.path.exists(temp_filepath) and os.path.getsize(temp_filepath) > 1000:
                # Remove old file and rename temp to final
                if os.path.exists(filepath):
                    os.remove(filepath)
                os.rename(temp_filepath, filepath)
                print(f"Model checkpoint saved to: {filepath}")
            else:
                print(f"WARNING: Checkpoint save failed - temp file too small or missing")
        except Exception as e:
            print(f"ERROR saving checkpoint: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass

    def load_checkpoint(self, filepath: str):
        """
        Load model checkpoint

        Args:
            filepath: Path to checkpoint file
        """
        if not os.path.exists(filepath):
            print(f"Checkpoint not found: {filepath}")
            return False

        checkpoint = torch.load(filepath, map_location=self.device, weights_only=False)

        self.load_state_dict(checkpoint['model_state_dict'])
        self.knowledge_store = checkpoint.get('knowledge_store', {})
        self.training_examples = checkpoint.get('training_examples', 0)
        self.training_epochs = checkpoint.get('training_epochs', 0)
        self.last_loss = checkpoint.get('last_loss', 0.0)

        print(f"Model checkpoint loaded from: {filepath}")
        print(f"  Training examples: {self.training_examples}")
        print(f"  Training epochs: {self.training_epochs}")
        print(f"  Knowledge entries: {len(self.knowledge_store)}")

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            'training_examples': self.training_examples,
            'training_epochs': self.training_epochs,
            'last_loss': self.last_loss,
            'knowledge_entries': len(self.knowledge_store),
            'vocab_size': self.vocab_size,
            'embed_dim': self.embed_dim,
            'parameters': sum(p.numel() for p in self.parameters()),
            'device': str(self.device)
        }


class TransformerBlock(nn.Module):
    """Single transformer block with self-attention and feed-forward"""

    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        ff_dim: int,
        dropout: float = 0.1
    ):
        super().__init__()

        # Multi-head attention
        self.attention = nn.MultiheadAttention(
            embed_dim, num_heads, dropout=dropout, batch_first=True
        )

        # Feed-forward network
        self.ff = nn.Sequential(
            nn.Linear(embed_dim, ff_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(ff_dim, embed_dim),
            nn.Dropout(dropout)
        )

        # Layer normalization
        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)

        # Dropout
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with residual connections"""

        # Self-attention with residual
        attn_out, _ = self.attention(x, x, x)
        x = self.norm1(x + self.dropout(attn_out))

        # Feed-forward with residual
        ff_out = self.ff(x)
        x = self.norm2(x + ff_out)

        return x


class SimpleTokenizer:
    """
    Simple character-level tokenizer for Genesis LLM

    Includes comprehensive mathematical symbol support:
    - Greek letters (α, β, γ, δ, etc.)
    - Math operators (∀, ∃, ∈, ∉, etc.)
    - Set theory (∪, ∩, ⊂, ⊃, etc.)
    - Calculus (∫, ∂, ∇, ∑, ∏, etc.)
    - Relations (≤, ≥, ≠, ≈, ≡, etc.)
    - Number sets (ℕ, ℤ, ℚ, ℝ, ℂ)
    """

    # Mathematical symbols organized by category
    MATH_SYMBOLS = {
        # Greek lowercase
        'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ',
        'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'ς', 'σ', 'τ',
        'υ', 'φ', 'χ', 'ψ', 'ω',
        # Greek uppercase
        'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ',
        'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ',
        'Φ', 'Χ', 'Ψ', 'Ω',
        # Quantifiers and logic
        '∀', '∃', '∄', '∴', '∵', '¬', '∧', '∨', '⊕', '⊗',
        '→', '←', '↔', '⇒', '⇐', '⇔', '⊢', '⊨', '⊤', '⊥',
        # Set theory
        '∈', '∉', '∋', '∌', '∅', '⊂', '⊃', '⊄', '⊅', '⊆',
        '⊇', '⊈', '⊉', '∪', '∩', '∖', '∆', '⊎',
        # Number sets
        'ℕ', 'ℤ', 'ℚ', 'ℝ', 'ℂ', 'ℍ', 'ℙ', 'ℵ', 'ℶ',
        # Calculus and analysis
        '∫', '∬', '∭', '∮', '∯', '∰', '∂', '∇', '∆',
        '∑', '∏', '∐', '√', '∛', '∜',
        # Relations
        '≤', '≥', '≠', '≈', '≅', '≡', '≢', '∝', '≪', '≫',
        '≮', '≯', '≰', '≱', '∼', '≃', '≄', '≍', '≎', '≏',
        # Arithmetic
        '±', '∓', '×', '÷', '·', '∘', '⊙', '⊛',
        # Geometry
        '∠', '∟', '⊾', '⊿', '∥', '∦', '⊥',
        # Arrows
        '↑', '↓', '↕', '↖', '↗', '↘', '↙', '⟵', '⟶', '⟷',
        '⇑', '⇓', '⇕', '↦', '↤', '⟼', '⟻',
        # Miscellaneous math
        '∞', '°', '′', '″', '‴', '∂', '∇', '℘', '℮',
        '⌈', '⌉', '⌊', '⌋', '⟨', '⟩', '⟦', '⟧',
        '‖', '∥', '⫽', '⟂',
        # Subscripts and superscripts
        '⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹',
        '⁺', '⁻', '⁼', '⁽', '⁾', 'ⁿ', 'ⁱ',
        '₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉',
        '₊', '₋', '₌', '₍', '₎',
        # Fractions
        '½', '⅓', '⅔', '¼', '¾', '⅕', '⅖', '⅗', '⅘',
        '⅙', '⅚', '⅛', '⅜', '⅝', '⅞',
        # Additional useful symbols
        '©', '®', '™', '§', '¶', '†', '‡', '•', '…', '‰',
        '€', '£', '¥', '¢', '₿',
        # Box drawing (for tables)
        '─', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼',
        '═', '║', '╔', '╗', '╚', '╝', '╠', '╣', '╦', '╩', '╬',
        # Checkmarks and crosses
        '✓', '✗', '✔', '✘', '☑', '☒', '✕', '✖',
    }

    def __init__(self, vocab_size: int = 10000):
        self.vocab_size = vocab_size

        # Build vocab from common characters and special tokens
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<BOS>': 2,
            '<EOS>': 3,
        }

        # Initialize vocab with special tokens
        self.char_to_id = {**self.special_tokens}
        self.id_to_char = {v: k for k, v in self.char_to_id.items()}

        next_id = len(self.special_tokens)

        # Add ASCII printable characters (32-126)
        for i in range(32, 127):
            char = chr(i)
            if char not in self.char_to_id:
                self.char_to_id[char] = next_id
                self.id_to_char[next_id] = char
                next_id += 1

        # Add extended Latin characters (128-255, useful for accented chars)
        for i in range(128, 256):
            try:
                char = chr(i)
                if char not in self.char_to_id and char.isprintable():
                    self.char_to_id[char] = next_id
                    self.id_to_char[next_id] = char
                    next_id += 1
            except (ValueError, UnicodeError):
                continue

        # Add all mathematical symbols
        for symbol in sorted(self.MATH_SYMBOLS):
            if symbol not in self.char_to_id:
                self.char_to_id[symbol] = next_id
                self.id_to_char[next_id] = symbol
                next_id += 1

        # Add common Unicode math characters by range
        math_ranges = [
            (0x2200, 0x22FF),  # Mathematical Operators
            (0x2300, 0x23FF),  # Miscellaneous Technical
            (0x27C0, 0x27EF),  # Miscellaneous Mathematical Symbols-A
            (0x2980, 0x29FF),  # Miscellaneous Mathematical Symbols-B
            (0x2A00, 0x2AFF),  # Supplemental Mathematical Operators
        ]

        for start, end in math_ranges:
            for i in range(start, min(end + 1, start + 50)):  # Limit per range
                try:
                    char = chr(i)
                    if char not in self.char_to_id and char.isprintable():
                        self.char_to_id[char] = next_id
                        self.id_to_char[next_id] = char
                        next_id += 1
                        if next_id >= vocab_size - 100:  # Leave room
                            break
                except (ValueError, UnicodeError):
                    continue
            if next_id >= vocab_size - 100:
                break

        self.actual_vocab_size = next_id

    def encode(self, text: str) -> List[int]:
        """Convert text to token IDs"""
        tokens = [self.special_tokens['<BOS>']]

        for char in text:
            token_id = self.char_to_id.get(char, self.special_tokens['<UNK>'])
            tokens.append(token_id)

        tokens.append(self.special_tokens['<EOS>'])
        return tokens

    def decode(self, tokens: List[int]) -> str:
        """Convert token IDs to text"""
        chars = []

        for token_id in tokens:
            if token_id in [0, 2, 3]:  # Skip special tokens
                continue

            char = self.id_to_char.get(token_id, '?')
            chars.append(char)

        return ''.join(chars)

    def save(self, filepath: str):
        """Save tokenizer vocabulary with UTF-8 encoding"""
        data = {
            'char_to_id': self.char_to_id,
            'id_to_char': {int(k): v for k, v in self.id_to_char.items()},
            'vocab_size': self.vocab_size,
            'actual_vocab_size': getattr(self, 'actual_vocab_size', len(self.char_to_id))
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str):
        """Load tokenizer vocabulary with UTF-8 encoding"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.char_to_id = data['char_to_id']
        self.id_to_char = {int(k): v for k, v in data['id_to_char'].items()}
        self.vocab_size = data.get('vocab_size', 10000)
        self.actual_vocab_size = data.get('actual_vocab_size', len(self.char_to_id))
