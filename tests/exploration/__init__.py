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
EXPLORATION LAYER TESTS
======================

Comprehensive test suite for the exploration layer (Tier 1.5).

Test Modules:
- test_data_structures.py: Tests for Strategy, ExplorationResult, StrategyRanking
- test_universal_explorer.py: Tests for UniversalStrategyExplorer
- test_integration.py: Integration tests with orchestrator and knowledge management

Running Tests:
-------------
# Run all exploration tests
pytest tests/exploration/

# Run specific test file
pytest tests/exploration/test_data_structures.py -v

# Run specific test class
pytest tests/exploration/test_data_structures.py::TestStrategy -v

# Run with coverage
pytest tests/exploration/ --cov=symbo_agentic_reasoners.exploration --cov-report=html
"""

__all__ = []
