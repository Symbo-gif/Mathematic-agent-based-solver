#!/usr/bin/env python3
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
SYMBO AGENTIC REASONERS - Main Entry Point
==========================================

Mathematical Agent-Based Solver System
260+ Agents | 38 Supervisors | 220+ Specialists | 6 Phases

This is the main entry point for the system. Run this file to start
the interactive CLI or process batch problems.

Usage:
    python main.py                         # Interactive mode
    python main.py solve "2+2"             # Solve single problem
    python main.py batch ./problems/       # Process folder
    python main.py status                  # System status

Architecture:
    Phase 0: Infrastructure (AMS, DF, ACC, Watchdog, Resource Governor)
    Phase 1: Cognition (Orchestrator, BDI Framework, Blackboard)
    Phase 2: Mathematical Workforce (38 Supervisors, 220+ Specialists across 30 domains)
    Phase 3: Meta-Cognition (Knowledge Management, Meta-Learning, Pattern Indexer)
    Phase 4: Governance (Conflict Resolution, Failure Analysis, Strategy Learning)
    Phase 5: Optimization (Distillation, Evolutionary Flywheel, Hardening)
    Phase 6: Discovery (Conjecture, Deep Search, Algorithm Synthesis)
"""

import sys
import os

# Add src to path for development
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def main():
    """Main entry point - launches the CLI."""
    try:
        from mathematic_solver.cli import main as cli_main
    except ImportError:  # Backwards compatibility during refactor
        from symbo_agentic_reasoners.cli import main as cli_main
    cli_main()


if __name__ == '__main__':
    main()
