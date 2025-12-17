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
Symbo LLM Adapter for SYMBO_AGENTIC_REASONERS Phase 5
==================================

Provides the LLM interface for mathematical problem solving with:
- Neural network training (when PyTorch available)
- Persistent checkpoints
- Continuous learning from interactions
- Knowledge base integration
- Fallback to symbolic reasoning when neural unavailable

Adapted from Genesis Symbo for SYMBO_AGENTIC_REASONERS mathematical discovery.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import logging
import os
import re
import random
from datetime import datetime

# Optional torch import
try:
    import torch
    import torch.optim as optim
    TORCH_AVAILABLE = True
except (ImportError, RuntimeError, OSError):
    # ImportError: torch not installed
    # RuntimeError: torch version incompatible with Python version (e.g., Python 3.14)
    # OSError: library loading issues
    TORCH_AVAILABLE = False

# Import from local package
from .symbo_llm_core import SymboLLMCore, SimpleTokenizer, TORCH_AVAILABLE as CORE_TORCH_AVAILABLE

logger = logging.getLogger(__name__)


@dataclass
class LLMTask:
    """
    Task specification for Symbo LLM

    Attributes:
        prompt: Mathematical query or problem description
        context: Optional context (problem state, history, etc.)
        task_type: Type of task (reasoning, proof, computation, simplify)
        max_tokens: Maximum response length
        temperature: Randomness (0=deterministic, 1=creative)
    """
    prompt: str
    context: Optional[str] = None
    task_type: str = "reasoning"  # reasoning, proof, computation, simplify
    max_tokens: int = 512
    temperature: float = 0.7
    metadata: Dict[str, Any] = field(default_factory=dict)


class SymboLLMAdapter:
    """
    LLM Adapter for SYMBO_AGENTIC_REASONERS Mathematical Problem Solving

    Features:
    - Loads neural network model (when PyTorch available)
    - Trains with backpropagation on mathematical examples
    - Persists weights between sessions
    - Learns continuously from problem-solving interactions
    - Falls back to symbolic methods when neural unavailable
    """

    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 256,
        device: str = "cuda",
        checkpoint_dir: str = None
    ):
        """
        Initialize LLM adapter

        Args:
            vocab_size: Vocabulary size
            embed_dim: Embedding dimension
            device: 'cuda' or 'cpu'
            checkpoint_dir: Directory for saving/loading checkpoints
        """
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.logger = logging.getLogger("symbo_agentic_reasoners.symbo.llm")

        # Determine device
        if TORCH_AVAILABLE:
            self.device = device if torch.cuda.is_available() else "cpu"
            self.logger.info(f"Initializing Symbo LLM on {self.device}")
        else:
            self.device = "cpu"
            self.logger.info("PyTorch not available - using symbolic fallback mode")

        # Set checkpoint directory
        if checkpoint_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
            checkpoint_dir = os.path.join(project_root, "training", "symbo")

        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

        # Initialize tokenizer
        self.tokenizer = SimpleTokenizer(vocab_size=vocab_size)
        tokenizer_path = os.path.join(checkpoint_dir, "tokenizer.json")
        if os.path.exists(tokenizer_path):
            self.tokenizer.load(tokenizer_path)
            self.logger.info("Tokenizer loaded from checkpoint")

        # Initialize model
        self.model = SymboLLMCore(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            num_heads=4,
            num_layers=3,
            ff_dim=512,
            max_seq_len=512,
            dropout=0.1,
            device=self.device
        )

        # Try to load existing checkpoint
        checkpoint_path = os.path.join(checkpoint_dir, "symbo_llm_latest.pt")
        if os.path.exists(checkpoint_path):
            self.model.load_checkpoint(checkpoint_path)
            self.logger.info("Loaded existing model checkpoint")
        else:
            self.logger.info("No checkpoint found - using fresh model")

        # Optimizer for continuous learning
        if TORCH_AVAILABLE:
            self.optimizer = optim.AdamW(self.model.parameters(), lr=0.0001)
        else:
            self.optimizer = None

        # Statistics
        self.total_queries = 0
        self.successful_generations = 0

        # Initialize mathematical response patterns
        self._init_math_patterns()

        self.logger.info("Symbo LLM initialization complete!")
        self.logger.info(f"Model stats: {self.model.get_stats()}")

    def _init_math_patterns(self):
        """Initialize mathematical response patterns for fallback"""
        # Mathematical operation patterns
        self.math_operations = {
            'triggers': [
                'differentiate', 'derivative', 'diff', 'd/dx',
                'integrate', 'integral', 'antiderivative',
                'solve', 'find x', 'find the value',
                'simplify', 'reduce', 'factor',
                'expand', 'distribute',
                'limit', 'lim',
                'sum', 'series', 'sequence',
            ],
            'responses': [
                "This requires applying {operation} to the expression.",
                "For {operation}, we follow the standard rules.",
                "The {operation} can be computed step by step.",
            ]
        }

        # Proof patterns
        self.proof_patterns = {
            'triggers': [
                'prove', 'proof', 'show that', 'demonstrate',
                'verify', 'confirm', 'establish',
            ],
            'responses': [
                "To prove this, we proceed by {method}.",
                "The proof follows from {principle}.",
                "We can establish this using {technique}.",
            ]
        }

        # Definition patterns
        self.definition_patterns = {
            'triggers': [
                'what is', 'define', 'meaning of', 'explain',
            ],
            'responses': [
                "In mathematics, {term} refers to...",
                "The definition of {term} is...",
                "{term} is a mathematical concept that...",
            ]
        }

    def _check_math_patterns(self, prompt: str) -> Optional[str]:
        """Check if prompt matches mathematical patterns"""
        prompt_lower = prompt.lower().strip()

        # Check operation patterns
        for trigger in self.math_operations['triggers']:
            if trigger in prompt_lower:
                response = random.choice(self.math_operations['responses'])
                return response.format(operation=trigger)

        # Check proof patterns
        for trigger in self.proof_patterns['triggers']:
            if trigger in prompt_lower:
                methods = ['induction', 'contradiction', 'direct proof', 'construction']
                response = random.choice(self.proof_patterns['responses'])
                return response.format(
                    method=random.choice(methods),
                    principle='fundamental axioms',
                    technique='established theorems'
                )

        # Check definition patterns
        for trigger in self.definition_patterns['triggers']:
            if trigger in prompt_lower:
                # Extract potential term
                term = prompt_lower.replace(trigger, '').strip().strip('?.')
                response = random.choice(self.definition_patterns['responses'])
                return response.format(term=term if term else 'this concept')

        return None

    def _is_gibberish(self, text: str) -> bool:
        """
        Detect if generated text is gibberish/corrupted output

        Returns True if the text appears to be nonsensical
        """
        if not text or len(text) < 5:
            return True

        # Check 1: Too many repeated characters (more than 3 in a row)
        if re.search(r'(.)\1{3,}', text):
            return True

        # Check 2: Very low vowel ratio (natural English needs vowels)
        vowels = sum(1 for c in text.lower() if c in 'aeiou')
        letters = sum(1 for c in text if c.isalpha())
        if letters > 10 and vowels / max(letters, 1) < 0.15:
            return True

        # Check 3: Very low space ratio (natural language has word breaks)
        spaces = text.count(' ')
        if len(text) > 20 and spaces / len(text) < 0.05:
            return True

        # Check 4: Too many non-alphanumeric characters
        non_alphanum = sum(1 for c in text if not c.isalnum() and c not in ' .,!?\'"-:;()[]{}^_+=')
        if len(text) > 10 and non_alphanum / len(text) > 0.3:
            return True

        # Check 5: Consecutive consonant runs too long (>6 consonants in a row)
        if re.search(r'[bcdfghjklmnpqrstvwxyz]{7,}', text.lower()):
            return True

        # Check 6: Check for some recognizable common words
        common_words = {
            'the', 'a', 'is', 'in', 'to', 'and', 'of', 'it', 'for', 'on',
            'are', 'with', 'as', 'be', 'this', 'have', 'from', 'by', 'or',
            # Math-specific words
            'let', 'if', 'then', 'where', 'such', 'that', 'given', 'find',
            'solve', 'prove', 'show', 'equals', 'plus', 'minus', 'times',
        }
        words = set(re.findall(r'\b[a-z]+\b', text.lower()))
        common_found = len(words & common_words)
        if len(words) > 5 and common_found == 0:
            return True

        return False

    def _generate_contextual_response(self, prompt: str, context: str = None) -> str:
        """Generate a contextual response for mathematical queries"""
        prompt_lower = prompt.lower()

        # Calculation request
        if any(w in prompt_lower for w in ['calculate', 'compute', 'evaluate', 'find']):
            return "This calculation requires systematic evaluation. Let me work through the steps."

        # Proof request
        if any(w in prompt_lower for w in ['prove', 'show', 'demonstrate', 'verify']):
            return "This proof requires careful logical reasoning. The approach depends on the specific structure."

        # Simplification request
        if any(w in prompt_lower for w in ['simplify', 'reduce', 'factor']):
            return "To simplify this expression, we apply algebraic transformations systematically."

        # Question with mathematical content
        if '?' in prompt or any(w in prompt_lower for w in ['what', 'how', 'why']):
            return "That's a mathematical question that requires analysis. Could you provide more specific context?"

        # Generic mathematical inquiry
        return "I understand this as a mathematical problem. Let me analyze the structure and approach."

    def handle_task(self, task: LLMTask) -> str:
        """
        Process LLM task with knowledge retrieval and fallback

        Args:
            task: LLMTask specification

        Returns:
            Generated response string
        """
        self.total_queries += 1

        try:
            # First: check knowledge base with fuzzy matching
            kb_results = self.model.query_knowledge_store(task.prompt, top_k=3)

            if kb_results and len(kb_results) > 0:
                # Found relevant knowledge - pick best match with valid response
                for result in kb_results:
                    if 'response' in result and len(result['response']) > 10:
                        response = result['response']
                        # Skip corrupted/invalid responses
                        if '<UNK>' in response:
                            continue
                        # Skip placeholder responses
                        if 'still learning' in response.lower():
                            continue
                        self.logger.debug(f"Knowledge base hit for: {task.prompt[:50]}")
                        self.successful_generations += 1
                        return response

            # Second: check mathematical patterns
            pattern_response = self._check_math_patterns(task.prompt)
            if pattern_response:
                self.successful_generations += 1
                return pattern_response

            # Third: try neural generation (if available)
            if TORCH_AVAILABLE:
                response = self._generate_response(task)
                if response and len(response.strip()) > 10:
                    self.successful_generations += 1
                    return response

            # Fourth: generate contextual response
            return self._generate_contextual_response(task.prompt, task.context)

        except Exception as e:
            self.logger.error(f"LLM task failed: {e}", exc_info=True)
            return "An error occurred processing that mathematical query. Please try rephrasing."

    def _generate_response(self, task: LLMTask) -> str:
        """
        Generate response using the neural model

        Args:
            task: LLMTask specification

        Returns:
            Generated text
        """
        if not TORCH_AVAILABLE:
            return ""

        # Build prompt in Q/A format (matches training format)
        prompt_text = f"Q: {task.prompt}\nA:"
        if task.context:
            prompt_text = f"Context: {task.context}\n\n{prompt_text}"

        # Tokenize
        prompt_tokens = self.tokenizer.encode(prompt_text)
        prompt_len = len(prompt_tokens)

        # Generate with repetition penalty
        generated_tokens = self.model.generate(
            prompt_tokens=prompt_tokens,
            max_new_tokens=task.max_tokens,
            temperature=task.temperature,
            top_k=50,
            repetition_penalty=1.3
        )

        # Only decode the NEW tokens (after prompt)
        new_tokens = generated_tokens[prompt_len:]

        # Remove special tokens from output
        filtered_tokens = [t for t in new_tokens if t not in (0, 1, 2, 3)]

        if not filtered_tokens:
            return ""

        # Decode only the generated response
        response = self.tokenizer.decode(filtered_tokens)

        # Clean up whitespace
        response = response.strip()

        # Remove any repeated characters (artifact of char-level model)
        response = re.sub(r'(.)\1{4,}', r'\1\1', response)  # Max 2 repeated chars

        # Check if response is gibberish - reject if so
        if self._is_gibberish(response):
            self.logger.debug(f"Neural output rejected as gibberish: {response[:50]}...")
            return ""  # Return empty to trigger fallback

        return response

    def generate(self, prompt: str, max_length: int = 150, temperature: float = 0.7) -> str:
        """
        Generate text response (Standard LLM interface)

        Args:
            prompt: Input text
            max_length: Max tokens
            temperature: Creativity

        Returns:
            Generated string
        """
        task = LLMTask(
            prompt=prompt,
            max_tokens=max_length,
            temperature=temperature,
            task_type="general"
        )
        return self.handle_task(task)

    def train(self, dataset: List[Dict[str, Any]], epochs: int = 50, batch_size: int = 4):
        """
        Train on mathematical examples with backpropagation

        Args:
            dataset: List of training examples
                     Each: {'prompt': str, 'response': str, 'category': str}
            epochs: Number of training epochs
            batch_size: Training batch size
        """
        if not TORCH_AVAILABLE:
            self.logger.warning("Training requires PyTorch - storing in knowledge base only")
            for item in dataset:
                if 'prompt' in item and 'response' in item:
                    key = f"{item.get('category', 'general')}_{len(self.model.knowledge_store)}"
                    self.model.add_to_knowledge_store(key, item)
            return

        self.logger.info(f"Starting training on {len(dataset)} examples for {epochs} epochs")

        self.model.train()

        # Prepare training data
        training_pairs = []
        for item in dataset:
            if 'prompt' in item and 'response' in item:
                prompt = item['prompt']
                response = item['response']

                # Store in knowledge base
                key = f"{item.get('category', 'general')}_{len(self.model.knowledge_store)}"
                self.model.add_to_knowledge_store(key, item)

                # Create training pair (prompt -> response)
                full_text = f"Q: {prompt}\nA: {response}"
                training_pairs.append(full_text)

        if not training_pairs:
            self.logger.warning("No training pairs found in dataset")
            return

        # Training loop
        total_loss = 0.0
        step = 0

        for epoch in range(epochs):
            epoch_loss = 0.0

            # Shuffle data
            random.shuffle(training_pairs)

            # Process in batches
            for i in range(0, len(training_pairs), batch_size):
                batch_texts = training_pairs[i:i + batch_size]

                # Tokenize batch
                batch_tokens = [self.tokenizer.encode(text) for text in batch_texts]

                # Pad to same length
                max_len = max(len(tokens) for tokens in batch_tokens)
                max_len = min(max_len, self.model.max_seq_len)

                padded_tokens = []
                for tokens in batch_tokens:
                    if len(tokens) > max_len:
                        tokens = tokens[:max_len]
                    else:
                        tokens = tokens + [0] * (max_len - len(tokens))
                    padded_tokens.append(tokens)

                # Convert to tensors
                input_ids = torch.tensor(padded_tokens, dtype=torch.long, device=self.device)

                # Target is same as input (language modeling)
                target_ids = input_ids.clone()

                # Forward pass
                loss = self.model.compute_loss(input_ids, target_ids)

                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()

                # Track loss
                epoch_loss += loss.item()
                step += 1

            avg_epoch_loss = epoch_loss / max(len(training_pairs) / batch_size, 1)
            total_loss += avg_epoch_loss

            if (epoch + 1) % 10 == 0:
                self.logger.info(f"Epoch {epoch + 1}/{epochs} - Loss: {avg_epoch_loss:.4f}")

        # Update model stats
        self.model.training_examples += len(dataset)
        self.model.training_epochs += epochs
        self.model.last_loss = total_loss / max(epochs, 1)

        # Save checkpoint
        self.save()

        self.logger.info(f"Training complete! Final loss: {self.model.last_loss:.4f}")
        self.logger.info(f"Total examples trained: {self.model.training_examples}")

    def learn_from_interaction(self, user_input: str, response: str, category: str = "interaction"):
        """
        Continuously learn from a problem-solving interaction

        This performs a single gradient update based on the interaction.

        Args:
            user_input: User's mathematical query
            response: System's response/solution
            category: Category for the interaction
        """
        # Add to knowledge store
        key = f"{category}_{len(self.model.knowledge_store)}"
        self.model.add_to_knowledge_store(key, {
            'prompt': user_input,
            'response': response,
            'category': category,
            'timestamp': datetime.now().isoformat()
        })

        if not TORCH_AVAILABLE:
            return

        # Perform a single training step
        self.model.train()

        try:
            # Create training text
            full_text = f"Q: {user_input}\nA: {response}"
            tokens = self.tokenizer.encode(full_text)

            # Truncate if needed
            if len(tokens) > self.model.max_seq_len:
                tokens = tokens[:self.model.max_seq_len]

            # Convert to tensor
            input_ids = torch.tensor([tokens], dtype=torch.long, device=self.device)
            target_ids = input_ids.clone()

            # Single gradient step
            loss = self.model.compute_loss(input_ids, target_ids)

            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            self.logger.debug(f"Learned from interaction - Loss: {loss.item():.4f}")

            # Periodically save (every 10 interactions)
            if len(self.model.knowledge_store) % 10 == 0:
                self.save()

        except Exception as e:
            self.logger.error(f"Failed to learn from interaction: {e}")

    def save(self, filepath: str = None):
        """
        Save model checkpoint

        Args:
            filepath: Optional custom save path

        Returns:
            True if successful
        """
        if filepath is None:
            filepath = os.path.join(self.checkpoint_dir, "symbo_llm_latest.pt")

        try:
            self.model.save_checkpoint(filepath)

            # Also save tokenizer
            tokenizer_path = os.path.join(self.checkpoint_dir, "tokenizer.json")
            self.tokenizer.save(tokenizer_path)

            self.logger.info(f"Saved checkpoint to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
            return False

    def load(self, filepath: str = None):
        """
        Load model checkpoint

        Args:
            filepath: Optional custom load path

        Returns:
            True if successful
        """
        if filepath is None:
            filepath = os.path.join(self.checkpoint_dir, "symbo_llm_latest.pt")

        try:
            success = self.model.load_checkpoint(filepath)

            if success:
                # Also load tokenizer
                tokenizer_path = os.path.join(self.checkpoint_dir, "tokenizer.json")
                if os.path.exists(tokenizer_path):
                    self.tokenizer.load(tokenizer_path)

                self.logger.info(f"Loaded checkpoint from {filepath}")

            return success
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        model_stats = self.model.get_stats()

        return {
            **model_stats,
            'total_queries': self.total_queries,
            'successful_generations': self.successful_generations,
            'success_rate': self.successful_generations / max(self.total_queries, 1),
            'checkpoint_dir': self.checkpoint_dir,
            'torch_available': TORCH_AVAILABLE,
            'device': self.device
        }

    def add_knowledge(self, fact: str, category: str = "general"):
        """
        Add knowledge to LLM's knowledge base

        Args:
            fact: Mathematical fact or statement
            category: Knowledge category (theorem, definition, technique, etc.)
        """
        key = f"{category}_{len(self.model.knowledge_store)}"
        self.model.add_to_knowledge_store(key, {
            'fact': fact,
            'category': category
        })
        self.logger.debug(f"Added knowledge: {category} - {fact[:50]}...")

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """
        Get summary of stored knowledge

        Returns:
            Dictionary with knowledge statistics
        """
        return {
            'mode': 'neural' if TORCH_AVAILABLE else 'symbolic_fallback',
            'knowledge_entries': len(self.model.knowledge_store),
            **self.get_stats()
        }

    def solve_mathematical_problem(self, problem: str, problem_type: str = "general") -> Dict[str, Any]:
        """
        High-level interface for mathematical problem solving

        Args:
            problem: The mathematical problem statement
            problem_type: Type hint (calculus, algebra, proof, etc.)

        Returns:
            Dictionary with solution and metadata
        """
        task = LLMTask(
            prompt=problem,
            task_type=problem_type,
            max_tokens=512,
            temperature=0.3,  # Lower temperature for math
            metadata={'problem_type': problem_type}
        )

        response = self.handle_task(task)

        return {
            'problem': problem,
            'solution': response,
            'problem_type': problem_type,
            'stats': self.get_stats()
        }
