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
LEARNING ENHANCEMENT TEAM - BPE Tokenizer Specialist (Tier 3)
==============================================================

Implements Byte Pair Encoding (BPE) tokenization optimized for mathematical
expressions. Reduces vocabulary waste from ~97% to near-optimal coverage.

PROBLEM:
-------
Character-level tokenization wastes capacity:
- "integral" = 8 tokens instead of 1
- "derivative" = 10 tokens instead of 1
- Mathematical meaning lost at character level
- vocab_size=10000 but only ~300 chars used

SOLUTION:
--------
BPE tokenization with mathematical primitives:
- Mathematical functions as single tokens (sin, cos, sqrt, integral)
- Common subwords learned from corpus
- Target vocab_size=8192 with efficient usage
- ~3x reduction in token count for typical problems

BPE ALGORITHM:
-------------
1. Initialize vocabulary with characters + math primitives
2. Count pair frequencies in training corpus
3. Merge most frequent pair into new token
4. Repeat until target vocab_size reached

REFERENCE:
---------
- Plan: lexical-leaping-tower.md Phase 3 Priority 1
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path

from symbo_agentic_reasoners.core.bdi_agent import BDIAgent, Intention
from symbo_agentic_reasoners.infrastructure.directory_facilitator import (
    DirectoryFacilitator, create_service_registration
)
from symbo_agentic_reasoners.core.blackboard import (
    Blackboard, create_entry, EntryType, EntryStatus
)

logger = logging.getLogger('symbo_agentic_reasoners.learning.bpe_tokenizer')


class BPETokenizerSpecialist(BDIAgent):
    """
    BPE Tokenizer Specialist - Tier 3

    Implements Byte Pair Encoding tokenization optimized for mathematical
    expressions. Preserves mathematical primitives and learns efficient
    subword vocabulary from corpus.

    ROLE:
    ----
    1. Train BPE vocabulary on mathematical corpus
    2. Encode/decode mathematical expressions
    3. Maintain math-specific primitive tokens
    4. Analyze tokenization efficiency

    MATHEMATICAL PRIMITIVES:
    -----------------------
    Pre-seeded tokens for mathematical concepts:
    - Functions: sin, cos, tan, sqrt, log, ln, exp, abs
    - Calculus: integral, derivative, limit, sum, series
    - Algebra: polynomial, coefficient, factor, solve
    - Linear Algebra: matrix, vector, eigenvalue, det
    - Number Theory: gcd, lcm, mod, prime, factorial

    Example:
        >>> tokenizer = BPETokenizerSpecialist()
        >>> tokenizer.train(corpus)
        >>> tokens = tokenizer.encode("integral of sin(x)")
        >>> text = tokenizer.decode(tokens)
    """

    # Mathematical primitives - these are always single tokens
    MATH_PRIMITIVES = [
        # Trigonometric functions
        'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
        'arcsin', 'arccos', 'arctan', 'arccot', 'arcsec', 'arccsc',
        'sinh', 'cosh', 'tanh', 'coth', 'sech', 'csch',
        'arcsinh', 'arccosh', 'arctanh',

        # Basic functions
        'sqrt', 'cbrt', 'log', 'ln', 'exp', 'abs', 'sgn', 'floor', 'ceil',

        # Calculus
        'integral', 'derivative', 'partial', 'limit', 'lim',
        'sum', 'product', 'series', 'sequence',
        'gradient', 'divergence', 'curl', 'laplacian', 'nabla',
        'd/dx', 'd/dy', 'd/dt', 'd/dz',

        # Linear Algebra
        'matrix', 'vector', 'det', 'determinant', 'trace', 'transpose',
        'eigenvalue', 'eigenvector', 'rank', 'nullity', 'kernel',
        'span', 'basis', 'dimension', 'orthogonal', 'orthonormal',

        # Number Theory
        'gcd', 'lcm', 'mod', 'factorial', 'binomial', 'permutation',
        'prime', 'divisor', 'totient', 'mobius', 'legendre', 'jacobi',

        # Algebra
        'polynomial', 'coefficient', 'degree', 'root', 'zero',
        'factor', 'expand', 'simplify', 'solve', 'substitute',

        # Constants
        'pi', 'euler', 'infinity', 'epsilon', 'delta', 'lambda', 'omega',

        # Operators/Keywords
        'where', 'such', 'that', 'given', 'find', 'prove', 'evaluate',
        'compute', 'calculate', 'determine', 'show', 'verify',

        # Greek letters (common in math)
        'alpha', 'beta', 'gamma', 'theta', 'phi', 'psi', 'sigma', 'tau',
    ]

    # Special tokens
    SPECIAL_TOKENS = {
        '<pad>': 0,
        '<unk>': 1,
        '<bos>': 2,
        '<eos>': 3,
        '<sep>': 4,
    }

    def __init__(
        self,
        agent_id: str = 'bpe_tokenizer_001',
        df: Optional[DirectoryFacilitator] = None,
        blackboard: Optional[Blackboard] = None,
        vocab_size: int = 8192,
        min_frequency: int = 2,
        persistence_path: Optional[str] = None
    ):
        """
        Initialize BPE Tokenizer Specialist.

        Args:
            agent_id: Unique agent identifier
            df: Directory Facilitator for service registration
            blackboard: Shared blackboard for communication
            vocab_size: Target vocabulary size
            min_frequency: Minimum frequency for merge consideration
            persistence_path: Path to save/load vocabulary
        """
        super().__init__(agent_id)

        self.df = df
        self.blackboard = blackboard
        self.target_vocab_size = vocab_size
        self.min_frequency = min_frequency
        self.persistence_path = persistence_path

        # BPE state
        self.vocab: Dict[str, int] = {}          # token -> id
        self.id_to_token: Dict[int, str] = {}    # id -> token
        self.merges: Dict[Tuple[str, str], str] = {}  # (a, b) -> ab
        self.merge_order: List[Tuple[str, str]] = []  # order of merges

        # Initialize with special tokens and math primitives
        self._initialize_vocabulary()

        # Statistics
        self.is_trained = False
        self.training_corpus_size = 0
        self.encode_calls = 0
        self.decode_calls = 0

        # BDI state
        self.beliefs: Dict[str, Any] = {
            'vocab_efficiency': 0.0,
            'math_coverage': 0.0,
            'retrain_needed': False
        }

        # Load from disk if available
        if persistence_path:
            self._load_from_disk()

        # Register with Directory Facilitator
        if self.df:
            self._register_services()

        logger.info(f"[{self.agent_id}] BPE Tokenizer initialized, vocab_size={len(self.vocab)}")

    def _register_services(self) -> None:
        """Register services with Directory Facilitator."""
        registration = create_service_registration(
            agent_id=self.agent_id,
            service_type='learning.tokenization',
            description='BPE tokenization for mathematical expressions',
            capabilities=['train', 'encode', 'decode', 'analyze']
        )
        self.df.register(registration)
        logger.info(f"[{self.agent_id}] Registered with DF")

    def _initialize_vocabulary(self) -> None:
        """Initialize vocabulary with special tokens and math primitives."""
        self.vocab = {}
        self.id_to_token = {}

        # Add special tokens first
        for token, token_id in self.SPECIAL_TOKENS.items():
            self.vocab[token] = token_id
            self.id_to_token[token_id] = token

        next_id = len(self.SPECIAL_TOKENS)

        # Add math primitives
        for primitive in self.MATH_PRIMITIVES:
            if primitive not in self.vocab:
                self.vocab[primitive] = next_id
                self.id_to_token[next_id] = primitive
                next_id += 1

        # Add basic ASCII characters
        for i in range(32, 127):
            char = chr(i)
            if char not in self.vocab:
                self.vocab[char] = next_id
                self.id_to_token[next_id] = char
                next_id += 1

        # Add common math symbols
        math_symbols = '∫∑∏√∂∞±≤≥≠≈∈∉∩∪∅⊂⊃⊆⊇∀∃∧∨¬→←↔⇒⇐⇔αβγδεζηθικλμνξπρστυφχψωΓΔΘΛΞΠΣΦΨΩ'
        for char in math_symbols:
            if char not in self.vocab:
                self.vocab[char] = next_id
                self.id_to_token[next_id] = char
                next_id += 1

        logger.debug(f"Initialized vocabulary with {len(self.vocab)} tokens")

    def train(
        self,
        corpus: List[str],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Train BPE on a mathematical corpus.

        Args:
            corpus: List of text samples for training
            verbose: Whether to print progress

        Returns:
            Training statistics
        """
        if not corpus:
            return {'error': 'Empty corpus'}

        logger.info(f"Training BPE on {len(corpus)} samples...")
        self.training_corpus_size = len(corpus)

        # Pre-tokenize corpus into words
        word_freqs = self._get_word_frequencies(corpus)

        if verbose:
            print(f"Unique words: {len(word_freqs)}")

        # Convert words to character sequences (for BPE)
        splits = {}
        for word, freq in word_freqs.items():
            # Check if word is a known primitive
            if word.lower() in self.vocab:
                splits[word] = [word.lower()]
            else:
                splits[word] = list(word)

        # Learn merges until target vocab size
        merges_learned = 0
        initial_vocab_size = len(self.vocab)

        while len(self.vocab) < self.target_vocab_size:
            # Count pair frequencies
            pair_freqs = self._get_pair_frequencies(splits, word_freqs)

            if not pair_freqs:
                break

            # Find most frequent pair
            best_pair = max(pair_freqs.items(), key=lambda x: x[1])
            pair, freq = best_pair

            if freq < self.min_frequency:
                break

            # Create new token
            new_token = pair[0] + pair[1]

            # Add to vocabulary
            if new_token not in self.vocab:
                new_id = len(self.vocab)
                self.vocab[new_token] = new_id
                self.id_to_token[new_id] = new_token

            # Record merge
            self.merges[pair] = new_token
            self.merge_order.append(pair)
            merges_learned += 1

            # Apply merge to splits
            splits = self._apply_merge(splits, pair, new_token)

            if verbose and merges_learned % 500 == 0:
                print(f"Merges: {merges_learned}, Vocab: {len(self.vocab)}")

        self.is_trained = True

        # Persist if configured
        if self.persistence_path:
            self._save_to_disk()

        stats = {
            'initial_vocab_size': initial_vocab_size,
            'final_vocab_size': len(self.vocab),
            'merges_learned': merges_learned,
            'corpus_size': len(corpus),
            'unique_words': len(word_freqs),
            'primitives_preserved': len(self.MATH_PRIMITIVES)
        }

        logger.info(f"BPE training complete: {stats}")
        return stats

    def _get_word_frequencies(self, corpus: List[str]) -> Dict[str, int]:
        """Get word frequencies from corpus."""
        word_freqs = Counter()

        for text in corpus:
            # Tokenize on whitespace and operators, preserve math terms
            words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\d+\.?\d*|[^\s]', text)
            word_freqs.update(words)

        return dict(word_freqs)

    def _get_pair_frequencies(
        self,
        splits: Dict[str, List[str]],
        word_freqs: Dict[str, int]
    ) -> Dict[Tuple[str, str], int]:
        """Count frequencies of adjacent token pairs."""
        pair_freqs = Counter()

        for word, split in splits.items():
            if len(split) < 2:
                continue

            freq = word_freqs[word]
            for i in range(len(split) - 1):
                pair = (split[i], split[i + 1])
                pair_freqs[pair] += freq

        return dict(pair_freqs)

    def _apply_merge(
        self,
        splits: Dict[str, List[str]],
        pair: Tuple[str, str],
        new_token: str
    ) -> Dict[str, List[str]]:
        """Apply merge to all word splits."""
        new_splits = {}

        for word, split in splits.items():
            new_split = []
            i = 0

            while i < len(split):
                if i < len(split) - 1 and (split[i], split[i + 1]) == pair:
                    new_split.append(new_token)
                    i += 2
                else:
                    new_split.append(split[i])
                    i += 1

            new_splits[word] = new_split

        return new_splits

    def encode(self, text: str) -> List[int]:
        """
        Encode text to token IDs using learned BPE.

        Args:
            text: Text to encode

        Returns:
            List of token IDs
        """
        self.encode_calls += 1

        if not text:
            return []

        # Pre-tokenize into words
        words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\d+\.?\d*|[^\s]', text)

        token_ids = []

        for word in words:
            word_lower = word.lower()

            # Check if it's a known primitive
            if word_lower in self.vocab:
                token_ids.append(self.vocab[word_lower])
                continue

            # Check original case
            if word in self.vocab:
                token_ids.append(self.vocab[word])
                continue

            # Apply BPE
            tokens = self._bpe_encode_word(word)
            for token in tokens:
                if token in self.vocab:
                    token_ids.append(self.vocab[token])
                else:
                    token_ids.append(self.SPECIAL_TOKENS['<unk>'])

        return token_ids

    def _bpe_encode_word(self, word: str) -> List[str]:
        """Apply BPE merges to a single word."""
        # Start with characters
        tokens = list(word)

        # Apply merges in order learned
        for pair in self.merge_order:
            new_tokens = []
            i = 0

            while i < len(tokens):
                if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == pair:
                    new_tokens.append(self.merges[pair])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1

            tokens = new_tokens

        return tokens

    def decode(self, token_ids: List[int]) -> str:
        """
        Decode token IDs back to text.

        Args:
            token_ids: List of token IDs

        Returns:
            Decoded text
        """
        self.decode_calls += 1

        if not token_ids:
            return ''

        tokens = []
        for token_id in token_ids:
            if token_id in self.id_to_token:
                token = self.id_to_token[token_id]
                # Skip special tokens in output
                if not token.startswith('<'):
                    tokens.append(token)
            else:
                tokens.append('<unk>')

        # Join tokens - add spaces between words
        text = ''
        for i, token in enumerate(tokens):
            if i > 0 and token.isalnum() and tokens[i-1].isalnum():
                text += ' '
            text += token

        return text

    def analyze_efficiency(self, samples: List[str]) -> Dict[str, Any]:
        """
        Analyze tokenization efficiency on sample texts.

        Args:
            samples: List of text samples to analyze

        Returns:
            Efficiency metrics
        """
        if not samples:
            return {'error': 'No samples to analyze'}

        total_chars = 0
        total_tokens = 0
        compression_ratios = []
        unknown_count = 0
        math_primitive_hits = 0

        for sample in samples:
            total_chars += len(sample)

            tokens = self.encode(sample)
            total_tokens += len(tokens)

            if len(sample) > 0:
                ratio = len(tokens) / len(sample)
                compression_ratios.append(ratio)

            # Count unknowns and primitives
            for token_id in tokens:
                if token_id == self.SPECIAL_TOKENS['<unk>']:
                    unknown_count += 1
                elif self.id_to_token.get(token_id, '') in self.MATH_PRIMITIVES:
                    math_primitive_hits += 1

        avg_compression = sum(compression_ratios) / len(compression_ratios) if compression_ratios else 0
        unk_rate = unknown_count / total_tokens if total_tokens > 0 else 0
        primitive_rate = math_primitive_hits / total_tokens if total_tokens > 0 else 0

        return {
            'samples_analyzed': len(samples),
            'total_characters': total_chars,
            'total_tokens': total_tokens,
            'avg_compression_ratio': avg_compression,  # < 1.0 is better
            'chars_per_token': total_chars / total_tokens if total_tokens > 0 else 0,
            'unknown_rate': unk_rate,
            'math_primitive_rate': primitive_rate,
            'vocab_utilization': len(self.vocab) / self.target_vocab_size,
            'is_trained': self.is_trained
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get tokenizer statistics."""
        return {
            'vocab_size': len(self.vocab),
            'target_vocab_size': self.target_vocab_size,
            'merges_learned': len(self.merges),
            'math_primitives': len(self.MATH_PRIMITIVES),
            'is_trained': self.is_trained,
            'training_corpus_size': self.training_corpus_size,
            'encode_calls': self.encode_calls,
            'decode_calls': self.decode_calls
        }

    def get_vocabulary(self) -> Dict[str, int]:
        """Get current vocabulary."""
        return dict(self.vocab)

    def _save_to_disk(self) -> None:
        """Persist vocabulary and merges to disk."""
        if not self.persistence_path:
            return

        try:
            path = Path(self.persistence_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'vocab': self.vocab,
                'merges': {f"{k[0]}|||{k[1]}": v for k, v in self.merges.items()},
                'merge_order': [f"{p[0]}|||{p[1]}" for p in self.merge_order],
                'target_vocab_size': self.target_vocab_size,
                'is_trained': self.is_trained,
                'training_corpus_size': self.training_corpus_size,
                'saved_at': datetime.now().isoformat()
            }

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved BPE vocabulary to {path}")

        except Exception as e:
            logger.error(f"Failed to save vocabulary: {e}")

    def _load_from_disk(self) -> None:
        """Load vocabulary and merges from disk."""
        if not self.persistence_path:
            return

        path = Path(self.persistence_path)
        if not path.exists():
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Restore vocabulary
            self.vocab = data.get('vocab', {})
            self.id_to_token = {int(v): k for k, v in self.vocab.items()}

            # Restore merges
            merges_raw = data.get('merges', {})
            self.merges = {}
            for key, value in merges_raw.items():
                parts = key.split('|||')
                if len(parts) == 2:
                    self.merges[(parts[0], parts[1])] = value

            # Restore merge order
            merge_order_raw = data.get('merge_order', [])
            self.merge_order = []
            for item in merge_order_raw:
                parts = item.split('|||')
                if len(parts) == 2:
                    self.merge_order.append((parts[0], parts[1]))

            self.target_vocab_size = data.get('target_vocab_size', 8192)
            self.is_trained = data.get('is_trained', False)
            self.training_corpus_size = data.get('training_corpus_size', 0)

            logger.info(f"Loaded BPE vocabulary from {path}: {len(self.vocab)} tokens")

        except Exception as e:
            logger.error(f"Failed to load vocabulary: {e}")

    # BDI Agent methods
    def update_beliefs(self, percept: Dict[str, Any] = None) -> None:
        """Update beliefs based on current state."""
        self.beliefs['vocab_efficiency'] = len(self.vocab) / self.target_vocab_size

        # Check math primitive coverage
        primitives_in_vocab = sum(
            1 for p in self.MATH_PRIMITIVES if p in self.vocab
        )
        self.beliefs['math_coverage'] = primitives_in_vocab / len(self.MATH_PRIMITIVES)

        # Check if retrain needed
        self.beliefs['retrain_needed'] = (
            not self.is_trained or
            self.beliefs['vocab_efficiency'] < 0.5
        )

    def deliberate(self) -> Optional[Intention]:
        """Deliberate on current beliefs."""
        if self.beliefs.get('retrain_needed', False):
            return Intention(
                plan_id='retrain_vocabulary',
                steps=['collect_corpus', 'clear_merges', 'train', 'validate', 'persist'],
                target_desire='optimal_tokenization'
            )
        return None

    def execute_step(self) -> bool:
        """Execute one step of agent processing."""
        if self.blackboard:
            # Would check for pending tokenization tasks
            pass
        return False

    def process(self, task_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task from the supervisor.

        Args:
            task_entry: Task with 'action' and relevant data

        Returns:
            Processing result
        """
        action = task_entry.get('action', 'encode')

        if action == 'train':
            return self.train(
                corpus=task_entry.get('corpus', []),
                verbose=task_entry.get('verbose', False)
            )

        elif action == 'encode':
            tokens = self.encode(task_entry.get('text', ''))
            return {'tokens': tokens, 'count': len(tokens)}

        elif action == 'decode':
            text = self.decode(task_entry.get('tokens', []))
            return {'text': text}

        elif action == 'analyze':
            return self.analyze_efficiency(task_entry.get('samples', []))

        elif action == 'get_stats':
            return self.get_stats()

        elif action == 'get_vocabulary':
            return {'vocabulary': self.get_vocabulary()}

        else:
            return {'error': f'Unknown action: {action}'}
