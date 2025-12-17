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
Mock Student Model for Testing
==============================

This mock student model is ONLY for testing purposes.
It should NEVER be used in production code.

Usage in tests:
    from tests.mocks.mock_student import MockStudentModel

    student = MockStudentModel()
    response = student.generate("Find derivative of x^2")
"""

import logging
from typing import Dict, Any

logger = logging.getLogger('symbo_agentic_reasoners.tests.mocks.student')


class MockStudentModel:
    """
    Mock student model for testing when Symbo is not available

    WARNING: This is for TESTING ONLY. Production code should fail-fast
    when student models are not available, not fall back to mocks.

    This mock simulates the interface of SymboLLMAdapter/SymboLLMCore
    to allow testing of the Phase 5 system without real dependencies.
    """

    def __init__(self, name: str = "mock_student"):
        """
        Initialize mock student model

        Args:
            name: Name identifier for this mock
        """
        self.name = name
        self.queries_processed = 0
        self._training_examples = []
        self._knowledge_base = []
        logger.warning(f"MockStudentModel initialized - FOR TESTING ONLY")

    def generate(self, query: str) -> str:
        """
        Generate a mock response for a query

        Args:
            query: User's mathematical query

        Returns:
            Mock response string
        """
        self.queries_processed += 1
        query_lower = query.lower()

        # Provide mock responses based on query type
        if 'derivative' in query_lower:
            response = "Derivative: (mock student response)"
        elif 'integrate' in query_lower:
            response = "Integral: (mock student response)"
        elif 'solve' in query_lower:
            response = "Solution: (mock student response)"
        elif 'prove' in query_lower:
            response = "Proof: (mock student response)"
        else:
            response = "Result: (mock student response)"

        logger.debug(f"MockStudentModel generated: {response}")
        return response

    def handle_task(self, task) -> str:
        """
        Handle a task (mimics SymboLLMAdapter interface)

        Args:
            task: LLMTask object with prompt

        Returns:
            Mock response string
        """
        prompt = getattr(task, 'prompt', str(task))
        return self.generate(prompt)

    def learn_from_interaction(
        self,
        user_input: str,
        response: str,
        category: str = 'general'
    ):
        """
        Mock learning from interaction (mimics SymboLLMAdapter interface)

        Args:
            user_input: Original query
            response: Response generated
            category: Category of the interaction
        """
        self._training_examples.append({
            'input': user_input,
            'response': response,
            'category': category
        })
        logger.debug(f"MockStudentModel recorded training example: {user_input[:50]}...")

    def add_knowledge(self, fact: str, category: str = 'general'):
        """
        Mock knowledge addition (mimics SymboLLMAdapter interface)

        Args:
            fact: Fact to add
            category: Category of the fact
        """
        self._knowledge_base.append({
            'fact': fact,
            'category': category
        })
        logger.debug(f"MockStudentModel added knowledge: {fact[:50]}...")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get mock statistics (mimics SymboLLMAdapter interface)

        Returns:
            Statistics dictionary
        """
        return {
            'device': 'mock',
            'torch_available': False,
            'total_queries': self.queries_processed,
            'successful_generations': self.queries_processed,
            'success_rate': 1.0 if self.queries_processed > 0 else 0.0,
            'knowledge_entries': len(self._knowledge_base),
            'training_examples': len(self._training_examples),
            'training_epochs': 0,
            'mock': True,
            'warning': 'This is a mock model - not real computation'
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Alias for get_stats()"""
        return self.get_stats()

    def __repr__(self) -> str:
        return f"MockStudentModel({self.name})"

    def __str__(self) -> str:
        return f"Mock Student Model '{self.name}' (TESTING ONLY)"
